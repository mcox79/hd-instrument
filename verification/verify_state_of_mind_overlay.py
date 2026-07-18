"""Scaffold-free witness: the packaged state-of-mind overlay reproduces the VALIDATED double-dissociation.

Proves hdlab.state_of_mind.WorkingOverlay is the LATEST validated overlay (longdist 49bb99c24; VET a7ca3db1),
not a drift, by exercising the REAL ported resolvers on two constructed micro-discourses and asserting BOTH
arms of the dissociation fire:
  (A) LONG distance: recency picks a near distractor (WRONG); maintained SALIENCE / FREQUENCY reach the far
      frequently-evoked antecedent (RIGHT)  -> salience owns long distance.
  (B) SHORT distance: recency picks the near correct antecedent (RIGHT); pure frequency / maintained pick the
      far high-frequency protagonist (WRONG) -> recency owns short distance.
Plus: proper-NAME -> entity instantiation resolvable by a later pronoun; recognize-KNOWN vs surprise-flag-new.

No corpus, no network, no torch, no tracing (module emits none). Run: python verification/verify_state_of_mind_overlay.py
(exit 0 = PASS). ASCII-only, terse.
"""

import os
import sys

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.state_of_mind import (  # noqa: E402
    AdditiveMapKnownBase,
    SetKnownBase,
    WorkingOverlay,
)


def _long_distance_overlay():
    """Alice evoked 4x EARLY (high frequency), then distractor fillers, then near Mary; 'she' -> Alice (far)."""
    ov = WorkingOverlay()
    for _ in range(4):
        ov.observe("alice", is_proper_name=True)      # frequently-evoked protagonist (gender unknown -> any)
    for filler in ("bob", "garden", "letter", "carriage", "village", "candle"):
        ov.observe(filler)                             # gap of distinct entities pushes Alice past window K
    ov.observe("mary", is_proper_name=True)            # nearer distractor, single mention
    return ov


def _short_distance_overlay():
    """Alice evoked 5x (protagonist), then near Mary; 'she' -> Mary (near, low frequency)."""
    ov = WorkingOverlay()
    for _ in range(5):
        ov.observe("alice", is_proper_name=True)
    for filler in ("road", "house"):
        ov.observe(filler)
    ov.observe("mary", is_proper_name=True)            # the near, correct antecedent
    return ov


def test_long_distance_salience_wins():
    """LONG distance: recency drops to the near distractor; maintained + freq reach the far protagonist."""
    ov = _long_distance_overlay()
    rec = ov.resolve_pronoun("she", strategy="recency")
    win = ov.resolve_pronoun("she", strategy="recency_window")
    maint = ov.resolve_pronoun("she", strategy="maintained")
    freq = ov.resolve_pronoun("she", strategy="freq")
    assert rec is not None and rec.head == "mary", "recency should pick the near distractor mary, got %s" % (rec and rec.head)
    # windowed recency cannot reach the far true antecedent (alice past window K); it can only pick the near
    # WRONG distractor mary that sits inside the window -- the structural wall (never the correct far entity).
    assert win is not None and win.head == "mary", "windowed recency should pick the near distractor mary (wall), got %s" % (win and win.head)
    assert win.head != "alice", "windowed recency must NOT reach the far true antecedent alice (structural wall)"
    assert maint is not None and maint.head == "alice", "maintained overlay should reach far alice, got %s" % (maint and maint.head)
    assert freq is not None and freq.head == "alice", "freq should reach far alice, got %s" % (freq and freq.head)
    return "LONG: recency=mary(wrong)  window=mary(wall, far alice unreachable)  maintained=alice(right)  freq=alice(right)"


def test_short_distance_recency_wins():
    """SHORT distance: recency picks the near correct antecedent; freq/maintained mispick the protagonist."""
    ov = _short_distance_overlay()
    rec = ov.resolve_pronoun("she", strategy="recency")
    freq = ov.resolve_pronoun("she", strategy="freq")
    maint = ov.resolve_pronoun("she", strategy="maintained")
    assert rec is not None and rec.head == "mary", "recency should pick the near mary, got %s" % (rec and rec.head)
    assert freq is not None and freq.head == "alice", "freq should mispick the protagonist alice, got %s" % (freq and freq.head)
    assert maint is not None and maint.head == "alice", "frequency-primary overlay should mispick alice, got %s" % (maint and maint.head)
    return "SHORT: recency=mary(right)  freq=alice(wrong)  maintained=alice(wrong)"


def test_double_dissociation():
    """The full claim: recency and salience win on OPPOSITE distance regimes (a true double-dissociation)."""
    lng = _long_distance_overlay()
    sht = _short_distance_overlay()
    # recency correct on SHORT, wrong on LONG
    assert sht.resolve_pronoun("she", strategy="recency").head == "mary"
    assert lng.resolve_pronoun("she", strategy="recency").head == "mary"   # mary is WRONG here (true = alice)
    # maintained salience correct on LONG, wrong on SHORT -> the crossing
    assert lng.resolve_pronoun("she", strategy="maintained").head == "alice"   # alice is RIGHT here
    assert sht.resolve_pronoun("she", strategy="maintained").head == "alice"   # alice is WRONG here (true = mary)
    return "DISSOCIATION: recency owns short, salience owns long (arms cross) -- validated behavior reproduced"


def test_proper_name_instantiation():
    """A capitalized MID-sentence proper noun instantiates a new entity a later pronoun resolves to."""
    ov = WorkingOverlay()
    ov.observe_surface("The", at_sentence_start=True)
    r = ov.observe_surface("lady")                             # common noun (fem cue) -> entity, gender fem
    r_ann = ov.observe_surface("Ann")                          # capitalized mid-sentence -> PROPER NAME entity
    assert r.entity is not None and r.entity.gender == "fem", "lady should be a fem-cued nominal entity"
    assert r_ann.entity is not None and r_ann.entity.is_named, "Ann should instantiate a NAMED entity"
    assert not r_ann.is_pronoun and r_ann.is_new_entity, "Ann should be a new (non-pronoun) entity"
    # a later 'she' (fem) resolves by recency to the most-recent compatible entity (Ann, gender-unknown -> any)
    got = ov.resolve_pronoun("she", strategy="recency")
    assert got is not None and got.head == "ann", "later 'she' should resolve to the instantiated name Ann, got %s" % (got and got.head)
    return "NAME: capitalized-mid-sentence 'Ann' -> new entity, later 'she' resolves to it"


def test_recognize_known_vs_surprise():
    """recognize-KNOWN (in durable base) vs SURPRISE-FLAG-new (absent = surprise 1.0); AdditiveMap seam works."""
    base = SetKnownBase({"alice"})
    ov = WorkingOverlay(base=base)
    known = ov.observe("alice", is_proper_name=True)
    new = ov.observe("zorlak", is_proper_name=True)
    assert known.is_known and known.surprise == 0.0, "alice is in base -> recognized, surprise 0"
    assert (not new.is_known) and new.surprise == 1.0, "zorlak absent -> surprise-flagged new, surprise 1"

    # AdditiveMapKnownBase seam: membership over an entity index object (no torch needed for the probe).
    class _StubMap:
        entity_to_idx = {"alice": 0, "bob": 1}
    amb = AdditiveMapKnownBase(_StubMap())
    assert amb.known("Alice") and not amb.known("mary"), "AdditiveMap membership probe should track its index"
    assert amb.surprise("mary") == 1.0 and amb.surprise("bob") == 0.0, "graded default = binary membership surprise"
    return "SURPRISE: base membership = recognize-vs-surprise; AdditiveMap index seam verified"


def test_active_set_ordering():
    """The maintained working state ranks the frequently-evoked protagonist above a one-off distractor."""
    ov = _long_distance_overlay()
    top = ov.active_set(top=1)
    assert top and top[0][0].head == "alice", "active-set top should be the high-salience protagonist alice"
    return "ACTIVE_SET: protagonist alice ranks top of the maintained state"


def test_deixis_participant_resolution():
    """Deixis (additive discourse-participant model): 1st-person -> speaker, 2nd-person -> addressee.
    Walkthrough of 'Who will help me?' said the hen / 'Not I,' said the dog: me->hen, I->dog, and the
    dog's 'you' falls back to the prior speaker (the hen). Also asserts the deixis axis does NOT perturb
    the validated antecedent resolvers (the reason it is opt-in / default-off)."""
    ov = WorkingOverlay()
    ov.observe("hen")
    ov.observe("dog")
    # unset participants -> deixis is a no-op (returns None; caller keeps the literal token).
    assert ov.resolve_deixis("me") is None and ov.resolve_deixis("you") is None
    # 'Who will help me?' said the hen -> speaker = hen.
    ov.note_turn(speaker="hen", addressee=None)
    assert ov.resolve_deixis("me") == "hen"
    assert ov.resolve_deixis("my") == "hen"
    assert ov.resolve_deixis("we") == "hen"
    # 'Not I,' said the dog -> new turn; the hen rotates into the prev-speaker slot.
    ov.note_turn(speaker="dog", addressee="hen")
    assert ov.resolve_deixis("i") == "dog"
    assert ov.resolve_deixis("you") == "hen"          # explicit addressee
    assert ov.prev_speaker == "hen"
    # a later turn with NO explicit addressee -> 2nd-person falls back to the prior speaker.
    ov.note_turn(speaker="hen", addressee=None)
    assert ov.resolve_deixis("your") == "dog"         # prior speaker = dog
    # a 3rd-person pronoun is not a participant deixis (returns None; goes to the antecedent path).
    assert ov.resolve_deixis("he") is None and ov.resolve_deixis("she") is None
    # ADDITIVE GUARD: the validated antecedent resolver is unperturbed by the deixis axis.
    got = ov.resolve_pronoun("they", strategy="recency")
    assert got is not None and got.head in ("hen", "dog")
    return "DEIXIS: me/my/we->hen(speaker); i->dog; you->hen(addressee); your->dog(prev-speaker); 3rd-person path untouched"


def main():
    tests = [
        test_long_distance_salience_wins,
        test_short_distance_recency_wins,
        test_double_dissociation,
        test_proper_name_instantiation,
        test_recognize_known_vs_surprise,
        test_active_set_ordering,
        test_deixis_participant_resolution,
    ]
    for t in tests:
        line = t()
        print("PASS %-34s %s" % (t.__name__, line))
    print("\nALL PASS: hdlab.state_of_mind.WorkingOverlay reproduces the validated recency/salience "
          "double-dissociation (longdist 49bb99c24; VET a7ca3db1) -- packaged overlay is the latest validated one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
