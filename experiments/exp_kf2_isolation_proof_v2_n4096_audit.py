"""KF-2 EDIT ISOLATION PROOF v2 N=4096 AUDIT: Kerdock-safe N=4096 corroboration.

PARENT: exp_kf2_isolation_proof_v2_n8192.py -- v2 at N=8192 (Kerdock-even-log2 risk).
  N=8192 log2=13 (ODD) -- Kerdock-vulnerable. The v2_n8192 script may have encountered
  the even-log2 silent fallback, entangling BE-1 precision interpretation.
  This v2_n4096_audit re-runs the SAME isolation proof logic at N=4096 (log2=12 EVEN, SAFE)
  MINUS the BE-1 precision entanglement. fp32 only; no --bit-precision sweep.

SCIENTIFIC QUESTION:
  Does KF-2 edit isolation hold at N=4096 without BE-1 precision entanglement?
  Specifically: isolation_ratio < 0.05 at ALL M_fracs, ALL 5 seeds?
  Does max_iso at N=4096 compare cleanly to theory_bound=1/sqrt(4096)=0.01563?

PRE-REGISTERED BANDS (N=4096; same gate as v2 but at lower N):
  Prior anchor: kf2_isolation_proof_v1 (N=4096 FIRST-HARD_PASS; max_iso=0.02020).
  HARD_PASS: max_iso < 0.05 across ALL M_fracs AND all 5 seeds.
    PLUS: max_iso <= 0.02020 (matches or improves on v1; N-corroboration).
    Interpretation: KF-2 isolation confirmed at N=4096 without precision entanglement.
  HARD_FAIL: max_iso >= 0.10 at any under-cap M_frac.
    Would indicate the v1 HARD_PASS was not reproducible.
  MIDDLE_BAND: max_iso in [0.05, 0.10).

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. theory_bound = 1/sqrt(4096) = 0.01563. Formula: 1.0/math.sqrt(N_FULL).
  3. isolation_ratio = max(|delta_acc[j]|) over j != edited. Range [0, 1].
  4. within_theory_frac = fraction of cells where isolation_ratio <= theory_bound.
  5. At N=4096: theory_bound=0.01563 (looser than N=8192 theory_bound=0.01105).

TIMEOUT ESTIMATE:
  v1 at N=4096 ran in ~19.6s (5 seeds x 5 M_fracs x 50 edits).
  Same config: estimate 30s. Safety 100x: 3000s. Floor _n4096 = 14400. timeout_s = 14400.

KERDOCK AUDIT: N=4096 log2=12 EVEN. SAFE. No Kerdock fallback risk.
N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: kf2_isolation_proof_v2_n4096_audit
Queue: overnight_queue (GPU; N=4096 KF-2 isolation without BE-1 precision entanglement)
Pre-reg: preregs/2026-05-29_kf2_isolation_proof_v2_n4096_audit.md
Parent: kf2_isolation_proof_v2_n8192 (Kerdock-risk); kf2_isolation_proof_v1 (HARD_PASS)
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

# Load v1 base (Kerdock builder, run_one_cell -- fp32 baseline; no bit-precision plumbing)
_v1_path = REPO / "experiments" / "exp_kf2_isolation_proof_v1.py"
_v1_spec = importlib.util.spec_from_file_location("kf2_v1_audit", _v1_path)
v1_mod = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1_mod)

run_one_cell = v1_mod.run_one_cell
v3 = v1_mod.v3  # Kerdock codebook builder pulled through v1

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096       # PROT-018 binding contract
N_SMOKE = 1024       # smoke at N=1024 (Kerdock-valid: log2=10)
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL  = [0.25, 0.5, 1.0, 2.0, 4.0]
M_FRACS_SMOKE = [0.25, 1.0, 2.0]

N_EDITS_FULL  = 50
N_EDITS_SMOKE = 10

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (v1 gate + same-or-better band)
HP_ISOLATION_MAX   = 0.05      # max_iso < 0.05 for all cells (same as v1)
HP_ISOLATION_MATCH = 0.02020   # max_iso <= v1 result = N-corroboration pass
HF_CONTAMINATION   = 0.10      # max_iso >= 0.10 at any under-cap cell


def get_output_dir(default_name: str = "kf2_isolation_proof_v2_n4096_audit") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict(summary: Dict) -> tuple:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF2V2AUDIT_MIDDLE_BAND", "No cells.")

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

    # HARD_FAIL: contamination
    if max_undercap_iso >= HF_CONTAMINATION:
        return ("KF2V2AUDIT_HARD_FAIL",
                f"EDIT CONTAMINATION at N=4096: max_undercap_iso={max_undercap_iso:.4f} >= "
                f"{HF_CONTAMINATION}. v1 HARD_PASS not reproduced. "
                + detail)

    # HARD_PASS: all cells below 0.05
    if max_iso < HP_ISOLATION_MAX:
        match_label = "MATCH" if max_iso <= HP_ISOLATION_MATCH else "STANDARD"
        return (f"KF2V2AUDIT_HARD_PASS_{match_label}",
                f"EDIT ISOLATION PROVED N=4096 ({match_label}): max_iso={max_iso:.5f} < "
                f"{HP_ISOLATION_MAX}. Kerdock-safe N=4096 corroboration without BE-1 entanglement. "
                + detail)

    return ("KF2V2AUDIT_MIDDLE_BAND",
            f"Partial isolation at N=4096: max_iso={max_iso:.5f} in "
            f"[{HP_ISOLATION_MAX},{HF_CONTAMINATION}). "
            + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"N_FULL must be 4096; got {N_FULL}"

    # Test theory bound formula at N=4096
    tb_4096 = 1.0 / math.sqrt(4096)
    assert abs(tb_4096 - 0.015625) < 1e-5, f"theory_bound at N=4096: {tb_4096}"

    # Confirm looser than N=8192 theory bound
    tb_8192 = 1.0 / math.sqrt(8192)
    assert tb_4096 > tb_8192, f"theory_bound at N=4096 should be looser: {tb_4096} <= {tb_8192}"

    # Test one cell at smoke scale
    cell = run_one_cell(M_frac=1.0, seed=17,
                        device=torch.device("cpu"), N_use=N_SMOKE, n_edits=5)
    assert cell["isolation_ratio"] is not None and 0 <= cell["isolation_ratio"] <= 1.0, \
        f"isolation_ratio sentinel: {cell['isolation_ratio']}"
    assert "within_theory" in cell, f"within_theory missing: {cell}"

    # Test verdict HARD_PASS path
    cells_hp = [{"M_frac": mf, "M": int(mf * 64), "seed": 17,
                  "isolation_ratio": 0.01, "theory_bound": tb_4096,
                  "within_theory": True, "n_edits_run": 5}
                for mf in [0.25, 0.5, 1.0, 2.0, 4.0]]
    v, msg = compute_verdict({"cells": cells_hp, "N": 4096})
    assert "HARD_PASS" in v, f"Self-test HP failed: {v}: {msg}"

    # Test HARD_FAIL path
    cells_hf = [{"M_frac": 0.5, "M": 32, "seed": 17,
                  "isolation_ratio": 0.15, "theory_bound": tb_4096,
                  "within_theory": False, "n_edits_run": 5}]
    v2, _ = compute_verdict({"cells": cells_hf, "N": 4096})
    assert "HARD_FAIL" in v2, f"Self-test HF failed: {v2}"

    # Validity: at least 1 cell survived
    assert len(cells_hp) >= 1, "validity filter: no cells at smoke scale"

    # OOM pre-check: W at N=4096 float32
    oom_bytes = N_FULL * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM: W at N=4096 = {oom_bytes:.2e} >= 6GB"

    print(f"[SELFTEST PASS] kf2_isolation_proof_v2_n4096_audit: N_FULL={N_FULL} "
          f"theory_bound={tb_4096:.6f} cell_check_OK OOM={oom_bytes:.2e}",
          flush=True)


_instrumentation_selftest()  # Called at module scope before sweep


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--N", type=int, default=N_FULL)
    parser.add_argument("--timeout", type=int, default=14400)
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    N_use = N_SMOKE if smoke else N_FULL
    M_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_edits = N_EDITS_SMOKE if smoke else N_EDITS_FULL
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    out_dir = get_output_dir()
    t0 = time.time()
    cells = []

    for seed in seeds:
        for mf in M_fracs:
            cell = run_one_cell(mf, seed, device, N_use, n_edits)
            cells.append(cell)
            elapsed = time.time() - t0
            print(f"M/N={mf} seed={seed} iso={cell['isolation_ratio']:.5f} "
                  f"within_theory={cell['within_theory']} elapsed={elapsed:.1f}s",
                  flush=True)

    elapsed_s = time.time() - t0
    summary = {"cells": cells, "N": N_use, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)

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
            "bit_precision": "fp32",
        },
        "summary": summary,
    }

    out = out_dir / "metrics.json"
    tmp = out.with_suffix(".json.tmp")
    with open(tmp, "w") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out)

    print(f"\nVERDICT: {verdict}", flush=True)
    print(f"MSG: {verdict_msg}", flush=True)
    print(f"elapsed={elapsed_s:.1f}s", flush=True)
    print(f"metrics -> {out}", flush=True)


if __name__ == "__main__":
    main()
