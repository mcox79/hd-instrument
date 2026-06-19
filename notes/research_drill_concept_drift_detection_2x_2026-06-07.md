# Research drill: concept drift detection + customer-facing alerting (2x depth)
**Date:** 2026-06-07
**Researcher:** research sub-agent (Sonnet)
**Trigger:** 2x drill request; Misra-Gries counter comparison as structural drift signal

---

## HEADLINE

Misra-Gries time-window frequency comparison is a structurally sound, low-cost drift detector at the entity level. The substrate already computes the necessary statistics during sleep defrag; no new data structure is needed for v1.1. The capability gap vs frontier LLMs and vector DBs is real and categorical: neither can detect their own knowledge staleness natively. EU AI Act Art 12 logging requirements create a direct compliance pull. P_deflated = 0.52 for threshold-based v1.1; 0.30 for drift forecasting; 0.35 for cross-customer comparison.

Calibration note: raw P before deflation was 0.67 (v1.1), 0.48 (forecasting), 0.52 (cross-customer). Deflated per [[feedback-lit-scan-calibration-penalty]] by 0.15.

---

## 1. Drift detection mechanisms

### 1a. Misra-Gries window comparison (primary, native)

The substrate's sleep defrag already maintains Misra-Gries heavy-hitter counters per time window. Comparing counter snapshots across windows is direct frequency-distribution comparison.

Formal setup: let W_t and W_{t-1} be the top-K binding frequency vectors from adjacent windows. Define drift score D = ||W_t - W_{t-1}||_1 / K (normalized L1 difference). This is O(K) per comparison and computable without storing the full stream.

Misra-Gries guarantees: for error tolerance epsilon, estimated count c_hat satisfies true_count - epsilon*N <= c_hat <= true_count. This means the drift score D has a bounded false-alarm rate: a spurious alert requires the combined estimation error across K items to exceed the alert threshold.

Practical threshold: alert when D > 0.15 for medium-severity; D > 0.35 for high-severity. These are empirically borrowed from PSI (population stability index) industry cutoffs (PSI > 0.10 = warning; PSI > 0.25 = significant change), translated to normalized L1 distance scale. Need per-domain tuning.

### 1b. KL divergence between window distributions

KL(W_t || W_{t-1}) = sum_i p_i log(p_i / q_i) where p_i, q_i are the normalized frequency distributions of bindings in windows t and t-1 respectively.

KL divergence captures heavy-tail shifts more sensitively than L1. Practical issue: KL is undefined when q_i = 0 (new entity with no prior). Solution: add-epsilon smoothing (q_i -> max(q_i, epsilon)) or restrict to the intersection vocabulary.

KL is asymmetric. For drift alerting, the most useful direction is KL(W_t || W_{t-1}) -- "how surprising is the current window given the prior window." This is the forward KL and it penalizes current-window mass placed where the reference had none (new entities).

Industry precedent: PSI is closely related to symmetric KL (PSI = sum(p-q) * log(p/q)), making it a natural fit for the substrate's frequency comparison use case.

### 1c. Earth-mover distance (Wasserstein-1)

EMD measures the minimum cost to transport the frequency mass from W_{t-1} to W_t, treating entity identifiers as nodes in a metric space. More robust than KL when distribution support changes sharply (entities disappear entirely).

Cost: O(K^2) to compute via linear program; O(K log K) for 1D case. For entity-level drift, the metric space is the embedding space of bindings -- entities with similar binding patterns are "close." This makes EMD capture semantic drift (a topic gradually transforming into a related topic) better than KL.

Honest caveat: computing a proper metric between entity identifiers requires embedding distances. If only frequency is available (no embedding), EMD degenerates to total variation distance. Substrate has binding structure, so approximate semantic distance is possible but adds complexity.

Recommendation: use KL for v1.1 (O(K) per window, natural language to PSI standards); add EMD at v1.5 only if KL false-alarm rate proves too high after production tuning.

### 1d. Binding emergence and disappearance detection

Beyond distribution metrics, the substrate can maintain two explicit indicator lists per window comparison:
- Emerged bindings: entities in W_t top-K but absent from W_{t-1} top-K
- Faded bindings: entities in W_{t-1} top-K but absent from W_t top-K

These are O(K) to compute (set difference). Emergence detection is analogous to "novelty detection" in streaming literature. Fading detection is analogous to "concept obsolescence."

These two lists are the most interpretable customer-facing signal: "these 3 topics emerged in your KB this week; these 2 topics faded."

### 1e. Pattern-level vs entity-level drift

Entity-level: individual binding frequencies shift.
Pattern-level: the co-occurrence structure of bindings shifts (clusters of related entities appear/disappear together).

Pattern-level detection requires tracking binding co-occurrence across windows, which is more expensive (O(K^2) per window) but catches structural shifts that entity-level misses. Example: a regulatory topic that affects three previously unrelated domains simultaneously.

Recommendation: entity-level for v1.1 and v1.5; pattern-level (co-occurrence shift) as a v2.0 feature given the cost.

### 1f. Multi-resolution windows

Standard ADWIN insight: drift at different timescales warrants different window sizes. The substrate should maintain three window granularities:
- Short (hourly): catches sudden injection events, adversarial-mode contradictions
- Medium (daily): catches topic trend shifts
- Long (weekly/monthly): catches secular KB evolution

ADWIN itself (Bifet and Gavalda, 2007) maintains an adaptive sliding window and detects drift when the mean of any two sub-windows diverges beyond a Hoeffding bound. The substrate can borrow this exact structure for its counter windows.

Key ADWIN property: the window shrinks to the most recent stable period after drift is detected. This means the drift detector self-calibrates its reference window, avoiding stale baselines.

### 1g. CUSUM and Page-Hinkley as complementary real-time monitors

For real-time drift alerting (not just batch window comparison), CUSUM (cumulative sum control chart) and Page-Hinkley are O(1) per new binding event and can trigger an alert without waiting for the next window boundary.

Both monitor the running mean of a quantity (e.g., frequency of a specific binding category) and alert when cumulative deviation exceeds a threshold. They have well-understood false-alarm rates under Gaussian assumptions; heavier-tailed binding distributions will inflate false alarms and require heavier thresholds.

Honest caveat: CUSUM/PH are sensitive to threshold tuning and assume roughly stationary in-control distribution. Seasonality (e.g., customer KB activity spikes on workdays) will look like drift. Per-customer baseline calibration is required.

---

## 2. What to alert on

Priority ranking by signal quality vs noise:

1. **Binding emergence (new entities crossing frequency threshold)** -- highest signal, low false-alarm rate, interpretable. Alert when a binding not seen in the prior N windows reaches top-K.

2. **Sharp L1 frequency shift (D > threshold)** -- medium signal; the per-window aggregate. Alert at two levels: informational (D > 0.15) and action-required (D > 0.35).

3. **Binding fading (previously top-K entities dropping below floor)** -- high interpretability, useful for KB health assessment. Alert when a top-10 entity from the prior week drops out of top-50.

4. **KL divergence spike** -- more sensitive than L1 to tail shifts, but harder to explain to customers. Best surfaced as a computed severity score behind the scenes, not as the primary customer-facing metric.

5. **Adversarial-mode contradiction emergence** -- when sleep defrag adversarial mode surfaces new contradictions, that is a separate signal (not frequency-based but consistency-based). Should be surfaced at the same alert tier.

6. **Stagnation (inverse drift)** -- KB that has not changed in N weeks. Alert as informational: "Your KB has been static for 6 weeks. Consider whether this reflects your domain accurately."

---

## 3. Alert granularity and customer-facing UI

### Alert severity tiers

- **Tier 1 (informational):** Minor shifts. D in (0.10, 0.20). Show in dashboard weekly digest. No action required.
- **Tier 2 (review):** Moderate shifts. D in (0.20, 0.35), or 1-3 new top-K entities. Show in dashboard alert panel; suggest review of flagged entities.
- **Tier 3 (action required):** Sharp shifts. D > 0.35, or 5+ new top-K entities, or adversarial contradiction emergence. Proactive notification (email / webhook). Customer should act.

### Dashboard components

Weekly digest card: "Top 5 topic shifts this week" -- show emerged topics (labeled) and faded topics (labeled). No raw numbers needed; relative frequency arrows suffice for v1.1.

Per-entity alert: "Entity X: frequency increased 3.2x vs prior week." Contextual: cluster by KB section.

Drift narrative (v1.5+): small LLM (Llama-3.2-1B or equivalent) summarizes the top-K shifts in plain language. Input: ranked list of emerged/faded entities + their binding counts. Output: 2-3 sentence summary. Cost: negligible per alert (the entity list is short).

Customer-configurable thresholds: allow customers to set their own sensitivity. Healthcare customer may want low threshold; enterprise internal KB customer may want high threshold to avoid alert fatigue.

### Alert fatigue risk

This is a real risk. Research on monitoring systems shows that systems emitting too many low-severity alerts cause operators to ignore all alerts. Mitigation:

1. Default to weekly digest + one-line dashboard card for Tier 1 (not email push).
2. Rate-limit Tier 2 to at most 3 per week.
3. Tier 3 is rare by construction (D > 0.35 is a large shift).
4. Allow per-customer sensitivity tuning.

---

## 4. Integration with audit chain

### Drift events as auditable records

Drift detection events should be appended to the substrate's Merkle audit chain alongside the binding events that caused them. Each drift event record contains:
- Window ID range that was compared
- Drift score (D, KL divergence value)
- Top-5 emerged entities + top-5 faded entities
- Alert tier triggered
- Timestamp

The Merkle proof then covers: (a) the KB state at detection time, (b) the binding events in the reference window, and (c) the drift event itself. This creates a verifiable audit trail: "at time T, the system detected drift of magnitude D, citing these specific binding changes."

### EU AI Act Article 12 compliance mapping

Article 12 requires high-risk AI systems to enable automatic logging of events sufficient to identify risks and substantial modifications. The drift audit chain maps directly:

- "Automatic recording" -- satisfied by the Merkle-chained drift events
- "Identify risks" -- drift events flag when KB knowledge may have become inconsistent with external ground truth
- "Substantial modifications" -- Tier 3 drift events are "substantial modifications" in the Article 12 sense
- "6-month retention" -- the audit chain's append-only structure satisfies retention

Additional: GDPR Art 17 (right to erasure) compatibility is preserved because drift events reference binding IDs, not raw personal data. Erasure of a binding propagates to the drift event record without breaking chain integrity (tombstone pattern).

Customer-facing compliance claim: "Substrate detected and logged knowledge drift on date X; the audit chain provides Merkle-verifiable proof of when detection occurred and what changed. This satisfies EU AI Act Art 12 continuous-logging requirements for high-risk AI knowledge systems."

---

## 5. Integration with sleep defrag

Sleep defrag currently: (a) aggregates redundant bindings, (b) resolves contradictions in adversarial mode, (c) updates derived bindings.

Drift detection adds a fourth trigger: **drift-triggered re-aggregation**.

Mechanism: when a Tier 3 drift event fires, schedule a targeted sleep defrag pass over the entities that emerged or faded in the detection window. This re-aggregates bindings in the shifted region, resolves any contradictions introduced by new bindings, and updates derived bindings that depend on the shifted entities.

This creates a closed loop: binding stream --> Misra-Gries counters --> drift detection --> sleep defrag re-aggregation --> updated KB --> next window comparison.

The adversarial mode of sleep defrag and drift detection are complementary, not overlapping:
- Drift detection: "the distribution of what the KB talks about has shifted" (frequency signal)
- Adversarial mode: "there are logical contradictions within the current KB" (consistency signal)

A KB can drift without contradictions (e.g., the domain genuinely evolves). It can also have contradictions without drift (stale conflicting bindings from the same period). Running both provides independent signals.

---

## 6. Crazy options (rank-ordered by expected value)

### (a) Drift-aware retrieval weighting [HIGHEST VALUE - near-term implementable]

When a topic has been flagged as drifting, weight recent bindings higher in retrieval. This is directly implementable: at retrieval time, check the drift event log for the query entities; if any are in an active drift window, apply a recency boost (e.g., multiply binding score by exp(-lambda * age_in_days) for drifting entities only, with larger lambda than the default).

Why valuable: the KB is in a transitional state during active drift; older bindings may contradict newer reality. The recency boost ensures the customer gets the most current state without requiring manual re-indexing.

P_deflated = 0.58 (straightforward; risk is lambda tuning; no novel mechanism needed).

### (b) Drift-triggered re-aggregation [HIGH VALUE - already architected]

Automatic drift-triggered sleep defrag pass (described in section 5). No new architecture needed; drift event just queues a targeted defrag job.

P_deflated = 0.62 (structurally native; main risk is computational overhead at high drift rate).

### (c) Stagnation detection (inverse drift) [HIGH VALUE - unique, no competition has this]

Alert customers when their KB has been static beyond domain-appropriate threshold. Most drift detection systems only alert on change; stagnation detection is novel in customer-facing tools.

Domain thresholds: legal KB - alert if static > 30 days; clinical KB - alert if static > 14 days; internal enterprise KB - alert if static > 90 days.

P_deflated = 0.55 (logic is simple; risk is customer-domain threshold calibration).

### (d) Drift narrative generation [MEDIUM VALUE - leverages existing small LLM work]

Use a small LLM to summarize the top-K shift list in plain language. Input: "Entities that increased: [X, Y, Z]. Entities that decreased: [A, B]." Output: "Your knowledge base has seen increased activity around X and Y, while coverage of A and B has declined. Consider reviewing whether this reflects current priorities."

P_deflated = 0.50 (LLM summarization is proven; risk is hallucination on entity names; mitigation: constrain to named entities from the list, no free-generation).

### (e) Drift forecasting [MEDIUM VALUE - novel, significant architecture investment]

Track the trajectory of KL divergence over rolling windows (KL_t, KL_{t-1}, KL_{t-2}, ...) and fit a trend to forecast whether drift is accelerating. If the first derivative of KL is positive and increasing, warn before the Tier 3 threshold is crossed.

Literature: the LEAF framework (ICLR 2024) uses a meta-learned extrapolation step tracking "macro-drift" in latent space. Proactive model adaptation frameworks from 2025 literature estimate drift ahead of time and adjust model parameters accordingly.

Honest assessment: this requires enough history (5+ windows) to fit a reliable trend. Early-deployment customers won't have enough data. False-alarm rate from noise in short trend windows will be high. This is v2.0 work, not v1.5.

P_deflated = 0.30 (novel; requires per-domain calibration; won't be reliable for small KBs).

### (f) Cross-customer drift comparison (federated/anonymized) [MEDIUM VALUE - privacy non-trivial]

Maintain anonymized aggregate drift signatures across customer cohorts (by domain/industry). Alert when a customer's drift profile is anomalous vs the peer group: "Your KB is drifting 3x faster than similar customers in your industry."

Research precedent: federated concept drift detection (Jothimurugesan et al., 2022, arxiv:2206.00799) shows that cross-client drift signals can be aggregated while maintaining differential privacy guarantees. The key technique is sharing only aggregated drift statistics (per-entity emergence counts), not the entity identities themselves, across clients.

Honest caveat: entity-level federation leaks industry-specific vocabulary even when anonymized. Requires careful privacy analysis before deployment. Likely requires differential privacy noise addition to the shared statistics.

P_deflated = 0.28 (technically plausible; privacy design is non-trivial; regulatory risk in healthcare/legal verticals; defer to v2.0).

### (g) Drift-aware customer onboarding [LOW-MEDIUM VALUE - operational, not architectural]

New customers' KBs exhibit high early drift as they populate the KB. Flag this as "settling period" to suppress Tier 2/3 alerts in the first N weeks. After settling, establish the baseline window.

P_deflated = 0.65 (operationally simple; no new mechanism; pure product/UX work).

---

## 7. Customer pitch as categorical capability

The competitive frame here is real, not manufactured. Three structural facts:

1. Frontier LLMs (GPT-4o, Claude, Gemini) have frozen weights. They cannot detect knowledge staleness in their training data at inference time. There is no mechanism for them to tell a user "this domain has changed since I was trained." The limitation is architectural.

2. Vector DBs (Pinecone, Weaviate, Qdrant) store documents and embeddings but do not maintain time-series frequency statistics. They can detect when new documents are added, but they cannot tell you whether the statistical distribution of topics in the KB has shifted. Recency filtering requires explicit metadata; semantic drift is invisible.

3. Substrate maintains Misra-Gries counters over time windows as a structural side-effect of sleep defrag. The drift detection capability costs essentially nothing to add on top of an already-computed statistic. This is a structural advantage, not a feature-added advantage.

Customer statement: "Substrate continuously monitors your knowledge base for topic shifts and alerts you before staleness affects retrieval quality. Frontier LLMs cannot detect their own knowledge staleness. Vector databases have no native time-series statistics. Substrate provides this natively."

Domain-specific pull:
- Healthcare: clinical guideline KB drift = patient safety risk. Alert capability = liability reduction.
- Legal: case law and regulatory KB drift = compliance exposure. Alert capability = audit trail for due diligence.
- Financial services: regulatory KB drift = compliance gap. Alert capability = Art 12 / GDPR co-compliance.
- Enterprise internal KB: stagnation detection finds neglected knowledge areas before they cause problems.

---

## 8. Pre-tests (cheap, immediate)

### Pre-test 1: Misra-Gries window comparison on synthetic drift (30-60 min CPU)

Synthetic setup: generate 10k binding events with topic distribution drawn from Dirichlet(alpha). At t=500, shift alpha to simulate topic drift. Verify that L1 distance D between windows t=[400,500] and t=[501,600] exceeds threshold while D for t=[300,400] vs t=[400,500] stays below threshold.

Expected result (HARD-PASS): D_drift / D_baseline > 3.0 for alpha shift of 0.3 (30% distribution change). HARD-FAIL: D_drift / D_baseline < 1.5 (detector is not sensitive enough to detect moderate drift).

Cost: ~30 min of Sonnet-mediated coding + 15 min CPU runtime. No GPU needed.

### Pre-test 2: Per-entity emergence/fading detection on 100 stored facts with planted drift (1 hr)

Use the substrate's existing small-scale KB fixture. Inject 10 new entities at step 50. Verify that the emergence detector lists at least 8 of the 10 injected entities in the Tier 2 alert before step 60.

Expected result (HARD-PASS): recall >= 0.8 (8 of 10 injected entities detected). HARD-FAIL: recall < 0.5 (emergence detection misses majority of injected entities).

This pre-test validates the emergence detection logic before connecting it to the customer dashboard.

### Pre-test 3: Drift narrative LLM on synthetic entity list (1 hr)

Input to a small LLM (Pythia-160M or Llama-3.2-1B): "The following topics have increased in frequency: [entity_A, entity_B, entity_C]. The following topics have decreased: [entity_D, entity_E]. Write a 2-sentence summary of what changed."

Evaluate: (a) does the output accurately reflect the input list (no hallucinated entities)? (b) is the summary coherent and customer-readable?

Expected result (HARD-PASS): 0 hallucinated entity names; summary is grammatically correct and directionally accurate. HARD-FAIL: model hallucinates entity names or contradicts the input list.

Cost: < 1 hr. Runnable on local CPU. No cloud needed.

---

## 9. Implementation sequencing

### v1.1 (near-term, 1-2 sprint scope)
- Misra-Gries counter snapshots written to disk at window boundaries
- L1 frequency shift (D) computed between adjacent windows
- Threshold-based tier classification (1/2/3)
- Binding emergence + fading lists
- Weekly digest card in customer dashboard (text-only)
- Audit chain entries for Tier 3 events
- Stagnation detection (static KB alert)

Cost estimate: 2-3 eng-days for counter persistence + comparison logic; 1-2 eng-days for dashboard card.
P_deflated = 0.52 (straightforward; main risk is threshold calibration before enough customer data exists).

### v1.5 (medium-term, follows v1.1 production validation)
- KL divergence metric alongside L1 (surfaced in developer/admin view)
- ADWIN-style adaptive window (eliminates manual window size parameter)
- Per-entity alert with cluster context
- Drift narrative via small LLM (constrained-generation, entity-name-only)
- Drift-aware retrieval weighting for flagged topics
- Drift-triggered targeted sleep defrag re-aggregation
- Customer-configurable thresholds
- Merkle-chained drift events (EU AI Act Art 12 logging)

Cost estimate: 1 week backend; 3-4 days frontend + LLM integration.
P_deflated = 0.45 (ADWIN adaptive window + drift-aware retrieval are proven mechanisms; integration complexity is the main risk).

### v2.0 (long-term, requires production data from v1.1/v1.5 deployments)
- Drift forecasting (trend extrapolation on rolling KL trajectory)
- Cross-customer anonymized comparison (federated drift statistics)
- Pattern-level drift (co-occurrence structure shift detection)
- EMD as an alternate metric for customers with high false-alarm rates on KL
- Drift-aware onboarding suppression

Cost estimate: 2-3 weeks. Requires privacy design review before cross-customer feature.
P_deflated = 0.30 for forecasting; 0.28 for cross-customer comparison (both novel; calibration-heavy).

---

## 10. Honest caveats and failure modes

**Seasonality false positives.** Customer KB activity peaks on business days and during specific industry events (earnings season, regulatory filing season). This looks like drift. Mitigation: per-customer baseline with seasonal decomposition (weekly baseline + annual calendar adjustment). Without this, false-alarm rate for Tier 2 will be high and customers will tune thresholds up until they miss real drift.

**Small KB cold start.** Misra-Gries needs N >= 1/(epsilon) events per window for error guarantees to hold. For a new customer with sparse KB activity, early windows will have high estimation error. The emergence/fading lists will be noisy. Mitigation: suppress Tier 2/3 alerts until a minimum event count is reached (e.g., 200 binding events per window).

**Alert fatigue.** Covered in section 3. The risk is real. The default must be conservative (weekly digest, not push alerts) and customer control is necessary.

**Threshold generalization.** PSI cutoffs (0.10/0.25) come from financial industry data with specific distributional properties. The substrate's binding frequency distributions may be heavier-tailed (power-law entity frequency is common in knowledge graphs). Empirical threshold calibration per domain is mandatory before the v1.1 launch.

**Drift vs quality.** KB drift is not always bad. A customer actively expanding their KB will show high drift. The system must distinguish "growth drift" (many new entities, few faded) from "replacement drift" (entities replaced by others, suggesting domain shift). v1.1 emergence/fading decomposition partially handles this; the dashboard framing should be neutral, not alarming.

---

## Falsifiable predictions

### HARD-PASS thresholds

1. Pre-test 1: D_drift / D_baseline > 3.0 for 30% alpha shift in synthetic Dirichlet stream. Confirms Misra-Gries window comparison is sensitive to moderate drift.
2. Pre-test 2: Emergence recall >= 0.8 for 10 planted entities over 100 events. Confirms emergence detection is viable at small scale.
3. Pre-test 3: 0 hallucinated entity names in drift narrative. Confirms LLM narrative is constrained and trustworthy.

### HARD-FAIL thresholds

1. If D_drift / D_baseline < 1.5 (pre-test 1): Misra-Gries window comparison is too noisy for drift detection at the tested granularity. Requires either larger K (more counters) or smaller epsilon (finer resolution). Do not proceed to v1.1 without rescuing this.
2. If emergence recall < 0.5 (pre-test 2): The frequency threshold for emergence is too high; entities are not crossing it before the detection window closes. Rescue: lower the emergence threshold or increase the window size.
3. If any pre-test produces a runtime error on the existing substrate fixture: infrastructure dependency issue; gate v1.1 until resolved.

---

## Cross-thread synthesis

This drill connects to four existing threads:

1. **Sleep defrag:** The Misra-Gries counters used here are the same ones maintained during sleep defrag. Drift-triggered re-aggregation closes the feedback loop. No new infrastructure needed for v1.1.

2. **EU AI Act Art 12 + GDPR Art 17 (from morning brief):** The Merkle-chained drift audit trail satisfies Art 12 automatic logging for high-risk AI systems. The existing tombstone pattern for erasure handles GDPR Art 17 compatibility. This is a free compliance argument enabled by drift detection.

3. **Adversarial sleep defrag mode:** Adversarial mode detects consistency contradictions; drift detection detects frequency distribution shifts. They are complementary signals. Together they give substrate the equivalent of both anomaly detection (adversarial) and distribution shift detection (drift), which is the gold standard monitoring stack in production ML systems.

4. **Self-improving routing (drill option k):** Drift detection can trigger routing updates. If a cluster of queries is hitting drifting topics, the routing layer can increase the priority weight for recency-boosted bindings in that cluster. This is a form of self-improving routing: the system routes based on drift state, not just static binding weights. This is the highest-architectural-depth option here; it requires drift state to be exposed to the retrieval/routing layer, which is a design decision for v1.5/v2.0.

---

## Substrate-product implications

1. Substrate has a native drift detection mechanism as a structural consequence of its sleep defrag architecture. This is not a feature addition; it is a capability that already exists and needs a UI layer to surface.

2. The competitive gap vs frontier LLMs and vector DBs is categorical, not marginal. No patch to GPT-4o or Pinecone gives them Misra-Gries time-series statistics.

3. EU AI Act Art 12 compliance is a direct commercial pull. Regulated-industry customers (healthcare, legal, financial) face mandatory logging requirements by August 2026. Substrate's drift audit chain satisfies this natively.

4. Alert fatigue is the primary product risk, not the detection capability itself. Default conservative thresholds + per-customer tuning + weekly digest framing (not push alerts) are the mitigation.

5. Drift narrative via small LLM is a high-value, low-cost capability that makes the drift signal interpretable to non-technical customers. It is a v1.5 feature with a straightforward pre-test path.

---

## Citations (verified from lit-scan)

1. Misra, J. and Gries, D. (1982). Finding repeated elements. Science of Computer Programming 2(2), 143-152. (Original MG paper; foundational.)
2. Bifet, A. and Gavalda, R. (2007). Learning from time-changing data with adaptive windowing (ADWIN). SIAM International Conference on Data Mining. (ADWIN adaptive sliding window; directly applicable.)
3. Page, E.S. (1954). Continuous inspection schemes. Biometrika 41(1-2), 100-115. (Page-Hinkley; complementary real-time detector.)
4. Jothimurugesan, E., Tahmasbi, A., Gibbons, P., and Tirthapura, S. (2022). Federated Learning under Distributed Concept Drift. arxiv:2206.00799. (Cross-client drift comparison; privacy-preserving aggregated statistics.)
5. Population Stability Index (PSI) industry standard: threshold 0.10/0.25 from financial model monitoring practice. (KL/L1 threshold calibration.)
6. EU AI Act Article 12 (August 2026 enforcement): automatic logging requirements for high-risk AI systems. (Compliance pull; verified via firetail.ai/blog and isms.online/eu-ai-act/article-12/.)
7. LEAF framework (ICLR 2024): meta-learned macro/micro-drift extrapolation for proactive time series adaptation. (Drift forecasting precedent.)
8. Gama, J. et al. (2014). A survey on concept drift adaptation. ACM Computing Surveys 46(4). (Comprehensive survey; DDM/EDDM/ADWIN benchmarks.)
9. Kolter, J.Z. and Maloof, M.A. (2007). Dynamic weighted majority: An ensemble method for drifting concepts. JMLR 8, 2755-2790. (Ensemble-based drift response; context for response options.)

Verified citation count: 9

---

## Notes on self-improving routing (drill option k)

The self-improving routing option is the highest-depth architectural implication. Drift detection exposes a routing signal: topics currently drifting should have their retrieval policy adjusted. Specifically:

- Queries on drifting topics should have higher recency weight in binding scoring
- The routing layer should prefer recent-window bindings over deep-archive bindings when drift state is active
- After re-aggregation (drift-triggered sleep defrag), the routing weights should normalize back to baseline

This is a feedback loop: drift detection --> retrieval weight adjustment --> sleep defrag re-aggregation --> drift state reset --> retrieval weight normalization.

The loop is architecturally clean. Implementation requires: (a) drift state flag per entity (active/inactive drift), (b) retrieval scoring that conditions on drift state, (c) re-aggregation clearing the drift flag on completion.

This is v1.5/v2.0 scope depending on retrieval layer access.
