"""exp_graded_animacy_competition_v1 -- consume the graded POS posterior as a BRAIN-FOUNDATIONAL animacy cue in
the Competition-Model role assigner.

WHY (the reframe, disk-earned): the brief's literal target -- graded posterior -> referent_per_np NP/name detection
-> who-did-what -- is a LOCATED NEGATIVE (exp_graded_pos_whodidwhat_v1: soft-nominal recovery = +0.0000 vs the
frame floor; introduction is PROPN<->NOUN-invariant; coref is UPOS-independent). The organ-map (this session) found
the ONE channel where PROPN<->NOUN actually changes a reader output is ANIMACY (animacy_lexicon: PROPN -> empty
overrides -> "unk"; 267/387 UD swaps flip it). And the Competition-Model role assigner (hdlab.graded_role_assigner,
the landed non-canonical patient route) already WEIGHTS animacy -- but a NAME (PROPN) gives "unk" -> 0.0 support, so
the animacy cue is DEAD for every name.

THE CHAIN (research-confirmed PINNED end-to-end, hdi_research this session):
  graded POS posterior P(cat|sent)  [P7 crf, calibrated]                         -- upstream capability
    -> EXPECTED animacy = E_P[animacy_support]  (marginalize over category uncertainty; PPC/Ernst-Banks)
    -> a NAME denotes an animate person (ATL person store; Damasio 1996) via the reader's OWN name gazetteer
    -> animacy competes as a validity-weighted cue (MacWhinney-Bates) -> biases AGENT/PATIENT (Dowty proto-roles)
Every hard-commit the current pipeline does (1-best POS, hard animacy route, "unk" for names) is the LESS
brain-faithful choice.

VARIANTS (one variable = the animacy support; ALL else = the landed Competition Model + refit-per-variant validity):
  floor    : lookup_animacy(tok, PERCEPTRON tag)             -- the DEPLOYED animacy cue (PROPN->unk).
  crf_hard : lookup_animacy(tok, CRF-argmax tag)             -- model switch only (isolates perceptron->CRF).
  name_hard: CRF-argmax; PROPN -> gazetteer name-animacy     -- the NAME FIX, hard (no graded posterior).
  graded   : E over CRF posterior: P(PROPN)*name + P(NOUN)*wordnet + P(PRON)*pron  -- the GRADED consumption.
  twin     : graded with the CRF posterior rows PERMUTED across token positions    -- info-free, MUST lose.
Contrasts isolate: graded-floor (total), graded-name_hard (the GRADEDNESS = the posterior's own value),
name_hard-crf_hard (the name fix), graded-twin (posterior values matter). Refit logistic per variant = the
animacy cue validity is SWEPT (research: English animacy validity is LOW; do not adopt Italian-scale weights).

Reads the aligned non-canonical gold (exp_noncanonical_role_diagnostic_v1). Glass-box, CPU, NO LLM. hdlab READ-only.
ASCII. own dir.
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

from hdlab.graded_competition import map_pick
from hdlab.relcl_resolver import resolve_patient, precise_passive, is_object_gap, _cands
from hdlab.thematic_role_labeler import lemma_verb
from hdlab.animacy_lexicon import lookup_animacy
from hdlab.coref import load_name_gender
from hdlab.crf_tagger import GlassBoxCRF
from experiments.exp_competition_model_noncanonical_assigner_v1 import voice_cues, gap_config, UNACC

CACHE = os.path.join(_REPO, "data/exp_noncanonical_role_diagnostic_v1/aligned_gold.jsonl")
OUT_DIR = os.path.join(_REPO, "data/exp_graded_animacy_competition_v1")
CUES = ["order", "adjacency", "passive_strong", "passive_weak", "gap", "unacc", "byagent", "animacy"]
NOMINAL = {"NOUN", "PROPN", "PRON"}
SEED = 20260904
VARIANTS = ["floor", "crf_hard", "name_hard", "graded", "twin"]


def _map_av(anim):
    """animacy dict -> support scalar (animate favours AGENT/against patient = -1; inanimate favours patient = +1)."""
    av = anim["animacy"] if anim is not None else "unk"
    return 1.0 if av == "inanimate" else (-1.0 if av == "animate" else 0.0)


def _name_support(tok, gaz):
    """A personal name (gazetteer hit) -> animate person -> -1.0; else unknown -> 0.0 (conservative NER signal)."""
    w = tok.lower().strip(".,\"'();:")
    return -1.0 if w in gaz else 0.0


def _shared_cue_supports(toks, pos, v, cands):
    """The variant-INDEPENDENT cues (everything but animacy), verbatim to the landed Competition Model."""
    low = [t.lower() for t in toks]
    post = [i for i in cands if i > v]; pre = [i for i in cands if i < v]
    nearest_post = post[0] if post else None
    nearest_pre = pre[-1] if pre else None
    vc = voice_cues(toks, pos, v)
    strong = vc["vc_strong"] or vc["vc_get"] or vc["vc_being"] or vc["vc_bypp"]
    weak = vc["vc_partN"] and not strong
    ante, _subj = gap_config(toks, pos, v)
    lemma = lemma_verb(toks[v - 1])
    unacc_sole = (lemma in UNACC and len(pre) == 1)
    S = {c: np.zeros(len(cands)) for c in CUES}
    for j, i in enumerate(cands):
        if i == nearest_post:
            S["order"][j] = 1.0
        elif i > v:
            S["order"][j] = 0.4
        S["adjacency"][j] = 1.0 / (1.0 + abs(i - v))
        if strong and i == nearest_pre:
            S["passive_strong"][j] = 1.0
        if weak and i == nearest_pre:
            S["passive_weak"][j] = 1.0
        if ante is not None and i == ante:
            S["gap"][j] = 1.0
        if unacc_sole and i == nearest_pre:
            S["unacc"][j] = 1.0
        if (i - 2) >= 0 and low[i - 2] == "by":
            S["byagent"][j] = 1.0
    return S


def _animacy_column(variant, toks, pos, cands, marg, Li, gaz, permute_rows=None):
    """The animacy support array over cands for the given variant."""
    col = np.zeros(len(cands))
    argmax_tag = None
    if variant in ("crf_hard", "name_hard"):
        argmax_tag = [marg[t].argmax() for t in range(len(toks))]
    for j, i in enumerate(cands):
        t = i - 1
        tok = toks[t]
        if variant == "floor":
            col[j] = _map_av(lookup_animacy(tok, pos[t] if t < len(pos) else None))
        elif variant == "crf_hard":
            tag = GlassBoxCRF_LABELS[argmax_tag[t]]
            col[j] = _map_av(lookup_animacy(tok, tag))
        elif variant == "name_hard":
            tag = GlassBoxCRF_LABELS[argmax_tag[t]]
            if tag == "PROPN":
                col[j] = _name_support(tok, gaz)
            else:
                col[j] = _map_av(lookup_animacy(tok, tag))
        elif variant in ("graded", "twin"):
            row = marg[t] if permute_rows is None else marg[permute_rows[t]]
            p_propn = row[Li["PROPN"]] if "PROPN" in Li else 0.0
            p_noun = row[Li["NOUN"]] if "NOUN" in Li else 0.0
            p_pron = row[Li["PRON"]] if "PRON" in Li else 0.0
            s_name = _name_support(tok, gaz)
            s_noun = _map_av(lookup_animacy(tok, "NOUN"))
            s_pron = _map_av(lookup_animacy(tok, "PRON"))
            col[j] = p_propn * s_name + p_noun * s_noun + p_pron * s_pron
    return col


GlassBoxCRF_LABELS = None


def _fit_logistic(X, y, l2=1.0, iters=400, lr=0.2):
    mu = X.mean(0); sd = X.std(0); sd[sd < 1e-9] = 1.0
    Xs = (X - mu) / sd
    n, d = Xs.shape
    w = np.zeros(d); b = 0.0
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-(Xs @ w + b)))
        w -= lr * (Xs.T @ (p - y) / n + l2 * w / n)
        b -= lr * float((p - y).mean())
    return {c: float(w[k] / sd[k]) for k, c in enumerate(CUES)}


def _span_set(g):
    return set(range(g[0], g[1])) if (len(g) == 2 and g[1] > g[0]) else set(g)


def _in_span(pred_1, g):
    return pred_1 is not None and (pred_1 - 1) in _span_set(g)


def _boot_diff(a, b, seed, n_boot=2000):
    a = np.asarray(a, float); b = np.asarray(b, float); r = np.random.default_rng(seed); n = len(a)
    idx = r.integers(0, n, size=(n_boot, n))
    d = (a[idx].mean(1) - b[idx].mean(1))
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    signs = r.choice([-1.0, 1.0], size=(n_boot, n))
    nullb = ((a - b)[None, :] * signs).mean(1)
    return {"delta": round(float(a.mean() - b.mean()), 4), "ci": [round(lo, 4), round(hi, 4)],
            "hw": round((hi - lo) / 2, 4), "null_p95": round(float(np.percentile(np.abs(nullb), 95)), 4),
            "sep": bool(lo > 0)}


def run(smoke=False, seed=SEED):
    global GlassBoxCRF_LABELS
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    crf = GlassBoxCRF.load(); GlassBoxCRF_LABELS = crf.labels; Li = crf.Li
    gaz = load_name_gender()
    rows = [json.loads(l) for l in open(CACHE, encoding="utf-8")]
    if smoke:
        rows = rows[::6]

    # precompute per-item: cands, shared supports, CRF marginals, name-bearing flag, calibration stats
    items = []
    calib_top = []; calib_nom_conf = []
    for it in rows:
        toks, pos, v = it["toks"], it["pos"], it["verb_idx"] + 1
        cands = _cands(pos)
        if not cands:
            continue
        marg = crf.marginals(toks)   # (n,K)
        shared = _shared_cue_supports(toks, pos, v, cands)
        namebearing = any((toks[i - 1].lower().strip(".,\"'();:") in gaz) for i in cands)
        for t in range(len(toks)):
            calib_top.append(float(marg[t].max()))
        it2 = {"toks": toks, "pos": pos, "v": v, "cands": cands, "patient": it["patient"],
               "pre": it["patient_position"] == "pre", "marg": marg, "shared": shared, "name": namebearing}
        items.append(it2)

    rng = np.random.default_rng(seed)
    sent_of = [" ".join(it["toks"]) for it in items]
    uniq = sorted(set(sent_of))
    perm = rng.permutation(len(uniq))
    test_sents = set(uniq[i] for i in perm[: len(uniq) // 2])
    train = [it for it, s in zip(items, sent_of) if s not in test_sents]
    test = [it for it, s in zip(items, sent_of) if s in test_sents]

    # per-variant: build train X/y with that animacy col, refit, evaluate on test
    weights = {}
    for var in VARIANTS:
        X, y = [], []
        for it in train:
            col = _animacy_column(var, it["toks"], it["pos"], it["cands"], it["marg"], Li, gaz,
                                  permute_rows=(rng.permutation(len(it["toks"])) if var == "twin" else None))
            gset = _span_set(it["patient"])
            for j, i in enumerate(it["cands"]):
                X.append([it["shared"][c][j] if c != "animacy" else col[j] for c in CUES])
                y.append(1.0 if (i - 1) in gset else 0.0)
        weights[var] = _fit_logistic(np.array(X), np.array(y))

    # evaluate
    def pick(it, var, w):
        col = _animacy_column(var, it["toks"], it["pos"], it["cands"], it["marg"], Li, gaz,
                              permute_rows=(np.random.default_rng(seed + hash(" ".join(it["toks"])) % 99999)
                                            .permutation(len(it["toks"])) if var == "twin" else None))
        S = {c: (it["shared"][c] if c != "animacy" else col) for c in CUES}
        idx = map_pick(S, w)
        return it["cands"][idx] if 0 <= idx < len(it["cands"]) else None

    slices = {"pre": {v: [] for v in VARIANTS}, "post": {v: [] for v in VARIANTS},
              "all": {v: [] for v in VARIANTS}, "name_pre": {v: [] for v in VARIANTS}}
    # floor via resolve_patient too (the true deployed floor, tag-based) for reference
    ref_resolve = {"pre": [], "post": [], "all": []}
    for it in test:
        g = it["patient"]
        rp = resolve_patient(it["toks"], it["pos"], it["v"], it["cands"])
        okrp = _in_span(rp, g)
        (ref_resolve["pre"] if it["pre"] else ref_resolve["post"]).append(okrp); ref_resolve["all"].append(okrp)
        for var in VARIANTS:
            ok = _in_span(pick(it, var, weights[var]), g)
            slices["all"][var].append(ok)
            (slices["pre"] if it["pre"] else slices["post"])[var].append(ok)
            if it["pre"] and it["name"]:
                slices["name_pre"][var].append(ok)

    def acc(d):
        return round(float(np.mean(d)), 4) if d else None
    res = {"n_items": len(items), "n_train": len(train), "n_test": len(test),
           "n_test_pre": len(slices["pre"]["floor"]), "n_test_name_pre": len(slices["name_pre"]["floor"]),
           "crf_mean_top_posterior": round(float(np.mean(calib_top)), 4),
           "learned_validities": {v: {c: round(weights[v][c], 3) for c in CUES} for v in VARIANTS},
           "acc": {sl: {v: acc(slices[sl][v]) for v in VARIANTS} for sl in slices},
           "ref_resolve_patient": {sl: acc(ref_resolve[sl]) for sl in ref_resolve}}
    # contrasts on the pre-verbal (non-canonical) slice + name sub-slice
    def C(sl, a, b):
        return _boot_diff(slices[sl][a], slices[sl][b], seed + hash(a + b + sl) % 9999)
    res["contrasts_pre"] = {
        "graded_minus_floor": C("pre", "graded", "floor"),
        "graded_minus_crf_hard": C("pre", "graded", "crf_hard"),
        "graded_minus_name_hard": C("pre", "graded", "name_hard"),
        "name_hard_minus_crf_hard": C("pre", "name_hard", "crf_hard"),
        "graded_minus_twin": C("pre", "graded", "twin"),
    }
    res["contrasts_name_pre"] = {
        "graded_minus_floor": C("name_pre", "graded", "floor"),
        "graded_minus_twin": C("name_pre", "graded", "twin"),
    }
    res["contrasts_post_netpos"] = {"graded_minus_floor": C("post", "graded", "floor")}
    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "graded_animacy_competition_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    res = run(smoke=(a.self_test or a.smoke))
    print(json.dumps({k: res[k] for k in ("n_items", "n_test_pre", "n_test_name_pre",
                                          "crf_mean_top_posterior", "acc", "contrasts_pre",
                                          "contrasts_name_pre", "contrasts_post_netpos", "elapsed_s")}, indent=2),
          flush=True)
    print("\n=== PRE-VERBAL (non-canonical) accuracy ===", flush=True)
    for v in VARIANTS:
        print("  %-10s %s" % (v, res["acc"]["pre"][v]), flush=True)
    print("  (ref resolve_patient pre = %s)" % res["ref_resolve_patient"]["pre"], flush=True)
    print("=== key contrasts (pre) ===", flush=True)
    for k, d in res["contrasts_pre"].items():
        print("  %-26s d=%+.4f CI[%+.4f,%+.4f] %s" % (k, d["delta"], d["ci"][0], d["ci"][1],
                                                      "SEP" if d["sep"] else "n.s."), flush=True)
    print("=== name-bearing pre sub-slice (n=%d) ===" % res["n_test_name_pre"], flush=True)
    for k, d in res["contrasts_name_pre"].items():
        print("  %-26s d=%+.4f CI[%+.4f,%+.4f] %s" % (k, d["delta"], d["ci"][0], d["ci"][1],
                                                      "SEP" if d["sep"] else "n.s."), flush=True)
    if a.self_test or a.smoke:
        assert res["n_test_pre"] > 30
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
