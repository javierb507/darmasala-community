# 🧘‍♀️ DarmaSala - Sistema de Gestión de Escuela de Yoga

## Documentación Completa del Sistema

### 📋 Índice
1. [Descripción General](#descripción-general)
2. [Funcionalidades Implementadas](#funcionalidades-implementadas)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Modelos de Base de Datos](#modelos-de-base-de-datos)
5. [Rutas y Endpoints](#rutas-y-endpoints)
6. [Templates y UI](#templates-y-ui)
7. [Instalación y Configuración](#instalación-y-configuración)
8. [Uso del Sistema](#uso-del-sistema)
9. [API Endpoints](#api-endpoints)
10. [Funcionalidades Pendientes](#funcionalidades-pendientes)

---

## 📖 Descripción General

**DarmaSala** es un sistema completo de gestión para escuelas de yoga desarrollado en Flask. Permite administrar alumnos, pagos, clases, horarios, asistencias, yogaterapia y contabilidad de manera integral.

### 🎯 Objetivos del Sistema
- Gestión completa de alumnos y sus datos
- Control de pagos y cuotas (mensuales y bimensuales)
- Seguimiento de asistencias a clases
- Administración de horarios y clases
- Gestión de sesiones de yogaterapia
- Control contable y de gastos
- Dashboard con estadísticas y reportes

---

## ✅ Funcionalidades Implementadas

### 👥 Gestión de Alumnos
- ✅ **Registro de alumnos** con datos completos
- ✅ **Edición de información** personal y médica
- ✅ **Vista detallada** con historial completo
- ✅ **Activación/desactivación** de alumnos
- ✅ **Búsqueda y filtrado** por nombre, email
- ✅ **Indicadores visuales** de estado de pagos
- ✅ **Detección de alumnos inactivos** (sin actividad +2 meses)

### 💰 Sistema de Pagos
- ✅ **Tipos de pago**: Cuotas, matrículas, clases sueltas, yogaterapia
- ✅ **Cuotas mensuales y bimensuales**
- ✅ **Validación de pagos duplicados**
- ✅ **Edición y eliminación de pagos**
- ✅ **Múltiples métodos de pago**: Efectivo, transferencia, tarjeta, Bizum
- ✅ **Cálculo automático de precios** según tipo de cuota
- ✅ **Año académico 25/26** (septiembre a agosto)

### 📚 Gestión de Clases
- ✅ **Configuración de clases** con precios personalizables
- ✅ **Múltiples tipos**: Yoga integral, menopausia, embarazadas, meditación
- ✅ **Configuración visual** con colores y niveles
- ✅ **Capacidad máxima y duración** configurable
- ✅ **Activación/desactivación** de clases

### 🕐 Horarios
- ✅ **Horarios semanales** completos
- ✅ **Vista calendario** visual
- ✅ **Histórico de cambios** en horarios
- ✅ **Asignación de instructores**

### 📅 Asistencias
- ✅ **Registro de asistencias** por clase y fecha
- ✅ **Histórico completo** con estadísticas
- ✅ **Porcentajes de asistencia** por alumno
- ✅ **Filtros por fecha y clase**
- ✅ **Observaciones** en cada asistencia

### 🧘‍♀️ Yogaterapia
- ✅ **Sesiones individuales** detalladas
- ✅ **Registro terapéutico** completo
- ✅ **Seguimiento de objetivos** y técnicas
- ✅ **Gestión de archivos** adjuntos
- ✅ **Control de pagos** específicos

### 💼 Gestión Económica
- ✅ **Dashboard contable** con gráficos
- ✅ **Gestión de gastos** mensuales
- ✅ **Categorización** de gastos
- ✅ **Proveedores y facturas**
- ✅ **Gastos fijos** recurrentes
- ✅ **Reportes PDF** exportables

### ⚙️ Configuración
- ✅ **Gestión de tipos de clase** con precios
- ✅ **Configuración visual** del sistema
- ✅ **Información del centro**
- ✅ **Backup automático**
- ✅ **Configuración avanzada**

---

## 🏗️ Arquitectura del Sistema

### Tecnologías Utilizadas
- **Backend**: Flask (Python)
- **Base de Datos**: SQLite con SQLAlchemy ORM
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Gráficos**: Chart.js
- **Iconos**: Font Awesome

### Estructura del Proyecto
```
darmasala/
├── app.py                 # Aplicación principal
├── config.py             # Configuración
├── requirements.txt      # Dependencias
├── templates/           # Templates HTML
│   ├── base.html        # Template base
│   ├── index.html       # Dashboard principal
│   ├── alumnos_mejorado.html
│   ├── ver_alumno_compacto.html
│   ├── configuracion.html
│   ├── economia/        # Templates económicos
│   └── components/      # Componentes reutilizables
├── utils/              # Utilidades
│   ├── export.py       # Exportación de datos
│   ├── backup.py       # Sistema de backup
│   └── validators.py   # Validadores
├── backups/           # Copias de seguridad
└── instance/          # Base de datos
```

---

## 🗄️ Modelos de Base de Datos

### Modelo Alumno
```python
class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    fecha_nacimiento = db.Column(db.Date)
    direccion = db.Column(db.Text)
    condiciones_medicas = db.Column(db.Text)
    tipo_cuota = db.Column(db.String(30), nullable=False)
    matricula_pagada = db.Column(db.Boolean, default=False)
    fecha_matricula = db.Column(db.Date)
    activo = db.Column(db.Boolean, default=True)
```

### Modelo Pago
```python
class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'))
    mes = db.Column(db.String(7))  # YYYY-MM
    año = db.Column(db.Integer)    # Para matrículas
    fecha_clase = db.Column(db.Date)  # Para clases sueltas
    monto = db.Column(db.Float, nullable=False)
    tipo_pago = db.Column(db.String(20))  # cuota, matricula, clase_suelta
    descripcion = db.Column(db.String(100))
    metodo_pago = db.Column(db.String(50))
```

### Modelo Clase
```python
class Clase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    precio_clase_suelta = db.Column(db.Float, default=15.00)
    precio_1_semanal = db.Column(db.Float, default=40.00)
    precio_2_semanal = db.Column(db.Float, default=70.00)
    precio_plana = db.Column(db.Float, default=90.00)
    precio_1_bimensual = db.Column(db.Float, default=75.00)
    precio_2_bimensual = db.Column(db.Float, default=135.00)
    color = db.Column(db.String(7), default='#007bff')
    nivel = db.Column(db.String(20), default='todos')
    duracion_minutos = db.Column(db.Integer, default=75)
    capacidad_maxima = db.Column(db.Integer, default=15)
    activa = db.Column(db.Boolean, default=True)
```

### Otros Modelos Importantes
- **HorarioSemanal**: Horarios de clases por día de la semana
- **Asistencia**: Registro de asistencias con observaciones
- **SesionYogaterapia**: Sesiones terapéuticas detalladas
- **GastoMensual**: Gastos y contabilidad
- **CategoriaGasto**: Categorización de gastos
- **Proveedor**: Gestión de proveedores
- **FacturaProveedor**: Facturas de proveedores

---

## 🛣️ Rutas y Endpoints Principales

### Gestión de Alumnos
- `GET /alumnos` - Lista de alumnos con filtros
- `GET /alumnos/nuevo` - Formulario nuevo alumno
- `POST /alumnos/nuevo` - Crear alumno
- `GET /alumnos/<id>` - Ver detalles del alumno
- `GET /alumnos/<id>/editar` - Editar alumno
- `POST /alumnos/<id>/eliminar` - Desactivar alumno

### Gestión de Pagos
- `GET /alumnos/<id>/pago` - Formulario agregar pago
- `POST /alumnos/<id>/pago` - Crear pago
- `GET /pagos/<id>/editar` - Editar pago
- `POST /pagos/<id>/eliminar` - Eliminar pago

### Configuración
- `GET /configuracion` - Panel de configuración
- `GET /configuracion/clases/nueva` - Nueva clase
- `GET /configuracion/clases/<id>/editar` - Editar clase

### API Endpoints
- `GET /api/stats` - Estadísticas del sistema
- `GET /api/clases` - Lista de clases (JSON)
- `POST /api/clases/<id>/toggle` - Activar/desactivar clase
- `POST /api/backup` - Crear backup

---

## 🎨 Templates y UI

### Sistema de Templates
- **base.html**: Template base con Bootstrap 5
- **Componentes reutilizables**: Alertas, notificaciones, filtros
- **Responsive design**: Adaptado a móviles y tablets
- **Iconografía consistente**: Font Awesome

### Características UI
- ✅ **Diseño responsive** para todos los dispositivos
- ✅ **Indicadores visuales** de estado (pagos, asistencias)
- ✅ **Gráficos interactivos** con Chart.js
- ✅ **Filtros y búsquedas** en tiempo real
- ✅ **Modales de confirmación** para acciones críticas
- ✅ **Navegación intuitiva** con breadcrumbs

---

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.8+
- pip (gestor de paquetes de Python)

### Instalación
```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/darmasala.git
cd darmasala

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Inicializar la aplicación
python crear_app_limpia.py

# 5. Ejecutar la aplicación
python app.py
```

### Configuración Inicial
1. Acceder a `http://localhost:5000`
2. Ir a **Configuración** para personalizar:
   - Información del centro
   - Precios de clases
   - Configuración avanzada

---

## 📖 Uso del Sistema

### Flujo de Trabajo Típico

#### 1. Configuración Inicial
1. **Configurar clases** y precios en `/configuracion`
2. **Crear horarios** semanales
3. **Configurar información** del centro

#### 2. Gestión de Alumnos
1. **Registrar nuevos alumnos** con sus datos
2. **Configurar tipo de cuota** (mensual/bimensual)
3. **Registrar pago de matrícula** si corresponde

#### 3. Gestión de Pagos
1. **Registrar cuotas mensuales** o bimensuales
2. **Validar pagos duplicados** automáticamente
3. **Editar pagos** si hay errores

#### 4. Seguimiento de Asistencias
1. **Registrar asistencias** por clase
2. **Revisar estadísticas** de asistencia
3. **Identificar alumnos** con baja asistencia

#### 5. Gestión Económica
1. **Registrar gastos** mensuales
2. **Categorizar gastos** por tipo
3. **Generar reportes** económicos

---

## 🔌 API Endpoints

### Estadísticas
```http
GET /api/stats
Response: {
  "alumnos_activos": 15,
  "total_pagos": 1250.50,
  "ultimo_backup": "2025-09-18"
}
```

### Gestión de Clases
```http
GET /api/clases
Response: {
  "success": true,
  "clases": [
    {
      "id": 1,
      "nombre": "Yoga integral",
      "precio_clase_suelta": 15.00,
      "activa": true
    }
  ]
}
```

### Control de Clases
```http
POST /api/clases/1/toggle
Response: {
  "success": true,
  "activa": false
}
```

---

## 📊 Características Destacadas

### 🎯 Gestión Inteligente de Pagos
- **Detección automática** de pagos duplicados
- **Cálculo automático** de precios según tipo de cuota
- **Soporte para cuotas bimensuales** con lógica específica
- **Año académico personalizado** (25/26)

### 📈 Dashboard Analítico
- **Estadísticas en tiempo real** de alumnos y pagos
- **Gráficos interactivos** de ingresos y gastos
- **Indicadores visuales** de estado de pagos
- **Detección de alumnos inactivos**

### 🔒 Validaciones y Seguridad
- **Validación de datos** en formularios
- **Prevención de duplicados** en pagos
- **Confirmaciones** para acciones críticas
- **Backup automático** de datos

### 📱 Experiencia de Usuario
- **Interfaz responsive** para móviles
- **Navegación intuitiva** con iconos claros
- **Feedback visual** inmediato
- **Búsquedas y filtros** eficientes

---

## 🔧 Configuración Avanzada

### Variables de Entorno
```python
# config.py
SECRET_KEY = 'tu-clave-secreta'
SQLALCHEMY_DATABASE_URI = 'sqlite:///yoga_school.db'
BACKUP_AUTOMATICO = True
DURACION_CLASE_DEFAULT = 75
INSTRUCTOR_DEFAULT = 'Minouche'
```

### Personalización de Precios
Los precios se pueden configurar por clase en `/configuracion`:
- Clase suelta
- 1 clase semanal
- 2 clases semanales
- Tarifa plana
- 1 clase bimensual
- 2 clases bimensuales

---

## 📝 Notas Técnicas

### Base de Datos
- **SQLite** para desarrollo y producción pequeña
- **Migraciones automáticas** con SQLAlchemy
- **Relaciones optimizadas** entre modelos
- **Índices** en campos de búsqueda frecuente

### Rendimiento
- **Consultas optimizadas** con joins eficientes
- **Paginación** en listas largas
- **Carga lazy** de relaciones
- **Cache** de consultas frecuentes

### Mantenimiento
- **Logs** de errores y actividad
- **Backup automático** configurable
- **Limpieza** de datos antiguos
- **Monitoreo** de rendimiento

---

## 🎓 Casos de Uso Específicos

### Gestión de Cuotas Bimensuales
El sistema maneja automáticamente las cuotas bimensuales:
- **Enero-Febrero**, **Marzo-Abril**, **Mayo-Junio**
- **Julio-Agosto**, **Septiembre-Octubre**, **Noviembre-Diciembre**

### Año Académico 25/26
- Comienza en **septiembre 2025**
- Termina en **agosto 2026**
- Matrícula válida para todo el período

### Detección de Inactividad
Alumnos marcados como inactivos si:
- No tienen pagos en los últimos 60 días
- No tienen asistencias en los últimos 60 días

---

## 📞 Soporte y Mantenimiento

### Backup y Recuperación
- **Backup manual** desde configuración
- **Backup automático** semanal (configurable)
- **Restauración** desde archivos de backup

### Resolución de Problemas
1. **Verificar logs** de la aplicación
2. **Comprobar integridad** de la base de datos
3. **Restaurar desde backup** si es necesario
4. **Contactar soporte** técnico

---

*Documentación actualizada: Septiembre 2025*
*Versión del sistema: 2.0*