"""A5-gated atomize: LANDED-VET of reasoning_readout_length_generalization_clutrr_cg_v1.
CONSTRUCTION-FAVORED / TUNED-SYNTHETIC (HARD_FAIL as a chain-grade). LOCAL-ONLY.
Atomic tmp+os.replace, verify-load, integrity-check. needs_orchestrator_store_sync=True.
NO push, NO remote-persist, NO git add -A.
"""
import json, os, time
from datetime import datetime, timezone

ROOT = r"d:/AI/hd-instrument/data/substrate_index"
MATH = os.path.join(ROOT, "math", "atoms.jsonl")
LEDGER = os.path.join(ROOT, "meta", "cert_ledger.jsonl")

ts = time.time()
ts_iso = datetime.now(timezone.utc).isoformat()

PARENT = ("math::LANDED_VET_role_filler_factorization_learning_curve_cg_v1_MIDDLE_BAND_"
          "MEASURED_MECHANISM (atom-29363 factorization: compositional generalization is "
          "FREE / construction-determined; CG needs REAL non-matched-decoder data)")

decisive = {
    "reproduced_headline_byte_level": {
        "ARM_A_k2_to_k10": [0.841, 0.701, 0.626, 0.543, 0.495, 0.448, 0.414, 0.385, 0.341],
        "ARM_B_k2_to_k10": [0.191, 0.113, 0.102, 0.069, 0.093, 0.072, 0.079, 0.071, 0.063],
        "oracle_k2_to_k10": [0.858, 0.743, 0.676, 0.623, 0.566, 0.515, 0.482, 0.471, 0.434],
        "long_gap_clean": 0.341, "long_gap_scram": -0.000, "chance": 0.0556,
        "seeds": [7, 13, 19], "matches_metrics_json": True},
    "DECISIVE_probe_B_deterministic_composition_ambiguity_0": {
        "note": "ambiguity_rate=0.0 == real symbolic kinship (deterministic rule-based composition)",
        "oracle_all_lengths": 1.000, "ARM_A_len10": 0.982, "ARM_B_len10": 0.086,
        "long_gap_clean": 0.904,
        "cell_OWN_verdict": "GUARD_FAIL_CONSTRUCTION_DETERMINED",
        "G1_oracle_lt_0p90": False, "baseline_in_band": False},
    "DECISIVE_probe_C_knob_sweep_oracle_len10_vs_ambiguity_rate": {
        "0.00": 1.000, "0.10": 0.772, "0.20": 0.618, "0.35": 0.465, "0.50": 0.448, "0.70": 0.323,
        "note": "oracle_len10 (the G1 guard) is a direct monotone function of the injected knob; "
                "0.35 chosen to land oracle in the (2*chance, 0.90) target band = tuned-to-pass"},
    "P1_arm_a_reproduces_oracle_at_len2": {"arm_a": 0.841, "oracle": 0.858, "genuine_but_trivial_lookup": True},
    "capacity": "N=1024 > m^2=324 (heteroassoc memory stores the pairwise table; folding is free)",
}

plain = (
    "An experiment claimed a big win: a native-VSA reasoner that folds a chain hop-by-hop "
    "beats a flat baseline that cannot chain, and keeps working as chains get longer (a "
    "'length-generalization' chain-grade). The auditor reproduced every headline number exactly, "
    "then ran the decisive test the whole reorientation demanded: what happens on REAL kinship data? "
    "Real CLUTRR kinship composition is DETERMINISTIC (mother's mother = grandmother, by a fixed rule "
    "table); its real difficulty lives in the TEXT (who-is-who), which this substrate does not read. "
    "The auditor set the generator's one difficulty knob to zero (= deterministic real-kinship-like "
    "composition) and the perfect-oracle immediately solves length-10 for free (100 percent) -- which "
    "trips the cell's OWN guard and prints GUARD_FAIL_CONSTRUCTION_DETERMINED. Sweeping the knob shows "
    "the sub-100-percent ceiling that supposedly made the task 'honest and hard' is entirely a dial: "
    "0.00->100pct, 0.35->46pct, 0.70->32pct. So the ceiling was manufactured, not discovered, and it has "
    "no analog in real CLUTRR's symbolic form. Worse, the folder-beats-flat gap is even BIGGER with the "
    "knob off (0.90) -- proving the win is just 'a folding machine beats a machine that provably can't "
    "fold, on a folding task.' That is a near-tautology, exactly the atom-29363 trap the reorientation "
    "was meant to escape: multi-hop over clean structure is FREE. The genuinely learned part here is only "
    "a lookup table of pairwise rules (real but trivial). The scramble control and 3-seed reproduction "
    "are clean and the cell is honestly engineered -- the failure is in the SCIENCE TARGET, not integrity. "
    "Verdict: CONSTRUCTION-FAVORED / TUNED-SYNTHETIC, a clean negative -- NOT a chain-grade."
)

importance = (
    "This is the load-bearing guard on the whole post-29363 reorientation: the lesson was that a genuine "
    "chain-grade must live where capability is LEARNED and the ceiling is honestly < 1.000, and that "
    "synthetic tasks can be rigged. This candidate rigged exactly that ceiling with a single ambiguity "
    "knob and then cited an oracle<0.90 guard that the knob itself controls -- a circular defense. Catching "
    "it prevents a false CG from entering CERT N and re-establishes the real bar: the sub-1.0 ceiling must "
    "be INTRINSIC to the symbolic task (not an injected sampling knob) AND the win must be non-tautological "
    "(not folder-vs-provably-cannot-fold). Routes the genuine target to REAL incomplete KGs (FB15k-237 / "
    "MetaQA multi-hop) where no oracle path-follower wins, per the drill's own Scan 3."
)

atom = {
    "id": ("math::LANDED_VET_reasoning_readout_length_generalization_clutrr_cg_v1_"
           "CONSTRUCTION_FAVORED_TUNED_SYNTHETIC_HARD_FAIL_sub1p0_ceiling_MANUFACTURED_by_injected_"
           "ambiguity_rate_knob_no_real_CLUTRR_symbolic_analog_deterministic_composition_ambiguity0_"
           "gives_oracle_1p000_at_len10_trips_cells_OWN_G1_guard_GUARD_FAIL_CONSTRUCTION_DETERMINED_"
           "knob_sweep_oracle_len10_0p00to1p000_0p10to0p772_0p20to0p618_0p35to0p465_0p70to0p323_"
           "guard_is_direct_monotone_of_knob_0p35_tuned_into_target_band_ARMA_vs_ARMB_gap_0p341_"
           "near_tautological_folder_beats_provably_cannot_fold_on_first_order_fold_task_gap_GROWS_"
           "to_0p904_when_knob_off_atom29363_multihop_over_good_structure_is_FREE_trap_in_new_dress_"
           "length_gen_is_the_FREE_part_geometry_does_NOT_break_ARMA_tracks_oracle_within_0p09_cleanup_"
           "keeps_single_relation_state_on_manifold_rides_decaying_stochastic_ceiling_learned_part_is_"
           "only_m2_pairwise_lookup_P1_0p841_vs_oracle_0p858_capacity_N1024_gt_m2_324_scramble_C1_"
           "neg0p000_clean_but_proves_foldability_required_not_nonconstruction_3seed_reproduced_one_"
           "variable_no_leakage_cell_integrity_CLEAN_failure_is_science_target_not_integrity_"
           "expdev_admission_tuned_so_guard_provably_passes_is_self_refuting_2026-07-19"),
    "name": ("LANDED-VET reasoning_readout_length_generalization_clutrr_cg_v1: CONSTRUCTION-FAVORED / "
             "TUNED-SYNTHETIC (HARD_FAIL as chain-grade). Sub-1.0 ceiling is a manufactured ambiguity "
             "knob with no real-CLUTRR symbolic analog; deterministic composition (=real kinship) trips "
             "the cell's own oracle<0.90 guard; ARM_A-vs-ARM_B gap is the near-tautological "
             "folder-beats-cannot-fold atom-29363 free-multihop trap."),
    "corpus": "math",
    "tier": "HARD_FAIL",
    "kind": "landed_vet",
    "cert_status": ("construction_favored_tuned_synthetic_honest_negative_chain_grade_attempt_did_NOT_"
                    "escape_atom29363_sub1p0_ceiling_MANUFACTURED_by_injected_ambiguity_knob_guard_"
                    "circular_win_near_tautological_folder_vs_cannot_fold_length_gen_is_the_free_part"),
    "cert_class": "HARD_FAIL",
    "description": (
        "Independent off-disk VET (.venv, byte-level reproduction + adversarial knob probes) of the "
        "NIGHT-3 reoriented CLUTRR length-generalization chain-grade candidate. HEADLINE REPRODUCES "
        "EXACTLY (ARM_A 0.841->0.341 over k=2..10; ARM_B ~chance 0.191->0.063; oracle 0.858->0.434; "
        "long_gap_clean=0.341; long_gap_scram=-0.000; 3 seeds 7/13/19). VERDICT = CONSTRUCTION-FAVORED / "
        "TUNED-SYNTHETIC, NOT a chain-grade, on three decisive grounds. (1) THE SUB-1.0 CEILING IS "
        "MANUFACTURED: it is entirely produced by the generator's injected ambiguity_rate=0.35 stochastic "
        "mixture, which has NO analog in real CLUTRR's SYMBOLIC form. Real CLUTRR kinship composition is "
        "DETERMINISTIC (rule-based); its <1.0 difficulty lives in TEXT/coref, which the substrate does not "
        "read. The auditor ran the real-CLUTRR-equivalent (ambiguity_rate=0.0 == deterministic monoid "
        "composition): oracle=1.000 at ALL lengths, and the cell's OWN guard fires "
        "GUARD_FAIL_CONSTRUCTION_DETERMINED (G1 oracle_len10<0.90 = False, baseline_in_band=False). Knob "
        "sweep: oracle_len10 = {0.00:1.000, 0.10:0.772, 0.20:0.618, 0.35:0.465, 0.50:0.448, 0.70:0.323} -- "
        "the G1 guard is a DIRECT MONOTONE FUNCTION of the injected knob, and 0.35 was chosen to land the "
        "oracle inside the (2*chance, 0.90) target band = tuned-to-pass. (2) THE ARM_A-vs-ARM_B GAP IS "
        "NEAR-TAUTOLOGICAL AND INDEPENDENT OF THE AMBIGUITY: with the knob OFF the gap GROWS to 0.904. The "
        "generator is a first-order Markov left-fold over single-relation states; ARM_A is exactly that "
        "folder with per-hop cleanup snapping back to a clean single relation. 'A folder beats a "
        "provably-cannot-fold flat readout on a fold task' is the atom-29363 'multi-hop over good structure "
        "is FREE' trap in a new dress. (3) LENGTH-GENERALIZATION IS THE FREE PART, NOT THE LEARNED PART "
        "(contradicting the reorientation's own thesis that length-gen is where the free geometry BREAKS). "
        "Here the geometry does NOT break: ARM_A tracks the oracle within ~0.09 at every length because "
        "cleanup keeps the intermediate state a clean single relation on-manifold indefinitely; ARM_A merely "
        "RIDES the task's decaying STOCHASTIC ceiling (the oracle itself falls 0.858->0.434 purely from "
        "per-hop sampling). The only genuinely LEARNED thing is a heteroassociative lookup of the m^2 "
        "pairwise table (P1: ARM_A 0.841 vs oracle 0.858 at len-2; capacity N=1024>m^2=324) -- real but "
        "trivial. GENUINENESS SIGNALS WEIGHED: the scramble control (long_gap_scram=-0.000) is CLEAN and "
        "reproduces, but it only proves foldability-is-required (anti-memorization/leakage), NOT "
        "non-construction -- and real kinship IS foldable, so it does not rescue genuineness. 3-seed "
        "reproduction, one-variable (only the reasoner differs; identical codes/position-family/data), and "
        "no label leakage into the held-out long chains are all CLEAN. ARM_B is a FAIR flat baseline in "
        "isolation (no flat linear readout can compute an arbitrary-length fold; honest floor is chance) and "
        "the len-2-only-for-A vs 2-4-for-B asymmetry is genuinely conservative-for-A -- but the comparison "
        "is UNINFORMATIVE because tautological. The cell is well-engineered and integrity-honest; the "
        "failure is in the SCIENCE TARGET (a manufactured ceiling + a self-controlled guard), NOT in "
        "integrity. exp_dev's own justification -- 'real CLUTRR's usable symbolic form is identical to what "
        "I generate' and 'I tuned the ambiguity so the guard provably passes' -- is SELF-REFUTING: the real "
        "symbolic form is deterministic (oracle=1.0), the injected 35pct ambiguity is the ONLY thing making "
        "the guard pass, and 'tuned so the guard provably passes' is precisely the prohibited tune-to-pass."),
    "aliases": [
        "reasoning_readout_length_generalization_clutrr_cg_v1",
        "clutrr_length_generalization_cg_v1",
        "clutrr_length_gen_construction_favored",
        "length_gen_ceiling_is_a_knob",
        "folder_beats_cannot_fold_tautology",
    ],
    "ts_iso": ts_iso,
    "ts": ts,
    "metadata": {
        "anchor": "reasoning_readout_length_generalization_clutrr_cg_v1",
        "verified_off_data": True,
        "verify_method": ("independent .venv recompute: imported the cell's own make_world/run_seed/"
                          "aggregate and (a) byte-reproduced the 3-seed headline metrics.json, "
                          "(b) ran ambiguity_rate=0.0 deterministic-composition = real-symbolic-kinship "
                          "equivalent -> oracle=1.000 trips cell's own GUARD_FAIL, (c) swept ambiguity_rate "
                          "to show oracle_len10 (G1) is a direct monotone function of the injected knob"),
        "decisive_numbers": decisive,
        "plain_language": plain,
        "importance": importance,
        "cert_delta": "0 chain-grade (HARD_FAIL / CONSTRUCTION-FAVORED; NOT counted toward CERT N)",
        "builds_on": [PARENT],
        "real_clutrr_test": ("Acquisition was feasible (git ls-remote facebookresearch/clutrr succeeded), "
                             "but UNNECESSARY: the ambiguity_rate=0.0 run IS the faithful symbolic-CLUTRR "
                             "equivalent (real kinship composition is a deterministic monoid), and it yields "
                             "oracle=1.000 at length 10 -> the cell's own construction-determined guard fails. "
                             "Honest caveat: real symbolic kinship may carry a SMALL residual ambiguity "
                             "(ungendered 'sibling' etc.), but nothing near the 0.43 the 0.35 knob manufactures, "
                             "and CLUTRR's documented length-difficulty (0.9->0.3) is a TEXT/model phenomenon, "
                             "not a symbolic-oracle one."),
        "framing_correction_vs_director": (
            "Director framed the decision as 'if the length-generalization gap HOLDS on real CLUTRR -> "
            "genuine.' CORRECTION: the gap holding is NECESSARY BUT NOT SUFFICIENT. On real (deterministic) "
            "CLUTRR the gap holds AND grows (0.904) -- yet the oracle solves length-10 for free (=1.000), "
            "tripping the guard and REVEALING construction-determination. 'Folder beats provably-cannot-fold' "
            "holds on ANY fold task, synthetic or real. The decisive test is not 'does the gap hold' but "
            "'is the sub-1.0 ceiling intrinsic to the symbolic task (not a knob) AND is the win "
            "non-tautological' -- both FAIL. So running real CLUTRR would have reproduced the gap and still "
            "been construction-favored."),
        "framing_correction_vs_exp_dev": (
            "exp_dev justified synthetic-over-real with 'real CLUTRR's usable symbolic form is identical to "
            "what I generate' and 'synthetic lets us TUNE the ambiguity so the construction-determined GUARD "
            "provably passes.' Both are SELF-REFUTING. (i) The symbolic forms are NOT identical: real kinship "
            "composition is DETERMINISTIC (oracle=1.0), the generator injects 35pct stochastic ambiguity. "
            "(ii) That injection is the ONLY thing pulling the oracle below 0.90; the guard the cell cites as "
            "its defense is a direct function of the knob it set -- a circular defense. 'Tuned so the guard "
            "provably passes' IS tune-to-pass. CREDIT preserved: the cell is honestly instrumented "
            "(reproduces byte-level, gates fire correctly, scramble+3-seed+one-variable all clean) -- the "
            "flaw is target design, not integrity."),
        "brain_check": (
            "The drill (SCAN 2/3) said multi-hop over GOOD structure is FREE (geometric) and the genuine "
            "LEARNED part is length-generalization WHERE THE FREE GEOMETRY BREAKS. This cell placed "
            "length-gen on a task where the geometry does NOT break: clean single-relation intermediate "
            "states + per-hop cleanup keep ARM_A on-manifold to any length, so length-gen stayed FREE. The "
            "brain-faithful lever (monotonic/ordered codes + commutative bind) is real but is NOT what wins "
            "here -- the deterministic (ambiguity=0) case wins by 0.904 identically. So the brain-check "
            "confirms this is the FREE regime, not the break regime a genuine chain-grade needs."),
        "revival_criterion": (
            "Promote toward CG only with a task whose sub-1.0 ceiling is INTRINSIC to the SYMBOLIC "
            "composition (not an injected sampling knob) AND where ARM_A's win is NOT the "
            "folder-vs-provably-cannot-fold tautology -- e.g. real INCOMPLETE KGs (FB15k-237, MetaQA "
            "multi-hop) where relations are NOT deterministic compositions and NO oracle path-follower wins "
            "(drill Scan 3: 'no algebraic freebie'), OR a task whose intermediate state is NOT a clean single "
            "relation so cleanup cannot trivially keep it on-manifold. Do NOT revive with an injected-"
            "ambiguity knob on a clean monoid, and do NOT cite an oracle<0.90 guard whose value the "
            "generator's own knob controls."),
        "fairness_guards": (
            "Symmetric anti-negativity: the headline reproduces EXACTLY and the cell's integrity is CLEAN "
            "(scramble control genuine, 3-seed, one-variable, no leakage, honest gates) -- credited. ARM_B is "
            "confirmed a FAIR flat baseline (structural chance floor, not a hobbled strawman) and the "
            "len-2-only-for-A asymmetry is genuinely conservative-for-A. The HARD_FAIL is NOT a claim the "
            "cell cheated; it is that the SCIENCE TARGET is construction-determined (manufactured ceiling + "
            "self-controlled guard + tautological gap). can-fail check: the guard COULD have failed honestly "
            "and DOES the moment the knob is set to the real-kinship value (0.0)."),
        "cross_arc_overlap_check": ("substrate_query (char-trigram) top hit cosine=0.292 ('Iteration' note); "
                                    "NONE at cosine>0.30. No prior chain-grade cert atom duplicated. Distinct "
                                    "adjudication; composes with the atom-29363 factorization "
                                    "construction-determined lesson (same lesson-class, cited)."),
        "needs_orchestrator_store_sync": True,
        "local_write_only": True,
    },
    "serves_capability": ["chain_grade_audit", "construction_determined_detection",
                          "reasoning_readout_length_generalization", "cert_integrity"],
}

ledger = {
    "op": "landed_vet_atomize",
    "corpus": "math",
    "tier": "HARD_FAIL",
    "cert_status": atom["cert_status"],
    "cert_class": "HARD_FAIL",
    "anchor": "reasoning_readout_length_generalization_clutrr_cg_v1",
    "live_reader": False,
    "atom_id": atom["id"],
    "cert_delta": "0 chain-grade (HARD_FAIL / CONSTRUCTION-FAVORED-TUNED-SYNTHETIC)",
    "cell_verdict": "HARD_PASS (cell self-report)",
    "auditor_tier": "HARD_FAIL / CONSTRUCTION-FAVORED-or-TUNED-NULL",
    "verdict": ("CONSTRUCTION-FAVORED / TUNED-SYNTHETIC. Headline reproduces byte-level, but the sub-1.0 "
                "ceiling is a manufactured ambiguity knob (no real-CLUTRR symbolic analog; deterministic "
                "composition -> oracle=1.000 at len10 -> cell's OWN guard fires GUARD_FAIL). The "
                "ARM_A-vs-ARM_B gap is near-tautological (folder beats provably-cannot-fold; grows to 0.904 "
                "with knob off) = the atom-29363 free-multihop trap. Length-gen is the FREE part, not the "
                "learned part. NOT a chain-grade."),
    "verified_off_data": True,
    "decisive_numbers": decisive,
    "framing_correction_vs_director": atom["metadata"]["framing_correction_vs_director"],
    "framing_correction_vs_exp_dev": atom["metadata"]["framing_correction_vs_exp_dev"],
    "brain_check": atom["metadata"]["brain_check"],
    "revival_criterion": atom["metadata"]["revival_criterion"],
    "fairness_guards": atom["metadata"]["fairness_guards"],
    "cross_arc_overlap_check": atom["metadata"]["cross_arc_overlap_check"],
    "net_cert_delta": {"CG": 0, "MM": 0, "HF": 1},
    "auditor": "hdi_skunkworks",
    "decision": "atomize_local_only_hard_fail_construction_favored_tuned_synthetic",
    "needs_orchestrator_store_sync": True,
    "local_write_only": True,
    "ts_iso": ts_iso,
    "ts": ts,
}


def a5_append(path, obj):
    """Atomic append: read-all + verify-load + append + tmp-write + os.replace + verify-load."""
    with open(path, "r", encoding="utf-8") as f:
        existing = f.readlines()
    # integrity pre-check: every existing line parses
    for i, ln in enumerate(existing):
        if ln.strip():
            json.loads(ln)
    line = json.dumps(obj, ensure_ascii=True)
    json.loads(line)  # verify the new record serializes+parses
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(existing if existing and existing[-1].endswith("\n") else
                     [l if l.endswith("\n") else l + "\n" for l in existing])
        f.write(line + "\n")
    os.replace(tmp, path)
    # verify-load post: full file reparses and last record == obj id
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for ln in lines:
        if ln.strip():
            json.loads(ln)
    last = json.loads(lines[-1])
    assert last.get("id", last.get("atom_id")) == obj.get("id", obj.get("atom_id")), "tail mismatch"
    return len(lines)


n_math = a5_append(MATH, atom)
n_ledger = a5_append(LEDGER, ledger)
print(f"OK atom appended -> math/atoms.jsonl now {n_math} lines")
print(f"OK ledger appended -> meta/cert_ledger.jsonl now {n_ledger} lines")
print(f"atom_id={atom['id'][:80]}...")
print(f"ts_iso={ts_iso}")
