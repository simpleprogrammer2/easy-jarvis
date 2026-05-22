import asyncio
import os
import sys
from src.ear import Ear
from src.voice import Voice
from src.brain import Brain
from src.executor import Executor
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
        """Logic for when JARVIS is woken up by a double-clap."""
        if self.is_active: return
        self.is_active = True
        
        print("\n🍱 easy-jarvis: Session Started.")
        await self.voice.speak("I'm here. How can I help you build today?")
        
        # In this skeleton, we'll use input() as a placeholder for Whisper STT
        # This allows you to test the Brain/Executor loop via typing for now.
        while True:
            user_text = input("\n>>> [Voice Mock] Speak to JARVIS (or type 'sleep'): ")
            
            if user_text.lower() in ["sleep", "exit", "quit"]:
                await self.voice.speak("Understood. I'm going back to sleep. Just double-clap if you need me.")
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
                
        self.is_active = False

    def run(self):
        print("🍱 easy-jarvis: Systems Online. Monitoring for claps...")
        # Since start_listening is blocking, we wrap on_wake in a runner
        def wake_wrapper():
            asyncio.run(self.on_wake())
            
        self.ear.start_listening(wake_wrapper)

if __name__ == "__main__":
    jarvis = EasyJarvis()
    jarvis.run()
