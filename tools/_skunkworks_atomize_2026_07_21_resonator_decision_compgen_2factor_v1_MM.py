"""
A5-gated LOCAL-ONLY atomize: exp_resonator_decision_compgen_2factor_v1.
tier=MEASURED_MECHANISM / proven-bound / CERT +0.
Already-VET'd decisively (adbdc068). This banks it correctly; no re-litigation.
Atomic tmp->os.replace; verify-load both files; matching ts on atom+ledger.
LOCAL WRITE ONLY -- NO origin push, NO remote persist (USER did not authorize).
"""
import json, os, time, tempfile, datetime

ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

# ---- A5 pre-load gate: confirm store integrity + expected count ----
with open(ATOMS, encoding="utf-8") as f:
    atom_lines = [l for l in f.read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]  # raises on any corruption
assert len(parsed) == 29398, f"expected 29398 atoms pre-write, got {len(parsed)}"
existing_ids = {o.get("id") for o in parsed if o.get("id")}
# confirm 29393-29398 intact (line positions == cert-arc refs)
ref = {29379: parsed[29378]["id"], 29380: parsed[29379]["id"],
       29381: parsed[29380]["id"], 29382: parsed[29381]["id"],
       29398: parsed[29397]["id"]}
print("PRE-GATE: 29398 atoms load-valid; last id ends ...", parsed[-1]["id"][-40:])

# ---- reproduce key numbers off-disk (Fix #28) ----
m = json.load(open("data/exp_resonator_decision_compgen_2factor_v1/metrics.json", encoding="utf-8"))
gm = m["gate_metrics"]
assert m["cardinality_ok"] and m["arms_differ"] and m["pos_control_ok"] and m["void_reasons"] == []
assert abs(gm["resonator_heldout"] - 1.0) < 1e-9 and abs(gm["gen_gap_resonator"] - 0.0) < 1e-9
assert abs(gm["flat_joint_heldout"] - 0.17997685185185186) < 1e-9
assert abs(gm["flat_factored_heldout"] - 0.22916666666666666) < 1e-9
assert abs(m["chance"] - 0.25) < 1e-9
res22 = m["arm_by_sigma"]["2.2"]["resonator_iter"]["heldout_mean"]
res28 = m["arm_by_sigma"]["2.8"]["resonator_iter"]["heldout_mean"]
assert abs(res22 - 0.873263888888889) < 1e-9 and abs(res28 - 0.3275462962962963) < 1e-9
print(f"OFF-DISK OK: res ho=1.000 (gen_gap 0.000), knee s2.2 ho={res22:.4f}, "
      f"collapse s2.8 ho={res28:.4f} (chance 0.25); flat_joint {gm['flat_joint_heldout']:.4f} "
      f"flat_factored {gm['flat_factored_heldout']:.4f} single_shot {gm['single_shot_heldout']:.4f}")

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

AID = ("math::MEASURED_MECHANISM_resonator_decision_compgen_2factor_v1_train_free_2factor_"
       "iterative_resonator_decision_readout_recovers_role_label_from_bind_construction_verbclass_"
       "1p000_HELDOUT_EQ_INDIST_BY_CONSTRUCTION_gen_gap_resonator_0p000_combination_agnostic_"
       "re_derivation_of_resonator_network_factorization_Frady_Kent_Kymn_Sommer_2020_EXTENDED_to_"
       "2_entangled_factor_decision_lookup_NOT_learned_generalization_proven_train_free_"
       "resonator_decode_takes_no_split_arg_swap_split_invariance_1p000_on_trainable_as_novel_"
       "FLAT_MLP_baselines_joint_0p180_csordas_factored_0p229_DROP_TO_CHANCE_0p25_on_heldout_"
       "because_bound_product_marginals_carry_zero_factor_signal_verified_0p012_single_shot_0p380_"
       "heldout_gap_vs_joint_plus0p820_vs_factored_plus0p771_gen_gap_joint_0p811_factored_0p763_"
       "construction_FORCED_contrast_NOT_fair_learner_gap_indist_gap_0p009_indist_cost_neg0p009_"
       "ONE_GENUINELY_MEASURED_quantity_extraction_noise_proxy_envelope_holds_1p000_through_"
       "sigma_le_1p5_knee_sigma_2p2_ho_0p873_collapses_to_chance_by_sigma_ge_2p8_ho_0p328_"
       "SYNTHETIC_only_FHRR_2048d_codebooks_N_CONSTR8_N_VERBCLASS10_N_ROLE4_random_role_table_"
       "sigma_abstract_phase_jitter_proxy_n24_per_product_3seed_7_13_19_72of72_cardinality_ok_"
       "arms_differ_pos_control_ok_void_none_NO_real_text_transfer_does_NOT_move_reader_0p557_"
       "labeling_bound_STRATEGIC_compgen_via_binding_systematicity_is_FREE_ALGEBRA_construction_"
       "determined_at_ANY_factor_count_a_property_not_a_learned_capability_NO_learned_chain_grade_"
       "compgen_to_find_via_binding_genuine_CG_compgen_learned_reader_generalization_bounded_by_"
       "SAME_extraction_labeling_wall_frontier_for_BOTH_axes_is_GROUNDING_composes_29379_29380_"
       "29381_29382_free_algebra_family_and_29398_reader_arc_closure_does_NOT_supersede_"
       "proven_BOUND_not_CG_CERT_plus0_LOCAL_ONLY_2026-07-21")

assert AID not in existing_ids, "duplicate atom id"

NAME = ("MATH MEASURED_MECHANISM (proven-bound; compgen-via-binding). CLAIM: a train-free 2-factor "
        "iterative resonator decision-readout recovers a role label from bind(construction, verb-class) "
        "at 1.000 with held-out == in-dist BY CONSTRUCTION (resonator gen_gap = 0.000) -- a re-derivation "
        "of the resonator-network factorization property (Frady/Kent/Kymn/Sommer 2020) EXTENDED to a "
        "2-entangled-factor decision lookup, NOT learned generalization. Flat MLP baselines drop to chance "
        "on held-out (joint 0.180, factored 0.229) because bound-product marginals carry ~0 factor signal "
        "= a construction-forced contrast, not a fair-learner gap. The one genuinely-measured quantity is "
        "the extraction-noise-proxy envelope (1.000 through sigma<=1.5, knee sigma~2.2 ho~0.87, chance by "
        "sigma>=2.8). SYNTHETIC-only; no real-text transfer; does NOT move the reader's 0.557 labeling bound.")

PLAIN = ("A resonator network is asked: given a single vector that BINDS two factors (a sentence-"
         "construction and a verb-class) together, read out the role label that the pair maps to. It scores "
         "1.000 on 'held-out' factor combinations that were never in training -- but that is FREE: the "
         "resonator uses no training split at all (resonator_decode takes no split argument; swapping which "
         "combinations count as 'novel' still scores 1.000), so held-out == in-distribution BY CONSTRUCTION. "
         "This is the known resonator-network factorization property (Frady/Kent/Kymn/Sommer 2020) applied to "
         "a 2-factor lookup, not a learned ability to generalize. Ordinary flat neural-net baselines fall to "
         "chance (0.25) on the held-out combinations (joint 0.180, factored 0.229) because the bound product's "
         "marginals carry almost no factor signal -- so the big gap between the resonator and the flat nets is "
         "forced by how the task is built, not a fair contest a learner could win. The only thing actually "
         "measured here is how much abstract phase-noise the readout tolerates before it breaks: perfect up to "
         "sigma 1.5, a knee at ~2.2 (about 0.87), and chance by 2.8. It is all synthetic (random FHRR codebooks, "
         "a random role table, noise as an abstract phase-jitter proxy) with no real-text transfer, and it does "
         "NOT improve the who-was-affected reader's 0.557 labeling ceiling. STRATEGIC POINT: compositional "
         "generalization via binding is a free/algebraic property at ANY number of factors -- there is no "
         "learned chain-grade compgen to be discovered through binding; the genuine learned kind is bounded by "
         "the SAME extraction/labeling wall as accuracy, and the frontier for both is grounding.")

CERT_CLASS = ("resonator_decision_compgen_2factor_train_free_readout_role_from_bind_construction_verbclass_"
              "heldout1p000_EQ_indist_gen_gap_resonator_0p000_BY_CONSTRUCTION_re_derivation_Frady2020_"
              "factorization_2_entangled_factor_lookup_NOT_learned_gen_flat_joint_ho0p180_factored_ho0p229_"
              "to_chance0p25_bound_product_marginal_signal_0p012_construction_forced_contrast_heldout_gap_"
              "plus0p820_plus0p771_measured_envelope_1p000_to_sigma1p5_knee2p2_ho0p873_chance_by2p8_ho0p328_"
              "synthetic_FHRR2048_n24_3seed_72of72_no_real_text_reader0p557_unmoved_frontier_is_grounding")

atom = {
    "id": AID,
    "name": NAME,
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": "proven-bound",
    "cert_class": CERT_CLASS,
    "plain_language": PLAIN,
    "importance": ("MEDIUM (proven-bound; construction-scoped mechanism proof). It CLOSES the "
                   "compgen-via-binding question by proving systematicity from binding is free-algebra / "
                   "construction-determined at any factor count (a property, not a learned capability), so "
                   "there is no learned chain-grade compgen to be found VIA binding; it redirects both the "
                   "accuracy axis and the learned-compgen axis to the shared extraction/labeling wall whose "
                   "fix is grounding. Extends the 29379-82 free-algebra family to a 2-entangled-factor "
                   "decision lookup. +0 CERT."),
    "description": NAME,
    "aliases": [
        "resonator-decision 2-factor compgen: train-free readout, held-out == in-dist BY CONSTRUCTION (MM)",
        "resonator gen_gap 0.000; flat MLP joint 0.180 / factored 0.229 drop to chance 0.25 on held-out",
        "compgen-via-binding is free-algebra at any factor count -- a property not a learned capability",
        "measured envelope: 1.000 to sigma<=1.5, knee sigma~2.2 (ho~0.87), chance by sigma>=2.8",
        "re-derivation of resonator-network factorization (Frady/Kent/Kymn/Sommer 2020), 2-factor extension",
    ],
    "ts_iso": ts_iso,
    "ts": ts,
    "serves_capability": ("compositional_generalization_via_binding_is_free_algebra_construction_determined_"
                          "at_any_factor_count_NOT_a_learned_capability_no_chain_grade_compgen_via_binding_"
                          "learned_compgen_bounded_by_same_extraction_labeling_wall_frontier_is_grounding"),
    "metadata": {
        "provenance_quality": ("independent_venv_offdisk_recompute_off_metrics_json_key_load_bearing_numbers_"
                               "reproduce_gate_metrics_resonator_ho1p000_gen_gap0p000_flat_joint0p180_"
                               "flat_factored0p229_chance0p25_knee_sigma2p2_ho0p873_collapse_sigma2p8_ho0p328_"
                               "cardinality72of72_arms_differ_pos_control_ok_void_none_decisive_VET_adbdc068_"
                               "code_structural_claims_no_split_arg_swap_split_invariance_marginal0p012_"
                               "inherited_from_decisive_prior_VET_not_re_litigated"),
        "anchor": "exp_resonator_decision_compgen_2factor_v1",
        "cell_commit": "local_full_run_metrics_ts_2026-07-21T06:56:47Z_run_mode_full_untracked",
        "vet_ref": "adbdc068_decisive_prior_VET_this_is_the_bank_step_not_re_litigation",
        "supersedes": None,
        "amends_atom_ids": None,
        "store_head_at_write": "unsynced_needs_orchestrator",
        "metrics_path": "data/exp_resonator_decision_compgen_2factor_v1/metrics.json",
        "verified_off_data": ("INDEP recompute (.venv Scripts/python, off "
            "data/exp_resonator_decision_compgen_2factor_v1/metrics.json, NOT verdict_msg; Fix #28). "
            "Reproduced BIT-EXACT: resonator_heldout=1.0 with gen_gap_resonator=0.0 (held-out==in-dist BY "
            "CONSTRUCTION); flat_joint_heldout=0.17997685 (~0.180), flat_factored_heldout=0.22916667 (~0.229), "
            "single_shot_heldout=0.37962963 (~0.380); chance=0.25 (N_ROLE=4); heldout_gap vs joint +0.8200231, "
            "vs factored +0.7708333; gen_gap joint 0.8107639 / factored 0.7633102; indist_gap 0.00925926, "
            "indist_cost -0.00925926; envelope: resonator ho 1.000 at sigma 0.0/0.8/1.5, knee sigma2.2 "
            "ho=0.8732639 (id 0.8807870), collapse sigma2.8 ho=0.3275463 (id 0.3200231) ~chance; controls "
            "cardinality_ok=True (72/72), arms_differ=True, pos_control_ok=True, void_reasons=[]. Config: "
            "N_DIM=2048 FHRR, N_CONSTR=8, N_VERBCLASS=10, N_ROLE=4, HELD_PER_CONSTR=3, n_train=n_test=24/product, "
            "seeds 7/13/19, RES_N_ITER=25 RES_N_RESTART=4."),
        "honest_scope": ("Full run, local, SYNTHETIC-only. Random FHRR codebooks (N_DIM=2048), random role table, "
                         "sigma = abstract phase-jitter extraction-noise PROXY (not a real perceptual/text "
                         "channel), n=24 per (construction x verb-class) product, 3 seeds. NO real-text transfer; "
                         "does NOT move the who-was-affected reader's 0.557 labeling bound. The train-free / "
                         "no-split and marginal-signal ~0.012 claims are code-structural, inherited from the "
                         "decisive prior VET (adbdc068), not independently re-derived here."),
        "metrics": {
            "resonator_heldout": 1.0, "resonator_indist": 1.0, "gen_gap_resonator": 0.0,
            "flat_joint_heldout": 0.17997685185185186, "flat_joint_indist": 0.9907407407407408,
            "flat_factored_heldout": 0.22916666666666666, "single_shot_heldout": 0.3796296296296296,
            "chance": 0.25, "heldout_gap_vs_flat_joint": 0.8200231481481481,
            "heldout_gap_vs_flat_factored": 0.7708333333333334,
            "gen_gap_flat_joint": 0.810763888888889, "gen_gap_flat_factored": 0.7633101851851851,
            "indist_gap": 0.00925925925925919, "indist_cost": -0.00925925925925919,
            "envelope_resonator_ho": {"0.0": 1.0, "0.8": 1.0, "1.5": 1.0,
                                       "2.2": 0.873263888888889, "2.8": 0.3275462962962963,
                                       "3.5": None},
            "knee_sigma": 2.2, "collapse_sigma": 2.8,
            "bound_product_marginal_factor_signal_approx": 0.012,
            "n_per_product": 24, "seeds": [7, 13, 19], "n_units": "72/72",
        },
        "over_reads_corrected": [
            ("Do NOT read the resonator 1.000 held-out as LEARNED compositional generalization. gen_gap_"
             "resonator=0.000 exactly and resonator_decode takes no split argument (swap-split invariance "
             "1.000): held-out == in-distribution BY CONSTRUCTION. This is the resonator-network factorization "
             "property (Frady/Kent/Kymn/Sommer 2020), a re-derivation extended to a 2-entangled-factor lookup, "
             "NOT a learned capability."),
            ("Do NOT read the +0.820 / +0.771 held-out gap over flat MLP baselines as a fair-learner advantage. "
             "The flat nets fall to chance because bound-product marginals carry ~0 factor signal (~0.012) -- "
             "the contrast is FORCED by construction, not a contest a flat learner could win with more capacity."),
            ("Do NOT generalize this to real text or to the reader. It is synthetic (FHRR codebooks, random role "
             "table, phase-jitter proxy) with NO real-text transfer and does NOT move the reader's 0.557 "
             "labeling bound."),
        ],
        "genuine_positives_symmetric_anti_negativity": (
            "GENUINE, credited (symmetric anti-negativity): (1) The ONE genuinely-measured quantity -- the "
            "extraction-noise-proxy ROBUSTNESS ENVELOPE -- is real and clean: resonator holds 1.000 through "
            "sigma<=1.5, degrades at a knee sigma~2.2 (ho 0.873), and collapses to chance by sigma>=2.8 "
            "(ho 0.328), monotone across a principled sweep, 3 seeds, 72/72 units, positive control clears. "
            "(2) The construction is correctly designed and honestly reported: gen_gap_resonator=0.000, arms "
            "differ, void none. (3) The STRATEGIC closure is load-bearing and correct: compgen-via-binding is "
            "free-algebra / construction-determined at any factor count, which cleanly removes an entire class "
            "of would-be chain-grade targets and redirects effort to the grounding frontier."),
        "revival_criteria": [
            ("PROMOTE toward chain-grade requires LEARNED compositional generalization on REAL data (not a "
             "train-free binding readout on synthetic codebooks): a learned reader that generalizes to held-out "
             "role/construction combinations on real text. Per this atom that axis is bounded by the SAME "
             "extraction/labeling wall as accuracy (reader 0.557 / labeler plateau 29398), whose fix is grounding."),
            ("A real (non-proxy) extraction/perceptual noise channel replacing the abstract phase-jitter sigma "
             "would upgrade the envelope from a proxy measurement to a grounded one."),
        ],
        "cross_arc_overlap_check": (
            "substrate_query 'resonator decision compgen 2-factor binding free algebra held-out construction' "
            "-> nearest banked CELLS are the 29379-82 free-algebra family (compgen-via-binding / codebook "
            "induction) and the reader-arc closure 29398; this atom EXTENDS that family to a 2-entangled-factor "
            "DECISION readout (a new construction, not a rediscovery of a prior cell) and COMPOSES (does NOT "
            "supersede) all of them. Confirmed a targeted extension at cell-level, not a duplicate."),
        "cites": [
            "Fix_28_verify_off_data_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "cited_number_must_reproduce_from_cell",
            "verify_the_referent_atom_ids_mechanism_metric_regime",
            "construction_proof_is_not_capability_win_VET_asks_live_alternative_or_forced_by_construction",
            "synthetic_toy_corpus_outcomes_can_be_construction_determined_real_questions_need_real_data",
            "Frady_Kent_Kymn_Sommer_2020_resonator_networks_factorization",
        ],
        "composes_with": [
            ("COMPOSES (does NOT supersede) 29379 MM_compgen_binding_vs_flat_LEARNED_PERCEPTUAL_frontend: the "
             "free-algebra result holds when the learned frontend is a noisy perceptual MLP -- this extends the "
             "same free-algebra mechanism to a 2-entangled-factor decision lookup."),
            "COMPOSES 29380 MM_novel_atom_generalization_codebook_binding (construction-determined by linear shared latent).",
            "COMPOSES 29381 MEASURED_MECHANISM_novel_atom_real_codebook_generalization (composition survives real nonlinear codebook, capacity-contingent).",
            "COMPOSES 29382 MM_novel_atom_real_codebook_capacity_curve (induction-vs-NN margin flips positive with capacity).",
            ("COMPOSES (does NOT supersede) 29398 reader-arc CLOSURE patient-classifier / archaic-domain labeling "
             "plateau: the STRATEGIC bridge -- learned chain-grade compgen (learned reader generalization) is "
             "bounded by the SAME extraction/labeling wall as accuracy; frontier for BOTH axes is grounding."),
        ],
        "strategic_implication": (
            "compgen-via-binding systematicity is FREE-ALGEBRA / construction-determined at ANY factor count "
            "(a property, not a learned capability) -> there is no learned chain-grade compgen to find VIA "
            "binding; the genuine chain-grade compgen (learned reader generalization) is bounded by the SAME "
            "extraction/labeling wall as accuracy; the frontier for BOTH axes = GROUNDING."),
        "atomized_by": "hdi_skunkworks",
        "atomized_date": "2026-07-21",
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
    },
}

# sanity: atom must json-roundtrip
json.loads(json.dumps(atom))

# ---- A5 atomic append to atoms.jsonl (tmp -> os.replace) ----
new_atoms_text = "\n".join(atom_lines + [json.dumps(atom, ensure_ascii=False)]) + "\n"
d = os.path.dirname(os.path.abspath(ATOMS))
fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
with os.fdopen(fd, "w", encoding="utf-8") as f:
    f.write(new_atoms_text)
    f.flush(); os.fsync(f.fileno())
os.replace(tmp, ATOMS)

# ---- verify-load atoms.jsonl ----
with open(ATOMS, encoding="utf-8") as f:
    v = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(v) == 29399, f"post-write expected 29399, got {len(v)}"
assert v[-1]["id"] == AID and v[-1]["tier"] == "MEASURED_MECHANISM" and v[-1]["cert_status"] == "proven-bound"
# 29393-29398 unchanged
for i in [29379, 29380, 29381, 29382, 29398]:
    assert v[i-1]["id"] == ref[i], f"atom {i} MUTATED"
print(f"ATOMS OK: now {len(v)} atoms; new atom #29399 verified; 29379-82 + 29398 intact.")

# ---- ledger entry (matching ts) ----
ledger = {
    "op": "landed_vet_atomize",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "proven-bound",
    "cert_class": CERT_CLASS,
    "anchor": "exp_resonator_decision_compgen_2factor_v1",
    "cell_commit": "local_full_run_metrics_ts_2026-07-21T06:56:47Z_run_mode_full_untracked",
    "vet_ref": "adbdc068_decisive_prior_VET_bank_step_only_no_re_litigation",
    "supersedes_commit": None,
    "supersedes_atom_id": None,
    "amends_atom_id": None,
    "composes": [ref[29379], ref[29380], ref[29381], ref[29382], ref[29398]],
    "store_head_at_write": "unsynced_needs_orchestrator",
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": AID,
    "decision": ("MEASURED_MECHANISM / proven-bound. Banks the already-VET'd (adbdc068, decisive) "
                 "resonator-decision 2-factor compgen result. A train-free 2-factor iterative resonator "
                 "decision-readout recovers a role label from bind(construction, verb-class) at 1.000 with "
                 "held-out == in-dist BY CONSTRUCTION (gen_gap_resonator=0.000; resonator_decode takes no split "
                 "arg; swap-split invariance 1.000) = a re-derivation of resonator-network factorization "
                 "(Frady/Kent/Kymn/Sommer 2020) extended to a 2-entangled-factor decision lookup, NOT learned "
                 "generalization. Flat MLP baselines (joint 0.180, factored 0.229) drop to chance because "
                 "bound-product marginals carry ~0 factor signal (~0.012) = construction-forced contrast. The one "
                 "genuinely-MEASURED quantity is the extraction-noise-proxy envelope (1.000 to sigma<=1.5, knee "
                 "sigma~2.2 ho~0.87, chance by sigma>=2.8). SYNTHETIC-only; no real-text transfer; does NOT move "
                 "the reader's 0.557 labeling bound. Key numbers reproduce BIT-EXACT off metrics.json (Fix #28). "
                 "STRATEGIC: compgen-via-binding is free-algebra at any factor count (property, not learned "
                 "capability) -> no learned chain-grade compgen VIA binding; genuine learned compgen bounded by "
                 "the SAME extraction/labeling wall as accuracy; frontier for BOTH = grounding. COMPOSES (does "
                 "NOT supersede) 29379-82 free-algebra family + 29398 reader-arc closure. CERT +0 (proven bound, "
                 "not chain-grade). Local-only; needs orchestrator store sync."),
    "cert_delta": "+0 (MEASURED_MECHANISM proven-bound / construction-scoped mechanism proof; not chain-grade)",
    "net_cert_delta": "+0",
    "ts_iso": ts_iso,
    "ts": ts,
    "atom_id": AID,
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}
json.loads(json.dumps(ledger))

with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]
n_ledger_before = len(ledger_lines)
new_ledger_text = "\n".join(ledger_lines + [json.dumps(ledger, ensure_ascii=False)]) + "\n"
dl = os.path.dirname(os.path.abspath(LEDGER))
fd2, tmp2 = tempfile.mkstemp(dir=dl, suffix=".tmp")
with os.fdopen(fd2, "w", encoding="utf-8") as f:
    f.write(new_ledger_text)
    f.flush(); os.fsync(f.fileno())
os.replace(tmp2, LEDGER)

with open(LEDGER, encoding="utf-8") as f:
    vl = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(vl) == n_ledger_before + 1
assert vl[-1]["atom_id"] == AID and vl[-1]["ts"] == ts
print(f"LEDGER OK: {n_ledger_before} -> {len(vl)}; entry ts matches atom ts ({ts_iso}).")
print("ATOM_ID:", AID)
print("DONE. LOCAL-ONLY. needs_orchestrator_store_sync=True; no origin push; no remote persist.")
