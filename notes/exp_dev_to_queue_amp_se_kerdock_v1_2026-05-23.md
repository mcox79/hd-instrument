# Exp Dev -> Queue: AMP state-evolution at Kerdock codebook

**Filed**: 2026-05-23
**Trigger**: exp_dev dispatch; meta-map Drill 4 (B4+F5 adjacency, P_deflated=0.45); pipeline
  invariant maintenance (local_cpu_queue has 1 pending item after sinova_cij queued)

---

## Entry: local_cpu_queue (pure CPU numpy; ~30 min)

```
queue=local_cpu_queue name=wave14_amp_se_kerdock_v1 script=experiments/exp_wave14_amp_se_kerdock_v1.py prereg=preregs/2026-05-23_wave14_amp_se_kerdock_v1.md timeout=3600
```

**Axis probed**: AMP state-evolution fixed-point vs empirical AMP on substrate's exact
  Kerdock 4-coset codebook (Maiorana-McFarland construction over GF(2^6) at N=4096).
  Direct theory-to-empirics capacity bound comparison at substrate's M/N ratios.

**Motivation**: meta-map Drill 4 (B4+F5): AMP/VAMP is load-bearing (cycle 127 VAMP chain),
  free probability is load-bearing (Bet I). No published RS theory predicts substrate's
  M/N=8 at N=4096 capacity (4 lit-scan agents span 4 orders of magnitude). AMP state
  evolution gives exact finite-N predictions IF the Kerdock codebook satisfies the
  AMP matrix-class assumption (Bayati-Montanari 2011: right-rotationally-invariant
  matrices). This is open for Kerdock codes. Answering it either gives the first
  theory-matching-empirics anchor or gives a sharp universality-boundary finding
  explaining why VAMP (not AMP) is the right readout for substrate.

**Self-test**: 4/4 PASS (verdict logic: MATCHES, DIVERGES, INCONCLUSIVE, empty-cells)

**Smoke gate**: PASSED at N=1024, alpha={0.5,1.0}, 2 seeds.
  Smoke verdict: AMP_SE_DIVERGES (SE_mse=0.091 vs emp_mse=0.651-0.951; rel_err=0.83-0.87).
  Note: smoke shows early divergence signal at under-determined regime (alpha<1). The
  substrate's actual capacity regime is alpha=8 (M/N=8); the FULL run includes this.
  The pattern of divergence at low alpha may invert or narrow at high alpha -- this is
  scientifically meaningful and the FULL run resolves it.

**Peak memory**: ~700 MB CPU (N=4096, M=32768 at alpha=8; numpy float64 SVD of (32768,4096))
**Expected wall time**: ~25-35 min CPU
**No remote data dependency**: all data generated fresh from Kerdock codebook builder
**queue.json**: updated (D:/AI/hd-instrument/data/local_cpu_queue/queue.json; 1 new pending entry)

---

## What the verdicts mean

- **AMP_SE_MATCHES_EMPIRICS**: SE MSE within 20% of empirical AMP MSE across >= 2/3 of
  alpha cells. Kerdock codebook is effectively in AMP universality class. First
  theory-to-empirics capacity anchor for substrate. Supports using AMP (not just VAMP)
  as theoretical tool for predicting substrate M/N capacity. Strengthens RS-phase
  framework (load-bearing since cycle 112).

- **AMP_SE_DIVERGES**: SE MSE diverges from empirical AMP (mean rel err > 80%, < 1/3 cells
  close). Kerdock's GF(2^t) algebraic structure breaks AMP-SE assumptions. Novel finding:
  sharp universality-boundary marker (Pattern 4 in meta-map). Validates the VAMP-over-AMP
  architecture choice in VAMP-on-chain (cap_map v127). Explains why the 4 prior RS-theory
  capacity predictions disagreed -- the standard AMP capacity formula does not apply to
  Kerdock matrices.

- **AMP_SE_INCONCLUSIVE**: intermediate regime; partial match. Likely indicates the SE
  converges but empirical AMP has finite-N instability, or that only certain alpha values
  are in-class.

---

## Pipeline depth after filing

- local_cpu_queue: 2 pending (sinova_cij_eigenvalue_v1 + amp_se_kerdock_v1)
- Pipeline invariant: SATISFIED (runner will not be idle)
