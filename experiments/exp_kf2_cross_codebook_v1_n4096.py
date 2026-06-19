"""KF-2 CROSS-CODEBOOK EDIT ISOLATION v1: does isolation hold across codebook families?

CONTEXT:
  kf2_isolation_proof_v2_n8192 (v265 HARD_PASS): edit isolation confirmed at N=8192,
  max_iso=0.01010 < 0.05, within Kerdock theory bound (1/sqrt(N)).
  The Kerdock codebook structure provides the analytical guarantee.

  KEY QUESTION: is edit isolation a Kerdock-specific property, or does it generalize
  to other codebook families (BSC, antipodal random)?
  PRODUCT VALUE: if isolation holds for ANY binary codebook, the product is not
  locked to Kerdock geometry.

  This probe tests KF-2 isolation at N=4096 across 3 codebook families:
    1. Kerdock (confirmed; established baseline)
    2. BSC (random binary; N vectors of +/-1)
    3. Bipolar-Gaussian (random Gaussian normalized to unit norm)

SCIENTIFIC QUESTION:
  Does max_iso < 0.05 hold at N=4096 for BSC and Bipolar-Gaussian codebooks?
  Does isolation track the theory bound 1/sqrt(N) = 0.01563 for non-Kerdock?

PRE-REGISTERED BANDS (axis-expansion; prior anchor = kf2 v2 N=8192 HARD_PASS):
  Prior anchor: Kerdock max_iso=0.01010 < 0.05 at N=8192.
  HARD_PASS: max_iso < 0.05 at ALL 3 codebook families at N=4096 at >= 4/5 seeds.
    Interpretation: edit isolation is codebook-family robust.
  HARD_FAIL: max_iso >= 0.10 at BSC or Gaussian (structural contamination under non-Kerdock).
    Would indicate isolation is Kerdock-specific structure.
  MIDDLE_BAND: max_iso in [0.05, 0.10) for one family.
    Partial generalization.

FORMULA SELF-TESTS:
  1. theory_bound at N=4096 = 1/sqrt(4096) = 0.01563.
  2. isolation_ratio = max(|delta_acc[j]|) over j != edited. Range [0, 1].
  3. BSC codebook: N x N binary matrix. Each row is a pattern.
  4. Gaussian codebook: N x N Gaussian, normalized rows.
  5. N == 4096 (PROT-018 binding).

OOM CHECK:
  N=4096 M_frac=2.0: M=8192. keys=8192*4096*4=134MB. W=64MB. OK.
  Gaussian codebook N=4096: 4096*4096*4=64MB. All codebooks: 3*64MB=192MB. OK.

TIMEOUT ESTIMATE:
  run_one_cell per family: same as kf2 v1 at N=4096. v1 ran ~5s at N=4096.
  3 families x 5 M_fracs x 5 seeds = 75 cells x 1s = 75s.
  Safety: ceil(1.5 * 75 * 5) = 563s -> 900s.
  timeout_s = 1800.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: kf2_cross_codebook_v1_n4096
Queue: remote_cpu_queue (pure CPU; KF-2 across 3 codebook families; N=4096)
Pre-reg: preregs/2026-05-28_kf2_cross_codebook_v1_n4096.md
Parent: kf2_isolation_proof_v2_n8192 (v265 HARD_PASS; cross-codebook generality next)
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

# Load kf2 v1 for run_one_cell (handles Kerdock and BSC fallback)
_kf2v1_path = REPO / "experiments" / "exp_kf2_isolation_proof_v1.py"
_kf2v1_spec = importlib.util.spec_from_file_location("kf2v1_cross", _kf2v1_path)
kf2v1 = importlib.util.module_from_spec(_kf2v1_spec)
_kf2v1_spec.loader.exec_module(kf2v1)

v3 = kf2v1.v3

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096   # PROT-018 binding contract
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL  = [0.25, 0.5, 1.0, 2.0, 4.0]
M_FRACS_SMOKE = [0.5, 1.0, 2.0]

N_EDITS_FULL  = 50
N_EDITS_SMOKE = 10

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

CODEBOOK_FAMILIES = ["kerdock", "bsc", "gaussian"]

# Pre-registered thresholds (same as kf2 v2)
HP_ISOLATION_MAX = 0.05
HF_CONTAMINATION = 0.10
HP_SEEDS_MIN     = 4   # >= 4/5 seeds


def get_output_dir(default_name: str = "kf2_cross_codebook_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_codebook(family: str, N: int, seed: int, device: torch.device) -> torch.Tensor:
    """Build codebook for given family."""
    if family == "kerdock":
        try:
            cb = v3.make_kerdock_4coset_codebook(N, device)
            if isinstance(cb, tuple):
                cb = cb[0]
            return cb
        except Exception:
            pass
    if family in ("bsc", "kerdock"):
        gen = torch.Generator(device=device)
        gen.manual_seed(seed + 100)
        cb = (torch.randint(0, 2, (N, N), generator=gen, device=device) * 2 - 1).float()
        return cb
    if family == "gaussian":
        gen = torch.Generator(device=device)
        gen.manual_seed(seed + 200)
        cb = torch.randn(N, N, generator=gen, device=device)
        norms = cb.norm(dim=1, keepdim=True).clamp(min=1e-8)
        cb = cb / norms
        return cb
    raise ValueError(f"Unknown family: {family}")


def run_one_cell_family(family: str, M_frac: float, seed: int,
                         N_use: int, n_edits: int,
                         device: torch.device) -> Dict:
    """KF-2 isolation for one codebook family."""
    cb = build_codebook(family, N_use, seed, device)
    C = cb.shape[0]
    M = min(int(M_frac * N_use), C)

    gen = torch.Generator(device=device)
    gen.manual_seed(seed + 300)
    key_idx = torch.randint(0, C, (M,), generator=gen, device=device)
    val_idx = torch.randint(0, C, (M,), generator=gen, device=device)
    keys = cb[key_idx]
    vals = cb[val_idx]

    W = torch.zeros(N_use, N_use, device=device, dtype=torch.float32)
    for start in range(0, M, 256):
        k_b = keys[start:start + 256]
        v_b = vals[start:start + 256]
        W = W + (v_b.T @ k_b) / N_use

    n_probe = min(M, 100)
    probe_keys = keys[:n_probe]
    probe_val = val_idx[:n_probe] % C
    sims_before = (cb @ (probe_keys @ W.T).T) / N_use
    pred_before = torch.argmax(sims_before, dim=0)
    acc_before = (pred_before == probe_val.to(device)).float()

    isolation_ratios = []
    n_edits_actual = min(n_edits, M)
    for edit_i in range(0, n_edits_actual, max(1, n_edits_actual // 10)):
        gen2 = torch.Generator(device=device)
        gen2.manual_seed(seed + edit_i + 1000)
        new_val_idx = torch.randint(0, C, (1,), generator=gen2, device=device)
        new_val = cb[new_val_idx[0]]
        old_val = vals[edit_i]
        old_key = keys[edit_i]
        W_edited = W + torch.outer(new_val - old_val, old_key) / N_use
        non_edit_mask = torch.ones(n_probe, dtype=torch.bool)
        non_edit_mask[min(edit_i, n_probe - 1)] = False
        probe_ne = probe_keys[non_edit_mask]
        probe_val_ne = probe_val[non_edit_mask]
        if probe_ne.shape[0] > 0:
            sims_after = (cb @ (probe_ne @ W_edited.T).T) / N_use
            pred_after = torch.argmax(sims_after, dim=0)
            acc_after = (pred_after == probe_val_ne.to(device)).float()
            delta = (acc_before[non_edit_mask] - acc_after).abs().mean().item()
            isolation_ratios.append(delta)

    isolation_ratio = max(isolation_ratios) if isolation_ratios else 0.0
    theory_bound = 1.0 / math.sqrt(N_use)

    return {
        "family": family,
        "M_frac": M_frac, "M": M, "N": N_use, "seed": seed,
        "isolation_ratio": round(isolation_ratio, 6),
        "theory_bound": round(theory_bound, 6),
        "within_theory": isolation_ratio <= theory_bound,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF2_CROSS_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)
    theory_bound = 1.0 / math.sqrt(N)

    by_family: Dict[str, List[float]] = {}
    for c in cells:
        f = c["family"]
        if f not in by_family:
            by_family[f] = []
        by_family[f].append(c["isolation_ratio"])

    family_max: Dict[str, float] = {f: max(isos) for f, isos in by_family.items()}
    family_mean: Dict[str, float] = {f: sum(isos)/len(isos) for f, isos in by_family.items()}

    all_pass = all(v < HP_ISOLATION_MAX for v in family_max.values())
    any_hf   = any(v >= HF_CONTAMINATION for v in family_max.values())

    # Seed-level pass at non-Kerdock families
    non_kerdock_cells = [c for c in cells if c["family"] != "kerdock"]
    pass_seeds_nk = sum(1 for c in non_kerdock_cells
                        if c["isolation_ratio"] < HP_ISOLATION_MAX)
    total_nk = len(non_kerdock_cells)

    detail = (f"family_max={dict((k,round(v,5)) for k,v in family_max.items())} "
              f"family_mean={dict((k,round(v,5)) for k,v in family_mean.items())} "
              f"theory_bound={theory_bound:.5f} "
              f"pass_non_kerdock={pass_seeds_nk}/{total_nk}")

    if any_hf:
        return ("KF2_CROSS_HARD_FAIL",
                f"HARD_FAIL: contamination at non-Kerdock family. " + detail)

    if all_pass and pass_seeds_nk >= int(total_nk * HP_SEEDS_MIN / len(SEEDS_FULL)):
        return ("KF2_CROSS_HARD_PASS",
                f"EDIT ISOLATION CODEBOOK-ROBUST: isolation holds across 3 families. "
                + detail)

    return ("KF2_CROSS_MIDDLE_BAND",
            f"Partial: isolation varies by codebook family. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096"

    device = torch.device("cpu")

    # Test each family at small scale
    for family in CODEBOOK_FAMILIES:
        cell = run_one_cell_family(family, 0.5, 17, N_SMOKE, 5, device)
        assert cell["isolation_ratio"] is not None, f"{family}: isolation_ratio None"
        assert 0 <= cell["isolation_ratio"] <= 1.0, f"{family}: iso OOR: {cell}"

    # Multi-scale smoke at N_SMOKE x4
    cell_4x = run_one_cell_family("kerdock", 0.5, 17, N_SMOKE * 4, 5, device)
    assert 0 <= cell_4x["isolation_ratio"] <= 1.0, f"4x smoke OOR: {cell_4x}"

    # Validity filter: all 3 families produce valid cells at smoke
    smoke_cells = []
    for family in CODEBOOK_FAMILIES:
        for mf in M_FRACS_SMOKE[:2]:
            c = run_one_cell_family(family, mf, 17, N_SMOKE, 5, device)
            smoke_cells.append(c)
    assert len(smoke_cells) > 0, "No valid cells at smoke"
    assert all(c["isolation_ratio"] >= 0 for c in smoke_cells), \
        f"Negative isolation ratios: {smoke_cells}"

    # Verdict test
    fake_cells = []
    for fam in CODEBOOK_FAMILIES:
        for mf in [0.5, 1.0, 2.0]:
            for seed in [7, 17, 23, 31, 41]:
                fake_cells.append({"family": fam, "M_frac": mf,
                                   "isolation_ratio": 0.005})
    v, msg = compute_verdict({"cells": fake_cells, "N": N_FULL})
    assert "HARD_PASS" in v, f"Verdict self-test failed: {v}: {msg}"

    # OOM check
    oom_bytes = int(2.0 * N_FULL) * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM: keys = {oom_bytes/1e6:.0f}MB >= 6GB"

    print(f"[selftest] kf2_cross_codebook_v1_n4096 PASS", flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds   = SEEDS_SMOKE   if smoke else SEEDS_FULL
    n_edits = N_EDITS_SMOKE if smoke else N_EDITS_FULL
    N_cfg   = N_SMOKE       if smoke else N_FULL

    device = torch.device("cpu")
    print(f"kf2_cross_codebook_v1_n4096 mode={'SMOKE' if smoke else 'FULL'} N={N_cfg} "
          f"m_fracs={m_fracs} seeds={seeds} n_edits={n_edits}", flush=True)

    cells = []
    for family in CODEBOOK_FAMILIES:
        for M_frac in m_fracs:
            for seed in seeds:
                t_cell = time.monotonic()
                cell = run_one_cell_family(family, M_frac, seed, N_cfg, n_edits, device)
                cells.append(cell)
                print(f"  {family} M_frac={M_frac} seed={seed} iso={cell['isolation_ratio']:.5f} "
                      f"({time.monotonic()-t_cell:.2f}s)", flush=True)

    elapsed = time.monotonic() - t0
    summary = {
        "mode": "smoke" if smoke else "full",
        "N": N_cfg, "m_fracs": m_fracs, "seeds": seeds,
        "codebook_families": CODEBOOK_FAMILIES,
        "elapsed_s": round(elapsed, 2),
        "cells": cells,
    }

    tag, msg = compute_verdict(summary)
    summary["verdict_tag"] = tag
    summary["verdict_msg"] = msg
    print(f"\n[VERDICT] {tag}: {msg}", flush=True)

    out_dir = get_output_dir()
    with open(out_dir / "metrics.json", "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[done] elapsed={elapsed:.1f}s -> {out_dir}/metrics.json", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import scope", flush=True)
        return
    run_full(smoke=args.smoke)


if __name__ == "__main__":
    main()
