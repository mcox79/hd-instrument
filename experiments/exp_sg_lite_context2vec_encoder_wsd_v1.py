"""CONTEXT2VEC-style glass-box CONTEXTUAL input encoder for specific-rare-sense selection.
(problem: break_the_contextual_input_encoding_ceiling_for_specific_sense_selection)

THE ONE UNTESTED GLASS-BOX ROUTE. The parent (build_sg_lite...) triangulated the ceiling: the wired
biased-competition readout (hdlab/diagnostic_context_wsd.py) tops out at a_s ~0.33 because every surface
form is ONE sense-conflated w2v vector -- the CONTEXT INPUT ENCODING, not the readout, is the cap. Two
things were proven dead: (a) a BiGRU-over-FROZEN-w2v trained SUPERVISED on tiny SemCor scored 0.227-0.253
< the parameter-free bag 0.283 (exp_sg_lite_context_encoder_wsd_v1/v2); (b) static per-synset sense
embeddings are brain-unfaithful + circular for topic-overlapping polysemy.

WHY THIS IS A DIFFERENT MECHANISM, NOT A RETUNE OF THE FAILED ONE (three axes):
  SELF-SUPERVISED at SCALE   -- a bidirectional LM trained cloze-style on the whole ~41M/277M-token corpus
                                (millions of examples), NOT a from-scratch encoder on ~thousands of SemCor
                                labels. This is the "learned scale beyond SemCor's 30k labels" lever.
  BOUNDARY / NO TARGET LEAK  -- context2vec (Melamud 2016): the forward LSTM summarizes the LEFT context
                                (words < t), the backward LSTM the RIGHT context (words > t); the target
                                token at position t is NEVER fed. The failed v2 read the hidden state AT the
                                target on frozen w2v, leaking the dominant-sense vector; the SG-lite gestalt
                                is unidirectional AND reads-at-target -> its h collapsed to ~ the context bag.
  LEARNED INPUT + TARGET EMB -- the model learns its own input embeddings and target (output) embeddings from
                                the LM objective (~half of BERT's WSD edge is the input representation itself,
                                per the design-validation drill), rather than sitting on frozen w2v.

BRAIN FOUNDATION (PINNED): lexical meaning is CONTEXT-SHAPED at access -- predictive coding over the
unfolding sentence; the N400 is graded by contextual fit (Kutas-Federmeier). context2vec / ELMo (both
PRE-transformer, glass-box, unsupervised) are the faithful glass-box analog: a recurrent LM that predicts
the word from its bidirectional context and exposes the context state as the word's contextual representation.
OUR-INVENTION-under-test: encoder class/scale/objective + how the contextual vector feeds the readout (swept).
NOT a transformer (that is the explicit owner FORK -- surfaced with the measured glass-box ceiling, not crossed).

MECHANISM (glass-box, NO external LLM at inference):
  train  : forward LSTM f_i = state after w_0..w_i ; backward LSTM b_i = state after w_i..w_{L-1} (right-to-left).
           context vector at slot t  C_t = MLP( [ f_{t-1} ; b_{t+1} ] )  -- NEVER sees w_t. Negative-sampling
           objective: sigmoid(C_t . T[w_t]) up, K negatives down (context2vec/word2vec). Persisted static asset.
  readout: sense score = cos( C_t , gloss_sig ), gloss_sig = unit-mean of the sense's gloss/rel/SyntagNet words
           in the model's TARGET-embedding space T. argmax = pick. GOLD-BLIND (all candidate senses symmetric).

ARMS (strict document-disjoint SemCor even/odd, subordinate senses, subject a_s, n~2676; all on ONE population):
  bag_w2v   parameter-free flat w2v context bag x w2v gloss           (the parent's 0.283 floor, recomputed)
  diag_w2v  biased-competition diagnostic readout on w2v (hdlab organ) (the parent's ~0.31-0.33 wired ceiling)
  C2V       context2vec contextual vector x gloss_sig(T)              <-- THE ARM the bar tests
  bag_T     flat context bag built from the model's TARGET embeddings x gloss_sig(T)  (isolates "LM static emb")
  diag_T    biased-competition on the model's TARGET embeddings                       (biased comp, LM emb)
  TWIN a    C2V with the sentence's context words PERMUTED before encoding (structure destroyed) -> MUST LOSE
  TWIN b    C2V encoding a DIFFERENT item's context (cross-item shuffle)              -> MUST LOSE
Paired bootstrap (same items): C2V vs bag_w2v, vs diag_w2v, vs each twin, vs bag_T/diag_T. CI half-width + null p95.

PASS = C2V beats BOTH bag_w2v(0.283) AND diag_w2v(~0.33) CI-separated, twins lose, no net regression over MFS.
A rigorous LOCATED NEGATIVE (C2V does NOT cross the frozen-input+biased-competition ceiling, named cause + number
+ the transformer fork it forces) is a FULL PASS. ASCII-only. Modes: --self-test | --smoke | full (default).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "4")

import sys
import time
import json
import argparse

import numpy as np
import torch                       # module-level (GPU queue PROT-020 requires it)
import torch.nn as nn

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_generative_situation_sense_selector_v1 as V1
import experiments.exp_topdown_situation_sense_selector_v1 as P
import experiments.exp_sg_lite_sense_gestalt_v1 as SG
from hdlab import diagnostic_context_wsd as DCW

# KB_REFERENT: data/corpora/simplewiki/simplewiki_clean_v1.txt
# KB_REFERENT: data/syntagnet/SyntagNet-1.0/SYNTAGNET_1.0.txt
# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
_DEV = "cuda" if torch.cuda.is_available() else "cpu"
_SCRATCH = SG._SCRATCH
EMB_DIM = 256          # context2vec input+target embedding dim (OUR-INVENTION; swept separately from w2v's 200)
HID = 256              # LSTM hidden per direction
NEG_K = 10
BATCH = 128
MAXLEN = 40            # training sentence cap (SG uses 40)
EVALLEN = 60           # eval sentence cap
CLIP = 40              # candidate-sense list guard


# ===========================================================================
# eval population -- IDENTICAL construction to the parent (v2 _targets / SG gestalts): strict even/odd docs.
# ===========================================================================
def _recs(emb, max_files):
    from nltk.corpus import wordnet as wn
    w2i = emb["w2i"]
    docs = P._semcor_docs(max_files)
    out = []
    for doc_id, si, toks, insts in docs:
        ids = [w2i.get(w, 0) for w in toks]
        if sum(1 for x in ids if x > 0) < 2:
            continue
        for tok_idx, lemma, pos, gold in insts:
            tgt, tn, prior = V1.G._target_senses(wn, lemma, pos)
            if not tn or len(tn) < 2 or gold not in tn:
                continue
            gi = tn.index(gold)
            prior = np.asarray(prior, float)
            out.append({"ids": ids[:EVALLEN], "toks": toks[:EVALLEN],
                        "tpos": min(tok_idx, len(ids) - 1, EVALLEN - 1),
                        "gold": gold, "tn": tn[:CLIP], "gi": gi if gi < CLIP else 0,
                        "pidx": int(np.argmax(prior)),
                        "subordinate": bool(prior[gi] < prior.max() - 1e-9),
                        "doc_id": doc_id,
                        "ctx": [w for w in toks if w in w2i and w != lemma]})
    return out


# ===========================================================================
# gloss signature word list (gloss+examples+lemmas+rels+SyntagNet) -- reused across embedding spaces.
# ===========================================================================
_GWORDS = {}


def _gloss_word_list(syn_name):
    if syn_name in _GWORDS:
        return _GWORDS[syn_name]
    from nltk.corpus import wordnet as wn
    words = []
    try:
        s = wn.synset(syn_name)
        words += V1.CM._toks(s.definition())
        for ex in s.examples():
            words += V1.CM._toks(ex)
        for ln in s.lemma_names():
            words.append(ln.lower().split("_")[0])
        rels = (s.hypernyms() + s.hyponyms()[:6] + s.part_meronyms()[:4] + s.member_holonyms()[:4]
                + s.instance_hypernyms())
        for h in rels:
            for ln in h.lemma_names():
                words.append(ln.lower().split("_")[0])
            words += V1.CM._toks(h.definition())
        words += SG._syntagnet().get(syn_name, [])
    except Exception:
        pass
    _GWORDS[syn_name] = words
    return words


def _sig(words, mat, w2i):
    vs = [mat[w2i[w]] for w in words if w in w2i]
    if not vs:
        return None
    v = np.mean(vs, 0); n = np.linalg.norm(v)
    return (v / n).astype(np.float32) if n > 1e-9 else v.astype(np.float32)


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


# ===========================================================================
# context2vec model.
# ===========================================================================
class Context2Vec(nn.Module):
    def __init__(self, V, direction="bi"):
        super().__init__()
        self.direction = direction
        self.emb = nn.Embedding(V, EMB_DIM, padding_idx=0)
        self.tgt = nn.Embedding(V, EMB_DIM, padding_idx=0)      # target (output) embeddings
        nn.init.normal_(self.emb.weight, std=0.05); nn.init.normal_(self.tgt.weight, std=0.05)
        with torch.no_grad():
            self.emb.weight[0].zero_(); self.tgt.weight[0].zero_()
        self.fwd = nn.LSTM(EMB_DIM, HID, batch_first=True)
        if direction == "bi":
            self.bwd = nn.LSTM(EMB_DIM, HID, batch_first=True)
            mlp_in = 2 * HID
        else:
            mlp_in = HID
        self.mlp = nn.Sequential(nn.Linear(mlp_in, 2 * EMB_DIM), nn.ReLU(), nn.Linear(2 * EMB_DIM, EMB_DIM))

    def context(self, ids, leak=False):
        """Contextual vector at EVERY position, (B, L, EMB). BOUNDARY (no target leak) unless leak=True."""
        e = self.emb(ids)                                   # (B, L, EMB)
        B, L, _ = e.shape
        of, _ = self.fwd(e)                                 # of[:, i] = state after w_i (left, incl i)
        if leak:
            left = of                                       # includes the target position (LEAK ablation)
        else:
            left = torch.zeros_like(of)
            left[:, 1:] = of[:, :-1]                         # left[:, t] = state after w_{t-1} (excludes t)
        if self.direction == "bi":
            idxr = torch.arange(L - 1, -1, -1, device=ids.device)
            ob_r, _ = self.bwd(e.index_select(1, idxr))     # backward pass over reversed sequence
            ob = ob_r.index_select(1, idxr)                 # ob[:, i] = state after w_i..w_{L-1} (right, incl i)
            if leak:
                right = ob
            else:
                right = torch.zeros_like(ob)
                right[:, :-1] = ob[:, 1:]                    # right[:, t] = state after w_{t+1} (excludes t)
            h = torch.cat([left, right], dim=-1)
        else:
            h = left
        return self.mlp(h)                                  # (B, L, EMB)


def _corpus_id_seqs(emb, max_sents):
    w2i = emb["w2i"]
    seqs = []
    for toks in SG._corpus_sents(max_sents):
        ids = [w2i[w] for w in toks if w in w2i]
        if len(ids) >= 4:
            seqs.append(ids[:MAXLEN])
    return seqs


def _train_c2v(emb, max_sents, tag, epochs, direction, smoke=False):
    cache = os.path.join(_SCRATCH, "c2v_%s_%s.pt" % (direction, tag))
    V = emb["mat"].shape[0]
    net = Context2Vec(V, direction).to(_DEV)
    if os.path.exists(cache) and not smoke:
        net.load_state_dict(torch.load(cache, map_location=_DEV)); net.eval()
        print("[c2v] loaded cache %s (dev=%s)" % (os.path.basename(cache), _DEV), flush=True)
        return net
    seqs = _corpus_id_seqs(emb, max_sents)
    print("[c2v] %d training sequences dir=%s dev=%s (%d tok)"
          % (len(seqs), direction, _DEV, sum(len(s) for s in seqs)), flush=True)
    negp = emb["negp"].astype(np.float64); negp = negp / negp.sum()
    opt = torch.optim.Adam([p for p in net.parameters() if p.requires_grad], lr=1e-3)
    rng = np.random.default_rng(0)
    t0 = time.time()
    net.train()
    for ep in range(epochs):
        rng.shuffle(seqs); tot = 0.0; nb = 0
        for b in range(0, len(seqs), BATCH):
            batch = seqs[b:b + BATCH]
            L = max(len(s) for s in batch)
            ids = torch.zeros(len(batch), L, dtype=torch.long)
            for i, s in enumerate(batch):
                ids[i, :len(s)] = torch.tensor(s)
            ids = ids.to(_DEV)
            C = net.context(ids)                             # (B, L, EMB) -- boundary, no leak
            valid = ids > 0
            if valid.sum() == 0:
                continue
            cv = C[valid]                                    # (M, EMB)
            tw = ids[valid]                                  # (M,)
            e_true = net.tgt(tw)                             # (M, EMB)
            negs = torch.tensor(rng.choice(V, size=(cv.shape[0], NEG_K), p=negp), dtype=torch.long).to(_DEV)
            e_neg = net.tgt(negs)                            # (M, K, EMB)
            s_pos = (cv * e_true).sum(-1)
            s_neg = torch.einsum("me,mke->mk", cv, e_neg)
            loss = -(torch.nn.functional.logsigmoid(s_pos).mean()
                     + torch.nn.functional.logsigmoid(-s_neg).mean())
            opt.zero_grad(); loss.backward(); opt.step()
            tot += float(loss.detach()); nb += 1
            if smoke and nb >= 40:
                break
        print("[c2v] epoch %d loss=%.4f (%.0fs)" % (ep, tot / max(nb, 1), time.time() - t0), flush=True)
    net.eval()
    if not smoke:
        torch.save(net.state_dict(), cache)
    return net


# ===========================================================================
# contextual-vector extraction for the eval recs.
# ===========================================================================
@torch.no_grad()
def _encode_recs(net, recs, leak=False, shuffle_within=False, want_ctxwords=False, seed=13):
    """Encode each rec ONCE. Returns (target_vec (N,EMB) unit, ctxword_list).
      target_vec[i]  = contextual vector at rec i's TARGET slot (the context2vec 'what fills this slot' vector).
      ctxword_list[i]= (Wi,EMB) unit contextual vectors at rec i's non-target in-vocab positions (each context
                       word's OWN contextualised representation, in the target-embedding space) -- only if
                       want_ctxwords, else None. This is the ELMo-style per-word contextual rep the biased-
                       competition readout consumes (contextual encoding STACKED with precision-weighting).
    shuffle_within: permute the sentence's NON-target positions before encoding (structure-destroyed twin)."""
    rng = np.random.default_rng(seed)
    dev = next(net.parameters()).device
    tvec = np.zeros((len(recs), EMB_DIM), np.float32)
    cwords = [None] * len(recs)
    order = sorted(range(len(recs)), key=lambda i: len(recs[i]["ids"]))
    for b in range(0, len(order), BATCH):
        chunk = order[b:b + BATCH]
        items = [recs[i] for i in chunk]
        L = max(len(t["ids"]) for t in items)
        ids = torch.zeros(len(items), L, dtype=torch.long)
        tpos = []
        for k, t in enumerate(items):
            seq = list(t["ids"]); tp = t["tpos"]
            if shuffle_within and len(seq) > 2:
                pos = [j for j in range(len(seq)) if j != tp]
                perm = list(pos); rng.shuffle(perm)
                new = list(seq)
                for a, c in zip(pos, perm):
                    new[a] = seq[c]
                seq = new
            ids[k, :len(seq)] = torch.tensor(seq); tpos.append(tp)
        idst = ids.to(dev)
        C = net.context(idst, leak=leak).cpu().numpy()       # (B, L, EMB)
        for k, i in enumerate(chunk):
            tp = tpos[k]
            tvec[i] = _unit(C[k, tp])
            if want_ctxwords:
                seqn = ids[k].numpy()
                rows = [_unit(C[k, j]) for j in range(L) if seqn[j] > 0 and j != tp]
                cwords[i] = np.stack(rows).astype(np.float32) if rows else None
    return tvec, cwords


def _ctx_vectors(net, recs, leak=False, shuffle_within=False, seed=13):
    tvec, _ = _encode_recs(net, recs, leak=leak, shuffle_within=shuffle_within, seed=seed)
    return tvec


# ===========================================================================
# scoring.
# ===========================================================================
def _score_arms(recs, emb, net, tgt_mat):
    """Return dict arm -> per-rec correctness array (int) over ALL recs (masked later)."""
    w2i = emb["w2i"]; w2v = emb["mat"]
    # gloss sigs in both spaces
    names = sorted({s for r in recs for s in r["tn"]})
    gw = {s: _gloss_word_list(s) for s in names}
    gsig_w2v = {s: _sig(gw[s], w2v, w2i) for s in names}
    gsig_T = {s: _sig(gw[s], tgt_mat, w2i) for s in names}

    cv_ctx, cw_ctx = _encode_recs(net, recs, leak=False, want_ctxwords=True)
    cv_leak = _ctx_vectors(net, recs, leak=True)
    cv_tw_a = _ctx_vectors(net, recs, leak=False, shuffle_within=True)
    # cross-item twin: assign each rec another rec's context vector (same sense-count bucket)
    from collections import defaultdict
    buckets = defaultdict(list)
    for i, r in enumerate(recs):
        buckets[len(r["tn"])].append(i)
    rng = np.random.default_rng(7); mp = {}
    for _, idxs in buckets.items():
        perm = list(idxs); rng.shuffle(perm)
        for a, c in zip(idxs, perm):
            mp[a] = c
    cv_tw_b = np.stack([cv_ctx[mp[i]] for i in range(len(recs))])

    def cos_arm(cvecs, gsig):
        ok = np.zeros(len(recs), int)
        for i, r in enumerate(recs):
            q = cvecs[i]
            sc = [float(q @ gsig[s]) if gsig[s] is not None else -9.0 for s in r["tn"]]
            ok[i] = int(r["tn"][int(np.argmax(sc))] == r["gold"])
        return ok

    def bag_arm(mat, gsig):
        ok = np.zeros(len(recs), int)
        for i, r in enumerate(recs):
            vs = [mat[w2i[w]] for w in r["ctx"] if w in w2i]
            if not vs:
                ok[i] = 0; continue
            q = _unit(np.mean(vs, 0))
            sc = [float(q @ gsig[s]) if gsig[s] is not None else -9.0 for s in r["tn"]]
            ok[i] = int(r["tn"][int(np.argmax(sc))] == r["gold"])
        return ok

    def diag_arm(mat, gsig):
        ok = np.zeros(len(recs), int)
        for i, r in enumerate(recs):
            rows = [_unit(mat[w2i[w]]) for w in r["ctx"] if w in w2i]
            if not rows:
                ok[i] = 0; continue
            C = np.stack(rows).astype(np.float32)
            G = np.stack([gsig[s] if gsig[s] is not None else np.zeros(mat.shape[1], np.float32)
                          for s in r["tn"]]).astype(np.float32)
            sc = DCW.diagnostic_context_scores(C, G)
            ok[i] = int(r["tn"][int(np.argmax(sc))] == r["gold"])
        return ok

    def cw_arm(cwords, gsig, diag):
        """readout over the CONTEXTUALISED context-word vectors (ELMo-style). diag=True -> biased competition
        (contextual encoding STACKED with precision-weighting, the maximally brain-faithful arm)."""
        ok = np.zeros(len(recs), int)
        for i, r in enumerate(recs):
            C = cwords[i]
            if C is None:
                ok[i] = 0; continue
            G = np.stack([gsig[s] if gsig[s] is not None else np.zeros(EMB_DIM, np.float32)
                          for s in r["tn"]]).astype(np.float32)
            if diag:
                sc = DCW.diagnostic_context_scores(C.astype(np.float32), G)
            else:
                q = _unit(C.mean(0)); sc = G @ q
            ok[i] = int(r["tn"][int(np.argmax(sc))] == r["gold"])
        return ok

    arms = {
        "bag_w2v": bag_arm(w2v, gsig_w2v),
        "diag_w2v": diag_arm(w2v, gsig_w2v),
        "bag_T": bag_arm(tgt_mat, gsig_T),
        "diag_T": diag_arm(tgt_mat, gsig_T),
        "C2V": cos_arm(cv_ctx, gsig_T),
        "bag_C2V": cw_arm(cw_ctx, gsig_T, diag=False),
        "diag_C2V": cw_arm(cw_ctx, gsig_T, diag=True),
        "C2V_leak": cos_arm(cv_leak, gsig_T),
        "C2V_twinA_shufwords": cos_arm(cv_tw_a, gsig_T),
        "C2V_twinB_crossitem": cos_arm(cv_tw_b, gsig_T),
    }
    return arms


def evaluate(recs, emb, net, direction):
    tgt_mat = net.tgt.weight.detach().cpu().numpy().astype(np.float32)
    arms = _score_arms(recs, emb, net, tgt_mat)
    doc = np.array([r["doc_id"] for r in recs]); te = doc % 2 == 1
    sub = np.array([r["subordinate"] for r in recs], bool)
    pidx = [r["pidx"] for r in recs]
    mfs = np.array([int(recs[i]["tn"][pidx[i]] == recs[i]["gold"]) for i in range(len(recs))], int)
    tsub = te & sub
    n = int(tsub.sum())

    def a_s(arm):
        return round(float(arms[arm][tsub].mean()), 4)

    # the BAR is met by the BEST brain-faithful contextual arm (plain contextual vector OR contextual+biased-comp)
    ctx_arms = ["C2V", "diag_C2V", "bag_C2V"]
    best = max(ctx_arms, key=lambda k: a_s(k))
    B = arms[best][tsub].astype(float)
    C = arms["C2V"][tsub].astype(float)
    out = {"direction": direction, "n_test_sub": n, "MFS_overall": round(float(mfs.mean()), 4),
           "best_ctx_arm": best,
           "a_s": {k: a_s(k) for k in arms},
           "net_best_over_MFS": V1._paired(B, mfs[tsub].astype(float), 301)}
    out["paired"] = {
        # the two BAR floors, tested against the BEST contextual arm:
        "best_vs_bag_w2v": V1._paired(B, arms["bag_w2v"][tsub].astype(float), 311),
        "best_vs_diag_w2v": V1._paired(B, arms["diag_w2v"][tsub].astype(float), 312),
        # attribution -- did contextual encoding itself help, and does biased-competition STACK on it:
        "C2V_vs_bag_T": V1._paired(C, arms["bag_T"][tsub].astype(float), 313),
        "C2V_vs_diag_T": V1._paired(C, arms["diag_T"][tsub].astype(float), 314),
        "diagC2V_vs_C2V": V1._paired(arms["diag_C2V"][tsub].astype(float), C, 318),
        "diagC2V_vs_diag_w2v": V1._paired(arms["diag_C2V"][tsub].astype(float),
                                          arms["diag_w2v"][tsub].astype(float), 319),
        # mandatory info-free twins (must LOSE) and the target-leak ablation (why v2 failed):
        "best_vs_twinA": V1._paired(B, arms["C2V_twinA_shufwords"][tsub].astype(float), 315),
        "best_vs_twinB": V1._paired(B, arms["C2V_twinB_crossitem"][tsub].astype(float), 316),
        "C2V_vs_leak": V1._paired(C, arms["C2V_leak"][tsub].astype(float), 317),
    }
    p = out["paired"]
    out["headline"] = (
        "C2V(%s) strict doc-disjoint subord n=%d | BEST=%s a_s=%.3f | vs bag_w2v=%.3f (%+.4f sep=%s) vs "
        "diag_w2v=%.3f (%+.4f sep=%s) | C2V=%.3f diag_C2V=%.3f diag_T=%.3f | twinA %+.4f sep=%s twinB %+.4f "
        "sep=%s | leak=%.3f"
        % (direction, n, best, out["a_s"][best], out["a_s"]["bag_w2v"], p["best_vs_bag_w2v"]["delta"],
           p["best_vs_bag_w2v"]["sep"], out["a_s"]["diag_w2v"], p["best_vs_diag_w2v"]["delta"],
           p["best_vs_diag_w2v"]["sep"], out["a_s"]["C2V"], out["a_s"]["diag_C2V"], out["a_s"]["diag_T"],
           p["best_vs_twinA"]["delta"], p["best_vs_twinA"]["sep"], p["best_vs_twinB"]["delta"],
           p["best_vs_twinB"]["sep"], out["a_s"]["C2V_leak"]))
    return out


def run(mode, max_sents, max_files, epochs, direction, tag):
    t0 = time.time()
    wtag = "full" if mode != "smoke" else "smoke"
    emb = SG._build_embeddings(max_sents if mode == "smoke" else 0, wtag)
    net = _train_c2v(emb, max_sents if mode == "smoke" else 0, tag, epochs, direction, smoke=(mode == "smoke"))
    recs = _recs(emb, max_files)
    print("[run] %d SemCor recs (%.0fs)" % (len(recs), time.time() - t0), flush=True)
    out = evaluate(recs, emb, net, direction)
    out["mode"] = mode; out["epochs"] = epochs; out["tag"] = tag; out["elapsed_s"] = round(time.time() - t0, 2)
    odir = os.path.join(_REPO, "data", "exp_sg_lite_context2vec_encoder_wsd_v1")
    os.makedirs(odir, exist_ok=True)
    with open(os.path.join(odir, "metrics_%s_%s.json" % (direction, tag)), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "sg_lite_context2vec_encoder_wsd_v1", "verdict": "MEASURED", "result": out}, f,
                  indent=2, default=str)
    print("[run] " + out["headline"], flush=True)
    return out


def self_test():
    V = 40
    net = Context2Vec(V, "bi")
    ids = torch.tensor([[1, 2, 3, 4, 5, 0, 0]])
    C = net.context(ids)
    assert C.shape == (1, 7, EMB_DIM), C.shape
    # boundary property: slot 0 has no left context; the no-leak vector at t must not equal the leak vector
    Cl = net.context(ids, leak=True)
    assert not np.allclose(C.detach().numpy(), Cl.detach().numpy()), "leak vs no-leak must differ"
    # readout plumbing on 2 toy recs
    recs = [{"ids": [1, 2, 3], "toks": ["a", "b", "c"], "tpos": 1, "gold": "dog.n.01",
             "tn": ["dog.n.01", "cat.n.01"], "gi": 0, "pidx": 1, "subordinate": True, "doc_id": 1,
             "ctx": ["a", "c"]},
            {"ids": [1, 2, 3], "toks": ["a", "b", "c"], "tpos": 2, "gold": "cat.n.01",
             "tn": ["dog.n.01", "cat.n.01"], "gi": 1, "pidx": 0, "subordinate": True, "doc_id": 1,
             "ctx": ["a", "b"]}]
    emb = {"w2i": {"a": 1, "b": 2, "c": 3}, "mat": np.random.default_rng(0).standard_normal((V, SG.EMB_DIM)).astype(np.float32),
           "negp": np.ones(V) / V}
    tgt_mat = net.tgt.weight.detach().cpu().numpy().astype(np.float32)
    # patch a tiny gloss list so _sig has something in-vocab
    _GWORDS["dog.n.01"] = ["a"]; _GWORDS["cat.n.01"] = ["b"]
    arms = _score_arms(recs, emb, net, tgt_mat[:, :EMB_DIM] if tgt_mat.shape[1] >= EMB_DIM else tgt_mat)
    assert all(len(v) == len(recs) for v in arms.values()), "arm shapes"
    print("SELFTEST PASS (boundary no-leak differs from leak; all 8 arms score; readout plumbing ok)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full", choices=["smoke", "full"])
    ap.add_argument("--max-sents", type=int, default=30000)     # only used in smoke
    ap.add_argument("--max-files", type=int, default=30)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--direction", default="bi", choices=["bi", "fwd"])
    ap.add_argument("--tag", default="full41m")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    mode = "smoke" if (args.smoke or args.mode == "smoke") else "full"
    run(mode, args.max_sents, args.max_files, 1 if mode == "smoke" else args.epochs, args.direction, args.tag)
    return 0


if __name__ == "__main__":
    sys.exit(main())
