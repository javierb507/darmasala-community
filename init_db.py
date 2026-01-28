from app import app, db, Usuario, Sutra, Configuracion, Tarifa, Clase
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_production():
    with app.app_context():
        print("🔧 Iniciando configuración de base de datos...")
        
        # Crear todas las tablas si no existen
        db.create_all()
        print("✅ Tablas creadas correctamente.")
        
        # Crear usuario administrador si no existe
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(
                username='admin',
                email='admin@atmasuddhi.es',
                password_hash=generate_password_hash('AtmaSuddhi74'),
                nombre='Administrador',
                apellido='Sistema',
                rol='admin'
            )
            db.session.add(admin)
            print("👤 Usuario admin creado.")
        else:
            print("👤 Usuario admin ya existe.")
            
        # Añadir configuraciones básicas
        configs_base = [
            {'clave': 'nombre_escuela', 'valor': 'ATMA SUDDHI', 'descripcion': 'Nombre de la escuela'},
            {'clave': 'logo_escuela', 'valor': 'images/logo.svg', 'descripcion': 'Ruta del logo'},
            {'clave': 'direccion', 'valor': 'Calle Principal 123', 'descripcion': 'Dirección física'},
            {'clave': 'telefono', 'valor': '+34 123 456 789', 'descripcion': 'Teléfono de contacto'}
        ]
        
        for c in configs_base:
            if not Configuracion.query.filter_by(clave=c['clave']).first():
                nueva_conf = Configuracion(clave=c['clave'], valor=c['valor'], descripcion=c['descripcion'])
                db.session.add(nueva_conf)
                print(f"⚙️ Configuración '{c['clave']}' añadida.")

        # Añadir tarifas básicas
        if Tarifa.query.count() == 0:
            tarifas_base = [
                {'nombre': 'Clase Suelta', 'precio': 15.0, 'descripcion': 'Una sesión individual'},
                {'nombre': 'Mensualidad 1 día/semana', 'precio': 45.0, 'descripcion': '4 clases al mes'},
                {'nombre': 'Mensualidad 2 días/semana', 'precio': 75.0, 'descripcion': '8 clases al mes'}
            ]
            for t in tarifas_base:
                nueva_tarifa = Tarifa(nombre=t['nombre'], precio=t['precio'], descripcion=t['descripcion'])
                db.session.add(nueva_tarifa)
            print("💰 Tarifas básicas añadidas.")

        # Añadir una clase básica para evitar listas vacías críticas
        if Clase.query.count() == 0:
            clase_demo = Clase(
                nombre='Yoga General',
                descripcion='Clase de yoga para todos los niveles',
                precio=15.0,
                duracion_minutos=60,
                color='#8B5FBF',
                activa=True
            )
            db.session.add(clase_demo)
            print("🧘 Clase básica añadida.")

        # Añadir sutras básicos si no hay ninguno
        if Sutra.query.count() == 0:
            sutras_base = [
                {
                    'numero': 'I.1',
                    'sanscrito': 'अथ योगानुशासनम्',
                    'transliteracion': 'atha yogánuśásanam',
                    'traduccion': 'Ahora comienza la enseñanza del Yoga.',
                    'libro': 'Samadhi Pada'
                },
                {
                    'numero': 'I.2',
                    'sanscrito': 'योगश्चित्तवृत्तिनिरोधः',
                    'transliteracion': 'yogaś-citta-vṛtti-nirodhaḥ',
                    'traduccion': 'Yoga es la cesación de las fluctuaciones de la mente.',
                    'libro': 'Samadhi Pada'
                }
            ]
            for s in sutras_base:
                nuevo_sutra = Sutra(
                    numero=s['numero'],
                    sanscrito=s['sanscrito'],
                    transliteracion=s['transliteracion'],
                    traduccion=s['traduccion'],
                    libro=s['libro']
                )
                db.session.add(nuevo_sutra)
            print("📖 Sutras básicos añadidos.")
            
        db.session.commit()
        print("🚀 Configuración completada con éxito.")

if __name__ == '__main__':
    init_production()
