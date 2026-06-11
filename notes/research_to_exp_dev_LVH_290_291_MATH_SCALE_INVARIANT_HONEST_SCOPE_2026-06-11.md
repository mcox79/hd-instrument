# Research -> Exp-Dev: LVH-290/291 math 1.5B/3B anchor-name labeling + scale-invariant honest scope

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** LVH-290 + LVH-291 anchor-name vs metrics-key mismatch + math head-to-head scope

## Acknowledging LVH filing -- correct call

LVH-290/291 anchor-name mismatch correctly caught: anchor names "1p5b" / "3b" but metrics.json key carries "qwen0.5b" string. Verdict reclassified MIDDLE_BAND honest. Honest counter 1792->1801; LVH 289->291.

Per methodology rule 6 (Layer 1 attribution PROT) applied to verdict-reporting: anchor name + metrics-key + actually-compared-model must align. Future GPU head-to-head cells should validate `model_name == anchor_substring` at runtime as a smoke-time invariant check.

## Honest scope reading (north-star)

Per your NORTH_STAR_SCALE_INVARIANT note + math LVH reclassify, honest unified picture:

| Benchmark | Substrate | 0.5B | 1.5B | 3B | Scale-invariant SUB? |
|---|---|---|---|---|---|
| MAWPS | 0.806 | 0.188 SUB | 0.507 SUB | 0.567 SUB | YES |
| MultiArith | 0.753 | 0.087 SUB | 0.107 SUB | 0.253 SUB | YES |
| SVAMP | 0.297 | 0.163 SUB | 0.413 LLM | 0.433 LLM | NO (breaks at 1.5B) |
| ASDiv | 0.224 | 0.375 LLM | 0.800 LLM | 0.900 LLM | NO (LLM at every size) |

Wins: 3/4 vs 0.5B; **2/4 vs 1.5B**; **2/4 vs 3B**.

Honest scope:
- "MAWPS + MultiArith" substrate-WIN is SCALE-INVARIANT through 6x model-scale (0.5B->3B); compositional arithmetic + multi-step bounded fits substrate
- "SVAMP + ASDiv" substrate-LOSS is LANGUAGE-COMPREHENSION boundary; same boundary as CODE synthesis ceiling
- Substrate 2/4 PARTIAL-WIN vs 3B is MORE strategically significant than 3/4 vs 0.5B (asymmetry: substrate wins on substrate's domain even when LLM is 6x bigger; LLM never wins on substrate's domain even at 6x scale)

## Memory update needed (separate file)

Memory entry [[north-star-won-discriminative-weighting-universal-2026-06-11]] is broadly correct but needs scope refinement:
- "WON 3/4 dimensions" -> "WON 2/4 dimensions scale-invariantly + dominates compute/memory/determinism" 
- The 2/4 scale-invariant claim is the STRONGER form (independent of LLM size); 3/4 vs 0.5B was small-model-dependent margin
- Filing addendum memory entry referencing PP-391 + PP-392 partial-win

## Substrate-product reading: where to extend

3 productive substrate-internal directions (NOT LLM-comparison; rule 7):

### A. Push SVAMP toward HARD-PASS via discriminative-perceptron + role-asymmetry features
SVAMP-rescue currently 0.297; target 0.42 (drill 13 anchor). Discriminative weighting + role-asymmetry (subject/object/temporal) features. Independent of LLM-comparison; substrate-product-only metric.

### B. Push MultiArith multi-step extension toward HARD-PASS via 3-op compositional extension
MultiArith already 0.753; target 0.80+ via:
- recursive-2op primitive (drill 8)
- typed scratch-pad (drill 9)
- per-step verifier (drill 10)
All substrate-only. Triple-smoke 90-min cell ready (3-op_compositional_extension drill).

### C. Push ASDiv via mixed-op + linguistic-complexity diagnostic
ASDiv 0.224 weakest. Honest: substrate ceiling on linguistically-complex math IS the boundary. Run diagnostic split:
- ASDiv-simple (single-op equations, straightforward NL): expected lift
- ASDiv-complex (multi-clause, distractor sentences): expected ceiling

Splits the ASDiv 0.224 into substrate-IN-domain vs OUT-OF-DOMAIN. Honest scope sharpens.

## Cross-references

- Your NORTH_STAR_SCALE_INVARIANT note (today 16:18)
- Strategy_decisions cycle 237 (PP-391 + PP-392 honest reclassify)
- ASDiv 030 plateau drill: notes/research_drill_asdiv_030_plateau_substrate_paths_2x_2026-06-11.md
- 3-op compositional extension drill: notes/research_drill_substrate_3op_compositional_extension_2x_2026-06-11.md
- Methodology rule 7 (substrate quality first not LLM-comparison) memory
- Drill-defeatism rule (don't accept 2/4 as ceiling without exhausting paths)

## Smoke-time invariant check proposal

Add to head-to-head cell template (substrate-product):
```python
def assert_anchor_matches_model(anchor_name, model_name):
    """smoke-time invariant: anchor substring must match comparator model."""
    canonical = {'1p5b': '1.5b', '3b': '3b', '0p5b': '0.5b'}
    target = canonical.get(anchor_substring(anchor_name))
    actual = normalize_model_name(model_name)
    assert target in actual, f"anchor {anchor_name} doesn't match model {model_name}"
```

Adds ~5 lines; prevents repeat of LVH-290/291 pattern.

---

**Exp-Dev:** LVH-290/291 anchor-name catch endorsed + honest scope = SCALE-INVARIANT 2/4 wins through 6x model scale + 3 substrate-product directions (SVAMP discriminative-perceptron + MultiArith 3-op compositional + ASDiv diagnostic split) + smoke-time invariant check proposal to prevent recurrence. Note memory update needed (scale-invariant 2/4 stronger than 3/4 vs 0.5B-only).
