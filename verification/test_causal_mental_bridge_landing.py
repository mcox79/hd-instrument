"""LANDING WITNESS -- the MENTAL-BRIDGE causal path + the promoted event-TYPE organ
(owner-DONE a_force_dynamic_meaning_hub_causal_scorer_retire_the_connective_scoping_workaround, Q111, 2026-09-05).

Confirms the hdlab landing is FAITHFUL + a PURE ADD (default-on, no-default-off):
  1. hdlab.event_type.event_type is BYTE-IDENTICAL to the proof cell's event_type over a vocabulary, and hits the
     documented anchor cases (see->PERCEPTION, remember->COGNITION, fear->EMOTION, tell->COMMUNICATION).
  2. With causal_mental_bridge ON (default) vs OFF, on real board docs:
       - connective causal QA answers BYTE-IDENTICAL (the mental path fires ONLY on non-connective sentences, and
         the causal QA gold is connective-only -- so the ONE scored causal consumer cannot change);
       - events + coref digests BYTE-IDENTICAL;
       - goal WANT + goal-WHY QA answers BYTE-IDENTICAL (the board's goal scorers read sm.goal_register, which does
         NOT consume causal_links -- so the goal dim cannot change either);
       - the goal GRAPH is a strict SUPERSET (no node/edge removed; connective links emitted first -- the measured
         landing requirement);
       - the mental path ADDS >0 mental_bridge links (the upside -- crossing the mental wall the physical force
         lexicon cannot represent).
  3. all_capabilities_off() sets causal_mental_bridge False (baseline reproducibility).

The mental-bridge FIELD accuracy is not scored here (there is no live mental-causal instrument yet -- the mined
real-corpus gold is a filed follow-on); this witness proves the landing is faithful + regresses NOTHING on the
current board while enriching the situation model for the filed downstream consumers. Glass-box, NO LLM. ASCII.

Run: .venv/Scripts/python.exe verification/test_causal_mental_bridge_landing.py
"""
from __future__ import annotations
import os, sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.situation_reader import SituationReader
import hdlab.event_type as ET
import experiments.exp_causal_unified_bridge_event_type_v1 as PROOF

NDOCS = 12
_checks = []


def _ck(name, ok, detail=""):
    _checks.append((name, bool(ok), detail))
    print("  %s: %s%s" % ("ok" if ok else "FAIL", name, ("  -- " + detail) if detail else ""))


def _causal_qa(sm, sents):
    ans = {}
    for cl in sm.causal_links:
        ans.setdefault(SITQA._norm(cl.outcome), cl.cause)
    qs = SITQA.build_causal_questions(sm, sents)
    return tuple(sorted((SITQA._norm(q["outcome"]), ans.get(SITQA._norm(q["outcome"]))) for q in qs))


def _goal_qa(sm):
    out = []
    for q in SITQA.build_goal_questions(sm):
        out.append(("want", q["agent"], str(SITQA._answer_goal(sm, q))))
    for q in SITQA.build_goal_why_questions(sm):
        out.append(("why", str(q.get("agent")), str(q.get("action_head")), str(SITQA._answer_goal(sm, q))))
    return tuple(sorted(map(str, out)))


def _events_digest(sm):
    return tuple(sorted((e.sent_idx, str(e.predicate).lower(), str(getattr(e, "agent", None)).lower(),
                         str(getattr(e, "patient", None)).lower()) for e in sm.events))


def _coref_digest(sm):
    return tuple(sorted((r.sent_idx, str(r.pronoun).lower(), str(r.gold_cluster)) for r in (sm.coref_resolutions or [])))


def _graph_sig(sm):
    g = getattr(sm, "goal_graph", None)
    if g is None:
        return frozenset(), frozenset()
    nodes = frozenset(g.nodes.keys())
    edges = frozenset((c, p) for c, p in g.parent.items() if p is not None)
    return nodes, edges


def main():
    print("=" * 96)
    print("LANDING WITNESS: mental-bridge causal path + event-type organ")

    # (1) event_type byte-identity vs the proof cell + anchors
    ET._LEXCACHE.clear(); PROOF._LEXCACHE.clear()
    anchors = {"see": "PERCEPTION", "remember": "COGNITION", "fear": "EMOTION", "tell": "COMMUNICATION"}
    _ck("event_type anchors (see/remember/fear/tell)",
        all(ET.event_type(v) == t for v, t in anchors.items()),
        " ".join("%s=%s" % (v, ET.event_type(v)) for v in anchors))
    vocab = ["heard", "wept", "remembered", "smiled", "told", "sobbed", "learned", "understood", "beheld",
             "fainted", "feared", "gasped", "knew", "grieved", "noticed", "blushed", "ran", "hit", "broke",
             "gave", "saw", "thought", "spoke", "died", "walked", "pushed", "believed", "shouted", "trembled"]
    mism = [(v, ET.event_type(v), PROOF.event_type(v)) for v in vocab if ET.event_type(v) != PROOF.event_type(v)]
    _ck("event_type BYTE-IDENTICAL to the proof cell over %d verbs" % len(vocab), not mism, str(mism[:5]))

    # (2) pure-add on real board docs (off vs on)
    gaz = SITQA.load_given_gazetteer()
    docs = SITQA.load_docs(NDOCS)
    n = 0
    causal_id = goal_id = events_id = coref_id = graph_superset = 0
    total_mental = 0
    fails = []
    for doc in docs:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        if not os.path.exists(path):
            continue
        n += 1
        off = SituationReader(gaz=gaz, causal_mental_bridge=False).read(path)
        on = SituationReader(gaz=gaz, causal_mental_bridge=True).read(path)
        sents = SITQA._conll_sents(path)
        if _causal_qa(off, sents) == _causal_qa(on, sents):
            causal_id += 1
        else:
            fails.append(("causal_qa", doc))
        if _goal_qa(off) == _goal_qa(on):
            goal_id += 1
        else:
            fails.append(("goal_qa", doc))
        if _events_digest(off) == _events_digest(on):
            events_id += 1
        else:
            fails.append(("events", doc))
        if _coref_digest(off) == _coref_digest(on):
            coref_id += 1
        else:
            fails.append(("coref", doc))
        nb, eb = _graph_sig(off); ne, ee = _graph_sig(on)
        if nb <= ne and eb <= ee:
            graph_superset += 1
        else:
            fails.append(("goal_graph_not_superset", doc))
        total_mental += sum(1 for cl in on.causal_links if getattr(cl, "method", "") == "mental_bridge")

    _ck("connective causal QA byte-identical off-vs-on (%d/%d)" % (causal_id, n), causal_id == n)
    _ck("goal WANT+WHY QA byte-identical off-vs-on (%d/%d)" % (goal_id, n), goal_id == n)
    _ck("events byte-identical off-vs-on (%d/%d)" % (events_id, n), events_id == n)
    _ck("coref byte-identical off-vs-on (%d/%d)" % (coref_id, n), coref_id == n)
    _ck("goal graph strict SUPERSET off-vs-on (%d/%d)" % (graph_superset, n), graph_superset == n)
    _ck("mental-bridge ADDS causal coverage (+%d mental_bridge links, >0)" % total_mental, total_mental > 0)

    # (3) baseline reproducibility
    off_reader = SituationReader.all_capabilities_off(gaz=gaz)
    _ck("all_capabilities_off() sets causal_mental_bridge False", off_reader.causal_mental_bridge is False)

    npass = sum(1 for _n, ok, _d in _checks if ok)
    print("=" * 96)
    print("ALL %d CHECKS PASSED" % len(_checks) if npass == len(_checks) else "FAILED %d/%d (fails=%s)" % (
        len(_checks) - npass, len(_checks), fails[:6]))
    print("=" * 96)
    return 0 if npass == len(_checks) else 1


if __name__ == "__main__":
    sys.exit(main())
