import os
import datetime
from src.core.config import setup_logging


class MatrixManager:
    """Manages the offline Life-Matrix data persistence (Markdown storage)."""

    def __init__(self):
        self.logger = setup_logging(self.__class__.__name__)
        self.base_path = os.path.join(os.getcwd(), "life-matrix", "health")
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

    def generate_weekend_report(self):
        """Generates a summary of the week's health metrics."""
        today = datetime.date.today()
        # Find last 7 days
        start_date = today - datetime.timedelta(days=7)

        report = "### 📊 WEEKLY HEALTH MATRIX REPORT\n\n"

        # 1. Process Habits
        try:
            with open(self.habits_file, "r") as f:
                lines = f.readlines()[2:]  # Skip header
                habits_count = {
                    "no_phone": 0,
                    "read_book": 0,
                    "exercise": 0,
                    "meditation": 0,
                }
                days_tracked = 0

                for line in lines:
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 5:
                        d = datetime.date.fromisoformat(parts[0])
                        if d >= start_date:
                            days_tracked += 1
                            if "✅" in parts[1]:
                                habits_count["no_phone"] += 1
                            if "✅" in parts[2]:
                                habits_count["read_book"] += 1
                            if "✅" in parts[3]:
                                habits_count["exercise"] += 1
                            if "✅" in parts[4]:
                                habits_count["meditation"] += 1

                report += "**Habit Compliance (Last 7 Days):**\n"
                report += f"- 📱 No Phone: {habits_count['no_phone']}/{days_tracked}\n"
                report += f"- 📚 Reading: {habits_count['read_book']}/{days_tracked}\n"
                report += f"- 🏃 Exercise: {habits_count['exercise']}/{days_tracked}\n"
                report += (
                    f"- 🧘 Meditation: {habits_count['meditation']}/{days_tracked}\n\n"
                )
        except Exception as e:
            report += f"[!] Error processing habits: {e}\n"

        # 2. Process Weight
        try:
            with open(self.weight_file, "r") as f:
                lines = f.readlines()[2:]
                weights = []
                for line in lines:
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 2:
                        d = datetime.date.fromisoformat(parts[0])
                        if d >= start_date:
                            weights.append(float(parts[1]))

                if weights:
                    avg = sum(weights) / len(weights)
                    diff = weights[-1] - weights[0]
                    trend = "📉" if diff < 0 else "📈" if diff > 0 else "➡️"
                    report += "**Weight Metrics:**\n"
                    report += f"- Average: {avg:.1f}kg\n"
                    report += f"- Trend: {trend} {abs(diff):.1f}kg this week\n"
                else:
                    report += "**Weight Metrics:** No data for this week.\n"
        except Exception as e:
            report += f"[!] Error processing weight: {e}\n"

        return report
