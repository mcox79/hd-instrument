"""tools/measure_definitional_pattern_association_v2.py

STEP-1 DIAGNOSIS, POWERED VERSION. v1 of this measurement was underpowered on M2: only 8 of the
32 independently-labelled v1 pairs had ANY sentence available, because it searched only the 634
v2 facts' own evidence sentences. This version searches the WHOLE READING CORPUS (the same
segment pools the loop reads), so every labelled pair gets a fair test.

M2': for each independently-labelled pair (subject S, object O) from the previous director's v1
audit, gather every corpus sentence containing BOTH S and O (lemma-matched), then ask:
  (a) does any definitional construction LINK S->O in one of them?
  (b) do S and O merely CO-OCCUR (the null the hypothesis says is doing all the work)?
  (c) is S and O a COMPOUND TERM ("phylogenetic tree") -- an adjacent-token multiword unit?
If the hypothesis is right, MEANINGFUL pairs should be enriched for (a) and/or (c) relative to
NOISE pairs, which should be explicable by (b) alone.

Writes data/analysis_definitional_pattern_association_v2/metrics.json.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.definitional_extraction import (  # noqa: E402
    extract_definitions, links, sentence_has_definitional_pattern,
)
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
from tools.measure_definitional_pattern_association_v1 import V1_LABELS  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "data", "analysis_definitional_pattern_association_v2")


def load_corpus() -> List[Tuple[str, str]]:
    """[(segment, sentence)] over every pool the reading loop reads."""
    from experiments.exp_reading_grounding_loop_cycle1_v1 import build_curriculum_pool
    from experiments.exp_reading_grounding_loop_cycle2_v1 import SEGMENT_POOL_LOADERS
    out: List[Tuple[str, str]] = []
    for _tier, s in build_curriculum_pool(None):
        out.append(("bootstrap", s))
    for seg, loader in SEGMENT_POOL_LOADERS.items():
        for _tier, s in loader(None):
            out.append((seg, s))
    return out


def main() -> None:
    corpus = load_corpus()
    lemma_sets: List[Set[str]] = []
    lemma_seqs: List[List[str]] = []
    import re
    tok_re = re.compile(r"[A-Za-z][A-Za-z'-]*")
    for _seg, s in corpus:
        seq = [lemma_verb(t) for t in tok_re.findall(s)]
        lemma_seqs.append(seq)
        lemma_sets.append(set(seq))

    rows = []
    for (subj, obj), label in V1_LABELS.items():
        idxs = [i for i, ls in enumerate(lemma_sets) if subj in ls and obj in ls]
        n_co = len(idxs)
        link_kind = None
        compound = False
        for i in idxs:
            seq = lemma_seqs[i]
            for j in range(len(seq) - 1):
                if (seq[j], seq[j + 1]) in ((subj, obj), (obj, subj)):
                    compound = True
                    break
            lk = links(corpus[i][1], subj, obj)
            if lk is not None and (link_kind is None or lk.endswith(":HEAD")):
                link_kind = lk
        n_subj_only = sum(1 for ls in lemma_sets if subj in ls)
        rows.append({"subject": subj, "object": obj, "label": label,
                     "n_cooccurring_sentences": n_co,
                     "n_subject_sentences": n_subj_only,
                     "pair_linked_by_definition": link_kind,
                     "compound_term_adjacent": compound})

    by_label: Dict[str, List[dict]] = defaultdict(list)
    for r in rows:
        by_label[r["label"]].append(r)

    summary = {}
    for lab, rs in sorted(by_label.items()):
        n = len(rs)
        summary[lab] = {
            "n_pairs": n,
            "n_with_cooccurrence": sum(1 for r in rs if r["n_cooccurring_sentences"] > 0),
            "n_linked_by_definition": sum(1 for r in rs if r["pair_linked_by_definition"]),
            "rate_linked_by_definition": round(
                sum(1 for r in rs if r["pair_linked_by_definition"]) / n, 4),
            "n_compound_term": sum(1 for r in rs if r["compound_term_adjacent"]),
            "rate_compound_term": round(sum(1 for r in rs if r["compound_term_adjacent"]) / n, 4),
            "median_cooccurring_sentences": sorted(
                r["n_cooccurring_sentences"] for r in rs)[n // 2],
        }

    out = {
        "n_corpus_sentences": len(corpus),
        "segments": dict(Counter(seg for seg, _ in corpus)),
        "M2prime_per_label": summary,
        "rows": rows,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))
    for r in sorted(rows, key=lambda r: r["label"]):
        print(f"  {r['label']:11s} {r['subject']:16s} -> {r['object']:14s} "
              f"co={r['n_cooccurring_sentences']:4d} def={r['pair_linked_by_definition']} "
              f"compound={r['compound_term_adjacent']}")


if __name__ == "__main__":
    main()
