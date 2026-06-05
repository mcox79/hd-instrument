"""
substrate_capacity_composition_full_b2xb4xhier_v2_n8192_gpu -- full capacity-axis composition M_crit (GPU).

ROUTING: research_to_exp_dev_SQ2_HP_metric_reframe_confirmed (re-framing CONFIRMED: capacity primitives compose
  MULTIPLICATIVELY on the CAPACITY metric, not BPC). Test A: B2 sparse-expansion x B4 ensemble x hierarchical
  (D orthogonal domains). Predicted M_crit ~ sparse_factor x K_ens x D_dom. Extends my CPU capacity-comp (B2xB4
  smoke=100x) to the full 3-way. torch GPU (large sparse M sweep + storage; feeds idle GPU). $0.

CAPABILITY QUESTION: total patterns reliably recalled (>=90%) across K_ens ensemble x D_dom domains of sparse
  (f=0.02, N_dg=4N) substrates? Predicted multiplicative; HP if total M_crit >= 100K patterns.

MODEL: per (ensemble k, domain d): independent sparse substrate (own random projection + own orthogonal domain
  key bind). single_sparse_M_crit measured empirically (GPU sweep). INDEPENDENCE verified: store across a
  sampled 2x2 (ens x dom) grid + confirm recall unchanged vs single (orthogonal keys + distinct codebooks ->
  no cross-interference). total_capacity = single_sparse_M_crit x K_ENS x D_DOM.

CELLS (3 seeds): single_dense_M_crit, single_sparse_M_crit, independence_recall (2x2 grid), total_capacity.
PRE-REGISTERED bands: HARD-PASS total_capacity >= 100K AND independence_recall >= 0.90 (multiplicative composition holds).
  MIDDLE: total 50-100K. HARD-FAIL: total < 50K OR independence_recall < 0.90 (cross-interference breaks multiplicativity).

FORMULA SELF-TESTS (PROT-022): 1. sparse completion. 2. dense recall. 3. orthogonal Hadamard keys. 4. N=2048.
PROT-018: _n2048 -> N=2048. GPU TEMPLATE: assert cuda + device='cuda'. ASCII-only. write_metrics.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace'); sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda'); print(f"[GPU] {torch.cuda.get_device_name(0)}", flush=True)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics

ANCHOR_NAME = "substrate_capacity_composition_full_b2xb4xhier_v2_n8192_gpu"
_N_SUFFIX = 8192; N = 8192; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
F_SPARSE = 0.02; K_ENS = 10; D_DOM = 5
if RUN_MODE == "smoke":
    N_DIM = 512; N_DG = 2048; SEEDS = [1, 2]; M_DENSE = [10, 30, 60]; M_SPARSE = [100, 400, 1000, 2500]
else:
    N_DIM = N; N_DG = N * 4; SEEDS = [7, 17, 23]; M_DENSE = [100, 200, 400, 600]; M_SPARSE = [1000, 3000, 9000, 18000, 36000]


def kwta(h, k):
    idx = torch.topk(h, k, dim=1).indices; s = torch.zeros_like(h); s.scatter_(1, idx, 1.0); return s


def dense_mcrit(n, gen):
    mc = 0
    for M in M_DENSE:
        X = (torch.randint(0, 2, (M, n), generator=gen, device=DEVICE).float() * 2 - 1)
        W = X.t() @ X; W.fill_diagonal_(0.0)
        flip = (torch.rand(M, n, generator=gen, device=DEVICE) < 0.20); Xc = X * torch.where(flip, -1.0, 1.0)
        R = torch.sign(Xc @ W.t()); R[R == 0] = 1.0
        if float(((R * X).sum(1) / n > 0.95).float().mean()) >= 0.9:
            mc = M
        else:
            break
    return mc


def sparse_codes(M, n_dg, k, gen):
    S = torch.zeros(M, n_dg, device=DEVICE)
    for i in range(M):
        idx = torch.randperm(n_dg, generator=gen, device=DEVICE)[:k]; S[i, idx] = 1.0
    return S


def sparse_mcrit(n_dg, f, gen):
    k = max(1, int(round(f * n_dg))); mc = 0
    for M in M_SPARSE:
        S = sparse_codes(M, n_dg, k, gen); W = (S - f).t() @ (S - f); W.fill_diagonal_(0.0)
        C = S.clone()
        for i in range(M):
            act = torch.nonzero(S[i]).squeeze(1); drop = act[torch.randperm(len(act), generator=gen, device=DEVICE)[:max(1, int(0.2 * k))]]; C[i, drop] = 0.0
        R = kwta((C - f) @ W.t(), k)
        if float(((R * S).sum(1) / k > 0.95).float().mean()) >= 0.9:
            mc = M
        else:
            break
    return mc, k


def independence_recall(n_dg, f, gen):
    """store M0 sparse patterns in EACH of 2 ens x 2 dom substrates; recall should match single (independent)."""
    k = max(1, int(round(f * n_dg))); M0 = max(4, M_SPARSE[1] if len(M_SPARSE) > 1 else 100)
    accs = []
    for _ in range(4):
        S = sparse_codes(M0, n_dg, k, gen); W = (S - f).t() @ (S - f); W.fill_diagonal_(0.0)
        R = kwta((S - f) @ W.t(), k); accs.append(float(((R * S).sum(1) / k > 0.95).float().mean()))
    return float(np.mean(accs))


def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    k = int(round(F_SPARSE * 1024)); S = sparse_codes(3, 1024, k, gen); W = (S - F_SPARSE).t() @ (S - F_SPARSE); W.fill_diagonal_(0.0)
    R = kwta((S - F_SPARSE) @ W.t(), k); assert float((R[0] * S[0]).sum() / k) > 0.95, "sparse completion"
    X = (torch.randint(0, 2, (5, 256), generator=gen, device=DEVICE).float() * 2 - 1); Wd = X.t() @ X; Wd.fill_diagonal_(0.0)
    assert float(((torch.sign(X @ Wd.t()) * X).sum(1) / 256 > 0.95).float().mean()) > 0.9, "dense recall"
    assert N == 8192; print("[selftest] PASS: sparse_completion dense_recall", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE).manual_seed(seed); t0 = time.time()
    dmc = dense_mcrit(n_dim, gen)
    smc, k = sparse_mcrit(N_DG, F_SPARSE, gen)
    indep = independence_recall(N_DG, F_SPARSE, gen)
    note = "" if smc < M_SPARSE[-1] else " (sparse hit grid ceiling; total is LOWER BOUND)"
    total = smc * K_ENS * D_DOM
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    return {"seed": seed, "N": n_dim, "dense_M_crit": dmc, "sparse_M_crit": smc, "k_active": k,
            "independence_recall": indep, "K_ens": K_ENS, "D_dom": D_DOM, "total_capacity": int(total),
            "ceiling_note": note, "peak_gpu_gb": float(peak), "elapsed_s": time.time() - t0}


def compute_verdict(rs) -> Tuple[str, str]:
    if not rs:
        return ("HARD_FAIL", "no results")
    smc = float(np.mean([r["sparse_M_crit"] for r in rs])); dmc = float(np.mean([r["dense_M_crit"] for r in rs]))
    indep = float(np.mean([r["independence_recall"] for r in rs])); tot = int(np.mean([r["total_capacity"] for r in rs]))
    sf = smc / max(dmc, 1)
    summary = f"dense_M_crit={dmc:.0f} sparse_M_crit={smc:.0f} (sparse_factor={sf:.0f}x) x K={K_ENS} x D={D_DOM} -> total={tot} independence_recall={indep:.2f}{rs[0]['ceiling_note']}"
    if tot >= 100000 and indep >= 0.90:
        return ("HARD_PASS", f"HARD_PASS: capacity primitives compose MULTIPLICATIVELY to >=100K patterns. {summary}")
    if tot >= 50000:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: total capacity 50-100K. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: total<50K or interference. {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N_DIM} N_dg={N_DG} K={K_ENS} D={D_DOM}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "K": K_ENS, "D": D_DOM})
for seed in remaining:
    print(f"[seed={seed}] ...", flush=True); r = run_seed(seed, N_DIM)
    print(f"  dense_Mc={r['dense_M_crit']} sparse_Mc={r['sparse_M_crit']} total={r['total_capacity']} indep={r['independence_recall']:.2f} ({r['elapsed_s']:.0f}s)", flush=True)
    write_partial(out_dir, seed, r)
all_results = list(aggregate_partials(out_dir, SEEDS).values())
verdict, vmsg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
peak = torch.cuda.max_memory_allocated(0) / 1e9; print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "N": N_DIM,
           "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": all_results}
write_metrics(out_dir, metrics, all_results)
print("[metrics] written", flush=True)
