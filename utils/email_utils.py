import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def enviar_email(destinatario: str, asunto: str, cuerpo_html: str,
                 cuerpo_texto: str = None, remitente: str = None) -> bool:
    """Envía email via SMTP. Requiere SMTP_HOST y SMTP_USER en env. Retorna True si OK."""
    host = os.environ.get('SMTP_HOST', '')
    port = int(os.environ.get('SMTP_PORT', '587'))
    user = os.environ.get('SMTP_USER', '')
    password = os.environ.get('SMTP_PASS', '')
    use_tls = os.environ.get('SMTP_USE_TLS', 'true').lower() != 'false'

    if not host or not user:
        return False

    from_addr = remitente or user

    msg = MIMEMultipart('alternative')
    msg['Subject'] = asunto
    msg['From'] = from_addr
    msg['To'] = destinatario

    if cuerpo_texto:
        msg.attach(MIMEText(cuerpo_texto, 'plain', 'utf-8'))
    msg.attach(MIMEText(cuerpo_html, 'html', 'utf-8'))

    try:
        if use_tls:
            server = smtplib.SMTP(host, port, timeout=10)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(host, port, timeout=10)
        server.login(user, password)
        server.sendmail(from_addr, [destinatario], msg.as_string())
        server.quit()
        return True
    except Exception:
        return False


def smtp_configurado() -> bool:
    return bool(os.environ.get('SMTP_HOST') and os.environ.get('SMTP_USER'))


def generate_reset_token(email: str) -> str:
    from itsdangerous import URLSafeTimedSerializer
    from flask import current_app
    s = URLSafeTimedSerializer(current_app.secret_key)
    return s.dumps(email, salt='darmasala-password-reset')


def verify_reset_token(token: str, max_age: int = 1800):
    """Retorna el email si el token es válido y no ha expirado, None si no."""
    from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
    from flask import current_app
    s = URLSafeTimedSerializer(current_app.secret_key)
    try:
        return s.loads(token, salt='darmasala-password-reset', max_age=max_age)
    except (SignatureExpired, BadSignature):
        return None
