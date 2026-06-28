# exp_dev -> orchestrator: dispatch substrate_wm_multibank_K_cliff_phase_diagram_v1 (3 chunked seeds) + smoke to overnight_queue (GPU)

**Date:** 2026-06-28
**Pre-reg:** `preregs/2026-06-28_substrate_wm_multibank_K_cliff_phase_diagram_v1.md`
**Commit:** see git log (this routing note committed in same commit as cells + prereg)

## Why this comes to you (route)
- GPU MANDATE strict on FULL (Fix #24): N_DIM=8192, K up to 65536, fp16 storage + nvidia-smi util sampling. Local has NO CUDA -> cannot smoke on GPU here.
- Push is harness-DENIED to me; both queues require remote push.
- Cell architecture per USER 2026-06-28 chunked-seeds directive: 3 sibling files, one seed each, survives runner death.

## Local CPU pipeline-validation (pre-route)
- Self-test: ALL 12 cases PASS on all 3 sibling cells (seed 7, 13, 19). Cell self-tests cover bipolar / bank_overlap mechanics / SUBSTRATE arm end-to-end / RANDOM floor / chunked-argmax / OOM detector / VRAM probe / routing_noise degradation / arms_differ_sha256 / cardinality math.
- Local CPU smoke (seed_7): pipeline runs end-to-end. Early partials confirm:
  - (K=4096, ov=0.0, rn=0.0): SUBSTRATE=1.0000 RANDOM=0.0000 (margin=1.0000)
  - (K=65536, ov=0.0, rn=0.0): SUBSTRATE=1.0000 RANDOM=0.0000 (margin=1.0000; CLEAN K=65536 surprisingly saturates)
  - (K=4096, ov=0.3, rn=0.15): SUBSTRATE=1.0000 RANDOM=0.0000 (high overlap+noise at low K still saturates)
  - K=65536 high-noise + K=16384 mid-noise pending at file time (will update on land or in landed-VET note).
- arms_differ_sha256 distinct on all observed points. Zero LLM calls. cardinality_ok=True for 6 of 10 units so far.

## Dispatch ask

### Phase 1 (BLOCKING smoke gate on GPU)
Please dispatch ONE GPU smoke first to validate Fix #24 gpu_util_p50 >= 50%:

```bash
bash tools/orchestrator/queue_add.sh overnight_queue \
  substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1_smoke \
  experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1.py \
  preregs/2026-06-28_substrate_wm_multibank_K_cliff_phase_diagram_v1.md \
  1800
```

After smoke lands, verify on the metrics.json:
- `verdict == "SMOKE_PASS"`
- `gpu_util_p50 >= 50.0`
- `cardinality_ok == True` (10 units = 5 corners x 2 arms)
- `detail.arms_differ_count == 5` (per-point arms distinct)
- `n_llm_calls == 0`
- `n_pass >= 2` AND `n_saturate >= 1` AND (`n_floor + n_probe_cliffs >= 1`)

### Phase 2 (FULL after SMOKE_PASS)
On SMOKE_PASS, dispatch all 3 chunked seed FULL cells. Each runs 45 phase points (5 K x 3 overlap x 3 noise) x 2 arms = 90 units. ETA ~3-5 min/point on GPU -> ~3-4h per seed; chunked architecture survives runner death (only loses current seed).

```bash
bash tools/orchestrator/queue_add.sh overnight_queue \
  substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1 \
  experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1.py \
  preregs/2026-06-28_substrate_wm_multibank_K_cliff_phase_diagram_v1.md \
  18000

bash tools/orchestrator/queue_add.sh overnight_queue \
  substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_13_v1 \
  experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_13_v1.py \
  preregs/2026-06-28_substrate_wm_multibank_K_cliff_phase_diagram_v1.md \
  18000

bash tools/orchestrator/queue_add.sh overnight_queue \
  substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_19_v1 \
  experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_19_v1.py \
  preregs/2026-06-28_substrate_wm_multibank_K_cliff_phase_diagram_v1.md \
  18000
```

Per-experiment timeout = 18000s (5 hours). Justification: 45 points x ~3-5 min GPU each = ~3-4h; +50% margin per queue_add.py guidance.

## Expected FULL output per seed
- `data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_<N>_v1/metrics.json`
- `phase_map` field: list of 45 entries with {K, bank_overlap, routing_noise, top1_substrate, top1_random, arms_differ, verdict_tier, saturation, cliff_marker}
- Headline: `cliff_per_ov_rn` mapping {"ov=0.00_rn=0.00": 65536, "ov=0.10_rn=0.05": 32768, ...}
- HP_VRAM_PROBE_BREACH entries (if any) are CLIFF MARKERS counted toward cardinality, NOT failures.

## Cliff prediction (from CRLB pre-validation)
- Bank-routing SNR ∝ 1/sqrt(K); drops 4x from K=4096 (snr=7.92) to K=65536 (snr=1.98).
- Cliff expected at (high K) x (high overlap) x (high noise) combinations.
- Surprising local-smoke evidence: clean K=65536 saturates -> cliff is overlap+noise driven, not K-alone driven.
- Phase-coherence (F6): cliff K should be monotone-decreasing in (overlap+noise).

## REMOTE VERIFY ask (post-dispatch)
- 3 sibling scripts + prereg on remote at the committed hash.
- `queue.json` shows 4 entries (1 smoke + 3 full) on remote, NOT just local sentinel.
- Confirm `nvidia-smi` accessible from the runner (gpu_util_p50 measurement depends on it).

## Coordination
- Skunkworks: notify on each seed landing for landed-VET (chain-grade-eligible: WM multibank K-cliff phase diagram extension to K=65536 + overlap/noise axes; 3-seed aggregation grade).
- Research: aware via this routing-note (sub-agent spawn architecture; routing per Orchestrator's lane). Layer-2 phase operations gated on this Layer-1 phase data.

## VRAM note
- Estimated eval-peak at (K=65536, fp16, CB=65536, N=8192): ~9.7 GB. If GPU < 12GB, K=65536 may probe-deny -> recorded as cliff_marker (NOT failure). The cell DOES NOT halt on probe-deny (continues to next unit). This is correct cliff detection per discriminator-must-survive-scale.

exp_dev (hdi_exp_dev sub-agent)
