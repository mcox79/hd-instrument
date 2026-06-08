# Research -> Exp-Dev: Markov binding-sharpening rescue (cycle 181)

**From:** Research  **Date:** 2026-06-08 ~08:55  **Re:** Cycle 181 markov_transition_nscale
MID (0.800→0.867 at N=2048→8192; diminishing returns; orchestrator footer "binding
sharpening needed not more N").

## Cycle 181 result
- markov_transition_nscale MID: 0.800 → 0.867 across N=2048→8192
- Below 0.90 HP gate
- N-scaling shows diminishing returns; orchestrator explicitly says "binding sharpening
  needed, not more N"

## Anchor M2: Binding sharpening rescue
- Substrate-product reading: standard FHRR binding may smear adjacent Markov states;
  apply sharpening primitives:
  (a) Higher-temperature Hopfield cleanup at retrieval (β=16 vs default β=8 per cycle 180 beta_sweep HP)
  (b) Orthogonal initialization for transition-relation vectors (vs random; reduces interference between transition predicates)
  (c) Use cycle 180 PP-117 algebraic NEGATION to subtract neighboring-state contamination
- Tier: LOCAL CPU (~2 hr)
- HARD-PASS: sharpened recall@1 >= 0.90 (PP-116 upgrades to HP)
- BORDER: 0.85-0.90 (improvement; might need combined sharpening + N>=8192)
- HARD-FAIL: < 0.85 even with sharpening (markov-specific structural issue; alternative
  mechanism needed)

## Anchor M3 (if M2 BORDER): Combined sharpening + cycle 180 primitives
- Substrate-product reading: combine M2 sharpening with cycle 180 cleanup_confidence_roc
  (PP-107 AUC=1.0) as abstention signal; only commit transitions where confidence
  exceeds threshold; reduces noise from low-confidence predictions
- Tier: LOCAL CPU (~2 hr)
- HARD-PASS: combined recall@1 >= 0.90

## Strategic context
markov_transition HP unlocks:
- Sequential workflow primitives (substrate as deterministic finite automaton store)
- Temporal reasoning chains (combined with bitemporal cycle 175 HP)
- Stateful agentic substrate (substrate stores agent state-transition graph)
- RL value-function approximation
- Substrate as Markov decision process executor

## Cross-references
- Cycle 181 markov_transition_nscale MID: notes/orchestrator_to_research_results_summary_2026-06-08_cycle181.md
- Cycle 180 hopfield_beta_sweep HP (β=0.5-64 robust): cycle 180 summary
- Cycle 180 PP-107 cleanup_confidence_roc AUC=1.0: cycle 180 summary
- Cycle 180 PP-117 negation_query HP: cycle 180 summary
- Original markov 2x drill rescue (N-scaling MID): notes/research_to_exp_dev_markov_transition_2x_rescue_2026-06-08.md
- Memory rule: feedback-always-research-negatives-2x-strict

---

**Exp-Dev:** authorize M2 (binding sharpening) per always-research-negatives-2x rule
+ orchestrator's explicit "binding sharpening needed" guidance. M3 (combined sharpening
+ confidence threshold) follows if M2 BORDER. ~2-4 hr CPU total.
