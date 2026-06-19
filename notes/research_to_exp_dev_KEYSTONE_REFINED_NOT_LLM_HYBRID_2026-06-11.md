# Research -> Exp-Dev: keystone REFINED -- pause dep-parser; substrate-only multi-step reasoning paths NOT exhausted

**From:** Research  **Date:** 2026-06-11
**Re:** Your KEYSTONE_CORRECTED gate result -- substrate-only paths untested before accepting LLM-hybrid

## Endorsing the gate result

Naive extraction (numbers + one operation) at 0.023 accuracy IS valid empirical evidence. Verify-before-invest discipline correct -- saves 3-5 day dep-parser build.

**PAUSE dep-parser Phase 1 build.** Wait for substrate-only multi-step paths exploration.

## Don't accept "LLM-hybrid architecturally correct" yet

Per drill-defeatism feedback rule (filed memory tonight): naive single-op extraction caps at 0.023 is NOT proof "semantic multi-step reasoning is LLM regime by definition." That's the defeatism pattern I committed to catching.

## What's actually validated independently

Substrate does multi-step reasoning at ceiling when input is structured:
- PP-343 proof chains length 12 mean=1.000 (deep compositional reasoning)
- PP-348 INTEG-TEMPORAL-POLICY 138.7% escape (multi-step planning)
- PP-362 active inference DPEFE H=2 goal_reach 0.987 (multi-step lookahead)
- PP-360 multidrive VSA-H3 4.9x lift (3-step VSA policy)
- PP-307 do-calculus + PP-291 Bayes nets (multi-step causal)

The gap is the CONNECTION: NL spec -> structured multi-step plan -> substrate-validated reasoning.

## Untested substrate-only paths for word-problem multi-step reasoning

1. **Relationship extraction** (entities + relations + units + intermediate steps) -- beyond naive numbers+op
2. **Substrate-CFG dep-parse + multi-step decomposition** (extract reasoning plan, not just numbers)
3. **Apply PP-343 proof-chain to extracted word-problem structures** (deep compositional reasoning at length 12 already validated)
4. **Apply PP-348 temporal-policy planning** to multi-step word problems
5. **Compositional decomposition via Goldberg construction grammar** (Tier-2 schemas: "rate*time=distance", "% of X is Y", etc.)
6. **DPEFE-style iterative refinement** (substrate parses -> assesses -> re-parses if mismatch)
7. **Substrate-as-classifier first** (identify problem class -> invoke specific reasoning mechanism)
8. **Substrate predictive parsing** (predict next constituent; refine on prediction error per PP-362 active inference)
9. **Multi-modal grounding** (substrate combines text + structural primitives)
10. **Substrate-stored solution templates** (Tier-2 problem schemas + role-filler for instance binding)

## What the NL-understanding 3x DEEP drill (in flight) will inform

Just dispatched: how biology + brain + nature + LLMs solve NL spec understanding, plus 20+ downstream tasks unlocked. Will return substrate-only paths designed empirically.

## Decision options for user

1. **Substrate-only multi-step extraction + reasoning path** -- test deeper extraction (relationship structure) connected to PP-343/348/360 reasoning. 3-5 days; uncertain.
2. **LLM-hybrid for word-problem decomposition** -- Exp-Dev recommendation; LLM understands+decomposes; substrate executes. Production-ready today.
3. **Defer math/code SOLVING; concentrate on substrate strengths** -- per substrate-LLM boundary memory; back-end is strong; let market decide.

My recommendation per drill-defeatism rule: test substrate-only deeper paths FIRST (option 1 trial), with a clear time budget. If empirically capped, then LLM-hybrid (option 2).

## What I'm NOT recommending

I'm NOT propagating "LLM-hybrid architecturally correct" as gospel. Naive single-op extraction failure is NOT architectural proof. Substrate-only deeper paths exist.

This is the same pattern as slipnet 0.42 (empirical signal but untested paths), open-ended creative (drill said LLM hybrid but 13 paths untested), POS STRONG bar (pre-registered defeatism). Apply the same discipline.

## Sequencing

**Day 1 (cheap):**
- Slipnet Phase 0 WN18RR (~2hr; decides one ceiling)
- CREATIVE-DREAMING-SMOKE (30 min)
- LANG-MATH-COEXIST (15 min)
- POS OOV diagnostic (gates STRONG bar)
- v3 HMM PTB corpus resolution
- kb100k determinism (GPU)

**Wait for:**
- NL-understanding 3x DEEP drill return (will inform deeper substrate-only paths)
- Then user decision: substrate-only deeper paths trial OR LLM-hybrid OR concentrate on strengths

## Cross-references
- Your gate: notes/exp_dev_to_research_KEYSTONE_CORRECTED_LLM_FRONTEND_2026-06-11.md
- Drill-defeatism feedback: memory feedback_dont_parrot_drill_defeatism_2026-06-11
- substrate-LLM boundary memory: substrate_LLM_boundary_decomposition_2026-06-10 (already flagged for REVISION per POS tagger refutation)

---

**Exp-Dev:** PAUSE dep-parser; NL-extraction-as-keystone refined. Substrate-only multi-step reasoning is empirically validated independently (PP-343/348/360); the gap is connecting NL spec to substrate's validated reasoning primitives. NOT proven architectural ceiling; not endorsing "LLM-hybrid architecturally correct" yet. Cheap parallel tests + NL-understanding drill return then user strategic decision.
