"""
A5-gated atomization: exp_base_reader_grounded_relations_coref_v1 (commit ae23c4b42) -> ONE atom (2026-07-18).
  MEASURED_MECHANISM: the FIRST reader-arc POSITIVE, scoped. Grounded words + REAL packaged WorkingOverlay
  coref (recency) + glass-box grade-1 relation extractor COMPOSE into an end-to-end pipeline that correctly
  comprehends multi-hop McGuffey grade-1 questions. GENUINELY-EMPIRICAL kernel = overlay coref accuracy 6/7
  + coref-dependent 2-hop composition beating frequency. BOUNDED: extraction is CONSTRUCTION-FORCED (NC=1.000
  both arms; extractor hand-tuned to the 7 passages), coref is EASY (5/7 gender-exclusion-to-singleton), and
  the whole thing lives INSIDE the hand-rule extraction wall proven by read_grow_reread HF (0.44 on real prose).

Cell verdict was HARD_PASS. Auditor DEMOTES to MEASURED_MECHANISM (proven-bound): the load-bearing HARD_PASS
discriminators are partly tautological (coref_lift vs a forced-zero no-coref baseline; relation_lift dominated
by construction-forced NC extraction). Independent off-disk recompute (.venv; Fix #28): byte-reproduces EXACT;
per-Q correctness re-derived from answers-vs-gold matches author per_q for all 3 arms; slice accuracies
independently recomputed. Author's honest caveats (floor-close-on-CO, she->pet fail, small N) all CONFIRMED.
LOCAL ONLY: store_head_at_write=unsynced_needs_orchestrator; NO origin push; NO remote persist.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"
ATOMIZED_BY = "skunkworks_landed_vet_base_reader_grounded_relations_coref_v1_MM_first_reader_arc_positive_scoped_2026-07-18"
ATOMIZED_DATE = "2026-07-18"
ANCHOR = "base_reader_grounded_relations_coref_v1"
CELL_COMMIT = "ae23c4b42"

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

XARC = (
    "substrate_query.sh 'reader coref overlay grow relations comprehension grounded words' -> top hits are "
    "GENERIC concept/wordnet atoms: 'grounder' cosine=0.3105, 'comprehension' 0.3066, a note "
    "F2_ABSTRACTION_RATIO 0.3037, 'Word_relations' framenet 0.2832. NO prior ARC EXPERIMENT CELL returns above "
    "cosine 0.30 -- the >0.30 hits are foundation concept atoms, not a prior reader-arc run. This is genuinely "
    "novel as an experiment: a TARGETED EXTENSION of the reader arc that COMPOSES the packaged WorkingOverlay "
    "(first validated in the 2026-07-17 state-of-mind arc) with a grade-1 relation extractor. Not a rediscovery."
)

ATOM_ID = (
    "math::MM_base_reader_grounded_relations_coref_v1_FIRST_reader_arc_POSITIVE_scoped_grounded_words_plus_REAL_"
    "packaged_WorkingOverlay_recency_coref_plus_glassbox_grade1_relation_extractor_COMPOSE_into_end_to_end_"
    "pipeline_that_correctly_comprehends_multihop_McGuffey_grade1_Qs_full_all_0p920_CO_0p857_NC_1p000_CMP_0p800_"
    "vs_nocoref_0p600_0p143_1p000_0p200_vs_freq_floor_0p600_0p714_0p615_0p400_HARD_PASS_DEMOTED_to_MM_because_"
    "the_load_bearing_discriminators_are_PARTLY_TAUTOLOGICAL_coref_lift_0p714_p0p0002_is_full_minus_nocoref_on_"
    "CO_but_nocoref_CANNOT_resolve_ANY_pronoun_by_construction_so_fails_every_coref_required_Q_forced_zero_and_"
    "relation_lift_0p320_p0p0022_is_DOMINATED_by_CONSTRUCTION_FORCED_NC_extraction_full_1p000_vs_floor_0p615_"
    "the_SVO_attr_loc_poss_extractor_plus_STOPWORDS_GROUNDING_OVERRIDE_ACTION_VERBS_are_hand_tuned_to_these_"
    "exact_7_passages_NC_1p000_BOTH_arms_is_tautological_not_discovered_GENUINELY_EMPIRICAL_kernel_is_the_"
    "overlay_coref_ACCURACY_6of7_CO_single_miss_P2c_she_to_pet_recency_binds_nearer_gender_any_pet_over_farther_"
    "fem_Kitty_plus_coref_dependent_2hop_COMPOSITION_full_0p800_beats_floor_0p400_and_nocoref_0p200_with_2_"
    "genuine_structural_wins_P3d_hen_via_poss_coref_and_P5d_hand_via_loc_of_2hop_but_coref_is_EASY_5of7_CO_are_"
    "gender_number_exclusion_to_a_SINGLE_remaining_candidate_only_P3_her_hen_vs_duck_and_P4_his_dog_vs_Tom_"
    "resolve_among_multiple_same_agreement_cands_and_both_by_recency_happening_right_AND_on_the_honest_frequency_"
    "floor_overlay_barely_wins_single_hop_CO_6of7_vs_5of7_net_plus1_lives_INSIDE_the_hand_rule_extraction_wall_"
    "proven_by_read_grow_reread_HF_0p44_on_real_Brown_prose_small_N_CO7_CMP5_byte_reproduce_exact_seed12345_"
    "omp1_real_UNMODIFIED_overlay_ae23c4b42_2026-07-18"
)

ATOM_CLAIM = (
    "MATH MEASURED_MECHANISM (proven-bound; the FIRST reader-arc POSITIVE, but a CONSTRUCTION-PROOF-of-composition "
    "scoped well below its HARD_PASS framing). CLAIM: with word meanings GROUNDED up front (WordNet lexname + "
    "curated grade-1 category/name-gender = the dictionary/picture stand-in), the REAL packaged "
    "hdlab.state_of_mind.WorkingOverlay (recency strategy, UNMODIFIED -- only fed grounded gender/animacy "
    "attributes) plus a glass-box grade-1 relation extractor (SVO / attribute / location / possession) COMPOSE "
    "into an end-to-end reader that correctly comprehends multi-hop questions over 7 real cleaned McGuffey First "
    "Reader passages (25 hand-authored independent-gold Qs). full acc: all 0.920, NC 1.000 (13/13), CO 0.857 "
    "(6/7), CMP 0.800 (4/5) vs no-coref ablation 0.600/1.000/0.143/0.200 and grounded frequency floor "
    "0.600/0.615/0.714/0.400. "
    "AUDITOR DEMOTION HARD_PASS->MM, and the load-bearing separation of DISCOVERED vs CONSTRUCTION-FORCED: "
    "(1) NC=1.000 in BOTH the full AND no-coref arms is CONSTRUCTION-FORCED, not a discovered capability -- the "
    "extractor's ACTION_VERBS / STOPWORDS / GROUNDING_OVERRIDE dicts are hand-authored to exactly these 7 "
    "passages, so 'reading grows relations' on the single-sentence NC slice is tautological. relation_lift=0.320 "
    "(p=0.0022) is DOMINATED by this forced NC extraction (full NC 1.000 vs floor 0.615). "
    "(2) coref_lift=0.714 (p=0.0002) is PARTLY TAUTOLOGICAL: the no-coref arm leaves every pronoun unresolved and "
    "therefore CANNOT answer ANY genuinely coref-required Q by construction (forced-zero baseline). The empirical "
    "content is not the lift over that forced baseline but the overlay's RESOLUTION ACCURACY = 6/7 on CO. "
    "(3) The GENUINELY-DISCOVERED, load-bearing kernel: the UNMODIFIED overlay, given grounded gender/animacy, "
    "correctly resolves 6/7 coref-required McGuffey references AND coref-resolved relations enable 2-hop "
    "COMPOSITION (full 0.800) that beats BOTH frequency (0.400) and the unresolved baseline (0.200), with 2 "
    "genuine structural wins that frequency cannot get (P3d 'whose nest' = hen via possessive coref; P5d 'where "
    "is Ned's pen' = hand via a real 2-hop poss->loc join). "
    "(4) BUT the coref task is EASY: 5 of the 7 CO resolutions collapse to a SINGLE compatible candidate after "
    "gender/number agreement (e.g. she->hen because masc Ned is excluded and hen is the only other entity); only "
    "P3 (her->hen among hen/duck, both animal gender-any) and P4 (his->dog among dog/Tom, both masc) resolve "
    "among multiple same-agreement candidates, and both succeed only because recency happens to be right. "
    "(5) On the HONEST floor (grounded frequency), the overlay barely wins the single-hop CO slice: full 6/7 vs "
    "floor 5/7 = net +1 Q -- frequency nearly matches because in short passages the coref target is usually the "
    "salient/frequent entity. The real structure-beats-frequency signal is the COMPOSITION slice, not CO. "
    "(6) One documented FAILURE (P2c 'who fed the pet' -> full=null): the overlay mis-resolves 'she' to the "
    "nearer gender-any 'pet' over the farther fem 'Kitty' (recency + animal-gender-unknown = compatible) -- a "
    "FAIR, faithful overlay limitation that also cascades to fail P2e composition. "
    "SCOPE: this is a CONSTRUCTION-PROOF that the packaged overlay + grounding + glass-box extraction COMPOSE "
    "into working multi-hop comprehension, with the coref-accuracy piece genuinely empirical -- it is NOT "
    "evidence that reading-grows-relations is a DISCOVERED capability (extraction is hand-built), and it works "
    "here precisely because the corpus is tiny, simple grade-1 SVO, hand-matched to the extractor. It lives "
    "strictly INSIDE the hand-rule extraction wall (0.44) that read_grow_reread_compounding_kgguided_v1 already "
    "PROVED on real Brown prose."
)

ATOM_RECOMPUTE = (
    "INDEP recompute (.venv Scripts/python, NOT verdict_msg; Fix #28): (A) self-test PASSES (she->hen resolved "
    "via real overlay; arms differ; full_CO 0.857 > nocoref_CO 0.143). (B) Full run BYTE-REPRODUCES the "
    "discriminators/arms/gates/questions/coref_resolutions_sample IDENTICAL across a second run (ts differs "
    "only) -> deterministic (seed 12345, OMP=1). (C) Re-derived per-Q correctness INDEPENDENTLY from "
    "answers-vs-gold (normalize+compare, ignoring author per_q) -> EXACT match to author per_q for ALL 3 arms. "
    "Slice recompute: full NC 13/13, CO 6/7, CMP 4/5, all 23/25=0.920; nocoref NC 13/13, CO 1/7, CMP 1/5, all "
    "15/25; floor NC 8/13=0.615, CO 5/7=0.714, CMP 2/5, all 15/25. coref_lift = full_CO 0.857 - nocoref_CO "
    "0.143 = 0.714 (confirmed); relation_lift = 0.920 - 0.600 = 0.320 (confirmed); composition_full = 0.800 "
    "(confirmed). (D) CO disagreement audit full-vs-floor: they differ on P1d (full nest RIGHT / floor has "
    "WRONG), P2b (full sing RIGHT / floor None WRONG), P2c (full None WRONG / floor kitty RIGHT) -> net full +1 "
    "over frequency on single-hop CO. (E) Composition win audit: full beats floor on P3d (hen vs duck) and P5d "
    "(hand vs box) -- the 2 genuine coref-dependent structural wins; P1e/P7b both also solved by floor "
    "(frequency flukes); P2e failed by full (she->pet cascade). (F) coref_resolutions_sample confirms the "
    "she->pet mis-resolution in P2 and correct resolutions elsewhere (she->hen, her->hen, his->dog, he/his->ned, "
    "she->cow, she->nell, it->pan). (G) Overlay is the REAL packaged hdlab.state_of_mind.WorkingOverlay "
    "(observe/resolve_pronoun signatures bound in self-test); the cell feeds grounded gender only, resolution "
    "LOGIC untouched. Uses strategy='recency' (NOT the packaged default 'maintained'), which is the correct + "
    "brain-aligned choice for the all-short-distance grade-1 regime (consistent with the longdist MM finding "
    "that recency owns short distance)."
)

ATOM_SCOPE = (
    "GRADE-1 toy: 7 hand-picked McGuffey First Reader passages (2-4 short sentences each), 25 hand-authored Qs "
    "(NC=13, CO=7, CMP=5), a hand-tuned glass-box extractor, and the REAL packaged overlay fed curated grounding "
    "-- glass-box symbolic, NO LLM, NO HD primitive (relations are Python tuples). Load-bearing BOUNDS: "
    "(a) EXTRACTION IS CONSTRUCTION-FORCED -- the extractor dicts are hand-matched to these exact passages, so "
    "NC=1.000 (both arms) and the bulk of relation_lift are tautological; do NOT read this as 'reading grows "
    "relations' being a discovered capability. (b) COREF IS EASY -- 5/7 CO resolutions are single-candidate "
    "after agreement; only 2 exercise recency among competitors; the 1 competitive+non-recency case that WOULD "
    "test the mechanism harder (she vs pet vs Kitty, P2) is the one that FAILS. (c) OVERLAY BARELY BEATS "
    "FREQUENCY on single-hop CO (+1/7); the genuine structural edge is the n=5 composition slice. (d) SMALL N "
    "(CO=7, CMP=5) -- the bootstrap p-values (0.0002, 0.0022) are on tiny slices and the composition claim has "
    "NO p-gate. (e) LIVES INSIDE the proven hand-rule extraction wall (read_grow_reread_kgguided_v1 HF, 0.44 on "
    "real Brown prose) -- this positive exists BECAUSE the corpus is tiny and hand-matched; it does NOT breach "
    "that wall. BRAIN-CHECK: relation-comprehension here = positional SVO hand-rules producing Python tuples, "
    "NOT the substrate's native HD role-filler BIND -- so this is NOT a demonstrated Frontier-2 substrate-native "
    "advantage; the mechanism is a hand-rule SHORTCUT (thematic roles assigned by surface position, not by the "
    "thematic-role machinery the parallel drill a7a02502 is mapping). The overlay's coref (recency + weak "
    "agreement) IS loosely brain-aligned for LOCAL/short-distance resolution (Hobbs recency), and the grade-1 "
    "regime is entirely short-distance, so recency is the appropriate + brain-consistent strategy here. "
    "REVIVAL to CG: (1) run the SAME overlay+extraction pipeline on HELD-OUT passages the extractor was NOT "
    "tuned on (or a LEARNED extractor), showing coref-accuracy + composition survive when extraction is not "
    "hand-matched; (2) expand CO/CMP N by 3-5x with genuinely competitive multi-candidate coref (multiple "
    "same-gender entities where recency is NOT the right answer, so the overlay's agreement+salience must do "
    "real work); (3) show the overlay beats the frequency floor on single-hop CO by more than a single Q."
)

ATOM_METRICS = {
    "full": {"acc_all": 0.920, "acc_NC": 1.000, "acc_CO": 0.857, "acc_CMP": 0.800},
    "nocoref": {"acc_all": 0.600, "acc_NC": 1.000, "acc_CO": 0.143, "acc_CMP": 0.200},
    "floor": {"acc_all": 0.600, "acc_NC": 0.615, "acc_CO": 0.714, "acc_CMP": 0.400},
    "coref_lift": 0.714, "coref_lift_p_le0": 0.0002,
    "relation_lift": 0.320, "relation_lift_p_le0": 0.0022,
    "composition_full": 0.800, "nc_control_delta": 0.0,
    "slice_counts": {"NC": 13, "CO": 7, "CMP": 5},
    "overlay_coref_accuracy_CO": "6of7",
    "coref_single_candidate_after_agreement": "5of7_CO_gender_or_number_exclusion_to_singleton",
    "coref_competitive_recency_cases": {"P3_her_hen_vs_duck": "correct", "P4_his_dog_vs_Tom": "correct",
                                        "P2_she_kitty_vs_pet": "FAIL_recency_picks_nearer_pet"},
    "genuine_structural_composition_wins_over_frequency": {"P3d_whose_nest": "hen_via_poss_coref",
                                                           "P5d_where_ned_pen": "hand_via_2hop_poss_to_loc"},
    "floor_frequency_fluke_wins": {"P1e": "hen", "P7b": "eggs"},
    "single_hop_CO_full_vs_floor": "6of7_vs_5of7_net_plus1",
    "documented_failure": "P2c_she_to_pet_mis_resolution_cascades_to_P2e_composition_fail",
    "byte_reproduce": "exact_discriminators_arms_gates_questions_coref_sample_seed12345_omp1",
    "overlay": "real_UNMODIFIED_hdlab.state_of_mind.WorkingOverlay_strategy_recency",
    "construction_forced_component": "NC_1p000_both_arms_extractor_hand_tuned_to_7_passages_relation_lift_dominated_by_NC",
    "genuinely_discovered_component": "overlay_coref_accuracy_6of7_plus_coref_dependent_2hop_composition_2_genuine_wins",
    "cell_verdict": "HARD_PASS",
    "auditor_tier": "MEASURED_MECHANISM (demoted from HARD_PASS; construction-forced extraction + easy coref + small N + inside 0.44 hand-rule wall)",
}

COMPOSES = [
    "LIVES INSIDE / is bounded by math::HARD_FAIL_read_grow_reread_compounding_kgguided_v1 (commit ddfd17f34, HF): "
    "that cell PROVED hand-rule KG_APPOS/COREF extraction fires almost entirely SPURIOUSLY on real Brown prose "
    "and hits a 0.44 extraction wall; compounding requires LEARNED comprehension beyond local hand-rules. THIS "
    "positive does not breach that wall -- it works only because the 7 grade-1 passages are tiny and the "
    "extractor is hand-matched to them. The two are CONSISTENT: hand-rules comprehend hand-matched simple SVO "
    "(here) but NOT open real prose (there). The revival criteria target exactly this gap (held-out / learned "
    "extractor).",
    "REGIME-composes with math::LANDED_VET_read_discourse_overlay_longdist_reference_v1 (commit 49bb99c24, MM): "
    "that MM established RECENCY owns SHORT-distance reference (freq owns long-distance). This cell operates "
    "entirely in the short-distance grade-1 regime and correctly uses strategy='recency' -- its 6/7 coref "
    "accuracy is a within-regime confirmation of that boundary, and its 1 failure (she->pet) is the recency "
    "tie-break behaving as the longdist VET documented.",
    "CONTINUES the reader arc past math::MIDDLE_BAND_base_first_reader_heldout_context_learn_v1 (50e4a73c0, MB) "
    "and the pivot-motivating math::HARD_FAIL_base_first_reader_crosssentence_thematic_overlay_v1 (781125f41, "
    "HF): those established that grade-1 word-MEANING inference from sparse text is a dead-end and that grade-1 "
    "reading is comprehension-among-KNOWN-grounded-words. This cell tests the PIVOT (ground the words, then grow "
    "RELATIONS) and returns the first POSITIVE for it -- scoped as a construction-proof-of-composition.",
    "USES the packaged hdlab.state_of_mind.WorkingOverlay first validated + VET'd in the 2026-07-17 two-layer "
    "state-of-mind arc (overlay layer; recency/salience double-dissociation). This is the first DOWNSTREAM "
    "consumer of that packaged module in the reader arc -- a construction-proof that the packaged overlay drops "
    "into a reading pipeline unmodified.",
    "credit: McGuffey First Reader (public-domain grade-1 corpus); WordNet (grounding stand-in); the overlay's "
    "recency/Hobbs-style local resolution (brain-aligned short-distance reference). Extractor + query engine + "
    "gold are original to this cell (hand-authored, honestly flagged as construction-favored by the author).",
]

OVER_READS = [
    "The cell's HARD_PASS verdict OVER-READS. coref_lift=0.714 (p=0.0002) is presented as the primary "
    "discriminator, but the no-coref baseline is FORCED to zero on coref-required Qs (it cannot resolve any "
    "pronoun by construction), so the lift is partly tautological; the empirical content is the overlay's "
    "RESOLUTION ACCURACY (6/7), not the lift. Demoted to MM.",
    "relation_lift=0.320 is framed as 'relation structure beats frequency', but it is DOMINATED by the "
    "construction-forced NC slice (full 1.000 vs floor 0.615) where the extractor is hand-tuned to the passages. "
    "On the HONEST single-hop CO slice the overlay beats frequency by only +1/7 (6 vs 5). The genuine "
    "structure-beats-frequency signal is the n=5 composition slice, not the headline relation_lift.",
    "'Grounded words + overlay coref GROW correct relations' (verdict_msg) reads as a discovered capability, but "
    "the RELATION-GROWTH (extraction) is construction-forced; only the COREF-ACCURACY and the coref-dependent "
    "COMPOSITION are genuinely empirical. The honest framing: the packaged overlay + grounding + a hand-built "
    "extractor COMPOSE into working comprehension on hand-matched grade-1 text.",
    "composition=0.800 is n=5 with 2 of the 4 full-correct Qs also solved by the frequency floor (P1e, P7b) -- "
    "the genuine coref-dependent composition wins are 2 (P3d, P5d). Too thin to bank as chain-grade.",
]

REVIVAL = [
    "run the SAME overlay+extraction pipeline on HELD-OUT McGuffey passages the extractor dicts were NOT tuned "
    "on (or swap in a LEARNED extractor), showing coref-accuracy + composition survive when extraction is not "
    "hand-matched -- this is the decisive test that separates the genuine overlay contribution from the "
    "construction-forced extractor.",
    "expand CO/CMP N by 3-5x with genuinely COMPETITIVE multi-candidate coref: passages with multiple "
    "same-gender entities where RECENCY is NOT the correct antecedent, forcing the overlay's agreement + "
    "maintained-salience to do real work (the current set has only 2 competitive cases and 1 of them fails).",
    "show the overlay beats the grounded frequency floor on SINGLE-HOP CO by more than a single question (the "
    "current +1/7 is within noise at n=7).",
    "if held-out extraction COLLAPSES (as read_grow_reread_kgguided HF predicts for open prose), the correct "
    "conclusion is that the composition works only under hand-matched extraction and the genuine banked kernel "
    "narrows to 'the packaged overlay resolves grade-1 short-distance coref at ~6/7 given grounded agreement'.",
]

GENUINE_POS = (
    "GENUINE kernel preserved symmetrically (NOT dismissed to a null): the REAL UNMODIFIED packaged "
    "WorkingOverlay, fed only grounded gender/animacy, correctly resolves 6/7 coref-required references on real "
    "(if simple) McGuffey text, and coref-resolved relations enable 2-hop COMPOSITION with 2 genuine structural "
    "wins (P3d whose-nest=hen via possessive coref; P5d where-is-Neds-pen=hand via a real poss->loc join) that "
    "the frequency floor and the unresolved baseline both MISS. The overlay is unmodified packaged code and was "
    "NOT tuned for this task, so its coref accuracy is a real, load-bearing empirical result. This IS the first "
    "reader-arc positive -- scoped as a construction-proof that the packaged overlay + grounding + glass-box "
    "extraction COMPOSE into working multi-hop comprehension, with the coref-accuracy piece genuinely earned. "
    "Author is CREDITED for honest caveat-flagging (floor-close-on-CO, she->pet fail, small N, and the "
    "construction-determinism caveat written into the cell docstring) -- the auditor's demotion sharpens, not "
    "overturns, the author's own stated bounds."
)


def build_atom():
    return {
        "id": ATOM_ID, "name": ATOM_CLAIM, "corpus": "math", "tier": "MEASURED_MECHANISM",
        "kind": "experiment_landed_vet",
        "cert_status": "proven_bound",
        "cert_class": ("first_reader_arc_positive_scoped_construction_proof_of_composition_genuine_overlay_coref_"
                       "accuracy_6of7_plus_coref_dependent_2hop_composition_bounded_by_construction_forced_"
                       "extraction_NC_1p000_both_arms_easy_coref_5of7_singleton_small_N_inside_0p44_hand_rule_wall"),
        "description": (ATOM_CLAIM + "\n\nRECOMPUTE (off-disk .venv, Fix #28): " + ATOM_RECOMPUTE
                        + "\n\nHONEST SCOPE: " + ATOM_SCOPE),
        "aliases": [], "ts_iso": _iso, "ts": _ts,
        "metadata": {
            "provenance_quality": "byte_reproduce_exact_seed12345_omp1_plus_independent_perQ_and_slice_recompute_off_disk",
            "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes": None,
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_base_reader_grounded_relations_coref_v1/metrics.json",
            "verified_off_data": ATOM_RECOMPUTE, "honest_scope": ATOM_SCOPE, "metrics": ATOM_METRICS,
            "over_reads_corrected": OVER_READS,
            "genuine_positives_symmetric_anti_negativity": GENUINE_POS,
            "revival_criteria": REVIVAL,
            "cross_arc_overlap_check": XARC,
            "cites": [
                "Fix_28_verify_off_data_not_verdict_msg",
                "symmetric_anti_negativity_verify_both_directions_USER",
                "cited_number_must_reproduce_from_cell",
                "verify_the_referent_atom_ids_mechanism_metric_regime",
                "synthetic_toy_corpus_outcomes_can_be_construction_determined_real_questions_need_real_data",
                "construction_proof_not_capability_win_could_it_fail_informatively",
                "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
                "every_negative_and_positive_brain_check_mechanism_vs_shortcut",
            ],
            "composes_with": COMPOSES,
            "atomized_by": ATOMIZED_BY, "atomized_date": ATOMIZED_DATE,
            "needs_orchestrator_store_sync": True,
            "local_write_only_no_origin_push_no_remote_persist": True,
        },
    }


def ledger_row(atom):
    return {
        "op": "cert_ruling", "corpus": "math", "tier": atom["tier"], "cert_status": atom["cert_status"],
        "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes_commit": None,
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True,
        "auditor": "hdi_skunkworks", "atomized_by": ATOMIZED_BY,
        "verdict": ("MEASURED_MECHANISM_demoted_from_HARD_PASS_first_reader_arc_positive_scoped_construction_proof_"
                    "of_composition_genuine_overlay_coref_6of7_plus_2hop_composition_bounded_construction_forced_NC_"
                    "extraction_easy_coref_small_N_inside_0p44_hand_rule_wall_byte_reproduce_exact"),
        "cert_increment_delta": 1,
        "decision": (
            "MM (proven-bound), DEMOTED from the cell's HARD_PASS. Byte-reproduces EXACT off-disk; per-Q "
            "re-derived from answers-vs-gold matches author per_q for all 3 arms. The HARD_PASS discriminators "
            "are partly tautological: coref_lift=0.714 is full minus a FORCED-ZERO no-coref baseline (cannot "
            "resolve any pronoun by construction); relation_lift=0.320 is dominated by CONSTRUCTION-FORCED NC "
            "extraction (full NC 1.000 vs floor 0.615, extractor hand-tuned to the 7 passages). GENUINELY "
            "EMPIRICAL kernel = overlay coref accuracy 6/7 CO (real UNMODIFIED packaged WorkingOverlay, fed only "
            "grounded gender) + coref-dependent 2-hop composition beating frequency (2 genuine wins P3d/P5d). "
            "Coref is EASY (5/7 gender-exclusion-to-singleton; only 2 competitive recency cases, 1 fails "
            "she->pet). On the honest frequency floor the overlay beats single-hop CO by only +1/7. Lives INSIDE "
            "the 0.44 hand-rule extraction wall proven by read_grow_reread HF. Counts toward CERT as a scoped "
            "first-positive / proven-bound composition. Local-only; needs orchestrator store sync."),
        "framing_correction_vs_director": (
            "Director flagged this as the potential FIRST reader-arc positive, load-bearing, with the author's "
            "own caveats (floor-on-CO, she->pet, small N) and asked to separate CONSTRUCTION-FORCED from "
            "GENUINELY-DISCOVERED and NOT trust the HARD_PASS. RESULT (symmetric): I DEMOTE HARD_PASS->MM. It IS "
            "the first reader-arc positive, but scoped to a CONSTRUCTION-PROOF-of-composition -- the "
            "relation-EXTRACTION (NC=1.000 both arms) is hand-built-to-corpus and tautological, and coref_lift is "
            "measured against a forced-zero baseline. The DISCOVERED part is narrow but real: the packaged "
            "overlay's 6/7 coref accuracy + coref-dependent composition (2 genuine wins over frequency). The "
            "honest surviving claim vs frequency is the COMPOSITION slice (0.800 vs 0.400), NOT the CO slice "
            "where the overlay beats frequency by a single question -- the author's floor-on-CO honesty flag is "
            "CONFIRMED and is the correct read. The she->pet failure is a FAIR faithful recency limitation (not "
            "gerrymandered); the other pronouns resolve for real (mostly by gender exclusion). BRAIN-CHECK: this "
            "is NOT a Frontier-2 substrate-native win -- relations are hand-rule Python tuples, not native HD "
            "role-filler bind; the coref (recency+agreement) is loosely brain-aligned for short-distance only. "
            "Do NOT let the HARD_PASS steer the thrust as if reading-grows-relations is demonstrated as a "
            "capability -- it is demonstrated as COMPOSITION on hand-matched grade-1 text, strictly inside the "
            "proven 0.44 hand-rule extraction wall. Author credited for honest caveat-flagging."),
        "cross_arc_overlap_check": XARC,
        "net_cert_delta": ("+1 MM (scoped first reader-arc positive: packaged overlay + grounding + glass-box "
                           "extraction COMPOSE into working multi-hop grade-1 comprehension; genuine kernel = "
                           "overlay coref 6/7 + coref-dependent composition; bounded by construction-forced "
                           "extraction, easy coref, small N, and the 0.44 hand-rule wall. Held-out/learned "
                           "extraction is the CG revival gate)."),
        "supersedes": None,
        "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
        "ts_iso": _iso, "ts": _ts, "atom_id": atom["id"],
    }


def write_atomic_append(path, new_lines):
    if not path.exists():
        return (0, 0, False, "path does not exist: %s" % path)
    with open(path, "rb") as f:
        cur_bytes = f.read()
    cur_text = cur_bytes.decode("utf-8")
    pre_count = cur_text.count("\n")
    if cur_bytes and not cur_bytes.endswith(b"\n"):
        cur_bytes = cur_bytes + b"\n"
    parts = [cur_bytes]
    for line in new_lines:
        s = json.dumps(line, ensure_ascii=True)
        if "\n" in s:
            return (pre_count, pre_count, False, "JSON contains newline; not jsonl-safe")
        parts.append((s + "\n").encode("utf-8"))
    new_bytes = b"".join(parts)
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "wb") as f:
        f.write(new_bytes); f.flush(); os.fsync(f.fileno())
    os.replace(tmp_path, path)
    with open(path, "rb") as f:
        verify_text = f.read().decode("utf-8")
    post_count = verify_text.count("\n")
    expected_post = pre_count + len(new_lines)
    if post_count != expected_post:
        return (pre_count, post_count, False, "line count mismatch: expected %d got %d" % (expected_post, post_count))
    tail = verify_text.rstrip("\n").split("\n")[-len(new_lines):]
    for i, tl in enumerate(tail):
        try:
            parsed = json.loads(tl)
        except Exception as e:
            return (pre_count, post_count, False, "tail-line %d JSON round-trip fail: %s" % (i, e))
        for key in ("id", "atom_id"):
            if key in new_lines[i] and parsed.get(key) != new_lines[i][key]:
                return (pre_count, post_count, False, "tail-line %d %s mismatch" % (i, key))
    return (pre_count, post_count, True, "OK")


def main():
    atom = build_atom()
    ledger = ledger_row(atom)
    print("=== A5 atom-write: base_reader_grounded_relations_coref_v1 -> MM (first reader-arc positive, scoped) (2026-07-18) ===")
    print("ts_iso =", _iso)
    assert atom["id"].isascii(), "non-ascii atom id"
    assert ledger["atom_id"] == atom["id"], "atom_id/id mismatch"

    existing = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                existing.add(json.loads(line).get("id"))
            except Exception:
                pass
    if atom["id"] in existing:
        print("ABORT: id already in store:", atom["id"]); sys.exit(1)
    print("id-uniqueness OK (1 new, not pre-existing)")

    print("Writing 1 atom to math/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(MATH_ATOMS, [atom])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: math atoms write failed"); sys.exit(1)

    print("Writing 1 row to meta/cert_ledger.jsonl ...")
    pre, post, ok, err = write_atomic_append(CERT_LEDGER, [ledger])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: cert_ledger write failed"); sys.exit(1)

    n_ok = 0
    present = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            json.loads(line); n_ok += 1
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                present.add(json.loads(line).get("id"))
            except Exception:
                pass
    assert atom["id"] in present, "post-write integrity: new id missing"
    print("integrity: math/atoms.jsonl fully parses (%d lines), new id present." % n_ok)
    print()
    print("=== A5 WRITE COMPLETE (LOCAL ONLY; needs_orchestrator_store_sync=True; no origin push; no remote persist) ===")
    print("ATOM (MM):", atom["id"][:100], "...")


if __name__ == "__main__":
    main()
