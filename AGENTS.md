# AGENTS.md

# Sistema de reservas de laboratorio

Instrucciones para el agente de programación (opencode). Leer completo antes de actuar.

## Objetivo

Aplicación local pequeña para **consultar disponibilidad, reservar y cancelar** unidades de equipo de un laboratorio, sin perder historial. Todo debe poder verificarse y reproducirse sin cuenta de modelo.

## Inventario (precargado, solo lectura)


| ID     | Equipo                 |
| ------ | ---------------------- |
| MIC-01 | Microscopio digital    |
| MIC-02 | Microscopio digital    |
| OSC-01 | Osciloscopio           |
| MUL-01 | Multímetro             |
| FUE-01 | Fuente de alimentación |


Cada ID es una unidad física distinta. Vive en `data/inventory.json`. No hay que administrarlo (sin alta/baja/edición).

## Reglas de negocio (fuente de verdad)

1. Una reserva tiene: `id` único, `unit_id`, `requester`, `start`, `end`, `status` (`active` | `cancelled`), `created_at`, `cancelled_at` (opcional).
2. Una reserva `active` ocupa el intervalo; una `cancelled` **no** bloquea.
3. Validaciones (todas con mensaje de error claro):
   - unidad existe en el inventario;
   - `requester` no vacío ni solo espacios (se guarda con `strip()`);
   - fechas/horas con formato válido;
   - `start` **estrictamente anterior** a `end`.
4. Superposición: dos reservas activas de la **misma** unidad se superponen si `a.start < b.end and b.start < a.end`. Rechazar.
5. Límites consecutivos permitidos (fin de una = inicio de otra). Unidades distintas pueden coincidir en horario.
6. Cancelar: conserva id y datos, cambia estado a `cancelled`, libera el intervalo. Cancelar una reserva inexistente o ya cancelada devuelve error claro.
7. **La consulta de disponibilidad y la creación usan la misma función de validación y de detección de conflictos.** Nunca duplicar la lógica.
8. Persistencia: reservas y estados se recuperan al reiniciar.

Ejemplo canónico (debe ser un test): MIC-01 reservado 10:00–11:00 → rechazar 10:30–11:30, permitir 11:00–12:00, permitir MIC-02 10:00–11:00.

## Supuestos (decididos; documentar en el README, no cambiar sin registrar)

- Formato de fecha/hora: ISO 8601 sin zona, `YYYY-MM-DDTHH:MM` (ej. `2026-11-03T10:00`).
- Zona horaria: hora local del laboratorio, `America/Argentina/Buenos_Aires` (UTC-3). Se trabaja con datetimes *naive* interpretados en esa zona.
- Fechas pasadas: se rechaza `start` anterior al momento actual. El reloj se **inyecta** (parámetro `now`) para que los tests sean deterministas.
- Duración máxima: 8 horas. Anticipación máxima: 90 días. Constantes en un solo módulo.
- Una unidad por reserva. Solicitantes ficticios únicamente.

## Stack y estructura

- Python 3.11+, **solo biblioteca estándar** (sin dependencias externas): `argparse`, `sqlite3`, `unittest`.
- Interfaz: CLI.
- Almacenamiento: SQLite en `data/reservas.db` (ignorado por Git). Alternativa descartada: JSON plano (más frágil ante escrituras parciales).

```
.
├── AGENTS.md
├── README.md              # 4 secciones: Especificación, Solución, Preparación del agente, Decisiones y delegación
├── data/inventory.json
├── docs/
│   ├── PROGRESS.md        # progreso y decisiones (versionado)
│   ├── agent-setup/       # opencode.json saneado, extractos de instrucciones, evidencia
│   └── delegation/        # un archivo por episodio (EP-1, EP-2, EP-3)
├── src/reservas/
│   ├── models.py          # dataclasses, enums, constantes
│   ├── validation.py      # validación de entrada
│   ├── service.py         # crear, cancelar, disponibilidad (lógica única)
│   ├── storage.py         # SQLite
│   └── cli.py             # comandos
└── tests/
    ├── test_service.py
    ├── test_validation.py
    └── test_persistence.py

```

## Comandos

```bash
python -m unittest discover -s tests -v          # pruebas
python -m reservas init                          # crea BD y carga inventario (borra reservas: avisar)
python -m reservas list-units
python -m reservas availability MIC-01 2026-11-03T10:00 2026-11-03T11:00
python -m reservas reserve MIC-01 "Ana Pérez" 2026-11-03T10:00 2026-11-03T11:00
python -m reservas cancel <reservation_id>
python -m reservas list [--unit MIC-01] [--status active|cancelled]

```

(Ejecutar con `PYTHONPATH=src` o instalando en modo editable si se agrega `pyproject.toml`.)

## Tests obligatorios

Deben existir y pasar:

- creación válida;
- rechazo de superposición (parcial, contenida, contenedora, idéntica);
- límites consecutivos permitidos (ambos órdenes);
- unidades distintas simultáneas;
- entradas inválidas: unidad desconocida, solicitante vacío/solo espacios, formato de fecha inválido, `start >= end`, fecha pasada, duración/anticipación excedida;
- cancelación conserva el registro y libera el horario (se puede volver a reservar el mismo intervalo);
- persistencia: crear activa + cancelada, cerrar y reabrir el storage sobre el mismo archivo, verificar ambas;
- disponibilidad coherente con creación (si `availability` dice libre, `reserve` acepta; si dice ocupado, rechaza).

## Forma de trabajo

1. **Plan primero.** Antes de editar, proponer un plan corto y esperar aprobación.
2. **Pasos pequeños.** Un cambio acotado por vez; escribir el test antes o junto con la implementación.
3. **Ejecutar, no suponer.** Después de cada cambio correr los tests y reportar el comando y el resultado real. Si algo no se ejecutó, decirlo explícitamente.
4. **No inventar.** Si un dato no es visible (versión del modelo, resultado de un comando), decir "no visible" / "no ejecutado".
5. Resolver ambigüedades con el supuesto documentado arriba; si hace falta uno nuevo, proponerlo y registrarlo, no decidirlo en silencio.

### Adaptación específica (turnos consecutivos y persistencia)

- **Turnos consecutivos:** para cualquier comparación de intervalos usar *solo* `start < other_end and other_start < end` (intervalos semiabiertos `[start, end)`). Prohibido usar `<=`/`>=` en esa comparación. Todo cambio en esa lógica debe acompañarse de tests de borde (11:00 fin vs 11:00 inicio).
- **Persistencia:** nunca borrar ni recrear `data/reservas.db` salvo en el comando explícito `init`, que debe advertir que borra reservas. Los tests usan archivos temporales (`tempfile`), jamás la BD real. Al tocar [`storage.py`](http://storage.py), re-ejecutar `tests/test_[persistence.py](http://persistence.py)`.

## Registro de progreso (obligatorio)

Al terminar cada tarea relevante, agregar al final de `docs/[PROGRESS.md](http://PROGRESS.md)`:

```
## YYYY-MM-DD — <título>
- Objetivo/requisito:
- Qué hizo el agente:
- Comando ejecutado y resultado real:
- Decisión humana (aceptar/corregir/rechazar) y motivo:   <- lo completa el humano
- Commit:

```

Los **tres episodios de delegación** van en `docs/delegation/[EP-N.md](http://EP-N.md)` con: objetivo y requisito → contexto e instrucción → acción/resultado del agente → decisión humana con motivo → enlace a archivo/commit/prueba. Registrar correcciones **solo si ocurrieron**. Sin transcripciones completas.

## Permisos y límites

- Permitido: leer/editar archivos dentro del repo; correr `python -m unittest`, `python -m reservas ...`, `git status`, `git diff`, `git log`.
- Requiere aprobación humana: `git commit`, `git push`, borrar archivos, instalar paquetes, cualquier comando fuera del repo.
- Prohibido: acceder a la red, leer/escribir fuera del repo, tocar credenciales, agregar dependencias externas sin aprobación, agregar funcionalidad fuera de alcance.
- **Fuera de alcance:** autenticación/roles, notificaciones, pagos, integraciones externas, despliegue, GUI, concurrencia distribuida, administración del inventario.
- No incluir secretos, tokens ni datos reales de estudiantes. Solicitantes ficticios (Ana Pérez, Luis Gómez, etc.).

## Convenciones de código

- Tipado con type hints; funciones pequeñas y puras donde se pueda (la lógica de conflictos no toca la BD).
- Errores de dominio con excepciones propias (`ValidationError`, `ConflictError`, `NotFoundError`); la CLI las traduce a mensajes y códigos de salida distintos de 0.
- Mensajes de usuario y documentación en español.
- Commits pequeños con mensaje descriptivo (qué y por qué).

## Definición de terminado

- \[ \] Todas las reglas implementadas y los tests obligatorios en verde (comando y resultado registrados).
- \[ \] Persistencia verificada tras reinicio.
- \[ \] README con las 4 secciones, supuestos, advertencia de `init`, pendientes y limitaciones.
- \[ \] `docs/[PROGRESS.md](http://PROGRESS.md)` y los 3 episodios completos con enlaces a commits/tests.
- \[ \] Sin secretos; `data/reservas.db` en `.gitignore`.