# CouchDB backup and restore

Run a logical backup from the repository root:

```powershell
.\.venv\Scripts\python.exe -m gartner_app.ops.backup
```

The timestamped backup contains one JSONL stream per application database and
a manifest with file hashes, semantic hashes, counts, database names, and
source-controlled security/index references. Secrets are never included.

Validate recovery without touching production databases:

```powershell
.\.venv\Scripts\python.exe -m gartner_app.ops.restore `
  backups\couchdb\<timestamp>\manifest.json `
  --prefix restore_drill
```

The command creates clean isolated databases, reapplies security, restores
documents, compares semantic hashes, and removes the drill databases.

Keep the initial migration manifest permanently. Retain accepted research
evidence and decisions for the life of the research product; retain retrieval
snapshots for seven years and operational audit events for two years unless a
later legal or owner policy requires longer. No automatic deletion is enabled.

Store at least one encrypted copy outside the CouchDB data directory and,
preferably, on another machine. For lower recovery-point objectives, configure
continuous replication to a separately managed CouchDB node.

Install the nightly 2:00 AM Windows task from an elevated PowerShell session:

```powershell
.\scripts\install_couchdb_backup_task.ps1
```

Monitor document counts, file/active sizes, compaction, and active tasks:

```powershell
.\.venv\Scripts\python.exe -m gartner_app.ops.status
```
