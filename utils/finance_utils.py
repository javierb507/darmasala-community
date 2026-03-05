from datetime import date, timedelta, datetime
import os
from flask import flash, redirect, url_for, make_response
from models import Pago

def exportar_facturas_excel(facturas):
    """Exportar facturas a Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        
        data = []
        for factura in facturas:
            data.append({
                'Número Factura': factura.numero_factura,
                'Proveedor': factura.proveedor.nombre,
                'Categoría': factura.categoria.nombre,
                'Fecha Factura': factura.fecha_factura.strftime('%d/%m/%Y'),
                'Fecha Vencimiento': factura.fecha_vencimiento.strftime('%d/%m/%Y') if factura.fecha_vencimiento else '',
                'Importe sin IVA': factura.importe_sin_iva,
                'IVA %': factura.iva,
                'Importe Total': factura.importe_total,
                'Estado': factura.estado.title(),
                'Fecha Pago': factura.fecha_pago.strftime('%d/%m/%Y') if factura.fecha_pago else '',
                'Método Pago': factura.metodo_pago or '',
                'Descripción': factura.descripcion or '',
                'Notas': factura.notas or ''
            })
        
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Facturas', index=False)
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=facturas_{date.today().strftime("%Y%m%d")}.xlsx'
        
        return response
        
    except ImportError:
        flash('Error: pandas y openpyxl no están instalados. Instale con: pip install pandas openpyxl', 'error')
        return redirect(url_for('finance.facturas'))
    except Exception as e:
        flash(f'Error al exportar facturas: {str(e)}', 'error')
        return redirect(url_for('finance.facturas'))

def exportar_gastos_fijos_excel(gastos):
    """Exportar gastos fijos a Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        
        data = []
        for gasto in gastos:
            data.append({
                'Nombre': gasto.nombre,
                'Descripción': gasto.descripcion or '',
                'Categoría': gasto.categoria.nombre,
                'Importe': gasto.importe,
                'Frecuencia': gasto.frecuencia.title(),
                'Día de Cargo': gasto.dia_cargo,
                'Fecha Inicio': gasto.fecha_inicio.strftime('%d/%m/%Y'),
                'Fecha Fin': gasto.fecha_fin.strftime('%d/%m/%Y') if gasto.fecha_fin else '',
                'Activo': 'Sí' if gasto.activo else 'No',
                'Notas': gasto.notas or ''
            })
        
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Gastos Fijos', index=False)
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=gastos_fijos_{date.today().strftime("%Y%m%d")}.xlsx'
        
        return response
        
    except ImportError:
        flash('Error: pandas y openpyxl no están instalados. Instale con: pip install pandas openpyxl', 'error')
        return redirect(url_for('finance.gastos_fijos'))
    except Exception as e:
        flash(f'Error al exportar gastos fijos: {str(e)}', 'error')
        return redirect(url_for('finance.gastos_fijos'))

def exportar_proveedores_excel(proveedores):
    """Exportar proveedores a Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        
        data = []
        for proveedor in proveedores:
            data.append({
                'Nombre': proveedor.nombre,
                'CIF/NIF': proveedor.cif_nif or '',
                'Dirección': proveedor.direccion or '',
                'Teléfono': proveedor.telefono or '',
                'Email': proveedor.email or '',
                'Contacto Principal': proveedor.contacto_principal or '',
                'Activo': 'Sí' if proveedor.activo else 'No',
                'Fecha Registro': proveedor.fecha_registro.strftime('%d/%m/%Y'),
                'Notas': proveedor.notas or ''
            })
        
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Proveedores', index=False)
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=proveedores_{date.today().strftime("%Y%m%d")}.xlsx'
        
        return response
        
    except ImportError:
        flash('Error: pandas y openpyxl no están instalados. Instale con: pip install pandas openpyxl', 'error')
        return redirect(url_for('finance.proveedores'))
    except Exception as e:
        flash(f'Error al exportar proveedores: {str(e)}', 'error')
        return redirect(url_for('finance.proveedores'))

def exportar_ingresos_excel():
    """Exportar ingresos a Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        
        # Obtener ingresos de los últimos 12 meses
        fecha_inicio = date.today() - timedelta(days=365)
        fecha_fin = date.today()
        
        pagos = Pago.query.filter(
            Pago.fecha_creacion >= fecha_inicio,
            Pago.fecha_creacion <= fecha_fin
        ).order_by(Pago.fecha_creacion.desc()).all()
        
        data = []
        for pago in pagos:
            data.append({
                'Fecha': pago.fecha_creacion.strftime('%d/%m/%Y'),
                'Alumno': f"{pago.alumno.nombre} {pago.alumno.apellido}",
                'Tipo Pago': pago.tipo_pago.title(),
                'Mes/Año': pago.mes or f"{pago.año}" if pago.año else '',
                'Fecha Clase': pago.fecha_clase.strftime('%d/%m/%Y') if pago.fecha_clase else '',
                'Monto': pago.monto,
                'Método Pago': pago.metodo_pago or '',
                'Descripción': pago.descripcion or ''
            })
        
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Ingresos', index=False)
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=ingresos_{date.today().strftime("%Y%m%d")}.xlsx'
        
        return response
        
    except ImportError:
        flash('Error: pandas y openpyxl no están instalados. Instale con: pip install pandas openpyxl', 'error')
        return redirect(url_for('finance.economia_historico'))
    except Exception as e:
        flash(f'Error al exportar ingresos: {str(e)}', 'error')
        return redirect(url_for('finance.economia_historico'))

def generar_reporte_pdf(facturas, gastos_fijos, ingresos, fecha_inicio, fecha_fin):
    """Generar reporte de contabilidad en PDF"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        
        # Título
        story.append(Paragraph("REPORTE DE CONTABILIDAD", title_style))
        story.append(Paragraph(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Resumen financiero
        total_facturas = sum(f.importe_total for f in facturas)
        total_gastos_fijos = sum(g.importe for g in gastos_fijos)
        balance = ingresos - total_facturas - total_gastos_fijos
        
        resumen_data = [
            ['Concepto', 'Importe (€)'],
            ['Ingresos Totales', f"{ingresos:.2f}"],
            ['Gastos en Facturas', f"{total_facturas:.2f}"],
            ['Gastos Fijos', f"{total_gastos_fijos:.2f}"],
            ['BALANCE', f"{balance:.2f}"]
        ]
        
        resumen_table = Table(resumen_data)
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        story.append(Paragraph("RESUMEN FINANCIERO", styles['Heading2']))
        story.append(resumen_table)
        story.append(Spacer(1, 20))
        
        # Facturas
        if facturas:
            story.append(Paragraph("FACTURAS DEL PERÍODO", styles['Heading2']))
            facturas_data = [['Número', 'Proveedor', 'Fecha', 'Importe', 'Estado']]
            for factura in facturas:
                facturas_data.append([
                    factura.numero_factura,
                    factura.proveedor.nombre,
                    factura.fecha_factura.strftime('%d/%m/%Y'),
                    f"{factura.importe_total:.2f}",
                    factura.estado.title()
                ])
            
            facturas_table = Table(facturas_data)
            facturas_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(facturas_table)
            story.append(Spacer(1, 20))
        
        # Gastos fijos
        if gastos_fijos:
            story.append(Paragraph("GASTOS FIJOS", styles['Heading2']))
            gastos_data = [['Nombre', 'Categoría', 'Importe', 'Frecuencia']]
            for gasto in gastos_fijos:
                gastos_data.append([
                    gasto.nombre,
                    gasto.categoria.nombre,
                    f"{gasto.importe:.2f}",
                    gasto.frecuencia.title()
                ])
            
            gastos_table = Table(gastos_data)
            gastos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(gastos_table)
        
        doc.build(story)
        
        buffer.seek(0)
        
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=reporte_{date.today().strftime("%Y%m%d")}.pdf'
        
        return response
    except Exception as e:
        flash(f"Error al generar reporte PDF: {e}", "error")
        return redirect(url_for('finance.economia_historico'))
