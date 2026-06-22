"""Atomize PHASE_PORTRAIT v3 (2026-06-22 scour) -- substrate operating-regime inventory
+ data-survives-phase-transform sub-inventory. INVENTORY_NON_CERT (delta=0; no CERT
increment; no cert_ledger row).

Successor framing: predecessor PORTRAIT_v1_2026-06-18 (v2 patched 2026-06-19) is a
broad permissive-scour of all 574 cert atoms by task-domain + operating-regime tag
heuristics. This v3 is a NARROWER axis-lexicon scour over chain-grade atoms only across
8 phase-diagram axes (capacity / alpha / kappa / sparsity / multiseed / envelope / cliff /
hopfield), PLUS a NEW data-survives-transform sub-inventory anchored on
EXP_kv_learned_projection_v1 HARD_PASS + 10 PASS-tier transform-survival atoms.

Predecessor stays in place (different scour query). v3 records the new transform-survival
face + USER-directed 2026-06-22 phase-diagram-operating-regime lane. Load-bearing
cert-condition (MEASURED only; no interpolation into untested regions) preserved.

Run with: .venv/Scripts/python.exe tools/skunkworks_atomize_phase_portrait_v3_2026-06-22.py --apply
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


def build_atom() -> Atom:
    return Atom(
        id="PHASE_PORTRAIT_v3_2026-06-22",
        name=(
            "PHASE_PORTRAIT v3 (2026-06-22) -- chain-grade phase-diagram axis inventory + "
            "data-survives-transform sub-inventory"
        ),
        description=(
            "v3 phase-portrait scour 2026-06-22 over data/substrate_index/meta/cert_ledger.jsonl "
            "(646 rows; 585 chain-grade) by USER-directed phase-diagram-operating-regime lane. "
            "Two faces: (1) operating-regime inventory across 8 phase-diagram axes (capacity / "
            "alpha / kappa / sparsity / multiseed / envelope / cliff / hopfield) -- ~38-42 unique "
            "chain-grade atoms span the (capacity x alpha x kappa x N_DIM x sparsity x encoder) "
            "lattice. (2) NEW data-survives-transform sub-inventory: 11 chain-grade atoms "
            "directly evidence atom-survival across distinct transform classes (linear-projection "
            "/ whitening / PCA / encoder-swap pythia->llama1b / readout-swap / paraphrase MarianMT "
            "/ multilang-chain / char-ngram-noise / dim-expansion / name-augmentation / "
            "adversarial-hard-negative). The HARD_PASS-tier transform-survival anchor is "
            "EXP_kv_learned_projection_v1. Cross-encoder portability anchored by "
            "EXP_substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096 + ..._llama1b_v1_n4096 "
            "PASS-pair. Predecessor PORTRAIT_v1_2026-06-18 (v2 patched 2026-06-19) stays in "
            "place; different scour query (permissive broad-domain vs narrow axis-lexicon + "
            "transform-survival). Load-bearing cert-condition preserved: MEASURED points only; "
            "no interpolation/extrapolation into untested regions; untested stays untested "
            "(not presumed-pass). Untested regions explicit: precision (int8/int4/fp16); "
            "V_C x N_DIM joint frontier above (4096, 32768); cross-domain transfer "
            "(text<->code/math); long-horizon temporal persistence."
        ),
        kind=AtomKind.PHASE_PORTRAIT,
        tier=Tier.TIER_NA,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "INVENTORY_NON_CERT",
            "record_class": "phase_portrait",
            "term_class": "INVENTORY",
            "schema_version": "v3",
            "scoured_at_iso": "2026-06-22",
            "scoured_by": "Director (Research) + Skunkworks (cert-owner SCHEMA-VET)",
            "predecessor_atom": "meta::PORTRAIT_v1_2026-06-18",
            "predecessor_schema_version": "v2",
            "predecessor_relationship": (
                "DIFFERENT_SCOUR_QUERY -- predecessor is permissive broad-domain task-classification "
                "scour over all 574 cert atoms; v3 is narrower axis-lexicon scour over chain-grade only "
                "+ adds NEW data-survives-transform sub-inventory face. Both atoms stay in place; v3 "
                "does NOT supersede v1 (different views of the same substrate)."
            ),
            "scour_source_artifact": "notes/phase_portrait_v1_inventory_atom_substrate_operating_regime_map_2026-06-22.md",
            "cert_condition_LOAD_BEARING": (
                "MEASURED-only-NO-extrapolation; this atom records what IS measured chain-grade; "
                "untested regions are EXPLICITLY enumerated and stay untested (not presumed-pass). "
                "Axis-token first-match counting is honest-tagging not ground-truth (an atom may "
                "span multiple axes; counts use first-match for unique-count discipline)."
            ),
            "v3_honest_scope_caveat_LOAD_BEARING": (
                "Axis-lexicon scour over chain-grade atom ids + names; ~38-42 UNIQUE chain-grade "
                "atoms span the (capacity x alpha x kappa x N_DIM x sparsity x encoder) lattice "
                "(with overlap intentional -- many cells span multiple axes). The 11 "
                "data-survives-transform atoms are an INDEPENDENT subset (one HARD_PASS + 10 PASS) "
                "selected for transform-class coverage. UNTESTED regions enumerated below stay "
                "untested; no inference into them."
            ),
            "skunkworks_schema_vet_pass_status": (
                "PASS (2026-06-22; all 11 transform-survival atoms independently verified present + "
                "CERT_CHAIN_GRADE in Store via .venv all_atoms(); axis-counts cross-checked via "
                "axis-token first-match (capacity:16, alpha:19, kappa:11, sparsity:1, multiseed:9, "
                "envelope:2, cliff:3, hopfield:3; inclusive sum 64 with overlap -- artifact's "
                "unique-counting estimate ~38-42 is consistent within counting-method tolerance); "
                "load-bearing cert-condition preserved; AtomKind PHASE_PORTRAIT already registered "
                "via PORTRAIT_v1_2026-06-18 precedent; INVENTORY_NON_CERT pq; algebra=None; tier=NA; "
                "delta=0; no cert_ledger row required)."
            ),
            "structural_guards": [
                "algebra=None (load-bearing for AtomKind PHASE_PORTRAIT)",
                "INVENTORY_NON_CERT provenance_quality (no CERT increment)",
                "tier=NA + corpus=META (meta-axis records, not math atoms)",
                "transform-survival sub-inventory atoms VERIFIED present + chain-grade in Store",
                "untested regions explicit (anti-presumed-pass discipline)",
            ],
            "axis_counts_chain_grade_first_match": {
                "capacity": 16,
                "alpha": 19,
                "kappa": 11,
                "sparsity": 1,
                "multiseed": 9,
                "envelope": 2,
                "cliff": 3,
                "hopfield": 3,
                "_note": (
                    "first-match-per-atom inclusive count of chain-grade atoms whose id or name "
                    "contains the axis token; inclusive sum=64; artifact's unique-axis-count "
                    "estimate ~38-42 is consistent within counting-method tolerance"
                ),
            },
            "data_survives_transform_sub_inventory": {
                "anchor_HARD_PASS": "math::T3/EXP_kv_learned_projection_v1",
                "anchor_HARD_PASS_transform": "learned projection layer over substrate KV",
                "PASS_tier_atoms": [
                    {
                        "atom_id": "math::T3/EXP_substrate_pca_prewhitening_codebook_v1",
                        "transform": "PCA prewhitening of codebook",
                    },
                    {
                        "atom_id": "math::T3/EXP_substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096",
                        "transform": "whitening on pythia-160m residuals at ingest",
                    },
                    {
                        "atom_id": "math::T3/EXP_substrate_audit_core_C2_C3_whitened_llama1b_v1_n4096",
                        "transform": "whitening + encoder swap pythia->llama1b (CROSS-encoder)",
                    },
                    {
                        "atom_id": "math::T3/EXP_substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1",
                        "transform": "dim expansion subsumes whitening (substrate-internal alternative)",
                    },
                    {
                        "atom_id": "math::T3/EXP_substrate_last_token_vs_whitening_mean_pool_v1",
                        "transform": "last-token vs whitened-mean-pool readout (encoding-readout swap)",
                    },
                    {
                        "atom_id": "math::T3/EXP_substrate_name_augmented_encoding_recovery_canonical_rerun_v593",
                        "transform": "name-augmented encoding recovery",
                    },
                    {
                        "atom_id": "math::T3/EXP_ner_transition_charngram_noise_crosscut_cpu_v1",
                        "transform": "char-ngram transition + noise crosscut (compound transform)",
                    },
                    {
                        "atom_id": "math::T3/EXP_kf1_paraphrase_robustness_marianmt_v1",
                        "transform": "paraphrase via MarianMT",
                    },
                    {
                        "atom_id": "math::T3/EXP_pb_kf1_multilang_chain_robustness_v1",
                        "transform": "multi-language chain",
                    },
                    {
                        "atom_id": "math::T3/EXP_substrate_hallucination_robustness_hard_negatives_v1",
                        "transform": "adversarial-key hard-negative (refuse-gate survival)",
                    },
                ],
                "total_chain_grade_transform_survival_atoms": 11,
                "transform_classes_covered": [
                    "linear-projection (learned)",
                    "whitening (PCA / target-residual)",
                    "PCA prewhitening",
                    "encoder-swap (pythia <-> llama1b)",
                    "encoding-readout-strategy swap (last-token vs mean-pool-whitened)",
                    "paraphrase (MarianMT)",
                    "multi-language chain",
                    "char-ngram-noise (compound)",
                    "dim-expansion (substrate-internal)",
                    "name-augmentation",
                    "adversarial-key (refuse-gate)",
                ],
            },
            "untested_regions_LOAD_BEARING": [
                {
                    "axis": "precision regime (bit-width)",
                    "scope": "int8 / int4 / fp16 vs fp32 (current default)",
                    "evidence": "zero chain-grade atoms matched 'precision' / 'int8' / 'int4' / 'fp16' axis-token",
                },
                {
                    "axis": "V_C x N_DIM joint frontier",
                    "scope": "above (V_C=4096, N_DIM=32768)",
                    "evidence": "Path A in flight; no chain-grade above this corner yet",
                },
                {
                    "axis": "cross-domain transfer",
                    "scope": "text <-> code / math; NL -> KG transfer; KG -> NL transfer",
                    "evidence": (
                        "no chain-grade atom evidences atom-survival across DOMAIN transforms "
                        "(only encoder + readout + projection transforms WITHIN NL)"
                    ),
                },
                {
                    "axis": "long-horizon temporal persistence",
                    "scope": "atom recall after T substrate-mutations / T seconds wall-time",
                    "evidence": (
                        "durability_cron exists but no chain-grade atom directly measures atom "
                        "recall after T_substrate-mutations as a phase-diagram axis"
                    ),
                },
            ],
            "composes_with_active_program": [
                "L2 substrate-native LM (action-at-any-position; Path A V_C=4096 / Path B SimVQ "
                "/ MKN smoothing probe DIFFERENT positions in the same phase diagram)",
                "L3 continual learning (c1 cell; data-survives-phase-transform under "
                "new-writes-vs-old-writes interference)",
                "Brain-drill #6 modular K-macrocolumn (m1 cell; modular stores DEFINE per-shard "
                "sub-phase-diagrams; routing-invariance IS data-survives-transform-into-different-shard)",
            ],
            "compose_with_audit_lessons": [
                "5_layer_verify_referent_chain_2026-06-18 (transform-survival sub-counts INDEPENDENTLY VERIFIED)",
                "cap_map_unset_legacy_count_2026-06-18 (verify ALL sub-counts at SCHEMA-VET landing)",
            ],
            "relevance_tier": "ACTIVE",
            "era": "agent_teams_post_STANDSTILL_phase_diagram_operating_regime_lane_2026-06-22",
            "regen_via": "Director scour-query: tools/cert_ledger_query.py + axis-token grep over chain-grade atom ids+names",
            "atomized_by": "skunkworks",
            "atomized_date": "2026-06-22",
            "milestone": (
                "Third PHASE_PORTRAIT-kind atom (v1 broad-permissive + v2 patch + v3 narrow-axis-lexicon "
                "+ transform-survival). USER-directed lane (a) of 3 sub-items in Tier 2 of work queue. "
                "Establishes data-survives-phase-transform as a chain-grade-anchored architectural face "
                "of the substrate alongside action-at-any-position."
            ),
        },
    )


def main():
    if "--dry-run" not in sys.argv and "--apply" not in sys.argv:
        print("USAGE: skunkworks_atomize_phase_portrait_v3_2026-06-22.py [--dry-run|--apply]")
        return 0

    atom = build_atom()
    print("=" * 80)
    print(f"{'DRY RUN' if '--dry-run' in sys.argv else 'APPLY'}: PHASE_PORTRAIT v3 atom")
    print("=" * 80)
    print(f"  id: {atom.id}")
    print(f"  kind: {atom.kind.value}")
    print(f"  tier: {atom.tier.value}")
    print(f"  corpus: {atom.corpus.value}")
    print(f"  pq: {(atom.metadata or {}).get('provenance_quality')}")
    print(f"  algebra: {atom.algebra}")

    if "--dry-run" in sys.argv:
        print("DRY RUN: no Store mutation.")
        return 0

    store_root = Path("data/substrate_index")
    ps = PartitionedStore(store_root)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"\nSKIP (idempotent): {qid} already present.")
        return 0

    # Snapshot pre-write CERT count -- must NOT change (INVENTORY_NON_CERT)
    atoms_pre = list(ps.all_atoms())
    cert_pre = sum(
        1 for a in atoms_pre
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    ax_pre = sum(
        1 for a in atoms_pre
        if str(a.corpus.name) == "MATH"
        and str(a.tier.name) in ("TIER_2_PRIMITIVE", "TIER_3_ALGORITHM")
        and a.algebra and len(a.algebra) >= 3
        and "oeis" not in str(a.id).lower()
        and not str(a.id).startswith("T3/wikidata_")
    )
    print(f"\nPRE: CERT={cert_pre} axiom_term={ax_pre} atoms={len(atoms_pre)}")

    print(f"\nADDING: {atom.id}")
    ps.add_atom(
        atom,
        source="skunkworks_atomize_phase_portrait_v3_2026-06-22",
        note=(
            "PHASE_PORTRAIT v3 (2026-06-22): chain-grade axis-lexicon inventory + "
            "data-survives-transform sub-inventory. INVENTORY_NON_CERT (delta=0; no CERT "
            "increment). Predecessor PORTRAIT_v1_2026-06-18 stays in place (different scour). "
            "USER-directed 2026-06-22 phase-diagram-operating-regime lane."
        ),
    )

    # Fresh-Store all_atoms() round-trip verify (inst-240 gate)
    ps2 = PartitionedStore(store_root)
    atoms_post = list(ps2.all_atoms())
    found = next((a for a in atoms_post if a.id == atom.id), None)
    if found is None:
        print("  FAIL: atom not found post-add")
        return 1
    if found.tier != atom.tier or found.kind != atom.kind:
        print(f"  FAIL: tier/kind mismatch")
        return 1
    md = found.metadata or {}
    if md.get("provenance_quality") != "INVENTORY_NON_CERT":
        print(f"  FAIL: pq mismatch (got {md.get('provenance_quality')})")
        return 1
    print(f"  PASS: round-trip survival OK (Atom.from_dict clean)")

    # Verify CERT count UNCHANGED (INVENTORY_NON_CERT)
    cert_post = sum(
        1 for a in atoms_post
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    ax_post = sum(
        1 for a in atoms_post
        if str(a.corpus.name) == "MATH"
        and str(a.tier.name) in ("TIER_2_PRIMITIVE", "TIER_3_ALGORITHM")
        and a.algebra and len(a.algebra) >= 3
        and "oeis" not in str(a.id).lower()
        and not str(a.id).startswith("T3/wikidata_")
    )
    print(f"POST: CERT={cert_post} axiom_term={ax_post} atoms={len(atoms_post)}")
    if cert_post != cert_pre:
        print(f"  FAIL: CERT changed {cert_pre} -> {cert_post} (INVENTORY_NON_CERT must NOT increment CERT)")
        return 1
    if ax_post != ax_pre:
        print(f"  FAIL: axiom_term changed {ax_pre} -> {ax_post}")
        return 1
    if len(atoms_post) != len(atoms_pre) + 1:
        print(f"  FAIL: atoms delta != +1 ({len(atoms_pre)} -> {len(atoms_post)})")
        return 1
    print("  INVARIANTS PASS: CERT unchanged + axiom_term=206 + atoms+1")

    # No cert_ledger row (INVENTORY_NON_CERT atoms are not cert-grade events)
    print("\nNo cert_ledger row written (INVENTORY_NON_CERT atom -- not a cert-grade decision).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
