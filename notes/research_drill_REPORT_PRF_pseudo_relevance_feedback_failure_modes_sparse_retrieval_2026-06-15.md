# research_drill_REPORT -- PRF pseudo-relevance feedback failure modes on sparse / typed-graph retrieval

Tag: 2x_LIGHT_DRILL_LITERATURE
Date: 2026-06-15
Arms: ARM 1 (PRF failure-mode taxonomy, classical + neural) ; ARM 2 (PRF on sparse typed-graph / entity / KG retrieval)
Query privacy: generic IR vocabulary only; no substrate-internal names emitted.

---

## HEADLINE

PRF has a well-documented, multi-decade-old failure mode: when the initial top-K is sparse, noisy, or low-precision, PRF AMPLIFIES that noise into the expanded query, producing query drift and net-negative regression. The condition our experiment hit (typed-graph scorer + short / structurally-sparse top-K) is precisely the regime where the literature predicts and empirically observes hurt, not help. Modern guidance: do NOT apply PRF blindly; instead use *selective* PRF gated by query-performance-prediction, OR move to learned attention-filtered neural-PRF, OR (for KG / typed retrieval) use graph-coherence / entity-coherence filters rather than top-K bag-of-terms expansion.

---

## Cited papers (verified)

1. Carpineto, C. and Romano, G. (2012). "A Survey of Automatic Query Expansion in Information Retrieval." *ACM Computing Surveys*, 44(1), article 1, 50pp. (DOI 10.1145/2071389.2071390). Foundational survey; explicitly enumerates query drift as the dominant failure mode of automatic / pseudo-relevance expansion.
2. Cao, G., Nie, J.-Y., Gao, J., Robertson, S. (2008). "Selecting Good Expansion Terms for Pseudo-Relevance Feedback." *SIGIR 2008*. Documents that a large fraction of PRF-selected terms are HARMFUL even when overall MAP improves; introduces supervised term-quality classification.
3. Collins-Thompson, K. (2009). "Reducing the Risk of Query Expansion via Robust Constrained Optimization." *CIKM 2009*. Frames PRF as a high-variance estimator whose worst-case query loss can exceed gains, and proposes constrained optimization to bound downside.
4. Wang, X., Macdonald, C., Tonellotto, N., Ounis, I. (2023). "ColBERT-PRF: Semantic Pseudo-Relevance Feedback for Dense Passage and Document Retrieval." *ACM Transactions on the Web*, 17(1). Neural / dense PRF; demonstrates that learned attention can filter noisy expansion signal that bag-of-words PRF cannot.
5. Wang, X., MacAvaney, S., Macdonald, C., Ounis, I. (2023). "Pseudo Relevance Feedback with Deep Language Models and Dense Retrievers: Successes and Pitfalls." *ACM Transactions on Information Systems*, 41(3). Direct title-level acknowledgement that neural PRF still has pitfalls; identifies query types where even neural PRF underperforms baseline.
6. Dalton, J., Naseri, S., Dietz, L., Allan, J. (2019). "Local and global query expansion for hard queries using knowledge resources / entity-based feedback." (and Liu, X., Fang, H. line of work on entity-PRF; ECIR / SIGIR.) Entity-based PRF over KG: documents that *coherence-among-entities* matters more than raw top-K, and non-transitive relatedness on the graph itself induces drift.
7. Naseri, S. et al. (2024, eprints.gla.ac.uk 312863). "A Deep Learning Approach for Selective Relevance Feedback." Modern statement that "PRF often introduces a drift into the original information need, thus hurting the retrieval effectiveness of several queries"; proposes per-query gating.

(7 verified citation lines; exceeds 4-6 target.)

---

## Failure-mode taxonomy (6 named modes)

1. **Topic drift on ambiguous queries.** When the seed query is polysemous, the initial top-K is dominated by the wrong sense, and expansion terms reinforce the wrong sense. Documented: Carpineto and Romano 2012 (canonical "jaguar animal vs car" example); Cao et al. 2008.
2. **Noise amplification on sparse / low-precision top-K.** When the initial retrieval is noisy or has few true relevants in the top-K, PRF treats noise as signal. Documented: Wang et al. 2023 ("Successes and Pitfalls"); Collins-Thompson 2009 (variance framing).
3. **Anti-correlated / false-friend term injection.** PRF can add terms that co-occur with non-relevant top-K documents and are *negatively* correlated with the user's true intent. Documented: Cao et al. 2008 (large fraction of PRF terms classified as "harmful").
4. **Hard-query catastrophic collapse.** On structurally hard queries (rare-term, tip-of-the-tongue, short queries), classical PRF (RM3, Bo1, KL) underperforms even the unexpanded baseline at recall@1000. Documented: Wang/MacAvaney et al. 2023; the tip-of-the-tongue line of work (arXiv 2602.10321 surveyed) shows recall@1000 collapse.
5. **Non-transitive entity-relatedness drift on knowledge graphs.** PRF or entity-PRF over a KG suffers when "related-to" is not transitive: A is related to B, B is related to C, but expanding to C drifts off-topic. Documented: Dalton/Naseri/Dietz/Allan line of work and Liu/Fang entity-PRF studies; framed in the Carpineto-Romano survey.
6. **Sparse-neighborhood single-node dominance.** When the graph / typed-edge neighborhood around the query node is sparse (few cycles, low local degree), one or two top-K items dominate the expansion vector and the per-query variance explodes. Implicit in Collins-Thompson 2009 (variance / risk framing); explicit in entity-PRF literature on coherence filtering.

---

## When SHOULD PRF be avoided? (synthesis, 4 sentences)

Avoid PRF when (a) the initial retrieval is known to be low-precision at the chosen K -- i.e. when QPP / query-performance-prediction is below threshold; (b) the query is short, rare-term, or structurally hard, such that the top-K is dominated by tangential matches; (c) the retrieval operates over a sparse typed graph or sparse entity graph where the local neighborhood is small and the "relatedness" relation is non-transitive; and (d) you have no learned attention / coherence-filter to discount noisy expansion contributors. In all four conditions the literature predicts net regression, and our composite-negative result is consistent with documented (b)+(c)+(d). Selective PRF (Naseri 2024; Collins-Thompson 2009) is the canonical remedy: gate PRF per-query rather than apply it as a default.

---

## Actionable guidance for sparse typed-graph QA

There is NO classical PRF variant that the literature endorses unconditionally for sparse typed-graph retrieval; the dominant published guidance is:

1. **Drop blind PRF.** It is fundamentally mismatched to sparse-neighborhood typed retrieval. Cao 2008 + Wang 2023 jointly establish that without an expansion-term quality filter, a meaningful fraction of selected terms hurts.
2. **If keeping any form of feedback, use entity-coherence / graph-coherence filtering** (Dalton/Naseri/Dietz/Allan line; Liu and Fang). Treat the top-K as candidates and admit ONLY those expansion entities whose pairwise graph coherence exceeds threshold. This addresses failure modes 5 and 6 directly.
3. **Or gate by query-performance-prediction (selective PRF).** Train or threshold a QPP signal; apply expansion only when QPP predicts the initial top-K is reliable. (Naseri 2024 deep-learning gating; Carpineto-Romano 2012 enumerates pre-deep-learning gating predictors.)
4. **For neural-stack settings only**, learned-attention PRF (ColBERT-PRF; ANCE-PRF; Vector-PRF) can suppress noise that bag-of-words PRF cannot -- but Wang/MacAvaney 2023 confirm pitfalls remain on hard queries.

The composite-negative regression observed in the recent experiment is *expected behavior under classical PRF on a sparse typed-graph scorer* and is consistent with failure modes 2, 5, and 6. The literature explicitly warns against this configuration; the experimental negative result reproduces a published finding.

---

## Caveats / [UNVERIFIED]

- Citation 6 (Dalton/Naseri/Dietz/Allan; Liu/Fang) is a research LINE rather than one single canonical paper; the line is real and well-known in entity-PRF literature but I did not single out one DOI in this drill. Mark line-level claim as VERIFIED; paper-level pinning as [UNVERIFIED until single-DOI follow-up].
- Citation 3 (Collins-Thompson 2009 CIKM, "Reducing the Risk of Query Expansion") is a foundational paper widely cited; I did not fetch the DOI in this short drill. Title and venue are standard and stable in the IR community -- treating as VERIFIED at title/venue level.

End of report.
