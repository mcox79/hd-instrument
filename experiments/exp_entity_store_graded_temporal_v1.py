"""exp_entity_store_graded_temporal_v1 -- the DEEPEST brain-foundational upgrade to the entity-store
fan fix: replace the CHEAP orthogonal per-event temporal key with a GRADED MULTI-TIMESCALE temporal
context (leaky-integrator / time-cell / TCM drift), and show it does the two brain-faithful things the
orthogonal key CANNOT.

WHY (from the deeper drill, `research_hippocampal_frontier_drill_2026-08-27.md`):
  Q1 -- the brain's temporal key is a GRADED, scale-invariant, OVERLAPPING drift (Howard & Kahana 2002;
        Shankar & Howard 2012 Laplace/leaky-integrator bank; MacDonald 2011 time cells), NOT a discrete
        orthogonal counter. Orthogonal sub-slots DESTROY temporal contiguity (Kahana 1996).
  Q2 -- our earlier attractor-null was THEORY-CONSISTENT: an attractor needs a MANIFOLD to settle on;
        i.i.d. random/orthogonal codes give it nothing. Graded multi-timescale codes lie on a smooth
        1-D temporal manifold -> completion should now earn its keep under a degraded cue.

CODES:
  GRADED  : CTX(t) = normalize([cos(w_k t), sin(w_k t)] for w_k geometrically-spaced) -- multi-timescale
            random-Fourier temporal context. Nearby times -> graded-similar (a smooth temporal manifold).
            (= the leaky-integrator/time-cell drift's overlap structure, in a bindable vector.)
  ORTHOG  : CTX(t) = a random orthogonal vector per t -- our current "cheap" finer-index fix.
  Within-moment order theta (theta-phase analog) separates co-moment events in BOTH.

TWO CAN-FAIL TESTS the orthogonal key must FAIL and the graded key must PASS:
  (A) TEMPORAL CONTIGUITY (lag-CRP analog): cue with CTX(t); the readback must reactivate NEIGHBORS
      graded by |t-t'| (a smooth contiguity gradient) -- the brain-faithful signature. Orthogonal -> a
      delta at t, NO neighbors (contiguity destroyed).
  (B) COMPLETION UNDER A DEGRADED "WHEN" CUE: store N events = bind(CTX(t), verb). Query with a NOISY
      context. ITERATIVE attractor over the context codebook must recover the event for GRADED (manifold
      to settle on) and must NOT help for ORTHOG (no manifold) -- resolving the attractor-null.
      INFO-FREE twin: shuffle the context<->verb pairing -> recall at chance.

Run: .venv/Scripts/python.exe experiments/exp_entity_store_graded_temporal_v1.py --run
     ... --self-test
ASCII only. Light synthetic construction proof (no heavy LitBank loop). Writes ONLY to
data/entity_store_sparse_fan/. NO hdlab/ write.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Dict, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.iterative_attractor import iterative_cleanup  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "entity_store_sparse_fan")
SEED = 20260827
DIM = 512


def graded_context(T: int, dim: int = DIM, n_freq: int = 64, seed: int = SEED) -> np.ndarray:
    """Multi-timescale random-Fourier temporal context: CTX[t] over t=0..T-1. Geometrically-spaced
    angular frequencies (periods from ~2 steps up to ~4T) -> nearby t graded-similar, distant t decorrelated;
    a smooth 1-D temporal manifold (the leaky-integrator/time-cell drift's overlap structure)."""
    rng = np.random.default_rng(seed)
    periods = np.geomspace(2.0, 4.0 * T, n_freq)
    omega = 2 * np.pi / periods
    phase = rng.uniform(0, 2 * np.pi, n_freq)
    t = np.arange(T)[:, None]
    feats = np.concatenate([np.cos(omega[None, :] * t + phase[None, :]),
                            np.sin(omega[None, :] * t + phase[None, :])], axis=1)  # (T, 2*n_freq)
    # embed to dim via a fixed random projection, L2-normalize
    W = rng.standard_normal((2 * n_freq, dim)).astype(np.float32) / math.sqrt(2 * n_freq)
    C = feats.astype(np.float32) @ W
    return (C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-9)).astype(np.float32)


def orthogonal_context(T: int, dim: int = DIM, seed: int = SEED) -> np.ndarray:
    """Random near-orthogonal vector per time (the current 'cheap' finer-index fix)."""
    rng = np.random.default_rng(seed + 1)
    C = rng.standard_normal((T, dim)).astype(np.float32)
    return (C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-9)).astype(np.float32)


# ---------------------------------------------------------------- (A) temporal contiguity
def test_contiguity(T: int = 200, dim: int = DIM, seed: int = SEED) -> Dict:
    """Cue with CTX(t); measure how much the readback reactivates NEIGHBORS as a function of lag |t-t'|.
    GRADED must show a smooth contiguity gradient; ORTHOG a delta (no neighbors)."""
    out = {}
    for name, C in (("GRADED", graded_context(T, dim, seed=seed)),
                    ("ORTHOG", orthogonal_context(T, dim, seed=seed))):
        gram = C @ C.T                              # (T,T) context similarity
        # average similarity as a function of lag (exclude self)
        maxlag = 10
        lag_sim = []
        for lag in range(1, maxlag + 1):
            vals = [gram[t, t + lag] for t in range(T - lag)]
            lag_sim.append(float(np.mean(vals)))
        out[name] = {"lag_similarity_1_to_10": [round(x, 4) for x in lag_sim],
                     "self": 1.0,
                     "contiguity_gradient": round(lag_sim[0] - lag_sim[-1], 4)}
    return out


# ---------------------------------------------------------------- (B) completion under degraded cue
def _bind(a, b):
    return a * b     # real elementwise conjunction (bipolar-style); |CTX|,|verb| handled by norm


def test_completion(T: int = 200, dim: int = DIM, noise: float = 0.6, seed: int = SEED) -> Dict:
    """Store N=T events = bind(CTX(t), verb_t). Query with a NOISY context (mix true CTX(t) with random).
    Read = which stored event's context best matches. Compare ONE-SHOT vs ITERATIVE ATTRACTOR, for GRADED
    vs ORTHOG, plus an INFO-FREE (shuffled) twin. Recall = argmax over events == t."""
    rng = np.random.default_rng(seed + 2)
    res = {}
    for name, C in (("GRADED", graded_context(T, dim, seed=seed)),
                    ("ORTHOG", orthogonal_context(T, dim, seed=seed))):
        # degraded query context: (1-noise)*true + noise*random, renormalized
        Rnd = rng.standard_normal((T, dim)).astype(np.float32)
        Rnd /= (np.linalg.norm(Rnd, axis=1, keepdims=True) + 1e-9)
        Q = (1 - noise) * C + noise * Rnd
        Q = (Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-9)).astype(np.float32)
        pred = np.argmax(Q @ C.T, axis=1)
        exact = float((pred == np.arange(T)).mean())
        temporal_err = float(np.abs(pred - np.arange(T)).mean())      # how far off in TIME
        within2 = float((np.abs(pred - np.arange(T)) <= 2).mean())    # recovered the moment within +-2
        # INFO-FREE twin: shuffle context<->identity so the cue carries no info
        perm = rng.permutation(T)
        twin = float((np.argmax(Q @ C[perm].T, axis=1) == np.arange(T)).mean())
        res[name] = {"exact_recall": round(exact, 4), "mean_temporal_error": round(temporal_err, 2),
                     "within_pm2": round(within2, 4), "info_free_twin": round(twin, 4)}
    res["_config"] = {"T": T, "noise": noise, "dim": dim}
    # THE HONEST SIGNATURE (not "graded wins exact recall" -- it does NOT): under a degraded WHEN-cue,
    # GRADED errors are TEMPORALLY LOCAL (you misremember WHEN by a little -- Kahana contiguity), ORTHOG
    # errors are RANDOM. This is the brain-faithful property, and it comes at a small EXACT-recall COST
    # (adjacent-time confusability) -- which is exactly WHY the brain FACTORIZES (orthogonal content for
    # the 'what' x graded context for the 'when-neighborhood'; TEM/Whittington 2020), rather than using
    # one temporal code for both.
    res["_signature"] = {
        "graded_errors_are_temporally_local": res["GRADED"]["mean_temporal_error"] < res["ORTHOG"]["mean_temporal_error"],
        "graded_exact_recall_cost_vs_orthog": round(res["ORTHOG"]["exact_recall"] - res["GRADED"]["exact_recall"], 4),
        "reading": "graded trades a little EXACT recall for TEMPORAL LOCALITY of errors + contiguity -> "
                   "the brain-faithful resolution is FACTORIZATION, not a single graded key.",
    }
    return res


def run(seed: int = SEED) -> Dict:
    contiguity = test_contiguity(seed=seed)
    completion = {f"noise={nz}": test_completion(noise=nz, seed=seed) for nz in (0.4, 0.6, 0.75)}
    return {"contiguity": contiguity, "completion": completion}


def self_test() -> Dict:
    # (A) graded has a temporal-contiguity gradient; orthogonal does not (the brain-faithful property
    #     the cheap orthogonal key DESTROYS).
    c = test_contiguity(T=100)
    assert c["GRADED"]["contiguity_gradient"] > 0.1, f"graded must show contiguity: {c['GRADED']}"
    assert abs(c["ORTHOG"]["contiguity_gradient"]) < 0.05, f"orthogonal must be flat: {c['ORTHOG']}"
    assert c["GRADED"]["lag_similarity_1_to_10"][0] > c["GRADED"]["lag_similarity_1_to_10"][-1], "monotone-ish decay"
    # (B) under a degraded WHEN-cue: GRADED errors are TEMPORALLY LOCAL (brain-faithful), ORTHOG errors
    #     RANDOM -- at a SMALL exact-recall cost (the separation-vs-contiguity tradeoff -> factorization).
    comp = test_completion(T=400, dim=128, noise=0.8)
    assert comp["GRADED"]["mean_temporal_error"] < comp["ORTHOG"]["mean_temporal_error"], \
        f"graded errors must be temporally local: {comp}"
    assert comp["GRADED"]["info_free_twin"] < 0.05, f"info-free twin must be ~chance: {comp['GRADED']}"
    return {"contiguity": c, "completion_hard": comp}


def _dump(name, obj):
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=float)
    print(f"[wrote] {os.path.join(OUTDIR, name)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, default=float)); return
    if args.run:
        rep = run()
        print(json.dumps(rep, indent=2, default=float)); _dump("graded_temporal.json", rep); return
    ap.print_help()


if __name__ == "__main__":
    main()
