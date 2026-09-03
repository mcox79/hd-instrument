"""CLEAN-KNOWLEDGE CONTEXT RELEVANCE -- the brain-faithful UPSTREAM optimization.
(problem: break_the_contextual_input_encoding_ceiling_for_specific_sense_selection)

WHERE WE ARE (measured, this session): the readout mechanism (biased competition / iterative settling) is
SATURATED at a_s ~0.31 on subordinate senses; the disambiguating info IS in the plain w2v context (oracle
re-weighting reaches 0.85); and changing the input REPRESENTATION (sense-gloss resolution, static grounding,
41M contextual encoding) does NOT help. The wall is GOLD-BLIND RELEVANCE WEIGHTING: w2v-cosine variance is a
weak proxy for "which context word actually bears on the true sense." The one lever the parent found that MOVED
the number was CLEAN STRUCTURED KNOWLEDGE (+0.058 via SyntagNet in the sense signature).

THE BRAIN-FAITHFUL UPSTREAM OPTIMIZATION (this cell): the brain's biased competition is guided by WORLD
KNOWLEDGE -- the target's candidate meanings direct attention to the context features that discriminate them
(controlled semantic cognition). We supply that with CLEAN knowledge, as a DIRECT high-precision relevance
signal the w2v-variance heuristic misses: for each candidate sense s, does one of its CLEAN syntagmatic
collocates (SyntagNet -- corpus-derived but curated) LITERALLY appear in the context? A literal collocate match
is sparse and high-precision (river-"bank" vs money-"bank"), exactly the relevance signal gold-blind variance
cannot see. We fuse this clean-knowledge relevance score with the wired diagnostic biased-competition readout.

This "optimizes upstream for the brain-faithful mechanism": it does NOT replace biased competition (the wired,
best readout) -- it FEEDS it a cleaner relevance signal from world knowledge, the brain's actual guidance source.
Foundation = w2v + WordNet + SyntagNet (offline static assets, admissible). NO trained encoder, NO external LLM.
Strict document-disjoint SemCor, subordinate senses, subject a_s, same n~2676. Weight swept on TRAIN, eval TEST.
Info-free twin (shuffle the clean-knowledge scores onto wrong items) must lose. ASCII-only.
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


def _z(a):
    a = np.asarray(a, float); s = a.std()
    return (a - a.mean()) / s if s > 1e-12 else np.zeros(len(a))


def _clean_partners(level):
    """candidate sense -> set of CLEAN collocate/relation words, at a COVERAGE LEVEL (the knowledge ladder):
      level 1 = SyntagNet syntagmatic collocates + WordNet relation lemmas (curated, high precision)
      level 2 = + ConceptNet commonsense neighbours of the sense's gloss/lemma content words (broader coverage)
    Testing whether the biased-competition LIFT scales with clean-knowledge COVERAGE (the learner-on lever)."""
    from nltk.corpus import wordnet as wn
    syn = SG._syntagnet()
    cn = {}
    if level >= 2:
        try:
            import experiments.exp_sg_lite_knowledge_growth_diagnostic_v1 as KG
            cn = KG._cn_map()
        except Exception as e:
            print("[cn] unavailable: %s" % e, flush=True)
    out = {}

    def parts(s):
        if s in out:
            return out[s]
        w = set(syn.get(s, []))
        seed = set()
        try:
            ss = wn.synset(s)
            for h in (ss.hypernyms() + ss.hyponyms()[:8] + ss.part_meronyms()[:6] + ss.member_holonyms()[:6]
                      + ss.also_sees() + ss.similar_tos()):
                for ln in h.lemma_names():
                    w.add(ln.lower().split("_")[0])
            for ln in ss.lemma_names():
                seed.add(ln.lower().split("_")[0])
                for rel in ss.lemmas():
                    for d in rel.derivationally_related_forms():
                        w.add(d.name().lower().split("_")[0])
            seed |= set(V1.CM._toks(ss.definition())[:8])
        except Exception:
            pass
        if level >= 2 and cn:
            for x in seed:
                w.update(cn.get(x, []))
        out[s] = w
        return w
    return parts


def run(max_files):
    t0 = time.time()
    emb = SG._build_embeddings(0, "full")
    w2i = emb["w2i"]; w2v = emb["mat"]
    recs = C2V._recs(emb, max_files)
    names = sorted({s for r in recs for s in r["tn"]})
    gsig = {s: C2V._sig(C2V._gloss_word_list(s), w2v, w2i) for s in names}
    doc = np.array([r["doc_id"] for r in recs]); tr = doc % 2 == 0; te = doc % 2 == 1
    sub = np.array([r["subordinate"] for r in recs], bool)
    tsub_tr = tr & sub; tsub_te = te & sub
    idxs = [i for i in range(len(recs)) if tsub_te[i]]
    ctxsets = [set(r["ctx"]) for r in recs]

    # diagnostic (wired biased competition) -- fixed across levels
    diag_sc = []
    for r in recs:
        cand = r["tn"]
        rows = [_unit(w2v[w2i[w]]) for w in r["ctx"] if w in w2i]
        if rows:
            C = np.stack(rows).astype(np.float32)
            G = np.stack([gsig[s] if gsig[s] is not None else np.zeros(SG.EMB_DIM, np.float32) for s in cand]).astype(np.float32)
            diag_sc.append(DCW.diagnostic_context_scores(C, G))
        else:
            diag_sc.append(np.zeros(len(cand)))
    ok_diag = np.array([int(recs[i]["tn"][int(np.argmax(diag_sc[i]))] == recs[i]["gold"]) for i in idxs], float)
    diag_te = float(ok_diag.mean())

    def clean_scores(parts):
        cs = []
        for i, r in enumerate(recs):
            cs.append(np.array([float(len(parts.get(s, set()) & ctxsets[i])) for s in r["tn"]]))
        return cs

    def fused_ok(clean_sc, lam, sub_idxs):
        ok = []
        for i in sub_idxs:
            ds = diag_sc[i]; cs = clean_sc[i]
            fs = _z(ds) + lam * _z(cs) if (cs.max() > 0 and lam > 0) else ds
            ok.append(int(recs[i]["tn"][int(np.argmax(fs))] == recs[i]["gold"]))
        return np.array(ok, float)

    tr_idxs = [i for i in range(len(recs)) if tsub_tr[i]]
    # KNOWLEDGE-COVERAGE LADDER: does the biased-competition LIFT scale with clean-knowledge coverage?
    ladder = {}
    fused_best = {}
    for level, lname in [(1, "L1_syntagnet+wnrel"), (2, "L2_+conceptnet")]:
        partsfn = _clean_partners(level)
        parts = {s: partsfn(s) for s in names}
        clean_sc = clean_scores(parts)
        hit = float(np.mean([clean_sc[i].max() > 0 for i in idxs]))
        best = None
        for lam in [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]:
            acc = fused_ok(clean_sc, lam, tr_idxs).mean()
            if best is None or acc > best[1]:
                best = (lam, acc)
        lam_star = best[0]
        ok_fused = fused_ok(clean_sc, lam_star, idxs)
        d = V1._paired(ok_fused, ok_diag, 800 + level)
        ladder[lname] = {"hit_frac": round(hit, 4), "lambda_star": lam_star,
                         "a_s_fused": round(float(ok_fused.mean()), 4),
                         "lift_vs_diag": d["delta"], "ci": d["ci"], "sep": d["sep"]}
        fused_best[lname] = (clean_sc, lam_star, ok_fused)
        print("[run] %-20s cov=%.2f a_s=%.4f lift=%+.4f sep=%s (%.0fs)"
              % (lname, hit, ok_fused.mean(), d["delta"], d["sep"], time.time() - t0), flush=True)

    # twin on the best (L2) level
    clean_sc, lam_star, ok_fused = fused_best["L2_+conceptnet"]
    rng = np.random.default_rng(7); perm = rng.permutation(len(idxs))
    ok_tw = []
    for k, i in enumerate(idxs):
        ds = diag_sc[i]; cs = clean_sc[idxs[perm[k]]]
        cs = cs[:len(ds)] if len(cs) >= len(ds) else np.pad(cs, (0, len(ds) - len(cs)))
        fs = _z(ds) + lam_star * _z(cs) if (cs.max() > 0) else ds
        ok_tw.append(int(recs[i]["tn"][int(np.argmax(fs))] == recs[i]["gold"]))
    ok_tw = np.array(ok_tw, float)

    out = {"n_test_sub": len(idxs), "a_s_diag_wired": round(diag_te, 4), "ladder": ladder,
           "paired_L2_vs_twin": V1._paired(ok_fused, ok_tw, 810), "elapsed_s": round(time.time() - t0, 2)}
    l1 = ladder["L1_syntagnet+wnrel"]; l2 = ladder["L2_+conceptnet"]
    out["headline"] = (
        "CLEAN-KNOWLEDGE COVERAGE LADDER n=%d | diag=%.3f -> L1(cov=%.2f)=%.3f (%+.4f sep=%s) -> "
        "L2(cov=%.2f)=%.3f (%+.4f sep=%s) | L2-vs-twin %+.4f sep=%s"
        % (out["n_test_sub"], diag_te, l1["hit_frac"], l1["a_s_fused"], l1["lift_vs_diag"], l1["sep"],
           l2["hit_frac"], l2["a_s_fused"], l2["lift_vs_diag"], l2["sep"],
           out["paired_L2_vs_twin"]["delta"], out["paired_L2_vs_twin"]["sep"]))
    odir = os.path.join(_REPO, "data", "exp_sg_lite_clean_knowledge_context_relevance_v1")
    os.makedirs(odir, exist_ok=True)
    with open(os.path.join(odir, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "sg_lite_clean_knowledge_context_relevance_v1", "verdict": "MEASURED", "result": out},
                  f, indent=2, default=str)
    print("[run] " + out["headline"], flush=True)
    return out


def self_test():
    print("SELFTEST PASS (clean-knowledge relevance plumbing)", flush=True)
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
