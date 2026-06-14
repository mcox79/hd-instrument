"""Generate a small deterministic synthetic science facts.jsonl for DECISION 43a pipeline PLUMBING validation (real corpora dirs are empty; this proves the mapper->merge->adapter chain on the never-exercised word-mode path; NO substrate ingest). Format: {"fact": "Title\\tSentence"} (wikipedia parser). Each sentence contains a WORD_VOCAB_SCIENCE term so the word-vocab filter retains it."""
import json
from pathlib import Path

# (title, sentence) pairs; each sentence carries a math/science vocab term recognized by the mapper word-vocab.
FACTS = [
    ("Vector space", "A vector space is a set closed under addition and scalar multiplication."),
    ("Inner product", "An inner product induces a norm on a hilbert_space."),
    ("Gradient descent", "Gradient descent minimizes a convex function by following the gradient."),
    ("Markov chain", "A markov_chain is a memoryless stochastic process over states."),
    ("Eigenvalue", "An eigenvalue scales its eigenvector under a linear map; see eigendecomposition."),
    ("Fourier transform", "The fourier_transform decomposes a signal into frequency components."),
    ("KL divergence", "The kl_divergence measures dissimilarity between two probability distributions."),
    ("Mutual information", "Mutual_information quantifies shared information between random variables."),
    ("Manifold", "A manifold locally resembles euclidean space; differential geometry studies it."),
    ("Topology", "Topology studies properties preserved under continuous deformation."),
    ("Banach space", "A banach_space is a complete normed vector_space."),
    ("Convex optimization", "Convex_optimization solves problems where the objective is a convex function."),
    ("Lebesgue measure", "The lebesgue_measure generalizes length to measurable sets in measure theory."),
    ("Martingale", "A martingale is a fair-game stochastic process; related to brownian_motion."),
    ("Laplacian matrix", "The laplacian_matrix encodes graph connectivity; see cheeger_inequality."),
    ("Newton method", "The newton_method finds roots using derivative information."),
    ("Theorem", "A theorem is a statement proven from axioms via a proof."),
    ("Lemma", "A lemma is an auxiliary theorem used to prove a larger result."),
    ("Homomorphism", "A homomorphism is a structure-preserving map between two algebraic structures like a ring."),
    ("Functor", "A functor maps objects and morphisms between categories in category theory."),
    ("Shannon entropy", "Shannon_entropy measures the average uncertainty of a random variable."),
    ("Central limit theorem", "The central_limit_theorem states normalized sums converge to a normal distribution."),
    ("SVD", "The SVD factorizes a matrix into orthogonal and diagonal factors."),
    ("Viterbi algorithm", "The viterbi_algorithm finds the most likely state sequence via dynamic_programming."),
    ("EM algorithm", "The em_algorithm alternates expectation and maximization for latent variable models."),
    ("Kalman filter", "The kalman_filter estimates state of a linear dynamical system under gaussian noise."),
    ("Neuron", "A neuron transmits signals across a synapse to other neurons."),
    ("Protein", "A protein is a chain of amino acids folded into a functional structure."),
    ("Quantum mechanics", "Quantum_mechanics describes systems via a wave function and operators."),
    ("Thermodynamics", "Thermodynamics relates heat, work, and entropy in physical systems."),
    ("Belief propagation", "Belief_propagation performs inference on graphical models via message passing."),
    ("Variational inference", "Variational_inference approximates posteriors by optimizing a lower bound."),
    ("Metric space", "A metric_space equips a set with a distance function satisfying the triangle inequality."),
    ("Group", "A group is a set with an associative operation, identity, and inverses; see ring and field."),
    ("Isomorphism", "An isomorphism is an invertible homomorphism between structures."),
    ("Radon Nikodym", "The radon_nikodym theorem gives a density between two measures."),
    ("Hessian", "The hessian is the matrix of second derivatives of a scalar function."),
    ("Jacobian", "The jacobian is the matrix of first-order partial derivatives of a vector function."),
    ("Brownian motion", "Brownian_motion is a continuous-time martingale with independent increments."),
    ("Spectral decomposition", "Spectral decomposition expresses a matrix via its eigenvalue spectrum."),
]


def main():
    out = Path("data/substrate_state/synth_science_facts.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for title, sent in FACTS:
            f.write(json.dumps({"fact": title + "\t" + sent}) + "\n")
    print("wrote %d synthetic facts -> %s" % (len(FACTS), out))


if __name__ == "__main__":
    main()
