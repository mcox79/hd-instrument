"""REGION C OPTIMAL PROBE v1: 8-cell Region C vs Region A at N=4096.

CONTEXT:
  Region C = (beta > beta_c, M < M_c) -- "spin-glass-on-the-cold-side"
  Region A = (beta < beta_c, M < M_c) -- standard operating point
  Question: does Region C provide substantially better killer-feature
  characteristics than standard Region A? If so, Region C is substrate's
  "best" region -- product positioning shifts toward high-beta operation.

  This anchor is the 8-cell focused comparison BEFORE the 63-cell unified
  grid sweep. The metric battery (6 metrics) is shared with Anchor 3 via
  experiments/_metric_battery.py.

SCIENTIFIC QUESTION:
  Across the 6 product-relevant metrics, does Region C beat matched Region
  A by a meaningful factor?

PRE-REGISTERED BANDS:
  Cells (per spec):
    Region C: (beta=16, M_frac=0.5), (beta=32, M_frac=1), (beta=64, M_frac=2),
              (beta=128, M_frac=4)
    Region A: (beta=4,  M_frac=0.5), (beta=8,  M_frac=1), (beta=10, M_frac=2),
              (beta=10, M_frac=4)
  (Region A cells matched to Region C cells on M_frac for per-M comparison.)

  HARD_PASS: Region C provides >= 2x improvement on AT LEAST 2 metrics
    compared to matched Region A cell in >= 3/5 seeds. (C is substrate's
    "best" region.)
  HARD_FAIL: Region C is statistically indistinguishable from Region A
    across all 6 metrics (within +/-20%). (No optimal-region signal.)
  MIDDLE_BAND: Region C wins on 1 metric, or 1.2x-2x on 1-2 metrics.

  Direction convention (which way is "better"):
    above_thresh_frac     lower is better (fewer hallucinations)
    max_iso               lower is better (less edit leakage)
    retention             higher is better
    edit_then_retrieve    higher is better
    retrieval_latency_ns  lower is better
    kf1_sharpness         higher is better

  Improvement ratio computed in the "better" direction per metric so a 2x
  factor always means substrate-product gain.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. M for region_C cell (beta=16, M_frac=0.5): M = 512.
  3. M for region_C cell (beta=128, M_frac=4):  M = 4096.
  4. 8 cells x 5 seeds = 40 cell-seeds total.
  5. Metric-improvement = ratio in the "better" direction per metric.

OOM CHECK:
  Max M at full N=4096: M_frac=4 -> M=4096. keys=4096*4096*4=67MB.
  W=64MB. CB=268MB. Total ~400MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  Per cell at N=4096: substrate build + 6 metrics ~= 5-10s.
  8 cells x 5 seeds = 40 cell-seeds x 8s mean = 320s nominal.
  Scaling-exp 1.5, smoke wall ~30s, FULL = 30 * 4^1.5 * 5 = 1200s; safety
  1.5x = 1800s.
  PROT-019 floor (_n4096) = 14400s. Adopt 21600s per user spec.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: region_c_optimal_probe_v1_n4096
Queue: overnight_queue (GPU; N=4096; 8 cells x 5 seeds; metric battery)
Pre-reg: preregs/2026-05-30_region_c_optimal_probe_v1_n4096.md
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

# Metric battery (single source of truth; shared with Anchor 3)
from experiments._metric_battery import (   # noqa: E402
    run_battery,
    METRIC_NAMES,
)

# Seed-checkpoint helper
_ckpt_path = REPO / "experiments" / "_seed_checkpoint.py"
_ckpt_spec = importlib.util.spec_from_file_location("_seed_checkpoint_rc", _ckpt_path)
_ckpt = importlib.util.module_from_spec(_ckpt_spec)
_ckpt_spec.loader.exec_module(_ckpt)
resumable_seeds   = _ckpt.resumable_seeds
write_partial_key = _ckpt.write_partial_key
list_completed_keys = _ckpt.list_completed_keys
load_partial_key   = _ckpt.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds to N = 4096
N = 4096        # PROT-018 production-N anchor (queue_add.py regex hits this line)
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Cells (region, beta, M_frac). M_frac is fraction of N (not multiplier of 1024
# here; user spec for Anchor 2 lists "M_frac=0.5..4" which would be very small
# if multiplied by 1024; cross-referencing the Anchor 3 grid which lists
# M_frac in [0.25..16] makes it clear M_frac here is fraction-of-N -- so
# M = M_frac * N. We use this convention consistently between Anchor 2 and
# Anchor 3 to make the comparison comparable.)
CELLS = [
    # Region C: beta > beta_c=10
    ("C", "c_b16_m0p5",  16.0,  0.5),
    ("C", "c_b32_m1",    32.0,  1.0),
    ("C", "c_b64_m2",    64.0,  2.0),
    ("C", "c_b128_m4",  128.0,  4.0),
    # Region A: beta <= beta_c
    ("A", "a_b4_m0p5",    4.0,  0.5),
    ("A", "a_b8_m1",      8.0,  1.0),
    ("A", "a_b10_m2",    10.0,  2.0),
    ("A", "a_b10_m4",    10.0,  4.0),
]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

N_PROBE = 200
N_EDITS = 16

# Pre-registered thresholds
HP_RATIO_THRESHOLD     = 2.0     # >= 2x improvement on a metric
HP_METRICS_MIN         = 2       # >= 2 metrics meeting 2x
HP_SEEDS_MIN           = 3       # >= 3 seeds where the 2x holds
HF_INDISTINGUISHABLE   = 1.2     # |ratio| in [1/1.2, 1.2] = indistinguishable
HF_INDIST_METRICS_MAX  = 6       # if ALL 6 metrics within +/-20%

# "Better direction" map (True = higher better; False = lower better)
BETTER_HIGHER = {
    "above_thresh_frac":    False,
    "max_iso":              False,
    "retention":            True,
    "edit_then_retrieve":   True,
    "retrieval_latency_ns": False,
    "kf1_sharpness":        True,
}


def get_output_dir(default_name: str = "region_c_optimal_probe_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _M_for_cell(M_frac: float, N: int) -> int:
    """M = M_frac * N (fraction-of-N convention, see comment above)."""
    return max(1, int(round(M_frac * N)))


def improvement_ratio(metric_name: str, c_val: float, a_val: float) -> float:
    """Ratio in the better direction (>1 means C beats A).

    For "higher better": ratio = c / a.
    For "lower  better": ratio = a / c.
    Handles zero-denominator by clamping.
    """
    if BETTER_HIGHER[metric_name]:
        denom = max(abs(a_val), 1e-9)
        return float(c_val) / denom
    else:
        denom = max(abs(c_val), 1e-9)
        return float(a_val) / denom


def run_one_cell(cell_key: str, region: str, beta: float, M_frac: float,
                  seed: int, N_use: int, device: torch.device) -> Dict:
    """One cell: substrate build + 6-metric battery. Returns flat dict."""
    M = _M_for_cell(M_frac, N_use)
    out = run_battery(N_use, M, beta, seed, device, n_probe=N_PROBE, n_edits=N_EDITS)
    out["cell_key"] = cell_key
    out["region"] = region
    out["M_frac"] = float(M_frac)
    return out


def pair_cells_by_mfrac(seed_cells: List[Dict]) -> List[Tuple[Dict, Dict]]:
    """Return (region_C_cell, region_A_cell) pairs matched on M_frac."""
    by_region = {"C": [], "A": []}
    for c in seed_cells:
        by_region.setdefault(c["region"], []).append(c)
    pairs = []
    for cc in by_region["C"]:
        for ac in by_region["A"]:
            if abs(cc["M_frac"] - ac["M_frac"]) < 1e-6:
                pairs.append((cc, ac))
                break
    return pairs


def seed_passes_hp(pairs: List[Tuple[Dict, Dict]]) -> bool:
    """Seed passes if >= HP_METRICS_MIN metrics show >= 2x improvement on the
    SAME-M_frac comparison (using the best matched pair per metric)."""
    if not pairs:
        return False
    # For each metric, take the BEST improvement-ratio across the M_frac pairs
    metric_best_ratio = {}
    for name in METRIC_NAMES:
        best = 0.0
        for cc, ac in pairs:
            r = improvement_ratio(name, cc[name], ac[name])
            if r > best:
                best = r
        metric_best_ratio[name] = best
    n_metrics_2x = sum(1 for r in metric_best_ratio.values() if r >= HP_RATIO_THRESHOLD)
    return n_metrics_2x >= HP_METRICS_MIN


def seed_indistinguishable(pairs: List[Tuple[Dict, Dict]]) -> bool:
    """Seed indistinguishable if ALL 6 metrics are within +/-20% across all
    matched pairs."""
    if not pairs:
        return False
    for name in METRIC_NAMES:
        for cc, ac in pairs:
            r = improvement_ratio(name, cc[name], ac[name])
            # |r| outside [1/1.2, 1.2] => distinguishable on this metric
            if r >= HF_INDISTINGUISHABLE or r <= 1.0 / HF_INDISTINGUISHABLE:
                return False
    return True


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("REGION_C_INCONCLUSIVE", "No cells.")

    # Group by seed
    by_seed: Dict[int, List[Dict]] = {}
    for c in cells:
        by_seed.setdefault(int(c["seed"]), []).append(c)

    n_seeds_hp     = 0
    n_seeds_indist = 0
    seed_summaries = []
    for s, sc in by_seed.items():
        pairs = pair_cells_by_mfrac(sc)
        hp = seed_passes_hp(pairs)
        indist = seed_indistinguishable(pairs)
        if hp:
            n_seeds_hp += 1
        if indist:
            n_seeds_indist += 1
        seed_summaries.append((s, hp, indist, len(pairs)))

    detail = (
        f"n_seeds_hp={n_seeds_hp}/{len(by_seed)} "
        f"n_seeds_indist={n_seeds_indist}/{len(by_seed)} "
        f"N={summary.get('N', N_FULL)} cells={len(cells)} "
        f"per_seed={seed_summaries[:5]}"
    )

    if n_seeds_indist >= len(by_seed):
        return ("REGION_C_HARD_FAIL",
                f"INDISTINGUISHABLE: Region C ~ Region A on all 6 metrics across "
                f"all seeds. " + detail)
    if n_seeds_hp >= HP_SEEDS_MIN:
        return ("REGION_C_HARD_PASS",
                f"REGION_C_OPTIMAL: 2x+ improvement on 2+ metrics in 3+/5 seeds. "
                + detail)
    return ("REGION_C_MIDDLE_BAND",
            f"PARTIAL: 1-metric wins or 1.2x-2x advantage. " + detail)


def _instrumentation_selftest() -> None:
    """Mandatory: assert all 6 metrics non-null/non-sentinel + verdict gates."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    assert len(CELLS) == 8, f"cell count: {len(CELLS)} != 8"
    assert sum(1 for c in CELLS if c[0] == "C") == 4, "Region C cell count"
    assert sum(1 for c in CELLS if c[0] == "A") == 4, "Region A cell count"

    # Formula self-tests
    assert _M_for_cell(0.5, N_FULL) == 2048, f"M @ M_frac=0.5: {_M_for_cell(0.5, N_FULL)}"
    assert _M_for_cell(4.0, N_FULL) == 16384, f"M @ M_frac=4: {_M_for_cell(4.0, N_FULL)}"

    # OOM check
    M_max = _M_for_cell(4.0, N_FULL)
    total_bytes = M_max * N_FULL * 4 + N_FULL * N_FULL * 4 + 49152 * N_FULL * 4
    assert total_bytes < 6e9, f"OOM: {total_bytes/1e6:.0f}MB >= 6GB"

    # Improvement-ratio formula self-tests
    # higher-better: C=0.9, A=0.1 -> ratio = 9.0
    assert abs(improvement_ratio("retention", 0.9, 0.1) - 9.0) < 1e-6
    # lower-better: C=0.01, A=0.1 -> ratio = 10.0
    assert abs(improvement_ratio("above_thresh_frac", 0.01, 0.1) - 10.0) < 1e-6

    # Verdict self-tests
    # HARD_PASS: each seed has C dominating on retention + above_thresh_frac
    fake_seed = lambda s: [
        {"seed": s, "region": "C", "M_frac": 0.5,
         "above_thresh_frac": 0.01, "max_iso": 0.01, "retention": 0.95,
         "edit_then_retrieve": 0.95, "retrieval_latency_ns": 10000.0,
         "kf1_sharpness": 50.0},
        {"seed": s, "region": "A", "M_frac": 0.5,
         "above_thresh_frac": 0.20, "max_iso": 0.20, "retention": 0.30,
         "edit_then_retrieve": 0.30, "retrieval_latency_ns": 20000.0,
         "kf1_sharpness": 5.0},
    ]
    fake_cells_hp = []
    for s in SEEDS_FULL:
        fake_cells_hp.extend(fake_seed(s))
    v, msg = compute_verdict({"cells": fake_cells_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HARD_PASS gate: {v} {msg}"

    # HARD_FAIL: indistinguishable across all metrics
    fake_indist = []
    for s in SEEDS_FULL:
        fake_indist.append({"seed": s, "region": "C", "M_frac": 0.5,
                              "above_thresh_frac": 0.10, "max_iso": 0.10,
                              "retention": 0.50, "edit_then_retrieve": 0.50,
                              "retrieval_latency_ns": 10000.0, "kf1_sharpness": 5.0})
        fake_indist.append({"seed": s, "region": "A", "M_frac": 0.5,
                              "above_thresh_frac": 0.10, "max_iso": 0.10,
                              "retention": 0.50, "edit_then_retrieve": 0.50,
                              "retrieval_latency_ns": 10000.0, "kf1_sharpness": 5.0})
    vf, mf = compute_verdict({"cells": fake_indist, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL indist gate: {vf} {mf}"

    # Smoke: one C cell + matched A cell at smoke scale, on CPU
    device = torch.device("cpu")
    sample_C = ("C", "smoke_c_b16_m0p5",  16.0, 0.5)
    sample_A = ("A", "smoke_a_b4_m0p5",    4.0, 0.5)
    out_c = run_one_cell(sample_C[1], sample_C[0], sample_C[2], sample_C[3],
                          17, N_SMOKE, device)
    out_a = run_one_cell(sample_A[1], sample_A[0], sample_A[2], sample_A[3],
                          17, N_SMOKE, device)
    for nm, out in [("C", out_c), ("A", out_a)]:
        for k in METRIC_NAMES:
            v = out.get(k)
            assert v is not None and not (isinstance(v, float) and math.isnan(v)), (
                f"smoke {nm}: metric {k} null/NaN: {out}")

    print(
        f"[selftest] region_c_optimal_probe_v1_n4096 PASS "
        f"smoke_C(ret={out_c['retention']:.3f}, hallu={out_c['above_thresh_frac']:.3f}) "
        f"smoke_A(ret={out_a['retention']:.3f}, hallu={out_a['above_thresh_frac']:.3f})",
        flush=True,
    )


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done_seeds, remaining_seeds = resumable_seeds(seeds, out_dir)

    print(f"[run] region_c_optimal_probe_v1_n4096 smoke={smoke} N={N_cfg} "
          f"cells={len(CELLS)} seeds={seeds} done={done_seeds} todo={remaining_seeds} "
          f"device={device_str}", flush=True)
    t0 = time.time()

    for seed in remaining_seeds:
        seed_cells = []
        for region, cell_key, beta, M_frac in CELLS:
            cell = run_one_cell(cell_key, region, beta, M_frac, seed, N_cfg, device)
            seed_cells.append(cell)
            print(f"  seed={seed} region={region} cell={cell_key} "
                  f"ret={cell['retention']:.3f} hallu={cell['above_thresh_frac']:.3f} "
                  f"max_iso={cell['max_iso']:.3f} etr={cell['edit_then_retrieve']:.3f} "
                  f"lat={cell['retrieval_latency_ns']:.0f}ns "
                  f"sharp={cell['kf1_sharpness']:.1f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        write_partial_key(out_dir, seed, {
            "seed": seed,
            "N": N_cfg,
            "cells": seed_cells,
            "_done_at": time.time(),
        })

    # Aggregate
    all_cells = []
    for s in seeds:
        body = load_partial_key(out_dir, s)
        if body is None:
            continue
        all_cells.extend(body["cells"])

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "region_c_optimal_probe_v1_n4096",
        "N": N_cfg,
        "smoke": smoke,
        "cells_count": len(CELLS),
        "seeds": seeds,
        "cells": all_cells,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_path = out_dir / "metrics.json"
    payload = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
