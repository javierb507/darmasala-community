#!/usr/bin/env python3
"""
MASTER INITIALIZATION SCRIPT - DarmaSala
This script simplifies the database setup process.
Usage:
  python init_db.py          - Basic initialization (Tables, Categories, Config)
  python init_db.py --test   - Initialization + Load test data (Students, Payments, etc.)
  python init_db.py --reset  - Wipe current database and start fresh
"""

import os
import sys
import argparse
from datetime import datetime, date, time, timedelta
import random
from werkzeug.security import generate_password_hash

# Ensure the root directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import (
    Usuario, Alumno, Pago, Clase, HorarioSemanal, Asistencia, 
    GastoMensual, CategoriaGasto, Configuracion, ConfiguracionFiscal,
    Instructor, Tarifa, TipoClase
)

def reset_database():
    """Wipes the database and starts fresh"""
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    
    if db_uri.startswith('sqlite:///'):
        db_path = os.path.join(app.root_path, 'instance', 'yoga_school.db')
        # Close connection before deleting
        db.session.remove()
        db.engine.dispose()
        
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"🗑️ Removed existing database at {db_path}")
            except Exception as e:
                print(f"⚠️ Could not remove database file: {e}")
        elif os.path.exists('yoga_school.db'):
            try:
                os.remove('yoga_school.db')
                print("🗑️ Removed existing database at root")
            except Exception as e:
                print(f"⚠️ Could not remove database file: {e}")
    else:
        # For MySQL or PostgreSQL, drop all tables
        print("🏗️ Dropping all tables (detected non-SQLite database)...")
        db.reflect()
        db.drop_all()
        print("✅ All tables dropped.")

def init_base_data():
    """Initializes essential system data"""
    print("🏗️ Creating database tables...")
    db.create_all()

    # 1. Categories
    print("📂 Initializing expense categories...")
    categorias = [
        {'nombre': 'Alquiler', 'descripcion': 'Alquiler del local', 'color': '#1E3A2F'},
        {'nombre': 'Suministros', 'descripcion': 'Luz, agua, gas, internet', 'color': '#6B8E7E'},
        {'nombre': 'Material', 'descripcion': 'Esterillas, bloques, etc.', 'color': '#D4C9B3'},
        {'nombre': 'Marketing', 'descripcion': 'Publicidad y promoción', 'color': '#1E3A2F'},
        {'nombre': 'Formación', 'descripcion': 'Cursos y formación', 'color': '#1E3A2F'},
        {'nombre': 'Otros', 'descripcion': 'Gastos varios', 'color': '#6B8E7E'}
    ]
    for cat_data in categorias:
        if not CategoriaGasto.query.filter_by(nombre=cat_data['nombre']).first():
            db.session.add(CategoriaGasto(**cat_data))

    # 2. Config
    print("⚙️ Initializing system configuration...")
    config_defaults = {
        'nombre_escuela': 'DarmaSala',
        'email_escuela': 'info@darmasala.cloud',
        'logo_escuela': 'images/logo_darmasala.jpg',
        'color_primario': '#1E3A2F',
        'capacidad_centro': '20',
        'dominio_portal': '',  # vacío = auto-detect desde request
    }
    for clave, valor in config_defaults.items():
        if not Configuracion.query.filter_by(clave=clave).first():
            db.session.add(Configuracion(clave=clave, valor=valor))

    # 3. Fiscal Config
    if not ConfiguracionFiscal.query.first():
        db.session.add(ConfiguracionFiscal(
            nombre_empresa='DarmaSala Yoga',
            nif='00000000X',
            direccion_fiscal='Calle Principal 1, Madrid',
            serie_factura_default='A'
        ))

    # 4. Class Types (New for flexible pricing)
    print("💰 Initializing class types...")
    tipos_clase = [
        {'codigo': '1_clase_semanal', 'nombre': '1 Clase Semanal', 'precio': 40.0, 'frecuencia': 'mensual'},
        {'codigo': '2_clases_semanal', 'nombre': '2 Clases Semanal', 'precio': 70.0, 'frecuencia': 'mensual'},
        {'codigo': 'plana', 'nombre': 'Tarifa Plana', 'precio': 90.0, 'frecuencia': 'mensual'},
        {'codigo': 'clase_suelta', 'nombre': 'Clase Suelta', 'precio': 15.0, 'frecuencia': 'por_clase'}
    ]
    for tipo in tipos_clase:
        if not TipoClase.query.filter_by(codigo=tipo['codigo']).first():
            db.session.add(TipoClase(**tipo))

    db.session.commit()

def init_test_data():
    """Loads demo data for testing"""
    print("👥 Creating demo students...")
    
    # Classes
    clases_data = [
        {'nombre': 'Yoga Integral', 'color': '#1E3A2F', 'duracion_minutos': 75},
        {'nombre': 'Yoga Menopausia', 'color': '#6B8E7E', 'duracion_minutos': 75},
        {'nombre': 'Meditación', 'color': '#D4C9B3', 'duracion_minutos': 45}
    ]
    clases = []
    for c_data in clases_data:
        clase = Clase.query.filter_by(nombre=c_data['nombre']).first()
        if not clase:
            clase = Clase(**c_data)
            db.session.add(clase)
            db.session.flush()
        clases.append(clase)

    # Students
    students = [
        {'nombre': 'Ana', 'apellido': 'García', 'email': 'ana@example.com', 'dni': '12345678A', 'telefono': '600111222', 'tipo_cuota': '1_clase_semanal', 'activo': True},
        {'nombre': 'Luis', 'apellido': 'Pérez', 'email': 'luis@example.com', 'dni': '87654321B', 'telefono': '611222333', 'tipo_cuota': '2_clases_semanal', 'activo': True},
        {'nombre': 'Marta', 'apellido': 'Sanz', 'email': 'marta@example.com', 'dni': '11223344C', 'telefono': '622333444', 'tipo_cuota': 'plana', 'activo': True},
        {'nombre': 'Carlos', 'apellido': 'Ruiz', 'email': 'carlos@example.com', 'dni': '44332211D', 'telefono': '633444555', 'tipo_cuota': '1_clase_semanal', 'activo': True},
        {'nombre': 'Elena', 'apellido': 'Martínez', 'email': 'elena@example.com', 'dni': '55667788E', 'telefono': '644555666', 'tipo_cuota': '2_clases_semanal', 'activo': True},
        {'nombre': 'Javier', 'apellido': 'López', 'email': 'javier@example.com', 'dni': '99887766F', 'telefono': '655666777', 'tipo_cuota': 'plana', 'activo': True}
    ]
    for s_data in students:
        if not Alumno.query.filter_by(email=s_data['email']).first():
            alumno = Alumno(**s_data)
            db.session.add(alumno)
            db.session.flush()
            
            # Use DNI as password if exists, otherwise use phone
            password_plain = s_data.get('dni') or s_data.get('telefono') or 'DarmaSala1234'
            # Create Portal User for this student
            portal_user = Usuario(
                username=s_data['email'],
                email=s_data['email'],
                password_hash=generate_password_hash(password_plain),
                nombre=s_data['nombre'],
                apellido=s_data['apellido'],
                rol='alumno',
                activo=True
            )
            db.session.add(portal_user)
            db.session.flush()

            # Add some payments
            for i in range(2):
                mes = (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m')
                pago = Pago(
                    alumno_id=alumno.id,
                    mes=mes,
                    monto=40.0 if i==0 else 35.0,
                    tipo_pago='cuota',
                    metodo_pago='bizum'
                )
                db.session.add(pago)

    # Schedule
    if HorarioSemanal.query.count() == 0:
        print("🕐 Creating demo schedule...")
        horarios = [
            {'clase_id': clases[0].id, 'dia_semana': 0, 'hora_inicio': time(10, 0), 'hora_fin': time(11, 15)},
            {'clase_id': clases[1].id, 'dia_semana': 2, 'hora_inicio': time(18, 0), 'hora_fin': time(19, 15)},
            {'clase_id': clases[2].id, 'dia_semana': 4, 'hora_inicio': time(19, 0), 'hora_fin': time(19, 45)}
        ]
        for h_data in horarios:
            db.session.add(HorarioSemanal(**h_data))

    db.session.commit()
    print("✅ Demo data loaded.")

def create_admin(password='admin'):
    """Creates a default admin user"""
    with app.app_context():
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(
                username='admin',
                email='admin@darmasala.cloud',
                password_hash=generate_password_hash(password),
                nombre='Admin',
                apellido='Sala',
                rol='admin',
                activo=True
            )
            db.session.add(admin)
            db.session.commit()
            print(f"👤 Default admin created (user: admin, pass: {password})")
        else:
            print("👤 Admin user already exists.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Initialize DarmaSala database')
    parser.add_argument('--reset', action='store_true', help='Wipe database before starting')
    parser.add_argument('--test', action='store_true', help='Load test/demo data')
    parser.add_argument('--admin-pass', type=str, default='DarmaSala2025!', help='Set initial admin password')
    
    args = parser.parse_args()

    with app.app_context():
        if args.reset:
            reset_database()
        
        init_base_data()
        
        if args.test:
            init_test_data()
            
        create_admin(args.admin_pass)
        
    print("\n" + "=" * 50)
    print("✅ INITIALIZATION COMPLETE")
    print("=" * 50)
