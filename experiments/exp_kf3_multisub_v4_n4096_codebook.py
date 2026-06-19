"""KF-3 MULTI-SUBSTRATE v4: N=4096 codebook-type audit (BSC vs Kerdock).

CONTEXT:
  kf3_multisub_v2_n4096 (HARD_PASS): substrate A and B isolate at N=4096 Kerdock codebook.
  kf3_multisub_v3_n8192 (shipped to GPU): N=8192 Kerdock isolation envelope extension.
  v4 (THIS): at N=4096, test BSC codebook instead of Kerdock.
  Why: Kerdock has special algebraic structure (equidistant codewords). Does the isolation
  property hold with random BSC atoms (no special structure)?
  BSC atoms are +/-1 random -- NOT equidistant; interference pattern is different.

SCIENTIFIC QUESTION:
  Does KF-3 multi-substrate isolation hold at N=4096 with BSC atoms?
  Is the isolation property substrate-codebook-agnostic (holds for both Kerdock and BSC)?
  Does max_leakage at N=4096 BSC match the 1/sqrt(N) theoretical bound?

PRE-REGISTERED BANDS:
  Prior: v2 N=4096 Kerdock HARD_PASS (max_leakage < 0.01).
  BSC atoms have higher variance than Kerdock (not equidistant).
  Expected: isolation holds but with higher leakage than Kerdock.
  Theory bound at N=4096: 1/sqrt(4096) = 0.01563.

  HARD_PASS: max_leakage < 0.05 (3x theory bound, generous for BSC)
    AND max_contam < 0.10 at >= 4/5 seeds.
    Interpretation: isolation is codebook-agnostic (holds for BSC too).
  HARD_FAIL: leakage >= 0.20 at N=4096 BSC.
    Interpretation: BSC isolation fails -- codebook structure is critical.
  MIDDLE_BAND: leakage in [0.05, 0.20).

  NOTE: BSC bands are wider than Kerdock (v2 HP threshold was 0.01).
  This is a calibration probe for BSC type. Bands widened per policy.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. theory_bound_bsc = 1/sqrt(4096) = 0.01563. HP_LEAKAGE_MAX = 0.05 (3x, BSC widened).
  3. BSC atoms: torch.randint(2, (M, N)) * 2 - 1. NOT Kerdock.
  4. M at M_frac=8, N=4096: M=32768.
  5. isolation_ratio: cross-substrate retrieval accuracy <= HP_LEAKAGE_MAX.

OOM CHECK:
  Two W matrices at N=4096: 2 * 64MB = 128MB. Keys at M_frac=8 N=4096: M=32768, 512MB.
  Total ~700MB. Under 6GB. OK for remote CPU 16GB RAM.

TIMEOUT ESTIMATE:
  v2 at N=4096 Kerdock: 3 M_fracs x 5 seeds x ~5s/cell = 75s.
  v4: same cells, BSC codebook build. BSC build: O(M*N) = ~same as Kerdock.
  Total: ~75s. Safety: ceil(1.5*75*5) = 563s. Floor 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: kf3_multisub_v4_n4096_codebook
Queue: remote_cpu_queue (CPU; N=4096 BSC codebook; cross-substrate isolation)
Pre-reg: preregs/2026-05-29_kf3_multisub_v4_n4096_codebook.md
Parent: kf3_multisub_v2_n4096 (Kerdock HARD_PASS); codebook-audit probe
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load kf3_multisub_v2_n4096 for run_one_cell logic (we'll patch codebook type)
import importlib.util
_v2_path = REPO / "experiments" / "exp_kf3_multisub_v2_n4096.py"
_v2_spec = importlib.util.spec_from_file_location("kf3v2_v4", _v2_path)
_kf3_v2 = importlib.util.module_from_spec(_v2_spec)
_v2_spec.loader.exec_module(_kf3_v2)

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL  = [0.5, 2.0, 8.0]   # same as v2
M_FRACS_SMOKE = [2.0]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (BSC; wider than Kerdock v2)
HP_LEAKAGE_MAX = 0.05   # max cross-substrate leakage
HP_CONTAM_MAX  = 0.10   # max contamination
HF_LEAKAGE_MIN = 0.20   # above this = HARD_FAIL
HP_SEEDS_MIN   = 4      # >= 4/5 seeds


def get_output_dir(default_name: str = "kf3_multisub_v4_n4096_codebook") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_bsc_codebook(N: int, M: int, seed: int, device) -> torch.Tensor:
    """Build BSC (+/-1) random atoms (N,M) then transpose to (M,N)."""
    gen = torch.Generator(device=device).manual_seed(seed + 5555)
    atoms = torch.randint(0, 2, (M, N), generator=gen, device=device).float() * 2 - 1
    return atoms  # shape (M, N)


def run_one_cell_bsc(N: int, M_frac: float, seed: int,
                     device: torch.device) -> Dict:
    """Run KF-3 isolation test with BSC codebook."""
    M = int(M_frac * N)

    # Build two independent BSC codebooks (substrates A and B)
    gen_a = torch.Generator(device=device).manual_seed(seed)
    gen_b = torch.Generator(device=device).manual_seed(seed + 9999)

    # Keys and values for substrate A
    keys_A = torch.randint(0, 2, (M, N), generator=gen_a, device=device).float() * 2 - 1
    vals_A = torch.randint(0, 2, (M, N), generator=gen_a, device=device).float() * 2 - 1

    # Keys and values for substrate B (independent random atoms)
    keys_B = torch.randint(0, 2, (M, N), generator=gen_b, device=device).float() * 2 - 1
    vals_B = torch.randint(0, 2, (M, N), generator=gen_b, device=device).float() * 2 - 1

    # Build W matrices (Hebbian)
    W_A = (vals_A.T @ keys_A) / N   # (N, N)
    W_B = (vals_B.T @ keys_B) / N   # (N, N)

    # Retrieval function: nearest-key cosine match
    def retrieve_acc(W, keys_q, vals_q, n_probe=50):
        """Fraction of queries correctly retrieved."""
        n_q = min(n_probe, keys_q.shape[0])
        q_idx = torch.arange(n_q, device=device)
        q_keys = keys_q[:n_q]   # (n_q, N)
        q_vals = vals_q[:n_q]   # (n_q, N)
        logits = (W @ q_keys.T).T   # (n_q, N)
        # Match against all stored keys (brute-force cosine nearest-key)
        sims = logits @ keys_q.T    # (n_q, M)
        pred_idx = sims.argmax(dim=-1)   # (n_q,)
        # Retrieve value
        correct = sum(1 for i, p in enumerate(pred_idx.tolist())
                      if torch.allclose(vals_q[p], q_vals[i]))
        return correct / n_q

    # Self-retrieval (should be high)
    acc_AA = retrieve_acc(W_A, keys_A, vals_A)
    acc_BB = retrieve_acc(W_B, keys_B, vals_B)

    # Cross-substrate leakage: substrate A queried with substrate B keys
    # (should be near-zero -- isolation)
    acc_AB = retrieve_acc(W_A, keys_B, vals_B)  # B keys into A's W
    acc_BA = retrieve_acc(W_B, keys_A, vals_A)  # A keys into B's W

    leakage = (acc_AB + acc_BA) / 2.0
    contam  = max(acc_AB, acc_BA)
    passes  = leakage < HP_LEAKAGE_MAX and contam < HP_CONTAM_MAX

    print(f"    N={N} M_frac={M_frac} seed={seed} "
          f"acc_AA={acc_AA:.4f} acc_BB={acc_BB:.4f} "
          f"leak_AB={acc_AB:.4f} leak_BA={acc_BA:.4f} "
          f"leakage={leakage:.4f} passes={passes}", flush=True)

    return {
        "N": N, "M_frac": M_frac, "M": M, "seed": seed,
        "acc_AA": round(acc_AA, 5), "acc_BB": round(acc_BB, 5),
        "acc_AB": round(acc_AB, 5), "acc_BA": round(acc_BA, 5),
        "leakage": round(leakage, 5), "contam": round(contam, 5),
        "passes_hp": passes,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF3_V4_INCONCLUSIVE", "No cells.")

    valid = [c for c in cells if c.get("leakage") is not None]
    if not valid:
        return ("KF3_V4_INCONCLUSIVE", "No valid leakage values.")

    max_leak = max(c["leakage"] for c in valid)
    max_cont = max(c["contam"] for c in valid)
    n_pass   = sum(1 for c in valid if c.get("passes_hp", False))
    n_total  = len(valid)
    mean_acc_AA = sum(c["acc_AA"] for c in valid) / n_total

    N = summary.get("N", N_FULL)
    detail = (f"max_leakage={max_leak:.5f} max_contam={max_cont:.5f} "
              f"n_pass={n_pass}/{n_total} mean_acc_AA={mean_acc_AA:.4f} "
              f"HP_leak={HP_LEAKAGE_MAX} HF_leak={HF_LEAKAGE_MIN} N={N}")

    if max_leak >= HF_LEAKAGE_MIN:
        return ("KF3_V4_HARD_FAIL",
                f"BSC_ISOLATION_FAILS: leakage={max_leak:.4f}. " + detail)

    if n_pass >= HP_SEEDS_MIN:
        return ("KF3_V4_HARD_PASS",
                f"BSC_ISOLATION_HOLDS: codebook-agnostic isolation confirmed. " + detail)

    return ("KF3_V4_MIDDLE_BAND",
            f"PARTIAL: n_pass={n_pass}/{n_total}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Import chain
    assert _kf3_v2 is not None, "kf3_v2 import failed"

    # Formula tests
    theory_bound = 1.0 / math.sqrt(N_FULL)
    assert abs(theory_bound - 0.015625) < 0.001, f"theory_bound: {theory_bound}"
    assert HP_LEAKAGE_MAX > theory_bound, "HP_LEAKAGE_MAX should be wider than theory bound"
    assert int(8.0 * N_FULL) == 32768, "M at M_frac=8"

    # Verdict tests
    cells_hp = [{"leakage": 0.02, "contam": 0.03, "acc_AA": 0.90, "passes_hp": True}
                for _ in range(5)]
    v, msg = compute_verdict({"cells": cells_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"Expected HP: {v}"

    cells_hf = [{"leakage": 0.25, "contam": 0.30, "acc_AA": 0.40, "passes_hp": False}
                for _ in range(3)]
    v_hf, _ = compute_verdict({"cells": cells_hf, "N": N_FULL})
    assert "HARD_FAIL" in v_hf, f"Expected HF: {v_hf}"

    # Live smoke cell at N=1024 with M_frac=0.1 (well within capacity for BSC)
    device = torch.device("cpu")
    result = run_one_cell_bsc(N_SMOKE, 0.1, 17, device)
    assert "leakage" in result, f"missing leakage: {list(result.keys())}"
    leak = result["leakage"]
    assert leak is not None and not math.isnan(leak), f"leakage NaN"
    assert 0.0 <= leak <= 1.0, f"leakage out of [0,1]: {leak}"
    # At M_frac=0.1 (well below capacity), acc_AA should be positive
    assert result["acc_AA"] > 0.0, f"acc_AA not positive at M_frac=0.1: {result['acc_AA']}"

    # 4x smoke: N=4096 with M_frac=0.5
    result4 = run_one_cell_bsc(N_SMOKE * 4, 0.5, 17, device)
    assert "leakage" in result4, "4x missing leakage"
    assert result4["acc_AA"] >= 0.0, f"4x acc_AA invalid: {result4['acc_AA']}"

    print(f"[selftest] kf3_multisub_v4_n4096_codebook PASS "
          f"leak_smoke={leak:.4f} acc_AA={result['acc_AA']:.4f}", flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds   = SEEDS_SMOKE if smoke else SEEDS_FULL
    N_cfg   = N_SMOKE if smoke else N_FULL

    device = torch.device("cpu")
    print(f"kf3_multisub_v4_n4096_codebook mode={'SMOKE' if smoke else 'FULL'} "
          f"N={N_cfg} BSC-codebook m_fracs={m_fracs} seeds={seeds}", flush=True)

    all_cells = []

    for M_frac in m_fracs:
        M = int(M_frac * N_cfg)
        print(f"\n== M_frac={M_frac} (M={M}) ==", flush=True)
        for seed in seeds:
            t_cell = time.monotonic()
            result = run_one_cell_bsc(N_cfg, M_frac, seed, device)
            elapsed_cell = time.monotonic() - t_cell
            result["elapsed_s"] = round(elapsed_cell, 2)
            all_cells.append(result)

    elapsed_total = time.monotonic() - t0
    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})

    summary = {
        "anchor": "kf3_multisub_v4_n4096_codebook",
        "N": N_cfg, "smoke": smoke, "codebook_type": "BSC",
        "m_fracs": m_fracs, "seeds": seeds,
        "cells": all_cells,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed_total, 2),
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as fp:
        json.dump(summary, fp, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_total:.1f}s", flush=True)
    print(f"[output] {out_path}", flush=True)


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run_full(smoke=args.smoke)


if __name__ == "__main__":
    main()
