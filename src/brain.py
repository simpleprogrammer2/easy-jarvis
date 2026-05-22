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
        
        # Use native system_instruction to save tokens in chat history
        self.model = genai.GenerativeModel(
            'models/gemini-1.5-flash',
            system_instruction=self.system_prompt
        )
        
        # Initialize chat session
        self.chat = self.model.start_chat(history=[])
        self.max_history = 10 # Keep only last 10 exchanges to save tokens

    async def process_command(self, user_input: str):
        """Processes user input in a multi-turn chat session."""
        print(f"[*] easy-jarvis Brain: Conversing about '{user_input}'...")
        
        # Prune history if it gets too long to stay within free tier token limits
        if len(self.chat.history) > self.max_history * 2:
            self.chat.history = self.chat.history[-(self.max_history * 2):]
        
        try:
            response = self.chat.send_message(
                user_input,
                generation_config={"response_mime_type": "application/json"}
            )
            
            # Robust JSON cleaning
            raw_text = response.text.strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()
            
            import json
            return json.loads(raw_text)
        except Exception as e:
            error_msg = str(e)
            print(f"[!] Brain Error: {error_msg}")
            
            # Quota handling (429)
            if "429" in error_msg:
                return {
                    "speech": "I've hit my daily thinking quota. I'll take a short nap and try again later.",
                    "command": None,
                    "thought": "Gemini API Quota Exceeded (429)."
                }
                
            return {
                "speech": "I've hit a slight cognitive snag. Could you rephrase?",
                "command": None,
                "thought": f"Error: {error_msg}"
            }

if __name__ == "__main__":
    # Local test
    async def test():
        b = Brain()
        result = await b.process_command("Check the current directory and list all files.")
        print(result)
    # asyncio.run(test())
