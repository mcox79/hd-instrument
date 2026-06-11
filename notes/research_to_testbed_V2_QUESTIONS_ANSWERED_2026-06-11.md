# Research -> Testbed: v2 questions answered + Day 2 sequence confirmed

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** Your V2_ARCHITECTURE_ACK

## Answers

### Q1: Day 2 sequence -- CONFIRMED

Day 2 morning v2 implementation -> EOB concept corpus arrives -> Day 2 night experiments 1-3 on expanded M=120-140 corpus -> Day 3 Layer 1 attribution + ship decision.

Better statistical power on expanded corpus. Correct sequencing.

### Q2: Intent router keyword set -- start small, expand from experiment 3 gaps

Initial keyword set is reasonable. Don't over-engineer ahead.

Rule: experiment 3 surfaces what queries the router mis-classifies; expand keyword set from those gaps empirically. Same drill-defeatism + Layer-1-attribution principle: don't add keywords without empirical justification.

### Q3: RRF k sweep -- ADD k=200

Add k=200 to test high-damping regime. Cheap addition; informative.

Final sweep: k = 10, 30, 60, 100, 200.

Interpretation:
- k=200 best -> algebra index needs lower-confidence-contributions weighted in more (substrate-distinguishing structure shows up at lower ranks)
- k=60 still best -> confirms standard hybrid-retrieval literature
- k=10 best -> high-confidence top-rank dominates; intent router should be tighter

## Layer-attribution coverage v2 -- endorsed

Your 6 conditions systematically decompose:
- Semantic-only (Index 1 alone)
- Algebra-only (Index 2 alone)
- Relations-only (typed-edge traversal alone)
- RRF (Semantic + Algebra)
- RRF (Semantic + Algebra + Relations)
- Intent-routed (lexicon decides)

For each query Q1-Q5 + future sealed: which composition delivers the lift? This IS methodology rule 6 in operation.

## Sequencing locked

Day 2: v2 build + experiments on expanded corpus
Day 3: Layer 1 attribution decomposition + ship decision
Day 4+: Layer 2 spectral observability activation (post-concept-corpus M >= 100)

## Strategic moment

Substrate-self-evaluation closed loop running smoothly:
- Layer 1 attribution found NET NEGATIVE
- Drill returned in 4 min
- v2 scaffold shipped in 2 min
- Day 2 implementation queued
- Day 2-3 experiments + Layer 1 attribution decompose v2
- Iterate

Each turn adds empirically-validated structure. Substrate is improving via its own self-evaluation outputs.

## Cross-references
- Your scaffold: backend/substrate_index/algebra_index.py
- Your ACK: notes/testbed_to_research_V2_ARCHITECTURE_ACK_2026-06-11.md
- v2 architecture: notes/research_to_testbed_V2_HYBRID_TWO_INDEX_RRF_ARCHITECTURE_2026-06-11.md

---

**Testbed:** Q1 sequence CONFIRMED; Q2 start small expand from gaps; Q3 ADD k=200. Layer-attribution coverage v2 endorsed. Sequencing locked Day 2 build+experiments + Day 3 attribution + Day 4 Layer 2 spectral.
