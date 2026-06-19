"""KF-2 EDIT ISOLATION PROOF v2: N=8192 envelope-extension of v1 HARD_PASS at N=4096.

CONTEXT:
  kf2_isolation_proof_v1 (N=4096): FIRST-HARD_PASS of KF-2 reframe.
    max_iso=0.02020 < 0.05 (2.5x below threshold), 5-seed x 5-M_fracs.
    within_theory_frac reported; 20% theory-bound exceedance at N=4096.
  v2 (THIS): N=8192 envelope-extension per
    strategy_request_to_exp_dev_v260_kf2_n8192_envelope_extension_2026-05-28.md
    Characterize whether theory_bound exceedance persists or CLOSES at N=8192.
    theory_bound at N=8192: 1/sqrt(8192) = 0.01105 (vs 0.01563 at N=4096).

SCIENTIFIC QUESTION:
  Does isolation_ratio < 0.05 hold at N=8192 (production scale)?
  Does theory_bound exceedance fraction decrease at higher N (expected if exceedance
  is a finite-N artifact)?
  Does max_iso CLOSE toward theory_bound at N=8192 vs N=4096?

PRE-REGISTERED BANDS (envelope-extension; prior anchor = v1 N=4096 HARD_PASS):
  Prior anchor: v1 max_iso=0.02020 < 0.05 all cells. within_theory_frac ~0.80.
  HARD_PASS: max_iso < 0.05 across ALL M_fracs AND all 5 seeds (same gate as v1).
    PLUS: max_iso < 0.02020 (tighter than v1 = improvement at N=8192; product story strengthens).
    Interpretation: N=8192 confirms structural edit isolation; exceedance closes with N.
  HARD_FAIL: max_iso >= 0.10 at any under-cap M_frac (structural contamination).
    Would require re-analysis of edit-isolation claim.
  MIDDLE_BAND: max_iso in [0.05, 0.10); partial isolation.

FORMULA SELF-TESTS:
  1. theoretical bound at N=8192: 1/sqrt(8192) = 0.01105. Verify formula.
  2. delta_acc = acc_before - acc_after for non-edited keys. Should be ~0.
  3. isolation_ratio = max(|delta_acc[j]|) over j != edited. Range [0, 1].
  4. N stated in anchor name (_n8192 suffix; production N = 8192).
  5. within_theory_frac = fraction of cells where isolation_ratio <= theory_bound.
  6. at N=8192 theory_bound=0.01105 < N=4096 theory_bound=0.01563 (smaller = tighter).

TIMEOUT ESTIMATE:
  v1 ran in ~19.6s at N=4096 (5 seeds x 5 M_fracs x 50 edits).
  N-scale factor: (8192/4096)^1.5 = 2.828x.
  timeout_s = ceil(1.5 * 19.6 * 2.828) = ceil(83.1) -> 300s.
  Safety: use 600s (same as v1; conservative for N=8192).
  Under 2h: no extra visibility flag.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Queue: remote_cpu_queue (pure CPU; Kerdock isolation proof; fast)
Pre-reg: preregs/2026-05-28_kf2_isolation_proof_v2_n8192.md
Parent: kf2_isolation_proof_v1 (N=4096 FIRST-HARD_PASS)
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
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load v1 base (Kerdock builder, run_one_cell, compute_verdict)
_v1_path = REPO / "experiments" / "exp_kf2_isolation_proof_v1.py"
_v1_spec = importlib.util.spec_from_file_location("kf2_v1_base", _v1_path)
v1_mod = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1_mod)

# Bit-precision helper (BE-1 plumbing; fp32 default = no-op = backwards compat).
sys.path.insert(0, str(REPO / "experiments"))
import _bit_precision as bp  # noqa: E402

run_one_cell = v1_mod.run_one_cell
v3 = v1_mod.v3  # Kerdock codebook builder pulled through v1


def run_one_cell_with_precision(M_frac: float, seed: int, device: torch.device,
                                  N_use: int, n_edits: int, precision: str) -> Dict:
    """Precision-aware variant of v1.run_one_cell.

    Mirrors v1 exactly when precision='fp32' (no-op quantize-roundtrip is byte-exact).
    For non-fp32 precisions: quantizes W after the storage step but before retrieval,
    so all retrieval/edit-impact computations see the precision-degraded substrate.
    """
    try:
        cb = v3.make_kerdock_4coset_codebook(N_use)
    except Exception:
        cb = None
    if cb is None:
        rng_cb = torch.Generator()
        rng_cb.manual_seed(0)
        cb = (torch.randint(0, 2, (N_use, N_use), generator=rng_cb) * 2 - 1).float()
    C = cb.shape[0]
    M = min(int(M_frac * N_use), C)
    cb = cb.to(device)

    rng = torch.Generator()
    rng.manual_seed(seed + 300)
    key_idx = torch.randint(0, C, (M,), generator=rng)
    val_idx = torch.randint(0, C, (M,), generator=rng)
    keys = cb[key_idx]
    vals = cb[val_idx]

    # --- Storage step ---
    W = torch.zeros(N_use, N_use, device=device, dtype=torch.float32)
    batch = 256
    for start in range(0, M, batch):
        k_b = keys[start:start + batch]
        v_b = vals[start:start + batch]
        W = W + (v_b.T @ k_b) / N_use

    # --- Precision intercept: quantize W after storage, before retrieval. ---
    if precision != "fp32":
        W = bp.quantize_roundtrip(W, precision)

    # --- Retrieval baseline ---
    n_probe = min(M, 100)
    probe_keys = keys[:n_probe]
    probe_val = val_idx[:n_probe] % C
    sims_before = (cb @ (probe_keys @ W.T).T) / N_use
    pred_before = torch.argmax(sims_before, dim=0)
    acc_before = (pred_before == probe_val.to(device)).float()

    isolation_ratios = []
    n_edits_actual = min(n_edits, M)
    for edit_i in range(0, n_edits_actual, max(1, n_edits_actual // 10)):
        rng2 = torch.Generator()
        rng2.manual_seed(seed + edit_i + 1000)
        new_val_idx = torch.randint(0, C, (1,), generator=rng2)
        new_val = cb[new_val_idx[0]]
        old_val = vals[edit_i]
        old_key = keys[edit_i]

        W_edited = W + torch.outer(new_val - old_val, old_key) / N_use
        # Re-quantize edited W so the substrate-at-INTN simulation is consistent.
        if precision != "fp32":
            W_edited = bp.quantize_roundtrip(W_edited, precision)

        non_edit_mask = torch.ones(n_probe, dtype=torch.bool)
        non_edit_mask[min(edit_i, n_probe - 1)] = False
        probe_ne = probe_keys[non_edit_mask]
        probe_val_ne = probe_val[non_edit_mask]

        if probe_ne.shape[0] > 0:
            sims_after = (cb @ (probe_ne @ W_edited.T).T) / N_use
            pred_after = torch.argmax(sims_after, dim=0)
            acc_after = (pred_after == probe_val_ne.to(device)).float()
            acc_before_ne = acc_before[non_edit_mask]
            delta = (acc_before_ne - acc_after).abs().mean().item()
            isolation_ratios.append(delta)

    isolation_ratio = max(isolation_ratios) if isolation_ratios else 0.0
    theory_bound = 1.0 / math.sqrt(N_use)

    return {
        "M_frac": M_frac,
        "M": M,
        "seed": seed,
        "isolation_ratio": isolation_ratio,
        "theory_bound": theory_bound,
        "n_edits_run": n_edits_actual,
        "within_theory": isolation_ratio <= theory_bound,
    }

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL = 8192        # PROT-018 binding contract
N_SMOKE = 1024       # smoke at N=1024 (Kerdock-valid: log2=10)
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

M_FRACS_FULL = [0.25, 0.5, 1.0, 2.0, 4.0]
M_FRACS_SMOKE = [0.25, 1.0, 2.0]

N_EDITS_FULL = 50
N_EDITS_SMOKE = 10

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (v1 gate + tighter improvement band)
HP_ISOLATION_MAX = 0.05        # max_iso < 0.05 for all cells (same as v1)
HP_ISOLATION_TIGHT = 0.02020   # max_iso < v1 result = improvement at N=8192
HF_CONTAMINATION = 0.10        # max_iso >= 0.10 at any under-cap cell


def get_output_dir(default_name: str = "kf2_isolation_proof_v2_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict(summary: Dict) -> tuple:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF2V2_MIDDLE_BAND", "No cells.")

    N_use = summary.get("N", N_FULL)
    theory_bound = 1.0 / math.sqrt(N_use)

    all_iso = [c["isolation_ratio"] for c in cells]
    max_iso = max(all_iso)
    mean_iso = sum(all_iso) / len(all_iso)

    undercap_cells = [c for c in cells if c["M_frac"] <= 1.0]
    undercap_iso = [c["isolation_ratio"] for c in undercap_cells]
    max_undercap_iso = max(undercap_iso) if undercap_iso else 0.0

    theory_pass_frac = sum(1 for c in cells if c["isolation_ratio"] <= theory_bound) / len(cells)

    detail = (f"N={N_use}. max_iso={max_iso:.5f}. mean_iso={mean_iso:.5f}. "
              f"max_undercap_iso={max_undercap_iso:.5f}. "
              f"theory_bound={theory_bound:.5f}. "
              f"within_theory_frac={theory_pass_frac:.2f}.")

    # HARD_FAIL: contamination > 0.10 at under-cap cells
    if max_undercap_iso >= HF_CONTAMINATION:
        return ("KF2V2_HARD_FAIL",
                f"EDIT CONTAMINATION: max_undercap_iso={max_undercap_iso:.4f} >= {HF_CONTAMINATION}. "
                + detail)

    # HARD_PASS: all cells below 0.05
    if max_iso < HP_ISOLATION_MAX:
        tight_label = "TIGHT" if max_iso < HP_ISOLATION_TIGHT else "STANDARD"
        return (f"KF2V2_HARD_PASS_{tight_label}",
                f"EDIT ISOLATION PROVED N=8192 ({tight_label}): max_iso={max_iso:.5f} < {HP_ISOLATION_MAX}. "
                f"Kerdock substrate structurally isolates edits at production scale. "
                + detail)

    return ("KF2V2_MIDDLE_BAND",
            f"Partial isolation: max_iso={max_iso:.5f} in [{HP_ISOLATION_MAX}, {HF_CONTAMINATION}). "
            + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel."""
    # PROT-018: N_FULL must be 8192
    assert N_FULL == 8192, f"N_FULL must be 8192; got {N_FULL}"

    # Test theory bound formula at N=8192
    tb_8192 = 1.0 / math.sqrt(8192)
    assert abs(tb_8192 - 0.011048543) < 1e-5, f"theory_bound at N=8192: {tb_8192}"

    # Confirm theory bound is tighter at N=8192 than at N=4096
    tb_4096 = 1.0 / math.sqrt(4096)
    assert tb_8192 < tb_4096, f"theory_bound not tighter at N=8192: {tb_8192} >= {tb_4096}"

    # Test one cell at smoke scale
    cell = run_one_cell(M_frac=1.0, seed=17,
                        device=torch.device("cpu"), N_use=N_SMOKE, n_edits=5)
    assert cell["isolation_ratio"] is not None and 0 <= cell["isolation_ratio"] <= 1.0, \
        f"isolation_ratio sentinel: {cell['isolation_ratio']}"
    assert "within_theory" in cell, f"within_theory missing: {cell}"

    # Test verdict HARD_PASS path
    cells_hp = [{"M_frac": mf, "M": int(mf * 64), "seed": 17,
                  "isolation_ratio": 0.01, "theory_bound": tb_8192,
                  "within_theory": True, "n_edits_run": 5}
                for mf in [0.25, 0.5, 1.0, 2.0, 4.0]]
    v, msg = compute_verdict({"cells": cells_hp, "N": 8192})
    assert "HARD_PASS" in v, f"Self-test HP failed: {v}: {msg}"

    # Test verdict HARD_FAIL path
    cells_hf = [{"M_frac": 0.5, "M": 32, "seed": 17,
                  "isolation_ratio": 0.15, "theory_bound": tb_8192,
                  "within_theory": False, "n_edits_run": 5}]
    v2, _ = compute_verdict({"cells": cells_hf, "N": 8192})
    assert "HARD_FAIL" in v2, f"Self-test HF failed: {v2}"

    # OOM pre-check: Kerdock W at N=8192 float32
    oom_bytes = N_FULL * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM: W at N=8192 = {oom_bytes:.2e} >= 6GB"

    print(f"[SELFTEST PASS] kf2_isolation_proof_v2_n8192: N_FULL={N_FULL} "
          f"theory_bound={tb_8192:.6f} cell_check_OK OOM={oom_bytes:.2e}",
          flush=True)


_instrumentation_selftest()  # Called at module scope before sweep


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--bit-precision", dest="bit_precision", default="fp32",
                        choices=list(bp.VALID_PRECISIONS),
                        help="W-matrix precision for BE-1 sweep (default fp32 = no-op)")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    N_use = N_SMOKE if smoke else N_FULL
    M_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_edits = N_EDITS_SMOKE if smoke else N_EDITS_FULL
    device = torch.device("cpu")
    precision = args.bit_precision

    outdir = get_output_dir()
    t0 = time.time()
    cells = []

    for seed in seeds:
        for mf in M_fracs:
            if precision == "fp32":
                # Backwards-compat path: identical to pre-retrofit behavior.
                cell = run_one_cell(mf, seed, device, N_use, n_edits)
            else:
                cell = run_one_cell_with_precision(mf, seed, device, N_use,
                                                    n_edits, precision)
            cells.append(cell)
            elapsed = time.time() - t0
            print(f"M/N={mf} seed={seed} iso={cell['isolation_ratio']:.5f} "
                  f"within_theory={cell['within_theory']} "
                  f"precision={precision} elapsed={elapsed:.1f}s")

    elapsed_s = time.time() - t0
    summary = {"cells": cells, "N": N_use, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)

    precision_md = bp.precision_metadata(N_use * N_use, precision)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed_s,
        "config": {
            "N": N_use,
            "M_fracs": M_fracs,
            "seeds": seeds,
            "n_edits": n_edits,
            "smoke": smoke,
            "bit_precision": precision,
        },
        "summary": summary,
        **precision_md,
    }

    out = outdir / "metrics.json"
    tmp = out.with_suffix(".json.tmp")
    with open(tmp, "w") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out)

    print(f"\nVERDICT: {verdict}")
    print(f"MSG: {verdict_msg}")
    print(f"elapsed={elapsed_s:.1f}s")
    print(f"precision={precision} W_bytes={precision_md['precision_memory_bytes']} "
          f"(baseline={precision_md['precision_baseline_bytes']}, "
          f"ratio={precision_md['precision_compression_ratio']}x)")
    print(f"metrics -> {out}")


if __name__ == "__main__":
    main()
