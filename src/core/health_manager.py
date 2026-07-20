import datetime
from src.core.database import get_connection


class HealthManager:
    def __init__(self):
        self.conn = get_connection()

    def log_weight(self, weight: float, notes: str = ""):
        cursor = self.conn.cursor()
        now = datetime.datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO weight_logs (log_date, weight, notes, created_at) VALUES (?, ?, ?, ?)",
            (now[:10], weight, notes, now),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_weight_history(self, days: int = 14):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM weight_logs ORDER BY created_at DESC LIMIT ?",
            (days,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def log_habits(
        self,
        no_phone: bool,
        read_book: bool,
        exercise: bool,
        meditation: bool,
        notes: str = "",
    ):
        cursor = self.conn.cursor()
        now = datetime.datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO habit_logs (log_date, no_phone, read_book, exercise, meditation, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                now[:10],
                int(no_phone),
                int(read_book),
                int(exercise),
                int(meditation),
                notes,
                now,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_recent_habits(self, days: int = 7):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM habit_logs ORDER BY created_at DESC LIMIT ?",
            (days,),
        )
        return [dict(row) for row in cursor.fetchall()]
