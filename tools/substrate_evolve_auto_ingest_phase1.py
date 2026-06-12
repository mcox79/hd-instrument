"""evolve.py auto-ingest Phase 1: research_drill_*.md -> research_history partition.

Per Research FINDINGS_15_Q1_Q2_Q3 endorsement: substrate-self-referential pipeline:
1. Substrate composite C classifies each file (NOVEL / TIER-A / etc.)
2. evolve.py reads NOVEL classification + cluster pattern + maps to target partition
3. evolve.py parses file content via substrate-eval mediated path (not regex extraction)
4. evolve.py creates partition-specific atoms with appropriate schema
5. Ingest via Testbed write boundary
6. Path A re-runs; classification of those files SHIFTS from NOVEL to TIER-A/B

Phase 1 = research_drill_*.md only (76 files target; ~research_history partition).

Validates pre-registered Hypothesis 1:
- After ingest, subsequent Path A on those files moves from NOVEL to TIER-A/B
- Expected: <10% NOVEL on drill files post-ingest
- Specifically: TIER-A >= 30% / TIER-B >= 30% / TIER-C <= 30% / NOVEL <= 10%
"""
from __future__ import annotations

import hashlib
import json
import logging
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.algebra_index import AlgebraIndex
from backend.substrate_index.encode import AtomEncoder
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.retrieve import Retriever
from backend.substrate_index.schema import Atom, AtomKind, Corpus, RelationType, Tier

# Reuse substrate-eval v2 composite C logic
from tools.substrate_eval_ingest_v2_composite import (
    _math_atoms_referenced_by_text,
    _algebra_novelty_of_atoms,
    _paragraph_coherence,
    classify_verdict,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("evolve_phase1")

NOTES_DIR = Path("notes")
DATA_ROOT = Path("data/substrate_index")


def file_to_research_history_atom(
    file_path: Path,
    encoder: AtomEncoder,
    retriever: Retriever,
    aidx: AlgebraIndex,
    pstore: PartitionedStore,
) -> Atom:
    """Substrate-eval mediated atom creation (NOT regex extraction).

    Atom's structural information comes from substrate's classification:
    - semantic_vec via bge.encode (substrate's encoder)
    - nearest neighbors via retriever.semantic
    - math atom references via name-match
    - algebra_novelty via HRR cluster spread of referenced math atoms
    - classification verdict via composite C

    NO regex extraction of headers / TL;DR / cross-refs. The substrate
    classifies; we record.
    """
    text = file_path.read_text(encoding="utf-8", errors="replace")
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    file_id = file_path.stem

    # Substrate's classification
    candidates = retriever.semantic(text, top_k=10)
    top5_ids = tuple(c.atom_id for c in candidates[:5])
    top5_scores = tuple(c.score for c in candidates[:5])
    avg_top3 = float(sum(c.score for c in candidates[:3]) / 3) if len(candidates) >= 3 else 0.0
    semantic_novelty = 1.0 - avg_top3

    # Algebra novelty from name-matched math atoms
    referenced_math = _math_atoms_referenced_by_text(text, pstore)
    algebra_nov, n_math = _algebra_novelty_of_atoms(referenced_math, aidx)
    composite_novelty = 0.6 * semantic_novelty + 0.4 * algebra_nov  # Option E

    coherence = _paragraph_coherence(text, encoder)
    verdict, reasoning = classify_verdict(composite_novelty, coherence, n_math_referenced=n_math)

    # First line as name (minimal extraction; just first markdown header line)
    name = file_id
    for line in text.splitlines()[:10]:
        line = line.strip()
        if line.startswith("# "):
            name = line[2:].strip()[:200]
            break

    description = text[:600].strip()

    return Atom(
        id=file_id,
        name=name,
        corpus=Corpus.RESEARCH_HISTORY,
        tier=Tier.TIER_NA,
        kind=AtomKind.PRIMITIVE,
        description=description,
        metadata={
            "phase1_research_drill_ingest": True,
            "content_hash": content_hash,
            "file_size_bytes": len(text),
            "file_mtime": file_path.stat().st_mtime,
            "substrate_eval_verdict": verdict,
            "substrate_eval_verdict_reason": reasoning,
            "semantic_novelty": round(semantic_novelty, 4),
            "algebra_novelty": round(algebra_nov, 4),
            "composite_novelty": round(composite_novelty, 4),
            "coherence_score": round(coherence, 4),
            "nearest_atom_ids": list(top5_ids),
            "nearest_atom_scores": [round(s, 3) for s in top5_scores],
            "referenced_math_atom_ids": referenced_math[:20],  # cap
            "n_math_atoms_referenced": n_math,
            "provenance": {
                "source_file": str(file_path),
                "content_hash": content_hash,
                "ingest_pipeline": "evolve_auto_ingest_phase1_research_drill",
                "classifier": "substrate_eval_v2_composite_C",
                "ingest_date": time.strftime("%Y-%m-%d"),
            },
        },
    )


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("pre-ingest atoms: %d (research_history: %d)",
             len(pstore.all_atoms()),
             pstore.stats()["partitions"].get("research_history", {}).get("n_atoms", 0))

    log.info("loading encoder + retriever + algebra_index...")
    encoder = AtomEncoder()
    retriever = Retriever(pstore, encoder)
    retriever.rebuild_index()
    aidx = AlgebraIndex(dim=1024)
    aidx.build(pstore)

    # Find all research_drill files
    drill_files = sorted(NOTES_DIR.glob("research_drill_*.md"))
    log.info("Phase 1 target: %d research_drill files", len(drill_files))

    pre_verdicts_counter: Counter = Counter()
    ingested = 0
    skipped = 0
    relations_added = 0

    for i, fp in enumerate(drill_files):
        if i % 10 == 0:
            log.info("  progress: %d/%d", i, len(drill_files))
        try:
            atom = file_to_research_history_atom(fp, encoder, retriever, aidx, pstore)
        except Exception as e:
            log.error("eval failed %s: %s", fp.name, e)
            continue
        pre_verdicts_counter[atom.metadata["substrate_eval_verdict"]] += 1

        if pstore.has_atom(atom.qualified_id):
            skipped += 1
            continue
        try:
            pstore.add_atom(atom, source="evolve_auto_ingest_phase1",
                            note="research_history partition auto-ingest via substrate-eval mediated pipeline")
            ingested += 1
        except Exception as e:
            log.error("add failed %s: %s", atom.qualified_id, e)
            continue
        # Wire DEPENDS_ON to referenced math atoms (typed-edge connection)
        for tgt in atom.metadata.get("referenced_math_atom_ids", []):
            try:
                pstore.add_relation(atom.qualified_id, RelationType.DEPENDS_ON, tgt,
                                    source="evolve_phase1_math_ref",
                                    note="referenced by drill content")
                relations_added += 1
            except Exception:
                pass

    print("\n" + "=" * 80)
    print("EVOLVE.PY AUTO-INGEST PHASE 1: research_drill_*.md -> research_history")
    print("=" * 80)
    print(f"\nPre-ingest substrate-eval verdict distribution on {len(drill_files)} drill files:")
    for cls in ("TIER-A", "TIER-B", "TIER-C", "OUT_OF_DOMAIN", "NOVEL", "REJECT"):
        n = pre_verdicts_counter.get(cls, 0)
        pct = 100 * n / max(1, len(drill_files))
        print(f"  {cls:15s}  {n:3d}  ({pct:5.1f}%)")

    stats = pstore.stats()
    print(f"\nIngest result:")
    print(f"  drill files atom-created: {ingested}")
    print(f"  skipped (already present): {skipped}")
    print(f"  DEPENDS_ON edges added: {relations_added}")
    print(f"  research_history partition atoms: {stats['partitions'].get('research_history', {}).get('n_atoms', 0)}")
    print(f"  total atoms: {stats['total_atoms']}")
    print(f"  total relations: {stats['total_relations']}")

    out = DATA_ROOT / "bench_reports" / f"evolve_phase1_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "phase": "1_research_drill",
        "n_files": len(drill_files),
        "pre_verdicts": dict(pre_verdicts_counter),
        "ingested": ingested,
        "skipped": skipped,
        "relations_added": relations_added,
        "post_research_history_atoms": stats["partitions"].get("research_history", {}).get("n_atoms", 0),
        "post_total_atoms": stats["total_atoms"],
    }, indent=2), encoding="utf-8")
    log.info("wrote phase1 report -> %s", out)


if __name__ == "__main__":
    main()
