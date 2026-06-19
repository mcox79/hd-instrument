# exp_dev hand-off -- research: v1.5 LOCK-IN BATCH 2026-06-08

**Filed:** 2026-06-08 ~09:30 by research; user flagged queue empty.
**Trigger:** queue empty post-cycle-182; need batch to lock v1.5 demo gate + extract pending priorities.
**Pause state:** cloud_paused_overnight.flag check; mostly local CPU; one GPU anchor (Path B) and one optional GPU (T5-1) flagged.

**Per [[feedback-no-experiment-design-in-prompts]]:** anchor pointers only; exp_dev designs N/M/K/seeds/bands/profile/anchor name.

## STATUS CONTEXT

Cycle 182 close: HONEST 1360, Portfolio 32+126, multi-hop converged at cycle 181 (PP-119/123/125/120 production architecture), sharding universal capacity primitive locked (PP-101 + PP-100 + PP-116). v1.5 demo gate: pending extraction quality close + demo-prep specific experiments.

## GROUP A: Multi-hop extraction close (HIGHEST PRIORITY — gates v1.5 free-text demo)

### A1: Path A — Qwen-1.5B + few-shot connected-chain prompt + canonicalization (CPU; cheap)
- Pointer: notes/research_to_exp_dev_extractor_escalation_AUTHORIZE_2026-06-08.md
- Substrate-product reading: few-shot triple-extraction prompt forcing connected chain through bridge entity + alias-table entity linking; closes cheap end of extractor spectrum
- Tier: LOCAL CPU (~2-3 hr)
- HP: recall@2 >= 0.50

### A2: Path B — Llama-3.1-8B-Instruct extractor (Testbed-GPU; HippoRAG/BridgeRAG SOTA class)
- Pointer: same; matches published-SOTA extractor class
- Tier: TESTBED GPU (~2-3 hr; $5-15 cloud OR local laptop GPU)
- HP: recall@2 >= 0.55

## GROUP B: Demo-prep specific experiments (build v1 demo with empirical backing)

### B1: Sharding contrast visualization data
- Substrate-product reading: extend sharding_scaling_law sweep to S=32/64/128 with same monolithic baseline; produces "categorical scaling chart" for demo
- Tier: LOCAL CPU (~1 hr)
- HP: per-shard recall stays at 1.000 / monolithic continues collapsing
- Demo asset: contrast chart for v1 webpage

### B2: PP-107 confidence overlay demo data
- Substrate-product reading: generate confidence-vs-correctness data points (in-distribution vs out-of-distribution queries) for substrate; demo shows "substrate flags when it doesn't know" with AUC=1.0 separation
- Tier: LOCAL CPU (~1 hr)
- HP: AUC remains 1.0 on 200-query held-out set
- Demo asset: confidence-overlay visualization

### B3: Counterfactual do() demo scenarios
- Substrate-product reading: build 20 customer-pitch counterfactual scenarios (e.g., "what would happen if the bridge was X instead of Y") with substrate generating + audit chain proving determinism + tamper detection
- Tier: LOCAL CPU (~2 hr)
- HP: 20/20 deterministic + auditable
- Demo asset: counterfactual panel for webpage

### B4: Legal citation snowball extended demo
- Substrate-product reading: extend PP-120 from 50 to 500 seed papers (10x); validate 100% 3-hop closure holds at scale; build demo dataset for legal pitch
- Tier: LOCAL CPU (~2 hr)
- HP: 95-100% 3-hop closure at 500 seeds
- Demo asset: legal demo with realistic dataset size

## GROUP C: Native multi-hop ablations (close remaining gaps)

### C1: N1b — Per-hop iterative ablation on native substrate
- Pointer: notes/research_to_exp_dev_N1b_TIER5_additions_2026-06-08.md
- Substrate-product reading: parse hop-1 first, traverse 1 hop, use intermediate to parse hop-2; compare vs single-pass N1
- Tier: LOCAL CPU (~2-3 hr)
- HP: matches single-pass within +/-2pp

### C2: N1d — Parallel sub-question decomposition on NATIVE substrate
- Pointer: notes/research_to_exp_dev_N1cN1dN1e_alternatives_test_AUTHORIZE_2026-06-08.md
- Substrate-product reading: small LLM generates K=3 parallel sub-questions; all queried against substrate triples; results fused
- Tier: LOCAL CPU (~2-3 hr)
- HP: recall@2 >= 0.55

### C3: I1 — Real KG (NELL or Freebase mini) substrate K-hop
- Pointer: notes/research_to_exp_dev_iterative_drill_5_anchors_AUTHORIZE_2026-06-08.md
- Substrate-product reading: encode NELL-595 or Freebase-mini KG subset as Pattern B triples; 2-hop and 3-hop queries; recall@K against gold paths
- Tier: LOCAL CPU (~1-2 hr; requires KG download ~500MB)
- HP: real-KG 2-hop recall@K >= 0.70

## GROUP D: Tier 5 foundational (substrate-intrinsic-language gate)

### D1: T5-1 Pythia-160M Arch 8 substrate-KV-cache MVE
- Pointer: notes/research_to_exp_dev_N1b_TIER5_additions_2026-06-08.md
- Substrate-product reading: replace one Pythia-160M attention layer's KV-cache with substrate retrieval; evaluate on WikiText perplexity
- Tier: LOCAL GPU (~4-6 hr) OR LOCAL CPU (~12-24 hr)
- HP: perplexity within 10% of standard Pythia-160M

## GROUP E: Substrate capability extensions (open priorities)

### E1: Wikipedia substrate ingest dry-run (10K articles smoke)
- Pointer: notes/exp_dev_handoff_research_overnight_2026-06-07_batch.md C1
- Substrate-product reading: 10K-article Wikipedia ingest smoke; validate pipeline timing extrapolation; OAS-cleared (cycle 181)
- Tier: LOCAL CPU (~30-60 min smoke)
- HP: 10K completes; timing extrapolates < 12 hr for full 5.84M

### E2: Wish 2 multimodal MSCOCO binary-CLIP pre-test
- Pointer: notes/research_to_exp_dev_composition_plus_wish_we_had_pretests_AUTHORIZE_2026-06-07.md
- Substrate-product reading: bipolar-CLIP at N=512; MSCOCO image-text retrieval; r@10 vs full-precision baseline
- Tier: LOCAL GPU OR CPU (~3-4 hr)
- HP: binary CLIP retains >= 90% MSCOCO r@10

### E3: Wish 3 preference bindings (customer-specific intuitions)
- Pointer: same routing; Wish 3 anchor
- Substrate-product reading: synthetic customer feedback on 100 queries; substrate accumulates bindings; sleep defrag aggregates; predicts 50 held-out queries
- Tier: LOCAL CPU (~2-3 hr)
- HP: substrate preference prediction matches >= 75% on held-out

## GROUP F: 2x rescue residuals (per always-research-negatives-2x rule)

### F1: Bundle capacity cliff sqrt(K-1) scaling-law verification
- Pointer: notes/research_to_exp_dev_negatives_2x_GAP_FILL_cycle178_2026-06-08.md Gap 1
- Substrate-product reading: K_crit at N=4096/8192/16384; verify sqrt(K-1) prediction
- Tier: LOCAL CPU (~2 hr)
- HP: K_crit/N follows sqrt(K-1) within 5% (cliff predictable scaling-law)

### F2: Resonator K=4 multi-axis rescue (N + M + iterations + init)
- Pointer: same; Gap 2
- Substrate-product reading: combined N=4096 + M=20 + higher iterations + warm-start init
- Tier: LOCAL CPU (~2-3 hr)
- HP: K=4 recall >= 0.70

### F3: Mycorrhizal multi-hub similarity-weighted rescue
- Pointer: same; Gap 3
- Substrate-product reading: similarity-weighted hub selection (vs uniform random cycle 178); per-domain hubs
- Tier: LOCAL CPU (~2-3 hr)
- HP: >= 0.70 topic coverage at Q=100

## RECOMMENDED ORDERING (max queue depth)

Highest yield + cheap first:
1. A1 Path A extractor (CPU; cheap; closes free-text v1.5)
2. B1 Sharding viz (CPU; 1 hr; demo asset)
3. B2 PP-107 confidence viz (CPU; 1 hr; demo asset)
4. E1 Wikipedia smoke (CPU; 30-60 min)
5. F1 Bundle cliff (CPU; 2 hr; 2x rescue residual)
6. C3 I1 NELL KG (CPU; 1-2 hr; structured benchmark)
7. C2 N1d parallel native (CPU; 2-3 hr)
8. C1 N1b iterative-on-native ablation (CPU; 2-3 hr)
9. B3 Counterfactual scenarios (CPU; 2 hr; demo)
10. B4 Legal snowball 500 seeds (CPU; 2 hr; demo)
11. F2 Resonator K=4 (CPU; 2-3 hr)
12. F3 Mycorrhizal multi-hub (CPU; 2-3 hr)
13. E3 Wish 3 preference (CPU; 2-3 hr)
14. E2 Wish 2 multimodal (CPU/GPU; 3-4 hr)
15. A2 Path B Llama-8B extractor (GPU; 2-3 hr; SOTA gate; needs install + GPU auth)
16. D1 T5-1 Pythia substrate-KV-cache (GPU 4-6h OR CPU 12-24h; Tier 5 foundational)

Total: 16 anchors; ~30-50 hr CPU + 4-10 hr GPU. Fills queue with weeks of work.

## Cross-references

- Cycle 181 multi-hop convergence (PP-119/123/125/120): notes/orchestrator_to_research_results_summary_2026-06-08_cycle181.md
- Sharding universal principle: notes/research_to_exp_dev_sharding_universal_capacity_primitive_2026-06-08.md
- Extractor escalation: notes/research_to_exp_dev_extractor_escalation_AUTHORIZE_2026-06-08.md
- Hybrid 5 anchors: notes/research_to_exp_dev_hybrid_drill_5_anchors_AUTHORIZE_2026-06-08.md
- DEEPER consolidated AUTHORIZE: notes/research_to_exp_dev_DEEPER_drills_8_consolidated_AUTHORIZE_2026-06-08.md
- 5x deep dive iterative drill 5 anchors: notes/research_to_exp_dev_iterative_drill_5_anchors_AUTHORIZE_2026-06-08.md
- N1b + T5-1: notes/research_to_exp_dev_N1b_TIER5_additions_2026-06-08.md

---

**Exp-Dev:** queue refill batch (16 anchors). Group A is HIGHEST yield (closes v1.5 free-text multi-hop story); Group B is demo-asset building (cheap CPU); Group C/F are remaining gap closures; Group D is Tier 5 foundation; Group E is product capability extensions. Recommended ordering above; pick per resource availability.

Path B + T5-1 + Wish 2 may need GPU or library install auth — flag as needed.
