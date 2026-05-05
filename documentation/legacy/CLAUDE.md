# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sistema de Gestión DarmaSala - A lightweight web-based management system for yoga schools built with Flask and SQLite. The system manages students (alumnos), payments (pagos), classes, schedules, attendance, and financial operations including suppliers and invoices.

## Common Commands

### Running the Application
```bash
python app.py
```
The app runs on http://localhost:5000 with debug mode enabled.

### Database Setup
The database is automatically created when running the app for the first time. The `app.py` initialization (lines 989-995) performs:
1. `db.create_all()` - Creates all tables
2. `inicializar_clases()` - Seeds 4 default yoga class types
3. `inicializar_categorias_gastos()` - Seeds 8 default expense categories
4. `crear_datos_prueba()` - Creates 10 test students (only if database is empty)

### Installing Dependencies
```bash
pip install -r requirements.txt
```
Dependencies: Flask 2.3.3, Flask-SQLAlchemy 3.0.5, Flask-Migrate 4.0.5, python-dateutil 2.8.2

## Architecture & Data Model

### Core Models (SQLAlchemy)

**Alumno (Student)** - Main entity with fields:
- Personal info: nombre, apellido, email, telefono, fecha_nacimiento, direccion
- Medical: condiciones_medicas
- Payment: tipo_cuota (subscription type), matricula_pagada (enrollment paid), activo (active status)
- Subscription types: clase_suelta, 1_clase_semanal, 2_clases_semanal, plana (unlimited), 1_clase_bimensual, 2_clases_bimensual
- Relationships: One-to-many with Pago and Asistencia

**Pago (Payment)** - Tracks student payments:
- Links to Alumno via alumno_id
- tipo_pago: 'cuota' (monthly), 'matricula' (enrollment), 'clase_suelta' (single class)
- For monthly payments: stores mes (YYYY-MM format)
- For enrollment: stores año (year)

**Clase (Class)** - Yoga class types (4 predefined):
- Yoga menopausia, Yoga integral, Yoga embarazadas, Meditación
- Configuration fields:
  - duracion_minutos: Default duration in minutes (default: 75)
  - periodicidad: Frequency (semanal, quincenal, mensual)

**HorarioSemanal (Schedule)** - Weekly class schedule:
- Links to Clase via clase_id
- dia_semana: 0-6 (Monday-Sunday)
- hora_inicio, hora_fin (time fields)
- Default instructor: "Minouche"

**Asistencia (Attendance)** - Attendance records:
- Links to Alumno and HorarioSemanal
- fecha_clase: specific date of class
- presente: boolean for attendance

**Configuracion (Settings)** - Key-value store for app configuration

### Economic Module Models

**Proveedor (Supplier)** - Supplier information:
- nombre, cif_nif, direccion, telefono, email, contacto_principal

**CategoriaGasto (Expense Category)** - 8 predefined categories:
- Alquiler (#dc3545), Suministros (#ffc107), Material (#28a745), Marketing (#007bff), Formación (#6f42c1), Seguros (#fd7e14), Mantenimiento (#20c997), Otros (#6c757d)

**FacturaProveedor (Supplier Invoice)**:
- Links to Proveedor and CategoriaGasto
- estado: pendiente, pagada, vencida
- importe_sin_iva, iva (default 21%), importe_total
- Methods: calcular_total(), esta_vencida()

**GastoFijo (Fixed Expense)** - Recurring expenses:
- frecuencia: mensual, trimestral, anual
- dia_cargo: day of month for charge

**Ingreso (Income)** - Income records:
- tipo: cuota, matricula, clase_suelta, otros
- Can link to Alumno via alumno_id

## Route Structure

### Student Management
- `/alumnos` - List active students
- `/alumnos/desactivados` - List deactivated students
- `/alumnos/nuevo` - Create new student
- `/alumnos/<id>` - View student details with payment history
- `/alumnos/<id>/editar` - Edit student
- `/alumnos/<id>/eliminar` - Deactivate student (sets activo=False)
- `/alumnos/<id>/reactivar` - Reactivate student (POST only)
- `/alumnos/<id>/pago` - Add payment for student

### Class & Schedule Management
- `/clases` - List classes
- `/horarios` - List weekly schedules
- `/horarios/nuevo` - Create new schedule

### Attendance
- `/asistencias` - View attendance records
- `/asistencias/registrar` - Register attendance
- `/reportes/asistencia` - Attendance reports with filters

### Economic Module
- `/economia` - Economic dashboard with monthly summary
- `/economia/proveedores` - List suppliers
- `/economia/proveedores/nuevo` - Create supplier
- `/economia/facturas` - List invoices (placeholder)
- `/economia/facturas/nueva` - Create invoice (placeholder)
- `/economia/gastos-fijos` - List fixed expenses (placeholder)
- `/economia/gastos-fijos/nuevo` - Create fixed expense (placeholder)
- `/economia/export/<tipo>` - Export data to CSV (facturas, gastos, ingresos)

### Configuration & API
- `/configuracion` - View settings
- `/configuracion/guardar` - Save settings (POST)
- `/api/alumnos` - JSON API for students list

## Payment System Logic

### Subscription Pricing (get_precio_cuota method):
- clase_suelta: 15€
- 1_clase_semanal: 40€/month
- 2_clases_semanal: 70€/month
- plana (unlimited): 90€/month
- 1_clase_bimensual: 75€ (every 2 months)
- 2_clases_bimensual: 135€ (every 2 months)
- Matrícula anual: 25€

### Payment Display in Student View:
- Monthly subscriptions show individual months
- Bimonthly subscriptions show combined periods (Ene/Feb, Mar/Abr, etc.)
- Visual indicators: Green checkmark (✅) for paid, Red X (❌) for pending
- Current academic year format: "25/26"

## Template Organization

Templates are in `/templates/`:
- Base template: `base.html` (Bootstrap 5 navbar, purple/yellow DarmaSala theme)
- Student templates: `alumnos.html`, `nuevo_alumno.html`, `ver_alumno.html`, `editar_alumno.html`, `alumnos_desactivados.html`
- Payment: `agregar_pago.html`
- Classes/Schedule: `horarios.html`, `calendario_horarios.html`
- Attendance: `asistencias.html`, `registrar_asistencia.html`, `reporte_asistencia.html`
- Economic module: `economia/dashboard.html`, `economia/proveedores.html`
- Other: `index.html`, `configuracion.html`

## Centralized Calendar System

**IMPORTANT**: The project now has a centralized calendar system in `utils/calendar_utils.py`.

### When Working with Dates/Calendars:

**DO**:
- Use `CalendarioAcademico` for date operations
- Use `HorarioSemanalHelper` for schedule operations
- Use `render_payment_calendar()` component in templates
- Leverage context processor (calendario, current_year, formatear_fecha, etc.)

**DON'T**:
- Write date logic directly in templates
- Manually calculate periods or format dates
- Repeat calendar logic across files

### Quick Reference:

```python
# In routes (app.py)
from utils.calendar_utils import CalendarioAcademico, HorarioSemanalHelper

# Get week range
inicio, fin = CalendarioAcademico.get_rango_semana()

# Parse dates
fecha = CalendarioAcademico.parsear_fecha(request.form['fecha'], 'iso')

# Calculate end time
hora_fin = CalendarioAcademico.calcular_hora_fin(hora_inicio, 75)
```

```jinja2
{# In templates #}
{% from "components/payment_calendar.html" import render_payment_calendar %}
{{ render_payment_calendar(alumno) }}

{# Available globally #}
{{ current_year }}, {{ current_month }}
{{ formatear_fecha(fecha, 'corto') }}
{{ formatear_horario(hora_inicio, hora_fin) }}
{{ calendario.get_año_academico_formato() }}
```

See `docs/CALENDAR_SYSTEM.md` for complete documentation.

## Key Patterns & Conventions

### Database Sessions:
- Use `db.session.add()` for new records
- Always commit with `db.session.commit()`
- Wrap in try/except with `db.session.rollback()` on error

### Flash Messages:
- Use `flash('message', 'category')` for user feedback
- Categories: 'success', 'danger', 'warning', 'info'
- Messages are in Spanish

### Academic Year Format:
- Matrícula displayed as "25/26" for 2025-2026 academic year
- Uses current year and next year (e.g., año % 100 and (año + 1) % 100)

### Test Data:
- 10 test students auto-created on first run with random data
- Random subscription types and payment statuses
- Student emails: alumno1@test.com through alumno10@test.com

## Language & Branding

- **Language**: All UI, database fields, and code comments are in Spanish
- **School Name**: DarmaSala
- **Website**: atmasuddhi.es (linked in navigation)
- **Theme Colors**: Purple and yellow matching school branding
- **Default Instructor**: "Minouche"

## Known Issues & Roadmap

See ROADMAP.md for detailed future improvements. Critical current issues:
1. Student reactivation functionality needs fixes (app.py:411-423)
2. Invoice and supplier forms are placeholders - need full implementation
3. Fixed expenses management incomplete
4. No authentication/user system yet
5. Economic dashboard graphs not implemented

## Database File

- SQLite database: `yoga_school.db` (created automatically)
- Located in project root directory
- Contains all production data - backup regularly
