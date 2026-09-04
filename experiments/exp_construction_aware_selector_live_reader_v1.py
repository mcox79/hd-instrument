"""exp_construction_aware_selector_live_reader_v1 -- the END-TO-END confirmation of the located NEGATIVE, through the
ACTUAL live SituationReader().read().

The selector-level cells showed construction-aware routing adds 0.000 (19c) / -0.001 (modern) over the live theme
selector hybrid_role_patient. This cell confirms it end-to-end: it monkeypatches the ONE function the live wired
router calls for the theme (hdlab.predicate_argument_frontend.hybrid_role_patient) with a construction-aware wrapper
(multi-DO give-class -> obj1; naming-class -> last DO; else the untouched live pick), runs the full deployed
SituationReader().read() per arm on the 25 real LitBank conll docs, and scores effective who-did-what
(pick==gold_head, ABSTENTION=WRONG) on the cleaned-DO gold. One variable: the theme SELECTOR. hdlab is READ
(monkeypatched at runtime, not edited).

Why this is the strongest form of the negative, not a weaker one: the selector-level isolation is the highest-power
test (it strips the upstream source/event losses that are COMMON to both arms). End-to-end the deployed reader sits
at ~0.63 vs the selector's ~0.93 -- that 0.30 gap is upstream and identical across arms, so it can only DILUTE an
already-null selector difference toward zero, never resurrect one. If the delta is null here too, the negative holds
at both levels.

Glass-box, CPU, NO LLM/spaCy on the scored path. ASCII. own dir.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, glob, json, sys, time
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_19c_composed_cleaned_gold_v1 as CG
import experiments.exp_whodidwhat_coverage_transitivity_control_v1 as TC
from experiments.exp_construction_aware_selector_diagnosis_v1 import GIVE_CLASS, NAMING_CLASS
from experiments.exp_referent_per_np_end_to_end_v1 import _norm
from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences
from hdlab.thematic_role_labeler import lemma_verb
import hdlab.predicate_argument_frontend as PAF
from hdlab.situation_reader import SituationReader

OUT_DIR = os.path.join(_REPO, "data/exp_construction_aware_selector_live_reader_v1")
CORPUS = os.path.join(_REPO, "data/corpora/litbank_coref_conll")
POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
LB = os.path.join(_REPO, "data/predict_revise_recall_v1/_population_litbank.json")

_ORIG_HRP = PAF.hybrid_role_patient


def _make_constr_hrp(twin_rng=None):
    """A construction-aware wrapper around the LIVE theme selector. v and cands are 1-based (router convention)."""
    def _hrp(tokens, upos, v, cands=None, weights=None, np_head_reduce=False):
        base = _ORIG_HRP(tokens, upos, v, cands=cands, weights=weights, np_head_reduce=np_head_reduce)
        vi0 = v - 1
        if not (0 <= vi0 < len(tokens)):
            return base
        lv = lemma_verb(tokens[vi0])
        if lv not in GIVE_CLASS and lv not in NAMING_CLASS:
            return base
        c = list(cands) if cands is not None else [i for i in range(1, len(upos) + 1) if upos[i - 1] in ("NOUN", "PROPN", "PRON")]
        if np_head_reduce:
            from hdlab.np_head_reduce import is_np_head
            c = [i for i in c if is_np_head(tokens, upos, i - 1)] or c
        bare = sorted(i for i in c if i > v and TC.is_bare_do(tokens, upos, v - 1, i - 1))
        if len(bare) >= 2:
            if twin_rng is not None:
                return int(bare[twin_rng.integers(0, len(bare))])
            return int(bare[0]) if lv in GIVE_CLASS else int(bare[-1])
        return base
    return _hrp


def read_doc_patients(reader, path):
    sm = reader.read(path)
    sents = parse_conll_sentences(path)
    sent_norm = {si: _norm(toks) for si, toks in enumerate(sents)}
    picks = {}
    for e in sm.events:
        if e.pred_idx is None:
            continue
        key = (sent_norm.get(e.sent_idx), e.pred_idx)
        if key[0] is not None:
            picks[key] = (e.patient or "?").lower()
    return picks


def score(rows, picks):
    return np.array([1 if (picks.get((_norm(r["sent"]), r["verb_idx"]), "?") not in ("?", "", None)
                           and picks.get((_norm(r["sent"]), r["verb_idx"])) == r["gold_head"]) else 0
                     for r in rows], dtype=float)


def _boot(a, b, nboot=3000, seed=13):
    d = a - b; rg = np.random.default_rng(seed)
    bs = d[rg.integers(0, len(d), size=(nboot, len(d)))].mean(1)
    lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
    return dict(delta=round(float(d.mean()), 4), ci_lo=round(lo, 4), ci_hi=round(hi, 4),
                half=round((hi - lo) / 2, 4), sep=bool(lo > 0))


def run(n_docs=None):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tagger = PosTagger.load(POS_ASSET)
    gaz = {}
    try:
        import experiments.exp_situation_qa_v1 as SITQA
        gaz = SITQA.load_given_gazetteer()
    except Exception:
        gaz = {}
    reader = SituationReader(gaz=gaz)
    docs = sorted(glob.glob(os.path.join(CORPUS, "*.conll")))
    if n_docs:
        docs = docs[:n_docs]
    rows_all = V1.load_pop(LB)
    doc_sents = set()
    for d in docs:
        for toks in parse_conll_sentences(d):
            doc_sents.add(_norm(toks))
    rows = [r for r in rows_all if r.get("gold_head") and _norm(r["sent"]) in doc_sents]
    clean = np.array([CG.is_clean_do(r, tagger.tag(r["sent"].split()))[0] for r in rows], dtype=bool)

    arms = {}
    for name, patch in [("LIVE", None), ("CONSTR", _make_constr_hrp()),
                        ("TWIN", _make_constr_hrp(twin_rng=np.random.default_rng(20260903)))]:
        PAF.hybrid_role_patient = patch if patch is not None else _ORIG_HRP
        try:
            picks = {}
            for d in docs:
                picks.update(read_doc_patients(reader, d))
        finally:
            PAF.hybrid_role_patient = _ORIG_HRP
        arms[name] = score(rows, picks)

    res = {"n_docs": len(docs), "n_clauses_full": len(rows), "n_clauses_clean_do": int(clean.sum())}
    for regime, mask in [("FULL", np.ones(len(rows), bool)), ("CLEAN_DO", clean)]:
        L, C, T = arms["LIVE"][mask], arms["CONSTR"][mask], arms["TWIN"][mask]
        res[regime] = {"n": int(mask.sum()),
                       "acc": {"LIVE": round(float(L.mean()), 4), "CONSTR": round(float(C.mean()), 4),
                               "TWIN": round(float(T.mean()), 4)},
                       "CONSTR_vs_LIVE": _boot(C, L), "CONSTR_vs_TWIN": _boot(C, T)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "construction_aware_selector_live_reader_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    args = ap.parse_args()
    res = run(n_docs=(3 if (args.self_test or args.smoke) else args.docs))
    print("\n===== CONSTRUCTION SELECTOR END-TO-END through LIVE reader (docs=%d) =====" % res["n_docs"], flush=True)
    for regime in ("FULL", "CLEAN_DO"):
        b = res[regime]; a = b["acc"]
        print("\n-- %s (n=%d) --" % (regime, b["n"]), flush=True)
        print("  LIVE %.4f | CONSTR %.4f | TWIN %.4f" % (a["LIVE"], a["CONSTR"], a["TWIN"]), flush=True)
        for k in ("CONSTR_vs_LIVE", "CONSTR_vs_TWIN"):
            d = b[k]
            print("    %-16s d=%+.4f CI[%+.4f,%+.4f] half=%.4f %s"
                  % (k, d["delta"], d["ci_lo"], d["ci_hi"], d["half"], "CI-SEP" if d["sep"] else "n.s."), flush=True)
    if args.self_test or args.smoke:
        assert res["n_clauses_full"] >= 10
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
