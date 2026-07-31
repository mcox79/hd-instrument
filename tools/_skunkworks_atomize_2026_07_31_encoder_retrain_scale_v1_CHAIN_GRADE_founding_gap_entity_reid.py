"""A5-gated LOCAL-ONLY atomize: CHAIN_GRADE (CERT +1) for situation_model_assembly_encoder_retrain_scale_v1.

FINAL-LOCK VET of the biggest claim of the arc: a CLEAN_PASS certified founding-gap break. This is the
confirmatory re-run of the corrected-guard scale cell. Underlying d1 numbers (s7/s13) were already bit-exact
reproduced by the prior audit (a78ff08); this audit locks the CONFIRMATORY re-run's integrity because the
corrected collapse guard was authored by the same exp_dev that ran it.

INDEPENDENT RECOMPUTE (this audit, off-disk, ignoring stored guard flags -- reproduced all 7 conditions):
 - PRE-REG INTEGRITY: guard prereg + guard/verdict CODE both committed eae0a3867 @ 2026-07-31T04:48:42-04:00
   ("pre-run"); metrics.json appears ONLY in the later 565f28009 @ 05:24:54-04:00. metrics ts_iso 09:23:53Z =
   05:23:53 EDT, elapsed_s 793 => run started ~05:10 EDT = 22 min AFTER the guard commit. metrics mtime
   05:23:54 matches ts_iso; working tree clean. The verdict-computing code was frozen in git 22 min before any
   number existed -> guard could NOT have been retrofitted to observed numbers. Ordering independently confirmed.
 - GUARD FAIRNESS: FAIR, not a rubber stamp. C1 (tuned>=frozen) is an anti-COLLAPSE disambiguator, NOT the
   performance bar; the performance gate is type_ok = ALL 3 query types >= 0.60 loop, well above the frozen wall
   (frozen types 0.42-0.60, frozen loop 0.47-0.52). A barely-better encoder fails type_ok. C3/C4 (entcons,
   q_agree) are individually foolable by a degenerate encoder (d6 saturates both to 1.000) -- prereg states this
   and anchors the guard to loop (C1) + frozen-referenced drift cap (C2), which d6 fails on BOTH.
 - d6 MUST-FAIL CONTROL: d6_div40_s7 guard FAILS on C1 (tuned 0.292 < frozen 0.470) AND C2 (wc_drift +0.354 >
   0.15) -- doubly robust anti-rubber-stamp proof, reproduced off-disk.
 - CLEAN_PASS reproduces: all 6 d1 conditions pass type_ok + guard(C1-C4) + mem(gap<=0.15) + oracle(tuned<=
   tuned_oracle+0.02); both configs (d1_div40, d1_div80) clean-pass across 3 seeds each. New seed s19 lands
   in-family (d1_div40_s19 tuned 0.765, d1_div80_s19 tuned 0.772). My recompute matched every stored flag 7/7.
 - NO exceeds-oracle: tuned_loop < tuned_oracle on EVERY arm (diffs -0.020..-0.054). The prior "0.830>0.730" red
   flag was the frozen-arm-oracle mislabel; the tuned-oracle (0.854 for the standout) is the correct ceiling.
 - Floors ALL collapse (random_addr/no_coref-b/wrongrole/shuffled/most_recent under bars; pooled b/c << 0.80).
 - mem_gap <= +0.103 all conditions, several negative (held >= train) -> no memorization.

HONEST FRAMING (required correction, RIDES the atom): the claim is "minimal-unfreeze (top-1 layer, 3.15M params)
fine-tune of the substrate's OWN v2 encoder with the validated cross-mention-consistency + inter-entity-push +
VICReg objective lifts HELD-OUT situation-model loop 0.52->0.83 via cross-frame ENTITY re-identification" --
NOT "breaks the 0.31 wall" (that 0.31 was the bolt-on-WM learned-key harness = a DIFFERENT addressing scheme;
the frozen entity-re-id baseline HERE is loop 0.47-0.52 / entcons 0.813 / q_agree 0.73).

SCOPE (does not drop): (a) SYNTHETIC situation-model harness (colors-as-entities, templated passages) --
naturalistic generalization UNTESTED; (b) addresses the DOMINANT (entity re-id) half of the founding wall; the
ROLE/filler-attribution half is a SEPARATE untested track; (c) win = CHEAP minimal-unfreeze (top-1; deeper
unfreeze OVERFITS/craters = d6); (d) 3 seeds x 2 diversity levels, generalizes to held-out entities, distinct-
not-collapsed (loop-anchored guard, d6 fails control), tuned_loop < tuned-oracle, floors collapse, no
memorization; (e) triple-VET'd (a78ff08 recompute + this final lock + the pre-registered corrected guard).
"""
import json, os, time, tempfile, datetime, hashlib

ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"
REGISTRY = "data/capability_registry.jsonl"

def iseq(o):
    try: return int(o.get("seq"))
    except: return -1

# ---- PRE-GATE: load + validate ----
atom_lines = [l for l in open(ATOMS, encoding="utf-8").read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]
existing_ids = {o.get("atom_id") for o in parsed if o.get("atom_id")}
assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR -- investigate"
ledger_lines = [l for l in open(LEDGER, encoding="utf-8").read().splitlines() if l.strip()]
lp = [json.loads(l) for l in ledger_lines]
reg_lines = [l for l in open(REGISTRY, encoding="utf-8").read().splitlines() if l.strip()]
[json.loads(l) for l in reg_lines]  # validate registry loads

STORE_HEAD = max(max(iseq(o) for o in parsed), max(iseq(o) for o in lp))
meta_atoms = [json.loads(l) for l in open("data/substrate_index/meta/atoms.jsonl", encoding="utf-8").read().splitlines() if l.strip()]
STORE_HEAD = max(STORE_HEAD, max(iseq(o) for o in meta_atoms))
assert STORE_HEAD == 29592, f"expected store head 29592, got {STORE_HEAD}"
NEW_SEQ = 29593
# parent = the assembly loop (29592), whose naturalistic wall was localized to the encoder; this breaks the
# dominant entity-re-id half of that wall via encoder retrain.
parent = [o for o in parsed if iseq(o) == 29592]
assert parent and "binding_wm_coref" in parent[0].get("anchor_name", ""), "parent 29592 not the assembly-loop atom"
assert not any("encoder_retrain_scale" in o.get("anchor_name", "") for o in parsed), "anchor already atomized"
print(f"PRE-GATE: {len(atom_lines)} atoms load-valid; store head {STORE_HEAD}; NEW_SEQ {NEW_SEQ}; parent 29592 present.")

# ---- OFF-DISK verification of the metrics (independent recompute of gates) ----
M = json.load(open("data/exp_situation_model_assembly_encoder_retrain_scale_v1/metrics.json", encoding="utf-8"))
assert M["verdict"] == "CLEAN_PASS" and M["run_mode"] == "grid"
QT = ("a_name_maintenance", "b_competitive_coref", "c_overwrite")
LOOP, MEMGAP, WCDRIFT, ENTCONS, QAG, OTOL = 0.60, 0.15, 0.15, 0.85, 0.60, 0.02
DECODE_FLOOR, ADDR_FLOOR, PROVEN = 0.20, 0.287, 0.80
def guard(r):
    c1 = r["tuned_loop_mean"] >= r["frozen_loop_mean"]
    wcd = r["wc_held"] - r["wc_frozen"]; c2 = wcd <= WCDRIFT
    c3 = r["tuned_ent_consistency"] >= ENTCONS; c4 = r["tuned_q_agree"] >= QAG
    return c1, c2, c3, c4, wcd, (c1 and c2 and c3 and c4)
clean_cfgs = {}
for r in M["per_condition"]:
    to = all(r["tuned_type"][q] >= LOOP for q in QT)
    c1, c2, c3, c4, wcd, gp = guard(r)
    mem = (r["train_loop_mean"] - r["tuned_loop_mean"]) <= MEMGAP
    ora = r["tuned_loop_mean"] <= r["oracle_tuned_loop_mean"] + OTOL
    p = to and gp and mem and ora
    assert p == M["bands"]["per_condition_clean_pass"][r["name"]]["pass"], f"recompute mismatch {r['name']}"
    clean_cfgs.setdefault("d%d_div%d" % (r["depth"], r["nctx"]), []).append(p)
    # every arm below the tuned-oracle
    assert r["tuned_loop_mean"] <= r["oracle_tuned_loop_mean"] + OTOL, f"exceeds-oracle {r['name']}"
# d6 doubly fails
d6 = [r for r in M["per_condition"] if r["depth"] == 6][0]
c1, c2, c3, c4, wcd, gp = guard(d6)
assert (not gp) and (not c1) and (not c2), "d6 must fail C1 AND C2"
assert abs(d6["tuned_loop_mean"] - 0.2915789473684211) < 1e-9 and abs(d6["frozen_loop_mean"] - 0.47035087719298246) < 1e-9
# both d1 configs clean-pass across 3 seeds
assert clean_cfgs["d1_div40"] == [True, True, True] and clean_cfgs["d1_div80"] == [True, True, True]
assert clean_cfgs["d6_div40"] == [False]
# floors collapse
for r in M["per_condition"]:
    for arm, (qts, bar) in {"random_addr": (QT, ADDR_FLOOR), "no_coref": (("b_competitive_coref",), ADDR_FLOOR),
                            "wrongrole": (QT, DECODE_FLOOR), "shuffled": (QT, DECODE_FLOOR)}.items():
        for q in qts:
            assert r["floors"][arm][q] <= bar, f"floor {r['name']} {arm} {q}"
    for q in QT:
        assert r["most_recent"][q] <= DECODE_FLOOR
    assert r["pooled_b"] < PROVEN and r["pooled_c"] < PROVEN
best = M["bands"]["best_condition"]; best_loop = M["bands"]["best_tuned_loop_mean"]
assert best == "d1_div80_s13" and abs(best_loop - 0.829820788530466) < 1e-9
print("OFF-DISK OK: 7/7 recompute matches stored; both d1 configs clean-pass 3 seeds; d6 fails C1+C2; "
      "no exceeds-oracle; floors collapse; best d1_div80_s13 tuned 0.830.")

cell_sha16 = hashlib.sha256(open("experiments/exp_situation_model_assembly_encoder_retrain_scale_v1.py", "rb").read()).hexdigest()[:16]
prereg_sha16 = hashlib.sha256(open("preregs/2026-07-31_encoder_retrain_scale_corrected_guard.md", "rb").read()).hexdigest()[:16]
metrics_sha16 = hashlib.sha256(open("data/exp_situation_model_assembly_encoder_retrain_scale_v1/metrics.json", "rb").read()).hexdigest()[:16]
assert cell_sha16 == "d28019195b91cfa6" and prereg_sha16 == "0f6c6091d2ea1497" and metrics_sha16 == "4471d44ebf53c14a"

ts = time.time(); ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat(); ts_day = "2026-07-31"

AID = ("math::situation_model_assembly_encoder_retrain_scale_v1_CHAIN_GRADE_FOUNDING_GAP_ENTITY_REID_BREAK_"
    "minimal_unfreeze_top1_layer_3p15M_params_fine_tune_of_substrate_OWN_v2_encoder_with_validated_cross_"
    "mention_consistency_plus_inter_entity_push_plus_VICReg_objective_lifts_HELD_OUT_situation_model_loop_"
    "0p52_to_0p83_via_cross_frame_ENTITY_re_identification_NOT_breaks_0p31_wall_that_was_bolt_on_WM_learned_"
    "key_DIFFERENT_addressing_scheme_frozen_entity_reid_baseline_HERE_is_loop_0p47_0p52_entcons_0p813_q_agree_"
    "0p73_SYNTHETIC_harness_colors_as_entities_templated_passages_naturalistic_UNTESTED_addresses_DOMINANT_"
    "entity_reid_HALF_role_filler_attribution_half_SEPARATE_untested_track_win_is_CHEAP_minimal_unfreeze_top1_"
    "deeper_unfreeze_OVERFITS_craters_d6_full_unfreeze_tuned_0p292_below_frozen_0p470_3seeds_x_2diversity_"
    "generalizes_heldout_entities_distinct_not_collapsed_loop_anchored_guard_d6_fails_control_C1_and_C2_"
    "tuned_loop_below_tuned_oracle_no_exceeds_oracle_floors_collapse_no_memorization_gap_below_0p103_"
    "PREREG_corrected_guard_committed_eae0a3867_22min_BEFORE_run_triple_VET_a78ff08_plus_this_lock_CERT_"
    "plus1_LOCAL_ONLY_2026_07_31")
assert AID not in existing_ids, "duplicate atom id"

HEADLINE = ("CHAIN_GRADE (CERT +1) founding-gap break. Minimal-unfreeze (top-1 encoder layer, 3.15M trainable "
    "params) fine-tune of the substrate's OWN v2 encoder with the validated cross-mention-consistency + inter-"
    "entity-push + VICReg objective lifts HELD-OUT situation-model loop 0.52 -> 0.83 via cross-frame ENTITY re-"
    "identification. Two configs (d1_div40, d1_div80) CLEAN_PASS across 3 seeds each: all 3 query types >= 0.60 "
    "loop, corrected loop-anchored collapse guard HOLDS (C1 tuned_loop>=frozen, C2 wc_drift<=0.15, C3 entcons>="
    "0.85, C4 q_agree>=0.60), memorization gap closed (<=+0.103, several negative), tuned_loop < TUNED-oracle "
    "every arm (no exceeds-oracle), all 6 can-fail floors collapse. HONEST FRAMING (NOT 'breaks the 0.31 wall'): "
    "that 0.31 was the bolt-on-WM learned-key harness = a DIFFERENT addressing scheme; the frozen entity-re-id "
    "baseline HERE is loop 0.47-0.52 / entcons 0.813 / q_agree 0.73, and THAT is what the retrain breaks. SCOPE: "
    "(a) SYNTHETIC harness (colors-as-entities, templated passages) -- naturalistic generalization UNTESTED; (b) "
    "addresses the DOMINANT entity-re-id half of the founding wall; the ROLE/filler-attribution half is a SEPARATE "
    "untested track; (c) win = CHEAP minimal-unfreeze (top-1; deeper unfreeze OVERFITS and CRATERS -- d6 full-"
    "unfreeze tuned_loop 0.292 < frozen 0.470, fails the guard on BOTH C1 and C2 = anti-rubber-stamp control). "
    "PRE-REG INTEGRITY: the corrected collapse guard + verdict CODE were committed (eae0a3867) 22 min BEFORE the "
    "results run (565f28009); the verdict-computing code was frozen in git before any number existed, so the guard "
    "could not be retrofitted to observed numbers -- independently confirmed via git timestamps + metrics ts_iso/"
    "mtime. GUARD FAIRNESS: C1 is an anti-collapse disambiguator (not the performance bar; the 0.60-per-type loop "
    "is the performance gate, well above the frozen wall); C3/C4 are individually foolable by a degenerate encoder "
    "(d6 saturates entcons=q_agree=1.000) which is exactly why the guard is loop-anchored (C1) + drift-capped (C2) "
    "-- d6 fails both. Triple-VET'd: prior recompute (a78ff08) bit-exact-reproduced s7/s13, this final lock "
    "independently recomputed all 7 conditions (new seed s19 lands in-family), + the pre-registered corrected "
    "guard. WIRE candidate; deploy/scale PENDING USER steer + naturalistic validation. CERT +1 LOCAL-ONLY.")

key_metrics = {
    "cell_verdict": "CLEAN_PASS", "auditor_tier": "CHAIN_GRADE_founding_gap_entity_reid_break", "cert_delta": 1,
    "claim": ("minimal-unfreeze top-1 layer (3.15M params) fine-tune of substrate's own v2 encoder with validated "
        "cross-mention-consistency+inter-entity-push+VICReg objective lifts held-out situation-model loop "
        "0.52->0.83 via cross-frame ENTITY re-identification"),
    "NOT_claim": ("breaks the 0.31 wall -- that 0.31 was the bolt-on-WM learned-key harness, a DIFFERENT addressing "
        "scheme; frozen entity-re-id baseline HERE = loop 0.47-0.52 / entcons 0.813 / q_agree 0.73"),
    "frozen_baseline_loop": "0.470-0.525", "frozen_entcons": 0.813, "frozen_q_agree": 0.739,
    "best_condition": "d1_div80_s13", "best_tuned_loop_mean": 0.8298,
    "clean_pass_configs": ["d1_div40", "d1_div80"], "seeds": [7, 13, 19], "diversity_levels_nctx": [40, 80],
    "n_trainable_params": 3153408, "unfreeze_depth_top1": True,
    "d1_div40_tuned_loop_by_seed": [0.7147, 0.7991, 0.7647], "d1_div80_tuned_loop_by_seed": [0.7423, 0.8298, 0.7716],
    "d1_div40_config_mean": 0.7595, "d1_div80_config_mean": 0.7813,
    "all_3_query_types_ge_0p60_all_seeds": True,
    "corrected_collapse_guard_C1_loop_ge_frozen": True, "C2_wc_drift_le_0p15": True,
    "C3_entcons_ge_0p85_tuned_0p94_0p98": True, "C4_q_agree_ge_0p60_tuned_0p99_1p00": True,
    "guard_is_loop_anchored_not_rubber_stamp": True,
    "C1_is_anti_collapse_disambiguator_not_performance_bar_which_is_0p60_per_type": True,
    "d6_must_fail_control_full_unfreeze": {"tuned_loop": 0.2916, "frozen_loop": 0.4704, "wc_drift": 0.3538,
        "C1_fail": True, "C2_fail": True, "guard_pass": False, "doubly_robust": True,
        "note": "d6 saturates entcons=1.000 q_agree=1.000 (C3/C4 foolable) yet FAILS on loop C1 + drift C2"},
    "no_exceeds_oracle_every_arm_tuned_lt_tuned_oracle": True,
    "tuned_oracle_standout_0p854_gt_tuned_loop_0p830": True,
    "prior_frozen_arm_oracle_0p730_was_mislabel_red_flag_resolved": True,
    "memorization_gap_max_plus0p103_several_negative_held_ge_train": True,
    "all_6_floors_collapse": True,
    "floors_note": "random_addr/no_coref-b/wrongrole/shuffled/most_recent under bars; pooled b/c << 0.80",
    "prereg_integrity": {"guard_commit": "eae0a3867", "guard_commit_time_edt": "2026-07-31T04:48:42",
        "results_commit": "565f28009", "results_commit_time_edt": "2026-07-31T05:24:54",
        "run_start_est_edt": "~05:10", "guard_committed_min_before_run": 22,
        "verdict_code_frozen_in_git_before_any_number_existed": True,
        "metrics_ts_iso_utc": "2026-07-31T09:23:53", "elapsed_s": 793, "working_tree_clean": True,
        "could_not_be_retrofitted_to_observed_numbers": True},
    "triple_vetted": ["prior recompute a78ff08 (bit-exact s7/s13)", "this final lock (all 7 conds recomputed; new "
        "seed s19 in-family)", "pre-registered corrected guard"],
    "recompute_matched_all_7_stored_flags": True,
    "atype_recovers_under_scale_capture_a_1p00_b_0p99_c_1p15": True,
    "construction_audit_shortcuts_at_chance": True,
    "scope_synthetic_harness_colors_as_entities_templated": True, "naturalistic_untested": True,
    "addresses_dominant_entity_reid_half": True, "role_filler_attribution_half_separate_untested_track": True,
    "win_is_cheap_minimal_unfreeze_deeper_overfits_craters": True,
    "cell_sha16": cell_sha16, "prereg_sha16": prereg_sha16, "metrics_sha16": metrics_sha16,
    "cross_arc_overlap": ("same arc/harness as the prior-audited bounded-scale run (a78ff08); this is a scoped "
        "confirmatory re-run of a known referent (targeted extension, not a rediscovery). Only same-family banked "
        "atom is the assembly loop 29592; no spurious duplication."),
}

atom = {
    "atom_id": AID, "seq": NEW_SEQ, "op": "atomize", "corpus": "math",
    "tier": "CHAIN_GRADE", "cert_status": "chain-grade",
    "grade": "CHAIN_GRADE_founding_gap_entity_reid_break_minimal_unfreeze_top1_scope_bounded_synthetic",
    "verdict": "CLEAN_PASS", "anchor": "situation_model_assembly_encoder_retrain_scale_v1",
    "anchor_name": "situation_model_assembly_encoder_retrain_scale_v1",
    "cell": "experiments/exp_situation_model_assembly_encoder_retrain_scale_v1.py",
    "cell_commit": "eae0a3867", "cell_content_sha256_16": cell_sha16,
    "prereg": "preregs/2026-07-31_encoder_retrain_scale_corrected_guard.md", "prereg_sha256_16": prereg_sha16,
    "metrics_path": "data/exp_situation_model_assembly_encoder_retrain_scale_v1/metrics.json",
    "metrics_sha256_16": metrics_sha16,
    "module": ("minimal_unfreeze_top1_layer_fine_tune_of_substrate_own_v2_encoder_cross_mention_consistency_plus_"
        "inter_entity_push_plus_VICReg_objective_held_out_situation_model_loop_via_cross_frame_entity_reid_"
        "corrected_loop_anchored_collapse_guard_tuned_oracle_ceiling_d6_full_unfreeze_must_fail_control"),
    "headline": HEADLINE, "key_metrics": key_metrics,
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("AUDIT-ONLY independent recompute (.venv, off-disk, ignoring stored guard flags): "
        "reproduced all 7 conditions' type_ok + guard(C1-C4) + mem + oracle gates from raw per_condition fields; "
        "matched every stored guard_pass flag 7/7. d6 fails C1(0.292<0.470) AND C2(drift+0.354). Both d1 configs "
        "clean-pass 3 seeds. No arm exceeds its tuned-oracle. All floors collapse. Pre-reg integrity confirmed via "
        "git commit timestamps (guard code committed eae0a3867 22 min before results 565f28009) + metrics ts_iso/"
        "mtime + clean working tree."),
    "composes_seq": [29592], "corrects_seq": [], "amends_seq": [],
    "cert_delta": 1, "net_cert_delta": 1, "store_head_at_write": STORE_HEAD,
    "store_head_at_write_note": f"max seq across math+meta atoms + cert_ledger = {STORE_HEAD} at write; assigned {NEW_SEQ}",
    "honest_scope": ("(a) SYNTHETIC situation-model harness: colors-as-entities, templated passages, glass-box "
        "extraction -- naturalistic (real-text) generalization is UNTESTED. (b) Breaks the DOMINANT half of the "
        "founding wall (cross-frame ENTITY re-identification); the ROLE/filler-attribution half is a SEPARATE, "
        "still-untested track. (c) The win is specifically CHEAP MINIMAL-UNFREEZE (top-1 encoder layer, 3.15M "
        "params); deeper unfreeze OVERFITS and CRATERS (top-3 lite plateaus ~0.534; top-6 full-unfreeze d6 craters "
        "to 0.292 below the frozen wall). (d) 3 seeds x 2 diversity levels (nctx 40/80; palette hard-capped at "
        "V_FILL=20 so contexts, not palette, is the honest diversity axis); generalizes to HELD-OUT entities; "
        "distinct-not-collapsed under a loop-anchored guard with a working d6 must-fail control; tuned_loop below "
        "the tuned-oracle ceiling; floors collapse; no memorization. (e) The absolute loop ceiling here is the "
        "tuned-oracle ~0.80-0.85, so 0.83 is near-ceiling for this harness, NOT a solved-comprehension claim."),
    "framing_correction": ("MUST NOT be recorded as 'breaks the 0.31 wall'. The 0.31 was the bolt-on-WM learned-"
        "key harness = a DIFFERENT addressing/mechanism/harness, NOT comparable to this role_attn-decoded entity-"
        "re-id harness. The honest anchor is: held-out situation-model loop 0.52->0.83 via cross-frame ENTITY re-"
        "identification, where the frozen (un-retrained) v2-encoder baseline HERE sits at loop 0.47-0.52 / entcons "
        "0.813 / q_agree 0.73. The cell verdict_msg wording 'BREAKS the wall' is defensible ONLY within this "
        "harness's frozen entity-re-id ceiling; it must never be conflated with the cross-arc 0.31 bolt-on wall."),
    "fairness_verdict": ("FAIR, pre-registered, not a rubber stamp. The collapse guard's C1 (tuned_loop>=frozen) "
        "is an anti-COLLAPSE disambiguator, NOT the performance bar -- CLEAN_PASS additionally requires all 3 "
        "query types >= 0.60 loop, well above the frozen wall (frozen types 0.42-0.60), so a barely-better-than-"
        "frozen encoder FAILS. C3 (entcons>=0.85) and C4 (q_agree>=0.60) are individually FOOLABLE by a degenerate "
        "encoder (d6 saturates both to 1.000), which is exactly why the guard is ANCHORED to loop decode (C1) plus "
        "a frozen-referenced drift cap (C2); the d6 full-unfreeze control fails on BOTH C1 and C2 (doubly robust). "
        "Pre-reg integrity: guard prereg + verdict code committed 22 min before the results run, so the guard "
        "could not be retrofitted to observed numbers (git-timestamp confirmed). No exceeds-oracle (the prior "
        "'0.830>0.730' red flag was a frozen-arm-oracle mislabel; tuned-oracle 0.854 is the correct ceiling)."),
    "revival_criteria": ("EXTENSION / promotion paths: (1) NATURALISTIC validation -- swap the synthetic templated "
        "harness for real-text passages; a cross-voice, role-probe-fair held-out loop clearing the same bars would "
        "extend from synthetic to naturalistic reading. (2) The ROLE/filler-attribution half of the founding wall "
        "is a SEPARATE untested track -- this cell only breaks the entity-re-id half. (3) DEPLOY/SCALE of the "
        "minimal-unfreeze fine-tune as a wired reusable module is PENDING USER steer + naturalistic validation "
        "(WIRE-candidate, not yet promoted). (4) DEMOTE trigger: if a naturalistic re-run shows the lift is "
        "template-memorization rather than genuine cross-frame re-id, or if the tuned-oracle ceiling is an "
        "artifact of the synthetic construction."),
    "primitive_assessment": ("The missing primitive for the DOMINANT half of the founding wall was a CROSS-FRAME-"
        "STABLE entity representation -- and the fix is the substrate's OWN encoder EARNING it via error-driven "
        "fine-tune (top-1 layer) with the validated consistency+push+VICReg objective, NOT a borrowed embedding or "
        "a bolt-on reader. This is consistent with the arc's diagnosis (frozen encoder was the ceiling for entity "
        "re-id) and respects the USER invariant (own learned mechanism, minimal-unfreeze, glass-box). The role/"
        "filler-attribution half remains a separate primitive gap."),
    "promote_verdict": "WIRE_CANDIDATE_deploy_and_scale_PENDING_USER_steer_plus_naturalistic_validation",
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom))

# ---- A5 WRITE: atoms.jsonl ----
new_line = json.dumps(atom, ensure_ascii=False)
assert "\r" not in new_line and "\n" not in new_line
new_text = "\n".join(atom_lines + [new_line]) + "\n"
d = os.path.dirname(os.path.abspath(ATOMS))
fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp"); os.close(fd)
with open(tmp, "w", encoding="utf-8", newline="") as f:
    f.write(new_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp, ATOMS)
raw = open(ATOMS, "rb").read()
assert b"\r\n" not in raw, "CRLF doubling in atoms.jsonl"
v = [json.loads(l) for l in open(ATOMS, encoding="utf-8").read().splitlines() if l.strip()]
assert len(v) == len(atom_lines) + 1 and v[-1]["atom_id"] == AID and v[-1]["tier"] == "CHAIN_GRADE" and v[-1]["cert_delta"] == 1
print(f"ATOMS OK: {len(atom_lines)} -> {len(v)}; seq {NEW_SEQ}; CHAIN_GRADE cert_delta +1; no CRLF.")

# ---- A5 WRITE: cert_ledger.jsonl ----
ledger = dict(atom)
ledger["decision"] = ("CHAIN_GRADE CERT +1. FINAL-LOCK VET of the arc's biggest claim: a CLEAN_PASS certified "
    "founding-gap break (encoder retrain lifts held-out situation-model loop 0.52->0.83 via cross-frame entity "
    "re-id). Scoped to the CONFIRMATORY re-run's integrity because the corrected collapse guard was authored by "
    "the same exp_dev that ran it. VERDICT: LEGITIMATELY-CERTIFIED CLEAN_PASS -- (1) PRE-REG INTEGRITY confirmed "
    "off git: guard prereg + verdict code committed eae0a3867 @ 04:48:42 EDT, results 565f28009 @ 05:24:54 EDT, "
    "run started ~05:10 EDT (ts_iso 09:23:53Z - 793s) = 22 min AFTER the guard commit; verdict-computing code "
    "frozen in git before any number existed -> guard NOT retrofitted. (2) GUARD FAIR: C1 anti-collapse "
    "disambiguator (performance bar is 0.60-per-type, above the frozen wall); C3/C4 foolable by d6's saturation so "
    "guard is loop-anchored C1 + drift-cap C2; d6 fails BOTH (doubly robust anti-rubber-stamp). (3) d6 must-fail "
    "control verified off-disk (tuned 0.292<frozen 0.470, wc_drift +0.354). (4) CLEAN_PASS reproduces: both d1 "
    "configs pass 3 seeds; new seed s19 in-family; my recompute matched all 7 stored flags; no exceeds-oracle "
    "(tuned<tuned_oracle every arm; the 0.730 red flag was a frozen-arm-oracle mislabel). (5) Floors collapse; "
    "mem_gap honest (held ~ train). FRAMING RIDES THE ATOM: claim = 0.52->0.83 via cross-frame entity re-id, "
    "minimal-unfreeze top-1 (3.15M params); NOT 'breaks the 0.31 wall'. SCOPE: synthetic harness (naturalistic "
    "UNTESTED), dominant entity-re-id half only, cheap-minimal-unfreeze win, triple-VET'd. WIRE-candidate; deploy/"
    "scale PENDING USER steer + naturalistic validation. Local-only; needs orchestrator store sync.")
ledger["note"] = ("AUDIT-ONLY independent .venv recompute off metrics.json (ignored stored guard flags; "
    "recomputed all 7 conditions from raw per_condition). Hashes: cell d28019195b91cfa6, prereg 0f6c6091d2ea1497, "
    "metrics 4471d44ebf53c14a. Composes 29592 (assembly loop whose naturalistic wall was localized to the "
    "encoder; this breaks the dominant entity-re-id half).")
json.loads(json.dumps(ledger))
led_line = json.dumps(ledger, ensure_ascii=False)
assert "\r" not in led_line and "\n" not in led_line
new_led = "\n".join(ledger_lines + [led_line]) + "\n"
dl = os.path.dirname(os.path.abspath(LEDGER))
fd2, tmp2 = tempfile.mkstemp(dir=dl, suffix=".tmp"); os.close(fd2)
with open(tmp2, "w", encoding="utf-8", newline="") as f:
    f.write(new_led); f.flush(); os.fsync(f.fileno())
os.replace(tmp2, LEDGER)
assert b"\r\n" not in open(LEDGER, "rb").read(), "CRLF doubling in ledger"
vl = [json.loads(l) for l in open(LEDGER, encoding="utf-8").read().splitlines() if l.strip()]
assert len(vl) == len(ledger_lines) + 1 and vl[-1]["atom_id"] == AID and iseq(vl[-1]) == NEW_SEQ
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)}; seq {NEW_SEQ}; cert_delta +1; no CRLF.")

# ---- A5 WRITE: capability_registry.jsonl (WIRE candidate; deploy PENDING) ----
reg = {
    "id": "encoder_retrain_minimal_unfreeze_top1_entity_reid_situation_model",
    "name": ("Minimal-unfreeze (top-1 layer) v2-encoder fine-tune for cross-frame ENTITY re-identification "
        "(VET-CONFIRMED CHAIN_GRADE founding-gap break, synthetic harness)"),
    "kind": "exp-cell+capability",
    "path": ["experiments/exp_situation_model_assembly_encoder_retrain_scale_v1.py",
             "experiments/exp_situation_model_assembly_encoder_retrain_lite_v1.py"],
    "status": "vet_confirmed_chain_grade_founding_gap_entity_reid_break_2026-07-31",
    "gate_decision": "WIRE_CANDIDATE",
    "gate_decision_target": ("minimal-unfreeze top-1 encoder layer (3.15M trainable params) fine-tune of the "
        "substrate's OWN v2 encoder with the validated cross-mention-consistency + inter-entity-push + VICReg "
        "objective; lifts held-out situation-model loop 0.52->0.83 via cross-frame ENTITY re-identification, "
        "breaking the DOMINANT (entity-re-id) half of the founding comprehension wall"),
    "integration_status": "ISLAND",
    "used_by": [],
    "deploy_scale_decision": "PENDING_USER_steer_plus_naturalistic_validation",
    "revival_criteria": ("Deploy/scale as a wired reusable module is PENDING USER steer + NATURALISTIC validation. "
        "(1) Swap the synthetic templated harness (colors-as-entities) for real-text passages; a cross-voice, "
        "role-probe-fair held-out loop clearing the same bars extends synthetic->naturalistic and promotes to a "
        "wired module. (2) The ROLE/filler-attribution half of the wall is a SEPARATE untested track. (3) DEMOTE "
        "if a naturalistic re-run shows the lift is template-memorization, not genuine cross-frame re-id."),
    "supersedes": None, "superseded_by": None,
    "current_best_for": ("VET math seq 29593 CONFIRMED CHAIN_GRADE (scope-bounded, synthetic harness): on the "
        "situation-model harness (6 entities across STATE/PLACE roles, held-out entities), minimal-unfreeze top-1 "
        "encoder fine-tune lifts held-out loop 0.47-0.52 -> 0.83 (best d1_div80_s13 0.830) across 3 seeds x 2 "
        "diversity levels, all 3 query types >= 0.60, distinct-not-collapsed (loop-anchored guard; d6 full-unfreeze "
        "control fails on C1+C2), tuned_loop < tuned-oracle every arm (no exceeds-oracle), all 6 floors collapse, "
        "no memorization. HONEST FRAMING: 0.52->0.83 via cross-frame ENTITY re-id -- NOT 'breaks the 0.31 wall' "
        "(that was the bolt-on-WM learned-key harness, a different addressing scheme). Win = CHEAP minimal-unfreeze "
        "(top-1; deeper unfreeze overfits/craters). SCOPE: synthetic harness, naturalistic UNTESTED; dominant "
        "entity-re-id half only."),
    "provenance": ("cell eae0a3867; VET math seq 29593 (hdi_skunkworks) = CONFIRMED CHAIN_GRADE founding-gap break. "
        "Independent .venv recompute of all 7 conditions matched stored flags; pre-reg integrity confirmed (guard "
        "code committed 22 min before results run); triple-VET'd (prior recompute a78ff08 bit-exact s7/s13 + this "
        "final lock + pre-registered corrected guard). Composes seq 29592 (assembly loop). Cross-arc: scoped "
        "confirmatory re-run of a known referent, not a rediscovery."),
    "last_audit_utc": ts_iso, "last_decision_utc": ts_iso,
}
json.loads(json.dumps(reg))
reg_line = json.dumps(reg, ensure_ascii=False)
assert "\r" not in reg_line and "\n" not in reg_line
new_reg = "\n".join(reg_lines + [reg_line]) + "\n"
dr = os.path.dirname(os.path.abspath(REGISTRY))
fd3, tmp3 = tempfile.mkstemp(dir=dr, suffix=".tmp"); os.close(fd3)
with open(tmp3, "w", encoding="utf-8", newline="") as f:
    f.write(new_reg); f.flush(); os.fsync(f.fileno())
os.replace(tmp3, REGISTRY)
assert b"\r\n" not in open(REGISTRY, "rb").read(), "CRLF doubling in registry"
vr = [json.loads(l) for l in open(REGISTRY, encoding="utf-8").read().splitlines() if l.strip()]
assert len(vr) == len(reg_lines) + 1 and vr[-1]["id"] == reg["id"]
print(f"REGISTRY OK: {len(reg_lines)} -> {len(vr)}; WIRE_CANDIDATE; deploy PENDING USER steer + naturalistic.")
print(f"DONE. atom_id={AID}")
print("LOCAL-ONLY. no origin push; no remote persist.")
