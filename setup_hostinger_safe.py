#!/usr/bin/env python3
"""
SETUP HOSTINGER SAFE - Script que no limpia datos existentes
Script seguro que agrega datos sin eliminar los existentes
"""

import os
import sys

def main():
    print("🌐 CONFIGURACIÓN SEGURA PARA HOSTINGER")
    print("🧘‍♀️ Atma Suddhi - Sin eliminar datos existentes")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('app.py'):
        print("❌ Error: No se encuentra app.py")
        print("   Asegúrate de estar en el directorio correcto")
        return 1
    
    # Verificar que las dependencias están instaladas
    try:
        import flask
        import flask_sqlalchemy
        print("✅ Dependencias verificadas")
    except ImportError as e:
        print(f"❌ Error: Falta instalar dependencias")
        print(f"   Ejecuta: pip3 install -r requirements.txt")
        return 1
    
    # Ejecutar carga de datos segura
    print("\n🚀 Cargando datos de prueba (modo seguro)...")
    try:
        # Importar funciones específicas
        from testing_app import (
            app, crear_tablas, crear_usuario_admin, 
            crear_clases_completas, crear_horarios_semanales,
            crear_alumnos_diversos, crear_pagos_realistas,
            crear_sesiones_yogaterapia, crear_asistencias,
            crear_categorias_gastos, crear_proveedores,
            crear_gastos_fijos, crear_facturas_ejemplo,
            cargar_sutras, mostrar_resumen
        )
        
        with app.app_context():
            print("🏗️ Verificando estructura de tablas...")
            crear_tablas()
            
            # Ejecutar migración de campos de alumno si es necesario
            print("🔄 Verificando migración de campos de alumno...")
            try:
                from migrate_alumno_fields import migrar_campos_alumno
                migrar_campos_alumno()
            except Exception as e:
                print(f"⚠️ Migración no necesaria o ya aplicada: {e}")
            
            print("👤 Verificando usuario administrador...")
            crear_usuario_admin()
            
            print("📚 Procesando clases...")
            clases = crear_clases_completas()
            
            print("⏰ Verificando horarios...")
            # Solo crear horarios si no existen
            from app import HorarioSemanal
            if HorarioSemanal.query.count() == 0:
                horarios = crear_horarios_semanales(clases)
            else:
                print("✅ Horarios ya existen, manteniéndolos")
                horarios = HorarioSemanal.query.all()
            
            print("👥 Verificando alumnos...")
            from app import Alumno
            if Alumno.query.count() < 5:  # Solo agregar si hay pocos alumnos
                alumnos = crear_alumnos_diversos()
                crear_pagos_realistas(alumnos)
                crear_sesiones_yogaterapia(alumnos)
                crear_asistencias(alumnos, horarios)
            else:
                print("✅ Ya hay suficientes alumnos, manteniéndolos")
            
            print("📊 Verificando contabilidad...")
            from app import CategoriaGasto
            if CategoriaGasto.query.count() == 0:
                crear_categorias_gastos()
                crear_proveedores()
                crear_gastos_fijos()
                crear_facturas_ejemplo()
            else:
                print("✅ Módulo de contabilidad ya configurado")
            
            print("📜 Verificando sutras...")
            from app import Sutra
            if Sutra.query.count() == 0:
                cargar_sutras()
            else:
                print("✅ Sutras ya cargados")
            
            print("\n" + "=" * 50)
            print("🎉 ¡CONFIGURACIÓN COMPLETADA!")
            print("=" * 50)
            print("🔗 Tu aplicación está lista en tu dominio de Hostinger")
            print("🔑 Credenciales:")
            print("   👤 Usuario: admin")
            print("   🔒 Contraseña: AtmaSuddhi74")
            print("\n📊 Estado actual de la base de datos:")
            mostrar_resumen()
            print("\n🚀 ¡Listo para usar!")
            return 0
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
