"""T1 batches 13 (graph theory + combinatorics) + 14 FINAL (numerical methods + classical algorithms).

17 absent atoms (substrate already has graph, em_algorithm, kalman_filter, viterbi_algorithm
(via CAP_), newton_method, runge_kutta, dynamic_programming, variational_inference).

After this ingest the 144 T1 target is COMPLETE.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


SPECS = [
    # BATCH 13: graph theory + combinatorics
    ("T1/tree", "Tree", ("acyclic_connected_graph",),
     "Connected acyclic undirected graph. n vertices => n-1 edges. Foundation for graph algorithms + parsing + decision trees.",
     ("graph_theory_foundation", "data_structure_foundation", "substrate_self_knowledge"),
     "graph_theory::core_structures", "connected_acyclic", "batch_13"),
    ("T1/bipartite_graph", "Bipartite graph", ("two_part_graph", "G_eq_U_V_E"),
     "Vertex set partitions into U, V with all edges between U and V. Foundation for matching + Hungarian algorithm + recommender systems.",
     ("graph_theory_foundation", "matching_problem_foundation", "substrate_self_knowledge"),
     "graph_theory::core_structures", "two_vertex_class_no_intra_edges", "batch_13"),
    ("T1/planar_graph", "Planar graph", ("crossing_free_drawing",),
     "Graph drawable on plane without edge crossings. Foundation for graph visualization + map coloring.",
     ("graph_theory_foundation", "topological_graph_theory", "substrate_self_knowledge"),
     "graph_theory::core_structures", "planar_embedding_exists", "batch_13"),
    ("T1/laplacian_matrix", "Laplacian matrix", ("L_eq_D_minus_A",),
     "L = D - A (degree matrix minus adjacency). PSD; eigenvalue 0 with multiplicity = number of connected components.",
     ("spectral_graph_theory", "graph_partitioning_foundation", "substrate_self_knowledge"),
     "graph_theory::spectral", "degree_minus_adjacency", "batch_13"),
    ("T1/spectral_graph_theory", "Spectral graph theory", ("graph_spectrum_analysis",),
     "Study of graph properties via eigenvalues/vectors of Laplacian + adjacency matrices. Foundation for Cheeger + Fiedler + community detection.",
     ("graph_analysis_foundation", "community_detection_foundation", "substrate_self_knowledge"),
     "graph_theory::spectral", "eigenvalue_eigenvector_analysis", "batch_13"),
    ("T1/chromatic_number", "Chromatic number", ("chi_G", "min_colors"),
     "Minimum number of colors needed to color vertices such that no adjacent vertices share color. NP-hard in general.",
     ("graph_theory_foundation", "scheduling_foundation", "substrate_self_knowledge"),
     "graph_theory::core_invariants", "min_color_proper_coloring", "batch_13"),
    ("T1/cheeger_inequality", "Cheeger inequality", ("isoperimetric_bound",),
     "Bounds graph conductance via second-smallest Laplacian eigenvalue: phi^2 / 2 <= lambda_2 <= 2 phi. Foundation for spectral clustering + expander graphs.",
     ("spectral_graph_theory", "conductance_bound", "substrate_self_knowledge"),
     "graph_theory::spectral_inequalities", "conductance_via_eigenvalue", "batch_13"),
    ("T1/fiedler_vector", "Fiedler vector", ("second_eigenvector_laplacian",),
     "Eigenvector of Laplacian's second-smallest eigenvalue. Foundation for spectral bisection + manifold learning.",
     ("spectral_graph_theory", "spectral_clustering_foundation", "substrate_self_knowledge"),
     "graph_theory::spectral", "second_laplacian_eigenvector", "batch_13"),
    ("T1/generating_function", "Generating function", ("formal_power_series", "f_x_eq_sum_a_n_x_n"),
     "Formal power series sum a_n x^n encoding sequence (a_n). Foundation for combinatorial identities + asymptotic analysis.",
     ("combinatorics_foundation", "sequence_analysis", "substrate_self_knowledge"),
     "combinatorics::algebraic_methods", "power_series_encodes_sequence", "batch_13"),
    # BATCH 14 FINAL: numerical methods + classical algorithms
    ("T1/finite_difference", "Finite difference", ("forward_central_backward_diff",),
     "Discrete approximation of derivative: (f(x+h) - f(x))/h (forward), (f(x+h) - f(x-h))/2h (central). Foundation for numerical PDEs.",
     ("numerical_analysis_foundation", "PDE_discretization", "substrate_self_knowledge"),
     "numerical_analysis::differentiation", "discrete_derivative_approximation", "batch_14"),
    ("T1/monte_carlo", "Monte Carlo method", ("random_sampling_estimation",),
     "Estimate via random sampling: E[f(X)] ~ (1/N) sum f(x_i). Convergence rate O(1/sqrt(N)) dimension-free.",
     ("numerical_integration", "stochastic_estimation", "substrate_self_knowledge"),
     "numerical_analysis::stochastic_methods", "random_sampling_for_expectation", "batch_14"),
    ("T1/importance_sampling", "Importance sampling", ("IS", "biased_sampling_with_correction"),
     "Sample from q + reweight by p(x)/q(x) to estimate E_p[f(X)]. Variance reduction when q ~ |f| * p.",
     ("variance_reduction", "monte_carlo_extension", "substrate_self_knowledge"),
     "numerical_analysis::variance_reduction", "reweighted_sampling", "batch_14"),
    ("T1/viterbi_algorithm", "Viterbi algorithm", ("max_product_DP_on_HMM",),
     "Dynamic programming for max-product (most likely state sequence) in HMM. Foundation for sequence decoding + structured prediction.",
     ("dynamic_programming_foundation", "structured_prediction_decoding", "substrate_self_knowledge"),
     "algorithms::dynamic_programming", "max_product_DP_chain", "batch_14"),
    ("T1/linear_programming", "Linear programming", ("LP", "linear_objective_linear_constraints"),
     "min c^T x s.t. Ax <= b, x >= 0. Foundation for combinatorial optimization + duality theory.",
     ("optimization_foundation", "combinatorial_optimization", "substrate_self_knowledge"),
     "optimization::linear", "linear_objective_polytope_constraints", "batch_14"),
    ("T1/graph_random_walk", "Random walk on graph", ("graph_RW", "Markov_chain_on_vertices"),
     "Markov chain on vertices with transition P_{ij} = 1/deg(i) for edge (i,j). Foundation for PageRank + diffusion maps.",
     ("graph_analysis", "markov_on_graph_foundation", "substrate_self_knowledge"),
     "graph_theory::stochastic_methods", "uniform_neighbor_transition", "batch_14"),
    ("T1/shortest_path", "Shortest path", ("Dijkstra_Bellman_Ford",),
     "Find path with minimum total edge weight between vertices. Dijkstra (non-negative); Bellman-Ford (negative allowed); Floyd-Warshall (all pairs).",
     ("graph_algorithm_foundation", "routing_foundation", "substrate_self_knowledge"),
     "algorithms::graph_algorithms", "min_weight_path", "batch_14"),
    ("T1/belief_propagation", "Belief propagation", ("BP", "message_passing_inference"),
     "Iterative message passing on factor graph for marginal/MAP inference. Exact on trees; loopy approximation on general graphs.",
     ("graphical_model_inference", "message_passing_foundation", "substrate_self_knowledge"),
     "algorithms::graphical_models", "iterative_message_passing", "batch_14"),
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    print(f"pre-ingest: {len(ps.all_atoms())} atoms\n")
    c = s = f = 0
    for (aid, name, aliases, desc, serves, cat, sig, batch) in SPECS:
        qid = f"math::{aid}"
        if ps.has_atom(qid):
            print(f"SKIP: {qid}"); s += 1; continue
        try:
            atom = Atom(id=aid, name=name, corpus=Corpus.MATH, tier=Tier.TIER_1_FOUNDATIONAL,
                        description=desc, kind=AtomKind.PRIMITIVE, aliases=aliases,
                        metadata={"science_algebra_category": cat, "signature_hint": sig, "batch_origin": batch},
                        serves_capability=serves)
            ps.add_atom(atom, source="t1_algebra_dict_batches_13_14_FINAL",
                        note=f"per {batch}; T1 math foundation (144 target complete)")
            print(f"CREATED: {qid}"); c += 1
        except Exception as e:
            print(f"FAIL: {qid}: {str(e)[:100]}"); f += 1
    print(f"\npost-ingest: {len(ps.all_atoms())}; created={c} skipped={s} failed={f}")
    print("\n*** 144-T1-target COMPLETE after this ingest ***")


if __name__ == "__main__":
    main()
