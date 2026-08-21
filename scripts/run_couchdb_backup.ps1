$ErrorActionPreference = 'Stop'
Set-Location 'C:\Gartner'
& 'C:\Gartner\.venv\Scripts\python.exe' -m gartner_app.ops.backup
if ($LASTEXITCODE -ne 0) {
    throw "CouchDB backup failed with exit code $LASTEXITCODE"
}
