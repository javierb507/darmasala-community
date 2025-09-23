#!/usr/bin/env python3
"""
Script para inicializar la base de datos en producción
"""

from app import app, db, Usuario, Clase, CategoriaGasto, generate_password_hash
from datetime import datetime, date

def inicializar_clases():
    """Inicializar clases básicas"""
    clases_basicas = [
        {'nombre': 'Yoga Integral', 'descripcion': 'Clase completa de yoga integral', 'duracion_minutos': 75, 'precio': 12.0},
        {'nombre': 'Yoga Menopausia', 'descripcion': 'Yoga especializado para mujeres en menopausia', 'duracion_minutos': 75, 'precio': 12.0},
        {'nombre': 'Yoga Prenatal', 'descripcion': 'Yoga para embarazadas', 'duracion_minutos': 75, 'precio': 12.0},
        {'nombre': 'Meditación', 'descripcion': 'Sesión de meditación guiada', 'duracion_minutos': 60, 'precio': 10.0},
        {'nombre': 'Yoga al aire libre', 'descripcion': 'Yoga en espacios naturales', 'duracion_minutos': 90, 'precio': 15.0}
    ]
    
    for clase_data in clases_basicas:
        clase = Clase.query.filter_by(nombre=clase_data['nombre']).first()
        if not clase:
            clase = Clase(**clase_data)
            db.session.add(clase)
    
    db.session.commit()
    print("✅ Clases básicas inicializadas")

def inicializar_categorias_gastos():
    """Inicializar categorías de gastos"""
    categorias = [
        {'nombre': 'Alquiler', 'descripcion': 'Alquiler del local'},
        {'nombre': 'Servicios', 'descripcion': 'Electricidad, agua, gas'},
        {'nombre': 'Material', 'descripcion': 'Materiales para las clases'},
        {'nombre': 'Marketing', 'descripcion': 'Publicidad y promoción'},
        {'nombre': 'Administración', 'descripcion': 'Gastos administrativos'},
        {'nombre': 'Mantenimiento', 'descripcion': 'Reparaciones y mantenimiento'}
    ]
    
    for cat_data in categorias:
        categoria = CategoriaGasto.query.filter_by(nombre=cat_data['nombre']).first()
        if not categoria:
            categoria = CategoriaGasto(**cat_data)
            db.session.add(categoria)
    
    db.session.commit()
    print("✅ Categorías de gastos inicializadas")

def crear_usuario_admin():
    """Crear usuario administrador"""
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        admin = Usuario(
            username='admin',
            email='admin@atmasuddhi.es',
            password_hash=generate_password_hash('AtmaSuddhi74'),
            nombre='Administrador',
            apellido='Sistema',
            rol='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuario administrador creado: admin / AtmaSuddhi74")
    else:
        print("✅ Usuario administrador ya existe")

def inicializar_base_datos():
    """Inicializar toda la base de datos"""
    with app.app_context():
        print("Inicializando base de datos...")
        
        # Crear todas las tablas
        db.create_all()
        print("✅ Tablas creadas")
        
        # Inicializar datos básicos
        inicializar_clases()
        inicializar_categorias_gastos()
        crear_usuario_admin()
        
        print("✅ Base de datos inicializada correctamente")

if __name__ == "__main__":
    inicializar_base_datos()
