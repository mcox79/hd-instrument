"""
substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512 -- cf-RPE x STDP heterogeneous pairing (GPU).

ROUTING: notes/routing_cfrpe_stdp_superadditive_test_2026-06-04.md. Per the cf-RPE+sparse shared-axis drill:
  cf-RPE + sparse combined ADDITIVELY (both task-supervised axis -> collinear). Predicted HETEROGENEOUS
  pairings (task axis + temporal axis) compose SUPERADDITIVELY. cf-RPE (task) + STDP (temporal) is the
  cheapest test. Owned GPU, $0.

FOUR ARMS (5 seeds; synthetic V=512 Zipf bigram; N=512):
  A1 hebbian_k1 : one-shot symmetric Hebbian (baseline).
  A2 cfrpe      : cf-RPE delta (task-supervised axis).             [HP at bigram in Bundle A]
  A3 stdp       : W = W_Hebbian + 0.5*W_STDP-asymmetric (temporal). [MIDDLE at bigram in Bundle A]
  C1 cfrpe_stdp : cf-RPE delta + 0.5*W_STDP-asymmetric (both axes combined).

PRE-REGISTERED BANDS (BPC nats; gap = uniform - val):
  HARD-PASS (superadditive): C1 gap > 0.70 nats AND 4/5 seeds (orthogonal-axis sqrt-sum bound per drill).
  MIDDLE: C1 gap in [max(gap_cf, gap_stdp), 0.70].
  HARD-FAIL (still additive/sub-additive): C1 gap <= max(gap_cf, gap_stdp) (task+temporal still share an axis at bigram).

FORMULA SELF-TESTS (PROT-022):
  1. STDP antisym part W_STDP + W_STDP^T = 0. 2. cf-RPE shrinks single-pair error. 3. zipf cond-ent < log(V).
  4. uniform nats = ln(V).

PROT-018: anchor _n512 -> N=512. PROT-021: per-seed partials.
QUEUE: overnight_queue (GPU). GPU TEMPLATE: assert cuda + device='cuda' + batched matmul. ASCII-only.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda')
print(f"[GPU] {torch.cuda.get_device_name(0)}", flush=True)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics

ANCHOR_NAME = "substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512"
_N_SUFFIX = 512
N = 512
assert N == _N_SUFFIX

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LR = 0.5
BATCH = 64
VOCAB = 512
K_ACTIVE = 8
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
HP_SUPER = 0.70
ARMS = ["A1_hebbian_k1", "A2_cfrpe", "A3_stdp", "C1_cfrpe_stdp"]

if RUN_MODE == "smoke":
    N_DIM = 256; VOCAB = 128; SEEDS = [1, 2]; N_STEPS = 80; CORPUS = 6000
else:
    N_DIM = N; SEEDS = [7, 17, 23, 31, 41]; N_STEPS = 1000; CORPUS = 60000


def gen_zipf(V, length, gen_np):
    ranks = 1.0 / np.arange(1, V + 1); zp = ranks / ranks.sum()
    T = np.zeros((V, V))
    for c in range(V):
        tg = gen_np.choice(V, size=K_ACTIVE, replace=False, p=zp)
        lg = gen_np.standard_normal(K_ACTIVE) * 2.0; w = np.exp(lg - lg.max()); w /= w.sum(); T[c, tg] = w
    with np.errstate(divide='ignore', invalid='ignore'):
        ce = float((-np.sum(np.where(T > 0, T * np.log(T), 0.0), axis=1)).mean())
    ids = np.zeros(length, dtype=np.int64); s = 0
    for i in range(length):
        ids[i] = s; s = gen_np.choice(V, p=T[s])
    return ids, ce


def build_codebook(V, n, gen):
    cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    return cb / (cb.norm(dim=1, keepdim=True) + 1e-8)


def train_eval(arm, n, cb, tr, va, gen) -> float:
    W = torch.zeros(n, n, device=DEVICE); ntr = tr.shape[0]
    for _ in range(N_STEPS):
        st = torch.randint(0, ntr - 1, (BATCH,), generator=gen, device=DEVICE)
        Ctx = cb[tr[st]]; Nxt = cb[tr[st + 1]]
        Heb = (Nxt.t() @ Ctx) / BATCH
        if arm == "A1_hebbian_k1":
            dW = Heb
        elif arm == "A2_cfrpe":
            dW = ((Nxt - Ctx @ W.t()).t() @ Ctx) / BATCH
        elif arm == "A3_stdp":
            Asym = (Nxt.t() @ Ctx - Ctx.t() @ Nxt) / BATCH
            dW = Heb + 0.5 * Asym
        else:  # C1_cfrpe_stdp: cf-RPE task axis + STDP temporal axis
            cf = ((Nxt - Ctx @ W.t()).t() @ Ctx) / BATCH
            Asym = (Nxt.t() @ Ctx - Ctx.t() @ Nxt) / BATCH
            dW = cf + 0.5 * Asym
        W = W + LR * dW
    nb = min(2000, va.shape[0] - 1)
    st = torch.randint(0, va.shape[0] - 1, (nb,), generator=gen, device=DEVICE)
    ctx = cb[va[st]]; nxt = va[st + 1]
    pred = ctx @ W.t(); pn = pred / (pred.norm(dim=1, keepdim=True) + 1e-8); cos = pn @ cb.t()
    best = float("inf")
    for t in TEMP_GRID:
        z = cos / t; z = z - z.max(dim=1, keepdim=True).values; ez = torch.exp(z)
        pr = ez / (ez.sum(dim=1, keepdim=True) + 1e-30)
        pt = pr[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        best = min(best, float((-torch.log(pt)).mean()))
    return best


def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    cb = build_codebook(7, 128, gen); ctx, nxt = cb[0], cb[1]
    Asym = torch.outer(nxt, ctx) - torch.outer(ctx, nxt)
    assert float((Asym + Asym.t()).abs().max()) < 1e-4
    W = torch.zeros(128, 128, device=DEVICE); v = W @ ctx; eb = float((nxt - v).norm())
    W = W + torch.outer(nxt - v, ctx); ea = float((nxt - W @ ctx).norm()); assert ea < eb
    g = np.random.default_rng(0); _, ce = gen_zipf(64, 1000, g); assert ce < math.log(64)
    assert abs(math.log(7) - 1.9459) < 1e-3
    print(f"[selftest] PASS: stdp_antisym cfrpe {eb:.3f}->{ea:.3f} zipf_ce={ce:.3f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    gen_np = np.random.default_rng(seed + 5000); t0 = time.time()
    ids, ce = gen_zipf(VOCAB, CORPUS, gen_np); sp = int(0.8 * len(ids))
    tr = torch.tensor(ids[:sp], dtype=torch.long, device=DEVICE)
    va = torch.tensor(ids[sp:], dtype=torch.long, device=DEVICE); un = math.log(VOCAB)
    arms = {}
    for arm in ARMS:
        cb = build_codebook(VOCAB, n_dim, gen)
        nats = train_eval(arm, n_dim, cb, tr, va, gen)
        arms[arm] = {"val_nats": float(nats), "gap": float(un - nats)}
        print(f"    [{arm}] gap={un - nats:.4f}", flush=True); del cb; torch.cuda.empty_cache()
    print(f"  [seed={seed}] elapsed={time.time() - t0:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "uniform_nats": un, "arms": arms, "elapsed_s": time.time() - t0}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "no results")
    g = lambda a: float(np.mean([r["arms"][a]["gap"] for r in results if a in r["arms"]]))
    gcf, gstdp, gc1 = g("A2_cfrpe"), g("A3_stdp"), g("C1_cfrpe_stdp")
    n = len(results); n_super = sum(1 for r in results if r["arms"]["C1_cfrpe_stdp"]["gap"] > HP_SUPER)
    best_single = max(gcf, gstdp)
    summary = f"gap cfrpe={gcf:.3f} stdp={gstdp:.3f} combined={gc1:.3f} (max_single={best_single:.3f}) super_seeds={n_super}/{n}"
    if gc1 > HP_SUPER and n_super >= math.ceil(0.8 * n):
        return ("HARD_PASS", f"HARD_PASS: heterogeneous cf-RPE+STDP SUPERADDITIVE (gap>{HP_SUPER}, {n_super}/{n}). {summary}")
    if gc1 > best_single:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: combined > best single but < {HP_SUPER} (partial superadditive). {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: combined <= max single (still shared-axis/additive). {summary}")


print(f"[config] anchor={ANCHOR_NAME} arms={ARMS} N={N_DIM} V={VOCAB} mode={RUN_MODE} seeds={SEEDS}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "arms": ARMS})
print(f"[ckpt] {len(done)} done, {len(remaining)} to run", flush=True)
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    write_partial(out_dir, seed, run_seed(seed, N_DIM))
per_seed = aggregate_partials(out_dir, SEEDS); all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
peak = torch.cuda.max_memory_allocated(0) / 1e9; print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg, "N": N_DIM,
           "V": VOCAB, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "arms": ARMS,
           "per_seed": [{"seed": r.get("seed"), "uniform_nats": r.get("uniform_nats"), "arms": r.get("arms"), "elapsed_s": r.get("elapsed_s")} for r in all_results]}
write_metrics(out_dir, metrics, all_results)
print("[metrics] written", flush=True)
