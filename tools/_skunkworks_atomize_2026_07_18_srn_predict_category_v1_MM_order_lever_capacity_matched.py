"""
A5-gated atomization: srn_predict_category_v1 -> MEASURED_MECHANISM (order-sensitivity lever, capacity-matched)
(2026-07-18).

Director HELD pending this VET. Auditor tier = MEASURED_MECHANISM (DEFLATED from cell HARD_PASS).

VET independently off-disk (.venv, Fix #28: recompute off metrics.json per-seed records + fresh arm re-run,
NOT verdict_msg):
  - BYTE-REPRODUCE EXACT (fresh full re-run, seeds 7/13/19): ami_pos 0.1587/0.1624/0.1543, ami_bag
    0.0731/0.0983/0.1099, ami_static 0.0984/0.0974/0.0991; delta_pos +0.0602/+0.0650/+0.0551 (3/3 >= +0.02);
    delta_bag mean -0.005 (TIE). Matches metrics.json to 4dp.
  - CAPACITY CONFOUND RULED OUT: pos and bag have IDENTICAL trainable params (2*V*d = 230400 each); roles are
    a FIXED +/-1 sign-multiply (gr-seed 20260718, non-trainable, 0 free params). The order lever adds ZERO
    capacity -> the win IS attributable to order-sensitivity, not more parameters. This is the strong result.
  - FORKING-PATHS: single principled change (add Elman order-sensitivity after the bag ablation tied);
    tie-ablation RETAINED + reported (delta_bag ~ -0.005); reported config is NOT max-delta (lr=0.003 gives
    +0.165, epochs=8 gives +0.120 -- both LARGER than the reported +0.060) -> no cherry-pick toward reported
    config. NOT a garden-of-forking-paths artifact.
  - ROBUSTNESS: delta_pos stays positive across d(64:+0.055, 256:+0.056), lr(0.003:+0.165, 0.03:+0.053),
    epochs(8:+0.120, 32:+0.045), k(8:+0.089). BUT FLIPS NEGATIVE at k=3 (delta -0.015; static AMI jumps to
    0.167). The effect is WINDOW-CONTINGENT -- a real boundary, must be disclosed.
  - METRIC SWITCH NMI->AMI: LEGIT (chance-corrected; conservative). Effect holds on BOTH (NMI delta +0.059 ~
    AMI delta +0.060). Not metric-shopping.
  - ABSOLUTE STRUCTURE WEAK: ami_pos 0.158 (chance=0), purity 0.55 vs 0.499 one-cluster majority-class floor
    (+0.05 only). Example clusters show DET/NUM/PRON function words grouped but labeled 'NOUN' by 50% base
    rate; only 1 of 4 shown clusters is a clean NOUN cluster (city/house/school 0.822). 'Induces category
    structure' OVER-READS; defensible = a modest COMPARATIVE edge over best-in-class static counting.

TIER: MEASURED_MECHANISM (proven-bound), DEFLATED from cell HARD_PASS. The MECHANISM (order-sensitivity is the
lever, capacity-matched) is cleanly proven; the CLAIM is bounded to a modest, window-contingent, absolute-weak
comparative AMI edge on real Brown prose -- a construction-proof, NOT downstream reading capability.

Cross-arc overlap check (USER-locked): substrate_query.sh top hit cosine=0.2617 (Hebbian CA3 structure-blind
META rule -- unrelated); structured-prediction drill notes at 0.26/0.25. NONE at cosine>0.30 -> genuinely novel
as an experiment, no rediscovery. Prereg's own KB check concurred (concepts known cos~0.31, no prior cell).

A5: read -> build -> tmp write + fsync -> os.replace -> re-read + verify count delta + tail-id match, both files.
LOCAL ONLY: store_head_at_write=unsynced_needs_orchestrator + needs_orchestrator_store_sync=True; NO origin push.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"
ATOMIZED_BY = "skunkworks_landed_vet_srn_predict_category_v1_MM_order_lever_capacity_matched_2026-07-18"
ATOMIZED_DATE = "2026-07-18"
ANCHOR = "srn_predict_category_v1"
CELL_COMMIT = "9d8afcbd1"

XARC = ("substrate_query.sh 'order-sensitive next-word prediction learning induces lexical category structure "
        "beyond static co-occurrence PPMI' -> top hit cosine=0.2617 (meta Hebbian-CA3 structure-blind META "
        "rule, UNRELATED); structured-prediction drill notes at 0.26/0.25. NONE at cosine>0.30. Prereg's own "
        "KB check concurred (concepts 'self-supervised learning'/'lexical category' cos~0.31, but NO prior arc "
        "experiment cell runs this contrast). Genuinely novel as an experiment; no rediscovery.")

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

ATOM_ID = ("math::MM_MEASURED_MECHANISM_srn_predict_category_v1_ORDER_SENSITIVITY_is_the_capacity_matched_lever_"
           "over_static_counting_learner_pos_AMI_0p158_beats_static_PPMI_SVD_0p098_by_plus0p060_mean_3of3_seeds_"
           "7_13_19_spread_0p055_to_0p065_order_BLIND_bag_ablation_TIES_static_delta_bag_minus0p005_bag_and_pos_"
           "have_IDENTICAL_trainable_params_230400_roles_fixed_plusminus1_signbind_0_free_params_so_win_is_ORDER_"
           "not_capacity_byte_reproduce_EXACT_fresh_rerun_NOT_forking_paths_tie_ablation_retained_reported_config_"
           "NOT_max_delta_lr0p003_gives_plus0p165_robust_across_d_lr_epochs_but_WINDOW_CONTINGENT_flips_NEGATIVE_"
           "at_k3_delta_minus0p015_static_jumps_0p167_ABSOLUTE_STRUCTURE_WEAK_purity_0p55_vs_0p499_majority_class_"
           "floor_function_words_DET_NUM_grouped_labeled_NOUN_by_base_rate_only_1of4_clusters_clean_metric_AMI_"
           "chance_corrected_legit_effect_holds_on_NMI_too_real_Brown_prose_CONSTRUCTION_PROOF_not_downstream_"
           "reading_capability_DEFLATED_from_cell_HARD_PASS_9d8afcbd1_2026-07-18")

CLAIM = (
    "MATH MEASURED_MECHANISM (proven-bound; DEFLATED from cell HARD_PASS). On real NLTK Brown prose (~100k "
    "tokens, V=900, 9 universal-POS gold cats), self-supervised next-word PREDICTION-LEARNING with ORDER-"
    "SENSITIVE context (VSA fixed-role position-bind, Elman/SRN-faithful) yields a modest COMPARATIVE edge in "
    "POS-category induction over best-in-class STATIC PPMI-SVD counting of the SAME text: AMI 0.158 vs 0.098, "
    "delta +0.060 mean on 3/3 seeds (spread +0.055..+0.065). The LEVER is cleanly localized to ORDER-"
    "SENSITIVITY and is CAPACITY-MATCHED: the order-BLIND bag ablation TIES static (delta_bag ~ -0.005), and "
    "the order-sensitive arm has IDENTICAL trainable params to the bag arm (2*V*d=230400; roles are a fixed "
    "+/-1 sign-multiply, 0 free params) -- so the win is ORDER, NOT more capacity. VERBATIM BOUNDS: (1) "
    "absolute category structure is WEAK (AMI 0.158 on a 0..1 chance-corrected scale; cluster purity 0.55 vs "
    "0.499 one-cluster majority-class floor; function words DET/NUM/PRON group together but read as 'NOUN' by "
    "base rate; only ~1 of 4 example clusters is a clean POS cluster) -- 'induces category structure' over-"
    "reads; the defensible claim is a modest comparative edge over counting; (2) WINDOW-CONTINGENT -- the "
    "effect flips NEGATIVE at context window k=3 (delta -0.015; static AMI jumps to 0.167), positive at k>=5; "
    "(3) CONSTRUCTION-PROOF that order-sensitive prediction CAN beat counting on this metric -- does NOT prove "
    "downstream reading capability. Revival to CG: demonstrate the comparative edge translates to a downstream "
    "reading/tagging task, or characterize + defend the window-boundary, at multi-corpus scale.")

RECOMPUTE = (
    "INDEP recompute (.venv, fresh full re-run importing the REAL arm functions, off Brown; Fix #28): "
    "BYTE-REPRODUCE EXACT to 4dp -- seed 7 ami_pos=0.1587 ami_bag=0.0731 ami_static=0.0984 delta_pos=+0.0602; "
    "seed 13 ami_pos=0.1624 ami_bag=0.0983 ami_static=0.0974 delta_pos=+0.0650; seed 19 ami_pos=0.1543 "
    "ami_bag=0.1099 ami_static=0.0991 delta_pos=+0.0551. All 3/3 >= HP_MARGIN +0.02; delta_bag mean -0.005 "
    "(TIE with static, the honest control). CAPACITY (the load-bearing check): pos and bag both allocate "
    "E(V,d)+W(V,d)=230400 trainable params; roles are torch.randint fixed +/-1 (gr-seed 20260718, NOT an "
    "nn.Parameter) -> 0 free params added by order-sensitivity -> capacity-matched, win attributable to ORDER. "
    "ROBUSTNESS (seed 7): delta_pos positive across d(64:+0.055, 256:+0.056), lr(0.003:+0.165, 0.03:+0.053), "
    "epochs(8:+0.120, 32:+0.045), k(8:+0.089) -- reported config (+0.060) is NOT the max-delta config (lr/"
    "epochs give larger), arguing AGAINST forking-paths cherry-pick. BUT k=3 FLIPS the sign: delta -0.0146, "
    "static AMI leaps to 0.1666 -> window-contingent boundary. METRIC: AMI is chance-corrected (random AMI "
    "-0.0002, metric fires); NMI shows the same effect (delta +0.059) -> the NMI->AMI switch is conservative, "
    "not metric-shopping. HONESTY: purity_pos 0.55 vs one-cluster majority-class floor 0.4994 (+0.05); example "
    "clusters 0/1/3 are DET/NUM/PRON function words ('the a his this an', 'its two most many those') mislabeled "
    "'NOUN' by the 50% base rate; only cluster 2 (city/house/school, 0.822) is a genuinely clean POS cluster.")

SCOPE = (
    "REAL prose (NLTK Brown, ~100k tokens, 8000 sents, V=900, 9 universal-POS gold cats, 893 gold words), "
    "glass-box numpy/torch(cpu)/sklearn, NO LLM. This is a MECHANISM/construction boundary, NOT capability-at-"
    "scale. Three load-bearing limits: (a) absolute POS-category induction is weak -- AMI 0.158, purity barely "
    "above the majority-class one-cluster floor; the qualitative clustering separates function-word families "
    "but the dominant-gold readout is base-rate-dominated; the load-bearing claim MUST be the COMPARATIVE "
    "contrast (LEARNER_POS > STATIC), never absolute category induction. (b) the comparative edge is WINDOW-"
    "CONTINGENT -- it reverses at k=3 (static wins) and grows at k=8; k=5 sits in the winning region but the "
    "sign is not window-universal, so 'order beats counting' holds only for windows k>=5 on this corpus. (c) "
    "construction-proof only: proves order-sensitive prediction CAN induce more category structure than "
    "counting on this AMI metric; does NOT establish any downstream reading/tagging capability (prereg's own "
    "SECONDARY next-word top-1 is WEAKER than a bigram: learner 0.136 < bigram 0.168, non-load-bearing but "
    "notable). Do NOT bank as reading capability.")

METRICS = {
    "ami_learner_pos_mean": 0.1585, "ami_learner_bag_mean": 0.0938,
    "ami_static_mean": 0.0983, "ami_random_mean": -0.0002,
    "delta_ami_pos_mean": 0.0602, "delta_ami_bag_mean": -0.0045,
    "hp_seeds": 3, "hf_seeds": 0, "hp_margin": 0.02,
    "per_seed_delta_pos": [0.0602, 0.0650, 0.0551],
    "nmi_learner_pos_mean": 0.1763, "nmi_static_mean": 0.1176, "nmi_delta": 0.0587,
    "purity_pos_seed7": 0.5711, "purity_static_seed7": 0.5308, "majority_class_one_cluster_floor": 0.4994,
    "trainable_params_pos": 230400, "trainable_params_bag": 230400, "roles_free_params": 0,
    "robustness_delta_pos": {"base_k5": 0.0602, "k3": -0.0146, "k8": 0.0886, "d64": 0.0549, "d256": 0.0560,
                             "lr0.003": 0.1652, "lr0.03": 0.0533, "epochs8": 0.1204, "epochs32": 0.0452},
    "k3_static_ami": 0.1666,
    "secondary_learner_top1": 0.1357, "secondary_bigram_top1": 0.1684,
    "cell_verdict": "HARD_PASS", "auditor_tier": "MEASURED_MECHANISM (deflated: order-lever proven but bounded)",
}

COMPOSES = [
    "novel as an experiment (no prior arc cell at cosine>0.30). Composes with the reading-arc theme that "
    "keeps 'tying frequency' -- this cell localizes ONE thing prediction-learning adds over static frequency/"
    "counting = ORDER/SEQUENCE-sensitivity (Elman 1990 SRN insight), capacity-matched.",
    "CONSISTENT-WITH the encoding-lever finding (match code to data structure): order-bind is a structural code "
    "the symmetric co-occurrence count cannot represent; the bag ablation tying static is the fair witness.",
    "credit: Elman (1990) SRN category induction (mechanism analog); Levy-Goldberg (2014) word2vec~PPMI-SVD "
    "(the fair static baseline).",
]

atom = {
    "id": ATOM_ID,
    "name": CLAIM,
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": ("confirmed_measured_mechanism_order_sensitivity_is_the_capacity_matched_lever_learner_pos_"
                    "beats_static_ppmi_svd_by_plus0p060_ami_3of3_seeds_bag_ablation_ties_static_identical_params_"
                    "window_contingent_flips_at_k3_absolute_structure_weak_construction_proof_not_reading_"
                    "capability_deflated_from_cell_hard_pass"),
    "cert_class": ("self_supervised_next_word_prediction_learning_order_sensitive_context_induces_modest_"
                   "comparative_pos_category_edge_over_static_ppmi_svd_counting_capacity_matched_order_is_the_"
                   "lever_bag_ties_static_window_contingent_absolute_weak_construction_proof_measured_mechanism"),
    "description": (CLAIM + "\n\nRECOMPUTE (off-disk .venv, Fix #28): " + RECOMPUTE
                    + "\n\nHONEST SCOPE: " + SCOPE),
    "aliases": [],
    "ts_iso": _iso,
    "ts": _ts,
    "metadata": {
        "provenance_quality": "byte_reproduce_exact_fresh_full_rerun_plus_capacity_and_robustness_probes_off_disk",
        "anchor": ANCHOR,
        "cell_commit": CELL_COMMIT,
        "supersedes": None,
        "store_head_at_write": "unsynced_needs_orchestrator",
        "metrics_path": "data/exp_srn_predict_category_v1/metrics.json",
        "verified_off_data": RECOMPUTE,
        "honest_scope": SCOPE,
        "metrics": METRICS,
        "over_reads_corrected": [
            "cell/exp_dev verdict = HARD_PASS with claim 'prediction-LEARNING induces category structure BEYOND "
            "static co-occurrence'. DEFLATED to MEASURED_MECHANISM: (1) 'induces category structure' over-reads "
            "-- absolute AMI 0.158 is weak, purity 0.55 barely clears the 0.499 majority-class one-cluster "
            "floor, and the example clusters are function-word groupings base-rate-labeled 'NOUN'. The "
            "defensible claim is a modest COMPARATIVE edge over static counting, not absolute category "
            "induction.",
            "(2) the +0.060 edge is WINDOW-CONTINGENT (undisclosed in the cell): it FLIPS NEGATIVE at k=3 "
            "(delta -0.015, static AMI 0.167). The 'order beats counting' claim holds only for windows k>=5 on "
            "this corpus; this boundary must be stated.",
            "(3) construction-proof, not capability: the cell's own SECONDARY next-word top-1 is WEAKER than a "
            "bigram (0.136 < 0.168), so this does NOT demonstrate downstream reading benefit.",
        ],
        "genuine_positives_symmetric_anti_negativity": (
            "STRONG, honest positives banked symmetrically: (a) byte-reproduce EXACT on a fresh full re-run; "
            "(b) the CAPACITY confound is CLEANLY ruled out -- pos and bag have identical trainable params "
            "(230400) and roles are a fixed 0-param sign-multiply, so the win is genuinely ORDER-sensitivity, "
            "the single cleanest part of the cell; (c) the bag ablation is a FAIR capacity-matched control and "
            "it ties static exactly as the honest can-fail predicted; (d) NOT forking-paths -- single "
            "principled Elman change, tie-ablation retained + reported, and the reported config is NOT the "
            "max-delta config (lr=0.003/epochs=8 give LARGER deltas), so no cherry-pick toward the headline; "
            "(e) delta positive and 3/3-seed-robust across d, lr, epochs; (f) AMI (chance-corrected) is the "
            "conservative metric choice and the effect also holds on NMI; (g) REAL Brown prose + real POS gold, "
            "unsupervised (gold never touches representation learning)."),
        "revival_criteria": [
            "MM->CG: show the comparative order>counting edge translates to a DOWNSTREAM reading/tagging task "
            "(not just intrinsic clustering AMI), or",
            "characterize + defend the WINDOW-boundary (why k=3 flips; is k>=5 the right regime) at multi-corpus "
            "scale, so the 'order beats counting' claim is not window-lucky, and",
            "a stronger absolute-structure result or a fair-baseline downstream metric, since intrinsic AMI is "
            "weak in absolute terms.",
        ],
        "cross_arc_overlap_check": XARC,
        "cites": [
            "Fix_28_verify_off_data_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "cited_number_must_reproduce_from_cell",
            "verify_the_referent_atom_ids_mechanism_metric_regime",
            "feedback_construction_proof_is_not_a_capability_win",
            "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
            "capacity_matched_control_confound_check_order_vs_params",
        ],
        "composes_with": COMPOSES,
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
    },
}

ledger = {
    "op": "cert_ruling",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": atom["cert_status"],
    "anchor": ANCHOR,
    "cell_commit": CELL_COMMIT,
    "supersedes_commit": None,
    "store_head_at_write": "unsynced_needs_orchestrator",
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": ATOMIZED_BY,
    "verdict": ("MEASURED_MECHANISM_order_sensitivity_is_the_capacity_matched_lever_learner_pos_AMI_0p158_beats_"
                "static_PPMI_SVD_0p098_plus0p060_mean_3of3_seeds_bag_ablation_ties_static_delta_bag_minus0p005_"
                "IDENTICAL_trainable_params_230400_roles_0_free_win_is_ORDER_not_capacity_byte_reproduce_EXACT_"
                "NOT_forking_paths_reported_config_not_max_delta_but_WINDOW_CONTINGENT_flips_at_k3_absolute_"
                "structure_weak_purity_0p55_vs_0p499_floor_construction_proof_not_reading_capability_DEFLATED_"
                "from_cell_HARD_PASS"),
    "cert_increment_delta": 1,
    "decision": (
        "MM (proven-bound), DEFLATED from cell HARD_PASS. Numbers reproduce EXACTLY off-disk (ami_pos 0.158 vs "
        "static 0.098, delta +0.060 mean 3/3 seeds; bag ties static delta -0.005). The order-sensitivity lever "
        "is cleanly PROVEN and CAPACITY-MATCHED (pos and bag identical 230400 trainable params; roles are a "
        "0-param fixed sign-multiply) -- the strongest part of the cell. NOT forking-paths: single principled "
        "Elman change, tie-ablation retained + reported, reported config is NOT max-delta (lr=0.003 gives "
        "+0.165). BUT bounded: (1) absolute structure WEAK (AMI 0.158, purity 0.55 vs 0.499 floor; function "
        "words base-rate-labeled NOUN) so 'induces category structure' over-reads -> defensible = modest "
        "COMPARATIVE edge; (2) WINDOW-CONTINGENT (flips negative at k=3, static jumps to 0.167); (3) "
        "construction-proof, not capability (secondary next-word 0.136 < bigram 0.168). Counts toward CERT as "
        "a proven mechanism boundary."),
    "framing_correction_vs_director": (
        "Director flagged this as the HARD_PASS 'most wanted to be true' (core language engine) and asked me to "
        "audit over-optimism HARDEST. I DEFLATE HARD_PASS -> MEASURED_MECHANISM (symmetric anti-negativity: "
        "honest downward). The order-lever mechanism is real, capacity-matched, and NOT p-hacked -- credit "
        "where due. But the headline 'induces category structure' over-reads a weak-absolute, window-contingent "
        "comparative edge, and it is a construction-proof, NOT downstream reading capability (the cell's own "
        "secondary next-word metric LOSES to a bigram). exp_dev's flagged caveats (modest effect, post-hoc "
        "iteration) are BOTH real; the post-hoc iteration is honest (not forking-paths) but the modest-effect "
        "caveat is load-bearing. Bank as a proven mechanism boundary, not as the language engine working."),
    "cross_arc_overlap_check": XARC,
    "net_cert_delta": ("+1 MM (proven mechanism boundary: order-sensitivity is the capacity-matched lever by "
                       "which self-supervised prediction-learning gains a modest, window-contingent comparative "
                       "POS-category edge over static counting on real Brown prose; construction-proof, "
                       "capability OPEN)."),
    "supersedes": None,
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
    "ts_iso": _iso,
    "ts": _ts,
    "atom_id": ATOM_ID,
}


def write_atomic_append(path, new_lines):
    if not path.exists():
        return (0, 0, False, "path does not exist: %s" % path)
    with open(path, "rb") as f:
        cur_bytes = f.read()
    cur_text = cur_bytes.decode("utf-8")
    pre_count = cur_text.count("\n")
    if cur_bytes and not cur_bytes.endswith(b"\n"):
        cur_bytes = cur_bytes + b"\n"
    parts = [cur_bytes]
    for line in new_lines:
        s = json.dumps(line, ensure_ascii=True)
        if "\n" in s:
            return (pre_count, pre_count, False, "JSON contains newline; not jsonl-safe")
        parts.append((s + "\n").encode("utf-8"))
    new_bytes = b"".join(parts)
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "wb") as f:
        f.write(new_bytes); f.flush(); os.fsync(f.fileno())
    os.replace(tmp_path, path)
    with open(path, "rb") as f:
        verify_text = f.read().decode("utf-8")
    post_count = verify_text.count("\n")
    expected_post = pre_count + len(new_lines)
    if post_count != expected_post:
        return (pre_count, post_count, False, "line count mismatch: expected %d got %d" % (expected_post, post_count))
    tail = verify_text.rstrip("\n").split("\n")[-len(new_lines):]
    for i, tl in enumerate(tail):
        try:
            parsed = json.loads(tl)
        except Exception as e:
            return (pre_count, post_count, False, "tail-line %d JSON round-trip fail: %s" % (i, e))
        for key in ("id", "atom_id"):
            if key in new_lines[i] and parsed.get(key) != new_lines[i][key]:
                return (pre_count, post_count, False, "tail-line %d %s mismatch" % (i, key))
    return (pre_count, post_count, True, "OK")


def main():
    print("=== A5 atom-write: srn_predict_category_v1 -> MM (order lever, capacity-matched) (2026-07-18) ===")
    print("ts_iso =", _iso)
    assert atom["id"].isascii(), "non-ascii atom id"
    assert ledger["atom_id"] == atom["id"], "atom_id / id mismatch"

    existing = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                existing.add(json.loads(line).get("id"))
            except Exception:
                pass
    if atom["id"] in existing:
        print("ABORT: id already in store"); sys.exit(1)
    print("id-uniqueness OK (1 new, not pre-existing)")

    print("Writing 1 atom to math/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(MATH_ATOMS, [atom])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: math atoms write failed"); sys.exit(1)

    print("Writing 1 row to meta/cert_ledger.jsonl ...")
    pre, post, ok, err = write_atomic_append(CERT_LEDGER, [ledger])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: cert_ledger write failed"); sys.exit(1)

    n_ok = 0
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            json.loads(line); n_ok += 1
    present = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                present.add(json.loads(line).get("id"))
            except Exception:
                pass
    assert atom["id"] in present, "post-write integrity: new id missing"
    print("integrity: math/atoms.jsonl fully parses (%d lines), new id present." % n_ok)
    print()
    print("=== A5 WRITE COMPLETE (LOCAL ONLY; needs_orchestrator_store_sync=True) ===")
    print("ATOM_ID:", atom["id"])


if __name__ == "__main__":
    main()
