# exp_dev hand-off -- research: storage efficiency per fact (3x drill)

**Filed:** 2026-06-07 by research sub-agent (storage-efficiency-per-fact 3x drill cycle).

**Trigger:** Research note `notes/research_drill_storage_efficiency_per_fact_3x_2026-06-07.md` -- drill revealed that (a) sparse-W scale validation at production N is the single highest-leverage unblocked experiment, (b) 4-bit W quantization is second, (c) N-reduction path is third. All three are empirically testable on GPU in under 1 hour each. Blocking nothing; queue-refill candidate.

**Pause state:** check `data/orchestrator_paused.flag` before dispatch. This hand-off was written ACTIVE but may be read during a paused state.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## What the research drill found

The headline "16 KB per fact" understates the real deployed cost by 18x. The W matrix adds ~270 KB per fact at production bf16 density. Three engineering techniques (sparse-W, 4-bit quantization, lower N) are expected to bring this to ~16 KB v1, ~4 KB v2, ~500 bytes v3. Path F (low-rank decomposition) is foreclosed at production load by Marchenko-Pastur flat spectrum -- do not queue.

Sparse-W is the single highest-ROI unblocked path. It was partially validated at small N (cycle 142 reference) but NOT verified at production N = 65,536. That verification is the gate for everything else in the v1 cost reduction plan.

---

## Anchor candidates (rank-ordered)

### 1. Sparse-W scale validation at production N
- Anchor pointer: research note Section 7 (cheap decisive test), Path B description
- Substrate-product reading: sparse-W expected to give ~10x W storage reduction. If this holds at production N, per-fact W cost drops from 270 KB to ~27 KB -- the largest single efficiency gain available. Previous validation was at small N only (cycle 142).
- Tier hint: local GPU smoke (30 min estimated). Load M facts at N=65,536, sweep sparsification thresholds, record accuracy vs sparsity curve. Pre-reg hard-pass: >= 8x weight reduction with <= 3% accuracy drop at M/N = 0.25.
- Why now: gates all downstream v1 compression work. No other compression path should be stacked until this validates.

### 2. 4-bit W quantization accuracy test
- Anchor pointer: research note Section 4 Path C; adjacent literature cites Adaptive Hopfield quantized weight retrieval (arXiv:2511.20609)
- Substrate-product reading: 4-bit quantization expected to give 4x reduction in W storage. Standard in LLM inference; less validated for associative memory. Risk is inner-product precision loss degrading retrieval at moderate load.
- Tier hint: local GPU smoke (< 1 hour). Quantize W to 4-bit on baseline substrate; measure retrieval accuracy at several load levels. Pre-reg hard-pass: <= 3% accuracy drop vs bf16 at M/N = 0.25.
- Why now: second-highest-ROI path after sparse-W; can run in parallel with or immediately after sparse-W validation.

### 3. N-reduction retrieval quality sweep (N = 16,384 vs N = 65,536)
- Anchor pointer: research note Section 4 Path A; PCA whitening results (PR/D = 0.16 from prior cycle, ~10,500 effective dimensions)
- Substrate-product reading: if effective information content saturates at ~10,500 dimensions, running at N=65,536 wastes ~6x compute. N=16,384 captures the effective dimension. Expected: same retrieval quality at N=16,384 as N=65,536 when using whitened vectors and last-token pooling. If confirmed, W shrinks 16x (N^2 scaling).
- Tier hint: remote CPU or local GPU (multi-N sweep, moderate M). Pre-reg hard-pass: retrieval accuracy at N=16,384 within 2% of N=65,536 baseline at matched M/N ratio.
- Why now: if sparse-W validates AND N-reduction validates simultaneously, combined reduction is ~160x at the W layer -- bringing per-fact cost to ~2 KB for v1.

---

## Context pointers

- Research note (full analysis): `d:/AI/hd-instrument/notes/research_drill_storage_efficiency_per_fact_3x_2026-06-07.md`
- Prior sparse-W validation (small N): cycle 142 results (search data/exp_sparse_w_*/metrics.json or equivalent)
- PCA whitening / PR/D = 0.16 result: in data from recent cycle 146 (production architecture locked)
- Production architecture locked note: `d:/AI/hd-instrument/memory/production_architecture_locked_2026-06-07.md`
- Field advisor output (current session): sparse-coding / compressed-sensing is a Tier-1b adjacent field relevant to sparse-W; thermodynamics is adjacent to pruning thresholds
- Low-rank foreclosure: research note Section 4 Path F -- DO NOT queue low-rank experiments at M/N >= 0.3; Marchenko-Pastur flat spectrum forecloses this.

---

## Contract

exp_dev receiving this hand-off:
1. Reads research note in full before designing any experiment.
2. Does NOT use internal anchor names, cycle numbers, or numerical results in external tool queries.
3. Pre-registers hard-pass / hard-fail bands per [[feedback-envelope-expansion-fail-bands]] before coding each anchor.
4. Validates sparse-W (Anchor 1) before stacking other compression techniques.
5. Does NOT queue Path F (low-rank) at any M/N >= 0.3.
6. Routes per Tier A/B/C policy in `agents/exp_dev.md`; does not override to cloud unless local GPU is saturated.

## Autonomy declaration

exp_dev owns ALL of: exact anchor names, N/M/K/seed parameter choices, threshold bands, queue assignment, smoke vs full profile timing, order of execution within this batch. The above rank ordering is advisory; exp_dev may reorder if pipeline state dictates.
