"""PHASE LATTICE GRID v1: full (beta, M_frac) envelope map at N=4096.

CONTEXT:
  Foundational substrate-physics characterization. Single points (Region C/D
  HARD_PASS at v267) are not characterization; one-point-per-region doesn't
  ship product positioning. This is the full 9 x 7 = 63-cell grid at N=4096
  with the shared 6-metric battery from experiments/_metric_battery.py.

  Each cell measures all 6 metrics on ONE substrate setup (no recomputation
  per metric). Region labels (A/B/C/D) are derived at analysis-time from the
  M_c probe result.

SCIENTIFIC QUESTION:
  What is the operational envelope of the substrate across the (beta, M_frac)
  plane at N=4096? Where do the killer features survive, fade, and break?

PRE-REGISTERED BANDS (CHARACTERIZATION COVERAGE, not verdict-test):
  HARD_PASS: >= 290/315 cell-seeds complete with all 6 metrics populated.
    (The grid IS the deliverable; pass = sufficient coverage for the
     envelope map. >= 92% completion across 63 cells x 5 seeds.)
  HARD_FAIL: < 200/315 cell-seeds complete. (Insufficient coverage --
    something systematic broke.)
  MIDDLE_BAND: 200-289 cell-seeds (partial map; identify what failed.)

  Interpretation lives in cap_map post-analysis, NOT here. This anchor's
  job is to deliver populated metric data for the whole grid.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. 9 betas x 7 M_fracs = 63 cells.
  3. 63 cells x 5 seeds = 315 cell-seeds.
  4. HARD_PASS gate: completed_cell_seeds >= 290.
  5. M for M_frac=0.25 at N=4096: M = 1024.
  6. M for M_frac=16   at N=4096: M = 65536.

OOM CHECK:
  Max M at M_frac=16, N=4096: M=65536. keys=65536*4096*4 = 1.07GB.
  W=64MB. CB=268MB. Total ~1.4GB. Under 6GB. OK at every cell.

TIMEOUT ESTIMATE (battery class):
  Per cell at N=4096: substrate build + 6 metrics ~ 5-15s (M-dependent).
  315 cell-seeds x ~10s mean = ~3150s = ~0.9h optimistic.
  315 cell-seeds x ~60s mean (matrix dominant cases) = ~5.25h.
  User spec adopts 86400s (24h) per PROT-019 keyword guidance for the
  battery-class scope. Justification: 9-beta x 7-M_frac x 5-seed sweep at
  N=4096 with 6-metric battery per cell; conservative ceiling.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: phase_lattice_grid_v1_n4096
Queue: overnight_queue (GPU; N=4096; 63 cells x 5 seeds = 315 cell-seeds)
Pre-reg: preregs/2026-05-30_phase_lattice_grid_v1_n4096.md
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

# Metric battery (single source of truth; shared with Anchor 2)
from experiments._metric_battery import (   # noqa: E402
    run_battery,
    METRIC_NAMES,
)

# Cell-level checkpointing: each (beta, M_frac, seed) writes its own partial.
# We use the lower-level write_partial_key with composite keys.
_ckpt_path = REPO / "experiments" / "_seed_checkpoint.py"
_ckpt_spec = importlib.util.spec_from_file_location("_seed_checkpoint_grid", _ckpt_path)
_ckpt = importlib.util.module_from_spec(_ckpt_spec)
_ckpt_spec.loader.exec_module(_ckpt)
list_completed_keys = _ckpt.list_completed_keys
write_partial_key   = _ckpt.write_partial_key
load_partial_key    = _ckpt.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds to N = 4096
N = 4096        # PROT-018 production-N anchor (queue_add.py regex hits this line)
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Grid: 9 betas x 7 M_fracs = 63 cells. M_frac is fraction-of-N
# (consistent with Anchor 2).
BETAS_FULL = [2.0, 4.0, 8.0, 10.0, 12.0, 16.0, 32.0, 64.0, 128.0]
MFRACS_FULL = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]

# Smoke: small grid to exercise every codepath
BETAS_SMOKE = [4.0, 10.0, 32.0]
MFRACS_SMOKE = [0.25, 1.0, 4.0]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

N_PROBE = 200
N_EDITS = 16

# Pre-registered coverage thresholds (at FULL: 315 cell-seeds expected).
# HARD_PASS at >= 290/315 ~= 92%. HARD_FAIL at < 200/315 ~= 63%.
# At smoke (9 cell-seeds), we still gate on absolute coverage AT FULL --
# but for smoke labelling we use fractional thresholds so smoke can pass
# its own coverage check (smoke complete = 9/9 = 100% -> HARD_PASS smoke).
HP_COMPLETED_MIN = 290    # of 315
HF_COMPLETED_MAX = 199    # < 200 = failure
HP_FRAC          = 290.0 / 315.0
HF_FRAC          = 200.0 / 315.0


def get_output_dir(default_name: str = "phase_lattice_grid_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _M_for_cell(M_frac: float, N: int) -> int:
    """M = M_frac * N (fraction-of-N convention)."""
    return max(1, int(round(M_frac * N)))


def cell_key(beta: float, M_frac: float, seed: int) -> str:
    """Composite key for per-cell-seed checkpoint."""
    bs = f"{beta:g}".replace(".", "p").replace("-", "n")
    ms = f"{M_frac:g}".replace(".", "p").replace("-", "n")
    return f"b{bs}_m{ms}_seed{int(seed)}"


def run_one_cell(beta: float, M_frac: float, seed: int, N_use: int,
                 device: torch.device) -> Dict:
    """One (beta, M_frac, seed) cell: substrate build + 6-metric battery."""
    M = _M_for_cell(M_frac, N_use)
    out = run_battery(N_use, M, beta, seed, device, n_probe=N_PROBE, n_edits=N_EDITS)
    out["M_frac"] = float(M_frac)
    out["cell_key"] = cell_key(beta, M_frac, seed)
    return out


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("GRID_INCONCLUSIVE", "No cells.")

    total_expected = summary.get("total_expected", 315)

    n_complete = 0
    for c in cells:
        if all(c.get(m) is not None for m in METRIC_NAMES):
            n_complete += 1

    # Quick stats across the grid (informational, not gating)
    rets = [c.get("retention") for c in cells if c.get("retention") is not None]
    halls = [c.get("above_thresh_frac") for c in cells
              if c.get("above_thresh_frac") is not None]
    mean_ret = (sum(rets) / len(rets)) if rets else 0.0
    mean_hall = (sum(halls) / len(halls)) if halls else 0.0

    detail = (f"cells_complete={n_complete}/{total_expected} "
              f"mean_retention={mean_ret:.3f} mean_above_thresh={mean_hall:.3f} "
              f"N={summary.get('N', N_FULL)} "
              f"betas={len(set(c.get('beta') for c in cells))} "
              f"mfracs={len(set(c.get('M_frac') for c in cells))}")

    frac_complete = n_complete / max(1, total_expected)
    if frac_complete < HF_FRAC:
        return ("GRID_HARD_FAIL",
                f"INSUFFICIENT_COVERAGE: frac_complete={frac_complete:.3f} < "
                f"{HF_FRAC:.3f}. " + detail)
    if frac_complete >= HP_FRAC:
        return ("GRID_HARD_PASS",
                f"ENVELOPE_MAP_DELIVERED: {n_complete}/{total_expected} cells "
                f"populated with 6 metrics each (frac={frac_complete:.3f}). "
                + detail)
    return ("GRID_MIDDLE_BAND",
            f"PARTIAL_MAP: frac_complete={frac_complete:.3f} in [{HF_FRAC:.3f},"
            f"{HP_FRAC:.3f}). " + detail)


def _instrumentation_selftest() -> None:
    """Mandatory: assert all 6 metrics non-null/non-sentinel + verdict gates."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    assert len(BETAS_FULL) == 9, f"betas count: {len(BETAS_FULL)} != 9"
    assert len(MFRACS_FULL) == 7, f"mfracs count: {len(MFRACS_FULL)} != 7"
    assert len(BETAS_FULL) * len(MFRACS_FULL) == 63, "63-cell grid"
    assert 63 * len(SEEDS_FULL) == 315, "315 cell-seeds"

    # Formula self-tests
    assert _M_for_cell(0.25, N_FULL) == 1024, f"M @ M_frac=0.25: {_M_for_cell(0.25, N_FULL)}"
    assert _M_for_cell(16.0, N_FULL) == 65536, f"M @ M_frac=16: {_M_for_cell(16.0, N_FULL)}"

    # OOM check at max M
    M_max = _M_for_cell(16.0, N_FULL)
    total_bytes = M_max * N_FULL * 4 + N_FULL * N_FULL * 4 + 49152 * N_FULL * 4
    assert total_bytes < 6e9, f"OOM at FULL max-M: {total_bytes/1e6:.0f}MB >= 6GB"

    # Cell key formula
    ck = cell_key(32.0, 1.0, 17)
    assert ck == "b32_m1_seed17", f"cell_key: {ck}"
    ck2 = cell_key(0.25, 0.5, 7)
    assert ck2 == "b0p25_m0p5_seed7", f"cell_key: {ck2}"

    # Verdict self-tests
    # HARD_PASS: 290 complete cells
    fake_hp = [
        {"beta": 4.0, "M_frac": 1.0, "seed": 17,
         "above_thresh_frac": 0.01, "max_iso": 0.01, "retention": 0.9,
         "edit_then_retrieve": 0.9, "retrieval_latency_ns": 10000.0,
         "kf1_sharpness": 30.0}
        for _ in range(290)
    ]
    v, msg = compute_verdict({"cells": fake_hp, "N": N_FULL, "total_expected": 315})
    assert "HARD_PASS" in v, f"HARD_PASS gate: {v} {msg}"

    # HARD_FAIL: 100 complete cells
    fake_hf = fake_hp[:100]
    vf, mf = compute_verdict({"cells": fake_hf, "N": N_FULL, "total_expected": 315})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf} {mf}"

    # MIDDLE_BAND: 250 complete cells
    fake_mb = fake_hp[:250]
    vm, mm = compute_verdict({"cells": fake_mb, "N": N_FULL, "total_expected": 315})
    assert "MIDDLE_BAND" in vm, f"MIDDLE_BAND gate: {vm} {mm}"

    # Smoke: 1 cell at smoke scale (CPU, small N) to exercise the battery
    device = torch.device("cpu")
    out = run_one_cell(8.0, 1.0, 17, N_SMOKE, device)
    for k in METRIC_NAMES:
        v_ = out.get(k)
        assert v_ is not None and not (isinstance(v_, float) and math.isnan(v_)), (
            f"smoke: metric {k} null/NaN: {out}")

    print(
        f"[selftest] phase_lattice_grid_v1_n4096 PASS "
        f"smoke ret={out['retention']:.3f} hallu={out['above_thresh_frac']:.3f} "
        f"max_iso={out['max_iso']:.3f} etr={out['edit_then_retrieve']:.3f} "
        f"lat={out['retrieval_latency_ns']:.0f}ns sharp={out['kf1_sharpness']:.1f}",
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

    N_cfg    = N_SMOKE if smoke else N_FULL
    betas    = BETAS_SMOKE if smoke else BETAS_FULL
    mfracs   = MFRACS_SMOKE if smoke else MFRACS_FULL
    seeds    = SEEDS_SMOKE if smoke else SEEDS_FULL

    total_expected = len(betas) * len(mfracs) * len(seeds)
    out_dir = get_output_dir()

    # Per-cell-seed checkpoint: list completed keys
    done_keys = set(list_completed_keys(out_dir))
    print(f"[run] phase_lattice_grid_v1_n4096 smoke={smoke} N={N_cfg} "
          f"betas={len(betas)} mfracs={len(mfracs)} seeds={len(seeds)} "
          f"total_expected={total_expected} already_done={len(done_keys)} "
          f"device={device_str}", flush=True)
    t0 = time.time()

    n_done_this_run = 0
    n_skipped = 0
    for beta in betas:
        for M_frac in mfracs:
            for seed in seeds:
                ck = cell_key(beta, M_frac, seed)
                if ck in done_keys:
                    n_skipped += 1
                    continue
                try:
                    out = run_one_cell(beta, M_frac, seed, N_cfg, device)
                    # _seed_checkpoint verifies 'seed' field matches the key.
                    # Move the int-seed aside and stamp the composite key.
                    out["seed_int"] = out["seed"]
                    out["seed"] = ck
                    write_partial_key(out_dir, ck, out)
                    n_done_this_run += 1
                    print(f"  {ck} ret={out['retention']:.3f} "
                          f"hallu={out['above_thresh_frac']:.3f} "
                          f"max_iso={out['max_iso']:.3f} "
                          f"etr={out['edit_then_retrieve']:.3f} "
                          f"lat={out['retrieval_latency_ns']:.0f}ns "
                          f"sharp={out['kf1_sharpness']:.1f} "
                          f"({time.time()-t0:.1f}s)", flush=True)
                except (RuntimeError, MemoryError) as e:
                    # OOM or runtime: log + continue. Coverage metric counts
                    # populated cells only -- failure is implicit absence.
                    print(f"  {ck} CELL_FAILED: {type(e).__name__}: {e}", flush=True)
                    if device.type == 'cuda':
                        torch.cuda.empty_cache()

    # Aggregate all completed cells (from this run + earlier checkpoints)
    all_cells = []
    for ck in list_completed_keys(out_dir):
        body = load_partial_key(out_dir, ck)
        if body is None:
            continue
        all_cells.append(body)

    verdict, verdict_msg = compute_verdict({
        "cells": all_cells, "N": N_cfg, "total_expected": total_expected,
    })
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "phase_lattice_grid_v1_n4096",
        "N": N_cfg,
        "smoke": smoke,
        "betas": betas,
        "mfracs": mfracs,
        "seeds": seeds,
        "total_expected": total_expected,
        "n_completed": len(all_cells),
        "n_done_this_run": n_done_this_run,
        "n_skipped_already_done": n_skipped,
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
    print(f"[completed] {len(all_cells)}/{total_expected}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
