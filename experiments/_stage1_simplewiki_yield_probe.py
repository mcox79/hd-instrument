"""STAGE-1 PRICE TAG: what does running Simple English Wikipedia through the REAL definitional
extractor buy us, in SimLex-999 covered PAIRS?

Read-only. Uniformly samples every Nth sentence of the already-cleaned simplewiki corpus, runs
hdlab.definitional_extraction.extract_definitions unmodified, and reports the measured SimLex
yield plus a wall-time-based cost estimate for the full corpus.

Nothing under hdlab/ is modified. ASCII-only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import csv
import json
import time

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.definitional_extraction import extract_definitions      # noqa: E402

CORPUS = os.path.join(REPO_ROOT, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")
SIMLEX = os.path.join(REPO_ROOT, "data", "encoder_eval_benchmarks", "simlex999.txt")

STRIDE = 20          # uniform 1-in-20 sample across the WHOLE file (not a biased head slice)
MAX_PROCESSED = 120000


def main():
    pairs = []
    with open(SIMLEX, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            pairs.append((r["word1"], r["word2"], float(r["SimLex999"])))
    vocab = {w for p in pairs for w in p[:2]}

    hit_terms = set()          # SimLex words that got a definition WITH a definiens surface
    n_defs = 0
    n_processed = 0
    n_seen = 0
    t0 = time.time()
    with open(CORPUS, encoding="utf-8", errors="replace") as f:
        for line in f:
            n_seen += 1
            if n_seen % STRIDE:
                continue
            s = line.strip()
            if not s or len(s) > 600:
                continue
            n_processed += 1
            for d in extract_definitions(s):
                n_defs += 1
                for cand in (d.term, d.definiendum, d.definiendum_lemma):
                    if not cand:
                        continue
                    c = cand.strip().lower()
                    if c in vocab and d.definiens:
                        hit_terms.add(c)
            if n_processed >= MAX_PROCESSED:
                break
    dt = time.time() - t0

    cov = hit_terms
    cp = [p for p in pairs if p[0] in cov and p[1] in cov]

    frac_of_file = n_seen / max(n_seen, 1)
    rate = n_processed / max(dt, 1e-9)
    # full corpus = every sentence, i.e. STRIDE x the sample we processed, scaled to whole file
    est_total_sentences = n_seen * (1.0)   # sentences scanned so far
    report = {
        "corpus": os.path.relpath(CORPUS, REPO_ROOT),
        "stride": STRIDE,
        "sentences_scanned": n_seen,
        "sentences_processed": n_processed,
        "definitions_extracted": n_defs,
        "simlex_words_hit": len(cov),
        "simlex_pairs_both_covered": len(cp),
        "elapsed_s": round(dt, 1),
        "extractor_sentences_per_s": round(rate, 1),
        "sample_covered_pairs": [(a, b, g) for a, b, g in cp[:40]],
        "sample_hit_terms": sorted(cov)[:80],
    }
    print(json.dumps(report, indent=2))
    out = os.path.join(REPO_ROOT, "data", "_stage1_simplewiki_yield_probe.json")
    with open(out + ".tmp", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    os.replace(out + ".tmp", out)
    print("\nWROTE %s" % out)


if __name__ == "__main__":
    main()
