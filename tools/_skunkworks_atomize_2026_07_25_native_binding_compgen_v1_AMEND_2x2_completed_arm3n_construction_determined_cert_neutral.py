"""A5-gated LOCAL-ONLY atomize: AMENDMENT to seq 29557 (native_binding_compositional_generalization_v1).

The cell was ALREADY banked as 29557 (MEASURED_MECHANISM, proven-bound) at cell_commit 58c317af2 by a
prior skunkworks the SAME day, with a well-calibrated 3-bound atom (binding untested-not-refuted single-hop;
readout-linearity is the demonstrated fix for 29556's flat-MLP failure but only an ACTIONABLE HYPOTHESIS at
+1/9 above base-rate; genuine systematicity base-rate-limited/underpowered at 9 pairs). The a09baa4aa
extension (arm 3n native-encoder + bind-MLP quadrant + prereg) OVERWROTE metrics.json (new sha) but only
ADDS two measurements; it does NOT change the verdict/tier and does NOT warrant a second CERT+1. This atom
is CERT-NEUTRAL (cert_delta 0) and AMENDS 29557.

INDEPENDENT RECOMPUTE (.venv, off-disk + full re-run, deterministic):
 - Re-ran experiments/exp_native_binding_compositional_generalization_v1.py --full: ALL metrics reproduce
   BIT-EXACT vs the on-disk a09baa4aa metrics.json (verdict MIDDLE; frozen 0.5556; native_binding 0.7778;
   concat_linear 0.7778; flat_mlp 0.5556; bind_mlp 0.5556; shuffled 0.6667; bind_over_concat 0.0;
   shuffle_sep 0.1111; arm3n held 0.8889; role_max_cos 0.1889; every curve identical) -> determinism +
   the arm3n/bind-MLP extension did NOT perturb any pre-existing arm number (git diff 58c317..a09baa4 on
   the .py is additive: arm3n + bind-MLP + prints only; no frozen/bind/concat/flat_mlp/shuffled/_verdict
   code touched). Confirms 29557's core numbers off-disk.
 - Raw item counts (n_held=9, unit 1/9): frozen 5/9, bind+linear 7/9, concat+linear 7/9, flat_mlp(concat+
   MLP) 5/9, bind+MLP 5/9, shuffled(base-rate) 6/9. 2x2 COMPLETED.

WHAT THE EXTENSION ADDS (the only new content vs 29557):
 (1) bind+MLP = 5/9 (ho_lift 0.0) completes the {bind,concat} x {linear,MLP} 2x2 (29557 had only 3 of 4
     quadrants). Full 2x2: bind+linear = concat+linear = 7/9; bind+MLP = concat+MLP = 5/9. STRENGTHENS
     29557's point-2 (readout-linearity is the axis, independent of combination format on BOTH sides) but
     does NOT change its magnitude caveat (+1/9 above base-rate) NOR the confound: the linear arms use
     LINEAR_LR=0.3 while the MLP arms use MLP_LR=0.1 + H_BOTTLENECK=32, so linear-vs-MLP is CONFOUNDED
     with lr/width -> "the MLP's nonlinear hidden layer entangles" stays an ACTIONABLE HYPOTHESIS, not a
     proven causal mechanism.
 (2) arm3n native ConceptEncoder + fixed bind + linear = held 0.8889 (lift +0.3333 over frozen-GloVe;
     lift_over_chance +0.463) BUT within_cat_cos 0.7007 / cross_cat 0.0289 is DESIGNER-PLANTED via a
     synthetic shared-marker corpus -> CONSTRUCTION-DETERMINED. NOT evidence the unsupervised encoder
     discovers structure (correctly caveated by the author). Read correctly it REINFORCES 29557's routing:
     given CLEAN category structure IN THE MEANING, the same bind+linear stack jumps 0.778 -> 0.889 ->
     meaning-structure is the upstream lever, consistent with the thin-meaning wall.

FRAMING CORRECTION (to the Director's spawn, symmetric anti-negativity):
 The spawn framed this as "refutes binding-as-fix -> meaning is the lever" and as a fresh landing. Both
 need correcting. (a) The cell is ALREADY certified (29557). (b) 29557 already established the sharper
 truth: single-hop bind+linear is per-relation-linear-in-item (M @ circ(role_r) @ item) and concat+linear
 is shared-linear-in-item + per-relation bias; neither exercises binding's DISTINCTIVE capability
 (superposing a variable number of role-filler bindings in ONE vector + unbind-by-role), so bind_over_concat
 = 0.0 is near-STRUCTURAL and the HARD_PASS binding-necessity gate was near-unreachable. Binding is UNTESTED
 single-hop, NOT REFUTED. The routing conclusion "meaning is the lever" is CORRECT; the reason "binding
 refuted" is WRONG -- it needs a MULTI-ROLE / DEEP-COMPOSITION regime to test at all. (Minor: 29557's
 "matched expressivity by construction" slightly overstates -- bind gives multiplicative per-relation
 conditioning, concat gives additive; but the conclusion holds.)

POSITIVE-CONTROL / HF-ATTRIBUTION: the self-test planted-separable env (bind+linear must generalize ~1
where structure is present, frozen ~chance, shuffled flat) PASSES on the re-run -> the discriminator CAN
fire when systematicity is present, so the near-null real result (+1/9) is a SUBSTANTIVE finding, not a
test-design failure.
"""
import json, os, time, tempfile, datetime, hashlib

ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

with open(ATOMS, encoding="utf-8") as f:
    atom_lines = [l for l in f.read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]
assert len(parsed) == 29559, f"expected 29559 atoms pre-write, got {len(parsed)}"
existing_ids = {o.get("atom_id") for o in parsed if o.get("atom_id")}
assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR -- investigate"

with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]
lp = [json.loads(l) for l in ledger_lines]
last_seq = [o["seq"] for o in lp if "seq" in o][-1]
assert last_seq == 29562, f"expected ledger last seq 29562, got {last_seq}"
# confirm the parent 29557 exists and is the native_binding atom
parent = [o for o in lp if o.get("seq") == 29557]
assert parent and "native_binding" in parent[0].get("anchor_name", ""), "parent 29557 not the native_binding atom"
NEW_SEQ = 29563
print(f"PRE-GATE: {len(parsed)} atoms load-valid; ledger last seq {last_seq}; parent 29557 present; NEW_SEQ {NEW_SEQ}.")

M = json.load(open("data/exp_native_binding_compositional_generalization_v1/metrics.json", encoding="utf-8"))
assert M["verdict"] == "MIDDLE" and M["run_mode"] == "full"
assert M["heldout_n"] == 9
assert abs(M["frozen_heldout"] - 0.5556) < 1e-6
assert abs(M["native_binding_ho_lift"] - 0.2222) < 1e-6
assert abs(M["concat_linear_ho_lift"] - 0.2222) < 1e-6
assert abs(M["flat_mlp_ho_lift"] - 0.0) < 1e-9
assert abs(M["bind_mlp_ho_lift"] - 0.0) < 1e-9
assert abs(M["bind_over_concat"] - 0.0) < 1e-9
assert abs(M["shuffle_separation"] - 0.1111) < 1e-6
assert M["combination_x_readout_2x2"] == {"bind_linear": 0.2222, "concat_linear": 0.2222,
                                          "bind_mlp": 0.0, "concat_mlp_flatMLP": 0.0}
assert abs(M["arm3n_native_encoder"]["held_last"] - 0.8889) < 1e-6
assert abs(M["arm3n_native_encoder"]["ho_lift_vs_frozen_glove"] - 0.3333) < 1e-6
assert abs(M["arm3n_native_encoder"]["item_structure"]["within_cat_cos_mean"] - 0.7007) < 1e-6
assert abs(M["arm3n_native_encoder"]["item_structure"]["cross_cat_cos_mean"] - 0.0289) < 1e-6
print("OFF-DISK OK: 2x2 completed (bind+MLP 0.0); arm3n 0.8889 lift+0.333 within/cross 0.70/0.03; core arms match 29557.")

cell_sha16 = hashlib.sha256(open("experiments/exp_native_binding_compositional_generalization_v1.py", "rb").read()).hexdigest()[:16]
metrics_sha16 = hashlib.sha256(open("data/exp_native_binding_compositional_generalization_v1/metrics.json", "rb").read()).hexdigest()[:16]
assert cell_sha16 == "938dd7ac0889931e", cell_sha16
assert metrics_sha16 == "1fa3c0ef2159c30f", metrics_sha16

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
ts_day = "2026-07-25"

AID = ("math::native_binding_compgen_v1_AMEND_29557_2x2_COMPLETED_plus_arm3n_construction_determined_CERT_"
    "NEUTRAL_a09baa4aa_extension_adds_bind_MLP_quadrant_5of9_holift_0p0_completing_bind_linear_eq_concat_"
    "linear_7of9_and_bind_MLP_eq_concat_MLP_5of9_readout_linearity_is_the_axis_on_BOTH_formats_STILL_"
    "hypothesis_not_capability_win_plus1of9_above_baserate_linear_lr0p3_vs_mlp_lr0p1_h32_CONFOUNDED_and_"
    "arm3n_native_conceptencoder_bind_linear_held_0p8889_lift_plus0p333_within_cat_cos_0p70_cross_0p03_"
    "DESIGNER_PLANTED_synthetic_marker_corpus_CONSTRUCTION_DETERMINED_not_encoder_discovers_structure_"
    "reinforces_meaning_structure_is_upstream_lever_binding_UNTESTED_single_hop_NOT_refuted_bind_over_"
    "concat_0p0_near_structural_needs_multi_role_deep_composition_selftest_planted_PASSES_discriminator_"
    "can_fire_so_null_is_substantive_recompute_bit_exact_reproduces_29557_amends_29557_no_second_CERT_"
    "LOCAL_ONLY_2026_07_25")
assert AID not in existing_ids, "duplicate atom id"

HEADLINE = ("AMENDMENT to seq 29557 (native_binding_compositional_generalization_v1). The cell was ALREADY "
    "certified MEASURED_MECHANISM at commit 58c317af2 (same day); the a09baa4aa extension (arm 3n + bind-MLP "
    "+ prereg) OVERWROTE metrics.json but only ADDS two measurements and does NOT change the verdict/tier -> "
    "this atom is CERT-NEUTRAL (cert_delta 0) and amends 29557. Independent full re-run reproduces ALL metrics "
    "BIT-EXACT (verdict MIDDLE; frozen 5/9=0.5556; bind+linear=concat+linear=7/9=0.7778; bind+MLP=concat+MLP="
    "5/9=0.5556; shuffled base-rate 6/9=0.6667; bind_over_concat 0.0; shuffle_sep +1/9=0.1111; arm3n 0.8889), "
    "and the additive extension did NOT perturb any pre-existing arm number. TWO NEW MEASUREMENTS: (1) the "
    "bind+MLP quadrant (ho_lift 0.0) COMPLETES the {bind,concat}x{linear,MLP} 2x2 that 29557 lacked -- both "
    "linear arms 7/9, both MLP arms 5/9 -- STRENGTHENING 29557's read that readout-LINEARITY (not the bind-vs-"
    "concat combination format) is what separates generalizing from non-generalizing arms; magnitude UNCHANGED "
    "(+1/9 above base-rate = an ACTIONABLE HYPOTHESIS, not a capability win) and the linear-vs-MLP contrast is "
    "CONFOUNDED with hyperparameters (LINEAR_LR 0.3 vs MLP_LR 0.1, H_BOTTLENECK 32), so 'the nonlinear hidden "
    "layer entangles' is not a proven causal mechanism. (2) arm-3n (native ConceptEncoder item + fixed bind + "
    "linear) reaches held 0.8889 (lift +0.3333 over frozen-GloVe) but its within-cat cos 0.7007 / cross-cat "
    "0.0289 item structure is DESIGNER-PLANTED via a synthetic shared-marker corpus -> CONSTRUCTION-DETERMINED, "
    "NOT evidence the unsupervised encoder discovers structure (author caveat correct). Read correctly it "
    "REINFORCES 29557's routing: given clean category structure IN THE MEANING the same bind+linear stack jumps "
    "0.778->0.889, i.e. meaning-STRUCTURE is the upstream lever. FRAMING CORRECTION: the arc must NOT record "
    "'native binding refuted as the systematicity fix' -- 29557 already established that single-hop bind_over_"
    "concat=0.0 is NEAR-STRUCTURAL (both features are linear-in-item; binding's distinctive superpose-many-"
    "bindings+unbind capability is NOT exercised single-hop), so binding is UNTESTED here, not refuted. The "
    "routing 'meaning is the lever' is CORRECT; the reason 'binding refuted' is WRONG. Self-test planted env "
    "PASSES on re-run -> the discriminator CAN fire, so the near-null real systematicity (+1/9) is substantive.")

key_metrics = {
    "cell_verdict": "MIDDLE", "auditor_tier": "MEASURED_MECHANISM_amendment_CERT_NEUTRAL",
    "cert_delta": 0, "amends_seq": 29557,
    "run_mode": "full", "heldout_n": 9, "n_domains": 4, "chance_ho": 0.4259,
    "recompute_bit_exact_reproduces_29557": True,
    "extension_did_not_perturb_preexisting_arms": True,
    "combination_x_readout_2x2_COMPLETED": {"bind_linear": 0.2222, "concat_linear": 0.2222,
                                            "bind_mlp": 0.0, "concat_mlp_flatMLP": 0.0},
    "raw_item_counts_of_9": {"frozen": "5/9", "bind_linear": "7/9", "concat_linear": "7/9",
                             "flat_mlp": "5/9", "bind_mlp": "5/9", "shuffled_baserate": "6/9"},
    "NEW_bind_mlp_ho_lift": 0.0,
    "readout_linearity_axis_on_both_formats": True,
    "readout_linearity_still_hypothesis_not_capability_win_plus1of9": True,
    "linear_vs_mlp_confounded_lr_and_bottleneck": {"LINEAR_LR": 0.3, "MLP_LR": 0.1, "H_BOTTLENECK": 32},
    "NEW_arm3n_native_encoder_held_last": 0.8889,
    "arm3n_ho_lift_vs_frozen_glove": 0.3333, "arm3n_lift_over_chance": 0.463,
    "arm3n_within_cat_cos": 0.7007, "arm3n_cross_cat_cos": 0.0289,
    "arm3n_construction_determined_planted_not_discovered": True,
    "arm3n_reinforces_meaning_structure_is_upstream_lever": True,
    "bind_over_concat_0p0_is_near_structural_single_hop": True,
    "binding_UNTESTED_single_hop_NOT_refuted": True,
    "shuffle_sep_beyond_baserate": 0.1111, "genuine_systematicity": "1/9_noise_floor",
    "selftest_planted_PASSES_discriminator_can_fire": True,
    "metrics_sha_drift": {"29557_recorded": "099f49fce37bc68f", "a09baa4aa_current": "1fa3c0ef2159c30f",
                          "core_numbers_identical_29557_stays_valid": True},
}

CERT_CLASS = ("native_binding_compgen_v1_AMEND_29557_CERT_NEUTRAL_2x2_completed_bind_MLP_0p0_both_linear_7of9_"
    "both_MLP_5of9_readout_linearity_axis_still_hypothesis_plus1of9_confounded_lr_bottleneck_arm3n_0p8889_"
    "construction_determined_planted_within_cat_0p70_reinforces_meaning_structure_lever_binding_untested_not_"
    "refuted_single_hop_recompute_bit_exact_amends_29557")

atom = {
    "atom_id": AID, "seq": NEW_SEQ, "op": "amend_atomize", "corpus": "math",
    "tier": "MEASURED_MECHANISM", "cert_status": "amendment-cert-neutral", "cert_class": CERT_CLASS,
    "grade": "MM_amendment_2x2_completed_plus_arm3n_construction_determined_binding_untested_not_refuted_cert_neutral",
    "verdict": "MEASURED", "anchor": "native_binding_compositional_generalization_v1",
    "anchor_name": "native_binding_compositional_generalization_v1",
    "cell": "experiments/exp_native_binding_compositional_generalization_v1.py",
    "cell_commit": "a09baa4aa", "cell_content_sha256_16": cell_sha16,
    "metrics_path": "data/exp_native_binding_compositional_generalization_v1/metrics.json",
    "metrics_sha256_16": metrics_sha16,
    "module": "native_VSA_bind_hdlab_binding_bind_HRR_plus_single_linear_readout_vs_flat_concat_MLP_hub_over_FROZEN_SemanticHDEncoder_GloVe_category_correlated_only_heldout_split_property_value_recovery_2x2_combination_x_readout_plus_arm3n_native_conceptencoder_construction_sensitive_diagnostic",
    "headline": HEADLINE, "key_metrics": key_metrics,
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "composes_seq": [29557], "corrects_seq": [], "amends_seq": 29557,
    "cert_delta": 0, "net_cert_delta": 0, "store_head_at_write": 29562,
    "cross_arc_overlap": ("substrate_query 'native VSA binding compositional generalization systematicity "
        "role-filler readout linearity' top hits are NOTES/preregs at cosine 0.37-0.38 (the Lake-Baroni "
        "'VSA generalizes by construction' drill note, the wave14e compgen note, the 2026-07-03 vsa-native "
        "task-suite prereg) -- NO prior landed EXPERIMENT atom >0.30. This cell EMPIRICALLY TESTS+BOUNDS the "
        "KB-resident theoretical claim ('bind() is algebraically well-defined without seeing the combination') "
        "on a real frozen-GloVe-meaning task and finds it does NOT confer a unique single-hop edge (untested "
        "distinctive-capability regime). The only same-anchor atom is the direct parent 29557; this is its "
        "amendment, not a rediscovery."),
    "honest_scope": ("Single seed (20260725), 4-domain toy (energy/metal/planet/animal from 29556), 9 held-out "
        "category-correlated pairs, single deterministic split, high chance 0.4259 with small property-value "
        "contrast sets (metal/source = {nugget,ore}, chance 0.5) -> the property-value-recovery metric (a sound "
        "deviation from the note's concept-recovery, which is ill-posed for shared-value cc relations, applied "
        "IDENTICALLY to all arms) makes absolute numbers easy and the resolution coarse (1/9 per item). Every "
        "effect discussed is a +/-1-item quantity at the noise floor; NOTHING ABSOLUTE about systematicity level "
        "or real-data generality is concludable. What IS robust (within-cell, reproduced bit-exact): the 2x2 "
        "pattern (both linear arms 7/9, both MLP arms 5/9), the flat-MLP ho_lift 0.0 reproduction of 29556, "
        "bind_over_concat=0.0, and the arm-3n construction-determined jump. What is NOT: absolute systematicity, "
        "the causal 'MLP entangles' claim (confounded with LR/bottleneck), and any claim about native binding "
        "proper (single-hop cannot exercise it). Gate promotion of the linear-readout finding on a scaled "
        "(>9-pair, balanced, multi-seed) AND multi-role/deep-composition re-run."),
    "framing_correction": ("Director spawn framed this as (i) a FRESH landing and (ii) 'refutes binding-as-fix -> "
        "meaning is the lever'. Both corrected. (i) The cell is ALREADY certified as seq 29557 (MEASURED_MECHANISM, "
        "same day) -- this is an amendment, not a new CERT+1; banking a second CERT+1 for the same finding would "
        "double-count. (ii) 'Binding refuted' is TOO STRONG: 29557 already established that single-hop bind+linear "
        "(M @ circ(role_r) @ item, per-relation linear-in-item) and concat+linear (shared-linear-in-item + "
        "per-relation bias) neither exercise binding's DISTINCTIVE power (superpose a variable number of role-filler "
        "bindings in ONE vector + unbind-by-role), so bind_over_concat=0.0 is NEAR-STRUCTURAL and the HARD_PASS "
        "binding-necessity gate was near-unreachable -> binding is UNTESTED single-hop, NOT refuted. The routing "
        "conclusion 'meaning is the lever' is CORRECT and is independently REINFORCED by arm-3n (clean planted "
        "category structure in meaning -> 0.889); the reason 'binding refuted' is WRONG and should not enter the "
        "arc record. Testing native binding requires a MULTI-ROLE / DEEP-COMPOSITION regime. (Minor: 29557's "
        "phrase 'matched expressivity by construction' slightly overstates -- bind conditions the item map "
        "MULTIPLICATIVELY per relation, concat ADDITIVELY via bias; but the conclusion that neither exercises "
        "binding's unique capability single-hop stands.)"),
    "fairness_verdict": ("The cell is a FAIR can-fail experiment (real frozen baseline, difficulty-on non-degenerate "
        "cosines 0.28-0.50, one-variable combination-mechanism isolation, shuffled base-rate control, self-test "
        "planted positive control that PASSES so the discriminator can fire, glass-box decodes, arms_differ "
        "verified). The property-value-recovery metric deviation is SOUND and unbiased across arms. The only "
        "over-reach to guard is the causal 'nonlinear hidden layer entangles' reading of the 2x2, which is "
        "confounded with the linear-vs-MLP hyperparameter gap. Amendment is CERT-NEUTRAL: the proven bounds were "
        "already banked in 29557 (CERT +1); the extension adds one completing quadrant + a construction-determined "
        "diagnostic, neither a new proven bound."),
    "revival_criteria": ("Inherits 29557's revival: (1) MULTI-ROLE / DEEP-COMPOSITION test is the ONLY way to "
        "actually test native binding (superpose >=2 bindings + unbind-by-role, or multi-hop) -- the regime where "
        "bind_over_concat CAN separate. (2) Scale the held-out env well beyond 9 pairs (more domains/relations, "
        "balanced value sets, multi-seed) to lift the +1/9 systematicity off the noise floor before promoting the "
        "linear-readout finding toward CG. (3) To promote the 'readout-linearity is the lever' claim, DECONFOUND it "
        "from LR/bottleneck (match optimizer + capacity across the linear and MLP arms). (4) arm-3n only becomes "
        "evidence of DISCOVERED structure if an UNsupervised encoder (no planted markers) yields within>>cross "
        "category cosine on real corpora. (5) hydroelectric-class misses (thin-meaning wall) re-implicate the "
        "grounded/richer-meaning fork, upstream of both readout-linearity and binding."),
    "primitive_assessment": ("Reaffirms: the missing primitive is GROUNDED/STRUCTURED MEANING, not the binding "
        "algebra. arm-3n shows that when category structure is SUPPLIED in the item representation, the fixed "
        "bind+linear stack generalizes (0.889); with thin conflated GloVe it does not (7/9, +1/9 above base-rate). "
        "Route = SUPPLY richer/grounded meaning (Track-2 earned/grounded encoder) and/or a MULTI-ROLE regime to "
        "test binding proper -- NOT more single-hop binding-architecture work."),
    "promote_verdict": "HOLD_amendment_cert_neutral_parent_29557_stays_MEASURED_MECHANISM",
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
    "store_head_at_write_note": "math atoms=29559 lines, ledger last seq 29562 at write; parent 29557 present",
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
assert len(v) == 29560, f"post-write expected 29560, got {len(v)}"
assert v[-1]["atom_id"] == AID and v[-1]["tier"] == "MEASURED_MECHANISM" and v[-1]["cert_delta"] == 0
print(f"ATOMS OK: now {len(v)} (was 29559); new seq {NEW_SEQ}; cert_delta 0; no CRLF doubling.")

ledger = dict(atom)
ledger["decision"] = ("AMEND 29557 as CERT-NEUTRAL (cert_delta 0). The cell (native_binding_compositional_"
    "generalization_v1) was ALREADY banked as seq 29557 (MEASURED_MECHANISM, proven-bound) at commit 58c317af2 "
    "the same day. The a09baa4aa extension overwrote metrics.json (sha drift 099f49->1fa3c0; core numbers "
    "identical so 29557 stays valid) and ADDS only (1) the bind+MLP quadrant (ho_lift 0.0) completing the 2x2 "
    "-- STRENGTHENS but does not change 29557's readout-linearity read (still +1/9-above-base-rate hypothesis; "
    "linear-vs-MLP confounded with LR/bottleneck) -- and (2) an arm-3n native-encoder diagnostic at 0.8889 that "
    "is CONSTRUCTION-DETERMINED (planted within-cat cos 0.70), reinforcing meaning-structure as the upstream "
    "lever. No new proven bound -> no second CERT+1. Independent full re-run reproduces every metric BIT-EXACT "
    "(determinism confirmed; extension did not perturb pre-existing arms). FRAMING: binding is UNTESTED single-"
    "hop (bind_over_concat=0 near-structural), NOT refuted -- corrects the spawn's 'refutes binding-as-fix'; the "
    "'meaning is the lever' routing is correct. Local-only; needs orchestrator store sync.")
ledger["note"] = ("AUDIT-ONLY independent recompute (.venv full re-run). All metrics reproduce bit-exact vs "
    "a09baa4aa metrics.json. git diff 58c317af2->a09baa4aa on the .py is additive (arm3n + bind-MLP + prints; "
    "no pre-existing arm/gate code touched), and the re-run confirms pre-existing arm numbers unchanged. Parent "
    "29557 already adjudicates Q1(bind_over_concat robustness -> near-structural), Q2(systematicity +1/9 base-"
    "rate-limited), Q3(9-pair underpowered), Q6(routing) with high rigor. Hashes: cell 938dd7ac0889931e, "
    "metrics 1fa3c0ef2159c30f.")
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
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)}; seq {last_seq} -> {NEW_SEQ}; cert_delta 0; no CRLF.")
print("DONE amendment. LOCAL-ONLY. no origin push; no remote persist.")
