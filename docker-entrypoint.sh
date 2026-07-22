#!/bin/sh
set -e

# Inicializa la BD (SQLite) en el primer arranque. init_db.py es
# idempotente y stampea las migraciones automáticamente.
if [ -z "$DATABASE_URL" ] && [ ! -f /app/instance/yoga_school.db ]; then
    echo "Primera ejecución: inicializando base de datos..."
    python init_db.py ${INIT_DB_ARGS:-}
fi

exec gunicorn --bind 0.0.0.0:5001 --workers "${GUNICORN_WORKERS:-3}" app:app
