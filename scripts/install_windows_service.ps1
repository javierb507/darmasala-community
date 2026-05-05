<#
.SYNOPSIS
    Installs DarmaSala as a Windows Service using NSSM.
    Run this script from an Administrator PowerShell prompt.
#>

$ProjectDir = Get-Location
$ServiceName = "AtmaSuddhiYoga"
$DisplayName = "DarmaSala - Yoga Management"
$Description = "Servicio de gestión de escuela de yoga DarmaSala"
$PythonExe = Join-Path $ProjectDir "venv\Scripts\python.exe"
$ScriptPath = Join-Path $ProjectDir "production_server.py"

# NSSM variables
$NssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
$NssmZip = Join-Path $ProjectDir "nssm.zip"
$NssmPath = Join-Path $ProjectDir "nssm.exe"

# 1. Check for Administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Por favor, ejecuta este script como ADMINISTRADOR."
    exit
}

Write-Host "🧘 Preparando servicio DarmaSala..." -ForegroundColor Cyan

# 2. Ensure venv and requirements are ready
if (-not (Test-Path $PythonExe)) {
    Write-Host "📦 Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "📥 Verificando dependencias..."
& $PythonExe -m pip install -r requirements.txt

# 3. Download NSSM if not present
if (-not (Test-Path $NssmPath)) {
    Write-Host "📥 Descargando NSSM (Service Manager)..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $NssmUrl -OutFile $NssmZip
    
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($NssmZip, $ProjectDir)
    
    # Move the correct architecture exe to root
    $Arch = if ([Environment]::Is64BitOperatingSystem) { "win64" } else { "win32" }
    Move-Item "$ProjectDir\nssm-2.24\$Arch\nssm.exe" $NssmPath
    
    # Cleanup
    Remove-Item $NssmZip
    Remove-Item -Recurse "$ProjectDir\nssm-2.24"
}

# 4. Remove existing service if it exists
& $NssmPath stop $ServiceName 2>$null
& $NssmPath remove $ServiceName confirm 2>$null

# 5. Install the service
Write-Host "⚙️ Instalando el servicio Windows..." -ForegroundColor Yellow
& $NssmPath install $ServiceName $PythonExe $ScriptPath
& $NssmPath set $ServiceName AppDirectory $ProjectDir
& $NssmPath set $ServiceName DisplayName $DisplayName
& $NssmPath set $ServiceName Description $Description
& $NssmPath set $ServiceName Start SERVICE_AUTO_START

# 6. Start the service
Write-Host "🚀 Iniciando el servicio..." -ForegroundColor Green
& $NssmPath start $ServiceName

Write-Host "✅ Servicio instalado y en ejecución correctamente." -ForegroundColor Green
Write-Host "🌐 Puedes acceder en: http://localhost:5001"
Write-Host "📋 Usa 'nssm.exe edit $ServiceName' para cambiar configuraciones."
