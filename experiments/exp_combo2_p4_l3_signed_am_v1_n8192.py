"""
combo2_p4_l3_signed_am_v1_n8192 -- Wave 4 COMBO-2: p=4 DAM + L3 + signed-AM at N=8192.

SAME DESIGN AS n4096 VERSION but production envelope N=8192.
Unlocks Negative-Knowledge Tree + Hierarchical Refusal Cert + Counterfactual Abduction.

HARD-PASS: HP1 AND HP2 AND HP3 (all 3).
  HP1: l3_fidelity_A >= 0.85
  HP2: b_repulsion_rate >= 0.95
  HP3: parity_contamination <= 0.05
HARD-FAIL: l3_fidelity_A < 0.50 OR b_repulsion_rate < 0.50.
MIDDLE: 2/3 conditions met.

PRE-REGISTERED BANDS:
  HP: l3_fidelity_A >= 0.85, b_repulsion_rate >= 0.95, parity_contamination <= 0.05.
  HF: l3_fidelity_A < 0.50 OR b_repulsion_rate < 0.50.
  Calibration: first COMBO-2 test at N=8192; bands from n4096 pair.

PROT-018: anchor name contains _n8192; N MUST = 8192.
PROT-021: run_config includes N, M_inner, run_mode.
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

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "combo2_p4_l3_signed_am_v1_n8192"

# PROT-018: anchor has _n8192 -> N must = 8192
_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_INNER = 8
    M_MID = 4
    M_OUTER = 2
    M_B = 2
    N_QUERIES = 10
    NOISE_FRAC = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_INNER = 16
    M_MID = 8
    M_OUTER = 4
    M_B = 4
    N_QUERIES = 30
    NOISE_FRAC = 0.10

HP_L3_FIDELITY = 0.85
HP_B_REPULSION = 0.95
HP_PARITY_CONTAMINATION = 0.05
HF_L3_FIDELITY = 0.50
HF_B_REPULSION = 0.50

ALPHA_C = 0.138


def _selftest_p4_update():
    n = 4
    xi_0 = np.array([1.0, 1.0, -1.0, 1.0])
    Xi = xi_0.reshape(1, n)
    x = xi_0.copy()
    overlaps = Xi @ x
    h = (Xi.T @ (overlaps**3)) / n
    expected_h = xi_0 * (4.0**3) / 4.0
    assert np.allclose(h, expected_h, atol=1e-8), f"p=4 update: got {h}, expected {expected_h}"


def _selftest_hadamard():
    xi_a = np.array([1.0, -1.0, 1.0, -1.0])
    xi_b = np.array([1.0, 1.0, -1.0, -1.0])
    bound = xi_a * xi_b
    decoded = bound * xi_a
    assert np.allclose(decoded, xi_b, atol=1e-8), f"Hadamard decode: {decoded} != {xi_b}"


def _selftest_signed_am():
    n = 16
    rng = np.random.RandomState(0)
    eta_b = rng.choice([-1.0, 1.0], size=n)
    W_B = np.outer(eta_b, eta_b) / n
    result = W_B @ eta_b
    expected = eta_b
    assert np.allclose(result, expected, atol=1e-8), f"signed_AM: {result[:3]} != {expected[:3]}"


def _instrumentation_selftest():
    _selftest_p4_update()
    _selftest_hadamard()
    _selftest_signed_am()
    print("[selftest] combo2_p4_l3_signed_am_n8192: p4_update, hadamard, signed_am all PASS", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def p4_retrieve(Xi: np.ndarray, probe: np.ndarray, n_steps: int = 5, n: int = None) -> np.ndarray:
    if n is None:
        n = probe.shape[0]
    state = probe.copy()
    for _ in range(n_steps):
        overlaps = Xi @ state
        h = (Xi.T @ (overlaps**3)) / n
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    Xi_inner = rng.choice([-1.0, 1.0], size=(M_INNER, N)).astype(np.float64)
    Xi_ctx2 = rng.choice([-1.0, 1.0], size=(M_MID, N)).astype(np.float64)
    Xi_mid = Xi_ctx2 * Xi_inner[:M_MID]
    Xi_ctx3 = rng.choice([-1.0, 1.0], size=(M_OUTER, N)).astype(np.float64)
    Xi_outer = Xi_ctx3 * Xi_mid[:M_OUTER]

    Xi_A_sub = rng.choice([-1.0, 1.0], size=(M_B, N)).astype(np.float64)
    Xi_B = rng.choice([-1.0, 1.0], size=(M_B, N)).astype(np.float64)

    # L3 end-to-end fidelity
    l3_fidelities = []
    for q_idx in range(min(N_QUERIES, M_OUTER)):
        xi_outer_true = Xi_outer[q_idx]
        probe = xi_outer_true.copy()
        flip = rng.random(N) < NOISE_FRAC
        probe[flip] *= -1.0

        xi_outer_ret = p4_retrieve(Xi_outer, probe, n=N)
        xi_mid_ptr = xi_outer_ret * Xi_ctx3[q_idx]
        xi_mid_ret = p4_retrieve(Xi_mid, xi_mid_ptr, n=N)
        xi_inner_ptr = xi_mid_ret * Xi_ctx2[q_idx]
        xi_inner_ret = p4_retrieve(Xi_inner, xi_inner_ptr, n=N)
        xi_inner_true = Xi_inner[q_idx]
        fid = cosine_sim(xi_inner_ret, xi_inner_true)
        l3_fidelities.append(fid)

    l3_fid_mean = float(np.mean(l3_fidelities)) if l3_fidelities else 0.0

    # B-repulsion
    repulsion_count = 0
    n_b_queries = min(N_QUERIES, M_B)
    for b_idx in range(n_b_queries):
        eta_b = Xi_B[b_idx]
        probe_b = eta_b.copy()
        flip = rng.random(N) < NOISE_FRAC
        probe_b[flip] *= -1.0
        state = probe_b.copy()
        for _ in range(5):
            ov_A = Xi_A_sub @ state
            ov_B = Xi_B @ state
            h = (Xi_A_sub.T @ (ov_A**3) - Xi_B.T @ (ov_B**3)) / N
            state = np.sign(h)
            state[state == 0] = 1.0
        cos_to_b = cosine_sim(state, eta_b)
        if cos_to_b < -0.3:
            repulsion_count += 1

    b_repulsion_rate = repulsion_count / n_b_queries if n_b_queries > 0 else 0.0

    # Parity contamination
    contamination_flags = 0
    n_contam_tests = min(N_QUERIES, M_OUTER, M_B)
    for q_idx in range(n_contam_tests):
        xi_outer_true = Xi_outer[q_idx]
        probe = xi_outer_true.copy()
        flip = rng.random(N) < NOISE_FRAC
        probe[flip] *= -1.0
        xi_outer_ret = p4_retrieve(Xi_outer, probe, n=N)
        xi_mid_ptr = xi_outer_ret * Xi_ctx3[q_idx]
        xi_mid_ret = p4_retrieve(Xi_mid, xi_mid_ptr, n=N)
        xi_inner_ptr = xi_mid_ret * Xi_ctx2[q_idx]
        xi_inner_ret = p4_retrieve(Xi_inner, xi_inner_ptr, n=N)
        max_b_cos = max(abs(cosine_sim(xi_inner_ret, Xi_B[b])) for b in range(M_B))
        if max_b_cos > 0.5:
            contamination_flags += 1

    parity_contamination = contamination_flags / n_contam_tests if n_contam_tests > 0 else 0.0

    elapsed = time.time() - t0
    print(f"  [seed={seed}] l3_fid={l3_fid_mean:.4f} b_repulsion={b_repulsion_rate:.4f} "
          f"parity_contam={parity_contamination:.4f} elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "run_mode": RUN_MODE,
        "M_inner": M_INNER, "M_mid": M_MID, "M_outer": M_OUTER, "M_B": M_B,
        "l3_fidelity_A": float(l3_fid_mean),
        "b_repulsion_rate": float(b_repulsion_rate),
        "parity_contamination": float(parity_contamination),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    l3_fids = [r["l3_fidelity_A"] for r in results if "l3_fidelity_A" in r]
    b_reps = [r["b_repulsion_rate"] for r in results if "b_repulsion_rate" in r]
    p_conts = [r["parity_contamination"] for r in results if "parity_contamination" in r]

    if not l3_fids:
        return ("HARD_FAIL", "No valid results.")

    mean_l3 = float(np.mean(l3_fids))
    mean_brep = float(np.mean(b_reps))
    mean_pcont = float(np.mean(p_conts))

    summary = (f"l3_fidelity_A={mean_l3:.4f} (HP>={HP_L3_FIDELITY} HF<{HF_L3_FIDELITY}) "
               f"b_repulsion={mean_brep:.4f} (HP>={HP_B_REPULSION} HF<{HF_B_REPULSION}) "
               f"parity_contamination={mean_pcont:.4f} (HP<={HP_PARITY_CONTAMINATION}) "
               f"n_seeds={len(l3_fids)}")

    if mean_l3 < HF_L3_FIDELITY or mean_brep < HF_B_REPULSION:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp1 = mean_l3 >= HP_L3_FIDELITY
    hp2 = mean_brep >= HP_B_REPULSION
    hp3 = mean_pcont <= HP_PARITY_CONTAMINATION

    if hp1 and hp2 and hp3:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP conditions met. {summary}")
    if sum([hp1, hp2, hp3]) >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {sum([hp1,hp2,hp3])}/3 HP conditions. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: {sum([hp1,hp2,hp3])}/3 HP conditions. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_inner": M_INNER, "M_outer": M_OUTER, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N} M_inner={M_INNER} M_outer={M_OUTER} M_B={M_B}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "mean_l3_fidelity_A": float(np.mean([r["l3_fidelity_A"] for r in all_results])) if all_results else None,
    "mean_b_repulsion_rate": float(np.mean([r["b_repulsion_rate"] for r in all_results])) if all_results else None,
    "mean_parity_contamination": float(np.mean([r["parity_contamination"] for r in all_results])) if all_results else None,
}
metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
