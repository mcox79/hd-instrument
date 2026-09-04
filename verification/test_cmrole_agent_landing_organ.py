"""LANDING witness for the Competition-Model AGENT role assigner promoted into hdlab (P2).

Unlike test_cmrole_agent_board_organ.py (which proves the SOLVER's shadow CMAgentReader), this witness
exercises the LANDED substrate directly:
  - hdlab.graded_role_assigner.agent_competition_pick (the promoted organ), and
  - hdlab.situation_reader.SituationReader with the landed flags cm_agent / include_pron_agents /
    case_filter / clause_local (NOT the experiment's CMAgentReader).

Two independent checks on the LIVE reader:
  A. AGENT RECOVERY (positional path -- reproduces the SOLVED proof): with referent_per_np ON, the landed
     cm_agent stack recovers the who-did-what AGENT arm to > the pre-referent baseline AND >> the pre-P2
     regression (cm_agent OFF over the dense set).
  B. PATIENT BYTE-IDENTITY (positional AND wired paths): the cm_agent change is AGENT-ONLY -- the event
     patient signatures are byte-identical between the cm_agent-ON and cm_agent-OFF readers (the +0.336
     PATIENT win preserved by construction). Also confirms the info-free twin (shuffled cue supports) loses.

Scores through the live board path (SITQA.build_events_questions -> SituationQA.answer -> _match), which
now carries the context-cued answer_instanced readout (default-on).

Run: .venv/Scripts/python.exe verification/test_cmrole_agent_landing_organ.py
"""
import os
import sys

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import json

import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.situation_reader import SituationReader

_PASS = []


def _ok(name, cond, detail=""):
    _PASS.append(bool(cond))
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name, ("  -- " + detail) if detail else ""))


def _docset(n, wdw):
    docs = SITQA.load_docs(n)
    return [d for d in docs if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]


def _agent_acc(reader, docset, wdw):
    """who-did-what AGENT accuracy through the live board scorer + the patient signatures per doc."""
    correct, pat = [], []
    for doc in docset:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        sm = reader.read(path)
        qa = SITQA.SituationQA(sm)
        for q in SITQA.build_events_questions(sm, wdw[doc]):
            _d, ans = qa.answer(q["question"], q)
            correct.append(int(SITQA._match(ans, q["gold"], "events")))
        pat.append([(ev.sent_idx, ev.predicate, ev.patient) for ev in sm.events])
    return float(np.mean(correct)) if correct else 0.0, pat


def run():
    gaz = SITQA.load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}

    # ---- A. AGENT RECOVERY on the positional path (reproduces the SOLVED proof through the LANDED reader) ----
    print("A. AGENT RECOVERY through the LANDED hdlab reader (positional path, %d docs)" % 8)
    ds = _docset(8, wdw)
    pre_ref = SituationReader(gaz=gaz, role_route="positional", referent_per_np=False)          # baseline
    landed_off = SituationReader(gaz=gaz, role_route="positional", referent_per_np=True, cm_agent=False)  # regression
    landed_on = SituationReader(gaz=gaz, role_route="positional", referent_per_np=True)          # full stack (defaults ON)

    a_base, pat_base = _agent_acc(pre_ref, ds, wdw)
    a_off, pat_off = _agent_acc(landed_off, ds, wdw)
    a_on, pat_on = _agent_acc(landed_on, ds, wdw)
    print("    pre-referent baseline (referent_per_np OFF)      acc=%.4f" % a_base)
    print("    regression (referent_per_np ON, cm_agent OFF)    acc=%.4f" % a_off)
    print("    LANDED full stack (cm_agent + pron + case + clause) acc=%.4f" % a_on)
    _ok("landed cm_agent recovers ABOVE the pre-referent baseline", a_on > a_base,
        "landed=%.4f baseline=%.4f" % (a_on, a_base))
    _ok("landed cm_agent recovers over the regression (large)", a_on > a_off + 0.10,
        "landed=%.4f regression=%.4f" % (a_on, a_off))

    # ---- B1. PATIENT BYTE-IDENTITY on the positional path (cm_agent ON vs OFF) ----
    print("\nB1. PATIENT byte-identity (positional path): landed cm_agent ON vs OFF")
    _ok("PATIENT signatures byte-identical (the +0.336 preserved)",
        all(pat_on[i] == pat_off[i] for i in range(len(ds))))

    # ---- B2. PATIENT BYTE-IDENTITY on the WIRED (live/default) path ----
    print("\nB2. PATIENT byte-identity (WIRED/live path): cm_agent ON vs OFF (%d docs)" % 4)
    dsw = _docset(4, wdw)
    wired_on = SituationReader(gaz=gaz)                       # DEFAULT reader: role_route=wired, cm_agent ON
    wired_off = SituationReader(gaz=gaz, cm_agent=False)      # same, cm_agent OFF
    _, pw_on = _agent_acc(wired_on, dsw, wdw)
    _, pw_off = _agent_acc(wired_off, dsw, wdw)
    _ok("WIRED PATIENT signatures byte-identical (cm_agent ON vs OFF)",
        all(pw_on[i] == pw_off[i] for i in range(len(dsw))))

    # ---- B3. info-free twin loses (shuffled cue supports carry no info) ----
    print("\nB3. info-free twin (shuffled cue supports) loses (positional path)")
    twin = SituationReader(gaz=gaz, role_route="positional", referent_per_np=True, cm_twin_seed=20260904)
    a_twin, _pt = _agent_acc(twin, ds, wdw)
    print("    info-free twin acc=%.4f  (landed full stack=%.4f)" % (a_twin, a_on))
    _ok("info-free twin loses to the landed cue competition", a_twin < a_on - 0.02,
        "twin=%.4f landed=%.4f" % (a_twin, a_on))


if __name__ == "__main__":
    run()
    n = len(_PASS); k = sum(_PASS)
    print("\n%d/%d PASS" % (k, n))
    sys.exit(0 if k == n else 1)
