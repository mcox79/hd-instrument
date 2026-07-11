# Prereg: grounding_labelshuffle_null_cskg_v2 -- redesigned grounding-percolation audit (label-shuffle null)

- Cell: `experiments/exp_grounding_labelshuffle_null_cskg_v2.py`
- Anchor: `grounding_labelshuffle_null_cskg_v2`  (no `_n<N>` suffix -> N-suffix binding rule N/A; this is a
  graph-reachability audit, not an N-dim substrate sweep. Production has no vector dimensionality.)
- Queue: `remote_cpu_queue` (pure numpy/stdlib CPU; no torch; keeps the laptop free per no-local-smokes lock)
- Supersedes-context: `exp_grounding_percolation_reachability_cskg_v1` (HARD_FAIL; landed-VET =
  ARTIFACT_INCONCLUSIVE -- P1 null confounded).

## Question
Is abstract-concept grounding a STRUCTURAL property of the ingested CSKG cross-cutting graph -- i.e. do
concreteness-anchored (grounded) seeds reach the abstract-concept target population better than arbitrary
seeds, AND is that advantage carried by the REAL grounding-signal-to-topology alignment rather than by
topology/degree that any labeling of the same graph would inherit?

## Why v2 (the v1 VET finding this fixes)
v1's P1 must-fail control was a degree-preserving double-edge-swap scramble, and the pre-reg bet "real graph
reaches abstract targets at SHORTER median hop than the scramble." That direction is near-UNWINNABLE BY
CONSTRUCTION: degree-preserving randomization GENERICALLY SHORTENS path length (destroys clustering, injects
long-range shortcuts -- textbook small-world), so the scramble almost always beats the real graph on median
hop -> forced HARD_FAIL independent of substrate truth. The confound was in the NULL MODEL.

## Null redesign (autonomous design choice)
REPLACE the degree-preserving scramble with a **concreteness-LABEL-SHUFFLE null** -- the strongest
TOPOLOGY-PRESERVING null. It preserves the ENTIRE graph structure EXACTLY (degree sequence, clustering
coefficient, community structure), and permutes ONLY the exogenous concreteness labels across the covered
nodes. This is the limiting case of the offered "clustering-preserving null" (preserves not just clustering
but all topology), so it cannot suffer the small-world path-shortening artifact -- there is NO rewiring.

A concrete->abstract BRIDGE-SURVIVAL test (the other offered option) was prototyped and REJECTED as
inherently confounded here: the reach target (the concrete seed set S) and the "bridges" (concrete-crossing
edges) are BOTH defined by the same concreteness axis, so bridges always point toward S's region and their
deletion hurts concrete-reach REGARDLESS of grounding; label-shuffling does not break this because S and the
bridge set stay co-defined. The self-test measured a persistent ~0.03 tautological offset under shuffled
labels for that design. The label-shuffle null has no such coupling; its negative control goes cleanly to
~0.00 (verified in self-test).

## Arms + falsifiable bands (headline = grounding STRUCTURAL iff P2 AND P1 both HARD_PASS)

### P2 -- grounded-seed advantage (the valid v1 positive, promoted to FIRST-CLASS + faired)
The one v1 control that was NOT confounded: grounded (concreteness-selected) seeds beat size-matched RANDOM
seeds at small k on the SAME graph (v1: reach_S(k<=2)=0.467 > random 0.368). Faired here: random seeds are
drawn from the NON-TARGET pool matched to |S| (S is disjoint from A by construction; v1 drew random from ALL
nodes, letting a random seed land ON a target -> dist 0 -> counted unreached -> spuriously depressed random
reach).
- HARD-PASS: reach_S(k<=2) > random-seed 95th-pct AND reach_S(k<=2) - random-seed MEAN >= P2_EFFECT_BAR=0.05
  AND grounded median hop < random mean median hop.
- HARD-FAIL: reach_S(k<=2) inside the random-seed [p5,p95] band AND margin < effect bar.
- MIDDLE_BAND: otherwise.

### P1 -- form-without-content / topology-preserving null (the REDESIGNED null)
- HARD-PASS: real grounded-margin > label-shuffle-null 95th-pct AND (real margin - null mean) >=
  STRUCT_EFFECT_BAR=0.03. (The advantage is carried by the real grounding labels, not topology.)
- HARD-FAIL: real margin inside the null [p5,p95] AND (real margin - null mean) < STRUCT_EFFECT_BAR.
  (Any labeling of the same graph does as well -- the Bender-Koller octopus / form-without-content failure.)
- MIDDLE_BAND: otherwise.

### P3 -- kernel/hub != grounded population (v1's un-confounded secondary; kept)
- HARD-PASS: mean Conc.M(top-degree hub seeds) <= mean Conc.M(S) - 0.5 AND hub mean < 3.0
  (Vincent-Lamarre 2016: dictionary-graph core/kernel words are LESS concrete than satellites).
- HARD-FAIL: hub mean >= S mean - 0.1 (centrality is an acceptable grounding-seed proxy after all).

## Achievability positive control + must-fail negative control (self-test; both behave correctly)
- POSITIVE control (synthetic grounded graph: concrete anchors bridge to an isolated abstract mesh; dense
  mid-conc background; low-conc hubs). MUST clear BOTH the P2 and P1 HARD-PASS bars. This proves the bars
  are ACHIEVABLE -- exactly what v1's confounded/unwinnable bar failed. MEASURED@self-test: P2 margin=0.684
  (>> 0.05), P1 real_margin=0.684 > nullP95=0.021 (struct=0.685 >> 0.03). Both HARD_PASS.
- NEGATIVE control (form-without-content: the SAME topology with concreteness labels randomly SHUFFLED --
  identical FORM, scrambled CONTENT). MUST FAIL both bars DETERMINISTICALLY over repeats WITH MARGIN.
  MEASURED@self-test (each repeat = mean of 8 shuffles for tight variance): P2 margins=[0.000,0.000,-0.001,
  0.002] (all < 0.05); struct margins=[-0.000,-0.000,-0.002,0.001] (all < 0.03). Both fail robustly.
Positive + negative controls run the SAME `grounded_advantage()` + `label_shuffle_null()` code path as the
real CSKG audit (no separate synthetic logic to drift), so passing them validates the real arms.

## Validity preflight (MANDATORY -- all four DECLARED in self_test(); this cell is the poster child)
`from experiments._validity_preflight import run_validity_preflight` (triggers module auto-SCP). Declared:
1. `positive_control` (MANDATORY) -- synthetic grounded arm clears the P2+P1 HARD-PASS bars. Catches the
   exact v1 failure: an unwinnable bar. MEASURED@self-test: passes.
2. `metric_moves` -- reach_S(k<=2) moves from an EMPTY seed set (0.000) to grounded seeds (1.000). Catches a
   structurally-frozen readout.
3. `full_gates_exercised` -- the FULL fail-closed gates (cardinality, arms_differ) are exercised at
   self-test scale, not only at run_mode=full.
4. `negative_control_margin` -- TWO must-fail controls (form_without_content_P2 + form_without_content_
   labelshuffle) fail deterministically over 4 repeats WITH margin.
Preflight mode = WARN (bake period); self-test additionally has belt-and-suspenders hard asserts.
MEASURED@self-test: `preflight_ok=True` (all four green, zero WARN).

## Confounds controlled
- Small-world path-shortening (the v1 confound): ELIMINATED -- no rewiring; label-shuffle preserves all
  topology exactly.
- Target-overlap bias: random-seed control drawn from NON-TARGET pool (matched to S which is disjoint from
  A). Caught + fixed at self-test (before the fix, shuffled-label margins were biased +0.035).
- Degree confound / centrality vs groundedness: measured directly by P3 (hubs vs grounded seeds) + the P1
  null preserves the degree sequence exactly, so a pure-degree explanation of the grounded advantage would
  survive label-shuffling and FAIL P1.
- Coverage: reported (`coverage_frac`); data-sufficiency floors MIN_SEEDS=100, MIN_TARGETS=200 gate the run
  (HARD_FAIL_DATA_INSUFFICIENT if unmet -- an honest abort, not a fake verdict).
- Metric saturation at scale (discriminator-survives-scale, option B): all metrics at k<=2 (non-saturated;
  v1 measured reach_S(k<=2)=0.467, well below 1.0). Small-k carries resolution.

## SCHEMA-VET fields
- cardinality_ok: EXPECTED units = N_RANDOM_DRAWS(20) + N_LABEL_SHUFFLE(20); short -> HARD_FAIL_CARDINALITY_
  BREACH_META_RULE_H.
- arms_differ_verified: >=3 distinct sigs (S / controlA-random-seed / labelshuffle / controlC-hub); gated.
- final_metrics_atomicity: tmp_replace (write_metrics + crash-writer both tmp+os.replace).
- except-ordering: `except SystemExit: raise` before `except Exception`; no BaseException, no bare except
  (grep-clean).
- crlb_n/a: graph-reachability distribution-separation audit; achievability proven by positive control, not
  a CRLB. calibration_check: default_ok_for_this_regime (BFS + label permutation are parameter-free).
- baseline_in_band: random-seed + label-shuffle nulls are OPEN MEASUREMENTS at full scale (reported, not
  smoke-aborted); self-test proves the machinery separates signal from null.
- discriminator survives scale: analytical option B (k<=2 non-saturated).
- start_marker_written / crash_diagnostic_present / heartbeat_present: yes (per label-shuffle draw).
- progress_logging: print_flush_true. cell_chunked: false (single graph).
- effective_vs_nominal / discriminating_fraction / composition_edges / positive_control_arms /
  functional_requirements: this is a pure graph audit, not a primitive-composition or parameter-sweep cell;
  no swept axis and no chain-grade primitive composed. The label-shuffle null IS the positive/negative
  control apparatus (declared above).

## Compute architecture
Class (b) sequential-CPU with justification: pure combinatorial graph traversal (multi-source BFS over CSR,
label permutation, dict joins). NO substrate vectors / bind-unbind / matmul / torch -> GPU batching does not
apply. No degree-preserving swap (v1's expensive + confounded step is gone); the null only permutes a
length-n float array + re-selects seeds then reuses the SAME CSR -> strictly cheaper than v1. Storage:
no_storage / no_composition.

## Timeout estimate
- Anchor: v1 landed elapsed_s=271s MEASURED@data/exp_grounding_percolation_reachability_cskg_v1/metrics.json
  WITH the expensive degree-preserving swap (20 rewirings x 3*|E| swaps). v2 removes the swap entirely.
- v2 BFS budget: P2 (1 grounded + 20 random) + P1 (20 shuffles x (1 grounded + 5 random) = 120) + 1 hub
  ~= 142 multi_source_bfs on the ~471k-node / ~1.18M-edge LCC (~0.5-2s each vectorized) ~= 150-300s, plus
  gzip parse (~30-60s) + union-find LCC build (~20-40s). Estimate ~250-400s.
- Self-test wall (synthetic) = 14s (not representative of the full-graph parse; used only for gate).
- TIMEOUT SET = 2400s (40 min), ~6-9x the estimate anchored on v1's 271s + v2's larger BFS count. Under the
  4h hard cap and under the 2h long-run-flag threshold.

## Dispatch
`bash tools/orchestrator/queue_add.sh remote_cpu_queue grounding_labelshuffle_null_cskg_v2 experiments/exp_grounding_labelshuffle_null_cskg_v2.py preregs/2026-07-11_grounding_labelshuffle_null_cskg_v2.md 2400`

Runner invokes `python -u <script>` with no argv -> `_selftest()` (fast synthetic gate, asserts fire) then
`main()` at RUN_MODE=full. Expected landed run_mode=full, verdict in {HARD_PASS_GROUNDING_STRUCTURAL,
HARD_FAIL_GROUNDING_NOT_STRUCTURAL, MIDDLE_BAND_PARTIAL}. This is an OPEN measurement -- any of the three is
a valid scientific outcome (v1's confound is removed).
