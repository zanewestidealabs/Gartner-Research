# PowerShell Deployment Script for Gartner DFIR Application to Windows IIS
# ============================================================================
# This script deploys the Gartner application from the production server to
# a Windows 11 machine running IIS at C:\inetpub\wwwroot\
# 
# Prerequisites:
#   - Windows 11 with IIS installed
#   - Python 3.10+ installed
#   - SSH/SCP available (OpenSSH for Windows)
#   - Run as Administrator
#
# Usage: .\deploy-to-iis.ps1

param(
    [string]$DeployPath = "C:\inetpub\wwwroot\gartner",
    [string]$ProductionServer = "192.168.15.51",
    [string]$SSHUser = "vm-ssh",
    [string]$RemotePath = "/home/vm-ssh/gartner"
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Gartner DFIR Application - IIS Deployment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    exit 1
}

# Step 1: Create folder structure
Write-Host "`n[1] Creating folder structure..." -ForegroundColor Yellow

$folders = @(
    $DeployPath,
    "$DeployPath\templates",
    "$DeployPath\static",
    "$DeployPath\logs"
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "  Created: $folder" -ForegroundColor Green
    }
    else {
        Write-Host "  Already exists: $folder" -ForegroundColor Gray
    }
}

# Step 2: Download files from production server
Write-Host "`n[2] Downloading files from production server..." -ForegroundColor Yellow

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

foreach ($file in $filesToDownload) {
    $remoteSrc = "$RemotePath/$file"
    $localDest = Join-Path $DeployPath $file
    
    # Create subdirectory if needed
    $destDir = Split-Path $localDest -Parent
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    
    Write-Host "  Downloading: $file"
    $scpCmd = "scp -r `"$SSHUser@$ProductionServer`:$remoteSrc`" `"$localDest`""
    
    try {
        Invoke-Expression $scpCmd | Out-Null
        Write-Host "    ✓ Downloaded" -ForegroundColor Green
    }
    catch {
        Write-Host "    ✗ Failed to download: $_" -ForegroundColor Red
    }
}

# Step 3: Create Python virtual environment
Write-Host "`n[3] Setting up Python virtual environment..." -ForegroundColor Yellow

$venvPath = "$DeployPath\.venv"

if (-not (Test-Path $venvPath)) {
    Write-Host "  Creating virtual environment..."
    & python -m venv $venvPath
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}
else {
    Write-Host "  ✓ Virtual environment already exists" -ForegroundColor Gray
}

# Step 4: Install Python dependencies
Write-Host "`n[4] Installing Python dependencies..." -ForegroundColor Yellow

$pipExe = "$venvPath\Scripts\pip.exe"
$pythonExe = "$venvPath\Scripts\python.exe"

if (Test-Path $pipExe) {
    Write-Host "  Installing Flask and dependencies..."
    & $pipExe install -r "$DeployPath\requirements.txt" --upgrade
    & $pipExe install waitress  # WSGI server for Windows/IIS
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
}
else {
    Write-Host "  ✗ Python virtual environment setup failed" -ForegroundColor Red
    exit 1
}

# Step 5: Create IIS web.config
Write-Host "`n[5] Creating IIS web.config..." -ForegroundColor Yellow

$webConfigContent = @"
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <appSettings>
    <add key="pythonPath" value="$venvPath\Scripts\python.exe" />
    <add key="pythonVirtualEnv" value="$venvPath" />
  </appSettings>

  <system.webServer>
    <staticContent>
      <mimeType fileExtension=".json" type="application/json" />
    </staticContent>

    <handlers>
      <add name="Python FastCGI" path="*" verb="*" modules="FastCgiModule" scriptProcessor="$pythonExe|app" resourceType="Unspecified" requireAccess="Script" />
    </handlers>

    <httpErrors errorMode="Custom">
      <error statusCode="404" path="/api/notfound" responseMode="ExecuteURL" />
    </httpErrors>

    <rewrite>
      <rules>
        <rule name="Flask Rule" stopProcessing="true">
          <match url=".*" ignoreCase="false" />
          <conditions>
            <add input="{REQUEST_FILENAME}" matchType="IsFile" ignoreCase="false" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" ignoreCase="false" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>

    <defaultDocument>
      <files>
        <add value="index.html" />
      </files>
    </defaultDocument>

    <directoryBrowse enabled="false" />
    
    <security>
      <authentication>
        <anonymousAuthentication enabled="true" />
      </authentication>
    </security>

    <httpProtocol>
      <customHeaders>
        <add name="X-Content-Type-Options" value="nosniff" />
        <add name="X-Frame-Options" value="SAMEORIGIN" />
        <add name="Access-Control-Allow-Origin" value="*" />
      </customHeaders>
    </httpProtocol>
  </system.webServer>

  <system.webServer>
    <httpLogging dontLog="true" />
  </system.webServer>
</configuration>
"@

$webConfigPath = "$DeployPath\web.config"
Set-Content -Path $webConfigPath -Value $webConfigContent
Write-Host "  ✓ web.config created" -ForegroundColor Green

# Step 6: Create startup script for Waitress WSGI
Write-Host "`n[6] Creating application wrapper..." -ForegroundColor Yellow

$startupScriptContent = @"
"""
Waitress WSGI Application Wrapper
Runs Flask application on Windows/IIS with Waitress
"""
import sys
import os

# Add the application directory to Python path
sys.path.insert(0, r'$DeployPath')

from app import app

if __name__ == '__main__':
    # For production on Windows
    from waitress import serve
    serve(app, host='127.0.0.1', port=8080, threads=10, _quiet=True)
"@

Set-Content -Path "$DeployPath\wsgi.py" -Value $startupScriptContent
Write-Host "  ✓ Startup script created" -ForegroundColor Green

# Step 7: Create IIS Application Pool
Write-Host "`n[7] Configuring IIS Application Pool..." -ForegroundColor Yellow

$appPoolName = "GartnerPool"
$siteName = "gartner"

try {
    # Import IIS Module
    Import-Module WebAdministration -ErrorAction Stop

    # Create Application Pool if it doesn't exist
    if (-not (Test-Path "IIS:\AppPools\$appPoolName")) {
        New-WebAppPool -Name $appPoolName
        $pool = Get-Item "IIS:\AppPools\$appPoolName"
        $pool.processModel.identityType = "ApplicationPoolIdentity"
        $pool | Set-Item
        Write-Host "  ✓ Application Pool created: $appPoolName" -ForegroundColor Green
    }
    else {
        Write-Host "  ✓ Application Pool already exists: $appPoolName" -ForegroundColor Gray
    }

    # Create IIS Website if it doesn't exist
    $iisPath = "IIS:\Sites\$siteName"
    if (-not (Test-Path $iisPath)) {
        New-WebSite -Name $siteName -PhysicalPath $DeployPath -Port 8080 -ApplicationPool $appPoolName
        Write-Host "  ✓ Website created: $siteName on port 8080" -ForegroundColor Green
    }
    else {
        Write-Host "  ✓ Website already exists: $siteName" -ForegroundColor Gray
    }

    # Assign Application Pool
    $site = Get-Item $iisPath
    $site.applicationPool = $appPoolName
    $site | Set-Item
    Write-Host "  ✓ Application Pool assigned" -ForegroundColor Green
}
catch {
    Write-Host "  ⚠ IIS Module error: $_" -ForegroundColor Yellow
    Write-Host "    Note: IIS Management Module may need to be installed" -ForegroundColor Yellow
}

# Step 8: Set folder permissions
Write-Host "`n[8] Setting folder permissions..." -ForegroundColor Yellow

$identities = @(
    "IIS AppPool\$appPoolName",
    "IUSR"
)

foreach ($identity in $identities) {
    try {
        $acl = Get-Acl $DeployPath
        $ace = New-Object System.Security.AccessControl.FileSystemAccessRule($identity, "Modify", "ContainerInherit,ObjectInherit", "None", "Allow")
        $acl.SetAccessRule($ace)
        Set-Acl -Path $DeployPath -AclObject $acl
        Write-Host "  ✓ Permissions set for: $identity" -ForegroundColor Green
    }
    catch {
        Write-Host "  ⚠ Could not set permissions for $identity : $_" -ForegroundColor Yellow
    }
}

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

# Step 10: Summary
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "Deployment Summary" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deployment Path: $DeployPath" -ForegroundColor White
Write-Host "IIS Site: $siteName" -ForegroundColor White
Write-Host "Application Pool: $appPoolName" -ForegroundColor White
Write-Host "Port: 8080" -ForegroundColor White
Write-Host "Python Virtual Env: $venvPath" -ForegroundColor White

if ($allPresent) {
    Write-Host "`n✓ DEPLOYMENT SUCCESSFUL" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Open IIS Manager (inetmgr)" -ForegroundColor White
    Write-Host "2. Right-click '$siteName' site and select 'Restart'" -ForegroundColor White
    Write-Host "3. Navigate to http://localhost:8080" -ForegroundColor White
    Write-Host "4. Check Event Viewer > Windows Logs > Application for any errors" -ForegroundColor White
}
else {
    Write-Host "`n✗ DEPLOYMENT INCOMPLETE - Some files are missing" -ForegroundColor Red
    exit 1
}

Write-Host "`n=========================================" -ForegroundColor Cyan
