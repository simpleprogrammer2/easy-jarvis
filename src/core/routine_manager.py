import datetime
from src.core.database import get_connection


class RoutineManager:
    def __init__(self):
        self.conn = get_connection()

    def list_routines(self, domain=None, active=True):
        cursor = self.conn.cursor()
        query = "SELECT * FROM routines WHERE 1=1"
        params = []
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        if active is not None:
            query += " AND active = ?"
            params.append(1 if active else 0)
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_routine(self, routine_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM routines WHERE id = ?", (routine_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def create_routine(self, title, domain, schedule, notes=""):
        cursor = self.conn.cursor()
        created_at = datetime.datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO routines (title, domain, schedule, notes, active, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (title, domain, schedule, notes, 1, created_at),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_routine(self, routine_id, payload):
        fields = []
        params = []
        for key in ["title", "domain", "schedule", "notes", "active"]:
            if key in payload:
                fields.append(f"{key} = ?")
                params.append(payload[key])
        if not fields:
            return self.get_routine(routine_id)

        params.append(routine_id)
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE routines SET {', '.join(fields)} WHERE id = ?",
            params,
        )
        self.conn.commit()
        return self.get_routine(routine_id)

    def delete_routine(self, routine_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM routines WHERE id = ?", (routine_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def log_routine(self, routine_id, status, notes=""):
        cursor = self.conn.cursor()
        now = datetime.datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO routine_logs (routine_id, log_date, status, notes, created_at) VALUES (?, ?, ?, ?, ?)",
            (routine_id, now[:10], status, notes, now),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_routine_logs(self, routine_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM routine_logs WHERE routine_id = ? ORDER BY created_at DESC",
            (routine_id,),
        )
        return [dict(row) for row in cursor.fetchall()]
