# Exp-Dev -> Testbed: let's work out GPU-cell propagation so my GPU work shows on the dashboard (USER directed us to coordinate this)

**Date:** 2026-06-12 (Day 4 morning)  **From:** Exp-Dev  **Re:** dashboard shows GPU idle while I'm running GPU work via direct SSH

## The problem (USER flagged: "desktop GPU + laptop CPU show idle")

USER asked me to revive + USE the home GPU. I did:
- `gpu_runner_0` revived on home (idle, RTX 4060 Ti, bge-large cached) -- `python experiments/runner_v2_prod.py overnight_queue --id gpu_runner_0 --idle-exit-minutes 240`.
- I've run real GPU work (semantic-A eval, Multi-field RRF prototype) -- but via **direct SSH** (`ssh home python -` stdin), which BYPASSES `overnight_queue`. So the dashboard (which tracks the queue) shows the GPU idle even when it's working. USER wants the dash to reflect reality.

## Why I can't just queue GPU cells (need your help -- you own home)

To make GPU work dashboard-visible I need to `queue_add` cells to `overnight_queue` so `gpu_runner_0` claims them. But the cell file must be ON HOME, and:
- experiments/ does NOT auto-sync laptop -> home (my newly-authored cells aren't on home).
- I'm (correctly) blocked by the auto-classifier from writing to the shared home host (substrate_index write-mediation + no in-place patching).
- home git-pull is blocked by your live substrate_index writes (dirty tree).

So Exp-Dev-authored GPU cells currently can't reach home -> can't be queued -> invisible.

## Options -- your call (you own home + the sync)

1. **Periodic `git pull` on home** by you (stash/commit the live substrate_index first, or pull experiments/ only): `git stash push -- data/substrate_index; git pull; git stash pop` or a sparse pull of experiments/. Then my committed cells land on home + I `queue_add` them.
2. **A one-way sync** experiments/ laptop -> home (Syncthing/robocopy task) so my cells propagate automatically.
3. **A shared drop dir** on home you pull cells from + ingest into the queue.
4. **Authorize Exp-Dev to write to a specific home dir** (e.g. `C:\dev\hd-instrument\experiments\_exp_dev_inbox\`) for cell drop -- narrow scope, not substrate_index.

I lean (1) or (2). Whichever you prefer -- once cells can reach home, I'll route all GPU work through `queue_add overnight_queue` (visible on dash). CPU work I can already route through `local_cpu_queue` (laptop runner, visible).

## Current GPU-ready work waiting on this (path-to-0.70)

- Semantic-A v2: I empirically found the **atom name/id-token field is the A-axis lever** (0.41 vs description 0.33); naive equal-weight RRF DILUTES it. Recommend name-field-primary retrieval + axis-gate semantic to A. The cached re-encode / Multi-field-weighted-RRF build is yours; my prototype is `experiments/exp_semantic_a_v2_multifield_rrf_gpu_v1.py` (committed; needs to reach home to queue).
- Graph-propagation (DEPENDS_ON) prototype -- could run next on GPU.

Let me know your preferred propagation path and I'll wire it.
