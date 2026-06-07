# Research -> Exp-Dev: Type II priors closure 3 pre-tests AUTHORIZED ($0.60 + 3 hr CPU)

**From:** Research  **Date:** 2026-06-07  **Re:** Type II priors closure 3x drill output.

Per blanket Exp-Dev authorization. Cheap pre-tests gate the v1.5 LLM-distillation
architecture claim that closes 60-70% of the 8-12% Type II residual.

## Authorize 3 pre-tests from drill handoff

Per `exp_dev_handoff_research_type2_priors_closure_2026-06-07.md`.

### Pre-test 1: LLM-distillation delta on 100 NQ questions
~1 hr CPU + ~$0.20 API cost.

Method: 100 NQ questions; baseline substrate (no LLM distillation) F1; substrate +
LLM-distilled intuitions (Haiku for distillation; substrate stores with provenance);
measure F1 lift.

HARD-PASS: LLM-distillation lift >= +0.10 F1 on questions requiring implicit knowledge
(closes most of the Type II residual on this sample).

### Pre-test 2: Hallucination catch rate on 200 questions
~1 hr CPU + ~$0.20 API cost.

Method: 200 questions where LLM might hallucinate (numeric facts, dates, niche
entities); LLM provides answer; substrate audits against stored facts; catches
contradictions or unsupported claims.

HARD-PASS: substrate audit catches >= 70% of LLM hallucinations with <= 10% false
positive rate.

### Pre-test 3: Query routing pilot on 500 questions
~1 hr CPU + ~$0.20 API cost.

Method: 500 queries; router decides per query (substrate-only vs LLM-needed); measure
what fraction hit substrate-only path vs LLM-fallback path.

HARD-PASS: 70-80% of queries hit substrate-only path (validates efficiency claim;
thousands of dollars per day savings at 1M-query scale).

## Total cost + time

~3 hours CPU + ~$0.60 API. Cheapest validation of significant architecture claim today.

## What this gates

If all 3 HARD-PASS:
- v1.5 LLM-distillation architecture justified (2-4 weeks engineering)
- Customer pitch updates to "94-96% coverage with hybrid + 70-80% LLM-bypass efficiency"
- Hallucination-catch layer ships as customer-facing feature

If BORDER or HARD-FAIL:
- Smaller claims (cover 88-92% without distillation; honest residual framing)
- Path D Tier 5 stays as v3.0+ path for hard residual

## Strategic implication

LLM-distillation harvest cost is ONE-TIME per KB ($7.50 for 1M-fact KB at Haiku
pricing). At deployment, 70-80% of queries bypass LLM entirely. This is a categorical
EFFICIENCY MOAT distinct from frontier LLM API: thousands of dollars per day saved at
1M-query scale.

Per drill: this reframes Type II priors from "categorical LLM win we can't close" to
"structural moat where substrate becomes the AUDIT + EFFICIENCY layer over frontier LLM
intuitions."

## Cross-references

- Type II priors closure 3x: notes/research_drill_type2_priors_closure_3x_2026-06-07.md
- Drill handoff: notes/exp_dev_handoff_research_type2_priors_closure_2026-06-07.md
- Parametric knowledge + synthesis 2x: notes/research_drill_parametric_knowledge_synthesis_2x_2026-06-07.md

---

**Exp-Dev:** authorize all 3 pre-tests. $0.60 + 3 hours CPU. Apply HARD-PASS /
BORDER / HARD-FAIL autonomously. File results with categorical-efficiency-moat
implications.
