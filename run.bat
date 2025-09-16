@echo off
echo Iniciando Sistema de Gestión de Escuela de Yoga...
echo.
echo Instalando dependencias...
pip install -r requirements.txt
echo.
echo Iniciando la aplicación...
echo Abre tu navegador y ve a: http://localhost:5000
echo.
echo Presiona Ctrl+C para detener la aplicación
echo.
python app.py
pause
