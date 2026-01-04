"""
Módulo para generar PDFs de facturas
Utiliza ReportLab para crear facturas profesionales en formato PDF
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime


class FacturaPDFGenerator:
    """Generador de PDFs para facturas emitidas"""

    def __init__(self):
        self.width, self.height = A4
        self.margin = 20 * mm

    def generar_factura(self, factura, config_fiscal):
        """
        Genera un PDF de factura

        Args:
            factura: Objeto FacturaEmitida con sus líneas
            config_fiscal: Objeto ConfiguracionFiscal con datos de la empresa

        Returns:
            BytesIO con el contenido del PDF
        """
        buffer = BytesIO()

        # Crear el documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )

        # Contenedor de elementos
        story = []

        # Estilos
        styles = getSampleStyleSheet()

        # Estilo personalizado para el título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#8B5FBF'),
            spaceAfter=30,
            alignment=1  # Centro
        )

        # Estilo para datos de empresa
        empresa_style = ParagraphStyle(
            'Empresa',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6f4a99'),
            alignment=2  # Derecha
        )

        # Título
        title = Paragraph("FACTURA", title_style)
        story.append(title)
        story.append(Spacer(1, 10 * mm))

        # Cabecera con datos de empresa y cliente
        cabecera_data = [
            ['DATOS DE LA EMPRESA', 'DATOS DEL CLIENTE'],
            [
                Paragraph(f"<b>{config_fiscal.nombre_empresa}</b><br/>"
                         f"NIF: {config_fiscal.nif}<br/>"
                         f"{config_fiscal.direccion_fiscal}<br/>"
                         f"{config_fiscal.codigo_postal or ''} {config_fiscal.ciudad or ''}<br/>"
                         f"{config_fiscal.provincia or ''}", styles['Normal']),
                Paragraph(f"<b>{factura.cliente.nombre}</b><br/>"
                         f"NIF/CIF: {factura.cliente.nif_cif}<br/>"
                         f"{factura.cliente.direccion or ''}<br/>"
                         f"{factura.cliente.codigo_postal or ''} {factura.cliente.ciudad or ''}",
                         styles['Normal'])
            ]
        ]

        cabecera_table = Table(cabecera_data, colWidths=[85 * mm, 85 * mm])
        cabecera_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B5FBF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 1), (-1, -1), 10),
            ('RIGHTPADDING', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ]))

        story.append(cabecera_table)
        story.append(Spacer(1, 10 * mm))

        # Datos de la factura
        factura_info_data = [
            ['Número de Factura:', f"{factura.serie}/{factura.numero:04d}"],
            ['Fecha de Emisión:', factura.fecha_emision.strftime('%d/%m/%Y')],
            ['Fecha de Vencimiento:', factura.fecha_vencimiento.strftime('%d/%m/%Y')],
            ['Estado:', factura.estado.upper()],
        ]

        factura_info_table = Table(factura_info_data, colWidths=[60 * mm, 50 * mm])
        factura_info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        story.append(factura_info_table)
        story.append(Spacer(1, 10 * mm))

        # Líneas de factura
        lineas_header = ['Descripción', 'Cantidad', 'Precio Unit.', 'Subtotal']
        lineas_data = [lineas_header]

        for linea in factura.lineas:
            lineas_data.append([
                linea.descripcion,
                str(linea.cantidad),
                f"{linea.precio_unitario:.2f} €",
                f"{linea.subtotal:.2f} €"
            ])

        lineas_table = Table(lineas_data, colWidths=[90 * mm, 30 * mm, 30 * mm, 30 * mm])
        lineas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B5FBF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('LEFTPADDING', (0, 1), (-1, -1), 5),
            ('RIGHTPADDING', (0, 1), (-1, -1), 5),
        ]))

        story.append(lineas_table)
        story.append(Spacer(1, 10 * mm))

        # Totales
        totales_data = []

        # Base imponible
        totales_data.append(['Base Imponible:', f"{factura.base_imponible:.2f} €"])

        # IVA o exención
        if factura.exenta_iva:
            totales_data.append([
                Paragraph(f"<b>IVA (Exento)</b><br/><font size=7>{config_fiscal.texto_exencion_iva or 'Exento de IVA'}</font>",
                         styles['Normal']),
                "0.00 €"
            ])
        else:
            totales_data.append([f'IVA ({factura.tipo_iva}%):', f"{factura.cuota_iva:.2f} €"])

        # Retención si aplica
        if factura.tipo_retencion > 0:
            totales_data.append([
                f'Retención IRPF ({factura.tipo_retencion}%):',
                f"-{factura.cuota_retencion:.2f} €"
            ])

        # Total
        totales_data.append(['', ''])  # Línea en blanco
        totales_data.append([Paragraph('<b>TOTAL A PAGAR:</b>', styles['Normal']),
                            Paragraph(f'<b>{factura.total:.2f} €</b>', styles['Normal'])])

        totales_table = Table(totales_data, colWidths=[120 * mm, 50 * mm])
        totales_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#8B5FBF')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0e6ff')),
            ('TOPPADDING', (0, -1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -2), 3),
        ]))

        story.append(totales_table)
        story.append(Spacer(1, 15 * mm))

        # Método de pago
        if factura.metodo_pago:
            metodo_pago_text = Paragraph(
                f"<b>Método de pago:</b> {factura.metodo_pago.capitalize()}",
                styles['Normal']
            )
            story.append(metodo_pago_text)
            story.append(Spacer(1, 5 * mm))

        # Observaciones
        if factura.observaciones:
            obs_title = Paragraph("<b>Observaciones:</b>", styles['Normal'])
            story.append(obs_title)
            obs_text = Paragraph(factura.observaciones, styles['Normal'])
            story.append(obs_text)
            story.append(Spacer(1, 10 * mm))

        # Pie de página
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1  # Centro
        )

        footer_text = Paragraph(
            f"{config_fiscal.nombre_empresa} - NIF: {config_fiscal.nif}<br/>"
            f"{config_fiscal.direccion_fiscal}, {config_fiscal.codigo_postal} {config_fiscal.ciudad}",
            footer_style
        )
        story.append(footer_text)

        # Generar PDF
        doc.build(story)

        # Volver al inicio del buffer
        buffer.seek(0)
        return buffer


def generar_pdf_factura(factura, config_fiscal):
    """
    Función helper para generar un PDF de factura

    Args:
        factura: Objeto FacturaEmitida
        config_fiscal: Objeto ConfiguracionFiscal

    Returns:
        BytesIO con el contenido del PDF
    """
    generator = FacturaPDFGenerator()
    return generator.generar_factura(factura, config_fiscal)
