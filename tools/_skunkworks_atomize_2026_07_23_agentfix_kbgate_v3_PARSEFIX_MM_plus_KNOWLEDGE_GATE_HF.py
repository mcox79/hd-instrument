"""
A5-gated LOCAL-ONLY atomize of the MIXED result exp_multipred_argstruct_agentfix_kbgate_v3
(cell commit f0e9ff9c5, cell verdict HARD_FAIL_INTEGRATION_BOUNDED_CEILINGS_COMPOUND).

Two SEPARABLE findings, banked as two atoms (current flat schema; matches 29481/29482):
  Atom A (seq NEW+0)  = PARSE-FIX POSITIVE, MEASURED_MECHANISM / proven-bound / CERT +0.
      The parse-scoped two-pass agent/subject routing fix + a KNOWLEDGE-INDEPENDENT single-patient
      argmax dedup mechanic advance the parser-integrated reader (recall_ceiling 0.6->0.7, F1
      0.4478->0.5738, 7/8 agent-routing regressions closed), arc-scramble-CONFIRMED structure-load-bearing.
  Atom B (seq NEW+1)  = KNOWLEDGE-GATE NEGATIVE, HARD_FAIL / honest-negative / CERT +0.
      The scaled-knowledge patient gate's CONTENT contributes exactly ZERO to the integrated reader:
      V3_INTEGRATED is BYTE-IDENTICAL to V3_KNOWLEDGE_SCRAMBLE (same kept_hash be02002c1579217f). The
      29479 isolated-2AFC +0.199 knowledge win does NOT transfer at real competing-pairs -- coverage-
      limited (the 579-pair table rarely dual-covers both competitors, so argmax is coverage/OOV-driven,
      not plausibility-driven). The must-fail knowledge-scramble control FIRED correctly.

Independent .venv off-disk recompute (metrics.json): every F1 reproduces bit-exact from per-arm
precision/recall; the INTEGRATED==KNOWLEDGE_SCRAMBLE full-record identity is confirmed on disk.
BINARY-SAFE write (newline="") + dynamic count gate + seq continuity. LOCAL WRITE ONLY -- no origin
push, no remote persist.
"""
import json, os, time, tempfile, datetime, hashlib
os.chdir(r"D:\AI\hd-instrument")
ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

# ---- A5 pre-load gate (dynamic counts; serialize-safe) ----
with open(ATOMS, encoding="utf-8") as f:
    atom_lines = [l for l in f.read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]
N_ATOMS = len(parsed)
existing_ids = {o.get("atom_id") or o.get("id") for o in parsed}
assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR -- investigate"
with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]
last_seq = json.loads(ledger_lines[-1])["seq"]
SEQ_A = last_seq + 1
SEQ_B = last_seq + 2
print(f"PRE-GATE: {N_ATOMS} atoms load-valid; ledger last seq {last_seq}; SEQ_A={SEQ_A} SEQ_B={SEQ_B}")

# ---- off-disk recompute confirmation ----
m = json.load(open("data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json", encoding="utf-8"))
assert m["verdict"] == "HARD_FAIL_INTEGRATION_BOUNDED_CEILINGS_COMPOUND"
A = m["arms"]
def f1(p, r): return round(2 * p * r / (p + r), 4) if (p + r) > 0 else 0.0
for name in A:
    assert abs(f1(A[name]["precision"], A[name]["recall"]) - A[name]["f1"]) <= 1e-4, name
# parse-fix numbers
assert A["V2_FRAMES_29478"]["f1"] == 0.4478 and A["V2_FRAMES_29478"]["recall_ceiling"] == 0.6
assert A["V3_PARSEFIX_ONLY"]["f1"] == 0.4651 and A["V3_PARSEFIX_ONLY"]["recall_ceiling"] == 0.7
assert A["V3_INTEGRATED"]["f1"] == 0.5738 and A["V3_INTEGRATED"]["recall_ceiling"] == 0.7
assert A["V3_INTEGRATED"]["precision"] == 0.4861 and A["V3_INTEGRATED"]["recall"] == 0.7
assert A["V3_INTEGRATED"]["within_frame_fp"] == 6 and A["V3_PARSEFIX_ONLY"]["within_frame_fp"] == 44
assert A["BASELINE"]["f1"] == 0.2708  # original single-verb reader (29473)
assert m["agent_routing_closure_fraction"] == 0.875 and m["n_agent_routing"] == 8 and m["n_agent_routing_closed"] == 7
# arc-scramble control fired (structure load-bearing)
assert A["V3_ARCSCRAMBLE"]["f1"] == 0.3114
assert A["V3_INTEGRATED"]["f1"] - A["V3_ARCSCRAMBLE"]["f1"] >= 0.05
assert m["hard_pass_conditions"]["control_arcscramble"] is True
# KNOWLEDGE-content-null: INTEGRATED byte-identical to KNOWLEDGE_SCRAMBLE
assert A["V3_INTEGRATED"] == A["V3_KNOWLEDGE_SCRAMBLE"], "expected byte-identical INTEGRATED vs KNOWLEDGE_SCRAMBLE"
assert A["V3_INTEGRATED"]["kept_hash"] == A["V3_KNOWLEDGE_SCRAMBLE"]["kept_hash"] == "be02002c1579217f"
assert m["hard_pass_conditions"]["control_knowledge_scramble"] is False
assert m["hard_fail_reasons"] and "KNOWLEDGE_SCRAMBLE" in m["hard_fail_reasons"][0]
assert m["learning_curve"]["lc_rise"] == 0.04
print("OFF-DISK OK: F1 all reproduce from p/r; V2 0.4478 -> PARSEFIX 0.4651 (+0.0173 parse routing) "
      "-> INTEGRATED 0.5738 (+0.1087 KNOWLEDGE-INDEPENDENT patient-dedup); rc 0.6->0.7 (parse-fix); "
      "agent closure 7/8=0.875; ARCSCRAMBLE 0.3114 (structure load-bearing, control FIRED); "
      "INTEGRATED==KNOWLEDGE_SCRAMBLE byte-identical hash be02002c1579217f (knowledge CONTENT null, "
      "control FIRED as must-fail); lc_rise 0.04 noisy.")

cell_path = "experiments/exp_multipred_argstruct_agentfix_kbgate_v3.py"
cell_sha = hashlib.sha256(open(cell_path, "rb").read()).hexdigest()[:16]
CELL_COMMIT = "f0e9ff9c5"
METRICS_PATH = "data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json"
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
ts = "2026-07-23"

# =====================================================================================
# ATOM A -- PARSE-FIX POSITIVE (MEASURED_MECHANISM)
# =====================================================================================
AID_A = ("math::multipred_argstruct_agentfix_v3_MEASURED_MECHANISM_SEPARABLE_POSITIVE_from_cell_HARD_FAIL_"
    "the_parse_scoped_TWO_PASS_agent_subject_routing_fix_closes_7of8_of_29478s_localized_agent_routing_"
    "regressions_frac_0p875_and_lifts_the_parser_integrated_reader_recall_ceiling_0p6_to_0p7_pure_parse_"
    "routing_F1_0p4478_to_0p4651_plus0p0173_then_a_KNOWLEDGE_INDEPENDENT_single_patient_argmax_DEDUP_"
    "mechanic_lifts_F1_0p4651_to_0p5738_plus0p1087_precision_0p3483_to_0p4861_within_frame_fp_44_to_6_"
    "cumulative_over_the_original_single_verb_reader_29473_baseline_F1_0p2708_to_0p5738_ARC_SCRAMBLE_"
    "CONTROL_CONFIRMS_structure_is_load_bearing_F1_collapses_to_0p3114_margin_0p2624_31_recovered_5_"
    "regressed_vs_baseline_pre_reg_bars_set_before_run_grounded_on_cited_29478_landed_anchor_plus0p02_"
    "not_floor_hugged_INTEGRATED_clears_them_comfortably_MM_NOT_CG_single_seed_parser_train_plus_UD_EWT_"
    "to_McGuffey_out_of_domain_transfer_untested_flagged_composes_29478_parser_29473_reader_CERT_plus0_"
    "LOCAL_ONLY_2026-07-23")
assert AID_A not in existing_ids

HEAD_A = ("agentfix_kbgate_v3 SEPARABLE POSITIVE -> MEASURED_MECHANISM (banked from an overall-HARD_FAIL "
    "cell). The parse-scoped two-pass agent/subject routing fix (PASS 1 = 29478's ascend-only walk, PASS 2 "
    "= fallback checking each visited node for a direct-child predicate) closes 7/8 of 29478's localized "
    "agent-routing regressions (frac 0.875) and lifts the parser-integrated reader recall_ceiling 0.6->0.7 "
    "with pure-parse-routing F1 0.4478->0.4651 (+0.0173); a SECOND, KNOWLEDGE-INDEPENDENT single-patient "
    "argmax DEDUP mechanic then lifts F1 0.4651->0.5738 (+0.1087; precision 0.3483->0.4861, within_frame_fp "
    "44->6). Cumulative over the original single-verb reader (29473 baseline F1 0.2708) -> 0.5738, a real "
    "reader-accuracy advance. ARC-SCRAMBLE control CONFIRMS the parse structure is load-bearing (F1 "
    "collapses to 0.3114, margin 0.2624). 31 recovered / 5 regressed vs baseline. MM not CG (single-seed "
    "parser training; UD-EWT->McGuffey out-of-domain transfer untested/flagged).")

DEC_A = ("landed_vet_atomize: SEPARABLE POSITIVE from cell HARD_FAIL_INTEGRATION_BOUNDED_CEILINGS_COMPOUND "
    "-> MEASURED_MECHANISM (proven-bound; CERT +0). Independent .venv off-disk recompute (metrics.json): "
    "every arm F1 reproduces bit-exact from its own precision/recall. PARSE-FIX REAL y: recall_ceiling 0.6 "
    "(V2_FRAMES_29478) -> 0.7 (V3_PARSEFIX_ONLY AND V3_INTEGRATED, so the ceiling gain is 100% the parse-"
    "fix, knowledge/dedup only touch precision); F1 0.4478->0.4651 pure parse routing; agent-routing closure "
    "7/8 = 0.875 (n=8). FRAMING CORRECTION (symmetric anti-negativity, UPWARD honesty check on the win's "
    "attribution): the cell/Director framing 'the parse-fix took F1 0.4478->0.5738' is an OVER-ATTRIBUTION "
    "-- the CLEAN parse-routing fix is 0.4478->0.4651 (+0.0173); the further +0.1087 to 0.5738 is a "
    "KNOWLEDGE-INDEPENDENT single-patient argmax DEDUP mechanic (keep only ONE of >=2 competing PATIENT "
    "candidates), PROVEN knowledge-independent because V3_INTEGRATED is BYTE-IDENTICAL to V3_KNOWLEDGE_"
    "SCRAMBLE (kept_hash be02002c1579217f). So the positive = TWO knowledge-independent structural mechanics "
    "(parse routing + patient dedup), NEITHER is the knowledge CONTENT. Both are real: dedup drops "
    "within_frame_fp 44->6 and lifts precision 0.3483->0.4861. Cumulative over the original single-verb "
    "reader (29473 baseline F1 0.2708) -> 0.5738. ARC-SCRAMBLE control FIRED (F1 0.3114, collapse margin "
    "0.2624 >= 0.05 bar) -> parse structure is genuinely load-bearing, not an artifact. Pre-reg bars "
    "(HP_F1_MIN 0.4678 = cited 0.4478+0.02; HP_RECALL_MIN 0.62 = 0.6+0.02) were set BEFORE the run grounded "
    "on 29478's landed anchor, NOT floor-hugged -- INTEGRATED clears them comfortably; the cell's overall "
    "HARD_FAIL is triggered ONLY by the knowledge-scramble control (banked separately as the HF atom). Grade "
    "MEASURED_MECHANISM not CG: single-seed parser training + untested UD-EWT->19thc-McGuffey transfer "
    "(cell's own flagged scope caveat). Cross-arc overlap: substrate_query top hit 0.3223 is a strategic-"
    "overview NOTE (non-cell); nearest experiment cells are the DIRECT lineage 29478/29473 this cell extends "
    "by design -- targeted extension, NOT a rediscovery. CERT +0. Composes 29478 (parser, not superseded) + "
    "29473 (reader, not superseded). LOCAL-ONLY needs orchestrator sync.")

KM_A = {
    "v2_frames_29478_f1": 0.4478, "v2_frames_29478_recall_ceiling": 0.6, "v2_frames_29478_precision": 0.3571,
    "parsefix_only_f1": 0.4651, "parsefix_only_recall_ceiling": 0.7, "parsefix_only_precision": 0.3483,
    "parsefix_only_within_frame_fp": 44,
    "integrated_f1": 0.5738, "integrated_recall_ceiling": 0.7, "integrated_precision": 0.4861,
    "integrated_within_frame_fp": 6,
    "pure_parse_routing_f1_gain": 0.0173, "patient_dedup_f1_gain_knowledge_independent": 0.1087,
    "baseline_original_reader_29473_f1": 0.2708, "cumulative_reader_advance_f1": 0.5738,
    "agent_routing_n": 8, "agent_routing_closed": 7, "agent_routing_closure_fraction": 0.875,
    "arcscramble_f1": 0.3114, "arcscramble_collapse_margin": 0.2624, "control_arcscramble_fired": True,
    "n_recovered_v3": 31, "n_regressed_v3": 5,
    "hp_f1_min_preset": 0.4678, "hp_recall_min_preset": 0.62, "bars_floor_hugged": False,
    "parser_uas_dev": 0.7882, "parser_single_seed": True,
    "integrated_eq_knowledge_scramble_hash": "be02002c1579217f",
    "note": "parse-fix + dedup are knowledge-INDEPENDENT structural mechanics; the knowledge CONTENT null is the sister HF atom",
}

atom_A = {
    "atom_id": AID_A, "corpus": "math", "tier": "MEASURED_MECHANISM", "cert_status": "proven-bound",
    "anchor_name": "multipred_argstruct_agentfix_kbgate_v3", "cell": cell_path,
    "cell_commit": CELL_COMMIT, "cell_content_sha256_16": cell_sha, "metrics_path": METRICS_PATH,
    "verdict": "HARD_FAIL_INTEGRATION_BOUNDED_CEILINGS_COMPOUND(cell)__MM_SEPARABLE_PARSEFIX_POSITIVE(atom)",
    "grade": "MEASURED_MECHANISM", "auditor": "hdi_skunkworks", "verified_off_data": True,
    "cert_delta": 0, "net_cert_delta": 0, "composes_seq": [29478, 29473], "seq": SEQ_A,
    "store_head_at_write": last_seq, "headline": HEAD_A, "decision": DEC_A, "key_metrics": KM_A,
    "cross_arc_overlap": ("substrate_query top hit 0.3223 = strategic-overview NOTE (non-cell); nearest "
        "experiment cells are the DIRECT lineage 29478 parser / 29473 reader this cell extends by design -- "
        "targeted extension not rediscovery"),
    "ts_iso": ts_iso, "ts": ts, "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True, "op": "add", "cert_class": "proven-bound",
}
json.loads(json.dumps(atom_A))

# =====================================================================================
# ATOM B -- KNOWLEDGE-GATE NEGATIVE (HARD_FAIL / honest-negative)
# =====================================================================================
AID_B = ("math::multipred_argstruct_kbgate_v3_HARD_FAIL_honest_negative_the_29479_scaled_selectional_"
    "KNOWLEDGE_CONTENT_does_NOT_integrate_into_the_reader_at_real_competing_pairs_V3_INTEGRATED_is_BYTE_"
    "IDENTICAL_to_V3_KNOWLEDGE_SCRAMBLE_same_kept_hash_be02002c1579217f_so_the_knowledge_gates_PICK_is_"
    "100pct_knowledge_INDEPENDENT_on_this_slice_zero_of_the_multi_patient_competition_instances_pick_"
    "differently_under_scrambled_vs_real_table_CAUSE_is_COVERAGE_the_579_pair_table_rarely_DUAL_covers_"
    "both_competing_patient_candidates_so_argmax_with_OOV_treated_as_minus1p0_picks_the_COVERED_one_"
    "regardless_of_its_rating_value_and_scrambling_that_value_cannot_flip_it_because_the_competitor_is_"
    "OOV_the_29479_isolated_2AFC_plus0p199_knowledge_win_had_BOTH_candidates_in_table_BY_CONSTRUCTION_but_"
    "real_reader_competitions_have_OOV_competitors_so_the_knowledge_does_NOT_transfer_ATTRIBUTION_coverage_"
    "POVERTY_bound_NOT_test_design_failure_the_gate_is_LIVE_witness_admire_beauty_over_way_passes_arc_"
    "scramble_differs_dedup_fires_the_must_fail_knowledge_scramble_control_FIRED_correctly_caught_the_null_"
    "learning_curve_rise_0p04_noisy_dips_to_0p4359_at_frac_0p5_REVIVAL_denser_table_covering_BOTH_"
    "competitors_at_real_decision_points_OR_OOV_back_off_smoothing_echoes_29481_condenser_auditor_"
    "knowledge_independent_discrimination_via_scramble_composes_29479_knowledge_29473_reader_29478_parser_"
    "CERT_plus0_LOCAL_ONLY_2026-07-23")
assert AID_B not in existing_ids

HEAD_B = ("agentfix_kbgate_v3 KNOWLEDGE-GATE -> HARD_FAIL (honest-negative). The 29479 scaled selectional "
    "KNOWLEDGE CONTENT does NOT integrate into the reader at real competing-pairs: V3_INTEGRATED is "
    "BYTE-IDENTICAL to V3_KNOWLEDGE_SCRAMBLE (same kept_hash be02002c1579217f) -- the gate's pick is 100% "
    "knowledge-independent on this slice (0 multi-patient-competition instances pick differently under a "
    "scrambled vs the real table). CAUSE = coverage: the 579-pair table rarely DUAL-covers both competing "
    "patients, so argmax (OOV = -1.0) picks the COVERED one regardless of its rating value, and scrambling "
    "that value cannot flip it while the competitor is OOV. The 29479 isolated-2AFC +0.199 win had BOTH "
    "candidates in-table BY CONSTRUCTION; real reader competitions have OOV competitors, so the knowledge "
    "does NOT transfer. Coverage-POVERTY bound, NOT a test-design failure (the gate is LIVE: the synthetic "
    "admire|beauty>way witness passes, arc-scramble differs, the dedup fires). The must-fail knowledge-"
    "scramble control FIRED correctly and is what triggers the cell's overall HARD_FAIL. Revival: denser "
    "table covering both competitors at real decision points, OR OOV back-off smoothing.")

DEC_B = ("landed_vet_atomize: KNOWLEDGE-GATE HARD_FAIL honest-negative (CERT +0). Independent .venv off-disk "
    "recompute confirms the load-bearing evidence directly on disk: V3_INTEGRATED's FULL arm record is "
    "byte-identical to V3_KNOWLEDGE_SCRAMBLE (precision 0.4861 / recall 0.7 / f1 0.5738 / n_pred 144 / "
    "within_frame_fp 6 / kept_hash be02002c1579217f all identical) -> the scaled-knowledge table's CONTENT "
    "contributes EXACTLY ZERO to the integrated reader; permuting its 579 values across keys changes NO "
    "pick. GENUINE-COVERAGE-BOUND y (not a fixable wiring artifact): the argmax patient gate scores OOV "
    "pairs as -1.0 (strictly below any rated pair) with leftmost tie-break; when only ONE of two competing "
    "patients is in-table (the common case at real decision points), argmax picks the covered one in BOTH "
    "the real and scrambled table (any real value in [0,1] > -1.0 OOV), so the pick is COVERAGE/OOV-driven, "
    "not plausibility-driven; a flip requires BOTH competitors in-table, which is rare (0 observed). This is "
    "why the 29479 +0.199 isolated-2AFC knowledge win FAILS to transfer to the integrated reader: the 2AFC "
    "had both candidates in-table BY CONSTRUCTION; the reader's real competing-pairs have OOV competitors. "
    "ANTI-CHEAT FIRED CORRECTLY y: this is the guard working as intended, not a bug -- the knowledge-scramble "
    "must-fail control caught that discrimination is knowledge-independent and correctly demoted an otherwise-"
    "HP-looking F1 (all other HP conditions passed) to HARD_FAIL. ATTRIBUTION = coverage POVERTY bound, NOT "
    "HF_TEST_DESIGN_FAILURE: positive controls clear their floors -- BASELINE precision 0.1956 in-band, "
    "arc-scramble collapses (structure load-bearing), the synthetic knowledge-gate witness (admire|beauty "
    "0.9 > admire|way 0.15) passes in isolation, and the dedup fires -- so the gate is CAPABLE of acting; it "
    "simply never gets the chance at real competing-pairs due to coverage. FRAMING CORRECTION (for Director): "
    "the cell's hard_pass_condition 'knowledge_adds=True' is MISLABELED -- it measures gate-vs-no-gate (the "
    "dedup), NOT knowledge-vs-scramble; the decisive knowledge test is control_knowledge_scramble=False. So "
    "'knowledge adds' is really 'dedup adds'; the knowledge CONTENT adds nothing. Learning-curve rise 0.04 "
    "is a NOISY non-signal (dips to 0.4359 at frac 0.5, peaks 0.5783 at 0.75). Cross-arc: ECHOES 29481 "
    "(condenser-as-auditor) which independently found LLM-knowledge discrimination is knowledge-independent "
    "via a scramble control on a different mechanism -- same finding-shape, genuine replication not "
    "rediscovery. REVIVAL: denser selectional table that covers BOTH competitors at real decision points, OR "
    "OOV back-off / smoothing so the gate can discriminate when one competitor is unrated. Grade HARD_FAIL "
    "(proven NEGATIVE: knowledge content does not integrate at real competing-pairs, coverage-limited). CERT "
    "+0. Composes 29479 (knowledge table, not superseded -- its isolated win stands, this bounds its "
    "transfer) + 29473 (reader) + 29478 (parser). LOCAL-ONLY needs orchestrator sync.")

KM_B = {
    "integrated_kept_hash": "be02002c1579217f", "knowledge_scramble_kept_hash": "be02002c1579217f",
    "integrated_eq_knowledge_scramble_full_record": True, "picks_changed_under_scramble": 0,
    "integrated_f1": 0.5738, "knowledge_scramble_f1": 0.5738,
    "control_knowledge_scramble_fired_correctly": True,
    "cited_29479_isolated_2afc_knowledge_lift": 0.199, "isolated_2afc_both_candidates_in_table_by_construction": True,
    "knowledge_table_n_pairs": 579, "cause": "coverage_table_rarely_dual_covers_both_competitors_argmax_OOV_neg1_picks_covered",
    "attribution": "coverage_poverty_bound_not_test_design_failure",
    "positive_controls_clear_floor": True, "baseline_precision_in_band": 0.1956,
    "arcscramble_structure_load_bearing": True, "knowledge_gate_witness_passes_in_isolation": True,
    "learning_curve_rise": 0.04, "learning_curve_points_f1": [0.5338, 0.4359, 0.5783, 0.5738],
    "learning_curve_noisy_non_signal": True,
    "revival": "denser_table_dual_covering_competitors_OR_OOV_back_off_smoothing",
    "echoes_seq": 29481,
}

atom_B = {
    "atom_id": AID_B, "corpus": "math", "tier": "HARD_FAIL", "cert_status": "honest-negative",
    "anchor_name": "multipred_argstruct_agentfix_kbgate_v3", "cell": cell_path,
    "cell_commit": CELL_COMMIT, "cell_content_sha256_16": cell_sha, "metrics_path": METRICS_PATH,
    "verdict": "HARD_FAIL_INTEGRATION_BOUNDED_CEILINGS_COMPOUND",
    "grade": "HARD_FAIL", "auditor": "hdi_skunkworks", "verified_off_data": True,
    "cert_delta": 0, "net_cert_delta": 0, "composes_seq": [29479, 29473, 29478], "seq": SEQ_B,
    "store_head_at_write": SEQ_A, "headline": HEAD_B, "decision": DEC_B, "key_metrics": KM_B,
    "cross_arc_overlap": ("ECHOES 29481 condenser-as-auditor (LLM-knowledge discrimination is knowledge-"
        "independent via scramble control, different mechanism) -- same finding-shape, genuine replication "
        "not rediscovery; lineage cells 29479/29473/29478 are the intended composition targets"),
    "ts_iso": ts_iso, "ts": ts, "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True, "op": "add", "cert_class": "honest-negative",
}
json.loads(json.dumps(atom_B))

# ---- A5 atomic append of BOTH atoms (BINARY-SAFE newline="") ----
new_lines = [json.dumps(atom_A, ensure_ascii=False), json.dumps(atom_B, ensure_ascii=False)]
for nl in new_lines:
    assert "\r" not in nl and "\n" not in nl
new_atoms_text = "\n".join(atom_lines + new_lines) + "\n"
d = os.path.dirname(os.path.abspath(ATOMS))
fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp"); os.close(fd)
with open(tmp, "w", encoding="utf-8", newline="") as f:
    f.write(new_atoms_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp, ATOMS)
with open(ATOMS, "rb") as f:
    assert b"\r\n" not in f.read(), "CRLF doubling in atoms.jsonl"
with open(ATOMS, encoding="utf-8") as f:
    v = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(v) == N_ATOMS + 2, (len(v), N_ATOMS)
assert v[-2]["atom_id"] == AID_A and v[-2]["tier"] == "MEASURED_MECHANISM" and v[-2]["seq"] == SEQ_A
assert v[-1]["atom_id"] == AID_B and v[-1]["tier"] == "HARD_FAIL" and v[-1]["seq"] == SEQ_B
print(f"ATOMS OK: {N_ATOMS} -> {len(v)}; A(MM seq {SEQ_A}) + B(HF seq {SEQ_B}) verified; no CRLF doubling.")

# ---- ledger entries (both) ----
def ledger_entry(seq, atom_id, grade, cert_status, cert_class, decision, note, cross, head_at):
    return {
        "seq": seq, "op": "add", "corpus": "math", "tier": grade, "cert_status": cert_status,
        "cert_class": cert_class, "atom_id": atom_id, "anchor_name": "multipred_argstruct_agentfix_kbgate_v3",
        "cell": cell_path, "cell_commit": CELL_COMMIT, "cell_content_sha256_16": cell_sha,
        "auditor": "hdi_skunkworks", "verified_off_data": True, "cert_delta": 0, "net_cert_delta": 0,
        "composes_seq": ([29478, 29473] if seq == SEQ_A else [29479, 29473, 29478]),
        "decision": decision, "note": note, "cross_arc_overlap": cross,
        "ts_iso": ts_iso, "ts": ts, "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True, "store_head_at_write": head_at,
    }

NOTE_A = ("SEPARABLE POSITIVE banked MM from an overall-HARD_FAIL cell. Parse-scoped two-pass agent/subject "
    "routing fix closes 7/8 agent-routing regressions (0.875) and lifts recall_ceiling 0.6->0.7 (parse-fix "
    "owns the ceiling gain 100%). Pure parse routing F1 0.4478->0.4651; a KNOWLEDGE-INDEPENDENT single-"
    "patient argmax DEDUP then F1 0.4651->0.5738 (precision 0.3483->0.4861, within_frame_fp 44->6). "
    "CORRECTION: do NOT attribute the full 0.4478->0.5738 to 'the parse-fix' -- half is the dedup mechanic, "
    "proven knowledge-independent (INTEGRATED==KNOWLEDGE_SCRAMBLE). Arc-scramble control FIRED (F1 0.3114) "
    "-> structure load-bearing. Cumulative over original reader 0.2708->0.5738. MM not CG (single-seed "
    "parser; UD-EWT->McGuffey transfer untested). Composes 29478+29473. LOCAL-ONLY.")
NOTE_B = ("KNOWLEDGE-GATE honest-negative banked HARD_FAIL. The 29479 scaled selectional KNOWLEDGE CONTENT "
    "does NOT integrate into the reader: V3_INTEGRATED byte-identical to V3_KNOWLEDGE_SCRAMBLE (hash "
    "be02002c1579217f), 0 picks change under scramble. CAUSE = coverage (579-pair table rarely dual-covers "
    "both competitors; argmax OOV=-1.0 picks the covered one, scramble can't flip it). The isolated-2AFC "
    "+0.199 win had both candidates in-table by construction; real competitions have OOV competitors -> "
    "knowledge does NOT transfer. Coverage-POVERTY bound not test-design failure (gate is live: witness "
    "passes, arc-scramble differs, dedup fires). Anti-cheat knowledge-scramble control FIRED correctly = the "
    "guard working. Cell's 'knowledge_adds=True' is MISLABELED (it's the dedup, not knowledge content). "
    "lc_rise 0.04 noisy. Echoes 29481. Revival: denser dual-covering table OR OOV back-off. Composes "
    "29479+29473+29478. LOCAL-ONLY.")

led_A = ledger_entry(SEQ_A, AID_A, "MEASURED_MECHANISM", "proven-bound", "proven-bound", DEC_A, NOTE_A,
                     atom_A["cross_arc_overlap"], last_seq)
led_B = ledger_entry(SEQ_B, AID_B, "HARD_FAIL", "honest-negative", "honest-negative", DEC_B, NOTE_B,
                     atom_B["cross_arc_overlap"], SEQ_A)
for e in (led_A, led_B):
    json.loads(json.dumps(e))
new_led_lines = [json.dumps(led_A, ensure_ascii=False), json.dumps(led_B, ensure_ascii=False)]
for nl in new_led_lines:
    assert "\r" not in nl and "\n" not in nl
new_ledger_text = "\n".join(ledger_lines + new_led_lines) + "\n"
dl = os.path.dirname(os.path.abspath(LEDGER))
fd2, tmp2 = tempfile.mkstemp(dir=dl, suffix=".tmp"); os.close(fd2)
with open(tmp2, "w", encoding="utf-8", newline="") as f:
    f.write(new_ledger_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp2, LEDGER)
with open(LEDGER, "rb") as f:
    assert b"\r\n" not in f.read(), "CRLF doubling in cert_ledger.jsonl"
with open(LEDGER, encoding="utf-8") as f:
    vl = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(vl) == len(ledger_lines) + 2
assert vl[-2]["seq"] == SEQ_A and vl[-2]["atom_id"] == AID_A
assert vl[-1]["seq"] == SEQ_B and vl[-1]["atom_id"] == AID_B
assert vl[-3]["seq"] == last_seq, "seq continuity broken"
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)}; seq {last_seq} -> {SEQ_A},{SEQ_B}; no CRLF.")
print("DONE. LOCAL-ONLY; no origin push; no remote persist. needs_orchestrator_store_sync=True")
