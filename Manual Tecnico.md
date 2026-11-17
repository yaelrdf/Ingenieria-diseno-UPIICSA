# Manual técnico — Sonrisa Perfecta v1.1.0

- [Arquitectura](#arquitectura)
- [Requisitos técnicos](#requisitos-técnicos)
- [Instalación](#instalación)
- [Accediendo al sistema](#accediendo-al-sistema)
- [Operación](#operación)
- [Gestor de base de datos (Adminer)](#gestor-de-base-de-datos-adminer)
- [Solución de problemas](#solución-de-problemas)

## Arquitectura

El sistema se despliega al 100 % con Docker Compose, con tres servicios:

| Servicio | Imagen | Función | Puerto |
|---|---|---|---|
| `app` | `sonrisa-perfecta:1.1.0` (se construye desde `Sistema/Dockerfile`) | Aplicación web (Python 3.12 + NiceGUI) | `8080` (configurable con `APP_PORT`) |
| `db` | `postgres:17-alpine` | Base de datos PostgreSQL | No se publica fuera de Docker |
| `adminer` | `adminer:5.4.1` | Gestor web de la BD (opcional, perfil `tools`) | `127.0.0.1:8081` |

Volúmenes persistentes:

- `pgdata`: datos de PostgreSQL.
- `sesiones`: sesiones de los usuarios de la aplicación.

Al crearse el volumen `pgdata` por primera vez, PostgreSQL ejecuta automáticamente:

1. `db/init/01-schema.sql`: tablas, restricciones y el usuario `admin`.
2. `db/init/02-datos-muestra.sh`: carga `db/seed/datos_muestra.sql` si `SEED_DEMO_DATA=true`.

## Requisitos técnicos

- Servidor Linux (Debian 12 o superior recomendado), Windows o macOS.
- Docker Engine 24 o superior con el complemento Docker Compose v2 (`docker compose version`).
- Git (opcional, para descargar el repositorio).
- 1 GB de RAM libre y 2 GB de disco.

No es necesario instalar Python ni PostgreSQL en el servidor.

## Instalación

> [!NOTE]
> Si el servidor tiene instalada la versión 1.0.0 (con `Install.py`), desinstálela primero: vea [Desinstalar la versión 1.0.0](#desinstalar-la-versión-100).

1. Descargue el repositorio:

```bash
git clone https://github.com/yaelrdf/Ingenieria-diseno-UPIICSA
```

```bash
cd Ingenieria-diseno-UPIICSA
```

2. Cree el archivo de configuración y cambie las contraseñas y el secreto de sesión:

```bash
cp .env.example .env
```

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Credenciales de PostgreSQL | `sistema_dental` / `postgres` / `postgres` |
| `STORAGE_SECRET` | Secreto para firmar las sesiones | `cambie-este-secreto` |
| `APP_PORT` | Puerto web en el servidor | `8080` |
| `ADMINER_PORT` | Puerto local de Adminer | `8081` |
| `SEED_DEMO_DATA` | `true` carga datos de muestra; `false` crea la base vacía | `true` |

> [!WARNING]
> Las credenciales de la base de datos solo se aplican al crear el volumen por primera vez. Para cambiarlas después hay que reiniciar los datos (ver [Operación](#operación)).

3. Construya e inicie el sistema:

```bash
docker compose up -d --build
```

4. Verifique que los servicios estén en ejecución (`db` debe aparecer como `healthy`):

```bash
docker compose ps
```

El primer arranque tarda un poco más porque descarga las imágenes, construye la aplicación y crea la base de datos. Los contenedores se reinician solos al reiniciar el servidor (`restart: unless-stopped`), por lo que no se requiere un servicio de systemd.

### Desinstalar la versión 1.0.0

El script `desinstalar_v1.sh` elimina por completo la instalación anterior:

- el servicio de systemd `sistema_dental`;
- el proceso iniciado manualmente con `python Sistema/main.py`;
- el contenedor, el volumen y la red de la base de datos antigua;
- el entorno virtual `.venv` y los archivos de sesión.

No afecta a la versión 1.1.0. Ejecútelo desde la carpeta del repositorio donde se instaló la versión anterior, después de actualizar el código con `git pull`:

```bash
./desinstalar_v1.sh
```

El script pide confirmación y ofrece respaldar la base de datos antigua en un archivo `respaldo_v1_<fecha>.sql`. Pide la contraseña de `sudo` solo si existe el servicio de systemd.

Si la carpeta del repositorio cambió de nombre desde la instalación anterior, indique el nombre del proyecto Docker antiguo (se puede consultar con `docker ps -a`; es la parte antes de `-db-1`):

```bash
./desinstalar_v1.sh nombre-del-proyecto
```

## Accediendo al sistema

El sistema queda disponible en toda la red local del servidor en `http://ip_servidor:8080` (o el puerto definido en `APP_PORT`).

Cuenta de administrador (siempre se crea):

| Usuario | Contraseña | Perfil |
|---|---|---|
| `admin` | `admin123` | Super administrador |

Cuentas incluidas en los datos de muestra:

| Usuario | Contraseña | Perfil |
|---|---|---|
| `alisson` | `1234` | Recepcionista (Vista general, citas, pacientes, expedientes, adeudos) |
| `Angel` | `1234` | Médico vinculado al Dr. Ángel Domínguez Ruiz (ve sus citas y las que no tienen médico) |

> [!IMPORTANT]
> Cambie la contraseña de `admin` y elimine o cambie las cuentas de muestra antes de usar el sistema en producción.

### Datos de muestra

Las fechas se calculan respecto al día en que se creó la base de datos, por lo que siempre hay citas pasadas, del día y futuras. Incluyen: 6 médicos (uno inactivo y uno sin citas), 10 pacientes, 18 citas en todos los estados (una sin médico asignado), procedimientos liquidados, con saldo, en proceso y pendientes, pagos, odontogramas e historial médico.

## Operación

Ver los registros de la aplicación:

```bash
docker compose logs -f app
```

Detener el sistema (los datos se conservan):

```bash
docker compose down
```

Actualizar a una nueva versión del código:

```bash
git pull
```

```bash
docker compose up -d --build
```

Respaldar la base de datos:

```bash
docker compose exec -T db pg_dump -U postgres --clean --if-exists sistema_dental > respaldo.sql
```

Restaurar un respaldo (reemplaza los datos actuales por los del respaldo):

```bash
docker compose exec -T db psql -U postgres -d sistema_dental < respaldo.sql
```

Reiniciar la base de datos desde cero (**borra todos los datos** y vuelve a cargar el esquema y, si está activo, los datos de muestra):

```bash
docker compose down -v
```

```bash
docker compose up -d --build
```

### Verificar el almacenamiento de contraseñas (RNF06 / TC-90)

Las contraseñas se guardan como hash SHA-256 de 64 caracteres hexadecimales; la base de datos rechaza cualquier otro valor. Para comprobarlo:

```bash
docker compose exec db psql -U postgres -d sistema_dental -c "SELECT username, password, length(password) AS longitud FROM usuarios_sistema;"
```

## Gestor de base de datos (Adminer)

Adminer permite consultar la base de datos desde el navegador. No se inicia por defecto:

```bash
docker compose --profile tools up -d
```

Abra `http://127.0.0.1:8081` en el propio servidor y conéctese con:

- Sistema: PostgreSQL
- Servidor: `db`
- Usuario y contraseña: los de `DB_USER` y `DB_PASSWORD`
- Base de datos: `sistema_dental`

Por seguridad solo escucha en `127.0.0.1`. Para usarlo desde otro equipo, cree un túnel SSH (`ssh -L 8081:127.0.0.1:8081 usuario@servidor`). Deténgalo al terminar:

```bash
docker compose --profile tools stop adminer
```

## Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `app` se reinicia continuamente | La BD no está disponible o las credenciales no coinciden | Revise `docker compose logs app` y que `.env` no haya cambiado desde la creación del volumen |
| El puerto 8080 está ocupado | Otro servicio usa el puerto | Cambie `APP_PORT` en `.env` y ejecute `docker compose up -d` |
| No aparecen los datos de muestra | El volumen ya existía o `SEED_DEMO_DATA=false` | Reinicie la base de datos desde cero |
| Todos los usuarios perdieron la sesión | Cambió `STORAGE_SECRET` o se borró el volumen `sesiones` | Inicie sesión de nuevo |
