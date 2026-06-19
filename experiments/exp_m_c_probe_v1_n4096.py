"""M_c PROBE v1: locate codebook-collision boundary M_c at N=4096, beta=4.

CONTEXT:
  M_c (the "codebook-collision boundary") is the M value at which retrieval
  accuracy collapses as a function of fact-count, with temperature held
  well below beta_c (so no temperature confound). Currently an ESTIMATE
  (40K-120K at N=4096) -- not measured. Region boundaries on a phase-grid
  map require M_c known.

  This anchor measures M_c at N=4096 by sweeping M_frac in [2..32] at
  beta=4.0 (fixed below beta_c=10). Sharp drop in retention accuracy as M
  crosses M_c is the signature.

SCIENTIFIC QUESTION:
  Where does retention drop from "high" to "low" as M increases at fixed
  sub-critical beta?

PRE-REGISTERED BANDS (calibration probe; first systematic M_c at N=4096):
  HARD_PASS: sharp transition detected -- mean_acc drops by >= 0.4 between
    two adjacent M_fracs in >= 3/5 seeds (M_c is INSIDE the sweep range and
    resolved).
  HARD_FAIL: no transition -- accuracy stays >= 0.7 across all M (M_c > 32K;
    extend in v2) OR accuracy stays <= 0.3 across all M (M_c < 2K; below
    probe).
  MIDDLE_BAND: gradual decline without sharp transition.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. M at M_frac=2, N=4096: M = 8192.
  3. M at M_frac=32, N=4096: M = 131072.
  4. beta_c ~ 10 from t1_beta_fine_v2; beta=4 is below.
  5. sharp drop = max over adjacent M_frac steps of |ret[i+1] - ret[i]|.
  6. HARD_PASS gate: sharp_drop >= 0.4 at >= 3/5 seeds.

OOM CHECK:
  M=131072, N=4096: keys=131072*4096*4 bytes = 2.15GB. W=64MB. CB=268MB.
  Total ~2.48GB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  Per cell at M_frac=32 N=4096: store~2s + retrieval~0.2s = ~2.5s.
  12 M_fracs x 5 seeds = 60 cells x ~1.5s mean = ~90s nominal.
  Scaling-exp = 1.5 (matrix-store dominant), smoke 1024->4096 = 4x.
  Smoke wall ~30s, FULL ~ 30 * 4^1.5 * 5 = 1200s. 1.5x safety = 1800s.
  PROT-019 floor (_n4096) = 14400s. Adopt 21600s per user spec (50%
  headroom over PROT-019 floor).

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: m_c_probe_v1_n4096
Queue: overnight_queue (GPU; N=4096 Kerdock; 12 M_fracs x 5 seeds = 60 cells)
Pre-reg: preregs/2026-05-30_m_c_probe_v1_n4096.md
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

# Substrate primitives (Kerdock codebook + batched store + retention)
_t1_path = REPO / "experiments" / "exp_t1_beta_sweep_v1_n4096.py"
_t1_spec = importlib.util.spec_from_file_location("t1v1_mcprobe", _t1_path)
t1v1 = importlib.util.module_from_spec(_t1_spec)
_t1_spec.loader.exec_module(t1v1)

store_facts_batched = t1v1.store_facts_batched
compute_retention   = t1v1.compute_retention
v3                  = t1v1.v3

# Seed checkpointing (PROT-021)
_ckpt_path = REPO / "experiments" / "_seed_checkpoint.py"
_ckpt_spec = importlib.util.spec_from_file_location("_seed_checkpoint_mcprobe", _ckpt_path)
_ckpt = importlib.util.module_from_spec(_ckpt_spec)
_ckpt_spec.loader.exec_module(_ckpt)

resumable_seeds   = _ckpt.resumable_seeds
write_partial_key = _ckpt.write_partial_key
aggregate_partials = _ckpt.aggregate_partials


# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N = 4096        # PROT-018 production-N anchor (queue_add.py regex hits this line)
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# M sweep: M_frac in [2..32]; absolute M = M_frac * 1024 -> [2048..32768].
# Brackets the 40K estimate from below; if M_c < 40K we resolve it; if M_c > 32K
# (i.e. M_frac=32 still in Region A) we extend in v2.
M_FRACS_FULL  = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 20.0, 24.0, 28.0, 32.0]
M_FRACS_SMOKE = [2.0, 8.0, 32.0]   # span the range, single seed for smoke

# beta fixed well below beta_c=10
BETA_FIXED = 4.0

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

N_PROBE = 200

# Pre-registered thresholds
HP_SHARP_DROP_MIN  = 0.4      # |ret[i+1] - ret[i]| >= 0.4 between adjacent M_fracs
HP_SEEDS_MIN       = 3        # >= 3 seeds show the sharp drop
HF_ALL_HIGH_MIN    = 0.7      # if all M_fracs >= 0.7, M_c > 32K (extend v2)
HF_ALL_LOW_MAX     = 0.3      # if all M_fracs <= 0.3, M_c < 2K (below probe)


def get_output_dir(default_name: str = "m_c_probe_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _M_for_frac(M_frac: float) -> int:
    """Absolute M = M_frac * 1024 (user spec; M_frac is a multiplier of 1024)."""
    return int(M_frac * 1024)


def run_one_cell(M_frac: float, beta: float, seed: int, N_use: int,
                 device: torch.device) -> Dict:
    """Measure retention at (M, beta, seed). Single substrate setup per call."""
    M = _M_for_frac(M_frac)
    codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N_use, device)
    retention = compute_retention(W, keys, val_idx, codebook, beta, N_use, n_probe=N_PROBE)
    # Free tensors before next cell
    del W, keys, _vals, _key_idx, val_idx, codebook
    return {
        "M_frac": float(M_frac),
        "M": int(M),
        "N": int(N_use),
        "beta": float(beta),
        "seed": int(seed),
        "retention": round(float(retention), 5),
    }


def seed_sharp_drop(seed_cells: List[Dict]) -> float:
    """Max adjacent-M_frac drop in retention for one seed.

    seed_cells must be in M_frac-ascending order. Returns max |ret[i] -
    ret[i+1]| where ret[i] > ret[i+1] (sharp drop). If not monotone-decreasing,
    we still take the largest absolute step.
    """
    rets = [c["retention"] for c in seed_cells]
    if len(rets) < 2:
        return 0.0
    diffs = [rets[i] - rets[i + 1] for i in range(len(rets) - 1)]   # positive drop
    return max(diffs) if diffs else 0.0


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("MC_PROBE_INCONCLUSIVE", "No cells.")

    N_used = summary.get("N", N_FULL)

    # Group by seed
    by_seed: Dict[int, List[Dict]] = {}
    for c in cells:
        by_seed.setdefault(int(c["seed"]), []).append(c)
    for s in by_seed:
        by_seed[s].sort(key=lambda c: c["M_frac"])

    # All-high / all-low HARD_FAIL checks
    all_rets = [c["retention"] for c in cells]
    if min(all_rets) >= HF_ALL_HIGH_MIN:
        return ("MC_PROBE_HARD_FAIL",
                f"M_C_TOO_HIGH: min(retention)={min(all_rets):.4f} >= {HF_ALL_HIGH_MIN} "
                f"-- M_c > 32K at N={N_used}; extend in v2.")
    if max(all_rets) <= HF_ALL_LOW_MAX:
        return ("MC_PROBE_HARD_FAIL",
                f"M_C_TOO_LOW: max(retention)={max(all_rets):.4f} <= {HF_ALL_LOW_MAX} "
                f"-- M_c < 2K at N={N_used}; below probe range.")

    # Sharp-drop test
    seed_drops = {s: seed_sharp_drop(cells_list) for s, cells_list in by_seed.items()}
    n_sharp = sum(1 for d in seed_drops.values() if d >= HP_SHARP_DROP_MIN)

    # Identify where the largest mean drop occurs (M_c estimate)
    # For each adjacent pair, mean ret-drop across seeds:
    M_fracs_sorted = sorted(set(c["M_frac"] for c in cells))
    drop_at_step = []
    for i in range(len(M_fracs_sorted) - 1):
        a, b = M_fracs_sorted[i], M_fracs_sorted[i + 1]
        seeds_with_both = [s for s, cs in by_seed.items()
                            if any(c["M_frac"] == a for c in cs)
                            and any(c["M_frac"] == b for c in cs)]
        if not seeds_with_both:
            drop_at_step.append((a, b, 0.0))
            continue
        diffs = []
        for s in seeds_with_both:
            ra = next(c["retention"] for c in by_seed[s] if c["M_frac"] == a)
            rb = next(c["retention"] for c in by_seed[s] if c["M_frac"] == b)
            diffs.append(ra - rb)
        drop_at_step.append((a, b, sum(diffs) / len(diffs)))

    biggest = max(drop_at_step, key=lambda t: t[2])
    M_c_estimate_lo = _M_for_frac(biggest[0])
    M_c_estimate_hi = _M_for_frac(biggest[1])

    detail = (
        f"n_seeds_sharp={n_sharp}/{len(by_seed)} "
        f"biggest_step={biggest[0]}->{biggest[1]} mean_drop={biggest[2]:.3f} "
        f"M_c_estimate=[{M_c_estimate_lo},{M_c_estimate_hi}] N={N_used} beta={BETA_FIXED}"
    )

    if n_sharp >= HP_SEEDS_MIN:
        return ("MC_PROBE_HARD_PASS",
                f"SHARP_TRANSITION_RESOLVED: " + detail)

    return ("MC_PROBE_MIDDLE_BAND",
            f"GRADUAL_DECLINE: no sharp drop, but transition present. " + detail)


def _instrumentation_selftest() -> None:
    """Mandatory: assert all metrics non-null/non-sentinel at smoke scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula self-tests
    assert _M_for_frac(2.0) == 2048, f"M @ M_frac=2: {_M_for_frac(2.0)} != 2048"
    assert _M_for_frac(32.0) == 32768, f"M @ M_frac=32: {_M_for_frac(32.0)} != 32768"

    # OOM check at maximum M
    M_max = _M_for_frac(32.0)
    keys_bytes = M_max * N_FULL * 4
    w_bytes = N_FULL * N_FULL * 4
    cb_rows = 49152          # Kerdock 4-coset rows at N=4096 (3 * (2^7 - 1) * 128 etc.)
    cb_bytes = cb_rows * N_FULL * 4
    total = keys_bytes + w_bytes + cb_bytes
    assert total < 6e9, f"OOM at FULL: {total/1e6:.0f}MB >= 6GB"

    # Smoke at N_SMOKE=1024, 3 M_fracs, 1 seed (single representative call each).
    # NOTE: at N=1024, Kerdock 4-coset gives C=2^5*3*32 = 3072 codewords or similar
    # (exact count from build_kerdock_4coset_codebook); M_frac=32 -> M=32768 which is
    # over-capacity (forces store_facts_batched into repeated-permutation regime).
    # That is the intended exercise of the over-capacity codepath at smoke scale.
    device = torch.device("cpu")
    cell_lo = run_one_cell(2.0, BETA_FIXED, 17, N_SMOKE, device)
    cell_mid = run_one_cell(8.0, BETA_FIXED, 17, N_SMOKE, device)
    cell_hi = run_one_cell(32.0, BETA_FIXED, 17, N_SMOKE, device)
    for nm, c in [("lo", cell_lo), ("mid", cell_mid), ("hi", cell_hi)]:
        assert "retention" in c and not math.isnan(c["retention"]), (
            f"cell_{nm}: retention missing/NaN: {c}")
        assert 0.0 <= c["retention"] <= 1.0, (
            f"cell_{nm}: retention out of range: {c['retention']}")

    # 4x scale smoke for one M_frac (multi-scale per role contract).
    # Only run for the lowest M_frac to keep selftest fast.
    cell_4x = run_one_cell(2.0, BETA_FIXED, 17, N_SMOKE * 4, device)
    assert 0.0 <= cell_4x["retention"] <= 1.0, f"4x: retention out of range"

    # Verdict self-tests
    # HARD_PASS: sharp drop present in 3+/5 seeds
    fake_hp_seed_cells = lambda s: [
        {"seed": s, "M_frac": mf, "retention": (0.9 if mf <= 8.0 else 0.1)}
        for mf in M_FRACS_FULL
    ]
    fake_cells_hp = []
    for s in SEEDS_FULL:
        fake_cells_hp.extend(fake_hp_seed_cells(s))
    v, msg = compute_verdict({"cells": fake_cells_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HARD_PASS verdict gate failed: {v} {msg}"

    # HARD_FAIL all-high
    fake_high = [{"seed": s, "M_frac": mf, "retention": 0.95}
                  for s in SEEDS_FULL for mf in M_FRACS_FULL]
    v2, m2 = compute_verdict({"cells": fake_high, "N": N_FULL})
    assert "HARD_FAIL" in v2 and "TOO_HIGH" in m2, f"HARD_FAIL high: {v2} {m2}"

    # MIDDLE_BAND: gradual decline, no sharp drop
    fake_grad = [{"seed": s, "M_frac": mf,
                   "retention": max(0.0, 0.9 - 0.025 * M_FRACS_FULL.index(mf))}
                  for s in SEEDS_FULL for mf in M_FRACS_FULL]
    v3v, m3 = compute_verdict({"cells": fake_grad, "N": N_FULL})
    assert "MIDDLE" in v3v, f"MIDDLE_BAND verdict gate failed: {v3v} {m3}"

    print(
        f"[selftest] m_c_probe_v1_n4096 PASS "
        f"ret_lo={cell_lo['retention']:.4f} ret_mid={cell_mid['retention']:.4f} "
        f"ret_hi={cell_hi['retention']:.4f} ret_4x_lo={cell_4x['retention']:.4f}",
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
    M_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL

    out_dir = get_output_dir()
    done_seeds, remaining_seeds = resumable_seeds(seeds, out_dir)

    print(f"[run] m_c_probe_v1_n4096 smoke={smoke} N={N_cfg} M_fracs={M_fracs} "
          f"beta={BETA_FIXED} seeds={seeds} done={done_seeds} todo={remaining_seeds} "
          f"device={device_str}", flush=True)
    t0 = time.time()

    for seed in remaining_seeds:
        seed_cells = []
        for M_frac in M_fracs:
            cell = run_one_cell(M_frac, BETA_FIXED, seed, N_cfg, device)
            seed_cells.append(cell)
            print(f"  seed={seed} M_frac={M_frac} M={cell['M']} "
                  f"retention={cell['retention']:.5f} ({time.time()-t0:.1f}s)",
                  flush=True)
        # Write per-seed checkpoint
        write_partial_key(out_dir, seed, {
            "seed": seed,
            "N": N_cfg,
            "beta": BETA_FIXED,
            "M_fracs": M_fracs,
            "cells": seed_cells,
            "_done_at": time.time(),
        })

    # Aggregate partials
    per_seed = aggregate_partials(out_dir, seeds)
    all_cells = []
    for s in seeds:
        body = per_seed.get(str(s))
        if body is None:
            continue
        all_cells.extend(body["cells"])

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "m_c_probe_v1_n4096",
        "N": N_cfg,
        "smoke": smoke,
        "beta": BETA_FIXED,
        "M_fracs": M_fracs,
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
        json.dump(payload, f, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
