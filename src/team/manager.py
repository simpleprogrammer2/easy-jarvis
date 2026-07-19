import time
import datetime
import subprocess
import os
import asyncio
import requests
import re
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
            "DESIGNER": Personas.DESIGNER,
            "INFRA": Personas.INFRA,
        }

    async def start_shift(self):
        print(
            f"[{datetime.datetime.now()}] 🌙 Team Autonomous-Evolution: All members reporting for duty."
        )

        # 0. Read the Backlog
        backlog_content = "[Empty Backlog]"
        if os.path.exists("BACKLOG.md"):
            with open("BACKLOG.md", "r") as f:
                backlog_content = f.read()

        # 1. Leader: Mission Briefing
        leader_briefing = await self.role_action(
            "LEADER",
            f"Current Backlog:\n{backlog_content}\n\nTASK: Review the backlog and pick the single most important task. State as 'MISSION: [task name]'",
        )

        current_mission = "General Improvements"
        if "MISSION:" in leader_briefing.get("speech", ""):
            current_mission = (
                leader_briefing["speech"].split("MISSION:")[1].split("\n")[0].strip()
            )

        # Create a unique branch for this mission
        mission_id = current_mission.lower().replace(" ", "-")
        mission_id = re.sub(r"[^a-z0-9-]", "", mission_id)[:20]
        mission_id = re.sub(r"-+", "-", mission_id).strip("-")

        self.branch_name = f"evolution/{mission_id}-{int(time.time())}"
        self._prepare_branch()

        print(
            f"🎯 [TEAM] Current Mission: {current_mission} (Branch: {self.branch_name})"
        )

        # 2. Sequential Execution (Teammates collaborating on the mission)
        await self.role_action(
            "DESIGNER", f"Mission: {current_mission}. Design the visual components."
        )
        await self.role_action(
            "BACKEND",
            f"Mission: {current_mission}. Implement the core logic and run commands to create/edit files.",
        )
        await self.role_action(
            "FRONTEND",
            f"Mission: {current_mission}. Implement the UI templates and run commands to save them.",
        )

        # 3. Infrastructure & Monitoring Check
        infra_report = await self.role_action(
            "INFRA",
            f"Mission: {current_mission}. Verify build stability and ensure CI/CD monitoring is active. If previous deployments failed or errors were detected, create a recovery script or diagnostic command.",
        )

        # 4. Final Leader Review & Push
        # If Infra detected a critical blocker, Leader asks for a fix before pushing
        if (
            "blocker" in infra_report.get("speech", "").lower()
            or "fail" in infra_report.get("speech", "").lower()
        ):
            print(
                "[!] INFRA detected a potential blocker. Requesting emergency recovery logic..."
            )
            await self.role_action(
                "INFRA",
                "CRITICAL: The build or deployment is unstable. Generate a specific shell command to fix the infrastructure or provide a rollback script immediately.",
            )

        await self.role_action(
            "LEADER", f"Mission complete: {current_mission}. Finalizing build."
        )
        self._sync_and_push(current_mission)

    async def role_action(self, role, task_description):
        from src.executor import Executor

        executor = Executor()

        print(f"\n>>> [{role}] Thinking: {task_description}")
        persona_prompt = f"""
        ACT AS: {self.roles[role]}
        TASK: {task_description}
        
        CRITICAL: You are in AUTONOMOUS MODE. 
        - If you write code, YOU MUST provide a shell command to save it (e.g., 'cat > filename.py <<EOF...').
        - Do not just talk about code. WRITE it to the disk.
        - Ensure your JSON 'command' field is populated with the save command.
        """

        try:
            ai_response = await self.brain.process_command(persona_prompt)

            # Reset failure counter on success (if not a snag)
            if (
                "snag" not in ai_response.get("speech", "").lower()
                and "trouble thinking" not in ai_response.get("speech", "").lower()
            ):
                self.consecutive_failures = 0
            else:
                self.consecutive_failures += 1
                print(
                    f"[!] Warning: Consecutive failure {self.consecutive_failures}/{self.max_failures}"
                )

            print(f"[*] [{role}] Thoughts: {ai_response['thought']}")
            print(f"[*] [{role}] Speech: {ai_response['speech']}")

            if self.consecutive_failures >= self.max_failures:
                self.notifier.send_alert(
                    "Leader Stuck",
                    f"The Leader has encountered {self.consecutive_failures} consecutive failures during the task: {task_description}. Please check the Colab Brain or API quota.",
                )

            if ai_response.get("command"):
                print(f"[*] [{role}] Executing: {ai_response['command']}")
                exec_result = executor.execute(ai_response["command"])
                print(f"[#] Result: {exec_result}")

            time.sleep(1)
            return ai_response
        except Exception as e:
            self.consecutive_failures += 1
            print(f"[!] System Error in {role} turn: {e}")
            if self.consecutive_failures >= self.max_failures:
                self.notifier.send_alert(
                    "System Crash", f"Critical error in {role}: {str(e)}"
                )
            return {"speech": "Error occurring.", "thought": str(e), "command": None}

    def _prepare_branch(self):
        try:
            # Inject GITHUB_TOKEN into remote URL for authentication
            token = os.getenv("GITHUB_TOKEN")
            if token:
                remote_info = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    capture_output=True,
                    text=True,
                )
                current_url = remote_info.stdout.strip()
                if "github.com" in current_url and "@github.com" not in current_url:
                    new_url = current_url.replace(
                        "https://github.com/",
                        f"https://x-access-token:{token}@github.com/",
                    )
                    subprocess.run(
                        ["git", "remote", "set-url", "origin", new_url], check=True
                    )
                    print("[+] GITHUB_TOKEN injected into remote URL.")

            subprocess.run(["git", "checkout", "main"], check=True)
            subprocess.run(["git", "pull", "origin", "main"], check=True)
            subprocess.run(["git", "checkout", "-b", self.branch_name], check=True)
            print(f"[+] Switched to evolution branch: {self.branch_name}")
        except Exception as e:
            print(f"[!] Branch Setup Error: {e}")

    def _sync_and_push(self, mission_name):
        try:
            status = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True
            )
            if status.stdout.strip():
                print(f"[+] Changes detected for mission: {mission_name}")
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(
                    ["git", "commit", "-m", f"🤖 Evolution: {mission_name}"], check=True
                )

                # Push the branch
                print(f"[*] Pushing {self.branch_name} to GitHub...")
                subprocess.run(["git", "push", "origin", self.branch_name], check=True)

                # Create Pull Request via GitHub REST API
                self._create_github_pr(mission_name)

                # Switch back to main for next cycle
                subprocess.run(["git", "checkout", "main"], check=True)
            else:
                print("[*] No changes were made by the team. Skipping push.")
        except Exception as e:
            print(f"[!] Team Push Error: {e}")

    def _create_github_pr(self, mission_name):
        """Creates a Pull Request using the GitHub REST API."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            print("[!] PR Error: GITHUB_TOKEN not set.")
            return

        # Get repo owner and name from git remote
        try:
            remote_info = subprocess.run(
                ["git", "remote", "get-url", "origin"], capture_output=True, text=True
            )
            url = remote_info.stdout.strip()
            # Handle both https and ssh formats
            repo_path = url.split("github.com/")[1].replace(".git", "")
            owner, repo = repo_path.split("/")
            if ":" in owner:
                owner = owner.split(":")[-1]  # Handle x-access-token format
        except Exception as e:
            print(f"[!] PR Error parsing remote: {e}")
            return

        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        data = {
            "title": f"🤖 Evolution: {mission_name}",
            "body": f"This PR was generated autonomously by JARVIS.\n\n**Mission:** {mission_name}\n**Status:** Built and Verified locally.",
            "head": self.branch_name,
            "base": "main",
        }

        try:
            print(f"[*] Creating Pull Request for {self.branch_name}...")
            response = requests.post(api_url, headers=headers, json=data)
            if response.status_code == 201:
                pr_url = response.json().get("html_url")
                print(f"🚀 PULL REQUEST CREATED: {pr_url}")
                self.notifier.send_alert(
                    "PR Created",
                    f"Jarvis has completed '{mission_name}'. Review the PR here: {pr_url}",
                )
            else:
                print(f"[!] PR Failed ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"[!] PR API Error: {e}")


if __name__ == "__main__":
    manager = TeamManager()
    asyncio.run(manager.start_shift())
