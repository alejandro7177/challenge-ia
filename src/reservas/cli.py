import argparse
import sys
from .storage import SQLiteStorage
from .validation import load_inventory
from .service import check_availability, create_reservation, cancel_reservation, list_reservations
from .models import ValidationError, ConflictError, NotFoundError

def main():
    parser = argparse.ArgumentParser(description="Sistema de reservas de laboratorio.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    subparsers.add_parser("init", help="Crea la BD y prepara el almacenamiento (ADVERTENCIA: borra reservas existentes).")

    # list-units
    subparsers.add_parser("list-units", help="Lista las unidades de equipo del inventario.")

    # availability
    avail_parser = subparsers.add_parser("availability", help="Consulta disponibilidad de una unidad en un intervalo.")
    avail_parser.add_argument("unit_id", help="ID de la unidad (ej. MIC-01)")
    avail_parser.add_argument("start", help="Fecha/hora de inicio (YYYY-MM-DDTHH:MM)")
    avail_parser.add_argument("end", help="Fecha/hora de fin (YYYY-MM-DDTHH:MM)")

    # reserve
    res_parser = subparsers.add_parser("reserve", help="Crea una reserva para una unidad.")
    res_parser.add_argument("unit_id", help="ID de la unidad (ej. MIC-01)")
    res_parser.add_argument("requester", help="Nombre del solicitante")
    res_parser.add_argument("start", help="Fecha/hora de inicio (YYYY-MM-DDTHH:MM)")
    res_parser.add_argument("end", help="Fecha/hora de fin (YYYY-MM-DDTHH:MM)")

    # cancel
    cancel_parser = subparsers.add_parser("cancel", help="Cancela una reserva existente.")
    cancel_parser.add_argument("reservation_id", help="ID de la reserva")

    # list
    list_parser = subparsers.add_parser("list", help="Lista reservas con filtros opcionales.")
    list_parser.add_argument("--unit", help="Filtrar por ID de unidad")
    list_parser.add_argument("--status", choices=["active", "cancelled"], help="Filtrar por estado")

    args = parser.parse_args()
    storage = SQLiteStorage()

    try:
        if args.command == "init":
            print("ADVERTENCIA: Esta operación inicializará la base de datos y eliminará todas las reservas previas.")
            confirm = input("¿Desea continuar? (s/N): ")
            if confirm.lower() not in ["s", "si", "sí", "y", "yes"]:
                print("Operación cancelada.")
                sys.exit(0)
            storage.init_db()
            print("Base de datos inicializada correctamente.")

        elif args.command == "list-units":
            inventory = load_inventory()
            print("Inventario de equipos:")
            for item in inventory:
                print(f"  - {item['id']}: {item['name']}")

        elif args.command == "availability":
            is_avail = check_availability(args.unit_id, args.start, args.end, storage=storage)
            if is_avail:
                print(f"Disponible: La unidad '{args.unit_id}' está libre en el intervalo {args.start} a {args.end}.")
            else:
                print(f"Ocupado: La unidad '{args.unit_id}' ya está reservada en el intervalo {args.start} a {args.end}.")
                sys.exit(1)

        elif args.command == "reserve":
            res = create_reservation(args.unit_id, args.requester, args.start, args.end, storage=storage)
            print(f"Reserva creada exitosamente.")
            print(f"  ID: {res.id}")
            print(f"  Unidad: {res.unit_id}")
            print(f"  Solicitante: {res.requester}")
            print(f"  Desde: {res.start.strftime('%Y-%m-%dT%H:%M')}")
            print(f"  Hasta: {res.end.strftime('%Y-%m-%dT%H:%M')}")

        elif args.command == "cancel":
            res = cancel_reservation(args.reservation_id, storage=storage)
            print(f"Reserva '{res.id}' cancelada exitosamente.")

        elif args.command == "list":
            reservations = list_reservations(unit_id=args.unit, status=args.status, storage=storage)
            if not reservations:
                print("No se encontraron reservas.")
            else:
                print(f"Reservas ({len(reservations)}):")
                for r in reservations:
                    cancel_info = f" (Cancelada: {r.cancelled_at.strftime('%Y-%m-%dT%H:%M')})" if r.cancelled_at else ""
                    print(f"  [{r.status.upper()}] ID: {r.id} | Unidad: {r.unit_id} | Solicitante: {r.requester} | {r.start.strftime('%Y-%m-%dT%H:%M')} -> {r.end.strftime('%Y-%m-%dT%H:%M')}{cancel_info}")

    except (ValidationError, ConflictError, NotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        sys.exit(1)
