# Sistema de Facturación - DarmaSala

## Resumen del Sistema

El sistema de facturación implementado cumple con la normativa fiscal española para autónomos y pequeñas empresas. Incluye gestión completa de facturas emitidas (ingresos) y facturas de proveedores (gastos).

## Características Implementadas

### 1. Configuración Fiscal

**Ruta:** `/facturacion/configuracion-fiscal`
**Template:** `templates/configuracion_fiscal.html`

Permite configurar:
- Datos de la empresa (nombre, NIF, dirección fiscal)
- Información de contacto (teléfono, email)
- Epígrafe IAE
- Régimen de IVA (exento, general, recargo de equivalencia)
- Tipo de retención IRPF por defecto (0%, 7%, 15%)
- Exención de IVA con texto legal
- Serie de factura por defecto
- Pie de factura (texto legal)

### 2. Gestión de Clientes

**Rutas:**
- `/facturacion/clientes` - Listado de clientes
- `/facturacion/clientes/nuevo` - Crear cliente
- `/facturacion/clientes/<id>/editar` - Editar cliente

**Características:**
- Almacena NIF/CIF único
- Dirección completa con código postal, ciudad, provincia
- Tipo de cliente (particular, empresa, autónomo)
- Vinculación opcional con alumnos
- Estado activo/inactivo

### 3. Facturas Emitidas (Ingresos)

**Rutas:**
- `/facturacion` - Dashboard de facturación
- `/facturacion/nueva` - Crear nueva factura
- `/facturacion/<id>` - Ver detalle de factura
- `/facturacion/<id>/marcar_pagada` - Marcar como pagada
- `/facturacion/<id>/anular` - Anular factura

**Características:**
- Numeración secuencial automática por serie y año
- Múltiples líneas de factura con descripción, cantidad y precio
- Cálculo automático de totales
- Exención de IVA (Art. 20.Uno.9º Ley 37/1992)
- Retención IRPF automática según tipo de cliente
- Estados: emitida, pagada, anulada
- Tarifas rápidas para agregar servicios comunes
- Observaciones y notas
- Vista de impresión optimizada

**Cálculos Fiscales:**
- Base Imponible = Suma de líneas
- Cuota IVA = Base × (Tipo IVA / 100) [si no está exento]
- Cuota Retención = Base × (Tipo IRPF / 100)
- Total a Pagar = Base + Cuota IVA - Cuota Retención

### 4. Gestión de Proveedores

**Rutas:**
- `/economia/proveedores` - Listado de proveedores
- `/economia/proveedores/nuevo` - Crear proveedor

**Características:**
- Datos completos del proveedor (nombre, CIF/NIF, dirección)
- Persona de contacto
- Datos de contacto (teléfono, email)
- Notas sobre condiciones comerciales
- Estado activo/inactivo

### 5. Facturas de Proveedores (Gastos)

**Rutas:**
- `/economia/facturas` - Listado de facturas de proveedores
- `/economia/facturas/nueva` - Registrar nueva factura de proveedor

**Características:**
- Número de factura del proveedor
- Asignación a proveedor y categoría de gasto
- Fecha de factura y vencimiento (calculado automáticamente +30 días)
- Importe sin IVA + IVA = Total
- Descripción del servicio/producto
- Estados: pendiente, pagada, vencida
- Alertas de facturas vencidas
- Método de pago

**Categorías de Gastos:**
1. Alquiler (#dc3545 - Rojo)
2. Suministros (#ffc107 - Amarillo)
3. Material (#28a745 - Verde)
4. Marketing (#007bff - Azul)
5. Formación (#6f42c1 - Morado)
6. Seguros (#fd7e14 - Naranja)
7. Mantenimiento (#20c997 - Turquesa)
8. Otros (#6c757d - Gris)

### 6. Dashboard Económico Unificado

**Ruta:** `/economia`
**Template:** `templates/economia/dashboard.html`

**Muestra:**
- Total facturado en el año actual
- Facturas emitidas pagadas y pendientes
- Gastos del mes actual
- Facturas de proveedores pendientes y vencidas
- Últimas facturas emitidas (5 más recientes)
- Acciones rápidas para todas las operaciones

**Diseño:**
- Dos columnas: Ingresos (izquierda) y Gastos (derecha)
- Tarjetas con estadísticas resumidas
- Alertas visuales para facturas vencidas
- Enlaces directos a todas las funciones

## Modelos de Base de Datos

### Cliente
```python
- id (PK)
- nombre
- nif_cif (único)
- direccion, codigo_postal, ciudad, provincia, pais
- email, telefono
- tipo_cliente (particular/empresa/autonomo)
- activo (boolean)
- alumno_id (FK opcional)
```

### ConfiguracionFiscal
```python
- id (PK)
- nombre_empresa, nif
- direccion_fiscal, codigo_postal, ciudad, provincia
- telefono, email
- epigrafe_iae
- regimen_iva, tipo_retencion_default
- exento_iva (boolean)
- texto_exencion_iva
- serie_factura_default
- pie_factura
```

### FacturaEmitida
```python
- id (PK)
- serie, numero, numero_completo (único)
- fecha_emision, fecha_prestacion
- cliente_id (FK)
- base_imponible, cuota_iva, cuota_retencion, total
- exenta_iva, tipo_iva, tipo_retencion
- motivo_exencion
- estado (emitida/pagada/anulada)
- fecha_pago, metodo_pago
- observaciones
```

### LineaFactura
```python
- id (PK)
- factura_id (FK)
- orden
- descripcion
- cantidad, precio_unitario, subtotal
```

### Proveedor
```python
- id (PK)
- nombre, cif_nif
- direccion, telefono, email
- contacto_principal
- notas
- activo (boolean)
```

### FacturaProveedor
```python
- id (PK)
- numero_factura
- proveedor_id (FK)
- categoria_id (FK)
- fecha_factura, fecha_vencimiento
- importe_sin_iva, iva, importe_total
- descripcion, notas
- estado (pendiente/pagada/vencida)
- fecha_pago, metodo_pago
```

### CategoriaGasto
```python
- id (PK)
- nombre (único)
- color (código hexadecimal)
- activa (boolean)
```

## Cumplimiento Normativo

### Ley 37/1992 - IVA
- Art. 20.Uno.9º: Exención de IVA para actividades de enseñanza (yoga, meditación)
- Texto de exención configurable
- Tipos de IVA: 0%, 4%, 10%, 21%

### IRPF - Retenciones
- 0%: Particulares (sin retención)
- 7%: Actividades profesionales
- 15%: Actividades artísticas y deportivas

### Numeración de Facturas
- Formato: {SERIE}/{AÑO}/{NÚMERO}
- Ejemplo: A/2025/0001
- Secuencial por serie y año
- Sin saltos ni duplicados
- Basado en fecha de emisión (no fecha del sistema)

### Conservación
- Las facturas se mantienen incluso si se anulan (obligación legal)
- Estado "anulada" las excluye de cálculos pero mantiene registro
- Periodo de conservación: 4 años (recordado en configuración)

## Datos de Prueba

Script: `crear_datos_prueba_economia.py`

**Genera:**
- 5 clientes (particulares, empresas, autónomos)
- 18 facturas emitidas distribuidas en 6 meses
- 5 proveedores
- 24 facturas de proveedores distribuidas en 6 meses
- 8 categorías de gastos
- Configuración fiscal de ejemplo

## Funcionalidades JavaScript

### Formulario de Nueva Factura Emitida
- Agregar/eliminar líneas dinámicamente
- Botones de tarifas rápidas
- Cálculo automático de subtotales
- Cálculo en tiempo real de IVA y retención
- Toggle de IVA exento
- Asignación automática de retención según tipo de cliente

### Formulario de Nueva Factura de Proveedor
- Cálculo automático del total con IVA
- Fecha de vencimiento automática (+30 días)
- Actualización en tiempo real de importes

## Templates Creados

1. `templates/configuracion_fiscal.html` - Configuración fiscal del negocio
2. `templates/facturacion.html` - Dashboard de facturación
3. `templates/clientes_facturacion.html` - Listado de clientes
4. `templates/nuevo_cliente.html` - Formulario de cliente
5. `templates/editar_cliente.html` - Edición de cliente
6. `templates/nueva_factura.html` - Formulario de factura emitida
7. `templates/ver_factura.html` - Detalle de factura con impresión
8. `templates/economia/dashboard.html` - Dashboard económico unificado
9. `templates/economia/facturas.html` - Listado de facturas de proveedores
10. `templates/economia/nueva_factura.html` - Formulario de factura de proveedor
11. `templates/economia/proveedores.html` - Listado de proveedores
12. `templates/economia/nuevo_proveedor.html` - Formulario de proveedor

## Próximas Funcionalidades Pendientes

### Alta Prioridad
1. **Generación de PDF** para facturas emitidas
   - Formato oficial con todos los datos fiscales
   - Descarga y envío por email

2. **Informes Fiscales**
   - Modelo 303 (IVA trimestral)
   - Modelo 130 (IRPF trimestral)
   - Modelo 390 (Resumen anual IVA)
   - Libro de facturas emitidas
   - Libro de facturas recibidas

### Media Prioridad
3. **Facturación Recurrente**
   - Generación automática de facturas mensuales
   - Vinculación con cuotas de alumnos

4. **Alertas y Notificaciones**
   - Vencimientos de facturas de proveedores
   - Plazos tributarios
   - Facturas pendientes de cobro

5. **Exportación de Datos**
   - CSV para contabilidad
   - Formato compatible con software contable

### Baja Prioridad
6. **Estadísticas Avanzadas**
   - Gráficos de ingresos/gastos
   - Proyecciones
   - Comparativas año a año

7. **Facturas Rectificativas**
   - Corrección de facturas emitidas
   - Trazabilidad completa

## Notas de Implementación

- Todas las interfaces están en español
- Diseño responsive con Bootstrap 5
- Iconos de Font Awesome
- Validación de formularios HTML5
- Flash messages para feedback al usuario
- Protección contra duplicados (NIF únicos, números de factura únicos)
- Soft delete (activo/inactivo) en lugar de borrado físico
