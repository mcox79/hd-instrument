# Pre-registration: substrate-self-index v2 architecture experiments

**Filed:** 2026-06-11 late evening (before running)
**For execution:** 2026-06-12 (Day 2 night, after concept corpus + schools corpus + cross-corpus relations land at M=120-140 atoms)
**Owner:** Testbed
**Per:** deep-self-evaluation Hazards Extension item #1 (pre-registered hypothesis before running; surprise rate measurable per drill-defeatism rule)
**Methodology basis:** [[feedback-literature-is-not-oracle-2026-06-11]] + Research V2_HYBRID_TWO_INDEX_RRF_ARCHITECTURE drill + Layer 1 attribution rule 6

## Context

Three v2 architecture experiments queued (~2-5 hr total CPU). Each has prior expectations from literature + drill recommendation. Empirical outcome may CONFIRM literature, ASTONISH (substrate-divergent), or fall in DON'T-KNOW-YET regime.

Surprises (per drill-defeatism rule) trigger analysis; expected outcomes ratify the architecture without claim inflation.

## Experiment 1: 5-architecture comparison

### Architectures compared
1. Semantic-only baseline (Fix A current state)
2. Semantic + tag-vec composite (REJECTED per FINDINGS_04 + 05; included as control)
3. **HYBRID semantic + HRR/TPR algebra index + RRF + intent router (RECOMMENDED per drill)**
4. bge-encode-algebra-as-text (Fix B alternative)
5. Co-trained dual embeddings (out of scope for v1; placeholder)

### Hypotheses (pre-registered)

| Architecture | Predicted Q1 (DUAL) | Predicted Q2 (DISCRETE family) | Predicted Q3 (cross-corpus) | Predicted Q4 (probabilistic family) | Predicted Q5 (FFT-dual) |
|---|---|---|---|---|---|
| 1 semantic-only | high (post-batch-02 description) | high | partial | high | high |
| 2 tag-vec composite | high | LOW (FINDINGS_04 confirmed) | partial | high | high |
| 3 HYBRID (RRF+intent) | high | high | **HIGH** (relations + algebra index combined) | high | high (FFT-dual relation) |
| 4 bge-as-text | high | high | medium (text-prefix less structured than HRR) | high | medium |
| 5 co-trained | OUT-OF-SCOPE for v1 |

**Primary hypothesis**: architecture 3 (hybrid) beats all others on Q3 (cross-corpus concept-link). Architecture 3 ties architecture 1 on Q1/Q2/Q4/Q5.

**Surprise outcome A**: architecture 4 (bge-as-text) BEATS architecture 3 on multiple queries. This means bge-encoded structured-text carries more relevant signal than HRR/TPR algebra-vec. Triggers drill on hybrid encoder design.

**Surprise outcome B**: architecture 1 (semantic-only) BEATS architecture 3 on Q3. Means concept-corpus relations don't help cross-corpus retrieval; redesign needed.

**Surprise outcome C**: architecture 2 (tag-vec composite) DOES NOT regress vs architecture 1. Would invalidate FINDINGS_04 finding; need to redo Layer 1 attribution with multi-seed.

### Success criterion (per Tier 1 gate)
Architecture 3 (hybrid) shows demonstrable LIFT on at least one query without REGRESSION on any. Demonstrates the v2 architecture genuinely earns its complexity.

If architecture 3 ties architecture 1 on all 5 queries: signal too weak; need expanded query set + sealed queries to differentiate.

## Experiment 2: RRF k sweep

### Sweep
k = 10, 30, 60, 100, 200 (per Research V2_QUESTIONS_ANSWERED reply addition of k=200)

### Hypotheses (pre-registered)

**Literature prediction** (Cormack 2009 + Bruch et al. recent hybrid retrieval):
- k = 60 wins; rank-fusion smoothing standard
- k = 10 too tight (only top-rank dominates fusion)
- k = 200 too loose (rank dilution)

**Per [[feedback-literature-is-not-oracle-2026-06-11]]: substrate-self-index empirical winner may differ.**

Substrate-distinguishing predictions:
- If k=60 wins -> literature standard holds
- If k=100 or 200 wins -> substrate algebra-index produces meaningful signal AT LOWER RANKS that wider damping captures. Implies algebra-vec captures fine structure beyond top-rank.
- If k=10 wins -> top-rank dominates; algebra-index is mostly confirming semantic results not adding new ones. Intent router should be tighter (use algebra only when semantic disagrees).

### Success criterion
Find a single k that wins or ties on majority of queries. If no clear winner, choose k=60 (literature) as conservative default.

## Experiment 3: Lexicon intent-classifier validation

### Test queries
- 5 disclosed queries (Q1-Q5; Day 1)
- 5 sealed queries (Day 2 from Research)
- 5 synthetic ad-hoc queries spanning structural / semantic / mixed intent

### Hypotheses (pre-registered)

Per Research Q2 in V2_QUESTIONS_ANSWERED: "Start small. Expand from experiment 3 gaps empirically."

Current lexicon (12 structural keywords + 8 semantic keywords) is starting point. Predictions:
- **80-90% intent classification accuracy** on disclosed + sealed (mostly-clean keyword matches)
- **50-70% accuracy on synthetic** (likely have stem variants like "share" vs "shared", phrase ordering)

Surprises:
- **<50% on disclosed**: lexicon too narrow; major expansion needed
- **>95% on synthetic**: surprisingly robust; lexicon is more general than expected

Per drill-defeatism rule: surprises trigger expansion + multi-seed adversarial validation.

### Success criterion
70%+ on disclosed + sealed; identify which keywords are missing from synthetic gaps.

## What I will explicitly flag in the run report

Per [[feedback-literature-is-not-oracle-2026-06-11]]:

For each experiment outcome, the report will have a section:
- "Literature prediction": expected from cited literature
- "Pre-registered hypothesis": what I wrote down before running
- "Empirical result": what actually happened
- "Divergence assessment": was there substrate-distinguishing finding? Could it be a discovery?

Substrate-self-index divergent findings get flagged as potential discovery, not "bug, we got it wrong" framing.

## Honest attribution rule (per Research FINDINGS_04 endorsement)

Each query result will attribute lift to specific mechanism:
- Semantic-vec contribution
- Algebra-vec contribution (Index 2 HRR)
- Relation traversal contribution
- RRF rank-fusion contribution

NOT aggregate "lift" claims. Per methodology rule 6.

## Cross-references

- v2 architecture: notes/research_to_testbed_V2_HYBRID_TWO_INDEX_RRF_ARCHITECTURE_2026-06-11.md
- V2 questions answered: notes/research_to_testbed_V2_QUESTIONS_ANSWERED_2026-06-11.md
- Hazards extension: notes/research_to_testbed_DEEP_SELF_EVALUATION_PROGRAM_ENDORSED_2026-06-11.md
- Literature-not-oracle feedback: memory/feedback_literature_is_not_oracle_2026-06-11.md
- Findings 04 + 05 (Layer 1 attribution): notes/testbed_to_research_INDEX_FINDINGS_04_* + 05_*
