# Pre-registration: wave14_parisi_pq_kerdock_v2

**Date**: 2026-05-23
**Queue**: remote_cpu_queue (Glauber MC chains; numpy; CPU-bound)
**Axis probed**: Parisi P(q12) overlap distribution on Kerdock-Hebbian W (REAL chain length)
**Trigger**: Emergency refill 2026-05-23 19:50; v1 finished in 24s with under-resolved chains
**Script**: experiments/exp_wave14_parisi_pq_kerdock_v2.py
**Peak memory**: ~400 MB CPU at N=1024
**Expected elapsed**: ~45-60 min (3 alpha * 20 beta * 10 seed * 1e6 sweeps / parallelism)

---

## Scientific question

The v1 (parisi_pq_kerdock_v1) ran 800 total sweeps per (alpha, beta, seed) cell
and finished in 24s with verdict that may have reflected insufficient mixing
rather than true equilibrium P(q12) structure. For an N=1024 Ising-like system
in the slow-mixing low-T phase, chain lengths >> 10^4 sweeps are needed to resolve
the Parisi overlap distribution.

v2 expands chain length 1000x (n_burn=3e5, n_collect=7e5), broadens beta grid
(20 points covering paramagnetic, transition, deep ordered regime), and doubles
seed count (10) to make the P(q12) shape classifier statistically credible.

Same vertex set as v1.

---

## Design

- **N**: 1024 (same as v1; sufficient for Parisi resolution at chain length 1e6)
- **alpha grid (M/N)**: [0.05, 0.10, 0.20]
- **beta grid**: [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 14.0, 16.0, 20.0]
- **Seeds**: 10 per (alpha, beta)
- **n_burn**: 300,000 sweeps
- **n_collect**: 700,000 sweeps
- **Total chain length**: 1,000,000 sweeps per (alpha, beta, seed) per replica

Two-replica protocol (independent thermal chains, both random init) recording q12 at every sweep.

---

## Falsifiable predictions

### PARISI_RSB_KERDOCK (HARD PASS for glassy substrate)

>=1 low-T (beta>=4) cell shows continuous-support P(q12) (support_width > 0.5,
n_peaks >= 3 or sw > 0.7 with n_peaks >= 2). Substrate sustains a replica-symmetry-
broken glass phase. Deflated P = 0.30 (v1 already saw under-determined hints but
no clean RSB shape).

### PARISI_RS_KERDOCK (REPLICA SYMMETRIC)

All low-T cells show two-delta shape (n_peaks=2, dz<0.3, sw<0.4); >=50%. Substrate
is RS-like Hopfield-on-Kerdock; no glassy complexity. P = 0.30.

### PARISI_PARAMAGNET_KERDOCK

All low-T cells show single-delta-at-zero. Either T_c is higher than tested or
substrate's Kerdock-Hopfield does not enter an ordered phase. P = 0.20.

### PARISI_INCONCLUSIVE

Mixed shapes across low-T cells. P = 0.20.

---

## Substrate-product interpretation

- **RSB**: Kerdock-Hebbian W sustains a glassy free-energy landscape. Implications:
  thermal-style retrieval (annealing, simulated annealing readout) has access to
  hierarchical metastable structure -- substrate-product handle for "memory-as-energy-landscape"
  story.
- **RS**: substrate is computationally simpler than glasses (two-delta retrieval state).
  AMP_SE_DIVERGES must arise from non-glassy mechanism (kappa_n profile).
- **PARAMAGNET**: Kerdock-Hopfield is unusually high-T -- substrate-product flag that
  retrieval requires temperatures cooler than naive AGS theory predicts.

---

## PROT compliance

Per [[feedback-pipeline-pacing]]: long-running CPU work on remote runner; non-trivial
runtime (~45-60 min) to keep queue depth >=1 while GPU runs kappa_n / VAMP-contrast.
