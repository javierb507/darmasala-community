#!/bin/bash
set -euo pipefail

# Setup completo DarmaSala en VPS Ubuntu/Debian.
# Crea venv, instala deps, inicializa DB, configura permisos, instala
# unit systemd y arranca el servicio.
#
# Uso:
#   sudo ./scripts/setup_vps.sh                     (auto-detecta dir y usuario)
#   sudo INSTALL_DIR=/var/www/darmasala-portal ./scripts/setup_vps.sh
#   sudo SERVICE_USER=www-data ./scripts/setup_vps.sh
#
# Idempotente: re-ejecutar es seguro. Sobrescribe el unit systemd.

# ---------------------------------------------------------------------------
# Config (variables de entorno override defaults)
# ---------------------------------------------------------------------------

INSTALL_DIR="${INSTALL_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
SERVICE_USER="${SERVICE_USER:-www-data}"
SERVICE_GROUP="${SERVICE_GROUP:-www-data}"
SERVICE_NAME="${SERVICE_NAME:-darmasala}"
PORT="${PORT:-5001}"
SECRET_KEY="${SECRET_KEY:-}"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${BLUE}[setup]${NC} $*"; }
ok()   { echo -e "${GREEN}[ok]${NC} $*"; }
warn() { echo -e "${YELLOW}[warn]${NC} $*"; }
die()  { echo -e "${RED}[error]${NC} $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Pre-checks
# ---------------------------------------------------------------------------

[[ $EUID -eq 0 ]] || die "Ejecuta como root (usa sudo)."
[[ -d "$INSTALL_DIR" ]] || die "INSTALL_DIR no existe: $INSTALL_DIR"
[[ -f "$INSTALL_DIR/production_server.py" ]] || die "$INSTALL_DIR no parece DarmaSala (falta production_server.py)"

id -u "$SERVICE_USER" >/dev/null 2>&1 || die "Usuario $SERVICE_USER no existe en el sistema."

log "Install dir:    $INSTALL_DIR"
log "Service user:   $SERVICE_USER:$SERVICE_GROUP"
log "Service name:   $SERVICE_NAME"
log "Listen port:    $PORT"

# Genera SECRET_KEY si no se pasó
if [[ -z "$SECRET_KEY" ]]; then
    SECRET_KEY="$(head -c 48 /dev/urandom | base64 | tr -d '\n/+=' | head -c 48)"
    log "SECRET_KEY:     <generada automáticamente>"
else
    log "SECRET_KEY:     <provista vía env>"
fi

# ---------------------------------------------------------------------------
# 1. Paquetes sistema
# ---------------------------------------------------------------------------

log "[1/7] Instalando paquetes del sistema..."
apt-get update -qq
apt-get install -y -qq \
    python3 python3-pip python3-venv python3-dev \
    build-essential libssl-dev libffi-dev sqlite3
ok "paquetes OK"

# ---------------------------------------------------------------------------
# 2. Ownership del proyecto
# ---------------------------------------------------------------------------

log "[2/7] Ajustando ownership del proyecto a $SERVICE_USER:$SERVICE_GROUP..."
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"
ok "ownership OK"

# ---------------------------------------------------------------------------
# 3. Virtualenv + deps
# ---------------------------------------------------------------------------

log "[3/7] Creando virtualenv en $INSTALL_DIR/venv..."
if [[ ! -x "$INSTALL_DIR/venv/bin/python" ]]; then
    sudo -u "$SERVICE_USER" python3 -m venv "$INSTALL_DIR/venv"
    ok "venv creado"
else
    ok "venv ya existe — reutilizando"
fi

log "Instalando dependencias Python..."
sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install --quiet --upgrade pip setuptools wheel
# Intenta binary-only primero (evita compilar numpy/pandas)
if ! sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install --quiet --only-binary :all: -r "$INSTALL_DIR/requirements.txt"; then
    warn "Binary-only falló, reintentando con compilación..."
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt"
fi
ok "deps OK"

# ---------------------------------------------------------------------------
# 4. Directorios + permisos (instance, uploads)
# ---------------------------------------------------------------------------

log "[4/7] Creando directorios writeables (instance/, uploads/)..."
sudo -u "$SERVICE_USER" mkdir -p "$INSTALL_DIR/instance" "$INSTALL_DIR/uploads"
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR/instance" "$INSTALL_DIR/uploads"
chmod 755 "$INSTALL_DIR/instance" "$INSTALL_DIR/uploads"
ok "directorios OK"

# ---------------------------------------------------------------------------
# 5. Inicializa DB si no existe
# ---------------------------------------------------------------------------

log "[5/7] Inicializando base de datos..."
DB_FILE="$INSTALL_DIR/instance/yoga_school.db"
# Mueve DB legacy si está en raíz del proyecto
if [[ -f "$INSTALL_DIR/yoga_school.db" && ! -f "$DB_FILE" ]]; then
    warn "DB legacy detectada en raíz, moviendo a instance/..."
    mv "$INSTALL_DIR/yoga_school.db" "$DB_FILE"
    chown "$SERVICE_USER:$SERVICE_GROUP" "$DB_FILE"
fi

if [[ ! -f "$DB_FILE" ]]; then
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/init_db.py"
    ok "DB inicializada (admin: admin / DarmaSala2025!)"
else
    ok "DB ya existe — no se toca"
fi
# Asegura permisos del archivo
chown "$SERVICE_USER:$SERVICE_GROUP" "$DB_FILE"
chmod 644 "$DB_FILE"

# ---------------------------------------------------------------------------
# 6. Unit systemd
# ---------------------------------------------------------------------------

log "[6/7] Instalando unit systemd /etc/systemd/system/${SERVICE_NAME}.service..."
cat >"/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=Servicio DarmaSala - Gestión de Escuela de Yoga
After=network.target

[Service]
User=${SERVICE_USER}
Group=${SERVICE_GROUP}
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${INSTALL_DIR}/venv/bin"
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=${SECRET_KEY}"
Environment="PORT=${PORT}"
ExecStart=${INSTALL_DIR}/venv/bin/python ${INSTALL_DIR}/production_server.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
chmod 644 "/etc/systemd/system/${SERVICE_NAME}.service"
ok "unit instalado"

# ---------------------------------------------------------------------------
# 7. Habilita + arranca
# ---------------------------------------------------------------------------

log "[7/7] Reload systemd + restart servicio..."
systemctl daemon-reload
systemctl enable "${SERVICE_NAME}.service" >/dev/null 2>&1
systemctl restart "${SERVICE_NAME}.service"
sleep 2

if systemctl is-active --quiet "${SERVICE_NAME}.service"; then
    ok "Servicio ${SERVICE_NAME} activo y escuchando en :${PORT}"
else
    warn "Servicio NO arrancó. Logs:"
    journalctl -u "${SERVICE_NAME}.service" -n 30 --no-pager
    die "Revisa logs arriba."
fi

# ---------------------------------------------------------------------------
# Resumen
# ---------------------------------------------------------------------------

echo
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✅ DarmaSala instalado correctamente${NC}"
echo -e "${GREEN}=========================================${NC}"
echo
echo "Acceso:       http://$(hostname -I | awk '{print $1}'):${PORT}"
echo "User admin:   admin"
echo "Pass admin:   DarmaSala2025!  (cambia tras primer login)"
echo
echo "Comandos útiles:"
echo "  sudo systemctl status ${SERVICE_NAME}"
echo "  sudo systemctl restart ${SERVICE_NAME}"
echo "  sudo journalctl -u ${SERVICE_NAME} -f"
echo
echo "Próximo paso recomendado: configurar Nginx reverse proxy + SSL"
echo "(ver docs/deployment-ubuntu.md)"
