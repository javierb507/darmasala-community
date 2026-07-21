# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

DarmaSala — Flask-based management system for a yoga school (students, payments, attendance, weekly schedules, individual yogatherapy sessions, Spanish-compliant invoicing). Single-tenant deployment. UI, code comments, and DB column names are in Spanish; preserve that convention.

### Editions

This repo is the **Community Edition**: intended for local installation in a single school, no public exposure, no student-facing portal. The student portal, PWA, online reservations, and password reset flows live in the private Enterprise fork only.

- `DARMASALA_EDITION=community` (default) — what this repo ships
- `DARMASALA_EDITION=enterprise` — set in the private fork
- The flag is read in `app.py` and exposed to templates as `edition` for the badge in `base.html`

When working on this repo, **do not reintroduce portal endpoints** (`/portal/*`), the `alumno` `Usuario.rol`, or PWA assets. Those belong in the Enterprise fork. If you find yourself needing them, the change goes in the Enterprise repo, not here.

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
```bash
./venv_mac/bin/python -m pytest tests/ -v        # toda la suite
./venv_mac/bin/python -m pytest tests/test_pagos.py -v   # un fichero
```
La suite usa una BD SQLite temporal (`DATABASE_URL` se fija en `tests/conftest.py` antes de importar `app`); nunca toca `instance/yoga_school.db`. Cobertura actual: pagos, facturación, asistencia por lotes, morosidad, bajas, informes, humo de login. `docs/CALENDAR_SYSTEM.md` references a `test_calendar.py` that does not exist.

### One-off scripts
- `python reset_admin.py` — reset admin credentials
- `python cargar_sutras_produccion.py` — seed weekly sutras shown on login
- `python cargar_datos_prueba_completos.py` — full demo dataset for "modo pruebas" (see `docs/MODO_PRUEBAS.md`)
- `python scripts/migrate_clase_online.py` — one-off migration

## Architecture

### Flask app composition
`app.py` is the composition root. It:
1. Builds the `Flask` app and chooses DB URI based on `FLASK_ENV` (SQLite in dev at `instance/yoga_school.db`, MySQL via `DATABASE_URL` in prod). Note: all configuration is inline in `app.py`; there is no separate config module.
2. Calls `db.init_app(app)` from `models.py` (single SQLAlchemy `db` instance, no factory pattern).
3. Imports and registers **ten Blueprints** from `routes/__init__.py`: `main, auth, student, finance, class, yogatherapia, settings, user_routes, setup, bug_report`. (No student portal in Community Edition.)
4. Registers a `@before_request` hook that redirects to `/setup` (the onboarding flow) when `Usuario` table is empty — this is how first-run provisioning works. The hook MUST exclude endpoints `setup.onboarding` and `static` or it infinite-loops (see commit `90eed08`).
5. Registers a `@context_processor` injecting four things into **every template**: school config (`Configuracion` key/value rows), calendar helpers, version info, today's date. Templates rely on this — adding a render path that bypasses the context processor will break shared partials.

### Auth flow
- **Staff only** (`routes/auth_routes.py`, blueprint `auth`): username/email + password, `session['rol']` ∈ `{admin, instructor, recepcionista}`. Admin-only actions are gated by `Usuario.is_admin()` / `can_manage_*` helpers on the model.

Auth is session-based (`session['user_id']`, `session['rol']`). No Flask-Login. Decorators/checks live in `utils/auth_utils.py`.

### Domain model layout
All ~30+ SQLAlchemy models live in a **single file** `models.py` (~37KB). Key entities and relationships:
- `Usuario` — staff auth (admin/instructor/recepcionista)
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
- `github_issues.py` — minimal GitHub Issues API client used by `routes/bug_report_routes.py` to file issues from in-app bug reports (see `docs/BUG_REPORTING.md`).
- `validators.py` — input validation helpers; check before adding parallel implementations.

### Templates (`templates/`)
- ~60 Jinja2 templates, flat layout with a few subdirs (`alumno/`, `auth/`, `economia/`, `configuracion/`, `components/`, `setup/`).
- `base.html` is the layout; every page extends it and gets `config`, `calendario`, `version_info`, `today` from the context processor.
- `templates/components/payment_calendar.html` exposes `render_payment_calendar(alumno)` — use it instead of re-implementing the monthly/bimonthly pay grid.

### Design system
Two design docs exist and **disagree** — treat `docs/CORE_DESIGN.md` ("Deep Purple & Enchanted Gold") as historical. The current branding is "Moss Green & Sage" (primary `#1E3A2F`, accent `#6B8E7E`, neutral `#D4C9B3`) as seeded by `init_db.py` and used in `Configuracion.color_primario`. Logo: `static/images/logo_darmasala.jpg`. Theme values are configurable via the Configuración section, so prefer reading `config.color_primario` etc. over hardcoding.

## Conventions

- **Language**: All user-facing strings, flash messages, and most identifiers are Spanish. Keep new code consistent (e.g. `alumno` not `student` in DB models; the `Alumno`/`Usuario` split is intentional).
- **Branding**: The app rebranded from "Atma Suddhi" → "DarmaSala" in v2.0.0 (commit `ff7519d`). Don't reintroduce the old name.
- **SECRET_KEY**: `app.py` refuses to start with `FLASK_ENV=production` unless the `SECRET_KEY` env var is set; dev falls back to a hardcoded dev-only key.
- **DB sessions**: Routes commit via `db.session.commit()` directly and `rollback()` on exception — no service layer. Follow the same pattern in new routes.
- **First-run gate**: Any new top-level route should be reachable without an authenticated user only if it's `/setup`, `/login`, or `/static/...` — the onboarding redirect in `app.py` runs before every request.
- **Docs live in `docs/`**: `documentation/` is legacy (old Windows deploy guide + `legacy/` archive) — put new docs in `docs/`.
- **Migrations**: Flask-Migrate is wired in `app.py` (`migrations/` holds the baseline). New schema change = `flask db migrate -m "..."` + review + `flask db upgrade`. `init_db.py` creates the schema via `db.create_all()` and stamps the DB automatically; only installs that predate migrations must run `FLASK_APP=app.py flask db stamp head` once by hand.
