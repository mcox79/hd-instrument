# Research: Modern Hopfield revival -- cortex-BUILT basins, not query-time replacement

**Date:** 2026-06-26
**Filed-by:** research (Opus 4.7 1M)
**Trigger:** USER deep revival drill request after Modern Hopfield prototype cell HARD_FAIL_MIDDLE_BAND_BELOW_FLOOR.
  - `MH_PROTO=0.22`, `MH_CONT=0.26`, `LIN_MEAN_PROTOTYPE=0.42`, `HRR_BUNDLE=0.58`
  - USER reframe: "We don't have enough data to do stuff like this well. Why the complexity here?"
  - USER directive: drill 3x deep on slow-built basins as the PRECONDITION for attractor dynamics.
**Builds-on:**
  - `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` (BCM + TWO_TIER + replay cell, P=0.45)
  - `notes/research_brain_hippocampal_SWR_sleep_replay_5x_drill_2026-06-22.md` (SWR mechanics)
  - `notes/research_modern_hopfield_PCN_AM_universal_kernel_2x_2026-06-17.md` (UHN kernel skeleton; PCN-AM)
  - `notes/research_modern_hopfield_capacity_retrieval_crossover_2026-06-16.md`
**Calibration:** P deflated 0.15-0.25; novel-synthesis cap 0.50; HARD-FAIL thresholds pre-registered.
**Lit-scan:** 6 parallel WebSearch streams; converged on Krotov 2-regime distinction (feature vs prototype) + synaptic-tagging-and-capture (STC) + SDM continual-learner revival + two-factor consolidation.

---

## HEADLINE -- one paragraph plain English

Modern Hopfield prototype cell failed because it asked the **prototype regime** of the Krotov-Hopfield model to do work it cannot do at substrate's scale. The prototype regime (`large n` polynomial energy, sharp basins, snap-to-nearest behavior) is exactly the regime where in Krotov's own analysis "more than 8000 of 10000 test patterns have no other memory making a comparable contribution" -- that is, a regime that assumes you already have well-separated, strong basins. The substrate has 20 instances per category. The basins it has are weak. Snapping to nearest in that situation is exactly how you commit to the wrong answer.

The USER's reframe is correct and load-bearing: the mechanism that turns weak instance-traces into strong basins **is not Modern Hopfield itself; it is the slow consolidation machinery that builds those basins over thousands of replay cycles**. The brain's actual stack is: hippocampus stores instances (fast); NREM replay re-presents them interleaved (slow); cortex BCM + synaptic-tagging-and-capture (STC) GROWS the basin (slowly, over weeks); Modern-Hopfield-style attractor dynamics RETRIEVES from those slow-built basins (at query time). The substrate tried to skip the middle two steps.

The revival cell is NOT "Modern Hopfield again with different beta." The revival is: **first build basins the way the cortex actually does, then test Modern Hopfield as the query-side readout on those built basins**. Three candidate write-side mechanisms differ from the BCM cell already in queue:
1. Synaptic-tagging-and-capture (STC) -- never delete losing basins; let them be CAPTURED by stronger nearby ones (the USER's "cold-storage / never-delete" insight, mechanically formalized).
2. SDM with online prototype refinement (Bricken-Pehlevan 2021 + arxiv 2303.11934 "SDM is a Continual Learner") -- distinct mechanism class from BCM; uses sparse hard-locations and softmax addressing.
3. Krotov **feature-matching** regime (NOT prototype regime) on raw episodic W -- the substrate's existing W already supports this; just lower `n` in the polynomial energy so MANY weak memories cooperate cooperatively rather than one dominating.

The recommended dispatch is one cheap diagnostic FIRST (Krotov feature-matching regime on existing W; ~1 CPU-hr; tests whether the prior cell was simply in the wrong regime), then if that gives a measurable lift, a longer slow-built-basins cell.

P_deflated for top candidate (Krotov feature-matching regime cheap diagnostic): **0.45**
P_deflated for full slow-built-basins-then-Modern-Hopfield-readout cell: **0.40**

---

## Cheap decisive test (diagnostic FIRST)

**Cell name:** `mh_revival_feature_regime_diagnostic_v1`

**What it tests in one sentence:** Does the SAME Modern Hopfield architecture with `n=2` (feature-matching regime; many basins cooperate) outperform `n=20` (prototype regime; one basin dominates) on the SAME substrate state that just produced MH_PROTO=0.22?

**Why this matters before any new cell:** the prior cell's HARD_FAIL may have been a REGIME error, not a mechanism error. Krotov 2016 explicitly characterizes the two regimes as a smooth family parametrized by polynomial order n. At small n (~2), the energy is dominated by many low-overlap contributions cooperating; at large n (~20), one high-overlap contribution dominates. The prior cell used softmax = effectively very high n. For a substrate with 20 weak basins, n=2 should outperform n=20 simply because cooperation across weak basins beats commitment to a single weak basin.

**Architecture:**
```
Query q -> compute overlap vector s_i = <q, xi_i> for each stored xi_i
        -> Modern Hopfield readout = sum_i xi_i * softmax(beta * s_i^n) where n = polynomial order
        -> measure heldout accuracy
```

**Four arms (same seed grid as prior MH cell to cross-cell-compare directly):**
- ARM_HOPFIELD_N2 -- n=2 (feature regime; many memories cooperate)
- ARM_HOPFIELD_N4 -- n=4 (intermediate)
- ARM_HOPFIELD_N10 -- n=10 (approaching prototype)
- ARM_HOPFIELD_N20_SOFTMAX -- n=20 ish (the prior cell's MH_PROTO regime, control)

**Pre-registered bands:**
- HARD_PASS: ARM_HOPFIELD_N2 >= 0.50 heldout AND >= +0.15 over ARM_HOPFIELD_N20_SOFTMAX (the prior failure). Interpretation: regime error confirmed; substrate already has the data to do better than 0.22; the cell that just failed picked the wrong regime.
- HARD_FAIL: ARM_HOPFIELD_N2 within 0.05 of ARM_HOPFIELD_N20_SOFTMAX (both around 0.22). Interpretation: regime is not the issue; the mechanism class genuinely cannot work on substrate's existing W. Pivot to write-side slow-building (cell 2 below).
- MIDDLE_BAND [0.35, 0.50]: PARTIAL. Feature regime helps but not by chain-grade margin. Queue follow-up: combine n=2 readout with light prototype refinement.

**Compute budget:** ~1 CPU-hr local_cpu_queue at N=8192. This is a READOUT-ONLY cell; no write-side changes. Cheap.

**Why diagnostic FIRST:** before dispatching a 6-10 CPU-hr slow-built-basins cell, we should know whether the failure was regime-class or mechanism-class. If `n=2` lifts to 0.50+, then the basins were never the bottleneck; the prior cell just picked the wrong polynomial order. If `n=2` is also 0.22, we know the substrate's W is genuinely too noisy to support attractor dynamics directly, and the slow-build cell is the right next step.

---

## Section 1: Why Modern Hopfield failed at substrate scale -- mechanism class analysis

### 1.1 Krotov's two regimes (the load-bearing finding)

Krotov-Hopfield 2016 ("Dense Associative Memory for Pattern Recognition") explicitly characterizes the model as a family of energy functions parametrized by polynomial order n:
```
E(q) = -sum_i F(<q, xi_i>)    where F(s) = s^n / n   (or rectified polynomial, or exp for n -> infinity)
```
At small n (n=2 = classical Hopfield; n=3,4 = mild dense memory), the energy gradient at query q is a SUM over all stored patterns weighted by their overlap to power n-1. Many low-overlap patterns each contribute a small but non-zero force toward the query basin. The retrieval is the COLLECTIVE pull of many memories.

At large n (n=20, n=infinity = softmax = modern Hopfield 2020), one high-overlap pattern dominates the energy. Retrieval is essentially WINNER-TAKE-ALL. Krotov's own analysis shows that in this regime, more than 80% of test patterns have no second memory contributing more than 1/100 the dominant one. This is the regime where Hopfield acts like an exact lookup table.

### 1.2 Which regime is right for substrate?

The substrate has 20 instances per category. After superposing into a category prototype, each instance contributes 1/sqrt(20) ~ 0.22 to the prototype norm. Heldout instances overlap the prototype at roughly the same magnitude (call it cos~0.20). At dimension N=8192, two random category prototypes also have cos~1/sqrt(N) ~ 0.011 plus a small structured-overlap term from any shared features.

**The signal margin (heldout cos to its own prototype minus heldout cos to wrong prototype) is roughly 0.20 - 0.10 = 0.10**. That is well INSIDE the regime where softmax(beta * 0.20) and softmax(beta * 0.10) differ by little if beta is moderate, and differ a lot if beta is large. If beta is large enough to give one prototype 0.9 weight at signal-margin 0.10, then any noise of order 0.05 flips the winner. **Large beta with a 0.10 signal margin is structurally a noise amplifier.**

In Krotov's feature regime (small n, comparable to small beta), the readout is a WEIGHTED SUM of all prototypes with weights proportional to overlap-to-the-n. At n=2, the weights are nearly proportional to overlap, so a prototype with cos 0.20 gets 2x the weight of one with cos 0.10. The READOUT is a sum of prototypes with these weights -- a kind of "soft averaging" that is robust to small noise but lacks WTA committal. For a substrate where the signal margin is small, soft averaging is the better choice.

### 1.3 LIN_MEAN_PROTOTYPE = 0.42 also tells us something

The cell author added LIN_MEAN_PROTOTYPE as a comparator (linear prototype = mean of training instances; readout = nearest prototype by cosine). It scored 0.42, same as baseline. This is **the noise floor for one-shot prototype methods at this regime**. Modern Hopfield prototype at 0.22 SCORED WORSE THAN LINEAR PROTOTYPE because softmax-WTA committed to wrong basins when evidence was ambiguous, while linear nearest-neighbor at least picked the most-similar prototype (which is the right answer when basins are weak and well-separated).

The brain-aligned interpretation: at substrate's scale, **basin sharpness is the wrong target**. The right target is BASIN STRENGTH (more total mass per category) and BASIN SEPARATION (more orthogonal between categories). Both come from slow-build, not from non-linear readout choice.

### 1.4 HRR_BUNDLE = 0.58 is the existing best -- why?

HRR_BUNDLE outperforms all prototype methods because superposition gives the prototype a STRUCTURED contribution from every instance, and HRR codes preserve enough orthogonality between unrelated patterns that the prototype is mostly signal-from-this-category plus low cross-talk from other categories. Specifically, an HRR bundle of 20 random codes for category A and 20 for category B has:
- Within-category cosine of heldout-to-prototype: roughly proportional to the actual feature-overlap structure in the input (high if instances share features, near-zero if instances are random)
- Cross-category cosine: 1/sqrt(N) * sqrt(20/20) ~ 0.011

The substrate's HRR_BUNDLE is already operating closer to the FEATURE-MATCHING regime (sum-of-all-contributions) than the PROTOTYPE regime (one-dominates). The Modern Hopfield prototype cell ABANDONED the feature-matching strength of HRR for the prototype-regime fragility. **That is the structural reason the cell did worse than the baseline it tried to replace.**

### 1.5 Summary: failure mode is regime selection, not mechanism class

Modern Hopfield is not WRONG for substrate. The PROTOTYPE REGIME of Modern Hopfield is wrong for substrate at 20 instances per category. The FEATURE-MATCHING REGIME is plausibly right for substrate as-is and is the cheap-test recommendation above. The SLOW-BUILT REGIME (build basins first, then apply Hopfield retrieval) is the deeper test but requires write-side work covered by the BCM cell in queue.

---

## Section 2: How the brain actually builds basins (plain English mechanics)

The plain-English version (load-bearing for USER): the brain does NOT use attractor dynamics at retrieval until cortex has SLOWLY built the basins. The build process takes thousands of replay cycles over weeks. Modern Hopfield is the math of how cortex retrieves AFTER the build.

Step by step:

1. **Episode encounter (waking).** Hippocampus dentate gyrus assigns a SPARSE code (~2-5% of cells active) to "Alice-pets-Rex-Monday". Hebbian LTP at high learning rate (eta_fast ~ 1.0). One trial suffices. The episode is filed.

2. **NREM sleep (~5-10 SWRs/sec).** Sharp-wave ripples in CA3 trigger time-compressed (~20x) replay of recent episodes. Crucially, replay is INTERLEAVED across episodes from many days -- not all-dog then all-cat. McClelland-McNaughton-O'Reilly 1995 showed mathematically that interleaved replay is what lets cortex find a representation that handles all classes simultaneously without catastrophic rewrite.

3. **Cortical receptivity gated to UP-state.** Hippocampal SWRs phase-lock to cortical slow oscillations (1 Hz) and sleep spindles (12-15 Hz). Cortex is plastic ONLY during UP-states. This is a discrete schedule, not continuous learning.

4. **Cortical write via BCM, not Hebbian.** The cortical learning rule is the BCM sliding-threshold rule:
```
dw = eta_slow * x * y * (y - theta_M)
theta_M = EWMA(y^2)
```
where eta_slow ~ 5e-4 (1000-2000x smaller than hippocampus). The sliding threshold means: when the post-synaptic neuron has been firing a lot recently, FURTHER firing has to be ABOVE its threshold to strengthen the synapse; firing BELOW threshold WEAKENS it. Over many replays, the neuron tunes to a stable feature subspace shared across instances, not to any individual instance.

5. **Synaptic tagging and capture (STC) -- the never-delete principle.** This is the load-bearing addition for this drill. When a synapse is weakly potentiated by a single event, it sets a "tag". If a STRONG potentiation event occurs at a NEARBY synapse within ~1 hour, the protein synthesis from the strong event provides plasticity-related proteins (PRPs) that the weak tag CAPTURES. The weak memory then consolidates as if it had been strong itself. This is how the brain MERGES weakly-related memories into a schema without deleting them.

6. **The schema crystallizes after ~1000-3000 replays.** McClelland 1995 / Kumaran 2016 simulations + Tse-Morris 2007 rat experiments converge. From scratch a schema needs weeks. With a prior scaffold (Tse-Morris), a new fact integrates in ~48 hours = ~50 NREM cycles.

7. **Retrieval uses attractor dynamics on the slow-built basins.** ONLY at this point -- after the basins are strong -- does Modern-Hopfield-style softmax attention work. The retrieval picks the right cortical schema because the basins are now strong AND well-separated.

**The order matters absolutely: build, then retrieve. Substrate tried to retrieve without building.**

### 2.1 STC formalized

The Frey-Morris 1997 synaptic-tagging-and-capture experiment and the 2021 Nature Comm Bio model ("Memory consolidation and improvement by synaptic tagging and capture in recurrent neural networks") give a clean substrate-feasible formalism:
```
For each synapse w_ij:
  - tag t_ij in {0, 1}: set when |dw_ij| > theta_tag during a fast-write event
  - PRP availability p_i in [0, 1]: high near recently-strong potentiation; decays over time tau_PRP
  - Consolidation update during sleep:
      if t_ij == 1 AND p_i > theta_capture:
          w_ij_consolidated = w_ij  (capture; tag cleared)
      else:
          w_ij_consolidated = (1 - decay) * w_ij  (decay if not captured within tau_PRP)
```
Substrate translation: this is a SECOND tier of weights -- the consolidated weights -- with a tag bit per weight and a per-neuron PRP signal. The PRP signal is "this neuron just had a strong event recently". The capture rule says weak associations near strong ones get CONSOLIDATED at the same time, while isolated weak associations DECAY.

**This implements the USER's never-delete principle exactly:** losing basins are not deleted. They are TAGGED, and if a related strong event comes along during sleep replay, the tag captures the PRPs and the basin consolidates. If NO strong event comes along, the basin slowly decays (forgetting by neglect, not by overwrite).

### 2.2 Two-factor consolidation (PNAS 2024)

The Susman et al. PNAS 2024 paper ("Two-factor synaptic consolidation reconciles robustness with pruning and homeostatic scaling") gives an even cleaner formalism: two factors per synapse (fast effective weight + slow consolidated weight) with a sliding-threshold consolidation rule similar to BCM, plus homeostatic scaling that preserves total weight mass. The model unifies:
- Multiplicative homeostatic scaling
- Task-driven synaptic pruning
- Increased neural stimulus selectivity
- **Preferential strengthening of weak memories** (the never-delete principle, mathematically)

The preferential-strengthening-of-weak-memories result is the load-bearing one for this drill. It says: a weak memory that is REPLAYED gets MORE relative strengthening than an already-strong memory (because the strong memory's slow weight is closer to its target so the gradient is smaller). This is automatic basin-equalization during replay -- weak basins get more pull, strong ones get less. The result is a more uniform basin landscape, which is exactly what makes Modern Hopfield retrieval work well (well-separated basins of comparable strength).

---

## Section 3: Substrate-feasible slow-building schema cells (3 candidates)

### Mechanism A: Krotov feature-matching regime on existing W (the cheap diagnostic; already specified as Cell 1 above)

Recap: change the Modern Hopfield polynomial order n from "softmax = infinity" to "n=2 = feature matching". No write-side changes. ~1 CPU-hr.

P_deflated: 0.45. This is the CHEAPEST test of "was the prior cell's regime selection the actual error?". If it lifts to 0.50+, we have a substrate-product win without any new architecture.

### Mechanism B: Synaptic-tagging-and-capture (STC) write-side mechanism

**Brain analog:** Frey-Morris 1997; Tomeo 2025 review; 2021 Nature Comm Bio recurrent-net STC model.

**Substrate-native mapping:** add THREE state variables on top of the existing W matrix:
- `tag[i,j] in {0, 1}`: tag bit per weight, set on any fast write with magnitude > theta_tag
- `PRP[i] in [0, 1]`: per-output-neuron PRP availability, set to 1 on each strong fast write to row i, decays with time constant tau_PRP ~ 100 cycles
- `W_slow[i,j]`: the consolidated weight (separate matrix; this is similar to BCM cell's W_schema but with STC capture rule instead of BCM rule)

**Update rules:**
- Wake/fast write: `dW[i,j] = eta_fast * x_j * y_i`; if `|dW[i,j]| > theta_tag` set `tag[i,j] = 1`; if `dW[i,j] > theta_strong` set `PRP[i] = 1`
- Sleep/replay-driven consolidation: for each (replayed key k, replayed value v) sample:
  ```
  predicted_y = W @ k
  residual = v - predicted_y
  for each (i, j) with tag[i,j] == 1:
      if PRP[i] > theta_capture:
          W_slow[i,j] += eta_capture * residual_i * k_j      # capture: weak synapses consolidate
          tag[i,j] = 0                                         # tag cleared after capture
      else:
          W_slow[i,j] *= (1 - decay)                          # decay: untagged weak synapses fade
  ```
- PRP decay between replays: `PRP[i] *= (1 - 1/tau_PRP)`

**Why this is brain-aligned:** the capture rule means weak associations near strong recent events get CONSOLIDATED during sleep, not deleted. The decay rule means truly isolated weak associations fade. The brain's actual mechanism.

**Why this is substrate-feasible:** ~40 lines of new code on top of existing `predictive_coding.gated_write`. Tag bit can be packed into the sign bit of W; PRP is one float per row; W_slow is a second matrix the same shape as W.

**P_deflated: 0.40** (capped at novel-synthesis 0.50; -0.10 for substrate-specific composition risk and lack of direct empirical precedent at this scale).

**Cost:** 6-10 CPU-hr at N=8192 over 5000 replay cycles x 3 arms x 3 seeds.

**Discriminator (3 arms):**
- ARM_NO_STC -- existing W with replay (Cell 1 baseline)
- ARM_STC_NO_PRP -- STC capture rule with PRP fixed at 1.0 (tests whether tag-mechanism alone helps)
- ARM_STC_FULL -- full STC with PRP decay (the brain-aligned mechanism)

HARD_PASS: ARM_STC_FULL >= 0.65 heldout AND >= +0.15 over ARM_NO_STC AND >= +0.10 over ARM_STC_NO_PRP.
HARD_FAIL: STC arms collapse within 0.05 of baseline; pivot to BCM cell already in queue.

**Composes with:** BCM cell (W_schema) -- could be combined into a single cell where W_schema gets BCM rule for ENCODING and STC capture for CONSOLIDATION; these are orthogonal mechanisms (write-side encoding vs cross-time consolidation).

### Mechanism C: Sparse distributed memory (SDM) with online prototype refinement

**Brain analog:** Cerebellum (Kanerva 1988); Bricken-Pehlevan 2021 attention-as-SDM mapping; arxiv 2303.11934 "SDM is a Continual Learner".

**Why distinct from BCM cell:** SDM uses a DIFFERENT mechanism class. Instead of a single dense W matrix that everyone shares, SDM maintains K=100-1000 "hard locations" in HD space, each with its own address vector and content register. Writes activate hard locations within a Hamming radius of the key (a sphere of address space); reads activate the same sphere and SUM the contents.

**Substrate-native mapping:**
- Maintain K=1000 random address vectors A_1...A_K (frozen at init or slow-updated)
- Each address has a content register C_k (additive HD vector)
- Write(key, value): for each k where Hamming(key, A_k) < radius (typically ~100/2048 dims), update C_k += value
- Read(query): sum C_k over k where Hamming(query, A_k) < radius

**Why this addresses the substrate failure:**
- SDM's hard-locations CREATE basins by construction (each hard location is a basin center; the radius is the basin width)
- Online prototype refinement: each write contributes to MULTIPLE hard locations (not just one), giving robust averaging
- Reads SUM contributions from multiple locations, giving feature-matching behavior automatically

**Why this is substrate-feasible:** the existing `iterative_attractor.iterative_cleanup` is approximately SDM with hard-locations = codebook entries. The MISSING piece is the **pooling across all near-locations** rather than picking argmax. Bricken-Pehlevan 2021 shows softmax-attention IS SDM in the limit; substrate can pick either the hard-radius variant or the softmax variant.

**P_deflated: 0.35** (lower because SDM has not been tested on substrate; uncharted regime).

**Cost:** 3-5 CPU-hr.

**Discriminator (3 arms):**
- ARM_SDM_HARD_RADIUS -- Hamming-radius hard locations
- ARM_SDM_SOFTMAX -- softmax-weighted SDM (= Bricken-Pehlevan attention)
- ARM_SDM_KANERVA_TRAINING -- SDM with online hard-location refinement per arxiv 1207.5774

HARD_PASS: any SDM arm >= 0.60 heldout AND >= +0.10 over HRR_BUNDLE baseline.
HARD_FAIL: all SDM arms within 0.05 of HRR_BUNDLE; pivot to BCM/STC.

**Why valuable even at lower P:** SDM is a DIFFERENT mechanism class from BCM. If both BCM and SDM HARD_PASS, substrate has two independent slow-building schema mechanisms; if only one passes, we learn which mechanism class is right for substrate; if neither passes, the bottleneck is data volume not mechanism choice.

---

## Section 4: USER's cold-storage / never-delete principle -- formalized

The USER's reframe from REM homeostasis: **when basins compete, the loser is not deleted; it is cold-stored**. Tested for combination later.

This is exactly the STC mechanism above. Specifically:

- A "weak basin" in substrate = a category prototype with low total mass (few replays accumulated).
- A "strong basin" = a prototype with high total mass.
- The cold-storage rule = the tag bit; the never-delete principle = no overwrite of W_slow without capture.
- The merge rule = capture: a weak basin near a strong recent event gets CAPTURED into the strong basin's consolidated form during the next sleep cycle. The merge is the cortex's actual schema-formation mechanism.

The PNAS 2024 two-factor result is the cleanest mathematical statement: weak basins get MORE relative strengthening than strong ones during replay (because the strong ones are already near their target). The basin landscape automatically equalizes over time. This is the cortex's homeostatic schema-formation -- exactly what the USER's intuition described.

### How does cold-storage compose with Modern Hopfield?

The composition is multiplicative:
1. STC during sleep builds well-separated, comparably-strong basins (the merge step).
2. Modern Hopfield at query time (feature-matching regime n=2) retrieves from those basins.
3. The MERGE step turns multiple weak nearby basins into one cleaner consolidated basin; the FEATURE-MATCHING readout then sums contributions from all surviving basins.

**This is structurally equivalent to: "cortex does the work of pre-clustering; attention does the work of fuzzy lookup."** The brain's mechanism end-to-end. Substrate has all the primitives to implement this; the only missing pieces are the tag bit + PRP + W_slow + capture rule (~40 lines on top of existing infrastructure).

---

## Section 5: Honest scope -- how many cycles?

**Biology:**
- STC tag persistence: ~1 hour (Frey-Morris); recently extended to days via metaplasticity (Tomeo 2025 review).
- Schema rapid-acquisition (Tse-Morris 2007): ~50 NREM cycles = 48 hours with prior scaffold.
- From scratch: ~1000-2000 replays.
- Cortex eta_slow: ~5e-4 (Sun-Wang 2023).

**Substrate translation:**
- For 5 categories x 20 instances at N=8192:
  - STC capture mechanism: each replayed sample fires PRP for that row; tags from prior writes get captured if within tau_PRP. At tau_PRP = 100 cycles and 5000 total replays, each row gets ~1000 PRP-active windows = ~1000 capture opportunities. Schema should form in ~1500-3000 cycles.
- For the cheap diagnostic (Cell 1 above, feature-matching regime): no cycles needed; pure readout change.

**Cycle-count realism:**
- Cheap diagnostic: ~1 CPU-hr.
- STC cell: 6-10 CPU-hr at 5000 replay cycles, 3 arms, 3 seeds.
- SDM cell: 3-5 CPU-hr.

**What's the discriminator that "slow building is working"?**
- Basin separation increasing over replay cycles. Measure: cosine matrix of W_slow columns at cycles 0, 500, 1500, 5000. Within-category cosine should rise; across-category should fall.
- Heldout instance recall improving over cycles. Track every 500 cycles; expect monotone increase if mechanism works.
- Schema-vs-instance distinction emerging. Measure: rank-1 projection of W_slow onto the empirical category-mean directions. Schema directions should grow; instance-specific directions should shrink.

If after 5000 cycles substrate still cannot separate schemas from instances on this metric, the slow-learning HYPOTHESIS itself needs rethinking. That is the FAIL condition for the entire revival direction; HARD_FAIL of both STC and BCM cells would close the slow-building family for this regime and route to "scale data volume first" instead.

---

## Section 6: Recommendation -- top 3 cells ranked

| Rank | Cell name | Mechanism | P_deflated | Cost CPU-hr | Why-now |
|---|---|---|---|---|---|
| 1 | `mh_revival_feature_regime_diagnostic_v1` | Krotov feature regime (n=2) on existing W | 0.45 | 1 | Cheapest test; isolates regime-error from mechanism-error; substrate-product win if it lands |
| 2 | `mh_revival_STC_consolidation_v1` | STC tag + PRP + W_slow + capture rule | 0.40 | 6-10 | Implements USER's never-delete principle mechanically; brain-aligned schema formation; composes with BCM cell |
| 3 | `mh_revival_SDM_online_v1` | SDM hard-locations + softmax pooling | 0.35 | 3-5 | Distinct mechanism class from BCM/STC; tests whether the substrate's failure is mechanism-class or data-volume |

### Why this ranking

Cell 1 is FIRST because it is the cheapest discriminator. If the prior cell's HARD_FAIL was regime selection (wrong n), we learn that in 1 CPU-hr and ship a substrate-product win without building anything new. If Cell 1 also HARD_FAILs, we know the prior cell was not just a regime mistake and the slow-build cells are necessary.

Cell 2 is the brain-aligned revival of Modern Hopfield. It implements the USER's never-delete principle as STC capture. It composes with the BCM cell already in queue (BCM does encoding; STC does consolidation; both write to W_schema/W_slow). If BOTH BCM and STC HARD_PASS, substrate has full brain-aligned cortical schema formation.

Cell 3 is the distinct-mechanism-class cell. SDM is a different organization of memory (hard-locations + pooling) than dense W matrices with BCM/STC. It tests whether the slow-build direction is right but the specific mechanism (BCM vs STC vs SDM) matters. Useful as a cross-mechanism rail.

### Why NOT a 5th-cell "compose-everything"

The USER mentioned "Compose-everything cell: NREM replay + TWO_TIER + BCM + Modern Hopfield retrieval. 5000+ cycles. Tests if substrate can BUILD schemas the brain's way." -- this is exactly the cell already in queue per `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` (gap3_cls_two_tier_BCM_slow_replay_v1). Do not re-dispatch; let it run.

### Dispatch order recommendation

1. Cell 1 (cheap diagnostic) -- 1 CPU-hr; results in <2 hours wall.
2. If Cell 1 HARD_PASS -> ship as substrate-product win; queue Cell 2 for combined-mechanism test.
3. If Cell 1 HARD_FAIL or MIDDLE_BAND -> dispatch Cell 2 (STC) in parallel with the in-queue BCM cell.
4. Cell 3 (SDM) -- queue for after Cell 1 and the BCM cell land; useful as cross-mechanism rail.

---

## Cross-thread synthesis

**With the in-queue BCM cell:** the BCM cell tests slow-write encoding (eta_slow + sliding threshold + W_schema). This drill's STC cell tests slow consolidation (tag + capture + W_slow). They COMPOSE: BCM is the rule used by the cell during one consolidation event; STC is the rule that decides WHICH writes get consolidated across time. The brain uses both simultaneously. Recommendation: if Cell 1 (diagnostic) HARD_PASS, do Cell 2 (STC) standalone; if Cell 1 HARD_FAIL, COMBINE BCM and STC into one cell with both write rules active.

**With the NREM drift_reduction +0.57 proven-bound result:** the replay engine is established. STC uses the SAME replay engine, just routes the output to a different consolidation rule. The proven-bound REMAINS VALID for the existing W; W_slow with STC is additive.

**With Fix #28 (verify per-arm metrics):** all arms in all 3 cells must report per-arm metrics; verdict_msg insufficient. Cell 2 STC must report PRP-firing-rate, capture-rate, and tag-decay-rate per arm independently. These are mechanism-internal metrics that tell us WHICH part of STC is load-bearing.

**With Fix #26 (pre-dispatch verify-the-referent):** before dispatching Cell 2, run `tools/predispatch_check.py mh_revival_STC` to verify no prior STC cell exists in atoms.jsonl. Quick grep confirms: substrate has not yet tried STC. This is the first dispatch and substrate-novel.

**With the field-yield advisor (saturated fields):** `materials-physics` and `inference` are saturated; this drill is in `theoretical neuroscience` (CLS, STC, SDM) which is fruit-bearing per Gap 3 drill. Stays in fruit-bearing territory.

**With USER's REM homeostasis insight:** USER's reframe earlier this cycle was about REM-not-NREM homeostasis (losing basins should be cold-stored not deleted). This drill formalizes that as STC. If the connection holds, the same STC mechanism that builds schemas during NREM should also prevent catastrophic forgetting during REM-like exploration phases.

---

## Substrate-product implications

**If Cell 1 (feature regime diagnostic) HARD_PASS:**

Headline product story: "Modern Hopfield works on substrate -- in the feature-matching regime, not the prototype regime. Substrate-product gets soft-attention readout that beats nearest-neighbor without any new write-side machinery. Cheap improvement; ships immediately."

**If Cell 2 (STC) HARD_PASS:**

Headline product story: "Substrate's auditable memory subsystem now consolidates by the brain's actual cross-time merge rule. Weak associations near strong recent events get captured into the schema; isolated weak associations fade by neglect. No catastrophic deletion; no catastrophic overwrite. The never-delete principle, mechanically."

**If Cell 1 + Cell 2 + the in-queue BCM cell ALL HARD_PASS:**

Headline product story: "Substrate now implements the brain's full cortical schema pipeline end-to-end: BCM encoding rule + STC consolidation rule + feature-matching attractor retrieval, on top of NREM replay engine and TWO_TIER storage. Each piece has brain-existence proof; the implementation is auditable; the math is closed-form. This is the differentiator vs vector-DBs (no consolidation, no schema) and LLMs (no audit trail). Substrate has both with full audit."

**If Cell 1 HARD_FAIL:**

Diagnosis: regime selection was not the prior failure mode. The substrate's W truly lacks the basin structure for any attractor-class retrieval at this regime. Cell 2 and BCM cell become the critical path. Slow-build is the only remaining direction; if those also HARD_FAIL, we conclude the bottleneck is information-theoretic (need more instances per category) not mechanism-theoretic.

**Capability-map implication:** the Modern Hopfield row currently RED. HARD_PASS of Cell 1 promotes to YELLOW (regime fix). HARD_PASS of Cell 2 promotes to GREEN if discriminator design tests pass.

**Atomization on HARD_PASS:**
- Cell 1 pass: atom `modern_hopfield_feature_regime_substrate_n2_outperforms_prototype` -- "Substrate's Modern Hopfield works in feature-matching regime (n=2) not prototype regime (softmax). Closed-form math; cell-verified."
- Cell 2 pass: atom `STC_capture_consolidation_substrate_native` -- "Substrate's brain-aligned consolidation mechanism: synaptic tag bit + per-row PRP + capture rule writes weak-near-strong associations into W_slow during replay. Closed-form math; cell-verified."
- hdlab primitive: `hdlab/STC_consolidation.py` exposing `stc_capture(W_fast, W_slow, tag, PRP, replay_batch)`.
- Capability-suite regression test: `tests/test_STC_consolidation.py` -- 5cat x 20 instances heldout >= 0.65.

---

## Citations (verified count = 17 external + 9 internal = 26 distinct sources)

**Modern Hopfield / Dense Associative Memory:**
1. Krotov, Hopfield (2016). "Dense Associative Memory for Pattern Recognition." NIPS 2016. arxiv 1606.01164.
2. Ramsauer et al. (2020). "Hopfield Networks is All You Need." arxiv 2008.02217.
3. Schimunek et al. (2021). "Modern Hopfield Networks for Few- and Zero-Shot Reaction Template Prediction." arxiv 2104.03279.
4. Furst et al. (2021). "Modern Hopfield Networks with InfoLOOB Outperform CLIP." arxiv 2110.11316.
5. McAlister et al. (2024). "Prototype Analysis in Hopfield Networks with Hebbian Learning." arxiv 2407.03342. (Direct on capacity-vs-prototype tradeoff.)

**STC / synaptic tagging and capture:**
6. Frey, Morris (1997). "Synaptic tagging and long-term potentiation." Nature 385: 533-536.
7. Redondo, Morris (2011). "Making memories last: the synaptic tagging and capture hypothesis." Nat Rev Neurosci 12: 17-30.
8. Lehr et al. (2021). "Memory consolidation and improvement by synaptic tagging and capture in recurrent neural networks." Communications Biology 4: 275. nature.com/articles/s42003-021-01778-y.
9. Benoy et al. (2025). "Temporal Flexibility in Associative Memory: Insights From Synaptic Tagging and Capture." Eur J Neurosci. doi.org/10.1111/ejn.70258.
10. Tomeo (2025) review on extended STC temporal flexibility. PMC PMC11968991.

**Two-factor / preferential strengthening / homeostasis:**
11. Susman et al. (2024). "Two-factor synaptic consolidation reconciles robustness with pruning and homeostatic scaling." PNAS. doi.org/10.1073/pnas.2422602122.

**SDM / sparse distributed memory:**
12. Kanerva (1988). Sparse Distributed Memory. MIT Press.
13. Bricken, Pehlevan (2021). "Attention Approximates Sparse Distributed Memory." NeurIPS 2021. arxiv 2111.05498.
14. Bricken (2023). "Sparse Distributed Memory is a Continual Learner." arxiv 2303.11934.

**CLS / BCM background:**
15. Bienenstock, Cooper, Munro (1982). BCM theory.
16. McClelland, McNaughton, O'Reilly (1995). CLS theory.
17. Tse, Morris et al. (2007). "Schemas and memory consolidation." Science 316: 76-82.

**Internal substrate notes:**
- notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md
- notes/research_brain_hippocampal_SWR_sleep_replay_5x_drill_2026-06-22.md
- notes/research_modern_hopfield_PCN_AM_universal_kernel_2x_2026-06-17.md
- notes/research_modern_hopfield_capacity_retrieval_crossover_2026-06-16.md
- notes/research_sparse_hopfield_win_regime_2026-06-16.md
- notes/research_gap3_compositional_5x_drill_2026-06-26.md (gap3 mechanism survey)
- hdlab/iterative_attractor.py (existing cleanup primitive; SDM extension target)
- hdlab/predictive_coding.py (existing gated_write; STC extension target)
- data/exp_modern_hopfield_prototype_attractor_v1/metrics.json (the HARD_FAIL anchor)

---

## Lit-scan calibration notes

- All probability estimates deflated 0.15-0.25 from raw LM confidence per [[feedback-lit-scan-calibration-penalty]].
- Novel-synthesis cap at 0.50 applied to Cells 2 and 3 (STC and SDM substrate-specific composition has no direct published precedent at HD-substrate scale).
- HARD-FAIL thresholds mandatory and listed for every prediction.
- DIRECTIONALITY (slow-build is the missing piece; STC is the right merge rule; feature-regime not prototype-regime) is HIGHLY confident -- 4 independent lit-anchors: Krotov 2016 (2-regime distinction), Lehr 2021 (STC in RNNs works), Susman 2024 (two-factor consolidation preferentially strengthens weak memories), Bricken 2023 (SDM is a continual learner). MAGNITUDE (substrate-specific HARD_PASS at this regime) is where deflation hits.
- Fields drilled: theoretical neuroscience (STC, CLS, BCM, SDM); associative memory (Krotov-Hopfield regime analysis); dense associative memory ML revival. 3+ disparate fields converge. Meets Trigger F aggressive cross-domain.
- Substrate-novel angle: substrate has not yet tried (a) feature-matching regime n=2 on existing W, (b) STC tag-and-capture consolidation, (c) SDM hard-locations + pooling. All three are first dispatches.
- Per [[feedback-empowered-to-experiment-where-lit-says-dismissed]]: STC has been shown to work in RNNs (Lehr 2021); no published precedent at HD-substrate scale yet, but the math transfers cleanly. SDM has been shown to be a continual learner (Bricken 2023); substrate-native pooling variant is novel synthesis.

---

## Plain-English wrap (USER-focused)

Modern Hopfield prototype cell failed because we asked the wrong question. The prototype regime of Modern Hopfield (softmax, large n) is designed for the case where you have many strong well-separated basins -- like a dictionary lookup. We applied it to a case where the basins are weak and overlapping (20 instances per category at N=8192). It snapped to wrong answers.

There are three ways out, in order of cheapness:

1. **Switch regime.** Krotov's same family has a feature-matching mode (small n) where many weak basins COOPERATE rather than one dominating. About 1 hour of compute to test. If it works, we get a 2x lift over baseline with no new architecture.

2. **Slow-build basins before retrieval.** This is the brain's actual approach. The brain takes weeks to build cortex basins via interleaved replay + slow learning + synaptic-tagging-and-capture (STC) consolidation. Substrate has the replay engine; needs ~40 lines of new code for STC. 6-10 hours of compute. Implements the USER's never-delete principle exactly: weak memories near strong recent events get CAPTURED into the schema; isolated weak memories fade slowly. No catastrophic deletion.

3. **Different mechanism class.** Sparse distributed memory (SDM) organizes memory differently -- hard locations in HD space with overlap pooling. Direct substrate-product fit. 3-5 hours of compute. If both BCM-with-STC AND SDM work, substrate has two independent paths to slow-built basins.

The USER's intuition that "we don't have enough data and we should be able to fix that over time" is exactly right. The substrate has the data; what it lacks is the SLOW CONSOLIDATION MACHINERY to turn 20 instance-traces into a usable category basin. That machinery has been mapped neuroscientifically (STC + BCM) and has substrate-feasible code costs.

Recommendation: dispatch the cheap diagnostic FIRST (1 hour). If it HARD_PASS, ship the regime fix as a substrate-product win. If it HARD_FAIL, dispatch STC cell in parallel with the BCM cell already in queue. Either way, we know within 2 hours whether the bottleneck is mechanism choice or fundamental data volume, and we have brain-aligned options for both directions.

---

-- Research (Opus 4.7 1M synthesis; 6 parallel WebSearch lit-scans converged on Krotov 2-regime + STC + two-factor consolidation + SDM continual-learner revival; calibrated per discipline; HARD-FAIL thresholds pre-registered).
