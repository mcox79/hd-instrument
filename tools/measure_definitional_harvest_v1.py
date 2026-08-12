"""tools/measure_definitional_harvest_v1.py

STEP-1 GO/NO-GO: how many DISTINCT definitional facts can `hdlab.definitional_extraction` harvest
from the reading corpus, and what does a raw random sample of them look like? This is the
coverage question that decides whether definitional extraction is worth building into the loop at
all -- per the honesty requirement, both the RATE and the ABSOLUTE COUNT are reported, because a
high rate on 40 facts is not obviously better than a low rate on 634.

Writes data/analysis_definitional_harvest_v1/metrics.json + a raw 40-row eyeball sample.
"""

from __future__ import annotations

import json
import os
import random
import sys
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.definitional_extraction import extract_definitions  # noqa: E402
from tools.measure_definitional_pattern_association_v2 import load_corpus  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "data", "analysis_definitional_harvest_v1")


def main() -> None:
    corpus = load_corpus()
    facts = []
    per_seg = Counter()
    per_pat = Counter()
    for seg, s in corpus:
        for d in extract_definitions(s):
            facts.append({"segment": seg, "subject": d.definiendum_lemma, "object": d.head,
                          "pattern": d.pattern, "definiendum": d.definiendum,
                          "definiens": d.definiens, "sentence": s})
            per_seg[seg] += 1
            per_pat[d.pattern] += 1

    uniq = {}
    for f in facts:
        uniq.setdefault((f["subject"], f["object"]), f)
    uniq_subj = {}
    for f in facts:
        uniq_subj.setdefault(f["subject"], []).append(f)

    out = {
        "n_corpus_sentences": len(corpus),
        "n_definitional_extractions_raw": len(facts),
        "n_distinct_subject_object_pairs": len(uniq),
        "n_distinct_definienda": len(uniq_subj),
        "per_segment_raw": dict(per_seg),
        "per_pattern_raw": dict(per_pat),
        "top_20_definienda_by_count": [
            {"subject": k, "n": len(v), "objects": sorted({x["object"] for x in v})}
            for k, v in sorted(uniq_subj.items(), key=lambda kv: -len(kv[1]))[:20]],
    }

    rng = random.Random(42)
    keys = sorted(uniq)
    sample = [uniq[k] for k in rng.sample(keys, min(40, len(keys)))]
    out["raw_sample_40"] = sample

    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print(json.dumps({k: v for k, v in out.items() if k != "raw_sample_40"}, indent=2)[:2500])
    print("--- raw sample (first 30) ---")
    for f in sample[:30]:
        print(f"  [{f['pattern']:15s} {f['segment']:9s}] {f['subject']:18s} -> {f['object']:16s}"
              f" | {f['sentence'][:95]}")


if __name__ == "__main__":
    main()
