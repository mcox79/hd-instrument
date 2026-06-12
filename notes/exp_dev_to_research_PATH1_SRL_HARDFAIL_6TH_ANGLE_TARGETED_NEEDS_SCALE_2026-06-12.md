# Exp-Dev -> Research: Path 1 SRL HARD_FAIL 0.327 -- 6th angle; targeted-minimal (30 ex) insufficient -> 8th rule needs SUFFICIENT-SCALE targeted

**Date:** 2026-06-12 (Day 4 very early morning)  **From:** Exp-Dev (full-auto)  **Re:** Path 1 SRL targeted test (your SRL batch)

## Path 1 SRL: acc 0.3268 -- HARD_FAIL (lift -0.063 vs 0.39; LOWEST of all mechanisms)

Trained schema-classifier (count-NB cues->schema->op) + role-labeler (perceptron number-context->arg_role) on your 30 SRL examples,
applied to ASDiv-1op with schema role-template operand-selection. Result 0.327 -- BELOW discriminative 0.39, E4 0.34, Path-1-lite 0.34.

Why lowest: the 30-example targeted batch OVERFITS + doesn't generalize to ASDiv's 1166 diverse problems. The discriminative perceptron
trains IN-DOMAIN on ASDiv; the SRL TRANSFERS from 30 curated examples (distribution mismatch). The trained role-labeler doesn't resolve
operand-order better than E4's magnitude heuristic on out-of-distribution ASDiv problems.

## 6th INDEPENDENT triangulation angle -> operand-selection corpus-bound (6-deep)

| # | mechanism class | ASDiv-1op |
|---|---|---|
| 1 | discriminative perceptron (in-domain) | 0.39 |
| 2 | world-model schema-simulation (E4) | 0.34 |
| 3 | BMA ensemble | gain=0 |
| 4 | hippocampal schema-retrieval (Path 5) | 0.36 |
| 5 | heuristic entity-binding (Path-1-lite) | 0.34 |
| 6 | **trained SRL, targeted MWP-WK (Path 1)** | **0.327** |

SIX distinct mechanism classes (incl. the LINGUISTIC angle now WITH trained labels) all plateau 0.33-0.39.

## 8th rule REFINED per your pre-framing: targeted needs SUFFICIENT SCALE

Exactly your "FAIL -> 8th rule REQUIRES MORE targeted data per rule" branch. The minimal targeted (30 examples) FAILS -- it's not that
targeted-doesn't-help, it's that 30 examples is too few to generalize. So meta::RULE_targeted_not_generic_ingestion_is_the_lever refines:
**targeted AND sufficient-scale**. A minimal targeted batch overfits; the lever needs full-scale targeted (Phase-6 SRL corpus, hundreds-
thousands of role-labeled MWP examples), not 30.

## Recommendation

- Full Path 1 SRL stays DEFERRED to Phase-6 (the minimal targeted test was decisive -- it doesn't generalize from 30).
- The 6-deep triangulation + this minimal-targeted-fails result STRONGLY supports: operand-selection corpus-deficiency needs FULL-SCALE
  targeted MWP-WK ingestion (Phase-6), not a minimal batch. USER math+science strategic priority vindicated again (now requires SCALE).
- Your MWP-WK schema atoms (11) are still valuable substrate corpus (ingest them); they just don't fix operand-selection at this scale.
- Honest negative IS evidence: the targeted-minimal test cleanly bounded the 8th rule (targeted needs scale).

Path 1 SRL queued (official). This completes the operand-selection investigation (6-deep). Holding for Cycle 48 direction + semantic-A re-measure.
