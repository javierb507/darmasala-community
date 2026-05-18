"""Bug reporter in-app: crea issues en GitHub desde la aplicación."""

import time
from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session,
    jsonify, current_app,
)

from models import db, Configuracion
from utils.auth_utils import login_required, admin_required
from utils.app_utils import get_version_info
from utils.github_issues import load_config, create_issue, GitHubIssuesError


bug_report_bp = Blueprint('bug_report', __name__)

# Rate limit: máximo 5 issues por sesión por hora
RATE_LIMIT_WINDOW = 3600
RATE_LIMIT_MAX = 5


# ---------------------------------------------------------------------------
# Admin config
# ---------------------------------------------------------------------------

@bug_report_bp.route('/admin/bug-report', methods=['GET'])
@login_required
@admin_required
def admin_config():
    cfg = {c.clave: c.valor for c in Configuracion.query.all()}
    gh = load_config(cfg)
    return render_template(
        'configuracion/bug_report.html',
        enabled=cfg.get('bug_report_enabled', '') == 'true',
        repo=cfg.get('bug_report_repo', ''),
        labels=cfg.get('bug_report_labels', 'bug,reportado-desde-app'),
        token_set=bool(gh.token),
    )


@bug_report_bp.route('/admin/bug-report/save', methods=['POST'])
@login_required
@admin_required
def admin_save():
    items = {
        'bug_report_enabled': 'true' if request.form.get('enabled') else 'false',
        'bug_report_repo':    request.form.get('repo', '').strip(),
        'bug_report_labels':  request.form.get('labels', '').strip() or 'bug,reportado-desde-app',
    }
    for clave, valor in items.items():
        existing = Configuracion.query.filter_by(clave=clave).first()
        if existing:
            existing.valor = valor
            existing.fecha_actualizacion = datetime.utcnow()
        else:
            db.session.add(Configuracion(clave=clave, valor=valor,
                                         descripcion='Bug Reporter (GitHub)'))
    db.session.commit()
    flash('Configuración guardada.', 'success')
    return redirect(url_for('bug_report.admin_config'))


# ---------------------------------------------------------------------------
# Submission endpoint (any authenticated admin)
# ---------------------------------------------------------------------------

def _rate_limited() -> bool:
    history = session.get('bug_report_times', [])
    now = time.time()
    history = [t for t in history if now - t < RATE_LIMIT_WINDOW]
    if len(history) >= RATE_LIMIT_MAX:
        return True
    history.append(now)
    session['bug_report_times'] = history
    return False


def _build_body(user_msg: str, what_doing: str) -> str:
    from models import Usuario, Configuracion
    version = get_version_info()
    git = (version or {}).get('git_info', {}) or {}

    current_url = (request.form.get('current_url') or request.referrer or '(desconocida)').strip()
    hostname = (request.form.get('current_hostname') or request.host or '(desconocido)').strip()

    user_id = session.get('user_id')
    usuario = Usuario.query.get(user_id) if user_id else None
    nombre_completo = f"{usuario.nombre} {usuario.apellido}" if usuario else '(desconocido)'

    cfg_escuela = Configuracion.query.filter_by(clave='nombre_escuela').first()
    nombre_escuela = cfg_escuela.valor if cfg_escuela else 'DarmaSala'

    ctx = {
        'url':             current_url,
        'hostname':        hostname,
        'user_agent':      request.user_agent.string,
        'version':         version.get('version', '?'),
        'build_date':      version.get('build_date', '?'),
        'commit':          git.get('commit_hash', '?'),
        'branch':          git.get('branch', '?'),
        'session_user':    session.get('username', '?'),
        'nombre_completo': nombre_completo,
        'session_rol':     session.get('rol', '?'),
        'escuela':         nombre_escuela,
        'timestamp':       datetime.utcnow().isoformat(timespec='seconds') + 'Z',
    }

    return (
        f"### Descripción\n{user_msg.strip() or '(sin descripción)'}\n\n"
        f"### ¿Qué estabas haciendo?\n{what_doing.strip() or '(no especificado)'}\n\n"
        f"### Contexto técnico\n"
        f"- **Escuela**: {ctx['escuela']}\n"
        f"- **Dominio**: `{ctx['hostname']}`\n"
        f"- **URL**: `{ctx['url']}`\n"
        f"- **Usuario**: {ctx['nombre_completo']} (`{ctx['session_user']}`, rol `{ctx['session_rol']}`)\n"
        f"- **Versión**: `{ctx['version']}` (build {ctx['build_date']})\n"
        f"- **Commit**: `{ctx['commit']}` — rama `{ctx['branch']}`\n"
        f"- **User-Agent**: `{ctx['user_agent']}`\n"
        f"- **Timestamp UTC**: `{ctx['timestamp']}`\n\n"
        f"_Reportado automáticamente desde la aplicación._"
    )


@bug_report_bp.route('/admin/bug-report/submit', methods=['POST'])
@login_required
@admin_required
def submit():
    cfg = load_config({c.clave: c.valor for c in Configuracion.query.all()})
    wants_json = request.headers.get('Accept', '').startswith('application/json') \
                 or request.is_json

    title = (request.form.get('title') or (request.get_json(silent=True) or {}).get('title', '')).strip()
    description = (request.form.get('description') or (request.get_json(silent=True) or {}).get('description', ''))
    what_doing = (request.form.get('what_doing') or (request.get_json(silent=True) or {}).get('what_doing', ''))

    if not title:
        msg = 'El título es obligatorio.'
        return (jsonify({'ok': False, 'error': msg}), 400) if wants_json else (flash(msg, 'error') or redirect(request.referrer or '/'))

    if _rate_limited():
        msg = 'Has reportado demasiados bugs en la última hora. Inténtalo más tarde.'
        return (jsonify({'ok': False, 'error': msg}), 429) if wants_json else (flash(msg, 'error') or redirect(request.referrer or '/'))

    if not cfg.configured:
        msg = 'El sistema de reportes no está configurado por el administrador.'
        return (jsonify({'ok': False, 'error': msg}), 503) if wants_json else (flash(msg, 'error') or redirect(request.referrer or '/'))

    try:
        issue = create_issue(cfg, title, _build_body(description, what_doing))
    except GitHubIssuesError as exc:
        current_app.logger.warning('Bug report failed: %s', exc)
        msg = f'No se pudo crear el issue: {exc}'
        return (jsonify({'ok': False, 'error': str(exc)}), 502) if wants_json else (flash(msg, 'error') or redirect(request.referrer or '/'))

    url = issue.get('html_url', '')
    number = issue.get('number', '?')
    if wants_json:
        return jsonify({'ok': True, 'url': url, 'number': number})
    flash(f'Bug reportado correctamente: issue #{number} — {url}', 'success')
    return redirect(request.referrer or url_for('main.index'))
