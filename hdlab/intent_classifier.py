"""Substrate-native Hebbian-bound prototype-bundle intent classifier.

Operationalizes the a1 substrate intent classifier (CERT chain-grade
at n_intents=50; acc=0.754; maj_mult=4.62; rand_mult=5.19; p95=0.54ms)
plus EXT-3 production-scale extension (intent classifier v2 50-1000 intents).

Mechanism:
  Codebook E [n_intents, n_dim] = random bipolar; one prototype HD per intent.
  Train (Hebbian, one-shot): W = (E[labels].T @ question_hds) / n_dim
                             where E[labels] picks the prototype HD per training example.
  Predict: scores = E @ (W @ q); argmax.

Composes with `hdlab.char_trigram_encoder.CharTrigramEncoder` for text->HD.
Substrate-only (zero LLM forward calls at inference); designed for M3 cortex
router (substrate_router.api.SubstrateRouterAPI) as the intent-classification
primitive.

Cell source: experiments/exp_substrate_intent_classifier_v2_production_scale_100plus_intents.py
"""
from __future__ import annotations

import numpy as np


def make_intent_codebook(n_intents: int, n_dim: int, seed: int) -> np.ndarray:
    """Random bipolar codebook E [n_intents, n_dim] with shape annotation.

    Seed is mixed (seed * 1009 + 17) to decouple from data sampling RNG.
    """
    rng = np.random.default_rng(int(seed) * 1009 + 17)
    return (rng.integers(0, 2, size=(n_intents, n_dim)) * 2 - 1).astype(np.float32)


def hebbian_train(
    question_hds: np.ndarray,
    labels: np.ndarray,
    intent_codebook: np.ndarray,
) -> np.ndarray:
    """Hebbian one-shot bind: prototypes outer-product training questions.

    question_hds: [n_train, n_dim] float32 (encoded text -> HD)
    labels: [n_train] int64 (intent ID per training question)
    intent_codebook: [n_intents, n_dim] float32 (bipolar prototypes)

    Returns W: [n_dim, n_dim] float32. One-shot; no iteration; substrate-faithful.
    """
    intent_per_q = intent_codebook[labels]
    W = (intent_per_q.T @ question_hds) / float(intent_codebook.shape[1])
    return W.astype(np.float32)


def hebbian_predict(
    question_hd: np.ndarray,
    W: np.ndarray,
    intent_codebook: np.ndarray,
) -> int:
    """Single-query intent prediction.

    question_hd: [n_dim] float32
    W: [n_dim, n_dim] from hebbian_train
    intent_codebook: [n_intents, n_dim]

    Returns argmax intent ID. O(n_dim^2 + n_intents * n_dim).
    """
    Wq = W @ question_hd
    scores = intent_codebook @ Wq
    return int(np.argmax(scores))


def hebbian_predict_batch(
    question_hds: np.ndarray,
    W: np.ndarray,
    intent_codebook: np.ndarray,
) -> np.ndarray:
    """Vectorized batch prediction.

    question_hds: [n_query, n_dim]
    Returns: [n_query] int64 of argmax intent IDs.
    """
    Wq = question_hds @ W.T
    scores = Wq @ intent_codebook.T
    return np.argmax(scores, axis=1).astype(np.int64)


class IntentClassifier:
    """Composed intent classifier: codebook + Hebbian-bound W; train + predict API.

    Usage:
        clf = IntentClassifier(n_intents=50, n_dim=8192, seed=11)
        clf.fit(train_hds, train_labels)
        pred = clf.predict(test_hd)        # single query
        preds = clf.predict_batch(test_hds)  # batch
    """

    def __init__(self, n_intents: int, n_dim: int, seed: int) -> None:
        self.n_intents = n_intents
        self.n_dim = n_dim
        self.seed = seed
        self.codebook = make_intent_codebook(n_intents, n_dim, seed)
        self.W: np.ndarray | None = None

    def fit(self, question_hds: np.ndarray, labels: np.ndarray) -> "IntentClassifier":
        self.W = hebbian_train(question_hds, labels, self.codebook)
        return self

    def predict(self, question_hd: np.ndarray) -> int:
        if self.W is None:
            raise RuntimeError("call fit() before predict()")
        return hebbian_predict(question_hd, self.W, self.codebook)

    def predict_batch(self, question_hds: np.ndarray) -> np.ndarray:
        if self.W is None:
            raise RuntimeError("call fit() before predict_batch()")
        return hebbian_predict_batch(question_hds, self.W, self.codebook)
