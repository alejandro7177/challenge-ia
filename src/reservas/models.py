from dataclasses import dataclass
from datetime import datetime
from typing import Optional

class ValidationError(Exception):
    """Excepción para errores de validación de datos de entrada."""
    pass

class ConflictError(Exception):
    """Excepción para conflictos de superposición de reservas."""
    pass

class NotFoundError(Exception):
    """Excepción cuando un recurso (unidad o reserva) no es encontrado."""
    pass

MAX_DURATION_HOURS = 8
MAX_ADVANCE_DAYS = 90
TIMEZONE_NAME = "America/Argentina/Buenos_Aires"

@dataclass
class Reservation:
    id: str
    unit_id: str
    requester: str
    start: datetime
    end: datetime
    status: str  # "active" | "cancelled"
    created_at: datetime
    cancelled_at: Optional[datetime] = None
