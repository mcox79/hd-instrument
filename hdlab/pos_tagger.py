"""Glass-box UPOS tagger -- our-own averaged structured perceptron (NO nltk).

Front-end Asset 1 for the reader-parser pipeline. Wraps hdlab.perceptron.StructuredPerceptron
(Collins 2002 averaged perceptron + Viterbi) as a persistable tag(tokens)->UPOS operator so the
reading pipeline gets POS in-substrate + inspectable, with no external nltk dependency.

Public API:
  PosTagger.train(train_seqs, epochs, ...) -> PosTagger      # train from [(word, upos), ...] sequences
  PosTagger.load(path) -> PosTagger                          # load persisted json model
  tagger.save(path)                                          # persist averaged weights + tag set (json = glass-box)
  tagger.tag(tokens) -> list[str]                            # UPOS per token (Viterbi-decoded)
  tagger.evaluate(seqs) -> float                             # token UPOS accuracy

Feature functions are module-level + deterministic so a loaded model decodes identically.
NO LLM. NO nltk. NO torch. numpy + pure-python only.
ASCII-only.
"""
from __future__ import annotations

import json
from typing import List, Sequence, Tuple

import numpy as np

from hdlab.perceptron import StructuredPerceptron


def pos_features(obs: Sequence[str], i: int, tag: str) -> List[str]:
    """Emission features for token i under candidate `tag`. Ratnaparkhi/Collins-style; word + affix + shape + context."""
    w = obs[i]
    wl = w.lower()
    feats = ["b~" + tag, "w:" + wl + "~" + tag]
    L = len(wl)
    for k in (1, 2, 3, 4):
        if L >= k:
            feats.append("suf%d:%s~%s" % (k, wl[-k:], tag))
            feats.append("pre%d:%s~%s" % (k, wl[:k], tag))
    if w[:1].isupper():
        feats.append("cap~" + tag)
    if any(c.isdigit() for c in w):
        feats.append("hasdig~" + tag)
    if "-" in w:
        feats.append("hyph~" + tag)
    if i > 0:
        feats.append("pw:" + obs[i - 1].lower() + "~" + tag)
    else:
        feats.append("BOS~" + tag)
    if i + 1 < len(obs):
        feats.append("nw:" + obs[i + 1].lower() + "~" + tag)
    else:
        feats.append("EOS~" + tag)
    return feats


def pos_transition(prev_tag: str, cur_tag: str) -> str:
    """Transition feature string prev->cur (includes <S> start pseudo-tag)."""
    return "tt:" + prev_tag + "~" + cur_tag


def token_bases(obs: Sequence[str], i: int) -> List[str]:
    """The TAG-INDEPENDENT part of pos_features(obs,i,tag), in the EXACT emit order (drop the ~tag).

    Mirrors pos_features line-for-line: b, w:, (suf/pre 1..4), cap, hasdig, hyph, pw:/BOS, nw:/EOS.
    Preserving the order => re-suffixing each base with ~tag reproduces pos_features's feature strings
    => identical dict values in identical sum order => byte-identical emission scores. Promoted verbatim
    from experiments/exp_pos_tagger_fastfeat_v1.py.
    """
    w = obs[i]
    wl = w.lower()
    bases = ["b", "w:" + wl]
    L = len(wl)
    for k in (1, 2, 3, 4):
        if L >= k:
            bases.append("suf%d:%s" % (k, wl[-k:]))
            bases.append("pre%d:%s" % (k, wl[:k]))
    if w[:1].isupper():
        bases.append("cap")
    if any(c.isdigit() for c in w):
        bases.append("hasdig")
    if "-" in w:
        bases.append("hyph")
    if i > 0:
        bases.append("pw:" + obs[i - 1].lower())
    else:
        bases.append("BOS")
    if i + 1 < len(obs):
        bases.append("nw:" + obs[i + 1].lower())
    else:
        bases.append("EOS")
    return bases


class _FastEmissionPlan:
    """Byte-identical variant-C fast emission plan for the POS tagger, promoted verbatim from
    experiments/exp_pos_tagger_fastfeat_v1.py (FastTagger). Built ONCE from the averaged weights:

      * base_contrib: base -> [(tag_idx, weight)]   (emission keys split on the LAST '~'; 'tt:' = transition)
      * TM [n_tags x n_tags] + SV [n_tags]: precomputed transition potentials (constant given the weights),
        built via pos_transition so they are bit-identical to the stock per-sentence rebuild.

    emission(obs, n) collects the PRESENT weights per tag lane IN BASE ORDER, then sum()s each lane with
    the SAME built-in sum() the stock path uses -- so CPython's Neumaier-compensated reduction is
    bit-identical (dropping the 0.0-default terms is a no-op inside the compensated sum). The witness
    asserts the whole emission matrix np.array_equal to the reference, precisely to guard this.
    """

    def __init__(self, weights, tags, transition_fn):
        self.weights = weights            # identity guard: fast path fires only when _viterbi is passed THIS dict
        self.tags = list(tags)
        self.n_tags = len(self.tags)
        ti = {t: i for i, t in enumerate(self.tags)}
        self.base_contrib = {}            # base -> list[(tag_idx, weight)]
        for key, val in weights.items():
            if key.startswith("tt:"):
                continue
            base, tag = key.rsplit("~", 1)
            k = ti[tag]
            self.base_contrib.setdefault(base, []).append((k, val))
        self.TM = np.array([[weights.get(transition_fn(self.tags[j], self.tags[k]), 0.0)
                             for k in range(self.n_tags)] for j in range(self.n_tags)])
        self.SV = np.array([weights.get(transition_fn("<S>", self.tags[k]), 0.0)
                            for k in range(self.n_tags)])

    def emission(self, obs, n):
        """Sparse per-lane emission matrix (variant C), byte-identical to the stock full-sum build.
        The per-lane lists are allocated ONCE per sentence and cleared per token (reuse avoids realloc)."""
        nt = self.n_tags
        bc = self.base_contrib
        perlane = [[] for _ in range(nt)]
        em = np.empty((n, nt))
        for i in range(n):
            for lst in perlane:
                lst.clear()
            for base in token_bases(obs, i):
                c = bc.get(base)
                if c is not None:
                    for k, w in c:
                        perlane[k].append(w)
            row = em[i]
            for k in range(nt):
                row[k] = sum(perlane[k])   # sum([]) == 0 -> +0.0, matching stock's all-0.0 lane
        return em


class PosTagger:
    """Persistable UPOS tagger over the averaged structured perceptron."""

    def __init__(self, tags: Sequence[str], perceptron: StructuredPerceptron):
        self.tags = list(tags)
        self._perc = perceptron
        self._fast: "_FastEmissionPlan | None" = None  # byte-identical variant-C plan, built lazily on first tag

    @classmethod
    def train(
        cls,
        train_seqs: Sequence[Sequence[Tuple[str, str]]],
        epochs: int = 6,
        rng_seed: int = 1024,
        tags: Sequence[str] | None = None,
    ) -> "PosTagger":
        """Train from sequences of (word, upos) pairs. Returns a fitted PosTagger."""
        if tags is None:
            tags = sorted({t for s in train_seqs for _, t in s})
        perc = StructuredPerceptron(tags, rng_seed=rng_seed)
        perc.fit(list(train_seqs), pos_features, pos_transition, epochs=epochs)
        return cls(tags, perc)

    def tag(self, tokens: Sequence[str]) -> List[str]:
        """UPOS tag per token via Viterbi under averaged weights (byte-identical variant-C fast path)."""
        self._ensure_fast()
        return self._perc.predict(list(tokens), pos_features, pos_transition)

    def _ensure_fast(self) -> "_FastEmissionPlan":
        """Lazily build + attach the variant-C fast emission plan (byte-identical). Idempotent.

        The plan is built from self._perc.weights (the averaged dict) and attached to the perceptron;
        _viterbi then fires the fast path whenever it is handed that same dict (inference), while
        training (fit) -- which uses the raw weights -- stays on the stock reference."""
        if self._fast is None:
            self._fast = _FastEmissionPlan(self._perc.weights, self.tags, pos_transition)
            self._perc.set_fast_emission(self._fast)
        return self._fast

    def _emission_fast(self, tokens: Sequence[str]) -> "np.ndarray":
        """Variant-C fast emission matrix (pure-hdlab byte-identity witness hook)."""
        obs = list(tokens)
        return self._ensure_fast().emission(obs, len(obs))

    def _emission_reference(self, tokens: Sequence[str]) -> "np.ndarray":
        """Stock emission matrix -- the byte-identity REFERENCE (pure-hdlab witness hook)."""
        obs = list(tokens)
        return self._perc._emission_reference(obs, self._perc.weights, pos_features)

    def _tag_reference(self, tokens: Sequence[str]) -> List[str]:
        """Stock Collins-Viterbi tags (UNCHANGED reference path). Pure-hdlab witness hook + fair-timing floor."""
        return self._perc._viterbi_reference(list(tokens), self._perc.weights, pos_features, pos_transition)

    def evaluate(self, seqs: Sequence[Sequence[Tuple[str, str]]]) -> Tuple[float, int, int]:
        """Token UPOS accuracy over gold (word, upos) sequences. Returns (acc, n_correct, n_tokens)."""
        c = 0
        t = 0
        for s in seqs:
            obs = [w for w, _ in s]
            gold = [g for _, g in s]
            pred = self.tag(obs)
            for p, g in zip(pred, gold):
                c += int(p == g)
                t += 1
        return (c / t if t else 0.0, c, t)

    def save(self, path: str) -> None:
        """Persist averaged weights + tag set to json (glass-box, inspectable)."""
        payload = {"tags": self.tags, "weights": self._perc.weights}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f)

    @classmethod
    def load(cls, path: str) -> "PosTagger":
        """Load a persisted json model; decodes identically to the trained tagger."""
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        perc = StructuredPerceptron(d["tags"])
        perc._averaged = {k: float(v) for k, v in d["weights"].items()}
        return cls(d["tags"], perc)
