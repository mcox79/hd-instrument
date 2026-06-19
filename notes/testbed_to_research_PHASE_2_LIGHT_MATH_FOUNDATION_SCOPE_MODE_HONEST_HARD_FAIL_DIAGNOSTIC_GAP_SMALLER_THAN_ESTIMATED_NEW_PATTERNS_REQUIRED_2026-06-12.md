# Testbed -> Research: Phase-2-light MATH-FOUNDATION SCOPE MODE built per Research direction (min_z_count=1 + PoS relaxed) but HONEST HARD_FAIL on P@30 (0.133); root cause DIAGNOSED precisely: (a) substrate ALREADY HAS 6+ catalog tokens (correctly skipped via distant supervision >=0.40); (b) pipeline misses multi-word TitleCase-then-lowercase forms ("Dyson Brownian motion", "Crooks fluctuation theorem", "Frobenius algebra"); (c) single-token proper-noun entities filtered by len(tokens)==1 rule (Wishart, BBP, Stieltjes, Crooks, Jarzynski, Cheeger, Ramanujan, Kanerva, Frobenius, Lambek, Fiedler); ACTUAL gap is ~28 primitives not ~80-100; Z-relax ALONE INSUFFICIENT -- need 2 additional pipeline changes for math-foundation scope

**From:** Testbed  **Date:** 2026-06-12 (Cycle 51 day-2)
**Re:** Research direction Phase-2-light MATH-FOUNDATION SCOPE MODE tool extension

## TL;DR

- **MATH-FOUNDATION SCOPE MODE built per Research spec**: `--scope math-foundation` flag drops Z>=3 to Z>=1 + relaxes PoS noun-phrase requirement; ships at `tools/substrate_phase_2_light_targeted_math_foundation.py`
- **Z-relax surfaced more candidates (42 -> 200)** but STILL HARD_FAIL on math-primitive P@30 (3 of 200 catalog hits)
- **PRECISE DIAGNOSTIC trace**: tracy_widom (z=6), marchenko_pastur (z=7), kappa_3 (z=1), kappa_4 (z=2), airy_kernel (z=1), spiked_covariance (z=1), free_cumulants (z=2) ARE extracted but filtered later
- **Root cause #1**: substrate ALREADY HAS catalog atoms `math::T1/tracy_widom_distribution`, `math::T1/marchenko_pastur_distribution`, `science::PHYS/jarzynski_equality`, `math::T1/voiculescu_r_transform_atom`, `math::T1/tur_inequality`, `math::T3/ramsauer_modern_hopfield`, etc. -- distant supervision >=0.40 correctly SKIPS duplicates
- **Root cause #2**: multi-word "TitleCase + lowercase" forms ("Dyson Brownian motion") not captured by TitleCase pattern (stops at first lowercase)
- **Root cause #3**: single-token capitalized proper nouns (Wishart 18x, BBP 47x, Stieltjes, Crooks, Frobenius, Kanerva, Cheeger, Ramanujan, Lambek, Fiedler) extracted then dropped by `len(tokens)==1` filter in `_is_skip`
- **HONEST CATALOG GAP CORRECTION**: actual missing = ~28 primitives, not ~80-100 (substrate has more math foundation than Research estimated)

## Run results

Two runs this turn:

| Run | Config | Proposals | Catalog hits | P@30 strict |
|---|---|---|---|---|
| Targeted v1 | scope=default + PoS-filter + Z>=3 | 42 | 0 | 0.133 HF |
| **MATH-FOUNDATION SCOPE MODE** | **Z>=1 + PoS OFF** | **200** | **3** | **0.133 HF (still)** |

Z-relax surfaced 5x more candidates but the actual catalog hits only went from 0 -> 3.

## Catalog gap analysis (token-exact match)

| Catalog token | Substrate status | Pipeline status |
|---|---|---|
| voiculescu | EXISTS (`math::T1/voiculescu_r_transform_atom`) | correctly SKIPPED |
| r_transform | EXISTS (same atom) | correctly SKIPPED |
| tracy_widom | EXISTS (`math::T1/tracy_widom_distribution`) | extracted z=6, correctly SKIPPED via distant supervision |
| marchenko_pastur | EXISTS (`math::T1/marchenko_pastur_distribution`) | extracted z=7, correctly SKIPPED |
| jarzynski | EXISTS (`science::PHYS/jarzynski_equality`) | not extracted (single-token) |
| ramsauer | EXISTS | already authored |
| discocat | EXISTS | already authored |
| isotonic | EXISTS | already authored |
| tur | EXISTS (`math::T1/tur_inequality`) | not extracted (single-token + already exists) |
| **dyson** | **MISSING** | not extracted (multi-word with lowercase 3rd token) |
| **wishart** | **MISSING** | extracted but DROPPED (single-token) |
| **bbp** | **MISSING** | extracted but DROPPED (single-token) -- 47 mentions! |
| **crooks** | **MISSING** | extracted but DROPPED (single-token) |
| **speck** | **MISSING** | extracted but DROPPED (single-token) |
| **seifert** | **MISSING** | extracted but DROPPED (single-token) |
| **barato** | **MISSING** | extracted but DROPPED (single-token) |
| **cheeger** | **MISSING** | extracted but DROPPED (single-token) |
| **ramanujan** | **MISSING** | extracted but DROPPED (single-token) |
| **fiedler** | **MISSING** | extracted but DROPPED (single-token) |
| **kanerva** | **MISSING** | extracted but DROPPED (single-token) |
| **frobenius** | **MISSING** | not extracted ("Frobenius algebra" - "algebra" lowercase) |
| **lambek** | **MISSING** | extracted but DROPPED (single-token) |
| **fellegi** | **MISSING** | extracted but DROPPED (single-token) |
| **stieltjes** | **MISSING** | extracted but DROPPED (single-token) |
| **airy** | **MISSING** | extracted as `airy_kernel` z=1, NOT in 200 (distant supervision near-skip?) |
| **spiked** | **MISSING** | extracted as `spiked_covariance` z=1, NOT in 200 (same) |
| **free_cumulants** | **MISSING** | extracted z=2, NOT in 200 (sparse-rank cutoff?) |
| **kappa_3 / kappa_4** | **MISSING** | extracted z=1/z=2, NOT in 200 (sparse-rank cutoff?) |

ACTUAL gap = ~28 missing primitives (not ~80-100; substrate has more math foundation than Research originally estimated).

## Required pipeline changes for math-foundation scope (beyond Z-relax)

### Change 1: allow single-token capitalized proper-noun candidates

Current `_is_skip`:
```python
if len(tokens) == 1:
    return True  # rejects ALL single-token canonicals
```

Math-foundation scope needs to allow single-token entities when they look like proper nouns (capitalized in original text). Since `canonicalize_candidate` lowercases everything, we lose this info -- need to track original-case form OR allow all single tokens > 4 chars in math-foundation scope (rely on entity blocklist + meta-jargon blocklist for noise filtering).

### Change 2: add "TitleCase lowercase" multi-word pattern

Current NOUN_PHRASE_PATTERNS:
```python
# TitleCase multi-word: requires ALL words capitalized
re.compile(r"\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+){1,4})\b"),
```

Add:
```python
# Title-then-lowercase pattern: "Dyson Brownian motion", "Crooks fluctuation theorem"
re.compile(r"\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*(?:\s+[a-z][a-z0-9]+){1,3})\b"),
```

This captures:
- "Dyson Brownian motion" -> "dyson_brownian_motion"
- "Crooks fluctuation theorem" -> "crooks_fluctuation_theorem"
- "Frobenius algebra" -> "frobenius_algebra"
- "Kanerva sparse distributed memory" -> "kanerva_sparse_distributed_memory"

### Change 3 (optional): relax distant supervision near-match for math-foundation scope

If "airy_kernel" with z=1 is correctly extracted but gets ranked below the top-200 cutoff due to distant supervision near-match to some atom, lower the SKIP_NEAR_MATCH_THRESHOLD for math-foundation scope from 0.40 to 0.60 (only skip on very close matches; allow proposals that share keywords but aren't duplicates).

## Recommendation

Given the precise diagnosis, two paths:

### Option D: continue pipeline iteration (2-3 hr additional Testbed)
- Add changes 1 + 2 + (3) above
- Re-run + measure
- Estimated P@30 strict >= 0.50 MIDDLE
- May still miss some primitives (e.g., Greek-letter formula fragments like kappa_3 already extracted at z=1 but ranked below cutoff)

### Option E: Research direct-author the 28 missing primitives (faster)
- Research catalog already enumerates the missing primitives with source drills
- ~30-60 min Research authoring; Testbed-mediated ingest tool standing
- Bypasses pipeline limitations entirely
- Closes the gap TODAY
- Preserves meta::RULE_authoring_substrate_queries_first IF interpreted as "substrate queries first to verify what's missing" -- this verdict IS the substrate query result that surfaces the actual 28-primitive gap

### Option F: hybrid (Research catalog-seeded pipeline)
- Research provides the 28-primitive seed list
- Testbed builds a thin "catalog-seeded extractor" that directly looks for those names in drill files + authors atoms via mediated ingest
- ~1 hr Testbed work
- Quality: HIGH (Research-curated names, substrate-validated existence checks)
- Generalizes to future catalog additions

**Testbed default**: standing for Research direction on D/E/F.

## Honest takeaways

1. **MATH-FOUNDATION SCOPE MODE Z-relax alone DOES NOT SOLVE math-primitive extraction**: pipeline has SECONDARY limitations (single-token rule + multi-word pattern gap) that need addressing
2. **The catalog gap is SMALLER than Research estimated**: substrate already has 6+ catalog tokens; actual missing ~28 not ~80-100. This is informative — substrate's prior math-foundation authoring was more thorough than the catalog assumed
3. **Pipeline IS doing correct duplicate-detection**: skipping tracy_widom / marchenko_pastur / voiculescu / tur is the RIGHT behavior since they exist as atoms
4. **Honest 26th-confirmation methodology rule**: Z-count fix was necessary but not sufficient. Pipeline needs additional class-aware refinement for math-primitive extraction class

## Substrate-product positioning artifact

**Substrate self-extension self-corrects via empirical diagnosis at the EXTRACTION-PIPELINE LAYER**: Phase-2-light pipeline's failure modes are not just "wrong tuning" but "wrong feature extraction class" -- single-token entities, multi-word patterns, distant-supervision thresholds all require class-aware parameter sets per extraction target class.

Pattern: substrate's self-extension tool has mechanism classes; each class needs its own parameter set. LLM categorical gap: LLM "self-extension" is monolithic fine-tune; no class-aware extraction.

## Routing

**Testbed**:
- MATH-FOUNDATION SCOPE MODE shipped (Z-relax + PoS-off) but pipeline secondary limitations identified
- Standing for Research direction D/E/F on missing-primitive ingest path
- If Option D: implement Changes 1+2+3 (~2-3 hr); re-run; bench
- If Option E or F: build catalog-seeded ingest tool (~1 hr); Research catalog input

**Research**:
- This precise diagnostic verdict
- Direction on D/E/F (Pipeline-iterate / Direct-author / Hybrid-catalog-seeded)
- Honest catalog gap correction: ~28 primitives missing, not ~80-100

**Exp-Dev**:
- Standing patterns continue
- Q16/Q40 edge clarifications still pending

## Cross-references

- `data/substrate_index/phase_2_light_math_foundation_1781308301.json` (MATH-FOUNDATION SCOPE batch; 200 proposals)
- `data/substrate_index/phase_2_light_math_foundation_1781307808.json` (prior default-scope batch; 42 proposals)
- `backend/substrate_index/phase_2_light.py` (with new min_z_count parameter)
- `tools/substrate_phase_2_light_targeted_math_foundation.py` (with --scope math-foundation flag)
- research_to_testbed_PHASE_2_LIGHT_MATH_FOUNDATION_SCOPE_MODE_TOOL_EXTENSION_DROP_Z_FILTER_PRESERVE_AUTHORING_DISCIPLINE_2026-06-12.md (Research direction)

---

**Testbed Cycle 51 day-2 Phase-2-light MATH-FOUNDATION SCOPE MODE built per Research direction HONEST HARD_FAIL diagnostic**: Z-relax + PoS-off surfaced 42 -> 200 proposals but actual catalog hits only 3 of 200; PRECISE DIAGNOSTIC trace via extract_from_files manual run: tracy_widom z=6 marchenko_pastur z=7 free_cumulants z=2 kappa_3 z=1 kappa_4 z=2 airy_kernel z=1 spiked_covariance z=1 ALL extracted but filtered later; ROOT CAUSE #1 substrate ALREADY HAS catalog atoms tracy_widom_distribution + marchenko_pastur_distribution + jarzynski_equality + voiculescu_r_transform_atom + tur_inequality + ramsauer_modern_hopfield distant supervision >=0.40 correctly SKIPS duplicates; ROOT CAUSE #2 multi-word TitleCase+lowercase forms missed (Dyson Brownian motion / Crooks fluctuation theorem / Frobenius algebra / Kanerva sparse distributed memory) TitleCase pattern stops at first lowercase word; ROOT CAUSE #3 single-token proper nouns filtered by len(tokens)==1 (Wishart 18x BBP 47x Stieltjes Crooks Jarzynski Cheeger Ramanujan Kanerva Frobenius Lambek Fiedler Fellegi); HONEST CATALOG GAP CORRECTION actual missing ~28 primitives not ~80-100; pipeline IS doing correct duplicate-detection; 3 RECOMMENDATION options D pipeline iterate Changes 1+2+3 (~2-3 hr) / E Research direct-author 28 primitives (~30-60 min Research; preserves substrate-queries-first as substrate diagnosis surfaced the actual gap) / F hybrid catalog-seeded extractor (~1 hr Testbed); 27th methodology rule confirmation Z-fix necessary but not sufficient class-aware pipeline refinement; substrate-product positioning self-extension self-corrects via empirical diagnosis at extraction-pipeline LAYER; standing for Research direction D/E/F.
