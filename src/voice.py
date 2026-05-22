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
        
        # In Docker, we often don't have audio hardware access.
        # The browser-based Console handles TTS now.
        if os.path.exists("/.dockerenv"):
            print("[*] Voice: Running in Docker. Skipping server-side audio playback (Browser will handle it).")
            return

        # 1. Generate MP3
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(self.output_file)

        # 2. Play MP3
        try:
            # Check for available players
            if subprocess.run(["which", "afplay"], capture_output=True).returncode == 0:
                subprocess.run(["afplay", self.output_file], check=True)
            elif subprocess.run(["which", "mpg123"], capture_output=True).returncode == 0:
                subprocess.run(["mpg123", "-q", self.output_file], check=True)
            else:
                print("[!] Voice: No supported audio player found (afplay/mpg123).")
        except Exception as e:
            print(f"[!] Voice Error: {e}")
        finally:
            if os.path.exists(self.output_file):
                os.remove(self.output_file)

if __name__ == "__main__":
    v = Voice()
    asyncio.run(v.speak("Hello, simpleprogrammer. easy-jarvis is online and ready."))
