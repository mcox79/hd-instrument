"""A5-gated LOCAL-ONLY atomize: exp_learned_meaning_frontend_realslice_v1 (commit 33b86bfc2).
tier=MEASURED_MECHANISM / proven-bound. Cell verdict MIDDLE (borderline positive). Auditor SCOPES DOWN:
the in-vocab lift (+0.1497 converged) is MEMORIZATION-INCLUSIVE (in-vocab eval == train set) and does
NOT generalize -- independent held-out-TRIPLE recompute (3 seeds) gives converged 0.106/0.107/0.157 vs
frozen 0.324/0.326/0.328 (below frozen AND below chance 0.171), even for the seen-concept-new-triple
subset (conv 0.062-0.102). The 'meaning is learnable SCALES to real data in-vocab' read is a train-fit,
not generalizable linearly-decodable structure. The thin-meaning wall STANDS at real scale. Composes
29556 (toy, in-vocab construction-determined, held-out decays to frozen) + 29557 (readout linearity).

INDEPENDENT RECOMPUTE (.venv, off-disk + re-run):
 - Reproduced the FULL run bit-close (metrics on disk was a STALE SMOKE; re-ran --full): verdict MIDDLE,
   frozen_fine 0.329, converged_linear 0.4787 (CI [0.4465,0.5111]), lift +0.1497, shuffled 0.0536 (sep
   +0.4251), glass 32/97=0.330<0.34 => glass_moves_wall FALSE, heldout-concept converged lift -0.2048,
   MLP collapses ~0.08. Matches the commit message to 4 decimals => deterministic.
 - VET#1 CONVERGED-vs-GD CONFIRMED: ClosedFormLinear solves (Xa^T Xa + lam I)W = Xa^T Y with lam=wd*n/2,
   which is EXACTLY the stationary point of the GD arm's objective (1/n)||XW-Y||^2+(wd/2)||W||^2 -> the
   0.4787 is the genuine converged optimum; the GD curve climbs monotonically 0.256(512)->0.350(1024),
   still rising toward it (not plateaued) => initial HARD_FAIL WAS under-training. BUT this converged
   optimum is a TRAIN-FIT optimum.
 - VET#2 NOT-MEMORIZATION REFUTED (load-bearing): the shuffled control (0.0536) only rules out a
   relation-MARGINAL shortcut (a memorizing map ALSO fails shuffled-on-true). The memorization question
   needs a held-out-TRIPLE split. Fit ridge on 80% of triples, eval FINE discrimination on held-out 20%:
   converged 0.106/0.107/0.157 (seeds 555/777/999) vs frozen 0.324/0.326/0.328 -> lift ~ -0.20, BELOW
   frozen and BELOW chance. Seen-concept-new-triple subset: conv 0.062/0.086/0.102. => the +0.1497
   in-vocab lift is ENTIRELY memorization/train-fit; the generalizable linearly-decodable component is
   ~0/negative. (over-determination 1522 pairs vs 308 dims does NOT rescue generalization.)
 - VET#3 SCALE-ATTENUATION reinterpreted: real (smoke half-scale converged lift 0.4253 -> full 0.1497)
   but this is the MEMORIZATION FRACTION shrinking as n grows past input_dim, NOT 'signal needs more
   capacity'. More capacity would memorize MORE (higher train in-vocab), not generalize. Grounding /
   richer meaning is the lever (consistent with the ARC binding-wall).
"""
import json, os, time, tempfile, datetime, hashlib

ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

with open(ATOMS, encoding="utf-8") as f:
    atom_lines = [l for l in f.read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]
assert len(parsed) == 29554, f"expected 29554 atoms pre-write, got {len(parsed)}"
existing_ids = {o.get("atom_id") for o in parsed if o.get("atom_id")}
assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR -- investigate"

with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]
lp = [json.loads(l) for l in ledger_lines]
last_seq = [o["seq"] for o in lp if "seq" in o][-1]
assert last_seq == 29557, f"expected ledger last seq 29557, got {last_seq}"
NEW_SEQ = 29558
print(f"PRE-GATE: {len(parsed)} atoms load-valid; ledger last seq {last_seq}; NEW_SEQ {NEW_SEQ}.")

M = json.load(open("data/exp_learned_meaning_frontend_realslice_v1/metrics.json", encoding="utf-8"))
assert M["verdict"] == "MIDDLE" and M["run_mode"] == "full"
assert abs(M["frozen_fine_invocab"] - 0.329) < 1e-6
assert abs(M["converged_linear_fine_invocab"] - 0.4787) < 1e-6
assert abs(M["in_vocab_fine_lift_over_frozen_converged"] - 0.1497) < 1e-6
assert abs(M["converged_shuffled_fine_invocab"] - 0.0536) < 1e-6
assert M["glass_moves_wall"] is False
assert abs(M["heldout_fine_lift_over_frozen_converged"] - (-0.2048)) < 1e-6
assert abs(M["chance_fine"] - 0.171) < 1e-6
print("OFF-DISK OK: MIDDLE full; frozen 0.329; converged 0.4787; lift 0.1497; shuf 0.0536; "
      "glass_moves_wall False; heldout-concept lift -0.2048.")

cell_sha16 = hashlib.sha256(open("experiments/exp_learned_meaning_frontend_realslice_v1.py", "rb").read()).hexdigest()[:16]
metrics_sha16 = hashlib.sha256(open("data/exp_learned_meaning_frontend_realslice_v1/metrics.json", "rb").read()).hexdigest()[:16]
assert cell_sha16 == "1e0335b2f4f1fb72", cell_sha16
assert metrics_sha16 == "3a8f94860ea0b70f", metrics_sha16

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
ts_day = "2026-07-25"

AID = ("math::learned_meaning_frontend_realslice_v1_MEASURED_MECHANISM_learned_LINEAR_readout_over_FROZEN_"
    "GloVe_on_REAL_WorldTree_fine_content_the_toy_meaning_is_learnable_29556_does_NOT_scale_as_GENERALIZABLE_"
    "structure_the_in_vocab_lift_is_MEMORIZATION_cell_verdict_MIDDLE_converged_ridge_in_vocab_fine_0p4787_vs_"
    "frozen_0p329_lift_plus0p1497_CI_0p4465_0p5111_shuffled_0p0536_sep_0p4251_chance_0p171_N_fine_915_BUT_"
    "in_vocab_eval_EQUALS_train_set_so_lift_is_MEMORIZATION_INCLUSIVE_by_construction_AUDITOR_held_out_TRIPLE_"
    "recompute_3_seeds_fit_ridge_on_80pct_eval_20pct_unseen_triples_converged_0p106_0p107_0p157_vs_frozen_0p324_"
    "0p326_0p328_lift_approx_neg0p20_BELOW_frozen_AND_BELOW_chance_seen_concept_new_triple_subset_conv_0p062_"
    "0p086_0p102_so_generalizable_linearly_decodable_component_is_ZERO_or_negative_shuffled_control_only_rules_"
    "out_relation_MARGINAL_shortcut_NOT_memorization_a_memorizing_map_also_fails_shuffled_on_true_VET1_converged_"
    "vs_GD_CONFIRMED_ClosedFormLinear_lam_eq_wd_times_n_over_2_IS_exact_GD_objective_optimum_GD_curve_monotone_"
    "0p256_at512_to_0p350_at1024_still_rising_initial_HARD_FAIL_was_under_training_but_endpoint_is_a_TRAIN_FIT_"
    "VET3_scale_attenuation_smoke_half_scale_lift_0p4253_to_full_0p1497_is_the_MEMORIZATION_FRACTION_shrinking_"
    "as_n_grows_past_input_dim_308_not_signal_needing_more_capacity_more_capacity_memorizes_more_not_generalizes_"
    "MLP_entangles_collapses_to_0p08_below_chance_reproduces_29557_readout_linearity_glass_box_32of97_frozen_"
    "missed_energy_cases_0p330_BELOW_0p34_bar_glass_moves_wall_FALSE_held_out_concept_converged_lift_neg0p2048_"
    "THIN_MEANING_WALL_STANDS_at_real_scale_grounding_richer_meaning_is_the_lever_not_a_learned_readout_over_the_"
    "same_frozen_input_composes_29556_29557_CERT_plus1_proven_bound_LOCAL_ONLY_2026_07_25")
assert AID not in existing_ids, "duplicate atom id"

HEADLINE = ("LEARNED-LINEAR readout over FROZEN GloVe on REAL WorldTree fine-content: the toy 'meaning is "
    "learnable' (29556) does NOT scale as GENERALIZABLE structure -- the in-vocab lift is MEMORIZATION "
    "(MEASURED_MECHANISM, CERT +1 as a proven bound; DOWNWARD correction from the cell's MIDDLE 'borderline "
    "positive'). Reproduced full run (the on-disk metrics was a STALE SMOKE; re-ran --full, deterministic to 4 "
    "decimals): converged-ridge in-vocab fine 0.4787 vs frozen 0.329 = lift +0.1497 (CI [0.4465,0.5111]), "
    "shuffled 0.0536 (sep +0.4251), chance 0.171, N_fine 915. BUT the cell's in-vocab eval == the TRAIN set, so "
    "the lift is MEMORIZATION-INCLUSIVE by construction. AUDITOR held-out-TRIPLE recompute (3 seeds; fit ridge on "
    "80% of triples, eval the unseen 20%): converged 0.106/0.107/0.157 vs frozen 0.324/0.326/0.328 -> lift ~ -0.20, "
    "BELOW frozen AND BELOW chance; the seen-concept-new-triple subset is worse (conv 0.062/0.086/0.102). So the "
    "GENERALIZABLE linearly-decodable fine component of frozen GloVe is ~ZERO/negative -- the +0.1497 is a train-set "
    "fit (a lookup table), NOT extracted meaning. The shuffled control (0.0536) only rules out a relation-MARGINAL "
    "shortcut; it does NOT rule out memorization (a memorizing map also fails shuffled-on-true). VET#1 (converged "
    "vs GD): CONFIRMED -- ClosedFormLinear lam=wd*n/2 is the exact optimum of the GD objective; the GD curve climbs "
    "monotonically (0.256@512 -> 0.350@1024, still rising) so the initial HARD_FAIL was genuine under-training; but "
    "that converged optimum is a TRAIN-FIT. VET#3 (scale-attenuation): real (smoke half-scale lift 0.4253 -> full "
    "0.1497) but this is the MEMORIZATION FRACTION shrinking as n grows past input_dim 308, NOT 'signal needs more "
    "capacity'. MLP entangles (collapses ~0.08 below chance, reproduces 29557). Glass-box 32/97 frozen-missed energy "
    "cases now right = 0.330 < 0.34 bar -> glass_moves_wall FALSE. NET: the thin-meaning wall STANDS at real scale; "
    "grounding / richer meaning is the lever, not a learned readout over the same frozen input. This CONFIRMS the "
    "ARC arc's binding-wall conclusion rather than moving it.")

key_metrics = {
    "cell_verdict": "MIDDLE", "auditor_tier": "MEASURED_MECHANISM_proven_bound_downward_correction",
    "run_mode": "full", "N_fine_invocab": 915, "N_coarse_invocab": 607, "chance_fine": 0.171,
    "frozen_fine_invocab": 0.329, "frozen_fine_invocab_ci": [0.2993, 0.3601],
    "converged_linear_fine_invocab_TRAINFIT": 0.4787, "converged_ci": [0.4465, 0.5111],
    "in_vocab_lift_over_frozen_converged_MEMORIZATION_INCLUSIVE": 0.1497,
    "converged_shuffled_fine": 0.0536, "true_vs_shuffled_sep": 0.4251,
    "shuffled_rules_out_marginal_NOT_memorization": True,
    "GD_curve_fine_invocab": [0.1563,0.0514,0.0612,0.0514,0.0546,0.0601,0.0743,0.1005,0.1366,0.188,0.2557,0.3497],
    "GD_monotone_climbing_still_rising_at_1024": True,
    "converged_is_exact_GD_optimum_lam_eq_wd_n_over_2": True,
    "mlp_collapses_entangles": 0.0798, "mlp_below_chance": True,
    "AUDITOR_heldout_TRIPLE_converged_fine": {"seed555": 0.1061, "seed777": 0.1067, "seed999": 0.1566},
    "AUDITOR_heldout_TRIPLE_frozen_fine": {"seed555": 0.324, "seed777": 0.3258, "seed999": 0.3283},
    "AUDITOR_heldout_TRIPLE_lift_below_frozen_and_chance": True,
    "AUDITOR_seen_concept_new_triple_converged": {"seed555": 0.0625, "seed777": 0.0864, "seed999": 0.102},
    "generalizable_linear_component_of_frozen_meaning": "approx_zero_or_negative",
    "heldout_CONCEPT_converged_lift_cell": -0.2048, "frozen_heldout_concept": 0.3238,
    "glass_energy_frozen_missed": 97, "glass_energy_fixed": 32, "glass_frac_fixed": 0.3299,
    "glass_bar": 0.34, "glass_moves_wall": False,
    "smoke_half_scale_lift_for_scale_attenuation": 0.4253, "input_dim": 308, "in_vocab_train_pairs": 1522,
    "bands": {"LIFT_HP": 0.15, "LIFT_HF": 0.05, "GLASS_MIN": 0.34},
}

CERT_CLASS = ("learned_meaning_frontend_realslice_v1_MEASURED_MECHANISM_learned_linear_over_frozen_GloVe_real_"
    "worldtree_fine_in_vocab_lift_0p1497_is_MEMORIZATION_in_vocab_eval_eq_train_set_heldout_triple_recompute_3seed_"
    "converged_0p106_0p107_0p157_vs_frozen_0p324_below_chance_seen_concept_new_triple_0p062_0p102_generalizable_"
    "component_zero_shuffled_rules_out_marginal_not_memorization_converged_ridge_is_exact_GD_optimum_HARD_FAIL_was_"
    "undertraining_but_trainfit_scale_attenuation_is_memorization_fraction_shrinking_mlp_entangles_glass_32of97_"
    "0p330_below_0p34_moves_wall_FALSE_thin_meaning_wall_STANDS_grounding_is_the_lever_composes_29556_29557")

atom = {
    "atom_id": AID, "seq": NEW_SEQ, "op": "landed_vet_atomize", "corpus": "math",
    "tier": "MEASURED_MECHANISM", "cert_status": "proven-bound", "cert_class": CERT_CLASS,
    "grade": "MM_learned_linear_over_frozen_meaning_real_data_in_vocab_lift_is_MEMORIZATION_no_generalization_wall_stands",
    "verdict": "MEASURED", "anchor": "learned_meaning_frontend_realslice_v1",
    "anchor_name": "learned_meaning_frontend_realslice_v1",
    "cell": "experiments/exp_learned_meaning_frontend_realslice_v1.py",
    "cell_commit": "33b86bfc2", "cell_content_sha256_16": cell_sha16,
    "metrics_path": "data/exp_learned_meaning_frontend_realslice_v1/metrics.json",
    "metrics_sha256_16": metrics_sha16,
    "module": "learned_LINEAR_and_MLP_readout_over_FROZEN_SemanticHDEncoder_GloVe_WordNet_concept_plus_rel_onehot_to_gold_value_MSE_property_completion_ONE_VARIABLE_transform_converged_ridge_closed_form_plus_GD_curve_shuffled_mustfail_control_held_out_concept_coverage_probe_glassbox_energy_wall",
    "headline": HEADLINE, "key_metrics": key_metrics,
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "composes_seq": [29556, 29557], "corrects_seq": [],
    "cert_delta": 1, "net_cert_delta": 1, "store_head_at_write": 29557,
    "cross_arc_overlap": ("substrate_query 'learned linear readout over frozen meaning fine content "
        "discrimination in-vocab lift' top cosine 0.3232 = a June-2026 NOTE 'linear-readout-as-ceiling' "
        "(ARCH-A Drosophila: linear readout = capacity ceiling; MLP entangles) -- SAME structural shape but a "
        "DIFFERENT axis (capacity vs fine-content-discrimination) and different data (toy vs real WorldTree); it "
        "is a conceptual note, not a prior landed EXPERIMENT atom. No experiment atom >0.30. The direct lineage "
        "is the composed 29556 (toy differentiation, MEASURED_MECHANISM) + 29557 (readout linearity). This is a "
        "targeted REAL-DATA scale-up of 29556 with a NEW decisive held-out-TRIPLE generalization test, not a "
        "rediscovery."),
    "honest_scope": ("Single primary seed (20260725) reproduced deterministically; auditor held-out-TRIPLE "
        "generalization test run at 3 split seeds (555/777/999). REAL WorldTree v2.1 property tables, N_fine "
        "in-vocab 915, 6-way hard candidate sets (mean distractor cos 0.61, frozen fine 0.329 below ceiling = "
        "difficulty-on). The cell is INTERNALLY HONEST: its docstring/comments explicitly mark in-vocab as "
        "'memorization-inclusive' and report held-out-CONCEPT separately (-0.2048, coverage framing). What the "
        "AUDITOR adds is the DECISIVE distinction the cell did not test: a held-out-TRIPLE split shows the "
        "converged readout collapses to 0.106-0.157 (below frozen 0.324 AND below chance 0.171) even for SEEN "
        "concepts under NEW triples (conv 0.062-0.102) -> the failure is NOT merely 'unseen-concept coverage' (as "
        "the cell frames it) but that the learned map is a MEMORIZED LOOKUP that cannot infer a seen concept's "
        "OTHER properties. Nuance: as a STORE/lookup the in-vocab fit is fine (that is what a fact-store does) but "
        "as a claim about LEARNED GENERALIZABLE MEANING it is negative. The learnability DYNAMICS (GD monotone "
        "rise, shuffled flat) are real -- the readout genuinely learns a map -- but it learns to memorize, not to "
        "generalize. Held-out-triple test uses the same hard-distractor candidate construction; frozen baseline on "
        "held-out (0.324) matches full frozen (0.329) so the held-out population is representative."),
    "framing_correction": ("Director/cell framing: 'MIDDLE, borderline positive; the toy meaning-is-learnable "
        "finding SCALES to real data in-vocab; NOT memorization (shuffled 0.054 vs true 0.479, sep +0.425); "
        "held-out non-generalization is the coverage/grounding gap.' AUDITOR corrects DOWNWARD on the load-bearing "
        "interpretive claim (symmetric anti-negativity; VET POSITIVES HARDEST): (1) 'NOT memorization' is REFUTED. "
        "The shuffled control only rules out a relation-MARGINAL shortcut -- a genuinely memorizing map ALSO scores "
        "near-zero on shuffled-trained/true-eval, so shuffled cannot distinguish memorization from generalizable "
        "structure. The correct test is a held-out-TRIPLE split, which the cell did not run; the auditor's (3 "
        "seeds) gives converged 0.106-0.157 vs frozen 0.324 (below frozen AND chance) -> the +0.1497 in-vocab lift "
        "is memorization/train-fit with ~ZERO generalizable component. (2) The held-out FAILURE is NOT just "
        "'ingest the concept and it's fixed' coverage -- SEEN concepts under NEW triples also collapse (conv "
        "0.06-0.10), so this readout cannot infer a known concept's other properties; it is a lookup, not learned "
        "meaning. (3) VET#1 stands: the converged ridge IS the exact GD optimum (lam=wd*n/2) and the initial "
        "HARD_FAIL was under-training -- but the optimum it converges to is a TRAIN-FIT. (4) VET#3: the "
        "scale-attenuation (0.43 half -> 0.15 full) is the memorization fraction shrinking as pairs (1522) exceed "
        "input_dim (308), NOT 'needs more capacity/grounding for coverage' -- more capacity would memorize MORE, "
        "not generalize. NET: this cell CONFIRMS the ARC thin-meaning binding-wall at real scale rather than "
        "moving it; glass_moves_wall is FALSE (0.330<0.34) consistent with that. The DIRECT lever is grounded/"
        "richer meaning (the USER's binding-wall thesis), not a learned readout over the same frozen GloVe."),
    "fairness_verdict": ("The cell is a FAIR, well-designed can-fail experiment (real frozen baseline, hard "
        "nearest-distractors, difficulty-on, one-variable transform, shuffled must-fail control, held-out probe, "
        "glass-box energy re-test) and is internally honest about in-vocab being memorization-inclusive. The one "
        "gap is that its headline in-vocab metric evaluates on the TRAIN set and its anti-memorization argument "
        "leans on the shuffled control, which is insufficient. Auditor's held-out-triple recompute closes that "
        "gap. Tier MEASURED_MECHANISM proven-bound: the mechanism is real and characterized (memorization works "
        "in-vocab; learnability dynamics real; zero generalizable structure), CERT +1 as a proven boundary, "
        "consistent with how the toy parent 29556 was banked."),
    "revival_criteria": ("This would move toward a POSITIVE (meaning is learnable/generalizable) only if a "
        "held-out-TRIPLE (not just held-out-concept) evaluation shows converged lift materially ABOVE frozen on "
        "UNSEEN triples of SEEN concepts -- currently -0.20. Candidate levers per the arc: (1) grounded/richer "
        "meaning representation (Barsalou/perceptual, or a denser knowledge-sourced concept embedding) replacing "
        "thin GloVe -- the USER-flagged binding wall; (2) supplying per-concept property structure (ingestion) so "
        "the readout has a real relational schema to generalize over, not isolated pairs. A learned readout over "
        "the SAME frozen input is refuted as the lever by this cell."),
    "primitive_assessment": ("Confirms: frozen GloVe/WordNet meaning carries NO generalizable linearly-decodable "
        "fine-content structure at real scale (the primitive the reader needs for fine content-selection is "
        "MISSING, not merely under-read). A learned linear readout can memorize seen pairs but cannot synthesize "
        "the missing primitive. Route = SUPPLY richer/grounded meaning (missing-PRIMITIVE lane), not learn-a-rule "
        "over thin input."),
    "promote_verdict": "HOLD_at_MEASURED_MECHANISM_proven_bound_negative_leaning",
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
    "store_head_at_write_note": "math atoms=29554 lines, last seq 29557, ledger last seq 29557 at write",
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom))

new_line = json.dumps(atom, ensure_ascii=False)
assert "\r" not in new_line and "\n" not in new_line
new_atoms_text = "\n".join(atom_lines + [new_line]) + "\n"
d = os.path.dirname(os.path.abspath(ATOMS))
fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp"); os.close(fd)
with open(tmp, "w", encoding="utf-8", newline="") as f:
    f.write(new_atoms_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp, ATOMS)
with open(ATOMS, "rb") as f:
    raw = f.read()
assert b"\r\n" not in raw, "CRLF doubling in atoms.jsonl"
with open(ATOMS, encoding="utf-8") as f:
    v = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(v) == 29555, f"post-write expected 29555, got {len(v)}"
assert v[-1]["atom_id"] == AID and v[-1]["tier"] == "MEASURED_MECHANISM" and v[-1]["cert_status"] == "proven-bound"
print(f"ATOMS OK: now {len(v)} (was 29554); new seq {NEW_SEQ}; no CRLF doubling.")

ledger = dict(atom)
ledger["decision"] = ("BANK as MEASURED_MECHANISM (proven-bound / CERT +1) with a DOWNWARD framing correction. "
    "Cell verdict MIDDLE (borderline positive) rests on an in-vocab lift (+0.1497 converged) measured on the "
    "TRAIN set; independent held-out-TRIPLE recompute (3 seeds) shows converged 0.106-0.157 vs frozen 0.324 "
    "(below frozen AND chance), even for seen-concept-new-triple (0.062-0.102) -> the lift is MEMORIZATION with "
    "zero generalizable component. Shuffled control only rules out marginal shortcut. Converged ridge IS the "
    "exact GD optimum (HARD_FAIL was under-training) but is a train-fit. Scale-attenuation = memorization "
    "fraction shrinking. MLP entangles. glass_moves_wall FALSE (0.330<0.34). The thin-meaning wall STANDS at "
    "real scale; grounding/richer meaning is the lever. Composes 29556 (toy) + 29557 (readout linearity). "
    "Local-only; needs orchestrator store sync.")
ledger["note"] = ("AUDIT-ONLY independent recompute (.venv). Reproduced the FULL run (disk had a stale SMOKE; "
    "re-ran --full) matching the commit message to 4 decimals. Verified converged ridge = exact GD-objective "
    "optimum (lam=wd*n/2); GD curve monotone-rising to 1024. DECISIVE held-out-TRIPLE test (3 seeds) refutes the "
    "'NOT memorization' claim. Hashes: cell 1e0335b2f4f1fb72, metrics 3a8f94860ea0b70f.")
json.loads(json.dumps(ledger))
new_led_line = json.dumps(ledger, ensure_ascii=False)
assert "\r" not in new_led_line and "\n" not in new_led_line
new_ledger_text = "\n".join(ledger_lines + [new_led_line]) + "\n"
dl = os.path.dirname(os.path.abspath(LEDGER))
fd2, tmp2 = tempfile.mkstemp(dir=dl, suffix=".tmp"); os.close(fd2)
with open(tmp2, "w", encoding="utf-8", newline="") as f:
    f.write(new_ledger_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp2, LEDGER)
with open(LEDGER, "rb") as f:
    rawl = f.read()
assert b"\r\n" not in rawl, "CRLF doubling in ledger"
with open(LEDGER, encoding="utf-8") as f:
    vl = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(vl) == len(ledger_lines) + 1 and vl[-1]["atom_id"] == AID and vl[-1]["seq"] == NEW_SEQ
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)}; seq {last_seq} -> {NEW_SEQ}; no CRLF.")
print("DONE cell#1. LOCAL-ONLY. no origin push; no remote persist.")
