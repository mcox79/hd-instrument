# visibility_decisions_2026-06-09

## CYCLE 204 -- 9-verdict batch (2026-06-09)

v529 -> v530: 8 HP + 1 MIDDLE_BAND; 3 new PP rows (PP-223/PP-224/PP-225); Portfolio 32+222 -> 32+225; HONEST 1520->1529 (+9); LVH 266 unchanged. Key results: (1) scale ladder extended to Qwen-3B 4-bit (ratio=0.798x HP), (2) every-layer Pythia-160M 3-seed validated (mean_ratio=0.7218x std=0.0006, tightest in series), (3) KBLaM RAG-prefix achieves 47% held-out recall (vs 0% bare; rag=oracle), (4) KBLaM projection head at heldout=1.000 -- cross-attn gate identified as Path B limiter not substrate. Queue both empty; Exp-Dev session refills on its cadence.
﻿CYCLE 205 (2026-06-09 PP-225 multi-axis + decisive3 multihop): 3 HP (kb5k heldout=1.000 n=2000; 3seed mean=1.000 std=0.000; kb10k heldout=0.998 n=4000) + 2 HF (Qwen-1.5B bf16 train=0.000 total-fail; Pythia-1.4B bf16 train=0.000 total-fail) + 1 HP decisive3 (substrate=0.996 vs probabilistic=0.753 margin=0.243). 2 LVH-mechanism catches: HF verdict_msg claimed memorization but data shows total non-convergence. PP-225 band 0.78-0.90->0.86-0.95; NEW PP-226 0.80-0.92. Portfolio +1 (PP-226). HONEST 1529->1535. LVH 266->268. v530->v531.
