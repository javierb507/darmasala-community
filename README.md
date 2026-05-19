<p align="center">
  <img src="static/images/logo_darmasala.jpg" alt="DarmaSala Logo" width="300">
</p>

<p align="center">
  <a href="https://darmasala.cloud"><strong>☁️ Versión gestionada en la nube → darmasala.cloud</strong></a>
</p>

# DarmaSala — Community Edition

Sistema de gestión de código abierto para escuelas de yoga: alumnos, pagos, asistencia, horarios semanales, yogaterapia individual, calendario unificado y facturación española.

**Licencia:** GNU AGPL v3  
**Versión:** 2.0.0-community

---

## ¿Community o Enterprise?

| | Community (este repo) | Enterprise / Cloud |
|---|---|---|
| Distribución | Pública, AGPL-3 | [darmasala.cloud](https://darmasala.cloud) |
| Despliegue | Local (PC, intranet) | Gestionado en la nube |
| Gestión administrativa completa | ✅ | ✅ |
| Facturación española (IVA, IRPF) | ✅ | ✅ |
| Yogaterapia individual | ✅ | ✅ |
| Calendario unificado | ✅ | ✅ |
| Portal de alumnos | ❌ | ✅ |
| Reservas y pagos online | ❌ | ✅ |
| PWA / app móvil | ❌ | ✅ |
| Notificaciones por email | ❌ | ✅ |
| Lista de espera | ❌ | ✅ |
| Soporte y actualizaciones | Comunidad | Incluido |

> **¿Quieres todo sin instalar nada?** Visita [darmasala.cloud](https://darmasala.cloud) para la versión gestionada.

---

## Características

### Alumnos
- Ficha completa: datos personales, contacto, tipo de cuota
- Historial de pagos y asistencia por alumno
- Cuotas mensuales, bonos y clases sueltas
- Seguimiento de pagos pendientes

### Calendario y Horarios
- Vista mensual, semanal y anual con mini-calendarios
- Horarios semanales recurrentes con tipos de clase y precios
- Pase de lista visual desde cualquier clase
- Gestión de instructores y aforo

### Economía
- Dashboard de ingresos, gastos y balance mensual/anual
- Gastos fijos, variables y por categoría
- Gestión de proveedores
- Exportación de datos

### Facturación española
- Facturas emitidas con numeración secuencial (`{SERIE}/{AÑO}/{NNNN}`)
- IVA con exención Art. 20.Uno.9º (enseñanza)
- Retención IRPF configurable (0 / 7 / 15 %)
- Facturas de proveedor recibidas
- Generación de PDF con ReportLab

### Yogaterapia Individual
- Citas individuales con sesiones terapéuticas detalladas
- Subida de archivos de práctica personal
- Seguimiento de objetivos y evaluaciones

### Administración
- Usuarios staff con roles: `admin`, `instructor`, `recepcionista`
- Configuración de branding (nombre, logo, colores)
- Timeout de sesión configurable
- Reportar bugs directamente a GitHub desde la app

---

## Instalación

```bash
# Requisitos: Python 3.10+ (3.14 no compatible con numpy)
python -m venv venv && source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate                           # Windows

pip install -r requirements.txt

# Inicializar base de datos
python init_db.py              # datos base + usuario admin
python init_db.py --test       # + alumnos y pagos de demo
python init_db.py --reset      # borrar y reinicializar

# Arrancar servidor de desarrollo (puerto 5001)
python run.py
```

Credenciales por defecto: `admin` / `DarmaSala2025!`

### Producción

| Plataforma | Método |
|---|---|
| Linux VPS | Gunicorn + Nginx + systemd (`scripts/setup_vps.sh`, guía en `docs/deployment-ubuntu.md`) |
| Windows | Waitress vía `production_server.py` |
| Hostinger / shared hosting | `wsgi.py` + `DATABASE_URL=mysql://...` |

---

## 🌿 Inspiración

> "El éxito del yoga no radica en la capacidad de realizar posturas, sino en cómo cambia positivamente nuestra forma de vivir la vida y nuestras relaciones."  
> — *T.K.V. Desikachar*

---

## Licencia

DarmaSala Community Edition se distribuye bajo la **GNU Affero General Public License v3.0** ([LICENSE](LICENSE)).

La licencia AGPL exige que cualquier servicio público derivado de este código publique sus modificaciones bajo la misma licencia. Para la versión gestionada en la nube sin restricciones AGPL, visita [darmasala.cloud](https://darmasala.cloud).

## Contribución

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit y push
4. Abre un Pull Request

## Contacto

- **Soporte cloud y Enterprise:** [darmasala.cloud](https://darmasala.cloud)
- **Autor:** Javier Ballesteros — javierb507@gmail.com
