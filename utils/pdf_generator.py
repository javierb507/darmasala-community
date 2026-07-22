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


class FichaAlumnoPDFGenerator:
    """Generador de PDFs con la ficha completa de un alumno"""

    COLOR_CABECERA = colors.HexColor('#8B5FBF')

    def __init__(self):
        self.width, self.height = A4
        self.margin = 20 * mm

    def _tabla_seccion(self, titulo, filas, col_widths):
        """Tabla con cabecera de sección al estilo de las facturas."""
        data = [[titulo] + [''] * (len(col_widths) - 1)] + filas
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('SPAN', (0, 0), (-1, 0)),
            ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_CABECERA),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('LEFTPADDING', (0, 1), (-1, -1), 6),
            ('RIGHTPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        return table

    def generar_ficha(self, alumno, datos):
        """
        Genera un PDF con la ficha completa del alumno

        Args:
            alumno: Objeto Alumno
            datos: dict con los datos ya calculados (sin acceso a BD):
                nombre_escuela, pagos, pendientes, deuda, total_asistencias,
                asistencias_presente, porcentaje_asistencia,
                asistencias_por_mes, bonos

        Returns:
            BytesIO con el contenido del PDF
        """
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )

        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'FichaTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=self.COLOR_CABECERA,
            spaceAfter=5,
            alignment=1  # Centro
        )
        subtitle_style = ParagraphStyle(
            'FichaSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=1
        )

        # Cabecera
        story.append(Paragraph("FICHA DE ALUMNO", title_style))
        story.append(Paragraph(
            f"{datos['nombre_escuela']} — Generada el {datetime.now().strftime('%d/%m/%Y')}",
            subtitle_style))
        story.append(Spacer(1, 8 * mm))

        # Datos personales y de contacto
        fmt_fecha = lambda f: f.strftime('%d/%m/%Y') if f else '-'
        personales = [
            ['Nombre:', f"{alumno.nombre} {alumno.apellido}",
             'DNI:', alumno.dni or '-'],
            ['Email:', alumno.email or '-',
             'Teléfono:', alumno.telefono or '-'],
            ['Fecha de nacimiento:', fmt_fecha(alumno.fecha_nacimiento),
             'Fecha de alta:', fmt_fecha(alumno.fecha_registro)],
            ['Dirección:', Paragraph(alumno.direccion or '-', styles['Normal']), '', ''],
            ['Estado:', 'Activo' if alumno.activo else
             f"Inactivo (baja: {fmt_fecha(alumno.fecha_baja)})",
             'Tipo de cuota:', alumno.get_tipo_cuota_display()],
            ['Matrícula:', 'Pagada' if alumno.matricula_pagada else 'Pendiente',
             '', ''],
        ]
        tabla = self._tabla_seccion('DATOS PERSONALES', personales,
                                    [35 * mm, 50 * mm, 35 * mm, 50 * mm])
        tabla.setStyle(TableStyle([
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
            ('SPAN', (1, 4), (-1, 4)),  # Dirección a lo ancho (fila 4: título + 3)
        ]))
        story.append(tabla)
        story.append(Spacer(1, 6 * mm))

        # Condiciones médicas
        story.append(self._tabla_seccion(
            'CONDICIONES MÉDICAS',
            [[Paragraph(alumno.condiciones_medicas or 'Sin condiciones médicas registradas',
                        styles['Normal'])]],
            [170 * mm]))
        story.append(Spacer(1, 6 * mm))

        # Historial de pagos
        pagos = datos['pagos']
        filas_pagos = [['Periodo', 'Tipo', 'Método', 'Fecha', 'Importe']]
        for pago in pagos:
            if pago.mes:
                periodo = pago.mes
            elif pago.fecha_clase:
                periodo = pago.fecha_clase.strftime('%d/%m/%Y')
            else:
                periodo = str(pago.año) if pago.año else '-'
            filas_pagos.append([
                periodo,
                (pago.tipo_pago or '-').replace('_', ' ').capitalize(),
                (pago.metodo_pago or '-').capitalize(),
                pago.fecha_creacion.strftime('%d/%m/%Y') if pago.fecha_creacion else '-',
                f"{pago.monto:.2f} €",
            ])
        if not pagos:
            filas_pagos.append(['Sin pagos registrados', '', '', '', ''])
        tabla_pagos = self._tabla_seccion(
            'HISTORIAL DE PAGOS', filas_pagos,
            [40 * mm, 35 * mm, 30 * mm, 30 * mm, 35 * mm])
        tabla_pagos.setStyle(TableStyle([
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
        ]))
        story.append(tabla_pagos)

        # Deuda pendiente
        if datos['pendientes']:
            periodos_txt = ', '.join(p.nombre_corto for p in datos['pendientes'])
            deuda_style = ParagraphStyle(
                'Deuda',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#B00020'),
            )
            story.append(Spacer(1, 3 * mm))
            story.append(Paragraph(
                f"<b>Deuda pendiente: {datos['deuda']:.2f} €</b> "
                f"(periodos sin pagar: {periodos_txt})",
                deuda_style))
        story.append(Spacer(1, 6 * mm))

        # Resumen de asistencias (últimos 90 días)
        filas_asis = [[
            'Clases registradas:', str(datos['total_asistencias']),
            'Presente:', str(datos['asistencias_presente']),
            '% asistencia:', f"{datos['porcentaje_asistencia']:.0f}%",
        ]]
        for mes_key in sorted(datos['asistencias_por_mes'].keys(), reverse=True):
            stats = datos['asistencias_por_mes'][mes_key]
            filas_asis.append([
                f"Mes {mes_key}:",
                f"{stats['presente']} de {stats['total']} clases",
                '', '', '', '',
            ])
        tabla_asis = self._tabla_seccion(
            'ASISTENCIAS (ÚLTIMOS 90 DÍAS)', filas_asis,
            [40 * mm, 40 * mm, 25 * mm, 20 * mm, 30 * mm, 15 * mm])
        tabla_asis.setStyle(TableStyle([
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 1), (2, 1), 'Helvetica-Bold'),
            ('FONTNAME', (4, 1), (4, 1), 'Helvetica-Bold'),
        ]))
        story.append(tabla_asis)
        story.append(Spacer(1, 6 * mm))

        # Bonos
        bonos = datos['bonos']
        filas_bonos = [['Clases', 'Compra', 'Caducidad', 'Estado']]
        for bono in bonos:
            if bono.esta_vigente():
                estado = 'Vigente'
            elif bono.clases_restantes <= 0:
                estado = 'Agotado'
            else:
                estado = 'Caducado'
            filas_bonos.append([
                f"{bono.clases_consumidas}/{bono.clases_totales}",
                fmt_fecha(bono.fecha_compra),
                fmt_fecha(bono.fecha_caducidad),
                estado,
            ])
        if not bonos:
            filas_bonos.append(['Sin bonos', '', '', ''])
        tabla_bonos = self._tabla_seccion(
            'BONOS DE CLASES', filas_bonos,
            [42.5 * mm, 42.5 * mm, 42.5 * mm, 42.5 * mm])
        tabla_bonos.setStyle(TableStyle([
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ]))
        story.append(tabla_bonos)
        story.append(Spacer(1, 10 * mm))

        # Pie de página
        footer_style = ParagraphStyle(
            'FichaFooter',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1
        )
        story.append(Paragraph(
            f"{datos['nombre_escuela']} — Documento de uso interno",
            footer_style))

        doc.build(story)
        buffer.seek(0)
        return buffer


def generar_pdf_ficha_alumno(alumno, datos):
    """
    Función helper para generar el PDF de la ficha de un alumno

    Args:
        alumno: Objeto Alumno
        datos: dict con los datos calculados (ver FichaAlumnoPDFGenerator)

    Returns:
        BytesIO con el contenido del PDF
    """
    generator = FichaAlumnoPDFGenerator()
    return generator.generar_ficha(alumno, datos)


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
