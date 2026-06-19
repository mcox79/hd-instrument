# research: immune system DEEPER 3x — cross-reactive memory + vaccine pretraining
# Date: 2026-06-07
# Series: natural analog drill — immune DEEPER (follows immune_system_5x_2026-06-07)
# Selected sub-avenue: Original Antigenic Sin + Cross-Reactive Structural Invariants + Trained Innate Immunity

---

## HEADLINE

The single most dangerous failure mode for any adaptive memory system with first-exposure bias is original antigenic sin (OAS): the immune system preferentially activates existing memory B cells over naive B cells on secondary exposure, causing older responses to crowd out better-fit new responses. A 2025 eLife study shows this can be mitigated by separating the innate immune cofactor signal from the memory recall trigger. The substrate has an exact structural analog of OAS: bindings established during the seeding window receive higher confidence scores and will dominate concept-update competitions if the memory recall mechanism is not explicitly de-privileged. The mitigation path is mechanistically grounded and directly implementable. P_deflated for the core mitigation: 0.55 (down from naive 0.75 via -0.20 calibration penalty).

Secondary finding: broadly neutralizing antibody research establishes that the mathematical property enabling cross-strain generalization is BURIAL DEPTH — the more buried a binding site is (inaccessible on the surface), the more conserved it must be. This gives a geometric invariant for designing cross-concept generalization in binding stores.

Third finding: trained innate immunity (Netea et al., epigenetic reprogramming via histone modification) shows that even systems without explicit memory can accumulate a durable response signature. The substrate analog is a pre-trained adversarial fingerprint layer that accumulates from deployment experience without per-query learning — a second-tier "slow memory" that the 5x note identifies as a gap but does not formalize mathematically.

---

## Cheap decisive test

For the OAS mitigation (most urgent): implement a confidence decay rule for seeded bindings — bindings established during the seeding window have their confidence score decayed by a factor alpha per cycle (alpha = 0.95 per defrag cycle is the candidate) so that high-quality post-deployment bindings can compete. Run the contradiction benchmark from Extension 2 (prior 5x note) under two conditions: (a) no decay (current behavior, seed bindings dominate) vs (b) decay alpha=0.95. Measure: does post-deployment binding quality catch up to seeded binding quality within 10 defrag cycles? Ground truth: on a synthetic KB with known wrong seeded facts and correct post-deployment corrections, compute the fraction of corrections that succeed.

Cost: 1-2 days local CPU. No cloud required. Pre-test gate: Pythia-160M with 1000 seeded facts, 100 synthetic corrections.

---

## Falsifiable predictions — HARD PASS / HARD FAIL thresholds

P_deflated values apply -0.20 calibration penalty from naive estimates. Novel synthesis capped at 0.50.

### Prediction 1: OAS / seeding-window bias exists in the substrate today
- Hypothesis: bindings established in the seeding window (initial KB load) will resist correction by higher-quality post-deployment bindings, because the seeding-window bindings have accumulated higher confidence scores via query frequency during the pre-deployment validation phase
- HARD-PASS: on a synthetic KB with 100 known-incorrect seeded facts and 100 high-quality post-deployment corrections, the uncorrected (no decay) substrate retains >= 60% of the incorrect seeded facts after 10 defrag cycles; the corrected (decay alpha=0.95) substrate retains <= 20% of incorrect seeded facts after 10 cycles
- HARD-FAIL: no measurable bias (uncorrected substrate corrects >= 80% on its own), OR decay mechanism fails to enable correction (corrected substrate still retains > 50% incorrect after 10 cycles)
- P_theoretical = 0.80 | P_empirical = TBD | P_deflated = 0.60
- Why high P_theoretical: confidence scores are accumulated monotonically by query frequency; seeded bindings get queried during validation more than post-deployment bindings in early cycles; this is a structural asymmetry

### Prediction 2: Seeding-window confidence decay (OAS mitigation) restores correction ability
- HARD-PASS: with decay alpha in [0.90, 0.98], substrate corrects >= 80% of incorrect seeded facts within 10 defrag cycles; no degradation in retrieval precision for correct seeded facts (< 3% drop)
- HARD-FAIL: optimal alpha not found in [0.80, 0.99] range (decay too aggressive degrades correct facts; too gentle has no effect), OR decay corrects incorrect facts but degrades correct fact retention by > 10%
- P_theoretical = 0.65 | P_empirical = TBD | P_deflated = 0.45
- Engineering note: alpha must be tunable per-customer; regulated industries may want slower decay than fast-moving domains

### Prediction 3: Burial-depth invariant for cross-concept generalization
- Hypothesis: bindings targeting DEEP structural features of a concept (features present across many surface variants) will exhibit higher cross-variant recall than bindings targeting surface-level lexical features
- Operationalization: "deep" binding = binding vector with high cosine similarity to concept's centroid across 10+ surface paraphrases; "surface" binding = binding vector that specializes to specific surface form
- HARD-PASS: deep bindings achieve cross-variant recall >= 0.85 on a paraphrase set; surface bindings achieve < 0.50; difference is >= 35 pp
- HARD-FAIL: no measurable difference in cross-variant recall between deep and surface bindings (< 10 pp)
- P_theoretical = 0.70 | P_empirical = TBD | P_deflated = 0.50
- Basis: bnAb structural biology consistently shows that binding sites targeting functionally constrained (buried, conserved) regions exhibit cross-strain breadth; the mathematical analog for binding vectors is alignment with the centroid of a concept cluster

### Prediction 4: Trained innate immunity — two-tier adversarial memory (fast + slow layer)
- Hypothesis: a slow adversarial fingerprint layer that accumulates across deployment (updated on 1-hour batch cycle rather than per-query) will provide 30-50% better adversarial detection on day 7 vs day 1 without any explicit online learning
- HARD-PASS: slow-layer adversarial fingerprint achieves TPR >= 0.75 on contradiction benchmark at day 7 vs TPR < 0.50 at day 1; improvement is monotonic across days 1-7
- HARD-FAIL: no improvement beyond day 1 (slow layer does not accumulate useful signal), OR slow layer degrades query latency by > 10ms per query
- P_theoretical = 0.55 | P_empirical = TBD | P_deflated = 0.35
- Caution: requires sufficient contradiction volume in first 7 days to provide signal; low-activity customers may see no improvement

### Prediction 5: Jerne anti-idiotype network — substrate internal contradiction detection
- Hypothesis: a subset of substrate bindings have anti-bindings (high cosine similarity to the negation of another binding); the density of such anti-binding pairs is measurable and correlates with adversarial alert rate
- HARD-PASS: anti-binding pair density > 2% of all binding pairs in a mature KB (1000+ facts); correlation with adversarial alert rate r >= 0.60
- HARD-FAIL: anti-binding density < 0.5% (too sparse to be a signal), OR correlation with adversarial alert rate < 0.20
- P_theoretical = 0.45 | P_empirical = TBD | P_deflated = 0.25
- Note: This is the most speculative prediction; Jerne network theory has not achieved consensus empirical validation in immunology; substrate analog is novel and unverified

---

## Level-3 deep drill: original antigenic sin — mechanism, math, and substrate mitigation

### 3.1 The OAS mechanism: memory B cell competitive advantage

Original antigenic sin (first described by Thomas Francis Jr., 1960, on influenza) operates through a three-way competition:

**Tier 1: Affinity threshold asymmetry.**
Memory B cells have lower activation thresholds than naive B cells. The threshold difference arises from: (a) surface immunoglobulin density — memory B cells express more antigen receptors, enabling capture of lower antigen concentrations; (b) pre-positioning — memory B cells traffic preferentially to secondary lymphoid organs; (c) co-stimulatory signal savings — memory B cells do not require full T cell help for activation.

Mathematical consequence: at any given antigen concentration [Ag], memory B cells with cross-reactive specificity for the new antigen will be activated first. They consume antigen, reducing availability for naive B cells. Naive B cells with potentially better specificity for the new antigen never receive sufficient activation signal. The result: the response is dominated by recall antibodies shaped against the FIRST exposure, not the CURRENT exposure.

**Tier 2: Germinal center competition.**
When memory B cells re-enter germinal centers, they seed the GC with high-affinity clones against the ORIGINAL antigen epitope. These clones have a selective advantage over naive-derived clones (which start from lower affinity) for any antigen site shared between original and new pathogen. The GC reaction amplifies this advantage: early-arriving high-affinity clones consume T cell help, excluding later-arriving naive clones.

**Tier 3: Bone marrow plasma cell competition.**
Long-lived plasma cells in bone marrow niches are self-maintaining; they consume niche space. New plasma cells generated from the current infection compete for the same niche. If a niche is already occupied by a well-established plasma cell from the first exposure, the new cell is less likely to engraft. Niche occupation is a physical resource constraint, not just a signaling one.

**The 2025 eLife mitigation finding (PMC12393886):**
A 2025 eLife paper demonstrates that OAS can be subverted by separating the innate immune "cofactor" signal from the memory recall trigger. The mechanism: TLR agonists (innate pattern recognition signals) provided at the time of secondary exposure can be tuned to preferentially activate naive B cells over memory B cells by biasing the cytokine environment. Specifically, high TLR7/TLR8 signal (single-stranded RNA motifs) drives plasmacytoid dendritic cells to produce IFN-alpha, which paradoxically SUPPRESSES memory B cell proliferation while PROMOTING naive B cell activation. This creates a "window of opportunity" for naive B cells to compete. The paper explicitly frames this as a vaccine design strategy for overcoming OAS in influenza universal vaccine design.

**Mathematical model (Altan-Bonnet / Chakraborty group framework):**
GC dynamics under OAS conditions can be modeled as:

    dM/dt = r_M * [Ag] * (K_M + [Ag])^{-1} * M - delta_M * M
    dN/dt = r_N * [Ag] * (K_N + [Ag])^{-1} * N - delta_N * N

where M = memory clone population, N = naive clone population, K_M < K_N (memory has lower half-saturation constant for antigen), r_M > r_N (memory has faster proliferation). With K_M < K_N, at any realistic [Ag], M dominates. The mitigation acts on r_M: suppressing memory proliferation rate (r_M -> r_M * eta, eta < 1) via IFN-alpha signaling shifts the balance.

### 3.2 Substrate analog of OAS — the seeding window bias

The substrate has a structural analog of all three OAS tiers:

**Tier 1 analog: Seeded bindings accumulate confidence before deployment.**
During the seeding window (initial KB construction), bindings are created from large structured corpora (Wikipedia, Wikidata). These bindings are immediately validated: queries during the validation phase probe seeded facts primarily. Each successful retrieval increments the confidence score of the seeded binding. By deployment time, seeded bindings have confidence scores derived from many validation-phase retrievals.

Post-deployment, new bindings start at minimum confidence (no query history). They must accumulate retrieval history to compete. In contradiction scenarios, the adversarial ranking uses confidence delta as the triage signal (Extension 2 from 5x note). A new binding that correctly identifies an outdated seeded fact as wrong will be de-prioritized because its confidence score is lower than the seeded binding it contradicts.

This is OAS tier 1: seeded bindings have lower effective activation threshold by virtue of prior confidence accumulation.

**Tier 2 analog: Sleep defrag preferentially reinforces high-confidence bindings.**
During sleep defrag, bindings are aggregated and compressed. Higher-confidence bindings are more likely to survive aggregation (they are the "centroids" in the compression step). Lower-confidence new bindings are more likely to be merged into existing high-confidence centroids rather than forming their own stable cluster. The GC competition dynamics apply directly: new bindings compete for "centroid slots" in the defrag embedding space; high-confidence seeded bindings already occupying centroid positions exclude new challengers.

**Tier 3 analog: KB niche occupation.**
At fixed N (vector dimensionality), the effective capacity of the binding store is bounded. If the N-dimensional space is already well-occupied by seeded bindings with high separation margins, new bindings find less favorable positions (closer to existing centroids, lower retrieval precision). This is the physical niche competition analog.

**Why this matters for product reliability:**
A customer loads their enterprise KB. The initial seeding creates hundreds of authoritative bindings. Over 6 months, the domain evolves — regulations change, data is updated, new entities emerge. The updated facts should replace outdated seeded facts. But OAS dynamics mean the outdated seeded facts resist replacement: they have high confidence from 6 months of successful queries, they dominate defrag centroid allocation, and their confidence is never decayed because the current substrate has no decay mechanism.

The adversarial mode (cycle 167 HP) can detect the contradiction between old and new facts. But Extension 2 triage RANKS the alert by confidence delta: high-confidence (old seeded) vs low-confidence (new post-deployment). The OLD fact receives a LOWER contradiction priority because the new fact has lower confidence. The alert fires in the wrong direction: the customer is told to verify the new fact, not the old one.

This is the OAS failure mode fully articulated: the substrate's memory management will systematically protect outdated high-confidence bindings against correct low-confidence corrections unless a confidence decay mechanism is implemented.

### 3.3 The mitigation: confidence decay + innate-cofactor separation

**Mitigation 1: Confidence decay for seeded bindings (direct OAS analog)**

Implement a per-binding age-weighted confidence decay:

    c_t = c_0 * alpha^n

where c_0 is the confidence at seeding time, alpha is the decay factor (0.90-0.99 per defrag cycle), and n is the number of defrag cycles elapsed since the binding was established.

This decays the competitive advantage of seeded bindings over time, allowing post-deployment high-quality bindings to catch up. The decay is NOT applied to confidence scores used for retrieval quality (those remain undecayed for user-facing precision); it is applied ONLY to the conflict priority scoring in the adversarial ranking.

Two-tier confidence: c_retrieval (undecayed, used for retrieval precision) and c_adversarial (age-weighted decayed, used for conflict priority ranking). Seeded bindings keep their retrieval quality but lose their competitive advantage in adversarial triage over time.

**Mitigation 2: Innate cofactor separation — hard-coded conflict priority for domain-change events**

When a customer signals a domain change (regulatory update, product launch, data refresh), the substrate enters a temporary "naive window" analogous to the IFN-alpha-mediated suppression in the eLife paper. During this window:
- New bindings loaded in the current refresh cycle receive a temporary confidence boost (c_naive_window = c_base * 2.0 for adversarial triage purposes only)
- Old seeded bindings from the previous epoch receive a temporary confidence suppression (c_seeded * 0.5 for adversarial triage purposes only)
- Window duration: N defrag cycles (N configurable; default 3)
- After the window, all confidence values return to their natural age-weighted trajectory

This is the direct substrate implementation of the eLife 2025 mitigation: the "innate cofactor" is the domain-change signal; its effect is to temporarily invert the memory vs naive competitive advantage, allowing the new facts to establish themselves in the GC (defrag centroid competition) before the window closes.

**Mitigation 3: Anti-idiotype contradiction detection (Jerne network analog)**

Before raising an alert that "new binding A contradicts old binding B," compute whether A is also in an anti-idiotype relationship with any OTHER bindings in the store (not just B). If A contradicts B but is consistent with C, D, E (other bindings about the same entity), the alert priority should be INCREASED (the network is providing convergent evidence that B is wrong). If A contradicts B but is also inconsistent with C, D, E (A is globally inconsistent), the alert priority should be DECREASED (A may be noise, not a genuine correction).

This adds a network-level coherence signal to the adversarial ranking. It is the Jerne idiotype network applied as a meta-validator: the network's internal consistency (do most bindings agree with A or with B?) provides a prior on alert validity.

Mathematical form: coherence(A, B) = |{C : cos(A, C) > 0.7}| - |{C : cos(B, C) > 0.7 AND cos(A, C) < 0.3}|. Positive coherence favors A over B in the conflict; negative coherence favors B.

### 3.4 Cross-reactive structural invariants — the burial depth principle

**From bnAb structural biology:**
The conserved epitopes targeted by broadly neutralizing antibodies (bnAbs) share one consistent geometric property: they are buried. The HIV gp120 CD4 binding site, the influenza hemagglutinin stem, and the SARS-CoV-2 RBD cryptic epitope (3D1 antibody, Nature Comms 2025) are all partially or fully occluded from the molecular surface. Why must they be conserved? Because they are FUNCTIONALLY CONSTRAINED — they are part of the machinery of viral entry, and mutations at these sites abolish viral fitness. Evolution cannot mutate them.

An antibody that binds a buried, functionally constrained epitope will therefore bind ALL viral variants, because all variants must maintain the epitope for functional reasons.

Mathematical generalization: a binding target that is conserved across variants is one that is REQUIRED for the function of the entity it belongs to. "Buried" in molecular terms = "load-bearing" in functional terms. Variants that mutate load-bearing regions lose function.

**Substrate analog: semantic load-bearing positions**

Every concept has "load-bearing" semantic features — features without which the concept cannot function as that concept. For "contract", load-bearing features include: parties, obligations, consideration. These cannot be absent without the entity ceasing to be a contract. "Surface" features (specific dates, names, formats) can vary arbitrarily.

A binding that targets load-bearing semantic features will exhibit cross-variant recall (across paraphrases, domains, surface formats) because the load-bearing features are always present. A binding targeting surface features will fail on paraphrase.

**Engineering implication: load-bearing feature extraction**

For each concept cluster in the KB, identify the features present in >= 90% of all surface variants (load-bearing candidates). Bindings that are aligned with these features should receive: (a) higher initial confidence (they generalize better), (b) immunity from the confidence decay mechanism (they are the "buried conserved epitopes" of the KB), (c) cross-variant retrieval.

The surgical insight: OAS mitigation (decay seeded bindings) and bnAb generalization (protect load-bearing bindings) are NOT in conflict if they target different binding types. Seeded bindings should decay for surface-level features but NOT for load-bearing features. This requires a feature-type tag on bindings: surface vs load-bearing. Load-bearing bindings are permanent, surface bindings are age-weighted.

This two-class binding architecture is the most important engineering output of this drill. It reconciles the OAS mitigation (which could naively decay important foundational facts) with the cross-reactive generalization goal (which requires permanent high-confidence anchors).

### 3.5 Trained innate immunity — the substrate "two-speed memory" formalization

**Mechanism:**
Netea et al. (2016+; Immunological Reviews 2024) demonstrate that macrophages and monocytes undergo epigenetic reprogramming after first exposure: histone H3K4me3 marks at promoters of key cytokine genes are modified, enabling faster transcriptional response on re-exposure. The key properties: (a) the modification persists for months without antigen re-exposure, (b) the modification is NOT receptor-specific (it enhances general response magnitude, not epitope specificity), (c) it is initiated by metabolic switches (aerobic glycolysis via mTOR/HIF-1alpha) not receptor engagement.

This is a distinct memory type from adaptive B-cell memory:
- Adaptive (B-cell) memory: receptor-specific, slow to establish (7-14 days for GC), durable, exquisitely specific
- Trained innate memory: receptor-agnostic, fast to establish (24-72h), medium duration (months), broad sensitivity

**Substrate analog: two-speed adversarial memory**

The substrate currently has one adversarial memory speed: per-query contradiction detection (adaptive, receptor-specific analog). The trained innate memory analog is a missing second tier:

FAST layer (current, adaptive analog): per-binding contradiction detection using cosine distance + confidence thresholds. Specific to binding pairs. Updates on every query.

SLOW layer (new, trained innate analog): a batch-updated adversarial fingerprint tensor that captures the statistical distribution of contradiction types seen in the past 24-48 hours. Not specific to individual binding pairs. Updated on 1-hour batch cycle. Provides elevated sensitivity to recurring contradiction PATTERNS even when the specific binding pair involved is novel.

The slow layer works like epigenetic priming: if the substrate has been seeing many time-based contradictions (facts from year X vs facts from year Y), the slow layer's fingerprint reflects this pattern and primes the fast layer to be more sensitive to time-based conflicts. New time-based conflicts are detected faster (lower activation threshold) even if neither binding is familiar.

**Formalization:**
Let F_t be a fingerprint vector of dimension D_fingerprint, updated as:

    F_t = beta * F_{t-1} + (1 - beta) * f(recent_contradiction_vectors)

where f() is a function that extracts the statistical pattern of recent contradictions (e.g., mean of contradiction direction vectors in embedding space), and beta = 0.95 (slow decay, 24-hour half-life at 1-hour batch cadence).

Slow-layer activation: when a new potential contradiction is detected, compute:

    slow_boost = cos(new_contradiction_direction, F_t)

If slow_boost > threshold (e.g., 0.7), multiply the conflict priority score by a factor > 1 (e.g., 1.5x). This is the epigenetic priming effect: recurring contradiction types receive elevated triage priority.

---

## Cross-thread synthesis with prior drills

### OAS links to hippocampal-cortical consolidation (prior analog 1)
The hippocampal-cortical replay mechanism (prior drill) describes how memories are replayed during sleep to consolidate them. OAS dynamics mean that WHICH memories get replayed preferentially shapes which ones persist. If replay preferentially rehearses high-confidence (seeded) bindings (analogous to offline replay of well-practiced memories), OAS is being REINFORCED during sleep defrag. The mitigation: defrag's replay selection must sample proportionally across all confidence tiers, not just high-confidence bindings. This is a concrete implementation instruction for the sleep defrag module.

### Buried epitopes link to adversarial clustering (Extension 5 from 5x note, GC clustering)
Extension 5 (germinal center alert clustering) groups adversarial alerts by cosine similarity. The burial depth principle refines this: the clustering should weight alerts about LOAD-BEARING features more heavily than alerts about surface features. Two alerts — one about a load-bearing feature and one about a surface feature — should NOT be merged into the same cluster, because their implications are different: a load-bearing contradiction is a fundamental conflict; a surface contradiction may be a paraphrase.

### Trained innate immunity links to concept drift (cycle 170 HP)
Cycle 170 HP validates concept drift detection. The trained innate analog (slow adversarial fingerprint) provides a two-speed enhancement to drift detection: the slow layer detects drift PATTERN accumulation before individual bindings cross the drift threshold. This is early warning: if the slow fingerprint shows increasing cosine distance in a particular semantic direction, a drift alarm can be raised before any individual binding has formally drifted. Pre-emptive drift detection, not just reactive.

### OAS failure mode links to autoimmune disease (prior note, section 5.1)
The prior 5x note identifies autoimmune disease as the most important failure mode: the immune system attacks self. OAS is the PRIOR failure mode that enables autoimmune patterns to establish: first-exposure bias causes certain self-patterns to be classified as authoritative (self) before better evidence arrives. OAS mitigation is therefore the prerequisite for preventing autoimmune-analog cascades. Sequence: deploy OAS mitigation (confidence decay + naive window) first; then deploy protected binding exemption (Extension 3); the combination prevents both OAS false-protection (outdated facts resisting update) AND autoimmune false-attack (authorized facts being flagged).

---

## Substrate-product implications

**Implication 1: Memory freshness SLA**
The OAS analysis enables a formally groundable "memory freshness" SLA: the substrate can guarantee that seeded bindings older than T defrag cycles have their adversarial priority decayed to below a specified threshold, ensuring they cannot block legitimate corrections indefinitely. This is a concrete, measurable product promise: "your KB self-corrects within N days of deploying an update, guaranteed."

**Implication 2: Load-bearing vs surface binding classification as a product feature**
The burial-depth analysis motivates a customer-facing feature: "load-bearing fact detection." The substrate identifies which facts in a KB are load-bearing (high cross-variant coherence, present across most surface formats) vs surface (specific, variant-dependent). Customers can review the load-bearing classification and confirm or override it. This serves regulated industries (financial, legal, pharmaceutical) where the distinction between foundational rules and specific instances is operationally critical.

**Implication 3: Two-speed adversarial memory as product differentiator**
The trained innate analog (slow adversarial fingerprint) creates a product pitch: "the substrate gets better at detecting contradictions in YOUR domain the longer it runs, without any explicit training step." This is differentiated from both (a) static rule-based systems (which never improve) and (b) fine-tuned ML models (which require expensive labeled training data). The slow fingerprint accumulates from deployment activity automatically. Customer value: day-30 adversarial performance is materially better than day-1 performance, at zero incremental cost.

**Implication 4: OAS mitigation as EU AI Act compliance**
EU AI Act Art 12 requires audit trails. The confidence decay mechanism creates an audit-relevant record: every binding has a creation timestamp and a current adversarial priority score, with the decay function defining how priority evolves over time. Auditors can verify: "was this outdated binding given lower adversarial priority than this correct new binding by the time the contradiction was raised?" The decay function makes this answer checkable. This is an Art 12 compliance feature with direct engineering specification.

---

## Engineering rank-order (new extensions from this drill)

| Extension | Mechanism | P_deflated | Cost | Priority |
|---|---|---|---|---|
| OAS mitigation: confidence decay | Two-tier confidence (retrieval vs adversarial); age-weighted decay for seeded bindings | 0.45 | 2-3 days | 1 — prerequisite for other adversarial features |
| Load-bearing binding classification | Identify bindings present in >= 90% of entity surface variants; exempt from decay | 0.50 | 3-5 days | 2 — required to make decay safe |
| Naive window on domain-change signal | Temporary confidence inversion on KB refresh events | 0.45 | 1-2 days | 3 — high customer value |
| Anti-idiotype coherence scoring | Network consistency prior on adversarial alerts | 0.35 | 3-4 days | 4 — enhancement to ranking |
| Two-speed adversarial memory (slow fingerprint) | Batch-updated contradiction pattern vector; trained innate analog | 0.35 | 1 week | 5 — differentiating long-run feature |
| Replay sampling across confidence tiers | Defrag sleep replay samples uniformly, not high-confidence-biased | 0.55 | 1-2 days | 6 — addresses OAS amplification in defrag |

---

## HARD-PASS / HARD-FAIL summary (pre-registered, this drill)

| Prediction | P_deflated | HARD-PASS | HARD-FAIL |
|---|---|---|---|
| OAS bias exists today | 0.60 | >= 60% incorrect seeded facts retained without decay after 10 cycles | < 20% retained (no OAS) |
| Decay restores correction | 0.45 | >= 80% correction within 10 cycles; < 3% correct-fact degradation | No alpha in [0.80, 0.99] works |
| Burial depth invariant | 0.50 | Deep bindings cross-variant recall >= 0.85 vs surface < 0.50 | < 10 pp difference |
| Two-speed adversarial memory | 0.35 | TPR day 7 >= 0.75 vs day 1 < 0.50; monotonic improvement | No improvement past day 1 |
| Anti-idiotype coherence signal | 0.25 | Anti-binding density > 2%; r >= 0.60 with alert rate | Density < 0.5% OR r < 0.20 |

---

## Citations (verified from lit-scan)

1. Burnett et al. (2025) "Innate immunity and training to subvert original antigenic sin by the humoral immune response." eLife. https://pmc.ncbi.nlm.nih.gov/articles/PMC12393886/
2. Vierra et al. (2025) "Frontiers in Immunology: Factors determining the outcomes of immune imprinting after repeated orthoflavivirus infections." https://www.frontiersin.org/journals/immunology/articles/10.3389/fimmu.2025.1560851/full
3. Huang et al. (2024) "Immune imprinting: The persisting influence of the first antigenic encounter with rapidly evolving viruses." Human Vaccines & Immunotherapeutics. https://www.tandfonline.com/doi/full/10.1080/21645515.2024.2384192
4. Carreno et al. (2025) "Broadly neutralizing antibodies targeting a conserved silent face of spike RBD resist extreme SARS-CoV-2 antigenic drift." Cell Reports. https://www.cell.com/cell-reports/fulltext/S2211-1247(25)00719-3
5. Nature Communications (2025) "A broadly neutralizing antibody recognizes a unique epitope with a signature motif common across coronaviruses." https://www.nature.com/articles/s41467-025-63101-1
6. npj Systems Biology (2025) "Machine learning framework to extract physicochemical features of B-cell epitopes recognized by a cross-reactive antibody." https://www.nature.com/articles/s41540-025-00583-1
7. Frontiers in Cellular and Infection Microbiology (2026) "A computational pipeline to discover potential cross-reactive antibodies." https://www.frontiersin.org/journals/cellular-and-infection-microbiology/articles/10.3389/fcimb.2026.1692727/full
8. Vuscan et al. (2024) "Trained immunity: General and emerging concepts." Immunological Reviews. https://onlinelibrary.wiley.com/doi/10.1111/imr.13326
9. Journal of Allergy and Clinical Immunology (2024) "Trained innate immunity: Concept, nomenclature, and future perspectives." https://www.jacionline.org/article/S0091-6749(24)00943-6/fulltext
10. Nature Cell Research (2025) "Trained immunity: induction of an inflammatory memory in disease." https://www.nature.com/articles/s41422-025-01171-y
11. Francis Jr. T. (1960) "On the doctrine of original antigenic sin." Proceedings of the American Philosophical Society 104(6):572-578. [Foundational]
12. Jerne N.K. (1974) "Towards a network theory of the immune system." Ann. Immunol. 125C:373-389. [Foundational]
13. bioRxiv (2025) "Replaying germinal center evolution on a quantified affinity landscape." https://www.biorxiv.org/content/10.1101/2025.06.02.656870v2
14. PMC (2024) "An HIV-1 broadly neutralizing antibody overcomes structural and dynamic variation." npj Viruses. https://www.nature.com/articles/s44298-023-00002-4
15. Frontiers in Immunology (2025) "The past, present, and future of anti-idiotype antibodies." https://www.frontiersin.org/journals/immunology/articles/10.3389/fimmu.2025.1686107/full

Verified citation count: 15

---

## Next-drill candidate

The OAS mathematical model (GC population dynamics with asymmetric activation thresholds) maps directly onto the `population-genetics-wright-fisher` Tier-1b field: the competition between memory B cells and naive B cells under OAS is a Wright-Fisher dynamics problem where the "allele" is the binding type (seeded vs post-deployment) and selection is the confidence-weighted retrieval advantage. Fixation probability theory (Kimura 1962) gives the exact probability that a low-confidence correct binding will displace a high-confidence incorrect binding at a given population size (KB size) and selection coefficient (confidence delta). This is the mathematical ground truth for how aggressively the confidence decay parameter alpha must be set.

Recommended: dispatch a `population-genetics-wright-fisher` drill specifically targeting fixation probability of a low-fitness invader vs high-fitness resident under memory B cell competition dynamics. The result would give the alpha parameter selection criterion from first principles.
