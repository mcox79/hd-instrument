"""Skunkworks landed-VET atomize: char_trigram + g1b-SubstrateGenerator composition
on HotpotQA -- MEASURED_MECHANISM (re-scoped per Director ratification 2026-06-22).

CONTEXT (A5 role-separation):
  Cell `substrate_native_qa_hotpotqa_v1` (commit 1115ac3b) was landed by exp_dev with
  verdict HARD_FAIL per its own pre-registered bands (composed_em=0.010 < HARD_FAIL bar
  0.10; lift_composed_vs_best_primitive=-0.112; cv_composed_em=0.091). Director's
  initial framing ("g1b SubstrateGenerator @ 12.2% = substrate-as-LLM-substitute existence
  proof") was overstated by attributing the GENERATION_ONLY arm signal to g1b alone
  without acknowledging (a) the cell's own composition bars HARD_FAIL'd by 9x, and
  (b) GENERATION_ONLY in this cell is "char_trigram nearest-neighbor + g1b generator"
  not g1b autonomous. Skunkworks held the original chain-grade-meta atomization request
  (DEFERRED VET) per A5; Director RATIFIED 2026-06-22 a re-scoped MEASURED_MECHANISM atom
  with CERT-delta=0, the narrower claim text below.

CERT-OWNER DISPOSITION (cert-owner-overrides-Director per A5 + verify-the-referent):
  Director's ratified claim text includes a 4-part decomposition (5.5pp char_trigram-
  nearest-name retrieval contribution, 6.7pp marginal generation-stage lift, random-start
  EM=0%, bridge-only EM=7.8%, per-100-most-common EM=23.6% vs rare EM=8.7% / 2.7x freq-
  bias enrichment). I verified `data/exp_substrate_native_qa_hotpotqa_v1/metrics.json`
  contains the headline number (mean_em GENERATION_ONLY = 0.1223, cv = 0.00385, per-seed
  EM = 0.123/0.122/0.122) and the HARD_FAIL composition (composed_em=0.010 vs
  generation_only_em=0.122 lift=-0.112). The 4-part decomposition (random-start probe,
  bridge-only, freq-bias breakdown) is NOT present in the committed metrics artifact.
  Per verify-the-referent + Fix #28-class discipline (don't ratify Director-cited numbers
  the auditor can't reproduce from data on disk), I am atomizing ONLY the data-verifiable
  scope and EXPLICITLY noting in honest_scope which Director-cited pieces are not yet
  data-backed. Those pieces would lift to data-verified if a separate C5-probe cell is
  spawned + landed; until then the atom carries the narrower honest claim.

RATIFIED ATOM CLAIM (data-verifiable subset):
  "char_trigram-encoder + g1b-SubstrateGenerator GENERATION_ONLY arm achieves 12.2% +-
   0.05% EM (cv=0.004, n_seeds=3, N_Q=1000 HotpotQA-distractor dev) with zero LLM calls
   at inference (n_llm=0). Cell's pre-registered COMPOSED arm (retrieval x generation
   composition) HARD_FAIL'd (composed_em=0.010 << HARD_FAIL bar 0.10; lift -0.112);
   the substantive measured outcome is the GENERATION_ONLY-arm alone-mean stability,
   NOT a composition-level claim. The 12.2% is the GENERATION_ONLY-arm headline on
   HotpotQA-distractor; mechanism is char_trigram nearest-entity-name retrieval +
   g1b SubstrateGenerator stack."

CERT TIER: MEASURED_MECHANISM (NOT chain-grade-meta).
CERT CLASS: mechanism_characterization.
CERT DELTA: 0 (MEASURED_MECHANISM does not increment CERT count; substrate stays at
  CERT 590).

WHY NOT CHAIN-GRADE-META (Director rationale, ratified):
  1. Cell's own pre-reg HARD_PASS bar (COMPOSED EM >= 0.20 + lift >= 0.05) HARD_FAIL'd;
     post-hoc reframing to GENERATION_ONLY is by-construction-saturation per banked
     discipline; cannot be chain-grade-meta.
  2. Director's original framing ("substrate-as-LLM-substitute existence proof") over-
     attributes; the cell measures char_trigram-encoder + g1b composition, not g1b-
     autonomous QA performance. The substrate_native_qa_v2 (composition-fix) drill is
     queued in Research's revival lane; IF v2 lands HARD_PASS (different score-fusion;
     pre-registered + new cell + discriminating), THAT is the chain-grade-meta candidate.
  3. MEASURED_MECHANISM captures the data-verifiable outcome honestly: 12.2% +- 0.05%
     EM on a generation-only arm at zero LLM calls is genuinely measured + stable
     (cv=0.004 well below cv_max=0.10) and non-trivial; it just isn't a chain-grade
     composition-level claim.

WHY NOT HELD_OTHER_CONCERN:
  Director cross-referenced the cell's metrics, ratified the MM scope explicitly, and
  authorized atomization at delta=0. No new mechanism / data / cert-architecture concern
  blocks ratification at the narrower scope. The Director-cited decomposition pieces
  (random-start, bridge-only, freq-bias) are noted as not-yet-data-verified in honest_
  scope; this is transparency about audit boundaries, not a hold.

VERIFIED-OFF-DATA (.venv numpy recompute off the metrics.json):
  - n_seeds=3 (7, 17, 23); N_DIM=8192; N_Q=1000; TOP_K=5; GEN_DEPTH=4
  - run_mode='full' (per_seed); device=cuda
  - n_llm_calls=0 (substrate-only-decode gate enforced)
  - per-arm across-seed mean_em:
      SUBSTRATE_COMPOSED = 0.0103  cv = 0.0912
      RETRIEVAL_ONLY     = 0.0103  cv = 0.0912
      GENERATION_ONLY    = 0.1223  cv = 0.00385
  - per-seed GENERATION_ONLY: seed7=0.123, seed17=0.122, seed23=0.122
    (re-derived: mean = 0.12233, std = 0.000471, cv = 0.00385)
  - composed_em=0.0103 < HARD_FAIL_bar=0.10 -> cell verdict HARD_FAIL on own bars
  - lift_composed_vs_best_primitive = -0.112 (COMPOSED is WORSE than GENERATION_ONLY)
  - per-arm mean_retrieval_recall_at_5: COMPOSED=0.019, RETRIEVAL_ONLY=0.019
  - per-arm mean_generation_n_distinct: COMPOSED=3.994, RETRIEVAL_ONLY=1.000,
    GENERATION_ONLY=3.988 (generator producing diverse but mostly-wrong answers)
  - elapsed per seed: 271.83s + 360.40s + 497.84s = total 1130.83s
  - config_version baked verbatim: 'substrate-native-qa-hotpotqa-v1: N_DIM=8192 N_Q=1000
    TOP_K=5 GEN_DEPTH=4 arms=SUBSTRATE_COMPOSED,RETRIEVAL_ONLY,GENERATION_ONLY sigma=0.100
    run_mode=full device=cuda; bands HP_composed_em=0.20 HP_lift=0.05 HF_composed_em=0.10
    cv_max=0.10'

NOT VERIFIED-OFF-DATA (Director-cited but absent from metrics.json):
  - 5.5pp char_trigram-encoder nearest-entity-name retrieval decomposition
  - 6.7pp marginal generation-stage lift conditional on retrieval start
  - random-start EM = 0% (C5 probe; not in metrics)
  - bridge-only EM = 7.8% (per-question-class breakdown; not in metrics)
  - per-100-most-common-answers EM = 23.6%; rare-answers EM = 8.7%; 2.7x freq-bias
    enrichment (frequency-bin probe; not in metrics)
  These would require a separate C5-probe cell to land + write metrics; explicitly
  flagged not-yet-data-verified in honest_scope.

COMPOSITION:
  - g1b standalone (T3/EXP_g1b_capacity_sweep_v1, CERT 587): chain-grade generation
    mechanism. This MM atom OBSERVES the g1b stack composed with char_trigram-encoder
    achieves 12.2% EM on HotpotQA generation-only; does NOT extend g1b's chain-grade
    scope beyond its CERT 587 conditions.
  - h_hotpotqa KG ingest (T3/EXP_h_hotpotqa_ingest_v1, CERT 588): provides the corpus
    + KG structure. This MM atom uses the same HotpotQA dev split; references h_hotpotqa
    as the corpus precedent.
  - char_trigram_encoder (hdlab/ primitive): underlies the GENERATION_ONLY arm.
  - Designed-revival follow-up: substrate_native_qa_v2 composition-fix drill
    (notes/research_substrate_native_qa_2x_revival_composition_fix_drill_2026-06-22.md)
    will retry composition with different score-fusion; if HARD_PASS that is the
    chain-grade-meta candidate (not this v1 MM atom).

Disciplines honored:
  - Foreground execution (Fix #20)
  - Path-scoped commits (no git add -A)
  - Idempotency: round-trip Store verify post-add
  - A5 PRE/POST snapshot via cert_ledger_writer.append_cert_ledger_row
  - verify-the-referent: only data-verifiable claims atomized; Director-cited decomposition
    explicitly flagged as not-yet-data-verified in honest_scope
  - delta=0 ledger-writer pattern: expected_cert_n_pre == expected_cert_n_post = 590
    (live CERT count after add_atom for MM; add_atom does NOT move CERT N since
    provenance_quality is MEASURED_MECHANISM not CERT_CHAIN_GRADE)

ASCII-only.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_measured_mechanism_row,
)


STORE_ROOT = Path("data/substrate_index")


def build_atom() -> Atom:
    return Atom(
        id="T3/EXP_substrate_native_qa_hotpotqa_v1_MM",
        name=(
            "substrate_native_qa_hotpotqa_v1 char_trigram+g1b composition on HotpotQA "
            "-- MEASURED_MECHANISM (re-scoped: cell HARD_FAIL on own COMPOSED bars; "
            "GENERATION_ONLY arm 12.2% +- 0.05% EM cv=0.004 zero-LLM)"
        ),
        description=(
            "Re-scoped MEASURED_MECHANISM characterization of the substrate_native_qa_"
            "hotpotqa_v1 cell (commit 1115ac3b). Cell pre-registered HARD_PASS bar was "
            "composed_em >= 0.20 + lift >= 0.05 (composition over retrieval x generation); "
            "cell verdict HARD_FAIL with composed_em=0.010 << HF bar 0.10 and lift=-0.112 "
            "(COMPOSED is WORSE than GENERATION_ONLY alone). The data-verifiable measured "
            "outcome retained from the run is the GENERATION_ONLY-arm headline: across 3 "
            "seeds at N_DIM=8192, N_Q=1000 HotpotQA-distractor dev, char_trigram-encoder "
            "+ g1b SubstrateGenerator achieves mean_em = 0.1223 with cv = 0.00385 (per-"
            "seed: 0.123/0.122/0.122), at n_llm_calls=0 (substrate-only-decode gate). This "
            "is NOT a chain-grade composition claim (cell's own composition HARD_FAIL'd) "
            "and NOT a g1b-autonomous-QA claim (the 12.2% comes from char_trigram-nearest-"
            "entity-name + g1b stack, not g1b alone). This atom honestly captures the "
            "measured mechanism: the char_trigram + g1b stack achieves seed-stable 12.2% EM "
            "on a real multi-hop QA benchmark with zero LLM forward calls at inference. "
            "CERT-delta=0 per Phase C MEASURED_MECHANISM policy; substrate stays at CERT 590. "
            "The substrate_native_qa_v2 composition-fix drill (Research designed-revival lane) "
            "is the chain-grade-meta candidate IF v2 lands HARD_PASS. Verified-off-data via "
            ".venv numpy recompute off data/exp_substrate_native_qa_hotpotqa_v1/metrics.json; "
            "Director-cited decomposition pieces (5.5pp / 6.7pp split, random-start EM=0%, "
            "bridge-only EM=7.8%, freq-bias 2.7x) are NOT in metrics.json and are explicitly "
            "flagged not-yet-data-verified in honest_scope (separate C5-probe cell required)."
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
                "MEASURED_MECHANISM_cell_HARD_FAIL_on_own_COMPOSED_bars_composed_em_0p010_"
                "lt_HF_0p10_lift_minus_0p112_GENERATION_ONLY_arm_headline_12p2pct_cv_0p004_"
                "n_seeds_3_NQ_1000_HotpotQA_distractor_zero_LLM_substrate_only_decode_gate_"
                "preserved_re_scoped_per_Director_ratification_A5_verify_referent_decomposition_"
                "pieces_not_in_metrics_json_flagged"
            ),
            "cell_commit": "1115ac3b",
            "metrics_path": "data/exp_substrate_native_qa_hotpotqa_v1/metrics.json",
            "notes_path": "notes/substrate_native_qa_hotpotqa_generation_v1_design_2026-06-22.md",
            "verified_off_data": (
                "cert-owner re-derived all cited numbers from "
                "data/exp_substrate_native_qa_hotpotqa_v1/metrics.json per_seed/per_unit "
                "(seeds 7, 17, 23) via .venv numpy + manual: per-arm across-seed mean_em "
                "SUBSTRATE_COMPOSED=0.0103 cv=0.0912; RETRIEVAL_ONLY=0.0103 cv=0.0912; "
                "GENERATION_ONLY=0.1223 cv=0.00385. Per-seed GENERATION_ONLY: seed7=0.123, "
                "seed17=0.122, seed23=0.122; recomputed mean=0.12233 std=0.000471 cv=0.00385 "
                "matches metrics.detail.cv_em.GENERATION_ONLY=0.00385 verbatim. "
                "composed_em=0.0103 < HARD_FAIL_bar=0.10 (cell verdict HARD_FAIL on own "
                "pre-reg bands HP_composed_em=0.20 HP_lift=0.05 HF_composed_em=0.10 "
                "cv_max=0.10). lift_composed_vs_best_primitive=-0.112 (COMPOSED < GENERATION_"
                "ONLY by 11.2pp; composition is value-negative on this arm pair). "
                "mean_retrieval_recall_at_5: COMPOSED=0.019, RETRIEVAL_ONLY=0.019 "
                "(retrieval stage is the principal failure point). mean_generation_n_distinct: "
                "COMPOSED=3.994 RETRIEVAL_ONLY=1.000 GENERATION_ONLY=3.988 (generator produces "
                "diverse outputs but mostly wrong answers). substrate_only_ok=True; "
                "zero_llm_calls_at_inference=True; n_llm_calls=0. run_mode='full' per_seed "
                "(all 3); device=cuda all seeds. elapsed per seed: 271.83 / 360.40 / 497.84 "
                "(total 1130.83s; matches metrics.elapsed_s). config_version baked verbatim: "
                "'substrate-native-qa-hotpotqa-v1: N_DIM=8192 N_Q=1000 TOP_K=5 GEN_DEPTH=4 "
                "arms=SUBSTRATE_COMPOSED,RETRIEVAL_ONLY,GENERATION_ONLY sigma=0.100 run_mode="
                "full device=cuda; bands HP_composed_em=0.20 HP_lift=0.05 HF_composed_em=0.10 "
                "cv_max=0.10'. corpus_provenance='hotpotqa_distractor_dev_1k_jsonl'; "
                "allow_synthetic=False (real benchmark). SCHEMA-VET PASS on all measured "
                "fields. NOT verified (absent from metrics.json): random-start EM=0%, "
                "bridge-only EM=7.8%, per-100-most-common EM=23.6%, rare EM=8.7%, freq-bias "
                "2.7x, 5.5pp/6.7pp decomposition. These would require a separate C5-probe "
                "cell + metrics.json artifact for verify-off-data; explicitly flagged in "
                "honest_scope."
            ),
            "honest_scope": (
                "MEASURED_MECHANISM characterization of char_trigram-encoder + g1b "
                "SubstrateGenerator stack on HotpotQA-distractor 1k dev. RE-SCOPED from "
                "Director's initial chain-grade-meta framing per A5 hold + Director-ratified "
                "narrower MM claim (2026-06-22). Cell pre-reg HARD_PASS bar (composed_em >= "
                "0.20 + lift >= 0.05) HARD_FAIL'd with composed_em=0.010 (9.7x below HF bar) "
                "and lift=-0.112 (COMPOSED is worse than GENERATION_ONLY); composition-level "
                "claim is OUT OF SCOPE. The retained measured mechanism is the GENERATION_"
                "ONLY-arm headline: char_trigram + g1b stack achieves 12.2% +- 0.05% EM "
                "(cv=0.004) seed-stable across 3 seeds at zero LLM calls. DOES NOT claim "
                "g1b-autonomous-QA (the 12.2% requires char_trigram-encoder to seed nearest-"
                "entity-name retrieval; g1b SubstrateGenerator runs ON TOP of that). DOES "
                "NOT claim chain-grade meta (cell HARD_FAIL'd own bars per by-construction-"
                "saturation discipline; cannot post-hoc reframe). DOES NOT claim substrate-"
                "as-LLM-substitute (the 12.2% is a single-arm headline, not a substitution-"
                "level evidence point). DOES NOT extend g1b CERT 587 chain-grade scope; "
                "g1b's chain-grade conditions remain those certified at CERT 587. NOT YET "
                "DATA-VERIFIED (Director-cited but absent from metrics.json; would require "
                "separate C5-probe cell): the 5.5pp char_trigram-nearest-entity-name retrieval "
                "contribution split, the 6.7pp marginal generation-stage lift conditional on "
                "retrieval start, random-start EM=0% (would confirm conditional-on-retrieval), "
                "bridge-only EM=7.8% (per-question-class breakdown), per-100-most-common EM="
                "23.6% vs rare EM=8.7% (2.7x freq-bias enrichment, below 5x drill bar). These "
                "decomposition pieces would substantiate Director's mechanism story but are "
                "not in the committed metrics artifact; this atom flags them transparently. "
                "Designed follow-up: substrate_native_qa_v2 composition-fix drill (Research "
                "designed-revival lane, notes/research_substrate_native_qa_2x_revival_"
                "composition_fix_drill_2026-06-22.md); IF v2 lands HARD_PASS that is the "
                "chain-grade-meta candidate (NEW cell + pre-reg + discriminating); this v1 "
                "MM atom is the honest-scope baseline."
            ),
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "N_DIM": 8192,
            "N_Q": 1000,
            "TOP_K": 5,
            "GEN_DEPTH": 4,
            "run_mode": "full",
            "device": "cuda",
            "corpus": "hotpot_qa_distractor_dev_1k",
            "corpus_path": "data/datasets/hotpot_qa_distractor_dev_1k.jsonl",
            "corpus_provenance": "hotpotqa_distractor_dev_1k_jsonl",
            "allow_synthetic": False,
            "arms": ["SUBSTRATE_COMPOSED", "RETRIEVAL_ONLY", "GENERATION_ONLY"],
            "mean_em_SUBSTRATE_COMPOSED": 0.010333333333333332,
            "mean_em_RETRIEVAL_ONLY": 0.010333333333333332,
            "mean_em_GENERATION_ONLY": 0.12233333333333334,
            "cv_em_SUBSTRATE_COMPOSED": 0.09123958466923196,
            "cv_em_RETRIEVAL_ONLY": 0.09123958466923196,
            "cv_em_GENERATION_ONLY": 0.0038534429492454937,
            "per_seed_GENERATION_ONLY_em": [0.123, 0.122, 0.122],
            "composed_em": 0.010333333333333332,
            "retrieval_only_em": 0.010333333333333332,
            "generation_only_em": 0.12233333333333334,
            "lift_composed_vs_best_primitive": -0.112,
            "cv_composed_em": 0.09123958466923196,
            "mean_retrieval_recall_at_5_COMPOSED": 0.019,
            "mean_retrieval_recall_at_5_RETRIEVAL_ONLY": 0.019,
            "mean_generation_n_distinct_COMPOSED": 3.994,
            "mean_generation_n_distinct_RETRIEVAL_ONLY": 1.000,
            "mean_generation_n_distinct_GENERATION_ONLY": 3.988,
            "substrate_only_decode": True,
            "zero_llm_calls_at_inference": True,
            "n_llm_calls": 0,
            "elapsed_s_total": 1130.83,
            "elapsed_s_per_seed": [271.83, 360.40, 497.84],
            "cell_pre_reg_bands": {
                "HP_composed_em": 0.20,
                "HP_lift": 0.05,
                "HF_composed_em": 0.10,
                "cv_max": 0.10,
            },
            "cell_verdict_per_own_bars": "HARD_FAIL",
            "config_version": (
                "substrate-native-qa-hotpotqa-v1: N_DIM=8192 N_Q=1000 TOP_K=5 GEN_DEPTH=4 "
                "arms=SUBSTRATE_COMPOSED,RETRIEVAL_ONLY,GENERATION_ONLY sigma=0.100 "
                "run_mode=full device=cuda; bands HP_composed_em=0.20 HP_lift=0.05 "
                "HF_composed_em=0.10 cv_max=0.10"
            ),
            "encoder": "char_trigram",
            "encoder_rationale": (
                "no_MiniLM_chosen_for_full_substrate_only_decode_accepts_semantic_loss_"
                "tradeoff_for_zero_LLM_calls_at_inference_gate"
            ),
            "composes_with": [
                "T3/EXP_g1b_capacity_sweep_v1",  # CERT 587 g1b generation mechanism
                "T3/EXP_h_hotpotqa_ingest_v1",  # CERT 588 HotpotQA KG corpus precedent
            ],
            "designed_revival_follow_up": (
                "substrate_native_qa_v2_composition_fix_drill_Research_designed_revival_lane_"
                "notes_research_substrate_native_qa_2x_revival_composition_fix_drill_2026_06_22_md_"
                "different_score_fusion_if_HARD_PASS_chain_grade_meta_candidate_NOT_this_v1_MM_atom"
            ),
            "decomposition_director_cited_but_not_data_verified": {
                "char_trigram_nearest_entity_name_retrieval_pp_contribution": 5.5,
                "marginal_generation_stage_lift_pp_conditional_on_retrieval_start": 6.7,
                "random_start_em_pct": 0.0,
                "bridge_only_em_pct": 7.8,
                "per_100_most_common_answers_em_pct": 23.6,
                "rare_answers_em_pct": 8.7,
                "freq_bias_enrichment_ratio": 2.7,
                "freq_bias_drill_bar_ratio": 5.0,
                "note": (
                    "Director-ratified claim text includes the above decomposition; "
                    "absent from data/exp_substrate_native_qa_hotpotqa_v1/metrics.json; "
                    "explicitly NOT verified-off-data. Separate C5-probe cell required to "
                    "lift these to verifiable status. Atomized as Director-claim provenance, "
                    "not auditor-verified provenance."
                ),
            },
            "cites": [
                "USER_directed_substrate_as_LLM_substitute_lane_2026-06-22",
                "A5_role_separation_skunkworks_holds_chain_grade_atomization_when_cell_HARD_FAIL_on_own_bars",
                "by_construction_saturation_meta_post_hoc_reframing_not_chain_grade",
                "verify_the_referent_decomposition_not_in_metrics_flagged_in_honest_scope",
                "Fix_16_discriminator_regime_must_can_fail",
                "Fix_2_pre_reg_direction_must_honor_intent",
                "Phase_C_MEASURED_MECHANISM_policy_delta_0_CERT_N_unchanged",
            ],
            "atomized_by": (
                "skunkworks_g1b_hotpotqa_12pct_atomize_RE_SCOPED_MM_per_Director_ratification_2026-06-22"
            ),
            "atomized_date": "2026-06-22",
            "session_authored": (
                "skunkworks_held_original_chain_grade_meta_request_DEFERRED_VET_Director_"
                "ratified_re_scoped_MM_claim_A5_role_separation_working_as_designed"
            ),
        },
    )


def safe_add_with_ledger(atom: Atom, source: str, note: str, ledger_row: dict):
    """Add atom + fresh-Store round-trip verify, then append ledger row (delta=0)."""
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"  SKIP (idempotent at Store layer): {atom.id} already present.")
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
            print(f"  FAIL: tier mismatch (expected {atom.tier}, got {found.tier})")
            return (False, None)
        if found.kind != atom.kind:
            print(f"  FAIL: kind mismatch")
            return (False, None)
        md = found.metadata or {}
        expected_pq = (atom.metadata or {}).get("provenance_quality")
        if md.get("provenance_quality") != expected_pq:
            print(f"  FAIL: pq mismatch (expected {expected_pq}, got {md.get('provenance_quality')})")
            return (False, None)
        print(f"  PASS: round-trip survival OK (pq=MEASURED_MECHANISM confirmed)")

    # Live CERT count (post-add). Ledger writes do NOT move CERT N. For MM atoms,
    # add_atom also does NOT move CERT N (provenance_quality != CERT_CHAIN_GRADE).
    ps_live = PartitionedStore(STORE_ROOT)
    live_cert = sum(1 for a in ps_live.all_atoms()
                    if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
    print(f"  live CERT at ledger time = {live_cert} (MM atom add does NOT move CERT N)")

    print(f"  appending cert-ledger row "
          f"(op={ledger_row.get('op')} status={ledger_row.get('cert_status')} "
          f"delta={ledger_row.get('cert_increment_delta')})")
    try:
        # delta=0 ledger-writer pattern: expected_cert_n_pre = expected_cert_n_post = live_cert
        row_h = append_cert_ledger_row(
            ledger_row,
            expected_cert_n_pre=live_cert,
            expected_cert_n_post=live_cert,
        )
        print(f"  ledger row appended; row_hash = {row_h}")
        return (True, row_h)
    except Exception as e:
        print(f"  FAIL: cert-ledger append errored: {e}")
        return (False, None)


def main() -> int:
    if "--apply" not in sys.argv:
        print("DRY: pass --apply to mutate Store + ledger.")
        a = build_atom()
        print(f"  atom id: {a.id}")
        print(f"  qualified id: {a.corpus.value}::{a.id}")
        print(f"  pq={a.metadata['provenance_quality']} cert_status={a.metadata['cert_status']} "
              f"cert_class={a.metadata['cert_class']}")
        print(f"  verdict={a.metadata['verdict'][:80]}...")
        print(f"  cell_commit={a.metadata['cell_commit']}")
        print(f"  metrics_path={a.metadata['metrics_path']}")
        return 0

    # A5 PRE
    ps = PartitionedStore(STORE_ROOT)
    atoms_pre = list(ps.all_atoms())
    n_atoms_pre = len(atoms_pre)
    cert_pre = sum(1 for a in atoms_pre if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
    print(f"A5-PRE: total atoms = {n_atoms_pre}; CERT N = {cert_pre}")
    expected_atoms_post = n_atoms_pre + 1
    expected_cert_post = cert_pre  # MM atom: delta=0
    print(f"        expected post: atoms = {expected_atoms_post}; CERT N = {expected_cert_post} (delta=0)")

    if cert_pre != 590:
        print(f"NOTE: CERT N pre = {cert_pre}, Director expected 590 (informational).")

    print()
    print("=" * 72)
    print("Window 1: char_trigram + g1b composition HotpotQA MEASURED_MECHANISM (delta = 0)")
    print("=" * 72)
    atom = build_atom()
    notes_path = atom.metadata["notes_path"]
    metrics_path = atom.metadata["metrics_path"]
    row = build_measured_mechanism_row(
        atom_id=f"{atom.corpus.value}::{atom.id}",
        cell_commit=atom.metadata["cell_commit"],
        verdict=(
            "MEASURED_MECHANISM_cell_HARD_FAIL_on_own_COMPOSED_bars_GENERATION_ONLY_arm_"
            "12p2pct_cv_0p004_zero_LLM_re_scoped_per_Director_ratification_A5_verify_referent"
        ),
        notes_path=notes_path,
        metrics_path=metrics_path,
        atomized_by="skunkworks",
        note=(
            "char_trigram_g1b_composition_hotpotqa_MM_atomize_re_scoped_per_Director_ratification_"
            "cell_HARD_FAIL_on_own_COMPOSED_bars_composed_em_0p010_lt_HF_0p10_lift_minus_0p112_"
            "GENERATION_ONLY_arm_headline_12p2pct_cv_0p004_n_seeds_3_NQ_1000_HotpotQA_distractor_"
            "zero_LLM_n_llm_0_substrate_only_decode_gate_preserved_per_seed_0p123_0p122_0p122_"
            "encoder_char_trigram_no_MiniLM_for_full_substrate_only_decode_composes_g1b_CERT_587_"
            "h_hotpotqa_CERT_588_NOT_chain_grade_meta_per_by_construction_saturation_discipline_"
            "designed_revival_v2_composition_fix_drill_Research_lane_if_HARD_PASS_chain_grade_"
            "meta_candidate_NOT_this_v1_MM_atom_Director_cited_decomposition_pieces_5p5pp_6p7pp_"
            "random_start_0pct_bridge_only_7p8pct_freq_bias_2p7x_NOT_in_metrics_json_flagged_"
            "honest_scope_separate_C5_probe_cell_required_substrate_stays_CERT_590"
        ),
    )
    ok, h = safe_add_with_ledger(
        atom,
        source="skunkworks_landed_vet_re_scoped_MM_2026-06-22",
        note=row["note"],
        ledger_row=row,
    )
    if not ok:
        print("ABORT: char_trigram_g1b_composition_hotpotqa MM atomize failed.")
        return 1
    print(f"  Window 1 OK; row_hash={h}")

    # A5 POST
    ps_post = PartitionedStore(STORE_ROOT)
    atoms_post = list(ps_post.all_atoms())
    n_atoms_post = len(atoms_post)
    cert_post = sum(1 for a in atoms_post if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
    print()
    print("=" * 72)
    print(f"A5-POST: total atoms = {n_atoms_post} (expected {expected_atoms_post}); "
          f"CERT N = {cert_post} (expected {expected_cert_post}; delta=0 for MM)")
    print(f"  row_hash: {h}")
    print("=" * 72)

    if n_atoms_post != expected_atoms_post:
        print(f"WARNING: atom count drift ({expected_atoms_post} expected, got {n_atoms_post})")
        return 1
    if cert_post != expected_cert_post:
        print(f"WARNING: CERT count drift ({expected_cert_post} expected, got {cert_post})")
        return 1
    print("A5 invariants PRESERVED (atom count +1, CERT N unchanged at delta=0 for MM).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
