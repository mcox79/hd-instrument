"""Run Layer 3 algebra-cluster archaeology + EQUIVALENT_UNDER discovery.

Per deep-self-eval program priority 3 + extension to Layer 4
(empirical-theoretical dialectic): substrate proposes mis-tag candidates
and cross-domain equivalence candidates from its own structure.

Output: JSON + markdown report ready to file as findings #6.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.algebra_cluster import (
    archaeology,
    discover_equivalence_candidates,
)
from backend.substrate_index.algebra_index import AlgebraIndex
from backend.substrate_index.encode import AtomEncoder
from backend.substrate_index.partition import PartitionedStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("layer3_run")

DATA_ROOT = Path("data/substrate_index")


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("loading encoder...")
    encoder = AtomEncoder()
    atoms = pstore.all_atoms()
    av_dict = encoder.encode_atoms(atoms)
    semantic_vectors = {a.qualified_id: av_dict[a.id].semantic for a in atoms}
    log.info("encoded %d atoms", len(atoms))

    log.info("building algebra_index...")
    aidx = AlgebraIndex(dim=1024)
    n_encoded = aidx.build(pstore)
    log.info("algebra_index: %d atoms with algebra_hrr", n_encoded)

    log.info("running Layer 3 archaeology...")
    report = archaeology(pstore, aidx, distance_threshold=0.3)
    log.info("archaeology: %d algebra clusters, %d signature clusters, %d mistag candidates",
             len(report.algebra_clusters), len(report.signature_clusters),
             len(report.mistag_candidates))

    log.info("running EQUIVALENT_UNDER discovery...")
    eq_candidates = discover_equivalence_candidates(
        pstore, aidx, semantic_vectors,
        algebra_threshold=0.5,
        semantic_threshold=0.5,
        min_divergence=0.15,
        top_k=20,
    )
    log.info("discovered %d EQUIVALENT_UNDER candidate pairs", len(eq_candidates))

    # ============================================================
    # Print summary + persist
    # ============================================================
    print("\n" + "=" * 80)
    print("Layer 3: algebra-cluster archaeology + EQUIVALENT_UNDER discovery")
    print("=" * 80)
    print(f"\nAtoms with algebra_hrr: {report.n_atoms_clustered}")
    print(f"Algebra clusters (distance_threshold=0.3): {len(report.algebra_clusters)}")
    for cid, cluster in enumerate(report.algebra_clusters[:10]):
        if len(cluster) >= 2:
            short = [c.split("::")[-1] for c in cluster]
            print(f"  cluster {cid} (n={len(cluster)}): {short[:6]}{'...' if len(cluster) > 6 else ''}")

    print(f"\nMistag candidates: {len(report.mistag_candidates)}")
    for cand in report.mistag_candidates[:10]:
        print(f"  {cand.atom_id.split('::')[-1]:30s}"
              f" declared: {[d.split('::')[-1] for d in cand.declared_family_tags]}"
              f" -> suggested: {cand.inferred_family_candidate.split('::')[-1] if cand.inferred_family_candidate else None}"
              f" (conf {cand.confidence})")

    print(f"\nEQUIVALENT_UNDER candidate pairs (algebra similar + semantic divergent):")
    print(f"{'algebra_sim':>11s} {'semantic_sim':>13s} {'divergence':>10s}  existing_rel  pair")
    print("-" * 100)
    for c in eq_candidates[:15]:
        a_short = c.atom_a.split("::")[-1]
        b_short = c.atom_b.split("::")[-1]
        rel = c.existing_relation or "-"
        print(f"  {c.algebra_sim:9.3f} {c.semantic_sim:13.3f} {c.divergence:10.3f}  {rel:12s} {a_short} <-> {b_short}")

    # Persist JSON
    out_json = DATA_ROOT / "bench_reports" / f"layer3_run_{int(time.time())}.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps({
        "archaeology": report.to_dict(),
        "equivalence_candidates": [c.to_dict() for c in eq_candidates],
    }, indent=2), encoding="utf-8")
    log.info("wrote layer3 report -> %s", out_json)


if __name__ == "__main__":
    main()
