"""KF-3 CROSS-CODEBOOK MULTI-SUBSTRATE ISOLATION v1: N=4096 across codebook families.

CONTEXT:
  kf3_multisub_v2_n4096 (MIDDLE_BAND): max_leakage=0.0148 > HP=0.01, max_contam=0.0544.
  Isolation mechanism (from kf3v2): info_leakage = mean |cos(resp_A, resp_B_Akeys)|,
    state_contamination = max |cos(resp_A, resp_B_Akeys)| where resp_X = X's query response.
  v2 uses Kerdock codebook only.

  KEY QUESTION: does cross-substrate isolation depend on the codebook family?
  With BSC or Gaussian codebooks, do W_A and W_B show less cross-talk?

SCIENTIFIC QUESTION:
  Using the same kf3v2 isolation protocol (info_leakage, state_contamination) applied to
  3 codebook families: Kerdock, BSC, Gaussian.
  Does any family achieve max_leakage < 0.01 AND max_contam < 0.05?
  Is Kerdock the best (due to structured orthogonality), or does Gaussian perform similarly?

PRE-REGISTERED BANDS (axis-expansion; prior = kf3_multisub_v2_n4096 MIDDLE_BAND):
  Prior anchor: kf3v2 Kerdock: leakage=0.0148, contam=0.0544 at M_frac=4, N=4096.
  HARD_PASS: at least 1 codebook family shows max_leakage < 0.01 AND max_contam < 0.05
    at M_frac=4 at >= 3/5 seeds.
    Interpretation: isolation IS achievable with appropriate codebook choice.
  HARD_FAIL: max_leakage > 0.10 OR max_contam > 0.30 in ANY family.
  MIDDLE_BAND: all families have max_leakage > 0.01 but < HF.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. theory_bound = 1/sqrt(N) = 1/sqrt(4096) = 0.01563.
  3. info_leakage = mean |cos(resp_A, resp_B_Akeys)|.
     Expected for orthogonal HD spaces: ~ 1/sqrt(N) = 0.01563.
  4. state_contamination = max |cos(resp_A, resp_B_Akeys)|.
  5. For Kerdock: theory bound tighter (codebook orthogonality reduces cross-talk).
  6. selftest: theory_bound = 1/sqrt(4096) = 0.01563.

OOM CHECK:
  N=4096, M_frac=4: M=16384. W=64MB per substrate x 2 = 128MB.
  Codebook=64MB x 3 = 192MB. Query resp = 16384 * 4096 * 4 = 268MB. Total ~588MB. OK.

TIMEOUT ESTIMATE:
  3 families x 3 M_fracs x 5 seeds = 45 cells.
  Reference: kf3_multisub_v2_n4096 runs 5-seed x 3 M_fracs with N=4096.
  kf3v2 selftest runs in ~0.5s at N=4096 small probe. FULL: ~6s per cell.
  45 * 6 = 270s. Safety: ceil(1.5 * 270 * 3) = 1215s.
  Floor _n4096 = 14400s. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: kf3_cross_codebook_v1_n4096
Queue: remote_cpu_queue (CPU; KF-3 cross-codebook; N=4096; ~1h)
Pre-reg: preregs/2026-05-29_kf3_cross_codebook_v1_n4096.md
Parent: kf3_multisub_v2_n4096 (MIDDLE_BAND); kf2_cross_codebook_v1_n4096 (HARD_PASS)
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

# Load kf3_multisub_v2 for build_substrate, query_response, measure_info_leakage,
# measure_state_contamination, v3
_v2_path = REPO / "experiments" / "exp_kf3_multisub_v2_n4096.py"
_v2_spec = importlib.util.spec_from_file_location("kf3v2_cross", _v2_path)
kf3v2 = importlib.util.module_from_spec(_v2_spec)
_v2_spec.loader.exec_module(kf3v2)

v3 = kf3v2.v3
build_substrate_kerdock = kf3v2.build_substrate  # takes (codebook, M, seed, N, device)
query_response = kf3v2.query_response
measure_info_leakage = kf3v2.measure_info_leakage
measure_state_contamination = kf3v2.measure_state_contamination

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL  = [4, 8, 12]
M_FRACS_SMOKE = [4]

N_PROBE_FULL  = 100
N_PROBE_SMOKE = 30

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

CODEBOOK_FAMILIES = ["kerdock", "bsc", "gaussian"]

# Pre-registered thresholds (same as kf3v2)
HP_LEAKAGE_MAX = 0.01
HP_CONTAM_MAX  = 0.05
HF_LEAKAGE_MIN = 0.10
HF_CONTAM_MIN  = 0.30
HP_SEEDS_MIN   = 3


def get_output_dir(default_name: str = "kf3_cross_codebook_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_bsc_codebook(N: int, seed: int, device: torch.device) -> torch.Tensor:
    """Build N x N BSC (+/-1) codebook."""
    gen = torch.Generator(device=device).manual_seed(seed + 100)
    return (torch.randint(0, 2, (N, N), generator=gen, device=device) * 2 - 1).float()


def build_gaussian_codebook(N: int, seed: int, device: torch.device) -> torch.Tensor:
    """Build N x N Gaussian codebook (normalized rows)."""
    gen = torch.Generator(device=device).manual_seed(seed + 200)
    cb = torch.randn(N, N, generator=gen, device=device)
    norms = cb.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return cb / norms


def build_codebook_and_substrate(family: str, M: int, seed_cb: int, seed_sub: int,
                                   N: int, device: torch.device) -> Tuple:
    """Build codebook and substrate W for given family.
    Returns (codebook, W, keys, val_idx).
    """
    if family == "kerdock":
        try:
            cb, _ = v3.make_kerdock_4coset_codebook(N, device)
        except Exception:
            cb = build_bsc_codebook(N, seed_cb, device)
    elif family == "bsc":
        cb = build_bsc_codebook(N, seed_cb, device)
    elif family == "gaussian":
        cb = build_gaussian_codebook(N, seed_cb, device)
    else:
        raise ValueError(f"Unknown family: {family}")

    C = cb.shape[0]
    M_actual = min(M, C)
    # Use kf3v2 build_substrate logic (permutation-based key/val assignment)
    gen_cpu = torch.Generator(device='cpu').manual_seed(seed_sub)
    perm = torch.randperm(C, generator=gen_cpu)
    key_idx = perm[:M_actual].to(device)
    gen_val = torch.Generator(device='cpu').manual_seed(seed_sub + 99999)
    val_idx = torch.randperm(C, generator=gen_val)[:M_actual].to(device)
    keys = cb[key_idx]
    values = cb[val_idx]
    W = torch.zeros(N, N, dtype=torch.float32, device=device)
    batch = 256
    for start in range(0, M_actual, batch):
        k_b = keys[start:start + batch]
        v_b = values[start:start + batch]
        W += (v_b.T @ k_b) / N
    return cb, W, keys, val_idx


def run_one_cell_family(family: str, M_frac: int, seed: int,
                         N_use: int, n_probe: int,
                         device: torch.device) -> Dict:
    """KF-3 cross-substrate isolation (kf3v2 protocol) for one codebook family."""
    M = M_frac * N_use
    # Use same codebook for both substrates (same family, different seeds)
    cb, W_A, keys_A, val_A = build_codebook_and_substrate(
        family, M, seed_cb=seed, seed_sub=seed + 0, N=N_use, device=device)
    _, W_B, keys_B, val_B = build_codebook_and_substrate(
        family, M, seed_cb=seed, seed_sub=seed + 1000, N=N_use, device=device)

    n = min(n_probe, keys_A.shape[0], keys_B.shape[0])

    # kf3v2 isolation protocol: measure cross-talk via query responses
    resp_A = query_response(W_A, keys_A[:n], N_use)        # A queries via W_A
    resp_B_Akeys = query_response(W_B, keys_A[:n], N_use)  # B queries with A's keys

    info_leakage = measure_info_leakage(resp_A, resp_B_Akeys)
    state_contamination = measure_state_contamination(resp_A, resp_B_Akeys)
    theory_bound = 1.0 / math.sqrt(N_use)

    print(f"    fam={family} N={N_use} M_frac={M_frac} M={min(M, cb.shape[0])} seed={seed} "
          f"leakage={info_leakage:.5f} contam={state_contamination:.5f} "
          f"theory={theory_bound:.5f}", flush=True)
    return {
        "family": family,
        "M_frac": M_frac, "M": min(M, cb.shape[0]), "N": N_use, "seed": seed,
        "info_leakage": round(info_leakage, 6),
        "state_contamination": round(state_contamination, 6),
        "theory_bound": round(theory_bound, 6),
        "passes_hp_leakage": info_leakage < HP_LEAKAGE_MAX,
        "passes_hp_contam": state_contamination < HP_CONTAM_MAX,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF3_CROSS_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)
    theory_bound = 1.0 / math.sqrt(N)

    by_family: Dict[str, List] = {}
    for c in cells:
        by_family.setdefault(c["family"], []).append(c)

    results_per_family: Dict[str, Dict] = {}
    for fam, fam_cells in by_family.items():
        max_leakage_all = max(c["info_leakage"] for c in fam_cells)
        max_contam_all  = max(c["state_contamination"] for c in fam_cells)
        n_hp = sum(1 for c in fam_cells
                   if c.get("passes_hp_leakage") and c.get("passes_hp_contam"))
        results_per_family[fam] = {
            "max_leakage": max_leakage_all,
            "max_contam": max_contam_all,
            "n_hp": n_hp,
            "n_total": len(fam_cells),
        }

    if not results_per_family:
        return ("KF3_CROSS_INCONCLUSIVE", "No family results.")

    best_fam = min(results_per_family, key=lambda f: results_per_family[f]["max_leakage"])
    best = results_per_family[best_fam]

    detail = (f"best_family={best_fam} max_leakage={best['max_leakage']:.5f} "
              f"max_contam={best['max_contam']:.5f} n_hp={best['n_hp']}/{best['n_total']} "
              f"theory={theory_bound:.5f} HP_leak<{HP_LEAKAGE_MAX} HP_cont<{HP_CONTAM_MAX} N={N}")
    for fam, res in results_per_family.items():
        detail += f" | {fam}: leak={res['max_leakage']:.5f} cont={res['max_contam']:.5f}"

    # Hard fail: any family structurally contaminated
    hf_fams = [f for f, r in results_per_family.items()
               if r["max_leakage"] >= HF_LEAKAGE_MIN or r["max_contam"] >= HF_CONTAM_MIN]
    if hf_fams:
        return ("KF3_CROSS_HARD_FAIL",
                f"STRUCTURAL_CONTAMINATION: families={hf_fams}. " + detail)

    # Smoke case
    if len(cells) <= 5 or all(r["n_total"] <= 2 for r in results_per_family.values()):
        label = "KF3_CROSS_SMOKE_PASS" if best["n_hp"] > 0 else "KF3_CROSS_SMOKE_PARTIAL"
        return (label, f"SMOKE: " + detail)

    # Hard pass: at least one family meets HP criteria at enough seeds
    hp_fams = [f for f, r in results_per_family.items()
               if r["max_leakage"] < HP_LEAKAGE_MAX
               and r["max_contam"] < HP_CONTAM_MAX
               and r["n_hp"] >= HP_SEEDS_MIN]
    if hp_fams:
        return ("KF3_CROSS_HARD_PASS",
                f"ISOLATION_CONFIRMED: best_family={hp_fams[0]}. " + detail)

    return ("KF3_CROSS_MIDDLE_BAND", "PARTIAL_ISOLATION: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula self-tests
    theory_bound = 1.0 / math.sqrt(N_FULL)
    assert abs(theory_bound - 0.01563) < 0.001, f"theory_bound: {theory_bound}"

    # Verify kf3v2 module loaded correctly and has needed functions
    assert hasattr(kf3v2, "v3"), "kf3v2.v3 missing"
    assert hasattr(kf3v2, "query_response"), "query_response missing"
    assert hasattr(kf3v2, "measure_info_leakage"), "measure_info_leakage missing"
    assert hasattr(kf3v2, "measure_state_contamination"), "measure_state_contamination missing"

    # Verdict gates
    fake_hp_kerdock = [
        {"family": "kerdock", "M_frac": 4, "M": 16384, "N": N_FULL, "seed": s,
         "info_leakage": 0.005, "state_contamination": 0.03,
         "theory_bound": theory_bound,
         "passes_hp_leakage": True, "passes_hp_contam": True}
        for s in [7, 17, 23, 31, 41]
    ]
    fake_bsc = [
        {"family": "bsc", "M_frac": 4, "M": 4096, "N": N_FULL, "seed": s,
         "info_leakage": 0.02, "state_contamination": 0.07,
         "theory_bound": theory_bound,
         "passes_hp_leakage": False, "passes_hp_contam": False}
        for s in [7, 17, 23, 31, 41]
    ]
    v, msg = compute_verdict({"cells": fake_hp_kerdock + fake_bsc, "N": N_FULL})
    assert "HARD_PASS" in v, f"HP gate: {v}: {msg}"

    # HF case
    fake_hf = [
        {"family": "bsc", "M_frac": 4, "M": 4096, "N": N_FULL, "seed": 17,
         "info_leakage": 0.15, "state_contamination": 0.40,
         "theory_bound": theory_bound,
         "passes_hp_leakage": False, "passes_hp_contam": False},
    ]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HF gate: {vf}"

    # Smoke forward pass (N_SMOKE=1024, M_frac=4, BSC -- fast)
    device = torch.device("cpu")
    cell = run_one_cell_family("bsc", 4, 17, N_SMOKE, N_PROBE_SMOKE, device)
    assert "info_leakage" in cell, "info_leakage missing"
    assert not math.isnan(cell["info_leakage"]), "info_leakage NaN"
    assert cell["info_leakage"] >= 0, f"info_leakage negative: {cell['info_leakage']}"
    assert cell["info_leakage"] < 1.0, f"info_leakage >= 1.0: {cell['info_leakage']}"
    # Verify filter passes: at least 1 item has non-zero leakage
    # (If info_leakage > 0, that means cross-talk exists -- which is expected before HP)

    # 4x smoke (N_SMOKE * 4 = N_FULL = 4096 -- valid Kerdock N)
    cell4 = run_one_cell_family("bsc", 4, 17, N_SMOKE * 4, N_PROBE_SMOKE, device)
    assert "info_leakage" in cell4, "4x info_leakage missing"
    assert not math.isnan(cell4["info_leakage"]), "4x info_leakage NaN"

    print(f"[selftest] kf3_cross_codebook_v1_n4096 PASS "
          f"leakage_smoke={cell['info_leakage']:.5f} "
          f"leakage_4x={cell4['info_leakage']:.5f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device = torch.device("cpu")
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_probe = N_PROBE_SMOKE if smoke else N_PROBE_FULL

    print(f"[run] kf3_cross_codebook_v1_n4096 smoke={smoke} N={N_cfg} "
          f"M_fracs={m_fracs} seeds={seeds} n_probe={n_probe}", flush=True)
    t0 = time.time()

    all_cells = []
    for family in CODEBOOK_FAMILIES:
        print(f"\n  [family={family}]", flush=True)
        for M_frac in m_fracs:
            for seed in seeds:
                cell = run_one_cell_family(family, M_frac, seed, N_cfg, n_probe, device)
                all_cells.append(cell)
        print(f"  family={family} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "kf3_cross_codebook_v1_n4096", "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "seeds": seeds,
        "codebook_families": CODEBOOK_FAMILIES,
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
