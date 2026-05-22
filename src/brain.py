import os
import requests
import json
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
                self.gemini_model_name = 'gemini-2.0-flash'
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

        is_important = self._is_important(user_input)

        # 1. Attempt Local First (Always respect 'local model first' request)
        local_result = await self._process_local(user_input)

        # 2. If local succeeded AND it wasn't a timeout/error, return it
        if "trouble thinking locally" not in local_result.get("speech", ""):
            # If it wasn't important, we are done.
            # If it WAS important, but local did a good job, we stick with it to save quota.
            return local_result

        # 3. Fallback to Gemini if Local failed or timed out
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
        """Handles inference via local llama.cpp server with increased timeout."""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add history
        for h in self.history:
            messages.append(h)
            
        # Add current input
        messages.append({"role": "user", "content": user_input})

        payload = {
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }

        try:
            # Increased timeout to 120s for resource-constrained environments
            response = requests.post(self.local_url, json=payload, timeout=120)
            if response.status_code != 200:
                print(f"[!] Local Brain Error {response.status_code}: {response.text}")
                response.raise_for_status()
                
            data = response.json()
            content = data['choices'][0]['message']['content']

            # Record in history (limiting size)
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": content})
            if len(self.history) > self.max_history * 2:
                self.history = self.history[-(self.max_history * 2):]

            # Attempt to parse JSON
            try:
                return json.loads(content)
            except:
                return {
                    "speech": content,
                    "command": None,
                    "thought": "Model returned plain text instead of JSON."
                }
        except Exception as e:
            print(f"[!] Local Brain Error: {e}")
            return {
                "speech": "I'm having trouble thinking locally. The local model is taking too long to respond.",
                "command": None,
                "thought": f"Local LLM Error: {str(e)}"
            }

    async def _process_gemini(self, user_input: str):
        """Handles inference via Google Gemini API using new SDK."""
        if not self.gemini_ready:
            return {"speech": "Gemini not configured.", "command": None, "thought": "API key missing."}
            
        try:
            # Map history to new SDK format
            contents = []
            for h in self.history:
                role = "user" if h["role"] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part(text=h["content"])]))
            
            # Add current input
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
            
            # Add to history
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": response.text})
            
            return result
        except Exception as e:
            error_msg = str(e)
            print(f"[!] Gemini Brain Error: {error_msg}")
            
            # Quota handling (429)
            thought = f"Gemini API Error: {error_msg}"
            if "429" in error_msg:
                thought = "Gemini API Quota Exceeded (429)."
                
            return {
                "speech": "I've hit a slight cognitive snag with the cloud.",
                "command": None,
                "thought": thought
            }

if __name__ == "__main__":
    # Local test
    async def test():
        b = Brain()
        result = await b.process_command("Check the current directory and list all files.")
        print(result)
    # asyncio.run(test())
