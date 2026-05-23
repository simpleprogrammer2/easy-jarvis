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

    def log_habits(self, no_phone: bool, read_book: bool, exercise: bool, meditation: bool):
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
            self.logger.info(f"Weight logged for {date_str}: {weight}lbs")
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
