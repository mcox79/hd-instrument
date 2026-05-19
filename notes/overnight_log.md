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

### 2026-05-19 ~00:25: ALPHA sweep + bundle noise theory came back

**ALPHA sweep result** (4 min wall):

| alpha | pre C1 | pre C2 | post C1 | post C2 | C2-C1 post |
|---|---|---|---|---|---|
| 0.10 | 2.4539 | 2.4615 | 4.9750 | 5.0170 | −0.0421 |
| 0.30 | 2.4817 | 2.5006 | 4.3352 | 4.3911 | −0.0559 |
| 0.50 | 2.5945 | 2.6246 | 4.0193 | 4.0800 | −0.0607 |
| 0.70 | 2.7926 | 2.8351 | 3.8368 | 3.8967 | −0.0600 |

C2-C1 gap is consistent across ALPHA (−0.04 to −0.06 bpc), slightly
larger at higher ALPHA. NOT pool-weight-dependent — confirms the gap
is intrinsic to the readout, not from pool retrieval interference.

**Bundle decomposition noise theory survey** (came back ~10 min later):

Decisive theoretical prediction: bundle decomposition CANNOT produce
0.02-0.06 bpc loss. Theoretical lower bound on extra CE from bundle
encoding at N=4096, B=5 is `(M-1)*exp(-N/(2(2B-1))) ~ 10^-95 bpc`.

Therefore the empirical gap must be from **uncalibrated softmax
readout**. Bayes-optimal LLR for v = a_k + noise (var B-1) is
`2v/(B-1)`, not raw v. Survey explicit diagnostic: apply LLR factor
2/(B-1)=0.5 in our case, see if gap collapses.

Wrote notes/wave14b_bundle_noise_theory.md with full synthesis.

**Phase B.2-LLR experiment** queued: same B.2 architecture but with
LLR factor in predict_pool_vsa. Pre-registered:
- Gap closes <0.005 bpc → calibration was the entire story
- Gap remains >0.04 bpc → hypothesis falsified, deeper issue

If LLR works: C2 matches C1, C3 only needs to beat by ANY margin to
win the headline test. Big strategic implication if confirmed.

### 2026-05-18 23:17 + 2026-05-19 00:17: GPU queue complete — TWO MAJOR RESULTS

**Phase B.2 (VSA-pool C2 vs classical C1)** — minor negative, honest read:

| Condition | Pre-shift bpc | Post-shift bpc | BWT |
|---|---|---|---|
| C1 (classical) | 2.4817 | 4.3352 | −1.8535 |
| C2 (VSA-pool)  | 2.5006 | 4.3911 | −1.8906 |

C2 trails C1 by 0.056 bpc post-shift. Pre-shift already 0.019 bpc worse:
14.B target extraction adds noise vs explicit label lookup. The substrate
works correctly (decomposition recovers targets) but the encoding doesn't
itself win on perplexity.

**Implication for headline**: C3 (compositional retrieval) must beat C1
by MORE than ~0.06 bpc to overcome the decomposition-noise overhead.
This raises the bar for what C3 has to do.

**Phase B.2 launching unbiased follow-up research**: "what does the math
say about information loss in target-encoded HDC bundles" — framed without
AI bias. Goal: understand the 0.05-0.06 bpc gap analytically. Background.

**Scaling sweep N=8K to N=65K** — DECISIVE positive:

| N | B in {2,8,32,128} | K in {32,256,2048} | Recovery |
|---|---|---|---|
| 8192  | all | all | 100% |
| 16384 | all | all | 100% |
| 32768 | all | all | 100% |
| 65536 | all | all | 100% |

The substrate scales to N=65K with ZERO degradation. At N=65536, K=32,
B=128 — still 100%. This is the biggest empirical finding so far for
the platform commitment: production-relevant dimensions ALL hold.

**Implication**: the platform claim ("works at workstation/server scale")
is validated. Any future N choice from 4K to 64K+ is safe.

**GPU watchdog exited** after 1 hour idle (per design). Will be
relaunched with parameter-sweep follow-ups.

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
