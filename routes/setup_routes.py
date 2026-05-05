from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from models import db, Usuario, Configuracion
from werkzeug.security import generate_password_hash
import os

setup_bp = Blueprint('setup', __name__)

@setup_bp.route('/setup', methods=['GET', 'POST'])
def onboarding():
    # Verificar si ya existe un admin
    if Usuario.query.filter_by(rol='admin').first():
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        admin_email = request.form.get('email')
        admin_password = request.form.get('password')
        school_name = request.form.get('school_name', 'DarmaSala')
        load_test_data = request.form.get('load_test_data') == 'on'

        try:
            # 1. Crear el usuario administrador
            admin = Usuario(
                username='admin',
                email=admin_email,
                password_hash=generate_password_hash(admin_password),
                nombre='Administrador',
                apellido='Sistema',
                rol='admin',
                activo=True
            )
            db.session.add(admin)

            # 2. Configurar branding básico
            config_defaults = {
                'nombre_escuela': school_name,
                'email_escuela': admin_email,
                'logo_escuela': 'images/logo_darmasala.jpg',
                'color_primario': '#1E3A2F'
            }
            for clave, valor in config_defaults.items():
                config_item = Configuracion.query.filter_by(clave=clave).first()
                if config_item:
                    config_item.valor = valor
                else:
                    db.session.add(Configuracion(clave=clave, valor=valor))

            db.session.commit()

            # 3. Cargar datos de prueba si se solicita
            if load_test_data:
                from init_db import init_test_data, init_base_data
                # Ya se crearon las tablas en app.py, pero aseguramos datos base
                init_base_data()
                init_test_data()

            flash('Configuración completada con éxito. Por favor, inicia sesión.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error durante la configuración: {str(e)}', 'danger')

    return render_template('setup/onboarding.html')
