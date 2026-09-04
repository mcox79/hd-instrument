"""OPTIMIZATION: bound the Competition-Model AGENT candidates to the verb's CLAUSE span (incremental clause
segmentation) instead of the whole multi-clause sentence.

Brain-foundational basis: reading is INCREMENTAL and role assignment is CLAUSE-BOUNDED -- an argument competes
within its own clause (the parser builds clause structure on the fly; clause boundaries are marked by
subordinators, clause-level coordinators, and strong punctuation). The subject search stops at the clause edge.
The SOLVED agent competition pooled candidates over the whole sentence; in 19c prose (long multi-clause
sentences) that lets one agent leak across clauses. `clause_bounds` (glass-box, toks/pos only) restricts each
verb's candidates to its clause span. Relativizers are deliberately NOT boundaries (they embed).

ARMS (referent_per_np ON except the floor; board who-did-what AGENT scorer):
  pos_OFF          positional, ref OFF                 -> pre-referent baseline (0.2257)
  cm_pron          CM agent + subject pronouns          -> the current best (0.4082)
  cm_pron_clause   + CLAUSE-LOCAL candidate bounding     -> THE OPTIMIZATION
  twin_clause      cm_pron_clause with shuffled supports -> info-free, MUST LOSE

Reports the full-16 (tuned) AND docs[16:40] (held-out) so the optimization is shown to generalize, not overfit.

Run: .venv/Scripts/python.exe experiments/exp_cmrole_agent_clause_v1.py [--nboot 2000]
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
OUT_DIR = os.path.join(_REPO, "data", "exp_cmrole_agent_clause_v1")


def _reader(arm, gaz):
    if arm == "pos_OFF":
        return SituationReader(gaz=gaz, role_route="positional", referent_per_np=False)
    twin = SEED if arm == "twin_clause" else None
    clause = arm in ("cm_pron_clause", "twin_clause")
    return CMAgentReader(gaz=gaz, role_route="positional", referent_per_np=True, cm_weights=AGENT_W,
                         cm_gaz=gaz, cm_twin_seed=twin, agent_source="coref",
                         include_pron_agents=True, clause_local=clause)


def _measure(docset, gaz, wdw, nboot, label):
    arms = ["pos_OFF", "cm_pron", "cm_pron_clause", "twin_clause"]
    per = {a: [] for a in arms}
    for doc in docset:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        for a in arms:
            sm = _reader(a, gaz).read(path)
            c, _ = _score_doc(sm, wdw[doc])
            per[a].append(np.array(c, float))
    acc = {a: float(np.concatenate(per[a]).mean()) for a in arms}
    n = int(sum(len(x) for x in per["cm_pron"]))
    print("\n[%s]  n=%d" % (label, n))
    for a in arms:
        print("   %-16s acc=%.4f" % (a, acc[a]))
    tests = {}
    for lab, a, b in [("cm_pron_clause - cm_pron (optimization)", "cm_pron_clause", "cm_pron"),
                      ("cm_pron_clause - twin (beats info-free)", "cm_pron_clause", "twin_clause"),
                      ("cm_pron_clause - pos_OFF", "cm_pron_clause", "pos_OFF")]:
        d = _boot(per[a], per[b], nboot, SEED, doc_level=True)
        tests[lab] = d
        print("   %-42s d=%+.4f CI[%+.4f,%+.4f] hw=%.4f sep=%s"
              % (lab, d["delta"], d["lo"], d["hi"], d["ci_hw"], d["ci_sep"]))
    return {"acc": acc, "n": n, "tests": tests}


def run(nboot=2000):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    gaz = SITQA.load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    alldocs = SITQA.load_docs(40)
    tuned = [d for d in alldocs[:16] if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    held = [d for d in alldocs[16:40] if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    print("=" * 92)
    print("CLAUSE-LOCAL AGENT COMPETITION (incremental clause segmentation)")
    r_tuned = _measure(tuned, gaz, wdw, nboot, "TUNED docs[0:16]")
    r_held = _measure(held, gaz, wdw, nboot, "HELD-OUT docs[16:40] (never inspected)")
    print("=" * 92)
    out = {"anchor_name": "cmrole_agent_clause_v1", "tuned": r_tuned, "held_out": r_held,
           "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[done] %.0fs -> %s" % (time.time() - t0, os.path.join(OUT_DIR, "metrics.json")))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--nboot", type=int, default=2000)
    args = ap.parse_args()
    run(args.nboot)
