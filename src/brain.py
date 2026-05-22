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
        
        if self.mode == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment.")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('models/gemini-1.5-flash', system_instruction=self.system_prompt)
            self.chat = self.model.start_chat(history=[])
        
        self.history = []
        self.max_history = 10

    async def process_command(self, user_input: str):
        """Processes user input using either Local LLM or Gemini."""
        print(f"[*] easy-jarvis Brain ({self.mode} mode): Conversing about '{user_input}'...")
        
        if self.mode == "local":
            return await self._process_local(user_input)
        else:
            return await self._process_gemini(user_input)

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
                "thought": str(e)
            }

    async def _process_gemini(self, user_input: str):
        """Handles inference via Google Gemini API."""
        try:
            response = self.chat.send_message(user_input, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            print(f"[!] Gemini Brain Error: {e}")
            return {"speech": "API snag. Check quota.", "command": None, "thought": str(e)}

if __name__ == "__main__":
    # Local test
    async def test():
        b = Brain()
        result = await b.process_command("Check the current directory and list all files.")
        print(result)
    # asyncio.run(test())
