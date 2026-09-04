"""exp_crf_glassbox_marginals_v1 -- resolve the CRF runtime-dependency story: a GLASS-BOX, pure-numpy linear-chain
CRF forward-backward marginal reader that reproduces sklearn_crfsuite.predict_marginals from an EXTRACTED WEIGHT
ASSET, with NO crfsuite (and no C extension) at inference.

WHY: the calibrated CRF tagger (exp_register_predicate_crf_tagger_v1) is a sklearn_crfsuite.CRF -- crfsuite is NOT a
tracked substrate dependency, and a pickled estimator is not glass-box. A linear-chain CRF, though, is just state
potentials + label-label transition potentials + forward-backward; ALL its learned weights are introspectable
(crf.state_features_ = {(attr,label): w}, crf.transition_features_ = {(prev,cur): w}). We extract them ONCE (offline,
crfsuite used only to BUILD the asset) into a plain json, then compute P(VERB|sentence) in pure numpy. This makes the
calibrated posterior a dependency-free static asset admissible to land in hdlab (the brief's named alternative to
tracking crfsuite as a runtime dep).

crfsuite attribute convention (verified on-disk): a feature dict entry with a STRING value v under key k becomes the
attribute "k:v" with feature value 1.0; a NUMERIC/BOOL value becomes the attribute "k" with that numeric value. The
per-token features are exactly exp_register_predicate_crf_tagger_v1.crf_token_feats.

VERIFY: max |P_glassbox(VERB) - P_crfsuite(VERB)| over all tokens of N UD-EWT test sentences (must be < 1e-4).

Glass-box, CPU, numpy only at inference. ASCII. own dir.
# KB_REFERENT: data/exp_register_predicate_crf_tagger_v1/crf_tagger.pkl
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, pickle, sys, time
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_register_predicate_crf_tagger_v1 as CRF

OUT_DIR = os.path.join(_REPO, "data/exp_crf_glassbox_marginals_v1")
ASSET = os.path.join(OUT_DIR, "crf_tagger_glassbox.json")
PKL = os.path.join(_REPO, "data/exp_register_predicate_crf_tagger_v1/crf_tagger.pkl")


def extract_asset(pkl_path=PKL, out=ASSET):
    """One-time offline extraction of the linear-chain CRF weights into a plain json (crfsuite used ONLY here)."""
    import sklearn_crfsuite  # noqa: F401  (only to unpickle)
    with open(pkl_path, "rb") as f:
        crf = pickle.load(f)
    labels = list(crf.classes_)
    state = {}
    for (attr, lab), w in crf.state_features_.items():
        state.setdefault(attr, {})[lab] = float(w)
    trans = {}
    for (a, b), w in crf.transition_features_.items():
        trans["%s|%s" % (a, b)] = float(w)
    asset = {"model": "linear_chain_crf_glassbox", "labels": labels, "state_features": state,
             "transition_features": trans}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="ascii") as f:
        json.dump(asset, f)
    return asset


class GlassBoxCRF:
    """Pure-numpy linear-chain CRF marginals from the extracted json asset. NO crfsuite/C-extension at inference."""
    def __init__(self, asset):
        self.labels = asset["labels"]
        self.Li = {l: i for i, l in enumerate(self.labels)}
        self.state = asset["state_features"]
        self.K = len(self.labels)
        T = np.zeros((self.K, self.K), np.float64)
        for k, w in asset["transition_features"].items():
            a, b = k.split("|", 1)
            if a in self.Li and b in self.Li:
                T[self.Li[a], self.Li[b]] = w
        self.T = T
        self._vi = self.Li.get("VERB")

    @classmethod
    def load(cls, path=ASSET):
        with open(path, encoding="ascii") as f:
            return cls(json.load(f))

    def _attrs(self, feat_dict):
        """crf_token_feats dict -> [(attr, value)] per the crfsuite convention."""
        out = []
        for k, v in feat_dict.items():
            if isinstance(v, str):
                out.append((k + ":" + v, 1.0))
            else:
                out.append((k, float(v)))
        return out

    def _emissions(self, toks):
        n = len(toks); E = np.zeros((n, self.K), np.float64)
        for i in range(n):
            for attr, val in self._attrs(CRF.crf_token_feats(list(toks), i)):
                row = self.state.get(attr)
                if row:
                    for lab, w in row.items():
                        E[i, self.Li[lab]] += w * val
        return E

    def marginals(self, toks):
        """P(label | sentence) via log-space forward-backward. Returns (n, K)."""
        E = self._emissions(toks); n = self.K and len(toks)
        if n == 0:
            return np.zeros((0, self.K))
        T = self.T
        alpha = np.empty((n, self.K)); beta = np.empty((n, self.K))
        alpha[0] = E[0]
        for i in range(1, n):
            # alpha[i,y] = E[i,y] + logsumexp_{y'} alpha[i-1,y'] + T[y',y]
            m = alpha[i - 1][:, None] + T            # (K prev, K cur)
            alpha[i] = E[i] + _logsumexp_axis0(m)
        beta[n - 1] = 0.0
        for i in range(n - 2, -1, -1):
            # beta[i,y] = logsumexp_{y'} T[y,y'] + E[i+1,y'] + beta[i+1,y']
            m = T + (E[i + 1] + beta[i + 1])[None, :]  # (K cur=y, K next=y')
            beta[i] = _logsumexp_axis1(m)
        logZ = _logsumexp(alpha[n - 1])
        logp = alpha + beta - logZ
        return np.exp(logp)

    def vpost(self, toks):
        M = self.marginals(toks)
        return M[:, self._vi] if (self._vi is not None and len(M)) else np.zeros(len(toks))

    def tag(self, toks):
        """Viterbi argmax tags (for parity with crfsuite.predict, though the reader only needs vpost)."""
        E = self._emissions(toks); n = len(toks)
        if n == 0:
            return []
        T = self.T; d = np.empty((n, self.K)); bp = np.zeros((n, self.K), int)
        d[0] = E[0]
        for i in range(1, n):
            m = d[i - 1][:, None] + T
            bp[i] = np.argmax(m, axis=0); d[i] = E[i] + m[bp[i], np.arange(self.K)]
        y = [int(np.argmax(d[-1]))]
        for i in range(n - 1, 0, -1):
            y.append(int(bp[i, y[-1]]))
        return [self.labels[k] for k in reversed(y)]


def _logsumexp(v):
    m = v.max(); return m + np.log(np.exp(v - m).sum())
def _logsumexp_axis0(M):
    m = M.max(axis=0); return m + np.log(np.exp(M - m).sum(axis=0))
def _logsumexp_axis1(M):
    m = M.max(axis=1); return m + np.log(np.exp(M - m[:, None]).sum(axis=1))


def verify(n_sents=120, rebuild=False):
    if rebuild or not os.path.exists(ASSET):
        print("[extract] building glass-box asset from crfsuite pkl (offline) ...", flush=True)
        extract_asset()
    gb = GlassBoxCRF.load()
    # reference: crfsuite marginals
    import sklearn_crfsuite  # noqa
    with open(PKL, "rb") as f:
        crf = pickle.load(f)
    ud = CRF.load_ud_tagged(os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu"), cap=n_sents)
    max_err = 0.0; n_tok = 0; tag_match = 0; tag_tot = 0
    for toks, _ in ud:
        if not toks:
            continue
        ref = crf.predict_marginals([CRF.sent_feats(toks)])[0]
        ref_v = np.array([m.get("VERB", 0.0) for m in ref])
        gb_v = gb.vpost(toks)
        max_err = max(max_err, float(np.max(np.abs(ref_v - gb_v))))
        n_tok += len(toks)
        # tag parity
        rt = crf.predict([CRF.sent_feats(toks)])[0]; gt = gb.tag(toks)
        tag_match += sum(int(a == b) for a, b in zip(rt, gt)); tag_tot += len(toks)
    res = {"n_sentences": len(ud), "n_tokens": n_tok, "max_abs_vpost_error": max_err,
           "viterbi_tag_agreement": round(tag_match / max(1, tag_tot), 6), "asset": ASSET,
           "asset_bytes": os.path.getsize(ASSET)}
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "crf_glassbox_marginals_v1", "results": res}, f, indent=2)
    print("[verify] n_tok=%d  max|P(VERB)_glassbox - P(VERB)_crfsuite| = %.2e  viterbi-tag-agreement=%.5f  asset=%dKB"
          % (n_tok, max_err, res["viterbi_tag_agreement"], res["asset_bytes"] // 1024), flush=True)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--n", type=int, default=120)
    args = ap.parse_args()
    t0 = time.time()
    res = verify(n_sents=(40 if args.self_test else args.n), rebuild=args.rebuild)
    if args.self_test:
        assert res["max_abs_vpost_error"] < 1e-4, "glass-box CRF diverges from crfsuite"
        print("[self-test] PASS (%.0fs)" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
