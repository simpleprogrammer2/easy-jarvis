import pyaudio
import numpy as np
import time
import os

class Ear:
    def __init__(self, threshold=1000, chunk_size=1024, rate=44100):
        self.threshold = threshold
        self.chunk_size = chunk_size
        self.rate = rate
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.last_clap_time = 0
        self.double_clap_window = (0.1, 1.0) # seconds

    def start_listening(self, on_wake_callback):
        """Starts the audio stream and listens for claps."""
        try:
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            print("[*] easy-jarvis Ear: Listening for double-claps...")
        except Exception as e:
            print(f"[!] Ear Error: Could not open microphone. {e}")
            self._start_mock_listener(on_wake_callback)
            return

        while True:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                rms = np.sqrt(np.mean(audio_data.astype(float)**2))

                if rms > self.threshold:
                    self._handle_clap(on_wake_callback)

            except Exception as e:
                print(f"[!] Stream Error: {e}")
                break

    def _handle_clap(self, on_wake_callback):
        current_time = time.time()
        time_since_last = current_time - self.last_clap_time
        
        if self.double_clap_window[0] < time_since_last < self.double_clap_window[1]:
            print("[+] Double-clap detected! Waking up...")
            on_wake_callback()
            self.last_clap_time = 0 # Reset
        else:
            self.last_clap_time = current_time

    def _start_mock_listener(self, on_wake_callback):
        """Fallback listener that uses a file trigger for testing."""
        print("[!] Falling back to MOCK EAR. Use 'touch wake.trigger' to wake easy-jarvis.")
        trigger_file = "wake.trigger"
        if os.path.exists(trigger_file): os.remove(trigger_file)
        
        while True:
            if os.path.exists(trigger_file):
                print("[+] Mock trigger detected! Waking up...")
                os.remove(trigger_file)
                on_wake_callback()
            time.sleep(1)

if __name__ == "__main__":
    def my_callback():
        print(">>> JARVIS: I am awake. What can I do for you?")
    
    ear = Ear(threshold=3000) # Adjust threshold as needed
    ear.start_listening(my_callback)
