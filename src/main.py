import asyncio
import os
import sys

# Handle module path for robust execution
try:
    from src.ear import Ear
    from src.voice import Voice
    from src.brain import Brain
    from src.executor import Executor
except ImportError:
    from ear import Ear
    from voice import Voice
    from brain import Brain
    from executor import Executor

from dotenv import load_dotenv

load_dotenv()

class EasyJarvis:
    def __init__(self):
        self.ear = Ear(threshold=3000)
        self.voice = Voice()
        self.brain = Brain()
        self.executor = Executor()
        self.is_active = False

    async def on_wake(self):
        """Auto-wake logic for immediate startup."""
        if self.is_active:
            return
        self.is_active = True
        
        print("\n🍱 easy-jarvis: Session Started.")
        print("[*] Transcript Mode: Monitoring 'transcript.txt' for commands...")
        await self.voice.speak("I am awake and monitoring the transcript. How can I help you build today?")
        
        transcript_file = "transcript.txt"
        
        # Ensure file exists
        if not os.path.exists(transcript_file):
            with open(transcript_file, 'w') as f: f.write("")

        # Command loop (Monitoring File)
        while True:
            try:
                with open(transcript_file, 'r') as f:
                    user_text = f.read().strip()
                
                if user_text:
                    # Clear the transcript file immediately after reading
                    with open(transcript_file, 'w') as f: f.write("")
                    
                    print(f"\n>>> [Transcript Captured]: {user_text}")
                    
                    if user_text.lower() in ["sleep", "exit", "quit"]:
                        await self.voice.speak("Understood. Systems standing by.")
                        break
                        
                    # 1. Brain Reasoning
                    ai_response = await self.brain.process_command(user_text)
                    
                    # 2. Speak Thought/Safety Warning
                    print(f"[*] Thoughts: {ai_response['thought']}")
                    await self.voice.speak(ai_response['speech'])
                    
                    # 3. Execute Command (if provided)
                    if ai_response['command']:
                        output = self.executor.execute(ai_response['command'])
                        print(f"\n--- Terminal Output ---\n{output}\n")
                
                # Small sleep to prevent high CPU usage
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"[!] Transcript Error: {e}")
                await asyncio.sleep(2)
                
        self.is_active = False

    def run(self):
        print("🍱 easy-jarvis: Systems Online. Initializing Auto-Wake...")
        asyncio.run(self.on_wake())

if __name__ == "__main__":
    jarvis = EasyJarvis()
    jarvis.run()
