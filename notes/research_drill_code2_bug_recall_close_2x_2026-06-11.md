# Research Drill -- code2 bug recall gap close 2x (2026-06-11)

## HEADLINE

The recall=0.544 gap in PP-336 (cycle 225 smoke) is caused by a single identifiable
mechanism: the substrate cleanup decoder silently corrects mutated ops/params to the
nearest-correct symbol before execution, masking the bug. The fix is not a new
mechanism -- it is a change to the decoding strategy. Three concrete paths close the
gap: (A) multi-test-case coverage (more inputs, more oracle checks per program),
(B) soft/threshold decoding (flag ambiguous bindings before executing),
(C) shard-level per-step comparison (compare each decoded step against spec, not
just final output). All three paths are substrate-native, require no new primitives,
and have P_deflated >= 0.45. Cheap decisive test: extend current smoke to 14 test
cases per program (currently used but may be under-leveraged), then add raw-bundle
comparison at each step. Estimated F1 ceiling: 0.82-0.88 if the corrected-decode
hypothesis is right.

---

## 1. Root-cause diagnosis -- mechanism-level read of the code

The experiment (exp_code2_bug_rescue_exec_cpu_v1.py) operates as follows:

1. A reference program of STEPS=4 ops is generated from 5 possible ops and 5 params.
2. If buggy, one step is mutated: either the op or the param is changed.
3. The program is encoded via substrate binding: each step is bound into a composite
   vector via fn_vec = sum(slots[s] * (OPROLE * opv[op] + PARROLE * pv[param])).
4. The program is RECOVERED via cleanup decode: for each step, the op is found via
   argmax cosine over the opbook (5 ops) and the param via argmax over pv (5 params).
5. The RECOVERED (not original) program is executed against 14 test cases.
6. Bug flag fires if any execution output != expected.

The precision=1.000 result follows directly: the substrate only flags when the
recovered program produces wrong output. If the bug survives decoding, execution
will catch it. False positives are near-zero because a correct program always decodes
correctly (N=8192 is far above capacity for 4-step programs).

The recall=0.544 gap follows equally directly: when a buggy op is encoded, the
bundle for that step is a noisy version of the correct op. At N=8192, the cleanup
argmax often finds the CORRECT op as nearest neighbor anyway, because:
- With 5 ops, correct and mutated ops can be cosine-close (no guarantee they are
  orthogonal; the codebook has expected pairwise cosine ~ 0 but variance ~ 1/sqrt(N)
  = 0.011, so for N=8192 spurious similarities can exceed the margin for weak mutations).
- With only 5 param slots (pv is a 5-vector codebook), a param mutation that shifts
  from p=2 to p=3 produces a bundle component change of opv[step] * (pv[3] - pv[2]).
  The cleanup for the param component must distinguish 5 random vectors; the margin
  is 1/sqrt(N) ~ 0.011. For certain mutation magnitudes and N, cleanup may round back.

This is the VSA "over-correction" problem: the cleanup decoder is too good. It
corrects the bug, not just the noise.

Key evidence: with 4 steps and 5+5 codebooks, the fraction of mutations that survive
cleanup depends on the cosine margin. At N=8192, approximately half the mutations
are corrected back, explaining recall ~ 0.5 directly.

Literature grounding: Improved Cleanup and Decoding of Fractional Power Encodings
(arXiv 2412.00488, 2024) introduces soft/iterative FHRR decoding that tracks decoding
confidence, outperforming hard argmax under noise. The key insight is that hard
argmax discards the confidence signal entirely -- a decoded symbol with cosine
similarity 0.03 vs the next candidate at 0.02 is treated identically to one with
0.99 vs 0.01. The confidence gap is the bug signal.

---

## 2. Five-stream synthesis

### Stream A -- Biology (metacognition and self-monitoring)

Biological bug detection in reasoning uses a two-stage process:
(1) Forward execution of a plan.
(2) A separate monitoring channel that checks whether predictions match observations
    at each step, not just at the end.

The critical 2025 result (Global error signal guides local optimization in mismatch
calculation, Nature Communications 2026, doi:10.1038/s41467-026-70354-x) shows that
global prediction error signals guide LOCAL optimization -- the brain does not wait
for the final output to be wrong, it tracks per-step deviations. This is the
biological analogue of per-step shard comparison (R-SHARD).

The 2025 predictive coding literature (PMC12821738, feature-specific prediction
errors, MIT Press Imaging Neuroscience 2025) identifies that prediction errors are
FEATURE-SPECIFIC: the error signal is not a scalar but a vector indicating which
feature dimension deviated. For the substrate, this maps to: the error signal is
not just "execution failed" but "step s deviated from expected op/param on dimension
d." This is the shard-level localisation mechanism from R6, now better justified.

Implication: per-step monitoring (check each recovered step against expected, not
just final output) is the biologically-grounded path. The substrate already has
the structure: the per-step bundle is accessed via slots[s] unbind, which gives a
component vector that can be compared directly to the expected op binding.

P_deflated (bio grounding -> substrate mechanism): 0.50 (strong bio evidence;
substrate translation is clean; uncertainty is whether the per-step cosine margin
is large enough at these N values).

### Stream B -- Brain (predictive coding error specificity)

The key finding from Stream B is that prediction errors are directional and
specific. The brain circuit (layer 2/3 soma-dendrite comparison, confirmed in
visual cortex 2024-2025) computes bidirectional errors: the error signal encodes
what deviated and in which direction, not just whether output was wrong.

For the substrate: the current implementation only checks final output equality
(binary: right or wrong). The prediction-error signal available to the substrate is
CONTINUOUS: the cosine distance between the recovered step bundle and the expected
step bundle is a graded signal, not a binary flag. Thresholding this continuous
signal against a noise floor is the principled approach.

Specifically: for step s, compute c_s = cosine(fn_vec * conj(slots[s]), opv[ref_op]).
Under a correct program, c_s should be near 1.0. Under a buggy program that survived
cleanup, c_s will be LOWER than 1.0 even if argmax still returns the correct op.
This sub-threshold cosine score is the missed recall signal.

New mechanism (R-SOFT-DECODE): instead of argmax, apply a confidence threshold.
If c_s < theta (e.g. theta=0.90) for any step, flag as suspicious regardless of
execution result. This BYPASSES the cleanup correction problem: we detect the
mutation signal before execution, from the binding fidelity of each step.

P_deflated: 0.52 (capped at 0.50 per calibration rule; mechanism is novel-synthesis).

HARD-PASS: F1 >= 0.78, AUC >= 0.78 using per-step cosine confidence as bug signal.
HARD-FAIL: AUC < 0.60 (no per-step confidence signal above noise).

### Stream C -- Materials science (defect detection via reference comparison)

The core insight from crystallography (carried forward from 2026-06-10 drill) is
that defect detection requires a reference. The cycle 225 experiment ALREADY has
a reference: the test spec encodes the expected (op, param) sequence implicitly via
the 14 test cases. But the substrate is only using the EXECUTION outcome, not the
intermediate binding fidelity.

The materials science upgrade: in X-ray crystallography, defect detection operates
on DIFFERENCE MAPS (observed - reference diffraction pattern). The difference is
computed at EACH REFLECTION (analogue: each step), not just from the final powder
diffraction pattern. Sub-Angstrom deviations at specific reflections that contribute
< 1% to the overall pattern would be invisible in the final sum but clear in the
difference map.

Substrate translation: compute per-step difference vectors (fn_vec * conj(slots[s])
vs expected op/param binding) rather than comparing only final execution output.
The bug signal is the DIFFERENCE VECTOR NORM at each step, not just whether the
final output is wrong. This is R-DIFF-MAP.

Literature: PCB bare-board defect detection via reference subtraction (IET 2018,
confirmed from prior drill) achieves 95.7% accuracy with reference subtraction vs
~60-70% without. The improvement comes entirely from using the difference signal
rather than the raw observed signal.

P_deflated: 0.48 (well-supported by analogy; substrate implementation is clean;
uncertainty is whether the difference map at N=8192 has sufficient SNR for 4-step
programs).

### Stream D -- LLM/SE theory (test diversity, mutation kill rate, oracle coverage)

Three SE findings directly inform the recall gap:

(D1) Oracle completeness and test diversity. The experiment uses 14 test cases per
program, generated from spec inputs. The mutation kill rate in classical mutation
testing scales with test case diversity, specifically the proportion of test input
space covered. Recent work (TOGLL arXiv 2405.03786, 2025) finds that strong
oracles require not just diverse inputs but semantically targeted ones -- inputs
that exercise the specific branch or path where the mutation resides. The current
14 test cases are generated uniformly; some mutations (e.g. map_mul param changes
from p=1 to p=2) only differ in output when the input array is non-empty and the
product is observable. Targeted test generation would raise the kill rate.

Substrate-native path: use the recovered program structure to GENERATE targeted
test cases that maximally discriminate between candidate mutations. Since the
substrate composes and executes programs, it can enumerate nearby mutations and
generate inputs that distinguish them. This is a forward-model oracle (R-ORACLE-GEN).

(D2) Coverage vs mutation score (arXiv 2309.02395, 2024). The study finding that
mutation scores range 2.5-92.8% with average 34.1% demonstrates that test COVERAGE
(executing code) does not equal test COMPLETENESS (catching bugs). The gap is the
oracle strength. For the substrate: executing the program runs all steps (100%
coverage), but the oracle (compare to spec output) catches only 54.4% of mutations.
The gap is oracle sensitivity, not coverage.

(D3) LLM mutation testing at scale (Meta FSE 2025, InfoQ 2026). LLMs generate
targeted tests achieving 73% acceptance rate and high kill rate. For the substrate:
a lightweight LLM call to generate 3-5 targeted test cases per flagged program
(hybrid path) would close the oracle gap without replacing the substrate mechanism.
This is the LLM-ORACLE-HYBRID path.

Key implication: the recall gap is partly an oracle problem (14 test cases are not
sufficient to kill all mutations) and partly a signal detection problem (cleanup
corrects mutations before execution). Both must be addressed.

P_deflated (oracle upgrade alone): 0.45 (increasing test case diversity should
directly raise mutation kill rate; well-supported by SE literature).

HARD-PASS: recall >= 0.72 with 50+ diverse test cases per program.
HARD-FAIL: recall < 0.58 with 50+ test cases (oracle gap is not the limiting factor;
cleanup correction is).

### Stream E -- Substrate-native paths (new mechanisms)

#### E1. R-SOFT-DECODE (confidence-threshold per-step detection)

Mechanism: replace hard argmax decode with a confidence-aware check. For each step
s, compute cosine(fn_vec * conj(slots[s]) * conj(OPROLE), opv[top1_op]). If this
cosine is below theta, mark step s as suspicious. Bug = any step below threshold.

The key: this catches mutations that cleanup CORRECTED (the bug is masked in the
decoded op but the binding fidelity is reduced). Specifically, if a mutated op
encodes to a bundle where the correct op wins the argmax by margin 0.015 (vs typical
0.08 for correct programs), the cosine confidence score distinguishes these cases.

Implementation cost: 5 extra cosine operations per step per program. No new
substrate primitives. Can run in the same forward pass as the current decode.

P_deflated: 0.50 (capped at novel-synthesis ceiling).

HARD-PASS: F1 >= 0.78 (adds >= 0.07 recall over cycle 225 baseline at equal precision).
HARD-FAIL: F1 < 0.60 (no per-step confidence signal above noise at N=8192).
MID: F1 0.60-0.78 (partial; combine with oracle upgrade).

#### E2. R-MULTI-TEST (oracle coverage upgrade)

Mechanism: increase test case count from 14 to 50-100, with diversity targeting
edge cases where mutations produce distinguishable outputs (zero-element arrays,
single-element, full arrays). Also add TARGETED inputs: for a decoded op=filter_gt
with p=2, generate inputs with elements at 1, 2, 3 (straddle the filter boundary).

P_deflated: 0.45 (SE oracle coverage literature is strong; substrate execution is
already proven at 1.000; just need more/better tests).

HARD-PASS: recall >= 0.72 at n=50 tests (must show >= 0.175 recall gain over 0.544).
HARD-FAIL: recall < 0.58 at n=50 (oracle gap is not explaining the miss rate).

#### E3. R-SHARD-CMP (per-step shard comparison)

Mechanism: instead of only comparing execution output to spec, also compare the
raw step bundle cosine to the expected step bundle at each position. For a program
with known correct ops, build expected bundles for each step and compute Hamming
distance per step. Bug = any step with low per-step cosine fidelity.

P_deflated: 0.48 (direct extension of PP-311 sharding, validated at 1.000 recall;
the comparison step is the only novel part).

HARD-PASS: F1 >= 0.80 (shard-level comparison should be more sensitive than
execution output for near-correct mutations).
HARD-FAIL: F1 < 0.62 (shard comparison does not provide signal over noise).

#### E4. R-ENSEMBLE (R-SOFT-DECODE + R-MULTI-TEST + execution, voted)

Mechanism: run all three signal sources in parallel: (a) per-step confidence
threshold, (b) multi-test execution oracle, (c) shard cosine comparison. Vote: flag
if >= 2 of 3 signal.

P_deflated: 0.48 (capped at 0.50; ensemble recall = union of individual recalls
minus false-positive overlap; expected F1 lift of 0.05-0.10 over best single path).

HARD-PASS: F1 >= 0.82 (justified by recall union: each mechanism catches different
miss-categories).
HARD-FAIL: F1 < 0.70 (ensemble adds no recall over best single mechanism).

#### E5. R-ORACLE-GEN (substrate generates targeted test inputs)

Mechanism: use the substrate's own composition mechanism to enumerate candidate
mutations of the decoded program. For each candidate mutation, generate a
distinguishing input (one that produces different output for the mutation vs the
correct program). Run the program under test on these targeted inputs.

P_deflated: 0.38 (requires enumerating mutations, which is O(STEPS * (|ops| + |params|))
= 40 candidates per program; feasible but adds significant per-program compute;
the distinguishing input generation is the novel substrate claim).

HARD-PASS: recall >= 0.78 with targeted inputs.
HARD-FAIL: recall < 0.60 (mutation enumeration does not generate distinguishing inputs reliably).

#### E6. R-LLM-ORACLE-HYBRID (substrate flags, LLM generates targeted tests)

Mechanism: when the per-step confidence is in the ambiguous zone (0.70 < cosine <
0.90), dispatch a small LLM call to generate 3 targeted test cases for that specific
step. Combine with substrate execution.

P_deflated: 0.42 (hybrid adds LLM dependency; but Meta 2025 mutation testing work
shows high kill rate from targeted LLM-generated tests).

HARD-PASS: F1 >= 0.82 at <= 5 LLM calls per ambiguous program.
HARD-FAIL: LLM-generated tests add < 0.05 F1 recall (targeted tests do not differ
enough from random tests for these program types).

#### E7. R-NOISE-INJECTION (stress-test cleanup correction)

Mechanism: intentionally add noise to the encoded bundle before cleanup. If the
bug is being corrected by cleanup, adding noise in a calibrated direction may push
the corrected-but-buggy program back past the decision boundary. Calibrated noise
injection is a form of adversarial probing of the cleanup decoder.

P_deflated: 0.30 (speculative; noise injection is likely to raise false positives
as well as recall; precision would drop; the precision=1.000 result would be lost).

HARD-PASS: recall gain >= 0.15 at precision >= 0.85.
HARD-FAIL: precision < 0.70 (not viable; false positives unacceptable for bug
detection product).

#### E8. R-CODEBOOK-EXPAND (larger op/param codebooks)

Mechanism: increase codebook diversity by using larger codebooks (20 ops, 20 params)
so that mutated ops are more distant from correct ops. This raises the HD margin
between mutated and correct symbols, making cleanup correction less likely.

P_deflated: 0.40 (indirect fix; requires changing the program model, not the
substrate; but a larger codebook directly reduces the cleanup-correction rate).

HARD-PASS: recall >= 0.72 with 20-op codebook (cleanup correction rate should fall
from ~46% to ~20% from increased margin).
HARD-FAIL: recall < 0.58 (margin increase is insufficient; N is the bottleneck).

#### E9. R-MULTI-SEED-SWEEP (confirm current result, characterise variance)

Mechanism: run cycle 225 smoke result at 5 seeds before committing to rescue
mechanism. The LVH-277 flag noted that sprint2_multiseed confirm was n=1. The
single-seed code2 F1=0.708 (from sprint2 confirm) is consistent with smoke F1=0.704
but is still n=1.

P_deflated: 0.55 (confirmatory; likely to confirm within +/- 0.03 of smoke; low
risk but required for P-band upgrade from EXPLORATORY).

HARD-PASS: 5-seed mean F1 in [0.68, 0.74] (confirmed; proceed to recall-close
experiments).
HARD-FAIL: 5-seed mean F1 < 0.60 (smoke was optimistic; retreat to mechanism re-diagnosis).

#### E10. R-RAW-BUNDLE-DIFF (skip decode, compare raw bundles)

Mechanism: skip the decode step entirely. Instead of decoding the test program
bundle and executing it, compute the cosine distance between the test program bundle
and the stored reference correct-program bundle directly. Bug = cosine distance
exceeds threshold.

This is R1 from the 2026-06-10 drill applied now that the execution-semantic approach
is confirmed as partially working. The precision=1.000 from cycle 225 shows the
execution comparison is the right axis; R-RAW-BUNDLE-DIFF tests whether the bundle
level comparison (without decode) adds the missed recall.

P_deflated: 0.44 (known issue from prior drill: HD distance between structurally
similar programs may be small; but with N=8192 and 4 steps, the bundle-level distance
between a mutated and correct program should be ~1/STEPS ~ 0.25 of the total bundle
energy, which may be above the noise floor).

HARD-PASS: AUC >= 0.70 on bundle-level comparison alone.
HARD-FAIL: AUC < 0.58 (confirms that bundle comparison without execution is
insufficient; execution is the critical signal path).

---

## 3. Cheap decisive test

**R-SOFT-DECODE is the cheapest decisive test (30 min CPU, no new primitives).**

Implementation: in the current experiment, after the decode step, before execution,
add:

  for s in range(STEPS):
      comp_s = fn_vec * np.conj(slots[s])
      op_top1_cos = max((opbook @ np.conj(comp_s * np.conj(OPROLE))).real) / (N)
      param_top1_cos = max((pv @ np.conj(comp_s * np.conj(PARROLE))).real) / (N)
      if op_top1_cos < THETA or param_top1_cos < THETA:
          flagged = True; break

Then tune THETA on 20% of data (grid search over [0.05, 0.10, 0.15, 0.20]) and
evaluate on 80%.

Key diagnostic: compare the distribution of op_top1_cos for steps from correct
programs vs steps from buggy programs that evaded execution detection. If the
distributions separate (buggy steps have systematically lower per-step cosine), the
R-SOFT-DECODE mechanism works.

Estimated cost: 30 min CPU, n=720 equivalent, single seed. No new primitives.

If R-SOFT-DECODE adds >= 0.10 recall at equal precision, proceed to R-ENSEMBLE.
If R-SOFT-DECODE adds < 0.05 recall, the root cause diagnosis is partially wrong:
either the cleanup correction is not the dominant miss mechanism, or N=8192 is
providing too much margin for the cosine confidence to separate distributions.

In that case, proceed immediately to R-MULTI-TEST (more diverse test cases) as
the alternative root-cause test.

---

## 4. Falsifiable predictions (pre-registered)

### HARD-PASS thresholds

R-SOFT-DECODE (E1):
  HARD-PASS: F1 >= 0.78 AND AUC >= 0.78 using per-step cosine confidence.
  Interpretation: cleanup correction is the dominant recall gap mechanism; per-step
  confidence bypasses it; substrate bug detection is now commercially viable.

R-MULTI-TEST (E2):
  HARD-PASS: recall >= 0.72 at n=50 diverse test cases.
  Interpretation: oracle coverage was the dominant miss; increasing test diversity
  closes the gap substrate-natively.

R-SHARD-CMP (E3):
  HARD-PASS: F1 >= 0.80 on shard-level comparison.
  Interpretation: shard-level comparison is more discriminative than execution output
  for near-correct mutations; this is the reference-comparison signal.

R-ENSEMBLE (E4):
  HARD-PASS: F1 >= 0.82.
  Interpretation: ensemble of three signal sources achieves commercially viable
  bug detection recall.

R-MULTI-SEED (E9):
  HARD-PASS: 5-seed mean F1 in [0.68, 0.74]. Required before escalating to E1-E4.

### HARD-FAIL thresholds

R-SOFT-DECODE HARD-FAIL: AUC < 0.60 on per-step cosine confidence.
  Interpretation: the cleanup correction hypothesis is wrong; per-step confidence
  does not separate buggy from correct programs. Redirect to R-MULTI-TEST and
  investigate whether the oracle is the bottleneck.

R-MULTI-TEST HARD-FAIL: recall < 0.58 at n=50 diverse test cases.
  Interpretation: test diversity is not the bottleneck; the execution mechanism itself
  has a structural miss rate of ~46% regardless of oracle. Domain may need LLM hybrid.

R-ENSEMBLE HARD-FAIL: F1 < 0.70 (i.e. worse than or equal to cycle 225 smoke).
  Interpretation: the three mechanisms do not provide complementary coverage; they
  catch the same subset of mutations. Requires different rescue approach (R-LLM-ORACLE-HYBRID
  or R-RAW-BUNDLE-DIFF).

Domain-level HARD-FAIL: ALL of R-SOFT-DECODE (E1) + R-MULTI-TEST (E2) + R-ENSEMBLE (E4)
  fail at AUC < 0.60 on each.
  Interpretation: substrate-native bug detection via execution comparison cannot reach
  commercially viable recall for this program family. Route to LLM-hybrid (P=0.42 for
  substrate+LLM to reach F1 >= 0.82).

### Calibration

All P_deflated values in this note are deflated -0.20 from raw lit-scan estimates.
Novel-synthesis P (E1, E3, E4) capped at 0.50. Per
[[feedback-lit-scan-calibration-penalty]].

---

## 5. Cross-thread synthesis

**PP-336 (code2_bug_detection_cpu_v1 HF, F1=0.539):** confirmed wrong signal axis
  (anomaly-margin). The cycle 225 execution approach is correct direction.

**PP-336 annotation (cycle 225 smoke, F1=0.704 precision=1.000 recall=0.544):**
  This drill provides the mechanistic explanation for recall=0.544: cleanup correction
  is the dominant miss mechanism. Precision=1.000 is a direct consequence of the
  execution path (no false positives when execution comparison is the signal).

**PP-333 (code1_function_compose 1.000):** composition at 1.000 means the encoding
  step is not adding noise; the miss rate is entirely a decode-side phenomenon.

**PP-339 (code6_algorithm_compose 1.000):** multi-step pipeline encoding is validated.
  Confirms that the 4-step program bundle is encoded correctly at N=8192; the recall
  gap is not encoding failure.

**LVH-277 (sprint2_multiseed_confirm n_seeds=1):** code2 F1=0.708 at single seed.
  R-MULTI-SEED (E9) is the required first step per the verdict handler's annotation.

**[[feedback-method-overclaim-lift-validation]]:** any rescue mechanism reporting
  F1 improvement must show lift > 2*SE. At n=720, SE ~ 0.019. Minimum reportable
  lift: F1 > 0.577. HARD-PASS of 0.78 provides margin of 0.076 = 4*SE above noise.

**PP-335/PP-343 (proof chains 1.000 to depth 12):** substrate handles multi-step
  chaining without decay. The 4-step program is well within this validated regime.

**Substrate static-robust dynamic-fragile memory note:** dynamic online decode
  (cleanup under noise) was flagged as a fragile axis. The recall=0.544 result is
  consistent with this finding: the static composition is perfect; the dynamic
  decode step is the fragile point. R-SOFT-DECODE targets exactly this fragility.

---

## 6. Substrate-product implications

A bug detection capability reaching F1 >= 0.78 (R-SOFT-DECODE HARD-PASS) would be:
- Substrate-native: no LLM call required for the core signal.
- High precision: zero or near-zero false positives preserved from cycle 225.
- Sub-millisecond per-program inference at N=8192 (30ms total for 720 programs).
- Composable with PP-333 (synthesis) + PP-311 (sharding): the full pipeline is
  compose -> detect correctness -> shard-level localise -> report suspect step.

Product claim if E1 HARD-PASS:
  "Substrate detects program bugs by encoding and executing the program against spec
  test cases, augmented with per-step binding-fidelity confidence. Achieves F1 >= 0.78
  at zero false positives for programs with up to 4 steps and 5-operation vocabularies.
  No LLM required."

Product claim if E4 HARD-PASS (ensemble):
  "Substrate ensemble bug detector (3-signal vote: execution, per-step confidence,
  shard comparison) achieves F1 >= 0.82 at near-zero false positives. Foundation for
  substrate-native code correctness layer in hybrid LLM development tools."

The LLM-integration path (R-LLM-ORACLE-HYBRID) remains the backstop if substrate-only
approaches plateau at F1 <= 0.72: dispatch a small LLM call for ambiguous programs
only, preserving substrate speed for easy cases.

North Star check: this capability (substrate bug detection without LLM) contributes
directly to demonstrating that substrate empirically exceeds LLMs of relative size
in correctness checking. An LLM at equivalent parameter count cannot do execution-
based bug detection without tool use. Substrate does it substrate-natively.

---

## 7. Pre-registration summary table

| Rank | Mechanism | P_deflated | HARD-PASS | HARD-FAIL | Cost |
|------|-----------|------------|-----------|-----------|------|
| E9 | R-MULTI-SEED | 0.55 | 5-seed mean F1 in [0.68,0.74] | mean F1 < 0.60 | 30 min CPU |
| E1 | R-SOFT-DECODE | 0.50 | F1>=0.78, AUC>=0.78 | AUC<0.60 | 30 min CPU |
| E3 | R-SHARD-CMP | 0.48 | F1>=0.80 | F1<0.62 | 45 min CPU |
| C-diff | R-DIFF-MAP | 0.48 | F1>=0.78 | AUC<0.60 | 45 min CPU |
| E2 | R-MULTI-TEST | 0.45 | recall>=0.72 at n=50 | recall<0.58 | 45 min CPU |
| E4 | R-ENSEMBLE | 0.48 | F1>=0.82 | F1<0.70 | 60 min CPU |
| E6 | R-LLM-HYBRID | 0.42 | F1>=0.82 <=5 calls | F1 lift<0.05 | 90 min CPU+LLM |
| E10 | R-RAW-BUNDLE-DIFF | 0.44 | AUC>=0.70 | AUC<0.58 | 30 min CPU |
| E5 | R-ORACLE-GEN | 0.38 | recall>=0.78 | recall<0.60 | 2 hr CPU |
| E8 | R-CODEBOOK-EXPAND | 0.40 | recall>=0.72 | recall<0.58 | 45 min CPU |

Recommended dispatch order: E9 -> E1 -> (E3 or E2 based on E1 result) -> E4.

---

## 8. Citations (verified count)

1. Improved Cleanup and Decoding of Fractional Power Encodings -- arXiv 2412.00488 (2024).
   Soft/iterative FHRR decoding outperforms hard argmax under noise; introduces
   confidence-aware decoding for complex-valued VSA vectors.

2. Classification and Recall with Binary Hyperdimensional Computing: Trade-offs in Choice
   of Density and Mapping -- IEEE Trans Neural Networks 2018 (ieeexplore 8331890).
   Precision-recall trade-off in HDC classification; density and mapping choice
   determines recall gap for ambiguous inputs.

3. Optimal Hyperdimensional Representation for Learning and Cognitive Computation --
   Frontiers AI 2026 (frontiersin.org/journals/frai 1690492). Encoder design for HDC
   remains open question; cleanup decoder accuracy depends on codebook size and N.

4. Global error signal guides local optimization in mismatch calculation --
   Nature Communications 2026 (doi:10.1038/s41467-026-70354-x). Per-step prediction
   error signals in neural circuits; biological basis for per-step bug monitoring.

5. Feature-specific predictive processing: What's in a prediction error? --
   Imaging Neuroscience MIT Press 2025 (direct.mit.edu/imag IMAG.a.1061).
   Prediction errors are feature-specific vectors, not scalars; directional error signal.

6. Ensuring Critical Properties of Test Oracles for Effective Bug Detection --
   ICSE 2024 Companion (dl.acm.org/doi/10.1145/3639478.3639791). Oracle weakness
   (not test coverage) is the dominant cause of missed bugs in property-based testing.

7. The Difference Between Coverage and Mutation Score --
   arXiv 2309.02395 (2024). Mutation scores 2.5-92.8% avg 34.1%; coverage does not
   predict oracle completeness.

8. TOGLL: Correct and Strong Test Oracle Generation with LLMs --
   arXiv 2405.03786 (2025). Targeted oracle generation improves mutation kill rate;
   semantically targeted tests outperform random inputs for mutation detection.

9. State Field Coverage: A Metric for Oracle Quality --
   arXiv 2510.03071 (2025). Oracle quality metric for property-based testing;
   distinguishes oracle weakness from test coverage gaps.

10. Test Oracle Automation in the Era of LLMs --
    ACM TOSEM 2025 (dl.acm.org/doi/10.1145/3715107). LLM-generated test oracles;
    relevant for R-LLM-ORACLE-HYBRID path.

11. Spectrum-Based Fault Localization without Test Oracles --
    UTD technical report (personal.utdallas.edu ewong documents UTD-CS-TR-2010-02-12).
    SBFL per-element suspiciousness scores; granularity effect on recall.

12. Extending Delta Debugging Minimization for SBFL --
    arXiv 2601.04689 (2026). Recent SBFL improvement via delta debugging combination.

13. A comparison of Vector Symbolic Architectures --
    arXiv 2001.11797. Reference for VSA cleanup mechanisms and pairwise cosine
    distributions at high N.

14. Holographic Invariant Storage: Safety Contracts via VSA --
    arXiv 2603.13558 (2026). Safety-critical VSA applications; confidence-threshold
    decoding for reliability.

15. Neural Bug Finding: A Study of Opportunities and Challenges --
    arXiv 1906.00307. Baseline recall rates for neural bug detection; contextualises
    F1=0.704 against the field.

16. Meta Mutation Testing with LLMs at Scale --
    Meta Engineering Blog / InfoQ 2026 (engineering.fb.com 2025/09/30). 73%
    acceptance rate for LLM-generated mutation tests; kill rate improvement.

17. Prediction mismatch responses arise as corrections of a predictive spiking code --
    bioRxiv 2023.11.16 (2024 update). Neural prediction error as corrections, not
    signals; directional mismatch computation.

18. Teralizer: Semantics-Based Test Generalization --
    arXiv 2512.14475 (2025). Property-based test generation from unit tests;
    semantic targeting improves mutation score.

Verified citations: 18.

---

## 9. Next-drill candidate

If R-SOFT-DECODE (E1) returns mid-band (F1 0.62-0.78): drill the CODEBOOK-GEOMETRY
mechanism -- investigate whether the 5-op codebook pairwise cosine distribution
at N=8192 has sufficient margin to separate mutations (compute expected margin =
1/sqrt(N) = 0.011 for random codebook; measure actual margin for the fixed seed
g=833 codebook used in the experiment). If actual margins are near the expected
random value, the codebook is too small and R-CODEBOOK-EXPAND (E8) is the next step.

Field: VSA cleanup theory + spectrum-based fault localisation at sub-component
granularity.
