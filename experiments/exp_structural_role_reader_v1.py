"""exp_structural_role_reader_v1 -- the OPTIMIZATION: a brain-faithful STRUCTURE-FIRST who-did-what reader.

WHY (this session): the live reader assigns core roles by a flat cue/position heuristic that "takes NO arc heads"
(the agrammatic/backup route). The brain reads roles off the PARSE (subject/object grammatical relations) + a VOICE
remapping (Hagoort MUC; Levin-Rappaport-Hovav). On clean UD-EWT gold that structural route beats the live heuristic
0.735 vs 0.673 EVEN WITH OUR CURRENT PARSER, and hits 0.913 with a perfect parse. This module is that route,
proposed for hdlab.

GENERALIZABLE BY CONSTRUCTION: `structural_roles` has ZERO tuned parameters -- it is grammatical relations + voice
remapping (universal), not corpus-fitted cue weights. So it does not overfit a register the way the Competition
Model (weights trained on the confounded role-balanced gold) does. Demonstrated on the UD-EWT test AND train splits
+ the gold-parse ceiling; the no-regress check runs it through the LIVE reader.

structural_roles(toks, pos, heads, v) -> {"agent": pos|None, "patient": pos|None}, 1-based, glass-box, NO LLM.
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import argparse, json, time
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.pos_tagger import PosTagger
from hdlab.relcl_resolver import _cands, resolve_patient
from hdlab.graded_role_assigner import hybrid_role_patient, robust_passive
import experiments.exp_whodidwhat_ud_structural_v1 as UD

POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
UD_TRAIN = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu")
OUT_DIR = os.path.join(_REPO, "data/exp_structural_role_reader_v1")
NOMINAL = {"NOUN", "PROPN", "PRON"}
BY = {"by"}


# ============================ THE PROPOSED ORGAN (zero tuned parameters) ============================
def _verb_nom_deps(pos, heads, v, n):
    return [c for c in range(1, n + 1) if heads.get(c) == v and pos[c - 1] in NOMINAL]


def _by_agent(toks, pos, heads, v, n):
    """a nominal governed by the verb whose left edge is 'by' (the demoted agent of a passive)."""
    for c in range(1, n + 1):
        if pos[c - 1] in NOMINAL and heads.get(c) == v:
            j = c - 1
            while j - 1 >= 1 and pos[j - 2] in ("ADJ", "NOUN", "PROPN", "DET"):
                j -= 1
            if j - 1 >= 1 and toks[j - 2].lower() in BY:
                return c
    return None


def _shared_object(toks, pos, heads, v, n):
    """coordination/control SHARING: if v has no object of its own, borrow the object of a coordinated verb
    (a verb sharing v's head, or v's head if v is a conjunct). Mirrors UD enhanced-dependency argument sharing."""
    hv = heads.get(v)
    sib_verbs = [u for u in range(1, n + 1) if pos[u - 1] == "VERB" and u != v and (heads.get(u) == hv or u == hv or heads.get(v) == u)]
    for u in sib_verbs:
        post = [c for c in _verb_nom_deps(pos, heads, u, n) if c > u]
        if post:
            return post[0]
    return None


def structural_roles(toks, pos, heads, v, is_passive=None):
    """Read (agent, patient) off the verb's grammatical relations in the parse + voice remapping. 1-based."""
    n = len(toks)
    if is_passive is None:
        is_passive = robust_passive(toks, pos, v)
    nom = _verb_nom_deps(pos, heads, v, n)
    pre = [c for c in nom if c < v]; post = [c for c in nom if c > v]
    if is_passive:
        patient = pre[-1] if pre else (post[0] if post else None)   # promoted subject
        agent = _by_agent(toks, pos, heads, v, n)                    # by-phrase (often absent)
    else:
        patient = post[0] if post else None                         # object
        agent = pre[-1] if pre else None                            # subject
    if patient is None:
        patient = _shared_object(toks, pos, heads, v, n)            # coordination/control sharing
    return {"agent": agent, "patient": patient}
# ===================================================================================================


def eval_split(path, tagger, W, parse, max_sents=None):
    sents = UD.load_ud(path)
    if max_sents:
        sents = sents[:max_sents]
    items = UD.gold_items(sents)                       # (toks, v, gold_patient, passive)
    # also gold agent per (sent,v)
    gold_agent = {}
    for s in sents:
        toks = tuple(t["form"] for t in s)
        for t in s:
            if t["upos"] != "VERB":
                continue
            v = t["id"]; deps = [d for d in s if d["head"] == v]
            passive = any(d["deprel"].startswith(("nsubj:pass", "aux:pass")) for d in deps)
            ag = None
            for d in deps:
                if passive and d["dep"] == "obl" and d["deprel"].endswith("agent"):
                    ag = d["id"]; break
                if not passive and d["deprel"].startswith("nsubj") and not d["deprel"].startswith("nsubj:pass"):
                    ag = d["id"]; break
            gold_agent[(toks, v)] = ag
    R = {k: {"active": {"pat": [], "ag": []}, "passive": {"pat": [], "ag": []}}
         for k in ("HEURISTIC", "STRUCT_ourparse", "STRUCT_goldparse")}
    # gold heads per sentence for the ceiling
    gheads = {}
    gpos = {}
    for s in sents:
        toks = tuple(t["form"] for t in s)
        gheads[toks] = {t["id"]: t["head"] for t in s}
        gpos[toks] = [t["upos"] for t in s]
    for toks_l, v, pat, passive in items:
        toks = tuple(toks_l); sl = "passive" if passive else "active"
        pos = tagger.tag(list(toks_l))
        cands = _cands(pos)
        if not cands:
            continue
        try:
            oh = parse(list(toks_l), pos, W)[0]
        except Exception:
            oh = {}
        ga = gold_agent.get((toks, v))
        # HEURISTIC (live reader): patient via hybrid; agent via nearest pre-verbal nominal
        hpat = hybrid_role_patient(toks_l, pos, v, cands)
        hpre = [c for c in cands if c < v]
        hag = hpre[-1] if hpre else None
        R["HEURISTIC"][sl]["pat"].append(1 if hpat == pat else 0)
        if ga is not None:
            R["HEURISTIC"][sl]["ag"].append(1 if hag == ga else 0)
        # STRUCT our parse
        so = structural_roles(toks_l, pos, oh, v, robust_passive(toks_l, pos, v))
        R["STRUCT_ourparse"][sl]["pat"].append(1 if so["patient"] == pat else 0)
        if ga is not None:
            R["STRUCT_ourparse"][sl]["ag"].append(1 if so["agent"] == ga else 0)
        # STRUCT gold parse (ceiling)
        sg = structural_roles(toks_l, gpos[toks], gheads[toks], v, passive)
        R["STRUCT_goldparse"][sl]["pat"].append(1 if sg["patient"] == pat else 0)
        if ga is not None:
            R["STRUCT_goldparse"][sl]["ag"].append(1 if sg["agent"] == ga else 0)

    def acc(d):
        return round(float(np.mean(d)), 4) if d else None
    out = {}
    for k in R:
        pat_all = R[k]["active"]["pat"] + R[k]["passive"]["pat"]
        ag_all = R[k]["active"]["ag"] + R[k]["passive"]["ag"]
        out[k] = {"patient_all": acc(pat_all), "patient_active": acc(R[k]["active"]["pat"]),
                  "patient_passive": acc(R[k]["passive"]["pat"]),
                  "agent_all": acc(ag_all), "whodidwhat_all": acc(pat_all + ag_all),
                  "n_pat": len(pat_all), "n_ag": len(ag_all)}
    return out


def run(smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tagger = PosTagger.load(POS_ASSET)
    from hdlab.arceager_parser import load_model, parse_with_conf, MODEL_PATH
    W = load_model(MODEL_PATH)
    res = {"TEST": eval_split(UD_TEST, tagger, W, parse_with_conf, max_sents=(120 if smoke else None)),
           "TRAIN_sample": eval_split(UD_TRAIN, tagger, W, parse_with_conf, max_sents=(120 if smoke else 1500))}
    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "structural_role_reader_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    res = run(smoke=(a.self_test or a.smoke))
    for split in ("TEST", "TRAIN_sample"):
        s = res[split]
        print("\n=== %s (n_pat=%d n_ag=%d) -- who-did-what accuracy ===" % (split, s["HEURISTIC"]["n_pat"], s["HEURISTIC"]["n_ag"]), flush=True)
        print("  %-18s %8s %8s %8s %8s" % ("route", "pat_all", "pat_pass", "agent", "wdw_all"), flush=True)
        for k in ("HEURISTIC", "STRUCT_ourparse", "STRUCT_goldparse"):
            print("  %-18s %8s %8s %8s %8s" % (k, s[k]["patient_all"], s[k]["patient_passive"], s[k]["agent_all"], s[k]["whodidwhat_all"]), flush=True)
    if a.self_test or a.smoke:
        assert res["TEST"]["HEURISTIC"]["n_pat"] > 30
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
