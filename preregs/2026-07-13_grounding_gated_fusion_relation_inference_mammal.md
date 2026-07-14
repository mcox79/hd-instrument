# Pre-reg: GROUNDING GATED-FUSION (recover grounding's strength via a glass-box learned gate)

- Anchor: `grounding_gated_fusion_relation_inference_mammal_v1`
- Cell: `experiments/exp_grounding_gated_fusion_relation_inference_mammal_v1.py`
- Date: 2026-07-13
- Queue target: `remote_cpu_queue` (CPU-cheap; N~128, nq~28, seconds/seed)
- Forks: `grounding_improves_relation_inference_mammal_v1` (REUSES arena/arms/controls/FPE wiring;
  ONLY the fusion changes).

## Question (a follow-up to the v1 landed-VET)
v1 PROVED grounding carries genuine leak-free signal on held-out relation inference
(MEASURED@data/exp_grounding_improves_relation_inference_mammal_v1/metrics.json:gates.heldout_mrr:
GROUNDED_ONLY=0.617996 >> RELATIONAL_ONLY=0.386723; grounding beat POP 8/8 seeds) BUT the naive
equal-weight fusion (alpha=beta=1, a literal SUM in the additive-KGE latent) DILUTED it:
GROUNDED_FUSED(1:1)=0.397608 ~= RELATIONAL, drowning the 0.618 grounding signal. VET diagnosis
(banked): the fusion failure is a DILUTION/magnitude artifact of the equal-weight SUM. This cell asks:
does a GLASS-BOX learned gate RECOVER grounding's standalone strength instead of drowning it?

## Mechanism (glass-box; low-dim; interpretable; NOT an opaque net)
GATED_FUSED head code = (1-lambda)*relational_bundle + lambda*grounded_code (CONVEX; weights sum to 1
so magnitude stays on-manifold, unlike the SUM). lambda in [0,1] = a SINGLE learned scalar per seed,
chosen by grid-search (11 points 0.0..1.0) to MAXIMIZE MRR on a DISJOINT VALIDATION held-out entity
split. train / val / test entity partition; KGE fit + ridge grounding map see ONLY train; lambda is fit
on VAL; GATED is applied to TEST. One inspectable number per seed (reported as lambda_star). KEY
property: the pure-grounding endpoint lambda=1 is IN the gate's family, so on VAL the gate can never do
worse than GROUNDED_ONLY -> it RECOVERS grounding (adds a relational component only where VAL says it
helps). Cold (0-support) held-out entities -> pure grounding.

## Scope (honest, per VET framing)
All held-out queries in this mammal arena are d1 (exactly 1 support edge) -- the relational channel is
STARVED. This cell rescues low-support entity PLACEMENT via the grounded similarity signal; it is NOT a
multi-hop-reasoning result.

## Metric (PRIMARY = held-out RELATION inference; PAIRED ablation on the SAME queries)
Filtered MRR + hits@{1,3,10} rank-vs-all (KGE standard, degree-unbiased; no sampled-negative pool).
Split: TEST HELDOUT_ENTITY_FRAC=0.28, disjoint VAL_ENTITY_FRAC=0.16, SUPPORT_FRAC=0.34; train-absent
gold tails DROPPED.

## Arms (8; SHARDED per-entity codes; the only bundle is a per-ENTITY anchor mean)
- RELATIONAL_ONLY (ablation baseline): mean over support edges of (X[symbol]-D[r]).
- GATED_FUSED (mechanism): convex (1-lam)*rel + lam*grd, lam learned on VAL.
- GROUNDED_ONLY (recovery TARGET / reference): grounded ridge estimate only.
- FUSED_EQUAL_1TO1 (diagnostic): the OLD diluting alpha=beta=1 SUM being replaced.
- SCRAMBLE_GATED (must-fail): the SAME gate over attributes SHUFFLED across species; lambda re-learned.
- RANDOM_CODES (null); ORACLE_ADDITIVE (held-out folded in = arena-answerable ceiling); BASELINE_POP.

## PRE-REGISTERED BANDS (BOTH sides; RELATIVE to measured GROUNDED_ONLY reference + RELATIONAL baseline)
Absolute MRR shifts with the smaller train pool (val carved out), but recovery is a RELATIVE claim so
relative bands are robust. ORACLE saturates (~1.0) BY CONSTRUCTION -> arena-answerable gate only.
- GATED_FUSION_RECOVERS_GROUNDING (HARD_PASS), ALL of:
  (a) mean (GATED - RELATIONAL)_mrr >= 0.10  (real recovery, >> the +0.03 the naive fusion failed);
  (b) mean GATED_mrr >= GROUNDED_ONLY_mrr - 0.03  (NO dilution below grounding);
  (c) mean (GATED - SCRAMBLE)_mrr >= 0.05  (the RIGHT attributes, not any prior);
  (d) per-seed (GATED - RELATIONAL) > 0 in >= 75% of seeds;
  (e) ORACLE fires (>=3x RANDOM & headroom>=0.05) AND RELATIONAL above RANDOM (>=0.02) AND not broken.
- PARTIAL_RECOVERY (MIDDLE_BAND): mean (GATED - RELATIONAL)_mrr >= 0.03 but fails no-dilution OR
  scramble-margin OR consistency -- the gate helps over the naive fusion but does not fully recover.
- GATE_FAILS_TO_RECOVER (HARD_FAIL): mean (GATED - RELATIONAL)_mrr < 0.03 with ORACLE firing.
- INCONCLUSIVE if ORACLE does not fire / too few held-out queries / RELATIONAL at floor / RANDOM beats
  RELATIONAL (broken).

## Must-fail semantics (pre-registered scope clarification)
The RIGHT-attributes control is the GATED - SCRAMBLE margin (>= 0.05): real attributes must beat
SHUFFLED attributes through the same gate. Scrambled attributes CAN still lift above the STARVED d1
relational baseline (a ridge-placed grounded code is a plausible typical-entity prior beating a single
noisy relational estimate) -- this is NOT an "added-channel dimensionality" artifact because EVERY arm
shares the SAME k=16 latent (grounding BLENDS the head code, does not concatenate extra dims). So the
scramble-vs-relational delta is REPORTED as a diagnostic (scramble_artifact flag) but does NOT gate
HARD_PASS. (This is a deliberate correction of an initially-pre-registered secondary guard whose stated
rationale is structurally inapplicable here; the fair must-fail, GATED-SCRAMBLE, is retained.)

## FULL config
k=16, epochs=300, n_neg=48, seeds=[7,13,17,23,29,31,37,41] (8), device cpu. Weak-point localization:
support-degree stratified GATED-vs-RELATIONAL-vs-GROUNDED delta (all d1 in this arena).

## Validity preflight (F.1-F.4 ENFORCE) + machinery
- F.1 real_code_path: self-test CALLS fit_kge_anchor1 + filtered_hits_from_scores + fit_ridge (planted).
- F.2/F.3 substrate_signature: fit_kge_anchor1 bound with BASE/portable kwargs only.
- F.4 guard_baseline_valid: RELATIONAL_ONLY validated above RANDOM floor.
- positive_control: PLANTED latent-consistent arena (deg=3, multi-support) where attributes carry the
  latent -> the learned gate MUST recover grounding (GATED beats REL, no dilution below GROUNDED, beats
  SCRAMBLE) -> ship gate.
- arms_differ (>=6 sigs; EXEMPTED-by-correct-construction pairs: (GATED,GROUNDED) at lam*=1.0,
  (SCRAMBLE,RELATIONAL) at lam_scr=0.0), cardinality (n_seeds), no bare except, atomic metrics
  (tmp_replace), progress_logging=print_flush_true.

## Self-test (planted; enforce) + Smoke result (3 seeds, real mammal KG) -- HINT ONLY (hold story to VET)
SELFTEST_PASS under enforce: planted GATED=0.570 ~ GROUNDED=0.579 (dilution 0.009), gain over
RELATIONAL +0.456, beats FUSED_EQ(sum)=0.158 and SCRAMBLE=0.472, lambda*=0.8.
MEASURED@data/exp_grounding_gated_fusion_relation_inference_mammal_v1_smoke/metrics.json:
verdict=HARD_PASS_GATED_FUSION_RECOVERS_GROUNDING. RELATIONAL_mrr=0.2929 GATED=0.5816 (recover_gain
+0.2887); GROUNDED_ONLY=0.6050 (dilution 0.0234 <= 0.03, NO dilution); FUSED_EQ(1:1)=0.3484 (gate beats
the naive diluting fusion by +0.2332); SCRAMBLE=0.4406 (GATED-SCRAMBLE margin +0.1410); seeds_pos 3/3;
lambda*=[0.6,0.7,0.5]; ORACLE=1.0 (34.5x RANDOM, fires). The 8-seed FULL is the arbiter.
