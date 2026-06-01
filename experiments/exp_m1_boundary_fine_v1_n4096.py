"""M1 BOUNDARY LOCALIZATION FINE SWEEP v1: pin M_c to +/-5K at N=4096.

CONTEXT:
  Axis1 chunks 1-7 established:
    M/N=4  (M=16384): ret~1.0 (deep multi-basin / high retention)
    M/N=8  (M=32768): ret~0.503 (transition zone boundary)
    M/N=10 (M=40960): ret~0.3-0.5 (transition zone; sign_divergence in axis3 v2)
  The EXACT boundary where retention drops below 0.5 is between M/N=6 and M/N=8 per chunk3.
  The user requests a fine M-sweep at absolute M values to pin M_c to +/-5K precision.

  This anchors the product framing: "substrate can store up to M_c patterns at N=4096 Kerdock
  with > 50% retrieval accuracy."

SCIENTIFIC QUESTION:
  At N=4096 Kerdock, beta=32, where EXACTLY does retention drop from >0.7 to <0.3?
  Fine sweep: M in {40K, 50K, 60K, 70K, 80K, 90K, 100K, 110K, 120K}.
  M/N ratios: {9.77, 12.2, 14.6, 17.1, 19.5, 22.0, 24.4, 26.9, 29.3}.
  Metric: argmax retention at beta=32, 5 seeds each.
  Locate M_c: the smallest M where mean_retention < 0.50.

  Note: argmax retention is beta-invariant (confirmed by axis1 chunk5).
  Using beta=32 as standard operating point.

PRE-REGISTERED BANDS:
  HARD_PASS: Retention drops from >0.5 at M=40K to <0.5 at M<=80K, AND
    the transition is MONOTONE (ret(M_i) > ret(M_{i+1}) for all i in sweep).
    M_c = first M where mean_ret < 0.50, localized to +/-10K (adjacent M values).
  HARD_FAIL: ret > 0.5 at ALL M values in sweep (boundary above M=120K).
    Would indicate axis1 chunk estimates were inaccurate or beta=32 is anomalous.
  MIDDLE_BAND: Monotone sweep but transition too gradual to pin M_c to +/-10K
    (ret stays in [0.3, 0.7] across all sweep points without sharp crossing).

FORMULA SELF-TESTS:
  1. M/N ratio: M=40000 / N=4096 = 9.766. M=80000 / 4096 = 19.53.
  2. Expected argmax retention at M=40K N=4096: ~0.4-0.6 (from axis1 chunk5 data).
  3. Expected ret at M=120K: ~0.05-0.2 (deep over-capacity from chunk7 data).
  4. Monotone gate: all pairs (ret[i], ret[i+1]) satisfy ret[i] >= ret[i+1] - 0.05 (tolerates noise).
  5. M_c = M_vals[first index where mean_ret < 0.50].
  6. N == 4096 (PROT-018 binding).

OOM CHECK:
  Largest M = 120K. keys=120000*4096*4=1.96GB. W=64MB. CB=268MB. Total=2.3GB. Under 6GB.
  At M=80K: keys=1.31GB. Total=1.65GB. OK.

TIMEOUT ESTIMATE:
  Per-cell cost: store_facts_batched + argmax_retention.
    At M=40K N=4096: batched store ~0.7s (batch=256 -> 156 batches); retrieval ~0.1s.
    At M=120K: linear in M -> 0.7 * 3 = 2.1s store + 0.1s retrieval.
  Average per cell: ~1.5s at N=4096 (bulk of time in batched W outer products).
  Total: 9 M_vals x 5 seeds = 45 cells x 1.5s = 67.5s.
  Smoke: 3 M_vals x 2 seeds = 6 cells x 0.5s = 3s.
  Safety: ceil(1.5 * 67.5 * 3) = ceil(304s) -> 600s.
  User override for _n4096: --timeout >= 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: m1_boundary_fine_v1_n4096
Queue: overnight_queue (GPU; N=4096 Kerdock, 9 M values x 5 seeds, argmax retention)
Pre-reg: preregs/2026-05-28_m1_boundary_fine_v1_n4096.md
Parent: axis1_mb_chunk3_v1_n4096 + axis1_mb_chunk5_n4096 (established transition zone)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load chunk1 base (store_facts_batched, compute_retention, Kerdock)
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_m1", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched
compute_retention    = c1.compute_retention
v3 = c1.v3  # Kerdock codebook builder

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL = 4096       # PROT-018 binding contract
N_SMOKE = 1024      # smoke scale (Kerdock requires log2(N) even integer)
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# M fine sweep (user-specified absolute values)
M_VALS_FULL  = [40000, 50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000]
M_VALS_SMOKE = [40000, 80000, 120000]  # 3-point smoke for shape check

BETA = 32.0       # standard operating point; argmax is beta-invariant but record anyway

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

N_PROBE = 200  # number of stored facts to probe at each cell

# Pre-registered thresholds
HP_BOUNDARY_UPPER = 80000   # M_c <= 80K for HARD_PASS (transition below M/N=20)
HP_MIN_RET_LOW_M  = 0.50    # ret at M=40K must be > 0.50
HF_MIN_RET_HIGH_M = 0.50    # HARD_FAIL if ret > 0.50 even at M=120K
TRANSITION_THRESHOLD = 0.50 # boundary = first M where mean_ret < this


def get_output_dir(default_name: str = "m1_boundary_fine_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, M: int, seed: int, device: torch.device) -> Dict:
    """Store M facts, measure retention. Returns metrics dict."""
    t0 = time.monotonic()
    codebook, _info = v3.make_kerdock_4coset_codebook(N, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)
    n_probe = min(N_PROBE, M)
    ret = compute_retention(W, keys, val_idx, codebook, BETA, N, n_probe=n_probe)
    elapsed = time.monotonic() - t0
    return {
        "M": M, "M_over_N": round(M / N, 4), "N": N,
        "seed": seed, "beta": BETA,
        "retention": round(float(ret), 5),
        "elapsed_s": round(elapsed, 3),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    """Compute verdict from per-M mean retention."""
    by_M = summary.get("by_M", {})
    if not by_M:
        return ("M1_INCONCLUSIVE", "No by_M data computed.")

    m_sorted = sorted(by_M.keys())
    mean_ret_by_M = {m: by_M[m]["mean_retention"] for m in m_sorted}

    # Find M_c: first M where mean_ret < TRANSITION_THRESHOLD
    M_c = None
    for m in m_sorted:
        if mean_ret_by_M[m] < TRANSITION_THRESHOLD:
            M_c = m
            break

    # Check monotonicity (tolerance +/-0.05 for noise)
    is_monotone = all(
        mean_ret_by_M[m_sorted[i]] >= mean_ret_by_M[m_sorted[i + 1]] - 0.05
        for i in range(len(m_sorted) - 1)
    )

    detail = {
        "M_c": M_c, "is_monotone": is_monotone,
        "mean_ret_by_M": {m: round(v, 4) for m, v in mean_ret_by_M.items()},
    }

    # HARD_FAIL: boundary above sweep range (all M values show high retention)
    if mean_ret_by_M.get(m_sorted[-1], 0.0) > HF_MIN_RET_HIGH_M:
        return ("M1_HARD_FAIL",
                f"BOUNDARY_NOT_FOUND: ret at M={m_sorted[-1]} = "
                f"{mean_ret_by_M[m_sorted[-1]]:.3f} > {HF_MIN_RET_HIGH_M}. "
                f"Phase boundary above sweep range. details={detail}.")

    # HARD_PASS: clear monotone boundary within sweep range
    if (M_c is not None and M_c <= HP_BOUNDARY_UPPER and
            mean_ret_by_M.get(m_sorted[0], 0.0) > HP_MIN_RET_LOW_M and
            is_monotone):
        M_c_idx = m_sorted.index(M_c)
        M_c_minus = m_sorted[M_c_idx - 1] if M_c_idx > 0 else None
        return ("M1_HARD_PASS",
                f"BOUNDARY_PINNED: M_c={M_c} (first M where mean_ret < {TRANSITION_THRESHOLD}). "
                f"M_c bracketed by [{M_c_minus}, {M_c}] (+/-{(M_c - (M_c_minus or M_c))//2 + 5000} resolution). "
                f"Monotone={is_monotone}. details={detail}.")

    # MIDDLE_BAND: boundary found but gradual or outside HP range
    return ("M1_MIDDLE_BAND",
            f"GRADUAL_TRANSITION: M_c={M_c} monotone={is_monotone}. "
            f"Boundary found but may not meet precision target (+/-5K). details={detail}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: HARD_PASS verdict path
    # Monotone decreasing, boundary at M=80K
    by_M = {
        40000: {"mean_retention": 0.72},
        50000: {"mean_retention": 0.60},
        60000: {"mean_retention": 0.52},
        70000: {"mean_retention": 0.45},  # -> boundary here
        80000: {"mean_retention": 0.30},
    }
    summary = {"by_M": by_M}
    v, msg = compute_verdict(summary)
    assert "HARD_PASS" in v, f"selftest HARD_PASS failed: v={v} msg={msg}"
    assert "70000" in msg or "M_c=70000" in msg, f"M_c not correctly identified: {msg}"

    # Self-test 2: HARD_FAIL (all high)
    by_M_hf = {m: {"mean_retention": 0.80} for m in M_VALS_FULL}
    v2, msg2 = compute_verdict({"by_M": by_M_hf})
    assert "HARD_FAIL" in v2, f"selftest HARD_FAIL failed: {v2}"

    # Self-test 3: MIDDLE_BAND (boundary above 80K)
    by_M_mid = {
        40000: {"mean_retention": 0.65},
        80000: {"mean_retention": 0.52},
        120000: {"mean_retention": 0.40},   # boundary at 120K, above HP_BOUNDARY_UPPER
    }
    v3, _ = compute_verdict({"by_M": by_M_mid})
    assert "MIDDLE_BAND" in v3 or "HARD_PASS" in v3, f"selftest MIDDLE_BAND failed: {v3}"

    # Self-test 4: formula check M/N ratios
    for M in M_VALS_FULL:
        ratio = M / N_FULL
        assert 8.0 < ratio < 32.0, f"M/N ratio out of expected range: M={M} ratio={ratio:.2f}"

    # Self-test 5: actual smoke computation at N_SMOKE
    device = torch.device("cpu")
    N_t = N_SMOKE
    # Adjust M values for smoke scale (smoke uses N=1024, so M/N ratios shift)
    # Use same absolute M to be honest about scale
    M_smoke = M_VALS_SMOKE[0]  # 40000
    cell = run_one_cell(N_t, M_smoke, 17, device)
    assert "retention" in cell, f"retention missing from cell: {cell}"
    assert 0.0 <= cell["retention"] <= 1.0, f"retention out of range: {cell['retention']}"
    assert not math.isnan(cell["retention"]), f"retention is NaN: {cell}"
    print(f"[selftest] N={N_t} M={M_smoke}: retention={cell['retention']:.4f} "
          f"elapsed={cell['elapsed_s']:.2f}s OK", flush=True)

    # Multi-scale: test at M_VALS_SMOKE[1] (=80000) to verify no OOM pattern at intermediate M
    cell2 = run_one_cell(N_t, M_VALS_SMOKE[1], 17, device)
    assert 0.0 <= cell2["retention"] <= 1.0, f"M=80K smoke: retention out of range: {cell2}"
    print(f"[selftest] multi-scale M={M_VALS_SMOKE[1]}: ret={cell2['retention']:.4f} OK", flush=True)

    print("[selftest] PASS: all assertions OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N     = N_SMOKE if smoke else N_FULL
    m_vals = M_VALS_SMOKE if smoke else M_VALS_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    exp_name = os.environ.get("HDLAB_EXP_NAME", "m1_boundary_fine_v1_n4096")
    print(f"[run] {exp_name} smoke={smoke} N={N} seeds={seeds} "
          f"M_vals={m_vals} device={device}", flush=True)
    if not smoke:
        assert N == 4096, f"FULL run must use N=4096 (PROT-018); got {N}"

    all_cells: List[Dict] = []

    for M in m_vals:
        print(f"  [M={M} M/N={M/N:.2f}]", flush=True)
        for seed in seeds:
            cell = run_one_cell(N, M, seed, device)
            all_cells.append(cell)
            print(f"    seed={seed} ret={cell['retention']:.4f} "
                  f"({cell['elapsed_s']:.1f}s)", flush=True)

    # Aggregate by M
    by_M: Dict = {}
    for cell in all_cells:
        m = cell["M"]
        if m not in by_M:
            by_M[m] = {"retentions": [], "M_over_N": cell["M_over_N"]}
        by_M[m]["retentions"].append(cell["retention"])
    for m in by_M:
        rets = by_M[m]["retentions"]
        by_M[m]["mean_retention"] = round(float(sum(rets) / len(rets)), 5)
        by_M[m]["std_retention"]  = round(float(
            (sum((r - by_M[m]["mean_retention"])**2 for r in rets) / max(1, len(rets))) ** 0.5
        ), 5)
        by_M[m]["n_seeds"] = len(rets)

    summary = {"by_M": by_M, "N": N, "beta": BETA, "seeds": seeds}
    verdict_str, verdict_msg = compute_verdict(summary)

    elapsed = time.time() - t0
    print(f"\n[verdict] {verdict_str}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)

    out_dir = get_output_dir(exp_name)
    metrics = {
        "verdict": verdict_str,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N, "smoke": smoke, "seeds": seeds, "M_vals": m_vals, "beta": BETA},
        "summary": summary,
        "all_cells": all_cells,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import scope", flush=True)
        sys.exit(0)
    run(smoke=args.smoke)
else:
    run(smoke=False)
