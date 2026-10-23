import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from .models import Reservation

def get_default_db_path() -> Path:
    root = Path(__file__).resolve().parent.parent.parent
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "reservas.db"

class SQLiteStorage:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_default_db_path()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        conn = self._get_connection()
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reservations (
                    id TEXT PRIMARY KEY,
                    unit_id TEXT NOT NULL,
                    requester TEXT NOT NULL,
                    start TEXT NOT NULL,
                    end TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    cancelled_at TEXT
                )
            """)
        conn.close()

    def save_reservation(self, res: Reservation) -> None:
        conn = self._get_connection()
        with conn:
            conn.execute("""
                INSERT OR REPLACE INTO reservations (id, unit_id, requester, start, end, status, created_at, cancelled_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                res.id,
                res.unit_id,
                res.requester,
                res.start.strftime("%Y-%m-%dT%H:%M"),
                res.end.strftime("%Y-%m-%dT%H:%M"),
                res.status,
                res.created_at.strftime("%Y-%m-%dT%H:%M"),
                res.cancelled_at.strftime("%Y-%m-%dT%H:%M") if res.cancelled_at else None
            ))
        conn.close()

    def get_reservation(self, res_id: str) -> Optional[Reservation]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservations WHERE id = ?", (res_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return self._row_to_reservation(row)

    def get_reservations(self, unit_id: Optional[str] = None, status: Optional[str] = None) -> List[Reservation]:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM reservations WHERE 1=1"
        params = []
        if unit_id:
            query += " AND unit_id = ?"
            params.append(unit_id)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY start ASC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_reservation(row) for row in rows]

    def update_reservation_status(self, res_id: str, status: str, cancelled_at: Optional[datetime] = None) -> None:
        conn = self._get_connection()
        with conn:
            conn.execute("""
                UPDATE reservations 
                SET status = ?, cancelled_at = ?
                WHERE id = ?
            """, (
                status,
                cancelled_at.strftime("%Y-%m-%dT%H:%M") if cancelled_at else None,
                res_id
            ))
        conn.close()

    def _row_to_reservation(self, row: sqlite3.Row) -> Reservation:
        return Reservation(
            id=row["id"],
            unit_id=row["unit_id"],
            requester=row["requester"],
            start=datetime.strptime(row["start"], "%Y-%m-%dT%H:%M"),
            end=datetime.strptime(row["end"], "%Y-%m-%dT%H:%M"),
            status=row["status"],
            created_at=datetime.strptime(row["created_at"], "%Y-%m-%dT%H:%M"),
            cancelled_at=datetime.strptime(row["cancelled_at"], "%Y-%m-%dT%H:%M") if row["cancelled_at"] else None
        )
