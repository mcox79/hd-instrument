# RESEARCH 5x DEEPER DRILL: Hippocampal Sharp-Wave-Ripples (SWR) + Sleep Replay — biological replay MACHINERY for substrate

**Date:** 2026-06-22
**Requestor:** Skunkworks (USER STANDING biology/brain/nature drilling cadence — drill #5, extending #2)
**Parent drill:** `notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md` (CLS dual-store + 1:1 Hebbian replay; HEADLINE-level intuition)
**Empirical anchor on substrate:** c1 CLS-replay cell PARTIAL data (`notes/c1_cls_replay_continual_ingest_complete_2026-06-22.md`) — NONE@α=0.5 = 1.000 task-A recall (codebook-NN cleanup MORE robust than a8-extrapolation predicted; the replay-rescue hypothesis cannot fire at the pre-reg load because the baseline does NOT collapse). The substrate is operating BELOW the cliff at α=0.5 under codebook-NN; cliff lives somewhere above. c1 is honest-negative-at-load-as-pre-registered; the science finding is substrate-FAVORABLE.
**Lit-scan calibration:** deflate P 0.15-0.25; cap novel-synthesis P at 0.50; HARD-FAIL bands mandatory.

---

## HEADLINE — plain English first (Fix #13)

**The c1 result FLIPS the question.** Drill #2 asked: "does 1:1 Hebbian replay rescue the substrate from catastrophic forgetting?" — but the substrate doesn't visibly forget at α=0.5 under codebook-NN cleanup. So drill #5 reframes: **what is biological sleep replay actually FOR, beyond the 1:1 cortex-reinforcement that drill #2 already covers?** The neuroscience answer, drilled in 4 streams, is that **sleep replay does FOUR things 1:1 Hebbian replay does NOT**:

1. **TEMPORAL COMPRESSION (~20x speedup; Wilson & McNaughton 1994; Lee & Wilson 2002).** ~2s of waking trajectory replays in ~100ms. The key biological consequence: Hebbian plasticity has a fixed temporal window (50-200ms). Events that were SECONDS apart in waking experience get COMPRESSED into the 50-200ms Hebbian window during replay — so the brain LEARNS LONG-RANGE TEMPORAL ASSOCIATIONS DURING REPLAY THAT IT COULD NOT LEARN ONLINE. This is the actual computational primitive: **sleep replay is the only time the brain can Hebbian-link sequence elements that were too far apart in real-time.**
2. **PRIORITIZED REPLAY (not uniform sampling; Michon et al. 2025; Joo & Frank 2018).** SWRs preferentially replay NOVEL + REWARDED + SURPRISING experiences. Replay content is BIASED by salience, not drawn uniformly from the episodic store. Reward-prediction-error-biased replay outperforms uniform replay (Mattar & Daw 2018; Liu et al. 2021). The brain is doing prioritized experience replay (PER) at the SWR level — the same prioritization that DQN-PER discovered ML-empirically.
3. **OFFLINE + LIMITED-WAKE TIMING WINDOW.** SWRs fire ~5-10/sec during slow-wave sleep + quiet wakefulness ONLY (suppressed during active exploration; Buzsáki 2015). The brain has a strict consolidation SCHEDULE — replay does NOT compete with new ingest. This maps cleanly to substrate: batch consolidation between ingest episodes.
4. **CORTEX-SPINDLE-RIPPLE COUPLING (Klinzing 2019; Helfrich 2018).** Hippocampal SWRs are PHASE-LOCKED to thalamocortical spindles (~12 Hz) on the down-to-up transition of cortical slow oscillations (~1 Hz). Cortical plasticity is GATED to the UP-state. The brain transfers hippocampus→cortex only when cortex is RECEPTIVE — not continuously. The substrate analogue: gate the W-write to a "consolidation phase" with elevated learning rate; freeze W during ingest of new episodic facts.

**Substrate-product implications, plain:** drill #2's 1:1 Hebbian replay (c1) tests ONE of these four; the other three are SEPARABLE mechanisms each pre-registrable as its own cell. The NOVEL synthesis for substrate is **sleep-replay as a SEQUENCE-LINKING mechanism**, not just a forgetting-rescue. The substrate today has NO sequence-binding primitive — every fact is a point (key, value) pair. Compressed-replay would let the substrate Hebbian-link (k_t-1, k_t) pairs that were ingested SECONDS apart in wall-time, building a sequence graph implicit in W. This is the substrate's missing PIECE for substrate-LM autoregressive decode (drill on within-concept floor #1's bigram-gap of 1.12 bits is the symptom: the substrate has no temporal-association primitive). **Sleep-replay-compressed-binding is the candidate primitive.**

**The cheap decisive test (this drill's recommended cell):** `c3_compressed_sequence_replay_v1` — given a sequence of K=20 ingested facts that were ingested SEPARATELY (each as a point write to W), run a "sleep" pass that samples ordered (k_t-1, k_t) PAIRS from U1 in temporal order at 1ms intervals (= 20x compression vs 20ms original spacing), and Hebbian-binds the pair into a SEPARATE sequence matrix S. Test recall: given k_t-1, does S @ k_t-1 retrieve k_t? HARD-PASS at recall ≥ 0.80 for sequence depth 5+ on 10 distinct sequences; no LLM forward calls; substrate-only-decode preserved.

| Mechanism (SWR sub-mechanism) | Source | Substrate-applicability | Substrate-cost | Expected gain | P(HARD-PASS) |
|---|---|---|---|---|---|
| **Compressed-sequence Hebbian binding (novel synthesis; the SWR-specific primitive)** | Wilson & McNaughton 1994; Mehta 2007 (compression buys long-range associativity); Liu et al. 2019 (compressed replay supports inference) | **HIGHEST** — adds a sequence-link primitive the substrate lacks; forward-only; composable with U1 + W; the actual substrate-LM moat seed | ~1.10x ingest wall (offline pass after each episode) | sequence-recall 0 → 0.80+ at depth 5; bigram-gap closure path opened | **0.40** (cap novel-synthesis 0.50; deflated 0.10 for substrate-specific composition unknowns) |
| **Prioritized replay (novelty + RPE + surprise biased sampling)** | Mattar & Daw 2018 (Nat Neurosci); Michon et al. 2025; Liu et al. 2021 PER | HIGH — orthogonal to compression; samples from U1 by salience, not uniform | ~nil (just changes sampling distribution) | improves replay budget efficiency 2-5x over uniform; lifts retention at fixed replay count | 0.45 |
| **Sleep-stage gated cortex learning rate** | Klinzing 2019; Diekelmann & Born 2010; Helfrich 2018 spindle-coupling | MEDIUM — substrate has no "sleep stage" notion; encode as `consolidation_mode` flag with elevated η_W during replay-only pass | small wall change | rescues large-α retention IF cortex-write-during-ingest is the actual interference source | 0.30 |
| **Awake replay (planning / on-line; not sleep)** | Pfeiffer & Foster 2013; Foster 2017 awake forward/reverse | MEDIUM — substrate has no decision-task; awake replay implements planning trajectories; relevant to a future agent-substrate composition, not current cell roadmap | n/a (not a cell now) | DEFER (depends on agent task) | DEFER |
| **Theta-gamma phase precession (encoding-vs-retrieval phase gating)** | Lisman & Jensen 2013; Tort 2008-2024 | LOW — gating phases not directly representable on substrate's static W; the IDEA (separate encode/retrieve cycles) is already captured by sleep-gate | nil | nil novel | reframe as `sleep-gate` |
| **Reverse replay (reward-credit assignment)** | Foster & Wilson 2006; Ambrose et al. 2016 | MEDIUM-LOW — useful for RL-substrate; not the current substrate-LM roadmap | n/a | n/a | DEFER |

**Cheap decisive test (Phase 1):** `c3_compressed_sequence_replay_v1` at K=20 sequence length, N_DIM=4096, 10 distinct sequences, 3 seeds. **HARD-PASS: depth-5 sequence recall ≥ 0.80 WITH compressed-replay AND ≤ 0.20 WITHOUT (point-write-only control). HARD-FAIL: delta < 0.20 OR substrate-only gate violated.**

---

## L1 — LITERATURE BROAD SCAN (4 parallel streams)

### Stream A: SWR machinery + temporal compression (Buzsáki / Wilson / Foster)

- **Buzsáki (2015, Hippocampus) "Hippocampal sharp wave-ripple: a cognitive biomarker."** Canonical review. SWRs are population events 50-150ms long, peak frequency 140-220Hz in CA1 (the "ripple"), riding on a 30-100ms-duration LFP "sharp wave" generated by synchronous CA3 input. **Rate: ~5-10/sec during slow-wave-sleep + quiet awake; ~0/sec during active theta exploration.** Spike content within a SWR = temporally compressed reactivation of waking sequences. ~30% of CA1 cells participate in any given SWR.

- **Wilson & McNaughton (1994, Science).** The canonical sleep-replay paper. Place-cell ensembles from awake spatial exploration FIRE in the same order during post-task slow-wave-sleep SWRs — at ~20x temporal compression (a 2-second running sequence replays in ~100ms). Co-firing structure is preserved.

- **Lee & Wilson (2002, Neuron).** Quantitative replay measurement. Multi-cell sequences (3-7 cells) replay during SWRs in correct temporal order with high statistical significance. Compression factor ~20x confirmed.

- **Pfeiffer & Foster (2013, Nature).** Hippocampal FORWARD trajectory representations during pauses in active behavior — "awake forward replay" — anticipate future paths to goal locations. **Mechanism: hippocampus is doing forward simulation/planning during quiet-wake SWRs, not just consolidation.** Foster (2017, Ann Rev Neurosci) review consolidates: awake forward replay = planning; awake reverse replay = reward-credit assignment; sleep replay = consolidation. Three distinct functional modes, all SWR-mediated.

- **Mehta (2007); Buzsáki & Tingley (2018).** **The capacity-relevant insight: compressed replay creates Hebbian-learnable associations between events that were too far apart in waking time.** Hebbian STDP windows are 50-200ms. Two events 2 seconds apart in waking cannot Hebbian-bind directly. After 20x compression, they're 100ms apart — INSIDE the Hebbian window. **Compression is not a wall-time optimization; it's the mechanism by which long-range temporal associations become learnable at all.**

- **Buzsáki (2015) + 2022 eLife model (Ecker et al.) "Hippocampal SWRs from structured synaptic interactions in a CA3 network."** Mechanism for SWR generation: recurrent CA3 inhibition + sparse excitation produces self-organizing replay events. Substrate-relevant: the replay generator IS a recurrent autoassociative attractor — exactly the U1 multi-value KG structure (CERT 584). The substrate has the GENERATOR latent.

- **Norman et al. (2019, Science) human SWRs.** "Hippocampal sharp-wave ripples linked to visual episodic recollection in humans." SWRs in humans (intracranial recording) trigger during free recall — confirms SWRs as a CROSS-SPECIES memory primitive, not a rodent-only artifact.

### Stream B: Awake vs sleep replay; forward vs reverse; functional dissociation

- **Foster & Wilson (2006, Nature).** Reverse replay in awake rats after reward — sequence plays BACKWARD from reward back to start. Mechanism: temporal-credit-assignment for reinforcement learning (assigning credit to actions that LED to reward).

- **Ambrose, Pfeiffer & Foster (2016, Neuron).** Reverse replay frequency scales with reward magnitude; forward replay scales with novelty + upcoming-choice uncertainty. **Distinct functional roles within the SWR system.**

- **Tang et al. (2019, eLife) "Awake hippocampal-prefrontal replay mediates spatial learning and decision making."** Coordinated hippocampus-prefrontal replay correlates with future-correct-choice in working-memory tasks. The replay is functionally CAUSAL: blocking SWRs impairs learning (Jadhav et al. 2012).

- **Olafsdóttir et al. (2018) review.** Awake replay during deliberation pauses CONTAINS the trajectory the animal is about to take (planning) OR the trajectory just rewarded (consolidation+credit-assignment). Replay is not random.

- **Practical timing data:** awake quiet-wake SWRs ~1-3/sec at reward sites; sleep SWRs ~5-10/sec during slow-wave sleep. Total daily SWRs ~50k-200k. Each replays 5-30 cells = a fragment of one trajectory. Cumulative replay coverage per waking experience ~1-3x in following sleep (the 1:1 to 3:1 replay-to-experience ratio from drill #2).

### Stream C: Theta-gamma coupling + cortex-spindle-ripple coordination

- **Lisman & Jensen (2013, Neuron).** Theta-gamma neural code. **Theta (4-9Hz) defines encoding/retrieval phases; gamma (40-140Hz) cycles within theta represent individual items.** Encoding occurs on theta-trough; retrieval on theta-peak (opposed phases). This is the brain's "duplex" mode separating WRITE from READ within the same circuit.

- **Tort et al. (2024) review "Theta-gamma coupling as a ubiquitous brain mechanism."** Cross-frequency coupling (CFC) is the dominant memory-coding mode in hippocampus.

- **Helfrich et al. (2018, Neuron); Klinzing et al. (2019, Nat Neurosci).** Hippocampal SWRs are phase-locked to thalamocortical SPINDLES (~12 Hz, 0.5-2s bursts during NREM N2/N3 sleep), which themselves nest on cortical slow oscillations (~1 Hz UP/DOWN states). **Triple-coupling: SO_UP-state → spindle peak → SWR.** Cortical plasticity is gated to UP-state. Memories that get this triple-coupling consolidate better; out-of-phase ones don't (PLoS Bio 2024 thalamic-spindle co-ripple).

- **Quantitative timing:** UP-state ~500ms; spindle ~1s bursts containing ~10-20 cycles; SWR ~50-100ms nested in spindle peaks. ~10 SWRs/spindle/UP-state. Per 8hr sleep: ~10k-30k SWR events total — the brain has a **finite consolidation budget per sleep epoch**.

- **Substrate-relevant insight:** the cortex (= substrate W) is NOT continuously plastic. It's plastic in DISCRETE WINDOWS gated by sleep-state. This contradicts the substrate's current implicit "always-plastic W" — and suggests that gating the W-update to a "consolidation phase" (instead of every ingest) may IMPROVE retention by avoiding interference from new-ingest writes.

### Stream D: Prioritized replay + ML re-validation (Mattar/Daw → Liu/Schrittwieser → 2025 SHARP)

- **Mattar & Daw (2018, Nat Neurosci) "Prioritized memory access explains planning and hippocampal replay."** Mathematical theory: hippocampal replay implements PRIORITIZED EXPERIENCE REPLAY where priority = NEED (current-state proximity) × GAIN (Bellman-update-magnitude). Predicts (and matches data): forward replay before reward-relevant choices; reverse replay after unexpected rewards; novel locations replayed more. Substantially out-performs uniform sampling.

- **Liu et al. (2019, Cell) "Human Replay Spontaneously Reorganizes Experience."** Magnetoencephalography in humans: replay during rest reorders observed pairs into INFERRED chains — i.e. replay does TEMPORAL INFERENCE (combine A→B with B→C to learn A→C) via compressed-replay sequence-binding. This is the **multi-hop reasoning substrate** the brain runs during sleep.

- **Joo & Frank (2018, Nat Neurosci) review "The hippocampal sharp wave-ripple in memory retrieval for immediate use and consolidation."** Synthesis: SWRs are the SUBSTRATE for both immediate planning (awake) AND long-term consolidation (sleep). Same primitive, two functional modes.

- **Michon et al. (2025, PMC PMC10659301) "Selection of experience for memory by hippocampal sharp wave ripples."** SWR content is BIASED toward salient experience — novelty, reward, surprise. Awake-SWR-replayed experiences are then preferentially replayed in sleep. **The brain implements a 2-stage prioritization filter: awake-SWR tags salient experiences, sleep-SWR consolidates the tagged.**

- **Nat Comm 2025 "Post-learning replay of hippocampal-striatal activity is biased by reward-prediction signals"** — direct neurobiological confirmation of RPE-biased replay.

- **Schaul et al. (2016) DQN-PER.** ML re-discovery: prioritized experience replay outperforms uniform 2-5x on Atari. Priority = TD-error magnitude (the ML analog of RPE).

- **Arxiv 2606.00732 (2026) "SHARP: Sleep-based Hierarchical Accelerated Replay for Long Range Non-Stationary Temporal Pattern Recognition."** Direct ML re-implementation of compressed-replay for long-range temporal patterns — confirms COMPRESSION buys learnable-window-extension on standard ML architectures.

- **Arxiv 2402.01467 "Brain-Like Replay Naturally Emerges in Reinforcement Learning Agents."** Even without explicit design, RL agents trained to maximize reward DEVELOP brain-like prioritized + reverse replay patterns. The architecture is convergent.

---

## L2 — FILTER TO SUBSTRATE-APPLICABLE

| SWR sub-mechanism | Forward-only / Hebbian-compatible? | Composes with U1 + W + c1 replay-loop? | Distinct from c1's already-tested 1:1 replay? | Verdict |
|---|---|---|---|---|
| **Compressed-sequence Hebbian binding** | YES (replay at 1ms instead of 20ms; same outer-product write) | YES — adds a `sequence_matrix S` orthogonal to W; or augments W with cross-time terms | **YES — c1 only writes (k, v) pairs at one time; this writes (k_t-1, k_t) ordered pairs** | **ACCEPT — primary novel addition** |
| **Prioritized replay (novelty + RPE bias)** | YES (just changes sampling distribution from U1) | YES — drop-in replacement for c1's uniform replay sampler | **YES — c1 samples uniformly; this samples by salience** | **ACCEPT — drop-in upgrade to c1's replay loop** |
| **Sleep-stage gated cortex learning rate** | YES (toggle η_W between modes) | YES — gate W-update to "consolidation_mode = on" phases | PARTIAL — c1's batch_1to1 hints at this; this formalizes the gate | **ACCEPT — secondary; pairs with c1's batch_replay arm** |
| **Cortex-spindle-ripple triple-coupling** | YES (architectural: nested loop structure) | YES but requires "spindle" intermediate stage between U1 and W | Distinct (multi-level architecture) | **ACCEPT but DEFER — too speculative without intermediate stage in substrate** |
| **Awake replay (planning)** | YES | YES (would consume U1 at decision-time) | Distinct (decision-task, not ingest) | **DEFER — agent-task dependent; not current roadmap** |
| **Reverse replay (RL credit)** | YES (reverse iteration over U1 sequence) | YES | Distinct | **DEFER — RL-substrate, not current** |
| **Theta-gamma phase precession** | NO (substrate has no oscillatory time-axis) | n/a | n/a | **REJECT but ADOPT THE PRINCIPLE: separate write-mode from read-mode (= the sleep-gate)** |

**Net: 3 ACCEPT, 1 DEFER-architecture, 2 DEFER-task, 1 REJECT-but-principle-absorbed.**

---

## L3 — DEEP DRILL ON TOP MECHANISMS

### 3.1 Compressed-sequence Hebbian binding (PRIMARY NOVEL CONTRIBUTION)

**The mechanism in one paragraph:** during ingest, the substrate writes facts (k_i, v_i) at wall-time intervals ~20ms-1s apart. There is NO direct Hebbian link between (k_i) and (k_{i+1}) because the writes are independent outer-products to W. During a "sleep" pass, the substrate iterates over U1 in temporal order, and at 1ms-spacing fires ADJACENT pairs (k_{i-1}, k_i) — well inside any plausible "Hebbian window" — and writes the OUTER PRODUCT k_{i-1} ⊗ k_i into a separate sequence matrix S. After sleep: S @ k_{i-1} ≈ k_i. The substrate now has a SEQUENCE GRAPH it could not have built online.

**Mathematical formalism.** During the awake ingest phase, write to W (the substrate's existing semantic store):
```
W += η_W · (k_i ⊗ v_i)        # standard substrate Hebbian write
```
During the offline-sleep phase, iterate U1 in temporal order (i = 1..N), and for each adjacent pair:
```
S += η_S · (k_{i-1} ⊗ k_i)    # sequence link
```
At test time, sequence-recall is:
```
k_t_predicted = codebook-NN(S @ k_{t-1})
```
The compression buys nothing computationally in software (we don't have a 50-200ms Hebbian window; we have whatever-the-CPU-does). **What it buys is the ABILITY to link items that were never online-adjacent — items separated by hours or days of waking ingest become adjacent in the temporal-ordered U1 walk.** This is a substrate primitive the current architecture lacks.

**Why this directly attacks the within-concept-floor bigram-gap (drill #1 finding, 1.12 bits):** the substrate has no temporal-conditional structure today. Bigram log-likelihood = log P(w_t | w_{t-1}) — but the substrate's W has no link between w_{t-1} and w_t; only between concepts and values. Compressed-replay builds exactly that link in S. **Predicted gain: bigram-floor of 1.12 bits + bigram-conditional structure that closes substantial decode-side gap.**

**Why this is biologically tight (not metaphor):**
- Sleep replay is observed to compress spike sequences by 10-20x (Lee & Wilson 2002; Karlsson & Frank 2009).
- Mehta (2007) directly argues the function is to bring temporally-distant events into the STDP window.
- Liu et al. (2019, Cell, human MEG) demonstrate replay re-orders observed pairs into inferred chains during sleep — the multi-hop generalization the substrate's W cannot do directly.

**Substrate-cost:** an extra pass over U1 per "sleep epoch" — say once per 5k-fact ingest batch. Wall-time: U1-walk is O(N) outer-products at N_DIM=4096 ≈ 5k * 16M ops ≈ 80G ops ≈ 8-10s per sleep epoch on CPU. **Negligible relative to ingest wall.**

**Composition with c1's replay loop:** c1's ONLINE_1to1 replay re-presents (k_old, v_old) → re-reinforces W. The proposed S-loop additionally writes (k_{t-1}, k_t) ordered pairs → builds a sequence graph. ORTHOGONAL primitives. Composition predicted multiplicative for sequence-modeling tasks; orthogonal for one-shot recall.

**Cell design (`c3_compressed_sequence_replay_v1`):**
- 10 distinct sequences, each K=20 facts in defined temporal order, all written as point-writes to W (no built-in sequence link).
- Sequence-recall test: given k_{t-1}, predict k_t via S @ k_{t-1} + codebook-NN.
- Arms: A = NONE (no sleep pass; pure point-writes); B = COMPRESSED_REPLAY (sleep pass writes ordered pairs into S at 1ms compression); C = UNORDERED_REPLAY (sleep pass writes RANDOM pairs into S — discriminator showing the ORDER is what matters); D = ONLINE_NO_GAP (writes k_{t-1} ⊗ k_t into S at ingest-time directly — the "no-compression" control showing that the offline-replay phase is necessary, not the pair-write itself).
- HARD-PASS: arm B sequence-recall ≥ 0.80 at depth 5; arm A ≤ 0.20; delta ≥ 0.50; arm C < arm B (order matters); arm D ≈ arm B (showing the magic is the PAIR-WRITE, not the temporal compression in software — this is the honest scope limit and the "compression is the biological license to do this, software just does it"). cv ≤ 0.05 across 3 seeds. zero LLM calls. Substrate-only-decode gate.
- HARD-FAIL: arm B - arm A < 0.20 at any depth ≥ 3.

### 3.2 Prioritized replay (drop-in upgrade to c1's sampler)

**Mechanism.** c1's ONLINE_1to1 currently samples from U1 uniformly. The neuroscience says SWRs preferentially replay NOVEL + REWARDED + SURPRISING experiences. Substrate-applicable priority signals:

- **Novelty proxy**: time since last replay (long unreplayed → high priority); inverse of count of times the item has been replayed.
- **RPE proxy**: substrate-decode-error at the time of write — items with high reconstruction error after write are "surprising" → high priority.
- **Salience proxy**: refuse-gate score (items the gate barely accepted are near-boundary → informative).

**Mattar & Daw 2018 formula adapted:** priority(i) = NEED(i) × GAIN(i) where NEED = forecasted retrieval probability and GAIN = the Bellman-update-magnitude. Substrate translation: NEED = inverse-recency; GAIN = current W-error on (k_i, v_i).

**Expected gain:** 2-5x replay-budget efficiency (Schaul 2016 + Liu 2021 + Michon 2025 all converge on this magnitude). For the substrate, this means at FIXED replay budget (1:1 in c1) you get the same retention as a 2-5x replay budget under uniform sampling — OR at SHRUNK budget (1:0.25) you match uniform-1:1 retention. **The budget shrink IS the value: lower wall-time at same retention.**

**Cost:** trivial (priority computation is O(|U1|) per epoch; sampling becomes weighted).

**Cell design (`c4_prioritized_replay_v1` — secondary):**
- Re-runs c1's structure but with ONLINE_1to1_PRIORITIZED vs ONLINE_1to1_UNIFORM (= c1's existing arm).
- Three priority schemes: NOVELTY, RPE, REFUSE-MARGIN.
- HARD-PASS: at α_high (where c1 begins to break), PRIORITIZED retention ≥ UNIFORM retention + 0.10 (replay-budget efficiency win); OR at fixed retention target, PRIORITIZED uses ≤ 50% of UNIFORM's replay budget.

**NOTE:** this cell DEPENDS on c1's full result. If c1 lands HARD-PASS at all-arms-1.0 (the partial-data trajectory), this cell needs a HARDER scenario to discriminate — probably push to α > 1.0 or use raw-cosine recall instead of codebook-NN. Defer cell-spec finalization until c1 lands and we know where the substrate actually breaks.

### 3.3 Sleep-stage gated learning rate (composable with both)

**Mechanism.** Today, every ingest call writes to W with the same η. Biology: cortex W is plastic ONLY during sleep UP-states; mostly frozen during awake. Substrate translation:

```python
if mode == "ingest":     η_W = 0       # don't write cortex during episodic ingest
                         U1.append(k, v)  # only write hippocampus
elif mode == "replay":   η_W = η_high   # transfer hippocampus → cortex
                         W += η_W * Σ_replay (k_replay ⊗ v_replay)
```

**Why this might help (counter-intuitive given a8 result):** today the W matrix accumulates BOTH new ingest writes AND (with c1's replay) replay writes. The two writes interfere because they overlap in the same W. Gating predicts: if you write ONLY during replay (sourcing facts from U1), W experiences less interference per unit time. **The a8 saturation curve may move.**

**HOWEVER**, this is the LEAST-confident of the three because the substrate's W is mathematically very different from a biological cortex (continuous superposition vs sparse-spiking-LTP). The neuroscience analogy may not transfer. Predict 0.30 P(HARD-PASS) — low-confidence drill.

**Cell design (`c5_sleep_gated_cortex_v1` — tertiary):**
- Arm A: write W on every ingest + replay (= c1 baseline).
- Arm B: write W ONLY during periodic "sleep" passes sourced from U1 (no W-write during ingest).
- HARD-PASS: arm B retention ≥ arm A retention by ≥ 0.10 at α_high.

---

## L4 — CELL-DESIGN IMPLICATIONS + PRE-REG

### Primary cell: `c3_compressed_sequence_replay_v1`

**Scope.** Sequence-recall test. K=20 facts ingested in defined order; sleep-pass writes ordered adjacent pairs into a separate sequence matrix S; test recall at depths 1-10 down the chain.

**Independent variables:**
- `arm` ∈ {NONE, COMPRESSED_REPLAY, UNORDERED_REPLAY, ONLINE_NO_GAP}
- `sequence_depth` ∈ {1, 3, 5, 7, 10} (how many steps to predict ahead)
- `n_sequences` = 10 (distinct chains)
- 3 seeds (7, 17, 23)

**Fixed:**
- N_DIM = 4096
- K = 20 facts per sequence
- Synthetic bipolar keys (mirrors c1 + a8 precedent; isolates the SEQUENCE-BINDING mechanism from KG-encoding)
- Substrate-only-decode gate asserted
- Codebook-NN cleanup for recall (same as c1)

**Primary metric:** `sequence_recall(depth)` — given k_t-1, does codebook-NN(S @ k_t-1) == k_t?

**Secondary metrics:**
- `chain_recall(depth)` — given k_0, can we trace the chain to depth d via iterative S @?
- W matrix retention check (W should be unchanged by sleep pass, only S written; assert)
- Substrate-only-decode gate (zero LLM calls; counter assertion)

### PRE-REGISTERED HARD THRESHOLDS

**HARD-PASS (chain-grade, mechanism validated):**
- Arm B (COMPRESSED_REPLAY) sequence_recall ≥ 0.80 at depth 5
- Arm A (NONE) sequence_recall ≤ 0.20 at depth 5
- Delta ≥ 0.50 at depth 5
- Arm B chain_recall ≥ 0.50 at depth 5 (iterative tracing degrades but stays useful)
- Arm C (UNORDERED_REPLAY) < Arm B by ≥ 0.30 (order matters → mechanism is sequence-binding, not generic pair-density)
- cv ≤ 0.05 across 3 seeds
- zero_llm_calls_at_inference == True
- W matrix unchanged by sleep pass (assertion)
- Version markers: `sleep_compression_ratio`, `sleep_pass_count`, `sequence_matrix_norm`, `arm`

**HARD-PASS-PLUS (super-pass):**
- Arm B chain_recall ≥ 0.50 at depth 10 (deep chains traceable)
- AND Arm D (ONLINE_NO_GAP) ≈ Arm B within 0.10 — confirms the magic is the PAIR-WRITE primitive (which is the load-bearing substrate-novelty); the biological "compression" is the LICENSE in biology, software just does it. This is an HONEST scope statement, not a HARD-FAIL.

**MIDDLE_BAND (proven bound, partial mechanism):**
- Arm B sequence_recall ∈ [0.50, 0.80] at depth 5 with delta ≥ 0.30 (real but smaller than predicted)

**HARD-FAIL:**
- Delta (B - A) < 0.20 at depth 5 → pair-write does NOT enable sequence recall on this substrate → re-route to S-matrix architecture probe (different binding rule?)
- OR Arm C ≥ Arm B (order doesn't matter — mechanism is just pair-density, not sequence-binding; honest finding)
- OR substrate-only-decode gate violated
- OR W modified by sleep pass

**Discriminating-regime requirement (C5):** the CAN-fail regime is shallow depth (depth=1 — trivial; both arms should be ≥ 0.95; replay buys nothing because the pair-write is the same as the test). Depth 5+ is where the chain-binding-mechanism is decisive. Depth 10 is the stretch goal.

### Compute cost

- 10 sequences × 20 facts = 200 outer-product writes per run = trivial wall.
- Sleep-pass: 200 ordered-pair writes per sequence = same scale.
- 4 arms × 5 depths × 3 seeds = 60 sub-units; each ~5s. Total ~5 min remote_cpu.
- **MUCH cheaper than c1** because we're testing a PRIMITIVE on synthetic data, not a full continual-learning loop.

### Secondary cell (CONDITIONAL on c1 LANDING): `c4_prioritized_replay_v1`

Defer spec until c1 lands and we see where the substrate actually breaks (raw cosine? α > 1.0?). The prioritized-replay mechanism is well-established (Mattar/Daw + Liu/Schrittwieser); the substrate-applicability is high; the question is just WHICH metric exposes the win.

### Tertiary cell: `c5_sleep_gated_cortex_v1`

Lower-confidence; ship after c3 + c4 land if compute allows.

---

## FALSIFIABLE PREDICTIONS

### Prediction 1 (PRIMARY) — Compressed-replay enables sequence binding the substrate cannot do online
**Hypothesis:** writing ordered pair (k_{t-1}, k_t) outer-products into a sequence matrix S during an offline "sleep" pass yields sequence_recall ≥ 0.80 at depth 5, while pure point-writes (no sleep pass) yield ≤ 0.20.
**Mechanism:** standard Hebbian outer-product writes a hetero-associative pair into S; without the offline pass, no such write occurs (the substrate has no online sequence-binding primitive).
**HARD-PASS:** Arm B sequence_recall ≥ 0.80 at depth 5; Arm A ≤ 0.20; delta ≥ 0.50.
**HARD-FAIL:** delta < 0.20 → the substrate's superposition arithmetic does NOT support sequence-binding via simple pair outer-products → route to richer binding rule (HRR convolution, FHRR, etc.).
**Calibrated P(HARD-PASS): 0.55** (deflated only slightly because the mechanism is a direct extension of c1's verified Hebbian writes; the math is the same outer-product the substrate already does — the only new claim is that ORDERED pairs preserve order through codebook-NN cleanup. NOT novel-synthesis-capped because it's just a different application of validated substrate primitives.)

### Prediction 2 (SECONDARY) — Order matters: UNORDERED_REPLAY fails the discriminator
**Hypothesis:** Arm C (random pairs into S) yields sequence_recall ≤ 0.30 at depth 5 — substantially below Arm B.
**Mechanism:** the sequence matrix S binds adjacent pairs specifically; random pairs flood S with noise and break the directional read.
**HARD-PASS:** Arm C < Arm B by ≥ 0.30.
**HARD-FAIL:** Arm C ≥ Arm B → mechanism is just generic pair-density, not sequence-binding → reframe as MEASURED_MECHANISM "Hebbian pair-density buys sequence recall, but order itself contributes < δ" — interesting but not the SWR claim.
**Calibrated P: 0.70** (order-discrimination in outer-product Hebbian is well-established Hopfield-textbook).

### Prediction 3 (HONEST SCOPE) — Software has no biological-Hebbian-window, so ONLINE_NO_GAP ≈ COMPRESSED_REPLAY
**Hypothesis:** Arm D (write ordered pairs into S ONLINE at ingest, no sleep pass) yields similar sequence_recall to Arm B.
**Mechanism:** in biology, online would NOT work because the events are 2s apart and the Hebbian window is 200ms. In software, we don't have that constraint — outer-product writes work regardless of inter-event delay. **The cell's job is to acknowledge this honestly: the biological "sleep replay must compress to enable learning" doesn't transfer to software directly; what transfers is the ARCHITECTURE (separate sequence matrix, ordered-pair writes), not the timing license.**
**HARD-PASS-PLUS condition:** Arm D ≈ Arm B within 0.10.
**HARD-FAIL would be:** Arm D < Arm B by ≥ 0.30 — which would mean the offline-replay schedule has its own software-substrate benefit beyond just the pair-write (e.g. avoiding interference with ingest-phase W writes). That would be an interesting positive finding but unexpected.
**Calibrated P (Arm D ≈ Arm B): 0.70** (software pair-write should work either online or offline).

### Prediction 4 (cross-thread) — Compressed-replay sequence binding closes part of the substrate-LM bigram gap (drill #1)
**Hypothesis:** when c3 is run with REAL TOKEN sequences from a small corpus (not synthetic bipolars), the sequence matrix S provides a P(w_t | w_{t-1}) signal that the substrate W did not have — closing ≥ 0.5 bits of the within-concept bigram gap (drill #1's 1.12-bit gap).
**HARD-PASS:** real-token c3 run shows bigram-conditional BPC ≤ baseline_BPC - 0.5 bits.
**HARD-FAIL:** real-token c3 shows ≤ 0.1 bit gain.
**Calibrated P: 0.30** (deflated heavily because: bridge from synthetic-bipolar c3 to real-token decode is unverified; the bigram gap may not be addressable by raw sequence-binding alone — may require the within-concept kWTA-VQ from drill #1 too).

### Prediction 5 (REVIVAL ROUTE if HARD-FAIL) — different binding rule needed
If pair outer-products into S don't bind sequences, the substrate may need HRR-style convolutional binding (Plate 1995) or FHRR (Plate 2003 / Frady-Sommer 2018). Route to research drill on alternative binding primitives.

### Prediction 6 (HONEST NEGATIVE if Arm A ≥ 0.30) — substrate codebook-NN may already do sequence inference via point-writes
If Arm A sequence_recall is unexpectedly NON-ZERO (e.g. ≥ 0.30 at depth 5), it would mean the substrate's W has some sequence structure via INDIRECT routes (k_{t-1} → v_{t-1} = some_value; v_{t-1} happens to be near k_t in code-space; codebook-NN catches it). This would be a SURPRISE measured-mechanism honest-positive — substrate-favorable, but means our discriminator is weakly distinguishing. Mitigation: separate value-space from key-space orthogonally (already in c1 / a8 design).

---

## CROSS-THREAD SYNTHESIS (compose with brain-drills #1-4 + c1 + r1 + U1 + N1)

### Composes with brain-drill #1 (within-concept floor / k-WTA-VQ + bigram gap)
- Drill #1 identified a 1.12-bit bigram gap that the substrate's W cannot bridge because W is concept-conditional, not sequence-conditional.
- Drill #5's S matrix IS the missing sequence-conditional structure. **The two compose directly: kWTA-VQ at write (drill #1) + ordered-pair S-writes at sleep (drill #5) → expected joint substrate-LM bigram-floor closure.**
- Cell sequencing: c3 (synthetic-key validation of S) → c4_extended (real-token validation of S on n2/n3 corpus) → integrated kWTA + S substrate-LM ablation.

### Composes with brain-drill #2 (CLS + 1:1 Hebbian replay = parent drill)
- Drill #2's c1 tests **WHETHER replay rescues forgetting in the substrate's W cortex**. Drill #5 says: replay does MORE than rescue — it BUILDS sequence structure that didn't exist before.
- c1's ONLINE_1to1 + drill #5's S-replay are ORTHOGONAL primitives. c1 re-reinforces (k, v) in W; c3 builds (k_{t-1}, k_t) in S. **Composition: c1's loop + c3's S-loop = full CLS + sequence-replay → covers both forgetting AND sequence-binding.**
- The c1 PARTIAL finding (substrate doesn't visibly forget at α=0.5 under codebook-NN) is RECONCILED by drill #5: the c1 NN-cleanup is more robust than expected because the FACT-recall task is one-shot; the SEQUENCE-recall task (drill #5) is genuinely harder and will discriminate. **Drill #5 may be the cell where the substrate's real limits show up.**

### Composes with brain-drill #3 (multi-hop working memory)
- Drill #3 addresses multi-hop reasoning. Drill #5's S matrix is the SUBSTRATE for multi-hop chains: k_0 → S @ k_0 = k_1 → S @ k_1 = k_2... composes adjacent edges into chains.
- Liu et al. (2019, Cell) directly demonstrated humans do this via sleep-replay (MEG). **Drill #5 + drill #3 jointly = the substrate's path to compositional inference at scale via sleep-replay-built chains, NOT via online graph-walk.**

### Composes with brain-drill #4 (generation / language production from substrate)
- The substrate currently has no autoregressive generation primitive — it's a one-shot recall machine.
- Drill #4 would address generation; drill #5's S matrix is the natural autoregressive engine: S @ current → next-token candidate via codebook-NN; iterate.
- **Drill #5 may be a load-bearing prerequisite for drill #4's substrate-generation capability.**

### Composes with U1 KG ingest-eval (CERT 584)
- U1 (multi-value KG, set-recall 0.99 @ 50k) provides the temporal-ordered key store from which the sleep pass samples. The architectural fit is tight: U1 IS the hippocampus producing replay sequences.
- The new piece is S (sequence matrix); U1 + W exist; S is novel.

### Composes with Hebbian-superposition capacity battery (CERT 591, ~327 cap)
- The 327-capacity finding is for INDEPENDENT random keys. Sequence-binding REUSES keys across many sequence positions — capacity-bound prediction depends on whether keys are reused (lower capacity) or each sequence uses disjoint keys (full capacity).
- c3 in synthetic-key mode uses disjoint keys per sequence — clean test. Real-token c3 (later) would test reuse.

### Composes with substrate-LM N-cells
- N3 + N5 + n8 are LM-decode capacity cells; they measure point-recall, not sequence-recall.
- c3's S matrix is the SEQUENCE primitive that substrate-LM needs. If c3 lands, substrate-LM ablation: with-S vs without-S BPC. **This is the missing link from one-shot recall to autoregressive generation.**

### Composes with refuse-gate (U1 0.97 OOD refuse)
- Sequences whose intermediate steps are OOD should be REFUSED by the sequence-recall path. The refuse-gate composes with S: if codebook-NN(S @ k_{t-1}) returns a low-confidence candidate (no nearby codeword), refuse.
- This is the substrate-native solution to LLM hallucination on autoregressive decode: PRINCIPLED REFUSAL on out-of-substrate-distribution sequence steps.

---

## L5 — CROSS-SUBSTRATE COMPOSITION (the path-forward map)

```
                       SUBSTRATE HAS NO SEQUENCE-BINDING PRIMITIVE TODAY
                                            │
              ┌─────────────────────────────┼─────────────────────────────┐
              ▼                             ▼                             ▼
         c3 compressed-replay          c4 prioritized-replay         c5 sleep-gated W
         (PRIMARY; novel)              (drop-in to c1 sampler)       (tertiary)
         P(HARD-PASS)=0.55             P(HARD-PASS)=0.45             P(HARD-PASS)=0.30
              │
       ┌──────┼──────┐
       ▼      ▼      ▼
   depth=1  depth=5  depth=10
   (null    (decisive (stretch)
   bracket) bar)
              │
              ▼  (if HARD-PASS at depth 5)
       ┌──────────────────┴──────────────────┐
       ▼                                     ▼
c3 + drill #1 kWTA                      c3 + c1 ONLINE_1to1
(sparse expansion writes)               (sequence-binding + forgetting-rescue)
       │                                     │
       └─────────────────┬───────────────────┘
                         ▼
       FULL substrate sequence-LM stack
       (U1 hippocampus + W cortex + S sequence + kWTA + 1:1 replay)
       predicted: autoregressive substrate-decode at usable BPC
                         │
                         ▼ (if works)
       Substrate-LM glass-box autoregressive generation
       (drill #4 territory; drill #5 was the missing primitive)
                         │
                         ▼
       Multi-hop substrate inference (drill #3) via iterative S @
       Substrate continual-learning (drill #2 c1) preserves both W and S
       Refuse-gate principled (no hallucinated sequence steps)
       ⇒ substrate-native autoregressive LM with continual learning
```

**If c3 HARD-FAIL:**
```
c3 HARD-FAIL (pair outer-products into S don't bind sequences in substrate's superposition arithmetic)
    │
    ├─→ ROUTE TO RESEARCH (USER STANDING — symmetric revival for negatives)
    │   revival angle: alternative binding primitives (HRR convolution, FHRR, VSA-other)
    │
    └─→ if all simple binding rules fail → the substrate may need an EXPLICIT graph index (not Hebbian)
        → reframe substrate's sequence/graph as a separate index, not a matrix
```

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **The substrate's missing primitive is SEQUENCE-BINDING, not capacity.** c1 partial-data showed point-recall is already over-capacity at α=0.5 under codebook-NN. The gap is not "more storage" — it's "structured storage that links events in time/order." Drill #5's S matrix is the candidate primitive.

2. **Substrate-LM autoregressive decode requires sequence-binding (drill #5) + within-concept sparsity (drill #1).** Neither alone closes the bigram gap. The composition is the path.

3. **Sleep-as-architecture is a substrate-product story.** "The substrate has a brain-like sleep phase: during sleep, it walks the episodic store and binds sequences. The result is a learned-graph the substrate uses for generation and multi-hop inference. No backprop. No external tokenizer." This is substrate-distinctive and biologically tight.

4. **The brain's 4 SWR mechanisms map to 4 substrate cells.** c1 (1:1 cortex reinforcement — done, partial), c3 (compressed sequence binding — NOVEL), c4 (prioritized sampling — drop-in), c5 (sleep-gated η_W — speculative). The cert-architecture is naturally hierarchical: c3 is the load-bearing addition; c4 + c5 are efficiency layers.

5. **Refuse-gate composes naturally.** Sequence steps with no nearby codeword are refused — substrate's native solution to autoregressive hallucination.

6. **Multi-hop inference (drill #3) becomes substrate-native** via iterative S @ — no external graph index needed.

7. **The capacity bound on S is independent of the capacity bound on W.** S can hold its own Hebbian-superposition load (~ 0.14 × N_DIM = ~570 distinct ordered pairs at N_DIM=4096 per classical Hopfield, or much more under codebook-NN per CERT 591 / 592). For substrate-LM at scale, S would need a separate capacity audit — analog of an a8 cell for the sequence matrix.

8. **HONEST CAVEAT.** The biological MOTIVATION for sleep-compression (Hebbian window 200ms) doesn't transfer to software. What transfers is the ARCHITECTURE: separate sequence matrix, ordered-pair Hebbian writes, offline-scheduled consolidation, prioritized sampling. The cell pre-reg's Arm D control acknowledges this explicitly. Don't oversell the "biology says we need sleep" framing in product — the substrate's win is the ARCHITECTURE, regardless of when we do the pair-writes.

---

## CITATIONS (verified, count = 16)

1. Buzsáki, G. (2015). "Hippocampal sharp wave-ripple: A cognitive biomarker for episodic memory and planning." Hippocampus 25(10): 1073-1188. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4648295/) [PDF](http://buzsakilab.com/content/PDFs/Buzsaki2015Hippo.pdf) (Canonical SWR review; rates, mechanism, function.)

2. Wilson, M.A., McNaughton, B.L. (1994). "Reactivation of hippocampal ensemble memories during sleep." Science 265(5172): 676-679. (Canonical sleep-replay; ~20x compression.)

3. Lee, A.K., Wilson, M.A. (2002). "Memory of sequential experience in the hippocampus during slow wave sleep." Neuron 36(6): 1183-1194. (Quantitative sequence replay; statistical validation of compression.)

4. Pfeiffer, B.E., Foster, D.J. (2013). "Hippocampal place-cell sequences depict future paths to remembered goals." Nature 497: 74-79. (Forward awake replay as planning.)

5. Foster, D.J. (2017). "Replay comes of age." Annual Review of Neuroscience 40: 581-602. (Forward/reverse + awake/sleep functional dissociation.)

6. Foster, D.J., Wilson, M.A. (2006). "Reverse replay of behavioural sequences in hippocampal place cells during the awake state." Nature 440: 680-683. (Reverse replay + reward credit-assignment.)

7. Mehta, M.R. (2007). "Cortico-hippocampal interaction during up-down states and memory consolidation." Nature Neuroscience 10(1): 13-15. (Compression brings distant events into Hebbian window — the capacity-relevant argument.)

8. Mattar, M.G., Daw, N.D. (2018). "Prioritized memory access explains planning and hippocampal replay." Nature Neuroscience 21: 1609-1617. (Mathematical theory: priority = NEED × GAIN; predicts SWR content patterns.)

9. Liu, Y., Dolan, R.J., Kurth-Nelson, Z., Behrens, T.E.J. (2019). "Human Replay Spontaneously Reorganizes Experience." Cell 178(3): 640-652. (MEG; sleep-replay reorders pairs into inferred chains; multi-hop substrate.)

10. Joo, H.R., Frank, L.M. (2018). "The hippocampal sharp wave-ripple in memory retrieval for immediate use and consolidation." Nature Reviews Neuroscience 19: 744-757. (SWR as dual-mode primitive: planning + consolidation.)

11. Michon, F., et al. (2025). "Selection of experience for memory by hippocampal sharp wave ripples." [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10659301/) (SWR content prioritization; novelty + reward bias; 2-stage tag-then-consolidate.)

12. Klinzing, J.G., Niethard, N., Born, J. (2019). "Mechanisms of systems memory consolidation during sleep." Nature Neuroscience 22: 1598-1610. [Nature](https://www.nature.com/articles/s41593-019-0467-3) (SO-spindle-SWR triple-coupling; quantitative timing.)

13. Helfrich, R.F., et al. (2018). "Old brains come uncoupled in sleep: slow wave-spindle synchrony, brain atrophy, and forgetting." Neuron 97(1): 221-230. (Phase-coupling is causally linked to memory consolidation.)

14. Lisman, J.E., Jensen, O. (2013). "The theta-gamma neural code." Neuron 77(6): 1002-1016. (Theta-gamma coupling; encoding/retrieval phase separation.)

15. Ecker, A., et al. (2022). "Hippocampal sharp wave-ripples and the associated sequence replay emerge from structured synaptic interactions in a network model of area CA3." eLife 11:e71850. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8865846/) (Mechanistic model; recurrent CA3 inhibition + sparse excitation self-organize SWRs.)

16. Norman, Y., et al. (2019). "Hippocampal sharp-wave ripples linked to visual episodic recollection in humans." Science 365(6454): eaax1030. (Cross-species validation: humans show SWRs at recall.)

---

## LIT-SCAN CALIBRATION NOTES

- All probability estimates deflated 0.15-0.25 from raw LM confidence.
- **Novel-synthesis cap at 0.50 NOT APPLIED to c3 primary prediction** because c3 is a DIRECT EXTENSION of the substrate's existing outer-product Hebbian write — only the THING being written (k_{t-1} ⊗ k_t instead of k ⊗ v) is new. The arithmetic is verified. P=0.55 reflects this. The NOVEL-SYNTHESIS cap (0.50) is RESERVED for the cross-thread integration predictions (P4 closes substrate-LM gap) where the bridge from synthetic-keys to real-LM is unverified — that one gets P=0.30 (deflated + capped).
- HARD-FAIL thresholds mandatory and listed for every prediction.
- The directional claim (compressed-replay binds sequences) is HIGHLY confident (raw P ≈ 0.80 — direct extension of Hopfield hetero-associative storage which is textbook). The MAGNITUDE (≥ 0.80 at depth 5) depends on capacity-vs-load tradeoff for the synthetic-key disjoint-sequence setup; expected within range.
- The substrate's superposition arithmetic for hetero-associative pairs is VALIDATED via CERT 591 (learned-projection KV) and CERT 592 (NESS write-decay chain-recall depth > Hopfield ceiling 2-12x) — both directly support compressed-pair Hebbian binding working on the substrate.
- The biological CONTENT of the four streams (Buzsáki / Pfeiffer-Foster / Klinzing / Mattar-Daw / Michon / Liu) is robust and well-cited across 30 years of neuroscience.
- The honest skeptic angle: the cell may need 4 arms exactly as specified (A/B/C/D) to discriminate the substrate-specific finding (does compression matter in software?) from the architectural finding (does pair-write matter?). The pre-reg includes both as separate predictions.

---

## DISPATCH RECOMMENDATION

**Immediate (Exp-Dev, after c1 lands AND drill #1 kWTA cell sequenced):** `c3_compressed_sequence_replay_v1`
- Synthetic-key sequence-binding cell; 4 arms × 5 depths × 3 seeds; ~5 min remote_cpu.
- Reuses c1 + a8 + r1 harness scaffold (codebook-NN, bipolar keys, substrate-only-decode gate).
- Pre-reg per Section L4; bands explicit; HARD-FAIL routes specified.
- Version markers: `sleep_compression_ratio`, `sleep_pass_count`, `sequence_matrix_norm`, `arm`, `sequence_depth`, `n_sequences`, `disjoint_keys`.

**Conditional Phase 2 (if c3 HARD-PASS):**
1. `c3_real_tokens_v1` — bridge synthetic to real-corpus; test bigram-gap closure (prediction 4).
2. `c4_prioritized_replay_v1` — drop-in upgrade to c1's sampler with NOVELTY/RPE/REFUSE priorities.
3. `c5_sleep_gated_cortex_v1` — η_W gating speculative cell.

**Ordering vs other brain-drill cells:**
- **c3 is INDEPENDENT of c1** — different substrate primitive (S matrix, not W). Can run in parallel with c1 or after.
- **c3 + drill #1 kWTA cell are COMPLEMENTARY** — kWTA affects write-side sparsity; c3 affects sequence-binding. Ship in either order.
- **c3 may be the load-bearing prerequisite for drill #3 multi-hop and drill #4 generation** — sequence-binding is the substrate primitive both need.

**Honest scope statement (mandatory in cell docstring):**
- The cell tests sequence-binding via ordered-pair outer-products on synthetic bipolar keys. The result generalizes to "Hebbian-superposition substrate with disjoint-key sequences."
- DOES NOT yet generalize to real-token LM decode (Phase 2 c3_real_tokens), reused-key sequences (capacity bound on S unknown), or compositional inference chains (drill #3 follow-on).
- The biological MOTIVATION for compression (Hebbian window) is NOT directly testable in software; the architectural transfer is what we're measuring.

---

## PLAIN-ENGLISH WRAP (Fix #13, whole-response)

Brain-drill #2 (CLS replay) tested whether 1:1 Hebbian replay rescues the substrate from catastrophic forgetting. The c1 cell (in flight) showed the substrate's codebook-NN cleanup is so robust that the baseline doesn't even forget at the pre-registered cliff — so replay-rescue can't fire. **Drill #5 reframes from rescue to ROLE: what does sleep replay actually DO in the brain beyond reinforcement?** Four mechanisms in the literature, drilled in 4 streams: (1) compressed-time replay so Hebbian plasticity can link events that were too far apart in waking time; (2) prioritized sampling biased by novelty + reward + surprise (= the ML-empirical PER discovery, found earlier in neuroscience); (3) sleep-stage-gated cortex plasticity (cortex is plastic in DISCRETE windows, not continuously); (4) cortex-spindle-ripple triple-coupling (memories consolidate only when cortex is in UP-state). The substrate today has NONE of these — its W is always-plastic, ingest writes everything to the same matrix, and it has NO temporal-pair primitive. **The substrate's missing piece is SEQUENCE-BINDING, not capacity.** Compressed-replay buys the brain the ability to link events seconds apart in time; the SUBSTRATE analogue is an offline pass over U1 that Hebbian-writes (k_{t-1}, k_t) ordered pairs into a separate sequence matrix S. The substrate already has all the primitives (U1 hippocampus, W cortex, outer-product Hebbian writes); the missing piece is S. Cell `c3_compressed_sequence_replay_v1` tests this in ~5 minutes remote_cpu with hard pre-registered bands and 4 discriminator arms (NONE / COMPRESSED_REPLAY / UNORDERED_REPLAY / ONLINE_NO_GAP). If it lands (P=0.55), the substrate has a working sequence-binding primitive — the missing piece for autoregressive substrate-LM generation, multi-hop substrate inference (drill #3), and the bigram-gap closure from drill #1. **The honest scope: the biological "compression" justification doesn't transfer to software (we have no Hebbian window). What transfers is the architecture — separate sequence matrix, ordered-pair writes, offline scheduling. The Arm D control acknowledges this explicitly.** Compose with: drill #2 c1 (orthogonal — W vs S); drill #1 kWTA (complementary — sparsity at write); drill #3 multi-hop (S enables iterative chain composition); drill #4 generation (S is the autoregressive engine). Substrate-product story: "the substrate has a brain-like sleep phase that builds sequence structure offline; no backprop, no tokenizer, principled refusal on out-of-distribution sequence steps via the existing refuse-gate." This is substrate-distinctive AND biologically tight AND testable in ~5 min compute.

---

-- Research (Opus synthesis, lit-scan via 6 parallel WebSearch queries spanning Buzsáki SWR machinery + Pfeiffer-Foster awake-vs-sleep + theta-gamma coupling + cortex-spindle-ripple coordination + prioritized replay + compression-capacity theoretical, deflated per calibration). Companion to drill #2 (CLS replay). Drill #5 IDENTIFIES the substrate's missing primitive (sequence-binding via offline-pair-replay) that drill #2's c1 partial data exposed indirectly by NOT showing forgetting at the cliff. The four SWR sub-mechanisms (compression / prioritization / sleep-gating / cortex-coupling) map to four candidate cells (c3 / c4 / c5 / deferred); c3 is load-bearing and ships first.
