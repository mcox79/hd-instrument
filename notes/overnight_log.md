# Overnight autonomy log

User went to sleep 2026-05-18 evening. This file tracks autonomous cycles.

## Starting state

- **Market lock**: persistent cognitive layer / agent memory backend
- **Platform lock**: consumer CPU (AVX-2/NEON) + NVMe-backed pool, no GPU
- **Headline test**: Phase B.3 compositional retrieval (C3) must beat C1 classical pool
- **Queue runner**: launched on remote GPU box, processes data/overnight_queue/queue.json
- **Cron wake-up**: every 30 min at :17 and :47, runs autonomous monitoring cycle

## Three parallel watchdogs

1. **GPU queue (remote `marsh@home`)**: `data/overnight_queue/`
   - phase_b2_vsa_pool (Phase B.2 VSA-pool vs classical)
   - scaling_sweep_N8K_to_64K (M5 scaling at N in {8K..64K})

2. **CPU queue (local laptop)**: `data/local_cpu_queue/`
   - cpu_platform_timing (validate <100ms p99 on consumer CPU)

3. **CPU queue (remote workstation, runs alongside GPU queue)**: `data/remote_cpu_queue/`
   - cpu_platform_timing (validate on stronger workstation-class CPU)

Plus background research agent on **memory consolidation neuroscience**
(unbiased framing: describe biology/math, not design AI).

## Already established (pre-overnight)

- Phase A: W_A baseline 2.4817 bpc, state saved
- Phase B.1: C0 +3.57 bpc forgetting, C1 +1.85 bpc (partial mitigation)
- Wave 14.B bundle/K sweeps: 100% recovery at B up to 128 and K up to 2048 (N=4096)

## Cycle entries (most recent first)

### 2026-05-18 ~22:25: CPU platform timing v1 — honest negative finding + follow-up queued

Both CPU timing v1 runs completed (laptop ~6 min, workstation ~6 min).

- **Laptop (consumer baseline)**: 2/27 configs met <100ms p99
- **Workstation (high-end consumer)**: 3/27 configs met <100ms p99

Configurations that met the target on laptop: N=2048 + P in {1K, 10K} + B=2.
Decomposition cost dominates: ~60-90ms per single decompose at B=2, scales
linearly with B. The v1 test decomposed top-M=4 bundles per query, which
is 4x the realistic cost.

**Honest reframing**: the v1 experiment design was overly pessimistic.
Real deployment patterns:
- Most queries: retrieve-only (no decomposition)
- Some queries: retrieve + 1 decompose (when agent asks "what's in here")
- Rare: decompose-only (background consolidation)

Wrote `exp_wave14b_cpu_platform_timing_v2.py` with three realistic modes
and queued on both CPU watchdogs. Hypothesis: retrieve-only meets target
at all configs; retrieve+1 meets target at modest N/B. Will know in ~10
min.

This is NOT a substrate failure. It's an instrumentation correction.

### 2026-05-18 evening: consolidation neuroscience research returned

Unbiased survey of memory consolidation biology + math came back
(notes/wave14b_m2_consolidation_design.md). Five concrete algorithmic
steps for M2 design:

1. **Selection scoring** (Mattar-Daw 2018): need × gain prioritization
   for which pool entries to replay. Need = retrieval count; gain =
   delta-rule residual norm.
2. **Pattern extraction**: 14.B decompose selected entries, build
   co-occurrence matrix, find top-K recurring patterns.
3. **Concept atoms**: bundle recurring patterns into new codebook atoms,
   bound to new position codes.
4. **Interleaved cortical update** (CLS, McClelland 1995): replay
   selected entries mixed 50/50 with current training data through
   delta-rule W updates.
5. **Homeostatic downscaling** (Tononi-Cirelli SHY): after each
   consolidation cycle, multiplicatively decay all pool entries.
   Concept atoms in codebook don't decay.

This is a complete algorithmic recipe grounded in concrete biological
findings (Wilson-McNaughton 1994 replay discovery; Tse 2007 schema
consolidation; Kitamura-Tonegawa 2017 engram tagging; Saxe 2019 SVD
ordering). Falsification criteria + validation experiment also
specified in the design doc.

NOT implemented — design only, awaits supervised implementation in
next session.

(autonomous cycles will append below)
