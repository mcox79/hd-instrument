# exp_dev hand-off -- research: two-regime alpha capacity scaling rescue 2x

Filed-by: research sub-agent
Trigger: notes/research_drill_two_regime_alpha_capacity_scaling_rescue_2x_2026-06-06.md
Pause state: check data/orchestrator_paused.flag before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchors and WHY, not sweep grids, threshold formulas, or queue choices.

---

## Anchor Candidates (rank-ordered)

### 1. capacity_sweep_n32768_asymptotic_alpha_v1
- Substrate-product reading: confirms whether Phase 3 blueprint alpha=0.040 is correct or needs further downward revision; gates the entire Phase 3 production capacity commitment
- Tier hint: CPU smoke; <5 min wall; Tier-1 (blocking decision gate)
- Why now: 2 N-doublings at N=4096..16384 show stable alpha=0.040 but N=32768 is the next extrapolation checkpoint before the Phase 3 N=65536 commitment; cheap and decisive

### 2. sparse_vs_dense_write_regime_alpha_n4096_n16384_v1
- Substrate-product reading: tests whether sparse write rule breaks the large-N crosstalk scaling; if HARD PASS, sparse write is a major rescue path that recovers alpha~0.055+ at large N without tensor-order change
- Tier hint: CPU smoke; <15 min wall; Tier-2 (rescue path validation)
- Why now: RSB analysis and SNR theory both predict sparse write reduces per-write crosstalk; empirical check is cheap at N<=16384

### 3. n3_cubic_tensor_capacity_n4096_v1 (CRITICAL UNKNOWN)
- Substrate-product reading: calibrates the prefactor C_3 for cubic-tensor (n=3) capacity M_max ~= C_3 * N^2; without this, the Phase 3 Wikipedia-class capacity claim for n=3 is unverified
- Tier hint: CPU or GPU; moderate wall; Tier-1 (blocking decision gate for Phase 3 n=3 commitment)
- Why now: Phase 3 blueprint relies on n=3 O(N^2) scaling for Wikipedia-class capacity; the prefactor C_3 for this specific substrate is UNKNOWN; must be measured before engineering commitment

---

## Context Pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_two_regime_alpha_capacity_scaling_rescue_2x_2026-06-06.md
- Phase 3 blueprint (prior): check notes/ for production architecture drill (morning 2026-06-06)
- Cap map: d:/AI/hd-instrument/data/cap_map.md (check rows for n=2 capacity and n=3 capacity)
- Field advisor output: spin-glass (83% yield), free-probability (100% yield) are highest-yield adjacencies

---

## Contract

exp_dev owns: anchor design, sweep grids, threshold formulas, queue routing, pre-reg bands, self-test verification.
research handed off: anchor names, WHY, tier hints, context pointers.
exp_dev does NOT inherit the specific numerical thresholds from this file as binding contracts -- it pre-registers its own per [[feedback-envelope-expansion-fail-bands]].

## Autonomy Declaration

exp_dev has full autonomy over anchor implementation, smoke-gate design, and queue placement. The three anchors above are SUGGESTIONS ordered by strategic priority; exp_dev may reorder, split, or combine based on current queue state and runner availability.
