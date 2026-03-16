# 🚀 Guía de Instalación y Uso

## 📋 Prerrequisitos

- Python 3.11 o superior
- Git
- Navegador web moderno (Chrome, Firefox, Safari, Edge)

## 🛠️ Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/javierb507/yoga-school-management.git
cd yoga-school-management
```

### 2. Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Inicializar Base de Datos
```bash
# Recrear base de datos
python recrear_bd.py

# Cargar datos de prueba
python cargar_datos_prueba.py
```

### 5. Ejecutar la Aplicación
```bash
python app.py
```

### 6. Acceder a la Aplicación
- Abrir navegador en `http://127.0.0.1:5000`
- La aplicación se ejecuta en modo debug

## 📖 Uso del Sistema

### Acceso Inicial
1. Abrir la aplicación en el navegador
2. La aplicación se inicializa con datos de prueba
3. Navegar por las diferentes secciones del menú

### Gestión de Alumnos
1. **Ver Alumnos**: Lista completa en la página principal
2. **Agregar Alumno**: Botón "Nuevo Alumno"
3. **Editar Alumno**: Clic en el nombre del alumno
4. **Ver Detalles**: Información completa y historial

### Creación de Citas de Yogaterapia
1. **Desde Calendario**: Clic en cualquier día
2. **Desde Menú**: Sección "Yogaterapia" > "Nueva Cita"
3. **Desde Alumno**: Botón "Nueva Cita" en perfil del alumno
4. **Completar Formulario**: Datos personales y terapéuticos

### Gestión del Calendario
1. **Vista Mensual**: Navegación principal
2. **Vista Semanal**: Botón "Vista Semanal"
3. **Vista Anual**: Botón "Vista Anual"
4. **Crear Citas**: Clic en cualquier día disponible

### Configuración de Horarios
1. **Ir a Horarios**: Menú principal
2. **Nuevo Horario**: Botón "Nuevo Horario"
3. **Configurar**: Día, hora, clase, instructor
4. **Activar**: Marcar como activo

## 🔧 Configuración

### Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta_aqui
DATABASE_URL=sqlite:///yoga_school.db
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216
```

### Configuración de Base de Datos
- **Desarrollo**: SQLite (por defecto)
- **Producción**: PostgreSQL (recomendado)

### Configuración de Archivos
- **Directorio de subidas**: `static/uploads/`
- **Tamaño máximo**: 16MB por archivo
- **Tipos permitidos**: PDF, JPG, PNG, DOC, DOCX

## 🐛 Solución de Problemas

### Error de Base de Datos
```bash
# Eliminar base de datos existente
rm yoga_school.db

# Recrear base de datos
python recrear_bd.py
```

### Error de Dependencias
```bash
# Actualizar pip
pip install --upgrade pip

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error de Puerto
```bash
# Cambiar puerto en app.py
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Error de Permisos
```bash
# Dar permisos de escritura
chmod 755 static/uploads/
```

## 📁 Estructura del Proyecto

```
yoga-school-management/
├── app.py                          # Aplicación principal Flask
├── requirements.txt                # Dependencias Python
├── recrear_bd.py                   # Script de inicialización de BD
├── cargar_datos_prueba.py          # Script de datos de prueba
├── README.md                       # Documentación principal
├── FUNCIONALIDADES.md              # Funcionalidades detalladas
├── PENDIENTES.md                   # Tareas pendientes
├── INSTALACION.md                  # Guía de instalación
├── templates/                      # Plantillas HTML
│   ├── base.html                   # Plantilla base
│   ├── index.html                  # Página principal
│   ├── alumnos.html                # Lista de alumnos
│   ├── ver_alumno.html             # Perfil de alumno
│   ├── yogaterapia.html            # Lista de sesiones
│   ├── nueva_yogaterapia.html      # Formulario de nueva cita
│   ├── ver_sesion_yogaterapia.html # Detalles de sesión
│   ├── editar_sesion_yogaterapia.html # Edición de sesión
│   ├── calendario_unificado.html   # Vista mensual del calendario
│   ├── calendario_semanal.html     # Vista semanal del calendario
│   ├── calendario_anual.html       # Vista anual del calendario
│   ├── horarios.html               # Gestión de horarios
│   ├── nuevo_horario.html          # Formulario de nuevo horario
│   ├── configuracion.html          # Configuración del sistema
│   └── usuarios.html               # Gestión de usuarios
├── static/                         # Archivos estáticos
│   ├── css/                        # Estilos CSS
│   ├── js/                         # JavaScript
│   └── uploads/                    # Archivos subidos
└── yoga_school.db                  # Base de datos SQLite
```

## 🔒 Seguridad

### Recomendaciones de Producción
1. **Cambiar SECRET_KEY**: Usar clave secreta fuerte
2. **HTTPS**: Configurar SSL/TLS
3. **Firewall**: Restringir acceso a puertos
4. **Backup**: Respaldos regulares de BD
5. **Logs**: Monitoreo de actividad

### Configuración de Producción
```python
# app.py - Configuración de producción
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['DEBUG'] = False
```

## 📊 Monitoreo

### Logs de Aplicación
- **Desarrollo**: Logs en consola
- **Producción**: Archivos de log
- **Niveles**: DEBUG, INFO, WARNING, ERROR

### Métricas de Rendimiento
- **Tiempo de respuesta**: < 2 segundos
- **Uso de memoria**: Monitoreo continuo
- **Errores**: Alertas automáticas

## 🔄 Actualizaciones

### Actualizar Código
```bash
# Obtener últimos cambios
git pull origin main

# Instalar nuevas dependencias
pip install -r requirements.txt

# Reiniciar aplicación
python app.py
```

### Actualizar Base de Datos
```bash
# Backup de datos existentes
cp yoga_school.db backup_$(date +%Y%m%d).db

# Aplicar migraciones
python recrear_bd.py
```

## 📞 Soporte

### Problemas Comunes
1. **Error 500**: Revisar logs de aplicación
2. **Error de BD**: Verificar permisos de archivo
3. **Error de puerto**: Cambiar puerto en configuración
4. **Error de dependencias**: Reinstalar requirements.txt

### Contacto
- **Email**: soporte@yogaschool.com
- **GitHub**: [Issues](https://github.com/javierb507/yoga-school-management/issues)
- **Documentación**: [Wiki](https://github.com/javierb507/yoga-school-management/wiki)

---

**Última actualización**: Septiembre 2025
