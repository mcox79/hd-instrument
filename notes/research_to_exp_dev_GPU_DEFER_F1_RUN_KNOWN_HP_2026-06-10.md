# Research -> Exp-Dev: defer F1 HumanEval, run known-HP GPU instead

**From:** Research  **Date:** 2026-06-10
**Re:** Your F1 HumanEval HP consult; per discipline don't guess multi-hour HP

## Decision: DEFER F1 + run alternatives with known HP

F1 HumanEval program-shard is genuinely a multi-day build (substrate code-shard encoder + LLM logit-bias for code + HumanEval execution harness). I won't guess HP for it. Will route a proper design when ready (separate routing in coming days).

## Run NOW (known HP)

### Priority 1: PP-225 fact-recall kb500k or kb1M scaling
- kb100k DONE; push to production scale
- Multi-hop revive (user-locked priority "extremely important")
- Known HP recipe (matches kb100k)
- Resumable from existing checkpoint
- GPU-appropriate; long training run

### Priority 2: Tier-5c Path A 5-seed extension
- Cycle 217 Path A multi-seed already validated 1 seed
- Extend to 5-seed for HP fragility characterization
- Known HP recipe
- ~7 min per seed × 5 = ~35 min GPU

### Priority 3: HYBRID composed at 1.4B (cycle 217 reference)
- Path A + PP-225 composition at 1.4B
- IF HP recipe is in cycle 217 notes; otherwise defer
- Validates "substrate scaffold + LLM token via PP-225" at 1.4B scale

## F1 design cycle (proper routing in coming days)

Will need:
- Code-shard encoder design (substrate representation of function structure)
- HumanEval execution harness (sandboxed code execution)
- Logit-bias scale for code generation (NEW; different from fact-recall)
- LLM choice rationale (Pythia-1.4B vs Qwen-1.5B vs Llama-7B)
- Pre-reg with realistic HARD-PASS (small LLM baseline 0.10-0.20; substrate-hybrid target ≥0.15)

Worth doing properly. Not tonight.

## Note: highest revival path D3.5 LLM-hybrid (cross-domain)

Cross-domain revival drill identified D3.5 LLM-hybrid as P=0.62 (highest of any revival). This ALSO uses PP-225 head + LLM inference. Substantially less novel HP than F1 (LLM proposes + substrate ranks; uses validated head; no code-execution harness). Might be design-ready in 1-2 days if user prioritizes cross-domain commercial claim restoration.

If you want to design D3.5 cross-domain LLM-hybrid before F1 HumanEval, that's the highest-leverage revival GPU work.

## Sequence

1. PP-225 fact-recall kb500k/kb1M (multi-hop revive; known HP; resumable)
2. Tier-5c Path A 5-seed (HP fragility characterization)
3. HYBRID 1.4B (if HP recipe in cycle 217)
4. THEN design D3.5 cross-domain LLM-hybrid OR F1 HumanEval based on commercial priority

## Cross-references
- F1 follow-up routing: notes/research_to_exp_dev_FOLLOWUPS_CYCLES_218_219_WAVE5_2026-06-10.md
- Cross-domain revival drill: notes/research_drill_cross_domain_revival_3x_2026-06-10.md (D3.5 LLM-hybrid P=0.62)
- Original GPU priority: notes/research_to_exp_dev_GPU_PRIORITY_PP225_FACT_SCALE_2026-06-10.md
- Multi-hop revive memory: project_multihop_revive_priority.md

---

**Exp-Dev:** defer F1; run kb500k/kb1M PP-225 scaling + Tier-5c 5-seed. Multi-day design cycle for F1 (and possibly D3.5 cross-domain hybrid which is higher-leverage).
