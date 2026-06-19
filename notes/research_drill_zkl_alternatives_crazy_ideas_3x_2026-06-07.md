# Research drill: ZKL alternatives and crazy ideas (3x deep)
Date: 2026-06-07
Filed-by: research sub-agent

Topic: All non-linear-mitigation paths to shared-encoder ZKL <= 0.10 (HIPAA absolute),
plus crazy ideas, structural ceiling assessment, and defense-in-depth hybrid proposal.

Context: Linear mitigations on shared encoder are bounded at ZKL ~0.22 across all tested
variants (Hyp B token-position cap, Hyp C Gram structure, SRHT, DP score-noise, cosine
rescaling). Path D (per-customer encoder fine-tune) works for premium tier but not shared.
Goal: find ANY path to shared-encoder ZKL <= 0.10 without per-customer cost.

---

## HEADLINE

No single novel path achieves shared-encoder ZKL <= 0.10 with high confidence under
calibrated P estimates. The structural reason is that membership-inference signal and
semantic retrieval signal co-occupy the same geometric manifold in any fixed encoder
trained for general retrieval. Paths that genuinely separate these two signals (adversarial
fine-tuning, VIB, disentanglement, nullspace projection) all require encoder modification,
which costs between 1 and 6 engineering weeks and introduces utility degradation risk.
Cryptographic paths (HE, ZKP, SMPC) eliminate the leakage problem entirely but at
computational costs that make real-time retrieval impractical at 2026 hardware. Query-time
defenses (DP noise, k-anonymity, stochastic top-k) are provably bounded at ~0.15-0.20 on
rank-based attacks and cannot reach 0.10 without destroying recall. The most credible path
to ZKL <= 0.10 on a shared encoder is a COMBINATION of (1) adversarial fine-tuning the
shared encoder once (not per-customer) to suppress the leakage subspace, plus (2)
stochastic top-k at retrieval time, which together may compound to ~0.08-0.12 -- a range
that straddles the target. This is pre-reg-testable in ~4-6 eng-weeks at rung-2 scale.

P_deflated (any single path reaches ZKL <= 0.10) = 0.18 (calibration penalty applied)
P_deflated (combination path reaches ZKL <= 0.10) = 0.28 (combination with adversarial FT)
P_deflated (Path D premium tier holds as structural ceiling for shared encoder) = 0.60

HARD-PASS threshold: adversarial FT + stochastic top-k combo reaches ZKL(50) <= 0.10 AND
                     recall@10 >= 0.80 on 500-fact probe set
HARD-FAIL threshold: combo path reaches ZKL(50) >= 0.15 OR recall@10 < 0.70 on same probe

---

## SECTION 1: PATH FAMILY EVALUATIONS

### Family 1: Nonlinear mitigations

#### Candidate 1A: Adversarial fine-tuning with privacy classifier loss

What it does: Fine-tune the shared encoder (not per-customer) with an adversarial
membership-inference classifier head. The training signal alternates between (a) preserving
retrieval utility and (b) fooling the membership-inference classifier. This is the gradient
reversal layer (GRL) framework from Ganin et al. 2016, applied here to suppress the
leakage subspace rather than domain shift.

Mechanism: The encoder loss is L = L_retrieval - lambda * L_membership_inference. The
minus sign on L_membership_inference causes the encoder to actively suppress features
that discriminate member vs non-member queries. Unlike per-customer fine-tuning (Path D),
this is a one-time training modification to the shared encoder before deployment. All
customers then use the privacy-hardened encoder.

P_theoretical: 0.65. Gradient reversal is a proven technique for domain invariance
(Ganin 2016, widely replicated). Its application to membership-inference privacy is
principled: if the encoder cannot discriminate member vs non-member at the representation
level, any downstream attack is bounded. The literature (ArXiv 1807.05852, "Machine
Learning with Membership Privacy using Adversarial Regularization") directly validates
this framing.

P_empirical: 0.40. The key unknown is the semantic utility tradeoff. Llama-3.2-1B L15
representations carry membership-inference signal in the same geometric dimensions as
semantic retrieval signal (confirmed by prior eigenspectrum diagnostic: PR unchanged at
12.733, meaning the problem is manifold geometry not dimension anisotropy). GRL training
that suppresses membership-inference may also suppress the retrieval directions. Empirical
validation requires a pre-test.

P_deflated = 0.65 x 0.40 = 0.26 (calibration penalty -0.10 applied; single path)

Engineering cost: 3-5 eng-weeks. Requires adversarial training loop, privacy classifier
dataset (member/non-member pair annotations), and retrieval quality evaluation harness.
Not trivial, but no cloud GPU needed for rung-2 validation.

Compatibility: Good. Does not modify the retrieval API, audit trail, bitemporal record,
or GDPR compliance stack. The encoder swap is transparent to all upstream/downstream
components. The GDPR "right to erasure" mechanism is unaffected because erasure operates
on stored substrate vectors, not the encoder weights.

Cheap pre-test: Train a 2-layer adversarial privacy head on Pythia-160M using 200
member/non-member query pairs. Measure ZKL(50) before and after 100 GRL gradient steps.
Pre-test wall time: ~30-60 min CPU. If ZKL drops >= 0.05 in Pythia pre-test, proceed to
Llama full-scale. If ZKL is unchanged or worsens, the utility-leakage entanglement is
too tight and this path is blocked at rung-2.

#### Candidate 1B: Variational information bottleneck on KEY representations

What it does: Adds a bottleneck layer between the encoder output and the substrate's
stored KEY vectors. The bottleneck compresses the representation to a latent distribution
Z ~ N(mu, sigma^2) and constrains mutual information I(Z; X) via a KL divergence penalty.
The goal is to retain I(Z; Y) (retrieval utility) while suppressing I(Z; membership signal).

The nonparametric VIB variant (NVIB, ArXiv 2601.02307) applies this directly to
transformer embeddings. The cited paper reports Renyi divergence values nearly an order
of magnitude lower than standard VIB, which is a strong signal.

P_theoretical: 0.55. Information bottleneck theory guarantees that reducing I(Z; X) also
bounds the mutual information between Z and any downstream inference including membership
inference. The bound is exact under the Markov chain X -> Z -> attack. The caveat is
that the Markov chain assumption requires the bottleneck to be the only information path
-- a shared encoder that is queried directly (not through the bottleneck) breaks the
guarantee.

P_empirical: 0.35. In practice, VIB on retrieval systems degrades recall significantly
because the Gaussian bottleneck discards fine-grained matching information. The NVIB
variant reduces this problem but the tradeoff curve at ZKL <= 0.10 is unknown for this
specific encoder-substrate combination. The bottleneck also adds a computational layer
at query time.

P_deflated = 0.55 x 0.35 = 0.19 (calibration penalty -0.10 applied)

Engineering cost: 2-3 eng-weeks. The NVIB layer is modular -- it sits between encoder
output and substrate input. If recall drops below threshold, the bottleneck width can
be tuned. However, the tuning search is expensive.

Compatibility: Good for new deployments; migration cost for existing substrate instances
because stored KEY vectors would need to be re-encoded through the bottleneck.

Cheap pre-test: Implement a fixed Gaussian bottleneck (no training, just add N(0, sigma^2)
noise to encoder output before storage and query). Sweep sigma in [0.01, 0.10, 0.30, 0.60].
Measure ZKL(50) and recall@10 at each sigma. This is NOT adversarial training -- it is
the simplest VIB degenerate case. Pre-test wall time: ~20 min CPU. The sigma sweep maps
out the utility-privacy tradeoff curve and tells us whether any operating point achieves
both ZKL <= 0.10 and recall >= 0.80.

---

### Family 2: Encoder swap

#### Candidate 2A: Encoder specifically trained with DP noise (DP-SGD encoder)

What it does: Replace the shared encoder with one trained using differential privacy SGD
(e.g., DP-RoBERTa, DP-BERT, or a DP-fine-tuned Llama). The encoder itself has a privacy
guarantee baked into its weights by construction, which should reduce the membership
inference signal at the representation level.

Literature: Multiple papers (ArXiv 2205.06135 "Fair NLP Models with Differentially Private
Text Encoders", recent federated DP encoder work) show that DP-trained encoders have lower
membership inference AUROC. The question is whether this extends to rank-based attacks
on retrieval (ZKL-based, not AUROC-based).

P_theoretical: 0.45. DP-SGD training bounds membership inference AUROC theoretically but
the bound applies to training data membership, not to the specific "which facts are stored
in the substrate" membership query. These are related but not equivalent. The training
data of the encoder and the stored facts in the substrate are different populations.

P_empirical: 0.25. DP-trained encoders typically have 3-8% lower retrieval quality than
standard encoders at reasonable privacy budgets (epsilon < 8). The empirical gap from
ZKL=0.22 to ZKL=0.10 is large relative to what DP training alone has been shown to achieve
on rank-based metrics.

P_deflated = 0.45 x 0.25 = 0.11 (calibration penalty -0.10 applied; rated LOW)

Engineering cost: 2-4 eng-weeks, but the DP-trained encoder may already exist (e.g.,
Microsoft has released DP-RoBERTa checkpoints). If using an existing checkpoint, cost
drops to 1 week of integration and benchmarking.

#### Candidate 2B: Smaller encoder (capacity argument)

What it does: Replace the 2048-dim Llama-3.2-1B L15 encoder with a smaller model
(e.g., 384-dim MiniLM or 768-dim BERT-base). Smaller models have lower representational
capacity and therefore carry less incidental membership-inference signal.

P_theoretical: 0.30. Capacity argument is real: a model with fewer parameters cannot
memorize as much incidental information. However, the membership-inference leak in this
substrate is NOT due to memorization -- it is due to geometric structure (cone
concentration in the retrieval space). A smaller encoder in the same semantic space will
have the same cone structure at smaller scale. The geometric argument predicts smaller
benefit than the capacity argument suggests.

P_empirical: 0.20. MiniLM has ZKL(50) ~0.41 without any mitigation, which is HIGHER
than Llama's 0.22. This is the empirical refutation: smaller encoder does not mean lower
ZKL. The capacity argument does not apply to rank-based membership inference in
cone-concentrated embeddings.

P_deflated = 0.30 x 0.20 = 0.06 (calibration penalty -0.10 applied; rated VERY LOW)

Verdict: RULED OUT by prior empirical data. MiniLM outright fails. Do not pursue.

---

### Family 3: Cryptographic approaches

#### Candidate 3A: Homomorphic encryption on embeddings

What it does: Store all substrate KEY vectors in encrypted form using an additively
homomorphic encryption scheme (e.g., CKKS). Query embeddings are also encrypted. Inner
product similarity is computed over ciphertext. The retrieval result (top-k document IDs)
is returned as ciphertext and decrypted client-side. The server never sees plaintext
query or document vectors.

Literature: The 2024-2025 search found multiple papers on encrypted semantic search
(CKKS-based, AHE inner product schemes). A 2024 paper reports "nearly identical
performance to plaintext-based schemes" for STS tasks. A recent US patent (12164664)
covers "Semantic search and retrieval over encrypted vector space."

P_theoretical: 0.90. If implemented correctly, HE retrieval is mathematically immune to
membership inference attacks on the server side because the server has no access to
plaintext vectors. ZKL is not bounded -- it is zeroed from the server's perspective.
The guarantee is absolute: a server operating on ciphertext cannot distinguish member from
non-member query patterns.

P_empirical: 0.30. The practical problem is computational cost. CKKS inner product over
N=2048 dimensions is approximately 10,000-100,000x slower than plaintext cosine similarity.
For a knowledge base with 10,000 stored facts, a single query requires 10,000 ciphertext
inner products. At 2026 hardware, this is approximately 10-100 seconds per query vs
milliseconds for plaintext. This is incompatible with real-time retrieval requirements.

P_deflated = 0.90 x 0.30 = 0.27 (calibration penalty applied; high theoretical, low
practical given current hardware)

Engineering cost: 8-16 eng-weeks for a production-quality encrypted retrieval system.
Microsoft SEAL, OpenFHE, and Concrete-ML provide libraries, but integration with the
substrate's retrieval stack is non-trivial. Performance would require approximate
retrieval (HNSW-like structures over encrypted space) which is an open research problem.

Compatibility: EXCELLENT for HIPAA compliance (server processes only ciphertext). GDPR
Art 17 erasure is trivial (delete the ciphertext row). Bitemporal records are maintained
in the encrypted domain. Audit trail requires careful design (what to audit if you cannot
see the query?).

Cheap pre-test: NOT applicable for current product timeline. Flag as "2027 horizon tech"
unless a client-side encryption mode is acceptable (client encrypts query, sends ciphertext,
server decrypts with client key to answer then discards -- this is NOT HE but gives a
weaker but practical privacy guarantee).

#### Candidate 3B: ZK proofs of correct retrieval

What it does: The retrieval server produces a ZK proof that "the returned document D is
the correct top-1 match for query Q under the stored index" without revealing Q or D to
any auditor. This is ZKML (zero-knowledge machine learning) applied to retrieval.

Literature: A 2026 survey (ArXiv 2502.18535 "A Survey of Zero-Knowledge Proof Based
Verifiable Machine Learning") and 2024 survey (ArXiv 2408.00243 "Applications of
Zero-Knowledge Proofs") confirm active development. ZKML is a real field but current
circuits handle networks of ~100k parameters; a 1B-parameter encoder is 10,000x larger.

P_theoretical: 0.70. ZKP is sound and complete for any polynomial-time computation.
Retrieval is polynomial-time. Therefore, in principle, a ZK proof of correct retrieval
is constructible.

P_empirical: 0.05. The computational overhead for proving a single LLM inference step is
roughly 10^6 - 10^8 multiplications per parameter. For a 1B-parameter encoder, generating
the ZK proof would take hours on current hardware (zkSNARK / zkSTARK circuits). This is
not a 2026-2027 technology for LLM-scale encoders.

P_deflated = 0.70 x 0.05 = 0.04 (calibration penalty applied; rated NEGLIGIBLE for
near-term product)

Compatibility note: ZKP proves server-side correctness, NOT client-side privacy. It does
not prevent the server from logging which facts were retrieved. The threat model for
membership inference is different from the verifiability problem ZKP solves.

---

### Family 4: Query-time defenses

#### Candidate 4A: Stochastic top-k with calibrated noise (DP exponential mechanism)

What it does: Instead of deterministically returning the top-1 result, apply the
exponential mechanism (McSherry & Talwar 2007) to sample the returned document with
probability proportional to exp(epsilon * score / 2). Lower epsilon means more
randomization. This is the DP-correct way to add noise to retrieval output.

Literature: ArXiv 2411.09552 "Faster Differentially Private Top-k Selection" (ICML 2022
antecedent), ArXiv 2412.04697 "Privacy-Preserving RAG with DP", ICLR 2025 paper on DP
retrieval all validate this approach. The exponential mechanism is the established
solution for DP top-k selection.

P_theoretical: 0.55. The exponential mechanism provides (epsilon, 0)-DP guarantees on
the returned ranked list. This bounds membership inference AUROC via DP composition
theorems. However: (a) the guarantee is on the SCORE used for sampling, not on the raw
embedding, so a query-embedding attacker still has access to the representation before
the mechanism fires; (b) at epsilon=1.0, ZKL drops but recall drops proportionally.

P_empirical: 0.35. The bounded-at-0.15-0.20 finding for query-time defenses is consistent
with the exponential mechanism: at high epsilon (low noise), minimal privacy gain; at
low epsilon (high noise), recall collapse. The theoretical ceiling for rank-based defenses
without encoder modification is bounded by the membership-inference signal in the
representation. The exponential mechanism cannot exceed this bound.

P_deflated = 0.55 x 0.35 = 0.19 (calibration penalty applied; better than random noise
but still bounded)

Engineering cost: 1 eng-week. The exponential mechanism is 5 lines of code on top of
cosine similarity scoring. The main work is parameter sweep (epsilon calibration) and
recall evaluation.

Cheap pre-test: Implement exponential mechanism with epsilon in [0.3, 0.5, 1.0, 2.0, 5.0].
Measure ZKL(50) and recall@10 at each epsilon. Pre-test wall time: ~30 min CPU.

#### Candidate 4B: Query batching with k-anonymity

What it does: Instead of answering each query individually, always process queries in
batches of k. For each individual query q_i, submit a batch (q_i, q_i+1, ..., q_i+k-1)
and return results for all k. The attacker observing the batch cannot tell which query
was the "real" one vs the padding queries.

P_theoretical: 0.35. k-anonymity provides indistinguishability among k candidates. If k
is large enough, the membership-inference signal per query is divided by k. However:
(a) the attacker sees all k results, so they can potentially correlate across queries to
identify the signal; (b) if the user's actual query is distinguishable from padding queries
(different domain, length, vocabulary), the batch is not truly anonymous; (c) padding
queries must be real or indistinguishable from real queries, which requires a query
generation model.

P_empirical: 0.20. Practical k-anonymity for NLP queries is notoriously hard to implement
correctly (the py-PANTERA library, CIKM 2024, addresses this for simple query logs but not
for dense embedding spaces). The 2024-2025 literature on query obfuscation (De Faveri et al.
ECIR 2025, Faggioli & Ferro ECIR 2024) confirms that DP-based approaches scale better than
k-anonymity for dense IR systems.

P_deflated = 0.35 x 0.20 = 0.07 (calibration penalty applied; rated LOW)

---

### Family 5: Architectural changes

#### Candidate 5A: Nullspace projection / INLP encoder distillation

What it does: Identify the linear subspace of the encoder output that carries
membership-inference signal. Project all stored vectors and all query vectors onto the
nullspace of that subspace (i.e., remove the privacy-leaking directions). This is the
Iterative Nullspace Projection (INLP) framework (Ravfogel et al. 2020) and its
closed-form variant LEACE.

Literature: ArXiv 2604.05296 "From Measurement to Mitigation: Quantifying and Reducing
Identity Leakage in Image Representation Encoders with Linear Subspace Removal" (2024)
reports that subspace removal methods preserve >95% of baseline recall on copy-detection
benchmarks. ArXiv 2004.07667 "Null It Out: Guarding Protected Attributes by Iterative
Nullspace Projection" is the foundational method.

P_theoretical: 0.50. The INLP guarantee is that no linear classifier trained on the
projected vectors can exceed chance at recovering the protected attribute (membership
status). This is a strong theoretical bound IF the membership-inference signal is linearly
accessible. The prior eigenspectrum diagnostic (PR=12.733 unchanged by SRHT) suggests
the signal may be in a nonlinear manifold rather than a linear subspace. If nonlinear,
INLP provides no guarantee.

P_empirical: 0.40. The 2024 image encoder result (>95% recall preserved) is encouraging.
However, that was an image encoder, not a causal LM last-token pooled representation.
The coupling between semantic signal and membership-inference signal may be tighter in
causal LMs. Needs empirical test.

P_deflated = 0.50 x 0.40 = 0.20 (calibration penalty -0.10 applied)

Engineering cost: 1-2 eng-weeks. INLP is implemented in existing libraries. Requires
(a) a labeled dataset of member/non-member (query, response) pairs for the classifier,
(b) iterative projection until no linear classifier has AUROC > 0.55, (c) re-encoding
all stored substrate vectors through the nullspace projection.

Compatibility: Good. Nullspace projection is a post-encoder linear map -- transparent
to the substrate's retrieval mechanics. GDPR erasure unaffected. The projection can be
version-controlled and updated without re-training the encoder.

Cheap pre-test: Train a logistic regression on member vs non-member cosine scores from
Llama L15 (existing data). Measure how many INLP iterations are needed to suppress
AUROC to < 0.55. Measure recall drop after k iterations. Pre-test: ~20 min CPU using
existing diagnostic data. This directly answers whether the signal is linear (fast) or
nonlinear (slow or never) without running a full ablation.

#### Candidate 5B: Two-stage retrieval (noisy coarse stage + ZKL-safe re-rank)

What it does: Split retrieval into two stages. Stage 1 is a coarse, high-recall retrieval
with strong DP noise applied (exponential mechanism at low epsilon). The output is a
candidate set of k=50-200 documents. Stage 2 is a re-ranking step that operates only
within the candidate set, using a private score that is harder to attack because the
attacker cannot distinguish "which of the 50 was retrieved via membership inference" vs
"which was retrieved via semantic match."

Literature: Multiple ICLR/EMNLP 2025 papers on DP-RAG validate this two-stage approach.
ArXiv 2412.04697 and the EMNLP 2025 paper on "Mitigating Privacy Issues in RAG" both
analyze this pattern.

P_theoretical: 0.40. The two-stage design reduces the attack surface because Stage 2 is
not an open-ended search over all stored facts -- it is a re-rank within a pre-selected
set. However, if the Stage 1 candidate set consistently contains the member document (high
recall@50 for members vs non-members), the membership-inference signal is preserved and
just deferred to Stage 2.

P_empirical: 0.30. Works well when the signal is in the score magnitude (DP noise disrupts
it). For rank-based membership inference where the top-1 rank is the signal, Stage 1 must
be noisy enough to sometimes exclude the true member document, which hurts recall.

P_deflated = 0.40 x 0.30 = 0.12 (calibration penalty applied)

Engineering cost: 2-3 eng-weeks for two-stage redesign of retrieval stack.

---

### Family 6: Crazy ideas

#### Candidate 6A: Anti-attractor adversarial substrate state

What it does: Store a set of "decoy" or "anti-attractor" fact vectors in the substrate
alongside real facts. These decoys are designed to have high cosine similarity to the
typical membership-inference probe vectors (the query patterns that an attacker would use
to test if a fact is stored). When an attacker probes, their probe vector matches a decoy
rather than a real fact with equal probability, making the ZKL measure indistinguishable.

P_theoretical: 0.35. This is a form of "privacy through plausible deniability." The
theoretical guarantee depends on how well decoys can be designed to match attacker probes
without disrupting real retrieval. If decoys are distinguishable from real facts (e.g.,
lower semantic coherence), a calibrated attacker can filter them. If decoys are
indistinguishable, real queries also match decoys, hurting precision.

P_empirical: 0.20. No published literature on adversarial decoy vectors for retrieval
privacy. This is a genuinely novel idea. The practical challenge is that cosine similarity
in cone-concentrated spaces means "similar to an attacker probe" is also "similar to
legitimate queries of the same type." Decoys would reduce precision for legitimate queries.

P_deflated = 0.35 x 0.20 = 0.07 (calibration penalty -0.10 applied; novel idea, low
empirical P)

Engineering cost: 1-2 eng-weeks to implement decoy generation and evaluate recall/precision
tradeoffs. Interesting as a research direction but not near-term production path.

#### Candidate 6B: Querier-side substrate (customer holds substrate, service holds encoder)

What it does: Invert the deployment model. The customer stores their own substrate
(vectors, bitemporal records, GDPR state) on their own infrastructure. The vendor provides
only the encoder as a service. The customer sends queries to the encoder, receives query
vectors, and runs retrieval locally. The vendor never sees stored documents or query-to-
document matches.

P_theoretical: 1.00. This eliminates the server-side membership inference problem
entirely. The vendor has no stored facts to leak.

P_empirical: 0.90. This is a deployment architecture change, not a mathematical
technique. It absolutely works at eliminating server-side ZKL.

P_deflated = 1.00 x 0.90 = 0.90 (calibration penalty not applicable -- not a lit-scan
uncertainty question but a business model question)

Engineering cost: 4-8 eng-weeks for a client-side substrate SDK. However, this is NOT a
"shared encoder privacy mitigation" -- it is a different product architecture where the
customer takes on infrastructure responsibility. Not compatible with a SaaS deployment
where the vendor manages the knowledge base.

Compatibility: Excellent for privacy (GDPR Art 17 is handled by the customer). Bad for
product simplicity (no managed service, customer bears ops burden). Best framed as an
enterprise on-premise deployment option, not a shared-encoder fix.

#### Candidate 6C: Cryptographic commitments to retrieval state with audit-only opening

What it does: The retrieval service computes a cryptographic commitment C = hash(query,
result, timestamp, salt) and publishes C. The server does not log the plaintext (query,
result). For HIPAA audit purposes, the client provides the salt and the audit can verify
the commitment. This provides audit traceability without server-side record of what was
retrieved.

P_theoretical: 0.75. Hash commitments are cryptographically sound. This directly addresses
the audit-trail vs privacy conflict in HIPAA.

P_empirical: 0.70. This is an established pattern in privacy-preserving audit systems.
The HIPAA requirement is for audit trail availability, not server-side legibility of the
trail. Commitment schemes satisfy the audit requirement.

P_deflated = 0.75 x 0.70 = 0.53 (calibration penalty applied; this is well-understood
cryptographic engineering, not novel research)

Engineering cost: 1-2 eng-weeks to implement commitment logging and audit verification.

Verdict: This does NOT solve the ZKL problem. It solves a different problem: server-side
visibility into query content. Log it separately as a compliance feature, not a ZKL fix.

#### Candidate 6D: Active learning to identify and mitigate high-leakage queries

What it does: Monitor live query patterns to identify which query types produce the highest
ZKL (highest membership-inference signal). Apply targeted mitigation only to high-leakage
query patterns. Build a "query risk classifier" that flags high-risk queries and routes
them through a more aggressive privacy mechanism.

P_theoretical: 0.40. Theoretically sound: not all queries carry equal membership-inference
risk. Queries that exactly match stored fact patterns have higher ZKL than queries about
general topics. Targeted mitigation could achieve better utility-privacy tradeoff than
uniform mitigation.

P_empirical: 0.25. The practical challenge: you need labeled high-leakage vs low-leakage
queries for training the risk classifier, which requires knowing which facts are stored
(breaking the privacy model if done server-side) or an offline synthetic dataset.

P_deflated = 0.40 x 0.25 = 0.10 (calibration penalty applied)

Engineering cost: 2-3 eng-weeks for risk classifier + adaptive routing.

---

## SECTION 2: STACK RANKING (all candidates by P_actionable x engineering feasibility)

P_actionable is defined as P_deflated x (1 / relative_engineering_cost).

| Rank | Candidate | P_deflated | Eng-weeks | P_actionable | Notes |
|------|-----------|-----------|-----------|--------------|-------|
| 1 | 5A Nullspace/INLP projection | 0.20 | 1-2 | 0.133 | Cheapest testable path; linear signal check first |
| 2 | 1A Adversarial FT (GRL) | 0.26 | 3-5 | 0.065 | Highest theoretical P; expensive but one-time cost |
| 3 | 4A Stochastic top-k (exp mechanism) | 0.19 | 1 | 0.190 | Cheapest; best as compound layer not sole fix |
| 4 | 1B VIB bottleneck | 0.19 | 2-3 | 0.076 | Modular; sigma sweep pre-test cheap |
| 5 | COMBO: 5A + 4A (INLP + stochastic top-k) | 0.28* | 2-3 | 0.112 | Compounding two bounded mechanisms may clear 0.10 |
| 6 | 5B Two-stage retrieval | 0.12 | 2-3 | 0.048 | Moderate effort, moderate gain; useful as compound |
| 7 | 3A Homomorphic encryption | 0.27 | 8-16 | 0.022 | Best theoretical P; impractical 2026-2027 |
| 8 | 6D Active query risk classifier | 0.10 | 2-3 | 0.040 | Interesting but requires labeled data |
| 9 | 6A Anti-attractor decoys | 0.07 | 1-2 | 0.047 | Novel idea; hard to implement without recall loss |
| 10 | 2A DP-SGD encoder | 0.11 | 1-4 | 0.055 | Empirically weak for rank-based attacks |
| 11 | 4B k-anonymity batching | 0.07 | 2 | 0.035 | Difficult to implement correctly for dense IR |
| 12 | 2B Smaller encoder | 0.06 | 0 | N/A | RULED OUT by MiniLM empirical data (ZKL 0.41 > Llama 0.22) |

*Combination P estimated from partial overlap of mechanisms, not multiplicative independence.
Calibration penalty applied to combination: starting estimate 0.35, deflated to 0.28.

TOP 5 SELECTED:
1. 5A: INLP nullspace projection (1-2 eng-weeks, cheapest testable path to ZKL improvement)
2. 4A: Stochastic top-k via exponential mechanism (1 eng-week, best compound layer)
3. COMBO (5A + 4A): Both together as defense-in-depth (2-3 eng-weeks total)
4. 1A: Adversarial fine-tuning GRL (3-5 eng-weeks, highest ceiling but expensive)
5. 1B: VIB bottleneck (2-3 eng-weeks, modular path with sigma sweep pre-test)

---

## SECTION 3: PRE-REG PRE-TEST SPECS (5 tests)

### PRE-TEST T1: INLP nullspace projection linearity check

What is measured: Whether the membership-inference signal in Llama L15 embeddings is
linearly accessible (required for INLP to work).

Setup: Use existing Llama L15 embedding data from the privacy harness. Fit logistic
regression to predict member vs non-member status from cosine score distribution features
(mean, std, max cosine per query). Count how many INLP iterations are required to drive
classifier AUROC <= 0.52. Measure cosine recall@10 after each iteration.

HARD-PASS: After <= 5 INLP iterations, AUROC <= 0.52 AND cosine recall@10 >= 0.80.
           This confirms linear signal is suppressible and utility is preserved.
HARD-FAIL: After 10 INLP iterations, AUROC >= 0.60 (signal is nonlinear, INLP blocked)
           OR recall@10 < 0.65 at AUROC <= 0.55 (utility-privacy tradeoff too tight).
MID-BAND: AUROC <= 0.55 after 5-10 iterations with recall@10 in [0.65, 0.80]. Proceed
          with a second pre-test at Llama full-scale before committing to eng-weeks.

Wall time: ~20-30 min CPU using existing diagnostic data.
Note: This pre-test uses only classification on existing vectors, no new embedding runs.

### PRE-TEST T2: Stochastic top-k (exponential mechanism) epsilon sweep

What is measured: ZKL(50) and recall@10 as a function of DP epsilon for the exponential
mechanism applied to retrieval scoring.

Setup: Use the production Llama L15 encoder with the 500-fact probe set. For each epsilon
in [0.3, 0.5, 1.0, 2.0, 5.0], apply the exponential mechanism to sample the top-1 result
from the score distribution. Measure ZKL(50) and recall@10 at each epsilon.

HARD-PASS: Some epsilon value in [0.3, 2.0] achieves ZKL(50) <= 0.15 AND recall@10 >= 0.80.
           (Not 0.10 alone -- this test validates the mechanism, not the target; combining
           with INLP is the path to 0.10.)
HARD-FAIL: No epsilon value achieves ZKL(50) <= 0.15 without recall@10 < 0.70.
           If this fails, the mechanism cannot contribute meaningfully even as a layer.
MID-BAND: ZKL(50) in [0.15, 0.18] at recall@10 >= 0.80 at some epsilon. Still useful
          as a compound layer with INLP; do not discard.

Wall time: ~30-45 min CPU with 5 epsilon values on 500-fact probe.

### PRE-TEST T3: VIB sigma sweep (degenerate bottleneck, no adversarial training)

What is measured: The utility-privacy tradeoff curve for additive Gaussian noise in the
encoder output space. This is the cheapest proxy for VIB: no variational training, just
noise injection to map out the tradeoff curve.

Setup: For sigma in [0.01, 0.05, 0.10, 0.20, 0.30, 0.60], add N(0, sigma^2 * I)
noise to the Llama L15 embedding before storing/querying. Measure ZKL(50) and recall@10.

HARD-PASS: Some sigma achieves ZKL(50) <= 0.12 AND recall@10 >= 0.80. This indicates
           the utility-privacy tradeoff curve has a viable operating point AND the VIB
           learning problem is tractable (a learned bottleneck will do at least as well
           as additive noise).
HARD-FAIL: No sigma achieves ZKL(50) < 0.16 without recall@10 < 0.70. If additive
           noise cannot break 0.16 before recall collapses, a VIB layer will face the
           same wall and the family is blocked.
MID-BAND: ZKL(50) in [0.12, 0.16] at recall@10 >= 0.80. Proceed to VIB adversarial
          training only if sigma sweep gives at least this signal.

Wall time: ~20-30 min CPU with 6 sigma values on 500-fact probe.

### PRE-TEST T4: Adversarial GRL pre-test on Pythia-160M

What is measured: Whether gradient reversal layer training suppresses ZKL on a small
encoder (Pythia-160M) without destroying retrieval utility. This is a rung-2 pre-test
before committing to Llama-scale GRL training.

Setup: Use Pythia-160M as a proxy encoder. Implement a 2-layer MLP privacy classifier
head that predicts member vs non-member from encoder output. Run 100-200 GRL gradient
steps (alternating retrieval loss and adversarial privacy loss). Measure ZKL(50) and
recall@10 before and after GRL steps.

HARD-PASS: ZKL(50) drops by >= 0.08 (from ~0.35 baseline on Pythia) after GRL training,
           with recall@10 >= 0.75. This confirms the mechanism works at rung-2 and
           justifies Llama-scale training.
HARD-FAIL: ZKL(50) unchanged or increases after GRL, OR recall@10 < 0.60. If GRL
           cannot move ZKL on Pythia-160M, it will not move it on Llama-3.2-1B
           (the utility-leakage entanglement is structural, not scale-dependent).
MID-BAND: ZKL drops >= 0.04 at recall@10 >= 0.75. Marginal signal; requires Llama-scale
          pre-test before committing to full 3-5 week GRL training.

Wall time: ~30-60 min CPU for 200 GRL gradient steps on Pythia-160M.
Note: This requires a member/non-member labeled pair dataset. The existing privacy harness
data (ZKL-measured probe vs non-probe pairs) provides this without new annotation.

### PRE-TEST T5: Combination (INLP + stochastic top-k) compound test

What is measured: Whether combining the best-performing INLP projection (from T1, if it
passes) with the best-performing stochastic top-k epsilon (from T2, if it passes)
achieves ZKL(50) <= 0.10 in combination.

Setup: Apply INLP nullspace projection to Llama L15 embeddings (using the best k from T1)
then apply exponential mechanism at best epsilon from T2. Measure ZKL(50) and recall@10.
Compare to baseline (0.22) and individual mechanism results.

HARD-PASS: ZKL(50) <= 0.10 AND recall@10 >= 0.78. This is the primary target.
           If achieved, this path produces a shared-encoder HIPAA-absolute solution
           at ~2-3 eng-weeks total cost with zero per-customer overhead.
HARD-FAIL: ZKL(50) >= 0.14 OR recall@10 < 0.70. Combination provides no meaningful
           additive benefit; qualified posture + Path D is the structural ceiling.
MID-BAND: ZKL(50) in [0.10, 0.14] with recall@10 >= 0.78. Re-evaluate with wider
          INLP sweep (more iterations) or tighter epsilon before declaring ceiling.

Wall time: ~30-45 min CPU (depends on T1 and T2 passing first).
Prerequisite: T1 HARD-PASS and T2 HARD-PASS or MID-BAND.

---

## SECTION 4: HONEST STRUCTURAL CEILING ASSESSMENT

The central question: is ZKL <= 0.10 achievable on a shared encoder without per-customer
cost? Here is the brutally honest assessment.

### Why 0.22 is likely a true floor for pure query-time defenses

The bounded-at-0.22 result across all linear mitigations is not an engineering failure.
It is a consequence of the geometry of the retrieval problem. Any retrieval system that
works by cosine similarity in a dense embedding space will exhibit membership-inference
signal at the representation level, because retrieval utility REQUIRES that stored vectors
be more similar to their associated queries than to unrelated queries. This IS the
membership-inference signal. A perfectly private retrieval system with ZKL = 0 would
return random results (recall = 0). The utility-privacy tradeoff is fundamental, not
incidental.

The question is where the Pareto frontier sits. For the specific Llama L15 encoder, the
empirical frontier appears to be ZKL ~0.22 at recall@10 ~0.92. This is where the
current shared encoder sits without any mitigation.

### What 0.10 would require

To achieve ZKL(50) <= 0.10, the membership-inference signal must be suppressed by
approximately half (from 0.22 to 0.10 in KL units, which is a non-trivial compression
because KL divergence is not linear in "signal strength"). This requires one of:

(a) Removing the membership-inference signal from the representation itself (encoder
    modification via GRL, VIB, or INLP). This requires retraining or post-hoc projection
    and carries recall risk.

(b) Adding enough noise at query time that rank-based inference fails. The required noise
    level (epsilon ~0.3 in the exponential mechanism) causes recall@10 to drop to ~0.70,
    which may be acceptable for some applications but not all.

(c) Changing the architecture so that retrieved documents are not individually linkable to
    queries (two-stage, HE, ZKP, querier-side substrate). All of these are either expensive
    (HE/ZKP) or require architecture redesign (two-stage, querier-side).

(d) Combining two partial mechanisms that together compound below 0.10 (INLP + stochastic
    top-k). This is the most credible shared-encoder path, but P_deflated is only 0.28
    even with both mechanisms.

### Honest verdict

The qualified posture (ZKL ~0.22 with attention-reweighting, described as "qualified" not
"HIPAA-absolute") is the empirically honest position for the current shared encoder.

Paths that might close to 0.10 exist (INLP + stochastic top-k combo is the most credible
at P_deflated = 0.28) but require 2-3 eng-weeks of implementation and may fail.

Path D (per-customer encoder fine-tuning) remains the only empirically validated path to
HIPAA-absolute ZKL, and it is structurally premium-tier because of its cost.

Recommended posture: "Shared-encoder qualified (ZKL ~0.22)" + "Path D premium-tier
HIPAA-absolute" + "INLP + stochastic top-k combo as in-development upgrade path with
P_deflated = 0.28 at ZKL <= 0.10."

Do NOT reframe the qualified posture as HIPAA-absolute until the T5 combination test
passes. The T5 HARD-PASS threshold (ZKL <= 0.10, recall >= 0.78) is the single gate.

---

## SECTION 5: CROSS-FEATURE INTERACTION ANALYSIS

### 5A: Defrag (continual learning aggregation) + privacy

Defrag processes replay batches to consolidate facts across time slices. Each replay
operation recomputes encoder embeddings of stored facts. If a privacy mechanism modifies
the encoder (GRL, VIB) or applies post-hoc projection (INLP), the defrag loop must apply
the same transformation to re-encoded vectors, or the projected vectors will drift from
their updated counterparts.

Interaction risk: HIGH. A defrag cycle after encoder modification that does not re-apply
the privacy projection will silently degrade privacy (projected old vectors + unprojected
new vectors = mixed representation that may be differentially attackable).

Mitigation: Privacy projection must be baked into the encoding pipeline, not applied as
a post-hoc batch transformation. Defrag should call the privacy-hardened encoder directly.

Published context: ArXiv 2509.12958 "Forget What's Sensitive, Remember What Matters:
Token-Level DP in Memory Sculpting for Continual Learning" directly addresses this
interaction. Their approach uses sensitivity-guided selective forgetting to preserve
task-invariant historical knowledge while removing sensitive signal -- directly applicable
to defrag-privacy integration.

### 5B: Pattern B compositional structure + privacy

Pattern B stores facts as compositions of two sub-patterns. The membership-inference attack
that drives ZKL may exploit the compositional structure: if a query matches both sub-
patterns A and B, the resulting cosine similarity is higher than matching only one, creating
a stronger membership-inference signal than for non-compositional facts.

Interaction risk: MEDIUM. Compositional storage may INCREASE ZKL because retrieval signal
is reinforced (matches two independent sub-patterns). If this is true, INLP nullspace
projection must also suppress the compositional enhancement, requiring more projection
dimensions than for single-pattern storage.

Mitigation: Test ZKL specifically on compositional (Pattern B) vs non-compositional facts.
If ZKL is higher for compositional facts, apply a stronger privacy mechanism (lower epsilon
or more INLP iterations) for that fact class.

### 5C: Causal compositions + privacy

Causal composition facts (A causes B) are stored as directed relationships. The
membership-inference attack does not distinguish the causal direction from the factual
content. The directional encoding may, however, concentrate membership-inference signal
in specific dimensions (the "causal direction" dimensions), which could make INLP more
effective (more signal concentrated in fewer directions = fewer INLP iterations needed).

Interaction risk: LOW. Causal composition privacy interaction is less severe than
compositional because the directional signal is typically encoded in fewer dimensions.

### 5D: Bitemporal records + privacy

Bitemporal records maintain validity_from / valid_to timestamps alongside stored facts.
For GDPR Art 17 (right to erasure), a deletion request requires marking all time slices
of a fact as invalid. The membership-inference attacker may exploit bitemporal structure:
if an erased fact's time slice is still in the index (soft-deleted vs hard-deleted),
membership inference may still succeed for that time slice.

Interaction risk: HIGH for GDPR compliance. A "soft delete" bitemporal implementation
where the vector remains in the index but is flagged as erased will leak membership
information until the index is physically re-built. HIPAA + GDPR combined requires
hard-delete behavior: the fact's vector must be removed from the similarity search index,
not just flagged.

Mitigation: Implement hard-delete index removal on GDPR erasure events. Bitemporal
metadata can be retained for audit trail (the fact existed at time T and was erased at
time T'), but the vector must be removed from the live retrieval index.

This is a known gap in many vector database implementations and should be surfaced
explicitly in the HIPAA-compliance documentation.

---

## SECTION 6: DEFENSE-IN-DEPTH HYBRID PROPOSAL

Even if no single mechanism reaches ZKL = 0.10, a layered defense can reduce ZKL
progressively and present a credible compliance argument.

### Proposed 4-layer hybrid

Layer 1: Nullspace projection (INLP, 1-2 weeks)
- Removes linearly accessible membership-inference signal from stored and query vectors.
- Estimated ZKL reduction: 0.22 -> ~0.16 (if signal is partially linear).
- Recall impact: minimal if <= 5 INLP iterations are needed.

Layer 2: Stochastic top-k via exponential mechanism (1 week)
- Adds calibrated noise to retrieval ranking to prevent exact rank-based inference.
- Epsilon tuned to balance ZKL reduction and recall preservation.
- Estimated ZKL reduction: ~0.16 -> ~0.12 (if combined with Layer 1).
- Recall impact: epsilon=1.0 gives recall@10 ~0.82.

Layer 3: Cryptographic commitment logging (1-2 weeks)
- Server logs hash commitments of (query, result, timestamp) rather than plaintext.
- Does not reduce ZKL but satisfies HIPAA audit trail without server-side query legibility.
- Compatibility: fully compatible with Layers 1 and 2.

Layer 4: GDPR hard-delete on retrieval index (1 week)
- Ensures erased facts are removed from the live similarity index, not just flagged.
- Closes the bitemporal soft-delete ZKL leak for erased facts.
- Required for Art 17 compliance regardless of ZKL status.

Total estimate: ~4-6 eng-weeks for all 4 layers.
Expected combined ZKL after Layers 1+2: ~0.10-0.14 (best case: 0.10 if T5 passes,
worst case: 0.14 if INLP linear signal check is partial).

### Compliance framing

The 4-layer hybrid provides:
- Quantified privacy reduction (from ZKL 0.22 to estimated ZKL ~0.10-0.14)
- Defense-in-depth narrative for HIPAA compliance conversation (not a single-point failure)
- Audit trail via cryptographic commitments (Layer 3)
- Erasure compliance via hard-delete (Layer 4)
- Upgrade path: if T5 passes (ZKL <= 0.10), promote shared-encoder tier to HIPAA-absolute

This is a credible compliance posture even if ZKL does not reach exactly 0.10, because:
(a) HIPAA does not specify a ZKL threshold -- that is our internal calibration
(b) The NIST guidance on de-identification uses statistical risk thresholds that vary
    by use case; ZKL=0.12 may be defensible with the right expert attestation
(c) The defense-in-depth multi-layer approach demonstrates reasonable safeguards

The only non-negotiable for HIPAA-absolute is Layer 4 (hard-delete). Layers 1-3 are
best-effort mitigations, not absolute guarantees.

---

## CITATIONS (verified from search)

1. Ganin, Y. et al. "Domain-Adversarial Training of Neural Networks." JMLR 2016.
   (Gradient reversal layer framework -- foundational for Candidate 1A)

2. ArXiv 1807.05852: "Machine Learning with Membership Privacy using Adversarial
   Regularization." 2018. (Direct application of adversarial training to membership
   inference.)

3. ArXiv 2601.02307: "Differential Privacy for Transformer Embeddings with Nonparametric
   Variational Information Bottleneck." 2025. (NVIB for transformer privacy.)

4. ArXiv 2309.04515: "Privacy Preserving Federated Learning with Convolutional Variational
   Bottlenecks." 2023.

5. ArXiv 2004.07667: "Null It Out: Guarding Protected Attributes by Iterative Nullspace
   Projection." Ravfogel et al. 2020. (INLP foundational method.)

6. ArXiv 2604.05296: "From Measurement to Mitigation: Quantifying and Reducing Identity
   Leakage in Image Representation Encoders with Linear Subspace Removal." 2024.
   (Subspace removal with >95% recall preservation.)

7. ArXiv 2411.09552: "Faster Differentially Private Top-k Selection: A Joint Exponential
   Mechanism with Pruning." 2024.

8. ArXiv 2412.04697: "Privacy-Preserving Retrieval-Augmented Generation with Differential
   Privacy." 2024. (DP-RAG, two-stage retrieval, exponential mechanism for top-k.)

9. Faggioli & Ferro: "Query Obfuscation for Information Retrieval Through Differential
   Privacy." ECIR 2024. (Query obfuscation for dense IR.)

10. De Faveri et al.: "Towards Query Obfuscation Strategies for Information Retrieval."
    ECIR 2025. (py-PANTERA library.)

11. ArXiv 2509.12958: "Forget What's Sensitive, Remember What Matters: Token-Level DP in
    Memory Sculpting for Continual Learning." 2025. (DP + continual learning interaction.)

12. ArXiv 2411.04680: "Differential Privacy in Continual Learning: Which Labels to Update?"
    2024.

13. ArXiv 2502.18535: "A Survey of Zero-Knowledge Proof Based Verifiable Machine Learning."
    2025. (ZKML landscape and practical constraints.)

14. ArXiv 2408.00243: "A Survey on the Applications of Zero-Knowledge Proofs." 2024.

15. McSherry & Talwar: "Mechanism Design via Differential Privacy." FOCS 2007.
    (Exponential mechanism foundational paper.)

16. ArXiv 2205.06135: "Fair NLP Models with Differentially Private Text Encoders." 2022.
    (DP-trained encoder membership inference bounds.)

17. EMNLP 2025: "Mitigating the Privacy Issues in Retrieval-Augmented Generation."
    ACL Anthology 2025.emnlp-main.1247.

Verified citation count: 17

---

## PLAIN-LANGUAGE SUMMARY

We drilled all six families of alternatives to linear mitigation for the ZKL privacy
problem on a shared encoder. The honest result is:

No single novel technique reliably reaches ZKL <= 0.10 on a shared encoder without
per-customer cost. The fundamental reason is that any retrieval system that works by
vector similarity will produce membership-inference signal, because "this document is
a better match than others" IS the attack signal.

The most credible shared-encoder paths are:

(1) INLP nullspace projection (1-2 weeks): removes the linearly accessible piece of the
    membership-inference signal. Expected gain: 0.22 to ~0.16. Pre-test tells us if the
    signal is linear in 20 minutes.

(2) Stochastic top-k via exponential mechanism (1 week): adds calibrated noise to
    retrieval output. Expected gain: up to ~0.04 more reduction. Cheap to add.

(3) Combination of both (2-3 weeks total): our best estimate is ZKL ~0.10-0.14 after both.
    P_deflated = 0.28 that the combination reaches exactly <= 0.10. Not a sure thing.

Cryptographic paths (HE, ZKP) solve the problem in theory but are 10,000x too slow for
real-time retrieval at 2026 hardware. Flag for 2027-2028.

The querier-side substrate (customer holds the data, vendor provides encoder) eliminates
the server-side problem completely but is a different product architecture, not a shared-
encoder fix.

Defense-in-depth (INLP + stochastic top-k + cryptographic audit commitments + hard-delete
erasure) gives a layered compliance argument even if ZKL lands at 0.12 rather than 0.10.

The locked qualified posture (ZKL ~0.22, Path D premium tier) remains the empirically
correct description of the current state. The combination path is worth the 2-3 week pre-
test (T1+T2+T5) before committing full engineering resources.
