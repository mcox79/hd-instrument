"""
A5-gated atomization: exp_read_nested_clause_relative_third_reader_v1 (LOCAL commit 550455f5f) -> ONE atom (2026-07-18).
  MEASURED_MECHANISM / proven-bound. Cell verdict NEST_RESOLVES_EMBEDDING (HARD-PASS). Auditor CONFIRMS the
  clean-case pass and BANKS it MM with pinned scope: (1) SYMBOLIC-not-HD bridge gap; (2) corpus-wide precision
  ~0.40-0.55 vs the clean-gold 1.0; (3) reduced-RC / genuine 2-level embedding scoped out.

INDEPENDENT RECOMPUTE (off-disk, .venv, Fix #28):
  - ANGLE 1 (symbolic-not-HD): grep confirms bind()/unbind()/bundle() appear ONLY inside depth2_readout_fidelity
    (offline capacity measurement, lines 400-437). The RUNTIME nest axis (detect_rc_sites / nest_axis_passage /
    extract_passage_nest) is PURE SYMBOLIC: relativizer detection, span split at next-finite-verb, re-parse each
    span with the learned role-assigner, emit tuples, suppress mis-attach. The reader NEVER calls an HD primitive.
    So "the reader forms the HD reasoning-map" is NOT true -- the reader emits SYMBOLIC nested tuples; the reasoner
    (additive_map) uses HD binding; they are DIFFERENT representations, not yet bridged. Bridge gap OPEN.
  - ANGLE 3 (corpus-wide precision, the KEY RISK): ran --dump-rc, independently annotated ALL 73 detected RC fires
    (47 pids) for embedded-proposition correctness (subject+verb+obj). Result ~29/73 clearly correct, ~11 marginal,
    ~33 wrong => precision ~0.40 strict / ~0.55 lenient. vs the clean-gold transitive 12/12=1.0. CONFIRMS the risk:
    clean-gold HARD-PASS while corpus-wide precision is LOW. Dominant failure classes: (a) PIED-PIPING RCs
    ("through/with/on/upon/into/by which ... V") -- head forced as subject => wrong subject (~11 fires); (b)
    object-relatives with overt embedded subject on who/which ("words which I spoke", "life which you can never
    give", "anything which we know") -- head forced as subject; (c) demonstrative/complementizer "that" past the
    veto ("that evening", "quantity that would be", "see that crying") -- spurious nest; (d) wrong-head selection
    (nearest-noun picks wrong: "boy into my garden who meddles"->garden; "remember who watched"->remember); (e)
    spurious objects on intransitive RCs (blows/loveliness, springs/rock, frown/way, burneth/wherever, waxeth/dim)
    -- the same errors that fail 2/6 intransitive gold. These ~33 wrong tuples are ADDED to the foundation on RC
    pids and are NOT counted by nonrc_regression (which only checks NON-RC pids); an uncaptured precision cost.
  - REGRESSION guards independently confirmed: run_certification.py 208 PASSED / 0 FAILED (fleet green). metrics.json
    byte_identity_off deixis True+False over 79 lessons = True (structurally airtight: nest=False LITERALLY calls
    R.extract_passage_argrole). deixis unchanged 541=541. role controls 1.0/1.0. overlay 7/7. nonRC_touched=0.
  - CAN-FAIL genuine: nest scores 4/6 intransitive (fails brook/springs->spurious rock, flower/blows->spurious
    loveliness). Real self-penalty from the exact-match metric + spurious object => metric NOT construction-locked.
  - Depth-2 readout 1.0 on 51 real nest-links (N=2048) reproduces from metrics; it is an OFFLINE HD-CAPACITY check
    on WHATEVER was emitted (including wrong tuples), NOT an extraction-correctness measure. Confirms claim (b): HD
    nesting capacity is free. Depth-ceiling margin-shrink (D1 0.33-0.62 -> D2 0.13-0.20, Plate-1995 bounded-depth /
    human center-embedding ~2-3) is a STEP-0 pre-build probe recorded in the docstring, plausible + brain-faithful,
    NOT independently re-run in this VET.
  - +83.3pt: flat 2/12 -> nest 12/12. Flat's 2 correct (L09 men/hunt/animals, L30 boys/called/henry) are subject-RCs
    where flat SVO luckily seats the head as subject; the delta is REAL but on a single-annotator CLEAN-SITE-SELECTED
    gold (12 clean noun-headed non-pied-piping sites), a favorable denominator -- reported as scoped, not general.

TIER: MEASURED_MECHANISM / proven-bound. Clean-case symbolic-RC-parser pass is real; the bound is the corpus-wide
  precision + the symbolic-not-HD bridge gap + scoped-out reduced-RC. Not chain-grade (single-annotator clean-selected
  gold, low corpus-wide precision, symbolic not the HD-map unification, fragile span heuristic). Genuine positive
  component preserved (symmetric): the clean-case +83pt, the HD depth-2 capacity confirmation, and the HONEST
  bridge-gap identification are load-bearing. Author CREDITED: caught+rewrote a circular 100pt metric, self-flagged
  the symbolic caveat + explicit-relativizer scope + corpus-wide-precision-lower.

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
ATOMIZED_BY = "skunkworks_landed_vet_read_nested_clause_relative_third_reader_v1_MM_symbolic_RC_clean_pass_corpuswide_precision_bound_2026-07-18"
ATOMIZED_DATE = "2026-07-18"
ANCHOR = "read_nested_clause_relative_third_reader_v1"
CELL_COMMIT = "550455f5f"

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

XARC = (
    "cell-recorded prior-work check: substrate_query 'nested recursive binding extractor relative clause embedded "
    "proposition' -> top cosine 0.3975 = the KB LEXICAL concept atom 'relative_clause' (a foundation concept entry, "
    "NOT a prior experiment cell). No prior reader-arc EXPERIMENT cell returns at cosine>0.30 for this mechanism; "
    "this is a genuinely NOVEL reader axis (explicit-relativizer RC nest), a targeted extension of the argstruct-goal "
    "reader (b9136f131), not a rediscovery. Auditor accepts: the 0.3975 hit is a lexical false-friend, not a cell."
)

ATOM_ID = (
    "math::MM_read_nested_clause_relative_third_reader_v1_SYMBOLIC_explicit_relativizer_RC_parser_CLEAN_CASE_"
    "HARD_PASS_plus83pt_transitive_flat_2of12_0p167_to_nest_12of12_1p0_on_single_annotator_CLEAN_SITE_SELECTED_gold_"
    "plus_4of6_intransitive_recovered_flat_inexpressible_BUT_reader_NEVER_calls_HD_bind_runtime_nest_axis_is_PURE_"
    "SYMBOLIC_relativizer_detect_span_split_reparse_emit_tuples_so_reader_forms_HD_map_is_NOT_true_symbolic_tuples_"
    "NOT_HD_map_bridge_gap_to_additive_map_reasoner_OPEN_HD_depth2_nesting_capacity_confirmed_FREE_but_UNUSED_offline_"
    "FHRR_readout_1p0_on_51_emitted_nestlinks_N2048_is_capacity_check_on_whatever_emitted_NOT_extraction_correctness_"
    "CORPUS_WIDE_PRECISION_LOW_auditor_annotated_all_73_fires_47_pids_approx_29_correct_11_marginal_33_wrong_0p40_"
    "strict_0p55_lenient_vs_cleangold_1p0_failure_classes_PIED_PIPING_object_relative_overt_subject_demonstrative_"
    "that_past_veto_wrong_head_nearest_noun_spurious_object_intransitive_33_wrong_tuples_added_to_foundation_on_RC_"
    "pids_NOT_counted_by_nonrc_regression_REDUCED_RC_and_genuine_2level_embedding_SCOPED_OUT_can_fail_genuine_4of6_"
    "intrans_self_penalty_regression_clean_cert_208of0_byte_identity_off_deixisTrueFalse_79_deixis_541_controls_1p0_"
    "overlay_7of7_nonRC_touched_0_MM_not_CG_single_annotator_clean_selected_gold_low_corpuswide_precision_symbolic_"
    "not_HDmap_fragile_span_heuristic_550455f5f_2026-07-18"
)

ATOM_CLAIM = (
    "MATH MEASURED_MECHANISM (proven-bound). CLAIM: a SYMBOLIC explicit-relativizer relative-clause axis wired into "
    "the McGuffey Third Reader (that/who/which/whom trigger; split matrix vs embedded span at the next finite verb; "
    "re-parse each span with the SAME learned role-assigner; emit embedded + matrix propositions + a ('nest',head,"
    "ev,eobj) link; suppress the object-RC cross-clause mis-attachment) RESOLVES explicit-relativizer non-adjacent-"
    "role embedding on the CLEAN sub-case: transitive-RC attachment flat 2/12 (0.167) -> nest 12/12 (1.0), delta "
    "+83.3pt (HARD-PASS bar >=10pt), plus 4/6 intransitive propositions recovered that the flat reader is "
    "STRUCTURALLY inexpressible on (no intransitive relation type). Additive, default-OFF, byte-identity-preserving. "
    "AUDITOR SCOPE (BANKED MM, NOT CG) with three load-bearing pins: "
    "(1) SYMBOLIC-NOT-HD BRIDGE GAP (confirmed off-code): the runtime nest axis NEVER calls an HD bind()/unbind() "
    "primitive -- bind/unbind/bundle appear ONLY inside the OFFLINE depth2_readout_fidelity measurement. So the win "
    "is a SYMBOLIC RC parser + new emission types, NOT 'the reader forms the HD reasoning-map'. The reader emits "
    "SYMBOLIC nested Python tuples; the reasoner (additive_map) uses HD role-filler binding; these are DIFFERENT "
    "representations that are NOT YET BRIDGED. The unification 'sentences = reasoning-maps' is a HYPOTHESIS with an "
    "OPEN bridge, not a demonstrated identity. HD depth-2 nesting capacity IS confirmed FREE (offline FHRR readout "
    "1.0 on 51 emitted nest-links at N=2048) but is UNUSED by the reader -- the depth-2 readout is a CAPACITY check "
    "on whatever was emitted, NOT an extraction-correctness measure. "
    "(2) CORPUS-WIDE PRECISION IS LOW: the clean gold is single-annotator and CLEAN-SITE-SELECTED (12 clean noun-"
    "headed non-pied-piping sites out of 73 fired). Auditor independently annotated ALL 73 detected RC fires (47 "
    "pids): ~29 clearly correct, ~11 marginal, ~33 wrong => corpus-wide embedded-proposition precision ~0.40 strict "
    "/ ~0.55 lenient, versus 1.0 on the clean gold. Dominant failure classes: PIED-PIPING RCs (head forced as "
    "subject, ~11 fires), object-relatives with an overt embedded subject on who/which (head forced as subject), "
    "demonstrative/complementizer 'that' slipping past the veto (spurious nest), wrong-head nearest-noun selection, "
    "and spurious objects on intransitive RCs. These ~33 wrong tuples are ADDED to the foundation on RC pids and are "
    "NOT captured by nonrc_regression (which only checks NON-RC pids). "
    "(3) REDUCED RC / garden-path (no relativizer) + genuine 2-level embedding are DELIBERATELY SCOPED OUT (Stage-B "
    "learned-disambiguation), flagged honestly by the author. "
    "The +83.3pt is REAL but on the favorable clean-selected denominator; can-fail is genuine (nest self-penalizes "
    "4/6 on intransitive via spurious objects; the metric is NOT construction-locked -- the author caught + rewrote "
    "a circular 100pt version). Regression clean: cert 208/0, byte-identity OFF (deixis True+False, 79 lessons), "
    "deixis 541=541, controls 1.0/1.0, overlay 7/7, nonRC_touched=0."
)

ATOM_RECOMPUTE = (
    "INDEP recompute (.venv Scripts/python, off-disk, NOT verdict_msg; Fix #28): "
    "(A) ANGLE-1 symbolic-not-HD: grep of the cell => bind/unbind/bundle ONLY in depth2_readout_fidelity (offline, "
    "lines ~400-437); detect_rc_sites / nest_axis_passage / extract_passage_nest are pure symbolic (relativizer "
    "detect, span split at next finite verb, re-parse via ORC.assign_roles_learned, emit tuples, suppress). Reader "
    "runtime calls NO HD primitive. CONFIRMED. "
    "(B) ANGLE-3 corpus-wide precision (KEY RISK): ran `--dump-rc` -> 73 explicit-relativizer RC sites over 47 pids "
    "(matches metrics n_rc_sites=73, n_rc_pids=47, n_nest_links=73). Independently annotated each fire for embedded-"
    "proposition subject+verb+obj correctness: ~29 clearly correct (e.g. men/hunt/animals, boys/called/henry, "
    "clock/kept/time, fisher/draws/net, plume/decked/head), ~11 marginal (fact-correct-but-clause-mislabeled or PP-"
    "obj debatable), ~33 wrong. Precision ~0.40 strict / ~0.55 lenient vs clean-gold 12/12=1.0. Failure classes "
    "enumerated (pied-piping ~11, object-rel overt-subject, demonstrative/complementizer that, wrong-head, spurious "
    "intransitive obj). "
    "(C) run_certification.py -> 208 PASSED / 0 FAILED (fleet green; cell touches no certified module). "
    "(D) metrics.json cross-checks reproduce: transitive flat 2/12 0.1667, nest 12/12 1.0, delta 83.33pt; "
    "intransitive_recovered 4/6; depth2_cleanup_acc 1.0 on 51 nest-links N=2048; nonrc_regression n_touched=0 (32 "
    "non-RC pids); deixis_unchanged 541=541; byte_identity_off deixis_true+deixis_false True over 79; role_controls "
    "passive 1.0 reversal 1.0; overlay 7/7. "
    "(E) byte-identity OFF is structurally airtight: extract_passage_nest(nest=False) LITERALLY delegates to "
    "R.extract_passage_argrole(argrole=True) and returns before the nest pass. "
    "(F) can-fail genuine: the 2/6 intransitive misses (brook/springs->spurious 'rock' obj, flower/blows->spurious "
    "'loveliness' obj) are real self-penalties under the exact-match metric; nest FAILS its own errors."
)

ATOM_SCOPE = (
    "McGuffey Third Reader (PG#14766, PD), 79 lessons, glass-box POS + averaged-perceptron role-assigner + WordNet "
    "grounding + a transparent relativizer/span layer; NO LLM; torch used ONLY for the offline HD readout. "
    "Load-bearing BOUNDS: "
    "(a) SYMBOLIC-NOT-HD: runtime is a symbolic RC parser; HD bind() is UNUSED at runtime; the depth-2 HD readout is "
    "an offline capacity check. 'Reader forms the HD map' is NOT demonstrated -- symbolic tuples != HD map; the "
    "bridge to the additive_map reasoner is OPEN. "
    "(b) CLEAN-CASE ONLY: the +83.3pt is on a single-annotator, clean-SITE-SELECTED gold (12 clean noun-headed non-"
    "pied-piping transitive sites). Corpus-wide precision on all 73 fires is ~0.40 strict / ~0.55 lenient. "
    "(c) FRAGILE SPAN HEURISTIC: RC ends at the next finite verb; head = nearest preceding noun. Breaks on pied-"
    "piping ('with/through/on which ... V'), object-relatives with an overt embedded subject on who/which, "
    "demonstrative/complementizer 'that' the veto misses, and produces spurious objects on intransitive RCs. "
    "(d) UNCAPTURED FOUNDATION COST: ~33 wrong nested tuples are added on RC pids; nonrc_regression only guards NON-"
    "RC pids, and the mis-attach suppression can drop correct matrix relations on object-RC pids (unmeasured). "
    "(e) REDUCED RC + genuine 2-level embedding SCOPED OUT (Stage-B). "
    "BRAIN-CHECK: hierarchical composition via Merge / online constituent-tracking (Ding et al. 2016) / the "
    "temporal-retrieval + BA44-unification division of labor (Friederici) maps onto reuse-the-role-assigner-per-"
    "span; the human center-embedding depth limit ~2-3 (Miller-Chomsky) matches the Plate-1995 bounded-depth HD "
    "ceiling (D1 0.33-0.62 -> D2 0.13-0.20) -- so the depth-2 degradation is a brain-faithful REAL bound, NOT a "
    "crosstalk bug to fix. The extraction machinery here is a CURATED closed-class scaffold (pivot authorizes any "
    "tool for the FOUNDATION; runtime stays glass-box), NOT a learned clause segmenter. "
    "REVIVAL to CG: (1) BRIDGE the symbolic tuples to the HD additive_map reasoner (encode the emitted nested "
    "propositions as the reasoner's actual runtime representation and show reasoning over them), turning the offline "
    "capacity check into a live runtime path -- this is the real 'reader forms the map' test; (2) raise corpus-wide "
    "precision (handle pied-piping + object-relatives with overt subjects + tighter that/demonstrative veto + "
    "better head selection) so the clean-case win generalizes past the selected gold; (3) a LEARNED clause "
    "segmenter replacing the closed-class scaffold; (4) reduced-RC / garden-path (Stage-B learned disambiguation)."
)

ATOM_METRICS = {
    "transitive_attach_flat": "2/12 (0.1667)",
    "transitive_attach_nest": "12/12 (1.0)",
    "attach_delta_points": 83.33,
    "intransitive_recovered": "4/6 (flat structurally inexpressible)",
    "depth2_readout_acc": 1.0, "depth2_n_sites_tested": 51, "depth2_n_dim": 2048,
    "depth2_note": "OFFLINE FHRR capacity check on emitted structures; NOT extraction-correctness; runtime uses NO HD bind",
    "n_rc_sites_fired": 73, "n_rc_pids": 47,
    "corpus_wide_precision_strict": "~0.40 (~29/73 clearly correct)",
    "corpus_wide_precision_lenient": "~0.55 (~40/73 incl marginal)",
    "corpus_wide_wrong_estimate": "~33/73",
    "failure_classes": ["pied_piping_head_forced_as_subject_~11", "object_relative_overt_embedded_subject_who_which",
                        "demonstrative_or_complementizer_that_past_veto", "wrong_head_nearest_noun_selection",
                        "spurious_object_on_intransitive_RC_blows_loveliness_springs_rock_frown_way"],
    "uncaptured_foundation_cost": "~33_wrong_tuples_added_on_RC_pids_nonrc_regression_only_guards_non_RC_pids",
    "nonrc_touched": 0, "nonrc_pids": 32,
    "byte_identity_off": "True deixis_true+deixis_false over 79 lessons (nest=False LITERALLY R.extract_passage_argrole)",
    "deixis_unchanged": "541=541", "role_controls": "passive 1.0 / reversal 1.0", "overlay_witness": "7/7",
    "certification": "208 PASSED / 0 FAILED (independently re-run)",
    "can_fail_genuine": "nest self-penalizes 4/6 intransitive via spurious objects; metric not construction-locked (author rewrote a circular 100pt version)",
    "symbolic_not_HD": "bind/unbind/bundle ONLY in offline depth2_readout_fidelity; runtime nest axis is pure symbolic",
    "gold": "single-annotator, clean-SITE-SELECTED (12 clean transitive + 6 intransitive of 73 fires)",
    "depth_ceiling": "D1 0.33-0.62 -> D2 0.13-0.20 (STEP-0 probe, Plate-1995 bounded-depth, human center-embedding ~2-3; brain-faithful, not re-run in this VET)",
    "cell_verdict": "NEST_RESOLVES_EMBEDDING (HARD-PASS)",
    "auditor_tier": "MEASURED_MECHANISM (proven-bound; clean-case symbolic-RC pass real, bounded by symbolic-not-HD bridge gap + corpus-wide precision ~0.40-0.55 + scoped-out reduced-RC)",
}

COMPOSES = [
    "EXTENDS the reader arc from math atom for read_argstruct_goal_role_third_reader_v1 (commit b9136f131): this is "
    "the fourth reader, adding the explicit-relativizer RC nest axis. nest=False is BYTE-IDENTICAL to the argstruct-"
    "goal reader (both deixis settings, 79 lessons) -> a clean additive, default-OFF extension.",
    "IS BOUNDED BY math::HARD_FAIL_read_grow_reread_compounding_kgguided_v1 (ddfd17f34, HF; and its MM re-analysis): "
    "that HF proved hand-rule extraction hits a ~0.44 wall on open real prose. This cell's corpus-wide precision "
    "~0.40-0.55 on the full 73 RC fires is CONSISTENT with / inside that wall -- the clean-case +83pt exists because "
    "the gold is clean-site-selected, NOT because the hand-rule RC parser generalizes. The two cohere.",
    "REGIME-composes with math atom for base_reader_grounded_relations_coref_v1 (ae23c4b42, MM, first reader-arc "
    "positive scoped): same pattern -- a real positive on a clean/selected sub-case that is a CONSTRUCTION/SCAFFOLD "
    "proof, not a generalized capability. The auditor scopes both as MM inside the hand-rule extraction wall.",
    "REFRAMES the 'sentences = reasoning-maps' unification: this cell is STEP-1 (reader emits nested SYMBOLIC "
    "structure) but does NOT close it -- the reader's symbolic tuples are NOT the reasoner's HD additive_map "
    "representation. The bridge (encode emitted nested propositions as the HD reasoner's runtime map) is the OPEN "
    "load-bearing next step; the offline depth-2 FHRR readout only confirms the HD capacity is free.",
    "credit: McGuffey Third Reader (PD); Plate-1995 (bounded-depth HD capacity); Chomsky Merge / Ding et al. 2016 "
    "(online constituent tracking) / Friederici (temporal + BA44 division of labor) for the brain-faithfulness "
    "framing; the closed-class relativizer scaffold + span heuristic + gold are original to this cell. Author "
    "CREDITED for catching + rewriting a circular 100pt metric and self-flagging the symbolic caveat + explicit-"
    "relativizer scope + corpus-wide-precision-lower.",
]

OVER_READS = [
    "The chain framing 'reader forms the HD reasoning-map (step-1)' OVER-READS. Confirmed off-code: the runtime nest "
    "axis is PURE SYMBOLIC and never calls an HD bind() primitive; the reader emits symbolic Python tuples, not an "
    "HD map. The depth-2 HD readout is an OFFLINE capacity check. The honest framing: a SYMBOLIC RC parser resolves "
    "clean-case embedding, and HD depth-2 nesting capacity is separately confirmed FREE but UNUSED. The bridge from "
    "symbolic tuples to the additive_map HD reasoner is OPEN -- the unification is a hypothesis, not demonstrated.",
    "The headline +83.3pt is a CLEAN-CASE number on a single-annotator, clean-SITE-SELECTED gold (12 of 73 fires). "
    "It is REAL for that sub-case but does NOT generalize: independent annotation of all 73 fires gives corpus-wide "
    "precision ~0.40 strict / ~0.55 lenient. Report the +83pt strictly scoped to explicit-relativizer noun-headed "
    "non-pied-piping RCs, with the ~0.40-0.55 corpus-wide number as the load-bearing general figure.",
    "nonrc_regression n_touched=0 does NOT mean the nest axis is clean on RC content. It only guards NON-RC pids. "
    "On RC pids the axis ADDS ~33 wrong nested tuples to the foundation and its object-RC mis-attach suppression can "
    "drop correct matrix relations (unmeasured). The zero-regression guard is real but narrow.",
    "depth2_readout=1.0 is NOT evidence of extraction correctness. It encodes/decodes WHATEVER tuples were emitted "
    "(including the ~33 wrong ones) and confirms only the HD FHRR depth-2 capacity property. Correctly a capacity "
    "check, not a comprehension score.",
]

REVIVAL = [
    "BRIDGE the symbolic nested tuples to the HD additive_map reasoner: encode the emitted nested propositions as "
    "the reasoner's actual runtime representation and demonstrate reasoning over them. This turns the offline "
    "capacity check into a live runtime path and is the real test of 'the reader forms the HD map' -- the decisive "
    "CG gate for the sentences=reasoning-maps unification.",
    "Raise corpus-wide precision from ~0.40-0.55 toward the clean-case: handle pied-piping RCs (head is the object "
    "of a preposition, not the embedded subject), object-relatives with overt embedded subjects on who/which, a "
    "tighter demonstrative/complementizer 'that' veto, and better head selection -- so the clean-case win "
    "generalizes past the hand-selected gold.",
    "Replace the closed-class relativizer + span heuristic with a LEARNED clause segmenter (foundation-tool "
    "authorized), and re-measure corpus-wide precision on held-out lessons.",
    "Extend to reduced-RC / garden-path (no relativizer) via Stage-B learned disambiguation; and independently "
    "re-run the depth-margin probe (D1->D2 shrink) to confirm the brain-faithful bounded-depth ceiling on-data.",
]

GENUINE_POS = (
    "GENUINE kernel preserved symmetrically (NOT dismissed): on the clean explicit-relativizer sub-case the symbolic "
    "RC axis genuinely resolves non-adjacent-role embedding (+83.3pt, flat 2/12 -> nest 12/12) and recovers 4/6 "
    "intransitive matrix predications the flat reader is structurally inexpressible on -- a real, can-fail "
    "(self-penalizing 4/6 intransitive), regression-clean (cert 208/0, byte-identity, deixis, controls, overlay all "
    "green) component. The HD depth-2 FHRR capacity is independently confirmed FREE (readout 1.0 on 51 emitted nest-"
    "links). And the auditor CREDITS the author's honesty: caught + rewrote a circular 100pt metric, and self-"
    "flagged the symbolic-not-HD caveat, the explicit-relativizer scope, and that corpus-wide precision is lower "
    "than the clean gold. The auditor's scoping SHARPENS (pins the symbolic bridge gap + the measured ~0.40-0.55 "
    "corpus-wide number), it does not overturn the author's stated bounds. This IS a real step-1 component; what it "
    "is NOT (yet) is the HD-map unification or a generalized RC parser."
)


def build_atom():
    return {
        "id": ATOM_ID, "name": ATOM_CLAIM, "corpus": "math", "tier": "MEASURED_MECHANISM",
        "kind": "experiment_landed_vet",
        "cert_status": "proven_bound",
        "cert_class": ("symbolic_explicit_relativizer_RC_parser_clean_case_HARD_PASS_plus83pt_transitive_12of12_on_"
                       "clean_site_selected_gold_plus_4of6_intransitive_but_reader_NEVER_calls_HD_bind_symbolic_"
                       "tuples_NOT_HD_map_bridge_gap_open_HD_depth2_capacity_free_but_unused_corpus_wide_precision_"
                       "0p40_strict_0p55_lenient_on_all_73_fires_pied_piping_object_relative_demonstrative_that_"
                       "wrong_head_spurious_object_failure_classes_reduced_RC_scoped_out_can_fail_genuine_regression_"
                       "clean_cert_208of0_inside_0p44_hand_rule_extraction_wall"),
        "description": (ATOM_CLAIM + "\n\nRECOMPUTE (off-disk .venv, Fix #28): " + ATOM_RECOMPUTE
                        + "\n\nHONEST SCOPE: " + ATOM_SCOPE),
        "aliases": [
            "nested relative-clause reader v1",
            "symbolic RC parser clean-case +83pt HD-nesting-free-but-unused",
            "reader emits symbolic nested tuples NOT HD map bridge gap open",
            "corpus-wide RC precision ~0.40-0.55 vs clean-gold 1.0",
            "explicit-relativizer RC HARD-PASS reduced-RC scoped out",
        ],
        "ts_iso": _iso, "ts": _ts,
        "metadata": {
            "provenance_quality": ("independent_venv_offdisk_recompute_dump_rc_annotated_all_73_fires_plus_grep_"
                                   "confirms_bind_only_in_offline_readout_plus_cert_208of0_rerun_plus_metrics_"
                                   "cross_checks_reproduce"),
            "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes": None,
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_read_nested_clause_relative_third_reader_v1/metrics.json",
            "verified_off_data": ATOM_RECOMPUTE, "honest_scope": ATOM_SCOPE, "metrics": ATOM_METRICS,
            "over_reads_corrected": OVER_READS,
            "genuine_positives_symmetric_anti_negativity": GENUINE_POS,
            "revival_criteria": REVIVAL,
            "cross_arc_overlap_check": XARC,
            "symbolic_not_HD_confirmed": True,
            "bridge_gap_open": "reader emits symbolic nested tuples; additive_map reasoner uses HD binding; not yet one representation",
            "corpus_wide_precision": "~0.40 strict / ~0.55 lenient (auditor annotated all 73 fires / 47 pids)",
            "cites": [
                "Fix_28_verify_off_data_not_verdict_msg",
                "symmetric_anti_negativity_verify_both_directions_USER",
                "cited_number_must_reproduce_from_cell",
                "verify_the_referent_atom_ids_mechanism_metric_regime",
                "synthetic_toy_corpus_outcomes_can_be_construction_determined_real_questions_need_real_data",
                "construction_proof_not_capability_win_could_it_fail_informatively",
                "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
                "every_negative_and_positive_brain_check_mechanism_vs_shortcut",
                "substrate_kb_concept_overlap_check_on_schema_vet",
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
        "supersedes_atom_id": None, "amends_atom_id": None,
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True,
        "auditor": "hdi_skunkworks", "atomized_by": ATOMIZED_BY,
        "verdict": ("MEASURED_MECHANISM_proven_bound_symbolic_explicit_relativizer_RC_parser_clean_case_HARD_PASS_"
                    "plus83pt_but_reader_never_calls_HD_bind_symbolic_tuples_not_HD_map_bridge_gap_open_HD_depth2_"
                    "capacity_free_but_unused_corpus_wide_precision_0p40_strict_0p55_lenient_on_all_73_fires_reduced_"
                    "RC_scoped_out_can_fail_genuine_regression_clean_cert_208of0"),
        "cert_increment_delta": 1,
        "decision": (
            "MM (proven-bound). Cell verdict NEST_RESOLVES_EMBEDDING (HARD-PASS) CONFIRMED on the clean sub-case but "
            "BANKED MM, not CG, with pinned scope. Off-disk recompute (.venv, Fix #28): (1) grep confirms the "
            "runtime nest axis is PURE SYMBOLIC -- bind/unbind/bundle appear ONLY in the offline depth2 readout; the "
            "reader emits symbolic nested tuples, NOT an HD map, so 'reader forms the HD reasoning-map' is NOT true "
            "and the bridge to the additive_map reasoner is OPEN. (2) Independent annotation of ALL 73 RC fires (47 "
            "pids) gives corpus-wide precision ~0.40 strict / ~0.55 lenient (vs clean-gold 12/12=1.0); the gold is "
            "single-annotator, clean-site-selected. Failure classes: pied-piping, object-relatives with overt "
            "subjects, demonstrative/complementizer 'that' past the veto, wrong-head, spurious intransitive objects; "
            "~33 wrong tuples added on RC pids (uncaptured by nonrc_regression). (3) Reduced-RC + genuine 2-level "
            "embedding scoped out. Regression clean: cert 208/0 (re-run), byte-identity OFF deixis True+False over "
            "79, deixis 541=541, controls 1.0/1.0, overlay 7/7, nonRC_touched=0. Can-fail genuine (nest self-"
            "penalizes 4/6 intransitive; author rewrote a circular 100pt metric). HD depth-2 capacity confirmed FREE "
            "(readout 1.0 on 51 nest-links) but UNUSED. Counts toward CERT as a scoped clean-case positive / "
            "proven-bound. Local-only; needs orchestrator store sync."),
        "framing_correction_vs_director": (
            "Director framed this as HARD-PASS +83.3pt (CLAIM-VET-pending) with a load-bearing HONESTY caveat that "
            "the win is SYMBOLIC parsing, not the reader using HD binding, and asked to VERIFY the symbolic caveat + "
            "the corpus-wide precision (the key risk). RESULT (symmetric): the clean-case HARD-PASS is CONFIRMED and "
            "the caveat is CONFIRMED off-code (bind() only in the offline readout; runtime is pure symbolic). I BANK "
            "MM (proven-bound), scoped to: symbolic explicit-relativizer RC parser, clean-case +83pt on a single-"
            "annotator clean-site-selected gold, HD depth-2 nesting capacity confirmed FREE but UNUSED by the reader, "
            "corpus-wide precision ~0.40 strict / ~0.55 lenient (I annotated all 73 fires -- the key risk is REAL: "
            "clean-gold pass while corpus-wide precision is low), reduced-RC scoped out. The 'reader forms the HD "
            "map' unification is a HYPOTHESIS with an OPEN bridge: the reader emits SYMBOLIC tuples, the additive_map "
            "reasoner uses HD binding, they are NOT yet one representation -- do NOT let step-1 read as the "
            "unification closed. The genuine positive (clean-case win + free HD capacity + honest bridge-gap "
            "identification) is preserved. Author CREDITED for catching + rewriting a circular 100pt metric and "
            "self-flagging the symbolic caveat, explicit-relativizer scope, and corpus-wide-precision-lower."),
        "cross_arc_overlap_check": XARC,
        "net_cert_delta": ("+1 MM (scoped clean-case reader component: symbolic explicit-relativizer RC parser "
                           "resolves clean-case embedding +83pt; HD depth-2 nesting capacity confirmed free but "
                           "UNUSED by the reader; bounded by the symbolic-not-HD bridge gap, corpus-wide precision "
                           "~0.40-0.55, and scoped-out reduced-RC. The symbolic->HD bridge + precision generalization "
                           "are the CG revival gates)."),
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
    print("=== A5 atom-write: read_nested_clause_relative_third_reader_v1 -> MM (symbolic RC clean-case pass; corpus-wide precision bound) (2026-07-18) ===")
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
