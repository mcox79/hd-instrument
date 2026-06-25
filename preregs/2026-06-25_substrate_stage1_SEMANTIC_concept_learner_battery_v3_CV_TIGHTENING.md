# PRE-REG: substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING

**Date:** 2026-06-25
**Cell:** `experiments/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING.py`
**Lane:** 1 (substrate-native)
**Routing:** remote_cpu_queue (via hdi_orchestrator handoff; CPU-feasible synthetic data)

## What it tests

v3 CV-tightening rerun of `substrate_stage1_SEMANTIC_concept_learner_battery_v2_FULL`. v2
landed `HARD_PASS` with 6/6 arms PASS but `max_cv = 0.083` above the 0.05
chain-grade-DEFINITIVE threshold. Pattern: 3 seeds was too few to drive CV below 0.05
with smaller-N effects.

v3 doubles seeds + adds more concepts for better averaging through chain primitives:
- SEEDS 3 -> 5
- N_CATEGORIES 8 -> 12
- N_ATTRIBUTES 12 -> 16
- M_basic 96 -> 144
- n_heldout 8 -> 12 (tighter A3 PRIMARY CV)
- n_foreign 6 -> 8
- n_audit 24 -> 36

## Arms (UNCHANGED from v2 -- same 6)

1. A1 `arm1_learn_basic_facts` (recall@5)
2. A2 `arm2_hierarchical_inheritance` (top1 via chain)
3. **A3 `arm3_generalization_new_inst` (top1 -- PRIMARY chain-grade signal)**
4. A4 `arm4_compositional_triple` (top1)
5. A5 `arm5_refuse_foreign_concept` (refuse + retention)
6. A6 `arm6_audit_chain_semantic` (chain_completeness)

## HARD bands (production-scale, definitive)

- `STAGE_1_CHAIN_GRADE_DEFINITIVE`: >= 5/6 arms PASS AND `max_cv <= 0.05` AND A3 top1 >= 0.95
  (UPGRADE target from v2)
- `STAGE_1_CHAIN_GRADE_ALIVE`: >= 5/6 arms PASS (any CV) -- v2 status
- `STAGE_1_PARTIAL`: 3-4/6 PASS

## Per-arm bands (UNCHANGED from v2)

- A1 recall5 >= 0.95
- A2 >= 0.80
- A3 >= 0.85 (PRIMARY)
- A4 >= 0.50
- A5 refuse >= 0.80 AND retention >= 0.85
- A6 >= 0.70

## Production config (v3 CV-tightening)

- N_DIM = 8192
- V_categories = 12 (up from v2 8)
- inst/cat = 4 (same -> 48 instances total)
- V_attrs = 16 (up from v2 12)
- M_basic = 144, n_heldout = 12, n_foreign = 8, n_audit = 36
- sparse_f = 0.020, sparse_amp = 7.071
- SEEDS = [7, 13, 17, 23, 29] (5 seeds, up from v2 3)
- Timeout: 3600s (remote_cpu_queue)

## Self-test evidence

`.venv/Scripts/python.exe experiments/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING.py --self-test`
returns: `PASS cat_has_recall5=1.00 isa_recall5=1.00 verdict_path=HARD_PASS (n_atoms=14 N=1024 sparse_f=0.020)`

Verifies:
- Sparse-bipolar HRR primitives operational
- Chain composition correct (cat_has + isa_recall both 1.00)
- Verdict-path reaches HARD_PASS on synthetic-pass mock

## Cites

- `experiments/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v2_FULL.py` (v2 base)
- `data/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v2_FULL/metrics.json`
  (v2 HARD_PASS 6/6 arms PASS at max_cv=0.083)
- `notes/research_readout_degeneracy_5x_disparate_drill_2026-06-25.md` (drill context;
  Cell 3 is NOT in the degeneracy cohort but follows same authoring discipline)

## Honest scope

- Tests 6-arm substrate-native concept-learner battery with SYNTHETIC semantic data;
  Lane 1 chance-relative deltas only.
- Does NOT test transformer baselines, statistical-LM, or real corpus data; substrate
  generalizes via CHAIN PRIMITIVE composition NOT encoder pre-bias (encoder is random
  sparse-bipolar by design).
- If max_cv remains > 0.05 even with 5 seeds + 12 categories, the chain-primitive
  variance has a structural floor at this scale; honest finding either way (definitive
  upgrade OR characterization of the variance floor).
