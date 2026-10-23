import uuid
from datetime import datetime
from typing import List, Optional
from .models import Reservation, ConflictError, NotFoundError, ValidationError
from .validation import validate_unit_exists, validate_requester, parse_datetime, validate_time_range
from .storage import SQLiteStorage

def _has_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
    # Regla: dos reservas activas se superponen si start1 < end2 and start2 < end1
    return start1 < end2 and start2 < end1

def check_availability_internal(unit_id: str, start: datetime, end: datetime, storage: Optional[SQLiteStorage] = None) -> bool:
    storage = storage or SQLiteStorage()
    active_reservations = storage.get_reservations(unit_id=unit_id, status="active")
    for res in active_reservations:
        if _has_overlap(start, end, res.start, res.end):
            return False
    return True

def check_availability(unit_id: str, start_str: str, end_str: str, now: Optional[datetime] = None, storage: Optional[SQLiteStorage] = None) -> bool:
    now = now or datetime.now()
    validate_unit_exists(unit_id)
    start = parse_datetime(start_str)
    end = parse_datetime(end_str)
    validate_time_range(start, end, now)
    return check_availability_internal(unit_id, start, end, storage)

def create_reservation(unit_id: str, requester: str, start_str: str, end_str: str, now: Optional[datetime] = None, storage: Optional[SQLiteStorage] = None) -> Reservation:
    now = now or datetime.now()
    storage = storage or SQLiteStorage()

    validate_unit_exists(unit_id)
    clean_requester = validate_requester(requester)
    start = parse_datetime(start_str)
    end = parse_datetime(end_str)
    validate_time_range(start, end, now)

    if not check_availability_internal(unit_id, start, end, storage):
        raise ConflictError(f"La unidad '{unit_id}' ya se encuentra reservada en el intervalo solicitado.")

    reservation_id = str(uuid.uuid4())
    reservation = Reservation(
        id=reservation_id,
        unit_id=unit_id,
        requester=clean_requester,
        start=start,
        end=end,
        status="active",
        created_at=now
    )
    storage.save_reservation(reservation)
    return reservation

def cancel_reservation(reservation_id: str, now: Optional[datetime] = None, storage: Optional[SQLiteStorage] = None) -> Reservation:
    now = now or datetime.now()
    storage = storage or SQLiteStorage()

    res = storage.get_reservation(reservation_id)
    if not res:
        raise NotFoundError(f"No se encontró ninguna reserva con ID '{reservation_id}'.")
    if res.status == "cancelled":
        raise ValidationError(f"La reserva '{reservation_id}' ya se encuentra cancelada.")

    storage.update_reservation_status(reservation_id, "cancelled", cancelled_at=now)
    res.status = "cancelled"
    res.cancelled_at = now
    return res

def list_reservations(unit_id: Optional[str] = None, status: Optional[str] = None, storage: Optional[SQLiteStorage] = None) -> List[Reservation]:
    storage = storage or SQLiteStorage()
    return storage.get_reservations(unit_id=unit_id, status=status)
