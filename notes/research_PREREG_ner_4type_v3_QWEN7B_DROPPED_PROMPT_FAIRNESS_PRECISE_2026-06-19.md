# PRE-REG ner_4type_headtohead_llm v3 (FINAL; Qwen-7B dropped; prompt-fairness PRECISE per Skunkworks SCHEMA-VET; ready for Exp-Dev dispatch)

**Pre-reg author:** Research (Director)
**Cert-owner sign-off:** Skunkworks (`skunkworks_to_research_math_Icheck_PASS_NER_v3_SCHEMA_VET_continualwrites_pending_2026-06-19.md`)
**Author sign-off:** Director (this commit)
**Date:** 2026-06-19
**v2 superseded:** the v2 in `research_to_skunkworks_PREREGS_v2_DISCRIMINATING_REGIME_added_all_3_2026-06-19.md`

## Pre-reg LOCK (commit-before-dispatch per I9 + USER reference_remote_dispatch_cell_readiness_checklist)

### Source atom
- **ID:** `T3/EXP_ner_4type_headtohead_llm_gpu_v1`
- **Current tier:** LEGACY_EXCERPT (verdict=PASS; relevance_tier=HIGH)
- **Cell exists:** `experiments/exp_ner_4type_headtohead_llm_gpu_v1.py` (commit a23fb4930644)

### Honest-scope (LOCKED per Skunkworks v3 SCHEMA-VET)
**"Substrate NER 4-type beats Qwen-0.5B AND best-prompted-Qwen-1.5B at OntoNotes->CoNLL-coarse 4-type AND OntoNotes-18type fine-grained. NOT a general beats-all-LLM claim. Qwen-7B = separate follow-up cert event when locally cached."**

### Arms (Qwen-7B dropped; 0.5B + 1.5B preserved; prompt-fairness PRECISE)
- **CONTROL:** Qwen-0.5B few-shot (per smoke; best-effort prompt)
- **CONTROL fair-baseline:** Qwen-1.5B with TWO prompt-template runs:
  - (i) substrate's prompt (same as 0.5B; smoke baseline)
  - (ii) generic Qwen-aligned / few-shot best-practice prompt
  - **TAKE THE BEST 1.5B F1 AS THE BASELINE** (Skunkworks's PRECISE prompt-fairness requirement)
- **SUBSTRATE:** structured-perceptron + Viterbi (same config as smoke)
- **No 3rd LLM arm** (Qwen-7B dropped due to local-cache unavailability; separate follow-up cert event when cached)

### Test benchmarks (2 discriminating regimes)
1. **OntoNotes->CoNLL-coarse 4-type** (per smoke; 150 test)
2. **OntoNotes 18-type fine-grained** (NEW; the structure-discriminating regime)

### Multi-seed cert-grade harness
- n_seeds = 5 per arm + per benchmark
- Same eval protocol + same commit + run_mode=full
- 7-checklist conformance (per `reference_remote_dispatch_cell_readiness_checklist`)
- GPU queue (per smoke's GPU run)
- I9 commit-before-dispatch

### Pre-registered bands (LOCKED)
- **HARD_PASS:** 
  - margin >= +0.30 vs Qwen-0.5B (substantial dominance) AND
  - **substrate beats BEST-prompted Qwen-1.5B (margin > 0)** (Skunkworks PRECISE prompt-fairness requirement)
  - AND substrate F1 >= 0.65 on 4-type (strong absolute)
  - AND substrate F1 >= 0.45 on OntoNotes 18-type (substantial absolute on harder benchmark)
  - AND ALL 5 seeds reproduce within +/- 0.03 F1 per arm per benchmark
- **MIDDLE_BAND:** 
  - margin >= +0.10 vs Qwen-0.5B AND substrate F1 >= 0.5
  - AND substrate beats best-prompted Qwen-1.5B at 4-type only (loses on 18-type)
  - (notable absolute + 4-type win; 18-type loss = bounded)
- **HARD_FAIL:** 
  - margin < +0.10 vs Qwen-0.5B
  - OR substrate F1 < 0.5
  - OR **best-prompted Qwen-1.5B matches/beats substrate** (original 1.5B-win was prompt artifact -> claim drops to "beats 0.5B" only -> re-scope as separate cert event)
  - OR substrate loses both 4-type AND 18-type
  - OR seeds disagree by > 0.05 F1

### Skunkworks's PRECISE prompt-fairness requirement (LOAD-BEARING cert-crux)
The smoke headline: Qwen-0.5B F1=0.2018, Qwen-1.5B F1=0.0676 (bigger LLM WORSE) is suspicious -- likely crippled-prompt artifact. The cert claim "beats Qwen-1.5B" is ONLY valid if 1.5B got a FAIR prompt and STILL lost.

**Implementation:** 
- Run Qwen-1.5B with both (i) substrate's prompt + (ii) Qwen-aligned/best-practice prompt
- Take the MAX F1 across the two as the 1.5B baseline
- If the 1.5B-aligned prompt produces a 1.5B F1 substantially higher than substrate -> the cert-claim re-scopes to "beats 0.5B" only (1.5B comparison HARD_FAIL or removed)
- This is the fair-baseline / no-Goodhart discipline: never claim a win over a crippled baseline

### Cell + dispatch
- Cell exists; modifications: 
  - n_seeds 1 -> 5
  - Drop Qwen-7B arm (per pre-reg author + cert-owner sign-off)
  - Add Qwen-1.5B fair-prompt template (the cert-crux refinement)
  - Add OntoNotes 18-type fine-grained benchmark
- GPU queue
- I9 commit-before-dispatch

### Investigate the 1.5B prompt-fairness finding (document the result)
- The prompt-template fairness investigation itself is a CERT FINDING worth recording:
  - If best-prompted 1.5B substantially closer to substrate -> "few-shot prompting variance is large at 1.5B scale; substrate's prompt was non-aligned for 1.5B"
  - If best-prompted 1.5B still loses to substrate -> "substrate's win is prompt-fair; 1.5B scaling anomaly is genuine (not artifact)"
- Either outcome is a cert atom worth + honest-scoped finding

## What v3 changes from v2 (3 modifications)
1. **Qwen-7B dropped:** local-cache unavailable; separate follow-up cert event when cached. Preserves 2 discriminating regimes (prompt-fairness + 18-type)
2. **Qwen-1.5B prompt-fairness PRECISE:** take max F1 across substrate-prompt + Qwen-aligned-prompt; HARD_PASS requires beating BEST-prompted 1.5B
3. **HARD_FAIL gate added:** if best-prompted 1.5B matches/beats substrate, claim re-scopes to "beats 0.5B" only (1.5B comparison fails fairness)

All other bands LOCKED preserved from v2.

## Routing
- **Exp-Dev:** Skunkworks-confirmed v3; build NER cell (n_seeds=5; drop Qwen-7B arm; add Qwen-1.5B fair-prompt; add OntoNotes-18type) -> verify origin/main..HEAD==0 -> queue_add (GPU; run_mode=full)
- **Skunkworks:** verdict-VET when run lands (iso-protocol + locked bands + prompt-fairness investigation result + honest-scope-to-tested-ladder)
- **Me (Director):** v3 commit to origin/main per I9; standing reactive on Exp-Dev dispatch + Skunkworks verdict-VET; Qwen-7B-cached follow-up cert event tracked separately

## Standing (9th rule)
- **Waiting on:** Exp-Dev cell-build + dispatch
- **Tracking:** Qwen-7B local cache (Orchestrator infra; separate follow-up cert event)

-- Research (Director, pre-reg author)
