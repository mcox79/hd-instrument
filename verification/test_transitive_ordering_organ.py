"""Witness for the LANDED hdlab.transitive_ordering.TransitiveOrderingLine (first reasoning organ).

Landed 2026-08-28 from the integrated `transitive_comparison_reasoning_over_the_magnitude_ordering` (SOLVED/EXCELLENT,
owner-DONE). Confirms, scaffold-free on the ACTUAL hdlab organ, the reasoning result the experiment measured
(experiments/exp_transitive_ordering_magnitude_line_v1.py): read pairwise comparisons, integrate them into ONE
magnitude ordering, answer the UN-STATED pair by native FPE read-out (NOT a symbolic sort).

Asserts (deterministic, D=512, multi-seed):
  1. UN-STATED recovery on the ASSOCIATION-MATCHED critical set (both-internal pairs): the magnitude-line organ answers
     un-stated pairs ~1.0, vs the net-win ASSOCIATION floor ~0.5 (the Dusek/Eichenbaum control: on internal pairs
     #wins-#losses gives ZERO signal by construction -> the win is relational INTEGRATION, not associative strength).
  2. INFO-FREE TWIN: shuffling premise directions -> a random ordering -> the organ falls to chance (loses CI-clear).
  3. DISTANCE EFFECT DIRECTION (human signature that rules out chaining): under premise noise, FAR un-stated pairs are
     answered MORE accurately than NEAR ones (a POSITIVE symbolic-distance slope; serial chaining would make far pairs
     HARDER -> negative). Reported + asserted as a directional check.

Run: .venv/Scripts/python.exe verification/test_transitive_ordering_organ.py
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

from hdlab.transitive_ordering import TransitiveOrderingLine  # noqa: E402

D = 512
SEEDS = [0, 1, 2, 3, 4]


def _make_series(n, seed, noise_eps=0.0):
    """True order: item 0 (biggest) .. n-1 (smallest). Stated premises = adjacent (i beats i+1); with prob noise_eps a
    stated premise is FLIPPED. Returns premises=[(winner,loser),...]."""
    rng = np.random.default_rng(seed)
    premises = []
    for i in range(n - 1):
        w, l = i, i + 1
        if rng.random() < noise_eps:
            w, l = l, w
        premises.append((w, l))
    return premises


def _unstated(n, premises):
    stated = set()
    for w, l in premises:
        stated.add((w, l)); stated.add((l, w))
    out = []
    for a in range(n):
        for b in range(a + 1, n):
            if (a, b) in stated:
                continue
            out.append({"a": a, "b": b, "dist": abs(a - b),
                        "both_internal": a not in (0, n - 1) and b not in (0, n - 1)})
    return out


def _netwin_predict(premises, n):
    nw = np.zeros(n)
    for w, l in premises:
        nw[w] += 1; nw[l] -= 1
    return lambda a, b: (1 if nw[a] > nw[b] else (-1 if nw[a] < nw[b] else 0))


def _score(pairs, predict):
    if not pairs:
        return float("nan")
    tot = 0.0
    for pr in pairs:
        a, b = pr["a"], pr["b"]
        truth = 1 if a < b else -1                  # a<b as index => a is bigger => a>b => +1
        pred = predict(a, b)
        tot += 1.0 if pred == truth else (0.5 if pred == 0 else 0.0)
    return tot / len(pairs)


def _line(n, premises, seed):
    line = TransitiveOrderingLine(n, D, torch.Generator().manual_seed(seed * 2654435761 % (2**31)), seed=seed)
    line.integrate(premises, seed=seed)
    return line


def main() -> int:
    n = 7
    # (1) clean-chain un-stated recovery on the association-matched internal pairs vs the net-win floor.
    line_accs, floor_accs = [], []
    for s in SEEDS:
        prem = _make_series(n, s, noise_eps=0.0)
        internal = [p for p in _unstated(n, prem) if p["both_internal"]]
        line = _line(n, prem, s)
        line_accs.append(_score(internal, line.compare))
        floor_accs.append(_score(internal, _netwin_predict(prem, n)))
    line_acc, floor_acc = float(np.mean(line_accs)), float(np.mean(floor_accs))

    # (2) info-free twin: shuffle premise directions.
    twin_accs = []
    for s in SEEDS:
        prem = _make_series(n, s, noise_eps=0.0)
        rng = np.random.default_rng(s + 99)
        prem_tw = [((l, w) if rng.random() < 0.5 else (w, l)) for (w, l) in prem]
        allpairs = _unstated(n, prem)
        twin_accs.append(_score(allpairs, _line(n, prem_tw, s).compare))
    twin_acc = float(np.mean(twin_accs))
    # real line on ALL un-stated pairs (for the twin comparison population)
    real_all = float(np.mean([_score(_unstated(n, _make_series(n, s, 0.0)), _line(n, _make_series(n, s, 0.0), s).compare) for s in SEEDS]))

    # (3) distance-effect direction under noise: far vs near un-stated pairs.
    near_accs, far_accs = [], []
    for s in SEEDS:
        prem = _make_series(n, s, noise_eps=0.25)
        up = _unstated(n, prem)
        line = _line(n, prem, s)
        near = [p for p in up if p["dist"] <= 2]
        far = [p for p in up if p["dist"] >= 4]
        if near:
            near_accs.append(_score(near, line.compare))
        if far:
            far_accs.append(_score(far, line.compare))
    near_acc, far_acc = float(np.mean(near_accs)), float(np.mean(far_accs))

    checks = [
        (line_acc >= 0.95, f"[1] UN-STATED recovery on association-matched internal pairs: line {line_acc:.3f} (>=0.95)"),
        (floor_acc <= 0.65, f"[1b] net-win ASSOCIATION floor is ~chance on internal pairs: {floor_acc:.3f} (<=0.65, zero signal by construction)"),
        (line_acc - floor_acc > 0.25, f"[1c] line beats the association floor by relational INTEGRATION: {line_acc:.3f} vs {floor_acc:.3f} (+{line_acc - floor_acc:.3f})"),
        (real_all - twin_acc > 0.25, f"[2] INFO-FREE TWIN (shuffled premise directions) loses: real {real_all:.3f} vs twin {twin_acc:.3f} (+{real_all - twin_acc:.3f})"),
        (far_acc >= near_acc, f"[3] DISTANCE EFFECT DIRECTION (human; rules out chaining): far {far_acc:.3f} >= near {near_acc:.3f} (positive symbolic-distance slope)"),
    ]

    print("=== witness: hdlab.transitive_ordering.TransitiveOrderingLine (first reasoning organ) ===")
    all_pass = True
    for ok, msg in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        all_pass = all_pass and ok
    print(f"\nRESULT: {'ALL CHECKS PASS' if all_pass else 'FAIL'} ({sum(1 for ok, _ in checks if ok)}/{len(checks)})")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
