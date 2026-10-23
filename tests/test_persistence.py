import unittest
import tempfile
from pathlib import Path
from datetime import datetime
from reservas.storage import SQLiteStorage
from reservas.service import create_reservation, cancel_reservation, list_reservations

class TestPersistence(unittest.TestCase):
    def test_persistence_reload(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_db:
            db_path = Path(temp_db.name)

        try:
            now = datetime(2026, 11, 1, 10, 0)
            
            # Session 1: Create active and cancelled reservations
            storage1 = SQLiteStorage(db_path=db_path)
            storage1.init_db()

            res1 = create_reservation("MIC-01", "Ana Pérez", "2026-11-03T10:00", "2026-11-03T11:00", now=now, storage=storage1)
            res2 = create_reservation("OSC-01", "Luis Gómez", "2026-11-03T12:00", "2026-11-03T13:00", now=now, storage=storage1)
            cancel_reservation(res2.id, now=now, storage=storage1)

            # Session 2: Reopen storage on the exact same db file
            storage2 = SQLiteStorage(db_path=db_path)
            
            all_reservations = list_reservations(storage=storage2)
            self.assertEqual(len(all_reservations), 2)

            res1_reloaded = storage2.get_reservation(res1.id)
            res2_reloaded = storage2.get_reservation(res2.id)

            self.assertIsNotNone(res1_reloaded)
            self.assertEqual(res1_reloaded.status, "active")
            self.assertEqual(res1_reloaded.requester, "Ana Pérez")
            self.assertEqual(res1_reloaded.unit_id, "MIC-01")

            self.assertIsNotNone(res2_reloaded)
            self.assertEqual(res2_reloaded.status, "cancelled")
            self.assertEqual(res2_reloaded.requester, "Luis Gómez")
            self.assertEqual(res2_reloaded.unit_id, "OSC-01")
            self.assertIsNotNone(res2_reloaded.cancelled_at)

        finally:
            if db_path.exists():
                db_path.unlink()

if __name__ == "__main__":
    unittest.main()
