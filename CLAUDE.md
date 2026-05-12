# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

DarmaSala — Flask-based management system for a yoga school (students, payments, attendance, weekly schedules, individual yogatherapy sessions, Spanish-compliant invoicing). Single-tenant deployment. UI, code comments, and DB column names are in Spanish; preserve that convention.

## Commands

### Setup & run
```bash
# Install (Python 3.10+ required; experimental 3.14 known-broken for numpy)
python -m venv venv && source venv/bin/activate     # Linux/Mac
.\venv\Scripts\activate                              # Windows
pip install -r requirements.txt

# Initialize database (creates tables, seed config, admin user)
python init_db.py                       # base data only
python init_db.py --test                # base data + demo students/payments/schedule
python init_db.py --reset               # wipe DB, then init
python init_db.py --admin-pass <pw>     # set admin password (default: DarmaSala2025!)

# Run dev server (opens browser on :5001)
python run.py
# Or directly:
python app.py
```

### Production
- **Linux/VPS**: Gunicorn behind Nginx via `systemd` (template in `scripts/darmasala.service`, setup script `scripts/setup_vps.sh`, guide in `docs/deployment-ubuntu.md`). Entry point: `app:app`.
- **Windows**: Waitress via `production_server.py` (threads=4, port 5001). Installable as Windows service via `scripts/install_windows_service.ps1`.
- **Hostinger/shared**: `wsgi.py` exposes `app`. Set `FLASK_ENV=production` and `DATABASE_URL=mysql://...` — `app.py` switches to MySQL only when `FLASK_ENV=production`.

### Tests
There is no pytest suite. The legacy `python test_calendar.py` is referenced in `docs/CALENDAR_SYSTEM.md` but may not exist in the tree — verify before assuming.

### One-off scripts
- `python fix_db.py` — schema repair helper
- `python reset_admin.py` — reset admin credentials
- `python sync_alumnos.py` — sync `Alumno` ↔ portal `Usuario` (rol='alumno') accounts
- `python cargar_sutras_produccion.py` — seed weekly sutras shown on login
- `python scripts/migrate_clase_online.py` — one-off migration

## Architecture

### Flask app composition
`app.py` is the composition root. It:
1. Builds the `Flask` app and chooses DB URI based on `FLASK_ENV` (SQLite in dev, MySQL in prod).
2. Calls `db.init_app(app)` from `models.py` (single SQLAlchemy `db` instance, no factory pattern).
3. Imports and registers **ten Blueprints** from `routes/__init__.py`: `main, auth, student, finance, class, yogatherapia, settings, user_routes, student_portal, setup`.
4. Registers a `@before_request` hook that redirects to `/setup` (the onboarding flow) when `Usuario` table is empty — this is how first-run provisioning works. The hook MUST exclude endpoints `setup.onboarding` and `static` or it infinite-loops (see commit `90eed08`).
5. Registers a `@context_processor` injecting four things into **every template**: school config (`Configuracion` key/value rows), calendar helpers, version info, today's date. Templates rely on this — adding a render path that bypasses the context processor will break shared partials.

### Two parallel auth flows
- **Staff** (`routes/auth_routes.py`, blueprint `auth`): username/email + password, `session['rol']` ∈ `{admin, instructor, recepcionista}`. Admin-only actions are gated by `Usuario.is_admin()` / `can_manage_*` helpers on the model.
- **Student portal** (`routes/student_portal_routes.py`, blueprint `student_portal`): same login endpoint, but if `Usuario.rol == 'alumno'` it redirects to `/portal/dashboard` and sets `session['student_id']`. A student has BOTH an `Alumno` row (the domain entity) and a `Usuario` row with `rol='alumno'` (the auth principal), linked by email. `sync_alumnos.py` reconciles them.

Auth is session-based (`session['user_id']`, `session['rol']`). No Flask-Login. Decorators/checks live in `utils/auth_utils.py` and `utils/student_auth.py`.

### Domain model layout
All ~30+ SQLAlchemy models live in a **single file** `models.py` (~37KB). Key entities and relationships:
- `Usuario` — staff and portal-student auth
- `Alumno` — student domain entity; `tipo_cuota` drives pricing and the payment-calendar UI
- `Pago` — monthly payments; `mes` stored as `YYYY-MM` string, `tipo_pago` ∈ {`cuota`, `matricula`, `clase_suelta`, ...}
- `Clase` / `TipoClase` / `Tarifa` — class definitions and pricing
- `HorarioSemanal` + `inscripciones_horarios` (M2M) — weekly recurring schedule
- `Asistencia` — attendance per `(alumno, horario, fecha_clase)`
- `Cliente` / `FacturaEmitida` / `LineaFactura` / `ConfiguracionFiscal` — Spanish invoicing (issued)
- `Proveedor` / `FacturaProveedor` / `CategoriaGasto` / `GastoMensual` / `GastoFijo` — expense side
- `SesionYogaterapia` — individual therapy session records (separate from group attendance)
- `Configuracion` — global key/value store for branding/school settings (read in the context processor every request)

When changing models, also update `init_db.py` (seed data) and the `templates/modo-pruebas` reset flow which enumerates tables to wipe.

### Utilities layer (`utils/`)
- `calendar_utils.py` — **centralized date/period logic**. `CalendarioAcademico`, `PeriodoPago`, `HorarioSemanalHelper`. Do NOT re-implement date math in routes or templates; route everything through here. The context processor exposes its constants (`meses_nombres`, `dias_semana`, etc.) and helpers to every template. Detailed docs in `docs/CALENDAR_SYSTEM.md`.
- `app_utils.py` — `get_version_info()` (reads git), `obtener_sutra_semanal()`.
- `finance_utils.py`, `pdf_generator.py` — invoice math and ReportLab PDF generation (Spanish fiscal: IVA Art. 20.Uno.9º exemption for teaching, IRPF retention at 0/7/15%, sequential numbering by serie/year, format `{SERIE}/{YYYY}/{NNNN}`). See `docs/FACTURACION_SISTEMA.md`.
- `backup.py`, `export.py`, `sync_utils.py`, `validators.py`, `alerts.py` — self-explanatory; check before adding parallel implementations.

### Templates (`templates/`)
- ~60 Jinja2 templates, flat layout with a few subdirs (`alumno/`, `auth/`, `economia/`, `configuracion/`, `components/`, `setup/`).
- `base.html` is the layout; every page extends it and gets `config`, `calendario`, `version_info`, `today` from the context processor.
- `templates/components/payment_calendar.html` exposes `render_payment_calendar(alumno)` — use it instead of re-implementing the monthly/bimonthly pay grid.

### Design system
Two design docs exist and **disagree** — treat `docs/CORE_DESIGN.md` ("Deep Purple & Enchanted Gold") as historical. The current branding is "Moss Green & Sage" (primary `#1E3A2F`, accent `#6B8E7E`, neutral `#D4C9B3`) as seeded by `init_db.py` and used in `Configuracion.color_primario`. Logo: `static/images/logo_darmasala.jpg`. Theme values are configurable via the Configuración section, so prefer reading `config.color_primario` etc. over hardcoding.

## Conventions

- **Language**: All user-facing strings, flash messages, and most identifiers are Spanish. Keep new code consistent (e.g. `alumno` not `student` in DB models; the `Alumno`/`Usuario` split is intentional).
- **Branding**: The app rebranded from "Atma Suddhi" → "DarmaSala" in v2.0.0 (commit `ff7519d`). Don't reintroduce the old name. The `.env.example` still contains a stale "atma-suddhi" SECRET_KEY default — override via env var.
- **DB sessions**: Routes commit via `db.session.commit()` directly and `rollback()` on exception — no service layer. Follow the same pattern in new routes.
- **First-run gate**: Any new top-level route should be reachable without an authenticated user only if it's `/setup`, `/login`, or `/static/...` — the onboarding redirect in `app.py` runs before every request.
- **No migrations framework wired up**: `Flask-Migrate` is in `requirements.txt` but there's no `migrations/` directory. Schema changes today rely on `db.create_all()` (additive) + ad-hoc scripts in `scripts/` (e.g. `migrate_clase_online.py`). For destructive schema changes, write a one-off script and document it.
