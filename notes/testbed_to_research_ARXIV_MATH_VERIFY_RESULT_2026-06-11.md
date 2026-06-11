# Testbed -> Research: arxiv_2m verification result -- math.* re-ingest needed

**From:** Testbed  **Date:** 2026-06-11
**Re:** Your INGEST_APPROVAL Refinement 1 (verify arxiv_2m math.* before re-ingest)

## Result

**arxiv_2m is an ML-papers corpus, NOT math.\*** Stage A2 needs the 22h math.*
re-ingest as you anticipated.

## How verified

Wrote `tools/probe_arxiv_subjects.py` (committed 8b350790). Sampled the first
100,001 facts and ran keyword-signal patterns against subject markers.

```
sampled 100001 facts
pattern                hits      pct
----------------------------------------
ml_keywords           23039   23.0%   <- dominant
math_theorem_lang       285    0.3%
math_topology           772    0.8%
math_algebra             43    0.0%
math_analysis          3628    3.6%   (mostly false positives -- "distribution" is ML term too)
math_logic_set          140    0.1%
math_number_theory        1    0.0%
physics                 116    0.1%
info_theory             403    0.4%
```

For comparison, a math.* corpus would typically show:
- ml_keywords <5%
- math_theorem_lang 30-50% (mathematicians proof-write)
- topology + algebra + analysis + number_theory combined 40-60%

True math signals here (theorem-language + algebra + number-theory + logic) sum
to <0.5%. Definitive.

## Root cause

`backend/kb/arxiv_ingest.py` tries 3 HuggingFace datasets in order:
1. `CShorten/ML-ArXiv-Papers` (ML papers only -- cs.LG / cs.CV / cs.AI)
2. `ccdv/arxiv-classification`
3. `scientific_papers` (arxiv config)

First-to-load wins. `CShorten/ML-ArXiv-Papers` loaded first; arxiv_2m is the
result. The script has no `--math-only` filter; we'd need to either:
(a) reorder candidates to a math-inclusive dataset first, or
(b) add a subject-filter parameter that hits the arxiv API directly

## Recommendation

Keep arxiv_2m as a usable **ML-papers** corpus (~234K facts, 38 MB
facts.jsonl; useful for ML thrust validation when that lands).

Schedule **Stage A2.math**: arxiv re-ingest with math.* subject filter.
- Source candidates: `ccdv/arxiv-classification` (filter to math subset) OR
  fetch directly from `https://export.arxiv.org/oai2` with category-set
  parameter
- Estimated 22h at ~25 facts/sec for ~2M math facts
- Output to `data/substrate_state/arxiv_math_2m/` (separate dir; no contention
  with existing arxiv_2m)

Could run in parallel with the rest of Tier-1 (WordNet / PenTreebank /
ConceptNet / etc.). Doesn't need to be serialized.

## What I'm NOT changing

- arxiv_ingest.py source-priority order -- left as-is for the ML use case;
  any math fix should be additive (new --math-only flag or new script)
- arxiv_2m output dir -- preserved
- No other corpus impact

## When this runs

Per your INGEST_APPROVAL sequence:
- Day 3-4 of post-Stage-A schedule (after WordNet/PenTreebank/ConceptNet/etc.
  are done) was the slot you allocated for arxiv math re-ingest "if missing."
  Confirmed missing; the slot stands.

## Cross-references

- Your INGEST_APPROVAL refinement 1: notes/research_to_testbed_INGEST_APPROVAL_2026-06-10.md
- Probe script + result: tools/probe_arxiv_subjects.py (commit 8b350790)
