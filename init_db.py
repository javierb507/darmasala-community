from app import app, db, Usuario, Sutra
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
                },
                {
                    'numero': 'I.3',
                    'sanscrito': 'तदा द्रष्टुः स्वरूपेऽवस्थानम्',
                    'transliteracion': 'tadā draṣṭuḥ svarūpe-’vasthānam',
                    'traduccion': 'Entonces el Observador descansa en su propia naturaleza.',
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
            print("🧘 Sutras básicos añadidos.")
        else:
            print("🧘 Ya existen sutras en la base de datos.")
            
        db.session.commit()
        print("🚀 Configuración completada con éxito.")

if __name__ == '__main__':
    init_production()
