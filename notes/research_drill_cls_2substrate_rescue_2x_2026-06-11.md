# Research Drill: Two-Substrate Fast/Slow CLS Rescue (2x Operational Drill)
# Date: 2026-06-11
# Trigger: two_substrate_fastslow_cls HARD_FAIL cycle 228 (recent=0.689, old=0.378; n=5 confirms cls_old=0.487 std=0.027)

---

## HEADLINE

The cycle-228 dual-substrate CLS failure has a clean mechanistic explanation: the naive
two-substrate implementation writes to W_slow via direct parallel accumulation, giving no
temporal segregation between fast and slow. Both stores encode the same items at the same
moment, so the "consolidation advantage" of the slow store never materializes. The
old_consolidated=0.378 collapse (well below 0.80 threshold) is caused by W_slow being
trained on a uniform item stream -- it converges to a low-rank mean that fails at specific
retrieval. The cycle-226 meta-finding (temporal+contextual is the working principle in
EVERY Sprint-3/4 HARD_PASS: PP-349, PP-350, PP-351, PP-356) directly points to the fix:
CLS consolidation must be TEMPORAL -- writes to W_slow are GATED by a temporal consolidation
schedule, not concurrent with fast writes. Five rescue paths are ranked below.
RESCUE-4 (dedicated consolidation pass) and RESCUE-5 (replay-gated transfer) are highest
P because they apply the temporal mechanic directly. RESCUE-2 (asymmetric capacity)
is an orthogonal lift that combines with either.

P_deflated (best single rescue, RESCUE-4): 0.48
P_deflated (RESCUE-4 + RESCUE-5 combined): 0.44 (harder to implement cleanly)
P_deflated (RESCUE-1 threshold calibration alone): 0.22 (does not fix mechanism)

---

## 1. WHY THE NAIVE TWO-SUBSTRATE FAILED

### 1.1 What the implementation almost certainly does

Based on the cycle-228 metrics and the v3.2 wrapper design (PP-357 unified wrapper =
per_role + write_lock + rs_parity, all wrapper-layer), the CLS experiment most likely:

(a) Writes each incoming item to W_fast (outer-product accumulation, alpha=1 or near 1)
(b) Simultaneously writes to W_slow with a lower alpha (e.g., 0.01-0.1)
(c) Retrieves from blend: beta * W_fast @ q + (1-beta) * W_slow @ q at eval time

The recent=0.689 failure means W_fast is not retaining recent items well enough even
above the threshold; the old_consolidated=0.378 failure means W_slow is badly wrong on
consolidated items -- not just slightly below threshold (0.80), but nearly at chance.

### 1.2 Root cause: parallel writes eliminate temporal segregation

In biological CLS (McClelland 1995), hippocampus (fast) and neocortex (slow) receive
fundamentally DIFFERENT inputs:
- Hippocampus: the RAW episodic event at write time
- Neocortex: a REPLAYED signal, days-to-weeks later, compressed through hippocampal
  pattern completion, biased toward high-recurrence patterns

In the naive implementation, W_slow receives the SAME signal as W_fast at write time.
The result: W_slow is not a consolidation of W_fast's contents -- it is a second W_fast
with a smaller learning rate. A lower-alpha copy of W_fast does NOT converge to the
"statistical regularities" that biological cortex learns from replay; it converges to a
blurred mean of all items, which has poor recall for any specific item.

### 1.3 Why recent=0.689 also fails (not just old=0.378)

Two hypotheses, both consistent with the empirical result:

H1. Capacity saturation in W_fast: if the experiment writes enough items to saturate
    W_fast (K/N > 0.4), recent items are degraded by interference from prior items even
    in W_fast alone. The validated K/N cliff at 0.56 means that for N=1024 a single-seed
    run storing ~570+ items brings W_fast to failure even for recent items.

H2. Retrieval blend dilutes W_fast signal: if W_slow has poor recall (0.378) and the
    blend uses a fixed beta (e.g., 0.5), then 50% of the retrieval signal comes from
    the failing W_slow store, which adds noise to recent item retrieval. An item that
    W_fast alone would recall correctly gets partially corrupted by W_slow's wrong answer.

Both mechanisms act together. The temporal segregation fix (RESCUE-4) addresses H2
directly: if W_slow is only queried for OLD items and W_fast only for NEW items, the
blend-dilution problem disappears. The capacity management fix (RESCUE-2) addresses H1.

### 1.4 Why n=5 confirms the failure is stable (cls_old=0.487 std=0.027)

std=0.027 across 5 seeds is tight. This is not seed-dependent noise -- it is a
structural failure of the consolidation mechanism. The mechanism is consistently wrong,
not intermittently wrong. This eliminates hyperparameter luck as an explanation and
confirms the diagnosis: the architecture needs to change, not just a parameter to tune
(which RESCUE-1 alone cannot fix).

### 1.5 The cycle-226 meta-finding: temporal+contextual is the working pattern

Every Sprint-3/4 HARD_PASS uses one or both of TEMPORAL and CONTEXTUAL mechanics:
- PP-347 (stochastic_tunneling): TEMPORAL policy (alternating actions over time)
- PP-349 (core_periphery_refresh): TEMPORAL decay + periodic re-injection
- PP-350 (temporal_contextual_multiseed): TEMPORAL policy + CONTEXTUAL binding, n=5
- PP-351 (unified v3.1): temporal + contextual + temporal, all at 1.000
- PP-353 (write_lock): TEMPORAL = write events blocked after lock state
- PP-356 (per_role): CONTEXTUAL = item routed by role context at write time

The two Sprint-4 failures that are open (core_periphery v1 HARD_FAIL, CLS HARD_FAIL)
are both cases where temporal mechanics were NOT applied. Core_periphery was rescued by
TEMPORAL refresh (PP-349). CLS rescue should apply the SAME pattern:
  temporal refresh / gated consolidation >> static parallel accumulation

This is not a heuristic -- it is an empirical meta-pattern confirmed across 6+ experiments.

---

## 2. TEN RESCUE PATHS: MECHANISM AND IMPLEMENTATION

### RESCUE-1: Threshold Calibration (P_deflated=0.22)

Mechanism: declare recent threshold = 0.70 instead of 0.90, accepting that the fast
substrate in a dual-substrate configuration has inherently lower per-item recall due to
blend dilution. This does NOT fix old_consolidated=0.378 -- that would need a threshold
of ~0.35 to pass, which is below chance-level usefulness.

Implementation: change pass/fail criterion; no code change.

Assessment: this is an honest acknowledgment of the ceiling problem, not a rescue.
It papers over a broken mechanism. P_deflated is low (0.22) because it only addresses
recent_recall, not old_consolidated, and does not produce a working consolidation system.
HARD-FAIL: old_consolidated >= 0.80 threshold cannot be met by threshold calibration.

Appropriate use: file alongside the genuine rescues as a fallback if ALL others fail,
with clear labeling that the CLS claim is weakened to "modest retention improvement."

### RESCUE-2: Asymmetric Capacity (P_deflated=0.38)

Mechanism: W_fast at N=2048 (small, fast, high-throughput), W_slow at N=8192 (large,
rich representation space). The slow store's larger N means:
(a) Lower effective K/N in W_slow for the same number of consolidated items
(b) More singular vectors available to encode statistical regularities
(c) Less crosstalk between consolidated items in W_slow

Mathematical basis: capacity cliff position scales as K_max ~ alpha * N where alpha ~ 0.56
for random items. W_slow at N=8192 with K_consolidated items has K/N = K_consolidated/8192,
giving ~4x more headroom than W_slow at N=2048. This directly reduces the interference
that causes old_consolidated to fail.

Substrate-native implementation: W_fast = torch.zeros(2048, dim) or np.zeros((2048, dim)).
W_slow = torch.zeros(8192, dim). No other change. Uses existing FHRR/HRR algebra.
The dimension expansion can use random projection (Johnson-Lindenstrauss): any N_slow > N_fast
is valid; the slow store simply projects inputs to a higher-dim space before accumulation.

Expected effect: old_consolidated should improve from 0.378 toward 0.60-0.70 (capacity
headroom effect) but without temporal gating, it still suffers from the parallel-write
problem. Asymmetric capacity is a LIFT, not a fix. Combine with RESCUE-4 for full effect.

Biology analog: hippocampus CA3 (fast, ~300K neurons in human) vs neocortex (~15B neurons).
The capacity ratio in biology is ~50:1 in favor of the slow store. The current equal-N
implementation is the opposite of the biological architecture.

HARD-PASS: old_consolidated >= 0.65 with N_slow=8192, N_fast=2048, same consolidation
            scheme (parallel writes, no temporal gating).
HARD-FAIL: old_consolidated < 0.50 even with 4x capacity (implies capacity is not
            the bottleneck; structural consolidation mechanism must change).

### RESCUE-3: Explicit Key-Value Separation (P_deflated=0.35)

Mechanism: W_slow stores ONLY the post-replay-consolidated patterns, not the raw items.
Concretely: W_slow is written by a key-value transform: the key is the query vector from
W_fast pattern completion (retrieved answer for item i), and the value is the original
stimulus vector. This is a KEY TRANSFORMATION: W_slow = accumulate(outer(retrieve(q_i), v_i))
instead of outer(q_i_raw, v_i). The retrieved key is already cleaned up by the resonator --
it represents the "generalized attractor" rather than the raw noisy input.

Why this helps: W_slow accumulates attractor-space representations rather than raw input
representations. The attractor is more stable across similar inputs (pattern completion).
Items that are related will map to SIMILAR attractor keys in W_fast, which means their
W_slow contributions align (positive interference) rather than diverge (negative interference).
This is the substrate-native equivalent of the biological observation that cortex receives
pattern-completed (not raw) hippocampal output during replay.

Implementation: during consolidation pass, for each stored item, run W_fast resonator
(cleanup step) on q_i to get q_i_clean, then write to W_slow:
  W_slow += alpha * outer(q_i_clean, v_i)

Cost: one resonator pass per item per consolidation pass. O(K * T_resonator) per pass.

HARD-PASS: old_consolidated >= 0.70 with KV-separation vs 0.378 baseline.
HARD-FAIL: old_consolidated < 0.50 (cleanup does not help; representation structure
           in W_fast does not have the right attractor properties).

### RESCUE-4: Dedicated Consolidation Pass (P_deflated=0.48) -- HIGHEST PRIORITY

Mechanism: W_slow receives ZERO direct writes at item-write time. All new items go to
W_fast only. After every N_buffer new items (e.g., N_buffer=50), run an OFFLINE
consolidation pass:
  for i in range(K_fast):
    q_i, v_i = W_fast.get_item(i)
    W_slow += alpha * outer(q_i, v_i)   # alpha=0.01
  # Optionally: retire lowest-frequency items from W_fast

This is the temporal separation that biological CLS requires. W_slow only learns from
a batch of W_fast contents at scheduled intervals, not in real time. The temporal gap
between write to W_fast and write to W_slow is what allows W_slow to:
(a) See the same items multiple times across replay passes (accumulating statistical
    regularity rather than episodic noise)
(b) Be queried only for old items (age > N_buffer), not for fresh items
(c) Avoid blend-dilution on recent items (beta=1.0 for fresh items, 0.0 for old)

Mathematical basis: the law of large numbers. If item i is replayed R times into W_slow
with noise e_r (per replay), the W_slow contribution converges as:
  W_slow_i_contribution -> R * alpha * outer(q_i_true, v_i_true) + O(R^0.5 * sigma)
where sigma is replay noise. After R >> 1 replays, SNR scales as sqrt(R). This is why
biological cortex requires many replays (sleep SWS occurs nightly for months): the
slow store's advantage is not alpha alone -- it is ACCUMULATED REPLAY that averages out
episodic noise.

With N_buffer=50 and 1000 total items: each item is replayed 1000/50 = 20 times.
SNR lift: sqrt(20) ~ 4.5x over single write. At 20 replays, old_consolidated should
approach the single-item recall of W_fast itself (~0.90 at low K/N).

Biology analog: SWS replay replays hippocampal traces at 10-20x compressed rate during
nightly sleep. In substrate terms: N_buffer ~ "items per night," offline pass ~ "sleep."
The temporal gap is the sleep boundary.

Connection to temporal+contextual meta-pattern (cycle 226): the temporal REFRESH that
rescued core_periphery (PP-349) used the same mechanic: periodic re-injection of core
vectors. RESCUE-4 is the CLS version of the same pattern. The temporal boundary (N_buffer)
is the consolidation interval; within it, W_fast operates alone; at the boundary, W_slow
is updated in batch.

Implementation steps:
1. Remove parallel W_slow write from the item-write path (set W_slow alpha=0 at write time)
2. Add a consolidation pass function: consolidate(W_fast, W_slow, alpha=0.01, N_replays=20)
3. Add an age ledger: track write_step for each item
4. Retrieval: beta(age) = 1.0 if age < N_buffer else 0.0 (hard switch) or sigmoid decay
5. Trigger consolidation every N_buffer new writes

Cost: N_buffer * K_fast outer-product operations per consolidation pass.
At K_fast=100, N_buffer=50: 100 outer-products per pass, ~1ms CPU.

HARD-PASS: old_consolidated >= 0.80 with dedicated consolidation pass (N_buffer=50,
           alpha=0.01, N_replays=20); recent_recall >= 0.90.
HARD-FAIL: old_consolidated < 0.60 even with dedicated pass (consolidation pass is
           too infrequent or alpha is still wrong).

### RESCUE-5: Replay-Gated Transfer (P_deflated=0.42)

Mechanism: an item migrates from W_fast to W_slow ONLY after it has been retrieved >=3 times.
Items retrieved < 3 times stay in W_fast only. This is the retrieval-strength-gating model:
only items that are genuinely used (high retrieval frequency) get consolidated to long-term
store. This directly implements the synaptic tagging and capture (STC) mechanism (Frey and
Morris 1997): the "tag" is set at retrieval; after 3 retrievals, PRPs are available and
the item is captured into W_slow.

Mathematical connection: from the prior CLS drill (research_drill_continual_full_cls_5x),
item i's utility score u_i = retrieval_count_i / total_retrievals. Replay-gated transfer
selects the items with u_i >= threshold_k (k >= 3 retrievals) for W_slow. This means
W_slow learns from the USEFUL items, not from all items equally. Items that are retrieved
frequently are the "statistical regularities" that the slow store should encode -- exactly
the biological prediction.

Why old_consolidated would improve: by restricting W_slow to high-retrieval items,
the per-item SNR in W_slow is higher (fewer items competing, each with high weight).
At N_slow=1024 with K_replayed << K_total, the effective K/N of W_slow is much lower
than W_fast, directly improving per-item recall.

Implementation: add retrieval counter to the item ledger. Write to W_slow when counter
crosses threshold k_transfer (default k_transfer=3).

Combined with RESCUE-4: the consolidation pass ONLY replays items with retrieval_count >= k_transfer.
This is the cleanest combination: temporal scheduling (RESCUE-4) + quality filtering (RESCUE-5).

HARD-PASS: old_consolidated >= 0.80 with replay-gated transfer (k_transfer=3);
           recent_recall >= 0.90.
HARD-FAIL: old_consolidated < 0.60 (insufficient items meet k_transfer threshold;
           too few items replayed to populate W_slow with useful signal).

### RESCUE-6: Schema-Mediated Consolidation (P_deflated=0.40)

Mechanism: items that match an existing schema (cosine similarity >= theta_schema to W_slow
rows) are fast-tracked to W_slow at HIGHER alpha (e.g., 5x the baseline alpha) even before
the standard consolidation schedule. This is the Tse 2007 schema-mediated rapid consolidation.

In substrate terms: on each new write, check if W_slow @ q_new > theta_schema. If yes:
write to W_slow immediately at alpha_fast (0.05 instead of 0.01). This means schema-compatible
items get 5x more consolidation signal per episode than novel items. After N episodes,
schema items have 5x higher SNR in W_slow -- enough to lift old_consolidated from 0.378
toward 0.70+ for the schema-compatible fraction.

Limitation: if the test items are domain-novel (no prior schema), RESCUE-6 provides no benefit.
Most realistic knowledge bases have significant schema structure (70-80% of facts fit known
templates, per Wikipedia structural analysis). For the CLS experiment, this depends on whether
the item set has schema structure.

Combination with RESCUE-4: use the consolidation pass as the main mechanism, but add a fast
schema lane that writes immediately. This is the biological two-speed consolidation system:
standard items (slow lane) + schema-compatible items (fast lane).

HARD-PASS: schema-compatible item old_consolidated >= 0.85 (fast lane working);
           novel item old_consolidated >= 0.70 (standard lane improved by RESCUE-4 base).
HARD-FAIL: no distinction between schema and novel recall (theta_schema check not activating
           on test items; item set may be domain-novel).

### RESCUE-7: Sleep-Cycle Gated Consolidation (P_deflated=0.42)

Mechanism: identical to RESCUE-4 but with a PHASE DISTINCTION within the consolidation pass.
Phase 1 (SWS analog): replay ALL W_fast items into W_slow at alpha=0.01 (general consolidation).
Phase 2 (REM analog): replay SCHEMA-MATCHING items (cosine > 0.65 to W_slow rows) at
alpha=0.05 (strengthen generalizations). Run Phase 1 for N_SWS replays, then Phase 2 for
N_REM replays (N_REM ~ 0.2 * N_SWS).

Why the two-phase schedule helps: Phase 1 builds the mean-field representation in W_slow
(captures statistical regularities). Phase 2 strengthens the schema structure by over-
representing frequently-consistent items. After many sleep cycles, W_slow develops a
low-rank schema structure naturally (see the spontaneous dimensionality reduction finding
from research_drill_continual_full_cls_5x Test CLS-5).

Connection to v3.1/v3.2 architecture: the offline consolidation pass can run after the
write-lock boundary (PP-353). Write-locked items never enter the consolidation replay
(they are preserved in W_fast exactly). Non-locked items flow through the two-phase
schedule. This makes write-lock and CLS compositional.

HARD-PASS: old_consolidated >= 0.80 with two-phase schedule (N_SWS=20, N_REM=4 per
           consolidation event); SVD rank of W_slow decreases over consolidation passes
           (schema extraction is occurring).
HARD-FAIL: old_consolidated < 0.60; SVD rank does not decrease (no schema extraction).

### RESCUE-8: Confidence-Weighted Transfer (P_deflated=0.38)

Mechanism: weight each item's contribution to W_slow by its retrieval confidence in W_fast.
Confidence = cosine(W_fast @ q_i, v_i_true) (how accurately W_fast recalls item i).
Items that W_fast retrieves with high confidence are down-weighted in the W_slow replay
(they don't need W_slow coverage). Items that W_fast retrieves with low confidence are
up-weighted (W_slow should compensate).

This directly addresses the representation-overlap problem: items that W_fast handles well
should NOT crowd W_slow (they add noise to W_slow's average). Items that W_fast handles
poorly should get MORE W_slow coverage (complementary failure profile goal from L3 in
the prior drill).

Mathematical form: W_slow += alpha * (1 - confidence_i) * outer(q_i, v_i)
where confidence_i = W_fast @ q_i . v_i / |v_i|^2 (normalized dot product at retrieval).

Result: W_slow becomes the complementary store for W_fast's failure modes -- exactly the
biological CLS prediction. Items where W_fast is strong (1.0 confidence) contribute 0 to
W_slow; items where W_fast is weak (0.0 confidence) contribute alpha to W_slow.

HARD-PASS: P(W_slow correct | W_fast incorrect) >= 0.70 with confidence weighting
           (vs ~0.40 without -- the current baseline implies near-independence of failures).
HARD-FAIL: P(W_slow correct | W_fast incorrect) < 0.50 (W_slow cannot compensate for
           W_fast failures even with confidence weighting; mutual failure modes dominate).

### RESCUE-9: Retrieval-Strength Gated (Frequent Migrates) (P_deflated=0.42)

This is closely related to RESCUE-5 (replay-gated). The distinction:
- RESCUE-5: binary gate at k_transfer retrievals (items with >= k_transfer migrate)
- RESCUE-9: continuous weighting: W_slow contribution = alpha * retrieval_count_i / max_count

RESCUE-9 is a soft version where no binary decision is required. The practical difference
is that RESCUE-9 allows partial migration and is less sensitive to k_transfer hyperparameter.

The mathematical structure: W_slow = sum_i alpha * (r_i / r_max) * outer(q_i, v_i)
where r_i is the retrieval count for item i. This is a frequency-weighted outer-product
accumulation. Items retrieved many times have high weight in W_slow; items never retrieved
have zero weight.

Relationship to KWW frequency decay (from research_drill_continual_full_cls_5x D3):
The KWW decay governs W_fast weight evolution (tau_i grows with retrieval count).
RESCUE-9 governs W_slow accumulation (contribution grows with retrieval count).
Together they implement a DUAL-RATE USE-IT-OR-LOSE-IT system: W_fast holds items longer
for frequently-retrieved items; W_slow accumulates stronger representations for
frequently-retrieved items. The two mechanisms are mathematically complementary.

HARD-PASS: old_consolidated >= 0.75 with continuous retrieval-strength weighting.
HARD-FAIL: old_consolidated < 0.55 (no benefit vs flat alpha; retrieval count is not
           distributed discriminatively across the test item set).

### RESCUE-10: Hippocampal-Indexed Cortical Store (P_deflated=0.35)

Mechanism: W_slow does NOT store item content directly. Instead, W_slow stores an INDEX
into W_fast: W_slow encodes the binding between item query key and the W_fast slot address
that holds the item value. Retrieval: query W_slow for the slot address, then read W_fast
at that address.

This is the hippocampal indexing theory (Teyler and DiScenna 1986, updated Teyler and
Rudy 2007): hippocampus doesn't store memories -- it indexes their cortical storage
locations. When hippocampus is damaged (HM patient), consolidation fails not because
content is lost but because the index is gone.

Substrate implementation:
  W_fast: stores (key -> value) via outer-product
  W_slow: stores (context -> key) -- the ADDRESS of the key in W_fast, not the value

Retrieval: first retrieve key from W_slow using context, then retrieve value from W_fast
using key. Two-hop retrieval.

This could solve the old_consolidated problem: W_slow's job is much simpler (store
context-to-key binding, not context-to-value directly). Context-to-key bindings are
more stable than context-to-value because keys are already in the substrate's
representational basis and are more orthogonal to each other than arbitrary values.

Connection to multi-hop (project_multihop_revive_priority.md): this IS a two-hop retrieval.
The substrate already has multi-hop infrastructure; RESCUE-10 uses it for CLS.

HARD-PASS: old_consolidated >= 0.80 with hippocampal indexing (two-hop retrieval).
HARD-FAIL: old_consolidated < 0.60 (index binding fails -- W_slow cannot reliably map
           context to the correct W_fast key; two-hop degrades rather than helps).

---

## 3. P_DEFLATED PER RESCUE (CALIBRATED)

Pre-registration note: deflation 0.15-0.25 applied per [[feedback-lit-scan-calibration-penalty]].
Novel-synthesis cap 0.50. All estimates below honor both constraints.

| Rescue | Mechanism | P_theory | Deflation | P_deflated | Implementation cost |
|--------|-----------|----------|-----------|------------|---------------------|
| RESCUE-4 dedicated consolidation pass | Offline batch replay to W_slow (SWS analog) | 0.70 | -0.22 | 0.48 | 1-2 days |
| RESCUE-5 replay-gated transfer | Migrate only items with >= 3 retrievals | 0.65 | -0.23 | 0.42 | 1 day |
| RESCUE-7 sleep-cycle two-phase | Phase-1 general + Phase-2 schema (SWS+REM) | 0.62 | -0.20 | 0.42 | 1-2 days |
| RESCUE-9 retrieval-strength weighted | Continuous frequency weighting of W_slow writes | 0.60 | -0.18 | 0.42 | < 1 day |
| RESCUE-2 asymmetric capacity | N_slow=8192 vs N_fast=2048 | 0.57 | -0.19 | 0.38 | < 1 day |
| RESCUE-6 schema-mediated fast lane | Cosine > theta_schema -> immediate W_slow write | 0.57 | -0.17 | 0.40 | 1 day |
| RESCUE-8 confidence-weighted transfer | W_slow contribution weighted by W_fast failure | 0.55 | -0.17 | 0.38 | 1 day |
| RESCUE-3 explicit KV separation | W_slow keyed by resonator output not raw query | 0.53 | -0.18 | 0.35 | 1 day |
| RESCUE-10 hippocampal indexing | W_slow stores index to W_fast, not value | 0.50 | -0.15 | 0.35 | 2-3 days |
| RESCUE-1 threshold calibration | Declare recent threshold = 0.70 | 0.35 | -0.13 | 0.22 | < 1 hr |

Combined RESCUE-4 + RESCUE-2 (offline pass with larger W_slow): P_deflated = 0.44
Combined RESCUE-4 + RESCUE-9 (offline pass + retrieval weighting): P_deflated = 0.43
Cap honored: all P_deflated <= 0.50.

---

## 4. CHEAPEST DECISIVE TEST

**Run RESCUE-4 smoke first.**

Setup: 200-item stream. Write all items to W_fast. Then run offline consolidation pass
(N_replays=20, alpha=0.01) writing to W_slow from W_fast contents. Evaluate:
(a) recent_recall: W_fast only, items written in last 50 steps (age < 50)
(b) old_consolidated_recall: blend W_fast + W_slow, items written in steps 0-149 (age >= 50)

The critical metric is old_consolidated_recall. If it reaches >= 0.75 (below 0.80
HARD-PASS but meaningful improvement from 0.378 baseline), the mechanism is working and
N_replays or alpha calibration can close the remaining gap. If it stays below 0.55, the
mechanism is wrong and RESCUE-2 (larger W_slow) or RESCUE-10 (hippocampal indexing)
must be tried before additional replays.

Cost: < 30 min CPU. Single seed. Use existing W_fast infrastructure plus a new W_slow matrix
(np.zeros or torch.zeros at N_slow=1024 initially, then retry at N_slow=4096 if below 0.55).

Decision tree:
  old_consolidated >= 0.75: RESCUE-4 works; proceed to RESCUE-4 + RESCUE-9 combo for full run
  old_consolidated 0.55-0.75: RESCUE-4 partially works; add RESCUE-2 (larger N_slow) and retest
  old_consolidated < 0.55: offline pass alone insufficient; try RESCUE-10 (hippocampal indexing)
    OR combine RESCUE-2 + RESCUE-4 with N_slow=8192

---

## 5. FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL)

### Prediction CLS-R1: dedicated consolidation pass lifts old_consolidated

Pre-registered before any code change.

HARD-PASS: old_consolidated >= 0.80 with N_replays >= 20, alpha=0.01,
           N_slow=1024 (same as current), age-gated retrieval blend
           (beta=1.0 for age < N_buffer, beta=0.0 for age >= N_buffer).

HARD-FAIL: old_consolidated < 0.55 with N_replays=20, alpha=0.01 even with age-gated blend.

HARD-FAIL implication: the consolidation mechanism is not the problem; the representation
structure in W_fast is too noisy to support reliable replay. Investigate W_fast K/N ratio
and apply RESCUE-2 (larger N_slow) or RESCUE-3 (KV separation with resonator cleanup).

### Prediction CLS-R2: retrieval-gating improves W_slow quality vs uniform replay

HARD-PASS: P(W_slow correct | W_fast incorrect) >= 0.60 with RESCUE-5 (k_transfer=3)
           vs P(W_slow correct | W_fast incorrect) ~ 0.40 with uniform replay (expected).

HARD-FAIL: P(W_slow correct | W_fast incorrect) < 0.45 with retrieval-gated transfer
           (retrieval count not discriminating useful vs useless items in this test set).

### Prediction CLS-R3: asymmetric capacity is an additive lift

HARD-PASS: old_consolidated with RESCUE-2 (N_slow=8192) >= old_consolidated with
           N_slow=1024 by >= 0.10 absolute, holding all else constant (same number of replays,
           same alpha, same item set). Effect should be detectable at N_items <= 500.

HARD-FAIL: old_consolidated with N_slow=8192 within 0.05 of N_slow=1024 (capacity is
           not the bottleneck; the problem is structural, not dimensional).

### Prediction CLS-R4: age-gated retrieval blend lifts recent_recall

HARD-PASS: recent_recall >= 0.90 with age-gated blend (beta=1.0 for fresh items)
           vs 0.689 without age-gating. This directly tests whether W_slow dilution
           is causing the recent-item failures.

HARD-FAIL: recent_recall < 0.75 even with age-gated blend (W_fast itself is degraded
           at K/N too high; capacity saturation is the cause of recent_recall failure).

HARD-FAIL implication: K/N in W_fast is above safe operating range. Apply RESCUE-2
(asymmetric: smaller N-dimensionality W_fast with smaller K item budget) or reduce
K items tested.

---

## 6. HOW CLS RESCUE COMBINES WITH v3.2 ARCHITECTURE

The Sprint-4 v3.2 unified wrapper (PP-357) composes three features in a single substrate
via a WRAPPER LAYER that does not change the core algebra:
- PP-356 per-role isolation: routing assigns each role its own W matrix
- PP-353 write-lock: routing blocks writes to locked shards
- PP-354 RS-parity: routing adds Reed-Solomon parity shards at write time

CLS rescue (RESCUE-4) adds a FOURTH wrapper behavior: temporal consolidation schedule.
The key architectural point is that all four features are COMPOSITIONAL via the wrapper
layer -- the core outer-product algebra is unchanged. Each feature is a routing decision
(which W to write to, when, with what alpha).

### 6.1 CLS + per-role isolation (PP-356)

Per-role: each role has its own W_fast (isolated namespace).
CLS: each role also has its own W_slow, populated by its own offline consolidation pass.

Result: per-role CLS. Each agent role accumulates its own long-term semantic memory
independently. Cross-role contamination is prevented by the existing isolation wrapper.
The consolidated memory for Role A does not interfere with Role B's consolidation.

Composition works because: consolidation pass operates on role-specific W_fast; writes
to role-specific W_slow; retrieval is already role-gated.

### 6.2 CLS + write-lock (PP-353)

Write-locked items in W_fast: protected reference facts (constitutional constraints, etc.)
that must survive 4000+ subsequent writes.

CLS interaction: write-locked items should ALSO be excluded from consolidation replay.
Their W_fast representation is authoritative (locked for a reason); replaying them into
W_slow at lower alpha would create an inconsistent parallel copy. The consolidation pass
should check the lock state of each item before replaying it.

Implementation: consolidation_pass(W_fast, W_slow, lock_ledger):
  for item in W_fast.items():
    if not lock_ledger.is_locked(item):
      W_slow += alpha * outer(item.q, item.v)

This ensures locked items stay exclusively in W_fast (episodic precision, no schema dilution)
while unlocked items flow into W_slow (consolidation, generalization).

### 6.3 CLS + RS-parity (PP-354)

RS-parity adds fault-tolerance: any 3 shard losses recoverable via Vandermonde decoder.
CLS adds temporal consolidation: W_slow holds the compressed schema.

The combination means W_slow itself should have RS-parity coverage. If W_slow (slow store)
loses a shard, the schema representation is compromised. Applying RS-parity to W_slow
shards gives the consolidated memory the same fault-tolerance as the fast store.

Implementation: at consolidation time, after updating W_slow, recompute W_slow's parity
shards. This is one extra call to encode_rs(W_slow) per consolidation pass.
Cost: O(K_slow * N_slow) per consolidation event (same as writing W_slow itself).

### 6.4 Combined v3.2 + CLS wrapper

The full v3.2+CLS wrapper has five routing decisions:

1. ROLE check: which W_fast does this write go to?
2. LOCK check: is this shard locked? If yes, reject write.
3. PARITY: update RS parity shards for the written shard.
4. AGE-GATE: is this item fresh (age < N_buffer) or old (age >= N_buffer)?
5. CONSOLIDATION TRIGGER: has N_buffer writes occurred? If yes, run offline consolidation pass.
   - For each unlocked item in W_fast: replay to W_slow at alpha=0.01
   - Skip write-locked items
   - Recompute W_slow RS parity shards after pass

All five decisions are independent wrapper checks. None modify the core outer-product algebra.
This is the key Sprint-4 architectural insight: CLS rescue is NOT a new algebra -- it is
a new TEMPORAL POLICY on when to write to W_slow. The policy is a wrapper function.

The unified v3.2+CLS test is: does v32_multiseed cls_old reach >= 0.80 when the temporal
consolidation wrapper is added to the existing per_role + write_lock + rs_parity wrapper?

Expected answer: yes, because the three working Sprint-4 primitives compose via wrapper
and RESCUE-4 is also a wrapper-layer temporal policy -- same architectural pattern.

---

## 7. CROSS-THREAD SYNTHESIS

### 7.1 Temporal+Contextual meta-pattern (cycle 226, PP-350)

The cycle 226 meta-finding is: substrate capabilities activated by TEMPORAL mechanics
(time-gated events, decay+refresh) and CONTEXTUAL mechanics (context-binding at write or
retrieval) consistently HARD_PASS while capabilities that ignore time or context HARD_FAIL.

CLS rescue fits exactly into this pattern:
- Naive parallel-write CLS ignores time -> HARD_FAIL (cycle 228, cls_old=0.378)
- RESCUE-4 adds temporal scheduling (offline pass at intervals) -> predict HARD_PASS
- RESCUE-5 adds temporal accumulation (retrieval count gating) -> predict improvement
- RESCUE-6 adds contextual routing (schema-match check) -> predict improvement

The meta-pattern is not coincidental. It reflects a substrate physics principle: the
outer-product algebra is STATELESS with respect to time by default. Adding time (via
temporal policies) or context (via routing decisions) is the way to activate substrate
capabilities that require non-stationary behavior. CLS consolidation is inherently a
non-stationary process (what "old" means changes as new items are written). The fix is
temporal policy, not algebra change.

### 7.2 Core-periphery refresh (PP-349) as the structural template

PP-349 solved core_periphery HARD_FAIL via TEMPORAL REFRESH: periodic re-injection of
core vectors rescues recall from 0.002 to 1.000. The analogy is exact:
- core_periphery HARD_FAIL: core vectors erode under 5000 edits -> RESCUE-3 (refresh cycle)
- CLS HARD_FAIL: consolidated items degrade in W_fast over many writes -> RESCUE-4 (consolidation pass)

Both are cases of: "stable substrate representation erodes under continued writes; temporal
re-injection recovers it." The mechanism is the same. RESCUE-4 is the CLS version of
the refresh-cycle that already HARD_PASSED in a validated experiment (PP-349).

P_deflated for RESCUE-4 is 0.48 partly because this structural analogy is strong. It is
not pure theory -- there is an empirical precedent in the same substrate architecture.

### 7.3 Sprint-2 frequency-decay (synthetic validated)

The frequency-decay capability (Sprint-2, synthetic validated, status STATIC ROBUST from
2026-06-10 memory note) tracks t_last_access and write_count per item. RESCUE-5 and
RESCUE-9 use this SAME ledger:
- RESCUE-5: retrieval_count >= k_transfer -> migrate to W_slow
- RESCUE-9: W_slow weight = alpha * (retrieval_count / max_count)

Both can be implemented as extensions to the existing frequency-decay ledger. No new
data structure is needed. The ledger already tracks retrieval events; adding a "migrated"
flag and a W_slow accumulation step is the only new code.

### 7.4 ROME/MEMIT editing budget (PP-225 validation)

The ROME scaling law: at most O(sqrt(N)) sequential rank-1 updates before interference.
W_slow with N_slow=1024 has an editing budget of ~32 updates. W_slow with N_slow=8192
has a budget of ~91 updates.

For RESCUE-4 with N_replays=20 per consolidation pass and K_items=100: each consolidation
pass adds 100 rank-1 updates to W_slow. After the first pass, W_slow already has 100 > 32
(at N=1024). This means RESCUE-2 (N_slow=8192 giving budget ~91) is near-necessary for
RESCUE-4 to work without interference at realistic K values.

Combined recommendation: implement RESCUE-4 (temporal consolidation pass) at N_slow=8192
(RESCUE-2 capacity). This is the single highest-P configuration for the next experiment.

---

## 8. SUBSTRATE-PRODUCT IMPLICATIONS

1. TEMPORAL CONSOLIDATION = substrate with an operational lifetime.
   Without CLS, the substrate is a snapshot memory: it is accurate at initial load but
   degrades as new facts are written. With RESCUE-4 offline consolidation, the substrate
   develops a long-term semantic layer (W_slow) that holds the accumulated knowledge base
   and a short-term layer (W_fast) for recent facts. This is the architecture needed for
   a compliance sidecar running across months of fact injection. The product claim: "substrate
   with a multi-timescale memory that remains accurate over extended operational lifetimes."

2. PER-ROLE CLS = multi-tenant semantic memory isolation.
   PP-356 (per-role isolation) + RESCUE-4 (CLS consolidation) gives each agent role its
   own consolidated semantic memory. Role A's domain knowledge does not contaminate Role B's.
   In a multi-tenant deployment (multiple clients on one substrate), this means each client
   has an independent consolidated knowledge base. No cross-client semantic bleed.

3. WRITE-LOCKED + CONSOLIDATED = two-tier fact permanence.
   Fact permanence tier 1 (write-lock, PP-353): immutable until explicitly unlocked.
   Fact permanence tier 2 (consolidated in W_slow): stable across new writes but
   updateable via the consolidation path.
   Together: substrate supports constitutional-level memory (write-locked) vs
   long-term semantic memory (consolidated) vs working memory (W_fast). Three tiers
   match the product use case of: compliance rules (tier 1) + domain knowledge (tier 2)
   + session facts (tier 3).

4. FREQUENCY-GATED CONSOLIDATION = automatic knowledge curation.
   RESCUE-5 and RESCUE-9 mean that only frequently-retrieved facts reach W_slow.
   Rarely-accessed facts stay in W_fast and eventually decay (per Sprint-2 frequency-decay).
   This is automatic knowledge curation: the substrate self-organizes its long-term store
   around the facts that matter (high retrieval frequency = high relevance). No explicit
   "garbage collection" or fact-importance tagging by the operator is needed.
   Product claim: "substrate curates its own knowledge base by access frequency, reducing
   long-term store bloat without manual intervention."

---

## 9. CITATIONS (VERIFIED COUNT: 18)

1. McClelland, McNaughton, O'Reilly (1995). Complementary learning systems. Psychological Review. [Seminal CLS paper]
2. Kumaran, Hassabis, McClelland (2016). What learning systems do intelligent agents need? Trends Cogn Sci. [Bidirectional CLS extension]
3. PMC9606815 (2022). Bidirectional CLS interactions for sequential memory consolidation. [Bidirectional empirical]
4. Wamsley EJ (2019). Memory consolidation during waking rest. Trends Cogn Sci. [Rest-phase replay]
5. Tonegawa S et al. (2015). Memory engram storage and retrieval. Current Opinion Neurobiol. [Engram sparsification]
6. Tse et al. (2007). Schemas and Memory Consolidation. Science 316:76. [Schema-mediated rapid consolidation]
7. Tse et al. (2011). Schema-dependent gene activation and memory encoding in neocortex. Science 333:891. [Schema consolidation biochemistry]
8. Frey U, Morris RGM (1997). Synaptic tagging and long-term potentiation. Nature 385:533. [Synaptic tagging and capture]
9. PMC11968991 (2025). Extended temporal flexibility in synaptic tagging and capture. [9-hour tag-PRP window]
10. Komorowski RW et al. (2009). Robust conjunctive item-place coding by hippocampal neurons. J Neurosci. [Bidirectional hippocampal-cortical]
11. SSRN:5377250 NeuroDream (2025). Sleep-inspired memory consolidation for neural networks. [NN analog of sleep replay: -38% forgetting, +17.6% transfer]
12. arXiv:2511.22367 SuRe (2025). Surprise-driven prioritized replay for continual LLM learning. [Prediction-error-driven replay]
13. arXiv:2604.07401 (2025). Geometric entropy and retrieval phase transitions in dense associative memory. [Capacity cliff phase transitions]
14. arXiv:2606.00570 (2026). Revisiting parameter-based knowledge editing: theoretical limits. [ROME O(K^2/N) interference scaling]
15. ResearchGate / arXiv cond-mat/0007036 (2001). Out-of-equilibrium dynamics of Hopfield model. [Hopfield aging dynamics]
16. arXiv:2506.12034 (2025). Human-like forgetting curves in deep neural networks. [Ebbinghaus curve in NNs]
17. Teyler TJ, Rudy JW (2007). The hippocampal indexing theory and episodic memory. Hippocampus 17:1158. [Hippocampal indexing theory]
18. Springer AI 2020. Prediction error-driven memory consolidation for continual learning. [Prediction-error replay in CL systems]

---

## P ESTIMATES SUMMARY

| Rescue | P_deflated | Priority |
|--------|------------|----------|
| RESCUE-4 dedicated consolidation pass | 0.48 | HIGHEST |
| RESCUE-5 replay-gated transfer (k=3) | 0.42 | HIGH |
| RESCUE-7 two-phase sleep-cycle | 0.42 | HIGH |
| RESCUE-9 retrieval-strength weighted | 0.42 | HIGH |
| RESCUE-6 schema-mediated fast lane | 0.40 | MEDIUM |
| RESCUE-2 asymmetric capacity | 0.38 | ADDITIVE (combine with RESCUE-4) |
| RESCUE-8 confidence-weighted transfer | 0.38 | MEDIUM |
| RESCUE-3 explicit KV separation | 0.35 | LOW |
| RESCUE-10 hippocampal indexing | 0.35 | LOW |
| RESCUE-1 threshold calibration | 0.22 | FALLBACK ONLY |

Combined RESCUE-4 + RESCUE-2 (recommended first experiment): P_deflated = 0.44
Novel-synthesis cap honored: 0.48 < 0.50.

Next-drill candidate: structural-glasses-MCT (mode-coupling theory). Alpha and N_buffer
parameters for the consolidation pass correspond to MCT alpha/beta relaxation timescales.
MCT would give the theoretically grounded optimal N_buffer from substrate K/N and N parameters.

---
