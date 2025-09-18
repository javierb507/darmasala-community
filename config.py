"""
Configuración de la aplicación Atma suddhi
"""
import os
from datetime import timedelta

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'atma-suddhi-yoga-management-2025-secure-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de la aplicación
    APP_NAME = 'Atma suddhi - Gestión de Escuela de Yoga'
    APP_VERSION = '1.1.0'
    
    # Configuración de base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///yoga_school.db'
    
    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo para archivos
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    
    # Configuración de email (para futuras notificaciones)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configuración de precios por defecto
    PRECIOS_DEFAULT = {
        'clase_suelta': 15.00,
        '1_clase_semanal': 40.00,
        '2_clases_semanal': 70.00,
        'plana': 90.00,
        '1_clase_bimensual': 75.00,
        '2_clases_bimensual': 135.00,
        'matricula': 25.00
    }
    
    # Configuración de backup
    BACKUP_ENABLED = True
    BACKUP_INTERVAL_DAYS = 7
    BACKUP_RETENTION_DAYS = 30

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Cambiar a True para ver queries SQL

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # Configuración de seguridad adicional para producción
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}