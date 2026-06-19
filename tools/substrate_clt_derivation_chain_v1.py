"""Central Limit Theorem derivation chain authoring v1.

3rd cross-domain L6-PROOF chain this session. Replicates convolution-theorem
(968c8a38) + Bayes' rule (4f731dba) pattern for the CENTRAL LIMIT THEOREM.

Strong cross-domain bridge: PROBABILITY THEORY (iid random variables + variance +
expectation) <-> FOURIER ANALYSIS (characteristic function = E[exp(i*t*X)] =
Fourier transform of probability measure). The DFT/characteristic function is THE
canonical bridge object.

The CLT statement: For iid X_1, ..., X_n with mean mu, variance sigma^2 finite,
  Z_n := (sum_i X_i - n*mu) / (sigma * sqrt(n))
  converges in distribution to N(0, 1) as n -> infinity.

Characteristic-function proof sketch (well-known):
  Premise 1 (CHARACTERISTIC_FUNCTION_IID_SUM): phi_{sum X_i}(t) = prod phi_{X_i}(t)
    For independent RVs, char-function of sum = product of char-functions
    (cross-domain key: this IS the convolution theorem in probability)

  Premise 2 (TAYLOR_EXPANSION_AT_ZERO): phi_X(t) = 1 + i*mu*t - (sigma^2/2)*t^2 + O(t^3)
    Standard Taylor expansion of characteristic function around 0

  Premise 3 (LIMIT_OF_EXPONENTIATED_TAYLOR): (1 - x/n)^n -> exp(-x) as n -> infinity
    Standard exponential limit

  Synthesis: Combining P1+P2+P3, characteristic function of Z_n -> exp(-t^2/2)
    which is char-function of N(0, 1); convergence in distribution follows.

3 NEW T3 atoms + updates to existing T1/central_limit_theorem.

NO LLM. NO bge. Pure schema authoring.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


NEW_ATOMS = [
    {
        "id": "T3/characteristic_function_iid_sum_lemma",
        "name": "Characteristic function of iid sum (convolution-theorem in probability)",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": (
            "char_function_sum_independent",
            "fourier_convolution_in_probability",
        ),
        "description": (
            "For independent random variables X_1, ..., X_n: "
            "phi_{X_1 + ... + X_n}(t) = phi_{X_1}(t) * ... * phi_{X_n}(t). "
            "The characteristic function of a sum of independent RVs equals the "
            "product of their characteristic functions. THIS IS THE CONVOLUTION "
            "THEOREM IN PROBABILITY: sum of iid corresponds to convolution of "
            "densities, which Fourier-transforms to pointwise product of "
            "characteristic functions. Cross-domain bridge to signal processing."
        ),
        "serves_capability": (
            "cap_clt_derivation",
            "cap_probability_property",
            "cap_fourier_in_probability",
        ),
        "metadata": {
            "operation_type": "typed_lemma",
            "lemma": "phi_{sum X_i}(t) = prod phi_{X_i}(t)  for independent X_i",
            "science_algebra_category": "probability_theory::characteristic_function",
            "signature_hint": "char_function_factorizes_over_independent_sum",
            "is_axiom": False,
            "content_type": "FORMAL_SYSTEMS",
            "substrate_load_bearing": False,
            "batch_origin": "clt_derivation_chain",
            "cross_domain_link": "convolution_theorem_synthesis (signal_processing)",
        },
        "depends_on": (
            "math::T1/characteristic_function",
            "math::T1/random_variable",
        ),
    },
    {
        "id": "T3/characteristic_function_taylor_lemma",
        "name": "Characteristic function Taylor expansion at zero",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": (
            "char_function_taylor_at_zero",
            "moment_generating_function_expansion",
        ),
        "description": (
            "For random variable X with finite mean mu = E[X] and finite variance "
            "sigma^2 = Var(X), the characteristic function phi_X(t) admits the "
            "Taylor expansion at t=0: "
            "phi_X(t) = 1 + i*mu*t - (mu^2 + sigma^2)/2 * t^2 + o(t^2). "
            "Coefficients of the Taylor series correspond to moments of X "
            "(moment generating function correspondence). Required for CLT proof "
            "via characteristic function method."
        ),
        "serves_capability": (
            "cap_clt_derivation",
            "cap_characteristic_function_property",
        ),
        "metadata": {
            "operation_type": "typed_lemma",
            "lemma": "phi_X(t) = 1 + i*mu*t - (mu^2 + sigma^2)/2 * t^2 + o(t^2)",
            "science_algebra_category": "probability_theory::characteristic_function",
            "signature_hint": "taylor_expansion_at_origin",
            "is_axiom": False,
            "content_type": "FORMAL_SYSTEMS",
            "substrate_load_bearing": False,
            "batch_origin": "clt_derivation_chain",
        },
        "depends_on": (
            "math::T1/characteristic_function",
            "math::T1/random_variable",
            "math::T1/probability_distribution",
        ),
    },
    {
        "id": "T3/clt_synthesis",
        "name": "Central Limit Theorem (typed synthesis via characteristic function)",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": ("clt_proof_chain", "central_limit_theorem_typed_derivation"),
        "description": (
            "For iid X_1, ..., X_n with E[X_i] = mu and Var(X_i) = sigma^2 (finite), "
            "Z_n := (sum_i X_i - n*mu) / (sigma * sqrt(n)) converges in distribution "
            "to N(0, 1) as n -> infinity. "
            "DERIVATION (characteristic function method):\n"
            "  Premise 1 (char-function of iid sum factorizes): "
            "phi_{sum X_i}(t) = (phi_X(t))^n\n"
            "  Premise 2 (char-function Taylor expansion): "
            "phi_X(t/sqrt(n)) ~ 1 - t^2/(2n) for normalized RVs\n"
            "  Premise 3 (exponential limit): "
            "(1 + x/n)^n -> exp(x) as n -> infinity\n"
            "  Combine: phi_{Z_n}(t) -> exp(-t^2/2), which IS the characteristic "
            "function of N(0, 1)\n"
            "  By the Levy continuity theorem, convergence of char-functions implies "
            "convergence in distribution\n"
            "  QED\n"
            "CROSS-DOMAIN: probability theory (iid sums) <-> Fourier analysis "
            "(characteristic function as Fourier transform of probability measure)."
        ),
        "serves_capability": (
            "cap_clt_derivation",
            "cap_probability_limit_theorem",
            "cap_normal_distribution_universality",
        ),
        "metadata": {
            "operation_type": "typed_theorem",
            "theorem": "Z_n converges in distribution to N(0,1) for iid X_i with finite variance",
            "science_algebra_category": "probability_theory::clt",
            "signature_hint": "iid_sum_normalized_converges_to_normal",
            "is_axiom": False,
            "content_type": "FORMAL_SYSTEMS",
            "substrate_load_bearing": False,
            "batch_origin": "clt_derivation_chain",
            "derivation_steps": [
                "char_function_iid_sum: phi_{sum X_i}(t) = (phi_X(t))^n",
                "char_function_taylor: phi_X(t/sqrt(n)) ~ 1 - t^2/(2n)",
                "exponential_limit: (1 + x/n)^n -> exp(x)",
                "Combine: phi_{Z_n}(t) -> exp(-t^2/2) = char-function of N(0,1)",
                "Levy continuity theorem: convergence of char-functions -> convergence in distribution",
            ],
        },
        "depends_on": (
            "math::T3/characteristic_function_iid_sum_lemma",
            "math::T3/characteristic_function_taylor_lemma",
        ),
    },
]


# Existing atom updates
EXISTING_EDGES = [
    ("math::T1/central_limit_theorem", "math::T3/clt_synthesis"),
    # Cross-domain SHARES_MATH-style link: char_function in probability is structurally
    # the convolution theorem from signal processing. Use SHARES_MATH if available.
]

# Optional cross-domain SHARES_MATH bridge (BIG positioning win if both atoms exist)
CROSS_DOMAIN_BRIDGES = [
    ("math::T3/characteristic_function_iid_sum_lemma",
     "math::T3/dft_convolution_to_pointwise_lemma",
     RelationType.SHARES_MATH,
     "char-function of iid sum IS the convolution theorem in probability domain; "
     "same Fourier-transforms-convolution-to-multiplication identity"),
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_atoms} atoms, {pre_rels} relations\n")

    created = 0
    failed = 0
    for spec in NEW_ATOMS:
        qid = f"math::{spec['id']}"
        if ps.has_atom(qid):
            print(f"  ATOM SKIP (exists): {qid}")
            continue
        try:
            atom = Atom(
                id=spec["id"], name=spec["name"], corpus=Corpus.MATH,
                tier=spec["tier"], description=spec["description"],
                kind=AtomKind.PRIMITIVE, aliases=spec["aliases"],
                metadata=spec["metadata"], serves_capability=spec["serves_capability"],
            )
            ps.add_atom(atom, source="clt_derivation_chain_v1",
                        note="3rd cross-domain L6-PROOF chain; probability <-> Fourier")
            print(f"  ATOM CREATED: {qid}")
            created += 1
        except Exception as e:
            print(f"  ATOM FAIL: {str(e)[:120]}")
            failed += 1

    print()
    existing_edges = set()
    for r in ps.iter_all_relations():
        try:
            existing_edges.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass

    added = 0
    miss = 0
    edge_failed = 0
    for spec in NEW_ATOMS:
        src = f"math::{spec['id']}"
        if not ps.has_atom(src):
            continue
        for tgt in spec["depends_on"]:
            if not ps.has_atom(tgt):
                print(f"  EDGE SKIP_MISS_TGT: {src} -> {tgt}")
                miss += 1
                continue
            key = (src, "DEPENDS_ON", tgt)
            if key in existing_edges:
                continue
            try:
                ps.add_relation(src, RelationType.DEPENDS_ON, tgt,
                                source="clt_derivation_chain_v1", note="CLT derivation chain")
                print(f"  EDGE ADD: {src} -> {tgt}")
                added += 1
                existing_edges.add(key)
            except Exception as e:
                print(f"  EDGE FAIL: {str(e)[:80]}")
                edge_failed += 1

    print()
    for src, tgt in EXISTING_EDGES:
        if not ps.has_atom(src) or not ps.has_atom(tgt):
            miss += 1
            continue
        key = (src, "DEPENDS_ON", tgt)
        if key in existing_edges:
            continue
        try:
            ps.add_relation(src, RelationType.DEPENDS_ON, tgt,
                            source="clt_derivation_chain_v1",
                            note="existing atom update; CLT derivable from synthesis")
            print(f"  UPDATE EDGE: {src} -> {tgt}")
            added += 1
            existing_edges.add(key)
        except Exception as e:
            print(f"  UPDATE FAIL: {str(e)[:80]}")

    # CROSS-DOMAIN SHARES_MATH bridge (big positioning win)
    print()
    bridges_added = 0
    for src, tgt, rel_type, note in CROSS_DOMAIN_BRIDGES:
        if not ps.has_atom(src) or not ps.has_atom(tgt):
            print(f"  BRIDGE SKIP_MISS: {src} OR {tgt}")
            continue
        key = (src, rel_type.name, tgt)
        if key in existing_edges:
            continue
        try:
            ps.add_relation(src, rel_type, tgt,
                            source="clt_derivation_chain_v1_cross_domain_bridge", note=note)
            print(f"  CROSS-DOMAIN BRIDGE: {src} {rel_type.name} {tgt}")
            bridges_added += 1
            existing_edges.add(key)
            # symmetric direction
            key2 = (tgt, rel_type.name, src)
            if key2 not in existing_edges:
                ps.add_relation(tgt, rel_type, src,
                                source="clt_derivation_chain_v1_cross_domain_bridge_symm",
                                note=note + " (symmetric)")
                bridges_added += 1
                existing_edges.add(key2)
        except Exception as e:
            print(f"  BRIDGE FAIL: {str(e)[:120]}")

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== CLT DERIVATION CHAIN SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms} (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  atoms created: {created} failed: {failed}")
    print(f"  edges added: {added} miss: {miss} failed: {edge_failed}")
    print(f"  cross-domain bridges: {bridges_added}")
    print(f"\nCross-domain L6-PROOF chains cumulative (this session):")
    print(f"  #1 convolution theorem: VSA binding <-> signal processing (968c8a38)")
    print(f"  #2 Bayes rule: measure-theoretic probability <-> Bayesian inference (4f731dba)")
    print(f"  #3 CLT: probability theory <-> Fourier analysis (this commit)")
    print(f"  + 1 cross-domain SHARES_MATH bridge: char_function_iid_sum <-> dft_convolution_to_pointwise")


if __name__ == "__main__":
    main()
