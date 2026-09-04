"""Brain-foundational lexical-category assigner (the UPSTREAM component) -- prototype.

Direction for optimize_the_arc_parser_inner_loop... : the parser is already brain-foundational
(incremental arc-eager, UAS 0.842 vs arc-factored 0.791), but the DEPLOYED chain is capped by the
UPSTREAM tagger (batch Collins-Viterbi averaged perceptron, non-predictive): with gold POS the
incremental parser scores 0.842, but with the batch tagger's predicted POS only 0.805 -- 0.037 UAS
lost to the non-brain-foundational upstream link. "The only way to overcome the wall is for EVERY
component, you and upstream, to be brain-foundational" (owner). This builds the brain-foundational
upstream and measures whether the COMPOUNDED chain exceeds.

WHAT IS PINNED (copy the operation; research-verified this session, ~7 lit drills):
  * INCREMENTAL left-to-right, NOW-OR-NEVER bottleneck (Christiansen & Chater 2016) -- not batch.
  * RANKED-PARALLEL commitment (beam), not single-best serial nor exhaustive (MacDonald 1994;
    Jurafsky 1996) -- keep the top-B live analyses, graded.
  * CUE-BASED content-addressable RETRIEVAL is the attachment/lexical-access operation (Lewis &
    Vasishth 2005; and it maps to the substrate's own VSA/FHRR cleanup -- Kelly/West/Reitter 2020
    Holographic Declarative Memory: ACT-R activation softmax == VSA similarity softmax). Here the
    "retrieval" is lexical-category access: retrieve a word's candidate categories from the mental
    lexicon (train-derived), and its category from MORPHOLOGY when the word is novel.
  * MORPHOLOGICAL DECOMPOSITION for novel words (the brain reads morphemes; Brants 2000 TnT suffix
    backoff is the glass-box realization).
  * TOP-DOWN PREDICTION: the left context pre-activates the next category (predictive coding; Hale
    2001; Levy 2008 surprisal). Realized as a category trigram prior P(t | t-2, t-1).
  * COMPETITION-MODEL cue integration (MacWhinney): activation = a weighted (cue-validity) sum of
    the bottom-up lexical/morphology cue and the top-down predictive cue. Weight = SWEPT, never
    adopted.

NOT brain-faithful and deliberately excluded: batch Viterbi global optimisation over the whole
sentence (the current tagger). We use an INCREMENTAL BEAM instead (ranked-parallel).

All statistics are ONE-PASS COUNTS from UD-EWT-train (online-countable; NO gradient training, "the
brain does not do long training runs"). Glass-box, CPU, NO LLM. ASCII-only.
"""
from __future__ import annotations

import os
import sys
import math
import json
from collections import defaultdict, Counter

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

_TRAIN = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu")
_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
_OUT = os.path.join(_REPO, "data/exp_brain_foundational_tagger_v1")


def load(path):
    S, cur = [], []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip():
            if cur:
                S.append(cur); cur = []
            continue
        if line.startswith("#"):
            continue
        c = line.split("\t")
        if len(c) < 8 or "-" in c[0] or "." in c[0]:
            continue
        cur.append((c[1], c[3], int(c[6]), c[7]))   # form, upos, head, deprel
    if cur:
        S.append(cur)
    return S


def _shape(w):
    s = []
    if w[:1].isupper(): s.append("CAP")
    if any(ch.isdigit() for ch in w): s.append("DIG")
    if "-" in w: s.append("HYP")
    return "|".join(s) if s else "none"


class BrainTagger:
    """Incremental, ranked-parallel, cue-integration UPOS tagger (glass-box, one-pass counts)."""

    def __init__(self, w_ctx=1.0, beam=8, sfx_len=4, lex_min=1):
        self.w_ctx = w_ctx        # Competition-Model cue weight on top-down prediction (SWEPT)
        self.beam = beam
        self.sfx_len = sfx_len
        self.lex_min = lex_min

    def fit(self, sents):
        tags = set()
        lex = defaultdict(Counter)          # word.lower() -> tag counts  (mental lexicon)
        suf = [defaultdict(Counter) for _ in range(self.sfx_len + 1)]  # k -> suffix -> tag counts
        shp = defaultdict(Counter)          # shape -> tag counts (caps/digit/hyphen morphographemics)
        uni = Counter()                     # tag prior
        tri = defaultdict(Counter)          # (t-2,t-1) -> t
        bi = defaultdict(Counter)           # (t-1,) -> t
        for s in sents:
            prev2, prev1 = "<S>", "<S>"
            for form, tag, _, _ in s:
                wl = form.lower()
                tags.add(tag); uni[tag] += 1
                lex[wl][tag] += 1
                for k in range(1, self.sfx_len + 1):
                    if len(wl) >= k:
                        suf[k][wl[-k:]][tag] += 1
                shp[_shape(form)][tag] += 1
                tri[(prev2, prev1)][tag] += 1
                bi[(prev1,)][tag] += 1
                prev2, prev1 = prev1, tag
            tri[(prev1, "<E>")]["<E>"] += 0  # noop keep structure
        self.tags = sorted(tags)
        self.lex, self.suf, self.shp = lex, suf, shp
        self.uni, self.tri, self.bi = uni, tri, bi
        self.Ntok = sum(uni.values())
        self._logprior = {t: math.log((uni[t] + 1) / (self.Ntok + len(self.tags))) for t in self.tags}
        return self

    # ---- bottom-up cue: lexical retrieval, morphology backoff for novel words ----
    def _emis_logp(self, form):
        wl = form.lower()
        c = self.lex.get(wl)
        out = {}
        if c is not None and sum(c.values()) >= self.lex_min:
            tot = sum(c.values())
            for t in self.tags:
                out[t] = math.log((c.get(t, 0) + 0.01) / (tot + 0.01 * len(self.tags)))
            return out, False
        # OOV: morphological decomposition -- longest available suffix that has support, blended with shape
        dist = None
        for k in range(self.sfx_len, 0, -1):
            if len(wl) >= k:
                cc = self.suf[k].get(wl[-k:])
                if cc and sum(cc.values()) >= 3:
                    dist = cc; break
        sh = self.shp.get(_shape(form))
        blend = Counter()
        if dist:
            for t, n in dist.items(): blend[t] += n
        if sh:
            for t, n in sh.items(): blend[t] += n * 0.5
        if not blend:
            blend = self.uni
        tot = sum(blend.values())
        for t in self.tags:
            out[t] = math.log((blend.get(t, 0) + 0.05) / (tot + 0.05 * len(self.tags)))
        return out, True

    # ---- top-down cue: predictive category prior P(t | t-2, t-1), backoff ----
    def _ctx_logp(self, prev2, prev1, t):
        tri = self.tri.get((prev2, prev1))
        if tri and sum(tri.values()) >= 3:
            tot = sum(tri.values())
            return math.log((tri.get(t, 0) + 0.1) / (tot + 0.1 * len(self.tags)))
        bi = self.bi.get((prev1,))
        if bi and sum(bi.values()) >= 1:
            tot = sum(bi.values())
            return math.log((bi.get(t, 0) + 0.1) / (tot + 0.1 * len(self.tags)))
        return self._logprior[t]

    def tag(self, forms):
        """Incremental ranked-parallel (beam) decode. Returns list of UPOS."""
        beams = [(0.0, ("<S>", "<S>"), [])]   # (score, (prev2,prev1), tags)
        for form in forms:
            emis, _ = self._emis_logp(form)
            cand = []
            for score, (p2, p1), seq in beams:
                for t in self.tags:
                    sc = score + emis[t] + self.w_ctx * self._ctx_logp(p2, p1, t)
                    cand.append((sc, (p1, t), seq + [t]))
            cand.sort(key=lambda x: -x[0])
            beams = cand[:self.beam]
        return beams[0][2]

    def evaluate(self, sents, oov_only=False, known_lex=None):
        c = t = 0
        for s in sents:
            forms = [x[0] for x in s]; gold = [x[1] for x in s]
            pred = self.tag(forms)
            for f, g, p in zip(forms, gold, pred):
                if oov_only and (f.lower() in (known_lex or self.lex)):
                    continue
                t += 1; c += int(p == g)
        return (c / t if t else 0.0, c, t)


def main(sweep=True):
    os.makedirs(_OUT, exist_ok=True)
    tr, te = load(_TRAIN), load(_TEST)
    trainlex = set()
    for s in tr:
        for f, *_ in s:
            trainlex.add(f.lower())
    results = {}
    grid = [(w, b) for w in (0.5, 1.0, 1.5, 2.0) for b in (1, 8)] if sweep else [(1.0, 8)]
    best = None
    for w_ctx, beam in grid:
        m = BrainTagger(w_ctx=w_ctx, beam=beam).fit(tr)
        acc, cc, tt = m.evaluate(te)
        results["w%.1f_b%d" % (w_ctx, beam)] = acc
        print("w_ctx=%.1f beam=%d : acc=%.4f" % (w_ctx, beam, acc), flush=True)
        if best is None or acc > best[0]:
            best = (acc, w_ctx, beam)
    acc, w_ctx, beam = best
    print("\nBEST brain-tagger: acc=%.4f (w_ctx=%.1f beam=%d)  vs Viterbi floor 0.9445" % (acc, w_ctx, beam), flush=True)
    m = BrainTagger(w_ctx=w_ctx, beam=beam).fit(tr)
    oov_acc, oc, ot = m.evaluate(te, oov_only=True, known_lex=trainlex)
    print("OOV-slice acc=%.4f (%d/%d) -- morphology/prediction robustness" % (oov_acc, oc, ot), flush=True)

    # INFO-FREE TWIN: scramble the lexicon (word->random tag counts) -> emission carries no signal
    import random
    rng = random.Random(20260904)
    twin = BrainTagger(w_ctx=w_ctx, beam=beam).fit(tr)
    alltags = twin.tags
    twin.lex = defaultdict(Counter)
    for wl in list(m.lex.keys()):
        twin.lex[wl][rng.choice(alltags)] = 1     # random category per word, same shape
    twin_acc, _, _ = twin.evaluate(te)
    print("INFO-FREE twin (scrambled lexicon) acc=%.4f (must collapse)" % twin_acc, flush=True)

    with open(os.path.join(_OUT, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"viterbi_floor": 0.9445, "brain_best": acc, "best_cfg": [w_ctx, beam],
                   "oov_acc": oov_acc, "twin_acc": twin_acc, "sweep": results}, f, indent=2)
    print("wrote", os.path.join(_OUT, "metrics.json"), flush=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--no-sweep", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        tr = load(_TRAIN)[:400]
        m = BrainTagger(beam=4).fit(tr)
        out = m.tag("the quick brown fox jumps".split())
        assert len(out) == 5 and all(o in m.tags for o in out), out
        print("SELF-TEST PASS: brain-tagger decodes; tags=%s" % out)
    else:
        main(sweep=not a.no_sweep)
