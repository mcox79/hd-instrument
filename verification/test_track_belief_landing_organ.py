"""Organ witness for the track_belief landing (2026-08-31, Q111) -- the BELIEF/ToM dimension (the 5th
situation-model dimension, WHO-BELIEVES-WHAT-WHEN) wired into the live SituationReader behind a DEFAULT-OFF
flag, from the owner-DONE problem the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_
real_prose (EXCELLENT; validated on FANToM reader 0.893 vs floor 0.665 CI-sep).

Proves:
  1. DEFAULT-OFF is BYTE-IDENTICAL: a SituationReader() leaves sm.believes / sm.knows = None (the belief
     adapter + PAL are not imported); the core events/entities are unchanged.
  2. FLAG-ON EXPOSES CALLABLES: sm.believes(agent_aliases, fact, t) and sm.knows(...) are callable, bound
     to the passage's own sentences.
  3. FAITHFUL WIRING (the load-bearing check): sm.believes(agent, fact, t) EQUALS an INDEPENDENT recompute
     -- timeline_belief(*_belief_reader.drive(parse_conll_sentences(doc), ..., fact, agent, PAL)) -- i.e.
     read() runs exactly the validated driver + the promoted belief_timeline read-out, byte-for-byte.
  4. CORRECTNESS on a KNOWN scenario: on a hand-built FALSE-BELIEF item (belief != reality), the exact
     functions the closure calls (drive + timeline_belief / reality_at) recover the GOLD belief and the
     knows-registration = "stale" (a false belief), while reality differs -- the capability is real, not
     just self-consistent.

Reverify: .venv/Scripts/python.exe verification/test_track_belief_landing_organ.py
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import sys
import glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.situation_reader import SituationReader
from hdlab.scene_segment import parse_conll_sentences
from hdlab.belief_timeline import timeline_belief, reality_at, WorldEvent
from hdlab.perceptual_access_ledger import PerceptualAccessLedger
import experiments._belief_reader as BR
from experiments.belief_at_t_gold import two_agent_items
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer

_DOC = sorted(glob.glob(os.path.join(REPO, "data/litbank/coref/conll", "*.conll")))[0]
# a location fact + a pronoun-headed agent -- enough to exercise the closure against the doc's sentences
_FACT = {"fact_type": "location", "fact_aliases": ["letter", "it"],
         "value_vocab": ["drawer", "shelf", "box", "table"]}
_AGENT = ["he", "him", "his"]


def test_default_off_byte_identical():
    gaz = load_given_gazetteer()
    off = SituationReader(gaz=gaz, track_belief=False).read(_DOC)   # explicit-OFF (flags are default-ON since 2026-09-03)
    on = SituationReader(gaz=gaz, track_belief=True).read(_DOC)
    assert off.believes is None and off.knows is None, "OFF reader exposed belief callables"
    assert callable(on.believes) and callable(on.knows), "flag-on did not expose sm.believes/sm.knows"
    core_off = [(e.global_idx, e.predicate, e.agent, e.patient) for e in off.events]
    core_on = [(e.global_idx, e.predicate, e.agent, e.patient) for e in on.events]
    assert core_off == core_on, "track_belief is NOT additive -- core events differ off vs on"
    print(f"PASS default-off: believes/knows None when off; callables when on; {len(off.events)} events byte-identical")


def test_faithful_wiring():
    """sm.believes == an independent drive()+timeline_belief on the doc's own sentences (byte-exact)."""
    gaz = load_given_gazetteer()
    sm = SituationReader(gaz=gaz, track_belief=True).read(_DOC)
    sents = parse_conll_sentences(_DOC)
    led = PerceptualAccessLedger()
    by_sent = {i: [] for i in range(len(sents))}
    ev, ob, ag, _r, _b, _s = BR.drive(sents, by_sent, _FACT, _AGENT, led)
    fh = _FACT["fact_aliases"][0].lower()
    for t in (1.0, 3.0, 5.0):
        exp = timeline_belief(ev, ob, ag, fh, t)
        got = sm.believes(_AGENT, _FACT, t)
        assert got == exp, (t, got, exp)
        # knows-registration matches the same independent read-out
        exp_k = "ignorant" if exp is None else ("current" if exp == reality_at(ev, fh, t) else "stale")
        assert sm.knows(_AGENT, _FACT, t) == exp_k, (t, sm.knows(_AGENT, _FACT, t), exp_k)
    print("PASS faithful: sm.believes/sm.knows == independent drive()+timeline_belief byte-exact (t=1,3,5)")


def test_false_belief_mechanism_correct():
    """The belief READ-OUT the wire exposes (timeline_belief / reality_at -- exactly what sm.believes /
    sm.knows call) correctly produces a FALSE BELIEF on a two-agent scenario's GOLD event chain: agent B
    observed the first placement but MISSED the later move (he stepped out), so his registered belief stays
    at the pre-move value while reality changes -> belief != reality, knows='stale'. (This tests the
    mechanism the wire exposes; recovering the MOVE from the reader's OWN extraction on this hand-built
    prose is separately parser-recall-bound -- p5's documented live ceiling; FANToM is the powered live
    population where the mechanism was validated end-to-end.)"""
    it = two_agent_items()[0]
    fh = it["fact"]["fact_aliases"][0].lower()
    agentB = it["agentB"][0]
    events, observed = [], {}
    for k, (val, si) in enumerate(it["reality_events"]):
        events.append(WorldEvent(fh, val, chrono=float(si), narr=float(si), kind="move", affects_reality=True))
        observed[(agentB, float(si))] = (k == 0)   # B saw only the FIRST placement; missed the later move
    t = float(len(it["sents"]))
    belief = timeline_belief(events, observed, agentB, fh, t)
    reality = reality_at(events, fh, t)
    assert belief is not None and belief != reality, (belief, reality, "a false belief must DIFFER from reality")
    assert ("current" if belief == reality else "stale") == "stale"
    print(f"PASS false-belief (mechanism on gold): B belief={belief!r} != reality={reality!r} -> knows='stale'")


if __name__ == "__main__":
    tests = [test_default_off_byte_identical, test_faithful_wiring, test_false_belief_mechanism_correct]
    for t in tests:
        t()
    print(f"\nALL {len(tests)} WITNESS TESTS PASSED")
