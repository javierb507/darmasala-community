from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from datetime import datetime, date, timedelta
from models import db, Alumno, Pago, Bono, Cliente, FacturaEmitida, LineaFactura, ConfiguracionFiscal, GastoMensual, FacturaProveedor, GastoFijo, CategoriaGasto, Tarifa, Proveedor, HorarioSemanal, Asistencia
from utils.auth_utils import login_required
from utils.finance_utils import exportar_datos_tax_excel

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/economia')
@login_required
def economia():
    """Dashboard principal de gestión económica unificado"""
    # Resumen financiero del mes y año actual
    current_month = date.today().month
    current_year = date.today().year

    # INGRESOS - Facturas emitidas a clientes
    start_of_year = date(current_year, 1, 1)
    end_of_year = date(current_year, 12, 31)
    
    facturas_emitidas_año = FacturaEmitida.query.filter(
        FacturaEmitida.fecha_emision >= start_of_year,
        FacturaEmitida.fecha_emision <= end_of_year,
        FacturaEmitida.estado != 'anulada'
    ).all()

    total_facturado_año = sum(f.base_imponible for f in facturas_emitidas_año)
    facturas_emitidas_pendientes = FacturaEmitida.query.filter_by(estado='emitida').count()
    facturas_emitidas_pagadas = FacturaEmitida.query.filter_by(estado='pagada').count()

    # Últimas facturas emitidas
    ultimas_facturas_emitidas = FacturaEmitida.query.order_by(FacturaEmitida.fecha_emision.desc()).limit(5).all()

    # GASTOS FIJOS
    gastos_fijos_activos = GastoFijo.query.filter_by(activo=True).count()
    gastos_fijos = GastoFijo.query.filter_by(activo=True).all()

    # Calcular total mensual de gastos fijos
    gastos_fijos_mensuales = 0
    for gasto in gastos_fijos:
        if gasto.frecuencia == 'mensual':
            gastos_fijos_mensuales += gasto.importe
        elif gasto.frecuencia == 'trimestral':
            gastos_fijos_mensuales += gasto.importe / 3
        elif gasto.frecuencia == 'anual':
            gastos_fijos_mensuales += gasto.importe / 12

    # GASTOS VARIABLES - Facturas de proveedores
    start_of_month = date(current_year, current_month, 1)
    if current_month == 12:
        end_of_month = date(current_year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_month = date(current_year, current_month + 1, 1) - timedelta(days=1)

    gastos_mes = db.session.query(db.func.sum(FacturaProveedor.importe_total)).filter(
        FacturaProveedor.estado == 'pagada',
        FacturaProveedor.fecha_pago >= start_of_month,
        FacturaProveedor.fecha_pago <= end_of_month
    ).scalar() or 0

    facturas_proveedores_pendientes = FacturaProveedor.query.filter_by(estado='pendiente').count()

    facturas_proveedores_vencidas = FacturaProveedor.query.filter(
        FacturaProveedor.estado == 'pendiente',
        FacturaProveedor.fecha_vencimiento < date.today()
    ).count()

    # Configuración fiscal
    config_fiscal = ConfiguracionFiscal.query.first()

    return render_template('economia/dashboard.html',
                         # Facturas emitidas
                         total_facturado_año=total_facturado_año,
                         facturas_emitidas_pendientes=facturas_emitidas_pendientes,
                         facturas_emitidas_pagadas=facturas_emitidas_pagadas,
                         ultimas_facturas_emitidas=ultimas_facturas_emitidas,
                         # Gastos fijos
                         gastos_fijos_activos=gastos_fijos_activos,
                         gastos_fijos_mensuales=gastos_fijos_mensuales,
                         # Gastos variables (facturas proveedores)
                         gastos_mes=gastos_mes,
                         facturas_proveedores_pendientes=facturas_proveedores_pendientes,
                         facturas_proveedores_vencidas=facturas_proveedores_vencidas,
                         # General
                         current_year=current_year,
                         config_fiscal=config_fiscal)

@finance_bp.route('/alumnos/<int:alumno_id>/pago', methods=['GET', 'POST'])
@login_required
def agregar_pago(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)

    if request.method == 'POST':
        try:
            tipo_pago = request.form['tipo_pago']
            monto = float(request.form['monto'])
            metodo_pago = request.form.get('metodo_pago', 'efectivo')
            
            # Manejar mes y año según el tipo de pago
            mes = None
            año = None
            fecha_clase = None
            
            if tipo_pago == 'cuota':
                mes = request.form.get('mes')
                # Verificar si ya existe un pago para este mes
                pago_existente = Pago.query.filter_by(
                    alumno_id=alumno_id,
                    tipo_pago='cuota',
                    mes=mes
                ).first()
                if pago_existente:
                    flash(f'⚠️ Ya existe un pago de cuota para {mes}. Si necesitas modificarlo, edita el pago existente.', 'warning')
                    return redirect(url_for('students.ver_alumno', alumno_id=alumno_id))
                    
            elif tipo_pago == 'matricula':
                año = int(request.form.get('año', date.today().year))
                # Verificar si ya existe un pago de matrícula para este año
                pago_existente = Pago.query.filter_by(
                    alumno_id=alumno_id,
                    tipo_pago='matricula',
                    año=año
                ).first()
                if pago_existente:
                    flash(f'⚠️ Ya existe un pago de matrícula para el año {año}. Si necesitas modificarlo, edita el pago existente.', 'warning')
                    return redirect(url_for('students.ver_alumno', alumno_id=alumno_id))
                    
            elif tipo_pago == 'clase_suelta':
                fecha_clase = datetime.strptime(request.form['fecha_clase'], '%Y-%m-%d').date()
                # Verificar si ya existe un pago para esta fecha específica
                pago_existente = Pago.query.filter_by(
                    alumno_id=alumno_id,
                    tipo_pago='clase_suelta',
                    fecha_clase=fecha_clase
                ).first()
                if pago_existente:
                    flash(f'⚠️ Ya existe un pago de clase suelta para el {fecha_clase.strftime("%d/%m/%Y")}. Si necesitas modificarlo, edita el pago existente.', 'warning')
                    return redirect(url_for('students.ver_alumno', alumno_id=alumno_id))

            elif tipo_pago == 'bono':
                clases_totales = int(request.form.get('bono_clases', 10))
                caducidad_str = request.form.get('bono_caducidad', '')
                fecha_caducidad = (datetime.strptime(caducidad_str, '%Y-%m-%d').date()
                                   if caducidad_str else None)

            # Crear descripción según el tipo de pago
            if tipo_pago == 'matricula':
                # Calcular formato de año académico
                if año >= 2025:
                    matricula_desc = f"Matrícula {(año % 100)}/{((año + 1) % 100)}"
                else:
                    matricula_desc = f"Matrícula {año}"
            
            descripciones = {
                'cuota': f'Cuota mensual - {alumno.get_tipo_cuota_display()}',
                'matricula': matricula_desc if tipo_pago == 'matricula' else f'Matrícula {año}',
                'clase_suelta': f'Clase suelta - {fecha_clase.strftime("%d/%m/%Y") if fecha_clase else ""}',
                'bono': f'Bono de {clases_totales} clases' if tipo_pago == 'bono' else 'Bono de clases'
            }
            
            pago = Pago(
                alumno_id=alumno_id,
                mes=mes,
                año=año,
                fecha_clase=fecha_clase,
                monto=monto,
                tipo_pago=tipo_pago,
                descripcion=descripciones.get(tipo_pago, 'Pago'),
                metodo_pago=metodo_pago
            )
            db.session.add(pago)

            # Si es bono, crear el Bono vinculado al pago
            if tipo_pago == 'bono':
                db.session.flush()
                bono = Bono(alumno_id=alumno_id, pago_id=pago.id,
                            clases_totales=clases_totales,
                            fecha_caducidad=fecha_caducidad, precio=monto)
                db.session.add(bono)

            # Si es matrícula, marcar al alumno como que pagó la matrícula
            if tipo_pago == 'matricula':
                alumno.matricula_pagada = True
                alumno.fecha_matricula = date.today()
            
            db.session.commit()
            flash('¡Pago registrado exitosamente!', 'success')
            return redirect(url_for('students.ver_alumno', alumno_id=alumno_id))
        except Exception as e:
            flash(f'Error al registrar pago: {str(e)}', 'error')
            db.session.rollback()

    return render_template('economia/agregar_pago.html', alumno=alumno)

@finance_bp.route('/pagos/<int:pago_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_pago(pago_id):
    """Editar un pago existente"""
    pago = Pago.query.get_or_404(pago_id)
    alumno = pago.alumno
    
    if request.method == 'POST':
        try:
            # Actualizar datos del pago
            pago.monto = float(request.form['monto'])
            pago.metodo_pago = request.form.get('metodo_pago', 'efectivo')
            
            # Actualizar campos específicos según el tipo
            if pago.tipo_pago == 'cuota':
                nuevo_mes = request.form.get('mes')
                # Verificar duplicados solo si cambió el mes
                if nuevo_mes != pago.mes:
                    pago_existente = Pago.query.filter_by(
                        alumno_id=pago.alumno_id,
                        tipo_pago='cuota',
                        mes=nuevo_mes
                    ).filter(Pago.id != pago.id).first()
                    if pago_existente:
                        flash(f'⚠️ Ya existe un pago de cuota para {nuevo_mes}', 'warning')
                        return redirect(url_for('students.ver_alumno', alumno_id=alumno.id))
                pago.mes = nuevo_mes
                
            elif pago.tipo_pago == 'matricula':
                nuevo_año = int(request.form.get('año', date.today().year))
                # Verificar duplicados solo si cambió el año
                if nuevo_año != pago.año:
                    pago_existente = Pago.query.filter_by(
                        alumno_id=pago.alumno_id,
                        tipo_pago='matricula',
                        año=nuevo_año
                    ).filter(Pago.id != pago.id).first()
                    if pago_existente:
                        flash(f'⚠️ Ya existe un pago de matrícula para el año {nuevo_año}', 'warning')
                        return redirect(url_for('students.ver_alumno', alumno_id=alumno.id))
                pago.año = nuevo_año
                
            elif pago.tipo_pago == 'clase_suelta':
                nueva_fecha = datetime.strptime(request.form['fecha_clase'], '%Y-%m-%d').date()
                # Verificar duplicados solo si cambió la fecha
                if nueva_fecha != pago.fecha_clase:
                    pago_existente = Pago.query.filter_by(
                        alumno_id=pago.alumno_id,
                        tipo_pago='clase_suelta',
                        fecha_clase=nueva_fecha
                    ).filter(Pago.id != pago.id).first()
                    if pago_existente:
                        flash(f'⚠️ Ya existe un pago de clase suelta para el {nueva_fecha.strftime("%d/%m/%Y")}', 'warning')
                        return redirect(url_for('students.ver_alumno', alumno_id=alumno.id))
                pago.fecha_clase = nueva_fecha
            
            db.session.commit()
            flash('¡Pago actualizado exitosamente!', 'success')
            return redirect(url_for('students.ver_alumno', alumno_id=alumno.id))
            
        except Exception as e:
            flash(f'Error al actualizar pago: {str(e)}', 'error')
            db.session.rollback()
    
    # Calcular año de matrícula para el template
    current_date = date.today()
    if current_date.month >= 9:
        matricula_year = f"{current_date.year % 100}/{(current_date.year + 1) % 100}"
        matricula_year_numeric = current_date.year
    else:
        matricula_year = f"{(current_date.year - 1) % 100}/{current_date.year % 100}"
        matricula_year_numeric = current_date.year - 1
    
    return render_template('editar_pago.html', 
                         pago=pago,
                         alumno=alumno,
                         current_year=date.today().year,
                         matricula_year=matricula_year,
                         matricula_year_numeric=matricula_year_numeric)

@finance_bp.route('/pagos/<int:pago_id>/eliminar', methods=['POST'])
@login_required
def eliminar_pago(pago_id):
    """Eliminar un pago"""
    try:
        pago = Pago.query.get_or_404(pago_id)
        alumno_id = pago.alumno_id
        
        # Si es matrícula, actualizar el estado del alumno
        if pago.tipo_pago == 'matricula':
            # Verificar si hay otros pagos de matrícula
            otros_pagos_matricula = Pago.query.filter_by(
                alumno_id=alumno_id,
                tipo_pago='matricula'
            ).filter(Pago.id != pago.id).first()
            
            if not otros_pagos_matricula:
                alumno = Alumno.query.get(alumno_id)
                alumno.matricula_pagada = False
                alumno.fecha_matricula = None
        
        db.session.delete(pago)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Pago eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@finance_bp.route('/economia/historico')
@login_required
def economia_historico():
    """Dashboard principal de contabilidad con períodos"""
    from models import GastoMensual, FacturaProveedor
    # Obtener parámetros de período
    periodo = request.args.get('periodo', 'mes_actual')
    año = int(request.args.get('año', date.today().year))
    mes = int(request.args.get('mes', date.today().month))
    
    # Calcular fechas según el período
    if periodo == 'mes_actual':
        fecha_inicio = date(año, mes, 1)
        if mes == 12:
            fecha_fin = date(año + 1, 1, 1) - timedelta(days=1)
        else:
            fecha_fin = date(año, mes + 1, 1) - timedelta(days=1)
    elif periodo == 'trimestre':
        trimestre = ((mes - 1) // 3) + 1
        mes_inicio = (trimestre - 1) * 3 + 1
        fecha_inicio = date(año, mes_inicio, 1)
        if trimestre == 4:
            fecha_fin = date(año + 1, 1, 1) - timedelta(days=1)
        else:
            fecha_fin = date(año, mes_inicio + 3, 1) - timedelta(days=1)
    elif periodo == 'año':
        fecha_inicio = date(año, 1, 1)
        fecha_fin = date(año, 12, 31)
    else:  # mes_actual por defecto
        fecha_inicio = date(año, mes, 1)
        fecha_fin = date(año, mes + 1, 1) - timedelta(days=1) if mes < 12 else date(año, 12, 31)
    
    # Calcular ingresos del período
    ingresos_cuotas = db.session.query(db.func.sum(Pago.monto)).filter(
        Pago.tipo_pago == 'cuota',
        Pago.fecha_creacion >= fecha_inicio,
        Pago.fecha_creacion <= fecha_fin
    ).scalar() or 0
    
    ingresos_matriculas = db.session.query(db.func.sum(Pago.monto)).filter(
        Pago.tipo_pago == 'matricula',
        Pago.fecha_creacion >= fecha_inicio,
        Pago.fecha_creacion <= fecha_fin
    ).scalar() or 0
    
    ingresos_clases_sueltas = db.session.query(db.func.sum(Pago.monto)).filter(
        Pago.tipo_pago == 'clase_suelta',
        Pago.fecha_creacion >= fecha_inicio,
        Pago.fecha_creacion <= fecha_fin
    ).scalar() or 0
    
    total_ingresos = ingresos_cuotas + ingresos_matriculas + ingresos_clases_sueltas
    
    # Calcular gastos del período
    total_gastos = db.session.query(db.func.sum(GastoMensual.importe)).filter(
        GastoMensual.fecha >= fecha_inicio,
        GastoMensual.fecha <= fecha_fin
    ).scalar() or 0
    
    # Balance
    balance = total_ingresos - total_gastos
    
    # Calcular facturas pendientes
    facturas_pendientes = FacturaProveedor.query.filter_by(estado='pendiente').count()
    
    # Desglose de ingresos
    ingresos_detalle = {
        'cuotas': ingresos_cuotas,
        'matriculas': ingresos_matriculas,
        'clases_sueltas': ingresos_clases_sueltas,
        'yogaterapia': 0
    }
    
    # Desglose de gastos
    gastos_detalle = {
        'gastos_mensuales': total_gastos,
        'facturas': facturas_pendientes,
        'gastos_fijos': 0
    }
    
    return render_template('economia/dashboard_simple.html',
                         periodo=periodo,
                         año=año,
                         mes=mes,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin,
                         ingresos_cuotas=ingresos_cuotas,
                         ingresos_matriculas=ingresos_matriculas,
                         ingresos_clases_sueltas=ingresos_clases_sueltas,
                         ingresos_total=total_ingresos,
                         total_ingresos=total_ingresos,
                         total_gastos=total_gastos,
                         balance=balance,
                         facturas_pendientes=facturas_pendientes,
                         gastos_pendientes=0,
                         ingresos_detalle=ingresos_detalle,
                         gastos_detalle=gastos_detalle)

@finance_bp.route('/gastos-mensuales')
@login_required
def gastos_mensuales():
    """Vista de gastos mensuales"""
    from datetime import timedelta
    gastos = GastoMensual.query.order_by(GastoMensual.fecha.desc()).all()
    
    # Calcular ingresos del mes actual
    hoy = date.today()
    fecha_inicio = date(hoy.year, hoy.month, 1)
    if hoy.month == 12:
        fecha_fin = date(hoy.year + 1, 1, 1) - timedelta(days=1)
    else:
        fecha_fin = date(hoy.year, hoy.month + 1, 1) - timedelta(days=1)
    
    ingresos_mes = db.session.query(db.func.sum(Pago.monto)).filter(
        Pago.fecha_creacion >= fecha_inicio,
        Pago.fecha_creacion <= fecha_fin
    ).scalar() or 0
    
    # Calcular gastos del mes actual
    gastos_mes = db.session.query(db.func.sum(GastoMensual.importe)).filter(
        GastoMensual.fecha >= fecha_inicio,
        GastoMensual.fecha <= fecha_fin
    ).scalar() or 0
    
    # Calcular balance del mes
    balance_mes = ingresos_mes - gastos_mes
    
    return render_template('economia/gastos_mensuales.html', gastos=gastos, ingresos_mes=ingresos_mes, gastos_mes=gastos_mes, balance_mes=balance_mes)

@finance_bp.route('/agregar_gasto_mensual', methods=['POST'])
@login_required
def agregar_gasto_mensual():
    """Agregar nuevo gasto mensual"""
    try:
        gasto = GastoMensual(
            fecha=datetime.strptime(request.form.get('fecha'), '%Y-%m-%d').date(),
            concepto=request.form.get('concepto'),
            categoria=request.form.get('categoria'),
            importe=float(request.form.get('importe')),
            pagado='pagado' in request.form,
            metodo_pago=request.form.get('metodo_pago', ''),
            notas=request.form.get('notas', '')
        )
        
        db.session.add(gasto)
        db.session.commit()
        flash('Gasto mensual agregado exitosamente', 'success')
        return redirect(url_for('finance.gastos_mensuales'))
        
    except Exception as e:
        flash(f'Error al agregar gasto: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('finance.gastos_mensuales'))

@finance_bp.route('/proveedores')
@login_required
def proveedores():
    """Lista de proveedores"""
    proveedores = Proveedor.query.filter_by(activo=True).all()
    return render_template('economia/proveedores.html', proveedores=proveedores)

@finance_bp.route('/facturas')
@login_required
def facturas():
    """Lista de facturas"""
    facturas = FacturaProveedor.query.order_by(FacturaProveedor.fecha_factura.desc()).all()
    return render_template('economia/facturas.html', facturas=facturas)

@finance_bp.route('/facturas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_factura():
    """Crear nueva factura"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            numero_factura = request.form.get('numero_factura')
            proveedor_id = request.form.get('proveedor_id')
            categoria_id = request.form.get('categoria_id')
            fecha_factura = datetime.strptime(request.form.get('fecha_factura'), '%Y-%m-%d').date()
            fecha_vencimiento = datetime.strptime(request.form.get('fecha_vencimiento'), '%Y-%m-%d').date() if request.form.get('fecha_vencimiento') else None
            importe_sin_iva = float(request.form.get('importe_sin_iva'))
            iva = float(request.form.get('iva', 21.0))
            descripcion = request.form.get('descripcion', '')
            notas = request.form.get('notas', '')
            
            # Calcular importe total
            importe_total = importe_sin_iva * (1 + iva / 100)
            
            prov_id = request.form.get('proveedor_id')
            prov_id = int(prov_id) if prov_id and prov_id != '' else None
            
            # Crear factura
            factura = FacturaProveedor(
                numero_factura=numero_factura,
                proveedor_id=prov_id,
                nombre_proveedor=request.form.get('nombre_proveedor_libre', ''),
                categoria_id=categoria_id,
                fecha_factura=fecha_factura,
                fecha_vencimiento=fecha_vencimiento,
                importe_sin_iva=importe_sin_iva,
                iva=iva,
                importe_total=importe_total,
                descripcion=descripcion,
                notas=notas
            )
            
            db.session.add(factura)
            db.session.commit()
            flash('Factura creada exitosamente', 'success')
            return redirect(url_for('finance.facturas'))
            
        except Exception as e:
            flash(f'Error al crear factura: {str(e)}', 'error')
            db.session.rollback()
    
    proveedores = Proveedor.query.filter_by(activo=True).all()
    categorias = CategoriaGasto.query.filter_by(activo=True).all()
    
    return render_template('economia/nueva_factura.html', 
                         proveedores=proveedores, 
                         categorias=categorias,
                         date=date)

@finance_bp.route('/facturas/<int:factura_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_factura(factura_id):
    """Editar factura existente"""
    factura = FacturaProveedor.query.get_or_404(factura_id)
    
    if request.method == 'POST':
        try:
            factura.numero_factura = request.form.get('numero_factura')
            prov_id = request.form.get('proveedor_id')
            factura.proveedor_id = int(prov_id) if prov_id and prov_id != '' else None
            factura.nombre_proveedor = request.form.get('nombre_proveedor_libre', '')
            factura.categoria_id = request.form.get('categoria_id')
            factura.fecha_factura = datetime.strptime(request.form.get('fecha_factura'), '%Y-%m-%d').date()
            factura.fecha_vencimiento = datetime.strptime(request.form.get('fecha_vencimiento'), '%Y-%m-%d').date() if request.form.get('fecha_vencimiento') else None
            factura.importe_sin_iva = float(request.form.get('importe_sin_iva'))
            factura.iva = float(request.form.get('iva', 21.0))
            factura.importe_total = factura.importe_sin_iva * (1 + factura.iva / 100)
            factura.descripcion = request.form.get('descripcion', '')
            factura.notas = request.form.get('notas', '')
            factura.estado = request.form.get('estado', 'pendiente')
            factura.metodo_pago = request.form.get('metodo_pago', '')
            
            if factura.estado == 'pagada' and not factura.fecha_pago:
                factura.fecha_pago = date.today()
            
            db.session.commit()
            flash('Factura actualizada exitosamente', 'success')
            return redirect(url_for('finance.facturas'))
            
        except Exception as e:
            flash(f'Error al actualizar factura: {str(e)}', 'error')
            db.session.rollback()
    
    proveedores = Proveedor.query.filter_by(activo=True).all()
    categorias = CategoriaGasto.query.filter_by(activo=True).all()
    
    return render_template('economia/editar_factura.html', 
                         factura=factura,
                         proveedores=proveedores, 
                         categorias=categorias)

@finance_bp.route('/facturas/<int:factura_id>/marcar_pagada', methods=['POST'])
@login_required
def marcar_factura_pagada(factura_id):
    """Marcar factura como pagada"""
    try:
        factura = FacturaProveedor.query.get_or_404(factura_id)
        factura.estado = 'pagada'
        factura.fecha_pago = date.today()
        factura.metodo_pago = request.form.get('metodo_pago', 'transferencia')
        
        db.session.commit()
        flash('Factura marcada como pagada', 'success')
    except Exception as e:
        flash(f'Error al marcar factura: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('finance.facturas'))

@finance_bp.route('/facturas/<int:factura_id>/eliminar', methods=['POST'])
@login_required
def eliminar_factura(factura_id):
    """Eliminar factura"""
    try:
        factura = FacturaProveedor.query.get_or_404(factura_id)
        db.session.delete(factura)
        db.session.commit()
        flash('Factura eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar factura: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('finance.facturas'))

@finance_bp.route('/gastos-fijos')
@login_required
def gastos_fijos():
    """Lista de gastos fijos"""
    gastos = GastoFijo.query.filter_by(activo=True).order_by(GastoFijo.nombre).all()
    return render_template('economia/gastos_fijos.html', gastos=gastos)

@finance_bp.route('/gastos-fijos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_gasto_fijo():
    """Crear nuevo gasto fijo"""
    if request.method == 'POST':
        try:
            gasto = GastoFijo(
                nombre=request.form.get('nombre'),
                descripcion=request.form.get('descripcion', ''),
                categoria_id=request.form.get('categoria_id'),
                proveedor_id=request.form.get('proveedor_id') or None,
                importe=float(request.form.get('importe')),
                frecuencia=request.form.get('frecuencia', 'mensual'),
                dia_cargo=int(request.form.get('dia_cargo', 1)),
                fecha_inicio=datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d').date(),
                fecha_fin=datetime.strptime(request.form.get('fecha_fin'), '%Y-%m-%d').date() if request.form.get('fecha_fin') else None,
                notas=request.form.get('notas', '')
            )
            
            db.session.add(gasto)
            db.session.commit()
            flash('Gasto fijo creado exitosamente', 'success')
            return redirect(url_for('finance.gastos_fijos'))
            
        except Exception as e:
            flash(f'Error al crear gasto fijo: {str(e)}', 'error')
            db.session.rollback()
    
    categorias = CategoriaGasto.query.filter_by(activo=True).all()
    proveedores = Proveedor.query.filter_by(activo=True).all()
    fecha_hoy = date.today()
    return render_template('economia/nuevo_gasto_fijo.html', categorias=categorias, proveedores=proveedores, fecha_hoy=fecha_hoy)

@finance_bp.route('/gastos-fijos/<int:gasto_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_gasto_fijo(gasto_id):
    """Editar gasto fijo existente"""
    gasto = GastoFijo.query.get_or_404(gasto_id)
    
    if request.method == 'POST':
        try:
            gasto.nombre = request.form.get('nombre')
            gasto.descripcion = request.form.get('descripcion', '')
            gasto.categoria_id = request.form.get('categoria_id')
            gasto.proveedor_id = request.form.get('proveedor_id') or None
            gasto.importe = float(request.form.get('importe'))
            gasto.frecuencia = request.form.get('frecuencia', 'mensual')
            gasto.dia_cargo = int(request.form.get('dia_cargo', 1))
            gasto.fecha_inicio = datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d').date()
            gasto.fecha_fin = datetime.strptime(request.form.get('fecha_fin'), '%Y-%m-%d').date() if request.form.get('fecha_fin') else None
            gasto.notas = request.form.get('notas', '')
            gasto.activo = 'activo' in request.form
            
            db.session.commit()
            flash('Gasto fijo actualizado exitosamente', 'success')
            return redirect(url_for('finance.gastos_fijos'))
            
        except Exception as e:
            flash(f'Error al actualizar gasto fijo: {str(e)}', 'error')
            db.session.rollback()
    
    categorias = CategoriaGasto.query.filter_by(activo=True).all()
    proveedores = Proveedor.query.filter_by(activo=True).all()
    return render_template('economia/editar_gasto_fijo.html', gasto=gasto, categorias=categorias, proveedores=proveedores)

@finance_bp.route('/gastos-fijos/<int:gasto_id>/eliminar', methods=['POST'])
@login_required
def eliminar_gasto_fijo(gasto_id):
    """Eliminar gasto fijo"""
    try:
        gasto = GastoFijo.query.get_or_404(gasto_id)
        gasto.activo = False
        db.session.commit()
        flash('Gasto fijo desactivado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al desactivar gasto fijo: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('finance.gastos_fijos'))

@finance_bp.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_proveedor():
    """Crear nuevo proveedor"""
    if request.method == 'POST':
        try:
            proveedor = Proveedor(
                nombre=request.form.get('nombre'),
                cif_nif=request.form.get('cif_nif', ''),
                direccion=request.form.get('direccion', ''),
                telefono=request.form.get('telefono', ''),
                email=request.form.get('email', ''),
                contacto_principal=request.form.get('contacto_principal', ''),
                notas=request.form.get('notas', '')
            )
            
            db.session.add(proveedor)
            db.session.commit()
            flash('Proveedor creado exitosamente', 'success')
            return redirect(url_for('finance.proveedores'))
            
        except Exception as e:
            flash(f'Error al crear proveedor: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('economia/nuevo_proveedor.html')

@finance_bp.route('/proveedores/<int:proveedor_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_proveedor(proveedor_id):
    """Editar proveedor existente"""
    proveedor = Proveedor.query.get_or_404(proveedor_id)
    
    if request.method == 'POST':
        try:
            proveedor.nombre = request.form.get('nombre')
            proveedor.cif_nif = request.form.get('cif_nif', '')
            proveedor.direccion = request.form.get('direccion', '')
            proveedor.telefono = request.form.get('telefono', '')
            proveedor.email = request.form.get('email', '')
            proveedor.contacto_principal = request.form.get('contacto_principal', '')
            proveedor.notas = request.form.get('notas', '')
            proveedor.activo = 'activo' in request.form
            
            db.session.commit()
            flash('Proveedor actualizado exitosamente', 'success')
            return redirect(url_for('finance.proveedores'))
            
        except Exception as e:
            flash(f'Error al actualizar proveedor: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('economia/editar_proveedor.html', proveedor=proveedor)

@finance_bp.route('/proveedores/<int:proveedor_id>/eliminar', methods=['POST'])
@login_required
def eliminar_proveedor(proveedor_id):
    """Eliminar proveedor"""
    try:
        proveedor = Proveedor.query.get_or_404(proveedor_id)
        proveedor.activo = False
        db.session.commit()
        flash('Proveedor desactivado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al desactivar proveedor: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('finance.proveedores'))

@finance_bp.route('/exportar-tax')
@login_required
def exportar_tax():
    """Ruta para exportar datos especializados para impuestos"""
    año = request.args.get('año', date.today().year, type=int)
    
    # Obtener todas las facturas emitidas del año
    facturas_emitidas = FacturaEmitida.query.filter(
        db.extract('year', FacturaEmitida.fecha_emision) == año,
        FacturaEmitida.estado != 'anulada'
    ).all()
    
    # Obtener todas las facturas de proveedores del año
    facturas_proveedor = FacturaProveedor.query.filter(
        db.extract('year', FacturaProveedor.fecha_factura) == año
    ).all()
    
    # Obtener gastos fijos activos
    gastos_fijos = GastoFijo.query.filter_by(activo=True).all()
    
    return exportar_datos_tax_excel(facturas_emitidas, facturas_proveedor, gastos_fijos, año)

@finance_bp.route('/exportar/<tipo>')
@login_required
def exportar_datos(tipo):
    """Exportar datos a Excel"""
    from utils.finance_utils import exportar_facturas_excel, exportar_gastos_fijos_excel, exportar_proveedores_excel, exportar_ingresos_excel
    try:
        if tipo == 'facturas':
            facturas = FacturaProveedor.query.order_by(FacturaProveedor.fecha_factura.desc()).all()
            return exportar_facturas_excel(facturas)
        elif tipo == 'gastos-fijos':
            gastos = GastoFijo.query.filter_by(activo=True).all()
            return exportar_gastos_fijos_excel(gastos)
        elif tipo == 'proveedores':
            proveedores = Proveedor.query.filter_by(activo=True).all()
            return exportar_proveedores_excel(proveedores)
        elif tipo == 'ingresos':
            return exportar_ingresos_excel()
        else:
            flash('Tipo de exportación no válido', 'error')
            return redirect(url_for('finance.economia'))
    except Exception as e:
        flash(f'Error al exportar datos: {str(e)}', 'error')
        return redirect(url_for('finance.economia'))

@finance_bp.route('/reporte-contabilidad-pdf')
@login_required
def reporte_contabilidad_pdf():
    """Generar reporte de contabilidad en PDF"""
    from utils.finance_utils import generar_reporte_pdf
    try:
        # Obtener parámetros
        periodo = request.args.get('periodo', 'mes_actual')
        año = int(request.args.get('año', date.today().year))
        mes = int(request.args.get('mes', date.today().month))
        
        # Calcular fechas
        if periodo == 'mes_actual':
            fecha_inicio = date(año, mes, 1)
            if mes == 12:
                fecha_fin = date(año + 1, 1, 1) - timedelta(days=1)
            else:
                fecha_fin = date(año, mes + 1, 1) - timedelta(days=1)
        elif periodo == 'año':
            fecha_inicio = date(año, 1, 1)
            fecha_fin = date(año, 12, 31)
        else:
            fecha_inicio = date(año, mes, 1)
            fecha_fin = date(año, mes + 1, 1) - timedelta(days=1) if mes < 12 else date(año, 12, 31)
        
        # Obtener datos
        facturas = FacturaProveedor.query.filter(
            FacturaProveedor.fecha_factura >= fecha_inicio,
            FacturaProveedor.fecha_factura <= fecha_fin
        ).all()
        
        gastos_fijos = GastoFijo.query.filter_by(activo=True).all()
        
        ingresos = db.session.query(db.func.sum(Pago.monto)).filter(
            Pago.fecha_creacion >= fecha_inicio,
            Pago.fecha_creacion <= fecha_fin
        ).scalar() or 0
        
        return generar_reporte_pdf(facturas, gastos_fijos, ingresos, fecha_inicio, fecha_fin)
        
    except Exception as e:
        flash(f'Error al generar reporte PDF: {str(e)}', 'error')
        return redirect(url_for('finance.economia_historico'))

# --- RUTAS DE FACTURACIÓN EMITIDA (Migradas de app_recovered.py) ---

@finance_bp.route('/clientes-facturacion')
@login_required
def clientes_facturacion():
    """Lista de clientes para facturación"""
    clientes = Cliente.query.filter_by(activo=True).all()
    return render_template('economia/clientes.html', clientes=clientes)

@finance_bp.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    """Crear un nuevo cliente para facturación"""
    if request.method == 'POST':
        try:
            cliente = Cliente(
                nombre=request.form.get('nombre'),
                nif_cif=request.form.get('nif_cif'),
                direccion=request.form.get('direccion'),
                codigo_postal=request.form.get('codigo_postal'),
                ciudad=request.form.get('ciudad'),
                provincia=request.form.get('provincia'),
                email=request.form.get('email'),
                telefono=request.form.get('telefono'),
                tipo_cliente=request.form.get('tipo_cliente', 'particular'),
                notas=request.form.get('notas'),
                alumno_id=request.form.get('alumno_id') or None
            )
            db.session.add(cliente)
            db.session.commit()
            flash('Cliente creado exitosamente', 'success')
            return redirect(url_for('finance.clientes_facturacion'))
        except Exception as e:
            flash(f'Error al crear el cliente: {str(e)}', 'error')
            db.session.rollback()

    alumnos = Alumno.query.filter_by(activo=True).all()
    return render_template('economia/nuevo_cliente.html', alumnos=alumnos)

@finance_bp.route('/facturacion/clientes/<int:cliente_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_cliente(cliente_id):
    """Editar cliente existente"""
    cliente = Cliente.query.get_or_404(cliente_id)

    if request.method == 'POST':
        try:
            # Verificar NIF único (excepto el actual)
            nif_cif = request.form.get('nif_cif', '').strip()
            cliente_existente = Cliente.query.filter_by(nif_cif=nif_cif).first()
            if cliente_existente and cliente_existente.id != cliente_id:
                flash(f'Ya existe otro cliente con el NIF/CIF {nif_cif}', 'error')
                return redirect(url_for('finance.editar_cliente', cliente_id=cliente_id))

            cliente.nombre = request.form.get('nombre')
            cliente.nif_cif = nif_cif
            cliente.direccion = request.form.get('direccion')
            cliente.codigo_postal = request.form.get('codigo_postal')
            cliente.ciudad = request.form.get('ciudad')
            cliente.provincia = request.form.get('provincia')
            cliente.pais = request.form.get('pais', 'España')
            cliente.email = request.form.get('email')
            cliente.telefono = request.form.get('telefono')
            cliente.tipo_cliente = request.form.get('tipo_cliente', 'particular')
            cliente.notas = request.form.get('notas')
            cliente.alumno_id = request.form.get('alumno_id') if request.form.get('alumno_id') else None

            db.session.commit()

            flash(f'Cliente "{cliente.nombre}" actualizado exitosamente', 'success')
            return redirect(url_for('finance.clientes_facturacion'))
        except Exception as e:
            flash(f'Error al actualizar el cliente: {str(e)}', 'error')
            db.session.rollback()
            return redirect(url_for('finance.editar_cliente', cliente_id=cliente_id))

    # GET request
    alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.nombre).all()
    return render_template('economia/editar_cliente.html', cliente=cliente, alumnos=alumnos)

@finance_bp.route('/facturas-emitidas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_factura_emitida():
    """Crear nueva factura"""
    if request.method == 'POST':
        try:
            # Obtener configuración fiscal
            config_fiscal = ConfiguracionFiscal.query.first()
            if not config_fiscal:
                flash('Debe configurar los datos fiscales antes de emitir facturas', 'error')
                return redirect(url_for('finance.configuracion_fiscal'))

            # Crear factura
            factura = FacturaEmitida(
                serie=request.form.get('serie', config_fiscal.serie_factura_default),
                fecha_emision=datetime.strptime(request.form.get('fecha_emision'), '%Y-%m-%d').date(),
                fecha_prestacion=datetime.strptime(request.form.get('fecha_prestacion'), '%Y-%m-%d').date(),
                cliente_id=request.form.get('cliente_id'),
                exenta_iva=request.form.get('exenta_iva') == 'on',
                tipo_iva=float(request.form.get('tipo_iva', 0)),
                tipo_retencion=float(request.form.get('tipo_retencion', 0)),
                observaciones=request.form.get('observaciones'),
                base_imponible=0,  # Se calculará después
                total=0  # Se calculará después
            )

            # Asignar motivo de exención si aplica
            if factura.exenta_iva:
                factura.motivo_exencion = config_fiscal.texto_exencion_iva

            # Generar número de factura
            factura.generar_numero_factura()

            db.session.add(factura)
            db.session.flush()  # Para obtener el ID de la factura

            # Procesar líneas de factura
            lineas_count = int(request.form.get('lineas_count', 0))
            for i in range(lineas_count):
                descripcion = request.form.get(f'linea_{i}_descripcion')
                if descripcion:  # Solo agregar líneas con descripción
                    linea = LineaFactura(
                        factura_id=factura.id,
                        orden=i,
                        descripcion=descripcion,
                        cantidad=float(request.form.get(f'linea_{i}_cantidad', 1)),
                        precio_unitario=float(request.form.get(f'linea_{i}_precio', 0))
                    )
                    linea.calcular_subtotal()
                    db.session.add(linea)

            # Calcular totales de la factura
            factura.calcular_totales()

            db.session.commit()

            flash(f'Factura {factura.numero_completo} creada exitosamente', 'success')
            return redirect(url_for('finance.ver_factura_emitida', factura_id=factura.id))
        except Exception as e:
            flash(f'Error al crear la factura: {str(e)}', 'error')
            db.session.rollback()
            return redirect(url_for('finance.nueva_factura_emitida'))

    # GET request
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    config_fiscal = ConfiguracionFiscal.query.first()
    tarifas = Tarifa.query.filter_by(activa=True).all()

    return render_template('economia/nueva_factura_emitida.html',
                         clientes=clientes,
                         config_fiscal=config_fiscal,
                         tarifas=tarifas,
                         fecha_hoy=date.today())

@finance_bp.route('/facturas-emitidas/<int:factura_id>')
@login_required
def ver_factura_emitida(factura_id):
    """Ver detalle de factura"""
    factura = FacturaEmitida.query.get_or_404(factura_id)
    config_fiscal = ConfiguracionFiscal.query.first()
    return render_template('economia/ver_factura_emitida.html', factura=factura, config_fiscal=config_fiscal, fecha_hoy=date.today())

@finance_bp.route('/facturas-emitidas/<int:factura_id>/anular', methods=['POST'])
@login_required
def anular_factura_emitida(factura_id):
    """Anular una factura"""
    try:
        factura = FacturaEmitida.query.get_or_404(factura_id)

        if factura.estado == 'anulada':
            flash('La factura ya está anulada', 'warning')
            return redirect(url_for('finance.ver_factura_emitida', factura_id=factura_id))

        factura.estado = 'anulada'
        db.session.commit()

        flash(f'Factura {factura.numero_completo} anulada exitosamente', 'success')
        return redirect(url_for('finance.ver_factura_emitida', factura_id=factura_id))
    except Exception as e:
        flash(f'Error al anular la factura: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('finance.ver_factura_emitida', factura_id=factura_id))

@finance_bp.route('/facturas-emitidas/<int:factura_id>/marcar_pagada', methods=['POST'])
@login_required
def marcar_factura_emitida_pagada(factura_id):
    """Marcar factura como pagada"""
    try:
        factura = FacturaEmitida.query.get_or_404(factura_id)

        factura.estado = 'pagada'
        factura.fecha_pago = datetime.strptime(request.form.get('fecha_pago'), '%Y-%m-%d').date()
        factura.metodo_pago = request.form.get('metodo_pago')

        db.session.commit()

        flash(f'Factura {factura.numero_completo} marcada como pagada', 'success')
        return redirect(url_for('finance.ver_factura_emitida', factura_id=factura_id))
    except Exception as e:
        flash(f'Error al marcar la factura como pagada: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('finance.ver_factura_emitida', factura_id=factura_id))

@finance_bp.route('/facturas-emitidas/<int:factura_id>/pdf')
@login_required
def descargar_factura_pdf(factura_id):
    """Generar y descargar PDF de factura"""
    try:
        factura = FacturaEmitida.query.get_or_404(factura_id)
        config_fiscal = ConfiguracionFiscal.query.first()

        if not config_fiscal:
            flash('Debe configurar los datos fiscales antes de generar facturas en PDF', 'error')
            return redirect(url_for('finance.ver_factura_emitida', factura_id=factura_id))

        from utils.pdf_generator import generar_pdf_factura
        pdf_buffer = generar_pdf_factura(factura, config_fiscal)

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Factura_{factura.serie}_{factura.numero:04d}.pdf'
        )
    except Exception as e:
        flash(f'Error al generar PDF: {str(e)}', 'error')
        return redirect(url_for('finance.ver_factura_emitida', factura_id=factura_id))

@finance_bp.route('/configuracion-fiscal', methods=['GET', 'POST'])
@login_required
def configuracion_fiscal():
    """Gestionar la configuración fiscal del negocio"""
    config = ConfiguracionFiscal.query.first()
    if not config:
        config = ConfiguracionFiscal(nombre_empresa="Mi Escuela de Yoga")
        db.session.add(config)
        db.session.commit()

    if request.method == 'POST':
        try:
            config.nombre_empresa = request.form.get('nombre_empresa')
            config.nif = request.form.get('nif')
            config.direccion_fiscal = request.form.get('direccion_fiscal')
            config.codigo_postal = request.form.get('codigo_postal')
            config.ciudad = request.form.get('ciudad')
            config.provincia = request.form.get('provincia')
            config.telefono = request.form.get('telefono')
            config.email = request.form.get('email')
            config.epigrafe_iae = request.form.get('epigrafe_iae')
            config.regimen_iva = request.form.get('regimen_iva', 'general')
            config.tipo_retencion_default = float(request.form.get('tipo_retencion_default', 7.0))
            config.exento_iva = request.form.get('exento_iva') == 'on'
            config.texto_exencion_iva = request.form.get('texto_exencion_iva')
            config.serie_factura_default = request.form.get('serie_factura_default', 'A')
            config.pie_factura = request.form.get('pie_factura')

            db.session.commit()

            flash('Configuración fiscal actualizada exitosamente', 'success')
            return redirect(url_for('finance.economia_historico'))
        except Exception as e:
            flash(f'Error al actualizar la configuración fiscal: {str(e)}', 'error')
            db.session.rollback()
            return redirect(url_for('finance.configuracion_fiscal'))

    return render_template('economia/configuracion_fiscal.html', config=config)


@finance_bp.route('/morosidad')
@login_required
def morosidad():
    """Listado de alumnos con cuotas pendientes del año en curso"""
    from utils.finance_utils import calcular_morosidad
    morosos = calcular_morosidad()
    total_deuda = sum(m['deuda'] for m in morosos)
    return render_template('economia/morosidad.html',
                           morosos=morosos, total_deuda=total_deuda)


@finance_bp.route('/informes')
@login_required
def informes():
    """Informes: ocupación por horario, altas/bajas, ingresos por tipo"""
    hoy = date.today()

    # 1. Ocupación por horario (últimas 4 semanas): media de presentes por sesión vs capacidad
    desde = hoy - timedelta(weeks=4)
    ocupacion = []
    for h in HorarioSemanal.query.filter_by(activo=True).all():
        asistencias = Asistencia.query.filter(
            Asistencia.horario_id == h.id,
            Asistencia.fecha_clase >= desde,
            Asistencia.presente == True).all()  # noqa: E712
        fechas = {a.fecha_clase for a in asistencias}
        if not fechas:
            continue
        media = len(asistencias) / len(fechas)
        capacidad = h.capacidad_maxima or 15
        ocupacion.append({
            'nombre': f"{h.clase.nombre} {['L','M','X','J','V','S','D'][h.dia_semana]} {h.hora_inicio.strftime('%H:%M')}",
            'media': round(media, 1), 'capacidad': capacidad,
            'pct': round(100 * media / capacidad)})
    ocupacion.sort(key=lambda o: o['pct'], reverse=True)

    # 2. Altas y bajas por mes (últimos 12 meses)
    meses = []
    for i in range(11, -1, -1):
        y, m = hoy.year, hoy.month - i
        while m <= 0:
            y, m = y - 1, m + 12
        meses.append((y, m))
    altas_por_mes = {ym: 0 for ym in meses}
    bajas_por_mes = {ym: 0 for ym in meses}
    for a in Alumno.query.all():
        if a.fecha_registro:
            ym = (a.fecha_registro.year, a.fecha_registro.month)
            if ym in altas_por_mes:
                altas_por_mes[ym] += 1
        if a.fecha_baja:
            ym = (a.fecha_baja.year, a.fecha_baja.month)
            if ym in bajas_por_mes:
                bajas_por_mes[ym] += 1

    # 3. Ingresos por tipo por mes (últimos 12 meses, por fecha de cobro; incluye yogaterapia)
    tipos = ['cuota', 'matricula', 'clase_suelta', 'yogaterapia']
    ingresos = {t: {ym: 0.0 for ym in meses} for t in tipos}
    desde_pagos = date(meses[0][0], meses[0][1], 1)
    for p in Pago.query.filter(Pago.fecha_creacion >= desde_pagos).all():
        ym = (p.fecha_creacion.year, p.fecha_creacion.month)
        if ym in altas_por_mes and p.tipo_pago in ingresos:
            ingresos[p.tipo_pago][ym] += p.monto or 0

    etiquetas_meses = [f"{m:02d}/{y % 100}" for (y, m) in meses]
    return render_template('economia/informes.html',
                           ocupacion=ocupacion,
                           etiquetas_meses=etiquetas_meses,
                           altas=[altas_por_mes[ym] for ym in meses],
                           bajas=[bajas_por_mes[ym] for ym in meses],
                           ingresos={t: [ingresos[t][ym] for ym in meses] for t in tipos})
