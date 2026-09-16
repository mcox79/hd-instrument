"""Witness for THE GRADED PRONOUN PICK'S IDENTITY CONTRACT AND ITS SCORING (pri 131, deep review D02/D05/D06).

It PINS CLAIMS, NOT NUMBERS (README 2026-09-15).  Each check is an invariant of the contract, a direction, or
a can-fire control on the SHIPPED organ, measured through the LIVE `SituationReader().read()` on constructed
TEXT (no annotation column except where the check is about scoring):

  W1  two same-head referents stay DISTINCT files and the pick answers with a LIVE ENTITY ID
  W1b CAN-FIRE: the shipped organ answers with a head string and NO entity at all
  W2  a file is one candidate however many surface heads it carries (aliases compete once)
  W3  no valid id is used as a sentinel -- valid ids are NEGATIVE here, unresolved is None
  W4  no answer key -> coref_acc UNAVAILABLE, with discovered == attempted + abstained published
  W4b CAN-FIRE: the shipped organ reports coref_acc 0.0 on the same annotation-free text
  W5  a pick on the WRONG same-head mention scores WRONG (alignment by antecedent SPAN)
  W5b CAN-FIRE: the shipped scorer credits it through document-wide head membership
  W6  the single-sentence comparator is EXECUTED and can DISAGREE with the discourse resolver
  W7  Principle B from the reader's OWN parse: a plain pronoun skips its clause-mate co-argument
  W8  the goal canonicaliser returns the SELECTED identity, not whatever occupies id -1
  W9  the world-state possession holder is the entity the pick returned (the sign test dropped it)

The organ under test is the PROPOSED change, which is not in hdlab/ yet: the witness materialises
`notes/problems/<slug>/pick_identity_contract_patch.diff` into the cell's own data directory and loads it,
exactly as the cell does.  Once the diff is LANDED this file still passes unchanged (the materialised copy is
then byte-identical to hdlab/).

Run: .venv/Scripts/python.exe verification/test_pronoun_pick_identity_contract.py
"""
from __future__ import annotations
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)


def main():
    import experiments.exp_pronoun_pick_identity_contract_v1 as C
    print("THE PRONOUN PICK'S IDENTITY CONTRACT -- claims, not numbers")
    C.materialize(verbose=False)
    C.load_both(verbose=False)
    checks = C.witnesses(verbose=True)
    bad = [m for ok, m in checks if not ok]
    print("\nRESULT: %s" % ("PASS" if not bad else "FAIL (%d): %s" % (len(bad), bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
