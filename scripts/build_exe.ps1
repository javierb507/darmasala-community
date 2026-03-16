# 🛠️ Build Script for Standalone EXE: Atma Suddhi
# This script bundles Python 3.13 + Code + Libraries + Assets into a single 'dist' folder.

Write-Host "🧘 Starting Atma Suddhi Standalone Build..." -ForegroundColor Cyan

# Ensure we are in a clean state
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

# Check for PyInstaller
try {
    & .\venv\Scripts\pip.exe install pyinstaller
} catch {
    Write-Error "Could not find virtual environment. Please run .\run.bat first."
    exit
}

Write-Host "📦 Bundling application (this may take 1-2 minutes)..." -ForegroundColor Yellow

# Run PyInstaller
# --noconsole: No black terminal window
# --add-data: Include HTML templates and CSS/JS/Images
# --hidden-import: Ensure waitress and sqlalchemy are included
# --icon: Custom icon if available (falls back to default)
& .\venv\Scripts\pyinstaller.exe `
    --name "AtmaSuddhi" `
    --noconsole `
    --add-data "templates;templates" `
    --add-data "static;static" `
    --add-data "instance;instance" `
    --hidden-import "waitress" `
    --hidden-import "pandas" `
    --hidden-import "sqlalchemy" `
    --hidden-import "flask_sqlalchemy" `
    --hidden-import "flask_migrate" `
    --collect-all "pandas" `
    --collect-all "cryptography" `
    --clean `
    run.py

Write-Host "✅ Build Complete!" -ForegroundColor Green
Write-Host "📂 Your portable app is in: $(Get-Location)\dist\AtmaSuddhi" -ForegroundColor White
Write-Host "🚀 You can now run AtmaSuddhi.exe from that folder." -ForegroundColor Gray
