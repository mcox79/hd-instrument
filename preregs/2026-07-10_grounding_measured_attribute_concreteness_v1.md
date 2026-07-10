# Pre-registration: grounding_measured_attribute_concreteness_v1

Date: 2026-07-10
Cell: `experiments/exp_grounding_measured_attribute_concreteness_v1.py`
Anchor: `grounding_measured_attribute_concreteness_v1`
Author: exp_dev (hdi_exp_dev)
Engine reused (validated): `grounding_consolidation_loop_degree_invariant_v1` (diffusion-with-restart + collapse discriminator + independence gate; SELFTEST_PASS).

## Question (the fair grounding test)

Does anchoring the consolidation geometry to a genuinely-EXTERIOR MEASURED attribute (Brysbaert concreteness) produce
degree-INVARIANT grounding of the REAL ConceptNet substrate graph -- i.e. does the measured channel add held-out
concreteness-prediction power OVER the relational graph alone, survive the low-degree tail, and depend on the attribute
VALUES (scrambled control)?

## Dataset (Option C; coordinator-chosen) + provenance

Brysbaert, Warriner & Kuperman (2014) concreteness norms (Conc.M, 1..5; 39,954 words) joined to the ConceptNet subgraph
`load_typed_cn_subgraph`. Provenance: `data/grounding_testbed/PROVENANCE_concreteness.md` (source URL + citation + sha256;
LOCAL testbed input, NOT written to canonical substrate_index; self-acquired via curl if absent on the runner).
MEASURED@smoke: coverage 75.4% (1616/2143 at n_nodes=2500); covered+connected n=1609, edges 9642, degree 1..228,
concreteness std ~1.0. At n_nodes=5000: coverage 73.9%, n~3262, degree 1..238.

## Task (DETERMINACY: scalar, unique answer)

Hold out 30% of concepts; predict their concreteness from graph position + the consolidated geometry. Score = SPEARMAN
rank correlation (predicted vs true held-out), aggregate + per-degree-stratum (LOW/MID/HIGH tertiles of held-out degree).

## THE FAIRNESS GATE (HARD go/no-go, computed BEFORE the loop)

- F_triv = mean baseline (Spearman ~0). F_A = relational-only consolidation predicting concreteness. C = ceiling
  (graph-neighbour TRUE-attribute smoothing oracle).
- RUN ONLY IF F_triv < F_A < C with real gaps AND F_A meaningfully below C (FAIR_FLOOR_GAP=0.05, FAIR_HEADROOM=0.05).
  Block if F_A ~= C (common-cause) or F_triv ~= C (no predictability). MEASURED@smoke: F_triv=0.000 < F_A=0.547 < C=0.689
  -> floor_ok=True headroom_ok=True -> CLEARED. (n=3262 probe: F_A=0.505, C=0.716.) Concreteness domain PASSES; no
  fall-back to Option B (PanTHERIA) needed.

## Ablation + controls (the decisive discriminator)

- A-alone (F_A) = ablation of the exterior channel (consolidate structural anchor only). A+B = structural + measured
  concreteness in the restart anchor (VISIBLE values; held-out MASKED to visible-mean -> LEAK-FREE; diffusion spreads
  visible concreteness to held-out via the graph). Grounding evidence = A+B - F_A.
- Scrambled must-fail control: permute concreteness across concepts; A+B_scrambled - F_A must be ~0 (grounding must
  depend on VALUES, not channel presence). MEASURED@smoke: scrambled gap = -0.557 (fires).
- Independence pre-flight (reused engine gate): struct vs attribute channel. MEASURED@smoke: cross_sim_r=0.055,
  struct_deg_r=-0.070, attr_deg_r=0.058 -> genuinely independent, neither degree-loaded, not redundant.
- Collapse discriminator (reused): effective_rank + rep_variance floors. MEASURED@smoke: eff_rank~31.8, rep_var~0.97 (healthy).

## Pre-registered bands (numeric; BEFORE the FULL; principled, consistent with the engine cell)

FAIR_FLOOR_GAP=0.05, FAIR_HEADROOM=0.05, GROUND_MARGIN=0.05, STRAT_GROUND_MARGIN=0.03, SCRAMBLE_MAX=0.02, TIE_EPS=0.02,
MIN_STRAT_Q=40, HELDOUT_FRAC=0.30, COLLAPSE_RANK_FLOOR=3.0, COLLAPSE_VAR_FLOOR=0.02, CONS_KNN=8, CONS_PASSES=6, CONS_ALPHA=0.25.

### HARD_PASS_GROUNDING_REAL (ALL)
fairness cleared AND channels_independent AND not collapsed AND aggregate grounding gap (A+B - F_A) >= 0.05 AND
(A+B - F_A) >= 0.03 in BOTH LOW and MID strata (>=40 each; degree-invariant) AND scrambled gap <= 0.02.

### HARD_FAIL_GROUNDING_NOT_REAL
aggregate gap <= 0.02 (no exogenous work) OR grounding collapses on the tail (LOW or MID gap <= 0.02) OR scrambled also
grounds (scrambled gap >= 0.05).

### HARD_FAIL_FAIRNESS_BLOCKED / HARD_FAIL_CHANNELS_NOT_INDEPENDENT / HARD_FAIL_CONSOLIDATION_COLLAPSED
fairness gate fails / independence gate flags / consolidation collapses.

### MIDDLE_BAND_PARTIAL
otherwise (gain present but aggregate below the material bar / tail or scramble ambiguous).

## Smoke result (n=1609, 2 seeds, CPU 1.5s)

VERDICT MIDDLE_BAND_PARTIAL: F_A=0.520 A+B=0.561 grounding_gap=+0.041 (just below the 0.05 material bar at reduced
scale/2-seed variance) scrambled_gap=-0.557; STRATA gap LOW=0.085 MID=0.059 HIGH=0.053 -> tail_survives=True
(degree-invariant, LOW largest); fairness cleared; independent; not collapsed. The grounding signal FIRES and is
degree-invariant + scrambled-controlled; the aggregate sits at the margin -> the FULL (n=5000, 5 seeds) is the canonical
resolver. n=3262/3-seed probe gave aggregate +0.064 (clears 0.05). Reported as a smoke MIDDLE-to-PASS; mechanism story
HELD until landed-VET.

## Self-test (SELFTEST_PASS, 0.1s CPU)

(a) informative degree-independent attribute -> A+B beats A-alone (gap 0.265) + survives LOW-degree tail (0.230);
(b) scrambled does NOT ground (-0.518); (c) fairness-gate logic: headroom world passes (F_A 0.44 < C 0.98),
unpredictable world (y independent of graph) BLOCKS (F_A -0.04 ~ C -0.00 -> floor not cleared); (d) collapse caught.

## SCHEMA-VET

cell_chunked: false; start_marker_written: true; crash_diagnostic_present: true; final_metrics_atomicity: tmp_replace;
arms_differ_verified: true (>=4 sigs); except SystemExit before except Exception (no bare/BaseException);
crlb: Spearman chance ~0 THEORETICAL, HARD_PASS strictly above; baseline_in_band: F_TRIV null ~0, C must-fire ceiling
> F_A (headroom); discriminator-survives-scale: engine params shared self-test<->FULL, real-graph fairness+ablation is
the open measurement (smoke fires, at-margin -> FULL resolves); calibration_check: default_ok_for_this_regime (degree
tertiles data-driven; bands principled, not tuned to smoke -- smoke aggregate 0.041 is BELOW the 0.05 pre-registered bar);
cardinality_ok: EXPECTED_N_UNITS=n_seeds; progress_logging: print_flush_true; positive_control: C_CEILING oracle fires
(> F_A); functional_requirements: predict measured attribute from graph + exterior channel, exterior must be load-bearing
(ablation) -- decomposed. Data-dependency: cell self-acquires the public testbed file via curl if absent (validated by
header), else HARD_FAIL_DATA_MISSING.

## Compute architecture

class (a), CPU-fast: structural features + diffusion (dense [n,n]@[n,dim], n~3262) + ridge (small solve). NO KGE / NO
encoder. ~seconds/seed. FULL routes to remote_cpu_queue (CPU; no GPU benefit; SMOKE-ONLY-LOCAL lock keeps laptop free).

## Config

FULL: seeds=[7,13,17,23,29], n_nodes=5000. SMOKE: seeds=[7,13], n_nodes=2500. SELFTEST: planted worlds.
