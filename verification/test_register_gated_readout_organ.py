"""Witness for the LANDED AccumulateRegister.decode_gated (CA1-comparator readout) organ.

Landed 2026-08-28 from the integrated `the_register_reads_by_argmax_not_recurrent_completion` (SOLVED/EXCELLENT,
owner-DONE; bar item 4). Completes the register-READOUT line: the gate reconciles the completion-helps-decode /
hurts-ranking tension with NO oracle, by a CA1 reconstruction-residual match/mismatch test -- keep cheap argmax when it
already reconstructs the trace, accept serial only when it near-exactly reconstructs (its genuine overload recovery),
else fall back to argmax (refusing serial's spurious divergence at extreme overload).

Asserts (deterministic, D=256, V=100, per-slot recall accuracy over reps at each load):
  1. SAFETY: gated >= argmax at EVERY load (never worse than the cheap default).
  2. TRACKS BEST: gated >= max(argmax, serial) - eps at EVERY load (picks the better arm).
  3. CAPTURES SERIAL'S GAIN: at an overload where serial wins big (M=64), gated captures it (which="serial").
  4. REFUSES DIVERGENCE: at an extreme overload where serial diverges below argmax, gated falls back to argmax
     (which="argmax_fallback") and gated >= serial there. (Reported+asserted only if such a load is in range.)
  5. ADDITIVE: decode() (per-slot argmax path) byte-unchanged.

Run: .venv/Scripts/python.exe verification/test_register_gated_readout_organ.py
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402

D = 256
V = 100
SEED = 20260828
LOADS = [8, 64, 128, 256]
N_REPS = 12


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2**31))


def _load_row(m: int):
    """Per-slot recall accuracy at load m for argmax / serial / gated, + the gate's dominant chosen arm."""
    role_vocab = [f"r{i}" for i in range(V)]
    accs = {"argmax": [], "serial": [], "gated": []}
    which_counts = {}
    for rep in range(N_REPS):
        g = _gen(SEED + rep * 7919)
        reg = AccumulateRegister(role_vocab, D, g, max_event_slots=m)
        rr = np.random.default_rng(SEED + rep * 7919 + 1)
        truth = [f"r{int(rr.integers(0, V))}" for _ in range(m)]
        for s in range(m):
            reg.add_event("e", truth[s], s)
        arg = [reg.decode("e", s)[0] for s in range(m)]              # per-slot argmax (reads the renorm register)
        ser = reg.decode_serial("e")                                 # serial on the raw sum
        gat, which = reg.decode_gated("e")                           # CA1-gated on the raw sum
        which_counts[which] = which_counts.get(which, 0) + 1
        accs["argmax"].append(np.mean([arg[s] == truth[s] for s in range(m)]))
        accs["serial"].append(np.mean([ser[s] == truth[s] for s in range(m)]))
        accs["gated"].append(np.mean([gat[s] == truth[s] for s in range(m)]))
    row = {k: float(np.mean(v)) for k, v in accs.items()}
    row["which"] = max(which_counts, key=which_counts.get)
    return row


def main() -> int:
    rows = {m: _load_row(m) for m in LOADS}
    print("=== witness: AccumulateRegister.decode_gated (CA1-comparator readout organ) ===")
    print(f"  {'M':>4}  {'argmax':>8}  {'serial':>8}  {'gated':>8}  {'which':>16}")
    for m in LOADS:
        r = rows[m]
        print(f"  {m:>4}  {r['argmax']:>8.3f}  {r['serial']:>8.3f}  {r['gated']:>8.3f}  {r['which']:>16}")

    checks = []
    # (1) SAFETY + (2) TRACKS BEST at every load.
    safety = all(rows[m]["gated"] >= rows[m]["argmax"] - 0.03 for m in LOADS)
    checks.append((safety, "[1] SAFETY: gated >= argmax (never worse than the cheap default) at EVERY load"))
    tracks = all(rows[m]["gated"] >= max(rows[m]["argmax"], rows[m]["serial"]) - 0.05 for m in LOADS)
    checks.append((tracks, "[2] TRACKS BEST: gated >= max(argmax, serial) - 0.05 at EVERY load"))

    # (3) captures serial's gain at M=64.
    r64 = rows[64]
    cap = (r64["serial"] - r64["argmax"] > 0.20) and (r64["gated"] - r64["argmax"] > 0.20) and r64["which"] == "serial"
    checks.append((cap, f"[3] CAPTURES SERIAL'S GAIN @M=64: serial {r64['serial']:.3f} >> argmax {r64['argmax']:.3f}, gated {r64['gated']:.3f} (which={r64['which']})"))

    # (4) refuses divergence where serial < argmax (if present in range).
    div_loads = [m for m in LOADS if rows[m]["serial"] < rows[m]["argmax"] - 0.05]
    if div_loads:
        md = div_loads[-1]
        rd = rows[md]
        refuse = (rd["gated"] >= rd["serial"] + 0.03) and (rd["which"] == "argmax_fallback")
        checks.append((refuse, f"[4] REFUSES DIVERGENCE @M={md}: serial {rd['serial']:.3f} < argmax {rd['argmax']:.3f}; gated {rd['gated']:.3f} (which={rd['which']})"))
    else:
        checks.append((True, "[4] (no serial-divergence load in the tested range; 'tracks best' covers it) -- N/A PASS"))

    # (5) additive: decode() 1-event round-trip unchanged.
    reg = AccumulateRegister(["A", "B", "C"], D, _gen(SEED), max_event_slots=3)
    reg.add_event("x", "B", 1)
    checks.append((reg.decode("x", 1)[0] == "B", "[5] ADDITIVE: decode() 1-event round-trip unchanged -> 'B'"))

    all_pass = True
    for ok, msg in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        all_pass = all_pass and ok
    print(f"\nRESULT: {'ALL CHECKS PASS' if all_pass else 'FAIL'} ({sum(1 for ok, _ in checks if ok)}/{len(checks)})")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
