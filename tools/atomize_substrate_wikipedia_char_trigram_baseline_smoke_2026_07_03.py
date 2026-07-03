"""
A5-gated atomize: substrate-native char-trigram Wikipedia baseline SMOKE HARD_PASS.

CELL: experiments/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026-07-03.py (a71920bbf)
ANCHOR: substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03
METRICS: data/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03/metrics.json

OFF-DATA INDEPENDENT RECOMPUTE (skunkworks VET, off metrics.json not verdict_msg):
  ARM_CHAR_TRIGRAM_WIKIPEDIA per-seed r@5: [0.854, 0.854, 0.854]
    -> mean 0.854, std 0.000 (deterministic-by-blake2b-codebook; std=0 by construction, NOT a bug)
    -> HP1 (r@5 >= 0.60) clears with 0.254 headroom -> HARD_PASS correct
    -> per-seed intra_body_title_cos identical 0.20916 (encoder-deterministic)
    -> encoding_wall_s mean 1.439 (matches quote 1.44); throughput 349.68 art/sec (matches 349)
  ARM_RANDOM_BASELINE per-seed r@5: [0.002, 0.014, 0.006]
    -> mean 0.00733, std 0.00499 (stochastic clean; chance floor 0.01)
    -> in-band [0, 0.05]: 0.00733 < 0.05 -> baseline_in_band=True correct (META_RULE_AG)
  arms_differ_verified: per-seed arm digests distinct in all 3 seeds
    (char_trigram 591c3a5be65600cf constant across seeds; random {e2ec.., 4fc1.., 4508..} distinct)
  cardinality_ok: expected 6 = 2 arms x 3 seeds; actual 6; True
  positive-control:
    (a) char_trigram determinism selftest -- std=0 across seeds is REQUIRED evidence (not defect)
    (b) random baseline stochastic std 0.005 confirms scoring/matrix wiring is real

CELL-AUTHOR FRAMING AUDIT:
  verdict_msg: "HONEST SCOPE: title-body char-trigram overlap dominates; does NOT
    grant substrate general-knowledge of Wikipedia content"
  Scope discipline CLEAN. No "understand"/"know" overreach. Cell-author explicitly
  respects USER-locked "substrate knows almost nothing" (2026-07-02) framing.
  gap-to-bge=+0.138 (0.992 - 0.854) at CROSS-SCALE (100K bge vs 500 char_trigram)
  is a MEASURED gap number, presented as "residual capability headroom" not
  as a capability claim. Skunkworks concurs.

CROSS-ARC OVERLAP CHECK (substrate-KB v2 query 2026-07-03):
  Q "char trigram wikipedia title body retrieval substrate native":
    top-1 cosine=0.3789 -> Anchor "substrate_wikipedia_nq_triviaqa_retrieval_v1"
      (2026-06-07 planning note; NOT prior char-trigram probe)
    top-2 cosine=0.3311 -> REVIVAL_SUBSTRATE_NATIVE_ONLY (2026-06-10 note; general policy)
    top-3 cosine=0.3242 -> P2.1 pgvector-substrate retrieval planning (2026-06-11 drill)
  Direct grep: no prior atom contains "ARM_CHAR_TRIGRAM_WIKIPEDIA" or
    "char_trigram_wikipedia" substring. Genuinely novel as a substrate-native
    NON-bge dedicated 3-seed floor cell on real Wikipedia.
  CLOSEST PRIOR: 2026-07-02 apples-to-apples cell
    (exp_substrate_concept_encoder_wikipedia_10k_apples_to_apples_v1) ran
    ARM_CHAR_TRIGRAM_UNSUP as 1 of 4 arms at 1 seed and got r@5=0.872
    (SMOKE_PARTIAL_INFO_SKIPPED_ARMS -- bge arm not run; concept_encoder failed).
    Today's 3-seed r@5=0.854 is CONSISTENT with that partial-info 0.872 measurement.
    This cell HARDENS the finding: (a) 3-seed stable, (b) explicit random control
    clearing baseline_in_band, (c) dedicated cell not one-of-four with partial-info
    verdict.
  META atom "META_aggressive_competitive_hebbian_sparsification_k_0p02_LOSES_to_
    bag_of_char_trigram_on_real_symbolic_content_retrieval" (2026-07-02) already
    captures the cross-arc "task-class matters -- bag-of-char-trigram wins on real
    content" synthesis. No new META atom filed here to avoid duplicate.

TIER RULING:
  math atom: CG_MEASURED_BOUND at TIGHT SCOPE.
    Rationale for CG despite SMOKE tier:
      - HP1 clears with wide (0.254) headroom
      - 3-seed cross-seed variance clean: char_trigram std=0 by-construction
        (deterministic encoder), random std 0.005 stochastic clean
      - cardinality 6/6; arms_differ_verified True
      - positive control (random baseline in band) clears META_RULE_AG
      - framing scoped honestly by cell-author (verdict_msg + prereg)
      - prior apples-to-apples 1-seed 0.872 confirms independent-mechanism-real
    Scope BOUND (explicit in atom name):
      - N=500 Wikipedia SMOKE only (no FULL variant; scale-up needed)
      - title -> article body retrieval task ONLY
      - char-trigram mechanism ONLY (no other surface encoder tested here)
      - NOT a general-knowledge or capability claim
    Precedent: 2026-07-02 substrate_content_v1_CG_HONEST_NEGATIVE + component_C
      HF_smoke are CG-at-smoke-tier precedents when finding is clean + 3-seed +
      scope-bound.

  META atom: none filed (already-atomized 2026-07-02 competitive_hebbian_LOSES_to_
    bag META already synthesizes the "task-class matters" cross-arc finding at
    MM_TENTATIVE_SYNTHESIS; adding a second META atom would be redundant.
    Amendment to existing META recommended if apples-to-apples FULL lands: promote
    that MM_TENTATIVE -> MM_STANDARD with 3-seed hardened bar as second witness.

STRATEGIC IMPLICATION (audit-only observation, not dispatch direction):
  0.854 r@5 at N=500 SMOKE is a MUCH STRONGER floor than the 5x drill assumed
  (drill assumed char-trigram would be weak enough that VWFA + late-combine v3
  had clear justification). If char-trigram at N=10K holds anywhere above ~0.5,
  v3-composed must prove itself against a genuinely strong floor. If char-trigram
  DEGRADES sharply at N=10K, Spoke 3 (hippocampal consolidation) becomes
  load-bearing. Characterizing the scaling curve BEFORE dispatching v3-composed
  Wikipedia is HIGH_EV per cell-author's own read.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03"
CELL_COMMIT = "a71920bbf"
TS_ISO = "2026-07-03T02:10:00Z"

atom_math_CG = {
    "id": (
        "T3/EXP_substrate_wikipedia_char_trigram_baseline_SMOKE_CG_MEASURED_BOUND_"
        "3seed_N500_r5_0p854_std_0p000_deterministic_encoder_by_blake2b_codebook_"
        "vs_random_r5_0p007_baseline_in_band_HP1_0p60_cleared_with_0p254_headroom_"
        "substrate_native_char_trigram_bag_of_overlapping_3grams_bipolar_HD_sum_bundled_signed_"
        "title_to_article_body_retrieval_real_wikipedia_corpus_500_articles_body_cap_800_chars_"
        "cardinality_6of6_arms_differ_verified_intra_cos_0p209_inter_cos_0p034_snr_6p1_"
        "throughput_349_art_per_sec_wall_1p44s_per_seed_2048_dim_"
        "SCOPE_TIGHT_wikipedia_title_body_smoke_only_NOT_general_knowledge_claim_"
        "substrate_knows_almost_nothing_USER_LOCKED_framing_respected_"
        "hardens_2026_07_02_apples_to_apples_partial_info_1seed_0p872_char_trigram_arm_"
        "gap_to_bge_reference_plus_0p138_at_cross_scale_100k_vs_500_MEASURED_"
        "fork_of_wikipedia_ingest_bge_encoder_replacement_probe_no_production_modification_"
        "2026-07-03"
    ),
    "name": (
        "substrate-native char-trigram Wikipedia title->body retrieval SMOKE CG "
        "(N=500, 3-seed, r@5=0.854)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Substrate-native char-trigram surface encoder (bag of overlapping 3-grams "
        "-> per-trigram bipolar HD codebook seeded from blake2b(trigram) -> "
        "sum-bundled and signed) achieves r@5=0.854 (std 0.000 across seeds 11/17/23; "
        "deterministic by construction of the codebook) on N=500 real Wikipedia "
        "articles at N_DIM=2048 body-cap 800 chars for held-out title -> article "
        "body retrieval. Random-bipolar baseline r@5=0.00733 (chance floor 0.01; "
        "in-band [0, 0.05]; META_RULE_AG cleared). HP1 (r@5 >= 0.60) cleared with "
        "0.254 headroom -> HARD_PASS. cardinality 6/6 (2 arms x 3 seeds); "
        "arms_differ_verified True (char_trigram digest 591c3a5b constant, random "
        "digests distinct); intra-article body-title cos 0.209 vs inter-article "
        "0.034 -> SNR 6.1. Throughput 349 art/sec, wall 1.44 s/seed. Substrate-KB "
        "cross-arc check clean (top hit cosine 0.379 -> unrelated planning note; "
        "no prior atom contains char_trigram_wikipedia substring; closest prior is "
        "2026-07-02 apples-to-apples 1-seed 0.872 SMOKE_PARTIAL_INFO cell, which "
        "this hardens). CROSS-SCALE gap to bge reference (r@5=0.992 at 100K, "
        "2026-06-19) = +0.138 -- MEASURED, presented as capacity headroom, not "
        "capability claim. TIGHT SCOPE (explicit): Wikipedia title-body retrieval "
        "SMOKE only, N=500 only, char-trigram mechanism only; NOT a general "
        "knowledge or capability claim. Substrate has NO general knowledge "
        "ingested (USER-locked 2026-07-02); this cell is a MECHANISM PROBE that "
        "title-body character-trigram overlap dominates for Wikipedia article "
        "retrieval -- a bag-favorable task-class. Cell-author framing discipline "
        "clean (no understand/know overreach in verdict_msg or prereg)."
    ),
    "provenance": {
        "cell": "experiments/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026-07-03.py",
        "commit": CELL_COMMIT,
        "prereg": "preregs/2026-07-03_substrate_wikipedia_char_trigram_baseline_smoke.md",
        "anchor": "substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03",
        "metrics_path": "data/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03/metrics.json",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
    },
    "composes": [
        "T3/EXP_substrate_concept_encoder_substrate_content_v1_CG_HONEST_NEGATIVE_smoke_N100_3seed_HF2_mechanism_below_both_surface_baselines_concept_encoder_r5_0p160_char_positional_0p210_char_trigram_0p280_gap_neg_0p120_spoke1_v3D_synthetic_CG_mechanism_does_NOT_TRANSFER_to_substrate_WordNet_held_out_synonym_retrieval_aggressive_competitive_hebbian_k_0p02_discards_cheap_surface_signal_bag_of_char_trigram_wins_positive_control_ct_5p6x_chance_substantive_negative_not_test_design_failure_unanimous_direction_3_seeds_stage4_caveat_c_real_corpus_transfer_confirmed_2026-07-02"
    ],
}

ledger_math_CG = {
    "atom_id": atom_math_CG["id"],
    "corpus": "math",
    "tier": "T3",
    "disposition": "CG_MEASURED_BOUND",
    "cert_delta": {"CG": 1, "MM": 0, "HF": 0},
    "provenance": atom_math_CG["provenance"],
    "notes": (
        "SMOKE-tier CG at TIGHT SCOPE. HP1 cleared 0.254 headroom; 3-seed stable "
        "(deterministic encoder std=0 by construction, NOT a bug); random baseline "
        "in-band (0.007 < 0.05); cardinality 6/6; arms_differ True. Independent "
        "recompute off metrics.json (Fix#28); cell-author verdict_msg framing "
        "clean (no understand/know overreach). Precedent for CG-at-smoke: "
        "2026-07-02 substrate_content_v1_CG_HONEST_NEGATIVE + component_C. "
        "No META atom filed -- 2026-07-02 competitive_hebbian_LOSES_to_bag META "
        "already synthesizes the task-class-matters cross-arc finding at "
        "MM_TENTATIVE. Cross-arc query clean (top cosine 0.379 -> unrelated). "
        "Substrate-KB v2 concept-overlap check performed per USER-locked "
        "2026-07-01 rule."
    ),
    "ts_iso": TS_ISO,
    "atomized_by": ATOMIZED_BY,
}


def append_jsonl_a5(path: Path, new_row: dict, label: str) -> int:
    pre_lines = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id")

    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    import time as _time
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            _time.sleep(0.1 * (2 ** _attempt))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1

    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"]

    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    append_jsonl_a5(MATH_ATOMS, atom_math_CG,
                    "math/atoms (substrate-native char-trigram Wikipedia SMOKE CG)")
    append_jsonl_a5(CERT_LEDGER, ledger_math_CG,
                    "cert_ledger (CG_MEASURED_BOUND +1)")
    print(f"[A5] DONE OK")
    print(f"[A5] substrate-native char-trigram Wikipedia SMOKE CG_MEASURED_BOUND (+1 CG)")
    print(f"[A5] Cell commit: {CELL_COMMIT}")


if __name__ == "__main__":
    main()
