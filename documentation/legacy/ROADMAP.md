# 🗺️ ROADMAP - Sistema de Gestión DarmaSala

## 📋 **TAREAS PENDIENTES PRIORITARIAS**

### 🎯 **1. MEJORAS EN GESTIÓN DE ALUMNOS**

#### 📊 Vista de Pagos Mejorada
- [ ] **Indicadores visuales más claros** para meses pagados/pendientes
- [ ] **Tooltip con detalles** al pasar mouse sobre cada mes
- [ ] **Filtros por estado de pago** (al día, atrasados, sin matrícula)
- [ ] **Vista calendario** para pagos mensuales
- [ ] **Alertas automáticas** para pagos vencidos

#### 👥 Gestión de Alumnos Desactivados
- [ ] **Arreglar funcionalidad de reactivación** (actualmente no funciona)
- [ ] **Motivo de desactivación** (suspensión temporal, baja definitiva, etc.)
- [ ] **Fecha de desactivación** y usuario que la realizó
- [ ] **Historial de estados** del alumno
- [ ] **Búsqueda y filtros** en alumnos desactivados

### 💰 **2. DESARROLLO DEL MÓDULO ECONÓMICO**

#### 📄 Gestión de Facturas
- [ ] **Formulario completo** para nueva factura
- [ ] **Subida de archivos PDF** de facturas
- [ ] **Estados avanzados**: Pendiente, Pagada, Vencida, Anulada
- [ ] **Recordatorios automáticos** de vencimientos
- [ ] **Búsqueda y filtros** por proveedor, fecha, estado

#### 🏢 Gestión de Proveedores
- [ ] **Formulario completo** para nuevo proveedor
- [ ] **Edición de proveedores** existentes
- [ ] **Historial de facturas** por proveedor
- [ ] **Datos fiscales completos** (dirección fiscal, contactos)

#### 💸 Gastos Fijos
- [ ] **Formulario para gastos recurrentes** (luz, agua, internet, alquiler)
- [ ] **Generación automática** de gastos mensuales
- [ ] **Calendario de vencimientos** de gastos fijos
- [ ] **Categorización avanzada** con subcategorías

#### 📊 Dashboard Económico Configurable
- [ ] **Gráficos interactivos** (ingresos vs gastos)
- [ ] **Métricas personalizables** por usuario
- [ ] **Comparativas mensuales/anuales**
- [ ] **Exportación a Excel** con formato profesional
- [ ] **Reportes automáticos** por email

### 🔧 **3. MEJORAS GENERALES DE LA APLICACIÓN**

#### 🎨 Interfaz de Usuario
- [ ] **Tema oscuro/claro** configurable
- [ ] **Responsive design** mejorado para móviles
- [ ] **Iconos más intuitivos** y consistentes
- [ ] **Animaciones suaves** en transiciones
- [ ] **Breadcrumbs** para navegación

#### 🔐 Seguridad y Usuarios
- [ ] **Sistema de login** con usuarios diferenciados
- [ ] **Roles y permisos** (administrador, instructor, solo lectura)
- [ ] **Backup automático** de base de datos
- [ ] **Log de actividades** del usuario
- [ ] **Recuperación de datos** eliminados accidentalmente

#### 📱 Funcionalidades Móviles
- [ ] **App móvil** o PWA (Progressive Web App)
- [ ] **Notificaciones push** para pagos vencidos
- [ ] **Acceso offline** a datos básicos
- [ ] **Sincronización automática** cuando hay conexión

#### 🔄 Integración y Automatización
- [ ] **Integración con bancos** para importar movimientos
- [ ] **Generación automática** de recibos de pago
- [ ] **Envío automático** de recordatorios por email/SMS
- [ ] **Sincronización con Google Calendar** para clases
- [ ] **API REST** para integraciones externas

#### 📈 Reportes y Análisis
- [ ] **Dashboard de KPIs** (alumnos nuevos, bajas, ingresos)
- [ ] **Análisis de tendencias** de asistencia
- [ ] **Reportes de rentabilidad** por tipo de clase
- [ ] **Predicción de ingresos** basada en históricos
- [ ] **Comparativas con años anteriores**

#### 🎓 Gestión Académica Avanzada
- [ ] **Planificación de clases** con temarios
- [ ] **Evaluación de progreso** de alumnos
- [ ] **Certificados de participación** automáticos
- [ ] **Gestión de sustituciones** de instructores
- [ ] **Reserva de clases** por parte de alumnos

### 🛠️ **4. MEJORAS TÉCNICAS**

#### ⚡ Rendimiento
- [ ] **Optimización de consultas** a base de datos
- [ ] **Cache de datos** frecuentemente consultados
- [ ] **Compresión de imágenes** automática
- [ ] **Lazy loading** en listas largas

#### 🔍 Búsqueda y Filtros
- [ ] **Búsqueda global** en toda la aplicación
- [ ] **Filtros avanzados** en todas las listas
- [ ] **Búsqueda por texto** en facturas y documentos
- [ ] **Autocompletado** en formularios

#### 📊 Base de Datos
- [ ] **Migración a PostgreSQL** para mayor robustez
- [ ] **Índices optimizados** para consultas frecuentes
- [ ] **Archivado automático** de datos antiguos
- [ ] **Backup incremental** diario

---

## 🎯 **PRIORIDADES INMEDIATAS (Próxima Versión)**

### 🚨 **CRÍTICO - Debe funcionar**
1. **Arreglar reactivación de alumnos desactivados**
2. **Completar formularios de facturas y proveedores**
3. **Implementar gestión de gastos fijos**

### 🔥 **ALTA PRIORIDAD - Impacto en usabilidad**
1. **Mejorar vista visual de pagos mensuales**
2. **Dashboard económico con gráficos básicos**
3. **Sistema de alertas para pagos vencidos**

### 📈 **MEDIA PRIORIDAD - Mejoras incrementales**
1. **Filtros y búsquedas en listas**
2. **Exportación mejorada a Excel**
3. **Responsive design para móviles**

---

## 📝 **NOTAS DE DESARROLLO**

### 🏗️ **Arquitectura Actual**
- **Backend**: Flask + SQLAlchemy + SQLite
- **Frontend**: Bootstrap 5 + Jinja2 templates
- **Base de datos**: SQLite (considerar migrar a PostgreSQL)

### 🔄 **Próximos Pasos Técnicos**
1. Implementar tests unitarios básicos
2. Configurar CI/CD para despliegue automático
3. Documentar API endpoints existentes
4. Establecer estándares de código y linting

### 📋 **Changelog**
- **v1.1.0** (Actual): Módulo económico básico, gestión de alumnos mejorada
- **v1.0.0**: Sistema básico de gestión de yoga con alumnos y pagos

---

*Última actualización: Septiembre 2025*
*Mantenido por: Equipo DarmaSala*
