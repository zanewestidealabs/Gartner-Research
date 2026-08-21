# JSON Migration Inventory

`manifests/json_inventory.jsonl` is the deterministic first-pass inventory for
repository JSON data. Each line is a validated `migration_manifest` document
that can later be imported into `gartner_ops`.

Current scan:

| Metric | Value |
|---|---:|
| Files | 4,249 |
| Bytes | 678,612,328 |
| Parsed successfully | 4,249 |
| Core candidates | 93 |
| Research candidates | 79 |
| Archive candidates | 12 |
| Manifest-only candidates | 4,061 |
| Manual review required | 4 |

The scan excludes `.git`, `.venv`, `.vscode`, and `__pycache__`. The difference
from the original 4,252-file workspace count is the three local VS Code JSON
configuration files, which are not application data.

Regenerate from the repository root:

```powershell
.\.venv\Scripts\python.exe -m gartner_app.migration.inventory
```

Proposed dispositions are not final migration decisions. Canonical dataset
selection and retention approval are required before import.

Bootstrap the local CouchDB instance without entering secrets in chat:

```powershell
.\.venv\Scripts\python.exe -m gartner_app.couchdb.setup_local
```

The command prompts for the CouchDB administrator password without echoing it,
generates a gateway-service password, writes secrets only to ignored `.env`,
then creates the databases, service user, security objects, and Mango indexes.

Validate and import the manifest into `gartner_ops`:

```powershell
.\.venv\Scripts\python.exe -m gartner_app.migration.import_manifests --dry-run
.\.venv\Scripts\python.exe -m gartner_app.migration.import_manifests
```

The import uses deterministic IDs, retrieves existing revisions, and is safe to
rerun without creating duplicate logical records.
