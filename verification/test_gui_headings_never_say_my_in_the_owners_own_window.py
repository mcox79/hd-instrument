"""No owner-facing GUI heading may use a FIRST-PERSON pronoun.

WHY THIS EXISTS, AND WHY IT IS CODE RATHER THAN A COMMENT.

The owner, 2026-08-23, on the problems tab, verbatim:

    "there are a few problems that were completed by the solver in the problems tab that you say
     you're waiting on me 'Yes - re-verify' - what does that mean? Am I supposed to do anything?
     It's really not clear if that's 'you' - Opus 5, or me, the user."

The column read "WAITING ON ME?". It was written from Claude's point of view, and displayed in a
window the OWNER reads -- so "me" resolves to the reader, and the label means the opposite of what
it says. It was fixed to "WHOSE MOVE?", and a comment was added saying never to do it again.

**THE COMMENT DID NOT HOLD, AND IT FAILED IN BOTH DIRECTIONS.** It banned "a first- or second-person
pronoun", which is:

  - too BROAD: "YOU SAY" / "YOUR VERDICT" address the reader and resolve CORRECTLY. Banning them
    would make the window worse.
  - too NARROW in practice: "MY RATING" sat on the NEXT LINE, unfixed, for a full day. It is
    Claude's rating, displayed to the owner as "my". Exactly the reported defect, surviving the fix
    for it, one line below the rule forbidding it.

That is the project's most-repeated lesson: a caution written as prose gets violated; a control
written as code catches something. So the rule now lives here.

THE RULE: first person is banned in an owner-facing heading -- NAME THE ACTOR ("CLAUDE RATES IT").
Second person is fine when it means the reader.
"""

import io
import os
import re

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUI = os.path.join(_REPO, "tools", "status_gui.py")

# FIRST-PERSON SINGULAR ONLY, and the singular/plural split is the whole rule rather than a
# convenience. Drafting this test with an allowlist of blessed strings was the wrong shape: it
# immediately flagged "WHAT WOULD MAKE US STOP" and "WHERE THAT LEAVES US", which are FINE, and the
# fix would have been to keep pasting strings into an exemption list until it went quiet -- a
# detector tuned until it stops complaining measures nothing.
#
# The principled line:
#   MY / ME / MINE / I  -> can ONLY mean Claude. In the owner's own window it reads as the OWNER.
#                          Always wrong here. This is the reported defect.
#   WE / US / OUR       -> mean the project INCLUDING the reader. "Where that leaves us" is exactly
#                          right and needs no exemption.
# So there is no allowlist, and there is nothing for a future heading to hide behind.
FIRST_PERSON = re.compile(r"\b(MY|ME|MINE|I)\b", re.IGNORECASE)


def _heading_strings(text):
    """Every string literal inside a headings=(...) tuple, with its line number."""
    out = []
    for m in re.finditer(r"headings=\(", text):
        depth, i = 0, m.end() - 1
        while i < len(text):
            if text[i] == "(":
                depth += 1
            elif text[i] == ")":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        block = text[m.end() - 1:i + 1]
        line = text[:m.start()].count("\n") + 1
        for s in re.findall(r'"([^"]*)"', block) + re.findall(r"'([^']*)'", block):
            if s.strip():
                out.append((line, s))
    return out


def test_the_gui_exposes_headings_to_check():
    """POSITIVE CONTROL. Without this, a broken extractor makes the real test pass vacuously --
    'no offending headings found' would be indistinguishable from 'no headings found'."""
    text = io.open(GUI, encoding="utf-8").read()
    found = _heading_strings(text)
    assert len(found) >= 30, "extractor found only %d heading strings; it is broken" % len(found)
    flat = [s for _, s in found]
    assert "PROBLEM" in flat, "did not find a known heading; the extractor is not reading real data"
    assert "WHOSE MOVE?" in flat, "the already-fixed heading is missing -- extractor or file changed"


def test_no_owner_facing_heading_speaks_in_the_first_person():
    text = io.open(GUI, encoding="utf-8").read()
    bad = []
    for line, s in _heading_strings(text):
        m = FIRST_PERSON.search(s)
        if m:
            bad.append((line, s, m.group(0)))
    assert not bad, (
        "owner-facing heading(s) speak in the first person -- 'my'/'me' means Claude but reads as "
        "the OWNER in the owner's own window. Name the actor instead (e.g. 'CLAUDE RATES IT'):\n"
        + "\n".join("  status_gui.py:%d  %r  (pronoun: %s)" % b for b in bad)
    )


def test_the_whole_pipeline_would_catch_the_regression_reappearing():
    """END-TO-END POSITIVE CONTROL: extractor + rule together, on synthetic source.

    The regex tests below prove the RULE works on a bare string. They do not prove the EXTRACTOR
    would ever hand that string to the rule -- and an extractor that silently returns nothing is
    how "no offending headings found" becomes a lie. This runs the real pipeline over source text
    that contains the exact heading that shipped."""
    regressed = '''
        self._table(
            cols=("a", "b"),
            headings=("PROBLEM", "MY RATING"),
            height=9)
    '''
    found = _heading_strings(regressed)
    assert ("MY RATING" in [s for _, s in found]), "extractor did not surface the injected heading"
    flagged = [s for _, s in found if FIRST_PERSON.search(s)]
    assert flagged == ["MY RATING"], "pipeline failed to flag the regression, got %r" % flagged

    clean = '''
            headings=("PROBLEM", "CLAUDE RATES IT", "WHERE THAT LEAVES US"),
    '''
    assert not [s for _, s in _heading_strings(clean) if FIRST_PERSON.search(s)], \
        "pipeline flags the CORRECTED headings -- it would cry wolf and get disabled"


def test_the_detector_catches_the_heading_that_actually_shipped():
    """NEGATIVE CONTROL on the real regression. 'MY RATING' shipped and survived a fix aimed at it;
    a detector that cannot flag it is worthless. Also assert the second-person forms it must NOT
    flag, or the rule creeps back to the over-broad version that caused the miss."""
    assert FIRST_PERSON.search("MY RATING"), "detector misses the heading that actually shipped"
    assert FIRST_PERSON.search("WAITING ON ME?"), "detector misses the originally-reported heading"
    for ok in ("YOU SAY", "YOUR VERDICT AND NOTES ON THE SELECTED PROBLEM", "WHOSE MOVE?",
               "CLAUDE RATES IT", "WHAT NEEDS YOUR DECISION",
               # first-person PLURAL means the project including the reader, and is correct.
               # These are real headings in the file; if the rule ever bans them it has drifted
               # back to the over-broad version that let MY RATING through.
               "WHAT WOULD MAKE US STOP", "WHERE THAT LEAVES US",
               "CAN WE MEASURE IT ALONE?", "HOW CLOSELY WE COPY THE BRAIN"):
        assert not FIRST_PERSON.search(ok), (
            "detector flags %r, which addresses or includes the reader and is correct -- this is "
            "the over-broad rule that let MY RATING through" % ok)
