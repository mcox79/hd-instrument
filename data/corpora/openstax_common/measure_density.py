# -*- coding: utf-8 -*-
"""
Definitional-construction density measurement for newly-acquired corpora (2026-08-12).

Read-only reuse of hdlab.definitional_extraction.sentence_has_definitional_pattern (the same
sentence-level detector used in tools/measure_definitional_pattern_association_v1.py's M3
segment-density measurement) and the exact sentence-split recipe already used by the
reading-grounding-loop cell for the bio_new segment (experiments/exp_reading_grounding_loop_
cycle1_v1.py:clean_sentences + cycle2's load_biology_sentences line-filtering). No writes to
hdlab/, experiments/, or data/foundation/ -- this only imports a pure function and writes its
own output under data/corpora/<title>/.

IMPORTANT CAVEAT (disclosed, not hidden): this measures the same PROXY as the M3 measurement in
tools/measure_definitional_pattern_association_v1.py -- rate of sentences containing ANY
definitional-construction pattern. It is NOT the same number as "GROUNDED_MEANING facts per 1000
sentences" from the full reading_grounding_loop pipeline (that also requires curriculum-relative
canonicalization / dedup against the existing foundation, which this script deliberately does not
run, since running that pipeline would touch data/foundation/). The two are correlated but not
identical; report both with this caveat attached, do not conflate them.

Usage:
  python measure_density.py --clean-txt <path/to/cleaned.txt> --label psychology_2e
"""
import argparse
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.definitional_extraction import sentence_has_definitional_pattern  # noqa: E402 (read-only reuse)


def clean_sentences(text: str):
    """Verbatim recipe from experiments/exp_reading_grounding_loop_cycle1_v1.py:clean_sentences."""
    parts = re.split(r"[.!?]+['\"’”]?", text)
    return [s.strip() for s in parts if s.strip()]


def load_sentences(clean_txt_path: str):
    """Verbatim line-filtering recipe from cycle2's load_biology_sentences: strip heading lines
    (# ...) and list markers (-/*/N.) before sentence-splitting."""
    with open(clean_txt_path, encoding="utf-8") as f:
        lines = f.readlines()
    kept = []
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        s = re.sub(r"^[-*]\s+", "", s)
        s = re.sub(r"^\d+\.\s+", "", s)
        kept.append(s)
    text = "\n".join(kept)
    return clean_sentences(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean-txt", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out-json", default=None)
    args = ap.parse_args()

    sentences = load_sentences(args.clean_txt)
    n = len(sentences)
    hits = sum(1 for s in sentences if sentence_has_definitional_pattern(s))
    density_per_1000 = round(1000.0 * hits / n, 1) if n else 0.0

    out = {
        "label": args.label,
        "clean_txt": args.clean_txt,
        "n_sentences": n,
        "n_definitional_pattern_sentences": hits,
        "definitional_pattern_density_per_1000_sentences": density_per_1000,
        "caveat": "proxy measure (sentence-level pattern hit rate), not the full "
                  "GROUNDED_MEANING-facts-extracted pipeline rate; see module docstring",
    }
    print(json.dumps(out, indent=2))
    if args.out_json:
        os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
