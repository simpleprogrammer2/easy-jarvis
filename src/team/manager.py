import time
import datetime
import subprocess
import os
from src.team.personas import Personas

class TeamManager:
    def __init__(self):
        self.roles = {
            "LEADER": Personas.LEADER,
            "FRONTEND": Personas.FRONTEND,
            "BACKEND": Personas.BACKEND,
            "DESIGNER": Personas.DESIGNER
        }

    def start_shift(self):
        print(f"[{datetime.datetime.now()}] 🌙 Team Night-Shift: All members reporting for duty.")
        
        # 1. Leader: Repository Sync & Checkout
        self.role_action("LEADER", "Synchronizing easy-jarvis repository and ensuring main branch checkout.")
        self._leader_sync_repo()
        
        # 2. Leadership Sync: Backlog Review
        self.role_action("LEADER", "Analyzing backlog and setting the night's agenda.")
        
        # 3. Sequential Execution (Teammates collaborating)
        self.role_action("DESIGNER", "Reviewing visual consistency and proposing aesthetic tweaks.")
        self.role_action("BACKEND", "Implementing core logic and infrastructure updates.")
        self.role_action("FRONTEND", "Realizing UI features and template refinements.")
        
        # 4. Final Leader Review
        self.role_action("LEADER", "Finalizing build, running tests, and pushing to main.")
        self._sync_and_push()

    def _leader_sync_repo(self):
        """Leader logic to ensure the codebase is fresh."""
        try:
            print("[*] [LEADER] Running git pull origin main...")
            # We assume the container is started in the repo directory
            subprocess.run(["git", "fetch", "origin"], check=True)
            subprocess.run(["git", "checkout", "main"], check=True)
            subprocess.run(["git", "pull", "origin", "main"], check=True)
            print("[+] [LEADER] Repository synced successfully.")
        except Exception as e:
            print(f"[!] [LEADER] Repo Sync Error: {e}")

    def role_action(self, role, task_description):
        print(f"\n>>> [{role}] Active: {task_description}")
        # Here we would invoke the Brain with the specific persona prompt
        # for that role to actually perform the work.
        time.sleep(2) # Simulating "thinking/working" time

    def _sync_and_push(self):
        try:
            print("[*] Validating team build...")
            # subprocess.run(["pytest"], check=True)
            
            # Simple check for changes
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            if status.stdout.strip():
                print("[+] Changes detected. Syncing team work...")
                # git commands...
            else:
                print("[*] Build stable. No changes to sync.")
        except Exception as e:
            print(f"[!] Team Build Error: {e}")

if __name__ == "__main__":
    manager = TeamManager()
    manager.start_shift()
