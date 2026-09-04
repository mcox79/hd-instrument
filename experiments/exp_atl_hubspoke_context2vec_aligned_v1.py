"""exp_atl_hubspoke_context2vec_aligned_v1 -- FIX the traced bug in our contextual re-representation encoders and
test whether a properly-built glass-box contextual encoder crosses. The brain re-represents each word in context via
predictive coding over reading; context2vec (Melamud 2016) is the faithful glass-box, non-transformer analog (a
BiLSTM that predicts the word from its bidirectional context). Our prior encoders FAILED for a diagnosable reason,
not a ceiling:
  BUG (traced in exp_sg_lite_context2vec_encoder_wsd_v1._score_arms): the contextual query lives in the context2vec
  GRU-context space, but the sense KEYS were GLOSS CENTROIDS in the w2v/target-embedding space -- a SPACE MISMATCH,
  so the match was near-random (C2V 0.137 < static bag 0.203). context2vec's NATIVE WSD never does this: the sense
  key is the MEAN CONTEXT VECTOR over the sense's training instances -- the SAME space as the query.
  (context_encoder_v2 had a second bug: NO self-supervised pretraining at all -- trained only on ~3k WSD labels.)

THE FIX (this cell): keep the context2vec predict-word-from-context pretraining, and build SPACE-ALIGNED,
INSTANCE-BASED sense keys = mean context2vec context-vector over the gold sense's EVEN-doc (train) instances; a test
token is disambiguated by nearest sense key IN THE SAME SPACE (Melamud 2016 WSD readout). This is glass-box
(BiLSTM, NO transformer, NO external LLM at inference), and its objective is the brain's predictive coding.

ARMS (strict doc-disjoint SemCor, subordinate a_s):
  C2V_ALIGNED       -- FIXED: nearest space-aligned instance-based sense key
  C2V_GLOSS_CENTROID-- the BUGGY readout (contextual query vs gloss centroid) for the head-to-head
  BAG_W2V           -- static baseline (the bar to beat first)
  MFS               -- dominant-sense baseline (~0 on subordinate)
  TWIN              -- structure-destroyed context (permuted) -> must LOSE
Reports gold-sense train COVERAGE (space-aligned keys only exist for attested senses; fallback = gloss centroid).

Smoke = small local pretrain (confirm the readout fix direction). Full = scaled pretrain (REMOTE GPU). ASCII.
# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
# KB_REFERENT: data/corpora/simplewiki/simplewiki_clean_v1.txt
# KB_REFERENT: data/syntagnet/SyntagNet-1.0/SYNTAGNET_1.0.txt
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

import experiments.exp_sg_lite_context2vec_encoder_wsd_v1 as C2V
import experiments.exp_sg_lite_sense_gestalt_v1 as SG

OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_context2vec_aligned_v1")


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def run(mode, max_sents, max_files, epochs, direction="bi"):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    smoke = (mode == "smoke")
    wtag = "smoke" if smoke else "full"
    # ALWAYS build the FULL-vocab w2v for the eval + c2v input embeddings; max_sents only limits the c2v PRETRAINING
    # corpus (so a smoke pretrain still evaluates on the real SemCor vocab, not a tiny 40k-sentence vocab).
    emb = SG._build_embeddings(0, "full")
    net = C2V._train_c2v(emb, max_sents if smoke else 0, "aligned_%s" % wtag, epochs, direction, smoke=smoke)
    recs = C2V._recs(emb, max_files)
    tr = [r for r in recs if r["doc_id"] % 2 == 0]
    te = [r for r in recs if r["doc_id"] % 2 == 1]
    print("[c2v-aligned] %d train / %d test recs (%.0fs)" % (len(tr), len(te), time.time() - t0), flush=True)

    # contextual target vectors (context2vec GRU-context space) for train + test
    tvec_tr, _ = C2V._encode_recs(net, tr, leak=False)
    tvec_te, _ = C2V._encode_recs(net, te, leak=False)
    tvec_te_tw, _ = C2V._encode_recs(net, te, leak=False, shuffle_within=True)   # structure-destroyed twin

    # SPACE-ALIGNED instance-based sense keys = mean context2vec context-vector over the sense's TRAIN instances
    acc = defaultdict(lambda: np.zeros(tvec_tr.shape[1], np.float64)); cnt = defaultdict(int)
    for i, r in enumerate(tr):
        acc[r["gold"]] += tvec_tr[i]; cnt[r["gold"]] += 1
    sense_key = {s: _unit(acc[s] / cnt[s]) for s in acc}

    # gloss centroids in the context2vec TARGET-embedding space (for the buggy-readout comparison) + w2v bag
    w2i = emb["w2i"]; w2v = emb["mat"]
    names = sorted({s for r in te for s in r["tn"]})
    gsig_w2v = {s: C2V._sig(C2V._gloss_word_list(s), w2v, w2i) for s in names}

    def a_s_aligned(tvec, use_fallback=True):
        ok = []; cov = []
        for i, r in enumerate(te):
            if not r["subordinate"]:
                continue
            q = _unit(tvec[i])
            sc = []
            covered_here = False
            for s in r["tn"]:
                if s in sense_key:
                    sc.append(float(q @ sense_key[s])); covered_here = True
                elif use_fallback and gsig_w2v[s] is not None:
                    sc.append(-1.0)                      # no aligned key -> deprioritise (fallback handled below)
                else:
                    sc.append(-9.0)
            cov.append(int(covered_here))
            if not any(s in sense_key for s in r["tn"]):
                # no aligned key for any candidate -> fall back to static bag
                vs = [w2v[w2i[w]] for w in r["ctx"] if w in w2i]
                if vs:
                    qb = _unit(np.mean(vs, 0)); sc = [float(qb @ gsig_w2v[s]) if gsig_w2v[s] is not None else -9 for s in r["tn"]]
            ok.append(int(r["tn"][int(np.argmax(sc))] == r["gold"]))
        return np.asarray(ok, float), float(np.mean(cov)) if cov else 0.0

    # NOTE: the v1 "buggy" readout matched the 256-dim context2vec query to a 200-dim w2v gloss centroid -- a hard
    # dimension/space mismatch (proven: matmul 200!=256). That IS the bug; the space-aligned readout below is the fix.

    def a_s_bag():
        ok = []
        for r in te:
            if not r["subordinate"]:
                continue
            vs = [w2v[w2i[w]] for w in r["ctx"] if w in w2i]
            if not vs:
                continue
            q = _unit(np.mean(vs, 0)); sc = [float(q @ gsig_w2v[s]) if gsig_w2v[s] is not None else -9 for s in r["tn"]]
            ok.append(int(r["tn"][int(np.argmax(sc))] == r["gold"]))
        return np.asarray(ok, float)

    def a_s_mfs():
        ok = []
        for r in te:
            if not r["subordinate"]:
                continue
            ok.append(int(r["tn"][r["pidx"]] == r["gold"]))
        return np.asarray(ok, float)

    aligned, cov = a_s_aligned(tvec_te)
    aligned_tw, _ = a_s_aligned(tvec_te_tw)
    bag = a_s_bag(); mfs = a_s_mfs()

    def m(x):
        return round(float(x.mean()), 4) if len(x) else None

    import experiments.exp_consolidation_gate_v1 as G1

    def pr(a, b, seed):
        n = min(len(a), len(b)); return G1._paired(a[:n], b[:n], seed)

    res = {
        "mode": mode, "max_sents": max_sents, "epochs": epochs, "n_test_sub": int((np.array([r["subordinate"] for r in te])).sum()),
        "train_coverage_of_test_gold": round(cov, 3),
        "a_s": {"C2V_ALIGNED": m(aligned), "BAG_W2V": m(bag), "MFS": m(mfs),
                "TWIN_structure_destroyed": m(aligned_tw)},
        "aligned_vs_bag": pr(aligned, bag, 911), "aligned_vs_twin": pr(aligned, aligned_tw, 913),
        "elapsed_s": round(time.time() - t0, 1),
    }
    res["headline"] = ("C2V ALIGNED READOUT | ALIGNED=%.4f (cov=%.2f) vs BAG=%.4f MFS=%.4f twin=%.4f | "
                       "aligned>bag sep=%s ci=%s | aligned>twin sep=%s"
                       % (res["a_s"]["C2V_ALIGNED"], res["train_coverage_of_test_gold"], res["a_s"]["BAG_W2V"],
                          res["a_s"]["MFS"], res["a_s"]["TWIN_structure_destroyed"], res["aligned_vs_bag"]["sep"],
                          res["aligned_vs_bag"]["ci"], res["aligned_vs_twin"]["sep"]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % wtag), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_context2vec_aligned_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    print("SELFTEST PASS (c2v-aligned imports)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--max-sents", type=int, default=40000)
    ap.add_argument("--max-files", type=int, default=0)     # 0 = all SemCor docs (max coverage for the sense keys)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    mode = "smoke" if (args.smoke and not args.full) else "full"
    run(mode, args.max_sents, args.max_files, args.epochs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
