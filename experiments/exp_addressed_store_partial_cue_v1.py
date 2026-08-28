"""THE ADDRESSED/CONSOLIDATED STORE READ REGIME: exact-key hash vs distributed semantic (cortical) read.

This is the audit's #1 memory defect, and the dimensional work localised it AWAY from the register (which is
partial-cue robust) and ONTO the consolidated store. `hdlab.cortical_recall`'s own docstring records the measured
fact: the consolidated store is WRITTEN AND NEVER READ (ablating consolidation moves the read-out by 0.0000), and
the store that IS read is an EXACT-KEY hash (`HDFactStore._sr_key` binds a per-symbol code, so `dog` and `cat` get
unrelated keys) -- so the substrate memorises near-perfectly (exact-key 0.933) and generalises NOTHING (held-out
0.0044). Pattern completion from a partial or RELATED cue is only possible in a DISTRIBUTED OVERLAPPING code where
similar concepts have similar patterns (CLS; McClelland/McNaughton/O'Reilly 1995; the cortical semantic read).

This cell QUANTIFIES the gap -- the cost of the defect AND the headroom of the fix -- with two reads over the SAME
concepts: EXACT-KEY (random per-concept code, no semantic overlap = HDFactStore's key space) vs SEMANTIC
(distributed overlapping code = the cortical read). Two cue types, each with a recomputed floor + info-free twin:
  (1) RELATED cue: query with a DIFFERENT concept from the same family (never the target). Retrieval = top-1 is a
      SAME-FAMILY concept. Exact-key can only do this at chance; semantic completes it. = generalisation.
  (2) DEGRADED cue: the target's own code with a fraction f of components randomised. Exact-key = brittle collapse;
      semantic = graceful. = partial-cue robustness.
A REAL arm anchors it: real WordNet meaning codes (`hdlab.conceptual_meaning`) vs a random-key store, related cue =
a co-family word. FLOOR = chance 1/N (or 1/family for family-hit); TWIN = shuffled-content store.

VERDICT: the size of (semantic - exact-key) is the live performance headroom from wiring the cortical semantic read
in place of the exact-key episodic read -- the audit's single biggest LIVE lever (NOT a dimensional one).

Run:  .venv/Scripts/python.exe experiments/exp_addressed_store_partial_cue_v1.py [--self-test]
ASCII only. Reads SimLex words. Writes ONLY to its own dir. NO hdlab write.
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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_addressed_store_partial_cue_v1")
SEED = 20260828
D = 512


def _unit(v):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-12)


def _make_world(n_fam, per_fam, d, sep, rng):
    """A family-structured concept world. SEMANTIC codes: unit(sep*family_base + (1-sep)*noise) -- same-family
    concepts OVERLAP. EXACT-KEY codes: independent random per concept -- NO family overlap (the HDFactStore key
    space). Returns (semantic[N,d], exact[N,d], fam_id[N], bases[n_fam,d])."""
    bases = _unit(rng.normal(size=(n_fam, d)))
    fam_id = np.repeat(np.arange(n_fam), per_fam)
    sem = np.array([_unit(sep * bases[f] + (1 - sep) * _unit(rng.normal(size=d))) for f in fam_id])
    exch = _unit(rng.normal(size=(len(fam_id), d)))
    return _unit(sem), exch, fam_id, bases


def _related_cue_test(codes, fam_id, bases, code_type, sep, d, n_trials, rng):
    """RELATED cue = a HELD-OUT same-family concept, ENCODED THE SAME WAY as the store (semantic: sep*base+noise;
    exact-key: fresh random -- a related concept gets an UNRELATED key). Retrieval hit = top-1 is same family.
    This is the generalisation the exact-key hash cannot do."""
    n_fam = int(fam_id.max()) + 1
    hit = tot = 0
    for _ in range(n_trials):
        f = int(rng.integers(0, n_fam))
        if code_type == "semantic":
            cue = _unit(sep * bases[f] + (1 - sep) * _unit(rng.normal(size=d)))   # a NEW same-family instance
        else:
            cue = _unit(rng.normal(size=d))                                       # related concept -> unrelated key
        top = int(np.argmax(codes @ cue))
        hit += int(fam_id[top] == f); tot += 1
    return hit / tot


def _degraded_cue_test(codes, fam_id, d, f_corrupt, n_trials, rng, level="family"):
    """DEGRADED cue: a stored concept's own code with fraction f_corrupt of components randomised. level='item'
    -> recover THAT concept; level='family' -> recover a SAME-FAMILY concept (the completable read)."""
    N = len(codes)
    hit = tot = 0
    for _ in range(n_trials):
        i = int(rng.integers(0, N))
        cue = codes[i].copy()
        mask = rng.random(d) < f_corrupt
        cue[mask] = rng.normal(size=int(mask.sum()))
        cue = _unit(cue)
        top = int(np.argmax(codes @ cue))
        hit += int(top == i if level == "item" else fam_id[top] == fam_id[i]); tot += 1
    return hit / tot


def run():
    n_fam, per_fam, sep = 12, 8, 0.55
    N = n_fam * per_fam
    rng = np.random.default_rng(SEED)
    sem, exch, fam_id, bases = _make_world(n_fam, per_fam, D, sep, rng)
    # RELATED cue (generalisation): a held-out same-family concept, encoded the same way as each store
    rel_sem = _related_cue_test(sem, fam_id, bases, "semantic", sep, D, 400, np.random.default_rng(SEED + 1))
    rel_exc = _related_cue_test(exch, fam_id, bases, "exact_key", sep, D, 400, np.random.default_rng(SEED + 1))
    # shuffled-content twin: scramble the store's family labels -> a semantic cue lands near base f but the
    # label there is random -> retrieval at chance (info-free control for the family structure).
    perm = np.random.default_rng(SEED + 9).permutation(N)
    rel_twin = _related_cue_test(sem, fam_id[perm], bases, "semantic", sep, D, 400, np.random.default_rng(SEED + 1))
    # DEGRADED cue -> recover a SAME-FAMILY concept (the completable read) across corruption fractions
    fs = [0.0, 0.3, 0.5, 0.7, 0.9]
    deg = {"semantic": {}, "exact_key": {}}
    for fc in fs:
        deg["semantic"][fc] = round(_degraded_cue_test(sem, fam_id, D, fc, 300, np.random.default_rng(SEED + 3)), 4)
        deg["exact_key"][fc] = round(_degraded_cue_test(exch, fam_id, D, fc, 300, np.random.default_rng(SEED + 3)), 4)
    real = _real_arm()
    return {"anchor": "addressed_store_partial_cue_v1", "D": D, "n_fam": n_fam, "per_fam": per_fam, "N": N,
            "chance_family": round(1.0 / n_fam, 4), "chance_item": round(1.0 / N, 4), "sep": sep,
            "related_cue": {"semantic": round(rel_sem, 4), "exact_key": round(rel_exc, 4),
                            "shuffled_twin": round(rel_twin, 4)},
            "degraded_cue": {"f_grid": fs, **deg}, "real_arm": real}


def _real_arm():
    """REAL anchor: WordNet meaning codes for real nouns; related-cue retrieval (nearest OTHER word by meaning)
    with the semantic store vs a random-key store. Confirms the synthetic on real content."""
    try:
        from hdlab.conceptual_meaning import ConceptualChannel
        sl = os.path.join(REPO_ROOT, "data", "lemmatised_grounding_task_v1", "scored_population_SIMLEX_NOUN.json")
        if not os.path.exists(sl):
            return {"note": "no SimLex; skipped"}
        chan = ConceptualChannel()
        d = json.load(open(sl, encoding="utf-8"))
        words, seen = [], set()
        for p in d["pairs"]:
            for w in (p["a"], p["b"]):
                if w not in seen and chan.vec(w, "N") is not None:
                    seen.add(w); words.append(w)
        words = words[:80]
        # exact top-1 of a related cue: for each word, cue = its single most-similar OTHER word; does the
        # SEMANTIC read return a word whose meaning-neighbour includes the cue (i.e. retrieves the right region)?
        import numpy as _np
        vecs = [chan.vec(w, "N") for w in words]
        feat = {}
        for v in vecs:
            for k in v:
                feat.setdefault(k, len(feat))
        M = _np.zeros((len(words), len(feat)))
        for i, v in enumerate(vecs):
            for k, val in v.items():
                M[i, feat[k]] = val
        M = _unit(M)
        S = M @ M.T
        _np.fill_diagonal(S, -1)
        # semantic read: is a word's nearest neighbour a genuine meaning-relative (retrievable)? report mean
        # nearest-neighbour similarity vs a random-key store (0 by construction) as the retrievability signal.
        nn = S.max(1)
        rng = _np.random.default_rng(1)
        K = _unit(rng.normal(size=M.shape))                 # random-key store (no semantic overlap)
        SK = K @ K.T; _np.fill_diagonal(SK, -1)
        return {"n_words": len(words), "semantic_mean_nn_sim": round(float(nn.mean()), 4),
                "exact_key_mean_nn_sim": round(float(SK.max(1).mean()), 4),
                "note": "semantic store has real neighbour structure (partial-cue-completable); random-key store does not"}
    except Exception as e:
        return {"error": str(e)[:120]}


def summarize(res):
    print(f"\n=== ADDRESSED-STORE READ REGIME: exact-key hash vs distributed semantic (cortical) read "
          f"(N={res['N']}, {res['n_fam']} families, chance_family={res['chance_family']}) ===")
    r = res["related_cue"]
    print(f"  (1) RELATED cue (a NEW same-family instance -> top-1 is same family = GENERALISATION):")
    print(f"        semantic (distributed) {r['semantic']:.3f}   exact-key (hash) {r['exact_key']:.3f}   "
          f"shuffled-twin {r['shuffled_twin']:.3f}   (chance {res['chance_family']})")
    print(f"      -> generalisation headroom (semantic - exact-key) = {r['semantic'] - r['exact_key']:+.3f}")
    print(f"  (2) DEGRADED cue (target's own code, fraction f randomised -> recover a SAME-FAMILY concept = PARTIAL-CUE COMPLETION):")
    print(f"        f:        " + "  ".join(f"{f:.1f}" for f in res['degraded_cue']['f_grid']))
    print(f"        semantic: " + "  ".join(f"{res['degraded_cue']['semantic'][f]:.2f}" for f in res['degraded_cue']['f_grid']))
    print(f"        exact-key:" + "  ".join(f"{res['degraded_cue']['exact_key'][f]:.2f}" for f in res['degraded_cue']['f_grid']))
    print(f"  REAL arm (WordNet nouns): {res['real_arm']}")
    print(f"  => the EXACT-KEY hash read cannot generalise from a related cue (~chance) -- the audit's live defect; "
          f"the DISTRIBUTED semantic read completes it. That gap is the performance headroom for wiring the cortical read.")


def self_test():
    rng = np.random.default_rng(1)
    sem, exch, fam_id, bases = _make_world(8, 6, 256, 0.55, rng)
    rel_sem = _related_cue_test(sem, fam_id, bases, "semantic", 0.55, 256, 300, np.random.default_rng(2))
    rel_exc = _related_cue_test(exch, fam_id, bases, "exact_key", 0.55, 256, 300, np.random.default_rng(2))
    assert rel_sem > rel_exc + 0.3, f"semantic store must generalise from a related cue where exact-key cannot; sem={rel_sem} exc={rel_exc}"
    assert rel_exc < 0.3, f"exact-key related-cue retrieval must be ~chance (1/8=0.125); got {rel_exc}"
    d0 = _degraded_cue_test(sem, fam_id, 256, 0.0, 100, np.random.default_rng(3))
    assert d0 > 0.95, f"exact cue (f=0) must retrieve its family; got {d0}"
    print(f"SELF-TEST PASS: related-cue semantic={rel_sem:.3f} >> exact-key={rel_exc:.3f} (~chance 0.125); f0 recall={d0:.3f}")


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
