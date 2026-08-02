"""A5-gated LOCAL-ONLY atomize of the interactive-loop redirect's SETTLED, VET'd, load-bearing results.
AUDIT-ONLY (hdi_skunkworks). Independent .venv recompute off the raw metrics.json / gold jsonl on disk
(NOT verdict_msg strings, NOT the Director summary). No experiment authored/dispatched by this auditor.

THREE atoms, store head 29603 -> seqs 29604/29605/29606:
  29604 meta  : brain-fidelity broad-audit REFRAME (comprehension is INTERACTIVE not feed-forward). CERT-neutral.
  29605 math  : synthetic interactive-loop probe MIDDLE_PARTIAL + settling-iters NON-lever. MEASURED_MECHANISM, +0.
  29606 math  : REAL McGuffey gold -- interactive top-down loop RESOLVES quotative + by-agent passive. MEASURED_MECHANISM, +1.
                composes 29605 (synthetic origin) + 29602 (the wall this resolves).

DISK-VERIFY performed before this script banks:
  #3 metrics.json (exp_interactive_loop_real_gold_mcguffey_v1): quot OFF=0.2105/ON=0.8947/PLACEBO=0.3684 (N_hard=19),
     byagent OFF=0.0/ON=1.0/PLACEBO=0.0/NO_TD=0.4 (N=5). CONFIRMED matches Director summary EXACTLY.
     HONEST NUANCE the auditor adds: (a) quotative placebo=0.368 is ABOVE the 0.15 floor band (floor_held=False) --
     the content-specific effect is the ON-placebo gap 0.527, not a placebo-collapses-to-floor story; verdict's own
     label is FLOOR_MARGINAL_POSITION_BASELINE_NOT_LEAK. (b) the PLAIN passive arm (N=6) has PLACEBO=1.0 -- placebo
     ALSO solves it, so plain passive is NOT a clean dissociation; the load-bearing 2-way passive evidence is the
     BY-AGENT arm (N=5) where placebo collapses to 0.0 below the position baseline (NO_TD=0.4). Director correctly
     cited by-agent, not plain passive.
  #2 sweep_metrics.json (exp_interactive_extraction_situation_model_loop_probe1_v1): settling sweep content_margin
     0.113(iters3) -> 0.030(iters6) -> -0.001(iters12), 5 seeds; CONFIRMED. probe1's headline 0.15->0.55 was a
     SINGLE run; the 5-seed sweep mean at iters=3 is on_passive=0.391 -> the FRAGILITY caveat (commit c1e27b942
     "0.55 vs 0.39 run-to-run") is real and baked in. Settling is NOT the strengthening lever.
  #1 note research_brain_fidelity_broad_audit_synthesis_2026-08-01.md (commit 5b235c8f8): deflated CONTESTED-flagged
     lit-scan; best-replicated finding = interactivity (situation-model->extraction ~200ms feedback, Trueswell/
     Altmann&Kamide/Crain&Steedman) + acquisition specific-before-general; binding-by-synchrony refuted; the roadmap's
     feed-forward extraction->situation-model ORDER is non-biological. This REDIRECTED the program. CERT-neutral.

Commits verified present: 5b235c8f8, ba01892e9, 9a901e51d, 8a13fefec, c1e27b942. HEAD f014fa2d8.
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
assert not any("\r" in l for l in (math_lines[-5:] + meta_lines[-5:])), "existing atoms carry CR"
STORE_HEAD = max(max(iseq(o) for o in pm), max(iseq(o) for o in pe), max(iseq(o) for o in pl))
assert STORE_HEAD == 29603, f"expected store head 29603, got {STORE_HEAD}"
assert not any("interactive_loop_real_gold_mcguffey" in o.get("anchor_name", "") for o in pm), "resolution already atomized"
assert not any("interactive_extraction_situation_model_loop" in o.get("anchor_name", "") for o in pm), "probe already atomized"
# 29602 (wall characterization) must exist for composition
assert any(iseq(o) == 29602 for o in pm), "parent 29602 (mcguffey wall) missing"
print(f"PRE-GATE OK: store head {STORE_HEAD}; parent 29602 present; seqs 29604/29605/29606.")

# =====================================================================================================
# OFF-DISK independent recompute
# =====================================================================================================
# ---- #3 REAL McGuffey resolution ----
M3 = json.load(open("data/exp_interactive_loop_real_gold_mcguffey_v1/metrics.json", encoding="utf-8"))
s = M3["summary"]
pa = M3["per_arm"]
# quotative hard
assert abs(pa["OFF"]["quot_hard_acc"] - 0.21052631578947367) < 1e-12
assert abs(pa["ON"]["quot_hard_acc"] - 0.8947368421052632) < 1e-12
assert abs(pa["PLACEBO"]["quot_hard_acc"] - 0.3684210526315789) < 1e-12
assert pa["OFF"]["quot_hard_n"] == pa["ON"]["quot_hard_n"] == pa["PLACEBO"]["quot_hard_n"] == 19
quot_on_placebo_gap = pa["ON"]["quot_hard_acc"] - pa["PLACEBO"]["quot_hard_acc"]
assert abs(quot_on_placebo_gap - 0.5263157894736842) < 1e-12
# by-agent (the clean 2-way passive)
assert pa["OFF"]["byagent_hard_acc"] == 0.0
assert pa["ON"]["byagent_hard_acc"] == 1.0
assert pa["PLACEBO"]["byagent_hard_acc"] == 0.0
assert pa["NO_TD"]["byagent_hard_acc"] == 0.4
assert pa["OFF"]["byagent_hard_n"] == 5
# plain passive (NOT clean -- placebo also solves it)
assert pa["OFF"]["pass_hard_acc"] == 0.0
assert pa["ON"]["pass_hard_acc"] == 1.0
assert pa["PLACEBO"]["pass_hard_acc"] == 1.0, "plain passive placebo expected 1.0 (not a clean dissociation)"
assert pa["OFF"]["pass_hard_n"] == 6
# floor/placebo flags
assert s["placebo_collapses"] is True and s["not_a_leak"] is True
assert s["byagent_floor_held"] is True and s["byagent_pass"] is True
assert s["floor_held"] is False, "quotative floor NOT held (placebo 0.368 > 0.15 band) -- honest nuance"
assert abs(s["gold_filler_nominal_rate"] - 0.9375) < 1e-12  # tagger diagnostic
# gold cardinality on disk
n_byagent_gold = len(load("data/eval_gold_mention_role_mcguffey_v1/gold_passive_byagent_verified_v1.jsonl"))
n_quot_gold = len(load("data/eval_gold_mention_role_mcguffey_v1/gold_quotative_verified_v1.jsonl"))
assert n_byagent_gold == 5 and n_quot_gold == 20, (n_byagent_gold, n_quot_gold)
m3_sha = sha16("data/exp_interactive_loop_real_gold_mcguffey_v1/metrics.json")
cell3_sha = sha16("experiments/exp_interactive_loop_real_gold_mcguffey_v1.py")
print(f"#3 OFF-DISK OK: quot OFF={pa['OFF']['quot_hard_acc']:.4f} ON={pa['ON']['quot_hard_acc']:.4f} "
      f"PLACEBO={pa['PLACEBO']['quot_hard_acc']:.4f} (N=19, ON-placebo gap={quot_on_placebo_gap:.3f}); "
      f"byagent OFF=0 ON=1 PLACEBO=0 NO_TD=0.4 (N=5); plain passive placebo=1.0 (NOT clean). "
      f"floor_held(quot)=False -> placebo above 0.15 band, honest. metrics_sha={m3_sha}")

# ---- #2 synthetic probe + settling sweep ----
M2 = json.load(open("data/exp_interactive_extraction_situation_model_loop_probe1_v1/sweep_metrics.json", encoding="utf-8"))
rows = {r["settling_iters"]: r for r in M2["rows"]}
assert abs(rows[3]["content_margin"] - 0.11299999058246613) < 1e-9
assert abs(rows[6]["content_margin"] - 0.02999999821186064) < 1e-9
assert rows[12]["content_margin"] < 0.0
assert abs(rows[3]["off_passive_acc"] - 0.15225000083446502) < 1e-9  # feed-forward reproduces passive inversion ~0.15
assert abs(rows[3]["on_passive_acc"] - 0.39074999690055845) < 1e-9   # 5-seed mean 0.391 (single-run headline was 0.55)
assert rows[3]["placebo_ok"] is True and rows[3]["floor_held"] is True
assert M2["config"]["n_seeds"] == 5
m2_sha = sha16("data/exp_interactive_extraction_situation_model_loop_probe1_v1/sweep_metrics.json")
print(f"#2 OFF-DISK OK: settling content_margin {rows[3]['content_margin']:.3f}->{rows[6]['content_margin']:.3f}"
      f"->{rows[12]['content_margin']:.4f} (5 seeds); off_passive=0.152 on_passive(iters3,5seed-mean)=0.391 "
      f"(single-run headline 0.55 = fragile). settling NOT the lever. sweep_sha={m2_sha}")

# ---- #1 audit note ----
note1 = "notes/research_brain_fidelity_broad_audit_synthesis_2026-08-01.md"
n1_sha = sha16(note1)
txt = open(note1, encoding="utf-8").read()
assert "INTERACTIVE" in txt and "feed-forward" in txt.lower() and "Trueswell" in txt and "Altmann" in txt
assert "REFUTED" in txt  # binding-by-synchrony
print(f"#1 OFF-DISK OK: audit note present, interactivity+refuted-synchrony content confirmed. note_sha={n1_sha}")

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
ts_day = "2026-08-01"


def A5_write(path, lines, new_atom, tier_expect, delta_expect):
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
# ATOM 29604 -- META: brain-fidelity broad-audit REFRAME (CERT-neutral)
# =====================================================================================================
AID1 = ("meta::brain_fidelity_broad_audit_synthesis_2026_08_01_COMPREHENSION_IS_INTERACTIVE_NOT_FEED_FORWARD_"
    "situation_model_feeds_BACK_to_extraction_within_200ms_Trueswell_Altmann_Kamide_Crain_Steedman_so_the_"
    "roadmaps_strict_feed_forward_extraction_then_situation_model_ORDER_is_NON_biological_biggest_architectural_"
    "fidelity_gap_REDIRECTED_the_program_toward_an_interactive_loop_ALSO_binding_by_synchrony_LARGELY_REFUTED_"
    "Shadlen_Ray_do_not_justify_binding_via_synchrony_while_structure_content_factorization_for_generalization_"
    "entorhinal_TEM_and_entity_first_specific_before_general_acquisition_VINDICATED_deflated_lit_scan_CONTESTED_"
    "flagged_best_replicated_are_interactivity_and_acquisition_order_binding_mixed_selectivity_are_active_"
    "research_CERT_neutral_methodology_reframe_LOCAL_ONLY")
assert AID1 not in existing_ids
HEAD1 = ("METHODOLOGY / ROADMAP-REFRAME (CERT-neutral, MM_TENTATIVE_SYNTHESIS): the broad brain-fidelity audit's "
    "KEY reusable finding = COMPREHENSION IS INTERACTIVE, NOT strictly FEED-FORWARD. Situation-model information "
    "(plausibility, discourse referents, verb-driven expectations) feeds BACK to constrain extraction/parsing "
    "within ~200ms (Trueswell/Tanenhaus/Garnsey 1994; Altmann&Kamide 1999; Crain&Steedman). Our roadmap's strict "
    "feed-forward extraction -> situation-model ORDER is therefore NON-biological -- the single biggest "
    "architectural fidelity gap, baked into the whole plan. This audit REDIRECTED the program toward an "
    "interactive extraction<->situation-model loop. Secondary well-replicated finding: acquisition is "
    "SPECIFIC-before-general (Tomasello verb-islands; de Villiers; entity-tracking before abstract role-"
    "assignment) = VINDICATES the entity-identity-first competency ordering. Fidelity CORRECTIONS: binding-by-"
    "SYNCHRONY is LARGELY REFUTED as a general mechanism (Shadlen&Movshon 1999; Ray&Maunsell) -> do NOT justify "
    "our binding via synchrony; but structure/content FACTORIZATION-for-generalization (entorhinal/TEM; Bernardi "
    "2020) is VINDICATED for the generalization property we proved (while noting the brain's actual bind is "
    "CONJUNCTIVE/mixed-selective, not a clean orthogonal algebraic bind).")
atom1 = {
    "atom_id": AID1, "seq": 29604, "op": "atomize", "corpus": "meta",
    "tier": "MM_TENTATIVE_SYNTHESIS", "cert_status": "methodology (CERT-neutral)",
    "cert_class": "brain_fidelity_reframe_comprehension_is_interactive_not_feed_forward",
    "grade": "META_ROADMAP_REFRAME_INTERACTIVE_NOT_FEEDFORWARD_synchrony_refuted_factorization_and_entity_first_vindicated",
    "verdict": "MEASURED_MECHANISM", "anchor_name": "research_brain_fidelity_broad_audit_synthesis_2026_08_01",
    "cell": "notes/research_brain_fidelity_broad_audit_synthesis_2026-08-01.md",
    "cell_commit": "5b235c8f8", "cell_content_sha256_16": n1_sha,
    "metrics_path": note1, "metrics_sha256_16": n1_sha,
    "headline": HEAD1,
    "key_metrics": {
        "rule": "comprehension_is_interactive_situation_model_feeds_back_to_extraction_within_200ms",
        "roadmap_correction": "strict_feed_forward_extraction_then_situation_model_ORDER_is_non_biological_biggest_gap",
        "vindicated_1": "acquisition_specific_before_general_supports_entity_identity_first_competency_ordering",
        "vindicated_2": "structure_content_factorization_for_generalization_entorhinal_TEM",
        "refuted": "binding_by_synchrony_largely_refuted_do_not_justify_binding_via_synchrony",
        "caveat_binding": "brains_actual_bind_is_conjunctive_mixed_selective_not_clean_orthogonal_algebraic",
        "top_missing_mechanisms_flagged": ["precision_weighting_inverse_variance_reliability_gain", "top_down_interactivity", "multi_level_prediction", "mixed_selectivity_expressivity"],
        "sources": ["Trueswell_Tanenhaus_Garnsey_1994", "Altmann_Kamide_1999", "Crain_Steedman", "Zwaan_Radvansky", "Kintsch_CI", "Shadlen_Movshon_1999", "Ray_Maunsell", "Bernardi_2020", "Tomasello", "de_Villiers"],
    },
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("AUDIT-ONLY: verified the synthesis note exists on disk (commit 5b235c8f8, sha "
        + n1_sha + ") and that the interactivity + synchrony-refuted + factorization/entity-first-vindicated "
        "content is present as summarized. This is a lit-scan SYNTHESIS not an experimental measurement -- banked "
        "CERT-neutral as a methodology/roadmap reframe, deflated and CONTESTED-flagged per the note itself."),
    "composes_seq": [], "corrects_seq": [], "amends_seq": [],
    "cert_delta": 0, "net_cert_delta": 0, "store_head_at_write": STORE_HEAD,
    "honest_scope": ("A DEFLATED lit-scan synthesis (all sub-scan claims CITED@/REASONED@, ESTABLISHED/CONTESTED "
        "flagged) -- treat rankings as HYPOTHESES not settled fact. The best-REPLICATED findings are the "
        "interactivity (~200ms top-down feedback) and the specific-before-general acquisition order. The binding "
        "/ mixed-selectivity fidelity claims are ACTIVE-RESEARCH / contested. The 'highest-leverage = interactive "
        "entity-rep loop' recommendation is Director SYNTHESIS (REASONED), not an established result. This atom "
        "banks the roadmap REFRAME, not a proven capability. Its downstream experimental payoff is atom 29605 "
        "(synthetic proof-of-mechanism) and 29606 (real-text resolution)."),
    "framing_correction": ("Confirms the Director framing that this audit REDIRECTED the program; no inflation. "
        "The atom is careful to keep the interactivity finding (well-replicated) distinct from the binding/mixed-"
        "selectivity findings (contested) so downstream work does not over-weight the latter."),
    "revival_criterion": ("n/a (standing roadmap-reframe / methodology anchor). It graduates from 'reframe' to "
        "'validated redirect' exactly to the extent the interactive-loop experiments (29605 synthetic, 29606 "
        "real) hold -- which they partially/substantively do; a clean torch precision-weighted loop win on real "
        "text at larger N would fully vindicate it."),
    "hf_attribution": "n/a", "fairness_verdict": "n/a (methodology/lit-scan atom).",
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom1))

# =====================================================================================================
# ATOM 29605 -- MATH: synthetic interactive-loop probe (MIDDLE_PARTIAL) + settling NON-lever. +0.
# =====================================================================================================
AID2 = ("math::interactive_extraction_situation_model_loop_probe1_v1_MEASURED_MECHANISM_synthetic_proof_of_"
    "mechanism_interactive_top_down_loop_lifts_PASSIVES_specifically_feed_forward_reproduces_the_passive_"
    "inversion_off_passive_0p152_while_active_0p86_and_the_interactive_top_down_loop_lifts_passive_to_0p39_"
    "5seed_mean_single_run_headline_was_0p55_FRAGILE_run_to_run_placebo_clean_floor_held_precision_weighting_"
    "earns_keep_but_PARTIAL_below_0p75_hardpass_on_CHEAP_SYNTHETIC_AND_SETTLING_ITERS_IS_NOT_THE_STRENGTHENING_"
    "LEVER_content_margin_degrades_0p113_iters3_to_0p030_iters6_to_neg0p001_iters12_one_shot_additive_top_down_"
    "beats_iterative_PE_settling_synthetic_proof_of_concept_for_the_interactive_redirect_real_payoff_is_29606_"
    "no_new_cert_here_LOCAL_ONLY")
assert AID2 not in existing_ids
HEAD2 = ("MEASURED_MECHANISM (CERT +0; synthetic proof-of-mechanism -- the REAL cert is atom 29606). On CHEAP "
    "SYNTHETIC data, the interactive top-down loop produces a REAL but PARTIAL and RUN-TO-RUN-FRAGILE passive-"
    "specific lift: feed-forward alone reproduces the human-like passive-role inversion (off_passive_acc=0.152 "
    "vs off_active_acc=0.86, floor held), and adding one-shot top-down situation-model feedback lifts passives "
    "specifically to on_passive=0.391 (5-seed mean; the probe1 single-run headline of 0.55 is one draw of a "
    "fragile 0.39-0.55 spread), placebo clean, precision-weighting earns keep. It is NOT a hard pass (0.39-0.55 "
    "< 0.75). SECOND, load-bearing NEGATIVE folded in: SETTLING-ITERATIONS IS NOT THE STRENGTHENING LEVER -- a "
    "5-seed sweep shows the content margin DEGRADES with more settling (0.113 @ iters=3 -> 0.030 @ iters=6 -> "
    "-0.001 @ iters=12); more iterative PE-settling WASHES OUT the content effect, so one-shot additive top-down "
    "is better than iterating. This is the synthetic proof-of-concept that motivated the real-text test; the "
    "capability cert is carried by 29606, so this atom is banked CERT-neutral to avoid double-counting the same "
    "mechanism across synthetic + real.")
atom2 = {
    "atom_id": AID2, "seq": 29605, "op": "atomize", "corpus": "math",
    "tier": "MEASURED_MECHANISM", "cert_status": "proven-bound",
    "grade": "MM_synthetic_interactive_loop_partial_passive_lift_fragile_plus_settling_iters_non_lever_negative",
    "verdict": "MIDDLE_PARTIAL", "anchor": "interactive_extraction_situation_model_loop_probe1_v1",
    "anchor_name": "interactive_extraction_situation_model_loop_probe1_v1",
    "cell": "experiments/ (interactive_extraction_situation_model_loop_probe1_v1)",
    "cell_commit": "ba01892e9(probe1_landed),8a13fefec(settling_sweep),c1e27b942(settling_negative_verdict)",
    "cell_content_sha256_16": "NA_sweep_metrics", "metrics_path": "data/exp_interactive_extraction_situation_model_loop_probe1_v1/sweep_metrics.json",
    "metrics_sha256_16": m2_sha,
    "headline": HEAD2,
    "key_metrics": {
        "cell_verdict": "MIDDLE_PARTIAL", "auditor_tier": "MEASURED_MECHANISM", "cert_delta": 0,
        "off_passive_acc": 0.15225, "off_active_acc": 0.8595,
        "on_passive_acc_5seed_mean_iters3": 0.39075, "probe1_single_run_headline": 0.55,
        "fragility_caveat": "single-run 0.55 vs 5-seed mean 0.39 -- run-to-run variable, NOT a stable 0.55",
        "hard_pass_threshold": 0.75, "is_hard_pass": False,
        "settling_content_margin_by_iters": {"3": 0.113, "6": 0.030, "12": -0.001},
        "settling_verdict": "NEGATIVE_lever_more_settling_washes_out_content_effect_one_shot_additive_top_down_better",
        "n_seeds": 5, "placebo_ok": True, "floor_held": True,
    },
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("AUDIT-ONLY .venv recompute off sweep_metrics.json (NOT verdict_msg): content_margin "
        "0.113/0.030/-0.001 at settling_iters 3/6/12 (5 seeds) confirmed exactly; off_passive_acc=0.15225, "
        "on_passive_acc(iters3,5-seed mean)=0.39075 confirmed. The 0.15->0.55 probe1 headline is a SINGLE run; the "
        "5-seed sweep mean is 0.391 -- the fragility caveat is disk-verified, not inherited from the summary."),
    "composes_seq": [], "corrects_seq": [], "amends_seq": [],
    "cert_delta": 0, "net_cert_delta": 0, "store_head_at_write": STORE_HEAD,
    "honest_scope": ("CHEAP SYNTHETIC construction (outcomes can be construction-influenced). The passive-specific "
        "lift is REAL, PARTIAL (0.39-0.55, below the 0.75 hard-pass bar) and RUN-TO-RUN FRAGILE. Banked CERT-"
        "NEUTRAL on purpose: it is the proof-of-concept that MOTIVATED the real-text test; the capability cert is "
        "carried by 29606 (real McGuffey gold) -- granting cert to both the synthetic proof and the real "
        "confirmation of the SAME interactive-loop mechanism would double-count. The SETTLING-ITERS NEGATIVE is a "
        "genuine proven non-lever (more settling degrades the content margin), useful as a standing design rule: "
        "prefer one-shot additive top-down over iterative PE-settling for this mechanism."),
    "framing_correction": ("Confirms the Director MIDDLE_PARTIAL framing and the 'settling is not the lever' "
        "negative. Auditor SHARPENS the honesty: the 0.55 in the probe1 headline is a single fragile draw; the "
        "stable 5-seed estimate is ~0.39 -- cite the range 0.39-0.55, not 0.55, as the synthetic lift."),
    "revival_criteria": ("Promotion to a fresh cert requires a NON-fragile (tight cross-seed) lift on a REGIME "
        "with real-text stakes -- which 29606 supplies for real McGuffey constructions. On synthetic, a clean "
        "torch precision-weighted loop that lifts passives above ~0.75 with cv<0.15 across seeds would upgrade "
        "this from MIDDLE_PARTIAL, but synthetic construction-determinism caps its cert value regardless."),
    "primitive_assessment": ("No new primitive. Characterizes the interactive top-down situation-model->extraction "
        "loop on synthetic: a real partial passive-specific lift, best at MINIMAL settling (one-shot additive), "
        "degrading with iterative settling. Motivates 29606."),
    "hf_attribution": "n/a (MIDDLE_PARTIAL positive with an embedded settling-lever NEGATIVE, not a structural HF).",
    "fairness_verdict": ("Fair on its own terms (real feed-forward baseline reproduces the passive inversion; "
        "placebo clean; floor held; 5-seed). The limiting factor is REGIME (cheap synthetic), not test design -- "
        "hence the CERT-neutral disposition and the deferral of cert to the real-text atom."),
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom2))

# =====================================================================================================
# ATOM 29606 -- MATH: REAL McGuffey resolution. MEASURED_MECHANISM +1. composes 29605 + 29602.
# =====================================================================================================
AID3 = ("math::interactive_loop_real_gold_mcguffey_v1_MEASURED_MECHANISM_REAL_TEXT_who_did_what_ORDER_ne_ROLE_"
    "WALL_RESOLVED_on_verified_McGuffey_gold_the_interactive_top_down_situation_model_loop_resolves_BOTH_"
    "constructions_where_linear_order_provably_fails_QUOTATIVE_N19_OFF_0p211_ON_0p895_PLACEBO_0p368_content_"
    "specific_ON_minus_placebo_gap_0p527_and_BY_AGENT_PASSIVE_N5_exploratory_OFF_0p000_ON_1p000_PLACEBO_0p000_"
    "collapses_below_position_baseline_NO_TD_0p400_strongest_dissociation_mapping_LEARNED_ridge_logreg_no_bolt_"
    "on_parser_features_supplied_mapping_learned_HONEST_SCOPE_small_N_numpy_core_mechanism_NOT_full_graded_PE_"
    "precision_torch_loop_this_is_the_ROLE_EXTRACTION_wall_resolved_NOT_full_comprehension_plain_passive_N6_"
    "placebo_1p000_NOT_a_clean_dissociation_so_load_bearing_passive_evidence_is_the_byagent_arm_composes_29605_"
    "synthetic_origin_and_29602_the_wall_LOCAL_ONLY")
assert AID3 not in existing_ids
HEAD3 = ("MEASURED_MECHANISM (CERT +1, proven-bound). On VERIFIED REAL McGuffey mention/role gold, the interactive "
    "top-down situation-model loop RESOLVES BOTH order!=role constructions where LINEAR ORDER provably fails -- "
    "the who-did-what role-extraction wall (characterized in atom 29602) is CROSSED. QUOTATIVE (N=19 hard): OFF "
    "0.211 -> ON 0.895, with placebo 0.368 -- the content-SPECIFIC effect is the ON-minus-placebo gap of 0.527 "
    "(placebo lifts modestly above OFF but ON is far above both; verdict's own label FLOOR_MARGINAL_POSITION_"
    "BASELINE_NOT_LEAK). BY-AGENT PASSIVE (N=5, EXPLORATORY): OFF 0.000 -> ON 1.000, placebo 0.000 COLLAPSES to "
    "zero -- BELOW the position baseline (NO_TD=0.400) -- the strongest, cleanest dissociation. The mention/role "
    "mapping is LEARNED (ridge-logreg): features are SUPPLIED but the mapping is LEARNED, respecting the no-bolt-"
    "on-parser lock. This is the brain-foundational INTERACTIVE-loop redirect (atom 29604) paying off on real "
    "text: top-down feedback from the situation model resolves constructions a feed-forward linear reader cannot. "
    "HONEST SCOPE baked in: (1) small N (quotative 19 = moderate; by-agent 5 = exploratory); (2) the mechanism "
    "here is a numpy ridge-logreg top-down-construction-mapping, NOT the full graded-PE/precision torch loop; "
    "(3) this resolves ROLE-EXTRACTION on these specific constructions, NOT full comprehension; (4) the PLAIN "
    "passive arm (N=6) has placebo=1.000 -- placebo ALSO solves it, so plain passive is NOT a clean dissociation "
    "and the load-bearing 2-way passive evidence is the BY-AGENT arm, not plain passive.")
atom3 = {
    "atom_id": AID3, "seq": 29606, "op": "atomize", "corpus": "math",
    "tier": "MEASURED_MECHANISM", "cert_status": "proven-bound",
    "grade": "MM_real_text_order_ne_role_wall_resolved_interactive_top_down_loop_quotative_and_byagent_learned_mapping",
    "verdict": "HARD_PASS_INTERACTIVE_RESOLVES_QUOTATIVE_AND_BYAGENT_auditor_scoped_MEASURED_MECHANISM",
    "anchor": "interactive_loop_real_gold_mcguffey_v1", "anchor_name": "interactive_loop_real_gold_mcguffey_v1",
    "cell": "experiments/exp_interactive_loop_real_gold_mcguffey_v1.py",
    "cell_commit": "9a901e51d", "cell_content_sha256_16": cell3_sha,
    "metrics_path": "data/exp_interactive_loop_real_gold_mcguffey_v1/metrics.json", "metrics_sha256_16": m3_sha,
    "headline": HEAD3,
    "key_metrics": {
        "cell_verdict": "HARD_PASS_INTERACTIVE_RESOLVES_QUOTATIVE_AND_BYAGENT", "auditor_tier": "MEASURED_MECHANISM", "cert_delta": 1,
        "quot_off": 0.21052631578947367, "quot_on": 0.8947368421052632, "quot_placebo": 0.3684210526315789,
        "quot_on_minus_placebo_gap": 0.5263157894736842, "quot_n_hard": 19, "quot_floor_held": False,
        "quot_floor_note": "placebo 0.368 is ABOVE the 0.15 floor band -> content-specific effect = ON-placebo gap, not placebo-collapses-to-floor",
        "byagent_off": 0.0, "byagent_on": 1.0, "byagent_placebo": 0.0, "byagent_no_td_position_baseline": 0.4,
        "byagent_n": 5, "byagent_tag": "EXPLORATORY_small_N", "byagent_dissociation": "placebo collapses to 0.0 BELOW position baseline 0.4 = strongest",
        "plain_passive_off": 0.0, "plain_passive_on": 1.0, "plain_passive_placebo": 1.0, "plain_passive_n": 6,
        "plain_passive_note": "PLACEBO=1.0 -> NOT a clean dissociation; excluded from load-bearing claim",
        "mapping": "ridge_logreg_features_supplied_mapping_LEARNED_no_bolt_on_parser",
        "tagger_gold_nominal_rate": 0.9375, "gold_quotative_n_disk": 20, "gold_byagent_n_disk": 5,
    },
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("AUDIT-ONLY .venv recompute off metrics.json per_arm (NOT verdict_msg): quot OFF="
        "0.2105/ON=0.8947/PLACEBO=0.3684 (N=19, ON-placebo gap 0.526); byagent OFF=0/ON=1/PLACEBO=0/NO_TD=0.4 "
        "(N=5); plain passive OFF=0/ON=1/PLACEBO=1.0 (N=6 -> NOT clean). Gold cardinality checked on disk: "
        "quotative 20 lines, by-agent 5 lines. All match Director summary EXACTLY. Auditor ADDED two honesty "
        "checks not in the verdict label: (a) quotative floor_held=False (placebo above 0.15 band) -> reframed "
        "the win as the ON-placebo content gap; (b) plain-passive placebo=1.0 -> excluded plain passive from the "
        "load-bearing claim, keeping by-agent as the clean 2-way passive evidence."),
    "composes_seq": [29605, 29602], "corrects_seq": [], "amends_seq": [],
    "cert_delta": 1, "net_cert_delta": 1, "store_head_at_write": STORE_HEAD,
    "honest_scope": ("SMALL N: quotative 19 (moderate), by-agent passive 5 (EXPLORATORY -- treat the 0->1 "
        "dissociation as directional, not a precise rate). The resolving mechanism is a NUMPY RIDGE-LOGREG top-"
        "down-construction mapping (features supplied, mapping learned = respects the no-bolt-on-parser lock), "
        "NOT the full graded-PE/precision torch loop -- so this is the CORE mechanism validated on real text, not "
        "the full architecture. It resolves ROLE-EXTRACTION on these specific order!=role constructions "
        "(quotative speaker=agent; by-agent passive), NOT full comprehension. The PLAIN passive arm (N=6) is NOT "
        "a clean dissociation (placebo=1.0, i.e. the position baseline already solves it here) and is deliberately "
        "EXCLUDED from the load-bearing claim. Do NOT cite this as 'comprehension solved' or 'the full interactive "
        "loop'; cite it as: on real McGuffey gold, a learned top-down construction mapping crosses the linear-"
        "order-fails role-extraction wall for quotative (moderate N) and by-agent passive (exploratory N)."),
    "framing_correction": ("Matches the Director HARD_PASS framing on the load-bearing numbers; auditor DEFLATES "
        "the tier from the cell's HARD_PASS to MEASURED_MECHANISM (proven-bound) given small N + numpy-core-not-"
        "full-torch-loop + role-extraction-not-comprehension. Two auditor sharpenings vs the cell's verdict "
        "label: (1) quotative placebo (0.368) is NOT at the floor band (0.15) -- the honest content-specific "
        "effect is the ON-placebo gap (0.527), not a placebo-collapses story; the by-agent arm is where placebo "
        "cleanly collapses. (2) the PLAIN passive arm's ON=1.0 is NOT evidence for the loop -- its placebo is "
        "ALSO 1.0 -- so only the by-agent 2-way construction counts as passive evidence. Neither correction "
        "weakens the headline; both keep it honest and correctly scoped."),
    "revival_criteria": ("(1) LARGER gold N (esp. by-agent passive beyond 5) to convert the exploratory 0->1 "
        "dissociation into a precise rate. (2) Replace the numpy ridge-logreg core with the full graded-PE/"
        "precision-weighted torch loop and re-confirm on real text -- promotion to CHAIN_GRADE requires the FULL "
        "mechanism holding with tight cross-seed stability, not the numpy stand-in. (3) Extend beyond quotative + "
        "by-agent passive to other order!=role constructions (object-relatives, clefts) to show the loop "
        "generalizes across the construction family, not just these two."),
    "primitive_assessment": ("Validates, on REAL text, the interactive top-down situation-model->extraction "
        "mapping as the mechanism that crosses the order!=role wall (29602). The learned ridge-logreg mapping is "
        "the readout of that top-down constraint; the full graded-PE/precision loop (29604 roadmap) is the intended "
        "scaled form. This is the real-text payoff of the 29604 interactive-not-feed-forward redirect and the "
        "29605 synthetic proof-of-concept."),
    "hf_attribution": "n/a (positive resolution, tier-deflated to MEASURED_MECHANISM for scope, not a negative).",
    "fairness_verdict": ("FAIR on the load-bearing arms: real verified gold, OFF/ON/PLACEBO/NO_TD contrast, learned "
        "(not bolted-on) mapping, feed-forward/position baselines present. The by-agent arm is the cleanest "
        "dissociation (placebo below position baseline) but smallest N; the quotative arm is moderate N with a "
        "large ON-placebo content gap though placebo is above the floor band. The plain passive arm is correctly "
        "excluded as non-discriminating (placebo=1.0). Limiting factors are N and the numpy-core-not-full-loop "
        "mechanism, both scoped -- not a design flaw."),
    "cross_arc_overlap": ("Directly RESOLVES the wall that atom 29602 CHARACTERIZED (the who-did-what agent-"
        "inversion error confined to quotative + passive on McGuffey gold). Complementary to consolidated_reader_"
        "passive_mechanism_heldout (substrate's own learned passive) and distinct from the off-the-shelf-parser "
        "failure characterization in 29602. No unrelated prior-arc rediscovery."),
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom3))

# =====================================================================================================
# WRITE: atom1 -> meta; atom2, atom3 -> math (in seq order). Then 3 ledger entries.
# =====================================================================================================
meta_after = A5_write(ATOMS_META, meta_lines, atom1, "MM_TENTATIVE_SYNTHESIS", 0)
print(f"META ATOMS OK: {len(meta_lines)} -> {len(meta_after)}; seq 29604 CERT-neutral.")

math_after1 = A5_write(ATOMS_MATH, math_lines, atom2, "MEASURED_MECHANISM", 0)
math_after2 = A5_write(ATOMS_MATH, [json.dumps(o, ensure_ascii=False) for o in math_after1], atom3, "MEASURED_MECHANISM", 1)
assert math_after2[-1]["seq"] == 29606 and math_after2[-2]["seq"] == 29605
print(f"MATH ATOMS OK: {len(math_lines)} -> {len(math_after2)}; seqs 29605 (+0) & 29606 (+1).")

# ---- LEDGER (3 entries) ----
ledger_now = ledger_lines
for atom, decision in [
    (atom1, "MM_TENTATIVE_SYNTHESIS CERT +0 (CERT-neutral methodology/roadmap reframe). Verified the audit-synthesis "
             "note on disk (commit 5b235c8f8). KEY reusable finding: comprehension is INTERACTIVE not feed-forward "
             "(situation-model feeds back to extraction ~200ms) -> the roadmap's feed-forward ORDER is non-biological; "
             "this REDIRECTED the program. Deflated, CONTESTED-flagged; binding-by-synchrony refuted, factorization-"
             "for-generalization + entity-first acquisition vindicated. No cert (lit-scan synthesis)."),
    (atom2, "MEASURED_MECHANISM CERT +0 (synthetic proof-of-mechanism; cert deferred to 29606 to avoid double-count). "
             "Recompute off sweep_metrics.json confirms: interactive top-down loop lifts passives specifically "
             "(off_passive 0.152 -> on_passive 0.39-0.55, fragile; single-run headline 0.55 vs 5-seed mean 0.39), "
             "placebo clean, floor held, PARTIAL (below 0.75). Embedded NEGATIVE: settling-iters is NOT the lever "
             "(content margin 0.113->0.030->-0.001); one-shot additive top-down beats iterative PE-settling."),
    (atom3, "MEASURED_MECHANISM CERT +1 (proven-bound; deflated from the cell's HARD_PASS for scope). Recompute off "
             "metrics.json per_arm confirms EXACTLY: on REAL McGuffey gold the interactive top-down loop resolves "
             "QUOTATIVE (N=19, OFF 0.211/ON 0.895/placebo 0.368, content gap 0.527) and BY-AGENT PASSIVE (N=5 "
             "exploratory, OFF 0/ON 1/placebo 0 collapsing below position baseline 0.4). Mapping LEARNED (ridge-logreg, "
             "no bolt-on). Auditor sharpenings: quotative floor NOT held (placebo above 0.15 band) so the win = ON-"
             "placebo gap; PLAIN passive (N=6) placebo=1.0 so EXCLUDED as non-clean. Resolves the 29602 wall; composes "
             "29605+29602. Scope: small N, numpy-core-not-full-torch-loop, role-extraction not full comprehension."),
]:
    led = dict(atom)
    led["decision"] = decision
    led["note"] = ("AUDIT-ONLY (hdi_skunkworks) independent .venv recompute off metrics.json / gold jsonl / note, "
                   "NOT verdict_msg or Director summary. Interactive-loop redirect batch (3 atoms, store head 29603). "
                   "LOCAL-ONLY; no origin push; no remote persist.")
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
assert len(vl) == len(ledger_lines) + 3
assert [iseq(x) for x in vl[-3:]] == [29604, 29605, 29606]
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)}; seqs 29604/29605/29606.")
print("DONE. net_cert_delta = +1 (29606 only). LOCAL-ONLY; no origin push; no remote persist.")
