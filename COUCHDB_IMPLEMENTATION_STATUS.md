# CouchDB Implementation Status

Last updated: 2026-07-23

## Completed

- [x] Repository-specific migration plan.
- [x] Official Apache CouchDB Windows MSI downloaded and SHA-256 verified.
- [x] Apache CouchDB 3.3.0 installed as an automatic Windows service.
- [x] CouchDB verified listening only on `127.0.0.1:5984`.
- [x] Anonymous database and node-configuration access verified as HTTP 401.
- [x] Mermaid, Markdown All in One, and REST Client VS Code extensions installed.
- [x] Runtime and development dependencies added and installed in `.venv`.
- [x] Validated application/CouchDB configuration model added.
- [x] Redacting CouchDB HTTP client with bounded retries and conflict handling added.
- [x] Source-controlled core, research, and operations Mango indexes defined.
- [x] Idempotent database/security/user/index bootstrap code added.
- [x] Shared CouchDB document envelope and document-type vocabulary added.
- [x] Generic CouchDB repository abstraction added.
- [x] Safe legacy JSON repository with traversal protection and atomic writes added.
- [x] Core schema/vendor reads moved behind the legacy repository.
- [x] Schema and adoption-plan writes moved behind atomic repository writes.
- [x] Flask liveness and readiness endpoints added.
- [x] Read-only API characterization tests added.
- [x] JSON inventory and classification CLI added.
- [x] Initial inventory generated for 4,249 application JSON files.
- [x] All 4,249 inventoried JSON files parsed successfully.
- [x] Secure CouchDB bootstrap completed.
- [x] CouchDB system databases and four application databases created.
- [x] Restricted `gartner_gateway` service user and database security applied.
- [x] Thirty-three source-controlled Mango indexes installed.
- [x] All 4,249 inventory records imported idempotently into `gartner_ops`.
- [x] Imported disposition counts reconciled exactly with the source manifest.
- [x] Live Mango explain verified use of `idx_manifest_disposition_path`.
- [x] Canonical source decision manifest added for active application datasets.
- [x] Four manual-review inventory items resolved.
- [x] Deterministic canonical transforms added for schemas, vendors, scores,
  pricing, MQ scores, reports, frameworks, targets, and evidence.
- [x] 1,828 canonical documents imported into core, research, and archive.
- [x] Canonical reimport verified as a true no-op when sources are unchanged.
- [x] JSON/CouchDB/compare repository modes added for schema and vendor reads.
- [x] Repository reads added for pricing, MDR/CNAPP MQ scores, market insights,
  analyst takes, innovation profiles, and the Agentic SOC framework.
- [x] Active DFIR default corrected from a superseded file to `Vendor 3-7.json`.
- [x] Source-level semantic parity CLI added.
- [x] All 34 migrated core source families match between JSON and CouchDB.
- [x] Compare mode verified across 20 live endpoints with no parity warnings.
- [x] Fourteen migrated endpoints verified directly in pure CouchDB mode.
- [x] PreCyber and PMR statistics reads moved behind repositories.
- [x] ASMF orbital map, methodology documentation, and report definitions
  imported and moved behind repositories.
- [x] PMR, Analyst Take, and PreCyber PowerPoint generation verified in pure
  CouchDB mode.
- [x] Schema, adoption-plan, insight, analyst-take, and innovation-profile
  writes moved behind the selected repository.
- [x] CouchDB writes use current `_rev` values and surface conflicts as HTTP
  409 responses.
- [x] CouchDB dataset writes create pending/completed/failed audit events in
  `gartner_ops`.
- [x] Compare mode explicitly rejects persistent writes with HTTP 503 and
  leaves JSON files unchanged.
- [x] Live CouchDB write-and-rollback route cycle verified with completed audit
  events and restored semantic parity.
- [x] Canonical importer protects gateway-modified documents from overwrite.
- [x] Editable GET responses expose strong HTTP `ETag` revision tokens.
- [x] CouchDB write routes require `If-Match`; missing tokens return HTTP 428
  and stale tokens return HTTP 409.
- [x] Collection-backed resources use deterministic composite revision tokens.
- [x] Browser edit calls cache ETags and send them with persistent writes.
- [x] Live ETag write, stale-token rejection, and rollback cycle verified.
- [x] Typed research project, run, target, evidence, score-proposal,
  review-decision, and checkpoint contracts added.
- [x] Research evidence, score proposals, and review decisions are immutable.
- [x] Accepted scores publish as separate `vendor_score` documents linked to
  their proposal, decision, and evidence records.
- [x] Resumable research checkpoints require optimistic concurrency on update.
- [x] Bounded indexed queries added for run targets and score proposals.
- [x] Localhost-only research API gateway added; it refuses all requests unless
  `DATA_BACKEND=couchdb`.
- [x] Three-vendor live CouchDB dry run stopped, resumed, produced evidence,
  entered analyst review, and published three accepted scores without
  filesystem state.
- [x] Verification run and all three targets reached completed state.
- [x] Typed source-reference, immutable source-snapshot, and versioned
  research-policy contracts added.
- [x] URL canonicalization removes fragments and tracking parameters while
  retaining meaningful sorted query parameters.
- [x] Source IDs are deterministic SHA-256 IDs of canonical URLs.
- [x] Source snapshots retain retrieval method, outcome, hashes, text length,
  bot-wall signals, retry linkage, cache provenance, and optional full text.
- [x] Snapshot history is append-only; blocked and failed attempts are not
  overwritten by successful retries.
- [x] Evidence documents can link directly to their source and exact snapshot.
- [x] `research_precyber_v1_evidence.py` can append source lineage when invoked
  with explicit CouchDB project and run IDs.
- [x] `_render_precyber_zero_vendors.py` appends Playwright success, short,
  bot-wall, and failure snapshots and records whether Chromium was headed.
- [x] Playwright retries automatically link to the prior snapshot for the same
  canonical source instead of erasing its history.
- [x] `research_precyber_svc_pricing.py` appends lineage for both reused cache
  records and new urllib/Playwright fetches.
- [x] Strict PreCyber scoring creates immutable snapshot-backed
  `score_proposal` documents in explicit CouchDB mode.
- [x] Strict scoring supports non-destructive `--proposal-only` verification.
- [x] Positive score proposals require evidence; explicit L0 proposals may
  retain an empty evidence list.
- [x] Legacy score evidence and proposal IDs are deterministic and rerunnable
  without duplication.
- [x] Evidence and SVC/pricing workers use CouchDB research checkpoints when
  project/run IDs are supplied; file checkpoints remain compatibility-only.
- [x] Live Axonius scoring verification imported 14 cached sources, created 24
  snapshot-backed proposals, replayed all 24 idempotently, and resumed its
  CouchDB checkpoint without writing canonical JSON.
- [x] Live lineage verification retained blocked-to-headed-success retry
  history and imported real success/failure PreCyber cache records.
- [x] Live Mango explain selected all three source-lineage indexes.
- [x] Current test suite: 73 passing tests.
- [x] Ruff checks pass for new migration code and tests.
- [x] Final delta import completed with canonical source parity at 34/34.
- [x] `DATA_BACKEND=couchdb` cutover completed; the app is running on
  `127.0.0.1:5000`.
- [x] Compare-mode rollback rehearsal and CouchDB recutover produced identical
  response hashes for schemas, vendors, reports, and MDR pricing.
- [x] Pure-CouchDB smoke verification passed for health, schemas, vendors,
  reports, pricing, PreCyber, PMR, innovation profiles, and documentation.
- [x] MDR, PreCyber, and PMR PowerPoint generation passed after correcting two
  report-generator defects.
- [x] Pure-CouchDB optimistic write, stale ETag rejection, and semantic rollback
  passed on the live gateway.
- [x] Route discovery for schemas, reports, pricing, and PreCyber sources now
  comes from the canonical manifest rather than directory enumeration.
- [x] Request-size enforcement, JSON content-type validation, and a
  localhost/feature-flag shutdown guard are active.
- [x] Portable checksummed backup and isolated clean-database restore tooling
  added; two logical backups and one exact-hash restore drill completed.
- [x] CouchDB operational status command added for counts, sizes, compaction,
  and active tasks.
- [x] Local development, contracts, research state machine, backup/restore, and
  API request collection documentation added.
- [x] Full-repository Python compilation passes after repairing the quarantined
  helper script syntax error.

## Current gate

The local single-node cutover is complete. JSON files remain read-only rollback
sources for the acceptance window. The only local operations item not activated
is registration of the nightly Windows Scheduled Task: the script is ready at
`scripts/install_couchdb_backup_task.ps1`, but task registration could not be
approved by the execution environment. Off-machine replication/storage and
multi-user authentication remain future deployment decisions, not local
single-node cutover blockers.

Canonical decisions: `migration/canonical_sources.json`

## Data inventory

| Proposed disposition | Files |
|---|---:|
| Core candidate | 93 |
| Research candidate | 79 |
| Archive candidate | 12 |
| Manifest-only candidate | 4,061 |
| Manual review required | 4 |

Manifest: `migration/manifests/json_inventory.jsonl`

The four manual-review items were resolved as follows:

- Agentic SOC self-assessment template: canonical framework.
- CNAPP MQ evidence ledger: canonical research evidence.
- PreCyber targets v23: canonical research targets.
- Earlier PreCyber target list: archived legacy dataset.

## Canonical import

| Database role | Documents |
|---|---:|
| Core | 1,302 |
| Research | 525 |
| Archive | 1 |
| **Total** | **1,828** |

Core includes 325 deduplicated vendor identities, 680 score documents, 102
pricing documents, 150 MQ score documents, 10 schemas, 23 market insights,
six analyst takes, two frameworks, and one innovation profile.
The core total also includes three structured report definitions.

## Research workflow verification

The first-class workflow is implemented in:

- `gartner_app/domain/research.py`
- `gartner_app/repositories/research.py`
- `gartner_app/services/research_workflow.py`
- `gartner_app/api/research.py`

The reproducible live exercise is:

```powershell
.\.venv\Scripts\python.exe -m gartner_app.research.dry_run --json
```

The completed verification run was
`research_run:fb0cc1d5-1b4e-44f6-a25e-32a3b2b38a34`. It created three targets,
resumed from a rendering checkpoint, retained three immutable evidence records,
created three score proposals and three review decisions, and published three
linked accepted scores in the isolated `verification_precyber` market.

## Source-lineage verification

The legacy-cache bridge is implemented in
`gartner_app/research/lineage.py`. The evidence worker accepts
`--couchdb-project-id` and `--couchdb-run-id`; without both options it retains
its original behavior. The direct Playwright renderer and SVC/pricing worker
accept the same explicit options.

Run the reproducible cache-lineage exercise with:

```powershell
.\.venv\Scripts\python.exe -m gartner_app.research.lineage_dry_run --json
```

Completed run `research_run:bdf0f4e6-240a-4bb4-8ccb-97417ea3aafd` used policy
`research_policy:precyber-public-web:1.0`, retained a blocked first attempt and
headed successful retry as separate snapshots, linked extracted evidence to
the successful snapshot, and left the failed target explicitly blocked.

## Strict-scoring verification

The strict-scoring bridge is implemented in
`gartner_app/research/scoring.py`; legacy progress compatibility is implemented
in `gartner_app/research/checkpoints.py`.

Run the non-destructive scoring exercise with:

```powershell
.\.venv\Scripts\python.exe -m gartner_app.research.scoring_dry_run --json
```

Completed run `research_run:f219b68b-9de8-47cc-8f32-df4fca3515f8`
selected Axonius, imported 14 cached sources, created 24 strict proposals,
replayed all 24 with identical deterministic IDs, resumed its scoring
checkpoint, and wrote no canonical JSON.

Run source-level parity verification with:

```powershell
.\.venv\Scripts\python.exe -m gartner_app.migration.check_parity
```

## Intentional compatibility state

- The running local instance uses `DATA_BACKEND=compare`.
- Compare mode serves JSON and queries CouchDB for 34 migrated core source
  families.
- Readiness requires CouchDB while compare mode is active.
- JSON remains the source of truth until canonical dataset selection,
  full-route parity testing, and cutover complete.
- The browser has no direct CouchDB access or credentials.

## Platform note

Apache currently publishes CouchDB 3.5.2 source, but its official Windows
convenience-binary directory currently provides 3.3.0. The local development
service therefore uses verified Apache CouchDB 3.3.0 while the integration is
limited to stable CouchDB 3.x HTTP, security, bulk-document, and Mango APIs.
