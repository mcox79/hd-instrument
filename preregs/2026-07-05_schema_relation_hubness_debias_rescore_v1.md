# Pre-registration: schema_relation_hubness_debias_rescore_v1

**Filed:** 2026-07-05 by exp_dev (cell author)
**Cell:** `experiments/exp_schema_relation_hubness_debias_rescore_v1.py`
**Anchor:** `schema_relation_hubness_debias_rescore_v1`
**Queue (staged; NOT dispatched by exp_dev):** `overnight_queue` (GPU; reuses parent's torch-bmm B=2
  FROZEN + batched JOINT autograd; device auto->cuda). Acceptable fallback `remote_cpu_queue`
  (numpy/torch-cpu path correct; rescore is O(candidates^2), trivial).
**Timeout:** 3600 s (GPU estimate ~10-15 min; rescore adds negligible over the parent's ~7-10 min).
**Progress logging:** `print_flush_true` (all progress lines flush=True; line-buffered stdout).

## KB_REFERENT
- notes/research_hubness_popularity_debias_rank1_sharpening_2026-07-05.md (design source; CSLS +
  logit-adjust; per-relation hubness/label-prior diagnosis; Bands; training-free-first)
- experiments/exp_schema_relation_hitsatk_mrr_reframe_v1.py (commit 9cf4cc8c9; scorer/split/rank
  reused VERBATIM via `import ... as ref`)
- data/exp_schema_relation_hitsatk_mrr_reframe_v1_smoke/metrics.json (the PRE-rescore MIDDLE_BAND
  baseline the NONE variant reproduces exactly)

## Prior-work check (substrate-KB concept-query before authoring)
`bash tools/substrate_query.sh "hubness debias CSLS logit adjustment rank-1 rescore label prior
popularity"` top hit cosine=0.2783 (generic memory/wordnet/framenet atoms: "adjustment", "popularity").
**No prior arc cell at cosine>0.30.** This cell is genuinely novel (first CSLS/logit-adjust post-hoc
rescore on the substrate; not a rediscovery).

## Scientific question
The reframe cell landed MIDDLE_BAND: the true object lands top-10 but not rank-1; a drill diagnosed
the rank-1 crowding as geometric HUBNESS (object argmax-winner Gini 0.87-0.95) + LABEL-PRIOR bias
(corr with train_freq 0.42-0.80). Proposed training-free fix: post-hoc rescore of the EXISTING (T,V)
score matrix combining CSLS (hubness) + logit-adjustment (label-prior). Does it sharpen rank-1
(lift the paired filtered MRR/Hits@1 rms) with no retraining?

## THE ONE CHANGE vs the parent reframe
Add a post-hoc RESCORE step before ranking. Scores are first converted to per-row CALIBRATED
LOG-PROBS `L = log_softmax(S / slot_tau)` (log_softmax is strictly row-monotone -> the NONE variant
ranks IDENTICALLY to the parent reframe; positive-control reproduce asserted in-cell, Gate D). Then:
```
NONE  = L
CSLS  = L - r_k(row) - r_k(col)               # coefficient-1 (see CSLS-COEFFICIENT below)
LOGIT = L - tau * log P_train(object)         # tau=1.0 (Menon et al. 2021)
BOTH  = L - r_k(row) - r_k(col) - tau*log P_train(object)
```
k=10 (Conneau et al. 2018 standard; note pre-reg k), tau=1.0, both FIXED before the real run.
Ablation {NONE, CSLS, LOGIT, BOTH} x slots {FROZEN, JOINT, KNN} x arms {REAL, SHUFFLED} x evals
{inductive, transductive}. Same corpus/features/split/seeds as the parent.

## CSLS-COEFFICIENT (load-bearing design decision; exp_dev off-disk 2026-07-05)
Canonical CSLS (Conneau 2018) is `2*cos - r_k(x) - r_k(y)`, correct for a BOUNDED symmetric cosine.
For an UNBOUNDED per-row log-prob, a pure additive object-hub bias c_j SURVIVES the 2x form at
coefficient +1, but is fully removed (from the within-row ranking) by the coefficient-1 form -- which
is exactly the note's own written formula `s'(t,j) = s(t,j) - CSLS_term(t,j)`. exp_dev verified this
off-disk and confirmed CSLS(L+c) = CSLS(L) + per-row-constant (identical row argsort). The APPLIED
rescore uses coef-1; the canonical 2x is retained as a documented identity in the formula self-test.

## Contract -- PRE-REGISTERED BANDS (falsifiable; both directions)
Load-bearing comparison: POST-RESCORE vs PRE-RESCORE (NONE), PAIRED, same seed/config units, on the
filtered inductive REAL-minus-SHUFFLED (rms) discriminator.
- **HARD_PASS** = best-of-{FROZEN,JOINT} x {CSLS,LOGIT,BOTH}: filtered MRR rms >= 0.15 AND filtered
  Hits@1 rms LIFT (post minus matched NONE) >= 0.05 AND Hits@10 rms >= 0.20 (non-regression), holding
  on >=2 semantic relations x >=2 encoders at V>=300. Discriminator must fire.
- **HARD_FAIL** = max over semantic (rel x enc) at V>=300 of the best MRR rms LIFT <= +0.02 (rescore
  measurably fails to move MRR) while the synthetic veneer control fired. Redirects to trained
  hard-negative mining (DPR/ANCE) or richer content.
- **MIDDLE_BAND** = between (MRR rms lift in (+0.02, +0.15), or Hits@1 lifts but MRR short of 0.15 on
  one relation). Real but partial; stage the trained complements.

Bands ordered and separated (HF MRR lift 0.02 < HP MRR rms floor 0.15). META_RULE_L satisfied.

## EXP_DEV PRE-DISPATCH FINDINGS (MEASURED off-disk + smoke 2026-07-05; surfaced honestly)
Two load-bearing findings from the smoke that shaped the cell design:

1. **SHUFFLED-COLLAPSE PHANTOM (anti-phantom guard added).** The paired rms (REAL-SHUFFLED) MRR lift
   is GAMEABLE: on the FROZEN slot for CausesDesire (whose SHUFFLED arm is popularity-saturated,
   Gini 0.97), CSLS CRUSHES the SHUFFLED popularity control (Hits@1 0.567->0.0) while REAL rank-1
   actually DEGRADES (Hits@1 0.633->0.60) -- yet the paired rms MRR "lifts" +0.49. That is NOT rank-1
   sharpening; it is the mirror of the task's "rescore must not lift shuffled" artifact. The verdict
   now requires the rms improvement to be REAL-DRIVEN: HARD_PASS `clears` demands REAL-absolute Hits@1
   does NOT degrade (`real_h1_lift >= 0`). The cell reports `best_real_mrr_lift` (honest) alongside
   `best_mrr_rms_lift` (may be shuffled-collapse) + a per-cell `shuffled_collapse_phantom` flag.

2. **CSLS sharpening is SCORER-STRENGTH-DEPENDENT (discriminator-survives-scale flag).** On the
   FROZEN slot (near-full-strength even at smoke: 300 steps df=128) the rescore does NOT genuinely
   sharpen REAL rank-1 (only the phantom, correctly rejected). But on the JOINT slot -- which at SMOKE
   is UNDERTRAINED (80 steps) -- CSLS produces a DRAMATIC GENUINE sharpening on CausesDesire: REAL
   Hits@1 0.067->0.533 (+0.467), REAL MRR 0.129->0.58, while JOINT-SHUFFLED stays at 0.0 (no phantom,
   guard-verified). Mechanism: the undertrained JOINT collapses toward a few directions (a geometric
   hub over recoverable signal -- exactly the veneer positive-control phenomenon), which CSLS removes.
   **CAVEAT: FULL JOINT trains 500 steps (H=256 df=128) -- a STRONGER regime that may have LESS
   geometric-hub collapse, so the JOINT sharpening may SHRINK or vanish at FULL (classic
   discriminator-survives-scale risk; the smoke JOINT HP != FULL JOINT HP).** The FROZEN slot is the
   scale-representative one and shows no genuine win.

**Honest FULL prediction:** MIDDLE_BAND most likely (genuine CSLS sharpening on some JOINT/weak-scorer
cells but not clearing >=2 rel x >=2 enc at FULL-strength FROZEN); HARD_PASS if the JOINT sharpening
survives 500-step training across both encoders; HARD_FAIL if it does not and FROZEN carries nothing.
Discriminator fires (veneer CSLS REAL Hits@1 +0.095, rms +0.095, SHUFFLED not lifted; null clean).
The cell reports REAL-abs lift, SHUFFLED-abs lift, per-cell shuffled-collapse flag, and REAL-vs-
SHUFFLED argmax-winner Gini asymmetry so any band is interpretable. **DIRECTOR/RESEARCH note:** the
finding that CSLS-hubness-correction helps WEAK/hub-collapsed scorers (undertrained JOINT) but not
strong ones (FROZEN) is itself a real mechanism result worth the full measurement.

## Compute architecture
Class **(a) batched-GPU** (inherited from the parent: FROZEN torch-bmm B=2, JOINT batched autograd
B=2, kNN vectorized). Rescore = vectorized top-k reductions + column log-prior subtraction, O(V^2) at
V<=1000, trivial. Storage strategy: **no_storage** (single-hop ranking; no composition). No
generative-LLM calls (n_generative_llm_calls=0).

## SCHEMA-VET pre-dispatch checklist
- `cardinality_ok`: EXPECTED_N_UNITS = sum over grid of (rels x encs) x 3 slots x 2 arms x 2 evals;
  4 rescore variants are SUB-FIELDS of each unit (not separate units), so structure == parent.
  FULL = 3 V x 3 rels x 2 encs x 12 x 3 seeds = **648 units**. HARD_FAILs on breach unless gsbc-missing.
- `arms_differ_verified`: {NONE,CSLS,LOGIT,BOTH} REAL matrices pairwise differ + REAL!=SHUFFLED per
  variant (sha256; META_RULE_AF). MEASURED@selftest: True.
- `final_metrics_atomicity`: `tmp_replace`.
- `except SystemExit: raise` before `except Exception` (no BaseException; grep-clean). start-marker +
  crash-diagnostic + heartbeat present.
- `crlb_n/a`: rank transfer, no closed-form noise floor. Reachability: HF MRR lift 0.02 < HP MRR rms
  0.15 < 0.95 (asserted at import).
- `baseline_in_band` (META_RULE_AG): NONE reproduces the parent (asserted in-cell: log_softmax
  row-monotone -> identical filtered ranks). SHUFFLED filtered Hits@10 < 0.95 (not saturated).
- `discriminator_fires` (META_RULE_K): synth_csls_hub_veneer must recover REAL rank-1 (max(CSLS,BOTH)
  REAL Hits@1 lift >= 0.05 AND rms Hits@1 lift >= 0.05) while SHUFFLED not lifted (<= 0.04);
  synth_hub_null must be clean (|BOTH rms lift| <= 0.03). Two REPORTED diagnostics document the
  non-firing regimes: synth_label_hub_shared (paired-rms cancellation of shared label-prior) and
  synth_deep_truth (deep-truth non-recovery). This is the smoke-provable discriminator; the V>=300
  real recovery is the map question itself, justified per DISCRIMINATOR-MUST-SURVIVE-SCALE (C).
- `calibration_check`: `adaptive_with_discriminator_gate` (k/tau FIXED pre-run at standard defaults;
  veneer-fires + null-clean are the proofs; not tuned-for-pass on real data).
- `HP_SCOPE`: {best-of-{FROZEN,JOINT} x {CSLS,LOGIT,BOTH} REAL/inductive/FILTERED SEMANTIC at V>=300:
  [HARD_PASS, HARD_FAIL, MIDDLE_BAND]; NONE: pre-rescore baseline reproduces parent NOT HP; KNN:
  reference NOT HP; DerivedFrom: watchdog NOT HP; SHUFFLED: control/artifact-guard; raw: not gating}.
- §15 gates: Gate D positive control = NONE variant IS the reproduction of the parent reframe AT THE
  IDENTICAL regime (asserted bit-for-bit-rank in-cell); rescore functions verified at import on
  hand-constructed exact values (CSLS coef-1 + canonical-2x + logit + log-softmax monotonicity).
  Gate A/C n/a (no primitive-composition; single post-hoc rescore step). Gate B: the discriminating
  band is guarded by the veneer/null synthetic controls. Gate E: functional requirement = "recover
  rank-1 the hub/label-prior bias suppresses" -> mapped to CSLS + logit-adjust primitives.

## Smoke result (LOCAL, exp_dev pre-flight; MEASURED@data/exp_schema_relation_hubness_debias_rescore_v1_smoke/metrics.json)
- run_mode=smoke, size=440KB, elapsed 66s, good_units=48/48, cardinality_ok=True, fatal=False.
- arms_differ_verified=True; discriminator_fires=True: veneer CSLS REAL Hits@1 lift +0.095 / rms +0.095,
  SHUFFLED not lifted +0.000, LOGIT inert on the density hub +0.000; null BOTH rms Hits@1 lift -0.01
  (clean). label_hub_shared BOTH rms MRR lift -0.0014 (paired-cancellation demo confirmed).
- Formula self-tests PASS: CSLS coef-1 (+ canonical-2x reference identity), logit-adjust, log-softmax
  row-monotonicity, log-prior shuffle-invariance; NONE ranks the raw score S (bit-exact parent reproduce).
- SHUFFLED FROZEN filtered Hits@10 = 0.617 < 0.95 (baseline in band, not saturated).
- verdict=MIDDLE_BAND (best_REAL_MRR_lift@V300+=0.451 honest [JOINT CausesDesire, SHUFFLED unaffected];
  best_MRR_rms_lift@V300+=0.4948 partly shuffled-collapse on FROZEN, correctly flagged/rejected).
- The genuine JOINT-CausesDesire win is smoke-JOINT-regime-specific (see FINDING 2 caveat above).
