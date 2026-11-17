#!/usr/bin/env bash
# Desinstala por completo Sonrisa Perfecta v1.0.0 (la versión instalada con Install.py).
# No toca la versión 1.1.0 en Docker (proyecto "sonrisa-perfecta").
#
# Uso:   ./desinstalar_v1.sh [nombre_del_proyecto_docker_anterior]
# Por defecto el proyecto anterior se llama como la carpeta del repositorio
# (por ejemplo "ingenieria-diseno-upiicsa").
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
PROYECTO="${1:-$(basename "$REPO" | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9_-')}"
FILTRO="label=com.docker.compose.project=$PROYECTO"

preguntar() { read -r -p "$1 (s/n): " r; [[ "$r" =~ ^[sSyY] ]]; }

if [ "$PROYECTO" = "sonrisa-perfecta" ]; then
    echo "Error: 'sonrisa-perfecta' es el proyecto de la versión 1.1.0; no se eliminará." >&2
    exit 1
fi

echo "=== Desinstalación de Sonrisa Perfecta v1.0.0 ==="
echo "Proyecto Docker anterior: $PROYECTO"
echo "Se eliminarán el servicio systemd, la base de datos antigua (con TODOS sus datos),"
echo "el entorno virtual de Python y los archivos de sesión."
preguntar "¿Continuar?" || exit 0

# 1. Servicio de systemd y proceso iniciado manualmente
if [ -f /etc/systemd/system/sistema_dental.service ]; then
    sudo systemctl disable --now sistema_dental || true
    sudo rm -f /etc/systemd/system/sistema_dental.service
    sudo systemctl daemon-reload
    echo "[OK] Servicio systemd 'sistema_dental' eliminado"
else
    echo "[--] No hay servicio systemd instalado"
fi
pkill -f "python.*Sistema/main.py" && echo "[OK] Proceso manual detenido" || true

# 2. Contenedor, volumen y red de la base de datos antigua
CONTENEDORES="$(docker ps -aq --filter "$FILTRO")"
if [ -n "$CONTENEDORES" ]; then
    DB="$(docker ps -q --filter "$FILTRO" --filter label=com.docker.compose.service=db)"
    if [ -n "$DB" ] && preguntar "¿Respaldar la base de datos antigua antes de borrarla?"; then
        ARCHIVO="$REPO/respaldo_v1_$(date +%Y%m%d_%H%M%S).sql"
        docker exec "$DB" pg_dump -U postgres sistema_dental > "$ARCHIVO"
        echo "[OK] Respaldo guardado en $ARCHIVO"
    fi
    docker rm -f $CONTENEDORES > /dev/null
fi
docker volume ls -q --filter "$FILTRO" | xargs -r docker volume rm > /dev/null
docker network ls -q --filter "$FILTRO" | xargs -r docker network rm > /dev/null
echo "[OK] Contenedores, volúmenes y redes de '$PROYECTO' eliminados"

# 3. Archivos locales de la instalación anterior
rm -rf "$REPO/.venv" "$REPO/Sistema/.venv" "$REPO/.nicegui" "$REPO/Sistema/.nicegui" "$REPO/sistema_dental.service"
echo "[OK] Entorno virtual y archivos locales eliminados"

echo
echo "Desinstalación completada. Para instalar la versión 1.1.0:"
echo "  cp .env.example .env && docker compose up -d --build"
