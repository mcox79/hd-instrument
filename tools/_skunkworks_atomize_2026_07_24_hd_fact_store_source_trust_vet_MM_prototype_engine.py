"""A5-gated LOCAL-ONLY atomize: exp_hd_fact_store_source_trust_vet_v1 (hdlab/hd_fact_store.py).
tier=MEASURED_MECHANISM / proven-bound. Cell verdict PASS; auditor re-scopes DOWN to a bounded
mechanism-characterization (the DESIGN is built + works; the STORAGE ENGINE is an un-optimized prototype).

CLAIM (as banked): the USER's HD source-trust ingest-vetting DESIGN is BUILT and WORKS. A fact
(s,r,o) is stored as ONE role-slot HD bundle with SOURCE+TRUST bound IN (genuine reuse of
EventBundleCodec/RoleSlotSummarizer bipolar primitives -- bit-identity self-test in event_bundle.py);
glass-box round-trip 1.000 (every field incl provenance+trust recovers by unbind); native same-(s,r)
conflict retrieval + the 4 trust rules (REPLACE/DROP/FLAG/COMBINE) fire correctly (40/40); clean
false-flag 0.000. BOUND (why MM not CG): (a) the perfect DETECTION is construction-easy -- same-(s,r)
is a BIT-IDENTICAL 2-pair bundle (cosine EXACTLY 1.0) and the 0.75 threshold sits in a ~0.47-wide gap
above exact-string-confirm; no surface-variant / fuzzy conflict is tested; (b) false-flag 0.000 is
CORRECT-BY-DESIGN for a trust arbiter (a non-conflicting fact has nothing to arbitrate) -- it does NOT
verify factual truth and is NOT like-for-like vs the 0.53 correctness-auditor; (c) retrieval is O(n)
linear cosine over ALL active facts + O(vocab) cleanup per candidate -- bypasses the substrate's proven
partitioned/cleanup_family/capacity machinery; capacity un-benchmarked (140 facts); cardinality +
source->trust are HAND-tables; no subsumption; status is a symbolic ledger flag not HD-represented.
Design foundation-ready; storage-engine is a prototype. Independent .venv recompute reproduces all
metrics (seed7 AND seed123 both perfect) bit-for-bit. BINARY-SAFE write, LOCAL ONLY, git-commit.
"""
import json, os, time, tempfile, datetime, hashlib

ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

# ---- A5 pre-load gate ----
with open(ATOMS, encoding="utf-8") as f:
    atom_lines = [l for l in f.read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]
assert len(parsed) == 29527, f"expected 29527 atoms pre-write, got {len(parsed)}"
existing_ids = {o.get("atom_id") for o in parsed if o.get("atom_id")}
assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR -- investigate before write"

with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]
lp = [json.loads(l) for l in ledger_lines]
last_seq = [o["seq"] for o in lp if "seq" in o][-1]
assert last_seq == 29530, f"expected ledger last seq 29530, got {last_seq}"
NEW_SEQ = 29531
print(f"PRE-GATE: {len(parsed)} atoms load-valid; ledger last seq {last_seq}; NEW_SEQ {NEW_SEQ}.")

# ---- off-disk recompute confirmation (re-assert off metrics.json + independent re-run done separately) ----
M = json.load(open("data/exp_hd_fact_store_source_trust_vet_v1/metrics.json", encoding="utf-8"))
mm = M["metrics"]
assert M["verdict"] == "PASS" and M["deterministic"] is True
assert mm["confusion"] == {"tp": 40, "fp": 0, "tn": 120, "fn": 0}
assert mm["detection_precision"] == 1.0 and mm["detection_recall"] == 1.0
assert mm["resolution_accuracy"] == 1.0 and mm["resolution_correct"] == 40 and mm["resolution_total"] == 40
assert mm["clean_total"] == 120 and mm["clean_flagged"] == 0 and mm["clean_false_flag_rate"] == 0.0
assert mm["glassbox_roundtrip_acc"] == 1.0 and mm["n_trials"] == 160 and mm["n_live_facts"] == 140
assert {w["resolution"] for w in mm["worked_examples"]} == {"REPLACE", "DROP", "FLAG", "COMBINE"}
# INDEPENDENT re-run (separate .venv process) reproduced: seed7 confusion 40/0/120/0, seed123 ALSO
# perfect (seed-robust). sr_key cosine dist: SAME (s,r) exactly 1.0000 (60/60), share-subj max 0.5112,
# share-rel max 0.5310, share-none max 0.2837 -> 0.75 threshold in a ~0.47-wide gap (robust placement,
# but same-(s,r) is a BIT-IDENTICAL 2-pair bundle -> detection is exact-match not fuzzy). O(n) confirmed:
# _find_same_sr stacks M over ALL active facts + full cosine + per-candidate glass-box recover_fact.
print("OFF-DISK OK: roundtrip 1.0; detect P/R 1.0/1.0; res 40/40; clean false-flag 0/120; determ True. "
      "Independent re-run: seed7 AND seed123 both perfect; sr cosine same=1.0 / non-same max=0.531 "
      "(gap 0.47); O(n) linear retrieval source-confirmed.")

cell_sha16 = hashlib.sha256(open("experiments/exp_hd_fact_store_source_trust_vet_v1.py", "rb").read()).hexdigest()[:16]
module_sha16 = hashlib.sha256(open("hdlab/hd_fact_store.py", "rb").read()).hexdigest()[:16]
metrics_sha16 = hashlib.sha256(open("data/exp_hd_fact_store_source_trust_vet_v1/metrics.json", "rb").read()).hexdigest()[:16]
assert cell_sha16 == "262fc9387bca8e28" and module_sha16 == "799e5ec134b63c79" and metrics_sha16 == "558839b630d6b979"

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
ts_day = "2026-07-24"

AID = ("math::hd_fact_store_source_trust_vet_v1_MEASURED_MECHANISM_HD_NATIVE_FACT_STORE_plus_SOURCE_TRUST_"
    "INGEST_VET_DESIGN_BUILT_AND_WORKS_but_STORAGE_ENGINE_is_UN_OPTIMIZED_PROTOTYPE_a_FACT_subj_rel_obj_stored_"
    "as_ONE_role_slot_HD_bundle_with_SOURCE_id_and_TRUST_level_BOUND_IN_native_binding_not_side_metadata_fact_vec_"
    "quantize_bind_REL_rel_plus_ARG0_subj_plus_ARG1_obj_plus_SOURCE_src_plus_TRUST_trust_GLASSBOX_round_trip_1p000_"
    "EVERY_field_incl_provenance_plus_trust_recovers_by_per_role_unbind_plus_per_domain_cleanup_never_reads_"
    "plaintext_GENUINE_REUSE_EventBundleCodec_which_reuses_M1p7_RoleSlotSummarizer_bipolar_primitives_bit_identity_"
    "selftest_in_event_bundle_py_NOT_reimpl_CONFLICT_DETECTION_precision_recall_1p000_tp40_fp0_tn120_fn0_on_160_"
    "trials_native_same_s_r_HD_signature_2pair_bundle_plus_glassbox_string_confirm_THE_4_TRUST_RULES_40of40_REPLACE_"
    "higher_trust_overrides_DROP_lower_trust_dropped_FLAG_equal_trust_FUNCTIONAL_contradiction_both_kept_UNRESOLVED_"
    "COMBINE_equal_trust_MULTIVALUED_additive_merge_CLEAN_FALSE_FLAG_0p000_120_clean_plus_hard_distractor_facts_"
    "beats_the_failed_condenser_auditor_0p53_DETERMINISTIC_2_runs_bit_identical_seed7_and_seed123_both_perfect_seed_"
    "robust_BOUND_why_MM_not_CG_a_DETECTION_is_CONSTRUCTION_EASY_same_s_r_is_a_BIT_IDENTICAL_2pair_bundle_cosine_"
    "EXACTLY_1p0_60of60_share_subj_max_0p511_share_rel_max_0p531_share_none_max_0p284_so_0p75_threshold_sits_in_a_"
    "0p47_wide_gap_ROBUST_placement_BUT_no_surface_variant_or_fuzzy_conflict_tested_detection_is_effectively_an_"
    "EXACT_s_r_dictionary_lookup_via_HD_signature_plus_exact_string_confirm_NOT_a_hard_HD_retrieval_test_b_false_"
    "flag_0p000_is_CORRECT_BY_DESIGN_for_a_TRUST_ARBITER_a_non_conflicting_fact_has_NOTHING_to_arbitrate_it_does_"
    "NOT_verify_factual_TRUTH_trusts_curation_student_model_trade_so_NOT_like_for_like_vs_the_0p53_correctness_"
    "auditor_it_AVOIDS_that_failure_mode_by_not_attempting_correctness_vetting_c_RETRIEVAL_is_O_n_linear_cosine_"
    "over_ALL_active_facts_find_same_sr_stacks_M_over_full_list_plus_O_vocab_cleanup_per_candidate_BYPASSES_the_"
    "substrates_PROVEN_partitioned_store_cleanup_family_random_indexing_capacity_machinery_CAPACITY_UN_BENCHMARKED_"
    "tested_only_140_facts_no_crosstalk_wall_measured_d_cardinality_FUNCTIONAL_MULTIVALUED_plus_source_to_trust_are_"
    "HAND_tables_real_ingestion_needs_schema_KB_sourced_no_subsumption_crimson_lt_red_status_is_symbolic_ledger_flag_"
    "NOT_HD_represented_DESIGN_foundation_ready_STORAGE_ENGINE_is_a_PROTOTYPE_the_foundational_scale_optimization_"
    "gap_all_metrics_independently_recomputed_off_disk_venv_seed7_and_seed123_bit_for_bit_cross_arc_overlap_only_"
    "DESIGN_NOTES_analog5_immune_per_source_trust_cos_0p28_no_prior_experiment_atom_gt_0p30_novel_BUILD_CERT_plus1_"
    "LOCAL_ONLY_2026_07_24")

assert AID not in existing_ids, "duplicate atom id"

HEADLINE = ("HD FACT STORE + SOURCE-TRUST INGEST-VET: DESIGN BUILT + WORKS, STORAGE ENGINE = PROTOTYPE "
    "(MEASURED_MECHANISM, CERT +1 as a proven bound). The USER's source-trust vetting design is realized: a fact "
    "(subject,relation,object) is stored as ONE role-slot HD bundle with SOURCE-id + TRUST-level BOUND IN (native "
    "binding, not side metadata). GLASS-BOX round-trip 1.000 -- every field including provenance + trust recovers "
    "by per-role unbind + per-domain cleanup, never reading plaintext. GENUINE REUSE: the binding is "
    "EventBundleCodec, which reuses the M1.7 RoleSlotSummarizer bipolar primitives with a bit-identity self-test "
    "(not a re-impl). CONFLICT DETECTION P/R 1.000 (tp40/fp0/tn120/fn0 on 160 trials); the 4 TRUST RULES fire "
    "correctly 40/40 (REPLACE higher-trust overrides / DROP lower-trust / FLAG equal-trust functional "
    "contradiction keeps both unresolved / COMBINE equal-trust multivalued merges); CLEAN false-flag 0.000; "
    "deterministic (seed7 AND seed123 both perfect). WHY MEASURED_MECHANISM not CHAIN_GRADE (three bounds): "
    "(a) the perfect DETECTION is construction-easy -- same-(s,r) is a BIT-IDENTICAL 2-pair bundle (cosine EXACTLY "
    "1.0, 60/60), non-same tops out at 0.531, so the 0.75 threshold sits in a ~0.47-wide gap: robustly placed but "
    "the task is effectively an EXACT (s,r) dictionary lookup (HD signature + exact string confirm), no "
    "surface-variant / fuzzy conflict is tested. (b) false-flag 0.000 is CORRECT-BY-DESIGN for a trust arbiter -- "
    "a non-conflicting fact has nothing to arbitrate; it does NOT verify factual truth (trusts curation, "
    "student-model trade), so it is NOT a like-for-like win over the 0.53 correctness-auditor -- it AVOIDS that "
    "failure mode by not attempting correctness-vetting. (c) RETRIEVAL is O(n) linear cosine over ALL active facts "
    "(+ O(vocab) cleanup per candidate), bypassing the substrate's PROVEN partitioned/cleanup_family/capacity "
    "machinery; CAPACITY is UN-BENCHMARKED (only 140 facts, no crosstalk wall measured); cardinality + "
    "source->trust are HAND-tables; no subsumption; status is a symbolic ledger flag, not HD-represented. NET: the "
    "DESIGN is foundation-ready; the STORAGE ENGINE is a prototype -- this is exactly the foundational-scale "
    "optimization gap for a real curriculum.")

key_metrics = {
    "glassbox_roundtrip_acc": 1.0,
    "detection_precision": 1.0, "detection_recall": 1.0,
    "confusion_tp": 40, "confusion_fp": 0, "confusion_tn": 120, "confusion_fn": 0,
    "resolution_accuracy": 1.0, "resolution_correct": 40, "resolution_total": 40,
    "resolution_breakdown": "10 REPLACE + 10 DROP + 10 FLAG + 10 COMBINE",
    "clean_total": 120, "clean_flagged": 0, "clean_false_flag_rate": 0.0,
    "auditor_false_flag_reference": 0.53, "beats_auditor_but_different_task": True,
    "n_trials": 160, "n_live_facts": 140, "n_dim": 8192,
    "deterministic_seed7": True, "seed123_also_perfect": True,
    "sr_cos_same": 1.0, "sr_cos_share_subj_max": 0.5112, "sr_cos_share_rel_max": 0.5310,
    "sr_cos_share_none_max": 0.2837, "sr_threshold": 0.75, "sr_gap": 0.469,
    "detection_is_exact_match_not_fuzzy": True,
    "retrieval_complexity": "O(n) linear cosine over all active facts + O(vocab) cleanup per candidate",
    "uses_partitioned_store_or_cleanup_family": False,
    "capacity_benchmarked": False, "capacity_tested_facts": 140,
    "cardinality_hand_table": True, "source_to_trust_hand_table": True,
    "subsumption_supported": False, "status_hd_represented": False,
    "verifies_factual_truth": False, "verdict": "PASS",
}

CERT_CLASS = ("hd_fact_store_source_trust_vet_v1_MEASURED_MECHANISM_HD_native_fact_store_provenance_plus_trust_"
    "bound_in_glassbox_roundtrip_1p0_genuine_EventBundleCodec_RoleSlotSummarizer_reuse_conflict_detect_PR_1p0_4_"
    "trust_rules_REPLACE_DROP_FLAG_COMBINE_40of40_clean_false_flag_0p0_deterministic_seed7_seed123_BOUND_detection_"
    "construction_easy_same_sr_exact_1p0_bundle_075_threshold_047_gap_no_fuzzy_test_false_flag_0_correct_by_design_"
    "trust_arbiter_not_correctness_vetting_not_like_for_like_vs_053_auditor_retrieval_O_n_linear_bypasses_"
    "partitioned_cleanup_family_capacity_UN_benchmarked_140_facts_hand_tables_no_subsumption_design_foundation_"
    "ready_storage_engine_prototype")

atom = {
    "atom_id": AID,
    "seq": NEW_SEQ,
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "proven-bound",
    "cert_class": CERT_CLASS,
    "grade": "MM_HD_FACT_STORE_TRUST_VET_DESIGN_WORKS_ENGINE_PROTOTYPE",
    "verdict": "PASS",
    "anchor_name": "hd_fact_store_source_trust_vet_v1",
    "cell": "experiments/exp_hd_fact_store_source_trust_vet_v1.py",
    "module": "hdlab/hd_fact_store.py",
    "cell_commit": f"sha256_{cell_sha16}_working_tree_UNTRACKED_at_HEAD_868ee899f",
    "cell_content_sha256_16": cell_sha16,
    "module_content_sha256_16": module_sha16,
    "metrics_path": "data/exp_hd_fact_store_source_trust_vet_v1/metrics.json",
    "metrics_sha256_16": metrics_sha16,
    "headline": HEADLINE,
    "key_metrics": key_metrics,
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "composes_seq": [],
    "corrects_seq": [],
    "cert_delta": 1,
    "net_cert_delta": 1,
    "store_head_at_write": 29530,
    "cross_arc_overlap": ("substrate_query 'fact store source trust conflict resolution provenance HD binding' "
        "top cosine 0.3174 = a generic NOTE header '5.4 Conflict resolution'; 0.2803 = the DESIGN NOTE "
        "'Analog 3/5 IMMUNE per-source trust scoring pre-test' (V(D)J negative-selection analog: high-trust "
        "overrides low-trust on conflict) -- the conceptual ANCESTOR of this build; 0.2773 = 'Per-fact "
        "provenance'. ALL are design/planning notes, NONE a prior landed EXPERIMENT atom at cosine>0.30. This is "
        "a genuinely NOVEL BUILD that realizes the long-standing Analog-5 immune-trust design, not a rediscovery."),
    "honest_scope": ("Inline-local foreground demonstration on a CONTROLLED synthetic fact set (160 trials, 140 "
        "live facts, n_dim 8192): 40 clean unique-(s,r) facts + 40 hard distractors (same-r-diff-s and "
        "same-s-diff-r) + 40 injected conflicts (10 each REPLACE/DROP/FLAG/COMBINE). The perfect scores are "
        "CONSTRUCTION-FAIR on threshold placement (same-(s,r) cosine exactly 1.0 vs non-same max 0.531 = a "
        "0.47-wide gap) but the DETECTION TASK is easy: same-(s,r) is a bit-identical 2-pair HD bundle, so "
        "conflict retrieval is effectively an EXACT (s,r) dictionary lookup (HD signature + a redundant exact "
        "string-confirm) -- no surface-variant subjects ('USA' vs 'United States'), no synonym relations, no "
        "fuzzy conflict is tested; a real-ingestion collision would NOT land at cosine 1.0 and is UNMEASURED. "
        "The clean false-flag 0.000 is the CORRECT behavior for a source-trust arbiter (a non-conflicting fact "
        "has nothing to arbitrate) but is NOT solved correctness-vetting: the store TRUSTS the curated source and "
        "never checks whether a trusted fact is factually true. STUBBED / un-optimized for foundational scale: "
        "(a) retrieval is O(n) linear cosine over ALL active facts + O(vocab) cleanup per candidate -- it does NOT "
        "use the substrate's proven partitioned store / cleanup_family / random_indexing / banked capacity+"
        "partition theory; (b) CAPACITY (facts-before-crosstalk) is UN-BENCHMARKED (only 140 facts, round-trip "
        "1.0 there but no wall measured); (c) cardinality (FUNCTIONAL/MULTIVALUED) + source->trust are HAND-"
        "tables (real ingestion needs schema/KB-sourced); (d) no subsumption (crimson<red compatibility); (e) "
        "status is a symbolic control flag, NOT HD-represented."),
    "framing_correction": ("Director/cell framing is HONEST and largely UPHELD -- the cell's own docstring + "
        "honest_frame already state 'trusts curation, does NOT verify factual truth' and 'clean false-flag ~0 by "
        "construction'. Auditor SCOPES the tier DOWN from an implied capability-PASS to MEASURED_MECHANISM (proven "
        "bound), with three sharpenings the Director should carry forward for the foundational-scale question the "
        "USER asked: (1) the perfect CONFLICT-DETECTION is CONSTRUCTION-DETERMINED, not a live capability win -- "
        "same-(s,r) yields a bit-identical 2-pair bundle (cosine exactly 1.0) and there is ALSO an exact "
        "string-confirm, so the '0.75 threshold in a wide gap' is real but never load-bearing; this is exact-key "
        "retrieval dressed as HD cosine, and fuzzy / surface-variant conflict (the hard part of real ingestion) is "
        "UNTESTED. (2) 'beats the 0.53 auditor' is TRUE numerically but APPLES-TO-ORANGES: the auditor did "
        "correctness-vetting with an internal ontology; this does conflict-ARBITRATION only. The 0.000 false-flag "
        "is not 'we solved what the auditor failed at' -- it is 'we do not attempt correctness-vetting, so there "
        "is nothing to false-flag on a clean fact.' Report it as avoiding the failure mode, not beating the task. "
        "(3) The load-bearing gap for FOUNDATIONAL SCALE is the STORAGE ENGINE: O(n) linear retrieval + "
        "un-benchmarked capacity + hand-tables. The DESIGN (HD-native facts with bound provenance+trust, "
        "glass-box round-trip, trust-ranked resolution) is foundation-ready and correct; the ENGINE is a "
        "prototype that will NOT scale to a real curriculum without wiring in the substrate's proven "
        "partitioned/cleanup/capacity machinery and KB-sourced schema tables. Bank the DESIGN win; keep the "
        "ENGINE explicitly un-certified for scale."),
    "revival_criteria": ("Promote toward CHAIN_GRADE when: (1) conflict detection is tested on FUZZY / "
        "surface-variant (s,r) collisions (typo'd subjects, synonym relations) where cosine is NOT 1.0 -- the "
        "threshold becomes load-bearing; (2) retrieval is re-implemented on the substrate's partitioned store / "
        "cleanup_family (not O(n) linear scan) and CAPACITY is benchmarked to the crosstalk wall at scale "
        "(thousands+ of facts); (3) cardinality + source->trust are schema/KB-sourced rather than hand-tabled. "
        "Correctness-VERIFICATION (vs trust-arbitration) is a SEPARATE capability and out of scope for this atom."),
    "local_write_only_no_origin_push_no_remote_persist": True,
    "needs_orchestrator_store_sync": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom))

# ---- A5 atomic append (BINARY-SAFE: newline='' prevents Windows CRLF doubling) ----
new_line = json.dumps(atom, ensure_ascii=False)
assert "\r" not in new_line and "\n" not in new_line, "atom line contains embedded newline/CR"
new_atoms_text = "\n".join(atom_lines + [new_line]) + "\n"
d = os.path.dirname(os.path.abspath(ATOMS))
fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp"); os.close(fd)
with open(tmp, "w", encoding="utf-8", newline="") as f:
    f.write(new_atoms_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp, ATOMS)

with open(ATOMS, "rb") as f:
    raw = f.read()
assert b"\r\n" not in raw, "CRLF doubling detected in atoms.jsonl after write"
with open(ATOMS, encoding="utf-8") as f:
    v = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(v) == 29528, f"post-write expected 29528, got {len(v)}"
assert v[-1]["atom_id"] == AID and v[-1]["tier"] == "MEASURED_MECHANISM" and v[-1]["cert_status"] == "proven-bound"
print(f"ATOMS OK: now {len(v)} atoms (was 29527); new atom seq {NEW_SEQ}; no CRLF doubling.")

# ---- ledger entry (matching ts; seq continuity 29530 -> 29531) ----
ledger = {
    "seq": NEW_SEQ, "op": "landed_vet_atomize", "corpus": "math", "tier": "MEASURED_MECHANISM",
    "cert_status": "proven-bound", "cert_class": CERT_CLASS, "verdict": "PASS",
    "grade": "MM_HD_FACT_STORE_TRUST_VET_DESIGN_WORKS_ENGINE_PROTOTYPE",
    "atom_id": AID, "anchor_name": "hd_fact_store_source_trust_vet_v1",
    "cell": "experiments/exp_hd_fact_store_source_trust_vet_v1.py",
    "module": "hdlab/hd_fact_store.py",
    "cell_commit": f"sha256_{cell_sha16}_working_tree_UNTRACKED_at_HEAD_868ee899f",
    "cell_content_sha256_16": cell_sha16, "module_content_sha256_16": module_sha16,
    "metrics_path": "data/exp_hd_fact_store_source_trust_vet_v1/metrics.json",
    "metrics_sha256_16": metrics_sha16,
    "key_metrics": key_metrics,
    "headline": HEADLINE,
    "note": ("AUDIT-ONLY independent off-disk recompute (.venv). VERIFIED: (1) GLASS-BOX round-trip 1.000 -- "
        "re-ran _run_measurement, every field incl source+trust recovered by per-role unbind + per-domain "
        "cleanup; genuine reuse confirmed by READING event_bundle.py (_selftest_reuses_role_slot_summarizer_flat "
        "asserts encode_event == RoleSlotSummarizer.summarize_flat BIT-FOR-BIT), not a re-impl. (2) CONFLICT "
        "DETECTION P/R 1.000, confusion tp40/fp0/tn120/fn0 reproduced. CRUX construction-fairness: measured the "
        "sr_key cosine distribution -- SAME (s,r) = EXACTLY 1.0000 (60/60, because same-(s,r) is a bit-identical "
        "2-pair quantized bundle), share-subj max 0.5112, share-rel max 0.5310, share-none max 0.2837 -> the 0.75 "
        "threshold sits in a ~0.47-wide gap (ROBUST placement) BUT detection is effectively an EXACT (s,r) "
        "dictionary lookup (HD signature + a redundant exact string-confirm in _find_same_sr); no fuzzy / "
        "surface-variant conflict is tested. (3) THE 4 TRUST RULES 40/40 reproduced (worked_examples show REPLACE/"
        "DROP/FLAG/COMBINE each firing with recovered provenance). (4) CLEAN FALSE-FLAG 0.000 (0/120) reproduced "
        "-- HONEST FRAME: this is CORRECT-BY-DESIGN for a trust arbiter (a non-conflicting fact has nothing to "
        "arbitrate), NOT solved correctness-vetting; 'beats the 0.53 auditor' is APPLES-TO-ORANGES (the auditor "
        "did correctness-vetting with an internal ontology; this does conflict-arbitration only). (5) O(n) / "
        "capacity CRUX confirmed by SOURCE inspection: _find_same_sr stacks M over ALL active facts + full cosine "
        "+ a per-candidate glass-box recover_fact (O(vocab) cleanup) -- it does NOT use the substrate's proven "
        "partitioned store / cleanup_family / random_indexing; capacity UN-BENCHMARKED (only 140 facts); "
        "cardinality + source->trust are HAND-tables; no subsumption; status is a symbolic ledger flag not "
        "HD-represented. (6) DETERMINISM: seed7 two runs bit-identical AND seed123 ALSO perfect -> seed-robust, "
        "not seed-lucky. Metrics not hand-edited; all raw counts reproduce bit-for-bit."),
    "framing_correction": atom["framing_correction"],
    "fairness_verdict": ("FAIR on what it measures, but the headline DETECTION metric is CONSTRUCTION-DETERMINED "
        "(same-(s,r) exact 2-pair bundle -> cosine 1.0 + exact string-confirm), so it is a construction-PROOF of "
        "the design plumbing, not a live capability win against a fuzzy alternative. Discriminator CAN fail in "
        "principle (round-trip fails under capacity crosstalk; false-flag fails on a codebook collision; "
        "resolution fails on wrong trust logic) so it is not vacuous -- but the conflict-detection separation "
        "(gap 0.47) is trivially easy by construction. Tier DOWN to MEASURED_MECHANISM: the mechanism (HD-native "
        "facts with bound provenance+trust, glass-box round-trip, trust-ranked resolution) is real and works as "
        "specified; the CLAIM is bounded to a working prototype, not an optimized foundation-scale store."),
    "cross_arc_overlap": atom["cross_arc_overlap"],
    "revival_criteria": atom["revival_criteria"],
    "composes_seq": [], "corrects_seq": [],
    "cert_delta": 1, "net_cert_delta": 1, "store_head_at_write": 29530,
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "decision": ("BANK as MEASURED_MECHANISM (proven-bound / CERT +1). The USER's HD source-trust ingest-vetting "
        "DESIGN is BUILT and WORKS: HD-native facts with provenance+trust bound in (glass-box round-trip 1.000, "
        "genuine EventBundleCodec/RoleSlotSummarizer reuse), conflict detection + 4 trust rules correct (40/40), "
        "clean false-flag 0.000, deterministic + seed-robust. BUT the perfect scores are CONSTRUCTION-DETERMINED "
        "for detection (same-(s,r) exact 2-pair bundle, cosine 1.0; false-flag 0 is correct-by-design for a trust "
        "arbiter, NOT correctness-vetting), and the STORAGE ENGINE is an un-optimized PROTOTYPE: O(n) linear "
        "retrieval bypassing the substrate's partitioned/cleanup/capacity machinery, capacity un-benchmarked, "
        "hand-tables, no subsumption. Design foundation-ready; engine explicitly un-certified for scale. Revival "
        "criteria attached (fuzzy-conflict test + partitioned retrieval + capacity benchmark). Local-only; needs "
        "orchestrator store sync."),
    "local_write_only_no_origin_push_no_remote_persist": True,
    "needs_orchestrator_store_sync": True,
    "ts_iso": ts_iso, "ts": ts, "ts_day": ts_day,
}
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
assert b"\r\n" not in rawl, "CRLF doubling detected in cert_ledger.jsonl after write"
with open(LEDGER, encoding="utf-8") as f:
    vl = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(vl) == len(ledger_lines) + 1
assert vl[-1]["atom_id"] == AID and vl[-1]["ts"] == ts and vl[-1]["seq"] == NEW_SEQ
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)} entries; seq {last_seq} -> {NEW_SEQ}; ts matches atom; no CRLF.")
print("ATOM_ID tail:", AID[-70:])
print("DONE. LOCAL-ONLY. needs_orchestrator_store_sync=True; no origin push; no remote persist.")
