"""exp_whodidwhat_ud_structural_v1 -- the DECISIVE clean-instrument test: is the fidelity gap STRUCTURE?

Two errors were found (this session): (1) our who-did-what is a FLAT cue-competition/position heuristic with NO
grammatical structure -- the brain reads roles off an incremental parse (subj/obj) + verb-frame binding + voice
remapping (Hagoort MUC; Levin-Rappaport-Hovav; agrammatism replicates OUR algorithm); (2) the role-balanced gold is
confounded (crowd QA-SRL roles + the reader's OWN parse + engineered 62%-passive distribution + circular weights).

This cell re-bases on a CLEAN, NON-CIRCULAR instrument -- UD-EWT gold dependencies -- and tests the research claim
directly. Gold roles are read off GOLD grammatical relations + voice remapping (patient := obj [active] | nsubj:pass
[passive]; the field standard). Then four PATIENT routes, all given the SAME input, split ACTIVE vs PASSIVE:
  FLOOR_position   : resolve_patient (nearest post-verbal; the deployed word-order default).
  HEURISTIC_S4     : hybrid_role_patient (Competition Model -- cues+voice, NO structure; the live reader's route).
  STRUCT_ourparse  : read the patient off OUR arc-parser's dependents of the verb + detected voice (the brain-
                     faithful STRUCTURE-FIRST route we could build, using our real parse).
  STRUCT_goldparse : same off the GOLD parse + gold voice (the ceiling of a perfect structural route).
If STRUCT beats HEURISTIC on PASSIVES (where position is wrong), the fidelity gap is STRUCTURE and it is buildable
now. Glass-box, NO LLM. hdlab READ-only. ASCII. own dir.
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

POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
OUT_DIR = os.path.join(_REPO, "data/exp_whodidwhat_ud_structural_v1")
NOMINAL = {"NOUN", "PROPN", "PRON"}


def load_ud(path):
    sents = []; cur = []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line:
            if cur:
                sents.append(cur); cur = []
            continue
        if line.startswith("#"):
            continue
        c = line.split("\t")
        if len(c) < 8 or "-" in c[0] or "." in c[0]:
            continue
        cur.append({"id": int(c[0]), "form": c[1], "upos": c[3], "head": int(c[6]), "dep": c[7].split(":")[0],
                    "deprel": c[7]})
    if cur:
        sents.append(cur)
    return sents


def gold_items(sents):
    """Yield (toks, verb_id(1-based), gold_patient_id(1-based), is_passive) for every verb with a core patient."""
    out = []
    for s in sents:
        toks = [t["form"] for t in s]
        by_id = {t["id"]: t for t in s}
        for t in s:
            if t["upos"] != "VERB":
                continue
            v = t["id"]
            deps = [d for d in s if d["head"] == v]
            passive = any(d["deprel"].startswith("nsubj:pass") or d["deprel"].startswith("aux:pass") for d in deps)
            pat = None
            for d in deps:
                if not passive and d["dep"] == "obj":
                    pat = d["id"]; break
                if passive and d["deprel"].startswith("nsubj:pass"):
                    pat = d["id"]; break
            if pat is not None:
                out.append((toks, v, pat, passive))
    return out


def struct_patient(toks, pos, v, heads, is_passive):
    """STRUCTURE-FIRST patient: among the verb's NOMINAL dependents in the parse, apply voice remapping --
    passive -> the promoted (pre-verbal) subject; active -> the (post-verbal) object. Uses ATTACHMENT (heads), so a
    post-verbal noun that is NOT this verb's dependent (another clause) is correctly NOT taken."""
    n = len(toks)
    deps = [c for c in range(1, n + 1) if heads.get(c) == v and pos[c - 1] in NOMINAL]
    if not deps:
        return None
    pre = [c for c in deps if c < v]; post = [c for c in deps if c > v]
    if is_passive:
        return pre[-1] if pre else (post[0] if post else None)
    return post[0] if post else (pre[-1] if pre else None)


def run(smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tagger = PosTagger.load(POS_ASSET)
    from hdlab.arceager_parser import load_model, parse_with_conf, MODEL_PATH
    W = load_model(MODEL_PATH)
    sents = load_ud(UD_TEST)
    if smoke:
        sents = sents[:120]
    items = gold_items(sents)

    routes = ["FLOOR_position", "HEURISTIC_S4", "STRUCT_ourparse", "STRUCT_goldparse"]
    hits = {r: {"active": [], "passive": []} for r in routes}
    for toks, v, pat, passive in items:
        pos = tagger.tag(list(toks))
        cands = _cands(pos)
        if not cands:
            continue
        # our parse
        try:
            our_heads = parse_with_conf(toks, pos, W)[0]
        except Exception:
            our_heads = {}
        gold_heads = {}  # built per-sentence below is expensive; recompute cheaply from items? -> use gold from sents
        sl = "passive" if passive else "active"
        picks = {
            "FLOOR_position": resolve_patient(toks, pos, v, cands),
            "HEURISTIC_S4": hybrid_role_patient(toks, pos, v, cands),
            "STRUCT_ourparse": struct_patient(toks, pos, v, our_heads, robust_passive(toks, pos, v)),
        }
        for r in ("FLOOR_position", "HEURISTIC_S4", "STRUCT_ourparse"):
            hits[r][sl].append(1 if picks[r] == pat else 0)

    # STRUCT_goldparse: read off gold heads + gold voice (ceiling). Recompute with gold parse per sentence.
    for s in sents:
        toks = [t["form"] for t in s]
        gh = {t["id"]: t["head"] for t in s}
        pos_g = [t["upos"] for t in s]
        for t in s:
            if t["upos"] != "VERB":
                continue
            v = t["id"]; deps = [d for d in s if d["head"] == v]
            passive = any(d["deprel"].startswith("nsubj:pass") or d["deprel"].startswith("aux:pass") for d in deps)
            pat = None
            for d in deps:
                if not passive and d["dep"] == "obj":
                    pat = d["id"]; break
                if passive and d["deprel"].startswith("nsubj:pass"):
                    pat = d["id"]; break
            if pat is None:
                continue
            sl = "passive" if passive else "active"
            sp = struct_patient(toks, pos_g, v, gh, passive)
            hits["STRUCT_goldparse"][sl].append(1 if sp == pat else 0)

    def acc(d):
        return round(float(np.mean(d)), 4) if d else None
    n_act = len(hits["FLOOR_position"]["active"]); n_pas = len(hits["FLOOR_position"]["passive"])
    res = {"n_items": len(items), "n_active": n_act, "n_passive": n_pas,
           "acc": {r: {"active": acc(hits[r]["active"]), "passive": acc(hits[r]["passive"]),
                       "all": acc(hits[r]["active"] + hits[r]["passive"])} for r in routes},
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "whodidwhat_ud_structural_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    res = run(smoke=(a.self_test or a.smoke))
    print(json.dumps(res, indent=2), flush=True)
    print("\n=== WHO-DID-WHAT on CLEAN UD-EWT gold relations (patient), by VOICE ===", flush=True)
    print("  %-18s %8s %8s %8s" % ("route", "active", "passive", "all"), flush=True)
    for r in ["FLOOR_position", "HEURISTIC_S4", "STRUCT_ourparse", "STRUCT_goldparse"]:
        a_ = res["acc"][r]
        print("  %-18s %8s %8s %8s" % (r, a_["active"], a_["passive"], a_["all"]), flush=True)
    print("(n_active=%d n_passive=%d)" % (res["n_active"], res["n_passive"]), flush=True)
    if a.self_test or a.smoke:
        assert res["n_items"] > 30
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
