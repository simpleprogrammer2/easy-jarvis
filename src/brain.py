import os
import requests
import json
import google.generativeai as genai
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
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('models/gemini-1.5-flash', system_instruction=self.system_prompt)
                self.gemini_chat = self.gemini_model.start_chat(history=[])
                self.gemini_ready = True
            except Exception as e:
                print(f"[!] Gemini Init Warning: {e}")

        self.history = []
        self.max_history = 10

    async def process_command(self, user_input: str):
        """Processes user input with automatic fallback logic."""
        print(f"[*] easy-jarvis Brain ({self.mode} primary): Conversing about '{user_input}'...")
        
        if self.mode == "local":
            result = await self._process_local(user_input)
            # If local failed, attempt Gemini fallback
            if "trouble thinking locally" in result.get("speech", "") and self.gemini_ready:
                print("[*] Local LLM unavailable. Falling back to Gemini API...")
                return await self._process_gemini(user_input)
            return result
        else:
            result = await self._process_gemini(user_input)
            # If Gemini hits quota, attempt local fallback
            if "quota" in result.get("thought", "").lower():
                print("[*] Gemini quota hit. Falling back to Local LLM...")
                return await self._process_local(user_input)
            return result

    async def _process_local(self, user_input: str):
        """Handles inference via local llama.cpp server."""
        self.history.append({"role": "user", "content": user_input})
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-(self.max_history * 2):]

        payload = {
            "messages": [{"role": "system", "content": self.system_prompt}] + self.history,
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(self.local_url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Record assistant response in history
            self.history.append({"role": "assistant", "content": content})
            
            return json.loads(content)
        except Exception as e:
            print(f"[!] Local Brain Error: {e}")
            return {
                "speech": "I'm having trouble thinking locally. Is the model server running?",
                "command": None,
                "thought": f"Local LLM Error: {str(e)}"
            }

    async def _process_gemini(self, user_input: str):
        """Handles inference via Google Gemini API."""
        if not self.gemini_ready:
            return {"speech": "Gemini not configured.", "command": None, "thought": "API key missing."}
            
        try:
            response = self.gemini_chat.send_message(user_input, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)
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
