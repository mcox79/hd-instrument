# Pre-registration: ANCHOR_COMPOSE MAGNITUDE-OPTIMIZATION (two orthogonal levers, 2x2 attribution)

- **Cell:** `experiments/exp_anchor_compose_magnitude_opt_cskg_v1.py`
- **Shared-fit edit:** `experiments/_kge_anchor1_fit.py` (added `hard_neg_frac` kwarg; DEFAULT 0.0 == bit-identical to
  the confirmed uniform fit -> v1/v2/ladder reproducibility preserved).
- **Anchor:** `anchor_compose_magnitude_opt_cskg_v1`
- **Queue / device:** `overnight_queue` (GPU; batched matmul fits) | device=auto (cuda on host) | 2 seeds [7,13] |
  per-fit checkpoint (ckpt_every=20) -> outage/timeout resumable.
- **Strategic frame:** OPTIMIZE-THEN-NATIVIZE (USER). Find the best-performing generalization STRUCTURE by cleanly
  attributing per-lever lift; the optimized structure is then what the substrate is required to realize natively.

## Prior-work check (substrate-KB concept-query, mandatory pre-authoring)
`bash tools/substrate_query.sh "sequential peel SIC iterative bundle decode inductive entity anchor compose
hard-negative scorer"` -> top hits are CHAR-TRIGRAM LEXICAL NOISE only ('decorative' 0.371, 'inductive' 0.338,
'negative' 0.323); NO arc-cell semantic memory at cosine>0.30 (substrate has no ingested arc knowledge). This cell
is genuinely NOVEL, not a rediscovery.

## Mechanism under test
The VET-confirmed ANCHOR_COMPOSE inductive entity-generalizer represents a held-out entity's code as a FLAT
UNWEIGHTED additive mean over support-edge tail estimates `E_derived[t] = mean_i (X[h_i] + D[r_i])`. Baseline:
filtered-MRR 0.1282 (MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.
ANCHOR_COMPOSE). Two orthogonal levers, run as a 2x2 factorial {composer} x {scorer-fit}:
- **LEVER A (composer): SIC-PEEL SEQUENTIAL CONSENSUS DECODE.** Round 0 = the flat mean; each round re-weights each
  support-edge estimate by cosine agreement with the running per-tail consensus (segment-softmax, tau) and re-forms
  the consensus -> outlier/low-agreement support edges are peeled DOWN. Reduces EXACTLY to the flat mean at round 0 /
  tau->inf. Zero-training, deterministic, batched (index_add segment ops). Brain: theta-gamma sequential slotting +
  predictive-coding precision-weighting (CITED@notes/research_inductive_map_builder_best_in_class_magnitude_levers_
  2026-07-13.md Lever 1). Field: SIC/resonator sequential decode recovers ~8x more components vs flat readout
  (CITED@arXiv:2412.00354). This is the substrate's peel_sic_readout family RECAST as a consensus composer over a set
  of NOISY ESTIMATES OF ONE TARGET (NOT the index-decode contract of peel_sic_readout -- the authorized "equivalent
  sequential composer").
- **LEVER B (scorer-fit): IN-BATCH HARD NEGATIVES.** The shared additive scorer (X,D) is currently self-adversarial-
  weighted over UNIFORM-RANDOM negatives. Lever B refits X,D with a fraction (HARD_NEG_FRAC=0.5) of negatives drawn
  as real tails of other positives in the minibatch (structurally-plausible confusors). The held-out entity STILL
  receives zero gradient steps -> the "zero-training for new entities" property is preserved. Field: KGE hard-neg /
  self-adversarial +0.01-0.04 MRR (CITED@arXiv:1902.10197, 2202.09606; research note Lever 2, P_deflated 0.45).

## INFO-CEILING (load-bearing pre-reg insight; compute-test-ceiling-before-iterating discipline)
The MEASURED v1 transductive oracle (ORACLE_ADDITIVE, best-possible IN-arena code under the uniform scorer) is MRR
0.1373 (MEASURED@...v1/metrics.json:gates.heldout_mrr.ORACLE_ADDITIVE). The flat-mean baseline 0.1282 is ALREADY
**93% of that ceiling**. Therefore the COMPOSER lever (A, uniform fit) has only ~+0.009 absolute headroom against its
own oracle -- the research note's +0.02 ABSOLUTE HARD-PASS band is INFEASIBLE for Lever A in isolation (that band
computed headroom above RANDOM=0.137, NOT above ANCHOR=0.009). The SCORER lever (B) is the one with real headroom
because it LIFTS the ceiling itself. CONSEQUENCE (baked into the bands): Lever A is judged CEILING-RELATIVE against
its uniform-fit oracle; Lever B against its OWN hardneg-fit oracle (ORACLE_HARDNEG, measured in-run); the combined
arm's absolute MRR is reported vs the SOTA band. This is a genuine, pre-registered structural finding: on CSKG the
flat mean is near-ceiling for the current scorer, so the SCORER is the bottleneck, not the composer -- the 2x2
measures exactly that. (Self-test corroborates the mechanism: ORACLE_HARDNEG 0.316 > ORACLE_ADDITIVE 0.275 on the
planted arena -> the hardneg fit genuinely raises the wall. MEASURED@data/exp_anchor_compose_magnitude_opt_cskg_v1_
selftest/metrics.json:mechanism_selftest.heldout_mrr.)

## Arms (12; all scored PAIRED on the SAME held-out QUERY edges + candidate pool; SHARDED per-entity codes)
| Arm | Composer | Fit | Role |
|---|---|---|---|
| ANCHOR_COMPOSE | FLAT | UNIFORM | CONFIRMED v1 baseline (Gate-D reproduce 0.128) |
| ANCHOR_PEEL | SIC-PEEL | UNIFORM | Lever A isolated |
| ANCHOR_HARDNEG | FLAT | HARDNEG | Lever B isolated |
| ANCHOR_PEEL_HARDNEG | SIC-PEEL | HARDNEG | combined |
| ADDITIVE_TRANSE | (random-init held code) | UNIFORM | memorize control |
| RANDOM_CODES | random X,D | - | null |
| ANCHOR_SCRAMBLE | FLAT, relations scrambled | UNIFORM | must-fail (relation signal) |
| ANCHOR_PEEL_SCRAMBLE | SIC-PEEL, relations scrambled | UNIFORM | must-fail for the NEW composer |
| IDENTITY_SHUFFLE | cross-entity donated code | UNIFORM | must-fail (entity-specific) |
| ORACLE_ADDITIVE | held-out folded-in (learned) | UNIFORM | Lever-A ceiling / positive control (v1 0.137) |
| ORACLE_HARDNEG | held-out folded-in (learned) | HARDNEG | Lever-B lifted ceiling |
| BASELINE_POP | frequency incumbent | - | fit-independence sanity (~floor) |

## PRE-REG BANDS (picked BEFORE the FULL run; primary metric = FILTERED MRR rank-vs-ALL, degree-unbiased)
Notation: `b` = measured ANCHOR_COMPOSE baseline in-run; `C_uni` = ORACLE_ADDITIVE; `C_hn` = ORACLE_HARDNEG.
All numbers HYPOTHESIZED@this prereg unless tagged MEASURED@/CITED@.

- **GATE-D REPRODUCE** (must hold or the run is untrustworthy): `|b - 0.1282| <= 0.02` (baseline reproduces the
  confirmed v1 MEASURED@...v1 at the matched regime k=24/ep=500/k_core=12/support_frac=0.5). Else verdict
  `INCONCLUSIVE_BASELINE_DID_NOT_REPRODUCE_v1`.
- **ORACLE-FIRES** (arena answerable): `C_uni >= 3x RANDOM AND C_uni - RANDOM >= 0.003`.
- **LEVER A (PEEL, uniform fit; ceiling-relative):** headroom_A = C_uni - b.
  - HARD-PASS: `(PEEL - b) >= max(0.50*headroom_A, 0.002)` AND all must-fails intact.
  - HARD-FAIL: `(PEEL - b) < 0.20*headroom_A`.
  - MIDDLE otherwise -> degree-stratify (SIC lit predicts lift concentrates at HIGHER support degree).
  - ALSO reported: absolute lift vs the research +0.02/+0.005 band WITH the INFEASIBILITY flag (headroom_A ~0.009).
- **LEVER B (HARDNEG, hardneg fit; the real-headroom lever):**
  - HARD-PASS: `(HARDNEG - b) >= 0.02` absolute (research band; feasible iff `C_hn - C_uni` lifts the ceiling --
    reported).  HARD-FAIL: `(HARDNEG - b) < 0.005`.  MIDDLE otherwise -> stratify by query-frequency tertile.
- **COMBINED (PEEL_HARDNEG; ceiling C_hn):** HARD-PASS: `(PEEL_HARDNEG - b) >= 0.03` AND `>= max(PEEL-b, HARDNEG-b)`.
  Report absolute MRR of the best mechanism arm vs the InductivE/ConceptNet SOTA band 0.18-0.22
  (CITED@research note Part A).
- **MUST-FAILS (all required):** ORACLE fires; `(SCRAMBLE-RANDOM) <= 0.25*(ANCHOR-RANDOM)`;
  `(PEEL_SCRAMBLE-RANDOM) <= 0.25*(PEEL-RANDOM)`; IDENTITY_SHUFFLE retains `<= 0.20` of ANCHOR's margin-over-RANDOM;
  no control beats POP by the ceiling-relative broken margin; arms differ (>=8 distinct sigs of 12).
- **Load-bearing stratifier (per VET):** per-support-degree per-arm MRR + per-degree LIFT of PEEL/HARDNEG/PEELHN over
  ANCHOR reported in `gates.per_support_degree_lift`.

## Four validity-preflight checks (declared; run in the self-test via experiments._validity_preflight)
1. positive_control_passes: ORACLE_ADDITIVE recovers planted held-out tails + clears RANDOM by the fire gate.
2. metric_moves: MRR MOVES across [RANDOM, ADDITIVE, ANCHOR(flat), ANCHOR_PEEL, ORACLE].
3. negative_control_margin: RANDOM + ANCHOR_SCRAMBLE + PEEL_SCRAMBLE + IDENTITY_SHUFFLE below the PEEL arm, det >=2.
4. full_gates_exercised: aggregate_and_verdict runs on the planted per-seed, firing every fail-closed gate (Gate-D
   correctly fires INCONCLUSIVE on the non-CSKG synthetic arena).

## Adversarial self-test discriminator (Lever A fires) -- MEASURED
On a PLANTED arena with INJECTED OUTLIER support edges (`build_planted_transe_arena outlier_per_node=3`, moderately-
trained fit ep=200 so clean estimates are not razor-tight), SIC-PEEL recovers held-out tails GENUINELY BETTER than
the flat mean. MEASURED@data/exp_anchor_compose_magnitude_opt_cskg_v1_selftest/metrics.json:
- ANCHOR (flat) MRR = 0.2055 ; ANCHOR_PEEL MRR = 0.2310 -> **peel_margin = +0.0255 >= 0.02 gate (FIRES)**.
- peelscr_margin (PEEL - PEEL_SCRAMBLE) = +0.106 ; scramble_margin (ANCHOR - SCRAMBLE) = +0.075 (relational).
- ORACLE_ADDITIVE 0.275, ORACLE_HARDNEG 0.316 (hardneg lifts the ceiling); IDENTITY_SHUFFLE collapse_ratio 0.285.
- 12/12 distinct arm sigs ; 4/4 validity-preflight checks pass ; verdict SELFTEST_PASS.
Lever B's win is a data-scale training effect (analytical justification per DISCRIMINATOR-SURVIVES-SCALE option B;
the self-test only asserts the hardneg fit RUNS + yields a distinct valid arm; the FULL measures its lift on CSKG).

## Compute architecture
class (b/c) MIXED. 4 additive fits per seed (uniform, hardneg, uniform-oracle, hardneg-oracle) = minibatch SGD,
self-adversarial, neg-chunked (neg_chunk=16) on FULL, run SEQUENTIALLY with torch.cuda.empty_cache between them ->
PEAK memory == a SINGLE fit's footprint == the proven v1/v2 profile at k=24/n_neg=128 (OOM-safe by construction; no
new peak vs the landed v1/v2 runs on this GPU). FLAT/SIC-PEEL compose = vectorized index_add segment ops (seconds,
no Python loop over entities). Readouts = query-chunked batched matmul. Storage SHARDED. Per-fit checkpoint
(ckpt_every=20) makes any outage/timeout resumable.

## Cell-template mandatory items (self-verified)
- arms_differ_verified: 12 arms -> 12 distinct sigs at self-test (>=8 gate). final_metrics_atomicity: tmp_replace.
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except; grep gate CLEAN).
- info-ceiling: per-fit oracle IS the measured ceiling; Lever-A bands ceiling-relative, Lever-B vs its own oracle.
- baseline_in_band: Gate-D reproduce (0.128 +/- 0.02); ORACLE fires; RANDOM/POP near 1/N floor.
- discriminator survives scale: Lever A fires on the planted-outlier arena; the ceiling-relative CSKG band
  self-scales; Lever B analytical (B) + memsmoke memory profile == v1/v2 proven.
- HP strictly above floor: Lever-A HP 0.50*headroom clears HF 0.20*headroom by 30% of headroom + MIN_SIG 0.002;
  Lever-B HP 0.02 clears HF 0.005 by 0.015.
- HP_SCOPE: Lever-A gates -> ANCHOR_PEEL; Lever-B -> ANCHOR_HARDNEG; combined -> ANCHOR_PEEL_HARDNEG; ORACLE_* =
  positive controls; RANDOM/SCRAMBLE/PEEL_SCRAMBLE/IDENTITY_SHUFFLE = must-not-clear-bar; POP = fit-independence.
- cardinality: EXPECTED_N_UNITS = 2 seeds; each seed asserted 12 arms + >=8 sigs (HARD_FAIL_CARDINALITY else).
- per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
- calibration_check: adaptive_with_discriminator_gate -- PEEL_ROUNDS=6/PEEL_TAU=0.5/HARD_NEG_FRAC=0.5 + all band
  fractions pre-registered, NOT tuned on real data; lever bands are FRACTIONS OF THE MEASURED per-fit oracle.
- start_marker_written / crash_diagnostic_present / heartbeat_present: yes (_start_marker.json, _write_crash_metrics,
  _heartbeat.jsonl). cell_chunked: n/a (2-seed in-process with per-fit checkpoint; each fit resumable).
- progress_logging: print_flush_true (line_buffering + per-seed/per-arm flush prints; FULL wall > 1800s).
- RUN_MODE verification post-dispatch: expect run_mode=full, size >5KB, elapsed >1s (per-arm/per-seed data written).

## Timeout justification
per-fit-seed ~1342s (MEASURED@v1: 12073s / (3 fits x 3 seeds)). This cell = 4 fits x 2 seeds = 8 fit-units ~ 10700s +
11-arm scoring + 9-arm localization overhead ~ 12500s estimate. Timeout = 18000s (~1.44x margin over cap 14400,
JUSTIFIED: inherently 8 fit-units; per-fit checkpoint ckpt_every=20 makes any timeout/outage resumable so no work is
lost even if the wall is exceeded).
