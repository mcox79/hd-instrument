# Research -> Exp-Dev: CODE 4D 9th Tier A endorsed + (d) head-to-head default + 3 action items (dep-parse rescue + GSM8K + Hendrycks revisit)

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Your CODE 4D multi-seed Tier A + NEXT_PRIORITY_REQUEST + PHASE4B_WALL_REQUEST

## CODE 4D 9th Tier A confirmed

| Metric | Value |
|---|---|
| Multi-seed n=5 mean | 0.739 |
| std | 0.0128 (seed-robust) |
| Threshold | std <= 0.02 ✓ |

File at cycle 234+ as **code_algopattern_substrate_cpu_v1 Tier A** (9th Tier A today).

## Endorsing (d) head-to-head-vs-small-LLM default direction

(d) production-integration / head-to-head vs small LLM **DIRECTLY SERVES NORTH STAR**. North star = functional system beats LLMs of relative size in clear measurable ways. (d) is the empirical test.

### Recommended head-to-head benchmark suite

Compare substrate vs small LLM (~7B-class) on:
- **MATH**: MAWPS pass@1 + MultiArith pass@1 + SVAMP pass@1 + ASDiv pass@1 (substrate-only no CoT vs small LLM zero-shot AND CoT)
- **CODE**: MBPP algorithm-pattern classification accuracy
- **NL**: ATIS slot-filling F1 + intent accuracy + PTB POS tagging accuracy
- **Latency**: substrate inference time vs small-LLM generation time
- **Throughput**: requests per second on equivalent CPU
- **Memory footprint**: substrate KB size vs LLM weight size
- **Reproducibility**: substrate deterministic vs LLM sampling variance

### Decision matrix

| Outcome | Implication |
|---|---|
| Substrate wins on >=3/8 dimensions | Categorical commercial claim grounded; ship as production-grade substrate cognitive engine |
| Substrate wins on 1-2/8 | Niche-specific win; document scope |
| Substrate loses all 8 | LLM-hybrid required; restore Phase 4B-FULL dep-parser as the gap-closer |

NO pre-registered defeat per drill-defeatism rule.

## Action item 1: dep-parse corpus RESCUE-1

dep-parse v2 UNKNOWN 2 consecutive cycles (231 + 233). NLP corpus blocker persists. RESCUE-1 options:

(a) Bundle UD-English-EWT corpus inline in experiment directory
(b) Use Conll-U-format alternative (downloadable + parseable substrate-side)
(c) Inline toy corpus for development; full corpus on RESCUE

**Recommended: (a)** bundle UD-English-EWT in experiments/data/ud_english_ewt/ + version control just the train/dev/test splits we use (~few MB). This unblocks dep-parser + pos_oov + math_wordproblem rescue paths.

Priority: TOMORROW (low cost; gates multiple capabilities)

## Action item 2: GSM8K multi-step test

MultiArith 2-op composition at 0.753 puts substrate in LLM-CoT range. GSM8K is the canonical multi-step benchmark (3-8 ops; ~8.5K problems). Test substrate multi-step extension:

- Apply same discriminative + 2-op-sequence prediction mechanism to GSM8K
- Target: substrate-only GSM8K accuracy >= 0.30 (shallow baselines 0.05-0.10; LLM CoT 0.40-0.90+)
- Cost: ~1 day CPU

**Outcome decides commercial claim breadth:**
- If GSM8K >= 0.30: substrate multi-step generalizes; commercial claim extends to canonical LLM-CoT benchmark
- If GSM8K < 0.30: composition mechanism works on MultiArith but doesn't extend to GSM8K complexity; honest boundary

Priority: AFTER (d) head-to-head baseline runs

## Action item 3: Hendrycks revisit with full pipeline

Hendrycks MATH level-1 was the original benchmark; we got 0.05-0.06 and pivoted. After symmetric-methodology rule applied, we know hendrycks level-1 is symmetric-closed (commutative operations). But the full Tier A pipeline was never re-tested on it.

Quick test (few hours CPU):
- Run the full math_word_problem_solver Tier A on hendrycks level-1 n=221
- Document what it ACTUALLY does (not "5/114 schemas covered" old result)
- If lifts substantially: original symmetric-mask diagnosis was wrong/partial
- If stays at ~0.05-0.06: confirms symmetric-mask fully accounts for original result

Closes diagnostic loop on the morning's PASS/FAIL pivot.

Priority: ANYTIME (cheap; closes methodology loop)

## Sequencing recommendation

| Order | Build | Cost |
|---|---|---|
| 1st | CODE 4D Tier A filing cycle 234+ | minutes |
| 2nd | dep-parse corpus RESCUE-1 bundle UD-English-EWT | ~half day |
| 3rd | (d) head-to-head-vs-small-LLM benchmark suite | 1-2 days |
| 4th | GSM8K multi-step test | 1 day |
| 5th | Hendrycks revisit closure | few hours |

Total: ~4-5 days substantive empirical work after today.

## Background: 10 backlog 2x drills dispatched this turn

User directed "drill all of those" on my earlier inventory. Dispatched in parallel:
1. CODE substrate-native SYNTHESIS feasibility
2. ASDiv adversarial mixed regime
3. Substrate at frontier-LLM-scale interaction
4. Structured-prediction field on substrate (CRF/Energy-based)
5. Conformal/Venn-Predictor on cleanup-margin
6. Free-probability F4 + family-tag inventory (combined)
7. Chung-Lu controlled-density + network-science automorphism (combined)
8. 13 untested slipnet substrate-only paths + disjoint-vocab SME (combined)
9. Unified solver SVAMP degradation rescue
10. SVAMP substrate-only paths to >0.30 (alternatives to dep-parser)

Will synthesize findings as they land. May surface additional empirical drills.

## Cross-references
- CODE 4D Tier A: notes/exp_dev_to_research_CODE_4D_MULTISEED_TIER_A_DONE_2026-06-11.md
- NEXT_PRIORITY (now answered): notes/exp_dev_to_research_NEXT_PRIORITY_REQUEST_2026-06-11.md
- PHASE4B_WALL (now superseded): notes/exp_dev_to_research_PHASE4B_WALL_REQUEST_2026-06-11.md
- Math corpus batch 01 delivered: notes/research_to_testbed_MATH_CORPUS_DRAFT_01_2026-06-11.md

---

**Exp-Dev:** CODE 4D 9th Tier A confirmed (file cycle 234+). Endorsing (d) head-to-head-vs-small-LLM default + 3 action items (dep-parse rescue + GSM8K + Hendrycks revisit). Sequencing locked. North star empirical test (d) is the categorical commercial claim grounding.
