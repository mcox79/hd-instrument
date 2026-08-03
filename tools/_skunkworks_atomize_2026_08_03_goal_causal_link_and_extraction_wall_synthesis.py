"""
A5-gated atomization: goal-register causal-link cell (MEASURED_MECHANISM) +
CERT-neutral extraction-wall META-SYNTHESIS. AUDIT-ONLY (hdi_skunkworks).
Independent recompute off data/exp_goal_register_causal_link_v1/metrics.json's
raw open_close_register / causal_link_proposal / comparison / hard_pass_gate
blocks (NOT off verdict_msg/summary alone), plus cross-referencing prior
composed atoms (29610, 29613, 29629, 29631, 29632, 29633, 29634, 29635) already
on disk for the meta-synthesis.

Writes TWO atoms (seq 29636 math, seq 29637 meta) + 2 matching cert_ledger.jsonl
entries, atomically (tmp -> os.replace) per file, then verify-loads all files
and runs an integrity check. LOCAL-ONLY: no origin push, no remote persist.
"""
import json
import os
import time
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATH_ATOMS_PATH = os.path.join(REPO, "data", "substrate_index", "math", "atoms.jsonl")
META_ATOMS_PATH = os.path.join(REPO, "data", "substrate_index", "meta", "atoms.jsonl")
LEDGER_PATH = os.path.join(REPO, "data", "substrate_index", "meta", "cert_ledger.jsonl")

SEQ_GOAL_CAUSAL_LINK = 29636
SEQ_EXTRACTION_WALL_SYNTHESIS = 29637

ATOM_GOAL_CAUSAL_LINK = {
    "atom_id": (
        "math::goal_register_causal_link_v1_organ_precise_fp0p000_selfconsistency1p0_but_"
        "recall_goal_mediated_0p111_1of9_bottlenecked_by_automated_goal_extraction_recall_"
        "explicit_0p111_2of18_two_independent_0p111s_not_the_same_computation_vs_coherence_"
        "baseline_recall0p556_fp0p31_hard_pass_gate_false_threshold0p4_diagnosis_extraction_"
        "too_noisy_hand_matched_upper_bound_explicit0p889_any1p0_1400331cc_MEASURED_MECHANISM_"
        "LOCAL_ONLY"
    ),
    "seq": SEQ_GOAL_CAUSAL_LINK,
    "op": "insert",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "MEASURED_MECHANISM",
    "grade": "MM",
    "verdict": (
        "MECHANISM PRECISE, EXTRACTION BOTTLENECKED (matches the file's own verdict field "
        "MEASURED_MECHANISM; deflates the file's own verdict_msg/summary framing of "
        "MIDDLE_BAND_SOME_SIGNAL_BELOW_BAR to the correct, more informative tier). Independent "
        "recompute off the raw open_close_register / causal_link_proposal / comparison / "
        "hard_pass_gate blocks (not the verdict_msg string) confirms: the Trabasso goal-open/"
        "close causal-link register (reusing the atom-29609 CausalLinkRegister bind/bundle/"
        "unbind/cleanup-argmax organ, symbolic Python open/close endpoint search over the "
        "automated clause+coref stream) proposes 182 links with organ_self_consistency_rate="
        "1.0 (every proposed link's register decode is internally self-consistent) and, on the "
        "200-sampled-negative-pair harness, false_positive_rate=0.0 (0/200) -- markedly cleaner "
        "than the composed coherence-overlap baseline (recall=0.5556, FP=0.31, over-fires; atom "
        "29634). This precision is exactly what the cert-ladder MEASURED_MECHANISM tier is for: "
        "the underlying causal-link MECHANISM, when it fires, is trustworthy. However, "
        "recall_goal_mediated (n_flagged_goal_mediated / n_goal_mediated_total) = 1/9 = 0.1111, "
        "well below the cell's own hard_pass_gate threshold of 0.4, so hard_pass=False and the "
        "gate's own diagnosis field reads EXTRACTION_TOO_NOISY. The root cause is upstream: "
        "automated_goal_extraction.extraction_recall_explicit (n_matched_to_explicit_gold / "
        "n_explicit_gold) = 2/18 = 0.1111 -- the goal-verb+subject lexicon extractor recovers "
        "only 2 of 18 explicit gold goal statements from real prose, so the open/close proposer "
        "structurally cannot exceed what the extractor hands it. NOTE (audit-added precision "
        "correction, not present in the task input's framing): the two 0.1111 figures "
        "(recall_goal_mediated=1/9 and extraction_recall_explicit=2/18) are NUMERICALLY "
        "IDENTICAL but are two SEPARATE measurements over different denominators/item sets "
        "(9 goal-mediated causal-link items vs 18 explicit-goal gold items) -- this is a "
        "coincidence of small-N arithmetic (1/9 and 2/18 both reduce to 1/9), not the same "
        "computation reported twice or one derived from the other; both independently confirm "
        "the same qualitative EXTRACTION-bottleneck diagnosis without being redundant evidence "
        "for it."
    ),
    "anchor": "goal_register_causal_link_v1",
    "anchor_name": "goal_register_causal_link_v1_2026_08_03",
    "cell": (
        "experiments/exp_goal_register_causal_link_v1.py; "
        "data/exp_goal_register_causal_link_v1/metrics.json; commit 1400331cc"
    ),
    "headline": (
        "Goal-based (Trabasso open/close) causal-link proposer on Anne of Green Gables (n=38 "
        "chapters, 14839 clauses, 199 automated opens, 9 goal-mediated + 9 non-goal integration "
        "gold causal-link items): FP=0.0 (0/200 sampled negatives) and organ_self_consistency="
        "1.0, both cleaner than the composed coherence-overlap baseline (recall=0.5556, FP=0.31; "
        "atom 29634) -- the MECHANISM is precise when it fires. recall_goal_mediated=1/9=0.1111 "
        "fails the cell's own hard_pass_gate (threshold 0.4); DIAGNOSIS=EXTRACTION_TOO_NOISY, "
        "traced to automated_goal_extraction.extraction_recall_explicit=2/18=0.1111 (the goal-"
        "verb+subject lexicon misses natural phrasing on real prose). Hand-matched upper bound "
        "(explicit_only=0.889, any=1.0) confirms the gold goals ARE findable by a human, "
        "sharpening the diagnosis to an automated-EXTRACTION gap, not an inherent goal-mediation "
        "ceiling. Verdict: MEASURED_MECHANISM / MIDDLE_BAND-flavored (not HARD_PASS) -- the "
        "goal->causal MECHANISM works precisely GIVEN correct goal input; the wall is automated "
        "goal EXTRACTION from varied real-language phrasing, not the open/close register organ."
    ),
    "key_metrics": {
        "n_proposed_links": 182,
        "organ_self_consistency_rate": 1.0,
        "causal_link_fp_rate": 0.0,
        "n_negative_sampled": 200,
        "recall_goal_mediated": 0.1111111111111111,
        "n_goal_mediated_total": 9,
        "n_flagged_goal_mediated": 1,
        "recall_all_integration": 0.05555555555555555,
        "n_all_integration_total": 18,
        "extraction_recall_explicit": 0.1111111111111111,
        "n_explicit_gold": 18,
        "n_matched_to_explicit_gold": 2,
        "chapter_precision_proxy": 0.48743718592964824,
        "n_automated_opens_total": 199,
        "coherence_baseline_recall_integration": 0.5555555555555556,
        "coherence_baseline_fp_rate": 0.31,
        "random_base_rate_recall_expected": 0.00202020202020202,
        "hand_matched_upper_bound_explicit_only": 0.8888888888888888,
        "hand_matched_upper_bound_any": 1.0,
        "hard_pass_gate_recall_threshold": 0.4,
        "hard_pass_gate_fp_absolute_threshold": 0.15,
        "hard_pass_gate_fp_relative_to_coherence_threshold": 0.5,
        "hard_pass": False,
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Independent Python read of data/exp_goal_register_causal_link_v1/metrics.json's raw "
        "open_close_register, causal_link_proposal, comparison, and hard_pass_gate blocks (not "
        "the verdict_msg/summary strings). open_close_register.n_proposed_links=182, "
        "organ_self_consistency_rate=1.0 -- reproduces exactly. causal_link_proposal."
        "n_flagged_goal_mediated=1, n_goal_mediated_total=9 -> recall_goal_mediated="
        "0.1111111111111111 (independently divided, matches field exactly); fp_rate=0.0, "
        "n_negative_sampled=200 -- reproduces exactly. automated_goal_extraction."
        "n_matched_to_explicit_gold=2, n_explicit_gold=18 -> extraction_recall_explicit="
        "0.1111111111111111 (independently divided, matches field exactly) -- confirmed this is "
        "a SEPARATE computation over a different item set than recall_goal_mediated, not the "
        "same number reported twice (flagged explicitly in the verdict above as an audit-added "
        "precision correction). comparison.coherence_baseline.recall_integration="
        "0.5555555555555556, fp_rate=0.31 (source data/exp_causal_link_proposal_signal_probe_v1/"
        "metrics.json, commit 912077b81) -- cross-checked against atom 29634's own key_metrics, "
        "matches exactly. hard_pass_gate.recall_goal_mediated_threshold=0.4, hard_pass=false, "
        "diagnosis_if_not_hard_pass='EXTRACTION_TOO_NOISY: automated goal-verb+subject "
        "extraction recovers only 0.11 of explicit gold goals; the open/close proposal cannot "
        "exceed what the extractor finds.' -- reproduces exactly. Noted the internal "
        "inconsistency in the raw file: the top-level 'verdict' field reads MEASURED_MECHANISM "
        "while 'verdict_msg' reads 'VERDICT=MIDDLE_BAND_SOME_SIGNAL_BELOW_BAR' -- this atom "
        "resolves that inconsistency per the cert-disposition ladder: MEASURED_MECHANISM is the "
        "correct tier (a real, precise mechanism bound measured given correct input), not a "
        "plain MIDDLE_BAND (which would imply ambiguous/partial signal requiring further sub-"
        "audit before any tier decision -- here the sub-audit is already conclusive: mechanism "
        "precise, bottleneck is a named, specific upstream extraction gap)."
    ),
    "composes_seq": [29609, 29631, 29633, 29634],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_GOAL_CAUSAL_LINK - 1,
    "honest_scope": (
        "Small-N: 9 goal-mediated causal-link gold items, 18 explicit-goal gold items, out of a "
        "38-chapter/14839-clause automated pipeline run. chapter_precision_proxy=0.487 is "
        "explicitly flagged in the raw metrics.json itself as a WEAK proxy, not a valid "
        "precision claim (the 21-item gold set is a sample, not exhaustive, so item-level "
        "precision against it has no valid denominator) -- this atom does not upgrade that "
        "caveat. The inferred-goal subset (3 items, NEEDS-DEEPER-TOM) is explicitly out of scope "
        "per the cell's own inferred_subset_ceiling block and is not counted toward this atom's "
        "recall figures. hard_pass=False is the honest headline result: this is a MEASURED_"
        "MECHANISM (mechanism-precision) finding, not a capability that clears any usable "
        "recall bar end-to-end."
    ),
    "framing_correction": (
        "The raw metrics.json file itself carries an internal tier inconsistency: verdict="
        "MEASURED_MECHANISM but verdict_msg says 'VERDICT=MIDDLE_BAND_SOME_SIGNAL_BELOW_BAR'. "
        "This atom resolves in favor of MEASURED_MECHANISM per the cert-disposition ladder, "
        "since the sub-audit is conclusive (mechanism precise + specific named bottleneck), not "
        "ambiguous. Also: the task input's framing ('recall_goal_mediated=1/9=0.111 because "
        "automated goal-extraction recall on the explicit subset = 2/18=0.111') implies one "
        "number is DERIVED FROM or CAUSED BY the other in a single computation; independent "
        "recompute confirms these are two separate measurements over different item sets that "
        "happen to reduce to the same fraction (1/9 == 2/18) -- both point at the same "
        "diagnosis (extraction is the bottleneck) but are not the same measurement counted "
        "twice. This narrows a slightly overstated causal-chain framing to an honest "
        "'two independent measurements, same diagnosis' framing."
    ),
    "revival_criteria": (
        "Improve automated goal extraction beyond the current goal-verb+subject lexicon (e.g. "
        "construction-conditional goal-cue matching per atoms 29604-29606, or a learned "
        "goal-phrase classifier) and re-run this cell's causal_link_proposal stage unchanged; "
        "if extraction_recall_explicit rises materially above 0.111, recall_goal_mediated is "
        "expected to rise correspondingly (the register/proposer mechanism itself is not the "
        "limiting factor per this atom's FP=0.0/self-consistency=1.0 measurement) -- re-VET "
        "against the same hard_pass_gate thresholds (recall>=0.4, FP<=0.15 absolute or <=0.5x "
        "coherence baseline) once a better extractor is wired in."
    ),
    "primitive_assessment": (
        "No new primitive; reuses the atom-29609 CausalLinkRegister organ (bind/bundle/unbind/"
        "cleanup-argmax) with a symbolic-Python open/close endpoint search layered on top. "
        "Reusable methodology: when a downstream mechanism's recall bottoms out, decompose into "
        "(a) does the CORE MECHANISM itself over-fire/mis-fire (measure self-consistency + FP "
        "on a shared negative-pair harness), vs (b) does the UPSTREAM EXTRACTION feeding it "
        "simply miss cases -- here (a) cleared cleanly (FP=0.0, self-consistency=1.0) while (b) "
        "is the demonstrated bottleneck (2/18), which is the correct diagnostic sequencing to "
        "avoid mis-attributing an extraction gap to the mechanism or vice versa."
    ),
    "hf_attribution": "n/a (MEASURED_MECHANISM, not an HF cell).",
    "fairness_verdict": (
        "FAIR: every cited number reproduces exactly off the raw open_close_register/"
        "causal_link_proposal/automated_goal_extraction/hard_pass_gate blocks, not the verdict_"
        "msg summary string. Symmetric anti-negativity applied both directions: deflated the "
        "raw file's own MIDDLE_BAND-leaning verdict_msg framing where the sub-audit supports a "
        "clearer MEASURED_MECHANISM tier (precise mechanism + named bottleneck), while also "
        "correcting the task input's slightly over-tight causal-chain framing of the two "
        "coincidentally-equal 0.1111 figures to an honest 'two independent measurements' "
        "framing -- narrows rather than inflates the claim on net."
    ),
    "cross_arc_overlap": (
        "substrate_query.sh check ('goal register open close causal link Trabasso goal "
        "intention tracking') returns top hits at cosine<=0.3271, all generic FrameNet/WordNet "
        "concept-node matches (Intentional_traversing::Goal, Goal, goal, intentional) -- no "
        "prior experiment-cell duplicate of this specific goal-register causal-link result. "
        "Composes directly with 29609 (the CausalLinkRegister organ reused here), 29631 (causal-"
        "link organ's 0.9167 gold-isolated ceiling), 29633 (wall localized to link-detection not "
        "event-extraction), and 29634 (the signal probe that NAMED goal/intention tracking as "
        "the next lever, based on the 9/18 goal-mediated fraction this cell's causal_link_"
        "proposal.n_goal_mediated_total=9 independently confirms) -- this cell is the direct "
        "follow-through on that named lever, and its result (mechanism precise, extraction is "
        "the new bottleneck) extends rather than duplicates 29633's link-detection localization "
        "to the goal-specific sub-case."
    ),
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}

ATOM_EXTRACTION_WALL_SYNTHESIS = {
    "atom_id": (
        "meta::extraction_wall_synthesis_every_competency_mechanism_works_given_correct_"
        "structure_but_every_endtoend_path_bottoms_out_at_extraction_of_structure_from_"
        "varied_real_prose_coref0p87_causal_organ0p9167_given_links_goal_causal_fp0p0_given_"
        "goals_vs_role_agentid0p625_causal_link_detection0p3611_delta_goal_extraction0p111_"
        "corroborates_preexisting_memory_claim_north_star_bottleneck_is_reading_frontend_not_"
        "comprehension_machinery_no_bolt_on_parser_lock_tension_named_CERT_NEUTRAL_SYNTHESIS_"
        "LOCAL_ONLY"
    ),
    "seq": SEQ_EXTRACTION_WALL_SYNTHESIS,
    "op": "insert",
    "corpus": "meta",
    "tier": "CERT_NEUTRAL_SYNTHESIS",
    "cert_status": "n/a (CERT-neutral cross-arc synthesis atom)",
    "grade": "META",
    "verdict": (
        "SYNTHESIS OF MEASURED SUB-RESULTS (not a new experiment; a naming of a strategic "
        "frontier, tiered MM_TENTATIVE_SYNTHESIS-equivalent per the STANDARD_META_SYNTHESIS "
        "macro since the composing evidence spans qualitatively different sub-mechanisms rather "
        "than 3+ tight-cross-seed-cv numeric repeats of the same measurement). Independently "
        "re-verified off disk, each composing atom's own key_metrics: coreference (atom 29613, "
        "F1=0.8719 vs recency-floor 0.462 collapsed, vs random 0.526 -- fair-test cleared); "
        "situation-model accumulate + multi-bank capacity (atoms 29609/29632/29635 -- register/"
        "capacity organ works and is now pipeline-wired); causal-link organ GIVEN gold links "
        "(atom 29631, organ_accuracy_integration=0.9167); goal-based causal-link proposer GIVEN "
        "correct goal input (atom 29636 this session, FP=0.0, self_consistency=1.0). Each of "
        "these MECHANISMS is precise/performant when fed correctly-structured input. Yet every "
        "attempted END-TO-END path measured this session bottoms out at EXTRACTION of that "
        "structure (mentions/roles/events/goals/causal-links) from varied real prose: role "
        "agent-ID extraction accuracy=0.625 (atom 29633's stage1, and the earlier full-pipeline "
        "HARD_FAIL at atom 29610); causal-LINK detection collapses integration accuracy by "
        "delta=0.3611 from the gold-isolated ceiling when links must be DETECTED rather than "
        "supplied (atom 29633, arm a-to-c); goal extraction recovers only 2/18=0.111 of explicit "
        "gold goal statements (atom 29636). This SPECIFIC pattern (organ precise, upstream "
        "extraction/detection of RELATIONAL or discourse structure is what fails) corroborates "
        "the pre-existing MEMORY.md claim that 'the wall is EXTRACTION GENERALIZATION on real "
        "text,' and further sharpens it: the wall is not extraction UNIFORMLY across every sub-"
        "task -- atom 29633's own arm-b measurement shows event-extraction damage (the same "
        "62.5% agent-ID weakness) does NOT propagate into that organ's integration-accuracy "
        "metric (delta a-to-b=0.0000, byte-identical to the gold-isolated ceiling) -- so a "
        "blanket 'all extraction is the wall, uniformly' claim would overstate what's measured. "
        "The precise, evidence-grounded framing: extraction/detection of RELATIONAL/discourse "
        "structure (causal LINKS between events, GOAL statements, and role-agent identity "
        "specifically where a downstream layer reads it directly) is the recurring bottleneck "
        "across every measured sub-mechanism this session, while at least one extraction "
        "sub-task (bare event-mention extraction feeding the causal-integration organ "
        "specifically) has been directly shown NOT to propagate damage in the one case tested. "
        "This synthesis names the strategic frontier as the READING FRONT-END (extraction/"
        "generalization of relational structure from varied real-language phrasing), not the "
        "comprehension machinery downstream of it, and flags the standing lock tension: per "
        "the no-bolt-on-parser discipline, this extraction capability must be EARNED (learned "
        "from data, own mechanism) or explicitly SUPPLIED-AS-DATA (lexicon/gazetteer, allowed "
        "per the supply-a-dictionary discipline), never bolted on as an external reader/parser."
    ),
    "anchor": "extraction_wall_cross_arc_synthesis",
    "anchor_name": "extraction_wall_cross_arc_synthesis_2026_08_03",
    "cell": (
        "Synthesis over: data/exp_causal_endtoend_integration_gap_v1/metrics.json (atom 29633); "
        "data/exp_causal_link_proposal_signal_probe_v1/metrics.json (atom 29634); "
        "data/exp_goal_register_causal_link_v1/metrics.json (atom 29636, this session); "
        "data/exp_causal_link_comprehension_fuller_v2/metrics.json (atom 29631); "
        "coreference gold_multientity_dense_v1.jsonl results (atom 29613); "
        "role end-to-end wiring result (atom 29610). No new cell authored for this atom itself."
    ),
    "headline": (
        "Cross-arc synthesis (CERT-neutral): across the comprehension descent this session, "
        "every measured competency's MECHANISM is precise/performant GIVEN correctly-extracted "
        "structure (coref F1=0.8719; causal organ 0.9167 given gold links; goal-causal FP=0.0 "
        "given goals), but every measured END-TO-END path bottlenecks at EXTRACTION/DETECTION "
        "of relational structure (role agent-ID 0.625; causal-link detection costs delta=0.3611 "
        "from ceiling; goal extraction 0.111) from varied real prose. Corroborates the pre-"
        "existing MEMORY.md 'extraction generalization' claim, with one sharpening caveat: bare "
        "event-mention extraction was directly shown NOT to propagate damage into the causal "
        "organ's integration metric in the one case tested (atom 29633 arm a-to-b, delta=0.0) "
        "-- so the wall is specifically RELATIONAL/discourse-structure extraction (links, "
        "goals, role-identity where consumed directly), not a uniform blanket claim across all "
        "extraction sub-tasks. Names the reading front-end as the north-star strategic frontier, "
        "not the comprehension machinery, and flags the standing no-bolt-on-parser lock tension "
        "(extraction must be earned or supplied-as-data, never a bolted-on external reader)."
    ),
    "key_metrics": {
        "coref_F1_atom_29613": 0.8719,
        "coref_recency_floor_atom_29613": 0.462,
        "causal_organ_integration_given_gold_links_atom_29631": 0.9167,
        "goal_causal_link_fp_given_goals_atom_29636": 0.0,
        "goal_causal_link_self_consistency_atom_29636": 1.0,
        "role_agentid_extraction_accuracy_atom_29633": 0.625,
        "causal_link_detection_delta_from_ceiling_atom_29633": 0.3611111111111111,
        "goal_extraction_recall_explicit_atom_29636": 0.1111111111111111,
        "event_extraction_damage_nonpropagation_delta_atom_29633": 0.0,
        "n_composing_atoms": 6,
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Each composing atom's key_metrics field independently re-read off data/substrate_index/"
        "math/atoms.jsonl this pass (not re-deriving from raw experiment metrics.json a second "
        "time, since each was already independently verified off-disk at its own landing -- this "
        "is a synthesis-level composition, per the STANDARD_META_SYNTHESIS macro's own "
        "instruction to 'verify each composing atom's evidence off-disk' meaning the atom "
        "record, not re-running every underlying experiment cell). Confirmed: 29613.key_metrics "
        "F1=0.8719 (approx, matches headline 'F1=0.8719' cited); 29631.key_metrics "
        "organ_accuracy_integration=0.9166666666666666 (matches 0.9167 rounded); 29633."
        "key_metrics delta_a_to_b_event_extraction_damage=0.0, delta_a_to_c_link_detection_"
        "damage=0.3611111111111111, stage1_agent_extraction_accuracy=0.625 -- all read directly "
        "off that atom's key_metrics block, confirmed exactly. 29636 (this session, above): "
        "causal_link_fp_rate=0.0, organ_self_consistency_rate=1.0, extraction_recall_explicit="
        "0.1111111111111111 -- confirmed exactly (same atom, independently recomputed off raw "
        "metrics.json earlier in this session before this synthesis atom was written)."
    ),
    "composes_seq": [29610, 29613, 29631, 29632, 29633, 29634, 29635, SEQ_GOAL_CAUSAL_LINK],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_EXTRACTION_WALL_SYNTHESIS - 1,
    "honest_scope": (
        "This is a SYNTHESIS of already-measured sub-results, not a new experiment or a fresh "
        "measurement in its own right -- it names a strategic frontier and corroborates a "
        "pre-existing MEMORY.md claim, it does not independently establish a new numeric result. "
        "The composing atoms span different gold sets, sample sizes (mostly small-N, n=18-25 "
        "range), and gold-verification states (several composing atoms are explicitly "
        "gold_verified=False) -- this synthesis inherits those honest-scope caveats and does not "
        "upgrade any of them. The claim 'extraction of relational structure is the recurring "
        "bottleneck' is a PATTERN observation across 4-6 sub-results this session, not a "
        "statistically powered cross-arc claim; it should be read as a strategic-frontier "
        "naming, not a certified capability boundary in its own right (hence CERT-neutral, "
        "cert_delta=0). Expansion criterion for promoting this synthesis's confidence: a future "
        "measured sub-mechanism in a DIFFERENT competency (e.g. temporal-sequence tracking, "
        "negation-scope resolution) showing the same organ-precise/extraction-bottlenecked "
        "pattern would strengthen the generality claim; a counter-example (an organ that fails "
        "even given gold-correct structure) would falsify the 'machinery downstream of "
        "extraction is not the wall' half of the claim and should demote this synthesis."
    ),
    "framing_correction": (
        "The task input's framing states the synthesis uniformly as 'EXTRACTION of structure "
        "(mentions/roles/events/goals/causal-links) from varied real prose' as one undifferentiated "
        "bottleneck. Independent re-check of the composing atom 29633 shows this needs one "
        "honest narrowing: bare EVENT-MENTION extraction (the agent-ID weakness, 62.5% accuracy) "
        "was directly measured to NOT propagate into the causal-integration organ's own metric "
        "in the one case tested (arm a-to-b delta=0.0000, byte-identical to the gold-isolated "
        "ceiling) -- so 'event extraction' cannot be lumped in with 'causal-link extraction' and "
        "'goal extraction' as equally-proven bottlenecks; only link-detection and goal-extraction "
        "have been DIRECTLY measured to cost accuracy end-to-end, per atoms 29633 and 29636. "
        "Role agent-ID extraction (0.625) IS a real measured weakness (per atom 29610's full-"
        "pipeline HARD_FAIL and the pre-existing MEMORY 'the wall = EXTRACTION GENERALIZATION' "
        "callout), but it bites via a DIFFERENT downstream path (multiclause entity-tracking, "
        "read-off layers that consume the extracted agent field directly) than the causal-organ "
        "integration metric that atom 29633 specifically measured it NOT to bite. This synthesis "
        "narrows the task input's uniform framing to: 'RELATIONAL/discourse-structure "
        "extraction (causal links, goals, and role-identity specifically where consumed "
        "directly by a downstream layer) is the recurring, DIRECTLY-measured bottleneck; bare "
        "event-mention extraction has one direct counter-example (non-propagation into the "
        "causal organ) and should not be asserted as equally proven.'"
    ),
    "revival_criteria": (
        "n/a for the synthesis itself (this is a naming of a strategic frontier, not a "
        "falsifiable capability claim in isolation). The underlying claim would be strengthened "
        "by: (a) a fifth/sixth measured competency (temporal ordering, negation scope, quantity/"
        "number tracking) showing the same organ-precise/extraction-bottlenecked split; (b) "
        "gold-verifying the several composing atoms currently gold_verified=False; (c) building "
        "and measuring an EARNED (not bolted-on) extraction improvement for either goal "
        "statements or causal-link cues and confirming the predicted recall lift propagates "
        "through to end-to-end accuracy, closing the loop this synthesis only currently asserts "
        "as a pattern."
    ),
    "primitive_assessment": (
        "No new primitive. Reusable methodology: when auditing a multi-competency arc, compare "
        "each competency's ORGAN-GIVEN-CORRECT-INPUT metric against its END-TO-END (organ + "
        "automated extraction) metric side by side -- a wide, consistent gap across "
        "unrelated competencies (coref, causal-link, goal-tracking) localizes the strategic "
        "frontier to the shared upstream stage (extraction) rather than to any one competency's "
        "downstream machinery, which is exactly the diagnostic pattern this synthesis names and "
        "which the no-bolt-on-parser lock makes non-trivial to resolve (the fix must be earned "
        "or supplied-as-data, not swapped in as an external reader)."
    ),
    "hf_attribution": "n/a (CERT-neutral synthesis atom, not an HF cell).",
    "fairness_verdict": (
        "FAIR, with one narrowing correction applied (see framing_correction above): the task "
        "input's uniform 'all extraction is the wall' framing is corrected to exclude bare "
        "event-mention extraction from the DIRECTLY-measured bottleneck list, per atom 29633's "
        "own arm a-to-b non-propagation result, since accepting the broader claim uncaveated "
        "would overstate what this session's evidence actually supports. This is a downward, "
        "not upward, correction -- symmetric anti-negativity discipline applied to a synthesis "
        "claim, not just to a single-cell result."
    ),
    "cross_arc_overlap": (
        "This atom IS the cross-arc overlap check by construction (a synthesis across atoms "
        "29610/29613/29631/29632/29633/29634/29635/29636); substrate_query.sh was run for the "
        "underlying goal-causal-link atom (29636, cosine<=0.3271, no dup) and the prior link-"
        "proposal atom (29634, cosine<=0.3613, no dup) at their own landings. No separate query "
        "run for this synthesis-level atom itself since it composes only already-audited atoms "
        "and introduces no new experimental claim requiring a fresh dedup check."
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

    for atom in (ATOM_GOAL_CAUSAL_LINK, ATOM_EXTRACTION_WALL_SYNTHESIS):
        atom["ts"] = now
        atom["ts_iso"] = ts_iso
        atom["ts_day"] = ts_day

    ledger_goal_causal = make_ledger_entry(
        SEQ_GOAL_CAUSAL_LINK, ATOM_GOAL_CAUSAL_LINK, "math",
        "MEASURED_MECHANISM CERT +0 (goal-register causal-link cell). Independent recompute off "
        "raw open_close_register/causal_link_proposal/automated_goal_extraction/hard_pass_gate "
        "blocks reproduces exactly: organ_self_consistency=1.0, FP=0.0 (0/200 negatives), "
        "recall_goal_mediated=1/9=0.1111, extraction_recall_explicit=2/18=0.1111 (confirmed as "
        "two SEPARATE measurements that coincidentally reduce to the same fraction, not one "
        "derived from the other). hard_pass=False confirmed; diagnosis EXTRACTION_TOO_NOISY "
        "confirmed. Resolved an internal tier inconsistency in the raw file (verdict field says "
        "MEASURED_MECHANISM, verdict_msg says MIDDLE_BAND) in favor of MEASURED_MECHANISM per "
        "the cert ladder (mechanism precise + specific bottleneck named, not ambiguous).",
        "AUDIT-ONLY (hdi_skunkworks) independent recompute off data/exp_goal_register_causal_"
        "link_v1/metrics.json, NOT off verdict_msg alone. Commit 1400331cc. LOCAL-ONLY.",
    )
    ledger_extraction_wall = make_ledger_entry(
        SEQ_EXTRACTION_WALL_SYNTHESIS, ATOM_EXTRACTION_WALL_SYNTHESIS, "meta",
        "CERT-neutral cross-arc synthesis atom (cert_delta=0). Composes atoms 29610/29613/29631/"
        "29632/29633/29634/29635/29636: every measured competency's mechanism is precise given "
        "correct structure, every end-to-end path bottlenecks at extraction/detection of "
        "relational structure. Corroborates pre-existing MEMORY.md 'extraction generalization' "
        "claim, WITH one narrowing correction applied: bare event-mention extraction (atom "
        "29633 arm a-to-b, delta=0.0) was directly measured to NOT propagate damage in the one "
        "case tested, so the uniform 'all extraction is the wall' framing in the task input is "
        "corrected to specifically relational/discourse-structure extraction (links, goals, "
        "role-identity where consumed directly), not a blanket claim across every extraction "
        "sub-task.",
        "AUDIT-ONLY (hdi_skunkworks) synthesis-level composition, each composing atom's own "
        "key_metrics independently re-read off data/substrate_index/math/atoms.jsonl this pass. "
        "LOCAL-ONLY.",
    )

    atomic_append_jsonl(MATH_ATOMS_PATH, ATOM_GOAL_CAUSAL_LINK)
    atomic_append_jsonl(META_ATOMS_PATH, ATOM_EXTRACTION_WALL_SYNTHESIS)

    atomic_append_jsonl(LEDGER_PATH, ledger_goal_causal)
    atomic_append_jsonl(LEDGER_PATH, ledger_extraction_wall)

    results = []
    for path, seq, atom_id in (
        (MATH_ATOMS_PATH, SEQ_GOAL_CAUSAL_LINK, ATOM_GOAL_CAUSAL_LINK["atom_id"]),
        (META_ATOMS_PATH, SEQ_EXTRACTION_WALL_SYNTHESIS, ATOM_EXTRACTION_WALL_SYNTHESIS["atom_id"]),
    ):
        found, count = verify_load(path, expect_seq=seq, expect_atom_id=atom_id)
        assert found, f"FAIL: atom seq={seq} not found in {path} after write"
        results.append((path, seq, count))

    for seq in (SEQ_GOAL_CAUSAL_LINK, SEQ_EXTRACTION_WALL_SYNTHESIS):
        found, count = verify_load(LEDGER_PATH, expect_seq=seq)
        assert found, f"FAIL: ledger entry seq={seq} not found in {LEDGER_PATH} after write"

    for path, seq, count in results:
        print(f"OK: atom seq={seq} written to {path} ({count} total lines)")
    print(f"OK: 2 ledger entries written to {LEDGER_PATH}")
    print("atom_ids:")
    for atom in (ATOM_GOAL_CAUSAL_LINK, ATOM_EXTRACTION_WALL_SYNTHESIS):
        print(f"  seq={atom['seq']} corpus={atom['corpus']} -> {atom['atom_id'][:100]}...")


if __name__ == "__main__":
    main()
