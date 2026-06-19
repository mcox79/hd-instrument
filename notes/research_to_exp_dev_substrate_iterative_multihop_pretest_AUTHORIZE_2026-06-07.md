# Research -> Exp-Dev: substrate iterative multi-hop pre-test AUTHORIZED (decisive gate)

**From:** Research session
**To:** Exp-Dev (primary) + Testbed (inform; GPU lane)
**Date:** 2026-06-07
**Re:** Substrate iterative multi-hop 3x drill output. Per user multi-hop revival mandate.

## Authorize the decisive substrate_iterative_multihop_pretest_v1

Per drill recommendation: this is THE gate for the 1-2 week integration decision.

### Method
- 50 HotpotQA distractor BRIDGE questions
- Substrate-augmented iterative retrieval architecture:
  - Step 1: Query encoded as bipolar key; substrate retrieves top-K facts (Pattern A; standard)
  - Step 2: Qwen-1.5B identifies BRIDGE ENTITY from retrieved facts
  - Step 3: Substrate unbinds along bridge entity using Pattern B algebra (algebraically
    generates next-hop query candidates)
  - Step 4: K-hop substrate compose retrieves second-hop facts
  - Step 5: Audit chain captures each hop with Merkle proof
  - Step 6: LLM finalizes answer from accumulated multi-hop context

### Measure SEPARATELY (critical for diagnostic)
- Bridge indexing rate (does substrate have the HotpotQA bridge entities indexed?)
- Unbind accuracy (does Pattern B unbind return correct candidates given correct bridge entity?)
- Recall@2 (does top-2 contain both supporting facts?)
- Answer F1 (does LLM produce correct answer given the substrate-retrieved chain?)

### Decision rules

HARD-PASS: recall@2 >= 0.60 (clearly above bge ceiling 0.42; multi-hop revival is real)
  AND bridge indexing rate >= 0.55 (architecture is viable; not just lucky run)
  AND unbind accuracy >= 0.75 (Pattern B algebra works on real bridge entities)

BORDER: recall@2 0.50-0.60 (improvement but ceiling not fully broken)

HARD-FAIL: recall@2 < 0.45 (iterative doesn't help OR bridge indexing rate < 0.40)

### Wall: ~3-4 hours GPU

## Strategic context (combined with encoder ceiling drill)

Both drills converge on multi-hop revival paths:

| Path | P_deflated | Expected recall@2 | Engineering |
|---|---|---|---|
| Encoder upgrade alone (e5-large) | 0.60 | 0.55-0.65 | ~2 days |
| Substrate iterative alone | 0.28 | 0.58 (0.72 upper bound) | 1-2 weeks IF pre-test HP |
| COMPOSED (both) | combined | 0.70+ | composed engineering |

The cheapest resolving test for encoder side: e5-large head-to-head (1-2 hours; already
routed).
The cheapest resolving test for substrate side: THIS pre-test (3-4 hours; this routing).

Both pre-tests in parallel = full multi-hop revival picture in ~4 hours of work.

## Customer pitch unlock magnitude

If THIS pre-test HP + encoder head-to-head HP:
- Customer pitch becomes "substrate BEATS RAG on multi-hop too" — categorical unlock
- Magnitude: +0.10-0.20 F1 on HotpotQA depending on composition
- Closes the cycle 165 "structural ceiling" narrative

If THIS pre-test BORDER + encoder HP:
- Encoder upgrade alone clears 0.55; substrate iterative as v2.0 enhancement
- Customer pitch: "substrate matches RAG on multi-hop with e5-large encoder; iterative composition adds further upside in v2"

If THIS pre-test HF + encoder HF:
- Cycle 165 ceiling verdict stands; multi-hop precision deferred to v2.0+
- Customer pitch stays at current "96% RAG parity on multi-hop"

## 5 crazy options for parallel exploration (per user mandate)

The drill identified 5 crazy options; recommendations:

| # | Crazy idea | P_calibrated | Pre-test cost | Recommendation |
|---|---|---|---|---|
| 1 | Substrate Pattern B as complete retriever (no hop-1 standard retriever) | 0.08 | Skip | Post-v2.0 research only |
| 2 | LLM-substrate dual-mode voting per hop | --- | Future | After base architecture HP |
| 3 | Substrate-augmented bridge entity PREDICTION | --- | Future | Closes bridge indexing gap |
| 4 | Sleep defrag pre-computes common multi-hop chains offline | --- | Future | Links to sleep defrag (today's HP) |
| 5 | Substrate-native multi-hop end-to-end (Tier 4 multi-hop curriculum) | --- | Future | Tier 4 v2.0 path |

For v1.1: focus on base architecture pre-test. Crazy ideas 3 and 4 are v1.5/v2.0
candidates if base architecture passes.

## Cross-references

- Substrate iterative multi-hop 3x drill: notes/research_drill_substrate_iterative_multihop_3x_2026-06-07.md
- Drill Exp-Dev handoff (full pre-test spec): notes/exp_dev_handoff_research_substrate_iterative_multihop_2026-06-07.md
- Encoder ceiling 2x drill (parallel encoder side): notes/research_drill_retrieval_encoder_ceiling_alternatives_2x_2026-06-07.md
- Encoder head-to-head routing: notes/research_to_exp_dev_encoder_e5large_headtohead_AUTHORIZE_2026-06-07.md
- Cycle 158 Pattern B unbind acc=1.0: scorecard
- Cycle 166 hotpot_3baseline at 96%% RAG parity: scorecard

---

**END.**

**Exp-Dev / Testbed:** authorize substrate_iterative_multihop_pretest_v1 (3-4 hr GPU).
Apply HARD-PASS / BORDER / HARD-FAIL autonomously per spec. File verdict with
SEPARATELY-MEASURED bridge indexing rate + unbind accuracy + recall@2 (the diagnostic
breakdown matters more than the headline number).
