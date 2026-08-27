"""Forward-prediction reading organ -- the WORD/FEATURE level of the predictive hierarchy.

Landed 2026-08-26 from the integrated `the_reader_is_feed_forward_where_the_brain_is_predictive`
(SOLVED/EXCELLENT, owner-DONE; witness verify_predictive_reader.py 8/8 PASS). The verb (+ its
thematic role) pre-activates the expected argument's GROUNDED semantic features -- the literature-
standard role-specific selectional-preference centroid (Altmann & Kamide 1999; McRae et al. 1998
thematic fit) -- and the mismatch against the actual argument is read out as -log P softmax
surprisal. This is the missing FORWARD half of predictive coding; the `n400_coherence_monitor`
is the backward-looking EVENT-coherence half -- the two are TWO LEVELS of one predictive
hierarchy (temporal/ATL+angular-gyrus forward predictor feeding the frontal event monitor).

WHAT IS PINNED (copy the operation): pre-activate expected FEATURES, the error is the signal,
surprisal = -log P under softmax competition (Hale 2001; Levy 2008; Michaelov et al. 2024 -- LM
surprisal is the best single account of the N400). Predict MEANING FEATURES, not the word-FORM
(Nieuwland et al. 2018 -- our coarse grounded space is aligned with the ROBUST level). The
predictive benefit is PRECISION-WEIGHTED by the verb's selectional-preference concentration
(Friston constraint strength; Kutas-Federmeier): a sharp verb makes a high-precision prediction
that should be trusted more.

OUR-INVENTION-UNDER-TEST (swept, not adopted): the role-specific CENTROID as the selectional-
preference instantiation (the literature-standard thematic-fit model, Santus 2017); the softmax
TEMPERATURE; the grounded space as the feature basis.

DEFAULT-SAFE / ISLAND: importing this changes NO existing behaviour. `fit()` it on a predicate-
argument corpus (verb, role, arg triples -- e.g. QA-SRL via the predictive-reader cell's
`extract_triples`), then query `predict` / `surprisal` / `precision`. Reuses
`hdlab.grounded_similarity.grounded_vector` as the feature space. Do NOT predict word-forms; do
NOT route surprisal through `predictive_coding.predict`'s sign()-quantised residual (keep it
graded, in the content space, in -log P form). This is a construction-proven mechanism -- MEASURE
on the live reader before any capability claim; its live value is a graded difficulty /
anticipation SIGNAL (feeds the relcl route-conflict, write-gating, N400 confidence), not a
standalone accuracy lift (the isolation effect is modest, ceiling'd by the grounded space).
"""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from hdlab.grounded_similarity import grounded_vector

_EPS = 1e-9
DEFAULT_TEMP = 0.5  # OUR-INVENTION-UNDER-TEST, swept (the cell's value)


def _g(word: str) -> Optional[np.ndarray]:
    v = grounded_vector(word)
    if v is None:
        return None
    return np.asarray(v, dtype=np.float64).reshape(-1)


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < _EPS or nb < _EPS:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _softmax_neglogp_true(scores: np.ndarray, true_idx: int, temp: float) -> float:
    """-log softmax(scores/temp)[true_idx]; numerically safe. (copied verbatim from the
    validated cell exp_predictive_reader_anticipation_surprisal_v1)."""
    z = np.asarray(scores, dtype=np.float64) / max(temp, _EPS)
    z = z - float(np.max(z))
    ez = np.exp(z)
    denom = float(np.sum(ez)) + _EPS
    p_true = float(ez[true_idx]) / denom
    return -math.log(max(p_true, _EPS))


def _as_triple(t) -> Tuple[str, str, str]:
    if isinstance(t, dict):
        return (t["verb"], t["role"], t["arg"])
    return (t[0], t[1], t[2])


class PredictiveReader:
    """Verb (+role) -> expected argument grounded-feature centroid; -log P softmax surprisal.

    Fit on (verb, role, arg) triples, then:
      - predict(verb, role)   -> the expected features (falls back to the global role base rate)
      - surprisal(verb, role, actual, candidates) -> -log P(actual | softmax competition)
      - precision(verb, role) -> the selectional-preference concentration (trust weight)
    """

    def __init__(self, temp: float = DEFAULT_TEMP):
        self.temp = float(temp)
        self._argvecs: Dict[str, np.ndarray] = {}
        self._vr_centroid: Dict[Tuple[str, str], np.ndarray] = {}
        self._role_centroid: Dict[str, np.ndarray] = {}
        self._vr_count: Dict[Tuple[str, str], int] = {}
        self._precision: Dict[Tuple[str, str], float] = {}

    def fit(self, triples: Iterable) -> "PredictiveReader":
        """Build the verb-role centroids (mean grounded vector of the verb's args in that role),
        the GLOBAL role centroid (base rate), per-(verb,role) counts, and PRECISION (mean cosine
        of the args to their centroid -- selectional-preference concentration). Args with no
        grounded vector are skipped (grounded-covered by construction)."""
        norm = [_as_triple(t) for t in triples]
        argvecs: Dict[str, np.ndarray] = {}
        for _, _, arg in norm:
            if arg not in argvecs:
                g = _g(arg)
                if g is not None:
                    argvecs[arg] = g
        by_vr: Dict[Tuple[str, str], List[np.ndarray]] = defaultdict(list)
        by_role: Dict[str, List[np.ndarray]] = defaultdict(list)
        for verb, role, arg in norm:
            g = argvecs.get(arg)
            if g is None:
                continue
            by_vr[(verb, role)].append(g)
            by_role[role].append(g)
        self._argvecs = argvecs
        self._vr_centroid = {k: np.mean(np.stack(v), axis=0) for k, v in by_vr.items()}
        self._vr_count = {k: len(v) for k, v in by_vr.items()}
        self._role_centroid = {r: np.mean(np.stack(v), axis=0) for r, v in by_role.items()}
        self._precision = {
            k: float(np.mean([_cos(g, self._vr_centroid[k]) for g in v]))
            for k, v in by_vr.items()
        }
        return self

    def predict(self, verb: str, role: str) -> Optional[np.ndarray]:
        """The expected argument's grounded-feature centroid (the verb-role selectional
        preference), falling back to the GLOBAL role centroid (base rate) if the verb-role is
        unseen. None if the role itself is unseen."""
        c = self._vr_centroid.get((verb, role))
        if c is not None:
            return c
        return self._role_centroid.get(role)

    def precision(self, verb: str, role: str) -> Optional[float]:
        """Selectional-preference PRECISION (constraint strength): the concentration of the
        verb-role's argument distribution (mean cosine of its args to their centroid). Higher =
        a sharper, more reliable prediction to trust more (Friston precision-weighting). None if
        the verb-role is unseen."""
        return self._precision.get((verb, role))

    def count(self, verb: str, role: str) -> int:
        """How many training args backed this verb-role centroid (0 if unseen)."""
        return int(self._vr_count.get((verb, role), 0))

    def surprisal(self, verb: str, role: str, actual: str,
                  candidates: Sequence[str], temp: Optional[float] = None) -> Optional[float]:
        """-log P(actual | softmax over cos(g(candidate), verb-role centroid)) among the
        candidate set. `actual` is added to the candidates if absent. Lower = better anticipated.
        Returns None if the centroid or the actual candidate's grounded vector is unavailable."""
        centroid = self.predict(verb, role)
        if centroid is None:
            return None
        cands = list(candidates)
        if actual not in cands:
            cands = [actual] + cands
        g_true = self._argvecs.get(actual)
        if g_true is None:
            g_true = _g(actual)
        if g_true is None:
            return None
        scores = np.empty(len(cands), dtype=np.float64)
        for i, c in enumerate(cands):
            g = self._argvecs.get(c)
            if g is None:
                g = _g(c)
            scores[i] = _cos(g, centroid) if g is not None else -1.0
        true_idx = cands.index(actual)
        return _softmax_neglogp_true(scores, true_idx, self.temp if temp is None else float(temp))


__all__ = ["PredictiveReader", "DEFAULT_TEMP"]
