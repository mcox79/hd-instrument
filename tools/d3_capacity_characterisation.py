"""INSTRUMENT CHARACTERISATION for D3 (hippocampal one-shot write / index).

PROMOTED FROM scratch/ 2026-08-21, per the CLAUDE.md scratch corollary and the precedent ORGAN_MAP
records for tools/orthographic_floor_vet_v1.py: scratch/ is gitignored, so a diagnostic left there
is a diagnostic deleted. Three separate times this same night an experiment was found to have kept
only the summary it needed and lost the population it scored. This file IS the population: seeds are
fixed (7/11/13) and nothing here calls an unseeded RNG, so `python tools/d3_capacity_
characterisation.py` reproduces every number in the note below it, exactly, in one command.
Findings written up in notes/D3s_QUEUED_TEST_SWEEPS_THE_WRONG_VARIABLE_*.md.

THIS IS NOT THE D3 EXPERIMENT AND MUST NOT BE REPORTED AS ONE. No verdict is issued, nothing
touches the live anchor field, and the patterns are synthetic. Its ONLY job is to tell whoever
authors the D3 cell where the sweep should go and which knob actually moves the score.

WHY IT EXISTS. ORGAN_MAP's D3 can-fail test says "one-shot cued recall of N stored (context ->
lemma) pairs from the live anchor field after a SINGLE exposure, SWEEPING N TO FIND THE COLLAPSE
POINT". The organ's own 14/14 self-test reports one-shot recall at sign_agree = 1.000, which
ORGAN_MAP itself calls "a 14/14 self-test with no comparator" -- a ceiling at tiny N, not a
capability. So: where IS the collapse point?

WHAT IT FOUND (three arms, all below):
  ARM 1  sweep N with an EXACT cue           -> hit@1 = 1.0000 at EVERY N from 1 to 2000, sd 0.0000.
  ARM 2  the same with CA3 SWITCHED OFF      -> IDENTICAL 1.0000. The DG projection alone solves it.
  ARM 3  degrade the cue instead of the load -> the score finally moves, and CA3 is STILL never
                                                better than CA3-off (deltas 0 to -0.0480).
CONSEQUENCE: with an exact cue the task is solved by a deterministic injective encoding and
nearest-neighbour lookup, with NO memory involved. N is the wrong sweep variable. The knob that
moves the score is CUE DEGRADATION.

FLOOR NOTE, recorded because it is a trap: a "no-write" floor that zeroes W is DEGENERATE here --
settle() computes sign(W @ cue), so W = 0 returns the zero vector and the arm collapses for a
reason unrelated to memory. It looks like a working floor and is not one. ARM 2 (use_ca3=False) is
the informative control, because it removes the mechanism while leaving the pipeline intact.

PARAMETER vs COMPUTATION: sparsity is swept, never adopted -- ours (0.02, mid of the 0.01-0.03 band)
AND the pinned MTL 0.2% (Waydo 2006), because this project's own record says the pinned band was the
WORST point in its own sweep.

SCOPE LIMIT, stated because it bounds every number here: the patterns are i.i.d. random bipolar
vectors, which are near-orthogonal. Real (context -> lemma) pairs are CORRELATED, and DG pattern
separation exists precisely to decorrelate them -- so the real task is harder and these numbers do
not transfer to it. What DOES transfer is the structural point: an exact cue regenerates its own DG
code deterministically, whatever the inputs are.
"""
import json
import sys
import time

import numpy as np

sys.path.insert(0, ".")
from hdlab.hippocampal_encoder import HippocampalEncoder  # noqa: E402

INPUT_DIM = 256          # the live path's d
DG_DIM = 2048
N_GRID = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000]
SPARSITIES = [0.02, 0.002]
SEEDS = [7, 11, 13]
FLIPS = [0.0, 0.10, 0.25, 0.40]
N_FOR_FLIP = [100, 500, 2000]


def _hit1(enc, codes_norm, Q, use_ca3, n):
    out = enc.retrieve(Q, use_ca3=use_ca3)
    A = out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-12)
    return float(((A @ codes_norm.T).argmax(axis=1) == np.arange(n)).mean())


def _build(N, sparsity, seed):
    rng = np.random.default_rng(seed)
    X = rng.choice([-1.0, 1.0], size=(N, INPUT_DIM))
    enc = HippocampalEncoder(INPUT_DIM, DG_DIM, sparsity, seed=seed)
    codes = enc.encode_and_write(X)
    return rng, X, enc, codes / (np.linalg.norm(codes, axis=1, keepdims=True) + 1e-12)


def main():
    t0 = time.time()
    arm12 = []
    for sparsity in SPARSITIES:
        for N in N_GRID:
            on, off = [], []
            for seed in SEEDS:
                _, X, enc, B = _build(N, sparsity, seed)
                on.append(_hit1(enc, B, X, True, N))
                off.append(_hit1(enc, B, X, False, N))
            arm12.append({"sparsity": sparsity, "N": N,
                          "hit1_ca3_on": float(np.mean(on)), "sd_on": float(np.std(on)),
                          "hit1_ca3_off": float(np.mean(off)),
                          "delta_on_minus_off": float(np.mean(on) - np.mean(off)),
                          "per_seed_on": on, "per_seed_off": off, "chance": 1.0 / N})
            print(f"[exact cue] sparsity={sparsity:<6} N={N:<5} CA3_ON={np.mean(on):.4f} "
                  f"CA3_OFF={np.mean(off):.4f} delta={np.mean(on)-np.mean(off):+.4f}", flush=True)

    arm3 = []
    for N in N_FOR_FLIP:
        for flip in FLIPS:
            on, off = [], []
            for seed in SEEDS:
                rng, X, enc, B = _build(N, 0.02, seed)
                Q = X.copy()
                if flip > 0:
                    Q[rng.random(Q.shape) < flip] *= -1
                on.append(_hit1(enc, B, Q, True, N))
                off.append(_hit1(enc, B, Q, False, N))
            arm3.append({"N": N, "flip": flip,
                         "hit1_ca3_on": float(np.mean(on)), "hit1_ca3_off": float(np.mean(off)),
                         "delta_on_minus_off": float(np.mean(on) - np.mean(off)),
                         "per_seed_on": on, "per_seed_off": off})
            print(f"[degraded]  N={N:<5} flip={flip:<5.2f} CA3_ON={np.mean(on):.4f} "
                  f"CA3_OFF={np.mean(off):.4f} delta={np.mean(on)-np.mean(off):+.4f}", flush=True)

    deltas = [r["delta_on_minus_off"] for r in arm12 + arm3]
    out = {
        "WHAT_THIS_IS": "instrument characterisation for D3, NOT the D3 experiment; no verdict",
        "input_dim": INPUT_DIM, "dg_dim": DG_DIM, "seeds": SEEDS, "elapsed_s": time.time() - t0,
        "SCOPE_LIMIT": "i.i.d. random bipolar patterns (near-orthogonal); real context->lemma pairs "
                       "are correlated and harder. Numbers do not transfer; the structural point does.",
        "exact_cue_collapse_N": None if all(r["hit1_ca3_on"] > 0.5 for r in arm12) else "see rows",
        "max_delta_ca3_on_minus_off": max(deltas),
        "min_delta_ca3_on_minus_off": min(deltas),
        "ca3_ever_better_than_off": any(d > 1e-9 for d in deltas),
        "arm12_exact_cue_sweep_N": arm12,
        "arm3_degraded_cue": arm3,
    }
    with open("scratch/d3_capacity_characterisation.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print("\nCA3 EVER BETTER THAN CA3-OFF ANYWHERE IN THE GRID:", out["ca3_ever_better_than_off"])
    print("delta range: %+.4f .. %+.4f" % (out["min_delta_ca3_on_minus_off"],
                                           out["max_delta_ca3_on_minus_off"]))


if __name__ == "__main__":
    main()
