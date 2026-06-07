# exp_dev hand-off -- research: Snapshot Concurrency Protocol Under GDPR Erasure (Chain 2 / Drill 4)

Filed-by: research sub-agent (Chain 2 / Drill 4)
Trigger: notes/research_drill_substrate_developer_experience_5x_chain2_drill4_2026-06-07.md
Date: 2026-06-07
Per [[feedback-no-experiment-design-in-prompts]]: no inline experiment design.
  exp_dev reads the research note for mechanism detail; does NOT receive design instructions here.

---

## Pause state block

This file is auto-discovered by exp_dev on emergency-refill cycles (scan notes/exp_dev_handoff_*.md
sorted by mtime). The handoff is valid regardless of orchestrator pause state for DESIGN work.
Queue-add (actual dispatch) is pause-gated per data/orchestrator_paused.flag.

---

## Anchor candidates (rank-ordered)

### Anchor 1 -- Protocol E smoke test (ERASURE-CONCURRENCY-SMOKE)
Anchor pointer: implement erasure_concurrency_smoke per Part 5 of research note
Substrate-product reading: verifies the core GDPR safety invariant (zero pre-erasure
  content returned after ErasureRecord commit) under 200 concurrent readers
Tier hint: Tier 1 (rung-1 laptop CPU, <60 seconds, ~200 lines Python)
Why-now: Protocol E is the recommended concurrency protocol for Component 6 of the
  Drill 3 7-component bitemporal spec. The smoke test is the cheap decisive test
  that de-risks the full implementation. Cost: ~2 hours engineering.

### Anchor 2 -- Component 6 revision (ERASURE-RECORD-APPEND)
Anchor pointer: revise BiTemporalStorage.erase_fact() to use ErasureRecord append +
  at-query filter pattern (Protocol E) instead of in-place snapshot mutation
Substrate-product reading: replaces the rank-1 downdate-in-place design (Drill 3 Component 6)
  with an append-only ErasureRecord that preserves the Merkle log integrity guarantee
Tier hint: Tier 2 (rung-2 local runner, ~100 lines delta on existing Component 6 scaffold)
Why-now: Drill 3 7-component spec was complete; Component 6 was the only unresolved
  correctness gap (concurrency during erasure). Drill 4 resolves it. Component 6 revision
  can now be coded from the spec.

### Anchor 3 -- HMAC key store (ERASURE-HMAC-KEYSTORE)
Anchor pointer: add per-fact HMAC key store with key-deletion API; replace SHA256
  plain-hash fields in BiTemporalFact with HMAC-SHA256(erasure_key, vector.bytes)
Substrate-product reading: closes the hash-re-linkage GDPR gap (EDPB Position 3 risk);
  achieves GDPR Position 1 (HIGH defensibility) by making Merkle leaf hashes
  truly anonymous after key deletion
Tier hint: Tier 2 (rung-2 local runner, ~200 lines, key store is a dict with
  encrypted-at-rest wrapper)
Why-now: EDPB Guidelines 01/2025 and 02/2025 (April 2025) establish that deterministic
  SHA256 of personal-data-derived vectors may remain linkable. HMAC with key deletion
  closes this gap. Required for healthcare AI deployment (EU AI Act Article 12, Aug 2026).

---

## Context pointers (file paths, not summaries)

Research note (this drill):
  d:/AI/hd-instrument/notes/research_drill_substrate_developer_experience_5x_chain2_drill4_2026-06-07.md

Drill 3 implementation spec (7-component bitemporal build):
  d:/AI/hd-instrument/notes/research_drill_substrate_developer_experience_5x_chain2_drill3_2026-06-07.md

Drill 3 exp_dev handoff (bitemporal impl spec):
  d:/AI/hd-instrument/notes/exp_dev_handoff_research_bitemporal_impl_spec_chain2_drill3_2026-06-07.md

Chain 2 Drill 1 (XTDB isomorphism, SDK foundation):
  d:/AI/hd-instrument/notes/research_drill_substrate_developer_experience_5x_chain2_drill1_2026-06-07.md

Chain 2 Drill 2 (cross-shard K-hop gap):
  d:/AI/hd-instrument/notes/research_drill_substrate_developer_experience_5x_chain2_drill2_2026-06-07.md

---

## Contract section

exp_dev reads the research note (context pointer 1) for:
- Protocol E mechanism (Part 1, Protocol E)
- Cheap decisive test spec (Part 5)
- Pre-reg HP/HF bands (Part 5 falsifiable predictions: HP-1 through HP-6, HF-1 through HF-5)
- Component 6 revision delta (Part 6.1)
- HMAC key store architecture (Part 3.2)

exp_dev does NOT receive inline design instructions from this handoff file.
exp_dev does NOT interpret verdicts (orchestrator/verdict_handler owns).
exp_dev dispatches anchors via queue_add.sh per pause-gate check.

## Autonomy declaration

exp_dev has full autonomy to:
- Sequence the 3 anchors above in any order (recommended: Anchor 1 first as smoke gate)
- Adjust implementation details within the spec (e.g., cache data structures)
- Flag back to orchestrator if smoke test (Anchor 1) fires HF-1 (GDPR_SAFE violated)
- Combine Anchor 2 + Anchor 3 into a single dispatch if they share no data dependencies
  (they do share the BiTemporalFact schema; recommend sequential: 2 then 3)
