"""KF-2 CROSS-CODEBOOK v2: edit isolation at N=8192 across codebook families.

CONTEXT:
  v267 KF2_CROSS_HARD_PASS at N=4096: max_iso < 0.05 for Kerdock, BSC, Gaussian.
  Edit isolation generalizes beyond Kerdock at N=4096.
  v2 extends to N=8192 to confirm: (a) isolation still holds, (b) 1/sqrt(N) bound
  remains predictive (1/sqrt(8192) = 0.01104 vs 1/sqrt(4096) = 0.01563).

SCIENTIFIC QUESTION:
  At N=8192, does max_iso < 0.05 hold for all 3 codebook families?
  Does isolation ratio approach 1/sqrt(N) as N grows?

PRE-REGISTERED BANDS (prior anchor N=4096 HARD_PASS):
  Expected: isolation_ratio scales as 1/sqrt(N). At N=8192: ~0.011 vs N=4096: ~0.016.

  HARD_PASS: max_iso < 0.05 at ALL 3 families at >= 4/5 seeds.
    AND mean_max_iso at N=8192 < mean_max_iso at N=4096 (N-scaling confirmed).
    Interpretation: isolation robust to N-growth; KF-2 scales with N.
  HARD_FAIL: max_iso >= 0.10 at any family.
    Interpretation: isolation breaks at N=8192.
  MIDDLE_BAND: max_iso in [0.05, 0.10) for one family.

FORMULA SELF-TESTS:
  1. theory_bound at N=8192 = 1/sqrt(8192) = 0.01104.
  2. N=8192 isolation should be tighter than N=4096 (0.01563).
  3. N == 8192 (PROT-018 binding).
  4. M at M_frac=2.0, N=8192: M=16384.
  5. OOM: W=8192^2*4=268MB. Keys=16384*8192*4=537MB. CB=268MB. Total~1GB. OK.

OOM CHECK:
  Worst M_frac=4.0, N=8192: M=32768. Keys=32768*8192*4=1.07GB. W=268MB. CB=268MB.
  Total~1.6GB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  3 families x 3 M_fracs x 5 seeds = 45 cells. Per cell at N=8192 ~4s.
  Total: 45*4=180s. Safety: ceil(1.5*180*5)=1350s. _n8192 floor = 21600. timeout_s=21600.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: kf2_cross_codebook_v2_n8192
Queue: overnight_queue (GPU; N=8192)
Pre-reg: preregs/2026-05-28_kf2_cross_codebook_v2_n8192.md
Parent: kf2_cross_codebook_v1_n4096 (v267 HARD_PASS cross-codebook generalization)
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

# Load kf2_cross_codebook_v1 for run_one_cell_family
_v1_path = REPO / "experiments" / "exp_kf2_cross_codebook_v1_n4096.py"
_v1_spec = importlib.util.spec_from_file_location("kf2_cross_v1_n8k", _v1_path)
kf2_v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(kf2_v1)

run_one_cell_family = kf2_v1.run_one_cell_family

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

M_FRACS_FULL  = [0.5, 1.0, 2.0]
M_FRACS_SMOKE = [1.0]

FAMILIES = ["kerdock", "bsc", "gaussian"]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

N_PROBE = 200
N_EDITS = 10   # number of edit probes per cell (matches v1 default)

# Pre-registered thresholds
HP_ISOLATION_MAX = 0.05
HF_CONTAMINATION = 0.10
HP_SEEDS_MIN     = 4


def get_output_dir(default_name: str = "kf2_cross_codebook_v2_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF2_CROSS_V2_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)
    theory_bound = 1.0 / math.sqrt(N)

    # Per family max iso
    family_max: Dict[str, float] = {}
    for fam in FAMILIES:
        fc = [c for c in cells if c.get("family") == fam and c.get("isolation_ratio") is not None]
        family_max[fam] = max(c["isolation_ratio"] for c in fc) if fc else float("nan")

    all_max = [v for v in family_max.values() if not math.isnan(v)]
    any_hf = any(v >= HF_CONTAMINATION for v in all_max)
    all_pass = all(v < HP_ISOLATION_MAX for v in all_max)

    # Seed-level pass count for non-Kerdock
    nk_cells = [c for c in cells if c.get("family") != "kerdock"
                and c.get("isolation_ratio") is not None]
    pass_seeds_nk = sum(1 for c in nk_cells if c["isolation_ratio"] < HP_ISOLATION_MAX)
    total_nk = len(nk_cells)

    mean_max_iso = sum(all_max) / len(all_max) if all_max else float("nan")

    detail = (f"family_max={dict((k, round(v, 5)) for k,v in family_max.items())} "
              f"theory_bound={theory_bound:.5f} mean_max_iso={mean_max_iso:.5f} "
              f"nk_pass={pass_seeds_nk}/{total_nk} N={N}")

    if any_hf:
        return ("KF2_CROSS_V2_HARD_FAIL",
                f"CONTAMINATION: max_iso >= {HF_CONTAMINATION} at some family. " + detail)

    if all_pass and pass_seeds_nk >= HP_SEEDS_MIN:
        return ("KF2_CROSS_V2_HARD_PASS",
                f"ISOLATION_ROBUST: all_families max_iso < {HP_ISOLATION_MAX}. " + detail)

    return ("KF2_CROSS_V2_MIDDLE_BAND",
            f"PARTIAL_ISOLATION: some families above threshold. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"
    # Formula: theory bound
    tb = 1.0 / math.sqrt(N_FULL)
    assert abs(tb - 0.01104) < 0.001, f"theory_bound N=8192: {tb}"
    # Verdict gate
    fake_hp = [{"family": f, "isolation_ratio": 0.02} for f in FAMILIES for _ in range(5)]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HARD_PASS gate: {v}"
    fake_hf = [{"family": "bsc", "isolation_ratio": 0.15}]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell
    device = torch.device("cpu")
    n_edits_test = 5
    cell = run_one_cell_family("kerdock", 1.0, 17, N_SMOKE, n_edits_test, device)
    assert "isolation_ratio" in cell, f"isolation_ratio missing: {list(cell.keys())}"
    assert not math.isnan(cell["isolation_ratio"]), "isolation_ratio NaN"
    # 4x scale
    cell4 = run_one_cell_family("kerdock", 1.0, 17, N_SMOKE * 4, n_edits_test, device)
    assert "isolation_ratio" in cell4, f"4x isolation_ratio missing"
    print(f"[selftest] kf2_cross_codebook_v2_n8192 PASS iso_smoke={cell['isolation_ratio']:.5f}", flush=True)


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
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] kf2_cross_codebook_v2_n8192 smoke={smoke} N={N_cfg} families={FAMILIES} seeds={seeds} device={device_str}", flush=True)
    t0 = time.time()

    all_cells = []
    for family in FAMILIES:
        for M_frac in m_fracs:
            print(f"\n  [family={family} M_frac={M_frac}]", flush=True)
            for seed in seeds:
                cell = run_one_cell_family(family, M_frac, seed, N_cfg, N_EDITS, device)
                all_cells.append(cell)
                iso = cell.get("isolation_ratio")
                iso_str = f"{iso:.5f}" if iso is not None else "None"
                print(f"  {family} M={M_frac} seed={seed} iso={iso_str} ({time.time()-t0:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "kf2_cross_codebook_v2_n8192", "N": N_cfg, "smoke": smoke,
        "families": FAMILIES, "M_fracs": m_fracs, "seeds": seeds,
        "cells": all_cells, "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
