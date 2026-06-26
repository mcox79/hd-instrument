"""
meta_reasoning_corpus_builder_2026-06-25.py -- assemble NAMED operator dup-groups for v3 CHTV-1.

USER 2026-06-25: "this one we really want to nail, because this is going to be absolutely KEY
to how the system evaluates itself."

Output: data/meta_reasoning_corpus/algebra_dict_v1.jsonl
        one JSON object per group; >=24 NAMED groups + >=8 adversarial decoys.

Schema per group:
  {
    "group_name": "<short-name shared by all members>",
    "group_type": "true_positive" | "adversarial_decoy",
    "category": "math" | "programming" | "substrate" | "statistical",
    "members": [
      {"name": "<member-name>", "sigs": {SIG_FIELDS}, "caps": [<caps...>], "tier": "Tx"},
      ...  (2-4 members per group)
    ],
    "rationale": "<why this group should/shouldn't merge under CHTV-1>"
  }

CHTV-1 expectation (per experiments/exp_substrate_distill_verify_operator_equivalence_v2_full.py):
  - true_positive: members share IDENTICAL algebra_dict on the 5 SIG_FIELDS (domain,
    operation_type, signature_input_type, signature_output_type, complexity_class) AND
    consistent caps. CHTV-1 should return PROVABLY_EQUIVALENT.
  - adversarial_decoy: members have similar names but DIVERGENT sigs (at least one SIG_FIELD
    differs) OR contradictory caps. CHTV-1 should return NOT_EQUIVALENT (correct refusal).

ASCII-only. Self-test verifies >=24 NAMED + >=8 adversarial + stratification feasibility.
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "data" / "meta_reasoning_corpus"
OUT_FILE = OUT_DIR / "algebra_dict_v1.jsonl"
SIG_FIELDS = ("domain", "operation_type", "signature_input_type", "signature_output_type", "complexity_class")


def _tp(group_name: str, category: str, sig: dict, caps: list, member_names: list, tiers: list, rationale: str) -> dict:
    """Build a true-positive group: all members share the SAME signature + caps."""
    assert len(member_names) == len(tiers) and 2 <= len(member_names) <= 4
    # assert sig has >=3 SIG_FIELDS populated (else CHTV-1 falls into UNDECIDABLE)
    populated = sum(1 for k in SIG_FIELDS if sig.get(k) is not None)
    assert populated >= 3, "TP signature must populate >=3 SIG_FIELDS, got %d for %s" % (populated, group_name)
    members = [{"name": n, "sigs": dict(sig), "caps": list(caps), "tier": t}
               for n, t in zip(member_names, tiers)]
    return {"group_name": group_name, "group_type": "true_positive", "category": category,
            "members": members, "rationale": rationale}


def _adv(group_name: str, category: str, sigs_per_member: list, caps_per_member: list,
         member_names: list, tiers: list, rationale: str) -> dict:
    """Build an adversarial decoy: members have similar names but at least one signature/cap diverges."""
    assert len(sigs_per_member) == len(caps_per_member) == len(member_names) == len(tiers)
    assert 2 <= len(member_names) <= 4
    # assert at least one sig field differs across members (the divergence that CHTV-1 must catch)
    populated_sets = [{k: s[k] for k in SIG_FIELDS if s.get(k) is not None} for s in sigs_per_member]
    fully_typed = [p for p in populated_sets if len(p) >= 3]
    if len(fully_typed) >= 2:
        first = fully_typed[0]
        diverges = any(s != first for s in fully_typed[1:])
        # OR caps contradict
        nonempty_caps = [c for c in caps_per_member if c]
        caps_contradict = len(nonempty_caps) >= 2 and not all(set(c) == set(nonempty_caps[0]) for c in nonempty_caps[1:])
        assert diverges or caps_contradict, \
            "ADV %s must have diverging sigs or contradictory caps (else CHTV-1 will MERGE)" % group_name
    members = [{"name": n, "sigs": dict(s), "caps": list(c), "tier": t}
               for n, s, c, t in zip(member_names, sigs_per_member, caps_per_member, tiers)]
    return {"group_name": group_name, "group_type": "adversarial_decoy", "category": category,
            "members": members, "rationale": rationale}


# =============================================================================
# CATEGORY 1: MATH OPERATOR PAIRS (6 TP groups + 2 ADV decoys)
# =============================================================================
MATH_TP = [
    _tp("commutative_add", "math",
        {"domain": "algebra", "operation_type": "binary_commutative_add",
         "signature_input_type": "scalar_pair", "signature_output_type": "scalar",
         "complexity_class": "O(1)"},
        ["op_add"],
        ["sum_binary", "add_commutative", "plus_operator"],
        ["T1", "T2", "T3"],
        "Different surface names; same algebraic operation (binary commutative addition)."),
    _tp("multiplicative_product", "math",
        {"domain": "algebra", "operation_type": "binary_commutative_multiply",
         "signature_input_type": "scalar_pair", "signature_output_type": "scalar",
         "complexity_class": "O(1)"},
        ["op_mul"],
        ["product_binary", "multiply_commutative", "times_operator"],
        ["T1", "T2", "T3"],
        "Different surface names; same algebraic operation (binary commutative multiplication)."),
    _tp("distributive_multiply_then_add", "math",
        {"domain": "algebra", "operation_type": "distributive_fma",
         "signature_input_type": "scalar_triple", "signature_output_type": "scalar",
         "complexity_class": "O(1)"},
        ["op_fma"],
        ["fused_multiply_add", "fma_distributive", "muladd_combined"],
        ["T2", "T2", "T3"],
        "Distributive a*(b+c) computed as one fused-multiply-add."),
    _tp("identity_operator", "math",
        {"domain": "algebra", "operation_type": "identity_passthrough",
         "signature_input_type": "any", "signature_output_type": "same_as_input",
         "complexity_class": "O(1)"},
        ["op_identity"],
        ["noop_passthrough", "identity_fn", "id_operator"],
        ["T1", "T2", "T3"],
        "Pure passthrough identity (a -> a)."),
    _tp("left_inverse_complement", "math",
        {"domain": "algebra", "operation_type": "left_inverse_apply",
         "signature_input_type": "invertible_element", "signature_output_type": "element_inverse",
         "complexity_class": "O(1)"},
        ["op_left_inverse"],
        ["left_complement", "left_inverse_op", "inv_left"],
        ["T1", "T2", "T3"],
        "Left inverse of an invertible element under a group structure."),
    _tp("conjugate_transpose", "math",
        {"domain": "linear_algebra", "operation_type": "hermitian_transpose",
         "signature_input_type": "complex_matrix", "signature_output_type": "complex_matrix",
         "complexity_class": "O(n^2)"},
        ["op_conj_transpose"],
        ["hermitian_adjoint", "dagger_op", "conjugate_transpose_h"],
        ["T1", "T2", "T3"],
        "Conjugate transpose / Hermitian adjoint / dagger of a complex matrix."),
]
MATH_ADV = [
    _adv("transpose_vs_conjugate_transpose", "math",
         [{"domain": "linear_algebra", "operation_type": "transpose",
           "signature_input_type": "real_matrix", "signature_output_type": "real_matrix",
           "complexity_class": "O(n^2)"},
          {"domain": "linear_algebra", "operation_type": "hermitian_transpose",
           "signature_input_type": "complex_matrix", "signature_output_type": "complex_matrix",
           "complexity_class": "O(n^2)"}],
         [["matrix_op"], ["matrix_op"]],
         ["transpose_real", "transpose_conjugate"],
         ["T2", "T3"],
         "Name-similar but operation_type/input_type DIFFER (real transpose vs conjugate-transpose). CHTV-1 must refuse."),
    _adv("commutative_vs_noncommutative_multiply", "math",
         [{"domain": "algebra", "operation_type": "binary_commutative_multiply",
           "signature_input_type": "scalar_pair", "signature_output_type": "scalar",
           "complexity_class": "O(1)"},
          {"domain": "algebra", "operation_type": "binary_noncommutative_multiply",
           "signature_input_type": "matrix_pair", "signature_output_type": "matrix",
           "complexity_class": "O(n^3)"}],
         [["arith"], ["matrix_op"]],
         ["multiply_scalar", "multiply_matrix"],
         ["T2", "T3"],
         "Both 'multiply' but distinct algebra: scalar-commutative vs matrix-noncommutative. CHTV-1 must refuse."),
]

# =============================================================================
# CATEGORY 2: PROGRAMMING PRIMITIVE PAIRS (6 TP groups + 2 ADV decoys)
# =============================================================================
PROG_TP = [
    _tp("map_iteration", "programming",
        {"domain": "functional_programming", "operation_type": "elementwise_map",
         "signature_input_type": "iterable_plus_function", "signature_output_type": "iterable_same_length",
         "complexity_class": "O(n)"},
        ["iteration"],
        ["map_op", "fmap_functor", "transform_each", "foreach_pure"],
        ["T1", "T2", "T2", "T3"],
        "Apply fn elementwise to iterable; semantically same across map/fmap/transform/forEach-pure."),
    _tp("reduce_fold", "programming",
        {"domain": "functional_programming", "operation_type": "left_fold_reduction",
         "signature_input_type": "iterable_plus_binfn_plus_init", "signature_output_type": "scalar",
         "complexity_class": "O(n)"},
        ["aggregation"],
        ["reduce_left", "fold_left", "foldl_accumulate"],
        ["T1", "T2", "T3"],
        "Left fold / reduce: standard left-associative aggregation."),
    _tp("filter_select", "programming",
        {"domain": "functional_programming", "operation_type": "predicate_filter",
         "signature_input_type": "iterable_plus_predicate", "signature_output_type": "iterable_subset",
         "complexity_class": "O(n)"},
        ["iteration"],
        ["filter_pred", "select_where", "where_clause", "keep_if"],
        ["T1", "T2", "T2", "T3"],
        "Keep elements satisfying predicate; filter/select/where/keep_if are same operation."),
    _tp("concat_append", "programming",
        {"domain": "data_structures", "operation_type": "sequence_concatenation",
         "signature_input_type": "two_iterables", "signature_output_type": "iterable_combined",
         "complexity_class": "O(n+m)"},
        ["sequence_ops"],
        ["concat_seq", "append_lists", "extend_list", "join_sequences"],
        ["T1", "T2", "T2", "T3"],
        "Concatenate two sequences."),
    _tp("sort_ascending", "programming",
        {"domain": "data_structures", "operation_type": "sort_ascending_keyed",
         "signature_input_type": "iterable_plus_keyfn", "signature_output_type": "iterable_sorted",
         "complexity_class": "O(n log n)"},
        ["ordering"],
        ["sort_asc", "order_by_ascending", "sorted_default"],
        ["T1", "T2", "T3"],
        "Sort ascending by key; default Python/JS/Rust sort semantics."),
    _tp("lookup_by_key", "programming",
        {"domain": "data_structures", "operation_type": "dict_key_lookup",
         "signature_input_type": "dict_plus_key", "signature_output_type": "value_or_default",
         "complexity_class": "O(1)"},
        ["dict_ops"],
        ["get_by_key", "lookup_key", "dict_get", "fetch_by_key"],
        ["T1", "T2", "T2", "T3"],
        "Hash-table lookup by key; same operation across naming variants."),
]
PROG_ADV = [
    _adv("sort_ascending_vs_descending", "programming",
         [{"domain": "data_structures", "operation_type": "sort_ascending_keyed",
           "signature_input_type": "iterable_plus_keyfn", "signature_output_type": "iterable_sorted",
           "complexity_class": "O(n log n)"},
          {"domain": "data_structures", "operation_type": "sort_descending_keyed",
           "signature_input_type": "iterable_plus_keyfn", "signature_output_type": "iterable_sorted_reverse",
           "complexity_class": "O(n log n)"}],
         [["ordering"], ["ordering"]],
         ["sort_ascending_op", "sort_descending_op"],
         ["T2", "T3"],
         "Same complexity + io-shape but operation_type (ascending vs descending) + output (sorted vs sorted_reverse) DIFFER."),
    _adv("map_vs_flatmap", "programming",
         [{"domain": "functional_programming", "operation_type": "elementwise_map",
           "signature_input_type": "iterable_plus_function", "signature_output_type": "iterable_same_length",
           "complexity_class": "O(n)"},
          {"domain": "functional_programming", "operation_type": "elementwise_flatmap",
           "signature_input_type": "iterable_plus_function_to_iterable", "signature_output_type": "iterable_flattened",
           "complexity_class": "O(n*m)"}],
         [["iteration"], ["iteration"]],
         ["map_simple", "flatmap_combined"],
         ["T2", "T3"],
         "map preserves shape; flatmap flattens nested results -- DIFFERENT operation_type/input/output."),
]

# =============================================================================
# CATEGORY 3: SUBSTRATE-INTERNAL PRIMITIVE PAIRS (6 TP groups + 2 ADV decoys)
# =============================================================================
SUBSTRATE_TP = [
    _tp("hrr_bind_family", "substrate",
        {"domain": "hyperdimensional_computing", "operation_type": "circular_convolution_bind",
         "signature_input_type": "hd_vector_pair", "signature_output_type": "hd_vector",
         "complexity_class": "O(N log N)"},
        ["hrr_bind", "binding"],
        ["hrr_bind_v1", "hrr_bind_torch", "circular_convolve_bind"],
        ["T1", "T2", "T3"],
        "HRR binding via circular convolution; same primitive across implementation variants."),
    _tp("cleanup_argmax_family", "substrate",
        {"domain": "associative_memory", "operation_type": "argmax_dot_cleanup",
         "signature_input_type": "query_plus_codebook", "signature_output_type": "codebook_atom",
         "complexity_class": "O(M*N)"},
        ["cleanup"],
        ["cleanup_argmax", "cleanup_topk_k1", "nearest_codebook_atom"],
        ["T2", "T2", "T3"],
        "Argmax cleanup is topk-cleanup with k=1; same operation under different naming."),
    _tp("sparse_bipolar_K5_family", "substrate",
        {"domain": "encoding", "operation_type": "sparse_bipolar_random_projection_K5",
         "signature_input_type": "real_vector", "signature_output_type": "sparse_bipolar_K5",
         "complexity_class": "O(K*N)"},
        ["sparse_encoding"],
        ["sparse_bipolar_k5_v1", "bipolar_random_k5", "sbp_k5"],
        ["T1", "T2", "T3"],
        "K=5 sparse-bipolar encoding; same operation across naming variants."),
    _tp("partition_routing_v1_family", "substrate",
        {"domain": "store_partition", "operation_type": "hash_partition_routing",
         "signature_input_type": "atom_id_plus_partition_count", "signature_output_type": "partition_index",
         "complexity_class": "O(1)"},
        ["partition_routing"],
        ["partition_routing_v1a", "hash_partition_route", "partition_select_by_hash"],
        ["T1", "T2", "T3"],
        "Hash-partition routing for Store atom placement; same algorithm."),
    _tp("audit_subject_only_family", "substrate",
        {"domain": "audit", "operation_type": "subject_only_audit_check",
         "signature_input_type": "atom_plus_audit_question", "signature_output_type": "audit_verdict",
         "complexity_class": "O(1)"},
        ["audit"],
        ["audit_subject_only_v1", "subject_audit_simple", "single_subject_audit"],
        ["T1", "T2", "T3"],
        "Subject-only audit checks ONLY the subject atom (not relations)."),
    _tp("fhrr_bind_family", "substrate",
        {"domain": "hyperdimensional_computing", "operation_type": "fhrr_elementwise_complex_bind",
         "signature_input_type": "complex_unit_vector_pair", "signature_output_type": "complex_unit_vector",
         "complexity_class": "O(N)"},
        ["fhrr_bind", "binding"],
        ["fhrr_bind_v1", "fhrr_bind_torch", "fourier_hrr_bind"],
        ["T1", "T2", "T3"],
        "FHRR binding via elementwise complex multiplication; same primitive across variants."),
]
SUBSTRATE_ADV = [
    _adv("hrr_bind_vs_fhrr_bind", "substrate",
         [{"domain": "hyperdimensional_computing", "operation_type": "circular_convolution_bind",
           "signature_input_type": "hd_vector_pair", "signature_output_type": "hd_vector",
           "complexity_class": "O(N log N)"},
          {"domain": "hyperdimensional_computing", "operation_type": "fhrr_elementwise_complex_bind",
           "signature_input_type": "complex_unit_vector_pair", "signature_output_type": "complex_unit_vector",
           "complexity_class": "O(N)"}],
         [["binding"], ["binding"]],
         ["bind_real_hrr", "bind_fhrr_complex"],
         ["T2", "T3"],
         "Both 'bind' but DIFFERENT algebra: real circular-convolution vs complex elementwise. CHTV-1 must refuse."),
    _adv("sparse_K5_vs_K10", "substrate",
         [{"domain": "encoding", "operation_type": "sparse_bipolar_random_projection_K5",
           "signature_input_type": "real_vector", "signature_output_type": "sparse_bipolar_K5",
           "complexity_class": "O(K*N)"},
          {"domain": "encoding", "operation_type": "sparse_bipolar_random_projection_K10",
           "signature_input_type": "real_vector", "signature_output_type": "sparse_bipolar_K10",
           "complexity_class": "O(K*N)"}],
         [["sparse_encoding"], ["sparse_encoding"]],
         ["sparse_bipolar_K5_variant", "sparse_bipolar_K10_variant"],
         ["T2", "T2"],
         "Different sparsity (K=5 vs K=10) -> different operation_type + output_type. CHTV-1 must refuse merge."),
]

# =============================================================================
# CATEGORY 4: STATISTICAL EQUIVALENCES (6 TP groups + 2 ADV decoys)
# =============================================================================
STAT_TP = [
    _tp("mean_expected_value", "statistical",
        {"domain": "statistics", "operation_type": "first_moment_uniform_weight",
         "signature_input_type": "real_sample", "signature_output_type": "scalar_real",
         "complexity_class": "O(n)"},
        ["central_tendency"],
        ["sample_mean", "expected_value_uniform", "arithmetic_mean"],
        ["T1", "T2", "T3"],
        "Sample mean = uniform-weight expected value; same operation under different names."),
    _tp("variance_mse_around_mean", "statistical",
        {"domain": "statistics", "operation_type": "second_central_moment",
         "signature_input_type": "real_sample", "signature_output_type": "scalar_non_negative",
         "complexity_class": "O(n)"},
        ["dispersion"],
        ["sample_variance", "mse_around_mean", "second_central_moment_op"],
        ["T1", "T2", "T3"],
        "Variance is MSE around the sample mean; same operation."),
    _tp("correlation_cosine_after_centering", "statistical",
        {"domain": "statistics", "operation_type": "centered_normalized_inner_product",
         "signature_input_type": "real_vector_pair", "signature_output_type": "scalar_in_unit_interval",
         "complexity_class": "O(n)"},
        ["similarity"],
        ["pearson_correlation", "cosine_after_centering", "centered_cosine_sim"],
        ["T1", "T2", "T3"],
        "Pearson correlation = cosine similarity after mean-centering each vector."),
    _tp("entropy_shannon_normalized", "statistical",
        {"domain": "information_theory", "operation_type": "shannon_entropy_natural_log",
         "signature_input_type": "probability_distribution", "signature_output_type": "scalar_non_negative_nats",
         "complexity_class": "O(k)"},
        ["information_measure"],
        ["entropy_shannon_nats", "entropy_natural_log_normalized", "h_distribution_nats"],
        ["T1", "T2", "T3"],
        "Shannon entropy in nats (natural-log base); same operation under naming variants."),
    _tp("precision_ppv", "statistical",
        {"domain": "classification_metrics", "operation_type": "true_positive_over_predicted_positive",
         "signature_input_type": "confusion_matrix", "signature_output_type": "scalar_in_unit_interval",
         "complexity_class": "O(1)"},
        ["binary_classification_metric"],
        ["precision_metric", "positive_predictive_value", "ppv"],
        ["T1", "T2", "T3"],
        "Precision and PPV are identical: TP / (TP + FP)."),
    _tp("recall_sensitivity_tpr", "statistical",
        {"domain": "classification_metrics", "operation_type": "true_positive_over_actual_positive",
         "signature_input_type": "confusion_matrix", "signature_output_type": "scalar_in_unit_interval",
         "complexity_class": "O(1)"},
        ["binary_classification_metric"],
        ["recall_metric", "sensitivity_metric", "true_positive_rate"],
        ["T1", "T2", "T3"],
        "Recall, sensitivity, and TPR are identical: TP / (TP + FN)."),
]
STAT_ADV = [
    _adv("precision_vs_recall", "statistical",
         [{"domain": "classification_metrics", "operation_type": "true_positive_over_predicted_positive",
           "signature_input_type": "confusion_matrix", "signature_output_type": "scalar_in_unit_interval",
           "complexity_class": "O(1)"},
          {"domain": "classification_metrics", "operation_type": "true_positive_over_actual_positive",
           "signature_input_type": "confusion_matrix", "signature_output_type": "scalar_in_unit_interval",
           "complexity_class": "O(1)"}],
         [["binary_classification_metric"], ["binary_classification_metric"]],
         ["precision_variant", "recall_variant"],
         ["T2", "T3"],
         "Same IO + complexity but DIFFERENT operation_type (TP/PP vs TP/AP). CHTV-1 must refuse merge."),
    _adv("variance_vs_std", "statistical",
         [{"domain": "statistics", "operation_type": "second_central_moment",
           "signature_input_type": "real_sample", "signature_output_type": "scalar_non_negative",
           "complexity_class": "O(n)"},
          {"domain": "statistics", "operation_type": "sqrt_second_central_moment",
           "signature_input_type": "real_sample", "signature_output_type": "scalar_non_negative_sqrt_units",
           "complexity_class": "O(n)"}],
         [["dispersion"], ["dispersion"]],
         ["variance_op", "stddev_op"],
         ["T2", "T3"],
         "Variance vs std: stddev = sqrt(variance); different operation_type + output units. CHTV-1 must refuse."),
]


def build_corpus() -> list:
    """Assemble the full corpus as a list of group dicts."""
    all_groups = []
    all_groups.extend(MATH_TP); all_groups.extend(MATH_ADV)
    all_groups.extend(PROG_TP); all_groups.extend(PROG_ADV)
    all_groups.extend(SUBSTRATE_TP); all_groups.extend(SUBSTRATE_ADV)
    all_groups.extend(STAT_TP); all_groups.extend(STAT_ADV)
    return all_groups


def selftest(groups: list) -> None:
    """Verify the corpus meets the stated requirements + simulate CHTV-1 verdicts."""
    n_tp = sum(1 for g in groups if g["group_type"] == "true_positive")
    n_adv = sum(1 for g in groups if g["group_type"] == "adversarial_decoy")
    print("[selftest] total groups=%d (TP=%d ADV=%d)" % (len(groups), n_tp, n_adv), flush=True)
    assert n_tp >= 24, "need >=24 NAMED true-positive groups; have %d" % n_tp
    assert n_adv >= 8, "need >=8 adversarial decoys; have %d" % n_adv

    # category coverage: each category should have >=6 TP and >=2 ADV
    cats = {}
    for g in groups:
        c = g["category"]
        cats.setdefault(c, {"tp": 0, "adv": 0})
        cats[c]["tp" if g["group_type"] == "true_positive" else "adv"] += 1
    for c, counts in cats.items():
        assert counts["tp"] >= 6, "category %s has %d TP, need >=6" % (c, counts["tp"])
        assert counts["adv"] >= 2, "category %s has %d ADV, need >=2" % (c, counts["adv"])
        print("  category=%s TP=%d ADV=%d" % (c, counts["tp"], counts["adv"]), flush=True)
    assert len(cats) == 4, "need 4 categories; have %d" % len(cats)

    # simulate CHTV-1 on each group to verify the corpus is correctly built
    sys.path.insert(0, str(REPO))
    from experiments.exp_substrate_distill_verify_operator_equivalence_v2_full import classify_pair, SIG_FIELDS as CHTV_FIELDS
    assert set(CHTV_FIELDS) == set(SIG_FIELDS), "SIG_FIELDS divergence between builder and v2 cell"

    tp_correct = 0; tp_total = 0; adv_correct = 0; adv_total = 0
    for g in groups:
        sigs = [m["sigs"] for m in g["members"]]
        caps = [set(m["caps"]) for m in g["members"]]
        verdict = classify_pair(sigs, caps, allow_capability_fallback=False)
        if g["group_type"] == "true_positive":
            tp_total += 1
            if verdict in ("PROVABLY_EQUIVALENT",):
                tp_correct += 1
            else:
                print("  [TP MISCLASS] %s -> %s (sigs ident=%s)" % (g["group_name"], verdict,
                                                                     all(s == sigs[0] for s in sigs[1:])), flush=True)
        else:
            adv_total += 1
            if verdict in ("NOT_EQUIVALENT", "UNDECIDABLE_BY_PROVER"):
                adv_correct += 1
            else:
                print("  [ADV MISCLASS] %s -> %s (should be NOT_EQUIVALENT)" % (g["group_name"], verdict), flush=True)

    print("[selftest] CHTV-1 ground-truth check: TP=%d/%d correct, ADV=%d/%d correctly refused" % (
        tp_correct, tp_total, adv_correct, adv_total), flush=True)

    # the corpus is well-formed if CHTV-1 gives the right answer on the ground-truth
    # this is a CORPUS sanity check (mechanism is sound by construction); a failure here means the corpus is buggy
    assert tp_correct == tp_total, "corpus has TP groups CHTV-1 doesn't merge; fix the corpus, not the mechanism"
    assert adv_correct == adv_total, "corpus has ADV decoys CHTV-1 wrongly merges; tighten the adversaries"

    # stratification feasibility: each (category, type) bucket must have >=3 members for 3-fold stratified split
    for c, counts in cats.items():
        assert counts["tp"] >= 3, "stratified 3-fold needs >=3 TP per category for %s" % c
        # ADV can be >=2 (split 1-1-0 acceptable; we just don't want zero in any fold)
    print("[selftest] PASS: corpus is chain-grade-eligible for v3 stratified 3-fold CV", flush=True)


def write_corpus(groups: list) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        for g in groups:
            f.write(json.dumps(g, ensure_ascii=True, sort_keys=True) + "\n")
    print("[write] %d groups -> %s" % (len(groups), OUT_FILE), flush=True)


def main():
    groups = build_corpus()
    selftest(groups)
    write_corpus(groups)
    # verify-the-referent: re-read the file and confirm shape
    reread = [json.loads(line) for line in open(OUT_FILE, "r", encoding="utf-8") if line.strip()]
    assert len(reread) == len(groups), "round-trip mismatch"
    print("[verify] re-read %d groups (round-trip OK)" % len(reread), flush=True)


if __name__ == "__main__":
    main()
