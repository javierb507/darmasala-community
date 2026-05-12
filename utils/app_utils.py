import os
import json
from datetime import datetime
from flask import current_app
from models import Sutra, SesionYogaterapia

def get_version_info():
    """Obtener información de versión desde el archivo JSON"""
    try:
        # Usar current_app para acceder a static_folder de manera segura
        static_folder = current_app.static_folder
        version_file = os.path.join(static_folder, 'version.json')
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    
    # Fallback si no existe el archivo
    return {
        'version': '2.0.1-final',
        'build_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'git_info': {
            'commit_hash': 'unknown',
            'branch': 'main',
            'commit_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }

def obtener_sutra_semanal():
    """Obtener el sutra de la semana actual"""
    # Obtener el número de semana del año
    semana_actual = datetime.now().isocalendar()[1]
    
    # Obtener el sutra correspondiente a esta semana
    try:
        total_sutras = Sutra.query.count()
        if total_sutras == 0:
            return None
        
        # Usar el número de semana para seleccionar un sutra
        indice_sutra = (semana_actual - 1) % total_sutras
        sutra = Sutra.query.offset(indice_sutra).first()
        
        if sutra:
            # Formatear el número del sutra como I.1, I.2, etc.
            if '.' in str(sutra.numero):
                # Si ya tiene formato I.1, mantenerlo
                sutra.numero_formateado = sutra.numero
            else:
                # Si es solo un número, formatearlo como I.X
                try:
                    num = int(sutra.numero)
                    sutra.numero_formateado = f"I.{num}"
                except:
                    sutra.numero_formateado = sutra.numero
        
        return sutra
    except Exception as e:
        print(f"Error consultando sutras: {e}")
        return None

def obtener_proximas_citas(limite=5):
    """Obtener las próximas citas individuales para el dashboard"""
    hoy = datetime.now().date()
    
    from models import EventoCalendario
    
    # 1. Citas heredadas (SesionYogaterapia)
    proximas_yogaterapia = SesionYogaterapia.query.filter(
        SesionYogaterapia.fecha_sesion >= hoy
    ).all()
    
    # 2. Citas unificadas (EventoCalendario puntuales)
    hoy_dt = datetime.combine(hoy, datetime.min.time())
    proximas_evento = EventoCalendario.query.filter(
        EventoCalendario.fecha_inicio >= hoy_dt,
        EventoCalendario.activo == True
    ).all()
    
    citas_combinadas = []
    
    for s in proximas_yogaterapia:
        citas_combinadas.append({
            'id': s.id,
            'is_evento': False,
            'alumno_nombre': f"{s.alumno.nombre} {s.alumno.apellido}" if s.alumno else "Desconocido",
            'fecha_sesion': s.fecha_sesion,
            'hora_inicio': s.hora_inicio
        })
        
    for e in proximas_evento:
        citas_combinadas.append({
            'id': e.id,
            'is_evento': True,
            'alumno_nombre': e.titulo,
            'fecha_sesion': e.fecha_inicio.date(),
            'hora_inicio': e.fecha_inicio.time()
        })
        
    # Ordenar por fecha y hora
    citas_combinadas.sort(key=lambda x: (x['fecha_sesion'], x['hora_inicio'] if x['hora_inicio'] else datetime.min.time()))
    
    return citas_combinadas[:limite]

def verificar_conflicto_horario(fecha, hora_inicio, hora_fin, sesion_id=None):
    """Verificar si hay conflicto de horarios en una fecha específica"""
    from models import SesionYogaterapia, HorarioSemanal
    if not hora_inicio or not hora_fin:
        return False, None
    
    # Obtener el día de la semana (0=Lunes, 6=Domingo)
    dia_semana = fecha.weekday()
    
    # 1. Verificar conflictos con sesiones de yogaterapia existentes
    sesiones_existentes = SesionYogaterapia.query.filter(
        SesionYogaterapia.fecha_sesion == fecha,
        SesionYogaterapia.hora_inicio.isnot(None),
        SesionYogaterapia.hora_fin.isnot(None)
    ).all()
    
    # Si estamos editando, excluir la sesión actual
    if sesion_id:
        sesiones_existentes = [s for s in sesiones_existentes if s.id != sesion_id]
    
    for sesion in sesiones_existentes:
        # Verificar si los horarios se solapan
        if (hora_inicio < sesion.hora_fin and hora_fin > sesion.hora_inicio):
            return True, {
                'tipo': 'yogaterapia',
                'sesion': sesion,
                'mensaje': f'Ya existe una cita de yogaterapia de {sesion.hora_inicio.strftime("%H:%M")} a {sesion.hora_fin.strftime("%H:%M")} con {sesion.alumno.nombre} {sesion.alumno.apellido}'
            }
    
    # 2. Verificar conflictos con clases grupales del horario semanal
    horarios_semanal = HorarioSemanal.query.filter(
        HorarioSemanal.dia_semana == dia_semana,
        HorarioSemanal.activo == True
    ).all()
    
    for horario in horarios_semanal:
        # Verificar si los horarios se solapan
        if (hora_inicio < horario.hora_fin and hora_fin > horario.hora_inicio):
            return True, {
                'tipo': 'clase_grupal',
                'horario': horario,
                'mensaje': f'Conflicto con clase grupal: {horario.clase.nombre} de {horario.hora_inicio.strftime("%H:%M")} a {horario.hora_fin.strftime("%H:%M")} ({horario.get_dia_display()})'
            }
    
    return False, None

def inicializar_clases():
    """Inicializar las clases básicas si no existen."""
    from models import db, Clase
    clases_basicas = [
        {'nombre': 'Yoga menopausia', 'descripcion': 'Clase especializada para mujeres en etapa de menopausia'},
        {'nombre': 'Yoga integral', 'descripcion': 'Práctica completa de yoga que integra posturas, respiración y meditación'},
        {'nombre': 'Yoga embarazadas', 'descripcion': 'Yoga adaptado para mujeres embarazadas'},
        {'nombre': 'Meditación', 'descripcion': 'Práctica de meditación y mindfulness'}
    ]
    
    for clase_data in clases_basicas:
        clase_existente = Clase.query.filter_by(nombre=clase_data['nombre']).first()
        if not clase_existente:
            clase = Clase(
                nombre=clase_data['nombre'],
                descripcion=clase_data['descripcion']
            )
            db.session.add(clase)
    
    try:
        db.session.commit()
        print("✅ Clases básicas inicializadas")
    except Exception as e:
        db.session.rollback()
        print(f"Error al inicializar clases: {e}")

def inicializar_categorias_gastos():
    """Inicializar categorías de gastos predeterminadas si no existen."""
    from models import db, CategoriaGasto
    categorias_default = [
        {'nombre': 'Alquiler', 'descripcion': 'Alquiler del local', 'color': '#1E3A2F'},
        {'nombre': 'Suministros', 'descripcion': 'Luz, agua, gas, internet', 'color': '#6B8E7E'},
        {'nombre': 'Material', 'descripcion': 'Esterillas, bloques, material de yoga', 'color': '#D4C9B3'},
        {'nombre': 'Marketing', 'descripcion': 'Publicidad y promoción', 'color': '#1E3A2F'},
        {'nombre': 'Formación', 'descripcion': 'Cursos y certificaciones', 'color': '#1E3A2F'},
        {'nombre': 'Seguros', 'descripcion': 'Seguros de responsabilidad civil', 'color': '#6B8E7E'},
        {'nombre': 'Mantenimiento', 'descripcion': 'Limpieza y mantenimiento', 'color': '#D4C9B3'},
        {'nombre': 'Otros', 'descripcion': 'Gastos varios', 'color': '#6B8E7E'}
    ]
    
    try:
        for cat_data in categorias_default:
            categoria_existente = CategoriaGasto.query.filter_by(nombre=cat_data['nombre']).first()
            if not categoria_existente:
                categoria = CategoriaGasto(**cat_data)
                db.session.add(categoria)
        
        db.session.commit()
        print("✅ Categorías de gastos inicializadas")
    except Exception as e:
        db.session.rollback()
        print(f"Error al inicializar categorías: {e}")
