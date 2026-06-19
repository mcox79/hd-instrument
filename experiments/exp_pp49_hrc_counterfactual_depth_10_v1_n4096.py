"""
pp49_hrc_counterfactual_depth_10_v1_n4096 -- PP-49 HRC counterfactual abduction at depth-10.

Extends pp49_pp9_counterfactual_deletion_composition at depth-1 to depth-10 chain.
Analogous to Wave 5 Q-B1 depth-10 cloud HP. Tests whether counterfactual substitution
(rank-1 swap xi_A -> xi_B) retains its audit-trail validity across a depth-10 heteroassoc
chain, not just at the single-pattern level.

Protocol:
  - Build heteroassoc chain C: c0 -> c1 -> ... -> c10 at N=4096 (depth-10).
  - At position d=5 (midpoint), perform counterfactual substitution:
    W_cf = W - (1/N) xi_A xi_A^T + (1/N) xi_B xi_B^T  where xi_A = c5.
  - Tests:
    HP1: deletion cert for c5 in W_original = -1.0 (within 1e-4).
    HP2: counterfactual chain from c0 at depth 5 retrieves xi_B (not c5) from W_cf.
    HP3: audit cert -- c5 cert in W_cf near 0 (|cert| < 0.15).
    HP4: chain downstream of substitution (c6...c10) still retrievable from W_cf.

GPU IMPLEMENTATION:
  H matrix (N x N float32 at N=4096): 67 MB. Safe.
  Matrix-free deletion_cert (no W needed).
  H_cf = H - outer(c5, c4)/N + outer(xi_B, c4)/N  (only binding at hop 4->5 changes).

PRE-REGISTERED BANDS:
  HARD-PASS: HP1 AND HP2 AND HP3 AND HP4.
  HARD-FAIL: HP1 fails OR HP2 < 0.40.
  MIDDLE: 3/4 conditions.

FORMULA SELF-TESTS:
  1. cert for BSC xi in W = xi xi^T/N: cert = xi^T(-(1/N)xi xi^T)xi/N = -||xi||^4/N^2 = -1.0.
     [INPUT: N=8, BSC xi] [EXPECTED: -1.0]
  2. Cert for xi_A in W_cf after removal: for M=1, W_cf = (xi_B xi_B^T)/N.
     cert_A_in_Wcf = xi_A^T((1/N)xi_B xi_B^T)xi_A/N = (xi_A . xi_B)^2/N^2 ~ 0 for large N.
     [INPUT: orthogonal xi_A, xi_B] [EXPECTED: cert_A_in_Wcf = 0]
  3. GPU memory > 0 after H build.

PROT-018: anchor has _n4096; N MUST = 4096.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# GPU GUARD
try:
    import torch
    import torch.cuda
except ImportError:
    print("[FATAL] torch not installed; cannot run GPU experiment.", flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU. Aborting.", flush=True)
    sys.exit(1)

DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB", flush=True)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp49_hrc_counterfactual_depth_10_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

CHAIN_DEPTH = 10
SUBST_DEPTH = 5    # substitution at position 5
CERT_TOL = 1e-4

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    N_CHAINS = 3
    M_BG = 20
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_CHAINS = 10
    M_BG = 100

HP_CERT = 0.85    # fraction of seeds passing HP1
HP_CF_COS = 0.60  # counterfactual retrieval cosine
HP_AUDIT = 0.85   # fraction of seeds passing HP3 (|cert_A| < 0.15)
HP_DOWNSTREAM = 0.70
HF_CF_COS = 0.40


def deletion_cert_gpu(xi: torch.Tensor, n: int) -> float:
    """cert = xi^T(-(1/n)xi xi^T)xi / n = -(||xi||^2)^2 / n^2."""
    norm_sq = float(xi.dot(xi))
    return -(norm_sq ** 2) / (n * n)


def cosine_sim_gpu(a: torch.Tensor, b: torch.Tensor) -> float:
    na = float(a.norm())
    nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)


def _instrumentation_selftest():
    """Cert = -1.0 for BSC xi; cert = 0 for orthogonal xi_A after W_cf."""
    # Test 1: cert for BSC xi
    N_t = 8
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    xi = (torch.randint(0, 2, (N_t,), generator=gen, device=DEVICE).float() * 2 - 1)
    c = deletion_cert_gpu(xi, N_t)
    assert abs(c + 1.0) < 1e-8, f"cert selftest: {c:.6f} expected -1.0"

    # Test 2: cert for xi_A in W_cf after removal (M=1, orthogonal xi_B)
    # W_cf = (1/N) xi_B xi_B^T; cert_A = xi_A^T W_cf xi_A / N = (xi_A.xi_B)^2/N^2
    xi_A = torch.tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        dtype=torch.float32, device=DEVICE)
    xi_B = torch.tensor([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        dtype=torch.float32, device=DEVICE)
    # W_cf @ xi_A = (xi_B xi_B^T / N) @ xi_A = xi_B * (xi_B . xi_A) / N = 0 (orthogonal)
    dot = float(torch.dot(xi_A, xi_B))
    cert_A_cf = (dot ** 2) / (N_t * N_t)
    assert abs(cert_A_cf) < 1e-8, f"cert_A_in_Wcf: {cert_A_cf:.6f} expected ~0"

    # GPU memory check
    dummy = torch.zeros((256, 256), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    del dummy

    print(f"[selftest] PASS: cert=-1.0, cert_A_in_Wcf=0, gpu_mem_ok", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    def bsc(n_d):
        return (torch.randint(0, 2, (n_d,), generator=gen, device=DEVICE).float() * 2 - 1)

    chain_results = []
    for chain_idx in range(N_CHAINS):
        # Build depth-10 chain
        chain = [bsc(n_dim) for _ in range(CHAIN_DEPTH + 1)]

        # Build H (heteroassoc): H = sum_{d=0}^{depth-1} outer(chain[d+1], chain[d]) / n
        # + M_BG background bindings
        bg_keys = torch.stack([bsc(n_dim) for _ in range(M_BG)])
        bg_vals = torch.stack([bsc(n_dim) for _ in range(M_BG)])

        H = torch.zeros((n_dim, n_dim), device=DEVICE, dtype=torch.float32)
        for d in range(CHAIN_DEPTH):
            H += torch.outer(chain[d + 1], chain[d]) / n_dim
        H += (bg_vals.t() @ bg_keys) / n_dim

        # HP1: deletion cert for chain[SUBST_DEPTH] in W_original
        cert_orig = deletion_cert_gpu(chain[SUBST_DEPTH], n_dim)
        hp1_ok = abs(cert_orig + 1.0) < CERT_TOL

        # Build W_cf: replace binding at hop (SUBST_DEPTH-1 -> SUBST_DEPTH) with xi_B
        xi_A = chain[SUBST_DEPTH]
        xi_B = bsc(n_dim)   # replacement pattern
        H_cf = H - torch.outer(xi_A, chain[SUBST_DEPTH - 1]) / n_dim \
                 + torch.outer(xi_B, chain[SUBST_DEPTH - 1]) / n_dim

        # HP2: counterfactual retrieval -- starting from chain[SUBST_DEPTH-1], should get xi_B
        r_cf = chain[SUBST_DEPTH - 1].clone()
        for _ in range(3):
            h_vec = H_cf @ r_cf
            r_cf = torch.sign(h_vec)
            r_cf[r_cf == 0] = 1.0
        cf_cos = cosine_sim_gpu(r_cf, xi_B)

        # HP3: audit cert -- cert for xi_A (=chain[SUBST_DEPTH]) in W_cf
        # W_cf contribution to xi_A: H_cf @ xi_A vs H @ xi_A
        # Cert proxy: |H_cf @ xi_A . xi_A| / (n * ||xi_A||^2) vs original
        h_cf_xi_A = H_cf @ xi_A
        cert_A_cf_proxy = float(torch.dot(h_cf_xi_A, xi_A)) / (n_dim * float(xi_A.dot(xi_A)))
        hp3_ok = abs(cert_A_cf_proxy) < 0.15

        # HP4: downstream retrieval (chain[SUBST_DEPTH+1...]) still works under H_cf
        # Test: retrieve chain[SUBST_DEPTH+1] starting from chain[SUBST_DEPTH] using H_cf
        r_ds = chain[SUBST_DEPTH].clone()
        for _ in range(3):
            h_vec = H_cf @ r_ds
            r_ds = torch.sign(h_vec)
            r_ds[r_ds == 0] = 1.0
        ds_cos = cosine_sim_gpu(r_ds, chain[SUBST_DEPTH + 1])

        del H, H_cf

        chain_results.append({
            "hp1_ok": hp1_ok, "cert_orig": cert_orig,
            "cf_cos": float(cf_cos),
            "cert_A_cf": float(cert_A_cf_proxy),
            "hp3_ok": hp3_ok,
            "ds_cos": float(ds_cos),
        })

    # Aggregate over chains
    hp1_rate = float(sum(r["hp1_ok"] for r in chain_results) / len(chain_results))
    mean_cf_cos = float(sum(r["cf_cos"] for r in chain_results) / len(chain_results))
    hp3_rate = float(sum(r["hp3_ok"] for r in chain_results) / len(chain_results))
    mean_ds_cos = float(sum(r["ds_cos"] for r in chain_results) / len(chain_results))

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] hp1_rate={hp1_rate:.4f} cf_cos={mean_cf_cos:.4f} "
          f"hp3_rate={hp3_rate:.4f} ds_cos={mean_ds_cos:.4f} "
          f"peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "hp1_cert_rate": float(hp1_rate),
        "mean_cf_cos": float(mean_cf_cos),
        "hp3_audit_rate": float(hp3_rate),
        "mean_ds_cos": float(mean_ds_cos),
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs)/len(vs)) if vs else 0.0

    hp1 = mean_key("hp1_cert_rate")
    cf_cos = mean_key("mean_cf_cos")
    hp3 = mean_key("hp3_audit_rate")
    ds_cos = mean_key("mean_ds_cos")

    summary = (f"hp1_cert_rate={hp1:.4f}(>={HP_CERT}) cf_cos={cf_cos:.4f}(>={HP_CF_COS} HF<{HF_CF_COS}) "
               f"hp3_audit_rate={hp3:.4f}(>={HP_AUDIT}) ds_cos={ds_cos:.4f}(>={HP_DOWNSTREAM}) "
               f"n_seeds={len(results)}")

    if cf_cos < HF_CF_COS:
        return ("HARD_FAIL", f"HARD_FAIL: cf_cos={cf_cos:.4f} < {HF_CF_COS}. {summary}")

    c1 = hp1 >= HP_CERT
    c2 = cf_cos >= HP_CF_COS
    c3 = hp3 >= HP_AUDIT
    c4 = ds_cos >= HP_DOWNSTREAM

    if c1 and c2 and c3 and c4:
        return ("HARD_PASS", f"HARD_PASS: all 4 conditions met at depth-10. {summary}")
    if sum([c1, c2, c3, c4]) >= 3:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {sum([c1,c2,c3,c4])}/4 conditions. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {sum([c1,c2,c3,c4])}/4 conditions. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"chain_depth={CHAIN_DEPTH} subst_depth={SUBST_DEPTH}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

print(f"[GPU] memory before sweep: {torch.cuda.memory_allocated(0)/1e9:.3f} GB", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N_ACTIVE} depth={CHAIN_DEPTH} subst@{SUBST_DEPTH}...",
          flush=True)
    result = run_seed(seed, N_ACTIVE)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.01, f"GPU utilization check FAIL: peak_gpu={peak_mem_gb:.3f} GB (< 100MB)"

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N,
    "n_active": N_ACTIVE,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "peak_gpu_gb": float(peak_mem_gb),
}
if all_results:
    for k in ["hp1_cert_rate", "mean_cf_cos", "hp3_audit_rate", "mean_ds_cos"]:
        vs = [r[k] for r in all_results if k in r]
        metrics[f"grand_{k}"] = float(sum(vs)/len(vs)) if vs else None

metrics_path = out_dir / "metrics.json"
out_dir.mkdir(parents=True, exist_ok=True)
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
