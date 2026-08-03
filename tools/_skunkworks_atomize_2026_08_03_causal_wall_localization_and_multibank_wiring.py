"""
A5-gated atomization: causal-comprehension WALL localization (2 findings) +
multi-bank pipeline-wiring closure. AUDIT-ONLY (hdi_skunkworks). Independent
.venv recompute off the raw metrics.json files listed per-atom below (NOT off
verdict_msg/summary alone), plus independent pytest rerun of verification/ and
verification/verify_situation_model_multibank_dropin.py, plus a direct read of
data/capability_registry.jsonl's pipeline_status field for the wiring claim.

Writes THREE atoms (seq 29633-29635; 2 math, 1 meta) + 3 matching
cert_ledger.jsonl entries, atomically (tmp -> os.replace) per file, then
verify-loads all files and runs an integrity check. LOCAL-ONLY: no origin
push, no remote persist.
"""
import json
import os
import time
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATH_ATOMS_PATH = os.path.join(REPO, "data", "substrate_index", "math", "atoms.jsonl")
META_ATOMS_PATH = os.path.join(REPO, "data", "substrate_index", "meta", "atoms.jsonl")
LEDGER_PATH = os.path.join(REPO, "data", "substrate_index", "meta", "cert_ledger.jsonl")

SEQ_ENDTOEND_WALL = 29633
SEQ_LINK_PROPOSAL_PROBE = 29634
SEQ_MULTIBANK_WIRING_META = 29635

ATOM_ENDTOEND_WALL = {
    "atom_id": (
        "math::causal_endtoend_integration_gap_v1_wall_localized_to_link_detection_not_"
        "extraction_4way_ablation_gold_gold_0p9167_reader_gold_0p9167_delta0_gold_detected_"
        "0p5556_reader_detected_0p5556_delta0p3611_larger_delta_localizes_bottleneck_"
        "survival_fraction_0p606_optimistic_upper_bound_links_still_oracle_paired_when_cue_"
        "fires_event_extraction_agent_id_62p5pct_real_but_nonpropagating_weakness_would_bite_"
        "downstream_readoff_layer_smalln25_gold_UNVERIFIED_e6852ff7e_MEASURED_MECHANISM_LOCAL_ONLY"
    ),
    "seq": SEQ_ENDTOEND_WALL,
    "op": "insert",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "MEASURED_MECHANISM",
    "grade": "MM",
    "verdict": (
        "HONEST END-TO-END DECOMPOSITION (localization measurement, not a new capability claim). "
        "Independent recompute off the cell's own ablation block (not the verdict_msg string) confirms "
        "all 4 arms and the localization argument exactly: arm a (gold events + gold links) = 0.9167 "
        "organ-integration accuracy, reproducing the fuller_v2 organ's own HARD_PASS ceiling (atom "
        "29631). Arm b (reader-extracted events + gold links) = 0.9167 -- IDENTICAL to arm a "
        "(delta=0.0000): event-extraction damage from imperfect agent-ID (62.5% accuracy) does NOT "
        "propagate to the content-blind causal-comprehension organ at all on this sample, because the "
        "organ's causal-link binding does not depend on getting the extracted agent identity right. Arm "
        "c (gold events + DETECTED links) = 0.5556 (delta from arm a = 0.3611, ~6.5x arm b's delta) -- "
        "swapping gold causal links for the link-detectability heuristic (connective-cue OR shared-"
        "keyword-cue, fires on 17/25=68% of items) collapses integration accuracy by more than a third. "
        "Arm d (reader events + detected links, the genuine end-to-end condition) = 0.5556, identical to "
        "arm c, confirming again that the event-extraction weakness does not add further damage on top "
        "of the link-detection wall. LOCALIZATION: the larger delta (a-to-c, 0.3611) vs the near-zero "
        "delta (a-to-b, 0.0000) cleanly localizes the bottleneck to CAUSAL-LINK DETECTION, not event-"
        "extraction or coreference. End-to-end survival fraction vs the gold-isolated ceiling = "
        "0.90606... = 0.5556/0.9167, MEASURED exactly as 0.6060606060606061 in the metrics.json field "
        "survival_fraction_vs_gold_isolated_ceiling. This survival number is explicitly an OPTIMISTIC "
        "upper bound: the detected-link condition still ORACLE-PAIRS the link to the correct cause/effect "
        "event whenever a detection cue fires (the cell measures whether a cue exists at all, not whether "
        "a downstream heuristic correctly attaches it to the right event pair) -- a real link-PROPOSAL "
        "mechanism (see composed atom 29634) would face additional false-positive/mis-pairing risk not "
        "captured here."
    ),
    "anchor": "causal_endtoend_integration_gap_v1",
    "anchor_name": "causal_endtoend_integration_gap_v1_2026_08_03",
    "cell": (
        "experiments/exp_causal_endtoend_integration_gap_v1.py; "
        "data/exp_causal_endtoend_integration_gap_v1/metrics.json; commit e6852ff7e"
    ),
    "headline": (
        "4-way causal-comprehension ablation on Anne of Green Gables (n=25, gold_verified=False): "
        "gold+gold=0.9167, reader-events+gold-links=0.9167 (event-extraction damage does NOT reach the "
        "organ, delta=0.0000), gold-events+detected-links=0.5556, reader+detected=0.5556 (delta from "
        "ceiling=0.3611, ~6.5x the event-extraction delta) -- the WALL is causal-LINK DETECTION, not "
        "event-extraction or coreference. End-to-end survival = 60.6% of the gold-isolated ceiling, an "
        "OPTIMISTIC upper bound (links still oracle-paired to the right event when a cue fires). Event-"
        "extraction agent-ID accuracy = 62.5% (25/40 scoreable events) is a real weakness that happens "
        "not to propagate here, but would bite a downstream read-off layer that consumes the extracted "
        "agent identity directly (e.g. answer generation, not just link-organ integration)."
    ),
    "key_metrics": {
        "arm_a_gold_gold_integration": 0.9166666666666666,
        "arm_b_reader_gold_integration": 0.9166666666666666,
        "arm_c_gold_detected_integration": 0.5555555555555556,
        "arm_d_reader_detected_integration": 0.5555555555555556,
        "delta_a_to_b_event_extraction_damage": 0.0,
        "delta_a_to_c_link_detection_damage": 0.3611111111111111,
        "survival_fraction_vs_gold_isolated_ceiling": 0.6060606060606061,
        "stage1_event_extraction_coverage_recall": 1.0,
        "stage1_agent_extraction_accuracy": 0.625,
        "stage1_n_events_scored_for_agent": 40,
        "stage2_link_detectable_fraction": 0.68,
        "stage2_n_with_any_detectable_cue": 17,
        "stage2_n_with_connective_cue": 3,
        "stage2_n_with_shared_keyword_cue": 14,
        "n_items_total": 25,
        "n_real_gold_events": 45,
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Independent .venv-equivalent read of data/exp_causal_endtoend_integration_gap_v1/metrics.json's "
        "raw 'ablation' block (per-arm organ_accuracy_integration fields), NOT the verdict_msg summary "
        "string: a_gold_events_gold_links.organ_accuracy_integration=0.9166666666666666, "
        "b_reader_events_gold_links.organ_accuracy_integration=0.9166666666666666 (byte-identical to a), "
        "c_gold_events_detected_links.organ_accuracy_integration=0.5555555555555556, "
        "d_reader_events_detected_links.organ_accuracy_integration=0.5555555555555556 (byte-identical to "
        "c) -- all four reproduce the claimed 0.9167/0.9167/0.5556/0.5556 exactly. Recomputed delta(a,b)="
        "0.0 and delta(a,c)=0.3611111111111111 directly from these fields (not from a pre-summarized "
        "delta field) -- confirms the 'larger delta localizes the bottleneck' argument. Recomputed "
        "survival_fraction = 0.5555555555555556/0.9166666666666666 = 0.6060606060606061, matching the "
        "metrics.json's own survival_fraction_vs_gold_isolated_ceiling field exactly (independent division, "
        "not trusting the pre-computed field alone). stage1_event_extraction.agent_extraction_accuracy="
        "0.625 and stage2_link_detectability.fraction_with_any_detectable_cue=0.68 (17/25) both reproduce "
        "exactly off their respective raw blocks. Cross-checked gold_path's gold_anne_comprehension_v2.jsonl "
        "directly: n=25 rows, gold_verified=False on ALL 25 rows (parsed independently, not taken from the "
        "task's claim) -- confirms the small-N/gold-unverified honest-scope framing is accurate."
    ),
    "composes_seq": [29631],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_ENDTOEND_WALL - 1,
    "honest_scope": (
        "Small-N localization study: n=25 items, gold_verified=False on all 25 rows of the underlying "
        "gold_anne_comprehension_v2.jsonl (independently confirmed this pass, not inherited from the "
        "task's claim). The survival_fraction (0.606) is an OPTIMISTIC upper bound on true end-to-end "
        "performance: arms c/d measure whether ANY detectable cue exists for a link, not whether a "
        "downstream mechanism correctly proposes AND pairs that link to the right cause/effect events -- "
        "a genuine link-PROPOSAL mechanism (composed atom 29634) faces false-positive risk (measured "
        "FP=0.31 there) not modeled in this cell's binary detectability gate. The event-extraction agent-"
        "ID weakness (62.5%) not propagating to arm b is a genuine finding for THIS organ's integration "
        "metric specifically (which only needs the causal-link binding, not the extracted agent identity, "
        "to answer integration questions) -- it should NOT be read as 'event extraction quality does not "
        "matter downstream', since any future layer that reads the extracted agent field directly (e.g. "
        "answer-generation surface text) would be exposed to that 37.5% error rate."
    ),
    "framing_correction": (
        "Task input's framing is accurate and reproduces exactly; this atom adds one caveat not stated "
        "in the task input: the 0.606 survival fraction should be read as an OPTIMISTIC upper bound, not "
        "a realistic end-to-end estimate, because arms c/d's detected-links condition still oracle-pairs "
        "each detected cue to the correct event pair rather than modeling a real link-proposal mechanism's "
        "false-positive/mis-pairing risk (that risk is separately MEASURED in the composed link-proposal-"
        "signal-probe atom 29634 at FP=0.31 for the coherence-gain signal)."
    ),
    "revival_criteria": (
        "Re-run this 4-way ablation with a genuine (non-oracle-paired) link-PROPOSAL mechanism substituted "
        "for the binary detectability gate in arms c/d, once such a mechanism exists, to get a realistic "
        "(not optimistic-upper-bound) end-to-end survival number. Also: gold-verify the 25-item eval set "
        "(currently gold_verified=False) before promoting past MEASURED_MECHANISM."
    ),
    "primitive_assessment": (
        "No new primitive. Reusable methodology: a 4-way (gold x gold, reader x gold, gold x detected, "
        "reader x detected) ablation cleanly localizes a multi-stage pipeline's accuracy bottleneck to "
        "one stage by comparing which single-arm swap produces the larger accuracy delta from the "
        "gold-isolated ceiling -- reusable for any future stage-localization question in the comprehension "
        "pipeline (e.g. coreference vs situation-model accumulation)."
    ),
    "hf_attribution": "n/a (MEASURED_MECHANISM, not an HF cell).",
    "fairness_verdict": (
        "FAIR: recompute is off the raw per-arm ablation block, not the verdict_msg summary string, and "
        "every cited number reproduces exactly including independent re-derivation of the survival "
        "fraction and both deltas (not trusting pre-computed summary fields alone). Symmetric anti-"
        "negativity applied: this atom adds an explicit caveat (optimistic-upper-bound framing) that "
        "narrows the claim beyond what the task input stated, rather than accepting the more flattering "
        "reading uncaveated."
    ),
    "cross_arc_overlap": (
        "substrate_query.sh check ('causal link detection end-to-end integration comprehension') returns "
        "top hits at cosine<=0.4053, all generic WordNet/concept-node lexical matches ('detection', "
        "'integration', 'comprehension'), not prior experiment-cell duplicates -- below dup-check "
        "concern. Composes directly with 29631 (causal-link organ, gold-isolated 0.9167 ceiling this "
        "cell's arm a independently reproduces) -- this atom is the first stage-localization decomposition "
        "of that organ's end-to-end pipeline dependencies."
    ),
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}

ATOM_LINK_PROPOSAL_PROBE = {
    "atom_id": (
        "math::causal_link_proposal_signal_probe_v1_aim_probe_coherence_gain_recall0p556_"
        "fp0p31_overfires_nondiscriminating_conceptnet_commonsense_recall0p056_1of18_"
        "degenerate_selfloop_work_work_effectively_0of18_17of18_links_story_specific_1of18_"
        "generic_commonsense_matchable_9of18_goal_mediated_qualitative_verdict_deep_"
        "inference_required_next_lever_named_goal_intention_tracking_trabasso_goal_plan_"
        "chains_smalln25_not_dispatched_912077b81_MEASURED_MECHANISM_LOCAL_ONLY"
    ),
    "seq": SEQ_LINK_PROPOSAL_PROBE,
    "op": "insert",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "MEASURED_MECHANISM",
    "grade": "MM",
    "verdict": (
        "PROBE-TO-AIM (not the accumulate organ): a cheap-signal probe for what could PROPOSE causal "
        "links (rather than the end-to-end wall cell's binary detectability heuristic) before investing in "
        "a full link-proposal mechanism. Independent recompute off the raw signal1/signal2/signal3 blocks "
        "confirms all three signal results exactly. SIGNAL1 (coherence-overlap gain between candidate "
        "event pairs): recall_integration=0.5555555555555556 (10/18 gold integration links flagged), "
        "false_positive_rate=0.31 (62/200 sampled negative pairs also flagged) -- a recall around the "
        "wall cell's own detectability rate but with a materially non-trivial FP rate, meaning this signal "
        "OVER-FIRES and does not cleanly discriminate true causal pairs from spurious ones (attackable="
        "False per the cell's own gate). SIGNAL2 (ConceptNet Causes/CausesDesire commonsense-edge match): "
        "recall_integration=0.05555555555555555 (1/18) -- and independent inspection of the single flagged "
        "item (anne_causal_013) shows matched_pair=['work','work'], a DEGENERATE SELF-LOOP match (the same "
        "surface word matching itself, not a genuine commonsense causal edge between two distinct "
        "concepts) -- so the real, non-degenerate recall is effectively 0/18. generic_commonsense_"
        "matchable_n=1 vs story_specific_n=17 confirms 17 of 18 integration-gold causal links require "
        "story-specific (not generic-commonsense-lookup-able) inference. SIGNAL3 (qualitative goal/"
        "intention keyword scan of the human-written gold_answer text, no computed discriminator/FP rate "
        "-- no goal-tracking module exists yet): 9/18 (50%) of integration gold answers contain explicit "
        "goal/intention language (forgive, decide, promise, resolve, want-to, etc.), naming goal/"
        "intention tracking (Trabasso goal-plan causal chains) as a concrete, evidence-grounded next lever "
        "rather than a speculative one. Overall verdict DEEP_INFERENCE_REQUIRED: neither cheap signal "
        "(coherence-overlap, commonsense-KB lookup) is a viable stand-in for a real link-proposal "
        "mechanism at this sample size and difficulty; the causal links in Anne of Green Gables are "
        "predominantly story-specific and goal-mediated, requiring inference over the accumulated "
        "situation model rather than surface/commonsense pattern-matching."
    ),
    "anchor": "causal_link_proposal_signal_probe_v1",
    "anchor_name": "causal_link_proposal_signal_probe_v1_2026_08_03",
    "cell": (
        "experiments/exp_causal_link_proposal_signal_probe_v1.py; "
        "data/exp_causal_link_proposal_signal_probe_v1/metrics.json; commit 912077b81"
    ),
    "headline": (
        "Cheap-signal probe for causal-link proposal on Anne (n=25, 18 integration-type items, "
        "gold_verified=False): coherence-overlap gain signal recall=0.556, FP=0.31 (over-fires, non-"
        "discriminating). ConceptNet commonsense-edge signal recall=0.056 (1/18), and that single hit is a "
        "degenerate self-loop ('work'->'work'), so real commonsense-lookup recall is effectively 0/18 -- "
        "17/18 causal links are story-specific, not generic-commonsense-matchable. 9/18 (50%) of gold "
        "integration answers are goal/intention-mediated (qualitative keyword scan, no FP measured since "
        "no goal-tracking module exists yet). VERDICT: DEEP_INFERENCE_REQUIRED -> names GOAL/INTENTION "
        "TRACKING (Trabasso goal-plan causal chains) as the concrete next lever, not a speculative "
        "direction. Measurement-only per task instruction: cell was NOT dispatched/queued/shipped remote "
        "(dispatched=false, dispatch_note confirms measurement-only)."
    ),
    "key_metrics": {
        "signal1_coherence_recall_integration": 0.5555555555555556,
        "signal1_coherence_n_flagged_integration": 10,
        "signal1_coherence_n_integration": 18,
        "signal1_coherence_false_positive_rate": 0.31,
        "signal1_attackable": False,
        "signal2_conceptnet_recall_integration": 0.05555555555555555,
        "signal2_conceptnet_n_flagged_integration": 1,
        "signal2_conceptnet_false_positive_rate": 0.03,
        "signal2_generic_commonsense_matchable_n": 1,
        "signal2_generic_match_is_degenerate_selfloop": True,
        "signal2_attackable": False,
        "signal2_story_specific_n": 17,
        "signal3_n_goal_mediated_integration": 9,
        "signal3_n_integration_total": 18,
        "signal3_fraction_goal_mediated": 0.5,
        "n_conceptnet_causal_edges_loaded": 21484,
        "n_negative_pairs_sampled": 200,
        "n_items_total": 25,
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Independent read of data/exp_causal_link_proposal_signal_probe_v1/metrics.json's raw signal1/"
        "signal2/signal3 blocks, not the verdict_msg summary: signal1_coherence_overlap.recall_"
        "integration={n:18, n_flagged:10, recall:0.5555555555555556}, false_positive_rate=0.31, "
        "attackable=False -- reproduces exactly. signal2_conceptnet_commonsense.recall_integration="
        "{n:18, n_flagged:1, recall:0.05555555555555555}, generic_commonsense_matchable_n=1, "
        "story_specific_n=17 -- reproduces exactly. Independently inspected the per_item array for the "
        "single flagged signal2 hit (id=anne_causal_013): matched_pair=['work','work'] -- confirmed the "
        "'degenerate self-loop' characterization directly from the raw data (this is an audit-added "
        "finding, catching that the ONE commonsense hit is not a genuine distinct-concept match) rather "
        "than accepting the '1/18 recall' number at face value without checking WHAT matched. "
        "signal3_goal_intention_qualitative.n_goal_mediated_integration=9, n_integration_total=18 -- "
        "reproduces exactly; independently spot-checked 3 of the 9 flagged per_item entries (anne_"
        "causal_004 'forgive/forgives', anne_causal_006 'withdrew/promised/promise', anne_causal_025 "
        "'decide/decided/determined') against their goal_markers_found arrays -- all genuine keyword "
        "matches, not obviously spurious. dispatched=false and dispatch_note='measurement-only per task "
        "instruction; not queued, not shipped remote' confirmed present in metrics.json, matching the "
        "task's constraint that this probe was not to be dispatched."
    ),
    "composes_seq": [SEQ_ENDTOEND_WALL],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_LINK_PROPOSAL_PROBE - 1,
    "honest_scope": (
        "Small-N aim-probe (18 integration-type items scored for signal1/signal2; n_negative_pairs=200 "
        "synthetic negatives for FP rate, not real story-derived negatives). gold_verified=False on the "
        "underlying gold set (same corpus as the composed end-to-end wall atom 29633). Signal3 is "
        "explicitly qualitative (a keyword scan of human-written gold-answer TEXT, not a computed "
        "discriminator over model output) with NO false-positive rate measured -- the 9/18 goal-mediated "
        "fraction should be read as evidence that goal/intention language is PRESENT in gold explanations, "
        "not as a validated discriminator recall number; a real goal-tracking module's recall/FP would "
        "need separate measurement once built. This is a probe explicitly meant to AIM further investment, "
        "not a chain-grade capability result -- correctly tiered MEASURED_MECHANISM, not higher."
    ),
    "framing_correction": (
        "None vs the task input's framing, which already stated the ConceptNet result as 'degenerate "
        "self-loop -> effectively 0/18' -- this atom independently confirms that characterization by "
        "inspecting the actual matched_pair field rather than accepting the recall number alone, and adds "
        "the same rigor for signal3 (confirmed qualitative/no-FP-measured framing is preserved, not "
        "silently upgraded to a discriminator claim)."
    ),
    "revival_criteria": (
        "Build a goal/intention-tracking mechanism (Trabasso goal-plan causal chains, per the named next "
        "lever) that operates over the situation model's accumulated entity/event state rather than "
        "keyword-scanning gold-answer text, then re-run this probe's signal-3 slot as a real discriminator "
        "with a measured FP rate on the same 200-negative-pair harness used for signals 1-2, to get an "
        "apples-to-apples comparison against the coherence-overlap and ConceptNet signals."
    ),
    "primitive_assessment": (
        "No new primitive; this is a diagnostic probe cell. Reusable methodology: before building a full "
        "link-proposal mechanism, cheaply test candidate SIGNALS (coherence-overlap, commonsense-KB "
        "lookup, keyword-scan-for-a-not-yet-built-module) against the same gold set + shared negative-pair "
        "harness to see which signal class is worth investing further mechanism-building effort in -- here "
        "it correctly ruled out both cheap signals (over-fires / degenerate) and named the deep-inference "
        "direction instead of defaulting to build-the-cheap-thing-anyway."
    ),
    "hf_attribution": (
        "n/a (MEASURED_MECHANISM aim-probe, not an HF cell) -- though note both tested cheap signals "
        "(coherence-overlap, ConceptNet) are honest NEGATIVES for viability as a stand-alone link-proposal "
        "mechanism at this sample/difficulty: recorded here as the mechanism-class finding, not separately "
        "HF-tiered since no build-now decision was riding on either signal alone."
    ),
    "fairness_verdict": (
        "FAIR: recall/FP numbers reproduce exactly off the raw per-signal blocks, and the audit went "
        "further than the task's own framing by inspecting the single ConceptNet hit's actual matched "
        "concepts (confirming, not just accepting, the degenerate-self-loop characterization) and by "
        "explicitly flagging signal3's qualitative/no-FP-measured status so it is not later mistaken for a "
        "validated discriminator."
    ),
    "cross_arc_overlap": (
        "substrate_query.sh check ('conceptnet commonsense causal link goal intention tracking') returns "
        "top hits at cosine<=0.3613, generic lexical/concept-node matches ('commonsense', 'CN_commonsense', "
        "a D2-ConceptNet-ingest planning note) -- no prior experiment-cell duplicate of this specific "
        "signal-probe result. Composes with 29633 (the end-to-end wall cell this probe follows up on, "
        "aiming at the same link-detection bottleneck with candidate mechanisms instead of a binary "
        "detectability gate)."
    ),
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}

ATOM_MULTIBANK_WIRING_META = {
    "atom_id": (
        "meta::multibank_accumulateregister_wired_and_pipeline_used_closes_wire_dont_island_"
        "gap_flagged_by_user_29fb97354_make_situation_register_factory_backend_multibank_"
        "default_n_banks8_flat_optout_byteidentical_2of5_active_pipeline_entrypoints_self_"
        "improving_loop_read_anne_glassbox_v2_now_construct_via_factory_dropin_verified_"
        "decode_identical_at_pilot_scale_highload_multibank8_0p9992_vs_flat_0p6547_at_n256_"
        "208_verification_tests_green_3skip_a81f5e2f9_gate_fix_bfs_import_closure_pipeline_"
        "reachable_check_registry_pipeline_status_flipped_wired_but_not_pipeline_reachable_"
        "to_wired_and_pipeline_used_CERT_NEUTRAL_INTEGRATION_LOCAL_ONLY"
    ),
    "seq": SEQ_MULTIBANK_WIRING_META,
    "op": "insert",
    "corpus": "meta",
    "tier": "CERT_NEUTRAL_INTEGRATION",
    "cert_status": "n/a (CERT-neutral integration/wiring atom)",
    "grade": "META",
    "verdict": (
        "WIRE-DON'T-ISLAND CLOSURE, independently verified: MultiBankAccumulateRegister (the capacity-"
        "headroom fix MEASURED at atom 29632, flat degrades 0.9781->0.6547 at n_events=256 while "
        "multibank(n_banks=8) holds 0.9992) has moved from WIRED_BUT_NOT_PIPELINE_REACHABLE to actually "
        "reachable-and-used by the active reader pipeline. This directly resolves the specific wire-don't-"
        "island instance the USER flagged (capability-integration gate, 2026-07-25/07-28 discipline). "
        "Two commits, independently verified: (1) 29fb97354 adds make_situation_register() factory in "
        "hdlab/situation_model_accumulate.py (backend='multibank' default n_banks=8, backend='flat' "
        "opt-out byte-identical to the prior AccumulateRegister construction) and switches 2 of the 5 "
        "declared active-pipeline entry points (hdlab/self_improving_loop.py, tools/read_anne_glassbox_v2_"
        "honest_ledger.py) to construct their situation register via the factory instead of AccumulateRegister "
        "directly. verification/verify_situation_model_multibank_dropin.py (scaffold-free witness) "
        "independently re-run this pass: PASS -- multibank is drop-in decode-identical to flat at pilot "
        "scale, and retains decode self-consistency at high per-entity event load where flat degrades. "
        "(2) a81f5e2f9 fixes the audit tool's own gate hole: the prior WIRED check only asked 'does any "
        "consumer import this' (satisfiable by a throwaway verify_*_v1 smoke script), not 'is this "
        "reachable from what the active reader actually runs' -- adds a BFS import-closure seeded from the "
        "5 declared active-pipeline entry points plus a disk-scan-vs-registry unregistered-module check. "
        "Independently confirmed via direct read of data/capability_registry.jsonl: the "
        "working_memory_multibank_K_capacity row's pipeline_status field now reads "
        "WIRED_AND_PIPELINE_USED (was WIRED_BUT_NOT_PIPELINE_REACHABLE per that same row's own gate_"
        "decision_target note describing the prior gap). Full verification suite independently rerun this "
        "pass: 208 passed, 3 skipped (no failures), matching the task's '208 tests green' claim exactly."
    ),
    "anchor": "multibank_pipeline_wiring_closure",
    "anchor_name": "multibank_accumulateregister_pipeline_wiring_closure_2026_08_03",
    "cell": (
        "hdlab/situation_model_accumulate.py (make_situation_register factory); "
        "hdlab/situation_model_multibank.py (MultiBankAccumulateRegister.register() API-parity add); "
        "hdlab/self_improving_loop.py, tools/read_anne_glassbox_v2_honest_ledger.py (2 of 5 entry-point "
        "call-sites switched); verification/verify_situation_model_multibank_dropin.py; "
        "tools/capability_registry_audit.py (BFS pipeline-reachability closure + unregistered-module "
        "scan); data/capability_registry.jsonl (working_memory_multibank_K_capacity row); "
        "commits 29fb97354, a81f5e2f9"
    ),
    "headline": (
        "MultiBankAccumulateRegister flips from WIRED_BUT_NOT_PIPELINE_REACHABLE to "
        "WIRED_AND_PIPELINE_USED (2 of 5 active-pipeline entry points now construct via the new "
        "make_situation_register() factory, backend='multibank' n_banks=8 default). Drop-in decode-"
        "identity independently re-verified (PASS). High-load capacity-headroom result this wiring is "
        "MOTIVATED by (composed atom 29632): multibank(n_banks=8) holds 0.9992 vs flat's 0.6547 at "
        "n_events=256 (>=0.95 vs <=0.85 can-fail thresholds both correctly firing/holding). 208/211 "
        "verification tests green (3 pre-existing skips, 0 failures), independently rerun this pass. The "
        "audit tool's own gate hole (throwaway-consumer-import satisfying WIRED without genuine pipeline "
        "reachability) is separately fixed via a BFS import-closure check seeded from the 5 declared "
        "entry points, plus a disk-scan-vs-registry check so a chain-grade module can no longer silently "
        "exist unregistered in hdlab/ (the specific failure class this whole gate exists to prevent, per "
        "notes/integration_audit_built_vs_wired_vs_used_2026-08-02.md)."
    ),
    "key_metrics": {
        "n_active_pipeline_entrypoints_declared": 5,
        "n_entrypoints_switched_to_multibank_factory": 2,
        "multibank_dropin_verification_result": "PASS",
        "flat_decode_self_consistency_at_n_events_256": 0.6547,
        "multibank_n_banks8_decode_self_consistency_at_n_events_256": 0.9992,
        "canfail_threshold_flat_below": 0.85,
        "canfail_threshold_multibank_above": 0.95,
        "verification_suite_passed": 208,
        "verification_suite_skipped": 3,
        "verification_suite_failed": 0,
        "pipeline_status_before": "WIRED_BUT_NOT_PIPELINE_REACHABLE",
        "pipeline_status_after": "WIRED_AND_PIPELINE_USED",
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Independent commands run this pass (not trusting commit-message claims): (1) `git show --stat` "
        "on both 29fb97354 and a81f5e2f9 to independently read the actual file-level diffs and commit "
        "bodies. (2) `.venv/Scripts/python.exe verification/verify_situation_model_multibank_dropin.py` "
        "rerun directly -> stdout '[verify_situation_model_multibank_dropin] PASS: multibank backend is "
        "drop-in identical to flat at small (pilot) scale, and retains decode self-consistency at high "
        "per-entity event load where flat degrades.' (3) `.venv/Scripts/python.exe -m pytest verification/ "
        "-q` rerun directly -> '208 passed, 3 skipped in 135.05s', matching the task's '208 tests green' "
        "claim exactly (0 failures). (4) Direct Python read of data/capability_registry.jsonl, filtering "
        "for the working_memory_multibank_K_capacity row: pipeline_status field == "
        "'WIRED_AND_PIPELINE_USED', last_audit_utc=2026-08-03T04:37:38Z -- confirms the flip is reflected "
        "in the registry itself (not just the commit message), and the row's own gate_decision_target "
        "text independently confirms the PRIOR state was WIRED_BUT_NOT_PIPELINE_REACHABLE."
    ),
    "composes_seq": [29632],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_MULTIBANK_WIRING_META - 1,
    "honest_scope": (
        "This is an INTEGRATION/wiring event, not a new capability measurement -- the underlying capacity "
        "result (flat 0.9781->0.6547 vs multibank 0.9992 at n_events=256) was already MEASURED and "
        "atomized at 29632 (tiered MEASURED_MECHANISM, d=512 below the working_memory chain-grade "
        "envelope of d>=8192; that tiering is unchanged by this wiring event). Only 2 of the 5 declared "
        "active-pipeline entry points were switched this commit (hdlab/self_improving_loop.py, tools/"
        "read_anne_glassbox_v2_honest_ledger.py) -- the other 3 (hdlab/coreference_resolver.py, "
        "hdlab/situation_model_accumulate.py's own direct callers if any outside these two, hdlab/"
        "state_of_mind.py) were not independently checked this pass for whether they also construct a "
        "situation register that should route through the new factory; not claiming full pipeline "
        "coverage, only that the registry's BFS reachability check (which seeds from all 5 entry points, "
        "not just the 2 switched) now independently confirms reachability is closed. At current pilot "
        "scale (bundle-load ~2, per the commit's own honest-scope note) multibank and flat decode "
        "identically -- this wiring is capacity-headroom future-proofing, not a comprehension-accuracy "
        "lift at current scale, and this atom does not claim otherwise."
    ),
    "framing_correction": (
        "Task input's framing ('high-load holds >=0.95 vs flat <=0.85') is accurate and independently "
        "reproduces (0.9992 vs 0.6547, correctly on the >=0.95/<=0.85 sides of both can-fail thresholds); "
        "this atom adds one scope caveat not stated in the task input: only 2 of 5 declared entry points "
        "were switched this commit, not all 5 -- the registry's pipeline-reachable claim rests on BFS "
        "import-closure reachability from those 2 switched call-sites (plus situation_model_multibank.py's "
        "own import of situation_model_accumulate.py), not on every entry point independently constructing "
        "via the new factory."
    ),
    "revival_criteria": (
        "n/a for this integration atom itself (the wiring is DONE and independently verified). Follow-up "
        "(not required for this atom, noted for completeness): confirm whether the remaining 3 declared "
        "active-pipeline entry points (hdlab/coreference_resolver.py, hdlab/state_of_mind.py, and any "
        "direct AccumulateRegister construction outside the 2 switched call-sites) also route through "
        "make_situation_register(), or whether they never construct a situation register directly and so "
        "have no call-site to switch."
    ),
    "primitive_assessment": (
        "No new primitive (the primitive itself, MultiBankAccumulateRegister, was already assessed at "
        "atom 29632). Reusable methodology/integration pattern: a factory function with a backend= kwarg "
        "and a byte-identical opt-out path is a low-risk way to switch a pipeline's default memory backend "
        "without touching every call-site's construction logic individually, while the BFS-import-closure "
        "audit check (rather than a naive 'is it imported anywhere' check) is the correct way to verify a "
        "capability is ACTUALLY reachable from the live pipeline rather than merely imported by a "
        "throwaway smoke/verify script -- this is now durable at the tooling level, not just this one "
        "instance."
    ),
    "hf_attribution": "n/a (CERT-neutral integration atom, not an HF cell).",
    "fairness_verdict": (
        "FAIR: every claim independently re-verified off disk this pass (git diff read, verification "
        "script rerun, full pytest suite rerun, registry field read directly) rather than propagated from "
        "the commit messages or task-input framing alone. The one honest-scope caveat added (2-of-5 "
        "entry points switched, not all 5) narrows the claim rather than accepting the more complete-"
        "sounding 'the pipeline is wired' framing uncaveated."
    ),
    "cross_arc_overlap": (
        "Directly composes 29632 (the multibank capacity-headroom MEASUREMENT this wiring event makes "
        "actually pipeline-used) and closes out that atom's own implicit gap (a chain-grade-adjacent "
        "primitive that existed only as a registered-but-unreachable module). This is the concrete "
        "resolution instance of the standing USER discipline [[feedback_wire_latest_modules_into_"
        "discoverable_substrate_2026-07-25]] and [[feedback_capability_integration_gate_durability_via_"
        "session_read_not_crons_2026-07-28]] -- recorded here as a CERT-neutral methodology/integration "
        "atom per the discipline-atomization convention (META rules -> meta corpus), not a math-corpus "
        "capability claim."
    ),
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}


def atomic_append_jsonl(path, record):
    line = json.dumps(record, ensure_ascii=True) + "\n"
    dir_ = os.path.dirname(path)
    with open(path, "rb") as f:
        existing = f.read()
    fd, tmp_path = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(existing)
            tmp.write(line.encode("utf-8"))
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def verify_load(path, expect_seq=None, expect_atom_id=None):
    found = False
    count = 0
    with open(path, "rb") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            count += 1
            d = json.loads(raw.decode("utf-8"))
            if expect_seq is not None and d.get("seq") == expect_seq:
                found = True
            if expect_atom_id is not None and d.get("atom_id") == expect_atom_id:
                found = True
    return found, count


def make_ledger_entry(seq, atom, corpus, decision, note):
    now = time.time()
    return {
        "seq": seq,
        "atom_id": atom["atom_id"],
        "corpus": corpus,
        "decision": decision,
        "note": note,
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
        "ts": now,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00", time.gmtime(now)),
        "ts_day": time.strftime("%Y-%m-%d", time.gmtime(now)),
    }


def main():
    now = time.time()
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00", time.gmtime(now))
    ts_day = time.strftime("%Y-%m-%d", time.gmtime(now))

    for atom in (ATOM_ENDTOEND_WALL, ATOM_LINK_PROPOSAL_PROBE, ATOM_MULTIBANK_WIRING_META):
        atom["ts"] = now
        atom["ts_iso"] = ts_iso
        atom["ts_day"] = ts_day

    ledger_endtoend = make_ledger_entry(
        SEQ_ENDTOEND_WALL, ATOM_ENDTOEND_WALL, "math",
        "MEASURED_MECHANISM CERT +0 (4-way causal-comprehension ablation, wall localization). "
        "Independent recompute off the raw ablation block reproduces exactly: a=0.9167, b=0.9167 "
        "(delta=0.0000, event-extraction damage does not propagate), c=0.5556, d=0.5556 (delta from "
        "ceiling=0.3611) -- localizes the wall to causal-link detection, not extraction. Survival "
        "fraction=0.6060606060606061 independently re-derived (0.5556/0.9167), matches exactly. "
        "gold_verified=False confirmed on all 25 rows directly off gold_anne_comprehension_v2.jsonl. "
        "Flagged the 0.606 survival number as an OPTIMISTIC upper bound (links still oracle-paired when "
        "a cue fires).",
        "AUDIT-ONLY (hdi_skunkworks) independent recompute off data/exp_causal_endtoend_integration_gap_v1/"
        "metrics.json's raw ablation block, NOT off verdict_msg alone. Commit e6852ff7e. LOCAL-ONLY.",
    )
    ledger_link_probe = make_ledger_entry(
        SEQ_LINK_PROPOSAL_PROBE, ATOM_LINK_PROPOSAL_PROBE, "math",
        "MEASURED_MECHANISM CERT +0 (link-proposal signal aim-probe). Independent recompute off raw "
        "signal1/signal2/signal3 blocks reproduces exactly: coherence recall=0.5556 FP=0.31 (over-fires); "
        "ConceptNet recall=0.05555555555555555 (1/18) -- independently inspected the flagged per_item "
        "entry (anne_causal_013, matched_pair=[work,work]) and confirmed it is a degenerate self-loop, "
        "not a genuine commonsense match, so effective recall is 0/18; 17/18 story-specific. Signal3 (9/18 "
        "goal-mediated) confirmed as qualitative/no-FP-measured, not a validated discriminator. Verdict "
        "DEEP_INFERENCE_REQUIRED reproduces; dispatched=false confirmed in metrics.json (measurement-only "
        "per task instruction, not queued/shipped remote).",
        "AUDIT-ONLY (hdi_skunkworks) independent recompute off data/exp_causal_link_proposal_signal_"
        "probe_v1/metrics.json, including direct inspection of the matched_pair field for the single "
        "ConceptNet hit. Commit 912077b81. LOCAL-ONLY.",
    )
    ledger_multibank_wiring = make_ledger_entry(
        SEQ_MULTIBANK_WIRING_META, ATOM_MULTIBANK_WIRING_META, "meta",
        "CERT-neutral integration/wiring atom. Independently verified: verify_situation_model_multibank_"
        "dropin.py rerun -> PASS; full verification suite rerun -> 208 passed, 3 skipped, 0 failed "
        "(matches '208 tests green' claim exactly); data/capability_registry.jsonl's working_memory_"
        "multibank_K_capacity row pipeline_status field read directly -> WIRED_AND_PIPELINE_USED "
        "(confirmed flipped from WIRED_BUT_NOT_PIPELINE_REACHABLE per that row's own gate_decision_target "
        "text). Honest scope note added: only 2 of 5 declared active-pipeline entry points were switched "
        "this commit, not all 5 (BFS reachability from those 2 is what closes the registry gate).",
        "AUDIT-ONLY (hdi_skunkworks) independent git-show + pytest rerun + direct registry-field read, "
        "NOT off commit messages alone. Commits 29fb97354, a81f5e2f9. LOCAL-ONLY.",
    )

    # A5-gate: atomic write, math atoms first, then meta atom, then all 3 ledger entries.
    atomic_append_jsonl(MATH_ATOMS_PATH, ATOM_ENDTOEND_WALL)
    atomic_append_jsonl(MATH_ATOMS_PATH, ATOM_LINK_PROPOSAL_PROBE)
    atomic_append_jsonl(META_ATOMS_PATH, ATOM_MULTIBANK_WIRING_META)

    atomic_append_jsonl(LEDGER_PATH, ledger_endtoend)
    atomic_append_jsonl(LEDGER_PATH, ledger_link_probe)
    atomic_append_jsonl(LEDGER_PATH, ledger_multibank_wiring)

    # Verify-load + integrity check
    results = []
    for path, seq, atom_id in (
        (MATH_ATOMS_PATH, SEQ_ENDTOEND_WALL, ATOM_ENDTOEND_WALL["atom_id"]),
        (MATH_ATOMS_PATH, SEQ_LINK_PROPOSAL_PROBE, ATOM_LINK_PROPOSAL_PROBE["atom_id"]),
        (META_ATOMS_PATH, SEQ_MULTIBANK_WIRING_META, ATOM_MULTIBANK_WIRING_META["atom_id"]),
    ):
        found, count = verify_load(path, expect_seq=seq, expect_atom_id=atom_id)
        assert found, f"FAIL: atom seq={seq} not found in {path} after write"
        results.append((path, seq, count))

    for seq in (SEQ_ENDTOEND_WALL, SEQ_LINK_PROPOSAL_PROBE, SEQ_MULTIBANK_WIRING_META):
        found, count = verify_load(LEDGER_PATH, expect_seq=seq)
        assert found, f"FAIL: ledger entry seq={seq} not found in {LEDGER_PATH} after write"

    for path, seq, count in results:
        print(f"OK: atom seq={seq} written to {path} ({count} total lines)")
    print(f"OK: 3 ledger entries written to {LEDGER_PATH}")
    print("atom_ids:")
    for atom in (ATOM_ENDTOEND_WALL, ATOM_LINK_PROPOSAL_PROBE, ATOM_MULTIBANK_WIRING_META):
        print(f"  seq={atom['seq']} corpus={atom['corpus']} -> {atom['atom_id'][:100]}...")


if __name__ == "__main__":
    main()
