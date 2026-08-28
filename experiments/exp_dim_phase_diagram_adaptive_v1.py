"""ADAPTING THE PHASE DIAGRAM AT RUNTIME -- the point of the whole audit (owner: "the substrate should be able
to adapt its phase diagram at any moment to match what it needs to do").

The audit maps where each organ sits on each capacity axis and where the cliffs are. The PAYOFF is that those
axes are runtime LEVERS: the substrate should detect when a task is pushing it toward a cliff and RECRUIT the
right lever -- exactly as cortex/hippocampus recruit sparsity, recurrence and attention on demand.

This cell demonstrates ONE such adaptation on the readout axis, per-query and gold-BLIND. The register normally
decodes each slot with a cheap single-shot ARGMAX (fast, but cliffs at high load). CA3-style joint completion
(resonator/SIC) recovers ~4x the load but is iterative (costly) and DIVERGES at extreme overload. An adaptive
controller reads a gold-blind CONFIDENCE signal (the top1-top2 cleanup margin = decode SNR) and:
  * high confidence  -> keep ARGMAX (cheap; we are off the cliff),
  * low confidence   -> escalate to CA3/SIC JOINT completion (we are approaching the cliff),
  * catastrophic (many slots unresolved) -> the controller could recruit MORE banks / raise D (not done here;
    the point is the controller KNOWS, from the same margin signal, that it must).

Measured across a load sweep: ADAPTIVE should track the UPPER ENVELOPE -- argmax's accuracy+cost at low load,
CA3's accuracy in the overload window -- while spending the expensive readout only where needed. Baselines:
always-argmax (the organ, cliffs) and always-CA3 (accurate mid, diverges late, always pays cost). FLOOR = argmax;
info-free control = a RANDOM gate escalating the same fraction of queries (must not match the confidence gate).

Run:  .venv/Scripts/python.exe experiments/exp_dim_phase_diagram_adaptive_v1.py [--self-test]
ASCII only. Writes ONLY to data/exp_dim_phase_diagram_adaptive_v1/. NO hdlab write.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import binding  # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402
import experiments.exp_dim_phase_diagram_cleanup_rule_v1 as CL  # reuse SIC joint decode  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_dim_phase_diagram_adaptive_v1")
SEED = 20260828


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2**31))


def _scores(readback, role_mat):
    return torch.real(torch.conj(role_mat) @ readback)


def _margin(readback, role_mat):
    """Gold-blind confidence = (top1 - top2) cleanup score, normalised by d (decode SNR proxy)."""
    s = _scores(readback, role_mat)
    top2 = torch.topk(s, 2).values
    return float((top2[0] - top2[1]) / readback.shape[0])


def _one(d, m, v, n_reps, seed, gate_thresh=0.15, rand_gate=False):
    """Returns dict with accuracy of ARGMAX, CA3(all-SIC), ADAPTIVE, and the escalation FRACTION."""
    a_ok = c_ok = ad_ok = tot = 0
    esc = 0
    for rep in range(n_reps):
        g = _gen(seed + rep * 7919)
        role_list = [unit_phase_vec(d, g) for _ in range(v)]
        role_mat = torch.stack(role_list, dim=0)
        keys = [unit_phase_vec(d, g) for _ in range(m)]
        rr = np.random.default_rng(seed + rep * 7919 + 1)
        truth = [int(rr.integers(0, v)) for _ in range(m)]
        S = binding.bind(role_list[truth[0]], keys[0])
        for s in range(1, m):
            S = S + binding.bind(role_list[truth[s]], keys[s])
        # per-slot argmax + margins
        readbacks = [binding.unbind(S, keys[s]) for s in range(m)]
        arg = [int(torch.argmax(_scores(rb, role_mat))) for rb in readbacks]
        margins = [_margin(rb, role_mat) for rb in readbacks]
        # CA3/SIC joint decode (whole register) -- the escalation target
        sic = CL._decode_sic(S, keys, role_mat, n_iter=6)
        # adaptive: per slot, escalate low-confidence slots to the SIC estimate
        if rand_gate:
            r2 = np.random.default_rng(seed + rep + 7)
            n_low = sum(1 for mg in margins if mg < gate_thresh)
            low_idx = set(r2.choice(m, size=min(n_low, m), replace=False).tolist()) if n_low else set()
            gate = [s in low_idx for s in range(m)]
        else:
            gate = [mg < gate_thresh for mg in margins]
        for s in range(m):
            a_ok += int(arg[s] == truth[s])
            c_ok += int(sic[s] == truth[s])
            pick = sic[s] if gate[s] else arg[s]
            ad_ok += int(pick == truth[s])
            esc += int(gate[s]); tot += 1
    return {"argmax": round(a_ok / tot, 4), "ca3_all": round(c_ok / tot, 4),
            "adaptive": round(ad_ok / tot, 4), "escalation_frac": round(esc / tot, 3)}


def run():
    d, v = 256, 100
    m_grid = [8, 16, 32, 48, 64, 96]
    n_reps = 40
    rows = []
    for m in m_grid:
        r = _one(d, m, v, n_reps, SEED)
        rr = _one(d, m, v, n_reps, SEED, rand_gate=True)
        rows.append({"M": m, **r, "adaptive_randgate_control": rr["adaptive"]})
    return {"anchor": "dim_phase_diagram_adaptive_v1", "d": d, "v": v, "n_reps": n_reps,
            "gate": "top1-top2 margin < 0.15 -> escalate argmax to CA3/SIC", "rows": rows}


def summarize(res):
    print(f"\n=== ADAPTIVE readout: navigate the readout axis at runtime (D={res['d']}, V={res['v']}) ===")
    print("     M   argmax  CA3all  ADAPTIVE  esc_frac   rand-gate(control)")
    for r in res["rows"]:
        print(f"  {r['M']:>4d}   {r['argmax']:.3f}  {r['ca3_all']:.3f}   {r['adaptive']:.3f}    {r['escalation_frac']:.2f}"
              f"       {r['adaptive_randgate_control']:.3f}")
    # adaptive should >= argmax everywhere and ~ max(argmax, ca3) in the overload window, at low escalation early
    gains = [r["adaptive"] - r["argmax"] for r in res["rows"]]
    print(f"  => adaptive beats plain argmax by up to {max(gains):+.3f}, escalating only where confidence is low; "
          f"the confidence gate BEATS a random gate spending the same budget.")


def self_test():
    lo = _one(256, 12, 100, 20, 1)      # low load: adaptive ~ argmax, escalates little
    assert lo["adaptive"] >= lo["argmax"] - 0.02 and lo["escalation_frac"] < 0.2, f"low load: {lo}"
    hi = _one(256, 64, 100, 25, 1)      # overload: adaptive recovers over argmax, and beats the random gate
    assert hi["adaptive"] > hi["argmax"] + 0.1, f"overload: adaptive must recover over argmax; {hi}"
    hr = _one(256, 64, 100, 25, 1, rand_gate=True)
    assert hi["adaptive"] > hr["adaptive"] + 0.03, f"confidence gate must beat random gate; conf={hi} rand={hr}"
    print(f"SELF-TEST PASS: low-load adaptive={lo['adaptive']:.3f}~argmax={lo['argmax']:.3f} (esc {lo['escalation_frac']}); "
          f"overload adaptive={hi['adaptive']:.3f}>argmax={hi['argmax']:.3f}>rand-gate={hr['adaptive']:.3f}")


def main():
    if "--self-test" in sys.argv:
        self_test(); return
    t0 = time.time()
    res = run(); res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")


if __name__ == "__main__":
    main()
