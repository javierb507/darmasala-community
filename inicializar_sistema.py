#!/usr/bin/env python3
"""
INICIALIZAR_SISTEMA.PY - Script oficial de inicialización para Atma Suddhi
Este script prepara el entorno de base de datos para la aplicación,
creando las tablas necesarias y el usuario administrador inicial.
"""

import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

# Asegurarse de que el directorio actual esté en el path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Usuario, Clase, CategoriaGasto, Sutra, Configuracion

def main():
    print("🧘‍♀️ INICIALIZACIÓN DEL SISTEMA ATMA SUDDHI")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 50)

    with app.app_context():
        # 1. Crear tablas
        print("\n🏗️ 1. Creando estructura de base de datos...")
        try:
            db.create_all()
            print("✅ Estructura creada correctamente.")
        except Exception as e:
            print(f"❌ Error al crear tablas: {e}")
            return

        # 2. Crear usuario administrador
        print("\n👤 2. Configurando usuario administrador...")
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            admin = Usuario(
                username='admin',
                email='admin@atmasuddhi.es',
                password_hash=generate_password_hash('AtmaSuddhi74'),
                nombre='Administrador',
                apellido='Sistema',
                rol='admin',
                activo=True
            )
            db.session.add(admin)
            try:
                db.session.commit()
                print("✅ Usuario 'admin' creado exitosamente.")
                print("   🔑 Usuario: admin")
                print("   🔑 Contraseña: AtmaSuddhi74")
            except Exception as e:
                print(f"❌ Error al crear usuario admin: {e}")
                db.session.rollback()
        else:
            print("✅ Usuario administrador ya existe.")

        # 3. Inicializar clases básicas si no hay ninguna
        print("\n📚 3. Inicializando clases básicas...")
        if Clase.query.count() == 0:
            clases_basicas = [
                Clase(nombre='Yoga Integral', descripcion='Práctica completa de yoga', color='#007bff', activa=True),
                Clase(nombre='Yoga Embarazadas', descripcion='Yoga prenatal seguro', color='#28a745', activa=True),
                Clase(nombre='Meditación', descripcion='Sesiones de meditación guiada', color='#6f42c1', activa=True)
            ]
            for c in clases_basicas:
                db.session.add(c)
            try:
                db.session.commit()
                print(f"✅ {len(clases_basicas)} clases básicas creadas.")
            except Exception as e:
                print(f"❌ Error al crear clases: {e}")
                db.session.rollback()
        else:
            print("✅ Ya existen clases configuradas.")

        # 4. Inicializar categorías de gastos
        print("\n📊 4. Configurando categorías de gastos...")
        if CategoriaGasto.query.count() == 0:
            categorias = [
                CategoriaGasto(nombre='Alquiler', descripcion='Alquiler del local'),
                CategoriaGasto(nombre='Suministros', descripcion='Luz, agua, gas'),
                CategoriaGasto(nombre='Marketing', descripcion='Publicidad y web'),
                CategoriaGasto(nombre='Material', descripcion='Esterillas, bloques, etc.'),
                CategoriaGasto(nombre='Otros', descripcion='Gastos varios')
            ]
            for cat in categorias:
                db.session.add(cat)
            try:
                db.session.commit()
                print(f"✅ {len(categorias)} categorías de gastos creadas.")
            except Exception as e:
                print(f"❌ Error al crear categorías: {e}")
                db.session.rollback()
        else:
            print("✅ Categorías de gastos ya configuradas.")

        # 5. Inicializar configuración por defecto si está vacía
        print("\n⚙️ 5. Configurando valores por defecto...")
        if Configuracion.query.count() == 0:
            config_defaults = [
                Configuracion(clave='nombre_escuela', valor='Atma Suddhi', descripcion='Nombre de la escuela'),
                Configuracion(clave='email_escuela', valor='info@atmasuddhi.es', descripcion='Email de contacto'),
                Configuracion(clave='color_primario', valor='#8B5FBF', descripcion='Color principal de la marca'),
                Configuracion(clave='color_secundario', valor='#B19CD9', descripcion='Color secundario'),
                Configuracion(clave='capacidad_centro', valor='20', descripcion='Capacidad máxima de alumnos')
            ]
            for conf in config_defaults:
                db.session.add(conf)
            
            # También configuración fiscal básica
            from app import ConfiguracionFiscal
            if ConfiguracionFiscal.query.count() == 0:
                cf = ConfiguracionFiscal(
                    nombre_titular='Tu Nombre/Empresa',
                    cif_nif='00000000X',
                    serie_factura_default='A'
                )
                db.session.add(cf)
                
            try:
                db.session.commit()
                print("✅ Configuración inicial generada.")
            except Exception as e:
                print(f"❌ Error al guardar configuración: {e}")
                db.session.rollback()
        else:
            print("✅ La configuración ya tiene datos.")

        # 6. Cargar Sutras si es necesario
        print("\n📜 6. Verificando Sutras...")
        if Sutra.query.count() == 0:
            print("ℹ️ No hay sutras cargados. Puedes cargarlos ejecutando 'cargar_sutras_produccion.py'.")
        else:
            print(f"✅ {Sutra.query.count()} sutras cargados.")

    print("\n" + "=" * 50)
    print("🎉 ¡SISTEMA LISTO PARA USAR EN HOSTINGER!")
    print("=" * 50)

if __name__ == "__main__":
    main()
