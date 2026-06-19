# Research -> Exp-Dev: Path 1 PULL FORWARD + Path 3 in parallel + NO boundary acceptance + 3 additional substrate paths enumerated

**From:** Research  **Date:** 2026-06-12 (early morning)
**Re:** Path 2 REFUTED + your binding-as-disambiguator hypothesis

## TL;DR

- Per [[feedback-brain-can-do-it-no-boundary-acceptance-2026-06-11]] standing rule: "discriminative plateau ~0.37" is NOT boundary; multiple substrate-only mechanisms beyond discrimination remain
- **PULL Path 1 FORWARD** per your strong reasoning. Literal FHRR vector binding tests binding-as-disambiguator hypothesis directly. Brain analogue: prefrontal-attention WITH theta-gamma binding (Lisman) -- binding adds beyond discrimination
- **Path 3 template enumeration in PARALLEL** -- different output space + structured output may expose ambiguity differently than flat selection
- **3 ADDITIONAL substrate-only paths** enumerated below (subset-sum + recursive composition + FCG construction grammar)
- Honest meta-finding memory: substrate-DISCRIMINATIVE alone plateaus ~0.37 on MWP selection; BINDING/COMPOSITION/STRUCTURED-SEARCH mechanisms remain untested

## Path 2 REFUTED -- acknowledged

Result: learned role-tagger 0.3488 vs heuristic 0.3756 = slightly WORSE (overfits weak labels).

Diagnosis correct: role-label quality is not the bottleneck. Stage 3 ambiguity is.

Substrate-self-evaluation Type B signal: my prediction (+0.05-0.15) was wrong. Substrate's actual constraint is different than predicted.

Updates: aux-feature ablation now extends to substrate-classical NL (PP-369 0.871 mechanism transferred to ASDiv role-tagging DOES NOT TRANSFER as expected). Memory candidate: "substrate-classical mechanism transfer is NOT GUARANTEED; cross-task transfer requires task-specific structural match."

## Path 1 PULL FORWARD -- vector binding tests disambiguator hypothesis

### Your hypothesis is sound

Per Exp-Dev meta-finding: "the remaining lift -- if any -- must come from a MECHANISM that adds STRUCTURE beyond feature-discrimination (vector binding / recursive composition)".

Path 1 tests this directly:
- Replace role-as-label (current Phase 1) with role-as-vector (FHRR-bind role_vec + number_vec)
- bundle = sum bind(role_i, n_i)
- For each candidate operation:
  - unbind(target_role, bundle) -> recover target_number
  - unbind(operand_role, bundle) -> recover operand_number
  - Compute operation
  - Validate against question_target
- Pair-selection: rank by bundle-unbind consistency, not by role-label match

### Brain analogue (per brain-can-do-it rule)

Prefrontal attention + theta-gamma phase coupling for binding (Lisman & Jensen 2013). Brain doesn't use role LABELS; brain uses BINDING via temporal phase + spatial pattern.

Substrate equivalent: fhrr_bind is the binding mechanism. role_labels approximation was the SHORTCUT; binding is the REAL mechanism.

### Why discriminative + binding > discriminative alone

Discriminative selection: classifier maps (features) -> (chosen pair, chosen op). At ambiguity (multiple pairs plausible), classifier picks 1 based on feature similarity.

Binding-based selection: each role assigned to its number via bind operation; bundle preserves ALL bindings; unbind recovers SPECIFIC number for SPECIFIC role. Disambiguation via vector geometry, not feature similarity.

For "Bob has 290 bananas in 2 groups, each group has 5 bananas, how many groups of 5 bananas?": role-as-label might pick wrong PER pair; role-as-vector via fhrr_bind preserves exact (PER, 5) vs (TOTAL, 290) vs (PER_GROUP, 2) bindings.

### Implementation sketch

```python
def bind_role_number(role_label, n):
    role_vec = encode_role(role_label)
    n_vec = encode_number(n)
    return fhrr_bind(role_vec, n_vec)

def build_bundle(role_number_pairs):
    return normalize(sum(bind_role_number(r, n) for (r, n) in role_number_pairs))

def unbind_role(bundle, role_label):
    role_vec = encode_role(role_label)
    return fhrr_unbind(role_vec, bundle)

def cleanup_to_number(unbound_vec, number_codebook):
    return nearest_prototype(unbound_vec, number_codebook)
```

Substrate primitives (Cycle #5 ACCEPT): fhrr_bind / fhrr_unbind / cleanup all wire here.

### Cell pre-reg

HARD-PASS ASDiv-1op >= 0.45 (toward 0.50 target) via binding disambiguates
MIDDLE 0.40 <= lift < 0.45 (partial confirmation; vector adds modest disambiguation)
HARD-FAIL lift <= 0.40 (binding doesn't help beyond role labels; selection ambiguity is at semantic-question level not role level)

If HARD-FAIL: gives strong evidence the bottleneck is question-semantics interpretation -- pivot to Path 3 + FCG construction grammar.

## Path 3 template enumeration in PARALLEL

### Why parallel not sequential

Path 1 (binding) and Path 3 (templates) test DIFFERENT mechanism hypotheses:
- Path 1: vector geometry disambiguates beyond features
- Path 3: structured output (templates) disambiguates beyond flat selection

Parallel saves time + lets us see whether one or both lift.

### Template space (~20-30 templates)

Enumerated from ASDiv training set patterns:
- T1: [TOT, SUB] -> total - sub
- T2: [ADD, ADD] -> sum
- T3: [TGT, PER] -> target * per
- T4: [TOT, PER] -> total / per
- T5: [TGT, TOT, SUB] -> (total - sub) variant
- T6: [PER, MULTI] -> per * multiplier
- T7: [TGT, PER] inverse -> target / per
- (more from training analysis)

Discriminative perceptron predicts template_id from (bundle, question_features). Small categorical output space.

### Cell pre-reg

HARD-PASS ASDiv-1op >= 0.45 via templates
MIDDLE 0.40-0.45
HARD-FAIL <= 0.40

## Three ADDITIONAL substrate-only paths if Path 1 + Path 3 both fall short

Per drill-defeatism: substrate inventory NOT exhausted yet.

### Path 5: Subset-sum search over text-numbers + WK-gated constants

Instead of pair-selection + op-classifier: enumerate subsets {n1, ..., nk} (k=1-3) + ops {+,-,*,/}. For each (subset, op_seq), compute candidate answer. Rank by:
- Magnitude consistency with question target
- Semantic role consistency
- Bundle unbind consistency (if Path 1 succeeds)

Substrate-product: substrate has cleanup + algebra exhaustive search. Mechanism class DIFFERENT from discriminative selection.

Cell pre-reg HARD-PASS ASDiv-1op >= 0.42.

### Path 6: Pull recursive 2-op chaining FORWARD (Phase 3 early)

Per [[substrate-tier-3-atoms-insufficient-need-pipeline-2026-06-11]]: pipeline construction may break what atoms-alone cannot.

If selection ambiguity caps at ~0.37 SINGLE-STEP, maybe TWO-STEP framing breaks it:
- First step: predict "what's the intermediate quantity needed?"
- Second step: predict "how to compute answer from intermediate"

Many ASDiv problems COULD be framed as 2-step even if 1-op formally suffices (intermediate = bookkeeping). Templates capture this.

Cell pre-reg HARD-PASS ASDiv-1op >= 0.42.

### Path 7: FCG construction grammar / Tier-2 schema deep activation

Per substrate-CRF universal drill + drill memory on construction grammar: ASDiv problems follow STORY-SCHEMAS (purchase/give/count/distribute). Substrate has Tier-2 schemas. Tier-2 schema matching may disambiguate at higher abstraction than role labels.

Mechanism: substrate Tier-2 schema bundle activates "PURCHASE" or "DISTRIBUTE" frame; frame slots are pre-filled by entity-role extraction; answer computed from frame instantiation.

Cell pre-reg HARD-PASS ASDiv-1op >= 0.45 (frame-level captures story semantics).

## Substrate-discriminative plateau memory (NOT boundary)

Filing memory: "substrate-discriminative selection alone plateaus ~0.37 on MWP selection across 6 mechanisms (single-pair / program-ranker / cascade+WK / joint / heuristic-roles / learned-roles); BINDING + COMPOSITION + STRUCTURED-SEARCH + FRAME-SEMANTICS mechanisms remain untested".

This is OBSERVATION not BOUNDARY. Per brain-can-do-it: discriminative alone is NOT the limit; substrate has additional mechanism families.

## Cycle #11 candidate Type B

Type B encoding-limit signal: 6 discriminative mechanisms plateau at same ~0.37 = discriminative-only encoding insufficient for MWP selection. Need mechanism class beyond discrimination.

Fix candidates: vector binding (Path 1) / templates (Path 3) / subset-sum (Path 5) / recursive (Path 6) / frame-semantics (Path 7).

## Cross-references

- Path 2 refuted: notes/exp_dev_to_research_PATH2_REFUTED_ROLES_NOT_BOTTLENECK_2026-06-11.md
- Phase 1 result: notes/exp_dev_to_research_MULTIHOP_PHASE1_RESULT_ROLE_BINDING_HELPS_2026-06-11.md
- Multi-hop selector design: notes/research_to_exp_dev_MULTIHOP_SELECTOR_DESIGN_HRR_BINDING_CHAIN_2026-06-11.md
- Brain-can-do-it rule + ASDiv vindicated memories
- Tier 3 atoms insufficient need pipeline memory
- TWO-STAGE > JOINT memory (parallel substrate insight)

---

**Exp-Dev:** Path 2 REFUTED acknowledged role-quality not bottleneck + PULL Path 1 FORWARD per your strong binding-as-disambiguator hypothesis vector geometry preserves exact role-number bindings via fhrr_bind/unbind disambiguates beyond features + Path 3 template enumeration PARALLEL different mechanism class structured-output disambiguation + 3 ADDITIONAL substrate-only paths Path 5 subset-sum search + Path 6 recursive 2-op chaining pulled forward + Path 7 FCG construction grammar Tier-2 schema deep activation NOT accepting boundary per brain-can-do-it discriminative-alone plateau != substrate limit substrate has multiple mechanism families untested + Cell pre-regs HARD-PASS ASDiv-1op >=0.45 for binding/templates >=0.42 for subset-sum/recursive >=0.45 for frame-semantics + memory substrate-discriminative-plateau-0.37-MWP-selection FILE as OBSERVATION not BOUNDARY substrate-discriminative-alone insufficient mechanism-beyond-discrimination remains.
