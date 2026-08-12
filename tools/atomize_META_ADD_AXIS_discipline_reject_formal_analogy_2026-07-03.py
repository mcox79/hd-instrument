"""A5-gated atomization: META rule captured from spatial-coupling drill (task a2c1764a5af901762).

Drill outcome: MAYBE / lean-negative (P_deflated=0.20). Do NOT promote coupling-strength
as Regime Map axis. LDPC threshold-saturation mechanism is intrinsically ITERATIVE
(traveling-wave BP), no one-shot VSA argmax analog. Rule captured: axis promotion from
FORMAL analogy alone (no iterative-decoder analog AND no prior empirical evidence in
adjacent lit) must be REJECTED at pre-reg time.

Complements meta atom #44 (axis-labels-map-to-substrate-primitives, MM_STANDARD 2026-07-03):
- #44 is post-decision: "if you add an axis, its label must trace to a substrate primitive"
- This atom is pre-decision: "before you add an axis based on formal analogy, verify (a)
  prior empirical evidence in adjacent literature OR (b) mechanism analog mapping to
  VSA operational primitive"

Composes with multi-round retry drill universal inequality (gap * informativeness <= cost)
which provides information-theoretic backing for the rule.

Tier: MM_TENTATIVE. Single case-study (spatial-coupling drill). Promotion to MM_STANDARD
requires 2 additional independent axis-proposal rejections citing this rule; CG_META
requires 3rd-witness at production application.
"""
from __future__ import annotations
import json
import os
import sys
import datetime as _dt
from pathlib import Path

REPO = Path("d:/AI/hd-instrument")
sys.path.insert(0, str(REPO))

META_ATOMS = REPO / "data" / "substrate_index" / "meta" / "atoms.jsonl"
LEDGER = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"
DATE = "2026-07-03"
TS_ISO = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
ATOMIZED_BY = "skunkworks_atomize_META_ADD_AXIS_reject_formal_analogy_2026-07-03"


ATOM_ID = (
    "META_add_axis_discipline_reject_formal_analogy_without_"
    "iterative_decoder_analog_or_prior_empirical_evidence_v1_2026-07-03"
)


def build_atoms() -> list[dict]:
    return [
        dict(
            id=ATOM_ID,
            qualified_id=f"meta::{ATOM_ID}",
            name=(
                "MM_TENTATIVE_ADD_AXIS_DISCIPLINE: reject Regime Map axis promotion "
                "based on FORMAL cross-domain analogy alone (LDPC threshold saturation "
                "vs VSA argmax capacity corridor). Require either (a) prior empirical "
                "evidence in adjacent VSA/HDC/AM literature that the analog mechanism "
                "widens capacity or (b) mechanism analog that maps directly to a VSA "
                "operational primitive (one-shot bind/unbind/cleanup) rather than "
                "requiring an iterative-decoder surface not present in one-shot argmax. "
                "Captured from spatial-coupling drill 2026-07-03 (P_deflated=0.20)."
            ),
            corpus="meta",
            tier="MM_TENTATIVE",
            kind="methodology_rule_axis_promotion",
            description=(
                "SOURCE-DRILL: notes/research_drill_spatial_coupling_VSA_analog_"
                "regime_map_axis_2026-07-03.md (task a2c1764a5af901762). "
                "FINDING: SC-LDPC (Kudekar/Richardson/Urbanke 1001.1826, 1004.3742; "
                "Yedla 1204.5703, 1208.4080) threshold-saturation requires a "
                "traveling-wave iterative decoder propagating extrinsic information "
                "across a coupling window from a pinned boundary. Yedla potential-"
                "function proof shows this is a property of ANY monotone coupled "
                "recursion with spatial window + boundary + potential -- but reaching "
                "the saturation endpoint requires the ITERATIVE wave. Coupled "
                "compressed sensing (1109.4424, 1112.0708) and expander AM "
                "(1302.1156) both require iterative decoders (AMP, bit-flipping). "
                "VSA one-shot argmax retrieval has NO iterative-decoder surface. "
                "No prior VSA/HRR/resonator/structured-HDC paper implements cross-"
                "item spatial coupling with proven capacity-corridor widening "
                "(surveyed: Frady 1906.11684, Kleyko 2111.06077, VSA capacity "
                "2301.10352, Ramsauer 2008.02217, structured Hopfield 2402.13725). "
                "The analogy is FORMAL (BP-MAP area gap ~ argmax-listwise "
                "informativeness curve area) but does NOT map to a substrate "
                "operational primitive. RULE: axis promotion based on formal "
                "cross-domain analogy is INSUFFICIENT; require empirical "
                "grounding or substrate-primitive mechanism match."
            ),
            rule_statement=(
                "Before promoting a candidate axis to the Regime Map based on a "
                "formal cross-domain analogy (e.g., LDPC/SC-LDPC threshold "
                "saturation; coupled compressed sensing; expander capacity), the "
                "pre-reg MUST demonstrate at least ONE of: (a) prior empirical "
                "evidence in adjacent VSA/HDC/AM literature that the analog "
                "mechanism produces the claimed capacity or accuracy effect, OR "
                "(b) a mechanism analog that maps to a VSA operational primitive "
                "(bind, unbind, superposition, cleanup, argmax readout) rather "
                "than requiring an iterative-decoder or wave-propagation surface "
                "that is not present in one-shot substrate operations. If neither "
                "holds, downgrade the proposal to ONE-PROBE-ONLY with a HARD-FAIL "
                "gate on the discriminator, and do NOT promote the axis unless "
                "the probe HARD-PASSES with monotone-in-strength and cross-seed "
                "consistent effect."
            ),
            operational_rule_for_future_prereg=(
                "SCHEMA-VET checklist item: for any axis-promotion pre-reg citing "
                "a formal analogy from information-theory / coding-theory / "
                "AMP literature, auditor asks: (i) list one VSA/HDC/AM paper "
                "implementing this mechanism with a proven capacity or accuracy "
                "gain; (ii) name the VSA operational primitive the mechanism "
                "maps to. If both answers are absent, reject axis promotion; "
                "allow one probe cell only, with pre-committed HARD-FAIL closure."
            ),
            discriminator_locked=(
                "For coupling-strength axis specifically (probe17 if run): "
                "positive delta_acc must be (i) MONOTONE-in-c across c in "
                "{0, 0.25, 0.5, 0.75, 1.0} AND (ii) survive fixed bundling-"
                "density AND (iii) survive fixed M AND (iv) delta >= 0.15 at "
                "midpoint of dominance corridor; else mislabeled bundling-"
                "density effect or axis-aliasing with F or M."
            ),
            confounds=[
                "dimensionality confound: effective dim of coupled bundle vs "
                "uncoupled bundle; delta_acc must not track delta_d_eff",
                "bundling confound: fixed energy/norm budget across c settings",
                "axis-aliasing check: coupling delta at varying M vs bundle "
                "noise scaling with M",
            ],
            metadata={
                "atomized_by": ATOMIZED_BY,
                "atomized_date": DATE,
                "ts_iso_atomized": TS_ISO,
                "source_drill_memo": (
                    "notes/research_drill_spatial_coupling_VSA_analog_regime_"
                    "map_axis_2026-07-03.md"
                ),
                "source_drill_task_id": "a2c1764a5af901762",
                "P_deflated": 0.20,
                "P_deflated_reasoning": (
                    "novel-synthesis prior cap 0.50; deflation factor 0.30 "
                    "for (no prior VSA empirical precedent) AND (weak "
                    "mechanism-primitive match: iterative-decoder required)"
                ),
                "anchor": "META_add_axis_discipline_2026-07-03",
                "commit_hash": "aae259633",
                "cert_class": "MM_TENTATIVE_METHODOLOGY_RULE_axis_promotion_discipline",
                "cert_status": "MM_TENTATIVE_ADD_AXIS_DISCIPLINE",
                "cert_increment_delta": {"CG": 0, "MM": 1, "HF": 0},
                "verdict": "MM_TENTATIVE_ADD_AXIS_DISCIPLINE",
                "verdict_subtype": (
                    "reject_formal_analogy_without_iterative_decoder_analog_"
                    "or_prior_empirical_evidence"
                ),
                "composes_with": [
                    "meta::META_axis_labels_map_to_substrate_primitives_not_"
                    "theoretical_concepts_discipline_v1_2026_07_03",
                    "feedback_mechanism_abstraction_lossy_cite_source_"
                    "signature_2026-07-03",
                    "feedback_concept_query_before_dispatch_would_have_"
                    "predicted_substrate_content_HF_2026-07-02",
                ],
                "complements_atoms": [
                    "meta::META_axis_labels_map_to_substrate_primitives_not_"
                    "theoretical_concepts_discipline_v1_2026_07_03",
                ],
                "complement_relationship": (
                    "atom #44 is post-decision axis-LABELING discipline "
                    "(labels must trace to substrate primitives); this atom "
                    "is pre-decision axis-PROMOTION discipline (promotion "
                    "requires empirical grounding OR substrate-primitive "
                    "mechanism match, not just formal analogy)"
                ),
                "amends_atoms": [],
                "theoretical_backing": (
                    "Multi-round retry drill universal inequality: "
                    "gap * informativeness <= cost. Formal analogy alone "
                    "provides no bound on informativeness of the proposed "
                    "axis; without substrate-primitive mechanism match, "
                    "informativeness is unbounded from below. Empirical "
                    "evidence in adjacent lit or substrate-primitive "
                    "mechanism match provides the required lower bound."
                ),
                "novelty_check": (
                    "grep meta/atoms.jsonl for axis|add_axis|regime_matrix|"
                    "coupling|formal_analogy: closest existing is #44 "
                    "(axis-labels-to-substrate-primitives, MM_STANDARD) "
                    "which is post-decision LABELING discipline. This atom "
                    "is pre-decision PROMOTION discipline -- complementary "
                    "not overlapping. substrate_query cosine 0.36 top match "
                    "was WordNet stem 'axis' -- no methodology-rule at "
                    "cosine>0.30. Genuinely novel discipline layer."
                ),
                "cross_arc_overlap_check": (
                    "substrate_query 'ADD_AXIS discipline axis promotion "
                    "regime map' returned only wordnet stems at cosine 0.36 "
                    "and one unrelated 2026-05-23 note at 0.32; no prior "
                    "methodology atom at cosine>0.30. NONE."
                ),
                "promotion_criterion": (
                    "Promote MM_TENTATIVE -> MM_STANDARD when 2 additional "
                    "independent axis-proposal cycles (different arcs) "
                    "invoke this rule to reject or downgrade an axis "
                    "candidate. Promote MM_STANDARD -> CG_META when a 3rd "
                    "cycle at production-scrutiny catches an axis-inflation "
                    "attempt at pre-reg time."
                ),
                "revival_criteria_if_falsified": (
                    "If a future coupled-storage / cross-item structural "
                    "context axis is empirically shown to widen the argmax "
                    "dominance corridor in a VSA/HDC substrate WITHOUT an "
                    "iterative-decoder surface (i.e., one-shot argmax with "
                    "coupled bind achieves the widening), rule requires "
                    "amendment: iterative-decoder-analog is no longer "
                    "necessary; substrate-primitive mechanism match remains."
                ),
                "case_study_evidence": {
                    "drill_recommendation": (
                        "MAYBE / lean-negative; ONE-PROBE-ONLY not axis "
                        "promotion"
                    ),
                    "P_deflated": 0.20,
                    "citation_count_verified": 12,
                    "no_prior_VSA_empirical_precedent_found": True,
                    "iterative_decoder_required_across_all_4_frameworks": True,
                    "collapses_onto_existing_axes": (
                        "coupling collapses onto retrieval-mode axis OR "
                        "cortex-composition axis OR aliases with F/M -- "
                        "not a new axis (per drill section i)"
                    ),
                },
                "probe17_recommendation": (
                    "HOLD -- P_deflated=0.20 is below normal fire threshold. "
                    "Higher-P testing site is cortex composition (LDPC-"
                    "Maxwell drill 2026-07-04 target). Fire probe17 only "
                    "as residual closure if cortex-composition arc closes "
                    "without producing coupling-analog signal. Do NOT fire "
                    "as parallel probe."
                ),
                "session_atom_index_meta": 48,
                "verified_off_data": True,
                "verified_off_data_evidence": (
                    "Rule captured from drill memo (verified read, 67 "
                    "lines, 12 citations, all sections a-k present); "
                    "novelty check via grep of meta/atoms.jsonl for axis|"
                    "coupling|alias plus substrate_query; complement "
                    "relationship with #44 verified via read of #44 "
                    "rule_statement (MM_STANDARD, 2026-07-03). No cell "
                    "landing to re-verify -- this is a discipline atom "
                    "sourced from research-drill lit-review not empirical "
                    "cell outcome."
                ),
                "landed_vet_by": "skunkworks",
                "landed_vet_date": DATE,
                "session_id": "2026-07-03_META_add_axis_discipline",
            },
        ),
    ]


def append_ledger(entry: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    tmp = LEDGER.with_suffix(LEDGER.suffix + ".tmp")
    prior = LEDGER.read_text(encoding="utf-8") if LEDGER.exists() else ""
    if prior and not prior.endswith("\n"):
        prior += "\n"
    tmp.write_text(prior + json.dumps(entry, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    os.replace(tmp, LEDGER)


def main() -> int:
    print(f"[A5] Loading pre-existing meta atoms.jsonl lines ...")
    raw_lines = META_ATOMS.read_text(encoding="utf-8").splitlines() if META_ATOMS.exists() else []
    before_count = len([ln for ln in raw_lines if ln.strip()])
    print(f"[A5] before_count = {before_count}")

    existing_ids = set()
    for ln in raw_lines:
        s = ln.strip()
        if not s:
            continue
        try:
            d = json.loads(s)
            if "qualified_id" in d:
                existing_ids.add(d["qualified_id"])
            if "id" in d:
                existing_ids.add(d["id"])
            if "atom_id" in d:
                existing_ids.add(d["atom_id"])
        except json.JSONDecodeError:
            pass

    to_write = build_atoms()
    new_ids = [a["qualified_id"] for a in to_write]
    print(f"[A5] proposing {len(to_write)} new atoms:")
    for a in to_write:
        print(f"  - {a['qualified_id']}  (kind={a['kind']})")

    dup = [i for i in new_ids if i in existing_ids or i.split('::', 1)[-1] in existing_ids]
    if dup:
        print("[A5-FAIL] duplicate ids; aborting")
        for i in dup:
            print(f"  DUP: {i}")
        return 2

    print(f"[A5] atomic tmp write + os.replace ...")
    tmp = META_ATOMS.with_suffix(META_ATOMS.suffix + ".tmp")
    prior_text = META_ATOMS.read_text(encoding="utf-8") if META_ATOMS.exists() else ""
    if prior_text and not prior_text.endswith("\n"):
        prior_text += "\n"
    new_text_parts = [json.dumps(a, ensure_ascii=False) + "\n" for a in to_write]
    tmp.write_text(prior_text + "".join(new_text_parts), encoding="utf-8")
    os.replace(tmp, META_ATOMS)

    print("[A5] verify-load post-write ...")
    reloaded_lines = META_ATOMS.read_text(encoding="utf-8").splitlines()
    after_count = len([ln for ln in reloaded_lines if ln.strip()])
    print(f"[A5] after_count = {after_count}")

    assert after_count == before_count + len(to_write), (
        f"count mismatch: before={before_count} to_write={len(to_write)} after={after_count}"
    )
    reloaded_ids = set()
    for ln in reloaded_lines:
        s = ln.strip()
        if not s:
            continue
        try:
            d = json.loads(s)
            if "qualified_id" in d:
                reloaded_ids.add(d["qualified_id"])
        except json.JSONDecodeError:
            pass
    for new_id in new_ids:
        assert new_id in reloaded_ids, f"missing after reload: {new_id}"

    ledger_entry = {
        "ts": TS_ISO,
        "atom_id": f"meta::{ATOM_ID}",
        "atom_ref": (
            "meta::META_add_axis_discipline_reject_formal_analogy_"
            "spatial_coupling_drill_MM_TENTATIVE"
        ),
        "cert_class": "MM_TENTATIVE_ADD_AXIS_DISCIPLINE",
        "cert_delta": {"CG": 0, "MM": 1, "HF": 0},
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "source_drill_memo": (
            "notes/research_drill_spatial_coupling_VSA_analog_regime_map_"
            "axis_2026-07-03.md"
        ),
        "source_drill_task_id": "a2c1764a5af901762",
        "note": (
            "Meta rule captured from spatial-coupling drill "
            "(P_deflated=0.20). Rule: reject Regime Map axis promotion "
            "from formal cross-domain analogy alone; require prior "
            "empirical evidence in adjacent lit OR substrate-primitive "
            "mechanism match. Complements meta atom #44 (axis-labels-"
            "to-substrate-primitives, MM_STANDARD). Composes with "
            "multi-round retry drill universal inequality "
            "(gap * informativeness <= cost). Probe17 recommendation: "
            "HOLD pending cortex-composition arc outcome."
        ),
    }
    append_ledger(ledger_entry)
    print(f"[A5] ledger appended: {LEDGER}")
    print(f"[A5] DONE. new meta atom id: meta::{ATOM_ID}")
    print(f"[A5] session tally meta after write: {after_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
