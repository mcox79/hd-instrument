"""A5-gated atomization: 2026-07-03 Option Y SMOKE regime-boundary finding.

Landed-VET: CLEANUP_MECHANISM axis is REGIME-NARROW. Structurally degenerate
in SHARDED per-antecedent isolation regime because per-trial cleanup query has
exactly one dominant codebook match; argmax collapses distinct mechanism outputs
(distinct output_hashes verified: 7e58a6dd / 340cd0fb / ee2af1ab) to identical
target indices (acc=1.0 for all 3 mechanisms at both corr=0.20 AND corr=0.45).

Tier: MM_TENTATIVE_REGIME_BOUNDARY (single-witness scope refinement of prior
CG_META PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian).

Corpus: meta (methodology / regime-boundary finding about CG_META axis scope).

Off-data verification:
- metrics.json read: 7 phase points confirmed
  - modern_hopfield SHARDED c0.20 acc=1.0 c0.45 acc=1.0
  - iterative_cosine SHARDED c0.20 acc=1.0 c0.45 acc=1.0
  - soft_energy_attractor SHARDED c0.20 acc=1.0 c0.45 acc=1.0
  - BUNDLED_PC iterative_cosine c0.20 acc=0.0 storage_gap=1.0
- mech_output_hash_agg: 3 distinct hashes (per-mechanism cleanup work IS distinct)
- max_mechanism_variation_at_cliff = 0.0 (argmax collapse to identical indices)
- Core-cell code path verified (run_chain SHARDED branch line 299-306): per-trial
  rule_batch = sharded_codebook[ci, f_step] -> single stored codeword per trial;
  target-argmax has no cross-item competition; mechanism axis degenerate by
  construction.
"""
from __future__ import annotations
import json
import sys
import datetime as _dt
from pathlib import Path

REPO = Path("d:/AI/hd-instrument")
sys.path.insert(0, str(REPO))

import os

META_ATOMS = REPO / "data" / "substrate_index" / "meta" / "atoms.jsonl"
LEDGER = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"
DATE = "2026-07-03"
TS_ISO = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
ATOMIZED_BY = "skunkworks_atomize_2026-07-03_option_y_regime_boundary_MM"


ATOM_ID = (
    "T4/META_CLEANUP_MECHANISM_AXIS_IS_REGIME_NARROW_"
    "DEGENERATE_IN_SHARDED_PER_ANTECEDENT_ISOLATION_"
    "DISCRIMINATES_ONLY_IN_COMPETITIVE_CLEANUP_REGIME_"
    "amendment_to_M_sweep_CG_META_scope_"
    "witness_stage1_physics_law_joint_composition_factorial_v1_s11_SMOKE_2026-07-03"
)


def build_atoms() -> list[dict]:
    return [
        dict(
            id=ATOM_ID,
            qualified_id=f"meta::{ATOM_ID}",
            name=(
                "MM_TENTATIVE_REGIME_BOUNDARY: CLEANUP_MECHANISM CG_META axis is "
                "REGIME-NARROW. Discriminates in COMPETITIVE-CLEANUP regime (bipolar "
                "shared codebook, dense associative memory where many stored items "
                "share dimensions) but is STRUCTURALLY DEGENERATE in SHARDED "
                "per-antecedent isolation regime (per-trial cleanup query has exactly "
                "one dominant codeword match -> argmax collapses distinct mechanism "
                "outputs to identical target indices). Prior CG_META "
                "PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian (v2 M-sweep) "
                "requires regime-scope amendment. FULL dispatch aborted with "
                "substantive scientific finding. CERT +0 (regime-scope refinement)."
            ),
            corpus="meta",
            tier="T4",
            kind="methodology_rule_regime_refinement",
            description=(
                "SMOKE landing (Option Y regime = SHARDED FHRR chain composition) "
                "shows CLEANUP_MECHANISM axis produces zero variance across the "
                "3 mechanisms {modern_hopfield, iterative_cosine, soft_energy_"
                "attractor} at both corruption levels {0.20, 0.45} at fixed "
                "M=800 N=2048 F=1 L=2, TR=40 (all 6 SHARDED points acc=1.0). "
                "Per-mechanism output_hash_agg confirms mechanism-level cleanup "
                "IS distinct (7e58a6dd1f03f936 / 340cd0fb960b113b / "
                "ee2af1ab629d00e4) -- mechanisms produce different intermediate "
                "cleaned vectors, but subsequent matched-filter argmax readout "
                "against the props codebook collapses distinct vectors to the "
                "same target index because in SHARDED regime the per-antecedent "
                "shard stores exactly one rule per (ci, f_step) pair. Structural "
                "code-path evidence (experiments/_stage1_physics_law_joint_"
                "composition_factorial_v1_core.py:run_chain SHARDED branch "
                "L299-306): rule_batch = sharded_codebook[ci, f_step_per_trial] "
                "-> single target codeword per trial; cand_corr aligned with "
                "one dominant props row and near-noise with M-1 others; argmax "
                "trivially correct for all 3 mechanisms whenever SNR adequate. "
                "Cell-author extended L x corr sweep (L in {2,5,10,20}, corr in "
                "{0.45, 0.70, 0.85, 0.90}) reported bit-identical mechanism "
                "outputs -- consistent with structural argument (not "
                "independently re-run by auditor, but not required: SHARDED "
                "structural degeneracy is provable from code path). "
                "BUNDLED positive control fires cleanly: BUNDLED_PC "
                "iterative_cosine at same regime acc=0.0 vs SHARDED acc=1.0 "
                "-> storage-gap discriminator = 1.0 (SHARDED vs BUNDLED "
                "storage axis works exactly as prior CG_META predicted). "
                "REGIME-SCOPE AMENDMENT to PHYSICS_LAW_cleanup_mechanism_M_"
                "scaling_non_Hebbian: axis applies to competitive-cleanup "
                "regime (bipolar codebook with M items sharing dimensions, "
                "as in v2 M-sweep source atom) and does NOT compose with "
                "sharded per-antecedent isolation regime. This is not a bug "
                "in the pre-reg or cell -- it is a real property of the "
                "substrate physics: cleanup-mechanism differences manifest "
                "in top-k competition, not in single-target isolation. "
                "Cell-author 3-option assessment: (Y-2 add STORAGE axis) "
                "highest-value redesign -- swap BUNDLED and SHARDED as an "
                "axis so competitive regime is included and mechanism-axis "
                "fires; (Z pairwise cross-regime witnesses) valid but "
                "weaker; (A accept 3-axis composite + log CLEANUP_MECHANISM "
                "as regime-narrow) terminal fallback. Cell-author "
                "abort-FULL decision is CORRECT: running FULL 144-pt grid "
                "would produce pre-known-degenerate mechanism dimension "
                "and waste GPU budget with zero information gain. "
                "Meta-level: this is the 3rd cell-author self-correction "
                "halt today (Option Z regime-mismatch; 170K scale re-test "
                "blockers; this Option Y cliff degeneracy) -- pattern "
                "MM_TENTATIVE_STANDARD candidate (single-day 3-witness). "
                "Tier: MM_TENTATIVE_REGIME_BOUNDARY. Promotion to "
                "MM_STANDARD on second independent witness of "
                "CLEANUP_MECHANISM degeneracy in a different SHARDED "
                "config; promotion to CG_META on empirical confirmation "
                "via Option Y-2 STORAGE-axis sweep firing mechanism-axis "
                "in BUNDLED points at same cell."
            ),
            metadata={
                "atomized_by": ATOMIZED_BY,
                "atomized_date": DATE,
                "ts_iso_atomized": TS_ISO,
                "cell_path": (
                    "experiments/_stage1_physics_law_joint_composition_"
                    "factorial_v1_core.py"
                ),
                "wrapper_paths": [
                    "experiments/exp_stage1_physics_law_joint_composition_"
                    "factorial_v1_s11.py"
                ],
                "prereg_path": (
                    "preregs/2026-07-03_stage1_physics_law_joint_"
                    "composition_factorial_test.md"
                ),
                "metrics_path": (
                    "data/exp_stage1_physics_law_joint_composition_"
                    "factorial_v1_s11_smoke/metrics.json"
                ),
                "anchor": "stage1_physics_law_joint_composition_factorial_v1_s11",
                "cert_class": "regime_boundary_amendment",
                "cert_status": "MM_TENTATIVE_REGIME_BOUNDARY",
                "cert_increment_delta": {"CG": 0, "MM": 1, "HF": 0},
                "verdict": "MM_TENTATIVE_REGIME_BOUNDARY",
                "verdict_subtype": (
                    "cleanup_mechanism_axis_structurally_degenerate_in_"
                    "sharded_per_antecedent_isolation_regime_scope_narrow_"
                    "to_competitive_cleanup"
                ),
                "amends_atoms": [
                    "T4/PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian",
                ],
                "composes_atoms": [
                    "T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1",
                    "T4/PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian",
                ],
                "regime_scope_native": (
                    "competitive_cleanup_bipolar_or_dense_shared_codebook_"
                    "where_multiple_items_share_dimensions"
                ),
                "regime_scope_excluded": (
                    "sharded_per_antecedent_isolation_where_per_trial_"
                    "cleanup_query_has_single_dominant_target"
                ),
                "smoke_phase_point_count": 7,
                "sharded_phase_points": 6,
                "sharded_all_acc_equal_1p0": True,
                "mech_output_hashes_distinct": True,
                "mech_output_hash_agg": {
                    "modern_hopfield": "7e58a6dd1f03f936",
                    "iterative_cosine": "340cd0fb960b113b",
                    "soft_energy_attractor": "ee2af1ab629d00e4",
                },
                "max_mechanism_variation_at_cliff": 0.0,
                "bundled_pc_acc": 0.0,
                "sharded_at_same_regime_acc": 1.0,
                "storage_gap_sharded_minus_bundled": 1.0,
                "bundled_pc_fires_correctly": True,
                "cell_author_abort_full_correct": True,
                "cell_author_recommendation": (
                    "Option Y-2 add STORAGE axis (SHARDED vs BUNDLED "
                    "sweep) highest-value; Option Z pairwise cross-"
                    "regime witnesses valid but weaker; Option A accept "
                    "3-axis composite terminal-fallback"
                ),
                "cross_arc_overlap_check": (
                    "substrate_query cosine=0.289 top match 'Mechanism "
                    "isolation outcome' (June 12 testbed note) -- no "
                    "prior atom at cosine>0.30; novel regime-boundary "
                    "finding"
                ),
                "meta_rule_AY_self_report": True,
                "verified_off_data": True,
                "verified_off_data_evidence": (
                    "OFF-DATA .venv read of metrics.json phase_map: 6 "
                    "SHARDED points all acc=1.0; BUNDLED_PC acc=0.0; "
                    "3 distinct mech_output_hashes; max_mechanism_"
                    "variation_at_cliff=0.0. Structural argument "
                    "verified via code path _core.py:run_chain "
                    "L299-306 SHARDED branch reads sharded_codebook"
                    "[ci, f_step] single-rule-per-trial -> mechanism-"
                    "axis-degenerate by construction. Independent "
                    "L x corr extended-sweep (cell-author-reported) "
                    "not separately re-run but not required for "
                    "structural argument."
                ),
                "landed_vet_by": "skunkworks",
                "landed_vet_date": DATE,
                "session_id": "2026-07-03_option_y_smoke_regime_boundary",
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
    # A5 gate on raw JSONL (bypass strict AtomKind enum -- pre-existing schema
    # drift in meta partition with free-form kind values; we preserve that
    # convention rather than force-migrate).
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
        except json.JSONDecodeError:
            pass

    to_write = build_atoms()
    new_ids = [a["qualified_id"] for a in to_write]
    print(f"[A5] proposing {len(to_write)} new atoms:")
    for a in to_write:
        print(f"  - {a['qualified_id']}  (kind={a['kind']})")

    dup = [i for i in new_ids if i in existing_ids or i.split('::',1)[-1] in existing_ids]
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

    # Ledger entry
    ledger_entry = {
        "ts": TS_ISO,
        "atom_id": f"meta::{ATOM_ID}",
        "atom_ref": (
            "meta::stage1_physics_law_joint_composition_factorial_v1_"
            "s11_SMOKE_regime_boundary_MM_TENTATIVE"
        ),
        "cert_class": "MM_TENTATIVE_REGIME_BOUNDARY",
        "cert_delta": {"CG": 0, "MM": 1, "HF": 0},
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "landing_path": (
            "data/exp_stage1_physics_law_joint_composition_factorial_"
            "v1_s11_smoke/metrics.json"
        ),
        "note": (
            "CLEANUP_MECHANISM axis structurally degenerate in SHARDED "
            "per-antecedent isolation; regime-scope amendment to prior "
            "M-sweep CG_META. Cell-author FULL-abort correct. Option Y-2 "
            "recommended (add STORAGE axis) to restore mechanism-axis "
            "discrimination. Director M-sweep CG_META atom needs "
            "regime-scope annotation."
        ),
    }
    append_ledger(ledger_entry)
    print(f"[LEDGER-OK] appended entry ts={TS_ISO}")

    print(f"[A5-OK] wrote {len(to_write)} atoms; before={before} after={after}")
    for new_id in new_ids:
        print(f"  OK: {new_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
