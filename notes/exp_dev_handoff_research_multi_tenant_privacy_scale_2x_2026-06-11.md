# exp_dev hand-off -- research: multi-tenant isolation, privacy, and audit at production scale (2x)

**Filed:** 2026-06-11 by research sub-agent.  
**Trigger:** Research drill completed; five CPU-runnable anchor candidates identified. All are pure-numpy/pure-Python, local_cpu_queue eligible, runtime < 5 min each.  
**Research note:** `notes/research_drill_multi_tenant_privacy_scale_2x_2026-06-11.md`

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching. If present, hold. Annotation bumps allowed while paused.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, full implementation. Research does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### 1. PP-356-SCALE -- Shard-routing 10K-tenant memory and crosstalk benchmark

**Anchor pointer:** `notes/research_drill_multi_tenant_privacy_scale_2x_2026-06-11.md` Section Q1 + Stream D.  
**Substrate-product reading:** PP-356 validated per-role isolation algebraically at single-node. The production gap is in shard-routing memory scaling and intra-shard crosstalk at 10K+ tenants. This experiment closes the gap between "algebraically correct" and "deployable at production scale." Linear memory scaling is the gate for the enterprise pricing tier argument.  
**Tier hint:** local_cpu (pure-numpy, no GPU, < 5 min). Scale sweep 10 -> 100 -> 1K tenants; extrapolate to 10K.  
**Why now:** Product narrative (compliance sidecar, v315 cap map) depends on claiming production-scale multi-tenant isolation. Closing Q1 converts a theoretical claim into an empirical one. Highest priority because it is the foundation all other Q claims build on.

### 2. PP-9-CASCADE -- Cascading GDPR delete with dependency traversal

**Anchor pointer:** `notes/research_drill_multi_tenant_privacy_scale_2x_2026-06-11.md` Section Q2 + Stream E (E2 delta deletion).  
**Substrate-product reading:** PP-9 deletion cert validated for single-fact delete. CNIL 2025 enforcement (stream D) shows cascading delete (entity + all referencing facts) is the enforcement target. This experiment extends PP-9 to multi-hop dependency cascades and validates audit consistency post-delete. Closing Q2 enables the "full GDPR Article 17 compliance" product claim.  
**Tier hint:** local_cpu (pure-numpy dependency graph construction + algebraic delete cascade). Short run.  
**Why now:** CNIL 2025 enforcement report identifies right-to-erasure as #1 active enforcement priority. Regulatory urgency is real and growing.

### 3. PP-228-MERKLE -- Sparse Merkle audit compression at simulated 1M events

**Anchor pointer:** `notes/research_drill_multi_tenant_privacy_scale_2x_2026-06-11.md` Section Q3 + Stream B.  
**Substrate-product reading:** PP-228 cryptographic audit produces hash certificates per write. This experiment integrates sparse Merkle tree (O(log k) proof size) over write hashes to achieve < 1KB per event at 1B events/day throughput. Two peer-reviewed sources give the math (arXiv 2307.04085 vector commitments; arXiv 2605.00065 adaptive chunking). Closing Q3 enables the "audit without storage explosion" product claim.  
**Tier hint:** local_cpu (pure-Python Merkle tree implementation over simulated write-hash array). Simulate 1M events to measure compression ratio and proof generation time.  
**Why now:** Audit log compression is the missing infrastructure piece between PP-228 (per-write certificate) and production viability (billions of writes/day). Without compression, audit storage is infeasible.

### 4. PP-356-SYBIL -- 1000-fake-tenant Sybil attack on role-vector isolation

**Anchor pointer:** `notes/research_drill_multi_tenant_privacy_scale_2x_2026-06-11.md` Section Q4 + Stream E (E4 Sybil resistance).  
**Substrate-product reading:** PP-356 algebraic isolation is theoretically Sybil-resistant (fake role-vector retrieves near-zero from victim tenant's stored facts). This experiment confirms the claim empirically under an adversarial attack: 1000 fake tenants, each attempting to extract cross-tenant information via arbitrary role-vector probes. If cosine similarity of attacker's retrieved vector vs victim's stored vector is < 0.005, the claim is validated.  
**Tier hint:** local_cpu (pure-numpy random role-vector generation + cosine similarity measurement). Fast.  
**Why now:** Security certification (SOC 2, ISO 27001) requires empirical adversarial testing, not just theoretical claims. This anchor provides the adversarial test result.

### 5. PP-344-BATCH -- Batch key rotation 1000 keys, latency and old-key recall

**Anchor pointer:** `notes/research_drill_multi_tenant_privacy_scale_2x_2026-06-11.md` Section Q5 + Stream E (E5 key rotation).  
**Substrate-product reading:** PP-344 validated old-key recall = 0.002 at single-key rotation. Compliance mandates (FIPS 140-2, 90-day rotation) require 100K rotations/day. This experiment measures whether PP-344 properties hold at batch rotation rates and whether per-rotation latency enables the required throughput (>= 1 rotation/sec sustained). If the algebraic property degrades at batch rates, async pipeline redesign is needed.  
**Tier hint:** local_cpu (rotation = algebraic rebinding, no GPU needed). Run 1000 sequential rotations, measure mean and p99 latency + old-key recall at each step.  
**Why now:** FIPS compliance is a hard requirement for enterprise sales. Closing Q5 converts PP-344 (single-rotation proof) into production compliance evidence.

---

## Context pointers

- Research note: `d:/AI/hd-instrument/notes/research_drill_multi_tenant_privacy_scale_2x_2026-06-11.md`
- Cap map rows: PP-9, PP-13, PP-14, PP-15, PP-228, PP-344, PP-356 in `notes/substrate_capability_map.md`
- Product narrative (v315): `notes/substrate_capability_map.md` lines 26-37 (PRIMARY PRODUCT NARRATIVE + GTM)
- Key rotation patent precedent: USPTO 10819513 / 11057359 / 11374749 (referenced in research note Stream E)
- ZK audit precedent: arXiv 2512.14737 (referenced in research note Stream E, E1)
- Merkle audit precedent: arXiv 2307.04085, arXiv 2605.00065 (referenced in research note Stream B)

---

## Contract section

exp_dev owns all implementation decisions for these anchors. Research names the capability gap and the relevant literature; exp_dev designs the cell (N, M, seed count, queue, smoke bands, full profile). If exp_dev encounters an ambiguity in the experiment design that requires research input (e.g. which Merkle variant to implement, which ZK scheme to use), file a research request note rather than guessing.

---

## Autonomy declaration

Research sub-agent filed this hand-off based on drill findings from five parallel lit-scan streams (enterprise patterns, cryptography, database, substrate composition, new paths). No orchestrator action was required to generate the anchor list. exp_dev is authorized to pick up this hand-off on any emergency-refill cycle by scanning `notes/exp_dev_handoff_*.md` sorted by mtime.
