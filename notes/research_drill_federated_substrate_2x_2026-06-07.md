# Research drill: Federated substrate -- cross-customer routing intelligence without fact sharing

Filed: 2026-06-07
Topic: 2x drill on federated learning architecture for per-customer substrate with shared
       DP-protected routing statistics
Trigger: Self-improving routing drill identified federated moat as 9/10 creativity + business moat

---

## HEADLINE

Federated routing statistics (frequency distributions over slow-path triggers, bridge entity
hit rates, query-pattern vectors) are genuinely low-sensitivity DP targets: their L2 sensitivity
is bounded by O(1/N_queries), which means small Gaussian noise achieves epsilon < 1.0 at
practical utility. This is materially different from sharing model gradients (high sensitivity)
or embeddings (membership-inference risk). The architecture is sound in principle. The honest
risks are (a) rare-customer inference attacks on aggregated stats, (b) epsilon drift under
composition across many aggregation rounds, and (c) the warm-start lift being smaller than
projected if routing statistics are weakly correlated across customer domains.

P_theoretical = 0.72 (architecture is well-grounded in published federated DP lit)
P_empirical = 0.38 (warm-start lift magnitude and inference-attack robustness untested;
              applying 0.20 calibration penalty per feedback-lit-scan-calibration-penalty)

---

## Architecture specification

### Layer structure

Three independent layers. Facts never leave Layer 1.

Layer 1 -- Per-customer substrate (isolated)
  - One substrate instance per customer
  - All facts, embeddings, bridge graph, sleep-defrag state reside here
  - No outbound data except routing statistics (Layer 2 interface)
  - HIPAA/GDPR: data subject rights apply here and only here

Layer 2 -- Local routing statistics collector (per-customer, on-prem or tenant VPC)
  - Collects: slow-path trigger frequency, fast-path hit rate by query-type cluster,
    bridge entity frequency ranks (NOT identities), query latency distribution
  - Computes: local histogram over routing-decision buckets
  - Applies local DP noise (randomized response or Laplace on each histogram bin)
    before any export
  - Output: DP-protected local statistic vector sent to Layer 3 at configurable cadence

Layer 3 -- Federated aggregation server (vendor-controlled)
  - Receives: DP-protected histogram vectors from all participating customers
  - Applies: server-side Gaussian noise + clipping (second DP pass for defense in depth)
  - Computes: weighted average routing statistic vector across customers
  - Stores: anonymized aggregate routing model (NOT any per-customer vector)
  - Output: updated shared routing prior, pushed to all customers at next onboarding event
  - NEVER stores or logs per-customer contribution vectors

Layer 4 -- New customer onboarding
  - New customer receives shared routing prior from Layer 3
  - Warm-starts local router with priors; own substrate starts empty
  - As queries arrive, customer's Layer 2 accumulates local data and overrides priors
  - Contribution to Layer 3 begins after minimum query threshold (prevents inference from
    small-N customers)

---

## What gets shared vs private

SHARED (always DP-protected before leaving Layer 2):
  - Routing-decision bucket histogram (e.g. "40% of queries hit fast-path in bucket 3")
  - Bridge entity frequency RANKS (not identities; rank 1 = most-hit bridge entity)
  - Query latency quantiles (p50, p90, p99 per routing decision type)
  - Fast-path vs slow-path split fraction

NEVER SHARED:
  - Any fact, entity name, or content
  - Any embedding vector
  - Any customer identifier attached to a routing decision
  - Any customer's raw query text or query embedding
  - Any per-customer row in the substrate

---

## Differential privacy mechanics

### Sensitivity analysis for routing statistics

Routing statistics are histogram bins over decision buckets. If customer C has N queries,
changing one query changes exactly one bin by 1/N (L1 sensitivity = 1/N; L2 = 1/N).

Gaussian mechanism noise: sigma = sqrt(2 * ln(1.25/delta)) * (1/N) / epsilon

For N = 1000 queries, epsilon = 1.0, delta = 1e-5:
  sigma = sqrt(2 * ln(1.25e5)) * 0.001 / 1.0 ~ 0.0034

This is very small relative to typical histogram bin values (0.1 to 0.5 range). Utility
cost of DP at epsilon = 1.0 for N >= 1000 is negligible.

Key implication: routing statistics are naturally low-sensitivity because they are
per-query averages over a large query volume. This is NOT the same as gradient DP
(where sensitivity is high and noise must be large). The utility-privacy tradeoff is
far more favorable here than in federated model training.

### Composition budget

Each customer contributes one aggregated statistic update per cadence period (e.g. weekly).
With T aggregation rounds and advanced composition (Renyi DP or f-DP):
  - Total epsilon grows as O(sqrt(T)) not O(T) under advanced composition
  - For T = 52 rounds (1 year weekly) and per-round epsilon = 0.1:
    cumulative epsilon ~ 0.1 * sqrt(52) ~ 0.72

This is well within the published "acceptable" range (epsilon <= 10 for most industry
practitioners; strict researchers target epsilon <= 1.0 for classification tasks).

### Published precedent

- Geyer et al. (2017) "Differentially Private Federated Learning: A Client Level
  Perspective" -- demonstrated per-client DP with epsilon = 0.18 maintaining utility
  within 2% on MNIST. Routing statistics have LOWER sensitivity than gradient updates.

- McMahan et al. (2018) "Learning Differentially Private Recurrent Language Models" --
  achieved epsilon = 2.5 on next-word prediction with minimal utility loss at N = 763M
  tokens. Our N per customer is smaller but our statistic dimensionality is also much
  lower (O(100) bins vs O(10^8) parameters).

- DeSIA (2025, arxiv 2504.18497) -- showed reconstruction attacks on aggregated census
  statistics are effective when statistics are low-count (N < 50 respondents). The
  minimum query threshold in Layer 2 (above) is the mitigation: do not aggregate a
  customer until N_queries >= 500.

- DP-FedLoRA (2025, arxiv 2509.09097) -- demonstrated epsilon in [1, 5] maintains
  strong utility for federated LLM fine-tuning. Routing statistics are lower-dimensional
  and lower-sensitivity; epsilon <= 1.0 is achievable here.

- f-DP framework (OpenReview 2025, YIGUv0BZCy) -- provides tighter composition bounds
  than classic (epsilon, delta) accounting. Pairwise Network f-DP handles decentralized
  aggregation without a trusted server requirement.

### Rare-customer inference risk (honest risk)

DeSIA analysis applies: if a customer's routing statistics are highly unusual (rare
domain, unique query distribution), an adversary observing the aggregate before and
after that customer joins can infer their contribution. Mitigations:
  - Minimum N_queries threshold (500+) before first contribution
  - Contribution clipping: clip per-customer statistic vector to L2 norm = 1.0 before
    aggregation
  - Shuffle model: randomly permute contribution timing across customers per round

This is a real risk for small or domain-unique customers. It is not fully eliminated
by DP alone; it requires the additional structural mitigations above.

---

## New customer warm-start: quantitative projection

Assumption: routing statistics are moderately correlated across customers (similar query
types trigger similar routing decisions). This is the key empirical unknown.

Cold-start baseline: new customer, no shared prior
  - Day 1 fast-path fraction: ~0.10 (router has no domain knowledge)
  - Time to 0.40 fast-path fraction: ~500-2000 queries

Warm-start from shared prior: shared routing prior loaded at onboarding
  - Day 1 fast-path fraction: projected ~0.25-0.35 (IF routing statistics are correlated
    across customers; P_empirical = 0.38 per calibration penalty)
  - Time to 0.40 fast-path fraction: ~100-500 queries

Warm-start lift depends entirely on cross-customer routing correlation. This is NOT
guaranteed. Routing statistics may be domain-specific (medical vs. legal vs. financial)
with low cross-domain correlation. If correlation is low, warm-start lift collapses.

Published federated recommendation cold-start analogy (IFedRec, ACM Web 2024): item-level
attribute sharing across clients in recommendation systems provided 15-30% improvement
in cold-start quality. Routing statistics are a closer analog to item frequencies than
to personalized preferences; cross-customer correlation is plausible but domain-specific.

Honest projection: warm-start lift of 10-20% in fast-path fraction on Day 1 is
plausible; 30%+ requires high cross-domain routing correlation that must be measured.
Deflated P_empirical = 0.38 reflects this uncertainty.

---

## Commercial moat quantification

### Network effect structure

Standard RAG: per-customer vector DB, no cross-customer learning, no network effect.
Frontier LLM: one global model, benefits all customers equally, no per-customer
  accumulation, no marginal benefit from adding more customers beyond pricing leverage.
Federated substrate: per-customer fact isolation + shared routing intelligence =
  each new customer strengthens the routing prior for all others.

This is a DATA NETWORK EFFECT on the routing layer, not on the fact layer. The distinction
matters: fact network effects are blocked by privacy law; routing network effects are not,
because routing statistics are not PHI/PII by construction.

Published analysis (Federated Learning as a Network Effects Game, 2023 arxiv 2302.08533):
  "as more clients contribute to federated learning, training models with higher utility
  becomes more feasible, attracting more participants in a positive feedback loop."
  The same logic applies directly to the routing prior.

### Defensibility analysis

Moat strength depends on three factors:

1. Routing correlation across customers (empirical unknown; if low, moat is weak)
2. Exclusivity: can a competitor replicate this? Any multi-tenant system could implement
   this architecture. The moat is NOT architectural exclusivity -- it is the ACCUMULATED
   dataset of routing statistics from an existing customer base. A competitor launching
   today has zero accumulated statistics; the incumbent has N-customer-years.
3. Switching cost: once a customer's substrate is populated and their router is tuned,
   switching to a competitor means restarting from cold-start.

Moat verdict: REAL but not impregnable. The data flywheel is the actual moat, not the
architecture. First mover who accumulates routing statistics across diverse customer
domains will be hardest to displace. This is a 2-4 year moat given current market size.

### Network effect size (honest estimate)

Federated Learning Market Network Effects game (2024 arxiv 2408.13223): "rational clients
opt-in or opt-out based on utility gain and cost as network grows; heterogeneous data
can reduce utility in some settings." This is the non-monotonic risk: if customer domains
are too different, adding more customers may not help (or may inject noise into the routing
prior). Domain clustering (sharing routing priors only within similar customer domain
clusters) mitigates this.

---

## Privacy posture analysis

### HIPAA

Under HIPAA Option B (per-customer substrate), PHI is confined to Layer 1. Routing
statistics in Layer 2/3 contain no PHI by construction: they are frequency counts over
routing decision buckets, not over patient records or identifiable content.

Key HIPAA question: do routing statistics constitute "derived PHI"? The argument that
they do NOT: routing statistics are analogous to access-log aggregate counts (query
rates by type), which are standard operational metrics. They contain no patient
identifiers, no clinical terms, no record-level data.

Residual risk: a bucket label (e.g. "bucket 17 = queries containing the term 'diabetes'")
could leak PHI if bucket definitions are content-based. Mitigation: bucket definitions
must be routing-behavior-based (latency tier, path code) NOT content-based. This is an
implementation constraint, not a theoretical barrier.

Assessment: HIPAA-compatible with correct bucket-definition discipline.

### GDPR

GDPR Article 5.1(c) data minimization: routing statistics satisfy this requirement
because they are the minimum data needed to enable the federated routing function.
No personal data crosses customer boundaries.

GDPR Article 17 right to erasure: applies only to Layer 1 (per-customer substrate).
Layer 3 aggregated statistics are anonymized by construction; erasure of a single
customer's contribution is not technically required because their contribution is
indistinguishable in the aggregate. This is consistent with GDPR recital 26 (anonymized
data is outside GDPR scope).

GDPR Article 22 automated decision-making: routing decisions are infrastructure-level
(which knowledge path to take) not user-facing decisions. Article 22 does not apply.

Assessment: GDPR-compatible with anonymization argument for Layer 3.

### EU AI Act Article 12 (audit logging)

Article 12 requires that high-risk AI systems maintain logs sufficient to enable ex-post
auditing. The substrate routing log (Layer 1, per-customer) already provides this. The
federated layer adds the question: can the vendor prove that a routing decision for
customer C was not influenced by PHI from customer D?

The proof structure:
  - Layer 3 contains only aggregated DP-protected statistics with no per-customer ID
  - Layer 2 shows that customer C's routing prior = shared aggregate (not raw D data)
  - Noise injection records are stored per-round and can be audited

Assessment: Article 12-compatible; the DP noise injection log is the audit artifact.
This is actually STRONGER than a pure per-customer system because the federated architecture
creates a provable isolation boundary documented by the DP parameters.

---

## Six crazy options evaluated

### (a) Federated sleep defrag

Sleep defrag regularizes the substrate's stored representations during low-query periods.
Cross-customer federated sleep defrag would share the REGULARIZATION STATISTICS (which
representation clusters are most disordered) across customers.

P_theoretical = 0.55: sleep defrag statistics have similar DP-sensitivity properties to
routing statistics; feasible in principle.
Blocking issue: sleep defrag statistics are more representation-specific than routing
statistics. A customer whose substrate encodes rare medical procedures would have unusual
defrag statistics that could leak domain-specific information even after DP noise.
Verdict: CONDITIONAL. Safe if defrag statistics are bucketed by geometry (curvature,
  compactness) not by semantic content. Engineering complexity: HIGH. Defer to v3.0.

### (b) Federated bridge entity learning

Bridge entities are the connector nodes between query chains. Cross-customer federated
sharing of bridge entity FREQUENCY RANKS (not identities) is the routing statistics
case already covered. A stronger version would share bridge entity STRUCTURAL PROPERTIES
(valence, clustering coefficient in the bridge graph).

P_theoretical = 0.60: structural properties are lower-sensitivity than entity identities.
Blocking issue: structural properties are domain-specific; bridge graph topology in a
medical KB is different from a legal KB. Cross-domain aggregation may not help.
Verdict: VIABLE for same-domain customer clusters. DP on graph structural statistics
  is published (differential privacy on graph data, Nissim et al.). Engineering complexity:
  MEDIUM. Candidate for v2.5.

### (c) Federated adversarial contradiction detection

Cross-customer inconsistency detection: flag routing paths where multiple customers
report conflicting confidence on similar query types. This could surface systematic
errors in a shared base KB or encoder.

P_theoretical = 0.45: technically feasible; published work on federated anomaly detection.
Blocking issue: "conflicting confidence" is a noisy signal; high false-positive rate would
create alert fatigue. More critically, reporting that "50 customers got low confidence on
query-type X" might leak that a specific fact domain is poorly covered, which could be
commercially sensitive.
Verdict: SPECULATIVE. Interesting for a vendor-level quality signal. Not a customer-facing
  moat. Engineering complexity: HIGH. Defer to v3.0+.

### (d) Personalized federated (opt-in similar-customer sharing)

Customers opt into sharing routing statistics only with similar-domain customers (e.g.
all HIPAA-covered healthcare customers share with each other; legal customers share only
with legal customers). Stronger warm-start within a domain cluster.

P_theoretical = 0.65: domain clustering improves routing correlation, directly addressing
  the cross-domain correlation risk in the main architecture.
Blocking issue: requires domain classification at customer onboarding (customer must
  self-report domain; creates a new trust/verification challenge).
Verdict: STRONG. This is the most credible enhancement to the base architecture.
  Addresses the non-monotonic network effect risk directly. Engineering complexity: LOW
  (cluster tag + filter in aggregation server). Candidate for v2.0 alongside base federation.

### (e) Federated encoder fine-tuning

Cross-customer federated fine-tuning of the shared encoder (Llama-1B or BGE-large) using
DP-protected gradient updates. DP-FedLoRA (2025) is the direct precedent.

P_theoretical = 0.58: well-published; DP-FedLoRA achieves strong utility-privacy tradeoff
  for federated LLM fine-tuning.
Blocking issue: (1) per feedback-causal_lm_last_token_pool, encoder fine-tuning interacts
  with the last-token pooling dependency in non-obvious ways. (2) LoRA hurts retrieval
  per production-architecture-locked memory. (3) Gradient sensitivity for encoder updates
  is much higher than routing statistic sensitivity, requiring larger noise and causing
  larger utility loss. (4) Cloud compute requirement is substantial.
Verdict: RESEARCH-TRACK only. Do not include in v2.0 product roadmap. May become viable
  if retrieval-safe LoRA variant is discovered. Defer indefinitely.

### (f) Federated as premium tier

Customers pay more for warm-start benefits. Basic tier: cold-start, per-customer routing.
Premium tier: federated warm-start + ongoing routing prior updates.

P_theoretical = 1.0 (this is a pricing/packaging decision, not a technical one).
Business logic: this creates a monetization surface for the network effect. Premium tier
  customers subsidize the federated infrastructure cost and provide the routing statistics
  that improve the service for other premium tier customers.
Verdict: STRONG. Direct productization of the moat. Zero additional engineering beyond
  the base federated architecture. Should be part of the v2.0 product spec.

---

## Falsifiable predictions: HARD-PASS and HARD-FAIL thresholds

### Prediction 1: DP utility at epsilon=1.0

HARD-PASS: For a histogram over 50-100 routing buckets with N >= 500 queries per customer,
  Gaussian mechanism at epsilon=1.0, delta=1e-5 introduces < 5% mean absolute error on
  each bucket's estimated probability.
HARD-FAIL: MAE > 15% at epsilon=1.0 for N = 500 queries. (If this fails, epsilon must
  be relaxed to 3-5, weakening the privacy posture but not blocking the architecture.)

### Prediction 2: Warm-start routing lift

HARD-PASS: On a simulated new customer (held-out domain), warm-start routing prior
  achieves fast-path fraction >= 0.25 on Day 1 vs. baseline 0.10 (>= 15pp lift).
HARD-FAIL: Warm-start fast-path fraction < 0.12 on Day 1 (lift < 2pp; prior is
  essentially noise). This would mean routing statistics are domain-specific enough
  that cross-customer aggregation provides no benefit.

### Prediction 3: Inference attack robustness at N=500

HARD-PASS: With N=500 minimum query threshold + L2 clipping + Gaussian noise at sigma
  calibrated to epsilon=1.0, membership inference AUROC on the aggregated statistic
  vector is < 0.60 (near-random).
HARD-FAIL: Membership inference AUROC > 0.75 at epsilon=1.0 and N=500. This would mean
  rare-customer inference attack is practical and the minimum query threshold must be
  raised to N=2000+ or epsilon tightened to 0.2.

### Prediction 4: v2.0 engineering estimate

HARD-PASS: Federated aggregation server + DP noise injection + warm-start push is
  implementable in 2-3 weeks of engineering on top of existing per-customer substrate.
HARD-FAIL: Integration reveals that the routing statistics schema requires > 6 weeks of
  substrate refactoring to expose, making the v2.0 timeline 8+ weeks.

---

## Cheap decisive pre-tests

### Pre-test 1: DP utility simulation (1-2 hours, CPU, no cloud)

Synthetic data: generate M=20 simulated customer routing histograms (50 bins each,
  N=500-2000 queries per customer). Apply Gaussian mechanism at epsilon in [0.1, 0.5, 1.0,
  3.0]. Compute mean absolute error of aggregated histogram vs ground truth.
  Measure: does MAE < 5% for epsilon = 1.0 and N >= 500?
  Pre-reg: HARD-PASS if yes; HARD-FAIL if MAE > 15% at epsilon=1.0 for any N >= 500.
Cost: CPU only, ~30-60 minutes of numpy code. No substrate code needed.

### Pre-test 2: Cross-domain routing correlation (1-2 hours, CPU)

Simulate two domain types (e.g. "medical" and "legal") with distinct routing
distributions (different fast-path fractions, different bucket distributions). Measure
cosine similarity between routing statistic vectors across domains.
  Pre-reg: if cosine similarity >= 0.50, cross-domain warm-start is plausible.
  If cosine similarity < 0.20, domain-clustered federation (option d) is required.
Cost: CPU, synthetic data, ~1 hour. No substrate needed.

### Pre-test 3: Minimum N for inference attack robustness (2-4 hours, CPU)

Implement a simple reconstruction attack on the aggregated statistic: given aggregate
over M=50 customers with DP noise, can an adversary identify a single customer's
contribution from before/after the aggregate? Sweep N_queries from 50 to 2000.
  Pre-reg: find minimum N where reconstruction MSE exceeds DP noise floor (attacker
  cannot distinguish signal from noise). This gives the operational minimum query threshold.
Cost: CPU, ~2-4 hours. Published attack code (DeSIA framework) can be adapted.

---

## Cross-thread synthesis

### Connection to HIPAA Option B (per-customer substrate)

The federated architecture directly extends HIPAA Option B. Layer 1 is exactly the
per-customer substrate from Option B. Layers 2-4 add the cross-customer routing layer
ON TOP of a compliant per-customer design. This means federation does not require
re-architecting for HIPAA; it is an additive layer.

### Connection to self-improving routing (prior drill)

The self-improving routing drill accumulated per-customer query patterns. The federated
layer is the natural extension: instead of patterns improving routing for one customer,
DP-aggregated patterns improve routing initialization for all new customers. The
mechanism is the same (routing statistics accumulate per query); the federation adds
a sharing step with DP protection.

### Connection to ZKL privacy posture (prior privacy drills)

ZKL measures membership inference risk at the fact/embedding level (Layer 1). The
federated routing layer (Layers 2-4) does not affect ZKL because routing statistics
are not embeddings. These are orthogonal privacy questions. The ZKL work informs
how tight the per-customer privacy posture needs to be; the federated work adds a
new privacy surface (routing stats) that requires its own DP analysis.

---

## Substrate-product implications

### v1.5 / v2.0 / v3.0 sequencing

v1.5 (current work, no new engineering):
  - Per-customer substrate fully deployed
  - Self-improving routing accumulates per-customer statistics locally
  - No federation yet
  - This is the foundation that makes v2.0 possible

v2.0 (2-3 weeks additional engineering):
  - Layer 2: local DP statistics collector added to per-customer deployment
  - Layer 3: federated aggregation server deployed (simple weighted average + Gaussian noise)
  - Warm-start push: new customers receive shared routing prior at onboarding
  - Domain clustering option (d above) included from the start
  - Premium tier: federated warm-start as paid differentiator (option f)
  - Compliance artifact: DP noise injection log per round stored for Article 12 audit

v3.0 (months after v2.0, contingent on empirical validation of warm-start lift):
  - Federated bridge entity structural statistics (option b, same-domain clusters)
  - Federated sleep defrag regularization statistics (option a, geometry-bucketed only)
  - Multi-round composition budget dashboard for customers
  - Adversarial contradiction detection signals (option c, vendor-internal quality only)

### Customer pitch

Factual claims only:
  - "Your facts never leave your substrate. What we share across customers is anonymous
    routing statistics: which query patterns are slow, which are fast. These are protected
    by differential privacy with published mathematical guarantees."
  - "New customers start with a routing prior built from all existing customers. As we add
    more customers, new customers benefit from more accumulated routing intelligence."
  - "Frontier LLMs and standard RAG have no per-customer accumulation. Once trained, they
    don't improve on your domain. Our substrate gets better for your specific query patterns
    while drawing on the collective routing experience of the customer base."
  - "We can prove to your compliance team, through our differential privacy audit log,
    that no other customer's facts influenced your routing decisions."

What not to claim until pre-tests pass:
  - Do NOT claim specific warm-start lift numbers until Pre-test 2 is done
  - Do NOT claim HIPAA-absolute status for routing statistics until legal review confirms
    that operational routing metrics are outside PHI scope in your deployment context

---

## Implementation complexity estimate

Week 1:
  - Design routing statistics schema (bucket definitions, histogram dimensionality)
  - Implement Layer 2 local histogram collector (adds to existing per-customer substrate)
  - Implement Gaussian mechanism noise injection with epsilon/delta parameterization
  - Unit tests: verify DP guarantee holds for test histograms

Week 2:
  - Implement Layer 3 aggregation server (minimal: weighted average + server-side noise)
  - Implement minimum N_queries threshold gate
  - Implement L2 clipping of per-customer contribution vector
  - Integration test: simulated M=5 customers, verify aggregate is DP-correct

Week 2-3:
  - Implement warm-start push: new customer onboarding receives shared prior
  - Implement domain clustering tag (customer self-reported at onboarding)
  - Implement contribution eligibility check (N_queries gate + cluster membership)
  - Build DP audit log (noise params + round timestamp + epsilon budget tracker)

Libraries:
  - DP noise: numpy Gaussian is sufficient for this sensitivity level; opacus/google-dp
    are heavier-weight and designed for gradient DP. For routing statistics, numpy with
    verified sensitivity analysis is the correct approach.
  - Aggregation: no special library needed; this is a weighted mean over low-dimensional
    vectors.

Total engineering estimate: 2-3 weeks for one senior engineer who understands the
routing statistics schema. This is a low-risk estimate; the main uncertainty is the
routing statistics schema design (depends on how routing decisions are currently logged).

---

## Honest risks summary

1. WARM-START CORRELATION RISK (HIGH): If routing statistics are domain-specific, the
   cross-customer warm-start provides minimal lift. Domain clustering (option d) partially
   mitigates. Pre-test 2 is the gate.

2. RARE-CUSTOMER INFERENCE RISK (MEDIUM): Small or domain-unique customers are vulnerable
   to inference attacks even with DP. Minimum query threshold and shuffle model are
   required mitigations. Pre-test 3 is the gate.

3. EPSILON COMPOSITION DRIFT (LOW-MEDIUM): Over many aggregation rounds (years of weekly
   updates), cumulative epsilon may exceed budget. Advanced composition (f-DP or Renyi DP)
   mitigates; must be designed in from the start, not added later.

4. BUCKET DEFINITION PHI RISK (MEDIUM): If routing buckets are defined by content keywords
   rather than routing behavior, they could constitute derived PHI under HIPAA. This is
   an implementation discipline risk, not a theoretical barrier.

5. COMPETITOR REPLICATION (MEDIUM): The architecture is not secret. Any multi-tenant
   knowledge-retrieval vendor could implement this. The moat is the accumulated routing
   dataset, not the architecture. First-mover advantage is time-bounded (2-4 years).

6. NON-MONOTONIC NETWORK EFFECT (LOW-MEDIUM): Published theory (2024 arxiv 2408.13223)
   shows that heterogeneous client data can reduce federated utility as network grows.
   Domain clustering is the mitigation. Monitor aggregate routing utility per domain
   cluster as customer base grows.

---

## Citations (verified count: 10)

1. Geyer, R. et al. (2017). Differentially Private Federated Learning: A Client Level
   Perspective. arXiv:1712.07557
2. McMahan, H.B. et al. (2018). Learning Differentially Private Recurrent Language
   Models. ICLR 2018. arXiv:1710.06963
3. DeSIA: Attribute Inference Attacks Against Limited Fixed Aggregate Statistics (2025).
   arXiv:2504.18497
4. DP-FedLoRA: Privacy-Enhanced Federated Fine-Tuning for On-Device Large Language Models
   (2025). arXiv:2509.09097
5. Mitigating Privacy-Utility Trade-off in Decentralized Federated Learning via f-DP
   (2025). OpenReview YIGUv0BZCy / arXiv:2510.19934
6. Social Welfare Maximization for Federated Learning with Network Effects (2024).
   arXiv:2408.13223
7. Federated Learning as a Network Effects Game (2023). arXiv:2302.08533
8. When Federated Recommendation Meets Cold-Start Problem: IFedRec (2024).
   ACM Web Conference 2024. dl.acm.org/doi/10.1145/3589334.3645525
9. Mechanism Design for Federated Learning with Non-Monotonic Network Effects (2025).
   arXiv:2601.04648
10. Reviewing and Improving the Gaussian Mechanism for Differential Privacy (2019).
    arXiv:1911.12060 (sensitivity bounds used for routing statistics analysis)

---

## Next drill candidates

1. Graph differential privacy for bridge entity topology (federated option b): published
   work on DP for graph-structured data is sparse; this is the gap.
2. Domain clustering algorithms for routing statistics similarity (federated option d):
   how to cluster customers by routing pattern without seeing their content.
3. Shuffle model for federated aggregation: reduces trust assumptions on the aggregation
   server; recent 2024-2025 papers on shuffle DP for histogram aggregation.
