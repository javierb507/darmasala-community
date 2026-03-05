from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tables: {tables}")
    if 'inscripciones_horarios' not in tables:
        print("Creating table...")
        db.create_all()
        print("Done.")
    else:
        print("Table already exists.")
