"""Landing witness for the STRUCTURAL-DO recovery wire (default-off structural_do_recover) -- the coverage-gap §0g
item-2 lever. Proves: (a) the promoted primitive hdlab.structural_do.is_bare_do; (b) default-OFF byte-identical
(patient_is_bare_do stays None, the verb_subcat veto is unconditional); (c) flag-ON RECOVERS a bare post-verbal
direct object that verb_subcat vetoed on a low-transitivity verb (the 47 mis-vetoed 19c transitives); (d) it does
NOT over-recover a preposition-governed (oblique) nominal (intransitive/oblique precision preserved). Glass-box,
NO gold/LLM. Run: .venv/Scripts/python.exe verification/test_structural_do_recover_landing_organ.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.chdir(_REPO)

from hdlab.situation_reader import SituationReader
from hdlab.structural_do import is_bare_do, CLEAN_PREPS
from hdlab import verb_subcat as VS
from experiments._forward_prediction_live import get_tagger, read_sentence

_n = 0


def _ok(cond, msg):
    global _n
    assert cond, "FAIL: " + msg
    _n += 1
    print("  PASS " + msg, flush=True)


tagger = get_tagger()


def patients(reader, sent):
    toks = sent.split()
    up = tagger.tag(toks)
    evs = read_sentence(reader, toks, up)
    return {e.predicate: e.patient for e in evs}, evs


def main():
    # 1. PRIMITIVE (promoted verbatim)
    _ok(len(CLEAN_PREPS) == 59, "CLEAN_PREPS frozen at 59 prepositions")
    _ok(is_bare_do(["he", "rode", "the", "horse"], ["PRON", "VERB", "DET", "NOUN"], 1, 3),
        "is_bare_do: bare post-verbal nominal -> True (direct object)")
    _ok(not is_bare_do(["he", "sat", "on", "the", "chair"], ["PRON", "VERB", "ADP", "DET", "NOUN"], 1, 4),
        "is_bare_do: preposition-governed nominal -> False (oblique)")

    # precondition: 'ride' is a low-transitivity verb the verb_subcat gate vetoes
    _ok(VS.suppress_patient("ride", 0.35), "precondition: verb_subcat suppresses 'ride' (low-transitivity)")

    r_off = SituationReader(role_route="wired")                              # default: structural_do_recover OFF
    r_on = SituationReader(role_route="wired", structural_do_recover=True)

    # constructor/factory hygiene
    _ok("structural_do_recover" in SituationReader.CAPABILITY_FLAGS, "flag registered in CAPABILITY_FLAGS")
    _ok(r_off.structural_do_recover is False and SituationReader.all_capabilities_off().structural_do_recover is False,
        "default OFF + all_capabilities_off() covers it")

    # 2. DEFAULT-OFF byte-identical: patient_is_bare_do never set; veto unconditional (verb_subcat vetoes 'ride'
    #    even though a bare DO 'horse' is present -- the loss the fix recovers). (present tense -> predicate=='ride')
    poff, evoff = patients(r_off, "the men ride the horse")
    _ok(all(e.patient_is_bare_do is None for e in evoff), "default OFF: patient_is_bare_do stays None")
    _ok(poff.get("ride") == "?",
        "OFF: verb_subcat vetoes the transitive-use patient of the low-transitivity verb (ride -> '?')")

    # 3. FLAG-ON recovers the bare-DO patient the veto dropped (the 47 mis-vetoed transitives)
    pon, evon = patients(r_on, "the men ride the horse")
    _ok(pon.get("ride") == "horse", "ON: structural-DO override recovers the bare-DO patient (ride -> horse)")
    _ok(any(e.patient_is_bare_do for e in evon if e.predicate == "ride"),
        "ON: patient_is_bare_do is True for the recovered bare-DO event")

    # 4. PRECISION preserved: a preposition-governed (oblique) nominal is NOT recovered (still abstains)
    pon2, _ = patients(r_on, "the men sit on the bench")
    _ok(pon2.get("sit") == "?",
        "ON: oblique (prep-governed) nominal is NOT recovered (sit on bench -> '?', precision preserved)")

    print("%d/%d checks passed" % (_n, _n), flush=True)
    print("SELF-TEST PASSED", flush=True)


if __name__ == "__main__":
    main()
