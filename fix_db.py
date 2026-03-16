from app import app, db
from sqlalchemy import text

def add_column():
    with app.app_context():
        try:
            # Intentar añadir la columna password_hash a la tabla alumno
            db.session.execute(text("ALTER TABLE alumno ADD COLUMN password_hash VARCHAR(255)"))
            db.session.commit()
            print("✅ Columna 'password_hash' añadida correctamente a la tabla 'alumno'.")
        except Exception as e:
            print(f"⚠️ Error al añadir la columna (posiblemente ya existe): {e}")

if __name__ == "__main__":
    add_column()
