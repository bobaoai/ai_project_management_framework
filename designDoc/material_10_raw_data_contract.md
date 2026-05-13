---
title: Raw Data Material Contract
status: active_draft
layer: T1
parent: material_00_overview
created_date: 2026-05-07
reader_persona:
  - System Builder
  - Data Infrastructure Maintainer
  - Ingestion Maintainer
---

# Raw Data Material Contract

## 1. Purpose

`Raw Data` is original or provider-normalized material before interpretation.

This contract owns the material identity boundary for raw surfaces. It says what can enter the system as material before any Source Card, Evidence, Thesis, Scenario, report, or PM decision exists.

## 2. Boundary

Raw Data includes:

- raw archive payloads
- provider API payloads
- price bars and market data series
- filings, transcripts, press releases, PDFs, HTML, newsletters, images, and video / audio transcripts
- rendered page images and reviewed image candidates before downstream interpretation
- source-local assets preserved for audit or replay

Raw Data may be lightly normalized by provider or ingestion infrastructure, but it must not contain investment meaning, belief, thesis language, scenario prediction, or PM action language.

## 3. Required Properties

Every Raw Data object should be able to expose:

```yaml
raw_data_id:
source_ref:
origin:
provider:
source_collection:
content_type:
content_hash:
observed_at:
recorded_at:
raw_path:
license_or_access_note:
audit_paths:
```

Timestamp fields must follow the Timestamp Semantic Contract.

## 4. Allowed Handoffs

Raw Data may feed:

- Canonical Input
- Operating Cycle Artifact
- Source Card
- Technical Report input
- deterministic data stores
- audit / replay surfaces

Raw Data may not directly feed Thesis, Scenario, Evidence, or Portfolio Decision unless an owning workflow materializes the required intermediate object.

## 5. Must Not Do

Raw Data must not:

- summarize itself into a conclusion
- infer source meaning
- assign confidence or conviction
- create Evidence
- create Thesis or Scenario
- authorize portfolio action

## 6. Adjacent Owners

| Owner | Relationship |
|---|---|
| Ingestion | Captures, stores, normalizes, and indexes Raw Data. |
| Timestamp Semantic | Owns time field meanings. |
| Material Catalog | Owns the Raw Data material boundary. |
| Artifact Graph | Owns node identity and freshness if Raw Data becomes an artifact node. |

## 7. Open Decisions

1. Which Raw Data subclasses should receive dedicated schemas first: market bars, message archives, filings, media transcripts, or image evidence candidates?
2. Should provider-normalized data have a separate subtype from original raw capture?
3. Which Raw Data surfaces are graph nodes versus audit-only sidecars?

## References

- `[Material-Overview]` [Material Catalog Overview](material_00_overview.md)
- `[T0-Time]` [Timestamp Semantic Contract](the_timestamp_semantic.md)
- `[T1-Ingestion]` [Ingestion Overview](ingestion_00_overview.md)
