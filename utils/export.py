"""
Sistema de exportación mejorado con múltiples formatos
"""
import csv
import json
from datetime import datetime
from io import StringIO, BytesIO
import os

class ExportManager:
    
    @staticmethod
    def export_alumnos_csv(alumnos):
        """Exportar alumnos a CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Cabeceras
        writer.writerow([
            'ID', 'Nombre', 'Apellido', 'Email', 'Teléfono', 
            'Fecha Nacimiento', 'Dirección', 'Condiciones Médicas',
            'Tipo Cuota', 'Matrícula Pagada', 'Fecha Matrícula',
            'Fecha Registro', 'Activo'
        ])
        
        # Datos
        for alumno in alumnos:
            writer.writerow([
                alumno.id,
                alumno.nombre,
                alumno.apellido,
                alumno.email,
                alumno.telefono or '',
                alumno.fecha_nacimiento.strftime('%Y-%m-%d') if alumno.fecha_nacimiento else '',
                alumno.direccion or '',
                alumno.condiciones_medicas or '',
                alumno.get_tipo_cuota_display(),
                'Sí' if alumno.matricula_pagada else 'No',
                alumno.fecha_matricula.strftime('%Y-%m-%d') if alumno.fecha_matricula else '',
                alumno.fecha_registro.strftime('%Y-%m-%d %H:%M'),
                'Activo' if alumno.activo else 'Inactivo'
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_pagos_csv(pagos):
        """Exportar pagos a CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Cabeceras
        writer.writerow([
            'ID', 'Alumno', 'Mes/Año', 'Monto', 'Tipo Pago', 
            'Descripción', 'Fecha Creación'
        ])
        
        # Datos
        for pago in pagos:
            alumno_nombre = f"{pago.alumno.nombre} {pago.alumno.apellido}"
            mes_año = pago.mes if pago.mes else f"Año {pago.año}" if pago.año else "N/A"
            
            writer.writerow([
                pago.id,
                alumno_nombre,
                mes_año,
                f"{pago.monto:.2f}€",
                pago.tipo_pago.title(),
                pago.descripcion or '',
                pago.fecha_creacion.strftime('%Y-%m-%d %H:%M')
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_facturas_csv(facturas):
        """Exportar facturas a CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Cabeceras
        writer.writerow([
            'ID', 'Número Factura', 'Proveedor', 'Categoría', 'Fecha Factura',
            'Fecha Vencimiento', 'Importe Sin IVA', 'IVA %', 'Importe Total',
            'Estado', 'Fecha Pago', 'Método Pago', 'Descripción'
        ])
        
        # Datos
        for factura in facturas:
            writer.writerow([
                factura.id,
                factura.numero_factura,
                factura.proveedor.nombre,
                factura.categoria.nombre,
                factura.fecha_factura.strftime('%Y-%m-%d'),
                factura.fecha_vencimiento.strftime('%Y-%m-%d') if factura.fecha_vencimiento else '',
                f"{factura.importe_sin_iva:.2f}€",
                f"{factura.iva:.1f}%",
                f"{factura.importe_total:.2f}€",
                factura.estado.title(),
                factura.fecha_pago.strftime('%Y-%m-%d') if factura.fecha_pago else '',
                factura.metodo_pago or '',
                factura.descripcion or ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_asistencias_csv(asistencias):
        """Exportar asistencias a CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Cabeceras
        writer.writerow([
            'ID', 'Alumno', 'Clase', 'Día', 'Horario', 'Fecha Clase',
            'Presente', 'Observaciones', 'Fecha Registro'
        ])
        
        # Datos
        for asistencia in asistencias:
            alumno_nombre = f"{asistencia.alumno.nombre} {asistencia.alumno.apellido}"
            horario = f"{asistencia.horario.hora_inicio.strftime('%H:%M')} - {asistencia.horario.hora_fin.strftime('%H:%M')}"
            
            writer.writerow([
                asistencia.id,
                alumno_nombre,
                asistencia.horario.clase.nombre,
                asistencia.horario.get_dia_display(),
                horario,
                asistencia.fecha_clase.strftime('%Y-%m-%d'),
                'Sí' if asistencia.presente else 'No',
                asistencia.observaciones or '',
                asistencia.fecha_registro.strftime('%Y-%m-%d %H:%M')
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_alumnos_json(alumnos):
        """Exportar alumnos a JSON"""
        data = []
        for alumno in alumnos:
            alumno_data = alumno.to_dict()
            # Añadir información de pagos
            alumno_data['pagos'] = [pago.to_dict() for pago in alumno.pagos]
            data.append(alumno_data)
        
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)
    
    @staticmethod
    def create_backup_export():
        """Crear exportación completa para backup"""
        from app import Alumno, Pago, FacturaProveedor, Asistencia, Configuracion
        
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.2.6 version 1',
            'alumnos': [],
            'pagos': [],
            'facturas': [],
            'asistencias': [],
            'configuracion': []
        }
        
        # Exportar alumnos
        alumnos = Alumno.query.all()
        backup_data['alumnos'] = [alumno.to_dict() for alumno in alumnos]
        
        # Exportar pagos
        pagos = Pago.query.all()
        backup_data['pagos'] = [pago.to_dict() for pago in pagos]
        
        # Exportar facturas
        facturas = FacturaProveedor.query.all()
        backup_data['facturas'] = [
            {
                'id': f.id,
                'numero_factura': f.numero_factura,
                'proveedor_nombre': f.proveedor.nombre,
                'categoria_nombre': f.categoria.nombre,
                'fecha_factura': f.fecha_factura.isoformat(),
                'importe_total': f.importe_total,
                'estado': f.estado
            } for f in facturas
        ]
        
        # Exportar asistencias
        asistencias = Asistencia.query.all()
        backup_data['asistencias'] = [asistencia.to_dict() for asistencia in asistencias]
        
        # Exportar configuración
        configuraciones = Configuracion.query.all()
        backup_data['configuracion'] = [config.to_dict() for config in configuraciones]
        
        return json.dumps(backup_data, indent=2, ensure_ascii=False, default=str)
    
    @staticmethod
    def generate_filename(base_name, extension='csv'):
        """Generar nombre de archivo con timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{base_name}_{timestamp}.{extension}"
    
    @staticmethod
    def get_export_stats():
        """Obtener estadísticas de exportación"""
        from app import Alumno, Pago, FacturaProveedor, Asistencia
        
        return {
            'alumnos_activos': Alumno.query.filter_by(activo=True).count(),
            'alumnos_total': Alumno.query.count(),
            'pagos_total': Pago.query.count(),
            'facturas_total': FacturaProveedor.query.count(),
            'asistencias_total': Asistencia.query.count(),
            'last_export': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }