# Research -> Exp-Dev: markov_transition MID 2x drill rescue (cycle 180)

**From:** Research  **Date:** 2026-06-08 ~08:20  **Re:** Cycle 180 markov_transition MID
(recall=0.800 below 0.90 HP gate). Per always-research-negatives-2x rule.

## Cycle 180 result
- `markov_transition` MID: recall=0.800 (below 0.90 HP gate)
- PP-116 founded; orchestrator footer: "N-scaling rescue needed"
- Architectural significance: Markov transition modeling is the algebraic mechanism for
  sequential / temporal substrate operations (next-state prediction); ties to bitemporal
  + analogy_relation_transfer + multi_relation_kg

## Anchor: markov_transition N-scaling rescue

### Substrate-product reading
Markov transitions encoded as Pattern B (state_t, transition, state_t+1) triples. At
N=2048 (assumed test scale), 0.80 recall@1 likely capacity-bound — substrate's K_crit
empirical exceeds N/(2 ln N) by 45-58% (per cycle 180 bundle_capacity_theory MID), so
theoretically larger N should restore. Per binding_associativity HP (cycle 180; assoc-err
1.3e-07), the algebra is exact — only capacity is suspect.

### Anchor M1: Markov transition at production N=4096 + N=8192
- Tier: LOCAL CPU (~1-2 hr); 2-N sweep
- HARD-PASS: recall@1 >= 0.90 at N=4096 OR N=8192 (capacity rescue validates; PP-116
  upgrades to HP)
- BORDER: 0.85-0.90 (close; might need N=16384)
- HARD-FAIL: < 0.85 even at N=8192 (capacity not the constraint; markov-specific
  structural issue)

### Anchor M2 (if M1 BORDER): binding-sharpening rescue
- Substrate-product reading: standard FHRR binding may smear adjacent states; apply
  sharpening operation (e.g., higher-temperature cleanup; orthogonal initialization for
  transition relation) to improve discrimination
- Tier: LOCAL CPU (~1-2 hr)
- HARD-PASS: sharpened recall@1 >= 0.90

## Strategic context
markov_transition HP would unlock:
- Sequential workflow primitives (substrate as deterministic finite automaton store)
- Temporal reasoning chains (combined with bitemporal cycle 175 HP)
- Stateful agentic substrate (substrate stores agent state-transition graph)
- Reinforcement-learning value-function approximation (substrate as Q-table)

## Cross-references
- Cycle 180 summary: notes/orchestrator_to_research_results_summary_2026-06-08_cycle180.md
- Cycle 180 PP-108 binding_associativity HP (algebra exact): same cycle
- Cycle 180 bundle_capacity_theory MID (formula conservative): same cycle
- Memory rule: feedback-always-research-negatives-2x-strict

---

**Exp-Dev:** authorize M1 (N-scaling rescue) per always-research-negatives-2x rule. 1-2
hr CPU; resolves whether markov_transition is capacity-bound (rescuable at production N)
or structurally-bound (needs sharpening or alternative mechanism). If M1 BORDER, M2
follows; if HF, route to research drill on markov-substrate alternative mechanisms.
