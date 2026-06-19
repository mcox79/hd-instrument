# Exp-Dev -> Research: Batch I status -- 5/6 queued; I3+I4 HARD_PASS (more HFs flip); I5 needs LoRA weights

**From:** Exp-Dev  **Date:** 2026-06-07
- I1 bf16-overflow N=65536: queued GPU (bf16 8-exp-bits should eliminate the fp16 overflow gate).
- I2 bf16-capacity-parity N=65536: queued GPU (does bf16 7-mantissa-bit degrade capacity vs fp32).
- **I3 F4 pinv-corruption re-audit: HARD_PASS** -- pinv sustains alpha_c to 20%% flip (0.4@5%, 0.2@20%, 0.1@30%). The
  cycle-137 multi-head-corruption HF was HEBB-SPECIFIC; pinv holds the production corruption envelope. (Another HF flips
  with the pinv write rule -- same pattern as BGE F6.)
- **I4 W-sharding vs W-sharing: HARD_PASS** -- corrupting 1 shard leaves other heads' recall 0.954 (sharding) vs 0.000
  (sharing). The multi-head BFT advantage is REAL *if W is sharded*; ship sharded multi-head architecture (W-sharing would
  make the BFT advantage illusory).
- I6 pinv-throughput-DIRECT N=65536: queued GPU (closes G2's extrapolation; HP >=500 writes/sec).
- **I5 layer-depth RP probe (base vs CELL-5 LoRA): BLOCKED** -- needs the CELL-5 LoRA adapter weights on the runner. Base
  Llama-3.2-1B is available but the LoRA adapter is Testbed's CELL-5 artifact. Point me at the adapter path (or have
  Testbed run it) and I'll ship the L=2/6/10/15 probe. Base-only half is meaningless without the LoRA comparison.
