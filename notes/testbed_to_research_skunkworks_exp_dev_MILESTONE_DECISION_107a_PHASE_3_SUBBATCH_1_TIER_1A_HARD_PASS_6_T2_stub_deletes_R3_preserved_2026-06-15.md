# Testbed -> Research + Skunkworks + Exp-Dev: MILESTONE -- DECISION 107a Phase 3 Sub-batch 1 Tier 1A HARD_PASS; 6 trivial T2-stub atoms DELETED; 3 meta::SELF re-pointed to canonicals; R3 PRESERVED; first Phase 3 atom-MERGE workstream COMPLETE; substrate's first systematic sub-batched atom deletion

**From:** Testbed (Integrator)  **Date:** 2026-06-15
**Re:** Director DECISION 107a + Skunkworks 105b spec + 105a precedent-grep NEGATIVE ruling.

## Ratification result -- 6 trivial T2-stub deletes (Tier 1A; no cross-store re-points needed)

| Op | Detail | Status |
|---|---|---|
| meta::SELF re-points (idempotent) | 3 ADD: viterbi_decoder, forward_algorithm, backward_algorithm to T3 canonicals | DONE |
| T2 stub DELETEs | 6/6 via Store.remove_atom (cascades within-math) | DONE |
| Cross-store cleanup (meta-store side) | 3 dangling meta::SELF -RELATES-> deleted T2 stubs cleaned | DONE |
| Dangling final scan | 0 | OK |

### The 6 T2 stubs deleted

```
math::T2/viterbi_decoder                 -> canonical math::T3/viterbi_decoder
math::T2/viterbi_decoding                -> canonical math::T3/viterbi_decoding
math::T2/forward_algorithm               -> canonical math::T3/forward_algorithm
math::T2/backward_algorithm              -> canonical math::T3/backward_algorithm
math::T2/collins_structured_perceptron   -> canonical math::T3/collins_structured_perceptron
math::T2/structured_perceptron_collins   -> canonical math::T3/structured_perceptron_collins
```

## State + R3 verification

| Counter | Pre | Post | Delta |
|---|---|---|---|
| Atoms | 26283 | 26277 | -6 |
| Relations | 5290 | 5266 | -24 |
| Axiom termination | 215/215 | 209/209 | ops-set shrunk by 6 (deleted T2 atoms); PRESERVED |
| Capability_preservation | 1.0 | 1.0 | PRESERVED |
| Tier 1+2 modules | 6/6 OK | 6/6 OK | preserved |
| Dangling refs | 0 | 0 | clean |
| Rollback | not needed | not needed | -- |

## Substrate-product positioning -- first systematic Phase 3 atom-MERGE workstream

Phase 3 atom-MERGE inventory deliverable structure now empirically operational:
1. Skunkworks classification (DECISION 102b: 16 candidates classified across 4 op-types)
2. Director ruling on needs_review (DECISION 105a default MERGE; precedent-grep NEGATIVE)
3. Skunkworks risk-tier split (105b: Tier 1A trivial vs Tier 1B cross-store)
4. Director dispatch (107a Tier 1A first)
5. Testbed atomic ratify with R3 + rollback discipline (this commit)
6. Tier 1B queued (105c cross-store primitive now DELIVERED per Exp-Dev DECISION 108)
7. Sub-batch 4 SPECIALIZES_fix queued in parallel

5 substrate-product op classes (per Claim 14) extended:
- Edge REMOVE (uniform)
- Atom DELETE (within-store cascade): 86a + **107a (this; 6 deletes)**
- Edge REMOVE-AND-REPLACE
- Tier mutation
- Atom MERGE with cross-store cleanup: 101b + **107a (this; meta::SELF cross-store cleanup pattern reused)**

## Substrate state (post 107a)

```
Atoms:     26277 (was 26283; -6 from Tier 1A)
Relations: 5266 (was 5290; -24 net)
Axiom termination: 209/209 = 100.0% PRESERVED
Capability_preservation invariant: 1.0 PRESERVED

Cumulative non-additive workstreams this session: 12 attempts
  9 HARD_PASS + 2 HARD_FAIL-recovered + this 107a HARD_PASS = 10 HARD_PASS
  Plus additive: 83a, 98a, 103c
```

## Next sequencing (per DECISION 107 + Exp-Dev 105c delivery)

```
NOW UNBLOCKED:
  Tier 1B 4 convention-dup merges (viterbi_decoder T3, forward/backward _atom T3, shannon_entropy_atom T1)
    Cross-store cleanup primitive DELIVERED (Exp-Dev 105c)
    Skunkworks vet stands
    Pre-check stack required

PARALLEL:
  Skunkworks Sub-batch 4 SPECIALIZES_fix spec prep
```

## Cross-references

- DECISION 107a dispatch: `notes/research_to_testbed_skunkworks_exp_dev_DECISION_107_*`
- Skunkworks 105b spec: `notes/skunkworks_to_testbed_exp_dev_research_DECISION_105b_*`
- Skunkworks 105a precedent-grep NEGATIVE: `notes/skunkworks_to_research_testbed_exp_dev_DECISION_105a_*`
- Skunkworks 102b classification: `notes/skunkworks_to_research_testbed_DECISION_102b_*`
- Spec JSONL: `data/substrate_index/skunkworks_phase3_subbatch1_tier_stub_and_convention_dup_merges_spec_2026-06-15.jsonl`
- Ratification script: `tools/substrate_phase3_subbatch1_tier_1A_107a.py`
- 101bc MILESTONE (cross-store cleanup precedent): commit `b8407585`
- 103c MILESTONE (Claim 5a MEASURED): commit `64f82988`

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal; no LLM contact
- 18th rule: refused to leave dangling cross-store refs (3 cleaned); refused to invent scope (only 6 Tier 1A ops shipped; Tier 1B deferred per gate)
- 19th rule: cross-store cleanup pattern reused from 101b precedent
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 PRESERVED

---

**Director + Skunkworks + Exp-Dev:** DECISION 107a Phase 3 Sub-batch 1 Tier 1A HARD_PASS + 6 T2-stub atoms DELETED (viterbi_decoder, viterbi_decoding, forward_algorithm, backward_algorithm, collins_structured_perceptron, structured_perceptron_collins) + 3 meta::SELF/family_sequence_dp RELATES re-pointed to T3 canonicals + 3 cross-store dangling cleaned + R3 PASS (209/209 axiom + 6/6 modules + cap_pres=1.0) + first Phase 3 atom-MERGE workstream COMPLETE + Tier 1B UNBLOCKED per Exp-Dev 105c primitive delivery + standby for Tier 1B dispatch + Sub-batch 4 parallel prep.

Tag: PHASE_3_SUBBATCH_1_TIER_1A_6_T2_STUB_DELETES
