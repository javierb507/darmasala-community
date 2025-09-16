# Sistema de Gestión de Escuela de Yoga

Un sistema de gestión ligero y basado en web para escuelas de yoga construido con Python Flask y SQLite.

## Características

- **Gestión de Estudiantes**: Registrar, ver, editar y gestionar información de estudiantes
- **Base de Datos Ligera**: Usa SQLite - no requiere instalación, perfecto para laptops
- **Interfaz Web**: Interfaz web limpia y responsiva
- **Fácil Despliegue**: Funciona en cualquier laptop con Python instalado

## Inicio Rápido

1. **Instalar Python** (si no está instalado)
   - Descargar desde https://python.org
   - Asegúrate de marcar "Add Python to PATH" durante la instalación

2. **Instalar Dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la Aplicación**
   ```bash
   python app.py
   ```

4. **Abrir en el Navegador**
   - Ir a http://localhost:5000
   - ¡Comienza a gestionar tu escuela de yoga!

## Base de Datos

La aplicación usa SQLite, que crea un archivo local llamado `yoga_school.db`. Este archivo contiene todos tus datos y puede ser respaldado o movido fácilmente a otra computadora.

## Requisitos del Sistema

- Python 3.7 o superior
- 50MB de espacio en disco
- Cualquier navegador web moderno
- No se requiere instalación adicional de base de datos

## Características Disponibles

✅ **Gestión de Estudiantes**
- Agregar nuevos estudiantes
- Ver detalles de estudiantes
- Editar información de estudiantes
- Desactivar estudiantes
- Información de contacto de emergencia
- Seguimiento de condiciones médicas

🔄 **Próximamente**
- Gestión de clases
- Gestión de instructores
- Seguimiento de pagos
- Registros de asistencia
- Reportes y análisis

## Estructura de Archivos

```
yoga-school-management/
├── app.py                 # Aplicación principal de Flask
├── requirements.txt       # Dependencias de Python
├── yoga_school.db        # Base de datos SQLite (creada automáticamente)
├── templates/            # Plantillas HTML
│   ├── base.html
│   ├── index.html
│   ├── estudiantes.html
│   ├── nuevo_estudiante.html
│   ├── ver_estudiante.html
│   └── editar_estudiante.html
└── README.md
```

## Soporte

Este es un sistema ligero diseñado para escuelas de yoga pequeñas. Para soporte o solicitudes de características, por favor contacta al desarrollador.
