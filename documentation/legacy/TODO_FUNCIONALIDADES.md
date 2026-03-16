# 📋 TODO - Funcionalidades Pendientes

## Estado Actual: ✅ FUNCIONAL
**Fecha**: Septiembre 2025  
**Versión**: 2.0

---

## 🚀 Funcionalidades Pendientes por Prioridad

### 🔴 ALTA PRIORIDAD (Próximas 2 semanas)

#### 1. Corrección de Errores Críticos
- [ ] **Resolver problema de base de datos** - Las nuevas columnas del modelo Clase no se crean correctamente
- [ ] **Probar script crear_app_limpia.py** - Verificar que funciona sin errores
- [ ] **Validar todas las rutas** - Asegurar que no hay errores 404 o 500
- [ ] **Probar funcionalidad de editar pagos** - Verificar que funciona correctamente
- [ ] **Validar API endpoints** - Comprobar que devuelven datos correctos

#### 2. Funcionalidades Básicas Faltantes
- [ ] **Registro manual de asistencias** - Interfaz para marcar asistencias por clase
- [ ] **Generación de reportes PDF** - Implementar exportación de reportes
- [ ] **Sistema de notificaciones** - Alertas para pagos vencidos
- [ ] **Búsqueda avanzada de alumnos** - Filtros por estado, tipo de cuota, etc.

### 🟡 MEDIA PRIORIDAD (Próximo mes)

#### 3. Mejoras de UX/UI
- [ ] **Dashboard mejorado** - Más gráficos y estadísticas
- [ ] **Calendario de clases** - Vista mensual con asistencias
- [ ] **Notificaciones en tiempo real** - Usando WebSockets
- [ ] **Modo oscuro** - Tema alternativo para la interfaz
- [ ] **Responsive mejorado** - Optimización para tablets

#### 4. Gestión Avanzada de Alumnos
- [ ] **Historial médico detallado** - Seguimiento de condiciones
- [ ] **Fotos de alumnos** - Upload y gestión de imágenes
- [ ] **Comunicación integrada** - WhatsApp/Email desde la app
- [ ] **Etiquetas y categorías** - Clasificación personalizada de alumnos
- [ ] **Notas privadas** - Comentarios internos sobre alumnos

#### 5. Sistema de Pagos Avanzado
- [ ] **Descuentos y promociones** - Sistema de cupones
- [ ] **Pagos recurrentes** - Domiciliación bancaria
- [ ] **Facturación automática** - Generación de facturas PDF
- [ ] **Recordatorios de pago** - Email/SMS automáticos
- [ ] **Planes de pago** - Fraccionamiento de cuotas

### 🟢 BAJA PRIORIDAD (Futuro)

#### 6. Funcionalidades Avanzadas
- [ ] **App móvil** - Aplicación nativa para alumnos
- [ ] **Reserva online** - Sistema de booking de clases
- [ ] **Integración con redes sociales** - Compartir logros
- [ ] **Gamificación** - Sistema de puntos y logros
- [ ] **Clases virtuales** - Integración con Zoom/Meet

#### 7. Análisis y Reportes
- [ ] **Analytics avanzado** - Métricas de retención, LTV
- [ ] **Predicción de abandono** - ML para detectar riesgo
- [ ] **Reportes automáticos** - Envío periódico por email
- [ ] **Comparativas temporales** - Análisis año a año
- [ ] **Exportación a Excel** - Datos para análisis externo

#### 8. Integración y APIs
- [ ] **API REST completa** - Para integraciones externas
- [ ] **Webhook system** - Notificaciones a sistemas externos
- [ ] **Integración contable** - Conexión con software contable
- [ ] **Sincronización en la nube** - Backup automático online
- [ ] **Multi-centro** - Gestión de múltiples ubicaciones

---

## 🔧 Mejoras Técnicas Pendientes

### Infraestructura
- [ ] **Migración a PostgreSQL** - Para mejor rendimiento
- [ ] **Sistema de logs mejorado** - Logging estructurado
- [ ] **Monitoreo de rendimiento** - Métricas de la aplicación
- [ ] **Tests automatizados** - Suite completa de tests
- [ ] **CI/CD Pipeline** - Despliegue automático

### Seguridad
- [ ] **Autenticación de usuarios** - Login/logout con roles
- [ ] **Permisos granulares** - Control de acceso por funcionalidad
- [ ] **Encriptación de datos** - Datos sensibles encriptados
- [ ] **Audit trail** - Registro de todas las acciones
- [ ] **Backup encriptado** - Copias de seguridad seguras

### Optimización
- [ ] **Cache Redis** - Para consultas frecuentes
- [ ] **Optimización de consultas** - Índices y queries eficientes
- [ ] **Compresión de assets** - CSS/JS minificados
- [ ] **CDN para assets** - Carga rápida de recursos
- [ ] **Lazy loading** - Carga bajo demanda

---

## 🐛 Bugs Conocidos

### Críticos
- [ ] **Error en creación de BD** - Columnas de Clase no se crean
- [ ] **Rutas de configuración** - Algunas rutas devuelven 404
- [ ] **Validación de pagos** - Falsos positivos en duplicados

### Menores
- [ ] **Formato de fechas** - Inconsistencia en algunos templates
- [ ] **Responsive en móviles** - Algunos elementos se solapan
- [ ] **Validación de formularios** - Mensajes de error poco claros

---

## 📊 Métricas de Desarrollo

### Completado ✅
- **Gestión básica de alumnos**: 100%
- **Sistema de pagos**: 90%
- **Gestión de clases**: 85%
- **Dashboard básico**: 80%
- **Configuración**: 75%

### En Progreso 🔄
- **Sistema de asistencias**: 70%
- **Yogaterapia**: 60%
- **Gestión económica**: 65%

### Pendiente ⏳
- **Reportes avanzados**: 0%
- **App móvil**: 0%
- **Integración APIs**: 0%

---

## 🎯 Roadmap por Versiones

### Versión 2.1 (Octubre 2025)
- ✅ Corrección de bugs críticos
- ✅ Registro manual de asistencias
- ✅ Reportes PDF básicos
- ✅ Notificaciones de pagos vencidos

### Versión 2.2 (Noviembre 2025)
- 📊 Dashboard mejorado con más gráficos
- 📅 Calendario de clases interactivo
- 🔍 Búsqueda avanzada de alumnos
- 💳 Sistema de descuentos

### Versión 3.0 (Enero 2026)
- 👤 Sistema de usuarios y permisos
- 📱 App móvil básica
- 🌐 Reserva online de clases
- 📈 Analytics avanzado

### Versión 3.5 (Abril 2026)
- 🤖 Predicción de abandono con ML
- 🔗 Integración con software contable
- ☁️ Sincronización en la nube
- 🏢 Soporte multi-centro

---

## 📝 Notas de Desarrollo

### Decisiones Técnicas Pendientes
- [ ] **Migrar a PostgreSQL** vs mantener SQLite
- [ ] **Implementar autenticación** con Flask-Login vs custom
- [ ] **Frontend framework** - Mantener vanilla JS vs React/Vue
- [ ] **Deployment** - Docker vs tradicional
- [ ] **Monitoring** - Sentry vs custom logging

### Consideraciones de UX
- [ ] **Flujo de onboarding** para nuevos usuarios
- [ ] **Tutoriales interactivos** para funcionalidades complejas
- [ ] **Shortcuts de teclado** para usuarios avanzados
- [ ] **Personalización de dashboard** por usuario
- [ ] **Tema claro/oscuro** según preferencias

---

## 🚨 Problemas Críticos a Resolver

### 1. Base de Datos
**Problema**: Las nuevas columnas del modelo Clase no se crean automáticamente  
**Impacto**: Alto - Impide el funcionamiento de la configuración de clases  
**Solución propuesta**: Script de migración manual o recreación completa de BD  
**Prioridad**: 🔴 CRÍTICA

### 2. Rutas API
**Problema**: Algunas rutas API no están implementadas completamente  
**Impacto**: Medio - Funcionalidades de configuración no funcionan  
**Solución propuesta**: Completar implementación de todas las rutas  
**Prioridad**: 🔴 ALTA

### 3. Validación de Datos
**Problema**: Validaciones inconsistentes en formularios  
**Impacto**: Medio - Puede causar errores de datos  
**Solución propuesta**: Implementar validadores centralizados  
**Prioridad**: 🟡 MEDIA

---

## 📞 Contacto y Soporte

Para reportar bugs o solicitar nuevas funcionalidades:
- **GitHub Issues**: [Crear issue](https://github.com/tu-usuario/yoga-school-management/issues)
- **Email**: soporte@atmasuddhi.es
- **Documentación**: Ver DOCUMENTACION_COMPLETA.md

---

*Última actualización: Septiembre 2025*  
*Próxima revisión: Octubre 2025*