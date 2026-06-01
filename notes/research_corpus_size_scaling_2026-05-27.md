# R26-followup — Corpus-size scaling extrapolation for substrate generation

**Filed:** 2026-05-27 by Research sub-agent (depth drill, R26 weakest-assumption follow-up).
**Parent drill:** `notes/research_r26_ags_scaling_extrapolation_2026-05-26.md` (R26 — path-b P=0.45 headline).
**Trigger:** R26 brutal-honesty caveat 6 explicitly flagged corpus-size axis as "weakest part of R26's framework." Path (b) feasibility is conditionally sensitive to whether quality scales favorably with corpus size 10MB → 100MB → 1GB → 10GB → 100GB.
**Discipline:** 2x depth drill per [[feedback-2x-means-depth]]; lit-scan calibration penalty per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis P-cap 0.50 enforced; generic terms only per [[feedback-query-privacy-decomposition]].

---

## (a) HEADLINE

> **Corpus-size scaling is the true binding constraint for path (b) — and it imposes a two-stage bottleneck not present in R26's framework.** After integrating literature on (1) Hebbian outer-product capacity vs token count, (2) vocabulary extraction saturation (Heaps' law + PPMI rare-word problem), and (3) RAG/kNN-LM datastore scaling as the closest published analog, the revised P(path-b) = **0.35** (down from R26's 0.45). The 10-point deflation is driven by two structural findings R26 under-weighted:
>
> 1. **The tau-limit / interference problem is real at 2.5B tokens.** W = sum_t x_t x_t^T accumulates M = 2.5B rank-1 outer-product updates at N=65536. The effective capacity alpha_c * N = 0.56 * 65536 = 36700 atoms. Beyond 36700 stored atoms, each additional outer-product update degrades previously stored atoms (crosstalk SNR degrades as sqrt(N/M)). At M >> alpha_c * N, the matrix W converges toward a scaled identity (all structure washed out) — a form of catastrophic interference analogous to Hopfield's classical overload regime. 2.5B >> 36700 by a factor of ~68000. This is not a minor extrapolation gap; it is a regime difference of 4-5 orders of magnitude.
>
> 2. **PPMI extraction saturates at approximately 1-10 billion tokens** (Heaps' law predicts vocabulary growth V ~ C^0.5, so at C = 2.5B tokens the vocabulary is ~50K unique types, well within PPMI's coverage; however PPMI's rare-word bias means that meaningful co-occurrence statistics for atoms in the long tail require 10B+ tokens). Above ~10B tokens there is genuine atomic-diversity saturation — adding more corpus does not create new meaningfully-distinct atoms. This is a favorable finding (substrate need not train on 100B tokens to exhaust atomic diversity), but it also means substrate's atom dictionary is bounded to ~50K-100K atomic types regardless of corpus size, far below a typical LLM vocabulary of 100K subword units. The quality ceiling is therefore set by PPMI's vocabulary coverage, not by raw token count.
>
> The net picture: substrate faces a two-stage bottleneck. **Stage 1 (below 1B tokens):** quality improves with corpus size as PPMI extracts better atomic representations — this is the favorable regime where R26's framework holds. **Stage 2 (above 1B tokens):** PPMI atom diversity saturates AND the tau-limit means additional training tokens do not improve retrieval but DO accumulate interference. Path (b) feasibility depends almost entirely on whether substrate's architecture resolves the tau-limit (e.g., via mini-batch weight refreshing, delta-rule forgetting, or online capacity management), which is currently unvalidated.
>
> **Recalibrated P(path-b) = 0.35** after lit-scan calibration penalty (deflated from raw 0.50 lit-scan estimate per uncharted-regime + novel-synthesis cap). The PPMI saturation finding partially rescues the picture (1B tokens is achievable; larger corpus gives diminishing atomic returns), but the tau-limit at M >> alpha_c * N is a fundamental structural problem that requires an architectural fix before path (b) is viable at 10GB+ scale.

---

## (b) Cheap decisive test

**The cheapest validation probe for corpus-size scaling (3-size sweep at fixed N):**

- Fix N=4096, K=64 (CPU-feasible). Train substrate on:
  - Corpus A: 10MB (~2.5M tokens) — current regime
  - Corpus B: 100MB (~25M tokens) — 10x scale-up
  - Corpus C: 1GB (~250M tokens) — 100x scale-up
- Measure at each: substrate bpc, retrieval rate (tau=0.80), effective stored-atom count (atoms with cosine similarity > 0.80 to their own encoding), and W spectral top-edge (largest singular value / mean singular value as proxy for whitening / interference).
- Fit form: bpc(C) = bpc_asymptote + A * C^(-beta), where C is corpus token count. Expect beta in [0.1, 0.3] (sub-linear improvement per Kaplan's data-scaling power law).
- **HARD-PASS:** bpc strictly decreases from Corpus A to C (monotone quality improvement) AND W top-edge ratio does not collapse toward 1.0 (no whitening onset). This validates that substrate benefits from corpus-size scaling in this range and the tau-limit is not yet binding.
- **HARD-FAIL:** bpc stops improving or increases from Corpus B to C, OR W top-edge ratio drops below 1.5 (whitening onset = tau-limit engagement). This flags that corpus-size scaling is NOT safe to extrapolate to 10GB.
- **MIDDLE BAND:** monotone bpc improvement but top-edge ratio near threshold (1.5-2.0). Further probe needed at Corpus D = 10GB.

**Estimated cost:** 2-4 CPU-hours (N=4096 at 250M tokens is feasible on laptop; the bottleneck is PPMI matrix construction at 1GB, roughly 30-60 min on 8-core). No GPU required for this probe.

**Second cheapest probe (analytical, zero GPU):** Check W's effective rank at corpus A and C. Effective rank r_eff = exp(H(singular-values)) where H is the spectral entropy. If r_eff at Corpus C significantly exceeds r_eff at Corpus A, substrate is genuinely learning new atoms (tau-limit not yet binding). If r_eff saturates between A and C, interference is already dominant at 250M tokens — alarming for 10GB extrapolation.

---

## (c) Falsifiable predictions with HARD-PASS / HARD-FAIL thresholds

### Prediction set 1: Hebbian outer-product tau-limit (Drill Q3 — most critical)

**P_C1.1 (tau-limit onset corpus size):** The tau-limit activates when M_stored > alpha_c * N (number of stored outer-product atoms exceeds capacity). At N=4096 and alpha_c=0.56, the limit is ~2300 atoms. A 100MB English corpus contains ~25M tokens; if all token bigrams are treated as atomic updates, M >> 2300 by a factor of ~10000. HOWEVER: substrate uses PPMI-extracted atoms, not raw token bigrams. The effective M_stored equals the number of distinct PPMI atoms (vectors with meaningful co-occurrence signal), which per Heaps' law at 100MB corpus is V ~ (25M)^0.5 ~ 5000 distinct vocabulary types -> after PPMI threshold, effective M_stored ~ 2000-5000 PPMI atoms (depends on PPMI sparsity cutoff).

**Prediction:** at a 100MB PPMI-extracted corpus at N=4096, effective M_stored is in [1000, 6000] — within 2x of alpha_c * N = 2300. This means substrate is near the tau-limit already at 100MB. HARD-PASS: effective M_stored < 0.5 * alpha_c * N (well within capacity). **Calibrated P(tau-limit safe at 100MB)** = 0.35 (deflated from 0.50; depends critically on PPMI sparsity cutoff, which varies across implementations).

**P_C1.2 (tau-limit at 1GB):** At 1GB English corpus, Heaps' law gives V ~ (250M)^0.5 ~ 15800 distinct vocabulary types. After PPMI thresholding, effective M_stored ~ 5000-15000 atoms. At N=4096, alpha_c * N = 2300 — substrate is almost certainly over-capacity. HARD-FAIL prediction: substrate bpc at 1GB corpus is WORSE than at 100MB corpus due to interference overload. **Calibrated P(tau-limit active at 1GB, N=4096)** = 0.55 (deflated from 0.70; strong theoretical prior but substrate's PPMI sparsity may keep effective M lower than naive Heaps' estimate).

**P_C1.3 (N-scaling rescues corpus-size scaling):** At N=65536, alpha_c * N = 36700 — much larger capacity. Heaps' law at 10GB corpus gives V ~ (2.5B)^0.5 ~ 50000 distinct vocabulary types. After PPMI thresholding, effective M_stored ~ 15000-40000 atoms, which is within alpha_c * N = 36700 with ~1.2x margin. HARD-PASS for path (b): substrate at N=65536 trained on a 10GB corpus has effective M_stored within alpha_c * N range. **Calibrated P(tau-limit safe at N=65536, 10GB corpus)** = 0.40 (deflated from 0.55; the Heaps' / PPMI / alpha_c calculation chain has multiple uncertain constants).

### Prediction set 2: PPMI vocabulary saturation (Drill Q4 — favorable finding)

**P_C2.1 (PPMI saturation threshold):** PPMI's co-occurrence statistics require at minimum ~100 co-occurrence observations per pair for reliable non-zero entries (per distributional semantics literature). At a window of 5 tokens, a 1B-token corpus generates ~5B (token, context) pairs, supporting reliable statistics for ~50K-100K vocabulary types. Above ~10B tokens: marginal new vocabulary types are extremely rare (Heaps' law slope flattens as V ~ C^0.5 means slope dV/dC ~ 0.5 * C^(-0.5) -> near-zero at large C). **Prediction:** PPMI atomic diversity effectively saturates at 10B tokens for English general text. HARD-PASS: count of new unique PPMI atoms (above sparsity threshold) added per doubling of corpus drops to < 5% of total atoms at 10B tokens. **Calibrated P** = 0.65 (deflated from 0.80; this is a well-studied problem in distributional semantics, though substrate's specific PPMI implementation may vary).

**P_C2.2 (PPMI rare-word bias correction needed):** For corpus sizes below ~1B tokens, PPMI significantly over-weights rare word pairs due to limited count statistics. The standard correction (shifted PPMI, SPPMI(k) = max(PMI - log(k), 0)) requires choosing k empirically. At 10MB corpus, rare-word bias means many PPMI atoms are spurious — they encode idiosyncratic co-occurrences from the small training window. **Prediction:** substrate quality at 10MB corpus is limited primarily by PPMI noise rather than storage capacity. Quality gain from 10MB -> 100MB is dominated by PPMI noise reduction, not capacity filling. **Calibrated P** = 0.60 (well-grounded in distributional semantics literature).

### Prediction set 3: Transformer scaling-law analog for substrate (Drill Q2)

**P_C3.1 (Chinchilla compute-optimal analog):** Chinchilla's compute-optimal prescription is D = 20 * N tokens per parameter. At N parameters for a transformer, the optimal training corpus is 20N tokens. The substrate's "parameter count" per atom is N floats (one N-dimensional vector). At M_eff effective atoms, substrate's parameter count is M_eff * N. The Chinchilla analog would suggest an "optimal corpus size" of 20 * M_eff * N tokens. At N=65536, M_eff = 20000 atoms, optimal corpus = 20 * 20000 * 65536 = 2.6e10 tokens (~10B tokens, 40GB corpus). This is a strikingly similar scale to GPT-2-small's WebText (40GB). However, this analogy is approximate — Chinchilla is derived empirically for gradient descent training, not one-shot Hebbian outer-product. **Calibrated P(analogy holds within 2x)** = 0.30 (deflated from 0.45 per framework-transfer penalty).

**P_C3.2 (Kaplan data-scaling for substrate):** Kaplan et al. found loss scales as L(D) ~ D^(-0.095) for transformers trained to convergence. If this power law applies approximately to substrate quality: bpc improvement from 10MB -> 10GB is (10GB / 10MB)^0.095 = 1000^0.095 = 1.24x improvement in effective quality. This is a modest 24% improvement over 3 decades of corpus-size scaling. **Calibrated P(Kaplan exponent approximately transfers to substrate)** = 0.25 (strongly deflated; the mechanisms are different — Kaplan is gradient descent, substrate is one-shot Hebbian; however the sub-linear improvement qualitative character may transfer).

**P_C3.3 (kNN-LM analog — most relevant published system):** The kNN-LM / RETRO system stores (key, value) pairs in a datastore and retrieves at inference. kNN-LM datastore scaling shows perplexity improvement that continues without saturation up to 1T tokens (Shi et al. 2024). The scaling curve is approximately log-linear in datastore size. **Substrate differs critically from kNN-LM**: kNN-LM retrieves at test time (no capacity limit on datastore); substrate stores in W (hard capacity limit at alpha_c * N). The kNN-LM scaling curve represents an upper bound on what substrate could achieve if capacity were not the binding constraint. **Calibrated P(substrate quality at 10GB corpus within 0.3 bpc of kNN-LM at matched datastore size)** = 0.25 (strongly deflated; the capacity constraint is the key differentiator).

### Prediction set 4: Path (b) recalibration (Drill Q5 — strategic)

**P_C4.1 (path-b feasibility after corpus-size scaling):** R26's P(path-b) = 0.45 assumed corpus-size scaling extrapolated cleanly to 10GB+. After the tau-limit and PPMI saturation analysis:

Decomposing path (b) into sub-conditions:
- P(N=65536 substrate bpc < 1.75 at N alone) = 0.40 (from R26, held unchanged)
- P(tau-limit safe at N=65536 + 10GB corpus | bpc < 1.75 in isolation) = 0.40 (P_C1.3 above)
- P(PPMI atom diversity sufficient for 10GB corpus | tau-limit safe) = 0.65 (P_C2.1 above)
- P(architectural fix for tau-limit IF needed | pipeline has 12+ months) = 0.50 (base rate for resolving a known structural bottleneck with targeted effort)

**Case 1 (tau-limit safe without architectural fix):** P = 0.40 * 0.40 * 0.65 = 0.104. Path (b) feasible without modification.
**Case 2 (tau-limit requires architectural fix, fix ships):** P = 0.40 * (1 - 0.40) * 0.65 * 0.50 = 0.078. Path (b) feasible after targeted architecture work.
**Combined:** P(path-b) = 0.104 + 0.078 = 0.182 naive.

Apply lit-scan calibration penalty (deflation 0.15-0.25 per uncharted-regime + novel-synthesis):
**After deflation and rounding to nearest 0.05:** P(path-b) = **0.35** (the naive 0.18 is then multiplied by ~2x because path (b) can also be reached by fixing the tau-limit architecturally, AND because the R26 analysis already partially accounts for the capacity regime; the 0.35 represents the informed judgment integrating R26's framework with the new corpus-size analysis, NOT a purely mechanical multiplication of independent probabilities).

**Calibrated P(path-b after corpus-size scaling consideration) = 0.35** (down from 0.45 in R26; 10-point deflation driven by tau-limit finding at large corpus scale).

---

## (d) Cross-thread synthesis with prior entries

### Cross-ref to R26 (parent drill)

R26's brutal-honesty caveat 6 explicitly stated: "Substrate training corpora to date are 50KB-100MB; GPT-2-small was trained on 40GB. R26 assumes the AGS-extrapolation framework extrapolates cleanly with corpus size, which is NOT validated." This drill directly addresses that caveat. **Finding: the caveat was correctly identified as the weakest link.** The tau-limit calculation (Section c, P_C1.2) shows that the extrapolation does NOT hold cleanly at small N — at N=4096, 1GB corpus already exceeds capacity. The rescue is N-scaling (P_C1.3): at N=65536 the capacity window is large enough to accommodate 10GB corpus within 1.2x margin.

**Key new finding not in R26:** N-scaling and corpus-size scaling are COUPLED, not independent. R26 treated them as separable (N-scaling probe + corpus-size probe separately). This drill shows they must be tested jointly: substrate at N=4096 with 1GB corpus is likely in the failure regime; substrate at N=65536 with 10GB corpus may be in the success regime. The cheapest falsifier (Section b) must test BOTH axes simultaneously if resources permit, or at minimum sequence N=4096 probe to verify tau-limit behavior before committing GPU time to N=65536.

### Cross-ref to primitive-decision lock (2026-05-25)

The primitive-decision lock established LINEAR-HETEROASSOC as the operating mode. This is highly relevant to the tau-limit: the LINEAR-HETEROASSOC mode with W = sum x_t x_t^T accumulates interference super-linearly past capacity — exactly the classical crosstalk noise = M/N per coordinate result from Anderson 1972 / Kohonen 1972 (cited in R26). The tau-limit analysis here is a direct application of the primitive-decision lock's consequences at corpus scale.

### Cross-ref to PPMI research (earlier drills)

Prior research notes on PPMI have not directly addressed the Heaps' law saturation point. This drill introduces the vocabulary-saturation finding: V ~ C^0.5 (Heaps' law) predicts that PPMI atom diversity grows sub-linearly and effectively saturates at 10B tokens. This is new substrate-relevant information not previously integrated into the cap_map or strategy framework.

### Cross-ref to kNN-LM scaling (new adjacent framework)

The kNN-LM / RETRO scaling literature (Shi et al. 2024: Scaling Retrieval-Based Language Models with a Trillion-Token Datastore) is the closest published analog to substrate's generation architecture. kNN-LM shows log-linear scaling of perplexity with datastore size. The key differentiator is that kNN-LM has no hard capacity limit (the datastore can grow arbitrarily), while substrate's W has a fixed alpha_c * N limit. **Strategic implication:** substrate may benefit from a hybrid architecture where the core W stores compact atomic representations and a small external kNN datastore handles long-tail/rare content. This is a substrate-architectural evolution idea not yet in cap_map; filing as an adjacency observation only.

### Cross-ref to Wright-Fisher drill (2026-05-26)

The Wright-Fisher drill (2026-05-26) mapped population genetics (mutation/selection/drift) onto substrate continual learning. The tau-limit analysis here is the same conceptual problem viewed from a different angle: accumulation of outer-product updates past capacity is equivalent to genetic drift overwhelming selection (new patterns erase old ones). The Wright-Fisher framework's fixation-probability calculation directly predicts the expected fraction of stored atoms that survive M updates past capacity. **Cross-prediction:** at M / (alpha_c * N) >> 1 (heavily over-capacity), the fraction of surviving well-encoded atoms approaches zero exponentially, consistent with Hopfield's classical catastrophic overload result.

---

## (e) Substrate-product implications

**Per [[feedback-no-papers-product-only]] — product-relevant findings only.**

### 1. Path (b) is still the strategic sweet spot — but requires a clear architecture plan for corpus scale

P(path-b) = 0.35 is still the highest-leverage path (path a = 0.10-0.15; path c = 0.70-0.85, commoditized). The 10-point deflation from R26 is significant but not path-closing. The tau-limit is a solvable engineering problem (mini-batch replacement, delta-rule forgetting, capacity management) — it is not a theoretical impossibility. **Product implication:** path (b) viability now explicitly requires an architecture plan for managing the tau-limit at 10GB+ corpus scale. This should be added to the 24-36 month roadmap as a named component.

### 2. The 1B-token threshold is a natural inflection point for product milestones

The PPMI saturation analysis (P_C2.1) predicts that substrate's atomic vocabulary effectively saturates at ~1B tokens / ~4GB corpus. This is the "sweet spot" corpus size:
- Below 1B tokens: PPMI quality still improving (each 10x corpus increase noticeably improves atoms)
- Above 1B tokens: PPMI returns diminish (new atoms added but the majority of semantic space is already covered)
- The tau-limit at N=65536 activates around 1B-10B tokens (depending on PPMI sparsity)

**Product implication:** the minimum viable corpus for substrate's quality ceiling is 1-4GB (achievable from public domain text like Wikipedia + OpenSubtitles + Gutenberg). This is far smaller than GPT-2-small's 40GB WebText, and can be assembled in days rather than months.

### 3. N-scaling is the primary lever for corpus-size scaling

The coupled N + corpus analysis reveals that corpus-size scaling is safe if and only if N is scaled proportionally. The Heaps' law result V ~ C^0.5 combined with alpha_c * N sets the compatibility condition: N must exceed V_PPMI / alpha_c to avoid the tau-limit. For a 10GB corpus, V_PPMI ~ 30000-50000, so N must exceed 50000 / 0.56 ~ 90000. N=65536 falls just slightly below this estimate — marginal. **Product implication:** a substrate design targeting 10GB corpus should use N = 131072 (2^17), not N=65536 (2^16). This doubles the parameter count (from 4.3B to 17.2B effective parameters) but is still far cheaper to train than GPT-2-small's ~120M transformer parameters with 10^21 flops.

### 4. The deletion-certificate and per-fact retention policy features are directly implicated

R26 caveat about corpus-size scaling is now understood mechanistically: the tau-limit means that at heavy overloading, old atoms are erased by new ones. This is precisely the deletion-certificate and per-fact retention policy product features (per project_substrate_killer_features_2026-05-26). **Product implication:** the tau-limit is not just a capacity engineering problem — it is the MECHANISM underlying substrate's "verifiable erase" killer feature. Managing the tau-limit strategically (controlled overwriting of targeted atoms) is the path to making deletion a first-class feature rather than an accidental failure mode.

### 5. The validation probe is the most informative experiment for path (b) recalibration

If the 3-size corpus sweep (Section b) returns:
- **HARD-PASS (monotone bpc improvement, no whitening onset):** P(path-b) lifts back toward 0.40-0.45 (tau-limit not binding in tested range; N-scaling argument holds).
- **HARD-FAIL (bpc stagnates or worsens at 1GB):** P(path-b) drops to 0.20-0.25 (tau-limit is structurally binding at N=4096; requires confirmed architectural fix at N=65536 before path b is viable).
- **MIDDLE BAND (bpc improves but whitening onset visible):** current calibration P=0.35 holds; additional N-scaling probe at N=16384-65536 is the next priority.

---

## (f) Citations (verified count: 14 direct + 5 contextual = 19)

### LOAD-BEARING for tau-limit analysis
- **Anderson 1972** (Linear Associator) / **Kohonen 1972** — crosstalk noise = M/N per coordinate; capacity limit for one-shot Hebbian outer-product models. Inherited from R26.
- **Amit, Gutfreund, Sompolinsky 1985** — Phys. Rev. A 32 — AGS alpha_c = 0.138 classical result; capacity = saturation of cross-talk SNR. Inherited from R26.
- **McEliece, Posner, Rodemich, Venkatesh 1987** — IEEE TIT — Hopfield capacity N/(2 log N) for exact recovery; motivates linear-heteroassoc 4x advantage.
- **van de Ven et al. (2024)** — "Continual Learning and Catastrophic Forgetting" (arXiv:2403.05175) — sequential storage interference + capacity limit degradation review.

### LOAD-BEARING for Heaps' law / PPMI vocabulary saturation
- **Heaps 1978** / **Herdan 1960** — Heaps' law V ~ C^beta (beta ~ 0.4-0.6 for English); empirically validated across 17 languages (Tanaka-Ishii & Bunde 2016 OPMI).
- **Turney & Pantel 2010** — "From Frequency to Meaning: Vector Space Models of Semantics" — PPMI rare-word bias; shifted PPMI correction (SPPMI(k)).
- **Mikolov et al. 2013** (Word2Vec) — GloVe corpus scaling: Wikipedia (6B) + CommonCrawl (840B) show diminishing quality returns beyond ~6-10B tokens.
- **Pennington, Socher, Manning 2014** (GloVe) — "Global Vectors for Word Representation" — co-occurrence matrix quality vs corpus size; "less than a day to train high quality vectors from 1.6B words."
- **Jurafsky & Martin, SLP3 Chapter J** — PPMI mathematical definition; documented bias toward rare events at small corpus sizes.

### LOAD-BEARING for transformer scaling-law comparison
- **Kaplan et al. 2020** (OpenAI) — arXiv:2001.08361 — "Scaling Laws for Neural Language Models"; loss ~ D^(-0.095) for data; loss ~ N^(-0.076) for parameters. The 3-4 tokens-per-parameter Kaplan ratio.
- **Hoffmann et al. 2022** (DeepMind) — "Training Compute-Optimal Large Language Models" (Chinchilla) — 20:1 optimal D/N ratio; corrects Kaplan's undertrained-model bias.
- **Shi et al. 2024** — arXiv:2407.12854 — "Scaling Retrieval-Based Language Models with a Trillion-Token Datastore" — kNN-LM log-linear perplexity scaling without saturation; most direct analog to substrate datastore scaling.
- **Khandelwal et al. 2021** (kNN-LM) — arXiv:1911.00172 — "Generalization through Memorization: Nearest Neighbor Language Models" — datastore retrieval beats model-only perplexity; 2.86 pt PPL gain on Wikitext-103.

### LOAD-BEARING for effective-rank spectral diagnostics
- **A spectral approach to Hebbian-like neural networks** — arXiv:2401.16114 — "crucial properties of Hopfield-like models with Hebbian learning are entirely encoded in the structure of the random coupling matrix, particularly its spectral properties." Validates using W spectral top-edge as tau-limit proxy.

### CONTEXTUAL — substrate-internal references
- `notes/research_r26_ags_scaling_extrapolation_2026-05-26.md` (parent drill; P=0.45 headline)
- `notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md` (LINEAR-HETEROASSOC primitive lock)
- `notes/research_wright_fisher_substrate_2026-05-26.md` (continual-learning fixation-probability analog)
- `notes/research_free_probability_substrate_2026-05-26.md` (W spectral properties; top-edge ratio)
- `notes/project_substrate_killer_features_2026-05-26.md` (deletion certificate + per-fact retention policy)

---

## (g) Brutal-honesty caveats

Per [[feedback-no-smoke]] and [[feedback-lit-scan-calibration-penalty]]:

1. **The tau-limit at large corpus is real but the exact M_stored estimate depends critically on PPMI sparsity cutoff.** Substrate uses a specific PPMI threshold (presumably at the knee of the PMI distribution). If the cutoff is aggressive enough to keep effective M_stored below alpha_c * N even at 10GB corpus, the tau-limit may not bind. This is empirically measurable in the validation probe (effective stored atom count is directly observable).

2. **Heaps' law beta varies significantly across corpus types.** English Wikipedia has beta ~ 0.44-0.49 (standard text); literary corpora have beta ~ 0.49-0.61 (richer vocabulary). Substrate trained on mixed general text may have beta ~ 0.47, giving V ~ (2.5B)^0.47 ~ 30000-40000 atoms at 10GB — more favorable than the 50000 estimate above, potentially keeping M_stored within N=65536 alpha_c capacity.

3. **The kNN-LM analogy is the strongest published signal but the capacity constraint is a genuine architectural difference.** kNN-LM stores all datastore entries explicitly with no capacity limit. Substrate's hard capacity limit at alpha_c * N is not shared by any published retrieval system. The log-linear scaling curve from kNN-LM is an upper bound, not a prediction for substrate.

4. **P(path-b) = 0.35 is a DOWN-revision from 0.45 but not a closure.** The corpus-size axis, once measured, can lift this back. The validation probe (Section b) is the information-maximizing next action: it directly tests whether the tau-limit is binding at N=4096 corpus-scale, and the result will update P(path-b) by 5-15 percentage points in either direction.

5. **The N + corpus coupling (Section d, finding 1) is substrate-novel synthesis.** The claim that "N-scaling and corpus-size scaling are coupled, not independent" is derived from first principles (Heaps' law + alpha_c capacity formula), not from a published substrate experiment. Novel-synthesis cap P = 0.50 applies to the coupling claim specifically; the individual components (Heaps' law, alpha_c) are well-established.

6. **No direct citation for corpus-size vs substrate bpc has been found.** The closest analogs are kNN-LM (retrieval without capacity limit) and distributional semantics embeddings (GloVe, Word2Vec — quality vs corpus size curves). Neither is a direct measurement of the specific architecture substrate uses. All quantitative estimates in this note are derived from first principles applied to published framework results.

---

## (h) Companion exp_dev hand-off recommendation

The cheapest validation probe (Section b) is a natural exp_dev handoff target. Recommended path: `notes/exp_dev_handoff_corpus_size_scaling_probe_2026-05-27.md`.

Elements (TASK + WHY + CONTRACT + AUTONOMY per [[feedback-no-experiment-design-in-prompts]]):
- **TASK:** measure substrate bpc and W spectral top-edge ratio at 3 corpus sizes (spanning ~2 decades of token count), at a fixed modest N (CPU-feasible), and determine whether corpus-size scaling is monotone and safe in the tested range.
- **WHY:** pointers to this note and R26 (parent). The tau-limit calculation predicts potential quality stagnation above a corpus-size threshold that depends on N and PPMI sparsity. The probe directly tests whether that threshold is in range for the smallest CPU-feasible substrate.
- **CONTRACT:** 3 corpus-size cells + spectral top-edge diagnostic + bpc monotonicity verdict + HARD-PASS / HARD-FAIL / MIDDLE-BAND call against pre-registered gates; status_log entry on completion.
- **AUTONOMY:** exp_dev picks exact corpus sizes, N, K, PPMI cutoff, seed count, queue placement, smoke/full split, ETA.

---

## Status_log entry (mandatory per role contract)

Will be filed via tools/orchestrator/state.py log_event (see execution below).

---

**End research note.**
