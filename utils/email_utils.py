import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def _smtp_config():
    """Lee config SMTP: env vars tienen prioridad sobre Configuracion DB.
    SMTP_PASS es SIEMPRE env var (nunca se guarda en BD)."""
    try:
        from models import Configuracion
        cfg = {c.clave: c.valor for c in Configuracion.query.filter(
            Configuracion.clave.in_(['smtp_host', 'smtp_port', 'smtp_user', 'smtp_from', 'smtp_use_tls'])
        ).all()}
    except Exception:
        cfg = {}

    host = os.environ.get('SMTP_HOST') or cfg.get('smtp_host', '')
    port = int(os.environ.get('SMTP_PORT') or cfg.get('smtp_port') or 2525)
    user = os.environ.get('SMTP_USER') or cfg.get('smtp_user', '')
    from_addr = os.environ.get('SMTP_FROM') or cfg.get('smtp_from') or user
    password = os.environ.get('SMTP_PASS', '')
    use_tls_raw = os.environ.get('SMTP_USE_TLS') or cfg.get('smtp_use_tls', 'true')
    use_tls = str(use_tls_raw).lower() not in ('false', '0', 'no')

    return host, port, user, password, from_addr, use_tls


def enviar_email(destinatario: str, asunto: str, cuerpo_html: str,
                 cuerpo_texto: str = None, remitente: str = None) -> tuple[bool, str]:
    """Envía email via SMTP. Retorna (ok, mensaje_error)."""
    host, port, user, password, from_addr, use_tls = _smtp_config()

    if remitente:
        from_addr = remitente

    if not host or not user:
        return False, 'SMTP no configurado (faltan smtp_host y smtp_user)'
    if not password:
        return False, 'SMTP_PASS no definida en variables de entorno del servidor'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = asunto
    msg['From'] = from_addr
    msg['To'] = destinatario

    if cuerpo_texto:
        msg.attach(MIMEText(cuerpo_texto, 'plain', 'utf-8'))
    msg.attach(MIMEText(cuerpo_html, 'html', 'utf-8'))

    try:
        if use_tls:
            server = smtplib.SMTP(host, port, timeout=15)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(host, port, timeout=15)
        server.login(user, password)
        server.sendmail(from_addr, [destinatario], msg.as_string())
        server.quit()
        return True, ''
    except smtplib.SMTPAuthenticationError:
        return False, 'Credenciales SMTP incorrectas (usuario/contraseña)'
    except smtplib.SMTPConnectError:
        return False, f'No se pudo conectar a {host}:{port}'
    except Exception as e:
        return False, str(e)


def smtp_configurado() -> bool:
    host, _, user, password, _, _ = _smtp_config()
    return bool(host and user and password)


RECORDATORIO_ASUNTO_DEFAULT = 'Recordatorio de pago pendiente — {escuela}'
RECORDATORIO_PLANTILLA_DEFAULT = (
    '<p>Hola {nombre},</p>'
    '<p>Te recordamos que tienes pendiente el pago de: <strong>{periodos}</strong>.</p>'
    '<p>Importe pendiente: <strong>{deuda}</strong>.</p>'
    '<p>Puedes regularizarlo en recepción. Si ya lo has abonado, ignora este mensaje.</p>'
    '<p>Gracias,<br>{escuela}</p>')


def componer_recordatorio(alumno, hoy=None):
    """(asunto, cuerpo_html) del recordatorio de impago para un alumno."""
    from models import Configuracion
    from utils.finance_utils import periodos_pendientes

    pendientes = periodos_pendientes(alumno, hoy)
    cfg = {c.clave: c.valor for c in Configuracion.query.filter(
        Configuracion.clave.in_(['recordatorio_asunto', 'recordatorio_plantilla',
                                 'nombre_escuela'])).all()}
    valores = {
        'nombre': alumno.nombre,
        'periodos': ', '.join(p.nombre_corto for p in pendientes),
        'deuda': f'{alumno.get_precio_cuota() * len(pendientes):.2f} €',
        'escuela': cfg.get('nombre_escuela', 'DarmaSala'),
    }
    # El cuerpo es HTML: escapar el nombre (dato de usuario); el asunto es texto plano
    from markupsafe import escape
    valores_html = dict(valores, nombre=str(escape(alumno.nombre)))
    asunto_tpl = cfg.get('recordatorio_asunto') or RECORDATORIO_ASUNTO_DEFAULT
    cuerpo_tpl = cfg.get('recordatorio_plantilla') or RECORDATORIO_PLANTILLA_DEFAULT
    try:
        asunto = asunto_tpl.format(**valores)
    except (KeyError, IndexError, ValueError):
        asunto = asunto_tpl
    try:
        cuerpo = cuerpo_tpl.format(**valores_html)
    except (KeyError, IndexError, ValueError):
        cuerpo = cuerpo_tpl
    # Un salto de línea en el asunto permitiría inyectar cabeceras SMTP
    return asunto.replace('\n', ' ').replace('\r', ' '), cuerpo
