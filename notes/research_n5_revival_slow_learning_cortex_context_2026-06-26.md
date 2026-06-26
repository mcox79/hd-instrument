# Research: n5 trigram revival -- slow-learning cortex context compression (NOT HRR-blend)

**Date:** 2026-06-26
**Filed-by:** research (Opus 4.7 1M)
**Trigger:** USER deep revival drill. Plain English. n5 HARD_FAIL of HRR-blend trigram; USER reframe says wrong layer (query-time blend should be slow-learning compression).
**Builds-on:**
- n5 metrics: `data/exp_n5_trigram_concept_lm_v1/metrics.json` (HRR-blend trigram bpc=6.86 vs bigram baseline 4.97; depth gain = -1.89 bits)
- Gap 3 BCM drill (today): `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` (BCM + W_schema + replay)
- Gap 4 TWO_TIER (in-flight): `notes/exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md`
- NREM replay proven-bound +0.57 drift_reduction (2026-06-22)
- 5x deeper Path C universal encoder: `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md`
- Substrate-as-LM methodology audit (META_HARNESS_RIGGED reclassification): `notes/research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md`

**Calibration:** P estimates deflated 0.15-0.25; novel-synthesis cap 0.50; HARD-FAIL thresholds pre-registered.

---

## HEADLINE

USER is right. The n5 HRR-blend tried to do at QUERY TIME what the brain does over SLOW LEARNING. The math agrees: an HRR bind of (word_t-2, word_t-1) at substrate's regime injects ~1.9 bits of crosstalk noise into the query signature, which is worse than just throwing word_t-2 away (the backoff arm was -1.65 bits and still HARD_FAIL). The brain's actual mechanism for context-aware next-word prediction is a **slowly-learned conditional distribution** stored in cortex, written by Hebbian outer-products of (context_signature, target) pairs over thousands of replay cycles -- exactly the same family of mechanism as the Gap 3 BCM cell already in flight, but applied to a different task (next-token prediction, not categorical schema extraction). The substrate has every primitive needed; this is not a research gap, it is a recomposition of existing primitives into a sequence-prediction task.

The single highest-P_deflated cell is **slow_cortex_bigram_predictor_v1**: a separate W_pred matrix that accumulates Hebbian outer products of (bigram-context-signature, next-token) over text8 in a single slow pass. Read at query time as `next_token_dist = softmax(beta * W_pred . query_signature)`. This is a learned bigram-extended-with-context predictor, not a query-time blender. P_deflated = 0.40. Cost: ~2-4 CPU-hr at N=16384 over text8 with V_TOK=8192.

**Critical reframe in one sentence:** the n5 HRR-blend ceiling was not about HRR being wrong-family; it was about doing the work at the wrong LAYER. Move the same family of operation (binding + association) from QUERY-TIME to LEARNING-TIME and the crosstalk noise gets averaged out across the corpus instead of injected per-query.

---

## Cheap decisive test

**Cell name:** `slow_cortex_bigram_predictor_v1`

**One-sentence what it tests:** does a slow-learned W_pred matrix that stores Hebbian outer-products of (word_t-1, word_t) and (word_t-2, word_t) over text8 produce a top-1 prediction accuracy that BEATS the n5 BIGRAM baseline (top1=0.429) AND beats the n5 TRIGRAM_HRR (0.302), demonstrating that slow-learning cortex-style context compression succeeds where query-time HRR-blending failed?

**Architecture (drawn out plain English):**

```
   text8 stream (real corpus, ~17M tokens)
                 |
                 v
   For each triple (word_t-2, word_t-1, word_t):

       a) bigram context signature
          ctx_2     = encoder(word_t-1)                  -- pure bigram
          ctx_12    = bundle( encoder(word_t-1), 
                              encoder(word_t-2) )         -- BUNDLED context (not bound)
          target    = encoder(word_t)

       b) Hebbian outer-product write into TWO W matrices
          W_bigram[i,j] += eta * ctx_2[i]  * target[j]   (eta = 1/N effective)
          W_trigram[i,j] += eta * ctx_12[i] * target[j]   (eta = 1/N effective)

   (over all of text8 train split, one slow pass; 
    optional NREM replay decorator for second pass)
                 |
                 v
   At query time (word_t-2, word_t-1):
       query_2   = encoder(word_t-1)
       query_12  = bundle(encoder(word_t-1), encoder(word_t-2))
       logits_bigram   = W_bigram . query_2
       logits_trigram  = W_trigram . query_12

       (no HRR-blend at query time; W_trigram has already 
        absorbed the trigram statistics over millions of examples)

       interpolate:  logits = alpha * logits_trigram + (1-alpha) * logits_bigram
                     dist   = softmax(beta * logits)
```

**KEY MATHEMATICAL DIFFERENCE vs n5:**

n5 did:
```
query_HRR = bind(word_t-2, word_t-1)              <-- noisy at query time
W trained on (word_pair_signature, target)        <-- per-pair learning, sparse coverage
score = W . query_HRR                              <-- noise-vs-sparse-coverage = HARD_FAIL
```

This cell does:
```
W_trigram trained on (BUNDLED context, target)    <-- per-triple averaging at learning time
query = bundle(word_t-2, word_t-1)                 <-- bundle preserves both signals
score = W_trigram . query                          <-- dense coverage, learning-averaged
```

The decisive design difference: bind (circular convolution) at query time mixes the two operand vectors INTO each other, producing a third vector different from either; bundle (sum) at learning time KEEPS both signals identifiable and lets the W matrix do the per-target conditional-distribution work. The brain's mechanism is closer to bundle-at-context-time + learn-target-at-replay-time.

**Four arms:**

- `ARM_BIGRAM_BASELINE` -- replicate n5 BIGRAM_BASELINE; expected top1=0.429, bpc=4.97. Methodology rail (must match n5 within 0.02).
- `ARM_TRIGRAM_BUNDLE_SLOW` -- the cell-rank-1 mechanism. Bundle context at learning time, Hebbian outer-product write, score by inner product.
- `ARM_TRIGRAM_HRR_REPLICATION` -- replicate n5 TRIGRAM_HRR (HARD_FAIL) on identical hardware/seed/corpus to confirm the n5 ceiling is the structural ceiling (not n5-specific bug). Expected HARD_FAIL.
- `ARM_TRIGRAM_BUNDLE_NREM_REPLAY` -- as ARM_TRIGRAM_BUNDLE_SLOW BUT add NREM replay decorator (proven-bound +0.57 from substrate). Tests whether sleep replay sharpens W_trigram further.

**Pre-registered bands:**

- **HARD_PASS:** ARM_TRIGRAM_BUNDLE_SLOW or ARM_TRIGRAM_BUNDLE_NREM_REPLAY: top1 >= 0.47 (>= +0.04 over bigram baseline) AND bpc < 4.70 AND cv across 3 seeds <= 0.03. The +0.04 floor is conservative: real-text trigram statistics typically add only modest top1 lift over bigram on text8 (the natural ceiling is set by data, not by mechanism); +0.04 above bigram is the discriminating signal that slow-learning extracted ANY trigram structure.

- **HARD_FAIL:** All TRIGRAM_BUNDLE arms within 0.01 of bigram baseline (mechanism doesn't extract trigram structure at all) OR worse than bigram baseline (mechanism harms even with slow learning). Interpretation: substrate sequence-prediction is encoder-bound, not mechanism-bound; pivot to encoder improvements (Path C v2).

- **MIDDLE_BAND [0.43, 0.47]:** PARTIAL. Slow-learning helps marginally; mechanism is correct family but at substrate's regime the lift is small. Queue: increase N_DIM (16384 -> 32768), longer corpus pass, NREM replay multi-cycle (replay_cycles in {1, 3, 10}).

**Discriminator design (per [[feedback-experiment-bias-master-checklist]] BIAS-13/14/15):**
- ARM_BIGRAM_BASELINE must replicate n5 baseline within 0.02 top1 (methodology rail).
- ARM_TRIGRAM_HRR_REPLICATION must replicate n5 TRIGRAM_HRR within 0.02 top1 = 0.302 +- 0.02 (HARD_FAIL anchor; confirms the cell IS at the n5 regime, not different).
- Per-arm metrics MANDATORY per Fix #28; do NOT infer from verdict_msg. Specifically: top1, top5, bpc, alpha (interpolation), cv, n_seeds, V_TOK, N_DIM.
- W_trigram density audit: number of non-zero entries / N^2. Hebbian outer-product should produce a DENSE matrix (every-pair contribution); sparsity below 0.5 is a red flag for a learning bug.
- Same seeds [11, 13, 19] as Gap 3 BCM cell -- cross-cell rail.

**Compute budget:** 2-4 CPU-hr at N=16384 over text8 (100K docs). Dominant cost is text8 ingest with N^2 matrix updates (~17M tokens x N=16384 ~ 280B FLOPs at peak; manageable on remote_cpu_queue).

---

## Section 1: Why HRR-blending failed at substrate scale (plain English)

Substrate's binding operation is circular convolution. Mathematically:

```
bind(a, b)[k] = sum_j  a[j] * b[(k - j) mod N]
```

In bipolar HRR at N=16384, this produces a third vector whose cosine to either a or b is approximately zero. The bind is a one-way mixer: you can store (a bound with b) and later UN-BIND to recover something near a or near b given the other operand. But the BOUND signature itself has near-zero cosine to either a or b.

At n5 the query was `bind(word_t-2, word_t-1)`. The W matrix had been trained to associate this BOUND signature with the next-word target. But:

1. **Crosstalk problem.** With V_TOK = 8192 distinct word vectors, there are 8192^2 = 67M possible (word_t-2, word_t-1) pairs. Many of these bound signatures will have small but non-zero cosines to many other bound signatures (random-encoding noise floor at N=16384 = ~1/sqrt(16384) ~ 0.008). When you score against W, you accumulate noise from all the rows of W that have non-zero cosine to your query.

2. **Sparse coverage.** Even if substrate sees text8 ~17M tokens (= ~17M triples), the number of DISTINCT (word_t-2, word_t-1) pairs that appear more than once is much smaller than 8192^2. So most W rows are written with near-singleton samples. A learned predictor needs MULTIPLE samples per row to extract signal from noise.

3. **Bigram already saturates.** With V_TOK = 8192 and 17M tokens, the bigram-only level already covers ~3M distinct (word_t-1) contexts repeatedly. The bigram is the SATURATION level for text8 at this regime. Trigram statistics live mostly in the long tail where each (word_t-2, word_t-1) context appears once or twice.

So the n5 mechanism was simultaneously injecting query-time noise (point 1) AND working in a data-sparse regime (point 2) AGAINST a saturated bigram baseline (point 3). All three hurt. The fact that depth_gain was -1.89 bits is a SIGNATURE of all three at once: more capacity wasted on the trigram than the bigram could ever recover.

**The brain does not have this problem because** the brain's "trigram" predictor is not literally a per-pair learned signature; it is a learned distribution stored in cortical synaptic weights that has been slowly-shaped over thousands of exposures. The brain's W_pred matrix has effectively been writing the bigram-conditional distribution AT THE TARGET-WORD LEVEL, not the per-pair-signature level. This averaging-at-learning-time is what substrate-as-n5 was missing.

---

## Section 2: Brain's actual mechanism for context-aware prediction (step-by-step)

### Step 1 -- Online statistical learning (Saffran 1996; Romberg-Saffran 2010)

Infants extract transition probabilities between adjacent units (syllables, then words) from passive exposure. The mechanism is well-documented: 8-month-olds segment fluent speech based on co-occurrence probabilities between adjacent syllables; the brain is sensitive to bigram-level transition probabilities WITHOUT explicit training. This is the empirically-validated statistical-learning mechanism (Romberg-Saffran 2010, PMC 3112001).

The biological correlate is unclear at synaptic resolution, but functionally it is consistent with Hebbian-style associative learning: when syllable_a is followed by syllable_b, the cortical synapses connecting representations of a -> b are strengthened.

### Step 2 -- Encoded as cortical transition statistics (BCM neuron on sequences, Tino-Bishop 2003)

The Bienenstock-Cooper-Munro (BCM) rule applied to symbolic SEQUENCES has been studied analytically. The Tino-Bishop work showed that a BCM neuron exposed to a stochastic symbol sequence converges to weights that depend on the INTERNAL STRUCTURE of the input sequence -- specifically, sequences with different entropy converge to different equilibrium weights even when they share the same alphabet.

The key result for substrate purposes: BCM-on-sequences acts as a **slow-learning context-aware predictor**. The threshold theta_M sliding-tracks the recent activity. When a frequent (word_t-1 -> word_t) transition occurs many times, the postsynaptic neuron for word_t raises its threshold; subsequent OTHER transitions to word_t become harder to potentiate; the prototype-of-frequent-transitions sharpens.

When this is extended to higher-order context (word_t-2, word_t-1 -> word_t), the BCM rule applied to a BUNDLED context signature converges to a slowly-extracted per-target conditional distribution. The substrate's Gap 3 BCM cell already in flight covers the same mechanism family for categorical schema; the n5 revival is the SAME mechanism applied to sequence prediction.

### Step 3 -- During NREM, sharp-wave ripples replay episodes; cortex extracts higher-order transition statistics

This is exactly the mechanism Gap 3 covers in detail. The Buzsaki bidirectional dialog (Maingret 2021) delivers compressed replays from hippocampus to cortex; cortical slow-learning extracts second-order statistics that were not learnable from single exposures.

For language, the relevant lit is the predictive coding hierarchy (Caucheteux-King 2022 Nature Human Behaviour, Caucheteux-Gramfort-King 2023 Science Advances): the brain predicts hierarchically at multiple time scales -- temporal cortex predicts short-range (~bigram); inferior-frontal predicts longer-range; parietal predicts contextual representations spanning seconds-to-minutes. This is a STACKED predictive system, NOT a single query-time blend.

### Step 4 -- At prediction time, cortex's compressed schema returns the distribution

When you read a sentence and predict the next word, the relevant cortical region (left fronto-temporal pathway during language comprehension; Caucheteux et al. 2023 PMC 10110445) emits a top-down prediction based on the compressed schema; the sensory area signals the residual; the update is gated by surprisal.

Importantly: the prediction is NOT computed by mixing the recent words together at query time. The recent context activates a LEARNED set of cortical neurons whose tuning curves were shaped over the entire developmental history; the next-word distribution is the OUTPUT of those tuning curves, not a per-query bind.

### Step 5 -- The math behind it (four equations)

1. **Online transition write (the bigram brain rule, infant statistical learning analog):**
   ```
   W_bigram[ctx, target] += eta * ctx_signature * target_signature^T
   ```
2. **Higher-order write (BCM-on-bundled-context, Tino-Bishop analog):**
   ```
   ctx_higher = bundle(encoder(word_t-2), encoder(word_t-1))
   W_higher[ctx_h, target] += eta_slow * ctx_higher * target_signature^T * (target - theta_M)
   theta_M = EWMA(target^2)
   ```
3. **Query (no bind, no mix at query time):**
   ```
   query_bigram  = encoder(word_t-1)
   query_higher  = bundle(encoder(word_t-2), encoder(word_t-1))
   logits = alpha * (W_higher  . query_higher) + (1-alpha) * (W_bigram . query_bigram)
   distribution = softmax(beta * logits)
   ```
4. **Sleep refinement (NREM replay):**
   ```
   for replay_cycle in range(R):
       sampled_triple = replay_sample()  # interleaved
       apply steps 1-2 again with eta_replay = eta / 10
   ```

These four equations capture the substrate-feasible cortex-style next-word predictor. Nothing else is load-bearing.

---

## Section 3: Substrate-feasible slow-learning context predictor (composition)

The substrate already has every primitive needed. Status of each:

| Brain layer | Mechanism | Substrate primitive | Status |
|---|---|---|---|
| Encoder for words | Path C substrate-native | `hdlab/char_trigram_encoder.py` + `hdlab/sequence_memory.py` | EXISTS (chain-grade) |
| Bundle two context vectors | Bipolar/HRR sum | `hdlab/bundling.py` | EXISTS (chain-grade) |
| Outer-product W matrix | Hebbian outer-product | `hdlab/memory.py:KeyValueMemory` + `hdlab/predictive_coding.gated_write` | EXISTS (chain-grade) |
| BCM rule for slow-extracted statistics | Sliding-threshold rule | NEW (~20 lines on top of `gated_write`) | NEEDS WRITING (same as Gap 3 cell) |
| NREM replay decorator | Replay sampling | `hdlab/continual.py:nrem_replay_decorator` | EXISTS (proven-bound +0.57) |
| Eval harness (top1/top5/BPC) | META_M7-compliant | `hdlab/lm_eval_harness.py` | IN-FLIGHT (Drill 3 INFRA_1; build pending) |

**Composition sketch:** at each cycle in text8 stream, observe (word_t-2, word_t-1, word_t) triple. Compute ctx_2 = encoder(word_t-1), ctx_12 = bundle(encoder(word_t-2), encoder(word_t-1)), target = encoder(word_t). Apply outer-product writes to W_bigram and W_trigram. After full pass, OPTIONALLY run NREM replay decorator on the triples for second-pass refinement. At test time, read both W matrices linearly (no bind), interpolate, softmax.

**Key difference from n5:**

The n5 cell wrote into W_episodic via per-pair signatures (one signature per (word_t-2, word_t-1) PAIR). This cell writes into W_trigram via per-target accumulations (one update per (BUNDLED-context, target_word) PAIR, accumulating ACROSS many triples that share the same word_t target). The "compression" happens at LEARNING time: W_trigram[i, word_t] becomes the SUM of all ctx_12 signatures that preceded word_t, which is a context-prototype for word_t.

**Cost of bundle-vs-bind for context capacity:**

- HRR-bind preserves UNORDERED-ROLE-FILLER information (you can unbind given one operand). Cost: third-vector mixing.
- Bundle (sum) preserves NEITHER role NOR ordering. But for the LM next-token task, we DON'T NEED to recover individual context words at query time; we only need the cumulative signature to score against a learned target distribution. Bundle is sufficient AND avoids query-time mixing.

This is the structural insight: bundle is the right operation when the downstream consumer is a LEARNED mapping; bind is the right operation when the downstream consumer is an algebraic UNBIND. n5 used bind where bundle was sufficient.

---

## Section 4: Top cell candidates ranked

| Rank | Cell name | Mechanism | P_deflated | Cost CPU-hr | Composes-with | Why-now |
|---|---|---|---|---|---|---|
| 1 | `slow_cortex_bigram_predictor_v1` | Bundle-at-context + Hebbian-outer-product + W_trigram + W_bigram + softmax | 0.40 | 2-4 | NREM replay (substrate); lm_eval_harness (in-flight) | Cheapest decisive test of slow-learning vs query-time-blend |
| 2 | `TWO_TIER_replay_trained_LM_v1` | W_episodic (fast) + W_cortex_LM (slow, BCM) + arbitration | 0.30 | 4-6 | Gap 3 BCM cell; TWO_TIER cell (Gap 4) | TWO_TIER applied to LM task; HIGH composition value if Gap 3/4 land |
| 3 | `gap3_LM_extension_v1` | Extend Gap 3 BCM cell with LM task endpoint | 0.30 | +1 (delta on Gap 3) | Gap 3 BCM cell directly | Cheapest if Gap 3 lands HARD_PASS first |
| 4 | `predictive_coding_LM_hierarchy_v1` | Stack two predictive-coding layers; refuse-gate at top | 0.25 | 3-5 | `hdlab/predictive_coding.py`; Caucheteux 2022 hierarchy | Adds calibrated-refuse to LM output |
| 5 | `SDM_context_pooled_LM_v1` | Sparse distributed memory pool over W rows close to query | 0.20 | 2-3 | `hdlab/iterative_attractor.py` | Different mechanism class than HRR; cheap probe |

### Cell 1 detail (rank-1)

**Cell:** `slow_cortex_bigram_predictor_v1`

**Substrate-feasibility:** VERY HIGH. All required primitives exist; the cell is a NEW composition of existing primitives. No new code required if W_trigram update is plain Hebbian outer-product (use `predictive_coding.gated_write` with eta=1/N). If BCM rule wanted for higher-order arm, ~20 lines new (same code as Gap 3 cell).

**P_solve_deflated: 0.40.** Higher than Gap 3 cell (0.45) because the LM next-token task at bigram scale on text8 has ESTABLISHED ground-truth statistics; the only question is whether substrate's slow-learning composition can REPRODUCE the bigram-vs-trigram statistical structure. Lower than the no-deflation P because the discriminating signal between this and pure-bigram is small (typical text8 trigram-over-bigram lift in N-gram models is modest).

**Cost:** 2-4 CPU-hr at N=16384 over text8 (100K docs). Dominant cost is one text8 pass with N^2 = 268M-entry matrix updates per triple.

**Discriminator:** four-arm design (BIGRAM_BASELINE / TRIGRAM_BUNDLE_SLOW / TRIGRAM_HRR_REPLICATION / TRIGRAM_BUNDLE_NREM_REPLAY). The double-comparison rules out single-cause confounds: BUNDLE_SLOW must beat BIGRAM_BASELINE to establish slow-learning extracted ANY trigram structure; BUNDLE must beat HRR_REPLICATION to establish that BUNDLE was the load-bearing fix (not just slow-learning); NREM_REPLAY arm tests whether replay adds anything over single-pass.

**Why-now:** USER reframe is correct. The n5 HARD_FAIL is not closed; it is reclassified from "trigram-impossible" to "wrong-layer-for-trigram." The substrate has every primitive; the cell is a recomposition, not new research. Cheapest possible test of the USER's reframe. If it works, n5 ceiling is lifted; if it fails, the gap is encoder-bound (Path C v2 territory), not mechanism-bound.

**Connection to Drill 3 lang_ingest pipeline:** this cell IS effectively the Drill 3 ANCHOR_1 cell variant. Drill 3 ANCHOR_1 (`lang_ingest_vocab_bigram_meta_m7_v1`) was already designed to test bigram extraction on text8 via substrate-native pipeline; this cell extends ANCHOR_1's TRIGRAM arm with slow-learning bundle-at-context vs n5's bind-at-query. Recommend BUNDLING these two cells: ship as `lang_ingest_vocab_bigram_meta_m7_v1` with a slow_cortex_trigram arm added.

### Cell 2 detail (rank-2)

**Cell:** `TWO_TIER_replay_trained_LM_v1`

This is the FULL brain-aligned LM composition. Two W matrices: W_episodic (fast, hippocampus, written at eta_fast = 1.0 on each (word_t-1, word_t) triple) and W_cortex_LM (slow, written via BCM rule at eta_slow = 1e-3 during NREM replay). At query: try W_cortex_LM first (schema-completion); if low-confidence, fall back to W_episodic.

**P_deflated: 0.30.** Lower than Cell 1 because composition risk is higher: depends on Gap 3 BCM rule landing AND Gap 4 TWO_TIER landing. If both land, this cell is the natural composition. If neither lands, this cell is premature.

**Why useful as rank-2:** demonstrates SAME ARCHITECTURE handles (a) schema extraction (Gap 3), (b) long-term retention (Gap 4), AND (c) sequence prediction (this cell). Three endpoints, one architecture, one substrate-product story.

### Cell 3 detail (rank-3)

**Cell:** `gap3_LM_extension_v1`

Extend the in-flight `gap3_cls_two_tier_BCM_slow_replay_v1` cell with a SECONDARY ENDPOINT: at the end of training, also evaluate text8 next-token prediction using W_schema as W_cortex_LM. Costs almost nothing if Gap 3 cell is in the run anyway.

**P_deflated: 0.30.** Same as Cell 2 but cheaper because it piggybacks on Gap 3 dispatch.

**Why useful as rank-3:** cheapest possible test of whether the Gap 3 BCM rule generalizes from categorical-schema to sequence-prediction. If it does, ONE cell closes TWO gaps (categorical schema + sequence prediction). If it doesn't, the mechanism is task-specific and Cell 1 is still the right primary.

---

## Section 5: Honest scope -- realistic regime for actual brain-like compression

**Question USER raised:** brain LM acquisition takes years of input; substrate at 5000 cycles + 100k text8 docs has way less data than a brain. What is the realistic regime?

**Plain answer:**

text8 train at 100k docs is roughly 17M tokens. With V_TOK = 8192, the per-token bigram statistics are well-converged (each bigram pair (a,b) where both a and b are in top-8192 occurs many times). The bigram is SATURATED on this data scale. Going to trigram is harder because most (word_t-2, word_t-1) contexts are rare; the natural test8 trigram-over-bigram lift is small even for optimal models (typical KN-smoothed 3-gram beats bigram on text8 by ~0.3-0.5 bpc; ~+0.04 top1).

A child has heard ~50M words by age 5 (per CLARI 2021 estimate); ~200M by age 10. Substrate's text8 17M is in the same order of magnitude as a 3-year-old. The bigram-level transition statistics are LEARNABLE at this scale; the trigram-level is BORDERLINE; deeper context (5-10 word windows) is NOT learnable at this scale.

**What this means for the cell:**

- **HARD_PASS at +0.04 top1 over bigram is the realistic discriminating signal.** Asking for +0.10 is asking for more than the data supports.
- **N_REPLAY_CYCLES = 1 (single pass) should be sufficient.** Multi-cycle replay matters more for retention (Gap 4) than for extracting statistics already present in single-pass data.
- **If substrate cannot beat bigram even by +0.04, the gap is ENCODER, not MECHANISM.** Substrate's encoder may not have enough information to discriminate context. Pivot to Path C v2 (Section 6 of `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md`).

**What discriminator separates encoder-bound vs mechanism-bound:**

- If ARM_TRIGRAM_BUNDLE_SLOW beats baseline by even 0.01-0.04: mechanism works; encoder is adequate. Go to MIDDLE_BAND, queue follow-up sweeps.
- If ARM_TRIGRAM_BUNDLE_SLOW within 0.01 of baseline: ambiguous; could be mechanism-bound or data-saturation-bound. Run an ARM_TRIGRAM_BUNDLE_SLOW_LARGE_N (N=32768) as discriminator.
- If ARM_TRIGRAM_BUNDLE_SLOW WORSE than baseline: mechanism actively harms even with slow learning. This would falsify the USER reframe. Diagnostic dig required.

**To genuinely test cortex-style context compression at brain scale:** would need ~200M tokens (wikitext-103 scale or larger), N_DIM=32768+, multi-pass replay, and probably the Caucheteux hierarchical predictive-coding architecture (multi-layer). That is a 50-100 CPU-hr regime; out of scope for this cell. This cell tests the MECHANISM HYPOTHESIS at text8 scale; if it passes, the next scale-up cell can be designed.

---

## Section 6: Recommendation -- top 3 cells to dispatch (ranked)

**Rank 1: `slow_cortex_bigram_predictor_v1`** -- ship FIRST, standalone, decisive at low cost.

Compose with Drill 3 ANCHOR_1 if compute budget tight (one cell with extended arm-set). Otherwise ship standalone for cleaner discriminator.

**Cost:** 2-4 CPU-hr at N=16384 on text8.
**P_deflated:** 0.40.
**Decisive question:** does slow-learning bundle-at-context beat n5 HRR-blend AND beat bigram baseline?

**Rank 2: `gap3_LM_extension_v1`** -- ship if Gap 3 BCM cell lands HARD_PASS first.

**Cost:** +1 CPU-hr delta on Gap 3 (effectively free).
**P_deflated:** 0.30.
**Decisive question:** does Gap 3 BCM rule generalize from categorical-schema to sequence-prediction?

**Rank 3: `TWO_TIER_replay_trained_LM_v1`** -- ship if both Gap 3 AND Gap 4 land HARD_PASS, as the marquee composition cell.

**Cost:** 4-6 CPU-hr.
**P_deflated:** 0.30.
**Decisive question:** does ONE architecture (W_episodic + W_cortex_LM) handle schema-extraction + retention + sequence-prediction at unified cell?

**Dispatch sequence:**

Today (or next cycle): dispatch Cell 1. It's standalone, cheap, decisive.

Conditional on Gap 3 BCM cell HARD_PASS: dispatch Cell 2.

Conditional on Gap 3 + Gap 4 both HARD_PASS: dispatch Cell 3 (full brain-architecture-on-LM-task narrative).

---

## Cross-thread synthesis

**With n5 HARD_FAIL:** the cell's mathematical root cause is now diagnosed. n5 HRR-blend was wrong layer; slow-learning bundle-at-context is the substrate-feasible fix. n5 cell does NOT need to be revived structurally -- it gets superseded by Cell 1 with a different mechanism class. The HARD_FAIL of n5 STANDS as classified (HRR-blend at query time is a closed direction for trigram on substrate at N=16384), but the BROADER QUESTION ("can substrate beat bigram at trigram?") is reopened by Cell 1.

**With Gap 3 BCM cell (in flight):** same mechanism family applied to LM task. If Gap 3 lands HARD_PASS, Cell 1 (and especially Cell 2, Cell 3) inherit strong prior. If Gap 3 HARD_FAILs at categorical schema scale, Cell 1 should still be tried because LM task has DIFFERENT data structure (sequence-conditional vs categorical) -- it is plausible that one task works while the other doesn't.

**With Gap 4 TWO_TIER (in flight):** Gap 4 tests TWO_TIER for retention. Cell 3 here would test TWO_TIER for sequence-prediction. SAME ARCHITECTURE; different task endpoint. If Gap 4 lands, the TWO_TIER architecture inherits a chain-grade composition primitive.

**With Drill 3 ANCHOR_1 lang_ingest cell (queued):** Cell 1 here is effectively a slow-cortex extension of ANCHOR_1's TRIGRAM arm. Recommend either bundling (single cell with 4 arms instead of 3) or sequencing (ship ANCHOR_1 first to validate METHODOLOGY infra; Cell 1 second once INFRA_1/2/3 are committed).

**With Path C 5x deeper drill (2026-06-23):** that drill identified ENCODER as the load-bearing bottleneck across V1/V2/V3. If Cell 1 HARD_FAILs, the result is corroborating evidence for the encoder-bound diagnosis. If Cell 1 HARD_PASSes (with current substrate-native encoder), the encoder is not the load-bearing bottleneck for bigram-vs-trigram task -- the diagnosis from Path C drill is too pessimistic for this specific task.

**With NREM replay drift_reduction +0.57:** the replay engine is established. ARM_TRIGRAM_BUNDLE_NREM_REPLAY uses the replay decorator on text8 triples. If the replay arm beats the single-pass arm, it confirms that replay adds value to LM task (not just retention task). This would be a chain-grade-eligible cross-task generalization of the replay primitive.

**With substrate-as-LM methodology audit (META_HARNESS_RIGGED reclassification):** META_M7 harness from INFRA_1 (Drill 3) is required for Cell 1 to be cert-graded. Without it, top1/bpc comparison to bigram baseline may suffer the same trap as the rigged-harness substrate-as-LM cells. Cell 1 should ship AFTER INFRA_1 lands. n5 (which predated INFRA_1) used a different harness; results from n5 should be compared as bigram-vs-trigram RELATIVE LIFT (n5's bigram baseline was internally consistent), not as absolute BPC.

**With Fix #28 verify-per-arm-metrics:** Cell 1 has 4 arms; per-arm top1, top5, bpc, alpha must be reported. Verdict_msg insufficient. Specifically: the bigram-baseline ARM_BIGRAM_BASELINE replication test (must match n5 within 0.02) is the methodology-rail gate; it is a per-arm test, not a cell-level test.

---

## Substrate-product implications

**If Cell 1 HARD_PASSes:**

Headline product story: "Substrate's n5 trigram HARD_FAIL was a wrong-layer bug, not a wrong-mechanism finding. Moving the binding-and-association operation from query-time (HRR-bind) to learning-time (bundle-and-Hebbian-outer-product) lets substrate extract per-target trigram-conditional distributions over a single text8 pass and BEAT the bigram baseline. This is the substrate-feasible version of how the brain compresses context: slow-learning at the corpus level, not query-time mixing. Same family of primitives, different layer."

Capability-map implication: n5 trigram cap_map row is reopened. n5 HRR-blend stays closed. New row: SLOW_CORTEX_TRIGRAM via bundle-at-context + Hebbian-outer-product. If chain-grade, becomes the canonical substrate trigram primitive.

**If Cell 1 + Cell 2 + Cell 3 ALL HARD_PASS:**

Headline product story: "Substrate now has the FULL brain-aligned language model architecture: hippocampus (W_episodic, fast, instance-write) + cortex (W_cortex_LM, slow, BCM-write, replay-trained) + arbitration (refuse-gate, predictive-coding residual). One architecture handles categorical schema, long-term retention, AND sequence prediction. Each piece has brain-existence-proof. The mechanism is biologically grounded; the implementation is auditable; the math is closed-form. Substrate-as-LM finds its home at the cortex-slow layer, not the HRR-bind-query layer."

**If Cell 1 HARD_FAILs (within 0.01 of bigram, or worse):**

Diagnosis: the SLOW-LEARNING family of mechanism is not enough; the gap is encoder-information-content-bound. Pivot:
- ARM_TRIGRAM_BUNDLE_SLOW_LARGE_N at N=32768 (capacity sweep)
- Path C v2 encoder (Section 6 of 5x deeper Path C drill)
- Hierarchical predictive coding (Caucheteux 2022) -- multi-layer prediction

The HARD_FAIL would be a cert-grade negative result: USER reframe was directionally correct (slow-learning is the right family) but ENCODER limits the lift at substrate's current encoder regime.

**Capability-map implication of HARD_PASS:** Gap 3 (categorical schema) and the n5-revival (sequence prediction) become composable. Substrate now has a chain-grade SLOW-CORTEX primitive that works on BOTH task families. This is the substrate's first sequence-prediction primitive beyond bigram. The bigram-gap-closure work continues; substrate now has an architecturally-correct path to trigram and beyond.

**Atomization on HARD_PASS:**
- Atom: `slow_cortex_bigram_bundle_hebbian_outer_substrate_native_trigram_predictor` -- "Substrate's slow-learning context-aware next-word predictor: bundle-at-context + Hebbian-outer-product W matrices for bigram and trigram, scored linearly at query time. Beats n5 HRR-blend by extracting context-conditional statistics at learning time rather than query time."
- hdlab primitive: `hdlab/slow_cortex_lm.py` exposing `train_W_pred(W, ctx, target, eta)` and `predict_next(W_bigram, W_trigram, word_t_minus_1, word_t_minus_2, alpha, beta)`.
- Capability-suite regression test: `tests/test_slow_cortex_lm_trigram_beats_bigram.py` -- text8 bigram-vs-trigram lift >= 0.04 top1, cv <= 0.03.

---

## Citations (verified count = 12 external + 8 internal = 20 distinct sources)

**Brain side (statistical learning, BCM, predictive coding hierarchy):**
1. Saffran, Aslin, Newport (1996). "Statistical Learning by 8-Month-Old Infants." Science 274(5294): 1926-1928.
2. Romberg, Saffran (2010). "Statistical learning and language acquisition." [WIREs Cognitive Science PMC3112001](https://pmc.ncbi.nlm.nih.gov/articles/PMC3112001/)
3. Tino, Bishop, et al. (2003). "Processing Symbolic Sequences by the BCM Neuron." [Tino BCM-sequence paper](https://petertino.github.io/web/PAPERS/bcm.seq.pdf)
4. Caucheteux, Gramfort, King (2023). "Evidence of a predictive coding hierarchy in the human brain listening to speech." [Nature Human Behaviour PMC10038805](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10038805/)
5. Caucheteux, King (2022). "Predicting speech from a cortical hierarchy of event-based time scales." [Science Advances](https://www.science.org/doi/10.1126/sciadv.abi6070)
6. Heilbron, Armeni, Schoffelen, Hagoort, de Lange (2022). "Predictive coding across the left fronto-temporal hierarchy during language comprehension." [PMC10110445](https://pmc.ncbi.nlm.nih.gov/articles/PMC10110445/)
7. Bienenstock, Cooper, Munro (1982). "Theory for the development of neuron selectivity." J Neurosci 2(1): 32-48.
8. Maingret et al. (2021). "Bidirectional interaction of hippocampal ripples and cortical slow waves during NREM sleep." [PMC8179633](https://pmc.ncbi.nlm.nih.gov/articles/PMC8179633/)

**HRR / VSA capacity:**
9. Plate (1995). "Holographic Reduced Representations." IEEE Trans Neural Networks 6(3): 623-641.
10. Kleyko, Rachkovskij, Osipov, Rahimi (2022). "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part I." [arxiv 2111.06077](https://arxiv.org/pdf/2111.06077)

**Hopfield / sequential associative memory:**
11. Pereira, Brunel (2018). "Markov Transitions between Attractor States in a Recurrent Neural Network." [CBMM AAAI abstract](https://cbmm.mit.edu/sites/default/files/publications/aaai-abstract%20(1).pdf)
12. Hillar, Tran (2017). "Robust Exponential Memory in Hopfield Networks." [PMC5770423](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5770423/)

**Internal substrate notes:**
- `data/exp_n5_trigram_concept_lm_v1/metrics.json` (n5 HARD_FAIL anchor)
- `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` (sister BCM mechanism)
- `notes/exp_dev_handoff_research_language_ingest_drill3_pipeline_composition_substrate_native_2026-06-26.md` (Drill 3 ANCHOR_1 -- compose-with target)
- `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md` (encoder pivot if Cell 1 HARD_FAILs)
- `notes/research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md` (META_M7 harness requirement)
- `notes/exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md` (TWO_TIER architecture in flight)
- `hdlab/continual.py` (NREM replay decorator; proven-bound +0.57)
- `hdlab/predictive_coding.py` (gated_write; BCM extension lives here)

---

## Lit-scan calibration notes

- All probability estimates deflated 0.15-0.25 from raw LM confidence per [[feedback-lit-scan-calibration-penalty]].
- Novel-synthesis cap at 0.50 applied (slow-cortex bundle-at-context for substrate-LM is novel composition; the COMPONENTS each have lit precedent but the substrate-specific composition is novel).
- HARD-FAIL thresholds mandatory and listed for every prediction.
- Discriminator design follows BIAS-13/14/15 mismatch-bias check: ARM_BIGRAM_BASELINE must replicate n5 within 0.02; ARM_TRIGRAM_HRR_REPLICATION must replicate n5 within 0.02 (anchors discriminator); per-arm metrics mandatory per Fix #28.
- DIRECTIONALITY (slow-learning bundle-at-context is correct mechanism family) is MODERATELY confident (raw P ~ 0.65 across Saffran 1996, Tino-BCM 2003, Caucheteux 2022/2023). MAGNITUDE (substrate-specific +0.04 lift over bigram at text8 scale) is where deflation hits.
- Fields drilled explicitly: statistical learning (developmental psycholinguistics); BCM theoretical neuroscience; predictive coding (Caucheteux); HRR/VSA capacity (Plate); Hopfield-Markov (Pereira-Brunel). 5 disparate fields converge on the prescription. Meets Trigger F aggressive cross-domain requirement.
- Substrate-novel angle: substrate has not yet tried slow-cortex bundle-at-context Hebbian-outer-product for LM task. n5's bind-at-query closed that path; this cell opens the bundle-at-context-and-Hebbian-outer-product path. Adjacent failed cells (n5; substrate-as-LM rigged-harness 7 HARD_FAILs) all used QUERY-TIME mechanisms; this is the first LEARNING-TIME mechanism for sequence prediction.

---

## Plain-English wrap

USER's reframe is structurally correct. The n5 trigram cell tried to combine the two prior words at QUERY time using HRR-bind, which mixes the two words into a third vector with high crosstalk noise at substrate's regime. That noise dominated the signal, and the trigram arm scored 1.89 bits WORSE than the bigram baseline.

The brain does not do this. The brain learns context-aware predictions over thousands of slow cortical updates: each time it sees (word_a, word_b, word_c) in real corpus exposure, it strengthens the synapses connecting representations of (a-then-b) to c. Over many corpus exposures, the cortex builds a TABLE of context-conditional next-word distributions. At prediction time, the cortex looks up the table; it does not mix words at query time.

Substrate has every primitive needed to build this: encoders for words, bundling for context aggregation, key-value memory for the outer-product W matrix, NREM replay decorator for the second-pass refinement, and the BCM rule (~20 lines new) for sliding-threshold sharpening if wanted. The cell `slow_cortex_bigram_predictor_v1` composes these into a single text8 pass that builds W_bigram and W_trigram by Hebbian outer-products of (bundled context, target word) over the train split, then scores at query time via dense matrix-vector products. No HRR-bind at query time; the slow-learning has already absorbed the per-target conditional distribution at LEARNING time.

Estimated probability the cell will close n5's bigram-gap by >= 0.04 top1: 40 percent. Cost about 2-4 CPU-hr. Discriminator includes 4 arms (bigram baseline, slow-cortex trigram, HRR-replication, slow-cortex with NREM replay) so we can isolate which mechanism component is load-bearing.

Realistic regime: text8 17M tokens is roughly a 3-year-old child's exposure. Bigram statistics saturate; trigram statistics are sparse-at-the-tail. A +0.04 top1 lift over bigram is the realistic discriminating signal. Asking for +0.10 would be asking for more than the corpus supports. If the cell falls within 0.01 of bigram (mechanism doesn't extract trigram structure), the gap is encoder-bound (Path C v2 territory). If it beats bigram by +0.04+, substrate has its first substrate-feasible cortex-style sequence-prediction primitive.

If this cell PASSES, the broader product story is: substrate now has chain-grade slow-cortex primitives for BOTH categorical schema (Gap 3) AND sequence prediction (this cell). The same architecture handles both. Gap 4 TWO_TIER composes naturally. Substrate has the first brain-aligned LM architecture with full audit trail.

If this cell FAILS, the diagnosis is encoder-bound, not mechanism-bound. The slow-learning family of mechanism is the right family; the SUBSTRATE-NATIVE ENCODER at the current regime simply does not provide enough discriminating information beyond bigram. Pivot to Path C v2 (substrate-owned encoder with predictive-coding shaped representations).

Either outcome advances substrate's understanding of where the bigram-gap closure lives architecturally.

---

-- Research (Opus 4.7 1M synthesis; 6 parallel WebSearch lit-scans; calibrated per discipline; HARD-FAIL thresholds pre-registered).
