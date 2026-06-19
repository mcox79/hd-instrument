# Research -> Testbed: atom_candidates source #5 substrate-eval-references-unknown-math-term -- technical spec

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** Q2 from Findings 09 = YES add source #5; spec follows

## Purpose

Surfaces math atom candidates from research notes / drill outputs / PP rows that cite math primitives by name when substrate corpus has no such atom. Complement to source #2 (math primitive with no concept user).

Source #2 finds existing-math-no-concept; source #5 finds cited-math-no-atom. Together cover both directions of the math/concept join.

## Expected discoveries (Day 2 first run)

From memory + drill scan today, citations to math primitives substrate doesn't yet have:
- F4 / kappa_4_rect / Marchenko-Pastur / Tracy-Widom / spectral_gap (free-probability drill memory)
- GHRR / DisCoCat (substrate v4.0 lineage triangle memory; substrate-product noncommutative + categorical foundation)
- BOCPD (full-research-ledger drill bounded changepoint)
- Reed-Solomon (substrate v3.2 engineered wrapper drill, FHRR parity)
- Dyson-Brownian-motion (next-drill candidate beyond free-prob)
- conformal-prediction / isotonic-calibration (uncertainty-quantification memory)
- Chu-Liu-Edmonds (already accepted but appears in citations more than once -> confidence boost)

Order-of-magnitude: 10-20 new candidates Day 2 first run; 3-7 sustained per week.

## Algorithm

```python
def substrate_eval_references_unknown_math_term(corpus, source_paths, math_token_pattern):
    """
    Surfaces math atom candidates from citation analysis.
    Inputs:
      corpus -- substrate corpus (current atoms)
      source_paths -- list of file paths to scan (research notes + drill outputs + PP-row descriptions)
      math_token_pattern -- regex/heuristic for identifying math primitive names in text
    Output:
      candidates -- list of {name, confidence, sources, suggested_tier}
    """
    existing_math = {a.name for a in corpus.atoms if a.partition == 'math'}
    cited_names = defaultdict(list)  # name -> list of source paths
    for path in source_paths:
        text = read_text(path)
        for name in extract_math_token_candidates(text, math_token_pattern):
            if name not in existing_math:
                cited_names[name].append(path)
    candidates = []
    for name, sources in cited_names.items():
        if len(sources) < MIN_REFERRERS:  # default 2; tunable
            continue
        confidence = min(0.90, 0.40 + 0.10 * min(5, len(sources)))
        suggested_tier = infer_tier_from_context(name, sources)  # heuristic; see below
        candidates.append({
            'name': name,
            'confidence': confidence,
            'sources': sources,
            'suggested_tier': suggested_tier,
        })
    return sorted(candidates, key=lambda c: -c['confidence'])
```

## Math token extraction heuristic (rough)

Per-source heuristic candidates:
- Mixed-case CamelCase + capital starting letter following math context: `Marchenko-Pastur`, `Tracy-Widom`, `Chu-Liu-Edmonds`, `Reed-Solomon`
- snake_case in mathematical context with operator-like suffixes: `spectral_gap`, `kappa_4_rect`, `bocpd_changepoint`
- Acronyms in math context: `F4`, `GHRR`, `FHRR`, `BOCPD`, `RMT`, `PMI`

Implementation suggestion: build a starter math-name corpus (~200 names) from existing math atoms + lit-search drill outputs; extract tokens; filter by:
1. Token starts with capital letter OR contains underscore OR is acronym
2. Token appears within 50 chars of math-context keywords (algorithm, theorem, lemma, distribution, primitive, operator, etc.)
3. Token is not in stoplist (common English words + non-math jargon)

Source files to scan (Day 2 first run):
- All `notes/research_drill_*.md` (40+ files)
- All `notes/research_to_*.md` (routing notes)
- All `notes/exp_dev_to_research_*.md` (Exp-Dev findings)
- C:\Users\marsh\.claude\projects\d--AI\memory\*.md (memory entries)
- data/substrate_index/*.jsonl description fields

## Suggested-tier heuristic

```
if name appears with "axiom" or "field" or "space" context: T1
if name is operator-style (bind, compose, normalize): T2
if name is algorithm-style (algorithm, decoding, inference): T3
default: T2 (algebraic primitive most common gap)
```

## False-positive controls

- MIN_REFERRERS=2 (tunable; default avoids one-off mention)
- Stoplist of common math words: `theorem`, `lemma`, `proof`, `function`, `equation`
- Reject names matching existing math atoms case-insensitively + edit-distance <= 2 (catches typos)
- Reject names containing only digits or only punctuation

## Integration with existing atom_candidates pipeline

Add to `backend/substrate_index/atom_candidates.py`:
```python
def all_candidate_sources(corpus, source_paths=None):
    if source_paths is None:
        source_paths = default_source_paths()
    candidates = []
    candidates.extend(unmet_decomposes_to(corpus))
    candidates.extend(math_atom_has_no_concept_user(corpus))
    candidates.extend(algebra_centroid_orphan(corpus))
    candidates.extend(substrate_eval_references_unknown_math_term(corpus, source_paths))
    # repeated_name_candidates deferred to v2
    return candidates
```

## Provenance

Each source #5 candidate gets `provenance: "substrate_eval_references_unknown_math_term"` + `source_paths: [...]`. Research validation step uses source_paths to verify the math primitive is genuinely needed (not just a passing mention).

## Closed-loop expectations

Day 2 first run -> N candidates surfaced -> Research validates k accepted -> Research hand-authors k math atoms -> Testbed ingests -> substrate math atom count grows -> Layer 1 attribution re-rank -> potentially additional concept atoms now possible via source #2.

5-tier progression target: source #5 + source #2 together drive Tier 3 (substrate-self-extension) sustained for Tier 3 -> Tier 4 gate measurement.

## Cross-references

- Findings 09: notes/testbed_to_research_INDEX_FINDINGS_09_TIER3_ATOM_CANDIDATES_TYPE_A_2026-06-11.md
- FINDINGS_09 validation: notes/research_to_testbed_FINDINGS_09_TIER3_ATOM_CANDIDATES_VALIDATION_2026-06-11.md
- Two-axes memory: semantic-vec vs content-references
- 5-signal-types operational memory
- atom_candidates module: backend/substrate_index/atom_candidates.py

---

**Testbed:** Source #5 substrate-eval-references-unknown-math-term spec ready. Algorithm + token heuristic + tier heuristic + false-positive controls + integration sketch. Day 2 first run expected 10-20 candidates; specific predictions F4/kappa_4_rect/Marchenko-Pastur/Tracy-Widom/GHRR/DisCoCat/BOCPD/Reed-Solomon. Closed-loop substrate-self-extension sustained measurement begins.
