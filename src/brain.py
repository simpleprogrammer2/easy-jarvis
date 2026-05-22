import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class Brain:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-flash-latest')
        
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
        # Initialize chat session with system instructions
        self.chat = self.model.start_chat(history=[])
        self._set_system_instructions()

    def _set_system_instructions(self):
        """Initializes the chat with the system prompt."""
        # For Flash 1.5, we send the system prompt as the first message
        self.chat.send_message(f"SYSTEM INSTRUCTIONS: {self.system_prompt}")

    async def process_command(self, user_input: str):
        """Processes user input in a multi-turn chat session."""
        print(f"[*] easy-jarvis Brain: Conversing about '{user_input}'...")
        
        try:
            response = self.chat.send_message(
                user_input,
                generation_config={"response_mime_type": "application/json"}
            )
            
            import json
            return json.loads(response.text)
        except Exception as e:
            print(f"[!] Brain Error: {e}")
            return {
                "speech": "I've hit a slight cognitive snag. Could you rephrase?",
                "command": None,
                "thought": str(e)
            }

if __name__ == "__main__":
    # Local test
    async def test():
        b = Brain()
        result = await b.process_command("Check the current directory and list all files.")
        print(result)
    # asyncio.run(test())
