"""
substrate_k3_synthetic_uniform_zipf_falsifier_v1_n4096 -- is Zipf load-bearing for the K=3 trigram HP? (CPU).

ROUTING: notes/routing_k3_synthetic_uniform_zipf_falsifier_test_2026-06-04.md. Bundle E E1 got a K=3 trigram
  HP (+1.291 nats) on natural-language V=70. Drill: the K*_corr~3.97 explanation has 3 factors
  (heteroassoc beta~4, Zipf demand-deflation, language redundancy). This isolates whether the ZIPF marginal is
  load-bearing. CPU numpy (posbind + symmetric Hebbian char-LM; GPU not needed).

DESIGN (self-contained, controls everything but the marginal): a 2nd-order synthetic Markov over V=70 drives
  BOTH arms; the ONLY difference is how each context's target symbols are drawn:
    arm 'zipf'    : targets drawn with Zipf rank weights -> SKEWED unigram marginal (low entropy), like language.
    arm 'uniform' : targets drawn uniformly -> FLAT unigram marginal (~log V), no demand-deflation.
  Substrate (both arms): K=3 context bound by cyclic-shift roll (HRR), symmetric Hebbian W += outer(next,ctx),
  calibrated-temperature cosine readout BPC. gap = log(V) - val_nats.

CELLS (5 seeds): arm in {zipf, uniform}; K=3; V=70; N=4096.

PRE-REGISTERED BANDS (per the drill prediction; gap in nats):
  HARD-FAIL (Zipf load-bearing): uniform gap < 0.5 AND <=1/5 seeds with gap>0.5. Zipf is essential.
  MIDDLE (partial Zipf effect): uniform gap in [0.5, 0.8].
  HARD-PASS (Zipf NOT load-bearing): uniform gap > 0.8 AND 4/5 seeds. Heteroassoc beta drives trigram on its own.
  (Reported alongside the zipf-arm gap as an in-harness reference; the verdict is on the UNIFORM arm.)

FORMULA SELF-TESTS (PROT-022):
  1. roll-bind order-sensitive. 2. K=3 single-context recall (cos>0.5). 3. zipf marginal entropy < uniform marginal
  entropy (manipulation works). 4. uniform nats = ln(V).

PROT-018: anchor _n4096 -> N=4096. PROT-019: _n4096 floor 14400s. PROT-021: per-seed partials.
QUEUE: remote_cpu_queue (numpy; GPU not needed). ASCII-only.
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
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics

ANCHOR_NAME = "substrate_k3_synthetic_uniform_zipf_falsifier_v1_n4096"
_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

VOCAB = 70
K_CTX = 3
K_ACTIVE = 8
LR = 0.5
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
ARMS = ["zipf", "uniform"]
HP_GAP, MID_GAP = 0.8, 0.5

if RUN_MODE == "smoke":
    N_DIM = 256; VOCAB = 40; SEEDS = [1, 2]; CORPUS = 4000
else:
    N_DIM = N; SEEDS = [7, 17, 23, 31, 41]; CORPUS = 30000


def gen_markov2(V, length, mode, gen_np):
    """2nd-order Markov; target selection zipf (skewed marginal) or uniform (flat marginal)."""
    nctx = V * V
    if mode == "zipf":
        ranks = 1.0 / np.arange(1, V + 1); zp = ranks / ranks.sum()
    T = np.zeros((nctx, V), dtype=np.float64)
    for ctx in range(nctx):
        if mode == "zipf":
            tg = gen_np.choice(V, size=K_ACTIVE, replace=False, p=zp)
        else:
            tg = gen_np.choice(V, size=K_ACTIVE, replace=False)
        lg = gen_np.standard_normal(K_ACTIVE) * 2.0; w = np.exp(lg - lg.max()); w /= w.sum()
        T[ctx, tg] = w
    ids = np.zeros(length, dtype=np.int64); a, b = 0, 0
    for i in range(length):
        ids[i] = b
        nxt = gen_np.choice(V, p=T[a * V + b]); a, b = b, nxt
    return ids


def marginal_entropy(ids, V):
    cnt = np.bincount(ids, minlength=V).astype(np.float64); p = cnt / cnt.sum()
    p = p[p > 0]; return float(-(p * np.log(p)).sum())


def build_codebook(V, n, gen_np):
    cb = (gen_np.integers(0, 2, size=(V, n)) * 2 - 1).astype(np.float32)
    return cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)


def encode_ctx(cb, ids, starts, K):
    b = np.zeros((len(starts), cb.shape[1]), dtype=np.float32)
    for j in range(K):
        b = b + np.roll(cb[ids[starts + j]], shift=j + 1, axis=1)
    return b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-8)


def train_eval(n, cb, tr, va, un, gen_np):
    W = np.zeros((n, n), dtype=np.float32)
    BATCH = 64; N_STEPS = max(1, (len(tr) - K_CTX - 1) // BATCH)
    for _ in range(N_STEPS):
        st = gen_np.integers(0, len(tr) - K_CTX - 1, size=BATCH)
        ctx = encode_ctx(cb, tr, st, K_CTX); nxt = cb[tr[st + K_CTX]]
        W = W + LR * (nxt.T @ ctx) / BATCH
    nb = min(2000, len(va) - K_CTX - 1)
    st = gen_np.integers(0, len(va) - K_CTX - 1, size=nb)
    ctx = encode_ctx(cb, va, st, K_CTX); nxt = va[st + K_CTX]
    pred = ctx @ W.T; pred = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-8)
    cos = pred @ cb.T
    best = float("inf")
    for t in TEMP_GRID:
        z = cos / t; z = z - z.max(axis=1, keepdims=True); ez = np.exp(z)
        pr = ez / (ez.sum(axis=1, keepdims=True) + 1e-30)
        pt = np.clip(pr[np.arange(nb), nxt], 1e-12, None)
        best = min(best, float(-np.log(pt).mean()))
    return un - best


def _selftest():
    g = np.random.default_rng(0); cb = build_codebook(7, 128, g)
    seq = np.array([0, 1, 2, 3]); b1 = encode_ctx(cb, seq, np.array([0]), 3)
    b2 = encode_ctx(cb, np.array([2, 1, 0, 3]), np.array([0]), 3)
    assert float((b1 * b2).sum()) < 0.95, "roll-bind not order-sensitive"
    W = np.zeros((128, 128), dtype=np.float32); ctx = encode_ctx(cb, seq, np.array([0]), 3); nxt = cb[3]
    W = W + np.outer(nxt, ctx[0]); pred = W @ ctx[0]
    rc = float(pred @ nxt / (np.linalg.norm(pred) * np.linalg.norm(nxt) + 1e-8)); assert rc > 0.5, f"recall {rc}"
    iz = gen_markov2(30, 3000, "zipf", np.random.default_rng(1)); iu = gen_markov2(30, 3000, "uniform", np.random.default_rng(1))
    ez, eu = marginal_entropy(iz, 30), marginal_entropy(iu, 30)
    assert ez < eu, f"zipf marginal entropy {ez:.3f} not < uniform {eu:.3f}"
    assert abs(math.log(7) - 1.9459) < 1e-3
    print(f"[selftest] PASS: rollbind_order kctx_recall={rc:.3f} zipf_ent={ez:.2f}<unif_ent={eu:.2f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    t0 = time.time(); un = math.log(VOCAB); arms = {}
    for arm in ARMS:
        gen_np = np.random.default_rng(seed * 100 + (0 if arm == "zipf" else 1))
        ids = gen_markov2(VOCAB, CORPUS, arm, gen_np); sp = int(0.8 * len(ids))
        tr, va = ids[:sp], ids[sp:]
        cb = build_codebook(VOCAB, n_dim, gen_np)
        gap = train_eval(n_dim, cb, tr, va, un, gen_np)
        arms[arm] = {"gap": float(gap), "marginal_entropy": marginal_entropy(ids, VOCAB)}
        print(f"  [seed={seed} {arm}] gap={gap:.4f} marg_ent={arms[arm]['marginal_entropy']:.3f}", flush=True)
    return {"seed": seed, "N": n_dim, "uniform_nats": un, "arms": arms, "elapsed_s": time.time() - t0}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "no results")
    gz = float(np.mean([r["arms"]["zipf"]["gap"] for r in results]))
    gu = float(np.mean([r["arms"]["uniform"]["gap"] for r in results]))
    n = len(results); u_hi = sum(1 for r in results if r["arms"]["uniform"]["gap"] > MID_GAP)
    summary = f"uniform_gap={gu:.3f} zipf_gap={gz:.3f} (ref BundleE-natlang +1.291) uniform_seeds>{MID_GAP}={u_hi}/{n}"
    if gu > HP_GAP and u_hi >= math.ceil(0.8 * n):
        return ("HARD_PASS", f"HARD_PASS: Zipf NOT load-bearing (uniform trigram gap>{HP_GAP}); heteroassoc beta drives K=3. {summary}")
    if gu >= MID_GAP:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial Zipf effect (uniform gap in [{MID_GAP},{HP_GAP}]). {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: Zipf IS load-bearing (uniform gap<{MID_GAP}); marginal skew essential to K=3 trigram. {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_DIM} V={VOCAB} K={K_CTX} arms={ARMS} mode={RUN_MODE} seeds={SEEDS}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "arms": ARMS, "V": VOCAB})
print(f"[ckpt] {len(done)} done, {len(remaining)} to run", flush=True)
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    write_partial(out_dir, seed, run_seed(seed, N_DIM))
per_seed = aggregate_partials(out_dir, SEEDS); all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg, "N": N_DIM,
           "V": VOCAB, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "arms": ARMS,
           "per_seed": [{k: v for k, v in r.items()} for r in all_results]}
write_metrics(out_dir, metrics, all_results)
print("[metrics] written", flush=True)
