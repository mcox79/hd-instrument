"""
A5-gated atomization -- Skunkworks landed-VET 2026-07-05.
COMPREHENSION opening: frame_classify_then_known_decode_v1 (verdict HARD_PASS, run_mode=full,
3 seeds, frame_class/parse/cond_decode all 1.000). AUDIT-ONLY. Independently recomputed off-disk
via .venv (reproduced the cell EXACTLY) PLUS five mechanism/envelope probes the cell does NOT report.

TIER: MEASURED_MECHANISM (proven-bound / honestly-scoped capability OPENING), NOT chain-grade.

WHY MM not CG (symmetric, not over-deflating): the classify-then-decode ARCHITECTURE genuinely
composes end-to-end and the sparse-block-exposes-frame-structure MECHANISM is PROVEN non-vacuously
(paired dense_ctrl collapses to chance 0.078 ~ 1/F). That is real and load-bearing. BUT the headline
1.000 is a COMPOSITION of two by-construction / easy-regime factors, neither under stress at the
anchor:
  (1) FRAME RECOVERY is a DETERMINISTIC set-identity readout. AUDITOR PROBE 1: occupied-block L2
      energy is EXACTLY k=20 and empty-block energy is EXACTLY 0 on every trial; the matched-filter
      score margin (true - best_other) is EXACTLY k=20 (min==max), because each used block holds
      exactly ONE k-sparse filler (no cross-block superposition) so per-block energy = k independent
      of filler identity, and each candidate frame is a DISTINCT block-subset (intersection with the
      true subset <= D-1 for any other frame). frame_class=1.000 is exact-by-construction and
      CORRELATION-INDEPENDENT (PROBE 2: frame_class=1.000 even with RANDOM uncorrelated fillers).
      This is the builder's own honest note, confirmed: it is NOT a stress-tested recovery.
  (2) DECODE is at the ALREADY-PROVEN easy-regime ceiling: cond_decode/posctrl=1.000 at V1024D3 is
      exactly the cited known-frame ceiling (independently reproduced = 1.000). No decode stress at
      the anchor.
The perfect parse = frame_class(by-construction 1.0) * cond_decode(proven ceiling 1.0) is therefore
a MECHANISM DEMONSTRATION, not new evidence that a HARD comprehension task was solved.

SCOPE LIMITATION (the real comprehension frontier is untouched):
  - PROBE 4: two frames with the SAME block-set but DIFFERENT role->block ORDER produce IDENTICAL
    occupancy. The classifier recovers WHICH-BLOCKS (the set), NOT which-role-to-which-block (the
    binding/order). Here role order is FIXED by a sort convention (role d -> d-th smallest block),
    so order-recovery is never tested. Corroborated by the substrate itself: overlap-check top hit
    (cosine 0.3076) is the position-is-meaning VSA note -- "additive bundling gives a SET
    representation ... loses role-filler structure: A+B+C == C+B+A." The sparse compose IS additive
    block-superposition-sum; occupancy is set-only.
  - PROBE 3: frame_class stays 1.000 at F=8/16/32/56 (all distinct block-subsets, up to C(8,3)=56).
    The builder's proposed Arm 4 (frame_class vs F-count) will NOT locate a frame-classification
    bottleneck -- occupancy uniquely IDs any distinct subset; the axis is mis-targeted.
  - Decode cliff CITED+VERIFIED: known-frame block-local decode drops to exact_ordered=0.856 at
    V8192D26 (blocklocal cell, 3-seed mean) -> parse is bounded ~0.856 at the hard decode regime
    even with free frame recovery.

ENVELOPE / NEXT TEST (where comprehension actually becomes non-trivial):
  frame recovery UNDER STRESS -- specifically (a) ORDER/PERMUTATION recovery (same block-set,
  different role->block map; occupancy is degenerate -> needs a mechanism beyond occupancy), and/or
  (b) SUPERPOSITION within blocks (multiple fillers per block, D >= B_TOTAL, or fewer blocks -> per-
  block energy varies, cross-code correlation stresses BOTH classify and decode), and/or (c) decode-
  at-scale (V8192/D26). The occupancy classifier PROVABLY cannot do (a); that is the real gap.

NET CERT DELTA (this batch): MM +1, CG 0, HF 0. No DEMOTE.
COMPOSES WITH (does NOT supersede): the blocklocal generation CG atom (ec7aa9064) -- this reuses that
decoder as the known-frame half and cites its ceiling/cliff.
"""
import json
import os
import time
import tempfile

MATH_ATOMS = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))
SESSION_TAG = "2026-07-05_comprehension_frame_classify_then_known_decode_MEASURED_MECHANISM"

PRIOR_GEN_CG_ID = "math::CHAIN_GRADE_generation_decoder_native_GSBC_block_local_sparse_resonator_round_trips_REAL_native_GSBC_EXPAND2X_fillers_PERFECTLY_exact_ordered_1p000_cv0_across_full_envelope_V256_to_8192_at_D3_D6_and_V1024_at_D12_and_0p9889_at_V1024D26_3seed_ENCODING_MISMATCH_PROVEN_dense_bipolar_BSC_full_resonator_0p000_on_SAME_GSBC_fillers_vs_1p000_on_iid_synth_NON_VACUOUS_noorder_ctrl_0p000_and_dense_gsbc_fullreso_0p000_collapse_dense_synth_1p000_ceiling_PLUS_MEASURED_capacity_boundary_at_V8192D26_exact_0p856_3seed_mean_reconciled_with_sparse_Hebbian_law_Vmax_0p7n_over_a_ln_inv_a_cliff_at_V_over_Vmax_2p9x_holds_below_1x_block_local_is_brain_grounded_Sparse_Block_Codes_not_a_partition_cheat_positions_known_by_construction_for_generation_decode_3seed_FULL_N8192_K192_2026-07-05"

atom = {
    "id": "math::MEASURED_MECHANISM_comprehension_classify_then_decode_ARCHITECTURE_validated_end_to_end_and_sparse_block_geometry_makes_the_frame_BLOCK_SET_recoverable_as_a_ZERO_NOISE_occupancy_readout_where_the_DENSE_algebra_entangles_it_to_chance_dense_ctrl_frame_class_0p078_approx_1overF_vs_sparse_1p000_gap_0p922_PAIRED_non_vacuous_BUT_the_1p000_is_BY_CONSTRUCTION_deterministic_occupied_block_L2_energy_exactly_k20_empty_exactly_0_matched_filter_margin_exactly_k_min_eq_max_and_CORRELATION_INDEPENDENT_frame_class_1p000_even_on_RANDOM_uncorrelated_fillers_recovers_the_block_SET_NOT_role_ORDER_permuted_role_to_block_same_set_gives_IDENTICAL_occupancy_order_fixed_by_sort_convention_never_tested_frame_class_stays_1p000_to_F56_all_distinct_subsets_so_F_count_Arm4_wont_bottleneck_and_decode_is_at_proven_easy_regime_ceiling_cond_decode_1p000_at_V1024D3_cliff_CITED_0p856_at_V8192D26_comprehension_FRONTIER_OPENED_not_closed_next_test_is_ORDER_PERMUTATION_recovery_and_superposition_and_decode_at_scale_3seed_FULL_N8192_F16_2026-07-05",
    "name": "MATH MEASURED_MECHANISM (capability OPENING, honestly scoped): frame-classify-then-known-decode is a VALIDATED end-to-end classify-then-decode comprehension pipeline, and sparse-block DISJOINT geometry PROVABLY makes the frame's block-SET recoverable as a zero-noise occupancy readout where the DENSE algebra entangles it to chance (paired dense_ctrl frame_class=0.078~1/F vs sparse 1.000, gap 0.922, non-vacuous). BUT the headline 1.000 is BY-CONSTRUCTION: occupied-block L2 energy is exactly k=20, empty exactly 0, matched-filter margin exactly k (min==max), and frame_class=1.000 even on RANDOM uncorrelated fillers -> a deterministic set-identity readout, correlation-INDEPENDENT, not a stressed recovery. It recovers the block-SET, NOT role-ORDER (permuted role->block on the same set gives identical occupancy; order is fixed by a sort convention, never tested); frame_class stays 1.000 to F=56 (all distinct subsets) so the F-count Arm-4 will not bottleneck; and decode is at the proven easy-regime ceiling (cond_decode=1.000 at V1024D3; cited cliff 0.856 at V8192D26). Comprehension FRONTIER OPENED, not closed.",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": "proven_bound_measured_mechanism_capability_opening_honestly_scoped_easy_regime",
    "cert_class": "classify_then_decode_comprehension_architecture_validated_sparse_block_exposes_frame_SET_occupancy_dense_entangles_to_chance_PROVEN_but_frame_recovery_by_construction_deterministic_correlation_independent_recovers_set_not_order_decode_at_proven_easy_ceiling",
    "description": (
        "LANDED-VET of exp_frame_classify_then_known_decode_v1 (verdict HARD_PASS, run_mode=full, "
        "N=8192, B_TOTAL=8, bs=1024, D_ROLES=3, V=1024, F=16, trials=30, 3 seeds [7,13,19], 9 units, "
        "cardinality_ok=True, arms_differ_verified=True; cell commit d80c79de1). "
        "AUDITOR INDEPENDENT RECOMPUTE (.venv): re-ran the cell to an isolated output dir -- reproduced "
        "EXACTLY (sparse_block frame_class=1.000/parse=1.000/cond_decode=1.000 all seeds; dense_ctrl "
        "frame_class=0.078 [per-seed 0.100/0.033/0.100]; known_frame_posctrl decode=1.000; BIAS audit "
        "byte-identical: 16 distinct templates, min_pairwise_hamming=2, entropy=7.1696 bits, non_degenerate). "
        "Then FIVE mechanism/envelope probes the cell does NOT report (see below). "
        "\n"
        "WHAT IS REAL AND PROVEN (the load-bearing finding): (a) the classify-then-decode ARCHITECTURE "
        "composes end-to-end -- a cheap non-learned occupancy recognizer feeds the already-proven block-local "
        "decoder; the predicted frame is a glass-box inspectable intermediate. (b) sparse-block DISJOINT "
        "geometry makes the frame's block-SET recoverable from occupancy where the DENSE multiply-bind algebra "
        "ENTANGLES it: the PAIRED dense_ctrl (SAME fillers, dense binding) collapses to frame_class=0.078 ~ "
        "chance 1/F=0.0625 (gap=0.922). This is a genuine, non-vacuous, paired negative control -- occupancy-"
        "carries-frame is NOT automatic; it is a property of the sparse-block encoding. The discriminator FIRES. "
        "\n"
        "WHY IT IS MEASURED_MECHANISM NOT CHAIN_GRADE (the honest deflation, symmetric): the headline 1.000 is "
        "a COMPOSITION of two factors, NEITHER stress-tested at the anchor. "
        "PROBE 1 (occupancy margin): occupied-block L2 energy = EXACTLY k=20 on every trial, empty-block energy "
        "= EXACTLY 0; the matched-filter score margin (true - best_other) = EXACTLY k=20 (min==max across all "
        "trials). Because each used block holds exactly ONE k-sparse filler (block-superposition-sum, no cross-"
        "block interference) per-block energy = k independent of filler content, and every candidate frame is a "
        "DISTINCT block-subset (|other frame ∩ true| <= D-1 => other score <= (D-1)k < Dk). So frame recovery is "
        "a DETERMINISTIC set-identity readout with a fixed margin -- exact-by-construction, no noise floor. "
        "PROBE 2 (content-independence): frame_class=1.000 even with RANDOM uncorrelated fillers -> filler "
        "correlation plays ZERO role in the classify step; the verdict_msg's 'survives real filler correlation' "
        "is technically true but MISLEADING (nothing to survive -- disjoint injection makes energy=k regardless). "
        "DECODE factor: cond_decode/posctrl=1.000 at V1024D3 is EXACTLY the cited known-frame ceiling "
        "(independently reproduced=1.000). No decode stress at the anchor either. So parse=1.000 is a mechanism "
        "demonstration, not evidence a HARD comprehension task was cracked. "
        "\n"
        "SCOPE LIMITATIONS (the actual comprehension frontier is untouched): "
        "PROBE 4 (permutation blind-spot): two frames with the SAME block-set but DIFFERENT role->block ORDER "
        "produce IDENTICAL occupancy ([20,20,20,0,0,0,0,0] for both). The classifier recovers WHICH-BLOCKS (the "
        "set), NOT which-role-to-which-block (the binding). Here role order is FIXED by a sort convention "
        "(role d -> d-th smallest block), so there is one ordering per subset and order-recovery is NEVER "
        "tested. The substrate corroborates: overlap-check top hit (cosine 0.3076) is the position-is-meaning "
        "VSA note -- 'additive bundling gives a SET representation ... loses role-filler structure: A+B+C == "
        "C+B+A.' The sparse compose IS additive block-superposition-sum; occupancy is set-only. "
        "PROBE 3 (F-scaling): frame_class stays 1.000 at F=8/16/32/56 (all distinct block-subsets up to "
        "C(8,3)=56). The builder's proposed Arm 4 (frame_class vs F-count 8/16/32/64) will NOT locate a frame-"
        "classification bottleneck -- occupancy uniquely IDs any distinct subset; the axis is mis-targeted. "
        "PROBE 5 (decode cliff, CITED+VERIFIED off blocklocal metrics): known-frame block-local decode drops to "
        "exact_ordered=0.856 at V8192D26 (3-seed mean, verified) -> parse is bounded ~0.856 at the hard decode "
        "regime even with free frame recovery. "
        "\n"
        "TIER RATIONALE: MEASURED_MECHANISM (+1) -- the mechanism (sparse-block exposes frame-SET occupancy; "
        "dense entangles) and the architecture-composition are REAL and PROVEN non-vacuously, so this is NOT a "
        "HARD_FAIL and NOT dismissed. But the perfect 1.000 is by-construction at the easy regime for BOTH "
        "factors and recovers set-not-order, so 'COMPREHENSION OPENS' as a chain-grade solved-hard-task "
        "OVERSTATES it. This is a capability OPENING / proven mechanism boundary, honestly scoped to the easy "
        "regime, with the scaling+order-recovery test as the real frontier. Single regime point, no envelope "
        "swept, scaling Arm-4 explicitly deferred -> arc-OPENING not arc-closure."
    ),
    "aliases": ["comprehension_classify_then_decode_architecture_validated_frame_set_occupancy_by_construction_MM",
                "frame_recovery_is_deterministic_set_readout_not_order_recovery_easy_regime_opening"],
    "metadata": {
        "record_class": "experiment_landed_vet_measured_mechanism_capability_opening_honestly_scoped",
        "term_class": "COMPREHENSION_CLASSIFY_THEN_DECODE_ARCHITECTURE_VALIDATED_SPARSE_BLOCK_FRAME_SET_OCCUPANCY_BY_CONSTRUCTION_RECOVERS_SET_NOT_ORDER_EASY_REGIME",
        "cert_status": "proven_bound_measured_mechanism_capability_opening_honestly_scoped_easy_regime",
        "cert_class": "classify_then_decode_comprehension_architecture_validated_sparse_block_exposes_frame_SET_occupancy_dense_entangles_to_chance_PROVEN_but_frame_recovery_by_construction_deterministic_correlation_independent_recovers_set_not_order_decode_at_proven_easy_ceiling",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "verified_via": "independent .venv recompute: re-ran cell to isolated dir (reproduced exactly) + 5 mechanism/envelope probes (occupancy margin, content-independence, F-scaling, permutation blind-spot, decode-ceiling); not verdict_msg",
        "atomized_by": "skunkworks_landed_VET_2026-07-05_comprehension_frame_classify_MM",
        "anchor": "frame_classify_then_known_decode_v1",
        "cell_commit": "d80c79de1",
        "raw_metrics_path": "data/exp_frame_classify_then_known_decode_v1/metrics.json",
        "research_note": "notes/research_frontier_drill_comprehension_parse_unknown_structure_2026-07-05.md",
        "run_mode": "full", "N": 8192, "B_TOTAL": 8, "bs": 1024, "D_ROLES": 3, "V": 1024, "F": 16,
        "n_seeds": 3, "seeds": [7, 13, 19], "n_units": 9, "cardinality_ok": True,
        "recompute_off_disk": {
            "reproduce_cell": {"sparse_frame_class": 1.000, "sparse_parse": 1.000, "sparse_cond_decode": 1.000,
                               "dense_ctrl_frame_class_mean": 0.0778, "dense_ctrl_per_seed": [0.100, 0.0333, 0.100],
                               "dense_chance_1overF": 0.0625, "gap": 0.922, "known_frame_posctrl_decode": 1.000,
                               "parse_cv": 0.000, "match_disk": "EXACT"},
            "bias_audit": {"n_distinct_templates": 16, "min_pairwise_hamming": 2, "entropy_bits": 7.1696,
                           "non_degenerate": True, "match_disk": "EXACT"},
            "PROBE1_occupancy_margin": {"per_code_k_active": 20, "occupied_block_energy_min_max": [20.0, 20.0],
                                        "empty_block_energy_min_max": [0.0, 0.0],
                                        "matched_filter_score_margin_true_minus_best_other_min_max": [20.0, 20.0],
                                        "verdict": "frame recovery is a DETERMINISTIC set-identity readout, exact-by-construction, no noise floor"},
            "PROBE2_content_independence": {"frame_class_random_uncorrelated_fillers": 1.000,
                                            "verdict": "correlation-INDEPENDENT; disjoint injection makes per-block energy=k regardless of filler"},
            "PROBE3_F_scaling_distinct_subsets": {"F8": 1.000, "F16": 1.000, "F32": 1.000, "F56": 1.000,
                                                  "C_8_3_max_distinct_subsets": 56,
                                                  "verdict": "builder Arm-4 (frame_class vs F-count) will NOT bottleneck; occupancy IDs any distinct subset"},
            "PROBE4_permutation_blind_spot": {"occupancy_frameA_012": [20, 20, 20, 0, 0, 0, 0, 0],
                                              "occupancy_frameB_201_same_set": [20, 20, 20, 0, 0, 0, 0, 0],
                                              "identical": True,
                                              "verdict": "recovers block-SET not role-ORDER; order fixed by sort convention, never tested"},
            "PROBE5_decode_ceiling_and_cliff": {"known_frame_decode_V1024D3_reproduced": 1.000,
                                                "cited_cliff_V8192D26_exact_ordered_3seed_mean": 0.8556,
                                                "verdict": "decode at proven easy ceiling at anchor; parse bounded ~0.856 at hard decode regime"},
        },
        "non_vacuity_checks": {
            "paired_dense_negative_control_fires": "dense_ctrl frame_class=0.078 ~ chance 1/F=0.0625 vs sparse 1.000, gap 0.922 -> occupancy-carries-frame is a property of sparse-block geometry, PROVEN load-bearing",
            "bias_audit_non_degenerate": "16 distinct templates, min_pairwise_hamming=2, entropy 7.17 bits, no block used by all frames -> classifier basis is valid (not a degenerate single-signal false-positive)",
            "positive_control_clears_floor": "known_frame_posctrl decode=1.000 >= 0.90 floor -> block-local decode reproduces the cited ceiling at the test regime",
            "BUT_headline_metric_is_by_construction": "frame_class=1.000 has margin exactly k, correlation-independent (PROBE 1/2) -> the 1.000 itself is NOT a stressed recovery; the ARCHITECTURE + the sparse-vs-dense CONTRAST are the real content, not the perfect score",
        },
        "by_construction_verdict": "PARTIALLY BY-CONSTRUCTION. The MECHANISM (sparse-block exposes frame-SET occupancy; dense entangles to chance) is genuine and paired-non-vacuous. But the headline frame_class=1.000 is exact-by-construction (deterministic set-identity readout, margin=k, correlation-independent) and the decode 1.000 is the proven easy-regime ceiling -> the perfect parse is a mechanism demonstration, not a solved hard task. Recovers set-not-order (permutation blind-spot).",
        "cross_arc_overlap_check_2026_07_01_USER_locked": "substrate_query 'frame classification occupancy recovery role filler binding comprehension parse' -> top hit cosine=0.3076 = notes/research_drill_substrate_VSA_position_is_meaning_4x_2026-06-12.md::chunk006 (additive-vs-multiplicative composition; 'additive bundling gives a SET representation ... loses role-filler structure A+B+C==C+B+A'). This CORROBORATES the Probe-4 set-not-order finding rather than being a rediscovery. Remaining hits <0.30 (general VSA algebra/reasoning notes). The specific classify-then-decode block-occupancy comprehension mechanism is NOVEL; not a rediscovery.",
        "composes_with_atoms": [PRIOR_GEN_CG_ID],
        "composition_note": "COMPOSES WITH (does NOT supersede) the blocklocal generation CG atom (ec7aa9064): this cell reuses that block-local decoder as the known-frame 'generation/synthesis' half of the Helmholtz recognition+generation split, and cites its known-frame ceiling (V1024D3=1.000) and cliff (V8192D26=0.856). It also composes with the position-is-meaning VSA note (set-representation loses role-filler order), which the permutation-blind-spot probe empirically confirms for the block-superposition compose.",
        "framing_corrections_vs_director_and_cell": "AFFIRM: the architecture composes, the mechanism (sparse-block exposes frame-SET occupancy where dense entangles) is real and proven non-vacuously (dense_ctrl at chance, gap 0.922), BIAS audit is legit, positive control clears its floor. CORRECT (downward, symmetric): (1) 'COMPREHENSION OPENS' at a perfect 1.000 OVERSTATES -- frame recovery is exact-BY-CONSTRUCTION (margin=k, correlation-independent per Probes 1-2), and decode is the already-proven easy-regime ceiling, so the 1.000 is a composition of two non-stressed factors, not a cracked hard task. Tier = MEASURED_MECHANISM (capability OPENING), not chain-grade solved capability. (2) The verdict_msg 'survives real filler correlation via the occupancy signature' is technically true but misleading: disjoint injection makes per-block energy=k regardless of filler, so there is nothing for correlation to stress in the classify step (frame_class=1.000 even on RANDOM fillers). (3) It recovers the block-SET, NOT the role->block ORDER (permutation blind-spot, Probe 4) -- 'parse an UNKNOWN structure into role-filler' is scoped to which-blocks-occupied, weaker than full binding recovery. (4) The builder's proposed Arm-4 (frame_class vs F-count) is MIS-TARGETED: frame_class stays 1.000 to F=56 (Probe 3); it will not find a frame-classification bottleneck. No inflation and no unfair dismissal: the mechanism + architecture are credited as a genuine opening.",
        "envelope_and_next_test": "The ENVELOPE break (where comprehension becomes non-trivial): frame recovery UNDER STRESS -- (a) ORDER/PERMUTATION recovery: frames sharing a block-set but differing in role->block map, where occupancy is DEGENERATE (Probe 4) and a mechanism beyond occupancy (correlation-sensitive / learned recognizer) is required; this is the REAL comprehension test the occupancy classifier PROVABLY cannot do. (b) SUPERPOSITION within blocks: multiple fillers per block / D >= B_TOTAL / fewer blocks -> per-block energy varies, cross-code correlation stresses BOTH classify and decode. (c) DECODE-at-scale: V8192/D26 where the cited known-frame ceiling is 0.856 -> parse bounded there. The builder's F-count Arm-4 is NOT the right stress axis (Probe 3). Recommended next test: order-permutation frame recovery at V1024D3 (isolates the classify stress from the decode cliff), then compose with the V8192D26 decode regime.",
        "expansion_criterion": "PROMOTES toward CHAIN_GRADE iff a follow-up cell demonstrates frame recovery UNDER GENUINE STRESS -- e.g. ORDER/permutation recovery (same block-set, different role->block map) at >= HP with a paired negative control that CAN fail, and/or superposition-within-blocks recovery -- i.e. the classify step recovers structure that is NOT a by-construction set-identity readout. Stays MM if only the easy-regime composition is re-confirmed at more V/D points without an order/superposition stress. DEMOTES toward HARD_FAIL only if a re-run fails to reproduce the dense-vs-sparse contrast (not expected; reproduced exactly).",
        "disposition": "MEASURED_MECHANISM_comprehension_classify_then_decode_ARCHITECTURE_validated_and_sparse_block_frame_SET_occupancy_recovery_PROVEN_via_paired_dense_collapse_BUT_the_1p000_is_by_construction_deterministic_correlation_independent_recovers_set_not_order_decode_at_easy_ceiling_capability_OPENING_honestly_scoped_next_test_is_ORDER_permutation_and_superposition_and_decode_at_scale",
        "cert_increment_delta": 1,
    },
}


def a5_append(path, atom):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_atoms_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    n_lines = 0
    found = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_lines += 1
            obj = json.loads(line)  # integrity: raises on corrupt line
            aid = obj.get("id") or obj.get("atom_id")
            if aid == atom["id"]:
                found += 1
    if found != 1:
        raise RuntimeError(f"verify-load failed: atom id found {found}x (expected 1) in {path}")
    return n_lines


def ledger_append(atom, ledger_path=CERT_LEDGER):
    md = atom["metadata"]
    entry = {
        "ts": TS,
        "ts_iso": TS_ISO,
        "atom_id": atom["id"],
        "corpus": atom["corpus"],
        "tier": atom["tier"],
        "cert_status": md.get("cert_status"),
        "cert_class": md.get("cert_class"),
        "cert_increment_delta": md.get("cert_increment_delta", 0),
        "verified_off_data": True,
        "anchor": md.get("anchor"),
        "cell_commit": md.get("cell_commit"),
        "auditor": "skunkworks",
        "atomized_by": md.get("atomized_by"),
        "landed_VET_session": SESSION_TAG,
        "note": "capability OPENING honestly scoped: architecture + sparse-vs-dense mechanism REAL/proven; headline 1.000 is by-construction (margin=k, correlation-independent) + recovers set-not-order + decode at easy ceiling; next test = order-permutation + superposition + decode-at-scale",
    }
    d = os.path.dirname(ledger_path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_ledger_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(ledger_path):
                with open(ledger_path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ledger_path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


if __name__ == "__main__":
    print(f"[atomize] ts_iso={TS_ISO}")
    n = a5_append(MATH_ATOMS, atom)
    print(f"[atomize] math MEASURED_MECHANISM comprehension-frame-classify appended; math lines={n}")
    ledger_append(atom)
    print("[atomize] DONE 1 atom + 1 ledger entry; A5-gated (tmp+os.replace+verify-load+json-integrity); matching TS_ISO")
    print("[atomize] NET CERT DELTA: MM +1 (comprehension capability opening, honestly scoped), CG 0, HF 0")
