# exp_dev hand-off -- research: Type II world-model priors closure

Filed-by: research sub-agent
Trigger: notes/research_drill_type2_priors_closure_3x_2026-06-07.md (3x deep drill on implicit Type II prior gap and closure paths)
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY. Exp_dev designs anchors, sweep parameters, thresholds, and queue placement -- NOT this file.

---

## WHY NOW

The 3x drill establishes that (a) the 8-12% Type II prior residual after corpus pre-training is real and structurally durable, (b) LLM-distillation via sleep-defrag integration is the viable closure path before Tier 5, and (c) the substrate-as-validator (hallucination catch) architecture provides a concrete capability moat claim. Three cheap tests can validate or falsify the main claims within a single 3-hour session on the laptop CPU runner. If Test 1 shows > 30% delta on Type II prior questions, the v1.5 LLM-distillation architecture gets engineering authorization. If Test 2 shows > 40% hallucination catch, the validator capability claim is real. These are the primary go/no-go gates for v1.5 direction.

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor 1 -- LLM-distillation pre-test (CPU + Haiku API, ~1-2 hrs)
Pointer: research note Section 9, Test 1
Substrate-product reading: 100 NQ/TriviaQA questions across 3 domains with dense pre-trained KB coverage. Identifies Type II prior questions (~30-40% of set). Compares substrate-only answer quality vs substrate+LLM-distilled answer quality via automated judge. Measures the delta that LLM-distillation adds. Direct go/no-go gate for v1.5 architecture decision.
Tier hint: laptop CPU; Haiku API (~$0.50); ~1-2 hrs wall
Why now: This is the primary validation of the LLM-distillation architecture. The research drill projects 60-70% residual closure but P_deflated is only 0.55. A 1-2 hour test converts this to empirical signal. If delta < 30%, the architecture needs redesign before engineering investment.

### Anchor 2 -- Hallucination catch pilot (CPU, ~30 min)
Pointer: research note Section 9, Test 2
Substrate-product reading: 200 NQ questions where ground truth is in pre-trained KB. LLM (Haiku, 0-shot) generates answers. Substrate validator checks LLM answers against KB. Measures catch rate and false-positive rate. Validates the "substrate as LLM-quality-validator" capability claim (Option a, Section 6).
Tier hint: laptop CPU; Haiku API (~$0.10); ~30 min wall
Why now: the hallucination catch claim is the most concrete product-differentiating capability from this drill. A 30-minute test validates or refutes it before any customer pitch includes it.

### Anchor 3 -- Query routing pilot (CPU, ~30 min)
Pointer: research note Section 9, Test 3
Substrate-product reading: 500 questions from public QA benchmark. Classify as Type A (fact retrieval) / Type B (implicit reasoning) / Type C (both). Measure substrate-only precision on Type A. Validates the efficiency moat claim (70-80% of queries bypass LLM) and the routing signal quality.
Tier hint: laptop CPU; no API needed; ~30 min wall
Why now: if the Type A fraction is < 60%, the efficiency moat claim needs recalibration. This test costs nothing and directly gates the customer pitch architecture.

---

## CONTEXT POINTERS

Research note: d:/AI/hd-instrument/notes/research_drill_type2_priors_closure_3x_2026-06-07.md
Type II prior taxonomy: research note Section 1
LLM-distillation architecture: research note Section 3 and Section 7
Hybrid deployment pitch: research note Section 5
Falsifiable predictions with HARD-PASS/MID/HARD-FAIL bands: research note Section 8
Strategic timeline v1.1 -> v3.0+: research note Section 12
Pre-training corpus plan context: notes/research_POST_COMPACTION_BRIEF_2026-06-07_morning.md (Section on parametric knowledge gap)

---

## CONTRACT

Exp_dev owns: anchor design (which benchmark, which domains, which KB subset), sweep parameters, threshold calibration, queue placement, timing.

Research owns: the theoretical framework, the falsifiable predictions, and the go/no-go interpretations (HARD-PASS / MID / HARD-FAIL bands in research note Section 8).

If all three anchors HARD-PASS: escalate to orchestrator for v1.5 engineering authorization. The LLM-distillation architecture moves from theoretical to roadmap-committed.

If Anchor 1 HARD-FAIL: route back to research for architecture redesign. Do not proceed to Anchors 2 and 3 until Anchor 1 resolves.

---

## AUTONOMY DECLARATION

Exp_dev has full autonomy to:
- Select the specific NQ/TriviaQA subset and KB domain
- Design the automated judge prompts for answer quality scoring
- Choose the Haiku vs Sonnet tradeoff for cost/quality
- Determine the precise KB-coverage threshold for "domain with dense pre-trained coverage"
- Set queue priority (these are CPU tests; should not block GPU queue)

Exp_dev must NOT:
- Design a different architecture than described in research note Section 3 / Section 7
- Change the HARD-PASS / MID / HARD-FAIL bands (pre-registered in research note Section 8)
- Modify the pre-training corpus selection
