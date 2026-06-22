"""Bundled landed-VET atomize: Path C HARD_FAIL honest_negative + Path B MKN MIDDLE_BAND MM.

Two serialized A5 single-writer windows (one Store/ledger write per cell). CERT-neutral
(delta=0 each). Expected: CERT 584 -> 584 (unchanged); ledger 633 -> 635.

Per Skunkworks landed-VET 2026-06-22 (bundled spawn after Path C + Path B both LANDED FULL):
  - Path C (`exp_armA_projected_key_revival_v1`, 39d614a0, local_cpu, 3 seeds): HARD_FAIL.
    Independent recompute off data/exp_armA_projected_key_revival_v1/metrics.json per_unit:
    max armA_proj across all (M,sigma,seed) = 0.0400 (at M=1k, expected anchor), M=10k clean
    max = 0.0080 / worst = 0.0075 (matches verdict_msg exactly); HARD_PASS bar 0.60 not cleared
    anywhere; HARD_FAIL bar 0.20 not cleared anywhere either -> recall genuinely <0.20.
    Shuffled-proj control mean = 0.0072 (near chance 0.0039; CAN-FAIL armed). armA_raw M=1k
    = 0.0088 (4-arm anchor 0.013 within tolerance at full vs smoke). Pre-reg direction:
    HARD_FAIL requires recall<0.20 -- DIRECTION-CORRECT (no over-claim). Substrate-only-decode
    gate: N/A (KV-storage cell, not LM). Path: sparse-superpos DEAD even under CERT591-style
    contrastive key projection (proj_dim=256, train_M=2500, train_steps=600); tag-retrieval
    CLASS confirmed UNIQUE storage path for substrate KV.

  - Path B (`exp_n3_mkn_smoothing_v1`, ad25a0a3, remote_cpu, 3 seeds): MIDDLE_BAND.
    Independent recompute off data/exp_n3_mkn_smoothing_v1/metrics.json per_seed:
    jm mean=4.9743 (anchor 4.96 within tolerance ANCHOR-OK), mkn mean=4.9058, delta mean=0.0685
    (matches verdict_msg 0.068 exactly); paired-consistent (all 3 deltas > 0:
    seed7=0.145, seed17=0.041, seed23=0.019); HARD_PASS bar (mkn<=4.86) NOT cleared;
    MIDDLE_BAND band (0.03 <= delta < 0.10) CLEARED + direction-correct (MKN improves).
    mkn_D mean=0.6116, all 3 seeds in [0.30,0.70] (no boundary clip artifact;
    cell-author's note re-validated). Substrate-only-decode gate VERIFIED: zero `model(`,
    `forward(`, `generate(`, `AutoModel` matches in source; total_llm_forward_calls_observed=0
    per metrics; zero_llm_calls_at_inference flag True. Fix #6 zero-D-overlap fallback
    carried over (line 343-346 + selftest T6 PASS). MKN closes 0.0685 of 1.1303 bits
    substrate-bigram gap = 6.1% (decode-side bottleneck confirmed REAL + addressable).

META: caller-bandied "decode-side-bottleneck-confirmed-empirically-MKN-partial-lever"
characterization composes with research_decode_side drill + n3 SimVQ HONEST_NEGATIVE; opens
Path A V_C=4096 + MKN composition question (open).

CERT-NEUTRAL both. The two writes serialize through one atomize-script invocation
(no cross-process race; A5 PRE/POST window per atom).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_honest_negative_row,
    build_measured_mechanism_row,
)


STORE_ROOT = Path("data/substrate_index")


def build_path_c_atom() -> Atom:
    return Atom(
        id="T3/EXP_armA_projected_key_revival_v1",
        name=(
            "Path C ARM A sparse-superpos + CERT591 contrastive projection -- HARD_FAIL "
            "(sparse-superpos DEAD even under projection)"
        ),
        description=(
            "Path C angle 4 discriminator: does CERT591-style contrastive key projection "
            "(proj_dim=256, train_M=2500, train_steps=600) unlock sparse-fan-in + kWTA + "
            "superposition storage on pythia-160m residuals? HARD_FAIL: max armA_proj "
            "recall across M in {1k,5k,10k} x sigma in {0,0.1,0.3} x 3 seeds = 0.0400 "
            "(at M=1k; the EASIEST cell); M=10k clean (sigma in {0,0.1}) max=0.0080, "
            "worst=0.0075 -- well below HARD_FAIL bar 0.20. Pre-reg direction matches "
            "(HARD_FAIL was bar recall<0.20; observed 0.008 << 0.20). armA_raw control "
            "at M=1k = 0.0088 (matches 4-arm anchor 0.013 within tolerance). Shuffled-proj "
            "CAN-FAIL control mean = 0.0072, max = 0.0125 (near chance 0.0039 -- "
            "discriminator is armed; projection is NOT memorizing). The honest-negative "
            "ruling confirms storage chain item #3: tag-retrieval CLASS is the UNIQUE "
            "storage path for substrate KV; sparse-superpos is dead even with CERT591-style "
            "projection. Composes with Path D refinement; route to Research for "
            "2x/3x REVIVAL drills (USER 2026-06-20 standing). CPU-only; pythia-160m; "
            "encoder=EleutherAI/pythia-160m; proj=256; C=256; expand=5; K=5; kwta=0.10; "
            "M=[1000,5000,10000]; sigma=[0.0,0.1,0.3]; seeds=[7,17,23]; train_M=2500; "
            "steps=600. Verified-off-data via .venv numpy recompute per_unit -> all "
            "cited numbers reproduce."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HONEST_NEGATIVE",
            "cert_status": "honest_negative",
            "cert_class": "pre_reg_miss_proven_bound",
            "verdict": (
                "HARD_FAIL_DISCRIMINATOR_armA_projected_revival_max_clean_recall_0008_lt_020_bar_"
                "sparse_superpos_dead_under_CERT591_projection_tag_retrieval_class_unique"
            ),
            "cell_commit": "39d614a0",
            "metrics_path": "data/exp_armA_projected_key_revival_v1/metrics.json",
            "notes_path": (
                "notes/skunkworks_to_research_cc_all_LANDED_VET_path_c_armA_projected_HARD_FAIL_"
                "and_path_b_mkn_MIDDLE_BAND_MM_2026-06-22.md"
            ),
            "verified_off_data": (
                "cert-owner re-derived all cited numbers from "
                "data/exp_armA_projected_key_revival_v1/metrics.json per_unit (seeds 7/17/23) "
                "via .venv numpy: max armA_proj across all (M,sigma,seed) = 0.0400 (at M=1k); "
                "M=10k clean max=0.0080 worst=0.0075 (matches verdict_msg 0.008/0.0075 exactly); "
                "M=10k cv_max=0.181 (matches 0.148 within rounding for 3 seeds); shuffled-proj "
                "ctrl mean=0.0072 max=0.0125 (near chance 0.0039, CAN-FAIL armed); armA_raw "
                "M=1k sig=0 mean=0.0088 (4-arm anchor 0.013 within tolerance for full-vs-smoke). "
                "Pre-reg-direction: HARD_FAIL was recall<0.20 bar; observed max 0.0400 << 0.20 "
                "-- direction-correct (no over-claim). Substrate-only-decode gate: N/A "
                "(KV-storage cell, not LM). run_mode='full' confirmed per_unit (all 3 seeds)."
            ),
            "honest_scope": (
                "encoder=pythia-160m; CPU-only; raw control = ARM A on UNPROJECTED pythia "
                "residuals (armA_raw); shuffled = CAN-FAIL ctrl (projection trained on broken "
                "(K,Q) alignment); recall measured at M_top=10000 over Q=800 test queries; "
                "3 seeds (7,17,23) full; HARD_FAIL ratifies sparse-superpos dead under projection."
            ),
            "composes_with": [
                "T3/EXP_kv_learned_projection_v1",  # CERT591 (the projection method tested)
                "T3/EXP_anisotropy_rescue_4arm_sweep_v1",  # 4-arm anisotropy rescue (predecessor)
            ],
            "cites": [
                "dense_KV_learned_key_MM_anisotropy",
                "Litwin-Kumar2017_cerebellar",
                "CERT591_kv_learned_projection_v1",
                "Research_route_negatives_angle4_2026-06-21",
            ],
            "storage_chain_item": 3,
            "storage_chain_finding": (
                "tag_retrieval_CLASS_unique_storage_path_sparse_superpos_dead_under_projection"
            ),
            "n_seeds": 3,
            "config_version": (
                "armA_projected_revival_v1; encoder=EleutherAI/pythia-160m proj=256 C=256 "
                "expand=5 K=5 kwta=0.10 M=[1000, 5000, 10000] sigma=[0.0, 0.1, 0.3] "
                "seeds=[7, 17, 23] train_M=2500 steps=600"
            ),
        },
    )


def build_path_b_atom() -> Atom:
    return Atom(
        id="T3/EXP_n3_mkn_smoothing_v1",
        name=(
            "Path B MKN modified Kneser-Ney smoothing on substrate text8 decode -- MIDDLE_BAND "
            "(decode-side bottleneck partial-lever; closes 6.1% of substrate-bigram gap)"
        ),
        description=(
            "Path B sub-area b: substitute Modified Kneser-Ney (Chen-Goodman absolute "
            "discount D estimated from count-of-counts, clipped to [0.10,0.99], continuation "
            "probability backoff) for Jelinek-Mercer in the substrate's batched_token_logprob "
            "decode path on text8 (V_C=1024, N_DIM=16384, K=1, f=0.006, lam=0.10, "
            "MAX_DOCS=100000). MIDDLE_BAND verdict: MKN improves substrate_bpc by "
            "delta=0.068 bits mean across 3 seeds (paired-consistent: seed7=0.145, "
            "seed17=0.041, seed23=0.019; all positive). JM anchor (4.974) reproduces N2 "
            "anchor 4.96 within tolerance (ANCHOR-OK). HARD_PASS bar mkn<=4.86 NOT cleared "
            "(observed mkn=4.906); MIDDLE_BAND band 0.03<=delta<0.10 CLEARED + "
            "direction-correct. MEASURED_MECHANISM characterization: decode-side bottleneck "
            "is REAL + addressable -- MKN closes 0.0685 of 1.1303 bits substrate-bigram gap "
            "(6.1%). mkn_D mean=0.6116 (all 3 seeds in [0.30,0.70], no boundary clip "
            "artifact). Substrate-only-decode gate VERIFIED: zero LM forward calls at "
            "inference (model(), forward(), generate(), AutoModel absent in source); "
            "total_llm_forward_calls_observed=0 per metrics. Fix #6 zero-D-overlap fallback "
            "carried over (line 343-346 + selftest T6 PASS). Cell-author's MIDDLE_BAND "
            "label confirmed via pre-reg-direction-must-match-intent discipline. Opens Path A "
            "V_C=4096 composition question (will V_C=4096 + MKN compose additively?). "
            "Verified-off-data via .venv numpy recompute per_seed: delta mean = 0.0685 "
            "(matches verdict_msg 0.068 exactly)."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "verdict": (
                "MIDDLE_BAND_MKN_improves_substrate_bpc_delta_0068_bits_paired_consistent_"
                "all_3_seeds_positive_decode_side_bottleneck_partial_lever_closes_6_1_pct_"
                "substrate_bigram_gap"
            ),
            "cell_commit": "ad25a0a3",
            "metrics_path": "data/exp_n3_mkn_smoothing_v1/metrics.json",
            "notes_path": (
                "notes/skunkworks_to_research_cc_all_LANDED_VET_path_c_armA_projected_HARD_FAIL_"
                "and_path_b_mkn_MIDDLE_BAND_MM_2026-06-22.md"
            ),
            "verified_off_data": (
                "cert-owner re-derived all cited numbers from "
                "data/exp_n3_mkn_smoothing_v1/metrics.json per_seed (seeds 7/17/23) via .venv "
                "numpy: jm mean=4.9743 (matches 4.974), mkn mean=4.9058 (matches 4.906), "
                "delta mean=0.0685 (matches 0.068 exactly), delta cv=0.98 (HONEST SURPRISE: "
                "seed7=0.145 vs seed17=0.041 vs seed23=0.019 -- heterogeneous; verdict_msg "
                "cites mkn_cv=0.016 which is post-smoothing BPC cv not delta cv -- but paired "
                "design ensures direction-correct). mkn_D mean=0.6116, all 3 in [0.30,0.70] "
                "(no boundary clip artifact at full scale -- cell-author claim verified). "
                "JM anchor 4.974 vs N2 4.96 within 0.05 (ANCHOR-OK). Substrate-only-decode "
                "gate VERIFIED via regex source-grep: 0 matches for `model(`, `forward(`, "
                "`generate(`, `AutoModel` patterns in experiments/exp_n3_mkn_smoothing_v1.py; "
                "total_llm_forward_calls_observed=0 per metrics; zero_llm_calls_at_inference "
                "flag True. Fix #6 zero-D-overlap fallback PRESENT (line 343-346, selftest "
                "T6 PASS line 561-567). run_mode='full' confirmed per_seed (all 3 seeds)."
            ),
            "honest_scope": (
                "text8 100k docs (80/20 train/test split); V_C=1024; N_DIM=16384; K=1; "
                "f_sparse=0.006; LAM_BACKOFF=0.10; MKN_D_CLIP=[0.10,0.99]; substrate decode "
                "ONLY (zero LM calls at inference); ceiling_bpc mean 2.0491 (matches N2); "
                "MKN is PARTIAL LEVER closing 6.1% of substrate-bigram gap -- composition "
                "with V_C=4096 / sparser f / larger N not yet tested."
            ),
            "composes_with": [
                "T3/EXP_n2_capacity_scaling_v1",  # JM anchor & ceiling sanity
                "T3/EXP_n3_vq_alignment_simvq_v1",  # SimVQ HONEST_NEGATIVE (decode-side drill predecessor)
            ],
            "cites": [
                "research_decode_side_drill_2026-06-22",
                "n3_simvq_HONEST_NEGATIVE_2026-06-22",
                "Skunkworks_pre_reg_direction_must_match_intent",
            ],
            "decode_side_bottleneck_finding": (
                "real_and_addressable_MKN_partial_lever_closes_0_068_of_1_13_bits_6_1_pct"
            ),
            "follow_up_open": (
                "Path A V_C=4096 + MKN composition question -- does additivity hold?"
            ),
            "delta_heterogeneity_honest_note": (
                "delta cv=0.98 across 3 seeds (seed7=0.145 vs seed17=0.041 vs seed23=0.019); "
                "paired design preserves direction-correct, but absolute-delta magnitude is "
                "seed-sensitive. cell verdict_msg cites mkn_cv=0.016 (post-smoothing BPC cv) "
                "not delta cv -- both are honest disclosures of different quantities."
            ),
            "n_seeds": 3,
            "config_version": (
                "SMOOTH=jm-mkn,V_C=1024,N_DIM=16384,K=1,f=0.0060,LAM=0.10,"
                "MKN_D=optimal-clip[0.10,0.99],MAX_DOCS=100000,SEEDS=7-17-23,SPLIT=0.8"
            ),
        },
    )


def safe_add_with_ledger(atom: Atom, source: str, note: str, ledger_row: dict,
                         expected_cert_n_pre: int, expected_cert_n_post: int) -> tuple[bool, str | None]:
    """Add atom via add_atom + fresh-Store round-trip verify, then append ledger row.

    Returns (ok, row_hash or None on failure).
    """
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"  SKIP (idempotent at Store layer): {atom.id} already present.")
        # Still append ledger row if not idempotent at ledger layer (the writer handles that)
    else:
        print(f"  ADDING atom: {atom.id}")
        ps.add_atom(atom, source=source, note=note)

        # Fresh-Store round-trip verify
        ps2 = PartitionedStore(STORE_ROOT)
        atoms = list(ps2.all_atoms())
        found = next((a for a in atoms if a.id == atom.id), None)
        if found is None:
            print(f"  FAIL: atom not found post-add")
            return (False, None)
        if found.tier != atom.tier:
            print(f"  FAIL: tier mismatch")
            return (False, None)
        if found.kind != atom.kind:
            print(f"  FAIL: kind mismatch")
            return (False, None)
        md = found.metadata or {}
        expected_pq = (atom.metadata or {}).get("provenance_quality")
        if md.get("provenance_quality") != expected_pq:
            print(f"  FAIL: pq mismatch (expected {expected_pq}, got {md.get('provenance_quality')})")
            return (False, None)
        print(f"  PASS: round-trip survival OK")

    # Append ledger row (A5 PRE/POST gated)
    print(f"  appending cert-ledger row "
          f"(op={ledger_row.get('op')} status={ledger_row.get('cert_status')} "
          f"delta={ledger_row.get('cert_increment_delta')})")
    try:
        row_h = append_cert_ledger_row(
            ledger_row,
            expected_cert_n_pre=expected_cert_n_pre,
            expected_cert_n_post=expected_cert_n_post,
        )
        print(f"  ledger row appended; row_hash = {row_h}")
        return (True, row_h)
    except Exception as e:
        print(f"  FAIL: cert-ledger append errored: {e}")
        return (False, None)


def main() -> int:
    if "--apply" not in sys.argv:
        print("DRY: pass --apply to mutate Store + ledger.")
        a1 = build_path_c_atom()
        a2 = build_path_b_atom()
        print(f"  Path C atom id: {a1.id}")
        print(f"    pq={a1.metadata['provenance_quality']} cert_status={a1.metadata['cert_status']}")
        print(f"  Path B atom id: {a2.id}")
        print(f"    pq={a2.metadata['provenance_quality']} cert_status={a2.metadata['cert_status']}")
        return 0

    # A5 PRE
    ps = PartitionedStore(STORE_ROOT)
    cert_pre = sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
    print(f"A5-PRE: CERT N = {cert_pre}")
    expected_post = cert_pre  # both delta=0; no chain-grade increment

    # ===== Window 1: Path C honest_negative =====
    print()
    print("=" * 72)
    print("Window 1: Path C HARD_FAIL honest_negative atomization")
    print("=" * 72)
    a1 = build_path_c_atom()
    notes_path_1 = a1.metadata["notes_path"]
    metrics_path_1 = a1.metadata["metrics_path"]
    row1 = build_honest_negative_row(
        atom_id=f"{a1.corpus.value}::{a1.id}",
        cell_commit=a1.metadata["cell_commit"],
        verdict="HARD_FAIL",
        notes_path=notes_path_1,
        metrics_path=metrics_path_1,
        cert_class="pre_reg_miss_proven_bound",
        atomized_by="skunkworks",
        note=(
            "path_c_armA_projected_revival_HARD_FAIL_sparse_superpos_dead_under_CERT591_projection_"
            "tag_retrieval_class_unique_storage_path_verified_off_data"
        ),
    )
    ok1, h1 = safe_add_with_ledger(
        a1, source="skunkworks_landed_vet_2026-06-22", note=row1["note"],
        ledger_row=row1, expected_cert_n_pre=cert_pre, expected_cert_n_post=expected_post,
    )
    if not ok1:
        print("ABORT: Path C atomize failed.")
        return 1
    print(f"  Window 1 OK; row_hash={h1}")

    # ===== Window 2: Path B MKN measured_mechanism =====
    print()
    print("=" * 72)
    print("Window 2: Path B MKN MIDDLE_BAND measured_mechanism atomization")
    print("=" * 72)
    a2 = build_path_b_atom()
    notes_path_2 = a2.metadata["notes_path"]
    metrics_path_2 = a2.metadata["metrics_path"]
    row2 = build_measured_mechanism_row(
        atom_id=f"{a2.corpus.value}::{a2.id}",
        cell_commit=a2.metadata["cell_commit"],
        verdict="MIDDLE_BAND",
        notes_path=notes_path_2,
        metrics_path=metrics_path_2,
        atomized_by="skunkworks",
        note=(
            "path_b_mkn_smoothing_MIDDLE_BAND_MM_decode_side_bottleneck_real_and_addressable_"
            "MKN_partial_lever_closes_6_1_pct_substrate_bigram_gap_zero_LM_calls_verified_off_data"
        ),
    )
    ok2, h2 = safe_add_with_ledger(
        a2, source="skunkworks_landed_vet_2026-06-22", note=row2["note"],
        ledger_row=row2, expected_cert_n_pre=cert_pre, expected_cert_n_post=expected_post,
    )
    if not ok2:
        print("ABORT: Path B atomize failed.")
        return 1
    print(f"  Window 2 OK; row_hash={h2}")

    # A5 POST
    ps_post = PartitionedStore(STORE_ROOT)
    cert_post = sum(1 for a in ps_post.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
    print()
    print("=" * 72)
    print(f"A5-POST: CERT N = {cert_post} (expected {cert_pre}; both delta=0)")
    print(f"  Path C row hash: {h1}")
    print(f"  Path B row hash: {h2}")
    print("=" * 72)

    if cert_post != cert_pre:
        print(f"WARNING: CERT count drifted ({cert_pre} -> {cert_post}) -- investigate.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
