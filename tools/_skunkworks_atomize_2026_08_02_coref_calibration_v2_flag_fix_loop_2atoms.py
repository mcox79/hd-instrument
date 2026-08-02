"""A5-gated LOCAL-ONLY atomize of two independently-VET'd 2026-08-02 landings.
AUDIT-ONLY (hdi_skunkworks). Independent .venv recompute off raw metrics.json on disk
(NOT verdict_msg strings, NOT the Director/spawn-prompt summary). No experiment authored/dispatched
by auditor. Cross-arc overlap check run (substrate_query.sh "pronoun coreference self confidence
calibration flag topic continuity centering") -- top hit cosine=0.418 (tangential, not a duplicate);
NONE at cosine>0.30 is a rediscovery of this specific finding.

TWO atoms, store head 29617 -> seqs 29618/29619. Both math corpus, MEASURED_MECHANISM, cert_delta 0
(neither is a fresh CG capability grant; #1 amends/extends 29616's already-granted name-path cert with
a load-bearing DOWNWARD correction of the pronoun n_compatible framing; #2 is a clean pre-registered
NULL_FIX_MECHANISM branch, a proven mechanism characterization not a capability win).

DISK-VERIFY DEFLATION FOUND (#1): the spawn prompt's framing "n_compatible AUC = 0.724 baseline /
0.709 g5g6 = the CORRECT pronoun flag signal ... earned on BOTH tiers" MIXES TWO DIFFERENT AXES:
0.724 is combined_powered.baseline (full 36-passage/76-decision set) and 0.709 is g5g6_only.baseline
(an 18-passage/60-decision SUBSET, same baseline mechanism) -- i.e. both numbers are the BASELINE
mechanism on two overlapping passage sets, not baseline-vs-strict_cb. The actual strict_cb (the
better-performing coref mechanism) n_compatible AUC on the SAME full powered set is only 0.578125
(combined_powered.strict_cb.pronoun_subset.auc_ncompatible_predicts_error), and 0.577741 on the
g5g6_only subset -- i.e. under strict_cb the n_compatible signal is much weaker (near-chance-to-modest,
well below the 0.65 bar used elsewhere in this arc for margin), NOT robustly earned on both tiers.
Symmetrically, RAW MARGIN improves under strict_cb (0.536->0.627) while n_compatible degrades under
strict_cb (0.724->0.578) -- so "which signal is correct" is itself mechanism-dependent, not a clean
dual-tier win. This atom bans the "earned on both tiers" framing and states the corrected, mechanism-
dependent picture. Per symmetric anti-negativity discipline this is an honest downward correction of
the Director's finding-1 framing, filed as such.
"""
import json, os, time, tempfile, datetime, hashlib

ATOMS_MATH = "data/substrate_index/math/atoms.jsonl"
ATOMS_META = "data/substrate_index/meta/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"


def iseq(o):
    try:
        return int(o.get("seq"))
    except Exception:
        return -1


def load(p):
    return [l for l in open(p, encoding="utf-8").read().splitlines() if l.strip()]


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


# ---- PRE-GATE ----
math_lines = load(ATOMS_MATH)
meta_lines = load(ATOMS_META)
ledger_lines = load(LEDGER)
pm = [json.loads(l) for l in math_lines]
pe = [json.loads(l) for l in meta_lines]
pl = [json.loads(l) for l in ledger_lines]
existing_ids = {o.get("atom_id") for o in (pm + pe) if o.get("atom_id")}
assert not any("\r" in l for l in (math_lines[-5:] + meta_lines[-5:]))
STORE_HEAD = max(max(iseq(o) for o in pm), max(iseq(o) for o in pe), max(iseq(o) for o in pl))
assert STORE_HEAD == 29617, f"expected store head 29617, got {STORE_HEAD}"
assert any(iseq(o) == 29616 for o in pm), "parent 29616 (calibration v1, math) missing"
print(f"PRE-GATE OK: store head {STORE_HEAD}; parent 29616 present; new seqs 29618/29619.")

# =====================================================================================================
# OFF-DISK independent recompute -- #1 calibration v2 (powered)
# =====================================================================================================
C = json.load(open("data/exp_coref_self_confidence_calibration_v2/metrics.json", encoding="utf-8"))
assert C["verdict"] == "MIDDLE_BAND_PRONOUN"
r = C["results"]["combined_powered"]
b, s = r["baseline"], r["strict_cb"]
assert b["instrumented_copy_reproduces_mechanism_exactly"] is True and b["n_repro_mismatches"] == 0
assert s["instrumented_copy_reproduces_mechanism_exactly"] is True and s["n_repro_mismatches"] == 0
assert abs(b["name_subset"]["auc_margin_predicts_error"] - 0.8022976222281593) < 1e-9
assert abs(s["name_subset"]["auc_margin_predicts_error"] - 0.7921084018022794) < 1e-9
assert abs(b["pronoun_subset"]["auc_margin_predicts_error"] - 0.536281179138322) < 1e-9
assert abs(s["pronoun_subset"]["auc_margin_predicts_error"] - 0.6267857142857143) < 1e-9
assert b["pronoun_subset"]["n"] == 76 and s["pronoun_subset"]["n"] == 76
assert abs(b["pronoun_subset"]["auc_ncompatible_predicts_error"] - 0.7244897959183674) < 1e-9
assert abs(s["pronoun_subset"]["auc_ncompatible_predicts_error"] - 0.578125) < 1e-9  # DEFLATION: not 0.709

g = C["results"]["g5g6_only"]
gb, gs = g["baseline"], g["strict_cb"]
assert gb["instrumented_copy_reproduces_mechanism_exactly"] is True and gb["n_repro_mismatches"] == 0
assert gs["instrumented_copy_reproduces_mechanism_exactly"] is True and gs["n_repro_mismatches"] == 0
assert abs(gb["pronoun_subset"]["auc_ncompatible_predicts_error"] - 0.708994708994709) < 1e-9
assert abs(gs["pronoun_subset"]["auc_ncompatible_predicts_error"] - 0.5777414075286416) < 1e-9  # NOT a 2nd tier confirming 0.709
c_sha = sha16("data/exp_coref_self_confidence_calibration_v2/metrics.json")
cell1_sha = sha16("experiments/exp_coref_self_confidence_calibration_v2.py")
print(f"#1 OFF-DISK OK: name AUC base={b['name_subset']['auc_margin_predicts_error']:.4f} "
      f"strict_cb={s['name_subset']['auc_margin_predicts_error']:.4f} (both >>0.65, extends 29616). "
      f"pronoun margin AUC base={b['pronoun_subset']['auc_margin_predicts_error']:.4f} "
      f"strict_cb={s['pronoun_subset']['auc_margin_predicts_error']:.4f} (MIDDLE_BAND, neither clears 0.65). "
      f"pronoun n_compatible AUC base={b['pronoun_subset']['auc_ncompatible_predicts_error']:.4f} "
      f"strict_cb={s['pronoun_subset']['auc_ncompatible_predicts_error']:.4f} -- DEFLATION: strict_cb "
      f"n_compatible is NOT ~0.71 (that was g5g6_only.BASELINE on an 18-passage subset, 0.7090, confirmed "
      f"a same-mechanism cross-subset check, not a cross-mechanism one); g5g6_only.strict_cb n_compatible="
      f"{gs['pronoun_subset']['auc_ncompatible_predicts_error']:.4f} confirms the degradation is subset-"
      f"independent. metrics_sha={c_sha}")

# =====================================================================================================
# OFF-DISK independent recompute -- #2 flag/fix loop cycle 1
# =====================================================================================================
L = json.load(open("data/exp_coref_flag_fix_loop_topic_continuity_v1/metrics.json", encoding="utf-8"))
assert L["verdict"] == "NULL_FIX_MECHANISM"
fs = L["flag_selection"]
assert abs(fs["base_pronoun_error_rate"] - 0.2631578947368421) < 1e-9
ebn = fs["error_rate_by_n_compatible"]
assert ebn["0"]["error_rate"] == 0.0 and ebn["0"]["n_total"] == 7
assert abs(ebn["1"]["error_rate"] - 0.17647058823529413) < 1e-9 and ebn["1"]["n_total"] == 17
assert abs(ebn["2"]["error_rate"] - 0.2727272727272727) < 1e-9 and ebn["2"]["n_total"] == 11
assert abs(ebn["3"]["error_rate"] - 0.4482758620689655) < 1e-9 and ebn["3"]["n_total"] == 29
pct2 = fs["per_candidate_threshold"]["2"]
assert pct2["n_flagged"] == 52 and abs(pct2["flag_recall_of_errors"] - 0.85) < 1e-9
h = L["headline_combined"]
assert h["pronoun_b3_f1"]["loop_selective"] == h["pronoun_b3_f1"]["loop_uniform"]
assert abs(h["pronoun_b3_f1"]["strict_cb"] - 0.7029326700972488) < 1e-9
assert abs(h["pronoun_b3_f1"]["loop_selective"] - 0.676721094529708) < 1e-9
assert abs(h["identity_demanding_query_acc"]["strict_cb"] - 0.7192982456140351) < 1e-9
assert abs(h["identity_demanding_query_acc"]["loop_selective"] - 0.6842105263157895) < 1e-9
assert h["identity_demanding_query_acc"]["oracle"] > h["identity_demanding_query_acc"]["strict_cb"]
assert h["flag_localized_b3"] is True and h["flag_localized_iddem"] is True
cp = L["combined_powered"]
assert cp["selective_flip_passages"] == cp["uniform_flip_passages"] == 1  # selective==uniform: flag localizes, isn't the problem
trace = L["flag_fix_trace_combined"]
assert trace["n_flagged"] == 52 and trace["n_fix_differs_from_strict_cb"] == 6
assert trace["fix_corrected_strict_cb"] == 0 and trace["fix_broke_strict_cb"] == 3
decay = L["decay_sensitivity_combined"]
for k in ["0.5", "0.7", "0.9", "1.0"]:
    assert decay[k]["selective_pron_errors"] >= decay[k]["strict_cb_pron_errors"]  # robust null across decay
l_sha = sha16("data/exp_coref_flag_fix_loop_topic_continuity_v1/metrics.json")
cell2_sha = sha16("experiments/exp_coref_flag_fix_loop_topic_continuity_v1.py")
print(f"#2 OFF-DISK OK: flag localizes (err by n_compatible 0/17.6/27.3/44.8% vs base 26.3%; thr>=2 flags "
      f"52/76 capturing 85% of errors); selective==uniform on flip_passages ({cp['selective_flip_passages']}) "
      f"confirms flag ISN'T the problem; fix HURTS (pronoun-B3 {h['pronoun_b3_f1']['strict_cb']:.4f}->"
      f"{h['pronoun_b3_f1']['loop_selective']:.4f}, iddem {h['identity_demanding_query_acc']['strict_cb']:.4f}->"
      f"{h['identity_demanding_query_acc']['loop_selective']:.4f}); on 6 divergent flagged decisions "
      f"corrected={trace['fix_corrected_strict_cb']} broke={trace['fix_broke_strict_cb']}; null robust across "
      f"decay 0.5-1.0. metrics_sha={l_sha}")

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
ts_day = "2026-08-02"


def A5_write(path, lines, new_atom, tier_expect):
    line = json.dumps(new_atom, ensure_ascii=False)
    assert "\r" not in line and "\n" not in line
    new_text = "\n".join(lines + [line]) + "\n"
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp"); os.close(fd)
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(new_text); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)
    raw = open(path, "rb").read()
    assert b"\r\n" not in raw, f"CRLF doubling in {path}"
    v = [json.loads(l) for l in open(path, encoding="utf-8").read().splitlines() if l.strip()]
    assert len(v) == len(lines) + 1
    assert v[-1]["atom_id"] == new_atom["atom_id"] and v[-1].get("tier") == tier_expect
    return v


# =====================================================================================================
# ATOM 29618 -- MATH: calibration v2 powered flag layer, name-path extends 29616, pronoun DEFLATED framing.
# =====================================================================================================
AID1 = ("math::coref_self_confidence_calibration_v2_POWERED_pronoun_eval_n76_name_path_margin_AUC_"
    "STRENGTHENS_0p753_to_0p802_baseline_0p792_strict_cb_extends_29616_pronoun_path_RAW_MARGIN_remains_"
    "MIDDLE_BAND_0p536_baseline_0p627_strict_cb_neither_clears_0p65_bar_but_powered_trustworthy_negative_"
    "n_compatible_candidate_count_is_a_SEPARATE_diagnostic_signal_that_is_MECHANISM_DEPENDENT_not_a_"
    "clean_dual_tier_win_baseline_0p724_strict_cb_only_0p578_g5g6_subset_confirms_0p709_baseline_0p578_"
    "strict_cb_DEFLATES_the_directors_earned_on_both_tiers_framing_which_conflated_a_same_mechanism_"
    "cross_subset_check_0p724_vs_0p709_both_baseline_with_a_cross_mechanism_one_both_instrumented_"
    "copies_reproduce_exactly_0_mismatches_LOCAL_ONLY")
assert AID1 not in existing_ids
HEAD1 = ("MEASURED_MECHANISM (CERT +0; extends/amends 29616's already-granted name-path CERT+1, does not "
    "grant new CERT). On the powered combined eval (n=76 pronoun decisions, n=273 name decisions, clean "
    "local MUC-style decision-time label): the NAME-path decision-margin signal STRENGTHENS under power -- "
    "AUC 0.8023 (baseline mechanism) / 0.7921 (strict_cb mechanism), up from 29616's exploratory n=182 "
    "AUC=0.753 -- confirms the primitive generalizes, both well above the 0.65 pass bar. The PRONOUN-path "
    "RAW MARGIN remains uncalibrated: AUC 0.5363 (baseline) / 0.6268 (strict_cb), neither clears 0.65 -- "
    "this is now a POWERED (n=76, not 29616's underpowered n=16) trustworthy MIDDLE_BAND negative for the "
    "margin signal specifically. A SEPARATE diagnostic, pronoun-path #compatible-candidates (n_compatible), "
    "was proposed by the cell as a possibly better pronoun flag. Recompute finds this signal is real but "
    "MECHANISM-DEPENDENT, not a clean dual-tier win as initially framed: under the baseline mechanism "
    "n_compatible AUC=0.7245 (combined, n=76) / 0.7090 (g5g6-only 18-passage subset, n=60) -- consistent, "
    "a genuinely useful signal under baseline. Under strict_cb (the BETTER-performing coref mechanism) "
    "n_compatible AUC drops to 0.5781 (combined) / 0.5777 (g5g6-only subset) -- near-chance-to-modest, well "
    "below the margin signal's own bar. Symmetrically, raw margin IMPROVES under strict_cb (0.536->0.627) "
    "while n_compatible DEGRADES under strict_cb (0.724->0.578) -- so which pronoun-path signal is 'correct' "
    "flips depending on which coref mechanism is deployed; there is no single pronoun flag signal earned "
    "on both tiers. Both instrumented copies reproduce their mechanism's clusters exactly (0 mismatches for "
    "all four blocks: combined_powered.{baseline,strict_cb}, g5g6_only.{baseline,strict_cb}), so this is not "
    "a harness-drift artifact -- the mechanism-dependence is real.")
atom1 = {
    "atom_id": AID1, "seq": 29618, "op": "atomize", "corpus": "math",
    "tier": "MEASURED_MECHANISM", "cert_status": "proven-bound",
    "grade": "MM_calibration_v2_powered_name_path_extends_29616_pronoun_signal_mechanism_dependent_not_dual_tier",
    "verdict": "MIDDLE_BAND_PRONOUN", "anchor": "coref_self_confidence_calibration_v2",
    "anchor_name": "coref_self_confidence_calibration_v2",
    "cell": "experiments/exp_coref_self_confidence_calibration_v2.py",
    "cell_commit": "150058b03", "cell_content_sha256_16": cell1_sha,
    "metrics_path": "data/exp_coref_self_confidence_calibration_v2/metrics.json", "metrics_sha256_16": c_sha,
    "headline": HEAD1,
    "key_metrics": {
        "cell_verdict": "MIDDLE_BAND_PRONOUN", "auditor_tier": "MEASURED_MECHANISM", "cert_delta": 0,
        "name_auc_baseline": 0.8022976222281593, "name_auc_strict_cb": 0.7921084018022794,
        "name_n": 273, "name_auc_29616_prior_n182": 0.7531645569620253,
        "pronoun_margin_auc_baseline": 0.536281179138322, "pronoun_margin_auc_strict_cb": 0.6267857142857143,
        "pronoun_n": 76,
        "pronoun_ncompatible_auc_baseline_combined": 0.7244897959183674,
        "pronoun_ncompatible_auc_strict_cb_combined": 0.578125,
        "pronoun_ncompatible_auc_baseline_g5g6subset": 0.708994708994709,
        "pronoun_ncompatible_auc_strict_cb_g5g6subset": 0.5777414075286416,
        "repro_exact_all_4_blocks": True,
        "pass_bar_used_elsewhere_this_arc": 0.65,
    },
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("AUDIT-ONLY .venv recompute off metrics.json results.{combined_powered,"
        "g5g6_only}.{baseline,strict_cb} blocks (NOT verdict_msg): all 8 cited AUCs confirmed exact to "
        "1e-9. repro-exact flags (instrumented_copy_reproduces_mechanism_exactly, n_repro_mismatches=0) "
        "confirmed True/0 for all four (mechanism x eval-set) combinations independently, not just the "
        "combined_powered.pronoun_subset the cell's own verdict_driven_by field cites. DEFLATION CAUGHT: "
        "the spawn prompt's '0.724 baseline / 0.709 g5g6 = earned on BOTH tiers' claim was VERIFIED WRONG "
        "as framed -- 0.709 is g5g6_only.baseline (same baseline mechanism, an 18-passage subset), not "
        "g5g6_only.strict_cb or any strict_cb number at all; the actual strict_cb n_compatible AUC on the "
        "full powered set is 0.578125, independently confirmed to also degrade on the g5g6-only subset "
        "(0.5777), so the mechanism-dependence is not a fluke of set size. This is a genuine downward "
        "correction, filed per symmetric anti-negativity, not a rubber-stamp of the spawn prompt's framing."),
    "composes_seq": [29616], "corrects_seq": [], "amends_seq": [29616],
    "cert_delta": 0, "net_cert_delta": 0, "store_head_at_write": STORE_HEAD,
    "honest_scope": ("Verdict-bearing for: (a) name-path margin AUC generalizing under power (both "
        "mechanisms) -- extends 29616's cert, no new grant since 29616 already banked +1 for the name "
        "path; (b) pronoun-path margin remaining un-calibrated, now POWERED (n=76) rather than 29616's "
        "underpowered n=16 -- a trustworthy negative. NOT verdict-bearing as 'the flag layer is earned on "
        "both tiers via n_compatible' -- that claim is corrected here to 'n_compatible is a real diagnostic "
        "under the baseline mechanism only (AUC~0.71-0.72, consistent across two overlapping eval sets); "
        "under strict_cb it degrades to near-chance (AUC~0.58), so no pronoun-path signal (margin or "
        "n_compatible) is currently earned across both mechanisms simultaneously.'"),
    "framing_correction": ("DEFLATES the spawn-prompt framing for the n_compatible claim specifically: "
        "'AUC = 0.724 baseline / 0.709 g5g6 ... earned on BOTH tiers' mixed a same-mechanism cross-subset "
        "comparison (baseline on full-set vs baseline on an 18-passage subset) with what was described as "
        "a cross-mechanism comparison; the real strict_cb number (0.578) was omitted from the framing and "
        "is materially weaker. Name-path claims (0.802/0.792) and pronoun-margin MIDDLE_BAND claims "
        "(0.536/0.627) both confirm exactly as stated in the spawn prompt -- only the n_compatible framing "
        "needed correction."),
    "revival_criteria": ("To claim a genuine dual-tier pronoun flag signal: either (a) find a pronoun flag "
        "feature that holds AUC>=0.65 under BOTH baseline and strict_cb on the powered set, or (b) if the "
        "deployed mechanism is fixed to strict_cb (the stronger coref mechanism), re-evaluate whether "
        "n_compatible's baseline-only strength is even relevant -- the flag needs to be earned on whichever "
        "mechanism is actually in production. The 300-passage g5/g6 dense-pronoun mine noted as available "
        "in 29616's revival_criteria would further power both subsets for a decisive check."),
    "primitive_assessment": ("Reconfirms (does not newly grant) the name-path decision-margin self-"
        "monitoring primitive from 29616, now powered n=182->273 and cross-mechanism-checked. Does NOT "
        "validate a working pronoun-path self-monitoring primitive under all mechanisms -- n_compatible is "
        "a real but mechanism-conditional diagnostic (baseline-only), margin remains uncalibrated under "
        "either mechanism at the 0.65 bar."),
    "hf_attribution": "n/a (mixed positive-extension / negative-deflation, not a HF).",
    "fairness_verdict": ("FAIR: label definition unchanged from 29616 (clean local link-level MUC-style, "
        "judged at decision time); powered from n=16/182 to n=76/273 without re-tuning the label or the "
        "0.65 pass bar. Both mechanisms (baseline, strict_cb) and both eval sets (combined_powered, "
        "g5g6_only) evaluated under the identical protocol, enabling the honest cross-mechanism comparison "
        "that surfaced the n_compatible deflation."),
    "cross_arc_overlap": ("Composes/amends 29616 (same mechanism, powered). substrate_query.sh check "
        "('pronoun coreference self confidence calibration flag topic continuity centering') returned top "
        "hit cosine=0.418 (tangential note, not a duplicate); no prior-arc atom found rediscovering this "
        "specific powered pronoun-vs-name calibration result."),
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom1))

# =====================================================================================================
# ATOM 29619 -- MATH: self-improving-loop cycle 1 -- NULL_FIX_MECHANISM clean decomposition.
# =====================================================================================================
AID2 = ("math::coref_flag_fix_loop_topic_continuity_v1_NULL_FIX_MECHANISM_preregistered_branch_clean_"
    "decomposition_FLAG_earned_and_localizes_pronoun_error_rate_by_n_compatible_0pct_17p6pct_27p3pct_"
    "44p8pct_vs_base_26p3pct_thr_ge2_flags_52_of_76_capturing_85pct_of_errors_selective_equals_uniform_"
    "on_every_metric_confirms_flag_localization_not_the_problem_FIX_topic_continuity_centering_continue_"
    "HURTS_pronoun_B3_0p703_to_0p677_iddem_query_0p719_to_0p684_away_from_oracle_0p930_on_6_divergent_"
    "flagged_decisions_corrected_0_broke_3_null_robust_across_decay_0p5_to_1p0_MECHANISM_flagged_same_"
    "gender_pronouns_refer_to_a_NON_topic_entity_a_Centering_SHIFT_so_preferring_the_ongoing_topic_hurts_"
    "these_need_verb_semantics_selectional_preference_world_knowledge_not_available_glass_box_yet_"
    "strict_cb_remains_best_coref_this_cell_mutated_nothing_LOCAL_ONLY")
assert AID2 not in existing_ids
HEAD2 = ("MEASURED_MECHANISM (CERT +0; pre-registered NULL_FIX_MECHANISM branch, a clean mechanism "
    "characterization, not a capability win or a failure). DECOMPOSES the self-improving-reader loop's "
    "first cycle into two independently-testable claims. (a) FLAG EARNED + LOCALIZES: pronoun error rate "
    "rises sharply with #compatible-candidates (n_compatible) -- 0% at nc=0 (n=7), 17.6% at nc=1 (n=17), "
    "27.3% at nc=2 (n=11), 44.8% at nc=3 (n=29), vs a 26.3% base pronoun error rate; a threshold>=2 flags "
    "52/76 pronoun decisions, capturing 85% of the actual errors. Flag-localization control: applying the "
    "topic-continuity fix SELECTIVELY (only on flagged decisions) produces IDENTICAL headline metrics to "
    "applying it UNIFORMLY (everywhere) -- pronoun-B3 and identity-demanding-query accuracy match exactly "
    "between loop_selective and loop_uniform, and selective_flip_passages==uniform_flip_passages==1 -- "
    "i.e. the flag is not itself introducing harm by mis-targeting; whatever happens, happens the same way "
    "whether or not you gate by the flag. (b) FIX FAILS: topic-continuity (Centering-theory 'Continue' "
    "preference) applied to flagged decisions HURTS -- pronoun-B3 F1 drops 0.7029->0.6767, identity-"
    "demanding-query accuracy drops 0.7193->0.6842 (moving AWAY from the oracle ceiling of 0.9298). On the "
    "6 flagged decisions where the fix's choice differs from strict_cb, the fix corrected 0 and broke 3 "
    "(net negative, not merely inert). The null is robust across topic-decay 0.5/0.7/0.9/1.0 -- selective "
    "pronoun error count is >= strict_cb's at every decay setting. MECHANISM DIAGNOSIS (source-grounded, "
    "not asserted): the flagged same-gender pronouns systematically refer to a NON-topic entity -- a "
    "Centering-theory SHIFT, not a Continue -- so a mechanism that prefers the ongoing topic actively "
    "pushes the wrong direction on exactly the cases it was meant to help. These cases need verb-semantics "
    "/ selectional-preference / world-knowledge grounding, which is not yet available glass-box in this "
    "substrate. strict_cb (0.703 pronoun-B3) remains the best coref config; this cell mutated no production "
    "state.")
atom2 = {
    "atom_id": AID2, "seq": 29619, "op": "atomize", "corpus": "math",
    "tier": "MEASURED_MECHANISM", "cert_status": "proven-bound",
    "grade": "MM_selfimproving_loop_cycle1_flag_earned_localizes_topic_continuity_fix_fails_shift_not_continue",
    "verdict": "NULL_FIX_MECHANISM", "anchor": "coref_flag_fix_loop_topic_continuity_v1",
    "anchor_name": "coref_flag_fix_loop_topic_continuity_v1",
    "cell": "experiments/exp_coref_flag_fix_loop_topic_continuity_v1.py",
    "cell_commit": "82492af76", "cell_content_sha256_16": cell2_sha,
    "metrics_path": "data/exp_coref_flag_fix_loop_topic_continuity_v1/metrics.json", "metrics_sha256_16": l_sha,
    "headline": HEAD2,
    "key_metrics": {
        "cell_verdict": "NULL_FIX_MECHANISM", "auditor_tier": "MEASURED_MECHANISM", "cert_delta": 0,
        "base_pronoun_error_rate": 0.2631578947368421,
        "error_rate_nc0": 0.0, "error_rate_nc1": 0.17647058823529413,
        "error_rate_nc2": 0.2727272727272727, "error_rate_nc3": 0.4482758620689655,
        "flag_threshold_used": 2, "n_flagged": 52, "flag_recall_of_errors": 0.85,
        "pronoun_b3_strict_cb": 0.7029326700972488, "pronoun_b3_loop_selective": 0.676721094529708,
        "iddem_acc_oracle": 0.9298245614035088, "iddem_acc_strict_cb": 0.7192982456140351,
        "iddem_acc_loop_selective": 0.6842105263157895,
        "n_fix_differs_from_strict_cb": 6, "fix_corrected_strict_cb": 0, "fix_broke_strict_cb": 3,
        "selective_equals_uniform_flip_passages": True,
        "null_robust_across_decay_0p5_to_1p0": True,
    },
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("AUDIT-ONLY .venv recompute off metrics.json flag_selection/headline_combined/"
        "combined_powered/flag_fix_trace_combined/decay_sensitivity_combined blocks (NOT verdict_msg). All "
        "error-rate-by-n_compatible bins confirmed exact (0/17.65/27.27/44.83% vs base 26.32%). Confirmed "
        "loop_selective==loop_uniform on pronoun_b3_f1 bit-for-bit AND selective_flip_passages== "
        "uniform_flip_passages==1 independently -- this is the actual evidence for 'flag localizes, isn't "
        "the problem', not merely asserted from the verdict_msg. Independently confirmed fix_corrected_"
        "strict_cb=0 / fix_broke_strict_cb=3 on n_fix_differs=6 from flag_fix_trace_combined (not from "
        "verdict_msg's '0x/3x' phrase). Confirmed decay-robustness by iterating all 4 decay_sensitivity_"
        "combined keys (0.5/0.7/0.9/1.0) and checking selective_pron_errors>=strict_cb_pron_errors at each, "
        "not trusting the single 'robust to decay' claim."),
    "composes_seq": [29616, 29618], "corrects_seq": [], "amends_seq": [],
    "cert_delta": 0, "net_cert_delta": 0, "store_head_at_write": STORE_HEAD,
    "honest_scope": ("This is a PRE-REGISTERED branch outcome (NULL_FIX_MECHANISM was an anticipated "
        "verdict in the cell's own design, not a post-hoc reframe of a failure), so it is treated as a "
        "genuine, trustworthy mechanism characterization -- MEASURED_MECHANISM, not HARD_FAIL, because the "
        "flag half of the claim is a real positive result and the fix half is a real, well-controlled "
        "negative with an identified mechanism, not a broken test. Do not read this as 'the self-improving "
        "loop failed' -- it decomposed cleanly into an earned component (flag) and an open-frontier "
        "component (fix), which is exactly the diagnostic information a can-fail design is supposed to "
        "produce."),
    "framing_correction": ("Confirms the Director/spawn-prompt framing closely on every cited number. No "
        "deflation found for this finding -- all figures (error-rate-by-n_compatible, flag capture 85%, "
        "pronoun-B3/iddem lift deltas, 0-corrected/3-broke, decay robustness) reproduce exactly off metrics.json."),
    "revival_criteria": ("Fix needs supplied verb-semantics / selectional-preference / world-knowledge to "
        "distinguish Centering Continue vs Shift cases for these same-gender flagged pronouns -- directly "
        "maps to the standing USER steer of supply-a-dictionary/lexicon as allowed DATA plus the flag-and-"
        "tiered-research program. A cheap next probe: does a supplied verb-argument selectional-preference "
        "signal (not a bolt-on parser, a supplied FACT table) correctly re-route the 6 divergent flagged "
        "decisions toward Shift when the verb's semantics disfavor the topic entity as filler?"),
    "primitive_assessment": ("Validates a reusable primitive: n_compatible-count as a genuine, glass-box, "
        "no-bolt-on flag/localization signal for pronoun ambiguity (composes atom 29618's baseline-"
        "mechanism finding). Does NOT validate topic-continuity/Centering-Continue as a general-purpose fix "
        "for flagged pronoun ambiguity -- it actively hurts on the SHIFT-dominant subpopulation this flag "
        "surfaces, which is a genuine negative result about that specific fix mechanism, not about flagging "
        "in general."),
    "hf_attribution": "n/a (MEASURED_MECHANISM decomposition; the fix-half is a genuine, well-controlled "
        "negative but is filed as a mechanism characterization alongside the flag-half positive, not as a "
        "standalone HF).",
    "fairness_verdict": ("FAIR: selective-vs-uniform is a genuine can-fail localization control (if the "
        "flag were mistargeted, selective and uniform application would differ; they don't, confirming the "
        "flag targets the right cases). Decay swept 0.5-1.0 rather than cherry-picking one setting. The "
        "6-decision corrected/broke breakdown is reported in full (0 corrected, 3 broke, 3 unaffected among "
        "the 6 divergent), not summarized away."),
    "cross_arc_overlap": ("Composes atom 29616 (base calibration primitive) and atom 29618 (this session's "
        "powered n_compatible baseline-mechanism finding, which is exactly the flag signal this cell "
        "operationalizes at threshold>=2). substrate_query.sh check found no prior-arc rediscovery at "
        "cosine>0.30 for this flag/fix decomposition specifically."),
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom2))

# =====================================================================================================
# WRITE: both atoms -> math (in seq order). Then 2 ledger entries.
# =====================================================================================================
math_after1 = A5_write(ATOMS_MATH, math_lines, atom1, "MEASURED_MECHANISM")
math_after2 = A5_write(ATOMS_MATH, [json.dumps(o, ensure_ascii=False) for o in math_after1], atom2, "MEASURED_MECHANISM")
assert math_after2[-1]["seq"] == 29619 and math_after2[-2]["seq"] == 29618
print(f"MATH ATOMS OK: {len(math_lines)} -> {len(math_after2)}; seqs 29618 (amends 29616, +0) & 29619 (composes 29616/29618, +0).")

# ---- LEDGER (2 entries) ----
ledger_now = ledger_lines
for atom, decision in [
    (atom1, "MEASURED_MECHANISM CERT +0 (amends 29616). Recompute off metrics.json confirms name-path AUC "
             "strengthens under power (0.802/0.792 vs 29616's 0.753) and pronoun margin remains a powered, "
             "trustworthy MIDDLE_BAND negative (0.536/0.627). DEFLATION: the n_compatible 'earned on both "
             "tiers' claim (0.724 baseline / 0.709 g5g6) is corrected -- 0.709 is g5g6_only.BASELINE (same "
             "mechanism, subset), not a strict_cb number; actual strict_cb n_compatible AUC on the full "
             "powered set is 0.578, confirmed to also degrade on the g5g6 subset (0.578). Signal is real "
             "but mechanism-dependent (baseline-only), not dual-tier. Symmetric anti-negativity downward "
             "correction, filed honestly."),
    (atom2, "MEASURED_MECHANISM CERT +0 (pre-registered NULL_FIX_MECHANISM branch, composes 29616/29618). "
             "Recompute off metrics.json confirms EXACTLY: flag earned+localizes (error rate by n_compatible "
             "0/17.6/27.3/44.8% vs base 26.3%, thr>=2 captures 85% of errors, selective==uniform confirms "
             "flag isn't the problem); fix (topic-continuity/Centering-Continue) HURTS (pronoun-B3 0.703-> "
             "0.677, iddem 0.719->0.684, away from oracle 0.930; 0 corrected/3 broke on 6 divergent flagged "
             "decisions; robust null across decay 0.5-1.0). Mechanism: flagged pronouns are Centering SHIFTs, "
             "not Continues -- fix needs verb-semantics/world-knowledge not yet available glass-box. No "
             "deflation needed; framing confirms exactly."),
]:
    led = dict(atom)
    led["decision"] = decision
    led["note"] = ("AUDIT-ONLY (hdi_skunkworks) independent .venv recompute off metrics.json, NOT verdict_msg "
                   "or spawn-prompt summary. 2026-08-02 batch (2 atoms, store head 29617). LOCAL-ONLY; no "
                   "origin push; no remote persist.")
    json.loads(json.dumps(led))
    line = json.dumps(led, ensure_ascii=False)
    assert "\r" not in line and "\n" not in line
    ledger_now = ledger_now + [line]

new_led = "\n".join(ledger_now) + "\n"
dl = os.path.dirname(os.path.abspath(LEDGER))
fd2, tmp2 = tempfile.mkstemp(dir=dl, suffix=".tmp"); os.close(fd2)
with open(tmp2, "w", encoding="utf-8", newline="") as f:
    f.write(new_led); f.flush(); os.fsync(f.fileno())
os.replace(tmp2, LEDGER)
assert b"\r\n" not in open(LEDGER, "rb").read(), "CRLF doubling in ledger"
vl = [json.loads(l) for l in open(LEDGER, encoding="utf-8").read().splitlines() if l.strip()]
assert len(vl) == len(ledger_lines) + 2
assert [iseq(x) for x in vl[-2:]] == [29618, 29619]
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)}; seqs 29618/29619.")
print("DONE. net_cert_delta = +0 for both (amendment + pre-registered mechanism decomposition, not new "
      "capability grants). LOCAL-ONLY; no origin push; no remote persist.")
