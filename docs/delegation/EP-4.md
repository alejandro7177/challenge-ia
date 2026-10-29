# Episodio de Delegación 4 (EP-4)

- **Objetivo y requisito**: Migrar/extender el sistema de reservas para funcionar como una aplicación web interactiva en Django.
- **Contexto e instrucción**: Configurar Django (`settings.py`, `urls.py`, `views.py`), crear templates Bootstrap HTML e integrar directamente las funciones de `service.py` sin duplicar la lógica de negocio.
- **Acción/resultado del agente**: Creación del módulo web `src/reservas/web/`, plantillas HTML y suite de pruebas `tests/test_django_web.py` ejecutada exitosamente con 21/21 tests pasando.
- **Decisión humana con motivo**: Aceptado por ampliar las capacidades a interfaz web garantizando la misma consistencia de validaciones y almacenamiento.
- **Enlace a archivo/commit/prueba**: `src/reservas/web/views.py`, `src/reservas/web/templates/`, `tests/test_django_web.py`.
