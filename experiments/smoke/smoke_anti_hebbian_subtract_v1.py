"""
smoke_anti_hebbian_subtract_v1 -- Shotgun smoke: is -ACh*E_neg subtraction the load-bearing axis?

QUESTION:
  dual-trace drill predicted the anti-Hebbian subtraction term (-ACh*E_neg) is the key lever.
  Smoke with 3 arms at tiny scale to confirm or deny.

3 ARMS at N=256 N_TRAIN=2000 synthetic Zipf V=200 seeds=[7,17,23]:
  ARM_NO_SUBTRACT:    only +dopa*E_pos; no -ACh*E_neg
  ARM_WITH_SUBTRACT:  full dual-trace (+dopa*E_pos - ACh*E_neg)
  ARM_SUBTRACT_2X:    +dopa*E_pos - 2*ACh*E_neg (double the subtraction)

Metric: nearest-neighbor prediction BPC (nats) on held-out bigram; lower=better.
Uniform baseline = ln(V).

HARD_INFO band:
  - WITH >> NO_SUBTRACT -> subtraction IS the lever
  - SUBTRACT_2X >> WITH_SUBTRACT -> subtraction is monotonic-better
  - NO_SUBTRACT ~~ WITH_SUBTRACT -> subtraction NOT the lever

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
V = 200
N_TRAIN = 2000
N_HELD = 500
SEEDS = [7, 17, 23]

# Dual-trace timescales
TAU_POS = 5     # fast LTP trace (dopamine / prediction error)
TAU_NEG = 50    # slow LTD trace (ACh / attention)
NEUROMOD_CONTEXT = 8   # window for ACh centroid

# Sparse fraction for codebook
SPARSE_F = 0.10

# Temperature grid for BPC eval
TEMP_GRID = [0.05, 0.1, 0.2, 0.5, 1.0]
LR = 0.1

ARMS = [
    "ARM_NO_SUBTRACT",
    "ARM_WITH_SUBTRACT",
    "ARM_SUBTRACT_2X",
]


# ---- Primitives ----

def make_sparse_codebook(V_size, n, f, rng):
    cb = np.zeros((V_size, n), dtype=np.float32)
    k = max(1, int(round(f * n)))
    for i in range(V_size):
        idx = rng.choice(n, size=k, replace=False)
        sgn = rng.integers(0, 2, size=k).astype(np.float32) * 2.0 - 1.0
        cb[i, idx] = sgn
    norms = np.linalg.norm(cb, axis=1, keepdims=True)
    norms = np.where(norms < 1e-12, 1.0, norms)
    return cb / norms


def gen_zipf_bigram(V_size, length, rng):
    """Generate Zipf-distributed token sequence and bigram transition matrix."""
    ranks = 1.0 / np.arange(1, V_size + 1)
    p_unigram = ranks / ranks.sum()
    # Sparse transition matrix: each token has K_ACTIVE preferred successors
    K_ACTIVE = max(3, V_size // 20)
    T = np.zeros((V_size, V_size), dtype=np.float64)
    for c in range(V_size):
        tgt = rng.choice(V_size, size=K_ACTIVE, replace=False, p=p_unigram)
        w = np.exp(rng.standard_normal(K_ACTIVE))
        w /= w.sum()
        T[c, tgt] = w
    # Sample sequence
    ids = np.zeros(length, dtype=np.int64)
    s = int(rng.choice(V_size, p=p_unigram))
    for i in range(length):
        ids[i] = s
        s = int(rng.choice(V_size, p=T[s]))
    # Ground-truth conditional entropy
    with np.errstate(divide='ignore', invalid='ignore'):
        ce = float((-np.sum(np.where(T > 0, T * np.log(T), 0.0), axis=1)).mean())
    return ids, T, ce


def eval_bpc(W, codebook, val_ids, temp_grid):
    """Evaluate BPC on held-out sequence. Lower is better."""
    best = float("inf")
    V_size = codebook.shape[0]
    cb = codebook / (np.linalg.norm(codebook, axis=1, keepdims=True) + 1e-12)
    n = len(val_ids) - 1
    src = codebook[val_ids[:n]]    # (n, D)
    nxt_ids = val_ids[1:]
    pred = src @ W.T               # (n, D) raw predictions
    pred_n = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-12)
    cos = pred_n @ cb.T            # (n, V)
    for T in temp_grid:
        z = cos / T
        z = z - z.max(axis=1, keepdims=True)
        ez = np.exp(z.astype(np.float64))
        pr = (ez / (ez.sum(axis=1, keepdims=True) + 1e-30)).astype(np.float32)
        pt = pr[np.arange(n), nxt_ids].clip(1e-12, None)
        nats = float((-np.log(pt)).mean())
        if nats < best:
            best = nats
    return best


def run_dual_trace_arm(arm, codebook, train_ids, val_ids, seed):
    """Train W with specified dual-trace variant. Returns best BPC (nats)."""
    rng = np.random.default_rng(seed + 7777)
    n_dim = codebook.shape[1]   # vector dimensionality (not vocab size)
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    E_pos = np.zeros((n_dim, n_dim), dtype=np.float32)
    E_neg = np.zeros((n_dim, n_dim), dtype=np.float32)

    # Sliding context window for ACh (familiarity / recent-context centroid)
    context_window = []

    decay_pos = 1.0 - 1.0 / TAU_POS
    decay_neg = 1.0 - 1.0 / TAU_NEG

    n_steps = len(train_ids) - 1
    for i in range(n_steps):
        src_id = int(train_ids[i])
        tgt_id = int(train_ids[i + 1])
        src = codebook[src_id]       # (D,)
        tgt = codebook[tgt_id]       # (D,)
        pred = W @ src               # (D,) prediction

        # cf-RPE: prediction error -> dopamine signal
        err = tgt - pred
        err_norm = float(np.linalg.norm(err))
        # Dopamine: high prediction error -> high dopa (phasic burst)
        dopa = min(1.5, err_norm / (np.sqrt(n_dim) * 0.1 + 1e-9))

        # Eligibility trace update (E_pos = fast LTP; LR-normalized)
        outer_tgt = np.outer(tgt, src)   # shape (D, D)
        E_pos = decay_pos * E_pos + (1.0 - decay_pos) * outer_tgt

        # ACh: familiarity signal (high when context is predictable)
        context_window.append(src_id)
        if len(context_window) > NEUROMOD_CONTEXT:
            context_window.pop(0)
        if len(context_window) >= 2:
            ctx_vecs = codebook[context_window]
            ctx_mean = ctx_vecs.mean(axis=0)
            # ACh ~ centroid coherence; low variation -> high familiarity
            ctx_dev = float(np.linalg.norm(ctx_mean)) / (np.sqrt(n_dim) + 1e-9)
            ach = float(np.clip(ctx_dev, 0.0, 1.5))
        else:
            ach = 0.0

        # Prediction outer product for E_neg (LTD trace)
        outer_pred = np.outer(pred / (np.linalg.norm(pred) + 1e-12), src)
        E_neg = decay_neg * E_neg + (1.0 - decay_neg) * outer_pred

        # Weight update per arm
        if arm == "ARM_NO_SUBTRACT":
            dW = dopa * E_pos
        elif arm == "ARM_WITH_SUBTRACT":
            dW = dopa * E_pos - ach * E_neg
        else:  # ARM_SUBTRACT_2X
            dW = dopa * E_pos - 2.0 * ach * E_neg

        W = W + LR * dW

    return eval_bpc(W, codebook, val_ids, TEMP_GRID)


# ---- Self-test ----

def _instrumentation_selftest():
    """Assert all arms produce finite BPC in plausible range at tiny scale."""
    rng = np.random.default_rng(0)
    V_t = 30
    n_dim_t = 64
    cb = make_sparse_codebook(V_t, n_dim_t, 0.15, rng)
    ids_t, _, _ = gen_zipf_bigram(V_t, 200, rng)
    unigram_nats = math.log(V_t)
    for arm in ARMS:
        bpc = run_dual_trace_arm(arm, cb, ids_t[:150], ids_t[150:], seed=0)
        assert math.isfinite(bpc), f"selftest {arm} BPC not finite"
        assert 0.0 < bpc < unigram_nats * 3.0, \
            f"selftest {arm} BPC={bpc:.3f} outside plausible [0, {unigram_nats * 3:.1f}]"
    print(f"[selftest] PASS anti_hebbian_subtract: all arms finite BPC", flush=True)


_instrumentation_selftest()


# ---- Main sweep ----

t0 = time.time()
uniform_nats = math.log(V)

all_results = {arm: [] for arm in ARMS}

for seed in SEEDS:
    rng = np.random.default_rng(seed)
    codebook = make_sparse_codebook(V, N_DIM, SPARSE_F, rng)
    ids, T_mat, ce_true = gen_zipf_bigram(V, N_TRAIN + N_HELD, rng)
    train_ids = ids[:N_TRAIN]
    val_ids = ids[N_TRAIN:]

    print(f"  [seed={seed}] V={V} N_DIM={N_DIM} N_TRAIN={N_TRAIN} "
          f"uniform_nats={uniform_nats:.3f} true_ce={ce_true:.3f}", flush=True)

    for arm in ARMS:
        bpc = run_dual_trace_arm(arm, codebook, train_ids, val_ids, seed)
        all_results[arm].append(bpc)
        lift = uniform_nats - bpc
        print(f"    [{arm}] bpc={bpc:.4f} lift={lift:.4f}", flush=True)

elapsed = time.time() - t0

print("\n=== ANTI_HEBBIAN_SUBTRACT SMOKE RESULTS ===", flush=True)
print(f"N={N_DIM} V={V} N_TRAIN={N_TRAIN} seeds={SEEDS}", flush=True)
print(f"uniform_nats={uniform_nats:.4f}", flush=True)
print(f"elapsed={elapsed:.1f}s", flush=True)
print("", flush=True)

no_mean = float(np.mean(all_results["ARM_NO_SUBTRACT"]))
with_mean = float(np.mean(all_results["ARM_WITH_SUBTRACT"]))
x2_mean = float(np.mean(all_results["ARM_SUBTRACT_2X"]))

for arm in ARMS:
    vals = all_results[arm]
    mean = float(np.mean(vals))
    lift = uniform_nats - mean
    print(f"  {arm}: mean_bpc={mean:.4f} mean_lift={lift:.4f} "
          f"per_seed={[f'{v:.4f}' for v in vals]}", flush=True)

print("\nHARD_INFO interpretation:", flush=True)
delta_with_vs_no = no_mean - with_mean  # positive = WITH is better
delta_2x_vs_with = with_mean - x2_mean  # positive = 2X is better

MEANINGFUL_DELTA = 0.05  # nats; >= 0.05 nats = meaningful lift

if delta_with_vs_no >= MEANINGFUL_DELTA:
    print(f"  SUBTRACTION IS THE LEVER: WITH beats NO_SUBTRACT by {delta_with_vs_no:.4f} nats", flush=True)
    if delta_2x_vs_with >= MEANINGFUL_DELTA:
        print(f"  SUBTRACTION MONOTONIC: 2X beats 1X by {delta_2x_vs_with:.4f} nats -- lever is robust", flush=True)
    elif delta_2x_vs_with < -MEANINGFUL_DELTA:
        print(f"  SUBTRACTION HAS OPTIMUM: 2X WORSE by {-delta_2x_vs_with:.4f} nats -- saturates before 2X", flush=True)
    else:
        print(f"  SUBTRACTION: 2X ~~ 1X (delta={delta_2x_vs_with:.4f}); plateau around ACh=1.0", flush=True)
else:
    print(f"  SUBTRACTION NOT THE LEVER: WITH ~~ NO_SUBTRACT (delta={delta_with_vs_no:.4f} nats)", flush=True)
    print(f"  -> Check cardinality / heterogeneity / timescale as alternate axis", flush=True)
