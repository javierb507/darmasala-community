# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y este proyecto sigue [SemVer](https://semver.org/lang/es/) en la medida en que tiene sentido para una app monolito.

## [Unreleased]

### Added
- **Reporte de bugs in-app que crea issues de GitHub automáticamente.**
  Botón flotante "Reportar bug" abajo a la derecha visible para
  admins logueados cuando `bug_report_enabled = true`. Modal con
  título / descripción / "qué estabas haciendo" que dispara
  `POST /admin/bug-report/submit`. El servidor adjunta contexto
  técnico (URL, versión, commit, rama, user-agent, usuario, timestamp
  UTC) y crea el issue vía la API REST de GitHub. Token leído solo
  de `GITHUB_ISSUE_TOKEN`. Etiquetas configurables. Rate limit de
  5 reportes por hora y por sesión. Guía completa en
  `docs/BUG_REPORTING.md`.

## [2.0.1-final] — 2026-05-12

### Added
- **PWA en el portal de alumnos.** Manifest dinámico (`/portal/manifest.webmanifest`),
  service worker (`/portal/sw.js`) con scope `/portal/`, iconos PNG generados al
  vuelo desde el logo de la escuela (192/512 estándar y *maskable*). Botón
  "Instalar app" visible cuando dispara `beforeinstallprompt` y modal de
  instrucciones manuales para iOS Safari y otros navegadores sin prompt.
- **Configuración de dominio del portal.** Nueva clave `dominio_portal` en
  Configuración → "Datos de la escuela". El manifest la usa como `start_url`
  y `scope` para que la app instalada apunte al dominio público correcto.
- **Set de datos de prueba completo** (`cargar_datos_prueba_completos.py`):
  10 alumnos con usuarios de portal, 16 horarios Lun-Vie, ~450 asistencias
  de 4 semanas, pagos multi-mes, 5 clientes, 12 facturas emitidas con líneas,
  5 proveedores, 20 facturas de proveedores, 3 gastos fijos, 2 clases online.
  Idempotente: re-ejecutable sin duplicar.
- **Script de despliegue VPS end-to-end** (`scripts/setup_vps.sh`): instala
  apt deps, crea venv, instala requirements, prepara `instance/` y `uploads/`
  con permisos correctos, inicializa DB si falta, genera unit systemd con
  `SECRET_KEY` aleatoria + `DATABASE_URL` apuntando a SQLite, habilita y
  arranca el servicio. Idempotente.
- **CLAUDE.md**: guía del repositorio para futuras sesiones de Claude Code
  (arquitectura, comandos, convenciones, gotchas).
- Badge discreto de versión + buildstamp en la parte superior del portal
  de alumnos (igual al panel admin).

### Fixed
- **Modal de clases grabadas se congelaba en el portal.** Se renderizaba
  dentro de `.student-container` (`z-index: 1`) creando un stacking context
  local; el backdrop de Bootstrap (z-index 1050) tapaba el modal entero
  haciendo imposible cerrarlo o pulsar nada. Ahora se reparenta a `<body>`
  al cargar para compartir contexto raíz con el backdrop.
- **Reproductor de vídeo integrado.** En vez de mostrar el iframe pelado
  (que en vídeos con embed restringido sólo permite "Ver en YouTube"),
  se muestra el thumbnail con un play custom; al pulsar se carga el iframe
  con `autoplay=1` desde `youtube-nocookie.com` + `modestbranding`. Botón
  fallback "Abrir en YouTube" visible siempre por si el embed falla.
- **"Modo Pruebas" cargaba datos**. La ruta importaba un módulo
  inexistente (`cargar_datos_prueba_completos`); ahora existe de verdad
  y la ruta lo usa, mostrando resumen en flash.
- **Permisos SQLite en producción.** El servicio fallaba con *readonly
  database* tras un despliegue limpio: `instance/` no existía o pertenecía
  a otro usuario. `setup_vps.sh` ahora crea el directorio con el owner
  correcto y mueve cualquier DB que esté en la raíz del proyecto.
- **MySQLdb ausente bloqueaba el arranque en producción.** El default de
  `app.py` con `FLASK_ENV=production` apuntaba a una URI MySQL aunque no
  hay MySQL en el deploy típico. El unit systemd ahora inyecta
  `DATABASE_URL=sqlite:////…/instance/yoga_school.db`.
- **Loader fallaba si la BD tenía un alumno preexistente con el mismo
  DNI** (caso de instancias que habían cargado datos vía la ruta vieja).
  Ahora deduplica por email *y* DNI; reutiliza el alumno existente.
- **Tildes en emails generados**: ahora se quitan (`ana.garcia@…`) para
  evitar problemas en URLs/forms.
- **Bucle infinito en `/setup`** y conjunto completo de claves de
  branding al onboardear (fixes ya en `2.0.0-final`, mencionados aquí
  para referencia tras la promoción a `2.0.1-final`).
- **`body::before` interceptaba clicks** en el portal cuando se intentaba
  pulsar fuera del modal en algunas vistas: ahora tiene `pointer-events:
  none`.
- **`version.json` filtraba el token PAT de GitHub** en el campo
  `remote_url` cuando el remoto tenía credenciales embebidas. Se redactan
  antes de serializar.

### Changed
- **Calendario del portal adaptativo en móvil.** Por debajo de 768px se
  abre en `listWeek` (agenda legible) con toggle a vista de día; toolbar
  simplificado, fuentes reducidas, stat-bar apilado. Desktop mantiene
  `timeGridWeek`. Se recalcula al rotar/cambiar tamaño.
- **Botón "Instalar" siempre visible en móvil**, fuera del menú
  colapsable. Botón "i" siempre presente abre el modal de instrucciones
  manuales aunque el navegador no soporte `beforeinstallprompt`.

### Security
- Token de GitHub embebido en `remote_url` ya no se guarda en
  `static/version.json`. Si tu instalación ya tenía un `version.json`
  con el token, regenéralo (`python version_info.py`) tras actualizar.

## [2.0.0-final] — 2026-05-05

### Added
- Flujo de onboarding (`/setup`) para primera instalación.
- Rebranding completo "Atma Suddhi" → "DarmaSala".
- Logo nuevo integrado en README y plantillas.
- Configuración por defecto endurecida en `config.py`.
- Scripts de despliegue VPS iniciales + sección en README.

### Fixed
- Bucle infinito de redirecciones en `/setup` cuando ya había usuario.
- Todas las claves de branding se siembran durante el onboarding.

[2.0.1-final]: https://github.com/javierb507/darmasala-community/releases/tag/v2.0.1-final
[2.0.0-final]: https://github.com/javierb507/darmasala-community/releases/tag/v2.0.0-final
