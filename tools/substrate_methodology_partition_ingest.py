"""Ingest substrate-proposed methodology_corpus atoms.

Per Research FINDINGS_08_VALIDATE_METHODOLOGY_PARTITION 2026-06-11:
- 4 NOVEL atoms validated as "multi-operation methodological content"
- Add to Corpus.METHODOLOGY partition

Inputs: list of files classified as NOVEL by substrate-eval composite C.
Output: METHODOLOGY-corpus atoms with provenance + reasoning.
"""
from __future__ import annotations

import hashlib
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import (
    Atom,
    AtomKind,
    Corpus,
    Tier,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("methodology_ingest")

DATA_ROOT = Path("data/substrate_index")

# Hard-coded from Findings #8 NOVEL cluster.
# Once Path A full-scale completes, this will become a generic loader
# that pulls from path_a_full_*.json output.
NOVEL_ATOM_FILES = [
    "notes/research_drill_1bit_depth_verify_2x_2026-06-10.md",
    "notes/research_drill_20_ambitious_ideas_1x_plus_3_deep_dives_2x_2026-06-05.md",
    "notes/research_drill_8_channel_orchestration_architecture_2026-06-03.md",
    "notes/research_to_exp_dev_1BIT_DEPTH_VERIFICATION_2026-06-10.md",
]


def file_to_methodology_atom(file_path: Path) -> Atom:
    """Convert one file into a methodology_corpus Atom.

    Atom id is derived from filename. Description is the first ~600 chars of
    file body. Provenance = CAS hash + parser version.
    """
    text = file_path.read_text(encoding="utf-8", errors="replace")
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    # Extract a name (first markdown header) but limit dependency on regex
    name = file_path.stem
    for line in text.splitlines()[:10]:
        line = line.strip()
        if line.startswith("# "):
            name = line[2:].strip()[:200]
            break

    # Take first 600 chars of body as description (provenance-level, not
    # substrate-evaluation; per substrate two-axes insight, this is the
    # semantic-vec input)
    description = text[:600].strip()

    return Atom(
        id=file_path.stem,
        name=name,
        corpus=Corpus.METHODOLOGY,
        tier=Tier.TIER_NA,
        kind=AtomKind.METHODOLOGY,
        description=description,
        metadata={
            "auto_classified_as_methodology": True,
            "substrate_eval_verdict_class": "NOVEL_validated_METHODOLOGY",
            "content_hash": content_hash,
            "file_size_bytes": len(text),
            "provenance": {
                "source_file": str(file_path),
                "content_hash": content_hash,
                "parser_version": "methodology_v1_0",
                "classifier": "substrate_eval_v2_composite_C",
                "validated_by": "Research FINDINGS_08_VALIDATE_METHODOLOGY_PARTITION 2026-06-11",
            },
        },
    )


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("ingesting %d files into methodology_corpus partition...", len(NOVEL_ATOM_FILES))
    ingested = 0
    skipped = 0
    for rel in NOVEL_ATOM_FILES:
        path = Path(rel)
        if not path.exists():
            log.warning("file not found: %s", path)
            continue
        atom = file_to_methodology_atom(path)
        qid = atom.qualified_id
        if pstore.has_atom(qid):
            log.info("already present, skipping: %s", qid)
            skipped += 1
            continue
        try:
            pstore.add_atom(atom, source="methodology_corpus_ingest",
                            note="NOVEL-cluster validated by Research as multi-operation methodological content")
            ingested += 1
            log.info("ingested: %s", qid)
        except Exception as e:
            log.error("ingest failed %s: %s", qid, e)

    stats = pstore.stats()
    print(json.dumps({
        "ingested": ingested,
        "skipped": skipped,
        "methodology_partition_atoms": stats["partitions"].get("methodology", {}).get("n_atoms", 0),
        "total_atoms": stats["total_atoms"],
    }, indent=2))


if __name__ == "__main__":
    main()
