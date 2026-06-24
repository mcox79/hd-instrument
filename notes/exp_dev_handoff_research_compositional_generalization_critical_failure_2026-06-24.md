# exp_dev hand-off — research: compositional generalization critical-failure diagnosis

**Date.** 2026-06-24
**Owner.** Research → exp_dev.
**Trigger.** ARM 2 HARD_FAIL in `data/exp_substrate_brain_aligned_aliveness_shotgun_v1/metrics.json`; load-bearing drill at `notes/research_compositional_generalization_critical_failure_2x_drill_2026-06-24.md`.

**Pause state.** Honor `data/orchestrator_paused.flag` if present. If paused: file the cell-author specs to backlog (not the queue) and do NOT dispatch.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchors + bands + why-now. exp_dev decides smoke gate, queue, self-tests, ship mechanics.

## TASK

Three diagnostic retest cells (all cheap CPU, all <= 5 min wall each, all D=8192 single-seed-OK).
The load-bearing question: was ARM 2 mis-specified (most likely diagnosis P=0.85) or is the
substrate HRR primitive broken (low-prob fallback P=0.15)?

### Anchor candidates (rank-ordered)

**1. ANCHOR `substrate_arm2_capacity_respecting_pair_storage_v1`** (HIGHEST PRIORITY)

Tier hint: chain-grade-eligible diagnostic.

- D=8192, sparse-bipolar f=0.05.
- n_subj=20, n_obj=20, M=20 train pairs in 1-to-1 mapping: train pairs = [(i, pi(i)) for i in 0..19] where pi is a random permutation.
- Bank = sum_{(i,j) in train} bind(A_i, B_j).
- Compute in-distribution top-1: for each (i, pi(i)) in train, unbind(bank, A_i) and check argmax over obj_book == pi(i).
- Bands: HARD_PASS in-dist >= 0.95; HARD_FAIL in-dist < 0.80.
- Substrate-product reading: confirms or refutes HRR primitive capacity at canonical regime (M = vocab, 1-to-1).
- Why-now: the shotgun ARM 2 in-dist=0.10 confirms saturation at M=200; this is the canonical
  capacity-respecting test that should be the baseline for ALL HRR primitive evaluation going
  forward.

**2. ANCHOR `substrate_compositional_K10_K20_reconfirm_n8192_v1`** (PRIORITY 2)

Tier hint: chain-grade reconfirmation at upscaled N.

- Re-run the prior `substrate_compositional_generalization_K10_to_K20_v1_n4096` cell mechanism but at N=8192 (matching shotgun ARM 2's dim for direct comparability).
- Same G, L=20, LOAD_FRAC=0.3, K_TEST=[10,15,20], 3 seeds.
- Bands: HARD_PASS K=15 top-1 >= 0.70 (matches prior K15=1.000); HARD_FAIL K=15 < 0.50.
- Substrate-product reading: confirms substrate compositional-generalization capability at the
  AT D=8192, which is the relevant scale for the aliveness shotgun comparison.
- Why-now: contradicts the shotgun's BRAIN_ALIGNED_PARTIAL framing -- substrate IS alive on
  correctly-specified compositional generalization.

**3. ANCHOR `substrate_role_tagged_structural_holdout_v1`** (PRIORITY 3 -- exploratory)

Tier hint: MEASURED_MECHANISM (novel-architecture; calibration penalty applies).

- D=8192, sparse-bipolar f=0.05.
- 5 subject classes, 5 object classes; 4 instances per class for both subj (20 total) and obj (20 total).
- Train: for each pair_id k in train (25 pairs, one (subj_class_i, obj_class_j) cell), encode
  with role-tagged binding:
  ```
  payload_k = bind(R_subj, A_{i,m}) + bind(R_obj, B_{j,n})
  bank += bind(pair_id_k, payload_k)
  ```
  where (i,j,m,n) randomly chosen per pair_id.
- Holdout: a held (A_{i,m'}, B_{j,n'}) of a SEEN class combination (i,j) but DIFFERENT instances
  (m', n'). Test: can substrate recover B_{j,n'} given A_{i,m'} + the class-structure prior?
- Bands: HARD_PASS holdout top-1 >= 0.50; HARD_FAIL < 0.20; MIDDLE 0.20-0.50.
- Substrate-product reading: probes whether role-tagged binding alone (no learning) can support
  structural compositional generalization. If yes -> substrate has a structural-prior primitive
  beyond pair-bind. If no -> substrate needs cf-RPE replay or similar learning step.
- Why-now: this is the novel architectural claim worth probing; calibration penalty deflates
  P_pass to 0.30; experiment is cheap enough to run regardless.

## CONTRACT

Per [[feedback-envelope-expansion-fail-bands]]: bands above are sacrosanct both directions. Pass
above HARD_PASS = atom + Store ingestion same cycle. Fail below HARD_FAIL = HARD_FAIL atom + 2x
research drill.

Per [[feedback-formula-selftests]]: each cell must include selftest:
- ANCHOR 1: at D=512, M=5, 1-to-1, expect in-dist=1.000.
- ANCHOR 2: at N=256, L=4, K=3, expect 3-hop composition cos > 0.9.
- ANCHOR 3: at D=512, 2 classes x 2 obj, M=4 train, expect role-tagged holdout > 2x chance.

Per [[feedback-substrate-mine-capacity-before-extrapolating]]: ANCHOR 2 should be a near-verbatim
re-run of the existing chain-grade-PASS cell at upscaled N; no novel synthesis.

Per [[feedback-by-construction-saturation]]: if ANCHOR 1 in-dist=1.000 with very low cv, do NOT
escalate to chain-grade -- this is by-construction (M=20 << capacity at D=8192). Tier as
DIAGNOSTIC_PASS, not chain-grade.

## CONTEXT POINTERS

(file paths, not summaries)

- Research note (load-bearing diagnosis): `notes/research_compositional_generalization_critical_failure_2x_drill_2026-06-24.md`
- Failed cell: `data/exp_substrate_brain_aligned_aliveness_shotgun_v1/metrics.json` (ARM 2 details + in-dist=0.10 smoking gun)
- Failed cell source: `experiments/exp_substrate_brain_aligned_aliveness_shotgun_v1.py` (lines 185-230 for ARM 2)
- Prior PASS cell: `data/exp_substrate_compositional_generalization_K10_to_K20_v1_n4096/metrics.json`
- Prior PASS cell source: `experiments/exp_substrate_compositional_generalization_K10_to_K20_v1_n4096.py`
- Related primitive cells: `experiments/exp_bundle_capacity_theory_cpu_v1.py`, `experiments/exp_bundle_crosstalk_scaling_cpu_v1.py` (existing crosstalk math anchors)

## AUTONOMY

exp_dev decides:
- Queue choice (likely `local_cpu_queue` or `remote_cpu_queue`; cells are <= 5 min each so laptop quick-probe ok).
- Smoke gate per [[feedback-envelope-expansion-fail-bands]].
- Self-test pairs per [[feedback-strategy-spec-formula-selftests]] (spec'd above as recommendation; refine as needed).
- Ship-name-collision check per [[feedback-ship-name-collision]].
- Bundle priorities 1 + 2 in one dispatch; priority 3 separately if budget allows.
- Verdict envelope per standard.

## URGENCY

The shotgun's BRAIN_ALIGNED_PARTIAL verdict is mis-leading and currently in the status_log.
Resolving ANCHOR 1 + 2 in this cycle re-classifies substrate aliveness correctly. Recommend
dispatch within the next exp_dev cycle.
