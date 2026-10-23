import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from .models import ValidationError, NotFoundError, MAX_DURATION_HOURS, MAX_ADVANCE_DAYS

def load_inventory() -> List[Dict[str, str]]:
    # Path relative to project root or absolute
    root = Path(__file__).resolve().parent.parent.parent
    inv_path = root / "data" / "inventory.json"
    if not inv_path.exists():
        return []
    with open(inv_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_unit_ids() -> List[str]:
    inventory = load_inventory()
    return [item["id"] for item in inventory]

def validate_unit_exists(unit_id: str) -> None:
    valid_ids = get_unit_ids()
    if unit_id not in valid_ids:
        raise NotFoundError(f"La unidad '{unit_id}' no existe en el inventario.")

def validate_requester(requester: str) -> str:
    if not requester or not requester.strip():
        raise ValidationError("El solicitante no puede estar vacío o contener solo espacios.")
    return requester.strip()

def parse_datetime(dt_str: str) -> datetime:
    if not dt_str or not isinstance(dt_str, str):
        raise ValidationError(f"Formato de fecha/hora inválido: '{dt_str}'. Use YYYY-MM-DDTHH:MM.")
    try:
        return datetime.strptime(dt_str.strip(), "%Y-%m-%dT%H:%M")
    except ValueError:
        raise ValidationError(f"Formato de fecha/hora inválido: '{dt_str}'. Use YYYY-MM-DDTHH:MM.")

def validate_time_range(start: datetime, end: datetime, now: datetime) -> None:
    if start >= end:
        raise ValidationError("La fecha/hora de inicio debe ser estrictamente anterior a la de fin.")
    
    duration = end - start
    if duration > timedelta(hours=MAX_DURATION_HOURS):
        raise ValidationError(f"La duración de la reserva no puede exceder las {MAX_DURATION_HOURS} horas.")

    if start < now:
        raise ValidationError("No se pueden realizar reservas en el pasado.")

    max_advance = timedelta(days=MAX_ADVANCE_DAYS)
    if start > now + max_advance:
        raise ValidationError(f"No se pueden realizar reservas con más de {MAX_ADVANCE_DAYS} días de anticipación.")
