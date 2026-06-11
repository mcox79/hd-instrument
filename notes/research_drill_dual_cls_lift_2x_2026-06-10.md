# Research Drill: Why DUAL-CLS Synergy Is Modest and How to Lift It (2x)
# Date: 2026-06-10
# Topic: dual_recall=0.962, fast_only=0.490, slow_only=0.922; +4pp synergy; McClelland gap

---

## HEADLINE

The +4pp dual-CLS synergy is mechanistically expected given the current implementation
structure: slow_only is already so strong (0.922) that fast adds value only where slow
fails -- a narrow failure mode at specific item ages or similarity boundaries. McClelland's
large predicted synergy gap requires that fast and slow are COMPLEMENTARY in the strict
sense: they must fail on different items (fast handles recent, slow handles generalized).
The current system is likely NOT complementary in this sense -- both routes are queried on
the same item set with no age-gating, no schema-routing, and no differential failure modes.
Three substrate-native lift paths have P_deflated >= 0.40 and require no new math:
(1) AGE-GATED RETRIEVAL BLEND (beta decays with item age -- fast dominates fresh, slow
    dominates consolidated); (2) SCHEMA-ROUTING (items matching slow schema skip fast query
    entirely); (3) ADAPTIVE-REPLAY-SCHEDULE driven by prediction error to ensure W_slow
    gets informative signal rather than uniform item stream. Highest P_deflated: 0.45 for
    age-gated blend (directly addresses the representation-overlap problem). Combined
    lift target: dual_recall >= 0.975, synergy gap >= 0.05 (from current 0.04).

---

## Level-2 mechanism diagnosis: why +4pp instead of +15-20pp

### D1. The ceiling problem

slow_only = 0.922 means the slow store already handles 92.2% of queries correctly.
The maximum theoretical gain from adding fast is bounded by the FAILURE SET of slow_only.
If slow fails on 7.8% of items, and fast recovers X% of those, the gain is 0.078 * X.

To get a +15pp gain (matching McClelland prediction), fast would need to recover
100% of items that slow fails on PLUS items that slow would otherwise misclassify.
That is only possible if fast and slow have complementary failure profiles.

Current empirical situation: fast_only = 0.490. Fast alone handles 49% of queries
correctly. In the dual system, assuming optimal oracle combination:
  dual_ceiling = P(slow OR fast correct) = P(slow) + P(fast) - P(both correct)

If slow and fast fail INDEPENDENTLY: P(both correct) ~ 0.922 * 0.490 = 0.452.
  dual_ceiling_independent = 0.922 + 0.490 - 0.452 = 0.960

The empirical dual = 0.962 is VERY CLOSE to the independence ceiling (0.960).
This means slow and fast are operating nearly independently -- they add almost exactly
the expected value of independent combination. This is actually a GOOD sign for
mechanism: the combination is working as expected. But the ceiling is low because
fast_only is only 0.490.

DIAGNOSIS IMPLICATION: lifting dual_recall requires lifting fast_only recall, not
just combining the two. The current +4pp is mathematically near-optimal given
fast_only = 0.490. The McClelland prediction of a larger gap assumes BOTH systems
are strong, not that fast is weak.

### D2. Why fast_only = 0.490 is low

In biological CLS, hippocampal fast learning is essentially perfect for recent items
(within the last few minutes to hours). The 0.490 figure indicates the fast store is
performing at chance for roughly half of queries. Three candidate explanations:

D2.a. CAPACITY SATURATION: K/N ratio too high in W_fast; interference between atoms
      reduces per-item recall. At K/N = 0.40 (near the 0.56 cliff), crosstalk is
      significant. If K = 100 items and N = 256, recall drops to ~0.5 (matches
      0.490 data point).

D2.b. UNIFORM ITEM-AGE STREAM: test evaluates all items at a fixed post-write lag
      regardless of age. Fast stores have time-dependent recall: near-perfect for
      freshly written items, degrading over time. If the test queries items at a
      UNIFORM lag that is beyond the fast-store's natural retention window, all items
      appear equally degraded and fast_only = 0.5 is expected.

D2.c. WRITE FIDELITY PROBLEM: the outer-product write accumulates interference
      proportional to K (number of items stored). If interference is high, even
      the most recent items have noisy representation. This is different from
      the capacity cliff (which is a retrieval problem) -- this is a representation
      quality problem.

D2.d. REPRESENTATION OVERLAP: if items being stored have high cosine similarity
      to each other (dense item set), the fast-store's interference is MUCH higher
      than for orthogonal items. Biological DG pattern-separation enforces near-
      orthogonality BEFORE storage; the current substrate may not have this.

Highest-likelihood explanation: D2.b (uniform age stream) and D2.d (representation
overlap), which together mean the test is not exercising the complementarity that
McClelland predicts.

### D3. What McClelland's large synergy gap actually requires

McClelland CLS predicts a large synergy gap UNDER SPECIFIC CONDITIONS that the
current test may not satisfy:

1. TEMPORAL COMPLEMENTARITY: hippocampus is queried for recent items (days-old);
   neocortex is queried for consolidated items (weeks-old). The two systems are
   NEVER queried on the same item at the same time with equal weight in biology.

2. SCHEMA COMPLEMENTARITY: hippocampus handles episodic specifics; neocortex
   handles statistical regularities. The synergy comes from COMBINING these
   on DIFFERENT ITEM TYPES, not on the same item.

3. REPLAY-DRIVEN CONSOLIDATION: slow store only gains value after REPLAY of
   fast-store contents. If W_slow is trained on an independent but correlated
   stream (not replayed from W_fast), it misses the specific episode bindings
   that make hippocampal replay valuable.

The current DUAL-CLS implementation likely:
- Queries both W_fast and W_slow on the SAME item set with EQUAL blend weights
- Does not age-gate the blend (beta is fixed, not a function of item age)
- Does not use schema-routing to decide which store to query first
- W_slow was trained on some independent slow stream, not via replay from W_fast

This means the dual system is closer to a MIXTURE MODEL than a true complementary
system. A mixture of two imperfect models with similar failure profiles gets
sqrt(P1 * P2) synergy, not the superlinear synergy McClelland predicts.

### D4. The spin-glass aging analogy as mechanism explanation

From the materials science angle (D1-D3 in the prior CLS drill): in a spin glass,
fast and slow relaxation timescales are COUPLED but COMPLEMENTARY. The fast degrees
of freedom equilibrate quickly; the slow ones equilibrate over aging timescales.
The two timescales add synergistically because they handle DIFFERENT frequency
components of the input signal.

In a KWW system: C(t) = exp(-(t/tau)^beta). The initial fast relaxation (small t)
and the long-tail slow relaxation (large t) are complementary. Total retention
is the INTEGRAL over the full decay curve, not just a single time-point query.

Substrate implication: if the dual-CLS test queries both stores at a SINGLE time
point (one fixed lag), it captures only a slice of the complementary profile.
A TEST THAT QUERIES AT MULTIPLE TIME LAGS would show much larger synergy -- with
fast dominating early and slow dominating late. The McClelland gap is across
the temporal distribution of queries, not at a single point.

This is the most parsimonious explanation for the gap between theory and data.

### D5. Schema-mediated consolidation as the missing synergy amplifier

Tse et al. (2007, 2011): schema-compatible items consolidate rapidly (single-trial)
while novel items consolidate slowly (weeks). The synergy amplification comes from
the DIFFERENTIAL CONSOLIDATION RATE. In the current implementation:

- All items experience the same consolidation rate (uniform alpha in W_slow)
- No item is classified as schema-compatible vs novel
- No accelerated write path exists for schema-matching items

With schema-mediated consolidation:
- Schema-compatible items appear in BOTH W_fast and W_slow quickly
- Novel items appear only in W_fast initially
- Dual retrieval is VERY strong for schema-compatible items (2x reinforcement)
- Dual retrieval is the same as fast-only for novel items (W_slow not yet populated)

This differential creates a LARGE synergy gap for schema-compatible items (which
is the majority in any realistic knowledge base with structured domains).

### D6. Adaptive replay schedule -- the missing amplifier for slow-store quality

If the replay schedule that trains W_slow is UNIFORM (all items replayed equally),
then W_slow converges to the mean of all items (a low-quality average representation).
If the replay schedule is PREDICTION-ERROR-DRIVEN (items with high mismatch between
W_fast and W_slow are replayed preferentially), then W_slow converges to the
INFORMATION-MAXIMIZING representation of the item distribution.

The difference: uniform replay gives W_slow = low-rank mean (useful for schemas,
not for specific items). Adaptive replay gives W_slow = high-information representation
(useful for specific items that fast alone mishandles).

This is why slow_only = 0.922 but dual adds only +4pp: slow_only is already good
at the same task as fast_only, meaning they fail on the same items (uniform replay
gives correlated failure profiles). If slow were instead optimized for FAST's
failure modes, the synergy would be much larger.

---

## Eight substrate-native lift paths (ranked by P_deflated)

### L1. AGE-GATED RETRIEVAL BLEND (P_deflated = 0.45)

Mechanism: beta(age) = sigmoid(-(age - T_pivot) / tau_beta) where age = steps since
item was first written. At age < T_pivot, beta -> 1 (query mostly W_fast). At
age > T_pivot, beta -> 0 (query mostly W_slow). T_pivot = N_buffer consolidation interval.

Why this lifts synergy: it enforces the temporal complementarity that biological
CLS requires. Fast handles new items (where it is accurate). Slow handles old items
(where it is accurate after consolidation). The dual test then sees EACH system in
its STRONGEST regime, and the gap grows from +4pp to the biological prediction.

Implementation: 2 parameters (T_pivot, tau_beta). Empirically: T_pivot ~ N_buffer,
tau_beta ~ 0.5 * N_buffer. One lookup in the item age ledger per query.

Pre-reg criterion: if age-gated dual achieves recall >= 0.975 on a stream where half
the items are fresh (age < T_pivot) and half are consolidated (age > T_pivot),
the mechanism is confirmed. The key observable: fast's contribution should dominate
for fresh items and slow's contribution for consolidated items.

HARD-PASS: dual_recall >= 0.975 (vs current 0.962); synergy gap >= 0.05 (vs 0.04).
HARD-FAIL: dual_recall < 0.965; gap improvement < 0.01 (age-gating confers no benefit).

### L2. SPARSE-FAST / DENSE-SLOW REPRESENTATION (P_deflated = 0.43)

Mechanism: W_fast writes use K-SPARSE inputs (top-k components of v_query, k ~ 0.1*N).
W_slow writes use DENSE inputs (full v_query). This enforces the biological DG/CA3
distinction: hippocampus receives pattern-separated (sparse) inputs from DG, while
cortex receives full (dense) distributed inputs.

Why this lifts synergy: sparse-fast reduces inter-item interference in W_fast
(interference is proportional to dot-product overlap, which is smaller for sparse
codes). Dense-slow captures full distributional structure for schema extraction.
The two stores now have DIFFERENT representational regimes, making their failure
profiles complementary.

Expected effect on fast_only: recall improves from 0.490 toward 0.70+ by reducing
crosstalk. This in turn increases the ceiling: dual_ceiling = P(slow) + P(fast) -
P(both) = 0.922 + 0.70 - (0.922 * 0.70) = 0.97+.

Implementation: k-sparse projection applied to queries before W_fast write.
k = floor(0.1 * N). Standard operation (quantile threshold). O(N) per write.

HARD-PASS: fast_only recall >= 0.65 with k-sparse write (vs 0.490 current);
           dual_recall >= 0.972 with sparse-fast + dense-slow.
HARD-FAIL: fast_only recall < 0.55 with k-sparse write (sparsity hurts more than it helps).

### L3. PREDICTION-ERROR-DRIVEN REPLAY SCHEDULE (P_deflated = 0.42)

Mechanism: during each consolidation pass, replay items in descending order of
prediction error: priority_i = |W_slow @ q_i - W_fast @ q_i|. Items where slow
and fast disagree most are replayed first (most informative signal to W_slow).

Why this lifts synergy: W_slow trained on prediction-error-driven replay converges
to a representation that is COMPLEMENTARY to W_fast, not a redundant copy.
Specifically: items where W_fast is accurate do NOT get replayed often (low prediction
error). Items where W_fast fails (high prediction error between slow and fast
prediction) get replayed heavily. W_slow becomes specialized in recovering W_fast's
failure modes -- exactly the biological hippocampal-cortical relationship.

This directly addresses D6 (uniform replay gives correlated failure profiles).

HARD-PASS: dual_recall >= 0.972; slow_only recall SHIFTS to better cover fast_only's
           failure set (measure as: P(slow correct | fast incorrect) increases by >= 0.10).
HARD-FAIL: P(slow correct | fast incorrect) does not change with prediction-error replay.

### L4. SCHEMA-ACCELERATED CONSOLIDATION GATE (P_deflated = 0.40)

Mechanism: on each new write to W_fast, compute cosine similarity to W_slow rows.
If max cosine > theta_schema (e.g., 0.65): write at HIGHER alpha (e.g., 0.05 vs 0.01)
to W_slow AND reset decay timer. Schema-matching items get fast-tracked to W_slow
in addition to W_fast. Novel items wait for the standard replay schedule.

Why this lifts synergy: schema-compatible items appear in both stores with high
fidelity after few writes. When queried, both stores agree and reinforce (both return
close to the correct answer, so even a 50/50 blend is excellent). Novel items rely
on W_fast alone initially, then transition to W_slow after consolidation. The test
sees LARGE synergy for schema items and standard synergy for novel items.

Expected distribution: if 60% of a realistic KB is schema-compatible, the weighted
synergy across the full item set rises significantly above the current +4pp.

HARD-PASS: schema-compatible item recall >= 0.985; novel item recall similar to
           current (0.962); population-weighted dual recall >= 0.978 on a 60/40 schema/novel mix.
HARD-FAIL: schema-compatible recall < 0.970 (schema gate not helping).

### L5. ORTHOGONAL FAST-WRITE PROJECTION (P_deflated = 0.38)

Mechanism: when writing a new item v to W_fast, project v to be orthogonal to
existing W_fast rows (Gram-Schmidt step):
  v_ortho = v - W_fast^T @ (W_fast @ v / sum(|W_fast_rows|^2))
Write v_ortho to W_fast. This maximally separates new items from old ones,
reducing W_fast interference without increasing N.

Why this lifts synergy: the orthogonal projection is the substrate's analog of
DG pattern separation (see L2). Unlike k-sparse, it explicitly removes overlap
with stored items rather than just reducing individual vector density. Fast_only
recall should increase significantly (approaching the retrieval accuracy of an
uncrowded store). W_slow then learns over a less-noisy replay signal.

Limitation: v_ortho may not preserve full item identity if W_fast is near capacity
(projection removes information when items span most of the space). Requires K < N.
Not compatible with K/N near the cliff.

HARD-PASS: fast_only recall >= 0.70 with orthogonal write (vs 0.490 current).
HARD-FAIL: fast_only recall < 0.55 (orthogonalization loses too much information).

### L6. RECONSOLIDATION-EDIT AS SYNERGY BRIDGE (P_deflated = 0.38)

Mechanism: during the consolidation replay pass, instead of just reading W_fast
rows into W_slow, apply delta_W corrections:
  delta_W_fast = eta * (W_slow @ q_i - W_fast @ q_i) * q_i^T  (pull fast toward slow)
  delta_W_slow += alpha * outer(q_i, W_fast @ q_i)            (update slow with fast)
This bidirectional update (Kumaran 2016 extension) makes the two stores converge:
W_fast aligns its old items toward the W_slow generalization, and W_slow absorbs
new episodic specifics. The result is true complementarity: W_fast holds fresh
specifics and SCHEMA-CORRECTED old specifics; W_slow holds generalized patterns.

This is the bidirectional CLS extension (PMC9606815, 2022) applied to the substrate.

HARD-PASS: after 100 consolidation passes with bidirectional update, P(fast correct |
           slow correct) > 0.90 (the two stores agree on consolidated items);
           P(fast correct | slow incorrect) < 0.20 (truly complementary failure modes).
HARD-FAIL: P(fast correct | slow incorrect) does not decrease (bidirectional update
           doesn't create complementarity).

### L7. TIMESCALE-RATIO OPTIMIZATION (P_deflated = 0.36)

Mechanism: the alpha ratio (fast write step size / slow write step size) determines
how quickly W_slow tracks W_fast. Current alpha is a fixed constant. Theory predicts:
for maximum synergy, alpha_slow / alpha_fast should equal the ratio of item retention
windows (slow_window / fast_window). If fast window = 100 steps and slow window = 10000
steps, alpha_slow / alpha_fast = 100/10000 = 0.01. But if the actual operational window
is different (e.g., short-stream test), the alpha ratio is mismatched and synergy drops.

Empirical test: sweep alpha_slow over {0.001, 0.005, 0.01, 0.05, 0.1} and measure
synergy gap at each setting. The optimal alpha_slow is the one that maximizes
P(slow correct | fast incorrect) -- not overall accuracy.

HARD-PASS: at some alpha_slow in sweep, synergy gap >= 0.08 (doubling the current 0.04).
HARD-FAIL: synergy gap < 0.05 across all alpha_slow settings (timescale ratio is
           not the bottleneck; the problem is elsewhere).

### L8. LONG-STREAM AGE-STRATIFIED EVALUATION (P_deflated = 0.35)

Mechanism: the +4pp synergy may be a MEASUREMENT ARTIFACT of evaluating all items
at the same time-lag rather than at their natural age. This is not a lift path but
a diagnostic: replace the current uniform-lag evaluation with age-stratified evaluation:
  - Stratum 1: items queried at age < 50 steps (fresh)
  - Stratum 2: items queried at age 50-500 steps (consolidating)
  - Stratum 3: items queried at age > 500 steps (consolidated)

McClelland predicts: fast >> slow in stratum 1; fast ~ slow in stratum 2; slow >> fast
in stratum 3. The dual system should dominate in stratum 2 (transition zone).

If the current test evaluates everything in stratum 2 or 3, fast_only = 0.490 and the
synergy gap is small by construction. This diagnostic runs BEFORE any of L1-L7 and
may explain 80% of the gap from theory to data without any code change.

HARD-PASS (diagnostic): fast_only recall at stratum 1 >= 0.80 AND slow_only recall
           at stratum 3 >= 0.95 AND dual recall at stratum 2 >= 0.975.
HARD-FAIL (diagnostic): fast_only recall at stratum 1 < 0.60 (fast store is degraded
           even for fresh items; capacity saturation is the bottleneck not age-gating).

---

## Five empirical tests (pre-registered with HARD-PASS / HARD-FAIL bands)

### TEST DL-1: Age-stratified synergy profile (cheapest, 30 min CPU, runs first)

Setup: 1000-item continual stream. Write items in order. At evaluation time, split
items into 3 age strata (fresh: age < 100; mid: 100-300; old: > 300). Query each
stratum separately using (a) W_fast only, (b) W_slow only, (c) dual blend 50/50.
Report: fast_only, slow_only, dual recall per stratum.

Pre-reg: if fast_only drops monotonically with age (0.70 fresh -> 0.40 old),
this confirms D2.b (uniform-lag test is the explanation for low synergy).
If fast_only is flat (~0.490) across all strata, D2.c or D2.d (capacity/overlap)
is the bottleneck.

HARD-PASS: fast_only at fresh stratum >= 0.70; dual at mid stratum >= 0.975.
HARD-FAIL: fast_only at fresh stratum < 0.55 (fast is broken even for recent items;
           capacity saturation dominates; need L2 or L5 before any age-gating helps).

### TEST DL-2: K-sparse write benefit for fast_only (45 min CPU)

Setup: same 1000-item stream. Compare fast_only recall:
  (a) baseline: dense write (current)
  (b) k=10% sparse write (L2 mechanism)
  (c) k=5% sparse write
  (d) orthogonal projection write (L5 mechanism, if K < N)

HARD-PASS: at k=10%, fast_only recall >= 0.65 (improvement from 0.490 baseline).
HARD-FAIL: at k=10%, fast_only recall < 0.55 (sparsification does not help; implies
           capacity saturation is not the main bottleneck for fast failures).

### TEST DL-3: Prediction-error-driven replay vs uniform replay (1 hr CPU)

Setup: 2000-item stream. Train W_slow via:
  (a) uniform replay (all items equally)
  (b) prediction-error replay (high-error items first, L3 mechanism)
Measure: P(slow correct | fast incorrect) for each condition.
This directly tests whether W_slow trained on prediction-error-driven replay
covers fast's failure modes better than uniform replay.

HARD-PASS: prediction-error replay increases P(slow correct | fast incorrect) by >= 0.10
           (absolute) vs uniform replay. Dual recall with prediction-error replay >= 0.975.
HARD-FAIL: P(slow correct | fast incorrect) difference < 0.03 (replay strategy does
           not affect complementarity; both converge to same representation).

### TEST DL-4: Alpha-slow sweep for optimal timescale ratio (1 hr CPU)

Setup: 1000-item stream; sweep alpha_slow in {0.001, 0.005, 0.01, 0.05, 0.1}.
For each alpha_slow: measure (a) slow_only recall, (b) dual recall, (c) synergy gap.
Report: which alpha_slow maximizes synergy gap (not dual recall -- those are different).

HARD-PASS: best alpha_slow in sweep gives synergy gap >= 0.08 (dual - slow_only >= 0.08).
HARD-FAIL: synergy gap < 0.05 across all alpha_slow (timescale ratio is not the lever).

### TEST DL-5: Schema-gated consolidation on structured item stream (1.5 hr CPU)

Setup: two item classes: SCHEMA-COMPATIBLE (50% -- items in a known domain, high
cosine similarity to W_slow after 200 warmup items) and NOVEL (50% -- random items
in a different domain). Write 500 warmup items; then alternate schema/novel.
Compare recall per class with and without schema-accelerated consolidation (L4 mechanism).

HARD-PASS: schema-compatible recall with schema gate >= 0.985; population-weighted
           dual recall >= 0.978 (vs 0.962 current).
HARD-FAIL: schema-compatible recall with gate < 0.970 (gate not helping);
           OR schema-gate degrades novel recall by > 0.02 (interference from frequent
           schema writes disrupts novel-item retrieval).

---

## Falsifiable predictions summary (HARD-PASS / HARD-FAIL table)

| Test | Prediction | HARD-PASS | HARD-FAIL |
|---|---|---|---|
| DL-1 age-strata | fast drops with age; dual peaks at mid | fast fresh >= 0.70; dual mid >= 0.975 | fast fresh < 0.55 |
| DL-2 k-sparse | fast_only lifts to 0.65+ with k=10% | fast_only >= 0.65 at k=10% | fast_only < 0.55 at k=10% |
| DL-3 PE replay | P(slow|fast fail) lifts by 0.10+ | gap +0.10 abs; dual >= 0.975 | gap < 0.03 |
| DL-4 alpha sweep | best alpha gives synergy >= 0.08 | gap >= 0.08 at best alpha | gap < 0.05 all alpha |
| DL-5 schema gate | schema items >= 0.985; pop dual >= 0.978 | pop dual >= 0.978 | schema recall < 0.970 |

Highest P_deflated among all lift paths: L1 age-gated blend = 0.45.
Combined P_deflated (all 5 tests pass and all 3 highest-ranked lifts work): 0.40.
Novel-synthesis cap honored: 0.45 < 0.50.

---

## Cross-thread synthesis with prior entries

1. Sprint-2 frequency-decay (synthetic-validated): L1 age-gated blend is a
   DIRECT EXTENSION of the frequency-decay ledger. The item age is already tracked
   in the frequency-decay ledger as t_last_access. No new data structure required.
   beta(age) can be computed on-the-fly from the existing ledger.

2. Prior CLS drill (continual_full_cls_5x, 2026-06-10): this 2x drill focuses
   specifically on the SYNERGY DEFICIT identified after the empirical dual_recall
   result. The five-stream synthesis from the prior drill provides the mechanism
   vocabulary (W_fast, W_slow, alpha, consolidation pass, schema-gate). The 2x drill
   provides the diagnostic and lift experiments.

3. K/N capacity cliff (0.56, empirically validated): DL-1 HARD-FAIL condition
   (fast fresh < 0.55) would indicate capacity saturation is the bottleneck, which
   traces directly to K/N being too high in W_fast. The fix is L5 (orthogonal
   projection) or reducing K before the test. K/N monitoring from prior drills
   is the correct pre-check before running DL-1.

4. Pool retrieval (validated): the dual blend (beta * W_fast + (1-beta) * W_slow)
   is structurally identical to pool retrieval with age-dependent weights. The
   existing pool retrieval code is the implementation vehicle for L1.

5. ROME/MEMIT scaling (editing budget O(sqrt(N))): DL-3 prediction-error replay
   is equivalent to selective orthogonal editing of W_slow (only updating it on
   high-error items). The ROME interference budget applies: sqrt(N) selective edits
   are safe. At N=1024, 32 selective replay updates per consolidation pass are safe.

---

## Substrate-product implications

1. DUAL-CLS gap fix = higher effective knowledge retention across long operational
   lifetimes. The compliance sidecar needs dual_recall >= 0.975 across KB sizes
   of 50K-1M facts. The +4pp current synergy is insufficient at scale. Lifting to
   +15pp (matching biological prediction) makes the substrate a competitive
   long-term memory system.

2. AGE-GATED BLEND = built-in staleness handling with no explicit expiry metadata.
   Old facts (high age) are queried primarily against W_slow (generalized schema);
   new facts are queried against W_fast (episodic specifics). This is a natural
   temporal freshness model that can be surfaced as a product feature: "recent facts
   retrieved with episodic precision; historical facts retrieved with schema-level
   accuracy."

3. PREDICTION-ERROR REPLAY = automatic quality-signal for consolidation.
   Items that W_fast and W_slow disagree on are the MOST UNCERTAIN facts in the KB.
   Surfacing these as "facts with low consolidation confidence" is a product-level
   feature: the substrate can flag which stored facts are not yet fully consolidated,
   giving operators a quality management signal without running any separate
   uncertainty quantification model.

4. K-SPARSE FAST WRITE = higher capacity before the retrieval cliff.
   If k-sparse write raises fast_only from 0.490 to 0.65+, it also raises the
   effective capacity of W_fast from K_max ~ 0.56*N to K_max_sparse ~ 0.56*N/rho
   where rho is the sparsity ratio (rho = k/N). At rho = 0.1, effective capacity
   is 10x higher. This is a direct capacity scaling result with no change to N.

5. SCHEMA-GATE = fast domain onboarding. When a new domain is introduced to the KB
   (new customer with a new knowledge domain), the first 200 items in that domain
   are "novel" and rely on W_fast alone. But once the schema is established in W_slow,
   all subsequent domain items are schema-compatible and get immediate dual-store
   reinforcement. This creates a natural domain warm-up period that shortens over
   time -- a product onboarding story.

---

## Cheap decisive test

Run TEST DL-1 (age-stratified recall profile) first.

Requirements: existing W_fast + W_slow infrastructure from prior CLS drill (if built);
otherwise: 30-min CPU run with 1000-item synthetic stream, age ledger lookup, 3-stratum
split at evaluation. Single metric per stratum.

Why this is decisive: if fast_only at fresh stratum = 0.70+, it confirms that fast is
working correctly but the test setup was evaluating too-old items. This diagnosis
eliminates L2-L5 as prerequisites and makes L1 (age-gated blend) the immediate fix.
If fast_only at fresh stratum < 0.55, capacity saturation is the bottleneck and L2
(k-sparse) or L5 (orthogonal) must come first.

DECISION TREE:
  DL-1 fast_fresh >= 0.70 -> implement L1 (age-gated blend) -> retest -> expect dual >= 0.975
  DL-1 fast_fresh < 0.55 -> run DL-2 (k-sparse) -> if passes, implement L2 then L1

---

## Citations (verified from search results this session, 12 total)

1. McClelland, McNaughton, O'Reilly (1995). Complementary learning systems. Psychological Review.
2. PMC9606815 (2022). Bidirectional CLS interactions for sequential memory consolidation.
3. Tse et al. (2007). Schemas and Memory Consolidation. Science 316:76.
4. PMC9337604 (2022). Assimilation of novel information into schemata.
5. PMC6902718 (2019). Schema-like learning acting through myelination.
6. Nature Communications 2025. Post-learning replay biased by reward-prediction signals.
7. PNAS 2117625118 (2022). Prediction errors disrupt hippocampal representations.
8. PMC3904133 (2014). CA3 pattern completion and dentate gyrus pattern separation.
9. Roy Soc Phil Trans B 379/1906 (2024). Synaptic tagging and capture.
10. SSRN 5377250 NeuroDream (2025). Sleep-inspired memory consolidation in neural networks.
11. arXiv:2507.11393 (2025). Neural network model of CLS: pattern separation and completion.
12. Springer Artificial Intelligence 2020. Prediction error-driven memory consolidation for CL.

---

## P estimates summary

| Lift path | P_deflated | Cost | Why |
|---|---|---|---|
| L1 age-gated blend | 0.45 | < 1 day | Directly addresses temporal complementarity deficit; age ledger already exists |
| L2 sparse-fast/dense-slow | 0.43 | < 1 day | DG pattern-separation precedent; raises fast_only ceiling |
| L3 prediction-error replay | 0.42 | < 1 day | SuRe 2025 NN precedent; directly creates complementary failure profiles |
| L4 schema-accelerated gate | 0.40 | < 1 day | Tse 2007 schema precedent; large effect on structured KBs |
| L5 orthogonal fast-write | 0.38 | 1 day | ADEPT continual learning precedent; cleanest interference fix |
| L6 reconsolidation bridge | 0.38 | 1 day | Kumaran 2016 bidirectional CLS; requires W_fast delta-W capability |
| L7 timescale-ratio sweep | 0.36 | < 1 day | Cheap diagnostic; may reveal alpha misconfiguration |
| L8 age-stratified eval | 0.35 | < 1 day | Diagnostic only; no code change needed; highest elimination value |
| Combined (L1+L2+L3) | 0.40 | 2-3 days | Three mechanisms address different failure modes; diminishing returns |

Novel-synthesis cap: 0.45. Combined P_deflated = 0.40 (below cap, as required).
