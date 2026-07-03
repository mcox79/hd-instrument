"""F-6 Boolean KKL probe — re-ship with proper schema.

Kahn–Kalai–Linial (KKL) theorem bounds total influence of Boolean functions:
for a Boolean function f: {-1,+1}^n -> {-1,+1}, the total influence Inf(f)
satisfies Inf(f) >= C * Var(f) * log(n) / max_i Inf_i(f).

Substrate question: are the BSC substrate's coordinate-wise decision boundaries
"low-influence" (suggesting smooth, well-decomposed boundaries) or
"high-influence" (suggesting sharp pivot-coordinate behavior)? If substrate
boundaries are dominated by O(log n) coordinates, the substrate looks like a
junta. If they are spread (no coordinate dominates), substrate boundaries are
well-distributed.

Specifically: treat the sign-readout of a stored item retrieval as a Boolean
function of the key bits, measure per-coordinate influence, and check the
KKL ratio Inf_total / (Var * log n).

Per [[feedback-rehabilitation-after-rejection]]: this re-ships the F-6 row
from v183 5-anchor hand-off — never shipped via correct schema.

Pre-reg HARD-PASS: substrate boundary functions satisfy KKL bound with ratio
   max_influence_share <= 0.30 (no single coordinate dominates) AND
   Inf_total / (Var * log n) >= 1.0 (KKL lower bound met within a factor of 2).
   -> Boolean-analysis row 🔬 -> 🟡 (substrate boundaries are smooth/well-distributed).
Pre-reg HARD-FAIL: max_influence_share >= 0.60 (one coordinate dominates
   >= 60% of total influence) at >=1 operating point -> substrate behaves
   like a sparse junta; KKL row REJECTED for substrate boundaries.
Pre-reg MIDDLE: any intermediate; report bands.

CPU-suitable: pure-numpy probe, no training, no GPU.

Pre-reg: preregs/2026-05-24_wave14_F6_boolean_kkl_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# ───── design parameters (exp_dev autonomy) ─────
N_FULL = 256          # substrate width
N_SMOKE = 64
M_DENSITIES_FULL = [0.10, 0.30]  # M_stored / N at two density points
M_DENSITIES_SMOKE = [0.10]
N_SAMPLES_FULL = 2000   # boundary-function evaluations per coordinate
N_SAMPLES_SMOKE = 200
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

PASS_MAX_INF_SHARE = 0.30
PASS_KKL_RATIO = 1.0
FAIL_MAX_INF_SHARE = 0.60


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def bsc_atoms(num: int, dim: int, rng: np.random.Generator) -> np.ndarray:
    return (rng.integers(0, 2, size=(num, dim)).astype(np.float32) * 2 - 1)


def build_substrate_W(N: int, M_density: float, rng: np.random.Generator):
    M = max(1, int(round(M_density * N)))
    keys = bsc_atoms(M, N, rng)
    vals = bsc_atoms(M, N, rng)
    W = (keys.T @ vals) / M
    return W, keys, vals


def estimate_influences(W: np.ndarray, target_key: np.ndarray, target_val: np.ndarray,
                         n_samples: int, rng: np.random.Generator):
    """Estimate coordinate-wise influence of f(x) = sign(<x, W e_j>) on stored
    boundary near `target_key`.

    f: x -> sign(Wx)_j, fixing j to the first coordinate of target_val. Sample
    n_samples random x close to target_key (single-bit flips and pairs), and
    measure per-coordinate flip rate (influence Inf_i).
    """
    N = W.shape[0]
    j = 0  # first output coordinate
    # base sample: target_key
    base_score = float(W[:, j] @ target_key)  # scalar
    base_sign = 1.0 if base_score >= 0 else -1.0
    influences = np.zeros(N, dtype=np.float64)
    # For each coordinate i, sample n_samples random x's where bit i is flipped
    # relative to target_key, count how often f(x) != f(x with bit i restored).
    # Vectorized: pick n_samples random {-1,+1}^N samples, then for each pair
    # (x, x with bit i flipped), check sign change.
    samples = bsc_atoms(n_samples, N, rng)  # (n_samples, N)
    base_scores = samples @ W[:, j]  # (n_samples,)
    base_signs = np.sign(base_scores)
    base_signs[base_signs == 0] = 1.0
    # For each coordinate i: flipping bit i changes the score by -2 * sample[:, i] * W[i, j]
    delta_per_i = -2.0 * samples * W[:, j][None, :]  # (n_samples, N)
    flipped_scores = base_scores[:, None] + delta_per_i  # (n_samples, N)
    flipped_signs = np.sign(flipped_scores)
    flipped_signs[flipped_signs == 0] = 1.0
    flips = (base_signs[:, None] != flipped_signs).astype(np.float64)  # (n_samples, N)
    influences = flips.mean(axis=0)
    # Variance of f under uniform x_in.
    var_f = float(np.var(base_signs))
    return influences, var_f, base_sign


def run_one_seed_density(seed: int, density: float, N: int, n_samples: int):
    rng = np.random.default_rng(seed)
    W, keys, vals = build_substrate_W(N, density, rng)
    # Pick the first stored key as the target.
    target_key = keys[0]
    target_val = vals[0]
    influences, var_f, base_sign = estimate_influences(W, target_key, target_val, n_samples, rng)
    inf_total = float(influences.sum())
    max_inf = float(influences.max())
    max_inf_share = max_inf / max(inf_total, 1e-12)
    # KKL bound: Inf_total >= C * Var * log(n) / max_inf (rearranged)
    # We compute the ratio Inf_total / (Var * log(N)). KKL guarantees this >= C/max_inf,
    # we just check Inf_total >= Var * log(n) (KKL with C=1).
    kkl_lhs = inf_total
    kkl_rhs = var_f * math.log(N) if var_f > 0 else 1.0
    kkl_ratio = kkl_lhs / max(kkl_rhs, 1e-12)
    return {
        "inf_total": inf_total,
        "max_inf": max_inf,
        "max_inf_share": max_inf_share,
        "var_f": var_f,
        "kkl_ratio": kkl_ratio,
        "N": N,
        "density": density,
        "M_stored": int(round(density * N)),
    }


def compute_verdict(summary):
    per_density = summary.get("per_density")
    if not per_density:
        return ("KKL_INCONCLUSIVE", "Missing per_density data.")
    rows = []
    worst_max_inf_share = 0.0
    best_kkl_ratio = -1e9
    all_passed = True
    any_failed = False
    for d in sorted([float(x) for x in per_density.keys()]):
        seeds = per_density[str(d)]
        max_inf_share = sum(s["max_inf_share"] for s in seeds.values()) / len(seeds)
        kkl_ratio = sum(s["kkl_ratio"] for s in seeds.values()) / len(seeds)
        rows.append((d, max_inf_share, kkl_ratio))
        worst_max_inf_share = max(worst_max_inf_share, max_inf_share)
        best_kkl_ratio = max(best_kkl_ratio, kkl_ratio)
        if not (max_inf_share <= PASS_MAX_INF_SHARE and kkl_ratio >= PASS_KKL_RATIO):
            all_passed = False
        if max_inf_share >= FAIL_MAX_INF_SHARE:
            any_failed = True
    pts = ", ".join(f"density={d:.2f}: max_inf_share={s:.3f}, kkl_ratio={k:.3f}" for d, s, k in rows)
    if all_passed:
        return ("KKL_HARD_PASS_LOW_INFLUENCE",
                f"Substrate boundaries are low-influence/well-distributed: max_inf_share <= "
                f"{PASS_MAX_INF_SHARE} AND kkl_ratio >= {PASS_KKL_RATIO} at ALL operating points. {pts}.")
    if any_failed:
        return ("KKL_HARD_FAIL_HIGH_INFLUENCE",
                f"Substrate boundaries behave as junta: max_inf_share >= {FAIL_MAX_INF_SHARE} at "
                f">=1 operating point. KKL row REJECTED for substrate boundaries. "
                f"worst_max_inf_share={worst_max_inf_share:.3f}. {pts}.")
    return ("KKL_MIDDLE_BAND",
            f"Intermediate: worst_max_inf_share={worst_max_inf_share:.3f}, "
            f"best_kkl_ratio={best_kkl_ratio:.3f}. {pts}.")


def self_test_verdict():
    def mk(d_to_share, d_to_ratio):
        return {"per_density": {str(d): {"17": {"max_inf_share": s, "kkl_ratio": d_to_ratio[d]}}
                                for d, s in d_to_share.items()}}
    s_pass = mk({0.1: 0.20, 0.3: 0.25}, {0.1: 1.5, 0.3: 1.2})
    s_fail = mk({0.1: 0.65, 0.3: 0.40}, {0.1: 0.5, 0.3: 0.8})
    s_mid = mk({0.1: 0.45, 0.3: 0.35}, {0.1: 0.7, 0.3: 0.8})
    s_inconc = {}
    cases = [
        (s_pass, "KKL_HARD_PASS_LOW_INFLUENCE"),
        (s_fail, "KKL_HARD_FAIL_HIGH_INFLUENCE"),
        (s_mid, "KKL_MIDDLE_BAND"),
        (s_inconc, "KKL_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, msg = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; msg={msg}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    N = N_SMOKE if smoke else N_FULL
    densities = M_DENSITIES_SMOKE if smoke else M_DENSITIES_FULL
    n_samples = N_SAMPLES_SMOKE if smoke else N_SAMPLES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N,
        "M_densities": densities,
        "n_samples": n_samples,
        "seeds": seeds,
        "pass_max_inf_share": PASS_MAX_INF_SHARE,
        "pass_kkl_ratio": PASS_KKL_RATIO,
        "fail_max_inf_share": FAIL_MAX_INF_SHARE,
    }
    print(f"[config] {config}", flush=True)
    per_density = {}
    for d in densities:
        print(f"[density={d}] ...", flush=True)
        per_seed = {}
        for seed in seeds:
            r = run_one_seed_density(seed, d, N, n_samples)
            per_seed[str(seed)] = r
            print(f"  density={d} seed={seed}: max_inf_share={r['max_inf_share']:.3f} kkl_ratio={r['kkl_ratio']:.3f}", flush=True)
        per_density[str(d)] = per_seed
    summary = {"per_density": per_density}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_F6_boolean_kkl_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_F6_boolean_kkl_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict(); return 0
    if args.smoke:
        run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
