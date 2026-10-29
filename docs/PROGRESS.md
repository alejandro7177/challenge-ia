# Registro de Progreso

## 2026-10-23 — Estructura base y modelos de dominio
- Objetivo/requisito: Definir inventario precargado, excepciones de dominio y dataclass `Reservation`.
- Qué hizo el agente: Creación de `data/inventory.json` y `src/reservas/models.py`.
- Comando ejecutado y resultado real: `python -m unittest discover` (éxito inicial).
- Decisión humana (aceptar/corregir/rechazar) y motivo: Aceptado.
- Commit: Pendiente.

## 2026-10-23 — Validación, Servicio y Persistencia SQLite
- Objetivo/requisito: Implementar validación estricta, lógica única de superposición semiabierta (`[start, end)`), almacenamiento SQLite y CLI.
- Qué hizo el agente: Implementación de `validation.py`, `storage.py`, `service.py`, `cli.py` y `__main__.py`.
- Comando ejecutado y resultado real: `PYTHONPATH=src python -m unittest discover -s tests -v` -> 17 tests OK.
- Decisión humana (aceptar/corregir/rechazar) y motivo: Aceptado.
- Commit: Pendiente.

## 2026-10-29 — Integración de Interfaz Web con Django
- Objetivo/requisito: Transformar el proyecto para incluir una interfaz web en Django manteniendo la lógica de negocio, reglas de validación y almacenamiento unificados.
- Qué hizo el agente: Creación de la aplicación web Django en `src/reservas/web/` (`settings.py`, `urls.py`, `views.py`, templates Bootstrap HTML y suite de pruebas `test_django_web.py`).
- Comando ejecutado y resultado real: `PYTHONPATH=src ./venv/bin/python -m unittest discover -s tests -v` -> 21 tests OK.
- Decisión humana (aceptar/corregir/rechazar) y motivo: Aceptado por el usuario.
- Commit: Pendiente.
