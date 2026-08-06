"""Scaffold-free witness for hdlab/consequence_learning_loop.py (tracing=False; no framework scaffold).

NOT a pytest-collected cert test (filename is witness_*.py, and pyproject python_files=["test_*.py"]),
so it deliberately does NOT perturb the locked 220-passed/3-skipped certification count -- it is a
runnable, scaffold-free construction witness per the repo's "every feature ships a witness in
verification/" convention. Run directly: `.venv/Scripts/python.exe verification/witness_consequence_
learning_loop_oov_valence.py`.

Witnesses (all on HAND-AUTHORED micro-episodes, no corpus, no tracing):
  W1 the teacher signal is congruence_decision's OWN MET/UNMET (NOT any reward theta): fires MET and
     UNMET when Signal A and Signal B agree; abstains on no-outcome.
  W2 credit assignment is STRUCTURAL referent-linkage: a referent-linked OOV verb is credited; a
     bystander OOV verb (different-referent clause: savings/drawer) is NOT -- structural exclusion, no
     stoplist.
  W3 the 3-way consolidation reuses the abstain-band architecture: POS / NEG / GROUNDED_NEUTRAL /
     PENDING per the registered bands; a balanced (both-poles) verb washes to GROUNDED_NEUTRAL, it does
     NOT abstain and is NOT force-polarized (the light-verb payoff, at the mechanism level).
  W4 the module NEVER imports the reward-earned appraisal family (pfc_gate_cfrpe /
     context_grounded_valence / grounded_appraisal_sim) -- source-level assertion that the wrong
     mechanism was avoided.
  W5 the Tier-3 overlay is EMPTY at import (no production/cert side effect).
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import consequence_learning_loop as CLL
from hdlab.consequence_learning_loop import (
    teacher_verdict, consolidate, _credit_targets,
)
from hdlab import verb_lexical_similarity as vls


def witness():
    # W5: overlay empty at import (no production side effect).
    assert vls.ACQUIRED_OUTCOME_VERB_FEATURES == {}, "Tier-3 overlay must be EMPTY at import"

    # W1: teacher = congruence's own MET/UNMET (dual-signal AND-gate).
    g_save = "Owen wanted to save the boat before the storm hit"
    assert teacher_verdict(g_save, "The men worked hard. The boat sank in the storm.") == "UNMET"
    g_mend = "Owen wanted to mend the canoe before the flood came"
    assert teacher_verdict(g_mend, "The men worked all night. The canoe mended by dawn.") == "MET"
    assert teacher_verdict(g_save, "Nothing at all happened here today.") is None

    # W2: structural referent-linked credit (bystander excluded, no stoplist).
    tgts = _credit_targets("Nell tinkered the lantern and the savings dwindled in the drawer.", "lantern")
    assert "tinker" in tgts and "dwindle" not in tgts, f"credit must be referent-linked, got {tgts}"

    # W3: 3-way consolidation honoring the registered bands (light-verb payoff at mechanism level).
    assert consolidate({"x": {"POS": 3, "NEG": 0}})["x"] == "POS"
    assert consolidate({"x": {"POS": 0, "NEG": 3}})["x"] == "NEG"
    assert consolidate({"x": {"POS": 3, "NEG": 3}})["x"] == "GROUNDED_NEUTRAL"  # balanced -> washes out
    assert consolidate({"x": {"POS": 1, "NEG": 0}})["x"] == "PENDING"           # < MIN_CONFIRM

    # W4: the wrong mechanism (reward-earned appraisal theta) is never IMPORTED (scan import lines
    # only -- the docstring legitimately NAMES these modules to explain why they are avoided).
    import_lines = [ln for ln in open(CLL.__file__, "r", encoding="utf-8").read().splitlines()
                    if ln.strip().startswith(("import ", "from "))]
    for banned in ("pfc_gate_cfrpe", "context_grounded_valence", "grounded_appraisal_sim"):
        assert not any(banned in ln for ln in import_lines), \
            f"consequence_learning_loop must NOT import {banned} (the VET-confirmed wrong mechanism)"

    vls.clear_acquired_outcome()
    print("WITNESS PASS: teacher=congruence MET/UNMET (not theta); structural referent-linked credit; "
          "3-way abstain-band consolidation; wrong-mechanism avoided; overlay empty at import.")
    return True


if __name__ == "__main__":
    ok = witness()
    raise SystemExit(0 if ok else 1)
