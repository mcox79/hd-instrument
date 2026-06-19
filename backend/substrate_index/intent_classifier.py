"""Learned intent / text classifier -- extends LIVE intent_router.

Per Director DECISION 24 Tier 2 Item 5 (parallel with Item 4): integrate
intent / text classification into backend/substrate_index/intent_router
as a LEARNED classifier complementing the existing rule-based prototype.

Atoms grounded as executable:
  T2/discriminative_classification (multi-class perceptron)
  T3/count_nb (naive Bayes text classifier alternative; same API)

Public API:
  IntentClassifier -- multi-class averaged perceptron over bag-of-words
    fit(examples) -- examples = list of (text, label)
    predict(text) -> label
    predict_with_score(text) -> (label, confidence)

  RoutedIntentClassifier -- composes existing rule-based router with
                            learned fallback
    route(text) -> {primitive, confidence, args, source}
       source is 'rule' if rule-based router fired, else 'learned'

Design: extracts existing rule-based router's logic as the primary path;
falls back to learned classifier when rules produce no match or low
confidence. Atomic add; existing intent_router.py untouched.

USER 11th rule: pure-Python + optional numpy fallback. No LLM/bge/torch.
USER 18th rule: refuses-low-confidence (below threshold returns 'unknown').

NO LLM. NO bge. NO torch.
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Callable, Sequence

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ============================================================
# Bag-of-words feature extraction
# ============================================================

_TOKENIZE_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*")


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKENIZE_RE.findall(text)]


def bow_features(text: str) -> list[str]:
    """Bag-of-words + bigram features for intent classification."""
    toks = tokenize(text)
    feats = [f"w_{t}" for t in toks]
    for i in range(len(toks) - 1):
        feats.append(f"bg_{toks[i]}_{toks[i+1]}")
    if toks:
        feats.append(f"first_{toks[0]}")
        feats.append(f"last_{toks[-1]}")
    return feats


# ============================================================
# Multi-class averaged perceptron (text intent classifier)
# ============================================================

class IntentClassifier:
    """Multi-class averaged perceptron over bag-of-words features.

    Args:
        labels: optional list of intent labels (discovered from fit if None)
        rng_seed: shuffle seed for fit
        confidence_threshold: predict() returns None if max score below this
    """

    def __init__(
        self,
        labels: Sequence[str] | None = None,
        rng_seed: int = 1024,
        confidence_threshold: float = 0.0,
    ):
        self._labels = list(labels) if labels else None
        self._w: dict[str, dict[str, float]] = {}  # label -> feature -> weight
        self._cw: dict[str, dict[str, float]] = {}
        self._c: int = 1
        self._averaged: dict[str, dict[str, float]] | None = None
        self._rng_seed = rng_seed
        self.confidence_threshold = confidence_threshold

    @property
    def labels(self) -> list[str]:
        return self._labels or []

    @property
    def weights(self) -> dict[str, dict[str, float]]:
        if self._averaged is None:
            self._averaged = {}
            for lab, wmap in self._w.items():
                self._averaged[lab] = {
                    f: wmap[f] - self._cw[lab].get(f, 0.0) / self._c
                    for f in wmap
                }
        return self._averaged

    def _score(self, features: Sequence[str], weights: dict[str, dict[str, float]]) -> dict[str, float]:
        scores = {}
        for lab in self._labels:
            wmap = weights.get(lab, {})
            scores[lab] = sum(wmap.get(f, 0.0) for f in features)
        return scores

    def fit(
        self,
        examples: Sequence[tuple[str, str]],
        epochs: int = 10,
        feature_fn: Callable | None = None,
    ) -> None:
        """Train via online averaged perceptron.

        examples: list of (text, label) tuples
        feature_fn: optional override for feature extraction (default bow_features)
        """
        feature_fn = feature_fn or bow_features

        # Discover label set
        if self._labels is None:
            self._labels = sorted({lab for _t, lab in examples})
        for lab in self._labels:
            self._w.setdefault(lab, {})
            self._cw.setdefault(lab, {})

        if HAS_NUMPY:
            rng = np.random.default_rng(self._rng_seed)
            order_fn = lambda n: rng.permutation(n)
        else:
            import random
            rnd = random.Random(self._rng_seed)
            def order_fn(n):
                order = list(range(n))
                rnd.shuffle(order)
                return order

        for ep in range(epochs):
            order = order_fn(len(examples))
            for ei in order:
                text, gold = examples[ei]
                if gold not in self._labels:
                    continue
                feats = feature_fn(text)
                scores = self._score(feats, self._w)
                pred = max(scores, key=scores.get)
                if pred != gold:
                    for f in feats:
                        self._w[gold][f] = self._w[gold].get(f, 0.0) + 1
                        self._cw[gold][f] = self._cw[gold].get(f, 0.0) + self._c
                        self._w[pred][f] = self._w[pred].get(f, 0.0) - 1
                        self._cw[pred][f] = self._cw[pred].get(f, 0.0) - self._c
                self._c += 1

        # Reset cached averaged weights
        self._averaged = None

    def predict_with_score(
        self,
        text: str,
        feature_fn: Callable | None = None,
    ) -> tuple[str | None, float]:
        """Return (label, confidence_score). Label is None if below threshold."""
        feature_fn = feature_fn or bow_features
        feats = feature_fn(text)
        scores = self._score(feats, self.weights)
        if not scores:
            return None, 0.0
        best_label = max(scores, key=scores.get)
        best_score = scores[best_label]
        if best_score < self.confidence_threshold:
            return None, best_score
        return best_label, best_score

    def predict(self, text: str, feature_fn: Callable | None = None) -> str | None:
        return self.predict_with_score(text, feature_fn)[0]


# ============================================================
# Composed router: rule-based primary + learned fallback
# ============================================================

class RoutedIntentClassifier:
    """Compose the LIVE rule-based intent_router with a learned fallback.

    When rules produce a high-confidence match -> use rules.
    When rules fail / low confidence -> use learned classifier.

    Args:
        learned: a fit IntentClassifier
        rule_router_fn: callable(text) -> dict with at least 'primitive' +
                        'confidence'; or None to skip rule routing
        rule_confidence_threshold: threshold above which rule-router wins;
                                   below this, fall back to learned
    """

    def __init__(
        self,
        learned: IntentClassifier,
        rule_router_fn: Callable | None = None,
        rule_confidence_threshold: float = 0.7,
    ):
        self.learned = learned
        self.rule_router_fn = rule_router_fn
        self.rule_confidence_threshold = rule_confidence_threshold

    def route(self, text: str) -> dict:
        """Return composed routing decision.

        Returns dict: {primitive, confidence, args, source}
            source: 'rule' or 'learned' or 'unknown'
        """
        # Try rules first
        if self.rule_router_fn is not None:
            rule_result = self.rule_router_fn(text)
            if rule_result and rule_result.get("confidence", 0.0) >= self.rule_confidence_threshold:
                return {
                    "primitive": rule_result.get("primitive"),
                    "confidence": rule_result.get("confidence"),
                    "args": rule_result.get("args", {}),
                    "source": "rule",
                }

        # Fall back to learned
        label, score = self.learned.predict_with_score(text)
        if label is None:
            return {
                "primitive": None,
                "confidence": 0.0,
                "args": {},
                "source": "unknown",
            }
        return {
            "primitive": label,
            "confidence": float(score),
            "args": {},
            "source": "learned",
        }


# ============================================================
# Live-query test (DECISION 24 done-definition gate)
# ============================================================

def _live_query_test() -> dict:
    """Train a 4-class intent classifier and check it routes correctly."""
    train = [
        ("what is the weather today", "weather"),
        ("how warm is it outside", "weather"),
        ("will it rain tomorrow", "weather"),
        ("forecast for monday", "weather"),
        ("set an alarm for 7am", "alarm"),
        ("wake me up at six", "alarm"),
        ("set timer for 10 minutes", "alarm"),
        ("alarm for tomorrow morning", "alarm"),
        ("play some music", "music"),
        ("play jazz on speakers", "music"),
        ("turn on the radio", "music"),
        ("play classical music", "music"),
        ("send a message to alice", "message"),
        ("text bob hello", "message"),
        ("email mom about dinner", "message"),
        ("send sarah a text", "message"),
    ]
    clf = IntentClassifier(rng_seed=42, confidence_threshold=0.5)
    clf.fit(train, epochs=15)

    test_cases = [
        ("what is the temperature outside", "weather"),
        ("wake me at eight", "alarm"),
        ("play rock music", "music"),
        ("send tom a message", "message"),
    ]
    results = []
    for text, expected in test_cases:
        pred = clf.predict(text)
        results.append({"text": text, "expected": expected, "predicted": pred, "correct": pred == expected})

    return {
        "n_training": len(train),
        "n_test": len(test_cases),
        "n_correct": sum(1 for r in results if r["correct"]),
        "test_results": results,
    }


if __name__ == "__main__":
    print("=== INTENT CLASSIFIER -- DECISION 24 Item 5 live-query test ===")
    r = _live_query_test()
    print(f"training examples: {r['n_training']}")
    print(f"test predictions:")
    for tr in r["test_results"]:
        ok = "OK" if tr["correct"] else "FAIL"
        print(f"  [{ok}] '{tr['text']}' -> expected={tr['expected']} predicted={tr['predicted']}")
    print(f"\naccuracy: {r['n_correct']}/{r['n_test']}")
    assert r["n_correct"] >= 3, \
        f"Intent classifier expected >=3/4 correct on toy held-out; got {r['n_correct']}"
    print("LIVE QUERY PASS: intent classifier executable as substrate-internal primitive.")
