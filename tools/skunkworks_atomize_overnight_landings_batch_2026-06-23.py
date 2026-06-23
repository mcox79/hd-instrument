"""Skunkworks landed-VET batch atomize: overnight 2026-06-22 -> 2026-06-23.

13 un-atomized landings post CERT 590 (last cert ts=1782179924).

Director-classified candidates re-audited per Fix #28 (per-arm metrics read directly,
NOT verdict_msg framings). Cert-owner final-call per A5 role-separation discipline.

RULINGS (1 chain_grade + 3 measured_mechanism + 5 honest_negative; 3 smoke duplicates no-op):

  chain_grade (+1 CERT; 590 -> 591):
    1. a1_substrate_intent_classifier_v1_gatecheck (FULL 3 seeds, 25.3s, n_llm=0)
       SUBSTRATE 0.761 (cv 0.042) dominates RANDOM 0.145 / MAJORITY 0.163 across all 3 seeds
       maj_mult=4.66 rand_mult=5.23 p95=3.9ms; honest-scope discloses COMPARISON=0 per-class

  measured_mechanism (delta=0):
    2. substrate_native_qa_hotpotqa_v2_composition_drill (SMOKE; best_alpha=0.0 collapses
       to GENERATION_ONLY; FREQ_BIAS baseline 0.42 >> composed 0.22 = composition fix did
       NOT add value; smoke scope; v3 design required before chain-grade candidacy)
    3. a2_substrate_templated_response_v1 (SMOKE; gram_lift=0.833 real but factual=0.10
       identical across all 3 arms = retrieval ceiling, rendering machinery only)
    4. pc1_predictive_coding_residual_gate_v1 (SMOKE; VAN+PC arms all recall=1.0 in
       deeply-undersaturated regime M=80<<N capacity; CONTROL drops to 0.48 confirms
       harness but main signal saturated-by-construction per META atom on file)
    5. n11_random_indexing_semantic_v1 (SMOKE; ratios 1.35-1.46 vs control 1.08; cell
       itself self-classified MIDDLE_BAND citing by-construction-saturation discipline)
    6. c2_cascade_stc_swr_continual_v2 (SMOKE; gap=0.15 below HP gap_ok bar; mechanism
       partial, n_seeds=1 only)

  honest_negative (delta=0):
    7. b2_substrate_only_tinystories_lm_v1 (SMOKE; substrate ppl 512 > unigram 220; FAILS
       to beat unigram; mechanism broken at this scale/config)
    8. att1_iterative_attractor_cleanup_v1 (SMOKE; best_att1_lift=0.000; iterative attractor
       does NOT unlock argmax cleanup; META primitive REJECTED as substrate-mine swap-in)
    9. text8_substrate_pseudoLM_gpu_v1 (SMOKE; substrate BPC 9.37 > unigram BPC 8.02;
       substrate WORSE than unigram floor; Path A pseudo-LM broken at v1 config)
    10. cross_corpus_compose_chat_v1_n4096 (SMOKE; best_compose=0.059 == single=0.059;
        composition adds NO value vs single-corpus retrieval)
    11. substrate_self_map_v2c (FULL 3 seeds 5709s; cluster_gap = -3 (shuffle 38 > real 35);
        cv_clusters=0.314 > 0.10; substrate-native self-mapping path NEGATIVE on full-Store
        ingest after v2/v2b MIDDLE_BAND attempts -- mechanism rejected at this scope)

  smoke duplicates (no-op; FULL or peer covers):
    - a1_substrate_intent_classifier_v1_smoke (smoke of #1 FULL)
    - a1_substrate_intent_classifier_v1_gatecheck_smoke (smoke of #1 FULL)
    - text8_substrate_pseudoLM_gpu_v1_smoke_remote (identical-metrics duplicate of #9)

PER-CLASS AUDIT NOTES (Fix #28 verify per-arm not verdict_msg framing):

  a1 gatecheck FULL (chain_grade): substrate dominates BOTH baselines at EVERY seed
    individually (seed7: 0.804 vs 0.150/0.159; seed17: 0.728 vs 0.125/0.162; seed23:
    0.751 vs 0.162/0.169). Per-category granularity: COMPARISON=0.0 across all 3 seeds
    (char-trigram encoder cannot resolve and-coordination structure); LIST/CHAIN/COUNT
    near-perfect; LOOKUP weak (0.33-0.48). Headline 0.76 is honest mean over heterogeneous
    quality. Pre-reg bars cleared sacrosanctly (acc>=0.65, maj>=2.0, rand>=5.0, p95<10ms,
    n_llm=0). cv 0.042 well below 0.10 cap.

  v2 composition drill (MM): cell pre-reg HP bars say composed_em=0.22 + lift=0.08, both
    cleared. BUT load-bearing: best_alpha=0.0 = WEIGHTED AVERAGE COLLAPSES TO PURE
    GENERATION_ONLY. The 'composition fix' did NOT add value; alpha=0 is the no-composition
    point. C-arm reveals FREQ_BIAS baseline em=0.42 vs composed em=0.22, meaning a static
    'guess from top-100 frequent answers' baseline beats composed by 90%. Cell can claim:
    'composition machinery does not degrade vs pure generation'. Cannot claim: 'composition
    adds value vs pure generation'. NOT chain-grade until full-run + non-trivial best_alpha.

  a2 templated (MM): gram_lift=0.833 is REAL (rendering machinery vs raw entity sequence)
    BUT factual_ratio identical 0.10 across ALL 3 arms (TEMPLATED, RAW, NO_RETRIEVAL).
    Per by-construction-saturation: factual is GATED by KG retrieval quality (independent),
    not by template rendering. Cell honestly says so in honest_scope. Sample responses show
    grammatically-correct-but-factually-wrong (Scott Derrickson -> Esma Sultan Mansion).
    MM scope = rendering machinery only.

  pc1 (MM): all 3 substantive arms recall_at_1=1.000. M=80 << capacity (N=256 at alpha=
    0.3125 = ~25-40 effective slots). The mechanism IS sound (PC_RESIDUAL_PROPORTIONAL
    drops W_norm by 50% with no recall loss = lossless compression candidate), but at
    perfect-by-construction in this regime. Need denser regime to discriminate chain-grade.

  n11 (MM): distributional ratios 1.35-1.46 vs control 1.08. Cell self-classified
    MIDDLE_BAND citing by-construction-saturation. Single-seed; needs multi-seed to
    discriminate stability. cv=0 across all arms (single-seed = vacuous cv).

  c2 v2 (MM): C2 1.0 vs C1 0.85 gap=0.15 partial mechanism. n_seeds=1, hp gap_ok=False.
    v2b A+C Director option appears to recover SOME but not full chain-grade gap.

  b2 tinystories (honest_negative): substrate 159/512 lose to unigram 196/220. Path A
    pseudo-LM mechanism broken at V_DIM=1024, V=2000. Route to Research for 2x-revival.

  att1 (honest_negative): all 3 ATT1 arms underperform argmax baseline in both regimes
    (0.04 vs 0.04 at harder; 0.22/0.20/0.30 vs 0.34 at gentle). META primitive 'iterative
    soft-attractor cleanup' REJECTED as substrate-mine swap-in. Route to Research for
    2x-revival angle.

  text8 pseudoLM (honest_negative): substrate BPC 9.37 > unigram BPC 8.02; substrate is
    WORSE than ignoring context entirely. Backoff arm 9.29 also worse than unigram. Pure
    Hebbian on word-level text8 at N_DIM=4096, V=4000 = broken mechanism.

  cross_corpus_compose (honest_negative): single 0.059 = union 0.059 = hub 0.059. Three
    composition strategies tied at zero lift. Per-corpus: hotpotqa 0% (no answer match
    at all), fb15k 0%, conceptnet 16.7% (only contributing corpus). Composition cannot
    add value when 2/3 source corpora contribute zero.

  substrate_self_map_v2c (honest_negative): real_n_clusters=35 (mean), shuffle=38; gap=-3.
    Shuffled-relation control produces AS MANY OR MORE clusters than real-relation. Mechanism
    NULL on full-Store ingest scope. recall=1.000 confirms harness valid (atoms encoded +
    retrieved correctly); cv_clusters=0.314 confirms unstable cluster-count across seeds.
    This is the FULL-Store recovery path from v2b MIDDLE_BAND; both paths failed. Path
    rejected at this scope. Genuine substrate-native self-mapping (vs v1 Director-lexical
    scaffolding) does not emerge under (char_trigram + KGStore_multivalue_Hebbian +
    multi_hop_2hop_Jaccard) over 177k atoms.

DISCIPLINES HONORED:
  - A5 PRE/POST snapshot at start + end (one window for all 9 writes)
  - Fix #28: per-arm metrics read directly, not verdict_msg framings
  - by-construction-saturation tiering (MM when at metric ceiling regardless of bands)
  - honest_negative for cells that fail their own load-bearing bars
  - verify-the-referent: every cited number recomputed from metrics.json before write
  - Idempotency: skip atoms already in Store
  - Foreground execution (Fix #20)
  - ASCII-only
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_chain_grade_ruling_row,
    build_measured_mechanism_row,
    build_honest_negative_row,
)


STORE_ROOT = Path("data/substrate_index")
ATOMIZED_BY = "skunkworks_overnight_landings_batch_2026-06-23"


# ============================================================================
# 1. chain_grade: a1_substrate_intent_classifier_v1 (gatecheck FULL)
# ============================================================================

def build_a1_gatecheck_chain_grade() -> Atom:
    return Atom(
        id="T3/EXP_a1_substrate_intent_classifier_v1",
        name=(
            "a1 substrate-native intent classifier (7 categories) -- HARD_PASS "
            "(acc=0.761 cv=0.042; maj_mult=4.66 rand_mult=5.23; p95=3.9ms; n_llm=0)"
        ),
        description=(
            "Substrate-native question intent classifier across 7 categories (LOOKUP, "
            "COMPARISON, MULTI_HOP, LIST, CHAIN, COUNT, DEFINITION) using char-trigram "
            "encoder + HD bipolar similarity over class-prototype vectors. 3-seed FULL "
            "run at N_DIM=2048 N_TRAIN=5000 N_TEST=500 on hotpotqa_dev_1k + nq_open_val_1k "
            "+ conceptnet5_en_100k_templates. Zero LLM forward calls at inference (n_llm=0; "
            "char-trigram encoder, no MiniLM, no LLM teacher). HARD_PASS on all pre-reg bars "
            "(acc>=0.65, maj_mult>=2.0, rand_mult>=5.0, p95_ms<10.0, n_llm=0, cv<=0.10): "
            "mean_accuracy SUBSTRATE_INTENT=0.7606 (per-seed 0.804/0.728/0.751, cv=0.042) "
            "vs RANDOM_BASELINE=0.1455 vs MAJORITY_BASELINE=0.1632; maj_mult=4.66, "
            "rand_mult=5.23, p95_latency=3.90ms. Substrate dominates both baselines at "
            "every seed individually. Per-category granularity (load-bearing honest-scope): "
            "COMPARISON=0.0 across all 3 seeds (char-trigram encoder cannot resolve and-"
            "coordination structure semantically); LIST/CHAIN/COUNT near-perfect (0.97-1.00); "
            "LOOKUP weak (0.33-0.48); DEFINITION moderate (0.68-0.87). Headline 0.76 is "
            "honest mean over heterogeneous category quality. Labels synthesized procedurally "
            "from HotpotQA type field + NQ-open keyword-classifier + ConceptNet templates "
            "(allow_synthetic=True per cell config). Composes with char_trigram_encoder "
            "(CERT 585), kg_traversal primitive, and the substrate-native pipeline; "
            "supplies the substrate-only intent-classification primitive for the conversational "
            "lane (Director g1 conversational LATER per USER strategic vision 2026-06-22). "
            "Verified-off-data via .venv numpy recompute of metrics.json per_seed/per_unit; "
            "all cited numbers reproduce exactly. config_version baked AST-verifiable; "
            "run_mode='full' confirmed per_seed (all 3); elapsed_total=25.33s."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "verdict": (
                "HARD_PASS_substrate_native_intent_classifier_7categories_acc_0p761_cv_0p042_"
                "maj_mult_4p66_rand_mult_5p23_p95_3p9ms_n_llm_0_3seeds_FULL_char_trigram_encoder_"
                "substrate_dominates_both_baselines_at_every_seed_individually_COMPARISON_class_"
                "weak_per_category_honest_scope"
            ),
            "cell_commit": "overnight_2026-06-22",
            "metrics_path": "data/exp_a1_substrate_intent_classifier_v1_gatecheck/metrics.json",
            "notes_path": "notes/a1_substrate_intent_classifier_v1_design.md",
            "verified_off_data": (
                "cert-owner re-derived all cited numbers from "
                "data/exp_a1_substrate_intent_classifier_v1_gatecheck/metrics.json per_seed/"
                "per_unit (seeds 7, 17, 23): per-arm across-seed mean accuracy SUBSTRATE_INTENT="
                "0.7606 cv=0.042 (per-seed 0.8037/0.7275/0.7506; std=0.0319), RANDOM_BASELINE="
                "0.1455 cv=0.106 (per-seed 0.1501/0.1247/0.1617), MAJORITY_BASELINE=0.1632 "
                "cv=0.024 (per-seed 0.1594/0.1617/0.1686). maj_mult=0.7606/0.1632=4.66, "
                "rand_mult=0.7606/0.1455=5.23, both match metrics.summary verbatim. "
                "Pre-reg bands ALL cleared: acc>=0.65 PASS (0.761), maj_mult>=2.0 PASS (4.66), "
                "rand_mult>=5.0 PASS (5.23, just-cleared; smoke was 4.12 below bar), "
                "p95_ms<10.0 PASS (3.90), n_llm=0 PASS (substrate-only-decode gate verified), "
                "cv<=0.10 PASS (0.042). Per-category breakdown (load-bearing honest scope): "
                "COMPARISON=0.0 ALL 3 SEEDS (char-trigram encoder cannot resolve and-"
                "coordination structure); LIST=1.0/1.0/0.97; CHAIN=0.96/1.0/1.0; COUNT="
                "0.98/1.0/0.97; DEFINITION=0.87/0.68/0.79; MULTI_HOP=0.74/0.52/0.66; LOOKUP="
                "0.48/0.44/0.33. Substrate dominates BOTH baselines at EVERY seed individually "
                "(no seed where random or majority approaches substrate). elapsed_per_seed "
                "(s): 7.80, 8.84, 8.09 (total ~24.7s; matches metrics.elapsed_s=25.33 with "
                "harness overhead). n_llm_calls=0 per seed and total. config_version baked "
                "AST-verifiable matches metrics.config_version verbatim. corpus_provenance="
                "'hotpotqa_dev_1k + nq_open_val_1k + conceptnet5_en_100k_templates'; "
                "allow_synthetic=True (procedurally-synthesized labels from real data, per "
                "cell pre-reg). Discriminator (Fix #16) armed and behaves correctly: RANDOM "
                "and MAJORITY baselines both collapse to chance/majority rate respectively "
                "(can-fail discriminator). Smoke variant (N_DIM=512 N_TRAIN=200) cleared "
                "acc/maj/p95 bars but rand_mult=4.12 below 5.0 cap = MIDDLE_BAND at smoke "
                "scope; FULL config at N_DIM=2048 N_TRAIN=5000 clears all bars."
            ),
            "honest_scope": (
                "Substrate-native intent classifier; 7 categories; LOOKUP, COMPARISON, "
                "MULTI_HOP, LIST, CHAIN, COUNT, DEFINITION; N_DIM=2048 N_TRAIN=5000 N_TEST=500. "
                "3-arm discriminator (Fix #16): SUBSTRATE_INTENT vs RANDOM_BASELINE vs "
                "MAJORITY_BASELINE. Substrate-only-decode gate enforced (n_llm=0). Encoder: "
                "char-trigram (no MiniLM, no LLM teacher). Labels synthesized procedurally "
                "from HotpotQA type field + NQ-open keyword-classifier + ConceptNet templates "
                "(allow_synthetic=True). LOAD-BEARING HONEST-SCOPE: COMPARISON category "
                "accuracy=0.0 across all 3 seeds (char-trigram encoder cannot resolve and-"
                "coordination structure semantically); headline 0.761 is mean over heterogeneous "
                "per-category quality. DOES NOT claim parity with LLM-based intent classifiers; "
                "DOES NOT claim transfer to non-template categories; DOES NOT claim coverage "
                "of question-type taxonomies beyond the 7 chosen. Suitable as substrate-only "
                "intent-classification PRIMITIVE for the conversational pipeline lane."
            ),
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "N_DIM": 2048,
            "N_TRAIN": 5000,
            "N_TEST": 500,
            "n_categories": 7,
            "categories": ["LOOKUP", "COMPARISON", "MULTI_HOP", "LIST", "CHAIN", "COUNT", "DEFINITION"],
            "arms": ["SUBSTRATE_INTENT", "RANDOM_BASELINE", "MAJORITY_BASELINE"],
            "mean_acc_SUBSTRATE_INTENT": 0.7606,
            "mean_acc_RANDOM_BASELINE": 0.1455,
            "mean_acc_MAJORITY_BASELINE": 0.1632,
            "cv_SUBSTRATE_INTENT": 0.042,
            "majority_multiplier": 4.66,
            "random_multiplier": 5.23,
            "p95_latency_ms": 3.90,
            "elapsed_total_s": 25.33,
            "run_mode": "full",
            "encoder": "char_trigram",
            "corpus_provenance": "hotpotqa_dev_1k + nq_open_val_1k + conceptnet5_en_100k_templates",
            "allow_synthetic": True,
            "zero_llm_calls_at_inference": True,
            "n_llm_calls": 0,
            "per_category_known_weakness": {
                "COMPARISON": "0.0_all_3_seeds_char_trigram_encoder_cannot_resolve_and_coordination_structure",
                "LOOKUP": "0.33_to_0.48_weak_consistent_across_seeds",
            },
            "config_version": (
                "a1-substrate-intent-classifier-v1: N_DIM=2048 N_TRAIN=5000 N_TEST=500 "
                "arms=SUBSTRATE_INTENT,RANDOM_BASELINE,MAJORITY_BASELINE run_mode=full; "
                "bands HP_acc=0.65 HP_majority_mult=2.0 HP_random_mult=5.0 HP_p95_ms=10.0 "
                "HF_p95_ms=50.0"
            ),
            "composes_with": [
                "T3/char_trigram_encoder",  # CERT 585 encoder primitive
                "T3/kg_traversal",  # substrate-native primitive
            ],
            "cites": [
                "USER_strategic_vision_self_improvement_portal_2026-06-22",
                "Fix_16_discriminator_regime_must_can_fail",
                "Fix_28_verify_per_arm_metrics_not_verdict_msg_framing",
            ],
            "supplies_capability": [
                "cap_substrate_only_intent_classification_primitive",
                "cap_zero_LLM_question_routing",
            ],
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# 2-6. measured_mechanism atoms (delta=0; CERT-neutral)
# ============================================================================

def build_v2_composition_drill_mm() -> Atom:
    return Atom(
        id="T3/EXP_substrate_native_qa_hotpotqa_v2_composition_drill_MM",
        name=(
            "substrate_native_qa_hotpotqa_v2 composition-fix drill -- MEASURED_MECHANISM "
            "(SMOKE; best_alpha=0.0 collapses to GENERATION_ONLY; FREQ_BIAS 0.42 >> composed 0.22)"
        ),
        description=(
            "Research 2x-revival drill targeting v1's composition failure (CERT 590 MM atom). "
            "v2 design: score-fusion replaces v1's mode-aggregation composition; alpha-sweep "
            "alpha in {0.0, 0.2, 0.4, 0.6, 0.8, 1.0} over retrieval-score x generation-score. "
            "SMOKE run (N_Q=50, 1 seed, N_DIM=2048, GEN_DEPTH=3, TOP_K=5) on hotpotqa_distractor. "
            "Cell verdict HARD_PASS on its own bands (composed_em>=0.20, lift>=0.05, "
            "harness within tol); but per-arm LOAD-BEARING audit: best_alpha=0.0, which "
            "means the score-fusion COLLAPSES to pure GENERATION_ONLY (alpha=0 = no fusion). "
            "The 'composition fix' did NOT add value; alpha sweep monotonically degrades from "
            "alpha=0.0 (em=0.22) to alpha=1.0 (em=0.0). Furthermore, C-arm FREQ_BIAS baseline "
            "em=0.42 (predict from top-100 most-frequent answers) DOMINATES the composed arm "
            "by 90%. Question-type split: bridge em=0.28, comparison em=0.07 (large structural "
            "weakness); start-entity-leak rate=0.0 (clean discriminator); substring-overlap "
            "rate=0.04 (clean). Cell can claim: 'composition machinery is non-degrading vs "
            "pure generation in score-fusion form'. Cell CANNOT claim: 'composition adds "
            "value over pure generation' or 'beats FREQ_BIAS baseline'. MM (mechanism "
            "characterization) atomization at delta=0; NOT chain-grade until full-run + "
            "non-trivial best_alpha + FREQ_BIAS exceeded. Composes with v1 MM atom (CERT 590) "
            "and g1b CERT 587. Verified-off-data: best_alpha=0.0 confirmed in metrics.detail."
            "best_alpha; mean_b_by_alpha monotone decrease 0.0:0.22 -> 1.0:0.0; FREQ_BIAS "
            "em=0.42 in c_aggregate; question-type split bridge=0.278 vs comparison=0.071."
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
                "MEASURED_MECHANISM_smoke_HARD_PASS_on_own_bands_but_best_alpha_0p0_collapses_"
                "to_pure_GENERATION_ONLY_composition_did_not_add_value_FREQ_BIAS_baseline_0p42_"
                "DOMINATES_composed_0p22_not_chain_grade_until_full_plus_nontrivial_best_alpha"
            ),
            "cell_commit": "overnight_2026-06-22",
            "metrics_path": "data/exp_substrate_native_qa_hotpotqa_v2_composition_drill_smoke/metrics.json",
            "notes_path": "notes/research_substrate_native_qa_2x_revival_composition_fix_drill_2026-06-22.md",
            "verified_off_data": (
                "cert-owner re-derived all cited numbers from metrics.json: best_alpha=0.0 "
                "(detail.best_alpha); best_alpha_em=0.22; alpha-sweep mean_b_by_alpha "
                "monotone-decreasing: 0.0:0.22, 0.2:0.14, 0.4:0.14, 0.6:0.14, 0.8:0.02, "
                "1.0:0.0. harness_em=0.14 (delta=0.018 from v1=0.122, within tol=0.10). "
                "c_aggregate.FREQ_BIAS.em_mean=0.42 (>> composed 0.22); SUBSTRING_OVERLAP "
                "rate=0.04 clean; QUESTION_TYPE bridge=0.278 comparison=0.071 (4x gap is "
                "structural weakness, not noise); START_ENTITY_LEAK rate=0.000 clean; "
                "RANDOM_SEED_CONTROL em=0.08 (can-fail discriminator armed). n_llm_calls=0. "
                "n_seeds=1 (smoke; full-run gate not cleared). elapsed_s=0.93. config_version "
                "matches verbatim. LOAD-BEARING: alpha=0.0 = no composition; score-fusion "
                "design did NOT add measurable value over pure generation at this smoke scope. "
                "FREQ_BIAS dominance is a separate concern: a static baseline that predicts "
                "from top-100 frequent answers beats the composed substrate by 90%."
            ),
            "honest_scope": (
                "SMOKE scope only (N_Q=50, 1 seed, N_DIM=2048). Score-fusion composition "
                "between retrieval (top-K) and generation (g1b) on hotpotqa-distractor. "
                "Substrate-only-decode (n_llm=0). MM characterization: cell cleared own "
                "bands but load-bearing best_alpha=0.0 means composition did NOT add value; "
                "additionally a trivial FREQ_BIAS baseline beats composed by 90%. NOT a "
                "chain-grade composition claim. FOLLOW-UP: full-run (multi-seed N_Q>=500); "
                "v3 design that beats FREQ_BIAS baseline AND has non-trivial best_alpha."
            ),
            "n_seeds": 1,
            "N_DIM": 2048,
            "N_Q": 50,
            "run_mode": "smoke",
            "harness_em": 0.14,
            "best_alpha": 0.0,
            "best_alpha_em": 0.22,
            "FREQ_BIAS_em": 0.42,
            "bridge_em": 0.278,
            "comparison_em": 0.071,
            "start_entity_leak_rate": 0.0,
            "substring_overlap_rate": 0.04,
            "random_seed_control_em": 0.08,
            "zero_llm_calls_at_inference": True,
            "composes_with": [
                "T3/EXP_substrate_native_qa_hotpotqa_v1_MM",  # v1 baseline composition MM
                "T3/EXP_g1b_capacity_sweep_v1",
                "T3/EXP_h_hotpotqa_ingest_v1",
            ],
            "cites": [
                "research_2x_revival_drill_2026-06-22",
                "Fix_28_verify_per_arm_not_verdict_msg",
                "by_construction_saturation_tiering",
            ],
            "atomized_by": ATOMIZED_BY,
        },
    )


def build_a2_templated_mm() -> Atom:
    return Atom(
        id="T3/EXP_a2_substrate_templated_response_v1_MM",
        name=(
            "a2 substrate-templated response rendering -- MEASURED_MECHANISM "
            "(SMOKE; gram_lift=0.833 real; factual=0.10 ceiling across all 3 arms = retrieval-gated)"
        ),
        description=(
            "Substrate-native templated English-response rendering on hotpotqa-distractor "
            "(N_Q=30 SMOKE, 1 seed, N_DIM=2048, TOP_K=5). 3-arm discriminator: "
            "TEMPLATED_RESPONSE vs RAW_ENTITY_SEQUENCE vs NO_RETRIEVAL_TEMPLATE_ONLY. "
            "Cell verdict HARD_PASS on own bands (gram_lift>=0.5, gram>=0.8, n_llm=0). "
            "Per-arm LOAD-BEARING audit: gram_lift=0.833 (templated 0.833 vs raw 0.000) is "
            "REAL and confirms rendering-machinery works (TEMPLATED produces grammatical "
            "English; RAW produces arrow-separated entity sequence). HOWEVER: factual_ratio "
            "IDENTICAL 0.100 across all 3 arms (TEMPLATED, RAW, NO_RETRIEVAL). By by-"
            "construction-saturation tiering: factual is GATED by KG retrieval quality "
            "(independent capability), not by template rendering. Cell honest_scope discloses "
            "this. Sample responses show grammatically-correct-but-factually-wrong (Scott "
            "Derrickson + Ed Wood nationality? -> 'The answer is Esma Sultan Mansion.'). MM "
            "scope = English-rendering machinery; NOT a QA-accuracy claim. Composes with "
            "kg_traversal + h_hotpotqa CERT 588 (the retrieval primitive whose quality "
            "gates factual). Verified-off-data: per-category factual_ratio matrix shows "
            "factual ceiling is in retrieval/KG quality, not rendering."
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
                "MEASURED_MECHANISM_smoke_gram_lift_0p833_rendering_machinery_real_but_factual_"
                "0p10_IDENTICAL_across_all_3_arms_retrieval_gated_ceiling_NOT_QA_accuracy_claim_"
                "by_construction_saturation_tiering"
            ),
            "cell_commit": "overnight_2026-06-22",
            "metrics_path": "data/exp_a2_substrate_templated_response_v1_smoke/metrics.json",
            "notes_path": "notes/a2_substrate_templated_response_v1_design.md",
            "verified_off_data": (
                "cert-owner re-derived all cited numbers from metrics.json: "
                "mean_factual_ratio TEMPLATED=0.100 RAW=0.100 NO_RETRIEVAL=0.100 (IDENTICAL "
                "across all 3 arms); mean_gram_ratio TEMPLATED=0.833 RAW=0.000 NO_RETRIEVAL=0.133 "
                "(rendering-machinery discriminator armed and PASSES: templated produces "
                "grammatical English, raw produces arrow-separated entity sequence). gram_lift="
                "templated_gram - raw_gram = 0.833 - 0.000 = 0.833. fact_delta_templated_vs_raw="
                "0.000 (templated and raw equally inaccurate; rendering does NOT add factual "
                "value because retrieval is the ceiling). n_seeds=1; n_llm_calls=0. Sample "
                "responses: Q='Were Scott Derrickson and Ed Wood of the same nationality?' A="
                "'The answer is Esma Sultan Mansion.' gold='yes' factual_hit=0 gram_hit=1 "
                "(grammatically correct, factually wrong; confirms rendering-vs-retrieval "
                "decoupling). per-category factual: WHAT_IS_X templated=0.67 raw=0.0; "
                "WHO_DID_X templated=0.33 raw=0.33; COMPARE_X_Y/FALLBACK both arms 0.0. "
                "Cell honest_scope explicitly cites retrieval-ceiling (v1 retrieval_only "
                "EM=0.010 at N_DIM=8192 N_Q=1000 = independent retrieval weakness)."
            ),
            "honest_scope": (
                "SMOKE scope only (N_Q=30, 1 seed, N_DIM=2048). 3-arm rendering-machinery "
                "discriminator on hotpotqa-distractor. MM characterization: gram_lift=0.833 "
                "is REAL evidence the templated-rendering primitive produces grammatical "
                "English from substrate-retrieved entities. But factual_ratio=0.10 across "
                "ALL 3 arms confirms factual accuracy is gated by KG retrieval quality "
                "(independent capability), not by template rendering. MM scope: English-"
                "rendering primitive works as designed; NOT a QA-accuracy claim. DOES NOT "
                "claim factual QA on hotpotqa. DOES NOT compose with retrieval to produce "
                "useful answers (separate retrieval-quality lift required). Suitable as the "
                "rendering primitive in a substrate-only conversational pipeline once "
                "retrieval primitive lifts factual ceiling."
            ),
            "n_seeds": 1,
            "N_DIM": 2048,
            "N_Q": 30,
            "TOP_K": 5,
            "run_mode": "smoke",
            "arms": ["TEMPLATED_RESPONSE", "RAW_ENTITY_SEQUENCE", "NO_RETRIEVAL_TEMPLATE_ONLY"],
            "mean_gram_TEMPLATED": 0.833,
            "mean_gram_RAW": 0.000,
            "mean_gram_NO_RETRIEVAL": 0.133,
            "mean_factual_TEMPLATED": 0.100,
            "mean_factual_RAW": 0.100,
            "mean_factual_NO_RETRIEVAL": 0.100,
            "gram_lift_templated_vs_raw": 0.833,
            "fact_delta_templated_vs_raw": 0.000,
            "zero_llm_calls_at_inference": True,
            "composes_with": [
                "T3/EXP_h_hotpotqa_ingest_v1",  # the retrieval primitive whose quality is the ceiling
                "T3/kg_traversal",
            ],
            "cites": [
                "Fix_28_verify_per_arm_not_verdict_msg",
                "by_construction_saturation_tiering",
                "v1_retrieval_only_em_0p010_independent_retrieval_weakness",
            ],
            "supplies_capability": ["cap_substrate_only_english_rendering_primitive"],
            "atomized_by": ATOMIZED_BY,
        },
    )


def build_pc1_mm() -> Atom:
    return Atom(
        id="T3/EXP_pc1_predictive_coding_residual_gate_v1_MM",
        name=(
            "pc1 predictive-coding residual-gate -- MEASURED_MECHANISM "
            "(SMOKE; recall=1.0 all PC arms in undersaturated regime; PROPORTIONAL halves W_norm)"
        ),
        description=(
            "Predictive-coding-style residual-gated Hebbian writes on synthetic-bipolar keys "
            "at N=256, M=80 (SMOKE; alpha=0.3125, 1 seed). 4 arms: VANILLA_HEBBIAN, "
            "PC_RESIDUAL_GATE_THRESH_0p3, PC_RESIDUAL_PROPORTIONAL, RANDOM_GATE_CONTROL. "
            "All 3 substantive arms (VAN + 2 PC) achieve recall_at_1=1.000; CONTROL drops to "
            "0.48 (can-fail discriminator armed). MM scope: M=80 at N=256 alpha=0.3125 is "
            "in the deeply-undersaturated capacity regime (well below substrate's effective "
            "Hebbian capacity 0.14*N approx 36, but PC-residual structure compresses); both "
            "PC arms achieve full recall at saturation level. NOTABLE LOSSLESS-COMPRESSION "
            "FINDING: PC_RESIDUAL_PROPORTIONAL drops W_norm to 1148 from VAN 2293 (50% "
            "reduction) with ZERO recall loss; threshold variant skips zero writes at this "
            "scale (because all writes have residual>0.3) so reduces to vanilla. Mechanism "
            "IS sound but cannot discriminate chain-grade at this saturation level. Need "
            "denser regime (M near 0.14*N or higher) to test whether PC_RESIDUAL_PROPORTIONAL "
            "preserves recall at saturation density. Verified-off-data via metrics.json per-"
            "arm; W_norm ratio 0.501 confirms 50% compression. Composes with c1/c2 continual-"
            "ingest atoms + write-economy capacity-sweep cells."
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
                "MEASURED_MECHANISM_smoke_VAN_and_both_PC_arms_recall_1p000_in_undersaturated_"
                "regime_M_80_N_256_alpha_0p3125_CONTROL_drops_to_0p48_discriminator_armed_"
                "PC_RESIDUAL_PROPORTIONAL_halves_W_norm_with_zero_recall_loss_lossless_"
                "compression_candidate_at_this_scale"
            ),
            "cell_commit": "overnight_2026-06-22",
            "metrics_path": "data/exp_pc1_predictive_coding_residual_gate_v1_smoke/metrics.json",
            "notes_path": "notes/pc1_predictive_coding_residual_gate_v1_design.md",
            "verified_off_data": (
                "cert-owner re-derived from metrics.json per_seed.arms: VANILLA_HEBBIAN "
                "recall=1.000 W_norm=2293.00; PC_RESIDUAL_GATE_THRESH_0p3 recall=1.000 "
                "W_norm=2293.00 (identical to VAN; threshold did not trigger at this scale); "
                "PC_RESIDUAL_PROPORTIONAL recall=1.000 W_norm=1148.01 (50.07% of VAN; "
                "lossless compression); RANDOM_GATE_CONTROL recall=0.480 W_norm=1678.71 "
                "n_writes_skipped=37/80 = 46.25% (can-fail discriminator: confirms random "
                "skipping DOES degrade recall, so PC arms are doing something non-trivial). "
                "n_llm_calls=0; n_seeds=1; elapsed=0.32s. At M=80 N=256, all PC arms saturate "
                "recall=1.0 (deeply-undersaturated for this Hebbian); the load-bearing finding "
                "is W_norm reduction (PROPORTIONAL halves W_norm), not recall (which is "
                "ceiling). Per by-construction-saturation tiering: recall at perfect saturation "
                "is not chain-grade evidence; W_norm reduction at constant recall IS a "
                "discriminating mechanism characterization (MM)."
            ),
            "honest_scope": (
                "SMOKE scope only (M=80, N=256, alpha=0.3125, 1 seed). Predictive-coding "
                "residual-gated Hebbian writes. MM characterization: PC_RESIDUAL_PROPORTIONAL "
                "halves W_norm with zero recall loss in this undersaturated regime; this is "
                "a lossless-compression CANDIDATE. NOT a chain-grade claim until: (a) multi-"
                "seed; (b) saturation regime where VAN itself loses recall (M near 0.14*N "
                "or higher), at which point PC_RESIDUAL_PROPORTIONAL's compression discipline "
                "would be discriminating; (c) substrate-realistic keys (not synthetic-bipolar). "
                "DOES NOT claim PC outperforms VAN in recall (both at ceiling). DOES claim: "
                "structural W_norm reduction without recall loss in undersaturated regime."
            ),
            "n_seeds": 1,
            "N": 256,
            "M": 80,
            "alpha": 0.3125,
            "threshold_pc": 0.3,
            "run_mode": "smoke",
            "arms": ["VANILLA_HEBBIAN", "PC_RESIDUAL_GATE_THRESH_0p3", "PC_RESIDUAL_PROPORTIONAL", "RANDOM_GATE_CONTROL"],
            "recall_VANILLA": 1.000,
            "recall_PC_GATE_0p3": 1.000,
            "recall_PC_PROPORTIONAL": 1.000,
            "recall_RANDOM_CONTROL": 0.480,
            "wnorm_ratio_PC_PROPORTIONAL_to_VAN": 0.501,
            "wnorm_ratio_RANDOM_to_VAN": 0.732,
            "lossless_compression_finding": "PC_RESIDUAL_PROPORTIONAL_halves_W_norm_zero_recall_loss_in_undersaturated_regime",
            "zero_llm_calls_at_inference": True,
            "composes_with": [
                "T3/EXP_c1_cls_replay_continual_ingest_v1",
                "T3/EXP_c2_cascade_stc_swr_continual_v2_MM",
            ],
            "cites": [
                "Fix_28_verify_per_arm_not_verdict_msg",
                "by_construction_saturation_tiering",
                "META_no_Hebbian_window",
            ],
            "atomized_by": ATOMIZED_BY,
        },
    )


def build_n11_mm() -> Atom:
    return Atom(
        id="T3/EXP_n11_random_indexing_semantic_v1_MM",
        name=(
            "n11 random-indexing distributional semantic -- MEASURED_MECHANISM "
            "(SMOKE; ratios 1.35-1.46 vs control 1.08; cell self-tiered)"
        ),
        description=(
            "Substrate-native distributional-semantic encoding via random-indexing (RI) on "
            "text8 smoke subset (200k tokens; N_DIM=8192, sparsity=10, window=5, 1 seed). "
            "4 arms: RANDOM_INDEXING_ALONE, RI_PLUS_BEAGLE_ORDER, RI_HUB_SPOKE_KGSTORE, "
            "CONTROL_RANDOM_PERMUTE. Cell self-classified MIDDLE_BAND citing by-construction-"
            "saturation discipline. Per-arm: RI_ALONE ratio 1.368 (sim 0.578 vs dissim 0.422); "
            "BEAGLE 1.457 (best substantive); HUB_SPOKE 1.353; CONTROL 1.081 (can-fail "
            "discriminator armed: control permutes context vector indices, breaking the "
            "distributional signal). Substantive ratios all > control by ~25-37%, but no "
            "ratio crosses the 1.5x bar (substrate-only RI distributional signal is REAL "
            "but partial at this token-budget x N_DIM regime). cv=0 across all arms (single-"
            "seed = vacuous cv). MM scope: distributional-semantic encoding mechanism is "
            "armed and discriminates, but at modest signal strength. Needs multi-seed + "
            "either larger token budget or denser N_DIM to discriminate chain-grade. "
            "Composes with char_trigram_encoder (CERT 585) + KGStore primitives. Verified-"
            "off-data: ratios + per-arm cosines match metrics verbatim; control ratio 1.08 "
            "is the can-fail discriminator confirming non-trivial substantive signal."
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
                "MEASURED_MECHANISM_smoke_RI_distributional_signal_real_but_partial_BEAGLE_"
                "best_ratio_1p457_RI_alone_1p368_HUB_SPOKE_1p353_vs_CONTROL_1p081_no_ratio_"
                "crosses_1p5x_bar_cell_self_tiered_by_construction_saturation_discipline"
            ),
            "cell_commit": "overnight_2026-06-22",
            "metrics_path": "data/exp_n11_random_indexing_semantic_v1_smoke/metrics.json",
            "notes_path": "notes/n11_random_indexing_semantic_v1_design.md",
            "verified_off_data": (
                "cert-owner re-derived from metrics.json by_arm_agg: RANDOM_INDEXING_ALONE "
                "ratio_mean=1.3679 similar=0.5776 dissim=0.4223; RI_PLUS_BEAGLE_ORDER "
                "ratio=1.4567 similar=0.4867 dissim=0.3341 (BEAGLE best substantive); "
                "RI_HUB_SPOKE_KGSTORE ratio=1.3525 similar=0.298 dissim=0.220; "
                "CONTROL_RANDOM_PERMUTE ratio=1.0811 similar=0.673 dissim=0.6225 (can-fail "
                "discriminator armed). cv across all arms = 0.000 (single-seed; vacuous). "
                "Substantive ratios all > control by ~25-37%; mechanism IS armed and "
                "discriminates. No ratio crosses 1.5x bar (cell pre-reg). Headline arm "
                "RI_ALONE 1.368 < 1.5x cert-grade bar = MIDDLE_BAND. Hub-spoke variant "
                "ratio similar to RI_alone but at much lower absolute cosines (compositionality "
                "with KGStore adds structure but doesn't lift signal-to-noise). n_tokens="
                "200000 (text8 smoke); vocab=4533; n_probe=49 words; 100 similar + 100 "
                "dissimilar pairs each arm. Fit walls: bag=7.93s order=40.61s ctrl=22.92s "
                "unit_wall=74.3s. n_llm_calls=0 (substrate-only). Cell self-classified "
                "MIDDLE_BAND citing by-construction-saturation discipline; cert-owner "
                "concurs with MM tiering."
            ),
            "honest_scope": (
                "SMOKE scope only (200k tokens, N_DIM=8192, 1 seed). Substrate-only "
                "distributional-semantic encoding via random-indexing + 2 composition arms "
                "(BEAGLE order + hub-spoke KGStore). MM characterization: 4-arm discriminator "
                "armed; control collapses to 1.08 confirming substantive signal in RI/BEAGLE/"
                "hub-spoke arms. NOT chain-grade until: (a) multi-seed; (b) full text8 corpus "
                "(~17M tokens vs 200k); (c) at least one arm crosses 1.5x bar. Suitable as "
                "MM evidence that substrate-only distributional encoding produces measurable "
                "semantic structure above random-permute control."
            ),
            "n_seeds": 1,
            "N_DIM": 8192,
            "sparsity": 10,
            "window": 5,
            "max_tokens": 200000,
            "run_mode": "smoke",
            "arms": ["RANDOM_INDEXING_ALONE", "RI_PLUS_BEAGLE_ORDER", "RI_HUB_SPOKE_KGSTORE", "CONTROL_RANDOM_PERMUTE"],
            "ratio_RI_ALONE": 1.368,
            "ratio_BEAGLE": 1.457,
            "ratio_HUB_SPOKE": 1.353,
            "ratio_CONTROL": 1.081,
            "headline_arm": "RANDOM_INDEXING_ALONE",
            "headline_ratio": 1.368,
            "zero_llm_calls_at_inference": True,
            "composes_with": [
                "T3/char_trigram_encoder",  # CERT 585
                "T3/kg_traversal",
            ],
            "cites": [
                "Sahlgren_2005_random_indexing",
                "Jones_Mewhort_2007_BEAGLE",
                "Patterson_Nestor_Rogers_2007_ATL_hub_and_spoke",
                "Fix_28_verify_per_arm_not_verdict_msg",
                "by_construction_saturation_tiering",
                "research_brain_drill_substrate_native_relational_semantic_encoding_2026-06-22",
            ],
            "atomized_by": ATOMIZED_BY,
        },
    )


def build_c2_v2_mm() -> Atom:
    return Atom(
        id="T3/EXP_c2_cascade_stc_swr_continual_v2_MM",
        name=(
            "c2 cascade STC+SWR continual v2 (A+C Director option) -- MEASURED_MECHANISM "
            "(SMOKE; C2 1.0 vs C1 0.85 gap=0.15 below HP gap_ok bar)"
        ),
        description=(
            "Cascade STC + SWR-gated expanding-interval replay continual-ingest mechanism "
            "(v2 = Director Option A+C post-mortem from v1: N_DIM 4096->2048, drop NO_REPLAY "
            "arm). SMOKE 1 seed at N_DIM=512 J=4 alpha=1.00. 2 arms: C1_BASELINE (uniform "
            "1:1 replay), CASCADE_STC_SWR (expanding-interval STC+SWR replay). At k=3 "
            "(load-bearing eval) C2=1.000 cv=0.000 vs C1=0.850 gap=0.150. HP gap_ok bar "
            "not crossed (cell HP conditions: c2_above=True gap_ok=False cv_ok=True). "
            "Mechanism IS partial-substantive (C2 saturates while C1 dips at k=3), but "
            "gap below the cert-grade discrimination threshold. cv=0 across all evals "
            "(single-seed = vacuous). NOTE on k_final mismatch: cell reports k_final=3 "
            "but per_seed.per_unit retention_curve shows k=4 with both arms recovering "
            "(C1@k4=0.95, C2@k4=1.0; gap shrinks to 0.05 at k=4) — k=3 is the load-bearing "
            "discriminator and the mechanism characterization. MM scope: cascade-STC-SWR "
            "expanding-interval replay produces seed-stable retention at k=3 where uniform "
            "1:1 dips; need multi-seed + multi-task to discriminate chain-grade. Composes "
            "with c1 CLS-replay CERT atom + cascade-STC mechanism family. Verified-off-data."
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
                "MEASURED_MECHANISM_smoke_v2_A_plus_C_director_option_C2_1p000_vs_C1_0p850_"
                "gap_0p150_at_k3_below_HP_gap_ok_bar_partial_mechanism_n_seeds_1_load_bearing_"
                "discriminator_k3"
            ),
            "cell_commit": "overnight_2026-06-22",
            "metrics_path": "data/exp_c2_cascade_stc_swr_continual_v2_smoke/metrics.json",
            "notes_path": "notes/c2_cascade_stc_swr_continual_v2_design.md",
            "verified_off_data": (
                "cert-owner re-derived from metrics.json detail.by_arm_means: at k=3 "
                "C1_BASELINE=0.85 CASCADE_STC_SWR=1.000 gap=0.150; at k=2 C1=0.95 C2=1.00 "
                "gap=0.05; at k=4 (in per_seed.per_unit retention_curve) C1=0.95 C2=1.00 "
                "gap=0.05 — k=3 is the load-bearing dip point. cv_C2_k_load_bearing=0.0 "
                "(single-seed). HP conditions: c2_above (C2>0.95)=True; gap_ok (gap>0.20)="
                "False; cv_ok=True. Mechanism partial: cascade-STC-SWR preserves retention "
                "where uniform-replay dips by 15pp, but gap below the cert-grade threshold. "
                "n_seeds=1 n_llm=0 elapsed=5.97s. v2 change_set=N_DIM 4096->2048 (Option A) "
                "+ drop NO_REPLAY arm (Option C) per Director post-mortem. SUBSTRATE_only_OK "
                "verified."
            ),
            "honest_scope": (
                "SMOKE scope (J=4 tasks, N_DIM=512, alpha=1.00, 1 seed, synthetic-bipolar). "
                "MM characterization: cascade-STC-SWR expanding-interval replay produces "
                "seed-stable retention at k=3 where uniform 1:1 dips by 15pp. NOT chain-grade "
                "until: (a) multi-seed; (b) gap exceeds 0.20 (cert-grade bar); (c) at "
                "denser/more-tasks regime. NOTE: gap shrinks to 0.05 at k=2 and k=4 — the "
                "k=3 discrimination is specific to that depth. Suitable as mechanism evidence "
                "that expanding-interval SWR-gated replay holds where uniform replay dips."
            ),
            "n_seeds": 1,
            "N_DIM": 512,
            "J_tasks": 4,
            "M_per_task": 128,
            "alpha": 1.0,
            "k_load_bearing": 3,
            "run_mode": "smoke",
            "arms": ["C1_BASELINE", "CASCADE_STC_SWR"],
            "retention_C1_k3": 0.85,
            "retention_C2_k3": 1.000,
            "gap_C2_minus_C1_k3": 0.150,
            "cv_C2_k3": 0.0,
            "v2_change_set": "N_DIM=4096->2048_plus_drop_NO_REPLAY_arm_Director_Option_A_plus_C",
            "zero_llm_calls_at_inference": True,
            "composes_with": [
                "T3/EXP_c1_cls_replay_continual_ingest_v1",
                "T3/EXP_c3_compressed_sequence_replay_v1",
            ],
            "cites": [
                "Fix_28_verify_per_arm_not_verdict_msg",
                "by_construction_saturation_tiering",
                "Director_Option_A_plus_C_v2_post_mortem_2026-06-22",
            ],
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# 7-11. honest_negative atoms (delta=0; CERT-neutral; route to Research for 2x-revival)
# ============================================================================

def build_b2_tinystories_honest_negative() -> Atom:
    return Atom(
        id="T3/EXP_b2_substrate_only_tinystories_lm_v1_HN",
        name=(
            "b2 substrate-only TinyStories LM v1 -- HONEST_NEGATIVE "
            "(SMOKE; substrate ppl 512 > unigram 220; mechanism broken at this config)"
        ),
        description=(
            "Substrate-only language model on TinyStories smoke (V_DIM=1024 N_TRAIN=12000 "
            "N_HELD=1000 VOCAB_CAP=2000, 1 seed). Substrate Hebbian-LM perplexity 512.37 "
            "EXCEEDS unigram-baseline ppl 220.16 = substrate is WORSE than ignoring context. "
            "Accuracy SUB=0.159 < UNI=0.196 < BIGRAM=0.191. Bigram baseline ppl 381 also "
            "below substrate, so substrate even loses to a 2-word context model. Pure-"
            "Hebbian outer-product mechanism on word-level corpus at V_DIM=1024 V=2000 = "
            "broken. Cell verdict HARD_FAIL on the load-bearing must-beat-unigram bar. "
            "HONEST_NEGATIVE atomization: route to Research for 2x-revival angle (possible "
            "angles: V_DIM uplift, MKN smoothing, k-WTA-VQ encoding, whitening — all "
            "established substrate-mine levers from text8 work). Composes with the bigram-"
            "gap-closure arc (USER strategic 2026-06-22) as a smoke-failure data point. "
            "Verified-off-data: ppl + acc per-arm in metrics.json verbatim."
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
                "HONEST_NEGATIVE_smoke_substrate_ppl_512p37_exceeds_unigram_220p16_acc_"
                "SUB_0p159_lt_UNI_0p196_lt_BIGRAM_0p191_pure_Hebbian_word_LM_at_V_DIM_1024_"
                "broken_route_to_research_2x_revival"
            ),
            "cell_commit": "overnight_2026-06-22",
            "metrics_path": "data/exp_b2_substrate_only_tinystories_lm_v1_smoke/metrics.json",
            "notes_path": "notes/b2_substrate_only_tinystories_lm_v1_design.md",
            "verified_off_data": (
                "cert-owner re-derived from metrics.json per_seed: ppl_substrate=512.37, "
                "ppl_unigram=220.16, ppl_bigram=381.17 (substrate WORSE than both baselines); "
                "acc_substrate=0.159, acc_unigram=0.196, acc_bigram=0.191 (substrate worst "
                "of 3 on accuracy too). n_eval=786 V_DIM=1024 V=2000 N_TRAIN=12000 N_HELD=1000 "
                "n_seeds=1 elapsed=1.23s. Pure-Hebbian word-LM mechanism at this scale is "
                "broken: cannot beat unigram or bigram. cell verdict HARD_FAIL on the load-"
                "bearing must-beat-unigram bar (HF_need_beat_unigram=True in config_version)."
            ),
            "honest_scope": (
                "SMOKE scope failure (V_DIM=1024, V=2000, 1 seed). Pure-Hebbian word-LM "
                "substrate cannot beat unigram floor on TinyStories smoke. HONEST_NEGATIVE: "
                "the v1 mechanism config is broken at this scale. Route to Research for "
                "2x-revival angles: V_DIM uplift, MKN smoothing, k-WTA-VQ encoding, whitening, "
                "or alternate Hebbian formulation (sequence-aware vs pair-only)."
            ),
            "n_seeds": 1,
            "V_DIM": 1024,
            "V": 2000,
            "N_TRAIN": 12000,
            "N_HELD": 1000,
            "run_mode": "smoke",
            "ppl_substrate": 512.37,
            "ppl_unigram": 220.16,
            "ppl_bigram": 381.17,
            "acc_substrate": 0.159,
            "acc_unigram": 0.196,
            "acc_bigram": 0.191,
            "failure_mode": "substrate_worse_than_unigram_floor",
            "zero_llm_calls_at_inference": True,
            "composes_with": [],
            "cites": [
                "USER_strategic_bigram_gap_closure_arc_2026-06-22",
                "Fix_28_verify_per_arm_not_verdict_msg",
                "route_negatives_to_research_2x_3x_revival_drills_USER_STANDING_2026-06-20",
            ],
            "route_to_research_2x_revival": True,
            "candidate_revival_angles": ["V_DIM_uplift", "MKN_smoothing", "k_WTA_VQ_encoding", "whitening", "sequence_aware_Hebbian"],
            "atomized_by": ATOMIZED_BY,
        },
    )


def build_att1_honest_negative() -> Atom:
    return Atom(
        id="T3/EXP_att1_iterative_attractor_cleanup_v1_HN",
        name=(
            "att1 iterative-attractor cleanup -- HONEST_NEGATIVE "
            "(SMOKE; best_att1_lift=0.000; mechanism rejected as substrate-mine swap-in)"
        ),
        description=(
            "Iterative soft-attractor cleanup mechanism on HD substrate at N_DIM=512 M=200 "
            "N_EVAL=50 (SMOKE, 1 seed). 4 arms: ARGMAX_BASELINE + 3 ATT1 variants (SOFTATTRACTOR "
            "temp=4, LOW_TEMP=2, HIGH_TEMP=16). At NOISE_HARDER=1.50 (discriminator regime): "
            "argmax=0.040; ATT1_SOFTATTRACTOR=0.040 (tied); ATT1_LOW_TEMP=0.020 (worse); "
            "ATT1_HIGH_TEMP=0.020 (worse). best_att1_lift=0.000, basin_ratio=1.00x. ALL 3 "
            "iterative variants either tie or UNDERPERFORM the single-step argmax baseline. "
            "At NOISE_GENTLE=0.50: argmax=0.34 vs ATT1_SOFTATTRACTOR=0.22 LOW_TEMP=0.20 "
            "HIGH_TEMP=0.30 (all ATT1 variants UNDERPERFORM argmax). Mechanism does NOT "
            "unlock cleanup beyond what argmax already achieves. HONEST_NEGATIVE: this is "
            "the att1 path that would have unblocked n4 + n9 + n10 + p1 if it worked. "
            "Mechanism REJECTED as substrate-mine swap-in. Route to Research for 2x-revival "
            "(modern-Hopfield-style softmax, Krotov dense-associative, or learned attractor "
            "dynamics — the literature lit-scan negative-finding for THIS specific iterative-"
            "softattractor form is now an information point, not a stop signal, per USER "
            "empowerment 2026-06-22). Composes with cleanup-discipline atoms; META primitive "
            "candidate REJECTED at v1. Verified-off-data: per-arm recall_at_1 + basin_robustness "
            "matrix in metrics.json verbatim."
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
                "HONEST_NEGATIVE_smoke_iterative_attractor_does_NOT_unlock_argmax_cleanup_"
                "best_att1_lift_0p000_basin_ratio_1p00x_all_3_ATT1_arms_tie_or_underperform_"
                "argmax_at_both_gentle_and_harder_noise_META_primitive_rejected_at_v1"
            ),
            "cell_commit": "overnight_2026-06-22",
            "metrics_path": "data/exp_att1_iterative_attractor_cleanup_v1_smoke/metrics.json",
            "notes_path": "notes/att1_iterative_attractor_cleanup_v1_design.md",
            "verified_off_data": (
                "cert-owner re-derived from metrics.json per_seed.by_arm: at NOISE_HARDER=1.5 "
                "argmax recall=0.040, ATT1_SOFTATTRACTOR recall=0.040 (tied; no lift), "
                "ATT1_LOW_TEMP recall=0.020 (worse), ATT1_HIGH_TEMP recall=0.020 (worse). "
                "At NOISE_GENTLE=0.5 argmax=0.34 ATT1_SOFTATTRACTOR=0.22 LOW_TEMP=0.20 "
                "HIGH_TEMP=0.30 (all ATT1 underperform argmax). basin_robustness at sigma=1.5: "
                "argmax=0.04 ATT1_SOFTATTRACTOR=0.04 LOW_TEMP=0.02 HIGH_TEMP=0.02. "
                "frac_converged=1.0 all arms (convergence not the issue; mechanism is the "
                "issue). mean_iterations: argmax=1 (single-step), ATT1_SOFTATTRACTOR=3, "
                "LOW_TEMP=4, HIGH_TEMP=3 (3-4x more compute for no recall lift). best_att1_lift_"
                "over_argmax=0.000; basin_ratio_best_att1_over_argmax=1.00x. n_seeds=1 "
                "n_llm=0 elapsed=1.45s. CAN-FAIL discriminator armed and FIRES (mechanism "
                "rejected at this config)."
            ),
            "honest_scope": (
                "SMOKE scope (N_DIM=512, M=200, N_EVAL=50, 1 seed). HD-substrate-native "
                "cleanup-only test (no encoder). 4-arm discriminator with argmax-baseline "
                "as the can-fail floor. RESULT: ALL 3 ATT1 variants tie or underperform "
                "argmax at both noise regimes. Mechanism REJECTED as substrate-mine swap-in. "
                "HONEST_NEGATIVE atomization preserves the negative finding so Research can "
                "route 2x-revival to alternative attractor formulations (modern-Hopfield-"
                "softmax, Krotov dense-associative, learned attractor dynamics)."
            ),
            "n_seeds": 1,
            "N_DIM": 512,
            "M": 200,
            "N_EVAL": 50,
            "run_mode": "smoke",
            "arms": ["ARGMAX_BASELINE", "ATT1_SOFTATTRACTOR", "ATT1_LOW_TEMP", "ATT1_HIGH_TEMP"],
            "best_att1_lift_over_argmax": 0.000,
            "basin_ratio_best_att1_over_argmax": 1.00,
            "discriminator_sigma": 1.5,
            "argmax_recall_harder": 0.040,
            "best_att1_recall_harder": 0.040,
            "failure_mode": "iterative_attractor_does_not_lift_recall_above_single_step_argmax_at_any_noise_regime",
            "zero_llm_calls_at_inference": True,
            "would_have_unblocked_if_worked": ["n4_k_WTA_VQ", "n9_smh", "n10_whitening", "p1_action_at_any_position"],
            "composes_with": [],
            "cites": [
                "Saxena_Bartlett_2024_arXiv_2212p01196_VSA_FSM_attractor",
                "Ramsauer_2021_ICLR_Modern_Hopfield",
                "Krotov_Hopfield_2016_NeurIPS_dense_associative_memory",
                "Fix_28_verify_per_arm_not_verdict_msg",
                "USER_empowered_to_experiment_where_lit_says_dismissed_2026-06-22",
                "route_negatives_to_research_2x_3x_revival_drills_USER_STANDING_2026-06-20",
            ],
            "route_to_research_2x_revival": True,
            "candidate_revival_angles": ["modern_Hopfield_softmax", "Krotov_dense_associative", "learned_attractor_dynamics", "energy_function_redesign"],
            "atomized_by": ATOMIZED_BY,
        },
    )


def build_text8_pseudoLM_honest_negative() -> Atom:
    return Atom(
        id="T3/EXP_text8_substrate_pseudoLM_gpu_v1_HN",
        name=(
            "text8 substrate pseudo-LM gpu v1 -- HONEST_NEGATIVE "
            "(SMOKE; substrate BPC 9.37 > unigram BPC 8.02; substrate WORSE than unigram floor)"
        ),
        description=(
            "Path A pseudo-LM on text8 at GPU-class scale (V=4000 N_DIM=4096 N_TRAIN=100000 "
            "N_HELD=5000, 1 seed; SMOKE). Pure Hebbian W = sum outer(E[w_t+1], E[w_t]) "
            "single-relation NEXT_TOKEN; substrate-only-decode (n_llm=0). 4 arms: "
            "SUBSTRATE_LM_HEBBIAN, UNIGRAM_BASELINE (can-fail floor), WORD_BIGRAM_BASELINE "
            "(hard bar), SUBSTRATE_HEBBIAN_BIGRAM_BACKOFF (composition). Results: substrate "
            "BPC 9.37 > unigram 8.02 (substrate WORSE than ignoring context); bigram BPC "
            "8.33 (substrate also worse than 2-token context); backoff BPC 9.29 (substrate-"
            "first composition arm STILL worse than unigram floor at backoff_thresh=0.05). "
            "Accuracy: SUB=0.198 vs UNI=0.193 vs BIGRAM=0.213 (substrate beats unigram on "
            "acc by 0.5pp but loses on BPC by 1.35 nats = the bpp/acc decoupling is "
            "informative). Local-CPU and remote-CUDA runs produce IDENTICAL metrics "
            "(cv_substrate=0.000 across local/remote = matmul determinism confirmed). "
            "HONEST_NEGATIVE: pure-Hebbian word-LM mechanism at this V/N_DIM is broken. "
            "Composes with the bigram-gap-closure arc as a data point that Path A pseudo-LM "
            "needs structural changes (e.g. MKN smoothing, k-WTA-VQ V_C=4096, whitening "
            "per n10) to clear the unigram floor. Route to Research for 2x-revival. "
            "Verified-off-data: BPC + acc per-arm in metrics.json verbatim."
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
                "HONEST_NEGATIVE_smoke_substrate_BPC_9p37_exceeds_unigram_BPC_8p02_substrate_"
                "WORSE_than_unigram_floor_word_bigram_8p33_also_below_substrate_backoff_9p29_"
                "composition_arm_also_below_floor_pure_Hebbian_word_LM_broken_at_V4000_N4096"
            ),
            "cell_commit": "overnight_2026-06-22",
            "metrics_path": "data/exp_text8_substrate_pseudoLM_gpu_v1_local_smoke/metrics.json",
            "notes_path": "notes/text8_substrate_pseudoLM_gpu_v1_design.md",
            "verified_off_data": (
                "cert-owner re-derived from metrics.json per_seed: SUBSTRATE_LM_HEBBIAN "
                "bpc=9.371 ppl=662.24 acc=0.1984; UNIGRAM_BASELINE bpc=8.024 ppl=260.34 "
                "acc=0.1932 (unigram BEATS substrate on BPC by 1.35 nats); WORD_BIGRAM "
                "bpc=8.330 ppl=321.81 acc=0.2131 (bigram also beats substrate); "
                "SUBSTRATE_HEBBIAN_BIGRAM_BACKOFF bpc=9.290 ppl=626.20 acc=0.2074 (backoff "
                "composition slightly better than substrate alone but still below unigram). "
                "cv_substrate=0.000 between local-CPU and remote-CUDA runs (matmul determinism "
                "confirmed; not a hardware-noise artifact). backoff_frac_substrate=0.696 = "
                "substrate fires 70% of the time and degrades to bigram fallback 30% (and "
                "the 30% bigram-only is what holds backoff close to bigram, but not above "
                "unigram). n_eval=4007 n_llm=0. HARD_FAIL on the load-bearing must-beat-"
                "unigram bar (HF_need_beat_unigram=True). HONEST: this is a clean negative."
            ),
            "honest_scope": (
                "SMOKE scope failure (V=4000, N_DIM=4096, 1 seed, text8 first 100k tokens). "
                "Pure-Hebbian Path A pseudo-LM cannot beat unigram on BPC. HONEST_NEGATIVE: "
                "v1 mechanism config is broken at GPU-class scale; structural changes needed. "
                "Route to Research for 2x-revival: k-WTA-VQ V_C=4096 encoding (n4), MKN "
                "smoothing, whitening (n10), or learned-encoder substitute for raw E[word] "
                "vectors. Composes with bigram-gap-closure arc (USER strategic 2026-06-22) "
                "as a negative data point indicating Path A needs lever-application."
            ),
            "n_seeds": 1,
            "V": 4000,
            "N_DIM": 4096,
            "N_TRAIN": 100000,
            "N_HELD": 5000,
            "run_mode": "smoke",
            "arms": ["SUBSTRATE_LM_HEBBIAN", "UNIGRAM_BASELINE", "WORD_BIGRAM_BASELINE", "SUBSTRATE_HEBBIAN_BIGRAM_BACKOFF"],
            "bpc_substrate": 9.371,
            "bpc_unigram": 8.024,
            "bpc_bigram": 8.330,
            "bpc_backoff": 9.290,
            "acc_substrate": 0.1984,
            "acc_unigram": 0.1932,
            "acc_bigram": 0.2131,
            "failure_mode": "substrate_BPC_exceeds_unigram_floor_pure_Hebbian_word_LM_broken_at_V4000_N4096",
            "local_remote_consistency": "cv_0p000_matmul_determinism_confirmed",
            "zero_llm_calls_at_inference": True,
            "composes_with": [],
            "cites": [
                "USER_strategic_bigram_gap_closure_arc_2026-06-22",
                "L2_MVP_text8_word_bigram_bar_3p84_BPC",
                "Fix_28_verify_per_arm_not_verdict_msg",
                "route_negatives_to_research_2x_3x_revival_drills_USER_STANDING_2026-06-20",
            ],
            "route_to_research_2x_revival": True,
            "candidate_revival_angles": ["k_WTA_VQ_VC_4096_n4", "MKN_smoothing", "whitening_n10", "learned_encoder_substitute"],
            "atomized_by": ATOMIZED_BY,
        },
    )


def build_cross_corpus_compose_honest_negative() -> Atom:
    return Atom(
        id="T3/EXP_cross_corpus_compose_chat_v1_n4096_HN",
        name=(
            "cross-corpus composition chat v1 n4096 -- HONEST_NEGATIVE "
            "(SMOKE; best_compose=single=0.059 lift +0.000)"
        ),
        description=(
            "Cross-corpus composition over chat-style queries with single-corpus, union, "
            "and hub composition strategies. SMOKE 1 seed n=17 queries split across "
            "conceptnet (n=6, single=0.167), hotpotqa (n=6, single=0.000), fb15k (n=5, "
            "single=0.000). All 3 composition strategies tied at single=0.059 union=0.059 "
            "hub=0.059 = composition adds ZERO value above single-corpus retrieval. Per-"
            "corpus: conceptnet contributes 1/6 = 0.167; hotpotqa and fb15k contribute "
            "zero (no answer match in either). Composition cannot add value when 2/3 source "
            "corpora contribute zero retrieval signal. HONEST_NEGATIVE: cross-corpus chat-"
            "composition mechanism at n4096 cannot produce composition lift on chat queries "
            "given the source corpora's chat-coverage. Route to Research for 2x-revival "
            "angles: chat-aware encoder, multi-hop bridging between corpora, or different "
            "corpus mix where each contributes non-zero. Verified-off-data: per-corpus + "
            "composed accuracy in metrics.json verbatim."
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
                "HONEST_NEGATIVE_smoke_best_compose_0p059_equals_single_0p059_lift_plus_0p000_"
                "composition_adds_no_value_above_single_corpus_retrieval_per_corpus_conceptnet_"
                "0p167_hotpotqa_0p000_fb15k_0p000_2_of_3_corpora_contribute_zero_signal"
            ),
            "cell_commit": "overnight_2026-06-22",
            "metrics_path": "data/exp_cross_corpus_compose_chat_v1_n4096_smoke/metrics.json",
            "notes_path": "notes/cross_corpus_compose_chat_v1_n4096_design.md",
            "verified_off_data": (
                "cert-owner re-derived from metrics.json per_seed: n=17 chat queries; "
                "single_acc=0.059 union_acc=0.059 hub_acc=0.059 (all 3 strategies tied). "
                "Per-corpus: conceptnet n=6 single=0.1667 union=0.1667 hub=0.1667; hotpotqa "
                "n=6 single=0.0 union=0.0 hub=0.0; fb15k n=5 single=0.0 union=0.0 hub=0.0. "
                "Composition lift over single-best = 0.000 (no strategy beats the conceptnet-"
                "only single-corpus result). best_compose=UNION (tied). n_llm=0 eval_wall=107s "
                "elapsed=135s. Mechanism null: when 2 of 3 source corpora contribute zero "
                "retrieval, composition cannot manufacture signal."
            ),
            "honest_scope": (
                "SMOKE scope failure (n=17 queries, 1 seed, N_DIM=4096). Cross-corpus chat-"
                "composition mechanism at this corpus mix and query distribution cannot "
                "produce lift above single-corpus best. HONEST_NEGATIVE: not chain-grade; "
                "not even MM (composition machinery has no measurable mechanism signal on "
                "this slice). Route to Research for 2x-revival: chat-aware encoder, multi-"
                "hop bridging, or different corpus mix. NOTE: this is a corpus-coverage "
                "failure, not necessarily a composition-mechanism failure; would need an "
                "evaluation where each source corpus contributes non-zero signal to test "
                "the composition mechanism in isolation."
            ),
            "n_seeds": 1,
            "n_queries": 17,
            "N_DIM": 4096,
            "run_mode": "smoke",
            "arms": ["SINGLE", "UNION", "HUB"],
            "single_acc": 0.059,
            "union_acc": 0.059,
            "hub_acc": 0.059,
            "lift_compose_over_single": 0.000,
            "per_corpus_acc": {"conceptnet": 0.167, "hotpotqa": 0.000, "fb15k": 0.000},
            "failure_mode": "2_of_3_source_corpora_contribute_zero_signal_composition_cannot_add_value",
            "zero_llm_calls_at_inference": True,
            "composes_with": [],
            "cites": [
                "Fix_28_verify_per_arm_not_verdict_msg",
                "route_negatives_to_research_2x_3x_revival_drills_USER_STANDING_2026-06-20",
            ],
            "route_to_research_2x_revival": True,
            "candidate_revival_angles": ["chat_aware_encoder", "multi_hop_bridging", "corpus_mix_with_nonzero_each"],
            "atomized_by": ATOMIZED_BY,
        },
    )


def build_substrate_self_map_v2c_honest_negative() -> Atom:
    return Atom(
        id="T3/EXP_substrate_self_map_v2c_HN",
        name=(
            "substrate_self_map_v2c FULL Store ingest -- HONEST_NEGATIVE "
            "(3 seeds 5709s; cluster_gap=-3 shuffle 38 > real 35; mechanism NULL at full-Store scope)"
        ),
        description=(
            "Genuine substrate-native self-mapping mechanism (vs v1's Director-lexical "
            "scaffolding) at FULL-Store ingest scope. v2c is the Option-2 recovery path "
            "from v2/v2b MIDDLE_BAND attempts: ingest EVERY relations.jsonl triple across "
            "all corpora (~202k relations / ~177k atoms in universe; ~447 chain-grade-atoms "
            "for anchor sampling). 3 seeds (7, 17, 23) at N_DIM=4096, n_anchors=100, "
            "n_rel_samples=20, kset=16. 5709s wall (~95min). Mechanism: char_trigram atom "
            "encode + KGStore_multivalue_Hebbian binding + multi_hop_2hop_neighborhood "
            "Jaccard clustering + random-relation shuffle control. LOAD-BEARING DISCRIMINATOR: "
            "cluster-count difference (real - shuffle). RESULT: mean n_clusters_real=35.0 "
            "(seed7: 50, seed17: 24, seed23: 31) vs mean n_clusters_shuffle=38.0 (seed7: 39, "
            "seed17: 42, seed23: 33); gap=-3.0 (shuffle as granular or MORE granular than "
            "real-relation). cv_clusters_real=0.314 > 0.10 (unstable cluster-count across "
            "seeds). atom_retrieval_recall=1.000 (harness valid; atoms encoded + retrieved "
            "correctly). coh_real=0.329 ~= coh_shuf=0.332 (coherence indistinguishable). "
            "avg_jaccard_vs_v1=0.031 (substrate self-clusters don't match v1 hand-categorized "
            "families). new_cross_family_arrows_real=57 vs shuf=53 (real slightly more cross-"
            "family bridging, but in same order of magnitude). HONEST_NEGATIVE: substrate-"
            "native self-mapping via (char_trigram + KGStore_multivalue_Hebbian + 2hop_"
            "Jaccard) does NOT produce relation-structure-dependent clustering at full-"
            "Store scope. Path REJECTED after v2 / v2b / v2c sequence. Composes with v1 "
            "Director-lexical scaffolding (which DOES cluster but only because the "
            "categorization is Director-imposed, not substrate-derived). Self-improvement "
            "Phase 1 relational-analysis lane needs different mechanism (e.g. denser KG "
            "binding, learned similarity, or substrate-native clustering primitive beyond "
            "Jaccard). Verified-off-data: per-seed n_clusters + cluster_gap + cv in "
            "metrics.json verbatim."
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
                "HONEST_NEGATIVE_FULL_3seeds_5709s_cluster_gap_minus_3_shuffle_38_GE_real_35_"
                "cv_0p314_gt_0p10_substrate_native_self_mapping_NULL_at_full_Store_scope_after_"
                "v2_v2b_v2c_attempts_path_rejected_self_improvement_phase_1_needs_different_"
                "mechanism"
            ),
            "cell_commit": "overnight_2026-06-22",
            "metrics_path": "data/exp_substrate_self_map_v2c/metrics.json",
            "notes_path": "notes/substrate_self_map_v2_design.md",
            "verified_off_data": (
                "cert-owner re-derived from metrics.json per_seed: seed7 n_real=50 n_shuf=39 "
                "gap=+11 coh_real=0.321 coh_shuf=0.334; seed17 n_real=24 n_shuf=42 gap=-18 "
                "coh_real=0.346 coh_shuf=0.320; seed23 n_real=31 n_shuf=33 gap=-2 coh_real="
                "0.319 coh_shuf=0.344. Mean: n_real=35.0 (cv=0.314), n_shuf=38.0, gap_mean=-3.0. "
                "Wild seed-variation in n_real (24-50, ratio 2.08x) confirms cluster-count "
                "discriminator is UNSTABLE across seeds at this scope. avg_jaccard_vs_v1=0.031 "
                "(substrate self-clusters don't match v1 Director-lexical categorization). "
                "atom_retrieval_recall=1.000 all seeds (harness valid). new_cross_family_arrows: "
                "real avg 57 (37/68/66), shuf avg 49 (53/45/50) — real slightly more but "
                "noise-overlap. n_chain_grade_atoms=449 (anchor pool); n_atoms_universe=177488; "
                "n_triples=202402; n_relation_types=47. n_llm=0 substrate_only_ok=True. "
                "elapsed per seed: 1867.5 + 1701.1 + 2136.5 = 5705.1s (matches metrics.elapsed "
                "5709.0s). HARD_FAIL on cluster-gap discriminator + cv stability bars. Honest "
                "negative: mechanism does NOT discriminate relation-structure from shuffle-"
                "structure at this scope."
            ),
            "honest_scope": (
                "FULL 3-seed scope (~95min wall, N_DIM=4096, full-Store ingest). Substrate-"
                "native self-mapping via (char_trigram atom-encode + KGStore_multivalue_Hebbian "
                "binding + multi_hop_2hop_neighborhood Jaccard clustering + random-relation "
                "shuffle control). HONEST_NEGATIVE: cluster_gap=-3 (shuffle as granular or "
                "MORE granular than real); cv_clusters=0.314 unstable across seeds; mechanism "
                "NULL at full-Store scope. v2/v2b/v2c sequence: v2 MIDDLE_BAND -> v2b "
                "MIDDLE_BAND -> v2c (this) HARD_FAIL on cluster-gap bar (cell pre-reg bar "
                "n_clusters>=3 gap>=2). Path REJECTED for self-improvement Phase 1 relational-"
                "analysis lane via this mechanism. Need different mechanism: denser KG "
                "binding (multi-relation per atom), learned similarity replacing 2hop-Jaccard, "
                "or substrate-native clustering primitive (e.g. attractor-dynamics-based). "
                "DOES NOT invalidate v1 Director-lexical self-mapping (which clusters but "
                "because categorization is Director-imposed); v1 represents a different "
                "(lexical-scaffolded) self-mapping mechanism, NOT substrate-derived."
            ),
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "N_DIM": 4096,
            "n_anchors": 100,
            "n_rel_samples": 20,
            "kset": 16,
            "n_chain_grade_atoms": 449,
            "n_atoms_universe": 177488,
            "n_triples": 202402,
            "n_relation_types": 47,
            "run_mode": "full",
            "mean_n_clusters_real": 35.0,
            "mean_n_clusters_shuf": 38.0,
            "cluster_gap": -3.0,
            "cv_n_clusters_real": 0.314,
            "atom_retrieval_recall": 1.000,
            "coh_real_mean": 0.329,
            "coh_shuf_mean": 0.332,
            "avg_jaccard_vs_v1_mean": 0.031,
            "elapsed_total_s": 5709.0,
            "failure_mode": "cluster_gap_negative_shuffle_as_granular_as_real_cv_unstable_substrate_native_self_mapping_null_at_full_Store_scope",
            "zero_llm_calls_at_inference": True,
            "supersedes_attempts": ["substrate_self_map_v2_smoke", "substrate_self_map_v2b", "substrate_self_map_v2c_smoke"],
            "composes_with": [],
            "cites": [
                "USER_strategic_self_improvement_Phase_1_relational_analysis_2026-06-22",
                "v1_Director_lexical_scaffolding_self_map_baseline",
                "Fix_28_verify_per_arm_not_verdict_msg",
                "route_negatives_to_research_2x_3x_revival_drills_USER_STANDING_2026-06-20",
            ],
            "route_to_research_2x_revival": True,
            "candidate_revival_angles": ["denser_KG_binding_multi_relation_per_atom", "learned_similarity_replace_2hop_Jaccard", "attractor_dynamics_substrate_native_clustering", "different_relation_type_subset"],
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# Helpers
# ============================================================================

def safe_add_with_ledger(atom: Atom, ledger_row_builder, source: str, note: str,
                          notes_path: str, metrics_path: str, cv, verdict_text: str,
                          atom_id_full: str, cell_commit: str, expected_delta: int):
    """Add atom + append ledger row in one window.

    delta=+1 for chain_grade; delta=0 for MM / honest_negative.
    """
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"  SKIP (idempotent): {atom.id} already present.")
    else:
        print(f"  ADDING atom: {atom.id}")
        ps.add_atom(atom, source=source, note=note)

        ps2 = PartitionedStore(STORE_ROOT)
        atoms = list(ps2.all_atoms())
        found = next((a for a in atoms if a.id == atom.id), None)
        if found is None:
            print(f"  FAIL: atom not found post-add")
            return (False, None)
        md = found.metadata or {}
        expected_pq = (atom.metadata or {}).get("provenance_quality")
        if md.get("provenance_quality") != expected_pq:
            print(f"  FAIL: pq mismatch (expected {expected_pq}, got {md.get('provenance_quality')})")
            return (False, None)
        print(f"  PASS: round-trip OK (pq={expected_pq})")

    # Live CERT count after add (ledger neutral)
    ps_live = PartitionedStore(STORE_ROOT)
    live_cert = sum(1 for a in ps_live.all_atoms()
                    if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')

    # Build ledger row
    if ledger_row_builder == "chain_grade":
        row = build_chain_grade_ruling_row(
            atom_id=atom_id_full, cell_commit=cell_commit, verdict=verdict_text,
            notes_path=notes_path, metrics_path=metrics_path, cv=cv,
            cert_class="pre_reg_pass", atomized_by=ATOMIZED_BY, note=note,
        )
    elif ledger_row_builder == "measured_mechanism":
        row = build_measured_mechanism_row(
            atom_id=atom_id_full, cell_commit=cell_commit, verdict=verdict_text,
            notes_path=notes_path, metrics_path=metrics_path,
            atomized_by=ATOMIZED_BY, note=note,
        )
    elif ledger_row_builder == "honest_negative":
        row = build_honest_negative_row(
            atom_id=atom_id_full, cell_commit=cell_commit, verdict=verdict_text,
            notes_path=notes_path, metrics_path=metrics_path,
            cert_class="pre_reg_miss_proven_bound",
            atomized_by=ATOMIZED_BY, note=note, verified_off_data=True,
        )
    else:
        raise ValueError(f"unknown builder: {ledger_row_builder}")

    print(f"  appending cert-ledger row (op={row['op']} status={row['cert_status']} delta={row['cert_increment_delta']})")
    try:
        h = append_cert_ledger_row(
            row,
            expected_cert_n_pre=live_cert,
            expected_cert_n_post=live_cert,
        )
        print(f"  row_hash={h}")
        return (True, h)
    except Exception as e:
        print(f"  FAIL: ledger append errored: {e}")
        return (False, None)


# ============================================================================
# Main
# ============================================================================

ATOM_PLAN = [
    # (builder_fn, ledger_builder_name, notes_path, metrics_path, cv, verdict, cell_commit, expected_delta, ledger_note)
    (
        build_a1_gatecheck_chain_grade,
        "chain_grade",
        "notes/a1_substrate_intent_classifier_v1_design.md",
        "data/exp_a1_substrate_intent_classifier_v1_gatecheck/metrics.json",
        0.042,
        "HARD_PASS",
        "overnight_2026-06-22",
        1,
        "a1_substrate_intent_classifier_v1_HARD_PASS_3seeds_FULL_acc_0p761_cv_0p042_maj_mult_4p66_rand_mult_5p23_p95_3p9ms_n_llm_0_char_trigram_substrate_dominates_both_baselines_every_seed_COMPARISON_class_weak_honest_scope_substrate_only_intent_primitive_for_conversational_lane",
    ),
    (
        build_v2_composition_drill_mm,
        "measured_mechanism",
        "notes/research_substrate_native_qa_2x_revival_composition_fix_drill_2026-06-22.md",
        "data/exp_substrate_native_qa_hotpotqa_v2_composition_drill_smoke/metrics.json",
        None,
        "MEASURED_MECHANISM_smoke_best_alpha_0p0_collapses_to_GENERATION_ONLY",
        "overnight_2026-06-22",
        0,
        "substrate_native_qa_v2_composition_drill_MM_SMOKE_best_alpha_0p0_score_fusion_collapses_to_pure_GENERATION_ONLY_composition_did_NOT_add_value_FREQ_BIAS_baseline_0p42_dominates_composed_0p22_NOT_chain_grade_until_full_run_plus_nontrivial_best_alpha_plus_FREQ_BIAS_exceeded",
    ),
    (
        build_a2_templated_mm,
        "measured_mechanism",
        "notes/a2_substrate_templated_response_v1_design.md",
        "data/exp_a2_substrate_templated_response_v1_smoke/metrics.json",
        None,
        "MEASURED_MECHANISM_smoke_gram_lift_0p833_rendering_machinery_real_factual_0p10_retrieval_gated",
        "overnight_2026-06-22",
        0,
        "a2_substrate_templated_response_v1_MM_SMOKE_gram_lift_0p833_real_rendering_machinery_works_TEMPLATED_produces_grammatical_English_RAW_produces_arrow_sequence_BUT_factual_0p10_IDENTICAL_across_all_3_arms_retrieval_ceiling_per_by_construction_saturation_tiering_NOT_QA_accuracy_claim",
    ),
    (
        build_pc1_mm,
        "measured_mechanism",
        "notes/pc1_predictive_coding_residual_gate_v1_design.md",
        "data/exp_pc1_predictive_coding_residual_gate_v1_smoke/metrics.json",
        None,
        "MEASURED_MECHANISM_smoke_PC_PROPORTIONAL_halves_W_norm_zero_recall_loss_lossless_compression_candidate_undersaturated",
        "overnight_2026-06-22",
        0,
        "pc1_predictive_coding_residual_gate_v1_MM_SMOKE_VAN_and_both_PC_arms_recall_1p000_undersaturated_M_80_N_256_alpha_0p3125_CONTROL_drops_to_0p48_discriminator_armed_PC_RESIDUAL_PROPORTIONAL_halves_W_norm_2293_to_1148_zero_recall_loss_lossless_compression_candidate_at_this_scale_NOT_chain_grade_at_saturated_recall",
    ),
    (
        build_n11_mm,
        "measured_mechanism",
        "notes/n11_random_indexing_semantic_v1_design.md",
        "data/exp_n11_random_indexing_semantic_v1_smoke/metrics.json",
        None,
        "MEASURED_MECHANISM_smoke_RI_distributional_signal_partial_BEAGLE_best_1p457_no_arm_crosses_1p5x_bar",
        "overnight_2026-06-22",
        0,
        "n11_random_indexing_semantic_v1_MM_SMOKE_distributional_signal_real_but_partial_RI_alone_1p368_BEAGLE_1p457_HUB_SPOKE_1p353_vs_CONTROL_1p081_no_ratio_crosses_1p5x_bar_cell_self_tiered_by_construction_saturation_discipline_route_to_research_for_multi_seed_plus_full_corpus_replication",
    ),
    (
        build_c2_v2_mm,
        "measured_mechanism",
        "notes/c2_cascade_stc_swr_continual_v2_design.md",
        "data/exp_c2_cascade_stc_swr_continual_v2_smoke/metrics.json",
        None,
        "MEASURED_MECHANISM_smoke_v2_A_plus_C_C2_1p000_vs_C1_0p850_gap_0p150_below_HP_gap_ok_bar",
        "overnight_2026-06-22",
        0,
        "c2_cascade_stc_swr_continual_v2_MM_SMOKE_Director_Option_A_plus_C_post_mortem_N_DIM_4096_to_2048_drop_NO_REPLAY_arm_C2_1p000_vs_C1_0p850_gap_0p150_at_k_load_bearing_3_below_HP_gap_ok_bar_0p20_partial_mechanism_n_seeds_1_route_to_full_run_multi_seed_for_chain_grade_candidacy",
    ),
    (
        build_b2_tinystories_honest_negative,
        "honest_negative",
        "notes/b2_substrate_only_tinystories_lm_v1_design.md",
        "data/exp_b2_substrate_only_tinystories_lm_v1_smoke/metrics.json",
        None,
        "HONEST_NEGATIVE_substrate_ppl_512_exceeds_unigram_220_substrate_WORSE_than_unigram_floor",
        "overnight_2026-06-22",
        0,
        "b2_substrate_only_tinystories_lm_v1_HONEST_NEGATIVE_SMOKE_substrate_ppl_512p37_exceeds_unigram_220p16_substrate_WORSE_than_unigram_floor_acc_substrate_0p159_lt_unigram_0p196_lt_bigram_0p191_pure_Hebbian_word_LM_broken_at_V_DIM_1024_V_2000_route_to_research_2x_revival_angles_V_DIM_uplift_MKN_smoothing_k_WTA_VQ_whitening",
    ),
    (
        build_att1_honest_negative,
        "honest_negative",
        "notes/att1_iterative_attractor_cleanup_v1_design.md",
        "data/exp_att1_iterative_attractor_cleanup_v1_smoke/metrics.json",
        None,
        "HONEST_NEGATIVE_iterative_attractor_does_NOT_unlock_argmax_cleanup_best_att1_lift_0p000_basin_ratio_1p00x_all_3_ATT1_arms_tie_or_underperform_argmax",
        "overnight_2026-06-22",
        0,
        "att1_iterative_attractor_cleanup_v1_HONEST_NEGATIVE_SMOKE_best_att1_lift_0p000_basin_ratio_1p00x_all_3_iterative_variants_SOFTATTRACTOR_LOW_TEMP_HIGH_TEMP_tie_or_underperform_argmax_baseline_at_both_NOISE_GENTLE_and_NOISE_HARDER_META_primitive_REJECTED_as_substrate_mine_swap_in_would_have_unblocked_n4_n9_n10_p1_if_worked_route_to_research_2x_revival_modern_Hopfield_Krotov_learned_attractor",
    ),
    (
        build_text8_pseudoLM_honest_negative,
        "honest_negative",
        "notes/text8_substrate_pseudoLM_gpu_v1_design.md",
        "data/exp_text8_substrate_pseudoLM_gpu_v1_local_smoke/metrics.json",
        None,
        "HONEST_NEGATIVE_substrate_BPC_9p37_exceeds_unigram_BPC_8p02_substrate_WORSE_than_unigram_floor_at_V_4000_N_DIM_4096",
        "overnight_2026-06-22",
        0,
        "text8_substrate_pseudoLM_gpu_v1_HONEST_NEGATIVE_SMOKE_substrate_BPC_9p371_exceeds_unigram_BPC_8p024_by_1p35_nats_word_bigram_BPC_8p330_also_below_substrate_backoff_BPC_9p290_composition_arm_also_below_floor_pure_Hebbian_word_LM_broken_at_V_4000_N_DIM_4096_local_remote_cv_0p000_matmul_determinism_confirmed_NOT_hardware_noise_route_to_research_2x_revival_k_WTA_VQ_VC_4096_MKN_smoothing_whitening_learned_encoder",
    ),
    (
        build_cross_corpus_compose_honest_negative,
        "honest_negative",
        "notes/cross_corpus_compose_chat_v1_n4096_design.md",
        "data/exp_cross_corpus_compose_chat_v1_n4096_smoke/metrics.json",
        None,
        "HONEST_NEGATIVE_best_compose_0p059_equals_single_0p059_lift_plus_0p000_composition_adds_no_value_above_single_corpus_retrieval",
        "overnight_2026-06-22",
        0,
        "cross_corpus_compose_chat_v1_n4096_HONEST_NEGATIVE_SMOKE_best_compose_0p059_equals_single_0p059_union_0p059_hub_0p059_lift_plus_0p000_composition_adds_no_value_per_corpus_conceptnet_0p167_hotpotqa_0p000_fb15k_0p000_2_of_3_source_corpora_contribute_zero_signal_corpus_coverage_failure_route_to_research_2x_revival_chat_aware_encoder_multi_hop_bridging_different_corpus_mix",
    ),
    (
        build_substrate_self_map_v2c_honest_negative,
        "honest_negative",
        "notes/substrate_self_map_v2_design.md",
        "data/exp_substrate_self_map_v2c/metrics.json",
        None,
        "HONEST_NEGATIVE_FULL_3seeds_5709s_cluster_gap_minus_3_shuffle_as_granular_as_real_cv_0p314_unstable_substrate_native_self_mapping_NULL_at_full_Store_scope",
        "overnight_2026-06-22",
        0,
        "substrate_self_map_v2c_HONEST_NEGATIVE_FULL_3seeds_seeds_7_17_23_5709s_95min_wall_N_DIM_4096_full_Store_ingest_202k_triples_177k_atoms_47_relation_types_449_chain_grade_anchors_mean_n_clusters_real_35_vs_shuf_38_gap_minus_3_cv_real_0p314_gt_0p10_unstable_atom_retrieval_recall_1p000_harness_valid_coh_real_0p329_eq_coh_shuf_0p332_avg_jaccard_vs_v1_0p031_substrate_self_clusters_do_NOT_match_v1_Director_lexical_categorization_path_REJECTED_after_v2_v2b_v2c_sequence_self_improvement_Phase_1_needs_different_mechanism_denser_KG_binding_learned_similarity_attractor_clustering_n_llm_0_substrate_only_ok",
    ),
]


def main() -> int:
    if "--apply" not in sys.argv:
        print("DRY: pass --apply to mutate Store + ledger.")
        print(f"Plan: {len(ATOM_PLAN)} atomizations")
        for i, item in enumerate(ATOM_PLAN, 1):
            builder, lb, _, _, _, _, _, delta, _ = item
            a = builder()
            print(f"  {i}. {a.id}  pq={a.metadata['provenance_quality']}  ledger_op={lb}  delta=+{delta if delta>0 else 0}")
        return 0

    # A5 PRE
    ps = PartitionedStore(STORE_ROOT)
    atoms_pre = list(ps.all_atoms())
    n_atoms_pre = len(atoms_pre)
    cert_pre = sum(1 for a in atoms_pre if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
    print(f"A5-PRE: n_atoms={n_atoms_pre} CERT N={cert_pre}")
    expected_delta_atoms = len(ATOM_PLAN)
    expected_delta_cert = sum(d for _,_,_,_,_,_,_,d,_ in ATOM_PLAN)
    print(f"Expected delta: atoms +{expected_delta_atoms}; CERT +{expected_delta_cert}")
    print()

    row_hashes = []
    for i, item in enumerate(ATOM_PLAN, 1):
        builder, lb, notes_path, metrics_path, cv, verdict_text, cell_commit, delta, ledger_note = item
        atom = builder()
        atom_id_full = f"{atom.corpus.value}::{atom.id}"
        print(f"=== {i}/{len(ATOM_PLAN)}: {atom.id}  (pq={atom.metadata['provenance_quality']} delta=+{delta})")
        ok, h = safe_add_with_ledger(
            atom, lb,
            source=ATOMIZED_BY,
            note=ledger_note,
            notes_path=notes_path,
            metrics_path=metrics_path,
            cv=cv,
            verdict_text=verdict_text,
            atom_id_full=atom_id_full,
            cell_commit=cell_commit,
            expected_delta=delta,
        )
        if not ok:
            print(f"ABORT at item {i}")
            return 1
        row_hashes.append((atom.id, h))
        print()

    # A5 POST
    ps_post = PartitionedStore(STORE_ROOT)
    atoms_post = list(ps_post.all_atoms())
    n_atoms_post = len(atoms_post)
    cert_post = sum(1 for a in atoms_post if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
    print("=" * 72)
    print(f"A5-POST: n_atoms={n_atoms_post} (delta +{n_atoms_post-n_atoms_pre}, expected +{expected_delta_atoms})")
    print(f"         CERT N={cert_post} (delta +{cert_post-cert_pre}, expected +{expected_delta_cert})")
    print("=" * 72)
    print("Row hashes:")
    for aid, h in row_hashes:
        print(f"  {h}  {aid}")

    if (n_atoms_post - n_atoms_pre) != expected_delta_atoms:
        print("WARNING: atom count drift")
        return 1
    if (cert_post - cert_pre) != expected_delta_cert:
        print("WARNING: CERT count drift")
        return 1
    print("A5 invariants PRESERVED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
