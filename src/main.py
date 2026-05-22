import asyncio
from src.ear import Ear
from src.voice import Voice
import os

class EasyJarvis:
    def __init__(self):
        self.ear = Ear(threshold=3000)
        self.voice = Voice()

    def on_wake(self):
        """Callback for when a double-clap is detected."""
        asyncio.run(self.voice.speak("Systems online. At your service, simpleprogrammer."))

    def run(self):
        print("🍱 easy-jarvis: Initializing Physical Foundation...")
        self.ear.start_listening(self.on_wake)

if __name__ == "__main__":
    jarvis = EasyJarvis()
    jarvis.run()
