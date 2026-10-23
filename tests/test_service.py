import unittest
import tempfile
from pathlib import Path
from datetime import datetime
from reservas.storage import SQLiteStorage
from reservas.service import create_reservation, cancel_reservation, check_availability, list_reservations
from reservas.models import ConflictError, ValidationError, NotFoundError

class TestService(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = Path(self.temp_db.name)
        self.storage = SQLiteStorage(db_path=self.db_path)
        self.storage.init_db()
        self.now = datetime(2026, 11, 1, 10, 0)

    def tearDown(self):
        if self.db_path.exists():
            self.db_path.unlink()

    def test_valid_creation_and_availability(self):
        unit = "MIC-01"
        start = "2026-11-03T10:00"
        end = "2026-11-03T11:00"

        # Initially available
        self.assertTrue(check_availability(unit, start, end, now=self.now, storage=self.storage))

        # Create reservation
        res = create_reservation(unit, "Ana Pérez", start, end, now=self.now, storage=self.storage)
        self.assertEqual(res.unit_id, unit)
        self.assertEqual(res.requester, "Ana Pérez")
        self.assertEqual(res.status, "active")

        # Now unavailable
        self.assertFalse(check_availability(unit, start, end, now=self.now, storage=self.storage))

        # Trying to reserve same slot raises ConflictError
        with self.assertRaises(ConflictError):
            create_reservation(unit, "Luis Gómez", start, end, now=self.now, storage=self.storage)

    def test_overlap_rejections(self):
        unit = "MIC-01"
        # Base reservation: 10:00 - 12:00
        create_reservation(unit, "Ana Pérez", "2026-11-03T10:00", "2026-11-03T12:00", now=self.now, storage=self.storage)

        # 1. Idéntica: 10:00 - 12:00
        self.assertFalse(check_availability(unit, "2026-11-03T10:00", "2026-11-03T12:00", now=self.now, storage=self.storage))
        with self.assertRaises(ConflictError):
            create_reservation(unit, "Otro", "2026-11-03T10:00", "2026-11-03T12:00", now=self.now, storage=self.storage)

        # 2. Contenida: 10:30 - 11:30
        self.assertFalse(check_availability(unit, "2026-11-03T10:30", "2026-11-03T11:30", now=self.now, storage=self.storage))
        with self.assertRaises(ConflictError):
            create_reservation(unit, "Otro", "2026-11-03T10:30", "2026-11-03T11:30", now=self.now, storage=self.storage)

        # 3. Contenedora: 09:00 - 13:00
        self.assertFalse(check_availability(unit, "2026-11-03T09:00", "2026-11-03T13:00", now=self.now, storage=self.storage))
        with self.assertRaises(ConflictError):
            create_reservation(unit, "Otro", "2026-11-03T09:00", "2026-11-03T13:00", now=self.now, storage=self.storage)

        # 4. Solapamiento parcial (inicio dentro): 11:00 - 13:00 (espera: fin de base es 12:00, 11:00-13:00 solapa con 10:00-12:00)
        self.assertFalse(check_availability(unit, "2026-11-03T11:00", "2026-11-03T13:00", now=self.now, storage=self.storage))
        with self.assertRaises(ConflictError):
            create_reservation(unit, "Otro", "2026-11-03T11:00", "2026-11-03T13:00", now=self.now, storage=self.storage)

        # 5. Solapamiento parcial (fin dentro): 09:00 - 11:00
        self.assertFalse(check_availability(unit, "2026-11-03T09:00", "2026-11-03T11:00", now=self.now, storage=self.storage))
        with self.assertRaises(ConflictError):
            create_reservation(unit, "Otro", "2026-11-03T09:00", "2026-11-03T11:00", now=self.now, storage=self.storage)

    def test_consecutive_limits_allowed(self):
        unit = "MIC-01"
        # Base: 10:00 - 11:00
        create_reservation(unit, "Ana Pérez", "2026-11-03T10:00", "2026-11-03T11:00", now=self.now, storage=self.storage)

        # Turno consecutivo posterior: 11:00 - 12:00 (permitido)
        self.assertTrue(check_availability(unit, "2026-11-03T11:00", "2026-11-03T12:00", now=self.now, storage=self.storage))
        res2 = create_reservation(unit, "Luis Gómez", "2026-11-03T11:00", "2026-11-03T12:00", now=self.now, storage=self.storage)
        self.assertEqual(res2.status, "active")

        # Turno consecutivo anterior: 09:00 - 10:00 (permitido)
        self.assertTrue(check_availability(unit, "2026-11-03T09:00", "2026-11-03T10:00", now=self.now, storage=self.storage))
        res3 = create_reservation(unit, "Carlos Ruiz", "2026-11-03T09:00", "2026-11-03T10:00", now=self.now, storage=self.storage)
        self.assertEqual(res3.status, "active")

    def test_simultaneous_distinct_units(self):
        start = "2026-11-03T10:00"
        end = "2026-11-03T11:00"

        res1 = create_reservation("MIC-01", "Ana Pérez", start, end, now=self.now, storage=self.storage)
        self.assertEqual(res1.unit_id, "MIC-01")

        # Unidades distintas pueden coincidir en horario
        self.assertTrue(check_availability("MIC-02", start, end, now=self.now, storage=self.storage))
        res2 = create_reservation("MIC-02", "Luis Gómez", start, end, now=self.now, storage=self.storage)
        self.assertEqual(res2.unit_id, "MIC-02")

    def test_cancellation_frees_slot(self):
        unit = "MIC-01"
        start = "2026-11-03T10:00"
        end = "2026-11-03T11:00"

        res = create_reservation(unit, "Ana Pérez", start, end, now=self.now, storage=self.storage)
        self.assertFalse(check_availability(unit, start, end, now=self.now, storage=self.storage))

        # Cancel
        cancelled = cancel_reservation(res.id, now=self.now, storage=self.storage)
        self.assertEqual(cancelled.status, "cancelled")
        self.assertIsNotNone(cancelled.cancelled_at)

        # Slot is now available again
        self.assertTrue(check_availability(unit, start, end, now=self.now, storage=self.storage))
        res2 = create_reservation(unit, "Luis Gómez", start, end, now=self.now, storage=self.storage)
        self.assertEqual(res2.status, "active")

        # Canceling again raises error
        with self.assertRaises(ValidationError):
            cancel_reservation(res.id, now=self.now, storage=self.storage)

        # Canceling nonexistent raises NotFoundError
        with self.assertRaises(NotFoundError):
            cancel_reservation("non-existent-id", now=self.now, storage=self.storage)

if __name__ == "__main__":
    unittest.main()
