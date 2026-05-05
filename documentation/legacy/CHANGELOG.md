# 📋 CHANGELOG - Sistema de Gestión DarmaSala

## [1.1.0] - 2025-09-16

### ✨ Nuevas Funcionalidades

#### 👥 Gestión de Alumnos Mejorada
- **Pestaña separada** para alumnos desactivados/suspendidos
- **Menú dropdown** organizado en navegación (Activos, Nuevo, Desactivados)
- **Avatar con iniciales** en lugar de ID numérico
- **Vista mejorada de pagos bimensuales** mostrando "Ene/Feb", "Mar/Abr", etc.
- **Colores mejorados**: Verde para pagados, Rojo para pendientes
- **Sistema de reactivación** de alumnos con confirmación JavaScript
- **Matrícula en formato académico** 25/26

#### 💰 Módulo Económico
- **Dashboard económico** con resumen financiero mensual
- **Gestión de proveedores** con información completa de contacto
- **Sistema de export** de datos (facturas, gastos, ingresos) a CSV
- **Categorías de gastos** predeterminadas con colores organizativos
- **Modelo de datos completo** para gestión económica:
  - Proveedores con datos fiscales
  - Facturas con control de estados y vencimientos
  - Gastos fijos con periodicidad configurable
  - Ingresos vinculados a alumnos y pagos

#### 🌐 Navegación y UX
- **Enlace directo** a página web atmasuddhi.es
- **Menús dropdown** para mejor organización
- **Tooltips informativos** con iconos ✅ y ❌
- **Diseño responsive** mejorado

### 🔧 Correcciones de Errores

- **Error "Method Not Allowed"** en eliminación de alumnos
- **Error "TemplateNotFound"** en módulo económico  
- **Cálculo de pagos bimensuales** corregido
- **Separación clara** entre alumnos activos e inactivos
- **Rutas de reactivación** implementadas correctamente

### 🏗️ Mejoras Técnicas

- **Modelos de datos** expandidos para gestión económica
- **Rutas API** para reactivación de alumnos
- **Templates organizados** en carpetas por módulo
- **Sistema de inicialización** de categorías predeterminadas
- **Validación mejorada** en formularios

### 📊 Base de Datos

- **Nuevas tablas**:
  - `Proveedor`: Gestión de proveedores
  - `CategoriaGasto`: Categorización con colores
  - `FacturaProveedor`: Control completo de facturas
  - `GastoFijo`: Gastos recurrentes con periodicidad
  - `Ingreso`: Registro de ingresos vinculados

- **Campos añadidos**:
  - `matricula_pagada` y `fecha_matricula` en Alumno
  - `tipo_pago`, `año`, `descripcion` en Pago

---

## [1.0.0] - 2025-09-15

### 🎉 Lanzamiento Inicial

#### ✨ Funcionalidades Principales
- **Gestión completa de alumnos** (alta, edición, eliminación)
- **Sistema de pagos** con cálculo automático de tarifas
- **Gestión de clases** (Yoga menopausia, Yoga integral, Yoga embarazadas, Meditación)
- **Horarios semanales** con calendario interactivo
- **Sistema de asistencias** y reportes
- **Configuración** de precios y datos de la escuela
- **Sistema de matrícula** anual
- **10 alumnos de prueba** generados automáticamente
- **Interfaz 100% en español**
- **Diseño coherente** con el logo de DarmaSala

#### 🎯 Tipos de Cuota Implementados
- Clase suelta: 15€
- 1 clase por semana: 40€
- 2 clases por semana: 70€
- 3 clases por semana: 90€
- 1 clase bimensual: 75€
- 2 clases bimensual: 135€
- Matrícula anual: 25€

#### 🏗️ Arquitectura Inicial
- **Backend**: Flask + SQLAlchemy
- **Base de datos**: SQLite para fácil despliegue
- **Frontend**: Bootstrap 5 + Jinja2
- **Diseño**: Tema púrpura/amarillo coherente con DarmaSala

#### 📱 Funcionalidades Base
- Dashboard principal con acceso a todas las funciones
- Sistema de navegación intuitivo
- Formularios con validación
- Mensajes de confirmación y error
- Datos de prueba para testing inmediato

---

## 📋 Leyenda de Tipos de Cambio

- ✨ **Nuevas Funcionalidades**: Características completamente nuevas
- 🔧 **Correcciones**: Arreglos de bugs y errores
- 🏗️ **Mejoras Técnicas**: Optimizaciones y refactoring
- 📊 **Base de Datos**: Cambios en estructura de datos
- 🌐 **UX/UI**: Mejoras en interfaz y experiencia de usuario
- 🎯 **Configuración**: Cambios en configuración y setup

---

*Mantenido por: Equipo DarmaSala*
*Formato basado en [Keep a Changelog](https://keepachangelog.com/)*
