# PRE-REG: curriculum_order_ingest_real_codex_v1

Filed 2026-07-16 BEFORE running. Bands fixed a-priori. ASCII-only.

## Question
Does ingesting REAL CoDEx-S facts (structured triples) in a CURRICULUM order (foundational /
already-anchored facts first) through a single-pass schema-fit ingest-gate produce a BETTER foundation
than RANDOM order or FREQUENCY (popularity) order? "Better foundation" = a held-out, non-circular,
popularity-neutral quality metric. This is the REAL-DATA transfer test of the synthetic
`curriculum_order_ingest_schema_fit_v1` HARD_PASS ("order matters; curriculum rescues schema-fit") and
the `provisional_hold_bootstrap_arbitrary_order_v1` HARD_PASS ("hold recovers arbitrary order").

## Port of the synthetic mechanism to real triples
- SYNTHETIC prerequisite DAG -> REAL train-graph connectivity. A triple's "prerequisites" = its
  endpoints being already GROUNDED (anchored) in the current foundation.
- FOUNDATION = the growing subgraph of ADMITTED train triples + the set of grounded entities.
- INNATE ANCHOR SEED S = entities of a FIXED small random sample of train triples (default 8 triples).
  SHARED across all arms -> seed identity cancels in every arm-relative margin (fair by construction).
- schema_fit(h,r,t | foundation) = (anchored(h) + anchored(t)) / 2 in {0, 0.5, 1.0}; anchored(e) iff
  e in S OR admit_count[e] >= K_ground (default K_ground=1). This is the real analog of the synthetic
  "fraction of refs present".
- FIXED gate (anti-rig, identical across ALL arms + regimes): admit iff schema_fit >= tau (tau=0.5 ->
  at least one endpoint already anchored). SINGLE-PASS: a triple arriving before either endpoint is
  anchored is dropped forever -> that is exactly why ORDER matters. On admit: both endpoints ground.

## Arms (all share the SAME gate, tau, K_ground, seed S, and per-seed randomness)
1. CURRICULUM   : BFS-frontier admission order from S (present each triple as soon as it is anchorable).
2. RANDOM       : shuffled arrival, single-pass strict gate (baseline floor; averaged over RAND_SEEDS).
3. FREQUENCY    : triples ordered by descending relation-frequency then descending endpoint-degree
                  (a pure POPULARITY ordering; the popularity-neutrality control arm).
4. RANDOM_HOLD  : random arrival + PROVISIONAL-HOLD (rejected -> hold buffer; re-sweep to fixpoint).
                  Tests whether bootstrapping rescues arbitrary order on REAL data.
5. REVERSE      : reverse of curriculum order (deep/advanced first). DISCRIMINATOR / positive control
                  that a BAD order defeats the single-pass gate.

## Downstream foundation-quality metric (held-out, non-circular, popularity-neutral)
Q(arm) = held-out CoDEx-S claim-validity AUROC of the DEGREE-ORTHOGONALIZED pairwise Resource-Allocation
(RA) schema-fit index computed FROM THE ADMITTED FOUNDATION SUBGRAPH ONLY, scored on test positives vs
human-verified hard negatives (Safavi & Koutra 2020). RA(h,t)=sum_{z in N_found(h) cap N_found(t)}
1/deg_found(z). Degree-orthogonalization = the VALIDATED popularity-neutral recipe (from
exp_codex_claimvalidity_degree_orthogonal_schemafit_v2): fit a LABEL-FREE OLS projection
RA ~ [1, log deg_found(h), log deg_found(t)] on the VALID pos+neg rows (held-out, labels never used),
residualize, score TEST. A pair with an endpoint absent from the foundation -> RA 0 (a sparser
foundation structurally resolves fewer held-out claims -> the mechanism by which a better foundation
helps).
- NON-CIRCULAR: ingestion ORDER uses only train-graph structure + relation frequency; NO test labels.
  Foundation built from TRAIN only. Degree projection fit on VALID (label-free). Test labels touched
  ONLY in the final AUROC. Leakage guard asserts no test positive appears in the train graph.
- POPULARITY-NEUTRAL stack: (a) margin_over_degree per arm = orth_RA_AUROC - best-single-degree-feature
  AUROC; (b) the FREQUENCY arm itself is the popularity ordering -> curriculum must beat it; (c) SCRAMBLE
  null (degree-preserving rewire of curriculum's foundation) must collapse orth_RA_AUROC to chance ->
  the metric is structural, not a size/degree artifact.

## Size confound control -- BUDGET SWEEP (central)
Curriculum admits ~the whole reachable component; random admits nearly as much on DENSE real data (a
permissive single-pass gate snowballs), so a single min-admit "matched B" is ~the full graph and leaves
no room for an order effect. Instead the PRIMARY quality margins are swept over a FIXED a-priori BUDGET
grid B in {1000,2000,4000,8000,16000,24000, and the min-admit cap}, capped so every swept arm has >= B
admitted triples. At each B, each arm's admission-ordered foundation is truncated to its first B
(curriculum first-B = coherent BFS core; random first-B = scattered subset) and scored. This isolates
WHICH triples (coherent core) from HOW MANY. Full-size Q reported for hold-recovery. Admission /
premature-rejection reported as SECONDARY (near-by-construction) metrics.

## Null guards + info-ceiling
- tau=0 (gate OFF): every order admits the identical full train graph -> Q identical across orders
  (spread ~0). Confirms order-dependence is GATE-driven, not a harness order bug.
- SCRAMBLE: curriculum foundation rewired degree-preservingly -> orth_RA_AUROC <= 0.55 (structural).
- INFO-CEILING: info_ceiling = Q_cur_full - scramble_auroc. If < 0.03 the popularity-neutral metric is
  near-vacuous (the best real foundation barely beats its own degree-scramble) -> the test CANNOT
  distinguish "order-invariant" from "metric too weak to tell"; verdict MUST be MIDDLE (info-ceiling),
  NOT a HARD_FAIL order-invariance claim. (Anti over-claim guard.)

## Pre-registered bands (FIXED a-priori)
Let margin_cur_rand = mean over the budget grid of (orth_Q_cur@B - mean_seed orth_Q_rand@B);
margin_cur_freq = mean over grid of (orth_Q_cur@B - orth_Q_freq@B); robust_cur_rand = margin >= HP at a
MAJORITY of budgets (not cherry-picked).

HARD_PASS (ALL must hold):
- margin_cur_rand (mean over grid)                 >= +0.030  AND robust (majority of budgets)
- margin_cur_freq (mean over grid)                 >= +0.010   (beats popularity ordering; pop-neutral)
- curriculum margin_over_degree (mean over grid)   >= +0.020   (structure beats degree baseline)
- scramble_auroc                                   <= 0.55     (null: metric is structural)
- tau0_order_invariant                             == True
- DISCRIMINATOR fires: REVERSE craters -- reverse premature_rejection >= 0.30 AND reverse admits
  < 0.5 * curriculum admit (bad order defeats the single-pass gate)
- info_ceiling                                     >= 0.03     (metric NOT near-vacuous)

HARD_FAIL (ANY):
- margin_cur_rand (mean over grid) <= +0.005 AND info_ceiling >= 0.03  (a TRUSTWORTHY informative
  negative: order does NOT affect per-triple foundation quality -- pure efficiency, no quality prize), OR
- scramble_auroc >  0.60    (metric is a size/degree artifact -> quality measure untrustworthy), OR
- tau0 NOT order-invariant  (harness order bug).

MIDDLE (otherwise), including:
- MIDDLE_METRIC_NEAR_VACUOUS: info_ceiling < 0.03 (metric too weak to resolve the order Q -- order
  question UNRESOLVED, NOT disproven); the honest outcome when the popularity-neutral signal is near-chance
  on partial foundations, OR
- effect real but non-robust (margin in (0.005, 0.030) or positive only at some budgets).

## Discriminator-fires (smoke gate, MANDATORY before trusting FULL)
The reverse-craters discriminator is a FULL-DENSITY property (a subsampled smoke graph is too sparse for
reverse order to strand recoverable facts), so the self-test exercises the discriminator at FULL-N
(smoke-at-full-N; FULL runs in ~seconds) with a reduced 2-seed random set: REVERSE premature_rejection
>= 0.30 AND reverse admits < 0.5*curriculum AND curriculum admits more than random (arms differ) AND
tau0 order-invariant AND scramble collapses (<=0.60). If reverse does not crater there is no order
sensitivity to test -> BLOCK.

## Compute architecture
- Class (b) SEQUENTIAL-CPU with justification: directional gate on a small graph (n_ent=2034, ~33k
  train triples). Ingestion = single pass over triples; RA index = common-neighbor counting
  (O(sum deg^2)); no matmul-heavy batchable primitive; no GPU speedup relevant; wall time seconds to a
  few minutes. Proportional method for a directional/correlation question (NOT a KGE/SGD training fit).
- Storage: no_composition (subgraph edge lists + neighbor sets; no bundled/sharded HD vectors).
- LOCAL single-shot run-to-completion (NOT a queue dispatch) -> runner start_marker / heartbeat gates
  N/A. Cell-template still honored: atomic tmp+os.replace metrics write, no bare except, SystemExit-first
  ordering, arms-differ hash check, deterministic seeding (np.random.default_rng only; no hash()-seeded
  RNG; sorted() for set ops).
- crlb_n/a: metric is a rank-AUROC over a parameter-free structural score; no noise-floor threshold.
- baseline_in_band: freq/degree baselines land in a measurable AUROC band by construction; RA in band.
- deterministic_seeding: true (fixed integer seeds; default_rng; sorted selection; no hash()-derived RNG).

## Scale
- SELF-TEST (smoke gate): runs the discriminator + nulls at FULL-N graph with RAND_SEEDS=[11,23] (2)
  in ~3s (the reverse-craters discriminator needs full density). Verifies discriminator + tau0 + scramble
  + arms-differ + hold-bounded before trusting FULL.
- `--smoke` run mode: train subsampled to 6000 triples (fast iteration only; too sparse for the discriminator).
- FULL: all 32888 CoDEx-S train triples, RAND_SEEDS=[11,23,37,41,53] (5). Runs to completion locally in
  ~6s -> report the actual verdict with numbers.
- OPTIONAL scale-up: --dataset codex_m (CoDEx-M) if the S-result is decisive and a larger check is wanted
  (heavier; may route to remote_cpu_queue). Headline stays CoDEx-S.
