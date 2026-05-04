# Gartner Research Flask Server - Startup Script
# This script is called by the Windows Scheduled Task to start the server at logon.

$AppDir = "C:\Users\zwest\OneDrive\Gartner Research"
$PythonExe = "C:\Users\zwest\AppData\Local\Python\pythoncore-3.14-64\python.exe"
$LogFile = Join-Path $AppDir "server.log"

# Kill any existing instance on port 5000
$existing = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | Where-Object State -eq 'Listen'
if ($existing) {
    $existing | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
}

# Start the Flask server
Set-Location $AppDir
& $PythonExe app.py *>> $LogFile
