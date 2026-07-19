import os
import requests
import json
import asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class Brain:
    def __init__(self, mode="local"):
        self.mode = mode # "local" or "gemini"
        self.local_url = os.getenv("LOCAL_LLM_URL", "http://local-llm:8080/v1/chat/completions")
        
        # System instructions
        self.system_prompt = """
        You are 'easy-jarvis', a Kind, Teacher-like, and Funny autonomous assistant for 'simpleprogrammer'.
        
        YOUR ROLE:
        1. Act as a 'Terminal Master'. You build things by generating shell commands.
        2. Be Safety-First: Think ahead and predict failures.
        3. Be a Teacher: Briefly explain your logic.
        4. Multi-turn Chat: Remember previous context to guide the user.
        
        OUTPUT FORMAT (STRICT JSON):
        {
            "speech": "What you say back",
            "command": "Shell command or null",
            "thought": "Proactive safety/logic reasoning"
        }
        """
        
        # Initialize Gemini backend (lazy-ready)
        self.gemini_ready = False
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
                self.gemini_model_name = 'gemini-1.5-flash-8b'
                self.gemini_ready = True
            except Exception as e:
                print(f"[!] Gemini Init Warning: {e}")

        self.history = []
        self.max_history = 10

    def _is_important(self, text: str) -> bool:
        """Heuristic to determine if a question is 'important' enough for Gemini."""
        important_keywords = ["important", "critical", "security", "solve", "complex", "code", "debug", "architecture", "gemini"]
        text_lower = text.lower()
        return any(kw in text_lower for kw in important_keywords)

    async def process_command(self, user_input: str):
        """Processes user input with a 'Local-First' priority and intelligent fallback."""
        print(f"[*] easy-jarvis Brain: Processing '{user_input}'...")

        # 1. Attempt Local First
        local_result = await self._process_local(user_input)

        # 2. If local succeeded AND it wasn't a timeout/error, return it
        if "offline" not in local_result.get("speech", "").lower() and \
           "trouble thinking" not in local_result.get("speech", "").lower() and \
           "connection issue" not in local_result.get("speech", "").lower():
            return local_result

        # 3. Fallback to Gemini if Local failed
        if self.gemini_ready:
            print("[*] Local LLM struggled. Attempting Gemini Cloud fallback...")
            gemini_result = await self._process_gemini(user_input)

            # 4. Handle Gemini Quota/Error fallback
            if "snag with the cloud" in gemini_result.get("speech", ""):
                print("[!] Gemini failed (Quota or Error). Returning local error as last resort.")
                return local_result

            return gemini_result

        return local_result

    async def _process_local(self, user_input: str):
        """Handles inference via local llama.cpp server with 'Universal Compatibility' format."""
        messages = []
        if not self.history:
            combined_content = f"SYSTEM INSTRUCTIONS:\n{self.system_prompt}\n\nUSER INPUT:\n{user_input}"
            messages.append({"role": "user", "content": combined_content})
        else:
            for h in self.history:
                messages.append(h)
            messages.append({"role": "user", "content": user_input})

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 512,
            "stream": False
        }

        try:
            response = requests.post(self.local_url, json=payload, timeout=120)
            
            # Check for Ngrok/HTML error pages
            if "text/html" in response.headers.get("Content-Type", ""):
                print(f"[!] Local Brain is OFFLINE (HTML response from {self.local_url})")
                return {
                    "speech": "Sir, my remote brain is currently offline.",
                    "command": None,
                    "thought": "Ngrok returned HTML instead of JSON. The Colab server is likely stopped."
                }

            if response.status_code != 200:
                print(f"[!] Local Brain Error {response.status_code}: {response.text}")
                return {
                    "speech": "I'm having a connection issue with my local brain.",
                    "command": None,
                    "thought": f"Server Error {response.status_code}"
                }
                
            data = response.json()
            content = data['choices'][0]['message']['content']

            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": content})
            if len(self.history) > 8:
                self.history = self.history[-8:]

            try:
                return json.loads(content)
            except Exception:
                return {"speech": content, "command": None, "thought": "Plain text response."}
        except Exception as e:
            print(f"[!] Local Brain Connection Error: {e}")
            return {
                "speech": "I'm having trouble thinking locally. The local model is taking too long to respond.",
                "command": None,
                "thought": f"Connection Error: {str(e)}"
            }

    async def _process_gemini(self, user_input: str):
        """Handles inference via Google Gemini API with ultra-aggressive pacing."""
        if not self.gemini_ready:
            return {"speech": "Gemini not configured.", "command": None, "thought": "API key missing."}
            
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                # 20 second delay to avoid free tier RPM limits during team turns
                print(f"[*] Pacing Gemini (20s delay)... attempt {attempt+1}")
                await asyncio.sleep(20)
                
                contents = []
                for h in self.history:
                    role = "user" if h["role"] == "user" else "model"
                    contents.append(types.Content(role=role, parts=[types.Part(text=h["content"])]))
                
                contents.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

                response = self.client.models.generate_content(
                    model=self.gemini_model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_prompt,
                        response_mime_type="application/json"
                    )
                )
                
                result = json.loads(response.text)
                self.history.append({"role": "user", "content": user_input})
                self.history.append({"role": "assistant", "content": response.text})
                return result

            except Exception as e:
                error_msg = str(e)
                print(f"[!] Gemini Attempt {attempt+1} failed: {error_msg}")
                
                if "429" in error_msg:
                    if attempt < max_retries:
                        print("[*] Quota hit. Sleeping 40s before retry...")
                        await asyncio.sleep(40)
                        continue
                    else:
                        thought = "Gemini API Quota Exceeded (429)."
                else:
                    thought = f"Gemini API Error: {error_msg}"
                    
                return {
                    "speech": "I've hit a slight cognitive snag with the cloud.",
                    "command": None,
                    "thought": thought
                }

class BrainFactory:
    @staticmethod
    def create_brain():
        return Brain()

if __name__ == "__main__":
    async def test():
        b = Brain()
        result = await b.process_command("Hello")
        print(result)
    # asyncio.run(test())
