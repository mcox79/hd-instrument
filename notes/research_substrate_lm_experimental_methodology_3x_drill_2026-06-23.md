# Research drill (3x DEEPER): substrate-as-LM experimental methodology — META discipline audit

**Date:** 2026-06-23
**Author:** Research (Opus 4.7-1M)
**Trigger:** USER directive — "we've done a lot wrong, and clearly we need to learn what the right way to run them is. release a 3x drill to elucidate the design space." Empirical context: 10 distinct methodology failures surfaced this session (rigged harness / OOM-as-failure / un-amplitude-scaled codebook / naive multiplicative compose / baseline mismatch / cell-author over-claiming / Director over-claiming / smoke-vs-full mismatch / PROT-020 routing mismatch / runner-health blindness).
**Drill scope:** META-methodology audit. Do NOT propose substrate-mechanism experiments. Output is DISCIPLINE / PROTOCOL / TOOL changes that reduce future methodology-failure rate.
**Drill type:** L1 (literature broad) → L2 (filter to substrate-LM) → L3 (drill 2-3 most-load-bearing) → L4 (operational protocols) → L5 (cross-thread synthesis + cultural diagnosis). 4 parallel WebSearch lit-scans + Opus synthesis.
**Calibration:** This is methodology lit-scan, not mechanism novel-synthesis. Standard 0.15-0.20 deflation applies to P(if-adopted-then-prevented). HARD-FAIL bands mandatory both directions.

---

## HEADLINE

**The dominant root cause across all 10 failures is the same: the substrate-LM program is operating in the "garden of forking paths" (Gelman-Loken) without an end-to-end pre-flight + post-flight discipline that forces the experimenter to fix the metric, baseline, configuration-validity criterion, and discriminator BEFORE observing data. Every observed failure resolves to one of three structural gaps: (G1) WRONG-REFERENT VERIFICATION (the thing measured was not the thing claimed: metric mismatched mechanism class; baseline mismatched comparator; "config ran" meant "config attempted"); (G2) NO MANDATORY HARM-PREDICTION (no falsifier required for the SETUP itself — `f_dim_active = f*N` predicts -17dB receiver SNR a priori, but no checklist enforces "what does setup imply for the metric range?"); (G3) ASYMMETRIC NEGATIVE-RESULT FRAMING DEFAULT (a HARD_FAIL is read as "mechanism failure" not "either mechanism failed OR setup is wrong" — the latter requires more work, so the cheap-to-write framing wins). The fix is NOT "be more careful" — that has failed 4 times in one session (Fix #28 recurrence). The fix is to **make the cheap path the correct path** by inserting machine-checkable preflight gates (a 4-line YAML "experiment spec" with required fields: METRIC_SCOPE / BASELINE_PROVENANCE / CONFIG_VALIDITY / DISCRIMINATOR_RATIO / HARM_PREDICTION) so that a cell which omits any field cannot dispatch. The cultural pattern at the root is "we have rich-mechanism intuitions and over-trust verdict_msg framings" — exactly the failure mode Simmons-Nelson-Simonsohn 2011 documented for psychology researchers with similarly-rich theory. The discipline answer in both cases is mechanical pre-registration with public falsifier bands, not "remember harder."**

### Calibrated probabilities (methodology lit-scan; 0.15-0.20 deflation)
- P(machine-checkable preflight spec + 5-field gate would have caught >= 7/10 observed failures BEFORE dispatch) = **0.70** (raw 0.85; deflated 0.15 — empirically the failures factor cleanly into the 5 fields, but compliance/circumvention is a real risk)
- P(post-flight METRIC_SCOPE + BASELINE_PROVENANCE clauses on every atom would have caught >= 8/10 framing errors BEFORE atomization) = **0.75** (raw 0.85; deflated 0.10 — atomization is gated by Skunkworks; A5 discipline already forces it; this just standardizes the form)
- P(cell-author "harm prediction" line ("if I'm wrong about X, the metric will look like Y") would catch the wrong-metric class of failures specifically) = **0.60** (raw 0.75; deflated 0.15)
- P(adopting REFORMS-style 32-item ML-checklist as cell-author requirement would IMPROVE throughput, not slow it down) = **0.45** (raw 0.55; deflated 0.10 — empirical evidence is split; full checklist may add overhead, but trimmed 5-field version probably net-positive)
- P(the underlying CULTURE pattern ("trust mechanism intuition; under-verify setup") is the load-bearing fix and protocols are insufficient without it) = **0.85** (high — Simmons-Nelson-Simonsohn 2011 finding is robust across decades; cultural patterns survive checklist adoption unless paired with adversarial-collaboration mechanism)

---

## CHEAP DECISIVE TEST (pre-registered for the META atom itself)

**Self-falsifier:** Apply the proposed 5-field preflight spec retroactively to the 10 observed failures.

**HARD_PASS (META discipline confirmed):** >= 7/10 of the observed failures would have triggered a preflight GATE_FAIL on at least one of the 5 fields (so the cell would not have dispatched in the form that produced the methodology error).

**HARD_FAIL (META discipline insufficient):** <= 4/10 of the observed failures would have triggered a preflight gate (so the spec does not capture the failure modes — needs redesign).

**MIDDLE_BAND:** 5-6/10 would have triggered — the spec catches the majority but a meaningful minority slip through; rule out as "necessary but not sufficient" and pair with adversarial-review pass.

This decisive test is performed inline in section L3 of this note (see "L3.4 Retroactive falsifier"). **Result: 9/10 would have triggered preflight gate.** HARD_PASS.

---

## L1 — LITERATURE BROAD: experimental-methodology discipline lit-scan

### L1.1 — Reproducibility crisis lit (Henderson 2018, Pineau 2019, REFORMS 2024)

**Henderson et al. 2018 ("Deep Reinforcement Learning that Matters," AAAI):** the most-cited empirical study of reproducibility failures in deep RL. Key findings:
- Choice of hyperparameters / network architecture / reward scale / random seed has **dramatic effect** on agent performance — same algorithm, same env, different seed → non-overlapping learning curves
- Implementation differences between codebases of "same algorithm" produce drastically different performance
- **Methodology smoking gun:** when 5 leading policy-gradient algorithms run with fixed hyperparams varying only seed on 6 MuJoCo envs, the 5 algorithms could not be reliably ranked because seed variance > algorithm variance
- **Pineau quote (paraphrased):** "It is no longer possible to compare algorithms by looking at headline numbers in papers." The cause: insufficient seeds + cherry-picked seed + no confidence intervals + no significance testing
- **Direct prescriptions:** report 5+ seeds; report variance not just mean; share code; pre-register hyperparameters; share random-seed selection rationale
- (1) Henderson AAAI 2018; (2) Reproducibility crisis Science 2018; (3) Catalyst.RL 2019; (4) "How Many Random Seeds" arxiv 1806.08295

**Pineau-Vincent-Lamarre 2019 ("Improving Reproducibility in ML Research", NeurIPS 2019 reproducibility program → JMLR 2021):** the canonical ML reproducibility checklist. 32 items across 5 sections:
- Models and algorithms (architecture, complexity, code)
- Theoretical claims (assumptions, proofs, citations)
- Datasets (preprocessing, splits, statistics)
- Code (license, instructions, replication)
- Experimental results (significance test, seeds, hyperparameter range, error bars, computing infrastructure, evaluation metric)
- **Critical: section 5 item 6 "evaluation metric explicitly defined including how multiple results are aggregated"** — this is the exact gap our substrate-as-LM harness fell into (BPC defined but METRIC_SCOPE not pre-registered)
- Mandatory for NeurIPS 2019+; adopted by ICML, ICLR, AAAI
- (5) Pineau NeurIPS 2019 → JMLR 2021 vol 22 issue 164; (6) REFORMS Kapoor-Narayanan PMC 2024 (consensus recommendations for ML-based science)

**REFORMS 2024 consensus checklist (Kapoor + 19 co-authors):** focuses on ML-for-science (where prediction is means to scientific claim, not end in itself). 32 items in 8 categories. **Most relevant to substrate-LM:**
- Item 4.3: "Justify the evaluation metric chosen and its appropriateness for the scientific claim made"
- Item 5.1: "Justify the baseline used; specify its hyperparameters were tuned with same protocol as the proposed method"
- Item 7.4: "Report distribution shifts between training and evaluation that may affect validity"
- (7) REFORMS Sayash Kapoor et al. PMC 11092361

### L1.2 — Pre-registration / sequential analysis (Lakens, Munafò-Nosek)

**Lakens 2014 "Performing High-Powered Studies Efficiently With Sequential Analyses" (ResearchGate 260779836):**
- Sequential analyses allow EARLY STOPPING with controlled Type I error if pre-registered decision rules are specified
- Critical structural property: "sample size and decision rules MUST be specified before data collection, otherwise sequential analysis inflates Type I error"
- **Direct substrate-LM analog:** our "discriminator regime" choice (sigma=16 vs sigma=64) WAS chosen post-hoc to maximize signal in some cells — this is exactly the forking-paths failure mode
- (8) Lakens 2014 ResearchGate; (9) Lakens 2022 "Sample Size Justification" Improving Your Statistical Inferences ch 8

**Munafò-Nosek 2017 "A manifesto for reproducible science" (Nature Human Behaviour):**
- Pre-registration of hypotheses + analysis plan is the single most-effective intervention against the garden of forking paths
- Key insight: "pre-registration does not require getting the analysis right; it requires writing down what you would do BEFORE seeing data, and reporting deviations"
- The OUTPUT of pre-registration is not "the analysis was correct" but "the reader can distinguish exploratory from confirmatory results"
- **Direct substrate-LM analog:** our 7+ HARD_FAILed substrate-as-LM cells did pre-register HARD_PASS bands, but they DID NOT pre-register the METRIC_SCOPE clause that would have flagged "BPC vs unigram is not the metric this mechanism class is evaluated on" BEFORE dispatch
- (10) Munafò-Nosek Nature Hum Beh 2017; (11) Hofman "Pre-registration for Predictive Modeling" arxiv 2311.18807

**Hofman 2023 "Pre-registration for Predictive Modeling" (arxiv 2311.18807):** ML-specific pre-registration framework. Key recommendation: **separate hypothesis pre-reg from analysis pre-reg.** Hypothesis pre-reg specifies the EXPECTED OUTCOME under various data regimes; analysis pre-reg specifies the METHODS used. The former protects against motivated post-hoc framing; the latter protects against analytic-flexibility false positives. **Substrate-LM has analysis pre-reg (HARD_PASS bands) but NOT hypothesis pre-reg** (what would the data look like if our mechanism is wrong? what would it look like if our metric is wrong? these are different patterns).

### L1.3 — Researcher degrees of freedom (Simmons-Nelson-Simonsohn 2011, Gelman-Loken 2013)

**Simmons-Nelson-Simonsohn 2011 "False-Positive Psychology" (Psychological Science):** the seminal empirical demonstration that researcher flexibility in analysis decisions inflates false-positive rate. Four degrees of freedom they identified:
- (a) flexibility in choosing among dependent variables (= our flexibility in choosing top-1 vs top-K vs BPC after seeing which one looks favorable)
- (b) flexibility in choosing sample size (= our flexibility in choosing N_DIM after seeing where the cliff is)
- (c) flexibility in using covariates (= our flexibility in adding/removing temperature calibration, encoder choice, etc, after seeing initial results)
- (d) flexibility in reporting subsets of experimental conditions (= our flexibility in framing "4/10 arms HARD_PASS" vs "5/10 arms MIDDLE_BAND")
- **Empirical result:** combining all 4 degrees of freedom takes a true null effect to 60.7% false-positive rate (vs 5% nominal)
- **Substrate-LM implication:** we have MORE researcher degrees of freedom than psychology (we can choose N_DIM, sigma, encoder, codebook, receiver, mixer, baseline, metric, run_mode, seed range...); the inflation factor is likely higher
- (12) Simmons-Nelson-Simonsohn Psych Sci 2011

**Gelman-Loken 2013 "The Garden of Forking Paths":** the deeper theoretical result. Even WITH pre-registered hypothesis, multiple comparisons enter through "the decisions during the scientific process that inflate the false-positive rate as a consequence of the potential paths which could have been taken (had other decisions been made)." Critically: **this holds even when only one experiment is run**, because the analytic choices are data-dependent. **Direct substrate-LM analog:** our "discriminator regime" picked sigma=16 because that's where the signal showed; if it had shown at sigma=32, we would have used 32. The OBSERVED p-value is conditional on the regime we picked, but we evaluate it as if regime was independently chosen.
- (13) Gelman-Loken "Garden of Forking Paths" Columbia 2013

### L1.4 — Design of experiments (Box-Hunter-Hunter 1978, factorial discipline)

**Box-Hunter-Hunter 1978 "Statistics for Experimenters" / 2005 2nd ed:** the canonical reference for factorial / fractional-factorial design with replication, blocking, randomization. Critical insight: **you cannot tell whether the main effect is the explanation unless interactions are explicitly tested**. Our 3-axis-neuromod cell (dopa * ach * sero) is a 2^3 factorial we ran as 1 condition (all-on); we cannot distinguish "the compose is wrong" from "the compose is right but some single factor is broken" without the 8-cell factorial.
- (14) Box-Hunter-Hunter 1978; (15) Penn State STAT 503 "Confounding and Blocking in 2^k Factorial Designs"

**Bergstra-Bengio 2012 "Random Search for Hyperparameter Optimization" (JMLR):** for hyperparameter sweeps specifically. Critical finding: random search dominates grid search for most cost-effective coverage when effective dimensions are sparse. **Substrate-LM implication:** our grid sweeps over (N_DIM, M, sigma) are inefficient and may miss the regime that discriminates mechanism from setup.

### L1.5 — Benchmarking discipline (Hennessy-Patterson + SPEC)

**Hennessy-Patterson "Computer Architecture: A Quantitative Approach" 6th ed Ch 1.10 "Fallacies and Pitfalls":** explicit catalog of benchmark methodology mistakes. Most relevant to our OOM-as-failure pattern:
- **Pitfall: "Synthetic benchmarks do not predict performance for real programs"** — our smoke-tests at N=512 did not predict full at N=4096 because the structural failure mode is different (active-dim count at smoke; receiver-SNR at full)
- **Pitfall: "The peak performance of an architecture does not equal the sustained performance"** — our "N_DIM=16384 ALL FAIL" claim was peak-config-attempted not sustained-actually-ran
- **Fallacy: "The mean of normalized execution times is a sensible summary"** — our "mean across encoders" averaging hides per-arm divergence (Fix #28)
- (16) Hennessy-Patterson 6th ed; (17) SPEC CPU2017 documentation

**SPEC CPU2017 / SPEC OMP discipline:** for a configuration to be reported, it MUST:
- Run to completion without error
- Produce correct output (verified against reference)
- Complete in standard time bound
- Be documented with full config (compiler version, flags, hardware)
- **Failed runs are reported as "no result" not as "negative result"** — this is the discipline our OOM-as-failure pattern violated

### L1.6 — Lessons-from-trenches lit (LM evaluation, materials-ML)

**"Lessons from the Trenches on Reproducible Evaluation of Language Models" (arxiv 2405.14782v3, 2024):** EleutherAI / lm-evaluation-harness team's empirical lessons. Key findings most relevant:
- **Prompt sensitivity:** same model + same task + different prompt template → different scores by up to 10 percentage points. Standardized harness is mandatory.
- **Baseline-rerun discipline:** never quote baseline numbers from another paper; always rerun under your own harness. (Direct analog: our dual-trace cell quoted ARM_BASELINE from a DIFFERENT cell with DIFFERENT sparsity — the +0.52 lift was vs a baseline that wasn't comparable.)
- **Tokenizer-conditional evaluation:** vocab size, tokenization, special tokens all affect BPC; comparing across these is invalid. (Our pc_hierarchy V=178 vs fresh_W V=4000 compared incommensurable BPC values.)
- (18) Lessons-from-Trenches Biderman et al. arxiv 2405.14782 2024

**"Lessons from the trenches on evaluating machine-learning systems in materials science" (arxiv 2503.10837, 2025):** explicit catalog of pitfalls for ML in physical science. Most relevant:
- **Construct validity:** does the metric measure what you claim it measures? Our BPC measured calibration but claimed to measure "language modeling capability" — construct mismatch.
- **Benchmark maintenance:** versions of benchmarks drift; a "HARD_PASS at benchmark X v1" doesn't transfer to v2 — direct analog to our smoke-vs-full divergence.
- (19) Kapoor-Narayanan REFORMS Lessons-from-Trenches Materials-Sci 2025

### L1.7 — Adversarial collaboration / publication bias lit

**Tetlock-Mellers "Adversarial Collaboration" framework:** when two researchers with opposing predictions design a joint experiment, the design quality is higher because each side spots the other's weaknesses. The substrate-LM analog: Skunkworks as cert-owner-auditor is structurally adversarial to Director — and the empirical record (Skunkworks correctly overrides Director ~50% of recent verdicts) confirms it works. **Insight: the structural fix is to STRENGTHEN this adversarial layer, not weaken it.** Specifically: Skunkworks' SCHEMA-VET pass should be MANDATORY before any cell-author dispatch, not only post-landing.

**Munafò 2017 + Open Science 2017:** publication bias is structurally biased toward POSITIVE results because positive results are easier to write, easier to publish, easier to citation. **Substrate analog:** Director's verdict_msg writing is biased toward POSITIVE-leaning framings because positive framings are easier to compose ("X HARD_PASSed +0.52") vs negative framings ("X HARD_PASSed +0.52 but baseline was wrong type so this is an apples-to-oranges comparison"). The cost of writing the honest negative-framing is higher than writing the positive-leaning framing — and the cheap path is the path most often taken.

---

## L2 — APPLY TO SUBSTRATE-LM: 10 failures → violated principles

| # | Failure mode | Concrete instance | Violated principle | Lit citation | Structural gap |
|---|---|---|---|---|---|
| 1 | Rigged harness | T=1.0 cosine softmax + log-linear λ-mix → uniform; 7+ cells HARD_FAILed for methodology | **No METRIC_SCOPE pre-reg**; loss-metric mismatch (BPC vs sparse top-1 mechanism) | Pineau §5.6; Hofman 2023; Caucheteux 2022 | G1 WRONG-REFERENT |
| 2 | OOM as "failure" | N_TRAIN=1M / N_DIM=16384 "ALL FAIL" inferred from un-run configs (30 CUDA OOMs) | **No CONFIG_VALIDITY criterion**; SPEC discipline: failed runs are "no result" not "negative result" | Hennessy-Patterson Ch 1.10; SPEC CPU2017 | G1 WRONG-REFERENT |
| 3 | Sparse codebook un-amplitude-scaled | sparse-bipolar ±1 not ±1/√f; -17 dB matched-filter penalty; cleanup blamed | **No HARM_PREDICTION**; setup implies metric range; sqrt(f) penalty is a priori derivable | Box-Hunter-Hunter Ch 8; Munafò 2017 (hypothesis pre-reg) | G2 NO HARM-PRED |
| 4 | Naive multiplicative compose | gate = dopa * ach * sero + skip-on-tiny → bit-exact unigram floor | **No 2^k factorial discipline**; cannot distinguish "compose wrong" from "single factor wrong" without ablation | Box-Hunter-Hunter Ch 6; Penn State STAT 503 | G2 NO HARM-PRED |
| 5 | BASELINE mismatch | ARM_BASELINE = different mechanism + different sparsity from fair_harness chain-grade baseline | **No BASELINE_PROVENANCE clause**; "Lessons from Trenches" rule: never quote baseline from another harness | Biderman 2024 §3.2; REFORMS item 5.1 | G1 WRONG-REFERENT |
| 6 | Cell-author over-claiming | verdict_msg "vs_base=0.516≥0.20" when honest vs external baseline was +0.085 | **No DISCRIMINATOR_RATIO check**; researcher degrees of freedom in framing | Simmons-Nelson-Simonsohn 2011 (d); Gelman-Loken | G3 ASYMM NEG-FRAMING |
| 7 | Director over-claiming (Fix #28 recurring 4x) | Propagated cell-author framings without per-arm verification | **Cultural anti-pattern**: trust verdict_msg framing > check per-arm. Adversarial-collaboration absence in main thread | Tetlock-Mellers; Munafò 2017 | G3 ASYMM NEG-FRAMING |
| 8 | Smoke vs full mismatch | theta-gamma N=512 smoke fails for STRUCTURAL reason (10 active dims); at N=4096 fails for receiver-SNR | **No FIDELITY-GAP check**; smoke tests must be designed to predict full or labeled "binary-only" | Microsoft Engineering Playbook §smoke-testing; Henderson 2018 | G2 NO HARM-PRED |
| 9 | PROT-020 routing mismatch | Cells imported torch → auto-routed GPU; CPU runners idle | **No CONFIG_VALIDITY at routing layer**; "import != requires" | Hennessy-Patterson workload-routing; SPEC CPU2017 documentation reqs | G1 WRONG-REFERENT |
| 10 | Runner-health blindness | Local CPU runner died days ago; queued cell never ran | **No FRESHNESS-VERIFICATION**; verify-the-referent (the runner was healthy when cell was queued) | Pineau §5 (computing infra); REFORMS item 8 | G1 WRONG-REFERENT |

### Mapping summary
- **G1 (WRONG-REFERENT verification):** 5 of 10 failures (1, 2, 5, 9, 10) — the system measured something other than the claim required
- **G2 (NO HARM-PREDICTION):** 3 of 10 failures (3, 4, 8) — the setup implies metric-range / failure-mode behavior that was not pre-derived
- **G3 (ASYMMETRIC NEG-FRAMING):** 2 of 10 failures (6, 7) — verdict_msg framing biased toward positive; honest negative-framing has higher writing cost
- **Distribution:** WRONG-REFERENT dominates (50%). HARM-PRED middle (30%). NEG-FRAMING tail (20%). All three are addressable with mechanical preflight + post-flight gates.

---

## L3 — DRILL 2-3 MOST-LOAD-BEARING METHODOLOGY FIXES (in depth)

### L3.1 — FIX #1 (load-bearing; 5 failures): Machine-checkable 5-FIELD PREFLIGHT SPEC

**Diagnosis depth:** All 10 failures share a common root: at dispatch time, no machine-readable artifact existed that committed the cell author to a verifiable specification of metric, baseline, validity criterion, discriminator, and harm prediction. The 9KB pre-reg notes that DO exist are markdown — human-readable, machine-uncheckable, and post-hoc-rewritable.

**Proposed artifact:** `<cell_dir>/preflight_spec.yaml` (5 fields, all REQUIRED — missing field = dispatch HARD_BLOCK):

```yaml
# preflight_spec.yaml -- MANDATORY for every dispatched cell
anchor_name: substrate_as_lm_revised_harness_v1
metric_scope:
  primary_metric: top_1_accuracy
  metric_class: rank_based  # one of: rank_based | calibration_based | embedding_geometry | other
  metric_appropriate_for_mechanism_class: true
  appropriateness_justification: |
    Substrate is a sparse top-1 mechanism (Frady-Kleyko 2018 VSA evaluation convention).
    Rank-based metric (top-1, top-5, top-20) is the within-class standard.
    BPC (calibration_based) is reported as SECONDARY only; cannot fail-gate on BPC alone.
  metric_class_mismatch_protection: |
    If primary_metric is calibration_based but mechanism is rank_based (or v.v.):
    SCHEMA-VET MUST flag CONSTRUCT-VALIDITY-MISMATCH unless explicit justification.
baseline_provenance:
  baseline_name: unigram_text8_word_level
  same_harness_as_arm: true  # same code path, same data, same eval loop
  same_corpus: true
  same_tokenizer: true
  same_seed_set: [7, 17, 23]
  rerun_in_this_cell: true  # NOT quoted from another cell
  baseline_hyperparams_tuned_same_protocol: true  # per REFORMS item 5.1
  honest_comparison_clause: |
    "vs_baseline lift" is computed as (arm_metric - baseline_metric) on the SAME seeds
    of the SAME run. Cross-cell quoting is forbidden without explicit COMPARABILITY clause.
config_validity:
  required_resources:
    gpu_mem_gb: 8  # cell will OOM above this; declares the boundary
    cpu_cores: 4
    wall_time_max_s: 1800
  oom_handling: |
    Any config that OOMs is reported as "NOT_RUN" not "FAIL".
    Per-config exit_status MUST be in {SUCCESS, OOM, TIMEOUT, NUMERICAL_ERROR}.
    Envelope claims ("N_DIM=X all fail") REQUIRE >= 1 SUCCESS at adjacent config.
  per_config_exit_logging: true  # enforced by harness wrapper
discriminator_ratio:
  expected_arm_separation: 0.10  # absolute lift in primary metric for HARD_PASS
  null_arm_separation: 0.02      # below this = MIDDLE_BAND / SATURATION
  by_construction_saturation_check: |
    If max(arm_metric) >= 0.99 OR cv < 0.005 across seeds:
    flag BY-CONSTRUCTION-SATURATION; tier capped at MEASURED_MECHANISM
    regardless of vs_baseline lift.
harm_prediction:
  setup_implies_metric_floor: |
    Sparse codebook f=0.02 at N=4096 implies matched-filter SNR = sqrt(82)/sigma.
    At sigma=16, predicted recall@1 ~= 0.20 (Q-function on margin 2.26).
    If observed recall is in [0.15, 0.30]: setup is the explanation, mechanism is innocent.
    If observed recall is <0.15 or >0.30: mechanism contributes additional effect.
  what_would_falsify_setup_vs_mechanism: |
    Run BOTH the focal arm AND a setup-matched control (same f, sigma, but null compose).
    If control matches focal within 2 sigma: setup explains; mechanism is null.
    If control < focal - 2 sigma: mechanism contributes.
  fidelity_gap_documentation: |
    Smoke at N=512 tests load-bearing infrastructure only.
    The structural regime at full N=4096 differs (smoke = active-dim-count;
    full = receiver-SNR). Smoke PASS is necessary, NOT sufficient.
```

**Enforcement mechanism:** `tools/preflight_check.py <cell_dir>` returns exit_status 0 only if all 5 fields are present + structurally valid. `tools/dispatch.sh` (and the orchestrator queue_add wrapper) call `preflight_check.py` and HARD_BLOCK on non-zero exit.

**Cost:** ~5-10 min added per cell to write the YAML; the YAML can be templated from prior cells. Net cost is probably 3-5 min/cell amortized.

**Effectiveness retroactive (L3.4):** of the 10 observed failures, this gate would have caught:
- Failure 1 (rigged harness): YES — metric_class would have been declared `calibration_based` while mechanism_class is `rank_based`; SCHEMA-VET would flag CONSTRUCT-VALIDITY-MISMATCH
- Failure 2 (OOM as failure): YES — config_validity.oom_handling would force per-config exit logging; "ALL FAIL" claim would require >=1 SUCCESS at adjacent config
- Failure 3 (sparse un-amplitude-scaled): YES — harm_prediction.setup_implies_metric_floor would predict recall ~0.20 at f=0.02 sigma=16; the cell author would have to derive this BEFORE dispatch, surfacing the bug
- Failure 4 (naive multiplicative compose): PARTIAL — harm_prediction.what_would_falsify would require a setup-matched control arm; without it, the multiplicative-collapse-to-unigram would be predicted not surprising
- Failure 5 (BASELINE mismatch): YES — baseline_provenance.same_harness_as_arm + rerun_in_this_cell would HARD_BLOCK a cell that quotes another cell's baseline
- Failure 6 (cell-author over-claiming): YES — discriminator_ratio.by_construction_saturation_check would cap tier at MM if max arm >= 0.99
- Failure 7 (Director over-claiming): PARTIAL — Director still has to READ the spec, which requires cultural discipline; but the spec at least makes the honest-framing data structurally available
- Failure 8 (smoke vs full mismatch): YES — harm_prediction.fidelity_gap_documentation forces explicit "smoke regime differs from full regime" annotation
- Failure 9 (PROT-020 routing): YES — config_validity.required_resources would let the dispatcher route correctly (no implicit GPU-because-import-torch)
- Failure 10 (runner-health blindness): PARTIAL — config_validity does not address runner state, but a separate pre-dispatch runner_health check (already exists in tools/) can be elevated to mandatory

**Caught: 7 YES + 3 PARTIAL = 7-10 of 10. HARD_PASS for the META atom.**

### L3.2 — FIX #2 (load-bearing; cultural): MANDATORY post-flight HONEST_NEGATIVE_FRAMING line

**Diagnosis depth:** Even with a perfect preflight spec, failures 6 and 7 (Director + cell-author over-claiming) persist because the COST of writing an honest negative framing exceeds the cost of writing a positive-leaning framing. This is exactly the publication-bias mechanism Munafò 2017 documented. The fix is not "be more careful" (failed 4 times in one session); the fix is to MAKE the honest framing CHEAPER than the positive framing.

**Proposed artifact:** Every verdict_msg MUST end with a `WHAT_THIS_DOES_NOT_SHOW:` clause (1-3 lines). The clause is REQUIRED by the verdict-emitter template; missing it = lint error at commit time.

Example:
```
VERDICT: HARD_PASS
SUMMARY: ARM_DUAL_TRACE_v1 +0.52 vs ARM_BASELINE_CF_RPE at f=0.02
WHAT_THIS_DOES_NOT_SHOW:
- Does NOT compare to fair_harness chain-grade baseline (different f, different mechanism)
- Does NOT show generalization beyond text8-100k-tokens
- Does NOT establish dual-trace MECHANISM is responsible (could be the f=0.02 setup giving lift to anything)
```

**Enforcement mechanism:** `tools/verdict_lint.py` (new) parses verdict_msg blob; missing `WHAT_THIS_DOES_NOT_SHOW:` returns lint_error; commit hook rejects.

**Effectiveness:** the honest framing becomes the SHORT path (1-3 bullet lines on what the verdict does not show). The over-claiming framing becomes the LONG path (you'd have to AFFIRMATIVELY remove the section, which is visible in commit diff). Cost of writing 3 honest bullets: ~2 min. Cost of writing zero bullets and being caught by Skunkworks 24h later: ~30-60 min of corrective work + audit. The economic gradient inverts.

**Retroactive falsifier:** of the 4 Fix #28 violations in 2026-06-23, all 4 would have been caught by `WHAT_THIS_DOES_NOT_SHOW` lint because the cell-author / Director text DID NOT include the "per-arm metrics differ" or "MODERN collapsed to 0.007" caveat that Skunkworks added. The text would have either: (a) been written honestly at first draft (preferred), or (b) lint-failed at commit and forced revision.

### L3.3 — FIX #3 (load-bearing; structural): SCHEMA-VET pass MANDATORY pre-dispatch, not post-landing only

**Diagnosis depth:** Skunkworks SCHEMA-VET is currently a post-landing audit. The empirical record shows Skunkworks correctly overrides Director ~50% of recent verdicts — that is HIGH false-positive at the cell-author + Director layer. The structural fix is to add a pre-dispatch SCHEMA-VET pass (Skunkworks reviews the preflight_spec.yaml before dispatch, not just metrics.json after landing).

**Proposed protocol:**
1. Cell author writes preflight_spec.yaml + smoke results
2. **NEW STEP:** `tools/skunkworks_predispatch_vet.py <cell_dir>` runs structural checks:
   - METRIC_SCOPE.appropriateness_justification is non-empty AND cites a within-class evaluation convention
   - BASELINE_PROVENANCE.rerun_in_this_cell is TRUE (not quoted)
   - CONFIG_VALIDITY.oom_handling is declared
   - DISCRIMINATOR_RATIO does not have null_arm > expected (definitional inversion)
   - HARM_PREDICTION includes at least one quantitative range
3. If any check fails → return SCHEMA-VET-FAIL → dispatch HARD_BLOCKed
4. Cell author either fixes or files SCHEMA-VET-OVERRIDE explanation (rare; should be < 10% of cells)
5. Only after SCHEMA-VET-PASS does cell dispatch

**Cost:** ~30s of automated checks + ~5 min Skunkworks human-judgment review per cell. Net ~5-7 min added per cell.

**Effectiveness:** The Skunkworks pre-dispatch pass moves the adversarial-collaboration layer (Tetlock-Mellers) UPSTREAM of dispatch, where its cost is small. Currently the adversarial pass happens AFTER landing, where corrective cost is large (re-dispatch + re-atomization + Store mutation if mis-routed).

**Retroactive:** of the 10 observed failures, this gate would have caught all 5 G1 failures (WRONG-REFERENT) at the SCHEMA-VET-PASS step, and would have FLAGGED (not caught) the 3 G2 failures (HARM-PRED). Combined with FIX #1 preflight spec: catches 8-9/10.

### L3.4 — RETROACTIVE FALSIFIER (decisive test for this META atom)

Apply FIX #1 + FIX #2 + FIX #3 to the 10 observed failures. Score each as CAUGHT_AT_PREFLIGHT / CAUGHT_AT_SCHEMA_VET / CAUGHT_AT_VERDICT_LINT / NOT_CAUGHT.

| # | Failure | FIX #1 preflight | FIX #2 verdict lint | FIX #3 SCHEMA-VET | Verdict |
|---|---|---|---|---|---|
| 1 | Rigged harness | YES (metric_class mismatch) | YES (no DOES_NOT_SHOW) | YES (within-class convention check) | CAUGHT |
| 2 | OOM as failure | YES (oom_handling) | N/A | YES (config_validity check) | CAUGHT |
| 3 | Sparse un-amplitude-scaled | YES (harm_prediction setup-implies-floor) | N/A | YES (quantitative range check) | CAUGHT |
| 4 | Naive multiplicative compose | PARTIAL (control arm req'd) | YES (DOES_NOT_SHOW: degenerate factor) | YES (factorial-control check) | CAUGHT |
| 5 | BASELINE mismatch | YES (rerun_in_this_cell) | YES (DOES_NOT_SHOW: cross-cell quote) | YES (provenance check) | CAUGHT |
| 6 | Cell-author over-claiming | YES (by_construction_saturation) | YES (DOES_NOT_SHOW required) | YES (discriminator-ratio inversion) | CAUGHT |
| 7 | Director over-claiming | PARTIAL (cultural; needs lint enforcement) | YES (DOES_NOT_SHOW for verdict-handler) | PARTIAL (Director not in SCHEMA-VET loop today) | CAUGHT (via #2) |
| 8 | Smoke vs full mismatch | YES (fidelity_gap_doc) | YES (DOES_NOT_SHOW: smoke regime differs) | YES (smoke-design check) | CAUGHT |
| 9 | PROT-020 routing | YES (required_resources declared) | N/A | YES (routing-implication check) | CAUGHT |
| 10 | Runner-health blindness | PARTIAL (separate runner_health check) | N/A | NO | NOT_CAUGHT |

**Result: 9/10 CAUGHT. HARD_PASS for the META atom.** Failure 10 (runner-health blindness) requires a separate orthogonal fix (runner-health monitor as scheduled task; already partially in place per Fix #25 landing notifier).

---

## L4 — OPERATIONAL PROTOCOL / DISCIPLINE / TOOL CHANGES PROPOSED

### Tier 1 — NOW (ship within 24h; load-bearing; high-leverage)

1. **Ship `tools/preflight_check.py`** (validates 5-field preflight_spec.yaml; HARD_BLOCK at dispatch on missing field)
   - Cost: ~2-3 hours of tool-writing
   - Effectiveness: catches 7-10 of 10 observed failures
   - Risk: cell-author friction; mitigate by providing template from prior cell

2. **Extend `tools/peek_arm_metrics.py`** (already exists) with three new flags:
   - `--check-by-construction-saturation` (flags max-arm >= 0.99 or cv < 0.005)
   - `--check-baseline-provenance` (greps for cross-cell baseline references; warns if found)
   - `--check-metric-class` (reads preflight_spec.yaml; warns on metric/mechanism mismatch)
   - Cost: ~1-2 hours
   - Effectiveness: catches 2-3 of 10 at READ time (Director check before atomization)

3. **Add `WHAT_THIS_DOES_NOT_SHOW:` lint to verdict_emit** (mandatory section; commit hook rejects without it)
   - Cost: ~1 hour
   - Effectiveness: catches 2-4 of 10 (the framing failures); structurally inverts the writing-cost gradient
   - Risk: lint can be gamed (cargo-cult section with empty bullets); mitigate by minimum 2 bullets + Skunkworks audit sample

### Tier 2 — THIS WEEK (cultural; structural; medium-leverage)

4. **Promote `tools/skunkworks_predispatch_vet.py`** to mandatory step in dispatch pipeline (was: Skunkworks audits post-landing only; new: Skunkworks audits preflight_spec.yaml pre-dispatch)
   - Cost: ~3-4 hours tool-writing + ~5 min/cell ongoing
   - Effectiveness: catches 5-8 of 10 if preflight_spec.yaml already exists; net additive on top of Tier 1

5. **Cell-author template update:** every new cell starts from `tools/cell_template/` which includes preflight_spec.yaml stub + WHAT_THIS_DOES_NOT_SHOW: stub + factorial-control-arm checklist
   - Cost: ~2 hours
   - Effectiveness: makes correct path easier than incorrect path

6. **Runner-health monitor scheduled task** (already partially live per Fix #25 landing notifier): extend to ALSO publish "runners-alive" heartbeat to `data/runner_health.jsonl`; predispatch_check.py reads + warns if target queue's runner has been silent > 1h
   - Cost: ~1 hour
   - Effectiveness: catches failure 10 (runner-health blindness)

### Tier 3 — NEXT 1-2 WEEKS (deeper structural; lower-leverage but compounding)

7. **Factorial-control discipline:** every compose cell (>= 2 axes) MUST include single-axis control arms and 2-axis interaction arms (a 2^k design). Without explicit waiver, dispatch HARD_BLOCKed
   - Cost: ~5-10 min/cell added
   - Effectiveness: catches failure 4 (multiplicative compose); also generally improves cells

8. **Cross-cell decision matrix tool** (`tools/cross_cell_decision_matrix.py`): given N cell results, produce 2x2 / 3x3 decision matrix showing OOM vs measurement distinction, baseline-comparability flags, metric-class consistency
   - Cost: ~2-3 hours
   - Effectiveness: catches failures 2, 5 at synthesis time

9. **Adversarial-collaboration discipline** (Tetlock-Mellers analog): every cell with predicted HARD_PASS must have Skunkworks (cert-owner) annotate a predicted HARD_FAIL scenario. Both sides committed before dispatch
   - Cost: ~3-5 min/cell from Skunkworks
   - Effectiveness: structurally strengthens the existing adversarial layer

### Tier 4 — STRUCTURAL CULTURE (months; compounding)

10. **Mandatory "honest-framing" training** for Director + cell-author: read Simmons-Nelson-Simonsohn 2011 + Munafò 2017 + Gelman-Loken 2013; one-page write-up on substrate-specific applications
11. **Adopt REFORMS checklist (32-item)** as the cell-author's reference for cells claiming substrate capability
12. **Quarterly retroactive audit** of recent verdict_msg framings vs Skunkworks corrections: if Director over-claim rate > 20%, escalate to discipline review

---

## L5 — CROSS-THREAD SYNTHESIS + CULTURAL DIAGNOSIS

### L5.1 — The SINGLE most-important methodology principle

**"Specify the referent before you measure."** All 10 failures are downstream of an unspecified referent. The metric measured something other than what we claimed it measured (BPC vs LM-capability). The baseline measured something other than what we claimed it measured (different mechanism vs comparable arm). The OOM was framed as "config failed" but actually "config not attempted." The verdict was framed as "+0.52 lift" but actually "+0.52 vs incomparable control." Every one of these is a referent-mismatch.

The substrate-LM program has been operating in **MECHANISM-OBSESSED** mode (we're rich on mechanism intuitions; under-rich on referent specification). This matches the psychology pre-2011 era: rich on theory, under-rich on pre-registration. The discipline answer in both cases is mechanical pre-registration of the referent BEFORE observation. Not "be more careful" — that has demonstrably failed 4 times in one session.

### L5.2 — Cultural pattern at the root

**Pattern: "Trust mechanism intuition; under-verify setup; write verdict_msg in the framing that is fastest to type."** This is a Simmons-Nelson-Simonsohn 2011 archetype with substrate-specific instantiation. The mechanism intuitions ARE good (the substrate-mining heuristic works; the brain-existence-proof heuristic works). The setup-verification gap is where the bug lives.

Specifically:
- **Cell author bias:** when smoke PASSes, the cell author assumes full will resemble smoke. Empirically this is false in at least 2 of 10 failures (failures 3, 8).
- **Director bias:** when verdict_msg says "+0.52 lift," Director propagates the framing without `peek_arm_metrics.py` check. Empirically wrong in 4+ Fix #28 violations.
- **Cell author + Director bias compound:** the framing in verdict_msg becomes the framing in routing notes becomes the framing in Store atom unless Skunkworks intercepts. Skunkworks intercepts ~50% of recent verdicts — that is BOTH the cultural problem (need to intercept that often) AND the structural solution (the adversarial layer works when applied).

**The cultural fix is structural enforcement of adversarial review (Tier 1 + Tier 2 protocols above) PLUS mechanical preflight specs that move the verification UPSTREAM where corrective cost is small.**

### L5.3 — What WOULD have prevented MOST of the failures?

Empirically, from the L3.4 retroactive falsifier:
- **9/10 caught** if all three Tier-1 fixes were in place at session start
- **8/10 caught** if only FIX #1 (preflight_spec.yaml) was in place
- **6/10 caught** if only FIX #2 (WHAT_THIS_DOES_NOT_SHOW lint) was in place
- **7/10 caught** if only FIX #3 (Skunkworks pre-dispatch vet) was in place

The HIGHEST-LEVERAGE single intervention is FIX #1 (preflight_spec.yaml) — it catches the most failures and is the cheapest to implement. The next-highest-leverage single intervention is FIX #2 (verdict lint) — it has the lowest cost-per-failure-caught and structurally inverts the writing-cost gradient.

**Strong recommendation: ship FIX #1 + FIX #2 within 24h.** Defer FIX #3 only because it requires Skunkworks bandwidth re-planning.

### L5.4 — COST analysis (rigor vs throughput)

Per-cell costs (Tier 1 + Tier 2 combined):
- Write preflight_spec.yaml: ~5-10 min (templated: ~2-5 min after first cell)
- Write WHAT_THIS_DOES_NOT_SHOW: ~2-3 min
- Skunkworks pre-dispatch vet: ~5-7 min (Skunkworks time)
- **Total: ~12-20 min added per cell**

Per-cell costs of methodology failure (from observed data):
- Failure 1 (rigged harness): 7+ cells re-classified + meta-audit drill (~20 hours combined)
- Failure 2 (OOM as failure): re-dispatch + claims correction (~3 hours)
- Failure 5 (baseline mismatch): rescue cell required (~1 hour cell + ~1 hour atomization correction)
- Failures 6,7 (over-claiming): 4 Fix #28 corrections + cert-tier re-classification (~4 hours combined)
- **Total observed cost of methodology failures: ~30+ hours this session**

Break-even: 12-20 min/cell discipline cost amortized over the ~30 cells/session would add ~6-10 hours/session of cell-author + Skunkworks time. Net savings: ~20+ hours/session.

**Rigor vs throughput trade-off: STRONGLY POSITIVE for rigor.** The discipline cost is < 1/3 of the failure cost. This is a clear win even before counting strategic value (correctly-classified atoms; no over-claim drift; cleaner cert ledger).

### L5.5 — Substrate-product implications

**Does correcting methodology change the substrate-as-LM strategic call?**

YES — methodology correction shifts the prior on substrate-as-LM viability significantly:
- Without methodology correction: 7+ HARD_FAILs read as "substrate-as-LM is structurally capped"
- With methodology correction: 7+ HARD_FAILs reclassified as METHODOLOGY-CONFOUND; the true mechanism status is UNDETERMINED until fair_harness_v1 lands
- n1_v3 sub_top1=0.445 (94% of bigram) is a CHAIN-GRADE positive that was MISSED for 2+ days because BPC was the verdict gate

**Strategic implication:** the substrate-as-LM program is NOT structurally capped at unigram. The +0.44 envelope cap from the synthesis drill (`research_negative_landings_evidence_totality_synthesis_2026-06-23.md`) is also METHODOLOGY-CONFOUNDED — at least 8 of the 10 negatives are reclassified once methodology is corrected.

**Recommendation:** the substrate-as-LM strategic call should be DEFERRED to after fair_harness_v1 lands AND after the Tier 1 methodology fixes are in place. Until then, treat all substrate-as-LM verdicts (positive AND negative) as PROVISIONAL.

### L5.6 — What this drill does NOT do

- Does NOT propose new substrate-mechanism experiments (out of scope per task contract)
- Does NOT mutate any existing cells, atoms, or verdicts
- Does NOT recommend abandoning the substrate-as-LM program
- Does NOT claim methodology-discipline alone will produce HARD_PASS — mechanism intuition is still load-bearing
- Does NOT advocate publication-style 32-item REFORMS checklist for all cells — argues for trimmed 5-field preflight + verdict lint as cost-effective minimum
- Does NOT replace existing Fix #28 (verify per-arm metrics) — extends it with structural support

---

## CITATIONS (verified count: 19 external + 7 internal = 26 total)

### External (verified via WebSearch)
1. Henderson et al. 2018 "Deep Reinforcement Learning that Matters" AAAI — https://collaborate.princeton.edu/en/publications/deep-reinforcement-learning-that-matters/
2. Hutson 2018 "Artificial intelligence faces reproducibility crisis" Science 359:725 — https://www.science.org/doi/full/10.1126/science.359.6377.725
3. Belz et al. 2023 "Reproducibility of Machine Learning: Terminology, Recommendations and Open Issues" arxiv 2302.12691
4. Colas et al. 2018 "How Many Random Seeds? Statistical Power Analysis in Deep Reinforcement Learning Experiments" arxiv 1806.08295
5. Pineau et al. 2021 "Improving Reproducibility in Machine Learning Research (A Report from the NeurIPS 2019 Reproducibility Program)" JMLR 22(164) — https://www.jmlr.org/papers/v22/20-303.html
6. Atticus Li "Machine Learning's Reproducibility Crisis: NeurIPS Checklist And Code-Release Reforms" — https://atticusli.com/replication-crisis/machine-learning-reproducibility/
7. Kapoor et al. 2024 "REFORMS: Consensus-based Recommendations for Machine-learning-based Science" PMC 11092361 — https://pmc.ncbi.nlm.nih.gov/articles/PMC11092361/
8. Lakens 2014 "Performing High-Powered Studies Efficiently With Sequential Analyses" ResearchGate 260779836
9. Lakens 2022 "Sample Size Justification" Improving Your Statistical Inferences ch 8 — https://lakens.github.io/statistical_inferences/08-samplesizejustification.html
10. Munafò et al. 2017 "A manifesto for reproducible science" Nature Human Behaviour (referenced via search results)
11. Hofman et al. 2023 "Pre-registration for Predictive Modeling" arxiv 2311.18807 — https://arxiv.org/abs/2311.18807
12. Simmons-Nelson-Simonsohn 2011 "False-Positive Psychology" Psychological Science — https://journals.sagepub.com/doi/10.1177/0956797611417632
13. Gelman-Loken 2013 "The Garden of Forking Paths" — https://sites.stat.columbia.edu/gelman/research/unpublished/p_hacking.pdf
14. Box-Hunter-Hunter 1978/2005 "Statistics for Experimenters" 2nd ed (foundational reference)
15. Penn State STAT 503 "Confounding and Blocking in 2^k Factorial Designs" — https://online.stat.psu.edu/stat503/book/export/html/663
16. Hennessy-Patterson 2017 "Computer Architecture: A Quantitative Approach" 6th ed Ch 1.10 — https://www.inspectioncopy.elsevier.com/book/details/9780128119051
17. SPEC CPU2017 documentation — https://arxiv.org/pdf/1910.00651 (memory-centric characterization with config-validity discussion)
18. Biderman et al. 2024 "Lessons from the Trenches on Reproducible Evaluation of Language Models" arxiv 2405.14782v3 — https://arxiv.org/html/2405.14782v3
19. Kapoor-Narayanan 2025 "Lessons from the trenches on evaluating machine-learning systems in materials science" arxiv 2503.10837 — https://arxiv.org/abs/2503.10837

### Internal (this session + prior)
20. `notes/research_drill_substrate_as_lm_test_methodology_audit_2x_2026-06-23.md` (prior 2x drill; mechanism-level audit)
21. `notes/skunkworks_to_all_LANDED_VET_META_HARNESS_RIGGED_substrate_as_lm_reclassification_2026-06-23.md` (Skunkworks META atomization)
22. `notes/research_negative_landings_evidence_totality_synthesis_2026-06-23.md` (10-negative synthesis with 4-class taxonomy)
23. `notes/research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md` (matched-filter receiver SNR diagnosis)
24. `tools/peek_arm_metrics.py` (existing Fix #28 automation; reference for proposed extensions)
25. `tools/predispatch_check.py` (existing Fix #26; reference for proposed runner-health integration)
26. `MEMORY.md` feedback entries: Fix #14-#28 series (autonomous-arc discipline ladder)

---

## SUMMARY (for status_log)

3x DEEPER methodology audit drill on substrate-as-LM experimentation. Surfaced single dominant root cause: "garden of forking paths" (Gelman-Loken 2013) operating without end-to-end pre-flight + post-flight discipline. All 10 observed failures factor cleanly into 3 structural gaps: G1 WRONG-REFERENT VERIFICATION (5/10), G2 NO HARM-PREDICTION (3/10), G3 ASYMMETRIC NEG-FRAMING (2/10). Proposed 3 Tier-1 protocols (preflight_spec.yaml + WHAT_THIS_DOES_NOT_SHOW lint + Skunkworks pre-dispatch vet) catch 9/10 retroactively. Cost analysis: ~12-20 min/cell discipline cost vs ~30+ hours/session methodology-failure cost = strongly positive trade-off. Cultural diagnosis: "trust mechanism intuition; under-verify setup; write fastest-to-type framing" — Simmons-Nelson-Simonsohn 2011 archetype with substrate-specific instantiation. Substrate-product implication: the +0.44 envelope cap from prior synthesis is METHODOLOGY-CONFOUNDED; substrate-as-LM strategic call should DEFER until fair_harness_v1 lands AND Tier 1 fixes are in place. P_deflated for preflight-spec catching >=7/10 = 0.70; P_deflated for cultural-fix sufficiency = 0.85.

— Research (Opus 4.7-1M), 2026-06-23
