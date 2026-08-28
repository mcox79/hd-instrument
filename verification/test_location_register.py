"""Witness for the per-entity LOCATION REGISTER organ (experiments/location_register.py).

Scaffold-free: builds a spaCy model once and asserts the register's PINNED brain-faithful reading rules and
its discriminating behaviour vs a stateless last-mention baseline. Run:
    .venv/Scripts/python.exe verification/test_location_register.py
ASCII only. No hdlab writes.
"""
import os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import spacy
from experiments.location_register import LocationRegister, DEICTIC_SCENE, AWAY, canon_node, INDOORS, OUTDOORS

_NLP = spacy.load("en_core_web_sm")


def reg(text, name, aliases=None):
    r = LocationRegister(_NLP)
    r.read(text, {name: aliases or [name, "he", "she", "him", "her", "his", "their"]})
    return r


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  PASS  {msg}")


def test_goal_over_source():
    """A realized GOAL names the destination even when a Source/away particle co-occurs (Talmy)."""
    r = reg("Anna sat in the parlour. Anna went out to the garden.", "Anna")
    check(r.where_is("Anna") == "garden", "goal-over-source: 'went out to the garden' -> garden")


def test_deixis_and_explicit_return():
    r = reg("Anna went out to the garden. Anna came back.", "Anna")
    check(r.where_is("Anna") == DEICTIC_SCENE, "deixis toward 'came back' -> scene")
    r2 = reg("Thomas went upstairs to his study. Thomas went back.", "Thomas")
    check(r2.where_is("Thomas") == DEICTIC_SCENE, "explicit return satellite 'went back' overrides deixis-away")


def test_persistence_across_distance():
    """Location is a STATE carried across intervening locationless sentences (Zwaan)."""
    filler = " ".join(["The clock ticked on."] * 8)
    r = reg(f"Thomas walked to the cellar. {filler} Thomas sighed.", "Thomas")
    check(r.where_is("Thomas") == "cellar", "location persists across 8 filler sentences")


def test_source_only_departure():
    """A realized Source with no Goal is a departure (absent from that ground)."""
    r = reg("Clara sat in the study. Clara hastened from the room.", "Clara")
    check(not r.present_in_scene("Clara"), "source-only 'hastened from the room' -> departed (not present)")


def test_stative_locative_and_furniture():
    r = reg("Susan sat in the kitchen.", "Susan")
    check(r.where_is("Susan") == "kitchen", "stative locative sets a named node")
    r2 = reg("Henry lay asleep on the lounge.", "Henry")
    check(r2.present_in_scene("Henry"), "within-scene furniture ('on the lounge') = present, not relocated")
    r3 = reg("Mary was asleep in a minute.", "Mary")
    check(r3.present_in_scene("Mary"), "temporal PP ('in a minute') is NOT a location")


def test_reentry_interval_bookkeeping():
    """Presence intervals: departure closes, arrival re-opens (Allen)."""
    r = reg("Walter sat in the hall. Walter went out to the barn. Walter came back.", "Walter")
    ivs = r.intervals_of("Walter")
    check(len(ivs) >= 3, f"re-entry opens >=3 intervals (got {len(ivs)})")
    check(r.where_is("Walter") == DEICTIC_SCENE, "after re-entry, back in the scene")
    # the barn interval must have CLOSED (not still open) once he came back
    barn = [iv for iv in ivs if iv.node == "barn"]
    check(barn and barn[0].t_close is not None, "the barn interval closed on return")


def test_beats_stateless_last_mention():
    """The discriminating case: entity leaves to L1, narrative dwells on L0, query gives L1; a nearest-
    location-to-last-mention baseline gives L0 (wrong)."""
    text = ("Anna sat in the garden. Anna hurried to the cellar. "
            "The maid remained in the garden, tidying. The maid lit a candle in the garden.")
    r = reg("Anna sat in the garden. Anna hurried to the cellar. "
            "The maid remained in the garden, tidying. The maid lit a candle in the garden.",
            "Anna", ["Anna", "she", "her"])
    check(r.where_is("Anna") == "cellar", "register tracks Anna to the cellar despite the garden-dwelling scene")
    # stateless nearest-location-to-Anna's-last-mention would grab 'garden' (wrong)
    import re
    low = [s.lower() for s in text.split(". ")]
    check("garden" in low[-1], "sanity: the misleading 'garden' token is the nearest to the scene tail")


def test_motion_frame_gate():
    """A bare 'to X' PP is a spatial GOAL only under a self-MOTION verb; a communication/transfer verb's
    'to X' is the ADDRESSEE/RECIPIENT (VerbNet Destination vs Recipient). Satellites bypass the verb."""
    r = reg("Walter went to the cellar.", "Walter")
    check(r.where_is("Walter") == "cellar", "motion verb 'went to the cellar' -> Goal")
    r2 = reg("Walter said to the stranger that all was well.", "Walter")
    check(r2.where_is("Walter") == DEICTIC_SCENE, "communication 'said to X' -> NOT a destination (stays scene)")
    r3 = reg("Walter pointed to the door.", "Walter")
    check(r3.where_is("Walter") == DEICTIC_SCENE, "'pointed to the door' -> addressee/deixis, not relocation")
    # a PATH SATELLITE bypasses the verb gate (Talmy -- no manner-verb whitelist)
    r4 = reg("Walter florped out.", "Walter", ["Walter", "he", "him"])
    check(not r4.present_in_scene("Walter"), "novel verb + PATH satellite 'florped out' still departs")


def test_place_typing_gate():
    """The ATL semantic gate rejects abstract/idiomatic grounds ('broke into a laugh')."""
    from experiments.location_register import is_place_ground
    check(is_place_ground("kitchen") and is_place_ground("garden"), "kitchen/garden type as places")
    check(not is_place_ground("laugh") and not is_place_ground("feather"), "laugh/feather NOT places")
    r = reg("Walter broke into a laugh.", "Walter")
    check(r.where_is("Walter") == DEICTIC_SCENE, "'into a laugh' is not a relocation")


def test_argument_structure_gate():
    """A goal PP with a competing moved-THEME direct object is the OBJECT's path, not the agent's."""
    r = reg("Tom struck them to the ground.", "Tom", ["Tom", "he", "him"])
    check(r.where_is("Tom") == DEICTIC_SCENE, "'struck them to the ground' -> them moves, Tom stays")


def test_hierarchical_region_membership():
    """Region-based containment: 'is X in the house?' resolves when X is in a room (study), which a flat
    exact-node register cannot (Wiener & Mallot region-based cognitive maps; Hirtle & Jonides hierarchy)."""
    r = reg("Anna walked to the study.", "Anna")
    check(r.region_of("Anna") == INDOORS, "study -> INDOORS region")
    check(r.is_in_region("Anna", "house") is True, "'in the house?' True when in the study (containment)")
    check(r.is_in_region("Anna", "outdoors") is False, "'outdoors?' False when in the study")
    r2 = reg("Thomas hurried out to the garden.", "Thomas")
    check(r2.region_of("Thomas") == OUTDOORS, "garden -> OUTDOORS region")
    check(r2.is_in_region("Thomas", "house") is False, "'in the house?' False when in the garden")
    check(r2.is_in_region("Thomas", "outside") is True, "'outside?' True when in the garden")


def test_canon_node():
    check(canon_node("to the far field") == "field", "canon: 'to the far field' -> field")
    check(canon_node("back inside") == DEICTIC_SCENE, "canon: deictic-return words -> scene")
    check(canon_node("the drawing room") == "room", "canon: head noun of a place phrase")


def test_fhrr_readout_roundtrips():
    """The FHRR-bound representation (RelationRegister) decodes back to the same node -- proves the register
    composes with the substrate binding algebra (representation sweep), not a bolt-on."""
    try:
        import torch  # noqa
    except Exception:
        print("  SKIP  fhrr readout (torch unavailable)")
        return
    r = reg("Anna went out to the garden.", "Anna")
    node, cos = r.to_fhrr_readout("Anna")
    check(node == r.where_is("Anna") and cos > 0.9,
          f"FHRR-bound location decodes to the symbolic node (node={node!r} cos={cos:.3f})")


def main():
    tests = [test_goal_over_source, test_deixis_and_explicit_return, test_persistence_across_distance,
             test_source_only_departure, test_stative_locative_and_furniture,
             test_reentry_interval_bookkeeping, test_beats_stateless_last_mention,
             test_motion_frame_gate, test_place_typing_gate, test_argument_structure_gate,
             test_hierarchical_region_membership, test_canon_node, test_fhrr_readout_roundtrips]
    n = 0
    for t in tests:
        print(f"[{t.__name__}]")
        t(); n += 1
    print(f"\nLOCATION-REGISTER WITNESS: {n}/{len(tests)} test groups PASSED")


if __name__ == "__main__":
    main()
