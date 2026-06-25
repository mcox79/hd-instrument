# PRE-REG: substrate_compose_heterogeneous_routing_v3_full_config_rerun

**Date:** 2026-06-25
**Cell:** `experiments/exp_substrate_compose_heterogeneous_routing_v3_full_config_rerun.py`
**Lane:** 1 (substrate-native)
**Routing:** GPU overnight_queue (via hdi_orchestrator handoff; exp_dev push is harness-denied)

## What it tests

v3 rerun of `substrate_compose_heterogeneous_routing_v2_RESCUE_FULL` at SAME
fair-harness rail config. v2_RESCUE_FULL on overnight_queue (2026-06-25T01:19:24Z) landed
`failed` with no artifacts. v2_RESCUE (CPU smaller-scope) landed `HARD_FAIL_PROVENANCE`
because baseline drift was 0.35 from fair_harness rail 7.3065 -- the rail tolerance 0.05
was set INSIDE cross-config noise floor of 0.20-0.45 BPC (per drill cell 9).

Per drill `notes/research_readout_degeneracy_5x_disparate_drill_2026-06-25.md` Cell 9
diagnosis: the rail is correctly recorded but the cell mis-applied it (half-N / half-tokens /
2-seeds vs the rail's N=8192 / 100k / 3-seeds config). v3 reruns at FULL config matching the
rail EXACTLY + adds GPU setup hardening for the silent-failure mode the FULL run hit.

## CHANGES vs v2_RESCUE_FULL

1. **Bands TIGHTENED per drill recommendation:**
   - Sanity rail tolerance: 0.10 -> 0.05
   - CHAIN_GRADE BPC: 6.80 -> 6.95 + CV <= 0.03
   - HARD_PASS BPC: 6.95 -> 7.20
   - HARD_FAIL_DECISIVE: best_het <= baseline (was: all_het >= baseline + 0.05)

2. **GPU setup hardening (vs v2_RESCUE_FULL silent crash):**
   - `_gpu_setup_assert_and_report()` called at startup: `cuda.empty_cache` +
     `mem_get_info` + device-mismatch probe + `cuda.synchronize`
   - D2 atexit handler unchanged (already flushes partials on SIGTERM)
   - `expandable_segments:True` already set via `PYTORCH_CUDA_ALLOC_CONF`

3. **ARM_FREQ_ROUTED_K2 is the lead arm.** v2_RESCUE smoke showed +0.22 BPC differential
   lift. v3 full-config rerun is the decisive test.

## Arms (UNCHANGED from v2; same 4)

1. `ARM_BASELINE_FAIR_HARNESS` (sanity rail at fair_harness 7.3065)
2. `ARM_THETA_PHASE_TWO_W`
3. `ARM_FREQ_ROUTED_K2` (lead arm per v2_RESCUE smoke +0.22 BPC differential)
4. `ARM_ORTHOG_SUBSPACE`

## HARD bands

- `HARD_PASS_CHAIN_GRADE`: best het BPC <= 6.95 AND beats BASELINE by >= 0.20 BPC AND
  CV <= 0.03 AND `sanity_rail OK` (baseline within +/-0.05 of 7.3065)
- `HARD_PASS`: best het BPC <= 7.20 AND beats BASELINE by >= 0.10 BPC AND sanity_rail OK
- `HARD_FAIL_PROVENANCE`: baseline rail drift > 0.05 (sanity_rail FAIL = re-investigate
  upstream)
- `HARD_FAIL_DECISIVE`: best het <= BASELINE AND sanity_rail OK (heterogeneous arch refuted)

## Production config (MATCHES fair-harness rail EXACTLY)

- N_DIM = 8192 (NOT 4096)
- V = 4000 (text8)
- N_TRAIN = 100_000 (NOT 50k)
- N_HELD = 20_000
- SEEDS = [7, 17, 23] (NOT 2)
- word2vec sparse-bipolar f = 0.05
- Timeout: 7200s (overnight_queue GPU)

## Self-test evidence

`.venv/Scripts/python.exe experiments/exp_substrate_compose_heterogeneous_routing_v3_full_config_rerun.py --self-test`
returns PASS on ST1-ST16 including:

- ST1 cf-RPE shrinks error 1.0 -> 0.1
- ST2 STDP antisymmetry
- ST3 Gram-Schmidt orthogonal split
- ST4 freq-ranks
- ST5 hebbian baseline logits
- ST6 theta_phase encode/retrieve correlation
- ST7 freq_routed counts
- ST8 orthog_subspace residual + cross-grad
- ST9 arm logits diversity (theta/freq/orthog all distinct)
- ST10 joint_sweep
- ST11 sparsify_bipolar_gpu nnz
- ST12 LAMBDA_GRID excludes 0.0 (META C7)
- ST13 LLM call counter == 0
- ST14 ARMS consistent (4 arms)
- ST15 D2 atexit handler registered
- ST16 scope-reduction sanity

## Cites

- `notes/research_readout_degeneracy_5x_disparate_drill_2026-06-25.md` (drill that
  identified the rail-config-provenance mismatch + recommended fix)
- `experiments/exp_substrate_compose_heterogeneous_routing_v2_RESCUE_FULL.py` (v2 base;
  failed run on overnight_queue)
- `experiments/exp_substrate_compose_heterogeneous_routing_v2_RESCUE.py` (v2 smaller-scope;
  HARD_FAIL_PROVENANCE)
- `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` (rail 7.3065 at this exact config)

## Honest scope

- Tests 3 heterogeneous-routing composition architectures (theta-phase / freq-routed K=2 /
  orthogonal subspace) vs fair-harness Hebbian baseline at MATCHING fair-harness rail config.
- Does NOT test K>2 routing variants; modern-Hopfield cleanup not stacked here.
- If baseline drifts > 0.05 of 7.3065 at this config, encoder/Hebbian pipeline has a
  separate provenance issue (NOT scale-mismatch). v3 surfaces this honestly via
  HARD_FAIL_PROVENANCE.
