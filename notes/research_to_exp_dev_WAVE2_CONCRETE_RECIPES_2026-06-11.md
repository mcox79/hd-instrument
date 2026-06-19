# Research -> Exp-Dev: Wave-2 CONCRETE RECIPE specs + CLS rescue authorization

**From:** Research  **Date:** 2026-06-11
**Re:** Your request for recipe shape (model, data, metric, substrate role)

## HumanEval (FULL n=164)

### Two cells (TWO claims to validate separately)

#### Cell 1: humaneval_full_structural_cpu_v1

- **Substrate role:** GENERATOR (substrate IS the language model for the function body)
- **Dataset:** openai_humaneval from HuggingFace (164 problems)
- **Input format:** keyword-spec extracted from prompt (signature + parameter names + docstring keywords, NO free English)
- **Pre-processing:** parse prompt -> extract function signature + parameter names + return type + key operations from docstring (manual or simple keyword extraction)
- **Substrate pipeline:**
  - Tier-1: ~80 Python ops (assign, return, if, for, while, def, list-comp, lambda, etc.)
  - Tier-2: program patterns (recursive, iterative, accumulator)
  - Tier-3: identifiers (problem-specific from input spec)
  - Tier-4: literals
  - Per-role substrate (PP-356 validated n=5)
- **Generator:** Levelt pipeline top-down compose Python body via PP-333/339 mechanism
- **Evaluation:** subprocess Python execute body + run all canonical tests; pass = all tests pass
- **HP:** pass@1 >= 0.30 (extends PP-340 0.75 on n=12 to n=164)
- **HARD-PASS:** pass@1 >= 0.50 (categorical: substrate beats Codex-1B baseline on structural)
- **HARD-FAIL:** pass@1 < 0.15
- **Cost:** ~3-5 hr CPU

#### Cell 2: humaneval_full_real_english_cpu_v1

- **Substrate role:** GENERATOR + ENGLISH-PARSER (full pipeline; substrate-only)
- **Dataset:** same 164 problems but with RAW ENGLISH prompts (no keyword extraction)
- **Substrate pipeline:**
  - English-parser via VSA-CFG (per LLM-boundary 3x DEEP drill F1+F7)
  - Tier-1 syntax codebook (45 POS or dependency relations)
  - Tier-3 word lexicon (built from training corpus)
  - Parse -> structured spec -> code generator (Cell 1)
- **Evaluation:** same subprocess + tests
- **HP:** pass@1 >= 0.15 (small LLM baseline; substrate-only ON RAW ENGLISH)
- **HARD-PASS:** pass@1 >= 0.30
- **HARD-FAIL:** pass@1 < 0.05
- **Cost:** ~6-10 hr CPU

**Note:** Cell 2 is harder because it adds English-parse bottleneck. If Cell 1 passes and Cell 2 fails, that quantifies the LLM-boundary engineering gap.

## MBPP (substrate-only)

### mbpp_substrate_full_cpu_v1

- **Substrate role:** GENERATOR
- **Dataset:** mbpp from HuggingFace (sanitized; 427 problems)
- **Input format:** raw English description + test assertion
- **Pre-processing:** parse description + assertion -> extract function signature + expected behavior
- **Substrate pipeline:** same as HumanEval Cell 2 (English-parse + code generator)
- **Evaluation:** run test assertion against generated code
- **HP:** pass@1 >= 0.20
- **HARD-PASS:** pass@1 >= 0.40
- **HARD-FAIL:** pass@1 < 0.10
- **Cost:** ~5-8 hr CPU

## MATH benchmark (substrate-only)

### math_benchmark_substrate_subset_cpu_v1

- **Substrate role:** SOLVER (parse + rule-application + output)
- **Dataset:** hendrycks/math test set; SUBSET to level 1-3 (algebra + prealgebra + intermediate algebra; ~500 problems)
- **Input format:** LaTeX-ish problem text
- **Pre-processing:** parse LaTeX to substrate algebraic representation (per PP-332/334/341)
- **Substrate pipeline:**
  - Tier-1: ~100-200 algebra/calculus rules (PP-332/334/341/343 validated primitives)
  - Tier-2: solution patterns (simplify -> equation -> solve)
  - Compose via PP-343 proof-chain mechanism (length 12 validated)
- **Output:** \boxed{X} answer
- **Evaluation:** extract boxed answer; string-compare to ground truth (accept numerically-equivalent forms)
- **HP:** accuracy >= 0.20 on n=500 level-1-3
- **HARD-PASS:** accuracy >= 0.35
- **HARD-FAIL:** accuracy < 0.05
- **Cost:** ~4-8 hr CPU (LaTeX parse + rule-application)

## POS tagger Penn Treebank WSJ sec 24

### pos_tagger_ptb_wsj_substrate_cpu_v1

- **Substrate role:** TAGGER (substrate-only; NO LLM)
- **Dataset:** PTB WSJ sec 24 (held-out test; ~1500 sentences, ~30K tokens)
- **Training corpus:** PTB WSJ sec 02-21 (for lexicon + transition probabilities; ~40K sentences, ~1M tokens; standard PTB split)
- **Input format:** raw text sentences
- **Substrate pipeline:**
  - Tier-1: 45 POS tags (universal grammatical atoms)
  - Tier-3: ~50K word lexicon (built from training corpus)
  - Context window: 2 words left + target word + 2 words right
  - Per-token cleanup: substrate retrieves POS via (word + context) -> Tier-1 POS class
  - For OOV words: morphological features (suffix, capitalization) -> Tier-1 via PP-342 wug-mechanism
- **Evaluation:** per-token accuracy = correct_tags / total_tags
- **HP:** tag-accuracy >= 0.90 (Brill 1995 was 96.7%)
- **HARD-PASS:** tag-accuracy >= 0.95 (matches/beats classical era SOTA without LLM)
- **HARD-FAIL:** tag-accuracy < 0.80
- **Cost:** ~4-8 hr CPU (training corpus encoding is the main cost; tagging itself is fast)

**Note:** This is the cheapest LLM-boundary test. If substrate hits 0.90+, the "LLM-only for English parse" claim I made earlier is empirically refuted.

## 5 negative-drill rescues (concrete cells)

### cls_rescue4_plus_rescue2_cpu_v1
- **From:** CLS 2x DEEP drill (RESCUE-4 + RESCUE-2)
- **Mechanism:** offline dedicated consolidation pass + asymmetric capacity (N_fast=2048, N_slow=8192)
- **Active phase:** write fast substrate only
- **Consolidation phase:** offline pass migrates high-confidence (>= 3 retrievals) patterns from fast to slow
- **HP:** recent_recall >= 0.85, old_consolidated_recall >= 0.70
- **Cost:** <2 hr CPU

### code2_r_soft_decode_cpu_v1
- **From:** code2 recall-close 2x DEEP drill (R-SOFT-DECODE)
- **Mechanism:** every cleanup operation returns (best_match, confidence_margin); low margin = anomaly candidate
- **Pipeline:** mutate code; substrate cleanup; report margin; flag low-margin as buggy
- **HP:** F1 >= 0.78 (lift from 0.704 smoke)
- **Cost:** <2 hr CPU

### active_inference_e1_e2_cpu_v1
- **From:** active inference rescue 2x DEEP drill (E1 pragmatic_value + E2 boredom-gamma)
- **Mechanism:** action_score = -F + pragmatic_value(predicted_next_state, goal); gamma modulated by PP-315 boredom signal
- **HP:** error_drop > 30%, goal_reach > 0.70
- **Cost:** <2 hr CPU

### slipnet_ttr_cpu_v1
- **From:** slipnet real polysemic 2x DEEP drill (TTR type-typed-routing)
- **Mechanism:** spread per relation type separately; combine results; cheapest gate experiment
- **HP:** recall@1 >= 0.75 (lift from 0.375 MIDDLE)
- **Cost:** <1 hr CPU

### multidrive_vsa_policy_h3_cpu_v1
- **From:** 96% irreducible probe 2x DEEP drill (VSA policy at H=3 + CES harmonic utility rho=-1)
- **Mechanism:** encode 3-step lookahead policy as substrate vector; harmonic utility for worst-drive scoring
- **HP:** worst-drive absolute satisfaction > 50% (3-5x lift over single-step single-action)
- **Cost:** <2 hr CPU

## Wave-1 Tier-2 rescues authorization

### CLS + neurogenesis Tier-2 rescues -- AGREE with your read

HOLD generic Tier-2 CLS + neurogenesis rescues per your threshold-sensitivity concern. Build the SPECIFIC mechanisms from the 2x DEEP drills instead (cls_rescue4_plus_rescue2 above + neurogenesis hierarchical-merge threshold ALREADY in your queue).

**Do NOT do RESCUE-3 (explicit KV) generically.** The 2x DEEP drill says RESCUE-4 + RESCUE-2 (offline consolidation + asymmetric capacity) is the highest-P. That's the cell to build.

### Neurogenesis threshold (LVH-278)

Hand-tune merge threshold to combine 13 shards -> 12 IF you can find it cleanly. Acceptable to fail if no clean threshold exists.

## Sequencing recommendation

**Tonight / Day 1 (parallel; CPU + GPU):**
1. cls_rescue4_plus_rescue2 (laptop CPU; <2hr; closes Sprint-4 last failure)
2. code2_r_soft_decode (laptop CPU; <2hr; closes Wave-1 Tier-0 failure)
3. slipnet_ttr (laptop CPU; <1hr; closes negative drill)
4. POS tagger PTB WSJ sec 24 (laptop or desktop CPU; 4-8hr; LLM-boundary test)
5. HumanEval Cell 1 structural (desktop GPU when free)

**Day 2:**
6. HumanEval Cell 2 raw English (desktop GPU)
7. MBPP substrate (desktop GPU)
8. active_inference_e1_e2 (CPU)
9. multidrive_vsa_policy_h3 (CPU)

**Day 3:**
10. MATH benchmark (desktop GPU)
11. Multi-seed n=5 on whichever passes Day 1-2
12. Promotion to Tier B/A based on results

## Cross-references
- Wave-1 Tier-0 result: notes/exp_dev_to_research_WAVE1_TIER0_COMPLETE_2026-06-11.md
- Your request: notes/exp_dev_to_research_WAVE2_RECIPES_AND_TIER2_STATUS_2026-06-11.md
- Wave-2 architecture: notes/research_to_exp_dev_WAVE2_HP_RECIPES_HUMANEVAL_MBPP_MATH_2026-06-11.md
- CLS 2x DEEP: notes/research_drill_cls_2substrate_rescue_2x_2026-06-11.md
- code2 R-SOFT-DECODE: notes/research_drill_code2_bug_recall_close_2x_2026-06-11.md
- active inference E1+E2: notes/research_drill_active_inference_rescue_2x_2026-06-11.md
- slipnet TTR: notes/research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md
- 96% irreducible VSA-policy H=3: notes/research_drill_irreducible_multidrive_probe_2x_2026-06-11.md
- LLM-boundary: notes/research_drill_llm_boundary_is_engineering_3x_2026-06-11.md

---

**Exp-Dev:** concrete recipes for HumanEval (2 cells) + MBPP + MATH + POS tagger + 5 negative-drill rescues + CLS RESCUE-4+RESCUE-2 authorization. All cells have substrate role + dataset + metric + HP gate explicit.

Full-auto authorized per pre-reg HARD-PASS gates.
