"""Direct R-transform multi-N scaling probe of substrate Kerdock spectrum.

Motivation
----------
v164 cap_map (BATCHED): wave14_free_cumulants_kerdock_v1 GPU FULL =
FREE_CUMULANTS_DIVERGE confirmed the substrate Kerdock spectrum has nontrivial
higher free cumulants kappa_n (n>=2) at N=1024 (5/5 cells exceed 20%
deviation, max_dev=1.125 at kappa_4 alpha=2.00). The v164 row sits at
EVIDENCE-STRENGTH 🟢 single-N.

This experiment promotes the row from 🟢 to ✅ (or refutes) by directly
measuring whether the deviations are:
  (a) finite-N artifacts that shrink as N -> infinity (would refute the
      "substrate-novel observability" framing -- if kappa_n / c -> 1 in the
      thermodynamic limit, the divergence is a finite-N transient, not a
      substrate property)
  (b) STABLE in N (the dimension-independent free-cumulant signature is
      genuine; the "outside AMP universality" claim is anchored to a
      finite limit, not a finite-N artifact)
  (c) GROWING in N (the substrate's structure becomes MORE distinct from MP
      at larger N -- substrate-novel scaling regime)

Scientific question
-------------------
Does max |kappa_n / c - 1| (over n in {2,3,4}) STAY > 0.20 across N in
{1024, 2048, 4096, 8192} for the same alpha = M/N? If yes, the substrate's
R-transform deviation is dimension-stable and the v164 free-cumulant
fingerprint row promotes from 🟢 to ✅.

Companion: also supplies the spectral input (kappa_n profile per alpha) for
the deferred VAMP-SE-on-Kerdock follow-up (v163 + v164a composition; the
Onsager-correction coefficients in the exact VAMP-SE recursion ARE the free
cumulants of the noise spectrum).

Vertex
------
R_TRANSFORM_STABLE_IN_N : max_dev > 0.20 for all N, AND |max_dev(N_max) -
  max_dev(N_min)| < 0.20 (DIM-STABLE; promotes v164 row 🟢 -> ✅)
R_TRANSFORM_SHRINKS_IN_N : max_dev decreases with N AND max_dev(N_max) < 0.20
  (finite-N artifact; v164 row stays 🟢 with caveat; refute the substrate-
  novel framing at the thermodynamic limit)
R_TRANSFORM_GROWS_IN_N : max_dev increases with N by > 0.20 between extreme
  Ns (substrate-novel scaling regime; v164 row promotes to ✅ with growth
  annotation)
R_TRANSFORM_INCONCLUSIVE : mixed / insufficient N range

Pre-reg: preregs/2026-05-23_wave14_R_transform_kerdock_v1_multi_N.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Reuse the v1 module's helpers (kappa math + Kerdock spectrum extraction)
_v1_path = REPO / "experiments" / "exp_wave14_free_cumulants_kerdock_v1.py"
_spec = importlib.util.spec_from_file_location("free_cumulants_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v1)
moments_to_free_cumulants = _v1.moments_to_free_cumulants
mp_reference_cumulants = _v1.mp_reference_cumulants
mp_reference_moments = _v1.mp_reference_moments
get_kerdock_spectrum = _v1.get_kerdock_spectrum
spectral_moments = _v1.spectral_moments


# ---------------------------------------------------------------------------
# Verdict logic (multi-N scaling)
# ---------------------------------------------------------------------------

def compute_verdict_multi_N(summary: dict) -> tuple[str, str]:
    """Determine N-scaling verdict.

    Per (alpha, N) cell we have max_dev = max_{n in {2,3,4}} |kappa_n / c - 1|.
    Then for each alpha we examine how max_dev scales with N.
    """
    if not summary.get("cells"):
        return ("R_TRANSFORM_INCONCLUSIVE", "No cells computed.")

    # Group by alpha; for each alpha collect (N, max_dev)
    by_alpha: dict[float, list[tuple[int, float]]] = {}
    for cell in summary["cells"]:
        alpha = cell.get("alpha")
        N = cell.get("N")
        kappas = cell.get("kappa_mean", [])
        c_ref = alpha
        if alpha is None or N is None or c_ref is None or c_ref <= 0 or not kappas:
            continue
        worst_dev = 0.0
        worst_n = 0
        for n_idx in range(1, len(kappas)):
            n = n_idx + 1
            dev = abs(kappas[n_idx] / c_ref - 1.0)
            if dev > worst_dev:
                worst_dev = dev
                worst_n = n
        cell["worst_kappa_dev"] = worst_dev
        cell["worst_kappa_n"] = worst_n
        by_alpha.setdefault(float(alpha), []).append((int(N), float(worst_dev)))

    if not by_alpha:
        return ("R_TRANSFORM_INCONCLUSIVE", "No valid alpha-N cells.")

    # Per alpha: sort by N, look at max_dev trajectory
    DIVERGE_THRESHOLD = 0.20
    GROWTH_THRESHOLD = 0.20

    alpha_classifications: dict[float, str] = {}
    summary_lines: list[str] = []
    for alpha, pts in by_alpha.items():
        pts_sorted = sorted(pts, key=lambda x: x[0])
        if len(pts_sorted) < 2:
            alpha_classifications[alpha] = "single-N"
            continue
        N_min, dev_min = pts_sorted[0]
        N_max, dev_max = pts_sorted[-1]
        deltas = [dev for _, dev in pts_sorted]
        all_above_threshold = all(d > DIVERGE_THRESHOLD for d in deltas)
        all_below_threshold = all(d < DIVERGE_THRESHOLD for d in deltas)
        span = max(deltas) - min(deltas)

        if all_above_threshold and span < GROWTH_THRESHOLD:
            cls = "STABLE_DIVERGE"
        elif all_below_threshold:
            cls = "STABLE_MATCH"
        elif dev_max - dev_min > GROWTH_THRESHOLD:
            cls = "GROWS_IN_N"
        elif dev_min - dev_max > GROWTH_THRESHOLD:
            cls = "SHRINKS_IN_N"
        elif all_above_threshold:
            cls = "ABOVE_THRESHOLD_NONMONOTONIC"
        else:
            cls = "MIXED"
        alpha_classifications[alpha] = cls
        summary_lines.append(
            f"alpha={alpha:.2f}: N range [{N_min}, {N_max}] "
            f"dev range [{min(deltas):.3f}, {max(deltas):.3f}] -> {cls}"
        )

    # Aggregate verdict
    classifications = list(alpha_classifications.values())
    n_alpha = len(classifications)
    if n_alpha == 0:
        return ("R_TRANSFORM_INCONCLUSIVE", "No alpha cells with multi-N data.")

    n_stable_diverge = classifications.count("STABLE_DIVERGE")
    n_above_thresh = classifications.count("ABOVE_THRESHOLD_NONMONOTONIC") + n_stable_diverge
    n_grows = classifications.count("GROWS_IN_N")
    n_shrinks = classifications.count("SHRINKS_IN_N")
    n_match = classifications.count("STABLE_MATCH")

    detail = "; ".join(summary_lines)

    if n_grows >= max(1, n_alpha // 2):
        return (
            "R_TRANSFORM_GROWS_IN_N",
            f"Kerdock R-transform deviation from MP GROWS with N. "
            f"{n_grows}/{n_alpha} alpha cells show growth > {GROWTH_THRESHOLD:.2f} "
            f"between N range. Substrate-novel scaling regime confirmed: "
            f"v164 free-cumulant fingerprint row promotes 🟢 -> ✅ with "
            f"growth annotation. Details: {detail}",
        )

    if (n_stable_diverge + n_above_thresh) >= max(1, n_alpha // 2) and n_shrinks == 0:
        return (
            "R_TRANSFORM_STABLE_IN_N",
            f"Kerdock R-transform deviation from MP STAYS > 0.20 across N range "
            f"and does NOT shrink. {n_stable_diverge}/{n_alpha} alpha cells "
            f"stable+diverge, {n_above_thresh}/{n_alpha} above threshold. "
            f"Substrate-novel observability dimension-stable: v164 free-cumulant "
            f"fingerprint row promotes 🟢 -> ✅. Details: {detail}",
        )

    if n_shrinks >= max(1, n_alpha // 2):
        return (
            "R_TRANSFORM_SHRINKS_IN_N",
            f"Kerdock R-transform deviation from MP SHRINKS with N. "
            f"{n_shrinks}/{n_alpha} alpha cells shrink by > {GROWTH_THRESHOLD:.2f}. "
            f"Finite-N artifact suspected; v164 free-cumulant row stays 🟢 with "
            f"thermodynamic-limit caveat (consider WHETHER divergence persists in "
            f"large-N limit). Details: {detail}",
        )

    if n_match >= max(1, n_alpha // 2):
        return (
            "R_TRANSFORM_SHRINKS_IN_N",
            f"Kerdock spectrum is MP-LIKE in {n_match}/{n_alpha} alpha cells "
            f"across N range (max_dev < 0.20 in all N). Refutes the v164 single-N "
            f"FREE_CUMULANTS_DIVERGE: was a small-N artifact at N=1024. "
            f"Substrate's R-transform converges to MP at larger N. Details: {detail}",
        )

    return (
        "R_TRANSFORM_INCONCLUSIVE",
        f"Mixed N-scaling: stable_diverge={n_stable_diverge}, grows={n_grows}, "
        f"shrinks={n_shrinks}, match={n_match} over {n_alpha} alpha cells. "
        f"Need wider N range or more seeds. Details: {detail}",
    )


def self_test_verdict() -> None:
    """Verify the multi-N verdict classifier."""

    # Test 1: STABLE_DIVERGE - all cells above threshold, low span per alpha
    # span = 0.5 - 0.4 = 0.1 < GROWTH_THRESHOLD=0.20, all above 0.2 -> STABLE_DIVERGE
    summary = {
        "cells": [
            {"alpha": 0.5, "N": 1024, "kappa_mean": [0.5, 0.5, 0.5, 0.70]},  # dev 0.4
            {"alpha": 0.5, "N": 2048, "kappa_mean": [0.5, 0.5, 0.5, 0.72]},  # dev 0.44
            {"alpha": 0.5, "N": 4096, "kappa_mean": [0.5, 0.5, 0.5, 0.75]},  # dev 0.5
        ]
    }
    v, _ = compute_verdict_multi_N(summary)
    assert v == "R_TRANSFORM_STABLE_IN_N", f"expected STABLE got {v}"

    # Test 2: GROWS - clear growth across N
    summary = {
        "cells": [
            {"alpha": 0.5, "N": 1024, "kappa_mean": [0.5, 0.5, 0.5, 0.55]},  # dev 0.1
            {"alpha": 0.5, "N": 2048, "kappa_mean": [0.5, 0.5, 0.5, 0.7]},   # dev 0.4
            {"alpha": 0.5, "N": 4096, "kappa_mean": [0.5, 0.5, 0.5, 0.9]},   # dev 0.8
        ]
    }
    v, _ = compute_verdict_multi_N(summary)
    # dev_max - dev_min = 0.8 - 0.1 = 0.7 > 0.2 GROWS
    assert v == "R_TRANSFORM_GROWS_IN_N", f"expected GROWS got {v}"

    # Test 3: SHRINKS - clear shrinkage
    summary = {
        "cells": [
            {"alpha": 0.5, "N": 1024, "kappa_mean": [0.5, 0.5, 0.5, 0.9]},   # dev 0.8
            {"alpha": 0.5, "N": 2048, "kappa_mean": [0.5, 0.5, 0.5, 0.7]},   # dev 0.4
            {"alpha": 0.5, "N": 4096, "kappa_mean": [0.5, 0.5, 0.5, 0.55]},  # dev 0.1
        ]
    }
    v, _ = compute_verdict_multi_N(summary)
    # dev_min - dev_max = 0.8 - 0.1 = 0.7 > 0.2 SHRINKS
    assert v == "R_TRANSFORM_SHRINKS_IN_N", f"expected SHRINKS got {v}"

    # Test 4: empty
    v, _ = compute_verdict_multi_N({"cells": []})
    assert v == "R_TRANSFORM_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}"

    print("verdict self-test passed (4/4 cases)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    # Kerdock 4-coset codebook requires N = 2^k for even k AND t=k/2 in
    # PRIMITIVE_POLY registry. Currently registered: t=5 (N=1024) and t=6
    # (N=4096). Extending the registry to t=7,8 would unlock N=16384, N=65536
    # but is left for a future patch.
    if smoke:
        config = {
            "mode": "smoke",
            "N_list": [1024],
            "M_over_N_list": [0.5, 1.0],
            "n_seeds": 2,
            "n_max_moment": 4,
        }
    else:
        config = {
            "mode": "full",
            "N_list": [1024, 4096],
            "M_over_N_list": [0.5, 1.0, 2.0],
            "n_seeds": 5,
            "n_max_moment": 4,
        }

    n_max = config["n_max_moment"]
    cells = []
    for alpha in config["M_over_N_list"]:
        for N in config["N_list"]:
            M = max(1, int(alpha * N))
            if M > 4 * N:
                print(f"[skip] alpha={alpha:.2f} N={N}: M={M} > 4N={4*N}", flush=True)
                continue

            c_ref = float(alpha)

            print(f"\n[alpha={alpha:.2f}, N={N}] M={M} c_ref={c_ref:.4f}", flush=True)

            kappa_per_seed = []
            moms_per_seed = []
            for seed in range(config["n_seeds"]):
                seed_val = seed * 10000 + int(alpha * 100) * 100 + (N // 256)
                eigenvalues, _A_norm = get_kerdock_spectrum(N, M, seed=seed_val)
                moms = spectral_moments(eigenvalues, n_max)
                kappas = moments_to_free_cumulants(moms)
                kappa_per_seed.append(kappas)
                moms_per_seed.append(moms)
                print(
                    f"  seed={seed} moms={[f'{m:.4f}' for m in moms]} "
                    f"kappas={[f'{k:.4f}' for k in kappas]}",
                    flush=True,
                )

            kappa_arr = np.array(kappa_per_seed)
            kappa_mean = kappa_arr.mean(axis=0).tolist()
            kappa_std = kappa_arr.std(axis=0).tolist()
            moms_arr = np.array(moms_per_seed)
            moms_mean = moms_arr.mean(axis=0).tolist()

            kappa_mp = mp_reference_cumulants(c_ref, n_max)
            moms_mp = mp_reference_moments(c_ref, n_max)

            dev_per_n = [
                (kappa_mean[i] / c_ref - 1.0) if c_ref > 0 else 0.0
                for i in range(n_max)
            ]

            cell = {
                "alpha": float(alpha),
                "N": int(N),
                "M": int(M),
                "c_ref": c_ref,
                "kappa_mean": kappa_mean,
                "kappa_std": kappa_std,
                "kappa_mp": kappa_mp,
                "moments_mean": moms_mean,
                "moments_mp": moms_mp,
                "kappa_dev_relative": dev_per_n,
            }
            cells.append(cell)

            print(
                f"  AGGREGATE alpha={alpha:.2f} N={N}: "
                f"kappa_mean={[f'{k:.4f}' for k in kappa_mean]} "
                f"vs MP c={c_ref:.4f}; dev_rel={[f'{d:+.3f}' for d in dev_per_n]}",
                flush=True,
            )

    summary = {"cells": cells, "config": config}
    verdict, msg = compute_verdict_multi_N(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if not d.get("verdict"):
        raise ValueError("empty verdict")


def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test_verdict()
    out_dir = get_output_dir("wave14_R_transform_kerdock_v1_multi_N_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells produced"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test_verdict()
    out_dir = get_output_dir("wave14_R_transform_kerdock_v1_multi_N")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
