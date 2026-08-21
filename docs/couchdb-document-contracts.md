# CouchDB document contracts

All mixed databases require a `doc_type`. Application documents use stable
deterministic IDs where a natural identity exists and retain source provenance,
market, cycle, timestamps, and schema version as applicable.

## Database ownership

| Database | Principal document families |
|---|---|
| `gartner_core` | schema, vendor, vendor score, pricing, MQ score, report, framework, profile |
| `gartner_research` | project, run, target, source reference, snapshot, evidence, proposal, decision, checkpoint, policy |
| `gartner_ops` | migration inventory, audit event, dead letter |
| `gartner_archive` | explicitly superseded legacy datasets |

## Research integrity

- Source references are deduplicated by canonical URL.
- Snapshots are immutable and identified by content/retrieval identity.
- Evidence points to the exact source snapshot used.
- Score proposals and review decisions are immutable.
- Accepted scores are separate documents linked to the proposal, decision, and
  evidence.
- Updates use CouchDB revisions; HTTP writes require `If-Match`.

## Query rules

Selectors always include `doc_type`, use allowlisted filters, bounded limits,
field projections, and Mango bookmarks. Source-controlled indexes live under
`gartner_app/couchdb/design/`. Explain-plan tests verify intended index
selection for critical queries.

## Compatibility datasets

Some UI resources are still represented as aggregate dataset documents to
preserve route response contracts. The repository decomposes normalized
documents and reconstructs these shapes. Source JSON files are rollback-only
and are not the active persistence path when `DATA_BACKEND=couchdb`.
