"""Graded cue-based competition -- the parser/role-assigner's maintained-distribution organ.

Landed 2026-08-27 (consolidation phase) from the integrated
`discrete_where_the_brain_is_graded_in_parsing_and_role_assignment` (SOLVED/EXCELLENT, owner-DONE; witness
`verify_graded_competition_parsing_role.py` PASS, re-verified first-hand). The substrate's parser and role
assigner make HARD, DISCRETE decisions (commit to one attachment / one role); the brain runs a GRADED,
PARALLEL, PROBABILISTIC competition and only collapses to one answer when a task presses. This organ is the
brain's version; the discrete organs are its noise->0 argmax COLLAPSE.

WHAT IS PINNED (copy the operation):
  * Sentence processing is graded parallel probabilistic constraint satisfaction / cue-based retrieval
    (MacDonald/Pearlmutter/Seidenberg 1994; Spivey-Knowlton 1996; Lewis & Vasishth 2005). Candidates compete
    via ADDITIVE cue activation  A_i = sum_c w_c * support_c(i)  (Lewis-Vasishth).
  * The combination rule ADDITIVE-activation -> SOFTMAX IS the Bayesian/FLMP posterior for DISCRETE cue
    integration (McClelland 2013: softmax units exactly compute Bayesian posteriors with
    net = log P(h) + sum log P(e|h); Massaro-Friedman FLMP for independent cues). So additive+softmax is the
    pinned posterior, NOT a convenient stand-in -- the COPIED operation.
  * The difficulty currency is the maintained distribution's normalized ENTROPY (Levy 2008: comprehension is a
    distribution over structures; difficulty = its relative entropy). HIGH entropy = genuine competition =
    hard/underspecified. VALIDATED: entropy predicts where the discrete rule ERRS (gold-free) +0.384 CI-sep,
    is higher on literature-hard object-extraction constructions (Gordon/Gibson), and BEATS the substrate's
    shipped BINARY route-conflict on real QA-SRL (AUC 0.646 vs 0.512). The info-free twins (random settling /
    shuffled cue validities) LOSE.
  * argmax is a TASK-TRIGGERED COLLAPSE, not the default output (Swets/Desmet/Clifton/Ferreira 2008): the
    native output is the DISTRIBUTION; the discrete resolver reads out only its argmax. `map_pick` reproduces
    the discrete fixed-priority resolver EXACTLY (graded argmax == discrete on every item -- a MAP-optimality
    THEOREM, Bishop 1.5), so graded competition CANNOT beat its own argmax on gold accuracy: its unique value
    is the DISTRIBUTION (uncertainty/difficulty/underspecification), NOT the point estimate. Wiring this is a
    FIDELITY + UNCERTAINTY win, NOT a gold-accuracy jump.

OUR-INVENTION-UNDER-TEST (swept, not adopted): the softmax `gain` (a PRECISION term -- reuse the
predictive-reader precision-weighting rather than a fixed constant); the per-cue weights (learned Competition-
Model cue VALIDITIES supplied by the caller); the settling `criterion`. The competition DYNAMICS (settling /
normalized-recurrence vs racing / LCA/ACT-R) is NEURALLY UNRESOLVED for sentence processing -- we STRADDLE it,
exposing BOTH the distributional entropy (race/Levy view) and normalized-recurrence cycles-to-settle
(settling/McRae view); they AGREE on the difficulty ordering.

DEFAULT-SAFE / ISLAND: this is a NEW module -- importing it changes NO existing behaviour. It operates on
ABSTRACT per-cue support arrays + cue weights (the caller supplies both), so it composes with any front-end.
Keep ATTACHMENT and ROLE BINDING as SEPARATE POOLS (Matchin-Hickok 2020 / Friederici 2011 / eADM) sharing this
activation FORM with distinct cue weights -- do NOT fuse them into one competition. The maintained-distribution
ENTROPY is the shared gold-free difficulty currency (the continuous generalization of the relcl binary
route-conflict, same currency as the predictive reader's surprisal + N400); wire it ONCE. MEASURE on the live
reader before any capability claim.
"""
from __future__ import annotations

from typing import Dict, Optional, Sequence, Tuple

import numpy as np

DEFAULT_GAIN = 2.0            # softmax gain (a PRECISION term -- swept, not adopted)
DEFAULT_CRITERION = 0.90     # normalized-recurrence settling criterion
DEFAULT_MAX_CYCLES = 100


def net_activation(supports: Dict[str, Sequence[float]], weights: Dict[str, float]) -> np.ndarray:
    """Additive Lewis-Vasishth activation over candidates: A_i = sum_c w_c * support_c(i).

    Cue-agnostic: iterates the `weights` keys; each named cue must have a per-candidate support array in
    `supports` (same length). A cue absent from `supports` or with zero weight does not vote."""
    if not weights:
        raise ValueError("net_activation requires at least one weighted cue")
    n = None
    for c in weights:
        if c in supports:
            n = len(supports[c])
            break
    if n is None:
        raise ValueError("none of the weighted cues has a support array in `supports`")
    A = np.zeros(n, dtype=np.float64)
    for c, w in weights.items():
        if w == 0.0 or c not in supports:
            continue
        s = np.asarray(supports[c], dtype=np.float64).reshape(-1)
        if s.shape[0] != n:
            raise ValueError(f"cue '{c}' support length {s.shape[0]} != {n}")
        A = A + float(w) * s
    return A


def softmax(x: Sequence[float], gain: float = DEFAULT_GAIN) -> np.ndarray:
    """Numerically stable softmax with a gain (precision) term. gain->inf concentrates on the argmax (the
    discrete collapse); gain->0 approaches uniform."""
    z = np.asarray(x, dtype=np.float64).reshape(-1)
    z = gain * (z - z.max())
    e = np.exp(z)
    return e / e.sum()


def normalized_recurrence(net: Sequence[float], gain: float = DEFAULT_GAIN,
                          criterion: float = DEFAULT_CRITERION,
                          max_cycles: int = DEFAULT_MAX_CYCLES) -> Tuple[int, int, float]:
    """Spivey-Knowlton normalized recurrence over N candidate interpretations: multiplicative recurrent
    feedback + normalization (mutual inhibition), settle to `criterion`. Returns
    (winner_index, cycles_to_settle, final_gap). The winner == argmax(net) (settling is monotone in net) -- the
    DISCRETE argmax in the noise->0 limit; cycles-to-settle is the SETTLING-view graded difficulty."""
    net = np.asarray(net, dtype=np.float64).reshape(-1)
    n = len(net)
    if n == 0:
        return -1, 0, 0.0
    if n == 1:
        return 0, 1, 1.0
    a = np.full(n, 1.0 / n, dtype=np.float64)
    # shift by min for overflow safety -- PRESERVES the activation GAPs (net_i - net_j), which drive settling
    # speed. Do NOT rescale by max (the range): that would normalise the gap away and flatten the difficulty
    # gradient (every item would settle at the same rate).
    net = net - net.min()
    for cyc in range(1, max_cycles + 1):
        a = a * np.exp(gain * net)
        a = a / a.sum()
        top = np.sort(a)[::-1]
        if top[0] >= criterion:
            return int(np.argmax(a)), cyc, float(top[0] - top[1])
    top = np.sort(a)[::-1]
    return int(np.argmax(a)), max_cycles, float(top[0] - top[1])


def graded_pick(supports: Dict[str, Sequence[float]], weights: Dict[str, float],
                gain: float = DEFAULT_GAIN) -> Dict:
    """Run the graded competition and return the MAINTAINED DISTRIBUTION over candidates plus its readouts.

    The native output of comprehension is a PROBABILITY DISTRIBUTION over candidate interpretations (Levy 2008;
    Swets 2008); the single discrete answer is its ARGMAX -- a later, TASK-TRIGGERED collapse. Returns:
      win     : argmax candidate (the task-triggered collapse = the discrete resolver's pick).
      p       : the maintained softmax distribution over candidates (the native graded output).
      entropy : NORMALIZED Shannon entropy H/log(n) in [0,1] -- HIGH = ambiguous/underspecified = hard
                (candidate-count-robust; the Levy-faithful gold-free difficulty currency).
      margin  : top1-top2 of the raw additive activation (a monotone continuous competition margin).
      cycles  : Spivey-Knowlton normalized-recurrence cycles-to-settle (the settling-time difficulty).
    Takes NO gold/labels -- glass-box."""
    net = net_activation(supports, weights)
    n = len(net)
    if n == 0:
        return {"win": -1, "p": np.array([]), "entropy": 0.0, "margin": 0.0, "cycles": 0}
    if n == 1:
        return {"win": 0, "p": np.array([1.0]), "entropy": 0.0, "margin": float(net[0] + 1.0), "cycles": 1}
    p = softmax(net, gain)
    ent = float(-(p * np.log(p + 1e-12)).sum() / np.log(n))   # normalized entropy in [0,1]
    order = np.sort(net)[::-1]
    margin = float(order[0] - order[1])
    win, cycles, _gap = normalized_recurrence(net, gain=gain)
    return {"win": int(np.argmax(net)), "p": p, "entropy": ent, "margin": margin, "cycles": int(cycles)}


def map_pick(supports: Dict[str, Sequence[float]], weights: Dict[str, float]) -> int:
    """The MAP / argmax point estimate -- the DISCRETE resolver's pick, the noise->0 collapse of the graded
    distribution. By MAP-optimality this is the accuracy-optimal single answer; graded competition cannot beat
    it on gold accuracy (its value is the distribution, not the point estimate)."""
    net = net_activation(supports, weights)
    return int(np.argmax(net)) if len(net) else -1


def difficulty(supports: Dict[str, Sequence[float]], weights: Dict[str, float],
               gain: float = DEFAULT_GAIN) -> float:
    """The shared gold-free DIFFICULTY currency = the maintained distribution's normalized entropy in [0,1].
    HIGH = the argmax is on shaky ground. The continuous generalization of the binary route-conflict; the same
    currency as the predictive reader's surprisal and the N400 -- wire it ONCE across those consumers."""
    return float(graded_pick(supports, weights, gain=gain)["entropy"])


__all__ = ["net_activation", "softmax", "normalized_recurrence", "graded_pick", "map_pick",
           "difficulty", "DEFAULT_GAIN", "DEFAULT_CRITERION", "DEFAULT_MAX_CYCLES"]
