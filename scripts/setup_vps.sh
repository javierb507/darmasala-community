#!/bin/bash

# Script de configuración para DarmaSala en VPS Linux (Ubuntu/Debian)
# Autor: Antigravity AI
# Versión: 1.0

# Colores para la consola
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧘 Iniciando instalación de DarmaSala System...${NC}"

# 1. Actualizar sistema e instalar dependencias
echo -e "${GREEN}[1/5] Actualizando sistema e instalando dependencias de Python...${NC}"
sudo apt update
sudo apt install -y python3-pip python3-venv python3-dev build-essential libssl-dev libffi-dev

# 2. Crear entorno virtual
echo -e "${GREEN}[2/5] Creando entorno virtual...${NC}"
python3 -m venv venv
source venv/bin/activate

# 3. Instalar requerimientos
echo -e "${GREEN}[3/5] Instalando dependencias del proyecto...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 4. Inicializar base de datos y configuración
echo -e "${GREEN}[4/5] Inicializando base de datos...${NC}"
# Usamos el script existente para inicializar
python3 init_db.py

# 5. Crear carpetas necesarias
echo -e "${GREEN}[5/5] Preparando directorios...${NC}"
mkdir -p uploads
mkdir -p instance

echo -e "${BLUE}✅ Instalación completada correctamente.${NC}"
echo -e "Para probar el servidor manualmente: ${GREEN}source venv/bin/activate && python3 production_server.py${NC}"
