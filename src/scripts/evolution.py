import time
import datetime
import subprocess
import os
import asyncio

from src.team.manager import TeamManager

# Configuration for the Autonomous Evolution
CHECK_INTERVAL = 600  # Check every 10 minutes (pacing)


def is_within_working_hours():
    # Jarvis never sleeps. Evolution is 24/7.
    return True


def run_autonomous_cycle():
    """The core loop for the autonomous evolution team."""
    now = datetime.datetime.now()
    print(
        f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ⚙️ Autonomous-Evolution: Starting cycle..."
    )
    team = TeamManager()
    asyncio.run(team.start_shift())


def _setup_git():
    """Ensures git is configured inside the container."""
    try:
        subprocess.run(
            ["git", "config", "--global", "user.name", "EasyJarvis-Team"], check=True
        )
        subprocess.run(
            ["git", "config", "--global", "user.email", "team@easyjarvis.ai"],
            check=True,
        )
        if os.path.exists(".git"):
            subprocess.run(["git", "checkout", "main"], check=True)
    except Exception as e:
        print(f"[!] Git Setup Error: {e}")


def main():
    print("🚀 easy-jarvis: 24/7 Autonomous-Evolution Runner Active")
    _setup_git()

    while True:
        # Evolution loop
        run_autonomous_cycle()

        # Cooldown between task groups to manage API tokens and prevent runaway loops
        print(
            "[*] Task group complete. Standing by for next assignment in 10 minutes..."
        )
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
