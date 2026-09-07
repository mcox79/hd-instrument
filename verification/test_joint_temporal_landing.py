"""Scaffold-free LANDING witness: joint_temporal_events wired into hdlab.situation_reader (Q111 P1 landing).

L1 FLAG ON -- the LIVE reader's TEMPORAL event set reproduces the survival/recall GAIN: driving the reader's own
   _build_joint_temporal_reasoner over TB-Dense (the promoted hdlab.joint_relation_frontend detection) recovers
   event recall ~0.76, FAR above the incumbent tense-gated ~0.32 (the wall the SOLVED removed).
L2 FLAG OFF -- BYTE-IDENTICAL to the pre-landing reader: reading the SAME passage with joint_temporal_events off vs
   on leaves sm.events + sm.timeline_order + sm.causal_links + sm.goals byte-identical (the wire is reasoner-side +
   additive; it touches ONLY what sm.temporal_reasoner() returns, never an existing field).
L3 the OFF temporal reasoner is the pre-landing tense-gated set (STRICTLY smaller than the ON enriched set), and
   all_capabilities_off() forces joint_temporal_events + joint_nominal_events False (the historical-weak reader is
   unaffected).

Glass-box, NO LLM. Requires data/corpora/tb_dense + the litbank conll fixture.
Run: .venv/Scripts/python.exe verification/test_joint_temporal_landing.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402,F401  (pins PYTHONHASHSEED=0 -> reproducible parse)

import hdlab.situation_reader as SR  # noqa: E402
from hdlab.temporal_reasoner import TemporalReasoner  # noqa: E402
from experiments._tbdense_loader import load_split  # noqa: E402
from experiments.exp_joint_temporal_survival_v1 import _sentences, nltk_event_ranks  # noqa: E402
from experiments.exp_temporal_extraction_recall_v1 import _words_and_ranks  # noqa: E402

_FIXTURE = os.path.join(_REPO, "data", "litbank", "coref", "conll", "1023_bleak_house_brat.conll")

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def _events_snapshot(sm):
    """A rich per-event tuple over the fields every downstream board dimension reads (who-did-what / state /
    causal / affect / polarity / precision). If joint_temporal_events were touching sm.events, this would move."""
    return [(e.global_idx, e.sent_idx, e.predicate, e.agent, e.patient, str(e.tense),
             e.subj_role, e.obj_role, e.affect, e.pred_idx,
             getattr(e, "polarity", None), getattr(e, "quantity", None),
             getattr(e, "patient_conf", None), getattr(e, "agent_conf", None),
             getattr(e, "event_conf", None)) for e in sm.events]


def main():
    # ---- L1: FLAG ON -- live reader temporal event recall reproduces the gain (>> incumbent 0.32) ----
    docs = load_split("train")
    r_on = SR.SituationReader(gaz={}, joint_temporal_events=True)
    inc_hit = inc_tot = on_hit = on_tot = 0
    for doc in docs:
        toks = doc["tokens"]
        words, wr = _words_and_ranks(toks)
        gold = {wr[e["tok"]] for e in doc["events"].values()
                if e["tok"] is not None and wr[e["tok"]] is not None}
        if not gold:
            continue
        sents = [st for st, _ in _sentences(toks)]
        tr = r_on._build_joint_temporal_reasoner(sents)
        det = {e.idx for e in tr.events}
        det_wr = {wr[i] for i in det if 0 <= i < len(wr) and wr[i] is not None}
        inc = nltk_event_ranks(words, tense_gated=True)
        inc_hit += len(inc & gold); inc_tot += len(gold)
        on_hit += len(det_wr & gold); on_tot += len(gold)
    recall_inc = inc_hit / inc_tot if inc_tot else 0.0
    recall_on = on_hit / on_tot if on_tot else 0.0
    chk("L1 FLAG ON: live reader temporal event recall >> incumbent (>0.6 and > incumbent+0.3)",
        recall_on > 0.60 and recall_on > recall_inc + 0.30,
        "incumbent %.4f -> joint_ON %.4f" % (recall_inc, recall_on))

    # ---- L2/L3: FLAG OFF byte-identical + OFF is the pre-landing tense-gated reasoner ----
    if not os.path.exists(_FIXTURE):
        chk("L2 byte-identity (fixture present)", False, "fixture absent: %s" % _FIXTURE)
        print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
        return 1 if FAIL else 0
    r_off = SR.SituationReader(gaz={}, joint_temporal_events=False)
    r_on2 = SR.SituationReader(gaz={}, joint_temporal_events=True)
    sm_off = r_off.read(_FIXTURE)
    sm_on = r_on2.read(_FIXTURE)
    ev_off, ev_on = _events_snapshot(sm_off), _events_snapshot(sm_on)
    chk("L2a sm.events BYTE-IDENTICAL off vs on (the wire never touches the event output)",
        ev_off == ev_on, "n_events off=%d on=%d equal=%s" % (len(ev_off), len(ev_on), ev_off == ev_on))
    fields_ok = True
    detail = []
    for fld in ("timeline_order", "timeline", "causal_links", "goals"):
        va = getattr(sm_off, fld, "__MISSING__"); vb = getattr(sm_on, fld, "__MISSING__")
        eq = (va == vb)
        fields_ok = fields_ok and eq
        detail.append("%s=%s" % (fld, eq))
    chk("L2b existing list fields (timeline_order/timeline/causal_links/goals) byte-identical off vs on",
        fields_ok, " ".join(detail))

    keys_off = set(sm_off.temporal_reasoner().event_keys())
    keys_on = set(sm_on.temporal_reasoner().event_keys())
    chk("L3a OFF reasoner is the pre-landing tense-gated set (STRICTLY smaller than the ON enriched set)",
        0 < len(keys_off) < len(keys_on),
        "off=%d keys, on=%d keys" % (len(keys_off), len(keys_on)))

    # L3b -- the MECHANISM directly: the ON builder recovers the DROPPED copular/stative STATE events ('open' in
    # 'the door was open'; 'nurse' in 'she is a nurse') that the pre-landing TemporalReasoner.from_text (tense-gated
    # VBD/had+VBN/be+VBN) drops entirely. A STATE is an event -- this is the exact channel the wall hid.
    sents_cop = [["The", "door", "was", "open", "."], ["She", "is", "a", "nurse", "."]]
    on_keys = set(r_on2._build_joint_temporal_reasoner(sents_cop).event_keys())
    ft_keys = set(TemporalReasoner.from_text("The door was open . She is a nurse .", lexical_aspect=True).event_keys())
    chk("L3b ON recovers the DROPPED copular/stative events the pre-landing from_text drops ('open'/'nurse')",
        {"open", "nurse"} <= on_keys and not ({"open", "nurse"} & ft_keys),
        "ON keys=%s | pre-landing from_text keys=%s" % (sorted(on_keys), sorted(ft_keys)))

    roff = SR.SituationReader.all_capabilities_off(gaz={})
    chk("L3c all_capabilities_off forces joint_temporal_events + joint_nominal_events False",
        roff.joint_temporal_events is False and roff.joint_nominal_events is False,
        "joint_temporal_events=%s joint_nominal_events=%s" % (roff.joint_temporal_events, roff.joint_nominal_events))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
