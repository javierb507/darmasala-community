@echo off
echo ======================================================
echo   ATMA SUDDHI - Gestión de Escuela de Yoga
echo ======================================================
echo.

if not exist venv (
    echo [1/3] Creando entorno virtual...
    python -m venv venv
)

echo [2/3] Activando entorno y verificando dependencias...
call venv\Scripts\activate
pip install -r requirements.txt

echo.
echo [3/3] Iniciando la aplicación...
echo Abre tu navegador en: http://localhost:5001
echo.
echo Presiona Ctrl+C para detener el servidor.
echo.

python run.py

pause
