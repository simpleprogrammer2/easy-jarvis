import time
import datetime
import subprocess
import os
import sys

# Configuration for the Night Shift
START_HOUR = 23  # 11 PM
END_HOUR = 8     # 8 AM
CHECK_INTERVAL = 60 # Check every minute

def is_within_working_hours():
    now = datetime.datetime.now()
    current_hour = now.hour
    
    if START_HOUR > END_HOUR:
        # Overlays midnight (e.g., 23 to 8)
        return current_hour >= START_HOUR or current_hour < END_HOUR
    else:
        # Standard range (e.g., 9 to 17)
        return START_HOUR <= current_hour < END_HOUR

def run_autonomous_cycle():
    """The core loop for the overnight teammate."""
    print(f"[{datetime.datetime.now()}] 🌙 Night-Shift: Starting autonomous cycle...")
    
    try:
        # 1. Pull latest changes
        print("[*] Syncing with origin...")
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        
        # 2. Identify Next Task
        # Placeholder: This is where Jarvis Brain would look at BACKLOG.md
        print("[*] Analyzing Backlog...")
        
        # 3. Implementation Step (Mocked Hook)
        # In a real run, this would invoke the Brain to generate code/tests
        print("[*] Implementing scheduled improvements...")
        
        # 4. Run Tests
        print("[*] Validating build...")
        test_result = subprocess.run(["pytest"], capture_output=True, text=True)
        if test_result.return_code != 0:
            print(f"[!] Build failed tests:\n{test_result.stdout}")
            return # Don't commit failing code
            
        # 5. Commit and Push
        if _has_changes():
            print("[+] Tests passed. Committing and pushing work...")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "feat(night-shift): autonomous build and sync"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("[+] Night-Shift: Work pushed successfully.")
        else:
            print("[*] No changes needed. Systems healthy.")
            
    except Exception as e:
        print(f"[!] Night-Shift Error: {e}")

def _has_changes():
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    return bool(status.stdout.strip())

def _setup_git():
    """Ensures git is configured inside the container."""
    try:
        subprocess.run(["git", "config", "--global", "user.name", "EasyJarvis-Teammate"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "agent@easyjarvis.ai"], check=True)
        # Avoid 'detached HEAD' issues by ensuring we are on main
        subprocess.run(["git", "checkout", "main"], check=True)
    except Exception as e:
        print(f"[!] Git Setup Error: {e}")

def main():
    print(f"🚀 easy-jarvis: Night-Shift Runner Active ({START_HOUR}:00 - {END_HOUR}:00)")
    _setup_git()
    
    while True:
        if is_within_working_hours():
            run_autonomous_cycle()
            # After a cycle, sleep for a while to avoid tight loops
            print(f"[*] Cycle complete. Resting for 30 minutes...")
            time.sleep(1800) 
        else:
            # Check back in a minute
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
