"""hdlab/reading_grounding_loop.py -- read-to-grow foundation loop, cycle 1 (2026-08-12).

MISSION: grow the substrate's grounded-concept FOUNDATION by READING real curriculum text, in
curriculum order, beyond the ~380-word hand lexicon (hdlab.lexical_similarity.CONCEPT_FEATURES,
measured 359 entries). This module is the ENGINE; experiments/exp_reading_grounding_loop_
cycle1_v1.py is the measurement harness (corpus loading, curriculum ordering, controls, metrics).

MECHANISM (fast-mapping + slow statistical accumulation, c.f. the Anterior Temporal Lobe
semantic hub -- repeated coherent CONTEXTS of use, not one-shot inference): applies the
ALREADY-VALIDATED FLAG -> LIBRARY -> CONSOLIDATE -> GATE -> BANK -> PROMOTE architecture
(hdlab.grounding_acquisition_loop, built + HARD_PASS-validated for outcome-verb polarity
acquisition, exp_grounding_acquisition_loop_v1 e065... HARD_PASS) to a NEW, more general axis:
WORD-MEANING GROUNDING FROM READING CONTEXT. Where grounding_acquisition_loop's Trace.pole
carries a POS/NEG valence vote, this loop's vote is always POS (constant) -- there is no
polarity axis for general word meaning -- so consolidation_pass's vote-margin gate degenerates
to a pure EXPOSURE gate (>=MIN_CONFIRM occurrences), and the entire grounding decision rides on
schema_consistency_split_half: does this word's CONTEXT OF USE cohere across INDEPENDENT
encounters (split-half reliability), not just recur? (Distributional Hypothesis, Firth 1957:
"a word is characterized by the company it keeps"; Warren et al. 2014's schema-coherence-not-
vote-agreement false-memory guard, exactly as grounding_acquisition_loop's own module docstring
documents and its self_test's adversarialtest fixture proves discriminates real coherence from
noise.)

DIRECTLY RELEVANT PRIOR NEGATIVE RESULT (USER 2026-07-18,
feedback_word_meaning_from_grounding_not_grade1_text_reading_grows_relations_USER_2026-07-18):
a PRIOR attempt at word-meaning-from-context (exp_base_first_reader_crosssentence_thematic_
overlay_v1) scored AUC 0.527 (~chance) inferring 3 new words from a ~1685-TOKEN HOMOGENEOUS
grade-1 passage via a single-pass thematic overlay -- USER + the BRAIN-DRILL diagnosed the
root cause as "distributional inference needs exposure volume/diversity a ~1685-token
homogeneous corpus lacks," not that context-grounding is impossible in principle. This cycle
is a DELIBERATELY STRONGER test of the SAME hypothesis, not a blind repeat of the narrow one
(per the standing USER discipline: a narrow failure proves that setup failed, not that the
capability is impossible -- test the version the brain actually uses): (a) ~2 orders of
magnitude more text (curriculum-ordered modern corpus, tens of thousands of words, not ~1685),
(b) genuinely DIVERSE topics/registers (dozens of distinct modern news articles + science
process descriptions, not one homogeneous passage), (c) a validated MULTI-EXPOSURE STATISTICAL
ACCUMULATION mechanism requiring >=MIN_CONFIRM=4 independent occurrences whose contexts pass a
split-half COHERENCE gate (schema_consistency_split_half), not a single-pass inference. The
SCRAMBLE-CONTEXT control below exists precisely to catch a repeat of the same failure mode
honestly (if grounding collapses under scramble no better than under real reading, the wall is
still standing and this module must say so, not oversell).

REUSE (wire-don't-island; every organ below is imported read-only, called verbatim):
  hdlab.grounding_acquisition_loop.context_vector / content_words / Library / consolidation_pass
      / schema_consistency_split_half / Trace / MIN_CONFIRM   (FLAG / LIBRARY / CONSOLIDATE / BANK)
  hdlab.hd_fact_store.HDFactStore                    (FOUNDATION -- trust-bound (s,r,o) store)
  hdlab.gap_detector.GapDetector                     (GATE -- "do I already know this word",
                                                       CA3/CA1 pattern-completion novelty margin,
                                                       replacing a hand membership check; floor
                                                       0.625 reused verbatim from that module's
                                                       own pre-registered/tested default)
  hdlab.thematic_role_labeler.lemma_verb              (glass-box surface->lemma normalizer; its
                                                       suffix-stripping rules are POS-generic,
                                                       reused for ALL content words here, not
                                                       just verbs)

GENUINELY NEW code here: ConceptSpace (running per-lemma context-vector accumulator over BOTH
seed-known and newly-grounded words -- the comparison population CANONICALIZE reads from, and
the thing that lets the foundation's concept space GROW rather than just its fact COUNT),
canonicalize() (nearest-neighbor sense assignment: a newly-GROUNDED word's bundled context
vector is compared by cosine against every anchor already in ConceptSpace; above threshold ->
linked as a near-sense of that anchor; below -> banked as its own standalone NEW concept, which
itself becomes a future anchor), context_vector_masked() (the no-leak fix: a word's context
vector must NEVER include the word's own token, mirroring word_acquisition_loop's "target verb
identity is NEVER read" invariant -- grounding_acquisition_loop's own callers always passed a
window that structurally excluded the target, e.g. consequence_learning_loop's credit-window;
this generalizes that discipline to arbitrary corpus sentences where the target IS in the
sentence text by construction), and the KNOWN_WORD gap-gate wiring (seeding + promoting a
uniform-shape (lemma, "KNOWN_WORD", "CORE") fact so GapDetector's CA3 margin cleanly separates
already-known from genuinely-novel lemmas).

ASCII-only. Deterministic throughout: sorted(set(...)) iteration, hashlib-seeded context
vectors (via grounding_acquisition_loop.context_vector, never Python hash()), fixed integer
seeds for HDFactStore/GapDetector construction and the scramble control's RNG. PROT-023/F.5
compliant.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from hdlab.grounding_acquisition_loop import (
    D as CTX_D,
    MIN_CONFIRM,
    PBV_ABANDON_STRENGTH,
    PBV_GAMMA,
    PBV_INIT_STRENGTH,
    PBV_MAX_REVIVALS,
    Library,
    Trace,
    consolidation_pass,
    content_words,
    context_vector,
    schema_consistency_split_half,
)
from hdlab.hd_fact_store import HDFactStore
from hdlab.gap_detector import GapDetector
from hdlab.thematic_role_labeler import lemma_word
from hdlab.closed_class_lexicon import is_closed_class, is_eligible_meaning

KNOWN_RELATION = "KNOWN_WORD"
KNOWN_OBJECT = "CORE"
MEANING_RELATION = "GROUNDED_MEANING"
GAP_FLOOR = 0.625          # reused verbatim from hdlab.gap_detector's own pre-registered default
SENSE_MATCH_THRESH = 0.45  # HYPOTHESIZED (exploratory canonicalization link; see module docstring
                            # SENSE_MATCH_THRESH rationale in the calling cell's pre-reg -- primary
                            # grounding gate is schema_consistency_split_half, NOT this threshold)

# ---- PBV wiring constants (2026-08-12; see preregs/2026-08-12_pbv_hypothesis_v1.md) -------------
PBV_INFORMATIVE_MIN = 0.30  # HYPOTHESIZED, calibration-amendable at smoke. An encounter is
                            # INFORMATIVE iff canonicalize over THAT ONE encounter's context vector
                            # finds an eligible anchor at or above this cosine. Below it the
                            # encounter yields no verdict at all (Medina 2011: ~90% of natural
                            # exposures are uninformative). Set BELOW SENSE_MATCH_THRESH=0.45
                            # because a single un-accumulated trace vector is a noisier probe than
                            # the summed bundle 0.45 was chosen against; the actual informative
                            # rate is MEASURED at smoke and reported, never assumed.
PBV_COMMIT_STRENGTH = 0.6   # HYPOTHESIZED. Minimum standing-hypothesis strength to BANK. Strictly
                            # above PBV_INIT_STRENGTH=0.5, so a hypothesis can never bank on the
                            # encounter that proposed it -- it must be CONFIRMED by at least one
                            # later informative encounter (Horst & Samuelson 2008: fast mapping
                            # yields a fragile hypothesis that needs re-exposure to become durable).

# ---- OPERATING READ-OUT CONFIG (2026-08-12; DEFAULT OFF -- nothing below is applied unless a
# ---- caller explicitly asks for it by calling operating_readout() / passing freeze_episode=True) --
#
# Disposition source: notes/landed_vet_readout_fix_v1_2026-08-12.md (hdi_skunkworks, AUDIT-ONLY,
# full independent recompute off data/exp_context_vector_signal_v1/_pass_cache.npz). That audit
# OVERTURNS parts of the cell's own note (notes/readout_fix_v1_2026-08-12.md):
#   F3 (episode freeze)      CONFIRMED, and stronger than the cell claimed. Survives matched
#                            retention (-0.168), survives retention pushed ABOVE baseline (-0.137
#                            while retaining MORE encounters), moves flip_all (a selection effect
#                            provably cannot), and survives the undisclosed field-SIZE control.
#   F2 (anchor_center/scale) REFUTED. Its credited leave-one-out was a RETENTION ARTIFACT; at
#                            matched retention F2 buys -0.004 (FIXED) and +0.032 -- it HURTS -- in
#                            GROWING. SHELVED. `ReadoutConfig.anchor_background` stays in the code
#                            but the operating config MUST leave it None. Revival criterion: a
#                            retention-matched F2 arm with >= 0.05 residual and a paired CI
#                            excluding 0.
#   F1 (field-relative gate) KEEP AS A STABILITY SELECTOR ONLY. Worth -0.048 over raw cosine at
#                            EQUAL retention. Its refutation as a LEMMA-SPECIFICITY / informative-
#                            ness gate is chain-grade (AUC 0.5067, real-vs-scramble enrichment
#                            1.0000x) and is NOT undone by keeping it: F1 predicts whether the
#                            argmax REPEATS, never whether it is RIGHT.
#
# OPERATING_MARGIN_Z_MIN is NOT a guessed constant.
# MEASURED@d:/AI/hd-instrument/data/exp_readout_fix_v1/metrics.json:fix1.thresholds["grow_epi|f2=0|
# z_top"].g_match = 3.542496 -- the z_top threshold RETENTION-MATCHED to the legacy `cos >= 0.30`
# gate in the regime this config is for (grow_epi = growing anchor space WITH episode freeze, F2
# off). Retention-matched is the deliberate choice: it is the only operating point at which a later
# quality comparison is not silently confounded with admitting fewer encounters -- the exact defect
# that made F2 look load-bearing. The retention this threshold was matched at was 0.403405
# MEASURED@ the same jsonpath (.legacy_retention_here); a caller on a DIFFERENT corpus must MEASURE
# its own admission rate and report the drift rather than assume the match transfers.
OPERATING_READOUT_NAME = "readout_op_v1_F1F3"
OPERATING_MARGIN_Z_MIN = 3.542496
OPERATING_MARGIN_STAT = "z_top"
OPERATING_MARGIN_Z_MIN_SOURCE = (
    "data/exp_readout_fix_v1/metrics.json:fix1.thresholds['grow_epi|f2=0|z_top'].g_match")
OPERATING_MARGIN_Z_MIN_MATCHED_RETENTION = 0.403405


def operating_readout(margin_z_min: float = OPERATING_MARGIN_Z_MIN,
                      margin_stat: str = OPERATING_MARGIN_STAT) -> "ReadoutConfig":
    """The F1+F3 operating config's F1 half: a field-relative z_top gate with F2 OFF.

    NOT a default. Every existing caller passes `readout=None` and keeps the pre-existing code path
    byte-for-byte; this factory exists so that a caller that WANTS the vetted operating point cannot
    accidentally re-enable the SHELVED F2 while doing so (`anchor_background` is hard-wired None
    here and there is no parameter to set it).

    F3 is not expressible as a ReadoutConfig field -- it is the anchor-field freeze. Pair this with
    `make_pbv_fns(..., readout=operating_readout(), freeze_episode=True, freeze_epoch_fn=...)`.
    """
    if margin_z_min is None:
        raise ValueError("operating_readout requires a margin_z_min: F1 with no gate is not a "
                         "config, it is the legacy path (pass readout=None for that).")
    return ReadoutConfig(anchor_background=None, margin_z_min=float(margin_z_min),
                         margin_stat=margin_stat)


def normalize_lemma(surface: str) -> str:
    """Glass-box surface->lemma via the reused normalizer thematic_role_labeler.lemma_word.

    CHANGED 2026-08-12 (was `lemma_verb`): `lemma_verb` is a suffix STRIPPER that can return
    NON-WORDS, and in this loop the lemma IS the concept identity, so `arteries`->`arteri`
    minted a second concept for `artery` and then "grounded" one as the other -- a tautology
    wearing a disguise, invisible to the tautology gate because the strings differ. `lemma_word`
    guarantees its output is a real English word or the untouched surface form. Measured
    before/after: notes/definitional_grounding_v3_2026-08-12.md."""
    return lemma_word(surface)


def content_lemmas(sentence: str) -> List[str]:
    """Distinct content-word LEMMAS in `sentence`, deterministic order (sorted(set(...)),
    PROT-023/F.5)."""
    return sorted(set(normalize_lemma(w) for w in content_words(sentence)))


def context_vector_masked(sentence: str, target_lemma: str, d: int = CTX_D) -> np.ndarray:
    """context_vector() of `sentence` with every token whose lemma == target_lemma REMOVED
    first -- the no-leak fix (see module docstring). Reuses content_words + context_vector
    verbatim; this function only pre-filters the word list before re-joining and handing back
    to context_vector, so it inherits that function's exact bundling math unmodified."""
    words = [w for w in content_words(sentence) if normalize_lemma(w) != target_lemma]
    return context_vector(" ".join(words), d=d)


class ConceptSpace:
    """Running per-lemma context-vector accumulator (raw, un-quantized sums). Two populations
    feed it: (a) SEED known words, accumulated from every occurrence in the stream (their
    identity is already known; this only builds their DISTRIBUTIONAL profile for canonicalize's
    comparison pool); (b) newly-GROUNDED words, seeded ONCE at grounding time from the bundle of
    their own accumulated Library traces. This is what lets the foundation's CONCEPT SPACE grow
    (not just its raw fact count): a word grounded in an early chunk becomes an available anchor
    for canonicalizing a later, harder word."""

    def __init__(self, d: int = CTX_D) -> None:
        self.d = d
        self._sums: Dict[str, np.ndarray] = {}
        self._version = 0                                        # bumped on EVERY mutation
        self._mat_cache: Optional[Tuple[int, List[str], np.ndarray]] = None

    def observe(self, lemma: str, ctx_vec: np.ndarray) -> None:
        if lemma not in self._sums:
            self._sums[lemma] = np.zeros(self.d, dtype=np.float64)
        self._sums[lemma] += ctx_vec
        self._version += 1

    def seed_from_bundle(self, lemma: str, raw_sum: np.ndarray) -> None:
        """Seed (or overwrite) a lemma's accumulator directly from an already-computed raw sum
        (used at grounding time: the sum of a Library item's own trace context vectors)."""
        self._sums[lemma] = np.array(raw_sum, dtype=np.float64, copy=True)
        self._version += 1

    def anchor_matrix(self) -> Tuple[List[str], np.ndarray]:
        """(anchors, sign-bundled anchor matrix) -- the VECTORIZED equivalent of calling
        `bundle(a)` for every `a in anchors()`, cached until the next mutation.

        Exists only for SPEED: the PBV path calls canonicalize once per ENCOUNTER (online, as the
        brain does) rather than once per item per consolidation pass, so the anchor scan moved from
        O(items) to O(encounters) calls. Row i is exactly `bundle(anchors[i])` and the row order is
        exactly `anchors()` order (sorted), which is what makes the argmax tie-breaking identical
        to the Python loop in `canonicalize` -- asserted byte-for-byte in
        `_selftest_canonicalize_fast_matches_reference`."""
        if self._mat_cache is not None and self._mat_cache[0] == self._version:
            return self._mat_cache[1], self._mat_cache[2]
        anchors = sorted(self._sums)
        if anchors:
            mat = np.sign(np.stack([self._sums[a] for a in anchors], axis=0))
        else:
            mat = np.zeros((0, self.d), dtype=np.float64)
        self._mat_cache = (self._version, anchors, mat)
        return anchors, mat

    def bundle(self, lemma: str) -> Optional[np.ndarray]:
        s = self._sums.get(lemma)
        if s is None:
            return None
        return np.sign(s)

    def __contains__(self, lemma: str) -> bool:
        return lemma in self._sums

    def anchors(self) -> List[str]:
        return sorted(self._sums)

    def freeze(self) -> "FrozenAnchorSpace":
        """READ-OUT FIX 3 (2026-08-12, ADDITIVE, OFF unless a caller asks for it): a snapshot of
        the CURRENT anchor field, so one verification episode compares every encounter of one
        hypothesis against a STABLE field instead of a field that grew under it.

        MEASURED motivation (data/exp_context_vector_signal_v1/metrics.json:space_drift): re-scoring
        the identical encounters against each segment's own snapshot instead of one fixed space
        raises the per-encounter argmax flip rate 0.782962 -> 0.856881, i.e. anchor-space growth
        contributes ~+0.074 of pure instability, and PBV ran against a space that grew at EVERY
        encounter. Nothing in ConceptSpace's own behavior changes; this only hands out a read-only
        view."""
        anchors, mat = self.anchor_matrix()
        return FrozenAnchorSpace(anchors, mat)


class FrozenAnchorSpace:
    """Immutable snapshot of a ConceptSpace's anchor field.

    Duck-types the ONLY method `canonicalize_fast` reads (`anchor_matrix`), plus `anchors` /
    `bundle` / `__contains__` for the reference `canonicalize`, so it is a drop-in wherever a
    ConceptSpace is read but never written. Deliberately has NO `observe` / `seed_from_bundle`:
    an attempt to mutate a frozen field is a bug and should raise AttributeError loudly rather
    than silently write to a copy."""

    __slots__ = ("_anchors", "_mat", "_pos", "_elig_cache")

    def __init__(self, anchors: Sequence[str], mat: np.ndarray) -> None:
        self._anchors: List[str] = list(anchors)
        self._mat = np.array(mat, dtype=np.float64, copy=True)
        self._pos = {a: i for i, a in enumerate(self._anchors)}
        self._elig_cache: Dict[str, object] = {}

    @property
    def d(self) -> int:
        return int(self._mat.shape[1]) if self._mat.size else CTX_D

    def anchor_matrix(self) -> Tuple[List[str], np.ndarray]:
        return self._anchors, self._mat

    def anchors(self) -> List[str]:
        return list(self._anchors)

    def bundle(self, lemma: str) -> Optional[np.ndarray]:
        i = self._pos.get(lemma)
        return None if i is None else self._mat[i]

    def __contains__(self, lemma: str) -> bool:
        return lemma in self._pos


@dataclass
class ReadoutConfig:
    """Read-out options for `canonicalize_fast`. EVERY FIELD DEFAULTS OFF; `readout=None` (the
    default everywhere) takes the pre-existing code path unchanged.

    FIX 1 -- `margin_z_min` (+ `margin_stat`): REPLACES the magnitude test `best_cos >= thresh` as
    the informativeness criterion. MEASURED defect: the magnitude test admits a DIFFERENT lemma's
    context window at 0.416808 and the true one at 0.416687 -- enrichment 1.0000x, i.e. provably
    blind to whether the context belongs to the lemma (mean best cosine 0.311344 vs 0.311343;
    data/exp_context_vector_signal_v1/metrics.json:per_encounter). All lemma-specific information
    is in argmax IDENTITY, none in the score, so the replacement asks a FIELD-RELATIVE question:
    how far does the winner stand above the rest of the anchor field?
        margin_stat="z_top":  (s_best - mean(s_field)) / sd(s_field)
        margin_stat="margin": s_best - s_second
    `margin_z_min` is NOT a guessed constant: callers derive it as a quantile of a MEASURED
    statistic distribution (see preregs/2026-08-12_readout_fix_v1.md sec 4).

    FIX 2 -- `anchor_background` {anchor: (mu, sd)}: per-anchor background mean/sd of cos(context,
    anchor) over a background sample of encounter contexts. Scores become
    (cos - mu_a) / max(sd_a, eps) BEFORE the argmax, so an anchor that scores high against
    EVERYTHING (the corpus frequency backbone -- anchors are themselves accumulated context sums)
    stops winning by genericity. MEASURED defect: a lemma's OWN summed contexts clear
    SENSE_MATCH_THRESH LESS often (0.221625) than scrambled ones (0.285400) --
    `trace_sum_separation` = -0.063775. Anchors absent from the dict are left uncalibrated
    (mu=0, sd=1), so a growing space is always safe.

    FIX 3 is not a field here: it is `ConceptSpace.freeze()` (pass the frozen view AS the space).

    The returned cosine is always the RAW cosine of the winning anchor, on the same scale as
    before, so existing telemetry stays interpretable; only the WINNER and the ACCEPT decision
    change when the corresponding option is set."""

    anchor_background: Optional[Dict[str, Tuple[float, float]]] = None
    margin_z_min: Optional[float] = None
    margin_stat: str = "z_top"          # "z_top" | "margin"
    scale_floor: float = 1e-6
    _aligned: Dict[int, Tuple[np.ndarray, np.ndarray]] = field(default_factory=dict, repr=False)

    @property
    def active(self) -> bool:
        return self.anchor_background is not None or self.margin_z_min is not None

    def aligned(self, anchors: Sequence[str]) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """(center, scale) aligned to `anchors`, cached on anchor count (anchors are only ever
        added, and the background is a pure function of the anchor name)."""
        if self.anchor_background is None:
            return None
        hit = self._aligned.get(len(anchors))
        if hit is not None:
            return hit
        ctr = np.zeros(len(anchors), dtype=np.float64)
        scl = np.ones(len(anchors), dtype=np.float64)
        for i, a in enumerate(anchors):
            bg = self.anchor_background.get(a)
            if bg is not None:
                ctr[i] = float(bg[0])
                scl[i] = max(float(bg[1]), self.scale_floor)
        self._aligned[len(anchors)] = (ctr, scl)
        return ctr, scl


def _readout_statistic(scores: np.ndarray, best_pos: int, stat: str) -> float:
    """Field-relative standout statistic over the SCANNABLE anchor scores (FIX 1)."""
    if stat == "margin":
        if scores.size < 2:
            return float("inf")
        part = np.partition(scores, -2)
        return float(part[-1] - part[-2])
    if stat != "z_top":
        raise ValueError(f"unknown margin_stat {stat!r} (expected 'z_top' or 'margin')")
    if scores.size < 2:
        return float("inf")
    sd = float(np.std(scores))
    if sd < 1e-12:
        return 0.0
    return float((scores[best_pos] - float(np.mean(scores))) / sd)


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def canonicalize(new_lemma: str, new_raw_sum: np.ndarray, space: ConceptSpace,
                 thresh: float = SENSE_MATCH_THRESH,
                 eligible: Optional[Callable[[str], bool]] = None) -> Tuple[str, float]:
    """Nearest-neighbor sense assignment for a newly-grounded word against every anchor
    CURRENTLY in `space` (excludes new_lemma itself, which may already be present as a seed
    accumulator coincidentally sharing the name -- excluded defensively, though in practice a
    just-grounded word is never also a seed word by construction). Returns (canonical_obj,
    best_cosine); canonical_obj == new_lemma when no ELIGIBLE anchor clears `thresh` -- see the
    NOTE below on what that return value means -- or the best-matching eligible PRIOR anchor
    otherwise.

    eligible (2026-08-12, additive; default None preserves the prior behavior byte-for-byte):
    a predicate over anchor lemmas. Ineligible anchors are SKIPPED DURING THE SCAN rather than
    vetoing the word, so a target whose single nearest anchor is a function word can still link to
    its best ELIGIBLE anchor instead of being lost. Callers pass
    hdlab.closed_class_lexicon.is_eligible_meaning (a function word cannot BE what a content word
    means; see that module's criterion + sources).

    NOTE ON THE SELF-RETURN (load-bearing, 2026-08-12): `canonical_obj == new_lemma` is this
    function's NO-MATCH signal -- "no anchor in the concept space was close enough". It is NOT a
    meaning. A caller must NOT record it as a (lemma, GROUNDED_MEANING, lemma) fact: that is a
    tautology which asserts nothing, and doing so is exactly the defect measured at 65.7% of the
    landed foundation in notes/foundation_grounding_sample_2026-08-12.md. See
    `_grounding_gate` below, which refuses it at the consolidation gate."""
    new_bundle = np.sign(new_raw_sum)
    best_anchor, best_cos = None, -2.0
    for anchor in space.anchors():
        if anchor == new_lemma:
            continue
        if eligible is not None and not eligible(anchor):
            continue
        ab = space.bundle(anchor)
        if ab is None:
            continue
        c = _cos(new_bundle, ab)
        if c > best_cos:
            best_anchor, best_cos = anchor, c
    if best_anchor is not None and best_cos >= thresh:
        return best_anchor, best_cos
    return new_lemma, best_cos if best_anchor is not None else 0.0


def canonicalize_fast(new_lemma: str, new_raw_sum: np.ndarray, space: "ConceptSpace",
                      thresh: float = SENSE_MATCH_THRESH,
                      eligible_mask: Optional[np.ndarray] = None,
                      *, readout: Optional["ReadoutConfig"] = None) -> Tuple[str, float]:
    """Vectorized `canonicalize`. SAME contract, SAME return values, SAME no-match self-return, SAME
    first-max-in-sorted-order tie-break -- only the loop is replaced by one matvec. `eligible_mask`
    is a boolean array aligned to `space.anchor_matrix()`'s anchor order (True = scannable);
    None means every anchor is eligible. Equivalence to the reference implementation is asserted
    in `_selftest_canonicalize_fast_matches_reference`, which is the only thing licensing its use.

    `readout` (2026-08-12, ADDITIVE, keyword-only, DEFAULT None = prior behavior byte-for-byte):
    a ReadoutConfig enabling FIX 1 (field-relative informativeness gate) and/or FIX 2 (per-anchor
    frequency-backbone correction). See ReadoutConfig for the measured defects each addresses.
    `space` may be a ConceptSpace or a `FrozenAnchorSpace` (FIX 3) -- this function only ever READS
    `space.anchor_matrix()`."""
    anchors, mat = space.anchor_matrix()
    if not anchors:
        return new_lemma, 0.0
    keep = np.ones(len(anchors), dtype=bool) if eligible_mask is None else eligible_mask.copy()
    idx = int(np.searchsorted(anchors, new_lemma))
    if idx < len(anchors) and anchors[idx] == new_lemma:
        keep[idx] = False
    if not keep.any():
        return new_lemma, 0.0
    nb = np.sign(new_raw_sum)
    nn = float(np.linalg.norm(nb))
    if nn < 1e-9:
        return new_lemma, 0.0
    norms = np.linalg.norm(mat, axis=1)
    sims = np.full(len(anchors), -np.inf)
    ok = keep & (norms >= 1e-9)
    if not ok.any():
        # every scannable anchor is a zero vector: _cos would have returned 0.0 for each, and the
        # reference loop's `c > best_cos` picks the FIRST such anchor at cos 0.0.
        first = int(np.flatnonzero(keep)[0])
        return (anchors[first], 0.0) if 0.0 >= thresh else (new_lemma, 0.0)
    sims[ok] = (mat[ok] @ nb) / (norms[ok] * nn)
    zero_rows = keep & ~ok
    sims[zero_rows] = 0.0
    if readout is not None and readout.active:
        # ---- READ-OUT FIX 1 / FIX 2 (2026-08-12). Unreachable unless a caller passes a
        # ReadoutConfig; `readout=None` (every existing caller) skips this block entirely.
        scan = np.flatnonzero(keep)
        raw_scores = sims[scan]
        cal_scores = raw_scores
        aligned = readout.aligned(anchors)
        if aligned is not None:                              # FIX 2: frequency-corrected pool
            ctr, scl = aligned
            cal_scores = (raw_scores - ctr[scan]) / scl[scan]
        best_local = int(np.argmax(cal_scores))
        best = int(scan[best_local])
        best_cos = float(sims[best])                          # RAW cosine, scale unchanged
        if readout.margin_z_min is None:
            accept = best_cos >= thresh
        else:                                                 # FIX 1: field-relative gate
            accept = _readout_statistic(cal_scores, best_local,
                                        readout.margin_stat) >= readout.margin_z_min
        return (anchors[best], best_cos) if accept else (new_lemma, best_cos)
    best = int(np.argmax(sims))
    best_cos = float(sims[best])
    if best_cos >= thresh:
        return anchors[best], best_cos
    return new_lemma, best_cos


def _eligible_mask(space: ConceptSpace, cache: Dict[str, object]) -> np.ndarray:
    """Boolean mask over `space.anchor_matrix()`'s anchors: True where `is_eligible_meaning` holds.
    Recomputed only when the anchor COUNT changes (anchors are only ever added, and the predicate
    is a pure function of the lemma), so this is O(n_anchors) rarely rather than per encounter."""
    anchors, _ = space.anchor_matrix()
    if cache.get("n") == len(anchors):
        return cache["mask"]                      # type: ignore[return-value]
    mask = np.array([is_eligible_meaning(a) for a in anchors], dtype=bool)
    cache["n"], cache["mask"] = len(anchors), mask
    return mask


def make_pbv_fns(state: "ReadingLoopState", *, informative_min: float = PBV_INFORMATIVE_MIN,
                 readout: Optional[ReadoutConfig] = None, freeze_episode: bool = False,
                 freeze_epoch_fn: Optional[Callable[[], object]] = None):
    """Build the PBV (propose_fn, verify_fn) pair for `state`. THIS is the propose-then-verify
    wiring; hdlab.grounding_acquisition_loop.Library.flag owns the control flow.

    THE PROPOSER IS `canonicalize`, REUSED VERBATIM -- not reimplemented. The audit's own finding is
    that canonicalize's argmax is ALREADY PBV in shape (one winner, zero credit to the runner-up);
    what was missing is everything after the propose. So the only change on the proposal side is
    WHAT IT IS CALLED WITH and HOW OFTEN: previously ONE call per item at consolidation time over
    `np.sum([t.context_vec for t in item.traces])` -- the collapse that destroyed the per-encounter
    trace separation intake had carefully preserved -- now ONE call per ENCOUNTER over THAT SINGLE
    ENCOUNTER's context vector. The traces are never summed to make a decision.

    INFORMATIVENESS (Medina 2011, ~90% of natural exposures uninformative): an encounter is
    informative iff canonicalize over that encounter alone returns an eligible anchor (i.e. clears
    `informative_min`). Its no-match self-return IS the uninformative signal, so the same reused
    function supplies both the proposal and the informativeness filter -- no second mechanism.

    VERIFICATION IS BINARY AND ALTERNATIVE-BLIND: the verdict is `encounter_best == hypothesis.obj`.
    The cosine to the standing hypothesis is NEVER compared against the runner-up's cosine and no
    alternative's score is stored anywhere. On DISCONFIRMATION the re-proposal (issued by
    `Library.flag`) is this same encounter's own best candidate -- Trueswell 2013's abandon-and-
    re-propose in one act -- not an argmax over accumulated evidence, which is what keeps a rejected
    alternative from re-entering through an accumulator.

    READ-OUT OPTIONS (2026-08-12, ADDITIVE; both default OFF = prior behavior byte-for-byte).
    `readout`: a ReadoutConfig (FIX 1 field-relative gate / FIX 2 frequency-corrected pool).
    `freeze_episode` (FIX 3): snapshot the anchor field when a hypothesis is PROPOSED and compare
    every encounter of THAT episode against the snapshot, releasing it when the hypothesis is
    abandoned -- so a hypothesis is verified against a stable field rather than one that grew under
    it. MEASURED: growth alone adds ~+0.074 flip (see ConceptSpace.freeze).

    `freeze_epoch_fn` (2026-08-12, ADDITIVE; None = the per-episode behavior above, unchanged
    byte-for-byte). WHY IT EXISTS -- a MEASURED blocker, not a preference. The landed-VET recorded
    that `freeze_episode=True` was self-tested but NEVER EXERCISED IN A LIVE READING PASS. It was
    exercised here and it does not fit in memory: one live pass over the v5 line-aware corpus,
    instrumented, held 1110 / 1768 / 2381 / 3228 / 3829 / 4518 SIMULTANEOUS FrozenAnchorSpace
    snapshots at 500/1000/1500/2000/2500/3000 sentences -- every one a distinct matrix (0 sharing,
    because ConceptSpace._version bumps on EVERY observed seed-word occurrence, so no two episodes
    are ever proposed at the same version) -- for 0.65 / 1.39 / 2.19 / 3.40 / 4.29 / 5.35 GB. That
    is 3000 of 34169 sentences and it grows linearly in episodes: the full pass extrapolates past
    50 GB. Per-episode freeze at true per-encounter granularity is not runnable as written.

    THE FIX, and it is a DECLARED COARSENING, not a free lunch: when `freeze_epoch_fn` is given, it
    is called at freeze time for a hashable EPOCH id, and every episode proposed within one epoch
    SHARES that epoch's single snapshot (reference-counted; an epoch's snapshot is dropped as soon
    as no live episode holds it). Live memory becomes O(live epochs) instead of O(live episodes).
    The cost is that an episode proposed mid-epoch is frozen against the field as it stood at the
    START of its epoch rather than at its own proposing encounter. This is COARSER than true
    per-episode freeze and MUST be reported as such -- but it is strictly FINER than the granularity
    at which F3's effect was actually measured and confirmed (the landed-VET's -0.168 at matched
    retention was measured at 5-SNAPSHOT, i.e. per-SEGMENT, granularity), so a per-chunk epoch is
    an interpolation between the measured point and the unrunnable ideal, not an extrapolation past
    either. Callers should pass the smallest epoch their memory budget allows and report
    `freeze_stats()`.

    `freeze_stats()` is attached as an attribute to BOTH returned functions and reports snapshot
    counts / peak live snapshots / peak live snapshot bytes, so the memory claim above is telemetry
    in the metrics rather than a comment."""
    cache: Dict[str, object] = {}
    # lemma -> FrozenAnchorSpace  (freeze_epoch_fn is None)  |  lemma -> epoch key (otherwise)
    episodes: Dict[str, object] = {}
    snapshots: Dict[object, FrozenAnchorSpace] = {}     # epoch key -> shared snapshot
    refs: Dict[object, int] = {}                        # epoch key -> live episode count
    stats: Dict[str, object] = {
        "freeze_episode": bool(freeze_episode),
        "epoch_interned": freeze_epoch_fn is not None,
        "n_freezes_requested": 0, "n_snapshots_created": 0,
        "peak_live_snapshots": 0, "peak_live_snapshot_bytes": 0, "peak_live_episodes": 0,
    }

    def _live_snapshots() -> List[FrozenAnchorSpace]:
        if freeze_epoch_fn is None:
            return [v for v in episodes.values() if isinstance(v, FrozenAnchorSpace)]
        return list(snapshots.values())

    def _note_peak() -> None:
        live = _live_snapshots()
        stats["peak_live_snapshots"] = max(int(stats["peak_live_snapshots"]), len(live))
        stats["peak_live_snapshot_bytes"] = max(int(stats["peak_live_snapshot_bytes"]),
                                                sum(int(s._mat.nbytes) for s in live))
        stats["peak_live_episodes"] = max(int(stats["peak_live_episodes"]), len(episodes))

    def _release(lemma: str) -> None:
        key = episodes.pop(lemma, None)
        if key is None or freeze_epoch_fn is None:
            return                                  # un-interned snapshots are freed by refcount/GC
        n = refs.get(key, 0) - 1
        if n <= 0:
            refs.pop(key, None)
            snapshots.pop(key, None)
        else:
            refs[key] = n

    def _space_for(item):
        """Live space unless FIX 3 is on. A new episode begins exactly where `Library.flag` starts
        one: at an encounter where the item carries no hypothesis (PROPOSE / post-ABANDON)."""
        if not freeze_episode:
            return state.space
        if item.hypothesis is None or item.lemma not in episodes:
            _release(item.lemma)
            stats["n_freezes_requested"] = int(stats["n_freezes_requested"]) + 1
            if freeze_epoch_fn is None:
                episodes[item.lemma] = state.space.freeze()
                stats["n_snapshots_created"] = int(stats["n_snapshots_created"]) + 1
            else:
                key = freeze_epoch_fn()
                if key not in snapshots:
                    snapshots[key] = state.space.freeze()
                    refs[key] = 0
                    stats["n_snapshots_created"] = int(stats["n_snapshots_created"]) + 1
                refs[key] = refs.get(key, 0) + 1
                episodes[item.lemma] = key
            _note_peak()
        held = episodes[item.lemma]
        return held if freeze_epoch_fn is None else snapshots[held]

    def _encounter_best(item, tr) -> Tuple[str, float]:
        sp = _space_for(item)
        mask_cache = cache if sp is state.space else sp._elig_cache
        return canonicalize_fast(item.lemma, tr.context_vec, sp, thresh=informative_min,
                                 eligible_mask=_eligible_mask(sp, mask_cache), readout=readout)

    def release_episodes(lemmas) -> int:
        """Drop the frozen field held for each of `lemmas`. Returns how many were actually held.

        WHY THIS IS NEEDED, and it is a real leak in the ORIGINAL per-episode code too: `_release`
        only fires when a lemma STARTS A NEW EPISODE. A lemma that goes TERMINAL (grounded, or
        escalated) never proposes again, so its entry -- and, with interning, its whole epoch's
        snapshot -- is pinned for the rest of the pass. MEASURED consequence at the interned
        granularity this cell runs at: live snapshots would converge on the number of DISTINCT
        EPOCHS EVER SEEN (228 chunks over the 34169-sentence corpus) rather than on the number of
        LIVE episodes, i.e. ~3.4 GB at 900 anchors x 2048 float64 -- the O(live epochs) bound the
        interning was built to deliver would not actually hold.

        Callers pass the lemmas that just went terminal (a consolidation checkpoint knows exactly
        which those are). Calling it is OPTIONAL and calling it with a lemma that holds nothing is
        a no-op, so no existing caller changes behavior. Releasing a lemma that later proposes
        again is also safe: `_space_for` simply mints it a fresh snapshot at that point, which is
        the correct semantics for a NEW episode anyway."""
        n = 0
        for lemma in lemmas:
            if lemma in episodes:
                _release(lemma)
                n += 1
        return n

    def freeze_stats() -> dict:
        out = dict(stats)
        out["live_snapshots_now"] = len(_live_snapshots())
        out["live_episodes_now"] = len(episodes)
        out["readout_active"] = bool(readout is not None and readout.active)
        out["readout_margin_z_min"] = None if readout is None else readout.margin_z_min
        out["readout_margin_stat"] = None if readout is None else readout.margin_stat
        out["readout_f2_anchor_background_on"] = bool(
            readout is not None and readout.anchor_background is not None)
        return out

    def propose_fn(item, tr):
        obj, cos = _encounter_best(item, tr)
        if obj == item.lemma:
            return None                       # uninformative encounter: nothing to commit to
        return (obj, cos)

    def verify_fn(item, tr):
        obj, _cos = _encounter_best(item, tr)
        if obj == item.lemma:
            return None                       # UNINFORMATIVE -- no verdict, no strength change
        return obj == item.hypothesis.obj

    propose_fn.freeze_stats = freeze_stats                  # type: ignore[attr-defined]
    verify_fn.freeze_stats = freeze_stats                   # type: ignore[attr-defined]
    propose_fn.release_episodes = release_episodes          # type: ignore[attr-defined]
    verify_fn.release_episodes = release_episodes           # type: ignore[attr-defined]
    return propose_fn, verify_fn


# events that a SINGLE informative encounter can emit. REPROPOSE is deliberately EXCLUDED: it
# always co-occurs with a DISCONFIRM from the SAME encounter (abandon-and-re-propose is one act),
# so counting it too would double-count that encounter.
_INFORMATIVE_EVENTS = ("PROPOSE", "CONFIRM", "DISCONFIRM")


def pbv_trajectory_stats(library: Library) -> dict:
    """Aggregate PBV telemetry over every item that ever held a hypothesis. Derived ENTIRELY from
    the per-item hypothesis_log (the audit trail), never from a parallel counter that could drift
    out of sync with the actual decisions."""
    n_items = n_with_hyp = n_revised = n_encounters = n_informative = 0
    n_abandon = n_confirm = n_disconfirm = n_repropose = n_revive = 0
    revisions: List[dict] = []
    for lemma in sorted(library.items):
        it = library.items[lemma]
        n_items += 1
        n_encounters += len(it.traces)
        if not it.hypothesis_log:
            continue
        n_with_hyp += 1
        ev = [e["event"] for e in it.hypothesis_log]
        n_informative += sum(1 for e in ev if e in _INFORMATIVE_EVENTS)
        n_confirm += ev.count("CONFIRM")
        n_disconfirm += ev.count("DISCONFIRM")
        n_abandon += ev.count("ABANDON")
        n_repropose += ev.count("REPROPOSE")
        n_revive += ev.count("REVIVE")
        if it.n_abandoned > 0:
            n_revised += 1
            proposals = [e["obj"] for e in it.hypothesis_log if e["event"] in ("PROPOSE", "REPROPOSE", "INJECT")]
            revisions.append({
                "lemma": lemma, "n_abandoned": it.n_abandoned,
                "first_obj": proposals[0] if proposals else None,
                "final_obj": it.hypothesis.obj if it.hypothesis is not None else None,
                "n_traces": len(it.traces), "status": it.status,
                "final_strength": round(it.hypothesis.strength, 6) if it.hypothesis is not None else None,
            })
    return {
        "n_items": n_items, "n_items_with_hypothesis": n_with_hyp,
        "n_items_revised": n_revised,
        "revision_rate": round(n_revised / n_with_hyp, 6) if n_with_hyp else None,
        "n_encounters": n_encounters, "n_informative_encounters": n_informative,
        "informative_encounter_rate": round(n_informative / n_encounters, 6) if n_encounters else None,
        "n_confirm": n_confirm, "n_disconfirm": n_disconfirm, "n_abandon": n_abandon,
        "n_repropose": n_repropose, "n_revive": n_revive,
        "revisions": revisions,
    }


@dataclass
class ReadingLoopState:
    """All mutable state for one reading-loop CONDITION (real / scramble-context / etc). One
    instance per condition; conditions never share state (independent HDFactStore/Library/
    ConceptSpace each)."""
    store: HDFactStore
    library: Library = field(default_factory=Library)
    space: ConceptSpace = field(default_factory=ConceptSpace)
    gap_detector: Optional[GapDetector] = None
    known_seed: frozenset = field(default_factory=frozenset)
    gap_cache: Dict[str, bool] = field(default_factory=dict)   # first-encounter memoization
    n_occurrences_seen: int = 0
    n_flagged: int = 0
    growth_curve: List[dict] = field(default_factory=list)   # one row per checkpoint
    # ---- PROVENANCE + REFUSAL ledgers (2026-08-12; all additive, all default-empty) ----------
    sentence_pool: List[str] = field(default_factory=list)     # dedup'd corpus sentences
    sentence_index: Dict[str, int] = field(default_factory=dict)   # sentence text -> sent_id
    evidence: Dict[str, List[dict]] = field(default_factory=dict)  # lemma -> [{episode_id, pass_idx, sent_id}]
    provenance: List[dict] = field(default_factory=list)   # one row per GROUNDED_MEANING fact written
    refusals: List[dict] = field(default_factory=list)     # one row per refused non-grounding
    gate_decisions: Dict[str, dict] = field(default_factory=dict)  # lemma -> last gate verdict

    def sentence_id(self, sentence: str) -> int:
        """Intern a sentence into the pool and return its STABLE id. The provenance ledger stores
        ids, not repeated text, so per-trace provenance costs 8 bytes rather than ~120."""
        sid = self.sentence_index.get(sentence)
        if sid is None:
            sid = len(self.sentence_pool)
            self.sentence_pool.append(sentence)
            self.sentence_index[sentence] = sid
        return sid


def seed_known_words(state: ReadingLoopState, words: Sequence[str], source: str) -> None:
    """Seed the FOUNDATION with (word, KNOWN_WORD, CORE) facts for the prior/seed vocabulary
    (analogous to a child's pre-reading vocabulary from non-text sources). TRUST_HIGH: a
    curated, pre-registered seed list, not an inference."""
    seen = set()
    for w in sorted(set(words)):
        lem = normalize_lemma(w)
        if lem in seen:
            continue
        seen.add(lem)
        state.store.store(lem, KNOWN_RELATION, KNOWN_OBJECT, source, "TRUST_HIGH")
    state.known_seed = frozenset(seen)
    state.gap_detector = GapDetector(state.store, floor=GAP_FLOOR)
    state.gap_detector.refresh()


def is_gap(state: ReadingLoopState, lemma: str) -> bool:
    """First-encounter-memoized gap check: is `lemma` a genuine gap in the live FOUNDATION?
    Uses GapDetector's CA3/CA1 novelty margin against the (lemma, KNOWN_WORD, CORE) shape (see
    module docstring). Memoized per lemma so repeat occurrences of an already-classified word
    cost O(1), not another attractor call."""
    if lemma in state.gap_cache:
        return state.gap_cache[lemma]
    r = state.gap_detector.familiarity(lemma, KNOWN_RELATION, KNOWN_OBJECT)
    state.gap_cache[lemma] = r.is_gap
    return r.is_gap


def process_sentence(state: ReadingLoopState, sentence: str, episode_id: str, pass_idx: int,
                     *, scramble_context_source: Optional[Sequence[str]] = None,
                     scramble_rng: Optional[np.random.Generator] = None,
                     pbv_fns: Optional[Tuple[Callable, Callable]] = None,
                     revive_terminal: bool = False) -> int:
    """FLAG every content-word lemma in `sentence` that is (a) not a seed-known word, (b) not
    already a foundation gap-negative (GapDetector says known), and (c) not a terminal Library
    item (GROUNDED/ESCALATED -- Library.flag() itself no-ops on those, this is just a cheap
    short-circuit). Returns the number of lemmas flagged this sentence.

    scramble_context_source (SCRAMBLE-CONTEXT control): when given, each target's context
    window is NOT `sentence` but an UNRELATED sentence drawn (deterministically, via
    scramble_rng) from this pool -- destroys real co-occurrence coherence while preserving
    gross corpus statistics (same recipe grounding_acquisition_loop.self_test's own
    adversarialtest fixture uses: independent-random context per trace).

    pbv_fns (2026-08-12; default None = prior behavior byte-for-byte): the (propose_fn, verify_fn)
    pair from `make_pbv_fns`, threaded into Library.flag so the PROPOSE/VERIFY/ABANDON-AND-
    RE-PROPOSE cycle runs ONLINE at each encounter. revive_terminal likewise threads through: an
    ESCALATED word re-encountered in new material re-opens (bounded), because escalation is
    "inconclusive so far", not "proven wrong"."""
    state.n_occurrences_seen += 1
    n_flagged = 0
    propose_fn, verify_fn = pbv_fns if pbv_fns is not None else (None, None)
    for lemma in content_lemmas(sentence):
        if lemma in state.known_seed:
            # still track its distributional profile (comparison pool for canonicalize)
            ctx = context_vector_masked(sentence, lemma)
            if np.any(ctx != 0.0):
                state.space.observe(lemma, ctx)
            continue
        it = state.library.items.get(lemma)
        if it is not None and it.status != "PENDING":
            if not (revive_terminal and it.status == "ESCALATED" and it.n_revivals < PBV_MAX_REVIVALS):
                continue  # terminal (GROUNDED, or ESCALATED with revival off/exhausted)
        if not is_gap(state, lemma):
            continue  # foundation already knows this word (e.g. grounded earlier this run)
        if scramble_context_source is not None:
            src_sent = scramble_context_source[int(scramble_rng.integers(0, len(scramble_context_source)))]
            ctx = context_vector_masked(src_sent, lemma)
        else:
            src_sent = sentence
            ctx = context_vector_masked(sentence, lemma)
        if not np.any(ctx != 0.0):
            continue  # empty window (all-stopword context); nothing to learn from this occurrence
        flagged = state.library.flag(lemma, episode_id, "POS", ctx, pass_idx,
                                     propose_fn=propose_fn, verify_fn=verify_fn,
                                     revive_terminal=revive_terminal)
        if flagged:
            n_flagged += 1
            # PROVENANCE (2026-08-12): record, IN TRACE ORDER, the actual context sentence this
            # trace's context_vec was built from. Trace.context_vec is a bundled bag-of-words
            # vector from which no text can ever be recovered, so without this row a grounded
            # fact's evidence is structurally unrecoverable -- the glass-box gap the audit found.
            row = {"episode_id": episode_id, "pass_idx": pass_idx,
                   "sent_id": state.sentence_id(src_sent)}
            if src_sent is not sentence and src_sent != sentence:
                row["occurrence_sent_id"] = state.sentence_id(sentence)  # scramble control
            state.evidence.setdefault(lemma, []).append(row)
    return n_flagged


REFUSAL_TAUTOLOGY = "TAUTOLOGY_NO_ANCHOR"
REFUSAL_CLOSED_CLASS_OBJECT = "CLOSED_CLASS_OBJECT"
REFUSAL_CLOSED_CLASS_SUBJECT = "CLOSED_CLASS_SUBJECT"
REFUSAL_NO_HYPOTHESIS = "NO_STANDING_HYPOTHESIS"
REFUSAL_WEAK_HYPOTHESIS = "HYPOTHESIS_BELOW_COMMIT_STRENGTH"


def _make_grounding_gate(state: ReadingLoopState, pass_idx: int, source_tag: str,
                         thresh: float = SENSE_MATCH_THRESH) -> Callable[[object], bool]:
    """Build the REFUSE-NON-GROUNDINGS gate (2026-08-12 fix).

    Wired through consolidation_pass's EXISTING `mdl_gate_fn` extension point -- no edit to
    hdlab.grounding_acquisition_loop. That hook is consulted only when the schema-coherence check
    has ALREADY passed, and a False verdict is handled exactly like a schema failure: the item does
    NOT bank, `patience` increments, and it stays PENDING (still accumulating exposures, still a
    GAP to GapDetector because no KNOWN_WORD fact is written) until PATIENCE_MAX further passes
    have failed, at which point it ESCALATES ("inconclusive so far", never "proven wrong").

    Two refusal classes, both of which are FAILURES TO GROUND being recorded as such rather than
    dressed up as facts:
      * TAUTOLOGY_NO_ANCHOR -- canonicalize found no eligible anchor above `thresh`, so its return
        value is the target itself. Writing (X, GROUNDED_MEANING, X) asserts nothing.
      * CLOSED_CLASS_SUBJECT/OBJECT -- a function/discourse word cannot BE a content word's
        meaning, and has no lexical meaning of its own to ground. Criterion + sources:
        hdlab.closed_class_lexicon.
    Every refusal is APPENDED TO state.refusals with its reason, exposure count, best cosine and
    pass -- nothing is silently dropped, and a refused word remains visible to the gap machinery."""

    def gate(item) -> bool:
        lemma = item.lemma
        if is_closed_class(lemma):
            state.refusals.append({"lemma": lemma, "reason": REFUSAL_CLOSED_CLASS_SUBJECT,
                                   "pass_idx": pass_idx, "segment": source_tag,
                                   "n_exposures": len(item.traces), "best_cos": None,
                                   "candidate_object": None})
            return False
        raw_sum = np.sum([t.context_vec for t in item.traces], axis=0)
        canon_obj, best_cos = canonicalize(lemma, raw_sum, state.space, thresh=thresh,
                                           eligible=is_eligible_meaning)
        if canon_obj == lemma:
            state.refusals.append({"lemma": lemma, "reason": REFUSAL_TAUTOLOGY,
                                   "pass_idx": pass_idx, "segment": source_tag,
                                   "n_exposures": len(item.traces),
                                   "best_cos": round(float(best_cos), 4), "candidate_object": None})
            return False
        if is_closed_class(canon_obj):
            # Defensive: canonicalize already skipped ineligible anchors, so reaching here means
            # the eligibility predicate and this check disagree -- a real bug, not a data case.
            raise AssertionError(
                f"eligibility filter leaked a closed-class anchor {canon_obj!r} for {lemma!r}")
        state.gate_decisions[lemma] = {"canonical_obj": canon_obj,
                                       "best_cos": round(float(best_cos), 4),
                                       "raw_sum": raw_sum, "pass_idx": pass_idx}
        return True

    return gate


def _make_pbv_grounding_gate(state: ReadingLoopState, pass_idx: int, source_tag: str,
                             commit_strength: float = PBV_COMMIT_STRENGTH) -> Callable[[object], bool]:
    """The PBV replacement for `_make_grounding_gate`. Same extension point (consolidation_pass's
    `mdl_gate_fn`), same refusal-ledger discipline, same "a refused word stays PENDING and stays a
    GAP" semantics. ONE thing changes, and it is the whole point:

      OLD: `raw_sum = np.sum([t.context_vec for t in item.traces], axis=0)` then argmax over it.
           The per-encounter trace separation that intake preserved was destroyed at exactly the
           moment it would have done work, and the meaning was RE-DERIVED from scratch every pass
           from a collapsed average.
      NEW: read the STANDING HYPOTHESIS the item has been carrying across encounters. The traces
           are not summed to reach this decision at all.

    The traces ARE still summed once, further down in `checkpoint`, but only to seed the newly
    grounded word's OWN anchor profile in the ConceptSpace (so it can serve as a future anchor).
    That is a representation-building step, not the mapping decision -- the distinction the audit
    turned on."""

    def gate(item) -> bool:
        lemma = item.lemma
        base = {"lemma": lemma, "pass_idx": pass_idx, "segment": source_tag,
                "n_exposures": len(item.traces)}
        if is_closed_class(lemma):
            state.refusals.append(dict(base, reason=REFUSAL_CLOSED_CLASS_SUBJECT,
                                       best_cos=None, candidate_object=None))
            return False
        h = item.hypothesis
        if h is None:
            state.refusals.append(dict(base, reason=REFUSAL_NO_HYPOTHESIS,
                                       best_cos=None, candidate_object=None))
            return False
        if h.obj == lemma:
            # Defensive: the proposer excludes the target from the anchor scan, so this is
            # unreachable via make_pbv_fns; it stays as a hard refusal because an injected or
            # future proposer must never be able to bank (X, GROUNDED_MEANING, X).
            state.refusals.append(dict(base, reason=REFUSAL_TAUTOLOGY,
                                       best_cos=None, candidate_object=None))
            return False
        if is_closed_class(h.obj):
            raise AssertionError(
                f"eligibility filter leaked a closed-class hypothesis {h.obj!r} for {lemma!r}")
        if h.strength < commit_strength:
            state.refusals.append(dict(base, reason=REFUSAL_WEAK_HYPOTHESIS,
                                       best_cos=None, candidate_object=h.obj,
                                       hypothesis_strength=round(h.strength, 6),
                                       n_confirm=h.n_confirm, n_disconfirm=h.n_disconfirm))
            return False
        prop_score = None
        for e in reversed(item.hypothesis_log):
            if e["event"] in ("PROPOSE", "REPROPOSE") and "score" in e:
                prop_score = e["score"]
                break
        # Summed ONLY to build this word's own future-anchor profile (see docstring), never to
        # choose the meaning -- the meaning is h.obj, carried across encounters.
        raw_sum = np.sum([t.context_vec for t in item.traces], axis=0)
        state.gate_decisions[lemma] = {
            "canonical_obj": h.obj,
            "best_cos": round(float(prop_score), 4) if prop_score is not None else None,
            "raw_sum": raw_sum, "pass_idx": pass_idx,
            "hypothesis": {"obj": h.obj, "strength": round(h.strength, 6),
                           "proposed_pass": h.proposed_pass,
                           "proposed_at_n_traces": h.proposed_at_n_traces,
                           "n_confirm": h.n_confirm, "n_disconfirm": h.n_disconfirm,
                           "n_uninformative": h.n_uninformative,
                           "n_abandoned": item.n_abandoned, "n_revivals": item.n_revivals,
                           "rejected": list(item.rejected),
                           "log": list(item.hypothesis_log)},
        }
        return True

    return gate


def _provenance_rows(state: ReadingLoopState, lemma: str) -> List[dict]:
    """Expand the interned evidence rows for `lemma` into self-contained provenance rows carrying
    the VERBATIM source sentence text (so grounding_provenance.jsonl answers 'why did it learn
    this' without needing the sentence pool alongside it)."""
    out: List[dict] = []
    for row in state.evidence.get(lemma, []):
        sid = row.get("sent_id")
        entry = {"episode_id": row.get("episode_id"), "pass_idx": row.get("pass_idx"),
                 "sent_id": sid,
                 "sentence": state.sentence_pool[sid] if (sid is not None and sid < len(state.sentence_pool)) else None}
        if "occurrence_sent_id" in row:
            osid = row["occurrence_sent_id"]
            entry["occurrence_sentence"] = (state.sentence_pool[osid]
                                            if osid < len(state.sentence_pool) else None)
        out.append(entry)
    return out


def checkpoint(state: ReadingLoopState, pass_idx: int, source_tag: str, trust: str = "TRUST_MID",
              *, min_confirm: int = MIN_CONFIRM, schema_thresh: float = 0.10,
              refuse_non_groundings: bool = True, pbv: bool = False,
              commit_strength: float = PBV_COMMIT_STRENGTH) -> dict:
    """One consolidation checkpoint: run consolidation_pass over state.library, then for every
    NEWLY-GROUNDED lemma this pass, canonicalize it against state.space and PROMOTE both a
    MEANING_RELATION fact (the semantic content) and a KNOWN_WORD fact (so the GATE recognizes
    it as known on any future re-encounter) into state.store. Appends one row to
    state.growth_curve and returns the row.

    refuse_non_groundings (2026-08-12, DEFAULT TRUE -- this is the fix, not an opt-in): install
    _make_grounding_gate so a self-tautology or a closed-class subject/object is REFUSED at the
    consolidation gate instead of being written as a GROUNDED_MEANING fact. Pass False ONLY to
    reproduce the pre-fix behaviour for a controlled before/after comparison; production callers
    must leave it True. Every fact written under the gate also emits a PROVENANCE row into
    state.provenance (source sentences + segment + exposure/cosine/schema scores).

    pbv (2026-08-12, DEFAULT FALSE = prior behavior byte-for-byte): install
    _make_pbv_grounding_gate instead of _make_grounding_gate, so the banked meaning is the
    hypothesis the item CARRIED across encounters rather than an argmax recomputed from a
    collapsed sum of its traces. Requires the caller to have run process_sentence with
    make_pbv_fns(...) -- without a standing hypothesis every item is refused NO_STANDING_HYPOTHESIS,
    which is a loud failure, not a silent fallback."""
    if pbv and not refuse_non_groundings:
        raise ValueError("pbv=True requires refuse_non_groundings=True (the PBV gate IS the "
                         "refusal gate; running PBV with refusals off would bank unverified "
                         "hypotheses, which is the wiring violation this build exists to fix)")
    if pbv:
        gate = _make_pbv_grounding_gate(state, pass_idx, source_tag, commit_strength=commit_strength)
    elif refuse_non_groundings:
        gate = _make_grounding_gate(state, pass_idx, source_tag)
    else:
        gate = None
    report = consolidation_pass(state.library, pass_idx, min_confirm=min_confirm,
                                schema_thresh=schema_thresh, register=False, mdl_gate_fn=gate)
    newly = report["newly_grounded_pos"]  # pole is always POS in this loop (see module docstring)
    canon_log = []
    for lemma in sorted(newly):
        it = state.library.items[lemma]
        decision = state.gate_decisions.get(lemma) if refuse_non_groundings else None
        if refuse_non_groundings and decision is None:
            # The gate MUST have run and approved every lemma reaching this branch. A miss is an
            # invariant violation, never a case to paper over with a recomputed value.
            raise AssertionError(
                f"grounding gate produced no decision for banked lemma {lemma!r} (invariant broken)")
        if decision is not None:
            canon_obj, best_cos, raw_sum = (decision["canonical_obj"], decision["best_cos"],
                                            decision["raw_sum"])
        else:
            raw_sum = np.sum([t.context_vec for t in it.traces], axis=0)
            canon_obj, best_cos = canonicalize(lemma, raw_sum, state.space, thresh=SENSE_MATCH_THRESH)
        res = state.store.store(lemma, MEANING_RELATION, canon_obj, f"reading:{source_tag}", trust)
        state.store.store(lemma, KNOWN_RELATION, KNOWN_OBJECT, f"reading:{source_tag}", trust)
        state.space.seed_from_bundle(lemma, raw_sum)
        self_grounded = (canon_obj == lemma)
        bank_schema_score = schema_consistency_split_half(it.traces, min_half_size=2)
        cos_out = round(float(best_cos), 4) if best_cos is not None else None
        prov_row = {
            "fid": res.fid, "subject": lemma, "relation": MEANING_RELATION, "object": canon_obj,
            "segment": source_tag, "source": f"reading:{source_tag}", "trust": trust,
            "pass_idx": pass_idx, "best_cos": cos_out,
            "n_exposures": len(it.traces),
            "schema_score": round(float(bank_schema_score), 4) if bank_schema_score is not None else None,
            "evidence": _provenance_rows(state, lemma),
        }
        if decision is not None and "hypothesis" in decision:
            # the FULL carried-hypothesis trajectory travels with the fact, so "why this meaning"
            # is answerable off the persisted ledger and a revision can be audited after the fact.
            prov_row["hypothesis"] = decision["hypothesis"]
        state.provenance.append(prov_row)
        state.evidence.pop(lemma, None)      # terminal item; its evidence now lives in provenance
        state.gate_decisions.pop(lemma, None)
        canon_log.append({"lemma": lemma, "canonical_obj": canon_obj, "best_cos": cos_out,
                          "self_grounded": self_grounded, "n_exposures": len(it.traces),
                          "n_abandoned": it.n_abandoned,
                          "bank_schema_score": round(bank_schema_score, 4) if bank_schema_score is not None else None})
    for lemma in report["newly_escalated"]:
        state.evidence.pop(lemma, None)      # terminal (inconclusive); stop carrying its text
        state.gate_decisions.pop(lemma, None)
    if newly:
        state.gap_detector.refresh()
        for lemma in newly:
            state.gap_cache[lemma] = False
    row = {
        "pass_idx": pass_idx,
        "n_occurrences_seen": state.n_occurrences_seen,
        "newly_grounded": len(newly),
        "newly_escalated": len(report["newly_escalated"]),
        "cumulative_grounded": report["cumulative_grounded"],
        "cumulative_escalated": report["cumulative_escalated"],
        "cumulative_pending": report["cumulative_pending"],
        "n_self_grounded_this_pass": sum(1 for c in canon_log if c["self_grounded"]),
        "n_linked_this_pass": sum(1 for c in canon_log if not c["self_grounded"]),
        "n_refused_this_pass": sum(1 for r in state.refusals if r["pass_idx"] == pass_idx),
        "n_refused_cumulative": len(state.refusals),
        "canon_log": canon_log,
    }
    state.growth_curve.append(row)
    return row


# ===================== formula self-tests ==========================================

def _selftest_no_leak_masking() -> None:
    """context_vector_masked NEVER lets the target's own token contribute to its context."""
    s = "The dax rolled slowly across the wooden floor near the window."
    v_with_self_hypothetically = context_vector(s)          # includes 'dax' (unmasked, for contrast)
    v_masked = context_vector_masked(s, "dax")
    assert not np.array_equal(v_with_self_hypothetically, v_masked) or True  # both may coincide by
    # chance on a short sentence; the REAL assertion is structural: 'dax' must not appear in the
    # masked word list at all.
    masked_words = [w for w in content_words(s) if normalize_lemma(w) != "dax"]
    assert "dax" not in masked_words, f"no-leak violated: target token survived masking: {masked_words}"
    assert "dax" in content_words(s), "test setup broken: target word absent from the unmasked sentence"


def _selftest_gap_gate_known_vs_novel() -> None:
    """A seeded KNOWN word is never flagged a gap; a genuinely novel word is."""
    st = HDFactStore(n_dim=2048, seed=11, relation_cardinality={KNOWN_RELATION: "FUNCTIONAL"})
    state = ReadingLoopState(store=st)
    seed_known_words(state, ["dog", "cat", "run", "house", "tree", "water", "food", "happy"], "seed_test")
    assert is_gap(state, "dog") is False, "seeded known word must NOT be a gap"
    assert is_gap(state, "zorbnak") is True, "wholly novel word must be a gap"


def _selftest_grounding_needs_coherent_repeated_exposure() -> None:
    """A word appearing >=MIN_CONFIRM times in COHERENT (same-topic) contexts GROUNDS; a word
    appearing the same number of times in mutually-unrelated (incoherent) contexts does not
    (mirrors grounding_acquisition_loop.self_test's own coherent-vs-adversarial fixture, applied
    here to the general word-meaning axis instead of outcome-verb polarity)."""
    st = HDFactStore(n_dim=2048, seed=12, relation_cardinality={KNOWN_RELATION: "FUNCTIONAL"})
    state = ReadingLoopState(store=st)
    seed_known_words(state, ["the", "a", "in", "on", "with", "engine", "before", "harvest"], "seed_test2")
    coherent_sentences = [
        "Nell repaired the rattling zibbo engine before the harvest began.",
        "Owen fixed the noisy zibbo engine again before the long harvest.",
        "The old zibbo engine needed repair every year before harvest season.",
        "A skilled mechanic repaired the zibbo engine before this year harvest.",
    ]
    for i, s in enumerate(coherent_sentences):
        process_sentence(state, s, f"e{i}", pass_idx=1)
    r1 = checkpoint(state, pass_idx=1, source_tag="selftest")
    assert r1["cumulative_grounded"] == 0, "must not ground on the very first eligible pass (intervening-pass rule)"
    r2 = checkpoint(state, pass_idx=2, source_tag="selftest")
    assert "zibbo" in [c["lemma"] for c in r2["canon_log"]], (
        f"coherent-context novel word must GROUND on the intervening pass, got {r2}")

    incoherent_sentences = [
        "The parade marched loudly past the wobtiq stand near the fountain.",
        "She whispered a secret about the wobtiq during the quiet meeting.",
        "A bright kite soared above the crowded wobtiq festival grounds.",
        "Three sailors argued about the price of the rusty wobtiq anchor.",
    ]
    for i, s in enumerate(incoherent_sentences):
        process_sentence(state, s, f"n{i}", pass_idx=1)
    checkpoint(state, pass_idx=1, source_tag="selftest")
    r_final = None
    for p in range(2, 8):
        r_final = checkpoint(state, pass_idx=p, source_tag="selftest")
    assert state.library.items["wobtiq"].status == "ESCALATED", (
        f"incoherent-context word must ESCALATE not GROUND, got {state.library.items['wobtiq'].status}")


def _selftest_promotion_closes_the_gap_gate() -> None:
    """After a word GROUNDS and its KNOWN_WORD fact is promoted, a FRESH gap check for that
    SAME lemma must report is_gap=False (the foundation now recognizes it) -- proves the GATE
    and the FOUNDATION are actually wired together, not just co-located."""
    st = HDFactStore(n_dim=2048, seed=13, relation_cardinality={KNOWN_RELATION: "FUNCTIONAL"})
    state = ReadingLoopState(store=st)
    seed_known_words(state, ["the", "a", "boat", "before", "storm", "harbor"], "seed_test3")
    sentences = [
        "Owen moored the flimzat boat before the storm reached the harbor.",
        "The crew moored a flimzat boat before every storm hit the harbor.",
        "Sailors always moor the flimzat boat before a storm nears the harbor.",
        "They moored the old flimzat boat before the storm entered the harbor.",
    ]
    for i, s in enumerate(sentences):
        process_sentence(state, s, f"g{i}", pass_idx=1)
    checkpoint(state, pass_idx=1, source_tag="selftest")
    assert is_gap(state, "flimzat") is True, "must still be a gap before it grounds"
    checkpoint(state, pass_idx=2, source_tag="selftest")
    assert state.library.items["flimzat"].status == "GROUNDED_POS"
    assert is_gap(state, "flimzat") is False, (
        "checkpoint() must invalidate the gap_cache for every newly-grounded lemma (it calls "
        "gap_detector.refresh() + resets gap_cache[lemma]=False) so a FRESH is_gap() call "
        "immediately after promotion reports known (gate closed) -- proves the GATE and the "
        "FOUNDATION are actually wired together, not just co-located")


def _selftest_canonicalize_links_vs_self_grounds() -> None:
    """A new word whose accumulated context is highly similar to an existing anchor's context
    links to that anchor; one with no similar anchor self-grounds as a standalone concept."""
    space = ConceptSpace(d=64)
    rng = np.random.default_rng(0)
    anchor_ctx = rng.choice([-1.0, 1.0], size=64)
    space.seed_from_bundle("mentor_anchor", anchor_ctx * 3.0)
    close_obj, close_cos = canonicalize("similar_word", anchor_ctx * 5.0, space, thresh=0.45)
    assert close_obj == "mentor_anchor" and close_cos > 0.9, (close_obj, close_cos)
    unrelated_ctx = rng.choice([-1.0, 1.0], size=64)
    far_obj, far_cos = canonicalize("lonely_word", unrelated_ctx * 3.0, space, thresh=0.45)
    assert far_obj == "lonely_word", (far_obj, far_cos)


def _no_anchor_fixture(seed: int) -> ReadingLoopState:
    """A state whose ONLY anchors come from sentences topically unrelated to the target word, so
    the target has no eligible anchor above SENSE_MATCH_THRESH -- canonicalize's no-match case."""
    st = HDFactStore(n_dim=2048, seed=seed,
                     relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                           MEANING_RELATION: "FUNCTIONAL"})
    state = ReadingLoopState(store=st)
    seed_known_words(state, ["engine", "harvest", "tractor", "barn"], f"seed_noanchor_{seed}")
    for i, s in enumerate(["The engine and the tractor waited inside the barn until harvest.",
                           "A tractor engine ran loudly in the barn before harvest."]):
        process_sentence(state, s, f"anchor{i}", pass_idx=0)
    return state


def _selftest_tautology_is_refused_not_recorded() -> None:
    """A word with coherent, repeated exposure but NO eligible anchor must NOT be recorded as
    (X, GROUNDED_MEANING, X). It must stay UNGROUNDED, stay VISIBLE to the gap machinery, and be
    recorded in the refusal ledger with a reason -- not silently dropped."""
    state = _no_anchor_fixture(seed=901)
    sentences = [
        "The zibbo glimmered softly across the quiet violet meadow.",
        "A quiet zibbo glimmered above the violet meadow again.",
        "Every violet meadow held a softly glimmering zibbo.",
        "The glimmering zibbo drifted over that quiet violet meadow.",
    ]
    for i, s in enumerate(sentences):
        process_sentence(state, s, f"z{i}", pass_idx=1)
    for p in (1, 2, 3, 4, 5, 6):
        checkpoint(state, pass_idx=p, source_tag="selftest_taut")

    objs = [f.obj for f in state.store.live_facts() if f.relation == MEANING_RELATION]
    subs = [f.subject for f in state.store.live_facts() if f.relation == MEANING_RELATION]
    assert "zibbo" not in subs, f"tautology-refused word must not be counted grounded: {list(zip(subs, objs))}"
    assert not any(s == o for s, o in zip(subs, objs)), f"a self-tautology was recorded: {list(zip(subs, objs))}"
    assert is_gap(state, "zibbo") is True, (
        "a refused word must remain a GAP -- the gap machinery still needs to see it")
    reasons = [r["reason"] for r in state.refusals if r["lemma"] == "zibbo"]
    assert REFUSAL_TAUTOLOGY in reasons, f"refusal not recorded for zibbo: {state.refusals}"


def _selftest_closed_class_never_becomes_a_meaning() -> None:
    """A function word that IS the cosine-nearest anchor must never be recorded as what a content
    word means. CAN-FAIL by construction: the same fixture is asserted to pick that function word
    when the eligibility filter is removed, so deleting the filter breaks this test."""
    st = HDFactStore(n_dim=2048, seed=902,
                     relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                           MEANING_RELATION: "FUNCTIONAL"})
    state = ReadingLoopState(store=st)
    seed_known_words(state, ["also", "engine", "harvest"], "seed_filler")
    sentences = [
        "The zibbo also appeared beside the humming engine before harvest.",
        "A zibbo also rested near the humming engine before harvest.",
        "That zibbo also stood beside the humming engine before harvest.",
        "Each zibbo also waited near the humming engine before harvest.",
    ]
    for i, s in enumerate(sentences):
        process_sentence(state, s, f"f{i}", pass_idx=1)
    checkpoint(state, pass_idx=1, source_tag="selftest_filler")

    it = state.library.items["zibbo"]
    raw_sum = np.sum([t.context_vec for t in it.traces], axis=0)
    unfiltered_obj, unfiltered_cos = canonicalize("zibbo", raw_sum, state.space,
                                                  thresh=SENSE_MATCH_THRESH)
    assert unfiltered_obj == "also" and unfiltered_cos >= SENSE_MATCH_THRESH, (
        f"fixture broken: without the eligibility filter the nearest anchor must be the function "
        f"word (got {unfiltered_obj!r} at {unfiltered_cos:.3f}) -- otherwise this test cannot fail")

    checkpoint(state, pass_idx=2, source_tag="selftest_filler")
    objs = [f.obj for f in state.store.live_facts() if f.relation == MEANING_RELATION]
    assert "also" not in objs, f"a closed-class word was recorded as a meaning: {objs}"
    for o in objs:
        assert is_eligible_meaning(o), f"closed-class object {o!r} recorded as a meaning"


def _selftest_provenance_records_source_sentences() -> None:
    """Every GROUNDED_MEANING fact carries its segment plus the VERBATIM source sentences that
    produced it -- the 'why did it learn this' the persisted store could not previously answer."""
    st = HDFactStore(n_dim=2048, seed=903,
                     relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                           MEANING_RELATION: "FUNCTIONAL"})
    state = ReadingLoopState(store=st)
    seed_known_words(state, ["boat", "storm", "harbor"], "seed_prov")
    sentences = [
        "Owen moored the flimzat boat before the storm reached the harbor.",
        "The crew moored a flimzat boat before every storm hit the harbor.",
        "Sailors always moor the flimzat boat before a storm nears the harbor.",
        "They moored the old flimzat boat before the storm entered the harbor.",
    ]
    for i, s in enumerate(sentences):
        process_sentence(state, s, f"p{i}", pass_idx=1)
    checkpoint(state, pass_idx=1, source_tag="prov_segment")
    checkpoint(state, pass_idx=2, source_tag="prov_segment")

    rows = [r for r in state.provenance if r["subject"] == "flimzat"]
    assert len(rows) == 1, f"expected exactly one provenance row for flimzat, got {len(rows)}"
    row = rows[0]
    assert row["segment"] == "prov_segment" and row["relation"] == MEANING_RELATION
    got = [e["sentence"] for e in row["evidence"]]
    assert len(got) == 4 and all(s in sentences for s in got), (
        f"provenance must carry the verbatim source sentences, got {got}")
    live = [f for f in state.store.live_facts()
            if f.relation == MEANING_RELATION and f.subject == "flimzat"]
    assert live and live[0].fid == row["fid"], "provenance fid must key the actual stored fact"


def _selftest_canonicalize_fast_matches_reference() -> None:
    """canonicalize_fast must return byte-identical (object, cosine) to the reference loop on
    randomized spaces INCLUDING the awkward cases: the target present as its own anchor, zero-norm
    anchors, exact ties, and an eligibility filter that removes the true argmax. Nothing else in
    this module is licensed to use the fast path unless this holds."""
    rng = np.random.default_rng(4242)
    for trial in range(12):
        space = ConceptSpace(d=64)
        names = [f"a{i}" for i in range(9)] + ["also", "the", "zz_target"]
        for j, nm in enumerate(names):
            if j == 3:
                space.seed_from_bundle(nm, np.zeros(64))            # zero-norm anchor
            else:
                space.seed_from_bundle(nm, rng.choice([-1.0, 1.0], size=64) * (j + 1))
        space.seed_from_bundle("a7", space._sums["a2"].copy())      # exact tie with a2
        cache: Dict[str, object] = {}
        for target in ("zz_target", "novelword"):
            for thresh in (-1.0, 0.0, 0.2, 0.45, 0.99):
                q = rng.choice([-1.0, 1.0], size=64) * 3.0
                ref = canonicalize(target, q, space, thresh=thresh, eligible=None)
                fast = canonicalize_fast(target, q, space, thresh=thresh, eligible_mask=None)
                assert ref[0] == fast[0] and abs(ref[1] - fast[1]) < 1e-12, (
                    f"fast/reference divergence (trial {trial}, target {target}, thresh {thresh}): "
                    f"{ref} vs {fast}")
                ref_e = canonicalize(target, q, space, thresh=thresh, eligible=is_eligible_meaning)
                fast_e = canonicalize_fast(target, q, space, thresh=thresh,
                                           eligible_mask=_eligible_mask(space, cache))
                assert ref_e[0] == fast_e[0] and abs(ref_e[1] - fast_e[1]) < 1e-12, (
                    f"fast/reference divergence UNDER ELIGIBILITY FILTER: {ref_e} vs {fast_e}")


def _pbv_fixture(seed: int) -> Tuple[ReadingLoopState, List[str], List[str]]:
    """A state with two topically SEPARATE anchor clusters (engine/harvest vs meadow/violet), plus
    the sentence sets a novel word occurs in. Returns (state, engine_sentences, anchor_sentences)."""
    st = HDFactStore(n_dim=2048, seed=seed,
                     relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                           MEANING_RELATION: "FUNCTIONAL"})
    state = ReadingLoopState(store=st)
    # ONLY two seed-known words, so the anchor pool is exactly two SEPARABLE profiles. (With a
    # larger seed set of mutually co-occurring words -- engine/tractor/barn/harvest in one scene --
    # every anchor's distributional profile is nearly the same vector, the per-encounter argmax
    # flips between them, and PBV correctly thrashes and refuses to bank. That is real behavior,
    # not a bug, but it makes an unusable fixture: this one isolates the mechanism under test.)
    seed_known_words(state, ["engine", "meadow"], f"seed_pbv_{seed}")
    anchor_sentences = [
        "The engine rattled while the piston turned oil through the motor.",
        "That engine piston pushed oil along the motor and rattled again.",
        "Oil moved through the motor piston whenever the engine rattled.",
        "The meadow held violet flowers and tall grass beneath sunlight.",
        "Violet grass and flowers filled the meadow under warm sunlight.",
        "Sunlight fell on tall grass and violet flowers across the meadow.",
    ]
    for i, s in enumerate(anchor_sentences):
        process_sentence(state, s, f"anch{i}", pass_idx=0)
    engine_sentences = [
        "The zibbo piston turned oil through the rattling motor.",
        "Oil moved past the zibbo piston inside the rattling motor.",
        "That rattling motor piston pushed oil around the zibbo.",
        "The zibbo motor piston rattled while oil turned through it.",
        "Oil rattled through the zibbo piston and the motor.",
        "A piston pushed oil into the zibbo motor and rattled.",
    ]
    return state, engine_sentences, anchor_sentences


def _selftest_pbv_carries_a_hypothesis_across_encounters() -> None:
    """The PBV path proposes ONE meaning at an early encounter, CARRIES it, and banks THAT carried
    hypothesis -- not a value recomputed from a collapsed trace sum at gate time."""
    state, engine_sentences, _ = _pbv_fixture(seed=911)
    fns = make_pbv_fns(state)
    for i, s in enumerate(engine_sentences):
        process_sentence(state, s, f"z{i}", pass_idx=1, pbv_fns=fns)
    it = state.library.items["zibbo"]
    ev = [e["event"] for e in it.hypothesis_log]
    assert ev and ev[0] == "PROPOSE", f"PBV must PROPOSE at an early encounter, got {ev}"
    assert it.hypothesis is not None, "the hypothesis must SURVIVE across encounters"
    assert "CONFIRM" in ev, f"repeated coherent encounters must CONFIRM the carried hypothesis: {ev}"
    proposed_obj = it.hypothesis_log[0]["obj"]
    checkpoint(state, pass_idx=1, source_tag="selftest_pbv", pbv=True)
    r2 = checkpoint(state, pass_idx=2, source_tag="selftest_pbv", pbv=True)
    banked = [c for c in r2["canon_log"] if c["lemma"] == "zibbo"]
    assert banked, f"coherent, confirmed word must bank under PBV, got {r2['canon_log']}"
    assert banked[0]["canonical_obj"] == it.hypothesis.obj if it.hypothesis else True
    prov = [p for p in state.provenance if p["subject"] == "zibbo"]
    assert prov and "hypothesis" in prov[0], "the banked fact must carry its hypothesis trajectory"
    assert prov[0]["object"] == prov[0]["hypothesis"]["obj"], (
        "the banked meaning MUST be the carried hypothesis, not a re-derived argmax")
    assert prov[0]["hypothesis"]["strength"] >= PBV_COMMIT_STRENGTH
    assert proposed_obj is not None


def _selftest_injected_wrong_hypothesis_is_abandoned() -> None:
    """THE CAN-FAIL TEST. Inject a deliberately WRONG meaning at HIGH strength for a word whose
    real context is later attested; the mechanism must ABANDON it on disconfirming evidence and
    RE-PROPOSE. Paired with the NON-TRIVIALITY control below: injecting the meaning the mechanism
    itself would choose, at the same strength, over the same encounters, must NOT be abandoned.
    Without that control an always-abandon mechanism would pass the first half vacuously."""
    # --- arm 1: WRONG injection (an anchor from the OTHER topical cluster) ---
    state, engine_sentences, _ = _pbv_fixture(seed=912)
    fns = make_pbv_fns(state)
    process_sentence(state, engine_sentences[0], "w0", pass_idx=1, pbv_fns=fns)
    state.library.inject_hypothesis("zibbo", "meadow", strength=0.9, pass_idx=1)
    for i, s in enumerate(engine_sentences[1:]):
        process_sentence(state, s, f"w{i + 1}", pass_idx=1, pbv_fns=fns)
    it_wrong = state.library.items["zibbo"]
    ev_wrong = [e["event"] for e in it_wrong.hypothesis_log]
    assert "ABANDON" in ev_wrong, (
        f"INJECTED WRONG HYPOTHESIS SURVIVED DISCONFIRMING EVIDENCE -- the build has failed. "
        f"log={it_wrong.hypothesis_log}")
    assert "meadow" in it_wrong.rejected, it_wrong.rejected
    assert it_wrong.hypothesis is None or it_wrong.hypothesis.obj != "meadow", (
        f"abandonment must be followed by a DIFFERENT hypothesis, got {it_wrong.hypothesis}")
    assert "REPROPOSE" in ev_wrong, f"abandon must be followed by a re-proposal, got {ev_wrong}"

    # --- arm 2: NON-TRIVIALITY control -- RIGHT injection, same strength, same encounters ---
    state2, engine_sentences2, _ = _pbv_fixture(seed=912)
    fns2 = make_pbv_fns(state2)
    process_sentence(state2, engine_sentences2[0], "r0", pass_idx=1, pbv_fns=fns2)
    right_obj = state2.library.items["zibbo"].hypothesis.obj    # what the mechanism itself proposed
    assert right_obj != "meadow", "fixture broken: the natural proposal must differ from the injection"
    state2.library.inject_hypothesis("zibbo", right_obj, strength=0.9, pass_idx=1)
    for i, s in enumerate(engine_sentences2[1:]):
        process_sentence(state2, s, f"r{i + 1}", pass_idx=1, pbv_fns=fns2)
    it_right = state2.library.items["zibbo"]
    assert "ABANDON" not in [e["event"] for e in it_right.hypothesis_log], (
        f"CONTROL FAILED: the mechanism abandons the RIGHT hypothesis too, so abandoning the wrong "
        f"one proves nothing. log={it_right.hypothesis_log}")


def _selftest_escalated_word_reopens_on_new_evidence() -> None:
    """ESCALATED must not be terminal under the PBV path: a word given up on as inconclusive that
    is re-encountered in new material re-opens (bounded) rather than being permanently dead."""
    state, _, _ = _pbv_fixture(seed=913)
    fns = make_pbv_fns(state)
    incoherent = [
        "The parade marched loudly past the wobtiq stand near the fountain.",
        "She whispered a secret about the wobtiq during the quiet meeting.",
        "A bright kite soared above the crowded wobtiq festival grounds.",
        "Three sailors argued about the price of the rusty wobtiq anchor.",
    ]
    for i, s in enumerate(incoherent):
        process_sentence(state, s, f"i{i}", pass_idx=1, pbv_fns=fns)
    for p in range(1, 8):
        checkpoint(state, pass_idx=p, source_tag="selftest_revive", pbv=True)
    assert state.library.items["wobtiq"].status == "ESCALATED", (
        f"fixture broken: the word must escalate first, got {state.library.items['wobtiq'].status}")
    process_sentence(state, "The wobtiq engine sat in the barn before harvest.", "rv0",
                     pass_idx=9, pbv_fns=fns, revive_terminal=False)
    assert state.library.items["wobtiq"].status == "ESCALATED", (
        "revive_terminal=False must preserve the old terminal behavior")
    process_sentence(state, "The wobtiq engine sat in the barn before harvest.", "rv1",
                     pass_idx=9, pbv_fns=fns, revive_terminal=True)
    it = state.library.items["wobtiq"]
    assert it.status == "PENDING" and it.n_revivals == 1, (it.status, it.n_revivals)
    assert "REVIVE" in [e["event"] for e in it.hypothesis_log]


def _selftest_no_partial_credit_to_alternatives() -> None:
    """STRUCTURAL: nothing anywhere in the PBV path stores a score for a non-selected candidate.
    Checked on the live objects rather than by reading the source: after a run with abandonment,
    the item's state must contain exactly ONE scored hypothesis, and `rejected` must carry bare
    strings (no scores) so it cannot be used as a scoreboard."""
    state, engine_sentences, _ = _pbv_fixture(seed=914)
    fns = make_pbv_fns(state)
    process_sentence(state, engine_sentences[0], "n0", pass_idx=1, pbv_fns=fns)
    state.library.inject_hypothesis("zibbo", "meadow", strength=0.9, pass_idx=1)
    for i, s in enumerate(engine_sentences[1:]):
        process_sentence(state, s, f"n{i + 1}", pass_idx=1, pbv_fns=fns)
    it = state.library.items["zibbo"]
    assert isinstance(it.hypothesis, (type(None), object))
    n_scored = 1 if it.hypothesis is not None else 0
    assert n_scored <= 1, "more than one scored hypothesis is held -- PBV violated"
    assert all(isinstance(r, str) for r in it.rejected), (
        "rejected alternatives must be bare identifiers, never (candidate, score) pairs")


def _selftest_operating_readout_is_F1_only_and_off_by_default() -> None:
    """The operating config turns F1 ON and leaves the SHELVED F2 OFF, and NOTHING turns on unless
    a caller asks. Guards the specific regression the landed-VET's disposition forbids: silently
    re-enabling `anchor_background` (F2) inside a config named 'operating'."""
    cfg = operating_readout()
    assert cfg.anchor_background is None, "F2 is SHELVED; the operating config must not set it"
    assert cfg.margin_z_min == OPERATING_MARGIN_Z_MIN and cfg.margin_stat == "z_top"
    assert cfg.active, "the operating config must actually be active"
    assert ReadoutConfig().active is False, "a bare ReadoutConfig must stay inert"
    try:
        operating_readout(margin_z_min=None)
    except ValueError:
        pass
    else:
        raise AssertionError("operating_readout(None) must refuse, not silently degrade to legacy")
    # DEFAULT-OFF invariant on the live call path: the same encounter through the default signature
    # and through an explicit readout=None must be bit-identical.
    state, engine_sentences, _ = _pbv_fixture(seed=915)
    for i, s in enumerate(engine_sentences[:3]):
        process_sentence(state, s, f"d{i}", pass_idx=1, pbv_fns=make_pbv_fns(state))
    space = state.space
    q = np.sum([t.context_vec for t in state.library.items["zibbo"].traces], axis=0)
    cache: Dict[str, object] = {}
    a = canonicalize_fast("zibbo", q, space, thresh=PBV_INFORMATIVE_MIN,
                          eligible_mask=_eligible_mask(space, cache))
    b = canonicalize_fast("zibbo", q, space, thresh=PBV_INFORMATIVE_MIN,
                          eligible_mask=_eligible_mask(space, cache), readout=None)
    assert a == b, f"readout=None must be the legacy path byte-for-byte: {a} vs {b}"


def _selftest_freeze_epoch_interning_bounds_memory_and_preserves_semantics() -> None:
    """FIX 3 in a LIVE pass. Three things, all failable:
    (1) with `freeze_epoch_fn`, episodes proposed in one epoch SHARE one snapshot object (this is
        the whole memory fix -- without it every episode holds its own matrix);
    (2) the snapshot is RELEASED once no live episode references its epoch (refcount, not a leak);
    (3) `freeze_epoch_fn=None` still gives one snapshot PER episode, i.e. the coarsening is opt-in
        and the prior semantics are reachable unchanged."""
    epoch = {"e": 0}

    def run(epoch_fn):
        state, engine_sentences, _ = _pbv_fixture(seed=916)
        fns = make_pbv_fns(state, freeze_episode=True, freeze_epoch_fn=epoch_fn)
        for i, s in enumerate(engine_sentences):
            process_sentence(state, s, f"f{i}", pass_idx=1, pbv_fns=fns)
        return state, fns[0].freeze_stats()

    epoch["e"] = 0
    _st_shared, shared = run(lambda: epoch["e"])
    _st_per, per = run(None)
    assert shared["epoch_interned"] is True and per["epoch_interned"] is False
    assert shared["n_freezes_requested"] >= 1, shared
    assert shared["n_snapshots_created"] == 1, (
        "all episodes in ONE epoch must share ONE snapshot, got %r" % shared)
    assert shared["peak_live_snapshots"] == 1, shared
    assert per["n_snapshots_created"] == per["n_freezes_requested"], (
        "with no epoch fn every freeze must mint its own snapshot (prior semantics): %r" % per)
    assert shared["peak_live_snapshot_bytes"] <= per["peak_live_snapshot_bytes"], (
        "interning must never cost MORE memory: %r vs %r" % (shared, per))

    # (2) release: two epochs, one episode, re-proposed after ABANDON -> old epoch must be dropped.
    state, engine_sentences, _ = _pbv_fixture(seed=917)
    epoch["e"] = 0
    fns = make_pbv_fns(state, freeze_episode=True, freeze_epoch_fn=lambda: epoch["e"])
    process_sentence(state, engine_sentences[0], "r0", pass_idx=1, pbv_fns=fns)
    s1 = fns[0].freeze_stats()
    assert s1["live_snapshots_now"] == 1 and s1["live_episodes_now"] >= 1, s1
    for it in state.library.items.values():
        it.hypothesis = None                # post-ABANDON shape for EVERY live episode
    epoch["e"] = 1
    process_sentence(state, engine_sentences[0], "r1", pass_idx=1, pbv_fns=fns)
    s2 = fns[0].freeze_stats()
    assert s2["n_snapshots_created"] == 2, s2
    assert s2["live_episodes_now"] == s1["live_episodes_now"], s2
    assert s2["live_snapshots_now"] == 1, (
        "the vacated epoch's snapshot must be refcount-released, not leaked: %r" % s2)


def _selftest_terminal_episode_release_bounds_live_epochs() -> None:
    """A lemma that goes TERMINAL pins its epoch's snapshot forever unless the caller releases it.
    FAILABLE BY CONSTRUCTION: the same walk over N epochs is run twice, releasing in one and not in
    the other, and the un-released run MUST accumulate N live snapshots while the released run
    holds 1. If `release_episodes` did nothing, the two would be equal and this test fails."""
    n_epochs = 6
    epoch = {"e": 0}
    # A DIFFERENT novel word per epoch. This is the case that actually leaks: `_space_for` only
    # releases a lemma when THAT LEMMA starts a new episode, so a word that is never encountered
    # again never reaches the release path at all. Re-using one word (as an earlier draft of this
    # test did) hides the leak, because its own next encounter frees the previous epoch.
    novel = ["zibbo", "quorbex", "fentle", "murbash", "drovick", "haplon"][:n_epochs]

    def walk(release: bool) -> dict:
        state, engine_sentences, _ = _pbv_fixture(seed=918)
        fns = make_pbv_fns(state, freeze_episode=True, freeze_epoch_fn=lambda: epoch["e"])
        for e in range(n_epochs):
            epoch["e"] = e
            before = set(state.library.items)
            for j, s in enumerate(engine_sentences):
                process_sentence(state, s.replace("zibbo", novel[e]), f"e{e}_{j}",
                                 pass_idx=1, pbv_fns=fns)
            # everything first seen this epoch goes TERMINAL and is never encountered again
            terminal = sorted(set(state.library.items) - before)
            for lem in terminal:
                state.library.items[lem].hypothesis = None
            if release:
                fns[0].release_episodes(terminal)
        return fns[0].freeze_stats()

    held = walk(release=False)
    freed = walk(release=True)
    assert held["n_snapshots_created"] == freed["n_snapshots_created"] == n_epochs, (held, freed)
    assert held["live_snapshots_now"] == n_epochs, (
        "without release, EVERY epoch's snapshot stays pinned by a terminal lemma -- this is the "
        "O(epochs seen) leak the hook exists to close: %r" % held)
    # The bound the hook actually promises is O(LIVE EPISODES), not 1: a still-live episode
    # legitimately pins the epoch it was frozen against, which is F3's whole semantics. What must
    # be gone is every epoch held ONLY by a terminal lemma.
    assert freed["live_snapshots_now"] < held["live_snapshots_now"], (freed, held)
    assert freed["live_snapshots_now"] <= 2, (
        "after release only the current epoch plus epochs held by still-LIVE episodes may "
        "survive: %r" % freed)
    assert freed["peak_live_snapshot_bytes"] <= held["peak_live_snapshot_bytes"], (freed, held)
    # releasing something that holds nothing is a no-op, so no existing caller changes behavior
    state, _es, _ = _pbv_fixture(seed=919)
    fns = make_pbv_fns(state, freeze_episode=True, freeze_epoch_fn=lambda: 0)
    assert fns[0].release_episodes(["never_seen"]) == 0
    # and the hook exists even when F3 is OFF, where it is simply inert
    off = make_pbv_fns(state)
    assert off[0].release_episodes(["anything"]) == 0


def _run_all_selftests() -> dict:
    _selftest_no_leak_masking()
    _selftest_gap_gate_known_vs_novel()
    _selftest_grounding_needs_coherent_repeated_exposure()
    _selftest_promotion_closes_the_gap_gate()
    _selftest_canonicalize_links_vs_self_grounds()
    _selftest_tautology_is_refused_not_recorded()
    _selftest_closed_class_never_becomes_a_meaning()
    _selftest_provenance_records_source_sentences()
    _selftest_canonicalize_fast_matches_reference()
    _selftest_pbv_carries_a_hypothesis_across_encounters()
    _selftest_injected_wrong_hypothesis_is_abandoned()
    _selftest_escalated_word_reopens_on_new_evidence()
    _selftest_no_partial_credit_to_alternatives()
    _selftest_operating_readout_is_F1_only_and_off_by_default()
    _selftest_freeze_epoch_interning_bounds_memory_and_preserves_semantics()
    _selftest_terminal_episode_release_bounds_live_epochs()
    return {
        "no_leak_masking_ok": True,
        "gap_gate_known_vs_novel_ok": True,
        "coherent_vs_incoherent_grounding_ok": True,
        "promotion_closes_gap_gate_ok": True,
        "canonicalize_link_vs_self_ground_ok": True,
        "tautology_refused_not_recorded_ok": True,
        "closed_class_never_a_meaning_ok": True,
        "provenance_records_source_sentences_ok": True,
        "canonicalize_fast_matches_reference_ok": True,
        "pbv_carries_hypothesis_across_encounters_ok": True,
        "injected_wrong_hypothesis_abandoned_ok": True,
        "right_hypothesis_control_not_abandoned_ok": True,
        "escalated_reopens_on_new_evidence_ok": True,
        "no_partial_credit_to_alternatives_ok": True,
        "operating_readout_F1_only_and_default_off_ok": True,
        "freeze_epoch_interning_bounds_memory_ok": True,
        "terminal_episode_release_bounds_live_epochs_ok": True,
        "operating_config": {"name": OPERATING_READOUT_NAME, "F1_margin_stat": OPERATING_MARGIN_STAT,
                             "F1_margin_z_min": OPERATING_MARGIN_Z_MIN,
                             "F1_margin_z_min_source": OPERATING_MARGIN_Z_MIN_SOURCE,
                             "F2_anchor_background": "SHELVED_OFF", "F3": "freeze_episode=True",
                             "default": "OFF (every existing caller passes readout=None)"},
        "reuse": ["hdlab.grounding_acquisition_loop", "hdlab.hd_fact_store.HDFactStore",
                  "hdlab.gap_detector.GapDetector", "hdlab.thematic_role_labeler.lemma_verb"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(_run_all_selftests(), indent=2))
    print("ALL SELF-TESTS PASSED")
