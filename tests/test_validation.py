import unittest
from datetime import datetime, timedelta
from reservas.validation import (
    validate_unit_exists,
    validate_requester,
    parse_datetime,
    validate_time_range
)
from reservas.models import NotFoundError, ValidationError

class TestValidation(unittest.TestCase):
    def test_unit_exists_valid(self):
        try:
            validate_unit_exists("MIC-01")
            validate_unit_exists("OSC-01")
        except Exception as e:
            self.fail(f"Unidad válida rechazada: {e}")

    def test_unit_exists_invalid(self):
        with self.assertRaises(NotFoundError):
            validate_unit_exists("INVALID-99")

    def test_validate_requester_valid(self):
        name = validate_requester("  Ana Pérez  ")
        self.assertEqual(name, "Ana Pérez")

    def test_validate_requester_invalid(self):
        with self.assertRaises(ValidationError):
            validate_requester("")
        with self.assertRaises(ValidationError):
            validate_requester("   ")

    def test_parse_datetime_valid(self):
        dt = parse_datetime("2026-11-03T10:00")
        self.assertEqual(dt, datetime(2026, 11, 3, 10, 0))

    def test_parse_datetime_invalid(self):
        with self.assertRaises(ValidationError):
            parse_datetime("2026/11/03 10:00")
        with self.assertRaises(ValidationError):
            parse_datetime("invalid-date")

    def test_validate_time_range_valid(self):
        now = datetime(2026, 11, 1, 10, 0)
        start = datetime(2026, 11, 3, 10, 0)
        end = datetime(2026, 11, 3, 11, 0)
        try:
            validate_time_range(start, end, now)
        except Exception as e:
            self.fail(f"Rango de tiempo válido rechazado: {e}")

    def test_validate_time_range_start_after_end(self):
        now = datetime(2026, 11, 1, 10, 0)
        start = datetime(2026, 11, 3, 12, 0)
        end = datetime(2026, 11, 3, 11, 0)
        with self.assertRaises(ValidationError):
            validate_time_range(start, end, now)

    def test_validate_time_range_past(self):
        now = datetime(2026, 11, 3, 12, 0)
        start = datetime(2026, 11, 3, 10, 0)
        end = datetime(2026, 11, 3, 11, 0)
        with self.assertRaises(ValidationError):
            validate_time_range(start, end, now)

    def test_validate_time_range_exceeds_duration(self):
        now = datetime(2026, 11, 1, 10, 0)
        start = datetime(2026, 11, 3, 10, 0)
        end = datetime(2026, 11, 3, 19, 0) # 9 hours
        with self.assertRaises(ValidationError):
            validate_time_range(start, end, now)

    def test_validate_time_range_exceeds_advance(self):
        now = datetime(2026, 11, 1, 10, 0)
        start = now + timedelta(days=91)
        end = start + timedelta(hours=1)
        with self.assertRaises(ValidationError):
            validate_time_range(start, end, now)

if __name__ == "__main__":
    unittest.main()
