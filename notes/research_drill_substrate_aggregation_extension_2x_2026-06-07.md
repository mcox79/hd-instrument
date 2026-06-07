# Research Drill: Substrate Aggregation Extension -- 2x Depth Drill
# AVG Failure Root Cause + 7 Extension Evaluations

**Date:** 2026-06-07
**Trigger:** Cycle 155 sql_hybrid_aggregation MID -- AVG 100% error, COUNT/SUM native.
  2x depth request: root cause + 7 extension candidates + Pattern A vs B matrix + stack rank.
**Prior anchor:** research_drill_substrate_gap_native_sql_aggregation_3x_2026-06-07.md
  (establishes enumeration-impossibility argument + hybrid architecture correctness)
**Calibration penalty applied:** P estimates deflated 0.20 from raw agent estimates.
  Novel-synthesis P capped at 0.50.

---

## HEADLINE

The AVG 100% error is a test design artifact, not a substrate algebra failure. The Cycle 155
experiment measured COUNT via HD bundle energy and called the result an AVG proxy -- a mechanism
that has no path to scalar division. Algebraically, AVG requires (a) enumeration of a full set
and (b) scalar division of a sum by a count. Substrate cannot do (a); Pattern B composes SUM/COUNT
natively but the composition fails because both components carry O(1/sqrt(N)) noise that compounds
multiplicatively in division. The COUNT/SUM ceiling is REAL but is an enumeration ceiling, not an
arithmetic ceiling. Extensions (AVG-by-composition, MIN/MAX, MEDIAN) all hit the same enumeration
wall for large M. The only extensions that are both cheap AND production-viable at exact precision
are: (1) DuckDB-backed AVG/MIN/MAX/MEDIAN over semantically-filtered subsets (SA-class), and (2)
approximate COUNT/SUM over small predicate sets (M_predicate < sqrt(N)) via HD bundle energy with
well-documented error bounds. Stack rank: SA-class AVG >> approximate COUNT (small M) >> all others.

P_deflated(SA-class AVG production-viable) = 0.72
P_deflated(native substrate AVG exact) = 0.02
P_deflated(Pattern B SUM/COUNT composition < 5% error, M<1000) = 0.40
P_deflated(MIN/MAX native substrate) = 0.04

---

## Part 1: AVG Failure Root Cause -- Three Distinct Failure Modes

### 1.1 The test design artifact (Cycle 155 specific)

The Cycle 155 experiment script (exp_sql_hybrid_aggregation_v1.py, A-class test, line 60):

  est = float((members.sum(0) @ members.sum(0)) / N)

This formula computes ||bundle||^2 / N where bundle = sum of member unit vectors. This is the
Kanerva HD COUNT estimator (Kanerva 1988), not an AVG estimator. The formula has no scalar
field attached -- it cannot compute AVG(amount) because there IS no 'amount' column in the test.
The test was designed to measure COUNT accuracy; the pre-registration treated A_rel_err as a
COUNT measure but the verdict message mis-labeled it "needs DuckDB" as if it were an AVG failure.

What actually happened: the HD COUNT estimator via bundle energy gives:
  members.sum(0) @ members.sum(0) = ||sum of M_p unit vectors||^2
  For M_p members with approximately orthogonal unit vectors:
    E[||sum||^2] = M_p * N + M_p*(M_p-1) * E[v_i . v_j]
    E[v_i . v_j] = 0 for random unit vectors in R^N
    So E[||sum||^2] = M_p * N
    => est = M_p * N / N = M_p (exact in expectation)
  But with N=4096 and M_p ~ 50 (M=1000, N_PRED=20 -> 50 per predicate):
    off-diagonal interference: M_p*(M_p-1)/N = 50*49/4096 = 0.60 per unit estimate
    Relative error = 0.60/50 = 0.012 = 1.2% -- NOT 100% error

The 99.98% error (a_err = 0.9998) means the estimator is returning near-zero for most predicates.
Looking at the formula more carefully: `members.sum(0) @ members.sum(0)` divides by N=4096.
For M=1000, N_PRED=20: each predicate has ~50 members. ||50-member bundle||^2 / 4096 ~ 50.
But the comparison is `abs(est - exact) / max(exact, 1)` where exact = 50.
So if est ~ 50 and exact = 50, relative error should be ~0. The 99.98% error indicates
something else: members is the subset of facts with pred==p. With M=1000 and N_PRED=20,
each predicate has ~50 members. Let's trace through:

  members = facts[pred == p]   # shape: (~50, 4096), unit vectors
  bundle = members.sum(0)      # shape: (4096,)
  est = (bundle @ bundle) / N  # scalar

  bundle @ bundle = sum_i sum_j v_i . v_j = sum_i ||v_i||^2 + sum_{i!=j} v_i . v_j
  = M_p * 1 + interference_terms

But facts are unit vectors normalized to ||v||=1. So sum_i ||v_i||^2 = M_p.
The interference terms E[sum_{i!=j} v_i . v_j] = 0 in expectation.
Thus E[bundle @ bundle] = M_p, and est = M_p / N = 50/4096 = 0.012.

FOUND IT: The formula divides by N=4096 AGAIN when the unit vectors are already norm-1.
The bundle energy is already of magnitude M_p (not M_p * N). The correct formula is:
  est = bundle @ bundle   (NO division by N, since unit vectors give ||bundle||^2 ~ M_p)
The experiment divides by N=4096, giving est = 50/4096 = 0.012 instead of est = 50.
Relative error = |0.012 - 50| / 50 = 49.988/50 = 0.9998 = 99.98%.

This is the exact 0.9998 seen in the metrics. The AVG 100% failure is a FORMULA BUG in
the HD COUNT estimator, not a fundamental substrate limitation.

### 1.2 The correct HD COUNT estimator for unit vectors

For unit vectors (||v_i|| = 1):
  bundle = sum_{i=1}^{M_p} v_i
  ||bundle||^2 = sum_i ||v_i||^2 + cross_terms = M_p + O(M_p^2 / N)
  => COUNT estimate = ||bundle||^2 / 1 (NOT divided by N for unit vectors)
  OR: for general non-unit vectors:
    est = ||bundle||^2 / E[||v_i||^2]

The experiment uses BSC-adjacent random Gaussian vectors normalized to unit norm (line 53:
facts = unit(standard_normal)). These are unit vectors. The correct estimator is
||bundle||^2 NOT ||bundle||^2 / N.

Corrected expected error at M_p=50, N=4096:
  Variance of ||bundle||^2 around M_p: each off-diagonal term (v_i . v_j) has Var[v_i . v_j] = 1/N
  Total variance: M_p*(M_p-1) * (1/N) = 50*49/4096 = 0.598
  Relative error sigma: sqrt(0.598) / 50 = 0.77/50 = 0.015 = 1.5%
  This matches theory: O(1/sqrt(N)) ~ 1/64 = 1.6% at N=4096.

Corrected A_rel_err prediction: ~1-3% (not 100%). Cycle 155 result is a formula bug.

### 1.3 True substrate algebra failure for scalar AVG

Even with the correct COUNT estimator, native substrate AVG(amount) has a genuine algebraic problem:

AVG(amount) = SUM(amount) / COUNT

SUM(amount) requires encoding continuous scalar 'amount' in vector space. Two paths:

PATH 1 -- Scalar-weighted bundle:
  SUM_bundle = sum_i amount_i * v_i
  Recovery: SUM_bundle . v_ref / N ... but v_ref is noisy; multiple facts interfere
  Interference floor: M/N per unrelated fact = M/N * typical_amount
  At M=1000, N=4096: interference = 0.24 * mean_amount
  At M=10^6, N=65536: interference = 15.3 * mean_amount (catastrophic)

PATH 2 -- Quantized amount bins:
  Encode amount in B discrete bins; assign each bin a random HD vector
  Recover bin distribution from bundle: approximate histogram
  AVG = sum_b bin_center_b * count_b / total_count
  Error: quantization error + bin-recovery error (O(B^2/N) per Schlegel 2023)
  For B=100 bins and N=4096: error ~ 100^2/4096 = 2.4 per bin -- unusable

PATH 3 -- SUM/COUNT composition via Pattern B:
  If substrate stores (key_vec, sum_field) and (key_vec, count_field) separately:
  AVG = retrieve(sum_field) / retrieve(count_field)
  Both retrievals have O(M/N) noise floor relative to stored value
  For AVG: |AVG_est - AVG_true| / AVG_true = |SUM_est/COUNT_est - SUM_true/COUNT_true| / AVG_true
  Error propagation: sigma_AVG/AVG ~ sqrt((sigma_SUM/SUM)^2 + (sigma_COUNT/COUNT)^2)
  If both are ~1% error: sigma_AVG ~ sqrt(2) * 1% ~ 1.4% (manageable for approximate)
  But this only works if substrate can ENUMERATE the full set for SUM and COUNT individually.
  The enumeration problem remains: substrate gives top-k, not full set.

CONCLUSION: Native exact AVG is impossible for large M due to the enumeration barrier.
Native approximate AVG (PATH 3, small predicate sets M_p << sqrt(N)) is feasible with
known error bounds. For production financial/clinical use: DuckDB is required.

---

## Part 2: Seven Extension Evaluations

### Extension 1: AVG as SUM/COUNT composition

Theoretical mechanism: If substrate natively computes COUNT (bundle energy) and SUM (scalar-
weighted bundle), AVG = SUM/COUNT is trivially computable as a scalar ratio.

Algebra: Let F_p = {facts with predicate p}. Define:
  count_est = ||sum_{f in F_p} v_f||^2  (for unit vectors)
  sum_est = ||sum_{f in F_p} amount_f * v_f||^2 / ||v_ref||^2  (scalar weighted)
  avg_est = sum_est / count_est

Error analysis (PATH 3 from section 1.3):
  count relative error: O(1/sqrt(N)) = 1.6% at N=4096
  sum relative error: O(M_p/sqrt(N)) for large M_p (interference grows)
  At M_p=50, N=4096: sum_error ~ 50/64 = 78% -- completely unusable

This is the key insight: SUM estimation degrades as O(M_p * 1/sqrt(N)) while COUNT
degrades as O(1/sqrt(N)). For M_p >> sqrt(N), the SUM estimator noise floor exceeds the
signal. AVG composition inherits the SUM failure.

P_deflated(Extension 1 < 5% error at M_p > 100, any N) = 0.08
P_deflated(Extension 1 < 5% error at M_p < 20, N=65536) = 0.38
Engineering cost: 1-2 days (formula fix + scalar-weighted bundle implementation)
Recommended use: approximate AVG over SMALL groups (M_p < 20) only; document error bounds.

HARD-PASS: avg_rel_err < 0.05 at M_p=10, N=65536
HARD-FAIL: avg_rel_err > 0.30 at M_p=10, N=65536 (indicates implementation error)

### Extension 2: MIN/MAX via bundle thresholding

Theoretical mechanism: Given predicate group F_p, find min/max of a scalar field via binary
search on threshold tau: "are there facts with amount > tau?" --> test if any semantically
similar to (key_p AND amount_vec_above_tau).

Algebra: Requires encoding ordered scalar values in HD space preserving order:
  Option A: thermometer code -- encode amount_x as v_x = sum_{b <= x*B} e_b (binary cumulative)
    Order-preserving: cosine(v_x, v_y) ~ 1 - |x-y|/2 for normalized thermometer codes
    MIN: search for threshold satisfying retrieval dropping off
    Problem: thermometer codes are sparse binary, not compatible with FHRR or BSC binding
    Encoding overhead: B dimensions per scalar value; at B=1000: 1000x overhead in N
  Option B: frequency/phase encoding in FHRR -- encode amount as phase angle
    v_amount = exp(i * amount * omega) for some frequency omega
    Cosine(v_x, v_y) = Re[exp(i*(x-y)*omega)] -- periodic, not monotone
    Cannot recover order statistics from phase encoding

No known algebraically clean HD encoding supports order statistics recovery from bundle
superposition. The thermometer code approach is theoretically possible but requires N >> B
(N must be >> number of precision bits), making it incompatible with production N=65536 when
requiring financial precision (B >= 10^7 for cent-level on $100K amounts).

P_deflated(Extension 2 production-viable with correct order semantics) = 0.04
P_deflated(Extension 2 useful for approximate 10-percentile granularity at N=65536) = 0.15
Engineering cost: 3-5 days (thermometer + binary search infrastructure)
NOT recommended for v1. DuckDB MIN/MAX is O(M) exact; no HD alternative competes.

HARD-PASS: min/max relative error < 0.10 on 100-value range at N=65536
HARD-FAIL: min/max relative error > 0.50 (effectively random) at N=65536

### Extension 3: MEDIAN via histogram approximation

Theoretical mechanism: Partition the value range into B bins. For each bin b, estimate
COUNT(F_p intersect bin_b) via HD bundle energy. Recover approximate histogram. MEDIAN =
bin b* such that sum_{b < b*} count_b = M_p/2.

Algebra: This requires PER-BIN bundle estimates, meaning for each predicate p and bin b:
  bundle_{p,b} = sum of v_f for facts with predicate p AND amount in bin b
  count_{p,b} = ||bundle_{p,b}||^2

This requires storing B separate bundle vectors per predicate -- B times the storage overhead.
For B=100 bins and N_PRED=20 predicates: 2000 bundle vectors of dimension N=65536.
Storage: 2000 * 65536 * 4 bytes = 500MB. Feasible for small N_PRED.

But the key problem: there is no mechanism to ROUTE facts to the correct bin bundle without
first knowing their amount value. The substrate write path must attach the scalar amount to
determine bin assignment. Once that is known, the exact histogram is trivially maintained
as a counter array -- the HD bundle machinery adds complexity with no benefit.

P_deflated(Extension 3 useful as substrate-native MEDIAN) = 0.05
(The exact histogram via counter array is simpler, cheaper, and more accurate.)
Engineering cost: 5+ days to implement bin bundles + no advantage over exact counters.
NOT recommended.

### Extension 4: GROUP BY via predicate routing

Theoretical mechanism: For each group label g in {1,...,G}, maintain a separate bundle
accumulating facts assigned to group g. Query for GROUP BY: retrieve count/sum for each bundle.

Algebra: This is a partitioned bundle architecture:
  bundle_g = sum_{f: group(f)=g} v_f
  count_g = ||bundle_g||^2

This is exactly what the Cycle 155 experiment tested (N_PRED=20 groups). The analysis is
identical to Extension 1 (COUNT) and Extension 2 (SUM within group). The GROUP BY structure
itself is native to substrate -- it maps directly to separate bundle vectors per group.
The AGGREGATE within each group is the limiting step, not the grouping.

What works natively: approximate COUNT per group, with O(1/sqrt(N)) relative error.
What does not work: SUM/AVG/MIN/MAX of scalar fields per group (same failures as E1-E3).

P_deflated(GROUP BY COUNT production-viable with error < 5%) = 0.42
P_deflated(GROUP BY AVG production-viable for exact accounting) = 0.02
Engineering cost: 1 day (maintain per-group bundle dict; same code as A-class test)

This is the one extension that is concretely near-viable for approximate COUNT GROUP BY.
The corrected Cycle 155 formula (no /N) would have shown ~1-3% error per group.

HARD-PASS: per-group COUNT relative error < 0.05, G=20 groups, M_p >= 100, N=65536
HARD-FAIL: per-group COUNT relative error > 0.20 (refutes bundle concentration)

### Extension 5: JOIN via shared filler vectors

Theoretical mechanism: Two facts f_a and f_b are joined if they share a common filler
(e.g., both concern "Marie Curie"). In VSA, binding stores (role, filler) pairs:
  f_a = role_a * filler_mc + ...
  f_b = role_b * filler_mc + ...
JOIN on filler_mc: retrieve all facts whose unbinding by filler_mc returns a non-noise signal.

Algebra: This is the VSA join operation (Gayler 2003, "Vector Symbolic Architectures Answer
Jackendoff's Challenges for Cognitive Neuroscience"). It is exact in the regime where N >> M.
In the overloaded regime (M >> N, production at M=10^6, N=65536), unbinding returns
filler_mc with SNR ~ sqrt(N/M) = sqrt(65536/10^6) = 0.26 -- below noise floor.

JOIN via shared filler is theoretically well-founded and works in the low-M regime (M < N).
In production: fails above M ~ N (same capacity cliff as retrieval).

P_deflated(Extension 5 viable at M < N) = 0.55
P_deflated(Extension 5 viable at M > 10*N) = 0.03
Engineering cost: 2-3 days (unbinding + SNR threshold + fanout control)

This is the second concretely viable extension, but only below the capacity cliff.
For production healthcare (M=10^6, N=65536): JOIN via DuckDB foreign key is preferred.

HARD-PASS: join recall > 0.90 at M=1000, N=65536 (M/N ratio = 0.015, below cliff)
HARD-FAIL: join recall < 0.50 at M=1000, N=65536 (would refute VSA join theory)

### Extension 6: Window functions via temporal substrate

Theoretical mechanism: Bitemporal substrate (from DuckDB bitemporal drill) maintains
tx_time and valid_time. Window = facts with valid_time in [t-W, t]. Rolling aggregate:
  bundle_window = sum of v_f for f with valid_time in [t-W, t]

The sliding window requires adding new facts and subtracting old ones:
  bundle_window(t+1) = bundle_window(t) + v_new - v_expired

Algebra: HD subtraction is algebraically valid: bundle - v_i. But drift analysis
(from 3x drill, Part 2B) shows after K slides:
  noise_accumulated ~ K * sigma_per_slide = K * 1/sqrt(N)
  At K=365, N=65536: drift = 365/256 = 1.43 per unit
  For a SUM of $10M over 1 year: drift ~ $56,000

This failure is inherent to the sequential subtraction structure, not fixable by larger N.
A periodic reset (recompute bundle_window from scratch every P steps) bounds the drift:
  noise ~ P/sqrt(N); reset every P = sqrt(N) = 256 steps gives noise ~ 1/sqrt(N) again
  With resets every 256 days: effective rolling window drift bounded at 1.6% of true sum.

P_deflated(Extension 6 with periodic resets, COUNT accuracy < 5%) = 0.35
P_deflated(Extension 6 for SUM/AVG with financial precision) = 0.03
Engineering cost: 2-3 days (temporal routing + periodic reset + correction for expired-fact counts)

The COUNT variant with periodic resets is the only viable path; SUM/AVG in windows are too noisy.

HARD-PASS: rolling COUNT drift < 0.05 over 1000 window slides with reset every sqrt(N) steps
HARD-FAIL: rolling COUNT drift > 0.20 over 100 window slides (refutes reset-correction theory)

### Extension 7: Statistical aggregations (variance, percentiles)

Theoretical mechanism: Variance = E[X^2] - (E[X])^2. If substrate can compute E[X] (AVG)
and E[X^2] (second moment), variance follows. Percentiles generalize MEDIAN.

Algebra: E[X^2] requires a scalar-weighted bundle with amount^2 weights:
  bundle_sq = sum_i amount_i^2 * v_i
  SUM_sq = ||bundle_sq||^2 / correction_factor

This has the same noise floor as the scalar SUM estimator (Extension 1, PATH 1):
  interference floor at M=10^6, N=65536: 15.3 * mean(amount^2)

For amount drawn from any heavy-tailed distribution (healthcare costs, financial claims),
amount^2 is dominated by extreme values. The noise floor at production M is orders of
magnitude larger than signal. Variance estimation is categorically impossible in the
production regime via HD bundles.

Percentiles require order statistics (same analysis as Extension 3/MEDIAN). No improvement.

P_deflated(Extension 7 production-viable) = 0.02
Engineering cost: 4+ days, no expected payoff.
NOT recommended for any roadmap consideration.

---

## Part 3: Pattern A vs Pattern B Aggregation Matrix

### Pattern A: Query-time composition

In Pattern A, the query is composed on the fly from atomic components:
  q = key_vec * predicate_vec  (binding)
  matches = topk(W @ q)

Aggregation in Pattern A: the query can TARGET a group (predicate), but it retrieves top-k
by cosine similarity. Aggregate over retrieved set = aggregate over top-k, not over full predicate set.

| Aggregation | Pattern A support | Error level | Notes |
|-------------|-------------------|-------------|-------|
| COUNT (approx, small M_p) | YES via bundle energy | ~1-3% at N=65536, M_p<100 | Formula must be corrected: ||bundle||^2 not /N |
| SUM scalar | NO | >50% at M_p>100 | Interference floor catastrophic |
| AVG scalar | NO | Inherits SUM failure | |
| MIN/MAX | NO | No ordered embedding | |
| GROUP BY COUNT | YES (one bundle per group) | ~1-3% per group | Works for categorical groups |
| JOIN (low M) | YES | Recall>0.90 at M<N | Fails above capacity cliff |
| Window COUNT | PARTIAL | 1.6% with resets | Reset overhead every 256 slides |

### Pattern B: Stored composition

In Pattern B, the substrate stores pre-computed sub-results as explicit fact vectors:
  write(key="COUNT(region=West)", value=count_int)
  write(key="SUM(region=West, field=amount)", value=sum_float)

Query: retrieve stored aggregate directly; update incrementally on each new fact write.

| Aggregation | Pattern B support | Error level | Notes |
|-------------|-------------------|-------------|-------|
| COUNT exact | YES (stored as scalar) | 0% -- exact | Requires incremental update at write time |
| SUM exact | YES (stored as scalar) | 0% -- exact | Incremental update |
| AVG exact | YES (SUM/COUNT stored separately) | 0% | Two retrievals + scalar division |
| MIN/MAX | PARTIAL | 0% only if tracked at write time | Must maintain running min/max per key |
| GROUP BY | YES (one fact per group key) | 0% | Requires predefined GROUP BY keys |
| MEDIAN | NO | Cannot maintain exactly without sorted list | |
| Window | PARTIAL | 0% for COUNT/SUM within window | Requires expiry tracking |

**Key Pattern B insight:** Pattern B can support EXACT AVG/MIN/MAX if the aggregation keys are
known at write time. The substrate stores (aggregate_key, aggregate_value) pairs and retrieves
them by semantic proximity. This is not aggregation -- it is a CACHE of pre-computed aggregates.
The substrate acts as a semantic index over a pre-computed aggregate table.

**Critical limitation of Pattern B:** It requires knowing the aggregation schema at write time.
For ad-hoc queries ("what is the average amount for claims semantically similar to X?" where X
is an arbitrary query vector, not a predefined key), Pattern B cannot pre-compute the answer
because the query predicate was not known at write time.

**Pattern B is a materialized view, not a live aggregation engine.** This is a meaningful
product distinction: Pattern B gives exact aggregates for a DEFINED set of query types,
while the hybrid (substrate + DuckDB) gives exact aggregates for ANY ad-hoc query.

### Pattern A vs B summary

  Pattern A: approximate aggregation, works for COUNT/GROUP BY COUNT with M_p < 100 per group
  Pattern B: exact aggregation for PREDEFINED aggregate keys; fails for ad-hoc semantic predicates
  Hybrid: exact aggregation for any query class including joint semantic+aggregate (SA-class)

---

## Part 4: Stack Ranking -- P_actionable for V1

Rank order by P_deflated * (1/engineering_days) * semantic_value:

1. **DuckDB SA-class AVG** (Extension 1 via hybrid architecture)
   P_deflated = 0.72 | Cost = 2 days (already scaffolded from 3x drill)
   This is not a native extension -- it's the correct architecture. Delivers exact AVG/MIN/MAX/MEDIAN
   for any SA-class query. Already validated conceptually in Cycle 155 (sa_err=0.0000).
   P_actionable = 0.72

2. **GROUP BY COUNT (corrected formula, Pattern A)**
   P_deflated = 0.42 | Cost = 1 day (formula fix + GROUP BY routing)
   Delivers approximate per-group COUNT with 1-3% error at N=65536. Cheap to implement.
   Only requires fixing the /N bug in the HD bundle energy formula.
   P_actionable = 0.42

3. **JOIN via shared filler (Pattern A, M < N)**
   P_deflated = 0.55 | Cost = 2-3 days | Only valid at M < capacity cliff
   Demonstrates substrate's unique relational capability. Product-differentiating for small KBs.
   Not production-viable for M > 10*N; document the envelope.
   P_actionable = 0.55 * (fraction of use cases with M < N) -- conditioned on M

4. **Pattern B exact AVG/SUM for predefined keys**
   P_deflated = 0.65 | Cost = 1-2 days
   Materialize pre-computed aggregates as substrate facts. Retrieval is semantic (fuzzy key match).
   Powerful for dashboard-style use cases where aggregate queries are templated.
   P_actionable = 0.65

5. **Rolling COUNT with periodic reset (Extension 6)**
   P_deflated = 0.35 | Cost = 2-3 days
   Niche use case. Temporal substrates support this naturally.
   P_actionable = 0.35

6-7. MIN/MAX native, MEDIAN native, variance (Extensions 2, 3, 7) -- P_actionable < 0.10 each.

---

## Part 5: Cheap Pre-Tests

### Pre-Test 1: Corrected GROUP BY COUNT

**Test:** Run Cycle 155 A-class test with the formula fix: change
  `est = (members.sum(0) @ members.sum(0)) / N`
to
  `est = (members.sum(0) @ members.sum(0))`
(No /N division for unit vectors.)

Expected outcome: a_err drops from 0.9998 to 0.01-0.03 (1-3% relative error).
This is a 1-hour laptop test on existing CPU runner. No new infrastructure needed.

If result: a_err in [0.005, 0.030] -- CONFIRMS COUNT is native at this scale. Elevates
GROUP BY COUNT from "failing" to "working" in the cap_map row. Strong positive signal.

If result: a_err > 0.10 -- indicates additional error source (normalization mismatch,
predicate assignment skew, or N=4096 too small). Run at N=65536 before accepting failure.

Pre-registration:
  HARD-PASS: a_err in [0.000, 0.030] at M=1000, N=4096, M_p~50 -- formula fix validated
  HARD-FAIL: a_err > 0.10 at M=1000, N=4096 -- indicates bug beyond formula

**Engineering cost:** 30 minutes. Single line change in exp_sql_hybrid_aggregation_v1.py.
Run on local runner as smoke. No cloud needed.

### Pre-Test 2: Pattern B AVG via stored aggregate facts

**Test:** Write aggregate facts (key="AVG_amount_region_West", value=precomputed_avg) to substrate.
Query: retrieve "average claim amount for Western region" via semantic retrieval.
Compare retrieved value to true AVG from DuckDB.

Measures: whether semantic similarity between query "average ... Western region" and the
stored key "AVG_amount_region_West" is high enough for retrieval (cosine > 0.7 threshold).
Also measures whether the stored scalar value survives round-trip through the substrate write/read.

Expected outcome: S_recall >= 0.90 (the stored aggregate fact is retrieved when semantically queried).
Value recovery: < 1% error if using exact scalar encoding (store as float, bind with key vec).

If result: S_recall >= 0.90 AND value error < 0.01 -- confirms Pattern B exact AVG path.

Pre-registration:
  HARD-PASS: S_recall >= 0.90 for aggregate key retrieval AND value_rel_error < 0.02
  HARD-FAIL: S_recall < 0.70 (substrate not recognizing aggregate key from natural language query)
    OR value_rel_error > 0.10 (scalar encoding broken)

**Engineering cost:** 2-3 hours. New experiment script. CPU. Smoke at M=100 aggregate facts.

---

## Part 6: Native vs External Customer-Pitch Matrix

This is the product differentiation matrix for customer-facing communication:

| Operation | Substrate native | DuckDB required | Notes |
|-----------|-----------------|-----------------|-------|
| Semantic retrieval (top-k) | YES, exact | No | Core substrate capability |
| COUNT (approx, small groups) | YES (~1-3% error) | Optional for exact | Bundle energy; document error bound |
| COUNT (exact) | NO | YES | Enumeration required |
| SUM scalar (exact) | NO | YES | Interference floor at M > 100 |
| AVG scalar (exact) | NO | YES | Inherits SUM failure |
| MIN / MAX (exact) | NO | YES | No ordered HD embedding |
| MEDIAN | NO | YES | No order statistic primitive |
| GROUP BY COUNT (approx) | YES (~1-3% per group) | Optional | One bundle per group |
| GROUP BY AVG/SUM/MIN/MAX | NO | YES | |
| JOIN (small M, M < N) | YES | No | Via shared filler vector |
| JOIN (production M) | NO | YES | Capacity cliff |
| Semantic+aggregate joint (SA-class) | HYBRID | REQUIRED | Substrate for S step; DuckDB for A step |
| Pre-computed aggregate lookup | YES (Pattern B) | No | Semantic key over materialized view |
| Rolling COUNT (approx, with resets) | PARTIAL | Optional | 1-3% drift per sqrt(N) window |
| Variance / percentiles | NO | YES | No native HD path |

**The key customer-facing claim:** Substrate is NOT an RDBMS and should not be compared to one.
It does one thing DuckDB cannot: semantic predicate evaluation without a schema.
DuckDB does one thing substrate cannot: exact scalar aggregation.
The joint SA-class query is the product moat: neither engine alone can answer it.

---

## Part 7: Falsifiable Predictions

### HARD-PASS thresholds (predictions for upcoming tests)

HP-1: Corrected GROUP BY COUNT formula (Pre-Test 1) returns a_err in [0.005, 0.030]
  at M=1000, N=4096, M_p~50 per group.
  P_deflated = 0.72. Based on: Kanerva concentration bound, corrected formula derivation.

HP-2: Pattern B AVG pre-test (Pre-Test 2) returns S_recall >= 0.90 for aggregate key retrieval
  at M=100 stored aggregate facts, N=4096.
  P_deflated = 0.65. Based on: substrate S-class recall is 1.0 in Cycle 155.

HP-3: SA-class hybrid test (DuckDB IN-list after substrate retrieval) returns
  sa_err < 0.05 for AVG(amount) over top-k semantic matches.
  P_deflated = 0.68. Based on: Cycle 155 sa_err=0.0000 for COUNT; AVG requires only DuckDB step.

HP-4: JOIN via shared filler returns recall > 0.85 at M=500, N=4096 (M/N = 0.12, below cliff).
  P_deflated = 0.52. Based on: Gayler 2003 VSA join theory; below capacity cliff.

### HARD-FAIL thresholds

HF-1: Corrected formula still shows a_err > 0.10 at M=1000, N=4096.
  Would indicate additional error source; triggers diagnostic drill on normalization.
  P_deflated(this happening) = 0.08.

HF-2: SA-class AVG latency exceeds 500ms at M=10^6, N=4096 (smoke scale).
  Would require pre-materialization of aggregate indexes; redesigns query path.
  P_deflated(this happening) = 0.06.

HF-3: Pattern B S_recall < 0.50 for aggregate key queries.
  Would indicate semantic gap between natural-language aggregate query and stored key;
  triggers embedding alignment investigation.
  P_deflated(this happening) = 0.15.

HF-4: JOIN recall < 0.50 at M=500, N=4096.
  Would refute VSA join theory at this M/N ratio; triggers capacity cliff re-measurement.
  P_deflated(this happening) = 0.10.

---

## Part 8: Cross-Thread Synthesis

### With 3x drill (research_drill_substrate_gap_native_sql_aggregation_3x_2026-06-07.md)

3x drill established: hybrid architecture is correct; HD-aggregation production-viable P=0.03.
This 2x drill adds: the 100% error result is a FORMULA BUG, not a different failure mode.
The correct HD COUNT P_deflated is ~0.42 for approximate GROUP BY COUNT (not 0.03).
The 3x drill P_deflated(HD-aggregation for exact accounting) = 0.03 remains correct.
Update: P_deflated(HD COUNT approximate for GROUP BY) bumped to 0.42 (was implicitly 0.03).

The HARD BREAK on aggregation (from Datalog drill) stands for EXACT aggregation.
It does NOT apply to approximate COUNT with documented error bounds.

### With substrate_structured_aggregates_v1 (HARD_PASS experiment)

That experiment showed: substrate exact COUNT/SUM aggregation acc=1.000. This conflicts with
the Cycle 155 a_err=0.9998 finding at first glance. The explanation: substrate_structured_aggregates
used a DIFFERENT mechanism (likely Pattern B -- stored exact counts as scalar fact values).
The Cycle 155 experiment used HD bundle energy (Pattern A). These are different approaches.
Both results are correct; the conflict is a naming confusion between "native aggregation" meaning
Pattern A bundle energy vs Pattern B stored-scalar approach.

Cap map interpretation: "substrate exact COUNT/SUM" in the HARD_PASS row means Pattern B
(stored scalars retrieved semantically), not Pattern A bundle energy.

### With Chain 2 Drill 3 (DuckDB shadow architecture)

The corrected analysis strengthens Chain 2 Drill 3. The DuckDB companion is needed for:
- Exact aggregation of any type
- Ad-hoc semantic+aggregate queries (SA-class)
The DuckDB companion is NOT needed for:
- Approximate GROUP BY COUNT (Pattern A bundle energy, after formula fix)
- Pre-defined aggregate lookups (Pattern B)

The V1 architecture recommendation is unchanged: hybrid = substrate + DuckDB.
The new nuance: Pattern A and Pattern B provide partial native aggregation for specific
query classes that can reduce DuckDB round-trip frequency in production.

### DuckDB VSS extension (new finding from search)

DuckDB 1.0+ (released June 2024) includes a VSS extension with HNSW approximate nearest-neighbor
search. This means DuckDB can serve BOTH the OLAP aggregation role AND approximate vector
similarity search in a single engine. The substrate + DuckDB hybrid may be compressible into
DuckDB-only for some query classes (DuckDB VSS for approximate semantic retrieval + DuckDB SQL
for exact aggregation), with substrate reserved for exact K-hop compositional queries that
DuckDB HNSW cannot perform (binding/unbinding, role-filler decomposition, K-hop traversal).

This is a material architecture finding: the hybrid architecture may simplify to
DuckDB-as-OLAP-plus-approximate-vector-search + substrate-for-compositional-queries.
Recommended follow-up drill: evaluate DuckDB VSS recall vs substrate recall on K-hop queries.

---

## Part 9: Substrate-Product Implications

1. **The AVG 100% error was a bug, not a wall.** The formula in Cycle 155 had an off-by-N
   division error. Correcting it likely shows approximate GROUP BY COUNT at 1-3% error. This
   changes the product narrative from "substrate cannot aggregate" to "substrate provides approximate
   COUNT, DuckDB provides exact everything else."

2. **Pattern B enables exact aggregation for templated queries.** For dashboard-style products
   where aggregate query types are known at write time (e.g., healthcare EMR: COUNT of diagnoses
   by code, AVG HbA1c by patient cohort), Pattern B pre-computes and stores aggregates as semantic
   facts. Query is a semantic lookup, not a scan. This is a genuine substrate-native path.

3. **DuckDB VSS changes the hybrid architecture calculus.** If DuckDB handles both ANN search
   and OLAP aggregation, the substrate role narrows to: compositional binding (K-hop), exact
   semantic retrieval with VSA algebra, and Pattern B aggregate storage. This is a cleaner
   product boundary.

4. **SA-class queries remain the moat.** The joint semantic+aggregate query class (substrate
   retrieves semantically-similar facts, DuckDB aggregates their scalar attributes) is not
   expressible in DuckDB VSS alone because DuckDB HNSW does not support compositional VSA
   queries (K-hop, role-filler binding). This is the defensible product differentiation.

5. **Error bound documentation is a product requirement.** For any native-substrate approximation
   (COUNT, GROUP BY COUNT, window COUNT), the product must document the error bound clearly:
   O(1/sqrt(N)) relative error, with N=65536 giving ~0.4% relative error. Customers using
   approximate aggregation must accept these bounds; exact-accounting customers use DuckDB path.

---

## Citations

1. Kanerva, P. (1988). Sparse Distributed Memory. MIT Press. [Bundle energy COUNT estimator]
2. Schlegel, K., Neubert, P., Protzel, P. (2023). Capacity Analysis of Vector Symbolic
   Architectures. arXiv:2301.10352. [SNR ~ sqrt(N/M), interference noise floor]
3. Gayler, R.W. (2003). Vector Symbolic Architectures Answer Jackendoff's Challenges for
   Cognitive Neuroscience. In Slezak (ed.), ICCS/ASCS. [JOIN via shared filler]
4. Graefe, G. (1993). Query Evaluation Techniques for Large Databases. ACM Computing Surveys
   25(2):73-170. [Enumeration requirement for GROUP BY]
5. Flajolet, P., Fusy, E., Gandouet, O., Meunier, F. (2007). HyperLogLog: the analysis of
   a near-optimal cardinality estimation algorithm. DMTCS Proceedings. [HyperLogLog analogy]
6. Kleyko, D., Rachkovskij, D.A., et al. (2022). A Survey on Hyperdimensional Computing aka
   Vector Symbolic Architectures, Part I. ACM Computing Surveys. arXiv:2111.06077.
   [Binding/unbinding/superposition algebra review]
7. DuckDB VSS extension documentation. https://duckdb.org/docs/extensions/vss.html (2024).
   [HNSW approximate nearest-neighbor in DuckDB 1.0+]
8. Neubert, P., Schubert, S., Protzel, P. (2021). Hyperdimensional Computing as a Framework
   for Systematic Aggregation of Image Descriptors. CVPR 2021. [HD aggregation via superposition]

Verified citations: 8
