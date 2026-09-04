"""exp_graded_pos_whodidwhat_v1 -- does consuming the graded POS posterior in referent_per_np move LIVE who-did-what?

Direct test of the brief `consume_the_graded_pos_posterior_...`, against the STRONGEST floor actually deployed
(the landed referent_per_np with use_frame=True). The diagnostic (exp_graded_pos_diagnostic_v1) established:
  - referent introduction is INVARIANT to PROPN<->NOUN (both in NOMINAL) -> the brief's literal mechanism is out;
  - the ONLY coverage lever the graded posterior has is SOFT-NOMINAL recovery: open a referent for a content head
    the perceptron argmax tagged NON-nominal (missed by _content_head_positions) where the calibrated CRF
    nominal-mass P(NOUN)+P(PROPN) >= tau. That is 0.3-0.6% of heads over the frame detector -- this cell measures
    whether that (possibly patient-concentrated) recovery moves the LIVE who-did-what number.

ARMS (one variable = the referent head set; everything else the live default reader):
  floor  : the landed referent_per_np_source (base content heads + frame recoveries). The strongest deployed floor.
  soft   : floor + CRF soft-nominal heads (nom_mass >= tau, eligible, not already a head).
  twin   : floor + SHUFFLED-posterior heads (permute nom_mass across positions, same tau) -- info-free, matched
           mechanism/threshold, must LOSE. Isolates "the posterior VALUES pick the right positions" from
           "adding K more referents helps at all".

Scored: effective end-to-end who-did-what PATIENT through the LIVE reader (abstain = wrong), FULL + CLEAN_DO
regimes, paired bootstrap CI + sign-flip null. Reuses the organ's own eval harness gold/scoring
(exp_referent_per_np_end_to_end_v1). Glass-box, CPU, NO LLM. hdlab READ (monkeypatched at runtime). ASCII. own dir.
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import argparse, glob, json, time
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_19c_composed_cleaned_gold_v1 as CG
import experiments.exp_referent_per_np_end_to_end_v1 as E2E   # reuse _norm, score, _boot_delta
from hdlab.pos_tagger import PosTagger
from hdlab.crf_tagger import GlassBoxCRF
from hdlab.scene_segment import parse_conll_sentences
from hdlab.coref import parse_litbank_conll
import hdlab.referent_per_np as RNP
from hdlab.referent_per_np import (_content_head_positions, frame_heads, _mk_referent, _finalize, STOP)
from hdlab.situation_reader import SituationReader

OUT_DIR = os.path.join(_REPO, "data/exp_graded_pos_whodidwhat_v1")
CORPUS = os.path.join(_REPO, "data/corpora/litbank_coref_conll")
POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
LB = os.path.join(_REPO, "data/predict_revise_recall_v1/_population_litbank.json")

_CRF = None
_ORIG_RNP_SOURCE = RNP.referent_per_np_source


def _crf():
    global _CRF
    if _CRF is None:
        _CRF = GlassBoxCRF.load()
    return _CRF


def _eligible(toks, i, exclude):
    return (i not in exclude) and (toks[i].lower() not in STOP) and (len(toks[i]) >= 3)


def make_source(mode, tau, seed=20260904):
    """Return a referent_per_np_source-signature fn: (conll_path, tagger, name_gender_map=None, use_frame=True).
    floor == the landed source; soft/twin add extra heads from the CRF nominal-mass (true vs shuffled)."""
    crf = _crf()

    def _src(conll_path, tagger, name_gender_map=None, use_frame=True):
        coref, n_sents = parse_litbank_conll(conll_path, name_gender_map=name_gender_map)
        sents = parse_conll_sentences(conll_path)
        coref_head_wpos = {}
        pron = [m for m in coref if m["is_pronoun"]]
        for m in coref:
            if m["is_pronoun"]:
                continue
            span = max(0, m["gtok_end"] - m["gtok_start"])
            coref_head_wpos[(m["sent_idx"], m["wtok_start"] + span)] = m["cluster"]
        next_cluster = max([m["cluster"] for m in coref], default=-1) + 1
        rng = np.random.default_rng(seed + (hash(os.path.basename(conll_path)) % 100000))
        out = []
        for si, toks in enumerate(sents):
            if si >= n_sents:
                break
            up = tagger.tag(list(toks))
            base = set(_content_head_positions(toks, up))
            heads = set(sorted(base | frame_heads(toks, up, base))) if use_frame else base
            if mode in ("soft", "twin"):
                M = crf.marginals(toks)
                Li = crf.Li
                nm = M[:, Li["NOUN"]] + M[:, Li["PROPN"]]
                if mode == "twin":
                    nm = nm[rng.permutation(len(nm))]   # shuffled posterior (position-scrambled, same distribution)
                extra = [i for i in range(len(toks)) if _eligible(toks, i, heads) and nm[i] >= tau]
                heads = heads | set(extra)
            for hw in sorted(heads):
                cl = coref_head_wpos.get((si, hw))
                if cl is None:
                    cl = next_cluster
                    next_cluster += 1
                out.append(_mk_referent(toks[hw].lower(), si, hw, cl, -1))
        return _finalize(pron + out), n_sents

    return _src


def read_doc_patients(reader, path, mode, tau):
    """Run the LIVE default reader with referent_per_np_source swapped to the given mode; return
    {(norm_sent, pred_idx): patient_low}."""
    RNP.referent_per_np_source = make_source(mode, tau)
    try:
        sm = reader.read(path)
    finally:
        RNP.referent_per_np_source = _ORIG_RNP_SOURCE
    sents = parse_conll_sentences(path)
    sent_norm = {si: E2E._norm(toks) for si, toks in enumerate(sents)}
    picks = {}
    for e in sm.events:
        if e.pred_idx is None:
            continue
        key = (sent_norm.get(e.sent_idx), e.pred_idx)
        if key[0] is None:
            continue
        picks[key] = (e.patient or "?").lower()
    return picks


def run(n_docs=None, tau=0.7, n_boot=1000, seed=20260904):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tagger = PosTagger.load(POS_ASSET)
    gaz = {}
    try:
        import experiments.exp_situation_qa_v1 as SITQA
        gaz = SITQA.load_given_gazetteer()
    except Exception:
        gaz = {}
    reader = SituationReader(gaz=gaz)   # LIVE default reader (referent_per_np default-ON)
    docs = sorted(glob.glob(os.path.join(CORPUS, "*.conll")))
    if n_docs:
        docs = docs[:n_docs]

    rows_all = V1.load_pop(LB)
    doc_sents = set()
    for d in docs:
        for toks in parse_conll_sentences(d):
            doc_sents.add(E2E._norm(toks))
    rows = [r for r in rows_all if r.get("gold_head") and E2E._norm(r["sent"]) in doc_sents]
    clean_flags = np.array([CG.is_clean_do(r, tagger.tag(r["sent"].split()))[0] for r in rows], dtype=bool)

    modes = ["floor", "soft", "twin"]
    picks = {m: {} for m in modes}
    for d in docs:
        for m in modes:
            picks[m].update(read_doc_patients(reader, d, m, tau))

    hits = {m: E2E.score(rows, picks[m]) for m in modes}
    res = {"n_docs": len(docs), "tau": tau, "n_clauses_full": len(rows),
           "n_clauses_clean_do": int(clean_flags.sum())}
    for regime, mask in [("FULL", np.ones(len(rows), dtype=bool)), ("CLEAN_DO", clean_flags)]:
        h = {m: hits[m][mask] for m in modes}
        acc = {m: float(h[m].mean()) for m in modes}
        block = {"n": int(mask.sum()), "acc": {m: round(acc[m], 4) for m in modes}}
        for name, a, b in [("soft_vs_floor", "soft", "floor"),
                           ("soft_vs_twin", "soft", "twin"),
                           ("twin_vs_floor", "twin", "floor")]:
            dlt, lo, hi, half, p95 = E2E._boot_delta(h[a], h[b], n_boot, seed)
            block[name] = {"delta": round(dlt, 4), "ci_lo": round(lo, 4), "ci_hi": round(hi, 4),
                           "ci_half": round(half, 4), "null_p95": round(p95, 4),
                           "ci_separated": bool(lo > 0)}
        res[regime] = block
    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "graded_pos_whodidwhat_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--tau", type=float, default=0.7)
    ap.add_argument("--nboot", type=int, default=1000)
    a = ap.parse_args()
    nd = 3 if (a.self_test or a.smoke) else a.docs
    res = run(n_docs=nd, tau=a.tau, n_boot=(200 if (a.self_test or a.smoke) else a.nboot))
    print(json.dumps(res, indent=2), flush=True)
    for regime in ("FULL", "CLEAN_DO"):
        b = res[regime]
        print("\n-- %s (n=%d), tau=%.2f --" % (regime, b["n"], res["tau"]), flush=True)
        print("  floor %.4f | soft %.4f | twin %.4f" % (b["acc"]["floor"], b["acc"]["soft"], b["acc"]["twin"]), flush=True)
        for k in ("soft_vs_floor", "soft_vs_twin", "twin_vs_floor"):
            d = b[k]
            print("    %-16s d=%+.4f CI[%+.4f,%+.4f] half=%.4f %s"
                  % (k, d["delta"], d["ci_lo"], d["ci_hi"], d["ci_half"],
                     "CI-SEP" if d["ci_separated"] else "n.s."), flush=True)
    if a.self_test or a.smoke:
        assert res["n_clauses_full"] >= 15, "too few matched clauses"
        assert res["FULL"]["acc"]["soft"] >= res["FULL"]["acc"]["floor"] - 0.05, "soft should not collapse vs floor on smoke"
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
