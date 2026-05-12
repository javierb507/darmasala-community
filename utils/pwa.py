"""Utilidades PWA: genera iconos a partir del logo y resuelve el dominio del portal."""

import os
from urllib.parse import urlparse

from flask import current_app, request
from PIL import Image


ICON_SIZES = (192, 512)
MASKABLE_PADDING = 0.18  # 18% safe zone


def _logo_source():
    """Localiza el logo origen para generar iconos PWA."""
    static_dir = os.path.join(current_app.root_path, 'static')
    candidates = [
        os.path.join(static_dir, 'img', 'logo_darmasala.png'),
        os.path.join(static_dir, 'img', 'logo.png'),
        os.path.join(static_dir, 'images', 'logo_darmasala.jpg'),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def _icons_dir():
    path = os.path.join(current_app.root_path, 'static', 'icons')
    os.makedirs(path, exist_ok=True)
    return path


def ensure_icons():
    """Genera los iconos PNG en static/icons/ si no existen.

    Crea:
      - icon-192.png, icon-512.png (cualquier propósito)
      - icon-192-maskable.png, icon-512-maskable.png (safe-zone)
    """
    src = _logo_source()
    if not src:
        return False

    icons_dir = _icons_dir()
    work_needed = False
    expected = []
    for size in ICON_SIZES:
        expected.append((size, False, os.path.join(icons_dir, f'icon-{size}.png')))
        expected.append((size, True,  os.path.join(icons_dir, f'icon-{size}-maskable.png')))

    for _, _, dest in expected:
        if not os.path.exists(dest):
            work_needed = True
            break
    if not work_needed:
        return True

    try:
        with Image.open(src) as base:
            base = base.convert('RGBA')
            for size, maskable, dest in expected:
                if os.path.exists(dest):
                    continue
                _render_icon(base, size, maskable, dest)
    except Exception as exc:
        current_app.logger.warning('No se pudieron generar iconos PWA: %s', exc)
        return False
    return True


def _render_icon(base_rgba, size, maskable, dest_path):
    canvas = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    if maskable:
        inner = int(size * (1 - 2 * MASKABLE_PADDING))
    else:
        inner = size
    logo = base_rgba.copy()
    logo.thumbnail((inner, inner), Image.LANCZOS)
    x = (size - logo.width) // 2
    y = (size - logo.height) // 2
    canvas.paste(logo, (x, y), logo if logo.mode == 'RGBA' else None)
    canvas.save(dest_path, 'PNG', optimize=True)


def get_app_domain(config_dict):
    """Devuelve el dominio configurado del portal o None si no hay uno usable.

    Prioridad: configuración explícita 'dominio_portal' → request host.
    """
    raw = (config_dict or {}).get('dominio_portal') or ''
    raw = raw.strip()
    if raw:
        if not raw.startswith(('http://', 'https://')):
            raw = 'https://' + raw
        return raw.rstrip('/')
    # Fallback: request actual
    if request:
        return request.host_url.rstrip('/')
    return None


def is_local(url):
    """Decide si una URL apunta a localhost/loopback (PWA no instalable allí)."""
    if not url:
        return True
    try:
        host = urlparse(url).hostname or ''
    except Exception:
        return True
    return host in ('localhost', '127.0.0.1', '0.0.0.0') or host.endswith('.local')
