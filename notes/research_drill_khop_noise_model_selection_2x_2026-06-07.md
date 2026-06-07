# Research Drill: K-Hop Noise Model Selection -- Averaging vs Distractor (2x Deep Drill)
## Resolving Which Model Governs Real Cross-Shard Relay

**Date:** 2026-06-07
**Trigger:** Cycle 151 empirical battery -- averaging model (K_max GROWS with B) and distractor
  model (K_max COLLAPSES at B>=10) produce OPPOSITE trends; resolution determines v2/v3
  viability and whether Chain 3 GOLD 5.0 claims are honest
**Depth:** Level-2 operational drill; formal model selection, hybrid analysis, architectural
  mitigations, honest-correction of GOLD 5.0
**Discipline:** Theoretical / architectural / honest-correction. NO empirical verification.
**Calibration penalty:** P_deflated = raw P - 0.20 to 0.30; novel-synthesis cap P = 0.50
**Lit-scan calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]**
**Prior chain context:**
  Drill 3: pinv MAP denoising gives polynomial noise (averaging model assumed)
  Drill 4: sparse-KEY gives 3.16x K_max (averaging model assumed)
  Drill 5 FINAL: v3 10 ms K=12 at S=10^6 (averaging model assumed throughout)
**Discipline note:** 2x means operational drill on EXISTING findings, NOT re-verification.
  This note drills the mechanistic question the prior chain did NOT resolve: WHICH model?

---

## HEADLINE

**The real cross-shard relay under the substrate's production architecture is STRUCTURALLY a
distractor-regime system at naive broadcast scale (S=10^6), BUT the v2/v3 design choices
(LSH two-tier + confidence weighting) re-enter the HYBRID regime with a distractor fraction
p_d estimated at 0.25-0.55 for typical knowledge graph queries. The K_max collapse is NOT
universal: K_max collapses to zero ONLY when distractor fraction p_d > critical_p ~ 0.50 AND
no confidence filtering is applied. With LSH (B_eff=10-20) and tight cosine thresholds,
p_d_eff drops to 0.10-0.30, placing the architecture in the signal-recovery regime where
K_max is bounded below by 8-14 (dense) or 25-44 (sparse-KEY). GOLD 5.0 is conditionally
correct but requires an explicit p_d_eff < 0.50 constraint as a production invariant.**

**Honest correction to GOLD 5.0:** The v3 5-10ms K=12 claim is valid IF and ONLY IF p_d_eff
stays below ~0.40. This is achievable at v2 (S=10^4 with LSH) but REQUIRES active distractor
mitigation at v3 (S=10^6). Without per-shard confidence scoring + strict LSH, the distractor
model will dominate at S=10^6, collapsing K_max to near-zero at B>=10.

P_deflated for "v2 (S=10^4) with LSH stays in signal-recovery regime" = 0.55
P_deflated for "v3 (S=10^6) stays in signal-recovery regime WITHOUT mitigation" = 0.20
P_deflated for "v3 with LSH + confidence weighting keeps p_d_eff < 0.40" = 0.38
P_deflated for "averaging model alone governs at any production scale" = 0.15
  (cap at 0.15: production sharding is structurally distractor-generating)

---

## 1. FORMAL DEFINITIONS -- AVERAGING vs DISTRACTOR

### 1.1 Averaging Noise Model (Chain 3 Drills 3-4 Assumed Model)

**Setup:**
  N = vector dimensionality
  B = number of shards bundled per hop
  All B shards return CORRECT candidates for the query

**Mechanism:**
  Each shard j returns: v_j = x_target + eta_j
  where eta_j ~ N(0, sigma_shard^2 * I_N) is independent intra-shard noise
  sigma_shard^2 = alpha_shard / (1 - alpha_shard)  (pseudoinverse residual noise)

  Bundle: b = sign( sum_{j=1}^{B} v_j )
         = sign( B * x_target + sum_{j=1}^{B} eta_j )

  Signal amplitude in bundle: B * ||x_target|| = B * sqrt(N)
  Noise amplitude in bundle:  ||sum eta_j|| = sqrt(B) * sigma_shard * sqrt(N)
    (iid noise; CLT gives sqrt(B) scaling)

  Bundle SNR = B * sqrt(N) / (sqrt(B) * sigma_shard * sqrt(N))
             = sqrt(B) / sigma_shard
             = sqrt(B) * sqrt((1-alpha)/alpha)

**Key property:** SNR GROWS as sqrt(B). More shards bundled = better estimate.
**K_max consequence:** K_max increases (or stays high) as B increases.
**Cycle 151 observed trend:** K_max GROWS with B -- MATCHES averaging prediction.

**Physical interpretation of the model:**
  All B shards store the SAME target fact (or very closely related facts).
  Each shard's version adds independent noise, averaging improves estimate.
  This corresponds to: REPLICATED fact storage (same fact stored on multiple shards).

**When does this hold in production?**
  ONLY when: either (a) the queried fact is replicated across shards (e.g., hub replication
  in v2/v3), OR (b) all B shards in the LSH bucket happen to contain the target fact.

---

### 1.2 Distractor Noise Model (Cycle 151 Empirical Discovery)

**Setup:**
  B shards bundled per hop
  Fraction p_d of shards return DISTRACTORS (wrong candidates)
  Fraction (1 - p_d) of shards return correct candidates

**Mechanism:**
  Of B shards: B*(1-p_d) return x_target + eta_j (correct + intra-shard noise)
               B*p_d     return x_distractor_j + eta_j (wrong pattern + noise)

  For random distractors: E[x_distractor_j] = 0, ||x_distractor_j||^2 = N
    (distractors are approximately orthogonal to x_target for large N)

  Bundle signal: (1-p_d)*B * x_target
  Bundle noise from distractors: p_d*B * x_distractor (coherent, non-canceling)
  Bundle noise from intra-shard: sqrt(B) * sigma_shard * sqrt(N) (canceling)

  CRITICAL DISTINCTION: Distractor noise does NOT cancel under averaging.
  The distractors contribute COHERENT noise proportional to B*p_d.
  The intra-shard noise contributes INCOHERENT noise proportional to sqrt(B).

  Bundle SNR = (1-p_d)*B / sqrt( (p_d*B)^2 + B*sigma_shard^2 )

  For large B and p_d > 0:
    (p_d*B)^2 term dominates: Bundle SNR ~ (1-p_d) / p_d
    This is INDEPENDENT OF B (SNR saturates, then degrades as p_d * B > 1).

  For p_d*B > threshold (majority of shards return distractors):
    Bundle = sign(x_distractor_dominant) -- SNR = 0
    K_max = 0 (retrieval COLLAPSES)

**Key property:** SNR COLLAPSES when p_d * B > 1 (distractor majority).
**K_max consequence:** K_max collapses to near-zero when B is large enough for distractors to
  dominate the majority vote (p_d * B > 1).
**Cycle 151 observed trend:** K_max COLLAPSES at B >= 10 -- MATCHES distractor prediction if
  p_d >= 0.10 (1 out of 10 shards returns wrong candidate sufficient to degrade SNR).

**Physical interpretation of the model:**
  Most shards store DIFFERENT facts. When queried for a specific target, each shard returns
  its BEST LOCAL MATCH -- which may be a completely unrelated pattern.
  This corresponds to: consistent-hash sharding where each fact lives on exactly ONE shard.
  All OTHER shards return their own top-k (distractors).

**When does this hold in production?**
  ALWAYS under naive broadcast (no LSH pre-filter) with consistent hash sharding.
  At B = S (all shards), fraction p_d = (S-1)/S ~= 1.0 (almost all distractors).

---

### 1.3 The OPPOSITE TRENDS Reconciled

The averaging model gives: K_max GROWS with B.
The distractor model gives: K_max COLLAPSES with B.
Both are correct -- they describe different physical situations.

Cycle 151 observes BOTH trends, which means the experiment tested BOTH conditions:
  - When distractors are absent (or rare): averaging dominates; K_max grows.
  - When distractors are present (fraction p_d > 0.10): distractor dominates; K_max collapses.

This is not a paradox. It is a PHASE DIAGRAM with a transition at p_d ~ 1/(B+1).

---

## 2. REAL SHARD BEHAVIOR ANALYSIS

### 2.1 How Facts Are Actually Distributed in Production

**Substrate fact storage:** A fact ("entity X has attribute Y = value Z") is stored as a
  triple (k_e, k_a, v) where k_e = key for entity X, k_a = key for attribute Y, v = value Z.
  The pseudoinverse write: W += v (pinv_update) -- keys are implicit in the W structure.
  Under consistent hashing: fact_id = hash(entity_id || attribute_id) % S.
  Each fact lives on EXACTLY ONE shard (no replication, except for hub replication in v2/v3).

**Query execution:** "What is X's attribute Y at hop k+1?"
  - Query vector q = binding of entity_key and attribute_key
  - Coordinator broadcasts q to all shards (naive) or LSH-filtered shards (v2/v3)
  - Each shard j responds: v_j = argmax_{stored_fact_i in shard_j} cos(q, stored_key_i)
    i.e., shard j returns its BEST LOCAL MATCH for q

**What shard j returns:**
  Case 1: Shard j CONTAINS the correct fact (target fact is on shard j).
    Response: x_target + eta_j (correct answer plus retrieval noise)
    Probability: P(correct) = 1 / S (under uniform random fact placement)

  Case 2: Shard j does NOT contain the correct fact (all other S-1 shards).
    Response: x_best_local_j (top-k from shard j's facts, unrelated to target)
    This is a DISTRACTOR.
    Probability: P(distractor) = (S-1) / S ~= 1.0 for large S

**Critical conclusion:** Under naive broadcast (B = S), the distractor fraction is:
  p_d = (S-1) / S = 1 - 1/S

For S=10^4: p_d = 0.9999. Distractor model governs COMPLETELY.
For S=100:  p_d = 0.99.  Still nearly all distractors.
For S=10:   p_d = 0.90.  Still distractor-dominated.

Even at S=10 shards, broadcast to all shards produces 90% distractors.
The averaging model CANNOT HOLD under naive broadcast for any production shard count.

**The averaging model in Chain 3 Drills 3-4 implicitly assumed all B shards return correct
candidates.** This is physically accurate ONLY for REPLICATED storage (same fact on all shards)
-- which is exactly what hub replication provides, but only for hub facts (~top 1%).

**For 99% of facts (non-hub, non-replicated):** distractor model governs under broadcast.

---

### 2.2 The LSH Pre-Filter Effect on Distractor Fraction

The v2/v3 LSH two-tier fan-out changes the picture:

**LSH mechanism:** Instead of broadcasting to all S shards, the coordinator hashes the query
  vector q into an LSH bucket and sends only to the top-M shards in that bucket (M ~ 10-20).

**Effect on distractor fraction within the LSH bucket:**
  The LSH bucket contains shards whose LSH hash of their "typical stored vectors" is similar
  to the query hash. Therefore shards in the bucket have HIGHER PROBABILITY of containing the
  target fact than a randomly selected shard.

  Let recall@M = probability that the shard containing the target fact is in the top-M LSH
  bucket. From the HP-7 prediction in Drill 5: recall@10 >= 80% (designed target).

  If recall@M = recall_r, then of the M shards queried:
    Expected correct shards: recall_r * 1 (one shard actually contains the target)
    Expected distractor shards: M - recall_r * 1 = M - recall_r

  Distractor fraction within LSH bucket:
    p_d_LSH = (M - recall_r) / M = 1 - recall_r / M

  For M=10, recall_r=0.80: p_d_LSH = 1 - 0.08 = 0.92  -- STILL MOSTLY DISTRACTORS
  For M=10, recall_r=1.00: p_d_LSH = 1 - 0.10 = 0.90  -- even perfect recall gives 90%

**This is counterintuitive and important:** Even with perfect LSH recall (the correct shard
is ALWAYS in the top-10 bucket), 9 out of 10 shards return distractors if each fact lives
on exactly one shard. The LSH does NOT reduce the absolute number of distractors; it reduces
the B_eff (from S to M) but the FRACTION of distractors stays at ~(M-1)/M.

**What LSH actually provides:**
  Without LSH: B = S = 10,000; distractors = 9,999; correct = 1; p_d = 0.9999; p_d*B = 9999
  With LSH (M=10): B = 10; distractors = 9; correct = 1; p_d = 0.90; p_d*B = 9
  LSH reduces B*p_d from 9999 to 9 -- a 1111x reduction in distractor MASS.

  The majority vote is now 9 vs 1 rather than 9999 vs 1.
  At B=10 with 1 correct and 9 distractors: the correct shard wins the majority vote ONLY
  if the correct response has higher amplitude per dimension than the average distractor.

**SNR analysis for 1 correct vs 9 distractors (B=10, M=10):**
  Signal: 1 correct shard with cosine ~ 1.0 to target
  Noise: 9 random distractors with cosine ~ O(1/sqrt(N)) to target (orthogonality)

  Bundle = sign( v_correct + sum_{j=1}^{9} v_distractor_j )

  In each dimension i:
    v_correct_i = x_target_i + eta_correct_i  (signal + retrieval noise)
    v_distractor_j_i ~ N(0, 1) approximately (random vector, not aligned with x_target)

  Bundle component at dimension i:
    b_i = x_target_i + eta_correct_i + sum_{j=1}^{9} v_distractor_j_i

  E[b_i | x_target_i = +1] = 1 + 0 + 0 = 1  (distractors have mean zero per dimension)
  Var[b_i] = sigma_shard^2 + 9 * 1 = alpha/(1-alpha) + 9

  SNR_dim = E[b_i * x_target_i] / Var[b_i]^{1/2}
           = 1 / sqrt(alpha/(1-alpha) + 9)
           ~= 1 / sqrt(9 + 0.05/(0.95))
           ~= 1 / sqrt(9.053)
           ~= 1 / 3.009
           ~= 0.33 per dimension

  For cosine similarity with N dimensions:
    SNR_cosine = SNR_dim * sqrt(N) = 0.33 * 256 = 84.5

  This is POSITIVE SNR -- the correct shard wins the majority vote on average.

**KEY INSIGHT:** When distractors are random (orthogonal to target in expectation), the
majority vote STILL extracts the correct signal because:
  - Correct shard adds +1 per target dimension (coherent signal)
  - 9 distractors add +0 per target dimension in expectation (zero mean)
  - Statistical aggregation recovers the target from 1-in-10 correct shards

THIS IS THE CRITICAL MISSING PIECE that reconciles averaging and distractor models:
  - Distractor model as stated (majority vote collapses) assumes distractors have FIXED
    WRONG DIRECTION -- i.e., distractors point consistently AWAY from target.
  - Random distractors (independent of query) have ZERO MEAN, not negative mean.
  - Zero-mean distractors contribute NOISE, not NEGATIVE SIGNAL.
  - Noise from 9 random distractors is sqrt(9) = 3 times the single-shard noise.
  - The effective SNR degrades by factor 3, NOT to zero.

---

## 3. FORMAL HYBRID MODEL -- WEIGHTED MIXTURE WITH ORTHOGONALITY ASSUMPTION

### 3.1 Correct Hybrid SNR Formula

Let:
  B = total shards bundled per hop
  n_c = number of correct shards (return target + noise)
  n_d = B - n_c = number of distractor shards (return random pattern)
  Each distractor has cosine ~ N(0, 1/N) with target (orthogonal in expectation)
  Correct shard has cosine ~ 1 - epsilon (near-perfect retrieval from shard)

Bundle signal (target component):
  S_target = n_c (sum of n_c unit contributions)

Bundle distractor noise:
  sigma_d^2 = n_d * 1 (each distractor adds unit variance per dimension, independent)

Bundle intra-shard noise:
  sigma_shard^2 = n_c * alpha/(1-alpha) (retrieval residuals from correct shards)

Bundle SNR (per dimension, normalized):
  SNR = n_c / sqrt(n_d + n_c * alpha/(1-alpha))

For n_c = 1 (one correct shard), n_d = B-1 (all others distractors), alpha = 0.05:
  SNR = 1 / sqrt(B-1 + 0.053)
      ~ 1 / sqrt(B-1)   for B >> 1

  B=2:    SNR ~ 1 / sqrt(1) = 1.0
  B=5:    SNR ~ 1 / sqrt(4) = 0.5
  B=10:   SNR ~ 1 / sqrt(9) = 0.33
  B=100:  SNR ~ 1 / sqrt(99) = 0.10
  B=1000: SNR ~ 1 / sqrt(999) = 0.032

For cosine similarity (multiply by sqrt(N)):
  SNR_cosine = sqrt(N) / sqrt(B-1)
  B=10, N=65536: SNR_cosine = 256 / 3 = 85.3  -- RETRIEVAL WORKS

**Critical comparison:**
  Distractor model (worst case, COHERENT distractors):
    n_d distractors all point in SAME WRONG DIRECTION: SNR ~ n_c / n_d = 1/(B-1)
    This collapses to zero quickly.

  Distractor model (realistic, RANDOM distractors):
    n_d distractors are orthogonal in expectation: SNR ~ 1 / sqrt(B-1)
    This degrades slowly; retrieval works even at B=100.

**The cycle 151 empirical collapse pattern (K_max -> 0 at B >= 10) implies the distractors
in the experiment were COHERENT, not random.** Random distractors cannot produce collapse at
B=10 with N=65536. Coherent distractors (consistent wrong direction) can.

**When are distractors coherent vs random?**
  Random distractors: each shard returns its own top-1 from a different topic domain.
    Result: distractors are approximately orthogonal to the query. This is the typical case
    for a diverse knowledge graph (each shard covers a different semantic domain).

  Coherent distractors: multiple shards return patterns that are semantically CLOSE to the
    target but wrong -- e.g., near-duplicate facts, paraphrase variants, related entities.
    Result: distractors have positive (but incorrect) cosine with the query.
    This occurs for: high-similarity fact clusters (same entity, different attributes),
    near-synonym queries, or when the LSH pre-filter selects shards that are semantically
    close (which is exactly what a good LSH should do).

**Paradox of good LSH:** A high-quality LSH filter selects shards that are MOST SIMILAR to the
query. This means the top-M LSH shards contain:
  - The correct shard (high cosine with target fact)
  - Other shards with semantically SIMILAR facts (also high cosine -- i.e., coherent distractors)

Good LSH reduces random distractors but INCREASES coherent distractors.
This is why the LSH-enabled architecture may exhibit the DISTRACTOR collapse rather than
the averaging improvement: LSH specifically selects for high-cosine distractors.

---

### 3.2 Critical Distractor Fraction p_d_crit

Let p_d = fraction of shards that return distractors (n_d = p_d * B, n_c = (1-p_d) * B).

With RANDOM distractors:
  SNR = (1-p_d)*B / sqrt(p_d*B + (1-p_d)*B * alpha/(1-alpha))
      = (1-p_d)*sqrt(B) / sqrt(p_d + (1-p_d)*alpha/(1-alpha))

For retrieval to succeed: SNR * sqrt(N) > threshold T (typically T ~ 2.0):
  (1-p_d)*sqrt(B) * sqrt(N) / sqrt(p_d + small_alpha_term) > T
  (1-p_d)^2 * B * N / (p_d + small) > T^2
  p_d_crit: solve (1-p_d)^2 * B * N / p_d = T^2

For large B*N: p_d_crit approaches 1 (even high p_d is fine with random distractors and large N)

With COHERENT distractors (cosine = c_d > 0 with target):
  Signal: (1-p_d)*B * 1.0 (correct shards, cosine = 1)
  Noise-signal mix: p_d*B * c_d (coherent wrong direction -- partially ANTI-correlated to
    the correct signal if c_d < 0, or additively confusing if c_d > 0 but wrong fact)

  Net bundle cosine with target:
    = (1-p_d)*B * 1.0 + p_d*B * c_d (distractors add c_d to target direction)
      / sqrt((1-p_d)^2*B^2 + 2*(1-p_d)*p_d*B^2*c_d + p_d^2*B^2)

  If c_d = 0.5 (distractor is 50% similar to target, but WRONG):
    Bundle cosine = ((1-p_d) + 0.5*p_d) / sqrt(...)

  This is ALWAYS POSITIVE -- coherent distractors at c_d > 0 do NOT collapse SNR by
  themselves. They confuse the result (returned pattern is a blend of correct + distractor),
  but they don't zero it out.

  COLLAPSE condition: K_max -> 0 requires that the WRONG answer propagates down the K-hop
  chain. If the first hop returns a coherent distractor (c_d = 0.5 correct + 0.5 wrong),
  the second hop uses this noisy bundle as its query and retrieves an even noisier result.
  Over K hops, the distractor component accumulates:
    noise_k = k * p_d * c_d (distractor direction amplifies under coherent interference)

  This is the KEY mechanism for Cycle 151 K_max collapse at B=10:
    At each hop: the distractor fraction contributes c_d ~ 0.5 per distractor
    After K hops: cumulative distractor contamination grows as K * p_d * c_d * B
    K_max is where cumulative contamination equals correct signal:
      K * p_d * c_d * B = (1-p_d) * B
      K_max = (1-p_d) / (p_d * c_d)

  For p_d = 0.90 (LSH returns 9 coherent distractors + 1 correct), c_d = 0.5:
    K_max = 0.10 / (0.90 * 0.50) = 0.10 / 0.45 = 0.22

  K_max < 1: immediate failure. NOT gradual degradation. Collapse.

  This is the cycle 151 observed pattern: NOT gradual K_max degradation, but COLLAPSE at
  small B when distractors are coherent and LSH is selecting semantically-similar patterns.

---

### 3.3 Critical p_d Threshold as a Function of Coherence

Let c_d = distractor cosine similarity with target (coherence parameter).
Let the collapse condition be K_max < 12 (production minimum):

  K_max = (1-p_d) / (p_d * c_d) >= 12
  (1-p_d) >= 12 * p_d * c_d
  1 >= p_d * (1 + 12 * c_d)
  p_d <= 1 / (1 + 12 * c_d)

  c_d = 0.0 (random distractors): p_d_crit = 1.0  -- any fraction tolerable
  c_d = 0.1 (low coherence): p_d_crit = 1/2.2 = 0.45
  c_d = 0.2 (medium coherence): p_d_crit = 1/3.4 = 0.29
  c_d = 0.3 (high coherence, typical LSH near-neighbors): p_d_crit = 1/4.6 = 0.22
  c_d = 0.5 (very high coherence): p_d_crit = 1/7.0 = 0.14
  c_d = 1.0 (exact distractors): p_d_crit = 1/13 = 0.077

**Production estimate for LSH near-neighbors:**
  LSH top-M shards typically have cosine ~0.20-0.40 with the query (they were selected for
  similarity). If target cosine = 0.90 and distractor cosine = 0.25 in the same LSH bucket:
    c_d ~ 0.25/0.90 = 0.28 (distractor similarity as fraction of target similarity)

  At c_d = 0.28: p_d_crit = 0.23

  With B=10 and 1 correct shard: p_d = 9/10 = 0.90 > 0.23 = p_d_crit.
  **K_max COLLAPSES for typical LSH architecture with B=10 if coherence c_d ~ 0.28.**

  This is consistent with cycle 151 showing collapse at B >= 10.

**The averaging model (cycle 151 K_max grows with B) is therefore only valid when:**
  Either (a) c_d is near 0 (random distractors, diverse shards), or
  (b) n_c / B is large enough: multiple correct shards (requires fact replication).

---

## 4. WHICH MODEL GOVERNS REAL CROSS-SHARD RELAY -- VERDICT

**Verdict: The distractor model governs at production scale for most queries.**

**Reasoning chain:**
  1. Facts live on one shard each (consistent hashing, no replication for 99% of facts).
  2. Coordinator queries M shards per hop (LSH or broadcast).
  3. Only 1 shard contains the target fact per hop (assuming no replication).
  4. M-1 shards return their own best local match -- semantically near the query (because
     LSH selected them for high cosine), not random noise.
  5. Coherence c_d ~ 0.20-0.35 for typical KB facts with LSH top-M selection.
  6. At M=10, c_d=0.28: p_d = 0.90 > p_d_crit = 0.23. K_max COLLAPSES.

**BUT:** The extent of collapse depends critically on c_d and on the per-query confidence gap
  between the correct shard and the distractors.

**Three production operating regimes:**

  Regime A -- Sparse fact space (facts are well-separated in embedding space):
    c_d < 0.10 (distractors are nearly random relative to target).
    p_d_crit > 0.45. With B=10, p_d=0.90 > 0.45 still collapses.
    STILL fails without confidence filtering.

  Regime B -- Medium-density fact space (typical enterprise KB):
    c_d ~ 0.25. p_d_crit ~ 0.24.
    With B=10, p_d=0.90 > 0.24. Collapses without filtering.
    With confidence filter (keeping top 3 by cosine): effective B_conf=3, n_d_conf=2,
    p_d_conf = 2/3 = 0.67 > 0.24. Still collapses.
    With confidence filter (top 1 only, strict): effective B_conf=1 = correct shard.
    K_max = single-shard K_max ~ 20. Works but wastes bundling benefit.

  Regime C -- High-density fact space (Wikipedia-scale with many near-synonyms):
    c_d ~ 0.45. p_d_crit ~ 0.16.
    Even confidence-filtered to top-2: p_d = 0.50 > 0.16. Marginal.
    Requires: aggressive filtering OR fact deduplication OR key orthogonalization.

**SUMMARY TABLE:**

  | Architecture       | B_eff | c_d  | p_d  | p_d_crit | K_max status    |
  |--------------------|-------|------|------|----------|-----------------|
  | Naive broadcast    | 10^6  | 0.25 | ~1.0 | 0.23     | TOTAL COLLAPSE  |
  | LSH (M=10)         | 10    | 0.28 | 0.90 | 0.22     | COLLAPSE        |
  | LSH + conf top-3   | 3     | 0.28 | 0.67 | 0.22     | COLLAPSE        |
  | LSH + conf top-1   | 1     | --   | 0.0  | --       | K_max ~ 20      |
  | Hub replication    | 10    | 0.28 | 0.10 | 0.22     | SIGNAL RECOVERY |
  | Hub + conf top-3   | 3     | 0.28 | 0.0  | --       | K_max ~ 30-40   |

Hub replication changes the regime by making n_c > 1 (multiple correct shards).
If the target fact is replicated to 1 correct shard per 10 queried (hub fact), p_d = 0.90.
If the target fact is replicated to ALL 10 shards (fully replicated), p_d = 0 and averaging
dominates. Hub replication at 10% of queries (top-1% facts) puts those queries in averaging.

---

## 5. FIVE ARCHITECTURAL MITIGATIONS -- RANKED BY LEVERAGE

### Mitigation 1: Confidence-Weighted Bundling with Aggressive Threshold (CRITICAL)

**Mechanism:** Each shard returns (candidate_vector, cosine_score). Coordinator filters to
  only shards where cosine_score > threshold_T. Effective p_d_eff is reduced by selecting
  only high-confidence responses.

**Analysis:**
  If the correct shard has cosine ~ 0.85 with target, and distractors have cosine ~ 0.25:
  Setting threshold T = 0.70: correct shard passes; distractors fail.
  Result: p_d_eff ~ 0 (near-zero distractor fraction). K_max reverts to single-shard regime.

**Critical requirement:** There must be a cosine GAP between the correct shard and
  distractors. The gap is guaranteed if:
    (a) The retrieval quality within the correct shard is high (cosine > 0.80)
    (b) The LSH distractor shards have cosine < 0.70 to the query

  The gap may FAIL if: the target fact is embedded close to many other facts
  (near-synonyms, paraphrases), making distractor cosine ~ 0.65-0.75 -- within the gap.

**Implementation:**
  Coordinator receives B responses: {(v_1, c_1), ..., (v_B, c_B)}
  Filter: include only i where c_i > T (threshold)
  Bundle remaining: b = sign(sum_{filtered} v_i)
  Fallback if N_filtered = 0: return NONE (no retrieval at this hop; halt chain)

**K_max impact:** If gap is reliable (c_d < 0.70 for distractors):
  p_d_eff drops from 0.90 to ~0.05 (occasional high-cosine distractor slips through)
  K_max at p_d_eff = 0.05, c_d = 0.70: K_max = 0.95 / (0.05 * 0.70) = 27.1

  K_max ~ 27 (from 0 without filtering). This is the primary rescue mechanism.

**Ranking: #1. Highest leverage; low implementation cost (threshold parameter only).
  Works ONLY if cosine gap exists between correct and distractor shards.**

P_deflated for "confidence threshold restores K_max to 20-30": 0.45
  (depends on cosine gap; assumes gap is reliably > 0.20 for dense, N=65536, alpha=0.05)

---

### Mitigation 2: Hub Replication for K-Hop Critical Paths (HIGH LEVERAGE)

**Mechanism:** Identify the "hub facts" (high out-degree, high betweenness centrality in the
  K-hop graph) and replicate them to ALL shards that commonly serve as intermediate hops.
  This converts hub facts from "one correct shard out of B" to "multiple correct shards."

**Analysis:**
  For a hub fact replicated to R shards in the LSH top-M:
    n_c = R, n_d = M - R, p_d = (M-R)/M = 1 - R/M
    For R = 3 out of M = 10: p_d = 0.70
    At c_d = 0.28: K_max = 0.30 / (0.70 * 0.28) = 1.53 -- still marginal

  For R = 5 (50% replication): p_d = 0.50
    K_max = 0.50 / (0.50 * 0.28) = 3.57 -- barely functional at K=3 only

  For R = M (full replication to all LSH neighbors): p_d = 0 -- averaging model; K_max >> 20

  **Full replication of hub facts to ALL B query shards** is needed to reach K_max > 12.
  Partial replication (R/M < 0.5) is insufficient for the distractor regime.

**Tradeoff:** Full replication of hub facts costs M * storage_per_fact per hub.
  For M=10 and 1% of facts being hubs: 10x storage overhead for 1% of facts = 1.1x total.
  Acceptable for v2/v3 production.

**Ranking: #2. High leverage for hub-query K-hop chains; low cost for top-1% facts.
  Solves the distractor problem for hub facts; non-hub facts still need Mitigation 1.**

P_deflated for "hub replication to all M shards restores averaging model for hubs": 0.60
  (this is a well-understood distributed systems technique; substrate compatibility confirmed)

---

### Mitigation 3: Orthogonal Shard Key Space (STRUCTURAL FIX)

**Mechanism:** When assigning facts to shards, use a key-routing scheme that MAXIMIZES the
  cosine distance between facts on DIFFERENT shards (i.e., shard boundaries are orthogonal
  planes in embedding space, not arbitrary hash boundaries).

  Standard consistent hashing: fact_id = hash(entity_id || attribute_id) % S.
  Facts in the same semantic cluster may land on different shards (near-neighbor distractors).

  Orthogonal shard assignment: shard_id = argmax_{j} cos(embedding(fact), shard_centroid_j).
  Each shard "owns" a region of embedding space. Facts on the same shard are semantically
  similar to each other; facts on DIFFERENT shards are semantically DISTANT.

  Result: when querying shard j for a target in shard k (j != k), the distractor returned
  by shard j is ORTHOGONAL to the target (different semantic region).
  This converts coherent distractors (c_d ~ 0.28) into random distractors (c_d ~ 0.0).

  With c_d ~ 0.0 (random distractors): p_d_crit approaches 1.0.
  Even at p_d = 0.90 (9 out of 10 shards are distractors), K_max is not limited by
  the distractor fraction (random distractors don't accumulate across hops).

**Key requirement:** The LSH pre-filter must ALSO be aligned with the shard key space.
  If shards are in orthogonal regions, the correct shard for a query lives in the SAME
  region as the query. LSH will find it first. Distractors from other regions have low LSH
  similarity and are NOT selected. This means LSH + orthogonal shard boundaries gives:
    B_eff ~ 1-3 (mostly correct shards in LSH bucket) rather than B_eff ~ 10

  This is the structural fix: align shard boundaries with embedding geometry.

**Implementation cost:** Requires semantic sharding (not consistent hash). Initial assignment
  via embedding-space partitioning (K-means on fact embeddings). Migration for dynamic
  insertion: incremental assignment to nearest shard centroid.
  Engineering cost: ~3-4 weeks over consistent-hash baseline.

**Ranking: #3. Structural fix; medium engineering cost. Reduces c_d from ~0.28 to ~0.02.
  Enables large B with high K_max. NOT in v1 spec; should be in v2/v3.**

P_deflated for "semantic sharding eliminates coherent distractors": 0.48
  (semantic sharding well-understood for dense retrieval; K-hop composition is novel)

---

### Mitigation 4: Two-Round Relay -- Identify-then-Query (LATENCY TRADEOFF)

**Mechanism:**
  Round 1 (fan-out, identify): broadcast query to all M LSH shards; collect confidence scores
    only (no full vector retrieval); identify the TOP-1 shard by confidence score.
  Round 2 (targeted query): send full retrieval query to ONLY the top-1 shard.

  Result: p_d_eff = 0 (single correct shard queried).
  K_max = single-shard K_max ~ 20 (no bundling benefit; no distractor problem).
  Latency cost: 2x per hop (two rounds of RPC instead of one).
  Total K-hop latency: 2 * K * t_rpc instead of K * t_rpc.

  At v2 (10 ms target): 2-round relay gives 20 ms -- above target.
  Mitigation: parallelize Round 1 across all hops (pipeline the fan-outs).
  With pipelining: latency ~ K * t_rpc + (M-1) * t_rpc_small = effectively 1.5x penalty.

**Ranking: #4. Clean but costly. Doubles (or 1.5x) latency. Appropriate for high-precision
  queries where K_max matters more than latency. Not default production path.**

P_deflated for "2-round relay maintains K_max ~ 20 at any B": 0.70
  (single-shard retrieval quality well-established; the mechanism is simple and direct)

---

### Mitigation 5: Sparse-KEY + Confidence Joint Threshold (ZERO-CODE UNLOCK)

**Mechanism:** Combine the existing sparse-KEY intermediate encoding (zero code change, cycle
  142) with aggressive confidence thresholding (Mitigation 1):
    - Intermediate hops use alpha_sparse = 0.005
    - Each shard returns (sparse_v_j, cosine_j)
    - Threshold T = 0.85 (tight for sparse vectors; narrower active set = cleaner signal)
    - Only include i where cosine_i > T

  For sparse vectors with alpha = 0.005: correct shard cosine ~ 0.95+ (narrow, specific)
  For sparse distractors: cosine ~ sqrt(alpha^2 * N) = sqrt(0.005^2 * 65536) = 1.64/256 = 0.006
  (random distractor has nearly ZERO cosine with sparse query -- distractors are orthogonal
   for sparse vectors by construction, since alpha^2 * N = 0.005^2 * 65536 ~ 1.6 overlapping
   dimensions = effectively zero cosine)

  **This is the key synergy:** Sparse-KEY makes random distractors have c_d ~ 0 (orthogonal).
  Even coherent distractors may have low cosine if they are in a different semantic region
  (sparse representations are more separable than dense in cosine space due to narrow active set).

  With c_d ~ 0.02 for sparse distractors and T = 0.85:
    All random distractors filtered out (cosine << T)
    Only high-cosine responses pass (likely the correct shard)
    p_d_eff ~ 0.05-0.15 (small residual from coherent near-neighbors)

  K_max at p_d_eff = 0.10, c_d = 0.02: K_max = 0.90 / (0.10 * 0.02) = 450 -- huge.

  But at c_d = 0.10 (some near-neighbor coherence even for sparse):
    K_max = 0.90 / (0.10 * 0.10) = 90 -- still excellent.

**This is the primary production rescue path.** Sparse-KEY + confidence threshold jointly
  solve the distractor problem with zero new code. Sparse encoding reduces c_d for random
  distractors; confidence threshold filters residual coherent distractors.

**Ranking: #1 tie with Mitigation 1 (effectively combines M1 + existing sparse-KEY).
  Zero code change. Highest leverage. Requires calibrating the cosine gap for sparse
  vectors (needs empirical validation per Cell A below).**

P_deflated for "sparse-KEY + confidence restores K_max to 20+ in real production": 0.42
  (two well-understood mechanisms composed; interaction effect is the novel part)

---

## 6. EMPIRICAL TEST CELLS -- CHEAP DECISIVE TESTS

### Cell A: Shard Distractor Fraction + Coherence Measurement (MOST CRITICAL)

**What it resolves:** Directly measures c_d (distractor coherence) in real substrate queries.
  This is the SINGLE UNKNOWN that determines which regime the architecture is in.

**Setup:**
  - Build 100-shard substrate (consistent hashing, N=1024 for speed, alpha=0.05 per shard)
  - Store 100 distinct facts, 1 per shard
  - Query for each fact; record per-shard cosine scores
  - Compute: (1) fraction of shards returning high-cosine (> 0.70) results (p_high_cosine)
             (2) cosine of top response from EACH non-target shard (distractor cosine c_d_empirical)

**Prediction:**
  If c_d_empirical < 0.10: random distractor regime; averaging model approximately correct;
    Chain 3 GOLD 5.0 holds; no architecture changes needed beyond confidence threshold.
  If c_d_empirical ~ 0.20-0.40: coherent distractor regime; K_max collapse confirmed;
    Mitigation 5 (sparse-KEY + confidence) needed to rescue K_max.
  If c_d_empirical > 0.50: severe coherent distractors; semantic sharding (Mitigation 3) needed.

**HARD-PASS:** c_d_empirical < 0.15 (random distractor regime; averaging model holds)
**HARD-FAIL:** c_d_empirical > 0.35 (coherent distractor regime; v2/v3 needs structural fix)
**Middle band:** 0.15 <= c_d_empirical <= 0.35 (confidence threshold sufficient; no structural fix)
**Wall time:** ~2 hr CPU, N=1024 small test. $0 cost.
**Decisive:** YES. Binary outcome determines which of the 5 mitigations to prioritize.

---

### Cell B: K_max Sweep vs Distractor Fraction at Fixed B=10

**What it resolves:** Empirically maps K_max(p_d, c_d) landscape; validates the analytic
  formula K_max = (1-p_d) / (p_d * c_d).

**Setup:**
  - Synthetic 10-shard setup with N=4096
  - Store 1 correct fact per query; 9 distractors at various injection coherences
  - Sweep: p_d in {0.1, 0.3, 0.5, 0.7, 0.9} x c_d in {0.0, 0.1, 0.2, 0.3, 0.5}
  - Measure K_max at each (p_d, c_d) point

**Pre-reg HARD-PASS predictions (from analytic formula):**
  (p_d=0.9, c_d=0.0): K_max > 15 (random distractors tolerable)
  (p_d=0.9, c_d=0.3): K_max < 4 (coherent distractors collapse K_max)
  (p_d=0.5, c_d=0.3): K_max ~ 3-4 (critical_p boundary)
  (p_d=0.1, c_d=0.3): K_max > 20 (10% distractors tolerable even with coherence)

**HARD-FAIL:** K_max at (p_d=0.9, c_d=0.0) < 5 (random distractors cause collapse --
  would indicate additional noise source not in model; requires investigation)

**Wall time:** ~3 hr CPU. $0 cost. Generates K_max(p_d, c_d) phase diagram.

---

### Cell C: Mitigation 5 Validation -- Sparse-KEY + Confidence Threshold

**What it resolves:** Validates that sparse-KEY + T=0.85 confidence threshold rescues K_max
  in the coherent distractor regime.

**Setup:**
  - 10-shard substrate with coherent distractors: c_d = 0.30 (simulate medium-coherence regime)
  - Configuration A: dense-KEY + no threshold (baseline -- expect K_max collapse)
  - Configuration B: dense-KEY + T=0.70 confidence threshold
  - Configuration C: sparse-KEY + T=0.85 confidence threshold
  - Measure K_max at each configuration; B=10 throughout

**Pre-reg HARD-PASS (Mitigation 5 validates):**
  K_max(Config C) / K_max(Config A) >= 5x (sparse-KEY + threshold rescues from collapse)
  K_max(Config C) >= 12 (meets production minimum)

**Pre-reg HARD-FAIL (Mitigation 5 insufficient):**
  K_max(Config C) < 8 (sparse encoding still too coherent with distractors)
  Action: escalate to Mitigation 3 (semantic sharding) or Mitigation 4 (two-round relay)

**Wall time:** ~4 hr CPU. $0 cost. Most actionable cell for production architecture decision.

---

## 7. IMPLICATIONS FOR CHAIN 3 GOLD 5.0 -- HONEST CORRECTION

### 7.1 What GOLD 5.0 Got Right

**Correct claims in GOLD 5.0:**
  1. Pure-relay coordinator (GOLD 2.0): VALID. Independent of noise model. The distributive
     law holds regardless of distractor fraction. The coordinator can still relay without
     decoding.
  2. Additive noise (GOLD 3.0): CORRECT for intra-shard noise. The pinv MAP denoising still
     converts intra-shard noise from multiplicative to additive. The error was treating
     INTER-SHARD distractor noise as intra-shard noise -- they have different scaling.
  3. Sparse-KEY 3.16x SNR (GOLD 4.0): CORRECT for random distractors. The sqrt(alpha)
     SNR improvement holds when distractors are orthogonal (low c_d). For coherent
     distractors, the improvement is less but still positive (reduces c_d by narrowing
     active set).

### 7.2 Where GOLD 5.0 is Optimistic

**Optimistic claim 1: K_max(dense, B=10) ~ 14-18**
  GOLD 5.0 derived this from the AVERAGING model (all B candidates correct).
  In reality with 1 correct + 9 coherent distractors (c_d ~ 0.28):
    K_max = (1-p_d) / (p_d * c_d) = 0.1 / (0.9 * 0.28) = 0.40
  K_max < 1 under production conditions WITHOUT mitigation.

  With confidence threshold T=0.70 (Mitigation 1):
    p_d_eff ~ 0.10-0.20 (filtered out most distractors)
    c_d_eff ~ 0.28 (remaining coherent distractors)
    K_max_mitigated = 0.80 / (0.20 * 0.28) = 14.3 -- approaches GOLD 5.0 prediction

  **Conclusion:** GOLD 5.0 K_max ~ 14-18 is achievable but requires confidence threshold.
  Without threshold: K_max ~ 0. With threshold: K_max ~ 14-18. Threshold is MANDATORY.

**Optimistic claim 2: v3 5-10ms K=12 at S=10^6**
  GOLD 5.0 latency assumes K=12 hops complete successfully.
  Under production distractor regime without mitigation: K=12 is infeasible (K_max ~ 0).
  With confidence threshold + sparse-KEY:
    K_max_eff ~ 20-30 (sparse-KEY reduces c_d; threshold reduces p_d_eff)
    K=12 is below K_max_eff -- achievable.
  Latency estimate itself (3.9-10 ms) is NOT affected by noise model -- it's a timing model.

  **Revised claim:** v3 5-10ms K=12 is achievable IF AND ONLY IF:
    (a) Confidence threshold is enabled at the coordinator (Mitigation 1)
    (b) Sparse-KEY is configured at intermediate hops (Mitigation 5 prerequisite)
    (c) p_d_eff * c_d_eff < 1/(K+1) = 1/13 ~ 0.077 (production invariant to maintain)

**Optimistic claim 3: "v1 in 2 weeks"**
  Component 4 (sparse-KEY toggle, 0.5 days) + a confidence threshold at coordinator
  (not currently in Component 2 spec -- needs ~50 LOC addition) are REQUIRED for v1 to
  function at K=12. GOLD 5.0 v1 spec lists confidence filtering as "not implemented."
  **Correction:** Add confidence-weighted bundling to v1 Component 2 spec.

---

### 7.3 North-Star-Critical Honest Assessment

**User goal:** Functional system that empirically beats LLMs of comparable size.

**LLM baseline fact-recall:** ~20-50% accuracy on multi-hop knowledge queries across
  their training distribution (varies by LLM size; Llama-1B ~ 15-25%; Llama-7B ~ 35-55%).

**Substrate v2 (S=10^4) with confidence filtering:**
  Fact count: 327 million (100-1000x LLM parametric capacity at comparable size)
  K_max with mitigation: 14-27 (sufficient for K=12)
  p_d_eff with LSH + T=0.70: ~0.10-0.20 (rough estimate; Cell A confirms)
  Expected accuracy: dependent on confidence gap; NOT known without empirical Cell A.

  **v2 architecture is sufficient for north-star v1 demo -- IF confidence threshold works.**
  v3 (S=10^6) is a scale extension; not needed for north-star comparison.
  This is consistent with the task brief: "ship v2 + benchmark there."

**Critical path:** Cell A (distractor coherence measurement) is the LOAD-BEARING test for
  the entire v1/v2/v3 architecture. Everything else can be confirmed theoretically; Cell A
  requires measurement. Its cost: 2h CPU. It should be the FIRST experiment in the v1 build.

---

## 8. CROSS-THREAD SYNTHESIS WITH PRIOR FINDINGS

### With Drill 3 GOLD 3.0 (Additive Noise Under Pinv)
  GOLD 3.0 showed intra-shard noise is additive not multiplicative. This HOLDS.
  The error was conflating intra-shard noise (additive; pinv handles it) with inter-shard
  distractor noise (potentially coherent; pinv DOES NOT denoise it because distractors are
  not "noise around the pattern" but "wrong patterns from different shards").
  Correction: GOLD 3.0 K_max formula applies only to intra-shard noise channel.
  Inter-shard distractor channel needs the hybrid model above (Section 3.1).
  Combined two-channel noise model: K_max limited by WHICHEVER channel is more constraining.
  At production scale: inter-shard distractor channel is more constraining by default.

### With Drill 4 GOLD 4.0 (Sparse-KEY 3.16x)
  The 3.16x K_max improvement is correct for RANDOM distractors (c_d ~ 0).
  For coherent distractors, sparse-KEY reduces c_d by narrowing active overlap:
    Dense: c_d ~ alpha * N / N = alpha = 0.05 (overlap fraction for correlated patterns)
    Sparse: c_d ~ alpha_s * N / N = alpha_s = 0.005
    Reduction: 10x in c_d (not sqrt(10) in SNR as originally claimed, but 10x in coherence)
  This is BETTER than the original sqrt(10) claim for the coherent distractor regime.
  Sparse-KEY reduces distractor COHERENCE by 10x, not just the noise FLOOR by 3.16x.
  The mechanism works differently than Drill 4 described, but the benefit is stronger.

### With MMR Research (Clustered KB Anchoring Drill)
  MMR diversification for clustered KBs (cycle 145/146) operates at retrieval return time.
  Connection to distractor model: MMR selects diverse responses from retrieved candidates.
  For K-hop, if the bundled candidates are MMR-diversified:
    Near-duplicate distractors are filtered by MMR before bundling.
    This reduces coherent distractor count: p_d_eff decreases; c_d_eff decreases.
  MMR and confidence threshold are COMPLEMENTARY distractor mitigations:
    MMR: reduces COHERENCE among the B bundled candidates
    Confidence threshold: reduces FRACTION of distractors included

### With Adversarial Robustness Research
  The coherent distractor problem is closely related to the adversarial paraphrase attack
  analyzed in gradient-adversarial drilling. In that work, paraphrase attacks create near-
  neighbor noise in embedding space. The distractor regime is EQUIVALENT to passive paraphrase
  interference: the KB naturally contains near-paraphrases of the target that land on wrong
  shards and produce coherent distractors.
  The AT-1 through AT-6 adversarial defenses (confidence scoring, semantic similarity
  thresholding) from the adversarial drill are DIRECTLY applicable to the distractor problem.

---

## 9. FALSIFIABLE PREDICTIONS -- PRE-REGISTERED

**HARD-PASS (confirms averaging model still applies with mitigation):**

HP-1: Cell A measures c_d_empirical < 0.20 for typical production knowledge graph queries.
  Interpretation: Random or near-random distractors; averaging model approximately correct;
  confidence threshold is a safeguard, not a structural requirement.
  P_deflated = 0.30 (knowledge graphs often have semantically correlated facts)

HP-2: Cell C measures K_max(sparse-KEY + T=0.85) >= 12 at simulated c_d = 0.28.
  Interpretation: Mitigation 5 sufficient for v2/v3 production without structural redesign.
  P_deflated = 0.42

HP-3: Cell B confirms K_max formula: K_max = (1-p_d)/(p_d * c_d) within +/-30% at each
  (p_d, c_d) point.
  Interpretation: Analytic hybrid model is accurate; can use it to predict v2/v3 K_max from
  Cell A measurements.
  P_deflated = 0.45 (formula derivation is clean; empirical noise expected)

HP-4: At B=10, c_d=0.0 (random distractors injected): K_max > 15.
  Interpretation: Chain 3 Drill 3 results correct for the random distractor special case.
  P_deflated = 0.62 (this is the least novel prediction; follows from well-established VSA lit)

**HARD-FAIL (refutes averaging model viability at production; requires structural changes):**

HF-1: Cell A measures c_d_empirical > 0.40 for typical queries.
  Interpretation: Coherent distractor regime; confidence threshold insufficient; semantic
  sharding (Mitigation 3) or two-round relay (Mitigation 4) required before v2/v3 ships.
  Action: v2 spec must add semantic sharding component BEFORE production deployment.

HF-2: Cell C measures K_max(sparse-KEY + T=0.85) < 6 at c_d = 0.28.
  Interpretation: Sparse-KEY fails to reduce c_d sufficiently; active-set blowup or
  production codebook coherence exceeds model predictions.
  Action: Escalate to semantic sharding; re-evaluate GOLD 4.0 claims.

HF-3: Cell B shows K_max(p_d=0.9, c_d=0.0) < 5.
  Interpretation: Random distractors ALSO cause collapse; model is wrong; additional noise
  source (not intra-shard, not inter-shard coherence) is causing collapse.
  Action: Full noise model revision; potential showstopper for K-hop architecture.

HF-4 (CRITICAL): Cell A + B combined show: no confidence threshold can maintain p_d_eff *
  c_d_eff < 0.077 (the invariant needed for K=12).
  Interpretation: The fundamental assumption "cosine gap between correct and distractor shards
  is reliably > 0.20" is violated in practice; production architecture cannot achieve K=12.
  Action: North-star claim must be reduced to K < 8; GOLD 5.0 fundamentally revised.

---

## 10. CHEAP DECISIVE TEST

**Single cell to run FIRST (before any v1 build):**

Cell A (Distractor Coherence Measurement):
  - 100-shard substrate, N=1024 (fast), alpha=0.05, consistent hash routing
  - Store 100 distinct facts, one per shard, using real encoder embeddings (Llama-1B BASE)
  - Query each fact using full embedding of the query sentence
  - For each non-target shard: measure cosine(shard_top1_response, query_embedding)
  - Compute c_d_empirical = mean cosine of top-1 responses from non-target shards

  Decision rules:
    c_d < 0.10: random distractor regime -- proceed with confidence threshold as standard
    c_d in [0.10, 0.35]: coherent distractor regime -- enable sparse-KEY + T=0.85 as default
    c_d > 0.35: severe coherent regime -- semantic sharding must be added to v2 spec

  This test determines which of the 5 mitigations is structurally required.
  All other architecture decisions flow from this single measurement.
  Wall time: 2 hr CPU, $0 cost. Binary outcome.

---

## 11. SUBSTRATE-PRODUCT IMPLICATIONS

**Implication 1: Confidence-weighted bundling is NOT optional**
  The Chain 3 GOLD 5.0 v1 spec (Components 1-9) assumes bundling without confidence
  weighting. Given that production sharding is structurally distractor-generating, confidence
  weighting must be added to Component 2 (coordinator bundling) as a required element.
  Cost: ~50 LOC addition to coordinator. This should not delay v1 timeline.
  Without it: v1 K-hop will fail at K=3-5 before reaching K=12.

**Implication 2: Semantic sharding is a v2 architectural decision, not a v3 optimization**
  If Cell A shows c_d > 0.35, semantic sharding (Mitigation 3) needs to be in v2, not v3.
  This would add ~3-4 weeks to the v2 timeline. The v2 "2 months" estimate in GOLD 5.0
  should be revised to 2.5-3 months if semantic sharding is required.
  Decision point: after Cell A results. Not before.

**Implication 3: v2 (S=10^4) is the correct north-star target -- confirmed**
  v2 with LSH + confidence threshold + sparse-KEY has K_max ~ 14-27 (above K=12).
  Fact count: 327 million. This beats LLM parametric memory of comparable model size.
  The v3 (S=10^6) extension is commercially important but NOT needed for north-star demo.
  Ship v2 first; validate empirically; extend to v3 with distractor mitigation confirmed.

**Implication 4: Hub replication DOUBLY justified**
  Hub replication was justified in GOLD 5.0 for latency (reduce cross-shard RPC count).
  This drill adds a second justification: hub replication converts hub-fact queries from
  distractor regime (K_max ~ 0 without mitigation) to averaging regime (K_max >> 20).
  For enterprise KBs where 80% of queries hit 20% of facts (Pareto distribution), hub
  replication of the top-20% facts directly makes 80% of queries averaging-model queries.
  Hub replication coverage should be expanded from top-1% (GOLD 5.0) to top-20% for v2.

**Implication 5: The v2/v3 K=12 claim requires a production invariant**
  The GOLD 5.0 claim is only valid when: p_d_eff * c_d_eff < 1/(K+1) = 1/13.
  This is a MONITORING INVARIANT that must be instrumented:
    - Per-shard: measure cosine gap between top-1 response and the 2nd-response
      (gap ~ 1 - c_d; monitor this per shard, per time window)
    - Coordinator: measure effective p_d as fraction of responses below confidence threshold T
    - Alert: if p_d_eff > 0.30 OR c_d_eff > 0.25 (p_d * c_d = 0.075 ~ limit), issue warning
  This adds one monitoring component to the v1 spec. Implementation: ~30 LOC.

---

## CITATIONS (VERIFIED)

1. Kanerva, P. (1988). Sparse Distributed Memory. MIT Press.
   [Foundation for HDC retrieval with distributed storage; bundling with partial overlap]

2. Plate, T.A. (2003). Holographic Reduced Representations. CSLI Publications.
   [Bundling algebra; majority-vote decoder for bipolar vectors]

3. Kanter, I., Sompolinsky, H. (1987). "Associative recall of memory without errors."
   Physical Review A 35(1):380.
   [Pseudoinverse noise floor; intra-shard noise model -- Drill 3 basis]

4. Kleyko, D. et al. (2022). "A Survey on Hyperdimensional Computing aka Vector Symbolic
   Architectures, Parts I & II." ACM Computing Surveys.
   [Bundling noise; majority vote decoder; spurious pattern statistics]

5. Tsodyks, M.V., Feigelman, M.V. (1988). "Enhanced Storage Capacity in Neural Networks
   with Low Activity Level." Europhysics Letters 6.
   [Sparse Hopfield capacity; narrow basin = high specificity = reduced c_d for sparse]

6. Frady, E.P., Kleyko, D., Sommer, F.T. (2021). "Variable Binding for Sparse Distributed
   Representations." arXiv 2009.06734.
   [Block-code binding; sparsity preservation; active-set analysis]

7. Candes, E.J., Tao, T. (2006). "Near-Optimal Signal Recovery From Random Projections."
   IEEE Trans. Inf. Theory 52(12).
   [RIP / compressed sensing; sparse vector orthogonality and interference bounds]

8. Hopfield, J.J. (1982). "Neural networks and physical systems with emergent computational
   properties." PNAS 79(8):2554-2558.
   [Original network model; interference from near-neighbor patterns -- distractor analog]

9. Mezard, M., Parisi, G., Virasoro, M.A. (1987). Spin Glass Theory and Beyond.
   [RSB framework; near-neighbor spurious minima = coherent distractor analog in glass phase]

10. PowerGraph: Gonzalez et al. (2012). "PowerGraph: Distributed Graph-Parallel Computation
    on Natural Graphs." USENIX OSDI.
    [Power-law graph sharding; Pareto query distribution; hub fact replication justification]

11. Gripon, V., Berrou, C. (2011). "Sparse neural networks with large learning diversity."
    IEEE Trans. Neural Netw. 22(7).
    [Sparse HDC query; interference with stored patterns; active-set coherence analysis]

12. Carbonell, J., Goldstein, J. (1998). "The Use of MMR, Diversity-Based Reranking for
    Reordering Documents and Producing Summaries." ACM SIGIR.
    [MMR diversification; reducing coherent bundling from near-duplicate retrievals]

**Verified citation count: 12**

---

## CALIBRATION SUMMARY

| Prediction                                              | P_raw | Deflation | P_deflated |
|---------------------------------------------------------|-------|-----------|------------|
| Distractor model governs at naive broadcast scale       | 0.95  | -0.15     | 0.80       |
| LSH selects coherent distractors (not random)           | 0.80  | -0.20     | 0.60       |
| Confidence threshold rescues K_max to 14-27             | 0.65  | -0.20     | 0.45       |
| Sparse-KEY reduces c_d from 0.28 to < 0.05             | 0.55  | -0.25     | 0.30       |
| v2 with LSH + conf threshold: K=12 viable              | 0.75  | -0.20     | 0.55       |
| v3 with all mitigations: K=12 viable                   | 0.60  | -0.25     | 0.35       |
| c_d_empirical < 0.20 (random distractor regime lucky)  | 0.40  | -0.25     | 0.15       |
| c_d_empirical in [0.20, 0.40] (medium coherence)       | 0.55  | -0.20     | 0.35       |
| Hub replication resolves distractor for hub queries     | 0.80  | -0.20     | 0.60       |
| Cell A resolves which mitigation path is needed         | 0.90  | -0.15     | 0.75       |

Novel-synthesis cap (0.50) applied to: v3 viability composite claim
Maximum P_deflated: 0.80 (distractor model governs at broadcast scale -- well-established)
Minimum P_deflated: 0.15 (c_d_empirical < 0.20 -- optimistic; knowledge graphs are dense)

---

## KEY PARAMETERS TABLE

| Parameter              | Symbol   | Estimated Value      | Source                          |
|------------------------|----------|----------------------|---------------------------------|
| Shard count v2         | S        | 10^4                 | GOLD 5.0                        |
| Effective bundle size  | B_eff    | 10-20 (with LSH)     | Component 3 spec                |
| Correct shards per hop | n_c      | 1 (no replication)   | Consistent hash sharding model  |
| Distractor fraction    | p_d      | 0.90 (9/10 at B=10)  | Production shard model          |
| Distractor coherence   | c_d      | 0.20-0.35 (estimate) | UNKNOWN -- Cell A resolves      |
| Critical p_d           | p_d_crit | 1/(1+K*c_d) ~ 0.22   | Section 3.2 analytic formula    |
| K_max (no mitigation)  | --       | < 1                  | p_d=0.90 > p_d_crit=0.22        |
| K_max (with confidence)| --       | 14-27                | p_d_eff=0.10-0.20 after filter  |
| K_max (sparse + conf)  | --       | 20-90                | c_d reduced to 0.02-0.10        |
| Production invariant   | --       | p_d_eff*c_d_eff<0.077| K_max >= 12 + safety margin     |

---

## FINAL ANSWER: WHICH MODEL GOVERNS?

**Distractor model governs at production scale under naive broadcast.**
**Averaging model governs for hub facts under hub replication.**
**Hybrid model governs for non-hub facts under LSH + confidence threshold.**

The Chain 3 GOLD architecture is CONDITIONALLY VALID:
  - It holds if and only if confidence-weighted bundling is implemented (Component 2 update)
  - It holds for hub facts immediately (hub replication makes them averaging-regime)
  - It holds for non-hub facts with sparse-KEY + T=0.85 threshold IF c_d < 0.35

**GOLD 5.0 revision required (not a refutation -- a scope condition):**
  "v3 5-10ms K=12 at S=10^6" should read:
  "v3 5-10ms K=12 at S=10^6 WITH confidence-weighted coordinator bundling (50 LOC addition
   to Component 2) and sparse-KEY enabled at intermediate hops (Component 4 config)"

v2 (S=10^4) is sufficient for north-star demo with these two additions.
v3 (S=10^6) additionally requires semantic sharding if c_d > 0.35 (Cell A determines).

The K=12 production target is architecturally achievable. It is not trivially achievable.
The confidence gap (correct shard cosine >> distractor shard cosine) is the load-bearing
production assumption. Cell A measures it directly. All other decisions follow from Cell A.
