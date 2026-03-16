#!/usr/bin/env python3
"""
MASTER INITIALIZATION SCRIPT - Atma Suddhi Yoga School Management
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
        {'nombre': 'Alquiler', 'descripcion': 'Alquiler del local', 'color': '#dc3545'},
        {'nombre': 'Suministros', 'descripcion': 'Luz, agua, gas, internet', 'color': '#ffc107'},
        {'nombre': 'Material', 'descripcion': 'Esterillas, bloques, etc.', 'color': '#28a745'},
        {'nombre': 'Marketing', 'descripcion': 'Publicidad y promoción', 'color': '#007bff'},
        {'nombre': 'Formación', 'descripcion': 'Cursos y formación', 'color': '#6f42c1'},
        {'nombre': 'Otros', 'descripcion': 'Gastos varios', 'color': '#6c757d'}
    ]
    for cat_data in categorias:
        if not CategoriaGasto.query.filter_by(nombre=cat_data['nombre']).first():
            db.session.add(CategoriaGasto(**cat_data))

    # 2. Config
    print("⚙️ Initializing system configuration...")
    config_defaults = {
        'nombre_escuela': 'Atma Suddhi',
        'email_escuela': 'info@atmasuddhi.es',
        'color_primario': '#8B5FBF',
        'capacidad_centro': '20'
    }
    for clave, valor in config_defaults.items():
        if not Configuracion.query.filter_by(clave=clave).first():
            db.session.add(Configuracion(clave=clave, valor=valor))

    # 3. Fiscal Config
    if not ConfiguracionFiscal.query.first():
        db.session.add(ConfiguracionFiscal(
            nombre_empresa='Atma Suddhi Yoga',
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
        {'nombre': 'Yoga Integral', 'color': '#007bff', 'duracion_minutos': 75},
        {'nombre': 'Yoga Menopausia', 'color': '#e91e63', 'duracion_minutos': 75},
        {'nombre': 'Meditación', 'color': '#9c27b0', 'duracion_minutos': 45}
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
        {'nombre': 'Ana', 'apellido': 'García', 'email': 'ana@example.com', 'tipo_cuota': '1_clase_semanal', 'activo': True},
        {'nombre': 'Luis', 'apellido': 'Pérez', 'email': 'luis@example.com', 'tipo_cuota': '2_clases_semanal', 'activo': True},
        {'nombre': 'Marta', 'apellido': 'Sanz', 'email': 'marta@example.com', 'tipo_cuota': 'plana', 'activo': True}
    ]
    for s_data in students:
        if not Alumno.query.filter_by(email=s_data['email']).first():
            alumno = Alumno(**s_data)
            db.session.add(alumno)
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
                email='admin@atmasuddhi.es',
                password_hash=generate_password_hash(password),
                nombre='Admin',
                apellido='Atma',
                rol='admin',
                activo=True
            )
            db.session.add(admin)
            db.session.commit()
            print(f"👤 Default admin created (user: admin, pass: {password})")
        else:
            print("👤 Admin user already exists.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Initialize Atma Suddhi database')
    parser.add_argument('--reset', action='store_true', help='Wipe database before starting')
    parser.add_argument('--test', action='store_true', help='Load test/demo data')
    parser.add_argument('--admin-pass', type=str, default='AtmaSuddhi2025!', help='Set initial admin password')
    
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
