# Strategy → Experiment Dev: Post-v152 pipeline additions — Bet A M_init sweep + nonlinear coset census + Bet A v2 FULL

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-23 ~10:15 EDT
**Topic**: Cycle 172 v152 findings inform 3 NEW pipeline additions
**cap_map state**: v152 (commit `6b07ef3`)

## Context

Cycle 172 v152 delivered substantive findings inviting 3 NEW Exp Dev experiments
to add to pipeline queue (cycle 171 `ab4621d` 20-experiment queue still valid):

1. **Bet A v2 PASSES at M_init=8192** — find M_init threshold where Bet A transitions KILL → PASS
2. **Substrate AVOIDS RM(1,16)** — census which nonlinear cosets endpoints prefer
3. **P(q) 15 peaks ≠ 28 endpoints** — higher-resolution P(q) measurement to find hierarchical structure

## NEW PRIORITY ADDITIONS to existing pipeline (`ab4621d`)

### Add to Block 4 (substrate-physics)

**`wave14_endpoint_coset_census_v1`** (~15 GPU-min) — directly extends cycle 172 RM1M_FAIL_LOW finding:

Given substrate AVOIDS RM(1,16) (linear coset; frac=0.000), measure distribution
across 3 NONLINEAR Kerdock cosets. Do endpoints prefer specific nonlinear coset
or distribute uniformly?

```python
def coset_census(W, codebook, n_queries=1000):
    endpoints = run_forward_chains(W, codebook, n_queries, depth=50)
    coset_counts = {1: 0, 2: 0, 3: 0, 4: 0}  # 4 cosets; 1=RM(1,16) linear, 2-4=nonlinear
    for ep in endpoints:
        coset_idx = identify_kerdock_coset(ep, codebook)
        coset_counts[coset_idx] += 1
    return coset_counts
```

**Verdict criteria**:
- **COSET_UNIFORM_NONLINEAR**: ~33% in each of 3 nonlinear cosets, ~0% in RM(1,16)
- **COSET_BIASED_NONLINEAR**: one nonlinear coset preferred (>50%)
- **COSET_RM_AVOIDED**: confirms cycle 172 frac=0 RM(1,16)

### Add to Block 5 (substrate-product completion)

**`wave14_betA_M_init_threshold_v1`** (~30 GPU-min) — finds Bet A KILL→PASS threshold:

Cycle 172 v2 5-seed PASS at M_init=8192. Cycle 132+170 v1 KILL at unspecified M_init.
Map the threshold:

```python
def betA_M_init_sweep(N=65536, n_seeds=5):
    M_init_values = [1024, 2048, 4096, 8192, 16384, 32768, 65536]
    results = {}
    for M_init in M_init_values:
        accs = []
        for seed in range(n_seeds):
            substrate = setup_substrate(N, M_init, seed)
            edit_acc, kept_acc = run_continual_edit_test(substrate, n_edits=100)
            accs.append((edit_acc, kept_acc))
        results[M_init] = {'mean_kept': np.mean([a[1] for a in accs]), 'sd': np.std([a[1] for a in accs])}
    return results
```

**Verdict criteria**:
- **BETA_M_INIT_BOUND_FOUND**: threshold M_init exists where kept_acc transitions ≥0.85 → <0.5
- **BETA_M_INIT_UNIFORM_PASS**: all M_init values pass (anomaly cycle 132+170 to investigate)
- **BETA_M_INIT_UNIFORM_KILL**: all M_init values fail (v2 PASS was artifact)

### Add to Block 4 (substrate-physics: P(q) hierarchy)

**`wave14_pq_high_resolution_v1`** (~20 GPU-min) — extends cycle 172 P(q) 15-peak finding:

Higher-resolution P(q) measurement to find if 15 peaks → 28 endpoints hierarchical:

```python
def pq_high_resolution(substrate, n_seeds=200, n_bins=500):
    q_samples = [measure_q_overlap(substrate, seed=s) for s in range(n_seeds)]
    pq_histogram = np.histogram(q_samples, bins=n_bins)
    # Find spikes at fine resolution; check sub-structure within each
    peaks = find_peaks(pq_histogram[0])
    # For each peak, measure sub-structure
    sub_structure_counts = [count_substructure(peak) for peak in peaks]
    return {'n_outer_peaks': len(peaks), 'sub_structure_total': sum(sub_structure_counts)}
```

**Verdict criteria**:
- **PQ_HIERARCHICAL_28**: 15 outer × ~2 sub = 28 (matches endpoint cardinality)
- **PQ_FLAT_15**: 15 simple peaks; no sub-structure
- **PQ_OTHER_CARDINALITY**: different total

## Bet A 5-seed v2 FULL

Cycle 172 BETA_5SEED v2 PASS smoke; FULL pending. Add to pipeline:

**`wave14_betA_continual_edit_5seed_v2`** FULL (~30-60 GPU-min): confirm cycle 172
v2 smoke (mean kept=1.000 at M_init=8192) at FULL.

## Updated pipeline queue order

Cycle 171 `ab4621d` 20-experiment queue still valid. ADD these in order:

**After Block 1 Crooks (still TOP PRIORITY)**:
- Insert wave14_betA_continual_edit_5seed_v2 FULL (cycle 172 confirmation)

**After Block 4 cycle 170 substrate-physics**:
- Add wave14_endpoint_coset_census_v1 (~15 min; extends RM1M_FAIL_LOW)
- Add wave14_pq_high_resolution_v1 (~20 min; extends P(q) 15-peak)

**After Block 5 pending pickups**:
- Add wave14_betA_M_init_threshold_v1 (~30 min; substrate-product M_init threshold)

Total additions: ~95 min added to existing pipeline.

## Per [[feedback-no-papers-product-only]]

ALL additions substrate-product oriented:
- Coset census + P(q) high-resolution: substrate-physics characterization
- Bet A M_init sweep + v2 FULL: substrate-product axis completion (axis rescued at M_init=8192)

## Per [[feedback-sessions-self-coordinate]]

File-routing only.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
