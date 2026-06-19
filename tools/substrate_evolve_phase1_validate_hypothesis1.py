"""Validate pre-registered Hypothesis 1 from Findings #15:
After Phase 1 (76 research_drill_*.md ingested as research_history atoms),
subsequent substrate-eval on those files shifts from NOVEL to TIER-A/B.

Pre-registered:
- TIER-A >= 30% / TIER-B >= 30% / TIER-C <= 30% / NOVEL <= 10%
- HARD-FAIL if NOVEL still >= 30% post-ingest
- MIDDLE if 10% <= NOVEL < 30%
- HARD-PASS if NOVEL < 10%

Per [[feedback-literature-is-not-oracle-2026-06-11]]: surface divergence
between prediction and result as discovery, not bug.
"""
from __future__ import annotations

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
from tools.substrate_eval_ingest_v2_composite import (
    classify_verdict,
    find_self_recognition_atom,
    cortical_familiarity_signal,
    _algebra_novelty_of_atoms,
    _math_atoms_referenced_by_text,
    _paragraph_coherence,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("validate_h1")

NOTES_DIR = Path("notes")
DATA_ROOT = Path("data/substrate_index")


def reclassify(file_path: Path, encoder, retriever, aidx, pstore):
    text = file_path.read_text(encoding="utf-8", errors="replace")
    candidates = retriever.semantic(text, top_k=10)
    top_k_scores = [c.score for c in candidates]
    avg_top3 = float(sum(top_k_scores[:3]) / 3) if len(top_k_scores) >= 3 else 0.0
    semantic_novelty = 1.0 - avg_top3
    referenced_math = _math_atoms_referenced_by_text(text, pstore)
    algebra_nov, n_math = _algebra_novelty_of_atoms(referenced_math, aidx)
    composite_novelty = 0.6 * semantic_novelty + 0.4 * algebra_nov  # Option E
    coherence = _paragraph_coherence(text, encoder)
    # Option B: substrate-distinguishing self-recognition
    self_recog_atom, _ = find_self_recognition_atom(str(file_path), pstore)
    # Option H: cortical familiarity (top-K avg similarity)
    cortical_high, familiarity = cortical_familiarity_signal(top_k_scores, threshold=0.65)
    verdict, _ = classify_verdict(
        composite_novelty, coherence,
        n_math_referenced=n_math,
        self_recognition_found=(self_recog_atom is not None),
        cortical_familiarity_high=cortical_high,
        familiarity_score=familiarity,
    )
    return verdict


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("corpus state: %d atoms; research_history: %d", len(pstore.all_atoms()),
             pstore.stats()["partitions"].get("research_history", {}).get("n_atoms", 0))

    encoder = AtomEncoder()
    retriever = Retriever(pstore, encoder)
    retriever.rebuild_index()
    aidx = AlgebraIndex(dim=1024)
    aidx.build(pstore)

    drill_files = sorted(NOTES_DIR.glob("research_drill_*.md"))
    log.info("re-classifying %d drill files post-ingest", len(drill_files))

    post_verdicts: Counter = Counter()
    for i, fp in enumerate(drill_files):
        if i % 15 == 0:
            log.info("  %d/%d", i, len(drill_files))
        try:
            v = reclassify(fp, encoder, retriever, aidx, pstore)
            post_verdicts[v] += 1
        except Exception as e:
            log.error("eval %s: %s", fp.name, e)

    n_total = sum(post_verdicts.values())
    print("\n" + "=" * 80)
    print(f"Hypothesis 1 validation: post-Phase-1 distribution on {n_total} drill files")
    print("=" * 80)
    print("\nPre-registered hypothesis:")
    print("  TIER-A >= 30% / TIER-B >= 30% / TIER-C <= 30% / NOVEL <= 10%")
    print()
    print("Post-Phase-1 observed:")
    for cls in ("TIER-A", "TIER-B", "TIER-C", "OUT_OF_DOMAIN", "NOVEL", "REJECT"):
        n = post_verdicts.get(cls, 0)
        pct = 100 * n / max(1, n_total)
        bar = "#" * (n // 2)
        print(f"  {cls:15s}  {n:3d}  ({pct:5.1f}%)  {bar}")

    # Verdict
    novel_pct = 100 * post_verdicts.get("NOVEL", 0) / max(1, n_total)
    ab_pct = 100 * (post_verdicts.get("TIER-A", 0) + post_verdicts.get("TIER-B", 0)) / max(1, n_total)
    print()
    if novel_pct < 10:
        print(f"VERDICT: HARD-PASS (NOVEL {novel_pct:.1f}% < 10%)")
    elif novel_pct < 30:
        print(f"VERDICT: MIDDLE-BAND (NOVEL {novel_pct:.1f}% in [10%, 30%); partial validation)")
    else:
        print(f"VERDICT: HARD-FAIL (NOVEL {novel_pct:.1f}% >= 30%; hypothesis refuted)")
    print(f"TIER-A+B: {ab_pct:.1f}% (pre-registered >= 60% combined)")

    out = DATA_ROOT / "bench_reports" / f"h1_validation_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "phase": "1_validation",
        "n_files": n_total,
        "post_verdicts": dict(post_verdicts),
        "novel_pct": novel_pct,
        "tier_ab_pct": ab_pct,
        "hypothesis_verdict": "HARD-PASS" if novel_pct < 10 else ("MIDDLE-BAND" if novel_pct < 30 else "HARD-FAIL"),
    }, indent=2), encoding="utf-8")
    log.info("wrote h1 validation report -> %s", out)


if __name__ == "__main__":
    main()
