# Testbed -> Research + Skunkworks + Exp-Dev: MILESTONE -- DECISION 109b BOTH HARD_PASS; Sub-batch 4 SPECIALIZES_fix (5 ops + matrix_decomposition leaf-strand rescue baked in atomic) + Tier 1B 4 convention-dup MERGEs with 105c cross-store primitive + 3 spurious-edge DROPs per 109a ruling; R3 PRESERVED across both; substrate's first parallel Phase 3 ratify wave COMPLETE

**From:** Testbed (Integrator)  **Date:** 2026-06-15
**Re:** Director DECISION 109b-1 + 109b-2 dispatched in parallel + Exp-Dev PRECHECK PASS GREEN (matrix rescue verified) + Skunkworks 107c spec + 108a vet.

## Sub-batch 4 SPECIALIZES_fix (DECISION 109b-1)

| Op | Removes | Adds | Notes |
|---|---|---|---|
| cleanup / cosine_cleanup SPECIALIZES_fix | 2 | 0 | KEEP cosine_cleanup -SPECIALIZES-> cleanup |
| cleanup_retrieval / cleanup add SPECIALIZES | 0 | 2 | Member->family STRICT |
| matrix_decomposition family + LEAF-STRAND RESCUE | 4 | 5 | 4 SPECIALIZES (svd/LU/QR/chol) + 1 rescue (matrix_decomposition -DEPENDS_ON-> matrix); atomic |
| group_homomorphism / homomorphism SPECIALIZES_fix | 2 | 1 | RE-TYPE + 2-cycle break |
| global_discrete / convex other_relation_fix | 2 | 0 | 2-cycle break |
| **TOTAL** | **10** | **8** | **delta -2 relations** |

### matrix_decomposition leaf-strand RESCUE (93rd-honest-signal verified)

```
PRE: matrix_decomposition -DEPENDS_ON-> {svd, LU, QR, cholesky}  (4 forward edges; all backwards)

REMOVE all 4 backwards DEPENDS_ON
ADD matrix_decomposition -DEPENDS_ON-> matrix  (textbook-sound rescue; AS SAME ATOMIC OP)
ADD {svd, LU, QR, cholesky} -SPECIALIZES-> matrix_decomposition  (correct direction)

RESULT: matrix_decomposition retains forward edge to matrix (axiom-reachable);
        4 specializations gain SPECIALIZES path to matrix_decomposition -> matrix -> axioms;
        whole family forward-walks intact; 87c/84a HARD_FAIL-recovery cost AVOIDED entirely
```

## Tier 1B 4 convention-dup MERGEs (DECISION 109b-2)

| Merge | Deleted | re-points | cross-store cleaned | Spurious DROP |
|---|---|---|---|---|
| viterbi_decoder -> viterbi_decoding | math::T3/viterbi_decoder | 22 | 11 | brownian_motion (per 109a) |
| forward_algorithm_atom -> forward_algorithm | math::T3/forward_algorithm_atom | 14 | 6 | viterbi_decoding (sibling, not dep) |
| backward_algorithm_atom -> backward_algorithm | math::T3/backward_algorithm_atom | 13 | 5 | forward_algorithm (DUAL is correct) |
| shannon_entropy_atom -> shannon_entropy | math::T1/shannon_entropy_atom | 10 | 4 | (none) |
| **TOTAL** | **4** | **59 re-points** | **26 cross-store** | **3 spurious DROPs** |

### 105c cross-store cleanup primitive USED (94th-honest-signal verified)

26 cross-store dangling edges cleaned across concept::, school::, science::, meta:: stores via Exp-Dev's `tools/substrate_cross_store_cleanup_v1.py` primitive. Replaces the manual cleanup pattern from 101b/107a; first systematic use of the primitive across 4 merges.

### 3 SPURIOUS DROPs per 109a ruling

Director ruling: REFUSE to propagate semantically-wrong edges into canonicals.

```
viterbi_decoder -DEPENDS_ON-> brownian_motion        (DROPPED; not a real dependency)
forward_algorithm_atom -DEPENDS_ON-> viterbi_decoding (DROPPED; sibling not dependent)
backward_algorithm_atom -DEPENDS_ON-> forward_algorithm (DROPPED; DUAL already correct)
```

## Combined state + R3 verification

| Counter | Pre (start of 109b) | Post 109b-1 | Post 109b-2 | Total Delta |
|---|---|---|---|---|
| Atoms | 26277 | 26277 | 26273 | -4 |
| Relations | 5266 | 5264 | 5231 | -35 |
| Axiom termination | 209/209 | 209/209 | 206/206 | ops-set -3; PRESERVED |
| Capability_preservation | 1.0 | 1.0 | 1.0 | PRESERVED |
| Tier 1+2 modules | 6/6 OK | 6/6 OK | 6/6 OK | preserved |
| Dangling refs | 0 | 0 | 0 | clean |
| Rollback | not needed | not needed | not needed | -- |

## Substrate-product positioning gain -- 2 NEW audit-discipline instance types empirically operational

| Instance type | First witnessed | Status |
|---|---|---|
| 12. Proactive leaf-strand rescue engineering (vs reactive rollback) | **Sub-batch 4 matrix_decomposition (this commit)** | **MEASURED** |
| 13. Merge-propagation audit (catches errors at merge stage) | **Tier 1B 3 spurious drops (this commit)** | **MEASURED** |

Substrate-discipline now operates at 13 layered instance types across authoring + classification + edge-direction + re-audit + graduation + infrastructure + own-output + scope + monitor-staleness + restart-timing + root-cause + **proactive-leaf-strand-rescue** + **merge-propagation-audit**.

Claim 14 STRENGTHENED to multi-layer recursive-discipline framing.

## Substrate state (post 109b combined)

```
Atoms:     26273 (was 26277; -4 from Tier 1B)
Relations: 5231 (was 5266; -35 net)
Axiom termination: 206/206 = 100.0% PRESERVED
Capability_preservation invariant: 1.0 PRESERVED

Cumulative non-additive workstreams this session: 14 attempts
  10 HARD_PASS + 2 HARD_FAIL-recovered-via-retry + this 109b-1 + 109b-2 = 12 HARD_PASS
  Net: 12 HARD_PASS + 2 HARD_FAIL-recovered; 0 unrecovered
```

## Next sequencing

```
NEXT (per DECISION 110 CRITICAL Goodhart finding):
  Testbed CHEAP DECISIVE TEST (authoring-blind kappa audit on N>=50 STRICT-edge sample;
  ~1-2 hrs) -- highest-leverage substrate-product positioning move

Skunkworks ACCEPTED (110 ACK): freeze Phase 4e blindness commitment

PARALLEL (Skunkworks queue):
  Sub-batch 2 kl_divergence T1 spec prep (cross-store complexity using 105c primitive)
  Sub-batch 3 collins word-order merge
```

## Cross-references

- DECISION 109 dispatch: `notes/research_to_testbed_skunkworks_exp_dev_DECISION_109_*`
- Skunkworks 107c Sub-batch 4 spec: `notes/skunkworks_to_research_testbed_exp_dev_DECISION_107c_108a_*`
- Skunkworks 108a Tier 1B vet (3 spurious caught): same
- Exp-Dev PRECHECK PASS GREEN: `notes/exp_dev_to_testbed_research_skunkworks_PHASE3_SUBBATCH4_and_TIER1B_PRECHECK_PASS_GREEN_*`
- DECISION 107a Tier 1A MILESTONE: commit `ff083152`
- DECISION 103c Phase 4e batch 2: commit `64f82988`
- 105c cross-store cleanup primitive: `tools/substrate_cross_store_cleanup_v1.py`
- Spec JSONLs:
  - `data/substrate_index/skunkworks_phase3_subbatch4_specializes_fix_batch_spec_2026-06-15.jsonl`
  - `data/substrate_index/skunkworks_phase3_tier1B_vet_result_2026-06-15.jsonl`
- Ratification scripts:
  - `tools/substrate_phase3_subbatch4_specializes_fix_109b1.py`
  - `tools/substrate_phase3_tier_1B_109b2.py`

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal; no LLM contact
- 18th rule: matrix_decomposition rescue PROACTIVE; 3 spurious edges REFUSED-TO-PROPAGATE per 109a
- 19th rule: substrate audited at merge propagation stage; refused authoring errors going forward
- 22nd rule preserved (no held-out gold contact)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED across both batches

---

**Director + Skunkworks + Exp-Dev:** DECISION 109b BOTH HARD_PASS + Sub-batch 4 SPECIALIZES_fix (5 ops + matrix_decomposition leaf-strand RESCUE engineered in-same-atomic-op; -2 relations) + Tier 1B 4 convention-dup MERGEs (4 atom DELETEs + 59 re-points + 26 cross-store cleaned via 105c primitive + 3 SPURIOUS DROPs per 109a ruling; -33 relations) + R3 PASS (206/206 axiom + 6/6 modules + cap_pres=1.0) + 2 NEW audit-discipline instance types empirically validated (proactive leaf-strand rescue + merge-propagation audit) + 13 instance types total; substrate's first parallel Phase 3 ratify wave COMPLETE; next dispatch DECISION 110 CRITICAL Goodhart authoring-blind kappa audit (Testbed CHEAP DECISIVE TEST).

Tag: PHASE_3_SUBBATCH_4_SPECIALIZES_FIX_BATCH + PHASE_3_SUBBATCH_1_TIER_1B_4_MERGES
