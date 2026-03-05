#!/usr/bin/env python3
"""
TESTING_APP.PY - Script completo para cargar datos de prueba
Script integral para inicializar la aplicación Atma Suddhi con datos de prueba completos
Incluye: usuarios, alumnos, clases, horarios, pagos, sesiones de yogaterapia, contabilidad y sutras
"""

import os
import sys
import random
import re
from datetime import datetime, date, timedelta, time
from werkzeug.security import generate_password_hash

# Agregar el directorio actual al path para importar app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import (
    db, Usuario, Alumno, Pago, SesionYogaterapia, HorarioSemanal, 
    Clase, Asistencia, CategoriaGasto, Proveedor, GastoFijo, 
    FacturaProveedor, GastoMensual, Sutra, TipoClase, EventoCalendario, Instructor
)

def limpiar_base_datos():
    """Limpiar completamente la base de datos"""
    print("🧹 Limpiando base de datos...")
    
    try:
        # Eliminar en orden correcto para evitar problemas de claves foráneas
        from sqlalchemy import text
        db.session.execute(text('PRAGMA foreign_keys = OFF'))
        
        # Eliminar datos en orden
        # AsistenciaEvento.query.delete()  # Temporary fix - model not defined
        EventoCalendario.query.delete()
        Asistencia.query.delete()
        SesionYogaterapia.query.delete()
        Pago.query.delete()
        FacturaProveedor.query.delete()
        GastoMensual.query.delete()
        GastoFijo.query.delete()
        Proveedor.query.delete()
        CategoriaGasto.query.delete()
        HorarioSemanal.query.delete()
        Clase.query.delete()
        TipoClase.query.delete()
        Alumno.query.delete()
        Usuario.query.delete()
        Instructor.query.delete()
        Sutra.query.delete()
        
        db.session.commit()
        db.session.execute(text('PRAGMA foreign_keys = ON'))
        
        print("✅ Base de datos limpiada")
    except Exception as e:
        print(f"⚠️ Error al limpiar base de datos: {e}")
        try:
            db.session.rollback()
        except:
            pass

def crear_tablas():
    """Crear todas las tablas"""
    print("🏗️ Creando estructura de tablas...")
    db.create_all()
    print("✅ Tablas creadas")

def crear_instructores():
    """Crear instructores predeterminados"""
    print("👨‍🏫 Creando instructores...")
    instructores_data = [
        {'nombre': 'Minouche', 'especialidad': 'Yoga Integral y Yogaterapia', 'email': 'minouche@atmasuddhi.es'},
        {'nombre': 'Elena', 'especialidad': 'Hatha y Meditación', 'email': 'elena@atmasuddhi.es'},
        {'nombre': 'Carlos', 'especialidad': 'Vinyasa y Dinámico', 'email': 'carlos@atmasuddhi.es'}
    ]
    
    for data in instructores_data:
        inst = Instructor(**data)
        db.session.add(inst)
    
    db.session.commit()
    print("✅ Instructores creados")

def crear_usuario_admin():
    """Crear usuario administrador"""
    print("👤 Creando usuario administrador...")
    
    # Verificar si ya existe
    admin_existente = Usuario.query.filter_by(username='admin').first()
    if admin_existente:
        print("✅ Usuario administrador ya existe")
        print("   👤 Usuario: admin")
        print("   🔑 Contraseña: AtmaSuddhi74")
        return
    
    admin = Usuario(
        username='admin',
        email='admin@atmasuddhi.es',
        password_hash=generate_password_hash('AtmaSuddhi74'),
        nombre='Administrador',
        apellido='Sistema',
        rol='admin',
        activo=True,
        fecha_creacion=datetime.utcnow()
    )
    db.session.add(admin)
    db.session.commit()
    
    print("✅ Usuario administrador creado")
    print("   👤 Usuario: admin")
    print("   🔑 Contraseña: AtmaSuddhi74")

def crear_eventos_calendario():
    """Crear eventos del calendario unificado basados en horarios semanales"""
    print("📅 Creando eventos del calendario unificado...")
    
    # Obtener horarios semanales activos
    horarios = HorarioSemanal.query.filter_by(activo=True).all()
    eventos_creados = 0
    
    # Generar eventos para los próximos 3 meses
    fecha_inicio = date.today()
    fecha_fin = fecha_inicio + timedelta(days=90)
    
    for horario in horarios:
        # Generar eventos recurrentes para cada horario semanal
        fecha_actual = fecha_inicio
        
        while fecha_actual <= fecha_fin:
            # Verificar si la fecha corresponde al día de la semana del horario
            if fecha_actual.weekday() == horario.dia_semana:
                # Verificar si ya existe un evento para esta fecha y horario
                inicio_dt_check = datetime.combine(fecha_actual, horario.hora_inicio)
                evento_existente = EventoCalendario.query.filter_by(
                    fecha_inicio=inicio_dt_check
                ).first()
                
                if not evento_existente:
                    # Combinar fecha y hora para fecha_inicio y fecha_fin
                    inicio_dt = datetime.combine(fecha_actual, horario.hora_inicio)
                    fin_dt = datetime.combine(fecha_actual, horario.hora_fin)
                    
                    evento = EventoCalendario(
                        titulo=f"{horario.clase.nombre}",
                        descripcion=horario.clase.descripcion or f"Clase de {horario.clase.nombre}",
                        fecha_inicio=inicio_dt,
                        fecha_fin=fin_dt,
                        tipo='clase_grupal',
                        clase_id=horario.clase_id,
                        instructor=horario.instructor,
                        color=horario.clase.color,
                        activo=True
                    )
                    db.session.add(evento)
                    eventos_creados += 1
            
            fecha_actual += timedelta(days=1)
    
    # Crear algunos eventos especiales de ejemplo
    eventos_especiales = [
        {
            'titulo': 'Taller de Meditación Avanzada',
            'descripcion': 'Taller especial de meditación para practicantes avanzados',
            'fecha': date.today() + timedelta(days=14),
            'hora_inicio': time(10, 0),
            'hora_fin': time(12, 0),
            'tipo_evento': 'evento_especial',
            'instructor': 'Minouche',
            'capacidad_maxima': 8,
            'precio': 25.0,
            'color': '#9c27b0'
        },
        {
            'titulo': 'Sesión de Yoga en el Parque',
            'descripcion': 'Práctica de yoga al aire libre (sujeto a condiciones climáticas)',
            'fecha': date.today() + timedelta(days=21),
            'hora_inicio': time(9, 0),
            'hora_fin': time(10, 30),
            'tipo_evento': 'evento_especial',
            'instructor': 'Minouche',
            'capacidad_maxima': 15,
            'precio': 12.0,
            'color': '#4caf50'
        }
    ]
    
    for evento_data in eventos_especiales:
        # Combinar fecha y hora para fecha_inicio y fecha_fin
        fecha = evento_data.pop('fecha')
        hora_inicio = evento_data.pop('hora_inicio')
        hora_fin = evento_data.pop('hora_fin')
        
        inicio_dt = datetime.combine(fecha, hora_inicio)
        fin_dt = datetime.combine(fecha, hora_fin)
        
        # Mapear campos
        if 'tipo_evento' in evento_data:
            evento_data['tipo'] = evento_data.pop('tipo_evento')
            
        # Eliminar campos no presentes en el modelo simplificado
        if 'precio' in evento_data:
            evento_data.pop('precio')
        if 'capacidad_maxima' in evento_data:
            evento_data.pop('capacidad_maxima')
            
        evento = EventoCalendario(
            fecha_inicio=inicio_dt,
            fecha_fin=fin_dt,
            **evento_data
        )
        db.session.add(evento)
        eventos_creados += 1
    
    db.session.commit()
    print(f"✅ {eventos_creados} eventos de calendario creados")
    return eventos_creados

def crear_tipos_clase():
    """Crear tipos de clase configurables"""
    print("🏷️ Creando tipos de clase...")
    
    tipos_data = [
        {
            'codigo': 'pendiente',
            'nombre': 'Pendiente de asignación',
            'descripcion': 'Alumno registrado pero aún sin tipo de cuota definido',
            'precio': 0.00,
            'frecuencia': 'mensual',
            'orden': 0,
            'color': '#6c757d',
            'activo': True
        },
        {
            'codigo': 'clase_suelta',
            'nombre': 'Clase suelta',
            'descripcion': 'Pago por clase individual. Ideal para probar o asistencia esporádica',
            'precio': 15.00,
            'frecuencia': 'por_clase',
            'orden': 1,
            'color': '#17a2b8',
            'activo': True
        },
        {
            'codigo': '1_clase_semanal',
            'nombre': '1 clase por semana',
            'descripcion': 'Una clase semanal fija. Ideal para principiantes',
            'precio': 40.00,
            'frecuencia': 'mensual',
            'orden': 2,
            'color': '#28a745',
            'activo': True
        },
        {
            'codigo': '2_clases_semanal',
            'nombre': '2 clases por semana',
            'descripcion': 'Dos clases semanales. Práctica regular recomendada',
            'precio': 70.00,
            'frecuencia': 'mensual',
            'orden': 3,
            'color': '#ffc107',
            'activo': True
        },
        {
            'codigo': 'plana',
            'nombre': 'Tarifa plana',
            'descripcion': 'Acceso ilimitado a todas las clases del mes',
            'precio': 90.00,
            'frecuencia': 'mensual',
            'orden': 4,
            'color': '#dc3545',
            'activo': True
        },
        {
            'codigo': '1_clase_bimensual',
            'nombre': '1 clase bimensual',
            'descripcion': 'Una clase por semana pagada cada dos meses',
            'precio': 75.00,
            'frecuencia': 'bimensual',
            'orden': 5,
            'color': '#6f42c1',
            'activo': True
        },
        {
            'codigo': '2_clases_bimensual',
            'nombre': '2 clases bimensual',
            'descripcion': 'Dos clases por semana pagadas cada dos meses',
            'precio': 135.00,
            'frecuencia': 'bimensual',
            'orden': 6,
            'color': '#e83e8c',
            'activo': True
        },
        {
            'codigo': 'yogaterapia_individual',
            'nombre': 'Yogaterapia individual',
            'descripcion': 'Sesiones personalizadas de yogaterapia individual',
            'precio': 50.00,
            'frecuencia': 'por_clase',
            'orden': 7,
            'color': '#fd7e14',
            'activo': True
        },
        {
            'codigo': 'yogaterapia_pareja',
            'nombre': 'Yogaterapia en pareja',
            'descripcion': 'Sesiones de yogaterapia para dos personas',
            'precio': 70.00,
            'frecuencia': 'por_clase',
            'orden': 8,
            'color': '#20c997',
            'activo': True
        }
    ]
    
    try:
        tipos_creados = []
        for tipo_data in tipos_data:
            # Verificar si ya existe
            tipo_existente = TipoClase.query.filter_by(codigo=tipo_data['codigo']).first()
            if tipo_existente:
                # Actualizar datos existentes
                for key, value in tipo_data.items():
                    setattr(tipo_existente, key, value)
                tipos_creados.append(tipo_existente)
            else:
                # Crear nuevo tipo
                tipo = TipoClase(**tipo_data)
                db.session.add(tipo)
                tipos_creados.append(tipo)
        
        db.session.commit()
        print(f"✅ {len(tipos_creados)} tipos de clase procesados (creados/actualizados)")
        return tipos_creados
    except Exception as e:
        print(f"❌ Error al crear tipos de clase: {e}")
        db.session.rollback()
        return []

def crear_clases_completas():
    """Crear clases completas con todos los detalles"""
    print("📚 Creando clases completas...")
    
    clases_data = [
        {
            'nombre': 'Yoga Integral', 
            'descripcion': 'Práctica completa de yoga que integra posturas, respiración y meditación',
            'precio': 15.00,
            'color': '#007bff',
            'nivel': 'todos',
            'duracion_minutos': 75,
            'capacidad_maxima': 15,
            'activa': True
        },
        {
            'nombre': 'Yoga Embarazadas', 
            'descripcion': 'Yoga prenatal seguro y beneficioso para futuras mamás',
            'precio': 15.00,
            'color': '#28a745',
            'nivel': 'principiante',
            'duracion_minutos': 60,
            'capacidad_maxima': 10,
            'activa': True
        },
        {
            'nombre': 'Yoga Menopausia', 
            'descripcion': 'Yoga específicamente diseñado para mujeres en etapa de menopausia',
            'precio': 15.00,
            'color': '#dc3545',
            'nivel': 'principiante',
            'duracion_minutos': 60,
            'capacidad_maxima': 12,
            'activa': True
        },
        {
            'nombre': 'Meditación', 
            'descripcion': 'Sesiones de meditación guiada y mindfulness',
            'precio': 12.00,
            'color': '#6f42c1',
            'nivel': 'todos',
            'duracion_minutos': 45,
            'capacidad_maxima': 20,
            'activa': True
        }
    ]
    
    clases = []
    for clase_data in clases_data:
        # Verificar si la clase ya existe
        clase_existente = Clase.query.filter_by(nombre=clase_data['nombre']).first()
        if clase_existente:
            # Actualizar clase existente
            for key, value in clase_data.items():
                setattr(clase_existente, key, value)
            clases.append(clase_existente)
        else:
            # Crear nueva clase
            clase = Clase(**clase_data)
            db.session.add(clase)
            clases.append(clase)
    
    db.session.commit()
    print(f"✅ {len(clases)} clases procesadas (creadas/actualizadas)")
    return clases

def crear_horarios_semanales(clases):
    """Crear horarios semanales completos"""
    print("⏰ Creando horarios semanales...")
    
    # Mapeo de nombres de clases a objetos
    clase_map = {clase.nombre: clase for clase in clases}
    
    horarios_data = [
        # Lunes (0)
        {'clase': 'Yoga Integral', 'dia_semana': 0, 'hora_inicio': '09:30', 'hora_fin': '10:45'},
        {'clase': 'Yoga Menopausia', 'dia_semana': 0, 'hora_inicio': '18:00', 'hora_fin': '19:00'},
        
        # Martes (1)
        {'clase': 'Yoga Embarazadas', 'dia_semana': 1, 'hora_inicio': '10:00', 'hora_fin': '11:00'},
        {'clase': 'Meditación', 'dia_semana': 1, 'hora_inicio': '19:00', 'hora_fin': '19:45'},
        
        # Miércoles (2)
        {'clase': 'Yoga Integral', 'dia_semana': 2, 'hora_inicio': '09:30', 'hora_fin': '10:45'},
        {'clase': 'Yoga Menopausia', 'dia_semana': 2, 'hora_inicio': '18:00', 'hora_fin': '19:00'},
        
        # Jueves (3)
        {'clase': 'Yoga Embarazadas', 'dia_semana': 3, 'hora_inicio': '10:00', 'hora_fin': '11:00'},
        {'clase': 'Meditación', 'dia_semana': 3, 'hora_inicio': '19:00', 'hora_fin': '19:45'},
        
        # Viernes (4)
        {'clase': 'Yoga Integral', 'dia_semana': 4, 'hora_inicio': '10:00', 'hora_fin': '11:15'},
        {'clase': 'Yoga Integral', 'dia_semana': 4, 'hora_inicio': '18:30', 'hora_fin': '19:45'},
        
        # Sábado (5)
        {'clase': 'Yoga Integral', 'dia_semana': 5, 'hora_inicio': '10:00', 'hora_fin': '11:15', 'instructor': 'Minouche'},
        {'clase': 'Meditación', 'dia_semana': 5, 'hora_inicio': '11:30', 'hora_fin': '12:15', 'instructor': 'Elena'},
    ]
    
    horarios = []
    for horario_data in horarios_data:
        clase = clase_map.get(horario_data['clase'])
        if clase:
            horario = HorarioSemanal(
                clase_id=clase.id,
                dia_semana=horario_data['dia_semana'],
                hora_inicio=datetime.strptime(horario_data['hora_inicio'], '%H:%M').time(),
                hora_fin=datetime.strptime(horario_data['hora_fin'], '%H:%M').time(),
                instructor=horario_data.get('instructor', 'Minouche'),
                activo=True
            )
            db.session.add(horario)
            horarios.append(horario)
    
    db.session.commit()
    print(f"✅ {len(horarios)} horarios semanales creados")
    return horarios

def crear_alumnos_diversos():
    """Crear alumnos con diferentes estados de pago"""
    print("👥 Creando alumnos diversos...")
    
    nombres_f = ['Ana', 'María', 'Carmen', 'Isabel', 'Laura', 'Elena', 'Sofia', 'Patricia', 'Rosa', 'Mónica', 'Cristina', 'Pilar', 'Teresa', 'Esperanza', 'Dolores']
    nombres_m = ['Carlos', 'Miguel', 'Antonio', 'José', 'Francisco', 'David', 'Juan', 'Pedro', 'Luis', 'Alejandro', 'Rafael', 'Fernando']
    apellidos = ['García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez', 'Sánchez', 'Pérez', 'Gómez', 'Martín', 'Jiménez', 'Ruiz', 'Hernández', 'Díaz', 'Moreno']
    
    ciudades_madrid = ['Madrid', 'Alcalá de Henares', 'Getafe', 'Móstoles', 'Fuenlabrada', 'Leganés', 'Alcorcón', 'Parla', 'Torrejón de Ardoz', 'Alcobendas', 'Las Rozas', 'Pozuelo de Alarcón', 'San Sebastián de los Reyes', 'Rivas-Vaciamadrid', 'Majadahonda']
    
    medicamentos_comunes = [
        'Ninguno',
        'Ibuprofeno ocasional',
        'Paracetamol para dolores',
        'Omeprazol para el estómago',
        'Antihistamínicos para alergia',
        'Vitamina D',
        'Magnesio',
        'Suplemento de hierro',
        'Antidepresivos',
        'Anticonceptivos orales',
        'Medicación para la tensión',
        'Medicación para tiroides'
    ]
    
    alergias_comunes = [
        'Ninguna',
        'Polen',
        'Ácaros del polvo',
        'Frutos secos',
        'Látex',
        'Medicamentos (aspirina)',
        'Pelo de animales',
        'Mariscos',
        'Níquel',
        'Perfumes y productos químicos'
    ]
    
    estados_fisicos = [
        'Buena forma física general',
        'Sedentario, empezando actividad física',
        'Forma física regular, practica deporte ocasionalmente',
        'Muy activo, practica varios deportes',
        'En recuperación de lesión',
        'Problemas de espalda recurrentes',
        'Artritis leve en articulaciones',
        'Fibromialgia controlada',
        'Estrés y tensión muscular',
        'Embarazada (segundo trimestre)',
        'Postparto reciente',
        'Menopausia con sofocos',
        'Hipertensión controlada',
        'Ansiedad y estrés laboral',
        'Insomnio frecuente'
    ]
    
    motivaciones = [
        'Reducir el estrés del trabajo y encontrar paz interior',
        'Mejorar la flexibilidad y fortaleza del cuerpo',
        'Aliviar dolores de espalda y mejorar la postura',
        'Encontrar un momento de tranquilidad en el día',
        'Complementar otros deportes con flexibilidad',
        'Gestionar la ansiedad de forma natural',
        'Conectar con mi cuerpo durante el embarazo',
        'Recuperarme físicamente después del parto',
        'Encontrar equilibrio en la menopausia',
        'Socializar y conocer gente con intereses similares',
        'Desarrollar disciplina mental y concentración',
        'Mejorar la calidad del sueño',
        'Explorar la espiritualidad y mindfulness',
        'Rehabilitación después de una lesión',
        'Mantenerme activa de forma suave',
        'Liberar tensiones emocionales acumuladas',
        'Aprender técnicas de respiración para la vida diaria',
        'Complementar tratamiento médico de forma holística',
        'Encontrar una actividad que pueda hacer toda la vida',
        'Mejorar mi relación conmigo misma'
    ]
    
    current_year = date.today().year
    current_month = date.today().month
    
    alumnos = []
    
    # Función auxiliar para generar IBAN español
    def generar_iban_espanol():
        banco = random.randint(1000, 9999)
        sucursal = random.randint(1000, 9999)
        dc = random.randint(10, 99)
        cuenta = random.randint(1000000000, 9999999999)
        return f"ES{dc:02d} {banco:04d} {sucursal:04d} {dc:02d} {cuenta:010d}"
    
    # 1. Alumnos AL CORRIENTE (8 alumnos)
    for i in range(8):
        nombre = random.choice(nombres_f + nombres_m)
        apellido = random.choice(apellidos)
        tipo_cuota = random.choice(['1_clase_semanal', '2_clases_semanal', 'plana'])
        ciudad = random.choice(ciudades_madrid)
        
        alumno = Alumno(
            nombre=nombre,
            apellido=apellido,
            email=f"{nombre.lower()}.{apellido.lower()}{i}@email.com",
            telefono=f"6{random.randint(10000000, 99999999)}",
            fecha_nacimiento=date(1960 + random.randint(0, 40), random.randint(1, 12), random.randint(1, 28)),
            direccion=f"Calle {random.choice(['Mayor', 'Real', 'Nueva', 'Vieja', 'Principal'])} {random.randint(1, 100)}",
            condiciones_medicas=random.choice(['Ninguna', 'Hipertensión leve', 'Problemas de espalda', 'Artritis leve', 'Diabetes tipo 2 controlada']),
            tipo_cuota=tipo_cuota,
            matricula_pagada=True,
            fecha_matricula=date(current_year, 1, random.randint(1, 28)),
            activo=True
        )
        db.session.add(alumno)
        alumnos.append(alumno)
    
    # 2. Alumnos BIMENSUALES (4 alumnos)
    for i in range(4):
        nombre = random.choice(nombres_f)
        apellido = random.choice(apellidos)
        tipo_cuota = random.choice(['1_clase_bimensual', '2_clases_bimensual'])
        ciudad = random.choice(ciudades_madrid)
        
        alumno = Alumno(
            nombre=nombre,
            apellido=apellido,
            email=f"{nombre.lower()}.{apellido.lower()}{i+10}@email.com",
            telefono=f"6{random.randint(10000000, 99999999)}",
            fecha_nacimiento=date(1965 + random.randint(0, 35), random.randint(1, 12), random.randint(1, 28)),
            direccion=f"Avenida {random.choice(['Constitución', 'España', 'Libertad'])} {random.randint(1, 50)}",
            condiciones_medicas=random.choice(['Fibromialgia', 'Artritis reumatoide', 'Ninguna', 'Problemas cervicales']),
            tipo_cuota=tipo_cuota,
            matricula_pagada=True,
            fecha_matricula=date(current_year, 1, random.randint(1, 28)),
            activo=True
        )
        db.session.add(alumno)
        alumnos.append(alumno)
    
    # 3. Alumnos CON PAGOS PENDIENTES (5 alumnos)
    for i in range(5):
        nombre = random.choice(nombres_f + nombres_m)
        apellido = random.choice(apellidos)
        tipo_cuota = random.choice(['1_clase_semanal', '2_clases_semanal'])
        matricula_pagada = random.choice([True, False])
        ciudad = random.choice(ciudades_madrid)
        
        alumno = Alumno(
            nombre=nombre,
            apellido=apellido,
            email=f"{nombre.lower()}.{apellido.lower()}{i+20}@email.com",
            telefono=f"6{random.randint(10000000, 99999999)}",
            fecha_nacimiento=date(1970 + random.randint(0, 30), random.randint(1, 12), random.randint(1, 28)),
            direccion=f"Plaza {random.choice(['Mayor', 'España', 'Constitución'])} {random.randint(1, 20)}",
            condiciones_medicas=random.choice(['Estrés crónico', 'Insomnio', 'Ninguna', 'Ansiedad', 'Depresión leve']),
            tipo_cuota=tipo_cuota,
            matricula_pagada=matricula_pagada,
            fecha_matricula=date(current_year, 1, random.randint(1, 28)) if matricula_pagada else None,
            activo=True
        )
        db.session.add(alumno)
        alumnos.append(alumno)
    
    # 4. Alumnos INACTIVOS (2 alumnos)
    for i in range(2):
        nombre = random.choice(nombres_f)
        apellido = random.choice(apellidos)
        ciudad = random.choice(ciudades_madrid)
        
        alumno = Alumno(
            nombre=nombre,
            apellido=apellido,
            email=f"{nombre.lower()}.{apellido.lower()}{i+30}@email.com",
            telefono=f"6{random.randint(10000000, 99999999)}",
            fecha_nacimiento=date(1975 + random.randint(0, 25), random.randint(1, 12), random.randint(1, 28)),
            direccion=f"Calle {random.choice(['Olmo', 'Roble', 'Pino'])} {random.randint(1, 30)}",
            condiciones_medicas=random.choice(['Lesión de rodilla antigua', 'Problemas de espalda crónicos', 'Fibromialgia']),
            tipo_cuota=random.choice(['1_clase_semanal', '2_clases_semanal']),
            matricula_pagada=True,
            fecha_matricula=date(current_year, 1, 15),
            activo=True
        )
        db.session.add(alumno)
        alumnos.append(alumno)
    
    # 5. Alumno DESACTIVADO (1 alumno)
    alumno_desactivado = Alumno(
        nombre="Alumno",
        apellido="Desactivado",
        email="desactivado@email.com",
        telefono="600000000",
        fecha_nacimiento=date(1980, 5, 15),
        direccion="Calle Desactivada 1",
        condiciones_medicas="Ninguna",
        tipo_cuota='1_clase_semanal',
        matricula_pagada=False,
        activo=False
    )
    db.session.add(alumno_desactivado)
    alumnos.append(alumno_desactivado)
    
    # 6. Alumnos PENDIENTES (3 alumnos - solo datos recogidos, sin tipo de cuota definido)
    for i in range(3):
        nombre = random.choice(nombres_f + nombres_m)
        apellido = random.choice(apellidos)
        ciudad = random.choice(ciudades_madrid)
        
        alumno = Alumno(
            nombre=nombre,
            apellido=apellido,
            email=f"{nombre.lower()}.{apellido.lower()}{i+40}@email.com",
            telefono=f"6{random.randint(10000000, 99999999)}",
            fecha_nacimiento=date(1970 + random.randint(0, 30), random.randint(1, 12), random.randint(1, 28)),
            direccion=f"Calle {random.choice(['Esperanza', 'Libertad', 'Paz'])} {random.randint(1, 50)}",
            condiciones_medicas=random.choice(['Por determinar', 'Pendiente de evaluación', 'Sin especificar']),
            tipo_cuota='pendiente',  # Estado pendiente
            matricula_pagada=False,
            fecha_matricula=None,
            activo=True
        )
        db.session.add(alumno)
        alumnos.append(alumno)
    
    db.session.commit()
    print(f"✅ {len(alumnos)} alumnos creados (incluyendo 3 con estado pendiente)")
    return alumnos

def crear_pagos_realistas(alumnos):
    """Crear pagos realistas para los alumnos"""
    print("💰 Creando pagos realistas...")
    
    current_year = date.today().year
    current_month = date.today().month
    pagos_creados = 0
    
    for i, alumno in enumerate(alumnos):
        if not alumno.activo and alumno.email == "desactivado@email.com":
            continue  # Skip desactivado
        
        # Matrícula
        if alumno.matricula_pagada:
            pago_matricula = Pago(
                alumno_id=alumno.id,
                año=current_year,
                monto=25.00,
                tipo_pago='matricula',
                descripcion=f'Matrícula anual {current_year}',
                metodo_pago=random.choice(['efectivo', 'transferencia', 'tarjeta']),
                fecha_creacion=datetime(current_year, 1, random.randint(1, 28))
            )
            db.session.add(pago_matricula)
            pagos_creados += 1
        
        # Cuotas mensuales
        if i < 8:  # Alumnos al corriente
            for mes in range(1, current_month + 1):
                pago_cuota = Pago(
                    alumno_id=alumno.id,
                    mes=f"{current_year}-{mes:02d}",
                    monto=alumno.get_precio_cuota(),
                    tipo_pago='cuota',
                    descripcion=f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                    metodo_pago=random.choice(['efectivo', 'transferencia', 'tarjeta', 'bizum']),
                    fecha_creacion=datetime(current_year, mes, random.randint(1, 28))
                )
                db.session.add(pago_cuota)
                pagos_creados += 1
        
        elif i < 12:  # Alumnos bimensuales
            bimestres_pagados = []
            if current_month >= 2: bimestres_pagados.append((1, 2))
            if current_month >= 4: bimestres_pagados.append((3, 4))
            if current_month >= 6: bimestres_pagados.append((5, 6))
            if current_month >= 8: bimestres_pagados.append((7, 8))
            if current_month >= 10: bimestres_pagados.append((9, 10))
            
            for mes1, mes2 in bimestres_pagados:
                pago_bimestre = Pago(
                    alumno_id=alumno.id,
                    mes=f"{current_year}-{mes1:02d}",
                    monto=alumno.get_precio_cuota(),
                    tipo_pago='cuota',
                    descripcion=f'Cuota bimensual {mes1:02d}-{mes2:02d}/{current_year}',
                    metodo_pago=random.choice(['transferencia', 'efectivo']),
                    fecha_creacion=datetime(current_year, mes1, 15)
                )
                db.session.add(pago_bimestre)
                pagos_creados += 1
        
        elif i < 17:  # Alumnos con pagos pendientes
            meses_pagados = random.sample(range(1, current_month), random.randint(1, max(1, current_month - 2)))
            
            for mes in meses_pagados:
                pago_cuota = Pago(
                    alumno_id=alumno.id,
                    mes=f"{current_year}-{mes:02d}",
                    monto=alumno.get_precio_cuota(),
                    tipo_pago='cuota',
                    descripcion=f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                    metodo_pago=random.choice(['efectivo', 'transferencia']),
                    fecha_creacion=datetime(current_year, mes, random.randint(1, 28))
                )
                db.session.add(pago_cuota)
                pagos_creados += 1
        
        elif i < 19:  # Alumnos inactivos
            meses_antiguos = min(3, max(1, current_month - 3))
            for mes in range(1, meses_antiguos + 1):
                pago_cuota = Pago(
                    alumno_id=alumno.id,
                    mes=f"{current_year}-{mes:02d}",
                    monto=alumno.get_precio_cuota(),
                    tipo_pago='cuota',
                    descripcion=f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                    metodo_pago='efectivo',
                    fecha_creacion=datetime(current_year, mes, 15)
                )
                db.session.add(pago_cuota)
                pagos_creados += 1
    
    db.session.commit()
    print(f"✅ {pagos_creados} pagos creados")

def crear_sesiones_yogaterapia(alumnos):
    """Crear sesiones de yogaterapia"""
    print("🧘 Creando sesiones de yogaterapia...")
    
    sesiones_creadas = 0
    
    # Seleccionar algunos alumnos para yogaterapia
    alumnos_yogaterapia = random.sample([a for a in alumnos if a.activo], min(8, len([a for a in alumnos if a.activo])))
    
    for alumno in alumnos_yogaterapia:
        # Crear 2-4 sesiones por alumno
        num_sesiones = random.randint(2, 4)
        
        for i in range(num_sesiones):
            fecha_sesion = date.today() - timedelta(days=random.randint(0, 90))
            
            sesion = SesionYogaterapia(
                alumno_id=alumno.id,
                fecha_sesion=fecha_sesion,
                hora_inicio=datetime.strptime(f"{random.randint(9, 18):02d}:{random.choice(['00', '15', '30', '45'])}", '%H:%M').time(),
                hora_fin=datetime.strptime(f"{random.randint(10, 19):02d}:{random.choice(['00', '15', '30', '45'])}", '%H:%M').time(),
                duracion_minutos=random.choice([45, 60, 75, 90]),
                tipo_sesion='individual',
                motivo_consulta=random.choice([
                    'Dolor de espalda crónico',
                    'Estrés y ansiedad',
                    'Problemas de flexibilidad',
                    'Lesión de hombro',
                    'Insomnio',
                    'Fibromialgia',
                    'Problemas digestivos',
                    'Dolor cervical'
                ]),
                objetivos_terapeuticos=random.choice([
                    'Reducir dolor lumbar, mejorar postura',
                    'Gestión del estrés, técnicas de relajación',
                    'Aumentar flexibilidad, fortalecer core',
                    'Rehabilitación de hombro, movilidad',
                    'Mejorar calidad del sueño',
                    'Aliviar tensión muscular',
                    'Mejorar digestión, relajación abdominal',
                    'Liberar tensión cervical'
                ]),
                tecnicas_aplicadas=random.choice([
                    'Asanas terapéuticas, pranayama, relajación',
                    'Yin yoga, meditación mindfulness',
                    'Vinyasa suave, estiramientos',
                    'Yoga restaurativo, props',
                    'Nidra yoga, técnicas de respiración',
                    'Automasaje, movimientos suaves',
                    'Torsiones suaves, respiración abdominal',
                    'Movimientos cervicales, relajación'
                ]),
                posturas_trabajadas=random.choice([
                    'Balasana, Marjaryasana, Bhujangasana',
                    'Savasana, Viparita Karani, Sukhasana',
                    'Uttanasana, Adho Mukha Svanasana',
                    'Gomukhasana, Garudasana',
                    'Supta Baddha Konasana, Legs up the wall',
                    'Cat-Cow, Child pose, Sphinx',
                    'Supta Matsyendrasana, Apanasana',
                    'Neck rolls, Shoulder shrugs'
                ]),
                respiracion_pranayama=random.choice([
                    'Ujjayi, respiración abdominal',
                    'Nadi Shodhana, respiración 4-7-8',
                    'Bhramari, respiración completa',
                    'Respiración costal, Kapalabhati suave',
                    'Respiración lunar, So-Hum',
                    'Respiración consciente, conteo',
                    'Respiración abdominal profunda',
                    'Respiración relajante'
                ]),
                meditacion_relajacion=random.choice([
                    'Body scan, relajación progresiva',
                    'Mindfulness, atención plena',
                    'Visualización guiada',
                    'Meditación en la respiración',
                    'Yoga Nidra completo',
                    'Relajación muscular',
                    'Meditación caminando',
                    'Práctica de gratitud'
                ]),
                estado_inicial=random.choice([
                    'Tensión alta, dolor 7/10',
                    'Ansiedad, respiración superficial',
                    'Rigidez, movilidad limitada',
                    'Dolor agudo, inflamación',
                    'Insomnio, fatiga',
                    'Contracturas, estrés',
                    'Digestión lenta, hinchazón',
                    'Cefalea tensional'
                ]),
                respuesta_sesion=random.choice([
                    'Relajación progresiva, dolor 4/10',
                    'Respiración más profunda, calma',
                    'Mayor flexibilidad, bienestar',
                    'Reducción inflamación, alivio',
                    'Somnolencia, relajación profunda',
                    'Liberación tensión, paz',
                    'Mejora digestiva, relajación',
                    'Alivio cefalea, claridad'
                ]),
                estado_final=random.choice([
                    'Relajado, dolor reducido significativamente',
                    'Centrado, respiración equilibrada',
                    'Flexible, energizado',
                    'Alivio notable, movilidad mejorada',
                    'Muy relajado, preparado para dormir',
                    'Liberado, en paz',
                    'Digestión activada, cómodo',
                    'Sin dolor, mente clara'
                ]),
                observaciones_terapeuta=random.choice([
                    'Excelente respuesta, muy receptivo',
                    'Necesita práctica regular en casa',
                    'Progreso notable desde última sesión',
                    'Requiere trabajo específico en zona',
                    'Muy motivado, sigue indicaciones',
                    'Mejora gradual, constancia importante',
                    'Buena conciencia corporal',
                    'Responde bien a técnicas suaves'
                ]),
                recomendaciones_casa=random.choice([
                    'Practicar 10 min diarios, posturas básicas',
                    '5 min respiración antes de dormir',
                    'Estiramientos matutinos, 15 min',
                    'Ejercicios específicos 3 veces/día',
                    'Yoga Nidra nocturno, relajación',
                    'Automasaje diario, movimientos suaves',
                    'Respiración abdominal tras comidas',
                    'Pausas conscientes cada 2 horas'
                ]),
                proxima_sesion=random.choice([
                    'En una semana, continuar tratamiento',
                    'En 15 días, evaluar progreso',
                    'Próxima semana, trabajo específico',
                    'En 10 días, seguimiento',
                    'Semanal durante un mes',
                    'Según evolución, flexible',
                    'En una semana, profundizar técnicas',
                    'Quincenal, mantenimiento'
                ]),
                instructor='Minouche',
                precio=45.00,
                pagado=random.choice([True, False]),
                metodo_pago=random.choice(['efectivo', 'tarjeta', 'transferencia', 'bizum']) if random.choice([True, False]) else None
            )
            
            db.session.add(sesion)
            sesiones_creadas += 1
    
    db.session.commit()
    print(f"✅ {sesiones_creadas} sesiones de yogaterapia creadas")

def crear_asistencias(alumnos, horarios):
    """Crear asistencias simuladas"""
    print("📅 Creando asistencias simuladas...")
    
    if not horarios:
        print("⚠️ No hay horarios disponibles")
        return
    
    fecha_inicio = date.today() - timedelta(days=60)
    fecha_fin = date.today()
    asistencias_creadas = 0
    
    # Solo alumnos activos
    alumnos_activos = [a for a in alumnos if a.activo and a.email != "desactivado@email.com"]
    
    for alumno in alumnos_activos[:15]:  # Limitar para no sobrecargar
        # Determinar frecuencia según tipo de cuota
        if 'semanal' in alumno.tipo_cuota:
            if '1_clase' in alumno.tipo_cuota:
                clases_por_semana = 1
            elif '2_clases' in alumno.tipo_cuota:
                clases_por_semana = 2
            else:
                clases_por_semana = 1
        elif alumno.tipo_cuota == 'plana':
            clases_por_semana = random.randint(2, 4)
        else:
            clases_por_semana = 1
        
        probabilidad_asistencia = random.uniform(0.7, 0.95)
        
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            dia_semana = fecha_actual.weekday()
            
            # Buscar horarios para este día
            horarios_dia = [h for h in horarios if h.dia_semana == dia_semana]
            
            if horarios_dia and random.random() < (clases_por_semana / 7):
                horario = random.choice(horarios_dia)
                presente = random.random() < probabilidad_asistencia
                
                asistencia = Asistencia(
                    alumno_id=alumno.id,
                    horario_id=horario.id,
                    fecha_clase=fecha_actual,
                    presente=presente,
                    observaciones=random.choice([
                        None, None, None,  # Mayoría sin observaciones
                        'Muy bien hoy', 'Le costó un poco', 'Excelente práctica',
                        'Llegó tarde', 'Se fue antes'
                    ]) if presente else random.choice([
                        'Avisó por WhatsApp', 'No avisó', 'Enfermo/a',
                        'Trabajo', None
                    ])
                )
                db.session.add(asistencia)
                asistencias_creadas += 1
            
            fecha_actual += timedelta(days=1)
    
    db.session.commit()
    print(f"✅ {asistencias_creadas} asistencias creadas")

def crear_categorias_gastos():
    """Crear categorías de gastos"""
    print("📊 Creando categorías de gastos...")
    
    categorias = [
        {'nombre': 'Servicios Básicos', 'descripcion': 'Luz, agua, gas, internet', 'activo': True},
        {'nombre': 'Alquiler', 'descripcion': 'Alquiler del local', 'activo': True},
        {'nombre': 'Seguros', 'descripcion': 'Seguros del local y responsabilidad civil', 'activo': True},
        {'nombre': 'Mantenimiento', 'descripcion': 'Reparaciones y mantenimiento del local', 'activo': True},
        {'nombre': 'Marketing', 'descripcion': 'Publicidad, redes sociales, material promocional', 'activo': True},
        {'nombre': 'Material', 'descripcion': 'Esterillas, bloques, cinturones, etc.', 'activo': True},
        {'nombre': 'Formación', 'descripcion': 'Cursos, talleres, certificaciones', 'activo': True},
        {'nombre': 'Administración', 'descripcion': 'Gestoría, asesoría, software', 'activo': True},
        {'nombre': 'Transporte', 'descripcion': 'Combustible, transporte público', 'activo': True},
        {'nombre': 'Otros', 'descripcion': 'Gastos varios', 'activo': True}
    ]
    
    for cat_data in categorias:
        categoria = CategoriaGasto(**cat_data)
        db.session.add(categoria)
    
    db.session.commit()
    print(f"✅ {len(categorias)} categorías de gastos creadas")

def crear_proveedores():
    """Crear proveedores"""
    print("🏢 Creando proveedores...")
    
    proveedores = [
        {
            'nombre': 'Endesa Energía',
            'cif_nif': 'A81948009',
            'direccion': 'Calle de la Energía, 123, Madrid',
            'telefono': '900 123 456',
            'email': 'facturacion@endesa.es',
            'contacto_principal': 'Departamento de Facturación',
            'notas': 'Proveedor de electricidad',
            'activo': True
        },
        {
            'nombre': 'Canal de Isabel II',
            'cif_nif': 'G28000000',
            'direccion': 'Calle de Santa Engracia, 125, Madrid',
            'telefono': '900 100 100',
            'email': 'atencion@canaldeisabelsegunda.es',
            'contacto_principal': 'Atención al Cliente',
            'notas': 'Proveedor de agua',
            'activo': True
        },
        {
            'nombre': 'Propietario Local - María González',
            'cif_nif': '12345678A',
            'direccion': 'Calle del Yoga, 45, Madrid',
            'telefono': '666 123 456',
            'email': 'maria.gonzalez@email.com',
            'contacto_principal': 'María González',
            'notas': 'Propietaria del local',
            'activo': True
        },
        {
            'nombre': 'Yoga Material',
            'cif_nif': 'B12345678',
            'direccion': 'Calle de la Paz, 12, Madrid',
            'telefono': '911 234 567',
            'email': 'pedidos@yogamaterial.com',
            'contacto_principal': 'Pedro Martínez',
            'notas': 'Material de yoga y accesorios',
            'activo': True
        },
        {
            'nombre': 'Gestoría Contable SL',
            'cif_nif': 'B87654321',
            'direccion': 'Calle de la Contabilidad, 8, Madrid',
            'telefono': '915 678 901',
            'email': 'info@gestoriacontable.es',
            'contacto_principal': 'Ana López',
            'notas': 'Servicios de gestoría y asesoría fiscal',
            'activo': True
        }
    ]
    
    for prov_data in proveedores:
        proveedor = Proveedor(**prov_data)
        db.session.add(proveedor)
    
    db.session.commit()
    print(f"✅ {len(proveedores)} proveedores creados")

def crear_gastos_fijos():
    """Crear gastos fijos"""
    print("💼 Creando gastos fijos...")
    
    gastos_fijos = [
        {
            'nombre': 'Alquiler Local',
            'descripcion': 'Alquiler mensual del local',
            'categoria_id': CategoriaGasto.query.filter_by(nombre='Alquiler').first().id,
            'importe': 1200.00,
            'frecuencia': 'mensual',
            'dia_cargo': 1,
            'fecha_inicio': date(2024, 10, 1),
            'fecha_fin': date(2025, 12, 31),
            'activo': True
        },
        {
            'nombre': 'Gestoría Contable',
            'descripcion': 'Servicios de gestoría mensual',
            'categoria_id': CategoriaGasto.query.filter_by(nombre='Administración').first().id,
            'importe': 150.00,
            'frecuencia': 'mensual',
            'dia_cargo': 5,
            'fecha_inicio': date(2024, 10, 1),
            'fecha_fin': date(2025, 12, 31),
            'activo': True
        }
    ]
    
    for gasto_data in gastos_fijos:
        gasto = GastoFijo(**gasto_data)
        db.session.add(gasto)
    
    db.session.commit()
    print(f"✅ {len(gastos_fijos)} gastos fijos creados")

def crear_facturas_ejemplo():
    """Crear facturas de ejemplo"""
    print("🧾 Creando facturas de ejemplo...")
    
    hoy = date.today()
    tres_meses_atras = hoy - timedelta(days=90)
    
    proveedores_db = Proveedor.query.filter_by(activo=True).all()
    categorias_db = CategoriaGasto.query.filter_by(activo=True).all()
    
    if not proveedores_db or not categorias_db:
        print("⚠️ No hay proveedores o categorías disponibles")
        return
    
    facturas_ejemplo = [
        # Electricidad
        {'proveedor': 'Endesa Energía', 'categoria': 'Servicios Básicos', 'importe': 85.0, 'iva': 21.0},
        {'proveedor': 'Endesa Energía', 'categoria': 'Servicios Básicos', 'importe': 92.0, 'iva': 21.0},
        {'proveedor': 'Endesa Energía', 'categoria': 'Servicios Básicos', 'importe': 78.0, 'iva': 21.0},
        
        # Agua
        {'proveedor': 'Canal de Isabel II', 'categoria': 'Servicios Básicos', 'importe': 45.0, 'iva': 21.0},
        {'proveedor': 'Canal de Isabel II', 'categoria': 'Servicios Básicos', 'importe': 52.0, 'iva': 21.0},
        
        # Alquiler
        {'proveedor': 'Propietario Local - María González', 'categoria': 'Alquiler', 'importe': 1200.0, 'iva': 0.0},
        {'proveedor': 'Propietario Local - María González', 'categoria': 'Alquiler', 'importe': 1200.0, 'iva': 0.0},
        {'proveedor': 'Propietario Local - María González', 'categoria': 'Alquiler', 'importe': 1200.0, 'iva': 0.0},
        
        # Material
        {'proveedor': 'Yoga Material', 'categoria': 'Material', 'importe': 120.0, 'iva': 21.0},
        {'proveedor': 'Yoga Material', 'categoria': 'Material', 'importe': 85.0, 'iva': 21.0},
        
        # Gestoría
        {'proveedor': 'Gestoría Contable SL', 'categoria': 'Administración', 'importe': 150.0, 'iva': 21.0},
        {'proveedor': 'Gestoría Contable SL', 'categoria': 'Administración', 'importe': 150.0, 'iva': 21.0},
    ]
    
    fecha_actual = tres_meses_atras
    numero_factura = 1
    
    for factura_data in facturas_ejemplo:
        proveedor = next((p for p in proveedores_db if p.nombre == factura_data['proveedor']), None)
        categoria = next((c for c in categorias_db if c.nombre == factura_data['categoria']), None)
        
        if proveedor and categoria:
            fecha_vencimiento = fecha_actual + timedelta(days=30)
            
            factura = FacturaProveedor(
                numero_factura=f"FAC-{numero_factura:04d}",
                proveedor_id=proveedor.id,
                categoria_id=categoria.id,
                fecha_factura=fecha_actual,
                fecha_vencimiento=fecha_vencimiento,
                importe_sin_iva=factura_data['importe'],
                iva=factura_data['iva'],
                importe_total=factura_data['importe'] * (1 + factura_data['iva'] / 100),
                descripcion=f"Factura de {factura_data['categoria'].lower()} - {fecha_actual.strftime('%B %Y')}",
                estado='pagada' if fecha_actual < hoy - timedelta(days=15) else 'pendiente',
                fecha_pago=fecha_actual + timedelta(days=random.randint(1, 15)) if fecha_actual < hoy - timedelta(days=15) else None,
                metodo_pago=random.choice(['transferencia', 'efectivo', 'tarjeta']) if fecha_actual < hoy - timedelta(days=15) else None
            )
            
            db.session.add(factura)
            numero_factura += 1
            fecha_actual += timedelta(days=30)
    
    db.session.commit()
    print(f"✅ {numero_factura - 1} facturas creadas")

def cargar_sutras():
    """Cargar sutras desde archivo"""
    print("📜 Cargando sutras...")
    
    try:
        sutras_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Sutras_texto.md')
        
        if not os.path.exists(sutras_file):
            print("⚠️ Archivo Sutras_texto.md no encontrado, creando sutras básicos...")
            # Crear algunos sutras básicos si no existe el archivo
            sutras_basicos = [
                {
                    'numero': 'I.1',
                    'sanscrito': 'अथ योगानुशासनम्',
                    'transliteracion': 'atha yogānuśāsanam',
                    'traduccion': 'Ahora comienza la enseñanza del yoga.',
                    'libro': 'Samadhi Pada'
                },
                {
                    'numero': 'I.2',
                    'sanscrito': 'योगश्चित्तवृत्तिनिरोधः',
                    'transliteracion': 'yogaś citta-vṛtti-nirodhaḥ',
                    'traduccion': 'El yoga es el cese de las fluctuaciones de la mente.',
                    'libro': 'Samadhi Pada'
                },
                {
                    'numero': 'I.3',
                    'sanscrito': 'तदा द्रष्टुः स्वरूपेऽवस्थानम्',
                    'transliteracion': 'tadā draṣṭuḥ svarūpe\'vasthānam',
                    'traduccion': 'Entonces el observador se establece en su naturaleza esencial.',
                    'libro': 'Samadhi Pada'
                }
            ]
            
            for sutra_data in sutras_basicos:
                sutra = Sutra(**sutra_data)
                db.session.add(sutra)
            
            db.session.commit()
            print("✅ 3 sutras básicos creados")
            return
        
        # Leer archivo completo
        with open(sutras_file, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Patrón para extraer sutras
        patron = r'^([IVX]+\.\d+)\s*\n([^\n]+)\n([^\n]+)\n([^\n]+)$'
        sutras = re.findall(patron, contenido, re.MULTILINE)
        
        sutras_creados = 0
        for numero, sanscrito, transliteracion, traduccion in sutras:
            # Determinar libro según el número
            if numero.startswith('I.'):
                libro = 'Samadhi Pada'
            elif numero.startswith('II.'):
                libro = 'Sadhana Pada'
            elif numero.startswith('III.'):
                libro = 'Vibhuti Pada'
            elif numero.startswith('IV.'):
                libro = 'Kaivalya Pada'
            else:
                libro = 'Desconocido'
            
            sutra = Sutra(
                numero=numero.strip(),
                sanscrito=sanscrito.strip(),
                transliteracion=transliteracion.strip(),
                traduccion=traduccion.strip(),
                libro=libro
            )
            db.session.add(sutra)
            sutras_creados += 1
        
        db.session.commit()
        print(f"✅ {sutras_creados} sutras cargados desde archivo")
        
    except Exception as e:
        print(f"⚠️ Error cargando sutras: {e}")
        # Crear al menos un sutra básico
        sutra_basico = Sutra(
            numero='I.1',
            sanscrito='अथ योगानुशासनम्',
            transliteracion='atha yogānuśāsanam',
            traduccion='Ahora comienza la enseñanza del yoga.',
            libro='Samadhi Pada'
        )
        db.session.add(sutra_basico)
        db.session.commit()
        print("✅ 1 sutra básico creado")

def mostrar_resumen():
    """Mostrar resumen de datos creados"""
    print("\n" + "="*60)
    print("🎉 ¡DATOS DE TESTING CARGADOS EXITOSAMENTE!")
    print("="*60)
    
    try:
        print(f"👤 Usuarios: {Usuario.query.count()}")
        print(f"👨‍🏫 Instructores: {Instructor.query.count()}")
        print(f"👥 Alumnos: {Alumno.query.count()}")
        print(f"📚 Clases: {Clase.query.count()}")
        print(f"⏰ Horarios: {HorarioSemanal.query.count()}")
        print(f"💰 Pagos: {Pago.query.count()}")
        print(f"🧘 Sesiones Yogaterapia: {SesionYogaterapia.query.count()}")
        print(f"📅 Asistencias: {Asistencia.query.count()}")
        print(f"📊 Categorías Gastos: {CategoriaGasto.query.count()}")
        print(f"🏢 Proveedores: {Proveedor.query.count()}")
        print(f"💼 Gastos Fijos: {GastoFijo.query.count()}")
        print(f"🧾 Facturas: {FacturaProveedor.query.count()}")
        print(f"📜 Sutras: {Sutra.query.count()}")
        
        print("\n🔑 CREDENCIALES DE ACCESO:")
        print("   👤 Usuario: admin")
        print("   🔑 Contraseña: AtmaSuddhi74")
        print("   🌐 URL: http://localhost:5000")
        
        print("\n✨ CARACTERÍSTICAS INCLUIDAS:")
        print("   ✅ Usuarios y autenticación")
        print("   ✅ Alumnos con diferentes estados de pago")
        print("   ✅ Clases y horarios semanales")
        print("   ✅ Pagos realistas (al corriente, pendientes, etc.)")
        print("   ✅ Sesiones de yogaterapia detalladas")
        print("   ✅ Asistencias simuladas")
        print("   ✅ Módulo de contabilidad completo")
        print("   ✅ Sutras de Patanjali")
        
        print("\n🚀 ¡LISTO PARA USAR EN PRODUCCIÓN!")
        print("="*60)
        
    except Exception as e:
        print(f"⚠️ Error mostrando resumen: {e}")

def main():
    """Función principal"""
    print("🧘‍♀️ TESTING_APP - CARGA COMPLETA DE DATOS DE PRUEBA")
    print("🌟 Atma Suddhi - Gestión de Escuela de Yoga")
    print("="*70)
    
    try:
        # Generar información de versión
        print("📊 Generando información de versión...")
        try:
            from version_info import save_version_info
            save_version_info()
        except Exception as e:
            print(f"⚠️ No se pudo generar info de versión: {e}")
        
        with app.app_context():
            print("🚀 Iniciando proceso de carga...")
            
            # 1. Limpiar y crear estructura
            limpiar_base_datos()
            crear_tablas()
            
            # 2. Crear datos básicos
            crear_usuario_admin()
            crear_instructores()
            crear_tipos_clase()
            clases = crear_clases_completas()
            horarios = crear_horarios_semanales(clases)
            crear_eventos_calendario()
            
            # 3. Crear alumnos y pagos
            alumnos = crear_alumnos_diversos()
            crear_pagos_realistas(alumnos)
            
            # 4. Crear actividades
            crear_sesiones_yogaterapia(alumnos)
            crear_asistencias(alumnos, horarios)
            
            # 5. Crear módulo contabilidad
            crear_categorias_gastos()
            crear_proveedores()
            crear_gastos_fijos()
            crear_facturas_ejemplo()
            
            # 6. Cargar sutras
            cargar_sutras()
            
            # 7. Mostrar resumen
            mostrar_resumen()
            
            return 0
            
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        print("🔄 Revirtiendo cambios...")
        try:
            db.session.rollback()
        except:
            pass
        return 1

if __name__ == "__main__":
    exit(main())
