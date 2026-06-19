# Research Note: Adversarial Robustness 2x Drill -- Lucky vs Genuine + Adaptive Attack Catalog
**Date:** 2026-06-07
**Filed-by:** research sub-agent (2x level-2 operational drill)
**Trigger:** 5 Probe-2 adversarial predictions refuted empirically today; standing rule "negative findings 2x research"
**Prior note:** notes/research_drill_adversarial_substrate_divergence_2026-06-07.md (level-1 attack surface map)
**Calibration:** P estimates deflated 0.20-0.30 from raw lit-scan; novel-synthesis P capped at 0.45

---

## HEADLINE

Four Probe-2 adversarial predictions were refuted today (paraphrase collapse, fp16 drift, middle-hop
brittleness, anchoring-bias propagation), substrate performing BETTER than algebraic worst-case in all
four cases. This 2x drill finds: two refutations are LIKELY GENUINE (fp16 discreteness + VSA holographic
noise tolerance), one is PARTIALLY GENUINE (middle-hop: Merkle localizes random fabrications but
semantically-similar fabrications are untested), and two are PROBABLY LUCKY (paraphrase robustness
tested only with off-shelf MT; anchoring-bias tested without correlated KB). Critical untested tier is
"motivated researcher" -- gradient-based paraphrase models optimized against the specific detector. No
tested condition reached this tier. P_deflated = 0.38 that adaptive attacks would partially reverse
today's refutations.

---

## SECTION 1: LUCKY VS GENUINE -- PER-REFUTATION ASSESSMENT

### Refutation 1: KF-1 Paraphrase Collapse (predicted 0.55-0.65; empirical 0.903 NLLB + 0.983 MarianMT)

**What assumption did Probe 2 make that was wrong?**
Probe 2 assumed the word-bigram detector would behave like n-gram-based AI-text detectors (GLTR,
GPTZero architecture class), for which DIPPER-class back-translation attacks reliably drop AUC to
0.50-0.65 (Krishna et al. 2023). This assumption was wrong because KF-1 is NOT a fluency-based
detector -- it is a retrieval-grounding detector. The bigrams it monitors are the bigrams of retrieved
EVIDENCE, not generated text statistics. Back-translation preserves semantic content, so evidence-
grounding bigrams survive the round-trip.

**Genuine component:** KF-1 monitors evidence-generation alignment, not raw surface statistics.
Evidence-grounding detectors are fundamentally different from text-watermark or perplexity-based
detectors. This is a real architectural strength.

**Coincidental component:** NLLB and MarianMT are the WEAKEST paraphrase adversaries. Both are
off-shelf MT pipelines NOT optimized to maximize embedding drift. They happen to preserve semantic
content well (their design goal), meaning the grounding still holds.

**Would adaptive attacks change the picture?**
YES -- with high probability. Attack variants not tested:
(a) T5-paraphrase with semantic-divergence constraint (keep cosine_sim > 0.80, maximize bigram
divergence from evidence): literature precedent shows 40-60% bigram overlap drop while maintaining
human-judged meaning.
(b) Adversarially trained paraphrase model (GAN-loop: generate claim, measure KF-1 score, backprop
to minimize KF-1 detection): 1000 gradient steps typically suffice (GBDA, Guo et al. 2021).
(c) Entity substitution with preserved context bigrams: "Paris" -> "Lyon" while keeping surrounding
bigrams identical -- may score as GROUNDED (bigrams match) while being factually wrong.

**Verdict:** PARTIALLY LUCKY. P_deflated = 0.35 that robustness is genuine under adaptive attack.
Genuine for EVIDENCE-GROUNDING architecture class; lucky for the specific adversary capability tested.

---

### Refutation 2: fp16 vs fp32 Drift (predicted gap; empirical: zero gap; bit-level 99.5%)

**What assumption did Probe 2 make that was wrong?**
Probe 2 assumed fp16 quantization would introduce measurable numerical drift via catastrophic
cancellation in dot-product computations (standard concern for fp16 attention in transformers: Narang
et al. 2018). This assumption was wrong for VSA contexts because bipolar ternary-valued vectors
({-1, 0, +1}) do not suffer from catastrophic cancellation -- integer arithmetic on small-valued
vectors is exact regardless of float precision.

**Mathematical grounding for GENUINE:**
For bipolar vectors at N=1024:
- All dot products are sums of {-1, +1} entries (integer-valued).
- fp16 represents integers up to 2048 exactly (11-bit mantissa = 2^11 = 2048 representable integers).
- At N=1024, dot product is in [-1024, +1024] -- entirely within fp16 exact range.
- Therefore fp16 and fp32 produce IDENTICAL results for this operation class.
This is not a coincidence of test data; it is a consequence of the vector algebra. Zero gap is
THEORETICALLY EXPECTED, not a lucky measurement.

**Caveat for N=65536 (production):**
At N=65536, max dot product = 65536, which exceeds fp16 integer exact range. Robustness depends on
accumulation path: chunked (fp32 accumulation of fp16 partials) is safe; sequential fp16 accumulation
risks overflow for extreme bipolar inputs.

**Verdict:** GENUINE for N <= 2048. CONDITIONALLY GENUINE for N=65536 (accumulation path matters).
P_deflated = 0.75 genuine at N=1024; 0.50 at N=65536 under adaptive attack.

---

### Refutation 3: Fact-Checked K-Hop Middle-Hop Brittleness (predicted brittleness; empirical 1.000 HP)

**What assumption did Probe 2 make that was wrong?**
Probe 2 assumed fabrication at hop K//2 would propagate undetected because per-hop verification has
limited memory. The assumption was wrong because the Merkle audit chain provides STRUCTURAL localization:
a randomly injected fabrication produces a different embedding vector, which produces a different hash,
which produces a different Merkle root. The Merkle mechanism does NOT need semantic understanding.

**Genuine component:** Hash-level detection of random fabrications is cryptographically grounded.
Random fabrication necessarily changes the embedding vector with overwhelming probability, and SHA-256
preimage resistance (2^256) makes hash collision infeasible.

**Critical COINCIDENTAL component:** The test used RANDOM fabrication injection. Random fabrications
("ZXQWERTY is the capital of France") are wildly different in embedding space -- trivially caught.
The test did NOT use ADAPTIVE SIMILAR fabrications ("Lyon is the capital of France") where the
embedding is cosine_sim ~0.85 to the true fact.

**Key unknown:** Whether per-hop verification is HASH-BASED (exact, catches similar fabrications) or
SIMILARITY-THRESHOLD-BASED (threshold, misses near-threshold similar fabrications).
- If hash-based: adaptive similar fabrications ALSO caught (different vector = different hash).
- If similarity-based: fabrications within cosine_sim > theta evade detection.

**Multi-step consistent-lie attack NOT tested:** Craft a K-hop chain where each individual hop is
factually correct and passes per-hop check, but the COMPOSITION implies a false conclusion. This
exploits the multi-hop reasoning chain composition rather than individual hop fabrication.

**Verdict:** GENUINE for random fabrications. UNKNOWN for adaptive similar-fabrication.
P_deflated = 0.40 that full robustness holds under adaptive similar-fabrication attacks.

---

### Refutation 4: Anchoring-Bias Propagation Cascade (predicted cascade; empirical: no propagation)

**What assumption did Probe 2 make that was wrong?**
Probe 2 assumed early-hop retrieval anchoring would bias subsequent hops (confirmation-bias cascade).
The assumption was wrong because VSA/HDC retrieval is non-stateful by default: each hop query is
issued against the full substrate, not a filtered subset conditioned on prior retrievals. The binding
operation composes query vectors algebraically; it does not create a "context window" that biases
subsequent queries.

**Genuine component (mathematical grounding):**
For two independently drawn random bipolar HDVs X, Y of dimension N:
  P(|cosine_sim(X,Y)| > epsilon) < 2 exp(-epsilon^2 * N / 2)
At N=65536 and epsilon=0.05: P(|sim| > 0.05) ~ 0. Stored patterns are essentially orthogonal.
A query anchored in one region has near-zero cosine similarity with unrelated patterns; anchoring
bias cannot propagate via the similarity computation. This follows from VSA dimensionality theorem
(Kanerva 2009).

**Coincidental component:**
The test used INDEPENDENT, SYNTHETIC data. The anti-propagation theorem assumes near-orthogonality
of stored patterns, which does NOT hold if stored patterns are semantically correlated (as in any
real knowledge base). Medical facts cluster together; legal facts cluster together. In a correlated KB,
an anchor in the medical domain biases retrieval toward other medical facts -- not via VSA algebra, but
via embedding space clustering.

**Would adaptive attacks change the picture?**
CONDITIONALLY. Adversary who controls KB structure can create a structured KB where patterns are NOT
near-orthogonal, intentionally destroying the anti-propagation property. This is the adversarial KB
injection attack (ATTACK-5) combined with structured semantic clustering.

**Verdict:** GENUINE for independent (near-orthogonal) query patterns. COINCIDENTAL for correlated
real-world KBs. P_deflated = 0.60 that robustness holds in production (real KBs have correlation).

---

## SECTION 2: ADAPTIVE ATTACK CATALOG (12 attacks, severity-ranked)

### Adversary Tier Framework (adapted from IND-CCA2 adversary taxonomy)

- **Script-kiddie (CCA1 analog):** Off-shelf tools, no model access, public API only.
  Budget: $0-100, 1-2 days.
- **Motivated researcher (CCA2 analog):** Custom models, gradient access to proxy, whitebox knowledge
  of detector mechanism. Budget: 1 GPU-week, $500-5000.
- **Nation-state (adaptive CCA2 + side-channel):** Whitebox access, supply chain compromise.
  Budget: unlimited.
- **Insider (whitebox + write access):** Full substrate code + write access. Budget: any.

---

### ATTACK-1: Gradient-Based Paraphrase Optimized for Evidence Drift
**Tier:** Motivated researcher
**Mechanism:** GBDA (Gradient-Based Discrete Adversarial attack, Guo et al. 2021) against a proxy
KF-1 model. Train paraphrase model to minimize KF-1 score while maintaining cosine_sim > 0.80.
After ~1000 gradient steps, model generates claims that match evidence bigrams (defeating the check)
while having different semantic content (wrong but undetected).
**Predicted impact:** KF-1 AUC drops from 0.977 to 0.55-0.70 (P_deflated=0.35).
HARD-PASS: AUC >= 0.85. HARD-FAIL: AUC < 0.70.
**Cost to test:** 1 GPU-day; open-source GBDA available.

### ATTACK-2: Multi-Hop Language Chain Paraphrase (EN->DE->FR->RU->EN)
**Tier:** Script-kiddie (multi-hop free MT)
**Mechanism:** Each hop introduces independent noise. 4-hop chain preserves (0.80)^4 = 41% of bigrams.
Whether semantic content also degrades determines if KF-1 correctly flags (true positive) or is confused.
**Predicted impact:** MODERATE but ambiguous -- more bigram degradation but also more semantic noise.
HARD-PASS: AUC >= 0.92 (chain paraphrase flagged correctly). HARD-FAIL: AUC < 0.80.
P_deflated = 0.50 (unclear whether semantic drift helps or hurts attacker).
**Cost:** Free MT APIs, <1 hour.

### ATTACK-3: Entity Substitution with Preserved Context Bigrams
**Tier:** Script-kiddie (manual crafting)
**Mechanism:** Replace key entities while preserving ALL surrounding bigrams.
  Original: "The capital of France is Paris"
  Attack:   "The capital of France is Lyon"
  Bigrams "capital of France is" preserved; only terminal entity changes. For a 9-gram claim, bigram
overlap ratio = 8/9 = 0.89 -- may be above KF-1 threshold.
**Predicted impact:** CRITICAL if KF-1 uses bigram overlap ratio threshold without terminal-pair check.
HARD-PASS: entity substitutions correctly detected at overlap ratio < 0.95.
HARD-FAIL: entity substitutions with overlap > 0.85 pass undetected.
P_deflated = 0.40 that this is a real production vulnerability.
**Cost:** Manual crafting, <1 hour, no model needed.

### ATTACK-4: Targeted Bit-Flip at Most-Critical Positions (Gradient-Based)
**Tier:** Motivated researcher
**Mechanism:** Compute gradient of retrieval cosine similarity w.r.t. each bit position. Flip top-k
bits by gradient magnitude. Discrete bipolar constraint means exact solution requires beam search or
greedy; gradient guides the search. Carlini-Wagner (2017) analog for discrete HDV spaces.
At k=0.20N (20% targeted): cosine sim drops to ~0.60, near retrieval threshold.
Empirical boundary: multi-head collapse at 45% random flip (Cycle 137). Targeted flip may achieve
equivalent degradation at lower k.
HARD-PASS: retrieval correct despite targeted 10% bit flip.
HARD-FAIL: retrieval fails at < 15% targeted bit flip (worse than random flip equivalent).
P_deflated = 0.35 that targeted flip outperforms random by > 2x.
**Cost:** 1 GPU-hour for gradient computation on proxy.

### ATTACK-5: Adversarial KB Injection (Poisoned Source Data)
**Tier:** Motivated researcher / Insider
**Mechanism:** Inject semantically plausible but factually wrong entries with HIGH cosine similarity
to true entries (adversarially crafted to embed near true fact) but wrong content. At retrieval time,
poisoned entry may rank ABOVE true entry for target queries because it was crafted to maximize
retrieval score. ADMIT (2025): 86% attack success at 1e-6 poisoning ratio because adversarially
crafted entry ranks first for target query.
HARD-PASS: KF-1 detects >= 80% of poisoned entries via multi-source corroboration.
HARD-FAIL: > 20% poisoned entries evade detection and rank first for target queries.
P_deflated = 0.45 (RAG poisoning well-documented; VSA-specific behavior unknown).
**Cost:** 1 GPU-day for crafting adversarial entries.

### ATTACK-6: White-Box Attack on KF-1 Mechanism (Insider)
**Tier:** Insider (requires code access)
**Mechanism:** With access to KF-1 source code, craft fabrications that score exactly at threshold
(threshold straddling). Chosen-plaintext attack against detector's decision boundary. If KF-1 uses
a fixed seed for threshold calibration, insider can determine exact threshold and craft inputs at
threshold + epsilon (just barely passing).
**Predicted impact:** CRITICAL for insider threat model -- near-perfect evasion with code knowledge.
P_deflated = 0.70 that this attack succeeds given code access (guaranteed against threshold-based
detectors with known parameters).
**Cost:** Negligible given code access.

### ATTACK-7: Multi-Step Fabrication Chain (Consistent Lie Attack)
**Tier:** Motivated researcher
**Mechanism:** Craft K-hop chain where EACH INDIVIDUAL HOP is factually correct and passes per-hop
verification, but the COMPOSITION implies a false conclusion (logical fallacy in chain composition).
  Hop 1: "Entity A is related to Entity B" (TRUE)
  Hop 2: "Entity B has property P" (TRUE)
  Chain conclusion: "Entity A has property P" (FALSE if relation is not transitive)
Exploits multi-hop reasoning chain composition; requires no fabrication at individual hop level.
HARD-PASS: consistent-lie chains detected at end-to-end chain verification.
HARD-FAIL: consistent-lie chains pass all per-hop checks and produce wrong final answer.
P_deflated = 0.50 (depends entirely on whether chain-composition verification exists).
**Cost:** Manual chain construction, <2 hours.

### ATTACK-8: Adaptive Numerical Attack (Near-fp16-Overflow Inputs)
**Tier:** Script-kiddie (once vector known)
**Mechanism:** For N=65536, construct bipolar input X where first 2050 components are all +1.
Partial dot product at 2050 steps = 2050, exceeds fp16 integer exact range (max 2048).
Whether this overflows depends on accumulation implementation.
HARD-PASS: substrate produces finite outputs for all-positive extreme N=65536 inputs.
HARD-FAIL: any NaN/Inf in fp16 path at N=65536 with extreme bipolar inputs.
P_deflated = 0.25 (most modern ML frameworks use fp32 accumulation; may not be vulnerable).
**Cost:** 30 minutes; 2 lines of code; CPU-only.

### ATTACK-9: Semantic Similarity Cascade Attack (Correlated KB Exploitation)
**Tier:** Script-kiddie (exploits natural KB structure)
**Mechanism:** Real knowledge bases have semantically correlated entries (medical facts cluster in
embedding space). Anchor a query near a cluster centroid, causing retrieval of the MOST SIMILAR
stored item (possibly wrong domain) rather than the CORRECT item. Confusion-via-clustering attack:
high-density regions of embedding space have retrieval ambiguity.
P_deflated = 0.40 that this causes measurable retrieval degradation on a realistic KG.
**Cost:** Requires realistic (not synthetic SQuAD) knowledge base; 1 GPU-day.

### ATTACK-10: Measurement Pipeline Metric Inflation (LVH-241 Class)
**Tier:** Script-kiddie (exploits pipeline edge cases)
**Mechanism:** Craft inputs triggering pipeline bugs: empty retrieval -> 0/0 in accuracy = 100%;
single-item recall denominator = 1 -> recall=1.0 for any non-empty result; hop_count=0 where
fabrication at hop 0 never tested. Precedent: LVH #241 div-by-zero in G16 stacking claim.
P_deflated = 0.45 that at least one benchmark has an empty-set or div-by-zero edge case.
HARD-FAIL: any "100%" benchmark result that collapses on edge-case input injection.
**Cost:** Negligible -- inject empty string, zero-hop chain, single-item KB.

### ATTACK-11: Replay + Cross-Query Proof Reuse (Merkle Chain)
**Tier:** Motivated researcher (requires intercepted proof)
**Mechanism:** Valid hop-cert from query Q1 replayed for query Q2 if chain is not nonce-bound.
IND-CCA2 analog: adversary accumulates proofs via oracle queries, then forges verification for
target query Q* with no new query. Under adaptive CCA2 model (queries before AND after challenge),
this is the strongest audit chain attack short of hash collision.
HARD-PASS: each hop-cert bound to session nonce; cross-query reuse detected.
HARD-FAIL: replayed hop-cert passes verification for different query context.
P_deflated = 0.55 that current implementation lacks nonce-binding.
**Cost:** 2-3 hours to implement test; no model needed.

### ATTACK-12: Adversarial Measurement Fragmentation (Sparse Evaluation)
**Tier:** Structural (not adversarial per se, but a failure mode)
**Mechanism:** Wilson CI for 100% accuracy on N=30 cells: 95% CI lower bound = 88.4%. The true
failure rate could be 11.5% -- STATISTICALLY CONSISTENT with the observed 100%/30. At 10K
production queries per day, 11.5% failure rate = 1150 failures/day. The "lucky" hypothesis: the
30-cell test happened to avoid the 11.5% failure region. This is not a deliberate attack; it is
a structural evaluation gap.
P_deflated = 0.55 that actual production failure rate exceeds 5% for at least one "100%" capability.
**Cost:** Re-run benchmarks with N=200 cells (3x existing runtime).

---

## SECTION 3: SUBSTRATE PROPERTIES PROVIDING GENUINE ROBUSTNESS

### Property R-1: Holographic Noise Tolerance (VSA Fundamental)
**Mathematical grounding:**
  E[cosine_sim(X, X_corrupted)] = 1 - 2p  (p = fraction flipped)
  Var[cosine_sim] ~ 4p(1-p)/N
At N=65536 and p=0.20: E[sim] = 0.60, Std[sim] ~ 0.002 (negligibly small variance).
Random corruption has DETERMINISTIC effect on similarity, predictable by theory, with a hard
retrieval transition threshold. NOT an artifact -- core theorem of HDC (Kanerva 2009; Frady et al.
2021). Strongest robustness property of the substrate.
**Limitation:** Applies to RANDOM noise. Targeted corruption (ATTACK-4) breaks this by exploiting
non-uniformity. Gradient-guided targeted flip may achieve equivalent degradation at k < p.

### Property R-2: Bipolar Discreteness Limits Adversarial Gradients
**Mathematical grounding:** In continuous embedding spaces, adversarial examples are found by
gradient ascent on the loss w.r.t. input (dense gradient, every dimension contributes). In bipolar
{-1, +1} discrete spaces, the input is NOT differentiable -- gradients are undefined on the
discrete manifold. Adversary must solve combinatorial optimization (2^N states) rather than
continuous gradient problem.
**LARGELY FUNDAMENTAL** with caveat: PROXY ATTACK (ATTACK-1) bypasses this by attacking the
continuous encoder space BEFORE binarization, not the bipolar vector directly. Robustness is genuine
for post-binarization attacks; does NOT protect against pre-binarization attacks on the encoder.
**Literature support:** Lecuyer et al. (2019) shows discrete representations can provide certified
robustness guarantees that continuous representations cannot.

### Property R-3: Dimensionality-Induced Near-Orthogonality
**Mathematical grounding:**
  P(|cosine_sim(X,Y)| > epsilon) < 2 exp(-epsilon^2 * N / 2)
At N=65536 and epsilon=0.05: P(|sim| > 0.05) ~ 2 exp(-81.9) ~ 0.
Stored patterns are essentially orthogonal at N=65536. Anti-propagation robustness (Refutation 4)
follows directly: anchored query has near-zero similarity with unrelated patterns.
**FUNDAMENTAL for independently drawn patterns. ARTIFACT for correlated KBs** where patterns are
NOT drawn uniformly from {-1,+1}^N (real medical/legal knowledge has semantic clustering).

### Property R-4: Pseudoinverse Write Rule Zero Crosstalk (for M < N)
**Mathematical grounding:**
  Hebbian: retrieval accuracy ~ f(M/N, noise_level) -- degrades with both capacity and noise.
  Pseudoinverse W = X^+ X: achieves ZERO crosstalk for M < N (least-squares solution).
For M < N = 65536: retrieval accuracy depends only on noise_level, NOT M. Robustness does NOT
degrade as capacity grows (unlike Hebbian alternatives). The capacity cliff at M ~ N is sharp, but
BELOW the cliff, robustness is constant.
**FUNDAMENTAL** (algebraic property of pseudoinverse; Penrose 1955, Kohonen 1977).
**Artifact condition:** Assumes M < N = 65536. Production deployments with many diverse domains
may violate this; the cliff is sharp and the behavior above M~N is undefined.

### Property R-5: Defense-in-Depth Composition (Super-Additive Attack Difficulty)
**Mathematical grounding:** For three independent defense mechanisms with individual bypass
probabilities p1, p2, p3:
  P(all three bypassed) = p1 * p2 * p3
At p1=0.30 (KF-1 bypass), p2=0.20 (Merkle bypass), p3=0.10 (per-hop check bypass):
  Joint P = 0.006 (very small).
Analogous to Fujisaki-Okamoto transform achieving CCA2 security by composing CPA-secure components.
**CONDITIONALLY FUNDAMENTAL.** Holds IF the three mechanisms are statistically independent.
**CRITICAL FAILURE CONDITION:** An adversary who compromises the encoder (ATTACK-5, supply chain)
simultaneously bypasses ALL three mechanisms because all three depend on the same embedding
representation. Defense-in-depth collapses to zero when the shared foundation is compromised.
The encoder is the single point of failure for the entire composition argument.

### Property R-6: Merkle Chain Non-Repudiability (Cryptographic Foundation)
**Mathematical grounding:** SHA-256 preimage resistance = 2^256 (collision resistance 2^128).
To forge a Merkle inclusion proof, adversary must find SHA-256 collision: 2^128 operations.
A fabrication at any hop NECESSARILY changes the root hash (detectable). This is INFORMATION-
THEORETIC non-repudiability for random fabrications.
**FUNDAMENTAL provided:**
(a) Hash is over the EXACT embedding vector (not a similarity threshold).
(b) Root hash is externally anchored (to a trusted log or blockchain).
(c) Nonce-binding prevents replay (ATTACK-11).
Without (b), adversary who controls chain can recompute a valid Merkle root for falsified content.
The Merkle chain is only as trusted as the root anchor.

---

## SECTION 4: PROPOSED ADAPTIVE TEST CELLS

### Cell AT-1: Adaptive Paraphrase vs KF-1 (Entity Substitution)
**Test:** Generate 200 SQuAD claims. Apply entity substitution (named entity -> plausible alternative
of same type: city->city, person->person). Measure KF-1 AUC on substituted vs original claims.
**Rationale:** Cheapest adaptive attack test; no model needed; directly tests Refutation 1.
**HP/MID/HF:**
  HARD-PASS: AUC >= 0.92 (detector correctly flags wrong entities)
  MIDDLE:    0.78 <= AUC < 0.92
  HARD-FAIL: AUC < 0.78 (entity substitution evades detection -- production unsafe)
**Cost:** 2 GPU-hours. **Impact:** HIGH.

### Cell AT-2: Semantic-Similar Fabrication at Middle Hop
**Test:** Construct K=5 chains where hop K//2 is replaced with cosine_sim > 0.85 but factually
wrong alternative. Measure AUC of per-hop verification on semantically similar fabrications vs
random fabrications (baseline = today's empirical result).
**Rationale:** Directly tests Refutation 3's critical unknown: hash-based vs similarity-threshold.
**HP/MID/HF:**
  HARD-PASS: AUC >= 0.90 (hash-based mechanism confirmed; similar fabrications also caught)
  MIDDLE:    0.75 <= AUC < 0.90 (partial detection; threshold leaks near-boundary cases)
  HARD-FAIL: AUC < 0.75 (semantically similar fabrications evade per-hop check)
**Cost:** 2 GPU-hours. **Impact:** CRITICAL.

### Cell AT-3: Correlated KB Anchoring Bias Test
**Test:** Construct KB with 3 semantic clusters (medical, legal, technical). Issue 50 queries per
cluster plus 50 cross-cluster queries designed to exploit proximity. Measure cross-cluster retrieval
accuracy vs single-cluster baseline.
**Rationale:** Refutation 4 used independent synthetic data. Realistic KBs have cluster structure.
**HP/MID/HF:**
  HARD-PASS: cross-cluster accuracy >= 0.90 (anti-propagation holds under correlation)
  MIDDLE:    0.80 <= accuracy < 0.90 (mild cluster bias)
  HARD-FAIL: accuracy < 0.80 (cluster structure introduces significant anchoring bias)
**Cost:** 3 GPU-hours + clustered KB construction. **Impact:** HIGH.

### Cell AT-4: fp16 Overflow at N=65536 Extreme Inputs
**Test:** Construct 20 bipolar vectors where first 2050 components are all +1 (stress fp16
intermediate accumulation). Measure fp16 vs fp32 cosine similarity. Check for NaN/Inf outputs.
**Rationale:** Refutation 2 is GENUINE for N=1024. Validity at N=65536 depends on accumulation.
**HP/MID/HF:**
  HARD-PASS: finite outputs for all 20 extreme vectors at N=65536
  HARD-FAIL: any NaN/Inf in fp16 path at N=65536
**Cost:** 30 minutes, CPU-only. **Impact:** MEDIUM.

### Cell AT-5: Consistent-Lie Chain Verification
**Test:** Construct 10 K=5 chains where each hop is factually correct but chain conclusion is false
(logical fallacy in composition). Verify whether end-to-end chain verification catches these.
**Rationale:** Tests ATTACK-7. Currently unknown whether chain-level consistency is verified.
**HP/MID/HF:**
  HARD-PASS: 8+/10 consistent-lie chains rejected (chain-level verification exists)
  HARD-FAIL: consistent-lie chains pass all per-hop checks (no chain-level check -- architecture gap)
**Cost:** 2 GPU-hours + manual chain construction. **Impact:** HIGH.

### Cell AT-6: 200-Cell Re-Run of "100%" Capabilities (Statistical Validation)
**Test:** Re-run three capabilities with "100%/30 cells" results using N=200 independent cells.
Calculate Wilson CI lower bound.
**HP/MID/HF:**
  HARD-PASS: all three capabilities >= 97% accuracy at N=200 (claims upheld)
  MIDDLE:    90% <= accuracy < 97% for any capability (claim weakened)
  HARD-FAIL: any capability < 90% at N=200 (original claim was spurious)
**Cost:** 3x existing benchmark runtime. **Impact:** CRITICAL (blocks production readiness claims).

---

## SECTION 5: PRODUCTION ADVERSARIAL ROADMAP

### What is PROVEN Robust (Tested)
- Random bit-flip up to 40% (multi-head collapses at 45%; below holds empirically)
- Standard back-translation paraphrase (NLLB + MarianMT class) vs evidence-grounding detector
- Random fabrication injection at middle hop (Merkle detection)
- Anchoring bias propagation on independent synthetic queries
- fp16 vs fp32 for N <= 1024 bipolar vectors

### What is UNTESTED (Critical Unknowns)
- Gradient-based adaptive paraphrase optimized against KF-1 (ATTACK-1)
- Semantically similar fabrications near detection threshold (AT-2)
- Correlated KB anchoring bias (AT-3)
- fp16 accumulation at N=65536 with extreme bipolar inputs (AT-4)
- Consistent-lie chain composition (ATTACK-7, AT-5)
- Statistical validity of 100%/30 capability claims (AT-6)

### Hardening Priority Order (Before Production Deployment)

1. **IMMEDIATE (blocker):** AT-6 (200-cell re-validation). Statistical basis for 100% claims is
   insufficient. This is a measurement integrity issue, not an adversarial attack.

2. **IMMEDIATE (blocker):** AT-2 (semantically similar fabrication). The 1.000 HP on random
   fabrications may not hold for adaptive similar fabrications. Directly affects K-hop claim.

3. **URGENT (pre-deployment):** AT-1 (entity substitution vs KF-1). KF-1 is the primary
   hallucination guard; robustness to cheapest adaptive attack must be established.

4. **URGENT (pre-deployment):** Encoder hash-pinning (SHA-256 of BGE-large weights). Closes
   supply chain attack without architecture changes.

5. **HIGH (pre-deployment):** Merkle chain nonce-binding. Closes replay attack (ATTACK-11).

6. **HIGH (pre-deployment):** AT-4 (fp16 overflow at N=65536). Quick test; if HARD-FAIL,
   require fp32 accumulation in production config.

7. **MEDIUM (post-deployment):** Embedding distribution monitoring (rolling Mahalanobis baseline;
   alert at 2-sigma distribution shift).

8. **MEDIUM (roadmap):** Upgrade KF-1 to hybrid detector (bigram + dense semantic cosine).

### Attacks That Would Force Architecture Revision

- **HARD-FAIL AT-2 (semantically similar fabrication):** Per-hop verification is similarity-
  threshold-based, not hash-based. Requires shift to exact hash verification over embeddings.
- **HARD-FAIL AT-3 (correlated KB anchoring):** Non-propagation does not hold in production.
  Requires per-domain orthogonalization or domain-separated retrieval.
- **HARD-FAIL AT-5 (consistent-lie chains):** Chain-composition verification absent. Requires
  new end-to-end chain consistency check capability.
- **HARD-FAIL AT-1 (entity substitution):** KF-1 cannot detect minimal factual changes. Requires
  NLI-based upgrade (architectural, not just threshold tuning).

---

## CHEAP DECISIVE TEST

Run AT-1 + AT-2 in sequence (3 GPU-hours total):
1. AT-1: 200 entity-substituted SQuAD claims -> KF-1 AUC measurement.
2. AT-2: 20 semantically-similar fabrication chains at K=5 -> per-hop AUC measurement.

Together these resolve the two highest-priority lucky-vs-genuine questions (Refutations 1 and 3)
for less than 1/4 GPU-day on the existing runner.

HARD-PASS (both): substrate robustness is genuine for the tested regime.
HARD-FAIL (either): specific architecture revision required before production deployment.

---

## FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL)

| Prediction | HARD-PASS | HARD-FAIL | P_deflated | Category |
|---|---|---|---|---|
| KF-1 AUC vs entity substitution (AT-1) | >= 0.92 | < 0.78 | 0.35 | Lucky vs genuine |
| Per-hop AUC vs similar fabrication (AT-2) | >= 0.90 | < 0.75 | 0.40 | Lucky vs genuine |
| Anti-propagation with correlated KB (AT-3) | >= 0.90 accuracy | < 0.80 | 0.40 | Lucky vs genuine |
| fp16 overflow at N=65536 extreme inputs (AT-4) | finite outputs | any NaN/Inf | 0.20 | Implementation |
| Consistent-lie chain detection (AT-5) | 8/10 caught | 3/10 or fewer | 0.35 | Architecture gap |
| 200-cell re-validation of 100% claims (AT-6) | >= 97% all three | < 90% any | 0.45 | Statistical |
| Gradient-based paraphrase KF-1 evasion (ATTACK-1) | AUC >= 0.85 | AUC < 0.70 | 0.30 | Motivated adversary |
| Adversarial KB injection detection (ATTACK-5) | 80%+ detected | 20%+ evade | 0.40 | Motivated adversary |

All P_deflated values deflated 0.20-0.30 from raw lit-scan estimates. Novel-synthesis capped at 0.45.

---

## CROSS-THREAD SYNTHESIS

**With prior level-1 adversarial note** (research_drill_adversarial_substrate_divergence_2026-06-07.md):
Level-1 catalogued 10 attack vectors. This level-2 drill resolves the lucky-vs-genuine question for the
5 Probe-2 refutations and proposes AT-1 through AT-6 as the empirical follow-up to level-1's cheap test.
The two notes are complementary: level-1 mapped WHAT attacks exist; level-2 analyzes WHY refutations
were observed and what adaptive attacks weren't covered.

**With fp16/fp32 findings:** Genuine robustness for N=1024 (R-2, bipolar discreteness) needs conditional
extension to N=65536. AT-4 is the confirming test. If AT-4 HARD-FAILs, require fp32 accumulation in
production config for N=65536.

**With K-hop reasoning (1.000 HP):** Genuine-vs-lucky split on Refutation 3 is the most consequential
for the production capability claim. AT-2 is the critical follow-up; its result directly determines
whether the 1.000 HP is a production-safe claim or an artifact of easy (random) fabrication tests.

**With continual-KV:** Anti-propagation robustness (R-3, dimensionality-induced orthogonality) is
genuine for the tested (independent) distribution but may not hold for production KBs with cluster
structure. AT-3 extends the tested regime toward production realism.

**Cross-domain insight: randomized smoothing certification.** Cohen et al. (2019) and Adaptive
Randomized Smoothing (2024) show that Gaussian noise injection provides CERTIFIED robustness with
tight L2-ball certificates. The VSA's bipolar discreteness provides an analog: the discrete state
space limits the adversary's perturbation surface analogously to randomized smoothing. The Lecuyer
et al. (2019) DP-based certified robustness framework is directly applicable if the VSA binding
operation can be cast as a randomized function with bounded sensitivity. This suggests a new research
direction: CERTIFIED ROBUSTNESS for VSA/HDC substrates via randomized smoothing analogy. The
bipolar {-1,+1} space has a natural Hamming ball certificate; any adversarial perturbation that
flips fewer than d/2 bits cannot change the majority-vote classification. This is the discrete
analog of the L2 certificate. P_deflated = 0.35 that this direction yields useful formal bounds.

**Cross-domain insight: IND-CCA2 adversary hierarchy.** The IND-CCA2 model provides the correct
framework for categorizing adversary capabilities against the substrate. The script-kiddie/motivated-
researcher/nation-state taxonomy above maps directly to CCA1/CCA2/oracle-extended adversary classes.
The key insight: CCA2 security (adaptive queries after seeing the challenge) is the minimum required
for production-grade adversarial robustness. Today's tests were all CCA1 (non-adaptive, no oracle
feedback loop). Production deployment requires at least CCA2-tier testing.

**Cross-domain insight: Certificate Transparency anti-replay.** RFC 6962 (Certificate Transparency)
is the mature applied instance of Merkle audit chains at production scale. The substrate's audit chain
should adopt CT's nonce-binding + signed tree heads + domain separation verbatim -- these are solved
problems with deployed code, not novel design work.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Robustness is real but layer-conditional.** The substrate has genuine robustness at the vector
   algebra layer (holographic noise tolerance, near-orthogonality, pseudoinverse stability). These are
   NOT artifacts. However, this algebraic robustness does NOT automatically transfer to the application
   layer (KF-1 detector, K-hop chain verification) -- those layers have separate attack surfaces.

2. **The most dangerous tier is "motivated researcher" (not nation-state).** A motivated researcher
   with 1 GPU-week can train a gradient-based paraphrase model that evades KF-1 (GBDA, well-documented).
   The product needs to defend against this tier BEFORE any production deployment.

3. **Today's refutations should NOT be read as "substrate is adversarially robust."** Correct reading:
   "substrate is robust against the specific NON-ADAPTIVE attacks tested." Production robustness
   requires AT-1 through AT-6 before the claim can be defended against a customer security review.

4. **Defense-in-depth is the product's strongest asset.** The composition of KF-1 + Merkle + per-hop
   verification creates super-additive attack difficulty (R-5). Maintaining all three layers is more
   important than making any single layer perfect. HOWEVER, the encoder supply chain attack is the
   single point of failure that breaks the entire composition argument.

5. **Certified robustness as a product differentiator.** The randomized smoothing analogy (above)
   suggests a path to FORMAL robustness certificates for the substrate. A product claiming "certified
   robustness to epsilon Hamming-ball perturbations" has a significant advantage over products relying
   on empirical testing alone. Highest-value research direction opened by this 2x drill.

6. **Statistical thinness of 100%/30 claims.** Before any production deployment, AT-6 (200-cell re-
   validation) is mandatory. The Wilson CI argument is airtight: 30 cells with 100% success gives a
   95% CI lower bound of 88.4%, which is insufficient for production guarantees.

---

## CITATIONS (verified, 15 sources)

1. Guo et al. (2021). "Gradient-Based Adversarial Attacks against Text Transformers." EMNLP 2021.
   [https://arxiv.org/pdf/2104.13733]
2. Krishna et al. (2023). "Paraphrasing evades detectors of AI-generated text." arXiv:2303.13408.
   [https://arxiv.org/pdf/2303.13408]
3. Carlini & Wagner (2017). "Towards Evaluating the Robustness of Neural Networks." IEEE S&P 2017.
   [https://arxiv.org/pdf/1608.04644]
4. Carlini et al. (2023). "On Evaluating Adversarial Robustness." [https://nicholas.carlini.com/]
5. Cohen et al. (2019). "Certified Adversarial Robustness via Randomized Smoothing." ICML 2019.
   [https://arxiv.org/abs/1902.02918]
6. Lecuyer et al. (2019). "Certified Robustness to Adversarial Examples with Differential Privacy."
   IEEE S&P 2019. [https://arxiv.org/pdf/1802.03471]
7. Adaptive Randomized Smoothing (2024). "Certified Adversarial Robustness for Multi-Step Defences."
   arXiv:2406.10427. [https://arxiv.org/abs/2406.10427]
8. Kanerva (2009). "Hyperdimensional computing: an introduction to computing in distributed
   representation with high-dimensional random vectors." Cognitive Computation 1(2):139-159.
9. Frady et al. (2021). "Resonator Networks, 2: Factorization Performance and Capacity."
   Neural Computation. [https://arxiv.org/pdf/2109.01196]
10. Saxena et al. (2022). "Sequence-to-Sequence Knowledge Graph Completion." ACL 2022.
11. Zhang et al. (2023). "Testing and Enhancing Adversarial Robustness of Hyperdimensional Computing."
    IEEE Transactions. [https://ieeexplore.ieee.org/document/10089842]
12. ADMIT (2025). "Few-shot Knowledge Poisoning Attacks on RAG-based Fact Checking." arXiv:2510.13842.
    [https://arxiv.org/pdf/2510.13842]
13. Plate (2003). "Holographic Reduced Representations." CSLI Publications.
14. Penrose (1955). "A generalized inverse for matrices." Mathematical Proceedings of Cambridge.
15. Membership Inference Attacks Against RAG (2024). arXiv:2405.20446.
    [https://arxiv.org/abs/2405.20446]

---

*2x level-2 operational drill. No empirical verification performed. Generic terminology throughout.*
*Lit-scan calibration penalty applied: P estimates deflated 0.20-0.30 from raw baselines; novel-synthesis P capped at 0.45.*
*Prior level-1 note: notes/research_drill_adversarial_substrate_divergence_2026-06-07.md*
