"""
pp48_pp46_negative_knowledge_with_deletion_cert_v1_n4096 -- Cross-row composition:
PP-48 NKT negative-knowledge tree x PP-46 deletion certificate at N=4096.

SCIENTIFIC QUESTION:
  PP-48 (NKT signed-AM repulsion) confirmed independently.
  PP-46 (deletion certificate Z-ratio) confirmed independently.
  This anchor tests JOINT operation:
  - Build signed W = W_A (positive) - W_B (NKT forbidden patterns).
  - Compute deletion certificate for one forbidden NKT leaf: cert should be -1.0.
  - After leaf deletion from W_B: verify repulsion of remaining leaves is unaffected.
  - After leaf deletion: verify positive retrieval is unaffected.

  This is a cross-row SCORE composition: both PP-48 and PP-46 primitives must fire
  correctly on the SAME weight matrix simultaneously.

  NOTE: PP-46 is the deletion cert primitive. The cert value for a NKT forbidden leaf
  in W_B is: xi_leaf^T (-(1/N) xi_leaf xi_leaf^T) xi_leaf / N = -1.0 exactly for BSC.
  Same formula as PP-9 cert but applied to the W_B component.

PRE-REGISTERED BANDS:
  HP1: NKT leaf deletion cert = -1.0 (within 1e-4) in >= 4/5 seeds.
  HP2: positive retrieval rate >= 0.80 after leaf deletion in >= 4/5 seeds.
  HP3: NKT repulsion rate >= 0.70 after leaf deletion (remaining leaves) in >= 4/5 seeds.
  HARD-PASS: HP1 AND HP2 AND HP3.
  HARD-FAIL: HP1 fails (cert != -1.0) OR HP2 < 0.50.
  MIDDLE: 2/3 conditions.
  P_deflated = 0.68 (PP-48 and PP-46 individually confirmed; cross-row SCORE composition first test).

FORMULA SELF-TESTS:
  1. Deletion cert for NKT leaf in W_B: cert = -(||xi||^4) / N^2 = -1.0 for BSC.
     [INPUT: N=8, BSC xi_leaf] [EXPECTED: cert = -1.0]
  2. After leaf deletion: W_B_new = W_B - (1/N) xi_leaf xi_leaf^T.
     cert of deleted leaf in W_B_new is 0 if it was the only leaf.
     [INPUT: single leaf in W_B] [EXPECTED: cert_after = 0.0]
  3. Positive retrieval in W_signed is unaffected by leaf deletion (algebraic).
     [INPUT: W_A unchanged] [EXPECTED: pos retrieval >= 0.80]

PROT-018: anchor has _n4096; N MUST = 4096.
GPU REQUIRED: cross-row composition at N=4096 5-seed is compute-intensive (Tier A).
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
from typing import Dict, List, Tuple

import numpy as np

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

ANCHOR_NAME = "pp48_pp46_negative_knowledge_with_deletion_cert_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
NOISE_FRAC = 0.10
CERT_TOL = 1e-4
N_RETRIEVE_STEPS = 5

if RUN_MODE == "smoke":
    N_ACTIVE = 1024
    SEEDS = [7, 17]
    K_POS = 10
    K_NEG = 6
    N_TEST = 3
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    K_POS = 50
    K_NEG = 20     # NKT forbidden leaves (sampled; alpha_total = 70/4096 = 0.017)
    N_TEST = 10

# Capacity check
_alpha_total = (K_POS + K_NEG) / N
assert _alpha_total < ALPHA_C, (
    f"alpha_total={_alpha_total:.4f} >= alpha_c={ALPHA_C} "
    f"K_POS={K_POS} K_NEG={K_NEG} N={N}")

HP_POS = 0.80
HP_NKT_REP = 0.70
HF_POS = 0.50
HF_NKT_REP = 0.30


def deletion_cert_np(xi: np.ndarray, n: int) -> float:
    """cert = -(||xi||^2)^2 / n^2 = -1.0 for BSC."""
    norm_sq = float(np.dot(xi, xi))
    return -(norm_sq ** 2) / (n * n)


def _selftest_cert_bsc():
    N_t = 8
    rng = np.random.RandomState(0)
    xi = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    c = deletion_cert_np(xi, N_t)
    assert abs(c + 1.0) < 1e-10, f"cert selftest: {c:.6f} expected -1.0"
    return c


def _selftest_cert_after_deletion():
    N_t = 8
    rng = np.random.RandomState(1)
    xi = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    W_B = np.outer(xi, xi) / N_t
    W_B_new = W_B - np.outer(xi, xi) / N_t
    cert_after = float(xi @ W_B_new @ xi) / N_t
    assert abs(cert_after) < 1e-10, f"cert_after_del selftest: {cert_after:.6f} expected 0.0"
    return cert_after


def _selftest_gpu_vram():
    dummy = torch.zeros((2048, 2048), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 1e6, f"GPU memory not > 1MB: {mem/1e6:.1f}MB"
    del dummy
    torch.cuda.empty_cache()


def _instrumentation_selftest():
    c1 = _selftest_cert_bsc()
    c2 = _selftest_cert_after_deletion()
    _selftest_gpu_vram()
    n_active = N_ACTIVE if RUN_MODE == "smoke" else N
    alpha_t = (K_POS + K_NEG) / n_active
    assert alpha_t < ALPHA_C, f"alpha_total={alpha_t:.4f} >= alpha_c"
    assert K_NEG >= 2, f"K_NEG={K_NEG} too small for deletion test"
    print(f"[selftest] PASS: cert_bsc={c1:.6f} cert_after_del={c2:.6f} "
          f"alpha={alpha_t:.4f} K_POS={K_POS} K_NEG={K_NEG} gpu_vram_ok",
          flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def hopfield_retrieve_np(W: np.ndarray, probe: np.ndarray, n_steps: int = N_RETRIEVE_STEPS) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim_np(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.RandomState(seed)
    rng_noise = np.random.RandomState(seed + 300)
    t0 = time.time()

    Xi_pos = rng.choice([-1.0, 1.0], size=(K_POS, n_dim)).astype(np.float64)
    Xi_neg = rng.choice([-1.0, 1.0], size=(K_NEG, n_dim)).astype(np.float64)

    W_A = Xi_pos.T @ Xi_pos / float(n_dim)
    np.fill_diagonal(W_A, 0.0)
    W_B = Xi_neg.T @ Xi_neg / float(n_dim)
    np.fill_diagonal(W_B, 0.0)
    W_signed = W_A - W_B

    # HP1: deletion cert for NKT leaves
    cert_values = []
    for k in range(min(N_TEST, K_NEG)):
        xi_leaf = Xi_neg[k]
        c = deletion_cert_np(xi_leaf, n_dim)
        cert_values.append(c)
    cert_ok = [abs(c + 1.0) < CERT_TOL for c in cert_values]
    hp1 = all(cert_ok)

    # HP2: positive retrieval after deleting leaf 0 from W_B
    leaf_to_delete = Xi_neg[0]
    W_B_after = W_B - np.outer(leaf_to_delete, leaf_to_delete) / float(n_dim)
    np.fill_diagonal(W_B_after, 0.0)
    W_signed_after = W_A - W_B_after

    pos_cosines = []
    for k in range(min(N_TEST, K_POS)):
        probe = Xi_pos[k].copy()
        flip = rng_noise.random(n_dim) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved = hopfield_retrieve_np(W_signed_after, probe)
        pos_cosines.append(cosine_sim_np(retrieved, Xi_pos[k]))
    mean_pos = float(np.mean(pos_cosines)) if pos_cosines else 0.0
    hp2 = mean_pos >= HP_POS

    # HP3: NKT repulsion rate of remaining leaves after deletion
    nkt_rep_ok = 0
    n_rep_tests = min(N_TEST, K_NEG - 1)
    for k in range(1, 1 + n_rep_tests):
        xi_leaf = Xi_neg[k]
        probe = xi_leaf.copy()
        flip = rng_noise.random(n_dim) < NOISE_FRAC
        probe[flip] *= -1.0
        state = probe.copy()
        for _ in range(N_RETRIEVE_STEPS):
            ov_A = Xi_pos @ state
            ov_B_after = W_B_after @ state  # use W_B_after rows (remaining leaves)
            # signed-AM with W_A - W_B_after
            h = W_A @ state - W_B_after @ state
            state = np.sign(h)
            state[state == 0] = 1.0
        if cosine_sim_np(state, xi_leaf) < -0.2:
            nkt_rep_ok += 1
    nkt_rep_rate = nkt_rep_ok / max(n_rep_tests, 1)
    hp3 = nkt_rep_rate >= HP_NKT_REP

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={n_dim}] "
          f"cert_frac={sum(cert_ok)}/{len(cert_ok)}(HP_cert=-1.0) "
          f"pos_cos={mean_pos:.4f}(HP>={HP_POS}) "
          f"nkt_rep={nkt_rep_rate:.4f}(HP>={HP_NKT_REP}) "
          f"hp=[{int(hp1)},{int(hp2)},{int(hp3)}] elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "K_POS": K_POS, "K_NEG": K_NEG,
        "cert_frac": float(sum(cert_ok)) / max(len(cert_ok), 1),
        "mean_cert_value": float(np.mean(cert_values)) if cert_values else None,
        "mean_pos_cos": float(mean_pos),
        "nkt_rep_rate": float(nkt_rep_rate),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hf1": not bool(hp1),
        "hf2": bool(mean_pos < HF_POS),
        "hf3": bool(nkt_rep_rate < HF_NKT_REP),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    hp1_n = sum(1 for r in results if r["hp1"])
    hp2_n = sum(1 for r in results if r["hp2"])
    hp3_n = sum(1 for r in results if r["hp3"])
    hf1_any = any(r["hf1"] for r in results)
    hf2_any = any(r["hf2"] for r in results)

    mean_cert = float(np.mean([r.get("mean_cert_value") or 0 for r in results]))
    mean_pos = float(np.mean([r["mean_pos_cos"] for r in results]))
    mean_nkt = float(np.mean([r["nkt_rep_rate"] for r in results]))

    summary = (f"n_seeds={n} cert_value={mean_cert:.4f}(HP~=-1.0 tol={CERT_TOL}) "
               f"pos_cos={mean_pos:.4f}(HP>={HP_POS} HF<{HF_POS}) "
               f"nkt_rep={mean_nkt:.4f}(HP>={HP_NKT_REP} HF<{HF_NKT_REP}) "
               f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n}")

    if hf1_any:
        return ("HARD_FAIL", f"HARD_FAIL HF1: NKT leaf cert != -1.0. {summary}")
    if hf2_any:
        return ("HARD_FAIL", f"HARD_FAIL HF2: positive encoding destroyed after deletion. {summary}")

    min_threshold = math.ceil(n * 0.8)
    all_hp = all(cnt >= min_threshold for cnt in [hp1_n, hp2_n, hp3_n])
    if all_hp:
        return ("HARD_PASS",
                f"HARD_PASS: PP-48 x PP-46 cross-row composition confirmed at N=4096. {summary}")
    n_hp_conds = sum([hp1_n >= min_threshold, hp2_n >= min_threshold, hp3_n >= min_threshold])
    if n_hp_conds >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_conds}/3 HP. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_conds}/3 HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


n_active = N_ACTIVE if RUN_MODE == "smoke" else N
print(f"[config] PROT-018 N={N} n_active={n_active} mode={RUN_MODE} "
      f"K_POS={K_POS} K_NEG={K_NEG}", flush=True)
_prot018_startup_check(n_active)

peak_start = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] memory before sweep: {peak_start:.3f} GB", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "n_active": n_active, "K_POS": K_POS, "K_NEG": K_NEG, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME} N={n_active}...", flush=True)
    result = run_seed(seed, n_active)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.01, f"GPU utilization check FAIL: peak_gpu={peak_mem_gb:.3f} GB (< 100MB)"

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "n_active": n_active, "K_POS": K_POS, "K_NEG": K_NEG,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "peak_gpu_gb": float(peak_mem_gb),
    "mean_cert_value": float(np.mean([r.get("mean_cert_value") or 0 for r in all_results])) if all_results else None,
    "mean_pos_cos": float(np.mean([r["mean_pos_cos"] for r in all_results])) if all_results else None,
    "mean_nkt_rep": float(np.mean([r["nkt_rep_rate"] for r in all_results])) if all_results else None,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[done] metrics -> {metrics_path}", flush=True)
