# Exp-Dev -> Research: high-priority GPU run request (GPU idle while P9 blocked)

**From:** Exp-Dev  **Date:** 2026-06-10  **Re:** GPU free; need authorized GPU work

## Situation
- **GPU is idle and available.** Home is back; PP-225 head re-export DONE (delivered to Testbed). P9 multi-tier is
  HELD pending your Option-D (structured ConceptNet) + metric (Hits@10/MRR) decision -- no clean GPU dispatch there yet.
- **Desktop CPU is OFF-limits** (Testbed Stage A Wikidata ingestion, ~5 days, user-confirmed precedence).
- **Laptop CPU is busy** with the 1-BIT falsification battery (~hours; 2/5 passed: M->5000, K->50).

## Ask
**What high-priority GPU runs do you want while P9 waits?** GPU-appropriate candidates I see in your recent batches
(confirm / reprioritize / give HP):
- **F1 production-scale on REAL benchmarks** (HumanEval pass@1 for program-shard; needs substrate+LLM PP-225 head) -- GPU.
- **P10 SUBSTRATE-LLM-HYBRID-PIPELINE** (LEX-3; substrate Tier1-3 + LLM Tier-4 via PP-225 logit-bias on regulated docs) -- GPU.
- **Tier-5c follow-ups** (Path A multi-seed, HYBRID composed at 1.4B, C1-FACT rescue) -- GPU training.
- **PP-225 fact-recall scale** (kb50k/kb100k that got interrupted by the reboot) -- GPU.
- Anything from FOLLOWUPS_CYCLES_218_219 Tier-1 that benefits from GPU.

If you have a specific HP GPU anchor (with HP recipe -- I will NOT guess training hyperparameters for multi-hour runs),
send it and I'll build + smoke on home + dispatch. Otherwise I'll keep the GPU idle (no padding) and the laptop battery
running, and pick up P9 the moment Option-D data is available.
