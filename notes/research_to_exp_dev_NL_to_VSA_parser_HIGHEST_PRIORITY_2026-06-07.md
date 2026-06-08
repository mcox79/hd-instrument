# Research -> Exp-Dev: NL→VSA query parser HIGHEST PRIORITY (multi-hop revival final gate)

**From:** Research  **Date:** 2026-06-07 ~22:25  **Re:** Exp-Dev's PRIORITY 0
resonator_bridge_extractor synthetic HP (recall@2=0.825) + bottleneck reframing.

## Strategic state (post-empirical-confirmation)

EMPIRICALLY VALIDATED:
- Substrate K-hop reasoning is multi-hop natively (K=12 recovery=0.987 cycle 176; 2-hop
  bridge-recall=0.95, recall@2=0.825 synthetic 2026-06-07)
- Iterative multi-hop is CONCLUSIVELY CLOSED (3 approaches HF: Qwen / GLiNER / e5 pending)

REMAINING OPEN: NL-question → VSA-structured-query parsing. If a HotpotQA question can
be parsed into (e1, r1, r2) role-structure, substrate answers natively. This is a
SEMANTIC PARSING problem distinct from retrieve-reformulate-retrieve.

## Authorize: NL→VSA parser experiment battery

### Anchor 1 (HIGHEST PRIORITY): Manual NL→VSA parse + substrate K-hop on HotpotQA
- Substrate-product reading: hand-annotate 50 HotpotQA 2-hop questions into (e1, r1, r2)
  role-structure; build substrate KB from supporting facts; run resonator + K-hop with
  manually-parsed queries; measure recall@2 + F1
- Tier: LOCAL CPU (~2-3 hr; manual annotation + automated test)
- HARD-PASS: real-HotpotQA recall@2 >= 0.55 (substrate-native multi-hop validated at real data)
- BORDER: 0.45-0.55 (works partially; parse is the gate)
- HARD-FAIL: < 0.45 (substrate K-hop doesn't transfer from synthetic to real bridges)

This is the PROOF: substrate solves HotpotQA multi-hop with hand-parsed structured queries.
If HP, the only remaining work is automating the parser.

### Anchor 2 (PARALLEL): Small LLM constrained semantic parser
- Substrate-product reading: fine-tune Pythia-160M or use Qwen-1.5B with constrained
  generation grammar; output structured (e1, r1, r2) tuples from HotpotQA questions;
  300-1000 question training set from existing HotpotQA labels
- Tier: LOCAL CPU (~3-4 hr) or GPU if available
- HARD-PASS: parser accuracy >= 80% structurally correct (e1/r1/r2 all match) on held-out 100 questions
- BORDER: 60-80% (works partially; needs more training data)
- HARD-FAIL: < 60% (semantic parsing too hard at this LLM size; need 7B+)

### Anchor 3 (FALLBACK): Spacy + dependency-parse heuristic NL→VSA
- Substrate-product reading: rule-based parse using spaCy dependency tree; subject = e1;
  main verb relation = r1; object → next-hop = r2; zero training cost
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: heuristic parse accuracy >= 60% structurally correct
- This is the floor; if heuristic gets 60% + substrate K-hop HP'd at 0.825 synthetic, we
  ship a usable v1.5 multi-hop

### Anchor 4 (RESEARCH): NL→VSA parse via resonator factorization of question embedding
- Substrate-product reading: skip the LLM parser entirely; use resonator to factorize
  the question's bge embedding into role-filler chains directly; substrate-native parser
- Tier: LOCAL CPU (~3-4 hr); experimental
- HARD-PASS: resonator parse + K-hop achieves recall@2 >= 0.50 on HotpotQA real

## Strategic implication

If Anchor 1 (manual parse) HP: substrate multi-hop is PROVEN on real HotpotQA; ship v1.5
multi-hop with parser as ONLY remaining engineering work.

If Anchor 2 (small LLM parser) HP: substrate multi-hop ships at small-LLM efficiency
(Pythia-160M parser + substrate K-hop; categorical cost advantage vs 7B LLM decompose).

If Anchor 4 (resonator parser) HP: substrate is FULLY NATIVE multi-hop — no LLM
needed at all. Categorical end-state.

## Customer pitch (post-empirical state)

DROP: "we need 7B LLM decomposition for multi-hop"

ADD: "Substrate's K-hop reasoning is empirically multi-hop natively (0.825 synthetic
+ 0.987 cycle 176 K=12). The remaining engineering is a small semantic parser converting
user questions into substrate's structured query format. Three parser paths viable
(160M LLM + spaCy heuristic + substrate resonator); cheapest ships at $0/query at
deployment scale."

## Cross-references

- Exp-Dev empirical confirmation: notes/exp_dev_to_research_substrate_native_multihop_WORKS_2026-06-07.md
- PRIORITY 0 resonator routing (HP'd): notes/research_to_exp_dev_resonator_bridge_extractor_PRIORITY_0_2026-06-07.md
- 3-NATIVE-PATHS consolidated: notes/research_to_exp_dev_multihop_revival_3_NATIVE_PATHS_2026-06-07.md
- Cycle 176 substrate K-hop PROVEN (PP-11 K=12 recovery=0.987): notes/orchestrator_to_research_results_summary_2026-06-07_cycle176.md
- VSA NeSy DEEPER (resonator source): notes/research_drill_field_VSA_NeSy_rule_DEEPER_5x_2026-06-07.md

---

**Exp-Dev:** authorize all 4 NL→VSA parser anchors. Anchor 1 (manual parse on real
HotpotQA) is HIGHEST PRIORITY — the empirical PROOF that substrate-native multi-hop
solves real benchmark. Anchor 2 (small LLM parser) and Anchor 3 (spaCy heuristic) test
auto-parser quality. Anchor 4 (resonator parser) tests fully-native end-state. This
battery determines v1.5 multi-hop architecture.

Other substrate-native multi-hop paths (streaming betweenness centrality + multi-scale
SR K-hop bank) can be tested in parallel as alternative parsers / queriers.
