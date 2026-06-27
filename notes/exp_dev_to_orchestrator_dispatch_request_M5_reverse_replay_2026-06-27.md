# exp_dev -> orchestrator: dispatch request M5 reverse-replay cell

**Authored:** 2026-06-27 by exp_dev (USER NO LOCAL directive)
**Commit:** `2f12bb6a` (bundle: primitives + cell + prereg + drill stub)
**Routing:** remote_cpu_queue (CPU-bound matmul; harness-DENIED push for exp_dev)
**Timeout:** 14400s (4hr)

## Cell + prereg ready for dispatch

- Anchor: `multihop_reverse_replay_backward_sweep_v1`
- Cell: `experiments/exp_multihop_reverse_replay_backward_sweep_v1.py`
- Prereg: `preregs/2026-06-27_multihop_reverse_replay_backward_sweep_v1.md`
- HDLAB_EXP_NAME for dispatch: `multihop_reverse_replay_backward_sweep_v1`

## Smoke gate status: PASS

```
[seed=7] depth=2 A=0.800 B=0.133 C=0.900 D=0.867 E=0.833 F=0.767
[seed=7] depth=3 A=0.633 B=0.100 C=0.700 D=0.833 E=0.667 F=0.700
[seed=7] depth=5 A=0.533 B=0.100 C=0.533 D=0.733 E=0.500 F=0.533
[VERDICT] MIDDLE_BAND_PARTIAL_REVERSE_REPLAY: D-A_lift=+0.1556 C-F_temporal_order=+0.0444
```

Smoke MIDDLE_BAND is expected at V_C=80 (bands calibrated for V_C=200 full-N).
Discriminator alive: F < C by 0.044 absolute at V_C=80; gap should expand at V_C=200.

## Self-test gate: PASS

`python experiments/exp_multihop_reverse_replay_backward_sweep_v1.py --self-test` exits 0.

## Hoisted primitives (chain-grade-validated source, hoisted same-cycle per results-to-application discipline)

1. `hdlab/sequence_memory.py`: `S_back` matrix + `bind_pair_reverse` + `predict_prev` + `bind_sequence_reverse`
2. `hdlab/multi_hop.py`: `bidirectional_chain(kg, start, end_candidates, relations, midpoint_hop=None)`
3. `hdlab/continual.py`: `replay_cycle(..., direction='forward'|'reverse'|'both', W_back=None)`

All 3 primitives sanity-tested (predict_prev recovers magnitude; replay_cycle reverse adds expected outer-sum; bidirectional_chain returns best_Z + best_cos + diagnostics).

## Dispatch command (for Orchestrator)

Push origin/main first (commit `2f12bb6a` is on local main; remote_cpu_queue runner reads origin/main), THEN:

```
python tools/queue_add.py \
    remote_cpu_queue \
    multihop_reverse_replay_backward_sweep_v1 \
    experiments/exp_multihop_reverse_replay_backward_sweep_v1.py \
    --prereg preregs/2026-06-27_multihop_reverse_replay_backward_sweep_v1.md \
    --timeout 14400 \
    --purpose "M5 brain-mechanism cell: reverse-replay backward sweep"
```

## Strategy-route on landing

- HARD_PASS_CHAIN_GRADE_REVERSE_REPLAY -> Skunkworks landed-VET + atomization
- MIDDLE_BAND_PARTIAL_REVERSE_REPLAY -> Skunkworks landed-VET (likely MM)
- HARD_FAIL -> Research 2x post-mortem; route to alternative M-mechanism

## REMOTE VERIFY post-ship (exp_dev TODO after Orchestrator dispatches)

- Confirm cell-spec on remote matches local commit `2f12bb6a`
- Verify metrics path: `data/exp_multihop_reverse_replay_backward_sweep_v1/metrics.json`
- Verify REQUIRED_FIELDS (verdict, verdict_msg, elapsed_s, summary)
