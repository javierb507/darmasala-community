# Guía de Despliegue en Windows - DarmaSala

Esta guía detalla los pasos para desplegar la aplicación DarmaSala en un entorno Windows.

## Requisitos Previos

1. **Python 3.13**: Es la versión recomendada y probada para este entorno.
   - Descargar desde [python.org](https://www.python.org/downloads/windows/).
   - Asegurarse de marcar la opción **"Add Python to PATH"** durante la instalación.

2. **No es necesario Visual Studio**: La aplicación está diseñada para funcionar sin necesidad de compiladores complejos o entornos de desarrollo pesados como Visual Studio completo.

## Pasos de Instalación

1. **Clonar o descargar el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd darmasala
   ```

2. **Crear un entorno virtual**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Inicializar la base de datos**:
   ```powershell
   # Inicialización básica
   python init_db.py
   ```

## Configuración Inicial del Administrador

Al ejecutar la aplicación por primera vez, el sistema detectará que no hay usuarios y te redirigirá automáticamente a una página de configuración.

1. Inicia la aplicación:
   ```powershell
   python run.py
   ```
2. Abre tu navegador en `http://localhost:5001`.
3. Completa el formulario de **Configuración del Administrador** para establecer tu usuario y contraseña.

## Servicio en Windows (Auto-arranque)

Para que la aplicación siempre esté disponible (incluso después de reiniciar el portátil), puedes instalarla como un Servicio de Windows:

1.  **Abrir PowerShell como Administrador**:
    - Busca "PowerShell" en el menú inicio.
    - Haz clic derecho y elige **"Ejecutar como administrador"**.

2.  **Ejecutar el script de instalación**:
    ```powershell
    cd C:\ruta\a\tu\proyecto\darmasala
    .\scripts\install_windows_service.ps1
    ```

Este script descargará automáticamente una pequeña herramienta llamada `NSSM` (Non-Sucking Service Manager), configurará el entorno virtual e iniciará el servicio.

### Comandos Útiles del Servicio:
- **Ver estado/Editar**: `.\nssm.exe edit DarmaSalaYoga`
- **Reiniciar**: `.\nssm.exe restart DarmaSalaYoga`
- **Eliminar**: `.\nssm.exe remove DarmaSalaYoga confirm`

## Notas para Windows 3.13
- Se ha verificado que todas las librerías son compatibles con Python 3.13 sin necesidad de herramientas de compilación externas.
- Si encuentras errores de permisos, asegúrate de ejecutar la consola como Administrador.

## Servidor de Producción
Para el servicio de Windows se utiliza `Waitress`, un servidor web de producción de alto rendimiento para el entorno Windows, lo que garantiza estabilidad y velocidad.
