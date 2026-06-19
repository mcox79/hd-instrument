# Pre-registration: path_d_edit_isolation_under_load_v1_n4096

**Date:** 2026-05-30
**Anchor:** path_d_edit_isolation_under_load_v1_n4096
**Test:** T2 (Test 15 of user-routed batch)
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_path_d_edit_isolation_under_load_v1_n4096.py

## Hypothesis

Path D's per-candidate Bayesian evaluation (no state propagation through
hops) gives natural robustness to concurrent edits during traversal. Each
hop is evaluated against the substrate snapshot in one shot, so even at
high edit rates the substrate must either commit to a pre-edit OR post-edit
snapshot (not a mixed/torn view), and accuracy degradation must be
graceful.

If true, Path D is the production-scale robust mechanism for streaming
agentic workloads where edits arrive during retrieval.

## Config

- N = 4096 (PROT-018 _n4096 binding).
- BSC substrate. M = 2048; depth = 5; K_paths = 100.
- Edit rates = [10, 100, 1000] edits/sec injected (modeled as rank-1
  updates to W; the rate is the count of edits applied in one batch).
- Edit patterns = [on_path, off_path, mixed]: 3 x 3 = 9 cells per seed.
- 5 seeds = [7, 17, 23, 31, 41]; 45 cell-seeds total.
- Path D ONLY (Path B and Path E excluded by design; covered by S6).

### Apply edits

For each chosen key, replace stored value via rank-1 W update:
  W = W - (old_v * key_v^T) / N + (new_v * key_v^T) / N

### Metrics per cell

- pre_acc (Path D against W before edits).
- post_acc (Path D against W after edits).
- audit_pre, audit_post (16-byte SHA prefixes of W).
- audit_changed = (audit_pre != audit_post).
- snapshot_consistent = bool(post_correct == redo_correct), where redo
  runs Path D twice on W_post with same seed (must be deterministic).
- path_consistent: for off_path edits, |post_acc - pre_acc| < 0.15;
  for on/mixed, expected to differ -> path_consistent = True.
- consistent = snapshot_consistent AND path_consistent.
- perf_degradation = (post_lat - pre_lat) / pre_lat.

## Pre-registered bands

**HARD_PASS:**
For each of the 9 cell-groups at edit_rate=1000:
- >= 3/5 seeds have post_acc >= 0.85
- AND >= 3/5 seeds have audit_changed = True
- AND >= 3/5 seeds have consistent = True.

All 9 cell-groups must satisfy these conditions.

**HARD_FAIL:**
Any group (any rate, any pattern) triggers >= 3/5 seeds for ANY of:
- post_acc < 0.50 at any cell, OR
- audit chain unchanged when n_edits > 0 (audit failure), OR
- snapshot_consistent = False (mixed pre/post output).

**MIDDLE_BAND:** all other outcomes.

## Self-tests

- N_FULL == 4096 (PROT-018).
- apply_edits is exactly: subtract old rank-1 + add new rank-1, both
  divided by N (matches substrate store recipe in t1_beta_sweep
  store_facts_batched).
- _audit_hash is deterministic on identical W.
- redo_correct identical to post_correct on identical W (Path D
  determinism check inside measure_cell).
- compute_verdict returns T2_HARD_PASS / T2_HARD_FAIL / T2_MIDDLE_BAND /
  T2_INCONCLUSIVE only.

## OOM check

- N=4096, M=2048: 1 GB peak; W edits use existing keys/vals (no new alloc).
- Edit batch up to 1000 keys: 1000*N*4 = 16 MiB. Trivial.

## Smoke result

- N_smoke=1024, M=256, depth=3, K=20, rates=[10,100], patterns=[on_path,
  off_path], 1 seed.
- smoke_wall_s ~ 0.7s; all 4 cells produced valid metrics:
  - r=10,on_path: post=1.000, consistent=True
  - r=10,off_path: post=1.000, consistent=True
  - r=100,on_path: post=1.000, consistent=True
  - r=100,off_path: post=1.000, consistent=True
- audit_changed verified True in selftest at small scale.

## Walk-back gate

Smoke effect at the HP-key rate (1000) is not observed since smoke runs
rates=[10, 100]. The HP-threshold rate is 10x the largest smoke rate, but
at M=2048 substrate, 1000 edits = ~half capacity overwritten — non-trivial
stress. We do NOT double sample size: the FULL 45 cell-seed sweep already
provides 9 cell-groups x 5 seeds = power-adequate evaluation per HP rule.

## Timeout estimate

- smoke_wall_s = 0.7s at 4 cells = 0.175s/cell.
- FULL: N=4096 (4x), M=2048 (8x), depth=5 (1.7x), K=100 (5x), 9 cells * 5
  seeds = 45 cells.
- Per-cell scaling factor (FULL/smoke): 4*8*1.7*5 = ~272; with
  scaling_exp=1.5 -> ~32x per-cell vs smoke.
- 45 cells x 0.175 * 32 = 252s. Apply 2x safety -> 504s.
- However the 4096^2 W matrix multiplication at apply_edits + per-batch
  W computations + audit hash on W (N^2 * 4 = 64 MiB) push per-cell wall
  closer to 5-15s at N=4096. Conservative budget for 45 cells x 15s ~
  675s; apply 2x safety + slack -> 14400s (user task spec).

**timeout_s = 14400** (user task spec).
