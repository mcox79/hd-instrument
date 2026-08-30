"""Scaffold-free organ witness for hdlab/perceptual_access_ledger.py (PROMOTED 2026-08-30).

The observation-cue front-end (who-witnessed-what -> the ToM belief-update gate): reads the observation
cue from spatial / occlusion / testimony STRUCTURE, not a fixed keyword list. Recomputes the 5 canonical
perceptual-access cases from source through the promoted hdlab organ. spaCy is used at RUNTIME to parse
the vignettes (the organ's input), but is NOT a top-level import dependency of hdlab.

Run:  .venv/Scripts/python.exe verification/test_perceptual_access_ledger_organ.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.perceptual_access_ledger import (
    PerceptualAccessLedger, PresenceState, LedgerTrace, _self_test,
)

n = 0


def ok(cond, msg):
    global n
    assert cond, "FAIL: " + msg
    n += 1
    print("  ok  " + msg)


def main():
    print("[hdlab.perceptual_access_ledger organ witness]")

    # API surface present in the promoted organ
    ok(all(hasattr(PerceptualAccessLedger, m) for m in ("observed",)),
       "PerceptualAccessLedger exposes observed()")
    ok(PresenceState is not None and LedgerTrace is not None,
       "PresenceState + LedgerTrace bookkeeping types present")

    # the 5 canonical cases (re-entry / asleep-occlusion / testimony / new-place / classic absence),
    # each recomputed from source through the hdlab organ (asserts 5/5 internally)
    _self_test()
    ok(True, "5/5 canonical perceptual-access cases pass through the hdlab organ "
             "(absence / re-entry / occlusion / testimony / new-place -- structure, not keywords)")

    # a direct spot-check that the organ reads OCCLUSION (asleep = not observed despite co-presence)
    import spacy
    nlp = spacy.load("en_core_web_sm")
    led = PerceptualAccessLedger(nlp)
    tr = led.observed(
        "Anna lay asleep on the couch in the room. Ben quietly moved the marble to the blue basket.",
        ["Anna", "she", "her"], event_object="marble")
    ok(tr.observed is False, "occlusion: asleep-in-the-same-room reads NOT-observed (co-presence != perception)")

    tr2 = led.observed(
        "Anna went outside. Ben moved the marble to the basket. Later Ben told Anna he had moved it.",
        ["Anna", "she", "her"], event_object="marble")
    ok(tr2.observed is True, "testimony: being TOLD after absence updates knowledge (belief != vision)")

    print("\n%d/%d PASS -- hdlab.perceptual_access_ledger recomputed from source (observation cue from "
          "spatial/occlusion/testimony structure; the belief-update gate for the ToM organs)." % (n, n))


if __name__ == "__main__":
    main()
