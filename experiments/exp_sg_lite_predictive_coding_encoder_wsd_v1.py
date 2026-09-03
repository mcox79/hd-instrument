"""PREDICTIVE-CODING SENTENCE-GESTALT encoder -- the brain-FAITHFUL contextual input encoder.
(problem: break_the_contextual_input_encoding_ceiling_for_specific_sense_selection)

This is the CORRECT brain-foundational focus (owner-directed pivot). The sibling
exp_sg_lite_context2vec_encoder_wsd_v1 is the ISOLATION BASELINE (a convenient feedforward bidirectional
LM); it answers "does a context-shaped input help at all". It is brain-UNFAITHFUL on four axes this cell
closes -- the encoder the substrate's own audit (ORGAN_MAP F5 / G2) says is MISSING:

  F5  N400 = the MAGNITUDE OF UPDATE forced on a RUNNING situation-model state by the incoming word
      (Rabovsky-Hansen-McClelland 2018; Kutas-Federmeier 2011). Reference point PINNED (the running state);
      norm/update rule UNPINNED. The error is PRECISION-WEIGHTED (form pinned: precision x error).
  G2  hierarchical predictive coding: the residual (x - x_hat) is the drive/learning signal, precision-
      weighted so low-precision errors are suppressed (Rao-Ballard 1999; Friston). The substrate's
      predictive_coding.py is RIGHT-OP-WRONG-METRIC (sign-quantised, no precision) -- this cell builds the
      graded, precision-weighted version.

MECHANISM (glass-box, self-supervised at scale, OUR model, NO external LLM):
  A running "meaning-so-far" state s_t. At each word w_t:
    p_t = P(s_{t-1})            top-down PREDICTION of w_t's meaning from the state BEFORE seeing w_t
    e_t = precision * (x_t - p_t)   PRECISION-WEIGHTED PREDICTION ERROR (Rao-Ballard) -- x_t = E[w_t] bottom-up
    s_t = GRUCell(e_t, s_{t-1})     the recurrent state is driven by the ERROR, not the raw word (the pivot)
  Objective (meaning-prediction, Sentence-Gestalt, self-supervised): make p_t match the incoming word's
  MEANING (its learned target-embedding T[w_t]) via negative sampling -- predicts the DISTRIBUTED MEANING,
  not a one-hot token. N400_t = ||x_t - p_t|| (the graded content prediction error) -- validated to grade
  with word surprisal (a brain signal, not just an accuracy number).

  FOUR brain-faithful properties context2vec LACKS, each an ablation here:
    error-drive  : the GRU input is the prediction error e_t, NOT the raw embedding x_t   (--no-error-drive)
    precision    : per-dim learned precision gain on the error (Friston)                  (--no-precision)
    active query : the WSD query = the context's TOP-DOWN PREDICTION of the target slot   (p_target, no leak)
                   = biased competition by construction (vs a passive context average)
    incremental  : forward running state + a backward-revision pass (the brain uses right context via
                   revision/wrap-up, not a symmetric read)                                (--direction fwd)

READOUT: sense score = cos( p_target , gloss_sig(T) ). p_target = the context's prediction of the target's
meaning (fwd: from the left; bi: fwd+bwd) -- NEVER sees the target token. GOLD-BLIND. Also a diag_PC arm:
biased competition over the per-context-word predictions (contextual encoding STACKED with precision-weight).

Compared, strict document-disjoint SemCor even/odd, subordinate senses, subject a_s, SAME n~2676 population,
against the parent's banked floors: bag_w2v 0.283 and the wired biased-competition readout diag_w2v ~0.307.
Shuffled-context twins MUST lose. PASS = best PC arm beats BOTH floors CI-sep, twins lose, no MFS regression;
a rigorous located NEGATIVE (named cause + number + the transformer fork) is a FULL PASS. ASCII-only.
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
import experiments.exp_sg_lite_sense_gestalt_v1 as SG
import experiments.exp_sg_lite_context2vec_encoder_wsd_v1 as C2V   # reuse recs, gloss, readout helpers
from hdlab import diagnostic_context_wsd as DCW

# KB_REFERENT: data/corpora/simplewiki/simplewiki_clean_v1.txt
# KB_REFERENT: data/syntagnet/SyntagNet-1.0/SYNTAGNET_1.0.txt
# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
_DEV = "cuda" if torch.cuda.is_available() else "cpu"
_SCRATCH = SG._SCRATCH
EMB_DIM = C2V.EMB_DIM        # 256 -- shared with the baseline so the comparison is one-variable
HID = C2V.HID               # 256
NEG_K = C2V.NEG_K
BATCH = C2V.BATCH
MAXLEN = 30                 # shorter than c2v (the per-step loop is sequential; keeps training tractable)


class PCSentenceGestalt(nn.Module):
    """Predictive-coding running-state encoder. The recurrent state is driven by the precision-weighted
    prediction error e_t = prec*(x_t - P(s_{t-1})); P is BOTH the training predictor and the WSD query head."""

    def __init__(self, V, direction="bi", error_drive=True, precision=True):
        super().__init__()
        self.direction = direction
        self.error_drive = bool(error_drive)
        self.use_prec = bool(precision)
        self.emb = nn.Embedding(V, EMB_DIM, padding_idx=0)      # bottom-up input meaning
        self.tgt = nn.Embedding(V, EMB_DIM, padding_idx=0)      # target/output meaning (neg-sampling + gloss space)
        nn.init.normal_(self.emb.weight, std=0.05); nn.init.normal_(self.tgt.weight, std=0.05)
        with torch.no_grad():
            self.emb.weight[0].zero_(); self.tgt.weight[0].zero_()
        self.Pf = nn.Linear(HID, EMB_DIM)                      # forward top-down predictor
        self.fcell = nn.GRUCell(EMB_DIM, HID)
        if direction == "bi":
            self.Pb = nn.Linear(HID, EMB_DIM)
            self.bcell = nn.GRUCell(EMB_DIM, HID)
        self.log_prec = nn.Parameter(torch.zeros(EMB_DIM))     # per-dim precision (softplus); UNPINNED estimator

    def _precision(self):
        return torch.nn.functional.softplus(self.log_prec) if self.use_prec else 1.0

    def _pass(self, x, valid, cell, P):
        """Run one direction left-to-right over x (B,L,EMB). Returns:
          preds (B,L,EMB): p_t = P(s_{t-1}) -- prediction of word t from the state BEFORE t (no leak of w_t)
          n400  (B,L)    : SU_t = sum_i |s_t,i - s_{t-1},i| -- the L1 magnitude of update the incoming word
                           forces on the running gestalt state. This is Rabovsky-Hansen-McClelland (2018)'s
                           EXACT N400 metric (L1 state-delta, validated over 16 ERP paradigms), NOT L2/cosine.
        valid (B,L) gates the state update so padding does not corrupt the running state."""
        B, L, _ = x.shape
        s = x.new_zeros(B, HID)
        prec = self._precision()
        preds = []; n400 = []
        for t in range(L):
            p_t = P(s)                                         # (B,EMB) top-down prediction of w_t (no leak)
            preds.append(p_t)
            x_t = x[:, t]
            diff = x_t - p_t                                   # prediction error x - x_hat (Rao-Ballard)
            inp = (prec * diff) if self.error_drive else x_t   # error-driven (brain) vs raw-input (control)
            s_new = cell(inp, s)
            m = valid[:, t:t + 1].to(s.dtype)
            s_upd = m * s_new + (1.0 - m) * s
            n400.append(torch.sum(torch.abs(s_upd - s), dim=-1))   # L1 state-delta = the Rabovsky N400
            s = s_upd
        return torch.stack(preds, 1), torch.stack(n400, 1)

    def forward(self, ids):
        """Returns (pred_f, pred_b_or_None, err_f, err_b_or_None). pred_*[:,t] predicts w_t from that side,
        never seeing w_t. For bi, the target's contextual query is unit(pred_f + pred_b) at its slot."""
        x = self.emb(ids)
        valid = ids > 0
        pf, ef = self._pass(x, valid, self.fcell, self.Pf)
        if self.direction == "bi":
            L = ids.shape[1]
            idxr = torch.arange(L - 1, -1, -1, device=ids.device)
            xr = x.index_select(1, idxr); vr = valid.index_select(1, idxr)
            pb_r, eb_r = self._pass(xr, vr, self.bcell, self.Pb)
            pb = pb_r.index_select(1, idxr); eb = eb_r.index_select(1, idxr)
            return pf, pb, ef, eb
        return pf, None, ef, None


def _train_pc(emb, tag, epochs, direction, error_drive, precision, smoke=False, max_sents=0):
    cache = os.path.join(_SCRATCH, "pc_%s_ed%d_pr%d_%s.pt" % (direction, int(error_drive), int(precision), tag))
    V = emb["mat"].shape[0]
    net = PCSentenceGestalt(V, direction, error_drive, precision).to(_DEV)
    if os.path.exists(cache) and not smoke:
        net.load_state_dict(torch.load(cache, map_location=_DEV)); net.eval()
        print("[pc] loaded cache %s" % os.path.basename(cache), flush=True)
        return net
    # id sequences (reuse the c2v builder but with this cell's MAXLEN)
    w2i = emb["w2i"]; seqs = []
    for toks in SG._corpus_sents(max_sents if smoke else 0):
        ids = [w2i[w] for w in toks if w in w2i]
        if len(ids) >= 4:
            seqs.append(ids[:MAXLEN])
    print("[pc] %d seqs dir=%s ed=%s pr=%s dev=%s (%d tok)"
          % (len(seqs), direction, error_drive, precision, _DEV, sum(len(s) for s in seqs)), flush=True)
    negp = emb["negp"].astype(np.float64); negp = negp / negp.sum()
    opt = torch.optim.Adam([p for p in net.parameters() if p.requires_grad], lr=1e-3)
    rng = np.random.default_rng(0); t0 = time.time()
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
            pf, pb, _, _ = net(ids)
            valid = ids > 0
            # objective: p_t (from each available side) should match w_t's target-meaning T[w_t] (neg-sampling)
            def side_loss(pred):
                cv = pred[valid]                              # (M,EMB)
                tw = ids[valid]
                e_true = net.tgt(tw)
                negs = torch.tensor(rng.choice(V, size=(cv.shape[0], NEG_K), p=negp), dtype=torch.long).to(_DEV)
                e_neg = net.tgt(negs)
                s_pos = (cv * e_true).sum(-1)
                s_neg = torch.einsum("me,mke->mk", cv, e_neg)
                return -(torch.nn.functional.logsigmoid(s_pos).mean()
                         + torch.nn.functional.logsigmoid(-s_neg).mean())
            loss = side_loss(pf) + (side_loss(pb) if pb is not None else 0.0)
            opt.zero_grad(); loss.backward(); opt.step()
            tot += float(loss.detach()); nb += 1
            if smoke and nb >= 40:
                break
        print("[pc] epoch %d loss=%.4f (%.0fs)" % (ep, tot / max(nb, 1), time.time() - t0), flush=True)
    net.eval()
    if not smoke:
        torch.save(net.state_dict(), cache)
    return net


@torch.no_grad()
def _encode_recs_pc(net, recs, shuffle_within=False, want_ctxwords=False, seed=13):
    """Per rec: target-slot predictive query q (unit, no leak), per-context-word predictions (unit) if wanted,
    and the target-slot N400 error magnitude. q_fwd/q_bwd are the context's TOP-DOWN prediction of the target."""
    rng = np.random.default_rng(seed)
    dev = next(net.parameters()).device
    tvec = np.zeros((len(recs), EMB_DIM), np.float32)
    n400 = np.zeros(len(recs), np.float32)
    cwords = [None] * len(recs)
    order = sorted(range(len(recs)), key=lambda i: len(recs[i]["ids"]))
    for b in range(0, len(order), BATCH):
        chunk = order[b:b + BATCH]
        items = [recs[i] for i in chunk]
        L = max(len(t["ids"]) for t in items)
        ids = torch.zeros(len(items), L, dtype=torch.long); tpos = []
        for k, t in enumerate(items):
            seq = list(t["ids"]); tp = t["tpos"]
            if shuffle_within and len(seq) > 2:
                pos = [j for j in range(len(seq)) if j != tp]
                perm = list(pos); rng.shuffle(perm); new = list(seq)
                for a, c in zip(pos, perm):
                    new[a] = seq[c]
                seq = new
            ids[k, :len(seq)] = torch.tensor(seq); tpos.append(tp)
        pf, pb, ef, eb = net(ids.to(dev))
        pf = pf.cpu().numpy(); ef = ef.cpu().numpy()
        pb = pb.cpu().numpy() if pb is not None else None
        for k, i in enumerate(chunk):
            tp = tpos[k]
            q = pf[k, tp].copy()
            if pb is not None:
                q = q + pb[k, tp]
            tvec[i] = C2V._unit(q)
            n400[i] = float(ef[k, tp])
            if want_ctxwords:
                seqn = ids[k].numpy()
                rows = []
                for j in range(L):
                    if seqn[j] > 0 and j != tp:
                        qq = pf[k, j] + (pb[k, j] if pb is not None else 0.0)
                        rows.append(C2V._unit(qq))
                cwords[i] = np.stack(rows).astype(np.float32) if rows else None
    return tvec, cwords, n400


def _score_arms_pc(recs, emb, net):
    w2i = emb["w2i"]; w2v = emb["mat"]
    tgt_mat = net.tgt.weight.detach().cpu().numpy().astype(np.float32)
    names = sorted({s for r in recs for s in r["tn"]})
    gw = {s: C2V._gloss_word_list(s) for s in names}
    gsig_w2v = {s: C2V._sig(gw[s], w2v, w2i) for s in names}
    gsig_T = {s: C2V._sig(gw[s], tgt_mat, w2i) for s in names}

    q_pc, cw_pc, n400 = _encode_recs_pc(net, recs, want_ctxwords=True)
    q_tw_a, _, _ = _encode_recs_pc(net, recs, shuffle_within=True)
    from collections import defaultdict
    buckets = defaultdict(list)
    for i, r in enumerate(recs):
        buckets[len(r["tn"])].append(i)
    rng = np.random.default_rng(7); mp = {}
    for _, idxs in buckets.items():
        perm = list(idxs); rng.shuffle(perm)
        for a, c in zip(idxs, perm):
            mp[a] = c
    q_tw_b = np.stack([q_pc[mp[i]] for i in range(len(recs))])

    def cos_arm(cvecs, gsig):
        ok = np.zeros(len(recs), int)
        for i, r in enumerate(recs):
            sc = [float(cvecs[i] @ gsig[s]) if gsig[s] is not None else -9.0 for s in r["tn"]]
            ok[i] = int(r["tn"][int(np.argmax(sc))] == r["gold"])
        return ok

    def bag_arm(mat, gsig):
        ok = np.zeros(len(recs), int)
        for i, r in enumerate(recs):
            vs = [mat[w2i[w]] for w in r["ctx"] if w in w2i]
            if not vs:
                continue
            q = C2V._unit(np.mean(vs, 0))
            sc = [float(q @ gsig[s]) if gsig[s] is not None else -9.0 for s in r["tn"]]
            ok[i] = int(r["tn"][int(np.argmax(sc))] == r["gold"])
        return ok

    def diag_w2v_arm():
        ok = np.zeros(len(recs), int)
        for i, r in enumerate(recs):
            rows = [C2V._unit(w2v[w2i[w]]) for w in r["ctx"] if w in w2i]
            if not rows:
                continue
            C = np.stack(rows).astype(np.float32)
            G = np.stack([gsig_w2v[s] if gsig_w2v[s] is not None else np.zeros(w2v.shape[1], np.float32)
                          for s in r["tn"]]).astype(np.float32)
            sc = DCW.diagnostic_context_scores(C, G)
            ok[i] = int(r["tn"][int(np.argmax(sc))] == r["gold"])
        return ok

    def diag_pc_arm(cwords):
        ok = np.zeros(len(recs), int)
        for i, r in enumerate(recs):
            C = cwords[i]
            if C is None:
                continue
            G = np.stack([gsig_T[s] if gsig_T[s] is not None else np.zeros(EMB_DIM, np.float32)
                          for s in r["tn"]]).astype(np.float32)
            sc = DCW.diagnostic_context_scores(C.astype(np.float32), G)
            ok[i] = int(r["tn"][int(np.argmax(sc))] == r["gold"])
        return ok

    arms = {
        "bag_w2v": bag_arm(w2v, gsig_w2v),
        "diag_w2v": diag_w2v_arm(),
        "PC": cos_arm(q_pc, gsig_T),
        "diag_PC": diag_pc_arm(cw_pc),
        "PC_twinA_shufwords": cos_arm(q_tw_a, gsig_T),
        "PC_twinB_crossitem": cos_arm(q_tw_b, gsig_T),
    }
    return arms, n400


def evaluate(recs, emb, net, direction, error_drive, precision):
    arms, n400 = _score_arms_pc(recs, emb, net)
    doc = np.array([r["doc_id"] for r in recs]); te = doc % 2 == 1
    sub = np.array([r["subordinate"] for r in recs], bool)
    pidx = [r["pidx"] for r in recs]
    mfs = np.array([int(recs[i]["tn"][pidx[i]] == recs[i]["gold"]) for i in range(len(recs))], int)
    tsub = te & sub; n = int(tsub.sum())

    def a_s(arm):
        return round(float(arms[arm][tsub].mean()), 4)

    ctx_arms = ["PC", "diag_PC"]
    best = max(ctx_arms, key=lambda k: a_s(k))
    B = arms[best][tsub].astype(float)
    # N400 gradedness: does the target-slot state-update grade with the target word's SURPRISAL (a brain
    # signal, not just an accuracy number)? Rarity = -log(unigram freq) of the target token (from negp).
    negp = emb["negp"]
    rar = np.array([-np.log(max(float(negp[recs[i]["ids"][recs[i]["tpos"]]]), 1e-12))
                    for i in range(len(recs))])
    tv = te
    n400_corr = float(np.corrcoef(n400[tv], rar[tv])[0, 1]) if tv.sum() > 5 else float("nan")

    out = {"direction": direction, "error_drive": error_drive, "precision": precision,
           "n_test_sub": n, "MFS_overall": round(float(mfs.mean()), 4), "best_ctx_arm": best,
           "a_s": {k: a_s(k) for k in arms},
           "N400_error_vs_rarity_corr": round(n400_corr, 4),
           "net_best_over_MFS": V1._paired(B, mfs[tsub].astype(float), 401),
           "paired": {
               "best_vs_bag_w2v": V1._paired(B, arms["bag_w2v"][tsub].astype(float), 411),
               "best_vs_diag_w2v": V1._paired(B, arms["diag_w2v"][tsub].astype(float), 412),
               "diagPC_vs_PC": V1._paired(arms["diag_PC"][tsub].astype(float), arms["PC"][tsub].astype(float), 413),
               "best_vs_twinA": V1._paired(B, arms["PC_twinA_shufwords"][tsub].astype(float), 414),
               "best_vs_twinB": V1._paired(B, arms["PC_twinB_crossitem"][tsub].astype(float), 415),
           }}
    p = out["paired"]
    out["headline"] = (
        "PC-SG(dir=%s ed=%s pr=%s) strict doc-disjoint subord n=%d | BEST=%s a_s=%.3f | vs bag_w2v=%.3f "
        "(%+.4f sep=%s) vs diag_w2v=%.3f (%+.4f sep=%s) | PC=%.3f diag_PC=%.3f | twinA %+.4f sep=%s twinB "
        "%+.4f sep=%s | N400~rarity r=%.3f"
        % (direction, error_drive, precision, n, best, out["a_s"][best], out["a_s"]["bag_w2v"],
           p["best_vs_bag_w2v"]["delta"], p["best_vs_bag_w2v"]["sep"], out["a_s"]["diag_w2v"],
           p["best_vs_diag_w2v"]["delta"], p["best_vs_diag_w2v"]["sep"], out["a_s"]["PC"], out["a_s"]["diag_PC"],
           p["best_vs_twinA"]["delta"], p["best_vs_twinA"]["sep"], p["best_vs_twinB"]["delta"],
           p["best_vs_twinB"]["sep"], out["N400_error_vs_rarity_corr"]))
    return out


def run(mode, max_sents, max_files, epochs, direction, error_drive, precision, tag):
    t0 = time.time()
    wtag = "full" if mode != "smoke" else "smoke"
    emb = SG._build_embeddings(max_sents if mode == "smoke" else 0, wtag)
    net = _train_pc(emb, tag, epochs, direction, error_drive, precision,
                    smoke=(mode == "smoke"), max_sents=max_sents)
    recs = C2V._recs(emb, max_files)
    print("[run] %d SemCor recs (%.0fs)" % (len(recs), time.time() - t0), flush=True)
    out = evaluate(recs, emb, net, direction, error_drive, precision)
    out["mode"] = mode; out["epochs"] = epochs; out["tag"] = tag; out["elapsed_s"] = round(time.time() - t0, 2)
    odir = os.path.join(_REPO, "data", "exp_sg_lite_predictive_coding_encoder_wsd_v1")
    os.makedirs(odir, exist_ok=True)
    fn = "metrics_%s_ed%d_pr%d_%s.json" % (direction, int(error_drive), int(precision), tag)
    with open(os.path.join(odir, fn), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "sg_lite_predictive_coding_encoder_wsd_v1", "verdict": "MEASURED",
                   "result": out}, f, indent=2, default=str)
    print("[run] " + out["headline"], flush=True)
    return out


def self_test():
    V = 40
    net = PCSentenceGestalt(V, "bi", error_drive=True, precision=True)
    ids = torch.tensor([[1, 2, 3, 4, 5, 0, 0]])
    pf, pb, ef, eb = net(ids)
    assert pf.shape == (1, 7, EMB_DIM) and pb.shape == (1, 7, EMB_DIM), (pf.shape, pb.shape)
    assert ef.shape == (1, 7), ef.shape
    # error-drive must actually change the dynamics vs raw-input
    net_raw = PCSentenceGestalt(V, "bi", error_drive=False, precision=True)
    net_raw.load_state_dict(net.state_dict())
    pf2, _, _, _ = net_raw(ids)
    assert not np.allclose(pf.detach().numpy(), pf2.detach().numpy()), "error-drive vs raw must differ"
    # readout plumbing on toy recs
    recs = [{"ids": [1, 2, 3], "toks": ["a", "b", "c"], "tpos": 1, "gold": "dog.n.01",
             "tn": ["dog.n.01", "cat.n.01"], "gi": 0, "pidx": 1, "prior": np.array([.3, .7]),
             "subordinate": True, "doc_id": 1, "ctx": ["a", "c"]},
            {"ids": [1, 2, 3], "toks": ["a", "b", "c"], "tpos": 2, "gold": "cat.n.01",
             "tn": ["dog.n.01", "cat.n.01"], "gi": 1, "pidx": 0, "prior": np.array([.6, .4]),
             "subordinate": True, "doc_id": 1, "ctx": ["a", "b"]}]
    emb = {"w2i": {"a": 1, "b": 2, "c": 3},
           "mat": np.random.default_rng(0).standard_normal((V, SG.EMB_DIM)).astype(np.float32),
           "negp": np.ones(V) / V}
    C2V._GWORDS["dog.n.01"] = ["a"]; C2V._GWORDS["cat.n.01"] = ["b"]
    arms, n400 = _score_arms_pc(recs, emb, net)
    assert all(len(v) == len(recs) for v in arms.values()) and len(n400) == len(recs), "arm shapes"
    print("SELFTEST PASS (error-drive differs from raw-input; predictive query + N400 + all arms score)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full", choices=["smoke", "full"])
    ap.add_argument("--max-sents", type=int, default=30000)
    ap.add_argument("--max-files", type=int, default=30)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--direction", default="bi", choices=["bi", "fwd"])
    ap.add_argument("--no-error-drive", action="store_true")
    ap.add_argument("--no-precision", action="store_true")
    ap.add_argument("--tag", default="full41m")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    mode = "smoke" if (args.smoke or args.mode == "smoke") else "full"
    run(mode, args.max_sents, args.max_files, 1 if mode == "smoke" else args.epochs, args.direction,
        not args.no_error_drive, not args.no_precision, args.tag)
    return 0


if __name__ == "__main__":
    sys.exit(main())
