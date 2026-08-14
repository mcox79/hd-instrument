"""hdlab/grounding_acquisition_loop.py -- closed self-growing grounding loop (2026-08-09).

FLAG -> LIBRARY -> CONSOLIDATE ("sleep") -> GUARD (schema-consistency, escalate-don't-force-commit)
-> BANK. Wires hdlab.consequence_learning_loop's already-built propose/credit/teacher-verdict half
(FLAG) to a NEW trace-level library (this module) whose periodic consolidation pass gates every
BANK decision on a SCHEMA-CONSISTENCY signal computed over the item's own accumulated CONTEXT
vectors, independent of vote agreement. This is the missing piece the acquisition drill identified:
prior attempts (word_acquisition_loop.combine_votes, consequence_learning_loop.consolidate) gate
purely on VOTE agreement/margin; Warren et al. 2014 (vmPFC lesion, DRM) found that the SAME
schema-integration circuit that fast-tracks true learning also manufactures false memories, so
vote-agreement alone is exactly the failure mode a genuine anti-false-memory guard must catch, not
merely assume away.

Cites: notes/research_psych_acquisition_consolidation_loop_2026-08-09.md (full design + literature:
Dumay & Gaskell 2007 sleep-not-just-time word integration; Tamminen et al. 2010 replay-budget;
van Kesteren et al. 2012 SLIMM schema-gate; Warren et al. 2014 false-consolidation double-edge).
preregs/2026-08-09_grounding_acquisition_loop_v1.md (bands, config, deviations from the drill's
literal design -- notably: a split-half context-coherence metric standing in for a full FHRR/
hippocampal-encoder CA3-complete wiring, reusing exp_confidence_gated_codebook_consolidation_v1's
SPLIT-HALF RELIABILITY *shape* (test-retest consistency across two disjoint evidence slices),
applied to per-encounter bag-of-content-words context vectors instead of PPMI co-occurrence rows).

REUSE (wire-don't-island; every organ below is imported read-only, called verbatim):
  hdlab.consequence_learning_loop.credit_window / teacher_verdict   (FLAG: OOV outcome-verb credit
                                                                      scan + episode teacher label)
  hdlab.self_improving_loop.decide_keep_or_revert                   (abstain-band vote-margin gate,
                                                                      byte-identical idiom to
                                                                      consequence_learning_loop.consolidate)
  hdlab.verb_lexical_similarity.register_acquired_outcome / in_lexicon   (BANK write-back, overlay)
  hdlab.hd_fact_store.HDFactStore                                   (BANK write-back, NATIVE -- see
                                                                      PROMOTE below, 2026-08-10)

PROMOTE (2026-08-10, notes/research_brain_scaffolding_that_fades_2026-08-10.md +
notes/research_crutch_fade_loop_owned_organ_wiring_2026-08-10.md): consolidation_pass's BANK step
previously wrote ONLY into verb_lexical_similarity's flat overlay dict -- a permanent side-table,
never merged into any natively-read structure, which those two drills independently found makes the
"crutch fades" claim structurally impossible (an annotation, not a migration). This module now
OPTIONALLY (native_store=None preserves prior behavior byte-for-byte) also PROMOTES a banked item
into hdlab.hd_fact_store.HDFactStore's trust-bound representation, gated by a THIRD, independent
condition on top of the existing two (vote-margin abstain-band + schema-consistency split-half):
EXPOSURE (len(traces)) >= promote_min_exposure AND MAPPING-CONSISTENCY (abs(vote_margin)) >=
promote_min_consistency. This operationalizes Logan 1988 (Instance Theory: exposure count predicts
automaticity) and Schneider & Shiffrin 1977 (automaticity requires CONSISTENT mapping, not just
enough repetitions) as the promotion gate -- schema-coherence licenses BANKING (an "associative"
stage, Fitts & Posner 1967), but promotion to native/autonomous requires the stricter, independent
consistency bar this drill's Test A exists to validate. The existing false-memory guard
(schema_consistency_split_half) is NEVER loosened by this addition -- an item that fails it still
never reaches the BANK branch at all, so it structurally cannot promote either.

GENUINELY-NEW code here: context_vector (deterministic bag-of-content-words bipolar bundle, glass-
box, hashlib-seeded per PROT-023/F.5 -- never Python hash()), Library/LibraryItem/Trace (the
not-yet-grounded store, trace-level not counter-level -- traces are kept SEPARATE per Trueswell
propose-verify / the 07-28 audit's own core finding, never folded/averaged at intake),
schema_consistency_split_half (the guard signal), surprise_order (Tamminen/Rasch selective-replay
ordering, diagnostic), consolidation_pass (the periodic "sleep" pass: vote-margin gate AND
schema-consistency gate AND the Dumay-Gaskell intervening-pass rule, ESCALATE-don't-force-commit on
patience exhaustion -- ANY gate failing defers, never forces a commit).

ASCII-only. NumPy; deterministic integer/hashlib seeding throughout (no built-in hash(), no
list(set()) ordering -- PROT-023/F.5 compliant).
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from hdlab.consequence_learning_loop import (  # noqa: F401 (credit_window re-exported for callers)
    credit_window, _credit_targets, teacher_verdict,
)
from hdlab.self_improving_loop import decide_keep_or_revert
from hdlab.verb_lexical_similarity import register_acquired_outcome, in_lexicon
from hdlab.hd_fact_store import HDFactStore  # noqa: F401 (PROMOTE target; real code path, not a stub)

# ---- config (mine to set per exp_dev Autonomy grant; documented + justified in the pre-reg) ----
D = 256                      # context bipolar vector dimensionality
MIN_CONFIRM = 4                # schema_consistency_split_half needs >=2 traces PER HALF (n>=4) to
                                # ever produce a score; MIN_CONFIRM=4 (not consequence_learning_loop's
                                # 3) keeps "reached min_confirm" and "schema-scoreable" coincident so
                                # no item wastes patience while merely under-evidenced (see
                                # consolidation_pass: schema_score is None -> defer, no patience cost).
NEUTRAL_BAND = 0.34           # matches hdlab.consequence_learning_loop.NEUTRAL_BAND
PATIENCE_MAX = 3              # consolidation passes an item may fail the guard before ESCALATED
PROMOTE_MIN_EXPOSURE = 8       # native-promotion exposure floor (Logan 1988 instance count); strictly
                                # above MIN_CONFIRM=4 -- "eligible to bank" != "eligible to promote"
PROMOTE_MIN_CONSISTENCY = 0.75  # native-promotion |vote_margin| floor (Schneider & Shiffrin 1977
                                # consistent-mapping); strictly above NEUTRAL_BAND=0.34's banking bar
                                # -- a coherent-context item can bank (associative) on a much weaker
                                # vote margin than it needs to promote (autonomous).
PROMOTE_RELATION = "OUTCOME_POLARITY"  # hd_fact_store relation name for a promoted grounding

_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "if", "of", "to", "in", "on", "at", "by", "for", "with",
    "as", "is", "was", "were", "are", "be", "been", "being", "it", "its", "he", "she", "they",
    "him", "her", "them", "his", "their", "i", "you", "we", "me", "my", "your", "our", "this",
    "that", "these", "those", "not", "no", "so", "than", "then", "there", "here", "up", "out",
    "into", "over", "again", "very", "just", "would", "could", "should", "will", "shall", "can",
    "did", "do", "does", "had", "has", "have", "from", "all", "any", "some", "one", "two", "when",
    "what", "who", "which", "how", "why", "said", "upon",
})


def content_words(window_text: str) -> List[str]:
    """Pure content-word extraction (2026-08-11, additive extraction of context_vector's own
    filter -- SAME regex + stopword + length rule, byte-identical output on the same input;
    context_vector below now calls this instead of inlining the filter, so this is a refactor,
    not a behavior change). Exists so a caller can compare WORD IDENTITY across two texts (e.g.
    for a concept-similarity-based coherence metric) without re-deriving the exact same
    tokenization rule context_vector uses internally -- keeps both paths using ONE filter."""
    return [w for w in re.findall(r"[a-z']+", window_text.lower())
            if w not in _STOPWORDS and len(w) > 2]


def context_vector(window_text: str, d: int = D, *, graded: bool = False) -> np.ndarray:
    """Deterministic bag-of-content-words bipolar bundle (Kanerva random-indexing / BEAGLE-style
    context encoding). Each content word's vector = a hashlib.sha256-seeded bipolar draw (fixed
    across every call, no external embedding, no torch.Generator state to thread); the trace's
    context = sign(sum of its content words' vectors). Deterministic, PROT-023/F.5-compliant
    (hashlib, not built-in hash()). Returns an all-zero vector if the window has no content word
    (caller must guard cosine against a zero-norm vector -- see _cos).

    `graded` (2026-08-13, ADDITIVE, keyword-only, DEFAULT False = prior behavior BYTE-FOR-BYTE):
    return the raw accumulated sum instead of its sign. The terminal `np.sign` is a PER-COMPONENT
    magnitude-destroying normalisation; the brain's divisive normalisation uses a POOL-SHARED
    denominator (Carandini & Heeger 2012 Nat Rev Neurosci 13:51-62) which PRESERVES the ratios
    that sign() flattens to 1. Because sign(shared + distinctive) = sign(shared) wherever
    |shared| > |distinctive|, the default is a PROTOTYPE OPERATOR: at a 2% distinctive:shared
    ratio 10.13% of near-neighbour pairs become BIT-IDENTICAL, and at 10% only 26% of the
    difference direction between two concepts is real distinctive meaning
    (experiments/diag_sign_annihilates_distinctive_v1.py).
    MEASURED payoff, n=4000 held-out near-neighbour 2AFC in context, prereg d6c56353c:
    dropping this sign() is worth +0.0245 to +0.0267 accuracy on its own, CI excluding 0 at every
    normalisation level (data/exp_graded_divisive_comparator_v1/metrics.json). Witness:
    verification/verify_graded_divisive_comparator.py."""
    words = content_words(window_text)
    if not words:
        return np.zeros(d, dtype=np.float64)
    acc = np.zeros(d, dtype=np.float64)
    for w in words:
        seed = int.from_bytes(hashlib.sha256(w.encode("utf-8")).digest()[:8], "big") % (2**32)
        rng = np.random.default_rng(seed)
        acc += rng.choice([-1.0, 1.0], size=d)
    if graded:
        return acc
    out = np.sign(acc)
    out[out == 0] = 1.0
    return out


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _bundle(vecs: List[np.ndarray]) -> np.ndarray:
    """sign(sum(vecs)); zero entries broken toward +1 (bipolar cleanup, matches predictive_coding.py
    convention)."""
    out = np.sign(np.sum(vecs, axis=0))
    out[out == 0] = 1.0
    return out


@dataclass
class Trace:
    """One INDEPENDENT episode's evidence for a library item. Kept separate, never folded/averaged
    at intake (Trueswell propose-verify / the 07-28 audit's core finding)."""
    episode_id: str
    pole: str                  # "POS" | "NEG"  (MET->POS / UNMET->NEG, matching consequence_learning_loop)
    context_vec: np.ndarray
    pass_idx: int               # the pass this trace was recorded


@dataclass
class Hypothesis:
    """The ONE carried referent hypothesis for a library item (2026-08-12 PBV build).

    SHAPE (Medina 2011 PNAS / Trueswell 2013 Cog Psych / Woodard 2016): exactly one hypothesis is
    held at a time and NO score is retained for any alternative -- there is deliberately no
    `runner_up` field and no candidate set, because "no partial credit to alternatives" is the one
    thing the PBV literature is unambiguous about. `strength` is Stevens 2017 Hybrid Pursuit's
    refinement: the single carried hypothesis has a PERSISTING scalar that rises on confirmation
    and falls on disconfirmation, so it survives one noisy encounter but not a run of them.

    `rejected` is a LOG ONLY -- it is written on every abandonment and is NEVER read by any
    decision in this module (grep: it appears in exactly one write site and zero read sites in
    the update path). PBV learners retain nothing usable about hypotheses they have dropped;
    keeping the list readable by the mechanism would smuggle partial credit back in through the
    back door. It exists so a cell can AUDIT the trajectory."""
    obj: str
    strength: float
    proposed_pass: int
    proposed_at_n_traces: int
    n_confirm: int = 0
    n_disconfirm: int = 0
    n_uninformative: int = 0


@dataclass
class LibraryItem:
    lemma: str
    traces: List[Trace] = field(default_factory=list)
    status: str = "PENDING"     # PENDING | GROUNDED_POS | GROUNDED_NEG | GROUNDED_NEUTRAL | ESCALATED
    first_min_confirm_pass: Optional[int] = None
    patience: int = 0
    # ---- PBV hypothesis state (2026-08-12; all defaulted, so every existing constructor call
    # -- including hdlab.foundation_persistence.load_library_pending's keyword construction, which
    # this build does not touch -- keeps working unchanged and every pre-existing snapshot loads).
    hypothesis: Optional[Hypothesis] = None
    hypothesis_log: List[dict] = field(default_factory=list)   # PROPOSE/CONFIRM/DISCONFIRM/ABANDON/REPROPOSE/REVIVE
    n_abandoned: int = 0
    n_revivals: int = 0
    rejected: List[str] = field(default_factory=list)          # LOG ONLY -- never read by a decision


# ---- PBV config (Stevens 2017 Hybrid Pursuit shape; values are OURS, justified in the pre-reg) --
PBV_INIT_STRENGTH = 0.5      # a freshly proposed hypothesis is a coin-flip commitment, not a belief
PBV_GAMMA = 0.5              # Bush-Mosteller step. From 0.5: two consecutive disconfirmations reach
                             # 0.125 < PBV_ABANDON_STRENGTH -> ABRUPT switching (Trueswell), while a
                             # confirmed hypothesis (0.75, 0.875, ...) needs progressively more
                             # disconfirmation to dislodge -- Pursuit's persisting-strength refinement.
PBV_ABANDON_STRENGTH = 0.2   # strictly below PBV_INIT_STRENGTH, so abandonment always requires
                             # accumulated disconfirming evidence, never a single noisy encounter
                             # from the proposal point.
PBV_MAX_REVIVALS = 2         # bounded re-opening of an ESCALATED item (see Library.flag); a hard cap
                             # is what guarantees the loop still terminates once escalation is no
                             # longer terminal.


def pbv_update_strength(strength: float, confirmed: bool, gamma: float = PBV_GAMMA) -> float:
    """Bush-Mosteller linear reward-penalty update on the ONE carried hypothesis' strength.
    confirm: s + gamma*(1-s)  (asymptotes at 1, never saturates exactly)
    disconfirm: s*(1-gamma)   (geometric decay toward 0)
    Pure function of (strength, verdict) -- no reference to any alternative candidate's score,
    which is the structural guarantee that no partial credit can reach a runner-up."""
    if confirmed:
        return strength + gamma * (1.0 - strength)
    return strength * (1.0 - gamma)


class Library:
    """The not-yet-grounded store. Keyed by lemma-or-construction-signature (here: outcome-verb
    lemma, matching consequence_learning_loop's existing keying)."""

    def __init__(self) -> None:
        self.items: Dict[str, LibraryItem] = {}

    def flag(self, lemma: str, episode_id: str, pole: str, context_vec: np.ndarray,
             pass_idx: int, *,
             propose_fn: Optional[Callable[[LibraryItem, Trace], Optional[Tuple[str, float]]]] = None,
             verify_fn: Optional[Callable[[LibraryItem, Trace], Optional[bool]]] = None,
             gamma: float = PBV_GAMMA,
             abandon_strength: float = PBV_ABANDON_STRENGTH,
             init_strength: float = PBV_INIT_STRENGTH,
             revive_terminal: bool = False,
             max_revivals: int = PBV_MAX_REVIVALS) -> bool:
        """Append one trace -- and, when `propose_fn`/`verify_fn` are supplied, run the PBV
        PROPOSE / VERIFY / ABANDON-AND-RE-PROPOSE cycle at this encounter.

        DEFAULTS (both fns None, revive_terminal False) reproduce the prior behavior byte-for-byte:
        no-op (returns False) for an item that already reached a terminal status; append + return
        True otherwise. Every existing caller is unchanged.

        WHY HERE (2026-08-12): this is the "an encounter happened" site, and PBV's verification is
        an ONLINE event at the encounter -- not an offline pass. Putting it anywhere else would
        reproduce the POSITION infidelity the audit named. This module stays generic: it knows
        nothing about words, concept spaces or cosines. `propose_fn(item, trace)` returns
        (object, score) or None (this encounter licenses no proposal); `verify_fn(item, trace)`
        returns True (this encounter CONFIRMS the standing hypothesis), False (DISCONFIRMS), or
        None (UNINFORMATIVE -- Medina 2011's ~90%: no strength change at all, which is why the
        third return value is not optional).

        revive_terminal (default False = prior behavior): when True, an ESCALATED item receiving a
        new trace returns to PENDING with patience reset and n_revivals incremented, up to
        max_revivals. ESCALATE means "inconclusive so far", never "proven wrong" (this module's own
        docstring), and PBV abandons-and-re-proposes rather than exiting -- so permanent terminality
        on escalation was a fidelity bug. GROUNDED_* items are NEVER revived here (a banked fact is
        the store's business, not the library's).

        Returns True iff a trace was actually appended."""
        it = self.items.get(lemma)
        if it is None:
            it = LibraryItem(lemma=lemma)
            self.items[lemma] = it
        if it.status != "PENDING":
            if not (revive_terminal and it.status == "ESCALATED" and it.n_revivals < max_revivals):
                return False
            it.status = "PENDING"
            it.patience = 0
            it.n_revivals += 1
            it.hypothesis_log.append({"event": "REVIVE", "pass_idx": pass_idx,
                                      "n_revivals": it.n_revivals, "n_traces": len(it.traces)})
        tr = Trace(episode_id, pole, context_vec, pass_idx)
        it.traces.append(tr)
        if propose_fn is None and verify_fn is None:
            return True

        if it.hypothesis is None:
            self._propose(it, tr, pass_idx, propose_fn, init_strength, event="PROPOSE")
            return True
        if verify_fn is None:
            return True
        verdict = verify_fn(it, tr)
        h = it.hypothesis
        if verdict is None:
            h.n_uninformative += 1
            return True
        if verdict:
            h.n_confirm += 1
            h.strength = pbv_update_strength(h.strength, True, gamma)
            it.hypothesis_log.append({"event": "CONFIRM", "pass_idx": pass_idx, "obj": h.obj,
                                      "strength": round(h.strength, 6), "n_traces": len(it.traces)})
            return True
        h.n_disconfirm += 1
        h.strength = pbv_update_strength(h.strength, False, gamma)
        it.hypothesis_log.append({"event": "DISCONFIRM", "pass_idx": pass_idx, "obj": h.obj,
                                  "strength": round(h.strength, 6), "n_traces": len(it.traces)})
        if h.strength > abandon_strength:
            return True
        # ---- ABANDON, then RE-PROPOSE in the same act (Trueswell 2013). Abandonment is
        # hypothesis-level: the ITEM stays PENDING and keeps accumulating evidence. The re-proposal
        # is drawn from THIS (disconfirming) encounter, not from any accumulated score over past
        # encounters -- that is what keeps runner-up credit structurally impossible.
        it.hypothesis_log.append({"event": "ABANDON", "pass_idx": pass_idx, "obj": h.obj,
                                  "strength": round(h.strength, 6),
                                  "n_confirm": h.n_confirm, "n_disconfirm": h.n_disconfirm,
                                  "n_traces": len(it.traces)})
        it.rejected.append(h.obj)     # LOG ONLY (see Hypothesis docstring); never read below
        it.n_abandoned += 1
        it.hypothesis = None
        if propose_fn is not None:
            self._propose(it, tr, pass_idx, propose_fn, init_strength, event="REPROPOSE")
        return True

    @staticmethod
    def _propose(it: LibraryItem, tr: Trace, pass_idx: int,
                 propose_fn: Optional[Callable[[LibraryItem, Trace], Optional[Tuple[str, float]]]],
                 init_strength: float, *, event: str) -> None:
        """Propose from ONE encounter. No-op when propose_fn is None or declines (an uninformative
        encounter licenses no commitment -- Medina 2011)."""
        if propose_fn is None:
            return
        cand = propose_fn(it, tr)
        if cand is None:
            return
        obj, score = cand
        it.hypothesis = Hypothesis(obj=obj, strength=init_strength, proposed_pass=pass_idx,
                                   proposed_at_n_traces=len(it.traces))
        it.hypothesis_log.append({"event": event, "pass_idx": pass_idx, "obj": obj,
                                  "score": round(float(score), 6),
                                  "strength": round(init_strength, 6), "n_traces": len(it.traces)})

    def inject_hypothesis(self, lemma: str, obj: str, strength: float, pass_idx: int) -> None:
        """CAN-FAIL TEST HOOK (2026-08-12): force a specific standing hypothesis onto an item.
        Exists so an experiment can inject a DELIBERATELY WRONG meaning and measure whether the
        verification machinery abandons it on disconfirming evidence. Not called by any production
        path (grep-checkable: only experiments/exp_pbv_hypothesis_v1.py and the self-tests)."""
        it = self.items.get(lemma)
        if it is None:
            it = LibraryItem(lemma=lemma)
            self.items[lemma] = it
        it.hypothesis = Hypothesis(obj=obj, strength=strength, proposed_pass=pass_idx,
                                   proposed_at_n_traces=len(it.traces))
        it.hypothesis_log.append({"event": "INJECT", "pass_idx": pass_idx, "obj": obj,
                                  "strength": round(float(strength), 6), "n_traces": len(it.traces)})


def schema_consistency_split_half(traces: List[Trace], min_half_size: int = 2,
                                  coherence_fn: Optional[Callable[[List[Trace], List[Trace]], float]] = None
                                  ) -> Optional[float]:
    """Split-half context-coherence (reuses exp_confidence_gated_codebook_consolidation_v1's
    split-by-position reliability SHAPE -- there: two independent PPMI builds over disjoint token
    halves; here: two independent context-vector bundles over disjoint TRACE halves, ordered by
    accumulation order not shuffled). Returns None (defer, not zero) if fewer than min_half_size
    traces exist per half -- an under-evidenced item cannot yet be schema-scored, distinct from a
    genuinely LOW score.

    min_half_size (2026-08-11, additive; default 2 preserves the exact prior n<4->None behavior
    byte-for-byte): the minimum traces required PER HALF. A caller whose confirmation gate has
    been independence-weighted (see consolidation_pass's/prelim_tier's trace_weight_fn, which can
    legitimately cross MIN_CONFIRM at n=2..3 genuinely-independent-source traces, below the
    default n>=4 this split-half floor was coincidentally tuned to -- see grounding_acquisition_
    loop module docstring's own MIN_CONFIRM comment) may pass min_half_size=1 to permit a
    genuinely-informative (if noisier) 1-vs-1 or 1-vs-2 split at n=2..3. This does not change the
    split-half MATH, only the minimum n at which it is computed at all.

    coherence_fn (2026-08-11, additive; default None preserves the exact prior raw-context-vec-
    cosine computation byte-for-byte): when provided, called as coherence_fn(half_a, half_b) ->
    float and used IN PLACE OF the raw cosine-of-summed-context-vectors metric below. This is the
    hook the independence-weighted-corroboration drill's follow-on (cross-source PARAPHRASE
    alignment) uses to swap the surface-word-overlap check for a graded, concept-similarity-based
    coherence metric -- see experiments/exp_three_tier_loop_concept_coherence_v1.py's own
    concept_coherence_score, which this module knows nothing about (this module stays generic;
    it only calls whatever callable the caller supplies on the two half-lists of Trace objects).
    The n < 2*min_half_size defer gate above is evaluated identically regardless of coherence_fn
    (evidence-count sufficiency is orthogonal to which coherence metric computes the score).

    DEFAULT METRIC (coherence_fn is None): uses the RAW (non-sign-cleaned) sum of each half's
    context vectors, not the bipolar-cleaned bundle context_vector() itself returns: sign-cleanup's
    zero-tie-break-to-+1 convention (matches predictive_coding.py's own bipolar-cleanup convention)
    injects a systematic POSITIVE bias into the cosine between any two SMALL (e.g. 2-item)
    independently-random bundles, since ~50% of coordinates tie at 0 and both sides break the SAME
    direction -- confirmed empirically (self_test below caught a spurious 0.36 cosine between two
    independent noise bundles-of-2 under sign-cleanup). Cosine of the raw (uncleaned) sums has no
    such artifact and is the correct metric for a smooth reliability signal (we are not requesting
    a clean concept symbol here, just a coherence SCORE)."""
    n = len(traces)
    if n < 2 * min_half_size:
        return None
    half = n // 2
    a, b = traces[:half], traces[half:]
    if coherence_fn is not None:
        return float(coherence_fn(a, b))
    va = np.sum([t.context_vec for t in a], axis=0)
    vb = np.sum([t.context_vec for t in b], axis=0)
    return _cos(va, vb)


def surprise_order(traces: List[Trace]) -> List[Trace]:
    """Order traces by disagreement-with-the-bundle-of-the-OTHERS (Tamminen/Rasch selective-replay:
    highest-disagreement-with-the-rest first, i.e. the trace the running schema would predict
    LEAST well is replayed first). Diagnostic / logged (matches the v6 design's surprise-ordering
    leg); does not itself gate anything -- consolidation_pass uses the split-half score, not this
    order, to decide eligibility."""
    if len(traces) < 2:
        return list(traces)
    scored = []
    for i, t in enumerate(traces):
        others = [o.context_vec for j, o in enumerate(traces) if j != i]
        bundle = _bundle(others)
        scored.append((1.0 - _cos(t.context_vec, bundle), t))
    scored.sort(key=lambda x: -x[0])
    return [t for _, t in scored]


def _vote_margin(traces: List[Trace]) -> Tuple[float, int, int]:
    n = len(traces)
    pos = sum(1 for t in traces if t.pole == "POS")
    neg = n - pos
    margin = (pos - neg) / n if n else 0.0
    return margin, pos, neg


def consolidation_pass(library: Library, pass_idx: int, *,
                        min_confirm: int = MIN_CONFIRM,
                        schema_thresh: float = 0.10,
                        neutral_band: float = NEUTRAL_BAND,
                        patience_max: int = PATIENCE_MAX,
                        register: bool = True,
                        mdl_gate_fn: Optional[Callable[["LibraryItem"], bool]] = None,
                        native_store: Optional["HDFactStore"] = None,
                        promote_min_exposure: int = PROMOTE_MIN_EXPOSURE,
                        promote_min_consistency: float = PROMOTE_MIN_CONSISTENCY,
                        promote_relation: str = PROMOTE_RELATION,
                        promote_source: str = "grounding_acquisition_loop",
                        trace_weight_fn: Optional[Callable[[List[Trace]], float]] = None,
                        schema_min_half_size: int = 2,
                        coherence_fn: Optional[Callable[[List[Trace], List[Trace]], float]] = None
                        ) -> dict:
    """One offline 'sleep' pass over the WHOLE library (Diekelmann & Born: offline, separate from
    the reading/FLAG pass). For each PENDING item with >= min_confirm traces:
      1. mark first_min_confirm_pass on the FIRST pass this threshold is reached (if not yet set).
      2. Dumay & Gaskell intervening-pass rule: an item may NOT integrate on the very pass it first
         becomes eligible -- it must survive to a LATER pass, matching sleep-dependent (not just
         elapsed-time) word integration. This pass costs NO patience (it is a structural wait, not
         a failed evaluation).
      3. On any pass where intervening_pass_ok: compute vote_margin (POS/NEG tally) and the
         schema-consistency split-half score. BANK (GROUNDED_POS/NEG/NEUTRAL) iff schema_score is
         non-None AND schema_score >= schema_thresh (the mandatory guard -- vote agreement ALONE
         never banks anything, per Warren et al. 2014's same-circuit false-memory finding). Else
         increment patience; at patience_max -> ESCALATED (terminal, NEVER force-committed).

    mdl_gate_fn (optional, CONJUNCTIVE -- AND, never OR, with the schema-consistency check; see
    preregs/2026-08-09_learner_mdl_gate_on_acquisition_traces_v1.md): when provided, called as
    mdl_gate_fn(item) -> bool ONLY on passes where schema_score >= schema_thresh already holds (the
    schema check remains a NECESSARY condition regardless of what mdl_gate_fn returns -- this is
    the structural guarantee that the existing false-consolidation guard invariants can never be
    WEAKENED by adding this gate, only made stricter). A False mdl_gate_fn verdict is treated
    identically to a schema-check failure: patience increments, no forced commit. Default None
    preserves the exact prior behavior byte-for-byte (the ternary below reduces to `if schema_ok`).
    Operationalizes Ghosh & Gilboa (2014)'s 'non-specific/abstracted structure' schema criterion via
    hdlab.learner's MDL two-part-code compression gate (Perfors & Tenenbaum 2009), as a SECOND,
    independent test of whether the item's own accumulated evidence is genuinely compressible, not
    merely internally coherent by the cosine-based split-half metric alone.

    native_store (2026-08-10, optional -- default None preserves prior behavior byte-for-byte): when
    provided, every item that BANKS as GROUNDED_POS/GROUNDED_NEG is ALSO evaluated for PROMOTION into
    native_store's trust-bound (s,r,o) representation, gated on exposure (len(traces)) >=
    promote_min_exposure AND consistency (abs(vote_margin)) >= promote_min_consistency -- a strictly
    STRONGER, independent bar than banking's own (schema_thresh, neutral_band) gates (see module
    docstring PROMOTE section). GROUNDED_NEUTRAL items never promote (no directional fact to assert).
    promote_min_exposure/promote_min_consistency default to the module constants but are NOT
    hard-coded into the gate logic -- a caller (e.g. a research cell) may vary them, which is exactly
    what lets Test A probe the threshold's shape. Every BANK-branch item (grounded, any label) gets a
    `promotion_log` entry recording exposure/consistency/label/promoted, whether or not native_store
    was supplied (promoted is always False when native_store is None) -- this is what lets a caller
    later correlate native coverage against the two fade predictors without re-deriving them.

    trace_weight_fn (2026-08-11, optional, additive -- default None preserves the exact prior
    raw-trace-count gate byte-for-byte): when provided, called as trace_weight_fn(item.traces) ->
    float and used IN PLACE OF len(item.traces) for the min_confirm eligibility check below (the
    "CONFIRMATION gate" this drill makes independence-weighted -- see notes/2026-08-11 genuine-
    cross-source-corroboration drill). This lets a caller weight N genuinely-independent-source
    traces as stronger evidence than N repeats of one correlated source, without this module
    knowing anything about what a "source" is (that classification lives entirely in the
    caller-supplied function). schema_min_half_size threads through to schema_consistency_
    split_half unchanged (see that function's own docstring) -- the schema-coherence guard is a
    SEPARATE, still-mandatory condition; trace_weight_fn only changes what counts as "enough
    evidence to be schema-scored at all," never bypasses the schema check itself.

    coherence_fn (2026-08-11, optional, additive -- default None preserves the exact prior
    raw-context-vec-cosine schema-coherence metric byte-for-byte): threads through UNCHANGED to
    schema_consistency_split_half's own coherence_fn parameter (see that function's docstring).
    Lets a caller replace the surface-word-overlap coherence check with a graded, meaning-based
    one (e.g. concept_similarity-based) without this module knowing anything about words or
    concepts -- same "organ stays generic" discipline as trace_weight_fn above.

    Returns a per-pass report dict; mutates `library` in place."""
    newly_grounded = {"POS": [], "NEG": [], "NEUTRAL": []}
    newly_escalated: List[str] = []
    promotion_log: List[dict] = []
    for lemma in sorted(library.items):
        it = library.items[lemma]
        if it.status != "PENDING":
            continue
        n = len(it.traces)
        confirm_score = float(n) if trace_weight_fn is None else float(trace_weight_fn(it.traces))
        if confirm_score < min_confirm:
            continue
        if it.first_min_confirm_pass is None:
            it.first_min_confirm_pass = pass_idx
        if pass_idx <= it.first_min_confirm_pass:
            continue  # mandatory intervening-pass wait; not a failure, no patience cost
        schema_score = schema_consistency_split_half(it.traces, min_half_size=schema_min_half_size,
                                                     coherence_fn=coherence_fn)
        if schema_score is None:
            continue  # insufficient evidence for a split yet (should not occur once n>=MIN_CONFIRM=4,
                       # but defensive: defer, no patience cost -- not-enough-evidence is not a guard
                       # FAILURE, it's an open question more exposure may still answer)
        schema_ok = schema_score >= schema_thresh
        # mdl_gate_fn only ever CONSULTED when schema already passes (AND semantics); when
        # mdl_gate_fn is None (default) or schema_ok is False, mdl_ok is vacuously True/irrelevant
        # -- the `schema_ok and mdl_ok` check below is then identical to the original `schema_ok`
        # check, byte-for-byte, so this is a strictly additive, backward-compatible change.
        mdl_ok = mdl_gate_fn(it) if (schema_ok and mdl_gate_fn is not None) else True
        if schema_ok and mdl_ok:
            margin, pos, neg = _vote_margin(it.traces)
            vote = decide_keep_or_revert({"POS": margin, "NEG": -margin},
                                         abstain_band=neutral_band - 1e-9)
            label = vote if vote is not None else "NEUTRAL"
            it.status = f"GROUNDED_{label}"
            if register and label in ("POS", "NEG"):
                register_acquired_outcome(lemma, label)
            newly_grounded[label].append(lemma)
            # ---- PROMOTE: overlay-bank (above) is NOT native-promotion. A THIRD, independent gate
            # (exposure AND consistency, both strictly stronger than banking's own thresholds) decides
            # whether this item ALSO migrates into native_store. schema_ok being True here is a
            # NECESSARY-for-bank precondition, never a sufficient-for-promote one -- a coherent-context
            # item with a merely-adequate (not highly consistent) vote history banks but must not
            # promote (this is the guard Test A vets hardest; see module PROMOTE docstring).
            exposure = n
            consistency = abs(margin)
            promoted = False
            if (native_store is not None and label in ("POS", "NEG")
                    and exposure >= promote_min_exposure
                    and consistency >= promote_min_consistency):
                trust_sym = "TRUST_HIGH" if consistency >= 0.9 else "TRUST_MID"
                native_store.store(lemma, promote_relation, label, promote_source, trust_sym)
                promoted = True
            promotion_log.append({"lemma": lemma, "exposure": exposure,
                                  "consistency": round(consistency, 6), "label": label,
                                  "promoted": promoted})
        else:
            it.patience += 1
            if it.patience >= patience_max:
                it.status = "ESCALATED"
                newly_escalated.append(lemma)
    return {
        "pass": pass_idx,
        "newly_grounded_pos": newly_grounded["POS"],
        "newly_grounded_neg": newly_grounded["NEG"],
        "newly_grounded_neutral": newly_grounded["NEUTRAL"],
        "newly_escalated": newly_escalated,
        "cumulative_grounded": sum(1 for i in library.items.values() if i.status.startswith("GROUNDED")),
        "cumulative_grounded_polar": sum(1 for i in library.items.values()
                                         if i.status in ("GROUNDED_POS", "GROUNDED_NEG")),
        "cumulative_escalated": sum(1 for i in library.items.values() if i.status == "ESCALATED"),
        "cumulative_pending": sum(1 for i in library.items.values() if i.status == "PENDING"),
        "promotion_log": promotion_log,
    }


def self_test() -> dict:
    """Fast off-disk gate exercising the REAL code path (real credit_window call on hand-authored
    micro-episodes, not a synthetic-only branch), per exp_dev SCHEMA-VET F.1."""
    # (1) context_vector: deterministic + content-sensitive.
    v1 = context_vector("The lantern flickered in the storm.")
    v2 = context_vector("The lantern flickered in the storm.")
    assert np.array_equal(v1, v2), "context_vector is non-deterministic"
    v3 = context_vector("The dragon roared over the mountain kingdom.")
    assert _cos(v1, v3) < 0.5, "unrelated windows should not bundle to near-identical vectors"
    assert np.all(context_vector("the a an of to") == 0.0), "all-stopword window must be all-zero"

    # (2) schema_consistency_split_half: coherent-repeat vs incoherent-scramble discriminate.
    coherent_traces = [Trace(f"e{i}", "POS", context_vector("Nell fixed the lantern by the fire."), 1)
                       for i in range(4)]
    coherent_score = schema_consistency_split_half(coherent_traces)
    assert coherent_score is not None and coherent_score > 0.95, (
        f"identical-context traces must split-half near cos=1.0, got {coherent_score}")
    rng = np.random.default_rng(0)
    scrambled_traces = [Trace(f"s{i}", "POS", rng.choice([-1.0, 1.0], size=D), 1) for i in range(4)]
    scrambled_score = schema_consistency_split_half(scrambled_traces)
    assert scrambled_score is not None and abs(scrambled_score) < 0.35, (
        f"independent-random-noise traces must split-half near cos=0.0, got {scrambled_score}")
    assert coherent_score > scrambled_score + 0.3, "discriminant-validity: coherent must clear scrambled"
    assert schema_consistency_split_half(coherent_traces[:3]) is None, "n=3 (<4) must defer (None), not score"

    # (2b) coherence_fn (2026-08-11, additive): default None reproduces the raw-cosine metric
    # byte-for-byte (regression check); a caller-supplied function is ACTUALLY consulted (proves
    # threading is load-bearing, not silently ignored -- same convention as prelim_tier's own
    # "caller-supplied functions are ACTUALLY used" check).
    default_score = schema_consistency_split_half(coherent_traces, coherence_fn=None)
    assert default_score == coherent_score, (
        f"coherence_fn=None must reproduce the default cosine metric byte-for-byte, got "
        f"{default_score} vs {coherent_score}")
    sentinel_calls = []

    def _sentinel_coherence_fn(a, b):
        sentinel_calls.append((len(a), len(b)))
        return 0.777

    swapped_score = schema_consistency_split_half(coherent_traces, coherence_fn=_sentinel_coherence_fn)
    assert swapped_score == 0.777, (
        f"COHERENCE_FN NOT LOAD-BEARING: a caller-supplied coherence_fn must override the default "
        f"metric, got {swapped_score}")
    assert len(sentinel_calls) == 1 and sentinel_calls[0] == (2, 2), (
        f"coherence_fn must be called exactly once with the two half-lists, got {sentinel_calls}")

    # (3) Library.flag: appends + terminal no-op.
    lib = Library()
    assert lib.flag("catch", "e0", "POS", v1, 1) is True
    it = lib.items["catch"]
    assert len(it.traces) == 1
    it.status = "ESCALATED"
    assert lib.flag("catch", "e1", "POS", v1, 2) is False, "terminal item must reject new traces"
    assert len(lib.items["catch"].traces) == 1

    # (4) consolidation_pass: intervening-pass rule + guard-gated banking, real coherent item.
    lib2 = Library()
    for i in range(4):
        lib2.flag("mendtest", f"m{i}", "POS", context_vector("Owen mended the boat before the storm."), 1)
    r1 = consolidation_pass(lib2, 1, min_confirm=3, schema_thresh=0.10, register=False)
    assert lib2.items["mendtest"].status == "PENDING", (
        "must NOT ground on the very pass it first reaches min_confirm (Dumay-Gaskell rule)")
    assert r1["cumulative_grounded"] == 0
    r2 = consolidation_pass(lib2, 2, min_confirm=3, schema_thresh=0.10, register=False)
    assert lib2.items["mendtest"].status == "GROUNDED_POS", (
        f"coherent-context+consistent-vote item must ground on the intervening pass, got "
        f"{lib2.items['mendtest'].status}")
    assert "mendtest" in r2["newly_grounded_pos"]

    # (5) consolidation_pass: the guard REJECTS consistent-vote-but-scrambled-context (false-
    # consolidation can-fail case) -- must ESCALATE after patience_max, never GROUND.
    lib3 = Library()
    rng2 = np.random.default_rng(1)
    for i in range(4):
        lib3.flag("adversarialtest", f"a{i}", "POS", rng2.choice([-1.0, 1.0], size=D), 1)
    for p in range(1, 6):
        consolidation_pass(lib3, p, min_confirm=3, schema_thresh=0.10, patience_max=3, register=False)
    assert lib3.items["adversarialtest"].status == "ESCALATED", (
        f"scrambled-context item with consistent votes must ESCALATE not GROUND, got "
        f"{lib3.items['adversarialtest'].status}")

    # (6) real-code-path: actually call the REUSED hdlab.consequence_learning_loop referent-linked
    # credit scan on its own hand-authored micro-episode (not a synthetic-only branch). Uses
    # _credit_targets directly (byte-identical to consequence_learning_loop.self_test's own check)
    # since this particular window has no teacher_verdict (credit_window would return None for a
    # reason orthogonal to what this check tests: referent-linked OOV credit-scanning itself).
    g_lantern = "Nell wanted to fix the lantern before the guests came"
    win_credit = "Nell tinkered the lantern and the savings dwindled in the drawer."
    tgts = _credit_targets(win_credit, "lantern")
    assert "tinker" in tgts, f"real _credit_targets call did not credit 'tinker' as expected, got {tgts}"
    # and teacher_verdict (the OTHER real half credit_window composes) on a pair that DOES fire.
    g_save = "Owen wanted to save the boat before the storm hit"
    win_unmet = "The men worked hard. The boat sank in the storm."
    tv = teacher_verdict(g_save, win_unmet, signal_mode="signal_a_only")
    assert tv == "UNMET", f"real teacher_verdict call did not fire UNMET as expected, got {tv}"
    # credit_window itself composes both (verified separately above since this particular hand-
    # authored pair has no NOVEL credit target -- 'sank' is already lexicon-known -- exactly why
    # consequence_learning_loop.py's own self_test tests these two halves on separate examples too).
    assert credit_window(g_save, win_unmet, "boat", signal_mode="signal_a_only") is None, (
        "credit_window must return None when teacher fires but no OOV target is referent-linked")

    # (7) PROMOTE connector: real HDFactStore, real code path (not a synthetic-only branch).
    # 7a. high-exposure, highly-consistent, coherent-context item MUST bank AND promote.
    store = HDFactStore(n_dim=1024, seed=7)
    lib4 = Library()
    ctx_ok = context_vector("Nell repaired the engine before the harvest.")
    for i in range(8):
        lib4.flag("repairtest", f"r{i}", "POS", ctx_ok, 1)
    consolidation_pass(lib4, 1, min_confirm=4, schema_thresh=0.10, register=False, native_store=store,
                       promote_min_exposure=8, promote_min_consistency=0.75)
    r_promote = consolidation_pass(lib4, 2, min_confirm=4, schema_thresh=0.10, register=False,
                                   native_store=store, promote_min_exposure=8,
                                   promote_min_consistency=0.75)
    assert lib4.items["repairtest"].status == "GROUNDED_POS"
    assert any(e["lemma"] == "repairtest" and e["promoted"] for e in r_promote["promotion_log"]), (
        f"high-exposure consistent item must promote, log={r_promote['promotion_log']}")
    native_hit = store.query("repairtest", "OUTCOME_POLARITY")
    assert native_hit and native_hit[0]["object"] == "POS", (
        f"promoted fact must be readable lookup-free from hd_fact_store, got {native_hit}")

    # 7b. GUARD: same coherent context, same exposure count, but a merely-adequate (not highly
    # consistent) vote history -- must BANK (clears the low banking bar) but must NOT promote (fails
    # the strictly-stronger consistency bar). This is the sharp case DRILL 2 named: banking's own
    # vote-margin gate is much weaker than genuine automaticity requires.
    lib5 = Library()
    for i in range(6):
        lib5.flag("weaktest", f"w{i}", "POS", ctx_ok, 1)
    for i in range(2):
        lib5.flag("weaktest", f"wn{i}", "NEG", ctx_ok, 1)
    consolidation_pass(lib5, 1, min_confirm=4, schema_thresh=0.10, register=False, native_store=store,
                       promote_min_exposure=8, promote_min_consistency=0.75)
    r_guard = consolidation_pass(lib5, 2, min_confirm=4, schema_thresh=0.10, register=False,
                                 native_store=store, promote_min_exposure=8,
                                 promote_min_consistency=0.75)
    assert lib5.items["weaktest"].status == "GROUNDED_POS", (
        f"margin=0.5 (6 POS/2 NEG) must clear the banking bar (>0.34), got "
        f"{lib5.items['weaktest'].status}")
    assert not any(e["lemma"] == "weaktest" and e["promoted"] for e in r_guard["promotion_log"]), (
        f"consistency=0.5 (<0.75 promote floor) item must NOT promote despite banking, "
        f"log={r_guard['promotion_log']}")
    assert store.query("weaktest", "OUTCOME_POLARITY") == [], (
        "guard leak: an inconsistent-but-banked item is readable from native_store")

    # (8) PBV hypothesis: propose -> confirm -> disconfirm -> abandon -> re-propose, with the
    # BACKWARD-COMPAT check first (no fns supplied => no hypothesis state touched at all).
    lib6 = Library()
    lib6.flag("compat", "c0", "POS", v1, 1)
    assert lib6.items["compat"].hypothesis is None and lib6.items["compat"].hypothesis_log == [], (
        "flag() without propose_fn/verify_fn must not touch hypothesis state (backward compat)")

    # scripted verifier: returns the next verdict in a queue; None means UNINFORMATIVE.
    verdicts: List[Optional[bool]] = [None, True, False, False]
    proposals = ["alpha", "beta"]
    prop_calls: List[str] = []

    def _prop(item, tr):
        if not proposals:
            return None
        obj = proposals.pop(0)
        prop_calls.append(obj)
        return (obj, 0.9)

    def _ver(item, tr):
        return verdicts.pop(0) if verdicts else None

    lib7 = Library()
    for i in range(5):
        lib7.flag("pbvtest", f"p{i}", "POS", v1, 1, propose_fn=_prop, verify_fn=_ver)
    it7 = lib7.items["pbvtest"]
    events = [e["event"] for e in it7.hypothesis_log]
    assert events[0] == "PROPOSE" and prop_calls[0] == "alpha", (events, prop_calls)
    # t1 PROPOSE(alpha, s=0.5); t2 UNINFORMATIVE (no event, no strength change);
    # t3 CONFIRM -> 0.75; t4 DISCONFIRM -> 0.375; t5 DISCONFIRM -> 0.1875 <= 0.2 -> ABANDON+REPROPOSE
    assert events == ["PROPOSE", "CONFIRM", "DISCONFIRM", "DISCONFIRM", "ABANDON", "REPROPOSE"], events
    assert it7.n_abandoned == 1 and it7.rejected == ["alpha"], (it7.n_abandoned, it7.rejected)
    assert it7.hypothesis is not None and it7.hypothesis.obj == "beta", it7.hypothesis
    assert abs(it7.hypothesis.strength - 0.5) < 1e-12, "re-proposal must start at init_strength"
    conf_ev = [e for e in it7.hypothesis_log if e["event"] == "CONFIRM"][0]
    assert abs(conf_ev["strength"] - 0.75) < 1e-9, conf_ev
    aband = [e for e in it7.hypothesis_log if e["event"] == "ABANDON"][0]
    assert abs(aband["strength"] - 0.1875) < 1e-9, aband
    assert aband["n_confirm"] == 1 and aband["n_disconfirm"] == 2, aband
    assert len(it7.traces) == 5, "every encounter must still append a trace regardless of verdict"

    # (8b) UNINFORMATIVE encounters must leave strength EXACTLY unchanged (Medina ~90% census --
    # if uninformative encounters moved the strength the mechanism would be an accumulator again).
    lib8 = Library()
    lib8.flag("uninf", "u0", "POS", v1, 1, propose_fn=lambda i, t: ("gamma_obj", 0.8),
              verify_fn=lambda i, t: None)
    for i in range(1, 5):
        lib8.flag("uninf", f"u{i}", "POS", v1, 1, propose_fn=lambda it_, t: ("never", 0.1),
                  verify_fn=lambda it_, t: None)
    h8 = lib8.items["uninf"].hypothesis
    assert h8 is not None and h8.obj == "gamma_obj" and h8.strength == PBV_INIT_STRENGTH, h8
    assert h8.n_uninformative == 4 and h8.n_confirm == 0 and h8.n_disconfirm == 0, h8

    # (8c) pbv_update_strength: pure, monotone, bounded.
    assert abs(pbv_update_strength(0.5, True, 0.5) - 0.75) < 1e-12
    assert abs(pbv_update_strength(0.5, False, 0.5) - 0.25) < 1e-12
    assert pbv_update_strength(0.99, True, 0.5) < 1.0, "confirm must asymptote below 1"
    # a well-confirmed hypothesis resists a single disconfirmation (Pursuit persisting strength)
    s = PBV_INIT_STRENGTH
    for _ in range(3):
        s = pbv_update_strength(s, True)
    assert pbv_update_strength(s, False) > PBV_ABANDON_STRENGTH, (
        "a 3x-confirmed hypothesis must survive one disconfirmation (persisting strength)")

    # (9) ESCALATED is no longer terminal WHEN revive_terminal=True, and still terminal by default.
    lib9 = Library()
    lib9.flag("esc", "e0", "POS", v1, 1)
    lib9.items["esc"].status = "ESCALATED"
    assert lib9.flag("esc", "e1", "POS", v1, 2) is False, "default must keep ESCALATED terminal"
    assert lib9.flag("esc", "e1", "POS", v1, 2, revive_terminal=True) is True, (
        "revive_terminal=True must re-open an ESCALATED item")
    assert lib9.items["esc"].status == "PENDING" and lib9.items["esc"].n_revivals == 1
    lib9.items["esc"].status = "ESCALATED"
    assert lib9.flag("esc", "e2", "POS", v1, 3, revive_terminal=True) is True
    lib9.items["esc"].status = "ESCALATED"
    assert lib9.flag("esc", "e3", "POS", v1, 4, revive_terminal=True) is False, (
        "revival must be BOUNDED by max_revivals so the loop still terminates")
    lib9.flag("grounded_item", "g0", "POS", v1, 1)
    lib9.items["grounded_item"].status = "GROUNDED_POS"
    assert lib9.flag("grounded_item", "g1", "POS", v1, 2, revive_terminal=True) is False, (
        "revive_terminal must NEVER revive a GROUNDED item, only an ESCALATED one")

    return {
        "context_vector_deterministic": True,
        "schema_metric_discriminant_valid": True,
        "coherent_score": round(coherent_score, 4),
        "scrambled_score": round(scrambled_score, 4),
        "intervening_pass_rule_ok": True,
        "guard_rejects_scrambled_context_ok": True,
        "real_credit_window_exercised": True,
        "native_promotion_connector_ok": True,
        "native_promotion_guard_holds_ok": True,
        "pbv_backward_compat_ok": True,
        "pbv_propose_verify_abandon_repropose_ok": True,
        "pbv_uninformative_leaves_strength_unchanged_ok": True,
        "pbv_persisting_strength_resists_one_disconfirm_ok": True,
        "escalated_revivable_and_bounded_ok": True,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=2))
    print("ALL SELF-TESTS PASSED")
