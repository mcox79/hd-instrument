# Pre-registration: grounding_percolation_reachability_cskg_v1

**Date:** 2026-07-11
**Cell:** `experiments/exp_grounding_percolation_reachability_cskg_v1.py`
**Anchor:** `grounding_percolation_reachability_cskg_v1`
**Queue:** `remote_cpu_queue` (pure CPU graph BFS; no GPU benefit; keeps the laptop free per the no-local-smokes lock)
**Design source (verbatim):** `notes/research_grounding_percolation_reachability_cskg_audit_2026-07-11.md`
("Cheap decisive test" + "Falsifiable predictions" sections). Bands below are LIFTED from that note's
falsifiable-predictions table, NOT re-derived.

## Question
Is abstract-concept grounding a PERCOLATION / seeded-reachability property of the ingested graph? Does a
concreteness-ANCHORED seed set S reach the abstract-concept target population A on the real CSKG
cross-cutting graph, AND does the REAL edge structure (not just the degree sequence, not just seed count)
carry that reach? Pure graph computation; no training; no new data acquisition.

## Data (already on disk; no crawl)
- `data/grounding_testbed/cskg.tsv.gz` (112,312,195 bytes; Zenodo 4331372). Cross-cutting commonsense
  SPINE relations only (strips the 79% lexical/taxonomic dilution) per
  `notes/cskg_commonsense_core_kcore_density_gate_2026-07-10.md`. BFS graph = LARGEST CONNECTED COMPONENT
  of the cross-cutting simple-undirected graph (dense core PLUS periphery, for hop-count headroom).
- `data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt` (Brysbaert/Warriner/Kuperman 2014;
  Conc.M 1=abstract..5=concrete; 39,954 words). EXOGENOUS human-rated anchor; joined by lowercased exact
  label match. Provenance: `data/grounding_testbed/PROVENANCE_concreteness.md`.
- Both inputs verified present on disk (this laptop) and previously staged on the remote runner (the
  sibling cell `exp_grounding_measured_attribute_concreteness_v1` ran on remote using the same testbed
  dir). Cell also self-acquires from the documented public URLs if absent on the runner.

## Procedure (parameters I chose; autonomy per task)
1. **Grounded seed S** = the `N_SEED = 300` MOST-concrete covered non-function-word LCC nodes (a modest
   seed budget so hop-distance is GRADED, not saturated, in a dense LCC).
2. **Abstract targets A** = covered non-function-word LCC nodes with `Conc.M <= CONC_LOW = 2.5`, disjoint
   from S.
3. Function/grammatical words excluded from S and A (compact closed-class stoplist) per Vincent-Lamarre
   (function words confound the concrete/abstract contrast).
4. Multi-source BFS from S over the LCC -> hop-distance of each A node to nearest seed; reach curve
   `reach_S[k]` (frac of A within <= k hops, k=1..KMAX=6) + median hop-distance over reached targets.
5. **Control A (random-seed-same-graph):** `N_RANDOM_DRAWS = 20` random size-|S| seed sets, same graph.
6. **Control B (grounded-seed-scrambled-graph):** same S/A on `N_REWIRES = 20` degree-preserving
   double-edge-swap rewirings (`SWAP_MULT = 3` swaps per edge; degree sequence preserved exactly).
7. **Control C (kernel/hub seed):** S = top-N_SEED highest-degree LCC nodes; report its mean concreteness.

All three controls are MANDATORY and load-bearing: dense scale-free graphs percolate trivially, so a raw
reachability pass ALONE is VACUOUS. Prediction 1 HARD-PASS REQUIRES beating Control B.

## Falsifiable predictions (HARD-PASS / HARD-FAIL bands; lifted from the design note)

**Prediction 1 -- percolation framing is real and CSKG passes NON-VACUOUSLY.**
- HARD-PASS: `reach_S(k<=4) >= 0.70` (`P1_RAW_REACH_BAR`, matching the 70% grounding-reach threshold in
  `research_deliberate_ingest_spec_spanning_grounded_core_2026-07-10.md`) AND the real edge structure
  beats the degree-preserving scramble: `median_hop_S < ControlB_median_hop_p5` (S median hop strictly
  below the 5th percentile of the Control-B rewiring distribution). Median hop is used as the
  saturation-ROBUST structural discriminator (reach at k<=4 may saturate for both S and scramble on a
  dense graph; median hop does not).
- HARD-FAIL: `reach_S(k) < 0.70` at every k<=6 (closed-relational-island failure) OR reach
  indistinguishable from Control B (`median_hop_S >= ControlB_median_hop_p5`; form-without-content).

**Prediction 2 -- grounded seed selection beats generic seed-set size (Control A).**
- HARD-PASS: `reach_S(k<=2) > ControlA_reach(k<=2)_p95` (above the 95th percentile of the 20-draw random
  distribution; non/barely overlapping) AND `median_hop_S < mean(ControlA median hop)`. k<=2 chosen
  because it is non-saturated for |S|=300 in a ~1M-edge LCC.
- HARD-FAIL: `reach_S(k<=2)` inside the Control-A [p5,p95] band AND median hop comparable.

**Prediction 3 -- kernel/hub nodes are NOT the concreteness-anchored population.**
- HARD-PASS: `mean Conc.M(ControlC hub seeds) <= mean Conc.M(S) - 0.5` (`P3_CONC_MARGIN`) AND
  `mean Conc.M(hub) < 3.0` (materially less concrete than S; centrality != groundedness). Also report
  Spearman(degree, concreteness) over covered nodes (expected <= 0 per Vincent-Lamarre 2016).
- HARD-FAIL: `mean Conc.M(hub) >= mean Conc.M(S) - 0.1` (hubs as concrete as S; centrality is an OK
  grounding-seed proxy).

**Headline verdict** tracks Prediction 1 (the primary): `HARD_PASS_GROUNDING_PERCOLATES` /
`HARD_FAIL_GROUNDING_NOT_STRUCTURAL` / `MIDDLE_BAND_PARTIAL`. P2/P3 sub-verdicts reported in `gates`
(`p1_verdict`/`p2_verdict`/`p3_verdict`) and `verdict_msg`.

## Compute architecture
Class (b) sequential-CPU with justification: pure combinatorial graph traversal (multi-source BFS,
set-guarded double-edge-swap, dict joins). NO substrate vectors, NO bind/unbind, NO matmul, NO torch ->
GPU batching does not apply. BFS neighbourhood-gather is numpy-vectorized (CSR). Storage strategy:
`no_storage / no_composition`. numpy + stdlib ONLY (parity-safe: same self-contained discipline as
`exp_cskg_dense_core_headroom_acceptance_v1`, which ran on the remote runner without networkx).

## SCHEMA-VET declarations
- `arms_differ_verified`: true -- reach-vector sigs for S / ControlA / ControlB / ControlC must be >=3
  distinct (META_RULE_AF); enforced at self-test (e) AND before the FULL verdict.
- `final_metrics_atomicity`: `tmp_replace` (write_metrics + crash-writer both tmp+os.replace).
- `except SystemExit: raise` BEFORE `except Exception`; NO `except BaseException`; NO bare `except:`.
- `crlb_n/a`: no quantitative noise floor -- this is a graph-reachability audit, not an estimator. The
  discriminator is a distribution-separation test (S vs degree-preserving null / random-seed null); the
  self-test proves the separation is DETECTABLE by construction.
- `baseline_in_band`: the "baseline" is the null (Control A / Control B). At full scale, whether the null
  equals S is the OPEN MEASUREMENT reported as the verdict (not a smoke-abort). The self-test guarantees
  the machinery CAN detect a real separation (planted scramble reduces reach; random seeds under-reach
  planted targets).
- `discriminator_survives_scale`: analytical (option B). reach(k<=4) may SATURATE for both S and scramble
  on a dense graph, so P1's structural signal uses MEDIAN HOP-DISTANCE (S vs Control B), which does not
  saturate for a modest |S|; P2 uses reach(k<=2), also non-saturated for |S|=300 in a ~1M-edge LCC
  (k=1 neighbourhood of 300 seeds covers well under 100% of nodes). Small-k metrics carry resolution.
- `cardinality_ok`: EXPECTED control units = N_RANDOM_DRAWS (20) + N_REWIRES (20). Short count ->
  `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.
- `per-unit failure-class instrumentation`: no bare except; specific classes; data-missing /
  data-insufficient / cardinality / arms-identical each emit their own labelled HARD_FAIL metrics.
- `calibration_check`: `default_ok_for_this_regime` (BFS + double-edge-swap are parameter-free apparatus;
  the only knobs are seed budget / draw counts / swap multiplier, all declared here).
- `progress_logging`: `print_flush_true` (all logs flush=True; `_heartbeat.jsonl` appended per Control-B
  rewiring so a long rewiring loop is diagnosable).
- `cell_chunked`: false (single graph; no per-seed chunk). `start_marker_written`: true.
  `crash_diagnostic_present`: true. `heartbeat_present`: true (per rewiring).
- §15 gates A/C/D/E (effective-vs-nominal / shape-match / positive-control-reproducer /
  functional-decomposition): N/A -- this cell composes NO substrate primitives and sweeps NO substrate
  parameter; it is a pure external-graph acceptance audit (same class as
  `exp_cskg_dense_core_headroom_acceptance_v1`). Gate B (discriminating band): the CONTROLS are the
  discriminating apparatus and the self-test proves they FIRE (scramble reduces reach; random under-reaches).

## Self-test (tiny planted graph; deterministic; exits 0; does NOT touch CSKG)
Routed correctly per §16 / the prior ladder self-test-gate bug: `_selftest()` runs first (asserts fire),
then `if --self-test: write SELFTEST_PASS metrics + sys.exit(0)` -- a dedicated tiny branch that does NOT
fall through to the full CSKG audit. For a FULL run, `_selftest()` still runs first so the expensive audit
never executes on a broken BFS.
Discriminators (all must FIRE): (a) planted grounded->abstract path reachable within its planted hop; a
disjoint ISLAND of abstract nodes UNREACHABLE (dist == -1); (b) degree-preserving swap preserves the
degree sequence EXACTLY and reduces k<=2 reach (Control B fires); (c) grounded near-target seeds beat
random seeds at k<=2 (Control A fires); (d) planted LOW-concreteness hub has mean concreteness below the
concrete anchors (Control C / Prediction 3 fires); (e) reach arms differ.

## Timeout
`7200 s` (2 h). Estimate: CSKG stream+build LCC ~1-3 min; Control A 20 BFS ~fast; Control B 20 rewirings x
~3.3M double-edge swaps each (~66M set-guarded swaps total) is the dominant cost (~a few minutes) plus 20
CSR rebuilds + BFS. Generous headroom on a single shared runner. Cap 14400.

## Dispatch
`bash tools/orchestrator/queue_add.sh remote_cpu_queue grounding_percolation_reachability_cskg_v1 experiments/exp_grounding_percolation_reachability_cskg_v1.py preregs/2026-07-11_grounding_percolation_reachability_cskg_v1.md 7200`
Will QUEUE behind the running `course_c_oracle_capacity_ladder_v1` (single cpu_runner_0) and auto-run when
the runner frees. Post-ship REMOTE VERIFY via queue_add.sh exit code (exit 5 = not landed in remote
queue.json).
