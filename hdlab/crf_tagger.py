"""hdlab/crf_tagger.py -- GLASS-BOX CALIBRATED POS POSTERIOR (dependency-free).

The landed deployable win of the owner-DONE `upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior`.
The reader's perceptron POS tagger reports a MAX-MARGIN score, not a calibrated probability -- over-sure, and
register-brittle on archaic prose (its verb-margin caps 19c dropped-verb recovery at ~0.58). The brain's lexical
category is a GRADED, CALIBRATED belief (Kuperberg-Jaeger 2016; the axis-1 fix). A likelihood-trained linear-chain
CRF (SAME features + SAME UD-EWT data as the perceptron, only the training OBJECTIVE differs -- Lafferty 2001)
gives a calibrated posterior P(VERB|sentence) that separates 19c dropped verbs at AUROC 0.94 (vs the max-margin
0.58) and recovers them at 0.806 (vs 0.582), MODERN 0.955, argmax verb-recall TIED.

DEPENDENCY-FREE: the CRF weights are trained OFFLINE (crfsuite, never at inference) and extracted into a plain
json asset; this organ recomputes the marginals in PURE NUMPY (log-space linear-chain forward-backward), reproducing
sklearn_crfsuite.predict_marginals to max|dP(VERB)|=7.3e-7 (Viterbi tags 100% identical) -- so NO crfsuite / NO
C-extension / NO LLM at runtime. Promoted VERBATIM from experiments/exp_crf_glassbox_marginals_v1.GlassBoxCRF +
experiments/exp_register_predicate_crf_tagger_v1.crf_token_feats.

Primary consumer: the calibrated category cue for hdlab.predicate_detector (swap `verb_margin` ->
`logit(GlassBoxCRF.vpost)`, SS4c/SS6 -- the register-robust axis-1 cue, dependency-free). The JOINT parse-decode
the parent brief named is a LOCATED NEGATIVE (the calibrated posterior already captures the separable signal;
structure adds +0.0017 AUROC) -- NOT landed. Glass-box, NO LLM.
"""
from __future__ import annotations

import json
import math
import os
from typing import List, Sequence

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ASSET = os.path.join(_REPO, "data", "frontend_assets", "pos_crf_glassbox_ud_ewt.json")


def crf_token_feats(toks: Sequence[str], i: int) -> dict:
    """Per-token feature dict (mirrors hdlab.pos_tagger.pos_features content; the CRF learns transitions itself).
    Verbatim from exp_register_predicate_crf_tagger_v1.crf_token_feats -- the SAME information as the perceptron,
    a different training objective."""
    w = toks[i]; wl = w.lower(); L = len(wl)
    f = {"bias": 1.0, "w": wl}
    for k in (1, 2, 3, 4):
        if L >= k:
            f["suf%d" % k] = wl[-k:]; f["pre%d" % k] = wl[:k]
    if w[:1].isupper():
        f["cap"] = True
    if any(c.isdigit() for c in w):
        f["hasdig"] = True
    if "-" in w:
        f["hyph"] = True
    f["pw"] = toks[i - 1].lower() if i > 0 else "<BOS>"
    f["nw"] = toks[i + 1].lower() if i + 1 < len(toks) else "<EOS>"
    return f


def _logsumexp(v):
    m = v.max(); return m + np.log(np.exp(v - m).sum())


def _logsumexp_axis0(M):
    m = M.max(axis=0); return m + np.log(np.exp(M - m).sum(axis=0))


def _logsumexp_axis1(M):
    m = M.max(axis=1); return m + np.log(np.exp(M - m[:, None]).sum(axis=1))


class GlassBoxCRF:
    """Pure-numpy linear-chain CRF marginals from the extracted json asset. NO crfsuite/C-extension at inference.
    Verbatim from experiments/exp_crf_glassbox_marginals_v1.GlassBoxCRF (only the feature-extractor reference is
    the local promoted crf_token_feats)."""

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
    def load(cls, path: str = DEFAULT_ASSET) -> "GlassBoxCRF":
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
            for attr, val in self._attrs(crf_token_feats(list(toks), i)):
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
            m = alpha[i - 1][:, None] + T
            alpha[i] = E[i] + _logsumexp_axis0(m)
        beta[n - 1] = 0.0
        for i in range(n - 2, -1, -1):
            m = T + (E[i + 1] + beta[i + 1])[None, :]
            beta[i] = _logsumexp_axis1(m)
        logZ = _logsumexp(alpha[n - 1])
        logp = alpha + beta - logZ
        return np.exp(logp)

    def vpost(self, toks: Sequence[str]):
        """P(VERB) per token (the calibrated category cue). Returns an (n,) numpy array."""
        M = self.marginals(toks)
        return M[:, self._vi] if (self._vi is not None and len(M)) else np.zeros(len(toks))

    def tag(self, toks: Sequence[str]) -> List[str]:
        """Viterbi argmax tags (parity with crfsuite.predict; the reader only needs vpost)."""
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


def vlogit(toks: Sequence[str], crf: "GlassBoxCRF" = None, eps: float = 1e-6):
    """logit(P(VERB)) per token -- the calibrated category CUE for predicate_detector (SS6 swap from verb_margin).
    Clamped to [eps, 1-eps] before the logit. Loads the default asset if `crf` is None."""
    if crf is None:
        crf = GlassBoxCRF.load()
    p = crf.vpost(toks)
    p = np.clip(p, eps, 1.0 - eps)
    return np.log(p / (1.0 - p))
