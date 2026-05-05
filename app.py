from flask import Flask
import os
from utils.calendar_utils import crear_contexto_calendario
from utils.app_utils import get_version_info
from datetime import datetime, date

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'atma-suddhi-yoga-management-2025-secure-key')

# Configuración de base de datos para producción
if os.environ.get('FLASK_ENV') == 'production':
    # Para Hostinger con MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql://usuario:password@localhost/nombre_bd')
else:
    # Para desarrollo local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yoga_school.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# Initialize database
from models import db, Configuracion
db.init_app(app)

# Import Blueprints
from routes import (
    main_bp, auth_bp, student_bp, finance_bp, 
    class_bp, yogatherapia_bp, settings_bp, user_routes_bp,
    student_portal_bp, setup_bp
)

# Register Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(finance_bp)
app.register_blueprint(class_bp)
app.register_blueprint(yogatherapia_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(user_routes_bp)
app.register_blueprint(student_portal_bp)
app.register_blueprint(setup_bp)

# Context Processor para hacer disponibles las utilidades de calendario y versión en todos los templates
@app.context_processor
def inject_global_vars():
    """Inyecta configuración de la escuela, utilidades de calendario y versión en todos los templates."""
    try:
        # Obtener configuración de la escuela
        configs = Configuracion.query.all()
        config_dict = {c.clave: c.valor for c in configs}
    except Exception:
        config_dict = {}

    context = crear_contexto_calendario()
    context['config'] = config_dict
    context['version_info'] = get_version_info()
    context['today'] = date.today()
    context['datetime'] = datetime
    return context

# Onboarding check
from flask import redirect, url_for, request
from models import Usuario

@app.before_request
def check_onboarding():
    # Evitar bucle infinito y permitir estáticos
    if request.endpoint in ['setup.onboarding', 'static']:
        return
        
    # Si no hay usuarios en la DB, redirigir a setup
    try:
        if not Usuario.query.first():
            return redirect(url_for('setup.onboarding'))
    except Exception:
        # Probablemente la DB no está inicializada aún
        pass

# The rest of app.py is now handled by Blueprints
# Only keeping shell commands or app-level error handlers if any

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)