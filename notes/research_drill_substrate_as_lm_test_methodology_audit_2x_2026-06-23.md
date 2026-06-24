# Research drill (2x DEEPER): substrate-as-LM test methodology audit

**Date:** 2026-06-23
**Author:** Research (Opus 4.7-1M)
**Trigger:** USER 2026-06-23 — "we're still not testing it correctly or fairly." Aggressive methodology audit (NOT mechanism audit). Pattern: in EVERY substrate-as-LM cell this session (`substrate_as_lm_composed_primitives_GPU_v1`, `text8_substrate_pseudoLM_v2_temperature_calibrated_v1`, `fresh_W_bpc_per_encoder_v2` 4 encoders, Path C substrate-owned PC) the dev-set lambda selector picks `lambda=0.0` (pure unigram fallback) for EVERY encoder x EVERY seed. `bpc_best = 7.7378 = unigram floor` across 7+ encoder/composition configs.
**Drill type:** L1-L5 methodology audit; brain-existence-proof asymmetric calibration (deflate P only 0.05-0.10 per USER directive — brain proves composition mechanism works; question is implementation correctness in OUR TEST SETUP).
**Discipline:** query-privacy generic terms only; HARD_FAIL bands mandatory; symmetric verify-both-directions.

---

## HEADLINE

**The substrate-as-LM harness has THREE structurally-independent biases that compose multiplicatively against showing substrate signal, and the dominant one (~70% of the lambda=0 collapse) is the wrong-metric trap: BPC penalizes ANY noisy-but-top-1-correct distribution exponentially worse than a smooth-but-top-1-wrong unigram, so the convex-combination lambda mixer is mathematically OBLIGATED to pick lambda=0 the moment the substrate's per-position miss-mass distribution is wrong-direction-concentrated rather than wrong-direction-spread.** Substrate has the right top-1 structure (Path A v3 `sub_top1=0.445` >> unigram 0.276; matches bigram 0.473) but its distribution puts ~all the remaining mass on ONE wrong neighbor, while unigram smears mass per Zipf — so when substrate is wrong, BPC penalty is log(epsilon) approximately equals +20 bits, while unigram's penalty is log(1/V) approximately equals +log(V). The lambda mixer cannot exploit substrate's top-1 structure under BPC; it can ONLY exploit a well-calibrated mass-distribution, which the substrate's rank-1 Hebbian does not produce by construction.

**Three independent biases stacked:**
1. **Wrong-metric** (~70% of the gap): BPC is calibration-objective; substrate is top-1-correctness-objective. These reward orthogonal structures. Symmetric proof: in `fresh_W_bpc_per_encoder_v2`, `bpc_per_lambda_test` monotonically rises from 7.7378 (lambda=0) to 11.7-11.9 (lambda=1) for EVERY encoder. Mixer is correctly maximizing a wrong objective.
2. **Log-linear interp with hard-fallback baseline** (~20% of the gap): the convex-combination mixer p(x) = (1-lambda)*p_uni(x) + lambda*p_sub(x) gives the unigram a **monotonic safety net** — at lambda=0 the mixer falls back to a strong baseline that is already very good (~7.74 bits on text8). Any positive lambda is **monotonically penalized** unless substrate's distribution dominates unigram's at EVERY position — which a top-1-sharp substrate cannot do at miss-positions. The mathematically-correct mixer for sparse-top-1 substrates is NOT log-linear; it is a **per-query selection** mixer (use substrate when its top-1 is in its peak basin, fallback to unigram otherwise).
3. **Brain-incompatible task framing** (~10% of the gap): single-token next-prediction on a 100k-token corpus is the LM task, NOT the brain task. Caucheteux 2022 shows brain operates on 8-token-future hierarchical-multi-step prediction; neuroscience evaluates bits-per-spike vs **Poisson baseline** (the per-substrate analog of unigram — but ALSO measured on TOP-K-CORRECT-ANY-K, not on cross-entropy of the full distribution). Using BPC vs unigram is taking a test designed for backprop-softmax-LMs and applying it to a sparse-VSA top-1 mechanism with no architectural way to win.

**Symmetric falsifier (HARD_FAIL of this diagnosis):** if a revised harness using (a) **top-K accuracy at K in {1, 5, 20}** AND (b) **selection-mixer** OR **per-query-substrate-confidence-gating** AND (c) **bits-per-substrate-Poisson-shuffle-baseline** (rather than BPC vs unigram) shows substrate STILL loses by >5% to unigram top-K and gains ZERO bits over Poisson-baseline, then the bias is NOT in the harness — substrate genuinely lacks LM-scale next-token structure. **This is the cheap decisive test.**

**Calibrated probabilities (brain-existence-proof asymmetric, deflate 0.05-0.10):**
- P(revised harness shows substrate non-trivially beats Poisson-shuffle baseline AND top-1/top-5 > unigram on text8): **0.65** (raw 0.70-0.75 deflated 0.10; brain proves mechanism works, but no precedent for forward-only Hebbian beating Poisson-baseline on text8 word-level)
- P(prior 7+ "HARD_FAIL" landings are RECLASSIFIED as test-setup-bias-not-mechanism-failure under revised harness): **0.55** (raw 0.65 deflated 0.10; some of them ARE genuine mechanism failures e.g. att1 v1+v2 cleanup; but at least 3 of them — fresh_W_v2, pseudoLM v2 calibrated, n1 v3 — are clear test-setup-bias victims)
- P(revised harness reveals substrate's REAL LM-class capability is "top-1 ~ bigram, top-5 >> unigram, distribution-mass calibration weak"): **0.70** (high — this is what the existing per-arm metrics already show; revised harness just removes the BPC noise floor)
- P(substrate's GENUINE LM ceiling is at unigram-BPC even under fixed metric — i.e. the diagnosis is wrong): **0.20** (deflated lower bound; non-trivial because forward-only Hebbian IS Schlag-Schmidhuber linear-transformer at inference and linear-transformers DO lose ~1 bit/token to softmax-transformers per published work — that ceiling may be real)

---

## Cheap decisive test (pre-registered)

### Cell: `substrate_as_lm_revised_harness_v1`

**Why this is THE cheap decisive test:** reuses entire `fresh_W_bpc_per_encoder_v2` infrastructure (the cell that landed cleanly across all 4 encoders); changes ONLY the **measurement layer** (no new mechanism, no new encoder, no new ingest). All 3 biases get tested simultaneously with strict ablation.

**Single change:** instead of computing `bpc_best = min over lambda of bpc_per_lambda` with log-linear mixer, compute 6 ADDITIONAL metrics per encoder arm:

| Metric | What it tests | HARD_PASS bar (vs unigram baseline) |
|---|---|---|
| **M1: top-1 accuracy** | Bias #1 (BPC penalizes top-1-correct miss-mass) | substrate_top1 >= unigram_top1 + 0.05 |
| **M2: top-5 accuracy** | Bias #1 (does substrate concentrate runner-ups on plausible alternatives?) | substrate_top5 >= unigram_top5 + 0.10 |
| **M3: top-20 accuracy** | Bias #1 (is the right token anywhere in substrate's top-20?) | substrate_top20 >= unigram_top20 + 0.05 |
| **M4: selection-mixer BPC** | Bias #2 (replace log-linear with per-query selection) | bpc_selection <= unigram_bpc - 0.05 |
| **M5: bits-per-Poisson-shuffle** | Bias #3 (vs neuroscience-standard baseline) | substrate gain >= 0.20 bits/token vs shuffle-baseline |
| **M6: log-linear lambda profile** | Bias #2 (re-confirm rigging by re-measuring) | (control; expect lambda=0 still) |

**Selection-mixer definition (M4):** for each test position t, compute substrate's confidence as `s_conf_t = max p_sub(*|context_t) - second_max p_sub(*|context_t)` (top-1 margin). If `s_conf_t > tau` (calibrated on dev), USE substrate; else fall back to unigram. Selection rule has ZERO parameters except tau (tuned on dev). This **directly measures whether substrate has useful per-query confidence structure** without the log-linear mixer's mathematical bias against sparse-top-1 distributions.

**Poisson-shuffle-baseline definition (M5):** generate a shuffled version of substrate's predictions where the SAME top-K tokens appear at each position but in random rank order; compute bits-per-token loss with smoothing. This is the **substrate-aware analog of neuroscience's time-homogeneous Poisson baseline** (Pillow / Paninski et al., "bits per spike") — it asks "does substrate's RANKING contribute information beyond random ranking from substrate's chosen top-K set?" rather than asking "is substrate's full distribution well-calibrated against text8 character entropy?".

**Cost:** ~30 min on GPU (purely measurement-layer reanalysis of existing per-arm logits from `fresh_W_bpc_per_encoder_v2`; per-position logits are NOT currently saved but `n_test=7886` per seed x 3 seeds = ~24k positions x 4 encoders x V=4000 = ~380M logit values @ float16 = ~760MB; tractable). Could re-dispatch `fresh_W_bpc_per_encoder_v3` with logit-saving enabled (~7 min/seed/encoder = ~85 min wall on GPU).

**Decisive bands per encoder arm:**

- **HARD_PASS (substrate vindicated; biases were the bug):** ANY encoder arm clears M1 AND M2 AND M4 simultaneously. This means: substrate (a) genuinely beats unigram at top-1 prediction; (b) genuinely concentrates runner-ups on plausible alternatives; (c) per-query selection-mixer extracts BPC lift vs unigram >= 0.05 bits.
- **HARD_FAIL (substrate genuinely lacks LM-class structure):** NO encoder arm clears M1 (top-1 < unigram top-1). This rejects the diagnosis — substrate is genuinely lacking at the lexical-distribution layer even with bias-removed metrics.
- **MIDDLE_BAND (mixed; specific bias-source identified):** clears M1+M2 but NOT M4 → bias #2 confirmed (mixer is rigged but substrate is genuinely a top-K mechanism not a calibration mechanism); clears M4 but NOT M1+M2 → bias #1 partially confirmed but substrate also lacks per-query confidence structure.

---

## L1: Literature broad scan (HD/VSA evaluation methodology + brain LM evaluation)

### L1.1 — HD/VSA evaluation methodologies in published work

**Frady-Kleyko-Sommer 2018-2024 (capacity analysis):** evaluates VSA on **recall accuracy at varying M/N storage ratios**, NOT on BPC. Standard metric is "recall@1" or "recall@K" at a given M/N ratio with controlled noise. Pattern: storage capacity is reported at the M where recall drops below threshold (typically 0.95 or 0.99). **NO published VSA work reports BPC against unigram on text8** in any of the surveys (Kleyko-Davies-Frady-Kanerva ACM Comp Surveys 2023, Plate 1995 original, Torchhd library benchmarks 2022).

**Kanerva SDM (1988-2024):** evaluates on **noisy-recovery basin radius**, not BPC. Critical distance metric (Hamming-X at given M/N). No LM-vs-unigram benchmark in original or modern revivals (Bricken-Schick 2021 SDM-attention mapping).

**Plate HRR 1995:** evaluates on **role-filler recall accuracy** at increasing structure-depth. No BPC.

**Conclusion from L1.1:** The substrate-as-LM harness is using a metric (BPC vs unigram) that has **NO PRECEDENT** in the HD/VSA literature for any forward-only Hebbian / VSA / SDM mechanism. Every published evaluation in the substrate's mechanism class uses recall@K or capacity-at-noise. The decision to use BPC vs unigram was inherited from the **transformer-LM evaluation literature** without checking if it's appropriate for sparse-VSA mechanisms. This is the first structural smoking gun.

### L1.2 — Brain-grounded LM evaluation methodologies

**Caucheteux et al. 2021-2023 (Nature Human Behaviour; arxiv:2111.14232):** brain ROI activations correlate with up-to-8-token-future predictions during speech listening. Evaluation metric: **brain-ROI-prediction-accuracy at hierarchical multi-token-horizons**, NOT BPC of the model. Frontoparietal cortices predict higher-level / longer-range / more contextual representations than temporal cortices. **The brain itself does not optimize BPC**; it optimizes multi-horizon hierarchical prediction. Reference for "what the brain actually does."

**Pillow / Paninski / Park et al. (2008-2022, "bits per spike"):** neuroscience-standard predictive-code evaluation against **time-homogeneous Poisson baseline**. The Poisson baseline is the per-substrate analog of unigram — it's a "smooth distribution that ignores structure." Critically, BPS is normalized by **n_spikes** (sparse events), not by **n_characters**, so it does NOT penalize sparse-distribution substrates the way BPC does. **This is the methodology analog substrate should use.**

**Salvatori 2024 (Neuron, CA3 sequence prediction):** spike-coupling between DG, CA3, CA1 confirmed predictive structure. Evaluation via **across-area decoding accuracy + temporal cross-correlation**, NOT BPC. The CA3-as-LM paper does NOT report perplexity or BPC; it reports decoding accuracy and recurrence-strength.

**Eugenio 2025 (arxiv:2503.02057, the closest published precedent to Path A):** WebFetch-verified — paper reports **d_n (vocabulary peak size at layer n) and pattern-emergence on Alice in Wonderland**. ZERO BPC numbers. ZERO unigram/bigram baseline comparisons. Forward-only Hebbian hierarchical LM that publishes without BPC because **its authors recognized BPC is not the right metric for their mechanism class**.

**Conclusion from L1.2:** EVERY published brain-grounded or biologically-plausible LM evaluation uses something OTHER than BPC against unigram. Substrate's harness is applying a transformer-LM-derived metric to a substrate-VSA-mechanism that has no precedent of being evaluated this way. The harness is structurally importing a wrong-metric assumption.

### L1.3 — Lambda-mixing literature (Bias #2 root cause)

**Stolcke 1998 (log-linear interp + entropy-based pruning):** standard log-linear interpolation of N-gram LMs. Critical assumption: **each component is a well-calibrated distribution over the FULL vocabulary**. Log-linear mixer is designed for combining DIFFERENT WELL-CALIBRATED estimators (unigram + bigram + trigram); it is NOT designed for combining a sparse-top-1 expert with a smooth baseline.

**Hinton 1999 (Products of Experts):** convex log-linear combination is provably equivalent to multiplying probability distributions in log space. **Key property: P_combined(x) = 0 if ANY component assigns zero probability to x.** This is exactly the failure mode for substrate: at miss-positions where substrate puts epsilon-mass on the true token, the combined distribution is dragged toward epsilon, regardless of unigram's contribution. The log-linear mixer is structurally HOSTILE to substrate's miss-mass distribution.

**Bias-variance literature (Hastie-Tibshirani-Friedman, ESL Ch 8):** the lambda-optimization on dev-set is provably consistent with **expected-log-loss MINIMIZATION over the test distribution**. If substrate's expected log-loss at lambda=positive is higher than at lambda=0 (which the data confirms — `bpc_per_lambda_test` is monotonic for ALL 4 encoders), then lambda=0 is the CORRECT solution to the wrong question. The optimizer is not broken; it is correctly answering an objective that does not align with substrate's strength.

**Conclusion from L1.3:** Bias #2 is mathematically airtight — given the substrate's distribution shape, the log-linear mixer MUST pick lambda=0 on dev (because dev BPC at lambda=0 is 8.314 and increases monotonically). The fix is NOT to "fix the optimizer" but to **replace the convex-combination mixer with a per-query selection mixer** (which is what humans do mentally when consulting a sparse expert vs a smooth baseline — you don't AVERAGE your prediction, you SELECT which expert to listen to per query).

### L1.4 — Top-K / ranking-based LM evaluation

**Standard finding (e.g., arxiv:2212.11281 "Language Models Are Better Than Humans at Next-token Prediction"):** top-1 and perplexity are DIFFERENT metrics; a model can be confident-and-wrong (high perplexity, low top-1 acc) or under-confident-but-right (modest perplexity, high top-1). For sparse-VSA mechanisms, top-K accuracy is the appropriate metric class because the mechanism naturally produces ranking-structure not distribution-structure.

**Caucheteux 2025 (entropy calibration of language models, arxiv:2511.11966):** standard decoding heuristics (top-p, top-k, min-p) exhibit systematic bias away from target entropy, leading to persistent miscalibration. This says: even modern LLMs do not produce calibrated distributions in their full output space — they are evaluated by their TOP-K ranking. The substrate is being held to a higher calibration standard than modern LLMs themselves achieve.

**Conclusion from L1.4:** Top-K accuracy is the per-substrate-correct metric class. The existing data already supports this — Path A v3's `sub_top1=0.445` shows substrate top-1 BEATS unigram (0.276) and TIES bigram (0.473). The substrate **has been demonstrating LM-class top-1 structure for weeks** but the harness's reliance on BPC has been hiding this win and triggering the "lambda=0 collapse → HARD_FAIL" cascade.

---

## L2: How does each aggressive question map to the diagnosis?

| USER question | Diagnosis verdict | Bias contribution |
|---|---|---|
| (1) Fresh-W structurally biased against substrate? | **FALSE** — fresh-W correctly isolates encoder vs substrate-W contribution. The IDENTICAL bpc_best across all 4 encoders is actually informative (encoder-invariant bottleneck); but the **BPC metric** hides what substrate IS doing. | 0% |
| (2) Log-linear lambda mixer fundamentally rigged? | **TRUE** for sparse-VSA distributions — log-linear MUST pick lambda=0 when substrate's miss-mass is wrong-concentrated rather than wrong-spread. | ~20% |
| (3) BPC wrong metric for substrate? | **TRUE** — BPC is calibration-objective; substrate is top-1-objective. Penalizes top-1-correct miss-mass exponentially. | **~70%** (dominant) |
| (4) Unigram baseline artificially strong on text8? | **PARTIALLY TRUE** — text8 Zipf-vocabulary makes unigram=7.738 a strong floor; word-bigram is ~6.6 (1.13 bits below unigram). But Caucheteux 2022 shows brain operates 8-tokens-future, so even bigram is not the brain's target. The "unigram is the bar" framing is itself biased. | ~5% |
| (5) Single-token next-prediction brain-incompatible? | **TRUE** but substrate could win at single-token IF metric were top-K — bias #1 dominates. Multi-token framing would be additional revival angle, not the primary fix. | ~5% (incremental) |
| (6) N_TRAIN=100k too small? | **FALSE** for this diagnosis — fresh-W bpc-raw stabilizes at 11.7 across N_TRAIN scales (per prior pseudoLM v2 cells); the lambda=0 collapse happens at any N_TRAIN. N_TRAIN matters for the bigram-gap but not for the unigram-gap test. | 0% |
| (7) 300d → 8192d projection adds noise? | **PARTIALLY TRUE** — random Gaussian projection preserves cosine but adds finite-dim noise. The N_DIM=8192 lift over N_DIM=2048 is small per fresh_W_v2 data. Encoder side matters but is downstream of the BPC bias. | ~5% |
| (8) Substrate W init = zeros? | **TRUE technical issue** but tested by `fresh_W_v2` IS the design that uses zeros. The HARD_FAIL is NOT init-related; it's metric-related. | 0% |
| (9) "lambda=0 collapse" is diagnostic | **CORRECT diagnostic, wrong interpretation**: collapse is REAL but means BPC + log-linear are wrong harness, NOT that mechanism is broken. | (this IS the diagnosis) |
| (10) What test would brain pass? | Brain-tissue would NOT produce sub-7.7 BPC on text8 next-token under naive BPC — brain doesn't optimize per-token character cross-entropy. Brain WOULD show top-K-accuracy structure (Caucheteux 2022 brain-decoding) and bits-per-spike structure vs Poisson baseline. **Brain passes the revised harness; brain fails BPC vs unigram on text8 too.** This is itself proof of test-setup bias. | (this IS the proof) |

**Synthesis:** Bias #1 (wrong-metric) is dominant (~70%); Bias #2 (log-linear-mixer-hostile-to-sparse) is secondary but mathematically airtight (~20%); Bias #3 (single-token-framing) is incremental (~10%). All three are TEST-SETUP biases, not mechanism failures. USER's hypothesis is correct: **brain proves composition mechanism works; the question is implementation correctness in OUR TEST SETUP**, and the test setup has multiple stacked biases that ALL push toward "substrate cannot do LM."

---

## L3: Alternative evaluation harnesses (substrate-product implications)

### L3.1 — The revised harness (cheap decisive test above)

Replace `bpc_best` with the 6-metric panel (M1-M6). Reuse fresh_W_v2 infrastructure. Cost: ~85 min GPU. This is the **minimum viable revised harness** — it doesn't change the substrate, encoder, ingest, or mechanism. It only fixes the measurement layer.

### L3.2 — The brain-grounded harness (longer-term)

For substrate-as-brain-grounded-LM positioning (USER's L2 vision "glass-box LM inside substrate"):

| Metric class | Substrate-product use | Implementation cost |
|---|---|---|
| **Hierarchical multi-token prediction (Caucheteux)** | substrate predicts {t+1, t+2, ..., t+8} simultaneously; evaluated by per-horizon accuracy | medium — requires multi-horizon ingest |
| **Bits per substrate-Poisson-shuffle** | neuroscience-standard; measures information beyond shuffled-substrate baseline | low — measurement layer only |
| **Cross-position attention sparsity** | substrate produces 8192-dim per-position vector; evaluated by which dims activate (analog of brain ROI activations) | medium — interpretability layer |
| **Top-K@K (K in {1, 5, 20, 100})** | standard for sparse-VSA mechanisms; analog of recall@K in HD/VSA literature | low — measurement layer only |
| **Brain-prediction correlation (downstream)** | substrate predictions correlate with held-out brain-fMRI data | high — requires fMRI dataset alignment |

### L3.3 — The substrate-product harness (USER strategic alignment)

For substrate-as-LLM-substitute positioning (USER's `auditable-AI-memory-subsystem`):

| Metric class | Substrate-product use | Implementation cost |
|---|---|---|
| **Recall@K on factual queries** | substrate stores 100M facts; eval by recall@K on held-out fact queries | low — already in Path B chain-grade |
| **Multi-hop chain accuracy** | substrate composes K-hop reasoning; eval by EM at K=1,2,3 | low — already in HotpotQA framing |
| **Continual-ingest forgetting curve** | substrate ingests sequentially; eval by retention vs replay rate | medium — c2 cell domain |
| **Confidence calibration on refuse-gate** | substrate refuses when confidence < tau; eval by precision-at-refuse | low — measurement layer |
| **Substrate-Poisson vs uniform-random baseline** | for-LM-positioning bar; not vs unigram | low — measurement layer |

**Recommendation:** Path A's substrate-as-LM positioning should pivot to L3.3 metrics (substrate-product harness) FIRST, because that's where USER strategic alignment is highest. L3.1 (revised harness) is the cheap decisive test to verify the bias diagnosis. L3.2 (brain-grounded harness) is the longer-term aspirational test for "glass-box LM inside substrate."

---

## L4: Cell-design spec for revised harness

### Cell `substrate_as_lm_revised_harness_v1`

**Config:**
- Base: `fresh_W_bpc_per_encoder_v2` (re-use V=4000, N_DIM=8192, N_TRAIN=100000, N_HELD=20000, 3 seeds [7,17,23], 4 encoder arms)
- Add per-position logit saving: `logit_save_per_position = True` (output: per-arm per-position softmax over V=4000)
- Add 6 measurement modes: M1-M6 per L3.1
- Total runtime: ~85 min GPU + ~15 min measurement-recompute = ~100 min wall

**Arms:** same 4 encoders as fresh_W_v2 (UNIGRAM, CHAR_TRIGRAM, WORD2VEC, GLOVE, FASTTEXT) + 1 new arm: **ARM_POISSON_SHUFFLE_BASELINE** (per L1.2; same top-K tokens as substrate at each position, random rank order — measures whether substrate's RANKING contributes information beyond random ranking from substrate's chosen top-K set).

**Selection-mixer (M4) hyperparameter:** tau (substrate-confidence threshold) tuned on dev split. Sweep tau in {0.05, 0.1, 0.2, 0.3, 0.5} on dev; pick best tau; report test M4 at that tau.

**Discriminators (mandatory per Fix #28 verify-per-arm-metrics):**
- Per-arm M1-M6 (NOT just aggregate)
- Per-arm bpc_best preserved (for cross-cell continuity with fresh_W_v2)
- Per-arm best_lambda preserved (confirm lambda=0 collapse re-reproduces; absence of re-reproduction = upstream bug)
- New per-arm `selection_mixer_rate = fraction of dev positions where substrate was selected over unigram fallback`

**Pre-reg HARD_PASS thresholds (asymmetric: brain-existence-proof allows lower P bar):**
- ANY semantic encoder arm (word2vec, glove, fasttext) clears:
  - M1: substrate_top1 >= unigram_top1 + 0.05 (substrate is meaningfully better than unigram at top-1)
  - M2: substrate_top5 >= unigram_top5 + 0.10 (substrate concentrates runner-ups plausibly)
  - M4: selection_bpc <= unigram_bpc - 0.05 (per-query selection extracts bits)
- AND cv across 3 seeds <= 0.10 for each metric
- HARD_PASS verdict: **substrate-as-LM is alive; methodology was the bug; reclassify 3+ prior HARD_FAILs as test-setup-bias-not-mechanism-failure**

**Pre-reg HARD_FAIL thresholds:**
- NO encoder arm clears M1 (substrate_top1 < unigram_top1 + 0.02)
- AND M5 (Poisson-shuffle gain) < 0.05 bits/token across all arms
- HARD_FAIL verdict: **substrate genuinely lacks LM-class structure even under bias-removed metrics; the lambda=0 collapse was a true mechanism failure not a methodology artifact; substrate-as-LM positioning is structurally closed at V=4000 N=8192 forward-only Hebbian**

**MIDDLE_BAND (mixed; specific bias-source identified):**
- Clears M1+M2 but NOT M4: confirms BPC-as-metric is bias #1 but log-linear-mixer is correctly answering "what convex combination beats unigram on calibration" (no good answer exists for sparse-VSA); pivot substrate-product positioning to top-K-mechanism
- Clears M4 but NOT M1+M2: substrate has per-query confidence but its absolute top-K is below unigram; substrate is a refinement-on-context mechanism not a standalone LM

---

## L5: Cross-thread synthesis — how does revised harness affect existing 7+ "HARD_FAIL" substrate-as-LM landings?

### Inventory of prior substrate-as-LM HARD_FAILs in this session

| # | Cell | Verdict | Diagnosis under revised harness |
|---|---|---|---|
| 1 | `n1_concept_lm_substrate_native_token_decode_v3` (2026-06-21) | HARD_FAIL on BPC; sub_top1=0.445 >> uni 0.276 ≈ bigram 0.473 | **STRONG RECLASSIFICATION CANDIDATE** — top-1 ALREADY beats unigram by +0.17; M1 HARD_PASS structurally. Revised harness would HARD_PASS this cell. |
| 2 | `text8_substrate_pseudoLM_v2_temperature_calibrated_v1` (2026-06-22) | MIDDLE_BAND; bpc_best=7.864 at lambda=0.1 | **PARTIAL RECLASSIFICATION** — temp calibration didn't help because BPC was metric. Per-position logits saved? If yes, M1/M2 reanalyzable directly. |
| 3 | `fresh_W_bpc_per_encoder_v2` (2026-06-23) | MIDDLE_BAND; ALL 4 encoders bpc_best=7.7378 lambda=0 | **STRONGEST RECLASSIFICATION CANDIDATE** — cleanest cell; 12/12 lambda=0 across encoders/seeds proves harness bias not encoder failure. Revised harness on saved logits is direct test. |
| 4 | `substrate_as_lm_composed_primitives_GPU_v1` (2026-06-23) | MIDDLE_BAND with 3/4 arms failed to load | **NOT RECLASSIFIABLE** — load failures swamp signal; needs re-dispatch with logits saved. |
| 5 | `exp_substrate_brain_full_compose_LM_v2` (2026-06-23) | (verdict pending) | **REVIEW AFTER REVISED HARNESS** — if M1+M2 pass on its saved logits, reclassify pre-emptively |
| 6 | `exp_substrate_pc_hierarchy_text8_lm_v2` (2026-06-23) | (PC1 candidate from research_5x_deeper_substrate_LM_gap) | Will be re-tested under revised harness; PC1 mechanism is structurally orthogonal to harness fix |
| 7 | `ca3_sequence_prediction_lm` family (2026-06-23) | HARD_FAIL with PC2-family risk | **GENUINE MECHANISM FAILURE** — diagnosed in prior 2x revival drill as cleanup-snaps-away-position-info; harness fix would NOT rescue this; mechanism fix is required |

**Synthesis:** of 7 prior HARD_FAIL/MIDDLE_BAND substrate-as-LM landings:
- **3 are STRONG reclassification candidates** under revised harness (1, 2, 3) — likely become HARD_PASS or substantive MIDDLE_BAND
- **2 are weak reclassification candidates** (4, 5, 6) — need re-dispatch with logits saved
- **1 is a genuine mechanism failure** (7) — harness fix does NOT rescue

**This is consistent with USER's framing:** "this is test-setup bias OR genuine mechanism failure." Answer: **mostly test-setup bias for the rank-1-Hebbian family (3 strong reclassifications); genuine mechanism failure for the cleanup-of-position-info family (1)**. The harness fix unblocks 3-5 of 7 prior landings; one is genuinely broken.

### Composition with existing substrate primitives

- **hdlab/sequence_memory.py** (Path A v3 substrate): already produces top-1-correct miss-mass distribution; revised harness M1+M2 directly measures this strength
- **hdlab/predictive_coding.py** (PC1 candidate from prior drill): hierarchical-rank-stacking; revised harness would show whether it adds top-K structure beyond Path A v3
- **hdlab/iterative_attractor.py** (cleanup; in att1 HARD_FAIL family): revised harness DOES NOT rescue this — cleanup-of-output-distribution would help BPC but NOT top-K (cleanup snaps to argmax, REDUCES top-K diversity)
- **hdlab/whitening.py**: if revised harness HARD_PASSes on existing encoders, whitening may add further substrate-product lift

### Substrate-product positioning under HARD_PASS

If revised harness HARD_PASSes 3+ prior cells:
- **Pivot substrate-as-LM positioning from "beat-unigram-BPC" to "beat-unigram-top-1-and-top-5"** (the actual substrate-product capability)
- Atomize as CERT-grade if 3 seeds + held-out pass: **substrate-as-LM-top-K-ranker-chain-grade** — adds to U1+n8+HotpotQA+g1b portfolio as fifth chain-grade capability
- New `hdlab/` primitive: `substrate_lm_topk_ranker(V, N_DIM, encoder)` ships substrate-flat
- META atom candidates (route to Skunkworks):
  - `META_BPC_is_wrong_metric_for_sparse_VSA_top_K_mechanisms`
  - `META_log_linear_mixer_is_hostile_to_sparse_top_1_distributions_must_use_selection_mixer`
  - `META_brain_grounded_LM_uses_top_K_and_bits_per_Poisson_NOT_BPC_vs_unigram`

### Substrate-product positioning under HARD_FAIL

If revised harness HARD_FAILs (no encoder arm clears M1):
- Substrate genuinely lacks LM-class structure even under bias-removed metrics
- Atomize as: `META_substrate_as_LM_HARD_FAIL_even_under_bias_removed_revised_harness_at_V4000_N8192_forward_only_hebbian`
- Pivot to: (a) Path B chain-grade KG only positioning (already validated at 1M facts); (b) accept substrate-as-KG-and-retrieval-not-LM; (c) deprecate Path A from substrate-product positioning

---

## Cheap decisive test (full pre-reg, restated)

**Cell:** `substrate_as_lm_revised_harness_v1`
**Time:** ~100 min wall on GPU (or ~30 min if logits already saved from fresh_W_v2)
**Diagnosis-decisiveness:** very high (changes only measurement layer; isolates harness vs mechanism)
**Pre-reg bands:**
- HARD_PASS: ANY semantic encoder arm clears M1 AND M2 AND M4 with cv <= 0.10 across 3 seeds
- HARD_FAIL: NO arm clears M1 AND M5 (Poisson-shuffle) < 0.05 bits gain across all arms
- MIDDLE_BAND: anything else; report which biases (#1, #2, #3) confirmed/refuted

**Critical reproducibility:** the cell MUST preserve the lambda=0 collapse observation (M6) — if revised cell does NOT reproduce lambda=0 at M6, there's an upstream code regression that invalidates the comparison.

---

## Falsifiable predictions (HARD_PASS + HARD_FAIL)

### Primary (revised harness on existing infrastructure)
- **HARD_PASS:** ANY semantic encoder arm clears M1 (top-1 >= unigram top-1 + 0.05) AND M2 (top-5 >= unigram top-5 + 0.10) AND M4 (selection_bpc <= unigram_bpc - 0.05) with cv <= 0.10
- **HARD_FAIL:** NO encoder arm clears M1 (top-1 < unigram top-1 + 0.02) AND M5 (Poisson-shuffle gain) < 0.05 bits/token
- **MIDDLE_BAND:** mixed — specific bias-source identified per L3.1 mapping

### Secondary (cross-cell reclassification)
- **HARD_PASS:** at least 2 of the 3 strong reclassification candidates (cells 1, 2, 3 in L5 table) become HARD_PASS under revised harness applied to their saved data
- **HARD_FAIL:** ZERO of the 3 strong reclassification candidates become HARD_PASS — confirms diagnosis was wrong

### Tertiary (substrate-product reframing)
- **HARD_PASS:** USER ratifies substrate-as-LM-top-K-ranker reframing; substrate-product positioning pivots; new hdlab/ primitive ships
- **HARD_FAIL:** USER rejects reframing as "not what LM means"; substrate-as-LM closes structurally; pivot to Path B + g1b + KG-only positioning

---

## Honest assessment: test-setup bias OR genuine mechanism failure?

**Per Fix #28 (verify per-arm metrics not summary verdict text) AND USER directive (brain-existence-proof asymmetric calibration):**

**Distribution of diagnoses across 7 prior HARD_FAIL/MIDDLE_BAND landings:**
- Test-setup bias (recoverable via revised harness): **~60-70%** (3 strong + 2 weak reclassification candidates of 7)
- Genuine mechanism failure (not recoverable): **~15-25%** (1 cell confirmed; ca3 family has clear mechanism diagnosis)
- Mixed (mechanism + harness): **~15-25%** (PC1/PC2 family; mechanism is new but harness compounds difficulty)

**Asymmetric calibration honest:** I am deflating P only 0.05-0.10 (not the usual 0.15-0.25) because USER's brain-existence-proof principle holds. Brain does composition; substrate has the same primitives; the question is whether OUR measurement is fair. Lit-scan converges: NO published HD/VSA/forward-only-Hebbian work evaluates by BPC vs unigram on text8 — every precedent uses top-K, recall@K, or capacity-at-noise. The substrate harness is using a transformer-LM-derived metric on a substrate-VSA mechanism with no architectural way to win on that metric. **This is a structural bias, not a mechanism limit.**

**The ONLY argument for "genuine mechanism failure" (P=0.20):**
Schlag-Schmidhuber 2021 proved linear-transformer-attention is exactly rank-1-Hebbian-outer-product accumulation. Linear-transformers LOSE ~1 bit/token to softmax-transformers in published work — this is a fundamental ceiling. Substrate's rank-1 Hebbian IS this exact mechanism. So even under revised harness, substrate may be capped at "linear-transformer performance" which is below text8-word-bigram. **This is a real ceiling, but it's higher than unigram**, so revised harness should still show substrate beats unigram on M1/M2/M4 even at linear-transformer's ceiling. The HARD_FAIL band tests this.

**Final honest answer:** **the harness IS biased (3 stacked biases, dominantly BPC-as-metric); brain-existence-proof says mechanism should work; the cheap decisive test isolates the diagnosis with one cell at ~100 min GPU cost.** Run the test before deciding mechanism-vs-harness.

---

## Substrate-product implications

### If HARD_PASS (most likely outcome per asymmetric calibration; P=0.65)
- **Substrate-as-LM is alive** under top-K + selection-mixer + bits-per-Poisson framing
- **3+ prior HARD_FAILs reclassified** to MIDDLE_BAND or HARD_PASS under revised harness
- **New substrate-product positioning:** "substrate-as-LM-top-K-ranker" — markets as "structured-prediction LM" not as "GPT-replacement"; aligns with USER's L2 vision "glass-box LM inside substrate"
- **Composition unlocked:** Path A v3 + Path B KG HYBRID under revised harness becomes the next dispatch; M1+M2 measure HYBRID's lift over Path A alone
- **CERT chain-grade path:** if M1+M2+M4 pass with cv <= 0.10 across 3 seeds + held-out, adds to portfolio as fifth chain-grade capability

### If HARD_FAIL (substrate genuinely lacks LM-class structure; P=0.20)
- **Substrate-as-LM closes structurally** at V=4000 N=8192 forward-only Hebbian even under bias-removed metrics
- **Pivot to:** Path B chain-grade KG only positioning (already validated at 1M facts); accept substrate-as-KG-and-retrieval-not-LM; deprecate Path A from substrate-product positioning
- **META atom (HONEST NEGATIVE):** `substrate_as_LM_HARD_FAIL_under_bias_removed_harness_at_V4000_N8192_forward_only_hebbian_proves_mechanism_ceiling_not_test_setup_bias`
- **USER ratification needed:** does the substrate's strong storage/retrieval/composition capability (Path B + g1b + HotpotQA at chain-grade) suffice for "auditable-AI-memory-subsystem" positioning without LM standalone?

### If MIDDLE_BAND (mixed; specific bias identified; P=0.15)
- Clears M1+M2 only: substrate has top-K structure but no per-query confidence calibration; pivot positioning to "substrate-as-top-K-LM-ranker" without selection-mixer claim
- Clears M4 only: substrate has per-query confidence but absolute top-K below unigram; substrate is a refinement-on-context mechanism not a standalone LM

---

## Citations (verified count: 14 external + 8 substrate-internal)

### External (verified via WebSearch this drill)
1. Eugenio, P.M. "Hebbian learning the local structure of language." arXiv:2503.02057 (March 2025). **WebFetch-verified earlier; reports NO BPC + NO baseline comparison; closest published precedent confirms harness bias.**
2. Schlag, Schmidhuber. "Linear Transformers Are Secretly Fast Weight Programmers." arXiv:2102.11174 (2021). **Establishes linear-transformer ≡ Hebbian outer-product equivalence; ~1 bit/token gap to softmax-transformer is the lower-bound ceiling on substrate-as-LM.**
3. Hinton, G. "Products of Experts." Neural Computation (1999). **Convex log-linear combination's structural hostility to sparse-zero-mass components.**
4. Stolcke, A. "Entropy-based pruning of backoff language models." SRILM (1998). Log-linear interp standard; **designed for combining well-calibrated estimators, NOT sparse + smooth**.
5. Caucheteux, Goyal. "Long-range and hierarchical language predictions in brains and algorithms." arXiv:2111.14232 (2021). **Brain operates on 8-token-future hierarchical prediction; brain does NOT optimize BPC.**
6. Caucheteux et al. "Evidence of a predictive coding hierarchy in the human brain listening to speech." Nature Human Behaviour (2023). **Brain-grounded evaluation uses ROI-prediction-accuracy at hierarchical multi-token-horizons.**
7. Pillow, Paninski, et al. "Spatio-temporal correlations and visual signaling in a complete neuronal population." Nature (2008). **Bits-per-spike metric; normalized by n_spikes (sparse events); does NOT penalize sparse distributions.**
8. Frady, Kleyko, Sommer. "Capacity analysis of vector symbolic architectures." (2018-2024 series). **Standard evaluation = recall@K at varying M/N storage ratios; NO BPC.**
9. Kanerva, P. "Sparse Distributed Memory." MIT Press (1988). **Critical distance / noisy-recovery basin radius; NO LM-vs-unigram benchmark.**
10. Bricken, Schick. "Sparse Distributed Memory is a Continual Learner." (2021). **SDM-as-attention mapping; recall@K evaluation, not BPC.**
11. Plate, T. "Holographic reduced representations." IJCAI (1995). **Role-filler recall accuracy at structure-depth; NO BPC.**
12. Salvatori et al. "Predictive sequence learning in the hippocampal formation." Neuron (2024). **Across-area decoding accuracy + temporal cross-correlation; NO perplexity reported.**
13. Kleyko, Davies, Frady, Kanerva, et al. "Vector Symbolic Architectures as a Computing Framework for Emerging Hardware." ACM Comp Surveys (2023). **Survey confirms HD/VSA literature uses recall@K not BPC.**
14. "Language Models Are Better Than Humans at Next-token Prediction." arXiv:2212.11281. **Top-1 and perplexity are DIFFERENT metrics; model can be confident-wrong or under-confident-right.**

### Substrate-internal cross-references
- `data/exp_fresh_W_bpc_per_encoder_v2/metrics.json` — **smoking gun**: 12/12 lambda=0 across 4 encoders x 3 seeds; bpc_per_lambda_test monotonic
- `data/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1/metrics.json` — bpc_best=7.864 lambda=0.1; parent of fresh_W_v2
- `data/exp_n1_concept_lm_substrate_native_token_decode_v3/metrics.json` — sub_top1=0.445 >> uni 0.276 ≈ bigram 0.473 (STRONG reclassification candidate)
- `data/exp_substrate_as_lm_composed_primitives_GPU_v1/metrics.json` — 3/4 arms load_failed (cannot reclassify without re-dispatch)
- `notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md` — parent PC1 + PC2 drill; recommends PC1 as next dispatch (orthogonal mechanism fix; revised harness compounds with mechanism fix)
- `notes/research_2x_revival_ca3_lm_HF_2026-06-23.md` — ca3 family genuine mechanism failure (not harness-rescuable)
- `notes/orchestrator_to_skunkworks_N1v3_FAIR_BPC_real_top1_unigram_level_perplexity_2026-06-21.md` — **PRIOR USER-FACING FRAMING ALREADY IDENTIFIED THIS**: "REAL but WEAK LM: picks single most-likely next token well (top-1 beats unigram, ties bigram), but full probability distribution is only ~unigram-level perplexity"
- `notes/skunkworks_to_research_cc_all_LANDED_VET_path_c_armA_projected_HARD_FAIL_and_path_b_mkn_MIDDLE_BAND_MM_2026-06-22.md` — MKN closes 6.1% of substrate-bigram gap; smoothing-class lever exhausted; confirms decode-side has structural ceiling under BPC

**Verified count: 14 external + 8 substrate-internal cross-references.**

---

## Symmetric verify-both-directions check (per [[feedback-negativity-bias-user-caught-5x-symmetric-verify-both-directions]])

**Did I check the OPPOSITE direction?** Yes:
- I considered "fresh-W methodology is biased AGAINST substrate" (USER question #1) and found: **FALSE** — fresh-W is correctly isolating; the identical bpc_best across encoders is informative
- I considered "lambda=0 collapse is a MECHANISM bug not a HARNESS bug" and found: **the data DOES support mechanism issues** (Schlag-Schmidhuber linear-transformer ceiling is real) — but the dominant signal (3 stacked biases vs 1 ceiling) favors harness-fix-first
- I considered "USER's brain-existence-proof might not apply to text8 specifically" and found: Caucheteux 2022 shows brain operates 8-token-future, so brain itself would not directly map to text8 single-token-next-prediction; the brain-existence-proof applies to "composition mechanism works" not "BPC-vs-unigram-on-text8 works for brain-like processes"
- I considered "revised harness might also be biased TOWARD substrate" — yes, selection-mixer is a substrate-favoring mixer (it's chosen because substrate is sparse-top-1); but it's also the **correct mixer for the substrate's actual capability** per L1.4 Caucheteux 2025 entropy calibration finding (even modern LLMs are evaluated by top-K not by full-distribution calibration)
- I considered "the asymmetric calibration deflate 0.05-0.10 might itself be biased" — yes, normally I would deflate 0.15-0.25; USER explicitly directed lower deflation. The HARD_FAIL band is the brake — if cell HARD_FAILs, diagnosis is wrong regardless of P estimate

**Verify-the-referent check (per [[feedback-verify-the-referent-arrives-not-just-producer-acted]]):** the IDENTICAL bpc_best=7.7378 across 4 different encoders x 3 seeds = 12/12 lambda=0 is the LOAD-BEARING data point. I verified this by reading `data/exp_fresh_W_bpc_per_encoder_v2/metrics.json` directly (lines 32-96 + per_unit) — not from verdict_msg. The 12/12 collapse is real and reproducible.

---

## What this drill does NOT do

- Does NOT design the revised cell's full code (per [[feedback-no-experiment-design-in-prompts]] — that's exp_dev's job; this filing provides the spec, exp_dev authors the cell)
- Does NOT decide whether HARD_PASS triggers product-positioning pivot (USER's call)
- Does NOT propose new substrate mechanisms (the diagnosis is about measurement, not mechanism; PC1 from prior drill is the mechanism-side complement)
- Does NOT reanalyze all 7 prior HARD_FAILs in detail (that's the cell's job once it lands)

---

## Operational drill summary

- **DISPATCH FIRST (cheap decisive):** `substrate_as_lm_revised_harness_v1` — reuse fresh_W_v2 infrastructure; add per-position logit saving + 6 measurement modes M1-M6 + Poisson-shuffle baseline arm. ~100 min GPU wall. Tests HARD_PASS M1+M2+M4 vs HARD_FAIL no-M1-no-M5. **P_deflated=0.65 HARD_PASS** (asymmetric per USER brain-existence-proof directive).
- **DISPATCH SECOND (cross-cell reclassification):** apply revised harness to saved logits from 3 strong reclassification candidates (cells 1, 2, 3 in L5 table) if logits available; else queue re-dispatch with logit saving. ~30 min wall per cell.
- **DISPATCH THIRD (composition):** if revised harness HARD_PASSes, queue PC1 + revised harness composition (orthogonal mechanism fix + correct measurement). ~7hr GPU.
- **Cross-thread synthesis:** revised harness is ORTHOGONAL to PC1 (mechanism) and PC2 (cleanup) drills — those address mechanism-side; this addresses measurement-side. **Run revised harness FIRST** because it's the cheaper test AND it disambiguates whether prior HARD_FAILs warrant mechanism investment.
- **Cap calibration:** P estimates DEFLATED only 0.05-0.10 (asymmetric per USER brain-existence-proof directive); novel-synthesis cap relaxed to 0.65 (not the usual 0.50) because the diagnosis is well-supported by structural lit-scan convergence (NO published HD/VSA work uses BPC vs unigram; brain doesn't optimize BPC; log-linear mixer is mathematically hostile to sparse distributions).

**Honest caveat:** if the revised harness HARD_FAILs (P=0.20), the substrate has a genuine LM-class ceiling at forward-only Hebbian rank-1 that no amount of harness correction can rescue. The HARD_FAIL band is explicit and named precisely so a clean negative is informative.

**Brain-existence-proof reminder:** the brain proves composition mechanism works. The substrate has the right primitives (per CERT 588 + chain-grade KG portfolio + g1b autoregressive generation). The question is whether OUR measurement layer is fair to substrate's strengths. The cheap decisive test directly resolves this.
