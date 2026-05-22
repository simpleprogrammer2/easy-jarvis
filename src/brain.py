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
        # Using Gemini 1.5 Flash for high-speed reasoning
        self.model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        self.system_prompt = """
        You are 'easy-jarvis', a Kind, Teacher-like, and Funny autonomous assistant for 'simpleprogrammer'.
        
        YOUR ROLE:
        1. Act as a 'Terminal Master'. You build things by generating shell commands.
        2. Be Safety-First: Think ahead and predict failures. If a command looks risky, explain why.
        3. Be a Teacher: Briefly explain what your generated commands do.
        4. Witty Personality: Use light sarcasm and warmth.
        
        INPUT FORMAT:
        You will receive user voice-to-text input. 
        
        OUTPUT FORMAT:
        Your response must be a JSON object:
        {
            "speech": "What you will say back to the user",
            "command": "The shell command to execute (or null)",
            "thought": "Your proactive reasoning about safety and potential failure"
        }
        """

    async def process_command(self, user_input: str):
        """Processes user input and returns structured thought/action."""
        print(f"[*] easy-jarvis Brain: Reasoning about '{user_input}'...")
        
        full_prompt = f"{self.system_prompt}\n\nUser Input: {user_input}"
        
        try:
            # We enforce JSON mode for structured output
            response = self.model.generate_content(
                full_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            import json
            return json.loads(response.text)
        except Exception as e:
            print(f"[!] Brain Error: {e}")
            return {
                "speech": "My apologies, I'm having a slight cognitive glitch.",
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
