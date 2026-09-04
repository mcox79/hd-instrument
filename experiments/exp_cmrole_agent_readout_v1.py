"""READOUT FIX (the 54% AGGREGATION bucket): answer "who did {gov}?" by CONTEXT-CUED retrieval of the event
at the QUERIED sentence, not the board's last-matching-event collapse.

The gap decomposition (decompose_gap) showed 54% of the remaining cm_pron errors are AGGREGATION: the reader
assigned the gold agent correctly to SOME event with that verb, but `_answer_events` returns the LAST matching
event's agent across the whole passage and discards it. The WDW gold question is INSTANCE-specific (it carries
`sent` = the sentence of the gov_verb occurrence), so the board's global last-event readout is a scorer
artifact, not a mechanism failure.

BRAIN-FOUNDATIONAL fix: the brain answers "who did X" by CONTENT-ADDRESSABLE, CONTEXT-CUED retrieval from the
situation/episodic model (Lewis & Vasishth 2005 cue-based retrieval; the hippocampal event binding the
substrate already models with EventBundleCodec) -- the SENTENCE/recency is a retrieval cue that selects the
contextually-relevant event, not the most recent one globally. `answer_instanced` retrieves the matching-
predicate event NEAREST the queried sentence and returns its agent. This isolates the AGENT mechanism from the
readout artifact; it is applied to EVERY arm so the comparison stays fair.

Arms (referent_per_np ON except floor; board AGENT gold; instance-aware readout unless noted):
  pos_OFF                positional, ref OFF                       -> pre-referent baseline
  cm_pron_clause_LAST    full stack, BOARD last-event readout      -> the current number (0.42), for before/after
  cm_pron_clause         full stack, CONTEXT-CUED readout          -> THE FIX
  twin_clause            info-free (shuffled supports), cued readout -> MUST LOSE

Run: .venv/Scripts/python.exe experiments/exp_cmrole_agent_readout_v1.py [--docs 16] [--heldout] [--nboot 2000]
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.situation_reader import SituationReader, lemma_verb
from experiments.exp_cmrole_agent_board_v1 import CMAgentReader, AGENT_W, _boot

SEED = 20260904
OUT_DIR = os.path.join(_REPO, "data", "exp_cmrole_agent_readout_v1")


def _questions(rec):
    """Instance-specific who-did-what AGENT questions carrying the queried sentence (mirrors
    SITQA.build_events_questions but keeps `sent`)."""
    qs = []
    for m in rec.get("stream", []):
        if m.get("role") != "SUBJECT" or not m.get("gov_verb"):
            continue
        qs.append({"pred": m["gov_verb"], "gold": m["head_text"], "sent": int(m.get("sent", -1))})
    return qs


def answer_instanced(sm, q):
    """CONTEXT-CUED retrieval: the matching-predicate event NEAREST the queried sentence (recency/context is a
    retrieval cue). Ties -> the earliest. Returns the agent head, or None."""
    plem = lemma_verb(q["pred"]); S = q["sent"]
    best, bestkey = None, None
    for ev in sm.events:
        if lemma_verb(ev.predicate) != plem and SITQA._norm(ev.predicate) != SITQA._norm(q["pred"]):
            continue
        if ev.agent and ev.agent != "?":
            key = (abs(ev.sent_idx - S), ev.global_idx)
            if bestkey is None or key < bestkey:
                bestkey, best = key, ev.agent
    return best


def answer_last(sm, q):
    """The BOARD readout: last matching-predicate event's agent (global), ignoring the queried sentence."""
    plem = lemma_verb(q["pred"]); best = None
    for ev in sm.events:
        if lemma_verb(ev.predicate) != plem and SITQA._norm(ev.predicate) != SITQA._norm(q["pred"]):
            continue
        if ev.agent and ev.agent != "?":
            best = ev.agent
    return best


def _reader(arm, gaz):
    if arm == "pos_OFF":
        return SituationReader(gaz=gaz, role_route="positional", referent_per_np=False)
    twin = SEED if arm == "twin_clause" else None
    return CMAgentReader(gaz=gaz, role_route="positional", referent_per_np=True, cm_weights=AGENT_W,
                         cm_gaz=gaz, cm_twin_seed=twin, agent_source="coref", include_pron_agents=True,
                         clause_local=True)


def _measure(docset, gaz, wdw, nboot, label):
    arms = ["pos_OFF", "cm_pron_clause_LAST", "cm_pron_clause", "twin_clause"]
    per = {a: [] for a in arms}
    for doc in docset:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        readers = {}
        for a in arms:
            rarm = "cm_pron_clause" if a == "cm_pron_clause_LAST" else a
            if rarm not in readers:
                readers[rarm] = _reader(rarm, gaz).read(path)
            sm = readers[rarm]
            ans_fn = answer_last if a == "cm_pron_clause_LAST" else answer_instanced
            c = [int(SITQA._match(ans_fn(sm, q), q["gold"], "events")) for q in _questions(wdw[doc])]
            per[a].append(np.array(c, float))
    acc = {a: float(np.concatenate(per[a]).mean()) for a in arms}
    n = int(sum(len(x) for x in per["cm_pron_clause"]))
    print("\n[%s]  n=%d" % (label, n))
    for a in arms:
        print("   %-22s acc=%.4f" % (a, acc[a]))
    tests = {}
    for lab, a, b in [("readout fix: cued - LAST", "cm_pron_clause", "cm_pron_clause_LAST"),
                      ("cm_pron_clause - pos_OFF", "cm_pron_clause", "pos_OFF"),
                      ("cm_pron_clause - twin (info-free)", "cm_pron_clause", "twin_clause")]:
        d = _boot(per[a], per[b], nboot, SEED, doc_level=True)
        tests[lab] = d
        print("   %-34s d=%+.4f CI[%+.4f,%+.4f] hw=%.4f sep=%s"
              % (lab, d["delta"], d["lo"], d["hi"], d["ci_hw"], d["ci_sep"]))
    return {"acc": acc, "n": n, "tests": tests}


def run(n_docs=16, heldout=False, nboot=2000):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    gaz = SITQA.load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    total = 40 if heldout else n_docs
    alldocs = SITQA.load_docs(total)
    tuned = [d for d in alldocs[:n_docs] if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    print("=" * 92)
    print("CONTEXT-CUED READOUT (fix the 54% aggregation bucket)")
    out = {"anchor_name": "cmrole_agent_readout_v1", "tuned": _measure(tuned, gaz, wdw, nboot, "docs[0:%d]" % n_docs)}
    if heldout:
        held = [d for d in alldocs[16:40] if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
        out["held_out"] = _measure(held, gaz, wdw, nboot, "HELD-OUT docs[16:40]")
    print("=" * 92)
    out["elapsed_s"] = round(time.time() - t0, 1); out["ts_iso"] = datetime.now(timezone.utc).isoformat()
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[done] %.0fs -> %s" % (time.time() - t0, os.path.join(OUT_DIR, "metrics.json")))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", type=int, default=16)
    ap.add_argument("--heldout", action="store_true")
    ap.add_argument("--nboot", type=int, default=2000)
    args = ap.parse_args()
    run(args.docs, args.heldout, args.nboot)
