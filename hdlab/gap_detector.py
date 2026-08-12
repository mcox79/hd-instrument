"""hdlab/gap_detector.py -- ONLINE, AUTONOMOUS gap detection over a live hdlab.hd_fact_store.
HDFactStore, 2026-08-11.

Closes architecture-audit finding #3 (notes/architecture_audit_2026-08-11.md TIER-2 item 3,
VERY HIGH impact): every "gap" in this codebase up to now is an OFFLINE KB set-difference
(build_gap_set) or a hand-picked curriculum -- a MISLABEL, since nothing on disk ever asked the
substrate itself "do I already know this?" This module is that missing organ: for ONE incoming
(subject, relation, candidate_object) probe, compute a continuous FAMILIARITY/CONFIDENCE margin
from the substrate's OWN live retrieval/completion state and compare it to a decision FLOOR --
below floor => GAP (flag it, feed the gather->reason->gate loop); at/above floor => already
known, skip. No pre-computed gap-set is ever consulted; the decision is made fresh, per probe,
from whatever HDFactStore.live_facts() currently contains.

BRAIN-FOUNDATIONAL FRAMING (per task instruction, this is the actual mechanism, not decoration):
  - CA3/DG pattern completion (hdlab.cleanup_family.iterative_attractor, imported verbatim, NOT
    reimplemented) picks the BEST-MATCHING known item for a probe out of the live codebook.
  - CA1 match/mismatch COMPARATOR: the margin itself is the raw cosine between the untouched
    probe and its CA3-selected best match -- how well the "expected" (retrieved) pattern agrees
    with the "actual" (incoming) one, computed BEFORE the attractor's iterative pull forces
    convergence (a post-settle read would trivially converge toward SOME match regardless of
    true novelty, which would make the comparator uninformative -- see ca3_match_score below).
  - The codebook is rebuilt from hdlab.hd_fact_store.HDFactStore.live_facts() on every refresh()
    -- i.e. from the store's OWN consolidation-status bookkeeping (ACTIVE_STATUSES), so the
    detector is sensitive to the store's actual current state (a fact that gets SUPERSEDED via
    the store's own store()-ingest-vet conflict resolution silently drops out of the codebook,
    no separate "delete" needed) -- see test 3 (KB-state-sensitivity) in the calling cell.

REUSE (wire-don't-island; every organ below is imported read-only, called verbatim; this module
adds NO new binding/cleanup mechanism, only the "return a graded margin to the caller" wiring
gather_reason.ca3_relevance_gather does not itself expose):
  hdlab.cleanup_family.iterative_attractor          (CA3/DG attractor argmax pick)
  hdlab.hd_fact_store.HDFactStore / ACTIVE_STATUSES  (live consolidation-status-aware store)
  hdlab.role_slot_summarizer._bipolar_bind/_bipolar_quantize (the SAME bipolar primitives
                                                       HDFactStore._sr_key already uses; content_key
                                                       below is a direct 3-pair extension of that
                                                       existing 2-pair (subject,relation) signature
                                                       pattern -- not a new binding scheme)

NOT reused here (by design, to avoid touching in-flight modules): hdlab.gather_reason.py and
hdlab.three_tier_loop.py are consumed by the CALLING cell (experiments/exp_gap_detection_
autonomous_confidence_v1.py) for the GATHER+REASON+GATE end-to-end demonstration; this module
stays a single-purpose DETECTOR so it composes into that (or any other) loop without a dependency
edge back onto it.

ASCII-only. Deterministic: content_key gives a bit-identical vector for identical (subject,
relation, obj) strings; the only randomness anywhere is the store's own seeded symbol codebook
(torch.Generator, seeded once at HDFactStore construction). No hash(), no list(set()) ordering
(PROT-023 / F.5 compliant) -- refresh() explicitly sorts live facts by fid (monotonic append
order) before stacking the codebook.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch

from hdlab import cleanup_family
from hdlab.hd_fact_store import HDFactStore
from hdlab.role_slot_summarizer import _bipolar_bind, _bipolar_quantize

TripleKey = Tuple[str, str, str]


def content_key(store: HDFactStore, subject: str, relation: str, obj: str) -> torch.Tensor:
    """Deterministic 3-pair bipolar content signature: bind(REL,relation) + bind(ARG0,subject) +
    bind(ARG1,obj), quantized. Directly extends HDFactStore._sr_key's existing 2-pair
    (subject,relation) signature pattern by one more bound pair (the object) -- same primitives
    (_bipolar_bind/_bipolar_quantize), same shared symbol codebook (store.codec._sym_vec), same
    codec instance the store itself uses for _encode_fact/_sr_key. This is needed (rather than
    reusing store._encode_fact directly) because a GAP PROBE has no SOURCE/TRUST yet -- that is
    exactly the thing being asked about -- so probe vectors and stored-fact vectors must be
    compared on the CONTENT-ONLY (REL,ARG0,ARG1) subspace, which _encode_fact's full 5-role
    bundle does not expose on its own.

    Side effect (disclosed, harmless to KB content): calling this on a subject/relation/object
    string never seen before makes store.codec lazily register a fresh deterministic vector for
    it (codec._sym_vec's own pre-existing lazy-registration design, used everywhere else in this
    module's call graph too) -- this grows the store's SHARED symbol vector cache but does NOT
    call _register_domain and does NOT append a FactRecord, so it never changes live_facts(),
    query() results, or recover_fact's per-domain cleanup codebooks. Gap-probing is non-mutating
    with respect to the store's actual KNOWLEDGE content."""
    codec = store.codec
    acc = (_bipolar_bind(codec.role_key("REL"), codec._sym_vec(str(relation)))
           + _bipolar_bind(codec.role_key("ARG0"), codec._sym_vec(str(subject)))
           + _bipolar_bind(codec.role_key("ARG1"), codec._sym_vec(str(obj))))
    return _bipolar_quantize(acc)


def ca3_match_score(query_vec: np.ndarray, codebook: np.ndarray, *,
                    temp: float = 8.0, max_steps: int = 6) -> Tuple[int, float, bool, int]:
    """CA3/DG attractor best-match pick (hdlab.cleanup_family.iterative_attractor, called
    verbatim -- the ACTUAL completion mechanism, not reimplemented) + a CA1-style raw cosine
    comparator margin between the UNTOUCHED query and its winning codebook row.

    The margin is computed from the RAW query (before any attractor iteration pulls it toward a
    winner), not from iterative_attractor's own settled `state` output: the attractor's softmax
    dynamics blend toward SOME codebook combination on every call (that is the whole point of an
    attractor), so a post-settle read would be uninformative here -- it would report "converged"
    confidently for genuinely novel queries too. Reading the PRE-settle resemblance (identical
    dot/norm convention hdlab.gather_reason.ca3_relevance_gather's own peel-loop uses internally,
    factored out here since that function does not expose its score to callers) is what makes the
    margin a real match/mismatch COMPARATOR rather than a foregone "it always settles" readout.

    query_vec/codebook are bipolar {-1,+1} arrays (equal-norm rows), so dot/norm-normalized cosine
    and dot/n_dim (HDFactStore's own _sr_key convention, see _selftest_sr_key_separates) coincide;
    the norm-based form is used here so this also works for a non-bipolar codebook unmodified.

    Returns (best_idx, margin, converged, n_iterations)."""
    _, diag = cleanup_family.iterative_attractor(query_vec, codebook, temp=temp, max_steps=max_steps)
    idx = int(diag["final_argmax_idx"])
    cb_row = codebook[idx]
    qn = float(np.linalg.norm(query_vec))
    cn = float(np.linalg.norm(cb_row))
    denom = qn * cn + 1e-8
    margin = float(np.dot(query_vec, cb_row) / denom) if denom > 0 else 0.0
    return idx, margin, bool(diag["converged"]), int(diag["n_iterations"])


@dataclass
class FamiliarityResult:
    margin: float
    is_gap: bool
    matched_key: Optional[TripleKey]
    codebook_size: int
    converged: bool
    n_iterations: int
    ablated: bool = False


class GapDetector:
    """Online, autonomous gap detector wrapping ONE live hdlab.hd_fact_store.HDFactStore.

    No pre-built gap-set / KB-diff is ever constructed or consulted: refresh() rebuilds the
    known-content codebook FRESH from store.live_facts() (the store's own current consolidation
    state) and familiarity() computes a fresh CA3/CA1 margin per probe. floor is a caller-chosen,
    pre-registered decision threshold (see the calling cell's pre-reg for the THEORETICAL
    derivation of the default 0.625 used there); this module has no opinion on where it should
    sit -- that is a calibration choice, not a mechanism constant.
    """

    def __init__(self, store: HDFactStore, floor: float, *, temp: float = 8.0,
                 max_steps: int = 6, ablation_seed: int = 20260811) -> None:
        self.store = store
        self.floor = float(floor)
        self.temp = float(temp)
        self.max_steps = int(max_steps)
        self._codebook: Optional[np.ndarray] = None
        self._codebook_keys: List[TripleKey] = []
        self._ablation_rng = np.random.default_rng(ablation_seed)

    def refresh(self) -> int:
        """(Re)build the known-content codebook from store.live_facts() -- the substrate's OWN
        CURRENT consolidation state (ACTIVE/COMBINED/FLAGGED only; SUPERSEDED/DROPPED facts, e.g.
        via the store's own store()-ingest-vet REPLACE resolution, drop out automatically, no
        separate bookkeeping in this module). Deterministic ordering: sorted by fid (the store's
        own monotonic append order; explicit sort, not relied on implicitly). Returns codebook
        size (0 is valid -- an empty KB; every probe is then trivially a gap)."""
        facts = sorted(self.store.live_facts(), key=lambda f: f.fid)
        keys: List[TripleKey] = [(f.subject, f.relation, f.obj) for f in facts]
        if not keys:
            self._codebook = np.zeros((0, self.store.n_dim), dtype=np.float32)
            self._codebook_keys = []
            return 0
        vecs = [content_key(self.store, s, r, o).numpy().astype(np.float32) for (s, r, o) in keys]
        self._codebook = np.stack(vecs, axis=0)
        self._codebook_keys = keys
        return len(keys)

    def familiarity(self, subject: str, relation: str, obj: str, *,
                    use_confidence_signal: bool = True) -> FamiliarityResult:
        """The gap-detection decision for ONE probe. use_confidence_signal=False is the ABLATION
        hook (test 2, NOT-A-LOOKUP): when False, the REAL CA3/CA1 margin is computed (so codebook
        state + attractor diagnostics are unchanged) but then DISCARDED and replaced by a
        fixed-seed uniform-noise draw uncorrelated with true known/novel status, from a SEPARATE
        deterministic RNG stream consumed in call order -- proving the floor decision's quality
        comes from the real signal (ablating it collapses detection to chance), not from some
        other hidden shortcut in this code path."""
        if self._codebook is None:
            self.refresh()
        q = content_key(self.store, subject, relation, obj).numpy().astype(np.float32)
        if self._codebook.shape[0] == 0:
            idx, margin, converged, n_iter = None, 0.0, False, 0
        else:
            idx, margin, converged, n_iter = ca3_match_score(
                q, self._codebook, temp=self.temp, max_steps=self.max_steps)
        ablated = not use_confidence_signal
        if ablated:
            margin = float(self._ablation_rng.uniform(-1.0, 1.0))
        is_gap = margin < self.floor
        matched_key = (self._codebook_keys[idx] if (idx is not None and self._codebook.shape[0] > 0)
                      else None)
        return FamiliarityResult(margin=margin, is_gap=is_gap, matched_key=matched_key,
                                 codebook_size=int(self._codebook.shape[0]), converged=converged,
                                 n_iterations=n_iter, ablated=ablated)

    def batch_familiarity(self, triples: Sequence[TripleKey], *,
                          use_confidence_signal: bool = True) -> List[FamiliarityResult]:
        """Convenience: familiarity() over an ordered sequence of (subject,relation,obj) probes.
        Deterministic (no reordering); one attractor call per probe (codebook sizes here are small
        enough -- hundreds of rows -- that this is milliseconds per probe, no batching needed)."""
        return [self.familiarity(s, r, o, use_confidence_signal=use_confidence_signal)
                for (s, r, o) in triples]


# ===================== formula self-tests ==========================================

def _fresh_store(seed: int, n_dim: int = 2048) -> HDFactStore:
    return HDFactStore(n_dim=n_dim, seed=seed, relation_cardinality={"rel_a": "FUNCTIONAL"})


def _selftest_known_exact_match_margin_is_one() -> None:
    """A probe reproducing an exact stored (s,r,o) gets margin == 1.0 (bit-identical content
    key) and is NEVER flagged a gap at any floor < 1.0."""
    st = _fresh_store(1)
    st.store("alice", "rel_a", "paris", "src", "TRUST_HIGH")
    det = GapDetector(st, floor=0.625)
    det.refresh()
    r = det.familiarity("alice", "rel_a", "paris")
    assert abs(r.margin - 1.0) < 1e-6, f"exact-match margin != 1.0: {r.margin}"
    assert r.is_gap is False, r
    assert r.matched_key == ("alice", "rel_a", "paris"), r.matched_key


def _selftest_wholly_novel_margin_low() -> None:
    """A probe sharing NO role symbol with any stored fact (new relation, new subject, new
    object) gets a low margin (near the random-vector noise floor) and IS flagged a gap."""
    st = _fresh_store(2)
    for i in range(20):
        st.store(f"s{i}", "rel_a", f"o{i}", "src", "TRUST_HIGH")
    det = GapDetector(st, floor=0.625)
    det.refresh()
    r = det.familiarity("brand_new_subject", "brand_new_relation", "brand_new_object")
    assert r.margin < 0.20, f"wholly-novel margin too high: {r.margin} (matched {r.matched_key})"
    assert r.is_gap is True, r


def _selftest_shares_two_of_three_is_intermediate() -> None:
    """A probe sharing (subject,relation) with a stored fact but a DIFFERENT object -- the
    'novel-hard' construction -- gets an INTERMEDIATE margin (theory: ~0.5 for large n_dim;
    empirically measured, tolerant band) strictly between the exact-match (1.0) and
    wholly-novel (near-0) cases, and at n_dim=4096 is comfortably separated from the 0.625
    floor used throughout the calling cell."""
    st = _fresh_store(3, n_dim=4096)
    st.store("bob", "rel_a", "true_obj", "src", "TRUST_HIGH")
    for i in range(30):  # distractors so the codebook isn't trivially size-1
        st.store(f"filler{i}", "rel_a", f"filler_obj{i}", "src", "TRUST_HIGH")
    det = GapDetector(st, floor=0.625)
    det.refresh()
    r_exact = det.familiarity("bob", "rel_a", "true_obj")
    r_hard = det.familiarity("bob", "rel_a", "wrong_obj_never_stored")
    assert r_exact.margin > 0.99, r_exact
    assert 0.30 < r_hard.margin < 0.70, f"novel-hard margin outside expected intermediate band: {r_hard.margin}"
    assert r_hard.margin < r_exact.margin, (r_hard.margin, r_exact.margin)
    assert r_hard.is_gap is True and r_exact.is_gap is False, (r_hard, r_exact)


def _selftest_ablation_collapses_to_uncorrelated_noise() -> None:
    """use_confidence_signal=False replaces the margin with noise UNCORRELATED with the true
    known/novel status -- known and novel items' ablated margins must NOT be reliably separated
    (mean absolute difference near 0, unlike the real-signal case which is close to 1.0)."""
    st = _fresh_store(4, n_dim=2048)
    for i in range(15):
        st.store(f"k{i}", "rel_a", f"ko{i}", "src", "TRUST_HIGH")
    det = GapDetector(st, floor=0.625)
    det.refresh()
    real_known = [det.familiarity(f"k{i}", "rel_a", f"ko{i}").margin for i in range(15)]
    real_novel = [det.familiarity(f"novel{i}", "rel_a", f"novel_o{i}").margin for i in range(15)]
    ab_known = [det.familiarity(f"k{i}", "rel_a", f"ko{i}", use_confidence_signal=False).margin
               for i in range(15)]
    ab_novel = [det.familiarity(f"novel{i}", "rel_a", f"novel_o{i}", use_confidence_signal=False).margin
               for i in range(15)]
    real_gap = float(np.mean(real_known)) - float(np.mean(real_novel))
    ab_gap = float(np.mean(ab_known)) - float(np.mean(ab_novel))
    assert real_gap > 0.5, f"real signal must cleanly separate known/novel: {real_gap}"
    assert abs(ab_gap) < 0.35, f"ablated signal must NOT reliably separate known/novel: {ab_gap}"


def _selftest_scramble_flips_known_to_gap() -> None:
    """A fact known before a live-KB lesion (via the store's OWN store()-ingest-vet REPLACE
    resolution, trust MID -> HIGH) becomes a detected gap after -- proving refresh() reads the
    ACTUAL live consolidation state, not a static label frozen at first refresh()."""
    st = HDFactStore(n_dim=4096, seed=5, relation_cardinality={"rel_a": "FUNCTIONAL"})
    st.store("carol", "rel_a", "original_obj", "src", "TRUST_MID")
    for i in range(30):
        st.store(f"filler{i}", "rel_a", f"filler_obj{i}", "src", "TRUST_HIGH")
    det = GapDetector(st, floor=0.625)
    det.refresh()
    before = det.familiarity("carol", "rel_a", "original_obj")
    assert before.is_gap is False, f"pre-lesion known fact must NOT be a gap: {before}"
    res = st.store("carol", "rel_a", "lesion_replacement_obj", "lesion_src", "TRUST_HIGH")
    assert res.resolution == "REPLACE", f"lesion setup must REPLACE (trust MID->HIGH): {res}"
    det.refresh()  # re-read the NOW-live KB state
    after = det.familiarity("carol", "rel_a", "original_obj")
    assert after.is_gap is True, f"post-lesion the OLD fact must be detected as a gap: {after}"


def _selftest_empty_kb_everything_is_a_gap() -> None:
    st = _fresh_store(6)
    det = GapDetector(st, floor=0.625)
    n = det.refresh()
    assert n == 0
    r = det.familiarity("anyone", "rel_a", "anything")
    assert r.is_gap is True and r.codebook_size == 0, r


def _run_all_selftests() -> dict:
    _selftest_known_exact_match_margin_is_one()
    _selftest_wholly_novel_margin_low()
    _selftest_shares_two_of_three_is_intermediate()
    _selftest_ablation_collapses_to_uncorrelated_noise()
    _selftest_scramble_flips_known_to_gap()
    _selftest_empty_kb_everything_is_a_gap()
    return {"mechanism": "CA3 iterative_attractor argmax pick + CA1 raw pre-settle cosine comparator",
            "reuse": ["hdlab.cleanup_family.iterative_attractor", "hdlab.hd_fact_store.HDFactStore",
                     "hdlab.role_slot_summarizer._bipolar_bind/_bipolar_quantize"],
            "checks": ["exact_match_margin_1.0", "wholly_novel_low_margin",
                      "shares_two_of_three_intermediate", "ablation_collapses_to_noise",
                      "scramble_flips_known_to_gap", "empty_kb_all_gap"]}


if __name__ == "__main__":
    import json
    print(json.dumps(_run_all_selftests(), indent=2))
    print("ALL SELF-TESTS PASSED")
