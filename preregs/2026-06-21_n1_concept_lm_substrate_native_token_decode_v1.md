# Prereg: n1_concept_lm_substrate_native_token_decode_v1

**Anchor:** `n1_concept_lm_substrate_native_token_decode_v1`
**Script:** `experiments/exp_n1_concept_lm_substrate_native_token_decode_v1.py`
**Date:** 2026-06-21
**Queue:** `remote_cpu_queue` (residuals_per_token.npz lives on marsh@home; not present locally)
**Config version:** `V_C=256,N_DIM=1024,DECODE=freq,MAX_DOCS=100000,SEEDS=7-17-23,SPLIT=0.8`
**PROT-018:** No `_nN` suffix; production N_DIM=1024 (codebook dimension, not a sweep axis).
**Program:** N1 of the USER-ratified substrate-native LM program.

## Hypothesis

The substrate can act as a token-level language model without calling any external
transformer at inference. The concept transition memory W captures next-concept
predictions (~bigram level, verified by v1 cell). A substrate-native decode memory D
(Hebbian concept->token binding) then converts the predicted concept to a token
prediction. Together these form a fully substrate-native LM path:

  token_t -> residual -> concept_t --[W]--> concept_{t+1} --[D]--> token_{t+1}

No LLM head is called at inference. The decode is purely D^T @ C[concept_id].

## Substrate-only-ness gate

- INGEST (allowed): Pythia-160m ran once to produce per-token residuals. Token
  embeddings in D are static column sums of C[concept_id] vectors (NOT LM-head
  logits). The LLM is never called at inference.
- INFERENCE (substrate-native): W (concept->concept Hebbian cf-RPE) and D
  (concept->token Hebbian association, D[:,tok] += C[concept] for each
  (concept,token) observation at train) operate purely on substrate vectors.

## Decode mechanism (one sentence)

At each train step, the concept vector C[concept_id] is added to column D[:,token_id],
accumulating a Hebbian association; at inference, scores = D^T @ C[pred_concept] ranks
all tokens by how often they co-occurred with that concept in training.

## Data dependency

`data/exp_phase05_v1_pythia160m_residual_extract_pertoken_v1/residuals_per_token.npz`
must be present on the runner. Local laptop has only a metrics.json stub. Ship to
`remote_cpu_queue` ONLY (marsh@home has the full file).

## Pre-registered threshold bands (TOKEN BPC -- lower is better)

**Calibration-probe policy applies:** no prior empirical anchor for this exact
token-level pipeline. Bands set per calibration-probe policy: +/-50% of theoretical
prediction, NOT the theoretical point.

Theoretical prediction: substrate BPC ~ unigram_BPC - ~5-10%.
Unigram BPC ~ log2(V_TOK) ~ 14-16 bits (GPT-2 tokenizer, actual corpus vocab).
Expected substrate BPC: ~13-15 bits.

### HARD-PASS
substrate_bpc <= bigram_bpc + 0.5  AND  substrate_bpc <= 0.95 * unigram_bpc

Interpretation: substrate beats pure unigram by >=5% in BPC AND comes within 0.5 bits
of token-bigram. This would confirm the substrate concept path provides meaningful
token-level compression beyond unigram.

### MIDDLE-BAND
substrate_bpc <= 0.99 * unigram_bpc

Interpretation: substrate token decode is better than pure unigram by >=1%, but not
reaching near-bigram level.

### HARD-FAIL
substrate_bpc >= unigram_bpc

Interpretation: the concept bottleneck costs more than it saves; no token-level
improvement over unigram.

Note (calibration-probe): bands are wide per policy; no prior empirical anchor.
The analytic ceiling measures the irreducible concept-bottleneck cost:
ceiling_bpc >= bigram_bpc (ceiling uses PERFECT concept prediction; gap =
H(token|concept), the many-to-one information loss at the VQ bottleneck).

### Concept-level sanity (secondary, not verdict-bearing)
substrate_concept_top1 should reproduce ~0.446 from the v1 verified result.
If substrate_concept_top1 < 0.35, flag as data/pipeline anomaly and audit.

## N-suffix section

No `_nN` suffix. Production N_DIM=1024 (hypervector dimension). V_C=256 (concept
vocab). Neither is a primary sweep axis. Per PROT-018 no-suffix declaration.

## Anti-leakage guard

- VQ (MiniBatchKMeans) fit on TRAIN tokens only; TEST tokens assigned via predict().
- Decode memory D accumulated on TRAIN (concept,token) pairs only.
- Concept->token ceiling oracle computed from TRAIN conditional counts only.
- Train/test split is DISJOINT at the doc level (shuffle + 80/20 split).
- No test tokens influence W, D, VQ centroids, or baseline counts.

## Self-test

`_instrumentation_selftest()` called at module scope. Tests:
1. cf-RPE transition store+recall on synthetic 8-concept, 128-dim data.
2. Decode memory D argmax (concept 3 -> token 7 with 10x weight vs 1x for tok 2).
3. BPC formula: -log_p(tok) / log(2), checked for finite positive value.
4. doc_boundaries slice: 3 docs from [0,3,7,12] boundaries.
5. Instrumentation: all 8 claimed metrics non-null after one synthetic forward pass.

## Timeout estimate

Smoke not run locally (data absent). Estimate from v1 cell analogy:
- v1 cell (concept-only): 3 seeds, ~V_C=256, full run. Runtime unknown from metrics
  but remote_cpu_queue runs are typically 5-30 min for this data size.
- N1 adds decode memory D (V_TOK ~50k columns) and token-level eval loop.
  D is (1024 x 50000) = 200MB float32; accumulation is O(n_train_tokens * N_DIM).
  At ~10M train tokens: 10^7 * 1024 ops = ~10^10 flops; ~50s at 200 GFLOP/s CPU.
  Per-seed estimate: 3-8 min. 3 seeds: ~10-25 min.

timeout_s = ceil(1.5 * 600 * 1 * 3) = 2700 (conservative 10min/seed * 1.5 margin * 3)
Rounded to nearest 300: **timeout_s = 2700**

Note: D accumulation is the new cost vs v1; if V_TOK is small (token_ids absent
scenario: V_TOK = min(50257, actual)), runtime is dominated by W training (same as v1).

## Middle-band outcome plan

If MIDDLE_BAND: substrate beats unigram but misses bigram threshold. Route research
2x-revival note: (a) investigate improving D precision via per-concept normalization;
(b) test weighted D (frequency weighting vs flat LR_DECODE=1); (c) test N_DIM=2048.
Do NOT re-run at FULL N immediately without the research drill.

## Data-availability caveat

residuals_per_token.npz is ABSENT on local laptop (only metrics.json stub at the
data path). Full npz is on marsh@home (remote). This experiment MUST run on
remote_cpu_queue. Dispatching to local_cpu_queue or overnight_queue (GPU) is
wrong -- GPU queue is not needed (pure numpy/sklearn), local has no data.
