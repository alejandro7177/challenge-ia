# Sistema de Reservas de Laboratorio

Aplicación Web (Django) e Interfaz CLI en Python para consultar disponibilidad, reservar y cancelar unidades de equipo de un laboratorio manteniendo un historial persistente.

## 1. Especificación

El sistema gestiona el uso compartido de 5 unidades físicas de equipamiento de laboratorio precargadas en `data/inventory.json`:
- **MIC-01**: Microscopio digital
- **MIC-02**: Microscopio digital
- **OSC-01**: Osciloscopio
- **MUL-01**: Multímetro
- **FUE-01**: Fuente de alimentación

### Reglas de Negocio
- Cada reserva posee ID único, `unit_id`, `requester`, `start`, `end`, `status` (`active` | `cancelled`), `created_at` y opcionalmente `cancelled_at`.
- Una reserva `active` bloquea el intervalo; una `cancelled` libera el horario.
- Validación estricta:
  - La unidad debe existir en el inventario.
  - El solicitante no puede estar vacío ni contener solo espacios (`strip()`).
  - Formato de fecha/hora ISO 8601 sin zona (`YYYY-MM-DDTHH:MM`).
  - `start` strictly anterior a `end`.
  - No se permiten fechas pasadas (con reloj inyectable `now`).
  - Duración máxima: 8 horas. Anticipación máxima: 90 días.
- Superposición: Dos reservas activas de la misma unidad se superponen si `a.start < b.end and b.start < a.end` (intervalos semiabiertos `[start, end)`). Los turnos consecutivos (fin de uno = inicio de otro) están permitidos en ambos órdenes.
- Cancelación: Cambia el estado a `cancelled`, conserva los datos y libera el intervalo.

## 2. Solución

Arquitectura modular en Python 3.11+:
- `src/reservas/models.py`: Dataclasses, constantes y excepciones de dominio (`ValidationError`, `ConflictError`, `NotFoundError`).
- `src/reservas/validation.py`: Lógica de validación de entradas, fechas y existencia en inventario.
- `src/reservas/storage.py`: Persistencia basada en SQLite (`data/reservas.db`).
- `src/reservas/service.py`: Lógica central de negocio unificada sin duplicación de código.
- `src/reservas/cli.py`: Interfaz de línea de comandos basada en `argparse`.
- `src/reservas/web/`: Interfaz Web en Django (`views.py`, `urls.py`, `settings.py`, `templates/`).

### Ejecutar Servidor Web (Django)
```bash
PYTHONPATH=src ./venv/bin/python -m django runserver --settings=reservas.web.settings
```
Abre en el navegador: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Comandos CLI
```bash
PYTHONPATH=src python -m reservas init                    # Inicializa la BD (con advertencia)
PYTHONPATH=src python -m reservas list-units              # Lista equipos
PYTHONPATH=src python -m reservas availability MIC-01 2026-11-03T10:00 2026-11-03T11:00
PYTHONPATH=src python -m reservas reserve MIC-01 "Ana Pérez" 2026-11-03T10:00 2026-11-03T11:00
PYTHONPATH=src python -m reservas cancel <id>             # Cancela reserva
PYTHONPATH=src python -m reservas list [--unit ID] [--status active|cancelled]
```

### Ejecución de Pruebas
```bash
PYTHONPATH=src ./venv/bin/python -m unittest discover -s tests -v
```

## 3. Preparación del Agente

- Entorno Python 3.11+ con Django.
- Reglas estrictas de superposición semiabierta (`[start, end)`).
- Persistencia SQLite inmutable excepto mediante el comando explícito `init`.
- Pruebas unitarias completas cubriendo validaciones, solapamientos, turnos consecutivos, cancelación, persistencia y vistas web Django.

## 4. Decisiones y Delegación

- **Decisión de almacenamiento:** Se seleccionó SQLite (`data/reservas.db`) para prevenir corrupción por escrituras concurrentes o parciales y garantizar consultas eficientes.
- **Interfaz Web Django:** Implementada reutilizando el mismo motor de servicios (`service.py`) sin duplicar lógica de negocio ni validaciones.
- **Supuestos documentados:**
  - Formato estricto `YYYY-MM-DDTHH:MM`.
  - Zona horaria local `America/Argentina/Buenos_Aires` (interpretada como *naive* datetimes).
  - Reloj inyectable en las funciones de servicio para garantizar pruebas deterministas.
- **Delegación y progreso:** Registrado detalladamente en `docs/PROGRESS.md` y `docs/delegation/`.
