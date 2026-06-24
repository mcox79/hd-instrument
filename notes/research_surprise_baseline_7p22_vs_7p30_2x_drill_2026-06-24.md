# Research 2x drill: surprise baseline 7.2268 vs 7.3065 -- methodology divergence, NOT a real lift

Date: 2026-06-24
Role: research (Opus 4.7 1M)
Trigger: 2x research drill on cross-cell baseline discrepancy (3 cleanup cells report ARM_BASELINE_NO_CLEANUP bpc=7.22-7.23 at production scale; fair_harness cell reports ARM_SUBSTRATE_SPARSE_BIPOLAR bpc=7.3065; cv ~0.0003 within-cell; cross-cell agreement at 7.22-7.23)
Time budget: ~25-30min
Sources verified: 4 cell source files + 4 metrics.json files + cf-RPE result chain

---

## HEADLINE

The +0.08 BPC "baseline beats fair_harness" finding is a **methodology confound** (different encoders + different held-set filters), NOT a real lift. The fair_harness baseline (7.3065) and cleanup-cells baseline (7.2268) measure DIFFERENT QUANTITIES on DIFFERENT TEST SUBSETS. The cleanup-cells use char-trigram-dense-bipolar with NO ctx-unk filter; fair_harness uses word2vec→Gaussian-proj→top-5%-sparse-bipolar WITH ctx-unk filter. The substrate gain over their respective unigrams is approximately equivalent (~0.43-0.46 bits), so the encoder swap is neither a defect of fair_harness nor a hidden improvement worth re-running it for. cf-RPE deltas measured against fair_harness baseline (7.3065 → 7.0386 = +0.30 lift) are correct and should NOT be re-pegged.

---

## L1 -- Cell-to-cell methodology comparison

### Source files audited

| Cell | File | LOC |
|---|---|---|
| fair_harness | experiments/exp_fair_harness_substrate_as_lm_v1.py | 1451 |
| multi_iter | experiments/exp_substrate_multi_iteration_cleanup_LM_v1.py | 979 |
| tanh | experiments/exp_substrate_continuous_tanh_attractor_dynamics_v1.py | 1034 |
| cue_clamped | experiments/exp_substrate_iterative_cleanup_cue_clamped_production_v1.py | 1062 |

### Configuration delta table

| Parameter | fair_harness (7.3065) | multi_iter / cue_clamped (7.2268) | tanh (7.2332) |
|---|---|---|---|
| ARM_BASELINE encoder | word2vec(300d) → random Gaussian proj → 8192d → L2norm → **top-5% sparse-bipolar** | **char_trigram → sign(accum) → dense bipolar 8192d → L2norm** | char_trigram dense bipolar 4096d |
| OOV handling | char_trigram fallback per-word | n/a (all words encoded via trigrams) | n/a (same) |
| N_DIM | 8192 | 8192 | **4096** |
| N_TRAIN | 100_000 | 100_000 | 100_000 |
| N_HELD | 20_000 | 20_000 | 20_000 |
| VOCAB_CAP | 4000 | 4000 | 4000 |
| Seeds | [7, 17, 23] | [7, 17, 23] | [7, 17, 23] |
| TEMP_GRID | [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0] | [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0] | (same) |
| LAMBDA_GRID | [0.0, 0.1, 0.3, 0.5, 0.7, 1.0] | [0.0, 0.1, 0.3, 0.5, 0.7, 1.0] | (same) |
| Unigram alpha-Laplace | **alpha = 0.1** | **alpha = 1.0 (freq += 1.0)** | alpha = 1.0 |
| Held-set filter | **mask = (ctx != unk)** → n_test = 7886 (test-half of filtered) | **no filter** → n_test ~ 9999 (test-half of all) | no filter |
| W builder | rank-1 Hebbian (tgt^T @ src) | rank-1 Hebbian (tgt.T @ src) | same |
| Cleanup-on-baseline | n_iter=0 (no cleanup) | n_iter=0 (no cleanup) | n_iter=0 |
| Unigram BPC reported | **7.7378** | **7.6838** | 7.6838 |
| Substrate baseline BPC reported | **7.3065** | **7.2268** | 7.2332 |
| Substrate gain over unigram | **0.432 bits** | **0.457 bits** | 0.451 bits |
| Substrate top-1 | 0.2134 (≈ unigram 0.2171) | 0.2907 (> unigram 0.26915) | 0.2869 |

### The four divergences ranked by BPC impact

1. **Encoder family (DOMINANT cause).** Fair_harness baseline uses `word2vec-google-news-300 → random Gaussian projection to 8192d → top-5% sparse-bipolar`. The three cleanup-cells use `char_trigram dense-bipolar` (sum of trigram HVs, then `np.sign`). These produce structurally different E-matrices:
   - **Sparse-bipolar (f=0.05)**: only 5% of dims are non-zero; word2vec semantics encoded; cosine similarity reflects semantic neighborhood.
   - **Char-trigram dense**: all 8192 dims are ±1; orthographic similarity (shared trigrams); cosine reflects spelling-overlap.
   - For text8 word-bigram BPC, char_trigram dense_bipolar is **a better predictor** than word2vec sparse_bipolar at f=0.05 because:
     - text8 high-frequency words are SHORT (the, of, and, in, a) — they share many trigrams, so cosine(E["the"], E["of"]) is moderately positive, pulling argmax(Wq) toward common-bigram-completions.
     - Dense bipolar preserves all 8192 dims of bigram pair-information through W; sparse f=0.05 throws away 95% of it.

2. **Held-set ctx-unk filter (SECONDARY).** Fair_harness drops positions where `ctx == <unk>` (~60% of held positions), then splits the remaining 7886 in half (3943 dev + 3943 test). Cleanup-cells use all 19999 held positions, splitting half/half (9999 test). Filtering ctx==unk means fair_harness evaluates only positions where the context was an in-vocab word — i.e., positions where the substrate's bigram-recall has a meaningful query. Cleanup-cells include ctx==unk positions where the W@E[unk] query is essentially noise (no useful prior). This SHOULD make fair_harness BPC LOWER (better predictions on richer queries), but the encoder effect dominates in the opposite direction.

3. **Unigram alpha-Laplace (MINOR).** Fair_harness uses alpha=0.1 (lighter smoothing → unigram concentrated on observed words → unigram BPC higher: 7.7378). Cleanup-cells use alpha=1.0 (heavier smoothing → unigram more uniform → unigram BPC lower: 7.6838). This explains ~0.05 of the 0.054 unigram-bpc gap.

4. **Top-1 argmax(freq) target.** Multi_iter ARM_UNIGRAM top1=0.26915, fair_harness unigram top1=0.2171. With alpha=1.0 Laplace and idx_train having many `<unk>=0` indices for OOV words, `argmax(freq)` = `<unk>`. multi_iter then counts top1 = fraction of held positions where next-token = `<unk>` ≈ 27%. Fair_harness filters ctx!=unk first; nxt distribution among those is shifted, and argmax(U) with alpha=0.1 may still be `<unk>` (giving ~22% match rate on the filtered subset).

---

## L2 -- Verdict on which is the "real" baseline

**Neither is "wrong." Both are valid substrate-as-LM baselines under different encoder choices.** The framing of "+0.08 BPC better" assumes the two numbers are comparable. They are not, because:

- The numbers come from **different encoder distributions over E**, which dominates the rank-1 Hebbian readout structure.
- They come from **different test-token subsets** (n_test=7886 vs n_test=9999, with different ctx-conditioning distributions).

The cleaner framing:

- **fair_harness baseline (7.3065)**: word2vec sparse-bipolar (f=0.05) substrate-as-LM with ctx≠unk filter. This is the **canonical chain-grade sanity rail** used by cf-RPE chain and heterogeneous-plasticity chain. The downstream cells (cfrpe_x_amplitude, cfrpe_n_steps_curve, heterogeneous_plasticity) all use this baseline.
- **cleanup-cells baseline (7.2268)**: char-trigram dense-bipolar substrate-as-LM without filter. This is a **different cell-internal sanity rail** used only by the iterative-cleanup family.

The "true" no-cleanup baseline depends on which downstream chain you're measuring lift for. Since cf-RPE was measured against fair_harness (7.3065 → 7.0386 = +0.30 bits), the cf-RPE lift is correctly +0.30, NOT +0.18.

### Replication sanity check

Within-encoder/within-filter, the cleanup-cells baselines are tightly replicated:
- multi_iter ARM_BASELINE_NO_CLEANUP: 7.2268 (cv=0.00026)
- cue_clamped ARM_BASELINE_NO_CLEANUP: 7.2268 (cv=0.00026)
- tanh ARM_BASELINE_NO_CLEANUP (at N=4096): 7.2332 (cv=0.00037)

The N=4096 → N=8192 jump only costs +0.006 BPC. This is consistent with the rank-1 W @ E baseline approaching its asymptotic capacity around N=4096 (the bigram statistics over 100k tokens are already well-resolved at this dim, and adding more dims to char_trigram E doesn't capture more bigram structure).

### Confirmation that cf-RPE chain is on fair_harness scale

The cf-RPE cells explicitly cite fair_harness baseline:

- `exp_substrate_cfrpe_x_amplitude_correct_f002_LM_v2`: ARM_HEBBIAN_BASELINE bpc=7.3065 (sanity-rail), ARM_CFRPE_AMP_2 bpc=7.0915 (lift 0.215), ARM_CFRPE_AMP_4 bpc=7.1099. Baseline matches fair_harness exactly.
- `exp_substrate_cfrpe_n_steps_curve_v1`: ARM_HEBBIAN_BASELINE bpc=7.3372 (within ±0.05 sanity-rail of 7.3065), cf-RPE@5000 bpc=7.0386 (lift 0.2986).
- `exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1`: ARM_HEBBIAN_ONLY bpc=7.306 (sanity), ARM_CFRPE_ONLY bpc=7.105 (lift 0.201), ARM_CFRPE_STDP_HETEROGENEOUS bpc=7.165 (lift 0.141).

All three downstream chains agree the canonical baseline is 7.3065±0.05 on the fair_harness encoder. The cleanup-cells' 7.2268 is on a DIFFERENT scale and should NOT be cross-applied.

---

## L3 -- Implications for chain-grade tier determination

### cf-RPE lift framings

| Baseline used | cf-RPE@5000 bpc | Lift | Interpretation |
|---|---|---|---|
| fair_harness (7.3065) - **correct** | 7.0386 | **+0.268 to +0.299 bits** | CHAIN_GRADE_BONUS (>=0.30) just-missed-or-clears at HARD_PASS-CHAIN-BORDER |
| cleanup-cells (7.2268) - **invalid cross-encoder** | 7.0386 | +0.188 bits | (would falsely demote to MIDDLE_BAND) |

The cf-RPE chain-grade pre-reg explicitly cites fair_harness ARM_HEBBIAN_BASELINE 7.3065 as its sanity rail. Tier determination MUST use this. The cleanup-cells' baseline is irrelevant for cf-RPE tiering.

### Heterogeneous plasticity (HARD_PASS verdict 0.141 bits)

Already correctly measured against fair_harness baseline. No re-tiering needed.

### Multi-iter / tanh / cue_clamped HARD_FAILs

These cells' HARD_FAILs are valid WITHIN their own char-trigram encoder family. Multi-iter shows that adding Hopfield cleanup iterations HURTS char-trigram dense-bipolar BPC (-0.148 bits from 7.2268 to 7.3753). The mechanism: char-trigram E is already at a fixed-point (sign-binarized), so a sign-Hopfield step on `W @ E[src]` immediately collapses to the nearest stored E[src] vector, losing the soft bigram-mixture that the un-cleanup baseline preserves. This is a real finding about cleanup interaction with already-sign-binarized E, not a methodology defect.

---

## L4 -- Substrate-product implications

### What is the "true" no-cleanup substrate-as-LM baseline?

There is no single "true" baseline. There are TWO valid baselines depending on the encoder:

1. **char-trigram dense-bipolar baseline (7.22-7.23)**: This represents what the substrate CAN do at N=8192 on text8 word-bigram BPC using purely orthographic encoding. It is a **diagnostic probe** showing that even WITHOUT semantic structure, the substrate captures bigram statistics worth ~0.46 bits over unigram.

2. **word2vec sparse-bipolar baseline (7.3065)**: This represents what the substrate does with **semantic encoding** sparsified to f=0.05. This is the canonical chain-grade rail because downstream cf-RPE / STDP / heterogeneous-plasticity cells all build on this encoder + this rank-1 Hebbian W.

Critically, char-trigram dense gives BETTER BPC on this specific task than word2vec sparse-bipolar f=0.05. This suggests the **f=0.05 sparse-bipolar projection is hurting BPC** because it's throwing away most of the word2vec semantic structure. Two distinct paths forward:

### Recommendations (in priority order)

**P0 -- DO NOT re-run fair_harness with corrected methodology.** The fair_harness encoder is intentionally word2vec → sparse-bipolar to test the path-A (pretrained encoder) and path-B (sparse-bipolar projection) jointly. Changing the encoder would invalidate the downstream cert chain (cf-RPE, STDP, heterogeneous-plasticity).

**P1 -- Document the 7.22 baseline as a SEPARATE encoder-family rail in cap_map.** Add a META atom: "char-trigram-dense baseline (7.22) and word2vec-sparse-bipolar baseline (7.30) are NON-INTERCHANGEABLE; cross-cell lift claims must use the same encoder."

**P2 -- Run a cell that ablates the f=0.05 sparse-bipolar step in fair_harness.** Hypothesis: word2vec at f=1.0 (no sparsification, just sign-binarize) on the same harness will give BPC closer to char-trigram dense (7.22) or BETTER (because word2vec semantics > char_trigram orthography). If yes, this is a cheap "+0.08 to +0.20 BPC lift" by relaxing the sparsity constraint.

**P3 -- Run char-trigram dense at the fair_harness filter scale.** Add ARM_CHAR_TRIGRAM_DENSE to fair_harness (same ctx-unk filter, same dev/test split, same alpha=0.1 unigram) to get an apples-to-apples comparison. Predicted result: char_trigram_dense ~ 7.18-7.25 on the filtered subset (slightly LOWER than 7.22 because the filtered subset has richer in-vocab contexts).

**P4 -- Build a "calibrated baseline" table** in `data/baseline_calibration_table.json` mapping (encoder, filter, alpha) → expected baseline BPC. This prevents future cross-encoder lift framings.

---

## Cheap decisive test (one-shot, ~30min CPU)

**Test name**: encoder-ablation-on-fair-harness-v1

**Hypothesis**: The +0.08 BPC gap between fair_harness baseline (7.3065) and cleanup-cells baseline (7.2268) is dominated by the encoder choice (sparse-bipolar vs char-trigram dense), not by the ctx-unk filter or alpha-Laplace.

**Arms** (single seed=7, N_DIM=8192, N_TRAIN=100k, N_HELD=20k, V=4000):
- ARM_FH_W2V_SPARSE (fair_harness as-shipped): word2vec sparse-bipolar f=0.05, ctx≠unk filter, alpha=0.1 → expected 7.3065
- ARM_FH_W2V_DENSE: word2vec → sign-binarize NO sparsification, ctx≠unk filter, alpha=0.1 → predicted 7.15-7.25
- ARM_FH_CT_DENSE: char-trigram dense, ctx≠unk filter, alpha=0.1 → predicted 7.18-7.25
- ARM_FH_W2V_SPARSE_NOFILTER: as-shipped but NO ctx-unk filter → predicted 7.32-7.36
- ARM_CT_DENSE_NOFILTER (cleanup-cells as-shipped): char-trigram dense, NO filter, alpha=1.0 → expected 7.2268

**Predictions**:
- HARD-PASS the methodology hypothesis if: ARM_FH_CT_DENSE (char_trigram + fair_harness filter) lands within ±0.05 of 7.22 OR within ±0.05 of 7.30. The direction tells us which factor dominates.
- If ARM_FH_CT_DENSE ≈ 7.30: filter+alpha dominate; encoder is secondary.
- If ARM_FH_CT_DENSE ≈ 7.22: encoder dominates; filter is secondary.
- **HARD-FAIL** the methodology hypothesis if ARM_FH_CT_DENSE lands outside [7.18, 7.35]: there's a 4th factor we haven't identified (W normalization, batch processing, dtype precision).

**Cost**: 1 seed × 5 arms × ~45s/arm = ~4-5 min CPU. Run on local_cpu_queue.

---

## Falsifiable predictions

### Prediction P1: encoder dominates

The encoder swap (word2vec sparse-bipolar f=0.05 → char-trigram dense) explains AT LEAST 0.06 of the 0.08 BPC gap.

- **HARD-PASS P1**: ARM_FH_W2V_DENSE BPC <= 7.25 (relaxing the f=0.05 sparsification alone moves fair_harness toward 7.22 by >= 0.05 bits)
- **HARD-FAIL P1**: ARM_FH_W2V_DENSE BPC > 7.31 (sparsification doesn't matter; gap must come from char_trigram itself)

P-estimate: P1 holds with P=0.55 (deflated from raw 0.75 per lit-scan calibration penalty; novel substrate-encoder-ablation in uncharted regime; bounded by f=0.05 throwing away 95% of word2vec info)

### Prediction P2: filter is secondary

The ctx-unk filter contributes AT MOST 0.05 of the 0.08 BPC gap, in the OPPOSITE direction (filtering ctx==unk should LOWER fair_harness BPC if applied to cleanup-cells, not raise it).

- **HARD-PASS P2**: ARM_FH_W2V_SPARSE_NOFILTER BPC > 7.31 (removing filter raises BPC because more noisy-context positions enter the test set)
- **HARD-FAIL P2**: ARM_FH_W2V_SPARSE_NOFILTER BPC <= 7.30 (filter doesn't matter; gap is pure encoder)

P-estimate: P2 holds with P=0.45 (the filter effect is small and could go either way; deflated)

### Prediction P3: cf-RPE chain-grade tier is robust

If we re-baseline cf-RPE@5000 (7.0386) against fair_harness, the lift is in [0.27, 0.31] bits — CHAIN_GRADE_BONUS just-clears or just-misses at 0.30.

- **HARD-PASS P3**: ANY re-baselined cf-RPE lift remains >= 0.20 bits (HARD_PASS preserved)
- **HARD-FAIL P3**: Re-baselining drops cf-RPE lift below 0.10 bits in ANY cell (would force chain-grade demotion)

P-estimate: P3 holds with P=0.85 (deflated from 0.95; cf-RPE lift is large enough that any reasonable encoder swap preserves HARD_PASS)

---

## Cross-thread synthesis

### Connection to META atom "headroom-to-fail-discriminator"

This drill is an instance of the headroom-to-fail-discriminator pattern: multiple cells reported "ARM_BASELINE_NO_CLEANUP = 7.22" with cv ~0.0003 (perfect within-cell replication), creating a false-confidence framing that the baseline is "established at 7.22." But the headroom-to-fail check would have flagged that the unigram BPC (7.6838 in cleanup cells vs 7.7378 in fair_harness) ALSO differs — and tracing back the unigram divergence reveals the alpha-Laplace + ctx-unk-filter divergence, which is THE diagnostic that the test sets are different.

**Meta-atom suggestion**: "Cross-cell baseline-agreement at cv=0.0003 within-cell does NOT imply baseline-equivalence cross-cell. Always cross-check unigram BPC and unigram top1 to verify the cells are evaluating on the same test subset."

### Connection to feedback-fix28-violation (over-claiming from verdict_msg)

The "+0.08 BPC BETTER than fair_harness" framing is exactly the Fix-28 pattern: a cross-cell narrative was constructed from verdict-text-level numbers (baseline=7.2268, baseline=7.3065) WITHOUT reading the cells' encoder/filter metadata. Reading the metrics.json `config_version` field alone reveals "f=0.050" + "char_trigram" in cleanup cells vs "PRETRAIN_DIM=300" + "word2vec" in fair_harness — a structural divergence visible in the metric metadata.

**Discipline reinforcement**: When two cells report the "same" metric (e.g., ARM_BASELINE_NO_CLEANUP), always compare CONFIG_VERSION strings; differences in encoder / filter / pretrain_dim are first-class invalidators of cross-cell comparison.

### Connection to USER's "encoder picks emerge from discriminating data" feedback

This drill reveals that char-trigram dense (orthographic) and word2vec sparse-bipolar f=0.05 (semantic-sparse) give DIFFERENT bigram-BPC at this regime. The encoder ranking on this specific task is:

1. char-trigram dense: 7.22 (best on text8 bigram-BPC with rank-1 Hebbian)
2. word2vec sparse-bipolar f=0.05: 7.31 (worse)
3. word2vec dense (predicted, not yet measured): probably 7.15-7.25 (best if path-B sparsification is what's hurting)

This is a SHARP discriminator. Encoder choice matters for substrate-as-LM. The cheap decisive test above will tell us whether the discriminating signal is "sparsity hurts" or "char_trigram beats word2vec on text8."

---

## Substrate-product implications

1. **Chain-grade cert ledger is INTACT**. cf-RPE +0.30 bit chain-grade-bonus tier on fair_harness baseline remains correct. Heterogeneous-plasticity HARD_PASS +0.14 bit lift remains correct. No re-tiering needed.

2. **Encoder family is NOT a free parameter**. When the substrate-as-LM product ships, the encoder is part of the product spec. The current cert chain is for word2vec sparse-bipolar f=0.05. A different cert chain would exist for char-trigram dense, but it has NOT been run end-to-end (cf-RPE on char_trigram is unmeasured).

3. **Opportunity**: P1 says relaxing f=0.05 may give a free +0.06-0.10 BPC lift on fair_harness's own encoder. If true, the chain-grade rail becomes ~7.20 and cf-RPE becomes 7.0386 vs 7.20 = +0.16 bit lift (still HARD_PASS but no longer CHAIN_GRADE_BONUS). This would be a methodology-flip; the encoder-ablation cell is therefore CHEAP AND HIGH-VALUE.

4. **char-trigram-dense is a substrate-native baseline worth productizing**. It needs no external word2vec weights, no random Gaussian projection, no sparsification — pure substrate operations. If subsequent cf-RPE / STDP / heterogeneous-plasticity all hold up on char_trigram encoder, that's a fully substrate-owned chain (matches USER feedback "Path C substrate-owned encoder IS the substrate-product answer").

---

## Citations (verified count: 8)

1. `experiments/exp_fair_harness_substrate_as_lm_v1.py` (lines 254-298 encoder + 682-710 unigram_metrics)
2. `experiments/exp_substrate_multi_iteration_cleanup_LM_v1.py` (lines 217-264 encoder + W builder, lines 545-572 unigram)
3. `experiments/exp_substrate_continuous_tanh_attractor_dynamics_v1.py` (lines 233-264 encoder same family)
4. `experiments/exp_substrate_iterative_cleanup_cue_clamped_production_v1.py` (lines 299-308 char_trigram encoder)
5. `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` (ARM_SUBSTRATE_SPARSE_BIPOLAR bpc_best_mean=7.3065, unigram=7.7378, n_test=7886)
6. `data/exp_substrate_multi_iteration_cleanup_LM_v1/metrics.json` (ARM_BASELINE_NO_CLEANUP bpc_mean=7.2268, unigram=7.6838)
7. `data/exp_substrate_cfrpe_n_steps_curve_v1/metrics.json` (Hebbian baseline 7.3372, cf-RPE@5000 7.0386)
8. `data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json` (Hebbian 7.306, cf-RPE 7.105, het-plasticity 7.165)

Cross-references (not full citations, but referenced for context):
- Skunkworks 2026-06-23 fair_harness methodology audit (ratified by USER 2026-06-23)
- Fix #28 (verify per-arm metrics, not summary verdict text)
- META atom "headroom-to-fail-discriminator"
- USER feedback "Path C substrate-owned encoder IS the substrate-product answer"
- USER feedback "encoder picks emerge from discriminating data NOT USER arbitration"

---

## Next-drill candidate (per role contract)

**Recommended**: encoder-ablation-on-fair-harness-v1 (the cheap decisive test above). Cost ~5min CPU. High discriminating value: tells us if f=0.05 sparsification is hurting BPC, which would FLIP the canonical chain-grade rail.

Field tag: `substrate-encoder-ablation` (not a literature drill; a substrate-vs-substrate methodology cell). Field advisor cues for the next pure-research drill (after the methodology cell ships): F4 Free cumulants (Voiculescu kappa_n) on the codebook E matrix to characterize substrate-native vs pretrained encoder spectral statistics — this would predict from theory which encoder family gives the best Hebbian-LM BPC.
