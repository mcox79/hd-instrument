"""Witness for hdlab.relcl_resolver (landed 2026-08-27, consolidation phase).

Self-contained construction proof of the active-filler filler-gap resolver (no corpus):
  [1] the REVERSIBLE OBJECT-GAP case -- "the doctor that the lawyer chased" -- the resolver picks the fronted
      filler (doctor) as the patient, where the word-order baseline gets it WRONG (the discriminator).
  [2] SUBJECT-GAP relative clause -- "the lawyer that chased the doctor" -- the object gap does NOT fire (an
      overt post-verbal object exists), so the word-order rule applies (patient = doctor).
  [3] CANONICAL SVO -- no relativizer -> word-order rule (patient = the post-verbal object).
  [4] PASSIVE -- the pre-aux subject is the patient (arm 1).
  [5] glass-box: resolve_patient takes NO arc heads; the object-gap gate fires ONLY on the reversible case.
The powered CI-separated win over the two-line floor (0.9533 vs 0.4994) is the solver's
verify_relcl_incremental_fillergap_parser.py.
"""
from __future__ import annotations

import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.relcl_resolver import is_object_gap, resolve_patient, two_line_patient  # noqa: E402


def main() -> int:
    # [1] OBJECT-GAP reversible: the(1) doctor(2) that(3) the(4) lawyer(5) chased(6) -> patient of chased = doctor(2)
    t1 = ["the", "doctor", "that", "the", "lawyer", "chased"]
    p1 = ["DET", "NOUN", "PRON", "DET", "NOUN", "VERB"]
    r1 = resolve_patient(t1, p1, 6)
    tl1 = two_line_patient(t1, p1, 6)
    print(f"[1] object-gap 'the doctor that the lawyer chased': resolver->{r1} (doctor=2), two-line->{tl1}")
    assert r1 == 2, f"the fronted filler (doctor=2) must be the patient of an object-gap relative clause, got {r1}"
    assert tl1 != 2, "the word-order baseline should be WRONG here (that is why the resolver exists)"
    assert is_object_gap(t1, p1, 6), "the object-gap construction should fire on the reversible case"

    # [2] SUBJECT-GAP: the(1) lawyer(2) that(3) chased(4) the(5) doctor(6) -> gate off (post-object) -> patient=doctor(6)
    t2 = ["the", "lawyer", "that", "chased", "the", "doctor"]
    p2 = ["DET", "NOUN", "PRON", "VERB", "DET", "NOUN"]
    r2 = resolve_patient(t2, p2, 4)
    print(f"[2] subject-gap 'the lawyer that chased the doctor': resolver->{r2} (doctor=6); gate={is_object_gap(t2,p2,4)}")
    assert r2 == 6, f"a subject-gap relative clause falls to word-order -> post-verbal object (doctor=6), got {r2}"
    assert not is_object_gap(t2, p2, 4), "the object-gap gate must NOT fire when the object slot is filled"

    # [3] CANONICAL: the(1) lawyer(2) chased(3) the(4) doctor(5) -> word-order -> patient = post-verbal doctor(5)
    t3 = ["the", "lawyer", "chased", "the", "doctor"]
    p3 = ["DET", "NOUN", "VERB", "DET", "NOUN"]
    r3 = resolve_patient(t3, p3, 3)
    print(f"[3] canonical 'the lawyer chased the doctor': resolver->{r3} (doctor=5); gate={is_object_gap(t3,p3,3)}")
    assert r3 == 5, f"canonical SVO -> the post-verbal object is the patient (doctor=5), got {r3}"
    assert not is_object_gap(t3, p3, 3), "no relativizer -> the object-gap gate must not fire"

    # [4] PASSIVE (arm 1): the(1) mouse(2) was(3) eaten(4) -> pre-aux subject is the patient (mouse=2)
    t4 = ["the", "mouse", "was", "eaten"]
    p4 = ["DET", "NOUN", "AUX", "VERB"]
    r4 = resolve_patient(t4, p4, 4, prec_voice=True)     # test the passive ARM logic (voice detection is the role-labeler's job)
    print(f"[4] passive 'the mouse was eaten' (prec_voice=True): resolver->{r4} (mouse=2)")
    assert r4 == 2, f"passive -> the pre-aux subject is the patient (mouse=2), got {r4}"

    # [5] glass-box: no arc heads / gold in the signature
    params = list(inspect.signature(resolve_patient).parameters)
    assert "heads" not in params and "gold" not in params and "labels" not in params, params
    print(f"[5] glass-box PASS (no heads/gold/labels in signature; UPOS + closed-class relativizers only)")

    print("\nALL WITNESS ASSERTIONS PASSED -- the active-filler resolver binds the fronted filler as the patient")
    print("in an object-gap relative clause (where word order fails), leaves subject-gap/canonical clauses to the")
    print("word-order rule, handles the passive voice route, and is a glass-box function of UPOS + relativizers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
