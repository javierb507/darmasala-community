# Despliegue en Hostinger - Atma Suddhi 🧘‍♀️

Esta guía detalla los pasos para poner en marcha la aplicación en un entorno de Hostinger.

## 📋 Requisitos Previos

1.  Haber configurado el dominio/subdominio en Hostinger.
2.  Tener acceso mediante SSH o el Administrador de Archivos de Hostinger.
3.  Asegurarse de tener Python 3.x disponible en el servidor.

## 🚀 Pasos de Instalación

### 1. Subir los Archivos
Sube todo el contenido del repositorio al directorio raíz de tu aplicación en Hostinger (usualmente dentro de `public_html/tusubdominio`).

### 2. Configurar el Entorno
Ejecuta los siguientes comandos desde la terminal SSH en el directorio de la aplicación:

```bash
# Crear entorno virtual (opcional pero recomendado)
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Inicializar la Base de Datos
Este paso es crucial para que la aplicación funcione correctamente y para crear el usuario administrador inicial.

```bash
python inicializar_sistema.py
```

Al finalizar, tendrás el sistema listo con:
*   **Usuario**: `admin`
*   **Contraseña**: `AtmaSuddhi74`

### 4. Configurar el Servidor Web (WSGI)
Hostinger utiliza un archivo `passenger_wsgi.py` o configuraciones similares. Asegúrate de que tu archivo de entrada (usualmente `wsgi.py`) esté correctamente configurado.

Si Hostinger detecta automáticamente aplicaciones Python, solo asegúrate de que el punto de entrada sea `wsgi.py` y la aplicación sea `app`.

## 🛠️ Solución de Problemas Comunes

### Error: "Configuración no carga" o "Could not build url"
Si ves un error al acceder a la sección de Configuración, asegúrate de haber ejecutado el script `inicializar_sistema.py`. 
Este error suele ocurrir cuando la base de datos no tiene la estructura de tablas completa.

### Resetear Contraseña de Admin
Si pierdes el acceso, puedes resetear la contraseña del usuario `admin` ejecutando:
```bash
python reset_admin_password.py
```

## 📊 Mantenimiento
Para cargar datos de prueba completos (alumnos, pagos, asistencias, etc.) y ver cómo funciona el sistema, puedes ejecutar:
```bash
python setup_hostinger.py
```
*⚠️ Nota: Este script borrará los datos actuales para cargar un set de pruebas limpio.*

---
Desarrollado para **Atma Suddhi - Espacio de Yoga**
