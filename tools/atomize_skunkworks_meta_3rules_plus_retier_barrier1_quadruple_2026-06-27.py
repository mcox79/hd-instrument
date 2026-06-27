"""Atomize: 3 NEW META rules + RELABEL META_BARRIER_1_QUADRUPLE_NEGATIVE (2026-06-27).

Trigger: Research per-arm audit (Skunkworks request, USER pushback 2026-06-27).
Source note: notes/research_drill_brain_multihop_7mechanism_inventory_USER_PUSHBACK_2026-06-27.md

PER-ARM AUDIT FINDINGS (verify-off-data on existing metrics.json):
  - consolidation v3: NAIVE=0.85 OUT_OF_BAND (rail wanted 0.62-0.68); tested SHARED-W
    caricature (brain uses SEPARATE cortex W) -> not clean refutation of B1 schema-chunking
  - pointer-chain v1: BASELINE=0.395 OUT_OF_BAND -> cell wasn't in production regime;
    HRR-bind-in-SAME-W is NOT brain's PFC-scratchpad-with-separate-W (B2)
  - WM-scaffold v1: WM_2HOP=0.425 < BASELINE=0.65 (genuine harm) -> shared-W bug likely;
    code audit required before claiming PFC-scratchpad refuted
  - CSP-gated v1: BINARY abort at 41.5% != brain's graded confidence (B4/B8)
  - parallel-vote v2: K-scaling 0.40->0.50 from K=5->15 is REAL monotone lift;
    framed as "regime-artifact" via META_M6/M7 but WITHIN-cell mechanism IS present

NET: 0 of 5 are clean refutations of the BRAIN mechanism they were ostensibly testing.
The QUADRUPLE_NEGATIVE atom (2026-06-25) propagated verdict-msg framings into META
without per-arm verification (Fix #28 violation pattern, applied to a META atom).

ACTIONS:

  ACTION 1: RELABEL META_BARRIER_1_QUADRUPLE_NEGATIVE
    The atom remains in Store as historical evidence-trail (per discipline_meta convention
    of preserving prior reasoning), but a NEW relabel atom narrows its claim:
    - prior: '4 mechanism-independent refutations; 2-hop ceiling permanent-strengthened'
    - relabeled: '4 caricature-implementations refuted; brain-correct retests pending;
      atom MUST NOT be cited as evidence of substrate permanent 2-hop ceiling absent
      brain-mechanism-correct retests'
    Atomized as a NEW META atom (relabel_prior pattern); composes-with original;
    ledger cert_relabel op with supersedes pointing to QUADRUPLE atom row.

  ACTION 2: ATOMIZE 3 NEW META RULES (CERT-neutral; META corpus; T_methodology tier)
    [N1] META_RULE_T: META atomization MUST come from per-arm metric verification, NOT
         verdict-msg framings. Audit existing META atoms for the same pattern.
    [N2] META_RULE_U: Cell-authors MUST articulate the LOAD-BEARING architectural feature
         of the brain mechanism their cell tests (separate-W vs shared, graded vs binary,
         distributional vs point) AND demonstrate their implementation honors it. Cells
         that don't are testing a CARICATURE and cannot refute the brain mechanism.
    [N3] META_RULE_V: USER pushback on framing/limit claims triggers VERIFY-THE-REFERENT
         audit by default (read per-arm metrics; recompute discriminator; report findings)
         BEFORE defending the framing. Director propagation of verdict-msg into META is
         the failure pattern caught here.

CERT DELTA ANALYSIS:
  - All 4 atoms are CERT-neutral (META rules + relabel are discipline_meta; not CERT_CHAIN_GRADE)
  - cert_increment_delta = 0 for all 4 ledger rows
  - Live CERT N unchanged
  - The QUADRUPLE atom's prior_quality 'META_RULE_CERT_NEUTRAL' did NOT count toward CERT N
    in the first place (per ledger row cert_status='meta_rule' / delta=0)

LEDGER OPS:
  - 3 cert_ruling rows (op='cert_ruling') for N1/N2/N3 META rules
  - 1 cert_relabel row (op='cert_relabel', supersedes=<QUADRUPLE_atom_row_hash>) for ACTION 1

Run:
  .venv/Scripts/python.exe tools/atomize_skunkworks_meta_3rules_plus_retier_barrier1_quadruple_2026-06-27.py            # DRY
  .venv/Scripts/python.exe tools/atomize_skunkworks_meta_3rules_plus_retier_barrier1_quadruple_2026-06-27.py --apply    # WRITE
"""
from __future__ import annotations
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import append_cert_ledger_row


STORE_ROOT = Path("data/substrate_index")
RULING_NOTE = "notes/research_drill_brain_multihop_7mechanism_inventory_USER_PUSHBACK_2026-06-27.md"
CELL_COMMIT = "n/a-2026-06-27-meta-3rules-plus-retier"
ATOMIZED_BY = "skunkworks_meta_3rules_plus_retier_barrier1_quadruple_2026-06-27"

# Prior QUADRUPLE atom we are relabeling (full id; meta corpus; T3 tier).
PRIOR_QUADRUPLE_ATOM_QID = (
    "meta::T3/META_BARRIER_1_QUADRUPLE_NEGATIVE_csp_gated_extends_triple_substrate_native_"
    "multihop_4_for_4_REFUTED_2_hop_ceiling_permanent_strengthened"
)


# ============================================================================
# NEW ATOM 1 -- META_RULE_T: per-arm verification before META atomization
# ============================================================================

def build_atom_meta_rule_T() -> Atom:
    return Atom(
        id=(
            "T_methodology/META_RULE_T_per_arm_metric_verification_required_before_META_atomization_"
            "verdict_msg_framings_are_NOT_sufficient_Director_must_recompute_off_data_per_arm_for_"
            "each_constituent_cell_before_promoting_to_META_RULE_or_BARRIER_atom_Fix_28_applied_to_"
            "META_atoms_witness_BARRIER_1_QUADRUPLE_NEGATIVE_relabel_2026-06-27"
        ),
        name=(
            "META_RULE_T: per-arm metric verification REQUIRED before META atomization "
            "(verdict-msg framings NOT sufficient; Fix #28 applied to META atoms; "
            "BARRIER_1_QUADRUPLE_NEGATIVE relabel witness 2026-06-27)"
        ),
        description=(
            "META RULE T (CERT-neutral; discipline_meta):\n\n"
            "META atomization (META_RULE, META_BARRIER, META_RECONCILIATION) MUST be grounded "
            "in per-arm metric verification of EACH constituent cell, NOT in verdict-msg "
            "framings or summary text from the originating ruling notes.\n\n"
            "FAILURE PATTERN CAUGHT (2026-06-27 audit of META_BARRIER_1_QUADRUPLE_NEGATIVE):\n"
            "  The QUADRUPLE atom (2026-06-25) claimed 4 mechanism-independent refutations "
            "of substrate-native multi-hop. Per-arm audit triggered by USER pushback shows "
            "0 of 5 constituent cells are clean refutations of the BRAIN mechanism they were "
            "ostensibly testing:\n"
            "  - consolidation v3 NAIVE=0.85 OUT_OF_BAND (rail wanted [0.62, 0.68])\n"
            "  - pointer-chain v1 BASELINE=0.395 OUT_OF_BAND\n"
            "  - WM-scaffold v1 WM_2HOP=0.425 < BASELINE=0.65 (genuine harm; code audit needed)\n"
            "  - CSP-gated v1 BINARY abort 41.5% != brain's graded confidence\n"
            "  - parallel-vote v2 K=5->15 lift 0.40->0.50 monotone (framed as regime-artifact)\n\n"
            "All four cells were tier-ruled HARD_FAIL on metric-band reasoning alone; the "
            "META atom was authored without checking whether each cell tested the brain "
            "mechanism it claimed to refute. This is Fix #28 (verify per-arm metrics not "
            "summary verdict text) applied at the META layer.\n\n"
            "ENFORCEMENT:\n"
            "  (a) Before authoring any META atom that AGGREGATES across N constituent cells, "
            "Skunkworks (or whoever atomizes) MUST run a per-arm off-data recompute for each "
            "constituent and log the per-arm finding in the META atom's description.\n"
            "  (b) Audit existing META atoms (especially BARRIER and RECONCILIATION atoms) "
            "for the same pattern; relabel any that propagated verdict-msg without per-arm.\n"
            "  (c) Director (or any non-auditor) is FORBIDDEN from authoring META atoms; "
            "only cert-owner (Skunkworks) may, and only after explicit per-arm recompute.\n\n"
            "COMPOSES-WITH: Fix #28, META_RULE_K (smoke must FIRE discriminator), "
            "META_RULE_USER_PUSHBACK_TRIGGERS_VERIFY_THE_REFERENT (N3 in this batch).\n\n"
            "WITNESS: ledger relabel of META_BARRIER_1_QUADRUPLE_NEGATIVE 2026-06-27 (this batch).\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        corpus=Corpus.META,
        tier=Tier.TIER_METHODOLOGY,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "cert_status": "meta_rule",
            "cert_class": "discipline_meta",
            "rule_id": "META_RULE_T",
            "rule_tags": ["META_RULE", "PER_ARM_METRIC_VERIFICATION_REQUIRED", "FIX_28_AT_META_LAYER"],
            "rule_class": "META_atomization_discipline",
            "applies_to": "any META_RULE / META_BARRIER / META_RECONCILIATION authorship",
            "rule_text": (
                "META atomization MUST be grounded in per-arm metric verification of each "
                "constituent cell; verdict-msg framings or summary text are NOT sufficient. "
                "Director is forbidden from authoring META atoms; only cert-owner after "
                "explicit per-arm off-data recompute. Audit existing META atoms for the "
                "same pattern; relabel any that propagated verdict-msg without per-arm."
            ),
            "atomized_by": ATOMIZED_BY,
            "ratified_by": "skunkworks",
            "ratified_at_ts": time.time(),
            "ratified_at_date": "2026-06-27",
            "discovered_from_witness": "META_BARRIER_1_QUADRUPLE_NEGATIVE_relabel_2026-06-27",
            "discovered_from_note": RULING_NOTE,
            "skunkworks_schema_vet_action": (
                "any pre-reg or note proposing a new META_BARRIER / META_RECONCILIATION / "
                "META_RULE_aggregator must list constituent atoms + per-arm recompute table "
                "before Skunkworks atomizes; default-reject if missing"
            ),
            "verified_off_data": True,
            "referent_note": RULING_NOTE,
        },
    )


# ============================================================================
# NEW ATOM 2 -- META_RULE_U: brain-mechanism vs caricature discipline
# ============================================================================

def build_atom_meta_rule_U() -> Atom:
    return Atom(
        id=(
            "T_methodology/META_RULE_U_brain_mechanism_vs_caricature_discipline_cell_authors_"
            "must_articulate_load_bearing_architectural_feature_separate_W_vs_shared_graded_vs_"
            "binary_distributional_vs_point_AND_implementation_honors_it_otherwise_testing_"
            "caricature_cannot_refute_brain_mechanism_BARRIER_1_quadruple_5_caricature_witness"
        ),
        name=(
            "META_RULE_U: brain-mechanism vs CARICATURE discipline (cell-authors MUST "
            "articulate load-bearing architectural feature + demonstrate implementation "
            "honors it; otherwise testing a caricature cannot refute the brain mechanism)"
        ),
        description=(
            "META RULE U (CERT-neutral; discipline_meta):\n\n"
            "When a cell claims to test a BRAIN MECHANISM (e.g. schema-chunking, "
            "PFC-scratchpad, reverse-replay, belief-propagation, rate-coded-soft-completion), "
            "the cell-author MUST explicitly answer:\n"
            "  (Q1) What is the LOAD-BEARING ARCHITECTURAL FEATURE of the brain mechanism?\n"
            "       Examples: separate-W (cortex vs hippocampus); graded confidence vs binary "
            "       abort; distributional message vs point estimate; dedicated WM bank vs "
            "       same-W with tagging; replay-as-operator-gated-by-importance vs replay-as-signal.\n"
            "  (Q2) Does my implementation honor that feature, or does it implement a "
            "       structurally-different caricature?\n"
            "  (Q3) If a caricature, can I cite the brain-correct architecture for a future "
            "       proper retest?\n\n"
            "Cells that fail to answer Q1-Q3 in the pre-reg can be tier-ruled HARD_FAIL on "
            "the IMPLEMENTATION but CANNOT be cited as evidence the BRAIN MECHANISM is "
            "refuted. They are CARICATURE-REFUTATIONS, not mechanism refutations.\n\n"
            "WITNESS (2026-06-27 audit, 5 cells all caricature-implementations):\n"
            "  - consolidation v1/v2/v3: tested SHARED-W consolidation; brain mechanism (B1 "
            "    schema-chunking, McClelland-McNaughton-O'Reilly 1995) uses SEPARATE cortex W.\n"
            "  - pointer-chain v1/v2: HRR-bind intermediates in SAME W as content; brain "
            "    mechanism (B2 PFC-scratchpad, Miller-Cohen 2001) uses SEPARATE PERSISTENT "
            "    ACTIVITY in distinct neural populations.\n"
            "  - WM-scaffold v1: likely permutation-tagged in main W (code audit pending); "
            "    brain B2 requires DEDICATED bank with clean read/write.\n"
            "  - CSP-gated v1: BINARY abort at 41.5%; brain (B4 belief-propagation Lee-Mumford "
            "    2003, B8 rate-coded Renart-Brunel 2007) uses GRADED CONFIDENCE distribution.\n"
            "  - parallel-vote v2: hard-majority vote; brain (B4/B8) uses SOFT MESSAGE PASSING "
            "    preserving full distribution.\n\n"
            "CONTRAST: a substrate cell CAN legitimately diverge from brain in implementation "
            "while honoring the load-bearing feature (e.g. TWO_TIER VSA primitive vs literal "
            "cortex/hippocampus). The discipline isn't 'match the brain bit-for-bit'; it's "
            "'name the load-bearing feature and honor it'. Caricatures DROP the feature.\n\n"
            "ENFORCEMENT (Skunkworks SCHEMA-VET):\n"
            "  Pre-regs that claim brain-mechanism testing MUST include a 'brain_mechanism_"
            "load_bearing_feature' field + 'implementation_honors_feature' boolean + (if not) "
            "'caricature_disclaimer' field. SCHEMA-VET rejects pre-regs missing these or "
            "marking implementation_honors=False without caricature disclaimer.\n\n"
            "COMPOSES-WITH: META_RULE_T (per-arm verification), META_RULE_U_witness_relabel "
            "(this batch ACTION 1: BARRIER_1 QUADRUPLE relabeled because 5 cells all "
            "implementations were caricatures), USER brain-existence-proof prior (P+0.10 for "
            "brain-grounded mechanisms; the prior assumes implementation honors the brain "
            "feature, not just borrows the name).\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        corpus=Corpus.META,
        tier=Tier.TIER_METHODOLOGY,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "cert_status": "meta_rule",
            "cert_class": "discipline_meta",
            "rule_id": "META_RULE_U",
            "rule_tags": [
                "META_RULE",
                "BRAIN_MECHANISM_VS_CARICATURE",
                "PRE_REG_LOAD_BEARING_FEATURE_FIELD_REQUIRED",
            ],
            "rule_class": "pre_reg_brain_mechanism_fidelity_check",
            "applies_to": "any cell claiming to test a brain-mechanism",
            "rule_text": (
                "Cells claiming to test brain mechanisms must articulate (Q1) the load-bearing "
                "architectural feature, (Q2) whether implementation honors it, (Q3) if caricature, "
                "the brain-correct architecture for retest. Caricature-refutations are NOT "
                "mechanism refutations. Pre-regs must include brain_mechanism_load_bearing_feature "
                "field + implementation_honors_feature boolean + (if False) caricature_disclaimer."
            ),
            "atomized_by": ATOMIZED_BY,
            "ratified_by": "skunkworks",
            "ratified_at_ts": time.time(),
            "ratified_at_date": "2026-06-27",
            "discovered_from_note": RULING_NOTE,
            "load_bearing_feature_examples": [
                "separate_W (cortex_vs_hippocampus)",
                "graded_confidence_vs_binary_abort",
                "distributional_message_vs_point_estimate",
                "dedicated_WM_bank_vs_same_W_with_tagging",
                "replay_as_operator_gated_by_importance_vs_replay_as_signal",
            ],
            "witness_cells_all_caricature": [
                "consolidation_v1_v2_v3 (shared-W not separate cortex W)",
                "pointer-chain v1/v2 (HRR-bind in same W not separate persistent activity)",
                "WM-scaffold v1 (likely shared-W tagging not dedicated bank)",
                "CSP-gated v1 (binary abort not graded confidence)",
                "parallel-vote v2 (hard majority not soft message passing)",
            ],
            "skunkworks_schema_vet_action": (
                "reject pre-reg missing brain_mechanism_load_bearing_feature field OR "
                "marking implementation_honors_feature=False without caricature_disclaimer"
            ),
            "verified_off_data": True,
            "referent_note": RULING_NOTE,
        },
    )


# ============================================================================
# NEW ATOM 3 -- META_RULE_V: USER pushback triggers verify-the-referent audit
# ============================================================================

def build_atom_meta_rule_V() -> Atom:
    return Atom(
        id=(
            "T_methodology/META_RULE_V_USER_pushback_on_framing_or_limit_claim_triggers_verify_"
            "the_referent_audit_by_default_Director_must_recompute_per_arm_metrics_BEFORE_defending_"
            "framing_not_after_BARRIER_1_quadruple_relabel_witness_2026-06-27_research_drill_brain_"
            "multihop_7mechanism_inventory_USER_PUSHBACK"
        ),
        name=(
            "META_RULE_V: USER pushback on framing/limit claim triggers VERIFY-THE-REFERENT "
            "audit by DEFAULT (recompute per-arm metrics BEFORE defending framing, not after; "
            "BARRIER_1 QUADRUPLE relabel witness 2026-06-27)"
        ),
        description=(
            "META RULE V (CERT-neutral; discipline_meta):\n\n"
            "When USER pushes back on a Director (or any role) framing of a limit / barrier / "
            "negative claim, the DEFAULT response is a verify-the-referent audit:\n"
            "  (Step 1) Identify the load-bearing claims in the framing being pushed back on.\n"
            "  (Step 2) For each load-bearing claim, locate the constituent cells / metrics.\n"
            "  (Step 3) Per-arm off-data recompute; surface any out-of-band baselines, "
            "           caricature-implementations, by-construction-saturation, or band-floor results.\n"
            "  (Step 4) Report findings BEFORE defending the framing.\n"
            "  (Step 5) If audit confirms the framing, re-state with evidence; if audit refutes, "
            "           relabel/retract the framing and the META atoms that depend on it.\n\n"
            "FAILURE PATTERN CAUGHT (2026-06-27):\n"
            "  USER pushed back on the META_BARRIER_1_QUADRUPLE_NEGATIVE framing: 'i do not "
            "  accept those limitations. how does the brain do it'. Default response would "
            "  have been to defend the framing ('the quadruple negative shows...'). Correct "
            "  response was to audit per-arm: revealed 0/5 cells tested the brain mechanism "
            "  they claimed to refute (all 5 were CARICATURE implementations per META_RULE_U).\n\n"
            "USER PUSHBACK IS A SIGNAL not a complaint. USER often has correct intuition the "
            "framing missed something (Fix #28 recurring pattern: Skunkworks correctly overrides "
            "Director on by-construction-saturation; USER correctly overrides Director on "
            "verdict-msg framings).\n\n"
            "ENFORCEMENT:\n"
            "  (a) Director MUST run verify-the-referent audit before responding to USER "
            "      pushback on framing/limit/barrier/negative claims. No defending without "
            "      audit data.\n"
            "  (b) Audit must include per-arm metrics + brain-mechanism-fidelity check (per "
            "      META_RULE_U) + band-calibration check (per USER_BIAS_S).\n"
            "  (c) If audit refutes the framing, relabel/retract; Skunkworks atomizes the "
            "      relabel atom + ledger relabel op with supersedes pointing to prior atom.\n"
            "  (d) Director responses framing pushback without audit = procedural violation; "
            "      flag in next testbed fleet-health audit.\n\n"
            "COMPOSES-WITH:\n"
            "  - META_RULE_T (per-arm verification before META atomization): same root pattern, "
            "    different trigger (USER pushback vs new atomization)\n"
            "  - META_RULE_U (brain-mechanism vs caricature): the audit-step that often surfaces "
            "    USER's intuition\n"
            "  - Fix #28 (verify per-arm not verdict_msg)\n"
            "  - 'verify-OFF-DATA not reports' (Skunkworks discipline)\n"
            "  - 'verify-the-referent' (atom-id/mechanism/metric/regime all match the claim)\n\n"
            "WITNESS: this batch (ACTION 1) relabels META_BARRIER_1_QUADRUPLE_NEGATIVE; "
            "Skunkworks atomization triggered by USER pushback per Research drill 2026-06-27.\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        corpus=Corpus.META,
        tier=Tier.TIER_METHODOLOGY,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "cert_status": "meta_rule",
            "cert_class": "discipline_meta",
            "rule_id": "META_RULE_V",
            "rule_tags": [
                "META_RULE",
                "USER_PUSHBACK_TRIGGERS_VERIFY_THE_REFERENT",
                "DIRECTOR_NO_DEFEND_WITHOUT_AUDIT",
            ],
            "rule_class": "director_default_response_to_USER_pushback",
            "applies_to": "any USER pushback on framing/limit/barrier/negative-claim",
            "rule_text": (
                "USER pushback on framing/limit/barrier/negative claim triggers verify-the-"
                "referent audit by DEFAULT before any defending response. Audit per-arm metrics "
                "+ brain-mechanism-fidelity + band-calibration. If audit refutes framing, "
                "Skunkworks atomizes relabel + ledger relabel op. Director responses without "
                "audit = procedural violation."
            ),
            "atomized_by": ATOMIZED_BY,
            "ratified_by": "skunkworks",
            "ratified_at_ts": time.time(),
            "ratified_at_date": "2026-06-27",
            "discovered_from_note": RULING_NOTE,
            "witness_user_pushback": (
                "USER 2026-06-27: 'i do not accept those limitations. how does the brain do it' "
                "-- pushback on META_BARRIER_1_QUADRUPLE_NEGATIVE framing"
            ),
            "audit_outcome": (
                "0 of 5 constituent cells are clean refutations of the brain mechanism they "
                "ostensibly tested; all 5 are caricature-implementations per META_RULE_U; "
                "QUADRUPLE atom relabeled in this batch ACTION 1"
            ),
            "composes_with_disciplines": [
                "Fix_28_verify_per_arm_metrics_not_verdict_msg",
                "verify_OFF_DATA_not_reports",
                "verify_the_referent",
                "META_RULE_T_per_arm_required_before_META_atomization",
                "META_RULE_U_brain_mechanism_vs_caricature",
            ],
            "verified_off_data": True,
            "referent_note": RULING_NOTE,
        },
    )


# ============================================================================
# RELABEL ATOM -- ACTION 1: narrow META_BARRIER_1_QUADRUPLE_NEGATIVE scope
# ============================================================================

def build_atom_barrier1_quadruple_relabel() -> Atom:
    return Atom(
        id=(
            "T3/META_BARRIER_1_QUADRUPLE_NEGATIVE_RELABEL_2026-06-27_per_arm_audit_0_of_5_clean_"
            "refutations_all_caricature_implementations_atom_NOT_citable_as_evidence_of_substrate_"
            "permanent_2_hop_ceiling_absent_brain_mechanism_correct_retests_R1_R5_in_drill"
        ),
        name=(
            "META_BARRIER_1_QUADRUPLE_NEGATIVE RELABEL (2026-06-27): per-arm audit shows "
            "0 of 5 constituent cells are clean refutations of the BRAIN MECHANISM they "
            "ostensibly tested; all 5 are CARICATURE-IMPLEMENTATIONS per META_RULE_U; prior "
            "atom NOT citable as evidence of substrate permanent 2-hop ceiling absent "
            "brain-mechanism-correct retests (R1-R5 in research drill 2026-06-27)"
        ),
        description=(
            "RELABEL of meta::T3/META_BARRIER_1_QUADRUPLE_NEGATIVE (atomized 2026-06-25). "
            "Triggered by USER pushback 2026-06-27 + Research per-arm audit drill (note "
            "research_drill_brain_multihop_7mechanism_inventory_USER_PUSHBACK_2026-06-27.md).\n\n"
            "PRIOR ATOM CLAIM:\n"
            "  '4 mechanism-independent refutations of substrate-native multi-hop; per-hop "
            "  cleanup fidelity bounded by geometric chain decay; 2-hop ceiling substrate-"
            "  product permanent-strengthened at random-bipolar isotropic regime'\n\n"
            "AUDIT FINDING (per-arm off-data, 2026-06-27):\n"
            "  Constituent cell 1 -- consolidation v3:\n"
            "    NAIVE=0.85 OUT_OF_BAND (sanity rail wanted 0.62-0.68); K_THRESH gating did "
            "    not differentiate (train spread=0.006 < 0.10). Tested SHARED-W caricature; "
            "    brain mechanism (B1 schema-chunking, McClelland 1995) uses SEPARATE cortex W. "
            "    NOT a clean refutation of B1.\n"
            "  Constituent cell 2 -- pointer-chain v2:\n"
            "    BASELINE=0.395 OUT_OF_BAND. Pointer-chain HRR-bound intermediates in SAME W; "
            "    brain (B2 PFC-scratchpad, Miller-Cohen 2001) uses SEPARATE PERSISTENT ACTIVITY. "
            "    Cell wasn't in production regime AND tested caricature. NOT a clean refutation of B2.\n"
            "  Constituent cell 3 -- WM-scaffold v1:\n"
            "    BASELINE=0.65 (1/3 seed in band); WM_2HOP=0.425 < BASELINE (genuine harm). "
            "    Underperformance suggests shared-W crosstalk (code audit pending). NOT a "
            "    clean refutation of B2 PFC-scratchpad-with-separate-W; tested likely-shared-W bug.\n"
            "  Constituent cell 4 -- CSP-gated v1:\n"
            "    BASELINE=0.65 (1/3 in band); CSP_5HOP=0.030 with 41.5% refuse rate. Tested "
            "    BINARY abort gate; brain mechanism (B4 belief-propagation Lee-Mumford 2003, "
            "    B8 rate-coded Renart-Brunel 2007) uses GRADED CONFIDENCE distribution. NOT a "
            "    clean refutation of brain confidence-weighted output.\n"
            "  Constituent cell 5 -- parallel-vote v2:\n"
            "    BASELINE=0.645 (in band) but REPRODUCE_POINTER_CHAIN_V2=0.450 (META_M6 breach). "
            "    Within-cell K=5->15 lift 0.40->0.50 is REAL monotone (was framed as regime-"
            "    artifact). Tested HARD MAJORITY vote; brain (B4/B8) uses SOFT MESSAGE PASSING.\n\n"
            "NET FINDING: 0 of 5 constituent cells are clean refutations of any brain mechanism. "
            "All 5 are CARICATURE-IMPLEMENTATIONS per META_RULE_U (this batch). The QUADRUPLE "
            "atom's claim '4 mechanism-independent refutations' is reframed as '4 CARICATURE-"
            "implementation HARD_FAILs that do NOT bear on brain-mechanism-correct retests'.\n\n"
            "POST-RELABEL STATUS OF PRIOR ATOM:\n"
            "  - Atom REMAINS in Store as evidence trail (per discipline_meta convention)\n"
            "  - Atom MUST NOT be cited as evidence of 'substrate permanent 2-hop ceiling' "
            "    in future framings, pre-regs, or master plans\n"
            "  - Cells citing this atom in their pre-reg pre-flight check (Fix #26) must "
            "    handle the relabel: refuse-dispatch only applies to caricature-class "
            "    revivals, NOT brain-mechanism-correct retests (R1-R5 in research drill)\n"
            "  - Skunkworks SCHEMA-VET: any pre-reg invoking BARRIER_1 ceiling MUST declare "
            "    brain-mechanism load-bearing feature (per META_RULE_U) AND demonstrate the "
            "    cell HONORS it; default-accept brain-correct retests; default-refuse caricature retries\n\n"
            "COMPOSES-WITH:\n"
            "  - prior atom meta::T3/META_BARRIER_1_QUADRUPLE_NEGATIVE (relabel target; remains in Store)\n"
            "  - prior atom meta::T3/META_BARRIER_1_QUINTUPLE_RECONCILIATION_substrate_5hop_partition_per_hop_"
            "    routed_chain_grade (2026-06-26 narrowed-not-broke; this relabel further narrows by "
            "    introducing the caricature-vs-brain-mechanism distinction the QUINTUPLE atom did not address)\n"
            "  - new META_RULE_T (per-arm verification required before META atomization)\n"
            "  - new META_RULE_U (brain-mechanism vs caricature discipline)\n"
            "  - new META_RULE_V (USER pushback triggers verify-the-referent audit)\n\n"
            "RESEARCH DRILL FOLLOW-UP CELLS (R1-R5 + N1-N2 per inventory note 2026-06-27):\n"
            "  R1 NREM-REPLAY-AS-OPERATOR-INTO-SEPARATE-W_C (brain-correct B1+B5+B7 composition)\n"
            "  R2 PFC-SCRATCHPAD-SEPARATE-W (brain-correct B2)\n"
            "  R3 BIDIRECTIONAL-MEET-IN-MIDDLE (brain-correct B3)\n"
            "  R4 RECURRENT-ATTRACTOR-PER-HOP (brain-correct B8)\n"
            "  R5 GRADED-CONFIDENCE-OUTPUT (brain-correct B4/B8 replacing CSP binary abort)\n"
            "  N1 SCHEMA-EXTRACTED-WITHOUT-STORAGE-POLLUTION (brain-correct B1)\n"
            "  N2 RATE-CODED-SOFT-COMPLETION (brain-correct B8 missing from prior inventory)\n"
            "  These cells should be dispatched per Research roadmap before BARRIER_1 can be\n"
            "  re-evaluated. Until then, BARRIER_1 ceiling is OPEN at this regime.\n\n"
            "CERT DELTA: 0 (relabel of a CERT-neutral META atom; ledger op=cert_relabel; "
            "supersedes points to prior QUADRUPLE atom row; live CERT N unchanged).\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        corpus=Corpus.META,
        tier=Tier.TIER_3_ALGORITHM,  # same tier as relabel target for partition alignment
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "cert_status": "meta_rule",
            "cert_class": "discipline_meta",
            "rule_id": "META_BARRIER_1_QUADRUPLE_NEGATIVE_RELABEL",
            "rule_tags": [
                "META_RELABEL",
                "BARRIER_1_NARROWED_FURTHER",
                "CARICATURE_IMPLEMENTATIONS_NOT_MECHANISM_REFUTATIONS",
            ],
            "rule_class": "barrier_relabel",
            "applies_to": "any cell or framing citing META_BARRIER_1_QUADRUPLE_NEGATIVE",
            "relabel_target_atom_qid": PRIOR_QUADRUPLE_ATOM_QID,
            "relabel_target_rule_id": "BARRIER_1_QUADRUPLE_NEGATIVE",
            "prior_claim": (
                "4 mechanism-independent refutations of substrate-native multi-hop; 2-hop "
                "ceiling permanent-strengthened at random-bipolar isotropic regime"
            ),
            "post_relabel_claim": (
                "4 CARICATURE-implementation HARD_FAILs; per-arm audit shows 0 of 5 cells "
                "tested the brain mechanism they ostensibly refuted; atom NOT citable as "
                "evidence of substrate permanent 2-hop ceiling absent brain-mechanism-correct "
                "retests (R1-R5 + N1-N2 per Research drill 2026-06-27)"
            ),
            "per_arm_audit_summary": {
                "consolidation_v3": "NAIVE=0.85 OUT_OF_BAND; tested SHARED-W caricature (brain=SEPARATE W)",
                "pointer_chain_v2": "BASELINE=0.395 OUT_OF_BAND; HRR-bind in same W (brain=separate persistent activity)",
                "wm_scaffold_v1": "WM_2HOP=0.425 < BASELINE=0.65 (genuine harm); likely shared-W bug",
                "csp_gated_v1": "BINARY abort 41.5% != brain graded confidence (B4/B8)",
                "parallel_vote_v2": "K=5->15 lift 0.40->0.50 REAL monotone; hard-majority vote != soft message passing",
            },
            "n_clean_brain_mechanism_refutations": 0,
            "n_caricature_implementations": 5,
            "composes_with": [
                PRIOR_QUADRUPLE_ATOM_QID,
                "meta::T3/META_BARRIER_1_QUINTUPLE_RECONCILIATION_substrate_5hop_partition_per_hop_routed_chain_grade_at_0p955_cv_0p007_meta_M7_pass_narrows_quadruple_negative_to_routing_required_5hop",
            ],
            "follow_up_cells_brain_correct": [
                "R1_NREM_REPLAY_AS_OPERATOR_INTO_SEPARATE_W_C",
                "R2_PFC_SCRATCHPAD_SEPARATE_W",
                "R3_BIDIRECTIONAL_MEET_IN_MIDDLE",
                "R4_RECURRENT_ATTRACTOR_PER_HOP",
                "R5_GRADED_CONFIDENCE_OUTPUT",
                "N1_SCHEMA_EXTRACTED_WITHOUT_STORAGE_POLLUTION",
                "N2_RATE_CODED_SOFT_COMPLETION",
            ],
            "skunkworks_schema_vet_action": (
                "any pre-reg invoking BARRIER_1 ceiling MUST declare brain-mechanism "
                "load-bearing feature (per META_RULE_U) + demonstrate cell honors it; "
                "default-accept brain-correct retests; default-refuse caricature retries"
            ),
            "atomized_by": ATOMIZED_BY,
            "ratified_by": "skunkworks",
            "ratified_at_ts": time.time(),
            "ratified_at_date": "2026-06-27",
            "verified_off_data": True,
            "referent_note": RULING_NOTE,
            "user_pushback_trigger": (
                "USER 2026-06-27: 'i do not accept those limitations. how does the brain do it'"
            ),
        },
    )


# ============================================================================
# SAFE WRITER HELPER
# ============================================================================

def safe_add_with_ledger(
    atom: Atom,
    *,
    source: str,
    note: str,
    ledger_row: dict,
    expected_cert_n_after: int,
) -> tuple[bool, str | None]:
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"  SKIP (idempotent): {atom.id[:120]} already present.")
    else:
        print(f"  ADDING atom: {atom.id[:120]}...")
        ps.add_atom(atom, source=source, note=note)
        ps2 = PartitionedStore(STORE_ROOT)
        found = ps2.get_atom(qid)
        if found is None:
            print(f"  FAIL: atom not found post-add")
            return (False, None)
        md = found.metadata or {}
        expected_pq = (atom.metadata or {}).get("provenance_quality")
        if md.get("provenance_quality") != expected_pq:
            print(
                f"  FAIL: pq mismatch (expected {expected_pq}, got {md.get('provenance_quality')})"
            )
            return (False, None)
        print(f"  PASS: round-trip survival OK (pq={md.get('provenance_quality')})")

    ps_check = PartitionedStore(STORE_ROOT)
    live_n = sum(
        1 for a in ps_check.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    if live_n != expected_cert_n_after:
        print(f"  FAIL: live CERT N {live_n} != expected_cert_n_after {expected_cert_n_after}")
        return (False, None)

    print(
        f"  appending cert-ledger row "
        f"(op={ledger_row.get('op')} status={ledger_row.get('cert_status')} "
        f"delta={ledger_row.get('cert_increment_delta')})"
    )
    try:
        row_h = append_cert_ledger_row(
            ledger_row,
            expected_cert_n_pre=expected_cert_n_after,
            expected_cert_n_post=expected_cert_n_after,
        )
        print(f"  ledger row appended; row_hash = {row_h}")
        return (True, row_h)
    except Exception as e:
        print(f"  FAIL: cert-ledger append errored: {e}")
        return (False, None)


def build_meta_rule_ruling_row(*, atom_qid, verdict, note):
    return {
        "ts": None,
        "op": "cert_ruling",
        "atom_id": atom_qid,
        "cert_status": "custom",
        "cert_class": "discipline_meta",
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "cell_commit": CELL_COMMIT,
        "verdict": verdict,
        "cert_increment_delta": 0,
        "cv": None,
        "referent_pointer": {
            "notes_path": RULING_NOTE,
            "metrics_path": None,
            "atom_qualified_id": atom_qid,
        },
        "supersedes": None,
        "note": note,
    }


def build_relabel_row(*, relabel_atom_qid, prior_atom_qid, verdict, note):
    return {
        "ts": None,
        "op": "cert_relabel",
        "atom_id": relabel_atom_qid,
        "cert_status": "custom",
        "cert_class": "discipline_meta",
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "cell_commit": CELL_COMMIT,
        "verdict": verdict,
        "cert_increment_delta": 0,
        "cv": None,
        "referent_pointer": {
            "notes_path": RULING_NOTE,
            "metrics_path": None,
            "atom_qualified_id": prior_atom_qid,
        },
        "supersedes": prior_atom_qid,
        "note": note,
    }


# ============================================================================
# MAIN
# ============================================================================

def main() -> int:
    apply = "--apply" in sys.argv

    atom_T = build_atom_meta_rule_T()
    atom_U = build_atom_meta_rule_U()
    atom_V = build_atom_meta_rule_V()
    atom_relabel = build_atom_barrier1_quadruple_relabel()

    print("=" * 72)
    print("META atomization plan (3 NEW META rules + 1 RELABEL) -- 2026-06-27")
    print("=" * 72)
    for i, a in enumerate([atom_T, atom_U, atom_V, atom_relabel], 1):
        rule_id = (a.metadata or {}).get("rule_id", "?")
        print(f"  [{i}] {rule_id}")
        print(f"       qid={a.corpus.value}::{a.id[:90]}...")
        print(
            f"       pq={a.metadata.get('provenance_quality')} "
            f"status={a.metadata.get('cert_status')} delta=0"
        )
    print()
    print("  Net CERT N change: 0 (all 4 atoms CERT-neutral META)")
    print("  Net ledger rows: +4 (3 cert_ruling + 1 cert_relabel)")
    print(f"  RELABEL TARGET: {PRIOR_QUADRUPLE_ATOM_QID[:90]}...")

    if not apply:
        print()
        print("DRY: pass --apply to mutate Store + ledger.")
        return 0

    print()
    print("=" * 72)
    print("A5 PRE snapshot")
    print("=" * 72)
    ps_pre = PartitionedStore(STORE_ROOT)
    cert_pre = sum(
        1 for a in ps_pre.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    print(f"A5-PRE: live CERT N = {cert_pre}")

    # Verify prior QUADRUPLE atom exists (relabel target must exist)
    prior_atom = ps_pre.get_atom(PRIOR_QUADRUPLE_ATOM_QID)
    if prior_atom is None:
        print(f"ABORT: relabel target atom not found in Store: {PRIOR_QUADRUPLE_ATOM_QID}")
        return 1
    print(f"  PRIOR QUADRUPLE atom present (will be relabeled, not deleted)")

    # All 4 windows have delta=0 -> expected_cert_n_after = cert_pre throughout
    expected_after = cert_pre

    rows = []
    for atom, role, verdict_text, note_text in [
        (
            atom_T,
            "META_RULE_T",
            "META_RULE_CERT_NEUTRAL_T_per_arm_metric_verification_required_before_META_atomization_skunkworks",
            "meta_rule_T_per_arm_metric_verification_required_before_META_atomization_witness_BARRIER_1_QUADRUPLE_relabel_2026-06-27",
        ),
        (
            atom_U,
            "META_RULE_U",
            "META_RULE_CERT_NEUTRAL_U_brain_mechanism_vs_caricature_discipline_skunkworks",
            "meta_rule_U_brain_mechanism_vs_caricature_discipline_5_caricature_witness_cells_2026-06-27",
        ),
        (
            atom_V,
            "META_RULE_V",
            "META_RULE_CERT_NEUTRAL_V_USER_pushback_triggers_verify_the_referent_audit_skunkworks",
            "meta_rule_V_USER_pushback_triggers_verify_the_referent_audit_witness_2026-06-27",
        ),
    ]:
        print()
        print("=" * 72)
        print(f"Window {role} (delta=0)")
        print("=" * 72)
        qid = f"{atom.corpus.value}::{atom.id}"
        row = build_meta_rule_ruling_row(
            atom_qid=qid,
            verdict=verdict_text,
            note=note_text,
        )
        ok, h = safe_add_with_ledger(
            atom,
            source=ATOMIZED_BY,
            note=f"{role}: cert-neutral META rule atomized 2026-06-27.",
            ledger_row=row,
            expected_cert_n_after=expected_after,
        )
        if not ok:
            print(f"ABORT: {role} window failed; halting.")
            return 1
        rows.append((role, h))
        print(f"  Live CERT N now {expected_after}; row_hash {h}")

    # Window 4: RELABEL atom + cert_relabel ledger op
    print()
    print("=" * 72)
    print("Window RELABEL (BARRIER_1 QUADRUPLE_NEGATIVE; delta=0; cert_relabel op)")
    print("=" * 72)
    qid_relabel = f"{atom_relabel.corpus.value}::{atom_relabel.id}"
    row_relabel = build_relabel_row(
        relabel_atom_qid=qid_relabel,
        prior_atom_qid=PRIOR_QUADRUPLE_ATOM_QID,
        verdict=(
            "RELABEL_BARRIER_1_QUADRUPLE_NEGATIVE_per_arm_audit_0_of_5_clean_brain_mechanism_"
            "refutations_all_5_caricature_implementations_atom_NOT_citable_as_substrate_permanent_"
            "2_hop_ceiling_evidence_brain_correct_retests_R1_R5_N1_N2_dispatched_pending_skunkworks_off_data"
        ),
        note=(
            "relabel_BARRIER_1_QUADRUPLE_NEGATIVE_per_arm_audit_USER_pushback_2026-06-27_0_of_5_"
            "clean_refutations_all_caricature_per_META_RULE_U_brain_correct_retests_R1_R5_pending"
        ),
    )
    ok, h_relabel = safe_add_with_ledger(
        atom_relabel,
        source=ATOMIZED_BY,
        note=(
            "RELABEL atom narrows BARRIER_1 QUADRUPLE scope: 0 of 5 constituent cells are "
            "clean refutations of any brain mechanism; all 5 are caricature implementations "
            "per new META_RULE_U; brain-correct retests R1-R5 + N1-N2 pending per Research "
            "drill 2026-06-27."
        ),
        ledger_row=row_relabel,
        expected_cert_n_after=expected_after,
    )
    if not ok:
        print("ABORT: RELABEL window failed; halting.")
        return 1
    rows.append(("RELABEL", h_relabel))
    print(f"  Live CERT N now {expected_after}; row_hash {h_relabel}")

    # A5 POST
    print()
    print("=" * 72)
    print("A5 POST snapshot")
    print("=" * 72)
    ps_post = PartitionedStore(STORE_ROOT)
    cert_post = sum(
        1 for a in ps_post.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    net_delta = cert_post - cert_pre
    print(f"A5-POST: live CERT N = {cert_post}")
    print(f"  CERT N: {cert_pre} -> {cert_post} (net delta = {net_delta:+d}; expected 0)")
    assert net_delta == 0, f"CERT N drift: net_delta={net_delta} (expected 0)"

    # Verify all atoms present
    ps_v = PartitionedStore(STORE_ROOT)
    for label, a in [("T", atom_T), ("U", atom_U), ("V", atom_V), ("RELABEL", atom_relabel)]:
        qid = f"{a.corpus.value}::{a.id}"
        v = ps_v.get_atom(qid)
        assert v is not None, f"Atom {label} missing post-run"
        assert (v.metadata or {}).get("provenance_quality") == "META_RULE_CERT_NEUTRAL"
    print(f"  PASS: all 4 atoms present at intended pq=META_RULE_CERT_NEUTRAL")

    # Verify relabel target still present (we relabel, not delete)
    prior_check = ps_v.get_atom(PRIOR_QUADRUPLE_ATOM_QID)
    assert prior_check is not None, "Relabel target atom must remain in Store post-relabel"
    print(f"  PASS: prior QUADRUPLE atom remains in Store as evidence trail")

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    for role, h in rows:
        print(f"  {role}: row_hash = {h}")
    print(f"  CERT delta: 0 (all CERT-neutral META atoms)")
    print(f"  Live CERT N: {cert_pre} (unchanged)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
