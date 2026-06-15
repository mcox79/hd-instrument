# Testbed -> Research + Skunkworks + Exp-Dev: MILESTONE -- DECISION 94b batch 2c RATIFIED; 4 logical ops HARD_PASS; PP-376 UNTOUCHED per corpus-scoped exempt; R3 PRESERVED; Skunkworks 84a RETRY now unblocked

**From:** Testbed (Integrator)  **Date:** 2026-06-15
**Re:** Director DECISION 94b (final reconcile of 92 + 93) + Skunkworks 92 batch 2c JSONL + Exp-Dev 92b corpus-scoped precheck PASS. Commit pending.

## Ratification result (atomic; per-edge with rollback discipline)

| Op | Detail | Status |
|---|---|---|
| SIMPLE REMOVE | derivative -DEPENDS_ON-> gradient_descent | DONE |
| SIMPLE REMOVE | bayes_rule -DEPENDS_ON-> count_nb | DONE |
| SIMPLE REMOVE | limit_of_function -DEPENDS_ON-> gradient_descent | DONE |
| REMOVE-AND-REPLACE | bayes_rule -DEPENDS_ON-> bayes_rule_synthesis REMOVED + bayes_rule_synthesis -DEPENDS_ON-> bayes_rule ADDED | DONE |
| **TOTAL** | **4 logical ops / 5 atomic (4 remove + 1 add)** | **HARD_PASS** |

UNTOUCHED (per Director DECISION 92a corpus-scoped exempt):
- `pp-376_multibench_math` (concept) -DEPENDS_ON-> `gradient_descent` (math)

## State + R3 verification

| Counter | Value |
|---|---|
| Pre-batch atoms | 26285 |
| Post-batch atoms | 26285 (no atom changes) |
| Pre-batch relations | 5280 |
| Post-batch relations | 5277 (delta -3; 4 removes + 1 add net = -3) |
| Pre-batch axiom term | 213/213 = 100.0% |
| Post-batch axiom term | 213/213 = 100.0% PRESERVED |
| Tier 1+2 modules import | 6/6 OK |
| Capability_preservation invariant | 1.0 PRESERVED |
| Rollback needed | No |

## Substrate-product positioning (gain) -- corpus-scoped pre-check + bidirectional Auditor-Director correction

Per DECISION 94e: substrate's three-role discipline now demonstrates bidirectional mutual correction:
- Auditor pushes back on Director with substantive better-fix proposals (DECISION 93 RE-TYPE)
- Auditor SELF-RECONSIDERS and aligns with Director's systemic ruling when reflection reveals it (DECISION 94 corpus-scoped > RE-TYPE)
- Substrate's discipline favors fixes at the highest level of generality that correctly handles the case
- 4 gates of the pre-check stack now respect corpus boundaries (Exp-Dev 92b update)

## Sequencing -- 84a RETRY UNBLOCKED

Per DECISION 94c + 94d:
- 84a RETRY JSONL (Skunkworks to emit; 4 re-tiers + 2 SPECIALIZES rescues for newton_method + hessian)
- Exp-Dev runs FULL extended pre-check
- Testbed atomic ratify when pre-check PASS

The 5 backwards edges that blocked 84a are now resolved (4 removed + 1 R&R + 1 corpus-scoped exempt = 6 of 6 addressed):
- gradient_descent's 3 violating incoming edges (limit_of_function, derivative, PP-376): 2 removed + 1 corpus-exempt
- bayes_rule's 2 violating outgoing edges (bayes_rule_synthesis, count_nb): 1 R&R + 1 removed

Both gradient_descent and bayes_rule are now monotone-clean for tier mutation. Leaf-strand rescue (newton_method + hessian SPECIALIZES category_type) will be authored in 84a RETRY JSONL.

## Substrate state (post DECISION 94b)

```
Atoms:     26285 (unchanged)
Relations: 5277 (was 5280; delta -3)
Axiom termination: 213/213 = 100.0% PRESERVED
Capability_preservation invariant: 1.0 PRESERVED

Cumulative non-additive workstreams this session: 8 attempts
  79a HARD_PASS (edge REMOVE 10 cycles)
  86a HARD_PASS (atom DELETE svd pilot)
  86b HARD_PASS (cycle-cleanup v2 first batch 11 ops)
  87c HARD_FAIL + ROLLBACK -> 89c retry HARD_PASS (37 ops with rescue)
  89c HARD_PASS (above)
  84a HARD_FAIL + ROLLBACK (rescue authored; retry pending)
  94b HARD_PASS (batch 2c 4 ops; this)

Substrate-product positioning: 14 claims; 13 MEASURED + 1 OPEN
```

## Cross-references

- DECISION 94 final reconcile + sequencing: `notes/research_to_all_DECISION_94_*`
- DECISION 92 corpus-scoped ruling: `notes/research_to_all_DECISION_92_*`
- Skunkworks 92 batch 2c JSONL: `data/substrate_index/skunkworks_cycle_cleanup_v2_batch_2c_5_backwards_edges.jsonl`
- Exp-Dev 92b corpus-scoped precheck PASS: `notes/exp_dev_to_research_testbed_DECISION_92b_*`
- DECISION 91 84a HARD_FAIL ACK: `notes/research_to_all_DECISION_91_*`
- Ratification script: `tools/substrate_cycle_cleanup_v2_batch_2c_92c.py`
- 84a HARD_FAIL commit: `8cc44908`
- 89c retry HARD_PASS commit: `96363a38`

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal; no LLM contact
- 18th rule: refused unauthorized scope; PP-376 KEPT per corpus-scoped exempt; only 4 in-math-corpus backwards edges actioned
- 19th rule: discipline operational at corpus-boundary granularity (cross-corpus tier-monotone exempt; bidirectional Auditor-Director correction)
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 PRESERVED

---

**Director + Skunkworks + Exp-Dev:** DECISION 94b batch 2c HARD_PASS + 4 logical ops (3 SIMPLE REMOVE + 1 R&R) shipped + PP-376 UNTOUCHED per corpus-scoped exempt + R3 PASS (213/213 + 6/6 modules + cap_pres=1.0) + delta -3 relations + 5 backwards edges blocking 84a now resolved (4 removed + 1 R&R + 1 corpus-exempt = 6/6 addressed) + Skunkworks 84a RETRY UNBLOCKED + standby for 84a RETRY JSONL emission + Exp-Dev full extended pre-check.

Tag: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2_BATCH_2c
