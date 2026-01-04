# Sistema de Calendario Centralizado

## Descripción General

El sistema de calendario centralizado proporciona utilidades reutilizables para el manejo de fechas, períodos de pago y horarios en todo el sistema de gestión Atma suddhi.

## Arquitectura

```
utils/
├── __init__.py
└── calendar_utils.py
    ├── PeriodoPago          # Representa períodos de pago mensuales/bimensuales
    ├── CalendarioAcademico  # Maneja calendario académico y períodos
    ├── HorarioSemanalHelper # Utilidades para horarios semanales
    └── crear_contexto_calendario()  # Crea contexto para templates
```

## Componentes Principales

### 1. CalendarioAcademico

Clase principal para manejo de calendario académico.

#### Métodos principales:

```python
from utils.calendar_utils import CalendarioAcademico

cal = CalendarioAcademico(año=2025)

# Obtener formato académico (ej: "25/26")
formato = cal.get_año_academico_formato()

# Generar períodos mensuales
periodos = cal.generar_periodos_mensuales()  # Retorna 12 PeriodoPago

# Generar períodos bimensuales
periodos_bi = cal.generar_periodos_bimensuales()  # Retorna 6 PeriodoPago

# Generar períodos con estado de pago
periodos = cal.generar_periodos_con_pagos(
    es_bimensual=False,
    pagos=alumno.pagos  # Lista de objetos Pago
)

# Formatear fechas
fecha_str = CalendarioAcademico.formatear_fecha(
    date(2025, 3, 15),
    formato='corto'  # 'corto', 'largo', 'iso'
)

# Parsear fechas
fecha = CalendarioAcademico.parsear_fecha(
    "2025-03-15",
    formato='iso'  # 'iso', 'corto', 'month'
)

# Obtener rango de semana (lunes a domingo)
inicio, fin = CalendarioAcademico.get_rango_semana()

# Calcular hora de finalización
hora_fin = CalendarioAcademico.calcular_hora_fin(
    time(9, 0),
    duracion_minutos=75
)  # Retorna time(10, 15)

# Verificar matrícula vigente
es_vigente = cal.verificar_matricula_vigente(
    fecha_matricula=date(2025, 9, 1)
)
```

### 2. PeriodoPago

Representa un período de pago (mensual o bimensual).

#### Propiedades:

```python
periodo = PeriodoPago(año=2025, mes_inicio=1, mes_fin=2, pagado=True)

# Propiedades de texto
periodo.nombre_corto        # "Ene/Feb"
periodo.nombre_completo     # "Enero/Febrero 2025"

# Propiedades de estilo
periodo.clase_css           # "bg-success" o "bg-danger"
periodo.icono              # "✅" o "❌"
periodo.tooltip            # "✅ Pagado: Enero/Febrero 2025"

# Utilidades
periodo.es_bimensual       # True
periodo.contiene_mes(1)    # True
periodo.contiene_mes(3)    # False
```

### 3. HorarioSemanalHelper

Utilidades para manejo de horarios semanales.

```python
from utils.calendar_utils import HorarioSemanalHelper

# Formatear horario
horario_str = HorarioSemanalHelper.formatear_horario(
    time(9, 0),
    time(10, 15)
)  # "09:00 - 10:15"

# Parsear hora
hora = HorarioSemanalHelper.parsear_hora("14:30")  # time(14, 30)

# Generar horas disponibles
horas = HorarioSemanalHelper.generar_horas_disponibles(8, 22)
# ['08:00', '09:00', ..., '21:00']
```

## Uso en Templates

### Context Processor Global

Todas las utilidades están disponibles automáticamente en todos los templates:

```jinja2
{# Disponible en todos los templates #}
{{ current_year }}          {# Año actual #}
{{ current_month }}         {# Mes actual #}
{{ meses_nombres }}         {# Lista de nombres cortos #}
{{ meses_completos }}       {# Lista de nombres completos #}
{{ dias_semana }}           {# Lista de días de la semana #}

{# Funciones #}
{{ formatear_fecha(alumno.fecha_nacimiento, 'corto') }}
{{ formatear_horario(horario.hora_inicio, horario.hora_fin) }}

{# Objeto calendario #}
{{ calendario.get_año_academico_formato() }}
{{ calendario.verificar_matricula_vigente(alumno.fecha_matricula) }}
```

### Componente de Calendario de Pagos

Componente reutilizable para mostrar el calendario de pagos de un alumno:

```jinja2
{% from "components/payment_calendar.html" import render_payment_calendar %}

{# Renderizar calendario de pagos #}
{{ render_payment_calendar(alumno) }}
```

Este componente:
- Muestra el estado de la matrícula
- Muestra períodos mensuales o bimensuales según el tipo de cuota
- Marca automáticamente los períodos pagados en verde
- Marca los períodos pendientes en rojo
- Incluye tooltips informativos

## Uso en Rutas (app.py)

El context processor hace que las utilidades estén disponibles en todas las rutas:

```python
from utils.calendar_utils import CalendarioAcademico, HorarioSemanalHelper

@app.route('/asistencias')
def asistencias():
    # Usar utilidades de calendario
    inicio_semana, fin_semana = CalendarioAcademico.get_rango_semana()

    asistencias = Asistencia.query.filter(
        Asistencia.fecha_clase >= inicio_semana,
        Asistencia.fecha_clase <= fin_semana
    ).all()

    return render_template('asistencias.html', asistencias=asistencias)

@app.route('/horarios/nuevo', methods=['POST'])
def nuevo_horario():
    hora_inicio_obj = HorarioSemanalHelper.parsear_hora(request.form['hora'])
    hora_fin_obj = CalendarioAcademico.calcular_hora_fin(hora_inicio_obj, 75)

    horario = HorarioSemanal(
        hora_inicio=hora_inicio_obj,
        hora_fin=hora_fin_obj
    )
    # ...
```

## Constantes Disponibles

```python
from utils.calendar_utils import (
    MESES_NOMBRES,           # ['Ene', 'Feb', 'Mar', ...]
    MESES_NOMBRES_COMPLETOS, # ['Enero', 'Febrero', 'Marzo', ...]
    DIAS_SEMANA,            # ['Lunes', 'Martes', 'Miércoles', ...]
    DIAS_SEMANA_CORTOS      # ['Lun', 'Mar', 'Mié', ...]
)
```

## Beneficios del Sistema Centralizado

### Antes:
```jinja2
{# Lógica repetida en múltiples templates #}
{% set meses_nombres = ['Ene', 'Feb', 'Mar', ...] %}
{% for mes in range(1, 13) %}
    {% set mes_str = "%04d-%02d"|format(current_year, mes) %}
    {% set pago_mes = false %}
    {% for pago in alumno.pagos %}
        {% if pago.mes == mes_str and pago.tipo_pago == 'cuota' %}
            {% set pago_mes = true %}
        {% endif %}
    {% endfor %}
    {# ... más lógica compleja ... #}
{% endfor %}
```

### Ahora:
```jinja2
{# Simple y reutilizable #}
{{ render_payment_calendar(alumno) }}
```

## Testing

Ejecutar tests del sistema de calendario:

```bash
python test_calendar.py
```

Los tests verifican:
- ✓ Generación de períodos mensuales y bimensuales
- ✓ Formateo de fechas y horas
- ✓ Cálculos de rangos de fechas
- ✓ Parseo de fechas
- ✓ Integración con objetos Pago
- ✓ Creación del contexto para templates

## Migraciones Realizadas

### Rutas actualizadas:
- `alumnos()` - Usa calendario automáticamente via context processor
- `agregar_pago()` - Removido current_year manual
- `nuevo_horario()` - Usa HorarioSemanalHelper.parsear_hora()
- `asistencias()` - Usa CalendarioAcademico.get_rango_semana()
- `registrar_asistencia()` - Usa CalendarioAcademico.parsear_fecha()

### Templates actualizados:
- `alumnos.html` - Usa componente render_payment_calendar
- `agregar_pago.html` - Usa current_year del contexto global
- `horarios.html` - Usa formatear_horario del contexto global

## Mejoras Futuras

1. **Recordatorios de Pago**: Usar calendario para calcular próximos vencimientos
2. **Reportes Mensuales**: Generar reportes automáticos usando períodos
3. **Validación de Fechas**: Añadir validaciones más robustas
4. **Soporte Multi-idioma**: Internacionalización de nombres de meses/días
5. **Caché**: Cachear cálculos frecuentes de períodos

## Notas de Mantenimiento

- Todas las funcionalidades de calendario deben añadirse en `calendar_utils.py`
- NO repetir lógica de calendario en templates o rutas
- Usar siempre las utilidades centralizadas para consistencia
- Actualizar tests cuando se añadan nuevas funcionalidades
- El context processor se ejecuta en cada request, evitar operaciones costosas

## Soporte

Para preguntas o issues relacionados con el sistema de calendario, consultar:
- Este documento: `docs/CALENDAR_SYSTEM.md`
- Código fuente: `utils/calendar_utils.py`
- Tests: `test_calendar.py`
