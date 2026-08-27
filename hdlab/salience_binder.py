"""Salience binder -- ACT-R base-level activation + Centering grammatical prominence; graded (Nref) write.

Landed 2026-08-27 (consolidation phase) from two integrated results: `entity_binding_needs_a_modern_pronoun_corpus`
(the BIND half -- who a pronoun refers to) and `wire_entity_tracking_end_to_end_on_running_narrative` (the graded
write). Both SOLVED/EXCELLENT, owner-DONE; witnesses re-verified first-hand.

WHAT IS PINNED (copy the operation):
  * Resolving a pronoun binds it to the most SALIENT compatible entity, and salience is ACT-R BASE-LEVEL
    ACTIVATION (Anderson & Schooler 1991; ACT-R declarative retrieval): B = ln( sum_k w(role_k) * dt_k^-decay )
    over the entity's prior mentions -- a log-sum of power-law-decayed past uses, weighted by GRAMMATICAL
    PROMINENCE. The prominence weights are Centering theory's Cf-ranking (SUBJECT > POSSESSIVE > OBJECT >
    OTHER). VALIDATED on GAP (human-labeled same-gender ambiguous pronouns): 0.699 vs string-identity 0.508,
    recency 0.514, shuffled-salience twin 0.490 (all CI-sep). **KEY: on the HARD ambiguous cases RECENCY IS AT
    CHANCE -- the load-bearing cue is grammatical PROMINENCE, not recency** (binding is structural/salience,
    NOT semantic: implicit-causality does not replicate). The unifying scalar (prominence+recency+frequency)
    is the ACT-R base-level equation, beating the live salience() +0.213.
  * The pronoun WRITE into the entity store is GRADED, not hard-argmax: distribute the event across the
    compatible candidates by softmax(activation / temp) -- the Nref-faithful "hold candidates open under
    ambiguity" (a sustained anterior negativity = multiple candidates active under WM load). VALIDATED: graded
    write beats hard argmax on downstream who-did-what recall +0.0268 CI-sep, and a UNIFORM-weight control is
    WORSE than hard -> it is the ACTIVATION weighting that carries it. A temperature sweep is a textbook
    INTERIOR OPTIMUM (peak temp~2.0; both winner-take-all and uniform are worse) = the DIVISIVE-NORMALIZATION
    family (Carandini & Heeger 2012: a^n/(sigma^n+sum a^n) nests uniform/graded/argmax; intermediate = the
    canonical cortical computation). **The SHAPE (intermediate activation-weighted competition) is pinned; the
    temperature is a fitted parameter (no biological constant).**

BRAIN-FOUNDATIONAL COHERENCE (one operation, reused): the graded write's softmax(activation/temp) IS the SAME
divisive-normalization operation as the parser's role competition -- Lewis & Vasishth (2005) cue-based retrieval
is itself an ACT-R model. So `graded_write` REUSES `hdlab.graded_competition.softmax` (gain = 1/temp) rather
than re-implementing it. Both the parser role-competition and the entity-binding write are activation-based
competitive retrieval under divisive normalization.

OUR-INVENTION-UNDER-TEST (swept, not adopted): the decay `d` (held-out d*=2.0), the write temperature `temp`
(interior-optimum peak ~2.0 on LitBank), the exact prominence weights.

DISSOCIATION (do NOT cross the channels): BINDING is salience (this organ); PREDICTING what an entity does next
is content-addressable retrieval (a different channel). Keep salience for the pronoun pick, content for
prediction. And correct pronoun linking buys cross-sentence ATTRIBUTION (retrievable history), NOT a predictive
prior -- wire this for "what did X do" retrieval, not as an entity-conditioned predictor on running narrative.

DEFAULT-SAFE / ISLAND: a NEW module -- importing it changes NO existing behaviour. Representation-agnostic: the
caller supplies the agreement-compatible candidate set (each candidate = its mention history of (time, role))
and the query time; agreement/gender filtering stays with the caller. `bind` is the hard argmax collapse (the
current default); `graded_write` is the Nref-faithful distribution. MEASURE on the live reader before any claim.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from hdlab.graded_competition import softmax as _dn_softmax  # the shared divisive-normalization op

# Centering Cf-ranking / grammatical prominence weights (the load-bearing cue; recency is at chance on hard cases)
ROLE_PROMINENCE: Dict[str, float] = {"SUBJECT": 4.0, "POSSESSIVE": 2.5, "OBJECT": 2.0, "OTHER": 1.0}
DEFAULT_DECAY = 2.0     # ACT-R base-level decay (held-out d*)
DEFAULT_TEMP = 2.0      # graded-write temperature (interior-optimum peak on LitBank; a fitted parameter)

History = Sequence[Tuple[float, str]]   # a candidate entity's prior mentions: (time, role)


def _dt(now: float, t: float) -> float:
    """Temporal distance (>=1 so 1^-d is finite): now - t + 1, floored at 1."""
    return float(max(1.0, now - t + 1.0))


def actr_activation(history: History, now: float, decay: float = DEFAULT_DECAY,
                    role_prominence: Optional[Dict[str, float]] = None) -> float:
    """ACT-R base-level activation of one candidate entity at time `now`:
        B = ln( sum_k w(role_k) * dt_k^-decay )   over the candidate's prior mentions (time_k, role_k),
    with w = grammatical prominence (Centering Cf-ranking). An empty history -> -inf (no evidence). This is the
    log-sum of power-law-decayed, prominence-weighted past uses (Anderson & Schooler 1991)."""
    rp = ROLE_PROMINENCE if role_prominence is None else role_prominence
    s = 0.0
    for t, role in history:
        s += rp.get(role, 1.0) * (_dt(now, t) ** (-decay))
    return math.log(s) if s > 0.0 else float("-inf")


def activations(candidates: Sequence[History], now: float, decay: float = DEFAULT_DECAY,
                role_prominence: Optional[Dict[str, float]] = None) -> np.ndarray:
    """The ACT-R base-level activation of every compatible candidate (in the caller's candidate order)."""
    return np.array([actr_activation(h, now, decay, role_prominence) for h in candidates], dtype=np.float64)


def bind(candidates: Sequence[History], now: float, decay: float = DEFAULT_DECAY,
         role_prominence: Optional[Dict[str, float]] = None) -> int:
    """Hard bind: the argmax ACT-R activation (the current default / task-triggered collapse). Ties -> lowest
    index. Returns the index into `candidates` (-1 if there are no candidates). Takes NO gold."""
    if not len(candidates):
        return -1
    acts = activations(candidates, now, decay, role_prominence)
    best = int(np.argmax(acts))
    # np.argmax already returns the FIRST max on ties -> lowest index, matching the validated binder
    return best


def graded_write(candidates: Sequence[History], now: float, decay: float = DEFAULT_DECAY,
                 temp: float = DEFAULT_TEMP,
                 role_prominence: Optional[Dict[str, float]] = None) -> List[Tuple[int, float]]:
    """Nref-faithful GRADED write: distribute a pronoun's event across the compatible candidates by
    softmax(activation / temp) -- the divisive-normalization interior optimum. Returns [(index, weight), ...]
    over `candidates` (weights sum to 1). REUSES the shared divisive-normalization softmax (gain = 1/temp), the
    SAME operation as the parser's role competition. The hard bind is its argmax."""
    n = len(candidates)
    if n == 0:
        return []
    if n == 1:
        return [(0, 1.0)]
    acts = activations(candidates, now, decay, role_prominence)
    w = _dn_softmax(acts, gain=1.0 / max(temp, 1e-6))
    return [(i, float(w[i])) for i in range(n)]


__all__ = ["actr_activation", "activations", "bind", "graded_write",
           "ROLE_PROMINENCE", "DEFAULT_DECAY", "DEFAULT_TEMP"]
