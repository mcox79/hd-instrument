# Pre-registration: path_b_pythia_160m_frozen_encoder_dual_gain_v1

**Date:** 2026-06-23
**Anchor:** path_b_pythia_160m_frozen_encoder_dual_gain_v1
**Queue:** overnight_queue
**N:** 8192, **Seeds:** [7, 17, 23], **Encoder under test:** EleutherAI/pythia-160m (frozen)

## Scientific question

Does a FROZEN open-weights pretrained transformer (pythia-160m, trained on The Pile, fully published architecture + corpus + checkpoints) used as a substrate token encoder (mean-pool of last-layer hidden states, projected to N_DIM=8192 via fixed Gaussian) close the dual-gain criterion (both cleanup-recall@sigma=1.5 AND substrate-LM BPC vs unigram) that ALL prior forward-only / Hebbian / SoftHebb / Foldiak / FPE encoders failed?

USER 2026-06-22 blocked MiniLM / BGE / proprietary embeddings; pythia is a different category (open-weights public, published training data); USER 2026-06-23 explicitly authorized following all encoder-path angles including this one ("I'm open to being wrong here"; "yes follow all of these angles").

## Pre-registered bands

**HARD-PASS (chain-grade-eligible; dual-gain confluence):**
- Metric A: ARM_PYTHIA_160M_FRESH_W cleanup recall@1 at sigma=1.5 >= 0.20 AND cv across seeds <= 0.30
- Metric B: ARM_PYTHIA_160M_FRESH_W BPC < (ARM_WORD2VEC_FRESH_W BPC - 0.3) AND BPC < 7.738 AND BPC cv <= 0.05
- BOTH metric A AND metric B must pass.

**MIDDLE:** Pythia clears exactly one of A or B but not both (partial-mechanism; characterizes whether encoder semantic depth helps cleanup vs LM separately).

**HARD-FAIL:** Pythia fails BOTH:
- Metric A FAIL: cleanup@sigma=1.5 <= 0.05 (no lift over baseline ~0.022)
- Metric B FAIL: ARM_PYTHIA_160M_FRESH_W BPC >= ARM_WORD2VEC_FRESH_W BPC OR BPC >= 7.738

## Sanity gates (CONFOUND_FAIL detector)

- ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM at lambda=1.0 BPC must equal ARM_PYTHIA_160M_FRESH_W raw BPC (within 0.05 bits).
- ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM at lambda=0.0 BPC must equal ARM_UNIGRAM BPC (within 0.05 bits).
- cleanup recall@sigma=0 must be 1.000 on all arms (or arm trivially-broken).
- _LLM_CALL_COUNTER must be 0 at end (pythia ran once as static lookup; substrate-only at inference).

## Calibration rationale

- HP_BPC_BAR = 7.738 (unigram floor on text8; locked from text8_substrate_pseudoLM_v2 / fresh_W_bpc_per_encoder_v1).
- HP_BPC_LIFT_OVER_W2V = 0.3 bits: a meaningfully large lift over word2vec (which itself was the prior strongest semantic encoder). word2vec on Path A landed ~7.864 BPC; a 0.3-bit lift puts pythia at <=7.564, comfortably below unigram. Smaller lifts would be measurement noise on text8.
- HP_CLEANUP_RECALL_15 = 0.20: substantially above baseline ~0.022 (10x lift); matches the bar from encoder_dual_gain_softhebb_v1 prereg so cross-cell comparison is direct.
- HF_CLEANUP_RECALL_15 = 0.05: only modest lift (~2x baseline) is uninteresting; if pythia can't clear this it's effectively the substrate W matrix that's bottleneck-bound regardless of encoder quality.
- HP_CLEANUP_CV_MAX = 0.30 and HP_BPC_CV_MAX = 0.05: matches prior fresh-W methodology (BPC is much tighter across seeds than cleanup recall).

## Why this matters

The forward-only encoder family exhausted (Path A char-trigram + word2vec / glove / fasttext; encoder-side Hebbian SoftHebb / Foldiak / FPE) all failed to clear dual-gain. The substrate-W bottleneck hypothesis says no encoder helps. The encoder-quality hypothesis says a sufficiently-deep pretrained encoder DOES help. Pythia-160m is the cheapest open-weights pretrained transformer that's not blocked by USER directives; this discriminates between the hypotheses.

If HARD_PASS: substrate as token-LM is unblocked via open-weights pretrained encoders. Then we can scale pythia (410m, 1b, 2.8b) and have a working substrate-LM evaluation pipeline + a working Hebbian-readout under the open-weights regime.

If HARD_FAIL: substrate W rank-1 readout is encoder-invariant cap; pivot to architectural rewrite (multi-step readout / non-Hebbian update / sparse codebook).

## N-suffix section

Anchor has no _n<N> suffix; N_DIM=8192 is set as a module constant. PROT-018 binding does not apply (no _n<digits> token in anchor name).

## Timeout estimate

Smoke target: V=200, N_TRAIN=2000, N_HELD=400, N_DIM=8192, seeds=[0], pythia-160m forward over 200 tokens. Expected ~30-90s on GPU; CPU smoke fits under 180s (the small vocab keeps pythia inference bounded).

FULL: V=4000, N_TRAIN=100k, N_HELD=20k, N_DIM=8192, seeds=[7,17,23], + pythia inference over 4000 tokens (~2-4s on GPU).
- pythia encode vocab: ~10s GPU
- Hebbian W build per arm (3 arms x 3 seeds x 100k pairs at 8192d) on GPU: ~3-5min per arm-seed, ~30-45min total
- BPC eval per arm-seed: ~1-2min total per arm-seed
- Cleanup sweep: <1min total

Rough estimate: 60-90min wall on remote GPU. Pad 1.5x for cold cache + first-token tokenizer warmup + log-linear sweep on pythia+LL arm. Target 5400s (90min). PROT-019 floor does not apply (anchor not _n>=4096).

timeout_s = 5400 (1.5 hours)
