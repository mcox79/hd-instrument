# Pre-registration: a1_substrate_intent_classifier_v1

**Date:** 2026-06-22
**Anchor:** a1_substrate_intent_classifier_v1
**Queue:** remote_cpu_queue
**N:** 2048, **Seeds:** 3, **N_TRAIN:** ~5000, **N_TEST:** 500

## Scientific question

Can a substrate-native Hebbian-bound intent classifier (char-trigram question HD x category HD) reliably categorize natural-language queries across 7 intent categories (LOOKUP, COMPARISON, MULTI_HOP, LIST, CHAIN, COUNT, DEFINITION) with no LLM teacher distillation, beating a majority-class baseline by 2x and a random baseline by 5x, at sub-10ms CPU latency? This is the substrate-native equivalent of the original A1 anchor (which required a Qwen-2.5-3B teacher; rescoped substrate-only per USER L1 directive ZERO-LLM).

## Pre-registered bands

**HARD-PASS:**
- SUBSTRATE_INTENT mean accuracy across 3 seeds >= 0.65 on held-out 500-query test set
- AND SUBSTRATE_INTENT mean accuracy >= 2.0 * MAJORITY_BASELINE mean accuracy
- AND SUBSTRATE_INTENT mean accuracy >= 5.0 * RANDOM_BASELINE mean accuracy
- AND per-query inference latency P95 < 10 ms on CPU
- AND n_llm_calls == 0 (substrate-only-decode gate)

**MIDDLE:** SUBSTRATE_INTENT accuracy in [0.50, 0.65) with the multiplicative discriminators holding (>=2x majority AND >=5x random).

**HARD-FAIL:** SUBSTRATE_INTENT mean accuracy <= MAJORITY_BASELINE mean accuracy OR n_llm_calls > 0 OR P95 latency >= 50 ms.

## Calibration rationale

Substrate Hebbian-bind char-trigram question HDs to category HDs is a known associative-memory primitive (cleanup-load-bearing meta-rule). Char-trigram encoder lacks deep semantic similarity (loses cat/kitten paraphrases) so absolute accuracy is bounded by surface lexical/structural signal: question-word distribution (who/what/where/how/when/list/define/count/compare) carries most of the categorical information. A 0.65 bar is calibrated against:

- Random over 7 categories = 0.143; 5x bar = 0.715 -- but bar applied to RANDOM_BASELINE not absolute (so HP requires substrate >= 5x random which means random ~ 0.13 -> substrate >= 0.65).
- Majority class (LOOKUP/MULTI_HOP biggest) ~ 0.30-0.35; 2x bar -> substrate >= 0.65.
- Char-trigram literal-keyword overlap should easily catch LIST ("list", "name three"), COUNT ("how many"), DEFINITION ("what is", "define"), COMPARISON ("which is"); MULTI_HOP and BRIDGE harder. 0.65 is a discriminating-regime bar.

The labeled set is synthesized from:
- HotpotQA dev "type" field (bridge -> MULTI_HOP, comparison -> COMPARISON)
- NQ-open ~lookup questions (most "who/what/when" single-fact)
- Template-generated examples for LIST/COUNT/DEFINITION/CHAIN (~700 each)

If the bar trips MID, the read is "substrate carries categorical signal but bag-of-trigrams loses paraphrase variance"; if HF, the read is "char-trigram surface signal insufficient -- requires deeper encoder (n11 random-indexing semantic or whitening)."

## Substrate-only-decode gate

`n_llm_calls` counter asserted == 0 at exit. Char-trigram encoder is deterministic substrate primitive (no transformer, no external model). Category-HD bound via direct Hebbian outer product (W += sum_q outer(category_hd[label_q], question_hd[q]) / N). Inference: argmax over (E_cat @ W @ q_hd).

## N-suffix section

No _n<N> suffix in anchor name (this cell is not a vector-dim sweep; N_DIM is fixed at 2048 chosen for char-trigram bag bandwidth + sub-10ms CPU matmul. The DIM is a configuration choice, not a binding contract).

## Timeout estimate

Smoke wall: ~30-60s at N_TRAIN=200, N_TEST=50, 1 seed.
FULL: N_TRAIN=~5000, N_TEST=500, 3 seeds.
formula: ceil(1.5 * 60 * (5000/200)^1.0 * (3/1)) = ceil(1.5 * 60 * 25 * 3) = 6750s.

The per-question Hebbian-bind and per-question inference are O(N_DIM) vector ops; total wall is dominated by encoding (~5000 + 500 calls * ~0.5ms each = ~3s per seed) and the Hebbian outer-product accumulation (single matmul ~ N_train x N_DIM = 5000 * 2048 floats = ~40MB; sub-second). Realistic FULL wall: 5-15 min total. Setting timeout = 2400s (40 min) for safety margin.

timeout_s = 2400
