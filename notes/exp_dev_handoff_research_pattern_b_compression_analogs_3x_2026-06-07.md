# exp_dev hand-off -- research: Pattern B compression analogs 3x

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: notes/research_drill_pattern_b_compression_analogs_3x_2026-06-07.md
Pause state: RESPECT pause flag at data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file records WHAT to test and the
pre-registration bands. Exp_dev writes the experiment scripts; it does NOT receive inline
code or detailed implementation from this file.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (highest priority): Pre-Test 1 -- Concept reuse ratio on sample KBs
Anchor pointer: PTB-REUSE-1
Substrate-product reading: Validates whether Mechanism 2 (index-only filler cache) achieves
  10-31x compression in practice. If concept reuse < 3:1, the cache amortization fails and
  Pattern B costs 100-400 bytes/fact even with index-only storage. This is the decision gate
  for the entire v1.1 engineering path.
Tier hint: LOCAL CPU (no GPU needed; numpy/text parsing only; ~1 hour wall)
Why now: The v1.1 engineering path (Mechanism 2, 3-5 days) should not begin until this
  pre-test confirms concept reuse >= 3:1 on production-representative KBs.
Pre-registration bands:
  HARD PASS: reuse ratio > 10:1 on >= 2 of 3 sample KBs -> proceed to Mechanism 2 implementation
  MIDDLE BAND: reuse ratio 3-10:1 on all 3 KBs -> proceed with caution; cache savings modest
  HARD FAIL: reuse ratio < 3:1 on any 2 KBs -> do NOT invest in cache-amortization path;
    fall back to index-only (25-byte floor) without cache savings assumption

### Anchor 2: Pre-Test 2 -- Role-separable PCA on bge-small fillers
Anchor pointer: PTB-RSPCA-2
Substrate-product reading: Validates Mechanism 1 (role-separable PCA truncation). If each
  role's filler distribution has TwoNN < 150 and cosine retention at d=100 > 0.90, then the
  filler cache can be compressed from d=384 to d=100 (4x size reduction on cache) before
  TT decomposition.
Tier hint: LOCAL CPU (~2 hours wall; requires bge-small model; 10K sentence encoding)
Why now: If Pre-Test 1 passes, this test determines whether Mechanism 1 stacks on top.
  Do Pre-Test 2 in parallel with or immediately after Pre-Test 1.
Pre-registration bands:
  HARD PASS: TwoNN per role group < 150 AND cosine at d=100 > 0.90 for all groups
  MIDDLE BAND: TwoNN < 200 AND cosine at d=150 > 0.85 -> viable at d=150 (2.6x compression)
  HARD FAIL: TwoNN > 250 for any role group -> do NOT apply Mechanism 1; filler space is high-rank

### Anchor 3: Pre-Test 3 -- TT rank profile on bge-small filler matrix
Anchor pointer: PTB-TTRP-3
Substrate-product reading: Validates Mechanism 5 (tensor-train decomposition of filler cache).
  If SVD singular values of the 50K x 384 filler matrix decay quickly and TT at r=16 gives
  cosine similarity > 0.90, the cache can be compressed 24x (from 75 MB to 3 MB). This
  eliminates the cache amortization problem even at small KB scales.
Tier hint: LOCAL CPU (~2 hours wall; requires bge-small + SVD on 50K x 384 matrix; scipy ok)
Why now: If Pre-Tests 1 and 2 pass, this determines whether v1.2 (Mechanism 5) is viable.
Pre-registration bands:
  HARD PASS: cosine similarity at r=16 > 0.90 for 90% of vectors -> TT gives 24x compression
  MIDDLE BAND: cosine at r=32 > 0.85 -> 12x compression; still significant for v1.2
  HARD FAIL: cosine at r=64 < 0.80 -> bge-small is full-rank; TT compression fails

---

## Context pointers

Primary research note:
  d:/AI/hd-instrument/notes/research_drill_pattern_b_compression_analogs_3x_2026-06-07.md

Prior manifold drill (establishes TwoNN=731 baseline for bundles):
  d:/AI/hd-instrument/notes/research_drill_pattern_b_manifold_storage_2x_2026-06-07.md

Prior compositional storage feasibility drill:
  d:/AI/hd-instrument/notes/research_drill_pattern_b_compositional_storage_3x_2026-06-07.md

Cycle 154 sparse-KEY result (200x compression for Pattern A, NOT applicable to Pattern B):
  Ref: internal cycle logs / cap_map entry for sparse-KEY at alpha=0.005

Cycle 155 sparse-W collapse result (sparsity >= 0.75 kills recall -- confirms Mechanism 3/9
  infeasibility):
  Ref: internal cycle logs / cap_map entry for sparse-W

---

## Contract

Research claims these pre-tests are feasible on LOCAL CPU in 1-2 hours each.
Exp_dev is authorized to queue all three as a batch on the remote CPU runner.
All three are numpy/sklearn/bge-small inference only -- no GPU needed.
No authorization is granted for GPU dispatch of these pre-tests.

## Autonomy declaration

Exp_dev owns implementation details of the three pre-tests. The pre-registration bands above
are FIXED. Exp_dev must not redefine HARD PASS/FAIL thresholds. If results fall in MIDDLE BAND
for multiple tests, route back to orchestrator for strategy decision before proceeding to v1.1.
