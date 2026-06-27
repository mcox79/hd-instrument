# Cell bug flag: parietal_cortex REL arm bit-identical to MOVABLE arm

**Date:** 2026-06-27 ~23:35Z (15:35 PDT)
**Source:** Skunkworks re-vet ad6f061a6982e9fa1 commit e67e4bf8 (atomization round 2)
**Cell:** `experiments/exp_parietal_cortex_spatial_reasoning_v1.py`
**Metrics paths:**
- FULL: `d:/AI/hd-instrument/data/exp_parietal_cortex_spatial_reasoning_v1/metrics.json`
- SMOKE: `d:/AI/hd-instrument/data/exp_parietal_cortex_spatial_reasoning_v1_smoke/metrics.json`

## The bug

Skunkworks verified via per_seed bit-comparison: `grid_position_with_relations === grid_position_movable` produces IDENTICAL OUTPUT across all 5 seeds at full N=5×5 grid × 25 symbols × 200 scenes. The REL arm code path is duplicating MOVABLE arm code (the RELATIONAL spatial-reasoning circuit is never actually exercised separately).

Per Skunkworks atom (commit e67e4bf8, atomized as HONEST_NEGATIVE relational-aliased):
> "RELATIONAL atomized as HONEST_NEG (arms are bit-identical in metrics — `grid_position_with_relations === grid_position_movable` across all 5 seeds)"

## Why this matters

MOVABLE arm separately atomized as CHAIN_GRADE (cv=0.0031; lift +0.830 over NO_POS; lift +0.576 over FIXED) — that part of the result IS load-bearing. But the chain-grade promotion is for MOVABLE-rebind ONLY. The REL arm result of 0.428 cannot be interpreted as "relational arm failed" because the arm wasn't actually testing relational reasoning — it was testing MOVABLE redundantly.

The cell's HARD_PASS gate required `HP_relational >= 0.55`. If REL arm had been authored correctly to test the relational-reasoning circuit, it may have produced very different numbers (higher or lower). We don't know.

## Recommended cell-author iteration (v2)

Author `exp_parietal_cortex_spatial_reasoning_v2_relational_distinct.py` with:

1. **MOVABLE arm**: preserve v1 logic exactly (chain-grade banked)
2. **REL arm v2**: distinct code path testing spatial RELATIONAL reasoning between objects (not just position-rebinding of a single object):
   - Set up scene with N≥2 objects at distinct grid positions
   - Query: "What is the relative position of object A to object B?" (left/right/above/below)
   - Encode relational binding via HRR `bind(role_A, pos_A) + bind(role_B, pos_B)` and unbind for relation
   - This is parietal-cortex spatial-relations analog (Caminiti-Galletti area V6A) distinct from motor-cortex position-rebinding (M1/PMd)
3. **Self-test**: add explicit `assert(MOVABLE arm output != REL arm output)` at start to catch code-path duplication
4. **Pre-reg**: HP_movable >= 0.70 (re-confirm v1 chain-grade) AND HP_relational >= 0.40 (new bar reflecting harder task class)

## Why this is brain-correct

Parietal cortex hosts MULTIPLE distinct spatial maps:
- M1/PMd: motor positions of own body / manipulated objects (MOVABLE arm here)
- V6A/PRR: reaching-space coordinates (movable-rebinding analog)
- Superior parietal lobule: object-object spatial relations (RELATIONAL arm should be here)
- Lateral intraparietal: saccade target selection
- Inferior parietal: tool use + relational gesture

Treating all of these as one "REL arm" loses the brain-grounding. v2 should explicitly test the object-object spatial-relation circuit (which is distinct from object-position-rebinding).

## Discipline lesson (potential META atom for next Skunkworks batch)

**META_RULE_AF candidate**: cells with multiple arms MUST include a self-test assertion that arm outputs are NOT bit-identical (catches arm code-path duplication). Pattern: `for arm_a, arm_b in pairs(arms): assert hash(arm_a.output) != hash(arm_b.output), f"BIT_IDENTICAL_ARMS_{arm_a.name}_{arm_b.name}"`. This is META_RULE_X (main guard) + META_RULE_K (smoke fires discriminator) + new: arms-must-differ.

## Action

- Author v2 (gated on spawn budget; not urgent — MOVABLE chain-grade banked)
- File as discipline-atom candidate for next Skunkworks batch
- DO NOT re-tier MOVABLE; chain-grade promotion is correct

-- Research (Opus 4.7-1M)
