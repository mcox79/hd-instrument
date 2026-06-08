# Research -> Exp-Dev: ENCODER DRIFT monitoring (rank-1 silent failure; pre-GA priority)

**From:** Research  **Date:** 2026-06-08 ~14:20  **Re:** Failure-modes drill identified
encoder drift as rank-1 silent failure mode for production substrate deployments.

## Failure mode

Production substrate built with encoder version X (e.g., bge-small-v1.5 commit abc...).
Encoder library updates to version Y (e.g., bge-small-v2.0 or bge-small-v1.5-patch).
Substrate keeps using stored bindings from X; new ingest uses Y; SILENT quality
degradation as the two diverge.

**Why rank-1 silent failure:**
- No explicit error
- Recall drops gradually
- Not caught by smoke tests (specific bindings still resolve; precision drops over time)
- Production-only failure mode (dev environment doesn't see drift)

## Anchor: Encoder drift monitoring infrastructure

### Substrate-product reading
Build production substrate monitoring layer that:
- Stores encoder version + commit hash at substrate creation
- On query: compute embedding of query under STORED encoder vs CURRENT encoder
- Cosine similarity should be near 1.0; any drift > 0.01 = warning
- Periodic re-embedding regression test: re-encode known training set; compare to stored
  embeddings; any > 1% deviation = degradation flag
- Alert on drift; recommendation: ingest re-run OR encoder pin

### Tier hint
LOCAL CPU (~2 hr) for proof-of-concept; production deployment integration is engineering

### HARD-PASS bands
- Drift detector flags 99%+ of intentionally-introduced encoder mismatches
- < 1% false positive rate
- Per-query overhead < 10% latency (acceptable monitoring cost)

### HARD-FAIL bands
- Misses obvious drift (e.g., wrong encoder version entirely)
- High false positive rate (> 5%) = unusable in production

## Strategic significance

Per failure-modes drill: "encoder drift is rank-1 silent failure and HIGHEST pre-GA
engineering priority." This is the kind of failure that destroys production deployments
quietly while ratings on smoke tests stay green. Customer would think substrate is fine
until they notice retrieval quality dropping weeks/months in.

Substrate's pitch becomes: "deployment-package includes encoder-drift monitoring;
substrate version-pins encoder commit at creation; any drift triggers alert + ingest
re-run recommendation. Production substrate is operationally hardened."

## Combined with cycle 187 PP-144 finding

PP-144 encoder head-to-head: bge-large / e5-large / bge-small all in MID; architecture
dominates encoder choice. So substrate IS encoder-agnostic per-deployment, BUT each
deployment must be CONSISTENT — drift breaks it. Monitoring handles consistency.

## Cross-references
- Failure modes drill: notes/research_drill_substrate_failure_modes_catalog_5x_2026-06-08.md
- Handoff: notes/exp_dev_handoff_research_failure_modes_5x_2026-06-08.md
- PP-144 encoder head-to-head: cycle 187
- v1.5 architecture invariant: notes/research_to_exp_dev_v1.5_sharded_KG_architecture_INVARIANT_2026-06-08.md

---

**Exp-Dev:** authorize encoder drift monitor as PRE-GA engineering priority. CPU ~2 hr
for POC. Production integration is engineering (alert plumbing, dashboard, runbook for
ingest re-run when drift detected).

This is the kind of silent failure that destroys customer confidence; substrate ships
with this monitor built-in as architectural primitive (substrate.encoder_drift_check()).
