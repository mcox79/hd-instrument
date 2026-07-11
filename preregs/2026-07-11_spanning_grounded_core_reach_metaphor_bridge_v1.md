# Pre-registration: spanning_grounded_core_reach_metaphor_bridge_v1

Date: 2026-07-11
Cell: `experiments/exp_spanning_grounded_core_reach_metaphor_bridge_v1.py`
Anchor: `spanning_grounded_core_reach_metaphor_bridge_v1`
Author: exp_dev (hdi_exp_dev)
Line: SECONDARY (grounding / Line B) -- CPU/numpy, remote_cpu_queue; does NOT compete with the GPU reasoning FULL.
Spec: `notes/research_math_social_abstract_grounding_core_expansion_2026-07-10.md` Section 3 (B) "METAPHOR/ANALOGY
STRUCTURAL BRIDGE" + Section 4 HARD-FAIL item 1; hand-off `notes/exp_dev_handoff_research_math_social_abstract_grounding_
core_expansion_2026-07-10.md` Anchor 3. UNBLOCKED by Director (both scalar-channel anchors' residuals measured).
Reuses (validated): `exp_spanning_grounded_core_reach_v1` (reach apparatus: build_relational_subgraph / _diffuse_attr /
_cos / global z-scoring) + `exp_spanning_grounded_core_reach_magnitude_v1` (Anchor 1: magnitude/ordinality channels +
numeral core anchors + build_attr_matrix_ext) + `grounding_consolidation_loop_degree_invariant_v1` (a519 diffusion-with-
restart engine). No new mechanism -- the bridge is a new EDGE TYPE only.
Prior-work check: substrate_query "metaphor structural bridge image schema grounding abstract math operation words" ->
top hit cosine 0.3105 (note "3.2 PP-316 Image-Schema Grounding -- Real Abstract Concepts" + a "metaphor matrix" drill
idea using GloVe as VSA proxy). Those are DRILL/design notes (embodied-cognition scans), NOT a landed arc CELL that
tested a GROUNDED_VIA_METAPHOR edge type in the reach apparatus. This cell is genuinely novel as an experiment (first
edge-type implementation), informed-not-caged by the prior scans. Reported per the concept-query-before-authoring rule.

## Question

Anchor 1 (magnitude scalar channel) moved NUMERAL words but left MATH-OPERATION words (multiplication, ratio, equation,
infinity) UN-MOVED at ~-0.13 CITED@spawn-prompt (MIDDLE_BAND); Anchor 2 (social scalar channel) = HARD_FAIL_AFFECT_RELABEL.
Both scalar channels converge: operation words have NO scalar attribute value to inject -- they are grounded STRUCTURALLY
(Lakoff & Nunez metaphorical structure-mapping onto embodied image schemas), not by a scalar. Does adding a
GROUNDED_VIA_METAPHOR graph EDGE from each math-operation concept to a concrete image-schema hub (PATH/CONTAINER/FORCE/
COLLECTION/MOTION), reusing the existing diffusion machinery, move MATH-OPERATION-word grounding-reach off ~-0.13 where
the magnitude scalar channel could not? Apples-to-apples: the magnitude-only baseline arm reproduces the Anchor-1 state
(same Y incl. magnitude, same core, same base graph) so the ONLY between-arm difference is the metaphor edges.

## Mechanism (the structural bridge; new EDGE TYPE, not a scalar channel)

- IMAGE-SCHEMA LITERAL HUBS: 5 embodied schemas, each a synthetic core node whose attribute vector = nanmean of the
  MEASURED norm rows of its concrete EXEMPLAR words (PATH: road/journey/step/... ; CONTAINER: box/hold/fill/... ; FORCE:
  push/pull/weight/... ; COLLECTION: pile/heap/gather/... ; MOTION: move/flow/travel/...). REAL measured norms; a schema
  with no in-graph exemplar coverage gets NaN and is excluded (honest; HARD_FAIL_HUBS_MISSING if <3 hubs land).
- METAPHOR EDGES (Lakoff/Nunez arithmetic-grounding metaphors): each MATH-OPERATION probe -> its schema hub. Object-
  Collection (multiplication/sum/division/fraction/ratio/probability -> COLLECTION); Motion-Along-Path (average/integer/
  infinity/theorem -> PATH); balance (equation -> FORCE); container-of-value (variable/algebra/geometry -> CONTAINER);
  growth/rotation (exponent/angle -> MOTION). Probe stays HELD-OUT of core; diffusion carries the hub coordinate to it.
- INHERITS MAGNITUDE: baseline already carries Anchor-1 magnitude/ordinality channels + numeral core anchors.

## Arms / controls (4 arms differ ONLY by the metaphor edge set on the shared base graph; global z-scoring computed once)

- METAPHOR_BRIDGE: base graph + correct metaphor edges to the Lakoff/Nunez schema hubs (the mechanism).
- MAGNITUDE_BASELINE: base graph, NO metaphor edges (= the Anchor-1 magnitude state; the ~-0.13 operation-word baseline).
- SCRAMBLED_MAPPING (must-fail): metaphor edges present but the schema assignment PERMUTED across operation probes (each
  wired to another probe's schema hub) -> the gain must vanish (specific metaphor, not "any embodied edge").
- RANDOM_SCHEMA (must-fail): each operation probe wired to a UNIFORMLY-RANDOM schema hub -> the gain must vanish.

## Reach metric (identical to v1 / Anchor 1; apples-to-apples)

Per operation probe: grounded coordinate = diffusion-with-restart of the core's global-z-scored measured-attribute
vectors over the arm's graph (core + hubs anchored, probe starts at 0); sim = base._cos(coordinate, probe's OWN true
global-z-scored attribute vector) over co-present channels (MIN_REACH_CHANNELS=3, else no-coverage flag). MATH-OPERATION
subset = base.PROBES["MATHEMATICAL"] (multiplication, ratio, infinity, equation, integer, geometry, algebra, fraction,
exponent, variable, theorem, average, angle, probability, sum, division) -- reported SEPARATELY (per contract), not just
aggregate MATH. MEDIAN across seeds (seed-fragility discipline).

## Pre-registered bands (numeric; picked BEFORE the run; research-note Section 4 item 1 bar, sharpened not loosened)

SIM_FLOOR=0.30 (per-probe reach; random S-dim cosine E[cos]~0 std~1/sqrt(S)); MATH_OP_SIM_PASS=+0.15 (held-out operation
mean sim floor); MIN_ABS_GAIN=0.10 (mech - magnitude baseline, absolute); SPECIFICITY_MARGIN=0.05 (scrambled+random <=
baseline + this); BRIDGE_ABLATION_MIN_REL=0.50 (removing metaphor edges collapses >= 50% of the gain); HOPS=2,
CONS_PASSES=6, CONS_ALPHA=0.25 (engine defaults inherited from validated a519).

### METAPHOR_BRIDGE_GROUNDS_MATH_OP (structural fix REAL; ALL must hold)
operation mean sim_mech >= +0.15 (off ~-0.13) held-out AND gain (mech - baseline) >= 0.10 AND bridge ablation >= 0.50
relative AND scrambled <= baseline+0.05 AND random <= baseline+0.05, on the MEDIAN across 5 seeds.

### HARD_FAIL_BRIDGE_INSUFFICIENT (LEGITIMATE bounded finding; literature-consistent)
operation sim stays <= 0 with well-behaved (correctly-failing) scrambled+random controls -> the metaphor edge type is
well-formed but insufficient; the operation-word residual is carried by language/convention (Pecher & Zeelenberg boundary),
NOT a bug to chase with more edge types. Reported as a bounded finding, not an apparatus failure (self-test proves the
apparatus DETECTS a bridge when one exists).

### HARD_FAIL_FAIRNESS
scrambled OR random ALSO gains (> baseline + max(0.05, 0.5*gain)) while a gain exists -> any embodied edge inflates; the
specific metaphor mapping does no work; reject the operationalization.

### MIDDLE_BAND
operation sim moves positive but below +0.15, or gain/ablation weak -> investigate before scaling.

## Self-test (SELFTEST_PASS; LIGHT local gate; MEASURED)

Planted metaphor world (K=4 near-orthogonal schema signatures in Dc=10; exemplar core nodes = signature+noise -> grounded
hubs; operation probes' TRUE attrs = their schema signature but their only base edges run to a FEW exemplars of an
ORTHOGONAL schema -> baseline ~un-grounded). MEASURED@data/exp_spanning_grounded_core_reach_metaphor_bridge_v1_selftest/
metrics.json (run_mode=self_test, elapsed 0.067s, st_ok=True):
- (a) correct metaphor edges -> operation reach flips positive: op_sim_mech=+0.292 (>= +0.15) MEASURED.
- baseline (no metaphor edges) anti/un-grounded: op_sim_baseline=-0.026 MEASURED (baseline_anti fires).
- (c) scrambled mapping collapses the gain: op_sim_scrambled=-0.033 (<= baseline+0.05) MEASURED.
- (d) random schema collapses the gain: op_sim_random=-0.099 MEASURED.
- op_gain=+0.318; op_reach_mech=0.562 (> baseline reach); 4 distinct arm signatures (arms_differ).
Plants the FULL reach logic at small n = discriminator-survives-scale (Path C planted-preview; per-probe reach fraction
scale-invariant in expectation).

## Smoke (LOCAL, source=cn; MEASURED; apparatus + real-graph controls only, NOT the science)

MEASURED@data/exp_spanning_grounded_core_reach_metaphor_bridge_v1_smoke/metrics.json (run_mode=smoke, elapsed 4.7s,
16.5KB): source=cn n=3000 edges=11378; 5/5 schema hubs (10 exemplars each); 16/16 operation probes mapped; 12 channels
selected (incl magnitude); 4 distinct arm sigs. Preview verdict HARD_FAIL_BRIDGE_INSUFFICIENT: op_sim_mech=-0.201,
baseline=-0.219, gain=+0.017 -> on the SPARSE CN-only smoke graph the bridge barely moves operation words (leans toward
bounded-finding). This is a PREVIEW, not the canonical verdict: FULL uses the far richer CSKG cross-cutting graph
(n_kernel 1500, max_nodes 6000, 5 seeds) which supplies the relational context the bridge needs. Smoke's job (apparatus
runs + self-test discriminators fire + no spurious fairness inflation) is satisfied; the science is decided by FULL.
(scramble_ok=False at smoke is 2-seed noise on the sparse graph with no gain to inflate -> verdict correctly routes to
bounded-finding, not HARD_FAIL_FAIRNESS.)

## SCHEMA-VET

cell_chunked: false (single graph; seeds cheap; per-seed loop with cardinality-breach guard); start_marker_written: true;
crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics + traceback; SystemExit/KeyboardInterrupt re-raised);
final_metrics_atomicity: tmp_replace (write_metrics + os.replace; write_partial per seed); arms_differ_verified: true
(>=4 distinct arm sigs asserted per seed); except SystemExit before except Exception (no bare/BaseException; grep-gate
clean); crlb: per-probe cosine chance ~0 std~1/sqrt(S) (THEORETICAL), MATH_OP_SIM_PASS +0.15 strictly above 0 by the full
margin; baseline_in_band: MAGNITUDE_BASELINE operation sim <= 0 is the in-band anti-grounded baseline by construction
CITED@spawn-prompt(-0.13) + MEASURED@smoke(-0.219); discriminator-survives-scale: planted self-test fires bridge gain +
scramble collapse + random collapse at full reach logic; cardinality_ok: EXPECTED_N_UNITS=n_seeds (per-seed arms-differ +
cardinality-breach guard); calibration_check: default_ok_for_this_regime (SIM_FLOOR/pass/gain/ablation bands PRINCIPLED
and fixed before the run; engine CONS_* inherited from a519); progress_logging: print_flush_true (all _log flush=True;
MANDATORY as FULL timeout >= 1800s); sweep_alignment_verdict: N/A (no parameter sweep); discriminating_fraction: N/A
(fixed operation-probe subset, not a sweep); composition_edges: core+hub grounded-attr -> diffusion-with-restart -> probe
coordinate (SHAPE_MATCH: engine consumes [n,d] anchors + edge lists directly; metaphor edges are ordinary graph edges);
positive_control: planted correct-mapping arm reaches +0.292 (reproduces the bridge mechanism at the planted regime) +
MAGNITUDE_BASELINE reproduces the Anchor-1 operation-word state; functional_requirements: (i) build image-schema literal
hubs from measured exemplar norms, (ii) map each operation word to its Lakoff/Nunez schema, (iii) wire GROUNDED_VIA_METAPHOR
edges, (iv) diffuse + measure operation-word reach vs magnitude-only baseline, (v) prove specificity (scrambled/random
must-fail) + edge-carried (ablation) -- each decomposed + mapped to a validated primitive. Data-dependency: cell self-
acquires 4 norm files + CSKG via curl (validated) else HARD_FAIL_DATA_MISSING.

## Compute architecture

class (a), CPU-fast eval; DOMINANT cost = one-time streaming parse of the ~6M-edge CSKG TSV (CPU/IO-bound; gzip 112MB)
then edge-list diffusion-with-restart (n capped 6000) x 6 passes x 4 arms x 5 seeds -> seconds/seed on CPU (smoke was 4.7s
for 2 seeds x 4 arms at n=3000). Storage SHARDED. SELF-TEST planted-only (LOCAL, 0.067s). SMOKE source=cn (LOCAL). FULL
CSKG assembly + operation-subset reach routes to REMOTE (remote_cpu_queue; numpy/CPU; does NOT compete with the GPU
reasoning run). SMOKE-ONLY-LOCAL lock honored.

## Config

FULL: seeds=[7,13,17,23,29], source=cskg, n_kernel=1500, max_nodes=6000. SMOKE: seeds=[7,13], source=cn, n_kernel=300,
max_nodes=3000. SELFTEST: planted (LOCAL, SELFTEST_PASS).
FULL timeout: 3600s (worst-case CSKG self-acquire curl --max-time 1200 if uncached + ~3min 6M-edge streaming parse + ~5min
eval (5 seeds x 4 arms) + margin). progress_logging=print_flush_true as FULL timeout >= 1800s heartbeat-mandate.
```
bash tools/orchestrator/queue_add.sh remote_cpu_queue spanning_grounded_core_reach_metaphor_bridge_v1 experiments/exp_spanning_grounded_core_reach_metaphor_bridge_v1.py preregs/2026-07-11_spanning_grounded_core_reach_metaphor_bridge_v1.md 3600 --run-mode full --device cpu
```
