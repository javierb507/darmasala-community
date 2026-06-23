#!/usr/bin/env python3
"""
Carga un set completo de datos de prueba en DarmaSala.

Uso CLI:
    python cargar_datos_prueba_completos.py

Uso desde la web (Modo Pruebas):
    from cargar_datos_prueba_completos import cargar_datos_completos
    cargar_datos_completos(modo_web=True)

Genera:
- 10 alumnos
- 3 clases (Yoga Integral, Yoga Menopausia, Meditación)
- 16 horarios semanales repartidos entre lunes y viernes
- 4 semanas de asistencias históricas con tasa realista
- Pagos de cuotas de los 3 últimos meses + matrículas
- Configuración fiscal de la escuela
- 5 clientes (particulares, empresa, autónomo)
- 12 facturas emitidas distribuidas en 6 meses, con líneas
- 5 proveedores
- 20 facturas de proveedores distribuidas en 6 meses
- 3 gastos fijos (alquiler, luz, seguro)
- 2 clases online (YouTube) de la semana actual

Es idempotente respecto a duplicados detectables por clave única
(email, dni, número de factura, nombre de proveedor, etc.).
"""

import os
import sys
import random
import unicodedata
from datetime import datetime, date, time, timedelta


def _slug(s: str) -> str:
    """Quita acentos y espacios para construir emails seguros."""
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    return s.lower().split()[0]

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import (
    Alumno, Pago, Clase, HorarioSemanal, Asistencia,
    Cliente, ConfiguracionFiscal, FacturaEmitida, LineaFactura,
    Proveedor, CategoriaGasto, FacturaProveedor, GastoFijo,
    Configuracion, TipoClase,
)


# ---------------------------------------------------------------------------
# Catálogo base (clases, categorías, tipos de cuota, configuración)
# ---------------------------------------------------------------------------

def _ensure_clases():
    clases_data = [
        {'nombre': 'Yoga Integral',    'color': '#1E3A2F', 'duracion_minutos': 75, 'capacidad_maxima': 15, 'precio': 15.0},
        {'nombre': 'Yoga Menopausia',  'color': '#6B8E7E', 'duracion_minutos': 75, 'capacidad_maxima': 12, 'precio': 15.0},
        {'nombre': 'Meditación',       'color': '#D4C9B3', 'duracion_minutos': 45, 'capacidad_maxima': 20, 'precio': 10.0},
    ]
    out = {}
    for data in clases_data:
        clase = Clase.query.filter_by(nombre=data['nombre']).first()
        if not clase:
            clase = Clase(**data)
            db.session.add(clase)
            db.session.flush()
        out[data['nombre']] = clase
    return out


def _ensure_categorias():
    categorias = [
        {'nombre': 'Alquiler',     'color': '#dc3545'},
        {'nombre': 'Suministros',  'color': '#ffc107'},
        {'nombre': 'Material',     'color': '#28a745'},
        {'nombre': 'Marketing',    'color': '#007bff'},
        {'nombre': 'Formación',    'color': '#6f42c1'},
        {'nombre': 'Seguros',      'color': '#fd7e14'},
        {'nombre': 'Mantenimiento','color': '#20c997'},
        {'nombre': 'Otros',        'color': '#6c757d'},
    ]
    out = {}
    for data in categorias:
        cat = CategoriaGasto.query.filter_by(nombre=data['nombre']).first()
        if not cat:
            cat = CategoriaGasto(**data)
            db.session.add(cat)
            db.session.flush()
        out[data['nombre']] = cat
    return out


def _ensure_tipos_clase():
    tipos = [
        {'codigo': 'clase_suelta',       'nombre': 'Clase Suelta',       'precio': 15.0, 'frecuencia': 'por_clase'},
        {'codigo': '1_clase_semanal',    'nombre': '1 Clase Semanal',    'precio': 40.0, 'frecuencia': 'mensual'},
        {'codigo': '2_clases_semanal',   'nombre': '2 Clases Semanal',   'precio': 70.0, 'frecuencia': 'mensual'},
        {'codigo': 'plana',              'nombre': 'Tarifa Plana',       'precio': 90.0, 'frecuencia': 'mensual'},
        {'codigo': '1_clase_bimensual',  'nombre': '1 Clase Bimensual',  'precio': 75.0, 'frecuencia': 'bimensual'},
        {'codigo': '2_clases_bimensual', 'nombre': '2 Clases Bimensual', 'precio': 135.0,'frecuencia': 'bimensual'},
    ]
    for tipo in tipos:
        if not TipoClase.query.filter_by(codigo=tipo['codigo']).first():
            db.session.add(TipoClase(**tipo))


def _ensure_configuracion_fiscal():
    if ConfiguracionFiscal.query.first():
        return
    db.session.add(ConfiguracionFiscal(
        nombre_empresa='DarmaSala Yoga',
        nif='12345678X',
        direccion_fiscal='Calle del Loto 1, Bajo',
        codigo_postal='28001',
        ciudad='Madrid',
        provincia='Madrid',
        telefono='+34 600 000 000',
        email='info@darmasala.cloud',
        epigrafe_iae='967.2',
        regimen_iva='exento',
        tipo_retencion_default=7.0,
        exento_iva=True,
        texto_exencion_iva='Exento de IVA según art. 20.Uno.9º de la Ley 37/1992',
        serie_factura_default='A',
        pie_factura='Gracias por confiar en DarmaSala. Periodo de conservación: 4 años.',
    ))


def _ensure_configuracion_basica():
    defaults = {
        'nombre_escuela':         'DarmaSala',
        'email_escuela':          'info@darmasala.cloud',
        'logo_escuela':           'images/logo_darmasala.jpg',
        'color_primario':         '#1E3A2F',
        'capacidad_centro':       '20',
        'session_timeout_admin':  '60',
    }
    for clave, valor in defaults.items():
        row = Configuracion.query.filter_by(clave=clave).first()
        if row:
            row.valor = valor
        else:
            db.session.add(Configuracion(clave=clave, valor=valor))


# ---------------------------------------------------------------------------
# Alumnos + usuarios de portal
# ---------------------------------------------------------------------------

ALUMNOS = [
    {'nombre': 'Ana',     'apellido': 'García',    'dni': '12345678A', 'tipo_cuota': '1_clase_semanal',  'matricula_pagada': True},
    {'nombre': 'Luis',    'apellido': 'Pérez',     'dni': '87654321B', 'tipo_cuota': '2_clases_semanal', 'matricula_pagada': True},
    {'nombre': 'Marta',   'apellido': 'Sanz',      'dni': '11223344C', 'tipo_cuota': 'plana',            'matricula_pagada': True},
    {'nombre': 'Carlos',  'apellido': 'Ruiz',      'dni': '44332211D', 'tipo_cuota': '1_clase_semanal',  'matricula_pagada': True},
    {'nombre': 'Elena',   'apellido': 'Martínez',  'dni': '55667788E', 'tipo_cuota': '2_clases_semanal', 'matricula_pagada': True},
    {'nombre': 'Javier',  'apellido': 'López',     'dni': '99887766F', 'tipo_cuota': 'plana',            'matricula_pagada': True},
    {'nombre': 'Sofía',   'apellido': 'Romero',    'dni': '10293847G', 'tipo_cuota': '1_clase_bimensual','matricula_pagada': False},
    {'nombre': 'Pablo',   'apellido': 'Navarro',   'dni': '57463829H', 'tipo_cuota': '2_clases_bimensual','matricula_pagada': True},
    {'nombre': 'Lucía',   'apellido': 'Iglesias',  'dni': '38291746J', 'tipo_cuota': '1_clase_semanal',  'matricula_pagada': True},
    {'nombre': 'Diego',   'apellido': 'Castro',    'dni': '64738291K', 'tipo_cuota': 'clase_suelta',     'matricula_pagada': False},
]


def _ensure_alumnos():
    alumnos_obj = []
    for data in ALUMNOS:
        email = f"{_slug(data['nombre'])}.{_slug(data['apellido'])}@example.com"
        # Busca por email O dni; cualquiera de los dos puede existir
        alumno = (
            Alumno.query.filter_by(email=email).first()
            or Alumno.query.filter_by(dni=data['dni']).first()
        )
        if not alumno:
            alumno = Alumno(
                nombre=data['nombre'],
                apellido=data['apellido'],
                dni=data['dni'],
                email=email,
                telefono=f"6{random.randint(10000000, 99999999)}",
                tipo_cuota=data['tipo_cuota'],
                matricula_pagada=data['matricula_pagada'],
                fecha_matricula=date.today().replace(month=9, day=1) if data['matricula_pagada'] else None,
                activo=True,
            )
            db.session.add(alumno)
            db.session.flush()

        alumnos_obj.append(alumno)
    return alumnos_obj


# ---------------------------------------------------------------------------
# Horarios semanales (16 slots de lunes a viernes)
# ---------------------------------------------------------------------------

def _ensure_horarios(clases):
    """16 horarios entre lunes (0) y viernes (4)."""
    yi = clases['Yoga Integral']
    ym = clases['Yoga Menopausia']
    med = clases['Meditación']

    horarios_data = [
        # Lunes
        (0, time(10, 0),  time(11, 15), yi),
        (0, time(17, 0),  time(18, 15), ym),
        (0, time(18, 30), time(19, 15), med),
        (0, time(19, 30), time(20, 45), yi),
        # Martes
        (1, time(10, 0),  time(11, 15), yi),
        (1, time(18, 30), time(19, 15), med),
        (1, time(19, 30), time(20, 45), yi),
        # Miércoles
        (2, time(10, 0),  time(11, 15), yi),
        (2, time(18, 0),  time(19, 15), ym),
        (2, time(19, 30), time(20, 45), yi),
        # Jueves
        (3, time(10, 0),  time(11, 15), yi),
        (3, time(18, 30), time(19, 15), med),
        (3, time(19, 30), time(20, 45), yi),
        # Viernes
        (4, time(10, 0),  time(11, 15), yi),
        (4, time(18, 30), time(19, 15), med),
        (4, time(19, 30), time(20, 45), yi),
    ]

    horarios_obj = []
    for dia, ini, fin, clase in horarios_data:
        existente = HorarioSemanal.query.filter_by(
            clase_id=clase.id, dia_semana=dia, hora_inicio=ini
        ).first()
        if not existente:
            existente = HorarioSemanal(
                clase_id=clase.id,
                dia_semana=dia,
                hora_inicio=ini,
                hora_fin=fin,
                capacidad_maxima=clase.capacidad_maxima,
                activo=True,
            )
            db.session.add(existente)
            db.session.flush()
        horarios_obj.append(existente)
    return horarios_obj


# ---------------------------------------------------------------------------
# Asistencias históricas (4 semanas)
# ---------------------------------------------------------------------------

def _seed_asistencias(alumnos, horarios, semanas=4):
    """Genera asistencias para últimas N semanas. Tasa 60-90% por clase."""
    if alumnos and Asistencia.query.filter_by(alumno_id=alumnos[0].id).first():
        return 0

    hoy = date.today()
    creadas = 0
    for semana_atras in range(semanas):
        inicio_semana = hoy - timedelta(days=hoy.weekday() + 7 * semana_atras)

        for horario in horarios:
            fecha_clase = inicio_semana + timedelta(days=horario.dia_semana)
            if fecha_clase > hoy:
                continue

            # Selecciona inscritos al azar (40-80% del cupo)
            n = random.randint(max(3, horario.capacidad_maxima // 3),
                               max(4, horario.capacidad_maxima * 4 // 5))
            inscritos = random.sample(alumnos, min(n, len(alumnos)))
            for alumno in inscritos:
                presente = random.random() < random.uniform(0.6, 0.9)
                db.session.add(Asistencia(
                    alumno_id=alumno.id,
                    horario_id=horario.id,
                    fecha_clase=fecha_clase,
                    presente=presente,
                ))
                creadas += 1
    return creadas


# ---------------------------------------------------------------------------
# Pagos de cuota
# ---------------------------------------------------------------------------

PRECIOS = {
    'clase_suelta':       15.0,
    '1_clase_semanal':    40.0,
    '2_clases_semanal':   70.0,
    'plana':              90.0,
    '1_clase_bimensual':  75.0,
    '2_clases_bimensual': 135.0,
}


def _seed_pagos(alumnos):
    """Cuotas últimos 3 meses + matrículas."""
    if alumnos and Pago.query.filter_by(alumno_id=alumnos[0].id).first():
        return 0

    hoy = date.today()
    creados = 0
    for alumno in alumnos:
        precio = PRECIOS.get(alumno.tipo_cuota, 40.0)
        if alumno.matricula_pagada:
            db.session.add(Pago(
                alumno_id=alumno.id,
                año=hoy.year,
                monto=25.0,
                tipo_pago='matricula',
                metodo_pago=random.choice(['bizum', 'transferencia', 'efectivo']),
                descripcion='Matrícula curso',
            ))
            creados += 1

        for i in range(3):
            mes_dt = hoy.replace(day=1) - timedelta(days=30 * i)
            mes_str = mes_dt.strftime('%Y-%m')
            db.session.add(Pago(
                alumno_id=alumno.id,
                mes=mes_str,
                monto=precio,
                tipo_pago='cuota',
                metodo_pago=random.choice(['bizum', 'transferencia', 'efectivo', 'tarjeta']),
                descripcion=f"Cuota {mes_str}",
            ))
            creados += 1
    return creados


# ---------------------------------------------------------------------------
# Clientes + facturas emitidas
# ---------------------------------------------------------------------------

CLIENTES = [
    {'nombre': 'Ana García',              'nif_cif': '12345678A', 'tipo': 'particular', 'ciudad': 'Madrid'},
    {'nombre': 'Centro Deportivo Vital',  'nif_cif': 'B12345678', 'tipo': 'empresa',    'ciudad': 'Madrid'},
    {'nombre': 'Ayuntamiento de Alcalá',  'nif_cif': 'P2800100A', 'tipo': 'empresa',    'ciudad': 'Alcalá de Henares'},
    {'nombre': 'Carmen Ruiz Salazar',     'nif_cif': '87654321B', 'tipo': 'autonomo',   'ciudad': 'Madrid'},
    {'nombre': 'Luis Pérez Moreno',       'nif_cif': '11223344C', 'tipo': 'particular', 'ciudad': 'Madrid'},
]


def _ensure_clientes():
    clientes_obj = []
    for data in CLIENTES:
        c = Cliente.query.filter_by(nif_cif=data['nif_cif']).first()
        if not c:
            c = Cliente(
                nombre=data['nombre'],
                nif_cif=data['nif_cif'],
                direccion=f"Calle Ejemplo {random.randint(1,99)}",
                codigo_postal=f"28{random.randint(100,799)}",
                ciudad=data['ciudad'],
                provincia='Madrid',
                email=f"{data['nombre'].lower().replace(' ', '.')}@example.com",
                telefono=f"6{random.randint(10000000,99999999)}",
                tipo_cliente=data['tipo'],
                activo=True,
            )
            db.session.add(c)
            db.session.flush()
        clientes_obj.append(c)
    return clientes_obj


CONCEPTOS_FACTURA = [
    ('Mensualidad clases de yoga', 40.0),
    ('Mensualidad 2 clases semanales', 70.0),
    ('Mensualidad tarifa plana', 90.0),
    ('Taller meditación fin de semana', 60.0),
    ('Sesión individual yogaterapia', 50.0),
    ('Curso intensivo verano', 180.0),
]


def _seed_facturas_emitidas(clientes):
    if clientes and FacturaEmitida.query.filter_by(cliente_id=clientes[0].id).first():
        return 0

    hoy = date.today()
    creadas = 0
    contador_por_año = {}

    for i in range(12):
        cliente = random.choice(clientes)
        meses_atras = random.randint(0, 5)
        fecha = hoy.replace(day=random.randint(1, 28)) - timedelta(days=30 * meses_atras)
        año = fecha.year
        contador_por_año[año] = contador_por_año.get(año, 0) + 1
        numero = contador_por_año[año]
        numero_completo = f"A/{año}/{numero:04d}"

        # 1-2 líneas
        n_lineas = random.choice([1, 2])
        conceptos = random.sample(CONCEPTOS_FACTURA, n_lineas)
        base = round(sum(precio for _, precio in conceptos), 2)
        retencion = 7.0 if cliente.tipo_cliente in ('empresa', 'autonomo') else 0.0
        cuota_ret = round(base * retencion / 100, 2)
        total = round(base - cuota_ret, 2)
        estado = random.choices(
            ['pagada', 'emitida'], weights=[75, 25]
        )[0]

        f = FacturaEmitida(
            serie='A',
            numero=numero,
            numero_completo=numero_completo,
            fecha_emision=fecha,
            fecha_prestacion=fecha,
            cliente_id=cliente.id,
            base_imponible=base,
            tipo_iva=0.0,
            cuota_iva=0.0,
            tipo_retencion=retencion,
            cuota_retencion=cuota_ret,
            total=total,
            exenta_iva=True,
            motivo_exencion='Art. 20.Uno.9º Ley 37/1992',
            estado=estado,
            fecha_pago=fecha + timedelta(days=random.randint(1, 25)) if estado == 'pagada' else None,
            metodo_pago='transferencia' if estado == 'pagada' else None,
        )
        db.session.add(f)
        db.session.flush()

        for orden, (descripcion, precio) in enumerate(conceptos):
            db.session.add(LineaFactura(
                factura_id=f.id,
                orden=orden,
                descripcion=descripcion,
                cantidad=1.0,
                precio_unitario=precio,
                subtotal=precio,
            ))
        creadas += 1
    return creadas


# ---------------------------------------------------------------------------
# Proveedores + facturas de proveedores + gastos fijos
# ---------------------------------------------------------------------------

PROVEEDORES = [
    {'nombre': 'Inmobiliaria Centro SL',     'cif_nif': 'B11111111', 'categoria': 'Alquiler'},
    {'nombre': 'Iberdrola SA',               'cif_nif': 'A99000001', 'categoria': 'Suministros'},
    {'nombre': 'Suministros Yoga Spain SL',  'cif_nif': 'B22222222', 'categoria': 'Material'},
    {'nombre': 'Material Deportivo Pro',     'cif_nif': 'B33333333', 'categoria': 'Material'},
    {'nombre': 'Seguros Mapfre',             'cif_nif': 'A99000002', 'categoria': 'Seguros'},
]


def _ensure_proveedores():
    out = {}
    for data in PROVEEDORES:
        p = Proveedor.query.filter_by(nombre=data['nombre']).first()
        if not p:
            p = Proveedor(
                nombre=data['nombre'],
                cif_nif=data['cif_nif'],
                direccion=f"Calle Proveedor {random.randint(1, 50)}",
                telefono=f"9{random.randint(10000000, 99999999)}",
                email=f"contacto@{data['nombre'].split()[0].lower()}.es",
                activo=True,
            )
            db.session.add(p)
            db.session.flush()
        out[data['nombre']] = (p, data['categoria'])
    return out


def _seed_facturas_proveedores(proveedores_map, categorias):
    inmo = proveedores_map['Inmobiliaria Centro SL'][0]
    if FacturaProveedor.query.filter_by(proveedor_id=inmo.id).first():
        return 0

    hoy = date.today()
    rangos_por_categoria = {
        'Alquiler':    (800, 1000),
        'Suministros': (50, 180),
        'Material':    (60, 450),
        'Seguros':     (150, 320),
    }

    creadas = 0
    for i in range(20):
        nombre_prov, (proveedor, categoria_nombre) = random.choice(list(proveedores_map.items()))
        rango = rangos_por_categoria.get(categoria_nombre, (50, 200))
        importe_sin = round(random.uniform(*rango), 2)
        iva = 21.0
        total = round(importe_sin * (1 + iva / 100), 2)
        meses_atras = random.randint(0, 5)
        fecha = hoy.replace(day=random.randint(1, 28)) - timedelta(days=30 * meses_atras)
        estado = random.choices(['pagada', 'pendiente'], weights=[80, 20])[0]

        db.session.add(FacturaProveedor(
            numero_factura=f"{proveedor.cif_nif[:4]}-{fecha.strftime('%Y%m')}-{i:03d}",
            proveedor_id=proveedor.id,
            nombre_proveedor=proveedor.nombre,
            categoria_id=categorias[categoria_nombre].id,
            fecha_factura=fecha,
            fecha_vencimiento=fecha + timedelta(days=30),
            importe_sin_iva=importe_sin,
            iva=iva,
            importe_total=total,
            descripcion=f"Servicios {categoria_nombre.lower()} {fecha.strftime('%B %Y')}",
            estado=estado,
            fecha_pago=fecha + timedelta(days=random.randint(1, 28)) if estado == 'pagada' else None,
            metodo_pago='transferencia' if estado == 'pagada' else None,
        ))
        creadas += 1
    return creadas


def _seed_gastos_fijos(proveedores_map, categorias):
    if GastoFijo.query.filter_by(nombre='Alquiler del local').first():
        return 0

    inicio = date.today().replace(day=1)
    inmo = proveedores_map['Inmobiliaria Centro SL'][0]
    iberdrola = proveedores_map['Iberdrola SA'][0]
    mapfre = proveedores_map['Seguros Mapfre'][0]

    gastos = [
        GastoFijo(
            nombre='Alquiler del local',
            descripcion='Renta mensual del local de la escuela',
            proveedor_id=inmo.id,
            categoria_id=categorias['Alquiler'].id,
            importe=950.0,
            frecuencia='mensual',
            dia_cargo=1,
            fecha_inicio=inicio,
            activo=True,
        ),
        GastoFijo(
            nombre='Suministro eléctrico',
            descripcion='Factura de luz del local',
            proveedor_id=iberdrola.id,
            categoria_id=categorias['Suministros'].id,
            importe=120.0,
            frecuencia='mensual',
            dia_cargo=15,
            fecha_inicio=inicio,
            activo=True,
        ),
        GastoFijo(
            nombre='Seguro responsabilidad civil',
            descripcion='Seguro RC anual',
            proveedor_id=mapfre.id,
            categoria_id=categorias['Seguros'].id,
            importe=450.0,
            frecuencia='anual',
            dia_cargo=1,
            fecha_inicio=inicio,
            activo=True,
        ),
    ]
    for g in gastos:
        db.session.add(g)
    return len(gastos)


# ---------------------------------------------------------------------------
# Orquestador
# ---------------------------------------------------------------------------

def cargar_datos_completos(modo_web=False):
    """Carga el set completo. Idempotente: respeta registros existentes."""
    random.seed(42)

    with app.app_context():
        db.create_all()

        log = print if not modo_web else (lambda *a, **k: None)
        log('🔧 Configuración base...')
        _ensure_configuracion_basica()
        _ensure_configuracion_fiscal()
        _ensure_tipos_clase()
        categorias = _ensure_categorias()
        clases = _ensure_clases()

        log('👥 Alumnos...')
        alumnos = _ensure_alumnos()
        db.session.flush()

        log('🕐 Horarios semanales...')
        horarios = _ensure_horarios(clases)
        db.session.flush()

        log('📋 Asistencias históricas...')
        n_asis = _seed_asistencias(alumnos, horarios)

        log('💰 Pagos de cuota...')
        n_pagos = _seed_pagos(alumnos)

        log('👤 Clientes facturación...')
        clientes = _ensure_clientes()

        log('🧾 Facturas emitidas...')
        n_fac = _seed_facturas_emitidas(clientes)

        log('🏢 Proveedores...')
        proveedores_map = _ensure_proveedores()

        log('🧾 Facturas de proveedores...')
        n_facprov = _seed_facturas_proveedores(proveedores_map, categorias)

        log('🔁 Gastos fijos...')
        n_gf = _seed_gastos_fijos(proveedores_map, categorias)

        db.session.commit()

        resumen = {
            'alumnos':              len(alumnos),
            'horarios':             len(horarios),
            'asistencias':          n_asis,
            'pagos':                n_pagos,
            'clientes':             len(clientes),
            'facturas_emitidas':    n_fac,
            'proveedores':          len(proveedores_map),
            'facturas_proveedores': n_facprov,
            'gastos_fijos':         n_gf,
        }
        if not modo_web:
            print('\n✅ Datos de prueba cargados:')
            for k, v in resumen.items():
                print(f"   {k}: {v}")
        return resumen


if __name__ == '__main__':
    cargar_datos_completos(modo_web=False)
