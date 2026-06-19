# Research -> Exp-Dev: multi-hop revival follow-on experiment battery (per user "expand on this")

**From:** Research  **Date:** 2026-06-07  **Re:** Cycle 175 substrate_iterative_multihop_pretest
+0.04 lift validation. User explicit: "let's expand on this for sure."

## 5 follow-on experiments — multi-hop revival via composition

Cycle 175 validated the iterative architecture (+0.04 lift). Per orchestrator: "encoder
upgrade is the gating fix." Per bridge-ID categorical closure 3x drill: composition of
multiple paths projected to 0.65-0.71 P(2hop). These 5 experiments test each composition
path empirically.

### Experiment 1 (PRIORITY 1; cheapest): Iterative + bge-large
~1-2 hr CPU. Same iterative-multihop protocol with bge-large (cycle 166 recall@2=0.516)
instead of cycle 175's weaker encoder.

HARD-PASS: recall@2 >= 0.55 (encoder upgrade alone clears HP gate).
BORDER: 0.45-0.55.
HARD-FAIL: < 0.45.

### Experiment 2 (cheap): Iterative + GLiNER + pre-seeded bridge dictionary
~3-4 hr CPU. Iterative architecture + GLiNER bridge entity extraction (concept-entity
blind spot fix; 0 training cost) + pre-seeded bridge dictionary (300K HotpotQA +
2WikiMultiHopQA labels; 60-70% coverage of in-domain bridges at deployment).

HARD-PASS: recall@2 >= 0.55 (v1.1 cheap-wins composition validated).

### Experiment 3: Iterative at K=3 hops
~2-3 hr CPU. Same iterative protocol but K=3 (not just K=2). Tests whether deeper
iteration extracts more recall.

HARD-PASS: recall@2 >= 0.50 (deeper iteration adds value).
BORDER: 0.45-0.50.

### Experiment 4: Iterative + cross-encoder bridge ranker (Stage 2 cascade)
~3-4 hr CPU. Add MiniLM-22M cross-encoder bridge ranker per bridge-ID categorical
closure 3x drill (Stage 2; SIGIR 2025 lit shows +5-10 nDCG over bi-encoder).

HARD-PASS: recall@2 >= 0.55.

### Experiment 5: Iterative + per-domain encoder pattern
~4-6 hr CPU. Test whether cycle 174 per-domain encoder lift (PubMedQA 67% → 97.1% with
PubMedBERT swap) generalizes to iterative multi-hop. Use domain-matched encoder per
question type (medical → PubMedBERT; legal → LegalBERT-equivalent; general → bge-large).

HARD-PASS: per-domain iterative recall@2 >= 0.55 averaged across domains.

## Compositions to test if individual experiments BORDER

If Experiment 1 BORDER but Experiment 2 HP: encoder upgrade + bridge dictionary
compose for v1.1 ship.

If both BORDER but Experiment 4 HP: cross-encoder ranker adds the missing precision.

If Experiment 5 HP: per-domain encoder selection is the production architecture for
multi-hop AND single-hop (already validated for single-hop via cycle 174).

## Strategic context (for results synthesis)

- Cycle 175 iterative pretest = COLD START + WEAKEST ENCODER + NO NER CASCADE
- +0.04 lift on this floor = architecture works
- Each of these 5 experiments adds ONE upgrade
- Bridge-ID categorical closure 3x predicted: v1.1 0.65 / v1.5 0.67 / v2.0 0.71 P(2hop)
- These experiments map to that trajectory

## Total cost

~14-20 hours CPU (parallelized 4-6 hours wall time). $0 cloud.

## Cross-references

- Cycle 175 iterative pretest LVH #262: notes/orchestrator_to_research_results_summary_2026-06-07_cycle175.md
- Honest reframing: notes/research_to_exp_dev_iterative_multihop_HONEST_REFRAMING_2026-06-07.md
- Bridge-ID categorical closure 3x: notes/research_drill_bridge_id_categorical_closure_3x_2026-06-07.md
- Bridge-ID augmentation routing: notes/research_to_exp_dev_bridge_id_AUGMENTATION_3_cheap_wins_2026-06-07.md
- Cycle 174 PubMedBERT cross-axis: notes/orchestrator_to_research_results_summary_2026-06-07_cycle174.md
- Encoder ceiling alternatives 2x: notes/research_drill_retrieval_encoder_ceiling_alternatives_2x_2026-06-07.md

---

**Exp-Dev:** authorize all 5 follow-on experiments per blanket authorization. Experiment 1
is cheapest + most decisive single test. Total ~14-20 hr CPU. Multi-hop revival stays
OPEN; encoder + composition path predicted to reach 0.65-0.71 P(2hop) per bridge-ID
categorical closure 3x trajectory math.
