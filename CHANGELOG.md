# Changelog

## [1.1.0] — 2026-11-17

Versión de corrección de las incidencias reportadas por el equipo evaluador en la *Matriz Ciclo de Pruebas* (ciclo de prueba 1, Sonrisa Perfecta v1.0.0) y migración del despliegue a Docker.

### Casos rechazados

| Caso | Incidencia | Corrección |
|---|---|---|
| TC-25 | Se guardaba un CURP con menos de 18 caracteres | El CURP debe tener exactamente 18 letras o números. El formulario bloquea el guardado y la BD lo rechaza con una restricción `CHECK`. |
| TC-27 | Se guardaba un CURP con caracteres especiales (`@`) | Se valida el formato `^[A-Z0-9]{18}$`; símbolos y espacios muestran el error "El CURP solo admite letras y números" y se bloquea el guardado. |
| TC-86 (RNF02) | No había validación en tiempo real del CURP | El campo marca el error en rojo mientras se escribe, con contador `n/18`, límite de 18 caracteres y conversión a mayúsculas. |
| TC-43 | Se registraba un médico con email `correo@sin-dominio` | Validación de email con dominio y extensión (ej. `nombre@dominio.com`) en tiempo real, al guardar y con restricción en la BD. |
| TC-48 | Se eliminaba un médico con citas registradas | Antes de eliminar se cuentan sus citas; si tiene, se bloquea y se sugiere desactivarlo. La llave foránea `citas.doctor_id` cambió a `ON DELETE RESTRICT`. |
| TC-55 (RN05) | Con un médico inactivo se advertía pero se guardaba la cita | Al guardar se verifica en la BD que el médico esté activo y se bloquea la cita si no lo está. Si una cita existente tiene un médico que fue desactivado, aparece como "(inactivo)" y debe reasignarse para guardar. |
| TC-56 | Se creaban citas con fecha/hora en el pasado | El calendario solo permite fechas desde hoy y al guardar se rechaza cualquier fecha/hora anterior al momento actual (también al reprogramar una cita). |

### Casos no probados

| Caso | Motivo | Corrección |
|---|---|---|
| TC-79 | La fecha de pago venía prellenada sin forma de vaciarla | El campo de fecha ahora se puede borrar (botón ✕) o escribir; es obligatorio y no admite fechas futuras. Además se corrigió un defecto: la fecha elegida se ignoraba y siempre se guardaba la fecha del día. |
| TC-80 (RF23) | El método de pago traía "Efectivo" por defecto | El método inicia vacío y es obligatorio. El procedimiento tampoco se preselecciona. |
| TC-90 (RNF06) | El equipo de pruebas no tenía acceso a la BD | Se agregó Adminer (perfil `tools` de Docker Compose) y el comando de verificación en el Manual técnico. La BD solo acepta hashes SHA-256 de 64 caracteres hexadecimales. |

### Observaciones de casos aceptados

| Caso | Observación | Corrección |
|---|---|---|
| TC-81, TC-88 (RN02) | No se demostraba el bloqueo de pago de procedimientos "en progreso"; el procedimiento aparecía como "None" | Solo los procedimientos completados son pagables. Los "en proceso" se muestran en la tabla como "en proceso (no pagable)". Al guardar se revalida el estado y que el monto no exceda el saldo. El nombre se toma del catálogo, de la descripción de la cita o del tipo de cita. |
| TC-02, TC-03, TC-04 | Mensaje genérico "Usuario o contraseña incorrectos" con campos vacíos | Mensajes específicos: "El usuario es obligatorio", "La contraseña es obligatoria" e "Ingrese usuario y contraseña". |
| TC-07 | Espacios al inicio/final del usuario | Se eliminan los espacios del nombre de usuario; la contraseña se respeta tal cual. |

### Mejoras adicionales

- **Empalme de citas:** no se puede agendar a un médico en un horario que se traslape con otra de sus citas programadas o en curso.
- **Protección de médicos:** no se puede desactivar un médico que tenga citas programadas o en curso.
- **Validaciones nuevas:** teléfono de 10 dígitos (pacientes y médicos), email de paciente con formato válido, fecha de nacimiento no futura y monto de pago que no exceda el saldo pendiente.
- **Mensajes de error claros** para CURP, email de médico o nombre de usuario duplicados, en lugar del error técnico de PostgreSQL.

### Errores corregidos durante la revisión

- **Permisos:** los módulos se podían abrir escribiendo la URL aunque el usuario no tuviera permiso. Ahora cada página verifica el permiso y muestra "Acceso restringido". Los permisos se recargan de la BD en cada página y la sesión se cierra si la cuenta fue eliminada.
- **Sesiones mezcladas:** el contenedor de la página era una variable global compartida entre usuarios conectados al mismo tiempo; se eliminó.
- La sesión del navegador ya no guarda el hash de la contraseña.
- **Vista general:** el botón "Eliminar" quedaba anidado dentro del botón "Completar" por una etiqueta sin cerrar; se agregaron también "Editar" y "Cancelar".
- Una cita nueva podía crearse directamente como "Completada" o "Cancelada" sin generar el adeudo; ahora siempre inicia como "Programada" y el estado solo se cambia al editar.
- Los cambios de estado (iniciar, completar, cancelar) validan el estado actual y se ejecutan en una sola transacción junto con el registro del adeudo.
- La edad se calcula a partir de la fecha de nacimiento cada vez que se muestra, en lugar de usar el valor guardado.
- Ya no se muestra "None" en teléfonos, emails ni nombres de procedimientos vacíos.
- El buscador de pacientes encuentra también por nombre completo y CURP.
- El texto de ayuda "Dejar en blanco para no cambiar" de la contraseña no se mostraba al editar un usuario.
- La conexión a la base de datos se reintenta al arrancar y descarta conexiones rotas.
- La versión mostrada en el menú se toma de la configuración.

### Despliegue

- Despliegue 100 % Docker: `compose.yml` con la aplicación (`Sistema/Dockerfile`), PostgreSQL 17 con *healthcheck* y Adminer opcional.
- Esquema (`db/init/01-schema.sql`) y datos de muestra (`db/seed/datos_muestra.sql`) se cargan automáticamente al crear la base de datos. Los datos de muestra usan fechas relativas al día de instalación y se pueden desactivar con `SEED_DEMO_DATA=false`.
- Configuración por variables de entorno (`.env.example`): credenciales, secreto de sesión y puertos.
- Script `desinstalar_v1.sh` para eliminar por completo la instalación 1.0.0 (servicio de systemd, base de datos antigua, entorno virtual y sesiones), con respaldo opcional de la base de datos.
- Se eliminaron `Install.py`, el servicio de systemd, `add_users_table.sql` (tenía un hash de admin incorrecto), `test-data.sql`, `create_database.sql` y `filethree.txt`.
- `requirements.txt` reducido a las dependencias reales con versión fija (`nicegui`, `psycopg2-binary`); antes incluía `hashlib` y `logging`, que impedían la instalación.
- El entorno virtual (`Sistema/.venv`), las cachés de Python y las sesiones de NiceGUI se retiraron del control de versiones y se agregó `.gitignore`.
- Manual técnico reescrito para la instalación con Docker.

## [1.0.0]

Versión evaluada en el ciclo de prueba 1.
