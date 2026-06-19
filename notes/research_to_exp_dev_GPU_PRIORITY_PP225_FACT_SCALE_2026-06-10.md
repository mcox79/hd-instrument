# Research -> Exp-Dev: GPU priority — PP-225 fact-recall kb50k/kb100k completion (known HP recipe)

**From:** Research  **Date:** 2026-06-10
**Re:** Your GPU work request; P9 held pending Option D (5 days)

## Highest priority GPU work: PP-225 fact-recall kb50k/kb100k completion

**Why this first:**
1. **Already interrupted by home reboot** — partially complete; finishing avoids loss of prior work
2. **Known HP recipe** — fp32 head; LR/warmup/batch already validated for kb160m fact-recall on Pythia-1.4B
3. **High commercial value** — substrate as LLM memory v2.0 thesis; multi-hop revive (user-locked priority "extremely important")
4. **Builds on PP-225 export DONE** (fp32 head delivered to Testbed)
5. **GPU-appropriate** — long training run; uses your strongest hardware

Use the SAME recipe as the PP-225 head re-export you just completed (head_pythia14b_fp32.pt). The kb50k/kb100k fact tests just need execution on this head.

## Second priority (if PP-225 fact-recall ships fast)

**F1 follow-up Tier 1: program-shard on HumanEval pass@1**
- Build on existing COMP-26 program-shard (100 functions; recall=1.000)
- Pipeline: substrate composes function shards + LLM emits tokens via PP-225 logit-bias
- Eval: HumanEval-164 pass@1
- HARD-PASS: substrate-LLM hybrid ≥ small LLM baseline (Pythia-1.4B ≈ 0.10-0.20; substrate hybrid target ≥ 0.15)

**Caveat:** This requires NEW HP recipe (substrate-LLM hybrid for code; not just fact-recall). Per your discipline "will NOT guess HP for multi-hour runs": consult Research for HP recipe BEFORE long training run. Smoke first with conservative HP, then ask.

## Third priority

**Tier-5c Path A multi-seed validation**
- Existing path; existing HP
- Multi-seed (5 seeds) for HP fragility characterization
- Useful empirical evidence for cycle 217 Path A claim

## NOT yet ready for GPU dispatch

- **P10 LEX-3 substrate-LLM hybrid on regulated docs** — needs corpus + HP design + human eval setup. File this for Week 2-3.
- **C1-FACT rescue** — Research hasn't designed this yet; needs drill.
- **F1 NarrativeQA / ArgKP / HotpotQA** — need substrate-LLM hybrid setup + benchmark integration.

## Laptop 1-BIT falsification battery status

Glad to hear 2/5 PASS (M→5000 OK + K→50 OK). 1-bit is holding under realistic conditions. Standing for remaining 3 (correlated-atoms + depth-scaling + N-scaling).

## Sequencing recommendation

1. PP-225 fact-recall kb50k/kb100k (known HP; resumable)
2. Tier-5c Path A multi-seed (known HP; validation)
3. F1 HumanEval program-shard (needs HP consultation)
4. P10 LEX-3 (post-corpus design)

GPU stays busy with high-value validated-HP work. P9 multi-tier pickup the moment structured ConceptNet (Testbed A2) is available.

## Cross-references
- PP-225 head export DONE: notes/exp_dev_to_testbed_PP225_EXPORT_READY_2026-06-10.md
- F1 follow-up: notes/research_to_exp_dev_FOLLOWUPS_CYCLES_218_219_WAVE5_2026-06-10.md
- Multi-hop revive priority: memory/project_multihop_revive_priority.md
- Testbed Stage A precedence: notes/testbed_to_research_CONCEPTNET_STRUCTURED_NOT_HELD_2026-06-10.md

---

**Exp-Dev:** PP-225 fact-recall kb50k/kb100k FIRST (known HP; interrupted; high value). Then Tier-5c Path A multi-seed. Then F1 HumanEval program-shard (with HP consultation).

GPU stays productive while P9 multi-tier waits on Testbed A2 (~5 days).
