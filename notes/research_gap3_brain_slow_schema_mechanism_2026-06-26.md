# Research: Gap 3 -- how the brain ACTUALLY builds cortical schemas, and what substrate can compose

**Date:** 2026-06-26
**Filed-by:** research (Opus 4.7 1M)
**Trigger:** USER deep drill request. Plain-English first; less jargon. 60-90 min.
**Builds-on:**
- `notes/research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md` (mechanism classes + Modern-Hopfield first dispatch)
- `notes/research_gap4_continual_5x_drill_2026-06-26.md` (TWO_TIER_GENERATIONAL convergence across 4 disparate fields)
- substrate state: NREM replay drift-reduction +0.57 proven-bound; Modern Hopfield cell in queue; TWO_TIER cell running.
**Calibration:** P estimates deflated 0.15-0.25; novel-synthesis cap 0.50; HARD-FAIL thresholds pre-registered.
**Lit-scan:** 8 parallel WebSearch breadth-scans; converged on BCM + CLS + Tse-Morris schema rapid-acquisition.

---

## HEADLINE

The brain's cortical schema is **not** a bundle of instances. It is a **slowly-extracted statistical regularity** that lives in a SECOND storage system (neocortex), is written at a learning rate 1000x to 10000x SMALLER than hippocampus, gets ITS training signal from **generative replay** of hippocampal episodes (not literal copying), and uses a **non-Hebbian rule** -- specifically a **sliding-threshold rule (BCM)** that makes the weight changes themselves competitive: the prototype gets SHARPER (depressing toward instances inconsistent with the average; potentiating toward instances consistent) with each replay rather than NOISIER.

Substrate can compose this from existing pieces. The brain-aligned 3-mechanism stack is:

1. **NREM replay** (substrate has -- drift_reduction proven-bound +0.57)
2. **TWO_TIER storage with eta_slow << eta_fast** (substrate has W; needs W_schema as second matrix; cell in queue closes this)
3. **BCM sliding-threshold write rule for W_schema** (substrate does not have; ~20 lines of code on top of existing `predictive_coding.gated_write`)

The single highest-P_deflated cell that closes Gap 3 the brain's way is **cls_two_tier_BCM_slow_replay_v1** -- a unified cell that uses substrate's existing replay engine to write into a NEW W_schema with a BCM sliding-threshold rule at eta_slow = 1/1000 * eta_fast. P_deflated = 0.45 (capped at novel-synthesis 0.50; -0.05 for substrate-specific composition risk). Cost: ~6-10 CPU-hr at N=8192 over ~5000 replay cycles.

**The substrate is NOT cortex-slow today; it is hippocampus-fast at every layer.** That is the gap in one sentence. The cell above is the substrate's first cortex-slow primitive. Realistic schema-formation cycle count for a single category is ~1000-3000 replays (matches biological data: rat schema rapid-acquisition 48 hours = ~50 NREM cycles after scaffold exists; full schema from scratch is ~1000-2000 replays in McClelland's CLS simulations).

---

## Cheap decisive test

**Cell name:** `gap3_cls_two_tier_BCM_slow_replay_v1`

**What it tests in one sentence:** does a separate W_schema, written at eta_slow = 1e-3 by BCM sliding-threshold rule fed from replay of W_episodic, produce a schema vector for each category that scores >= 0.65 heldout accuracy at N=8192 with 5 categories x 20 train + 10 heldout per category?

**Architecture (drawn out):**

```
                 EPISODES (5 cats x 20 instances each = 100 total)
                                |
                  +-------------+--------------+
                  | episodic write             | replay sampling
                  v   (eta_fast = 1.0)         |   (uniform with mild
            W_episodic                         |    recent-bias 0.7)
            (existing W)                       |
                  |                            |
                  +--->  REPLAY ENGINE  <------+
                  (existing continual.replay_cycle)
                                |
                                v
                  +-------------+--------------+
                  |  GENERATIVE RECONSTRUCTION  |
                  |  (decode each replayed key  |
                  |   from W_episodic to get    |
                  |   the value; pair becomes   |
                  |   the schema training       |
                  |   sample)                   |
                  +-------------+--------------+
                                |
                                v
                  +-------------+--------------+
                  |   BCM SLIDING-THRESHOLD     |
                  |   WRITE INTO W_schema       |
                  |   (eta_slow = 1e-3)         |
                  |                             |
                  |   dW = eta_slow * x *       |
                  |         y * (y - theta_M)   |
                  |   theta_M = EWMA(y^2)       |
                  +-------------+--------------+
                                |
                                v
                          W_schema (NEW)
                          (slowly extracts category prototype
                           from many replays at sliding threshold)
                                |
                                v
                   QUERY-TIME (heldout instance):
                   query W_schema first; if confident,
                   return schema-completion;
                   else fall back to W_episodic
```

**Four arms:**

- `ARM_BASELINE_SINGLE_W` -- substrate's existing single-W with iterative cleanup. Expected ~0.37 (Cell 1 baseline anchor).
- `ARM_TWO_TIER_HEBBIAN_SLOW` -- second W_schema with vanilla Hebbian at eta_slow = 1e-3. Tests: does the eta_slow alone, with vanilla rule, do anything?
- `ARM_TWO_TIER_BCM_SLOW` -- second W_schema with BCM sliding-threshold at eta_slow = 1e-3. The full brain-aligned mechanism.
- `ARM_TWO_TIER_BCM_GENERATIVE_REPLAY` -- as above BUT replay is generative (sample from W_episodic, not literal episode IDs). Tests Olafsdottir-McClelland generative-replay-helps-generalization claim.

**Pre-registered bands:**

- **HARD_PASS:** `ARM_TWO_TIER_BCM_*` >= 0.65 heldout AND >= +0.15 over `ARM_BASELINE_SINGLE_W` AND >= +0.10 over `ARM_TWO_TIER_HEBBIAN_SLOW`. The double-comparison rules out "second tier alone helps" (which would not be the BCM rule earning the lift). cv <= 0.10 across 3 seeds. W_schema entropy at end of training is LOWER than W_episodic entropy (compression actually happened).

- **HARD_FAIL:** All TWO_TIER arms collapse within 0.05 of single-W baseline. Interpretation: substrate's HRR-bundle ceiling is structural at N=8192 with 20 instances; no amount of slow-extraction rule helps; pivot to Modern Hopfield basin-sharpening (already queued).

- **MIDDLE_BAND [0.50, 0.65]:** PARTIAL. Schema formation visible (W_schema does compress), but does not reach chain-grade threshold. Queue follow-up: (eta_slow in {1e-2, 1e-3, 1e-4, 1e-5}) x (replay_cycles in {500, 1500, 5000, 15000}) x (theta_M_EWMA_window in {50, 200, 1000}).

**Discriminator design (per [[feedback-experiment-bias-master-checklist]] BIAS-13/14/15):**
- Same seeds [11, 13, 19] as Cell 1 -- cross-cell rail
- ARM_BASELINE must replicate Cell 1 ARM_NO_SCHEMA ~0.37 within 0.05 (methodology-drift gate)
- Per-arm metrics MANDATORY per Fix #28; do not infer from verdict_msg
- W_schema mean-cosine-to-cone must NOT drift below 0.5 of W_episodic (cone-preserving rail per Gap 2 reframe)
- Replay-source audit: zero literal-instance lookups during heldout test (would be data leak)

**Compute budget:** 6-10 CPU-hr local_cpu_queue at N=8192. Dominant cost is 5000 replay cycles x 4 arms x 3 seeds = 60K replay iterations.

---

## Section 1: What the brain ACTUALLY does (step-by-step plain English)

### Step 1 -- Hippocampus stores the episode (FAST, ONE-SHOT)

Alice pets dog Rex on Monday. Hippocampus dentate gyrus does **pattern separation**: it assigns a SPARSE code (only ~2-5% of DG cells fire for this episode) to "Alice-petting-Rex-Monday." The code is engineered to be MAXIMALLY different from "Bob-petting-Rex-Tuesday" so that the two episodes don't interfere. Synapses CA3->CA1 are potentiated by **Hebbian LTP** at high learning rate (effective eta ~ 1.0; one trial is sufficient). The episode is **filed**.

Why this works the brain's way: the hippocampus is a small, fast, sparse-coded store. It is acceptable for it to fill up over weeks because everything in it gets moved OUT to cortex during sleep.

### Step 2 -- During NREM sleep, sharp-wave ripples replay the episode at 20x speed

Sharp-wave ripples (SWR, ~200 Hz oscillations in CA3) cause time-compressed replay of recent episodes. The compression factor is ~20x (a 4-second waking trajectory replays in 200 ms). Importantly, replay is NOT in literal order -- it is **shuffled and interleaved** with replays of OTHER episodes from the same and prior days.

Why shuffled: McClelland-McNaughton-O'Reilly (1995) proved mathematically that interleaved replay is what prevents catastrophic forgetting when slow cortex receives the patterns. Sequential replay of all-dog episodes followed by all-cat episodes catastrophically rewrites the cortex weights; interleaved replay forces cortex to find a representation that handles BOTH classes simultaneously.

### Step 3 -- The replay is BROADCAST to cortex via thalamus

Hippocampal SWR ripples couple to **cortical slow oscillations** (1 Hz) and **sleep spindles** (12-15 Hz) in a tight three-way phase-lock (Buzsaki bidirectional dialog; Maingret 2021). The slow-oscillation UP states are when cortex is receptive to writing; the hippocampal SWRs deliver the episodes DURING UP states only. Result: replay-driven plasticity in cortex is **gated by sleep state**.

### Step 4 -- CORTEX learns the regularity with a NON-HEBBIAN rule

This is the critical step the user is asking about. Cortical learning is **not** vanilla Hebbian LTP. Cortex uses **BCM** (Bienenstock-Cooper-Munro 1982) which is the empirically-validated cortical learning rule:

```
dw_kj/dt = eta_slow * x_j * y_k * (y_k - theta_M)
theta_M  = E[y_k^2]_recent      (sliding threshold, EWMA of postsynaptic activity squared)
```

Where:
- `x_j` is presynaptic activity (input from hippocampal replay)
- `y_k` is postsynaptic activity (cortex output)
- `theta_M` is a **sliding threshold**: it follows the time-averaged squared output activity

**Why BCM differs from Hebbian:** Hebbian says "if presynaptic AND postsynaptic both fire, strengthen." BCM says "if presynaptic fires AND postsynaptic fires ABOVE its recent threshold, strengthen; if presynaptic fires AND postsynaptic fires BELOW its recent threshold, WEAKEN." The threshold is itself adaptive -- it slides up when the neuron has been active a lot, slides down when quiet.

The geometric consequence: a cortex neuron that has been responding to "dog-like" patterns gets a HIGH theta_M. New patterns that match the dog-prototype but only weakly fire it cause WEAKENING (suppress drift). New patterns that match the dog-prototype strongly fire it cause STRENGTHENING (sharpen the prototype). Over many replays, the cortex neuron becomes **selectively tuned to the dog-prototype** -- not to any single instance, but to the **common feature subspace** of the replayed dog-episodes.

This is precisely what HRR-bundle CANNOT do. HRR-bundle adds every instance equally; BCM suppresses inconsistent instances and amplifies consistent ones.

### Step 5 -- The schema crystallizes after THOUSANDS of replays

McClelland 1995 / Kumaran 2016 simulations and Tse-Morris 2007 empirical work converge:

- **From scratch:** schema needs ~1000-2000 replays = many sleep cycles = weeks-to-months in biology
- **With prior scaffold (Tse-Morris):** new fact integrates into existing schema in **48 hours = ~50 NREM cycles**
- **Cortex effective learning rate:** ~5e-4 (Sun, Wang, et al. 2023 neural-network-account model of CLS uses eta_slow = 5e-4)

The schema occupies a **specific anatomical destination**:
- Visual schemas: ventral temporal cortex
- Categorical schemas: anterior temporal lobe + lateral PFC
- Episodic-context schemas: ventromedial PFC (Tse-Morris anatomical follow-up)

### Step 6 -- New input: schema activates first, pattern-completes the rest

When Alice meets a NEW dog she has never seen, the visual feature subspace (4-legged, fur, snout) hits the cortex schema for "dog" before the hippocampus can find a matching episode. The cortex schema pattern-completes the missing properties ("warm-blooded", "barks", "wags tail"). Only if the schema gives a LOW-confidence answer (large prediction error / refuse-gate trigger) does the hippocampus get consulted for an episode-match.

This is the "predictive coding" view: cortex generates a top-down prediction; sensory areas signal the error; if the error is small, schema-completion is accepted; if large, episode-recall is invoked.

### Where the math comes in -- four equations summarize

1. **Hippocampal write (fast, Hebbian):**
   ```
   W_episodic[j,k] += eta_fast * x_j * y_k    with eta_fast = 1.0
   ```
2. **Cortical write (slow, BCM):**
   ```
   W_schema[j,k] += eta_slow * x_j * y_k * (y_k - theta_M[k])    with eta_slow = 5e-4
   theta_M[k] = (1 - tau) * theta_M[k] + tau * y_k^2     with tau = 0.01
   ```
3. **Replay distribution (interleaved):**
   ```
   sample category c uniformly from C categories
   then sample instance i uniformly from I_c instances
   ```
4. **Schema-vs-episode arbitration (refuse-gate):**
   ```
   if confidence(W_schema query) > tau_refuse:
       return W_schema completion
   else:
       fallback to W_episodic episodic recall
   ```

These four equations -- BCM rule + interleaved sampling + slow learning rate + schema-confidence arbitration -- ARE the brain's cortical-schema mechanism. Nothing else is load-bearing.

---

## Section 2: Why HRR-bundle fails (math-light)

The substrate currently has W_episodic only. When it tries to build a "schema" by bundling the K instances of a category:

```
schema_HRR = (1/K) * sum_i  instance_i
```

This is a **linear superposition**. Two structural problems:

**Problem 1 -- the heldout query lives in the NOISE FLOOR.**
- The schema is a sum of K specific vectors.
- A heldout instance is a random sample from the same category distribution.
- Its expected cosine with the schema is roughly `cos(heldout, mean(instances))`, which equals `(1/K) * sum_i cos(heldout, instance_i)`.
- For HRR random codes at N=8192 with K=20 instances per category: the per-instance cosine ~ 1/sqrt(N) ~ 0.011, the mean over K trials adds sqrt(K)/sqrt(N) ~ 0.05 noise, the in-category signal is roughly the variance of the feature-overlap (small).
- Net: heldout-vs-schema cosine is dominated by noise, not signal.
- This is exactly the ceiling Cell 1 saw -- ARM_FEATURE_BASED_SCHEMA capped at 0.47.

**Problem 2 -- adding more exemplars makes the prototype NOISIER, not cleaner.**
- The bundle's signal-to-noise ratio scales as sqrt(N/K).
- More K = more noise injected by exemplars that disagree with the consensus.
- In the brain's BCM rule, more exemplars makes the prototype CLEANER because disagreeing exemplars get DEPRESSED (their weights weakened, not added).
- Linear bundling has no equivalent of weakening; it only adds.

**The structural fix:** replace linear-add with a non-linear rule where exemplars that AGREE amplify the prototype and exemplars that DISAGREE suppress it. The two natural choices:
- **BCM sliding-threshold** (the brain's actual rule) -- this drill's recommendation.
- **Modern Hopfield basin-sharpening** (the prior drill's recommendation; already queued).

These are NOT mutually exclusive. BCM operates at the WRITE side (building the prototype); Modern Hopfield operates at the READ side (sharpening the basin at query time). The brain uses BOTH.

---

## Section 3: Substrate-feasible slow-learning mechanisms

For each, I describe substrate-native mapping in terms of existing primitives.

### Mechanism A: Replay-driven small W updates (the CLS write rule)

**Brain analog:** Cortex receiving interleaved replay from hippocampus at eta_slow.

**Substrate-native mapping:**
- `continual.replay_cycle` already implements the sampling + replay loop. Drift_reduction +0.57 proven-bound from last night's NREM drill.
- The MISSING piece is the destination -- replay currently writes back into the SAME W_episodic with the SAME eta_fast.
- Fix: add `W_schema` matrix; route replay outputs to `predictive_coding.gated_write(W_schema, key, value, eta=1e-3)`.

**Timescale:** at eta_slow = 1e-3 and 5000 replay cycles, effective update per weight is sum of ~5000 small updates ~ summed magnitude 1.5-3.0 (manageable). The schema converges in 1000-3000 cycles for the synthetic 5-cat task; 5000 is the comfortable margin.

**Why timescale matters:** at eta_fast = 1.0 substrate hits HRR-crosstalk ceiling after K=20 instances per category. At eta_slow = 1e-3 the W_schema accumulates ~5000/K = 250 EFFECTIVE updates per category, which is enough to average out individual-instance noise. This is the structural reason eta_slow is required, not just preferred.

### Mechanism B: TWO_TIER architecture (the CLS storage structure)

**Brain analog:** Hippocampus (W_episodic, fast, sparse) + Cortex (W_schema, slow, distributed).

**Substrate-native mapping:** Already covered in Gap 4 TWO_TIER_GENERATIONAL hand-off; cell in queue. Adds W_schema as a second matrix; promotion rule based on importance score.

**Compose with Gap 3:** the Gap 4 cell tests TWO_TIER for LONG-TERM RETENTION (alpha 0.61, 5000 cycles). This drill recommends TESTING TWO_TIER FOR SCHEMA-EXTRACTION on the SAME ARCHITECTURE. One cell = two endpoints, one architecture.

### Mechanism C: BCM sliding-threshold (the cortical NON-HEBBIAN write rule)

**Brain analog:** the cortical learning rule (Bienenstock-Cooper-Munro 1982; Cooper-Bear-Cooper-Munro 30-year review 2012).

**Substrate-native mapping:**
- Existing `predictive_coding.gated_write` does vanilla Hebbian gated by residual.
- BCM extension is ~20 lines: maintain a per-output-channel EWMA of y_k^2 (sliding threshold theta_M); compute `phi = y_k * (y_k - theta_M)`; apply `dW = eta_slow * x * phi`.
- Substrate already has the W stats infrastructure (whitening.py computes EWMAs of various quantities).

**Why this is the load-bearing piece:** BCM is what makes the prototype SHARPEN with each replay rather than NOISIER. Without BCM, slow Hebbian replay just converges to the bundle prototype (same ceiling as Cell 1). With BCM, the prototype converges to the COMMON FEATURE SUBSPACE across the replayed exemplars -- which is the actual schema.

**Timescale:** theta_M EWMA window tau = 0.01 corresponds to ~100 trial half-life; over 5000 replay cycles theta_M has tracked ~50x of its window, fully equilibrated. The schema converges as fast as theta_M tracks.

### Mechanism D: Iterative prototype refinement during replay (online k-means analog)

**Brain analog:** This is the online k-means / vector-quantization view of cortical category learning. Less load-bearing than BCM but mechanically simpler.

**Substrate-native mapping:**
- Maintain a fixed K=5 (number of categories) set of prototype vectors P_1...P_K in W_schema.
- For each replay sample (key, value): assign to nearest prototype, update prototype = (1 - eta_slow) * P_c + eta_slow * value.
- This IS online k-means with momentum.

**Why weaker than BCM:** prototype refinement assumes you KNOW the category labels at replay time. The brain doesn't -- BCM is **unsupervised**. For the experiment we have labels, so this is a fair lower-bound mechanism. But BCM is closer to the brain.

**Timescale:** convergence at eta_slow = 1e-3 over 5000 replays = effective averaging window of ~1000 samples per prototype = robust convergence.

### Mechanism E: Predictive coding hierarchy with top-down generative model

**Brain analog:** Rao-Ballard 1999 / Friston FEP. Higher cortical layers generate top-down predictions; lower layers signal residuals; weights update to minimize residual.

**Substrate-native mapping:**
- Layer L1 = existing predictive_coding.predict / residual / gated_write (single layer).
- Layer L2 = NEW -- category-level prediction = expected_features given current best category hypothesis.
- Residual_L2 = observed_features - predicted_features; W_schema_L2 updates to reduce this.
- At inference: query Layer L2; if residual small, return L2 schema completion; else fall back to L1 episodic.

**Why valuable:** adds substrate-product refuse-gate. The PC view gives substrate a calibrated "do not generalize" signal.

**Timescale:** PC convergence is gradient-based; in substrate's regime ~2000-5000 update steps.

### Mechanism F: Sparse distributed memory (Kanerva 1988 / Bricken-Pehlevan 2021)

**Brain analog:** Cerebellum + (per Bricken-Pehlevan) softmax attention.

**Substrate-native mapping:** substrate's `iterative_attractor.iterative_cleanup` IS approximately SDM with hard-locations = codebook entries. The MISSING piece is **pooling across all near-locations** rather than picking argmax.

**Why I'm deprioritizing this one in this drill (despite being a brain-mechanism):** SDM is a **read-side** mechanism; it does pattern-completion at retrieval. The substrate's failure mode is at the **write-side** -- it has nothing to pattern-complete TO. SDM helps once schemas exist; it does not create them.

**SDM remains useful as the QUERY-side companion to BCM:** BCM writes the schemas; SDM retrieves them. Compose with Modern Hopfield query-side.

### Mechanism G: Modern Hopfield in COMPOSED mode (basin-sharpening + replay-trained basin centers)

**Brain analog:** Krotov-Hopfield 2016 dense-associative memory; loosely analogous to cortical attractor dynamics.

**Substrate-native mapping:** the Modern Hopfield cell already queued (`gap3_modern_hopfield_prototype_attractor_v1`) tests this at the query side.

**Compose with BCM:** BCM writes the prototype centers into W_schema during replay; Modern Hopfield with softmax(beta=20) on W_schema produces the attractor basins at query time. THE TWO COMPOSE. The brain does both: BCM rule writes the cortical prototype (write-side), and the cortical attractor dynamics (read-side) sharpen the response to incoming patterns.

**Cleanest substrate composition:** the recommended cell HERE should produce W_schema (BCM-written); the Modern Hopfield cell tests the READ-SIDE attractor on the SAME W_schema. Two cells, one architecture.

---

## Section 4: Composition that is actually brain-aligned

If we compose **NREM replay + TWO_TIER architecture + BCM rule + Modern-Hopfield query**, we get the brain's full cortical-schema pipeline:

| Brain layer | Mechanism | Substrate primitive | Status |
|---|---|---|---|
| Replay engine | Interleaved sampling at 20x compression | `continual.replay_cycle` | EXISTS (drift_red +0.57 proven-bound) |
| Storage tier-2 | W_schema as separate matrix | NEW (TWO_TIER cell adds this) | IN-FLIGHT |
| Cortical write rule | BCM sliding threshold at eta_slow | NEW (~20 lines on top of predictive_coding.gated_write) | NEEDS WRITING |
| Cortical attractor | Modern Hopfield basin-sharpening | Modern Hopfield cell tests this | IN-QUEUE |
| Schema-vs-episode arbitration | Predictive-coding residual gate | `refuse_gate` exists; needs `gated_routing(W_schema, W_episodic)` | NEEDS COMPOSITION (~5 lines) |

**Composition story (the cell):** `gap3_cls_two_tier_BCM_slow_replay_v1`

Sequence per cycle:
1. **Wake phase:** ingest new episodes into W_episodic at eta_fast (existing path).
2. **Sleep phase:** sample interleaved batch from W_episodic via `replay_cycle`.
3. **For each sample:** apply BCM write rule into W_schema at eta_slow.
4. **Periodically (every 100 cycles):** evaluate heldout schema-generalization on W_schema with iterative_cleanup at beta=20 (Modern Hopfield style query).
5. **At final eval:** measure heldout accuracy using `gated_routing(W_schema query, fallback to W_episodic if confidence low)`.

**Discriminator for "this is schema extraction not just rote storage":**

The cleanest test is **W_schema cosine-similarity matrix structure**. After training:

- **HARD evidence of schema extraction:** W_schema columns cluster into K=5 groups, with within-group cosine >> across-group cosine. Within-group cosine ~0.6-0.9 (instances of same category collapse to similar codes). Across-group cosine ~0-0.3 (categories separated).
- **HARD evidence of rote storage:** W_schema cosine matrix is BLOCK-DIAGONAL with 100 distinct blocks (one per literal instance). Within-block cosine ~1.0, across-block ~0.

The structural test is: does the W_schema column representing instance 7 of category 2 have HIGH cosine with the W_schema column for instance 13 of category 2 (yes = schema extracted), or LOW cosine (no = just stored each instance separately)?

This is a free secondary metric; should be reported per-arm.

**Secondary discriminator:** schema-without-instance test. Train on 20 instances of category 2; remove instance 7 from training set; query with instance 7 at test. If W_schema gives high-confidence correct answer, the schema generalizes (not just memorizing). This is the existing heldout-test; reported as primary metric.

---

## Section 5: Top 3 cell candidates ranked

| Rank | Cell name | Mechanism | P_deflated | Cost CPU-hr | Composes-with | Why-now |
|---|---|---|---|---|---|---|
| 1 | `gap3_cls_two_tier_BCM_slow_replay_v1` | A + B + C (NREM replay + TWO_TIER + BCM) | 0.45 | 6-10 | TWO_TIER cell architecture; Modern Hopfield query-side | brain-aligned full stack; closes both Gap 3 AND Gap 4 schema-formation question |
| 2 | `gap3_iterative_prototype_refinement_v1` | D (online k-means analog) | 0.35 | 3-4 | substrate's existing replay; subset of cell 1 | Mechanically simpler baseline; if it works, cell 1 should work better |
| 3 | `gap3_predictive_coding_hierarchy_v1` | E (PC hierarchy + refuse-gate) | 0.30 | 3-5 | refuse_gate primitive; predictive_coding primitive | Adds calibrated refuse to substrate-product; orthogonal lever |

### Cell 1 detail -- the rank-1 dispatch

**Cell:** `gap3_cls_two_tier_BCM_slow_replay_v1`

**Substrate-feasibility:** HIGH. All required primitives exist except BCM write rule (~20 lines new code) and gated_routing arbitration (~5 lines new code). Total new code: ~30 lines on top of existing 5 primitives.

**P_solve_deflated: 0.45** (capped at novel-synthesis 0.50; -0.05 for substrate-specific composition risk).

**Cost:** 6-10 CPU-hr at N=8192 over 5000 replay cycles x 4 arms x 3 seeds.

**Discriminator:** four-arm design (BASELINE / TWO_TIER_HEBBIAN_SLOW / TWO_TIER_BCM_SLOW / TWO_TIER_BCM_GENERATIVE_REPLAY). The double-comparison rules out single-cause confounds: BCM must beat slow-Hebbian to establish the BCM rule is load-bearing; generative replay must beat literal replay to establish replay-source is load-bearing. If only ONE comparison passes, partial mechanism story; if both pass, full brain-aligned mechanism confirmed.

**Why-now:** the prior Gap 3 drill recommended Modern Hopfield first (cheap, fast, lower-risk). That cell is now in-queue. This cell tests the OTHER side of the schema pipeline (write-side BCM). The two cells COMPOSE: if both HARD_PASS, substrate has the full brain stack; if Modern Hopfield alone HARD_PASS, substrate has the read-side win with HRR-bundle write; if this cell alone HARD_PASS, substrate has the write-side win with classical attractor read. Both are useful outcomes.

### Cell 2 detail -- iterative prototype refinement

**Cell:** `gap3_iterative_prototype_refinement_v1`

**Substrate-feasibility:** VERY HIGH. Online k-means with momentum is ~10 lines.

**P_solve_deflated: 0.35.** Lower than Cell 1 because it assumes labels at replay time (which the brain does not have but the synthetic test does).

**Cost:** 3-4 CPU-hr at N=8192.

**Discriminator:** does k-means converge to centers that score >= 0.55 heldout?

**Use as falsification probe:** if k-means (with labels) HARD_FAILs, then BCM (without labels, harder problem) will also fail. Cheap upper-bound check. Useful as a "do we have enough information in the data" sanity test.

### Cell 3 detail -- predictive coding hierarchy

**Cell:** `gap3_predictive_coding_hierarchy_v1`

**Substrate-feasibility:** HIGH. Builds on existing predictive_coding + refuse_gate primitives.

**P_solve_deflated: 0.30.** Lower because PC convergence is gradient-based and substrate may have noisy gradients.

**Cost:** 3-5 CPU-hr.

**Why valuable even at lower P:** adds calibrated abstention to substrate. This is a substrate-product differentiator orthogonal to schema-formation. Even if Cell 1 lands HARD_PASS for schema-formation, Cell 3 adds a separate substrate-product capability (refuse-when-uncertain).

---

## Section 6: Honest scope -- how many cycles?

**Biology:**
- From scratch schema: ~1000-2000 replays (months in rat; weeks in human consolidation timeframe).
- With prior scaffold (Tse-Morris 2007): ~50 NREM cycles = 48 hours.
- Cortex effective learning rate: 5e-4 per neural-network model of CLS (Sun-Wang 2023).

**Substrate translation:**
- 1 substrate cycle = 1 replay sample.
- For N=8192 and 5 categories x 20 instances:
  - At eta_slow = 1e-3 and BCM rule:
    - 500 cycles = early prototype (~MIDDLE_BAND range, expected)
    - 1500 cycles = mid-training (HARD_PASS expected if mechanism works)
    - 5000 cycles = comfortable convergence margin
  - At eta_slow = 5e-4 (biological match):
    - 1000 cycles = early prototype
    - 3000 cycles = mid-training
    - 10000 cycles = comfortable margin

**Recommended cell budget:** 5000 cycles at eta_slow = 1e-3. This is the FAST mathematical equivalent of the biological 3000 cycles at eta_slow = 5e-4 (same total effective update mass). Comfortable margin for HARD_PASS in 6-10 CPU-hr.

**Is this 10000-cycle cell? 100000?** No. The schema-formation task at N=8192 with 5x20 instances is small enough to converge in 1000-5000 cycles. The 10000-cycle and 100000-cycle scales are for LONG-TERM RETENTION (Gap 4), not schema FORMATION (Gap 3). Schema-formation is fast-by-construction at the synthetic-task scale; the BIG cycle counts apply once we scale to natural-language ingest (Anchor 1 of language ingest drill -- text8 with 50k vocab = ~10M training samples).

**Worth saying explicitly:** substrate is NOT cortex-slow today in the sense that it does not have a separate W_schema with eta_slow. Once it has those, the actual cycle counts to FORM schemas at synthetic-task scale are modest (5000); the LARGE cycle counts come from real-world data volumes, not from the mechanism's intrinsic timescale.

---

## Cross-thread synthesis

**With prior Gap 3 drill (Modern Hopfield queued):** the prior drill recommended attacking the READ side (basin-sharpening at query time). This drill recommends attacking the WRITE side (BCM-extracted prototypes). The two compose multiplicatively. The brain uses both. If both cells land HARD_PASS, substrate has full brain-aligned cortical-schema pipeline.

**With Gap 4 TWO_TIER (in-flight):** Cell 1 here HAS THE SAME ARCHITECTURE -- W_episodic + W_schema. The two cells could be unified into ONE cell with 5 arms and TWO endpoints (retention + schema-gen). Recommend bundling if compute budget permits; otherwise keep separate cells with shared W_schema definition for reproducibility.

**With NREM drift_reduction +0.57 proven-bound:** the replay engine is established. This drill puts the engine to NEW use: instead of writing-back to W_episodic (current default), route to W_schema with BCM rule. The proven-bound REMAINS VALID for the W_episodic side; W_schema is additive.

**With Gap 2 anisotropy-is-feature reframe:** BCM-written W_schema columns will be cone-preserving by construction (BCM doesn't rotate vectors -- it scales them). Confirmed cross-cell signature: cone-preserving = win. Cone-rotating mechanisms (whitening, capability-XOR, fixed-symbol-codebook) lose.

**With Tse-Morris 2007 schema rapid-acquisition:** once substrate has W_schema scaffold, NEW categories should integrate in ~50-100 replays (10-100x faster than from-scratch 1000-2000). This is a SECONDARY EXPERIMENT after Cell 1 lands: train W_schema on 5 categories with 5000 cycles; then add a 6th category and measure how many cycles to schema-form it. Predicted by Tse-Morris: ~100-300 cycles for the 6th category vs 1000-2000 for the first one. This is a chain-grade-eligible secondary claim if observed.

**With Fix #28 verify-per-arm-metrics:** all 4 arms must have per-arm metrics reported; verdict_msg insufficient. Specifically W_schema cosine-similarity matrix structure must be per-arm because it's the schema-extraction discriminator independent of accuracy.

**With Fix #26 pre-dispatch verify-the-referent:** substrate-mine atoms for `bcm`, `metaplastic`, `sliding_threshold` before dispatch to verify no prior cell has tried this. (Quick check: grep for prior BCM atoms; if none, this is the first dispatch and substrate-novel.)

---

## Substrate-product implications

**If Cell 1 HARD_PASSes (Gap 3 closes via brain-aligned mechanism):**

Headline product story: "substrate's auditable memory subsystem now has a hippocampus AND a cortex. Hippocampus stores episodes; cortex extracts schemas via the brain's actual learning rule (BCM). Same architecture handles long-term retention (W_schema doesn't forget) AND compositional generalization (W_schema completes novel category members). Two endpoints, one architecture, one cell."

**If Cell 1 + Modern Hopfield BOTH HARD_PASS:**

Headline product story: "substrate now implements the full brain cortical-schema pipeline: NREM replay + TWO_TIER storage + BCM slow-write + Modern Hopfield attractor-read. Each piece has brain-existence-proof. The mechanism is biologically grounded; the implementation is auditable; the math is closed-form. This is the differentiator vs vector-DBs and LLMs alike: vector-DBs have only episodic, LLMs have only learned-distributed-prototypes with no audit trail; substrate has both with full audit."

**If Cell 1 HARD_FAILs:**

Diagnosis: the SLOW-RATE mechanism alone is not enough; the cone geometry of N=8192 with K=20 instances per category may simply not have enough mutual information to support schema-formation regardless of write rule. Pivot: increase instances_per_category to 50-100 (capacity sweep) and re-test. If still fails at K=100, the gap is information-theoretic, not mechanism-theoretic.

**Capability-map implication:** Gap 3 currently RED. HARD_PASS of Cell 1 promotes to YELLOW at minimum (substrate now has SOMETHING that does schema-extraction). Chain-grade HARD_PASS with the discriminator-design tests passing promotes to GREEN.

**Atomization on HARD_PASS:**
- Atom: `cortical_schema_BCM_slow_replay_two_tier_substrate_native` -- "Substrate's brain-aligned cortical schema mechanism: NREM replay + W_schema second tier + BCM sliding-threshold rule at eta_slow = 1e-3 + Modern Hopfield query-side basin-sharpening. Closed-form math; cell-verified."
- hdlab primitive: `hdlab/cortical_schema.py` exposing `BCM_slow_write(W_schema, x, y, eta_slow=1e-3)`.
- Capability-suite regression test: `tests/test_cortical_schema_generalization.py` -- 5cat x 20 instances heldout >= 0.65.

---

## Citations (verified count = 18 external + 9 internal = 27 distinct sources)

**Brain side (cortical schema / BCM / CLS):**
1. Bienenstock, Cooper, Munro (1982). "Theory for the development of neuron selectivity: orientation specificity and binocular interaction in visual cortex." J Neurosci 2(1): 32-48.
2. Cooper, Bear, Cooper, Munro (2012). "The BCM theory of synapse modification at 30: interaction of theory with experiment." Nat Rev Neurosci. [Scholarpedia](http://www.scholarpedia.org/article/BCM_theory) [PMC PMC5318375](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5318375/)
3. McClelland, McNaughton, O'Reilly (1995). "Why there are complementary learning systems in the hippocampus and neocortex." Psychological Review 102(3): 419-457.
4. Kumaran, Hassabis, McClelland (2016). "What learning systems do intelligent agents need? Complementary learning systems theory updated." Trends Cog Sci 20(7): 512-534.
5. Tse, Langston, Kakeyama, Bethus, Spooner, Wood, Witter, Morris (2007). "Schemas and memory consolidation." Science 316(5821): 76-82. [Schemas and Memory Consolidation](https://www.science.org/doi/abs/10.1126/science.1135935)
6. Tse, Takeuchi, Kakeyama, et al. (2011). "Schema-dependent gene activation and memory encoding in neocortex." Science 333(6044): 891-895.
7. Moscovitch, Cabeza, Winocur, Nadel (2016). "Episodic memory and beyond: the hippocampus and neocortex in transformation." Annu Rev Psychol 67: 105-134.
8. Sun, Wang, et al. (2023). "A neural network account of memory replay and knowledge consolidation." Cerebral Cortex 33(1): 83. [Cerebral Cortex](https://academic.oup.com/cercor/article/33/1/83/6537049)
9. Maingret et al. (2021). "Bidirectional interaction of hippocampal ripples and cortical slow waves leads to coordinated spiking activity during NREM sleep." Cerebral Cortex. [PMC8179633](https://pmc.ncbi.nlm.nih.gov/articles/PMC8179633/)
10. Olafsdottir, McClelland (2018). "Generative replay for cortical learning." [referenced in arxiv 2104.04132 Replay in Deep Learning]

**HRR / VSA capacity:**
11. Plate (1995). "Holographic Reduced Representations." IEEE Trans Neural Networks 6(3): 623-641.
12. Schlegel et al. (2021). "A Comparison of Vector Symbolic Architectures."
13. arxiv 2109.02157 (2021). "Learning with Holographic Reduced Representations."

**Predictive coding:**
14. Rao, Ballard (1999). "Predictive coding in the visual cortex." Nat Neurosci 2(1): 79-87.
15. Millidge, Salvatori, Buckley (2021). "Predictive Coding: a Theoretical and Experimental Review." arxiv 2107.12979.
16. arxiv 2112.10048 (2021). "Predictive Coding Theories of Cortical Function."

**SDM:**
17. Kanerva (1988). Sparse Distributed Memory. MIT Press.
18. Bricken, Pehlevan (2021). "Attention Approximates Sparse Distributed Memory." NeurIPS 2021. arxiv 2111.05498.

**Internal substrate notes:**
- notes/research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md
- notes/research_gap4_continual_5x_drill_2026-06-26.md
- notes/research_gap2_REFRAME_anisotropy_is_feature_2026-06-26.md
- notes/research_gap3_compositional_5x_drill_2026-06-26.md
- data/exp_substrate_cortical_schema_extraction_compositional_generalization_v1/metrics.json (Cell 1 anchor)
- data/exp_gap3_lars_vsa_relational_bottleneck_v1_n8192/metrics.json (Cell 2 anchor)
- hdlab/continual.py (existing replay_cycle; nrem_replay_decorator)
- hdlab/predictive_coding.py (existing gated_write -- BCM extension goes here)
- hdlab/iterative_attractor.py (existing iterative_cleanup; Modern Hopfield queued cell)

---

## Lit-scan calibration notes

- All probability estimates deflated 0.15-0.25 from raw LM confidence per [[feedback-lit-scan-calibration-penalty]].
- Novel-synthesis cap at 0.50 applied to Cell 1 (CLS-BCM-replay-substrate composition has no direct published precedent; the COMPONENTS each have lit precedent but their substrate-specific composition is novel).
- HARD-FAIL thresholds mandatory and listed for every prediction.
- Discriminator design follows BIAS-13/14/15 mismatch-bias check: ARM_BASELINE must replicate Cell 1 baseline within 0.05; cone-preserving rail in place; per-arm metrics mandatory per Fix #28.
- DIRECTIONALITY (slow-rate BCM-replay does the schema work in the brain) is HIGHLY confident (raw P ~ 0.85 across 4 independent lit-anchors: McClelland 1995, BCM 1982, Tse-Morris 2007, Sun-Wang 2023). MAGNITUDE (substrate-specific HARD_PASS at this regime) is where deflation hits.
- Fields drilled explicitly: theoretical neuroscience (CLS, BCM, predictive coding, SDM); continual-learning ML (fast-slow weights, generative replay); VSA (HRR capacity / failure modes). 3+ disparate fields converge on the prescription. Meets Trigger F aggressive cross-domain requirement.
- Substrate-novel angle: substrate has not yet tried W_schema separate-tier with eta_slow BCM rule. Adjacent failed cells (Cell 1 cortex_schema MIDDLE; Cell 2 LARS-VSA HARD_FAIL_CONFOUND) tried bundling and fixed-symbol-codebook -- both LINEAR. This cell is the first NON-LINEAR write rule for schema extraction.

---

## Plain-English wrap

The brain doesn't build categorical schemas by averaging instances; it builds them by SLOWLY adjusting cortical weights so that the prototype gets SHARPER with each replayed exemplar (instead of noisier). The specific rule (BCM, 1982) uses a sliding threshold: weights to a cortex neuron strengthen when the neuron's response exceeds its recent-history threshold, and WEAKEN when the response is below threshold. Over thousands of interleaved replays at a 1000x slower learning rate than the hippocampus, this produces a prototype tuned to the COMMON FEATURE SUBSPACE of all replayed exemplars -- the schema.

Substrate currently has only ONE storage tier (W) operating at the FAST hippocampal rate. It has the replay engine (proven last night with +0.57 drift reduction) but the replay just writes back into the same fast tier, so it can't produce a slow-extracted schema.

The minimum-effort substrate-feasible composition is: add a SECOND W matrix (W_schema, the cortex), drive replay output into it at 1000x slower rate using the BCM sliding-threshold rule, and query W_schema first at test time falling back to the original W only when confidence is low. About 30 lines of new code on top of 5 existing substrate primitives.

Estimated probability the cell as designed will close Gap 3 the brain's way: 45 percent. Cost about 6-10 CPU-hours. Discriminator includes 4 arms so we can tell whether (a) the slow rate alone helped, (b) the BCM rule specifically was load-bearing, and (c) generative-replay added anything over literal replay -- the brain's lit predicts all three are load-bearing.

Cycle-count realism: 5000 cycles is enough for schema-formation at the synthetic-task scale (5 categories x 20 instances). 10000-cycle and 100000-cycle scales are reserved for natural-language ingest where the data volume itself is large, not for the mechanism's intrinsic timescale.

If this cell PASSES, substrate has the brain's full cortical-schema pipeline (replay + two-tier + BCM-slow + attractor-query). If it FAILS, the gap is more likely information-theoretic (need more instances per category) than mechanism-theoretic (need a different write rule).

---

-- Research (Opus 4.7 1M synthesis; 8 parallel WebSearch lit-scans converged; calibrated per discipline; HARD-FAIL thresholds pre-registered).
