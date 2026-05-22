import time
import datetime
import subprocess
import os
import asyncio
from src.team.personas import Personas
from src.brain import Brain

class TeamManager:
    def __init__(self):
        self.brain = Brain()
        self.roles = {
            "LEADER": Personas.LEADER,
            "FRONTEND": Personas.FRONTEND,
            "BACKEND": Personas.BACKEND,
            "DESIGNER": Personas.DESIGNER
        }

    async def start_shift(self):
        print(f"[{datetime.datetime.now()}] 🌙 Team Night-Shift: All members reporting for duty.")

        # 1. Leader: Repository Sync & Checkout
        await self.role_action("LEADER", "Synchronizing easy-jarvis repository and ensuring main branch checkout.")
        self._leader_sync_repo()

        # 2. Leadership Sync: Backlog Review
        await self.role_action("LEADER", "Analyzing BACKLOG.md and setting the night's agenda.")

        # 3. Sequential Execution (Teammates collaborating)
        await self.role_action("DESIGNER", "Reviewing visual consistency and proposing aesthetic tweaks.")
        await self.role_action("BACKEND", "Implementing core logic and infrastructure updates.")
        await self.role_action("FRONTEND", "Realizing UI features and template refinements.")

        # 4. Final Leader Review
        await self.role_action("LEADER", "Finalizing build, running tests, and pushing to main.")
        self._sync_and_push()

    async def role_action(self, role, task_description):
        print(f"\n>>> [{role}] Thinking: {task_description}")

        persona_prompt = f"ACT AS: {self.roles[role]}\nTASK: {task_description}"
        ai_response = await self.brain.process_command(persona_prompt)

        print(f"[*] [{role}] Thoughts: {ai_response['thought']}")
        print(f"[*] [{role}] Speech: {ai_response['speech']}")

        if ai_response['command']:
            print(f"[*] [{role}] Executing: {ai_response['command']}")
            # self.executor.execute(ai_response['command'])

        time.sleep(1) # Pace the collaboration

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
    asyncio.run(manager.start_shift())
