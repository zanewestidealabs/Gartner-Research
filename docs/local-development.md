# Local development

## Prerequisites

- Python virtual environment at `C:\Gartner\.venv`
- Apache CouchDB 3.3.0 Windows service
- An ignored `.env` copied from `.env.example`

CouchDB is intentionally bound to `127.0.0.1:5984`. The browser talks only to
the Flask gateway; CORS on CouchDB remains disabled.

## Start and verify

```powershell
Set-Location C:\Gartner
.\.venv\Scripts\Activate.ps1
python -m flask --app app run --host 127.0.0.1 --port 5000
```

Open `http://127.0.0.1:5000`. Verify:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/health/live
Invoke-RestMethod http://127.0.0.1:5000/api/health/ready
```

The Windows service is named `Apache CouchDB`. Administrative commands:

```powershell
Get-Service 'Apache CouchDB'
Start-Service 'Apache CouchDB'
Stop-Service 'Apache CouchDB'
```

Fauxton is available locally at `http://127.0.0.1:5984/_utils/`.

## Bootstrap and migration

Administrator credentials are used only by bootstrap and maintenance commands.
The app uses the restricted `gartner_gateway` identity.

```powershell
python -m gartner_app.couchdb.bootstrap
python -m gartner_app.migration.import_canonical
python -m gartner_app.migration.reconcile_canonical
```

Migration is idempotent. Gateway-modified documents are protected from
canonical re-import.

## Tests and troubleshooting

```powershell
python -m pytest -q
python -m ruff check gartner_app tests
```

If readiness fails, check the CouchDB service, `.env`, and that port 5984 is
listening only on loopback. Do not place credentials in logs, request files, or
source control. `/api/shutdown` is disabled unless
`ENABLE_LOCAL_SHUTDOWN=true`, and even then accepts only local requests.

## Backup and restore drill

```powershell
python -m gartner_app.ops.backup
python -m gartner_app.ops.restore backups\couchdb\<timestamp>\manifest.json --prefix restore_drill
```

Restore uses isolated databases, validates semantic hashes, and removes drill
databases unless `--keep` is supplied. Copy backup sets to separate storage;
another database on the same CouchDB node is not disaster recovery.
