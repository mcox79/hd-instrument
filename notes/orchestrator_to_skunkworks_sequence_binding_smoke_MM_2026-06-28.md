# orchestrator -> skunkworks: sequence_binding K-cliff CPU smoke MIDDLE_BAND atomize 2026-06-28

**Filed:** orchestrator (Opus 4.7 1M, agent-spawn) 2026-06-28 ~17:50Z
**Standing rule:** `feedback_every_failure_skunkworks_plus_intuitive_explanation_USER_STANDING_2026-06-28`
**Subject:** smoke seed_7 verdict = MIDDLE_BAND on CPU
**Cell:** `experiments/exp_substrate_sequence_binding_K_cliff_phase_diagram_v1_seed_7.py`
**Core:** `experiments/_substrate_sequence_binding_K_cliff_phase_diagram_v1_core.py`
**Pre-reg:** `preregs/2026-06-28_substrate_sequence_binding_K_cliff_phase_diagram_v1.md`
**Metrics:** `data/exp_substrate_sequence_binding_K_cliff_phase_diagram_v1_seed_7_smoke/metrics.json`

## Atomization request: MM (mechanism_characterization)

### Verdict from disk

```
verdict: MIDDLE_BAND
verdict_msg: K_cliff_min=100 loc=(4096, 0.3) | cliffs=4/12 | avg_arms_diff=0.167 |
             low_k_high_n_floor=False | cliff_observable=True |
             monotone_tags=1/3 | saturated=False | regime_flip=False
elapsed_s: 11.6 | seed: 7 | backend: torch.cpu | observed_n: 36 / expected_n: 36
```

### Cell-author's intuitive explanation (load-bearing)

Smoke ran on laptop CPU with Q=2 (smoke discretization); the substrate's per-arm top1 saturates to {0, 0.5, 1.0} bins at Q=2 — masking the actual cliff slope. Q=10 (full) gives 11 distinguishable bins per arm, resolving the cliff curve. The MM verdict is **EXPECTED at Q=2 by design**; cell-author flagged this is NOT a real mechanism failure.

Evidence in metrics.json:
- (K=10, N=2048, tag=0.1): SUBSTRATE=0.5, RANDOM=0, SHUFFLE=0 → arms_diff=0.5 (mechanism DOES fire at low load, but Q=2 means "0/2" or "1/2" only)
- (K=10, N=16384, tag=0.1): SUBSTRATE=0.5 — same
- All higher K/tag combos collapse to 0.0 because Q=2 hits Bernoulli floor

The cliff at K=100 (N=4096, tag=0.3) is observable but coarse-grained. cliffs=4/12 falls in MB band (3-5).

### Full-Q10 dispatch path BLOCKED

Attempted GPU smoke dispatch via `bash tools/orchestrator/queue_add.sh overnight_queue ... 1800` AFTER patching siblings with top-level `import torch` for PROT-020 gate. Gate passed, SCP+SSH succeeded, BUT **GPU self-test FAILED at `_self-test` with `SUBSTRATE=0.000 should exceed RANDOM=0.000 at low-K high-N`**.

```
[gate] PROT-020 OK: script imports torch (GPU queue routing justified)
[selftest] SELFTEST_FAIL: selftest: SUBSTRATE=0.000 should exceed RANDOM=0.000 at low-K high-N
GATE_FAIL: --self-test exit=1 (after 4.7s)
```

CPU smoke shows SUBSTRATE=0.5 at low-K high-N; GPU returns 0.0. This is a **real GPU-backend code-path bug** (likely in the cuda variant of bind/unbind or codebook generation in the core). Not a smoke-discretization artifact.

### Recommend

1. Atomize CPU smoke as MM per standing rule (single seed; cell ran clean; cliff observable but coarse-grained at Q=2).
2. Flag GPU self-test failure to cell-author for repair before any FULL dispatch on overnight_queue. Per `DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26`, dispatching --skip-smoke FULL siblings when self-test fails on target backend would discard ~5h x 3 GPU-hours.
3. Do NOT dispatch full siblings to overnight_queue until GPU backend path is repaired. Alternative: route 3 FULL siblings to `remote_cpu_queue` (numpy/torch.cpu path proven via local smoke), accepting longer wall-clock.

## Status log entry

Logged at `data/orchestrator_status_log.jsonl` ts=2026-06-28T17:50Z event=K_cliff_smoke_MM_GPU_blocked.
