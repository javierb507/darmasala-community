<p align="center">
  <img src="static/images/logo_darmasala.jpg" alt="DarmaSala Logo" width="200">
</p>

<h1 align="center">DarmaSala — Community Edition</h1>

<p align="center">
  Open-source management system for yoga schools · Sistema de gestión de código abierto para escuelas de yoga
</p>

<p align="center">
  <a href="https://github.com/javierb507/darmasala-community/actions/workflows/tests.yml"><img src="https://github.com/javierb507/darmasala-community/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
  <a href="https://github.com/javierb507/darmasala-community/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-AGPL--3.0-green" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/flask-3.x-lightgrey" alt="Flask">
  <a href="https://darmasala.cloud"><img src="https://img.shields.io/badge/cloud-darmasala.cloud-brightgreen" alt="Cloud"></a>
</p>

---

## En memoria · In memoriam

> A **Santiago Cogolludo**, mi profesor.
> Me abrió la puerta del yoga y caminó a mi lado siempre que lo necesité.
> Lo que él sembró vive en cada página de este proyecto.
> Om shanti. 🙏
>
> *To **Santiago Cogolludo**, my teacher.
> He opened the door of yoga for me and walked beside me whenever I needed him.
> What he planted lives on in every page of this project.
> Om shanti.*

---

## Screenshots

<table>
  <tr>
    <td align="center"><img src="docs/screenshots/01-dashboard.png" width="380" alt="Dashboard"/><br><sub>Dashboard</sub></td>
    <td align="center"><img src="docs/screenshots/02-alumnos.png" width="380" alt="Gestión de Alumnos"/><br><sub>Student management / Gestión de alumnos</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/03-horarios.png" width="380" alt="Horarios Semanales"/><br><sub>Weekly schedule / Horarios semanales</sub></td>
    <td align="center"><img src="docs/screenshots/04-economia.png" width="380" alt="Economía y Fiscalidad"/><br><sub>Finance dashboard / Panel de economía</sub></td>
  </tr>
  <tr>
    <td align="center" colspan="2"><img src="docs/screenshots/05-alumno.png" width="380" alt="Ficha de Alumno"/><br><sub>Student profile / Ficha de alumno</sub></td>
  </tr>
</table>

---

## English

### What is DarmaSala?

DarmaSala is a self-hosted management system for yoga schools — built for the front desk, not the cloud. It runs on your own computer or local server, keeps student data on your premises, and has no subscription fees.

### Features

| Module | Description |
|--------|-------------|
| **Students** | Full profiles, payment history, quotas (monthly, drop-in, bonos) |
| **Schedule** | Weekly recurring classes, attendance tracking, instructor management |
| **Finance** | Income/expense dashboard, fixed costs, supplier invoices |
| **Spanish invoicing** | Sequential numbering, VAT exemption (Art. 20.Uno.9º), IRPF withholding, PDF generation |
| **Yogatherapy** | Individual therapy session records, file uploads, goal tracking |
| **Staff** | Admin / instructor / receptionist roles |
| **Settings** | Branding (name, logo, colors), session timeout, bug reporting to GitHub |

### Community vs Enterprise

| | Community (this repo) | Enterprise / Cloud |
|---|---|---|
| Distribution | Public, AGPL-3 | [darmasala.cloud](https://darmasala.cloud) |
| Deployment | Self-hosted (PC, intranet) | Managed cloud |
| Full admin panel | ✅ | ✅ |
| Spanish invoicing (IVA, IRPF) | ✅ | ✅ |
| Yogatherapy sessions | ✅ | ✅ |
| Student portal (online bookings) | ❌ | ✅ |
| Email notifications | ❌ | ✅ |
| Mobile PWA | ❌ | ✅ |
| Support & updates | Community | Included |

### Quick Start (Docker)

```bash
git clone https://github.com/javierb507/darmasala-community.git
cd darmasala-community
docker compose up -d
```

Open http://localhost:5001 — default login: `admin` / `DarmaSala2025!`. Data persists in `./data/`. To start with demo data, uncomment `INIT_DB_ARGS=--test` in `docker-compose.yml` before the first run.

### Quick Start (manual)

**Requirements:** Python 3.10 – 3.14

```bash
git clone https://github.com/javierb507/darmasala-community.git
cd darmasala-community

python -m venv venv
source venv/bin/activate    # Linux/Mac
.\venv\Scripts\activate     # Windows

pip install -r requirements.txt

# Initialize with demo data
python init_db.py --test

# Start development server (port 5001)
python run.py
```

Open http://localhost:5001 — default login: `admin` / `DarmaSala2025!`

**Change the admin password immediately after first login.**

### Production Deployment

| Platform | Method |
|---|---|
| Linux VPS | Gunicorn + Nginx + systemd — see `scripts/setup_vps.sh` and `docs/deployment-ubuntu.md` |
| Windows | Waitress via `production_server.py` |
| Shared hosting | `wsgi.py` entrypoint + `DATABASE_URL=mysql://...` |

Set these environment variables before running in production:

```bash
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export FLASK_ENV=production
export DATABASE_URL=mysql://user:pass@host/dbname
```

See [SECURITY.md](SECURITY.md) for the full list of required variables.

---

## Español

### ¿Qué es DarmaSala?

DarmaSala es un sistema de gestión autoalojado para escuelas de yoga — diseñado para la recepción, no para la nube. Funciona en tu propio ordenador o servidor local, mantiene los datos de los alumnos en tus instalaciones y no tiene cuotas mensuales.

### Características

| Módulo | Descripción |
|--------|-------------|
| **Alumnos** | Fichas completas, historial de pagos, cuotas (mensual, sueltas, bonos) |
| **Horarios** | Clases semanales recurrentes, pase de lista, gestión de instructores |
| **Economía** | Dashboard de ingresos/gastos, gastos fijos, facturas de proveedor |
| **Facturación española** | Numeración secuencial, exención IVA (Art. 20.Uno.9º), retención IRPF, PDF |
| **Yogaterapia** | Sesiones individuales, subida de archivos, seguimiento de objetivos |
| **Usuarios** | Roles admin / instructor / recepcionista |
| **Configuración** | Branding personalizable, timeout de sesión, reporte de bugs a GitHub |

### Instalación rápida (Docker)

```bash
git clone https://github.com/javierb507/darmasala-community.git
cd darmasala-community
docker compose up -d
```

Abre http://localhost:5001 — credenciales: `admin` / `DarmaSala2025!`. Los datos persisten en `./data/`. Para empezar con datos de demostración, descomenta `INIT_DB_ARGS=--test` en `docker-compose.yml` antes del primer arranque.

### Instalación rápida (manual)

**Requisitos:** Python 3.10 – 3.14

```bash
git clone https://github.com/javierb507/darmasala-community.git
cd darmasala-community

python -m venv venv
source venv/bin/activate    # Linux/Mac
.\venv\Scripts\activate     # Windows

pip install -r requirements.txt

# Inicializar con datos de demostración
python init_db.py --test

# Arrancar servidor (puerto 5001)
python run.py
```

Abre http://localhost:5001 — credenciales: `admin` / `DarmaSala2025!`

**Cambia la contraseña de admin inmediatamente tras el primer acceso.**

### Producción

```bash
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export FLASK_ENV=production
export DATABASE_URL=mysql://usuario:pass@host/base_de_datos
```

Ver guía completa: [`docs/deployment-ubuntu.md`](docs/deployment-ubuntu.md) y [`SECURITY.md`](SECURITY.md).

---

## Architecture

Flask · SQLAlchemy · SQLite (dev) / MySQL (prod) · Jinja2 · Bootstrap 5 · ReportLab

- `app.py` — Flask app, Blueprint registration, context processor
- `models.py` — 30+ SQLAlchemy models (single file)
- `routes/` — 10 Blueprints: auth, student, finance, class, yogatherapia, settings, user, setup, bug_report, main
- `utils/` — calendar logic, PDF generation, auth helpers, exports
- `templates/` — ~60 Jinja2 templates extending `base.html`

---

## License / Licencia

[GNU AGPL v3.0](LICENSE) — free to use, modify, and self-host.  
If you distribute a modified version or offer it as a service, you must publish the source under the same license.

> Para una versión gestionada sin restricciones AGPL: [darmasala.cloud](https://darmasala.cloud)

---

## Support / Soporte

- **Community:** [GitHub Issues](https://github.com/javierb507/darmasala-community/issues)
- **Cloud & Enterprise:** [darmasala.cloud](https://darmasala.cloud)
- **Contact / Contacto:** javier.ballesteros@gmail.com

---

> *"El éxito del yoga no radica en la capacidad de realizar posturas, sino en cómo cambia positivamente nuestra forma de vivir la vida y nuestras relaciones."*  
> — T.K.V. Desikachar
