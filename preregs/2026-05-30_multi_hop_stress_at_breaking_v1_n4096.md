# Prereg: multi_hop_stress_at_breaking_v1_n4096

**Date:** 2026-05-30
**Anchor:** multi_hop_stress_at_breaking_v1_n4096
**Script:** experiments/exp_multi_hop_stress_at_breaking_v1_n4096.py
**Queue:** overnight_queue
**Timeout:** 21600s (per user spec)

## Why this anchor

P1+Q3 jointly confirmed multi-hop durability at M=8192 K=1000 (production-scale).
Now characterize the BOUNDARY: at what M and depth do the three multi-hop paths
(B, D, E) FAIL? The user directive is "push to BREAKING regime to find limits."

## Sweep grid

- N = 4096 (PROT-018 _n4096 binding).
- BSC substrate (Kerdock 4-coset codebook, C = 16384 codewords).
- Paths: {B (continuous-output), D (posterior-product), E (spectral-coherence)}.
- M grid: {16384 (= M_c), 24576 (= 1.5 * M_c, past M_c)}.
- Depth grid: {10, 15, 20} (deep multi-hop where noise should compound).
- K_paths = 500 (production-realistic).
- Seeds: {7, 17, 23, 31, 41}.
- Per-cell-seed checkpoint (PROT-021 reusable on crash).
- Cells: 3 paths x 2 M-points x 3 depths x 5 seeds = 90 cell-seeds.

## Pre-registered bands

- **HARD_PASS (HP)** = mean accuracy (over 5 seeds) >= 0.60 at EVERY (path, M, depth)
  cell. Reading: "multi-hop extends past test envelope; run harder v2."
- **HARD_FAIL (HF)** = mean accuracy (over 5 seeds) < 0.30 for ALL THREE paths at
  the worst cell (M=24576, depth=20). Reading: "breaking confirmed at predicted
  boundary."
- **MIDDLE_BAND (MB)** = otherwise. Reading: "mechanism-specific differential
  survival pattern; enables R2 composition design."

## Outcome plan

| Verdict | Action |
|---|---|
| HARD_PASS | Run a harder v2 with M >= 32768 OR depth >= 25; substrate beats current envelope. |
| HARD_FAIL | Confirm M_c boundary; cap_map row for production multi-hop set to "valid up to (M, d) before this boundary". |
| MIDDLE_BAND | Differential survival pattern unlocks R2 design — identify which path(s) survive longest, propose composition that exploits the asymmetry. |

## Closed-form self-tests in the script

- `compute_verdict(fake_hp)` returns HARD_PASS when all means >= HP_MIN_ACC.
- `compute_verdict(fake_hf)` returns HARD_FAIL when all paths < HF_MAX_ACC at worst cell.
- `compute_verdict(fake_mb)` returns MIDDLE_BAND when some cells degrade, some hold.

## Timeout estimate

smoke_wall_s = 0.5s (N=1024, M=512, 2 depths, 1 seed, 3 paths).
FULL scaling: N 1024->4096 (4x; exp=1.5), seeds 1->5, depths 2->3, M 512->24576.
M-storage scales linearly with M; matrix-multiply is O(N^2) so N exp = 2.0 not 1.5.
Per-cell-seed estimate ~30-60s at M=24576.
90 cell-seeds total -> 2700-5400s expected. User pre-spec'd 21600s buffer.

**Timeout: 21600s** (user spec, accommodates 4x slowdown for M>C repeats).

## PROT-018 _n4096 binding

`N = 4096` is a module-level constant. Verified by `grep -E "(N\s*=|n\s*=)\s*4096" experiments/exp_multi_hop_stress_at_breaking_v1_n4096.py`.

## Dependency check

- experiments/_metric_battery.py (make_substrate) -- exists
- experiments/_relation_graph.py (build_relation_facts, sample_coherent_starts, sample_incoherent_paths) -- exists
- experiments/_seed_checkpoint.py -- exists
- No upstream data files required.
