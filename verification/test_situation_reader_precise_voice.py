"""Witness: PRECISE-VOICE patient selection in situation_reader (`the_reading_extractor` SOLVED, 2026-08-26).

Landing p5's proven win: on a PASSIVE clause the PATIENT is the SURFACE SUBJECT (before the predicate),
not the nearest nominal after it -- "the metal was dissolved by the acid" -> patient=metal, agent=acid.
Default-OFF (precise_voice=False) -> byte-identical to the shipped positional-no-voice behavior; ON + the
sentence tokens -> the voice flip. Brain-faithful: voice is the ONLY cue on reversible passives
(MacWhinney's Competition Model). Scaffold-free; writes nothing to any landed directory.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import _assign_roles, _is_passive_predicate


def _noms(*items):
    # items: (wtok_start, head, is_subject)
    return [{"wtok_start": w, "head": h, "is_subject": s} for (w, h, s) in items]


def test_passive_detector():
    assert _is_passive_predicate(["the", "metal", "was", "dissolved", "by", "the", "acid"], 3) is True
    assert _is_passive_predicate(["the", "vase", "was", "broken", "by", "him"], 3) is True   # irregular participle
    assert _is_passive_predicate(["the", "acid", "dissolved", "the", "metal"], 2) is False   # no BE-aux -> active
    assert _is_passive_predicate(None, 3) is False                                           # no tokens -> no signal
    print("PASS passive_detector")


def test_default_off_is_byte_identical():
    # PASSIVE sentence, DEFAULT (no voice): the shipped positional rule -- patient = nearest AFTER (WRONG),
    # agent = the before-subject. This is the behavior we must NOT change when the flag is off.
    toks = ["the", "metal", "was", "dissolved", "by", "the", "acid"]
    noms = _noms((1, "metal", True), (6, "acid", False))
    assert _assign_roles(3, noms) == ("metal", "acid")                       # default: precise_voice=False
    assert _assign_roles(3, noms, toks=toks) == ("metal", "acid")            # toks WITHOUT the flag -> still unchanged
    print("PASS default_off_is_byte_identical")


def test_precise_voice_flips_the_passive():
    toks = ["the", "metal", "was", "dissolved", "by", "the", "acid"]
    noms = _noms((1, "metal", True), (6, "acid", False))
    # CORRECT: metal is the PATIENT (surface subject), acid is the AGENT (by-phrase)
    assert _assign_roles(3, noms, toks=toks, precise_voice=True) == ("acid", "metal")
    # agentless passive: "the metal was dissolved" -> patient=metal, agent='?'
    noms2 = _noms((1, "metal", True))
    a2, p2 = _assign_roles(3, noms2, toks=["the", "metal", "was", "dissolved"], precise_voice=True)
    assert p2 == "metal", (a2, p2)
    print("PASS precise_voice_flips_the_passive")


def test_active_clause_unchanged_even_with_flag_on():
    # ACTIVE clause: no BE-aux -> not passive -> flag ON must NOT flip.
    toks = ["the", "acid", "dissolved", "the", "metal"]
    noms = _noms((1, "acid", True), (4, "metal", False))
    assert _assign_roles(2, noms, toks=toks, precise_voice=True) == ("acid", "metal")
    print("PASS active_clause_unchanged_even_with_flag_on")


if __name__ == "__main__":
    test_passive_detector()
    test_default_off_is_byte_identical()
    test_precise_voice_flips_the_passive()
    test_active_clause_unchanged_even_with_flag_on()
    print("4/4 WITNESSES PASSED")
