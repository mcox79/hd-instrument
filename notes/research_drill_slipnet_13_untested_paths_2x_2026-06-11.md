# Research drill 2x DEEP — slipnet polysemic 13 untested substrate-only paths + disjoint-vocab SME methodology

Date: 2026-06-11
Topic: Operational deepening of the 13 substrate-only paths flagged after the WN18RR refutation of the "0.42 clean architectural ceiling" framing for polysemic cross-domain analogy. Tier-1 priority methodology drill.
Scope: ASCII-only output. Generic literature only. No project-specific numerical predictions.

## HEADLINE

Polysemic cross-domain analogy on a substrate-only stack is not a fixed-architecture problem; it is a fusion-over-roles + factorization-under-superposition problem. Across the 13 untested paths, the highest-yield candidates cluster into three families: (1) RANK-FUSION-OVER-ROLES (per-role-RRF, TSE argmax voting, summed-similarity TTR with role normalization), (2) ITERATIVE FACTORIZATION (resonator-network cleanup, recurrent dynamic-similarity VSA circuits), and (3) STRUCTURAL CONSTRAINT (one-to-one mapping, systematicity-weighted higher-order alignment). The single most important methodology gap is DISJOINT-VOCABULARY evaluation: every benchmark currently in use leaks lexical overlap which lets shallow surface similarity carry signal that masquerades as structural mapping. Without disjoint-vocab probes, the substrate's "polysemic ceiling" claim is unfalsifiable.

## Cheap decisive test

Construct a disjoint-vocabulary analogy probe (recipe in Section 5 below). Apply each of the top-5 substrate-only paths in parallel on the same probe. The decisive test is: which paths show LIFT over random on disjoint-vocab while baseline summed-cosine collapses to near-chance. A path that retains lift under vocabulary disjointness is doing structural work; a path that collapses with the baseline is doing surface-similarity work. Per-path operating cost is dominated by setup (substrate-internal: items, roles, binding) plus a single iteration sweep; no external model required.

Test specification:
- Source domain D_S and target domain D_T share NO surface tokens.
- Both domains share a relational schema (same roles, same higher-order structure).
- Query: from a base structure in D_S, retrieve the analog in D_T (or fill a missing role-filler).
- Per-path output: top-k accuracy at k in {1, 5, 20} and a per-role recall vector.

## 1. The 13 untested substrate-only paths — operational drill

Paths grouped by family. For each path I name the mechanism, what it operationally adds beyond plain summed-similarity TTR, and a tractability note. Paths marked [HIGH] are the recommended pilot set.

### Family A — Rank-fusion over roles (cheapest, most under-explored)

A1. PerRole-RRF (reciprocal rank fusion across role-channels) [HIGH]
- Mechanism: For each role r in the query, unbind the role from the query bundle, query the substrate against the per-role pool, get a ranked list R_r. Fuse the lists by RRF(item) = sum_r 1/(k0 + rank_r(item)) with k0 ~ 60 (standard).
- Why it helps polysemy: RRF is rank-based and scale-free, so a role-channel where the polysemous filler ambiguates similarity gets DOWN-WEIGHTED relative to roles that produce a sharp rank-1 hit. Polysemy in one role does not poison the global score.
- Tractability: O(|roles| * pool-lookup). No new substrate machinery. Drop-in on existing per-role unbind path.

A2. TSE (top-k role-set ensemble; argmax voting) [HIGH]
- Mechanism: Per role unbind + per-role argmax in the substrate pool. The target item with the most role-wise argmax votes wins. Ties broken by sum-of-cosines.
- Why it helps polysemy: hard-voting ignores graded similarity entirely — only the per-role winner counts. Polysemous fillers that produce a soft maximum still cast a single vote, removing the long-tail interference that biases summed similarity.
- Tractability: trivial.

A3. TTR with role-normalized similarity (centered/whitened per role) [HIGH]
- Mechanism: Per role, z-score (or ZCA-whiten) the similarity vector over the pool BEFORE summing. The summed-similarity TTR baseline assumes similarity scales across roles are comparable; they are not when role pools differ in size or density. Normalizing per role restores comparability.
- Why it helps polysemy: removes the per-role base-rate bias that polysemous-role similarity distributions inflate (cf. cycle 226 ZCA win on freq-decay).
- Tractability: trivial; ~30 lines.

A4. PerRole-Borda / weighted voting
- Mechanism: like TSE but each role contributes points equal to (|pool| - rank). Smoother than argmax, more robust than summed similarity to scale issues.
- Why it helps polysemy: middle ground between A1 and A2. Worth running but lower expected lift than the top 3.
- Tractability: trivial.

A5. Per-role confidence-gated fusion
- Mechanism: weight each role's contribution by an entropy or top1-minus-top2 confidence score over its per-role similarity distribution. Low-confidence (polysemous) roles get down-weighted.
- Why it helps polysemy: explicit polysemy detector; routes around weak channels.
- Tractability: trivial; complements A1/A3.

### Family B — Iterative factorization / resonator-style cleanup

B1. Resonator-network cleanup over the query bundle [HIGH]
- Mechanism: treat the query as a superposed product over (role x filler) factors; iterate {predict factor i, project to item memory, replace} until convergence. Frady-Kanerva-Olshausen resonator dynamics. This is exactly designed for the case where one of the factors is polysemous.
- Why it helps polysemy: the cleanup step at each iteration projects predictions onto valid item memory, which DISAMBIGUATES a polysemous filler by forcing it into the discrete codebook of stored fillers. The other factors in the bundle act as constraints that pick the right disambiguation.
- Tractability: well-established algorithm, ~50-100 lines on top of existing substrate unbind. Convergence in O(10-100) sweeps for typical factor counts.

B2. Recurrent dynamic-similarity VSA circuit (subgraph isomorphism via VSA)
- Mechanism: build a recurrent circuit whose dynamics evolve internal substitution vectors; converged fixed points correspond to maximal subgraph isomorphisms between source and target structures. (Literature: Frady-Kleyko-Sommer family extensions.)
- Why it helps polysemy: structural rather than feature based — polysemy at the filler level is irrelevant once relational alignment dominates.
- Tractability: substantially more engineering than B1; recommend only after B1 result.

B3. Hopfield-cleanup interleaved with role-cycling
- Mechanism: after per-role unbind, route through a modern-Hopfield cleanup (exponential capacity) before similarity scoring. Cycle through roles.
- Why it helps polysemy: cleanup converts soft polysemous response into the nearest discrete filler before similarity sums, which is mathematically equivalent to a hard argmax in similarity space but operating in vector space first.
- Tractability: needs modern-Hopfield primitive (already in scope per memory).

### Family C — Structural constraint (SME-substrate hybrid)

C1. One-to-one mapping enforcement on top of summed similarity [HIGH]
- Mechanism: after summed-similarity TTR scores all candidate (source-item, target-item) pairs, solve a maximum-weight bipartite matching (Hungarian, n^3, trivially fast at these sizes). The classic SME structural-consistency constraint.
- Why it helps polysemy: a polysemous filler may have high similarity to multiple targets, but one-to-one enforcement forces the global mapping to allocate it to its best fit, freeing the runner-up target to claim its second-best source. This is the single most important SME constraint and is purely a POST-PROCESS on substrate-internal scores.
- Tractability: scipy.optimize.linear_sum_assignment, ~10 lines.

C2. Systematicity-weighted higher-order alignment
- Mechanism: weight match-hypotheses by the count and connectivity of higher-order relations they participate in (Falkenhainer-Forbus-Gentner SES surrogate). In substrate terms: bind not only role-filler pairs but role-of-relation pairs, then score matches by how many higher-order bindings they preserve.
- Why it helps polysemy: a polysemous filler that participates in a higher-order relation (causal, schema-level) is disambiguated by the higher-order constraint; this is the "kernel growing" idea from SME.
- Tractability: requires higher-order substrate bindings — already supported.

C3. Pragmatic centrality weighting
- Mechanism: weight per-role similarity by a centrality score over the relation graph (e.g., PageRank of the role within the source-domain schema). Roles central to the query get higher weight.
- Why it helps polysemy: a polysemous filler in a peripheral role contributes less noise; a clean filler in a central role contributes more signal. SME's pragmatic constraint, made substrate-cheap.
- Tractability: precompute centrality offline; per-query is a weighted sum.

### Family D — LISA-inspired and probabilistic

D1. LISA-style synchrony-emulation (sequential role activation with temporal binding)
- Mechanism: instead of binding all role-filler pairs simultaneously, activate them in sequence and let the substrate's temporal policy (already validated in cycle 226) act as a synchrony-emulator. The substrate's TEMPORAL primitive can serve the same disambiguation role as LISA's synchronized firing of semantic units.
- Why it helps polysemy: the LISA insight is that bindings are dynamic and can be created/destroyed on the fly; this lets the same filler vector serve different roles at different times, which is exactly polysemy management.
- Tractability: leverages an already-validated substrate primitive; ~100 lines of orchestration.

D2. PAM-style Bayesian probabilistic graph matching (Lu-Ichien-Holyoak 2022)
- Mechanism: treat analogical mapping as posterior inference over discrete mapping variables; substrate provides the likelihood factors (per-pair similarity), and a constraint-satisfaction loop yields the MAP mapping.
- Why it helps polysemy: explicit probabilistic accounting for filler ambiguity; can mix prior schema knowledge with substrate-derived likelihoods.
- Tractability: medium — needs a small CSP/Bayes loop; competitive with C1 but heavier engineering.

## 2. SME methodology drill: what disjoint-vocabulary adds

Standard analogy benchmarks (including WN18RR and FB15K-237) suffer from massive surface overlap between query and target. Lexical-overlap analyses (Liu et al. type) show that vocabulary overlap predicts a large fraction of "cross-domain" performance. This means any substrate-only path that scores well on these benchmarks may be doing the wrong work.

Disjoint-vocabulary SME is the methodological cleanup: query and target use entirely separate token inventories, but share a relational SCHEMA. The only signal available is structural. This is the test SME was designed for, and it is the test that lets us distinguish:
- A path that ALIGNS STRUCTURE (e.g., A1, A3, B1, C1, C2) — should retain lift.
- A path that EXPLOITS SURFACE (e.g., raw cosine summed-similarity, retrieval by item-identity) — should collapse to near chance.

SME's foundational result is exactly this: when surface features are stripped, systematicity and one-to-one mapping are the constraints that recover the analogy. Substrate-only paths must inherit those constraints (Family C) or replicate the effect via rank-fusion (Family A) and factorization (Family B).

## 3. Cross-domain neighbor methods (briefly verified)

- LISA (Hummel-Holyoak): distributed binding via synchrony — substrate temporal policy is the natural emulator.
- Copycat / Metacat (Hofstadter-Mitchell): stochastic codelet workspace; not a clean substrate analog but the "abstract perception" framing maps to iterative substrate cleanup.
- IDyOT (Wiggins): information-dynamics framework; orthogonal, low priority.
- ICARUS (Langley): not analogy-centric; deprioritize.
- Resonator networks (Frady-Kanerva-Olshausen): direct substrate fit; this is Family B above.
- Relational Graph Transformer / Relational Attention (Diao-Loynd, Dwivedi-Jaladi-Shen 2026): demonstrates that transformer attention IS role-filler binding; reinforces that VSA-style fusion-over-roles is the right family.
- PAM (Lu-Ichien-Holyoak 2022): probabilistic graph matching on semantic relation networks; directly informs D2.
- VAEC (Webb-Dulberg-Frankland 2020) and A-I-RAVEN (Maczura et al. 2024): visual extrapolation benchmarks with controlled distribution shifts; templates for our disjoint-vocab probe design.

## 4. Ranked top-5 substrate-only paths for empirical pilot

Ranking criterion: P_deflated(lift > random on disjoint-vocab) x ease-of-implementation - novelty-cap penalty.

1. C1 — One-to-one mapping via Hungarian on summed-similarity. P_deflated = 0.50 (capped by novel-synthesis rule). Strongest theoretical grounding (SME core constraint), trivial implementation, immediate diagnostic. HARD-PASS threshold: lift over baseline >= 2x SE AND absolute disjoint-vocab top-1 lift > 1.5x chance. HARD-FAIL: lift within 1 SE of baseline.
2. A1 — PerRole-RRF. P_deflated = 0.45. Strongest expected polysemy robustness via rank-fusion. HARD-PASS: top-5 accuracy lift > 2x SE over summed-similarity AND retains lift when one role is artificially polysemized. HARD-FAIL: lift collapses under disjoint-vocab disambiguation noise.
3. B1 — Resonator-network cleanup over query bundle. P_deflated = 0.40. Most architecturally distinctive; aligns with substrate-product story. HARD-PASS: convergence in < 200 iterations on > 70% of disjoint-vocab queries AND top-1 lift > 2x SE. HARD-FAIL: non-convergence or no lift after cleanup.
4. A3 — Role-normalized (z-scored / ZCA-whitened) TTR. P_deflated = 0.40. Cheapest non-trivial fix; complements A1. HARD-PASS: lift > 2x SE over plain TTR. HARD-FAIL: lift within 1 SE.
5. C2 — Systematicity-weighted higher-order alignment. P_deflated = 0.35. Highest-novelty, biggest payoff if it works; substrate has the higher-order binding primitive already. HARD-PASS: lift > C1 alone AND lift scales with higher-order relation count. HARD-FAIL: no improvement over C1 baseline.

Calibration penalty applied (0.15-0.25 deflation; novel-synthesis cap 0.50) per lit-scan calibration discipline. None of these paths has published direct precedent for substrate-only polysemic disjoint-vocab analogy at production scale; treat all P values as theoretical with strong empirical-pre-test required.

Run order recommendation: C1 and A3 first (each is ~30 lines and serves as a baseline for the others). Then A1 + B1 in parallel. C2 last (most engineering).

## 5. Disjoint-vocabulary SME benchmark design

Generic template (substrate-product-neutral):

Step 1. Pick a relational schema with K roles (e.g., 4-6) and a known set of higher-order relations (e.g., causal, temporal, schema-membership). Examples: "predator chases prey" / "lawyer prosecutes defendant" share AGENT-ACTION-PATIENT plus causal-purpose higher-order structure.

Step 2. Generate N_source structures using vocabulary V_S and N_target structures using vocabulary V_T with V_S intersect V_T = empty. Each structure has the same role inventory but uses domain-specific fillers (e.g., biology-domain vs. legal-domain vocabularies).

Step 3. Pair structures across domains by manually-annotated structural analogy (gold mapping). Use 200-500 pairs for a tractable pilot.

Step 4. For each path: present source structure, ask substrate to retrieve top-k target structures. Measure top-1, top-5, top-20 accuracy AND per-role recall.

Step 5. Diagnostic conditions (run all paths against all four):
- (i) Baseline: same-vocabulary. All paths should perform well.
- (ii) Disjoint-vocabulary: V_S intersect V_T = empty. The decisive test.
- (iii) Polysemic-filler control: introduce K_poly fillers in V_S that are reused across roles. Tests polysemy specifically.
- (iv) Higher-order-stripped control: remove higher-order relations. Tests whether systematicity weighting (C2) actually depends on higher-order structure (HARD-FAIL of C2 if accuracy drops here).

Why this design is decisive:
- (i) -> (ii) gap measures surface-overlap reliance.
- (ii) -> (iii) gap measures polysemy robustness.
- (iii) -> (iv) gap measures higher-order dependence.
- Per-role recall vector diagnoses WHICH roles fail under each condition (critical for routing follow-up drills).

Existing benchmark seeds: SCAN (Scientific and Creative Analogies, Czinczoll et al. 2022) and VAEC (Webb et al. 2020) both have disjoint-vocab structure baked in. SCAN is the closest off-the-shelf disjoint-vocab analogy benchmark; recommended as the pilot dataset before constructing a custom one.

## 6. Falsifiable predictions with HARD-PASS / HARD-FAIL thresholds

HARD-PASS framework (any of the following, observed with lift > 2 SE):
- C1 (Hungarian one-to-one) provides lift over summed-similarity TTR on disjoint-vocab and the lift is GREATER on disjoint than on same-vocab. (Predicted: yes if structural constraint matters; no if substrate is doing surface work.)
- A1 (PerRole-RRF) lift is preserved when artificially polysemizing one role's filler distribution.
- B1 (resonator cleanup) converges on > 70% of disjoint-vocab queries within 200 iterations.
- A3 (role-normalized TTR) lifts over plain TTR with effect size that scales with role-pool-size heterogeneity.

HARD-FAIL framework (any of the following triggers a "this path does not add structural work" verdict):
- Path's disjoint-vocab top-1 within 1 SE of chance.
- Path's lift on disjoint-vocab is statistically smaller than its lift on same-vocab.
- Path's lift vanishes when higher-order relations are stripped (for C2 specifically).
- Resonator (B1) fails to converge on > 50% of queries (regime collapse).

If ALL five top paths HARD-FAIL on disjoint-vocab, the conclusion is: substrate-only polysemic cross-domain analogy is architecturally limited and the LLM-hybrid path is the honest answer. Note that this would be a SUBSTANTIVE refutation, not a re-statement of the earlier WN18RR result — because disjoint-vocab is the strictest possible structural test.

## 7. Cross-thread synthesis

- Builds on cycle 226 meta-finding (TEMPORAL + CONTEXTUAL primitives validate empirically; FIXED-ARCHITECTURE predictions tend to fail): Families A and B are CONTEXTUAL fusion methods; Family C is fixed-structural. The prediction is that A and B should outperform C if the cycle-226 pattern holds. Pre-register this expectation.
- Reinforces engineered-wrapper framing (memory 2026-06-11 substrate v3.2): all five recommended paths ride ON TOP of existing substrate algebra; none require core changes. Per-shard protection, multi-substrate fusion, and engineered importance all compose naturally with rank-fusion (A1) and resonator cleanup (B1).
- Connects to substrate-classical NLP finding (count-based methods stored as Tier-2 bundles beat phasor-only): the rank-fusion family (A1, A2, A3) is exactly the substrate-classical move applied to analogy.
- Reinforces drill-defeatism feedback (2026-06-11): polysemic cross-domain analogy was prematurely framed as architecturally closed. Ranking 13 paths with concrete per-path mechanisms is the correct response.

## 8. Substrate-product implications

If C1 (one-to-one mapping) is the dominant winner: ship as a 10-line post-process on retrieval. Trivial product win.

If A1 + A3 win: substrate API gains a "fuse-over-roles" call that returns RRF-fused top-k. Product-relevant because every customer query that involves multi-role retrieval benefits.

If B1 wins: substrate gains a "factorize-and-cleanup" primitive that disambiguates polysemic queries. Differentiates from LLM-only and from naive VSA libraries.

If C2 wins: substrate gains a higher-order-systematicity scoring path, which is the closest substrate has come to SME-style analogical reasoning. Highest novelty, most defensible against "this is just retrieval" framing.

If all five HARD-FAIL on disjoint-vocab: honest claim is "substrate is the memory and primitive layer; analogical mapping requires LLM front-end on disjoint-vocab cross-domain queries." This bounds the substrate-only NL boundary cleanly.

In all scenarios, the disjoint-vocab probe itself is a product asset: it is a clean, falsifiable, reproducible benchmark we can publish or use in customer demos to differentiate from systems that rely on surface overlap.

## 9. Citations (verified count: 12)

- Falkenhainer, Forbus, Gentner (1989) The Structure-Mapping Engine: Algorithm and Examples. Artificial Intelligence.
- Forbus, Ferguson, Lovett, Gentner (2017) Extending SME to Handle Large-Scale Cognitive Modeling. Cognitive Science.
- Hummel, Holyoak (2003) A Symbolic-Connectionist Theory of Relational Inference and Generalization. Psychological Review.
- Hummel, Licato, Bringsjord, Analogy Explanation and Proof.
- Lu, Ichien, Holyoak (2022) Probabilistic Analogical Mapping with Semantic Relation Networks. Psychological Review.
- Smolensky (1990) Tensor Product Variable Binding. Artificial Intelligence.
- Frady, Kent, Olshausen, Sommer (2020) Resonator Networks for Factoring Distributed Representations of Data Structures. arXiv:2007.03748.
- Kleyko et al. (2023) A comparison of vector symbolic architectures. AIR.
- Hofstadter, Mitchell (1990) The emergence of understanding in a computer model of concepts and analogy-making. (Copycat.)
- Webb, Dulberg, Frankland et al. (2020) Learning Representations that Support Extrapolation (VAEC). arXiv:2007.05059.
- Czinczoll et al. (2022) Scientific and Creative Analogies in Pretrained Language Models (SCAN). arXiv:2211.15268.
- Cormack, Clarke, Buettcher (2009) Reciprocal Rank Fusion outperforms Condorcet and individual rank learning methods. SIGIR. (RRF foundational.)

End of note.
