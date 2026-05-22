import time
import datetime
import subprocess
import os
import asyncio
from src.team.personas import Personas
from src.brain import Brain
from src.notifier import Notifier

class TeamManager:
    def __init__(self):
        self.brain = Brain()
        self.notifier = Notifier()
        self.consecutive_failures = 0
        self.max_failures = 3
        self.roles = {
            "LEADER": Personas.LEADER,
            "FRONTEND": Personas.FRONTEND,
            "BACKEND": Personas.BACKEND,
            "DESIGNER": Personas.DESIGNER
        }

    async def start_shift(self):
        print(f"[{datetime.datetime.now()}] 🌙 Team Autonomous-Evolution: All members reporting for duty.")

        # 0. Read the Backlog
        backlog_content = "[Empty Backlog]"
        if os.path.exists("BACKLOG.md"):
            with open("BACKLOG.md", "r") as f:
                backlog_content = f.read()

        # 1. Leader: Mission Briefing
        leader_briefing = await self.role_action("LEADER", f"Current Backlog:\n{backlog_content}\n\nTASK: Review the backlog and pick the single most important task. State as 'MISSION: [task name]'.")
        
        current_mission = "General Improvements"
        if "MISSION:" in leader_briefing.get("speech", ""):
            current_mission = leader_briefing["speech"].split("MISSION:")[1].split("\n")[0].strip()
        
        # Create a unique branch for this mission
        mission_id = current_mission.lower().replace(" ", "-")[:20]
        self.branch_name = f"evolution/{mission_id}-{int(time.time())}"
        self._prepare_branch()

        print(f"🎯 [TEAM] Current Mission: {current_mission} (Branch: {self.branch_name})")

        # 2. Sequential Execution (Teammates collaborating)
        await self.role_action("DESIGNER", f"Mission: {current_mission}. Design the visual components.")
        await self.role_action("BACKEND", f"Mission: {current_mission}. Implement the core logic and run commands to create/edit files.")
        await self.role_action("FRONTEND", f"Mission: {current_mission}. Implement the UI templates and run commands to save them.")

        # 3. Final Leader Review & Push
        await self.role_action("LEADER", f"Mission complete: {current_mission}. Finalizing build.")
        self._sync_and_push(current_mission)

    async def role_action(self, role, task_description):
        from src.executor import Executor
        executor = Executor()
        
        print(f"\n>>> [{role}] Thinking: {task_description}")
        persona_prompt = f"ACT AS: {self.roles[role]}\nTASK: {task_description}\n\nIMPORTANT: Use shell commands (e.g. 'cat > file.py <<EOF...') to save your work."
        
        try:
            ai_response = await self.brain.process_command(persona_prompt)
            
            # Reset failure counter on success (if not a snag)
            if "snag" not in ai_response.get("speech", "").lower() and "trouble thinking" not in ai_response.get("speech", "").lower():
                self.consecutive_failures = 0
            else:
                self.consecutive_failures += 1
                print(f"[!] Warning: Consecutive failure {self.consecutive_failures}/{self.max_failures}")

            print(f"[*] [{role}] Thoughts: {ai_response['thought']}")
            print(f"[*] [{role}] Speech: {ai_response['speech']}")

            if self.consecutive_failures >= self.max_failures:
                self.notifier.send_alert(
                    "Leader Stuck", 
                    f"The Leader has encountered {self.consecutive_failures} consecutive failures during the task: {task_description}. Please check the Colab Brain or API quota."
                )

            if ai_response.get('command'):
                print(f"[*] [{role}] Executing: {ai_response['command']}")
                # RE-ENABLED EXECUTOR FOR AUTONOMOUS BUILDING
                exec_result = executor.execute(ai_response['command'])
                print(f"[#] Result: {exec_result}")

            time.sleep(1) 
            return ai_response
        except Exception as e:
            self.consecutive_failures += 1
            print(f"[!] System Error in {role} turn: {e}")
            if self.consecutive_failures >= self.max_failures:
                self.notifier.send_alert("System Crash", f"Critical error in {role}: {str(e)}")
            return {"speech": "Error occurring.", "thought": str(e), "command": None}

    def _prepare_branch(self):
        try:
            subprocess.run(["git", "checkout", "main"], check=True)
            subprocess.run(["git", "pull", "origin", "main"], check=True)
            subprocess.run(["git", "checkout", "-b", self.branch_name], check=True)
            print(f"[+] Switched to evolution branch: {self.branch_name}")
        except Exception as e:
            print(f"[!] Branch Setup Error: {e}")

    def _sync_and_push(self, mission_name):
        try:
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            if status.stdout.strip():
                print(f"[+] Changes detected for mission: {mission_name}")
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", f"🤖 Evolution: {mission_name}"], check=True)
                
                # Push the branch
                print(f"[*] Pushing {self.branch_name} to GitHub...")
                subprocess.run(["git", "push", "origin", self.branch_name], check=True)
                
                print(f"🚀 MISSION UPLOADED! Check your branches: https://github.com/simpleprogrammer2/easy-jarvis/branches")
                self.notifier.send_alert("Mission Uploaded", f"Jarvis has completed '{mission_name}'. Review the PR here: https://github.com/simpleprogrammer2/easy-jarvis/compare/{self.branch_name}")
                
                # Switch back to main for next cycle
                subprocess.run(["git", "checkout", "main"], check=True)
            else:
                print("[*] No changes were made by the team. Skipping push.")
        except Exception as e:
            print(f"[!] Team Push Error: {e}")

if __name__ == "__main__":
    manager = TeamManager()
    asyncio.run(manager.start_shift())
