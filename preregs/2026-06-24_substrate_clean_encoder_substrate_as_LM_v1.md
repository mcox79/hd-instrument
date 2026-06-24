# Pre-reg: substrate_clean_encoder_substrate_as_LM_v1

Date filed: 2026-06-24
Filed-by: exp_dev
Trigger: Research routing -- TOP-5 bias #5 (encoder-leakage) decisive test
Cell: experiments/exp_substrate_clean_encoder_substrate_as_LM_v1.py

## Why (master-bias-memory: bias #5 encoder-leakage)

word2vec-google-news-300 was trained on ~100B tokens of Google News. text8 is
a 100MB subset of Wikipedia. PTB / Wikipedia / Google News distributional
overlap is non-trivial. When the substrate uses word2vec-google-news as its
input encoder and we measure "+12% top1 vs unigram", that lift could be:

  (a) Genuine substrate capability: rank-1 Hebbian W learning a transition
      structure on top of the encoder.
  (b) Encoder-leakage: word2vec's pretrained Google-News distributional
      knowledge bleeding through; the substrate is largely a passive carrier
      of word2vec's similarity structure.

This cell distinguishes (a) vs (b) by replacing word2vec-google-news with
a CLEAN encoder trained ONLY on text8's training split (no external data).
Same sparse-bipolar projection, same Hebbian W, same eval; only the encoder
varies.

## Arms (4 arms, single seed=7; pure numpy; remote_cpu)

| Arm | Encoder | OOV | Predicted BPC | Role |
|-----|---------|-----|---------------|------|
| A_W2V_GOOGLE_NEWS         | word2vec-google-news-300 (provenance rail) | char-trigram   | ~7.3065 +- 0.05 | sanity rail |
| B_W2V_TEXT8_ONLY          | Word2Vec trained on text8 training split only | char-trigram   | varies | PRIMARY |
| C_RANDOM_PROJECTION       | Fixed Gaussian projection (no semantic structure) | identity (random) | ~9-10 | floor |
| D_CHAR_TRIGRAM            | Bag-of-char-trigrams bipolar sign encoder | by construction | ~7.22-7.30 | substrate-native floor |

All arms use IDENTICAL sparse-bipolar projection at f=0.05 on top of the
encoder output, IDENTICAL rank-1 Hebbian W, IDENTICAL joint (T, lambda)
sweep on dev half, IDENTICAL ctx-unk filter, IDENTICAL alpha=0.1 Laplace.
The single varied knob is the ENCODER.

## Lane / discriminator

- LANE_2 declared (intra-corpus substrate-vs-substrate ablation; encoder is
  the ONE varied dimension).
- INTRA_LANE_DELTA = ARM_B - ARM_A (the clean-vs-leakage delta).
- CONFOUND_AUDIT (3 confounds named, controlled-or-acknowledged):
    1. Training-data-size: word2vec-google-news ~100B tokens; text8 clean
       encoder ~17M tokens (~6000x less). Confound: clean encoder may
       under-train. Mitigation: epochs=10 on text8 + dim=300 (matched) is
       standard for clean text8 word2vec; if under-training is the issue,
       arm B lands well-above 8.5 BPC; that itself is informative.
    2. OOV handling: both A and B use char-trigram fallback for OOV. Arm C
       cannot OOV. Mitigation: report n_oov per arm.
    3. Dim-mismatch: pretrained 300d projected to N_DIM=8192 via Gaussian.
       Same projection applied to both word2vec variants. Mitigation: same
       Gaussian seed across arms; arms A and B share the projection.

## Pre-registered HARD bands (PRE-REGISTERED BEFORE RUN; do NOT adjust)

PRIMARY arm = ARM_B_W2V_TEXT8_ONLY. PRIMARY rail = ARM_A_W2V_GOOGLE_NEWS.

HARD_PASS_LEAKAGE_REAL:
  ARM_B BPC >= ARM_A BPC + 0.30
  AND ARM_A within +/- 0.05 of 7.3065 (sanity rail OK)
  => word2vec's pretrained Google-News knowledge was load-bearing for
  substrate's "+12% top1" claim; substrate is partially measuring word2vec
  (not just substrate W). Action = re-tier all substrate-as-LM cf-RPE /
  STDP / heterogeneous-plasticity results that used word2vec-google-news;
  need cleaner encoder for chain-grade substrate claims.

HARD_PASS_LEAKAGE_NEGLIGIBLE:
  ARM_B within +/- 0.10 of ARM_A
  AND ARM_A within +/- 0.05 of 7.3065 (sanity rail OK)
  => substrate's capability is robust to encoder choice; word2vec gives
  the same boost a clean-text8-only encoder would. The "+12% top1" is
  genuine substrate work, not leakage.

MIDDLE_BAND_PARTIAL_LEAKAGE:
  ARM_B - ARM_A in [+0.10, +0.30]
  AND ARM_A sanity rail OK
  => partial leakage contribution; substrate still has real capability
  but encoder lift is non-trivial. Action = report magnitude; route to
  Research for decision.

HARD_FAIL_DECISIVE:
  ARM_A diverges from 7.3065 by > 0.10 (sanity rail FAILS)
  => cell uninterpretable; harness bug / load failure / config drift.

Secondary signals (informational, not bands):
- ARM_C_RANDOM_PROJECTION should land ~9-10 BPC (close to uniform 11.97).
  If C lands < 8.5, the "random projection" is accidentally semantic (e.g.,
  via the sparse-bipolar topk step picking up shared digits) -> harness bug.
- ARM_D_CHAR_TRIGRAM should land near cleanup-cells reference ~7.22 +- 0.10.
  If D and A differ significantly, that recovers the
  exp_substrate_encoder_ablation_on_fair_harness_v1 finding (independent
  cross-check; not a new claim).

## Config (FULL run)

- N_DIM = 8192
- N_TRAIN = 100_000 tokens, N_HELD = 20_000 tokens
- VOCAB_CAP = 4000
- text8 corpus (data/text8_cache/text8.txt; ~17M tokens)
- TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
- MRR_K = 10
- seeds = [7]
- Sparse-bipolar f=0.05 on ALL arms (matched primitives)
- Rank-1 Hebbian W; joint (T, lambda) sweep on dev half; report on test half
- Clean-encoder Word2Vec config: dim=300, window=5, min_count=5, epochs=10,
  workers=4 (gensim default sensible)
- Routing: remote_cpu_queue (pure numpy + gensim CPU; PROT-020)

## Critical disciplines

- Apples-to-apples lane 2 declared (encoder is the ONE varied knob)
- Single primary metric = BPW (top1 + MRR secondary)
- Pre-reg PRIMARY arm declared: ARM_B_W2V_TEXT8_ONLY
- Fix #14: ONE cell
- Fix #28: per-arm metrics ONLY; no cross-arm framing in verdict_msg
- Fix #26: predispatch_check passed (PROCEED, 0 prior landings)
- A5: path-scoped commit
- ASCII-only, no emojis, no em dashes
- PROT-018: no _nN suffix
- PROT-020: pure numpy -> remote_cpu_queue
- Substrate-only-decode gate asserted (zero LLM forward calls; word2vec is
  static open-weight lookup, not a forward LLM call)
- WHAT_THIS_DOES_NOT_SHOW clause in detail

## What this cell does NOT show

- It does NOT prove the substrate is a competitive LM in absolute terms
  (it's still well above bigram bound).
- It does NOT diagnose other possible leakage sources (e.g., text8 word
  frequency vs Google News word frequency; tokenization choice).
- It does NOT replace the WordSim353 / SimLex-999 external benchmark from
  clean_encoder_eval_harness_v1; that cell tested encoder semantic quality
  in isolation. This cell tests whether substrate-as-LM benefits from
  encoder semantic structure or substrate W does most of the work.
- The clean encoder is trained on text8 training split (no Google News);
  if the clean encoder is bad on text8 itself, that's NOT a substrate
  finding -- it's a "you cant train a good encoder on 17M tokens in one
  pass" finding.

## Cites

- notes/research_*_top5_bias_encoder_leakage_*.md (master bias memory)
- experiments/exp_fair_harness_substrate_as_lm_v1.py (fair_harness 7.3065 provenance)
- experiments/exp_substrate_encoder_ablation_on_fair_harness_v1.py (sibling cell; methodology gap study)
- experiments/exp_clean_encoder_eval_harness_v1.py (sibling; WordSim353/SimLex encoder quality eval)
- preregs/2026-06-23_clean_encoder_eval_harness_v1.md (the clean-encoder discipline note)
- USER 2026-06-23: clean methodology -- external ground truth + name-leak-stripped baselines

## Expected timeline

- Smoke (laptop CPU): <90s (small grid, no clean-encoder training; reuse word2vec cache)
- Full (remote CPU): ~40-60min wall (clean-encoder Word2Vec training on text8 dominates ~10-15min;
  word2vec model load ~30s; rank-1 W build + joint sweep ~5-10min per arm; 4 arms).
- timeout = 5400s (90 min budget; ~1.5x estimate)
