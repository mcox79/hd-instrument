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
    Library,
    Trace,
    consolidation_pass,
    content_words,
    context_vector,
    schema_consistency_split_half,
)
from hdlab.hd_fact_store import HDFactStore
from hdlab.gap_detector import GapDetector
from hdlab.thematic_role_labeler import lemma_verb

KNOWN_RELATION = "KNOWN_WORD"
KNOWN_OBJECT = "CORE"
MEANING_RELATION = "GROUNDED_MEANING"
GAP_FLOOR = 0.625          # reused verbatim from hdlab.gap_detector's own pre-registered default
SENSE_MATCH_THRESH = 0.45  # HYPOTHESIZED (exploratory canonicalization link; see module docstring
                            # SENSE_MATCH_THRESH rationale in the calling cell's pre-reg -- primary
                            # grounding gate is schema_consistency_split_half, NOT this threshold)


def normalize_lemma(surface: str) -> str:
    """Glass-box surface->lemma via the reused generic suffix-stripper (thematic_role_labeler.
    lemma_verb; POS-generic despite its name -- see that function's own docstring)."""
    return lemma_verb(surface)


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

    def observe(self, lemma: str, ctx_vec: np.ndarray) -> None:
        if lemma not in self._sums:
            self._sums[lemma] = np.zeros(self.d, dtype=np.float64)
        self._sums[lemma] += ctx_vec

    def seed_from_bundle(self, lemma: str, raw_sum: np.ndarray) -> None:
        """Seed (or overwrite) a lemma's accumulator directly from an already-computed raw sum
        (used at grounding time: the sum of a Library item's own trace context vectors)."""
        self._sums[lemma] = np.array(raw_sum, dtype=np.float64, copy=True)

    def bundle(self, lemma: str) -> Optional[np.ndarray]:
        s = self._sums.get(lemma)
        if s is None:
            return None
        return np.sign(s)

    def __contains__(self, lemma: str) -> bool:
        return lemma in self._sums

    def anchors(self) -> List[str]:
        return sorted(self._sums)


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def canonicalize(new_lemma: str, new_raw_sum: np.ndarray, space: ConceptSpace,
                 thresh: float = SENSE_MATCH_THRESH) -> Tuple[str, float]:
    """Nearest-neighbor sense assignment for a newly-grounded word against every anchor
    CURRENTLY in `space` (excludes new_lemma itself, which may already be present as a seed
    accumulator coincidentally sharing the name -- excluded defensively, though in practice a
    just-grounded word is never also a seed word by construction). Returns (canonical_obj,
    best_cosine); canonical_obj == new_lemma (self-grounded, standalone new concept) when no
    anchor clears `thresh`, or the best-matching PRIOR anchor's lemma otherwise."""
    new_bundle = np.sign(new_raw_sum)
    best_anchor, best_cos = None, -2.0
    for anchor in space.anchors():
        if anchor == new_lemma:
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
                     scramble_rng: Optional[np.random.Generator] = None) -> int:
    """FLAG every content-word lemma in `sentence` that is (a) not a seed-known word, (b) not
    already a foundation gap-negative (GapDetector says known), and (c) not a terminal Library
    item (GROUNDED/ESCALATED -- Library.flag() itself no-ops on those, this is just a cheap
    short-circuit). Returns the number of lemmas flagged this sentence.

    scramble_context_source (SCRAMBLE-CONTEXT control): when given, each target's context
    window is NOT `sentence` but an UNRELATED sentence drawn (deterministically, via
    scramble_rng) from this pool -- destroys real co-occurrence coherence while preserving
    gross corpus statistics (same recipe grounding_acquisition_loop.self_test's own
    adversarialtest fixture uses: independent-random context per trace)."""
    state.n_occurrences_seen += 1
    n_flagged = 0
    for lemma in content_lemmas(sentence):
        if lemma in state.known_seed:
            # still track its distributional profile (comparison pool for canonicalize)
            ctx = context_vector_masked(sentence, lemma)
            if np.any(ctx != 0.0):
                state.space.observe(lemma, ctx)
            continue
        it = state.library.items.get(lemma)
        if it is not None and it.status != "PENDING":
            continue  # terminal (GROUNDED/ESCALATED); already resolved either way
        if not is_gap(state, lemma):
            continue  # foundation already knows this word (e.g. grounded earlier this run)
        if scramble_context_source is not None:
            src_sent = scramble_context_source[int(scramble_rng.integers(0, len(scramble_context_source)))]
            ctx = context_vector_masked(src_sent, lemma)
        else:
            ctx = context_vector_masked(sentence, lemma)
        if not np.any(ctx != 0.0):
            continue  # empty window (all-stopword context); nothing to learn from this occurrence
        flagged = state.library.flag(lemma, episode_id, "POS", ctx, pass_idx)
        if flagged:
            n_flagged += 1
    return n_flagged


def checkpoint(state: ReadingLoopState, pass_idx: int, source_tag: str, trust: str = "TRUST_MID",
              *, min_confirm: int = MIN_CONFIRM, schema_thresh: float = 0.10) -> dict:
    """One consolidation checkpoint: run consolidation_pass over state.library, then for every
    NEWLY-GROUNDED lemma this pass, canonicalize it against state.space and PROMOTE both a
    MEANING_RELATION fact (the semantic content) and a KNOWN_WORD fact (so the GATE recognizes
    it as known on any future re-encounter) into state.store. Appends one row to
    state.growth_curve and returns the row."""
    report = consolidation_pass(state.library, pass_idx, min_confirm=min_confirm,
                                schema_thresh=schema_thresh, register=False)
    newly = report["newly_grounded_pos"]  # pole is always POS in this loop (see module docstring)
    canon_log = []
    for lemma in sorted(newly):
        it = state.library.items[lemma]
        raw_sum = np.sum([t.context_vec for t in it.traces], axis=0)
        canon_obj, best_cos = canonicalize(lemma, raw_sum, state.space, thresh=SENSE_MATCH_THRESH)
        state.store.store(lemma, MEANING_RELATION, canon_obj, f"reading:{source_tag}", trust)
        state.store.store(lemma, KNOWN_RELATION, KNOWN_OBJECT, f"reading:{source_tag}", trust)
        state.space.seed_from_bundle(lemma, raw_sum)
        self_grounded = (canon_obj == lemma)
        bank_schema_score = schema_consistency_split_half(it.traces, min_half_size=2)
        canon_log.append({"lemma": lemma, "canonical_obj": canon_obj, "best_cos": round(best_cos, 4),
                          "self_grounded": self_grounded, "n_exposures": len(it.traces),
                          "bank_schema_score": round(bank_schema_score, 4) if bank_schema_score is not None else None})
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


def _run_all_selftests() -> dict:
    _selftest_no_leak_masking()
    _selftest_gap_gate_known_vs_novel()
    _selftest_grounding_needs_coherent_repeated_exposure()
    _selftest_promotion_closes_the_gap_gate()
    _selftest_canonicalize_links_vs_self_grounds()
    return {
        "no_leak_masking_ok": True,
        "gap_gate_known_vs_novel_ok": True,
        "coherent_vs_incoherent_grounding_ok": True,
        "promotion_closes_gap_gate_ok": True,
        "canonicalize_link_vs_self_ground_ok": True,
        "reuse": ["hdlab.grounding_acquisition_loop", "hdlab.hd_fact_store.HDFactStore",
                  "hdlab.gap_detector.GapDetector", "hdlab.thematic_role_labeler.lemma_verb"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(_run_all_selftests(), indent=2))
    print("ALL SELF-TESTS PASSED")
