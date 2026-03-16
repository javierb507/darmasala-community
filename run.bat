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
python --version
python -m pip install --upgrade pip setuptools wheel
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Error actualizando pip/setuptools. Verifica tu conexión a internet.
    pause
    exit /b %ERRORLEVEL%
)

echo 📥 Instalando librerías (esto puede tardar un minuto)...
:: Forzamos binarios para evitar errores de compilación (vswhere/Meson)
python -m pip install --only-binary :all: -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️ Algunos binarios faltan en esta versión de Python. Intentando instalación estándar...
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ❌ Error crítico al instalar dependencias. 
        echo Revisa el error de arriba (posiblemente falta de compilador C++ o versión de Python incompatible).
        pause
        exit /b %ERRORLEVEL%
    )
)

echo.
echo [3/3] Iniciando la aplicación...
echo Abre tu navegador en: http://localhost:5001
echo.
echo Presiona Ctrl+C para detener el servidor.
echo.

python run.py

pause
