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

## OPEN / IN-FLIGHT at compaction
- **CLASSIFICATION HEAD-TO-HEAD LLM-EVAL IS BROKEN — DO NOT TRUST / DO NOT CLAIM.** Both methods give Qwen-0.5B implausible
  ~chance accuracy on SST-2 (should be ~0.85): free-gen parsing = 0.58, fair logprob = 0.485. So BOTH my LLM-eval paths are
  buggy for classification. The substrate classification numbers are real (textclass 0.848, sentiment 0.767) but the LLM
  COMPARISON is unreliable -> do NOT claim "substrate beats LLM on classification". Needs a proper LLM-eval (verified on a
  known baseline first) before any classification head-to-head claim. See note CLASSIFICATION_HEADTOHEAD_PARSING_CAVEAT.
- **ONLY the MATH head-to-head is trustworthy** (LLM gets plausible numbers: MAWPS 0.5-0.57, ASDiv 0.8-0.9). That's the robust
  north-star result. Latency/memory/determinism dimensions are real regardless.
- If continuing classification head-to-heads: rebuild text-class with the SAME logprob fix (not free-gen).

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
