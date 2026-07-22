# Copias de seguridad (backups)

Guía del sistema de backups de DarmaSala: qué incluye, cómo crearlos, dónde guardarlos y cómo restaurarlos.

## Qué incluye un backup

Cada backup es un archivo ZIP llamado `backup_darmasala_YYYYMMDD_HHMMSS.zip` que contiene:

| Contenido | Descripción |
|---|---|
| `yoga_school.db` | La base de datos SQLite completa: alumnos, pagos, asistencias, facturas, horarios, configuración… |
| `uploads/` | Los adjuntos: informes de yogaterapia y logo personalizado |
| `meta.json` | Metadatos: fecha de creación, revisión de migraciones (alembic) y versión de la aplicación |

Los backups se guardan en el directorio `backups/` de la instalación.

> Las versiones antiguas creaban backups como un fichero `.db` suelto. Siguen siendo válidos para restaurar, pero no incluyen los adjuntos.

## Crear un backup

1. Entra en **Configuración** y baja hasta la sección **Copias de seguridad**.
2. Pulsa **Crear backup**.
3. El nuevo archivo aparece en la lista con su fecha y tamaño.

## Descargar y guardar fuera del equipo

Un backup que vive en el mismo disco que la aplicación no protege contra el fallo de ese disco. Después de crearlo:

1. Pulsa el botón de **descarga** junto al backup en la lista.
2. Guarda el ZIP en al menos un sitio externo: otro ordenador, un disco USB o almacenamiento en la nube (Drive, Dropbox…).

## Restaurar un backup

**La restauración reemplaza la base de datos actual.** Antes de sobrescribir nada, la aplicación guarda automáticamente una copia del estado actual en `backups/` (`yoga_school_backup_before_restore_*.db`), así que siempre puedes volver atrás.

### En la misma instalación

1. En **Configuración → Copias de seguridad**, selecciona el archivo (`.zip` o `.db` antiguo) en el formulario de restauración.
2. Pulsa **Restaurar** y confirma.
3. La base de datos del ZIP reemplaza a la actual. Los adjuntos del ZIP se escriben sobre los actuales (los archivos añadidos después del backup **no se borran**; si quieres una restauración exacta, vacía `uploads/` antes de restaurar).

### En una instalación nueva (migrar de equipo o recuperar tras un desastre)

1. Instala DarmaSala en el equipo nuevo siguiendo el README (`pip install -r requirements.txt`, `python init_db.py`).
2. Arranca la aplicación y completa el asistente inicial si aparece (los datos que introduzcas serán reemplazados por el backup).
3. Entra con cualquier usuario administrador y ve a **Configuración → Copias de seguridad**.
4. Restaura el ZIP. Los usuarios y contraseñas pasan a ser los del backup, no los de la instalación nueva.
5. Si la versión de la aplicación es más nueva que la del backup, aplica las migraciones pendientes:
   ```bash
   FLASK_APP=app.py flask db upgrade
   ```

## Instalación manual vs Docker

- **Instalación manual**: los datos viven en `instance/yoga_school.db` y `uploads/` dentro del directorio de la aplicación. El flujo de esta guía cubre todo.
- **Docker**: los datos viven en los volúmenes montados `./data/instance` y `./data/uploads` del host. Puedes usar los backups desde Configuración igualmente, y además tienes una alternativa simple: con el contenedor parado (`docker compose down`), copiar la carpeta `./data` completa a un lugar seguro también es un backup válido. Para restaurarlo, vuelca la carpeta y levanta el contenedor.

## Nota para MySQL

Los backups integrados solo funcionan con SQLite (la instalación por defecto). Si tu despliegue usa MySQL (`FLASK_ENV=production` + `DATABASE_URL=mysql://...`), haz el backup con las herramientas de MySQL:

```bash
# Base de datos
mysqldump -u usuario -p nombre_bd > backup_darmasala_$(date +%Y%m%d).sql

# Adjuntos
tar czf uploads_$(date +%Y%m%d).tar.gz uploads/
```

Y para restaurar:

```bash
mysql -u usuario -p nombre_bd < backup_darmasala_YYYYMMDD.sql
tar xzf uploads_YYYYMMDD.tar.gz
```

## Frecuencia recomendada

- **Semanal** como mínimo, idealmente el mismo día a la misma hora para crear el hábito.
- **Antes de actualizar** la aplicación a una versión nueva.
- **Antes de operaciones masivas** (importaciones, borrados en Modo Pruebas…).
- Conserva al menos las últimas 4 copias y borra las más antiguas desde la propia lista para no acumular espacio.
