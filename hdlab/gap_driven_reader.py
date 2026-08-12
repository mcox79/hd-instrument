"""hdlab/gap_driven_reader.py -- SELF-DIRECTED GAP LOOP: identify the specific missing
prerequisite behind an ungrounded concept, and rank candidate reading material by how well it
supplies that prerequisite (2026-08-12).

MISSION (USER-greenlit): turn passive foundations-first reading into ACTIVE self-directed
learning. When reading hits a concept B it can't yet ground (a novel/escalated gap), the system
should IDENTIFY the specific missing prerequisite concept A that B's own context leans on, and
PRIORITIZE reading material that supplies A -- the "read basic math before QM" capability.
Brain-foundational framing: information-gap curiosity (Loewenstein 1994, the gap between what one
knows and wants to know drives exploration) + novelty/prediction-error-driven exploration
(hippocampal novelty signal steering what gets attended/explored next, c.f. gap_detector.py's own
CA3/CA1 framing below).

CRITICAL CONCURRENCY NOTE (2026-08-12): a separate LIVE session process is concurrently importing
hdlab/reading_grounding_loop.py and writing data/foundation/reading_grounding_v1 -- this module
does NOT modify that file (read-only import only) and does NOT write to that directory (this
module's own driver, experiments/exp_gap_driven_reader_controlled_v1.py, uses a wholly separate
data/exp_gap_driven_reader_controlled_v1* output path and fresh, throwaway HDFactStore/
ReadingLoopState instances per trial -- no shared mutable state with the concurrent session).

REUSE (wire-don't-island; every organ below is imported read-only, called verbatim; this module
adds NO new binding/cleanup/consolidation mechanism, only the IDENTIFY + RANK organs the mission
asks for, which nothing on disk currently provides):
  hdlab.reading_grounding_loop.ReadingLoopState / seed_known_words / process_sentence / checkpoint
      / content_lemmas / normalize_lemma / KNOWN_RELATION / KNOWN_OBJECT
                                                       (FLAG + CONSOLIDATE + FOUNDATION-GATE, the
                                                       whole cycle-1 read-to-grow engine, unmodified)
  hdlab.gap_detector.GapDetector.familiarity(..., use_confidence_signal=)
                                                       (the ONLINE "do I already know this concept"
                                                       CA3/CA1 novelty margin, INCLUDING its own
                                                       pre-built, pre-validated ablation hook -- this
                                                       module does not reimplement an ablation RNG,
                                                       it reuses GapDetector's existing one verbatim,
                                                       per the wire-don't-island discipline)
  hdlab.hd_fact_store.HDFactStore                     (the trust-bound FOUNDATION store)
  hdlab.grounding_acquisition_loop.content_words       (via reading_grounding_loop's content_lemmas)

GENUINELY NEW code here (nothing on disk does either of these -- confirmed by architecture-audit
finding #3, notes/architecture_audit_2026-08-11.md, and by this module's own substrate_query.sh
concept-check, which surfaced no prior-arc cell above cosine 0.33 for "gap-driven reading
prerequisite identification"): gap_detector.py answers "do I know THIS ONE probe" for a single
(subject,relation,object); reading_grounding_loop.py grows the foundation from reading in FIXED
curriculum order (purely passive); curriculum_prerequisite_scaffold_consolidation_v1 (commit
5fe41846d, HARD_PASS) gates a DEPENDENT concept's consolidation on a PRE-DECLARED prerequisite
chain (energy->work->power) being already-consolidated -- it never autonomously DISCOVERS which
concept is the blocker, and it never produces a reading-priority RANKING over candidate material.
This module is the missing ACTIVE piece: given only its own online gap signal + the co-occurrence
structure of what it has already read, autonomously (a) IDENTIFY which specific other concept a
blocked concept's own context leans on that is itself still a foundation gap, and (b) RANK
candidate unread material by how well each item supplies that identified gap.

  PrereqTracker         -- per-lemma co-occurrence bookkeeping (which OTHER content lemmas showed
                            up alongside a target lemma, one list per sentence, insertion order).
                            Purely additive bookkeeping alongside (never inside) Library/
                            ReadingLoopState -- no reused-module state is touched.
  identify_missing_prerequisites -- for a blocked/target lemma, rank its own co-occurring lemmas
                            by (a) how CONSISTENTLY they co-occur with it (fraction of the target's
                            own recorded sentences that contain the candidate) and (b) whether the
                            candidate IS ITSELF a live foundation gap right now (via
                            GapDetector.familiarity's OWN is_gap decision, real or -- the mandated
                            ablation control -- noise-substituted). This is the identification
                            mechanism: NOT a static lookup table, NOT a pre-declared chain; it is
                            computed fresh from (this module's own co-occurrence bookkeeping) x
                            (the substrate's own live gap signal), exactly the two ingredients the
                            mission specifies ("the concepts B leans on in its own context... that
                            are NOT grounded in the foundation").
  rank_material          -- given an IDENTIFIED target lemma (the output of the function above),
                            score each candidate unread document by how many of its sentences
                            mention that lemma. Deliberately the SIMPLEST possible "does this
                            material supply the target concept" proxy (a direct lexical-occurrence
                            count) -- the mission's decisive property is that ablating the GAP
                            SIGNAL upstream (in identification) must collapse this ranking to
                            chance; the ranking function itself does not need its own gap-awareness
                            because it is always fed the OUTPUT of identification, so ablating
                            identification cascades into ablating the ranking automatically (a
                            wrong/noise-driven target lemma correlates ~0 with which document truly
                            supplies the REAL prerequisite -- see module self-tests + the
                            controlled-scenario driver's gap-ablation arm).

ASCII-only. Deterministic throughout: sorted(set(...)) / sorted(dict) iteration everywhere (no
Python hash(), no unordered set iteration -- PROT-023/F.5 compliant), fixed integer seeds for
every HDFactStore/GapDetector/np.random.default_rng construction. The two randomness sources this
module touches are BOTH already-deterministic, already-seeded, reused-verbatim streams:
GapDetector's own ablation_rng (its ablation, its seed, untouched here) and
np.random.default_rng(<fixed int>) for the controlled-scenario driver's "random reading order"
baseline (never Python's built-in hash()-derived ordering).
"""
from __future__ import annotations

import inspect
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from hdlab.reading_grounding_loop import (
    KNOWN_OBJECT,
    KNOWN_RELATION,
    ReadingLoopState,
    checkpoint,
    content_lemmas,
    normalize_lemma,
    process_sentence,
    seed_known_words,
)
from hdlab.gap_detector import GapDetector  # noqa: F401 (re-exported for callers/tests)
from hdlab.hd_fact_store import HDFactStore  # noqa: F401 (re-exported for callers/tests)


@dataclass
class PrereqTracker:
    """Per-lemma co-occurrence bookkeeping. co_occurrences[lemma] is a list of lists (one entry
    PER SENTENCE that lemma appeared in), each inner list the OTHER content lemmas present in
    that same sentence (deterministic order: sorted(set(...)) within a sentence, insertion order
    across sentences -- never Python hash() or unordered set iteration). Purely additive
    bookkeeping; never mutates ReadingLoopState/Library/HDFactStore."""

    co_occurrences: Dict[str, List[List[str]]] = field(default_factory=dict)

    def record(self, lemma: str, co_lemmas: Sequence[str]) -> None:
        self.co_occurrences.setdefault(lemma, []).append(sorted(set(co_lemmas)))

    def n_sentences_for(self, lemma: str) -> int:
        return len(self.co_occurrences.get(lemma, []))


def read_and_track(state: ReadingLoopState, tracker: PrereqTracker, sentence: str,
                    episode_id: str, pass_idx: int) -> List[str]:
    """ONE sentence, TWO effects, in this fixed order: (1) record co-occurrence for EVERY content
    lemma in the sentence (unconditional -- this is the identification substrate, independent of
    whatever process_sentence decides to flag), (2) call reading_grounding_loop.process_sentence
    UNMODIFIED (the actual FLAG/no-leak/gap-gate logic, byte-identical to that module's own
    behavior). Returns the sentence's content lemmas (for the caller's bookkeeping/logging)."""
    lemmas = content_lemmas(sentence)
    for lem in lemmas:
        others = [x for x in lemmas if x != lem]
        tracker.record(lem, others)
    process_sentence(state, sentence, episode_id, pass_idx)
    return lemmas


@dataclass
class PrereqCandidate:
    lemma: str
    score: float           # co-occurrence CONSISTENCY: count / n_sentences_target_appeared_in
    count: int              # raw co-occurrence count
    n_target_sentences: int
    margin: float            # the (real-or-ablated) GapDetector familiarity margin that gated it
    ablated: bool


def identify_missing_prerequisites(state: ReadingLoopState, tracker: PrereqTracker,
                                    target_lemma: str, *, use_gap_signal: bool = True,
                                    min_count: int = 1) -> List[PrereqCandidate]:
    """IDENTIFY step. For `target_lemma` (a blocked/gap concept), rank every OTHER lemma that has
    ever co-occurred with it (per `tracker`) by co-occurrence consistency, but ONLY among
    candidates that are THEMSELVES a live gap in the foundation right now (GapDetector.familiarity
    .is_gap, real signal or -- via use_gap_signal=False -- GapDetector's OWN pre-built ablation
    substitution). Deterministic tie-break: score desc, then lemma asc (sorted(freq) iteration
    order, never a hash-derived order). Returns [] if target_lemma was never recorded (nothing to
    identify from) -- callers should treat that as "no prerequisite signal available yet", not an
    error.

    NO-LEAK BY CONSTRUCTION: this function's signature takes no ground-truth "true prerequisite"
    argument -- it can only ever rank what it has actually observed via `tracker` + queried via
    `state.gap_detector`. See _selftest_no_ground_truth_leak_in_signature below (a structural
    inspect.signature check, not just a docstring claim)."""
    occurrences = tracker.co_occurrences.get(target_lemma, [])
    n_occ = len(occurrences)
    if n_occ == 0:
        return []
    freq: Counter = Counter()
    for co_lemmas in occurrences:
        for c in co_lemmas:               # already sorted(set(...)) per-sentence at record() time
            if c == target_lemma:
                continue
            freq[c] += 1
    candidates: List[PrereqCandidate] = []
    for lemma in sorted(freq):             # deterministic (PROT-023/F.5); never a hash-derived order
        cnt = freq[lemma]
        if cnt < min_count:
            continue
        fam = state.gap_detector.familiarity(lemma, KNOWN_RELATION, KNOWN_OBJECT,
                                              use_confidence_signal=use_gap_signal)
        if fam.is_gap:
            candidates.append(PrereqCandidate(lemma=lemma, score=cnt / n_occ, count=cnt,
                                               n_target_sentences=n_occ, margin=fam.margin,
                                               ablated=fam.ablated))
    candidates.sort(key=lambda c: (-c.score, c.lemma))
    return candidates


def rank_material(state: ReadingLoopState, target_lemma: str,
                   candidate_docs: Dict[str, Sequence[str]]) -> List[Tuple[str, int]]:
    """RANK step. Score each candidate_docs[doc_id] (a sequence of unread sentences) by how many
    of its sentences mention `target_lemma` (a direct lexical-occurrence proxy for "does this
    material supply the target concept"). Deterministic tie-break: score desc, then doc_id asc.
    `state` is accepted (not currently used beyond documenting the call convention) so a future
    caller can swap in a richer relevance scorer without changing this function's call sites; the
    load-bearing gap-awareness lives entirely in WHICH target_lemma the caller passes in (see
    module docstring) -- this function is intentionally target-agnostic."""
    scores: Dict[str, int] = {}
    for doc_id, sentences in candidate_docs.items():
        cnt = 0
        for s in sentences:
            if target_lemma in content_lemmas(s):
                cnt += 1
        scores[doc_id] = cnt
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))


def next_read_target(state: ReadingLoopState, tracker: PrereqTracker, primary_lemma: str, *,
                      use_gap_signal: bool = True) -> Tuple[str, List[PrereqCandidate]]:
    """Decide what concept the NEXT read should try to supply: the top IDENTIFIED missing
    prerequisite of `primary_lemma` if one exists, else `primary_lemma` itself (no more known
    missing prerequisites -- the next-most-useful thing to read about is the blocked concept's own
    remaining explanation). Returns (target_lemma, full_candidate_list) so callers can log/grade
    the identification step separately from the scheduling decision it feeds."""
    candidates = identify_missing_prerequisites(state, tracker, primary_lemma,
                                                 use_gap_signal=use_gap_signal)
    target = candidates[0].lemma if candidates else primary_lemma
    return target, candidates


# ===================== formula self-tests ==========================================

def _fresh_state(seed: int, n_dim: int = 2048) -> ReadingLoopState:
    store = HDFactStore(n_dim=n_dim, seed=seed, relation_cardinality={KNOWN_RELATION: "FUNCTIONAL"})
    return ReadingLoopState(store=store)


def _selftest_tracker_records_cooccurrence() -> None:
    tracker = PrereqTracker()
    lemmas = ["velmara", "dravithex", "engine"]
    tracker.record("dravithex", [l for l in lemmas if l != "dravithex"])
    assert tracker.n_sentences_for("dravithex") == 1
    assert tracker.co_occurrences["dravithex"][0] == sorted(["velmara", "engine"])
    tracker.record("dravithex", ["engine", "borlune"])
    assert tracker.n_sentences_for("dravithex") == 2
    assert tracker.n_sentences_for("nobody_recorded_this") == 0


def _selftest_read_and_track_wires_both_effects() -> None:
    """read_and_track must (a) grow tracker co-occurrences AND (b) actually flag the lemma into
    state.library via the REAL (unmodified) process_sentence call -- both effects checked, real
    code path, not a synthetic-only branch (SCHEMA-VET F.1)."""
    state = _fresh_state(1)
    seed_known_words(state, ["the", "a", "before", "harvest", "engine", "rattling"], "seed")
    tracker = PrereqTracker()
    read_and_track(state, tracker, "Nell repaired the rattling velmara engine before harvest.",
                   "e0", pass_idx=1)
    assert "velmara" in tracker.co_occurrences, tracker.co_occurrences
    assert "engine" in tracker.co_occurrences["velmara"][0]
    assert "velmara" in state.library.items, "process_sentence must have actually flagged velmara"
    assert len(state.library.items["velmara"].traces) == 1


def _selftest_identify_prefers_consistent_gap_over_sporadic_gap() -> None:
    """A candidate co-occurring in EVERY one of the target's sentences must outrank one that only
    co-occurs sometimes; an already-KNOWN co-occurring word must never appear as a candidate at
    all (real gap signal, use_gap_signal=True)."""
    state = _fresh_state(2)
    seed_known_words(state, ["the", "a", "before", "sensor", "using", "engine", "calibrated",
                             "delicate", "harvest"], "seed")
    tracker = PrereqTracker()
    sentences = [
        "Nell calibrated the delicate dravithex sensor using the velmara engine before harvest.",
        "Owen adjusted the delicate dravithex sensor using the velmara engine before harvest, ignoring the borlune manual.",
        "The dravithex sensor needed calibration using the velmara engine before harvest.",
    ]
    for i, s in enumerate(sentences):
        read_and_track(state, tracker, s, f"e{i}", pass_idx=1)
    cands = identify_missing_prerequisites(state, tracker, "dravithex", use_gap_signal=True)
    names = [c.lemma for c in cands]
    assert "velmara" in names, f"true consistent gap must be a candidate: {cands}"
    assert names[0] == "velmara", f"consistent gap must rank first, got {cands}"
    assert "engine" not in names, f"already-KNOWN co-occurring word must never be a candidate: {cands}"
    velmara_c = next(c for c in cands if c.lemma == "velmara")
    assert abs(velmara_c.score - 1.0) < 1e-9, f"velmara co-occurs in all 3 sentences: {velmara_c}"
    if "borlune" in names:
        borlune_c = next(c for c in cands if c.lemma == "borlune")
        assert velmara_c.score > borlune_c.score, (velmara_c, borlune_c)


def _selftest_identify_empty_when_never_seen() -> None:
    state = _fresh_state(3)
    tracker = PrereqTracker()
    assert identify_missing_prerequisites(state, tracker, "nevermentioned") == []


def _selftest_ablation_is_load_bearing_not_silently_ignored() -> None:
    """use_gap_signal=False must ACTUALLY change identify_missing_prerequisites' output on a
    fixture where a co-occurring word is already GROUNDED (so real signal excludes it, ablated
    signal may include it) -- proves the ablation hook threads through, not silently ignored
    (same discipline as grounding_acquisition_loop.self_test's coherence_fn load-bearing check)."""
    state = _fresh_state(4)
    seed_known_words(state, ["the", "a", "before", "sensor", "using", "calibrated", "delicate"],
                     "seed")
    # 'harvest' is deliberately NOT seeded -- under real signal it is a genuine (if irrelevant)
    # gap; under ablation its inclusion becomes a coin-flip draw from GapDetector's own
    # ablation_rng, uncorrelated with truth -- across enough repeated probes the two conditions'
    # is_gap verdicts for the SAME lemma must diverge at least once.
    tracker = PrereqTracker()
    sentences = [
        "Nell calibrated the delicate dravithex sensor using the velmara engine before harvest.",
        "Owen adjusted the delicate dravithex sensor using the velmara engine before harvest.",
    ]
    for i, s in enumerate(sentences):
        read_and_track(state, tracker, s, f"e{i}", pass_idx=1)
    real = identify_missing_prerequisites(state, tracker, "dravithex", use_gap_signal=True)
    ablated_runs = [identify_missing_prerequisites(state, tracker, "dravithex", use_gap_signal=False)
                    for _ in range(8)]
    real_names = {c.lemma for c in real}
    ablated_name_sets = [{c.lemma for c in run} for run in ablated_runs]
    assert any(s != real_names for s in ablated_name_sets), (
        f"ablation must be load-bearing (candidate SET must differ from real at least once across "
        f"8 draws), real={real_names}, ablated_runs={ablated_name_sets}")
    assert all(c.ablated for run in ablated_runs for c in run), "ablated candidates must carry ablated=True"
    assert all(not c.ablated for c in real), "real-signal candidates must carry ablated=False"


def _selftest_rank_material_orders_by_target_occurrence() -> None:
    state = _fresh_state(5)
    docs = {
        "doc_a": ["The velmara field powers every device.", "A velmara field is measured in units."],
        "doc_b": ["The borlune manual is long.", "Nobody reads the borlune manual twice."],
        "doc_c": ["velmara velmara velmara appears here once as a sentence."],
    }
    ranking = rank_material(state, "velmara", docs)
    doc_scores = dict(ranking)
    assert doc_scores["doc_a"] == 2, ranking  # 2 sentences each mention velmara
    assert doc_scores["doc_c"] == 1, ranking  # 1 sentence total (velmara repeated within it, still 1 sentence)
    assert doc_scores["doc_b"] == 0, ranking
    assert ranking[0][0] == "doc_a", ranking  # highest sentence-level count ranks first


def _selftest_next_read_target_falls_back_to_primary() -> None:
    """When no missing prerequisite is identified (nothing recorded yet, or nothing survives the
    gap filter), next_read_target must fall back to the primary lemma itself, not crash or return
    an unrelated lemma."""
    state = _fresh_state(6)
    tracker = PrereqTracker()
    target, cands = next_read_target(state, tracker, "dravithex", use_gap_signal=True)
    assert target == "dravithex" and cands == [], (target, cands)


def _selftest_no_ground_truth_leak_in_signature() -> None:
    """Structural no-leak check: neither identify_missing_prerequisites nor rank_material accepts
    any parameter whose name suggests ground-truth (true_*, answer, label, gold*) -- the algorithm
    can only ever see what it observed (tracker) + what the substrate's own gap signal reports
    (state.gap_detector), never an externally-supplied 'correct answer'."""
    for fn in (identify_missing_prerequisites, rank_material, next_read_target):
        params = set(inspect.signature(fn).parameters)
        leaky = {p for p in params if any(tok in p.lower() for tok in
                                          ("true_", "answer", "label", "gold", "ground_truth"))}
        assert not leaky, f"{fn.__name__} signature leaks ground truth via params {leaky}"


def _selftest_end_to_end_real_code_path_identify_and_ground() -> None:
    """SCHEMA-VET F.1: exercises the REAL substrate objects (HDFactStore, ReadingLoopState,
    GapDetector via seed_known_words, Library via process_sentence, consolidation via
    reading_grounding_loop.checkpoint) at small scale -- not a synthetic-only branch. Mini version
    of the controlled scenario: B is introduced BEFORE its prerequisite A; identification must
    name A specifically; after reading A-material and B's fuller explanation, B must GROUND."""
    seed_vocab = ["the", "a", "before", "harvest", "began", "long", "season", "this", "year",
                 "sensor", "using", "engine", "calibrated", "adjusted", "delicate", "needed",
                 "calibration", "every", "nell", "owen", "skilled", "mechanic", "old", "repaired",
                 "rattling", "fixed", "noisy", "again"]
    state = _fresh_state(7, n_dim=4096)
    seed_known_words(state, seed_vocab, "seed")
    tracker = PrereqTracker()
    b_intro = [
        "Nell calibrated the delicate dravithex sensor using the velmara engine before harvest.",
        "Owen adjusted the delicate dravithex sensor using the velmara engine again before the long harvest.",
    ]
    a_material = [
        "Nell repaired the rattling velmara engine before the harvest began.",
        "Owen fixed the noisy velmara engine again before the long harvest.",
        "The old velmara engine needed repair every year before harvest season.",
        "A skilled mechanic repaired the velmara engine before this year harvest.",
    ]
    b_explained = [
        "The old dravithex sensor needed calibration using the velmara engine every year before harvest season.",
        "A skilled mechanic calibrated the dravithex sensor using the velmara engine before this year harvest.",
    ]
    pass_idx = 1
    for i, s in enumerate(b_intro):
        read_and_track(state, tracker, s, f"bi{i}", pass_idx)
    checkpoint(state, pass_idx, "bintro")
    target, cands = next_read_target(state, tracker, "dravithex", use_gap_signal=True)
    assert target == "velmara", f"must identify velmara as dravithex's missing prerequisite: {cands}"
    pass_idx += 1
    for i, s in enumerate(a_material):
        read_and_track(state, tracker, s, f"am{i}", pass_idx)
    checkpoint(state, pass_idx, "amaterial")
    assert state.library.items["dravithex"].status == "PENDING", "dravithex must not ground before its explanation is read"
    pass_idx += 1
    for i, s in enumerate(b_explained):
        read_and_track(state, tracker, s, f"be{i}", pass_idx)
    checkpoint(state, pass_idx, "bexplained")
    grounded = False
    for _ in range(4):
        pass_idx += 1
        checkpoint(state, pass_idx, "settle")
        if state.library.items["dravithex"].status == "GROUNDED_POS":
            grounded = True
            break
    assert grounded, f"dravithex must GROUND once its prerequisite is read then its explanation follows, final status={state.library.items['dravithex'].status}"
    assert state.library.items["velmara"].status == "GROUNDED_POS", state.library.items["velmara"].status
    assert is_gap_now(state, "dravithex") is False


def is_gap_now(state: ReadingLoopState, lemma: str) -> bool:
    """Thin convenience wrapper: fresh (non-memoized) gap check via state.gap_detector, refreshed.
    Distinct from reading_grounding_loop.is_gap (which memoizes per-lemma in state.gap_cache) --
    this module's identification logic calls state.gap_detector.familiarity directly per-candidate
    every time (candidates are re-evaluated as the foundation changes across scheduling steps), so
    this wrapper exists only for TEST/reporting convenience, not on the hot identification path."""
    state.gap_detector.refresh()
    return state.gap_detector.familiarity(lemma, KNOWN_RELATION, KNOWN_OBJECT).is_gap


def _run_all_selftests() -> dict:
    _selftest_tracker_records_cooccurrence()
    _selftest_read_and_track_wires_both_effects()
    _selftest_identify_prefers_consistent_gap_over_sporadic_gap()
    _selftest_identify_empty_when_never_seen()
    _selftest_ablation_is_load_bearing_not_silently_ignored()
    _selftest_rank_material_orders_by_target_occurrence()
    _selftest_next_read_target_falls_back_to_primary()
    _selftest_no_ground_truth_leak_in_signature()
    _selftest_end_to_end_real_code_path_identify_and_ground()
    return {
        "tracker_ok": True,
        "read_and_track_wires_both_effects_ok": True,
        "identify_prefers_consistent_gap_ok": True,
        "identify_empty_when_unseen_ok": True,
        "ablation_load_bearing_ok": True,
        "rank_material_orders_by_occurrence_ok": True,
        "next_read_target_fallback_ok": True,
        "no_ground_truth_leak_ok": True,
        "end_to_end_real_code_path_identify_and_ground_ok": True,
        "reuse": ["hdlab.reading_grounding_loop", "hdlab.gap_detector.GapDetector",
                  "hdlab.hd_fact_store.HDFactStore"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(_run_all_selftests(), indent=2))
    print("ALL SELF-TESTS PASSED")
