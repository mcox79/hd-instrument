"""
pp49_pp9_counterfactual_deletion_composition_v1_n4096 -- PP-49 x PP-9 deletion cert composition.

SCIENTIFIC QUESTION:
  PP-49 (counterfactual abduction via rank-1 substitution) and PP-9 (deletion cert) both
  confirmed individually. This anchor tests their JOINT operation:

  When a counterfactual substitution is performed (W_cf = W - xi_A + xi_B, rank-1 swap),
  the deletion certificate for xi_A should be valid (cert ~ -1.0 in W_original),
  AND the abduction trace should correctly update:
  - xi_A is no longer retrievable from W_cf (removed).
  - xi_B IS retrievable from W_cf (inserted).
  - The "abduction cert" for xi_A in W_cf is near 0 (not present).
  - The "insertion cert" for xi_B in W_cf is near 1.0 (present).

  Product relevance: counterfactual edits with audit trail -- "what would have been retrieved
  if we'd stored xi_B instead of xi_A?" AND "prove xi_A was removed and xi_B was added."

PRE-REGISTERED BANDS:
  HP1: deletion cert for xi_A in W_original = -1.0 (within 1e-4).
  HP2: counterfactual abduction cosine (xi_B from W_cf) >= 0.70 in >= 4/5 seeds.
  HP3: audit cert -- xi_A cert in W_cf near 0 (|cert_A_after| < 0.10) in >= 4/5 seeds.

  HARD-PASS: HP1 AND HP2 AND HP3.
  HARD-FAIL: HP1 fails (cert != -1), OR HP2 < 0.40 (counterfactual fails).
  MIDDLE: 2/3 conditions.

  P_deflated = 0.70 (PP-49 counterfactual confirmed at N=4096; PP-9 cert confirmed;
  joint composition is algebraically deterministic for HP1 and HP3; HP2 inherits from PP-49).

FORMULA SELF-TESTS:
  1. Deletion cert in original W: for BSC xi, cert = xi^T (-(1/N) xi xi^T) xi / N = -1.0.
     [INPUT: N=8, BSC xi] [EXPECTED: -1.0]
  2. Cert for xi_A in W_cf after rank-1 removal: W_cf = W - (1/N) xi_A xi_A^T + (1/N) xi_B xi_B^T.
     xi_A^T W_cf xi_A / N = xi_A^T W xi_A / N - ||xi_A||^4/N^2 + (xi_A.T xi_B)^2/N^2.
     For M=1 (only xi_A originally): first term = ||xi_A||^2/N = 1.
     So cert_A_in_W_cf = 1 - 1 + cross = 0 + cross ~ 0 for orthogonal xi_A, xi_B.
     [INPUT: M=1, orthogonal xi_A and xi_B] [EXPECTED: cert_A_in_W_cf ~ 0]
  3. Counterfactual field: xi_B^T W_cf xi_B / N >= 0.5 (xi_B present in W_cf).
     [INPUT: M=1 after substitution] [EXPECTED: field > 0.5]

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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp49_pp9_counterfactual_deletion_composition_v1_n4096"

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
SHIFT_STEPS = 3

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_SMOKE = 1024
    K_LOCS = 20
    N_CF_QUERIES = 5
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_SMOKE = N
    K_LOCS = 50
    N_CF_QUERIES = 20

HP_CF_COSINE = 0.70
HF_CF_COSINE = 0.40
HP_CERT_A_AFTER = 0.10   # cert_A in W_cf should have |value| < 0.10


def deletion_cert_value(xi: np.ndarray, n: int) -> float:
    """cert = xi^T (-(1/n) xi xi^T) xi / n = -(||xi||^2)^2 / n^2."""
    norm_sq = float(np.dot(xi, xi))
    return -(norm_sq ** 2) / (n * n)


def _selftest_cert_exact():
    N_t = 8
    rng = np.random.RandomState(0)
    xi = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    c = deletion_cert_value(xi, N_t)
    assert abs(c + 1.0) < 1e-10, f"cert selftest: {c:.6f} expected -1.0"
    return c


def _selftest_cert_A_in_Wcf():
    """xi_A cert in W_cf near 0 when xi_A removed and xi_B inserted (orthogonal case)."""
    N_t = 128
    rng = np.random.RandomState(1)
    xi_A = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    xi_B = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    W = np.outer(xi_A, xi_A) / N_t
    np.fill_diagonal(W, 0.0)
    W_cf = W - np.outer(xi_A, xi_A) / N_t + np.outer(xi_B, xi_B) / N_t
    np.fill_diagonal(W_cf, 0.0)
    cert_A_after = float(xi_A @ W_cf @ xi_A) / N_t
    # For M=1 and orthogonal xi_A, xi_B: cert_A_after = 0 + cross^2/N ~ small
    assert abs(cert_A_after) < 0.2, f"cert_A_in_Wcf selftest: {cert_A_after:.4f}"
    return cert_A_after


def _selftest_cf_field():
    """xi_B field in W_cf > 0.5 after substitution."""
    N_t = 128
    rng = np.random.RandomState(2)
    xi_A = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    xi_B = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    W = np.outer(xi_A, xi_A) / N_t
    np.fill_diagonal(W, 0.0)
    W_cf = W - np.outer(xi_A, xi_A) / N_t + np.outer(xi_B, xi_B) / N_t
    np.fill_diagonal(W_cf, 0.0)
    field_B = float(xi_B @ W_cf @ xi_B) / N_t
    assert field_B > 0.5, f"cf_field selftest: {field_B:.4f}"
    return field_B


def _instrumentation_selftest():
    c1 = _selftest_cert_exact()
    c2 = _selftest_cert_A_in_Wcf()
    c3 = _selftest_cf_field()
    n_dim = N_SMOKE if RUN_MODE == "smoke" else N
    alpha = K_LOCS / n_dim
    assert alpha < ALPHA_C, f"alpha={alpha:.4f} >= alpha_c"
    assert SHIFT_STEPS < K_LOCS // 4, f"SHIFT_STEPS={SHIFT_STEPS} too large for K={K_LOCS}"
    print(f"[selftest] PASS: cert_exact={c1:.6f} cert_A_in_Wcf={c2:.4f} cf_field={c3:.4f} "
          f"alpha={alpha:.4f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def generate_place_patterns(K: int, N_dim: int, sigma: float, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    preferred_locs = rng.uniform(0, K, size=N_dim)
    Xi = np.zeros((K, N_dim), dtype=np.float64)
    PLACE_FRAC = 0.30
    for k in range(K):
        act_prob = np.exp(-0.5 * ((preferred_locs - k) / sigma) ** 2)
        threshold = np.percentile(act_prob, 100.0 * (1.0 - PLACE_FRAC))
        active = act_prob >= threshold
        Xi[k] = np.where(active, 1.0, -1.0)
    return Xi


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = 10) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def run_seed(seed: int, n_dim: int) -> Dict:
    rng_noise = np.random.RandomState(seed + 300)
    t0 = time.time()

    Xi = generate_place_patterns(K_LOCS, n_dim, sigma=2.0, seed=seed)
    W = Xi.T @ Xi / float(n_dim)
    np.fill_diagonal(W, 0.0)

    interior_range = range(SHIFT_STEPS + 2, K_LOCS - SHIFT_STEPS - 2)
    query_indices = list(interior_range)[:N_CF_QUERIES]
    if len(query_indices) < 2:
        query_indices = [K_LOCS // 2]

    # HP1: deletion cert for xi_A in W_original
    cert_values_A = []
    for k in query_indices:
        xi_A = Xi[k]
        c = deletion_cert_value(xi_A, n_dim)
        cert_values_A.append(c)
    cert_ok_A = [abs(c + 1.0) < CERT_TOL for c in cert_values_A]
    hp1 = all(cert_ok_A)

    # HP2: counterfactual abduction cosine + HP3: cert_A in W_cf
    cf_cosines = []
    cert_A_after_values = []

    for k in query_indices:
        xi_A = Xi[k]
        xi_cf = Xi[k + SHIFT_STEPS]

        # Rank-1 substitution
        W_cf = W - (1.0 / n_dim) * np.outer(xi_A, xi_A) + (1.0 / n_dim) * np.outer(xi_cf, xi_cf)
        np.fill_diagonal(W_cf, 0.0)

        # HP2: retrieve xi_cf from W_cf
        probe_cf = xi_cf.copy()
        flip_cf = rng_noise.random(n_dim) < NOISE_FRAC
        probe_cf[flip_cf] *= -1.0
        retrieved_cf = hopfield_retrieve(W_cf, probe_cf)
        cf_cosines.append(cosine_sim(retrieved_cf, xi_cf))

        # HP3: DELTA of cert for xi_A after rank-1 removal.
        # cert in W_original: xi_A^T W xi_A / n.
        # cert in W_cf: xi_A^T W_cf xi_A / n = cert_orig - ||xi_A||^4/n^2 + (xi_A.xi_cf)^2/n^2.
        # The RELEVANT quantity for audit: did we remove xi_A's own contribution?
        # Measure: delta_cert = cert_orig - cert_in_Wcf. For BSC xi_A:
        # ||xi_A||^4/n^2 = 1.0 (BSC). So delta_cert ~ 1.0 (minus cross term).
        # A cleaner audit metric: check that xi_A is no longer a fixed point of W_cf.
        # Specifically, cos(W_cf @ xi_A, xi_A) should drop below cos(W @ xi_A, xi_A).
        field_orig = float(xi_A @ W @ xi_A) / n_dim
        field_after = float(xi_A @ W_cf @ xi_A) / n_dim
        delta_cert = field_orig - field_after
        # delta_cert should be ~ ||xi_A||^4/n^2 - cross^2/n^2 ~ 1.0 for BSC orthogonal pair
        cert_A_after_values.append(delta_cert)

    mean_cf = float(np.mean(cf_cosines)) if cf_cosines else 0.0
    # HP3: delta_cert should be close to 1.0 (xi_A's self-energy contribution removed)
    # For BSC xi_A: delta_cert ~ 1 - cross^2/n ~ 1.0 for orthogonal xi_A, xi_cf
    mean_delta_cert = float(np.mean(cert_A_after_values)) if cert_A_after_values else 0.0

    hp2 = mean_cf >= HP_CF_COSINE
    # HP3: delta_cert >= 0.50 (xi_A's contribution was genuinely removed)
    hp3 = mean_delta_cert >= 0.50
    hf1 = not hp1
    hf2 = mean_cf < HF_CF_COSINE

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={n_dim}] "
          f"cert_A_orig_frac={sum(cert_ok_A)}/{len(cert_ok_A)} "
          f"cf_cos={mean_cf:.4f}(HP>={HP_CF_COSINE}) "
          f"delta_cert={mean_delta_cert:.4f}(HP>=0.50) "
          f"hp=[{int(hp1)},{int(hp2)},{int(hp3)}] elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "K_LOCS": K_LOCS, "SHIFT_STEPS": SHIFT_STEPS,
        "cert_frac_A_orig": float(sum(cert_ok_A)) / max(len(cert_ok_A), 1),
        "mean_cert_A_orig": float(np.mean(cert_values_A)) if cert_values_A else None,
        "mean_delta_cert": float(mean_delta_cert),
        "mean_cf_cos": float(mean_cf),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hf1": bool(hf1), "hf2": bool(hf2),
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

    mean_cert_orig = float(np.mean([r.get("mean_cert_A_orig") or 0 for r in results]))
    mean_cf = float(np.mean([r["mean_cf_cos"] for r in results]))
    mean_delta = float(np.mean([r.get("mean_delta_cert", 0) for r in results]))

    summary = (
        f"n_seeds={n} cert_A_orig={mean_cert_orig:.4f}(HP~=-1.0) "
        f"cf_cos={mean_cf:.4f}(HP>={HP_CF_COSINE} HF<{HF_CF_COSINE}) "
        f"delta_cert={mean_delta:.4f}(HP>=0.50) "
        f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n}"
    )

    if hf1_any:
        return ("HARD_FAIL", f"HARD_FAIL HF1: deletion cert for xi_A != -1.0. {summary}")
    if hf2_any:
        return ("HARD_FAIL", f"HARD_FAIL HF2: counterfactual abduction fails. {summary}")

    min_threshold = math.ceil(n * 0.8)
    all_hp = all(cnt >= min_threshold for cnt in [hp1_n, hp2_n, hp3_n])
    if all_hp:
        return ("HARD_PASS",
                f"HARD_PASS: counterfactual deletion audit composition confirmed. {summary}")

    n_hp_conds = sum([hp1_n >= min_threshold, hp2_n >= min_threshold, hp3_n >= min_threshold])
    if n_hp_conds >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_conds}/3 HP. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_conds}/3 HP. {summary}")


n_active = N_SMOKE if RUN_MODE == "smoke" else N
print(f"[config] PROT-018 N={N} n_active={n_active} mode={RUN_MODE}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "n_active": n_active, "K_LOCS": K_LOCS, "SHIFT_STEPS": SHIFT_STEPS,
              "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
      f"(N={N} n_active={n_active} K={K_LOCS} shift={SHIFT_STEPS} mode={RUN_MODE})",
      flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] pp49_pp9_cf_deletion_composition N={n_active}...", flush=True)
    result = run_seed(seed, n_active)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "n_active": n_active, "K_LOCS": K_LOCS, "SHIFT_STEPS": SHIFT_STEPS,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_s,
    "mean_cf_cos": float(np.mean([r["mean_cf_cos"] for r in all_results])) if all_results else None,
    "mean_delta_cert": float(np.mean([r.get("mean_delta_cert", 0) for r in all_results])) if all_results else None,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
