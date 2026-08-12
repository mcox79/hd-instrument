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


class PosTagger:
    """Persistable UPOS tagger over the averaged structured perceptron."""

    def __init__(self, tags: Sequence[str], perceptron: StructuredPerceptron):
        self.tags = list(tags)
        self._perc = perceptron

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
        """UPOS tag per token via Viterbi under averaged weights."""
        return self._perc.predict(list(tokens), pos_features, pos_transition)

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
