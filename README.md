# 🧘‍♀️ ATMA SUDDHI - DarmaSala System

Sistema completo de gestión para una escuela de yoga que incluye gestión de alumnos, pagos, citas individuales de yogaterapia, horarios semanales, calendario unificado y administración de clases.

**Desarrollado por:** Javier Ballesteros para DarmaSala - Espacio de Yoga  
**Licencia:** GNU GPL v3  
**Versión:** 2.0.0-final  

## 🌿 Inspiración (Poem & Reflection)

> "I exist as I am, that is enough,  
> If no other in the world be aware I sit content,  
> And if each and all be aware I sit content.  
> One world is aware and by far the largest to me, and that is myself,  
> And whether I come to my own to-day or in ten thousand or ten million years,  
> I can cheerfully take it now, or with equal cheerfulness I can wait."  
> — *Walt Whitman, Leaves of Grass*

**Reflexión:**  
Este sistema, DarmaSala, ha sido diseñado para aportar orden y serenidad a la gestión de un santuario de yoga. Al igual que Whitman celebra la suficiencia inherente del ser, este software busca simplificar las cargas administrativas para que practicantes y maestros puedan centrarse en el presente. Al organizar lo múltiple (alumnos, clases, finanzas) en una estructura armónica, el sistema actúa como un compañero silencioso en el camino hacia el equilibrio y el autoconocimiento.

## 📋 Tabla de Contenidos

- [Visualización](#-visualización)
- [Inspiración](#-inspiración)
- [Características Principales](#-características-principales)
- [Funcionalidades Detalladas](#-funcionalidades-detalladas)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Instalación](#-instalación)
- [Uso del Sistema](#-uso-del-sistema)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Pendientes](#-pendientes)
- [Contribución](#-contribución)

## 📸 Visualización

### 🏠 Inicio (Dashboard Principal)
Interfaz premium con el tema "Deep Purple & Enchanted Gold", acceso directo a Alumnos, Calendario, Yogaterapia y Economía.
![Pantalla de Inicio](documentation/screenshots/01_dashboard.png)

### 📅 Calendario y Gestión de Asistencias
Vista unificada de clases con capacidad de pasar lista de forma visual y moderna.
![Calendario](documentation/screenshots/04_calendario.png)
![Gestión de Asistencia](documentation/screenshots/05_asistencia_modal.png)

### 👤 Perfil del Alumno
Historial completo de asistencias, estadísticas y sesiones de yogaterapia integradas.
![Perfil de Alumno](documentation/screenshots/03_perfil_alumno.png)

### 📊 Gestión Económica
Dashboard de contabilidad avanzado con resumen de ingresos, gastos y balance mensual/anual.
![Economía](documentation/screenshots/02_economia.png)

## 🌟 Características Principales

### 🎯 **Gestión Completa de Alumnos**
- Registro y edición de información personal
- Historial de pagos y asistencia
- Seguimiento de progreso individual
- Gestión de contactos y comunicaciones

### 💰 **Sistema de Pagos Avanzado**
- Registro de pagos por clase suelta o bono
- Seguimiento de pagos pendientes
- Historial completo de transacciones
- Reportes de ingresos

### 🧘‍♀️ **Yogaterapia Individual**
- Sistema completo de citas individuales
- Registro detallado de sesiones terapéuticas
- Subida de archivos de práctica personal
- Seguimiento de objetivos terapéuticos
- Evaluación y recomendaciones

### 📅 **Calendario Unificado**
- **Vista Mensual**: Calendario completo con navegación entre meses
- **Vista Semanal**: Gestión detallada de la semana actual
- **Vista Anual**: 12 mini-calendarios con estadísticas del año
- Indicadores visuales para citas y horarios
- Creación de citas desde cualquier día

### ⏰ **Gestión de Horarios**
- Configuración de horarios semanales recurrentes
- Diferentes tipos de clases con precios personalizables
- Gestión de instructores y capacidad
- Horarios activos/inactivos

### ⚙️ **Configuración del Sistema**
- Gestión de tipos de clase
- Configuración de precios y duraciones
- Categorías de gastos
- Proveedores y facturación

## 👨‍💻 Información del Autor

**Desarrollador:** Javier Ballesteros  
**Email:** javierb507@gmail.com  
**Proyecto:** Desarrollado específicamente para DarmaSala - Espacio de Yoga  
**Repositorio:** https://github.com/javierb507/darmasala

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia Pública General de GNU v3.0 (GPL-3.0).

Para más información sobre la licencia, consulta el archivo [LICENSE](LICENSE) o visita: https://www.gnu.org/licenses/gpl-3.0.html

## 🤝 Contribución

Este proyecto fue desarrollado específicamente para DarmaSala, pero está disponible como software libre bajo licencia GPL v3. Si deseas contribuir o adaptar el sistema para tu propia escuela de yoga, por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 🚀 Despliegue en Producción (Linux VPS)

Para facilitar el despliegue en un VPS Linux (Ubuntu/Debian), se han incluido scripts de automatización en la carpeta `scripts/`:

1.  **Instalación automática**: Ejecuta `./scripts/setup_vps.sh` para instalar dependencias y preparar el entorno virtual.
2.  **Servicio de sistema**: Utiliza la plantilla `scripts/darmasala.service` para configurar el sistema como un servicio de `systemd` que se inicie automáticamente.

Consulta la guía detallada en [docs/deployment-ubuntu.md](docs/deployment-ubuntu.md) para más información sobre la configuración de Nginx y certificados SSL.

## 📞 Contacto

Para consultas sobre el sistema o soporte técnico, contacta a:
- **Javier Ballesteros** - javierb507@gmail.com
- **DarmaSala** - Espacio de Yoga