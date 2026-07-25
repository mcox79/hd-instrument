# Pre-reg: native_meaning_encoder_wordnet_mechanism_v1

Date: 2026-07-25
Author: exp_dev (Director task; coordinator reframes: sparse-code crosstalk + fusion/readout)
Cell: `experiments/exp_native_meaning_encoder_wordnet_mechanism_v1.py`
Contract: INLINE-LOCAL CPU foreground; metrics.json; NO atom banking (skunkworks owns VET); VET-PENDING.

## Question (MECHANISM, not density)

Predecessor (`exp_native_meaning_encoder_binder_grounded_v1`, commit e45e89f0e / seq 29564) found
earn-grounded-meaning-from-RELATIONS is WEAK (relations-only p@10 0.139 vs distributional context 0.243)
and that adding relations to context DILUTES it (both 0.204 < context 0.243). VET seq 29564 established
that DENSITY is NOT the lever (per-concept corr(n_relations, relations p@10) ~= -0.007; dense strata
anti-scale). The two nearest UNTESTED levers are MECHANISM:

1. SPARSE CODES (crosstalk hypothesis): dense mean-bundling of many R^300 relation vectors blurs the
   centroid (dense-superposition crosstalk = the density-collapse signature). Fix = sparse low-crosstalk
   composition (cortical).
2. FUSION / READOUT: the "relations dilute context" artifact may be NAIVE CONCAT + a SINGLE GLOBAL ridge
   lambda (noisy relation dims add variance under one lambda). Fix = weighted / per-block fusion (block-
   diagonal ridge lambda; relation block regularized separately) = a learned/weighted readout.

CAN MECHANISM RESCUE RELATIONAL GROUNDING? WordNet supplies a RICHER structural relation set (mean ~33
rels/concept vs WorldTree ~2.4) = more raw material for the mechanism. Density is INSTRUMENTED (crosstalk
pairwise-overlap), NOT the hypothesis.

## Design (ONE variable = the mechanism; matched concept set)

- Concept set: Binder-534 INTERSECT WorldTree (>=1 rel) INTERSECT WordNet noun-synset INTERSECT native vocab
  = 139 matched concepts. Every arm on the SAME 139 concepts, SAME 5-fold no-leak CV, SAME p@10-vs-Binder-65
  gold-neighborhood metric. Retrieval pool = all 534 Binder gold vectors.
- Native encoder: trained IDENTICALLY to predecessor (ARC context SGNS + WorldTree relation channel;
  error-driven; NO GloVe/BGE in the learned rep). SMOKE_ENC (70k sentences, 1500 steps) = predecessor's
  147s regime. Reproduces context 0.2426 / relations_worldtree 0.139 as Gate-D positive controls.
- WordNet relations (SUPPLIED clean structure; first/most-frequent noun synset = honest polysemy):
  hypernym CLOSURE -> KINDOF; part meronyms -> PARTOF; substance meronyms -> MADEOF; member holonyms ->
  PARTOF; co-hyponyms/sisters -> SIMILAR (capped 20; total cap 60 to bound the noisy sister tail).
- Relation encodings: DENSE mean(E[value]+R[reltype]) [predecessor-faithful]; typed-BIND (circular-conv
  bind of a role key with E[value]); SPARSE-GSBC (random-lift 300->4096 + certified `_gsbc_code_from_z`
  top-3/block, summed); SPARSE-kWTA (sign-preserving top-45/300 on the LEARNED code, summed -- faithful,
  no random-projection loss).
- Fusion: naive-concat single-lambda vs WEIGHTED (block-diagonal ridge lambda; relation-block multiplier
  selected by INNER 3-fold CV MSE on TRAIN folds only -- no leak).

## Arm matrix (17 arms)

Fixed baselines/controls: chance; context_only (~0.243); untrained_input; relations_worldtree_dense_naive
(~0.139); both_wordnet_dense_naiveconcat (~0.204). Relations-alone x {DENSE, GSBC, kWTA, typed-bind} on
WordNet + WorldTree kWTA/GSBC validity checks. Fused x {naive, weighted} x {dense, GSBC, kWTA}. Shuffle
(permute relation->Binder target in TRAIN; MUST collapse).

## Bands (a priori, can-fail)

- **MECHANISM-RESCUED**: a SPARSE and/or WEIGHTED-FUSION (and/or typed-BIND) arm lifts the relational
  contribution MEANINGFULLY past 0.139 toward/above context 0.243 -- EITHER relations-alone >= 0.139 + LIFT
  (0.05) and generalizes (CI-lower > chance AND > untrained) [S1], OR a WEIGHTED-fusion arm > context +
  FUSE_EPS (0.01) AND > its naive-concat sibling [S2] -- with shuffle-collapse + no-leak. Report WHICH lever.
- **HONEST-WALL-structure-insufficient**: NONE of {sparse-kWTA, sparse-GSBC, weighted-fusion, typed-bind}
  lifts relations past ~0.139 (best_rel_alone within FLAT_EPS 0.03 of 0.139) AND best weighted-fusion does
  not beat context by >= FUSE_EPS. Relational/taxonomic grounding is mechanism+data limited even after the
  nearest fixes; grounding needs MORE than taxonomy (sensorimotor/Barsalou).
- **MIDDLE-partial-lift**: some lift (> 0.139 + LIFT) but below context and fusion does not beat context.
- **INVALID**: shuffle does NOT collapse (leak) OR n_test < 40 OR Gate-D controls out of band (context not
  in [0.20,0.29] or relations_worldtree not in [0.10,0.18]).

## Discriminator / validity

- Can-fail both ways (baseline context 0.245 well below 1.0; relations 0.139 is the bar to beat).
- SPARSE-lever validity: kWTA (faithful, keeps learned dims) vs GSBC (random-lift, lossy). Validity check =
  does kWTA PRESERVE the WorldTree dense signal (0.130) that GSBC destroys? If GSBC destroys signal, its null
  is a lossy-construction confound, NOT a fair sparse test; kWTA is the fair test.
- Crosstalk instrumentation: within-bundle constituent pairwise-overlap (LOWER = less crosstalk; the fair,
  non-negativity-robust metric) + own/cross bundle recoverability (caveat: cross biased up by GSBC
  non-negativity). Crosstalk-limited iff sparse pairwise-overlap << dense AND the faithful kWTA arm >> dense.
- calibration_check: fusion relation-block lambda multiplier by inner-CV MSE (TRAIN only); RIDGE_LAMBDA_HD
  dim-scaled (4096/300) not tuned-for-PASS; shuffle-collapse still gates.
- crlb_n/a: retrieval p@10 has no closed-form estimator noise floor; empirical chance (~0.026) + shuffle-
  collapse is the discriminator gate.

## Cell-template

except SystemExit before Exception (no BaseException/bare); tmp_replace atomic metrics; start-marker +
crash-diagnostic + heartbeat; arms_differ (per-arm pk hashes); deterministic (fixed int seeds, numpy
default_rng, sorted); real-code-path self-test (REAL Binder + WT parse + WordNet extract + tiny ARC encoder
+ GSBC + kWTA + ridge/fusion CV + planted-separability + shuffle-collapse + sparse-lowers-crosstalk +
determinism); progress print_flush_true; all headline numbers MEASURED@ this metrics.json.

## RESULT (MEASURED@data/exp_native_meaning_encoder_wordnet_mechanism_v1_smoke/metrics.json)

Verdict: **HONEST-WALL-structure-insufficient** (n_test=139, elapsed 258s, Gate-D controls reproduce,
shuffle collapses).
Matrix: context 0.245 | relations_worldtree_dense 0.130 | both_naive 0.219 -> both_weighted 0.250 (fusion
FIXES dilution +0.031, but only +0.004 over context < FUSE_EPS). Relations-alone: WordNet dense 0.049,
GSBC 0.033, kWTA 0.035, typed-bind 0.042; WorldTree kWTA 0.094, GSBC 0.034. Sparse LOWERS crosstalk
(pairwise dense 0.406 -> kWTA 0.297) yet does NOT improve retrieval => REFUTES the crosstalk-is-the-limiter
hypothesis. Density HURTS relations-alone (WordNet 33 rels 0.049 << WorldTree 2.4 rels 0.130). Sparse-
validity: kWTA preserves WorldTree (0.094, delta -0.037) while GSBC destroys it (0.034, delta -0.096) =>
kWTA is the fair sparse test and it still fails. NET: neither nearest mechanism fix rescues relational
grounding; taxonomy alone does not carry grounded meaning beyond distributional context.
