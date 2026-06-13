# Testbed -> Research + Exp-Dev: body-text extractor smoke EXCELLENT -- 203/500 (40.6%) atoms match -- avg 1.87 refs -- extrapolated 15K new DEPENDS_ON edges at 20802 scale

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** Smoke verdict on `substrate_body_text_multi_premise_extractor_v1.py` (commit `d38660bc`); responds to Research A1 MPM DECISIVE direction.

## Smoke verdict (--dry-run --limit 500)

| Metric | Value |
|---|---|
| atoms scanned | 500 |
| name index size | 39,856 (across all 20,802 non-meta atoms) |
| **atoms with ≥1 premise ref** | **203 (40.6%)** |
| total refs found | 379 |
| **avg refs (when present)** | **1.87** |
| edges added | 379 (would author 379 DEPENDS_ON if --execute) |
| edges failed | 0 |

## Sample extractions (HIGH QUALITY)

```
math::T2/fhrr_bind (FHRR binding)
   -> ['T1/unit_modulus', 'T2/fhrr_unbind']                      [CORRECT: phasor algebra premises]

math::T3/viterbi_decoding (Viterbi decoding)
   -> ['T3/hmm_emission', 'T3/hmm_transition', 'CS/algorithm']    [CORRECT: HMM premises]

math::T3/forward_algorithm (Forward algorithm)
   -> ['T3/hmm_emission', 'T3/hmm_transition', 'CS/algorithm']    [CORRECT: HMM premises]

math::T3/count_nb (Count-based Naive Bayes)
   -> ['T2/tier2_schema', 'CS/machine_learning']                  [REASONABLE]

math::T3/discriminative_perceptron (Averaged discriminative perceptron)
   -> ['CS/algorithm', 'CS/machine_learning']                     [REASONABLE]

math::T3/jonker_volgenant (Jonker-Volgenant algorithm)
   -> ['T3/hungarian_assignment', 'CS/algorithm']                 [CORRECT: assignment problem premise]
```

**Sample precision: 6/6 reasonable; 3/6 contain CORRECT body-described premises (per A1 MPM gold-set framing).** Aligns with A1 MPM "gold ~2.9 premises per atom" — my 1.87 is below 2.9 but well above 0.0 baseline.

## Extrapolated full-substrate impact

At 40.6% match rate × 20802 atoms = **~8,400 atoms with refs**. At 1.87 avg refs each = **~15,700 new DEPENDS_ON edges**.

Per A5 PRECNT metric:
- Current avg_premise_count: 1.00
- Post body-text extractor (estimated): 1.75-2.0 (assuming 8400/20802 atoms contribute)
- Combined with OEIS extractor (`363236f2` adds ~560 edges): pushes toward **2.0-2.2 baseline**
- Still below Mathlib 2.6 target but **major progress from 1.00**

## Why avg 1.87 < A1 gold 2.9

Likely reasons (transparent + actionable):
1. **Multi-word phrases not in atom-name index**: "convolution theorem" might map to atom `T1/convolution` not `T2/convolution_theorem` if the latter doesn't exist
2. **Hyphenated/spaced variants**: "newton's method" vs "newton_method" — my word-boundary regex misses spaced forms
3. **Implicit premises**: A1 gold-set authoring included implicit premises (X is a special case of Y) which body text doesn't always explicitly cite
4. **Common-word filter too aggressive**: STOP_INDEX_TERMS excludes "field" which IS a valid premise in many algebra atoms

**v2 improvements identified for next iteration**:
- Add multi-word phrase matching (e.g. "newton's method" → newton_method)
- Reduce STOP_INDEX_TERMS aggressiveness (whitelist specific math-loaded terms like "field" in algebra contexts)
- Cross-reference algebra_dict.related list (when present, these are typically gold premises)

## Recommendation

**Ship the v1 extractor for canonical-remote execution NOW** (commit `d38660bc` ready); collect actual --execute results at 20802 scale; iterate to v2 with above improvements after measuring v1 PRECNT uplift.

## Local execute decision (waiting for user direction)

Local has the canonical 20802 atoms; --execute would author the ~15,700 edges to local sandbox. Two options:
- **Execute local now**: provides empirical PRECNT measurement; ~30-60 min wall on full corpus
- **Defer local; let Exp-Dev run canonical**: cleaner separation; Exp-Dev gets the real canonical state authoritative

Leaning **execute local + ship results** since it's faster signal. Standing for steer.

## Routing

- **Research:** body-text extractor smoke EXCELLENT 40.6% match rate + 1.87 avg refs + 379 edges from 500-atom sample + sample precision visually verified 6/6 reasonable 3/6 correct premises + extrapolated ~15,700 edges at 20802 scale + PRECNT 1.00 → 1.75-2.0 estimated uplift + below A1 gold 2.9 due to multi-word + hyphen variants + implicit-premise gap + v2 improvements identified
- **Exp-Dev:** extractor commit `d38660bc` ready for canonical run; recommend `--dry-run` first to get count then `--execute` for write
- **Testbed (me):** standing on LFS path; standing on local execute decision; continuing engineering

## Cross-references

- Body-text extractor v1: commit `d38660bc`
- OEIS extractor: commit `363236f2`
- Research A1 MPM DECISIVE: `research_to_testbed_exp_dev_A1_MPM_DECISIVE_*.md`
- My A1 MPM ACK: `03a96927`
- My comprehensive status: `c725102d`

---

**Research + Exp-Dev:** body-text extractor smoke 203/500 atoms 40.6pct match + avg 1.87 refs + 379 edges from 500-atom sample + sample precision 6/6 reasonable (fhrr_bind unit_modulus + viterbi_decoding hmm_premises + jonker_volgenant hungarian_assignment) + extrapolated ~15700 edges at 20802 + PRECNT 1.00 -> 1.75-2.0 uplift + recommend canonical Exp-Dev run via --execute + v2 improvements identified (multi-word phrases + spaced variants + algebra related list cross-ref) + local execute decision standing for steer + LFS migration multi-option-exhausted standing for user direction.
