"""The architecture table makes checkable factual claims. Check them.

`hdlab/substrate.py`'s slot table is the only document recording whether an organ is wired, and
2026-08-22 it was found carrying a RESOLVED data-loss hazard as live: slot `D2` said
*"UNTRACKED IN GIT -- exists only in the working tree"* about `ca3_completer`, which had been
escalated as Q66 and committed at `f102e7081`. The claim was true when written and nothing re-checked
it.

These tests pin the claims a machine can verify. They deliberately do NOT check the judgement calls
(is `NEEDS_ADAPTER` the right status?) -- only the facts (does this file exist? is it really
untracked?).
"""

import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.slot_status import slots  # noqa: E402


def _tracked(path: str) -> bool:
    r = subprocess.run(["git", "ls-files", "--error-unmatch", path],
                       cwd=REPO_ROOT, capture_output=True, text=True)
    return r.returncode == 0


def _organ_paths():
    """(slot_id, organ, path) for slots naming an organ that maps to an hdlab module."""
    out = []
    for sid, _need, organ, _status, _rat in slots():
        if not organ:
            continue
        mod = organ.split(".")[0].strip()
        p = os.path.join("hdlab", mod + ".py")
        if os.path.isfile(os.path.join(REPO_ROOT, p)):
            out.append((sid, organ, p))
    return out


def test_the_table_is_parseable_and_populated():
    """POSITIVE CONTROL: if parsing silently returned nothing, every test below would vacuously pass."""
    rows = slots()
    assert len(rows) >= 10, "slot table parsed to %d rows -- the parser is broken" % len(rows)
    assert any(r[3] == "NEEDS_ADAPTER" for r in rows)
    assert any(r[3] == "FILLED" for r in rows)


def test_every_named_organ_resolves_to_a_file_or_is_explained():
    """A slot naming a module that no longer exists is a rename nobody propagated."""
    missing = []
    for sid, _need, organ, _status, _rat in slots():
        if not organ:
            continue
        mod = organ.split(".")[0].strip()
        if not os.path.isfile(os.path.join(REPO_ROOT, "hdlab", mod + ".py")):
            missing.append("%s -> hdlab/%s.py" % (sid, mod))
    # Not all organs are hdlab modules; this asserts the MAJORITY resolve, so a wholesale
    # rename breaks the test while a legitimately non-module organ does not.
    resolved = len(_organ_paths())
    assert resolved >= 8, ("only %d slot organs resolve to hdlab modules (missing: %s) -- "
                           "if the naming convention changed, change this test in the same commit"
                           % (resolved, missing[:6]))


def test_no_slot_claims_untracked_about_a_tracked_file():
    """The exact 2026-08-22 defect: a resolved data-loss hazard left standing in the doc."""
    wrong = []
    for sid, _need, organ, _status, rat in slots():
        if "UNTRACKED" not in rat.upper():
            continue
        mod = organ.split(".")[0].strip() if organ else ""
        p = os.path.join("hdlab", mod + ".py")
        if mod and os.path.isfile(os.path.join(REPO_ROOT, p)) and _tracked(p):
            # A row may narrate the resolved history; only an UNQUALIFIED claim is a defect.
            if "CORRECTED" not in rat.upper() and "WAS FIXED" not in rat.upper():
                wrong.append("%s says UNTRACKED but %s is tracked" % (sid, p))
    assert not wrong, "stale data-loss claim(s) in the slot table:\n  " + "\n  ".join(wrong)


def test_the_tracked_check_actually_works():
    """NEGATIVE/POSITIVE CONTROL on the helper itself.

    "no stale claims found" inherits every blindness of `_tracked`. If it returned True for
    everything the test above could never fail.
    """
    assert _tracked("hdlab/substrate.py"), "_tracked says a tracked file is untracked"
    assert not _tracked("hdlab/__this_file_does_not_exist_zzqq.py"), \
        "_tracked says a nonexistent file is tracked -- it cannot establish anything"
