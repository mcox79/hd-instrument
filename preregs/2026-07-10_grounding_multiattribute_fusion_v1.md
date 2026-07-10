# Pre-registration: grounding_multiattribute_fusion_v1

Date: 2026-07-10
Cell: `experiments/exp_grounding_multiattribute_fusion_v1.py`
Anchor: `grounding_multiattribute_fusion_v1`
Author: exp_dev (hdi_exp_dev)
Extends: `grounding_measured_attribute_concreteness_v1` (commit 382b6ae5e) -- the weak single-attribute MEASURED_MECHANISM.
Engine reused (validated): `grounding_consolidation_loop_degree_invariant_v1` (diffusion-with-restart + collapse
discriminator + independence gate; SELFTEST_PASS).
Drill: `notes/research_multi_attribute_grounding_fusion_ATL_hub_2026-07-10.md` (ATL hub-and-spoke; MLE cue combination;
inverse effectiveness; the attribute-independence pitfall). Prior-work check: substrate_query top hit = the tbind
FHRR modality-reliability-weighting drill (cosine 0.32, adjacent not duplicate); this cell is the FIRST multi-attribute
human-norm fusion over the diffusion-with-restart ConceptNet grounding engine -- genuinely novel, not a rediscovery.

## Question

Does RELIABILITY-WEIGHTED FUSION of several GENUINELY-INDEPENDENT measured attributes turn the WEAK single-attribute
grounding (concreteness-only: grounding_gap 0.059 but cross-seed cv 0.69, only 2/5 seeds clear 0.05, aggregate carried
by one seed, HIGH-degree stratum washes to 0.029) into a ROBUST grounding lift that clears the MM->CG promotion
criterion the single attribute MISSED?

## Datasets (public human-rating norms; LOCAL testbed inputs; provenance in data/grounding_testbed/PROVENANCE_multiattribute.md)

- Concreteness (Brysbaert 2014) Conc.M -- TARGET + anchor channel. (existing)
- Warriner (2013) valence/arousal/dominance -- `Ratings_Warriner_et_al.csv`,
  mirror https://raw.githubusercontent.com/JULIELab/XANEW/master/Ratings_Warriner_et_al.csv,
  sha256 78ac8107c78e116b...
- Lancaster/Lynott-Connell (2020) 6 sensory-modality perceptual-strength means -- `Lancaster_sensorimotor_norms_for_39707_words.csv`,
  OSF https://osf.io/48wsc/download, sha256 445d363fb1f9f3e5...
- Kuperman (2012) age-of-acquisition `AoA_Kup` -- `AoA_51715_words.csv`,
  mirror https://raw.githubusercontent.com/Cody-Lange/Milestone-2-Text-Difficulty-Classifier/main/assets/AoA_51715_words.csv,
  sha256 685c65e602b2fa6b...
NOT written to canonical substrate_index; NEVER git add -A; cell self-acquires via curl (header-key validated) if absent.

## Coverage-density diagnostic (cheap disambiguator; logged BEFORE the fusion verdict)

Per-held-out-node single-attribute lift |err_FA|-|err_AB| vs local density. MEASURED@existing v1 result (n=3262, 5 seeds):
Spearman(lift, visible-degree)=-0.052, Spearman(lift, #visible-neighbours)=-0.041; mean lift LOW-degree +0.028 vs
HIGH-degree -0.013. INTERPRETATION: the lift does NOT concentrate in high-coverage/high-density regions -- it is LARGEST
in SPARSE/low-degree regions and vanishes at HIGH degree because F_A already saturates there (headroom/ceiling artifact,
NOT missing coverage). => the marginality is CHANNEL-limited in the low/mid regime (fusion's target) and CEILING-limited
at HIGH. Fusion is the right lever for the low/mid fragility; HIGH is not expected to lift beyond non-negative.

## GUARDRAIL 1 -- per-attribute independence gate (make-or-break)

Report the full own-data pairwise |r| matrix; SELECT the fused set by MARGINAL-correlation greedy pruning: SEL=
[concreteness]; order remaining by |r_target| desc; ADD a candidate iff |r_target| >= MIN_TARGET_R (0.20; explains
>=4% of target variance = a real "sense") AND its max |r| with every already-selected attr < REDUNDANT_R (0.70; "highly
correlated -> treat as one channel", the drill's ~0.5-0.7 guidance; catches the imageability/concreteness r=-0.8 class).
Incremental R^2 (beyond the selected non-anchor extras) is computed + reported as a diagnostic. If fewer than 2 attrs
survive -> HARD_FAIL_CHANNELS_NOT_INDEPENDENT.
MEASURED@smoke selection: SELECTED = concreteness, visual (r=0.62), haptic (0.51), aoa (-0.42), interoceptive (-0.40),
olfactory (0.24) [n=6]. EXCLUDED: arousal (r=-0.17), auditory (-0.16), dominance (-0.09), valence (-0.01) [below the
0.20 sense-floor, per the drill "add VAD only if the gate clears them"]; gustatory (r_target 0.078 AND r=0.69 with
olfactory). incr_r2 beyond the other senses: visual +0.39, interoceptive +0.08, haptic +0.06, aoa +0.015, olfactory
+0.004 -- each adds non-redundant validity.

## GUARDRAIL 2 -- redundancy-faking must-fail control

Arm A_PLUS_FUSED_REDUNDANT fuses concreteness with near-duplicate copies of itself (concreteness + REDUNDANT_COPY_NOISE
0.15*std gaussian, mutual r ~0.99; K matched to the selected count). It must NOT beat single-attribute:
(redundant - single) <= REDUNDANT_MAX (0.02). If it does (>= FUSION_BEAT) the metric is laundering re-weighted
redundancy -> HARD_FAIL_REDUNDANCY_CHEAT. MEASURED@smoke: redundant_gap = +0.001 (fires; does NOT beat single).

## Fusion mechanic (late fusion; reliability-weighted MLE)

Per selected attribute k: leak-free restart anchor from attribute-k VISIBLE values (held-out AND missing MASKED to the
visible-observed mean; ALL channels masked on held-out so every channel grounds PURELY via graph diffusion -- the "rare
concept lacks all norms" regime), concat structural channel, diffuse-with-restart, ridge-predict held-out concreteness
-> pred_k. Reliability w_k = max(0, visible-CV Spearman)^2 (inverse-variance proxy) on a visible sub-holdout (val nodes
masked in the anchor -> NO leakage from the decision split; anti-overfit Pitfall #2). Fused = sum_k w_k * z(pred_k).

## Arms (all predict held-out concreteness on the SAME split per seed -> PAIRED)

F_TRIV (null), F_A (relational-only = ablation of ALL exterior channels), A_PLUS_B_SINGLE (concreteness-only = the v1
mechanism, baseline-to-BEAT), A_PLUS_FUSED (reliability-weighted fusion of the selected set = MECHANISM),
A_PLUS_FUSED_REDUNDANT (near-duplicate copies = redundancy control), A_PLUS_FUSED_SCRAMBLED (selected attrs permuted =
values control), C_CEILING (graph-neighbour TRUE-concreteness smoothing oracle).

## Pre-registered bands (numeric; BEFORE the FULL)

GROUND_MARGIN=0.05, CV_MAX=0.15, CV_FAIL=0.30, HIGH_NONNEG=0.0, FUSION_BEAT=0.02, REDUNDANT_MAX=0.02, SCRAMBLE_MAX=0.02,
TIE_EPS=0.0, MIN_STRAT_Q=40, HELDOUT_FRAC=0.30, VIS_VAL_FRAC=0.30, REDUNDANT_R=0.70, MIN_TARGET_R=0.20,
COLLAPSE_RANK_FLOOR=3.0, COLLAPSE_VAR_FLOOR=0.02, CONS_KNN=8, CONS_PASSES=6, CONS_ALPHA=0.25.

### HARD_PASS_FUSION_ROBUST (the VET-banked MM->CG promotion criterion; ALL must hold)
fairness cleared (F_triv<F_A<C) AND >=2 attrs survive independence AND not collapsed AND
(1) mean grounding_gap(FUSED - F_A) >= 0.05  AND
(2) cross-seed cv(grounding_gap) < 0.15  AND
(3) LEAVE-ONE-SEED-OUT: dropping ANY seed, mean grounding_gap still >= 0.05  AND
(4) HIGH-degree stratum fused gap >= 0.0 (NON-NEGATIVE; degree-uniform, HIGH no longer washes)  AND
(5) fusion BEATS single: mean(FUSED - single) >= 0.02  AND
(6) redundancy control: (redundant - single) <= 0.02  AND
(7) scramble control: (scrambled - F_A) <= 0.02.

### HARD_FAIL_FUSION_NOT_ROBUST
fusion ties single (FUSED - single <= 0.0) OR seed-fragile (cv >= 0.30 OR a LOSO drop < 0.05 with cv >= 0.15) OR
HIGH still washes (HIGH gap < 0.0).

### HARD_FAIL_REDUNDANCY_CHEAT
redundant control beats single by >= 0.02 OR scrambled grounds (>= 0.05).

### HARD_FAIL_FAIRNESS_BLOCKED / HARD_FAIL_CHANNELS_NOT_INDEPENDENT / HARD_FAIL_CONSOLIDATION_COLLAPSED
gates.

### MIDDLE_BAND_PARTIAL
otherwise (lift present but cv in [0.15,0.30) / gap sub-material / fusion-beat small).

## Smoke result (n=1609, 2 seeds, CPU 4.2s) -- SMOKE VERDICT ONLY; mechanism story HELD until landed-VET

VERDICT HARD_FAIL_FUSION_NOT_ROBUST, but the HARD_FAIL is driven ONLY by cv (0.43) and LOSO -- both STRUCTURALLY
MEANINGLESS at 2 seeds (cv of 2 points; LOSO drops to a single seed). Every substantive gate is in the PASS direction:
F_A=0.520 single=0.561 FUSED=0.581; fused_gap=0.061 (material PASS); fusion_beats_single=0.020 (at the 0.02 margin);
redundant_gap=+0.001 (control FIRES); scrambled_gap=-0.000 (control FIRES); STRATA fused_gap LOW=0.073 MID=0.066
HIGH=0.065 -> DEGREE-UNIFORM, HIGH strongly NON-NEGATIVE (the v1 HIGH-washout of 0.029 is FIXED). The 5-seed FULL is the
canonical resolver for cv<0.15 + LOSO robustness (exactly the seed-robustness the smoke cannot assess). Discriminator-
survives-scale: both must-fail controls fire at smoke scale; the open measurement is whether fusion-beats-single + cv +
LOSO hold at 5 seeds / n=3262.

## Self-test (SELFTEST_PASS, 1.6s CPU) -- planted worlds; discriminators FIRE

(a) INDEPENDENT world (K channels = hidden latent + INDEP noise, mutual r ~0.5): fusion BEATS single (+0.032), ground
gap 0.243, gate selects all 6; (b) REDUNDANT world (shared noise, mutual r ~0.98): near-duplicate arm does NOT beat
single (-0.003) + gate PRUNES the extras to n=1; (c) scrambled does NOT ground (-0.002); fairness gate passes the
headroom world (F_A 0.18 < C 0.52) + BLOCKS the unpredictable world (F_A -0.11 ~ C -0.04); (d) collapse caught; arms
differ (>=6 distinct sigs).

## SCHEMA-VET

cell_chunked: false; start_marker_written: true; crash_diagnostic_present: true; final_metrics_atomicity: tmp_replace
(write_metrics + os.replace; write_partial per seed); arms_differ_verified: true (>=6 distinct arm sigs, asserted per
seed); except SystemExit before except Exception (no bare/BaseException; grep-gate clean); crlb: Spearman chance ~0
THEORETICAL, HARD_PASS strictly above; baseline_in_band: F_TRIV null ~0, C must-fire ceiling > F_A (0.69 > 0.52);
discriminator-survives-scale: engine params shared self-test<->FULL, both must-fail controls fire at smoke; cardinality_ok:
EXPECTED_N_UNITS=n_seeds (per-seed arms-differ assertion + cardinality-breach guard); calibration_check:
default_ok_for_this_regime -- REDUNDANT_R=0.70 + MIN_TARGET_R=0.20 are PRINCIPLED (highly-correlated / >=4%-variance
sense-floor), set from the drill's guidance not tuned to a PASS (smoke aggregate 0.061 clears the 0.05 bar but the cell
HARD_FAILs on the 2-seed cv, i.e. the bands are not smoke-tuned); progress_logging: print_flush_true (line-buffered +
per-seed/per-stratum flush); positive_control: C_CEILING oracle fires (> F_A); functional_requirements: predict measured
attribute from graph + fused exterior senses, each sense must be non-redundant (independence gate) + load-bearing
(ablation to F_A) + values-dependent (scramble) + not-laundering-redundancy (redundant control) -- decomposed.
Data-dependency: cell self-acquires all 4 public testbed files via curl (header-validated), else HARD_FAIL_DATA_MISSING.

## Compute architecture

class (a), CPU-fast: structural features + per-channel diffusion-with-restart (dense [n,n]@[n,dim], n~3262) + ridge
solves. ~K*(2 diffusions)/seed, K=6 selected -> smoke 4.2s (n=1609, 2 seeds); FULL n=3262, 5 seeds extrapolates ~60-90s.
NO KGE / NO encoder. Storage SHARDED. FULL routes to remote_cpu_queue (CPU; no GPU benefit; SMOKE-ONLY-LOCAL lock keeps
the laptop free). Requires the 4 testbed files on the runner (self-acquired via curl).

## Config

FULL: seeds=[7,13,17,23,29], n_nodes=5000 (n~3262). SMOKE: seeds=[7,13], n_nodes=2500 (n~1609). SELFTEST: planted worlds.
FULL timeout: 600s (>6x the ~90s estimate; stays under the 1800s heartbeat-mandate threshold -- per-seed flush logging).
