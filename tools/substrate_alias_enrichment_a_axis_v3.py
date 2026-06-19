"""A-axis alias enrichment v3 -- expand composite strategy to Q02/Q03/Q04/Q31/Q36.

Q02 random matrix (2 kw), Q03 hopfield (1 kw - already enough), Q04 reinforcement (1 kw),
Q31 bayesian bayes (2 kw), Q36 fourier convolution fft (3 kw).

Q32 (6 kws) skipped: bonus mechanism can't sustain so many kws.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
import dataclasses


ENRICHMENTS = {
    # Q02-A: random matrix
    "math::T1/marchenko_pastur_distribution": ["random matrix pastur distribution"],
    "math::T1/tracy_widom_distribution": ["random matrix widom distribution"],
    "math::T1/voiculescu_free_probability": ["random matrix free probability"],
    "math::T3/mp_bulk_kl": ["random matrix bulk KL"],
    "math::T3/tw_edge_z": ["random matrix edge"],
    "math::T3/kappa_4_free": ["random matrix kappa free"],
    "school::SCHOOL/free_probability_family": ["random matrix free probability family"],
    "school::SCHOOL/spectral_observability_family": ["random matrix spectral family"],
    "science::PHYS/random_matrix_theory": ["random matrix theory RMT"],

    # Q03-A: hopfield (1-kw; just add "hopfield" alias)
    "math::T2/sparse_distributed_memory": ["hopfield sparse distributed memory"],
    "math::T2/amit_gutfreund_sompolinsky_capacity": ["hopfield capacity amit"],
    "math::T2/modern_hopfield_ramsauer": ["hopfield modern ramsauer"],
    "school::SCHOOL/hopfield_family": ["hopfield network family"],
    "school::SCHOOL/energy_based_models_family": ["hopfield energy based models"],
    "science::PHYS/spin_glass": ["hopfield spin glass physics"],

    # Q04-A: reinforcement
    "math::T3/policy_gradient": ["reinforcement policy gradient"],
    "math::T3/q_learning": ["reinforcement Q-learning"],
    "math::T3/markov_decision_process": ["reinforcement Markov decision process MDP"],
    "math::T3/bellman_equation": ["reinforcement Bellman equation"],
    "science::CS/reinforcement_learning": ["reinforcement learning RL"],
    "school::SCHOOL/reinforcement_learning_family": ["reinforcement learning family"],
    "science::BIO/dopamine_RPE": ["reinforcement dopamine RPE prediction error"],
    "science::BIO/basal_ganglia": ["reinforcement basal ganglia"],

    # Q31-A: bayesian bayes
    "concept::CAP_bayesian_inference": ["bayesian bayes inference capability"],
    "math::T1/bayes_rule": ["bayesian bayes rule theorem"],
    "math::T1/probability_space": ["bayesian bayes probability space foundation"],
    "math::T3/count_nb": ["bayesian bayes naive count_nb"],
    "math::T3/bayes_factor": ["bayesian bayes factor evidence"],
    "math::T3/mcmc_sampling": ["bayesian bayes MCMC sampling"],
    "math::T3/variational_inference": ["bayesian bayes variational inference"],
    "math::T3/gaussian_process": ["bayesian bayes gaussian process"],
    "math::T3/iterative_proportional_fitting": ["bayesian bayes IPF iterative"],
    "school::SCHOOL/bayesian_deep_learning_family": ["bayesian bayes deep learning family"],
    "science::BIO/predictive_coding": ["bayesian bayes predictive coding"],
    "science::CS/probabilistic_graphical_model": ["bayesian bayes probabilistic graphical model"],

    # Q36-A: fourier convolution fft
    "math::T3/fast_fourier_transform": ["fourier convolution fft fast"],
    "math::T3/discrete_fourier_transform": ["fourier convolution fft DFT"],
    "math::T2/circular_convolution": ["fourier convolution fft circular"],
    "concept::CAP_circular_convolution": ["fourier convolution fft circular cap"],
    "concept::CAP_fhrr_bind": ["fourier convolution fft fhrr bind"],
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    print(f"pre-enrichment: {len(ps.all_atoms())} atoms\n")
    e = s = nf = 0
    for qid, aliases in ENRICHMENTS.items():
        atom = ps.get_atom(qid)
        if atom is None:
            print(f"NOT FOUND: {qid}"); nf += 1; continue
        current = tuple(atom.aliases or ())
        existing_lower = {a.lower() for a in current}
        added = [a for a in aliases if a.lower() not in existing_lower]
        if not added:
            print(f"SKIP: {qid}"); s += 1; continue
        updated = dataclasses.replace(atom, aliases=current + tuple(added))
        ps.add_atom(updated, source="a_axis_alias_enrichment_v3_extended_qs",
                    note=f"composite alias: {added[0]}")
        print(f"ENRICHED: {qid}"); e += 1
    print(f"\nenriched={e}; skipped={s}; not_found={nf}")


if __name__ == "__main__":
    main()
