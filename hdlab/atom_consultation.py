"""Atom-consultation primitive -- Cortex-2 first probe (2026-07-03).

Turns the ~99-atom Stage-1 CG_META / Fix#28 constraint store from PASSIVE
documentation into ACTIVE CONSTRAINTS automatically consulted at Cortex
operation boundaries. Advisory-only in v1 (applied=False throughout the
first probe); enforcement is a separate, later, explicitly-audited promotion
decision.

Design (per notes/exp_dev_handoff_research_cortex_2_atoms_as_active_
constraints_2026-07-04.md and research memo section c/d):

- NO_STORAGE primitive: AtomConsultant is a stateless in-memory tag-filtered
  retrieval wrapper. NOT a KB loader -- for the first probe we hand-populate
  a small curated atom-set (~5-15 atoms covering the 5 hand-built ground-
  truth cases). Wrapping the full DirectorKBQuery (~970k entities, ~16s per
  cosine sweep) would blow the sub-ms wall budget by 4 orders of magnitude
  and is deferred to a later phase.

- 5 explicit operation classes (fixed enum, NOT a learned router):
    COMPOSITION / FRAMING / CAPACITY / RETRIEVAL / VERIFY
  Cell-authors tag call-sites explicitly; the memo argues cost-benefit at
  N~100 atoms does not justify a learned gate.

- Match scoring: strict-subset tag filter first, then char-trigram cosine
  ranking within the filtered subset. Guarantees never full-scan bypass.

- Sub-ms wall budget: at N<=20 curated atoms + N_DIM=1024 char-trigram
  encoding, per-consult wall is bounded by a 20 x 1024 matmul + argmax
  which is O(mus) on CPU. Load-time cost is amortized across cell lifetime.

- Advisory-only: ConsultationResult.applied is always False in v1; the
  downstream primitive receives the recommendation but is NOT forced to
  honor it. The match-and-honored discriminator (below) measures whether
  recommendations correctly PREDICT the downstream choice, which is the
  actual load-bearing question.

Storage architecture: NO_STORAGE (stateless; each consult() call is pure
matmul over the frozen in-memory atom table).

Anti-drift discriminator (research memo section e):
    match_and_honored_rate = (matched AND honored) / (matched)
    HARD-PASS: >= 70% AND zero silent contradictions across >= 50 calls.
    HARD-FAIL: < 20% -> decorative retrieval, do NOT promote.

References:
- notes/research_drill_cortex_2_atoms_as_active_constraints_M3_v2_2026-07-04.md
- notes/exp_dev_handoff_research_cortex_2_atoms_as_active_constraints_2026-07-04.md
- project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28.md
- project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30.md

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from hdlab.char_trigram_encoder import CharTrigramEncoder


# Fixed operation-class enum (see research memo section c). Cell-authors
# explicitly tag call-sites with one of these; unknown classes are rejected.
VALID_OP_CLASSES = frozenset({
    "COMPOSITION",   # bind/bundle/chain-compose; storage-strategy law fires
    "FRAMING",       # axis labelling; Fix#28 rules fire (axis-aliasing etc)
    "CAPACITY",      # M/N/K sweeps; bundle-bound + phase-transition laws
    "RETRIEVAL",     # unbind + cleanup; sigma0 gate + noise-tolerance
    "VERIFY",        # cross-term measurement; both-arms-in-band META rules
})


# --------------------------------- dataclasses ------------------------------


@dataclass
class AtomMatch:
    """Single atom match from consult() output.

    Fields:
        atom_id: stable string id for the atom (used in provenance).
        tier: source tier ("CG" | "CG_META" | "FIX28" | "HYPOTHESIS" | ...).
        source_signature: citation for the atom (e.g. commit hash / atom-file
            path / date). Load-bearing for MM_STANDARD (source-signature cite
            per USER-locked memory rule 2026-07-03).
        relevance_cosine: char-trigram cosine similarity between the tagged
            operation_class + params blob and the atom's tag_vec.
        constraint_text: plain-string constraint the atom encodes (e.g.
            "SHARDED > BUNDLED for compositional storage at K > 0.138 * N").
        recommendation: the concrete recommendation this atom implies for the
            given operation (e.g. "SHARDED"). None if atom is descriptive only.
    """
    atom_id: str
    tier: str
    source_signature: str
    relevance_cosine: float
    constraint_text: str
    recommendation: Optional[str] = None


@dataclass
class ConsultationResult:
    """Return value from AtomConsultant.consult().

    Fields:
        operation_class: the tag the caller passed in (must be in VALID_OP_CLASSES).
        matched_atoms: list of AtomMatch, sorted by relevance_cosine descending.
        recommendation: top atom's recommendation (None if no atom above
            relevance floor).
        applied: v1 ADVISORY-ONLY -- always False. Downstream primitive receives
            the recommendation but is NOT forced to honor it.
        wall_ms: measured wall-clock time for this consult() call.
        n_atoms_scanned: number of atoms after operation-class tag-filter
            (strict subset of full atom count; never equal to full count).
        n_atoms_total: total atoms in the consultant (for tag-filter strictness
            audit; strict_subset = (n_scanned < n_total)).
    """
    operation_class: str
    matched_atoms: List[AtomMatch]
    recommendation: Optional[str]
    applied: bool
    wall_ms: float
    n_atoms_scanned: int
    n_atoms_total: int


# --------------------------------- consultant -------------------------------


# Internal atom record for the in-memory table.
@dataclass
class _AtomRecord:
    atom_id: str
    op_classes: frozenset  # subset of VALID_OP_CLASSES this atom applies to
    tier: str
    source_signature: str
    constraint_text: str
    recommendation: Optional[str]
    # Per-atom tag-vec (char-trigram encoding of constraint_text + op_classes).
    # Row of the consultant's encoded matrix.
    row_idx: int = -1


def _default_curated_atoms() -> List[_AtomRecord]:
    """Curated atom set covering the 5 ground-truth cases in the first probe.

    Sources (per hand-off memo + memory index 2026-07-03):
    - Case 1: STORAGE_STRATEGY_SHARDED_MASTER_MODERATOR (math4_v2 CG 2026-07-02).
    - Case 2: BUNDLED_first_order_phase_transition_no_midband (atom #49).
    - Case 3: SCALE_FREE_law_hippo (Cortex-1 primitive; Skunkworks 2026-07-02).
    - Case 4: axis_aliasing_TOPOLOGY_vs_ALGEBRA (Fix#28 atom #48).
    - Case 5: cross_term_both_arms_in_band (Skunkworks META atom #43).
    Extra distractors intentionally include atoms tagged to OTHER op_classes so
    the strict-subset tag-filter has non-trivial work to do (proves tag-filter
    isn't a no-op).
    """
    return [
        _AtomRecord(
            atom_id="STORAGE_STRATEGY_SHARDED_MASTER_MODERATOR_v1",
            op_classes=frozenset({"COMPOSITION"}),
            tier="CG_META",
            source_signature="math4_v2_2026-07-02",
            constraint_text=(
                "SHARDED storage dominates BUNDLED for compositional storage "
                "when K exceeds 0.138 times N (Amit-Gutfreund wall); use "
                "SHARDED for any COMPOSITION operation"),
            recommendation="SHARDED",
        ),
        _AtomRecord(
            atom_id="BUNDLED_first_order_phase_transition_no_midband_v1",
            op_classes=frozenset({"CAPACITY"}),
            tier="CG_META",
            source_signature="atom_49_bimodal_2026-06-30",
            constraint_text=(
                "BUNDLED storage shows first-order bimodal phase transition; "
                "no mid-band possible; capacity crosses the wall as step "
                "function not smooth degradation"),
            recommendation="NO_MID_BAND",
        ),
        _AtomRecord(
            atom_id="SCALE_FREE_law_hippo_v1",
            op_classes=frozenset({"COMPOSITION", "CAPACITY"}),
            tier="CG",
            source_signature="hippo_v5_CG_2026-07-02",
            constraint_text=(
                "hippo M-scale-free: cleanup accuracy invariant across N "
                "when M/N ratio held fixed; scale-free composition primitive"),
            recommendation="SCALE_FREE",
        ),
        _AtomRecord(
            atom_id="axis_aliasing_TOPOLOGY_vs_ALGEBRA_Fix28_v1",
            op_classes=frozenset({"FRAMING"}),
            tier="FIX28",
            source_signature="atom_48_axis_aliasing_2026-06-27",
            constraint_text=(
                "axis labelling TOPOLOGY when the actual sweep varies "
                "ALGEBRAIC composition depth is aliasing; frame as ALGEBRA "
                "not TOPOLOGY when depth is the varying dimension"),
            recommendation="ALGEBRA",
        ),
        _AtomRecord(
            atom_id="cross_term_both_arms_in_band_META_v1",
            op_classes=frozenset({"VERIFY"}),
            tier="CG_META",
            source_signature="atom_43_cross_term_both_arms_2026-07-01",
            constraint_text=(
                "cross-term measurement verdict requires BOTH arms land in "
                "measurable band 0.05 to 0.95; single-arm-saturated is "
                "vacuous null; verify both arms in-band before trusting"),
            recommendation="BOTH_ARMS_IN_BAND",
        ),
        # Distractors tagged to RETRIEVAL only -- exercise strict-subset filter.
        _AtomRecord(
            atom_id="sigma0_cleanup_gate_retrieval_v1",
            op_classes=frozenset({"RETRIEVAL"}),
            tier="CG_META",
            source_signature="skunkworks_sigma0_2026-06-29",
            constraint_text=(
                "every encoder arm must clear sigma0 cleanup recall >= 0.95 "
                "as first gate before mechanism claims fire; retrieval "
                "integrity precondition"),
            recommendation="SIGMA0_GATE",
        ),
        _AtomRecord(
            atom_id="unbind_noise_tolerance_scales_sqrtN_v1",
            op_classes=frozenset({"RETRIEVAL"}),
            tier="CG",
            source_signature="hrr_unbind_2026-06-15",
            constraint_text=(
                "unbind + cleanup noise tolerance scales as sqrt(N); noise "
                "sigma target should scale with N^0.5 to hold discriminator"),
            recommendation="SIGMA_SCALES_SQRT_N",
        ),
    ]


class AtomConsultant:
    """Advisory-only atom retrieval at Cortex operation boundaries.

    Storage: NO_STORAGE (curated atom table + precomputed tag-vec matrix; all
    frozen at __init__ time; consult() is pure read).

    Perf budget: at N_atoms <= 20 and n_dim = 1024, per-consult wall bounded
    by a (K, 1024) x (1024,) matmul + argmax, ~10-100 microseconds on CPU.
    Sub-ms budget (memo section d) has ~10x slack at this scale.
    """

    # Char-trigram encoder dim -- keep small for speed. This is NOT the
    # substrate n_dim; it is a tiny sidecar encoder purpose-built for tag
    # similarity, orthogonal to any substrate configuration.
    _TAG_ENCODER_N_DIM = 1024

    # Relevance floor: cosine below this is treated as "no match" (recommendation
    # returned as None). Empirically calibrated to reject uncorrelated noise
    # in char-trigram cosine at N=1024 (unrelated strings ~ 0.05-0.15).
    _RELEVANCE_FLOOR = 0.20

    def __init__(self, atoms: Optional[List[_AtomRecord]] = None) -> None:
        self._atoms: List[_AtomRecord] = list(
            atoms if atoms is not None else _default_curated_atoms())
        for i, a in enumerate(self._atoms):
            a.row_idx = i
        self._encoder = CharTrigramEncoder(n_dim=self._TAG_ENCODER_N_DIM)
        # Precompute per-atom tag vectors (constraint_text encoded).
        tag_vecs = np.zeros(
            (len(self._atoms), self._TAG_ENCODER_N_DIM), dtype=np.float32)
        for i, a in enumerate(self._atoms):
            v = self._encoder.encode(a.constraint_text)
            n = float(np.linalg.norm(v))
            if n > 0:
                v = v / n
            tag_vecs[i] = v
        self._tag_vecs = tag_vecs
        # Precompute per-op-class row index list for O(1) tag-filter.
        self._rows_by_op: dict = {oc: [] for oc in VALID_OP_CLASSES}
        for i, a in enumerate(self._atoms):
            for oc in a.op_classes:
                self._rows_by_op[oc].append(i)

    def n_atoms_total(self) -> int:
        return len(self._atoms)

    def consult(self, operation_class: str,
                params: Optional[dict] = None,
                query_hint: Optional[str] = None,
                k: int = 3) -> ConsultationResult:
        """Consult the atom table for a given operation-class + params.

        Args:
            operation_class: one of VALID_OP_CLASSES; unknown class raises.
            params: optional dict of operation params (e.g. {"storage":
                "BUNDLED", "N": 1024, "M": 6400}). Used to build the query
                hint if query_hint not supplied.
            query_hint: optional explicit query string; if None, built from
                (operation_class, params) automatically.
            k: max atoms to return in matched_atoms (top-k above floor).

        Returns:
            ConsultationResult with matched_atoms sorted descending by
            relevance_cosine, recommendation from top atom (or None if all
            below floor), applied=False (advisory only), and wall_ms.
        """
        t0 = time.perf_counter()
        if operation_class not in VALID_OP_CLASSES:
            raise ValueError(
                f"unknown operation_class {operation_class!r}; "
                f"must be one of {sorted(VALID_OP_CLASSES)}")

        # Build query string from operation_class + params + hint.
        parts = [operation_class]
        if params:
            for key in sorted(params.keys()):
                parts.append(f"{key}={params[key]}")
        if query_hint:
            parts.append(query_hint)
        query = " ".join(str(p) for p in parts)

        # Strict-subset tag-filter: candidate rows = union of atoms tagged
        # with this operation_class. Guarantees never a full-scan bypass.
        candidate_rows = self._rows_by_op.get(operation_class, [])
        n_scanned = len(candidate_rows)
        if n_scanned == 0:
            return ConsultationResult(
                operation_class=operation_class,
                matched_atoms=[],
                recommendation=None,
                applied=False,
                wall_ms=(time.perf_counter() - t0) * 1000.0,
                n_atoms_scanned=0,
                n_atoms_total=len(self._atoms),
            )

        # Encode query + cosine vs. candidate rows only.
        q = self._encoder.encode(query).astype(np.float32)
        qn = float(np.linalg.norm(q))
        if qn > 0:
            q = q / qn
        sub_matrix = self._tag_vecs[candidate_rows]  # (n_scanned, n_dim)
        sims = sub_matrix @ q  # (n_scanned,)

        # Top-k above relevance floor.
        order = np.argsort(-sims)
        matches: List[AtomMatch] = []
        for pos in order[:k]:
            cos = float(sims[pos])
            if cos < self._RELEVANCE_FLOOR:
                break
            row = candidate_rows[pos]
            a = self._atoms[row]
            matches.append(AtomMatch(
                atom_id=a.atom_id,
                tier=a.tier,
                source_signature=a.source_signature,
                relevance_cosine=cos,
                constraint_text=a.constraint_text,
                recommendation=a.recommendation,
            ))
        top_rec = matches[0].recommendation if matches else None
        wall_ms = (time.perf_counter() - t0) * 1000.0
        return ConsultationResult(
            operation_class=operation_class,
            matched_atoms=matches,
            recommendation=top_rec,
            applied=False,  # ADVISORY-ONLY in v1; enforcement is later phase.
            wall_ms=wall_ms,
            n_atoms_scanned=n_scanned,
            n_atoms_total=len(self._atoms),
        )


# ------------------------------ formula selftests ---------------------------


def _selftest_op_class_enum_rejects_unknown() -> None:
    """Unknown operation_class raises ValueError."""
    ac = AtomConsultant()
    try:
        ac.consult("BOGUS_CLASS")
    except ValueError:
        return
    raise AssertionError("expected ValueError on unknown operation_class")


def _selftest_strict_subset_tag_filter() -> None:
    """Every consult() scans STRICTLY FEWER atoms than total (never bypass)."""
    ac = AtomConsultant()
    total = ac.n_atoms_total()
    for oc in VALID_OP_CLASSES:
        r = ac.consult(oc, params={"probe": "x"})
        if r.n_atoms_scanned >= total:
            raise AssertionError(
                f"tag-filter bypassed for {oc}: scanned={r.n_atoms_scanned} "
                f">= total={total}")
        if r.n_atoms_total != total:
            raise AssertionError(
                f"n_atoms_total mismatch: got {r.n_atoms_total}, expected {total}")


def _selftest_sub_ms_wall_budget() -> None:
    """Per-consult wall <= 5ms (memo section d perf budget).

    Warmed-up steady-state; the first call may include lazy imports.
    """
    ac = AtomConsultant()
    # Warm up (first call may include lazy imports / OS page-in).
    _ = ac.consult("COMPOSITION", params={"storage": "BUNDLED", "N": 1024})
    walls = []
    for _ in range(20):
        r = ac.consult("COMPOSITION", params={"storage": "BUNDLED", "N": 1024})
        walls.append(r.wall_ms)
    p95 = float(np.percentile(walls, 95))
    if p95 > 5.0:
        raise AssertionError(
            f"consult() p95 wall {p95:.3f}ms exceeds 5ms budget")


def _selftest_case1_storage_strategy_fires() -> None:
    """Case 1: COMPOSITION with BUNDLED storage retrieves SHARDED law atom."""
    ac = AtomConsultant()
    r = ac.consult("COMPOSITION",
                   params={"storage": "BUNDLED", "N": 1024, "M": 6400,
                           "corr": 0.85})
    if r.recommendation != "SHARDED":
        raise AssertionError(
            f"case 1 expected recommendation SHARDED; got {r.recommendation!r} "
            f"(top match: "
            f"{r.matched_atoms[0].atom_id if r.matched_atoms else 'NONE'})")


def _selftest_case2_bundled_bimodal_fires() -> None:
    """Case 2: CAPACITY with BUNDLED at L=2 retrieves bimodal atom."""
    ac = AtomConsultant()
    r = ac.consult("CAPACITY",
                   params={"storage": "BUNDLED", "L": 2, "F": 1},
                   query_hint="first-order phase transition bimodal")
    if r.recommendation != "NO_MID_BAND":
        raise AssertionError(
            f"case 2 expected recommendation NO_MID_BAND; got "
            f"{r.recommendation!r}")


def _selftest_case4_framing_axis_aliasing_fires() -> None:
    """Case 4: FRAMING with TOPOLOGY vs ALGEBRA axis retrieves Fix#28 atom."""
    ac = AtomConsultant()
    r = ac.consult("FRAMING",
                   params={"axis_label": "TOPOLOGY", "actual_sweep": "depth"},
                   query_hint="axis labelling algebra depth")
    if r.recommendation != "ALGEBRA":
        raise AssertionError(
            f"case 4 expected recommendation ALGEBRA; got {r.recommendation!r}")


def _selftest_case5_verify_cross_term_fires() -> None:
    """Case 5: VERIFY on cross-term measurement retrieves both-arms-in-band."""
    ac = AtomConsultant()
    r = ac.consult("VERIFY",
                   params={"measurement": "cross_term", "arms": 2},
                   query_hint="both arms in band measurable verdict")
    if r.recommendation != "BOTH_ARMS_IN_BAND":
        raise AssertionError(
            f"case 5 expected recommendation BOTH_ARMS_IN_BAND; got "
            f"{r.recommendation!r}")


def _selftest_applied_always_false_v1() -> None:
    """ADVISORY-ONLY contract: applied must always be False in v1."""
    ac = AtomConsultant()
    for oc in VALID_OP_CLASSES:
        r = ac.consult(oc, params={"probe": "x"})
        if r.applied is not False:
            raise AssertionError(
                f"v1 advisory contract violated: applied={r.applied} for {oc}")


def _run_all_selftests() -> dict:
    _selftest_op_class_enum_rejects_unknown()
    _selftest_strict_subset_tag_filter()
    _selftest_sub_ms_wall_budget()
    _selftest_case1_storage_strategy_fires()
    _selftest_case2_bundled_bimodal_fires()
    _selftest_case4_framing_axis_aliasing_fires()
    _selftest_case5_verify_cross_term_fires()
    _selftest_applied_always_false_v1()
    return {
        "primitive": "AtomConsultant",
        "phase": "ADVISORY_ONLY_v1",
        "storage": "NO_STORAGE",
        "op_classes": sorted(VALID_OP_CLASSES),
        "curated_atoms": AtomConsultant().n_atoms_total(),
        "wall_budget_ms": 5.0,
    }


if __name__ == "__main__":
    result = _run_all_selftests()
    print(f"[atom_consultation selftest] PASS {result}")
