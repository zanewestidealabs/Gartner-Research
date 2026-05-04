# PowerShell Deployment Script for Gartner DFIR Application to Windows IIS
# ============================================================================
# SIMPLER VERSION - Using Waitress WSGI Server
# This script deploys the Gartner application from the production server to
# a Windows 11 machine running IIS at C:\inetpub\wwwroot\
# 
# Prerequisites:
#   - Windows 11 with Python 3.10+ installed
#   - SSH/SCP available (OpenSSH for Windows built-in)
#   - Run as Administrator for IIS configuration
#
# Usage: .\deploy-to-iis-simple.ps1

param(
    [string]$DeployPath = "C:\inetpub\wwwroot\gartner",
    [string]$ProductionServer = "192.168.15.51",
    [string]$SSHUser = "vm-ssh",
    [string]$WaitressPort = "5000"
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Gartner DFIR - Windows Deployment" -ForegroundColor Cyan
Write-Host "Using Waitress WSGI Server" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Step 1: Check prerequisites
Write-Host "`n[1] Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Check SCP
try {
    $scpPath = Get-Command scp -ErrorAction Stop
    Write-Host "  ✓ SCP found: $($scpPath.Source)" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ SCP not found. Install OpenSSH for Windows" -ForegroundColor Red
    exit 1
}

# Step 2: Create folder structure
Write-Host "`n[2] Creating folder structure..." -ForegroundColor Yellow

$folders = @(
    $DeployPath,
    "$DeployPath\templates",
    "$DeployPath\static",
    "$DeployPath\logs"
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "  ✓ Created: $folder" -ForegroundColor Green
    }
    else {
        Write-Host "  ✓ Exists: $folder" -ForegroundColor Gray
    }
}

# Step 3: Download files from production server
Write-Host "`n[3] Downloading files from production server ($ProductionServer)..." -ForegroundColor Yellow

$filesToDownload = @(
    "app.py",
    "requirements.txt",
    "templates/index.html",
    "static/app.js",
    "static/style.css",
    "schema3-3.json",
    "vendor3-3.json",
    "vendor3-4.json",
    "vendor3-5.json",
    "Vendor 5-0 Researched.json"
)

$downloadedCount = 0

foreach ($file in $filesToDownload) {
    $remoteFile = "/home/$SSHUser/gartner/$file"
    $localFile = Join-Path $DeployPath $file
    
    # Create subdirectory if needed
    $destDir = Split-Path $localFile -Parent
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    
    Write-Host "  Downloading: $file" -NoNewline
    
    try {
        scp -r "${SSHUser}@${ProductionServer}:${remoteFile}" "$localFile" 2>&1 | Out-Null
        Write-Host " ✓" -ForegroundColor Green
        $downloadedCount++
    }
    catch {
        Write-Host " ✗ (will continue)" -ForegroundColor Yellow
    }
}

Write-Host "  Downloaded: $downloadedCount/$($filesToDownload.Count) files" -ForegroundColor Cyan

# Step 4: Create Python virtual environment
Write-Host "`n[4] Setting up Python virtual environment..." -ForegroundColor Yellow

$venvPath = "$DeployPath\.venv"
$pipExe = "$venvPath\Scripts\pip.exe"
$pythonExe = "$venvPath\Scripts\python.exe"

if (-not (Test-Path $venvPath)) {
    Write-Host "  Creating virtual environment..."
    python -m venv $venvPath
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}
else {
    Write-Host "  ✓ Virtual environment exists" -ForegroundColor Gray
}

# Step 5: Install Python dependencies
Write-Host "`n[5] Installing Python dependencies..." -ForegroundColor Yellow

if (Test-Path $pipExe) {
    Write-Host "  Installing Flask, Werkzeug, and Waitress..."
    & $pipExe install --upgrade pip setuptools wheel --quiet
    & $pipExe install flask waitress --quiet
    
    # Install from requirements.txt if it exists
    $reqFile = "$DeployPath\requirements.txt"
    if (Test-Path $reqFile) {
        Write-Host "  Installing from requirements.txt..."
        & $pipExe install -r $reqFile --quiet
    }
    
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
}
else {
    Write-Host "  ✗ Virtual environment creation failed" -ForegroundColor Red
    exit 1
}

# Step 6: Create startup batch script
Write-Host "`n[6] Creating startup script..." -ForegroundColor Yellow

$batchScript = @"
@echo off
REM Start Gartner application with Waitress WSGI server
echo Starting Gartner DFIR Application...
cd /d "$DeployPath"
"$pythonExe" -m waitress --port=$WaitressPort --threads=10 app:app
"@

Set-Content -Path "$DeployPath\start-app.bat" -Value $batchScript
Write-Host "  ✓ Created: start-app.bat" -ForegroundColor Green

# Step 7: Create PowerShell startup wrapper
Write-Host "`n[7] Creating PowerShell startup wrapper..." -ForegroundColor Yellow

$psStartupScript = @'
# Gartner DFIR Application Starter
# Run this script to start the application on Windows

param(
    [int]$Port = 5000,
    [int]$Threads = 10,
    [switch]$Interactive = $false
)

$AppPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = "$AppPath\.venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    Write-Host "Error: Python not found in virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Gartner DFIR Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Port: $Port" -ForegroundColor White
Write-Host "Threads: $Threads" -ForegroundColor White
Write-Host "Path: $AppPath" -ForegroundColor White
Write-Host "" -ForegroundColor Cyan
Write-Host "Application will be available at: http://localhost:$Port" -ForegroundColor Yellow
Write-Host "" -ForegroundColor Cyan

Set-Location $AppPath

if ($Interactive) {
    Write-Host "Running in interactive mode (Ctrl+C to stop)" -ForegroundColor Cyan
    & $PythonExe -m waitress --port=$Port --threads=$Threads app:app
}
else {
    Write-Host "Running in background..." -ForegroundColor Cyan
    Start-Process -FilePath $PythonExe -ArgumentList @("-m", "waitress", "--port=$Port", "--threads=$Threads", "app:app") -NoNewWindow -RedirectStandardOutput "$AppPath\logs\output.log" -RedirectStandardError "$AppPath\logs\error.log"
    Write-Host "Application started. Check logs at: $AppPath\logs\" -ForegroundColor Green
}
'@

Set-Content -Path "$DeployPath\start-gartner.ps1" -Value $psStartupScript
Write-Host "  ✓ Created: start-gartner.ps1" -ForegroundColor Green

# Step 8: Create IIS web.config for URL rewrite (optional, for IIS integration)
Write-Host "`n[8] Creating IIS web.config..." -ForegroundColor Yellow

$webConfig = @"
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="Gartner Application" stopProcessing="true">
          <match url="^(.*)" ignoreCase="false" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" ignoreCase="false" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" ignoreCase="false" negate="true" />
          </conditions>
          <action type="Rewrite" url="http://localhost:$WaitressPort/{R:1}" />
        </rule>
      </rules>
      <outboundRules>
        <rule name="Rewrite Location Header">
          <match serverVariable="RESPONSE_LOCATION" pattern="^http://localhost:$WaitressPort/(.*)" />
          <action type="Rewrite" value="/{R:1}" />
        </rule>
      </outboundRules>
    </rewrite>
    <staticContent>
      <mimeType fileExtension=".json" type="application/json" />
    </staticContent>
    <httpProtocol>
      <customHeaders>
        <add name="X-Content-Type-Options" value="nosniff" />
        <add name="X-Frame-Options" value="SAMEORIGIN" />
      </customHeaders>
    </httpProtocol>
  </system.webServer>
</configuration>
"@

Set-Content -Path "$DeployPath\web.config" -Value $webConfig
Write-Host "  ✓ Created: web.config" -ForegroundColor Green

# Step 9: Validate deployment
Write-Host "`n[9] Validating deployment..." -ForegroundColor Yellow

$requiredFiles = @(
    "app.py",
    "requirements.txt",
    "templates\index.html",
    "static\app.js",
    "static\style.css",
    "schema3-3.json",
    "vendor3-3.json"
)

$allPresent = $true
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $DeployPath $file
    if (Test-Path $filePath) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    }
    else {
        Write-Host "  ✗ $file (MISSING)" -ForegroundColor Red
        $allPresent = $false
    }
}

# Step 10: Test Python environment
Write-Host "`n[10] Testing Python environment..." -ForegroundColor Yellow

try {
    $testResult = & $pythonExe -c "import flask; import waitress; print('OK')" 2>&1
    if ($testResult -eq "OK") {
        Write-Host "  ✓ Flask and Waitress installed correctly" -ForegroundColor Green
    }
}
catch {
    Write-Host "  ✗ Python module test failed" -ForegroundColor Yellow
}

# Summary
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "Deployment Summary" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deployment Path: $DeployPath" -ForegroundColor White
Write-Host "Python: $pythonExe" -ForegroundColor White
Write-Host "Port: $WaitressPort" -ForegroundColor White
Write-Host "Virtual Environment: $venvPath" -ForegroundColor White

if ($allPresent) {
    Write-Host "`n✓ DEPLOYMENT SUCCESSFUL" -ForegroundColor Green
    Write-Host "`nTo start the application:" -ForegroundColor Cyan
    Write-Host "  1. Open PowerShell" -ForegroundColor White
    Write-Host "  2. Run: cd '$DeployPath'" -ForegroundColor White
    Write-Host "  3. Run: .\start-gartner.ps1 -Interactive" -ForegroundColor White
    Write-Host "" -ForegroundColor White
    Write-Host "Or use the batch file:" -ForegroundColor Cyan
    Write-Host "  $DeployPath\start-app.bat" -ForegroundColor White
    Write-Host "" -ForegroundColor White
    Write-Host "Access the application at: http://localhost:$WaitressPort" -ForegroundColor Yellow
}
else {
    Write-Host "`n⚠ DEPLOYMENT INCOMPLETE - Some files are missing" -ForegroundColor Red
    Write-Host "Re-run the deployment script or manually copy missing files from the production server" -ForegroundColor Yellow
}

Write-Host "`n=========================================" -ForegroundColor Cyan
