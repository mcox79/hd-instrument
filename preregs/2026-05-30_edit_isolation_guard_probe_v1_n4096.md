# Pre-reg: edit_isolation_guard_probe_v1_n4096

**Date:** 2026-05-30
**Anchor:** edit_isolation_guard_probe_v1_n4096 (U3, v289 follow-on)
**Script:** experiments/exp_edit_isolation_guard_probe_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Path B copy-on-write W for edit-coexistence with
v289 production-default Path D (SDK probe).

## Context

v289 cap_map shipped Path D as production-default for 6-axis robust
retrieval. T2 (path_d_edit_isolation_under_load_v1_n4096) is currently
in flight testing Path D's natural edit-robustness under concurrent edits.
THIS probe (U3) tests a DIFFERENT mechanism: an explicit copy-on-write (COW)
layer on W that lets Path D queries snapshot the substrate state at query
start, isolated from any edits arriving during traversal. This is the SDK
feasibility check: can the substrate support pre/mid/post edit-coexistence
patterns without (a) violating query consistency, (b) collapsing edit
throughput, (c) breaking the audit chain, or (d) blowing up memory?

## Hypothesis

Copy-on-write W is FEASIBLE for SDK use: across 3 timing patterns
{pre, mid, post}, consistency >=0.90, throughput >=50 edits/sec,
audit chain valid, mem amplification <=4x dense W.

## Pre-registered bands

| Outcome      | Condition                                                              |
|--------------|------------------------------------------------------------------------|
| HARD_PASS    | For all 3 timing patterns: >=3/5 seeds with consistency >=0.90 AND     |
|              | throughput >=50/sec AND audit chain valid AND mem amplification <=4x   |
| HARD_FAIL    | Any pattern with >=3/5 seeds at: consistency <0.70 OR throughput <10/sec |
|              | OR audit chain broken OR mem amplification >16x                        |
| MIDDLE_BAND  | otherwise (mechanism partially feasible, does not meet SDK bar)        |

## Workload

- N=4096, BSC, M=2048, depth=5, K_paths=100. 5 seeds.
- 50 Path D queries per cell-seed; 100 edit-ops per cell-seed.
- 3 timing patterns: pre, mid, post. 3 x 5 = 15 cell-seeds. Per-cell-seed
  checkpoint (PROT-021).

## Mechanism (copy-on-write W)

```
cow_apply_edit(W, codebook, key, old_val, new_val, N):
    W2 = W.clone()                              # copy-on-write
    W2 -= (codebook[old_val].T @ codebook[key]) / N
    W2 += (codebook[new_val].T @ codebook[key]) / N
    return W2
```

Per timing pattern:
- **pre**:  apply all edits BEFORE running queries -> queries see post-edit W only
- **mid**:  snapshot W; run query against snapshot; apply edits; verify
            re-query against snapshot gives same result (snapshot-isolated)
- **post**: run queries against original W FIRST; apply edits after -> queries
            unaffected

## Metrics

- **consistency_rate**: fraction of queries whose Path D result against the
  snapshot W equals a re-run against the same snapshot W (deterministic-
  given-W check; substrate must commit to one snapshot view)
- **edit_throughput**: edits per second (incl. COW clone overhead)
- **audit_chain_valid**: SHA-256 hash chain over W versions is fully
  distinct (no edit silently noop'd)
- **mem_amplification**: peak GPU bytes / baseline dense W bytes (GPU path);
  count of active snapshot tensors (CPU fallback)

## Self-test

- N == 4096 (PROT-018)
- HP verdict gate: synthesized cons=0.95 thru=100/s audit=True mem=2.5x ->
  HARD_PASS
- HF verdict gate: synthesized cons=0.50 thru=5/s audit=False mem=32x ->
  HARD_FAIL
- Live `measure_cell()` smoke on CPU returns all 4 metric fields with
  n_queries > 0.

## Timeout estimate

Smoke wall ~60s. FULL: 15 cell-seeds. Per cell-seed: substrate build (~10s)
+ 50 Path D queries x ~50ms (~2.5s) + 100 edit-clones x ~5ms (~0.5s) +
re-query for consistency (~2.5s) = ~15-30s. Total ~450s compute. 14400s
budget for safety against GPU contention from concurrent T2 anchor.

## Production config

- N=4096, M=2048, depth=5, K_paths=100, 50 queries, 100 edits.
- 3 timings x 5 seeds = 15 cell-seeds.

## N-suffix binding

`_n4096` -> production N = 4096 (PROT-018). `N_FULL = 4096` asserted at
import.

## Note (SDK probe scope)

This probe answers: is COW W FEASIBLE in principle? Engineering for
production (GC of stale snapshots, sync primitives, fallback rollback)
is followup IF HARD_PASS. Failure here means COW is not the right
edit-coexistence design and we explore alternatives (e.g., log-structured
edit queue, in-place with versioned audit) in followup.
