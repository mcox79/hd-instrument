# EXP-DEV POST-COMPACTION BRIEF — 2026-06-11 (north-star session). READ FIRST.

## HEADLINE: the north-star is empirically WON + SCALE-INVARIANT
Substrate (tiny <100MB, ~ms, deterministic) vs Qwen2.5-Instruct on math word problems:
- vs 0.5B: substrate wins 3/4 | vs 1.5B: 2/4 | vs **3B (6x larger): 2/4**
- Substrate WINS MAWPS (0.806) + MultiArith (0.753) at EVERY size — structured-arithmetic advantage is SCALE-INVARIANT.
- LLMs only win SVAMP/ASDiv (comprehension-heavy), and only from 1.5B up.
- This is the ROBUST north-star result (number-parsing is clean). Memory saved: north_star_won_discriminative_weighting_universal_2026-06-11.

## DEEPEST FINDING: discriminative weighting is the UNIVERSAL lever
Substrate cleanup/count ops plateau (can't weight features); an averaged/structured perceptron breaks every plateau:
POS 0.951 (Tier A) | NER 0.58 | chunking PASS(>=0.85) | dep-parse 0.60->0.787 | math (Tier A) | code 0.739 (Tier A) | textclass 0.848.
"Substrate stores+composes; discriminative perceptron classifies+reasons; conformal/isotonic calibrates." No LLM.

## CAPABILITIES BANKED (11+ Tier-A this session; all committed/pushed)
POS-perceptron 0.951 (11th Tier A), math-multibench/multistep (Tier A), code-algopattern 0.739 (Tier A), intent 0.834,
slot-filling 0.871, schema 0.967, routing 0.967. Uncertainty: conformal coverage guarantee + isotonic ECE 0.233->0.044.
Boundaries (honest): code-synthesis 0.074 (ceiling), GSM8K 0.16/0.385, ASDiv cascade 0.30, dep-parse arc-factored ceiling 0.787, NER 0.58.

## RESOLVED 2026-06-11 (post-compaction): classification head-to-head eval was SURFACE-FORM BIAS, now FIXED
- The prior "eval is broken" caveat was WRONG about the cause and is now resolved. Root cause: naive zero-shot label-logprob
  has SURFACE-FORM BIAS (Holtzman 2021 / Zhao 2021) -- on SST-2 the model's content-free prior favors " negative" (-2.673) over
  " positive" (-4.975) by +2.3 nats regardless of the review, so naive argmax sits at ~chance (raw=0.485). FIX = CONTEXTUAL
  CALIBRATION / PMI: score(label) = logP(label|prompt) - logP(label|content-free), averaging content-free prompts ["","N/A","nothing"].
- RESULT (exp_sentiment_headtohead_calibrated_gpu_v1, full 400 test): calibration lifted Qwen-0.5B SST-2 from 0.485 -> 0.748
  (plausible). With that TRUSTWORTHY baseline: substrate 0.767 >= calibrated-LLM 0.748 = HARD_PASS. Substrate ~5000x faster +
  deterministic + tiny. Honest framing: NARROW match/edge (0.02), single seed, 400 test -- not a blowout.
- METHOD LESSON (reusable): any zero-shot LLM classification baseline MUST be calibrated (PMI/contextual) or it under-measures the
  LLM to ~chance. Build a SANITY GATE into every head-to-head: if calibrated-LLM is still implausible, emit UNKNOWN, no claim.
- GENERALIZES to 4-class (exp_textclass_headtohead_calibrated_gpu_v1, AG-News, full 400 test): substrate topic 0.848 >> calibrated-
  LLM 0.647 (naive 0.600) = HARD_PASS, DECISIVE +0.20 margin (way beyond seed-noise), ~3000x faster (0.00014s vs 0.428s/item).
- SO THE CALIBRATED CLASSIFICATION PICTURE (honest + favorable): a TINY TRAINED substrate classifier MATCHES a 0.5B zero-shot LLM
  on SST-2 sentiment (0.767~0.748) and DECISIVELY BEATS it on 4-class AG-News topic (0.848>>0.647), at a fraction of size/latency,
  deterministic. This is the relevant "beats LLMs of comparable size" comparison (trained-substrate vs zero-shot-0.5B; NOT vs a
  fine-tuned or large LLM -- state that scope honestly).
- SST-2 edge FIRMED as ROBUST WIN (exp_sentiment_headtohead_calibrated_multiseed_gpu_v1, 5 seeds): substrate mean 0.7765 std
  0.0085 (mean-std 0.7680, worst seed 0.7675) > calibrated-LLM 0.748 -- EVERY seed beats the LLM. Not within-noise. So BOTH
  classification tasks are clean substrate wins vs the calibrated 0.5B: sentiment robust-win, topic decisive-win.
- SCALE TEST vs Qwen-1.5B (exp_classification_headtohead_1p5b_calibrated_gpu_v1) -- HONEST BOUNDARY:
  - AG-News TOPIC: substrate 0.860 > calibrated-1.5B 0.670 -> substrate win is SCALE-INVARIANT (beats 0.5B AND 1.5B), same
    shape as math north-star. Topic = strong-lexical-feature task; bag-of-words excels, zero-shot LLM has no edge.
  - SST-2 SENTIMENT: substrate 0.750 < calibrated-1.5B 0.847 -> sentiment win is NOT scale-invariant; breaks at 1.5B. Sentiment
    needs negation/context understanding where the larger LLM overtakes. (Substrate still beats 0.5B on sentiment.)
  - METHOD note: at 1.5B surface-form bias nearly vanished (SST-2 raw 0.85 ~ cal 0.847) -- calibration matters most for SMALLEST models.
  - DEFENSIBLE CLAIM: tiny trained substrate beats zero-shot LLMs of comparable+larger size on TOPIC classification (scale-invariant
    through 1.5B) and on the smallest (0.5B) for sentiment; a 1.5B LLM's deeper understanding overtakes substrate on sentiment.
- FULL SCALE LADDER COMPLETE (calibrated classification head-to-head, substrate = tiny trained perceptron):
  | Task            | vs 0.5B | vs 1.5B | vs 3B  | Substrate |
  | AG-News topic   | 0.647   | 0.670   | 0.710  | 0.860 (WINS ALL -- scale-invariant) |
  | SST-2 sentiment | 0.748   | 0.847   | 0.863  | 0.750 (wins 0.5B only -- boundary)  |
  TOPIC classification win is SCALE-INVARIANT across 0.5B/1.5B/3B (mirrors the math north-star), ~3000x faster, deterministic.
  SENTIMENT is an honest boundary: substrate competitive only vs 0.5B; LLM's deeper understanding pulls away with scale.
  (Cosmetic: exp_classification_headtohead_3b verdict_msg has a leftover "1.5B-cal" label from the copied template; model field
  + numbers are genuinely 3B. Not re-run -- data correct.)
- MATH head-to-head remains the strongest/robust north-star result (clean number parsing, no calibration needed).

## FULL-AUTO STRETCH 2026-06-11 (post desktop-restart) -- substrate-product per Research rule 7
- MATH SCOPE CORRECTED (Research LVH-290/291): the STRONGER honest claim is 2/4 dimensions (MAWPS+MultiArith) substrate-WIN is
  SCALE-INVARIANT through 0.5B/1.5B/3B (NOT "3/4 won" which was 0.5B-margin-dependent). SVAMP+ASDiv loss = comprehension boundary.
- NER FEATURE PROGRAM COMPLETE (OntoNotes 18-type, baseline 0.5817): Path 1 hard-BIO decoder -0.012 (REFUTED -- learned soft
  transitions already encode BIO, decoder NOT the bottleneck); Path 2 in-corpus Brown clusters +0.011; Path 3 POS cascade +0.013;
  4-type CoNLL-equivalent 0.648 (= CoNLL-2003 0.65 target); single-type boundary 0.664 (detection ceiling). Feature levers each
  SMALL at full data (lexical features subsume them at scale; smoke lifts of +0.078 shrink to +0.013). Honest: substrate NER is
  MODERATE/feature-limited ~0.60-0.66; breaking ~0.66 needs EXTERNAL resources (embeddings/large-corpus clusters). Stacked
  clusters+POS cell running (best in-corpus number). Reported to Research (exp_dev_to_research_NER_PROGRAM_COMPLETE_ASDIV_ORACLE).
- ASDiv 3-op ORACLE (Research B+C): reachability ceiling 1-op 0.721 / 2-op 0.833 / 3-op 0.684 -- NOT monotonic in depth. The
  limiter is WORLD-KNOWLEDGE CONSTANTS (~28-32% need a number not in text: dozen->12, days/week->7, dogs->4 legs). ASDiv substrate
  boundary is COMPREHENSION/world-knowledge, NOT composition depth -- confirms the north-star ASDiv-loss is the comprehension
  boundary. (Constant-augmented oracle abandoned: too permissive, spurious 1.0.)
- POS-LLM head-to-head NEGATIVE (eval-fragility): a Qwen-1.5B CANNOT reliably emit token-aligned POS tags via few-shot generation
  (mismatch rate 0.87 v1 / 1.0 v2); sanity gate correctly returns UNKNOWN both ways. A fair POS head-to-head needs slow per-token
  logprob scoring -- not worth it (rule 7: substrate-quality-first). POS-LLM thread DROPPED. (Substrate POS itself = 0.95, strong.)
- PENDING RESEARCH (3 questions filed): (1) NER -- accept ~0.60-0.66 boundary or authorize external embeddings? (2) build
  T-3OP-RECURSE (world-knowledge-bounded 0.68 ceiling) or pivot to direction A SVAMP role-asymmetry? (3) adopt smoke-time invariant
  model_name==anchor_substring for head-to-head cells (same label bug hit my 3B classification verdict_msg).
- SVAMP space already heavily built (bipartite/richfeat/perceptron/solver cells exist) -- don't duplicate; await Research priority.

## OPERATIONAL LESSONS (critical)
1. RUNNER HAS NO NETWORK: all benchmark cells must BUNDLE datasets inline (load_dataset -> UNKNOWN on runner). Bundled under
   experiments/data/: ud_english_ewt, mbpp(+with_tests), ontonotes_ner, ptb_treebank_tagged, math_benchmarks_test, asdiv_validation,
   atis_intent/atis_full, ag_news, sst2. Use these, not load_dataset, in any cell meant for the runner.
2. numpy-imported-before-torch -> OpenMP SEGFAULT (exit 139) on this Windows CPU. In LLM cells: import torch FIRST, avoid
   `from datasets import` in the same process (use bundled JSON), set KMP_DUPLICATE_LIB_OK=TRUE.
3. RE-QUEUING existing anchors DEDUPES (no depth added). For queue depth use NEW anchor names.
4. Pure-Python Viterbi/arc-scoring is too slow at full data -> VECTORIZE Viterbi DP (numpy) + FEATURE HASHING (crc32->np array)
   for arc models. Precompute-all-arcs OOMs at 12k+ sentences; cap or recompute.
5. GPU queue = overnight_queue on marsh@home via ssh + powershell + `& C:/dev/hd-instrument/.venv/Scripts/python.exe tools/queue_add.py`
   with HDLAB_QUEUE_ADD_ON_REMOTE=1 (cmd shell fails on .venv paths; use PowerShell call operator). GPU cells need `import torch` (PROT-020).

## NEXT (if continuing)
- Get the fair sentiment result; rebuild text-class head-to-head with logprob too; report HONEST classification comparison.
- The genuine frontier = comprehension-heavy boundary (SVAMP/ASDiv where LLMs win) + code synthesis. These need a different
  mechanism than discriminative-classification (the substrate-LLM boundary).
- The high-INSIGHT space is largely covered; further task-type probes confirm the pattern (breadth/commercial-coverage, not new insight).
- User pattern this session: relentless "keep going / continue / don't stop"; wants lanes BUSY (queue new-anchor cells across both lanes).
