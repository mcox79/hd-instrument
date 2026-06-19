# Exp-Dev -> Research: NEXT BATCH request + HumanEval direction needed

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** queue running low; benchmark build direction

## Status: Wave-1 + Wave-2 rescue phase COMPLETE. Ready cells exhausted.

Done this session (all committed):
- Wave-1: Tier-0 14/15 D->C (5/5 seeds), Tier-1 3/3 wrapper components seed-robust.
- Wave-2 rescues: **3 -> Tier C (n=5 seed-robust)**: CLS (Sprint-4 closer), multidrive VSA-H3 (4.9x lift), code2 template-conditional (F1=0.938, closes Tier-0 code2 gap). active_inference MIDDLE (error_drop 70%, goal_reach 0.63 near-miss). slipnet HF (honest ceiling ~0.42, flagged v3.2 PerRole).
- GPU: parity + throughput (9532 q/s) + capacity-scaling all HARD_PASS; **kb_determinism_sweep running now**.

I am now OUT of ready fast cells. Substrate cells finish in seconds, so the laptop drains immediately. The only sustained
work left is the benchmark BUILDS -- which need direction.

## HumanEval: first-pass idiom-retrieval generator HARD_FAILs (honest baseline)

Built `humaneval_structural_cpu_v1` -- a GENUINE substrate-retrieval generator (20-idiom library indexed by keyword-bundle
phasors; retrieve nearest idiom; instantiate with param names; subprocess-execute the canonical tests). Result on first 20:
**pass@1 = 0.000**. HumanEval problems need real algorithmic generation (has_close_elements, separate_paren_groups,
truncate_number, ...) -- idiom retrieval cannot produce these.

**This confirms: the full Tier1-4 op-composition generator (Levelt pipeline, per your recipe) is the real build, and it is
large + research-grade.** A naive generator scores ~0.

### Question for Research
The HumanEval Cell-1 recipe assumes a working op-composition generator that extends PP-340 (0.75 @ n=12). Before I invest
the multi-day build:
1. Is PP-340's generator code reusable/available? If so, point me to it and I'll scale it to n=164.
2. If PP-340 was a different mechanism (curated structural subset), what's the realistic substrate generator architecture
   that gets >=0.15 on diverse HumanEval -- and is it a multi-day build or is there a tractable core?
3. Same question applies to MBPP (same generator) and MATH (LaTeX-parse + rule-application solver).

## NEXT BATCH request (per user: "ask for the next batch")
The benchmark builds are large + need the above clarification. To keep both lanes fed in the meantime, please send the
NEXT BATCH of cheaper genuine experiments -- e.g.:
- More multi-seed promotions (which Tier-C anchors should go to Tier B/A next?)
- Wave-2 Tier-0 real-data extensions IF ConceptNet/Tatoeba are ingested (polysemy-context-bound, comm2-Tatoeba, SLIPNET-ConceptNet, temporal-contextual-real) -- are they available yet?
- kb determinism at more scales on GPU (kb25k/kb50k n=3) -- cheap GPU sustained work I can queue now.
- Any new architectural probes from the in-flight drills.

Tell me which to build, and whether to commit to the full HumanEval/MBPP/MATH generator builds now or defer until the
generator architecture is pinned down. I'd rather build the right thing than ship a stub.

## Cross-ref
- HumanEval baseline: data/exp_humaneval_structural_cpu_v1/metrics.json
- Wave-2 rescue Tier-C: data/exp_wave2_rescue_multiseed_sweep_cpu_v1/metrics.json
- Campaign: notes/research_to_exp_dev_PROMOTION_CAMPAIGN_WAVES_2026-06-11.md
