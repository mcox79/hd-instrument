"""Substrate-eval Path A FULL SCALE -- composite C on all drill/routing/exp_dev/testbed notes.

Per Research FINDINGS_07 endorsement (composite C works) + Findings #8 Q5
(scale Path A?). Runs v2 composite C novelty on the FULL note set, not just
5-per-pattern sample.

Outputs:
- Per-note verdict + composite_novelty + #math_atoms_referenced
- Distribution across all notes
- NOVEL cluster analysis: do clusters > 4 atoms emerge? Are there multiple
  distinct NOVEL clusters (suggesting multiple new partition candidates)?
- OUT_OF_DOMAIN classification (Q3 refinement): TIER-C with #math=0 -> OUT_OF_DOMAIN

This run answers: does composite C produce stable distributions at scale,
or does the jargon-floor / algebra-fallback behavior change?
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from backend.substrate_index.algebra_index import AlgebraIndex
from backend.substrate_index.encode import AtomEncoder
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.retrieve import Retriever

# Reuse v2 logic
from tools.substrate_eval_ingest_v2_composite import (
    _math_atoms_referenced_by_text,
    _algebra_novelty_of_atoms,
    _paragraph_coherence,
    classify_verdict,
    IngestVerdict,
    TIER_A_THRESHOLD,
    TIER_B_THRESHOLD,
    TIER_C_THRESHOLD,
    COHERENCE_MIN,
    REJECT_THRESHOLD,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("path_a_full")

DATA_ROOT = Path("data/substrate_index")
NOTES_DIR = Path("notes")


def evaluate_file_with_oob(
    file_path: Path,
    encoder: AtomEncoder,
    retriever: Retriever,
    pstore: PartitionedStore,
    aidx: AlgebraIndex,
) -> IngestVerdict:
    """Evaluate one file. If verdict is TIER-C and #math=0, reclassify to
    OUT_OF_DOMAIN (per Findings #8 Q3 refinement).
    """
    text = file_path.read_text(encoding="utf-8", errors="replace")
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    candidates = retriever.semantic(text, top_k=10)
    top5_ids = tuple(c.atom_id for c in candidates[:5])
    top5_scores = tuple(c.score for c in candidates[:5])
    avg_top3 = float(np.mean([c.score for c in candidates[:3]])) if candidates else 0.0
    semantic_novelty = 1.0 - avg_top3

    referenced_math = _math_atoms_referenced_by_text(text, pstore)
    algebra_nov, n_math = _algebra_novelty_of_atoms(referenced_math, aidx)
    composite_novelty = 0.6 * semantic_novelty + 0.4 * algebra_nov  # Option E
    coherence = _paragraph_coherence(text, encoder)
    verdict, reasoning = classify_verdict(composite_novelty, coherence)

    # Q3 refinement: TIER-C + #math=0 -> OUT_OF_DOMAIN
    if verdict == "TIER-C" and n_math == 0:
        verdict = "OUT_OF_DOMAIN"
        reasoning = f"no math atoms referenced; content not about substrate operations (composite={composite_novelty:.3f})"

    corpus_counts: Counter = Counter()
    for c in candidates[:5]:
        atom = pstore.get_atom(c.atom_id)
        if atom is not None:
            corpus_counts[atom.corpus.value] += 1

    return IngestVerdict(
        file_path=str(file_path),
        content_hash=content_hash,
        file_size_bytes=len(text),
        nearest_top5_atoms=top5_ids,
        nearest_top5_scores=top5_scores,
        semantic_novelty=semantic_novelty,
        algebra_novelty=algebra_nov,
        composite_novelty=composite_novelty,
        coherence_score=coherence,
        verdict_class=verdict,
        corpus_membership_of_nearest=dict(corpus_counts),
        n_math_atoms_in_top5=n_math,
        reasoning=reasoning,
    )


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("loading encoder + retriever + algebra_index...")
    encoder = AtomEncoder()
    retriever = Retriever(pstore, encoder)
    retriever.rebuild_index()
    aidx = AlgebraIndex(dim=1024)
    n_alg = aidx.build(pstore)
    log.info("existing corpus: %d atoms; %d with algebra_hrr", len(retriever._vectors), n_alg)

    patterns = [
        "research_drill_",
        "research_to_",
        "exp_dev_to_research_",
        "testbed_to_research_",
    ]

    all_files = []
    for prefix in patterns:
        files = sorted(NOTES_DIR.glob(f"{prefix}*.md"))
        all_files.extend(files)
        log.info("  %s%s: %d files", prefix, "*", len(files))

    log.info("evaluating %d files total...", len(all_files))
    verdicts = []
    t0 = time.perf_counter()
    for i, fp in enumerate(all_files):
        if i % 20 == 0:
            elapsed = time.perf_counter() - t0
            log.info("  progress: %d/%d  (%.1fs elapsed)", i, len(all_files), elapsed)
        try:
            v = evaluate_file_with_oob(fp, encoder, retriever, pstore, aidx)
            verdicts.append(v)
        except Exception as e:
            log.error("eval failed %s: %s", fp.name, e)

    class_counts = Counter(v.verdict_class for v in verdicts)
    print("\n" + "=" * 80)
    print(f"Substrate-eval PATH A FULL SCALE: composite C on {len(verdicts)} files")
    print("=" * 80)
    print(f"\nVerdict distribution:")
    for cls in ("TIER-A", "TIER-B", "TIER-C", "OUT_OF_DOMAIN", "NOVEL", "REJECT"):
        n = class_counts.get(cls, 0)
        pct = 100 * n / max(1, len(verdicts))
        bar = "#" * (n // 2)
        print(f"  {cls:15s}  {n:4d}  ({pct:5.1f}%)  {bar}")

    # Pattern breakdown: verdicts by note type
    print(f"\nVerdict by note pattern:")
    by_pattern: dict[str, Counter] = {p: Counter() for p in patterns}
    for v in verdicts:
        for p in patterns:
            if p in v.file_path:
                by_pattern[p][v.verdict_class] += 1
                break
    print(f"  {'pattern':<25s}  TIER-A  TIER-B  TIER-C  OUT_OF_DOMAIN  NOVEL  REJECT")
    for p in patterns:
        ctr = by_pattern[p]
        print(f"  {p:<25s}  {ctr.get('TIER-A', 0):6d}  {ctr.get('TIER-B', 0):6d}  "
              f"{ctr.get('TIER-C', 0):6d}  {ctr.get('OUT_OF_DOMAIN', 0):13d}  "
              f"{ctr.get('NOVEL', 0):5d}  {ctr.get('REJECT', 0):6d}")

    # NOVEL cluster analysis
    novel = [v for v in verdicts if v.verdict_class == "NOVEL"]
    print(f"\n=== NOVEL atoms found: {len(novel)} ===")
    for v in novel[:30]:
        short = Path(v.file_path).stem[:60]
        print(f"  alg_nov={v.algebra_novelty:.3f}  #math={v.n_math_atoms_in_top5}  {short}")

    if len(novel) >= 2:
        print(f"\nNOVEL cluster pairwise analysis (top 15 strongest pairs):")
        nv = [encoder.encode_query_text(Path(v.file_path).read_text(encoding="utf-8", errors="replace")) for v in novel]
        nm = np.stack(nv)
        ns = nm @ nm.T
        pairs = []
        for i in range(len(novel)):
            for j in range(i + 1, len(novel)):
                pairs.append((i, j, ns[i, j]))
        pairs.sort(key=lambda x: -x[2])
        for i, j, s in pairs[:15]:
            si = Path(novel[i].file_path).stem[:45]
            sj = Path(novel[j].file_path).stem[:45]
            print(f"  {s:.3f}  {si}  <->  {sj}")

    # Persist
    out = DATA_ROOT / "bench_reports" / f"path_a_full_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "verdicts": [v.to_dict() for v in verdicts],
        "distribution": dict(class_counts),
        "n_files_evaluated": len(verdicts),
        "thresholds": {
            "TIER_A": TIER_A_THRESHOLD,
            "TIER_B": TIER_B_THRESHOLD,
            "TIER_C": TIER_C_THRESHOLD,
            "REJECT": REJECT_THRESHOLD,
            "COHERENCE_MIN": COHERENCE_MIN,
        },
        "elapsed_sec": time.perf_counter() - t0,
    }, indent=2), encoding="utf-8")
    log.info("wrote report -> %s (elapsed %.1fs)", out, time.perf_counter() - t0)


if __name__ == "__main__":
    main()
