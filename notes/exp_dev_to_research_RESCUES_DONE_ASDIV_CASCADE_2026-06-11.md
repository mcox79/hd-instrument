# Exp-Dev -> Research: RESCUE-1 + RESCUE-2 DONE; ASDiv cascade 0.300 (MIDDLE); head-to-head deferred to GPU

## RESCUE-1 (dep-parse corpus) DONE
Bundled UD-English-EWT inline: experiments/data/ud_english_ewt/ (dev 2001 + test 2077 full, train 5000-sample) + _ud_loader.py
(tokens+heads+deprels). Resolves the 2-cycle dep-parser UNKNOWN corpus blocker. Dep-parser + pos_oov now runnable on the runner.

## RESCUE-2 (CODE Tier A ingestion) DONE
Root cause: my CODE cells used runtime load_dataset("mbpp") -> fails on runner (no network) -> "UNKNOWN load_failed". Bundled
MBPP inline (experiments/data/mbpp/*.json) + updated 3 CODE cells to load local. Re-verified: fulldata 0.750, multiseed 0.739
std 0.0128 (Tier A) reproduce with bundled data. Re-queued -> 10th Tier A code_algopattern should ingest now.
LESSON (filing): ALL my benchmark cells use runtime load_dataset -> bundle datasets inline for runner reproducibility.

## ASDiv cascade: MIDDLE 0.300 (authorized build)
Cascade (op-classifier gate + all-pairs extractive operand selection + plausibility verifier) = 0.300, vs first-2-numbers
baseline 0.255 and prior 0.224. The cascade LIFTS (distractor-robust selection helps) but below your 0.40 target. Gaps:
- ASDiv has MULTI-STEP problems (my cascade is single-op) -- adding 2-op composition would help.
- The operand-selector is a crude proximity heuristic (prefer later numbers); a LEARNED selector would do better.
Recommend: cascade v2 = single-op + multi-step heads + learned operand-selector + verifier. Building if you confirm priority.

## Head-to-head (north-star, your (d)): CPU-BLOCKED, deferred to GPU
Qwen2.5-0.5B-Instruct loads + generates fine STANDALONE on CPU, but the full head-to-head script SEGFAULTS at model load
(exit 139) under concurrent-job memory/OpenMP pressure (tried KMP_DUPLICATE_LIB_OK + torch-first import + reduced footprint).
The cell is ready (exp_headtohead_math_vs_llm_cpu_v1.py). Recommend running it on the GPU (home, stable LLM inference) -- needs
the 4 math datasets bundled (RESCUE pattern) for the runner. Will bundle + queue to GPU unless you prefer otherwise.

## Cross-ref
- ASDiv cascade: data/exp_asdiv_cascade_cpu_v1/metrics.json
- RESCUE bundles: experiments/data/{ud_english_ewt,mbpp,asdiv_validation.json}
