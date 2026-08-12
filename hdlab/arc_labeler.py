"""Glass-box UD dependency-RELATION labeler -- adds deprel LABELS on top of the unlabeled arc parser.

Front-end Asset 3 for the reader-parser pipeline. The persisted hdlab.arc_parser produces UNLABELED
heads (UAS ~0.7868); it cannot tell a subject from an object. This module classifies each arc's UD
RELATION LABEL (nsubj / obj / obl / nsubj:pass / obl:agent / amod / det / ...) with a multiclass averaged
perceptron (Collins-style averaging, the same learning discipline as hdlab.arc_parser.train_arc and
hdlab.pos_tagger), so a candidate-generation stage can restrict patient candidates to the labeled patient
roles (obj / nsubj:pass) instead of "any nominal dependent".

Design: labeling an arc is a per-arc MULTICLASS problem given the head structure (not a Viterbi sequence
decode), so this uses a lightweight dict-keyed averaged multiclass perceptron -- glass-box + json-persistable
exactly like hdlab.pos_tagger (weights are "feature~label" -> float). Subtypes are collapsed to the main UD
relation EXCEPT nsubj:pass and obl:agent, which are kept in full because they carry the patient/agent
distinction the whole asset exists to recover.

Public API:
  train_label(train_sents, epochs, ...) -> ArcLabeler                 # train from UD (id,form,upos,head,deprel)
  ArcLabeler.load(path) / .save(path)                                 # persist json (glass-box)
  labeler.label(tokens, pos, heads) -> Dict[dep_idx, deprel]          # label each arc under given heads
  labeler.label_accuracy(gold_sents) -> (acc, n_correct, n)          # labeling accuracy GIVEN gold arcs
  norm_label(deprel) -> str                                           # subtype-collapse (keeps :pass / :agent)

NO LLM. NO nltk. NO torch. numpy + pure-python only. ASCII-only.
"""
from __future__ import annotations

import json
from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

# Subtypes collapsed to main relation EXCEPT these -- they carry the patient/agent distinction.
KEEP_FULL = {"nsubj:pass", "obl:agent", "csubj:pass"}


def norm_label(deprel: str) -> str:
    """Collapse UD subtype to the main relation, keeping nsubj:pass / obl:agent / csubj:pass in full."""
    if deprel in KEEP_FULL:
        return deprel
    return deprel.split(":", 1)[0]


def _dist(d: int) -> str:
    a = abs(d)
    return "1" if a == 1 else ("2" if a == 2 else ("3-5" if a <= 5 else ("6-10" if a <= 10 else "11+")))


def _suf(w: str) -> str:
    return w[-3:] if len(w) >= 3 else w


def arc_features(tokens: Sequence[str], pos: Sequence[str], i: int, h: int) -> List[str]:
    """Features for the arc (dependent i -> head h), 1-based indices; h==0 is ROOT. Head structure GIVEN."""
    n = len(tokens)
    dw = tokens[i - 1].lower()
    dp = pos[i - 1]
    if h == 0:
        hw, hp = "<ROOT>", "ROOT"
        d = 0
        drc = "R"
    else:
        hw, hp = tokens[h - 1].lower(), pos[h - 1]
        d = h - i
        drc = "L" if d < 0 else "R"
    db = _dist(d)
    dpl = pos[i - 2] if i >= 2 else "<S>"
    dpr = pos[i] if i < n else "<E>"
    hpl = pos[h - 2] if h >= 2 else "<S>"
    hpr = pos[h] if 0 < h < n else "<E>"
    F = [
        "b",
        "dp:" + dp, "hp:" + hp, "hp_dp:%s_%s" % (hp, dp),
        "hp_dp_dir:%s_%s_%s" % (hp, dp, drc), "hp_dp_dist:%s_%s_%s" % (hp, dp, db),
        "dw:" + dw, "hw:" + hw, "dw_dp:%s_%s" % (dw, dp), "hw_hp:%s_%s" % (hw, hp),
        "hw_dw:%s_%s" % (hw, dw), "hp_dw:%s_%s" % (hp, dw), "hw_dp:%s_%s" % (hw, dp),
        "dp_dir:%s_%s" % (dp, drc), "hp_dir:%s_%s" % (hp, drc), "dp_dist:%s_%s" % (dp, db),
        "dsuf:%s" % _suf(dw), "dsuf_hp:%s_%s" % (_suf(dw), hp), "dsuf_dp:%s_%s" % (_suf(dw), dp),
        "dpl_dp:%s_%s" % (dpl, dp), "dpr_dp:%s_%s" % (dpr, dp),
        "hpl_hp:%s_%s" % (hpl, hp), "hpr_hp:%s_%s" % (hpr, hp),
        "ctx:%s_%s_%s_%s" % (dpl, dp, dpr, drc),
        "hp_dp_dpr:%s_%s_%s" % (hp, dp, dpr),
    ]
    return F


class ArcLabeler:
    """Multiclass averaged perceptron labeling each arc with its UD relation, given the head structure."""

    def __init__(self, labels: Sequence[str], weights: Dict[str, float] | None = None):
        self.labels = list(labels)
        self.weights: Dict[str, float] = dict(weights) if weights else {}

    def _score(self, feats: Sequence[str], lab: str) -> float:
        w = self.weights
        s = 0.0
        for f in feats:
            v = w.get(f + "~" + lab)
            if v is not None:
                s += v
        return s

    def _predict_label(self, feats: Sequence[str]) -> str:
        best_l = self.labels[0]
        best_s = float("-inf")
        for lab in self.labels:
            s = self._score(feats, lab)
            if s > best_s:
                best_s = s
                best_l = lab
        return best_l

    def label(self, tokens: Sequence[str], pos: Sequence[str], heads: Dict[int, int]) -> Dict[int, str]:
        """Label each arc dep->head under the GIVEN head map. Returns {dep_idx(1-based): deprel}."""
        out: Dict[int, str] = {}
        n = len(tokens)
        for i in range(1, n + 1):
            h = heads.get(i, 0)
            if h is None or h < 0 or h > n:
                h = 0
            feats = arc_features(tokens, pos, i, h)
            out[i] = self._predict_label(feats)
        return out

    def label_accuracy(self, gold_sents: Sequence[Sequence[tuple]], maxlen: int = 50) -> Tuple[float, int, int]:
        """Labeling accuracy GIVEN gold arcs: predict each arc's label under gold heads, compare to gold deprel."""
        correct = 0
        tot = 0
        for s in gold_sents:
            if not (1 <= len(s) <= maxlen):
                continue
            tokens = [t[1] for t in s]
            pos = [t[2] for t in s]
            for i in range(1, len(s) + 1):
                gold_h = s[i - 1][3]
                if gold_h < 0 or gold_h > len(s):
                    continue
                feats = arc_features(tokens, pos, i, gold_h)
                pred = self._predict_label(feats)
                gold_lab = norm_label(s[i - 1][4])
                correct += int(pred == gold_lab)
                tot += 1
        return (correct / tot if tot else 0.0, correct, tot)

    def save(self, path: str) -> None:
        """Persist labels + averaged weights to json (glass-box, inspectable)."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"labels": self.labels, "weights": self.weights}, f)

    @classmethod
    def load(cls, path: str) -> "ArcLabeler":
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        return cls(d["labels"], {k: float(v) for k, v in d["weights"].items()})


def train_label(
    train_sents: Sequence[Sequence[tuple]],
    epochs: int = 8,
    seed: int = 1031,
    maxlen: int = 50,
    min_label_count: int = 30,
) -> ArcLabeler:
    """Train multiclass averaged perceptron on UD (id,form,upos,head,deprel) sentences.

    Labels: norm_label(deprel); relations occurring < min_label_count times are folded into 'dep'
    (the UD catch-all), keeping the frequent + patient-critical relations sharp.
    """
    import numpy as np

    train = [s for s in train_sents if 1 <= len(s) <= maxlen]
    # label set from frequency
    freq: Dict[str, int] = defaultdict(int)
    for s in train:
        for t in s:
            if 0 <= t[3] <= len(s):
                freq[norm_label(t[4])] += 1
    keep = {lab for lab, c in freq.items() if c >= min_label_count}
    keep |= {"obj", "nsubj", "nsubj:pass", "obl", "obl:agent", "iobj", "dep", "root"}
    labels = sorted(keep)

    def lab_of(deprel: str) -> str:
        nl = norm_label(deprel)
        return nl if nl in keep else "dep"

    # precompute features + gold labels per arc
    data = []  # list of (feats, gold_label)
    for s in train:
        tokens = [t[1] for t in s]
        pos = [t[2] for t in s]
        arcs = []
        for i in range(1, len(s) + 1):
            gh = s[i - 1][3]
            if gh < 0 or gh > len(s):
                continue
            arcs.append((arc_features(tokens, pos, i, gh), lab_of(s[i - 1][4])))
        data.append(arcs)

    w: Dict[str, float] = defaultdict(float)
    cw: Dict[str, float] = defaultdict(float)
    c = 1
    rng = np.random.default_rng(seed)
    lab = ArcLabeler(labels)
    lab.weights = w  # share dict during training for scoring

    for ep in range(epochs):
        for si in rng.permutation(len(data)):
            for feats, gold in data[si]:
                pred = lab._predict_label(feats)
                if pred != gold:
                    for f in feats:
                        kg = f + "~" + gold
                        kp = f + "~" + pred
                        w[kg] += 1.0
                        cw[kg] += c
                        w[kp] -= 1.0
                        cw[kp] -= c
                c += 1

    averaged = {f: w[f] - cw[f] / c for f in w}
    return ArcLabeler(labels, averaged)


# ============================================================
# Live-query self-test
# ============================================================
def _self_test() -> bool:
    """Tiny synthetic self-test: labeler must separate subject from object under gold heads."""
    # sentences: (id, form, upos, head, deprel). "dog bites man": dog=nsubj, bites=root, man=obj.
    def mk(triples):
        return [(k + 1, w, p, h, r) for k, (w, p, h, r) in enumerate(triples)]

    train = []
    for subj, obj in [("dog", "man"), ("cat", "bird"), ("boy", "ball"), ("girl", "cup"), ("man", "dog")]:
        train.append(mk([(subj, "NOUN", 2, "nsubj"), ("bit", "VERB", 0, "root"), (obj, "NOUN", 2, "obj")]))
        train.append(mk([("the", "DET", 2, "det"), (subj, "NOUN", 3, "nsubj"),
                         ("saw", "VERB", 0, "root"), (obj, "NOUN", 3, "obj")]))
    lab = train_label(train, epochs=15, min_label_count=1)
    tokens = ["fox", "bit", "hen"]
    pos = ["NOUN", "VERB", "NOUN"]
    heads = {1: 2, 2: 0, 3: 2}
    got = lab.label(tokens, pos, heads)
    print("[selftest] label(fox bit hen) =", got)
    ok = (got[1] == "nsubj" and got[2] == "root" and got[3] == "obj")
    assert ok, "SELF-TEST FAIL: labeler did not separate nsubj(pre-verb) from obj(post-verb)"
    # round-trip persistence
    import tempfile
    import os
    tp = os.path.join(tempfile.gettempdir(), "arc_labeler_selftest.json")
    lab.save(tp)
    lab2 = ArcLabeler.load(tp)
    assert lab2.label(tokens, pos, heads) == got, "SELF-TEST FAIL: persistence round-trip changed labels"
    os.remove(tp)
    print("[selftest] PASS: subject/object separated + persistence round-trips")
    return True


if __name__ == "__main__":
    print("=== ARC LABELER -- live-query self-test ===")
    _self_test()
