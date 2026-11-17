# Ingenieria-diseno-UPIICSA

Repositorio de trabajo para el proyecto solicitado el semestre 2026-1 para la materia Ingeniería de Diseño en la UPIICSA.

Corresponde al caso de estudio "Consultorio dental" y la empresa ficticia "Sonrisa Perfecta". Versión actual: **1.1.0** (ver [CHANGELOG](CHANGELOG.md)).

## Inicio rápido

Requiere Docker con Docker Compose v2.

```bash
cp .env.example .env
```

```bash
docker compose up -d --build
```

Abra `http://localhost:8080` e inicie sesión con `admin` / `admin123`.

## Estructura

| Ruta | Contenido |
|---|---|
| `Sistema/` | Aplicación web (Python + NiceGUI) y su `Dockerfile` |
| `db/init/` | Esquema de la base de datos y script de carga de datos de muestra |
| `db/seed/` | Datos de muestra |
| `compose.yml` | Despliegue de la aplicación, PostgreSQL y Adminer (opcional) |

## Instalación (Manual técnico)

Consulte el [Manual técnico](/Manual%20Tecnico.md) para instrucciones detalladas de instalación, operación, respaldos y solución de problemas.
