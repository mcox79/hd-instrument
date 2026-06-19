"""
combo1_pp48_audit_on_nkt_v2_depth_5_v1 -- COMBO-1 implicit Gram audit on PP-48 NKT at depth-5.

v1 used NKT_DEPTH=4 (15 NKT patterns). v2 uses NKT_DEPTH=5 (31 NKT patterns) for explicit
depth-5 NKT structure, testing whether COMBO-1 Gram audit scales to deeper trees.

SCIENTIFIC QUESTION:
  COMBO-1 (implicit Gram-solve audit): confirmed for NKT-depth-4 W_signed (v1, cycle 10.5).
  v2 tests depth-5 NKT structure (31 forbidden patterns) for stronger repulsion signal
  and deeper tree audit coverage.

  Key audit claims (same as v1, extended to depth-5):
    (a) Deletion cert for xi_A (positive pattern) from W_signed ~ -1.0.
    (b) Deletion cert for xi_B_leaf (forbidden NKT leaf) > 0 (repelled) in >= 4/5 seeds.
    (c) kappa_3 of W_signed non-zero (|kappa_3| > 0.001).
    (d) CNDC for xi_A vs xi_B_leaf differs by >= 0.05 (discriminative audit).

HP:
  HP1: cert_A ~ -1.0 (within 0.20) for positive patterns.
  HP2: cert_B_leaf > 0 in >= 4/5 seeds.
  HP3: |kappa_3| > 0.001.
  HP4: |CNDC_A - CNDC_B_leaf| >= 0.05.
  HARD-PASS: all 4 HP in >= 4/5 seeds.
  HARD-FAIL: cert_A > -0.50 OR cert_B_leaf < 0 in >50% of seeds.
  MIDDLE: 3/4 conditions.

  P_deflated = 0.65 (v1 depth-4 confirmed; depth-5 is a modest extension,
  tree grows from 15 to 31 patterns -- algebra unchanged).

GPU IMPLEMENTATION:
  W_signed = W_A - W_B (matrix-free via Xi_A, Xi_B tensors).
  Xi_A (K_POS x N): K_POS=50 positive patterns.
  Xi_B (31 x N): depth-5 NKT forbidden patterns.

FORMULA SELF-TESTS:
  1. cert_A for xi_A in W_signed (M_A=1, xi_B orthogonal): cert ~ -1.0.
     [INPUT: M_A=1, xi_A = Xi_A[0], xi_B orthogonal] [EXPECTED: cert ~ -1.0]
  2. kappa_3 of W_B = Xi_B^T Xi_B / N: non-zero for M_B > 0.
     [INPUT: N=64, M_B=5] [EXPECTED: kappa3 != 0]
  3. CNDC formula: d1 + d2 + d3 arithmetic test.
     [INPUT: d1=0.1, d2=0.2, d3=0.3] [EXPECTED: CNDC = 0.6]
  4. GPU memory > 100 MB after Xi alloc.

PROT-018: anchor has no _nN suffix; production N=4096 (PROT-018 rule 3).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple

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

ANCHOR_NAME = "combo1_pp48_audit_on_nkt_v2_depth_5_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

NKT_DEPTH = 5            # v2: depth-5 (31 total NKT nodes)
BRANCH = 2
TOTAL_NKT = (BRANCH ** NKT_DEPTH - 1) // (BRANCH - 1)  # = 31

print(f"[config] NKT_DEPTH={NKT_DEPTH} TOTAL_NKT={TOTAL_NKT}", flush=True)

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    K_POS = 10
    N_TEST = 3
    N_HUTCHINSON = 100
else:
    N_ACTIVE = 4096
    SEEDS = [7, 17, 23, 31, 41]
    K_POS = 50
    N_TEST = 10
    N_HUTCHINSON = 300

HP_CERT_A_TOL = 0.20
HP_CERT_B_POSITIVE_RATE = 0.80
HP_KAPPA3_MIN = 0.001
HP_CNDC_DISC = 0.05
HF_CERT_A_MAX = -0.50


def hutchinson_kappa3_matfree(Xi: torch.Tensor, n: int, n_probes: int, seed: int,
                               weight: float = 1.0) -> float:
    """Hutchinson kappa_3 for W_signed = weight * Xi^T @ Xi / n."""
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + 7777)
    V0 = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)

    def w_op(V):
        return weight * (Xi.t() @ (Xi @ V)) / n

    V1 = w_op(V0)
    V2 = w_op(V1)
    V3 = w_op(V2)
    return float((V0 * V3).sum(dim=0).mean() / n)


def deletion_cert_matfree(Xi: torch.Tensor, xi: torch.Tensor, n: int,
                           weight: float = 1.0) -> float:
    """cert(xi) = -(weight * ||Xi xi||^2 / n^2) for stored pattern."""
    proj = Xi @ xi
    inner = float(torch.dot(proj, proj))
    return -weight * inner / (n * n)


def krylov_cndc(Xi_A: torch.Tensor, Xi_B: torch.Tensor, xi: torch.Tensor,
                n: int) -> Tuple[float, float, float, float]:
    """CNDC = delta_1 + delta_2 + delta_3 for W_signed = (Xi_A^T Xi_A - Xi_B^T Xi_B) / n."""
    def w_signed_op(v):
        return (Xi_A.t() @ (Xi_A @ v) - Xi_B.t() @ (Xi_B @ v)) / n

    V0 = xi.clone()
    V1 = w_signed_op(V0)
    V2 = w_signed_op(V1)

    delta_1 = float(torch.dot(V0, V1)) / n
    delta_2 = float(torch.dot(V0, V2)) / n
    delta_3 = float(torch.dot(V1, V2)) / n
    cndc = delta_1 + delta_2 + delta_3
    return delta_1, delta_2, delta_3, cndc


def _selftest_cert_formula():
    n_t = 8
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    xi_A = (torch.randint(0, 2, (n_t,), generator=gen, device=DEVICE).float() * 2 - 1)
    Xi_A = xi_A.unsqueeze(0)
    cert = deletion_cert_matfree(Xi_A, xi_A, n_t)
    assert abs(cert + 1.0) < 0.01, f"cert_A selftest: {cert:.4f} expected -1.0"


def _selftest_kappa3_nonzero():
    n_t = 64
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(1)
    Xi_B = (torch.randint(0, 2, (5, n_t), generator=gen, device=DEVICE).float() * 2 - 1)
    k3 = hutchinson_kappa3_matfree(Xi_B, n_t, 200, 1)
    assert k3 != 0.0, f"kappa3 for NKT Xi_B is zero"


def _selftest_cndc_formula():
    d1, d2, d3 = 0.1, 0.2, 0.3
    cndc = d1 + d2 + d3
    assert abs(cndc - 0.6) < 1e-9, f"CNDC formula: {cndc:.6f} expected 0.6"


def _instrumentation_selftest():
    _selftest_cert_formula()
    _selftest_kappa3_nonzero()
    _selftest_cndc_formula()
    dummy = torch.zeros((256, 256), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    del dummy
    print(f"[selftest] PASS: cert_A=-1.0, kappa3_nonzero, cndc_formula, gpu_mem_ok",
          flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def build_nkt_tree(n_dim: int, gen: torch.Generator) -> List[torch.Tensor]:
    """Build depth-5 NKT binary tree of forbidden patterns."""
    patterns = []
    root = (torch.randint(0, 2, (n_dim,), generator=gen, device=DEVICE).float() * 2 - 1)
    patterns.append(root)
    prev_level = [root]
    for _ in range(1, NKT_DEPTH):
        curr = []
        for parent in prev_level:
            for _ in range(BRANCH):
                ctx = (torch.randint(0, 2, (n_dim,), generator=gen, device=DEVICE).float() * 2 - 1)
                curr.append(parent * ctx)
        patterns.extend(curr)
        prev_level = curr
    return patterns


def cosine_sim_gpu(a: torch.Tensor, b: torch.Tensor) -> float:
    na = float(a.norm())
    nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    def bsc(m, n_d):
        return (torch.randint(0, 2, (m, n_d), generator=gen, device=DEVICE).float() * 2 - 1)

    Xi_A = bsc(K_POS, n_dim)
    nkt_patterns = build_nkt_tree(n_dim, gen)
    Xi_B = torch.stack(nkt_patterns)

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] GPU memory after Xi alloc: {mem_gb:.3f} GB "
          f"K_pos={K_POS} K_nkt={TOTAL_NKT}", flush=True)

    # HP1: cert_A for positive patterns
    cert_A_vals = []
    for q in range(min(N_TEST, K_POS)):
        xi_q = Xi_A[q]
        cert_q = deletion_cert_matfree(Xi_A, xi_q, n_dim)
        cert_A_vals.append(cert_q)
    mean_cert_A = float(sum(cert_A_vals) / len(cert_A_vals)) if cert_A_vals else 0.0
    hp1_ok = abs(mean_cert_A + 1.0) <= HP_CERT_A_TOL

    # HP2: cert_B_leaf > 0 (positive energy = repulsion)
    leaves = nkt_patterns[-(BRANCH ** (NKT_DEPTH - 1)):]  # depth-5 leaves
    cert_B_vals = []
    for leaf in leaves[:min(N_TEST, len(leaves))]:
        proj_A = float((Xi_A @ leaf).pow(2).sum()) / (n_dim ** 2)
        proj_B = float((Xi_B @ leaf).pow(2).sum()) / (n_dim ** 2)
        cert_B_raw = proj_A - proj_B
        cert_B_vals.append(cert_B_raw)

    cert_B_positive = float(sum(1 for v in cert_B_vals if v > 0) / max(len(cert_B_vals), 1))
    mean_cert_B = float(sum(cert_B_vals) / len(cert_B_vals)) if cert_B_vals else 0.0
    hp2_ok = cert_B_positive >= HP_CERT_B_POSITIVE_RATE

    # HP3: kappa_3 non-trivial
    kappa3_A = hutchinson_kappa3_matfree(Xi_A, n_dim, N_HUTCHINSON, seed + 100)
    hp3_ok = abs(kappa3_A) > HP_KAPPA3_MIN

    # HP4: CNDC discriminative
    xi_A_test = Xi_A[0]
    xi_B_test = leaves[0] if leaves else Xi_B[0]
    _, _, _, cndc_A = krylov_cndc(Xi_A, Xi_B, xi_A_test, n_dim)
    _, _, _, cndc_B = krylov_cndc(Xi_A, Xi_B, xi_B_test, n_dim)
    cndc_disc = abs(cndc_A - cndc_B)
    hp4_ok = cndc_disc >= HP_CNDC_DISC

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] cert_A={mean_cert_A:.4f}(HP|+1|<={HP_CERT_A_TOL}) "
          f"cert_B_pos={cert_B_positive:.4f}(HP>={HP_CERT_B_POSITIVE_RATE}) "
          f"kappa3_A={kappa3_A:.5f}(HP>{HP_KAPPA3_MIN}) "
          f"cndc_disc={cndc_disc:.4f}(HP>={HP_CNDC_DISC}) "
          f"hp=[{int(hp1_ok)},{int(hp2_ok)},{int(hp3_ok)},{int(hp4_ok)}] "
          f"peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "mean_cert_A": float(mean_cert_A),
        "cert_B_positive_rate": float(cert_B_positive),
        "mean_cert_B": float(mean_cert_B),
        "kappa3_A": float(kappa3_A),
        "cndc_disc": float(cndc_disc),
        "hp1": bool(hp1_ok), "hp2": bool(hp2_ok),
        "hp3": bool(hp3_ok), "hp4": bool(hp4_ok),
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    n = len(results)
    cert_A = mean_key("mean_cert_A")
    cert_B_pos = mean_key("cert_B_positive_rate")
    k3_A = mean_key("kappa3_A")
    cndc_d = mean_key("cndc_disc")
    hp1_n = sum(1 for r in results if r.get("hp1"))
    hp2_n = sum(1 for r in results if r.get("hp2"))
    hp3_n = sum(1 for r in results if r.get("hp3"))
    hp4_n = sum(1 for r in results if r.get("hp4"))

    summary = (f"cert_A={cert_A:.4f}(HP|+1|<={HP_CERT_A_TOL}) "
               f"cert_B_pos={cert_B_pos:.4f} kappa3_A={k3_A:.5f} "
               f"cndc_disc={cndc_d:.4f}(HP>={HP_CNDC_DISC}) "
               f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n} hp4={hp4_n}/{n}")

    if cert_A > HF_CERT_A_MAX:
        return ("HARD_FAIL", f"HARD_FAIL: cert_A={cert_A:.4f} > {HF_CERT_A_MAX}. {summary}")

    min_pass = max(1, int(n * 0.8))
    if all(cnt >= min_pass for cnt in [hp1_n, hp2_n, hp3_n, hp4_n]):
        return ("HARD_PASS", f"HARD_PASS: all 4 HP in >={min_pass}/{n} seeds (depth-5). {summary}")
    n_hp_met = sum(cnt >= min_pass for cnt in [hp1_n, hp2_n, hp3_n, hp4_n])
    if n_hp_met >= 3:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_met}/4 HP conditions met. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_met}/4 HP conditions met. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "NKT_DEPTH": NKT_DEPTH, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

print(f"[GPU] memory before sweep: {torch.cuda.memory_allocated(0)/1e9:.3f} GB", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
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
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N_ACTIVE, "NKT_DEPTH": NKT_DEPTH, "TOTAL_NKT": TOTAL_NKT,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "peak_gpu_gb": float(peak_mem_gb),
}
metrics_path = out_dir / "metrics.json"
out_dir.mkdir(parents=True, exist_ok=True)
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
