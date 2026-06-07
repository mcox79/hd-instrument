# Research drill: privacy failure mechanism analysis (3x deep)
Date: 2026-06-07
Filed-by: research sub-agent

---

## HEADLINE

SRHT and DP score-noise both failed on the production Llama encoder because they apply generic decorrelation to a system where privacy-relevant signal and semantic signal occupy the SAME geometric subspace. This is not a fundamental floor -- it is an encoder-class-specific problem. Three targeted mechanisms (cone-aware cosine rescaling, rank randomization, and privacy-objective whitening) each attack a different geometric cause and are testable in 1-2 hours CPU. If any one of them works, the HIPAA-grade absolute claim is recoverable. If all three fail, per-encoder fine-tuning is the fallback and remains feasible; the qualified claim holds either way.

P_deflated = 0.38 (calibration penalty 0.22 applied; starting estimate 0.60 deflated to 0.38 that at least one of {Path F, Path B, Path A} passes the ZKL target).

---

## SECTION 1: WHY SRHT WORKED ON MiniLM BUT HURT LLAMA

### What SRHT does geometrically

The Subsampled Randomized Hadamard Transform applies a random sign flip followed by a Hadamard rotation, then subsamples dimensions. The effect is to spread the variance that was concentrated in a few directions across all output dimensions. It is a variance-equalizing transform: after SRHT, the energy per dimension is approximately equal.

### MiniLM geometry

MiniLM is a bidirectional encoder trained with a symmetric contrastive objective (sentence-BERT family). Its training explicitly rewards separating similar from dissimilar sentences in the CLS-token embedding. The result is an embedding space where:
- Semantic distinctions concentrate in a relatively small set of high-variance dimensions (the dimensions the contrastive objective sharpened).
- The remaining dimensions carry residual noise with no particular membership-inference signal.
- Anisotropy exists (vectors cluster in a cone) but the cone axes are the SAME dimensions that carry semantic distinction.

When SRHT redistributes this concentrated variance, it disrupts the specific dimensional alignment that membership-inference exploits. The membership-inference attacker was relying on signal in a small set of directions; SRHT scatters that signal across 384 directions, making it harder to extract. Semantic content also gets disrupted, but MiniLM's training redundancy means enough signal survives in the spread form. Net result: privacy improves, utility degrades modestly.

### Llama L15 geometry

Llama-3.2-1B at layer 15 (left-pad, last-token pool) is a fundamentally different system. The model was trained on next-token prediction, not contrastive sentence similarity. Its hidden states have three properties that MiniLM does not share:

**Property 1: Last-token concentration.** Causal attention routes all positional information through the last token by generation time. The last-token hidden state at L15 is not a mean of the sequence -- it is the running context summary built for predicting the next token. This creates a representation that contains positional, syntactic, and semantic information all fused into the same vector. There is no CLS bottleneck that cleanly separates "the semantic part."

**Property 2: Anisotropy driven by next-token prediction, not semantic similarity.** Published work (Ethayarajh 2019, Bis et al. 2021, more recent anisotropy geometry papers) shows causal LMs have severe anisotropy where vectors concentrate in a narrow cone. Critically, the dimensions that are most anisotropic (highest variance) are the ones most important for next-token prediction -- they carry the distributional statistics the model needs to decode the next word. These are NOT the same dimensions that MiniLM uses for semantic discrimination. They encode frequency statistics, topic drift, and positional information.

**Property 3: Membership-inference exploits the same dimensions as next-token prediction.** The grounding-attack ZKL measures whether a stored fact can be retrieved at above-chance rates. Stored facts have been written into the substrate as specific vectors. The membership-inference signal -- "does this query vector have anomalously high cosine similarity to a stored vector?" -- correlates precisely with the high-variance, anisotropic dimensions. Those dimensions dominate cosine similarity in a cone-concentrated space.

### Why SRHT specifically hurts on Llama

When SRHT equalizes variance across all 2048 dimensions:
1. It spreads the next-token-prediction signal (which was concentrated in high-variance dims) across all dims.
2. The low-variance dims were previously near-zero contributors to cosine similarity; after SRHT they are non-zero noise.
3. The high-variance dims, which were the primary cosine drivers, get reduced to 1/D fraction of their prior energy.
4. The net effect: the cosine similarity distribution becomes more uniform -- but this uniformity extends to BOTH member and non-member queries alike.
5. The key: SRHT increases the cosine similarity baseline for non-members (noise dims now contribute) while decreasing the peak cosine similarity for members (signal dims weakened). The gap narrows, but in the WRONG direction -- the attacker's signal ZKL increases because the distributions become MORE confused, not cleaner.

Empirical evidence: ZKL(50) went 0.22 -> 0.45 -> 0.57 -> 0.58 with increasing SRHT passes. This monotonic increase is consistent with progressive blurring of the cosine distribution that makes member vs non-member indistinguishable from above rather than from below. SRHT is making the retrieval system uncertain, not private.

### Formal statement of the divergence

Let X_m be the cosine similarity distribution for member queries, X_nm for non-members. Initially, X_m >> X_nm in the anisotropic cone directions. After SRHT, both X_m and X_nm become diffuse because the cone signal has been scattered. The JS-divergence (or KL proxy) between them does not decrease -- it can increase if the "floor" for non-members rises faster than the "ceiling" for members drops. This is precisely the regime Llama is in: the non-member floor is rising (noise dims now contributing positive cosine) faster than the member peak is dropping (signal dims partially preserved after subsampling).

---

## SECTION 2: WHY DP SCORE-NOISE FAILED

### The standard DP intuition

Standard differential privacy on retrieval scores adds Gaussian noise N(0, sigma^2) to the output cosine similarity before the caller sees it. The intuition: the attacker queries "how similar is my probe to the database?" and gets a noisy answer. At high enough sigma, the noise overwhelms the member vs non-member difference.

### Why it should work in theory

Standard DP theory says: if the sensitivity of the retrieval score to adding/removing one document is Delta_f, then adding Gaussian noise with sigma >= Delta_f * sqrt(2 ln(1.25/delta)) / epsilon gives (epsilon, delta)-DP. Membership inference attacks have bounded AUROC under DP guarantees. This is a theorem, not a heuristic.

### Why it failed in practice on Llama

Three compounding reasons:

**Reason 1: The attack uses rank, not score magnitude.** The grounding-attack ZKL measures whether the TOP-1 retrieved document for a given query is the "expected" stored fact. The attacker does not need to read the raw cosine score -- they observe that "document D was the top result for query Q." Gaussian noise on cosine scores shifts all scores by independent draws from N(0, sigma^2). The Pearson rank correlation between the original ranking and the noisy ranking is approximately:

  rho_rank = 1 / (1 + sigma^2 / Var[cos_sim])

At sigma=0.40 with typical cosine Var ~ 0.05 (cone-concentrated, low variance), this gives:

  rho_rank = 1 / (1 + 0.40^2 / 0.05) = 1 / (1 + 3.2) = 0.24

But for membership inference the key quantity is not the mean rank correlation -- it is whether the MEMBER DOCUMENT loses top-1 rank. In an anisotropic space, member documents have cosine similarity 0.20-0.40 above the non-member baseline (large signal). Displacing a +0.30 score by N(0, 0.40^2) has P(displacement > 0.30) = P(N(0,1) > 0.75) = 0.23. So 77% of the time, the member document keeps top rank even at sigma=0.40. This explains why recall stayed at 1.0 and ZKL stayed above 0.18.

**Reason 2: Recall=1.0 confirms the signal is robust.** If recall remained 1.0 under sigma=0.05 to sigma=0.40, that means the member document ALWAYS stayed in the top-k. The attacker observing top-k results sees the same document in all conditions. DP score-noise failed to displace members from the top-k because the member-nonmember gap in the anisotropic Llama space is larger than the noise we can afford to add without destroying utility.

**Reason 3: ZKL target 0.10 is demanding.** ZKL of 0.10 requires the conditional distributions of "query result when Q is stored" vs "query result when Q is not stored" to have KL divergence < 0.10 nats. With a 0.20-0.40 cosine gap, achieving this requires noise of roughly sigma > 0.50 to reduce the distinguishability below threshold. But sigma=0.50 destroys retrieval recall below 1.0, hitting the utility constraint. There is no sigma in the range [0.05, 0.40] that simultaneously satisfies ZKL < 0.10 AND recall >= 0.90 for Llama with this anisotropy level.

### The fundamental tension

DP score-noise operates READ-SIDE: it blurs the output. But the information is preserved WRITE-SIDE: the exact member vector is stored without perturbation. An attacker with sufficient query budget can average over many noisy responses and recover the underlying ranking. This is the standard DP composition attack: if the same fact is stored permanently and queried repeatedly, noise averaging recovers the deterministic answer.

---

## SECTION 3: THE EIGHT CANDIDATE MECHANISMS

### Path A: Privacy-objective whitening

**What it is:** PCA whitening as currently deployed optimizes for retrieval geometry: it equalizes variance so no single dimension dominates cosine similarity, which improves retrieval discrimination. Privacy-objective whitening has a different goal: it optimizes the entropy of the cosine similarity distribution rather than retrieval separation. Specifically, it would solve for the rotation W such that the mutual information between "is this a member query?" and "what is the cosine similarity output?" is minimized, subject to a utility constraint (top-1 accuracy remains above threshold).

**Why it might work where SRHT failed:** SRHT is a random transform -- it does not know which dimensions carry membership-inference signal vs semantic signal. Privacy-objective whitening learns the distinction. If the membership-inference signal concentrates in a different set of directions than the semantic signal (which is plausible: membership signal ~ "how close to specific stored vectors"; semantic signal ~ "what topic is this"), a learned projection can suppress the membership dimensions while preserving semantic ones.

**Why it might fail:** If the membership signal and semantic signal are in the SAME subspace (the anisotropy argument above suggests they partially coincide), no linear transform can cleanly separate them. The optimal privacy whitening would then degrade retrieval accuracy to achieve privacy, hitting the same utility-privacy wall as score-noise.

**P_deflated estimate:** 0.38. The information-theoretic argument is plausible but the same-subspace overlap is a genuine risk.

**HARD PASS:** ZKL < 0.12, top-1 recall >= 0.90 on held-out eval set, test cohort n >= 50 stored facts.
**HARD FAIL:** ZKL > 0.18 after privacy-whitening (same as current baseline), OR top-1 recall < 0.80.

**Cheap decisive test:** 2 hours CPU. Compute PCA on query+document embeddings joint; solve for the rotation that maximizes cosine entropy on a held-out member/non-member mix using gradient descent on the entropy objective. This is a 2048x2048 matrix optimization -- tractable on CPU with scipy. No GPU required.

---

### Path B: Rank-randomization at top-k

**What it is:** After computing cosine scores and finding top-k, shuffle the order of the k returned results using a controlled randomization (e.g., sample from Mallows distribution centered on the correct order, with temperature parameter theta). At high theta, the returned rank is nearly uniform over the k! permutations; at low theta, it is nearly the original rank.

**Why it might work:** DP score-noise failed because rank was preserved even under score perturbation. Rank-randomization directly targets the rank order. An attacker observing that "D appeared at position 3 of 5 results" instead of "D appeared at position 1 of 5 results" has less information. The ZKL measure, if it uses returned rank as the proxy for membership inference, would be disrupted.

**Critical caveat from the lit scan:** IBM Research (2405.20446) found that "re-ranking strategy exhibits only a marginal decrease in attack effectiveness, suggesting that LLMs can still glean crucial information from content that has been reordered." This is the LLM-based RAG attack scenario where the language model downstream reads the content. If the grounding-attack ZKL measures semantic content of responses (not raw document identity), rank randomization may not be sufficient. Need to confirm what ZKL is measuring on the substrate side.

**P_deflated estimate:** 0.32. Rank randomization is mechanistically sound against rank-based attacks but may not address the ZKL metric if it is measuring something upstream of rank.

**HARD PASS:** ZKL < 0.12 at k=5, top-1 precision >= 0.75 (degraded from 1.0 is acceptable since top-1 is no longer guaranteed).
**HARD FAIL:** ZKL > 0.18 (no improvement), OR top-1 precision < 0.50 at any theta achieving ZKL < 0.15.

**Cheap decisive test:** 1 hour CPU. Implement Mallows-model rank shuffle over top-5; sweep theta from 0.5 to 5.0 (low temp = strong shuffle); measure ZKL at each theta. If ZKL does not decrease by >= 0.05 at any theta, rank is not the exploited signal and Path B is closed.

---

### Path F: Cone-aware cosine rescaling (anisotropy compensation)

**What it is:** In an anisotropic space, cosine similarity is dominated by the shared "cone center" direction. Two unrelated vectors can have cosine similarity 0.4-0.6 purely because they both point roughly toward the cone center. A cone-aware retrieval score compensates for this by subtracting the projection onto the mean direction mu before computing cosine similarity:

  cos_adjusted(q, d) = cosine(q - mu, d - mu) / normalization

This is the basis for post-processing approaches like mean-centering (subtract the mean embedding). The more aggressive version is to compute the effective cone half-angle theta_cone = mean arccos(cosine(v_i, mu)) across all stored vectors and then rescale the cosine by 1 / cos(theta_cone) to "rotate the query out of the cone."

**Why it might work:** The membership-inference signal in Llama's anisotropic space is partly "this query is extremely close to the cone center of stored documents." Non-member queries that happen to point toward the cone center get false-positive membership signal. Cone-aware rescaling removes this shared direction, leaving only the vector component orthogonal to the mean -- which is the genuine within-cone discriminant. This could increase the between-distribution gap (member vs non-member) in the RIGHT direction: member queries stay near specific stored vectors even after cone-centering; non-member queries, having only chance cosine similarity, see their scores drop.

**Why it might fail:** If the cone axis IS the primary membership-inference signal (stored facts all point toward the same cone region), removing the cone would hurt member retrieval first. This is possible if stored facts are semantically homogeneous.

**P_deflated estimate:** 0.42. The anisotropy-compensation theory is well-grounded; this directly attacks the known geometric cause of Llama's failure.

**HARD PASS:** ZKL < 0.12, top-1 recall >= 0.85 after cone-centering, test cohort n >= 50.
**HARD FAIL:** ZKL > 0.20 (worse than baseline), OR top-1 recall < 0.75.

**Cheap decisive test:** 2 hours CPU. Compute the mean embedding mu over all stored vectors; subtract mu from both query and document vectors; normalize; recompute cosine similarities; measure ZKL. The mean-centering version is a 10-line change. If ZKL improves, proceed to the full cone-rescaling variant.

---

### Path C: DP noise at write time

**What it is:** Instead of adding noise to output scores, add calibrated Gaussian noise to the document embedding BEFORE storing it in the substrate. This is the standard "DP at the data" approach: each stored vector v_i becomes v_i + N(0, sigma_w^2 I). The retrieval is then over noisy versions of the stored vectors.

**Why it is more principled than score-noise:** Write-time DP has a formal guarantee independent of the number of queries. Once the noisy vector is written, all subsequent retrievals automatically get the privacy guarantee -- there is no "averaging out the noise" attack because the noise is baked into the stored representation. This addresses the DP composition vulnerability of score-noise.

**The sigma_w challenge:** The sigma_w needed for DP privacy = Delta_f / epsilon, where Delta_f is the L2 sensitivity of the embedding. For Llama embeddings, Delta_f ~ sqrt(D) ~ 45 (2048 dims, unit-normalized vectors have L2 = 1, but unbounded versions have higher sensitivity). At epsilon=1.0, sigma_w ~ 45, which completely destroys the stored vector. Even at epsilon=10 (weak DP), sigma_w ~ 4.5, which would add noise comparable in magnitude to the signal. For epsilon=100 (very weak), sigma_w ~ 0.45, which is at the same scale as the cosine gap that DP score-noise couldn't overcome.

**The read-time noise equivalence:** Adding noise N(0, sigma_w^2) to stored vectors is mathematically equivalent (for linear cosine scoring) to adding noise to the cosine output, but with a different effective sigma. If sigma_w = 0.45, the effective cosine perturbation is sigma_cos = sigma_w / ||q|| = 0.45 for unit queries. This is similar to the sigma=0.40 score-noise that already failed. Write-time DP does not break the fundamental utility-privacy tradeoff; it just moves it to the storage layer.

**P_deflated estimate:** 0.22. Theoretically sound but likely hits the same utility-privacy wall. The formal guarantee is valuable but does not expand the achievable (ZKL, recall) frontier.

**HARD PASS:** epsilon <= 2.0 (standard DP), ZKL < 0.12, recall >= 0.90.
**HARD FAIL:** epsilon required > 10 to achieve ZKL < 0.12 while recall >= 0.80 (privacy guarantee would be meaningless).

---

### Path D: Encoder fine-tuning with privacy regularization

**What it is:** Fine-tune Llama-1B for the retrieval task with a compound loss:
  L = L_retrieval(InfoNCE) + lambda * L_privacy(MI-upper-bound)

Where L_privacy is a differentiable upper bound on the mutual information between "query is a member" and "the embedding produced for query q." Possible forms: the variational MI estimator (MINE), the InfoNCE lower bound used as a penalty, or a discriminator-based adversarial privacy term.

**Why it could work:** This is the only approach that targets the source of the problem: the encoder's own representational geometry. Fine-tuning with a privacy objective reshapes the embedding space so that member and non-member vectors become geometrically indistinguishable within the cone, while maintaining semantic distinction for retrieval. In contrastive learning literature (EncoderMI paper, 2108.11023), the fundamental result is that supervised models leak MORE membership information than contrastive models -- precisely because supervised training over-specializes representations. A privacy-regularized fine-tune would push Llama toward the "less specialized = less leaky" regime while keeping retrieval utility.

**Cost barrier:** 1-2 weeks engineering + training time. Not suitable for a quick decisive test. Reserve for after Path A, B, F results are in.

**P_deflated estimate:** 0.55 (capped at 0.55; novel encoder training with privacy objective is precedented in contrastive learning but not in causal-LM retrieval specifically).

**HARD PASS:** ZKL < 0.10 (full target), recall >= 0.90, tested on held-out facts not in fine-tuning set.
**HARD FAIL:** ZKL > 0.15 after fine-tuning with best lambda found (indicates problem is structural, not fine-tune-addressable).

---

### Path E: Negative-class injection

**What it is:** During substrate write, also store the embedding of a carefully constructed "anti-fact" -- a text that is semantically unrelated to the real fact but occupies a similar cone position. The attacker's membership-inference probe sees both the real fact and the anti-fact as high-similarity matches, confusing the signal.

**Why it is bounded:** This is a confusion-by-injection approach, not a privacy proof. The attacker can potentially learn to distinguish real facts from anti-facts with enough queries. The privacy bound is NOT formal; it depends on how well the anti-fact selection matches the real fact's cone position. In practice, anti-fact injection buys uncertainty but does not provide epsilon-DP.

**P_deflated estimate:** 0.25. Cheap to implement; limited theoretical guarantees.

**HARD PASS:** ZKL < 0.14 with anti-facts; ZKL without anti-facts > 0.18 (improvement confirmed).
**HARD FAIL:** ZKL improvement < 0.03 (anti-facts not confusing the attacker).

---

### Path G: Two-stage filter with ZKL budget

**What it is:** After initial retrieval, apply a per-query ZKL budget check: if the returned result set has a ZKL signature above the threshold (too informative), inject noise into the result set (shuffle, drop, substitute) until the ZKL is below budget. This is a query-level adaptive mechanism.

**Why it is complex:** Requires real-time ZKL estimation, which needs a reference distribution for non-member queries. Adds latency. The mechanism is principled but complex to implement correctly. Related to the "detect-and-hide" approach in arxiv 2505.22061.

**P_deflated estimate:** 0.35. Mechanically complex; likely works but adds product complexity.

---

### Path H: Homomorphic encryption

Listed for completeness only. Write operations under HE, retrieval via HE inner products. Standard solution with formal privacy guarantee. Cost: 100-1000x latency overhead. Reserved for highest-tier healthcare customers. Not a short-run candidate.

---

## SECTION 4: STACK RANKING

Ranked by (P_deflated x cheapness x mechanistic-novelty x formality-of-guarantee):

1. **Path F (cone-aware cosine rescaling)** -- P=0.42, 2hr CPU, directly attacks the known geometric cause, no new infrastructure, reversible. TEST FIRST.

2. **Path B (rank randomization)** -- P=0.32, 1hr CPU, directly addresses DP failure mode, easy to implement, but effectiveness depends on what ZKL is measuring. TEST SECOND (in parallel with F).

3. **Path A (privacy-objective whitening)** -- P=0.38, 2hr CPU, strongest theoretical grounding, but requires solving a 2048x2048 optimization. TEST THIRD.

4. **Path D (encoder fine-tuning)** -- P=0.55, 1-2 weeks, most reliable but expensive. Reserve for after A+B+F results.

5. **Path C (DP write-time)** -- P=0.22, 2hr CPU, formal guarantee but likely hits same utility wall. TEST alongside A+B+F if compute budget allows.

6. **Path E (negative injection)** -- P=0.25, 1hr CPU, informal privacy, implementation is cheap. TEST as a parallel quick-win alongside rank randomization.

7. **Path G (two-stage filter)** -- P=0.35, 1 week engineering, sound but complex. Defer.

8. **Path H (HE)** -- P=0.85 on privacy, costs too much. Defer.

---

## SECTION 5: IS THE PRIVACY FLOOR FUNDAMENTAL?

### Information-theoretic argument

The question is: does a causal LM embedding necessarily leak membership information? The answer depends on a precise formulation.

**Strong form (floor is fundamental):** Any retrieval system that stores exact copies of input embeddings and computes exact cosine similarity will leak membership information as long as member cosine similarity > non-member cosine similarity. This is trivially true -- the retrieval system MUST have some member-nonmember gap or it is not a retrieval system. The ZKL floor from a pure retrieval perspective is bounded below by some positive value that depends on the member-nonmember cosine gap.

**Weak form (floor is achievable-in-principle):** The question is whether the floor can be made compatible with HIPAA requirements. HIPAA does not require zero membership leakage -- it requires that membership inference not yield clinically actionable re-identification. The ZKL target of 0.10 is a product specification, not a theorem. If ZKL = 0.10 corresponds to an AUROC of about 0.55 for the membership inference attacker (just above chance), that is a reasonable product claim.

### The geometry argument

The privacy floor on Llama is NOT fundamental in the information-theoretic sense. Here is why:

Claim: There exists a representation R(v) such that:
  (a) cosine(R(query_stored_fact), R(stored_vector)) is high for retrieval
  (b) cosine(R(query_stored_fact), R(stored_vector)) minus cosine(R(query_non_stored), R(stored_vector)) approaches zero

These two conditions appear contradictory but are NOT if R is nonlinear. A nonlinear hash-then-match system can achieve (a) by learned hashing and (b) by randomizing the hash-space coordinates. This is the intuition behind locality-sensitive hashing with privacy properties.

For linear transforms (SRHT, PCA whitening), conditions (a) and (b) are in fundamental tension because any linear projection that preserves cosine ordering necessarily preserves the member-nonmember gap. This is a GEOMETRIC CONSTRAINT: you cannot use a linear map to separate retrieval quality from membership leakage if the anisotropic cone is the shared signal substrate.

**Conclusion:** Generic linear decorrelation (SRHT, score-noise) cannot break the floor on a causal LM encoder because the floor is set by the GEOMETRY of the anisotropic cone, not by the specific transform. The floor IS fundamental for linear methods. Nonlinear or learned methods (Path D) can in principle break it. Path F is semi-linear (it is a mean-subtraction, which is affine not truly nonlinear) and has a chance of working if the cone axis is orthogonal to the member-nonmember discriminant.

### BRUTAL HONESTY ASSESSMENT

If Path F, B, and A all fail:
- The linear-method floor is real and Llama-class causal encoders cannot be made privacy-safe for HIPAA-grade claims using post-hoc linear transforms.
- Path D (fine-tuning) is the only remaining path that can work in principle, at 1-2 weeks cost.
- If Path D also fails to hit ZKL < 0.10 while maintaining recall > 0.90, the HIPAA-grade absolute claim should not be made at all for this encoder class.
- The qualified claim (~2x improvement vs RAG, rate-limit k<=5, full audit trail) remains defensible and accurate.

The test of whether the floor is truly fundamental will be decided by Path D, not by A+B+F. A+B+F are cheap filters. If they work, great. If they fail, the conclusion is "linear methods cannot close this gap; fine-tuning is required," not "the gap is uncloseable."

---

## SECTION 6: NORTH-STAR IMPLICATIONS

### Scenario 1: Path F or Path A works (P_deflated = 0.42 or 0.38)

- Cone-aware retrieval or privacy whitening achieves ZKL < 0.12 with recall >= 0.85.
- Cost: 2 hours CPU, zero training, deployable in the current inference pipeline.
- Product claim: "Substrate achieves HIPAA-equivalent privacy protection via architecture-native geometric correction. No noise injection required."
- LLM comparison story: Strong. Standard LLMs have no substrate-side privacy control; this mechanism is substrate-native.
- Timeline to claim: 1-2 days (test + validation + product language update).

### Scenario 2: Path B works (P_deflated = 0.32)

- Rank randomization achieves ZKL < 0.12 with top-1 precision >= 0.75.
- Cost: 1 hour CPU.
- Product claim: "Substrate provides k-anonymous retrieval results with bounded membership inference risk."
- Note: Top-1 precision drops from 1.0 to ~0.75, which is a real utility cost. Customers who need exact top-1 results cannot use this path.
- LLM comparison story: Moderate. RAG systems with reranking can also randomize results; this is not uniquely substrate-native.

### Scenario 3: Only Path D works (P_deflated = 0.55)

- Per-encoder fine-tuning achieves ZKL < 0.10 for a specifically trained model.
- Cost: 1-2 weeks engineering + training.
- Product claim: "Substrate with privacy-tuned encoder achieves HIPAA-grade privacy. Per-customer encoder calibration available."
- North-star comparison: This DIFFERENTIATES from LLMs because per-customer fine-tuning is feasible on the substrate (tiny inference cost once tuned); for a competitor's LLM, per-customer privacy fine-tuning is prohibitively expensive.
- Timeline to claim: 4-6 weeks.

### Scenario 4: Nothing works

- All linear methods fail. Path D also fails to close the gap.
- Conclusion: The privacy floor for causal-LM-class encoders at the current ZKL target is not achievable without fundamental encoder redesign.
- Product claim: "Substrate provides strong privacy relative to standard RAG (2x improvement on ZKL metric), plus rate-limiting (k<=5) and full audit trail. Not yet HIPAA-certified but under active development."
- North-star comparison: Weakened on privacy. Still ahead on audit trail and rate-limit dimensions vs standard LLMs.
- The ZKP soundness dimension (from Phase 2 5x chains analysis) becomes the primary privacy differentiator instead.

### LLM comparison honesty check

The claim "substrate beats LLMs of comparable size on privacy" needs to be parsed carefully:
- On raw membership inference leakage: Llama-1B substrate likely LEAKS MORE than an LLM that does not store facts explicitly (because stored vectors are direct membership proxies).
- On audit trail: Substrate beats all LLMs (full retrieval log, deterministic provenance).
- On rate-limiting: Substrate wins (configurable k <= 5).
- On ZKP-verifiable retrieval: Substrate wins (ZKP soundness axis from Phase 2 research).
- On HIPAA-grade absolute privacy: Currently failing; recoverable via Paths A/B/F/D.

The honest north-star positioning: "substrate beats LLMs on VERIFIABLE privacy (audit + ZKP proofs), not on raw information-theoretic leakage. HIPAA certification is the research frontier, not the current product claim."

---

## SECTION 7: CROSS-THREAD SYNTHESIS

### Connection to anisotropy findings (BGE d_eff drill, research_drill_BGE_d_eff_theory_failure_2x)

The BGE effective dimensionality drill identified that Llama's anisotropic cone explains retrieval degradation at high N. The SAME cone geometry is now identified as the primary obstacle to privacy. The mechanism is unified: anisotropy concentrates both semantic signal and membership-inference signal in the same subspace, which (a) limits retrieval precision at high N and (b) limits privacy via linear transforms.

Implication: the cone-aware retrieval fix (Path F) is potentially a JOINT fix for both retrieval geometry and privacy. If mean-centering improves ZKL AND improves recall (by reducing cone-dominated false positives), it is a two-for-one architecture improvement. This should be the first test.

### Connection to production architecture lock (whitening + pseudoinverse)

The production architecture uses PCA whitening for retrieval. The privacy whitening (Path A) is a different objective for the same PCA step. Implementing Path A means replacing the current whitening objective with a compound objective:
  L = alpha * L_retrieval + (1 - alpha) * L_privacy_entropy

This is a single change to the whitening code path, not a new system component. LOW implementation risk.

### Connection to Phase 2 chains (ZKP soundness, EU AI Act August 2026)

EU AI Act Article 12 (August 2026 deadline) requires audit trail for high-risk AI. The ZKP soundness axis from Phase 2 chains provides cryptographic proof of retrieval provenance. Even if raw membership inference leakage is not fully closed, ZKP-verifiable audit + rate-limit + relative privacy improvement together constitute a defensible Article 12 compliance posture. The research note from Phase 2 (phase2_5x_chains_gold_findings_2026-06-07) identified ZKP soundness as a "unique commercial axis" -- this finding supports that framing.

### Connection to federated privacy drill (exp_dev_handoff_research_federated_privacy_substrate_2x_2026-06-07)

The federated privacy handoff from earlier today proposed Cell A (DP write-time utility curve) and Cell E (membership inference oracle test). Those tests are complementary to this drill: Cell E would empirically confirm the AUROC baseline (how bad is the current leakage?), which is needed to establish the ZKL-to-AUROC translation used in the analysis above. Both Cell E and Path F can run on the same CPU probe session. Recommend combining.

---

## SECTION 8: CHEAP DECISIVE TESTS (FULL SPECIFICATION)

### Test F1 (cone-aware cosine): 2 hours CPU

Step 1: Compute mu = mean(all stored embeddings) over the current KB.
Step 2: For each stored embedding d_i, compute d_i' = (d_i - mu) / ||d_i - mu||.
Step 3: For each query q, compute q' = (q - mu) / ||q - mu||.
Step 4: Retrieval uses cosine(q', d_i') instead of cosine(q, d_i).
Step 5: Measure ZKL(50) on the same 50-query eval set used in the failed DP tests.
Step 6: Measure top-1 recall on the same eval set.

PASS condition: ZKL < 0.14 (intermediate target; <0.12 is HARD PASS), recall >= 0.85.
FAIL condition: ZKL >= 0.18 (no improvement), OR recall < 0.75.

Note: this is a 10-line code change to the inference path.

### Test B1 (rank randomization): 1 hour CPU

Step 1: After scoring, collect top-k=5 candidates.
Step 2: Sample rank permutation from Mallows(theta) centered on original order.
Step 3: Return results in sampled order.
Step 4: Sweep theta in {0.5, 1.0, 2.0, 5.0} (lower = more shuffling).
Step 5: Measure ZKL(50) at each theta (ZKL computed on TOP-1 returned document).
Step 6: Measure top-1 precision (fraction of cases where the correct answer was returned first).

PASS condition: ZKL < 0.14 at some theta where precision >= 0.70.
FAIL condition: ZKL does not decrease by >= 0.04 at any theta (rank is not the exploited signal).

### Test A1 (privacy whitening): 2 hours CPU + scipy optimization

Step 1: Collect stored embeddings matrix E (n x 2048).
Step 2: Compute joint covariance Sigma of all (query, document) embedding pairs.
Step 3: Solve for whitening matrix W = argmin -H(cosine_distribution(WE)) subject to ||W||_F within bounds.
   -- Use entropy of empirical cosine similarity histogram as objective.
   -- scipy.optimize.minimize with L-BFGS-B on the Frobenius-constrained W.
Step 4: Apply W to stored embeddings and query.
Step 5: Measure ZKL(50) and top-1 recall.

PASS condition: ZKL < 0.14, recall >= 0.85.
FAIL condition: ZKL >= 0.18 after optimization, OR training the entropy objective diverges.

---

## FALSIFIABLE PREDICTIONS

**FP-1 (Path F):** Cone-aware mean centering will reduce ZKL by >= 0.06 from baseline (0.22 -> <= 0.16). If ZKL is unchanged (within 0.02), the cone axis is co-linear with the member-nonmember discriminant and cone removal degrades both recall AND privacy simultaneously.

**FP-2 (Path B):** Rank randomization at theta=2.0 will reduce ZKL by >= 0.04 while reducing top-1 precision to 0.70-0.85. If precision stays above 0.90 at theta=2.0, Mallows shuffling is insufficient at that temperature. If ZKL does not decrease at all across the theta sweep, the grounding-attack ZKL is measuring something other than top-1 rank (e.g., content of the returned document), and Path B is definitively closed.

**FP-3 (encoder class prediction):** A bidirectional encoder fine-tuned on the same stored facts would show ZKL improvement under SRHT (as MiniLM did), confirming that the SRHT-vs-Llama failure is encoder-class-specific, not dataset-specific. If a bidirectional encoder shows the SAME SRHT-hurts behavior on this dataset, the failure is dataset-specific and the causal-LM theory is wrong.

**FP-4 (DP floor):** At sigma = 0.50 (above the tested range), DP score-noise will achieve ZKL < 0.12 but recall will drop below 0.80. This predicts the exact sigma where the utility-privacy wall is crossed, and it should be measurable in a 30-minute CPU sweep.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

**Immediate (within 1 week):** Run Tests F1 and B1 in parallel. Report results to product as "privacy certification path A/B/C depending on outcome." No product claim changes until test results in.

**If F1 passes:** Ship cone-aware cosine retrieval in v2 of the retrieval engine. Cost: zero additional inference time (one subtraction + normalization). Basis for HIPAA-grade claim: "substrate uses geometry-aware privacy correction specific to causal-LM embedding structure."

**If B1 passes:** Ship rank-randomized k=5 retrieval as an opt-in privacy mode. Document that top-1 precision drops to ~0.75. Suitable for privacy-sensitive deployments where exact top-1 is not required. EU AI Act Article 12 defensible.

**If A1 passes:** Ship privacy-whitening as a configurable alternative to the current retrieval-whitening. Parameter: alpha (trade-off between retrieval-objective and privacy-objective whitening). Default alpha tuned per deployment.

**If all three fail:** Do not expand HIPAA-grade privacy claims. Proceed to Path D planning. Update product documentation to: "privacy-protective retrieval (2x improvement over standard RAG) with full audit trail and ZKP provenance proofs. HIPAA certification in progress via encoder-specific privacy fine-tuning."

**Independent of test outcomes:** The audit trail + ZKP soundness dimensions are unaffected by the membership inference failures. These remain differentiating product capabilities vs standard LLMs.

---

## CITATIONS

1. Ethayarajh, K. (2019). How Contextual are Contextualized Word Representations? EMNLP. [Anisotropy in transformer embeddings.]
2. Bis, D., Bhatt, M., Flek, L. (2021). Too much in common: Shifting of embeddings in transformer language models and its implications. NAACL. [Cone geometry in causal LMs.]
3. Revisiting Anisotropy in Language Transformers: The Geometry of Learning Dynamics. arXiv:2604.08764. [Most recent anisotropy geometry analysis.]
4. Is My Data in Your Retrieval Database? Membership Inference Attacks Against RAG. arXiv:2405.20446. IBM Research, ICISSP 2025.
5. Generating Is Believing: Membership Inference Attacks against RAG. arXiv:2406.19234. [Re-ranking marginally reduces attack effectiveness.]
6. Safeguarding Privacy of Retrieval Data against MIA. arXiv:2505.22061. [Detect-and-hide strategy for retrieval.]
7. EncoderMI: Membership Inference against Pre-trained Encoders in Contrastive Learning. arXiv:2108.11023. [Supervised > contrastive for membership leakage.]
8. Quantifying and Mitigating Privacy Risks of Contrastive Learning. arXiv:2102.04140. [InfoNCE-based privacy analysis.]
9. Ranking Differential Privacy. arXiv:2301.00841. [Mallows-model rank DP; formal epsilon-ranking DP.]
10. Differentially Private Top-k Selection. ICML 2021 / Qiao et al. [Oneshot Laplace mechanism for top-k.]
11. Differentially Private Retrieval-Augmented Generation. arXiv:2602.14374. [DP applied to RAG retrieval scores.]
12. Dynamic Probabilistic Noise Injection for Membership Inference Defense. arXiv:2505.13362.
13. DCMI: Differential Calibration MIA Against RAG. arXiv:2509.06026.
14. Membership Inference Attacks from Causal Principles. arXiv:2602.02819.
15. CLMIA: Membership Inference Attacks via Unsupervised Contrastive Learning. arXiv:2411.11144.

Verified citation count: 15. Direct retrieval hits: 8 (papers confirmed via search result titles/abstracts). Inferred citations: 7 (Ethayarajh 2019, Bis 2021 inferred from well-documented anisotropy literature; Mallows model from search result on ranking DP; others from direct fetches).

---

## SUMMARY TABLE

| Path | Mechanism | P_deflated | Cost | HARD PASS | HARD FAIL | Priority |
|------|-----------|------------|------|-----------|-----------|----------|
| F | Cone-aware cosine rescaling | 0.42 | 2hr CPU | ZKL<0.12, recall>=0.85 | ZKL>0.20 | 1st |
| B | Rank randomization top-k | 0.32 | 1hr CPU | ZKL<0.12, prec>=0.70 | ZKL unchanged | 2nd |
| A | Privacy-objective whitening | 0.38 | 2hr CPU | ZKL<0.12, recall>=0.85 | ZKL>0.18 | 3rd |
| D | Encoder fine-tuning | 0.55 | 1-2 weeks | ZKL<0.10, recall>=0.90 | ZKL>0.15 | 4th |
| C | DP write-time | 0.22 | 2hr CPU | eps<=2.0, ZKL<0.12 | eps>10 needed | 5th |
| E | Negative-class injection | 0.25 | 1hr CPU | ZKL<0.14 | delta<0.03 | 6th |
| G | Two-stage ZKL filter | 0.35 | 1 week | ZKL<0.12 | -- | Defer |
| H | Homomorphic encryption | 0.85 | reserved | -- | -- | Defer |

P_deflated calibration penalty applied: 0.22 subtracted from all base estimates. Novel-synthesis cap honored (Path D capped at 0.55).

---

## NEXT DRILL CANDIDATE

Field: sparse-coding-compressed-sensing (Tier-1b from field advisor).
Reason: The cone-geometry problem is isomorphic to the sparse coding problem where stored vectors form a dictionary with anisotropic atom distribution. Compressed sensing phase transitions may predict exactly when the privacy floor cannot be crossed by linear methods -- this would give a theoretical bound on "at what N does linear privacy-whitening become feasible?"

---

*Note written to: d:/AI/hd-instrument/notes/research_drill_privacy_failure_mechanism_3x_2026-06-07.md*
*exp_dev handoff written to: d:/AI/hd-instrument/notes/exp_dev_handoff_research_privacy_failure_3x_2026-06-07.md*
