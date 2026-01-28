# 🚀 Roadmap: Próximos Pasos

Lista de implementaciones priorizadas de menor a mayor complejidad técnica.

## 1. Personalización Estética y de Identidad (Baja Complejidad)
**Objetivo**: Permitir que el usuario cambie la identidad visual de la escuela sin tocar el código.
- [ ] **Nombre de la Escuela**: Campo en configuración para cambiar el título global.
- [ ] **Gestión de Logo**: Subida de imagen para el logo de la barra de navegación y facturas.
- [ ] **Apariencia Gráfica**: Selector de colores básicos (primario/secundario) que actualice variables CSS.
- [ ] **Favicon personalizado**: Permitir subir el icono de la pestaña del navegador.

## 2. Sección de Documentación Integrada (Baja Complejidad)
**Objetivo**: Facilitar el aprendizaje del sistema dentro de la propia aplicación.
- [ ] **Centro de Ayuda**: Nueva ruta `/ayuda` con guías interactivas.
- [ ] **Tooltips Informativos**: Añadir iconos de información `(i)` en campos complejos.
- [ ] **Videos/Manuales**: Enlaces a documentación externa o manuales PDF embebidos.
- [ ] **Sección de "Primeros Pasos"**: Guía rápida para nuevos usuarios en el Dashboard.

## 3. Backups Manuales con Descarga Local (Complejidad Media)
**Objetivo**: Garantizar la seguridad de los datos permitiendo al usuario llevarse una copia física.
- [ ] **Botón de Backup**: Función en configuración para generar un archivo `.sqlite` o `.json`.
- [ ] **Descarga Directa**: El sistema empaqueta la base de datos y la descarga en el ordenador del usuario.
- [ ] **Exportación de Medios**: Opcional: descargar también la carpeta de `uploads` (logos, documentos de alumnos).
- [ ] **Historial de Backups**: Registro de cuándo fue la última vez que se guardaron los datos.

## 4. Gestión Multiusuario y Roles (Complejidad Alta)
**Objetivo**: Permitir que más personas (profesores, secretaría) usen el sistema con permisos limitados.
- [ ] **Panel de Usuarios**: Vista para crear, editar y dar de baja usuarios.
- [ ] **Sistema de Roles**: 
    - `Admin`: Acceso total.
    - `Instructor`: Solo ve calendario, alumnos y asistencias.
    - `Secretaría`: Gestión de alumnos y pagos, pero no configuración del sistema.
- [ ] **Registro de Actividad**: Log de quién hizo qué cambios (opcional).
- [ ] **Seguridad**: Implementar lógica de permisos (`@role_required`) en cada ruta de `app.py`.

---
*Este documento sirve como guía oficial para las siguientes etapas de desarrollo.*
