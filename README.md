# 🧘‍♀️ Atma Suddhi - Sistema de Gestión de Escuela de Yoga

[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](https://github.com/tu-usuario/yoga-school-management)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-2.0+-red.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

Sistema completo de gestión para escuelas de yoga desarrollado en Flask. Gestiona alumnos, pagos, clases, asistencias, yogaterapia y contabilidad de manera integral.

## 🚀 Características Principales

- **👥 Gestión Completa de Alumnos** - Registro, edición, seguimiento y estados
- **💰 Sistema Avanzado de Pagos** - Cuotas mensuales/bimensuales, matrículas, validación de duplicados
- **📚 Configuración de Clases** - Precios personalizables, niveles, capacidades
- **📅 Control de Asistencias** - Histórico completo con estadísticas y porcentajes
- **🧘‍♀️ Gestión de Yogaterapia** - Sesiones terapéuticas detalladas con seguimiento
- **💼 Dashboard Económico** - Contabilidad, gastos, reportes y gráficos interactivos
- **⚙️ Configuración Avanzada** - Personalización completa del sistema

## ✨ Funcionalidades Destacadas

### 🎯 Gestión Inteligente
- **Detección automática** de pagos duplicados
- **Año académico 25/26** (septiembre a agosto)
- **Cuotas bimensuales** con lógica específica
- **Alumnos inactivos** detectados automáticamente
- **Precios dinámicos** según tipo de cuota

### 📊 Analytics y Reportes
- **Dashboard interactivo** con gráficos en tiempo real
- **Estadísticas de asistencia** por alumno y clase
- **Indicadores visuales** de estado de pagos
- **Histórico completo** de todas las actividades
- **Exportación de reportes** (en desarrollo)

### 🎨 Experiencia de Usuario
- **Diseño responsive** para todos los dispositivos
- **Interfaz intuitiva** con Bootstrap 5
- **Navegación fluida** con confirmaciones inteligentes
- **Búsquedas y filtros** eficientes
- **Feedback visual** inmediato

## 📋 Estado de Funcionalidades

| Módulo | Estado | Completado |
|--------|--------|------------|
| 👥 Gestión de Alumnos | ✅ Completo | 100% |
| 💰 Sistema de Pagos | ✅ Completo | 95% |
| 📚 Gestión de Clases | ✅ Funcional | 85% |
| 📅 Asistencias | ✅ Funcional | 80% |
| 🧘‍♀️ Yogaterapia | ✅ Funcional | 75% |
| 💼 Contabilidad | ✅ Funcional | 70% |
| ⚙️ Configuración | 🔄 En desarrollo | 60% |

## 🛠️ Tecnologías

- **Backend**: Flask 2.0+ (Python 3.8+)
- **Base de Datos**: SQLite + SQLAlchemy ORM
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript ES6
- **Gráficos**: Chart.js
- **Iconos**: Font Awesome 6
- **Validación**: WTForms + Custom validators

## 📦 Instalación Rápida

### Opción 1: Instalación Automática
```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/yoga-school-management.git
cd yoga-school-management

# 2. Ejecutar script de instalación
python crear_app_limpia.py

# 3. Iniciar aplicación
python app.py
```

### Opción 2: Instalación Manual
```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Inicializar base de datos
python crear_app_limpia.py

# 4. Ejecutar aplicación
python app.py
```

### 🌐 Acceso
```
http://localhost:5000
```

## 📖 Documentación

- **📚 [Documentación Completa](DOCUMENTACION_COMPLETA.md)** - Guía detallada del sistema
- **📋 [Funcionalidades Pendientes](TODO_FUNCIONALIDADES.md)** - Roadmap y tareas pendientes
- **🔧 [Guía de Instalación](docs/INSTALACION.md)** - Instalación paso a paso
- **🎯 [Casos de Uso](docs/CASOS_USO.md)** - Ejemplos prácticos de uso

## 🎯 Casos de Uso Principales

### 👩‍🏫 Para Instructores
- Gestión completa de alumnos y sus datos
- Control de asistencias por clase
- Seguimiento de pagos y cuotas
- Planificación de horarios semanales

### 👨‍💼 Para Administradores
- Dashboard económico con métricas clave
- Reportes de ingresos y gastos
- Control de rentabilidad por clase
- Gestión de proveedores y facturas

### 🧘‍♀️ Para Terapeutas
- Gestión detallada de sesiones de yogaterapia
- Seguimiento de objetivos terapéuticos
- Archivo de documentos y notas
- Control específico de pagos terapéuticos

## 📱 Características Técnicas

### 🔒 Seguridad
- Validación robusta de datos
- Prevención de inyección SQL
- Sanitización de entradas
- Backup automático configurable

### ⚡ Rendimiento
- Consultas optimizadas con SQLAlchemy
- Carga lazy de relaciones
- Índices en campos de búsqueda
- Cache de consultas frecuentes

### 📱 Responsive
- Diseño mobile-first
- Optimizado para tablets
- Interfaz adaptativa
- Touch-friendly en móviles

## 🗺️ Roadmap

### 🎯 Versión 2.1 (Octubre 2025)
- [ ] Corrección de bugs críticos
- [ ] Registro manual de asistencias
- [ ] Reportes PDF básicos
- [ ] Sistema de notificaciones

### 🚀 Versión 2.2 (Noviembre 2025)
- [ ] Dashboard mejorado con más gráficos
- [ ] Calendario de clases interactivo
- [ ] Búsqueda avanzada de alumnos
- [ ] Sistema de descuentos y promociones

### 🌟 Versión 3.0 (2026)
- [ ] Sistema de usuarios y permisos
- [ ] App móvil nativa
- [ ] Reserva online de clases
- [ ] Integración con pasarelas de pago

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. **Fork** el proyecto
2. **Crea** una rama para tu feature (`git checkout -b feature/NuevaFuncionalidad`)
3. **Commit** tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/NuevaFuncionalidad`)
5. **Abre** un Pull Request

### 📝 Guías de Contribución
- Sigue las convenciones de código existentes
- Agrega tests para nuevas funcionalidades
- Actualiza la documentación cuando sea necesario
- Usa mensajes de commit descriptivos

## 🐛 Reportar Bugs

Encontraste un bug? [Crea un issue](https://github.com/tu-usuario/yoga-school-management/issues) con:
- Descripción detallada del problema
- Pasos para reproducir el error
- Capturas de pantalla si es relevante
- Información del entorno (OS, Python version, etc.)

## 📊 Estadísticas del Proyecto

- **Líneas de código**: ~5,000
- **Templates**: 25+
- **Modelos de BD**: 15
- **Rutas**: 50+
- **Tests**: En desarrollo

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT** - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Contacto y Soporte

- **🐛 Issues**: [GitHub Issues](https://github.com/tu-usuario/yoga-school-management/issues)
- **📧 Email**: soporte@atmasuddhi.es
- **🌐 Web**: [atmasuddhi.es](http://atmasuddhi.es)
- **📖 Docs**: [Documentación Completa](DOCUMENTACION_COMPLETA.md)

## 🙏 Agradecimientos

- **[Bootstrap](https://getbootstrap.com)** - Framework CSS
- **[Font Awesome](https://fontawesome.com)** - Iconografía
- **[Chart.js](https://chartjs.org)** - Gráficos interactivos
- **[Flask](https://flask.palletsprojects.com)** - Framework web
- **[SQLAlchemy](https://sqlalchemy.org)** - ORM para Python

---

<div align="center">

**⭐ Si te gusta este proyecto, dale una estrella en GitHub ⭐**

Hecho con ❤️ para la comunidad de yoga

</div>