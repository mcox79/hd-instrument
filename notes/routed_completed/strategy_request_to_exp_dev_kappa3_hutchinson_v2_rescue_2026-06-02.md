# Strategy -> exp_dev: kappa3_hutchinson_v2 rescue (TIMEOUT design-fault)

**Filed:** 2026-06-02 (verdict_handler cycle-3 batch v327)
**Recipient:** exp_dev
**Routing class:** rescue (I-3 design-fault closure)
**Priority:** PRIMARY (highest of v327 post-batch routing candidates)
**Pause-gate:** check `data/orchestrator_paused.flag` before queue_add

## Why this rescue

`kappa3_hutchinson_v1` TIMED OUT at queue-budgeted 1800s during overnight CPU cycle 3. Remote bridge confirmed no FULL artifact written (local-fallback returned smoke). v327 honest re-read identifies the design-fault:

1. **Non-vectorized Hutchinson inner loop** at `experiments/exp_kappa3_hutchinson_v1.py` lines 110-128:
   ```python
   for i in range(n_probes):
       v = rng.choice([-1.0, 1.0], size=(N,))
       Wv = W @ v
       WWv = W @ Wv
       WWWv = W @ WWv
       estimates[i] = float(np.dot(v, WWWv)) / N
   ```
   Production scope: 5 seeds x M=[50,100,200,500] x N_PROBES=5000 x 2 (Hopfield+GOE) = 200,000 N=4096 dense N x N matvec sequences in Python loop. Dominated by Python overhead + GEMV calls.

2. **Tight 1800s queue.json timeout** (prereg said 3600s but queue.json had 1800s -- INFRA GAP exposed).

**Pattern-match:** identical class to v325 spectral_zstat_v1 I-2 (RESOLVED v326 by R3 rescue: vectorized inner product + raised timeout 300s -> 1800s; empirical wall 234.87s well within budget).

## Rescue spec (R2, the RECOMMENDED PRIMARY rescue from v327 cap_map)

### 1. Vectorize Hutchinson estimator

Replace `hutchinson_kappa3(W, n_probes, seed)` body with batched probes:

```python
def hutchinson_kappa3(W: np.ndarray, n_probes: int, seed: int) -> Tuple[float, float]:
    """Vectorized Hutchinson estimator for Tr(W^3) / N = kappa_3.
    Batched probes: V shape (N, n_probes); 3 GEMM calls instead of n_probes GEMV.
    """
    rng = np.random.RandomState(seed)
    N = W.shape[0]
    # Batched Rademacher probes: V shape (N, n_probes)
    V = rng.choice([-1.0, 1.0], size=(N, n_probes)).astype(np.float64)
    # 3 dense GEMM calls (BLAS-optimal)
    WV = W @ V              # (N, n_probes)
    WWV = W @ WV            # (N, n_probes)
    WWWV = W @ WWV          # (N, n_probes)
    # estimates[i] = V[:,i] . WWWV[:,i] / N
    estimates = (V * WWWV).sum(axis=0) / N    # shape (n_probes,)
    kappa3 = float(np.mean(estimates))
    std = float(np.std(estimates, ddof=1)) / math.sqrt(n_probes)
    return kappa3, std
```

**Expected speedup:** 10-100x (3 BLAS GEMM calls scale on cache + SIMD; per-probe Python overhead eliminated). For N=4096 n_probes=5000, the vectorized form is 3 * GEMM(N x N, N x n_probes) = 3 * 4096^2 * 5000 ~ 2.5e11 ops via BLAS; should complete in ~10-30s per (M, seed) pair on modern CPU.

### 2. Memory budget check (do this BEFORE running)

V shape (N=4096, n_probes=5000) = 1.64e7 float64 = 131 MB.
WV / WWV / WWWV: same shape = 131 MB each.
W: N x N = 1.34e8 float64 = 1.07 GB.

Total peak: ~1.5 GB working set per Hopfield/GOE call. Comfortable on remote CPU (verify free RAM before ship; if tight, fall back to chunked vectorization e.g. n_probes=1000 chunks of 5).

### 3. Queue.json timeout raise

Per-script timeout 1800s -> **3600s** (matches prereg budget; gives 2x safety margin over vectorized estimate).

### 4. Preserve verdict logic + prereg bands

Keep `compute_verdict`, `aggregate_results`, all HP/HF thresholds unchanged. The math is correct -- only the implementation is too slow.

### 5. Self-test additions

Add to `_instrumentation_selftest()`:
- Compare vectorized output to per-probe loop output on a small test case (N=128, n_probes=50): expect identical results to within float64 precision.
- Document the vectorized memory footprint in the docstring.

### 6. Re-ship instructions

```
queue=remote_cpu_queue anchor=kappa3_hutchinson_v2 script=experiments/exp_kappa3_hutchinson_v2.py prereg=preregs/2026-06-02_kappa3_hutchinson_v2.md timeout=3600
```

Create v2 script + v2 prereg (carry over HP/HF thresholds unchanged; note vectorization in prereg "Implementation notes" + "TIMEOUT ESTIMATE" sections).

PROT-018 binding: anchor name `kappa3_hutchinson_v2` carries no `_nN` suffix (production N=4096 per rule 3, same as v1).

## Cap_map cross-reference

- **I-3 (v327, NEW):** kappa3_hutchinson_v1 non-vectorized Hutchinson + tight timeout = TIMEOUT.
- **PP-33d (v326, DEFERRED):** substrate spectral concentration is non-asymptotic-BBP; kappa3 free-cumulant is same algebra family as spectral_zstat (both probe substrate spectral signature). If kappa3_v2 succeeds and shows ~10x deviation from theory ratio M/N (analogous to v326 PP-37 10x sensitivity finding), that corroborates PP-33d as a NON-ASYMPTOTIC-BBP class signature. Surface this comparison in v2 verdict_msg.
- **PP-37 (v326, NEW):** spectral_zstat_v2 success template for this rescue -- identical recipe (vectorize + raise timeout).

## Memory adherence

- [[feedback-no-experiment-design-in-prompts]]: this rescue spec hands TASK + WHY + CONTRACT + IMPLEMENTATION SKETCH; exp_dev retains autonomy on: variable names, exact wall-time prereg update, error-handling, partial-metrics seed-checkpoint integration with vectorized loop.
- [[feedback-per-experiment-timeout-required]]: queue.json timeout matches prereg budget 3600s (no mismatch).
- [[feedback-rescue-sketch-first-sequencing]]: R2 is cheapest viable rescue (R1 0-compute subsumption applied inline in v327 cap_map; R3 reduce-probes secondary if R2 hits implementation friction; R4/R5 deferred).
- [[feedback-lock-in-inefficiency-fixes]]: structural pattern -- "non-vectorized inner loop + tight timeout = TIMEOUT" is now the 2nd-instance design-fault (I-2 + I-3); exp_dev should ADD to script-design checklist "Hutchinson / Monte-Carlo / probe-style estimators MUST batch probes via GEMM not GEMV".

## Expected outcome

- Wall: ~600-1200s (well within 3600s budget).
- Verdict: HARD_PASS (smoke result already at min_sigma_sep=12.5 >> HP=4.0; theory_ratio=12.59 within 20.0x band; math is correct; v1 was strictly an implementation timeout).
- Cap_map impact: kappa3_hutchinson_v2 GENUINE_FULL_HARD_PASS = empirical anchor for free-Poisson signature (currently PP-33 framework-class sub-property candidate). If 10x ratio holds: PP-33d sub-candidate corroborated (joint with PP-37). If theory_ratio collapses to ~1.0 at production-scope multi-seed: theory-empirical reconciled and PP-33d weakens.

Acted-on 2026-06-02: kappa3_v2 shipped + HP'd FULL with 32.8-sigma; Wave 1 spectral primitive validated; Wave 5 cell 2 (kappa_4/kappa_6 fingerprint at N=32768) is on solid footing
