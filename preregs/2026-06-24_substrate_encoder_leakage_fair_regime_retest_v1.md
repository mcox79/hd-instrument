# Pre-reg: substrate_encoder_leakage_fair_regime_retest_v1

Date filed: 2026-06-24
Filed-by: exp_dev
Trigger: Research encoder-leakage 2x+3x revival drill -- ANCHOR 1
Cell: experiments/exp_substrate_encoder_leakage_fair_regime_retest_v1.py

## Why (revival drill -- v1 verdict may be artifact)

v1 (substrate_clean_encoder_substrate_as_LM_v1, landed 2026-06-24) returned
HARD_PASS_LEAKAGE_REAL with delta(B-A) = +0.4376 BPC. Research flagged the
verdict as potentially a MEASUREMENT-REGIME artifact, not a substrate property:

  (a) V=4000 forced unigram-floor pinning across all 4 arms.
      Evidence: top1 accuracy was 0.2151..0.2190 for ALL 4 arms (essentially
      identical); the +0.44 BPC delta was driven entirely by softmax T+lambda
      calibration in the lambda~0 regime (arm B's best_lambda=0.0 = PURE
      unigram backoff = the verdict was a unigram-floor comparison, NOT a
      substrate-W comparison).

  (b) Arm B (W2V trained on text8 only) ran 1.82s on 100k tokens. Standard
      text8 word2vec convergence requires the full ~17M-token corpus and
      5+ epochs (~10-30 min CPU). The 1.82s training was severely UNDER-
      CONVERGED vs the Google News 100B-token baseline; the 6000x training-
      data gap was the dominant confound.

P_deflated = 0.45 that the v1 HARD_PASS_LEAKAGE_REAL verdict gets REFUTED
on this fair re-test. If REFUTED, today's framing ("substrate-as-LM is mostly
word2vec leakage") reverses. If CONFIRMED, Path C substrate-owned encoder
becomes load-bearing.

## Arms (4 arms; 3 seeds [7, 13, 29]; pure numpy + gensim CPU; remote_cpu)

| Arm | Encoder | Training data | Role | Predicted bigram-BPC |
|-----|---------|---------------|------|----------------------|
| A_W2V_GOOGLE_NEWS_FAIR     | word2vec-google-news-300 | google_news_100B | rail (reproduces v1 arm A on V=20k bigram-cond) | varies |
| B_W2V_TEXT8_FULL_17M       | gensim Word2Vec | text8_full_~17M (epochs=5) | PRIMARY | varies |
| C_RANDOM_PROJECTION_FAIR   | Fixed Gaussian projection | none | floor | high (~uniform) |
| D_CHAR_TRIGRAM_FAIR        | Bag-of-char-trigrams bipolar sign | none (deterministic) | substrate-native floor | varies |

All arms use IDENTICAL sparse-bipolar projection at f=0.05, IDENTICAL rank-1
Hebbian W on N_TRAIN=100k token Hebbian substream, IDENTICAL joint
(T, lambda) sweep on dev half, IDENTICAL ctx-unk filter, IDENTICAL alpha=0.1
unigram + bigram baselines. The single varied knob is the ENCODER.

KEY FIX from v1: arm B's W2V is trained on the FULL ~17M-token text8 corpus
(separate from the Hebbian N_TRAIN substream) so that word2vec convergence
is fair vs google-news rail.

## Lane / discriminator (apples-to-apples)

- LANE_2 declared (intra-corpus substrate-vs-substrate ablation; encoder is
  the ONE varied dimension).
- INTRA_LANE_DELTA = ARM_B - ARM_A on bigram-conditional BPC (the
  load-bearing metric).
- CONFOUND_AUDIT (4 confounds named, controlled-or-acknowledged):
    1. Training-data-size: google-news ~100B vs text8 ~17M (~6000x less).
       Mitigation: 5 epochs over 17M is the STANDARD text8 W2V convergence
       bar; if arm B is still bad, that's an honest finding about text8 vs
       google-news for THIS scale of training.
    2. Vocab size: v1 V=4000 pinned all arms to unigram floor. v2 V=20000
       (5x larger) escapes that regime AND allows a non-trivial bigram floor.
    3. Temperature regime: v1 TEMP_GRID min was 0.01; v2 extends to 0.001
       to catch sharper softmax in the bigram-conditional regime.
    4. Metric choice: v1 used unigram-conditional BPC only; v2 reports BOTH
       bigram-conditional (PRIMARY per drill) and unigram-conditional
       (secondary; for v1 comparability).

## Pre-registered HARD bands (PRE-REGISTERED BEFORE RUN; do NOT adjust)

PRIMARY metric: bigram-conditional BPC (substrate lift over add-alpha word-
bigram backoff). PRIMARY arm = ARM_B_W2V_TEXT8_FULL_17M.

### HARD_PASS_LEAKAGE_REFUTED
- |delta_bi(B - A)| < 0.10 BPC AND arm B beats unigram floor by >= 0.50 BPC
- Interpretation: v1 verdict REFUTED. The +0.44 was a V=4000 +
  under-trained-B artifact. Substrate capability is robust to encoder
  choice in the fair regime. word2vec lift was a calibration effect at
  small V, not a leakage effect.
- Action: revise today's framing ("substrate-as-LM is mostly word2vec
  leakage") -- substrate W IS doing load-bearing work.

### HARD_PASS_LEAKAGE_CONFIRMED
- delta_bi(B - A) >= 0.30 BPC AND arm B beats unigram floor by < 0.20 BPC
- Interpretation: v1 verdict CONFIRMED on fair regime. Properly-converged
  clean encoder is still much worse than google-news; word2vec's
  pretrained Google-News knowledge IS load-bearing for substrate-as-LM.
- Action: Path C (substrate-owned encoder via predictive coding) becomes
  the load-bearing program direction per project memory.

### MIDDLE_BAND
- delta_bi(B - A) in [0.10, 0.30) on bigram-conditional metric
- Interpretation: partial leakage; smaller than v1's +0.44 estimate.
- Action: report magnitude; route to Research for decision on Path C
  priority vs continued use of google-news as input encoder.

### HARD_FAIL_REGIME
- All 4 arms cluster within 0.10 BPC on bigram-conditional metric at V=20k
- Interpretation: measurement regime STILL not discriminating across
  encoders. V=20k was insufficient (which would itself be a finding).
- Action: ANCHOR 3 calibration cell (different V / different metric /
  scale baseline) needed before any encoder-leakage claim is interpretable.

### HARD_FAIL_PROVENANCE
- Arm A cross-seed std > 0.10 BPC on bigram-conditional metric, OR
- Arm B convergence sentinel FAILS (training_wall_s < 60s on full corpus =
  did not actually train).
- Interpretation: cell methodology unstable / bug.
- Action: halt and inspect cell; do not propagate verdict.

## Config (FULL run)

- N_DIM = 8192
- N_TRAIN = 100_000 tokens (Hebbian substream)
- N_HELD = 20_000 tokens
- VOCAB_CAP = 20_000 (5x v1; per drill ANCHOR 1)
- W2V_TRAIN_TOKEN_BUDGET = 17_000_000 (FULL text8 for arm B W2V)
- text8 corpus (data/text8_cache/text8.txt; 100MB / ~17M tokens)
- TEMP_GRID = [0.001, 0.003, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
  (extended down to 0.001 per drill fix)
- LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
- MRR_K = 10
- seeds = [7, 13, 29] (3 seeds for cross-seed CV check on arm A)
- Sparse-bipolar f=0.05 on ALL arms (matched primitives)
- Rank-1 Hebbian W; joint (T, lambda) sweep on dev half; report on test half
- Clean-encoder Word2Vec config: dim=300, window=5, min_count=5, epochs=5
  (full 17M corpus = standard text8 W2V convergence bar)
- Bigram floor: add-alpha=0.1 dense V=20k x V=20k table (~1.6 GB float32;
  tractable on remote_cpu with 32GB+ RAM); backoff_lambda=0.3 to unigram
- Routing: remote_cpu_queue (pure numpy + gensim CPU; PROT-020)
- Timeout: 10800s (3 hr; per drill estimate ~2hr w/ 50% headroom)

## Critical disciplines

- Apples-to-apples lane 2 declared (encoder is the ONE varied knob)
- Single PRIMARY metric: bigram-conditional BPC
- Secondary: unigram-conditional BPC (for v1 comparability)
- Pre-reg PRIMARY arm declared: ARM_B_W2V_TEXT8_FULL_17M
- Pre-reg PRIMARY rail declared: ARM_A_W2V_GOOGLE_NEWS_FAIR
- Fix #14: ONE cell
- Fix #28: per-arm metrics ONLY; no cross-arm framing in verdict_msg
- Fix #26: predispatch_check passed (PROCEED, 0 prior landings)
- A5: path-scoped commit
- ASCII-only, no emojis, no em dashes
- PROT-018: no _nN suffix
- PROT-020: pure numpy -> remote_cpu_queue
- Substrate-only-decode gate asserted (zero LLM forward calls; word2vec is
  static open-weight lookup, not a forward LLM call)
- Convergence sentinel: arm B training_wall_s >= 60s OR auto-HARD_FAIL_PROVENANCE
- WHAT_THIS_DOES_NOT_SHOW clause in detail

## What this cell does NOT show

- It does NOT prove the substrate is a competitive LM in absolute terms.
- It does NOT eliminate ALL leakage sources (word frequency drift between
  google-news and text8 still applies even with fair training).
- It does NOT replace WordSim353/SimLex external encoder benchmarks. This
  cell tests substrate-as-LM behavior; encoder semantic quality in isolation
  is a different test.
- The bigram-conditional metric is substrate's lift OVER a proper add-alpha
  word-bigram backoff with unigram fallback. It is NOT compared to a tuned
  KN-smoothed bigram or n-gram LM. If arm B still fails to beat the unigram
  floor, that's informative about clean-encoder + small-Hebbian capacity,
  NOT a regime failure.
- It does NOT diagnose whether Path C predictive-coding encoder would
  succeed; the LEAKAGE_CONFIRMED verdict only makes that direction load-
  bearing as a hypothesis, not validated.

## Cites

- Today's USER drill spec: substrate_encoder_leakage_fair_regime_retest_v1
  ANCHOR 1 (encoder-leakage 2x+3x revival drill)
- preregs/2026-06-24_substrate_clean_encoder_substrate_as_LM_v1.md (v1 base)
- experiments/exp_substrate_clean_encoder_substrate_as_LM_v1.py (v1 cell;
  data/exp_substrate_clean_encoder_substrate_as_LM_v1/metrics.json has the
  HARD_PASS_LEAKAGE_REAL delta=+0.4376 result being retested)
- experiments/exp_substrate_brain_word_level_prediction_v2_production_config.py
  (bigram-floor implementation pattern source)
- project_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23.md
- feedback_brain_is_existence_proof_higher_prior_for_brain_grounded_mechanisms_USER_2026-06-23.md
- feedback_clean_encoder_tests_no_contamination_USER_2026-06-23.md

## Expected timeline

- Smoke (laptop CPU): <120s (small grid, no full w2v training)
- Full (remote CPU): ~90-150min wall per seed (W2V full-text8 training
  ~15-30min per seed dominates; bigram floor build + 4-arm sweep ~10-20min).
  3 seeds total ~ 5-7hr wall but seeds run serially.
- timeout = 10800s (3hr) per the user spec; if a single seed exceeds this,
  the atexit synthesizer will write a TIMEOUT_PARTIAL_NSEEDS metrics.json
  from whatever seed-partials completed.

## Routing decision

- Pure numpy + gensim CPU + V=20k bigram (1.6 GB dense): remote_cpu_queue.
- No torch -> PROT-020 blocks GPU routing.
- Local laptop CPU could run this but would tie up the laptop for 5-7hr;
  remote_cpu is the right place.
