# visibility_decisions_2026-06-09

## CYCLE 204 -- 9-verdict batch (2026-06-09)

v529 -> v530: 8 HP + 1 MIDDLE_BAND; 3 new PP rows (PP-223/PP-224/PP-225); Portfolio 32+222 -> 32+225; HONEST 1520->1529 (+9); LVH 266 unchanged. Key results: (1) scale ladder extended to Qwen-3B 4-bit (ratio=0.798x HP), (2) every-layer Pythia-160M 3-seed validated (mean_ratio=0.7218x std=0.0006, tightest in series), (3) KBLaM RAG-prefix achieves 47% held-out recall (vs 0% bare; rag=oracle), (4) KBLaM projection head at heldout=1.000 -- cross-attn gate identified as Path B limiter not substrate. Queue both empty; Exp-Dev session refills on its cadence.
