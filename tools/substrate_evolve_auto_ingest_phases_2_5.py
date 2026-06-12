"""evolve.py auto-ingest Phases 2-5 generalized.

Per Research FINDINGS_15 5-phase plan over Days 2-4:
- Phase 2: research_to_*.md -> decision_history (~58 files)
- Phase 3: testbed_to_research_*.md + exp_dev_to_research_*.md -> findings_history + verdict_history
- Phase 4: *_POST_COMPACTION_BRIEF_*.md -> meta-state snapshots (no dedicated partition; use research_history+meta marker)
- Phase 5: strategy_decisions_*.md -> results_history

Generalized over (file_glob, target_corpus, source_label).
Same substrate-self-referential pipeline as Phase 1.
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
from tools.substrate_eval_ingest_v2_composite import (
    _math_atoms_referenced_by_text,
    _algebra_novelty_of_atoms,
    _paragraph_coherence,
    classify_verdict,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("evolve_phases_2_5")

NOTES_DIR = Path("notes")
DATA_ROOT = Path("data/substrate_index")


# Phase definitions
PHASES = [
    {"phase": 2, "glob": "research_to_*.md", "corpus": Corpus.DECISION_HISTORY,
     "source": "evolve_phase2_routing_decisions"},
    {"phase": 3, "glob": "testbed_to_research_*.md", "corpus": Corpus.FINDINGS_HISTORY,
     "source": "evolve_phase3_findings"},
    {"phase": 3, "glob": "exp_dev_to_research_*.md", "corpus": Corpus.VERDICT_HISTORY,
     "source": "evolve_phase3_verdicts"},
    {"phase": 5, "glob": "strategy_decisions_*.md", "corpus": Corpus.RESULTS_HISTORY,
     "source": "evolve_phase5_strategy"},
]


def file_to_history_atom(
    file_path: Path,
    target_corpus: Corpus,
    source_label: str,
    encoder: AtomEncoder,
    retriever: Retriever,
    aidx: AlgebraIndex,
    pstore: PartitionedStore,
) -> Atom:
    text = file_path.read_text(encoding="utf-8", errors="replace")
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    file_id = file_path.stem

    candidates = retriever.semantic(text, top_k=10)
    top5_ids = tuple(c.atom_id for c in candidates[:5])
    top5_scores = tuple(c.score for c in candidates[:5])
    avg_top3 = float(sum(c.score for c in candidates[:3]) / 3) if len(candidates) >= 3 else 0.0
    semantic_novelty = 1.0 - avg_top3

    referenced_math = _math_atoms_referenced_by_text(text, pstore)
    algebra_nov, n_math = _algebra_novelty_of_atoms(referenced_math, aidx)
    composite_novelty = 0.6 * semantic_novelty + 0.4 * algebra_nov  # Option E
    coherence = _paragraph_coherence(text, encoder)
    verdict, reasoning = classify_verdict(composite_novelty, coherence, n_math_referenced=n_math)

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
        corpus=target_corpus,
        tier=Tier.TIER_NA,
        kind=AtomKind.PRIMITIVE,
        description=description,
        metadata={
            "auto_ingest_phase": source_label,
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
            "referenced_math_atom_ids": referenced_math[:20],
            "n_math_atoms_referenced": n_math,
            "provenance": {
                "source_file": str(file_path),
                "content_hash": content_hash,
                "ingest_pipeline": source_label,
                "classifier": "substrate_eval_v2_composite_C",
                "ingest_date": time.strftime("%Y-%m-%d"),
            },
        },
    )


def run_phase(phase_idx: int, pstore: PartitionedStore, encoder: AtomEncoder,
              retriever: Retriever, aidx: AlgebraIndex) -> dict:
    cfg = PHASES[phase_idx]
    files = sorted(NOTES_DIR.glob(cfg["glob"]))
    log.info("Phase %d (%s): %d files", cfg["phase"], cfg["glob"], len(files))
    pre_verdicts: Counter = Counter()
    ingested = skipped = relations_added = 0
    for i, fp in enumerate(files):
        if i % 15 == 0:
            log.info("  progress: %d/%d", i, len(files))
        try:
            atom = file_to_history_atom(
                fp, cfg["corpus"], cfg["source"],
                encoder, retriever, aidx, pstore,
            )
        except Exception as e:
            log.error("eval failed %s: %s", fp.name, e)
            continue
        pre_verdicts[atom.metadata["substrate_eval_verdict"]] += 1
        if pstore.has_atom(atom.qualified_id):
            skipped += 1
            continue
        try:
            pstore.add_atom(atom, source=cfg["source"],
                            note=f"Phase {cfg['phase']} auto-ingest")
            ingested += 1
        except Exception as e:
            log.error("add failed %s: %s", atom.qualified_id, e)
            continue
        for tgt in atom.metadata.get("referenced_math_atom_ids", []):
            try:
                pstore.add_relation(atom.qualified_id, RelationType.DEPENDS_ON, tgt,
                                    source=f"{cfg['source']}_math_ref")
                relations_added += 1
            except Exception:
                pass
    return {
        "phase": cfg["phase"],
        "glob": cfg["glob"],
        "target_corpus": cfg["corpus"].value,
        "n_files": len(files),
        "pre_verdicts": dict(pre_verdicts),
        "ingested": ingested,
        "skipped": skipped,
        "relations_added": relations_added,
    }


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("pre-ingest: %d atoms", len(pstore.all_atoms()))
    log.info("loading encoder + retriever + algebra_index...")
    encoder = AtomEncoder()
    retriever = Retriever(pstore, encoder)
    retriever.rebuild_index()
    aidx = AlgebraIndex(dim=1024)
    aidx.build(pstore)

    all_results = []
    for i in range(len(PHASES)):
        result = run_phase(i, pstore, encoder, retriever, aidx)
        all_results.append(result)
        log.info("Phase %d complete: ingested=%d skipped=%d relations=%d",
                 result["phase"], result["ingested"], result["skipped"], result["relations_added"])

    stats = pstore.stats()
    print("\n" + "=" * 80)
    print("EVOLVE.PY PHASES 2-5 COMPLETE")
    print("=" * 80)
    for r in all_results:
        print(f"\nPhase {r['phase']} ({r['glob']} -> {r['target_corpus']}):")
        print(f"  files: {r['n_files']}, ingested: {r['ingested']}, skipped: {r['skipped']}, relations: {r['relations_added']}")
        print(f"  pre-ingest verdicts: {r['pre_verdicts']}")

    print(f"\nFINAL atoms: {stats['total_atoms']} / relations: {stats['total_relations']}")
    print(f"Per partition:")
    for corpus, p in stats["partitions"].items():
        print(f"  {corpus}: {p['n_atoms']} atoms / {p['n_relations']} relations")

    out = DATA_ROOT / "bench_reports" / f"evolve_phases_2_5_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"phases": all_results, "final_stats": stats}, indent=2),
                   encoding="utf-8")
    log.info("wrote phases 2-5 report -> %s", out)


if __name__ == "__main__":
    main()
