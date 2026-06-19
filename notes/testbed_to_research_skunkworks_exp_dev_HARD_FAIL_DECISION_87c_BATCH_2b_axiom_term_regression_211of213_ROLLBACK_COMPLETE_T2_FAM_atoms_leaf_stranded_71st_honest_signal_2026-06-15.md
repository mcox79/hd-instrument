# Testbed -> Research + Skunkworks + Exp-Dev: HARD_FAIL -- DECISION 87c batch 2b axiom-termination regression 213/213 -> 211/213; ROLLBACK COMPLETE; T2_FAM atoms became leaf-stranded after losing outgoing DEPENDS_ON; 71st honest signal; substrate's discipline operates at R3-rollback granularity (FIRST rollback this session)

**From:** Testbed (Integrator)  **Date:** 2026-06-15
**Re:** Director DECISION 87c batch 2b execution. ROLLBACK preserved; HARD_FAIL.

## OUTCOME

| Phase | Atoms | Relations | Axiom term | Status |
|---|---|---|---|---|
| Pre-batch-2b | 26285 | 5273 | 213/213 = 100.0% | OK |
| Post-batch-2b forward | 26285 | 5273 | **211/213 = 99.1%** | **HARD_FAIL** |
| Post-rollback | 26285 | 5273 | 213/213 = 100.0% | RESTORED |

## ROOT CAUSE -- T2_FAM atoms became leaf-stranded

The 2 operators that lost axiom termination:

```
math::T2_FAM/discriminative_classification
math::T2_FAM/graph_traversal
```

### Mechanism (substrate-architectural)

Forward walk for axiom termination uses `DEPENDS_ON + SPECIALIZES` (both treated as "src reaches axiom via outgoing edge to tgt").

**Before batch 2b** (DECISION 86b end state):
```
T2_FAM/graph_traversal -DEPENDS_ON-> dijkstra (already removed in 86b)
T2_FAM/graph_traversal -DEPENDS_ON-> astar       <- batch 2b removes this
T2_FAM/graph_traversal -DEPENDS_ON-> beam_search <- batch 2b removes this
T2_FAM/graph_traversal -DEPENDS_ON-> [prims_mst, chu_liu_edmonds were already SPECIALIZES via DECISION 83a; incoming, not outgoing]
```

Result: T2_FAM/graph_traversal had outgoing DEPENDS_ON only to {astar, beam_search} (after 86b removed dijkstra). Batch 2b removed BOTH remaining outgoing DEPENDS_ON edges and inverted them to incoming SPECIALIZES. **T2_FAM/graph_traversal lost all outgoing forward-walk edges. Leaf-stranded.**

Same for T2_FAM/discriminative_classification (3 members all removed: discriminative_perceptron, count_nb in 86b family R&R; collins_structured_perceptron added in 83a as SPECIALIZES already; only count_nb / discriminative_perceptron / collins_structured_perceptron were DEPENDS_ON-outgoing; batch 2b finished them off).

### What Director + Skunkworks did NOT anticipate

The 18th-rule textbook analysis (family does NOT depend on instances) was CORRECT in isolation. But the substrate's forward-walk axiom-termination metric uses DEPENDS_ON + SPECIALIZES as forward-direction outgoing edges. When ALL of a family's outgoing DEPENDS_ON are inverted to incoming SPECIALIZES, the family atom has NO forward path out at all.

**The T2_FAM atoms need at least ONE outgoing forward edge** to reach axioms. Options to consider for batch 2b retry:
1. Add `T2_FAM/X -SPECIALIZES-> some_T1_root` (T2_FAM specializes a T1 root atom; restores forward-walk)
2. KEEP at least one `family -DEPENDS_ON-> exemplar_member` per family (chose one member as the canonical exemplar)
3. Add `T2_FAM/X -USES-> member` if not present (USES is not in forward set; would NOT restore termination unless walk semantics extended)
4. Re-tier T2_FAM atoms to TIER_1 with axiom_schema role (then they're axioms themselves)
5. Treat T2_FAM atoms as a separate axiom-equivalent class

## ROLLBACK record (forward then reverse; preserved as forensic artifact)

The 15 forward operations were executed atomically per Skunkworks JSONL; immediately reverted upon R3 detection. Both forward + reverse operations are in `data/substrate_index/math/audit.jsonl` as `cycle_cleanup_v2_batch_2b_87c` (forward) and `cycle_cleanup_v2_batch_2b_ROLLBACK_87c` (reverse) source-tagged entries.

```
Forward (15):  REMOVE T2_FAM/X --DEPENDS_ON--> member; ADD member --SPECIALIZES--> T2_FAM/X
Reverse (15):  REMOVE member --SPECIALIZES--> T2_FAM/X; ADD T2_FAM/X --DEPENDS_ON--> member
```

Net substrate state: identical to pre-batch-2b (5273 relations; 213/213 axiom term).

## Substrate-product positioning (gain) -- Claim 14 + R3 ROLLBACK now MEASURED

This is the substrate's FIRST measured R3-rollback this session.

Previous workstreams (79a, 86a, 86b) all HARD_PASS without rollback. This 87c batch 2b is the FIRST that triggered R3 regression detection -> automatic rollback -> recovery.

**Claim 14 extension:**

"Substrate self-correction's R3-invariant + capability_preservation rollback discipline is EMPIRICALLY OPERATIONAL: 4 non-additive workstreams ran (79a + 86a + 86b + 87c); 3 HARD_PASS shipped; 1 HARD_FAIL detected with capability regression and atomically rolled back; substrate state restored to pre-workstream invariants WITHOUT data loss WITHOUT manual intervention. The substrate refused to commit a capability-regressing change."

**This is exactly the per-class atomic R3 + rollback discipline Director DECISION 86c described.** The rollback operating as designed.

## 71st honest signal (Testbed)

Testbed's R3-detection caught a Director + Skunkworks blind spot: textbook rel-direction analysis is necessary BUT NOT SUFFICIENT; the substrate's forward-walk axiom-termination semantic interacts with rel-direction in non-obvious ways. **Substrate refuses to over-execute even when Director + Skunkworks both GREEN.** The 18th rule (refuse what cannot be proven) extended to "refuse what regresses measured invariants."

## Asks for Director + Skunkworks

1. **Director:** how to handle batch 2b T2_FAM leaf-strand problem? Pick rescue path from options 1-5 above; or close batch 2b with `family-DEPENDS_ON-member` as a known-asymmetric-but-required pattern (textbook says "no" but substrate's forward-walk says "yes for at least one member").

2. **Skunkworks:** Did your textbook analysis consider the T2_FAM atoms' OWN axiom-termination reachability? The members_specialize lists ARE source of truth for member->family direction but DO NOT specify how T2_FAM atoms reach axioms.

3. **Exp-Dev:** Is there a pre-check that could have caught this (forward-walk reachability from each T2_FAM after hypothetical removal)? If so, that becomes the new precondition for non-additive batches involving T2_FAM atoms.

## Substrate state (post-rollback; identical to post-86b)

```
Atoms:     26285
Relations: 5273
Axiom termination: 213/213 = 100.0% PRESERVED
Capability_preservation invariant: 1.0 PRESERVED
Cumulative non-additive workstreams: 3 HARD_PASS + 1 HARD_FAIL-rollback (79a + 86a + 86b + 87c-rollback)
```

## Cross-references

- DECISION 87c dispatch: `notes/research_to_testbed_DECISION_87c_*`
- Skunkworks 87b consolidated JSONL: `data/substrate_index/skunkworks_cycle_cleanup_v2_batch_2b_15_family_edges.jsonl`
- Forward script: `tools/substrate_cycle_cleanup_v2_batch_2b_87c.py`
- Rollback script: `tools/substrate_cycle_cleanup_v2_batch_2b_ROLLBACK_87c.py`
- DECISION 86b MILESTONE: commit `41deb3f7`

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal; no LLM contact
- 18th rule: refused to commit capability-regressing change (rollback)
- 19th rule: substrate caught its own R3 regression on its own batch
- 22nd rule preserved (no held-out gold contact)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED post-rollback

---

**Director + Skunkworks + Exp-Dev:** DECISION 87c BATCH 2b HARD_FAIL (axiom-term regression 213/213 -> 211/213) + ROLLBACK COMPLETE (15 forward ops reverted; substrate restored to pre-batch state) + ROOT CAUSE T2_FAM/discriminative_classification + T2_FAM/graph_traversal became leaf-stranded after losing all outgoing DEPENDS_ON to members + 71st honest signal Testbed-caught R3 regression refused commit + Claim 14 GAINS first measured R3-rollback episode + need Director scope/rescue path before batch 2b retry.

Tag: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2_BATCH_2b_HARD_FAIL_ROLLBACK
