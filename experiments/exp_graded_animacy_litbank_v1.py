"""exp_graded_animacy_litbank_v1 -- give the graded-animacy cue its BEST SHOT: name-rich 19c prose, non-canonical.

The science-text gold (exp_graded_animacy_competition_v1) showed graded animacy is a NO-OP (graded-floor -0.0020 n.s.):
word-order-dominant English + name-sparse expository text. The research caveat (hdi_research): the animacy cue's
EFFECT CONCENTRATES where word order is silent/ambiguous AND an animate competes with an inanimate -- i.e. NON-
CANONICAL clauses in NAME-RICH prose. This cell runs the SAME Competition Model + SAME animacy variants on the
LitBank who-did-what gold (19c novels, name-dense), on exactly that best-case slice, so a null here is a real
located negative and a win here is the scoped capability.

Reuses the variant machinery from exp_graded_animacy_competition_v1 (floor/crf_hard/name_hard/graded/twin,
refit-per-variant validities). One variable = the animacy support. Glass-box, CPU, NO LLM. hdlab READ. ASCII. own dir.
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import argparse, json, time
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_graded_animacy_competition_v1 as GAC
from hdlab.graded_competition import map_pick
from hdlab.relcl_resolver import resolve_patient
from hdlab.pos_tagger import PosTagger
from hdlab.crf_tagger import GlassBoxCRF
from hdlab.coref import load_name_gender

OUT_DIR = os.path.join(_REPO, "data/exp_graded_animacy_litbank_v1")
POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
LB = os.path.join(_REPO, "data/predict_revise_recall_v1/_population_litbank.json")
CUES = GAC.CUES
VARIANTS = GAC.VARIANTS
SEED = 20260904


def _prep(rows, tagger, crf, gaz, Li):
    """Attach toks/pos/v/cands/marg/shared/patient/flags to each usable row (gold_in_cands, verb present)."""
    items = []
    for r in rows:
        if not r.get("gold_head") or r.get("gold_idx") is None:
            continue
        toks = r["sent"].split()
        vi = r["verb_idx"]
        if not (0 <= vi < len(toks)):
            continue
        cand_idx = [int(i) for i in r.get("cand_idx", [])]
        cands = [i + 1 for i in cand_idx if 0 <= i < len(toks)]        # 1-based, in-range
        if len(cands) < 2:
            continue
        gold_idx = int(r["gold_idx"])
        if gold_idx not in cand_idx:                                    # patient must be reachable
            continue
        pos = tagger.tag(list(toks))
        marg = crf.marginals(toks)
        shared = GAC._shared_cue_supports(toks, pos, vi + 1, cands)
        namebearing = any(toks[i - 1].lower().strip(".,\"'();:") in gaz for i in cands)
        items.append({"toks": toks, "pos": pos, "v": vi + 1, "cands": cands, "gold": [gold_idx],
                      "marg": marg, "shared": shared, "name": namebearing,
                      "nc": bool(r.get("gold_preverbal") or r.get("noncanonical"))})
    return items


def run(smoke=False, seed=SEED):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tagger = PosTagger.load(POS_ASSET)
    crf = GlassBoxCRF.load(); GAC.GlassBoxCRF_LABELS = crf.labels; Li = crf.Li
    gaz = load_name_gender()
    rows = V1.load_pop(LB)
    if smoke:
        rows = rows[::15]
    items = _prep(rows, tagger, crf, gaz, Li)

    rng = np.random.default_rng(seed)
    sent_of = [" ".join(it["toks"]) for it in items]
    uniq = sorted(set(sent_of)); perm = rng.permutation(len(uniq))
    test_sents = set(uniq[i] for i in perm[: len(uniq) // 2])
    train = [it for it, s in zip(items, sent_of) if s not in test_sents]
    test = [it for it, s in zip(items, sent_of) if s in test_sents]

    weights = {}
    for var in VARIANTS:
        X, y = [], []
        for it in train:
            col = GAC._animacy_column(var, it["toks"], it["pos"], it["cands"], it["marg"], Li, gaz,
                                      permute_rows=(rng.permutation(len(it["toks"])) if var == "twin" else None))
            gset = set(it["gold"])
            for j, i in enumerate(it["cands"]):
                X.append([it["shared"][c][j] if c != "animacy" else col[j] for c in CUES])
                y.append(1.0 if (i - 1) in gset else 0.0)
        weights[var] = GAC._fit_logistic(np.array(X), np.array(y))

    def pick(it, var, w):
        col = GAC._animacy_column(var, it["toks"], it["pos"], it["cands"], it["marg"], Li, gaz,
                                  permute_rows=(np.random.default_rng(seed + hash(" ".join(it["toks"])) % 99999)
                                                .permutation(len(it["toks"])) if var == "twin" else None))
        S = {c: (it["shared"][c] if c != "animacy" else col) for c in CUES}
        idx = map_pick(S, w)
        return it["cands"][idx] if 0 <= idx < len(it["cands"]) else None

    SL = ["all", "nc", "name", "name_nc"]
    acc = {sl: {v: [] for v in VARIANTS} for sl in SL}
    ref = {sl: [] for sl in SL}

    def belongs(it):
        out = ["all"]
        if it["nc"]:
            out.append("nc")
        if it["name"]:
            out.append("name")
        if it["name"] and it["nc"]:
            out.append("name_nc")
        return out
    for it in test:
        gset = set(it["gold"])
        rp = resolve_patient(it["toks"], it["pos"], it["v"], it["cands"])
        okrp = (rp is not None and (rp - 1) in gset)
        for sl in belongs(it):
            ref[sl].append(okrp)
            for var in VARIANTS:
                p = pick(it, var, weights[var])
                acc[sl][var].append(p is not None and (p - 1) in gset)

    def m(d):
        return round(float(np.mean(d)), 4) if d else None
    res = {"n_items": len(items), "n_train": len(train), "n_test": len(test),
           "slice_n": {sl: len(acc[sl]["floor"]) for sl in SL},
           "acc": {sl: {v: m(acc[sl][v]) for v in VARIANTS} for sl in SL},
           "ref_resolve": {sl: m(ref[sl]) for sl in SL}}
    contr = {}
    for sl in SL:
        contr[sl] = {
            "graded_minus_floor": GAC._boot_diff(acc[sl]["graded"], acc[sl]["floor"], seed + 1),
            "graded_minus_name_hard": GAC._boot_diff(acc[sl]["graded"], acc[sl]["name_hard"], seed + 2),
            "name_hard_minus_floor": GAC._boot_diff(acc[sl]["name_hard"], acc[sl]["floor"], seed + 3),
            "graded_minus_twin": GAC._boot_diff(acc[sl]["graded"], acc[sl]["twin"], seed + 4),
        }
    res["contrasts"] = contr
    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "graded_animacy_litbank_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    res = run(smoke=(a.self_test or a.smoke))
    print(json.dumps({k: res[k] for k in ("n_items", "slice_n", "acc", "ref_resolve", "elapsed_s")}, indent=2), flush=True)
    for sl in ["all", "nc", "name", "name_nc"]:
        print("\n=== slice=%s (n=%d) ===" % (sl, res["slice_n"][sl]), flush=True)
        print("  floor %s | crf_hard %s | name_hard %s | graded %s | twin %s | (resolve %s)"
              % (res["acc"][sl]["floor"], res["acc"][sl]["crf_hard"], res["acc"][sl]["name_hard"],
                 res["acc"][sl]["graded"], res["acc"][sl]["twin"], res["ref_resolve"][sl]), flush=True)
        for k, d in res["contrasts"][sl].items():
            print("    %-24s d=%+.4f CI[%+.4f,%+.4f] %s" % (k, d["delta"], d["ci"][0], d["ci"][1],
                                                           "SEP" if d["sep"] else "n.s."), flush=True)
    if a.self_test or a.smoke:
        assert res["n_items"] > 30
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
