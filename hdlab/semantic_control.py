"""Semantic control -- the LIFG/pMTG conflict-gated suppression organ.

Landed 2026-08-27 from the integrated `context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark`
(SOLVED/EXCELLENT, owner-DONE; witness test_context_override_frequency.py PASS). The substrate's
identified MISSING organ: the reader had the look-up (reordered-access read: a frequency prior +
a context likelihood over candidate senses/interpretations) but not the CONTROL that actively
SUPPRESSES the habitual (dominant/prior) candidate when the context supports a competitor.

WHAT IS PINNED (copy the operation): semantic control resolves competition using CONTEXT (IFG/pMTG;
Thompson-Schill; Jefferies controlled semantic cognition). The GOLD-BLIND two-sided CONFLICT signal is
    conflict = max_{s != prior} coh(context, s)  -  coh(context, prior)
i.e. "does some non-prior candidate fit this context better than the prior one?". When conflict exceeds
threshold theta, GRADED suppression of the prior candidate fires:
    score[prior] -= gamma * relu(conflict - theta)
and the re-argmax picks the context-appropriate competitor. VALIDATED on modern SemCor: the trigger
predicts "the prior is wrong" gold-blind at AUC 0.79-0.81 (a SHUFFLED-context twin at 0.58); gated
suppression is net-positive CI-separated and lifts the frequency-OVERRIDE cases +0.007-0.033, the gain
attributable to the REAL trigger (an info-free shuffled-trigger twin loses).

OUR-INVENTION-UNDER-TEST (swept, not adopted): the threshold theta (calibrate on a dev batch -- the
validated headline is the 80th percentile of the conflict distribution) and the strength gamma
(validated headline 1.0). A better/lightly-learned TRIGGER is the forward lever (drill: unfitted/fitted
combiners of the current signals HURT; a genuinely new orthogonal directional signal is the direction).

DEFAULT-SAFE / ISLAND: importing this changes NO existing behaviour. It operates on ABSTRACT per-candidate
scores + a per-candidate context-coherence array + which candidate is the prior -- so it composes with any
meaning read-out (it is the ROUTER/gate the conceptual-meaning-channel work routes between the associative
and conceptual channels). Do NOT wire settling (formally == argmax) or diagnosticity word-weighting (null).
The net gain is MODEST + trigger-quality-limited (quote the trigger AUC + the override-case gain, not an
aggregate WSD lift). MEASURE on the live reading task before any capability claim.
"""
from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np

DEFAULT_QUANTILE = 0.80  # validated headline operating point (NOT tuned to gold)
DEFAULT_GAMMA = 1.0


def _relu(x: float) -> float:
    return x if x > 0.0 else 0.0


def conflict(coherences: Sequence[float], prior_idx: int) -> float:
    """The gold-blind two-sided conflict signal: the best NON-prior candidate's context-coherence
    minus the prior candidate's. High => 'the prior is probably wrong here'."""
    coh = np.asarray(coherences, dtype=np.float64).reshape(-1)
    if coh.size < 2:
        return 0.0
    best_other = float(np.delete(coh, prior_idx).max())
    return best_other - float(coh[prior_idx])


class SemanticControl:
    """Conflict-gated graded suppression of the prior/dominant candidate.

    theta: the conflict threshold. If None, fires never (default-safe no-op) until `calibrate`d on a
           batch of conflict values (or set explicitly). gamma: suppression strength.
    """

    def __init__(self, theta: Optional[float] = None, gamma: float = DEFAULT_GAMMA):
        self.theta = None if theta is None else float(theta)
        self.gamma = float(gamma)

    def calibrate(self, conflicts: Sequence[float], quantile: float = DEFAULT_QUANTILE) -> "SemanticControl":
        """Set theta to a quantile of the conflict distribution over a dev batch (the validated
        headline is the 80th percentile -- suppress only the top-conflict items)."""
        c = np.asarray(conflicts, dtype=np.float64).reshape(-1)
        self.theta = float(np.quantile(c, quantile)) if c.size else None
        return self

    def fires(self, conflict_value: float) -> bool:
        return self.theta is not None and conflict_value > self.theta

    def suppressed_scores(self, scores: Sequence[float], prior_idx: int, conflict_value: float) -> np.ndarray:
        """Return the candidate scores with the prior GRADED-suppressed by
        gamma*relu(conflict - theta). No-op if theta is None (uncalibrated) -- default-safe."""
        out = np.asarray(scores, dtype=np.float64).reshape(-1).copy()
        theta = self.theta
        if theta is None:
            return out
        out[prior_idx] -= self.gamma * _relu(conflict_value - theta)
        return out

    def resolve(self, scores: Sequence[float], coherences: Sequence[float],
                prior_idx: int) -> Tuple[int, float]:
        """Compute the conflict from the context-coherences, apply gated suppression to the base
        `scores` (any read-out: a reordered-access frequency+context read), and return
        (argmax_index, conflict_value). If uncalibrated (theta None) this is exactly argmax(scores)."""
        c = conflict(coherences, prior_idx)
        supp = self.suppressed_scores(scores, prior_idx, c)
        return int(np.argmax(supp)), c


# ---------------------------------------------------------------------------------------------------
# BRAIN-FAITHFUL REORDERED-ACCESS ADDITIVE read-out (landed 2026-09-03 from the owner-DONE north-star
# the_meaning_channel_needs_a_generative_world_knowledge_situation_model...). The parent's net-gain
# see-saw was NOT the generative source -- it was the DECISION RULE: a SUBTRACTIVE/gated hard-flip
# (like `resolve`'s suppression, or the parent's argmax override) can ERASE a correct dominant sense
# (Duffy/Morris/Rayner reordered access is ADDITIVE: the dominant is ALWAYS accessed by frequency;
# context only ADDS activation to a subordinate, never subtracts from the dominant), and using the
# posterior's own margin as confidence rewards a false-confident peak (Feldman-Friston: precision is
# EXPECTED reliability estimated from OTHER variables -- here context richness, NON-margin). This
# additive, facilitatory-only, non-margin-precision rule is the GENERALIZING net-gain lever: on held-out
# SemCor it nets +0.0116 over the MFS floor CI-separated (twin loses, dominant preserved 0.949) where the
# parent's gated hard-flip was -0.0013 CI-sep BELOW. Promoted VERBATIM from the validated
# experiments/exp_generative_situation_sense_selector_v2._additive_pick (+ _z/_margin) so a wired read is
# byte-exact to the witnessed cell. DEFAULT-SAFE: a NEW read-out; importing/using it does not change
# `resolve`/`conflict`/`suppressed_scores`. spaCy-free, LM-free. MEASURE on the live task before a claim.


def _z(a) -> np.ndarray:
    a = np.asarray(a, float)
    s = a.std()
    return (a - a.mean()) / s if s > 1e-12 else np.zeros(len(a))


def _margin(likelihood) -> float:
    """top1-top2 relative gap of the context likelihood -- used ONLY as an abstention gate (a totally
    flat context must not override), NOT as the confidence weight (that is the non-margin reliability)."""
    s = np.sort(np.asarray(likelihood, float))[::-1]
    return float((s[0] - s[1]) / (s[0] + 1e-9)) if len(s) > 1 else 0.0


def additive_reordered_read(prior, likelihood, reliability: float = 1.0,
                            gamma: float = DEFAULT_GAMMA, tau: float = 0.0) -> int:
    """The brain-faithful reordered-access ADDITIVE sense pick (byte-exact to the validated
    exp_generative_situation_sense_selector_v2._additive_pick):
        score(s) = log(prior(s)) + gamma * reliability * relu(z(likelihood)(s))
    argmax over senses. `prior` = frequency prior over candidate senses; `likelihood` = the context
    signal over the SAME senses (None or margin<tau => abstain to the dominant/prior argmax); `reliability`
    = expected non-margin context richness in [0,1] (Feldman-Friston precision, NOT the posterior margin).
    Context can only ADD activation to context-supported senses; the dominant is NEVER penalized (no
    see-saw). Deterministic, numpy-only. This is the net-gain read-out; `resolve` remains the (suppressive)
    conflict-gate for callers that want it."""
    pr = np.asarray(prior, float)
    pr = pr / pr.sum()
    if likelihood is None or _margin(likelihood) < tau:
        return int(np.argmax(pr))
    boost = gamma * float(reliability) * np.maximum(_z(np.asarray(likelihood, float)), 0.0)
    return int(np.argmax(np.log(pr + 1e-6) + boost))


__all__ = ["SemanticControl", "conflict", "additive_reordered_read", "DEFAULT_QUANTILE", "DEFAULT_GAMMA"]
