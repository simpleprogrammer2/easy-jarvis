import asyncio
import edge_tts
import os
import subprocess

class Voice:
    def __init__(self, voice="en-US-ChristopherNeural"):
        self.voice = voice
        self.output_file = "response.mp3"

    async def speak(self, text):
        """Generates and plays speech from text."""
        print(f"[*] easy-jarvis Voice: '{text}'")
        
        # 1. Generate MP3
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(self.output_file)

        # 2. Play MP3 (macOS 'afplay')
        try:
            subprocess.run(["afplay", self.output_file], check=True)
        except Exception as e:
            print(f"[!] Voice Error: Could not play audio. {e}")
        finally:
            if os.path.exists(self.output_file):
                os.remove(self.output_file)

if __name__ == "__main__":
    v = Voice()
    asyncio.run(v.speak("Hello, simpleprogrammer. easy-jarvis is online and ready."))
