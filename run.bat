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

REM Check for experimental Python versions
python -c "import sys; sys.exit(0 if sys.version_info < (3, 14) else 1)"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] ATENCION: Estas usando Python 3.14 (Version Experimental).
    echo [!] Es posible que muchas librerias (como NumPy) aun no funcionen.
    echo [!] Se recomienda usar Python 3.12 o 3.13.
    echo.
)

python -m pip install --upgrade pip setuptools wheel
if %ERRORLEVEL% NEQ 0 (
    echo [!] Error actualizando pip/setuptools.
)

echo [3/3] Instalando librerias...
REM Evitamos compilar desde cero para saltar errores de vswhere/Meson
python -m pip install --only-binary :all: -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [!] Algunos binarios no se encontraron. Intentando instalacion estandar...
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [!] ERROR CRITICO: No se pudieron instalar las dependencias.
        pause
        exit /b 1
    )
)

echo.
echo Iniciando aplicacion...
python run.py
pause
