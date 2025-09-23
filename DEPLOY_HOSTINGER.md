# 🚀 Despliegue en Hostinger - ATMA SUDDHI

## 📋 **Pasos para Desplegar**

### 1. **Preparar el Proyecto**

1. **Subir archivos a Hostinger:**
   - Sube todos los archivos del proyecto a tu directorio `public_html` o `htdocs`
   - Asegúrate de que la estructura sea:
   ```
   public_html/
   ├── app.py
   ├── wsgi.py
   ├── init_database.py
   ├── requirements.txt
   ├── static/
   ├── templates/
   ├── uploads/
   └── Sutras_texto.md
   ```

### 2. **Configurar Base de Datos MySQL**

1. **En el panel de Hostinger:**
   - Ve a "Bases de datos MySQL"
   - Crea una nueva base de datos
   - Anota: nombre de BD, usuario, contraseña, host

2. **Configurar variables de entorno:**
   - En el panel de Hostinger, ve a "Variables de entorno"
   - Agrega:
     ```
     FLASK_ENV=production
     DATABASE_URL=mysql://usuario:password@localhost/nombre_bd
     SECRET_KEY=tu-clave-secreta-muy-segura
     ```

### 3. **Instalar Dependencias**

1. **En el terminal SSH de Hostinger:**
   ```bash
   cd public_html
   pip3 install -r requirements.txt
   ```

### 4. **Inicializar Base de Datos**

1. **Ejecutar script de inicialización:**
   ```bash
   python3 init_database.py
   ```

2. **Cargar sutras (opcional):**
   ```bash
   python3 -c "
   from app import app, db, Sutra
   import re
   
   with app.app_context():
       # Cargar sutras desde el archivo
       with open('Sutras_texto.md', 'r', encoding='utf-8') as f:
           contenido = f.read()
       
       patron = r'^([IVX]+\.\d+)\s*\n([^\n]+)\n([^\n]+)\n([^\n]+)$'
       sutras = re.findall(patron, contenido, re.MULTILINE)
       
       for numero, sanscrito, transliteracion, traduccion in sutras:
           libro = 'Samadhi Pada' if numero.startswith('I.') else 'Sadhana Pada' if numero.startswith('II.') else 'Vibhuti Pada' if numero.startswith('III.') else 'Kaivalya Pada'
           
           sutra = Sutra(
               numero=numero.strip(),
               sanscrito=sanscrito.strip(),
               transliteracion=transliteracion.strip(),
               traduccion=traduccion.strip(),
               libro=libro
           )
           db.session.add(sutra)
       
       db.session.commit()
       print(f'Cargados {len(sutras)} sutras')
   "
   ```

### 5. **Configurar Servidor Web**

1. **Crear archivo .htaccess:**
   ```apache
   RewriteEngine On
   RewriteCond %{REQUEST_FILENAME} !-f
   RewriteCond %{REQUEST_FILENAME} !-d
   RewriteRule ^(.*)$ wsgi.py/$1 [QSA,L]
   ```

2. **Configurar Python en Hostinger:**
   - Ve a "Python" en el panel
   - Selecciona la versión 3.8 o superior
   - Establece el archivo de entrada: `wsgi.py`

### 6. **Permisos de Archivos**

```bash
chmod 755 wsgi.py
chmod 755 init_database.py
chmod 755 app.py
chmod -R 755 static/
chmod -R 755 templates/
chmod -R 777 uploads/
```

### 7. **Inicializar Base de Datos**

```bash
# Crear todas las tablas
python3 init_database.py

# Cargar sutras
python3 cargar_sutras_produccion.py

# Si hay problemas de login, resetear contraseña admin
python3 reset_admin_password.py

# Verificar estado de la base de datos
python3 verificar_db.py
```

### 8. **Solución de Problemas de Login**

#### Si no puedes hacer login:

1. **Verificar base de datos:**
```bash
python3 verificar_db.py
```

2. **Resetear contraseña admin:**
```bash
python3 reset_admin_password.py
```

3. **Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `AtmaSuddhi74`

4. **Verificar variables de entorno:**
```bash
echo $FLASK_ENV
echo $DATABASE_URL
echo $SECRET_KEY
```

### 9. **Verificar Despliegue**

1. **Accede a tu dominio:**
   - Deberías ver la pantalla de login
   - Usuario: `admin`
   - Contraseña: `AtmaSuddhi74`

## 🔧 **Solución de Problemas**

### Error de Base de Datos:
```bash
# Verificar conexión
python3 -c "from app import app, db; print('Conexión OK')"
```

### Error de Permisos:
```bash
chmod -R 755 .
chmod -R 777 uploads/
```

### Error de Dependencias:
```bash
pip3 install --user -r requirements.txt
```

## 📱 **Acceso Post-Despliegue**

- **URL:** `https://tu-dominio.com`
- **Usuario:** `admin`
- **Contraseña:** `AtmaSuddhi74`

## 🎯 **Características Disponibles**

✅ Sistema de autenticación completo
✅ Gestión de alumnos y sesiones
✅ Sistema de contabilidad
✅ Horarios semanales
✅ Sutra semanal en el dashboard
✅ Gestión de archivos
✅ Calendario de clases

## 📞 **Soporte**

Si tienes problemas, verifica:
1. Variables de entorno configuradas
2. Base de datos MySQL creada
3. Permisos de archivos correctos
4. Dependencias instaladas
