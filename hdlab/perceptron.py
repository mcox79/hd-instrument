"""Structured discriminative perceptron -- substrate-internal learning primitive.

Per Director DECISION 23 Tier 1 Item 2 (parallel with Item 1): integrate
discriminative_perceptron into hdlab/ as learning primitive.

This is the Collins (2002) averaged structured perceptron for sequence
labeling, with Viterbi inference. Substrate-on-its-own (USER 11th rule):
pure-Python + numpy; no LLM, no bge, no torch.

Atoms grounded as executable:
  T2/discriminative_perceptron
  T2/structured_perceptron_collins
  T2/weight_vector (via averaged weight dict)
  T2/perceptron_update (mistake-driven weight adjustment)

Public API:
  StructuredPerceptron(tags) -- create perceptron over a tag set
  fit(sequences, feature_fn, transition_fn, epochs) -- online averaged training
  predict(observations, feature_fn) -- Viterbi-decoded tag sequence
  weights -- averaged learned weights

Live-query test included via __main__.

NO LLM. NO bge. NO torch.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Sequence

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class StructuredPerceptron:
    """Collins (2002) structured perceptron with averaged weights + Viterbi inference.

    Args:
        tags: list of tag labels
        rng_seed: optional seed for permutation order during training
    """

    def __init__(self, tags: Sequence[str], rng_seed: int = 1024):
        self.tags = list(tags)
        self.tag_index = {t: i for i, t in enumerate(self.tags)}
        self.n_tags = len(self.tags)
        # Raw weights (updated each mistake) and cumulative for averaging
        self._w: dict[str, float] = defaultdict(float)
        self._cw: dict[str, float] = defaultdict(float)
        self._c: int = 1  # cumulative-step counter
        self._averaged: dict[str, float] | None = None  # computed lazily
        self._rng_seed = rng_seed

    @property
    def weights(self) -> dict[str, float]:
        """Averaged weights (computed lazily after fit)."""
        if self._averaged is None:
            self._averaged = {f: self._w[f] - self._cw[f] / self._c for f in self._w}
        return self._averaged

    def _viterbi(
        self,
        observations: Sequence,
        weights: dict[str, float],
        feature_fn: Callable,
        transition_fn: Callable,
    ) -> list[str]:
        """Viterbi inference under current weights."""
        n = len(observations)
        if n == 0:
            return []

        if HAS_NUMPY:
            em = np.array([
                [sum(weights.get(f, 0.0) for f in feature_fn(observations, i, self.tags[k]))
                 for k in range(self.n_tags)]
                for i in range(n)
            ])
            TM = np.array([
                [weights.get(transition_fn(self.tags[j], self.tags[k]), 0.0)
                 for k in range(self.n_tags)]
                for j in range(self.n_tags)
            ])
            SV = np.array([weights.get(transition_fn("<S>", self.tags[k]), 0.0)
                           for k in range(self.n_tags)])
            V = np.empty((n, self.n_tags))
            bp = np.zeros((n, self.n_tags), dtype=int)
            V[0] = em[0] + SV
            for i in range(1, n):
                cand = V[i - 1][:, None] + TM
                bp[i] = np.argmax(cand, axis=0)
                V[i] = cand[bp[i], np.arange(self.n_tags)] + em[i]
            seq = [int(np.argmax(V[n - 1]))]
            for i in range(n - 1, 0, -1):
                seq.append(int(bp[i][seq[-1]]))
            seq.reverse()
            return [self.tags[k] for k in seq]

        # numpy-free fallback
        em = [
            [sum(weights.get(f, 0.0) for f in feature_fn(observations, i, self.tags[k]))
             for k in range(self.n_tags)]
            for i in range(n)
        ]
        TM = [
            [weights.get(transition_fn(self.tags[j], self.tags[k]), 0.0)
             for k in range(self.n_tags)]
            for j in range(self.n_tags)
        ]
        SV = [weights.get(transition_fn("<S>", self.tags[k]), 0.0) for k in range(self.n_tags)]
        V = [[0.0] * self.n_tags for _ in range(n)]
        bp = [[0] * self.n_tags for _ in range(n)]
        for k in range(self.n_tags):
            V[0][k] = em[0][k] + SV[k]
        for i in range(1, n):
            for k in range(self.n_tags):
                best_score = float("-inf")
                best_prev = 0
                for j in range(self.n_tags):
                    score = V[i-1][j] + TM[j][k]
                    if score > best_score:
                        best_score = score
                        best_prev = j
                V[i][k] = best_score + em[i][k]
                bp[i][k] = best_prev
        seq = [max(range(self.n_tags), key=lambda k: V[n-1][k])]
        for i in range(n - 1, 0, -1):
            seq.append(bp[i][seq[-1]])
        seq.reverse()
        return [self.tags[k] for k in seq]

    def fit(
        self,
        sequences: Sequence,
        feature_fn: Callable,
        transition_fn: Callable,
        epochs: int = 6,
    ) -> None:
        """Train via online structured-perceptron with averaging.

        Each sequence is a list of (observation, gold_tag) tuples.
        feature_fn(observations, i, tag) returns iterable of feature strings.
        transition_fn(prev_tag, cur_tag) returns transition-feature string.
        """
        if HAS_NUMPY:
            rng = np.random.default_rng(self._rng_seed)
            order_fn = lambda n: rng.permutation(n)
        else:
            import random
            rnd = random.Random(self._rng_seed)
            def order_fn(n):
                ordering = list(range(n))
                rnd.shuffle(ordering)
                return ordering

        for ep in range(epochs):
            order = order_fn(len(sequences))
            for si in order:
                seq = sequences[si]
                if not seq:
                    continue
                obs = [pair[0] for pair in seq]
                gold = [pair[1] for pair in seq]
                pred = self._viterbi(obs, self._w, feature_fn, transition_fn)
                if pred != gold:
                    pg = "<S>"
                    pp = "<S>"
                    for i in range(len(obs)):
                        if pred[i] != gold[i] or i == 0 or pred[i-1] != gold[i-1]:
                            for f in feature_fn(obs, i, gold[i]):
                                self._w[f] += 1
                                self._cw[f] += self._c
                            for f in feature_fn(obs, i, pred[i]):
                                self._w[f] -= 1
                                self._cw[f] -= self._c
                        self._w[transition_fn(pg, gold[i])] += 1
                        self._cw[transition_fn(pg, gold[i])] += self._c
                        self._w[transition_fn(pp, pred[i])] -= 1
                        self._cw[transition_fn(pp, pred[i])] -= self._c
                        pg = gold[i]
                        pp = pred[i]
                self._c += 1

        # Reset cached averaged weights so .weights recomputes
        self._averaged = None

    def predict(
        self,
        observations: Sequence,
        feature_fn: Callable,
        transition_fn: Callable,
    ) -> list[str]:
        """Decode tag sequence under averaged weights."""
        return self._viterbi(observations, self.weights, feature_fn, transition_fn)


# ============================================================
# Live-query test (DECISION 23 done-definition gate)
# ============================================================

def _toy_features(obs, i, tag):
    """Toy emission features for the live-query test."""
    w = obs[i].lower()
    feats = [f"w_{w}~{tag}"]
    if i > 0:
        feats.append(f"pw_{obs[i-1].lower()}~{tag}")
    if i + 1 < len(obs):
        feats.append(f"nw_{obs[i+1].lower()}~{tag}")
    return feats


def _toy_transition(prev_tag, cur_tag):
    return f"tt_{prev_tag}~{cur_tag}"


def _live_query_test() -> dict:
    """DECISION 23 done-definition gate: operator EXECUTES on live query."""
    tags = ["DT", "NN", "VB"]
    train_data = [
        [("the", "DT"), ("dog", "NN"), ("runs", "VB")],
        [("a", "DT"), ("cat", "NN"), ("sleeps", "VB")],
        [("the", "DT"), ("bird", "NN"), ("flies", "VB")],
        [("the", "DT"), ("dog", "NN"), ("barks", "VB")],
    ]
    perc = StructuredPerceptron(tags=tags, rng_seed=42)
    perc.fit(train_data, _toy_features, _toy_transition, epochs=10)

    test_obs = ["the", "dog", "barks"]
    pred = perc.predict(test_obs, _toy_features, _toy_transition)
    weights_size = len(perc.weights)
    return {
        "observations": test_obs,
        "predicted_tags": pred,
        "expected_tags": ["DT", "NN", "VB"],
        "averaged_weights_size": weights_size,
        "n_training_sequences": len(train_data),
    }


if __name__ == "__main__":
    print("=== STRUCTURED PERCEPTRON -- DECISION 23 Item 2 live-query test ===")
    r = _live_query_test()
    print(f"observations:        {r['observations']}")
    print(f"predicted_tags:      {r['predicted_tags']}")
    print(f"expected_tags:       {r['expected_tags']}")
    print(f"averaged_weights_size: {r['averaged_weights_size']}")
    print(f"n_training_sequences: {r['n_training_sequences']}")
    assert r["predicted_tags"] == r["expected_tags"], \
        f"Perceptron expected {r['expected_tags']}, got {r['predicted_tags']}"
    print("LIVE QUERY PASS: structured perceptron executable as substrate-internal primitive.")
