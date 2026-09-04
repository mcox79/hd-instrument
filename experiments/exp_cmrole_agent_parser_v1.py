"""PARSER PROTOTYPE: does the in-repo glass-box arc parser's SUBJECT beat the register-general Competition-
Model competition on the who-did-what AGENT arm? This "proves out" the clause-structure lever with a real
parse instead of the crude `clause_bounds` heuristic.

The parser (hdlab.arc_parser richfeat, via route_predicate_arguments / SituationReader._router_roles) gives,
per verb, the grammatical subject ('agent') -- proper clause structure incl. relative clauses + commas that
the heuristic misses. It is glass-box + in-repo (NOT an external LLM). HONEST hypothesis: it is modern-trained
(UD-EWT); LitBank is 19c/OOD, so it may NOT beat the cue competition -- either outcome is informative.

Arms (referent_per_np ON except floor; tracked+pronoun agent candidate set; board AGENT scorer):
  pos_OFF          positional, ref OFF                       -> pre-referent baseline
  cm_pron_clause   CM competition + clause-local             -> the current best (glass-box, no parser)
  parser_pron      PARSER subject alone (no CM fallback)     -> isolates the parser's own agent recall
  parser_cm_pron   PARSER subject when it fires, CM fallback -> graded-precision hybrid

Run: .venv/Scripts/python.exe experiments/exp_cmrole_agent_parser_v1.py [--docs 16] [--heldout] [--nboot 2000]
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
from hdlab.situation_reader import SituationReader
from experiments.exp_cmrole_agent_board_v1 import CMAgentReader, AGENT_W, _score_doc, _boot

SEED = 20260904
OUT_DIR = os.path.join(_REPO, "data", "exp_cmrole_agent_parser_v1")
ARMS = ["pos_OFF", "cm_pron_clause", "parser_pron", "parser_cm_pron"]


def _reader(arm, gaz):
    if arm == "pos_OFF":
        return SituationReader(gaz=gaz, role_route="positional", referent_per_np=False)
    mode = {"cm_pron_clause": "cm", "parser_pron": "parser", "parser_cm_pron": "parser_cm"}[arm]
    clause = (arm == "cm_pron_clause")
    return CMAgentReader(gaz=gaz, role_route="positional", referent_per_np=True, cm_weights=AGENT_W,
                         cm_gaz=gaz, agent_source="coref", include_pron_agents=True,
                         clause_local=clause, agent_mode=mode)


def _measure(docset, gaz, wdw, nboot, label):
    per = {a: [] for a in ARMS}
    for doc in docset:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        for a in ARMS:
            sm = _reader(a, gaz).read(path)
            c, _ = _score_doc(sm, wdw[doc])
            per[a].append(np.array(c, float))
    acc = {a: float(np.concatenate(per[a]).mean()) for a in ARMS}
    n = int(sum(len(x) for x in per["cm_pron_clause"]))
    print("\n[%s]  n=%d" % (label, n))
    for a in ARMS:
        print("   %-16s acc=%.4f" % (a, acc[a]))
    tests = {}
    for lab, a, b in [("parser_pron    - cm_pron_clause", "parser_pron", "cm_pron_clause"),
                      ("parser_cm_pron - cm_pron_clause", "parser_cm_pron", "cm_pron_clause")]:
        d = _boot(per[a], per[b], nboot, SEED, doc_level=True)
        tests[lab] = d
        print("   %-32s d=%+.4f CI[%+.4f,%+.4f] sep=%s" % (lab, d["delta"], d["lo"], d["hi"], d["ci_sep"]))
    return {"acc": acc, "n": n, "tests": tests}


def run(n_docs=16, heldout=False, nboot=2000):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    gaz = SITQA.load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    total = 40 if heldout else n_docs
    alldocs = SITQA.load_docs(total)
    tuned = [d for d in alldocs[:n_docs] if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    print("=" * 92)
    print("PARSER vs COMPETITION on the who-did-what AGENT arm")
    out = {"anchor_name": "cmrole_agent_parser_v1", "tuned": _measure(tuned, gaz, wdw, nboot, "docs[0:%d]" % n_docs)}
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
