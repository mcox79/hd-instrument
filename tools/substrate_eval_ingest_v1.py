"""Substrate-evaluation ingest v1: 5-class verdict + novelty score + 2-stage NOVEL filter.

Per Research NOVELTY_REFRAME_ENDORSED 2026-06-11:
- Phase 1 (this script): 5-class verdict + novelty score A (semantic top-K) +
  adversarial-probe + 2-stage NOVEL filter
- Phase 2 (post-v2-Index-2): composite C primitive (semantic + algebra)
- Phase 3 (Week 2): K-L primitive D for Layer 8 BOCPD

User reframe: substrate doesn't just classify against existing structure;
it proposes structure when content doesn't fit. NOVEL atoms get watched
for cluster formation -> propose new corpus partition / tier classification.

Run target: all 4 note patterns (drill + research_to + exp_dev_to +
testbed_to) on the existing corpus to see verdict distribution.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from backend.substrate_index.encode import AtomEncoder
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.retrieve import Retriever
from backend.substrate_index.schema import Corpus

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("substrate_eval_v1")

DATA_ROOT = Path("data/substrate_index")
NOTES_DIR = Path("notes")

# Thresholds per Research Q2 (v1 starting points; bootstrap CI calibrate later)
NOVELTY_THRESHOLD = 0.45      # top-3 avg similarity below this = NOVEL candidate
TIER_A_THRESHOLD = 0.70       # top-3 avg above this = TIER-A high confidence
TIER_B_THRESHOLD = 0.55       # 0.55-0.70 = TIER-B provisional
TIER_C_THRESHOLD = 0.45       # 0.45-0.55 = TIER-C low confidence
COHERENCE_MIN = 0.35          # NOVEL-coherent vs REJECT-noise split (paragraph-level)
REJECT_THRESHOLD = 0.30       # top-3 avg below this is candidate for REJECT


@dataclass(frozen=True)
class IngestVerdict:
    """Substrate's evaluation of one incoming file."""
    file_path: str
    content_hash: str
    file_size_bytes: int
    nearest_top3_atoms: tuple[str, ...]
    nearest_top3_scores: tuple[float, ...]
    novelty_score: float            # 1 - avg(top-3 similarity)
    avg_top3_similarity: float
    coherence_score: float          # paragraph-level internal cosine
    verdict_class: str              # TIER-A / TIER-B / TIER-C / NOVEL / REJECT
    corpus_membership_of_nearest: dict  # {corpus_value: count}
    reasoning: str

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "content_hash": self.content_hash,
            "file_size_bytes": self.file_size_bytes,
            "nearest_top3_atoms": list(self.nearest_top3_atoms),
            "nearest_top3_scores": [round(s, 3) for s in self.nearest_top3_scores],
            "novelty_score": round(self.novelty_score, 3),
            "avg_top3_similarity": round(self.avg_top3_similarity, 3),
            "coherence_score": round(self.coherence_score, 3),
            "verdict_class": self.verdict_class,
            "corpus_membership_of_nearest": dict(self.corpus_membership_of_nearest),
            "reasoning": self.reasoning,
        }


def _paragraph_coherence(text: str, encoder: AtomEncoder, max_paragraphs: int = 8) -> float:
    """Measure internal coherence: average pairwise semantic cosine between
    paragraphs.

    Per Research Q5 2-stage NOVEL filter: NOVEL-coherent if content has
    internal coherence; REJECT-noise if not. Random text has near-zero
    paragraph coherence; structured content has high coherence.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 50]
    if len(paragraphs) < 2:
        return 0.0
    paragraphs = paragraphs[:max_paragraphs]
    vecs = []
    for p in paragraphs:
        v = encoder.encode_query_text(p[:1000])
        vecs.append(v)
    mat = np.stack(vecs)
    sim = mat @ mat.T
    # Off-diagonal mean
    n = len(paragraphs)
    off_diag = sim[np.triu_indices(n, k=1)]
    return float(off_diag.mean()) if len(off_diag) > 0 else 0.0


def classify_verdict(
    avg_top3: float,
    coherence: float,
    corpus_membership_diversity: int,
) -> tuple[str, str]:
    """Five-class verdict with 2-stage NOVEL filter.

    Returns (verdict_class, reasoning).
    """
    if avg_top3 >= TIER_A_THRESHOLD:
        return ("TIER-A", f"high-confidence classify (avg_top3={avg_top3:.3f} >= {TIER_A_THRESHOLD})")
    if avg_top3 >= TIER_B_THRESHOLD:
        return ("TIER-B", f"provisional classify (avg_top3={avg_top3:.3f} in [{TIER_B_THRESHOLD}, {TIER_A_THRESHOLD}))")
    if avg_top3 >= TIER_C_THRESHOLD:
        return ("TIER-C", f"low confidence (avg_top3={avg_top3:.3f} in [{TIER_C_THRESHOLD}, {TIER_B_THRESHOLD}))")
    # Below TIER_C: NOVEL or REJECT decided by coherence
    if avg_top3 < REJECT_THRESHOLD and coherence < COHERENCE_MIN:
        return ("REJECT", f"low similarity + low coherence (avg_top3={avg_top3:.3f}, coherence={coherence:.3f})")
    if coherence >= COHERENCE_MIN:
        return ("NOVEL", f"low similarity but content COHERENT (avg_top3={avg_top3:.3f}, coherence={coherence:.3f}) -- substrate lacks structure for this content type")
    return ("REJECT", f"low similarity + insufficient coherence (avg_top3={avg_top3:.3f}, coherence={coherence:.3f})")


def evaluate_file(
    file_path: Path,
    encoder: AtomEncoder,
    retriever: Retriever,
    pstore: PartitionedStore,
) -> IngestVerdict:
    """Substrate evaluates one file: position + classify + report."""
    text = file_path.read_text(encoding="utf-8", errors="replace")
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    candidates = retriever.semantic(text, top_k=10)
    top3_ids = tuple(c.atom_id for c in candidates[:3])
    top3_scores = tuple(c.score for c in candidates[:3])
    avg_top3 = float(np.mean(top3_scores)) if top3_scores else 0.0
    novelty_score = 1.0 - avg_top3

    # Corpus membership counts of top 5
    corpus_counts: Counter = Counter()
    for c in candidates[:5]:
        atom = pstore.get_atom(c.atom_id)
        if atom is not None:
            corpus_counts[atom.corpus.value] += 1

    coherence = _paragraph_coherence(text, encoder)

    verdict_class, reasoning = classify_verdict(
        avg_top3, coherence, len(corpus_counts)
    )

    return IngestVerdict(
        file_path=str(file_path),
        content_hash=content_hash,
        file_size_bytes=len(text),
        nearest_top3_atoms=top3_ids,
        nearest_top3_scores=top3_scores,
        novelty_score=novelty_score,
        avg_top3_similarity=avg_top3,
        coherence_score=coherence,
        verdict_class=verdict_class,
        corpus_membership_of_nearest=dict(corpus_counts),
        reasoning=reasoning,
    )


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("loading encoder + retriever...")
    encoder = AtomEncoder()
    retriever = Retriever(pstore, encoder)
    retriever.rebuild_index()
    log.info("existing corpus: %d atoms", len(retriever._vectors))

    # Sample 20 files: 5 from each of 4 patterns
    patterns = [
        ("research_drill_", 5),
        ("research_to_", 5),
        ("exp_dev_to_research_", 5),
        ("testbed_to_research_", 5),
    ]

    selected_files = []
    for prefix, n in patterns:
        files = sorted(NOTES_DIR.glob(f"{prefix}*.md"))[:n]
        selected_files.extend(files)

    log.info("evaluating %d files across 4 patterns...", len(selected_files))
    verdicts = []
    for fp in selected_files:
        v = evaluate_file(fp, encoder, retriever, pstore)
        verdicts.append(v)

    # Distribution summary
    class_counts = Counter(v.verdict_class for v in verdicts)
    print("\n" + "=" * 80)
    print(f"Substrate-eval v1 on {len(verdicts)} files (5 per pattern)")
    print("=" * 80)
    print(f"\nVerdict distribution:")
    for cls in ("TIER-A", "TIER-B", "TIER-C", "NOVEL", "REJECT"):
        n = class_counts.get(cls, 0)
        bar = "#" * n
        print(f"  {cls:8s}  {n:3d}  {bar}")

    # Per-file detail
    print(f"\nPer-file verdicts:")
    print(f"{'verdict':<10s} {'avg_top3':>10s} {'coher':>8s} {'novelty':>8s}  file")
    print(f"{'-'*10} {'-'*10} {'-'*8} {'-'*8}  {'-'*60}")
    for v in verdicts:
        short_path = Path(v.file_path).stem[:55]
        print(f"{v.verdict_class:<10s} {v.avg_top3_similarity:>10.3f} {v.coherence_score:>8.3f} {v.novelty_score:>8.3f}  {short_path}")

    # NOVEL cluster analysis: do the NOVEL atoms cluster together (same near
    # neighbors / same corpus targets)?
    novel_atoms = [v for v in verdicts if v.verdict_class == "NOVEL"]
    if len(novel_atoms) >= 2:
        print(f"\n=== NOVEL cluster analysis ({len(novel_atoms)} NOVEL atoms) ===")
        # Re-encode all NOVEL bodies and cluster them
        novel_vecs = []
        for v in novel_atoms:
            text = Path(v.file_path).read_text(encoding="utf-8", errors="replace")
            novel_vecs.append(encoder.encode_query_text(text))
        novel_mat = np.stack(novel_vecs)
        novel_sim = novel_mat @ novel_mat.T
        print("Pairwise semantic similarity among NOVEL atoms:")
        for i, vi in enumerate(novel_atoms):
            for j in range(i + 1, len(novel_atoms)):
                vj = novel_atoms[j]
                s = novel_sim[i, j]
                if s > 0.45:
                    print(f"  CLUSTER: {Path(vi.file_path).stem[:50]} <-> {Path(vj.file_path).stem[:50]}  ({s:.3f})")

    out = DATA_ROOT / "bench_reports" / f"substrate_eval_v1_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "verdicts": [v.to_dict() for v in verdicts],
        "distribution": dict(class_counts),
        "thresholds": {
            "TIER_A": TIER_A_THRESHOLD,
            "TIER_B": TIER_B_THRESHOLD,
            "TIER_C": TIER_C_THRESHOLD,
            "REJECT": REJECT_THRESHOLD,
            "COHERENCE_MIN": COHERENCE_MIN,
        },
    }, indent=2), encoding="utf-8")
    log.info("wrote report -> %s", out)


if __name__ == "__main__":
    main()
