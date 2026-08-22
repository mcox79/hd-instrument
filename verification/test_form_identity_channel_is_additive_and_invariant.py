"""WITNESS: the form-identity channel is (a) brain-correct and (b) ADDITIVE -- symbol_vector untouched.

Wired 2026-08-22 on the owner's Q102 ruling: connect the form organ only if it is doing the job
required of it AS ACCORDING TO THE BRAIN. The VWFA's defining property is INVARIANCE -- same word,
different surface, same code -- so that is what this asserts.

THE SECOND HALF IS THE ONE THAT MATTERS MOST. The wiring is additive by construction because
symbol_vector also encodes RELATION labels (a form code over "REL:^nmod" is noise), has a second live
consumer (perirhinal_conjunctive), and lands deterministic codes in accumulated stores -- so replacing
it would rewrite every persisted symbol code. A test that only checked the new channel could not catch
a regression in the old one, so this pins symbol_vector's exact byte-level behaviour as well.

Scaffold-free: imports the live module, no fixtures, no mocks.
"""
from __future__ import annotations

import hashlib
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.reading_grounding_loop import (        # noqa: E402
    CTX_D, form_identity_vector, symbol_vector,
)


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na == 0 or nb == 0 else float(a @ b / (na * nb))


def test_case_invariance_is_the_defining_property():
    """The VWFA's defining bar: same word, different case -> SAME code."""
    for w in ("cat", "doctor", "London", "running"):
        c = _cos(form_identity_vector(w), form_identity_vector(w.upper()))
        assert c > 0.99, f"case invariance failed for {w!r}: cos={c:.4f}"


def test_inflection_is_graded_not_identical_and_not_zero():
    """Same lexeme, different surface: RELATED but DISTINGUISHABLE. Both bounds matter --
    identical would lose the distinction, zero would lose the relation."""
    for a, b in (("cat", "cats"), ("child", "children"), ("walk", "walked")):
        c = _cos(form_identity_vector(a), form_identity_vector(b))
        assert 0.15 < c < 0.95, f"inflection not graded for {a}/{b}: cos={c:.4f}"


def test_unrelated_words_stay_low():
    """The control. Invariance is only worth having if it does not manufacture similarity."""
    for a, b in (("cat", "democracy"), ("doctor", "hammer")):
        c = _cos(form_identity_vector(a), form_identity_vector(b))
        assert abs(c) < 0.20, f"unrelated pair too similar: {a}/{b} cos={c:.4f}"


def test_form_channel_beats_the_hash_on_the_brain_bar():
    """The comparison that justified the wiring: the live hash has NO form structure."""
    pairs = (("cat", "CAT"), ("doctor", "DOCTOR"), ("running", "RUNNING"))
    form = np.mean([_cos(form_identity_vector(a), form_identity_vector(b)) for a, b in pairs])
    hashv = np.mean([_cos(symbol_vector(a), symbol_vector(b)) for a, b in pairs])
    assert form > 0.99, f"form channel lost its invariance: {form:.4f}"
    assert abs(hashv) < 0.20, f"hash unexpectedly has form structure: {hashv:.4f}"
    assert form - hashv > 0.75, f"margin collapsed: form={form:.4f} hash={hashv:.4f}"


def test_symbol_vector_is_BYTE_IDENTICAL_to_its_documented_construction():
    """ADDITIVITY, pinned at the byte level. symbol_vector's docstring promises a sha256-seeded
    bipolar draw; accumulated stores depend on it EXACTLY. Recompute it independently here rather
    than trusting that nothing touched it."""
    for sym in ("cat", "REL:^nmod", "wedding", "zzz_unlikely_symbol"):
        seed = int.from_bytes(hashlib.sha256(sym.encode("utf-8")).digest()[:8], "big") % (2 ** 32)
        expected = np.random.default_rng(seed).choice([-1.0, 1.0], size=CTX_D)
        assert np.array_equal(symbol_vector(sym), expected), f"symbol_vector CHANGED for {sym!r}"


def test_relation_labels_still_route_through_the_hash():
    """A form code over a relation tag is noise. This pins that REL: symbols are NOT form-coded --
    the failure mode would be someone 'helpfully' extending the form channel to all symbols."""
    a = symbol_vector("REL:^nmod")
    b = symbol_vector("REL:^obj")
    assert abs(_cos(a, b)) < 0.20, "relation tags should be near-orthogonal under the hash"
    f = form_identity_vector("REL:^nmod")
    assert _cos(a, f) < 0.90, "relation tag is being form-coded on the live identity path"


def _run() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL  {t.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run())
