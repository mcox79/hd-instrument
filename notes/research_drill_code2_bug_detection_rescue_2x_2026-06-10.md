# Research Drill -- code2 bug detection rescue 2x (2026-06-10)

## HEADLINE

Anomaly-margin approach fails for bug detection because bugs are execution-semantic violations, not retrieval anomalies. Eight substrate-native rescue mechanisms are viable; top-3 (KNOWN-CORRECT-BUNDLE-DIFF R1, EXECUTION-TRACE-BINDING R2, PROPERTY-TEST-VIA-INVARIANT R3) each have P_deflated 0.40-0.50 and share a common form: bind the expected behaviour as a substrate vector, compute Hamming distance to the observed behaviour, threshold on the margin. This is a different signal axis than the anomaly-margin used in PP-336 and is grounded in four independent scientific traditions (predictive coding, crystallographic defect detection, dynamic invariant inference, spectrum-based fault localisation). Cheap decisive test is R1 (30 min CPU). HARD-PASS: F1 >= 0.70 AND AUC >= 0.70 on n=720. HARD-FAIL: F1 < 0.55 or AUC < 0.58 on all three rescue mechanisms (domain remains closed).

---

## 1. Failure diagnosis -- why PP-336 failed at F1=0.539 / AUC=0.563

The PP-336 experiment used an anomaly-margin score: measure the cosine distance from a query bundle to the nearest stored bundle and threshold on distance magnitude. This is a retrieval-anomaly signal. It fails for bug detection for three reasons:

(a) Bugs are not anomalous in the retrieval sense. A buggy program can be structurally very close to correct programs -- off-by-one errors, wrong operator, transposed condition. The HD bundle for a buggy program often lands inside the correct-program cluster. Retrieval margin is near zero.

(b) The signal is symmetric. Distance from correct is the same as distance from buggy. Without a reference to compare against, the substrate cannot tell which direction is "toward correct."

(c) Anomaly-margin conflates rarity with incorrectness. A rare-but-correct program scores high anomaly; a common-but-buggy template scores low anomaly.

The correct signal axis is comparative: expected output vs actual output, or correct trace vs observed trace, or invariant hold vs invariant violation. The substrate can encode this via binding.

---

## 2. Five-stream synthesis

### Stream A -- Biology (predictive coding / expectation-violation)

Humans detect bugs primarily via expectation violation, not via global anomaly. The prefrontal cortex maintains a model of expected program behaviour; the prediction-error signal is generated when observed behaviour deviates from the model. Key evidence:

- Predictive coding (Rao & Ballard 1999, extended in Friston 2005): top-down predictions generate error signals at lower layers. Error = actual - predicted, not |actual|.
- The brain's model-prediction-error signal is DIRECTIONAL -- it encodes what deviated and in what direction, not just that something is unusual.
- Prefrontal studies on code comprehension (Siegmund et al. 2014, Fakhoury et al. 2018) show N400 mismatch events when expected control flow is violated.

Substrate-native translation: the "prediction" is a stored correct-behaviour bundle. The error signal is the Hamming distance between the stored-correct bundle and the observed-behaviour bundle. This maps precisely to R1 (known-correct-bundle-diff).

Calibration note: the neuroscience well supports the error-signal framing, but the direct translation to HD vectors is substrate-novel -- no published precedent on this exact mapping. P_deflated estimate for this explaining the failure and pointing to the right fix: 0.75 (well-supported conceptually, the mechanism translation is the open question).

### Stream B -- Brain (default mode / anomaly detection limits)

The default-mode network is implicated in anomaly detection (Anticevic et al. 2012), but critically, it is not the system responsible for detecting program correctness errors in humans. That is a task-positive network phenomenon involving dorsolateral PFC and anterior cingulate. The default-mode reading is a WRONG PRIOR for PP-336: anomaly-detection is not the right cognitive analogue for bug detection. Bug detection is a comparison task, not an outlier task. This validates the diagnosis in section 1: the anomaly-margin signal was the wrong substrate operation.

Implication: drop pure anomaly-detection framing. All rescue mechanisms should be framed as comparison / invariant-check operations.

### Stream C -- Materials science (defect detection via known-good reference)

X-ray crystallography detects defects by comparing the observed diffraction pattern to the expected pattern from a perfect lattice. Key properties:

- The reference (perfect lattice) is required. Without it, the diffraction pattern of a defective crystal looks indistinguishable from a rare but valid polymorph.
- The difference pattern (observed - reference) is the signal. Small but systematic deviations in specific Bragg peaks indicate specific defect types.
- Spectroscopic defect detection (IR, Raman, NMR) similarly subtracts a known-good reference spectrum and classifies based on the residual.
- PCB defect detection literature (CNN-based reference comparison, IET 2018) achieves 95.7% accuracy via reference subtraction -- dramatically better than anomaly scoring alone.

Substrate-native translation: store a verified-correct program bundle as reference. For an unknown program, compute the elementwise XOR (or Hamming distance vector) against the reference. The presence of systematic bit-pattern deviations indicates semantic mismatch. This is R1. For fine-grained localisation, shard the program into functional units (like PP-311 program shard at 1.000 recall) and compute per-shard difference.

Literature precedent: defect classification by comparing inspection vectors to reference vectors (US patent 12079310, 2024 classification apparatus) confirms reference-comparison is the canonical industrial approach.

### Stream D -- LLM / SE theory (static analysis, property testing, execution traces)

Four established SE methods are directly relevant:

(D1) Dynamic invariant inference (Daikon): monitors execution traces, infers invariants that hold across passing runs, flags violations in new runs. Achieves fault coverage 10-97% depending on application (Ernst et al. 2007). Key limitation: requires a test suite; standalone inference has high false-positive rate. Substrate-native mapping: store likely invariants as HD vectors; test an observed trace bundle against each invariant bundle via inner product. Violation = low cosine to the invariant bundle.

(D2) Spectrum-based fault localisation (SBFL): represents each program element as a vector of pass/fail outcomes across test cases. Ochiai similarity coefficient outperforms Tarantula. The vector representation is directly analogous to a substrate shard. Recent 2024-2025 work adds cosine similarity on LLM-synthesised embeddings for bug localisation (par.nsf.gov 2024 BigData paper).

(D3) Property-based testing (Hypothesis, QuickCheck): generates inputs, checks invariants (expected vs actual output). Agentic PBT (arXiv 2510.09907, 2025) finds bugs across the Python ecosystem. Substrate mapping: generate a set of (input, expected-output) pairs, bind each as substrate vectors, check observed output binding against expected output binding. HD difference = bug signal. This is R3.

(D4) Differential testing: compare two implementations on same input; disagreement = bug (Mokav, arXiv 2406.10375, 2024). Substrate mapping: store two bundles (implementation A output, implementation B output); if HD distance exceeds threshold, flag as disagreement. This is the DIFFERENTIAL-TESTING-VIA-COSINE mechanism.

Key insight from the literature: all four approaches share the property that the bug signal is a COMPARISON, not an anomaly. The exact comparison substrate (reference bundle, invariant bundle, expected-output bundle, or second-implementation bundle) varies by approach, but the structure is the same.

### Stream E -- New substrate-native paths

Eight substrate-native mechanisms are viable. See ranked list in section 4.

The most important new path identified in this drill: EXECUTION-TRACE-BINDING (R2). Represent a correct execution trace as a sequence of HD vectors (one per instruction or basic block), bound together as a trajectory bundle via HD sequential binding (PP-311 program shard mechanism generalises directly). For a test program, generate its trace bundle. Bug = Hamming distance between observed trace bundle and stored correct trace bundle exceeds threshold. This has strong literature support from execution-trace anomaly detection (DIDUCE, grammar-based trace anomaly, DyTrace 2024-2025) and maps to the substrate's demonstrated program-shard capability (PP-311 recall 1.000).

---

## 3. Why anomaly-margin was the wrong signal (mechanism-level)

The anomaly-margin approach computes: score = max_k cosine(query, stored_k). It is a one-sided nearest-neighbour distance.

The correct signal for bug detection is: score = 1 - cosine(observed_bundle, expected_bundle). This is a two-sided comparison: both the observed behaviour AND the expected behaviour must be encoded.

The PP-336 implementation only encoded the programs as bundles (structural form) and used retrieval distance. It did not encode expected outputs, invariants, or correct traces as separate bundles. The rescue mechanisms all require encoding a second bundle (the reference) and computing the distance between the two.

This is exactly the crystallographic reference-comparison insight: you need the perfect lattice diffraction pattern to detect deviations. The substrate already has this capability via PP-333 (program composition at 1.000) and PP-311 (program shard recall 1.000). The missing piece is building the expected-output bundle as a separate anchor.

---

## 4. Ten ranked rescue mechanisms with P_deflated

All P_deflated estimates apply calibration penalty of -0.20 from raw lit-scan estimate. Novel-synthesis P capped at 0.50.

### R1 -- KNOWN-CORRECT-BUNDLE-DIFF (verified-correct comparison)

Mechanism: store a verified-correct version of each program as a substrate bundle. For a test program, build its bundle. Bug signal = Hamming distance (or 1 - cosine) between test bundle and correct bundle, thresholded.

Rationale: directly maps to crystallographic reference comparison. Literature precedent: PCB defect detection via reference subtraction (95.7% accuracy). Substrate capability: PP-333 program composition 1.000, PP-311 program shard recall 1.000. The bundle construction path is validated.

Key requirement: requires a paired (buggy, correct) dataset. For a test set of 720 pairs this is satisfiable if the dataset includes correct versions.

P_deflated: 0.50 (strong conceptual grounding + validated substrate capability; uncertainty is whether the HD distance between structurally close programs that differ only in semantics is large enough to threshold reliably).

Cheap test: 30 min CPU. Compare 360 correct-vs-correct pairs (should have low distance) against 360 buggy-vs-correct pairs (should have higher distance). AUC from this simple threshold = the signal estimate.

HARD-PASS: AUC >= 0.72, F1 >= 0.70 at optimal threshold.
HARD-FAIL: AUC < 0.58 (near-chance; mechanism does not provide signal).
MID: AUC 0.58-0.72 (marginal signal; combine with other rescues).

### R2 -- EXECUTION-TRACE-BINDING

Mechanism: encode the correct execution trace (sequence of operations/values) as an HD trajectory bundle. Encode the test program's execution trace as a separate bundle. Bug = Hamming distance between the two trajectory bundles.

Rationale: maps to DIDUCE / Daikon trace comparison. HD sequential binding (PP-333 uses composition; trace binding is the dynamic analogue). Literature: grammar-based trace anomaly detection (ACM 2024), DyTrace spatial-temporal attention (2025).

Key requirement: requires an interpreter or symbolic executor to generate traces. Adds implementation complexity.

P_deflated: 0.45 (well-supported; implementation complexity is the risk; trace generation is an external dependency).

HARD-PASS: AUC >= 0.75, F1 >= 0.68 (trace comparison should be more discriminative than structural comparison).
HARD-FAIL: AUC < 0.60.

### R3 -- PROPERTY-TEST-VIA-INVARIANT (expected vs actual output binding)

Mechanism: for each test case (input, expected-output), build an expected-output bundle. Run the program under test and build an observed-output bundle. Bug = HD distance between expected-output bundle and observed-output bundle, aggregated across test cases.

Rationale: maps to property-based testing (Hypothesis/QuickCheck). Agentic PBT (arXiv 2510.09907 2025) validates that systematic invariant checking finds bugs at scale. HD binding of (input, output) pairs is natural -- substrate can store these as role-filler bindings.

P_deflated: 0.45 (strong SE literature precedent; substrate-native mapping is clean; uncertainty is whether HD distance between expected/actual outputs is sensitive enough for subtle bugs).

HARD-PASS: F1 >= 0.68, AUC >= 0.70.
HARD-FAIL: F1 < 0.55, AUC < 0.58.

### R4 -- DIFFERENTIAL-TESTING-VIA-COSINE

Mechanism: run the test program and a known-correct reference implementation on the same inputs. Build substrate bundles for each output sequence. Bug = cosine distance between the two output bundles.

Rationale: Mokav (arXiv 2406.10375, 2024) demonstrates execution-driven differential testing finds bugs that static analysis misses. The substrate adds: the comparison is done in HD space (cosine) rather than exact equality, which handles approximate equivalence.

P_deflated: 0.40 (requires a reference implementation -- often not available; when available, this is high-accuracy).

HARD-PASS: AUC >= 0.80 (differential testing should be highly discriminative when reference is available).
HARD-FAIL: AUC < 0.60.

### R5 -- MUTATION-TESTING-VIA-SUBSTRATE-BINDING

Mechanism: generate mutants of a correct program (single-operator mutations). Store each mutant's bundle. A bug is flagged if the test program's bundle is closer to some mutant's bundle than to the correct program's bundle.

Rationale: mutation testing literature (killing mutants with symbolic execution, arXiv 2001.02941). HD similarity to mutant > similarity to correct = the program has a mutation-like change.

P_deflated: 0.38 (computationally expensive to build mutant library; substrate similarity to mutants is noisier than direct comparison to correct).

HARD-PASS: AUC >= 0.68.
HARD-FAIL: AUC < 0.58.

### R6 -- SHARD-LEVEL-BUG-LOCALISATION (per-function comparison)

Mechanism: shard programs into per-function or per-block sub-bundles (PP-311 mechanism). Compare each shard of test program to corresponding shard of correct program. Bug localisation = shard(s) with highest HD distance.

Rationale: extends R1 to sub-program granularity. PP-311 program shard recall 1.000 validates that sharding works. Spectrum-based fault localisation literature shows per-element scoring outperforms whole-program scoring for localisation accuracy.

P_deflated: 0.42 (sharding path validated; localisation claim is stronger than detection claim -- detection is the conservative subgoal).

HARD-PASS: AUC >= 0.70, top-1 localisation accuracy >= 0.55 (correct shard identified).
HARD-FAIL: AUC < 0.58 OR top-1 localisation < 0.30 (no improvement over random).

### R7 -- SYMBOLIC-EXECUTION-VIA-COMPOSITION (path condition binding)

Mechanism: represent symbolic execution paths as HD composition bundles. Each path condition (branch predicate) is bound as a role-filler pair. Bug = path conditions in the test program that are absent from the correct program's path bundle.

Rationale: symbolic execution literature (Cadar et al. KLEE; GNN + symbolic execution for smart contract vulnerability ScienceDirect 2025). Substrate composition is validated for logical chains (PP-335 proof chains at 1.000). Path conditions are a natural role-filler structure.

P_deflated: 0.35 (symbolic execution of arbitrary programs requires an SMT solver; substrate-native path binding is novel; implementation complexity is high).

HARD-PASS: AUC >= 0.70 on programs where path conditions differ between correct/buggy versions.
HARD-FAIL: AUC < 0.58.

### R8 -- TYPE-CHECK-VIA-SHARD-TYPING (type constraint binding)

Mechanism: bind expected type signatures as substrate vectors. For each function call in the test program, build a type-application bundle. Bug = HD distance between expected type bundle and observed type-application bundle.

Rationale: type checking is one of the most reliable static analysis methods. HD vectors for type constraints are a natural extension of substrate's role-filler binding. Conceptually clean but limited to type errors (a subset of bugs).

P_deflated: 0.32 (covers only type bugs, which may be a minority of the PP-336 dataset; substrate-native type binding is novel).

HARD-PASS: AUC >= 0.70 on type-error subset.
HARD-FAIL: Coverage < 20% of bug types in dataset (mechanism is too narrow).

### R9 -- SPEC-BINDING (correct output bound to spec)

Mechanism: bind a formal spec (pre/postconditions) as substrate vectors. For a test program, generate its output given specific inputs and build an output bundle. Bug = output bundle violates the spec bundle (HD distance to spec region exceeds threshold).

Rationale: Design-by-contract (Eiffel, Dafny); substrate can store spec as binding of (precondition, postcondition) role-filler pairs. PP-264 (paraconsistent logic 1.000) and PP-266 (belief revision 1.000) suggest substrate handles logical constraints.

P_deflated: 0.35 (requires formal specs -- rarely available; when available, detection should be high precision, lower recall).

HARD-PASS: AUC >= 0.75 on programs with formal specs.
HARD-FAIL: Spec coverage < 15% of dataset.

### R10 -- DAIKON-BUNDLE (inferred invariant as HD vector)

Mechanism: run Daikon on passing test cases to infer likely invariants. Encode each invariant as a substrate bundle. For a new program execution, check each invariant bundle via inner product. Bug = number of invariant violations above threshold.

Rationale: Daikon system (Ernst et al. 2007) provides validated invariant inference. Fault coverage 10-97% across applications. Substrate adds: invariant representation as HD vectors enables approximate matching (tolerates minor deviations) rather than exact boolean checks.

P_deflated: 0.38 (Daikon is a mature tool with validated precision; substrate-native invariant bundles are novel; main risk is Daikon's known false-positive rate for invariants from small test suites).

HARD-PASS: AUC >= 0.68, F1 >= 0.60.
HARD-FAIL: False positive rate > 40% (Daikon false-positives dominate).

---

## 5. Cheap decisive test

**R1 known-correct-bundle-diff is the cheapest decisive test.**

Implementation:
1. For each of the 720 program pairs, build two bundles: B_correct (from the verified-correct program text) and B_test (from the program under test).
2. Compute HD distance = 1 - cosine(B_correct, B_test) for each pair.
3. Compute AUC and F1 over the 720 pairs using this single-feature classifier.
4. If AUC >= 0.72: R1 is viable, proceed to full implementation.
5. If AUC < 0.58: signal is absent, move to R2 (trace-based).

Requires: paired (buggy, correct) data. If PP-336 dataset does not have paired correct versions, use code2_correct_v1 corpus or generate correct versions via PP-333 composition mechanism.

Estimated cost: 30 min CPU, n=720.

---

## 6. Falsifiable predictions

### HARD-PASS thresholds

- R1: AUC >= 0.72 AND F1 >= 0.70 on n=720 pairs. This would demonstrate that known-correct-bundle HD distance provides reliable bug signal. Product implication: substrate-native code correctness checking without LLM.
- R2: AUC >= 0.75 AND F1 >= 0.68 on trace-paired subset. This would demonstrate execution-semantic comparison.
- R3: AUC >= 0.70 AND F1 >= 0.68 on property-test subset.

### HARD-FAIL thresholds

- ALL three of R1/R2/R3 fail at AUC < 0.58: domain remains closed. Bug detection is not achievable via substrate-native comparison at this N and architecture. Requires LLM-hybrid.
- R1 fails AND R2 requires SMT solver: substrate-only path is not viable; route to LLM-integrated approach.

### Calibration note

P_deflated values in this note are already deflated by -0.20 from raw lit-scan estimates. Novel-synthesis paths (R1, R2, R3 with substrate-specific binding) are capped at 0.50. Do not further deflate without additional negative evidence.

---

## 7. Cross-thread synthesis

**PP-263 -- meta-substrate (1.000 accuracy):** substrate can report its own knowledge state. This is relevant for R3: substrate can flag when its expected-output bundle for a given input has low confidence (uncertainty-aware bug detection).

**PP-311 -- program shard recall 1.000:** the sharding mechanism is validated. R6 (shard-level localisation) can be built directly on this path.

**PP-333 -- code composition 1.000:** substrate composes programs correctly. The same bundle-construction mechanism used for composition can build the correct-program bundle for R1. This is a direct capability transfer.

**PP-335 -- proof chains 1.000:** substrate chains deductive proofs. R9 (spec binding) can use proof-chain bundles to represent pre/postconditions.

**PP-275 -- LVH-274 struct-align noise-level lift:** the [[feedback-method-overclaim-lift-validation]] rule applies here. Any rescue mechanism reporting F1 improvement must show lift > 2*SE over the PP-336 baseline (F1=0.539). At n=720, SE ~ 0.019. Minimum reportable lift: F1 > 0.577. HARD-PASS threshold of 0.70 provides a clear margin above this noise floor.

**Anomaly-margin approach (PP-336 confirmed negative):** the negative result is structurally informative. It eliminates one class of approach (retrieval-distance-as-correctness-signal) and redirects to comparison-based approaches. This is consistent with the crystallographic insight: without a reference, you cannot detect a defect.

---

## 8. Substrate-product implications

A working bug detection capability (R1 or R2 at HARD-PASS) would be a commercial differentiator. Current product strengths are in storage, retrieval, and composition. Bug detection adds a correctness-checking layer that does not require an LLM call.

Product claim if R1 HP: "substrate detects code bugs by comparison to verified-correct reference bundles, with AUC >= 0.72 at 30-minute training cost per code domain."

This integrates with PP-333 (program composition) and PP-311 (program shard recall) to form a code intelligence stack: compose programs, shard them, check correctness against reference. Each step is substrate-native.

The LLM-hybrid path remains open: if substrate-native detection (R1/R2/R3) reaches only mid-band (AUC 0.58-0.72), a lightweight LLM call to classify ambiguous cases could push to HARD-PASS territory. This is cheaper per-query than LLM-only and retains substrate's provenance properties.

---

## 9. Citations (verified from lit-scan)

1. Tracking down software bugs using automatic anomaly detection -- Hangal & Lam, ICSE 2002, via ACM DL (dl.acm.org/doi/10.1145/581339.581377)
2. Grammar-based anomaly detection of microservice execution traces -- ACM/SPEC ICPE 2024 (dl.acm.org/doi/10.1145/3629527.3651844)
3. The Daikon system for dynamic detection of likely invariants -- Ernst et al. 2007, Science of Computer Programming (semanticscholar.org paper a99575d60)
4. Invalidator: Automated Patch Correctness Assessment via Semantic and Syntactic Reasoning -- arXiv 2301.01113 (2023)
5. Mokav: Execution-driven Differential Testing with LLMs -- arXiv 2406.10375 (2024)
6. Agentic Property-Based Testing: Finding Bugs Across the Python Ecosystem -- arXiv 2510.09907 (2025)
7. Killing Stubborn Mutants with Symbolic Execution -- arXiv 2001.02941 (2020)
8. Smart Contract Vulnerability Detection Based on Symbolic Execution and GNNs -- ScienceDirect 2025
9. CNN-based reference comparison method for classifying bare PCB defects -- IET Journal of Engineering, Wei et al. 2018 (ietresearch.onlinelibrary.wiley.com)
10. An Empirical Study of False Negatives and Positives of Static Code Analyzers -- arXiv 2408.13855 (2024)
11. CC2Vec: Combining Typed Tokens with Contrastive Learning for Code Clone Detection -- FSE 2024 (wu-yueming.github.io/Files/FSE2024_CC2Vec.pdf)
12. MSSA: multi-stage semantic-aware neural network for binary code similarity detection -- PMC 2025 (pmc.ncbi.nlm.nih.gov/articles/PMC11784775)
13. Defect classification apparatus (comparison inspection vector to reference vector) -- US Patent 12079310, 2024
14. Improving Spectrum-Based Fault Localization -- ISSTA 2023 (dl.acm.org/doi/10.1145/3597926.3598148)
15. PatchGuru: Patch Oracle Inference from NL Artifacts with LLMs -- arXiv 2602.05270 (2026)
16. Predictive coding (foundational) -- Rao & Ballard, Nature Neuroscience 1999; Friston, Phil Trans R Soc 2005
17. AnomalyGen: Automated Semantic Log Sequence Generation for Anomaly Detection -- arXiv 2504.12250 (2025)
18. FPA-FL: Static Fault-Proneness Analysis in Statistical Fault Localization -- arXiv 1712.03359

Verified citations: 18. All URLs confirmed reachable or are well-indexed academic identifiers.

---

## 10. Pre-registration summary table

| Rank | Mechanism | P_deflated | HARD-PASS | HARD-FAIL | Cost |
|------|-----------|------------|-----------|-----------|------|
| R1 | KNOWN-CORRECT-BUNDLE-DIFF | 0.50 | AUC>=0.72, F1>=0.70 | AUC<0.58 | 30 min CPU |
| R2 | EXECUTION-TRACE-BINDING | 0.45 | AUC>=0.75, F1>=0.68 | AUC<0.60 | 2-4 hr CPU |
| R3 | PROPERTY-TEST-VIA-INVARIANT | 0.45 | AUC>=0.70, F1>=0.68 | AUC<0.58 | 1-2 hr CPU |
| R4 | DIFFERENTIAL-TESTING-VIA-COSINE | 0.40 | AUC>=0.80 | AUC<0.60 | 1 hr CPU |
| R5 | MUTATION-TESTING-VIA-SUBSTRATE | 0.38 | AUC>=0.68 | AUC<0.58 | 4+ hr CPU |
| R6 | SHARD-LEVEL-LOCALISATION | 0.42 | AUC>=0.70, top1>=0.55 | AUC<0.58 | 45 min CPU |
| R7 | SYMBOLIC-EXECUTION-VIA-COMPOSITION | 0.35 | AUC>=0.70 | AUC<0.58 | 4+ hr (SMT req) |
| R8 | TYPE-CHECK-VIA-SHARD-TYPING | 0.32 | AUC>=0.70 | Coverage<20% | 45 min CPU |
| R9 | SPEC-BINDING | 0.35 | AUC>=0.75 | Coverage<15% | 2+ hr (spec req) |
| R10 | DAIKON-BUNDLE | 0.38 | AUC>=0.68, F1>=0.60 | FP rate>40% | 3+ hr |

---

## next-drill candidate

Mechanism: if R1 returns mid-band (AUC 0.58-0.72), drill the SHARD-LEVEL-LOCALISATION (R6) extension -- per-function bundle comparison may provide cleaner signal than whole-program comparison, analogous to SBFL per-element scoring outperforming whole-program scoring. Field: program analysis + materials science (reference subtraction at sub-component granularity).
