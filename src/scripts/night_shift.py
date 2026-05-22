import time
import datetime
import subprocess
import os
import sys

from src.team.manager import TeamManager

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
    """The core loop for the overnight teammate team."""
    team = TeamManager()
    team.start_shift()

def _setup_git():
    """Ensures git is configured inside the container."""
    try:
        subprocess.run(["git", "config", "--global", "user.name", "EasyJarvis-Team"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "team@easyjarvis.ai"], check=True)
        # Avoid 'detached HEAD' issues by ensuring we are on main
        if os.path.exists(".git"):
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
