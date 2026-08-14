"""Scaffold-free witness for the GRADED comparator path (2026-08-13).

Covers the three additive, default-OFF hdlab changes landed with
data/exp_graded_divisive_comparator_v1 (HARD_PASS, prereg d6c56353c):
  1. hdlab.grounding_acquisition_loop.context_vector(..., graded=True)
  2. hdlab.reading_grounding_loop.context_vector_masked(..., graded=True)
     and ConceptSpace.freeze_graded(normalise=...)
  3. hdlab.reading_grounding_loop.ReadoutConfig(graded_query=True)

The witness has two jobs and they are equally load-bearing:
  A. DEFAULTS ARE UNCHANGED. Every default path must be byte-for-byte what it was, because these
     functions are on the live reading pipeline (reading_grounding_loop, prelim_tier,
     script_grain_acquisition_loop, foundation_persistence all route through them).
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
    CTX_D, ConceptSpace, ReadoutConfig, canonicalize_fast, context_vector_masked,
    normalize_lemma,
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


def t1_defaults_are_byte_identical():
    for s in SENTS:
        assert np.array_equal(context_vector(s, d=CTX_D), _legacy_context_vector(s, CTX_D)), \
            "context_vector default changed on %r" % s
        assert np.array_equal(context_vector(s, d=CTX_D, graded=False),
                              _legacy_context_vector(s, CTX_D)), "graded=False is not the default"
        for lem in ("poet", "river", "zzzz"):
            kept = " ".join(w for w in content_words(s) if normalize_lemma(w) != lem)
            assert np.array_equal(context_vector_masked(s, lem, d=CTX_D),
                                  _legacy_context_vector(kept, CTX_D)), \
                "context_vector_masked default changed on (%r,%r)" % (s, lem)
    return "T1 defaults byte-identical to the pre-change implementation"


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


def t3_freeze_graded():
    sp = ConceptSpace(d=CTX_D)
    for w, ss in (("poet", SENTS[:1]), ("river", SENTS[1:3])):
        for s in ss:
            sp.observe(w, context_vector_masked(s, w))
    anchors, signed_mat = sp.anchor_matrix()
    raw = sp.freeze_graded("none")
    a2, gmat = raw.anchor_matrix()
    assert a2 == anchors, "freeze_graded changed the anchor order"
    assert np.array_equal(np.sign(gmat), signed_mat), \
        "freeze_graded('none') is not the pre-quantisation field"
    assert not np.array_equal(gmat, signed_mat), "freeze_graded('none') is already quantised"
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
    sp = ConceptSpace(d=CTX_D)
    for w, ss in (("poet", SENTS[:1]), ("river", SENTS[1:3])):
        for s in ss:
            sp.observe(w, context_vector_masked(s, w))
    q_signed = context_vector_masked(SENTS[0], "poet")
    q_graded = context_vector_masked(SENTS[0], "poet", graded=True)
    assert not np.array_equal(q_signed, q_graded), "the two query encoders agree"
    # default: graded_query off -> the query IS quantised, so a graded query gives the same answer
    # as its own sign. That equivalence is what proves the flag is what changes the behaviour.
    a_def, _ = canonicalize_fast("__x__", q_graded, sp, thresh=-1.0)
    a_sgn, _ = canonicalize_fast("__x__", q_signed, sp, thresh=-1.0)
    assert a_def == a_sgn, "the default path did not quantise the query"
    cfg = ReadoutConfig(graded_query=True)
    assert not cfg.active, "graded_query must NOT switch the FIX1/FIX2 block on"
    _a, c_graded = canonicalize_fast("__x__", q_graded, sp, thresh=-1.0, readout=cfg)
    _b, c_signed = canonicalize_fast("__x__", q_graded, sp, thresh=-1.0)
    assert abs(c_graded - c_signed) > 1e-9, "graded_query=True did not change the decision variable"
    assert np.isfinite(c_graded), "graded read-out cosine is not finite"
    return "T4 graded_query=True bypasses the query quantiser and does not enable FIX1/FIX2"


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
    tests = [t1_defaults_are_byte_identical, t2_graded_differs_and_signs_back, t3_freeze_graded,
             t4_graded_query_flag, t5_mechanism_the_quantiser_annihilates_distinctive_features]
    for fn in tests:
        print("PASS  %s" % fn())
    print("verify_graded_divisive_comparator: %d/%d PASS" % (len(tests), len(tests)))


if __name__ == "__main__":
    main()
