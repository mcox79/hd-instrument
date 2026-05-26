# R37 F.1 + F.3 engineering bridge — Experiment Dev-ready specs for substrate facilitation/nucleation test

**Routed**: User-directed exploration (cycle 41, post-Entry 44 prompt
"explore them all at your priority"). Extension of R37 (Entry 42).

**Date**: 2026-05-21 (~23:10 EDT).

**Status**: Engineering specification (NO new lit scan; uses R37 Entry
42 + Chacko 2024 + Herrero-Berthier 2024 methodology specs from R37
Pass 1).

**Owner**: Research session (single-writer-per-file).

**Connects**: R37 substrate facilitation/nucleation methodology (Entry
42); Bet E methodology escalation H2 (Entry 40); R18 Kerr Winter
mathematical-glass caveat (Entry 24); R24 FDT violation methodology
(Entry 21).

**Outcome category**: **EXPERIMENT-DEV-READY engineering specification**.
Translates R37 F.1 Chacko heating-cooling asymmetry test + F.3 Herrero-
Berthier conditional flip probability test into substrate-specific
pseudocode + parameter specs + verdict logic suitable for
`wave14_facilitation_nucleation_v1` build.

---

## HEADLINE

> Engineering-bridge specification ready for Experiment Dev queue. Both
> F.1 + F.3 implementations fit within standard substrate Glauber-
> dynamics framework with minor extensions for:
> - F.1: temperature-protocol scheduling + mobility-cluster tracking
> - F.3: codebook-similarity-graph + conditional probability statistics
>
> **Combined experiment**: `wave14_facilitation_nucleation_v1` with
> 4 sub-experiments (F.1 heating-cooling × {Kerdock v4, random BSC});
> (F.3 conditional flip × {Kerdock v4, random BSC}). Estimated 5-8
> GPU hours total. Substrate-first associative-memory facilitation
> test (per R37 Clark 2025 absence finding).

---

## 1. F.1 substrate Chacko heating-cooling asymmetry test

### Setup

**Substrate variant**: standard wave14 Hopfield framework at α=0.153
(just above AGS α_c=0.138; per R29 modern-Hopfield regime); N=4096;
Kerdock v4 codebook (PRIMARY); random ±1 BSC (CONTROL).

**Temperature schedule** (Glauber dynamics):
```
Phase A (equilibrate cold, retrieval-stable):
  T_init = 1/β = 1/32 = 0.03125
  duration: 10,000 Glauber steps
  initial state: stored-pattern (one of M=8N=32768 patterns)

Phase B HEAT (linear T ramp through AGS retrieval-glass boundary):
  T(t) = T_init + (T_high - T_init) · (t / T_heat_duration)
  T_high = 1/β_high = 1/4 = 0.25 (substrate spin-glass regime)
  duration: 10,000 Glauber steps

Phase C COOL (linear T ramp BACK; init from random):
  T(t) = T_high + (T_init - T_high) · (t / T_cool_duration)
  initial state: random ±1^N
  duration: 10,000 Glauber steps
```

### Mobility-cluster tracking

**Mobility cluster definition**:
- Track spin-flip events within rolling 100-step window
- Cluster: connected component of recently-flipped spins (within window)
  in codebook-similarity graph G_cb (substrate atoms connected if their
  Kerdock-codeword inner product exceeds threshold; e.g., top-10%
  similar pairs)
- Cluster size: number of spins in connected component

**Pseudocode**:
```python
def mobility_cluster_growth(spin_state_history, codebook_graph, window=100):
    cluster_sizes_over_time = []
    for t in range(window, len(spin_state_history)):
        recent_flips = set()
        for i in range(N):
            if any(spin_state_history[t-window:t, i] != spin_state_history[t, i]):
                recent_flips.add(i)
        # Find connected components in codebook_graph restricted to recent_flips
        clusters = connected_components(codebook_graph, recent_flips)
        max_cluster_size = max(len(c) for c in clusters) if clusters else 0
        cluster_sizes_over_time.append(max_cluster_size)
    return cluster_sizes_over_time
```

### Verdict logic

**Asymmetric observable**:
```
R_asym = mean(cluster_sizes_heating) / mean(cluster_sizes_cooling)
```

**Verdict per Chacko 2024**:
- **R_asym > 5**: facilitation-dominated (substrate IS Kerr Winter
  mathematical-glass class; supports Bet E H2 = substrate-NOT-true-
  thermodynamic-glass)
- **R_asym ∈ [1, 5]**: hybrid (RFOT mosaic + facilitation; modal
  position per literature 2024-2025)
- **R_asym ≈ 1**: nucleation-dominated (substrate IS true thermodynamic
  glass; Bet E v62 ✅ promotion supported)
- **R_asym < 1**: anomalous; likely artifact

### Parameters summary

| Parameter | Value | Notes |
|---|---|---|
| N | 4096 | Substrate dimension |
| M | 8N = 32768 | Pattern count (Bet C v4 ✅ regime) |
| α | 0.153 (M/N at fixed N) | Just above AGS α_c=0.138 |
| β_init | 32 | Substrate retrieval-stable (R29 modern-Hopfield) |
| β_high | 4 | Substrate spin-glass-like regime |
| T_heat_duration | 10K Glauber steps | Linear T ramp |
| T_cool_duration | 10K Glauber steps | Linear T ramp |
| Window | 100 Glauber steps | Mobility-cluster rolling window |
| Codebook | Kerdock v4 (PRIMARY); random ±1 (CONTROL) | |
| Similarity threshold | top-10% pairs | Define G_cb edges |
| Seeds | 5 minimum | Statistical robustness |

### Cost estimate

- 5 seeds × 30K Glauber steps × N=4096 substrate × 2 codebooks ≈ 1.2M
  spin-flip evaluations per cell
- Mobility-cluster tracking: ~ N · window = 4096 × 100 = 410K ops per
  cluster computation; computed every step → cluster computation
  dominates compute
- **Estimated 3-5 GPU hours per substrate variant** = 6-10 GPU hours
  total for Kerdock v4 + random ±1 BSC

---

## 2. F.3 substrate Herrero-Berthier conditional flip probability test

### Setup

**Substrate variant**: same as F.1; equilibrium sampling (no temperature
protocol; just Glauber at β=32).

**Codebook-similarity neighborhood**:
- Build G_cb from substrate codebook (Kerdock v4 PRIMARY; random ±1 BSC
  CONTROL)
- Define neighborhoods:
  - HIGH similarity: top-10% atom-pairs by codeword inner product
  - LOW similarity (control): random 10% atom-pairs (baseline)

**Conditional flip probability protocol**:
```
For each pair (i, j) with high similarity (or random baseline):
  Initialize substrate at stored pattern; Glauber-equilibrate
  Track: P(spin j flips within Δt=10 Glauber steps | spin i just flipped)
  Compute: F_{ij} = P_conditional - P_baseline
  Where P_baseline = P(spin j flips within Δt over random period)

Average F over high-similarity pairs:
  F_high = mean(F_{ij} for (i,j) in top-10% similar)
Average F over baseline pairs:
  F_baseline_random = mean(F_{ij} for random (i,j))

Discrimination metric: F_advantage = F_high - F_baseline_random
```

**Pseudocode**:
```python
def conditional_flip_probability(spin_history, atom_pairs, delta_t=10):
    F_values = []
    for (i, j) in atom_pairs:
        P_conditional_count = 0
        P_conditional_total = 0
        for t in range(delta_t, len(spin_history)):
            if spin_history[t-delta_t, i] != spin_history[t-delta_t+1, i]:
                # spin i flipped at time t-delta_t+1
                if any(spin_history[t-delta_t+1:t, j] != spin_history[t-delta_t, j]):
                    P_conditional_count += 1
                P_conditional_total += 1
        P_conditional = P_conditional_count / P_conditional_total if P_conditional_total > 0 else 0
        P_baseline = baseline_flip_probability(spin_history, j, delta_t)
        F_ij = P_conditional - P_baseline
        F_values.append(F_ij)
    return np.mean(F_values)
```

### Verdict logic

**Discrimination metric**:
```
F_advantage = F_high - F_baseline_random
```

**Verdict per Herrero-Berthier 2024**:
- **F_advantage > 0.1**: STRONG facilitation evidence (substrate IS
  facilitation-dominated)
- **F_advantage ∈ [0.01, 0.1]**: MODERATE facilitation evidence
- **F_advantage ∈ [-0.01, 0.01]**: NO facilitation (consistent with
  nucleation)
- **F_advantage < -0.01**: anomalous; investigate

### Parameters summary

| Parameter | Value | Notes |
|---|---|---|
| N | 4096 | Substrate dimension |
| α | 0.153 | Just above AGS |
| β | 32 | Substrate equilibrium temperature |
| Δt | 10 Glauber steps | Conditional probability time window |
| Equilibration | 20K Glauber steps before measurement | |
| Measurement | 100K Glauber steps | Statistical robustness |
| High-similarity pairs | top-10% by Kerdock IP | ~ 0.05 · N² = 840K pairs |
| Baseline pairs | random 10% | ~ 840K pairs |
| Seeds | 5 minimum | |

### Cost estimate

- 5 seeds × 100K Glauber steps × N=4096 × 2 codebooks ≈ 4M spin-flip
  evaluations
- Conditional probability tracking: O(pair_count · steps) ≈ 840K · 100K =
  8.4 × 10^10 ops (substantial)
- **Estimated 2-3 GPU hours per substrate variant** = 4-6 GPU hours
  total for Kerdock v4 + random ±1

---

## 3. Combined experiment: `wave14_facilitation_nucleation_v1`

### 4 sub-experiments structure

| Cell | Test | Codebook | Cost (GPU hrs) | Output metric |
|---|---|---|---|---|
| A1 | F.1 Chacko heating-cooling | Kerdock v4 | 3-5 | R_asym(v4) |
| A2 | F.1 Chacko heating-cooling | Random ±1 BSC | 3-5 | R_asym(BSC) |
| B1 | F.3 conditional flip | Kerdock v4 | 2-3 | F_advantage(v4) |
| B2 | F.3 conditional flip | Random ±1 BSC | 2-3 | F_advantage(BSC) |
| **Total** | | | **10-16** | 4 metrics |

### Combined verdict logic

**Facilitation-dominated**:
- R_asym(v4) > 5 AND F_advantage(v4) > 0.1 → STRONG facilitation
  evidence
- supports Kerr Winter mathematical-glass class
- supports Bet E H2 (substrate-NOT-true-thermodynamic-glass)
- Substrate-product implication: Bet E remains 🟡 methodology-bounded;
  do not promote back to v62 ✅

**Nucleation-dominated**:
- R_asym(v4) ≈ 1 AND F_advantage(v4) ≈ 0 → STRONG nucleation evidence
- supports Bet E v62 ✅ promotion as true thermodynamic glass
- Substrate-product implication: Bet E promotes back to ✅

**Hybrid (intermediate)**:
- R_asym(v4) ∈ [1, 5] OR F_advantage(v4) ∈ [0.01, 0.1] → hybrid
- supports modal RFOT-camp position (static RFOT + dynamic facilitation)
- Substrate-product implication: Bet E remains 🟡 methodology-bounded;
  document hybrid character

**Codebook-comparison**:
- Kerdock v4 vs random ±1 BSC should give CONSISTENT facilitation
  signal IF substrate-physics; INCONSISTENT IF codebook-geometry
  artifact (per Bet E methodology Entry 40 finding for Binder cumulant)

### Substrate-novel outcome

Per R37 + Clark 2025 absence: substrate would be FIRST associative-
memory facilitation-vs-nucleation empirical resolution. Substantial
substrate-product engineering value regardless of outcome.

---

## 4. Cross-mechanism integration with R36 + R24

**Combined 6-test substrate spin-glass characterization**:

| Test | Mechanism | Cost (GPU hrs) | Discriminates |
|---|---|---|---|
| F.1 Chacko heating-cooling | R37 this note | 6-10 | facilitation vs nucleation |
| F.3 conditional flip | R37 this note | 4-6 | direct facilitation |
| F.2 avalanche (backup) | R37 Entry 42 | 4-8 | substrate-specific facilitation |
| FDT violation X(C) | R24 Entry 21 | 5-10 | aging dynamics |
| Ultrametricity equilibrium | Bet E Entry 40 | 4-6 | RSB triplet structure |
| Small-field chaos (PNAS 2024) | Bet E Entry 40 | 4-6 | chaos signatures |

**Total**: 27-46 GPU hours for full 6-test substrate spin-glass
characterization. 65-80% P clean Bet E resolution per R37 Entry 42.

**Recommended sequence**:
1. F.1 + F.3 (10-16 GPU hours) — primary discrimination
2. FDT violation (5-10 GPU hours) — aging-dynamics validation
3. Ultrametricity + small-field chaos (8-12 GPU hours) — RSB triplet
   validation
4. F.2 avalanche (4-8 GPU hours) — backup if 1-3 inconclusive

---

## 5. Honest limitations (per [[feedback-no-smoke]])

1. **Glauber dynamics implementation** is substantial substrate
   engineering. Substrate framework currently uses Hebbian retrieval;
   adding Glauber sampling requires new module.

2. **Mobility-cluster tracking** assumes codebook-similarity-graph
   defines meaningful "spatial" structure for cluster connectivity.
   Substrate is fully-connected; this is an APPROXIMATION not perfect
   transfer of Chacko's spatial-glass methodology.

3. **F.1 R_asym threshold** at 5 is per Chacko 2024 finding for
   2D liquid glass; substrate-specific calibration may differ.

4. **F.3 conditional-probability noise** at substrate N=4096 may
   require longer measurement (100K+ Glauber steps) for statistical
   significance.

5. **Per [[feedback-rehabilitation-after-rejection]]**: this engineering
   bridge operationalizes R37 substrate-novel methodology for
   Experiment Dev queue; rehabilitates Bet E methodology question via
   substrate-applicable empirical resolution path.

6. **Per [[feedback-no-papers-product-only]]**: framing is "Experiment
   Dev queue specification + substrate-product engineering bridge,"
   NOT "novel methodology theory."

---

## 6. Deliverable summary

**To Experiment Dev (BUILD-READY specification)**:
- `wave14_facilitation_nucleation_v1`: 4 sub-experiments (A1, A2, B1,
  B2); 10-16 GPU hours total
- Standard substrate Glauber-dynamics framework with mobility-cluster
  tracking (F.1) + conditional probability statistics (F.3) modules
- Verdict logic: facilitation-dominated / hybrid / nucleation-dominated
  per joint R_asym + F_advantage criteria
- Codebook comparison (v4 Kerdock + random ±1 BSC) controls for
  geometry artifacts

**To Strategy**:
- Pairs with Bet E methodology escalation Entry 40 H2 question
- Combined R37 + R24 + Bet E methodology = 6-test substrate spin-glass
  characterization (27-46 GPU hours total; 65-80% P clean resolution)
- Substrate-novel: FIRST associative-memory facilitation-vs-nucleation
  test per Clark 2025 absence

**To Research**: engineering bridge complete; substrate-novel
methodology now Experiment Dev-actionable.

**Pass-1 honesty label**: NO new external lit scan; uses R37 Entry 42
+ Chacko 2024 + Herrero-Berthier 2024 specs.

---

**End R37 F.1 + F.3 engineering bridge note.** Size target ~14-16 KB;
actual: see wc -c on finalized file.
