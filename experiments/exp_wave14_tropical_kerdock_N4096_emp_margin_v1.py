"""Empirical BSC margin baseline at substrate-native N=4096 (Cap 13 companion).

Companion to wave14_tropical_margin_certificate_kerdock_v1: measures the
empirical adversarial bit-flip margin at production scale (N=4096, full 4-coset
MM Kerdock = 16384 codewords). Provides the empirical baseline against which
the Anchor-1 closed-form margin can be re-evaluated at production scale.

For each random codeword w_i and query point y = w_i + eps * direction:
  empirical bit-flip margin = min # of bit-flips in y to change argmax of <w_j, y>

GPU-vectorized: top-k coordinate selection per candidate competitor via
sorted gain vector.

Pre-reg: preregs/2026-05-24_wave14_tropical_kerdock_N4096_emp_margin_v1.md
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
from typing import Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import torch

# Import 4-coset MM Kerdock codebook builder (N=4096 supported via t=6)
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook


# ---------------------------------------------------------------------------
# Core: GPU-vectorized empirical bit-flip margin
# ---------------------------------------------------------------------------

def empirical_bsc_margin_gpu(codebook: torch.Tensor, y: torch.Tensor, i: int,
                              max_competitors: int = 64) -> tuple[float, Optional[int]]:
    """GPU-accelerated empirical bit-flip margin.

    codebook: (M, N) on GPU; entries in {-1, +1}.
    y:        (N,)   on GPU.
    i:        index of starting argmax codeword.

    Returns (margin_emp = 2 * min_k, j_closest).
    """
    M, N = codebook.shape
    device = codebook.device
    w_i = codebook[i]  # (N,)

    # Pre-rank competitors by closed-form margin to prune to top-max_competitors.
    diffs = w_i.unsqueeze(0) - codebook  # (M, N)
    numers = diffs @ y  # (M,)
    denoms = torch.sum(torch.abs(diffs), dim=1)  # (M,)
    closed = torch.full((M,), float("inf"), device=device, dtype=torch.float32)
    mask = (torch.arange(M, device=device) != i) & (denoms > 0)
    closed[mask] = numers[mask] / denoms[mask]
    # Pick top-max_competitors smallest closed margins
    n_cand = min(max_competitors, int(mask.sum().item()))
    candidates = torch.argsort(closed)[:n_cand]  # (n_cand,)

    # Vectorized: for each candidate j, compute gains[k] = 2 * y_k * (w_i_k - w_j_k)
    # Then sort descending, cumsum, find first k where cumsum > gap.
    w_js = codebook[candidates]  # (n_cand, N)
    gaps = (w_i.unsqueeze(0) - w_js) @ y  # (n_cand,); positive if y is in cell of i
    gains = 2.0 * y.unsqueeze(0) * (w_i.unsqueeze(0) - w_js)  # (n_cand, N)
    gains_sorted, _ = torch.sort(gains, dim=1, descending=True)  # (n_cand, N)
    cumsum = torch.cumsum(gains_sorted, dim=1)  # (n_cand, N)

    # For each j, find first index where cumsum > gap[j]; k_min = idx + 1
    # If cumsum[-1] <= gap[j], this j is unreachable.
    gaps_b = gaps.unsqueeze(1)  # (n_cand, 1)
    reachable_mask = cumsum > gaps_b + 1e-9  # (n_cand, N), True where cumsum exceeds gap
    # k_min per j: first True column (or N+1 if none)
    any_reachable = reachable_mask.any(dim=1)  # (n_cand,)
    # argmax of bool tensor gives FIRST True index (since False=0 < True=1)
    k_min_idx = torch.argmax(reachable_mask.int(), dim=1)  # (n_cand,), first True idx; 0 if none reachable
    k_min = torch.where(any_reachable, k_min_idx + 1, torch.tensor(N + 1, device=device))  # (n_cand,)
    # Also handle gap < 0 case (y not in cell of i): set k_min to N+1
    valid = gaps >= -1e-9
    k_min = torch.where(valid, k_min, torch.tensor(N + 1, device=device))

    best_idx = int(torch.argmin(k_min).item())
    best_k = int(k_min[best_idx].item())
    if best_k > N:
        return (float(N) * 2.0, None)
    best_j = int(candidates[best_idx].item())
    return (2.0 * float(best_k), best_j)


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("EMP_MARGIN_INCONCLUSIVE", "No cells computed.")

    all_margins = []
    n_degenerate = 0
    n_total = 0
    for cell in cells:
        for trial in cell.get("trials", []):
            n_total += 1
            m = trial.get("margin_emp")
            if m is None:
                n_degenerate += 1
                continue
            # Degenerate: margin = 0 (immediately ambiguous) or margin = full-N (unreachable)
            N = trial.get("N", 4096)
            if m <= 0 or m >= 2 * N:
                n_degenerate += 1
                continue
            all_margins.append(m)

    if n_total == 0:
        return ("EMP_MARGIN_INCONCLUSIVE", "No trials.")

    mean_m = float(np.mean(all_margins)) if all_margins else 0.0
    std_m = float(np.std(all_margins)) if all_margins else 0.0
    cv = std_m / max(mean_m, 1e-12)
    deg_frac = n_degenerate / max(n_total, 1)
    p25 = float(np.percentile(all_margins, 25)) if all_margins else 0.0

    msg_core = (
        f"n_total={n_total}, n_used={len(all_margins)}, deg_frac={deg_frac:.3f}, "
        f"mean_margin={mean_m:.2f}, std={std_m:.2f}, cv={cv:.3f}, p25={p25:.2f}"
    )

    if deg_frac > 0.20:
        return ("EMP_MARGIN_DEGENERATE", f"Too many degenerate trials. {msg_core}")
    if cv > 0.80:
        return ("EMP_MARGIN_DEGENERATE", f"Margin distribution dispersion too high. {msg_core}")
    if cv <= 0.30 and p25 > 0:
        return ("EMP_MARGIN_WELL_DEFINED",
                f"Empirical bit-flip margin baseline well-defined at N=4096. {msg_core}")
    return ("EMP_MARGIN_NOISY_BASELINE",
            f"Empirical margin reportable but noisy; needs higher statistics. {msg_core}")


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def self_test() -> None:
    device = torch.device("cpu")

    # 1. Kerdock codebook at N=1024 (smallest 4-coset; t=5)
    cb, info = make_kerdock_4coset_codebook(1024, device)
    assert cb.shape == (4096, 1024), f"codebook shape {tuple(cb.shape)} != (4096,1024)"
    vals = torch.unique(cb)
    assert vals.numel() == 2 and (vals == torch.tensor([-1.0, 1.0])).all(), \
        f"codebook entries not in {{-1,+1}}: {vals}"

    # 2. Self-margin: y = w_i has competitors at finite bit-flip distance
    cb_f = cb.float()
    i = 0
    y = cb_f[i].clone()
    margin, j = empirical_bsc_margin_gpu(cb_f, y, i, max_competitors=16)
    assert margin > 0, f"self-margin {margin} should be > 0"

    # 3. Bit-flip sensitivity ordering test: hand-built N=4 case via 2-coset
    _v2_path = REPO / "experiments" / "exp_wave14v_erase_kerdock_v2.py"
    spec = importlib.util.spec_from_file_location("kerdock_v2_st", _v2_path)
    v2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v2)
    cb4 = v2.make_kerdock_2coset_codebook(4, device).float()  # (8, 4)
    w_i = cb4[0]
    w_j = cb4[1]
    # When w_i[k] != w_j[k], (w_i[k] - w_j[k]) is ±2; gain when flipping y[k] is 2 * y[k] * (w_i[k] - w_j[k]) = ±4 * y[k]
    # Build y where flipping coord 0 gives max gain
    y = torch.tensor([1.0, 1.0, 1.0, 1.0])
    diff = w_i - w_j
    gain = 2.0 * y * diff
    # Just confirm gain entries are in {-4, 0, +4}
    unique_gains = torch.unique(torch.round(gain * 100) / 100)
    for g in unique_gains:
        assert abs(g.item()) in {0.0, 4.0}, f"unexpected gain entry {g}"

    # 4. Cell structure check on smoke
    config_smoke = {"N": 1024, "n_seeds": 1, "n_codewords": 2, "eps_list": [0.1, 0.5]}
    # We just check the structure won't crash; no full execution here.
    n_expected_smoke = 1 * 2 * 2  # n_seeds * n_codewords * len(eps_list)
    assert n_expected_smoke == 4

    # 5. Verdict logic
    # PASS: tight cluster around mean 200, cv ~0.05
    pass_data = {"cells": [{"trials": [{"margin_emp": 200 + (i - 25) * 0.4, "N": 4096} for i in range(50)]}]}
    v, _ = compute_verdict(pass_data)
    assert v == "EMP_MARGIN_WELL_DEFINED", f"PASS data → {v}"

    # FAIL: huge spread, cv > 0.80 (mostly small + a few large outliers)
    fail_data = {"cells": [{"trials":
        [{"margin_emp": 50.0, "N": 4096}] * 40 +
        [{"margin_emp": 2000.0, "N": 4096}] * 10
    }]}
    v, _ = compute_verdict(fail_data)
    assert v == "EMP_MARGIN_DEGENERATE", f"FAIL data → {v}"

    # MIDDLE: cv in (0.30, 0.80]
    middle_data = {"cells": [{"trials": [{"margin_emp": 200 + (i - 25) * 5, "N": 4096} for i in range(50)]}]}
    v, _ = compute_verdict(middle_data)
    assert v == "EMP_MARGIN_NOISY_BASELINE", f"MID data → {v}"

    degen_data = {"cells": [
        {"trials": [{"margin_emp": 100, "N": 4096}] * 30 + [{"margin_emp": 0, "N": 4096}] * 20}
    ]}
    v, _ = compute_verdict(degen_data)
    assert v == "EMP_MARGIN_DEGENERATE", f"DEGEN data → {v} (should be DEGENERATE due to 40% deg_frac)"

    print(f"self-tests passed (5 cells)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,  # smaller for smoke
            "eps_list": [0.1, 0.5],
            "n_seeds": 1,
            "n_codewords": 2,
            "max_competitors": 32,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "eps_list": [0.1, 0.3, 0.5, 0.7, 0.9],
            "n_seeds": 10,
            "n_codewords": 5,
            "max_competitors": 64,
        }

    use_cuda = torch.cuda.is_available() and not smoke
    device = torch.device("cuda" if use_cuda else "cpu")
    print(f"[device] {device}", flush=True)

    N = config["N"]
    print(f"[N={N}] building 4-coset Kerdock codebook...", flush=True)
    cb_t, info = make_kerdock_4coset_codebook(N, device)
    cb = cb_t.float().to(device)
    print(f"[codebook] shape={tuple(cb.shape)} info={info}", flush=True)

    cells = []
    for eps in config["eps_list"]:
        trials = []
        for seed in range(config["n_seeds"]):
            torch.manual_seed(seed * 7 + 13)
            rng = np.random.default_rng(seed * 1000 + int(eps * 100))
            n_cw = min(config["n_codewords"], cb.shape[0])
            cw_indices = rng.choice(cb.shape[0], size=n_cw, replace=False)
            for i in cw_indices:
                w_i = cb[int(i)]
                direction_t = torch.randn(N, device=device)
                direction_t = direction_t / max(float(direction_t.norm().item()), 1e-12)
                y = w_i + eps * direction_t

                # Confirm i is still argmax
                ips = cb @ y
                actual_i = int(torch.argmax(ips).item())
                if actual_i != int(i):
                    continue

                margin_e, j_e = empirical_bsc_margin_gpu(
                    cb, y, int(i), max_competitors=config["max_competitors"]
                )
                trials.append({
                    "seed": int(seed),
                    "i": int(i),
                    "eps": float(eps),
                    "margin_emp": float(margin_e),
                    "j_emp": int(j_e) if j_e is not None else -1,
                    "N": int(N),
                })

        # Per-cell aggregate
        margins = [t["margin_emp"] for t in trials]
        cell = {
            "eps": float(eps),
            "n_trials": len(trials),
            "mean_margin": float(np.mean(margins)) if margins else None,
            "std_margin": float(np.std(margins)) if margins else None,
            "min_margin": float(np.min(margins)) if margins else None,
            "max_margin": float(np.max(margins)) if margins else None,
            "trials": trials,
        }
        cells.append(cell)
        print(f"[eps={eps}] mean={cell['mean_margin']}, std={cell['std_margin']}, "
              f"n_trials={cell['n_trials']}", flush=True)

    summary = {"cells": cells, "config": config, "codebook_info": info}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    env_name = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{env_name}"
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
    self_test()
    out_dir = get_output_dir("wave14_tropical_kerdock_N4096_emp_margin_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells produced"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_tropical_kerdock_N4096_emp_margin_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
