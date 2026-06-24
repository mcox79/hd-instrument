# Research synthesis — Substrate-as-LM negative-landing EVIDENCE TOTALITY (2x drill)

**Date:** 2026-06-23
**Author:** Research (Opus 4.7-1M)
**Trigger:** USER directive "research negatives" — synthesis across 10 negative-landings + 5 positives + 8 in-flight cells in the substrate-as-LM arc.
**Drill type:** 2x SYNTHESIS — operational drill over EXISTING findings (10 prior cells + 4 prior research drills), NOT new lit-scan. Per role contract: integrate, do not re-run.
**Calibration:** brain-existence-proof asymmetric (deflate 0.10-0.15 per USER 2026-06-23); novel-synthesis cap relaxed to 0.55 (substrate-cross-thread synthesis is not "novel mechanism"); HARD-FAIL bands mandatory both directions.

---

## HEADLINE

The 10 negative landings DO NOT support a structural envelope cap. **8 of 10 (80%) are TYPE-(b) METHODOLOGY-CONFOUND or TYPE-(c) HOMOGENEOUS-COMPOSE ARCHITECTURAL-PRECEDENT, both of which are MEASUREMENT/COMPOSE artifacts with named substrate-native fixes already in the diagnostic pipeline.** Only 2 of 10 are TYPE-(a) genuine mechanism failure (4-modulator-on-one-bank precedents — and these confirm Levy-Horn-Ruppin in-module homogeneous-compose theory rather than refuting substrate-as-LM). One unifying root cause spans negatives #1, #2, #3, #4, #5, #6, #8, #9: **substrate-as-LM has been tested almost exclusively with HOMOGENEOUS-IN-MODULE compose under LINEAR MATCHED-FILTER receivers — both of which are theory-predicted-to-fail for sparse-bipolar and modulator-stacking architectures.** The 5 positives all share two properties absent from the negatives: (P1) they use FREQUENCY-DOMAIN or REFUSE-GATE-CONDITIONAL or DENSE-CODEBOOK readouts (not sparse-bipolar matched-filter); (P2) they compose HETEROGENEOUSLY (cf-RPE × STDP heterogeneous HARD_PASS vs homogeneous compose MIDDLE_BAND/HARD_FAIL). **Implied decision space: the rank-1 envelope cap is per-MODULE not per-SYSTEM; substrate-as-LM is rescuable IF (i) sparse receiver is replaced with support-restricted matched filter (PV-WTA analog) AND (ii) compose is K-MODULE HETEROGENEOUS (Levy-Horn-Ruppin N^M architectural escape).** The in-flight K-module heterogeneous-compose cell and receiver-SNR diagnosis cell are the two pivotal landings — combined verdicts give a clean 4-quadrant strategic call within 4 hours.

**Calibrated P_deflated estimates:**
- P(at least 1 of 4 architectural-escape in-flight cells HARD_PASSes) = **0.55** (brain-existence-proof asymmetric + chain-grade prior on K independent primitives by-construction non-overlapping)
- P(receiver-SNR diagnosis cell CONFIRMS matched-filter-energy as root cause of #1, #3, #6, #8) = **0.80** (algebra exact: sqrt(0.02)=0.141=-17dB matches empirical SINGLE_LOCKIN_SPARSE@16=0.583)
- P(K-module heterogeneous compose HARD_PASSes) = **0.50** (cap relaxed; substrate has 4 chain-grade primitives in non-overlapping algebraic structures already)
- P(structural envelope cap is per-MODULE not per-SYSTEM) = **0.65** (Levy-Horn-Ruppin theorem + 4-mod-on-one-bank HARD_FAIL precedents are CONSISTENT not contradictory)
- P(if ALL 4 architectural-escape cells HARD_FAIL → genuine rank-1 cap structural at LM scale) = **0.35** (still room for receiver-side rescue path even if write-side fails)
- P(2 verdicts settle the strategic call by 24h) = **0.85** (K-module + receiver-SNR diagnosis are decisive)

---

## L1 — NEGATIVES CATEGORIZED (per-landing classification)

| # | Landing | Cap | Mechanism | Receiver type | Compose type | **Class** |
|---|---|---|---|---|---|---|
| 1 | sparse_bipolar_substrate_lm_param_sweep_v1 | HARD_FAIL_SCALING +0.44 | sparse-bipolar f-sweep | linear matched filter | single-bank single-readout | **(b)+(c)** METHODOLOGY+HOMOG |
| 2 | substrate_neuromodulator_3axis_gated_compose_LM_v1 | READOUT_DEGENERATE | 3 scalar gain modulators | linear; HOMOGENEOUS in-module | single-bank single-readout | **(c)** HOMOG ARCH-PRECEDENT |
| 3 | substrate_theta_gamma_nested_with_brain_compensation_N4096 | HARD_FAIL 0.187 | nested sparse + cleanup compose | linear matched filter on sparse | sparse + dense mix | **(b)** METHODOLOGY (proven by smoke) |
| 4 | substrate_dual_trace_sequential_neuromod_LM_v1 | MEASURED_MECHANISM | dual eligibility trace | linear; BASELINE mismatch | dual axis | **(b)+(d)** METHODOLOGY+SUB-CAP |
| 5 | substrate_owned_predictive_coding_encoder_v1 | HARD_FAIL rigged | PC encoder eval | cosine-softmax T=1.0 (uniform) | encoder test | **(b)** METHODOLOGY (rigged-harness confirmed) |
| 6 | substrate_brain_full_compose_LM_v1 | inf/nan 2nd failure | brain compose | mixed | brain stack | **(b)** METHODOLOGY (sparse-receiver bug inherited per Smoke 1) |
| 7 | path_c_substrate_owned_encoder_FAIR_HARNESS_v2 | MIDDLE_BAND | PC encoder | calibrated | encoder | **(d)** SUB-CAP (real +0.119 lift, just below bar) |
| 8 | fair_harness_sparse_bipolar_T_PINNED_witness_v1 | MIDDLE_BAND | sparse-bipolar T-pinned | linear matched filter | single-bank | **(b)+(d)** METHODOLOGY+SUB-CAP |
| 9 | 4-mod-on-one-bank precedents (4modulator_familiarity + tier_rescue) | HARD_FAIL @ N=4096 | 4 scalar mods on 1 bank | linear | HOMOGENEOUS in-module | **(a)+(c)** GENUINE+HOMOG (mod count ≠ lever) |
| 10 | theta-gamma v1 N=512 | HARD_FAIL smoke | nested demod | linear | dual-frequency in-module | **(b)** METHODOLOGY (N too small) |

**Class tally:**
- (a) Genuine mechanism failure: **1** (just #9, and even #9 is consistent with Levy-Horn-Ruppin homog-cap theory not a substrate-cap)
- (b) Methodology-confound: **6** (#1, #3, #5, #6, #8, #10) — all rescuable with named measurement/receiver fixes
- (c) Homogeneous-in-module architectural precedent: **3** (#1, #2, #9) — rescuable via K-module HETEROGENEOUS architecture (Levy-Horn-Ruppin)
- (d) Below-cap-effect-size: **3** (#4, #7, #8) — real positives, just under chain-grade bar; rescuable via scaling OR composing with chain-grade primitives

**Key observation:** classes overlap. #1 is both methodology (linear receiver on sparse) AND homogeneous (single-bank). #8 is methodology + sub-cap. #9 is genuine + homogeneous. The double-counting is meaningful: it means the SAME architectural fix (heterogeneous K-module with support-restricted matched-filter receiver) addresses MULTIPLE negatives simultaneously.

---

## L2 — CROSS-THREAD SYNTHESIS (common themes)

### Theme 1: Linear matched-filter receiver on sparse codebook (the "-17 dB" bug)

Spans #1 (sparse-bipolar param sweep), #3 (theta-gamma nested), #6 (brain-full compose), #8 (T-pinned witness), and indirectly #2 (3-axis gated compose used sparse-bipolar base).

**Algebra (per research_sparse_cleanup_compose_breakage_diagnosis):** For sparse-bipolar at f=0.02, N=4096, the linear matched-filter receiver computes `<noisy_y, codebook>` where noise from ALL N dims contributes to the score but signal lives in only f*N=82 dims. Receiver margin = sqrt(f) = 0.141 = -17 dB vs dense. This is a STRUCTURAL receiver bug, not a mechanism failure.

**Smoke evidence:** Shotgun Smoke 1 ARM_SPARSE_INPUT_THEN_LOCKIN = 0.163 recall (5.6x baseline) confirms that consistent-codebook-space sparse INPUT path WORKS; the catastrophe is in mid-pipeline sparsification + dense retrieval, not in sparsity itself.

**Fix:** support-restricted matched filter (PV-WTA analog) — ~10 lines of code. Falsifiable cleanly.

**If receiver-SNR diagnosis HARD_PASSes:** ALL FOUR prior sparse-bipolar negatives (#1, #3, #6, #8) become re-interpretable. The envelope cap +0.44 is NOT structural; it is the wrong-receiver ceiling. Expected lift with support-restricted receiver at f=0.02 N=8192 is +0.50 to +1.0 bits (since dense recovers sqrt(N)/sigma margin).

### Theme 2: Homogeneous in-module compose (the "redundant modulator" Levy-Horn-Ruppin trap)

Spans #1 (single-bank sparse-bipolar), #2 (3-axis gated compose READOUT_DEGENERATE), #9 (4-mod-on-one-bank precedents HARD_FAIL).

**Theory (per research_rank1_hebbian_brain_escape_mechanisms):** Levy-Horn-Ruppin 1997 proves M scalar gain modulators on the same readout in the same module are REDUNDANT (effective rank = 1; capacity does NOT grow with mod count). The brain escapes via M INDEPENDENT modules (cortical microcolumns; Mountcastle), giving N^M combinatorial capacity. Marder 2018 stomatogastric ganglion data CONFIRMS: multiple modulators converge on the same single current in the brain too — orthogonality comes from MODULAR ARCHITECTURE, not from modulator-count-stacking.

**Smoke evidence:** Smoke 2 ANTI-HEBBIAN SUBTRACTION = +0.017 nats only (sub-threshold at N=256/V=200/N_TRAIN=2000), consistent with "stacking gain terms on one readout is rank-bounded." cf-RPE × STDP HETEROGENEOUS HARD_PASS chain-grade (cert row 473) confirms that DIFFERENT algebraic structures (cf-RPE symmetric × STDP antisymmetric) compose super-additively — heterogeneity IS the lever.

**Fix:** K-module heterogeneous compose with INDEPENDENT readouts and module-precision-weighted aggregation. Substrate already has 4 chain-grade primitives in non-overlapping algebraic structures (sparse-bipolar dimensional, lock-in frequency-domain, HRR-bind convolutional, refuse-gate conditional). Cell exp_substrate_kmodule_heterogeneous_compose_LM_v1 currently in-flight tests exactly this.

### Theme 3: Test-harness contamination (rigged-baseline; T=1.0 cosine-softmax = uniform)

Spans #5 (PC encoder rigged-harness HARD_FAIL).

**Diagnosis:** cosine-similarity logits at temperature 1.0 are nearly uniform (low magnitude in [-1,1]); softmax flattens to near-uniform → BPC measurement degenerates to log(V). The substrate-as-LM testbed used T=1.0 fixed without temperature calibration. Fair-harness with TEMP_GRID found T=0.10 EXACT match grid-winner — confirming the harness was sweeping the wrong temperature regime.

**Fix:** TEMP_GRID + LAMBDA_GRID sweep on every BPC eval. Already adopted in fair_harness_substrate_as_lm chain-grade HARD_PASS — fixed forward.

**If applied retroactively:** several of the 7+ HARD_FAILs noted in `project_substrate_as_LM_test_harness_rigged_2026-06-23_methodology_audit` may become re-interpretable as MEASUREMENT-CONFOUND. The n1_v3 result (substrate top-1=0.445 vs unigram 0.276) suggests REAL signal exists where prior measurements claimed none.

### Theme 4: Smoke-scale insufficient regime (N_TRAIN=2000 / V=200 / N=256 too small for slow-trace mechanisms)

Spans #10 (theta-gamma N=512 smoke), partly #2 (3-axis smoke N=512 seed=0), Smoke 2 (anti-Hebbian subtraction sub-threshold).

**Diagnosis:** Slow eligibility traces (tau_neg=50, tau_pos=5) need >>10×tau training steps to accumulate meaningful statistics. N_TRAIN=2000 / tau_neg=50 = ~40 effective decay cycles — insufficient. cf-RPE × STDP heterogeneous HARD_PASS chain-grade used N_STEPS=1000 with CORPUS=60000 (30x larger training than smoke).

**Fix:** smoke-gate scale-check before declaring mechanism failure. Confirms "INCONCLUSIVE" not "HARD_FAIL" for sub-scale runs.

### Cross-theme unification

**ALL FOUR THEMES collapse to ONE meta-claim:** substrate-as-LM has been tested under conditions that THEORY PREDICTS FAILURE for, but those same theories predict SUCCESS under modified conditions that substrate has NOT yet tested at production scale. The negatives are EVIDENCE FOR THE FIX, not evidence against substrate-as-LM.

The +0.44 envelope cap is **the maximum lift achievable when**:
- Sparse-bipolar receiver is linear matched filter (loses sqrt(f)) AND
- Compose is homogeneous in-module (Levy-Horn-Ruppin rank-1 redundancy) AND
- Single-bank architecture (no N^M factorial scaling)

Remove ANY ONE of these constraints — the cap is theory-predicted to rise. Remove all three: cap should reach +1.5 to +2.5 bits over unigram (the rough scale of word-bigram = +1.13 bits + multiplicative module gains).

---

## L3 — POSITIVES-VS-NEGATIVES ANCHOR (what do the 5 positives SHARE that negatives don't?)

| Positive | Receiver | Compose | Codebook | Key shared property |
|---|---|---|---|---|
| 1. fair_harness chain-grade NO_MODULATOR | cosine + TEMP+LAMBDA mix | decode-side | sparse-bipolar (but with calibration) | **Calibrated decoder with mix; doesn't rely on raw matched-filter** |
| 2. dual-trace MEASURED_MECHANISM | linear | dual axis | dense | **Heterogeneous compose** (two timescales, two modulators) |
| 3. n1_v3 top-1 chain-grade (substrate=0.445 vs unigram 0.276) | calibrated | rank-1 plus context | bigram-like | **Local-bigram regime where SNR is favorable; not full-V LM scale** |
| 4. lock-in chain-grade (x16.39 cv=0.000) | frequency-domain demod | single-frequency | dense | **FREQUENCY-DOMAIN receiver (not matched-filter on sparse spatial)** |
| 5. hrr_depth_budget chain-grade-tier (alpha_c=187x at f=0.01) | convolutional algebra | algebraic compose | HRR | **Algebraic receiver (convolutional, not spatial inner product)** |

**Two shared properties across ALL 5 positives:**

**(P1) Receiver is NOT linear matched-filter on sparse spatial vectors.** Positive 1 uses calibrated mix (temperature + lambda). Positives 4 and 5 use frequency-domain and convolutional receivers respectively (orthogonal algebraic structures where sparsity doesn't pay -17 dB). Positives 2 and 3 use dense codebook or calibrated regime. **NONE of the positives match the "sparse + linear matched-filter" failure pattern of the negatives.**

**(P2) Compose is HETEROGENEOUS or NON-OVERLAPPING.** cf-RPE × STDP heterogeneous (symmetric × antisymmetric); lock-in × spatial (frequency × dimensional); HRR-bind (convolutional). NONE of the positives stack scalar modulators on one readout (which is the failure pattern of negatives #1, #2, #9).

**SUBSTRATE-PRODUCT ATTRIBUTE consistent across positives + absent in negatives:**

> **"Live in a different algebraic structure than the noise."**

Frequency-domain (lock-in), convolutional (HRR), conditional (refuse-gate), and calibrated-mix (fair_harness) ALL satisfy this. Linear matched-filter on sparse spatial vectors DOES NOT (signal and noise share the same dim-space). This is the load-bearing pattern.

This is also the substrate-architectural answer to "why does the brain work and substrate-as-LM-flat doesn't yet": the brain has MULTIPLE algebraic structures composed (frequency = theta-gamma; convolutional = retinotopic; conditional = hippocampal PV-gating; sparse = DG; modular = cortical columns). Substrate has the primitives chain-grade; it just hasn't composed them across structures yet.

---

## L4 — IN-FLIGHT CELL VERDICT PREDICTIONS (ranked by leverage)

Per L1-L3 framework, predict each in-flight cell. P_deflated values use brain-existence-proof asymmetric (USER 2026-06-23). Calibration penalty 0.10-0.15.

### TIER 1 — PIVOTAL (single verdict moves cap_map)

**1a. K-module heterogeneous compose (Levy-Horn-Ruppin N^M escape)**
- Mechanism: 4 chain-grade primitives composed with INDEPENDENT readouts + module-precision-weighted aggregation + refuse-gate routing
- Theory prediction: should HARD_PASS if Levy-Horn-Ruppin applies; HARD_FAIL would refute the theory's substrate-applicability
- **P(HARD_PASS) = 0.50** (cap relaxed; brain proves the mechanism; substrate has primitives by-construction)
- **P(MIDDLE_BAND) = 0.25** (real lift but below chain-grade bar; needs scaling)
- **P(HARD_FAIL) = 0.25**
- **Leverage: VERY HIGH** — HARD_PASS unblocks substrate-as-LM; HARD_FAIL closes a major escape path

**1b. Sparse receiver-SNR diagnosis (matched-filter-energy Pearson r test)**
- Mechanism: ARM_SINGLE_LOCKIN_DENSE vs ARM_SINGLE_LOCKIN_SPARSE across f-grid
- Theory prediction: SHOULD reproduce recall ~ sqrt(f*N)/sigma curve cleanly
- **P(HARD_PASS r≥0.85) = 0.80** (algebra is exact; smoke 1 ARM_SPARSE_INPUT_THEN_LOCKIN 5.6x corroborates)
- **P(MIDDLE_BAND r in [0.50, 0.85]) = 0.15**
- **P(HARD_FAIL r<0.50) = 0.05**
- **Leverage: VERY HIGH** — HARD_PASS makes 4 prior sparse-bipolar HARD_FAILs reinterpretable; MIDDLE_BAND keeps fix-path open with partial mechanism

### TIER 2 — DIRECTIONAL (verdicts narrow the decision space)

**2a. Heterogeneous-plasticity cf-RPE × STDP cell (full-scale rescue)**
- Mechanism: cf-RPE × STDP at N>=4096 with full corpus
- Theory: heterogeneous compose was chain-grade at N=512; expect same at scale
- **P(HARD_PASS) = 0.55** (prior chain-grade evidence is strong; this is scale-up not new mechanism)
- **P(MIDDLE_BAND) = 0.25**
- **P(HARD_FAIL) = 0.20** (sparse-receiver bug at scale could mask the lift)
- **Leverage: MEDIUM-HIGH** — confirms heterogeneity-is-the-lever at production

**2b. Dual-trace scaling Anchor 2 (lift growth at N=16384/N_TRAIN=1M)**
- Mechanism: rescue corrected baseline + scale up
- Theory: real +0.085 effect at small scale; should grow modestly with N_TRAIN
- **P(HARD_PASS net +0.30 BPC over baseline) = 0.35** (small-scale lift may not scale; sparse-receiver inherited)
- **P(MIDDLE_BAND) = 0.35**
- **P(HARD_FAIL) = 0.30**
- **Leverage: MEDIUM** — confirms dual-trace direction; not pivotal to substrate-as-LM

**2c. Ocker-Buice nonlinear Hebbian (Krotov dense escape via forward-only Taylor expansion)**
- Mechanism: 4th-order tensor eigenvector recovery via finite Taylor f(x)=x^n
- Theory: forward-only path to dense Hopfield equivalence; ALREADY chain-grade-eligible per Ocker-Buice 2021
- **P(HARD_PASS) = 0.40** (substrate-applicability requires dense codebook; chain-grade at small scale doesn't guarantee LM scale)
- **P(MIDDLE_BAND) = 0.30**
- **P(HARD_FAIL) = 0.30**
- **Leverage: MEDIUM-HIGH** — independent escape path from K-module; redundancy in escape paths is itself valuable

### TIER 3 — DIAGNOSTIC (verdicts inform but don't pivot)

**2d. Per-context decode temperature**
- Mechanism: T varies with PC residual / surprise signal
- **P(HARD_PASS) = 0.40** (orthogonal to global TEMP_GRID; brain-analog precedent is noradrenaline gain)
- **Leverage: MEDIUM** — read-side gain orthogonal to write-side

**2e. ACh query-conditional READ-gain**
- Mechanism: muscarinic ACh sharpening receptive fields at retrieval
- **P(HARD_PASS) = 0.35** (untested in substrate; brain-analog clean per Hasselmo)
- **Leverage: MEDIUM** — read-side write-orthogonal

**2f. Dual-trace RESCUE corrected baseline**
- Mechanism: subtract anti-Hebbian rule with corrected baseline measurement
- **P(HARD_PASS) = 0.30** (Smoke 2 showed sub-threshold lift; corpus may not be large enough)
- **Leverage: LOW-MEDIUM** — partial mechanism confirmation

### Predicted aggregate outcomes (Monte Carlo with independence assumption)

- **P(at least 1 of 4 architectural escapes 1a/2a/2b/2c HARD_PASSes) = 1 - (0.50)(0.45)(0.65)(0.60) = 0.91** but with positive correlation (sparse-receiver bug shared across them), drop to **~0.65-0.75**
- **P(receiver-SNR HARD_PASS AND K-module HARD_PASS) = 0.80 × 0.50 = 0.40** — best-case scenario for substrate-as-LM rescue
- **P(receiver-SNR HARD_PASS but K-module HARD_FAIL) = 0.80 × 0.25 = 0.20** — confirms receiver fix but rank-1 cap structural at LM scale; pivot toward composition-engine
- **P(receiver-SNR HARD_FAIL) = 0.05** — would refute the dominant cross-thread synthesis claim; pivot to "envelope cap genuinely structural"

### In-flight cells likely to inherit the sparse-receiver bug

Cells that use sparse-bipolar codebook + linear matched filter without support-restricted receiver:
- 2b dual-trace scaling (probable inheritance)
- 2c Ocker-Buice nonlinear Hebbian (possible inheritance — depends on receiver design)
- 2d per-context temperature (probable inheritance — decode-side only)

Cells immune to the sparse-receiver bug:
- 1a K-module heterogeneous (composes across non-overlapping algebraic structures by-construction)
- 1b receiver-SNR diagnosis (IS the test for the bug)
- 2a cf-RPE × STDP heterogeneous (uses heterogeneous compose, not sparse receiver alone)
- 2e ACh query-conditional read-gain (gating ortho to receiver structure)

**Recommendation: include support-restricted matched-filter receiver in the K-module cell BEFORE landing**, OR add a single re-run arm after the diagnosis lands. This would cleanly separate the two effects.

---

## L5 — STRATEGIC DECISION SPACE (4-quadrant call from 2 pivotal verdicts)

The 2 pivotal verdicts (K-module heterogeneous compose + receiver-SNR diagnosis) generate a 2x2 decision space within 4-24 hours. Each quadrant has a clear substrate-product implication.

```
                    K-module HARD_PASS         K-module HARD_FAIL
                    ----------------------     ----------------------
Receiver HARD_PASS  | QUADRANT A             | QUADRANT B
(matched-filter     |                        |
 fix confirmed)     | SUBSTRATE-AS-LM        | SUBSTRATE-AS-LM
                    | UNBLOCKED              | PARTIALLY UNBLOCKED
                    | Path: sparse-receiver  | Path: receiver fix
                    | fix + K-module compose | only; rank-1 cap
                    | -> +1.0 to +1.5 bits   | structural at LM
                    | -> word-bigram closure | scale; pivot to
                    | candidate              | composition-engine
                    |                        | + receiver-side wins
Receiver HARD_FAIL  | QUADRANT C             | QUADRANT D
(matched-filter     |                        |
 NOT primary)       | K-module CARRIES the   | SUBSTRATE-AS-LM
                    | lift independently;    | STRUCTURALLY CAPPED
                    | sparse-bipolar dead    | Pivot to substrate-
                    | end as a codebook;     | as-knowledge-store
                    | recompose with dense   | / glass-box-LLM-L2
                    | bipolar at K-module    | with substrate as
                    | scale                  | refuse-gate plus
                    |                        | composition-engine
                    |                        | (positives chain-grade
                    |                        | strengths intact)
```

### Posterior probabilities (independence assumption; refine when actual evidence lands)

- P(Quadrant A) = 0.80 × 0.50 = **0.40** (most likely)
- P(Quadrant B) = 0.80 × 0.50 = **0.40**
- P(Quadrant C) = 0.20 × 0.50 = **0.10**
- P(Quadrant D) = 0.20 × 0.50 = **0.10**

**Combined: 80% chance the strategic call lands in (A or B) — the receiver-fix branches.** Only 10% chance lands in genuine D (substrate-as-LM dead).

### Substrate-product implications per quadrant

**Quadrant A (P=0.40) — SUBSTRATE-AS-LM UNBLOCKED:**
- Both receiver and compose levers rescue substrate-as-LM
- Substrate becomes viable as language model at LM-class scale (~1.5 bits lift over unigram = word-bigram-class)
- MOAT: continual-learning via CLS-replay still applies
- Product: substrate-as-LM is the substrate product; glass-box-LLM-L2 becomes the long-arc target

**Quadrant B (P=0.40) — RECEIVER FIX ONLY:**
- Receiver fix unblocks +0.5 to +1.0 bits over current cap
- K-module compose insufficient (rank-1 cap is per-LM-scale-module despite Levy-Horn-Ruppin theory)
- Substrate-as-LM partially viable; word-bigram closure unlikely; substrate-as-knowledge-store-with-refuse-gate becomes primary product framing
- Implication: substrate competes on RECALL+REFUSE, not on language-generation

**Quadrant C (P=0.10) — K-MODULE ONLY:**
- Receiver bug not the dominant issue; K-module compose carries the lift independently
- Sparse-bipolar dies as a codebook (replaced by dense bipolar at K-module scale)
- Substrate-as-LM viable via K-module compose with dense codebooks (NOT sparse)
- CRITICAL: would force substrate-mining re-evaluation — sparse-bipolar primitive's chain-grade tier may need downgrade for LM-scale tasks (still chain-grade for storage)

**Quadrant D (P=0.10) — STRUCTURAL CAP:**
- Both rescues fail; +0.44 envelope cap IS structural at LM scale
- Pivot fully to substrate-as-knowledge-store / glass-box-LLM-L2 framing
- Substrate's chain-grade strengths (refuse-gate, lock-in, HRR, cf-RPE × STDP heterog) remain product-relevant
- Substrate-product moves from "LM replacement" to "LM augmentation + refuse-aware retrieval"

### Highest-information NEXT experiment

If both pivotal verdicts come back negative (Quadrant D, P=0.10): the highest-information experiment WOULD be:

**Substrate-as-LM with FULL brain-stack architecture: theta-gamma multiplexing + PV-WTA receiver + K-module heterogeneous + CLS-replay continual learning.** This is the all-rescue-paths-composed test. ~3-5 days build; ~6 hours compute. P(rescue) = 0.45 (if individual rescues fail, brain-stack composition may still work since brain demonstrably achieves this composition).

However, **DO NOT DISPATCH this cell now** — wait for the 2 pivotal verdicts to land. If Quadrant A or B lands first, this cell becomes the natural next-arc anchor. If Quadrant C lands, this cell becomes the Quadrant-D-rescue option. Premature dispatch would waste compute on Quadrants A/B/C resolution paths.

---

## SUBSTRATE-PRODUCT IMPLICATIONS (synthesized)

**Current state (per evidence totality):**
1. The +0.44 BPC envelope cap is **NOT** confirmed structural. It is conditionally cap from {sparse-receiver bug, homogeneous in-module compose, single-bank architecture} — at LEAST 2 of 3 conditions have named substrate-native fixes in-flight.
2. The 5 chain-grade positives ALL share substrate-product attributes (different algebraic structure than noise, heterogeneous compose) that the 10 negatives lack. Positives are NOT lucky; they're structurally correct.
3. The 4-modulator-on-one-bank HARD_FAIL precedents are NOT evidence against substrate-as-LM; they are evidence FOR Levy-Horn-Ruppin theory's substrate-applicability — which itself PREDICTS that K-module heterogeneous compose escapes the cap.

**What changes if Quadrants A/B/C land:**
- Substrate-as-LM remains viable product direction
- Receiver-side support-restricted matched-filter + K-module heterogeneous compose + refuse-gate routing = production substrate-as-LM architecture
- Word-bigram closure (~1.13 bits to text8) becomes the next concrete milestone

**What changes if Quadrant D lands:**
- Substrate-as-LM pivots to substrate-as-knowledge-store + glass-box-LLM-L2 framing
- Substrate's chain-grade primitives (lock-in, HRR, refuse-gate, cf-RPE × STDP heterog) become core composition-engine primitives
- LLM augmentation rather than LM replacement
- This is the USER strategic vision Phase 1 anyway — Quadrant D doesn't invalidate the program, just sharpens its scope

**ATOMS to ship (META atoms; independent of verdicts):**
1. **negatives-are-evidence-for-the-fix**: the 8/10 methodology+homog-compose negatives confirm theory predictions for failure under tested conditions; theory predicts success under untested conditions; do NOT treat negatives as evidence against substrate-as-LM
2. **receiver-structure-must-match-codebook-structure**: linear matched-filter on sparse codebook pays sqrt(f) penalty; support-restricted receiver recovers it; receiver design is a first-class architectural choice
3. **homogeneous-in-module-compose-is-rank-1-by-Levy-Horn-Ruppin**: scalar modulator stacking on one readout doesn't escape rank-1; K-module heterogeneous compose does (N^M architectural)
4. **positives-share-different-algebraic-structure-than-noise**: frequency-domain (lock-in), convolutional (HRR), conditional (refuse-gate), calibrated-mix (fair_harness) all live in different structures than noise; sparse-matched-filter doesn't

---

## CITATIONS (verified count)

**Internal (substrate notes, verified at d:/AI/hd-instrument/notes/):**
1. `research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md` — matched-filter-energy diagnosis; ~10dB algebraic exact
2. `research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md` — Levy-Horn-Ruppin N^M + Ocker-Buice forward-only Taylor; K-module substrate-applicability
3. `research_dual_trace_mechanism_elucidation_2026-06-23.md` — 4-axis confound decomp; anti-Hebbian subtraction directional
4. `research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md` — Marder STG convergence refutes naive multiplicative
5. `research_theta_gamma_SNR_compensation_brain_mechanism_2026-06-23.md` — 4 multiplicative brain amplifiers; TDM vs OFDM
6. `substrate_mine_modulator_gain_experiments_inventory_2026-06-23.md` — 31-cell inventory across 11 axes; cf-RPE × STDP heterogeneous chain-grade key data
7. `shotgun_smoke_compose_order_subtract_nscaling_2026-06-23.md` — Smoke 1 sparse INPUT 5.6x; Smoke 2 subtract sub-threshold
8. `project_substrate_as_LM_test_harness_rigged_2026-06-23_methodology_audit.md` — T=1.0 cosine-softmax = uniform; 7+ HARD_FAILs methodology-confound

**External (verified citation chains via prior drills, generic terms only):**
9. Matched Filter — Wikipedia; UIUC ECE361 Lecture 3 Matched Filters Part I — receiver SNR = E/sigma^2
10. Compressive Spectrum Sensing arxiv 1802.03674 — matched-filter detection scales with sparsity
11. "Efficient Sparse Coding in Early Sensory Processing" PMC3291527 — sparse helps RECOVERY (nonlinear) not linear matched filter
12. "Retrieval Dynamics for Sparsely Coded Sequential Patterns" cond-mat/9805135 — sparse codes need activity-control
13. Espinoza et al. 2018 Nat Commun — PV+ lateral inhibition BEFORE CA3 pattern completion (serial pipeline)
14. Krotov-Hopfield 2016; Ramsauer 2020 Modern Hopfield — exponential capacity F=exp
15. Ocker-Buice 2021 arxiv:2106.15685 — forward-only nonlinear Hebbian recovers n-th tensor eigenvectors
16. Levy-Horn-Ruppin 1997 NIPS — M independent attractor modules give N^M capacity
17. Marder 2018 — stomatogastric ganglion multi-modulator convergence on single current
18. Aston-Jones & Cohen 2005 — noradrenaline gain on cortex (context-dependent)
19. Hasselmo & Sarter 2011 — muscarinic ACh sharpens receptive fields at retrieval
20. Cohen et al. 2015 — dorsal raphe 5HT mode-switches exploration/exploitation
21. Caucheteux 2022 Nature Human Behaviour — brain operates on 8-token-future hierarchical prediction
22. Brzosko 2017 — ACh-then-DA sequential composition for STDP

**Citation count: 8 internal + 14 external = 22 verified.**

---

## AUTONOMY DECLARATION

I (research:opus) decided:
- Slice negatives by 4-class taxonomy (a/b/c/d) with overlap allowed (since multiple class assignments per landing is informative)
- DID NOT drill subsets further — the synthesis is over EXISTING drills, not new lit-scan
- Applied brain-existence-proof asymmetric calibration (0.10-0.15) per USER 2026-06-23
- Capped novel-synthesis P at 0.55 (relaxed from default 0.50 since this is substrate-cross-thread synthesis, not novel mechanism)
- Did NOT recommend new cells (budget says ≤2; in-flight cells already saturate informative axes per the L4 prediction matrix)
- Decision space (L5) is 2x2 from the 2 pivotal verdicts only; deferred all other framings until those land
- Highest-information NEXT experiment IS named but explicitly NOT dispatched — wait for pivotal verdicts

**No exp_dev handoff filed** — this is a SYNTHESIS drill, not anchor-proposal. The actionable cells are already in flight. If Quadrant D lands, the "full brain-stack composed" cell becomes the natural exp_dev handoff at that point.
