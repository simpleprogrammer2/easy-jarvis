import os
import datetime
from src.core.config import setup_logging


class MatrixManager:
    """Manages the offline Life-Matrix data persistence (Markdown storage)."""

    def __init__(self):
        self.logger = setup_logging(self.__class__.__name__)
        self.base_path = os.path.join(os.getcwd(), "data", "life_matrix", "health")
        self.habits_file = os.path.join(self.base_path, "habits.md")
        self.weight_file = os.path.join(self.base_path, "weight.md")

    def log_habits(
        self, no_phone: bool, read_book: bool, exercise: bool, meditation: bool
    ):
        """Appends a new row to the habits Markdown table."""
        date_str = datetime.date.today().isoformat()
        row = f"| {date_str} | {'✅' if no_phone else '❌'} | {'✅' if read_book else '❌'} | {'✅' if exercise else '❌'} | {'✅' if meditation else '❌'} |\n"

        try:
            with open(self.habits_file, "a") as f:
                f.write(row)
            self.logger.info(f"Habits logged for {date_str}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to log habits: {e}")
            return False

    def log_weight(self, weight: float, notes: str = "-"):
        """Appends a new row to the weight Markdown table."""
        date_str = datetime.date.today().isoformat()
        row = f"| {date_str} | {weight} | {notes} |\n"

        try:
            with open(self.weight_file, "a") as f:
                f.write(row)
            self.logger.info(f"Weight logged for {date_str}: {weight}kg")
            return True
        except Exception as e:
            self.logger.error(f"Failed to log weight: {e}")
            return False

    def needs_weight_update(self) -> bool:
        """Checks if weight has been logged today."""
        if not os.path.exists(self.weight_file):
            return True

        date_str = datetime.date.today().isoformat()
        try:
            with open(self.weight_file, "r") as f:
                content = f.read()
                return date_str not in content
        except Exception:
            return True

    def get_habits_history(self, days=7):
        """Returns the last N days of habits data."""
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=days)
        history = []
        try:
            with open(self.habits_file, "r") as f:
                lines = f.readlines()[2:]  # Skip header
                for line in reversed(lines):
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 5:
                        date_str = parts[0]
                        d = datetime.date.fromisoformat(date_str)
                        if d >= start_date:
                            history.append(
                                {
                                    "date": date_str,
                                    "no_phone": "✅" in parts[1],
                                    "read_book": "✅" in parts[2],
                                    "exercise": "✅" in parts[3],
                                    "meditation": "✅" in parts[4],
                                }
                            )
        except Exception as e:
            self.logger.error(f"Failed to read habits history: {e}")
        return history
