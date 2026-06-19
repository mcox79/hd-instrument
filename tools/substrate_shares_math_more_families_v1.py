"""SHARES_MATH coverage expansion -- 6 more curated families.

Per Research periodic-verification action item #3 (push KP P3 from 8 classes -> 10+
classes -> HARD-PASS). 8 classes is below the HARD-PASS bar; adding 3+ more clean
families crosses it.

6 proposed families (Testbed-curated; mathematical equivalence semantics):
  STRUCTURED_PREDICTION: Viterbi/structured-perceptron/forward-backward/CRF/beam (sequence-decoding family)
  VARIATIONAL_INFERENCE: VI/EM/KL/Jensen (variational-bound family)
  GRAPH_ALGORITHMS: Dijkstra/Bellman-Ford/BFS/DFS/topological-sort/DP (graph-traversal optimization)
  BAYESIAN_INFERENCE: Bayes/conditional-prob/posterior/count-NB/GP (Bayesian-inference)
  ENTROPY_FAMILY: Shannon/KL/cross-entropy/MI/conditional (information-theoretic measures)
  CONVEX_OPTIMIZATION: gradient-descent/Newton/convex/Lagrangian/KKT (convex-optimization)

Local probe found: 3 well-resolved families (STRUCTURED_PREDICTION 6, BAYESIAN 5,
ENTROPY 4). 3 sparse-local (canonical-rich expected). Tolerant of misses per
BATCH 17 pattern.

NO LLM. NO bge. Pure graph authoring; composes with SHARES_MATH RelationType
(commit `7139f66f`).
"""
from __future__ import annotations
import sys
from pathlib import Path
from itertools import combinations
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


FAMILIES = {
    "STRUCTURED_PREDICTION": [
        "T3/discriminative_perceptron",
        "T3/structured_perceptron_collins",
        "T3/viterbi_decoder",
        "T3/forward_algorithm_atom",
        "T3/backward_algorithm_atom",
        "T3/hmm_transition",
        "T3/conditional_random_field",
        "T3/beam_search",
        "T2/structured_perceptron",
        "T2/viterbi",
    ],
    "VARIATIONAL_INFERENCE": [
        "T3/variational_inference",
        "T3/em_algorithm",
        "T1/kl_divergence",
        "T1/jensen_inequality",
        "T2/variational_free_energy",
        "T2/mean_field_approximation",
        "T3/variational_em",
        "T2/elbo",
    ],
    "GRAPH_ALGORITHMS": [
        "T3/dijkstra",
        "T3/bellman_ford",
        "T3/breadth_first_search",
        "T3/depth_first_search",
        "T3/topological_sort",
        "T3/dynamic_programming",
        "T1/dynamic_programming",
        "T3/a_star_search",
        "T3/floyd_warshall",
    ],
    "BAYESIAN_INFERENCE": [
        "T1/bayes_rule",
        "T1/conditional_probability",
        "T3/posterior_distribution",
        "T3/bayesian_inference",
        "T3/count_nb",
        "T3/gaussian_process",
        "T3/bayes_factor",
        "T3/mcmc_sampling",
        "T3/iterative_proportional_fitting",
    ],
    "ENTROPY_FAMILY": [
        "T1/shannon_entropy",
        "T1/kl_divergence",
        "T1/cross_entropy",
        "T1/mutual_information",
        "T1/conditional_entropy",
        "T1/entropy",
        "T1/joint_entropy",
    ],
    "CONVEX_OPTIMIZATION": [
        "T2/gradient_descent",
        "T2/newton_method",
        "T1/convex_function",
        "T1/lagrangian",
        "T2/kkt",
        "T2/convex_optimization",
        "T3/gradient_descent",
        "T2/saddle_point",
    ],
}


def resolve_qid(member: str, ps: PartitionedStore) -> str | None:
    if "::" in member:
        return member if ps.has_atom(member) else None
    for corpus in ("math", "concept", "science", "school", "meta"):
        qid = f"{corpus}::{member}"
        if ps.has_atom(qid):
            return qid
    return None


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest relations: {pre_rels}\n")

    existing = set()
    for r in ps.iter_all_relations():
        try:
            existing.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass

    total_added = 0
    total_miss = 0
    total_dup = 0
    total_fail = 0
    per_family = {}
    families_meeting_min = 0  # >= 3 atoms required for a class to "count" per Exp-Dev convention

    for fam_name, members in FAMILIES.items():
        print(f"=== Family {fam_name} ({len(members)} atoms) ===")
        resolved = []
        for m in members:
            qid = resolve_qid(m, ps)
            if qid:
                resolved.append(qid)
            else:
                total_miss += 1
        print(f"  resolved {len(resolved)}/{len(members)}: {[r.split('::')[-1] for r in resolved]}")
        if len(resolved) >= 3:
            families_meeting_min += 1

        added = 0
        dup = 0
        fail = 0
        for a, b in combinations(resolved, 2):
            for src, tgt in ((a, b), (b, a)):
                key = (src, "SHARES_MATH", tgt)
                if key in existing:
                    dup += 1
                    continue
                try:
                    ps.add_relation(
                        src, RelationType.SHARES_MATH, tgt,
                        source=f"shares_math_more_families_{fam_name.lower()}",
                        note=f"P3 HARD-PASS push; {fam_name} family per Testbed curation",
                    )
                    added += 1
                    existing.add(key)
                except Exception as e:
                    msg = str(e)[:120]
                    if any(k in msg.lower() for k in ("already", "duplicate")):
                        dup += 1
                    else:
                        print(f"  FAIL: {src} -> {tgt}: {msg}")
                        fail += 1
        per_family[fam_name] = {
            "resolved_count": len(resolved),
            "directed_edges_added": added,
            "meets_min_3_for_class": len(resolved) >= 3,
        }
        total_added += added
        total_dup += dup
        total_fail += fail
        print(f"  directed edges added: {added}; dup skipped: {dup}\n")

    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"=== MORE SHARES_MATH FAMILIES SUMMARY ===")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  total directed edges added: {total_added}")
    print(f"  total atom-resolve misses: {total_miss}")
    print(f"  total duplicate skipped: {total_dup}")
    print(f"  total failed: {total_fail}")
    print(f"  families >=3-atoms (count as KP P3 class): {families_meeting_min}/6")
    print(f"\nPer-family breakdown:")
    for fam, r in per_family.items():
        marker = "+" if r["meets_min_3_for_class"] else "-"
        print(f"  {marker} {fam}: resolved={r['resolved_count']} edges_added={r['directed_edges_added']}")
    print(f"\nKP P3 trajectory: 8 existing classes + {families_meeting_min} new classes")
    print(f"  -> {8 + families_meeting_min} total (HARD-PASS bar = 10)")
    print(f"  -> {'HARD-PASS PROJECTION' if 8 + families_meeting_min >= 10 else 'MIDDLE STILL'}")


if __name__ == "__main__":
    main()
