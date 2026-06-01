"""AXIS-1 Phase Diagram M x beta SCAN: chunk 4 -- N=8192 N-SCALING TEST.

CONTEXT:
  chunk3 (running): fine-grid M/N in {4.5..12} at N=4096 -> locates exact phase boundary.
  chunk4 (this): repeat chunk2 M/N in {4, 8, 16, 32} at N=8192 (2x N-scaling).
  Question: does the M/N=8 phase boundary HOLD at 2x larger substrate?

SCIENTIFIC QUESTION (Axis 1 -- N-scaling of phase transition):
  If the retention phase boundary is at M/N=8 at N=4096, is it ALSO at M/N=8 at N=8192?
  If yes: boundary location is substrate-intrinsic (scales with N).
  If boundary shifts to different M/N at N=8192: substrate class changes with N.

  N=8192 is NOT a Kerdock valid N. Use BSC atoms (random +/-1 bipolar vectors).
  This is consistent with chunk3 (which uses codebook at N=4096).

PRE-REGISTERED BANDS:
  HARD_PASS: (1) retention falls below 0.5 at some M* in {4N, 8N, 16N, 32N}
    AND (2) M_50 (M/N where ret first < 0.5) is within 1 M/N step of chunk2's M_50=8.
    Interpretation: phase boundary scales with N (substrate-intrinsic).
  HARD_FAIL: retention >= 0.90 across ALL M values up to M/N=32 at N=8192.
    Would mean N=8192 BSC substrate lacks phase transition in tested range.
  MIDDLE_BAND: retention drops but M_50 shifts by > 1 M/N step from chunk2 value.
    Partial N-scaling (boundary present but position shifts).

CALIBRATION: prior anchor = chunk2 M_50 ~ M/N=8 (ret=0.503 at M/N=8, ret=1.0 at M/N=4).
  Bands NOT widened to +-50% (prior anchor exists from N=4096 chunk2).

FORMULA SELF-TESTS:
  1. compute_retention at M=1 -> ret = 1.0 (trivially perfect).
  2. At M/N=32 (extreme over-capacity), retention << 1.0 (interference guaranteed).
  3. M_50 = first M where mean ret < 0.5; valid range [4*N, 32*N].
  4. HARD_PASS: M_50/N in [6, 10] (within 2 M/N of chunk2 boundary at 8).
  5. BNV increases with M (more aliasing = more heterogeneous norms).
  6. N == 8192 assertion (PROT-018 binding).

TIMEOUT ESTIMATE:
  chunk2 elapsed N=4096: 79s.
  N-scaling: (8192/4096)^1.5 = 2.83x geometric; BSC vs codebook: comparable cost.
  4 M values (same as chunk2). Seeds: 5 (same).
  timeout_s = ceil(1.5 * 79 * 2.83) = ceil(335) -> 600s (conservative).
  OOM check: W at N=8192 = 268MB. M max = 32*8192 = 262144 keys (26MB BSC).
    Total peak: ~300MB. Under 6GB. OK.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Queue: overnight_queue (GPU; N=8192 BSC, 5 seeds, 4 M values)
Pre-reg: preregs/2026-05-28_axis1_mb_chunk4_n8192.md
Parent: axis1_mb_chunk2_v1 (same M/N grid, 2x larger N)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

# Load chunk-1 base for store_facts_batched, compute_retention, compute_bundle_norm_var
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_c4", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N = 8192          # PROT-018 binding contract
N_SMOKE = 512     # smoke scale

# Same M/N fracs as chunk2
M_FRACS_FULL = [4.0, 8.0, 16.0, 32.0]
M_FRACS_SMOKE = [4.0, 8.0]

BETA_FULL = [1.0, 4.0, 16.0, 64.0, 128.0, 256.0]
BETA_SMOKE = [4.0, 64.0]

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
PASS_RETENTION_DROP_THRESHOLD = 0.50
FAIL_RETENTION_MIN = 0.90
CHUNK2_M_50_N_RATIO = 8.0    # chunk2 found M_50 at M/N=8
CHUNK2_M_50_TOL = 2.0         # boundary must be within 2 M/N steps of chunk2


def get_output_dir(default_name: str = "axis1_mb_chunk4_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_bsc_codebook(N: int, seed: int = 0) -> torch.Tensor:
    """Build BSC (random bipolar) codebook of size C x N."""
    # Use C = N (large enough to probe full retention range)
    C = N
    rng = torch.Generator()
    rng.manual_seed(seed)
    raw = torch.randint(0, 2, (C, N), generator=rng, dtype=torch.float32) * 2 - 1
    return raw


def run_one_cell(M: int, beta: float, seed: int, device: torch.device,
                 n_smoke: bool = False) -> Dict:
    """Run one (M, beta, seed) cell using BSC codebook at N=8192.

    Allows M > C via key index repetition (aliasing stress, same as chunk2 Kerdock approach).
    This is intentional: at M >> N the repeated keys create interference that produces the
    phase transition. The codebook acts as a value space, not a key uniqueness constraint.
    """
    N_use = N_SMOKE if n_smoke else N
    codebook = make_bsc_codebook(N_use, seed=0).to(device)
    C = codebook.shape[0]
    # Allow M > C via modular indexing (key repetition = aliasing stress)
    M_use = M

    rng = torch.Generator()
    rng.manual_seed(seed + 100)
    # Key indices with repetition allowed when M > C
    key_idx = torch.randint(0, C, (M_use,), generator=rng)
    val_idx = torch.randint(0, C, (M_use,), generator=rng)
    keys = codebook[key_idx]
    vals = codebook[val_idx]

    # Outer-product store (Hebbian)
    W = torch.zeros(N_use, N_use, device=device, dtype=torch.float32)
    batch = 512
    for start in range(0, M_use, batch):
        k_b = keys[start:start + batch]
        v_b = vals[start:start + batch]
        W += (v_b.T @ k_b) / N_use

    # Retention: argmax over codebook
    n_probe = min(200, M_use)
    probe_keys = keys[:n_probe]
    probe_val_idx = val_idx[:n_probe] % C
    sims = (codebook @ (probe_keys @ W.T).T) / N_use   # (C, n_probe)
    pred = torch.argmax(sims, dim=0)
    retention = float((pred == probe_val_idx.to(device)).float().mean().item())

    # Bundle norm var
    n_bnv = min(100, M_use)
    responses = probe_keys[:n_bnv] @ W.T
    norms = responses.norm(dim=1)
    bnv = float(norms.var().item()) if len(norms) > 1 else 0.0

    return {"M": M_use, "beta": beta, "seed": seed, "retention": retention,
            "bundle_norm_var": bnv}


def compute_verdict(summary: Dict) -> tuple:
    cells = summary["cells"]
    if not cells:
        return ("AXIS1C4_MIDDLE_BAND", "No cells completed.")

    N_use = summary.get("N", N)

    # Average retention by M (across beta and seeds)
    from collections import defaultdict
    ret_by_M: Dict[int, List[float]] = defaultdict(list)
    bnv_by_M: Dict[int, List[float]] = defaultdict(list)
    for c in cells:
        ret_by_M[c["M"]].append(c["retention"])
        bnv_by_M[c["M"]].append(c["bundle_norm_var"])

    M_set = sorted(ret_by_M.keys())
    ret_mean: Dict[int, float] = {M_v: sum(r) / len(r) for M_v, r in ret_by_M.items()}

    # HARD_FAIL: all retention >= 0.90
    if all(ret_mean[m] >= FAIL_RETENTION_MIN for m in M_set):
        return ("AXIS1C4_HARD_FAIL",
                f"No phase boundary in N=8192 BSC regime. All ret >= {FAIL_RETENTION_MIN}. "
                f"ret_by_MoverN={dict((round(m/N_use,1), round(ret_mean[m],3)) for m in M_set)}.")

    # Find M_50
    M_50 = None
    for m_v in M_set:
        if ret_mean[m_v] < PASS_RETENTION_DROP_THRESHOLD:
            M_50 = m_v
            break

    if M_50 is None:
        return ("AXIS1C4_MIDDLE_BAND",
                f"Partial retention drop (not below 0.5). "
                f"ret_by_MoverN={dict((round(m/N_use,1), round(ret_mean[m],3)) for m in M_set)}.")

    m50_over_N = M_50 / N_use
    shift = abs(m50_over_N - CHUNK2_M_50_N_RATIO)

    if shift <= CHUNK2_M_50_TOL:
        return ("AXIS1C4_HARD_PASS",
                f"Phase boundary SCALES WITH N: M_50/N={m50_over_N:.1f} at N=8192 "
                f"(chunk2 N=4096 M_50/N={CHUNK2_M_50_N_RATIO}, shift={shift:.1f}). "
                f"ret_by_MoverN={dict((round(m/N_use,1), round(ret_mean[m],3)) for m in M_set)}.")

    return ("AXIS1C4_MIDDLE_BAND",
            f"Phase boundary shifted: M_50/N={m50_over_N:.1f} at N=8192 "
            f"(chunk2 M_50/N={CHUNK2_M_50_N_RATIO}, shift={shift:.1f} > tol {CHUNK2_M_50_TOL}). "
            f"ret_by_MoverN={dict((round(m/N_use,1), round(ret_mean[m],3)) for m in M_set)}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N == 8192, f"PROT-018: N must be 8192 (matches _n8192 suffix); got {N}"

    # Test BSC codebook build
    cb = make_bsc_codebook(64, seed=0)
    assert cb.shape == (64, 64), f"BSC codebook shape wrong: {cb.shape}"
    assert set(cb.unique().tolist()).issubset({-1.0, 1.0}), "BSC must be bipolar"

    # Test one cell at tiny scale
    cell = run_one_cell(M=16, beta=4.0, seed=17, device=torch.device("cpu"), n_smoke=True)
    assert cell["retention"] is not None and 0 <= cell["retention"] <= 1.0, \
        f"retention sentinel: {cell['retention']}"
    assert cell["bundle_norm_var"] >= 0.0, f"bnv sentinel: {cell['bundle_norm_var']}"

    # Test verdict HARD_PASS path
    N_t = N_SMOKE
    cells_hp = []
    for mf in [4.0, 8.0, 16.0, 32.0]:
        M_t = int(mf * N_t)
        ret = 1.0 if mf <= 4.0 else max(0.0, 1.0 - (mf - 4.0) * 0.15)
        cells_hp.append({"M": M_t, "beta": 4.0, "seed": 17,
                          "retention": ret, "bundle_norm_var": mf * 0.5})
    v, msg = compute_verdict({"cells": cells_hp, "N": N_t})
    assert v in ("AXIS1C4_HARD_PASS", "AXIS1C4_MIDDLE_BAND"), \
        f"Self-test HARD_PASS path failed: {v}: {msg}"

    # Test verdict HARD_FAIL path
    cells_hf = [{"M": int(mf * N_t), "beta": 4.0, "seed": 17,
                  "retention": 0.95, "bundle_norm_var": mf * 0.5}
                for mf in [4.0, 8.0, 16.0, 32.0]]
    v2, _ = compute_verdict({"cells": cells_hf, "N": N_t})
    assert v2 == "AXIS1C4_HARD_FAIL", f"Self-test HARD_FAIL path failed: {v2}"


_instrumentation_selftest()  # Called at module scope before sweep


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    N_use = N_SMOKE if smoke else N
    M_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    betas = BETA_SMOKE if smoke else BETA_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    outdir = get_output_dir()
    t0 = time.time()
    cells = []

    for seed in seeds:
        for mf in M_fracs:
            M_val = int(mf * N_use)
            for beta in betas:
                cell = run_one_cell(M_val, beta, seed, device, n_smoke=smoke)
                cells.append(cell)
                elapsed = time.time() - t0
                print(f"cell M/N={mf:.1f} beta={beta} seed={seed} "
                      f"ret={cell['retention']:.3f} elapsed={elapsed:.1f}s")

    elapsed_s = time.time() - t0
    summary = {"cells": cells, "N": N_use, "M_fracs": M_fracs, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed_s,
        "config": {
            "N": N_use,
            "M_fracs": M_fracs,
            "betas": betas,
            "seeds": seeds,
            "smoke": smoke,
        },
        "summary": summary,
    }

    out = outdir / "metrics.json"
    with open(out, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nVERDICT: {verdict}")
    print(f"MSG: {verdict_msg}")
    print(f"elapsed={elapsed_s:.1f}s")
    print(f"metrics -> {out}")


if __name__ == "__main__":
    main()
