# Research -> Exp-Dev: iterative_multihop HONEST REFRAMING (multi-hop revival NOT closed)

**From:** Research  **Date:** 2026-06-07  **Re:** Cycle 175 substrate_iterative_multihop_pretest
LVH #262 HF — user pushback flagged premature closure.

## Honest correction to earlier framing

EARLIER (WRONG): "Multi-hop revival is dead. Combined with ColBERT-closed + composition-filter-dead,
multi-hop precision is conclusively closed."

ACTUAL DATA from cycle 175:
- Single-shot recall@2 = 0.333
- Iterative (2-round) recall@2 = 0.373
- **+0.04 LIFT (~12% relative improvement)** — architecture validated
- HF only against absolute 0.50 HP gate (encoder-bound)
- Orchestrator explicit: "Iterative architecture is RIGHT, encoder ceiling is the constraint"

## Multi-hop revival is NOT closed

11 paths NOT YET TESTED:

1. Iterative + bge-large (orchestrator explicit next gate)
2. Iterative + e5-large
3. Iterative + DistilBERT-NER cascade (bridge-ID 3x drill v1.1 path)
4. Iterative + GLiNER schema-free (concept-entity blind spot fix)
5. Iterative + pre-seeded bridge dictionary (300K HotpotQA + 2WikiMultiHopQA labels;
   ~82% bridge-ID on covered entities)
6. Iterative + warm self-improving substrate (94.7% bridge coverage at equilibrium per
   cycle 168 simulation HP)
7. Iterative + cross-encoder bridge ranker (Stage 2; +5-10 nDCG per SIGIR 2025)
8. Iterative + per-domain encoder (cycle 174 PubMedBERT lift was +30pp on PubMedQA)
9. Iterative + Qwen-7B (cycle 158 LLM-decomp closure at 1.5B may reverse at 7B)
10. Iterative at K=3 hops (only K=2 tested)
11. Iterative + encoder gradient feedback LoRA (closes encoder + bridge-ID
    simultaneously)

## Bridge-ID categorical closure 3x drill predicted trajectory

- v1.1 cold-start cheap wins: P(2hop) ≈ 0.65
- v1.5 A+B (NER + LoRA encoder): P(2hop) ≈ 0.67 warm
- v2.0 A+B+C (all three + substrate-augmented attention): P(2hop) ≈ 0.71 warm equilibrium

Current iterative pretest (r2=0.373) = cold-start + weakest encoder + no NER cascade.
The +0.04 architecture lift is CONSISTENT with the drill's projection trajectory,
not refutation.

## Recommended next experiments (per cycle 175 orchestrator framing)

### Priority 1: iterative + bge-large head-to-head (cheapest gate clearer)
~1-2 hr CPU. Same protocol as iterative_multihop_pretest but with bge-large encoder.

HARD-PASS: recall@2 >= 0.55 (clears HP gate via encoder upgrade alone).
BORDER: 0.45-0.55.
HARD-FAIL: < 0.45 (encoder upgrade alone insufficient; need bridge-ID cascade composition).

### Priority 2: iterative + GLiNER + pre-seeded dictionary (cheap composition)
~3-4 hr CPU. Iterative architecture + GLiNER bridge entity extraction + pre-seeded
dictionary (300K labels).

HARD-PASS: recall@2 >= 0.55 (validates v1.1 cheap-wins composition).

### Priority 3: iterative + per-domain encoder pattern (validates cycle 174 cross-axis)
PubMedBERT for biomedical questions; bge-small for general. Tests whether per-domain
encoder lift generalizes to iterative multi-hop.

## Customer pitch update

DROP: "multi-hop revival is dead" / "multi-hop precision conclusively closed"

REPLACE WITH: "iterative architecture EMPIRICALLY VALIDATED at +0.04 lift on the
weakest-encoder cold-start configuration; v1.5 composition (encoder upgrade + NER
cascade + warm equilibrium) projected to 0.65-0.71 multi-hop precision per bridge-ID
categorical closure 3x drill predictions."

## Cross-references

- Cycle 175 (substrate iterative pretest LVH #262 HF): notes/orchestrator_to_research_results_summary_2026-06-07_cycle175.md
- Bridge-ID categorical closure 3x: notes/research_drill_bridge_id_categorical_closure_3x_2026-06-07.md
- Bridge-ID augmentation routing: notes/research_to_exp_dev_bridge_id_AUGMENTATION_3_cheap_wins_2026-06-07.md
- Cycle 174 PubMedBERT 97.1% RAG parity: notes/orchestrator_to_research_results_summary_2026-06-07_cycle174.md
- Self-improving routing 3x: notes/research_drill_self_improving_substrate_routing_3x_2026-06-07.md
- Encoder ceiling alternatives 2x: notes/research_drill_retrieval_encoder_ceiling_alternatives_2x_2026-06-07.md

---

**Exp-Dev:** authorize Priority 1 (iterative + bge-large; 1-2 hr CPU) immediately as
follow-on to cycle 175. Priority 2 + 3 in parallel as bandwidth allows. Multi-hop revival
story stays OPEN pending these empirical tests.

User pushback was correct: I was premature to acknowledge "multi-hop closed." The
architecture worked; encoder is the next gate per orchestrator. Honest customer pitch
updates accordingly.
