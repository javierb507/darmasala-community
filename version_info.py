#!/usr/bin/env python3
"""
Script para obtener información de versión y Git
"""

import os
import re
import subprocess
from datetime import datetime
import json


def _redact_url(url):
    """Quita credenciales (user:token@) de la URL del remoto antes de guardar."""
    if not url:
        return url
    return re.sub(r'(https?://)[^@/]+@', r'\1', url)


def get_git_info():
    """Obtener información de Git"""
    try:
        # Obtener el hash del último commit
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], 
            cwd=os.path.dirname(__file__),
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()[:7]
        
        # Obtener la fecha del último commit
        commit_date = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cd', '--date=format:%Y-%m-%d %H:%M:%S'],
            cwd=os.path.dirname(__file__),
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        
        # Obtener el mensaje del último commit
        commit_message = subprocess.check_output(
            ['git', 'log', '-1', '--format=%s'],
            cwd=os.path.dirname(__file__),
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        
        # Obtener la rama actual
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=os.path.dirname(__file__),
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        
        # Obtener el repositorio remoto
        remote_url = subprocess.check_output(
            ['git', 'config', '--get', 'remote.origin.url'],
            cwd=os.path.dirname(__file__),
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        
        return {
            'commit_hash': commit_hash,
            'commit_date': commit_date,
            'commit_message': commit_message,
            'branch': branch,
            'remote_url': _redact_url(remote_url),
            'available': True
        }
    except:
        return {
            'commit_hash': 'unknown',
            'commit_date': 'unknown',
            'commit_message': 'Git info not available',
            'branch': 'unknown',
            'remote_url': 'unknown',
            'available': False
        }

def get_app_version():
    """Obtener versión de la aplicación"""
    # Versión basada en la fecha actual si no hay Git
    build_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    git_info = get_git_info()
    
    return {
        'version': '2.0.1-final',
        'build_date': build_date,
        'git_info': git_info,
        'app_name': 'DarmaSala',
        'description': 'Sistema de Gestión de Escuela de Yoga'
    }

def save_version_info():
    """Guardar información de versión en archivo JSON"""
    version_info = get_app_version()
    
    version_file = os.path.join(os.path.dirname(__file__), 'static', 'version.json')
    
    # Crear directorio static si no existe
    os.makedirs(os.path.dirname(version_file), exist_ok=True)
    
    with open(version_file, 'w', encoding='utf-8') as f:
        json.dump(version_info, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Información de versión guardada en {version_file}")
    return version_info

if __name__ == "__main__":
    info = save_version_info()
    print("\n📊 Información de Versión:")
    print(f"   🏷️  Versión: {info['version']}")
    print(f"   📅 Build: {info['build_date']}")
    if info['git_info']['available']:
        print(f"   🔗 Commit: {info['git_info']['commit_hash']}")
        print(f"   📝 Mensaje: {info['git_info']['commit_message']}")
        print(f"   🌿 Rama: {info['git_info']['branch']}")
        print(f"   📅 Fecha commit: {info['git_info']['commit_date']}")
    else:
        print("   ⚠️  Información de Git no disponible")
