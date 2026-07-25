"""A5-gated LOCAL-ONLY atomize: exp_arc_derivation_rule_supply_science_extract_v1 (commit 182b82a5f).
tier=MEASURED_MECHANISM / proven-bound. Cell verdict PROMISCUOUS (GATE_MEASURED). Closes the rule-supply
selectivity arc: science-precise extraction (the source 29554 redirected to) raises COVERAGE but gives NO
SELECTIVITY, converging with commonsense-CSKG (29553/29554) -> the depth-3 typed-connectivity GATE is the
bound, not the rule source. Rule-supply alone does NOT unblock Step 2 (the reasoner).

INDEPENDENT off-disk recompute (.venv, metrics.json):
 - positive control worldtree typed cov 0.070 REPRODUCES parent 29552 clean typed cov 0.060 (STILL_STARVED)
   -> genuine measured negative, not a test-design failure; the test CAN show coverage (science hits 0.50).
 - COVERAGE ROSE 0.07 -> 0.50 (science_extract, 5028 induced rules) -> corpus/extraction is NOT the coverage
   bottleneck (kills the RED 'broaden source' hypothesis). union 0.56.
 - SELECTIVITY is anti-selective/promiscuous: science typed sel_gap = correct_cov 0.50 - mean_wrong 0.559 =
   -0.0589, WORSE than untyped-null -0.0004; union typed -0.0494 vs untyped +0.0117 -> typed does NOT beat
   untyped-null (PROMISCUOUS band by pre-reg cov>0.5 AND typed_gap<=untyped).
 - STRUCTURAL not merely noisy: (a) untyped-NULL selectivity gap is ALSO ~0 (correct 0.71 vs wrong 0.710)
   => depth-3 REACHABILITY itself does not separate gold from distractor regardless of typing; (b)
   max_typed_deg 138-160 mega-hubs (label 'water'); (c) example_chains are VACUOUS single-word-overlap hub
   bridges (use->effects->size) = the same pattern 29553 flagged; (d) adding cleaner worldtree rules
   (union) did NOT improve selectivity (untyped gap went +0.0117). Precision ~0.45-0.55 (wellformed_proxy
   1.0 is a cheap lower-bar, NOT true precision) contributes noise but is not the root cause. Residual
   OPEN: no precision-controlled / shorter-depth / hub-capped ablation was run -> a precision-first v2 is
   the untested revival, but the convergence with the CSKG arc makes it a WEAK revival.
"""
import json, os, time, tempfile, datetime, hashlib

ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

with open(ATOMS, encoding="utf-8") as f:
    atom_lines = [l for l in f.read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]
assert len(parsed) == 29555, f"expected 29555 atoms pre-write, got {len(parsed)}"
existing_ids = {o.get("atom_id") for o in parsed if o.get("atom_id")}
assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR"

with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]
lp = [json.loads(l) for l in ledger_lines]
last_seq = [o["seq"] for o in lp if "seq" in o][-1]
assert last_seq == 29558, f"expected ledger last seq 29558, got {last_seq}"
NEW_SEQ = 29559
print(f"PRE-GATE: {len(parsed)} atoms; ledger last {last_seq}; NEW_SEQ {NEW_SEQ}.")

M = json.load(open("data/exp_arc_derivation_rule_supply_science_extract_v1/metrics.json", encoding="utf-8"))
assert M["headline_band"] == "PROMISCUOUS_FAIL" and M["verdict"] == "GATE_MEASURED"
assert M["positive_control_ok"] is True and abs(M["positive_control_worldtree_cov"] - 0.07) < 1e-6
R = M["results"]
assert abs(R["worldtree"]["typed_correct_coverage"] - 0.07) < 1e-6
assert abs(R["science_extract"]["typed_correct_coverage"] - 0.50) < 1e-6
assert abs(R["science_extract"]["typed_selectivity_gap"] - (-0.0589)) < 1e-4
assert abs(R["science_extract"]["untyped_selectivity_gap"] - (-0.0004)) < 1e-4
assert R["science_extract"]["typed_gap_beats_untyped"] is False
assert abs(R["worldtree_science"]["typed_correct_coverage"] - 0.56) < 1e-6
assert abs(R["worldtree_science"]["untyped_selectivity_gap"] - 0.0117) < 1e-4
assert M["extraction"]["n_induced_rows"] == 5028
print("OFF-DISK OK: PROMISCUOUS; posctrl 0.07 repro; science cov 0.50 gap -0.0589 vs untyped -0.0004; "
      "union cov 0.56 untyped_gap +0.0117; n_induced 5028.")

cell_sha16 = hashlib.sha256(open("experiments/exp_arc_derivation_rule_supply_science_extract_v1.py", "rb").read()).hexdigest()[:16]
metrics_sha16 = hashlib.sha256(open("data/exp_arc_derivation_rule_supply_science_extract_v1/metrics.json", "rb").read()).hexdigest()[:16]
assert cell_sha16 == "a188cd2f0d45db50", cell_sha16
assert metrics_sha16 == "77ebf9b87a2eeb63", metrics_sha16

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
ts_day = "2026-07-25"

AID = ("math::arc_derivation_rule_supply_science_extract_v1_MEASURED_MECHANISM_SCIENCE_PRECISE_rule_extraction_"
    "the_source_29554_redirected_to_raises_COVERAGE_but_gives_NO_SELECTIVITY_CLOSING_the_rule_supply_arc_positive_"
    "control_worldtree_typed_cov_0p070_REPRODUCES_29552_clean_0p060_STILL_STARVED_genuine_measured_negative_not_"
    "test_design_failure_science_extract_5028_induced_rows_typed_cov_0p50_COVERAGE_ROSE_from_0p07_so_corpus_"
    "extraction_is_NOT_the_coverage_bottleneck_kills_RED_broaden_source_BUT_typed_selectivity_gap_correct_0p50_"
    "minus_mean_wrong_0p559_eq_neg0p0589_WORSE_than_untyped_null_neg0p0004_typed_does_NOT_beat_untyped_PROMISCUOUS_"
    "union_worldtree_science_6896_rows_cov_0p56_typed_gap_neg0p0494_vs_untyped_plus0p0117_STRUCTURAL_not_merely_"
    "noisy_because_untyped_NULL_selectivity_ALSO_approx_zero_correct_0p71_vs_wrong_0p710_so_depth3_REACHABILITY_"
    "itself_does_NOT_separate_gold_from_distractor_regardless_of_typing_max_typed_deg_138_to_160_mega_hubs_water_"
    "example_chains_VACUOUS_single_word_overlap_hub_bridges_use_effects_size_same_pattern_as_29553_CSKG_and_adding_"
    "cleaner_worldtree_rules_union_did_NOT_improve_selectivity_precision_0p45_to_0p55_wellformed_proxy_1p0_is_cheap_"
    "lower_bar_not_true_precision_contributes_noise_but_not_root_cause_residual_OPEN_no_precision_controlled_shorter_"
    "depth_hub_capped_ablation_so_precision_first_v2_is_untested_WEAK_revival_given_arc_convergence_rule_supply_"
    "alone_gives_coverage_NOT_selectivity_similarity_reachability_NOT_entailment_does_NOT_unblock_Step2_reasoner_"
    "the_depth3_typed_connectivity_GATE_is_the_bound_not_the_rule_source_composes_29551_29552_29553_29554_CERT_"
    "plus1_proven_bound_LOCAL_ONLY_2026_07_25")
assert AID not in existing_ids, "duplicate atom id"

HEADLINE = ("SCIENCE-PRECISE rule extraction (the source 29554 redirected to) raises COVERAGE but gives NO "
    "SELECTIVITY -- CLOSING the rule-supply arc (MEASURED_MECHANISM, CERT +1 as a proven bound). Positive control: "
    "worldtree typed cov 0.070 REPRODUCES 29552's clean 0.060 (STILL_STARVED) -> this is a genuine measured "
    "negative, not a test-design failure (and the test CAN show coverage: science hits 0.50). COVERAGE ROSE 0.07 "
    "-> 0.50 (5028 induced science rules from ARC_Corpus) -> corpus/extraction is NOT the coverage bottleneck "
    "(kills the RED 'broaden the source' hypothesis). BUT SELECTIVITY is anti-selective/promiscuous: science typed "
    "sel_gap = correct_cov 0.50 - mean_wrong 0.559 = -0.0589, WORSE than the untyped-NULL gap -0.0004; the union "
    "(worldtree+science, 6896 rules, cov 0.56) is typed -0.0494 vs untyped +0.0117 -> typed connectivity does NOT "
    "beat an untyped null graph. STRUCTURAL, not merely noisy: (a) the untyped-NULL selectivity is ALSO ~0 "
    "(correct 0.71 vs wrong 0.710) so depth-3 REACHABILITY itself does not separate gold from distractor "
    "regardless of typing; (b) max typed degree 138-160 mega-hubs (label 'water'); (c) example chains are VACUOUS "
    "single-word-overlap hub bridges (use->effects->size) -- the same pattern 29553 flagged for CSKG; (d) adding "
    "cleaner worldtree rules (union) did NOT improve selectivity. Extraction precision ~0.45-0.55 (the "
    "wellformed_proxy 1.0 is a cheap automatic lower-bar, NOT true precision) contributes noise but is not the "
    "root cause. NET: rule-supply alone gives COVERAGE not SELECTIVITY; similarity/reachability != entailment; it "
    "does NOT unblock Step 2 (the reasoner). The bound is the depth-3 typed-connectivity GATE mechanism, not the "
    "rule source -- confirmed now across BOTH commonsense-CSKG (29553/29554) AND science-precise extraction.")

key_metrics = {
    "cell_verdict": "PROMISCUOUS_FAIL_GATE_MEASURED", "auditor_tier": "MEASURED_MECHANISM_proven_bound",
    "positive_control_worldtree_typed_cov": 0.07, "positive_control_reproduces_29552_clean": 0.06,
    "positive_control_ok_genuine_negative_not_testdesign_fail": True,
    "worldtree": {"typed_cov": 0.07, "untyped_cov": 0.51, "typed_gap": -0.0041, "untyped_gap": -0.0287,
                  "typed_beats_untyped": True, "band": "STILL_STARVED_RED"},
    "science_extract": {"typed_cov": 0.50, "untyped_cov": 0.71, "typed_gap": -0.0589, "untyped_gap": -0.0004,
                        "typed_beats_untyped": False, "n_rules": 5028, "max_typed_deg": 138, "band": "MIDDLE"},
    "union_worldtree_science": {"typed_cov": 0.56, "untyped_cov": 0.84, "typed_gap": -0.0494,
                                "untyped_gap": 0.0117, "typed_beats_untyped": False, "n_rules": 6896,
                                "max_typed_deg": 160, "band": "PROMISCUOUS_FAIL"},
    "coverage_rose_extraction_not_bottleneck": True,
    "untyped_null_also_flat_gate_is_structural_bound": True,
    "example_chains_vacuous_hub_bridges": True, "hub_label": "water",
    "precision_est": "0.45-0.55", "wellformed_proxy_is_cheap_lowerbar_not_true_precision": True,
    "n_induced_rows": 5028, "n_lines_scanned": 9153968, "n_raw_extracted": 648556,
    "depth": 3, "does_NOT_unblock_step2_reasoner": True,
    "bands_prereg": {"GREEN_cov": 0.35, "GREEN_typed_gap": 0.15, "PROMISCUOUS_cov": 0.5, "RED_cov": 0.15},
}

CERT_CLASS = ("arc_derivation_rule_supply_science_extract_v1_MEASURED_MECHANISM_science_precise_extraction_5028_"
    "rules_coverage_rose_0p07_to_0p50_extraction_NOT_bottleneck_but_typed_selectivity_neg0p0589_worse_than_untyped_"
    "null_neg0p0004_union_typed_neg0p0494_vs_untyped_plus0p0117_PROMISCUOUS_structural_untyped_null_also_flat_"
    "depth3_reachability_non_selective_mega_hubs_138_160_water_vacuous_hub_bridges_precision_0p45_0p55_residual_"
    "open_no_precision_ablation_weak_revival_rule_supply_gives_coverage_not_selectivity_similarity_not_entailment_"
    "does_not_unblock_step2_gate_is_the_bound_not_source_composes_29551_29552_29553_29554")

atom = {
    "atom_id": AID, "seq": NEW_SEQ, "op": "landed_vet_atomize", "corpus": "math",
    "tier": "MEASURED_MECHANISM", "cert_status": "proven-bound", "cert_class": CERT_CLASS,
    "grade": "MM_science_precise_rule_supply_raises_coverage_NO_selectivity_promiscuous_depth3_gate_is_the_structural_bound_not_the_source_closes_rule_supply_arc",
    "verdict": "MEASURED", "anchor": "arc_derivation_rule_supply_science_extract_v1",
    "anchor_name": "arc_derivation_rule_supply_science_extract_v1",
    "cell": "experiments/exp_arc_derivation_rule_supply_science_extract_v1.py",
    "cell_commit": "182b82a5f", "cell_content_sha256_16": cell_sha16,
    "metrics_path": "data/exp_arc_derivation_rule_supply_science_extract_v1/metrics.json",
    "metrics_sha256_16": metrics_sha16,
    "module": "science_precise_IE_extraction_from_ARC_Corpus_6_licensed_relations_CAUSE_IFTHEN_REQUIRES_COUPLEDRELATIONSHIP_SOURCEOF_USEDFOR_induce_subgraph_NegAwareEncoder_head_gate_polarity_merge_gate_build_graph_gated_meet_connected_depth3_ONE_VARIABLE_rule_source_worldtree_vs_science_vs_union_imported_UNCHANGED_from_CSKG_rule_supply_gate",
    "headline": HEADLINE, "key_metrics": key_metrics,
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "composes_seq": [29551, 29552, 29553, 29554], "corrects_seq": [],
    "cert_delta": 1, "net_cert_delta": 1, "store_head_at_write": 29558,
    "cross_arc_overlap": ("This cell IS the direct next step 29554 redirected to ('redirect science precise rule "
        "EXTRACTION'); it composes the rule-supply arc 29551 (connectivity gate, coverage-bound) / 29552 "
        "(cleannodes, coverage-bound confirmed) / 29553 (CSKG rule-supply, coverage-not-selectivity) / 29554 "
        "(depromisc, no recoverable selectivity by degree-filtering). substrate_query on the mechanism returns "
        "only generic concept/wordnet terms ('selectivity','connectivity') at cosine ~0.39, no prior EXPERIMENT "
        "atom -- the real lineage is the composed 29551-29554. This is a planned extension that CLOSES the arc "
        "(both commonsense and science sources tried), NOT a rediscovery."),
    "honest_scope": ("Full run; 6 licensed relations extracted from ARC_Corpus.txt (9.15M lines scanned, 648556 "
        "raw, 500000 kept, 5028 induced rows), depth-3 typed connectivity gate, 100 ARC questions x 4 choices, "
        "ONE-VARIABLE ablation (rule SOURCE only; node-identity/gate/induction/Qs/depth/thresholds imported "
        "UNCHANGED from the CSKG rule-supply cell). The PROMISCUOUS read is STRONGLY disk-supported (typed <= "
        "untyped-null on selectivity across science and union; untyped-null itself flat; mega-hubs; vacuous "
        "chains; union does not help). The one thing NOT tested is a precision-controlled ablation: extraction "
        "precision is ~0.45-0.55 (the reported wellformed_proxy=1.0 is a cheap automatic 'args are content words "
        "that differ' lower-bar, explicitly NOT true precision per the cell's own note), and no shorter-depth / "
        "hub-capped / high-precision-only arm was run. So 'promiscuity is purely structural' is FAVORED (medium-"
        "high confidence) but not fully closed vs 'partly extraction-noise'. The convergence with 29553/29554 "
        "(commonsense CSKG showed the same coverage-not-selectivity with a decisive de-confounded degree-filter "
        "sweep) is what tips it structural: a cleaner source (science) reached the same wall a noisier source did, "
        "and untyped-null reachability is non-selective independent of the rules."),
    "framing_correction": ("Director framing ('PROMISCUOUS clean; rule-supply alone gives coverage not "
        "selectivity; converges with similarity!=entailment; does NOT unblock Step 2') is UPHELD by disk. "
        "Sharpenings: (1) the strongest structural evidence is that the UNTYPED-NULL selectivity gap is ALSO ~0 "
        "(-0.0004) -- the depth-3 reachability gate is non-discriminative BEFORE typing even enters, so typed "
        "rules connecting wrong answers even more (-0.0589) is the gate + generic-science-hub structure, not "
        "primarily rule noise. (2) COVERAGE definitively is NOT the bottleneck now (0.07->0.50), so the arc's "
        "earlier 'STARVED/RED broaden-source' branch is closed -- the bound moved from coverage (29551/29552) to "
        "SELECTIVITY (29553/29554/this). (3) NOISE-vs-STRUCTURAL: the disk FAVORS structural (medium-high conf) "
        "but does NOT fully close it -- no precision-controlled ablation was run. Honest statement: a precision-"
        "first + shorter-depth + hub-capped v2 is the untested residual, but given the CSKG-arc convergence and "
        "the flat untyped-null, it is a WEAK revival, not a likely unlock. Do NOT invest in the Step-2 reasoner on "
        "the back of this rule supply."),
    "fairness_verdict": ("FAIR, well-controlled one-variable ablation with a real positive control that "
        "reproduces the prior coverage-bound (0.07) and a discriminator that CAN fire (science reaches cov 0.50, "
        "so the test is not rigged to fail on coverage; it fails specifically on selectivity). Pre-registered "
        "bands (GREEN/MIDDLE/PROMISCUOUS/RED) applied straight, not tuned. The only fairness caveat is the absent "
        "precision-controlled arm (noise-vs-structural not fully separated). Tier MEASURED_MECHANISM proven-bound, "
        "CERT +1, consistent with 29553/29554."),
    "revival_criteria": ("Would revisit rule-supply selectivity only with: (1) a PRECISION-FIRST extraction "
        "(high-confidence patterns only, spot-checked true precision >0.8) at shorter depth (1-2 hops) with "
        "hub-capping, testing whether typed_gap clears the PROMISCUOUS line (>0.05) AND beats untyped-null; (2) if "
        "that still fails, the bound is decisively the GATE mechanism (depth-N typed reachability != entailment) "
        "and the lever moves OFF rule-supply entirely to a different entailment/derivation mechanism. Given the "
        "convergence across commonsense (29553/29554) and science sources, (2) is the expected outcome; treat (1) "
        "as a WEAK revival."),
    "adjudication": ("Rule-supply arc CLOSED on the coverage axis and CONVERGED on the selectivity bound: raising "
        "coverage (commonsense CSKG 0.56, science 0.50, union 0.56) never buys selectivity; typed depth-3 "
        "connectivity <= untyped-null across sources; untyped-null itself is non-selective. The depth-3 "
        "typed-connectivity GATE is the proven bound; rule SOURCE is not the lever. Reasoner (Step 2) remains "
        "GATED -- not on rule supply, which is now shown sufficient for coverage and insufficient for selectivity."),
    "promote_verdict": "HOLD_at_MEASURED_MECHANISM_proven_bound",
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
    "store_head_at_write_note": "math atoms=29555 lines, last seq 29558, ledger last seq 29558 at write",
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
assert len(v) == 29556, f"post-write expected 29556, got {len(v)}"
assert v[-1]["atom_id"] == AID and v[-1]["tier"] == "MEASURED_MECHANISM" and v[-1]["cert_status"] == "proven-bound"
print(f"ATOMS OK: now {len(v)} (was 29555); new seq {NEW_SEQ}; no CRLF doubling.")

ledger = dict(atom)
ledger["decision"] = ("BANK as MEASURED_MECHANISM (proven-bound / CERT +1). Science-precise extraction (5028 "
    "rules, the source 29554 redirected to) raises COVERAGE 0.07->0.50 (extraction NOT the bottleneck) but gives "
    "NO SELECTIVITY: typed sel_gap -0.0589 <= untyped-null -0.0004; union typed -0.0494 vs untyped +0.0117. "
    "STRUCTURAL (untyped-null also flat; depth-3 mega-hubs; vacuous chains; union doesn't help) with precision "
    "0.45-0.55 as secondary noise; precision-first ablation UNTESTED (weak revival). Positive control 0.07 "
    "reproduces 29552 = genuine negative. Rule-supply gives coverage not selectivity; does NOT unblock Step 2; the "
    "depth-3 typed-connectivity GATE is the bound, not the source. Composes 29551-29554, closing the rule-supply "
    "arc. Local-only; needs orchestrator store sync.")
ledger["note"] = ("AUDIT-ONLY off-disk recompute (.venv). Reproduced per-source typed/untyped selectivity gaps, "
    "positive control, extraction counts. Confirmed structural read via untyped-null flatness + mega-hub degree "
    "+ vacuous example chains + union-no-help. Noise-vs-structural: structural FAVORED (medium-high), precision-"
    "controlled ablation not run (residual open, weak revival). Hashes: cell a188cd2f0d45db50, metrics "
    "77ebf9b87a2eeb63.")
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
print("DONE cell#2. LOCAL-ONLY. no origin push; no remote persist.")
