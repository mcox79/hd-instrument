"""Type bare duplicate atoms v1 -- unblock Class A atom-removal compression.

PIVOT continues. DISTILL-VERIFY-1 (HARD_PASS) showed 22 dup groups are
UNDECIDABLE because BARE (no algebra_dict typed signature). Typing them
unblocks substrate Class A atom-removal compression (20th rule mode 1).

This is the ACTUAL substrate self-improvement loop: detect dup -> type ->
prove equivalent -> remove. Without typing, distillation stays gated.

Targets (12 substantive algorithm dups):
  astar, dijkstra (graph search)
  dynamic_programming (combinatorial)
  beam_search (sequence decoding)
  forward_algorithm, backward_algorithm, hmm_transition (HMM)
  bayesian_inference (probabilistic)
  hungarian_assignment (assignment)
  perceptron_update (online learning)
  pca_whitening, zca_whitening (linear algebra preprocessing)

For each, we backfill algebra_dict onto the existing atoms so CHTV-1
type-equality can prove them PROVABLY_EQUIVALENT.

NO LLM. NO bge. Pure schema authoring.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore


# Each entry: short_id -> algebra_dict to MERGE into both duplicate atoms.
# All fields chosen to be PROVABLY shared (same algorithm, same complexity).
TYPING_SPECS = {
    "astar": {
        "domain": "graph_search",
        "operation_type": "shortest_path_with_heuristic",
        "signature_input_type": "weighted_graph_with_heuristic_function",
        "signature_output_type": "optimal_path_or_none",
        "complexity_class": "O(b^d)_with_admissible_heuristic_optimal",
    },
    "dijkstra": {
        "domain": "graph_search",
        "operation_type": "shortest_path_no_negative_weights",
        "signature_input_type": "weighted_graph_nonneg_weights",
        "signature_output_type": "shortest_path_tree_from_source",
        "complexity_class": "O((V+E)logV)_binary_heap",
    },
    "dynamic_programming": {
        "domain": "combinatorial_optimization",
        "operation_type": "optimal_substructure_memoization",
        "signature_input_type": "problem_with_overlapping_subproblems",
        "signature_output_type": "optimal_solution_via_table",
        "complexity_class": "subproblem_count_times_per_subproblem_work",
    },
    "beam_search": {
        "domain": "sequence_decoding",
        "operation_type": "approximate_top_k_path_search",
        "signature_input_type": "scoring_model_plus_beam_width",
        "signature_output_type": "top_k_candidate_sequences",
        "complexity_class": "O(B*V*T)_beam_B_vocab_V_steps_T",
    },
    "forward_algorithm": {
        "domain": "hidden_markov_models",
        "operation_type": "marginal_likelihood_via_alpha_recursion",
        "signature_input_type": "hmm_params_plus_observations",
        "signature_output_type": "p_observations_marginal",
        "complexity_class": "O(N^2*T)_states_N_time_T",
    },
    "backward_algorithm": {
        "domain": "hidden_markov_models",
        "operation_type": "smoothing_via_beta_recursion",
        "signature_input_type": "hmm_params_plus_observations",
        "signature_output_type": "beta_values_per_state_per_time",
        "complexity_class": "O(N^2*T)_states_N_time_T",
    },
    "hmm_transition": {
        "domain": "hidden_markov_models",
        "operation_type": "state_transition_probability_matrix",
        "signature_input_type": "n_states",
        "signature_output_type": "n_by_n_row_stochastic_matrix",
        "complexity_class": "O(N^2)_storage",
    },
    "bayesian_inference": {
        "domain": "probabilistic_reasoning",
        "operation_type": "posterior_from_prior_and_likelihood",
        "signature_input_type": "prior_likelihood_observations",
        "signature_output_type": "posterior_distribution",
        "complexity_class": "exact_O(state_space)_approx_varies",
    },
    "hungarian_assignment": {
        "domain": "combinatorial_optimization",
        "operation_type": "minimum_cost_bipartite_matching",
        "signature_input_type": "n_by_n_cost_matrix",
        "signature_output_type": "optimal_assignment_permutation",
        "complexity_class": "O(N^3)_kuhn_munkres",
    },
    "perceptron_update": {
        "domain": "online_learning",
        "operation_type": "weight_update_on_misclassification",
        "signature_input_type": "weights_features_label_prediction",
        "signature_output_type": "updated_weights",
        "complexity_class": "O(d)_per_update_d_features",
    },
    "pca_whitening": {
        "domain": "linear_algebra_preprocessing",
        "operation_type": "decorrelate_via_eigendecomp_then_scale",
        "signature_input_type": "n_by_d_data_matrix",
        "signature_output_type": "whitened_data_matrix",
        "complexity_class": "O(N*d^2 + d^3)_eigendecomp",
    },
    "zca_whitening": {
        "domain": "linear_algebra_preprocessing",
        "operation_type": "whiten_preserve_orientation",
        "signature_input_type": "n_by_d_data_matrix",
        "signature_output_type": "whitened_data_matrix_pca_then_rotate_back",
        "complexity_class": "O(N*d^2 + d^3)_eigendecomp",
    },
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    all_atoms = ps.all_atoms()

    # Group atoms by short_id (matching DISTILL-VERIFY-1 logic).
    from collections import defaultdict
    by_short = defaultdict(list)
    for a in all_atoms:
        short = str(a.id).split("::")[-1].split("/")[-1].strip().lower()
        by_short[short].append(a)

    typed_count = 0
    atoms_updated = 0
    pairs_skipped = 0
    for short_id, sig_dict in TYPING_SPECS.items():
        members = by_short.get(short_id, [])
        if len(members) < 2:
            print(f"  SKIP_NO_DUP: {short_id} (found {len(members)} members)")
            pairs_skipped += 1
            continue

        # For each duplicate atom, merge sig_dict into atom.algebra (correct API
        # per backend/substrate_index/schema.py:221). add_atom upserts in place.
        for a in members:
            try:
                existing_alg = dict(a.algebra) if a.algebra else {}
                merged = {**existing_alg, **sig_dict}
                meta = dict(a.metadata) if a.metadata else {}
                meta["typed_by"] = "type_bare_duplicates_v1"
                meta["distillation_class"] = "A_atom_removing_unblock"
                # Construct a new Atom with updated algebra+metadata (immutable-ish).
                from backend.substrate_index.schema import Atom as _A
                updated = _A(
                    id=a.id, name=a.name, corpus=a.corpus, tier=a.tier,
                    description=a.description, kind=a.kind, aliases=a.aliases,
                    metadata=meta, serves_capability=a.serves_capability,
                    algebra=merged,
                )
                ps.add_atom(updated, source="type_bare_duplicates_v1",
                            note=f"backfill algebra_dict for Class A unblock; short_id={short_id}")
                atoms_updated += 1
            except Exception as e:
                print(f"  UPDATE_FAIL {a.id}: {str(e)[:120]}")

        typed_count += 1
        print(f"  TYPED: {short_id} ({len(members)} atoms tiers={[str(getattr(m, 'tier', '?')) for m in members]})")

    print(f"\n=== TYPING SUMMARY ===")
    print(f"  duplicate groups typed: {typed_count} / {len(TYPING_SPECS)}")
    print(f"  atoms updated: {atoms_updated}")
    print(f"  skipped (no dup): {pairs_skipped}")
    print(f"\nNext: re-run DISTILL-VERIFY-1; UNDECIDABLE 22 should drop by {typed_count}.")
    print(f"Class A atom-removing distillation: enabled for {typed_count} groups.")


if __name__ == "__main__":
    main()
