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
        print("[*] Chat Mode: Active. Monitoring 'transcript.txt' for commands...")
        print("[*] Chat Log: Reading/Writing to 'chat_log.md' (Read-only for you)")
        await self.voice.speak("I am awake and ready to chat. How can I help you build today?")
        
        transcript_file = "transcript.txt"
        chat_log_file = "chat_log.md"
        
        # Initialize files
        if not os.path.exists(transcript_file):
            with open(transcript_file, 'w') as f: f.write("")
        
        with open(chat_log_file, 'w') as f:
            f.write("# 🍱 easy-jarvis: Active Chat Log\n\n*This log is updated autonomously in real-time.*\n\n---\n")

        # Command loop (Monitoring File)
        while True:
            try:
                with open(transcript_file, 'r') as f:
                    user_text = f.read().strip()
                
                if user_text:
                    # Clear the transcript file immediately after reading
                    with open(transcript_file, 'w') as f: f.write("")
                    
                    print(f"\n>>> [User]: {user_text}")
                    
                    if user_text.lower() in ["sleep", "exit", "quit"]:
                        await self.voice.speak("Understood. I'm taking a nap. Goodbye.")
                        break
                        
                    # 1. Brain Reasoning (Multi-turn)
                    ai_response = await self.brain.process_command(user_text)
                    
                    # 2. Update Chat Log (Read-only for user)
                    with open(chat_log_file, 'a') as f:
                        f.write(f"### 👤 User: {user_text}\n")
                        f.write(f"> **🧠 JARVIS Thoughts:** {ai_response['thought']}\n\n")
                        f.write(f"**🍱 JARVIS:** {ai_response['speech']}\n\n")
                        if ai_response['command']:
                            f.write(f"```bash\n# Executing: {ai_response['command']}\n```\n")
                        f.write("---\n")

                    # 3. Speak Response
                    await self.voice.speak(ai_response['speech'])
                    
                    # 4. Execute Command (if provided)
                    if ai_response['command']:
                        output = self.executor.execute(ai_response['command'])
                        with open(chat_log_file, 'a') as f:
                            f.write(f"**📟 Terminal Output:**\n```text\n{output}\n```\n\n---\n")
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
