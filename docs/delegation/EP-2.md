# Episodio de Delegación 2 (EP-2)

- **Objetivo y requisito**: Implementar la lógica central de negocio (disponibilidad y reservas) con detección de superposición semiabierta y persistencia SQLite.
- **Contexto e instrucción**: Desarrollar `storage.py` y `service.py` asegurando que disponibilidad y creación compartan la misma lógica de conflicto, permitiendo turnos consecutivos exactos.
- **Acción/resultado del agente**: Implementación completada con éxito, superando todas las pruebas de superposición y concurrencia por unidad.
- **Decisión humana con motivo**: Aceptado por su robustez y precisión en los intervalos semiabiertos `[start, end)`.
- **Enlace a archivo/commit/prueba**: `src/reservas/service.py`, `src/reservas/storage.py`, `tests/test_service.py`.
