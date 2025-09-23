#!/usr/bin/env python3
"""
Script para cargar sutras en producción
"""

from app import app, db, Sutra
import re

def cargar_sutras_produccion():
    """Cargar sutras en producción"""
    
    with app.app_context():
        # Verificar si ya existen sutras
        if Sutra.query.count() > 0:
            print("Ya existen sutras en la base de datos.")
            return
        
        # Leer el archivo de sutras
        try:
            with open('Sutras_texto.md', 'r', encoding='utf-8') as f:
                contenido = f.read()
        except FileNotFoundError:
            print("Error: No se encontró el archivo Sutras_texto.md")
            return
        
        # Patrón para extraer sutras
        patron = r'^([IVX]+\.\d+)\s*\n([^\n]+)\n([^\n]+)\n([^\n]+)$'
        sutras_encontrados = re.findall(patron, contenido, re.MULTILINE)
        
        print(f"Encontrados {len(sutras_encontrados)} sutras")
        
        # Determinar el libro actual
        libro_actual = "Samadhi Pada"
        
        for numero, sanscrito, transliteracion, traduccion in sutras_encontrados:
            # Limpiar los textos
            numero = numero.strip()
            sanscrito = sanscrito.strip()
            transliteracion = transliteracion.strip()
            traduccion = traduccion.strip()
            
            # Determinar el libro basado en el número
            if numero.startswith('I.'):
                libro_actual = "Samadhi Pada"
            elif numero.startswith('II.'):
                libro_actual = "Sadhana Pada"
            elif numero.startswith('III.'):
                libro_actual = "Vibhuti Pada"
            elif numero.startswith('IV.'):
                libro_actual = "Kaivalya Pada"
            
            # Crear el sutra
            sutra = Sutra(
                numero=numero,
                sanscrito=sanscrito,
                transliteracion=transliteracion,
                traduccion=traduccion,
                libro=libro_actual
            )
            
            db.session.add(sutra)
        
        db.session.commit()
        
        print("✅ Sutras cargados correctamente:")
        print(f"   - {len(sutras_encontrados)} sutras creados")

if __name__ == "__main__":
    cargar_sutras_produccion()
