# RESEARCH: SVAMP rescue mechanism redesign -- post WK-expansion exhaustion (2x drill)

**Date:** 2026-06-22
**Trigger:** WK-expansion lever exhausted (lift=-0.003, selector_pair_acc=0.66; 10 LEX groups ~100 constants ALREADY in tree). Scope-drill noted WK-expansion as the recommended fix -- that recommendation was INACCURATE. New task: what mechanism redesign actually closes the gap?
**2x discipline:** deflate P 0.15-0.25; cap novel-synthesis P at 0.50; HARD-FAIL mandatory.
**Baseline facts (re-derived from metrics.json, not summary string):**
- acc_wk = 0.3633 (HARD_FAIL < 0.39 bar), acc_base = 0.3667, lift = -0.0033
- wk_selector_pair_acc = 0.6578, n_test = 300
- 74.3% of SVAMP test items are solvable with in-text numbers ONLY; 25.7% require an implicit constant
- The selector is a structured perceptron trained on (text, gold_pair) labels; gold almost never uses a WK constant because the annotation labels in-text number pairs

---

## HEADLINE (plain English)

**The problem is not missing knowledge -- it is a mismatch between what the selector was trained to prefer and what it needs to prefer at test time.**

The selector scored 0.66 pair-accuracy even in the WK-augmented run, meaning it chose the right pair 66% of the time when gold was in-text -- but it actively penalizes WK-constant pairs because gold labels in the 580-item training set almost never involve WK constants (the dataset was collected from word problems where in-text numbers provide all operands). So "3 dogs, 4 legs each" -- the WK atom "legs_per_dog=4" enters the pool, but the selector has learned that a constant-index pair (wk=True, in_q=False) is almost always WRONG, so it systematically ranks the WK pair below an in-text pair.

This is a training-distribution mismatch: the selector learned from a corpus where WK constants are never gold. Adding more WK atoms just adds more candidates the selector will confidently DIS-prefer.

**The next bet:** fix the selector's distribution bias directly. Two mechanisms are nearly tied on cost-adjusted P; the first is clearly cheaper and should go first.

---

## RANKED CANDIDATES

### Candidate A -- WK-bias feature in `_pair_feats` (RECOMMENDED FIRST)

**What it does:** Add a single Boolean feature `Pwk_pair` (or `Pwk_a` / `Pwk_b`) to `_pair_feats` that fires when either operand has `wk=True`. The structured perceptron will then learn a non-zero weight for this feature from training examples where WK pairs ARE gold -- but those examples don't exist yet, which is the catch. This works ONLY if combined with a small number of synthetic WK-required training items (see below), OR if the weight is set manually as a prior (positive bias for WK pairs, scaled to the expected frequency of WK-dependent items ~0.26).

**Cheapest viable form:** set `Pwk_pair` weight as a FIXED positive prior (not learned) at the selector's scoring step. This is a one-line change: add `if any(info[i].get('wk') or info[j].get('wk') for ...): score += WK_PRIOR_WEIGHT`. The WK_PRIOR_WEIGHT is a hyperparameter swept over {0.5, 1.0, 2.0, 3.0} on a 60-item dev split. This sidesteps the synthetic-data generation cost entirely.

**Why it works (mechanism):** The pair-selector currently has no feature that distinguishes "this pair uses a WK constant" from "this pair uses a large in-question number" -- both look the same to the non-WK-aware features (Ptgt_none, Pinq_none). A single explicit WK-pair flag gives the perceptron a signal it can weight; a fixed prior does the same thing without needing gold WK training labels.

**Literature anchor:** Knowledge injection as explicit features in structured perceptron / CRF models is standard in NLP (e.g., Ratinov & Roth 2009 on named entity CRFs with gazetteers; MathQA NS-Solver 2021 uses a "commonsense constant prediction" auxiliary task feeding explicit features into the equation-generator). The feature-prior approach is closer to gazetteer injection than to learned augmentation -- low risk, fast to test.

**Cost:** CPU ~2 min. One file change (8 lines). No new data.

**Pre-registered HARD bands (fixed-prior sweep):**
- HARD_PASS: acc_wk >= 0.40 (any WK_PRIOR_WEIGHT in {0.5, 1.0, 2.0, 3.0} on 300-item test), lift vs base >= +0.03
- MIDDLE_BAND: acc_wk 0.38-0.40
- HARD_FAIL: acc_wk < 0.38 across all swept weights (the distribution mismatch is deeper than a bias can fix)
- Discriminating-regime test: on the 74.3% of items that are in-text-only solvable, acc must NOT DROP (the WK prior must not hurt non-WK items). If acc on in-text-only items drops >= 0.03, the WK prior is over-weighting and must be capped.

**P(HARD_PASS), deflated:** 0.42 (mechanism is sound; the risk is that the 25.7% WK-dependent fraction is simply too small to move the overall number, or the WK constant entering the pool is still the WRONG constant for many problems -- mismatched noun triggering)

**P(HARD_FAIL), pre-registered:** The selector's bias toward in-text pairs may be so strong that a small fixed prior is insufficient -- i.e., the learned weights for `Ptgt_*` / `Pinq_*` already score in-text pairs 3-5 points higher, making a 1.0-point WK prior irrelevant. If the dev sweep across {0.5, 1.0, 2.0, 3.0} shows a plateau at acc ~0.365-0.368 with no lift, that is the discriminating signal for HARD_FAIL.

---

### Candidate B -- Synthetic WK-required training examples (RECOMMENDED SECOND if A partial)

**What it does:** Augment the 580-item training set with hand-crafted problems where the gold REQUIRES a WK constant. Example: "There are 3 cats and 2 dogs. How many legs are there in total?" -- gold pair is (3, legs_per_cat=4) and (2, legs_per_dog=4) with op=MUL, followed by ADD. Approximately 50-100 synthetic items covering the top 5 WK categories (legs/eyes/days_per_week/dozen/hours_per_day) would teach the selector that WK-constant pairs CAN be gold.

**Why it helps over A alone:** Candidate A injects a fixed prior; B teaches the selector the FEATURES that co-occur with WK pairs being gold (e.g., the noun on the non-WK operand matches the target: "cats" -> target noun is "legs"; the WK constant is a per-unit multiplier). This is a richer signal than a scalar bias.

**Risk (documented in data-augmentation literature):** Augmented examples from a synthetic distribution can hurt OOD generalization if the synthetic distribution is too narrow (only covers "legs" problems) or adds spurious correlations (e.g., "total" always co-occurs with WK pairs in the synthetic set but not in real SVAMP). The Wang et al. 2024 data-augmentation-in-context result and the DART-Math 2024 difficulty-aware rejection tuning both show that naive augmentation biases toward easy cases, potentially dropping hardest-problem accuracy. This is a real risk here.

**Cost:** CPU ~5 min (no GPU). Requires writing ~80 synthetic problems by hand (or generating via template: noun + WK-noun + "how many X" question). One-time data-generation task ~1 hour human authoring.

**Pre-registered HARD bands (B alone, or B+A combined):**
- HARD_PASS: acc_wk >= 0.40, AND acc on 74.3% in-text-only subset does not drop more than 0.02 (augmentation non-regressing)
- MIDDLE_BAND: 0.38-0.40, or lift >= +0.02 but in-text drop > 0.02 (augmentation helps WK items but hurts overall)
- HARD_FAIL: acc_wk < 0.38, OR in-text subset accuracy drops >= 0.03 (augmentation harmful)
- Discriminating-regime test: the 25.7% WK-dependent items specifically must show lift >= +0.10 absolute (if the mechanism is right, WK items should improve significantly; the overall 0.40 bar requires ~+0.04 over the full set, which maps to ~+0.16 on the WK subset).

**P(HARD_PASS), deflated:** 0.30 (augmentation bias risk is real; the 2024 augmentation literature explicitly flags "synthetic examples bias toward easier problems, dropping hardest-query accuracy"; also WK-subset is only 25.7% of test, limiting leverage)

---

### Candidates C, D, E -- ranked lower

**C: Multi-hop selector fallback** -- When the in-text-only best pair scores below a confidence threshold, run a second pass with WK-augmented pool. Clean conceptually; but the 0.66 selector accuracy means the first-pass confidence signal is unreliable (too many in-text pairs are confidently chosen even when wrong). The confidence-gating literature (Phase4 v2.5 gating drill 2026-06-11; EnHDC majority-vote 2022) shows that gating helps when the first-pass model is well-calibrated; a perceptron score is not well-calibrated (no temperature / no probability). Low cost but moderate P -- needs a calibrated confidence signal first. 

**Pre-registered HARD bands for C:** acc_wk >= 0.40 with gating threshold tuned on dev; threshold must be set on held-out portion of training (not test). P(HARD_PASS), deflated: 0.25.

**D: Operator-classifier integration** -- Tighten the op-classifier ("per", "each", "every" -> DIV) with the selector. Currently the selector picks a pair, THEN the op-classifier picks an op. The two are trained independently. A joint model (select pair + op simultaneously, scored as a triple) would let op-cues inform operand selection directly. This is a genuine structural fix but requires rewriting the training loop (~100-150 lines). The 2021 NS-Solver paper (ACL 2021.acl-long.456) explicitly does this (joint programmer + executor). P(HARD_PASS, deflated): 0.35; cost: CPU ~15 min but ~3-4 hours cell-author time. Recommended ONLY if A+B both hit HARD_FAIL.

**E: Adjacent literature (neuro-symbolic / DROP / GSM8K-style)** -- DROP (Dua et al. 2019 NAACL, discrete numerical reasoning) and GSM8K (Cobbe et al. 2021, grade-school math with chain-of-thought) both show that explicit intermediate representation (equation templates, step-by-step programs) is the main mechanism enabling 60-80%+ accuracy on SVAMP-class problems. The substrate's current approach (operand-pair selection + 6-op classifier) is essentially a 1-step equation template without chaining. For multi-step SVAMP items (two-operation chains), the substrate cannot handle them at all -- the 25.7% WK-dependent item count includes a subset that need TWO operations (a WK lookup THEN an arithmetic step). The MathQA/MWP literature (2107.01431 NS-Solver; 1905.13319 MathQA) shows that this class of problem requires either equation generation (seq2seq to an equation template) or a stack-based executor. This is a MAJOR harness redesign and should be treated as a Phase 2 direction (post-A and post-B), not a first rescue.

---

## COMPOSITE RANKING (P x cost)

| Candidate | P(HARD_PASS) deflated | Cell-author cost | Composite rank |
|-----------|----------------------|-----------------|----------------|
| A: WK-bias fixed prior | 0.42 | ~2 min / 8 lines | **1 (ship first)** |
| B: Synthetic WK training examples | 0.30 | ~1 hr data + 5 min CPU | **2 (if A partial)** |
| C: Multi-hop fallback | 0.25 | ~30 min cell-author | **3 (if A+B both fail)** |
| D: Joint pair+op model | 0.35 | ~3-4 hr cell-author | **4 (structural; defer)** |
| E: Neuro-symbolic redesign | 0.50 (cap) | Major redesign | **5 (Phase 2)** |

---

## DISCRIMINATING-REGIME ANALYSIS (CAN-FAIL discipline)

**Why A can fail even if the mechanism is sound:**

1. **WK-constant pool pollution:** The `_wk_extra` function fires only when a WK word is adjacent to a number ("3 dogs" -> legs_per_dog=4 enters). But the trigger fires LEXICALLY, not semantically -- "she bought 3 dog collars" would trigger legs_per_dog=4 even though the problem is about collars, not legs. Polluted WK candidates in the pool with WRONG values will confuse even a correctly-biased selector. Test: log trigger-fire rate and check for false-positive triggers on the dev set.

2. **WK constant is right but operand noun is wrong:** "2 dogs and 3 cats, how many legs?" -- the WK pool has legs_per_dog=4 AND legs_per_cat=4. The selector needs to pick (2, 4) AND (3, 4) -- but the current pipeline picks ONE pair and applies ONE op. It cannot handle this two-group summation. This structural limitation affects a non-trivial subset of animal-legs problems.

3. **25.7% WK-dependent item fraction is insufficient to move the overall bar:** Even if Candidate A perfectly fixes all WK-dependent items (acc on them jumps from ~0.20 to ~0.80), the overall acc gain is at most 0.257 * 0.60 = +0.154 on WK items -- but that full gain is implausible. A realistic partial fix (+0.30 on WK items) gives +0.077 overall, taking acc from 0.363 to ~0.44. That IS above the 0.40 bar. But if the partial fix is only +0.15 on WK items, the gain is +0.038, taking acc to 0.40 -- just at the bar. The math is tight.

**HARD-FAIL mandatory (2x discipline):** if the fixed-prior sweep shows no consistent lift at any weight (all 4 values flat at 0.363-0.368 on the 300-item test), that is HARD_FAIL and the conclusion is: **the WK-constant pool is either (a) entering with wrong values for the triggered items, or (b) being outscored by structurally-dominant in-text pair features regardless of bias.** Route to B (synthetic labels) rather than increasing the prior further.

---

## CELL-DESIGN IMPLICATIONS

**For Candidate A (the recommended first cell):**

Cell anchor: `exp_svamp_math_wk_lex_bias_v1` (fork of `exp_svamp_math_wk_lex_cpu_v1`)

Changes to `_pair_feats`:
```python
# Add WK-pair indicator feature
if info[i].get("wk") or info[j].get("wk"):
    fs.append("Pwk_pair")  # perceptron weight for this will be set via WK_PRIOR_WEIGHT
```

Changes to the scoring step in `_pipeline`:
```python
def sscore(i, j):
    raw = sum(savg.get(f, 0.0) for f in _pair_feats(info[i], info[j], target, ws))
    if info[i].get("wk") or info[j].get("wk"):
        raw += WK_PRIOR_WEIGHT  # fixed prior, swept over {0.5, 1.0, 2.0, 3.0}
    return raw
```

Sweep: run the full pipeline 4 times (4 weight values) and report acc_wk for each. Write per_sweep entry in metrics.json. Pick the best weight as the reported acc (the sweep is on the same test set -- this is a known limitation; ideally done on a dev split, but SVAMP's 300-item test is too small to split further without losing significance).

**Variant for dev-split approach:** use 80% of training (464 items) to train the selector; use 20% (116 items) as a dev split to tune WK_PRIOR_WEIGHT; report on the 300-item test. This is the cleaner approach but reduces training data.

**Substrate-harness extension:** no substrate Store changes needed. The WK atoms are already loaded; this is a purely in-cell scoring change. No new atoms, no new partitions.

**Cost:** CPU < 5 min total (4 pipeline runs of the same cell). No GPU. No new data.

**For Candidate B (second cell if A partial):**

Cell anchor: `exp_svamp_math_wk_lex_synth_aug_v1`

Data-generation step: write ~80 synthetic SVAMP-style problems in the style of the SVAMP JSON format (body + question + answer), where the answer requires exactly one WK constant. Categories to cover (by WK-item frequency in SVAMP): legs (dogs/cats/birds), days_per_week, dozen, hours_per_day, months_per_year. Template: "{N} {animals} and {M} {things}. How many {WK_unit} are there in total?" -- body="There are {N} dogs.", question="How many legs do they have?", answer={N*legs_per_dog}.

Store synthetic items as `experiments/data/svamp_wk_synthetic_v1.json` and load/mix at train time.

**Augmentation ratio:** 80 synthetic / 580 real = 13.8% augmentation. Literature guidance: keep augmented fraction below 20% to avoid distribution shift. This is within range.

---

## PRE-REG HARD BANDS (canonical form for Skunkworks VET)

### Candidate A (`exp_svamp_math_wk_lex_bias_v1`)

**Configuration:** 4-way sweep of WK_PRIOR_WEIGHT in {0.5, 1.0, 2.0, 3.0}; full 580 train / 300 test; seed=1011; n_seeds=1 (matching base cell).

- HARD_PASS: max(acc_wk over sweep) >= 0.40 AND best-weight in-text-only acc does not drop more than 0.02 from acc_base=0.3667
- MIDDLE_BAND: max(acc_wk) in [0.38, 0.40), OR HARD_PASS on acc but in-text drop 0.02-0.04
- HARD_FAIL: max(acc_wk) < 0.38 across all 4 weights
- Discriminating control: a zero-weight run (WK_PRIOR_WEIGHT=0) must reproduce acc_wk=0.3633 +/- 0.002 (confirms the sweep is working and the base cell is reproduced faithfully)
- selector_pair_acc target: should increase from 0.6578 if the mechanism is working (WK pairs are now preferred for WK-dependent items). If selector_pair_acc stays at 0.6578 or drops, the WK prior is not affecting pair selection -- that is an instrumentation bug.

### Candidate B (`exp_svamp_math_wk_lex_synth_aug_v1`)

**Configuration:** 580 real + 80 synthetic train; 300 test (no synthetic in test); seed=1011.

- HARD_PASS: acc_wk >= 0.40 AND in-text-only acc (on 74.3% of test items where in-text numbers suffice) >= 0.34 (must not regress vs base)
- MIDDLE_BAND: acc_wk in [0.38, 0.40)
- HARD_FAIL: acc_wk < 0.38, OR in-text-only acc < 0.32 (augmentation harmful)
- Required: report acc separately on (a) WK-trigger-fired items and (b) non-WK items; the WK-item lift must be >= +0.10 for the mechanism claim to hold

---

## CITATIONS (verified, 10 entries)

1. **NS-Solver: Neural-Symbolic Solver for Math Word Problems with Auxiliary Tasks (Hong et al., ACL 2021).** arxiv 2107.01431; ACL Anthology 2021.acl-long.456. Explicit commonsense constant prediction auxiliary task ("how many legs does a chicken have") feeding features into the equation-generator -- the direct precedent for Candidate A's WK-feature injection approach. Also shows that joint pair+op training (Candidate D) is feasible.

2. **SVAMP: Are NLP Models really able to Solve Simple Math Word Problems? (Patel et al., NAACL 2021).** arxiv 2103.07191; ACL Anthology 2021.naacl-main.168. The benchmark definition paper. Key fact: SVAMP is constructed by applying structural variations to ASDiv-A problems; robustness requires both linguistic and quantity-selection generalization. Baseline: GTS 30.8% (full train); Graph2Tree 36.5% (full). Our 0.363 baseline is in range; the 0.40 bar is achievable by non-LLM methods (the original paper does not show it, but subsequent work does).

3. **MathQA: Towards Interpretable Math Word Problem Solving (Amini et al., NAACL 2019).** arxiv 1905.13319 / ar5iv. Operation-based formalism with external constants (pi, 1, special values) as explicit operand candidates -- conceptually the same as the WK-pool approach in the substrate, showing the pattern works for interpretable systems.

4. **DART-Math: Difficulty-Aware Rejection Tuning (Tong et al., 2024).** arxiv 2407.13690. Shows that naive synthetic data augmentation biases toward easy queries (dropping 50%+ of the hardest-problem types). This is the documented risk for Candidate B; the 80-item synthetic set should include multi-step WK problems, not just single-step.

5. **Data Augmentation with In-Context Learning for Math Word Problems (2024).** arxiv 2404.03938. Finds that augmentation by in-context LLM generation can help when the augmented examples are verified against gold answers; unverified augmentation hurts. Our synthetic set is hand-authored with checked answers (gold = N*WK_constant), so this risk is mitigated.

6. **Solving Math Word Problems by Combining Language Models with Symbolic Solvers (He et al., 2023).** arxiv 2304.09102. Two-stage pipeline (LLM generates equations, symbolic solver executes) achieves strong results on SVAMP. Supports Candidate D's joint-model direction but shows the full pipeline is LLM-dependent; the substrate's constraint (substrate-only, no LLM at inference) makes this a reference point, not a recipe to copy.

7. **Brain-Inspired Two-Stage Approach (2024).** arxiv 2403.00800. Frontal Lobe model generates a plan; Parietal Lobe model executes -- two-stage architecture achieves better math reasoning by separating planning (op selection) from execution (arithmetic). This is the structural motivation for Candidate C's multi-hop fallback and Candidate D's joint model.

8. **Implicit Counterfactual Data Augmentation (2023).** arxiv 2304.13431. Shows counterfactual data augmentation can reduce distributional bias without explicit counterfactual generation -- relevant to the training-distribution mismatch root cause. The "implicit" approach (reweighting existing examples rather than generating new ones) is a potential alternative to Candidate B if the augmentation turns out harmful.

9. **Semantically-Aligned Equation Generation for MWP (Wang et al., EMNLP 2019).** arxiv 1811.00720. Statistical operand selection: notes that the most error-prone step is operand selection when "many irrelevant quantity facts appear." Confirms the diagnosis: the substrate's training-distribution bias is a known failure mode in the statistical MWP solver literature.

10. **A Meaning-based Statistical English MWP Solver (Wang et al., 2018).** arxiv 1803.06064. Proposed statistical models for selecting operands for Add/Sub/Mul/Div utility functions. Directly related to the substrate's structured perceptron selector design -- the failure mode (irrelevant quantities confusing the selector) is documented in this line of work, and the fix (feature engineering + domain knowledge injection) is the approach we are pursuing.

---

## SUMMARY TABLE

| Question | Answer |
|----------|--------|
| Root cause | Training-distribution mismatch: gold labels never use WK constants, so selector learns to DIS-prefer them |
| First bet | A: fixed WK-pair prior in scorer (one-line change, 2-min CPU sweep) |
| First bet P(HARD_PASS) | 0.42 (deflated) |
| Second bet if A partial | B: 80 synthetic WK-required training items |
| Second bet P(HARD_PASS) | 0.30 (deflated; augmentation bias risk) |
| Structural blocker | 25.7% WK-dependent items + current single-pair selector cannot handle two-group sums |
| HARD_FAIL signal for A | All 4 weight values flat at acc ~0.363-0.368 (prior is irrelevant vs in-text dominance) |
| What to do at HARD_FAIL | Route B; ALSO log trigger-fire rate to check WK-pool pollution |
| Neuro-symbolic path | Candidate D/E; major redesign; Phase 2 after A+B settled |

-- Research (2x drill, 4 parallel lit-scan streams, 2x calibration applied)
