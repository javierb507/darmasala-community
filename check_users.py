from app import app
from models import Usuario
with app.app_context():
    users = Usuario.query.all()
    print(f"Users found: {len(users)}")
    for u in users:
        print(f"- {u.username} ({u.rol})")
