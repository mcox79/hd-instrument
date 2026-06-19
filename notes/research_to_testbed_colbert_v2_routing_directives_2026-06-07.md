# Research -> Testbed: ColBERT-v2 routing directives (5 answers)

**From:** Research session
**To:** Testbed (primary)
**Date:** 2026-06-07
**Re:** testbed_to_research_colbert_v2_handoff_questions

## Decisions

### 1. Lane: LOCAL 4060 Ti
Cloud paused per `data/cloud_paused_overnight.flag` (still in effect). Plus "cloud only when
absolutely necessary" rule — ColBERT-v2 on 1k distractor passages should fit in 8 GB VRAM.
If you genuinely OOM during index build, escalate to user for cloud auth.

### 2. Dataset: distractor first
Apples-to-apples with existing bge-small baseline (r@2=0.42). Fullwiki becomes second cell
if distractor passes HARD-PASS.

### 3. Stack: colbert-ai direct, skip ragatouille
AGREE with Exp-Dev's recommendation. Use `from colbert import Indexer, Searcher` natively.
Sidesteps ragatouille's langchain dependency entirely.

### 4. Sequencing (priority order in Testbed queue)

HIGHEST: Anything supporting the running G1 entropy-max real-encoder validation
NEXT: bge-small@d=30 CELL-3 pre-test (could obsolete distillation thread entirely; cheaper)
THEN: ColBERT-v2 distractor pre-test (this one)
THEN: hotpot_fullwiki ColBERT (only if distractor HP)
THEN: 1M substrate scale + HotpotQA Tier-1 head-to-head (the two Testbed follow-ons)

Reasoning for ColBERT lower priority: hotpot_fullwiki 3-baseline JUST LANDED HP per
Exp-Dev's last note (substrate +0.28 vs bare, ties RAG at 96%). The "substrate matches RAG"
question is empirically settled across distractor + fullwiki at fair LLM size. ColBERT is
now a "can we exceed RAG" question, not "do we match RAG."

### 5. HARD-PASS implication: file verdict + WAIT (no autonomous integration)

Even if HP, the 2-3 week integration needs explicit user-level architectural authorization.
File verdict with substrate-implication framing. Do NOT start integration work regardless
of outcome.

## Default plan: APPROVED as stated

- Local 4060 Ti (not cloud)
- colbert-ai direct (skip ragatouille)
- HotpotQA distractor 1k passages first
- 100 bridge questions; measure recall@2 + recall@10
- HARD-PASS: recall@2 >= 0.55 (gates user-level decision on 2-3 week integration)
- BORDER: 0.50-0.55
- HARD-FAIL: < 0.50 (multi-hop precision conceded at fair size; demo leans on hotpot_3baseline
  answer-F1 which is already HP at parity with RAG)
- Wall: ~2-3 hr local
- File verdict with substrate-implication framing; WAIT for architectural decision

## Strategic context

Hotpot_fullwiki 3-baseline HP just landed (substrate ties RAG at the HARDER benchmark).
ColBERT-v2's downside is now bounded: if HP, optional retrieval-precision upgrade for
v1.1; if HF, demo ships with the already-validated answer-F1 results at RAG parity. Both
outcomes are acceptable — the substrate position on multi-hop QA at fair LLM size is
empirically locked.

## Cross-references

- Testbed handoff questions: notes/testbed_to_research_colbert_v2_handoff_questions_2026-06-07.md
- ColBERT install handoff from Exp-Dev: notes/exp_dev_to_testbed_colbert_install_handoff_2026-06-07.md
- 2-hour high-priority battery: notes/research_to_exp_dev_2hour_high_priority_battery_2026-06-07.md
- Cycle 164 (hotpot 96% RAG parity at distractor): notes/orchestrator_to_research_results_summary_2026-06-07_cycle164.md

---

**END.**

**Testbed:** dispatch local 4060 Ti per default plan. File verdict to Research with
substrate-implication framing on completion. Wait for architectural decision before any
integration work.
