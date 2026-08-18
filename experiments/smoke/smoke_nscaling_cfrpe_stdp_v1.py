"""
smoke_nscaling_cfrpe_stdp_v1 -- Shotgun smoke: N-scaling for cf-RPE x STDP heterogeneous.

QUESTION:
  At N=512 cf-RPE ALONE (gap=4.77) outperformed cf-RPE x STDP HETEROGENEOUS (gap=5.02)?
  Wait -- 5.02 > 4.77, so HETEROGENEOUS WAS better at N=512. The Fix #28 concern was that
  HETEROGENEOUS arm was supposed to be 5.02 but cf-RPE alone was the EXPECTED winner.
  Per task spec: check if heterogeneity becomes net-beneficial at N=1024+.
  Does the gap GROW with N (heterogeneity scales better) or SHRINK (diminishing returns)?

2 ARMS x 4 N-values x 3 seeds at synthetic Zipf V=512 N_TRAIN=2000:
  ARM_CFRPE_ONLY       (single-rule cf-RPE delta)
  ARM_CFRPE_STDP_HET   (cf-RPE + STDP asymmetric; same as C1_cfrpe_stdp)

N in {128, 256, 512, 1024}

HARD_INFO band:
  - Identify N where HETEROGENEOUS inverts to beat CFRPE_ONLY (if not yet at N=512)
  - If HETEROGENEOUS consistently better: predict FULL at N=8192 will also HARD_PASS
  - If HETEROGENEOUS never beats CFRPE_ONLY by N=1024: predict N=8192 HARD_FAIL

No cert atomization. Information acquisition only. Pure CPU/numpy.
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
VOCAB = 512
N_TRAIN = 2000
CORPUS = 8000
SEEDS = [7, 17, 23]
N_VALUES = [128, 256, 512, 1024]

K_ACTIVE = 8    # active targets per token in bigram matrix
LR = 0.5
BATCH = 64
N_STEPS = 300   # enough for convergence at small N
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]

ARMS = ["ARM_CFRPE_ONLY", "ARM_CFRPE_STDP_HET"]


# ---- Primitives ----

def gen_zipf(V, length, rng):
    ranks = 1.0 / np.arange(1, V + 1)
    zp = ranks / ranks.sum()
    T = np.zeros((V, V), dtype=np.float64)
    for c in range(V):
        tgt = rng.choice(V, size=K_ACTIVE, replace=False, p=zp)
        lg = rng.standard_normal(K_ACTIVE) * 2.0
        w = np.exp(lg - lg.max())
        w /= w.sum()
        T[c, tgt] = w
    with np.errstate(divide='ignore', invalid='ignore'):
        ce = float((-np.sum(np.where(T > 0, T * np.log(T), 0.0), axis=1)).mean())
    ids = np.zeros(length, dtype=np.int64)
    s = int(rng.choice(V, p=zp))
    for i in range(length):
        ids[i] = s
        s = int(rng.choice(V, p=T[s]))
    return ids, ce


def build_codebook(V_size, n, rng):
    cb = (rng.integers(0, 2, size=(V_size, n)).astype(np.float32) * 2.0 - 1.0)
    norms = np.linalg.norm(cb, axis=1, keepdims=True)
    return cb / (norms + 1e-12)


def train_eval_arm(arm, n, cb, train_ids, val_ids, rng):
    """Train W and return best BPC (nats) over temperature grid."""
    W = np.zeros((n, n), dtype=np.float32)
    n_train = len(train_ids)

    for _ in range(N_STEPS):
        st = rng.integers(0, n_train - 1, size=BATCH)
        Ctx = cb[train_ids[st]]    # (BATCH, n)
        Nxt = cb[train_ids[st + 1]]  # (BATCH, n)
        Heb = (Nxt.T @ Ctx) / BATCH

        if arm == "ARM_CFRPE_ONLY":
            # cf-RPE: error = Nxt - Ctx @ W.T = prediction residual
            pred = Ctx @ W.T        # (BATCH, n)
            delta = Nxt - pred      # (BATCH, n)
            dW = (delta.T @ Ctx) / BATCH
        else:  # ARM_CFRPE_STDP_HET
            pred = Ctx @ W.T
            delta = Nxt - pred
            cf = (delta.T @ Ctx) / BATCH
            # STDP asymmetric part: W_STDP = outer(Nxt, Ctx) - outer(Ctx, Nxt)
            Asym = (Nxt.T @ Ctx - Ctx.T @ Nxt) / BATCH
            dW = cf + 0.5 * Asym

        W = W + LR * dW

    # Evaluation: nearest-neighbor softmax BPC
    n_val = len(val_ids) - 1
    if n_val <= 0:
        return float("inf")
    ctx_v = cb[val_ids[:n_val]]    # (n_val, n)
    nxt_ids_v = val_ids[1:]
    pred_v = ctx_v @ W.T           # (n_val, n)
    pred_n = pred_v / (np.linalg.norm(pred_v, axis=1, keepdims=True) + 1e-12)
    cos = pred_n @ cb.T            # (n_val, V)
    best = float("inf")
    for T in TEMP_GRID:
        z = cos / T
        z = z - z.max(axis=1, keepdims=True)
        ez = np.exp(z.astype(np.float64))
        pr = (ez / (ez.sum(axis=1, keepdims=True) + 1e-30)).astype(np.float32)
        pt = pr[np.arange(n_val), nxt_ids_v].clip(1e-12, None)
        nats = float((-np.log(pt)).mean())
        if nats < best:
            best = nats
    return best


# ---- Self-test ----

def _instrumentation_selftest():
    """Assert both arms produce finite BPC and N-scaling doesn't explode."""
    rng = np.random.default_rng(0)
    ids_t, _ = gen_zipf(32, 400, rng)
    for n_t in [64, 128]:
        cb = build_codebook(32, n_t, rng)
        for arm in ARMS:
            bpc = train_eval_arm(arm, n_t, cb, ids_t[:300], ids_t[300:], rng)
            assert math.isfinite(bpc), f"selftest {arm} N={n_t} BPC not finite"
            assert 0.0 < bpc < math.log(32) * 5, \
                f"selftest {arm} N={n_t} BPC={bpc:.3f} implausible"
    # Verify gen_zipf conditional entropy < log(V)
    ids_v, ce_v = gen_zipf(64, 2000, rng)
    assert ce_v < math.log(64), f"selftest Zipf ce={ce_v:.3f} >= log(64)={math.log(64):.3f}"
    print(f"[selftest] PASS nscaling_cfrpe_stdp: all arms finite both N; "
          f"zipf_ce={ce_v:.3f} < log(V)={math.log(64):.3f}", flush=True)


_instrumentation_selftest()


# ---- Main sweep ----

t0_total = time.time()
uniform_nats = math.log(VOCAB)
print(f"uniform_nats={uniform_nats:.4f} (V={VOCAB})", flush=True)

# results[arm][n] = list of BPC across seeds
results = {arm: {n: [] for n in N_VALUES} for arm in ARMS}

for seed in SEEDS:
    rng = np.random.default_rng(seed)
    ids, ce = gen_zipf(VOCAB, CORPUS, rng)
    split = N_TRAIN
    train_ids = ids[:split]
    val_ids = ids[split:]

    print(f"  [seed={seed}] corpus={CORPUS} N_TRAIN={split} "
          f"N_val={len(val_ids)} true_ce={ce:.3f}", flush=True)

    for n_val in N_VALUES:
        rng_cb = np.random.default_rng(seed + n_val * 37)
        cb = build_codebook(VOCAB, n_val, rng_cb)
        rng_tr = np.random.default_rng(seed + n_val * 37 + 1)

        for arm in ARMS:
            bpc = train_eval_arm(arm, n_val, cb, train_ids, val_ids, rng_tr)
            gap = uniform_nats - bpc
            results[arm][n_val].append(bpc)
            print(f"    [N={n_val}] {arm}: bpc={bpc:.4f} gap={gap:.4f}", flush=True)

elapsed = time.time() - t0_total

print("\n=== NSCALING_CFRPE_STDP SMOKE RESULTS ===", flush=True)
print(f"V={VOCAB} N_TRAIN={N_TRAIN} seeds={SEEDS}", flush=True)
print(f"uniform_nats={uniform_nats:.4f}", flush=True)
print(f"elapsed={elapsed:.1f}s", flush=True)
print("", flush=True)

# Summary table
print(f"{'N':>6}  {'CFRPE_mean':>12}  {'CFRPE_gap':>10}  "
      f"{'STDP_HET_mean':>14}  {'STDP_HET_gap':>12}  {'het_delta':>10}  {'verdict':>16}", flush=True)
print("-" * 90, flush=True)

inversion_N = None
for n_val in N_VALUES:
    cf_bpc = float(np.mean(results["ARM_CFRPE_ONLY"][n_val]))
    het_bpc = float(np.mean(results["ARM_CFRPE_STDP_HET"][n_val]))
    cf_gap = uniform_nats - cf_bpc
    het_gap = uniform_nats - het_bpc
    delta = het_gap - cf_gap   # positive = HET is better
    verdict = ""
    if delta > 0.05:
        verdict = "HET_WINS"
        if inversion_N is None:
            inversion_N = n_val
    elif delta < -0.05:
        verdict = "CF_WINS"
    else:
        verdict = "TIED"
    print(f"{n_val:>6}  {cf_bpc:>12.4f}  {cf_gap:>10.4f}  "
          f"{het_bpc:>14.4f}  {het_gap:>12.4f}  {delta:>10.4f}  {verdict:>16}", flush=True)

print("", flush=True)
print("HARD_INFO interpretation:", flush=True)
if inversion_N is not None:
    print(f"  INVERSION at N={inversion_N}: STDP_HETEROGENEOUS beats CFRPE_ONLY", flush=True)
    print(f"  Predict: FULL at N=8192 will likely HARD_PASS (heterogeneity scales)", flush=True)
else:
    # Check if HET was consistently worse or tied
    max_delta = max(
        float(np.mean(results["ARM_CFRPE_STDP_HET"][n])) - float(np.mean(results["ARM_CFRPE_ONLY"][n]))
        for n in N_VALUES
    )
    # max_delta here is raw bpc delta; negative = HET has lower BPC = better
    het_better_any = any(
        float(np.mean(results["ARM_CFRPE_ONLY"][n])) - float(np.mean(results["ARM_CFRPE_STDP_HET"][n])) > 0.05
        for n in N_VALUES
    )
    if het_better_any:
        print(f"  HET better at some N but gap < threshold; monitor at N=2048+", flush=True)
    else:
        print(f"  NO INVERSION through N={max(N_VALUES)}: HETEROGENEOUS does not beat CFRPE_ONLY", flush=True)
        print(f"  Predict: FULL at N=8192 likely HARD_FAIL (heterogeneity never dominant)", flush=True)
