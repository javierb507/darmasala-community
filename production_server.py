#!/usr/bin/env python3
"""
Production server for Atma Suddhi using Waitress.
This script is suitable for running as a Windows Service.
"""

import os
import sys
from waitress import serve
from app import app, db

# Ensure the root directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def start_server():
    print("🧘 Atma Suddhi - Starting Production Server (Waitress)")
    print("🌐 Port: 5001")
    
    with app.app_context():
        # Ensure database is ready
        db.create_all()
        
    serve(app, host='0.0.0.0', port=5001, threads=4)

if __name__ == "__main__":
    start_server()
