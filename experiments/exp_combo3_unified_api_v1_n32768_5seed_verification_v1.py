"""
combo3_unified_api_v1_n32768_5seed_verification_v1 -- COMBO-3 5-method API at N=32768, 5-seed production lock.

Re-confirmation of combo3_unified_api_v1_n32768_local (completed, HARD_PASS) with explicit
5-seed production-lock verification framing for cap_map PP-45 N-scaling sub-property at N=32768.

VRAM: Xi (M=1638 x N=32768 float32) = 214 MB; Krylov V (32768 x 500) = 65 MB; Gram (1638^2) = 10 MB.
Peak < 400 MB. Safe.

PRE-REGISTERED BANDS (inherited from n32768_local HARD_PASS):
  HARD-PASS: all 3 trace metrics (tr_W1, tr_W2, tr_W3) match closed-form within 1e-6 relative.
  MIDDLE: all within 1e-4; 1-2 within 1e-2.
  HARD-FAIL: any metric deviates by > 1e-2 from closed-form.

FORMULA SELF-TESTS:
  Krylov traces ~ closed-form within 20% at N=128, M=6.
  GPU memory > 0 after Krylov buffer alloc.

PROT-018: anchor has _n32768 -> N must = 32768.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
    import torch.cuda
except ImportError:
    print("[FATAL] torch not installed.", flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True)
    sys.exit(1)

DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB", flush=True)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "combo3_unified_api_v1_n32768_5seed_verification_v1"

_N_SUFFIX = 32768
N = 32768
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05

if RUN_MODE == "smoke":
    N_ACTIVE = 4096
    SEEDS = [7, 17]
    N_PROBES = 200
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_PROBES = 500

HP_REL_TOL = 1e-6
MID_REL_TOL = 1e-4
HF_REL_TOL = 1e-2


def build_Xi_gpu(m: int, n: int, seed: int) -> torch.Tensor:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    return (torch.randint(0, 2, (m, n), generator=gen, device=DEVICE).float() * 2 - 1)


def krylov_trace_gpu(Xi: torch.Tensor, n: int, n_probes: int, seed: int) -> Dict[str, float]:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + 9999)
    V0 = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)

    def w_op(V):
        return (Xi.t() @ (Xi @ V)) / n

    V1 = w_op(V0)
    V2 = w_op(V1)
    V3 = w_op(V2)

    tr_W1 = float((V0 * V1).sum(dim=0).mean())
    tr_W2 = float((V0 * V2).sum(dim=0).mean())
    tr_W3 = float((V0 * V3).sum(dim=0).mean())
    return {"tr_W1": tr_W1, "tr_W2": tr_W2, "tr_W3": tr_W3,
            "kappa_3": tr_W3 / n}


def closed_form_traces_gpu(Xi: torch.Tensor, n: int) -> Dict[str, float]:
    G = (Xi @ Xi.t()).float()
    eigs = torch.linalg.eigvalsh(G)
    tr_W1 = float(eigs.sum() / n)
    tr_W2 = float((eigs ** 2).sum() / (n ** 2))
    tr_W3 = float((eigs ** 3).sum() / (n ** 3))
    return {"tr_W1": tr_W1, "tr_W2": tr_W2, "tr_W3": tr_W3,
            "kappa_3": tr_W3 / n}


def _instrumentation_selftest():
    N_t = 128
    M_t = 6
    Xi_t = build_Xi_gpu(M_t, N_t, seed=42)
    cf = closed_form_traces_gpu(Xi_t, N_t)
    kr = krylov_trace_gpu(Xi_t, N_t, n_probes=2000, seed=42)
    for k in ["tr_W1", "tr_W2"]:
        rel = abs(kr[k] - cf[k]) / max(abs(cf[k]), 1e-12)
        assert rel < 0.20, f"{k} selftest: krylov={kr[k]:.4e} cf={cf[k]:.4e} rel={rel:.4e}"
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    print(f"[selftest] PASS: krylov vs closed_form within 0.20 N={N_t} GPU_mem={mem/1e6:.1f}MB",
          flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    t0 = time.time()
    M = int(ALPHA * n_dim)
    Xi = build_Xi_gpu(M, n_dim, seed=seed)

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim} M={M}] GPU memory after Xi alloc: {mem_gb:.3f} GB", flush=True)

    kr = krylov_trace_gpu(Xi, n_dim, n_probes=N_PROBES, seed=seed)
    cf = closed_form_traces_gpu(Xi, n_dim)

    metrics_per = {}
    for k in ["tr_W1", "tr_W2", "tr_W3"]:
        rel = abs(kr[k] - cf[k]) / max(abs(cf[k]), 1e-12)
        metrics_per[k] = rel

    peak_mem = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] rel: tr_W1={metrics_per['tr_W1']:.2e} "
          f"tr_W2={metrics_per['tr_W2']:.2e} tr_W3={metrics_per['tr_W3']:.2e} "
          f"peak_gpu={peak_mem:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "M": M, "run_mode": RUN_MODE,
        "tr_W1_rel": float(metrics_per["tr_W1"]),
        "tr_W2_rel": float(metrics_per["tr_W2"]),
        "tr_W3_rel": float(metrics_per["tr_W3"]),
        "kappa_3_krylov": float(kr["kappa_3"]),
        "kappa_3_cf": float(cf["kappa_3"]),
        "peak_gpu_gb": float(peak_mem),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No results.")

    mean_rel = {}
    for k in ["tr_W1", "tr_W2", "tr_W3"]:
        key = f"{k}_rel"
        vs = [r[key] for r in results if key in r]
        mean_rel[k] = float(sum(vs) / len(vs)) if vs else 1.0

    worst_rel = max(mean_rel.values())
    summary = (f"mean_rel tr_W1={mean_rel['tr_W1']:.2e} tr_W2={mean_rel['tr_W2']:.2e} "
               f"tr_W3={mean_rel['tr_W3']:.2e} worst={worst_rel:.2e} "
               f"n_seeds={len(results)} N={N}")

    if worst_rel > HF_REL_TOL:
        return ("HARD_FAIL", f"HARD_FAIL: worst_rel={worst_rel:.2e} > {HF_REL_TOL}. {summary}")

    n_hp = sum(1 for k in mean_rel if mean_rel[k] <= HP_REL_TOL)
    n_mid = sum(1 for k in mean_rel if mean_rel[k] <= MID_REL_TOL)

    if n_hp >= 3:
        return ("HARD_PASS",
                f"HARD_PASS: all 3 metrics < {HP_REL_TOL:.0e} at N=32768 5-seed lock. {summary}")
    if n_mid >= 3:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: all within {MID_REL_TOL:.0e}. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp}/3 at HP level. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha={ALPHA} n_probes={N_PROBES}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE, "alpha": ALPHA}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME} N={N_ACTIVE}...", flush=True)
    result = run_seed(seed, N_ACTIVE)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
assert peak_mem_gb > 0.01, f"GPU utilization check FAIL: peak_gpu={peak_mem_gb:.3f} GB"

elapsed_total = time.time() - t_sweep_start
metrics_out = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "peak_gpu_gb": float(peak_mem_gb),
    "per_seed": [
        {"seed": r.get("seed"), "tr_W1_rel": r.get("tr_W1_rel"),
         "tr_W2_rel": r.get("tr_W2_rel"), "tr_W3_rel": r.get("tr_W3_rel"),
         "peak_gpu_gb": r.get("peak_gpu_gb")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics_out, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
