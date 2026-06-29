# Pre-reg: substrate_routing_geometry_family_phase_diagram_v1

**Date:** 2026-06-29
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**USER directive context (2026-06-29):** systematic phase-diagram coverage
across substrate components. Already covered: encoder family / cleanup family
(PC) / routing family WM (4-family OUTER axis: partition / k-NN-softmax /
softmax-attn / hierarchical) / schema family / binding op family / refuse-gate
adaptivity. NOT YET COVERED: partition-routing GEOMETRY (DIFFERENT LEVER --
INTERNAL structure of partition routing branch, not the OUTER family axis).

**Cell:**
- Core: `experiments/_substrate_routing_geometry_family_phase_diagram_v1_core.py`
- Seeds:
  - `experiments/exp_substrate_routing_geometry_family_phase_diagram_v1_seed_7.py`
  - `experiments/exp_substrate_routing_geometry_family_phase_diagram_v1_seed_13.py`
  - `experiments/exp_substrate_routing_geometry_family_phase_diagram_v1_seed_19.py`

## Discriminator vs prior cells

| Lever | Prior cell (this session OR earlier) | THIS cell |
|---|---|---|
| WHICH routing primitive (partition vs softmax vs hierarchical vs knn) | `substrate_wm_routing_family_phase_diagram_v1` (LANDED MM 3-seed) | --- |
| HOW partition is constructed (geometry of the partition primitive) | --- | **THIS CELL** |
| WHICH encoder (PC / seqbind / WM / ANCHOR4) | `substrate_pc_encoder_family_phase_diagram_v1` etc. | --- |
| WHICH cleanup mechanism | `substrate_pc_cleanup_family_phase_diagram_v1` | --- |
| WHICH binding op | `substrate_pc_binding_operation_family_phase_diagram_v1` | --- |
| WHICH refuse-gate adaptivity | `substrate_refuse_gate_adaptivity_phase_diagram_v1` | --- |

This is a NEW axis (orthogonal to WM-routing-family). Partition is one branch
of the WM routing tree; this cell sweeps the INTERNAL structure of THAT branch
alone.

## Outer axis (LOCKED at module init)

4 partition-routing geometries:

1. **`random_uniform`** -- random bipolar anchors per partition.
   Current chain-grade default. **POSITIVE CONTROL.**
2. **`learned_supervised`** -- anchors = centroid of items assigned to
   partition. One-pass centroid smoothing (sigma=0.10 in HD space). Mimics
   STDP-driven prototype convergence.
3. **`hierarchical_2_level`** -- 2-level: G=sqrt(P) coarse groups x P/G fine.
   Group anchor = mean of fine anchors; route coarse-then-fine. Biological
   hierarchical allocation (cortex-region -> microcircuit).
4. **`hash_based_LSH`** -- n_planes = ceil(log2(P)) random projection planes;
   sign-pattern % P -> partition index. Fly-LSH style; rank-agnostic.

## Inner axis (LOCKED at module init)

- M (total items): `{1M, 5M, 10M}` FULL; `{10k, 100k}` SMOKE
- P (num partitions): `{64, 256, 1024}` FULL; `{64, 256}` SMOKE
- N (dim): 8192 FULL; 2048 SMOKE

CARDINALITY:
- FULL: 4 geometries x 3 M x 3 P = **36 phase points per seed**
- SMOKE: 4 geometries x 2 M x 2 P = **16 corner points per seed**

CARDINALITY_OK is HARD_FAIL on breach (META_RULE_H discipline).

## Storage-free design (load-bearing for M=10M)

Items are NOT stored as full HD vectors. Each item is represented by:
- An integer ground-truth partition assignment in [0, P).
- A noisy cue derived on-the-fly from the partition's anchor.

Working set per phase point: P * N * float32 (anchors) + N_PROBE * N * float32
(cues) + N_PROBE * int64 (labels). At M=10M, P=1024, N=8192:
- Anchors: 1024 * 8192 * 4 = 32 MB
- Cues: 4096 * 8192 * 4 = 128 MB peak
- Labels: 4096 * 8 = 32 KB
Total <= 200 MB. Fits easily on any GPU. M is sweepable orthogonal to memory.

The discriminator is **routing-recovery under noise**: does the geometry's
routing function correctly map noisy cue -> the partition whose anchor was the
clean cue? This generalizes to M items because the routing decision is the
same regardless of how many items COULD be routed (routing geometry is a
property of the (P, N) partition space, not M; M enters via the probe-sample
count and via the per-query routing latency).

## Discriminator (LOAD-BEARING)

Per phase point (geometry, M, P):
- **`route_acc`** = mean(pred_partition == true_partition) over N_PROBE
  random probe items (4096 FULL / 512 SMOKE).
- **`latency_us_per_query`** = wall-clock of the assign_fn call on the probe
  batch / N_PROBE, in microseconds.

GROUND TRUTH: for each probe-item, draw a random partition-ID uniformly in
[0, P). Generate a noisy cue from that partition's `random_uniform` GT-world
anchor (CUE_COS=0.70). The geometry's assign_fn is then expected to recover
the GT partition from the noisy cue. (See core docstring for the noise
schedule; honest ground-truth: same GT-world for all 4 geometries -- the
discriminator measures noise-robustness of routing recovery.)

## Bands (PRE-REG envelope-fail-bands)

Per phase point:
- `SATURATED`: route_acc >= 0.999 (suspect saturation -- discriminating
  regime not reached)
- `HARD_PASS`: route_acc >= 0.90
- `MIDDLE_BAND`: 0.50 <= route_acc < 0.90
- `FLOOR`: route_acc <= 1.5 / P (random chance + margin)
- `HARD_FAIL`: anything between FLOOR and MIDDLE_BAND

Per cell (FULL run):
- **`CHAIN_GRADE_PARTITION_GEOMETRY_PHASE_DIAGRAM`** (target):
  - cardinality_ok
  - positive_control passes (random_uniform at M=1M, P=256 -> route_acc >= 0.90)
  - **>=1 geometry achieves route_acc >= 0.97 at M=10M** (USER target)
  - <75% of phase points SATURATED
- **`DISCRIMINATING_PARTITION_GEOMETRY_PHASE_DIAGRAM`**:
  - cardinality_ok
  - positive_control passes
  - clear dominant geometry (best mean - next best > 0.10)
  - chain-grade target NOT met (no geom >= 0.97 at M=10M)
- **`GEOMETRY_INVARIANCE`**: 2+ geometries are COMPETITIVE (within 0.05 of best)
- **`MIDDLE_BAND_GEOMETRY`** / **`MIDDLE_BAND_BY_CONSTRUCTION_SATURATION`**:
  no clear discrimination or >=75% saturated
- **`HARD_FAIL_CARDINALITY_BREACH`** / **`HARD_FAIL_CONTROL_FAIL`**: rig broken

## Smoke gate (predicate in `smoke_gate_predicate(body)`)

Must pass ALL 5 criteria:
1. `cardinality_ok`: observed_n == expected_n (16 smoke / 36 full)
2. `positive_control`: random_uniform @ M=10k P=64 -> route_acc >= 0.85
3. **4/4 geometries produce distinct anchor hashes** (META_RULE_AF
   arms-differ; each geom has >=1 hash that NO other geom has)
4. **No all-FLOOR geometry** (silent dead-code guard)
5. **>=2 geometries show discriminating phase points** (>=30% disc-fraction)

Failure of any -> smoke verdict HARD_FAIL_SMOKE with reason string.

## Positive control (test-rig sanity)

`random_uniform` at M=1M, P=256 must produce `route_acc >= 0.90` (FULL).
Smoke equivalent: M=10k, P=64 -> route_acc >= 0.85. If the positive control
FAILS, the test rig is broken (the chain-grade default WM v3 partition
should reproduce evidence) and the cell HARD-FAILs immediately.

## Dispatch plan

**Destination:** `overnight_queue` (GPU; matmul-heavy at N=8192, n_probe=4096,
and especially M=10M LSH-codes which are GPU-friendly).
**Seeds:** 7, 13, 19 (3-seed chunked, per WM v1 pattern). One sibling file
per seed; siblings dispatched independently for parallelism + per-seed
checkpoint isolation.
**Routing path:** exp_dev cannot push (harness-DENIED); route to Orchestrator
via DISPATCH_REQUEST note + SendMessage.

**Per-seed timeout estimate:**
- Smoke wall-clock (measured): TBD seconds; estimated <120s on CPU at N=2048.
- Scaling factor: N=8192/2048 -> 4x; n_probe=4096/512 -> 8x; M=10M/100k -> 100x
  (but M ONLY affects anchor build for one geometry; routing latency is
  O(N_PROBE * N * P), not O(M)). True scale factor ~= 32x.
- Wall-clock per seed FULL on GPU: ~600-1800s. Add 1.5x safety -> 2700s.
- Use `--timeout 7200` (2 hr) per seed to absorb GPU-utilization variability.

PROT-019: anchor name has no `_n<N>` suffix (multi-N sweep cell); no floor
required.
PROT-021: timeout 7200 < 14400 threshold; checkpoint not strictly required
but `_seed_checkpoint` IS imported via the wrapper for crash-safe resume.
PROT-020: cells import torch at TOP; GPU eligibility OK.

## Authored discipline (cross-cutting)

- ASCII-only; no unicode; no em-dashes.
- META_RULE_AF (arms-differ): each geometry has unique anchor_hash and
  unique routing function; verified in `selftest` AND in `smoke_gate_predicate`.
- META_RULE_AE (constants LOCKED at module init): all bands + sweep axes
  defined as module-level constants; no runtime mutation.
- META_RULE_H (cardinality_ok mandatory): smoke_gate + FULL verdict both
  HARD_FAIL on cardinality breach.
- Discipline catalog references:
  - "test rationality - encoding before readout" (USER 2026-06-27): the
    geometry IS the encoding mechanism; routing accuracy is the readout.
    Encoding (anchor construction) is explicit in each builder.
  - "verify-run_mode-before-treating-verdict-as-cert-grade": cells stamp
    `run_mode` into metrics.json; aggregator reads it to choose verdict path.
  - "compute formulas in code": all band thresholds + cardinality + chance
    formulae are computed in the core module, not in this doc.

## Honest scope + caveats

- The `learned_supervised` builder simulates centroid smoothing analytically
  (noise sigma=0.10 around random anchors), NOT actual full M-item assignment
  + centroid update. This is by design (storage-free) -- it captures the
  GEOMETRY property of "anchors live at centroids of assigned items" without
  the M-scale cost. A separate cell could probe whether full assignment +
  centroid update yields meaningfully different routing accuracy.
- `hash_based_LSH` has no explicit "anchor" geometry; we return random
  anchors as a stand-in for the (P, N) slot (used only for distinctness
  hashing). LSH's assign_fn uses the planes directly.
- The "routing accuracy" metric is **noise-robustness of routing recovery**
  under fixed CUE_COS=0.70. It is NOT "fraction of items that COULD be
  retrieved from a real M-item store." This cell measures the routing
  primitive in isolation; pairing with a storage cell (e.g. PC-AM, dense KV)
  is a separate composability question.
- M is sweepable but does NOT appear in the routing function's wall-clock
  (only in anchor-build cost for learned_supervised, which is also
  simulated). M's role here is to verify the routing PRIMITIVE scales
  cleanly: a geometry that fails at M=10M failed at M=1M too. If we observe
  M-dependent variation in route_acc, that's a finding (suggests M-coupled
  state mutation, e.g. anchor drift).

## Skunkworks's expected VET arc

1. Independent recompute of route_acc per (geometry, M, P) point off the
   `phase_map` array.
2. Verify positive_control passes off raw numbers.
3. Verify anchor-hash distinctness (META_RULE_AF).
4. Skunkworks may rule MEASURED_MECHANISM if discriminator is real but
   chain-grade target (0.97 at M=10M) not hit; OR
   CHAIN_GRADE_PHASE_CHARACTERIZATION if any geometry meets it; OR
   GEOMETRY_INVARIANCE if multiple cluster (still cert-relevant: shows
   the routing primitive is robust to internal-structure choice).

Cell-author default: under-claim. Let cert-owner tier UP.
