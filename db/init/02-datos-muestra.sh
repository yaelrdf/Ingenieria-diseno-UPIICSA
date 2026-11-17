#!/bin/sh
# Carga los datos de muestra solo si SEED_DEMO_DATA=true (valor por defecto).
# Se ejecuta una única vez, al crear el volumen de datos de PostgreSQL.
set -e

if [ "${SEED_DEMO_DATA:-true}" = "true" ]; then
    echo "Cargando datos de muestra..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /seed/datos_muestra.sql
else
    echo "SEED_DEMO_DATA=$SEED_DEMO_DATA: se omite la carga de datos de muestra."
fi
