---
description: Initialize the Yoga School Management System environment
---

1. Create a virtual environment:
   `python -m venv venv`

2. Install dependencies:
   `.\venv\Scripts\pip install -r requirements.txt`

3. Recreate the database:
   `.\venv\Scripts\python recrear_bd.py`

4. Load test data:
   `.\venv\Scripts\python cargar_datos_prueba.py`
