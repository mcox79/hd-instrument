"""exp_structural_patient_noregress_v1 -- confirm the structure-first PATIENT is (a) net-positive as a hybrid with
heuristic fallback, and (b) does NOT hurt other consumers when wired through the LIVE reader.

The optimization (this session): read the PATIENT off the parse's grammatical relations + voice remapping
(structural_roles), which beats the live cue/position heuristic +0.06 on clean UD gold (test AND train; zero tuned
parameters -> generalizes). Keep the existing AGENT (nearest pre-verbal is already strong). This cell:
  (A) hybrid = structural patient if the parse yields one, else the heuristic -> confirm it is >= heuristic (net-safe
      floor) and captures the win, on UD-EWT test + train.
  (B) NO-REGRESS: monkeypatch the LIVE reader's wired role router (route_predicate_arguments) so the THEME/patient
      comes from structural_roles, run a real LitBank doc, and confirm the read COMPLETES and the non-role outputs
      (n_events, entities, coref_acc, causal, timeline) are stable while the patient-dependent outputs change in the
      intended (structural) direction. Glass-box, NO LLM. hdlab READ (patched at runtime). ASCII. own dir.
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import argparse, glob, json, time
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.pos_tagger import PosTagger
from hdlab.relcl_resolver import _cands
from hdlab.graded_role_assigner import hybrid_role_patient, robust_passive
import experiments.exp_whodidwhat_ud_structural_v1 as UD
from experiments.exp_structural_role_reader_v1 import structural_roles

POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
UD_TRAIN = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu")
LB = os.path.join(_REPO, "data/litbank/coref_conll")
OUT_DIR = os.path.join(_REPO, "data/exp_structural_patient_noregress_v1")


def hybrid_patient(toks, pos, heads, v, cands):
    """The DEPLOYABLE patient: structure-first (object/promoted-subject off the parse + voice), heuristic fallback
    where the parse yields no core object (net-safe: never worse than the heuristic on uncovered items)."""
    sp = structural_roles(toks, pos, heads, v)["patient"]
    return sp if sp is not None else hybrid_role_patient(toks, pos, v, cands)


def eval_patient(path, tagger, W, parse, max_sents=None):
    sents = UD.load_ud(path)
    if max_sents:
        sents = sents[:max_sents]
    gpos = {tuple(t["form"] for t in s): [t["upos"] for t in s] for s in sents}
    gheads = {tuple(t["form"] for t in s): {t["id"]: t["head"] for t in s} for s in sents}
    heur = []; struc = []; hyb = []; ceil = []
    for toks_l, v, pat, passive in UD.gold_items(sents):
        toks = tuple(toks_l); pos = tagger.tag(list(toks_l)); cands = _cands(pos)
        if not cands:
            continue
        try:
            oh = parse(list(toks_l), pos, W)[0]
        except Exception:
            oh = {}
        heur.append(1 if hybrid_role_patient(toks_l, pos, v, cands) == pat else 0)
        struc.append(1 if structural_roles(toks_l, pos, oh, v, robust_passive(toks_l, pos, v))["patient"] == pat else 0)
        hyb.append(1 if hybrid_patient(toks_l, pos, oh, v, cands) == pat else 0)
        ceil.append(1 if structural_roles(toks_l, gpos[toks], gheads[toks], v, passive)["patient"] == pat else 0)
    m = lambda d: round(float(np.mean(d)), 4) if d else None
    return {"n": len(heur), "heuristic": m(heur), "structure_only": m(struc), "hybrid": m(hyb), "ceiling_goldparse": m(ceil)}


def _summ(sm):
    evs = getattr(sm, "events", []) or []
    themes = tuple(sorted((str(getattr(e, "lemma", "")), str(getattr(e, "patient", ""))) for e in evs))
    return {"n_events": len(evs), "n_entities": len(getattr(sm, "entities", []) or []),
            "coref_acc": round(float(getattr(sm, "coref_acc", 0.0) or 0.0), 6),
            "n_causal": len(getattr(sm, "causal_links", []) or []),
            "n_timeline": len(getattr(sm, "timeline_frames", []) or []),
            "n_targets": getattr(sm, "n_targets", None), "_themes": themes}


def no_regress(reps=1):
    """Run the LIVE reader on a real doc with the wired role router's THEME swapped to structural, vs baseline."""
    import hdlab.situation_reader as SR
    from hdlab.situation_reader import SituationReader
    from hdlab.coref import load_name_gender
    gaz = load_name_gender()
    doc = sorted(glob.glob(os.path.join(LB, "*.conll")))[0]
    _orig = SR.route_predicate_arguments

    def _patched(toks, pos, heads, v, quotative=False, np_head_reduce=False):
        roles = _orig(toks, pos, heads, v, quotative=quotative, np_head_reduce=np_head_reduce)
        try:
            sp = structural_roles(list(toks), list(pos), dict(heads), v)["patient"]
        except Exception:
            sp = None
        if sp:
            roles = dict(roles); roles["theme"] = sp
        return roles

    r = SituationReader(gaz=gaz)
    base = _summ(r.read(doc))
    SR.route_predicate_arguments = _patched
    try:
        r2 = SituationReader(gaz=gaz)
        patched = _summ(r2.read(doc))
    finally:
        SR.route_predicate_arguments = _orig
    # non-role outputs must be stable; theme set is allowed (intended) to change
    stable_keys = ("n_events", "n_entities", "coref_acc", "n_causal", "n_timeline", "n_targets")
    stable = {k: (base[k] == patched[k]) for k in stable_keys}
    themes_changed = sum(1 for a, b in zip(base["_themes"], patched["_themes"]) if a != b)
    return {"doc": os.path.basename(doc), "completed": True,
            "non_role_outputs_stable": bool(all(stable.values())), "stable_detail": stable,
            "base": {k: base[k] for k in stable_keys}, "patched": {k: patched[k] for k in stable_keys},
            "n_themes_changed": themes_changed, "n_events": base["n_events"]}


def run(smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tagger = PosTagger.load(POS_ASSET)
    from hdlab.arceager_parser import load_model, parse_with_conf, MODEL_PATH
    W = load_model(MODEL_PATH)
    res = {"patient_TEST": eval_patient(UD_TEST, tagger, W, parse_with_conf, max_sents=(100 if smoke else None)),
           "patient_TRAIN": eval_patient(UD_TRAIN, tagger, W, parse_with_conf, max_sents=(100 if smoke else 1500)),
           "no_regress": no_regress()}
    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "structural_patient_noregress_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    res = run(smoke=(a.self_test or a.smoke))
    for split in ("patient_TEST", "patient_TRAIN"):
        s = res[split]
        print("%-14s (n=%d): heuristic %s | structure %s | HYBRID %s | ceiling %s"
              % (split, s["n"], s["heuristic"], s["structure_only"], s["hybrid"], s["ceiling_goldparse"]), flush=True)
    nr = res["no_regress"]
    print("\nNO-REGRESS (live reader, %s): completed=%s | non-role outputs stable=%s | themes changed=%d/%d events"
          % (nr["doc"], nr["completed"], nr["non_role_outputs_stable"], nr["n_themes_changed"], nr["n_events"]), flush=True)
    print("  stable detail:", nr["stable_detail"], flush=True)
    if a.self_test or a.smoke:
        assert res["patient_TEST"]["n"] > 20
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
