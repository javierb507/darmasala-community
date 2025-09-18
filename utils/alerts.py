"""
Sistema de alertas y notificaciones inteligentes
"""
from datetime import datetime, date, timedelta
from flask import flash

class AlertSystem:
    
    @staticmethod
    def check_payment_alerts(alumnos):
        """Verificar alertas de pagos pendientes"""
        alerts = []
        current_month = date.today().strftime('%Y-%m')
        
        for alumno in alumnos:
            if not alumno.activo:
                continue
                
            # Verificar matrícula
            if not alumno.matricula_pagada:
                alerts.append({
                    'type': 'warning',
                    'title': 'Matrícula Pendiente',
                    'message': f'{alumno.nombre} {alumno.apellido} no ha pagado la matrícula',
                    'alumno_id': alumno.id,
                    'priority': 'high'
                })
            
            # Verificar pago del mes actual
            pago_mes_actual = any(
                pago.mes == current_month and pago.tipo_pago == 'cuota' 
                for pago in alumno.pagos
            )
            
            if not pago_mes_actual:
                alerts.append({
                    'type': 'danger',
                    'title': 'Cuota Mensual Pendiente',
                    'message': f'{alumno.nombre} {alumno.apellido} no ha pagado la cuota de este mes',
                    'alumno_id': alumno.id,
                    'priority': 'medium'
                })
        
        return alerts
    
    @staticmethod
    def check_invoice_alerts(facturas):
        """Verificar alertas de facturas"""
        alerts = []
        today = date.today()
        
        for factura in facturas:
            if factura.estado == 'pendiente':
                # Facturas vencidas
                if factura.fecha_vencimiento and factura.fecha_vencimiento < today:
                    days_overdue = (today - factura.fecha_vencimiento).days
                    alerts.append({
                        'type': 'danger',
                        'title': 'Factura Vencida',
                        'message': f'Factura {factura.numero_factura} vencida hace {days_overdue} días',
                        'factura_id': factura.id,
                        'priority': 'high'
                    })
                
                # Facturas próximas a vencer (7 días)
                elif factura.fecha_vencimiento and factura.fecha_vencimiento <= today + timedelta(days=7):
                    days_to_due = (factura.fecha_vencimiento - today).days
                    alerts.append({
                        'type': 'warning',
                        'title': 'Factura Próxima a Vencer',
                        'message': f'Factura {factura.numero_factura} vence en {days_to_due} días',
                        'factura_id': factura.id,
                        'priority': 'medium'
                    })
        
        return alerts
    
    @staticmethod
    def check_system_alerts():
        """Verificar alertas del sistema"""
        alerts = []
        
        # Verificar si existe backup reciente (últimos 7 días)
        import os
        if os.path.exists('backups'):
            backup_files = [f for f in os.listdir('backups') if f.endswith('.zip')]
            if not backup_files:
                alerts.append({
                    'type': 'warning',
                    'title': 'Sin Backups',
                    'message': 'No se han encontrado backups recientes. Recomendamos crear uno.',
                    'priority': 'low',
                    'action': 'backup'
                })
        
        return alerts
    
    @staticmethod
    def get_all_alerts():
        """Obtener todas las alertas del sistema"""
        from app import Alumno, FacturaProveedor
        
        all_alerts = []
        
        # Alertas de pagos
        alumnos = Alumno.query.filter_by(activo=True).all()
        all_alerts.extend(AlertSystem.check_payment_alerts(alumnos))
        
        # Alertas de facturas
        facturas = FacturaProveedor.query.filter_by(estado='pendiente').all()
        all_alerts.extend(AlertSystem.check_invoice_alerts(facturas))
        
        # Alertas del sistema
        all_alerts.extend(AlertSystem.check_system_alerts())
        
        # Ordenar por prioridad
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        all_alerts.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return all_alerts
    
    @staticmethod
    def flash_alerts(limit=5):
        """Mostrar alertas como mensajes flash"""
        alerts = AlertSystem.get_all_alerts()
        
        for alert in alerts[:limit]:  # Limitar número de alertas
            flash(f"{alert['title']}: {alert['message']}", alert['type'])
        
        if len(alerts) > limit:
            flash(f"Y {len(alerts) - limit} alertas más...", 'info')
    
    @staticmethod
    def get_dashboard_summary():
        """Resumen de alertas para el dashboard"""
        alerts = AlertSystem.get_all_alerts()
        
        summary = {
            'total': len(alerts),
            'high': len([a for a in alerts if a['priority'] == 'high']),
            'medium': len([a for a in alerts if a['priority'] == 'medium']),
            'low': len([a for a in alerts if a['priority'] == 'low']),
            'recent': alerts[:3]  # 3 más recientes
        }
        
        return summary