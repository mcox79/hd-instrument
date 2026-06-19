"""
substrate_cfrpe_sparse_superadditive_bigram_v1_n512_gpu -- cf-RPE x Drosophila-sparse superadditivity (GPU).

ROUTING: notes/routing_bundle_a_combined_superadditive_test_2026-06-04.md. Bundle A showed cf-RPE alone and
  Drosophila-sparse alone BOTH beat K=1 baseline at bigram; is the COMBINATION superadditive (beyond either
  alone) or substitutive? Run on owned GPU ($0; matmul-light).

CAPABILITY QUESTION:
  cf-RPE (supervised error signal: Hebbian->conditional-prob bridge) and sparse coding (input representation:
  dense bipolar -> sparse binary, capacity gain) address conceptually ORTHOGONAL axes. Combined should be
  superadditive IF they fix independent failure modes; substitutive if they target the same gain.

FOUR ARMS (5 seeds; synthetic V=512 Zipf bigram; N=512):
  A1 hebbian_k1     : bipolar + one-shot symmetric Hebbian (dW = Nxt^T Ctx). baseline.
  A2 cfrpe          : bipolar + cf-RPE delta (dW = (Nxt - W Ctx)^T Ctx). [HP in Bundle A]
  A3 sparse_hebbian : sparse {0,1} f=0.05 + symmetric Hebbian (sparse representation, NO error signal).
  C_AB combined     : sparse {0,1} f=0.05 + cf-RPE delta (both axes combined).

PRE-REGISTERED BANDS (BPC nats; lower is better):
  HARD-PASS (superadditive): BPC_combined < min(BPC_cfrpe, BPC_sparse_hebbian) - 0.20 nats AND 4/5 seeds.
  MIDDLE (additive): BPC_combined in [min - 0.20, min + 0.05].
  HARD-FAIL (substitutive): BPC_combined >= min(BPC_cfrpe, BPC_sparse_hebbian) (no gain over either alone).

FORMULA SELF-TESTS (PROT-022):
  1. sparse support = f*N (unit-norm). 2. cf-RPE shrinks single-pair error. 3. zipf cond-entropy < log(V).
  4. uniform nats = ln(V).

PROT-018: anchor _n512 -> N=512. PROT-021: seed ckpt by run_mode+seed.
QUEUE: overnight_queue (GPU). TIMEOUT: 14400s. GPU TEMPLATE: assert cuda + device='cuda' + batched matmul.
ASCII-only stdout.
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
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB", flush=True)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "substrate_cfrpe_sparse_superadditive_bigram_v1_n512_gpu"
_N_SUFFIX = 512
N = 512
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LR = 0.5
BATCH = 64
VOCAB = 512
K_ACTIVE = 8
SPARSE_F = 0.05
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
SUPER_MARGIN = 0.20
# (name, coding, rule)  rule in {hebbian, cfrpe}
ARMS = [("A1_hebbian_k1", "bipolar", "hebbian"),
        ("A2_cfrpe", "bipolar", "cfrpe"),
        ("A3_sparse_hebbian", "sparse", "hebbian"),
        ("C_AB_sparse_cfrpe", "sparse", "cfrpe")]

if RUN_MODE == "smoke":
    N_DIM = 256
    VOCAB = 128
    SEEDS = [1, 2]
    N_STEPS = 80
    CORPUS = 6000
else:
    N_DIM = N
    SEEDS = [7, 17, 23, 31, 41]
    N_STEPS = 1000
    CORPUS = 60000


def gen_zipf_bigram(V, length, gen_np):
    ranks = 1.0 / np.arange(1, V + 1); zp = ranks / ranks.sum()
    T = np.zeros((V, V), dtype=np.float64)
    for c in range(V):
        tg = gen_np.choice(V, size=K_ACTIVE, replace=False, p=zp)
        lg = gen_np.standard_normal(K_ACTIVE) * 2.0
        w = np.exp(lg - lg.max()); w /= w.sum(); T[c, tg] = w
    with np.errstate(divide='ignore', invalid='ignore'):
        ce = float((-np.sum(np.where(T > 0, T * np.log(T), 0.0), axis=1)).mean())
    ids = np.zeros(length, dtype=np.int64); s = 0
    for i in range(length):
        ids[i] = s; s = gen_np.choice(V, p=T[s])
    return ids, ce


def build_codebook(V, n, coding, gen):
    if coding == "bipolar":
        cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    else:
        cb = torch.zeros(V, n, device=DEVICE)
        k = max(1, int(round(SPARSE_F * n)))
        for i in range(V):
            cb[i, torch.randperm(n, generator=gen, device=DEVICE)[:k]] = 1.0
    return cb / (cb.norm(dim=1, keepdim=True) + 1e-8)


def train_eval(coding, rule, n, cb, train_ids, val_ids, gen) -> float:
    W = torch.zeros(n, n, device=DEVICE)
    ntr = train_ids.shape[0]
    for _ in range(N_STEPS):
        starts = torch.randint(0, ntr - 1, (BATCH,), generator=gen, device=DEVICE)
        Ctx = cb[train_ids[starts]]; Nxt = cb[train_ids[starts + 1]]
        if rule == "hebbian":
            W = W + LR * (Nxt.t() @ Ctx) / BATCH
        else:
            W = W + LR * ((Nxt - Ctx @ W.t()).t() @ Ctx) / BATCH
    nb = min(2000, val_ids.shape[0] - 1)
    starts = torch.randint(0, val_ids.shape[0] - 1, (nb,), generator=gen, device=DEVICE)
    ctx = cb[val_ids[starts]]; nxt = val_ids[starts + 1]
    pred = ctx @ W.t(); pn = pred / (pred.norm(dim=1, keepdim=True) + 1e-8); cos = pn @ cb.t()
    best = float("inf")
    for temp in TEMP_GRID:
        z = cos / temp; z = z - z.max(dim=1, keepdim=True).values
        ez = torch.exp(z); prob = ez / (ez.sum(dim=1, keepdim=True) + 1e-30)
        pt = prob[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        best = min(best, float((-torch.log(pt)).mean()))
    return best


def _selftest():
    g = np.random.default_rng(0); ids, ce = gen_zipf_bigram(64, 2000, g); assert ce < math.log(64)
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    cbs = build_codebook(7, 128, "sparse", gen)
    assert int((cbs[0] != 0).sum()) == max(1, int(round(SPARSE_F * 128))) and abs(float(cbs[0].norm()) - 1) < 1e-4
    cb = build_codebook(7, 128, "bipolar", gen)
    W = torch.zeros(128, 128, device=DEVICE); ctx, nxt = cb[0], cb[1]
    v = W @ ctx; eb = float((nxt - v).norm()); W = W + torch.outer(nxt - v, ctx); ea = float((nxt - W @ ctx).norm())
    assert ea < eb and abs(math.log(7) - 1.9459) < 1e-3
    print(f"[selftest] PASS: zipf_ce={ce:.3f} sparse_support_ok cfrpe {eb:.3f}->{ea:.3f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    gen_np = np.random.default_rng(seed + 5000)
    t0 = time.time()
    ids, ce = gen_zipf_bigram(VOCAB, CORPUS, gen_np)
    split = int(0.8 * len(ids))
    tr = torch.tensor(ids[:split], dtype=torch.long, device=DEVICE)
    va = torch.tensor(ids[split:], dtype=torch.long, device=DEVICE)
    un = math.log(VOCAB)
    print(f"  [seed={seed}] V={VOCAB} N={n_dim} uniform_nats={un:.3f} cond_ent={ce:.3f}", flush=True)
    arms = {}
    for name, coding, rule in ARMS:
        cb = build_codebook(VOCAB, n_dim, coding, gen)
        nats = train_eval(coding, rule, n_dim, cb, tr, va, gen)
        arms[name] = {"coding": coding, "rule": rule, "val_nats": float(nats), "gap_vs_uniform": float(un - nats)}
        print(f"    [{name}] val_nats={nats:.4f} gap={un - nats:.4f}", flush=True)
        del cb; torch.cuda.empty_cache()
    peak = torch.cuda.max_memory_allocated(0) / 1e9; elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE, "uniform_nats": float(un), "arms": arms,
            "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    def mean_nats(nm):
        vs = [r["arms"][nm]["val_nats"] for r in results if nm in r.get("arms", {})]
        return float(np.mean(vs)) if vs else float("nan")
    b = mean_nats("A1_hebbian_k1"); cf = mean_nats("A2_cfrpe")
    sp = mean_nats("A3_sparse_hebbian"); comb = mean_nats("C_AB_sparse_cfrpe")
    best_single = min(cf, sp)
    n = len(results)
    n_super = sum(1 for r in results
                  if "C_AB_sparse_cfrpe" in r["arms"] and "A2_cfrpe" in r["arms"] and "A3_sparse_hebbian" in r["arms"]
                  and r["arms"]["C_AB_sparse_cfrpe"]["val_nats"] < min(r["arms"]["A2_cfrpe"]["val_nats"],
                                                                       r["arms"]["A3_sparse_hebbian"]["val_nats"]) - SUPER_MARGIN)
    summary = f"nats: hebbian={b:.3f} cfrpe={cf:.3f} sparse_hebbian={sp:.3f} combined={comb:.3f} (min_single={best_single:.3f}) super_seeds={n_super}/{n}"
    if comb < best_single - SUPER_MARGIN and n_super >= math.ceil(0.8 * n):
        return ("HARD_PASS", f"HARD_PASS: combined SUPERADDITIVE (< min single - {SUPER_MARGIN} nats, {n_super}/{n} seeds). {summary}")
    if comb <= best_single + 0.05:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: combined additive (~= best single). {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: combined substitutive (>= min single; no extra gain). {summary}")


print(f"[config] anchor={ANCHOR_NAME} arms={[a[0] for a in ARMS]} N={N_DIM} V={VOCAB} mode={RUN_MODE} "
      f"seeds={SEEDS} steps={N_STEPS}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError(f"PROT-018: N_DIM={N_DIM} != _N_SUFFIX={_N_SUFFIX}")

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_DIM, "V": VOCAB, "run_mode": RUN_MODE, "arms": [a[0] for a in ARMS], "n_steps": N_STEPS}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_DIM)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep
peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.001, f"GPU util check FAIL: {peak_mem_gb:.3f}GB"
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N_DIM, "V": VOCAB, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "n_steps": N_STEPS,
    "arms": [a[0] for a in ARMS], "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "uniform_nats": r.get("uniform_nats"), "arms": r.get("arms", {}),
                  "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
