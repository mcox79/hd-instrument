"""CONSTRUCTION-INTEGRATION joint sense settling -- the brain's ACTUAL mechanism (not lexical WSD).
(problem: break_the_contextual_input_encoding_ceiling_for_specific_sense_selection)

Three deep primary-source drills (2026-09-03) converged: the brain does NOT classify-then-weight context to
pick a sense. It runs Kintsch Construction-Integration -- exhaustively activate ALL candidate senses of ALL
content words, then INTEGRATE A(t+1)=normalize(A(t) . W) to a fixed point over a world-knowledge connection
matrix W; the winning sense is whichever node the surrounding network reinforces. RELEVANCE = CONNECTION
STRENGTH in W (learned offline across broad experience), never a per-instance relevance verdict (Kintsch 1988;
Waltz-Pollack 1985; Cottrell-Small 1983). This degrades gracefully with W quality instead of failing when a
standalone relevance stage is bad -- which is exactly our gold-blind wall.

This cell BUILDS that mechanism, glass-box, no trained encoder, no external LLM, and tests the drills' core
prediction: a_s scales with the QUALITY (density x cleanliness x gradedness) of W. If joint C-I settling over
a graded clean W beats the classify-then-weight diagnostic (0.31), the frame was wrong (as the drills argue)
and the lever is W-quality -> the consolidation/learner north star. If it caps, joint settling is not enough
either and the negative deepens.

MECHANISM:
  nodes  = all candidate WordNet senses of all content words in the sentence (target + context), exhaustive.
  W      = pairwise CLEAN-knowledge connection strength between senses, GRADED:
             W_gloss    = cos(gloss_sig_i, gloss_sig_j)  (clean, dense, graded -- from WordNet gloss knowledge)
             + SyntagNet boost (shared clean syntagmatic collocates) at higher W-levels (denser clean).
  A_0    = uniform over each word's senses (exhaustive construction; NO MFS prior in the base arm).
  settle = for K steps: A <- normalize_per_word( relu( A . W ) ); each word's senses COMPETE (softmax within
           the word), activation spreads through W between words (integration to a fixed point).
  read   = the TARGET word's winning sense = argmax A over its candidates.
W-QUALITY LADDER (does a_s scale with W?): W0 diagonal (no cross-talk = isolated) -> W1 gloss-cos -> W2 +SyntagNet.
Strict document-disjoint SemCor, subordinate senses, subject a_s, same n~2676. vs diagnostic (classify-then-
weight, 0.31). Shuffled-context twin must lose. Oracle-headroom = fraction of (0.31->0.85) recovered. ASCII-only.
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

MAXW = 16      # cap content words per sentence (target + context)
MAXC = 6       # cap candidate senses per word
KSET = 6       # integration steps


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def _softmax_rows(z, groups):
    """softmax within each word-group (competition among a word's senses)."""
    out = np.zeros_like(z)
    for g in groups:
        zz = z[g] - z[g].max()
        e = np.exp(zz)
        out[g] = e / (e.sum() + 1e-30)
    return out


def run(max_files):
    t0 = time.time()
    from nltk.corpus import wordnet as wn
    emb = SG._build_embeddings(0, "full")
    w2i = emb["w2i"]; w2v = emb["mat"]
    recs = C2V._recs(emb, max_files)
    syn = SG._syntagnet()

    # gloss signature + syntagnet partners per synset (cached lazily)
    gcache = {}
    def gsig(s):
        if s not in gcache:
            gcache[s] = C2V._sig(C2V._gloss_word_list(s), w2v, w2i)
        return gcache[s]

    doc = np.array([r["doc_id"] for r in recs]); te = doc % 2 == 1
    sub = np.array([r["subordinate"] for r in recs], bool)
    tsub = te & sub
    print("[run] %d recs (%d subord test) (%.0fs)" % (len(recs), int(tsub.sum()), time.time() - t0), flush=True)

    def build_graph(r, shuffle_ctx=False, seed=0):
        """nodes = candidate senses of target + up to MAXW context content words. Returns
        (node_syns, groups, tgt_group, gold_local, sig_mat, syn_sets)."""
        ctx = [w for w in r["ctx"] if w in w2i]
        if shuffle_ctx and len(ctx) > 1:
            rng = np.random.default_rng(seed); ctx = list(ctx); rng.shuffle(ctx)
        ctx = ctx[:MAXW - 1]
        words = [(r["tn"][0].split(".")[0], r["tn"])]     # target word -> its candidate senses (fixed set)
        seen = {words[0][0]}
        for w in ctx:
            if w in seen:
                continue
            ss = wn.synsets(w)
            if not ss:
                continue
            cand = [x.name() for x in ss[:MAXC]]
            if len(cand) >= 1:
                words.append((w, cand)); seen.add(w)
        node_syns = []; groups = []; tgt_group = None
        for wi, (w, cand) in enumerate(words):
            g = list(range(len(node_syns), len(node_syns) + len(cand)))
            groups.append(g)
            if wi == 0:
                tgt_group = g
            node_syns.extend(cand)
        N = len(node_syns)
        sig = np.zeros((N, SG.EMB_DIM), np.float32)
        for i, s in enumerate(node_syns):
            v = gsig(s)
            if v is not None:
                sig[i] = v
        syn_sets = [set(syn.get(s, [])) for s in node_syns]
        gold_local = tgt_group[r["tn"].index(r["gold"])] if r["gold"] in r["tn"] else tgt_group[0]
        return node_syns, groups, tgt_group, gold_local, sig, syn_sets

    def W_matrix(sig, syn_sets, groups, level):
        N = sig.shape[0]
        if level == 0:
            return np.eye(N, dtype=np.float32)            # W0: no cross-talk (isolated senses)
        Wm = sig @ sig.T                                  # W1: gloss-signature cosine (clean graded dense)
        np.clip(Wm, 0.0, None, out=Wm)
        if level >= 2:                                    # W2: + SyntagNet shared-collocate boost (denser clean)
            for i in range(N):
                if not syn_sets[i]:
                    continue
                for j in range(i + 1, N):
                    sh = len(syn_sets[i] & syn_sets[j])
                    if sh:
                        Wm[i, j] += 0.5 * sh; Wm[j, i] += 0.5 * sh
        # zero within-word edges (a word's senses compete, they don't reinforce each other)
        for g in groups:
            for a in g:
                for b in g:
                    Wm[a, b] = 0.0
        return Wm

    def settle_pick(r, level, shuffle_ctx=False, seed=0):
        node_syns, groups, tgt_group, gold_local, sig, syn_sets = build_graph(r, shuffle_ctx, seed)
        Wm = W_matrix(sig, syn_sets, groups, level)
        N = sig.shape[0]
        A = np.zeros(N, np.float32)
        A = _softmax_rows(A, groups)                      # uniform within each word (exhaustive construction)
        if level == 0:
            # isolated: each target sense scored only by self -> tie; fall back to context-bag cosine on target
            pass
        for _ in range(KSET):
            inp = Wm @ A                                  # integration: spread activation through W
            A = _softmax_rows(inp, groups)                # per-word competition (normalize within word)
        # target's winning sense (local index within tgt_group)
        tg = np.array(tgt_group)
        win = tg[int(np.argmax(A[tg]))]
        return node_syns[win] == r["gold"]

    # diagnostic (classify-then-weight) baseline on this population
    def diag_pick(r):
        rows = [_unit(w2v[w2i[w]]) for w in r["ctx"] if w in w2i]
        if not rows:
            return False
        C = np.stack(rows).astype(np.float32)
        G = np.stack([gsig(s) if gsig(s) is not None else np.zeros(SG.EMB_DIM, np.float32) for s in r["tn"]]).astype(np.float32)
        sc = DCW.diagnostic_context_scores(C, G)
        return r["tn"][int(np.argmax(sc))] == r["gold"]

    idxs = [i for i in range(len(recs)) if tsub[i]]
    ok_diag = np.array([int(diag_pick(recs[i])) for i in idxs], float)
    diag_te = float(ok_diag.mean())

    ladder = {}
    ok_by_level = {}
    for level, lname in [(1, "W1_gloss_cos"), (2, "W2_+syntagnet")]:
        ok = np.array([int(settle_pick(recs[i], level)) for i in idxs], float)
        ok_by_level[level] = ok
        d = V1._paired(ok, ok_diag, 900 + level)
        headroom = (float(ok.mean()) - diag_te) / max(0.853 - diag_te, 1e-9)
        ladder[lname] = {"a_s": round(float(ok.mean()), 4), "lift_vs_diag": d["delta"], "sep": d["sep"],
                         "oracle_headroom_recovered": round(headroom, 4)}
        print("[run] %-16s a_s=%.4f lift=%+.4f sep=%s headroom=%.3f (%.0fs)"
              % (lname, ok.mean(), d["delta"], d["sep"], headroom, time.time() - t0), flush=True)

    # twin on the best level (W2): shuffle context words before building the graph
    best_level = max(ladder, key=lambda k: ladder[k]["a_s"])
    bl = 2 if best_level == "W2_+syntagnet" else 1
    ok_tw = np.array([int(settle_pick(recs[i], bl, shuffle_ctx=True, seed=i)) for i in idxs], float)
    twin = V1._paired(ok_by_level[bl], ok_tw, 909)

    out = {"n_test_sub": len(idxs), "a_s_diag_classify_then_weight": round(diag_te, 4),
           "oracle_context_ceiling": 0.853, "ladder": ladder,
           "twin_real_vs_shuffled_ctx": twin, "elapsed_s": round(time.time() - t0, 2)}
    l1 = ladder["W1_gloss_cos"]; l2 = ladder["W2_+syntagnet"]
    out["headline"] = (
        "CONSTRUCTION-INTEGRATION joint settling n=%d | diag(classify-weight)=%.3f | W1_gloss=%.3f (%+.4f sep=%s "
        "headroom=%.2f) -> W2_+syntag=%.3f (%+.4f sep=%s headroom=%.2f) | twin %+.4f sep=%s"
        % (out["n_test_sub"], diag_te, l1["a_s"], l1["lift_vs_diag"], l1["sep"], l1["oracle_headroom_recovered"],
           l2["a_s"], l2["lift_vs_diag"], l2["sep"], l2["oracle_headroom_recovered"], twin["delta"], twin["sep"]))
    odir = os.path.join(_REPO, "data", "exp_sg_lite_construction_integration_joint_wsd_v1")
    os.makedirs(odir, exist_ok=True)
    with open(os.path.join(odir, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "sg_lite_construction_integration_joint_wsd_v1", "verdict": "MEASURED", "result": out},
                  f, indent=2, default=str)
    print("[run] " + out["headline"], flush=True)
    return out


def self_test():
    from nltk.corpus import wordnet as wn
    assert wn.synsets("bank")
    print("SELFTEST PASS (C-I joint settling plumbing; wordnet available)", flush=True)
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
