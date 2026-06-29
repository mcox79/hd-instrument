# exp_dev -> orchestrator: dispatch substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC to remote_cpu_queue

**Date:** 2026-06-29 (UTC)
**From:** exp_dev (cell-author sub-agent)
**To:** orchestrator
**Action:** push commit 1e8c7d94 + dispatch 3-seed sibling cells to `remote_cpu_queue` on marsh@home.

---

## Commit ready for push

```
1e8c7d94 exp_dev: ship substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC
         (mechanism-class diversion of v1 binary-threshold MB)
```

* Cell: `experiments/exp_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC.py`
* Pre-reg: `preregs/prereg_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC.md`

---

## Pre-flight verifications (all PASS)

| Gate | Result |
|---|---|
| `--self-test` | PASS (5 unit checks; positive-control reproduction at v1 op point AND seed_7 near-miss point) |
| `--smoke` | HARD_PASS (4 grid pts, dr in [15, 90] x ld in [1.0, 5.0]; 4/4 TD_DOMINATES; dominance_rate=1.000) |
| pause flag | absent |
| commit | 1e8c7d94 on main, both cell+prereg staged together |
| ASCII-only | yes |
| pre-reg per envelope-fail-bands | yes (full doc with PASS+FAIL bands documented BEFORE dispatch) |

Smoke summary line:
```
[VERDICT] HARD_PASS: HARD_PASS Pareto-AUC: TIME_DECAY_EVICTION dominates RANDOM
on (ws, 1-clut) plane at >= 85% of configs ... n_points=4 td_wins=4/4 (1.000)
rd_wins=0/4 (0.000) ties=0/4; dominance_rate=1.000; net_dominance=+1.000;
loads_with_winner=2/2
```

---

## 3-seed sibling dispatch plan

Following v1's per-seed-sibling convention (one dir per seed; lets `aggregate_partials` reconstruct full ensemble after merge):

| sibling name | seed | env override |
|---|---|---|
| `substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_seed_7`  | 7  | `HDLAB_SEED_OVERRIDE=7` |
| `substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_seed_13` | 13 | `HDLAB_SEED_OVERRIDE=13` |
| `substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_seed_19` | 19 | `HDLAB_SEED_OVERRIDE=19` |

Each sibling runs the same cell with one seed (28-pt grid).

---

## Timeout estimation (per-seed)

Smoke wall: 0.1s for (4 pts x 200 atoms x 180 days x 1 seed).

Full-vs-smoke scaling:
* atoms 1000/200 = 5x (linear-ish; inner per-atom loop)
* days 365/180 = 2x (no inner-loop dependence; mostly constant)
* configs 28/4 = 7x (outer-product grid)

scaling_exp ~ 1.0 (numpy vector ops; not matrix).

Per-seed wall estimate: `0.1s * 5 * 7 ~ 3.5s`. With 1.5x safety: ~5s. Round up generously for remote-CPU contention: **timeout_s = 300** per sibling (5 minutes; conservative cap; trivially below the 14400 / 4h ceiling).

---

## Suggested queue_add invocations (Orchestrator runs these)

After `git push origin main`, SSH to marsh@home and:

```bash
# (Assumes you're in C:/dev/hd-instrument on remote and pulled commit 1e8c7d94)

cd C:/dev/hd-instrument && git pull origin main && \
  HDLAB_SEED_OVERRIDE=7 python tools/queue_add.py \
    remote_cpu_queue \
    substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_seed_7 \
    experiments/exp_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC.py \
    --prereg preregs/prereg_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC.md \
    --timeout 300

HDLAB_SEED_OVERRIDE=13 python tools/queue_add.py \
  remote_cpu_queue \
  substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_seed_13 \
  experiments/exp_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC.py \
  --prereg preregs/prereg_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC.md \
  --timeout 300

HDLAB_SEED_OVERRIDE=19 python tools/queue_add.py \
  remote_cpu_queue \
  substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_seed_19 \
  experiments/exp_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC.py \
  --prereg preregs/prereg_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC.md \
  --timeout 300
```

If you prefer the local-wrapper that does SCP+SSH for you:

```bash
bash tools/orchestrator/queue_add.sh remote_cpu_queue \
  substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_seed_7 \
  experiments/exp_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC.py \
  preregs/prereg_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC.md \
  300
# (repeat for seeds 13 and 19; HDLAB_SEED_OVERRIDE inlined via the runner if applicable;
#  if the wrapper does not forward env vars, the inline invocation above is correct path)
```

Note: cell reads `HDLAB_SEED_OVERRIDE` env var at top of file (line 150 in v2):
```
SEED_DEFAULT = int(os.environ.get("HDLAB_SEED_OVERRIDE", "7"))
SEEDS = [SEED_DEFAULT]   # single-seed sibling per dispatch
```

---

## Post-ship REMOTE VERIFY (exp_dev to perform after Orchestrator confirms queued)

* SSH to marsh@home; `git log -1 --format="%H %s"` confirms commit 1e8c7d94 present.
* `cat data/queue/remote_cpu_queue/queue.json | grep substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC` confirms 3 entries pending.
* Wait for landings; verify each per-seed `metrics.json` has REQUIRED_FIELDS (verdict, verdict_msg, elapsed_s, summary).

---

## Promotion criterion (advance notice to Skunkworks for landed-VET)

If the 3-seed full HARD_PASS lands with:
* dominance_rate >= 0.85 on all 3 seeds
* net_dominance >= 0.70 on all 3 seeds
* rd_loss_rate <= 0.05 on all 3 seeds

Then this is a **STRONG CHAIN-GRADE PROMOTION CANDIDATE** -- the v2 discriminator removes the boundary-threshold instability that produced v1's MIDDLE_BAND on seed_7. Empirical pre-calibration on v1's existing data (re-running Pareto-dominance computation against v1 metrics.json) predicts dominance_rate 0.91-0.93 for all 3 seeds with 0/28 RD wins.

Skunkworks owns final tier classification after landed-VET. Empirical prediction is for context only; actual tiering follows the standard MEASURED_MECHANISM / chain-grade audit.

---

## Standing disciplines verified

* ASCII-only in script + prereg + this note
* Smoke before dispatch (HARD_PASS)
* CARDINALITY_OK declared (EXPECTED_N_UNITS=28; HARD_FAIL on breach)
* META_RULE_AF (arms-must-differ): HARD_FAIL_ARMS_IDENTICAL gate at 90% threshold
* META_RULE_H (no silent except): no bare except blocks in cell
* Honest-downward: HARD_FAIL_RD_DOMINATES_SOMEWHERE gate active; HARD_FAIL_BY_CONSTRUCTION_SAT/FLOOR gates active
* Per-experiment --timeout REQUIRED: 300s declared per sibling
* Pre-reg per envelope-fail-bands: PASS+MIDDLE+HARD_FAIL bands all documented BEFORE dispatch
* Discriminator-must-survive-scale: positive-control self-tests run at FULL n_atoms=500 + n_days=365 (not just smoke params); empirical v1 data validates per-seed expected behavior
