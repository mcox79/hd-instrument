# Pre-reg: substrate_compose_lock_in_frequency_stacking_v1
Date: 2026-06-24
Author: exp_dev (Wave E retry)
Routing: remote_cpu_queue via orchestrator handoff (was GPU; OOM-reroute -- see below)
Lane: 1 (substrate-native; controls + intra-arm ablations)

## Barrier addressed
Barrier 3 (alt): cross-layer independent W (cell 7) gave +0.376 BPC over the
collapse arm. Can SAME W carry multiple plasticity mechanisms via temporal
frequency-division separation (lock-in modulation at distinct frequencies),
rather than requiring spatial separation across distinct W matrices?

## USER directive
Temporal frequency-division separation: each plasticity rule rides a different
lock-in modulation frequency on the SAME W. Demodulate at target frequency to
recover that mechanism. Brain: theta-gamma nested oscillations. Engineering: FDM.

## Verify-the-referent (Skunkworks N1 discipline)
- exp_lock_in_amplifier_hd_frequency_smoke_v1/metrics.json: verdict=HARD_PASS;
  elapsed=146.8s; cited as the substrate primitive that lock-in works. SAFE.
- USER cited "~7.54 from same-W stacking" for ARM_BASELINE_SHARED_W. Closest
  available referent in compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield
  is ARM_FULL_JOINT_COMPOSE bpc=7.8919 (collapse) NOT 7.54. FLAGGED IN PREREG.
  We measure ARM_BASELINE_SHARED_W IN-CELL using ALL three mechanisms summed
  with no separation (cf-RPE + STDP + Hebbian onto same W). The expected band
  is [7.30, 7.95] depending on whether collapse happens at our config.
- USER cited "7.17 from Cell 7" for ARM_CROSS_LAYER_INDEPENDENT_W. Closest
  referents: substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1
  ARM_CFRPE_STDP_HETEROGENEOUS=7.1654 (HARD_PASS); compose_fair_harness
  ARM_BASELINE_NO_CLEANUP=7.1813. Either is within +/- 0.05 of 7.17. SAFE.
  We measure ARM_CROSS_LAYER_INDEPENDENT_W IN-CELL.

## Mechanism
- text8; V=4000; word2vec sparse-bipolar encoder (f=0.05); N=8192.
- 3 mechanisms (Hebbian rank-1; cf-RPE -- contextual-feedback residual update;
  STDP -- spike-timing-dependent with hardcoded asym window).
- LOCK-IN-FREQ separation: each mechanism's contribution to W is modulated by
  cos(2*pi*f_mod*t) where f_mod is mechanism-specific:
    f_mod_Hebbian = 1.0
    f_mod_cfRPE = 2.5
    f_mod_STDP  = 5.0
  At training time t, W += outer(target_t, src_t) * w_mech * cos(2*pi*f_mod_mech * t).
  At retrieval, query is REPEATED P times (P=8) at phases p=0..P-1:
    pred_p = roll_or_apply(W, p) * cos(2*pi*f_mod_target*p/P)
  Demodulated pred = (2/P) * sum_p pred_p picks out only the target-freq mechanism.

## Arms (4)
1. ARM_BASELINE_SHARED_W       -- control: 3 mechs into same W, no separation. EXPECTED collapse band [7.30, 7.95].
2. ARM_CROSS_LAYER_INDEPENDENT_W -- control: 3 separate W matrices summed at retrieval. EXPECTED [7.10, 7.25].
3. ARM_LOCK_IN_FREQ_SEPARATED  -- same W; lock-in modulation; demod at retrieval.
4. ARM_LOCK_IN_PLUS_CROSS_LAYER -- spatial + temporal multiplicative.

## Config
- N=8192, V=4000, N_TRAIN=100000, 3 seeds [7,17,23].
- P_demod = 8 (lock-in phases at retrieval).
- TEMP_GRID extended for joint sweep.
- GPU torch.cuda; batched matmul; chunked ingest.

## HARD bands
- HARD_PASS_CHAIN_GRADE: best lock-in arm BPC <= 6.95 AND beats SHARED_W by >= 0.40 bits.
- HARD_PASS: best lock-in BPC <= 7.10 AND beats SHARED_W by >= 0.30 bits.
- HARD_FAIL: lock-in within +/- 0.05 of SHARED_W (no separation lift).
- MIDDLE_BAND: otherwise.

## Sanity rails
- ARM_BASELINE_SHARED_W within [7.20, 7.95] (we accept a wide band since the cited 7.54 wasn't directly observed in audited referents; we report observed value and flag if outside).
- ARM_CROSS_LAYER reproduces 7.17 +/- 0.05 (rail from cfRPE_STDP_HETEROGENEOUS=7.1654).
- READOUT_DEGENERATE gate: raw_bpc_at_T1_L1 within +/- 0.5 of -log2(1/V) AND no arm HP -> DEGEN flag.

## Discriminator
- If ARM_LOCK_IN > ARM_BASELINE_SHARED by >= 0.30: lock-in works on single W (temporal separation viable).
- If ARM_LOCK_IN_PLUS_CROSS_LAYER > max(ARM_LOCK_IN, ARM_CROSS_LAYER) by >= 0.05: spatial + temporal multiplicative.
- If ARM_LOCK_IN <= ARM_BASELINE + 0.05 AND ARM_CROSS_LAYER passes: spatial-only is the lever (negative lock-in result).

## Timeout budget
- 10800s (3h) on remote_cpu_queue; 4 arms x 3 seeds; demod is the heavy step.
- (Was 7200s GPU; CPU is ~3-5x slower for matmul; 1.5x safety margin baked in.)

## Routing
- remote_cpu_queue via orchestrator handoff (Wave F reroute).
- Anchor: substrate_compose_lock_in_frequency_stacking_v1 (no _n suffix).

## Wave F reroute justification (2026-06-25)
Initial GPU dispatch HARD_FAILed with CUDA OOM on 8GiB GPU: tried to allocate
3.05GiB on top of 4.22GiB already pinned. Root cause: ARM_LOCK_IN_PLUS_CROSS_LAYER
holds 3 separate W matrices simultaneously (3 * N_DIM^2 * 4 bytes = 768MB at
N=8192 fp32) plus encoder state plus per-batch matmul intermediates (tgt @ src
broadcast at INGEST_CHUNK=4096). At v1 full config this exceeds 8GiB ceiling.
CPU has 64GB RAM (8x headroom); mechanism (lock-in frequency stacking) is
matmul-bound but not GPU-bound; CPU is correct fallback. Discriminators and
HARD bands UNCHANGED -- only wall-time and routing changed.

## Wave F v2 device-override fix (2026-06-26)
Wave F initial reroute relied on `DEVICE = cuda if available else cpu` to
auto-fall-back. This was INCORRECT: the remote_cpu_queue consumer machine
DOES have CUDA visible, so the cell ran on CUDA -> OOM at 8GiB anyway. Queue
routing alone does not enforce in-process device choice.

v2 fix: added `--device {auto,cpu,cuda}` argparse flag plus `HDLAB_DEVICE`
env var; default `auto` preserves backward compatibility. With `--device
cpu` (or `HDLAB_DEVICE=cpu`), DEVICE is forced to torch.device("cpu")
regardless of torch.cuda.is_available().

Dispatch invocation for v2 MUST include `--device cpu` in the cell argv
when routing to remote_cpu_queue. Self-test PASS on all three modes:
  - default (auto): DEVICE = cpu on laptop (no CUDA) -- PASS
  - --device cpu:   DEVICE = cpu explicit -- PASS
  - HDLAB_DEVICE=cpu env: DEVICE = cpu via env -- PASS

Code change only; HARD bands, discriminators, arms, and config UNCHANGED.
