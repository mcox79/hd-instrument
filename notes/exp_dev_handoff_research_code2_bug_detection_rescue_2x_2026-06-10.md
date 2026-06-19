# exp_dev hand-off -- research: code2 bug detection rescue 2x

Filed-by: research sub-agent, 2026-06-10
Trigger: research note notes/research_drill_code2_bug_detection_rescue_2x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and pre-reg bands only; exp_dev designs the implementation.

---

## Anchor candidates (rank-ordered, cheapest-first)

### Anchor 1 -- code2_r1_bundle_diff_cpu_v1 (CHEAPEST; Tier-1 gate)

Anchor pointer: R1 KNOWN-CORRECT-BUNDLE-DIFF

Substrate-product reading: build two HD bundles per program pair -- one from the verified-correct version, one from the test version. Compute 1 - cosine(correct_bundle, test_bundle) as bug score. Threshold to produce binary prediction. Measure AUC and F1 over n=720 pairs.

Why now: this is the cheapest decisive test for the PP-336 open gap. 30 min CPU. If AUC >= 0.72 the gap is resolved with a substrate-native capability (code correctness checking). This also directly tests whether the PP-333/PP-311 bundle construction transfers to a comparative correctness signal.

Pre-reg bands:
- HARD-PASS: AUC >= 0.72 AND F1 >= 0.70 at optimal threshold (n=720)
- MIDDLE-BAND: AUC 0.58-0.72 (marginal signal; combine with R6 shard extension)
- HARD-FAIL: AUC < 0.58 (reference-comparison does not provide signal; move to R2)

Tier hint: Tier-1 (gate for all subsequent rescues; run first)

### Anchor 2 -- code2_r3_property_test_cpu_v1 (PARALLEL; Tier-1 parallel gate)

Anchor pointer: R3 PROPERTY-TEST-VIA-INVARIANT

Substrate-product reading: for each test program, generate (input, expected-output) pairs for a set of test cases. Bind each pair as a substrate role-filler bundle. Build an expected-output bundle. Run the program under test and build an observed-output bundle. Bug score = HD distance between expected-output bundle and observed-output bundle, aggregated.

Why now: this tests a different signal axis than R1 (output semantics vs structural comparison). Can run in parallel with Anchor 1 at low cost. If both pass, they are combinable for a stronger detector.

Pre-reg bands:
- HARD-PASS: AUC >= 0.70 AND F1 >= 0.68 (n >= 300 pairs with executable test cases)
- MIDDLE-BAND: AUC 0.58-0.70
- HARD-FAIL: AUC < 0.58 OR fewer than 200 executable test cases in dataset

Tier hint: Tier-1 (parallel with Anchor 1; 1-2 hr CPU)

### Anchor 3 -- code2_r6_shard_localise_cpu_v1 (CONDITIONAL on Anchor 1 MIDDLE-BAND)

Anchor pointer: R6 SHARD-LEVEL-LOCALISATION

Substrate-product reading: shard each program into per-function sub-bundles using PP-311 mechanism. Compare per-function shards of test program to corresponding shards of correct program. Bug detection score = max shard-level HD distance. Bug localisation = top-1 highest-distance shard.

Why now: if Anchor 1 returns MIDDLE-BAND, per-function granularity may improve the signal. SBFL literature shows per-element scoring outperforms whole-program scoring. Run only if Anchor 1 is not HARD-PASS.

Pre-reg bands:
- HARD-PASS: AUC >= 0.70 AND top-1 localisation accuracy >= 0.55 (correct function identified as buggy)
- MIDDLE-BAND: AUC 0.58-0.70 OR localisation accuracy 0.30-0.55
- HARD-FAIL: AUC < 0.58 AND localisation < 0.30

Tier hint: Tier-2 (conditional on Anchor 1 result; 45 min CPU)

### Anchor 4 -- code2_r2_trace_binding_cpu_v1 (CONDITIONAL on Anchor 1 HARD-FAIL)

Anchor pointer: R2 EXECUTION-TRACE-BINDING

Substrate-product reading: for programs where a simple interpreter can generate execution traces (pure Python arithmetic/control-flow), bind the correct trace as a sequential HD bundle (operation sequence using position-encoding multiplication). Build the test trace bundle. Bug score = HD distance between trace bundles.

Why now: if structural comparison (R1) fails, execution-semantic comparison (R2) is the next strongest signal. Requires trace generation -- limited to programs with a Python executor. Run only if Anchor 1 is HARD-FAIL.

Pre-reg bands:
- HARD-PASS: AUC >= 0.75 AND F1 >= 0.68 (on trace-enabled subset, n >= 150)
- MIDDLE-BAND: AUC 0.60-0.75
- HARD-FAIL: AUC < 0.60 OR trace-enabled subset < 100 programs

Tier hint: Tier-1 conditional (run after Anchor 1 HARD-FAIL; 2-4 hr CPU)

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_code2_bug_detection_rescue_2x_2026-06-10.md
- PP-336 baseline: code2_bug_detection_cpu_v1 HARD_FAIL v558, AUC=0.563, F1=0.539, n=720 (cycle 224)
- PP-311 program shard mechanism: comp26_program_shard_l3_cpu_v1 HARD_PASS, recall=1.000
- PP-333 code composition mechanism: code1_function_compose_cpu_v1 HARD_PASS, correctness=1.000
- PP-335 proof chains: math4_proof_chains_cpu_v1 HARD_PASS, mean=1.000
- Strategy decisions with R1/R2/R3 sketch: d:/AI/hd-instrument/notes/strategy_decisions_2026-06-10.md line 336
- Lift validation rule: [[feedback-method-overclaim-lift-validation]] -- any reported F1 lift must exceed 2*SE ~ 0.038 at n=720; minimum reportable F1 > 0.577; HARD-PASS at 0.70 has clear margin

---

## Contract

exp_dev designs script structure, threshold formula details, queue routing, and test set construction. The HP/MID/HF bands above are research pre-reg; exp_dev may tighten but not loosen without re-routing.

Run order: Anchor 1 (R1) first. Anchor 2 (R3) can run in parallel. Anchor 3 (R6) only if Anchor 1 is MIDDLE-BAND. Anchor 4 (R2) only if Anchor 1 is HARD-FAIL.

Dataset requirement: the 720 n pairs from PP-336 need paired correct versions for R1 and R3. If the dataset does not have paired correct versions, exp_dev should generate them using PP-333 composition mechanism or source from a known Python bug benchmark (BugsInPy, Defects4J Python subset).

## Autonomy declaration

exp_dev has full autonomy on: bundle construction method (contiguous tokenisation vs AST-level), cosine vs Hamming distance choice, threshold optimisation strategy, whether to use train/val split or cross-validation, trace generation approach for R2, and which Python bug benchmark to use if original dataset lacks paired correct versions.

exp_dev does NOT have autonomy on: relaxing HARD-FAIL thresholds below AUC < 0.58 without re-routing to research; skipping Anchor 1 in favour of a more complex mechanism first (cheapest gate runs first per standing protocol).
