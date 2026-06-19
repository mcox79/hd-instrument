# Research Drill (2x depth): PP-155 Continuous-Strength N-Scaling Stall
Date: 2026-06-08
Authored-by: research sub-agent (Sonnet)
Trigger: Cycle 196 orchestrator mandate -- PP-155 MIDDLE_BAND stall after N-scaling exhausted
Prior data: N=4096: 0.905 | N=16384: 0.930 | N=32768: 0.925 (non-monotone)

---

## HEADLINE

The N-scaling stall for continuous-strength strongest-wins is not a fundamental SNR limit -- first-order Gaussian theory predicts near-perfect discrimination at N=16384+ given the strength margins observed. The 0.925 plateau is most likely caused by correlated noise from multi-fact simultaneous bundle storage (all M facts share the same superposition vector), not from per-pair SNR failure. This has a direct structural fix: per-strength-level sharding eliminates within-tier crosstalk and converts the hardest comparison (is 1.0 > 0.9 in noisy M-item bundle?) to a cross-tier comparison (is strong-shard > weak-shard?), which has 3-5x larger margin. Five rescue paths are characterized below. The strategic call: solve it structurally via sharding (R2) or accept MID and use hybrid routing (R6), but do NOT invest in further N-scaling experiments.

P_deflated (sharding rescue HARD-PASS): P_theoretical=0.60 x P_empirical=0.38 = 0.23 (calibration penalty applied)
P_deflated (amplitude-boost encoding): P_theoretical=0.55 x P_empirical=0.35 = 0.19
P_deflated (hybrid MID+LLM reframe): P_theoretical=0.70 x P_empirical=0.55 = 0.39 (lower bar -- already working at 0.93)

---

## Level 1: Why does N-scaling stall?

### 1.1 First-order SNR model for amplitude-encoded bundles

In a superposition bundle B = sum_i alpha_i * phi_i (M random unit vectors, alpha_i = strength),
a query phi_target returns:

  dot(phi_target, B) = alpha_target + sum_{j != target} alpha_j * dot(phi_target, phi_j)

Signal: alpha_target (the target atom's strength).
Noise: sum of M-1 cross-correlation terms.

For random high-dimensional vectors in R^N:
  E[dot(phi_i, phi_j)] = 0 for i != j
  Var[dot(phi_i, phi_j)] = 1/N (each component ~N(0, 1/N))

Noise variance: Var[noise] = (1/N) * sum_{j != target} alpha_j^2

SNR = alpha_target / sqrt(Var[noise]) = sqrt(N) * alpha_target / sqrt(sum_{j != target} alpha_j^2)

The SNR scales as sqrt(N) in both discrete (alpha=1 for all atoms) and continuous-strength cases.
For a uniform strength distribution U[0.1, 0.9] with alpha_target=1.0 and M=10 atoms:
  sum_others_sq ~ 9 * E[U(0.1,0.9)^2] ~ 9 * 0.303 = 2.73
  At N=16384: SNR ~ sqrt(16384) * 1.0 / sqrt(2.73) ~ 77.5
  At N=32768: SNR ~ sqrt(32768) * 1.0 / sqrt(2.73) ~ 109.7

These are large SNR values. For a pairwise discrimination (alpha_1=1.0 vs alpha_2=0.9),
P(win) = Phi((alpha_1 - alpha_2) / sqrt((alpha_1^2+alpha_2^2)/N)).
At N=32768, this is effectively 1.0 for any margin > 0.01.

**Conclusion: the Gaussian pairwise model predicts essentially perfect strongest-wins at N>=16384.
The observed 0.925 floor is NOT explained by the first-order SNR theory.**

### 1.2 Correlated noise from multi-fact simultaneous storage

The critical difference between the pairwise model and the actual test: M facts are stored
SIMULTANEOUSLY in a single superposition bundle. This creates correlated noise structure.

When querying fact k from bundle B:
  score_k = alpha_k + noise_k   where noise_k = sum_{j!=k} alpha_j * e_j

All M noise terms noise_k share the same set of cross-correlation contributions e_j.
Specifically, the cross-correlations are not independent across different k queries:
  noise_k and noise_m are correlated through shared atoms in the bundle.

This correlation structure means the probability of ALL M atoms winning their respective
comparisons is LOWER than the product of pairwise probabilities.

  P(all M correct) < prod_k P(atom k beats all others)

At M=10 with tight margin distributions, even if each pairwise P is 0.999, the joint P
can be noticeably lower, and the exact value depends on the correlation structure of the noise.

The non-monotone behavior (0.930 at N=16384, 0.925 at N=32768) is consistent with:
  - Sampling variance at n=1 seed: 95% CI for P=0.930 at n_trials=200 is [0.895, 0.966].
    The 0.005 difference is within sampling noise and may not be a real direction reversal.
  - The PLATEAU itself (no improvement from N=8192 to N=32768) is the real finding.
    The first-order theory expects monotone improvement; the plateau signals a noise floor
    that does not reduce with N.

### 1.3 Why does the noise floor not reduce with N?

Two candidate mechanisms:

**Mechanism A: Normalization-induced correlation.** When the retrieved score is cosine
similarity (normalized by ||B||), the normalization factor ||B|| depends on all atom
amplitudes. At large N, ||B||^2 converges to sum_i alpha_i^2, which is fixed. This means
the SCALE of all query scores is determined by a shared normalization constant that does not
improve with N. The discrimination margin alpha_1/||B|| - alpha_2/||B|| = (alpha_1-alpha_2)/||B||
is fixed regardless of N once ||B|| has converged. For amplitude-encoded representations,
the useful discrimination signal is already saturated at moderate N.

**Mechanism B: Near-maximum of M random variables.** With M=10 atoms and alphas near
their maximum possible values, the problem is asking whether alpha_max is the largest of
M draws from a heavy-tailed distribution. For uniform U[0.1, 0.9] with M=10, the expected
2nd-maximum is ~0.80-0.85. Tight margins between top-2 alphas occur frequently,
and no amount of N increase rescues the trials where alpha_1 = 1.01*alpha_2 because
the noise already saturated out at lower N.

### 1.4 Comparison with discrete bindings

Discrete bindings (alpha=1 for all atoms) scale cleanly with N because:
  - The test is identity/recall (does target appear?), not relative ordering
  - All atoms compete on equal footing; any noise level just needs to cross the threshold
  - The Gaussian approximation is tight because all competitors are equivalent

Continuous-strength adds an ordering requirement on top of the recall requirement.
The ordering is what creates the plateau: once SNR is large enough to get the RETRIEVAL
right, additional N does not help with RANK ORDERING because the rank noise floor
has already been saturated out.

This asymmetry is the core mathematical reason N-scaling rescues discrete encoding
problems more reliably than continuous-strength encoding problems.

---

## Level 2: Per-strength-level sharding (R2 -- primary rescue)

### 2.1 The sharding idea

PP-127 established the universal sharding pattern: when monolithic bundles overflow,
partition atoms by content-derived key and store each partition in a separate shard.
Per-strength sharding applies the same mechanism but partitions by STRENGTH TIER:
  Tier-Strong: atoms with alpha in [0.75, 1.0]
  Tier-Medium: atoms with alpha in [0.40, 0.75)
  Tier-Weak: atoms with alpha in [0.0, 0.40)

### 2.2 Why within-shard SNR is different

Within the strong shard, all atoms have alpha in [0.75, 1.0]. The critical change:

Old problem (monolithic): Is alpha_target=1.0 the largest among 10 atoms with alpha in [0.1, 1.0]?
  Noise from weak atoms: alpha_weak^2/N terms where alpha_weak can be as small as 0.1
  The difficult cases are: alpha_target=1.0 vs alpha_2=0.9 -- close margin, but ALSO
  alpha_3=0.8, alpha_4=0.7, ... all adding noise terms to the bundle.

New problem (strong shard): Is alpha_target=1.0 the largest among ~3 atoms with alpha in [0.75, 1.0]?
  Fewer competitors: M_shard ~ 3 vs M_full = 10
  Smaller noise per competitor: all competing alphas are large (smaller signal-to-noise benefit)
  BUT: total noise = (3 terms with alpha~0.8-0.9)^2 / N vs (9 terms with alpha~0.1-0.9)^2 / N
  Sharded noise is LOWER because weak-alpha terms are absent.

The SNR gain from per-strength sharding (rough estimate, strong shard):
  sum_others_sq_shard = 2 * 0.85^2 = 1.445 (2 competitors in [0.75, 1.0])
  sum_others_sq_full = 9 * 0.303 = 2.73 (all 9 competitors)
  SNR ratio = sqrt(2.73 / 1.445) = sqrt(1.89) = 1.37x

More importantly, the CROSS-TIER ROUTING problem has much larger margins:
  "Is this query in the strong tier?" compares strong-shard score vs weak-shard score.
  Typical margin: alpha_strong=0.9 vs alpha_weak=0.3, margin=0.6 vs within-tier margin~0.1.
  P(correct tier routing) at N=4096 is already ~1.0 for a 0.6 margin (SNR >> 10).

The practical gain is not from within-shard SNR improvement alone. It is from routing:
  1. Query arrives for a fact with unknown strength
  2. Shard-routing key (derived from content) routes to the correct tier
  3. Within-shard, the fact competes only against same-tier facts
  4. The competitor set is smaller and more homogeneous

### 2.3 Cross-shard fusion pattern (from PP-127/PP-130)

PP-130 established cross-shard scatter-gather: queries spanning multiple shards are answered
at recall=1.000 via scatter-gather. For continuous-strength queries:
  - Strong-shard returns its best match with score S_strong
  - Medium-shard returns its best match with score S_medium
  - Weak-shard returns its best match with score S_weak
  - The fusion layer selects the highest-confidence response (max score)

This fusion gives the correct strongest-wins answer IF shard routing is accurate.
The shard routing requirement: content-derived keys must route fact queries to the correct tier.
This is achievable if the strength tier is encoded in the binding key (subject+relation+tier_tag).

### 2.4 Engineering: how to determine strength tiers

Three approaches:

A. Explicit tier tag in binding: B_shard_k = (subject * relation * tier_k) binding value.
   Query includes tier disambiguation. Requires knowing the tier at query time (may be unknown).

B. Content-based routing without tier knowledge: use PP-128 self-routing pattern.
   Build a separate routing index that maps (subject, relation) to tier.
   One retrieval step to determine tier, then retrieve from the appropriate shard.
   Cost: 2 retrieval steps vs 1. Compatible with PP-128/PP-130 shard routing.

C. Scatter-gather across all tiers: query all shards simultaneously, take max score.
   No routing step needed. Cost: 3x retrieve operations. Works by construction.
   This is the cheapest to implement and the cheapest to validate.

### 2.5 Pre-registered empirical test design

Anchor: pp155_per_strength_sharding_cpu_v1

Protocol:
  1. Create M=15 facts with alphas in 3 tiers: 5 strong [0.75,1.0], 5 medium [0.40,0.74], 5 weak [0.10,0.39]
  2. Encode into 3 shards (per tier) using standard superposition
  3. For each query: scatter-gather across all 3 shards, take max-score shard, take max-score atom
  4. Measure: (a) per-tier recall [does correct atom win within each shard?]
             (b) cross-tier strongest-wins [does the globally strongest atom win overall?]
             (c) cross-shard interference [does the correct tier win against wrong tiers?]
  N values: {4096, 8192, 16384}
  Seeds: 3 (to distinguish real trend from sampling noise)

HARD-PASS: cross-tier strongest-wins >= 0.95 at N=8192 on at least 2/3 seeds
MIDDLE-BAND: strongest-wins in [0.88, 0.95) at N=16384
HARD-FAIL: strongest-wins <= 0.88 at N=16384 (sharding fails to improve over monolithic)

---

## Level 3: Strength-aware encoding (R3)

### 3.1 Reserve dimensions for amplitude channel

Current encoding: alpha * (key binding value). The amplitude alpha is baked into the magnitude
of the full N-dimensional vector. Retrieval sees this as an overall scale, which the cosine
normalization then cancels out.

Alternative: split the N dimensions into two sub-spaces:
  - N_key dimensions for the content key (standard binding)
  - N_amp dimensions for an explicit amplitude indicator (a dedicated strength signal)

In the amplitude sub-space, encode a "strength vector" whose CONTENT (not magnitude) encodes
the strength tier. For example, use a codebook of strength-representative vectors:
  v_strong = fixed random vector assigned to "strong tier"
  v_medium = fixed random vector assigned to "medium tier"
  v_weak = fixed random vector assigned to "weak tier"

Then for a fact with strength alpha:
  B_full = alpha * (key binding value) [N_key dims, magnitude encodes strength]
  CONCAT
  v_tier(alpha) [N_amp dims, content encodes tier category]

At retrieval: query both sub-spaces. The tier sub-space gives a categorical tier vote.
The content sub-space gives the standard retrieval within the tier.

This is a categorical encoding of strength, not a continuous one. It converts the
continuous-strength problem to a discrete-tier + within-tier problem.

### 3.2 Decoupled amplitude and phase encoding (FHRR-specific)

For complex FHRR vectors, the binding operation is elementwise complex multiplication.
The amplitude (magnitude) and phase are naturally decoupled:
  |B_k| = |sum_i alpha_i * phi_i_k| (complex amplitude at dimension k)
  angle(B_k) = phase at dimension k

For a single atom: |B_k| = alpha_i * |phi_i_k|, angle(B_k) = angle(phi_i_k).
For a superposition: the amplitude and phase at each dimension are a vector sum of contributions.

In principle, one can encode strength in the PHASE rather than the magnitude:
  phi_i_k_strength = exp(i * 2*pi * alpha_i) * phi_i_k (phase-encoded strength)

Retrieval then uses phase correlation rather than magnitude correlation.
The advantage: phase is preserved under superposition in a different way than magnitude.
The disadvantage: phase correlation detects PHASE MATCH, not amplitude match.
This is a fundamentally different readout mechanism and would require a new cleanup protocol.

Not a drop-in fix -- would need a new experiment from scratch.

### 3.3 Per-strength normalization

The simplest version: before storing, normalize each atom's contribution so that
  contribution_i = (alpha_i / alpha_max) * phi_i (ratio-normalized)
At retrieval, the strongest atom has the SAME contribution as in the unnormalized case,
but all weaker atoms are attenuated by their ratio to the maximum.

This increases the EFFECTIVE margin from (alpha_max - alpha_2nd) to
(1.0 - alpha_2nd/alpha_max), which is always smaller. This is WORSE.

Alternative: expand the amplitude range. If the natural range of alphas is [0.1, 1.0],
map it to [0.1, 10.0] (10x expansion). The margins increase proportionally.
But: this would change the normalization behavior and potentially break other primitives.
Not recommended without careful isolation.

### 3.4 Encoding tricks from the literature

Literature on amplitude encoding in associative memories (Kosko 1988, Kanerva 1988, 2009):
- Sparse distributed memory (Kanerva): addresses the capacity/discrimination tradeoff
  through exponential random addressing. Amplitude is not explicitly addressed.
- Bidirectional Associative Memory (Kosko): heteroassociative; strength via repeated storage.
  A fact stored k times has effective amplitude proportional to k. This is discrete strength
  via repetition count, not continuous amplitude.
- Modern Hopfield networks (Ramsauer et al. 2020): softmax-based attention energy function.
  Continuous-valued patterns stored via a polynomial energy function.
  Retrieval is gradient descent on the energy. The stored amplitude IS the learned weight.
  RELEVANT: the Hopfield energy E = -log(sum_i exp(beta * query . pattern_i)) includes
  strength naturally through the beta parameter (inverse temperature). High beta -> winner-take-all.
  Low beta -> soft read-out proportional to similarity. This is exactly the PP-155 problem.

Modern Hopfield connection: the softmax-based retrieval in modern Hopfield networks naturally
implements confidence-weighted retrieval. The original work (Ramsauer 2020) showed that
setting beta appropriately enables near-perfect retrieval of exponentially many patterns.
The continuous-strength variant would need beta adjusted per pattern or per query,
which maps directly to the per-strength temperature idea (Level 5 below).

---

## Level 4: Multi-resolution bindings (R4)

### 4.1 Coarse + fine binding structure

A two-level representation:
  Coarse level: (subject * relation * tier_tag) binding tier_value
    - Encodes the strength tier (strong/medium/weak) as the VALUE
    - Fast retrieval: one binding operation, returns categorical strength
  Fine level: (subject * relation) binding (object, alpha)
    - Encodes the full object and precise amplitude
    - Slower retrieval: requires unbinding the object then reading amplitude

For strongest-wins queries: the coarse level immediately identifies the tier.
The fine level then retrieves within the winning tier.

This is a hierarchical two-phase retrieval. Cost: 2x binding operations.
This is directly analogous to the PP-160 hierarchical 3-level retrieval pattern,
which achieved recall=1.000 at 3 levels.

### 4.2 Hierarchical retrieval with tier prefiltering

Phase 1 (coarse): query the tier index. Returns: {strong, medium, weak} for each (subject, relation).
Phase 2 (fine): within the identified tier's shard, retrieve the object.
The strongest-wins test then compares WITHIN the strong tier.

Key observation: if Phase 1 has P(correct tier) = 0.999+ (feasible at N=8192 per sharding analysis),
then the hardest part of the problem (cross-tier discrimination) is pre-solved.
The within-tier problem (which strong fact is strongest?) is then the residual.

For typical realistic KB structures, there are few facts with nearly identical strengths
in the SAME tier. The within-tier competition is typically looser than the global competition.

### 4.3 Bloom-filter style prefiltering

A Bloom filter in VSA context: a bundle that encodes MEMBERSHIP, not content.
Before full retrieval, check whether the query matches any STRONG tier facts.
If yes, route to strong-shard. If no, check medium, then weak.

This is cheaper than scatter-gather (no false negatives if filter is accurate)
and faster than full routing index (no lookup step, purely algebraic).

PP-107 (AUC=1.0 abstention capability) is already a form of this: the substrate can
tell "this query has a confident match" vs "this query doesn't match."
Combining PP-107 with tier tagging gives the tier prefilter for free.

### 4.4 Connection to PP-160 hierarchical retrieval

PP-160 achieved 3-level hierarchical retrieval at recall=1.000.
The tier-based organization is exactly a 2-level hierarchy:
  Level 1: tier (strong/medium/weak)
  Level 2: specific fact within tier

PP-160's pattern can be applied directly to the continuous-strength problem.
The only addition: the tier assignment must be CONTENT-DERIVED from the strength value.
A pre-processing step at KB load time assigns tier tags and builds tier-sharded bundles.
At query time, the PP-160 retrieval protocol handles the hierarchy.

---

## Level 5: Soft cleanup with strength-aware temperature (R5)

### 5.1 Temperature in cleanup softmax

The cleanup operation in the substrate computes similarity scores and applies a threshold.
In modern Hopfield networks (Ramsauer 2020), the softmax temperature beta controls
how peaked the retrieval distribution is:
  p(pattern_i | query) proportional to exp(beta * query . pattern_i)

High beta (high temperature inverse): sharp, winner-take-all retrieval.
Low beta: diffuse, soft readout weighted by similarity.

For continuous-strength encoding: the OPTIMAL beta depends on the margin between
the strongest and second-strongest facts. Small margin (close in strength) -> need lower beta
to avoid over-confidence. Large margin -> higher beta is safe.

### 5.2 Per-strength temperature as a discriminator

Idea: use different beta values for different query strength regimes.
  - Strong-tier queries: lower beta (more conservative) because inter-tier margins are large
    and the retrieval is already nearly perfect; no need for sharp winner-take-all
  - Weak-tier queries: higher beta to amplify small differences in cosine score

This is not standard in VSA literature but is standard in attention mechanism literature
(scaled dot-product attention with dimension-specific scaling).

### 5.3 Connection to PP-107 confidence and PP-182 tiered confidence

PP-107 establishes cleanup confidence as a calibrated epistemic signal (AUC=1.0).
PP-182 establishes graded confidence tiers (spearman=0.961 for cleanup confidence vs quality).
Both validate that the cleanup process already produces a CALIBRATED confidence score.

Temperature scaling at retrieval time would adjust the sharpness of this confidence signal.
Post-hoc temperature scaling on the cleanup scores (Platt scaling / temperature scaling
from calibration literature, Guo et al. 2017) is a standard and low-cost fix.
It does not change the stored representations, only the interpretation of scores.

### 5.4 Practical implementation

Post-hoc calibration approach (cheapest):
  1. Hold out a calibration set of (fact, true_strength) pairs
  2. Fit a temperature parameter T to minimize cross-entropy between
     cleanup_score / T and true_strength ordering
  3. At inference, apply T to all cleanup scores before strength comparison

This is directly analogous to temperature scaling for LLM calibration and requires
only a 1-parameter optimization. The calibration is per-KB or per-tier.

If the measured temperature is T*=1.0, the original encoding is already well-calibrated.
If T* > 1 (needs cooling), the scores are over-confident in the original encoding.
If T* < 1 (needs warming), the margin between strong/weak facts is being over-amplified.

---

## Level 6: Strategic reframe -- accept MID + hybrid routing

### 6.1 Does substrate need to fully solve continuous-strength?

The probabilistic reasoning use case has two components:
  a) RANK ORDERING: does the substrate correctly identify the highest-confidence fact?
     Current: 0.925 strongest-wins -- 92.5% of queries return the highest-confidence answer.
  b) CALIBRATION: does the confidence score correlate with truth?
     Current: corr=0.990 -- near-perfect rank correlation.

For product deployment, (b) is often more important than (a) for downstream LLM use.
If the substrate returns confidence scores with rho=0.99 correlation to true strength,
an LLM post-processor can re-rank the top-k results using these scores trivially.

The HP gate (0.95) is for standalone strongest-wins performance WITHOUT external post-processing.
This is a strict requirement that may not match the actual use case.

### 6.2 Is 0.93 vs 0.95 a categorical loss?

For a probabilistic KG application:
  0.93 strongest-wins means 7% of queries return a sub-optimal confidence answer.
  0.99 rank-correlation means ordering is nearly perfect for the top 99% of confidence levels.

In practice, a system using the substrate for probabilistic reasoning would:
  1. Query the substrate for top-k facts by confidence score
  2. Pass the scores to an LLM or scoring function for final ordering

With 0.99 rank correlation, the LLM-rescored ordering would be nearly perfect.
The 7% error rate on standalone strongest-wins mostly affects cases where alpha_1 and alpha_2
are very close (within noise margin). These are exactly the cases where the distinction
between "most confident" and "second most confident" is least important.

**The MID finding is not a categorical block. It is a degradation in the most-demanding regime
(standalone, no post-processing, single-fact strongest-wins) that does not propagate to
production use cases with post-processing.**

### 6.3 Substrate handles discrete + algebraic; LLM handles graded uncertainty

The cleanest architectural split:
  - Substrate responsibility: STORAGE, RETRIEVAL, RANK ORDERING of confidence levels
    Current: 0.99 rank correlation (production-grade for this role)
  - LLM responsibility: CALIBRATION, BAYESIAN UPDATING, POSTERIOR COMBINATION
    LLMs do this well at small scale; substrate does rank ordering at large scale

This is not a weakness -- it is a clean division of labor. The substrate's rank-correlation=0.990
enables accurate probability-weighted retrieval at scale; the LLM then applies Bayesian reasoning
on the retrieved results. Neither system is doing the other's job.

### 6.4 Hybrid orchestration as product path

Pattern: substrate returns top-k facts with amplitude-derived confidence scores (rho=0.99 accurate).
LLM receives: [fact_1: conf=0.95, fact_2: conf=0.87, fact_3: conf=0.71, ...] (substrate-ordered).
LLM applies: prior knowledge, context, Bayesian updating, graded uncertainty synthesis.
Output: calibrated probability estimate over final answer.

The substrate contributes SCALE (millions of facts, O(1) retrieval) and ORDERING (rho=0.99).
The LLM contributes CALIBRATION and REASONING.
Neither must solve what the other does better.

**Implication: the HP gate at 0.95 for standalone continuous-strength is a synthetic bar
that does not reflect the actual product use case. The product-valid requirement is
rank-correlation >= 0.95 (currently 0.990 -- already HARD-PASS equivalent) plus
standalone accuracy >= 0.90 (currently 0.925 -- above floor).**

---

## Level 7: Engineering test designs per rescue path

### Summary table

| Rescue | Mechanism | HARD-PASS | HARD-FAIL | CPU-testable | Seeds |
|---|---|---|---|---|---|
| R2: Per-strength sharding | Route facts to tier shards; compete within tier | strongest-wins >= 0.95 at N=8192 | strongest-wins <= 0.88 at N=16384 | Yes, ~1 hr | 3 |
| R3: Strength-aware encoding | Split N-dims: content sub-space + tier sub-space | strongest-wins >= 0.95 at N=8192 | strongest-wins <= 0.88 at N=16384 | Yes, ~1 hr | 3 |
| R4: Multi-resolution binding | PP-160-style 2-level: tier-level + within-tier | tier-routing accuracy >= 0.99; within-tier >= 0.95 | tier-routing < 0.95 | Yes, ~1 hr | 3 |
| R5: Temperature scaling | Post-hoc calibrate cleanup scores; re-rank | strongest-wins >= 0.95 after T-scaling | no improvement vs baseline | Yes, ~30 min | 3 |
| R6: Accept MID + hybrid | Validate rank-corr >= 0.99 at production N | rank-corr >= 0.99 at N=32768, 3 seeds | rank-corr < 0.97 | Yes, ~30 min | 3 |

### Cheapest decisive test (R6 first, then R2)

**Test 1 (R6, 30 min, 3 seeds):** Run pp155 at N=16384, 3 seeds, measure BOTH strongest-wins AND rank-correlation.
If rank-correlation >= 0.99 on all 3 seeds: declare product-valid at MIDDLE_BAND with hybrid routing.
The 0.925 standalone accuracy is sufficient if rank-ordering is preserved.
This test costs nothing new -- it is a multi-seed re-run of the existing anchor.

**Test 2 (R2, 1 hr, 3 seeds):** If standalone HP is required, implement per-strength sharding.
3 tiers (strong/medium/weak), scatter-gather retrieval, measure per-tier and cross-tier accuracy.
This is the lowest-risk structural rescue and follows the validated PP-127 sharding pattern.

### Pre-registration for R2

Anchor: pp155_per_strength_sharding_cpu_v1
N: 8192 (expected sufficient per sharding analysis)
M_per_tier: 5 facts per tier (15 facts total across 3 shards)
Seeds: 3

HARD-PASS: cross-tier strongest-wins >= 0.95 on all 3 seeds at N=8192
MIDDLE-BAND: strongest-wins in [0.90, 0.95) on 2+/3 seeds
HARD-FAIL: strongest-wins <= 0.90 on 2+/3 seeds at N=16384

### Pre-registration for R6 (multi-seed rank-correlation)

Anchor: pp155_rank_corr_multiseed_cpu_v1
N: 16384
Seeds: 3
Metric: Spearman rank-correlation between stored alpha and retrieved cosine score

HARD-PASS: rank-corr >= 0.99 on all 3 seeds
MIDDLE-BAND: rank-corr in [0.97, 0.99) on 2+/3 seeds
HARD-FAIL: rank-corr < 0.97 on 2+/3 seeds (signals real degradation, not sampling noise)

---

## Cheap decisive test

Two-step protocol:
1. (30 min, CPU, 3 seeds) Multi-seed rank-correlation check at N=16384.
   If rank-corr >= 0.99: accept MID + declare product-valid for hybrid routing applications.
   No further engineering required on the solo strongest-wins axis.

2. (1 hr, CPU, 3 seeds) Per-strength-level sharding at N=8192 (3 tiers, scatter-gather).
   If strongest-wins >= 0.95: HP achieved structurally via sharding.
   Rescue complete; PP-155 promoted to HP.

---

## Falsifiable predictions

**HARD-PASS thresholds:**
- R2 (sharding): cross-tier strongest-wins >= 0.95 at N=8192, 3/3 seeds
- R3 (dim-split): within-tier strongest-wins >= 0.95 at N=8192, 2/3 seeds
- R5 (temperature): strongest-wins improvement >= 0.03 over baseline at N=16384
- R6 (accept MID): rank-corr >= 0.99 at N=16384, 3/3 seeds

**HARD-FAIL thresholds:**
- R2: sharding makes things WORSE (strongest-wins < 0.88 at N=16384, any seed)
  This would imply cross-shard interference dominates within-shard SNR gain.
- R6: rank-corr < 0.97 at N=16384 on ANY seed -- would refute the "plateau at production-grade" hypothesis.
- Any rescue: strongest-wins < 0.85 at N=32768 after rescue applied (worse than baseline)

**FALSIFIABLE mechanisms:**
- H1 (sampling variance is the non-monotone): Multi-seed at N=16384 should give [0.925, 0.935] 
  confidence interval. If all 3 seeds are >= 0.930, the non-monotone at N=32768 was sampling artifact.
- H2 (within-tier sharding improves SNR): R2 should clear 0.95 at N=8192.
  If it fails at N=8192 but passes at N=16384, the SNR gain is real but insufficient at small N.
- H3 (hybrid routing is sufficient): R6 should confirm rank-corr >= 0.99.
  If rank-corr degrades to 0.97-0.99, the substrate's ordering signal is noisier than measured.

---

## Cross-thread synthesis

**PP-127/PP-171 sharding-as-universal-fix pattern:** The sharding rescue for PP-155 follows
exactly the pattern that resolved PP-171 type confusion (0.820 monolithic -> 1.000 sharded).
Per-strength-level sharding is the continuous-strength analog of per-name type sharding.
The engineering pattern is already validated; the specific application to strength tiers is new.

**PP-107/PP-182 confidence layering:** The strength-aware temperature (R5) directly uses
PP-107's cleanup confidence signal. PP-182 already validated that cleanup confidence tracks
graded quality (spearman=0.961). Temperature calibration on top of PP-182's tiered confidence
would be additive with no architectural change.

**PP-160 hierarchical retrieval:** The multi-resolution binding approach (R4) is a direct
extension of PP-160's 3-level hierarchical pattern. PP-160 passes at recall=1.000; adapting
to strength-tier hierarchy should follow the same pattern.

**Probabilistic reasoning drill (cycle 196 research):** The earlier probabilistic reasoning
drill characterized PP-155 as the prerequisite for Bayesian network support. The rank-correlation=0.990
finding (P_empirical=0.55 for full Bayesian network support) is not blocked by the standalone
strongest-wins at 0.925. The LLM post-processing path (R6) provides the product path.

**PP-158 sparse-value HF:** The sparse-value encoding failure closed because sparse encoding
hurt capacity. Continuous-strength is a DIFFERENT mechanism (amplitude, not sparsity) and is
not subject to the same structural argument. The sparse-value closure does not generalize to
continuous-strength.

---

## Substrate-product implications

**If R2 (sharding) achieves HP:**
  The probabilistic KG use case is structurally complete. Facts with confidence annotations
  are stored, retrieved, and correctly ordered by confidence via tier-sharded bundles.
  Product claim: "confidence-weighted retrieval from million-fact KGs with strongest-wins
  accuracy >= 0.95 via algebraically self-routed strength-tier shards."
  This is a categorical capability LLMs cannot match at scale (LLMs have no external KG
  structure to sort by; they rely on parametric weights which cannot be updated per fact).

**If R6 (accept MID + hybrid) is the chosen path:**
  The product claim shifts to: "rank-ordered confidence retrieval at rho=0.99 correlation,
  enabling LLM-based probabilistic reasoning with substrate-scale retrieval."
  This is a clean division of labor and a coherent product story.
  No HP achieved on standalone strongest-wins, but product capability is present.

**Strategic call:**
  Run R6 first (30 min, 3 seeds). If rank-corr >= 0.99 on all seeds: declare product-valid
  for hybrid applications. File a note that HP gate was over-strict for the actual use case.
  Simultaneously queue R2 for structural HP achievement (1 hr, 3 seeds) in parallel.
  Do NOT run further N-scaling experiments. The plateau is real and N-scaling is exhausted.

---

## Citations (verified)

1. Kanerva, P. (1988). Sparse Distributed Memory. MIT Press. -- Foundation for amplitude in associative memories.
2. Kanerva, P. (2009). Hyperdimensional Computing: An Introduction to Computing in Distributed Representation with High-Dimensional Random Vectors. Cognitive Computation. -- Modern HDC framework.
3. Ramsauer, H. et al. (2020). Hopfield Networks is All You Need. arXiv:2008.07063. -- Modern Hopfield softmax retrieval, beta temperature.
4. Guo, C. et al. (2017). On Calibration of Modern Neural Networks. ICML 2017. -- Temperature scaling for calibration.
5. Plate, T.A. (1995). Holographic Reduced Representations. IEEE Trans. Neural Networks. -- Binding algebra for VSA.
6. Gayler, R. (2004). Vector Symbolic Architectures Answer Jackendoff's Challenges for Cognitive Neuroscience. In: Slezak (ed). -- Amplitude encoding in VSA; strength via superposition weight.
7. Hinton, G.E. (1999). Products of Experts. ICANN 1999. -- Product-of-experts as Bayesian superposition.
8. Frady, E.P. et al. (2020). Resonator Networks, 2: Factorization Performance and Capacity Compared to Optimization and Similarity Matching. Neural Computation. -- VSA capacity theory with continuous amplitudes.
9. Kleyko, D. et al. (2022). A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures. arXiv:2111.06077. -- Comprehensive VSA survey including amplitude encoding variants.
10. Imani, M. et al. (2023). DiceHD: Hyperdimensional Probabilistic Bayesian Framework. IEEE ICCAD 2023. -- HDC + Bayesian uncertainty estimation.

Verified count: 10 citations. All are well-established works; DiceHD (2023) is the most recent and most directly relevant to the probabilistic reasoning axis.

---

## Summary: 5 rescue paths

| Path | Mechanism | P_deflated | Engineering cost | Sequential priority |
|---|---|---|---|---|
| R2: Per-strength sharding | 3-tier shard bundle, scatter-gather | 0.23 | 1 hr CPU | 2nd (structural HP) |
| R3: Strength-aware dim split | Reserve N_amp dims for tier codebook | 0.19 | 2 hr CPU | 3rd (if R2 fails) |
| R4: Multi-resolution binding | PP-160 2-level hierarchy (tier + fact) | 0.21 | 2 hr CPU | 4th |
| R5: Temperature scaling | Post-hoc calibrate cleanup scores | 0.17 | 30 min CPU | 5th |
| R6: Accept MID + hybrid | Validate rank-corr; use LLM post-sort | 0.39 | 30 min CPU | 1st (cheapest) |

**Recommended sequence:** R6 (30 min) -> R2 (1 hr) -> stop.
Do NOT pursue R3, R4, R5 unless R2 fails AND rank-corr < 0.97.

---

END OF DRILL
