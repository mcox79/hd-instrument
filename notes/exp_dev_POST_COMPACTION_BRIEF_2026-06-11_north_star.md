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
- IN-FLIGHT: exp_sentiment_headtohead_calibrated_multiseed_gpu_v1 (5 substrate seeds vs deterministic calibrated-LLM) -- firms
  whether the NARROW SST-2 edge (0.767 vs 0.748) is a robust win or a within-noise match.
- MATH head-to-head remains the strongest/robust north-star result (clean number parsing, no calibration needed).

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
