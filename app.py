from flask import Flask
import os
import time
from utils.calendar_utils import crear_contexto_calendario
from utils.app_utils import get_version_info
from datetime import datetime, date

# Initialize Flask app
app = Flask(__name__)

# Configuration
_secret_key = os.environ.get('SECRET_KEY', '')
if not _secret_key:
    if os.environ.get('FLASK_ENV') == 'production':
        raise RuntimeError(
            "SECRET_KEY environment variable is required in production. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    _secret_key = 'darmasala-dev-only-not-for-production'
app.config['SECRET_KEY'] = _secret_key

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

# Edition flag (community | enterprise). Community Edition strips the student portal.
app.config['DARMASALA_EDITION'] = os.environ.get('DARMASALA_EDITION', 'community')

# Import Blueprints
from routes import (
    main_bp, auth_bp, student_bp, finance_bp,
    class_bp, yogatherapia_bp, settings_bp, user_routes_bp,
    setup_bp, bug_report_bp
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
app.register_blueprint(setup_bp)
app.register_blueprint(bug_report_bp)

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

    from flask import session as fsession
    context = crear_contexto_calendario()
    context['config'] = config_dict
    context['version_info'] = get_version_info()
    context['today'] = date.today()
    context['datetime'] = datetime
    context['session_timeout_minutes'] = fsession.get('timeout_minutes', 60)
    context['edition'] = app.config.get('DARMASALA_EDITION', 'community')
    return context

# Onboarding check + session timeout
from flask import redirect, url_for, request, session, flash, jsonify
from models import Usuario

_SESSION_TIMEOUT_EXEMPT = {
    'setup.onboarding', 'static',
    'auth.login', 'auth.logout',
}

@app.before_request
def check_onboarding():
    if request.endpoint in ['setup.onboarding', 'static']:
        return
    try:
        if not Usuario.query.first():
            return redirect(url_for('setup.onboarding'))
    except Exception:
        pass


@app.before_request
def check_session_timeout():
    if request.endpoint in _SESSION_TIMEOUT_EXEMPT:
        return

    rol = session.get('rol')
    if not rol:
        return

    last_activity = session.get('last_activity')
    now = time.time()

    if last_activity is not None:
        timeout_min = int(session.get('timeout_minutes', 60))
        if (now - last_activity) > timeout_min * 60:
            session.clear()
            flash('Tu sesión ha expirado por inactividad.', 'warning')
            return redirect(url_for('auth.login'))

    session['last_activity'] = now


@app.route('/ping')
def ping():
    """Renueva last_activity para evitar expiración de sesión."""
    if session.get('rol'):
        session['last_activity'] = time.time()
    return jsonify(ok=True)


# The rest of app.py is now handled by Blueprints
# Only keeping shell commands or app-level error handlers if any

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)