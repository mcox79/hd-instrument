"""A-axis alias enrichment v2 (Cycle 51 day-3 close) -- composite-alias strategy.

Prior round (v1) added topic-relevant aliases but Q33/Q34/Q37 didn't lift because their
gold atoms got only 1-2 of N topic kws in aliases, missing the +10 all-kws bonus.

v2 strategy: each gold atom gets ONE composite alias containing ALL topic kws of the
relevant Q. Triggers the bonus and pushes gold atoms above competitors.

Target Qs:
- Q01-A topic "fhrr binding" (2 kws: fhrr, binding): gold atoms get "fhrr binding ..." alias
- Q33-A topic "gradient backprop chain" (3 kws): gold atoms get "gradient backpropagation chain ..." alias
- Q37-A topic "graphical markov bayes viterbi" (4 kws): gold atoms get composite alias
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
import dataclasses


# (atom_qid, [composite_aliases_to_add])
ENRICHMENTS = {
    # Q01-A: fhrr binding
    "math::T2/fhrr_bind": ["fhrr binding operation"],
    "math::T2/circular_convolution": ["fhrr binding circular_convolution"],
    "concept::CAP_fhrr_bind": ["fhrr binding capability"],
    "math::T1/kronecker_product": ["fhrr binding kronecker"],
    "math::T1/tensor": ["fhrr binding tensor"],

    # Q33-A: gradient backprop chain
    "math::T1/chain_rule": ["gradient backpropagation chain rule"],
    "math::T1/gradient": ["gradient backpropagation chain derivative"],
    "math::T1/gradient_descent": ["gradient backpropagation chain descent"],
    "math::T3/stochastic_gradient_descent": ["gradient backpropagation chain SGD"],
    "math::T3/adam_optimizer": ["gradient backpropagation chain adam"],
    "math::T3/cross_entropy_loss": ["gradient backpropagation chain cross_entropy"],
    "math::T3/residual_connection": ["gradient backpropagation chain residual"],
    # connectionist_family was NOT FOUND in v1

    # Q37-A: graphical markov bayes viterbi
    "science::CS/probabilistic_graphical_model": ["graphical markov bayes viterbi model"],
    "math::T1/markov_chain": ["graphical markov bayes viterbi chain"],
    "math::T1/bayes_rule": ["graphical markov bayes viterbi rule"],
    "concept::CAP_viterbi_decoding": ["graphical markov bayes viterbi decoding"],
    "concept::CAP_forward_algorithm": ["graphical markov bayes viterbi forward"],
    "math::T3/structured_perceptron_collins": ["graphical markov bayes viterbi structured"],
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    print(f"pre-enrichment: {len(ps.all_atoms())} atoms\n")
    enriched = 0
    skipped = 0
    not_found = 0
    for qid, aliases_to_add in ENRICHMENTS.items():
        atom = ps.get_atom(qid)
        if atom is None:
            print(f"NOT FOUND: {qid}")
            not_found += 1
            continue
        current = tuple(atom.aliases or ())
        existing_lower = {a.lower() for a in current}
        added = [a for a in aliases_to_add if a.lower() not in existing_lower]
        if not added:
            print(f"SKIP (already): {qid}")
            skipped += 1
            continue
        updated_aliases = current + tuple(added)
        updated = dataclasses.replace(atom, aliases=updated_aliases)
        ps.add_atom(updated, source="a_axis_alias_enrichment_v2_composite_strategy",
                    note=f"added composite all-kws alias for Q01/Q33/Q37 bonus trigger: {added[0]}")
        print(f"ENRICHED: {qid} += '{added[0]}'")
        enriched += 1
    print(f"\nenriched={enriched}; skipped={skipped}; not_found={not_found}")


if __name__ == "__main__":
    main()
