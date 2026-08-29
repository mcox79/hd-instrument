"""Witness for the LANDED hdlab.graded_coref_pick pool-cleanup (person-feature agreement candidate filter).

Landed 2026-08-29 from the integrated `the_reader_has_no_coherence_next_mention_prior` (the coherence prior was a
RIGOROUS NEGATIVE = full pass, owner-DONE/EXCELLENT: measured dead on the residual). Drilling surfaced a SEPARATE,
twin-controlled win: dropping mis-extracted 1st/2nd-person pronoun clusters ("I"/"we"/"my") from a 3rd-person pronoun's
candidate pool lifts full LitBank accuracy 0.775 -> 0.797 (+0.022 CI-sep [+0.007,+0.040]); the info-free random-drop
twin loses. Here the MECHANISM (the artifact classifier + the keep-filter) is witnessed store-agnostically.

Asserts:
  1. A 1st/2nd-person-ONLY pronoun cluster ("I","my","we") IS flagged as an artifact (excluded).
  2. A named-entity cluster ("Elizabeth","she") is NOT flagged (spared) -- a real referent.
  3. A purely 3rd-person-pronoun cluster ("he","him") is NOT flagged (no 1st/2nd member) -- agreement-compatible.
     3b. A pronoun-only cluster CONTAINING a 1st-person form IS flagged (contaminated). 3c. Empty -> not an artifact.
  4. keep_after_pool_cleanup drops exactly the artifact indices and preserves order.
  5. spaCy-FREE at runtime (no spacy imported).

Run: .venv/Scripts/python.exe verification/test_coref_pool_cleanup_organ.py
"""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.graded_coref_pick import is_first_second_person_artifact, keep_after_pool_cleanup  # noqa: E402


def main() -> int:
    checks = []

    # (1) 1st/2nd-person-only pronoun cluster -> artifact.
    checks.append((is_first_second_person_artifact(["I", "my", "we"]),
                   "[1] a 1st/2nd-person-only pronoun cluster IS flagged (mis-extracted speaker)"))
    # (2) named-entity cluster -> spared.
    checks.append((not is_first_second_person_artifact(["Elizabeth", "she", "her"]),
                   "[2] a named-entity cluster is NOT flagged (a real referent is spared)"))
    # (3) purely 3rd-person pronoun cluster -> spared (no 1st/2nd member).
    checks.append((not is_first_second_person_artifact(["he", "him", "his"]),
                   "[3] a purely 3rd-person-pronoun cluster is NOT flagged (agreement-compatible)"))
    # (3b) mixed 1st+3rd pronoun-only cluster IS an artifact (contaminated by a speaker pronoun).
    checks.append((is_first_second_person_artifact(["he", "I"]),
                   "[3b] a pronoun-only cluster containing a 1st-person form IS flagged (contaminated)"))
    # (3c) empty -> not an artifact.
    checks.append((not is_first_second_person_artifact([]),
                   "[3c] an empty cluster is not an artifact"))

    # (4) keep-filter drops exactly the artifact indices, order preserved.
    pool = [["Elizabeth", "she"], ["I", "my"], ["Darcy", "he"], ["we", "us"]]
    keep = keep_after_pool_cleanup(pool)
    checks.append((keep == [0, 2],
                   f"[4] keep_after_pool_cleanup drops the 1st/2nd-person artifacts, keeps real entities: {keep}"))

    # (5) spaCy-free.
    checks.append(("spacy" not in sys.modules,
                   f"[5] runtime is spaCy-FREE (no spacy in sys.modules): {'spacy' not in sys.modules}"))

    print("=== witness: hdlab.graded_coref_pick pool cleanup (person-feature agreement candidate filter) ===")
    all_pass = True
    for ok, msg in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        all_pass = all_pass and ok
    print(f"\nRESULT: {'ALL CHECKS PASS' if all_pass else 'FAIL'} ({sum(1 for ok, _ in checks if ok)}/{len(checks)})")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
