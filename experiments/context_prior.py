"""context_prior -- the CONTEXT cue (reordered access) as a first-class, deployable, RELIABILITY-GATED asset.

The brain disambiguates verb sense partly by CONTEXT (the prior discourse primes the sense; Duffy/Morris/Rayner
reordered access). Measured: a learned P(coarse_frame | context content-words) BEATS most-frequent-sense on the
MOTION confusion (5-fold pooled p=0.014) AND -- once PRECISION-WEIGHTED -- on the BROAD frame-alternating multiclass
task (5-fold pooled override precision 0.558, McNemar p=0.003). The precision weighting is a PER-VERB RELIABILITY
GATE (Friston): context is trusted ONLY for verbs where it demonstrably beats the frequency prior; elsewhere the
reader stays at MFS. Un-gated context HURTS the broad task (over-fires on taxonomy/idiom/world-knowledge senses);
gated, it helps. This module builds the model offline (SemCor) and exposes gated context scores for the
disambiguator's `context_scores` hook. Glass-box, no LLM at inference. ASCII.
"""
from __future__ import annotations
import math
import os
import pickle
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Sequence

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

ASSET = os.path.join(REPO, "data", "context_prior_v1", "model.pkl")
ALPHA = 0.1
DEFAULT_W = 3.0
MIN_CTX = 3            # reordered access needs actual DISCOURSE -- a single content word is not reliable context
_M = None


def _load():
    global _M
    if _M is None and os.path.exists(ASSET):
        with open(ASSET, "rb") as f:
            _M = pickle.load(f)
    return _M


def _scores(model, cands: Sequence[str], ctx: Sequence[str]) -> Dict[str, float]:
    """Diagnostic-word-WEIGHTED context log-likelihood per candidate frame, z-scored across candidates."""
    wf, ftot, V, diag = model["wf"], model["ftot"], model["V"], model["diag"]
    raw = []
    for f in cands:
        tot = ftot.get(f, 0.0); s = 0.0
        for w in ctx:
            c = wf.get(f, {}).get(w, 0.0)
            s += diag.get(w, 0.0) * math.log((c + ALPHA) / (tot + ALPHA * V))
        raw.append(s)
    raw = np.asarray(raw, float)
    if len(raw) < 2 or raw.std() < 1e-9:
        return {c: 0.0 for c in cands}
    z = (raw - raw.mean()) / (raw.std() + 1e-9)
    return {c: float(z[i]) for i, c in enumerate(cands)}


def gated_context_scores(lemma: str, cands: Sequence[str], ctx: Sequence[str]) -> Dict[str, float]:
    """Context scores for the disambiguator's `context_scores` hook -- ZERO (no effect) unless (a) the asset is
    present and (b) this verb is context-RELIABLE (learned on build data). This is the precision gate that makes
    the context cue safe on the broad population while keeping the motion/distinctive-context wins."""
    m = _load()
    if m is None or len(ctx) < MIN_CTX or not m["reliable"].get(lemma.lower(), False):
        return {c: 0.0 for c in cands}
    return _scores(m, cands, ctx)


def is_context_reliable(lemma: str) -> bool:
    m = _load()
    return bool(m and m["reliable"].get(lemma.lower(), False))


# ---------------------------------------------------------------------------
# Offline build from the cached SemCor instances (deployment model: uses all available sense-tagged data).
# ---------------------------------------------------------------------------
def build(cache=None, w_ctx=DEFAULT_W, min_n=5):
    from experiments.exp_frame_sense_semcor_v1 import mfs_of
    cache = cache or os.path.join(REPO, "data", "exp_frame_sense_semcor_v1", "instances_v6.pkl")
    insts, _ = pickle.load(open(cache, "rb"))
    # P(word|frame) + diagnostic weight (1 - normalized entropy of P(frame|word))
    wf = defaultdict(lambda: defaultdict(float)); ftot = defaultdict(float); vocab = set()
    wframe = defaultdict(lambda: defaultdict(float))
    cpri = defaultdict(lambda: defaultdict(float))
    for it in insts:
        f = it["gold_frame"]; cpri[it["lemma"]][f] += 1.0
        for w in it.get("ctx", []):
            wf[f][w] += 1.0; ftot[f] += 1.0; vocab.add(w); wframe[w][f] += 1.0
    diag = {}
    for w, fr in wframe.items():
        tot = sum(fr.values())
        if tot < 3:
            diag[w] = 0.0; continue
        ps = np.array([v / tot for v in fr.values()])
        h = -(ps * np.log(ps + 1e-12)).sum() / math.log(max(2, len(fr)))
        diag[w] = float(1.0 - h)
    model = {"wf": {f: dict(d) for f, d in wf.items()}, "ftot": dict(ftot), "V": max(1, len(vocab)), "diag": diag}
    cpri = {lm: dict(d) for lm, d in cpri.items()}
    # per-verb reliability: does context beat MFS on the data (>= min_n instances)?
    per = defaultdict(lambda: [0, 0, 0])
    for it in insts:
        cands = it["cands"]; pa = {c: cpri.get(it["lemma"], {}).get(c, 0.0) for c in cands}
        cz = _scores(model, cands, it.get("ctx", []))
        cp = max(cands, key=lambda c: pa[c] + w_ctx * cz[c]); mp = mfs_of(cpri, it["lemma"], cands)
        per[it["lemma"]][0] += 1
        per[it["lemma"]][1] += int(cp == it["gold_frame"]); per[it["lemma"]][2] += int(mp == it["gold_frame"])
    reliable = {lm: (v[0] >= min_n and v[1] > v[2]) for lm, v in per.items()}
    model["reliable"] = reliable
    os.makedirs(os.path.dirname(ASSET), exist_ok=True)
    tmp = ASSET + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(model, f)
    os.replace(tmp, ASSET)
    nrel = sum(reliable.values())
    print(f"[context_prior] built {ASSET}: {len(model['wf'])} frames, {model['V']} vocab, "
          f"{len(reliable)} verbs, {nrel} context-reliable.")
    return model


def _self_test():
    m = _load()
    if m is None:
        print("[context_prior] no asset -- run build() first"); return
    print("reliable verbs (sample):", [lm for lm in ("go", "leave", "come", "pass", "see", "make") if m["reliable"].get(lm)])
    print("gated_context_scores('go', ['motion','change'], ['bad','turn']):",
          {k: round(v, 2) for k, v in gated_context_scores("go", ["motion", "change"], ["bad", "turn"]).items()})


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--build", action="store_true"); ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.build:
        build()
    else:
        _self_test()
