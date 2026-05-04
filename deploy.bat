@echo off
REM Production Deployment Script
REM Deploys updated files to production server at 192.168.15.51

setlocal enabledelayedexpansion

set SERVER=192.168.15.51
set USER=vm-ssh
set REMOTE_DIR=/home/vm-ssh/gartner
set SSH_KEY=%USERPROFILE%\.ssh\id_ed25519

echo.
echo ========================================
echo   Gartner DFIR Vendor Analysis Platform
echo   PRODUCTION DEPLOYMENT
echo ========================================
echo.
echo Server: %SERVER%
echo User: %USER%
echo.

REM Check if SSH key exists
if not exist "%SSH_KEY%" (
    echo ERROR: SSH key not found at %SSH_KEY%
    exit /b 1
)

echo [1/4] Stopping production service...
ssh -i "%SSH_KEY%" %USER%@%SERVER% "sudo systemctl stop gartner"
timeout /t 2 /nobreak

echo [2/4] Uploading updated files...
ssh -i "%SSH_KEY%" %USER%@%SERVER% "mkdir -p %REMOTE_DIR%/templates %REMOTE_DIR%/static"

scp -i "%SSH_KEY%" -p app.py %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p requirements.txt %USER%@%SERVER%:%REMOTE_DIR%/

REM Frontend assets (keep correct folder structure)
scp -i "%SSH_KEY%" -p templates\index.html %USER%@%SERVER%:%REMOTE_DIR%/templates/index.html
scp -i "%SSH_KEY%" -p static\app.js %USER%@%SERVER%:%REMOTE_DIR%/static/app.js
scp -i "%SSH_KEY%" -p static\style.css %USER%@%SERVER%:%REMOTE_DIR%/static/style.css
scp -i "%SSH_KEY%" -p static\rough.min.js %USER%@%SERVER%:%REMOTE_DIR%/static/rough.min.js

REM Market Insight report data
scp -i "%SSH_KEY%" -p "mdr_market_insight_reports.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "precyber_market_insight_reports.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "dfir_market_insight_reports.json" %USER%@%SERVER%:%REMOTE_DIR%/

REM Schema files
scp -i "%SSH_KEY%" -p "Preemptive_Cybersecurity_Schema.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Preemptive_Cybersecurity_Schema_v2.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Secure_by_Design_AI_Controls_Schema.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Secure_by_Design_AI_Controls_Schema_v2.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "MDR_Services_Schema.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "analyst_take_reports.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Preemptive Cybersecurity Vendor 1-0 Seed.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Preemptive Cybersecurity Vendor 1-1 Validated.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Preemptive Cybersecurity Vendor 2-0 Researched.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Preemptive Cybersecurity Vendor 2-1 Consolidated.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Offensive_Security_Schema.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Offensive Security Vendor 1-0 Seed.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Offensive Security Vendor 2-0 Researched.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Offensive Security Vendor 2-1 Consolidated.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Offensive Security Vendor 2-2 Researched.json" %USER%@%SERVER%:%REMOTE_DIR%/

REM MDR vendor files
scp -i "%SSH_KEY%" -p "MDR Services Vendor 1-0 Seed.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "MDR Services Vendor 2-0 Researched.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "MDR Services Vendor 2-1 Consolidated.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "MDR Services Vendor Capability 1-0 Seed.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "MDR Services Vendor Pricing 1-0 Seed.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "MDR Services Vendor Pricing 2-0 Researched.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "MDR Services Vendor Pricing 2-1 AI Enriched.json" %USER%@%SERVER%:%REMOTE_DIR%/

REM CNAPP files
scp -i "%SSH_KEY%" -p "CNAPP_Schema.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "CNAPP Vendor 1-0 Seed.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "CNAPP Vendor 1-1 Researched.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "CNAPP Vendor 1-2 Researched.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "CNAPP_MQ_Gap_Schema_App.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "CNAPP MQ Vendor 1-0 Seed.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "CNAPP MQ Vendor 1-1 Researched.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "CNAPP MQ Vendor 1-2 Researched.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "CNAPP MQ Evidence Ledger.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "CNAPP Vendor MQ Scores.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "CNAPP Vendor MQ Scores v2.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "cnapp_mq_market_insight_reports.json" %USER%@%SERVER%:%REMOTE_DIR%/

REM Vendor datasets
scp -i "%SSH_KEY%" -p "vendor3-3.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "vendor3-4.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "vendor3-5.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Vendor 3-6.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Vendor 3-7.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Vendor 4-0 Validated.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Vendor 4-1 Researched.json" %USER%@%SERVER%:%REMOTE_DIR%/
scp -i "%SSH_KEY%" -p "Vendor 5-0 Researched.json" %USER%@%SERVER%:%REMOTE_DIR%/

REM Optional research report (for reference)
scp -i "%SSH_KEY%" -p "RESEARCH_VALIDATION_REPORT.md" %USER%@%SERVER%:%REMOTE_DIR%/

echo [3/4] Starting production service...
ssh -i "%SSH_KEY%" %USER%@%SERVER% "sudo systemctl start gartner"
timeout /t 3 /nobreak

echo [4/4] Verifying deployment...
echo.
echo Checking service status...
ssh -i "%SSH_KEY%" %USER%@%SERVER% "sudo systemctl is-active gartner"
echo.
echo Testing API endpoint...
powershell -NoProfile -Command "$response = Invoke-WebRequest -UseBasicParsing -Uri 'http://%SERVER%:5000/api/vendors' -ErrorAction SilentlyContinue; if ($response -and $response.StatusCode -eq 200) { $count = ($response.Content | ConvertFrom-Json).Count; Write-Host ('API OK: ' + $count + ' vendors') } else { Write-Host 'API FAILED' }"

echo.
echo Verifying Vendor 5-0 dataset is listed...
powershell -NoProfile -Command "$r = Invoke-WebRequest -UseBasicParsing -Uri 'http://%SERVER%:5000/api/vendor-files' -ErrorAction SilentlyContinue; if ($r -and $r.StatusCode -eq 200) { $files = ($r.Content | ConvertFrom-Json).files; $hit = $files | Where-Object { $_.filename -eq 'Vendor 5-0 Researched.json' }; if ($hit) { Write-Host ('FOUND: ' + $hit.filename + ' (' + $hit.count + ' vendors)') } else { Write-Host 'NOT FOUND: Vendor 5-0 Researched.json' } } else { Write-Host 'API FAILED: /api/vendor-files' }"

echo.
echo Checking that Comparison Radar widget is deployed...
ssh -i "%SSH_KEY%" %USER%@%SERVER% "grep -n 'comparison-radar-chart' %REMOTE_DIR%/templates/index.html | head -n 5 || true"
ssh -i "%SSH_KEY%" %USER%@%SERVER% "grep -n 'comparison-radar-chart' %REMOTE_DIR%/static/app.js | head -n 5 || true"

echo.
echo ========================================
echo DEPLOYMENT COMPLETE
echo Application: http://%SERVER%:5000
echo ========================================
echo.
