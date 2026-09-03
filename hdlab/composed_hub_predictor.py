"""composed_hub_predictor.py -- the ~200-d ATL-hub + precision-weighted composed-exemplar forward-prediction
predictor, promoted VERBATIM (2026-09-03) from experiments/_composed_hub_predictor.py (owner-DONE
upgrade_predictive_reader_to_a_composed_exemplar_predictor_over_a_richer_hub).

A drop-in upgrade for the reader's forward-prediction (N400) surprisal: same `surprisal(verb, role, actual,
candidates, agent)` API as hdlab.predictive_reader, but reads a ~200-d register-native distributional HUB (ATL
hub; Lambon Ralph 2017) instead of the 12-d sensorimotor SPOKE (which collapses same-category fillers = the
located representational loss), a verb-prior CENTROID base + precision-weighted agent-COMPOSED exemplar
sharpening (Bicknell 2010; Frankland & Greene 2015; Friston precision). Beats the spoke +0.076 held-out (2.4x)
AND +0.069 on the live reader (broad pre-activation), all info-free twins losing CI-sep; transfers to WiC
sense discrimination +0.027. FHRR untouched (this changes only the filler CONTENT code + composition).
Glass-box, CPU numpy, NO LLM. The hub + fitted store are STATIC OFFLINE ASSETS (frontend_assets/), the SAME
hub the north-star P1 reads -- built once.
"""
from __future__ import annotations
import math
import os
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

_EPS = 1e-9
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB_ASSET = os.path.join(_REPO, "data", "frontend_assets", "hub_ppmi_svd_200d.pkl")
PRED_ASSET = os.path.join(_REPO, "data", "frontend_assets", "hub_composed_predictor_v1.pkl")


def _cn(M: np.ndarray) -> np.ndarray:
    return M / (np.linalg.norm(M, axis=1, keepdims=True) + _EPS)


class HubComposedPredictor:
    """fit((agent|None, verb, patient) triples) then score_pool / surprisal / precision.

    vec: word -> unit np.ndarray or None (the hub lookup; agent/patient may be OOV -> None).
    """

    def __init__(self, vec: Callable[[Optional[str]], Optional[np.ndarray]],
                 gamma: float = 2.0, lam_lo: float = 0.20, lam_hi: float = 0.55,
                 precision: bool = True, min_pat: int = 3, temp: float = 0.5):
        self.vec = vec
        self.gamma = float(gamma)
        self.lam_lo = float(lam_lo)
        self.lam_hi = float(lam_hi)
        self.precision = bool(precision)
        self.min_pat = int(min_pat)
        self.temp = float(temp)
        self.store: Dict[str, Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]] = {}

    def fit(self, triples: Sequence[Tuple[Optional[str], str, str]]) -> "HubComposedPredictor":
        pat_by_v: Dict[str, List[np.ndarray]] = defaultdict(list)
        A_by_v: Dict[str, List[np.ndarray]] = defaultdict(list)
        P_by_v: Dict[str, List[np.ndarray]] = defaultdict(list)
        for ag, v, pat in triples:
            pv = self.vec(pat)
            if pv is None:
                continue
            pat_by_v[v].append(pv)
            av = self.vec(ag) if ag is not None else None
            if av is not None:
                A_by_v[v].append(av)
                P_by_v[v].append(pv)
        for v, P in pat_by_v.items():
            if len(P) >= self.min_pat:
                A_cov = np.stack(A_by_v[v]) if A_by_v.get(v) else None
                P_cov = np.stack(P_by_v[v]) if P_by_v.get(v) else None
                self.store[v] = (np.stack(P), A_cov, P_cov)
        return self

    def has(self, verb: str) -> bool:
        return verb in self.store

    def count(self, verb: str) -> int:
        return int(self.store[verb][0].shape[0]) if verb in self.store else 0

    def precision(self, verb: str, role: str = "PATIENT") -> Optional[float]:
        """Selectional-preference concentration = mean cosine of the verb's patients to their centroid
        (the constraint sharpness the N400 precision-weighting scales by). None if the verb is unseen."""
        ex = self.store.get(verb)
        if ex is None:
            return None
        P = ex[0]
        c = P.mean(axis=0)
        cn = c / (np.linalg.norm(c) + _EPS)
        Pn = _cn(P)
        return float(np.mean(Pn @ cn))

    def score_pool(self, verb: str, agent_vec: Optional[np.ndarray], Cn: np.ndarray,
                   ashuffle_rng=None, verb_key: Optional[str] = None) -> np.ndarray:
        """Score each pool candidate (rows of Cn, L2-normalized): verb-prior centroid over ALL patients,
        precision-weighted agent-composed sharpening over the agent-covered exemplars, centroid backoff
        when the agent is OOV / uncovered / thin. Returns a length-|pool| score vector."""
        P_all, A_cov, P_cov = self.store[verb_key or verb]
        c = P_all.mean(axis=0)
        cent = Cn @ (c / (np.linalg.norm(c) + _EPS))
        if agent_vec is None or A_cov is None:
            return cent
        ac = A_cov @ agent_vec / (np.linalg.norm(A_cov, axis=1) * np.linalg.norm(agent_vec) + _EPS)
        peak = float(ac.max()) if len(ac) else 0.0
        if ashuffle_rng is not None:
            ac = ac[ashuffle_rng.permutation(len(ac))]
        w = np.maximum(ac, 0.0) ** self.gamma
        if w.sum() < _EPS:
            return cent
        Pn = _cn(P_cov)
        S = Cn @ Pn.T
        comp = (S * w[None, :]).sum(axis=1) / w.sum()
        if not self.precision:
            return comp
        lam = float(np.clip((peak - self.lam_lo) / (self.lam_hi - self.lam_lo + _EPS), 0.0, 1.0))
        return (1.0 - lam) * cent + lam * comp

    def surprisal(self, verb: str, role: str, actual: str, candidates: Sequence[str],
                  agent: Optional[str] = None, temp: Optional[float] = None) -> Optional[float]:
        """-log P(actual | softmax over the composed prediction) among the candidate heads (the N400
        read-out). `actual` is added to the pool if absent. Returns None if the verb is unseen or the
        actual head is OOV of the hub. role kept for API-compatibility (the store is patient-keyed)."""
        if verb not in self.store:
            return None
        cands = list(candidates)
        if actual not in cands:
            cands = [actual] + cands
        vecs = [self.vec(c) for c in cands]
        keep = [i for i, v in enumerate(vecs) if v is not None]
        if actual not in [cands[i] for i in keep]:
            return None
        pool = [cands[i] for i in keep]
        Cn = _cn(np.stack([vecs[i] for i in keep]))
        a_vec = self.vec(agent) if agent is not None else None
        scores = self.score_pool(verb, a_vec, Cn)
        t = self.temp if temp is None else float(temp)
        z = scores / max(t, _EPS)
        z = z - float(np.max(z))
        ez = np.exp(z)
        denom = float(np.sum(ez)) + _EPS
        ti = pool.index(actual)
        p_true = float(ez[ti]) / denom
        return -math.log(max(p_true, _EPS))

    @classmethod
    def load(cls, hub_path: str = HUB_ASSET, pred_path: str = PRED_ASSET) -> "HubComposedPredictor":
        """Reconstruct the fitted predictor from the offline-built static assets (the ~200-d hub vectors +
        the fitted per-verb store). Byte-faithful to fitting fresh (the store IS the fit)."""
        import pickle
        with open(hub_path, "rb") as fh:
            hub = pickle.load(fh)["hub"]
        with open(pred_path, "rb") as fh:
            d = pickle.load(fh)
        p = cls(vec=hub.get, gamma=d["gamma"], lam_lo=d["lam_lo"], lam_hi=d["lam_hi"],
                precision=d["precision"], min_pat=d["min_pat"], temp=d["temp"])
        p.store = d["store"]
        return p
