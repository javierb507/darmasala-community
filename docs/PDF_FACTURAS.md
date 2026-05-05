# Generación de PDFs de Facturas

## Descripción

El sistema ahora incluye funcionalidad completa para generar facturas profesionales en formato PDF utilizando la biblioteca ReportLab.

## Características Implementadas

### 1. Módulo PDF Generator (`utils/pdf_generator.py`)

El módulo incluye:
- **Clase `FacturaPDFGenerator`**: Generador principal de PDFs
- **Función helper `generar_pdf_factura()`**: Interfaz simplificada

### 2. Diseño del PDF

Los PDFs generados incluyen:

#### Cabecera
- Título "FACTURA" en morado (#8B5FBF)
- Datos de la empresa (desde ConfiguracionFiscal)
- Datos del cliente
- Número de factura completo
- Fechas de emisión y vencimiento
- Estado de la factura

#### Líneas de Factura
Tabla con:
- Descripción del servicio
- Cantidad
- Precio unitario
- Subtotal

#### Totales
- Base imponible
- IVA (o texto de exención si aplica)
- Retención IRPF (si aplica)
- **TOTAL A PAGAR** destacado

#### Información Adicional
- Método de pago
- Observaciones
- Pie de página con datos fiscales

### 3. Estilos y Formato

- **Colores corporativos**: Morado (#8B5FBF, #6f4a99) y beige
- **Fuentes**: Helvetica y Helvetica-Bold
- **Tamaño de página**: A4
- **Márgenes**: 20mm
- **Diseño profesional** con tablas y gradientes

### 4. Integración con Flask

#### Nueva Ruta
```python
@app.route('/facturacion/<int:factura_id>/pdf')
def descargar_factura_pdf(factura_id):
```

#### Botón de Descarga
En `templates/ver_factura.html` se ha añadido un botón prominente:
```html
<a href="{{ url_for('descargar_factura_pdf', factura_id=factura.id) }}"
   class="btn btn-primary">
    <i class="fas fa-file-pdf"></i> Descargar PDF
</a>
```

## Uso

### Desde la Interfaz Web

1. Navegar a **Facturación** en el menú principal
2. Seleccionar una factura para ver detalles
3. Hacer clic en el botón **"Descargar PDF"**
4. El PDF se descargará con el nombre: `Factura_A_0001.pdf`

### Programáticamente

```python
from utils.pdf_generator import generar_pdf_factura

# Obtener la factura y configuración fiscal
factura = FacturaEmitida.query.get(factura_id)
config_fiscal = ConfiguracionFiscal.query.first()

# Generar PDF
pdf_buffer = generar_pdf_factura(factura, config_fiscal)

# El buffer contiene el PDF en memoria
# Se puede enviar por email, guardar en disco, etc.
```

## Requisitos

### Dependencia Instalada
```
reportlab==4.0.7
```

Ya incluida en `requirements.txt`

### Configuración Necesaria

Para generar PDFs correctamente, debe estar configurada la **Configuración Fiscal** en:
- Menú → Facturación → Configuración Fiscal

Datos requeridos:
- Nombre de la empresa
- NIF
- Dirección fiscal
- Ciudad y provincia
- Texto de exención de IVA (si aplica)

## Validaciones

El sistema incluye las siguientes validaciones:

1. **Configuración Fiscal Obligatoria**: Si no existe configuración fiscal, muestra un mensaje de error y no genera el PDF

2. **Manejo de Campos Opcionales**: Los campos que pueden estar vacíos (código postal, observaciones, etc.) se manejan correctamente con valores por defecto

3. **Formato de Números**: Todos los importes se formatean con 2 decimales y el símbolo €

## Campos del Modelo Utilizados

### FacturaEmitida
- `serie`, `numero`, `numero_completo`
- `fecha_emision`, `fecha_vencimiento`
- `cliente` (relación)
- `base_imponible`, `tipo_iva`, `cuota_iva`
- `tipo_retencion`, `cuota_retencion`
- `total`
- `exenta_iva`
- `metodo_pago`
- `observaciones`
- `lineas` (relación)
- `estado`

### LineaFactura
- `descripcion`
- `cantidad`
- `precio_unitario`
- `subtotal`

### Cliente
- `nombre`
- `nif_cif`
- `direccion`
- `codigo_postal`, `ciudad`

### ConfiguracionFiscal
- `nombre_empresa`
- `nif`
- `direccion_fiscal`
- `codigo_postal`, `ciudad`, `provincia`
- `texto_exencion_iva`

## Próximas Mejoras

Posibles extensiones futuras:

1. **Logo de la empresa**: Añadir el logo desde ConfiguracionFiscal.logo_factura
2. **Firma digital**: Opción de firmar PDFs digitalmente
3. **Envío automático por email**: Integración con servicio de correo
4. **Múltiples idiomas**: Soporte para facturas en inglés/catalán
5. **Personalización de plantillas**: Permitir diferentes diseños de factura
6. **Código QR**: Añadir QR con enlace a verificación online
7. **Archivo automático**: Guardar PDFs en la carpeta del sistema

## Ejemplos de Salida

El PDF generado incluye:

```
                        FACTURA

┌─────────────────────────┬─────────────────────────┐
│ DATOS DE LA EMPRESA     │ DATOS DEL CLIENTE       │
├─────────────────────────┼─────────────────────────┤
│ DarmaSala            │ Juan Pérez              │
│ NIF: X1234567X         │ NIF/CIF: 12345678A      │
│ C/ Ejemplo, 123        │ C/ Cliente, 456         │
│ 28001 Madrid           │ 28002 Madrid            │
│ Madrid                 │                         │
└─────────────────────────┴─────────────────────────┘

Número de Factura:        A/2025/0001
Fecha de Emisión:         04/01/2026
Fecha de Vencimiento:     04/02/2026
Estado:                   EMITIDA

┌────────────────────┬──────────┬──────────────┬──────────┐
│ Descripción        │ Cantidad │ Precio Unit. │ Subtotal │
├────────────────────┼──────────┼──────────────┼──────────┤
│ Clase Yoga Integral│    10    │   15.00 €    │ 150.00 € │
└────────────────────┴──────────┴──────────────┴──────────┘

                        Base Imponible:    150.00 €
                        IVA (Exento)         0.00 €
                        Exento de IVA según art. 20.Uno.9º

                        TOTAL A PAGAR:     150.00 €

Método de pago: Transferencia

Observaciones:
Factura correspondiente a clases del mes de enero 2026

────────────────────────────────────────────────────────
DarmaSala - NIF: X1234567X
C/ Ejemplo, 123, 28001 Madrid
```

## Solución de Problemas

### Error: "Debe configurar los datos fiscales"
**Solución**: Ir a Facturación → Configuración Fiscal y completar todos los campos obligatorios

### Error: "No module named 'reportlab'"
**Solución**: Ejecutar `pip install -r requirements.txt`

### El PDF se descarga pero está vacío
**Solución**: Verificar que la factura tenga líneas de factura asociadas

### Errores de encoding en caracteres españoles
**Solución**: El sistema usa UTF-8 y fuentes estándar que soportan acentos y ñ

## Soporte Técnico

Para problemas o sugerencias relacionados con la generación de PDFs:
1. Verificar los logs de Flask
2. Revisar que los datos de la factura estén completos
3. Comprobar que ReportLab está instalado correctamente

## Historial de Cambios

### Versión 1.0 (Enero 2026)
- Implementación inicial del generador de PDFs
- Integración con el módulo de facturación
- Diseño profesional con colores corporativos
- Soporte para exención de IVA y retenciones IRPF
