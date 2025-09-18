"""
Sistema de backup automático para la base de datos
"""
import os
import shutil
import sqlite3
from datetime import datetime, timedelta
import zipfile
import logging

class BackupManager:
    def __init__(self, db_path='yoga_school.db', backup_dir='backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.ensure_backup_dir()
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def ensure_backup_dir(self):
        """Crear directorio de backups si no existe"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self):
        """Crear backup de la base de datos"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'yoga_school_backup_{timestamp}.db'
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Crear backup usando SQLite backup API
            if os.path.exists(self.db_path):
                source_conn = sqlite3.connect(self.db_path)
                backup_conn = sqlite3.connect(backup_path)
                
                source_conn.backup(backup_conn)
                
                source_conn.close()
                backup_conn.close()
                
                # Comprimir el backup
                zip_path = backup_path.replace('.db', '.zip')
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(backup_path, backup_filename)
                
                # Eliminar archivo sin comprimir
                os.remove(backup_path)
                
                self.logger.info(f"Backup creado exitosamente: {zip_path}")
                return zip_path
            else:
                self.logger.warning(f"Base de datos no encontrada: {self.db_path}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error al crear backup: {str(e)}")
            return None
    
    def restore_backup(self, backup_path):
        """Restaurar backup de la base de datos"""
        try:
            if not os.path.exists(backup_path):
                self.logger.error(f"Archivo de backup no encontrado: {backup_path}")
                return False
            
            # Crear backup de la base actual antes de restaurar
            current_backup = self.create_backup()
            if current_backup:
                self.logger.info(f"Backup de seguridad creado: {current_backup}")
            
            # Extraer y restaurar
            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(self.backup_dir)
                    extracted_files = zipf.namelist()
                    if extracted_files:
                        extracted_db = os.path.join(self.backup_dir, extracted_files[0])
                        shutil.copy2(extracted_db, self.db_path)
                        os.remove(extracted_db)
            else:
                shutil.copy2(backup_path, self.db_path)
            
            self.logger.info(f"Base de datos restaurada desde: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al restaurar backup: {str(e)}")
            return False
    
    def cleanup_old_backups(self, retention_days=30):
        """Eliminar backups antiguos"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            deleted_count = 0
            
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('yoga_school_backup_') and filename.endswith('.zip'):
                    file_path = os.path.join(self.backup_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        deleted_count += 1
                        self.logger.info(f"Backup eliminado: {filename}")
            
            self.logger.info(f"Limpieza completada. {deleted_count} backups eliminados.")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error en limpieza de backups: {str(e)}")
            return 0
    
    def list_backups(self):
        """Listar todos los backups disponibles"""
        backups = []
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('yoga_school_backup_') and filename.endswith('.zip'):
                    file_path = os.path.join(self.backup_dir, filename)
                    file_size = os.path.getsize(file_path)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    backups.append({
                        'filename': filename,
                        'path': file_path,
                        'size': file_size,
                        'created': file_time,
                        'size_mb': round(file_size / (1024 * 1024), 2)
                    })
            
            # Ordenar por fecha de creación (más reciente primero)
            backups.sort(key=lambda x: x['created'], reverse=True)
            return backups
            
        except Exception as e:
            self.logger.error(f"Error al listar backups: {str(e)}")
            return []
    
    def get_backup_info(self):
        """Obtener información general de backups"""
        backups = self.list_backups()
        total_size = sum(backup['size'] for backup in backups)
        
        return {
            'count': len(backups),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'latest': backups[0] if backups else None,
            'oldest': backups[-1] if backups else None
        }

# Función de conveniencia para crear backup rápido
def create_quick_backup():
    """Crear un backup rápido"""
    backup_manager = BackupManager()
    return backup_manager.create_backup()

# Función para programar backups automáticos (se puede usar con cron o scheduler)
def scheduled_backup():
    """Función para backups programados"""
    backup_manager = BackupManager()
    
    # Crear backup
    backup_path = backup_manager.create_backup()
    
    # Limpiar backups antiguos
    if backup_path:
        backup_manager.cleanup_old_backups(retention_days=30)
    
    return backup_path