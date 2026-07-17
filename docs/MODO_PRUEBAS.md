# Modo de Pruebas - Sistema de Gestión DarmaSala

## Descripción General

El Modo de Pruebas es una funcionalidad de administración que permite gestionar fácilmente los datos de prueba del sistema. Es ideal para:
- Evaluar todas las funcionalidades de la aplicación
- Hacer demostraciones del sistema
- Desarrollar y probar nuevas características
- Resetear el sistema para empezar de cero

## Acceso

**Ruta**: Configuración → Modo de Pruebas
**URL directa**: `/modo-pruebas`
**Requisitos**: Solo para administradores

## Funcionalidades

### 1. Cargar Datos de Prueba Completos

Un solo clic carga un conjunto completo de datos realistas para simular una escuela de yoga en funcionamiento.

#### Datos Incluidos:

**Alumnos (10)**
- Nombres y apellidos variados
- Diferentes tipos de cuotas:
  - 1 clase semanal
  - 2 clases semanales
  - Plana (ilimitada)
  - 1 clase bimensual
  - 2 clases bimensuales
- Estados de matrícula variados (75% pagadas)
- DNI generados aleatoriamente

**Horarios Semanales (16)**
- **Lunes a Viernes 10:00-11:15**: Yoga Integral
- **Lunes a Viernes 18:30-19:15**: Meditación
- **Lunes a Viernes 19:30-20:45**: Yoga Integral
- **Solo Lunes 17:00-18:15**: Yoga Menopausia

**Asistencias (~450)**
- Generadas para las últimas 4 semanas
- Distribución realista (60-90% de asistencia por clase)
- Vinculadas a horarios y alumnos específicos
- Solo para fechas pasadas

**Clientes para Facturación (5)**
- 2 Particulares (vinculados a alumnos)
- 2 Empresas (Centro Deportivo, Ayuntamiento)
- 1 Autónomo (vinculado a alumno)
- Datos completos: NIF/CIF, dirección, contacto

**Facturas Emitidas (18)**
- Distribuidas en los últimos 6 meses
- 2-4 facturas por mes
- Conceptos variados:
  - Clases mensuales
  - Talleres de meditación
  - Sesiones individuales
  - Cursos de yoga
- Estados: 75% pagadas, 25% pendientes
- Cálculo correcto de IVA exento y retención IRPF

**Proveedores (5)**
- Suministros Yoga Spain SL (Material)
- Inmobiliaria Centro SL (Alquiler)
- Iberdrola SA (Suministros)
- Material Deportivo Pro (Material)
- Seguros Mapfre (Seguros)

**Gastos Fijos (3)**
- **Alquiler del Local**: 950€/mes (Mensual)
- **Suministro Eléctrico**: 120€/mes (Mensual)
- **Seguro de Responsabilidad Civil**: 450€/año (Anual)

**Facturas de Proveedores (24)**
- Distribuidas en los últimos 6 meses
- 3-5 facturas por mes
- Importes realistas según categoría:
  - Alquiler: 800-1000€
  - Suministros: 50-150€
  - Material: 100-500€
  - Seguros: 150-300€
- Estados: mayoría pagadas, algunas pendientes

**Configuración Fiscal**
- Datos de ejemplo de la escuela
- IVA exento configurado
- Retención IRPF al 7%
- Serie de factura 'A'

### 2. Resetear Sistema Completo

Elimina los datos transaccionales para empezar de cero, conservando catálogos y configuración.

#### Datos que SE ELIMINAN:
- ❌ Todos los alumnos e inscripciones a horarios
- ❌ Todos los pagos
- ❌ Todas las asistencias
- ❌ Todos los eventos de calendario
- ❌ Todos los clientes
- ❌ Todas las facturas emitidas y líneas de factura
- ❌ Todas las facturas de proveedores
- ❌ Todos los gastos mensuales
- ❌ Todas las sesiones de yogaterapia y sus archivos adjuntos

#### Datos que SE MANTIENEN:
- ✅ Usuarios y configuración general
- ✅ Clases, tipos de clase, horarios semanales e instructores
- ✅ Categorías de gastos (Alquiler, Suministros, etc.)
- ✅ Tarifas configuradas
- ✅ Gastos fijos y proveedores
- ✅ Sutras y configuración fiscal

Nota: si cargaste el dataset de demo, sus filas de catálogo (proveedores,
gastos fijos, horarios, clases) sobreviven al reset por diseño — el reset
limpia movimientos, no catálogos.

#### Protección:
- Solo administradores (`@admin_required`)
- Confirmación doble obligatoria
- Advertencias claras sobre irreversibilidad
- Mensajes de confirmación en la interfaz

### 3. Estadísticas en Tiempo Real

El panel muestra el estado actual del sistema:

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│  Alumnos    │  Horarios   │  Facturas   │  Facturas   │
│             │             │  Emitidas   │  Proveedores│
└─────────────┴─────────────┴─────────────┴─────────────┘
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Asistencias │  Clientes   │ Proveedores │ Gastos Fijos│
└─────────────┴─────────────┴─────────────┴─────────────┘
```

## Archivos del Sistema

### Scripts de Carga de Datos

**`cargar_datos_prueba_completos.py`**
- Script unificado para carga completa de datos
- Parámetro `modo_web=True` para ejecución sin interacción
- Parámetro `modo_web=False` para ejecución desde consola con mensajes
- Genera todos los tipos de datos de prueba
- Incluye generación de asistencias realistas

**Scripts Anteriores (Aún Disponibles)**
- `crear_datos_prueba_economia.py` - Solo datos económicos
- `crear_horarios_prueba.py` - Solo horarios semanales
- `add_horarios.py` - Script original de horarios

### Migraciones Aplicadas

**`migrate_add_proveedor_to_gastoFijo.py`**
- Añade campo `proveedor_id` a la tabla `gasto_fijo`
- Permite vincular gastos fijos con proveedores específicos

## Rutas del Sistema

```python
# Modo de Pruebas
GET  /modo-pruebas              # Panel de gestión
POST /cargar-datos-prueba       # Cargar datos de prueba
POST /resetear-sistema          # Resetear todo
```

## Casos de Uso

### Caso 1: Evaluar el Sistema por Primera Vez
1. Instalar la aplicación
2. Acceder a Configuración → Modo de Pruebas
3. Hacer clic en "Cargar Datos de Prueba"
4. Explorar todas las secciones con datos realistas

### Caso 2: Demostración a un Cliente
1. Resetear el sistema para tener datos limpios
2. Cargar datos de prueba frescos
3. Mostrar todas las funcionalidades con datos coherentes

### Caso 3: Desarrollo de Nuevas Funcionalidades
1. Cargar datos de prueba para tener un entorno completo
2. Desarrollar y probar la nueva funcionalidad
3. Si es necesario, resetear y volver a cargar

### Caso 4: Empezar con Datos Reales
1. Resetear el sistema completamente
2. Configurar datos fiscales reales
3. Empezar a introducir datos reales de alumnos y clases

## Ventajas del Sistema

### Para Desarrollo
- ✅ Datos realistas y coherentes
- ✅ Carga rápida (< 10 segundos)
- ✅ Incluye relaciones complejas (asistencias, facturas, etc.)
- ✅ Fácil de resetear y empezar de nuevo

### Para Demostración
- ✅ Datos variados que muestran todas las funcionalidades
- ✅ Estadísticas significativas para gráficos y reportes
- ✅ Casos de uso diversos (particulares, empresas, autónomos)
- ✅ Histórico de 6 meses de datos económicos

### Para Producción
- ✅ Reseteo limpio para empezar con datos reales
- ✅ Mantiene la configuración base importante
- ✅ No afecta a tipos de clases ni categorías configuradas
- ✅ Protección contra borrados accidentales

## Seguridad

### Medidas Implementadas
1. **Confirmación Doble**: Dos ventanas de confirmación para reseteo
2. **Advertencias Visuales**: Colores y mensajes claros
3. **Logs del Sistema**: Imprime en consola qué se está eliminando
4. **Flash Messages**: Confirmación visible de acciones completadas
5. **Rollback Automático**: Si hay error, se deshacen los cambios

### Restricciones
- Solo accesible desde la sección de configuración
- Marcado como "Solo Administradores"
- Requiere confirmación explícita del usuario

## Mantenimiento

### Actualizar Datos de Prueba
Para modificar los datos generados, editar:
```python
# cargar_datos_prueba_completos.py
# Líneas relevantes:
# 66-77: Definir alumnos
# 136-145: Definir horarios
# 200-210: Definir clientes
# 285-319: Definir conceptos de facturas
# 370-408: Definir proveedores
# 422-442: Definir gastos fijos
```

### Añadir Nuevos Tipos de Datos
1. Añadir generación en `cargar_datos_prueba_completos.py`
2. Añadir eliminación en ruta `resetear_sistema()`
3. Añadir contador en estadísticas del panel

## Mejoras Futuras Posibles

- [ ] Selector de cantidad de datos a generar
- [ ] Exportar configuración actual antes de resetear
- [ ] Importar/Exportar sets de datos de prueba personalizados
- [ ] Generar datos para períodos específicos
- [ ] Añadir pagos de alumnos en los datos de prueba
- [ ] Incluir eventos especiales en el calendario
- [ ] Generar informes fiscales de prueba

## Conclusión

El Modo de Pruebas es una herramienta esencial para el desarrollo, testing y demostración del sistema. Proporciona un entorno completo y realista con un solo clic, y permite resetear fácilmente para empezar de nuevo.
