"""Scaffold-free witness for the GRADED comparator path (2026-08-13).

Covers the three additive, default-OFF hdlab changes landed with
data/exp_graded_divisive_comparator_v1 (HARD_PASS, prereg d6c56353c):
  1. hdlab.grounding_acquisition_loop.context_vector(..., graded=True)
  2. hdlab.reading_grounding_loop.context_vector_masked(..., graded=True)
     and ConceptSpace.freeze_graded(normalise=...)
  3. hdlab.reading_grounding_loop.ReadoutConfig(graded_query=True)

UPDATED 2026-08-14: `context_vector_masked`'s default FLIPPED to graded behind the module switch
`GRADED_COMPARATOR` (`HD_GRADED_COMPARATOR=0` restores the prior behaviour), licensed by
data/exp_capacity_vs_format_2x2_livepath_v1 (prereg 29822f111). T1 was therefore rewritten to
assert the NEW default rather than deleted or relaxed -- it now pins BOTH formats explicitly and
carries a vacuity guard, so it is strictly more coverage than the version it replaces.
`context_vector` (grounding_acquisition_loop) did NOT flip; its default is still graded=False.

The witness has two jobs and they are equally load-bearing:
  A. THE DEFAULT CONTRACT IS PINNED IN BOTH DIRECTIONS. The bare call must be exactly what the
     module switch says, the explicit `graded=False` escape hatch must still be byte-for-byte the
     pre-change result, and the two must demonstrably DIFFER -- because these functions are on the
     live reading pipeline (reading_grounding_loop, prelim_tier, script_grain_acquisition_loop,
     foundation_persistence all route through them) and a silent no-op flip would look identical
     to a real one.
  B. THE MECHANISM IS REAL. A deterministic construction in which two concepts share a category
     component and differ only in a small distinctive component: the graded path must recover the
     right one and the quantised path must not. This is the audit's claim reduced to an assertion.

No tracing, no fixtures, no network. Run: python verification/verify_graded_divisive_comparator.py
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import hashlib
import sys

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.grounding_acquisition_loop import content_words, context_vector          # noqa: E402
from hdlab.reading_grounding_loop import (                                          # noqa: E402
    CTX_D, GRADED_COMPARATOR, ConceptSpace, ReadoutConfig, canonicalize_fast,
    context_vector_masked, normalize_lemma,
)

SENTS = [
    "The poet wrote a long book about rivers and mountains in winter.",
    "A cathedral stands beside the river near the old market square.",
    "Boats travel along the river between the town and the sea every summer.",
    "the of and a",                       # no content words -> the zero-vector edge case
]


def _legacy_context_vector(text, d):
    """The pre-change implementation, transcribed, so 'unchanged' is checked against an
    INDEPENDENT copy rather than against the function under test calling itself."""
    words = content_words(text)
    if not words:
        return np.zeros(d, dtype=np.float64)
    acc = np.zeros(d, dtype=np.float64)
    for w in words:
        seed = int.from_bytes(hashlib.sha256(w.encode("utf-8")).digest()[:8], "big") % (2 ** 32)
        acc += np.random.default_rng(seed).choice([-1.0, 1.0], size=d)
    out = np.sign(acc)
    out[out == 0] = 1.0
    return out


def _legacy_graded_context_vector(text, d):
    """The SAME independent transcription, stopped one operation earlier: the raw accumulated sum,
    which is what the graded path is supposed to return. Independent of the function under test for
    the same reason as above."""
    words = content_words(text)
    if not words:
        return np.zeros(d, dtype=np.float64)
    acc = np.zeros(d, dtype=np.float64)
    for w in words:
        seed = int.from_bytes(hashlib.sha256(w.encode("utf-8")).digest()[:8], "big") % (2 ** 32)
        acc += np.random.default_rng(seed).choice([-1.0, 1.0], size=d)
    return acc


def t1_default_contract():
    """THE DEFAULT CONTRACT, both halves of it.

    The default of context_vector_masked FLIPPED on 2026-08-14 (HD_GRADED_COMPARATOR, default ON).
    This test asserts the CURRENT contract in four arms and refuses to let a no-op switch satisfy
    it. Every expectation is an INDEPENDENT transcription (_legacy_context_vector /
    _legacy_graded_context_vector), never the function under test calling itself.

      (a) the BARE call follows the module switch -- graded when ON, signed when OFF;
      (b) graded=False EXPLICIT is still the legacy signed result byte-for-byte, either way;
      (c) graded=True EXPLICIT is the raw pre-quantisation sum, either way (and, when the switch is
          ON, is bit-identical to the bare call);
      (d) VACUITY GUARD: the two explicit paths must actually DIFFER on the same input, otherwise
          (a)-(c) would all pass on a switch that changes nothing.

    context_vector (grounding_acquisition_loop) did NOT flip -- its default is still graded=False --
    so that half stays an unchanged-defaults assertion."""
    differed = 0
    for s in SENTS:
        # context_vector's default is UNCHANGED by the 08-14 flip.
        assert np.array_equal(context_vector(s, d=CTX_D), _legacy_context_vector(s, CTX_D)), \
            "context_vector default changed on %r" % s
        assert np.array_equal(context_vector(s, d=CTX_D, graded=False),
                              _legacy_context_vector(s, CTX_D)), "graded=False is not the default"
        for lem in ("poet", "river", "zzzz"):
            kept = " ".join(w for w in content_words(s) if normalize_lemma(w) != lem)
            want_signed = _legacy_context_vector(kept, CTX_D)
            want_graded = _legacy_graded_context_vector(kept, CTX_D)
            bare = context_vector_masked(s, lem, d=CTX_D)
            expl_off = context_vector_masked(s, lem, d=CTX_D, graded=False)
            expl_on = context_vector_masked(s, lem, d=CTX_D, graded=True)
            # (a) the bare call = the NEW default = whatever the module switch says
            want_bare = want_graded if GRADED_COMPARATOR else want_signed
            assert np.array_equal(bare, want_bare), (
                "context_vector_masked bare call does not match the %s contract on (%r,%r)"
                % ("GRADED" if GRADED_COMPARATOR else "SIGNED (HD_GRADED_COMPARATOR=0)", s, lem))
            # (b) explicit legacy escape hatch, byte-for-byte, INDEPENDENT of the switch
            assert np.array_equal(expl_off, want_signed), \
                "graded=False is no longer the pre-change signed result on (%r,%r)" % (s, lem)
            # (c) explicit graded, INDEPENDENT of the switch; and bare==graded=True when ON
            assert np.array_equal(expl_on, want_graded), \
                "graded=True is not the raw pre-quantisation sum on (%r,%r)" % (s, lem)
            if GRADED_COMPARATOR:
                assert np.array_equal(expl_on, bare), \
                    "graded=True disagrees with the bare call while the switch is ON"
            else:
                assert np.array_equal(expl_off, bare), \
                    "graded=False disagrees with the bare call while the switch is OFF"
            # (d) VACUITY GUARD -- the flip must be a real change, not a relabelling. The
            # no-content-word window is degenerate (both paths are the zero vector) and is the one
            # case allowed to agree; it must agree at ZERO, not at some invented signal.
            if not expl_off.any():
                assert not expl_on.any(), "graded path invented signal from an empty window"
                continue
            assert not np.array_equal(expl_on, expl_off), (
                "the two comparator formats are bit-identical on (%r,%r) -- the default flip would "
                "be a no-op and arms (a)-(c) vacuous" % (s, lem))
            assert np.abs(expl_on).max() > 1.0, \
                "the graded default carries no magnitude; it is quantised in all but name"
            differed += 1
    assert differed >= 3, "not enough non-degenerate (sentence, lemma) pairs exercised the flip"
    return ("T1 default contract: bare call == %s, graded=False == legacy signed byte-for-byte, "
            "graded=True == raw sum, and the two formats differ on %d/%d non-degenerate windows"
            % ("GRADED" if GRADED_COMPARATOR else "SIGNED", differed, differed))


def t2_graded_differs_and_signs_back():
    hit = 0
    for s in SENTS:
        g = context_vector(s, d=CTX_D, graded=True)
        q = context_vector(s, d=CTX_D)
        if not q.any():                                   # the no-content-word case
            assert not g.any(), "graded path invented signal from an empty window"
            continue
        assert not np.array_equal(g, q), "graded output is bit-identical to the quantised one"
        assert np.array_equal(np.where(g == 0.0, q, np.sign(g)), q), \
            "sign(graded) != default: the graded path is not the same math minus one operation"
        assert np.abs(g).max() > 1.0, "graded output carries no magnitude"
        hit += 1
    assert hit >= 3, "not enough non-degenerate sentences exercised"
    return "T2 graded=True differs, carries magnitude, and signs back to the default exactly"


def _observed_space():
    """A ConceptSpace filled through the LIVE default path, plus an INDEPENDENTLY accumulated
    expectation for what its per-anchor sums must be under whichever default is in force."""
    sp = ConceptSpace(d=CTX_D)
    want = {}
    for w, ss in (("poet", SENTS[:1]), ("river", SENTS[1:3])):
        for s in ss:
            sp.observe(w, context_vector_masked(s, w))          # BARE call = the live default
            kept = " ".join(x for x in content_words(s) if normalize_lemma(x) != w)
            ref = (_legacy_graded_context_vector if GRADED_COMPARATOR
                   else _legacy_context_vector)(kept, CTX_D)
            want[w] = want.get(w, np.zeros(CTX_D, dtype=np.float64)) + ref
    return sp, want


def t3_freeze_graded():
    """`anchor_matrix`/`bundle` ALSO flipped on 2026-08-14 (same switch). This arm therefore pins
    the accumulated field against an independent accumulation, then pins the RELATIONSHIP between
    the default matrix and freeze_graded('none') in BOTH switch states -- byte-identical when the
    switch is ON (the documented coherence invariant: a graded field must never be read by a signed
    query), pre-quantisation form of it when OFF."""
    sp, want = _observed_space()
    anchors, default_mat = sp.anchor_matrix()
    want_sums = np.stack([want[a] for a in anchors], axis=0)
    assert np.array_equal(default_mat,
                          want_sums if GRADED_COMPARATOR else np.sign(want_sums)), \
        "anchor_matrix does not match an independent accumulation of the same observations"
    assert np.array_equal(sp.bundle(anchors[0]), default_mat[0]), \
        "bundle() and anchor_matrix() disagree -- canonicalize_fast and canonicalize would diverge"
    raw = sp.freeze_graded("none")
    a2, gmat = raw.anchor_matrix()
    assert a2 == anchors, "freeze_graded changed the anchor order"
    assert np.array_equal(gmat, want_sums), \
        "freeze_graded('none') is not the independently accumulated pre-quantisation field"
    # VACUITY GUARD: the field must carry magnitude that a quantiser would actually destroy.
    assert np.abs(gmat).max() > 1.0 and not np.array_equal(gmat, np.sign(gmat)), \
        "freeze_graded('none') is already quantised"
    if GRADED_COMPARATOR:
        assert np.array_equal(gmat, default_mat), \
            "graded default: anchor_matrix and freeze_graded('none') must agree byte-for-byte"
    else:
        assert np.array_equal(np.sign(gmat), default_mat), \
            "freeze_graded('none') is not the pre-quantisation field"
        assert not np.array_equal(gmat, default_mat), "freeze_graded('none') is already quantised"
    ctr = sp.freeze_graded("center").anchor_matrix()[1]
    assert np.allclose(ctr.mean(axis=0), 0.0, atol=1e-9), "'center' did not centre the field"
    z = sp.freeze_graded("z").anchor_matrix()[1]
    assert np.allclose(z.mean(axis=0), 0.0, atol=1e-9), "'z' did not centre"
    sd = np.std(z, axis=0)
    assert np.all(sd <= 1.0 + 1e-6), "'z' produced sd > 1"
    try:
        sp.freeze_graded("bogus")
        raise AssertionError("freeze_graded accepted an unknown normalise mode")
    except ValueError:
        pass
    # freeze_graded must be READ-ONLY, like freeze()
    assert not hasattr(raw, "observe"), "a frozen graded view exposes observe()"
    assert len(ConceptSpace(d=CTX_D).freeze_graded("z").anchors()) == 0, "empty space is not empty"
    return "T3 freeze_graded: pre-quantisation field, both pools correct, read-only, empty-safe"


def t4_graded_query_flag():
    """The QUERY quantiser is the fourth flipped site: `canonicalize_fast(readout=None)` and a bare
    `ReadoutConfig()` now follow the module switch. Both explicit settings are pinned here, and the
    default is required to AGREE with exactly one of them and DIFFER from the other -- which is what
    makes "the default followed the switch" a falsifiable statement rather than a label."""
    sp, _want = _observed_space()
    q_signed = context_vector_masked(SENTS[0], "poet", graded=False)
    q_graded = context_vector_masked(SENTS[0], "poet", graded=True)
    assert not np.array_equal(q_signed, q_graded), "the two query encoders agree"
    cfg_on, cfg_off = ReadoutConfig(graded_query=True), ReadoutConfig(graded_query=False)
    assert not cfg_on.active and not cfg_off.active, \
        "graded_query must NOT switch the FIX1/FIX2 block on"
    assert ReadoutConfig().graded_query is GRADED_COMPARATOR, \
        "a bare ReadoutConfig() does not follow the module switch"
    _a, c_on = canonicalize_fast("__x__", q_graded, sp, thresh=-1.0, readout=cfg_on)
    _b, c_off = canonicalize_fast("__x__", q_graded, sp, thresh=-1.0, readout=cfg_off)
    assert abs(c_on - c_off) > 1e-9, "graded_query did not change the decision variable"
    # graded_query=False must be quantising the QUERY: handing it the already-signed query is then
    # a no-op. That equivalence is what proves the flag is what changes the behaviour.
    _c, c_presigned = canonicalize_fast("__x__", np.sign(q_graded), sp, thresh=-1.0, readout=cfg_off)
    assert abs(c_off - c_presigned) < 1e-12, "graded_query=False did not quantise the query"
    # readout=None follows the switch: identical to one arm, measurably different from the other.
    _d, c_default = canonicalize_fast("__x__", q_graded, sp, thresh=-1.0)
    want, other = (c_on, c_off) if GRADED_COMPARATOR else (c_off, c_on)
    assert abs(c_default - want) < 1e-12, \
        "readout=None did not follow GRADED_COMPARATOR=%s" % GRADED_COMPARATOR
    assert abs(c_default - other) > 1e-9, "the two query conventions are indistinguishable"
    assert np.isfinite(c_on) and np.isfinite(c_default), "read-out cosine is not finite"
    return ("T4 graded_query pins both query conventions; readout=None follows the switch "
            "(GRADED_COMPARATOR=%s) and does not enable FIX1/FIX2" % GRADED_COMPARATOR)


def t5_mechanism_the_quantiser_annihilates_distinctive_features():
    """THE CLAIM, as an assertion. Two concepts share a category component S and differ only in a
    small distinctive component. The query carries S plus concept A's distinctive part. The graded
    field must pick A; the quantised field must not (it has thrown the distinctive part away).
    Deterministic: fixed seed, no corpus, no scaffolding."""
    d = CTX_D
    rng = np.random.default_rng(20260813)
    n_trials, ratio = 200, 0.06
    S = rng.normal(size=d) * 3.0
    graded_hits, signed_hits = 0, 0
    for t in range(n_trials):
        r2 = np.random.default_rng(1000 + t)
        dA = r2.normal(size=d) * 3.0 * ratio
        dB = r2.normal(size=d) * 3.0 * ratio
        aA_g, aB_g = S + dA, S + dB
        aA_s, aB_s = np.sign(aA_g), np.sign(aB_g)
        # the query is the SHARED component plus A's distinctive part, with independent noise
        q = S + dA + r2.normal(size=d) * 3.0 * ratio

        def pick(x, y, query):
            cx = float(x @ query / (np.linalg.norm(x) * np.linalg.norm(query)))
            cy = float(y @ query / (np.linalg.norm(y) * np.linalg.norm(query)))
            return cx > cy
        graded_hits += int(pick(aA_g, aB_g, q))
        signed_hits += int(pick(aA_s, aB_s, np.sign(q)))
    g_acc, s_acc = graded_hits / n_trials, signed_hits / n_trials
    # D-RECOVERY: how much of the code's difference between the two concepts IS the true
    # distinctive difference. 1.0 for a graded code by construction; the quantiser's value is the
    # measurement, and it is the annihilation claim stated directly.
    r3 = np.random.default_rng(4242)
    rec, n_rec = 0.0, 0
    for _ in range(n_trials):
        dA = r3.normal(size=d) * 3.0 * ratio
        dB = r3.normal(size=d) * 3.0 * ratio
        diff_s = np.sign(S + dA) - np.sign(S + dB)
        if np.linalg.norm(diff_s) > 0:
            rec += float(diff_s @ (dA - dB)
                         / (np.linalg.norm(diff_s) * np.linalg.norm(dA - dB)))
            n_rec += 1
    d_recovery_signed = rec / max(n_rec, 1)

    assert g_acc > s_acc, ("the graded field did not beat the quantised one (%.3f vs %.3f) -- the "
                           "mechanism this landing is based on does not reproduce" % (g_acc, s_acc))
    assert g_acc >= 0.95, "graded accuracy %.3f is implausibly low for a solvable task" % g_acc
    assert g_acc - s_acc >= 0.05, (
        "graded beat quantised by only %.3f; the witness requires the same +0.05 magnitude the "
        "experiment's HARD_PASS band used" % (g_acc - s_acc))
    assert d_recovery_signed <= 0.50, (
        "the quantised code recovered %.3f of the true distinctive difference direction; above 0.5 "
        "the annihilation claim would not hold at this ratio" % d_recovery_signed)
    return ("T5 mechanism: at a %.0f%% distinctive:shared ratio the graded field scores %.3f and "
            "the quantised field %.3f (gap %+.3f); the quantised code recovers only %.3f of the "
            "true distinctive difference direction (graded recovers 1.0 by construction)"
            % (ratio * 100, g_acc, s_acc, g_acc - s_acc, d_recovery_signed))


def main():
    tests = [t1_default_contract, t2_graded_differs_and_signs_back, t3_freeze_graded,
             t4_graded_query_flag, t5_mechanism_the_quantiser_annihilates_distinctive_features]
    for fn in tests:
        print("PASS  %s" % fn())
    print("verify_graded_divisive_comparator: %d/%d PASS" % (len(tests), len(tests)))


if __name__ == "__main__":
    main()
