"""
smoke_compose_order_v1 -- Shotgun smoke: which compose step breaks the theta-gamma pipeline?

QUESTION:
  N4096_v1 HARD_FAIL: nested_sparse alone fine (1.000), nested_cleanup alone fine (1.000),
  but composed ARM_NESTED_BRAIN_FULL collapsed to 0.187 at sigma=16. Which ordering breaks it?

6 ARMS at N=256 M=50 sigma=16 seeds=[7,17,23]:
  ARM_BASELINE_LOCKIN_ALONE
  ARM_LOCKIN_THEN_SPARSE           (lock-in demod on dense -> then sparsify output)
  ARM_LOCKIN_THEN_CLEANUP          (lock-in demod on dense -> then Hopfield cleanup)
  ARM_LOCKIN_THEN_SPARSE_THEN_CLEANUP  (order A->B->C)
  ARM_LOCKIN_THEN_CLEANUP_THEN_SPARSE  (order A->C->B)
  ARM_SPARSE_INPUT_THEN_LOCKIN_THEN_CLEANUP  (sparsify BEFORE lock-in)

HARD_INFO band:
  - Any arm in {2..6} within 0.05 of BASELINE -> that compose step is "free" (constructive)
  - Any arm below 0.5 recall -> that ORDER is destructive; identify the breakage step

No cert atomization. Information acquisition only.
ASCII-only. No emojis.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import math
import time
import numpy as np

# ---- Config ----
N_DIM = 256
M = 50
SIGMA = 16.0
SEEDS = [7, 17, 23]
P_THETA = 4
P_GAMMA = 7
K_THETA = 1
K_GAMMA = 31
P_SINGLE = 32
K_SINGLE = 31
SPARSE_F = 0.10   # at N=256: 0.10 -> 26 active; 0.02 -> 5 active (too few); use 0.10
CLEANUP_TAU = 0.30
CLEANUP_TEMP = 4.0
N_EVAL = 80


# ---- Core primitives (inlined; no external import) ----

def _roll(arr: np.ndarray, shift: int) -> np.ndarray:
    return np.roll(arr, shift, axis=-1)


def single_lockin(cues: np.ndarray, P: int, k: int, sigma: float, rng) -> np.ndarray:
    """Single-frequency lock-in demod. Returns (B, N) estimate."""
    if P == 1:
        return cues + sigma * rng.standard_normal(cues.shape).astype(np.float32)
    B, N = cues.shape
    acc = np.zeros_like(cues)
    for p in range(P):
        c = math.cos(2.0 * math.pi * p / P)
        rolled = _roll(cues, p * k)
        noise = sigma * rng.standard_normal((B, N)).astype(np.float32)
        acc += _roll(rolled * c + noise, -(p * k)) * c
    return (2.0 / P) * acc


def theta_gamma_lockin(cues: np.ndarray, P_th: int, P_gm: int, k_th: int, k_gm: int,
                        sigma: float, rng) -> np.ndarray:
    """Two-frequency nested lock-in demod. Returns (B, N) estimate."""
    B, N = cues.shape
    acc = np.zeros_like(cues)
    norm = (2.0 / P_th) * (2.0 / P_gm)
    for t in range(P_th):
        wt = math.cos(2.0 * math.pi * t / P_th)
        for g in range(P_gm):
            wg = math.cos(2.0 * math.pi * g / P_gm)
            carrier = wt * wg
            shift = t * k_th + g * k_gm
            noise = sigma * rng.standard_normal((B, N)).astype(np.float32)
            acc += _roll(_roll(cues, shift) * carrier + noise, -shift) * carrier
    return norm * acc


def sparsify(x: np.ndarray, f: float) -> np.ndarray:
    """Keep top-f fraction by magnitude, bipolar sign. (B, N) -> (B, N)."""
    if x.ndim == 1:
        x = x[None]
        squeeze = True
    else:
        squeeze = False
    B, N = x.shape
    k = max(1, int(round(f * N)))
    out = np.zeros_like(x)
    for i in range(B):
        idx = np.argpartition(np.abs(x[i]), -k)[-k:]
        out[i, idx] = np.sign(x[i, idx])
        out[i, idx[out[i, idx] == 0]] = 1.0
    if squeeze:
        return out[0]
    return out


def hopfield_cleanup(x: np.ndarray, codebook: np.ndarray,
                     tau: float, temp: float) -> np.ndarray:
    """Soft-attractor cleanup with refuse-gate. (B, N) x (M, N) -> (B, N)."""
    if x.ndim == 1:
        x = x[None]
        squeeze = True
    else:
        squeeze = False
    cb_n = codebook / (np.linalg.norm(codebook, axis=1, keepdims=True) + 1e-12)
    sqrt_N = float(np.sqrt(x.shape[1]))
    x_n = x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-12)
    scores = temp * sqrt_N * (x_n @ cb_n.T)   # (B, M)
    # softmax
    s_shifted = scores - scores.max(axis=1, keepdims=True)
    exp_s = np.exp(s_shifted.astype(np.float64)).astype(np.float32)
    weights = exp_s / (exp_s.sum(axis=1, keepdims=True) + 1e-30)
    snapped = weights @ cb_n   # (B, N) unit-norm blended
    top_cos = scores.max(axis=1) / (temp * sqrt_N + 1e-12)
    accept = (top_cos >= tau).astype(np.float32)[:, None]
    # rescale snapped to match input norm
    x_norms = np.linalg.norm(x, axis=1, keepdims=True)
    result = accept * snapped * x_norms + (1.0 - accept) * x
    if squeeze:
        return result[0]
    return result


def recall_at_1(decoded: np.ndarray, codebook: np.ndarray, targets: np.ndarray) -> float:
    scores = decoded @ codebook.T
    return float((scores.argmax(axis=1) == targets).mean())


# ---- Self-test ----

def _instrumentation_selftest():
    """Assert all arms produce finite non-sentinel recall at sigma=0."""
    rng = np.random.default_rng(0)
    N_t = 64; M_t = 20
    cb = rng.standard_normal((M_t, N_t)).astype(np.float32)
    cb_n = cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-12)
    sp_cb = np.zeros_like(cb_n)
    for i in range(M_t):
        k = max(1, int(round(0.10 * N_t)))
        idx = rng.choice(N_t, size=k, replace=False)
        sgn = rng.integers(0, 2, size=k).astype(np.float32) * 2.0 - 1.0
        sp_cb[i, idx] = sgn
    tgt = np.array([0, 5, 10, 15])
    cues_d = cb_n[tgt]
    cues_s = sp_cb[tgt]

    # ARM_BASELINE_LOCKIN: sigma=0 must give recall >= 0.90
    decoded = single_lockin(cues_d.copy(), P=4, k=31, sigma=0.0, rng=np.random.default_rng(1))
    r = recall_at_1(decoded, cb_n, tgt)
    assert r >= 0.90, f"selftest BASELINE sigma=0 recall={r:.3f} < 0.90"

    # ARM_LOCKIN_THEN_SPARSE: result is non-null, finite
    dec2 = single_lockin(cues_d.copy(), P=4, k=31, sigma=0.0, rng=np.random.default_rng(2))
    dec2_s = sparsify(dec2, f=0.10)
    assert np.isfinite(dec2_s).all(), "selftest SPARSE output has non-finite"

    # ARM_LOCKIN_THEN_CLEANUP: result is non-null, finite
    dec3 = single_lockin(cues_d.copy(), P=4, k=31, sigma=0.0, rng=np.random.default_rng(3))
    dec3_c = hopfield_cleanup(dec3, cb_n, tau=0.0, temp=4.0)  # tau=0: always accept
    assert np.isfinite(dec3_c).all(), "selftest CLEANUP output has non-finite"
    r3 = recall_at_1(dec3_c, cb_n, tgt)
    assert r3 >= 0.90, f"selftest CLEANUP sigma=0 recall={r3:.3f} < 0.90"

    # sparsify-before-lockin: sparse input must still give finite output
    dec6 = single_lockin(cues_s.copy(), P=4, k=31, sigma=0.0, rng=np.random.default_rng(4))
    assert np.isfinite(dec6).all(), "selftest SPARSE_INPUT output has non-finite"

    print(f"[selftest] PASS compose_order: baseline_r={r:.3f} cleanup_r={r3:.3f}", flush=True)


_instrumentation_selftest()


# ---- Main sweep ----

def make_dense_codebook(M, N, rng):
    cb = rng.standard_normal((M, N)).astype(np.float32)
    return cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-12)


def make_sparse_codebook(M, N, f, rng):
    cb = np.zeros((M, N), dtype=np.float32)
    k = max(1, int(round(f * N)))
    for i in range(M):
        idx = rng.choice(N, size=k, replace=False)
        sgn = rng.integers(0, 2, size=k).astype(np.float32) * 2.0 - 1.0
        cb[i, idx] = sgn
    return cb


ARMS = [
    "ARM_BASELINE_LOCKIN_ALONE",
    "ARM_LOCKIN_THEN_SPARSE",
    "ARM_LOCKIN_THEN_CLEANUP",
    "ARM_LOCKIN_THEN_SPARSE_THEN_CLEANUP",
    "ARM_LOCKIN_THEN_CLEANUP_THEN_SPARSE",
    "ARM_SPARSE_INPUT_THEN_LOCKIN_THEN_CLEANUP",
]

results = {arm: [] for arm in ARMS}

t0_total = time.time()
for seed in SEEDS:
    rng = np.random.default_rng(seed)
    rng_eval = np.random.default_rng(seed + 1000)

    dense_cb = make_dense_codebook(M, N_DIM, rng)
    sparse_cb = make_sparse_codebook(M, N_DIM, SPARSE_F, rng)

    # Build cue indices and cues
    idx = rng_eval.integers(0, M, size=N_EVAL)
    cues_d = dense_cb[idx]    # (N_EVAL, N_DIM) dense cues
    cues_s = sparse_cb[idx]   # sparse cues for ARM 6

    def _rng():
        return np.random.default_rng(seed + 9999)

    # ARM 1: single lock-in on dense (baseline)
    dec1 = single_lockin(cues_d.copy(), P=P_SINGLE, k=K_SINGLE, sigma=SIGMA, rng=_rng())
    r1 = recall_at_1(dec1, dense_cb, idx)
    results["ARM_BASELINE_LOCKIN_ALONE"].append(r1)

    # ARM 2: lock-in -> sparsify output (but retrieve against DENSE codebook)
    dec2 = single_lockin(cues_d.copy(), P=P_SINGLE, k=K_SINGLE, sigma=SIGMA, rng=_rng())
    dec2_sp = sparsify(dec2, f=SPARSE_F)
    # Use sparse_cb for retrieval since output is sparse-like
    r2 = recall_at_1(dec2_sp, sparse_cb, idx)
    results["ARM_LOCKIN_THEN_SPARSE"].append(r2)

    # ARM 3: lock-in -> cleanup (stay dense throughout)
    dec3 = single_lockin(cues_d.copy(), P=P_SINGLE, k=K_SINGLE, sigma=SIGMA, rng=_rng())
    dec3_cl = hopfield_cleanup(dec3, dense_cb, tau=CLEANUP_TAU, temp=CLEANUP_TEMP)
    r3 = recall_at_1(dec3_cl, dense_cb, idx)
    results["ARM_LOCKIN_THEN_CLEANUP"].append(r3)

    # ARM 4: lock-in -> sparse -> cleanup (A->B->C; codebook=sparse)
    dec4 = single_lockin(cues_d.copy(), P=P_SINGLE, k=K_SINGLE, sigma=SIGMA, rng=_rng())
    dec4_sp = sparsify(dec4, f=SPARSE_F)
    dec4_cl = hopfield_cleanup(dec4_sp, sparse_cb, tau=CLEANUP_TAU, temp=CLEANUP_TEMP)
    r4 = recall_at_1(dec4_cl, sparse_cb, idx)
    results["ARM_LOCKIN_THEN_SPARSE_THEN_CLEANUP"].append(r4)

    # ARM 5: lock-in -> cleanup -> sparse (A->C->B; cleanup first, then sparsify)
    dec5 = single_lockin(cues_d.copy(), P=P_SINGLE, k=K_SINGLE, sigma=SIGMA, rng=_rng())
    dec5_cl = hopfield_cleanup(dec5, dense_cb, tau=CLEANUP_TAU, temp=CLEANUP_TEMP)
    dec5_sp = sparsify(dec5_cl, f=SPARSE_F)
    r5 = recall_at_1(dec5_sp, sparse_cb, idx)
    results["ARM_LOCKIN_THEN_CLEANUP_THEN_SPARSE"].append(r5)

    # ARM 6: sparsify INPUT first, then lock-in on sparse input, then cleanup
    dec6 = single_lockin(cues_s.copy(), P=P_SINGLE, k=K_SINGLE, sigma=SIGMA, rng=_rng())
    dec6_cl = hopfield_cleanup(dec6, sparse_cb, tau=CLEANUP_TAU, temp=CLEANUP_TEMP)
    r6 = recall_at_1(dec6_cl, sparse_cb, idx)
    results["ARM_SPARSE_INPUT_THEN_LOCKIN_THEN_CLEANUP"].append(r6)

    print(f"  [seed={seed}] "
          f"BASE={r1:.3f} SPARSE={r2:.3f} CLEANUP={r3:.3f} "
          f"S>C={r4:.3f} C>S={r5:.3f} SpIN={r6:.3f}", flush=True)

elapsed = time.time() - t0_total

print("\n=== COMPOSE_ORDER SMOKE RESULTS ===", flush=True)
print(f"N={N_DIM} M={M} sigma={SIGMA} seeds={SEEDS} f={SPARSE_F}", flush=True)
print(f"elapsed={elapsed:.1f}s", flush=True)
print("", flush=True)
r_baseline = None
for arm in ARMS:
    vals = results[arm]
    mean = float(np.mean(vals))
    if arm == "ARM_BASELINE_LOCKIN_ALONE":
        r_baseline = mean
    flag = ""
    if r_baseline is not None and arm != "ARM_BASELINE_LOCKIN_ALONE":
        delta = mean - r_baseline
        if abs(delta) <= 0.05:
            flag = "  [FREE -- constructive]"
        elif mean < 0.5:
            flag = "  [DESTRUCTIVE <0.5]"
        elif delta < -0.05:
            flag = f"  [DEGRADED delta={delta:.3f}]"
    print(f"  {arm}: mean={mean:.3f} per_seed={[f'{v:.3f}' for v in vals]}{flag}", flush=True)

print("\nHARD_INFO interpretation:", flush=True)
for arm in ARMS[1:]:
    mean = float(np.mean(results[arm]))
    delta = mean - r_baseline
    verdict = ""
    if abs(delta) <= 0.05:
        verdict = "FREE (constructive compose)"
    elif mean < 0.5:
        verdict = "DESTRUCTIVE (this step/order collapses recall)"
    elif delta < -0.20:
        verdict = "HARMFUL (significant degradation)"
    elif delta < -0.05:
        verdict = "MODEST_DEGRADATION"
    else:
        verdict = "BENEFICIAL"
    print(f"  {arm}: {verdict}", flush=True)
