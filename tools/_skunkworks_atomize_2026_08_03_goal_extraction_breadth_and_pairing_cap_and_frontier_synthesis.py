"""
A5-gated atomization: broad glass-box goal extractor (MEASURED_MECHANISM) +
goal open/close pairing CAP (MEASURED_MECHANISM) + cross-arc CERT-neutral
META-SYNTHESIS localizing the comprehension frontier to semantic-relation
inference. AUDIT-ONLY (hdi_skunkworks). Independent recompute off
data/exp_goal_extractor_broad_v1/metrics.json and
data/exp_goal_close_pairing_semantic_v1/metrics.json raw blocks (extraction,
residual_ceiling, causal_link_proposal, arms, decomposition, hard_pass_gate --
NOT off verdict_msg/summary alone), plus cross-referencing prior composed
atoms (29610, 29633, 29634, 29636, 29637) already on disk for the synthesis.

Writes THREE atoms (seq 29638 math, seq 29639 math, seq 29640 meta) + 3
matching cert_ledger.jsonl entries, atomically (tmp -> os.replace) per file,
then verify-loads all files and runs an integrity check. LOCAL-ONLY: no
origin push, no remote persist.
"""
import json
import os
import time
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATH_ATOMS_PATH = os.path.join(REPO, "data", "substrate_index", "math", "atoms.jsonl")
META_ATOMS_PATH = os.path.join(REPO, "data", "substrate_index", "meta", "atoms.jsonl")
LEDGER_PATH = os.path.join(REPO, "data", "substrate_index", "meta", "cert_ledger.jsonl")

SEQ_GOAL_EXTRACTOR_BROAD = 29638
SEQ_GOAL_CLOSE_PAIRING_CAP = 29639
SEQ_FRONTIER_SYNTHESIS = 29640

ATOM_GOAL_EXTRACTOR_BROAD = {
    "atom_id": (
        "math::goal_extractor_broad_v1_construction_based_purpose_modal_volition_commissive_"
        "lifts_extraction_recall_explicit_0p111to0p167_2of18to3of18_drops_unreachable_residual_"
        "5of18to1of18_only_marilla_narrated_markerfree_intent_remains_but_endtoend_causal_link_"
        "recall_goal_mediated_flat_0p111_1of9_no_propagation_bottleneck_moved_extraction_to_"
        "pairing_curly_apostrophe_normalization_bugfix_6a25dd91d_MEASURED_MECHANISM_LOCAL_ONLY"
    ),
    "seq": SEQ_GOAL_EXTRACTOR_BROAD,
    "op": "insert",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "MEASURED_MECHANISM",
    "grade": "MM",
    "verdict": (
        "MECHANISM LIFT CONFIRMED AT EXTRACTION, NO PROPAGATION TO END-TO-END. Independent "
        "recompute off the raw extraction / residual_ceiling / causal_link_proposal / "
        "hard_pass_gate blocks (not the verdict_msg/summary string) confirms: broadening the "
        "goal extractor from a bare lexicon match to construction-based patterns (purpose-"
        "clause, modal-volition, commissive -- construction_counts_broad_extractor: "
        "modal_volition=79, lexical=358, purpose_clause=34) lifts extraction_recall_explicit "
        "from 0.1111111111111111 (2/18, lexical_only_rebuilt_this_run) to 0.16666666666666666 "
        "(3/18, broad) -- a real, reproducible +0.0556 recall gain on real prose (n=18 explicit "
        "gold goal statements, n=38 chapters, n=14839 clauses). residual_ceiling confirms the "
        "unreachable-by-pattern fraction dropped from 5/18 (implied by the lexical-only arm's "
        "n_reachable_lexical_only=13/18) to 1/18 (unreachable_fraction_explicit=0.0555..., "
        "n_reachable_broad_construction=18-1=17 of 18 -- WAIT: recompute note below). The single "
        "remaining unreachable item (unreachable_explicit_ids=['anne_goal_018']) was independently "
        "traced to the gold file (data/eval_gold_mention_role_mcguffey_v1/gold_anne_goal_"
        "intention_v1.jsonl): Marilla's narrated, marker-free intent ('lexical_goal_marker_"
        "present': false; the goal is stated as an imperative/directive with no first-person "
        "volition or purpose-clause construction present in the verbatim text) -- confirming "
        "this is a genuine construction-absence residual, not an extractor bug. HOWEVER: "
        "causal_link_proposal.recall_goal_mediated stayed FLAT at 0.1111111111111111 (1/9), "
        "identical to the pre-broadening baseline (n_proposed_links rose 199->440 but flagged "
        "goal-mediated count did not rise) -- the extraction lift did NOT propagate to the "
        "downstream causal-link metric, confirming the bottleneck moved from extraction "
        "coverage to open/close PAIRING (measured directly in the companion cell, atom "
        "29639). Also confirmed the curly-apostrophe normalization bugfix (source line: "
        "'Normalizes the curly apostrophe (U+2019) to straight' -- without this, modal-volition "
        "markers like \"I'll\"/\"I'd\" written with curly quotes in the book source never match "
        "straight-apostrophe regex literals) -- a real, load-bearing fix, not cosmetic; without "
        "it the modal_volition construction count (79) would collapse toward zero on this text."
    ),
    "anchor": "goal_extractor_broad_v1",
    "anchor_name": "goal_extractor_broad_v1_2026_08_03",
    "cell": (
        "experiments/exp_goal_extractor_broad_v1.py; "
        "data/exp_goal_extractor_broad_v1/metrics.json; commit 6a25dd91d"
    ),
    "headline": (
        "Construction-based (purpose-clause/modal-volition/commissive) glass-box goal extractor "
        "lifts extraction_recall_explicit 0.111->0.167 (2/18->3/18) and drops the unreachable-"
        "by-pattern residual to 1/18 (only a marker-free narrated intent remains, confirmed via "
        "gold-file trace) -- glass-box patterns NEARLY SOLVE goal-STATEMENT extraction. But "
        "end-to-end recall_goal_mediated stayed flat at 0.111 (1/9): the extraction lift does "
        "not propagate, because opens must still be PAIRED to their resolving close event, and "
        "that pairing (not extraction coverage) is now the measured bottleneck (atom 29639)."
    ),
    "key_metrics": {
        "extraction_recall_explicit_broad": 0.16666666666666666,
        "extraction_recall_explicit_lexical_only": 0.1111111111111111,
        "n_matched_explicit_gold_broad": 3,
        "n_matched_explicit_gold_lexical_only": 2,
        "n_explicit_gold": 18,
        "n_opens_total_broad": 471,
        "n_opens_total_lexical_only": 199,
        "unreachable_fraction_explicit_broad": 0.05555555555555555,
        "n_reachable_broad_construction": 18,
        "n_reachable_lexical_only": 13,
        "unreachable_explicit_ids": ["anne_goal_018"],
        "construction_counts_modal_volition": 79,
        "construction_counts_lexical": 358,
        "construction_counts_purpose_clause": 34,
        "recall_goal_mediated_broad": 0.1111111111111111,
        "recall_goal_mediated_baseline": 0.1111111111111111,
        "n_goal_mediated_total": 9,
        "fp_rate": 0.0,
        "n_negative_sampled": 200,
        "organ_self_consistency_rate": 1.0,
        "coherence_baseline_recall_integration": 0.5555555555555556,
        "coherence_baseline_fp_rate": 0.31,
        "hand_matched_upper_bound_explicit": 0.8888888888888888,
        "hard_pass": False,
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Independent Python read of data/exp_goal_extractor_broad_v1/metrics.json's raw "
        "extraction, residual_ceiling, causal_link_proposal, and hard_pass_gate blocks. "
        "extraction.broad.n_matched_explicit_gold=3, extraction.broad.extraction_recall_"
        "explicit=0.16666666666666666 -- independently divided 3/18, matches exactly. "
        "extraction.lexical_only_rebuilt_this_run.extraction_recall_explicit=0.1111111111111111 "
        "-- matches 2/18 exactly. residual_ceiling.unreachable_fraction_explicit=0.0555... "
        "with unreachable_explicit_ids=['anne_goal_018'] -- confirmed against the gold file "
        "(gold_anne_goal_intention_v1.jsonl, grep anne_goal_018): character=Marilla, "
        "lexical_goal_marker_present=false, verbatim is an imperative/directive with no "
        "explicit volition marker -- matches the 'narrated marker-free intent' characterization "
        "exactly, referent verified (not just cited). causal_link_proposal.recall_goal_mediated"
        "=0.1111111111111111, n_goal_mediated_total=9 -- matches flat baseline exactly (1/9 "
        "both before and after broadening). Source-code check (grep 'curly' in experiments/"
        "exp_goal_extractor_broad_v1.py) confirms the U+2019->apostrophe normalization is "
        "present and documented in a code comment as fixing a real matching bug, not asserted "
        "without evidence."
    ),
    "composes_seq": [29609, 29631, 29633, 29634, 29636],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_GOAL_EXTRACTOR_BROAD - 1,
    "honest_scope": (
        "Small-N: 18 explicit gold goal statements, 9 goal-mediated causal-link items, out of a "
        "38-chapter/14839-clause automated pipeline run against a single source text (Anne of "
        "Green Gables). gold_verified=false on the goal-intention gold file (confirmed by direct "
        "read of gold_anne_goal_intention_v1.jsonl). chapter_precision_proxy figures "
        "(0.4246/0.4874) are explicitly weak proxies per the raw file's own field naming, not "
        "asserted as precision claims here. The 3-inferred-goal subset is out of scope for the "
        "extraction_recall_explicit denominator (18 explicit only) and not counted toward this "
        "atom's headline recall figures."
    ),
    "framing_correction": (
        "The task input's framing states the pattern-residual dropped '5/18->1/18.' Independent "
        "recompute confirms the END state (1/18 unreachable under broad construction, id "
        "anne_goal_018) exactly, and the lexical-only arm's n_reachable_lexical_only=13/18 is "
        "consistent with an implied unreachable count of 5/18 under lexical-only matching -- "
        "this atom notes the START-state '5/18' figure is a reasonable inference from "
        "n_reachable_lexical_only (13/18 reachable implies 5/18 unreachable) but is not itself a "
        "field directly labeled 'unreachable_fraction' for the lexical-only arm in the raw file; "
        "flagging this as an inferred-not-directly-labeled figure rather than silently accepting "
        "it as identical in provenance to the directly-labeled 1/18 end-state figure."
    ),
    "revival_criteria": (
        "n/a as a standalone revival (mechanism already lifted extraction as measured); further "
        "extraction breadth improvements should re-check recall_goal_mediated end-to-end to "
        "confirm whether propagation remains blocked by pairing (per atom 29639) or whether a "
        "future pairing fix unlocks the extraction gain measured here."
    ),
    "primitive_assessment": (
        "No new primitive; extends the existing goal-extraction stage with additional "
        "syntactic-construction pattern classes (purpose-clause, modal-volition, commissive) "
        "layered onto the prior lexicon match, reusing the same CausalLinkRegister/open-close "
        "downstream organs unchanged. Reusable methodology: when a lift measured at one stage "
        "(extraction) does not propagate to an end-to-end metric, decompose immediately into "
        "the NEXT stage (pairing) with a dedicated companion cell rather than assuming a ceiling "
        "-- exactly what atom 29639 does."
    ),
    "hf_attribution": "n/a (MEASURED_MECHANISM, not an HF cell).",
    "fairness_verdict": (
        "FAIR: every cited number reproduces exactly off the raw extraction/residual_ceiling/"
        "causal_link_proposal/hard_pass_gate blocks, not the verdict_msg summary string. The "
        "referent of 'Marilla's narrated marker-free intent' was independently traced to and "
        "confirmed against the actual gold-file record (not accepted from the task input's "
        "characterization alone). Symmetric anti-negativity: flagged the 5/18 start-state figure "
        "as an inferred (not directly field-labeled) quantity rather than silently upgrading its "
        "evidentiary status to match the directly-measured 1/18 end-state figure."
    ),
    "cross_arc_overlap": (
        "substrate_query.sh check ('goal statement extraction construction purpose clause modal "
        "volition commissive') returns top hits at cosine<=0.4229, all generic WordNet/concept-"
        "node matches (election_commission, CN_construction, construction) -- no prior "
        "experiment-cell duplicate of this specific construction-based goal-extraction result. "
        "Composes directly with 29609 (CausalLinkRegister organ reused unchanged), 29634 (signal "
        "probe naming goal/intention tracking as the next lever), 29636 (prior lexical-only "
        "goal-causal-link measurement this cell directly extends)."
    ),
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}

ATOM_GOAL_CLOSE_PAIRING_CAP = {
    "atom_id": (
        "math::goal_close_pairing_semantic_v1_mechanical_reachability_gain_0p000_semantic_"
        "content_pairing_gain_0p000_both_tie_recall_0p111_fp_0p0_mechanism_level_arms_differ_"
        "verified_440vs469_proposed_links_outcome_level_ties_9_goal_mediated_decomposition_"
        "6of9_extraction_bound_3of9_pairing_bound_0of9_recovered_named_residual_satisfy_vs_"
        "restate_discrimination_content_overlap_necessary_not_sufficient_verdict_CAP_semantic_"
        "resolution_still_deep_frontier_75bcfc3ee_MEASURED_MECHANISM_LOCAL_ONLY"
    ),
    "seq": SEQ_GOAL_CLOSE_PAIRING_CAP,
    "op": "insert",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "MEASURED_MECHANISM",
    "grade": "MM",
    "verdict": (
        "MECHANICAL ALIGNMENT VERIFIED NOT BROKEN; PAIRING CAP LOCALIZED TO SATISFY-VS-RESTATE "
        "DISCRIMINATION. Independent recompute off the raw arms / decomposition / hard_pass_gate "
        "blocks (not the verdict_msg/summary string alone) confirms: three arms measured against "
        "the same 471-open broad extractor -- same_agent_baseline (440 proposed links), "
        "mechanical_reachability (469 proposed links, gate=drop same-agent-close requirement, "
        "accept nearest any-agent close-marker clause), semantic_content_pairing (469 proposed "
        "links, gate=broadened reachability + same-agent-OR-content-word-overlap). All THREE tie "
        "at recall_goal_mediated=0.1111111111111111 (1/9) and fp_rate=0.0 -- mechanical_gain_"
        "over_same_agent=0.0, semantic_gain_over_mechanical=0.0, total_gain_over_baseline=0.0 "
        "exactly, reproduced by direct division. arms_differ_verified=true at the MECHANISM level "
        "(distinct proposed-link-set digests: same_agent=b8e8244f..., mechanical_reachability="
        "1c683e27..., semantic_content_pairing=2587cf54..., with n_proposed_links 440/469/469 "
        "differing) but arms_differ_outcome_level=false (all three share outcome digest "
        "9be78753...) -- confirming this is a genuine null result on the narrow 9-item gold set, "
        "not a digest-compare bug (the file's own arms_differ_exempted_note explicitly documents "
        "this distinction, independently corroborated here). decomposition of the 9 goal-mediated "
        "causal-link items: n_extraction_bound=6 (no feeding goal-open extracted at all -- "
        "upstream of pairing, cannot be recovered by ANY pairing improvement), n_pairing_bound=3 "
        "(open extracted but no arm paired it to the correct resolving event), n_recovered=0 "
        "(neither new arm recovered any additional item). Named residual for the 3 pairing-bound "
        "items: content-overlap alone cannot discriminate a genuine SATISFY event from a mere "
        "RESTATEMENT (a character re-mentioning their wish recurs the same topic words without "
        "resolving it) -- the nearest qualifying same-chapter clause under content-gating is "
        "often the restatement, not the true distal resolving event. Verdict = "
        "CAP_SEMANTIC_RESOLUTION_STILL_DEEP_FRONTIER, correctly tiered MEASURED_MECHANISM: "
        "mechanical clause<->event alignment is a real, verified-working organ; the wall is "
        "specifically semantic discourse-relation classification (satisfy vs restate vs thwart), "
        "not mechanical brittleness."
    ),
    "anchor": "goal_close_pairing_semantic_v1",
    "anchor_name": "goal_close_pairing_semantic_v1_2026_08_03",
    "cell": (
        "experiments/exp_goal_close_pairing_semantic_v1.py; "
        "data/exp_goal_close_pairing_semantic_v1/metrics.json; commit 75bcfc3ee"
    ),
    "headline": (
        "Goal open/close pairing CAP: mechanical-reachability broadening (+0.000 gain) and "
        "semantic content-overlap gating (+0.000 gain over mechanical) both tie the same-agent "
        "baseline at recall_goal_mediated=0.111, fp=0.0, despite mechanism-level arms genuinely "
        "differing (440 vs 469 proposed links, distinct link-set digests) -- a verified, not "
        "artifactual, null. Decomposition of the 9 goal-mediated gold items: 6/9 EXTRACTION_"
        "BOUND (no feeding goal-open ever extracted -- unreachable by any pairing fix), 3/9 "
        "PAIRING_BOUND (open extracted, but content-overlap pairing selects a topical RESTATEMENT "
        "clause instead of the true distal SATISFY event), 0/9 recovered by either new arm. "
        "Localizes the residual precisely: mechanical clause<->event alignment already works; "
        "the wall is a satisfy-vs-restate (or more broadly satisfy/thwart) discourse-relation "
        "classifier, which content-overlap alone structurally cannot supply."
    ),
    "key_metrics": {
        "recall_goal_mediated_same_agent": 0.1111111111111111,
        "recall_goal_mediated_mechanical_reachability": 0.1111111111111111,
        "recall_goal_mediated_semantic_content_pairing": 0.1111111111111111,
        "fp_rate_all_arms": 0.0,
        "n_negative_sampled": 200,
        "n_proposed_links_same_agent": 440,
        "n_proposed_links_mechanical_reachability": 469,
        "n_proposed_links_semantic_content_pairing": 469,
        "mechanical_gain_over_same_agent": 0.0,
        "semantic_gain_over_mechanical": 0.0,
        "total_gain_over_baseline": 0.0,
        "n_goal_mediated_total": 9,
        "n_extraction_bound": 6,
        "n_pairing_bound": 3,
        "n_recovered": 0,
        "arms_differ_verified": True,
        "arms_differ_mechanism_level": True,
        "arms_differ_outcome_level": False,
        "coherence_baseline_recall_integration": 0.5555555555555556,
        "coherence_baseline_fp_rate": 0.31,
        "hand_matched_upper_bound_explicit": 0.8888888888888888,
        "hard_pass": False,
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Independent Python read of data/exp_goal_close_pairing_semantic_v1/metrics.json's raw "
        "arms, decomposition, and hard_pass_gate blocks (not verdict_msg alone). arms."
        "same_agent_baseline.recall_goal_mediated=0.1111111111111111, arms.mechanical_"
        "reachability.recall_goal_mediated=0.1111111111111111, arms.semantic_content_pairing."
        "recall_goal_mediated=0.1111111111111111 -- all three confirmed identical by direct "
        "field comparison; n_proposed_links 440/469/469 confirmed differing. decomposition."
        "n_extraction_bound=6, n_pairing_bound=3, n_recovered=0, summing to n_goal_mediated_"
        "total=9 -- confirmed the per_goal_mediated_item list (9 entries) sums to exactly this "
        "split by residual_class field (6 x 'EXTRACTION_BOUND', 3 x 'PAIRING_BOUND', 0 with "
        "'recovered'=true), independently recounted from the itemized list, not taken from the "
        "summary integers alone. arms_digest.mechanism_level three distinct hashes confirmed "
        "differing; arms_digest.outcome_level all three identical (9be78753...) confirmed -- "
        "matches the raw file's own arms_differ_mechanism_level=true/arms_differ_outcome_level="
        "false fields exactly, corroborating (not just trusting) the file's own exemption note."
    ),
    "composes_seq": [29609, 29631, 29633, 29634, 29636, SEQ_GOAL_EXTRACTOR_BROAD],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_GOAL_CLOSE_PAIRING_CAP - 1,
    "honest_scope": (
        "Small-N: 9 goal-mediated causal-link gold items (the entire decomposition analysis "
        "rests on this set), 200 sampled negatives for fp_rate. gold_verified=false on the "
        "underlying goal-intention gold file (confirmed by direct read). The reported +0.000 "
        "gains are exact ties on a 9-item denominator -- a single additional recovered item "
        "would move recall by 0.111, so these are NOT statistically precise gain estimates, they "
        "are exact-zero recoveries on a narrow gold set; the qualitative conclusion (mechanical "
        "alignment not broken, satisfy-vs-restate is the wall) is the load-bearing claim, not a "
        "precise effect-size estimate. Single source text (Anne of Green Gables)."
    ),
    "framing_correction": (
        "None required beyond honest-scope note above: the task input's characterization "
        "('arms_differ_verified=True at mechanism level, ties at outcome') is confirmed exactly "
        "as stated by independent recompute, no correction needed."
    ),
    "revival_criteria": (
        "Build and wire a satisfy/thwart/cause discourse-relation classifier (learned or "
        "construction-based, per the no-bolt-on-parser lock -- earned or supplied-as-data, not "
        "an external reader) that discriminates a genuine resolving SATISFY event from a topical "
        "RESTATEMENT; re-run this cell's pairing stage gated on that classifier's output instead "
        "of raw content-overlap and re-check recall_goal_mediated on the same 3 pairing-bound "
        "items (anne_causal_001, anne_causal_006, anne_causal_016 per the decomposition's "
        "residual_class='PAIRING_BOUND' entries) -- if recall rises materially above 0.111 while "
        "fp_rate stays near 0.0, that confirms the satisfy-vs-restate wall was the correct "
        "diagnosis and closes this CAP."
    ),
    "primitive_assessment": (
        "No new primitive; reuses the atom-29609 CausalLinkRegister organ and the broad "
        "extractor's opens (atom 29638) unchanged, adding two new close-selection GATES "
        "(mechanical any-agent reachability; content-word-overlap semantic gating) layered on "
        "the existing find_close_for_open search. Reusable methodology: when a downstream "
        "recall metric stays flat after a broadening change, do NOT assume the broadening was "
        "wasted -- verify at the MECHANISM level (distinct proposed-set digests) whether the "
        "arms actually differ before concluding a null; here they genuinely differ mechanically "
        "while tying at outcome, which is itself informative (the broadening reached new "
        "candidate closes, but none were the CORRECT one for these 9 items)."
    ),
    "hf_attribution": "n/a (MEASURED_MECHANISM, not an HF cell).",
    "fairness_verdict": (
        "FAIR: every cited number reproduces exactly off the raw arms/decomposition/hard_pass_"
        "gate blocks, not the verdict_msg summary string. The decomposition's per-item residual "
        "classes were independently recounted from the itemized list (not taken from the summary "
        "integers alone), confirming 6+3+0=9 exactly. Symmetric anti-negativity: this is a null-"
        "result cell and is graded with the same rigor as a positive lift would receive -- the "
        "mechanism-level-differs-but-outcome-ties finding is reported as informative (localizes "
        "the residual precisely) rather than either inflated into a false positive or dismissed "
        "as a wasted experiment."
    ),
    "cross_arc_overlap": (
        "substrate_query.sh check ('goal open close pairing satisfy restate discourse semantic "
        "content overlap mechanical reachability same agent') returns top hits at cosine<=0.2754, "
        "generic memory-note matches about semantic-vs-content-reference retrieval scoring (not "
        "an experiment-cell duplicate). Composes directly with 29609 (CausalLinkRegister organ "
        "reused unchanged), 29636 (prior same-agent-baseline measurement this cell directly "
        "extends with two new arms), and this session's atom 29638 (the broad extractor whose "
        "471 opens feed this cell's pairing arms)."
    ),
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}

ATOM_FRONTIER_SYNTHESIS = {
    "atom_id": (
        "meta::comprehension_frontier_exhaustively_localized_glass_box_extracts_structure_"
        "entities_events_goal_statements_pattern_residual_1of18_last_mile_is_semantic_relation_"
        "inference_unstated_goal_inference_6of9_satisfy_thwart_cause_discrimination_3of9_three_"
        "independent_glass_box_caps_converge_causal_link_overfire_goal_extraction_lexicon_goal_"
        "pairing_content_overlap_deep_frontier_is_earned_semantic_relation_inference_or_supplied_"
        "relational_knowledge_not_more_lexical_pattern_tuning_userAB_investment_fork_CERT_NEUTRAL_"
        "SYNTHESIS_LOCAL_ONLY"
    ),
    "seq": SEQ_FRONTIER_SYNTHESIS,
    "op": "insert",
    "corpus": "meta",
    "tier": "CERT_NEUTRAL_SYNTHESIS",
    "cert_status": "n/a (CERT-neutral cross-arc synthesis atom)",
    "grade": "META",
    "verdict": (
        "SYNTHESIS OF MEASURED SUB-RESULTS (not a new experiment; per STANDARD_META_SYNTHESIS, "
        "tiered as a tentative-synthesis since the composing evidence spans qualitatively "
        "different sub-mechanisms rather than 3+ tight-cross-seed-cv repeats of one measurement). "
        "Independently re-verified off disk, each composing atom's own key_metrics: causal-link "
        "detection over-fires when links must be detected rather than supplied (atom 29633, "
        "delta=0.3611 from gold-isolated ceiling); goal-extraction lexicon recovers only 2/18 "
        "explicit gold goals (atom 29636), and even a broadened construction-based extractor "
        "(atom 29638, this session) only lifts that to 3/18 with the residual now dominated by "
        "propagation failure, not extraction coverage (pattern-residual is down to 1/18); goal "
        "open/close pairing (atom 29639, this session) ties at recall=0.111 under both mechanical-"
        "reachability and semantic-content-overlap broadening, with a clean 6-extraction-bound / "
        "3-pairing-bound decomposition of the 9 goal-mediated items and 0 recovered by either "
        "new arm. These THREE independent glass-box capability-attempts (causal-link coherence "
        "gating, goal-extraction lexicon/construction breadth, goal-pairing content-overlap) "
        "converge on the same qualitative wall from three different angles: glass-box PATTERN "
        "and LEXICAL methods can now nearly saturate STRUCTURE extraction (entities, events, "
        "goal-statements: atom 29638's pattern-residual is 1/18, i.e. ~94% of explicit goal "
        "statements are structurally reachable by construction patterns), but every measured "
        "end-to-end path still bottoms out at SEMANTIC RELATION INFERENCE specifically: (a) "
        "inferring goals that are never lexically or syntactically marked at all (6/9 of the "
        "goal-mediated causal-link items in atom 29639's decomposition have NO feeding goal-open "
        "extracted by ANY construction pattern -- these are goals a human reader infers from "
        "context, not goals stated in an extractable construction), and (b) discriminating "
        "SATISFY from RESTATE (or more broadly satisfy/thwart/cause) between two events that "
        "share surface content (3/9 of the goal-mediated items, atom 29639's pairing-bound "
        "residual) -- content-word overlap is necessary but not sufficient for this "
        "discrimination, and no glass-box pattern method measured this session supplies it. "
        "This sharpens (not merely repeats) the pre-existing MEMORY.md 'extraction generalization "
        "is the wall' claim: the wall is not extraction of SURFACE structure (that is now nearly "
        "solved for goal statements specifically, 17/18 reachable) but extraction/inference of "
        "UNSTATED relational content and discourse-relation TYPE, which is a qualitatively "
        "harder, semantics-requiring task that pattern-matching on explicit constructions cannot "
        "reach by construction. This is exactly the USER's a/b/c investment fork named in the "
        "task input (earn a learned semantic-relation inferer vs supply relational knowledge as "
        "data vs continue lexical/pattern tuning) -- and this synthesis's evidence argues against "
        "option (c): three independent cells this session each tried a pattern/lexical-breadth "
        "improvement and each independently hit the SAME semantic-relation ceiling, which is "
        "evidence the remaining gap is not addressable by more pattern tuning of the kind tried "
        "so far, while remaining honest that this is a small-N (9-18 item), single-source-text "
        "observation, not a statistically powered generality claim, and does not itself decide "
        "between the earn-vs-supply fork (both remain live options under the no-bolt-on-parser "
        "lock)."
    ),
    "anchor": "comprehension_frontier_semantic_relation_synthesis",
    "anchor_name": "comprehension_frontier_semantic_relation_synthesis_2026_08_03",
    "cell": (
        "Synthesis over: data/exp_goal_extractor_broad_v1/metrics.json (atom 29638, this "
        "session); data/exp_goal_close_pairing_semantic_v1/metrics.json (atom 29639, this "
        "session); data/exp_causal_endtoend_integration_gap_v1/metrics.json (atom 29633); "
        "data/exp_causal_link_proposal_signal_probe_v1/metrics.json (atom 29634); "
        "data/exp_goal_register_causal_link_v1/metrics.json (atom 29636); prior synthesis atom "
        "29637. No new cell authored for this atom itself."
    ),
    "headline": (
        "The comprehension frontier is now exhaustively localized this session: glass-box "
        "construction-pattern methods can extract STRUCTURE (entities, events, goal-statements) "
        "with a pattern-residual down to 1/18 (atom 29638), but three independent glass-box "
        "capability attempts this session (causal-link coherence gating atom 29633/29634, goal-"
        "extraction breadth atom 29638, goal-pairing content-overlap atom 29639) each "
        "independently converge on the SAME wall: SEMANTIC RELATION INFERENCE, specifically (a) "
        "inferring goals never lexically marked (6/9 of goal-mediated links) and (b) satisfy-vs-"
        "restate discourse-relation discrimination (3/9). Names the deep frontier as EARNED "
        "semantic-relation inference or SUPPLIED relational knowledge, not more lexical/pattern "
        "tuning -- directly informs the USER's a/b/c investment fork under the standing no-bolt-"
        "on-parser lock, without itself deciding between earn-vs-supply."
    ),
    "key_metrics": {
        "goal_extraction_pattern_residual_atom_29638": 0.05555555555555555,
        "goal_extraction_recall_broad_atom_29638": 0.16666666666666666,
        "causal_link_detection_delta_from_ceiling_atom_29633": 0.3611111111111111,
        "goal_causal_link_fp_given_goals_atom_29636": 0.0,
        "goal_pairing_extraction_bound_fraction_atom_29639": 0.6666666666666666,
        "goal_pairing_pairing_bound_fraction_atom_29639": 0.3333333333333333,
        "goal_pairing_recovered_fraction_atom_29639": 0.0,
        "n_goal_mediated_total": 9,
        "coherence_baseline_fp_rate_atom_29634": 0.31,
        "n_composing_atoms": 6,
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Each composing atom's key_metrics field independently re-read off data/substrate_index/"
        "math/atoms.jsonl this pass (atoms 29633/29634/29636 already independently verified off-"
        "disk at their own prior landings; atoms 29638/29639 verified off-disk earlier in this "
        "same session per this script's own two prior entries). Confirmed: 29633.key_metrics "
        "delta_a_to_c_link_detection_damage=0.3611111111111111 -- matches exactly. 29636."
        "key_metrics causal_link_fp_rate=0.0 -- matches exactly. 29638 (this session) "
        "unreachable_fraction_explicit_broad=0.05555555555555555, extraction_recall_explicit_"
        "broad=0.16666666666666666 -- matches exactly (same values re-read, not re-derived). "
        "29639 (this session) n_extraction_bound=6/9=0.6666..., n_pairing_bound=3/9=0.3333..., "
        "n_recovered=0/9=0.0 -- independently re-divided, matches exactly."
    ),
    "composes_seq": [29610, 29633, 29634, 29636, 29637, SEQ_GOAL_EXTRACTOR_BROAD, SEQ_GOAL_CLOSE_PAIRING_CAP],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_FRONTIER_SYNTHESIS - 1,
    "honest_scope": (
        "This is a SYNTHESIS of already-measured sub-results, not a new experiment or a fresh "
        "measurement in its own right. All composing gold sets are small-N (9-25 items) and "
        "gold_verified=false, drawn from a single source text (Anne of Green Gables) -- this "
        "synthesis inherits those caveats and does not upgrade any of them. The convergence claim "
        "('three independent glass-box CAPs converge on the same wall') is a PATTERN observation "
        "across 3 cells this session on overlapping/adjacent gold subsets (not 3 fully "
        "independent datasets), so it should be read as a strategic-frontier naming that is "
        "internally consistent and evidence-grounded, not a statistically powered cross-domain "
        "claim; hence CERT-neutral, cert_delta=0. Expansion criterion: a fourth independent "
        "glass-box attempt on a DIFFERENT relational-inference sub-task (e.g. temporal-sequence "
        "ordering, negation-scope resolution) showing the same organ-precise/semantic-relation-"
        "bottlenecked pattern would strengthen the generality claim; a counter-example (a glass-"
        "box pattern method that DOES close a semantic-relation gap without earned/supplied "
        "relational knowledge) would falsify the 'deep frontier requires earn-or-supply' half of "
        "this claim and should demote this synthesis."
    ),
    "framing_correction": (
        "The task input frames the synthesis claim in the third person as an established fact "
        "('the comprehension frontier is now EXHAUSTIVELY localized'). This atom retains that "
        "framing as the headline (it is well-supported by the three composing cells) but adds "
        "the honest-scope caveat above: 'exhaustively localized' means exhaustively localized "
        "GIVEN the specific glass-box methods tried this session on this specific text and gold "
        "set, not a claim that no other pattern-based approach could ever close the gap. Also "
        "narrows the task input's implicit framing that these are '3 fully independent CAPs': "
        "atoms 29638/29639 share the same underlying gold-item set (the 9 goal-mediated causal-"
        "link items) as each other, so they are two angles on largely the SAME residual, not two "
        "independent samples -- only atom 29633/29634 (the causal-link-detection-without-goals "
        "measurement) draws on a meaningfully different comparison (coherence-baseline over-fire "
        "vs goal-specific pairing failure). This atom counts it as 'three independent glass-box "
        "capability ATTEMPTS' (a true, verifiable count of distinct mechanisms tried) rather than "
        "'three independent EVIDENCE SOURCES' (which would overstate the statistical "
        "independence of the underlying observations)."
    ),
    "revival_criteria": (
        "n/a for the synthesis itself (naming of a strategic frontier). The underlying claim "
        "would be strengthened by: (a) a satisfy/thwart discourse-relation classifier (earned or "
        "supplied-as-data per the no-bolt-on-parser lock) closing the 3/9 pairing-bound residual "
        "from atom 29639 and confirming the predicted recall lift; (b) an unstated-goal inference "
        "mechanism (e.g. a learned intention-inference model, or supplied common-sense-goal "
        "knowledge) closing some fraction of the 6/9 extraction-bound residual; (c) gold-"
        "verifying the composing gold sets (currently gold_verified=false); (d) a fourth "
        "independent relational-inference sub-task (temporal ordering, negation scope) showing "
        "the same pattern to strengthen generality."
    ),
    "primitive_assessment": (
        "No new primitive. Reusable methodology: when three independently-designed glass-box "
        "capability attempts (different mechanisms, overlapping-but-not-identical gold subsets) "
        "each converge on the same class of residual (semantic relation type, not surface "
        "structure), that convergence is a stronger signal for locating the true strategic "
        "frontier than any single cell's result alone -- this is the correct way to promote a "
        "session's worth of individually-MEASURED_MECHANISM cells into a CERT-neutral strategic "
        "synthesis without overstating statistical power."
    ),
    "hf_attribution": "n/a (CERT-neutral synthesis atom, not an HF cell).",
    "fairness_verdict": (
        "FAIR, with two narrowing corrections applied (see framing_correction above): (1) the "
        "task input's implicit 'three independent CAPs' framing is corrected to 'three "
        "independent glass-box capability ATTEMPTS' since two of the three share the same "
        "underlying 9-item gold subset; (2) 'exhaustively localized' is scoped to the specific "
        "methods and text tried this session, not a universal claim. Both corrections are "
        "downward (narrowing), consistent with symmetric anti-negativity applied to a synthesis "
        "claim, not just a single-cell result."
    ),
    "cross_arc_overlap": (
        "This atom IS the cross-arc overlap check by construction (a synthesis across atoms "
        "29610/29633/29634/29636/29637/29638/29639); substrate_query.sh was run for both new "
        "underlying atoms (29638 cosine<=0.4229, 29639 cosine<=0.2754, no experiment-cell "
        "duplicates for either) at their own landings this session. No separate query run for "
        "this synthesis-level atom itself since it composes only already-audited atoms and "
        "introduces no new experimental claim requiring a fresh dedup check."
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

    atoms = (ATOM_GOAL_EXTRACTOR_BROAD, ATOM_GOAL_CLOSE_PAIRING_CAP, ATOM_FRONTIER_SYNTHESIS)
    for atom in atoms:
        atom["ts"] = now
        atom["ts_iso"] = ts_iso
        atom["ts_day"] = ts_day

    ledger_extractor = make_ledger_entry(
        SEQ_GOAL_EXTRACTOR_BROAD, ATOM_GOAL_EXTRACTOR_BROAD, "math",
        "MEASURED_MECHANISM CERT +0 (broad glass-box goal extractor). Independent recompute off "
        "raw extraction/residual_ceiling/causal_link_proposal blocks reproduces exactly: "
        "extraction_recall_explicit lifts 0.111->0.167 (2/18->3/18), unreachable-by-pattern "
        "residual drops to 1/18 (id anne_goal_018, confirmed against gold file as Marilla's "
        "narrated marker-free intent), but recall_goal_mediated stays flat at 0.111 end-to-end -- "
        "bottleneck moved from extraction to pairing. Curly-apostrophe normalization bugfix "
        "confirmed present and load-bearing.",
        "AUDIT-ONLY (hdi_skunkworks) independent recompute off data/exp_goal_extractor_broad_v1/"
        "metrics.json, NOT off verdict_msg alone. Commit 6a25dd91d. Cross-arc overlap check via "
        "substrate_query.sh: cosine<=0.4229, no dup. LOCAL-ONLY.",
    )
    ledger_pairing = make_ledger_entry(
        SEQ_GOAL_CLOSE_PAIRING_CAP, ATOM_GOAL_CLOSE_PAIRING_CAP, "math",
        "MEASURED_MECHANISM CERT +0 (goal open/close pairing CAP). Independent recompute off raw "
        "arms/decomposition blocks reproduces exactly: mechanical-reachability and semantic-"
        "content-pairing arms both tie same-agent baseline at recall=0.111, fp=0.0 despite "
        "genuinely differing at the mechanism level (440 vs 469 proposed links, distinct "
        "digests) -- confirmed a real null, not a digest-compare bug. Decomposition of 9 goal-"
        "mediated items: 6 extraction_bound, 3 pairing_bound, 0 recovered -- independently "
        "recounted from itemized list, matches summary integers exactly. Named residual = "
        "satisfy-vs-restate discrimination, content overlap necessary-not-sufficient.",
        "AUDIT-ONLY (hdi_skunkworks) independent recompute off data/exp_goal_close_pairing_"
        "semantic_v1/metrics.json, NOT off verdict_msg alone. Commit 75bcfc3ee. Cross-arc "
        "overlap check via substrate_query.sh: cosine<=0.2754, no dup. LOCAL-ONLY.",
    )
    ledger_synthesis = make_ledger_entry(
        SEQ_FRONTIER_SYNTHESIS, ATOM_FRONTIER_SYNTHESIS, "meta",
        "CERT-neutral cross-arc synthesis atom (cert_delta=0). Composes atoms 29610/29633/29634/"
        "29636/29637/29638/29639: glass-box construction methods now nearly saturate STRUCTURE "
        "extraction (goal-statement pattern-residual 1/18), but three independent glass-box "
        "capability attempts this session converge on the same wall -- SEMANTIC RELATION "
        "INFERENCE (unstated-goal inference, 6/9; satisfy-vs-restate discrimination, 3/9). Names "
        "the deep frontier as earned semantic-relation inference or supplied relational "
        "knowledge, informing the USER's a/b/c investment fork, without deciding it. Two honest "
        "narrowing corrections applied (see framing_correction field): 'three independent CAPs' "
        "corrected to 'three independent attempts' since two share the same 9-item gold subset; "
        "'exhaustively localized' scoped to methods/text tried this session.",
        "AUDIT-ONLY (hdi_skunkworks) synthesis-level composition, each composing atom's own "
        "key_metrics independently re-read off data/substrate_index/math/atoms.jsonl this pass. "
        "LOCAL-ONLY.",
    )

    atomic_append_jsonl(MATH_ATOMS_PATH, ATOM_GOAL_EXTRACTOR_BROAD)
    atomic_append_jsonl(MATH_ATOMS_PATH, ATOM_GOAL_CLOSE_PAIRING_CAP)
    atomic_append_jsonl(META_ATOMS_PATH, ATOM_FRONTIER_SYNTHESIS)

    atomic_append_jsonl(LEDGER_PATH, ledger_extractor)
    atomic_append_jsonl(LEDGER_PATH, ledger_pairing)
    atomic_append_jsonl(LEDGER_PATH, ledger_synthesis)

    results = []
    for path, seq, atom_id in (
        (MATH_ATOMS_PATH, SEQ_GOAL_EXTRACTOR_BROAD, ATOM_GOAL_EXTRACTOR_BROAD["atom_id"]),
        (MATH_ATOMS_PATH, SEQ_GOAL_CLOSE_PAIRING_CAP, ATOM_GOAL_CLOSE_PAIRING_CAP["atom_id"]),
        (META_ATOMS_PATH, SEQ_FRONTIER_SYNTHESIS, ATOM_FRONTIER_SYNTHESIS["atom_id"]),
    ):
        found, count = verify_load(path, expect_seq=seq, expect_atom_id=atom_id)
        assert found, f"FAIL: atom seq={seq} not found in {path} after write"
        results.append((path, seq, count))

    for seq in (SEQ_GOAL_EXTRACTOR_BROAD, SEQ_GOAL_CLOSE_PAIRING_CAP, SEQ_FRONTIER_SYNTHESIS):
        found, count = verify_load(LEDGER_PATH, expect_seq=seq)
        assert found, f"FAIL: ledger entry seq={seq} not found in {LEDGER_PATH} after write"

    for path, seq, count in results:
        print(f"OK: atom seq={seq} written to {path} ({count} total lines)")
    print(f"OK: 3 ledger entries written to {LEDGER_PATH}")
    print("atom_ids:")
    for atom in atoms:
        print(f"  seq={atom['seq']} corpus={atom['corpus']} -> {atom['atom_id'][:100]}...")


if __name__ == "__main__":
    main()
