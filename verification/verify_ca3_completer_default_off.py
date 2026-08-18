"""Scaffold-free witness for hdlab/ca3_completer.py.

Independent of the module's own self-tests: this file re-derives what it checks rather than
calling `run_selftests()`.

Five gates, every one of which CAN FAIL:
  G1 DEFAULT-OFF        -- importing the organ leaves the live reading path BIT-IDENTICAL, and
                           the module switch is False.
  G2 REUSE-NOT-REBUILD  -- the completer's flat path is BIT-IDENTICAL to a direct call into
                           hdlab.iterative_attractor. If this fails the module has silently become
                           a second attractor implementation.
  G3 CUE-CLAMP-REACHES  -- alpha=0.0 reproduces the LEGACY self-consistent dynamics bit-for-bit,
                           and alpha=0.5 differs from it. So the only thing separating this organ
                           from the earlier HARD_FAIL baseline is the cue clamp, and that clamp
                           demonstrably reaches the organ.
  G4 DOES-SOMETHING     -- routed completion returns STORED patterns and is bit-exact at a full
                           cue; the oracle arm identifies; the shuffled-choice null does not.
  G5 CANNOT-BE-QUOTED-AS-A-WIN -- the random overcomplete-dictionary FLOOR is non-trivial, so a
                           writeup cannot present dictionary reconstruction as completion.

Run:  .venv/Scripts/python.exe verification/verify_ca3_completer_default_off.py
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

import hdlab.reading_grounding_loop as RGL
from hdlab.hd_fact_store import HDFactStore

SENT = "The zibbo flickered by the lantern in the storm above the quiet harbour."
SEEDS = ["lantern", "storm", "harbour", "fire"]


def _read():
    store = HDFactStore(n_dim=512, seed=11,
                        relation_cardinality={RGL.KNOWN_RELATION: "FUNCTIONAL",
                                              RGL.MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    st = RGL.ReadingLoopState(store=store)
    RGL.seed_known_words(st, SEEDS, source="witness")
    RGL.process_sentence(st, SENT, "e0", pass_idx=0, encoder=None)
    return st


def main() -> int:
    out = {}

    # ---- baseline captured BEFORE the organ module is imported at all
    pre = _read()
    pre_prof = {a: pre.space.bundle(a).copy() for a in pre.space.anchors()}
    assert len(pre_prof) > 0, "witness precondition failed: the live reader stored no profile"

    import hdlab.ca3_completer as CC
    from hdlab.iterative_attractor import iterative_cleanup

    # ---- G1 DEFAULT-OFF
    post = _read()
    assert CC.CA3_COMPLETION is False, "G1 FAIL: CA3_COMPLETION defaulted ON"
    assert sorted(pre_prof) == post.space.anchors(), \
        "G1 FAIL: importing the organ changed the anchor population"
    for a in pre_prof:
        assert np.array_equal(pre_prof[a], post.space.bundle(a)), \
            f"G1 FAIL: importing the organ perturbed the live default reader path at {a!r}"
    out["G1_default_off_live_path_bit_identical"] = {
        "switch": CC.CA3_COMPLETION, "n_anchors": len(pre_prof)}

    # ---- G2 REUSE, NOT REBUILD
    g = np.random.default_rng(101)
    M, d, n = 256, 128, 24
    cb = g.standard_normal((M, d)).astype(np.float32)
    cue = cb[g.integers(0, M, n)] + 0.5 * g.standard_normal((n, d)).astype(np.float32)
    mine = CC.complete_flat(cue, cb)
    ref = iterative_cleanup(cue.astype(np.float32), cb, temp=CC.DEFAULT_TEMP,
                            max_steps=CC.MAX_STEPS_BRAIN_MOTIVATED, tol=CC.DEFAULT_TOL,
                            alpha=CC.ALPHA_BRAIN_CANONICAL)["state"]
    assert np.array_equal(mine, ref), \
        "G2 FAIL: complete_flat is not bit-identical to hdlab.iterative_attractor -- the module " \
        "has become a second implementation rather than a router"
    out["G2_reuse_bit_identical"] = True

    # ---- G3 THE CUE CLAMP REACHES THE ORGAN, and alpha=0 is the legacy baseline
    legacy = CC.complete_flat(cue, cb, alpha=0.0)
    legacy_ref = iterative_cleanup(cue.astype(np.float32), cb, temp=CC.DEFAULT_TEMP,
                                   max_steps=CC.MAX_STEPS_BRAIN_MOTIVATED, tol=CC.DEFAULT_TOL,
                                   alpha=0.0)["state"]
    assert np.array_equal(legacy, legacy_ref), \
        "G3 FAIL: alpha=0.0 does not reproduce the legacy self-consistent dynamics"
    assert not np.array_equal(legacy, mine), \
        "G3 FAIL: the cue clamp changes nothing -- alpha is not reaching the organ"
    out["G3_cue_clamp_reaches_and_alpha0_is_legacy"] = True

    # ---- G4 the organ does what it claims, on a store built here rather than imported
    rng = np.random.default_rng(7)
    D, MM, F, NN = 256, 1024, 4, 192
    spokes = tuple(f"SP{i}" for i in range(F))
    keys = {s: rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=D) for s in spokes}
    cbs = {s: rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(MM, D)) for s in spokes}
    store = np.zeros((MM, D), dtype=np.float32)
    for s in spokes:
        store += cbs[s] * keys[s][None, :]
    idx = rng.choice(MM, size=NN, replace=False)

    def top1(q):
        qn = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-12)
        sn = store / (np.linalg.norm(store, axis=1, keepdims=True) + 1e-12)
        return float(np.mean(np.argmax(qn @ sn.T, axis=1) == idx))

    full = store[idx].copy()
    done, ch = CC.complete_addressed(full, keys, cbs, spokes, return_choices=True)
    assert np.array_equal(ch, np.repeat(idx[:, None], F, axis=1)), \
        "G4 FAIL: full-cue completion did not recover every spoke"
    assert np.array_equal(done, full), \
        "G4 FAIL: full-cue rebuild is not bit-identical to the stored vector"
    orc = CC.oracle_complete_addressed(idx, keys, cbs, spokes)
    assert top1(orc) >= 0.999, f"G4 FAIL: oracle arm does not identify: {top1(orc)}"

    # a partial cue, degraded per spoke INDEPENDENTLY (the experiment's inherited model)
    f = 0.50
    deg = {}
    for s in spokes:
        keep = rng.random((NN, D)) < f
        donor = (idx + rng.integers(1, MM, size=NN)) % MM
        deg[s] = np.where(keep, cbs[s][idx], cbs[s][donor]).astype(np.float32)
    cue_p = np.zeros((NN, D), dtype=np.float32)
    for s in spokes:
        cue_p += deg[s] * keys[s][None, :]
    _, ch_p = CC.complete_addressed(cue_p, keys, cbs, spokes, return_choices=True)
    perm = rng.permutation(NN)
    shuf = np.zeros_like(cue_p)
    for si, s in enumerate(spokes):
        shuf += cbs[s][ch_p[perm, si]] * keys[s][None, :]
    null_v = top1(shuf)
    assert null_v <= 0.02, f"G4 FAIL: shuffled-choice null identifies items: {null_v}"
    out["G4_organ_does_what_it_claims"] = {
        "full_cue_rebuild_bit_exact": True, "oracle_top1": top1(orc),
        "shuffled_choice_null_top1": null_v}

    # ---- G5 the overcomplete-dictionary floor is real and must be reported beside any win
    rnd = {s: rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(MM, D)) for s in spokes}
    floor_v = top1(CC.complete_addressed(cue_p, keys, rnd, spokes))
    assert floor_v > 0.02, (
        "G5 FAIL: the random overcomplete-dictionary floor is at chance here, so this witness is "
        "not exercising the leak it exists to expose")
    out["G5_random_overcomplete_dictionary_floor"] = {
        "top1": floor_v, "M_over_d": MM / float(D),
        "meaning": "a codebook holding NONE of the stored content still reconstructs this much; "
                   "any completion claim must be CI-separated above it"}

    print("[verify_ca3_completer_default_off] PASS 5/5\n" + json.dumps(out, indent=2, default=float),
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
