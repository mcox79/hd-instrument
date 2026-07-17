# Pre-reg: IMPORTANCE (downstream-reach) as an ingest-prioritization signal on real CoDEx

Anchor: `importance_downstream_reach_ingest_prioritization_real_codex_v1`
Cell: `experiments/exp_importance_downstream_reach_ingest_prioritization_real_codex_v1.py`
Date: 2026-07-16. Local CPU single-shot run-to-completion. No queue/GPU/atoms/push.

## Question (3 parts, reported SEPARATELY -- do not blob)
The ingest-gate 4th axis (IMPORTANCE = downstream-reach / value-of-information; the "rock-at-head"
salience signal) was validated ONLY in the synthetic multisource arena. Schema-fit + recurrence already
won on real CoDEx; importance never was. Close it:
1. SEPARABILITY: is importance (downstream-reach on the real train graph) a real signal, non-redundant
   with schema-fit, recurrence, and degree/frequency (popularity)?
2. FOUNDATION-GROWTH: does ingesting high-importance facts FIRST build a foundation that answers held-out
   queries better/sooner (foundation-quality vs #facts) than frequency-order or random-order?
3. POPULARITY-NEUTRALITY: does importance-order beat a DEGREE-MATCHED ordering (its own degree
   trajectory, importance content scrambled within degree bin)?

## Operationalization (train-graph-only, label-free, test-free)
- IMPORTANCE (primary) = SAMPLED edge BETWEENNESS centrality on the undirected train graph. Justification:
  "how many other facts a fact unlocks" = how many shortest reasoning-paths between other entity pairs
  route THROUGH this edge = value-of-information (remove it -> those connections degrade). Classic
  DEGREE-DECORRELATED centrality (bridge between sparse regions is high-value at low degree) -> gives the
  popularity-neutrality question real teeth. Secondary (diagnostic) = k-hop endpoint reachable mass
  (arena-faithful transfer; hub-aligned).
- FOUNDATION-QUALITY = degree-ORTHOGONALIZED held-out answerability AUROC from the first-B-triples
  foundation (label-free degree projection fit on VALID, residualized, scored on TEST pos vs human-
  verified hard negatives). AUAC = mean quality over a fixed budget grid (emphasizes the low-budget
  prioritization regime). Metric SELECTED by the info-ceiling gate: the answerability score that passes
  info-ceiling is primary.

## Info-ceiling gate (FIRST, mandatory; a precondition for interpreting ANY arm)
- (a) full-graph orth AUROC >= CEIL_FULL_MIN = 0.55 (metric resolves truth at all).
- (b) full - degree-scramble null >= CEIL_STRUCT_MIN = 0.03 (structural, not popularity artifact).
- (c) growth regime resolvable: q(full) - q(smallest budget) >= CEIL_RANGE_MIN = 0.02.
- FAIL any -> VACUOUS_METRIC verdict; do not interpret arms.
- CALIBRATION FINDING (measured at self-test, documented transparently): the degree-orthogonalized 2-hop
  RA (common-neighbor) answerability is POPULARITY-VACUOUS on this data (full orth AUROC 0.489, struct
  vs scramble 0.012 -- fails the gate). RA's discriminative power is degree (raw 0.629, degree 0.665).
  The degree-orthogonalized SR/PPR resolvent (multi-hop path reachability) PASSES the gate (full orth
  0.738, struct 0.274) and IS the real popularity-neutral schema-fit-win signal. Per the info-ceiling
  discipline (interpret only a non-vacuous metric), the resolvent is PRIMARY; RA is a documented
  diagnostic. The a-priori BANDS below are unchanged by this metric selection.

## Pre-registered bands (FIXED a-priori)
Info-ceiling PASS is a precondition for all of the below.
- PART1 SEPARABLE: importance unique-variance (1 - R^2 vs [deg, rel_freq, schema_fit, recurrence]) >=
  0.50 AND max|spearman(imp, {deg, rel_freq})| <= 0.40. REDUNDANT if unique-var < 0.20 OR pop-corr > 0.75.
- PART2 BEATS_BOTH: bootstrap p05[AUAC(imp)-AUAC(freq)] > 0 AND p05[AUAC(imp)-AUAC(rand)] > 0.
  FAILS if p05[AUAC(imp)-AUAC(freq)] <= 0 (importance does NOT beat frequency-order).
- PART3 NEUTRAL: bootstrap p05[AUAC(imp)-AUAC(degree_matched)] > 0. NOT_NEUTRAL if <= 0.
- HARD_PASS = info-ceiling PASS AND PART1 SEPARABLE AND PART2 BEATS_BOTH AND PART3 NEUTRAL.
- HARD_FAIL = info-ceiling PASS AND (PART2 FAILS OR PART1 REDUNDANT OR PART3 NOT_NEUTRAL)
  = the 4th axis does NOT transfer to real data as a growth-prioritization signal (honest negative).
- MIDDLE = mixed. VACUOUS_METRIC = info-ceiling FAIL.

## Brain-check note (for a HARD_FAIL)
The brain's salience/value signal ARE real, so a real-data fail => the operationalization/USE is the
mismatch, not the concept. In the brain AND the arena, importance gates KEEP/CONSOLIDATE (selective
retention under capacity limits; one-shot salience bypass) -- it is NOT a coverage-curriculum ordering.
So a fail of "importance-FIRST-for-broad-answerability" is consistent with importance not being a
growth-ordering signal, and points to testing importance as a KEEP/DISCARD gate as the follow-up (a
HYPOTHESIS, not a rescue of this result).

## Cell-template compliance (single-shot local, no queue)
arms_differ (order-prefix comparison), atomic tmp+os.replace metrics, except SystemExit-first (no
BaseException), deterministic (np.random.default_rng fixed seeds, sorted, NO hash()-derived seeds),
crlb_n/a (rank-AUROC, no noise floor), baseline_in_band (info-ceiling verifies measurable), ASCII-only.
Self-test: auroc orientation, spearman monotone, betweenness bridge-dominates positive control,
degree_matched trajectory-exact permutation, info-ceiling precondition on real CoDEx full-N.
