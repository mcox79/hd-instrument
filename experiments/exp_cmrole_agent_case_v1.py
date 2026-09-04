"""COMPETITION refinement: the Competition-Model CASE cue. The competition-error dump showed a large class
where an ACCUSATIVE/POSSESSIVE/REFLEXIVE pronoun (her/him/their/his/themselves) out-competed the true
NOMINATIVE subject (she/he/they). English marks case morphologically on pronouns, and case is one of the
HIGHEST-validity Competition-Model cues where a language marks it (Bates & MacWhinney). Restricting the
pronoun agent candidates to the nominative case (`case_filter`) is exactly that cue -- glass-box, no training.

Measured against the full stack (tracked set + pronouns + clause-local + context-cued readout), on the tuned
AND held-out sets, with the info-free twin.

Run: .venv/Scripts/python.exe experiments/exp_cmrole_agent_case_v1.py [--nboot 2000]
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
from experiments.exp_cmrole_agent_board_v1 import CMAgentReader, AGENT_W, _boot
from experiments.exp_cmrole_agent_readout_v1 import answer_instanced, _questions

SEED = 20260904
OUT_DIR = os.path.join(_REPO, "data", "exp_cmrole_agent_case_v1")


def _reader(arm, gaz):
    if arm == "pos_OFF":
        return SituationReader(gaz=gaz, role_route="positional", referent_per_np=False)
    twin = SEED if arm == "twin_case" else None
    case = arm in ("cm_case", "twin_case")
    return CMAgentReader(gaz=gaz, role_route="positional", referent_per_np=True, cm_weights=AGENT_W,
                         cm_gaz=gaz, cm_twin_seed=twin, agent_source="coref", include_pron_agents=True,
                         clause_local=True, case_filter=case)


def _measure(docset, gaz, wdw, nboot, label):
    arms = ["pos_OFF", "cm_nocase", "cm_case", "twin_case"]
    per = {a: [] for a in arms}
    for doc in docset:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        cache = {}
        for a in arms:
            rarm = "cm_nocase" if a == "cm_nocase" else a
            # cm_nocase = full stack WITHOUT case filter; build its own reader
            key = a if a != "cm_nocase" else "nocase"
            if key not in cache:
                if a == "cm_nocase":
                    cache[key] = CMAgentReader(gaz=gaz, role_route="positional", referent_per_np=True,
                                               cm_weights=AGENT_W, cm_gaz=gaz, agent_source="coref",
                                               include_pron_agents=True, clause_local=True, case_filter=False).read(path)
                else:
                    cache[key] = _reader(a, gaz).read(path)
            sm = cache[key]
            c = [int(SITQA._match(answer_instanced(sm, q), q["gold"], "events")) for q in _questions(wdw[doc])]
            per[a].append(np.array(c, float))
    acc = {a: float(np.concatenate(per[a]).mean()) for a in arms}
    n = int(sum(len(x) for x in per["cm_case"]))
    print("\n[%s]  n=%d" % (label, n))
    for a in arms:
        print("   %-12s acc=%.4f" % (a, acc[a]))
    tests = {}
    for lab, a, b in [("CASE cue: cm_case - cm_nocase", "cm_case", "cm_nocase"),
                      ("cm_case - pos_OFF", "cm_case", "pos_OFF"),
                      ("cm_case - twin (info-free)", "cm_case", "twin_case")]:
        d = _boot(per[a], per[b], nboot, SEED, doc_level=True)
        tests[lab] = d
        print("   %-30s d=%+.4f CI[%+.4f,%+.4f] hw=%.4f sep=%s"
              % (lab, d["delta"], d["lo"], d["hi"], d["ci_hw"], d["ci_sep"]))
    return {"acc": acc, "n": n, "tests": tests}


def run(nboot=2000):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    gaz = SITQA.load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    alldocs = SITQA.load_docs(40)
    tuned = [d for d in alldocs[:16] if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    held = [d for d in alldocs[16:40] if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    print("=" * 88)
    print("COMPETITION-MODEL CASE CUE (nominative-only pronoun agents) + full stack + cued readout")
    out = {"anchor_name": "cmrole_agent_case_v1",
           "tuned": _measure(tuned, gaz, wdw, nboot, "TUNED docs[0:16]"),
           "held_out": _measure(held, gaz, wdw, nboot, "HELD-OUT docs[16:40]")}
    print("=" * 88)
    out["elapsed_s"] = round(time.time() - t0, 1); out["ts_iso"] = datetime.now(timezone.utc).isoformat()
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
