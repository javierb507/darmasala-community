"""
Script para actualizar los colores de las clases existentes
"""
from app import app, db, Clase

def update_class_colors():
    """Actualiza los colores de las clases existentes con valores predeterminados"""
    with app.app_context():
        # Colores predeterminados para cada clase
        colores_default = {
            'Yoga integral': '#4ECDC4',
            'Yoga menopausia': '#FF6B6B',
            'Yoga embarazadas': '#FFE66D',
            'Meditación': '#A8E6CF'
        }

        clases = Clase.query.all()
        actualizadas = 0

        for clase in clases:
            # Si la clase no tiene color o tiene el color por defecto genérico
            if not clase.color or clase.color == '#4ECDC4':
                # Buscar si hay un color predeterminado para esta clase
                if clase.nombre in colores_default:
                    clase.color = colores_default[clase.nombre]
                    actualizadas += 1
                    print(f"✓ {clase.nombre}: {clase.color}")
                else:
                    # Si no hay color predefinido, asignar uno por defecto
                    if not clase.color:
                        clase.color = '#6c757d'  # Gris por defecto
                        actualizadas += 1
                        print(f"⚪ {clase.nombre}: {clase.color} (color por defecto)")

        db.session.commit()

        print(f"\n{'='*60}")
        print(f"OK - {actualizadas} clases actualizadas con colores")
        print(f"{'='*60}")

if __name__ == "__main__":
    print("=" * 60)
    print("ACTUALIZACIÓN DE COLORES DE CLASES")
    print("=" * 60)
    print()

    update_class_colors()

    print()
    print("=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)
