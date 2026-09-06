"""hdlab.theory_of_mind -- the glass-box FORWARD mentalizing chain: believes(A,F,t) x wants(A) -> action.

THE ORGAN (owner-DONE chain_belief_and_goal_into_theory_of_mind_inference_intention_and_false_belief, Q111).
The reader stores per-agent BELIEF (hdlab.belief_timeline, the rTPJ/mPFC mentalizing register, Saxe & Kanwisher
2003) and per-agent GOALS (hdlab.goal_register, the dmPFC intention register) but never CHAINED them into
"given what X believes and wants, what will X do?". This module is that composition -- a transparent,
hand-auditable forward inverse-planning step, NO external LLM at inference.

THE COMPUTATION (PINNED -- Bayesian Theory of Mind / inverse planning run FORWARD; Baker, Saxe & Tenenbaum
2009/2011/2017; Jara-Ettinger naive utility calculus 2016; Leslie 1987 meta-representation; Wimmer & Perner
1983 seeing->knowing):
  An agent selects the action that best achieves its DESIRE given its BELIEF about the world. The observer
  predicts the action by running that planner FORWARD over the agent's (possibly FALSE) BELIEF state, NOT
  reality. For the single-goal narrative case the soft-max policy collapses to ARGMAX over the believed
  goal-value (argmax = the high-beta limit of the pinned softmax). So:
      believed = belief_at_T(A, F)              # the agent's believed value of the goal-relevant fact (rTPJ)
      desire   = the value A wants F to have     # from the goal register (dmPFC)
      action   = PROCEED (use F as-is) if believed == desire   # A thinks F already satisfies the goal
                 else FETCH (go correct/obtain the desired)     # A thinks F does not satisfy the goal
  FALSE BELIEF falls out for free: where believed != reality (A missed the change), the belief-driven action
  DIVERGES from the reality-driven one -- and only the belief-driven one is right. Because the chain reads
  believes(A,F,t) and NOT reality_at(F,t), the meta-representational (false-belief) case is handled by the
  same rule as the true-belief case (Leslie 1987 -- one representation of the agent's representation).

BIDIRECTIONAL (Baker/Saxe/Tenenbaum 2017): a fully brain-foundational ToM computation is ONE generative
planner used both ways -- FORWARD to PREDICT an action, INVERSE to ATTRIBUTE the belief that rationalizes an
observed action (the intentional stance). `attribute_belief_from_action` is the exact inverse of
`forward_action`: one engine, both directions.

TWO UPSTREAM BRAIN-FOUNDATIONAL READING PIECES this organ carries (register-generalizations of the brain's
SAME operations, NOT new mechanisms; diagnosed inert without them on modern content-change ToM prose):
  (1) PRESENT-TENSE percept gate (`perceives_change`) -- a register-generalization of the PerceptualAccessLedger
      RULE-0 explicit-epistemic lexicon (which is 19c/past-tense: "saw"/"did not see"). BigToM is present-tense
      modern prose ("sees"/"does not see"); the gate reads whether the narrator states the agent perceived the
      change (Wimmer & Perner 1983 seeing->knowing). True -> the belief updates; False/unaware -> it freezes
      (the false belief).
  (2) CHANGE-OF-STATE / substitution reality cues (`_COS_CUES`) -- the belief PERCEPTION channel's resultant
      extractor generalized from object-MOVES + copular STATUS to content/state changes ("swap/replace X with
      Y", causative "rainfall opens the valve", "leaving the pot empty"). Dowty 1979 inchoative/resultant; the
      state_register organ's change-of-state territory.

MEASURED (BigToM, Gandhi et al. 2023, MODERN peer-reviewed ToM gold, 278 items): belief-prediction CHAIN 0.849
vs reality-only floor 0.500 (+0.349 CI-sep); the load-bearing FALSE-belief subset +0.871 (floor provably 0.000);
both info-free twins (percept-shuffle, belief-shuffle) LOSE CI-sep; composition EXACT with oracle belief (1.000)
-> the residual is EXTRACTION, not the inference rule.

REUSE, not rebuild: this organ COMPOSES the promoted hdlab.belief_timeline (sample-and-hold belief_at_T) and
hdlab.goal_register (the desire). It defines NO new register -- only the forward/inverse composition rules + the
two upstream reading generalizations. The BigToM item-coupled measurement glue (initial-belief / reality-change
/ desire extraction over the BigToM value model) lives in experiments/_tom_chain.py, which imports these organ
functions. Glass-box, NO external LLM at inference. ASCII only. Deterministic.
"""
from __future__ import annotations

import re
from typing import Optional, Sequence

# REUSE the promoted registers (do NOT rebuild): belief_timeline = the per-agent sample-and-hold belief
# (rTPJ/mPFC); the goal register (dmPFC desire) is consumed live via sm.wants at the SituationReader read-out.
from hdlab.belief_timeline import WorldEvent, timeline_belief, reality_at  # noqa: F401  (reused organ surface)


# ---------------------------------------------------------------------------
# (upstream 2) PRESENT-TENSE percept gate -- a register-generalization of PAL RULE-0 (_epistemic_patterns).
# ---------------------------------------------------------------------------
_PERCEIVE = (r"see|sees|saw|seeing|watch|watches|watched|watching|notice|notices|noticed|noticing|"
             r"observe|observes|observed|observing|witness|witnesses|witnessed|perceive|perceives|perceived|"
             r"spot|spots|spotted|hear|hears|heard|realize|realizes|realized|realise|realises|realised|"
             r"aware")
_NEG = r"(?:not|n't|never|fails? to|failed to|without|unable to|cannot|can't|does not|doesn't|did not|didn't|is not|isn't)"


def perceives_change(percept_sentence: str, agent_aliases: Sequence[str]) -> Optional[bool]:
    """Present-tense explicit epistemic gate: does the narrator state the agent perceived the change?
    Returns True (X sees ...), False (X does not see ... / unaware / unbeknownst), or None (no explicit cue)."""
    s = percept_sentence
    low = s.lower()
    a = "(?:" + "|".join(sorted({re.escape(al.lower()) for al in agent_aliases if al}, key=len, reverse=True)
                         + ["he", "she", "they", "it"]) + ")"
    # explicit NON-perception (negation before/around the perception verb) -> False
    neg_pats = [rf"\b{a}\b[^.]*?\b{_NEG}\b[^.]*?\b(?:{_PERCEIVE})\b",
                rf"\bunbeknownst? to\b", rf"\bunknown to\b", rf"\bwithout\b[^.]*?\bknow(?:ing|ledge)\b",
                rf"\b{a}\b[^.]*?\b(?:unaware|oblivious|ignorant)\b",
                rf"\b{a}\b[^.]*?\b(?:remains?|stays?|is|are)\b[^.]*?\bunaware\b"]
    for p in neg_pats:
        if re.search(p, low):
            return False
    # explicit perception -> True
    if re.search(rf"\b{a}\b[^.]*?\b(?:{_PERCEIVE})\b", low):
        return True
    return None


# ---------------------------------------------------------------------------
# (upstream 1) CHANGE-OF-STATE / SUBSTITUTION reality cues (belief PERCEPTION channel).
# ---------------------------------------------------------------------------
# Change-of-state / substitution / causative cues that RESULT IN F taking a new value (Dowty inchoative +
# Levin change-of-state / put / swap-substitution classes). Lemma-ish surface forms; the RESULTANT value is
# read from the candidate tokens present in the clause (the new state the change leaves F in).
_COS_CUES = {
    "swap", "swaps", "swapped", "replace", "replaces", "replaced", "switch", "switches", "switched",
    "exchange", "exchanges", "exchanged", "substitute", "substitutes", "substituted",
    "knock", "knocks", "knocked", "spill", "spills", "spilled", "spilling", "tear", "tears", "tearing",
    "torn", "break", "breaks", "broke", "broken", "crush", "crushes", "crushing", "crushed",
    "damage", "damages", "damaged", "damaging", "wilt", "wilts", "wilted", "wilting", "soak", "soaks",
    "soaked", "leak", "leaks", "leaked", "leaking", "wash", "washes", "washed", "washing", "consume",
    "consumes", "consumed", "leaving", "leaves", "left", "making", "makes", "made", "becoming", "becomes",
    "become", "became", "turn", "turns", "turned", "turning", "rise", "rises", "rose", "rising", "risen",
    "blow", "blows", "blew", "blown", "blowing", "reveal", "reveals", "revealing", "revealed", "place",
    "places", "placed", "put", "puts", "fill", "fills", "filled", "filling", "overflow", "overflows",
    "overflowing", "melt", "melts", "melted", "freeze", "freezes", "froze", "frozen", "spoil", "spoils",
    "spoiled", "contaminate", "contaminates", "contaminated", "empty", "empties", "emptied", "remove",
    "removes", "removed", "removing", "cause", "causes", "caused", "causing", "add", "adds", "added",
    "mix", "mixes", "mixed", "drop", "drops", "dropped", "shatter", "shatters", "shattered", "arrive",
    "arrives", "arrived", "dry", "dries", "dried", "rot", "rots", "rotted", "collapse", "collapses",
    "collapsed", "burn", "burns", "burned", "burnt", "flood", "floods", "flooded", "grow", "grows", "grew",
}


# ---------------------------------------------------------------------------
# The forward composition -> an action class (INDEX space -- the canonical rule the BigToM measurement uses).
# ---------------------------------------------------------------------------
def forward_action(believed_idx: Optional[int], desire_idx: Optional[int]) -> Optional[str]:
    """PROCEED (use F as-is) if the agent believes F already satisfies the goal, else FETCH (go correct/obtain)."""
    if believed_idx is None or desire_idx is None:
        return None
    return "PROCEED" if believed_idx == desire_idx else "FETCH"


def attribute_belief_from_action(observed_action: Optional[str], desire_idx: Optional[int]) -> Optional[int]:
    """INVERSE planning (Baker/Saxe/Tenenbaum 2017 attribution): the SAME forward planner run BACKWARD -- observe
    what the agent DID and attribute the BELIEF that rationalizes it given the desire. If the agent PROCEEDED
    (used F as-is), it must believe F satisfies the goal -> believed == desire; if it went to FETCH/correct, it
    believes F does NOT satisfy the goal -> believed == the OTHER candidate. This is the exact inverse of
    forward_action: one engine, both directions (the bidirectional mentalizing computation)."""
    if observed_action is None or desire_idx is None:
        return None
    return desire_idx if observed_action == "PROCEED" else (1 - desire_idx)


# ---------------------------------------------------------------------------
# VALUE-space read-out (the generic SituationReader.read() consumer): sm.believes returns a VALUE string and
# sm.wants a goal text, so the live wire composes VALUES rather than candidate indices. Same rule.
# ---------------------------------------------------------------------------
def compose_action(believed_value, desired_value) -> Optional[str]:
    """Value-space twin of forward_action for the LIVE reader read-out. PROCEED if the agent BELIEVES F already
    has the value it WANTS (act off the believed state), else FETCH. None if either value is unknown. Acting
    off `believed_value` (not reality) is exactly what makes the false-belief case come out right."""
    if believed_value is None or desired_value is None:
        return None
    return "PROCEED" if str(believed_value).strip().lower() == str(desired_value).strip().lower() else "FETCH"


def attribute_belief_value(observed_action: Optional[str], desired_value, other_value=None):
    """Value-space inverse of compose_action: from the observed action attribute the believed VALUE. PROCEED ->
    believed == the desired value; FETCH -> believed == the OTHER candidate value of the (binary) fact (None if
    that other value is not supplied)."""
    if observed_action is None or desired_value is None:
        return None
    return desired_value if observed_action == "PROCEED" else other_value


# ---------------------------------------------------------------------------
# Timeline-composing convenience (index space) -- makes the REUSE of belief_timeline explicit: read the agent's
# believed value at t off the promoted sample-and-hold, then compose forward.
# ---------------------------------------------------------------------------
def predict_action_over_timeline(events, observed, agent: str, obj: str, t: float,
                                 desire_idx: Optional[int]):
    """FORWARD ToM over the promoted hdlab.belief_timeline (REUSE, not rebuild): read belief_at_T (sample-and-hold
    over OBSERVED events -- the false belief falls out when an unobserved change leaves the belief stale), then
    compose with the desire. Returns (believed_idx, action_class)."""
    val = timeline_belief(events, observed, agent, obj, float(t))
    believed_idx = int(val) if val is not None else None
    return believed_idx, forward_action(believed_idx, desire_idx)
