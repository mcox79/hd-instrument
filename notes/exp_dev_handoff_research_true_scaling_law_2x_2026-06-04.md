# exp_dev hand-off -- research: true task-complexity scaling law (2x refutation drill)

Filed-by: research sub-agent, 2026-06-04
Trigger: notes/research_drill_substrate_true_task_complexity_scaling_law_2x_2026-06-04.md
Pause state: CHECK data/orchestrator_paused.flag before dispatching any anchor below.

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and
context pointers only. exp_dev designs sweep grids, threshold formulas, queue assignments,
and HF/HP numerical bounds without further input from research.

---

## Background

K* = log_V(alpha_c * N) + 1 formula is empirically refuted. K=3 (E1) and K=8 (Bundle B) both
HARD-PASS. Corrected law has architecture-dependent effective interaction order (gamma_arch) and
effective vocabulary V_eff << V for natural language. Key unknowns that require empirical
resolution are listed below.

---

## Anchor Candidates (rank-ordered by decisiveness and cheapness)

### 1. Cell X1 -- Pure Hebbian (no position-binding) at K=3, V=70, N=4096
- Anchor pointer: cheapest isolation test; does pure Hebbian (alpha_c=0.14) fail K=3 trigram?
- Substrate-product reading: if HARD-FAIL, position-binding is the load-bearing arch component
  for any K>=3 product; if HARD-PASS, pure Hebbian already supports trigram (formula revision)
- Tier hint: CPU smoke (cheap, ~5 min); no GPU needed for initial result
- Why-now: This is the single cheapest decisive test to isolate the architecture contribution.
  Must run before Bundle G extrapolation to know what is being extrapolated.

### 2. Cell G1 -- Combined arch at K=12, V=70, N=8192
- Anchor pointer: ceiling test for combined architecture at current N; tests gamma_arch >= 1.7
- Substrate-product reading: if HP, K=12 char-LM is product-viable; opens 12-gram completion tasks
- Tier hint: GPU smoke (K=12 requires larger batch sizes); FULL multi-seed if smoke passes
- Why-now: Directly tests the corrected scaling law's most actionable prediction; high-value next step

### 3. Cell G2 -- Combined arch at K=12, V=70, N=16384
- Anchor pointer: N-scaling test at K=12 ceiling; distinguishes gamma=1 from gamma>=1.5
- Substrate-product reading: N=16384 is product-relevant (real text passages); confirms viability
- Tier hint: GPU (N=16384 requires it); run in parallel with G1 after X1 resolves
- Why-now: Resolves whether K=12 ceiling is N-gated (needs N=16384) or arch-gated

### 4. Cell H1 -- Shakespeare char-LM at K=8, N=8192 (real-task test)
- Anchor pointer: V_eff test; Shakespeare char-LM has V_eff ~ 3-4 (low conditional entropy)
- Substrate-product reading: if outperforms synthetic V=70 K=8, confirms char-LM product niche
- Tier hint: GPU (same scale as Bundle B); can share infrastructure with G1
- Why-now: Validates the V_eff branch of the corrected law; highest product relevance

### 5. Cell X2 -- Position-binding at K=8, V=70, N=4096 (not N=8192)
- Anchor pointer: N-bottleneck test at K=8; is N=4096 sufficient or does K=8 require N=8192?
- Substrate-product reading: if HP at N=4096, substrate ceiling is higher than previously thought
- Tier hint: GPU smoke; lower priority than X1+G1 but resolves N-scaling coefficient
- Why-now: Cheaply resolves whether N is the bottleneck or architecture is

---

## Context Pointers

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_substrate_true_task_complexity_scaling_law_2x_2026-06-04.md
- Prior K* ceiling research: d:/AI/hd-instrument/notes/research_drill_substrate_task_complexity_ceiling_2x_2026-06-04.md
- Prior handoff (task-complexity ceiling): d:/AI/hd-instrument/notes/exp_dev_handoff_research_task_complexity_ceiling_2026-06-04.md
- Bundle E results (E1 pos-binding HP): d:/AI/hd-instrument/data/substrate_capability_map.md
- Bundle B results (K=8 HP): d:/AI/hd-instrument/data/substrate_capability_map.md
- Phase 0.5 auth: notes/project_phase05_combined_auth_2026-06-02.md (in memory)

---

## Contract

exp_dev autonomously decides:
- Exact anchor names (must include _n<N> suffix per PROT-018)
- Sweep parameters, seed counts, timeout formulas
- Queue assignment (overnight_queue vs remote_cpu_queue per torch-usage rule)
- HP/MID/HF numerical thresholds per envelope-fail-bands
- Sequencing (X1 cheapest; run before G1/G2; G1+G2 can parallel after X1)

exp_dev does NOT need to return to research or orchestrator for further design decisions.

## Autonomy declaration

This handoff is complete. exp_dev has full autonomy to design and dispatch anchors X1, G1, G2,
H1, X2 (in priority order) subject only to pause-flag check and queue depth >= 1 invariant.
