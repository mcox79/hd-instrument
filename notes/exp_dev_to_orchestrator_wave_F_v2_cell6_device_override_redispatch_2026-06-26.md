# exp_dev -> orchestrator: Wave F v2 Cell 6 device-override redispatch READY

**Date:** 2026-06-26
**From:** exp_dev (cell author)
**To:** hdi_orchestrator (dispatch)
**Type:** Wave F v2 redispatch (single cell)
**Sister fix:** SoftHebb upstream NaN fix landed same turn (do NOT
redispatch Cell 1 hub-spoke v3 -- waiting on Cell H' confirmation per
coordinator directive)

## Summary

Cell 6 (`substrate_compose_lock_in_frequency_stacking_v1`) was rerouted to
remote_cpu_queue in Wave F (2026-06-25) to escape an 8GiB GPU OOM. The
reroute relied on `DEVICE = cuda if available else cpu`, but the consumer
machine has CUDA visible -- so the cell ran on CUDA anyway and OOM'd
identically.

v2 fix: added `--device {auto,cpu,cuda}` argparse flag (default `auto`
preserves backward compatibility). With `--device cpu`, DEVICE is forced
to `torch.device("cpu")` regardless of `torch.cuda.is_available()`.

## Cell

- **Anchor:** `substrate_compose_lock_in_frequency_stacking_v1`
- **File:** `experiments/exp_substrate_compose_lock_in_frequency_stacking_v1.py`
- **Prereg:** `preregs/2026-06-24_substrate_compose_lock_in_frequency_stacking_v1.md` (Wave F v2 device-override section appended)
- **Commit:** `0176cdce` (cell + prereg)

## Dispatch spec

| Field          | Value                                                      |
|----------------|------------------------------------------------------------|
| Queue          | `remote_cpu_queue`                                         |
| Timeout        | `10800` (3h; was 7200s GPU, ~3-5x slower on CPU, 1.5x safety) |
| Extra args     | `--device cpu`  (MANDATORY -- without this it'll OOM on CUDA again) |
| Anchor         | `substrate_compose_lock_in_frequency_stacking_v1`          |
| Script         | `experiments/exp_substrate_compose_lock_in_frequency_stacking_v1.py` |

Suggested invocation:

```bash
python tools/queue_add.py remote_cpu_queue \
    substrate_compose_lock_in_frequency_stacking_v1 \
    experiments/exp_substrate_compose_lock_in_frequency_stacking_v1.py \
    --prereg preregs/2026-06-24_substrate_compose_lock_in_frequency_stacking_v1.md \
    --timeout 10800 \
    --extra-args="--device cpu"
```

(If `queue_add.py` does not yet support `--extra-args`, set
`HDLAB_DEVICE=cpu` in the runner env, OR append `--device cpu` to the
command line that the runner constructs.)

## Self-test PASS evidence

```
$ .venv/Scripts/python.exe experiments/exp_substrate_compose_lock_in_frequency_stacking_v1.py --self-test
[selftest] PASS shared!=lockin (diff=3.053e+03) Ws=3 logits_ok bpc_uniform_ok
[self-test] passed; exiting

$ .venv/Scripts/python.exe experiments/exp_substrate_compose_lock_in_frequency_stacking_v1.py --self-test --device cpu
[selftest] PASS shared!=lockin (diff=3.053e+03) Ws=3 logits_ok bpc_uniform_ok
[self-test] passed; exiting

$ HDLAB_DEVICE=cpu .venv/Scripts/python.exe experiments/exp_substrate_compose_lock_in_frequency_stacking_v1.py --self-test
[selftest] PASS shared!=lockin (diff=3.053e+03) Ws=3 logits_ok bpc_uniform_ok
[self-test] passed; exiting
```

All three modes PASS (USER smoke embargo respected -- self-test only).

## Disciplines preserved

- Path-scoped commit (cell + prereg in one commit; verification test and
  SoftHebb fix in separate commits).
- ASCII only.
- Backward-compatible default (`--device auto` = original behavior).
- HARD bands, discriminators, arms, config UNCHANGED.
- Self-test confirms numerical correctness; no fake -- same `diff=3.053e+03`,
  `Ws=3`, `logits_ok`, `bpc_uniform_ok` as Wave F.

## Other Wave F cells -- no action needed

| Cell | Status |
|------|--------|
| Cell 1 (hub_spoke_E1_v3) | SoftHebb upstream FIXED (commit `3e3a7421`); DO NOT redispatch -- wait for Cell H' Olshausen-Field confirmation, then author v4 |
| Cell 2 (compose_heterogeneous_v3) | Wave F dispatched on GPU; unaffected by device-override issue |
| Cell 5 (role_tagged) | Wave F dispatched on remote_cpu_queue; small enough to not OOM on CUDA fallback; left alone |
| Cell 6 (this cell) | v2 ready for dispatch |

## Commit hashes (this turn)

| Commit     | Scope                                                |
|------------|------------------------------------------------------|
| `3e3a7421` | Fix SoftHebb production NaN in build_spoke_softhebb_gpu |
| `322c9afd` | Add SoftHebb numerical-stability regression test    |
| `0176cdce` | Wave F v2 Cell 6: add --device flag                 |

## Push state

Laptop is harness-DENIED for push; relies on `hd_metrics_sync` task. Push
lane was healthy at `ba8beabe`; the three new commits are local-only until
sync runs.

## Recommendation: Cell 1 v4 sequencing

**Recommend WAIT for Cell H' (Olshausen-Field) to confirm before authoring
Cell 1 v4.**

Reasoning:
- Cell H' arm 2 (`encoder_olshausen_field`) is a forward-only SoftHebb
  variant in the W-matrix form (W += eta * Y.T @ X, not the codebook-row
  index_add form Cell 1 uses). It already has per-batch NaN guards and a
  char-trigram fallback.
- If Cell H' confirms the broader Olshausen-SoftHebb regime works
  end-to-end (BPC + anisotropy + label-free generalization), it validates
  the upstream math family AND gives Cell 1 v4 a known-good baseline to
  compare against.
- If Cell H' HARD_FAILs, we learn whether the fix is sufficient or whether
  the whole forward-only-Hebb-on-text8 approach is the wrong family. We
  avoid burning a Cell 1 v4 GPU-overnight slot pre-emptively.
- The Cell 1 v3 sister-fixes (FIX 1 health-check, FIX 2 MRC bundle, FIX 3
  task-signal gates) are sound and orthogonal to the SoftHebb math fix.
  v4 = v3 + fixed SoftHebb upstream + (potentially) Cell H'-validated
  hyperparams. Sequencing this way costs ~1-2 days and de-risks the v4
  dispatch substantially.

## Action for hdi_orchestrator

Dispatch ONLY Cell 6 v2 (`substrate_compose_lock_in_frequency_stacking_v1`,
remote_cpu_queue, 10800s, `--device cpu`) in a follow-up turn. Other
Wave F cells already dispatched or held per above. Cell 1 v4 authoring
gated on Cell H' verdict (separate routing event).
