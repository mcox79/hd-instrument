#!/usr/bin/env python3
"""Atomize n8 ConceptNet ingest-eval v1 as chain-grade EXPERIMENT_RECORD; CERT 584 -> 585.

Pattern: parallel to U1 FB15k-237 ingest-eval atom (the first post-STANDSTILL chain-grade),
which is the precedent at math::T3/EXP_u1_fb15k237_ingest_eval_v1.

n8 ConceptNet adds:
- KB-INGEST scale-curve PERFECT at M={5k, 10k, 25k, 50k, 100k} (vs U1's 50k cap)
- OPEN-C UNLOCKED: frozen-encoder semantic baseline (MiniLM-L6 ingest-time only;
  scoring is matmul, no LLM forward calls at inference -- substrate-only-decode preserved)
- 36.5x 2hop-vs-frozen-encoder ratio (vs the 2.0x band; 1hop=0.0 by closure construction)
- discriminator-real check: heldout_in_compose_graph==0 across all 3 seeds (perfect-by-
  construction guard from the inference-transfer eval design discipline; substrate
  must INFER, not retrieve)

Run with:
  .venv/Scripts/python.exe tools/skunkworks_atomize_n8_conceptnet_chain_grade_cert585_2026-06-22.py --apply
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import append_cert_ledger_row, build_chain_grade_ruling_row


def build_atom() -> Atom:
    return Atom(
        id="T3/EXP_n8_conceptnet_ingest_eval_v1",
        name=(
            "EXP exp_n8_conceptnet_ingest_eval_v1 -- chain-grade ConceptNet KB-ingest "
            "with frozen-encoder semantic baseline (OPEN-C unlock) + 2-hop inference "
            "vs 1-hop closure + 36.5x ratio over MiniLM-L6 frozen-encoder; setrecall 1.000 "
            "all 5 scale points 5k->100k; refuse-gate OOD=0.999 accept=0.997"
        ),
        description=(
            "n8 ConceptNet en-100k ingest-eval at N_DIM=8192 with 3 seeds (7/17/23) full run. "
            "Replicates U1 FB15k-237 chain-grade pattern on a SECOND KG (ConceptNet) at a "
            "LARGER M-scale (up to 100k triples vs U1's 50k cap). KEY ADDITION over U1: "
            "frozen-encoder semantic baseline (MiniLM-L6 sentence-transformer; OPEN-C unlock) "
            "as the harder bar -- substrate must beat semantic-similarity retrieval, not just "
            "lookup. ZERO LLM forward calls at inference (encoder used at ingest-stage only; "
            "scoring is matmul). HEADLINES: setrecall@M100000 all=1.000 1to1=1.000 across all "
            "3 seeds; refuse-gate OOD=0.999 accept=0.997; 2-hop inference 0.426 vs 1-hop 0.000 "
            "vs frozen-encoder 0.012 (ratio 36.5x over the 2.0x band). discriminator-real check: "
            "heldout_in_compose_graph==0 across all 3 seeds (substrate must INFER, not retrieve). "
            "1-hop=0 is exact closure baseline as designed (perfect-by-construction; "
            "frozen-encoder is the load-bearing semantic bar). per-seed 2hop: 0.415/0.425/0.4375 "
            "(cv=0.027 << 0.05); per-seed 1hop: 0.0/0.0/0.0; per-seed frozen-encoder: "
            "0.010/0.015/0.010 (cv=0.245 -- low absolute values; encoder baseline near floor). "
            "Honest scope: 8 ConceptNet relation types in en-100k vs FB15k-237's 237; OOD class = "
            "(s,p) in-KB no-edge. Composes with U1 (ingest mechanism) + EXP_kv_learned_projection "
            "(post-substrate transform survival) + KG-multihop trajectory."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "relevance_tier": "HIGH",
            "verdict": "HARD_PASS_chain_grade_conceptnet_ingest_eval_OPEN_C_unlocked",
            "run_mode": "full",
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "N_DIM": 8192,
            "M_scale_points": [5000, 10000, 25000, 50000, 100000],
            "corpus_dataset": "ConceptNet en-100k (n_ent=80181, n_rel=8, n_keys=42154 at M=100000)",
            "metrics_path": "data/exp_n8_conceptnet_ingest_eval_v1/metrics.json",
            "metrics_source": "substrate_KB_ingest_eval_ConceptNet_en100k_multi_value_hebbian_set_readout_frozen_encoder_baseline",
            "cell_commit": "8bbc11c4",
            "key_metrics": {
                "fidelity_setrecall_all_M100000_mean": 1.000,
                "fidelity_setrecall_1to1_M100000_mean": 1.000,
                "fidelity_setrecall_all_M50000_mean": 0.99990,  # (0.9997+1.0+1.0)/3
                "refuse_gate_OOD_refuse_mean": 0.9989,  # (1.0+0.9967+1.0)/3
                "refuse_gate_inkb_accept_mean": 0.9967,  # (0.9967+1.0+0.9933)/3
                "inference_2hop_mean": 0.4258,
                "inference_2hop_cv": 0.027,
                "inference_1hop_mean": 0.000,
                "inference_frozen_encoder_mean": 0.01167,
                "inference_2hop_vs_frozen_encoder_ratio": 36.50,
                "scale_curve_setrecall_all": {
                    "M5000": 1.000,
                    "M10000": 1.000,
                    "M25000": 1.000,
                    "M50000": 0.99990,
                    "M100000": 1.000,
                },
                "elapsed_s_total": 761.1,
                "heldout_in_compose_graph_per_seed": [0, 0, 0],
                "leak_skipped_per_seed": [1, 6, 10],
            },
            "honest_scope": (
                "Substrate KB-ingest on ConceptNet en-100k via multi-value Hebbian + set-readout. "
                "OPEN-C unlocked via frozen-encoder MiniLM-L6 ingest-time semantic baseline "
                "(scoring is matmul; no LLM forward calls). 8 relation types in en-100k vs "
                "FB15k-237's 237 (narrower relational vocabulary; broader entity count -- "
                "n_ent=80181 vs U1's 12838). 1-hop baseline = 0.0 by closure construction "
                "(heldout_in_compose_graph==0 -- perfect-by-construction; the load-bearing bar "
                "is frozen-encoder semantic). The 36.5x ratio is over the semantic bar, not "
                "the closure floor. OOD class = (s,p) in-KB no-edge."
            ),
            "finding": (
                "Second chain-grade KB-ingest atom after U1. ConceptNet ingests + governs + "
                "composes at a LARGER M-scale (up to 100k) than U1 (50k). The substrate is "
                "a working KB-ingest engine across at least two distinct KG corpora at chain-grade. "
                "OPEN-C unlock confirms the substrate's KG value beats the semantic-similarity bar, "
                "not just the lookup bar. 2-hop inference at substrate-scale (0.426) is 36.5x the "
                "frozen-encoder baseline (0.012) -- substrate is doing genuine compositional inference, "
                "not semantic retrieval."
            ),
            "baseline_provenance": (
                "1-hop baseline = exact closure (heldout_in_compose_graph==0; perfect-by-construction; "
                "0.0 by design). Frozen-encoder baseline = MiniLM-L6 sentence-transformer ingest-time "
                "(0.012 mean across 3 seeds). The load-bearing bar is the frozen-encoder; the closure "
                "floor is a sanity check that the eval is not retrieval-corrupted."
            ),
            "composes_with": [
                "math::T3/EXP_u1_fb15k237_ingest_eval_v1",
                "math::T3/EXP_kv_learned_projection_v1",
                "math::T3/EXP_ccc1_extra_fb15k237_kg_multihop_v1",
            ],
            "depends_on_text": (
                "Multi-value Hebbian KB-ingest; set-readout-top-k (faithful multigraph metric); "
                "margin-refuse on confidence; frozen-encoder semantic-similarity baseline (MiniLM-L6 "
                "at ingest-time only; substrate-only-decode preserved at inference)."
            ),
            "cert_vet_status": "LANDED_VET_skunkworks_2026-06-22_CERT_585_chain_grade_n8_conceptnet",
            "verified_off_data": (
                "cert-owner re-derived all cited numbers from data/exp_n8_conceptnet_ingest_eval_v1/metrics.json "
                "per-seed (seeds 7/17/23) via .venv numpy: 2hop mean = (0.415+0.425+0.4375)/3 = 0.4258; "
                "1hop mean = 0.0 (all seeds); frozen-encoder mean = (0.010+0.015+0.010)/3 = 0.01167; "
                "ratio = 0.4258/0.01167 = 36.49 ~ 36.50 (matches headline); setrecall@M100000 all=1.000 "
                "all 3 seeds; refuse OOD = (1.0+0.9967+1.0)/3 = 0.9989; accept = (0.9967+1.0+0.9933)/3 = "
                "0.9967; heldout_in_compose_graph==0 confirmed across all 3 seeds; discriminator-real "
                "(1hop is mechanism-DEAD can-fail control + frozen-encoder is HARNESS-NULL semantic-only "
                "control; both controls fire correctly)."
            ),
            "prereg": (
                "SCHEMA-VET + n8 prereg cell-commit 8bbc11c4; OPEN-C frozen-encoder semantic baseline "
                "design landed via exp_dev pre-flight (substrate-only-decode gate preserved)."
            ),
            "atomized_by": "skunkworks",
            "atomized_date": "2026-06-22",
            "era": "agent_teams_post_STANDSTILL_phase_C_live_write_n8_conceptnet_CERT_585",
            "milestone": (
                "Second chain-grade KB-ingest atom (CERT 584 -> 585). First production use of "
                "OPEN-C frozen-encoder semantic baseline (substrate-only-decode preserved; encoder "
                "is INPUT-stage only, scoring is matmul, zero LLM forward calls at inference). "
                "Path F (ingest-breadth) cert-chain extends: U1 (FB15k-237) + n8 (ConceptNet) "
                "at chain-grade."
            ),
            "open_followups": [
                "n6 WikiText-103 + n7 arxiv-abstracts (Tier-2 ingest breadth) cells pending",
                "Cross-KG transfer test: U1+n8 joint substrate -- does atom-set from one KG survive "
                "querying via the other's relation vocabulary?",
                "Robustness: refuse-gate at noisy / adversarial OOD on ConceptNet (parallel to U1's "
                "open-followup)",
            ],
            "discriminator_regime_check": (
                "Fix #16 compliance: 2hop=0.426 (mechanism-LIVE) vs 1hop=0.000 (closure baseline; "
                "mechanism-DEAD can-fail control) vs frozen-encoder=0.012 (HARNESS-NULL semantic-only "
                "control). Both control arms fire correctly; the discriminator is REAL not "
                "by-construction-saturation."
            ),
            "tier_2_ingest_breadth_anchor": True,
        },
    )


def main():
    if "--dry-run" not in sys.argv and "--apply" not in sys.argv:
        print("USAGE: skunkworks_atomize_n8_conceptnet_chain_grade_cert585_2026-06-22.py [--dry-run|--apply]")
        return 0

    atom = build_atom()
    print("=" * 80)
    print(f"{'DRY RUN' if '--dry-run' in sys.argv else 'APPLY'}: n8 ConceptNet chain-grade atom")
    print("=" * 80)
    print(f"  id: {atom.id}")
    print(f"  kind: {atom.kind.value}")
    print(f"  tier: {atom.tier.value}")
    print(f"  corpus: {atom.corpus.value}")
    print(f"  pq: {(atom.metadata or {}).get('provenance_quality')}")
    print(f"  cell_commit: {(atom.metadata or {}).get('cell_commit')}")

    if "--dry-run" in sys.argv:
        print("DRY RUN: no Store mutation.")
        return 0

    store_root = Path("data/substrate_index")
    ps = PartitionedStore(store_root)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"\nSKIP (idempotent): {qid} already present.")
        return 0

    print(f"\nADDING: {atom.id}")
    ps.add_atom(
        atom,
        source="skunkworks_atomize_n8_conceptnet_chain_grade_cert585_2026-06-22",
        note=(
            "Second chain-grade KB-ingest atom after U1 (FB15k-237). ConceptNet en-100k at "
            "M={5k,10k,25k,50k,100k} N_DIM=8192 3-seed full run. OPEN-C unlocked via frozen-encoder "
            "MiniLM-L6 semantic baseline (substrate-only-decode preserved). 36.5x 2hop ratio; "
            "discriminator-real (heldout_in_compose_graph==0). CERT 584 -> 585."
        ),
    )

    # Fresh-Store all_atoms() round-trip verify (inst-240 gate)
    ps2 = PartitionedStore(store_root)
    atoms = list(ps2.all_atoms())
    found = next((a for a in atoms if a.id == atom.id), None)
    if found is None:
        print("  FAIL: atom not found post-add")
        return 1
    if found.tier != atom.tier or found.kind != atom.kind:
        print(f"  FAIL: tier/kind mismatch")
        return 1
    md = found.metadata or {}
    if md.get("provenance_quality") != "CERT_CHAIN_GRADE":
        print(f"  FAIL: pq mismatch (got {md.get('provenance_quality')})")
        return 1
    print(f"  PASS: round-trip survival OK (Atom.from_dict clean)")

    # Verify CERT count moved 584 -> 585
    cert_n_post = sum(
        1 for a in atoms
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    print(f"  Post-write CERT count: {cert_n_post}")
    if cert_n_post != 585:
        print(f"  WARNING: CERT count is {cert_n_post}, expected 585")

    # cert_ledger row append
    ledger_row = build_chain_grade_ruling_row(
        atom_id="math::T3/EXP_n8_conceptnet_ingest_eval_v1",
        cell_commit="8bbc11c4",
        verdict="HARD_PASS",
        notes_path="notes/research_n8_conceptnet_LANDED_HARD_PASS_2026-06-22.md",
        metrics_path="data/exp_n8_conceptnet_ingest_eval_v1/metrics.json",
        cv=0.027,
        cert_class="pre_reg_pass",
        atomized_by="skunkworks",
        note=(
            "n8_conceptnet_ingest_eval_v1_chain_grade_CERT_585_second_KB_ingest_atom_after_U1_"
            "OPEN_C_frozen_encoder_unlock_36_5x_ratio_discriminator_real_heldout_in_compose_graph_zero"
        ),
    )
    row_h = append_cert_ledger_row(
        ledger_row,
        expected_cert_n_pre=584,
        expected_cert_n_post=585,
    )
    print(f"  PHASE-C ledger row appended; hash = {row_h}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
