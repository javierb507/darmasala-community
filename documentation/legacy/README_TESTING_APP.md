# 🧘‍♀️ Testing App - Script de Carga de Datos de Prueba

## 📋 **Descripción**

`testing_app.py` es un script completo que inicializa la aplicación **DarmaSala** con datos de prueba realistas para desarrollo y testing. Este script es especialmente útil para:

- **Desarrollo local**: Tener datos de prueba consistentes
- **Despliegue en Hostinger**: Cargar la aplicación con datos de ejemplo
- **Demostraciones**: Mostrar todas las funcionalidades de la aplicación
- **Testing**: Probar funciones con datos variados

## 🚀 **Uso**

### Ejecución Local
```bash
cd darmasala
python testing_app.py
```

### Ejecución en Hostinger
```bash
python3 testing_app.py
```

## 📊 **Datos que Carga**

### 👤 **Usuarios**
- **1 usuario administrador**
  - Usuario: `admin`
  - Contraseña: `AtmaSuddhi74`
  - Rol: Administrador completo

### 📚 **Clases (8 tipos)**
- Yoga integral
- Yoga menopausia  
- Yoga embarazadas
- Meditación
- Hatha Yoga
- Vinyasa Flow
- Yin Yoga
- Yogaterapia

### ⏰ **Horarios Semanales (26 horarios)**
- Horarios distribuidos de lunes a domingo
- Horarios matutinos y vespertinos
- Diferentes duraciones según el tipo de clase

### 👥 **Alumnos (20 alumnos diversos)**
- **8 alumnos al corriente**: Con todos los pagos al día
- **4 alumnos bimensuales**: Con cuotas bimensuales pagadas
- **5 alumnos con pagos pendientes**: Algunos meses sin pagar
- **2 alumnos inactivos**: Sin actividad reciente
- **1 alumno desactivado**: Para probar filtros

### 💰 **Pagos (138 pagos)**
- Pagos de matrícula
- Cuotas mensuales y bimensuales
- Diferentes métodos de pago (efectivo, tarjeta, transferencia, bizum)
- Estados realistas según el tipo de alumno

### 🧘 **Sesiones de Yogaterapia (22 sesiones)**
- Sesiones detalladas con:
  - Motivo de consulta
  - Objetivos terapéuticos
  - Técnicas aplicadas
  - Posturas trabajadas
  - Observaciones del terapeuta
  - Recomendaciones para casa

### 📅 **Asistencias (181 registros)**
- Asistencias simuladas de los últimos 60 días
- Patrones realistas según el tipo de cuota
- Observaciones variadas

### 💼 **Módulo de Contabilidad**
- **10 categorías de gastos**: Alquiler, servicios, material, etc.
- **5 proveedores**: Endesa, Canal Isabel II, gestoría, etc.
- **2 gastos fijos**: Alquiler mensual y gestoría
- **12 facturas**: De los últimos 3 meses con diferentes estados

### 📜 **Sutras de Patanjali (106 sutras)**
- Carga completa desde `Sutras_texto.md`
- Si no existe el archivo, crea sutras básicos
- Organizados por libros (Samadhi, Sadhana, Vibhuti, Kaivalya)

## 🛠️ **Características del Script**

### ✅ **Robusto y Seguro**
- Limpia la base de datos antes de cargar
- Maneja errores graciosamente
- Rollback automático en caso de error
- Compatible con SQLite (desarrollo) y MySQL (producción)

### 📈 **Datos Realistas**
- Alumnos con diferentes estados de pago
- Patrones de asistencia variables
- Sesiones de yogaterapia detalladas
- Facturas y gastos del mundo real

### 🔄 **Reutilizable**
- Se puede ejecutar múltiples veces
- Limpia datos existentes automáticamente
- No genera conflictos de claves duplicadas

## 📋 **Requisitos**

- Python 3.8+
- Flask y dependencias instaladas (`pip install -r requirements.txt`)
- Archivo `app.py` en el mismo directorio
- Opcionalmente: `Sutras_texto.md` para sutras completos

## 🎯 **Casos de Uso**

### 🏠 **Desarrollo Local**
```bash
# Cargar datos frescos para desarrollo
python testing_app.py

# Iniciar aplicación
python start.py
```

### 🌐 **Despliegue en Hostinger**
```bash
# En SSH de Hostinger
cd public_html
python3 testing_app.py

# La aplicación queda lista con datos de prueba
```

### 🧪 **Testing y Demostraciones**
- Datos consistentes para pruebas
- Ejemplos de todas las funcionalidades
- Estados variados para probar edge cases

## 📊 **Resumen de Datos Creados**

| Tipo | Cantidad | Descripción |
|------|----------|-------------|
| 👤 Usuarios | 1 | Admin completo |
| 👥 Alumnos | 20 | Estados diversos |
| 📚 Clases | 8 | Tipos variados |
| ⏰ Horarios | 26 | Semana completa |
| 💰 Pagos | 138 | Realistas |
| 🧘 Yogaterapia | 22 | Detalladas |
| 📅 Asistencias | 181 | 60 días |
| 📊 Cat. Gastos | 10 | Completas |
| 🏢 Proveedores | 5 | Reales |
| 🧾 Facturas | 12 | 3 meses |
| 📜 Sutras | 106 | Completos |

## 🔑 **Credenciales de Acceso**

Una vez ejecutado el script, puedes acceder a la aplicación con:

- **URL**: `http://localhost:5000` (local) o tu dominio (producción)
- **Usuario**: `admin`
- **Contraseña**: `AtmaSuddhi74`

## ⚠️ **Advertencias**

- **¡ELIMINA TODOS LOS DATOS EXISTENTES!** antes de cargar los nuevos
- Solo para desarrollo y testing, no usar en producción con datos reales
- Hacer backup de datos importantes antes de ejecutar

## 🎉 **Resultado**

Después de ejecutar el script tendrás una aplicación completamente funcional con:

- Sistema de login operativo
- Alumnos con historiales realistas
- Horarios y clases configuradas
- Módulo de contabilidad con datos
- Sesiones de yogaterapia detalladas
- Sutras cargados para el dashboard

¡Perfecto para desarrollo, demos y despliegue en Hostinger! 🚀
