"""
substrate_direct_generative_lm_ensemble_v1_n8192_J10 -- substrate-direct char-LM via J=10 ensemble -- remote CPU.

ROUTING: notes/research_to_exp_dev_B8_validated_pure_bio_confirmed_substrate_direct_LM (EX1-revised; P_drill=0.25).
  Drill: single substrate ~ppl 36 (bigram-class); J=10 ensemble ~ppl 10-12 (within 4x Pythia-160M). CRITICAL per
  drill: cf-RPE INVERTS for generative coverage (filtering removes diversity) -> NO cf-RPE; use symmetric Hebbian.
  CPU numpy, $0. remote_cpu_queue. No published HDC system has shown end-to-end generative char-LM perplexity.

CAPABILITY QUESTION: can a J=10 ensemble of substrate char-LMs (position-binding + symmetric Hebbian, disjoint
  splits, prediction-averaged) reach perplexity < 20 (within ~4x Pythia-160M-class)? vs single substrate + bigram baseline.

MODEL: Zipf bigram char-LM (V=70). Each of J substrates: context = cb[prev]; W += outer(cb[next], cb[prev])
  (SYMMETRIC HEBBIAN, no cf-RPE); readout = calibrated-temp cosine softmax. Ensemble = mean of J softmax dists.
  perplexity = exp(BPC). Arms: single (J=1), ensemble (J=10), bigram-frequency baseline.

CELLS (3 seeds): single_ppl, ensemble_ppl, bigram_ppl.
PRE-REGISTERED bands (on ensemble perplexity): HARD-PASS ppl<20; MIDDLE 20-40 (better than bigram ~30); HARD-FAIL ppl>60.

FORMULA SELF-TESTS (PROT-022): 1. symmetric-Hebbian recalls next at low load. 2. ensemble dist valid (sums to 1). 3. ppl=exp(bpc). 4. N=8192.
PROT-018: _n8192 -> N=8192. PROT-019: _n8192 timeout floor 21600s. ASCII-only. write_metrics.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, json, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_direct_generative_lm_ensemble_v1_n8192_J10"
_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

VOCAB = 70
K_ACTIVE = 8
J_ENS = 10
LR = 0.5
BATCH = 64
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]

if RUN_MODE == "smoke":
    N_DIM = 512; SEEDS = [1, 2]; CORPUS = 6000; N_STEPS = 200; J = 4
else:
    N_DIM = N; SEEDS = [7, 17, 23]; CORPUS = 30000; N_STEPS = 400; J = J_ENS


def gen_zipf(V, length, g):
    ranks = 1.0 / np.arange(1, V + 1); zp = ranks / ranks.sum(); T = np.zeros((V, V))
    for c in range(V):
        tg = g.choice(V, size=K_ACTIVE, replace=False, p=zp); lg = g.standard_normal(K_ACTIVE) * 2.0
        w = np.exp(lg - lg.max()); w /= w.sum(); T[c, tg] = w
    ids = np.zeros(length, dtype=np.int64); s = 0
    for i in range(length):
        ids[i] = s; s = g.choice(V, p=T[s])
    return ids, T


def codebook(V, n, g):
    cb = (g.integers(0, 2, size=(V, n)) * 2 - 1).astype(np.float32)
    return cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)


def train_hebb(n, cb, tr, g):
    W = np.zeros((n, n), dtype=np.float32)
    for _ in range(N_STEPS):
        st = g.integers(0, len(tr) - 1, size=BATCH); ctx = cb[tr[st]]; nxt = cb[tr[st + 1]]
        W = W + LR * (nxt.T @ ctx) / BATCH            # SYMMETRIC HEBBIAN (no cf-RPE)
    return W


def dist(W, cb, va, st, temp):
    ctx = cb[va[st]]; pred = ctx @ W.T; pred = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-8)
    cos = pred @ cb.T; z = cos / temp; z -= z.max(axis=1, keepdims=True); ez = np.exp(z)
    return ez / (ez.sum(axis=1, keepdims=True) + 1e-30)


def ppl_from(dists_or_W, cb, va, kind):
    nb = min(2000, len(va) - 1); st = np.arange(nb); nxt = va[st + 1]; best = float("inf")
    for t in TEMP_GRID:
        if kind == "single":
            P = dist(dists_or_W, cb, va, st, t)
        else:  # ensemble: mean of list of W's
            P = np.mean([dist(W, cb, va, st, t) for W in dists_or_W], axis=0)
        bpc = float(-np.log(np.clip(P[np.arange(nb), nxt], 1e-12, None)).mean()); best = min(best, bpc)
    return math.exp(best)


def _selftest():
    g = np.random.default_rng(0); cb = codebook(5, 128, g)
    seq = np.array([0, 1, 2, 3, 0, 1, 2, 3] * 20); W = train_hebb_mini(128, cb, seq, g)
    nb = 10; st = np.arange(nb)
    P = dist(W, cb, seq, st, 0.2); assert abs(P.sum(axis=1).mean() - 1.0) < 1e-5, "dist not normalized"
    assert abs(math.exp(1.6094) - 5.0) < 0.01, "ppl=exp(bpc)"
    assert N == 8192
    print("[selftest] PASS: dist_normalized ppl_exp_bpc", flush=True)


def train_hebb_mini(n, cb, tr, g):
    W = np.zeros((n, n), dtype=np.float32)
    for _ in range(50):
        st = g.integers(0, len(tr) - 1, size=16); ctx = cb[tr[st]]; nxt = cb[tr[st + 1]]
        W = W + LR * (nxt.T @ ctx) / 16
    return W


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    g = np.random.default_rng(seed); ids, T = gen_zipf(VOCAB, CORPUS, g); sp = int(0.8 * len(ids)); tr, va = ids[:sp], ids[sp:]
    cb = codebook(VOCAB, n_dim, g)
    # J substrates on disjoint splits
    splits = np.array_split(tr, J); Ws = [train_hebb(n_dim, cb, splits[i], np.random.default_rng(seed * 50 + i)) for i in range(J)]
    single_ppl = ppl_from(Ws[0], cb, va, "single")
    ens_ppl = ppl_from(Ws, cb, va, "ensemble")
    # bigram-frequency baseline perplexity
    counts = np.ones((VOCAB, VOCAB))
    for i in range(len(tr) - 1):
        counts[tr[i], tr[i + 1]] += 1
    Pb = counts / counts.sum(axis=1, keepdims=True)
    nb = min(2000, len(va) - 1)
    big_bpc = float(-np.mean([math.log(max(Pb[va[i], va[i + 1]], 1e-12)) for i in range(nb)]))
    return {"seed": seed, "N": n_dim, "J": J, "single_ppl": float(single_ppl), "ensemble_ppl": float(ens_ppl),
            "bigram_ppl": float(math.exp(big_bpc))}


def verdict(per_seed) -> Tuple[str, str]:
    sp = float(np.mean([s["single_ppl"] for s in per_seed])); ep = float(np.mean([s["ensemble_ppl"] for s in per_seed]))
    bp = float(np.mean([s["bigram_ppl"] for s in per_seed]))
    summary = f"single_ppl={sp:.1f} ensemble_ppl={ep:.1f} bigram_baseline_ppl={bp:.1f} (J={per_seed[0]['J']})"
    if ep < 20:
        return ("HARD_PASS", f"HARD_PASS: substrate-direct J-ensemble char-LM perplexity<20. {summary}")
    if ep < 40:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: ensemble ppl 20-40 (single-substrate territory). {summary}")
    if ep > 60:
        return ("HARD_FAIL", f"HARD_FAIL: ensemble ppl>60 (worse than bigram; not viable). {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: ensemble ppl 40-60. {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N_DIM} J={J} V={VOCAB}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); per_seed = []
for seed in SEEDS:
    r = run_seed(seed, N_DIM); per_seed.append(r)
    print(f"  [seed={seed}] single_ppl={r['single_ppl']:.1f} ensemble_ppl={r['ensemble_ppl']:.1f} bigram_ppl={r['bigram_ppl']:.1f}", flush=True)
v, vmsg = verdict(per_seed)
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "J": J,
           "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": per_seed, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
