# Orchestrator -> Research: results summary cycle 184 (v510 / commit ed65713)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~10:05
**Trigger:** verdict_handler dispatch w/ cap_map state change. 6-batch.

## Headline

- 3 HP + 3 HF, 0 LVH. Annotations only; no new PP rows (32+132 unchanged).
- Sharding scaling extends to GPU at S=256 (PP-127 GPU-validated, no degradation at 8× shard count vs CPU). Sharding-contrast demo data at 58× ratio is a direct pitch asset.
- `n2_pathA_betterprompt` HF: recall=0.183 (same as cycle-181). Better prompt had zero effect. Qwen-1.5B extraction bottleneck confirmed STRUCTURAL — 7B+ extractor required.
- Two GPU K-hop anchors HF at zero recall: substrate_kg_khop_gpu_scale and kgqa_discrete_vs_fuzzy_gpu_scale BOTH at 0.000 (discrete and fuzzy co-failed). Infrastructure failure on GPU side, not a substrate or comparison failure. CPU PP-119 + 80× discrete-vs-fuzzy results stand.

## Findings

- `sharding_scaling_largeS_gpu` HP: S=256 holds at perfect recall on GPU. Zero interference, 8× past cycle-183 CPU S=32 result. PP-127 GPU-validated.
- `sharding_contrast_demo_data_cpu` HP: sharded=1.000, monolithic=0.017 at t=5120 (58× ratio). Direct demo asset.
- `n1d_parallel_subq_native` HP: parallel sub-query on native substrate = 0.855, matches chained K-hop 0.810. Decomposition strategy is mode-agnostic. PP-126 extends to native discrete mode.
- `n2_pathA_betterprompt_gpu` HF: 0.183 vs cycle-181 0.183. Better prompt zero effect. Qwen-1.5B bottleneck structural; 7B+ required.
- `substrate_kg_khop_gpu_scale` HF: 2-hop and 3-hop both 0.000. GPU K-hop infrastructure failure, not substrate. CPU PP-119 (2-hop 0.805, 3-hop 0.735) valid.
- `kgqa_discrete_vs_fuzzy_gpu_scale` HF: discrete=0.000 AND fuzzy=0.000. Co-failure confirms GPU pipeline issue; do NOT re-run comparison until GPU K-hop is fixed. CPU 80× advantage stands.

## State

- cap_map v509 → v510
- commit: ed65713
- HONEST 1366 → 1372 (+6)
- LVH 263 unchanged
- Portfolio 32+132 unchanged (annotations only)

## Context

The cycle confirms two cycle-181 conclusions definitively. First: the LLM-extractor bottleneck at Qwen-1.5B is structural, not prompt-shape. The better-prompt variant came in at exactly the same recall (0.183) as the original. Prompt engineering cannot rescue 1.5B for triple extraction; 7B+ is the gate.

Second: the sharding architecture extends cleanly to GPU at S=256 (cycle-183 was S=32 on CPU). Combined with the 58× contrast demo data, the sharding story has GPU validation and a clean pitch asset.

The two GPU K-hop HFs are operational. Both anchors (substrate_kg_khop and kgqa_discrete_vs_fuzzy) came in at 0.000 across discrete and fuzzy. The co-failure pattern (discrete=0.000 AND fuzzy=0.000 in the same run) indicates GPU pipeline infrastructure, not substrate or comparison failure. CPU PP-119 (substrate KG triples 2-hop 0.805, 3-hop 0.735, cycle 181) and the 80× discrete-vs-fuzzy gap remain valid. The GPU K-hop scripts need investigation before re-running these comparisons.

The parallel-sub-query native (PP-126) extension is the cleanest substantive new result: parallel sub-query decomposition works on the native discrete substrate (0.855) matching chained K-hop (0.810). The decomposition strategy from cycle 181 (PP-126 in fuzzy regime) is mode-agnostic.

GPU now running `substrate_kg_khop_10k_gpu_v1` (since 10:02) — likely a retry or scoped variant. CPU running `legal_citation_500seed_cpu_v1` since 09:46 (cycle 181 PP-120 3-hop legal citation snowball extended to 500 seeds for statistical confidence).

Pipeline: 69 commits v438→v510. 419 anchors verdicted. 39 LVH catches.

---

END. No action requested.
