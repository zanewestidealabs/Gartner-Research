#!/usr/bin/env pwsh
# deploy.ps1 — Push to GitHub and deploy code files to VM (192.168.15.51)
# Usage: .\deploy.ps1 [-Message "commit message"]

param(
    [string]$Message = "Deploy update"
)

$VM = "vm-ssh@192.168.15.51"
$REMOTE_PATH = "/home/vm-ssh/gartner"
$ErrorActionPreference = "Stop"

Write-Host "`n=== 1. Committing and pushing to GitHub ===" -ForegroundColor Cyan
git add -A
git commit -m $Message 2>&1 | ForEach-Object { Write-Host $_ }
git pull --rebase 2>&1 | ForEach-Object { Write-Host $_ }
git push 2>&1 | ForEach-Object { Write-Host $_ }

Write-Host "`n=== 2. Copying code files to VM ===" -ForegroundColor Cyan
$files = @(
    @{ local = "app.py";                          remote = "$REMOTE_PATH/app.py" },
    @{ local = "templates/index.html";             remote = "$REMOTE_PATH/templates/index.html" },
    @{ local = "static/app.js";                    remote = "$REMOTE_PATH/static/app.js" },
    @{ local = "static/style.css";                 remote = "$REMOTE_PATH/static/style.css" },
    @{ local = "static/docs_architecture.json";    remote = "$REMOTE_PATH/static/docs_architecture.json" },
    @{ local = "static/asmf_orbital_map.json";     remote = "$REMOTE_PATH/static/asmf_orbital_map.json" }
)

foreach ($f in $files) {
    Write-Host "  $($f.local)" -NoNewline
    scp $f.local "${VM}:$($f.remote)"
    Write-Host " ✓"
}

Write-Host "`n=== 3. Restarting server on VM ===" -ForegroundColor Cyan
$restartScript = @'
pkill -f "python3 /home/vm-ssh/gartner/app.py" 2>/dev/null
sleep 1
cd /home/vm-ssh/gartner
nohup python3 app.py > app.log 2>&1 &
echo "PID:$!"
'@
ssh $VM $restartScript

Write-Host "`n=== 4. Verifying VM is up ===" -ForegroundColor Cyan
Start-Sleep -Seconds 3
$status = ssh $VM "curl -s -o /dev/null -w '%{http_code}' http://localhost:5000/"
if ($status -eq "200") {
    Write-Host "  VM responding HTTP 200 ✓" -ForegroundColor Green
} else {
    Write-Host "  WARNING: got HTTP $status - check app.log on VM" -ForegroundColor Yellow
}

Write-Host "`n=== Deploy complete ===" -ForegroundColor Green
