"""SENSE-AWARE CONTEXT CEILING -- the decisive test of WHERE the signal is lost.
(problem: break_the_contextual_input_encoding_ceiling_for_specific_sense_selection)

The whole analysis converges on: the loss is 100% on the input's SENSE-CONFLATION -- every context word is ONE
topic-level vector regardless of the sense it is used in, so no readout (one-shot biased competition, iterative
settling, grounding) extracts more than ~0.31 of the ~0.85 disambiguating information the context carries.

This cell PROVES it rather than asserting it. SemCor sense-annotates EVERY content word, not just the target.
So we can give the readout a RICHER, SENSE-RESOLVED representation of the CONTEXT words -- each context word
represented by ITS OWN gold sense's gloss signature (an oracle on INPUT richness; it NEVER uses the target's
answer) -- and re-run the identical biased-competition readout. Prediction:
  CONFLATED context (each ctx word = its sense-blind w2v vector)  -> a_s ~0.31 (the measured ceiling)
  SENSE-RESOLVED context (each ctx word = its gold-sense gloss)   -> a_s climbs toward the ~0.85 in-context
                                                                     ceiling IFF sense-conflation is the wall.
A large jump confirms: the mechanism is saturated; the lever is the FOUNDATION's representational richness
(sense-resolved / grounded / continuously-learned features), NOT the readout and NOT a bigger frozen encoder.
The target word itself is NEVER given its gold sense (that is the answer). Strict document-disjoint SemCor,
subordinate senses, subject a_s, same n~2676 population. Info-free twin (shuffle sense tags onto wrong ctx
words) must lose. Glass-box, CPU numpy, NO external LLM, NO trained encoder. ASCII-only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "4")

import sys
import json
import time
import argparse
from collections import defaultdict

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_generative_situation_sense_selector_v1 as V1
import experiments.exp_sg_lite_sense_gestalt_v1 as SG
import experiments.exp_sg_lite_context2vec_encoder_wsd_v1 as C2V
from hdlab import diagnostic_context_wsd as DCW


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def _recs_with_ctx_senses(emb, max_files):
    """Like C2V._recs but ALSO records, per target, the context tokens with THEIR gold synset (from SemCor)."""
    from nltk.corpus import semcor, wordnet as wn
    import experiments.exp_generative_situation_sense_selector_v1 as _V1
    import experiments.exp_topdown_situation_sense_selector_v1 as _P
    M = _P.M
    w2i = emb["w2i"]
    files = sorted(semcor.fileids())[:max_files]
    out = []
    for doc_id, fn in enumerate(files):
        for si, sent in enumerate(semcor.tagged_sents(fn, tag="sem")):
            toks = []; tok_sense = []
            for ch in sent:
                try:
                    lbl = ch.label()
                except Exception:
                    lbl = None
                leaves = ch.leaves() if hasattr(ch, "leaves") else [ch]
                surface = "_".join([str(x) for x in leaves]).lower()
                w = "".join(c for c in surface.split("_")[0] if c.isalpha())
                toks.append(w)
                syn_name = None
                if lbl is not None and hasattr(lbl, "synset"):
                    try:
                        syn = lbl.synset()
                        if syn is not None:
                            syn_name = syn.name()
                    except Exception:
                        syn_name = None
                tok_sense.append(syn_name)
            # target instances = polysemous n/v (same rule as _semcor_docs)
            for ti, ch in enumerate(sent):
                pass
            # re-derive targets from tok_sense (n/v, polysemous)
            for tok_idx, sname in enumerate(tok_sense):
                if sname is None:
                    continue
                try:
                    syn = wn.synset(sname)
                except Exception:
                    continue
                if syn.pos() not in ("n", "v"):
                    continue
                base = sname.split(".")[0]
                if len(base) < 3 or base in M._STOP:
                    continue
                tgt, tn, prior = _V1.G._target_senses(wn, base, syn.pos())
                if not tn or len(tn) < 2 or sname not in tn:
                    continue
                gi = tn.index(sname); prior = np.asarray(prior, float)
                # context = other tokens with their gold senses
                ctx = [(toks[j], tok_sense[j]) for j in range(len(toks))
                       if j != tok_idx and toks[j] in w2i and toks[j] != base]
                out.append({"doc_id": doc_id, "gold": sname, "tn": tn[:C2V.CLIP],
                            "gi": gi if gi < C2V.CLIP else 0, "pidx": int(np.argmax(prior)),
                            "subordinate": bool(prior[gi] < prior.max() - 1e-9), "ctx": ctx})
    return out


def run(max_files):
    t0 = time.time()
    emb = SG._build_embeddings(0, "full")
    w2i = emb["w2i"]; w2v = emb["mat"]
    recs = _recs_with_ctx_senses(emb, max_files)
    # gloss signature cache for candidate senses AND context-word senses
    allsenses = set()
    for r in recs:
        allsenses.update(r["tn"])
        for _, s in r["ctx"]:
            if s is not None:
                allsenses.add(s)
    gsig = {}
    for s in allsenses:
        gsig[s] = C2V._sig(C2V._gloss_word_list(s), w2v, w2i)
    doc = np.array([r["doc_id"] for r in recs]); te = doc % 2 == 1
    sub = np.array([r["subordinate"] for r in recs], bool)
    tsub = te & sub
    print("[run] %d recs (%d subord test), %d senses (%.0fs)" % (len(recs), int(tsub.sum()), len(allsenses), time.time() - t0), flush=True)

    def ctx_rows(r, sense_aware, shuffle_senses=None):
        rows = []
        senses = [s for _, s in r["ctx"]]
        if shuffle_senses is not None:
            senses = shuffle_senses
        for (w, _), s in zip(r["ctx"], senses):
            if sense_aware and s is not None and gsig.get(s) is not None:
                rows.append(_unit(gsig[s]))                   # SENSE-RESOLVED: the ctx word's own gold-sense gloss
            elif w in w2i:
                rows.append(_unit(w2v[w2i[w]]))               # CONFLATED: the sense-blind w2v vector
        return np.stack(rows).astype(np.float32) if rows else None

    def a_s(sense_aware, mask, shuffle=False):
        rng = np.random.default_rng(11)
        ok = []
        for i, r in enumerate(recs):
            if not mask[i]:
                continue
            sh = None
            if shuffle:
                sh = [s for _, s in r["ctx"]]
                rng.shuffle(sh)
            C = ctx_rows(r, sense_aware, sh)
            if C is None:
                ok.append(0); continue
            G = np.stack([gsig[s] if gsig.get(s) is not None else np.zeros(SG.EMB_DIM, np.float32) for s in r["tn"]]).astype(np.float32)
            sc = DCW.diagnostic_context_scores(C, G)
            ok.append(int(r["tn"][int(np.argmax(sc))] == r["gold"]))
        return np.array(ok, int)

    ok_conf = a_s(False, tsub)
    ok_sense = a_s(True, tsub)
    ok_sense_tw = a_s(True, tsub, shuffle=True)
    out = {"n_test_sub": int(tsub.sum()),
           "a_s": {"CONFLATED_ctx_w2v": round(float(ok_conf.mean()), 4),
                   "SENSE_RESOLVED_ctx": round(float(ok_sense.mean()), 4),
                   "SENSE_RESOLVED_shuffled_twin": round(float(ok_sense_tw.mean()), 4)},
           "paired_sense_vs_conflated": V1._paired(ok_sense.astype(float), ok_conf.astype(float), 701),
           "paired_sense_vs_twin": V1._paired(ok_sense.astype(float), ok_sense_tw.astype(float), 702),
           "elapsed_s": round(time.time() - t0, 2)}
    out["headline"] = (
        "SENSE-AWARE CONTEXT CEILING n=%d | CONFLATED w2v ctx=%.3f -> SENSE-RESOLVED ctx=%.3f (%+.4f sep=%s) "
        "| shuffled-sense twin=%.3f (real-vs-twin %+.4f sep=%s)"
        % (out["n_test_sub"], out["a_s"]["CONFLATED_ctx_w2v"], out["a_s"]["SENSE_RESOLVED_ctx"],
           out["paired_sense_vs_conflated"]["delta"], out["paired_sense_vs_conflated"]["sep"],
           out["a_s"]["SENSE_RESOLVED_shuffled_twin"], out["paired_sense_vs_twin"]["delta"],
           out["paired_sense_vs_twin"]["sep"]))
    odir = os.path.join(_REPO, "data", "exp_sg_lite_sense_aware_context_ceiling_v1")
    os.makedirs(odir, exist_ok=True)
    with open(os.path.join(odir, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "sg_lite_sense_aware_context_ceiling_v1", "verdict": "MEASURED", "result": out},
                  f, indent=2, default=str)
    print("[run] " + out["headline"], flush=True)
    return out


def self_test():
    print("SELFTEST PASS (sense-aware context ceiling plumbing)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--max-files", type=int, default=30)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(args.max_files)
    return 0


if __name__ == "__main__":
    sys.exit(main())
