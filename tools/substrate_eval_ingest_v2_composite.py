"""Substrate-evaluation ingest v2: composite novelty (semantic + algebra HRR).

Per Research FINDINGS_07_OPTION_4_COMPOSITE_C 2026-06-11:
composite_novelty = max(semantic_novelty, algebra_novelty)

semantic_novelty: 1 - avg(top-3 semantic similarity) -- same as v1
algebra_novelty: 1 - avg pairwise algebra_hrr cosine among semantic top-K's
                 math atoms. High if file references atoms spanning algebra
                 space (cross-domain/methodological content); low if file is
                 within one algebra cluster.

Hypothesis: drill on cross-domain equivalences scores HIGH algebra_novelty
(discusses many algebra categories); drill on 1bit_depth_verify scores LOW
algebra_novelty (within one substrate operation type).

If composite works: notes that look semantically similar to substrate jargon
but discuss algebraically-disparate content get correctly flagged NOVEL.
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
from backend.substrate_index.algebra_index import AlgebraIndex
from backend.substrate_index.encode import AtomEncoder
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.retrieve import Retriever
from backend.substrate_index.schema import Corpus

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("substrate_eval_v2")

DATA_ROOT = Path("data/substrate_index")
NOTES_DIR = Path("notes")

# v2 thresholds tuned for composite score
TIER_A_THRESHOLD = 0.30   # novelty <= 0.30 = high confidence match
TIER_B_THRESHOLD = 0.45   # 0.30-0.45 = provisional
TIER_C_THRESHOLD = 0.55   # 0.45-0.55 = low confidence
# > 0.55 = NOVEL (with coherence gate) or REJECT
COHERENCE_MIN = 0.35
REJECT_THRESHOLD = 0.70   # novelty >= 0.70 = candidate REJECT if also incoherent


@dataclass(frozen=True)
class IngestVerdict:
    file_path: str
    content_hash: str
    file_size_bytes: int
    nearest_top5_atoms: tuple[str, ...]
    nearest_top5_scores: tuple[float, ...]
    semantic_novelty: float
    algebra_novelty: float
    composite_novelty: float
    coherence_score: float
    verdict_class: str
    corpus_membership_of_nearest: dict
    n_math_atoms_in_top5: int
    reasoning: str

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "content_hash": self.content_hash,
            "file_size_bytes": self.file_size_bytes,
            "nearest_top5_atoms": list(self.nearest_top5_atoms),
            "nearest_top5_scores": [round(s, 3) for s in self.nearest_top5_scores],
            "semantic_novelty": round(self.semantic_novelty, 3),
            "algebra_novelty": round(self.algebra_novelty, 3),
            "composite_novelty": round(self.composite_novelty, 3),
            "coherence_score": round(self.coherence_score, 3),
            "verdict_class": self.verdict_class,
            "corpus_membership_of_nearest": dict(self.corpus_membership_of_nearest),
            "n_math_atoms_in_top5": self.n_math_atoms_in_top5,
            "reasoning": self.reasoning,
        }


def _paragraph_coherence(text: str, encoder: AtomEncoder, max_paragraphs: int = 8) -> float:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 50]
    if len(paragraphs) < 2:
        return 0.0
    paragraphs = paragraphs[:max_paragraphs]
    vecs = [encoder.encode_query_text(p[:1000]) for p in paragraphs]
    mat = np.stack(vecs)
    sim = mat @ mat.T
    n = len(paragraphs)
    off_diag = sim[np.triu_indices(n, k=1)]
    return float(off_diag.mean()) if len(off_diag) > 0 else 0.0


def _math_atoms_referenced_by_text(
    text: str,
    pstore: PartitionedStore,
) -> list[str]:
    """Find math atom IDs whose name or aliases appear in the file text.

    Distinct from semantic-nearest: this is "what atoms does the file
    LITERALLY mention by name?" — better signal for algebra_novelty since
    drill content discusses specific math primitives by name even when its
    overall semantic vector lives in concept-space.
    """
    text_lower = text.lower()
    matched: set[str] = set()
    for atom in pstore.all_atoms():
        if atom.corpus.value != "math":
            continue
        # Build candidate phrases: name, aliases, local-id suffix
        candidates = [atom.name.lower()]
        for alias in atom.aliases:
            candidates.append(alias.lower().replace("_", " "))
        # Also try the local id minus tier prefix (e.g. "fhrr_bind" -> "fhrr bind")
        local_id_phrase = atom.id.split("/")[-1].replace("_", " ").lower()
        if local_id_phrase and len(local_id_phrase) > 4:
            candidates.append(local_id_phrase)
        for cand in candidates:
            if len(cand) >= 4 and cand in text_lower:
                matched.add(atom.qualified_id)
                break
    return sorted(matched)


def _algebra_novelty_of_atoms(
    atom_ids: list[str],
    aidx: AlgebraIndex,
) -> tuple[float, int]:
    """Algebra novelty = 1 - avg pairwise algebra_hrr cosine among given atoms.

    Interpretation:
    - All atoms in same algebra cluster -> high pairwise sim -> low novelty
    - Atoms span algebra space -> low pairwise sim -> high novelty
    """
    algebra_vecs = []
    for aid in atom_ids:
        av = aidx._atom_vectors.get(aid)
        if av is None or av.algebra_hrr is None:
            continue
        algebra_vecs.append(av.algebra_hrr)
    n_math = len(algebra_vecs)
    if n_math < 2:
        return (0.5, n_math)
    mat = np.stack(algebra_vecs)
    sim = mat @ mat.T
    n = mat.shape[0]
    off_diag = sim[np.triu_indices(n, k=1)]
    avg_pairwise = float(off_diag.mean())
    return (1.0 - avg_pairwise, n_math)


def cortical_familiarity_signal(top_k_scores: list[float], threshold: float = 0.65) -> tuple[bool, float]:
    """Option H per Findings 17 drill rank 1 (combined with B): cortical familiarity.

    Top-K atom retrieval confidence: if substrate has many similar atoms in
    its corpus (high top-K average similarity), the input content is FAMILIAR
    even if not an exact source_file match.

    Combined with Option B (file_id recollection): dual-process recognition
    memory mechanism (brain CA3 hippocampal recollection + cortical familiarity).

    Returns (is_familiar, avg_top_k_score).
    """
    if not top_k_scores:
        return (False, 0.0)
    avg = sum(top_k_scores) / len(top_k_scores)
    return (avg >= threshold, avg)


def find_self_recognition_atom(file_path: str, pstore) -> tuple[str | None, float | None]:
    """Option B substrate-distinguishing self-recognition: look up whether any
    atom has provenance.source_file matching the input file path.

    Per Research FINDINGS_17 endorsement of Option B. Returns (atom_qid, 1.0)
    if found; else (None, None).
    """
    for atom in pstore.all_atoms():
        prov = atom.metadata.get("provenance") or {}
        if prov.get("source_file") == file_path:
            return (atom.qualified_id, 1.0)
        # Also check direct metadata fields (Phase 6 + math batch ingests may
        # not have provenance.source_file but might have content_hash)
        if atom.metadata.get("source_file") == file_path:
            return (atom.qualified_id, 1.0)
    return (None, None)


def classify_verdict(novelty: float, coherence: float, n_math_referenced: int = -1,
                     self_recognition_found: bool = False,
                     cortical_familiarity_high: bool = False,
                     familiarity_score: float = 0.0) -> tuple[str, str]:
    """6-class verdict per Research FINDINGS_08 Q3:
    TIER-A / TIER-B / TIER-C / OUT_OF_DOMAIN / NOVEL / REJECT.

    OUT_OF_DOMAIN: TIER-C-band novelty AND #math=0 -> content not about
    substrate operations at all (substrate detects its own scope-limit;
    Type B self-improvement signal).
    """
    # Option B per Findings 17: substrate-distinguishing self-recognition layer
    # If substrate has an atom referencing this file_id, classify TIER-A by self-recognition
    if self_recognition_found:
        return ("TIER-A", "substrate self-recognition: source file matches existing ingested atom (Option B = hippocampal recollection)")
    # Option H: cortical familiarity (top-K retrieval avg high)
    # Combined with B = brain dual-process recognition (CA3 recollection + cortical familiarity)
    if cortical_familiarity_high:
        return ("TIER-A", f"substrate cortical familiarity: avg top-K retrieval score {familiarity_score:.3f} (Option H)")
    if novelty <= TIER_A_THRESHOLD:
        return ("TIER-A", f"high-confidence classify (novelty={novelty:.3f} <= {TIER_A_THRESHOLD})")
    # NOTE: weighted-avg composite (Option E from Findings 17 drill) applied at the
    # call-site -- callers now pass weighted_avg(semantic, algebra) instead of max().
    if novelty <= TIER_B_THRESHOLD:
        return ("TIER-B", f"provisional classify (novelty={novelty:.3f} in [{TIER_A_THRESHOLD}, {TIER_B_THRESHOLD}])")
    if novelty <= TIER_C_THRESHOLD:
        # OUT_OF_DOMAIN check: TIER-C-band + no math atoms referenced
        if n_math_referenced == 0:
            return ("OUT_OF_DOMAIN", f"no math atoms referenced; content outside substrate's current scope (novelty={novelty:.3f})")
        return ("TIER-C", f"low confidence (novelty={novelty:.3f} in [{TIER_B_THRESHOLD}, {TIER_C_THRESHOLD}])")
    # Above TIER-C: NOVEL or REJECT decided by coherence
    if novelty >= REJECT_THRESHOLD and coherence < COHERENCE_MIN:
        return ("REJECT", f"high novelty + low coherence (novelty={novelty:.3f}, coherence={coherence:.3f})")
    if coherence >= COHERENCE_MIN:
        return ("NOVEL", f"high novelty + COHERENT content (novelty={novelty:.3f}, coherence={coherence:.3f}) -- substrate lacks structure for this content")
    return ("REJECT", f"high novelty + insufficient coherence (novelty={novelty:.3f}, coherence={coherence:.3f})")


def evaluate_file(
    file_path: Path,
    encoder: AtomEncoder,
    retriever: Retriever,
    pstore: PartitionedStore,
    aidx: AlgebraIndex,
) -> IngestVerdict:
    text = file_path.read_text(encoding="utf-8", errors="replace")
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    candidates = retriever.semantic(text, top_k=10)
    top5_ids = tuple(c.atom_id for c in candidates[:5])
    top5_scores = tuple(c.score for c in candidates[:5])

    # Semantic novelty: 1 - avg top-3 sim
    avg_top3 = float(np.mean([c.score for c in candidates[:3]])) if candidates else 0.0
    semantic_novelty = 1.0 - avg_top3

    # Algebra novelty: pairwise algebra_hrr spread among math atoms
    # LITERALLY REFERENCED (by name match) in the file text
    referenced_math = _math_atoms_referenced_by_text(text, pstore)
    algebra_nov, n_math = _algebra_novelty_of_atoms(referenced_math, aidx)

    # Composite: max of the two
    # Option E (Findings 17 drill bridge fix): weighted-avg instead of max
    composite_novelty = 0.6 * semantic_novelty + 0.4 * algebra_nov

    coherence = _paragraph_coherence(text, encoder)
    verdict, reasoning = classify_verdict(composite_novelty, coherence, n_math_referenced=n_math)

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
        ("research_drill_", 5),
        ("research_to_", 5),
        ("exp_dev_to_research_", 5),
        ("testbed_to_research_", 5),
    ]

    selected_files = []
    for prefix, n in patterns:
        files = sorted(NOTES_DIR.glob(f"{prefix}*.md"))[:n]
        selected_files.extend(files)

    log.info("evaluating %d files...", len(selected_files))
    verdicts = []
    for fp in selected_files:
        v = evaluate_file(fp, encoder, retriever, pstore, aidx)
        verdicts.append(v)

    class_counts = Counter(v.verdict_class for v in verdicts)
    print("\n" + "=" * 80)
    print(f"Substrate-eval v2 (composite C) on {len(verdicts)} files")
    print("=" * 80)
    print(f"\nVerdict distribution:")
    for cls in ("TIER-A", "TIER-B", "TIER-C", "NOVEL", "REJECT"):
        n = class_counts.get(cls, 0)
        bar = "#" * n
        print(f"  {cls:8s}  {n:3d}  {bar}")

    print(f"\nPer-file (composite = max(semantic, algebra)):")
    print(f"{'verdict':<10s} {'sem_nov':>8s} {'alg_nov':>8s} {'comp':>8s} {'coher':>8s} {'#math':>6s}  file")
    print(f"{'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*6}  {'-'*50}")
    for v in verdicts:
        short = Path(v.file_path).stem[:48]
        print(f"{v.verdict_class:<10s} {v.semantic_novelty:>8.3f} {v.algebra_novelty:>8.3f} "
              f"{v.composite_novelty:>8.3f} {v.coherence_score:>8.3f} {v.n_math_atoms_in_top5:>6d}  {short}")

    # NOVEL cluster analysis
    novel = [v for v in verdicts if v.verdict_class == "NOVEL"]
    if len(novel) >= 2:
        print(f"\n=== NOVEL cluster analysis ({len(novel)} NOVEL atoms) ===")
        nv = [encoder.encode_query_text(Path(v.file_path).read_text(encoding="utf-8", errors="replace")) for v in novel]
        nm = np.stack(nv)
        ns = nm @ nm.T
        for i in range(len(novel)):
            for j in range(i + 1, len(novel)):
                if ns[i, j] > 0.45:
                    print(f"  CLUSTER: {Path(novel[i].file_path).stem[:45]} <-> {Path(novel[j].file_path).stem[:45]}  ({ns[i,j]:.3f})")

    out = DATA_ROOT / "bench_reports" / f"substrate_eval_v2_{int(time.time())}.json"
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
        "composite": "max(semantic_novelty, algebra_novelty)",
    }, indent=2), encoding="utf-8")
    log.info("wrote report -> %s", out)


if __name__ == "__main__":
    main()
