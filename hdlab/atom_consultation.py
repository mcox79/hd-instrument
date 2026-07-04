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

import os
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from hdlab.char_trigram_encoder import CharTrigramEncoder


# Phase 2 enforcement graduation modes (per-atom flag; OPA/Gatekeeper pattern
# per research drill 2026-07-04 section 4). Default SHADOW; hand-promoted.
VALID_ENFORCEMENT_MODES = frozenset({"SHADOW", "WARN", "LIVE"})


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
    # Phase 2 write-nonce (16-byte hex; per drill section 3 Discriminator A).
    # Fresh per-call; downstream must ack via read_and_ack_nonce() to prove
    # mechanical read. Empty string in Phase 1 advisory-only consult() calls.
    nonce: str = ""


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
    # Phase 2 fields (additive; Phase 1 code paths leave these at defaults).
    applied_flag: str = "SHADOW"         # per-atom effective mode this call
    null_arm: bool = False               # True for null-arm A/B trials
    nonce_written: str = ""              # nonce written to target on WARN/LIVE
    pre_value: Optional[Any] = None      # value in target[param_name] pre-write
    post_value: Optional[Any] = None     # value written to target[param_name]
    param_name: Optional[str] = None     # name of target slot written
    enforcement_wrote: bool = False      # True iff target actually mutated


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
    # Phase 2 per-atom graduation flag (SHADOW default; hand-promoted).
    enforcement_mode: str = "SHADOW"


# --------------------------- Enforcement decision log -----------------------


@dataclass
class EnforcementDecision:
    """Two-tier record from enforce() (per drill section 4)."""
    decision_id: str
    op_class: str
    atom_id: Optional[str]
    recommendation: Optional[str]
    pre_value: Optional[Any]
    post_value: Optional[Any]
    enforcement_mode: str
    nonce: str
    wall_ms: float
    ts_iso: str
    null_arm: bool
    enforcement_wrote: bool
    # Rich-tier (populated by downstream ack callback if provided):
    downstream_nonce_ack: Optional[str] = None
    downstream_output_snap: Optional[Any] = None


class EnforcementDecisionLogger:
    """JSONL append sink for EnforcementDecisions. Atomic tmp+rename per flush.

    Buffered in memory; flush() writes buffered rows to `out_path` atomically.
    Cell can call flush() at end of run; individual appends are cheap.
    """

    def __init__(self, out_path: str) -> None:
        self._out_path = out_path
        self._buf: List[dict] = []

    def append(self, decision: EnforcementDecision) -> None:
        import dataclasses as _dc
        self._buf.append(_dc.asdict(decision))

    def n_buffered(self) -> int:
        return len(self._buf)

    def flush(self) -> None:
        import json as _json
        if not self._buf:
            return
        os.makedirs(os.path.dirname(self._out_path) or ".", exist_ok=True)
        tmp = self._out_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for row in self._buf:
                f.write(_json.dumps(row, default=str) + "\n")
        os.replace(tmp, self._out_path)


# --------------------------- Downstream nonce ack ---------------------------


def read_and_ack_nonce(target: Dict[str, Any],
                       param_name: str) -> Tuple[Any, str]:
    """Downstream instrumentation contract: read value + last-written nonce.

    Returns (value, nonce). Nonce empty string if no nonce recorded (i.e.
    no enforce() ever wrote to this param). Consumer emits `nonce` alongside
    its output; the audit boundary compares the emitted nonce to the
    enforcement decision's `nonce_written` to prove mechanical read.
    """
    value = target.get(param_name)
    nonce = target.get(f"{param_name}__nonce", "")
    return value, nonce


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

    # ----------------------- Phase 2 enforcement ----------------------------

    def set_enforcement_mode(self, atom_id: str, mode: str) -> None:
        """Promote/demote a single atom's enforcement mode."""
        if mode not in VALID_ENFORCEMENT_MODES:
            raise ValueError(
                f"unknown enforcement_mode {mode!r}; "
                f"must be one of {sorted(VALID_ENFORCEMENT_MODES)}")
        for a in self._atoms:
            if a.atom_id == atom_id:
                a.enforcement_mode = mode
                return
        raise KeyError(f"atom_id {atom_id!r} not in consultant")

    def get_enforcement_mode(self, atom_id: str) -> str:
        for a in self._atoms:
            if a.atom_id == atom_id:
                return a.enforcement_mode
        raise KeyError(f"atom_id {atom_id!r} not in consultant")

    def enforce(self,
                operation_class: str,
                params: Optional[dict],
                target: Dict[str, Any],
                param_name: str,
                *,
                null_arm: bool = False,
                query_hint: Optional[str] = None,
                k: int = 3,
                logger: Optional[EnforcementDecisionLogger] = None
                ) -> ConsultationResult:
        """Phase 2 enforcement wrapper around consult().

        Args:
            operation_class: one of VALID_OP_CLASSES.
            params: op params (as in consult()).
            target: dict-like slot that the enforcement may mutate.
                target[param_name] = pre_value BEFORE the call; on WARN/LIVE
                mode of the matched atom, target[param_name] is overwritten
                to recommendation-derived post_value (or pre_value for
                null_arm=True) AND target[param_name + '__nonce'] is set to
                a fresh 16-byte hex nonce.
            param_name: key to mutate in target.
            null_arm: if True, post_value = pre_value (identity write) but
                nonce is still fresh; used for A/B distributional test.
            query_hint: optional query hint (as in consult()).
            k: top-k above floor (as in consult()).
            logger: optional EnforcementDecisionLogger; every call appended.

        Returns:
            ConsultationResult with Phase 2 fields populated:
              applied_flag: effective mode (SHADOW/WARN/LIVE)
              null_arm: passed through
              nonce_written: nonce (empty if no write)
              pre_value / post_value / param_name
              enforcement_wrote: True iff target actually mutated
        """
        # Step 1: consult() as in Phase 1 (advisory retrieval).
        result = self.consult(operation_class, params=params,
                              query_hint=query_hint, k=k)
        # Step 2: determine effective enforcement mode from matched top atom.
        top_match = result.matched_atoms[0] if result.matched_atoms else None
        if top_match is not None:
            atom_id = top_match.atom_id
            mode = self.get_enforcement_mode(atom_id)
        else:
            atom_id = None
            mode = "SHADOW"  # no match -> no write

        # Step 3: apply mode semantics.
        pre_value = target.get(param_name)
        nonce_written = ""
        post_value = pre_value
        enforcement_wrote = False
        if mode in {"WARN", "LIVE"} and top_match is not None:
            nonce_written = secrets.token_hex(16)
            if null_arm:
                # Identity write; fresh nonce (per drill section 3
                # Discriminator B: null-arm control).
                post_value = pre_value
            else:
                post_value = top_match.recommendation
            target[param_name] = post_value
            target[f"{param_name}__nonce"] = nonce_written
            enforcement_wrote = True
        # (SHADOW: no write; nonce empty; target untouched.)

        # Update the matched atom's nonce field (for downstream ack compare).
        if top_match is not None:
            top_match.nonce = nonce_written

        # Step 4: populate Phase 2 fields on the result.
        result.applied_flag = mode
        result.null_arm = null_arm
        result.nonce_written = nonce_written
        result.pre_value = pre_value
        result.post_value = post_value
        result.param_name = param_name
        result.enforcement_wrote = enforcement_wrote

        # Step 5: log decision if logger provided.
        if logger is not None:
            decision = EnforcementDecision(
                decision_id=secrets.token_hex(16),
                op_class=operation_class,
                atom_id=atom_id,
                recommendation=(top_match.recommendation
                                if top_match is not None else None),
                pre_value=pre_value,
                post_value=post_value,
                enforcement_mode=mode,
                nonce=nonce_written,
                wall_ms=result.wall_ms,
                ts_iso=datetime.now(timezone.utc).isoformat(),
                null_arm=null_arm,
                enforcement_wrote=enforcement_wrote,
            )
            logger.append(decision)
        return result


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


# ----------------------- Phase 2 selftests ----------------------------------


def _selftest_shadow_mode_no_write() -> None:
    """SHADOW (default): enforce() must NOT write to target."""
    ac = AtomConsultant()
    target = {"storage": "BUNDLED"}
    r = ac.enforce("COMPOSITION",
                   params={"storage": "BUNDLED", "N": 1024, "M": 6400},
                   target=target, param_name="storage")
    if r.applied_flag != "SHADOW":
        raise AssertionError(
            f"expected applied_flag=SHADOW; got {r.applied_flag!r}")
    if r.enforcement_wrote:
        raise AssertionError("SHADOW mode wrote to target (must not)")
    if target["storage"] != "BUNDLED":
        raise AssertionError(
            f"SHADOW mode mutated target: {target['storage']!r}")
    if "storage__nonce" in target:
        raise AssertionError("SHADOW mode wrote a nonce (must not)")


def _selftest_warn_mode_writes_value_and_nonce() -> None:
    """WARN mode: enforce() writes recommendation + fresh nonce to target."""
    ac = AtomConsultant()
    ac.set_enforcement_mode("STORAGE_STRATEGY_SHARDED_MASTER_MODERATOR_v1",
                            "WARN")
    target = {"storage": "BUNDLED"}
    r = ac.enforce("COMPOSITION",
                   params={"storage": "BUNDLED", "N": 1024, "M": 6400},
                   target=target, param_name="storage")
    if r.applied_flag != "WARN":
        raise AssertionError(
            f"expected applied_flag=WARN; got {r.applied_flag!r}")
    if not r.enforcement_wrote:
        raise AssertionError("WARN mode did not write to target")
    if target["storage"] != "SHARDED":
        raise AssertionError(
            f"WARN mode value wrong: {target['storage']!r} != 'SHARDED'")
    if len(target.get("storage__nonce", "")) != 32:  # 16 bytes hex = 32 chars
        raise AssertionError(
            f"WARN mode nonce wrong length: "
            f"{len(target.get('storage__nonce', ''))!r}")


def _selftest_null_arm_writes_identity_with_fresh_nonce() -> None:
    """Null-arm: post_value == pre_value BUT fresh nonce still written."""
    ac = AtomConsultant()
    ac.set_enforcement_mode("STORAGE_STRATEGY_SHARDED_MASTER_MODERATOR_v1",
                            "WARN")
    target = {"storage": "BUNDLED"}
    r = ac.enforce("COMPOSITION",
                   params={"storage": "BUNDLED", "N": 1024, "M": 6400},
                   target=target, param_name="storage", null_arm=True)
    if not r.null_arm:
        raise AssertionError("null_arm flag not propagated")
    if not r.enforcement_wrote:
        raise AssertionError("null-arm should still write (identity + nonce)")
    if target["storage"] != "BUNDLED":
        raise AssertionError(
            f"null-arm should be identity write: {target['storage']!r}")
    if len(target.get("storage__nonce", "")) != 32:
        raise AssertionError("null-arm did not write a fresh nonce")


def _selftest_nonce_uniqueness_across_calls() -> None:
    """Nonces must be fresh (16-byte crypto random)."""
    ac = AtomConsultant()
    ac.set_enforcement_mode("STORAGE_STRATEGY_SHARDED_MASTER_MODERATOR_v1",
                            "WARN")
    nonces = set()
    for _ in range(50):
        target = {"storage": "BUNDLED"}
        r = ac.enforce("COMPOSITION",
                       params={"storage": "BUNDLED", "N": 1024, "M": 6400},
                       target=target, param_name="storage")
        nonces.add(r.nonce_written)
    if len(nonces) != 50:
        raise AssertionError(
            f"nonce collision: {len(nonces)} unique out of 50 calls")


def _selftest_read_and_ack_nonce_roundtrip() -> None:
    """read_and_ack_nonce returns the value + nonce a downstream would ack."""
    ac = AtomConsultant()
    ac.set_enforcement_mode("STORAGE_STRATEGY_SHARDED_MASTER_MODERATOR_v1",
                            "WARN")
    target = {"storage": "BUNDLED"}
    r = ac.enforce("COMPOSITION",
                   params={"storage": "BUNDLED", "N": 1024, "M": 6400},
                   target=target, param_name="storage")
    value, nonce_ack = read_and_ack_nonce(target, "storage")
    if value != "SHARDED":
        raise AssertionError(f"read value != SHARDED: {value!r}")
    if nonce_ack != r.nonce_written:
        raise AssertionError(
            f"nonce ack mismatch: read={nonce_ack!r} write={r.nonce_written!r}")


def _selftest_enforcement_decision_logger_appends_and_flushes() -> None:
    """Logger buffers decisions and flushes to JSONL atomically."""
    import json as _json
    import tempfile
    ac = AtomConsultant()
    ac.set_enforcement_mode("STORAGE_STRATEGY_SHARDED_MASTER_MODERATOR_v1",
                            "WARN")
    with tempfile.TemporaryDirectory() as td:
        log_path = os.path.join(td, "decisions.jsonl")
        logger = EnforcementDecisionLogger(log_path)
        for i in range(5):
            target = {"storage": "BUNDLED"}
            ac.enforce("COMPOSITION",
                       params={"storage": "BUNDLED", "N": 1024, "M": 6400},
                       target=target, param_name="storage",
                       null_arm=(i % 2 == 0), logger=logger)
        if logger.n_buffered() != 5:
            raise AssertionError(
                f"logger buffered {logger.n_buffered()} != 5")
        logger.flush()
        rows = [_json.loads(x) for x in open(log_path).read().splitlines()]
        if len(rows) != 5:
            raise AssertionError(f"flushed rows != 5: {len(rows)}")
        # decision_id uniqueness
        ids = {r["decision_id"] for r in rows}
        if len(ids) != 5:
            raise AssertionError("decision_id collision in logger flush")


def _run_all_selftests() -> dict:
    _selftest_op_class_enum_rejects_unknown()
    _selftest_strict_subset_tag_filter()
    _selftest_sub_ms_wall_budget()
    _selftest_case1_storage_strategy_fires()
    _selftest_case2_bundled_bimodal_fires()
    _selftest_case4_framing_axis_aliasing_fires()
    _selftest_case5_verify_cross_term_fires()
    _selftest_applied_always_false_v1()
    # Phase 2 selftests (added 2026-07-04):
    _selftest_shadow_mode_no_write()
    _selftest_warn_mode_writes_value_and_nonce()
    _selftest_null_arm_writes_identity_with_fresh_nonce()
    _selftest_nonce_uniqueness_across_calls()
    _selftest_read_and_ack_nonce_roundtrip()
    _selftest_enforcement_decision_logger_appends_and_flushes()
    return {
        "primitive": "AtomConsultant",
        "phase": "PHASE_2_APPLY_WITH_NONCE_v1",
        "storage": "NO_STORAGE",
        "op_classes": sorted(VALID_OP_CLASSES),
        "enforcement_modes": sorted(VALID_ENFORCEMENT_MODES),
        "curated_atoms": AtomConsultant().n_atoms_total(),
        "wall_budget_ms": 5.0,
    }


if __name__ == "__main__":
    result = _run_all_selftests()
    print(f"[atom_consultation selftest] PASS {result}")
