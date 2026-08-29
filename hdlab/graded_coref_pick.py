"""graded_coref_pick -- brain-faithful GRADED cue-based ANTECEDENT retrieval (the coref pronoun-resolution core).

Landed 2026-08-28 from the integrated `coreference_is_capped_at_065_on_real_narrative` (SOLVED/EXCELLENT, owner-DONE):
the reusable CORE computation that replaced the reader's rigid hard-tiered pronoun pick with the brain's actual
reference mechanism -- GRADED cue-based retrieval (Lewis & Vasishth 2005; McElree 2003). Over the gn-compatible
candidate antecedents, competing GRADED cue activations (recency, subjecthood/Cf-prominence, backward-center Cb,
frequency/topichood, first-mention, parallelism, and the pinned ACT-R base-level activation) are combined by the
substrate's own `graded_competition` into a softmax posterior; its argmax is the pick and its normalized ENTROPY is a
calibrated, gold-free ABSTAIN signal ("cues conflict -> flat posterior -> defer"; the brain's Nref "hold both", Nieuwland
& Van Berkum 2008). On real narrative this beats the incumbent hard subject-first tier +0.172 CI-sep and its entropy
predicts its own errors AUC 0.806 (the shipped result; this module is the mechanism, mechanism-witnessed here).

PINNED (copied): the retrieval CURRENCY is the ACT-R base-level activation A_i = ln(sum_k w_role(k)*dt_k^-d)
(recency x frequency x role prominence; Anderson; Lewis & Vasishth), read out by the graded competition's softmax.
OUR-INVENTION-UNDER-TEST (swept, DEV-tuned): the per-cue WEIGHTS (Competition-Model cue validities) and the softmax GAIN
(a precision term -- gain-invariant for the argmax, so it only sharpens the entropy). COPY the operation; sweep the
params.

spaCy-FREE: the caller supplies each candidate's prior-mention list as (sentence_index, role) tuples (role in
{"SUBJECT","POSSESSIVE","OBJECT","OTHER"}) from whatever parse it has; this is pure numeric competition, no LLM at
inference (the invariant). The RESOLVER-STREAM wiring (an opt-in run_graded_retrieval over coreference_resolver's
TrackedEntity stream) is a queued follow-on; this is the store-agnostic scoring core any caller can use.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .graded_competition import graded_pick

# Per-mention grammatical-role strength (Cf prominence; the ACT-R role term). From the landed activation binder.
ROLE_W = {"SUBJECT": 4.0, "POSSESSIVE": 2.5, "OBJECT": 2.0, "OTHER": 1.0}

# DEV-tuned defaults reported on TEST (OUR-INVENTION-UNDER-TEST; the winning config is ACT-R activation + a light
# subjecthood term -- the retrieval currency dominates, the Centering geometry cues are light additive terms).
TUNED_WEIGHTS: Dict[str, float] = {"recency": 0.0, "subject": 0.25, "cb": 0.0,
                                   "freq": 0.0, "first": 0.0, "parallel": 0.0, "actr": 1.5}
DEFAULT_GAIN = 8.0     # softmax gain (precision term; gain-invariant for argmax, sharpens the entropy/abstain)
DEFAULT_ACTR_D = 3.0   # ACT-R decay exponent (swept on DEV, not adopted)

_CUES = ("recency", "subject", "cb", "freq", "first", "parallel")


def _dt(p_sent: int, m_sent: int) -> float:
    """Sentence distance >= 1 (avoids 0^-d): how far back the mention is from the pronoun clause."""
    return float(max(1, p_sent - m_sent + 1))


def _zscore(v: np.ndarray) -> np.ndarray:
    s = v.std()
    return (v - v.mean()) / s if s > 1e-12 else np.zeros_like(v)


def graded_antecedent_pick(
    candidate_priors: Sequence[Sequence[Tuple[int, str]]],
    p_sent: int,
    pron_role: str = "OTHER",
    weights: Optional[Dict[str, float]] = None,
    gain: float = DEFAULT_GAIN,
    d: float = DEFAULT_ACTR_D,
) -> Dict[str, float]:
    """Graded cue-based antecedent retrieval over the gn-compatible candidates.

    candidate_priors: one entry per candidate = its list of prior mentions [(sentence_index, role), ...]
                      (role in {"SUBJECT","POSSESSIVE","OBJECT","OTHER"}); the caller pre-filters to gn-compatibles.
    p_sent: the pronoun clause's sentence index. pron_role: the pronoun's own grammatical role (for the parallelism cue).
    Returns {"pick": winning candidate INDEX (into candidate_priors), "entropy": normalized posterior entropy (the
    gold-free ABSTAIN signal; high = genuine competition -> defer), "margin": top1-top2 posterior gap}.
    """
    weights = TUNED_WEIGHTS if weights is None else weights
    n = len(candidate_priors)
    if n == 0:
        return {"pick": -1, "entropy": 0.0, "margin": 0.0}
    if n == 1:
        return {"pick": 0, "entropy": 0.0, "margin": 1.0}

    # backward-looking center: the most-recent PRIOR sentence any candidate occupied (< pronoun clause)
    prev_sent = max((s for pri in candidate_priors for (s, _r) in pri if s < p_sent), default=None)
    earliest = [min(s for s, _r in pri) for pri in candidate_priors]
    first_sent = min(earliest)

    rec, subj, cb, freq, first, par, actr = [], [], [], [], [], [], []
    for i, pri in enumerate(candidate_priors):
        nearest = min(_dt(p_sent, s) for s, _r in pri)
        rec.append(1.0 / nearest)                                        # recency: closer -> higher
        subj.append(max(ROLE_W.get(r, 1.0) for _s, r in pri))           # Cf prominence (subjecthood)
        cb.append(1.0 if any(s == prev_sent and r == "SUBJECT" for s, r in pri) else 0.0)  # backward center
        freq.append(math.log1p(len(pri)))                               # base-level frequency / topichood
        first.append(1.0 if earliest[i] == first_sent else 0.0)         # advantage-of-first-mention
        last_role = max(pri, key=lambda sr: sr[0])[1]                    # parallelism: last role == pronoun's role
        par.append(1.0 if last_role == pron_role else 0.0)
        s = sum(ROLE_W.get(r, 1.0) * (_dt(p_sent, sent) ** (-d)) for sent, r in pri)  # ACT-R base-level activation
        actr.append(math.log(s) if s > 0 else -1e9)

    zsup = {"recency": _zscore(np.array(rec)), "subject": _zscore(np.array(subj)),
            "cb": _zscore(np.array(cb)), "freq": _zscore(np.array(freq)),
            "first": _zscore(np.array(first)), "parallel": _zscore(np.array(par)),
            "actr": _zscore(np.array(actr))}
    g = graded_pick(zsup, weights, gain=gain)
    return {"pick": int(g["win"]), "entropy": float(g["entropy"]), "margin": float(g.get("margin", 0.0))}


def hard_tier_pick(candidate_priors: Sequence[Sequence[Tuple[int, str]]], p_sent: int) -> int:
    """The INCUMBENT rigid pick (for reference/comparison): the candidate holding the most-recent grammatical-SUBJECT
    clause < p_sent, ties broken by recency; else pure recency. This is the strong-but-rigid floor the graded retrieval
    beats +0.172 CI-sep on real narrative (it over-commits to the last subject even when the referent is less salient)."""
    if not candidate_priors:
        return -1
    best_i, best_subj_sent, best_recent = -1, None, None
    for i, pri in enumerate(candidate_priors):
        subj_sents = [s for s, r in pri if r == "SUBJECT" and s < p_sent]
        most_recent = max(s for s, _r in pri)
        if subj_sents:
            sc = max(subj_sents)
            if best_subj_sent is None or sc > best_subj_sent or (sc == best_subj_sent and most_recent > (best_recent or -1)):
                best_i, best_subj_sent, best_recent = i, sc, most_recent
    if best_i >= 0:
        return best_i
    return int(max(range(len(candidate_priors)), key=lambda i: max(s for s, _r in candidate_priors[i])))


# ── Person-feature agreement: candidate-pool cleanup (the measured +0.022 CI-separated pool-cleanup win) ──────────
# Landed 2026-08-29 from the integrated `the_reader_has_no_coherence_next_mention_prior` (the coherence prior was a
# RIGOROUS NEGATIVE / EXCELLENT, owner-DONE: measured dead on the residual). Drilling "any more optimizations?" surfaced
# a SEPARATE, twin-controlled win in the candidate POOL: the graded resolver's pool (mean ~39) is polluted with clusters
# whose only mentions are 1st/2nd-person pronouns ("I"/"we"/"my") -- extraction artifacts the agreement filter wrongly
# admits as candidates for a 3rd-person pronoun. Dropping them lifts full LitBank accuracy 0.775 -> 0.797 (+0.022 CI-sep
# [+0.007,+0.040]); the info-free RANDOM-drop twin LOSES (0.756, beaten +0.041) -- so it removes POLLUTION, not pool
# size. Brain-foundational: the brain never tracks a first-person SPEAKER as a 3rd-person referent (a person-feature the
# agreement filter should exclude). spaCy-FREE (pure head-string logic). ADDITIVE / opt-in: a pre-filter the caller
# applies to its candidate pool BEFORE graded_antecedent_pick; existing callers are byte-unchanged.

# 1st/2nd-person pronoun forms -- a candidate headed ONLY by these is a mis-extracted speaker, never a 3rd-person
# antecedent (exp_coref_pool_cleanup_v1's ARTIFACT set, extended with the 2nd-person reflexives).
FIRST_SECOND_PERSON = frozenset("i we me us my our you your myself ourselves yourself yourselves".split())
# 3rd-person pronoun forms (the resolvable pronouns + their genitives/reflexives; exp's NOMINAL_PRON set).
THIRD_PERSON_PRON = frozenset("he she it they him her them his its their himself herself itself themselves".split())


def is_first_second_person_artifact(mention_heads: Sequence[str]) -> bool:
    """True iff a candidate CLUSTER is a mis-extracted 1st/2nd-person speaker artifact to EXCLUDE from a 3rd-person
    pronoun's candidate pool: EVERY mention head is a pronoun AND at least one is 1st/2nd-person. A cluster with any
    non-pronoun head (a real named entity) is spared; a purely 3rd-person-pronoun cluster is spared (no 1st/2nd
    member). The person-feature agreement fix the brain applies automatically (a first-person speaker is never a
    3rd-person referent). spaCy-free."""
    hs = [h.lower() for h in mention_heads]
    if not hs:
        return False
    return (all(h in FIRST_SECOND_PERSON or h in THIRD_PERSON_PRON for h in hs)
            and any(h in FIRST_SECOND_PERSON for h in hs))


def keep_after_pool_cleanup(candidate_heads: Sequence[Sequence[str]]) -> List[int]:
    """Given each candidate cluster's mention-head list, return the indices to KEEP after dropping 1st/2nd-person
    pronoun artifacts (the measured +0.022 CI-separated pool cleanup; the info-free random-drop twin loses). Apply
    this to the candidate pool BEFORE graded_antecedent_pick to remove agreement pollution, not pool size."""
    return [i for i, heads in enumerate(candidate_heads) if not is_first_second_person_artifact(heads)]
