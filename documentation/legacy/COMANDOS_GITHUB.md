# 🚀 Comandos para Subir a GitHub

## Preparación del Repositorio

### 1. Inicializar Git (si no está inicializado)
```bash
git init
```

### 2. Configurar usuario (si es necesario)
```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@ejemplo.com"
```

### 3. Agregar todos los archivos
```bash
git add .
```

### 4. Crear commit inicial con toda la documentación
```bash
git commit -m "🎉 Release v2.0: Sistema completo de gestión de yoga

✨ Funcionalidades implementadas:
- 👥 Gestión completa de alumnos (100%)
- 💰 Sistema avanzado de pagos (95%)
- 📅 Control de asistencias (80%)
- 🧘‍♀️ Gestión de yogaterapia (75%)
- 💼 Dashboard económico (70%)
- ⚙️ Configuración del sistema (60%)

📚 Documentación completa:
- README.md actualizado
- Documentación técnica completa
- Lista de funcionalidades pendientes
- Estado actual del proyecto

🔧 Mejoras técnicas:
- Validación de pagos duplicados
- Año académico 25/26
- Interfaz responsive mejorada
- API endpoints para configuración
- Sistema de backup

🐛 Issues conocidos:
- Problema con modelo Clase (en resolución)
- Algunas rutas API pendientes
- Tests por implementar

📊 Estadísticas:
- ~4,500 líneas de código
- 28 templates HTML
- 45+ rutas Flask
- 12 modelos de BD"
```

### 5. Crear repositorio en GitHub
1. Ve a https://github.com
2. Clic en "New repository"
3. Nombre: `darmasala` o `atma-suddhi-management`
4. Descripción: "Sistema completo de gestión para escuelas de yoga - DarmaSala"
5. Público o Privado según prefieras
6. NO inicializar con README (ya tenemos uno)
7. Clic en "Create repository"

### 6. Conectar repositorio local con GitHub
```bash
# Reemplaza 'tu-usuario' y 'nombre-repo' con los valores reales
git remote add origin https://github.com/tu-usuario/darmasala.git
```

### 7. Subir código a GitHub
```bash
git branch -M main
git push -u origin main
```

## Comandos Adicionales Útiles

### Verificar estado del repositorio
```bash
git status
```

### Ver historial de commits
```bash
git log --oneline
```

### Crear una nueva rama para desarrollo
```bash
git checkout -b desarrollo
```

### Subir cambios futuros
```bash
git add .
git commit -m "Descripción de los cambios"
git push
```

## Estructura Recomendada de Commits Futuros

### Tipos de commits
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Cambios de formato (no afectan funcionalidad)
- `refactor:` Refactorización de código
- `test:` Agregar o modificar tests
- `chore:` Tareas de mantenimiento

### Ejemplos de commits
```bash
git commit -m "feat: agregar sistema de notificaciones por email"
git commit -m "fix: resolver problema de creación de BD con modelo Clase"
git commit -m "docs: actualizar documentación de API endpoints"
git commit -m "style: mejorar responsive en móviles"
git commit -m "refactor: optimizar consultas de base de datos"
git commit -m "test: agregar tests para sistema de pagos"
git commit -m "chore: actualizar dependencias de requirements.txt"
```

## Configuración del Repositorio en GitHub

### 1. Configurar README como página principal
- El README.md se mostrará automáticamente
- Asegúrate de que las imágenes y enlaces funcionen

### 2. Configurar Issues y Projects
- Habilitar Issues para tracking de bugs
- Crear labels: `bug`, `enhancement`, `documentation`, `help wanted`
- Considerar crear un Project para roadmap

### 3. Configurar Releases
```bash
# Crear tag para la versión actual
git tag -a v2.0 -m "Release v2.0: Sistema completo funcional"
git push origin v2.0
```

### 4. Configurar GitHub Pages (opcional)
- Si quieres documentación web
- Settings > Pages > Source: Deploy from a branch
- Seleccionar main branch / docs folder

## Archivos Importantes para GitHub

### .gitignore (crear si no existe)
```bash
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Backups
backups/*.db
backups/*.zip
```

### LICENSE (crear archivo de licencia)
```bash
# Crear archivo LICENSE con licencia MIT
# O la licencia que prefieras
```

## Comandos de Emergencia

### Si algo sale mal, deshacer último commit
```bash
git reset --soft HEAD~1
```

### Si necesitas forzar push (¡cuidado!)
```bash
git push --force-with-lease
```

### Clonar el repositorio en otra máquina
```bash
git clone https://github.com/tu-usuario/darmasala.git
cd darmasala
pip install -r requirements.txt
python crear_app_limpia.py
```

## Checklist Final

- [ ] Todos los archivos importantes están incluidos
- [ ] README.md está actualizado y es informativo
- [ ] Documentación completa está incluida
- [ ] .gitignore está configurado correctamente
- [ ] No hay información sensible (passwords, keys)
- [ ] requirements.txt está actualizado
- [ ] Scripts de inicialización funcionan
- [ ] Commit message es descriptivo
- [ ] Repositorio está configurado correctamente en GitHub

## Próximos Pasos Después de Subir

1. **Crear Issues** para los bugs conocidos
2. **Configurar Projects** para roadmap
3. **Invitar colaboradores** si es necesario
4. **Configurar CI/CD** (GitHub Actions)
5. **Crear documentación wiki** si es necesario
6. **Configurar notificaciones** de GitHub

¡Listo para subir a GitHub! 🚀