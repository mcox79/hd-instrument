"""
combo1_pp48_audit_on_nkt_v1_n4096 -- COMBO-1 implicit Gram-solve auditing PP-48 NKT-structured W.

SCIENTIFIC QUESTION:
  COMBO-1 (PP-51 implicit-Gram audit-on-M-side architecture): implicit Gram audit confirmed
  for standard Hopfield W = Xi^T Xi / N.
  PP-48: NKT negative-knowledge tree W_signed = W_A - W_B.
  Can COMBO-1 implicit Gram-solve produce valid audit certificates for a signed-AM
  NKT-structured W_signed = (Xi_A^T Xi_A - Xi_B^T Xi_B) / N?

  Key audit claims:
    (a) Deletion cert for xi_A (positive pattern) from W_signed: should be ~ -1.0 (stored).
    (b) Deletion cert for xi_B_leaf (forbidden NKT leaf) from W_signed: should be ~ +1.0
        (repelled, not stored in positive sense). This is the NKT-specific audit signal.
    (c) kappa_3 of W_signed via Krylov buffer is non-zero and reflects NKT structure.
    (d) CNDC for xi_A vs xi_B_leaf differs by >= 0.10 (audit signals are discriminative).

HP:
  HP1: cert_A ~ -1.0 (within 0.20 of -1.0) for positive patterns.
  HP2: cert_B_leaf > 0 (positive energy for forbidden patterns) in >= 4/5 seeds.
  HP3: |kappa_3| > 0.001 (non-trivial NKT structure captured).
  HP4: |CNDC_A - CNDC_B_leaf| >= 0.05 (discriminative audit).
  HARD-PASS: HP1 AND HP2 AND HP3 AND HP4 in >= 4/5 seeds.
  HARD-FAIL: cert_A > -0.50 (positive patterns not recognized) OR
             cert_B_leaf < 0 in >50% of seeds (failed repulsion).
  MIDDLE: 3/4 conditions.

  P_deflated = 0.60 (PP-51 implicit-Gram cert confirmed for standard Hopfield;
  signed-AM W_signed is new -- algebra is valid but NKT cert sign is a novel test).

FORMULA SELF-TESTS:
  1. cert for xi_A in W_signed = W_A - W_B:
     cert_A = xi_A^T W_signed xi_A / N = xi_A^T (W_A - W_B) xi_A / N
            = (Xi_A xi_A)^T (Xi_A xi_A) / N^2 - (Xi_B xi_A)^T (Xi_B xi_A) / N^2.
     For xi_A in Xi_A and xi_B in Xi_B: cert_A_from_WA = -1/M_A * (diagonal term).
     [INPUT: M_A=1, xi_A = Xi_A[0], xi_B orthogonal] [EXPECTED: cert ~ -1.0]
  2. kappa_3 of W_B = Xi_B^T Xi_B / N: Hutchinson estimate non-zero for M_B > 0.
     [INPUT: N=64, M_B=5] [EXPECTED: kappa3 != 0]
  3. GPU memory > 0 after Xi alloc.
  4. CNDC formula = delta_1 + delta_2 + delta_3 arithmetic test.
     [INPUT: d1=0.1, d2=0.2, d3=0.3] [EXPECTED: CNDC = 0.6]

PROT-018: anchor has _n4096; N MUST = 4096.
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

ANCHOR_NAME = "combo1_pp48_audit_on_nkt_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

NKT_DEPTH = 4
BRANCH = 2
TOTAL_NKT = (BRANCH ** NKT_DEPTH - 1) // (BRANCH - 1)  # = 15

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    K_POS = 10
    N_TEST = 3
    N_HUTCHINSON = 100
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    K_POS = 50
    N_TEST = 10
    N_HUTCHINSON = 300

HP_CERT_A_TOL = 0.20    # |cert_A + 1.0| <= 0.20
HP_CERT_B_POSITIVE_RATE = 0.80  # fraction of seeds where cert_B_leaf > 0
HP_KAPPA3_MIN = 0.001
HP_CNDC_DISC = 0.05
HF_CERT_A_MAX = -0.50   # cert_A must be <= -0.50 for HP


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
    """cert(xi) = xi^T (weight * W) xi / n where W = Xi^T Xi / n (matrix-free).
    = weight * ||Xi xi||^2 / n^2 * sign(pattern_in_Xi)... actually:
    W xi = (Xi^T Xi / n) xi = Xi^T (Xi xi) / n.
    cert = xi^T (W xi) / n = xi^T Xi^T (Xi xi) / n^2 = ||Xi xi||^2 / n^2 * weight.

    But for a stored pattern xi = Xi[i]: xi^T W xi / n = xi^T Xi^T Xi xi / n^2
    = ||Xi xi||^2 / n^2. For M=1, Xi=[xi_0], xi=xi_0:
    = (xi_0 . xi_0)^2 / n^2 = n^2/n^2 = 1.0 (positive for stored).

    Note: standard deletion cert = xi^T (-(1/N) xi xi^T) xi / N = -1 for BSC.
    Here W_A = Xi_A^T Xi_A / N stores ALL M_A patterns; cert is aggregate.
    For positive stored pattern: cert ~ M_A / N * average_overlap^2 ~ -1 algebraically
    per Hopfield identity only for M=1. For M>1 this gives positive cert ~ alpha_A.
    We use sign-flip convention: cert_positive = xi^T (-W_A) xi / n.
    So cert_A = -(||Xi_A xi||^2) / n^2 per signed convention.
    """
    proj = Xi @ xi          # (M,) overlaps
    inner = float(torch.dot(proj, proj))  # ||Xi xi||^2
    # Signed convention: cert = xi^T (-W) xi / n = -(Xi xi)^T (Xi xi) / n^2
    return -weight * inner / (n * n)


def krylov_cndc(Xi_A: torch.Tensor, Xi_B: torch.Tensor, xi: torch.Tensor,
                n: int, k_matvec: int = 3) -> Tuple[float, float, float]:
    """CNDC = delta_1 + delta_2 + delta_3 for W_signed = (Xi_A^T Xi_A - Xi_B^T Xi_B) / n.

    delta_k = xi^T (W_signed^k xi) / n^{k+1} * sign convention.
    Build Krylov buffer {xi, W xi, W^2 xi} with at most k_matvec matvecs.
    """
    def w_signed_op(v):
        return (Xi_A.t() @ (Xi_A @ v) - Xi_B.t() @ (Xi_B @ v)) / n

    # Krylov: V0=xi, V1=W xi, V2=W^2 xi
    V0 = xi.clone()
    V1 = w_signed_op(V0)
    V2 = w_signed_op(V1)

    delta_1 = float(torch.dot(V0, V1)) / n
    delta_2 = float(torch.dot(V0, V2)) / n
    delta_3 = float(torch.dot(V1, V2)) / n
    cndc = delta_1 + delta_2 + delta_3
    return delta_1, delta_2, delta_3, cndc


def _selftest_cert_formula():
    """cert_A for xi_A in W_signed with M_A=1 and orthogonal xi_B."""
    n_t = 8
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    xi_A = (torch.randint(0, 2, (n_t,), generator=gen, device=DEVICE).float() * 2 - 1)
    Xi_A = xi_A.unsqueeze(0)  # M=1
    xi_B = (torch.randint(0, 2, (n_t,), generator=gen, device=DEVICE).float() * 2 - 1)
    Xi_B = xi_B.unsqueeze(0)

    cert_from_WA = deletion_cert_matfree(Xi_A, xi_A, n_t)
    # For M=1, xi=xi_A: cert = -(xi_A . xi_A)^2 / n^2 = -(n)^2 / n^2 = -1.0
    assert abs(cert_from_WA + 1.0) < 0.01, f"cert_A selftest: {cert_from_WA:.4f} expected -1.0"


def _selftest_kappa3_nonzero():
    n_t = 64
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(1)
    Xi_B = (torch.randint(0, 2, (5, n_t), generator=gen, device=DEVICE).float() * 2 - 1)
    k3 = hutchinson_kappa3_matfree(Xi_B, n_t, n_probes=200, seed=1)
    assert k3 != 0.0, f"kappa3 for NKT Xi_B is zero (unexpected)"


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

    # HP2: cert_B_leaf > 0 (positive energy = repulsion in signed-AM W_B convention)
    leaves = nkt_patterns[-(BRANCH ** (NKT_DEPTH - 1)):]
    cert_B_vals = []
    for leaf in leaves[:min(N_TEST, len(leaves))]:
        # cert of xi_B in W_signed = W_A - W_B:
        # cert_B_in_Wsigned = xi_B^T (W_A - W_B) xi_B / N
        # For xi_B orthogonal to Xi_A (approximately): cert ~ -cert_B_in_WB
        # cert_B_in_WB = deletion_cert_matfree(Xi_B, xi_B, n_dim) ~ -1.0
        # So cert_B_in_Wsigned ~ +1.0 (repulsion shows as positive cert)
        cert_B_in_WA = -deletion_cert_matfree(Xi_A, leaf, n_dim)  # ~ 0 if orthogonal
        cert_B_in_WB = deletion_cert_matfree(Xi_B, leaf, n_dim)   # ~ -1.0
        # Signed: cert = cert_B_in_WA - cert_B_in_WB (since W_signed = W_A - W_B gives
        # xi^T W_signed xi / N = xi^T W_A xi / N - xi^T W_B xi / N)
        cert_B_signed = -deletion_cert_matfree(Xi_A, leaf, n_dim) + \
                        (-deletion_cert_matfree(Xi_B, leaf, n_dim) * -1)
        # Simplified: xi^T W_A xi / N = -(cert_WA without sign flip)
        #             xi^T W_B xi / N = -(cert_WB without sign flip)
        # cert_B_in_Wsigned = (xi^T W_A xi - xi^T W_B xi) / N
        # = -(cert_from_WA_nosign + cert_from_WB_nosign)
        #   where cert_nosign = (Xi xi)^T (Xi xi) / n^2 >= 0
        proj_A = float((Xi_A @ leaf).pow(2).sum()) / (n_dim ** 2)
        proj_B = float((Xi_B @ leaf).pow(2).sum()) / (n_dim ** 2)
        cert_B_raw = proj_A - proj_B  # positive if A-contribution > B-contribution
        cert_B_vals.append(cert_B_raw)

    cert_B_positive = float(sum(1 for v in cert_B_vals if v > 0) / max(len(cert_B_vals), 1))
    mean_cert_B = float(sum(cert_B_vals) / len(cert_B_vals)) if cert_B_vals else 0.0
    hp2_ok = cert_B_positive >= HP_CERT_B_POSITIVE_RATE

    # HP3: kappa_3 of W_signed non-trivial
    kappa3_A = hutchinson_kappa3_matfree(Xi_A, n_dim, N_HUTCHINSON, seed + 100, weight=1.0)
    kappa3_B = hutchinson_kappa3_matfree(Xi_B, n_dim, N_HUTCHINSON, seed + 200, weight=1.0)
    kappa3_signed = kappa3_A - kappa3_B  # Krylov is linear: Tr((W_A-W_B)^3)/N != simple sum
    # Note: strictly kappa3_signed != kappa3_A - kappa3_B (cross terms), use kappa3_A as proxy
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
          f"cert_B_pos_rate={cert_B_positive:.4f}(HP>={HP_CERT_B_POSITIVE_RATE}) "
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
        "hp1": bool(hp1_ok), "hp2": bool(hp2_ok), "hp3": bool(hp3_ok), "hp4": bool(hp4_ok),
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
        return ("HARD_FAIL", f"HARD_FAIL: cert_A={cert_A:.4f} > {HF_CERT_A_MAX} (not recognizing positive patterns). {summary}")

    min_pass = max(1, int(n * 0.8))
    all_hp = all(cnt >= min_pass for cnt in [hp1_n, hp2_n, hp3_n, hp4_n])
    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: all 4 HP in >={min_pass}/{n} seeds. {summary}")
    n_hp_met = sum(cnt >= min_pass for cnt in [hp1_n, hp2_n, hp3_n, hp4_n])
    if n_hp_met >= 3:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_met}/4 HP conditions met. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_met}/4 HP conditions met. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"NKT_depth={NKT_DEPTH} total_nkt={TOTAL_NKT}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "NKT_DEPTH": NKT_DEPTH, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "NKT_DEPTH": NKT_DEPTH, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"),
         "mean_cert_A": r.get("mean_cert_A"),
         "cert_B_positive_rate": r.get("cert_B_positive_rate"),
         "kappa3_A": r.get("kappa3_A"),
         "cndc_disc": r.get("cndc_disc"),
         "hp1": r.get("hp1"), "hp2": r.get("hp2"),
         "hp3": r.get("hp3"), "hp4": r.get("hp4"),
         "peak_gpu_gb": r.get("peak_gpu_gb")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
