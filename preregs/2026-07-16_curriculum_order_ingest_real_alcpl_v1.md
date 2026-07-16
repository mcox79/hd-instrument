# PRE-REG: curriculum_order_ingest_real_alcpl_v1

Filed 2026-07-16 BEFORE running the FULL verdict. Bands fixed a-priori (reused verbatim from the CoDEx
sibling prereg `2026-07-16_curriculum_order_ingest_real_codex_v1.md` except the two documented,
mechanistically-justified metric/discriminator calibrations in the "Deviations" section). ASCII-only.

## Question
Does ingesting REAL concept-PREREQUISITE facts in a CURRICULUM order (prerequisites first) through a
single-pass schema-fit ingest-gate build a BETTER foundation than RANDOM order or FREQUENCY (popularity)
order, on a corpus that ACTUALLY has prerequisite structure? This is the FAIR re-test of the synthetic
`curriculum_order_ingest_schema_fit_v1` HARD_PASS after the CoDEx real-data test landed
MIDDLE_BAND_METRIC_NEAR_VACUOUS -- the brain-check (`notes/research_curriculum_order_corpus_mismatch_brain_check_2026-07-16.md`)
attributed the CoDEx null to CORPUS-MISMATCH: CoDEx is a flat dense web (11-16x tree density, 0.18-0.26%
hierarchical edges) where Knowledge-Space-Theory predicts order is VACUOUS. AL-CPL is a genuine, author-
validated strict partial-order concept-prerequisite DAG (100% prerequisite-typed edges). If the principle
transfers to real data where structure EXISTS, curriculum should now BEAT random/frequency.

## Corpus: AL-CPL (github.com/harrylclc/AL-CPL-dataset, CC BY-NC-SA, research use; local, not redistributed)
- Data Mining domain (pilot; highest expected effect per the brain-check density-vs-tree ranking).
- `data_mining.preqs` (292 lines) = POSITIVE prerequisite pairs. Line `u,v` means "v is a prerequisite
  of u" -> DIRECTED edge v->u (prereq -> dependent). Confirmed strict partial order (irreflexive +
  transitive; author-validated). On-disk verified this session: 90 nodes in positive DAG, topo-sortable
  (NO cycle), 24 roots (in-degree 0), max longest-path depth 6.
- `data_mining.pairs` (826 lines) = ALL labeled candidate pairs = 292 positives + 534 negatives. The
  negatives INCLUDE the reversed pair of every positive (the dataset adds (B,A) as a negative when (A,B)
  is positive -- irreflexive/antisymmetric). Verified: 292/292 positives have their reversed hard-negative
  present -> a BUILT-IN popularity-neutral hard-negative set (a reversed pair has IDENTICAL endpoint
  degrees; only DIRECTION separates it from the positive).
- 120 total concepts (90 in the positive DAG; 30 appear only in negative candidate pairs).

## Port of the synthetic mechanism to AL-CPL directed prerequisite edges
- FOUNDATION = growing set of ADMITTED prerequisite edges + set of grounded concepts.
- INNATE ANCHOR SEED S = the ROOTS (in-degree-0 concepts) of the TRAIN prerequisite DAG. These are the
  genuinely foundational concepts with no prerequisites. SHARED identically across ALL arms -> seed
  identity cancels in every arm-relative margin (fair by construction). Uses TRAIN structure only, NO
  test/label info (leak guard).
- DIRECTIONAL schema_fit(edge prereq p -> dependent d) = anchored(p) in {0, 1}: the PREREQUISITE concept
  p must already be grounded before "d depends on p" can be properly ingested. This is the faithful port
  of the synthetic "fraction of refs present" to a genuine directed prerequisite ("must be anchored
  first" literally = the edge semantics). anchored(e) iff e in S OR (# times e admitted as a DEPENDENT)
  >= K_ground (default K_ground=1).
- FIXED gate (anti-rig, identical across ALL arms + regimes): admit iff schema_fit >= tau (tau=0.5 ->
  prereq anchored). SINGLE-PASS: an edge whose prereq is not yet grounded is dropped forever -> ORDER
  matters. On admit: the dependent d grounds.

## Arms (all share the SAME gate, tau, K_ground, seed S, per-seed randomness)
1. CURRICULUM   : topological-order admission (prereqs first) of the TRAIN DAG from S.
2. RANDOM       : shuffled arrival, single-pass strict gate (baseline floor; mean over RAND_SEEDS).
3. FREQUENCY    : edges by descending (prereq out-degree + dependent in-degree) (POPULARITY ordering;
                  popularity-neutrality control arm).
4. RANDOM_HOLD  : random arrival + PROVISIONAL-HOLD (rejected -> hold buffer; re-sweep to fixpoint).
5. REVERSE      : reverse of curriculum (advanced/dependent first). DISCRIMINATOR / positive control that
                  a BAD order strands prerequisites and defeats the single-pass gate.

## Non-circular train/test split + downstream foundation-quality metric
- Deterministic 30% hold-out of the 292 positive edges (np.random.default_rng(2024); sorted index set)
  -> TRAIN positives build the foundation; TEST positives are scored, NEVER admitted (leak guard asserts
  no test edge in the admitted foundation; foundation contains positive TRAIN edges only, so negatives
  and test positives are never in it).
- Q(arm) = held-out AUROC of a DEGREE-ORTHOGONALIZED directed KATZ proximity index computed FROM THE
  ADMITTED FOUNDATION SUBGRAPH ONLY, scoring TEST positives vs negatives. Katz(x,y) = sum_{k=1..L}
  beta^k (A^k)[x,y] over the directed foundation adjacency A (A[p,d]=1 for admitted prereq edge p->d),
  beta=0.5, L=6 (>= graph depth). Score candidate directed edge (p,d) = Katz[p,d] (does the foundation
  place p transitively upstream of d). Degree-orthogonalization (label-free, VALIDATED CoDEx recipe): fit
  OLS Katz ~ [1, log outdeg_found(p), log indeg_found(d)] over ALL candidate pairs (NO labels),
  residualize, then AUROC on the residual with labels. Test labels touched ONLY in the final AUROC.
- TWO negative sets reported: (all) TEST positives vs ALL 534 negatives (primary margin, matches CoDEx's
  all-hard-neg protocol); (rev) TEST positives vs their REVERSED hard-negatives (popularity-neutral
  corroboration: identical endpoint degrees, only direction differs).
- POPULARITY-NEUTRAL stack: (a) degree-orthogonalization; (b) the FREQUENCY arm is the popularity
  ordering -> curriculum must beat it; (c) the reversed-hard-neg AUROC (degree-controlled); (d) SCRAMBLE
  null (degree-preserving directed rewire of curriculum's foundation) must collapse orth-Katz-AUROC.

## Size confound control -- BUDGET SWEEP
Curriculum admits ~the whole reachable DAG; random admits less. PRIMARY quality margins are swept over a
FIXED a-priori BUDGET grid B in {40, 80, 120, and the min-admit cap across cur/freq/rand}, capped so
every swept arm has >= B admitted edges. At each B, each arm's admission-ordered foundation is truncated
to its first B (curriculum first-B = coherent upstream topological core; random first-B = scattered) and
scored. Isolates WHICH edges (coherent core) from HOW MANY. Full-size Q reported for hold-recovery +
reporting. Admission / premature-rejection reported as SECONDARY (near-by-construction) metrics.

## Null guards + info-ceiling (MANDATORY, checked FIRST)
- INFO-CEILING (load-bearing, checked before interpreting arm margins): info_ceiling = Q_cur_full_orth -
  scramble_orth. If < 0.03 the metric is near-vacuous (the best real foundation barely beats its own
  degree-scramble) -> the test CANNOT distinguish "order-invariant" from "metric too weak" -> verdict MUST
  be MIDDLE (info-ceiling), NOT a HARD_FAIL order-invariance claim. (Anti over-claim guard. Same gate that
  fired MIDDLE on CoDEx.)
- SCRAMBLE: curriculum foundation rewired degree-preservingly -> orth-Katz-AUROC <= 0.55 (structural).
- tau=0 (gate OFF): every order admits the identical full TRAIN graph -> Q identical across orders
  (spread ~0). Confirms order-dependence is GATE-driven, not a harness order bug.

## Pre-registered bands (FIXED a-priori)
Let margin_cur_rand = mean over the budget grid of (orth_Q_cur@B - mean_seed orth_Q_rand@B);
margin_cur_freq = mean over grid of (orth_Q_cur@B - orth_Q_freq@B); robust_cur_rand = margin >= HP at a
MAJORITY of budgets.

HARD_PASS (ALL must hold):
- margin_cur_rand (mean over grid)                 >= +0.030  AND robust (majority of budgets)
- margin_cur_freq (mean over grid)                 >= +0.010   (beats popularity ordering; pop-neutral)
- curriculum margin_over_degree (mean over grid)   >= +0.020   (structure beats best single-degree feature)
- scramble_orth_auroc                              <= 0.55     (null: metric is structural)
- tau0_order_invariant                             == True
- DISCRIMINATOR fires (see Deviations): REVERSE foundation quality craters to chance
  (orth_Q_rev_full <= 0.55) AND reverse premature_rejection_rate >= 0.30
- info_ceiling                                     >= 0.03     (metric NOT near-vacuous)

HARD_FAIL (ANY):
- margin_cur_rand (mean over grid) <= +0.005 AND info_ceiling >= 0.03  (a TRUSTWORTHY informative
  negative: order does NOT affect per-edge foundation quality even on a genuine DAG with a live metric ->
  the order principle does NOT transfer to real data), OR
- scramble_orth_auroc > 0.60  (metric is a size/degree artifact -> quality measure untrustworthy), OR
- tau0 NOT order-invariant  (harness order bug).

MIDDLE (otherwise), including:
- MIDDLE_METRIC_NEAR_VACUOUS: info_ceiling < 0.03 (metric too weak to resolve the order Q on this corpus
  too -- would relocate the bottleneck to metric-design, NOT corpus-selection), OR
- effect real but non-robust (margin in (0.005, 0.030) or positive only at some budgets), OR
- DISCRIMINATOR did not fire (reverse did not crater).

## Deviations from the CoDEx sibling prereg (documented; mechanistically justified, NOT tuned-to-pass)
1. METRIC: Resource-Allocation (common-neighbor) -> directed KATZ transitive-proximity. RA counts shared
   neighbors, which is near-vacuous on a sparse directed prerequisite DAG (few common neighbors); Katz
   sums decayed directed paths and captures the transitive-closure signal that IS a prerequisite DAG's
   structure. Verified this session (on-disk pre-flight, NOT the FULL verdict): orth-Katz info_ceiling =
   0.301 (raw 0.149) -> non-vacuous headroom, the exact contrast with CoDEx's near-vacuous 0.011.
2. DISCRIMINATOR: CoDEx used "reverse admits < 0.5 * curriculum". AL-CPL's DAG is shallow (depth 6) so
   reverse still admits ~57% by count, but reverse builds a CHANCE-quality foundation. The mechanistically
   correct order-sensitivity signature on a shallow DAG is QUALITY-craters (orth_Q_rev collapses to chance
   <= 0.55) with elevated premature-rejection (>= 0.30), not admit-halving. Pre-flight: orth_Q_rev = 0.500
   (chance), reverse premature = 0.420 -> discriminator fires.
All numeric margin/scramble/info-ceiling bands are UNCHANGED from CoDEx (0.030 / 0.010 / 0.020 / 0.55 /
0.60 / 0.03). Pre-flight numbers above are validity-gate measurements (headroom + discriminator-fires),
not the HARD_PASS margins, which are computed only in the committed FULL run.

## Compute architecture
- Class (b) SEQUENTIAL-CPU with justification: directional gate on a tiny graph (120 concepts, ~205 train
  edges). Katz = truncated matrix powers at N=120 (~10M FLOPs each), microseconds; no GPU speedup; total
  wall time seconds. Proportional method for a directional/correlation question (NOT a KGE/SGD fit).
- Storage: no_composition (edge lists + adjacency; no bundled/sharded HD vectors).
- LOCAL single-shot run-to-completion (NOT a queue dispatch) -> runner start_marker / heartbeat gates N/A.
  Cell-template honored: atomic tmp+os.replace metrics write, no bare except, SystemExit-first ordering,
  arms-differ hash check, deterministic seeding (np.random.default_rng only; no hash()-seeded RNG; sorted()
  for set ops).
- crlb_n/a: metric is a rank-AUROC over a parameter-free structural score; no noise-floor threshold.
- baseline_in_band: freq/degree baselines land in a measurable AUROC band; curriculum orth-Katz in band.
- deterministic_seeding: true (fixed integer seeds; default_rng; sorted selection; no hash()-derived RNG).

## Scale
- SELF-TEST (smoke gate): runs the FULL Data Mining graph (not a subsample -- the graph IS small) with a
  reduced 2-seed random set; verifies discriminator-fires (reverse craters to chance + premature),
  info-ceiling non-vacuous, tau0 order-invariant, scramble collapses, arms-differ, hold-bounded, in ~1s.
- FULL: all 292 positives (70/30 split), RAND_SEEDS=[11,23,37,41,53] (5). Runs to completion locally in
  ~seconds -> report the actual verdict with numbers.
- SWEEP (conditional): if Data Mining is decisive, re-run --domain {geometry, physics, precalculus} for
  the density-vs-effect-size robustness check the brain-check note predicts (Data Mining flattest-to-tree
  = strongest; Geometry densest = weakest).
