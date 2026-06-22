# RESEARCH 5x DEEPER DRILL: Continual Learning at scale — Complementary Learning Systems (CLS) for substrate

**Date:** 2026-06-22
**Requestor:** Skunkworks (USER STANDING — biology/brain/nature drill #2 for substrate gaps)
**Empirical anchor on substrate:** `exp_a8_continual_writes_no_catastrophic_forgetting_v1` HARD_PASS — perfect recall (acc=1.000, std=0.000) up to α=N/N_DIM=0.3; cliff at α=0.5 (acc=0.527); collapse at α=1.5 (acc=0.10). **The substrate has a Hebbian-superposition CAPACITY BOUND, but has NOT been tested in a CLS-graded sequential-task framework (no replay, no consolidation, no task-incremental retention curve).**
**Companion drill:** brain-drill #1 (within-concept floor; k-WTA-VQ at biological sparsity); same 5-level structure.
**Lit-scan calibration:** deflate P 0.15-0.25; cap novel-synthesis P at 0.50; HARD-FAIL thresholds mandatory.

---

## HEADLINE — intuitive first (Fix #13)

**The substrate's "27x no-forget" claim is real but UNDER-MEASURED.** It is a capacity-saturation bound on RANDOM independent keys at one ingest pass — NOT continual learning. Continual learning means: train on Task A; then train on Task B; **does A survive?** The substrate has never been tested this way at scale. Biology solved this with a TWO-MEMORY architecture (Complementary Learning Systems): a fast, sparse hippocampus that captures new experiences NOW, plus a slow, distributed cortex that absorbs them via INTERLEAVED REPLAY at a 1:1 ratio. The math (McClelland 1995 + Cheng 2026 Context Channel Capacity) is settled: zero-forgetting is provably IMPOSSIBLE for a single-store online-learner with fixed parameters; you need EITHER (a) a separate retrieval store, OR (b) a replay/regeneration loop, OR (c) per-weight consolidation thresholds (SNAP).

**The substrate ALREADY has all three primitives latent**: (a) the multi-value KG store U1 chain-grade ratified (CERT 584) — that IS a hippocampal-style episodic store at 50k scale, set-recall 0.99, refuse-gate 0.97; (b) the Hebbian-superposition W matrix IS a cortex-style slow-store (a8 saturation curve); (c) the substrate has no consolidation rule yet — that's the gap. **Novel synthesis:** wire U1's episodic store as the hippocampus, the W matrix as the cortex, and add a **Hebbian-only generative replay loop** that samples old keys from W (or U1) and re-writes them interleaved with new tasks. **The biology says optimal interleaving ratio = 1:1, optimal hippocampus-to-cortex transfer rate is GRADUAL (slow-cortex learning rate ~10x slower than hippocampus), and the SNAP sigmoidal-weight rule provides total Hebbian forgetting protection at the per-weight level.** All three are forward-only, no backprop, compatible with substrate primitives.

**The cheap decisive test:** sequential ingest of 10 disjoint task-batches (M=5k each) into U1+W, with vs. without 1:1 replay sampled from U1; HARD-PASS bar = task-A recall after task-J ingest ≥ 0.85 with replay vs. ≤ 0.40 without replay (the catastrophic-forgetting baseline) at total load α=0.5 (cliff regime).

| Mechanism | Source | Substrate-applicability | Substrate-cost | Expected gain | P(HARD-PASS) |
|-----------|--------|--------------------------|----------------|---------------|--------------|
| **CLS dual-store + 1:1 generative replay (novel synthesis)** | McClelland 1995, O'Reilly 2014, Kumaran/Hassabis/McClelland 2016, Gonzalez 2020 unsupervised-Hebbian-replay | **HIGHEST** — wires U1 (hippocampus) + W (cortex) + Hebbian-only replay, all already in substrate | ~2x ingest wall (replay pass) | task-A retention 0.40 → 0.85+ at α=0.5 | **0.45** (cap @ novel-synthesis) |
| **SNAP sigmoidal-weight consolidation (per-weight forget-protection)** | Tang et al. 2024 (arxiv 2410.15318); biological LTP consolidation | HIGH — Hebbian-only sigmoidal update; compatible with substrate W; minor primitive change | ~1.05x wall (one nonlinearity in update) | total forgetting protection on top of 0.3 cliff | 0.40 |
| **Hippocampal pattern-separation DG-style sparse coding (separator BEFORE write)** | Rolls 2013, Cayco-Gajic/Silver 2019, Yassa/Stark 2011 | MEDIUM — compatible with k-WTA-VQ from drill #1; same sparsity prior | ~1.10x wall (sparsifier) | crosstalk reduction; lifts α-cliff from 0.3 to ~0.5+ | 0.35 |
| **Context Channel Capacity-bound architecture audit** | Cheng 2026 (arxiv 2603.07415) | DIAGNOSTIC — proves which substrate config CAN-vs-CANNOT achieve zero-forget | nil | architectural clarity, not gain | 0.80 (mechanically applies) |
| **Sleep-stage temporal-compression replay (20x speed)** | Wilson & McNaughton 1994; Diekelmann/Born 2010; Klinzing 2019 | MEDIUM-LOW — wall-time optimization not a capacity-gain | small | speed only | DEFER |
| **Predictive-coding consolidation (cortex top-down)** | Friston, Bastos, Rao-Ballard | REJECTED — backprop-adjacent | n/a | n/a | rejected |

**Cheap decisive test:** `c1_cls_replay_continual_ingest_v1` — sequential 10×5k task-batches into U1+W ± 1:1 Hebbian generative replay, measure task-recall curve across J=1..10 at α∈{0.1, 0.3, 0.5, 0.75}. **HARD-PASS bar: at α=0.5 cliff, task-A recall after J=10 ≥ 0.85 WITH replay AND ≤ 0.40 WITHOUT replay AND replay-vs-no-replay delta ≥ 0.40 (controls the by-construction case). HARD-FAIL: replay delta < 0.10 at any α.**

---

## L1 — LITERATURE BROAD SCAN (4 parallel streams)

### Stream A: CLS foundational theory + 2024-2026 ML re-validation

- **McClelland, McNaughton & O'Reilly (1995):** the foundational paper. Catastrophic interference in connectionist models — when one network learns sequentially, posterior tasks overwrite prior tasks. The biological solution: TWO learning systems. The **HIPPOCAMPUS** is sparse, fast-learning, pattern-separated, episodic. The **NEOCORTEX** is distributed, slow-learning, semantic. The hippocampus captures new experiences IMMEDIATELY and replays them to cortex INTERLEAVED with old experiences, allowing the cortex to gradually integrate without overwriting. Key formal claim: **the cortical learning rate must be slow ENOUGH that no single experience can overwrite a stable representation; the hippocampus learning rate is fast and per-trial.** The two rates differ by ~10x in the McClelland model.

- **O'Reilly (2014):** modern re-statement. The hippocampus does pattern separation via DG sparse coding + pattern completion via CA3 attractor dynamics. The CLS factorization is supported by: post-hippocampal-lesion patients lose recent memories but not older ones (retrograde-amnesia gradient consistent with consolidation); sleep replay coupled with sharp-wave-ripples; cortical learning rates measured to be very slow in single-cell electrophysiology.

- **Kumaran, Hassabis & McClelland (2016, TICS):** explicitly re-frame for AI. **"What learning systems do intelligent agents need?"** Answer: TWO — a fast individual-experience store + a slow integrator. Argue this is exactly the same logical answer for AI as for biology. Direct citation source for substrate design rationale.

- **2024-2026 ML papers:** generative-replay re-implements CLS in deep nets (Shin 2017; van de Ven 2020 brain-inspired replay; arxiv 2507.11393 VAE+MHN for split-MNIST achieving 89.71% vs 67.75% no-replay baseline at 1:1 replay ratio). Common finding: 1:1 replay ratio is best; latent-space replay is more efficient than raw-data replay; the "hippocampal" store can be small (~5% of training set).

### Stream B: Sleep replay + biological consolidation rates

- **Wilson & McNaughton (1994):** the canonical paper. During post-task slow-wave sleep, hippocampal place-cell ensembles replay the spatial sequences from the awake task, **at ~20x temporal compression** (~100ms compressed sequences for ~2s awake sequences). The 30% of CA1 cells active during awake task fire in REPLAY during ripples.

- **Diekelmann & Born (2010, Nature Rev Neurosci); Klinzing, Niethard & Born (2019, Nat Neurosci):** quantitative model of systems consolidation. Replay occurs predominantly during slow-wave sleep (SWS) and quiet wakefulness. Sharp-wave-ripples (SWRs) at ~150-200Hz, lasting ~50-100ms; **rate ~5-10 SWRs/sec during SWS bouts**; a typical 8hr sleep contains ~10k-30k replay events. **Compression factor**: ~20x. **Replay-to-new-experience ratio**: ~1:1 to 3:1 on the timescale of hours-days (i.e., the brain replays each waking experience 1-3 times during the following sleep).

- **Rasch & Born (2013):** "About sleep's role in memory." Synthesis of synaptic-vs-systems consolidation distinction. Synaptic consolidation = local synaptic modifications, minutes-hours timescale. Systems consolidation = transfer hippocampus→cortex, days-years. Sleep drives BOTH.

- **Gonzalez et al. (2020, eLife) + Tadros et al. (2022, Sleep-Replay-Consolidation):** sleep-like REPLAY implemented as pure unsupervised Hebbian updates (no backprop) recovers catastrophic-forgotten tasks in standard ANNs. Retention 19.49% (sequential baseline) → 48.47% on 5-task MNIST WITHOUT touching the loss function. This is direct evidence that **Hebbian-only sleep-style replay works**.

### Stream C: Hippocampal architecture — DG / CA3 / CA1 separator-completer-output

- **Rolls (2013, Frontiers Syst Neurosci); Cayco-Gajic & Silver (2019, Neuron):** DG implements **pattern separation** via sparse expansion coding. ~10^6 granule cells (much more than ~3×10^5 entorhinal inputs), each fires for ~1-5% of input patterns (very sparse: f≈0.01-0.05). Mossy fibers project to CA3 (~3×10^5 cells). The expansion + sparsification ENSURES that nearby inputs land on DISJOINT CA3 subsets — eliminating crosstalk at write.

- **CA3 pattern completion (Rolls):** recurrent collaterals act as autoassociative Hopfield network. Storage capacity (anatomical estimate) ≈ p_max ≈ 0.14 × C / (a × log(1/a)) where C ≈ 12k recurrent synapses per CA3 cell, a = sparsity ≈ 0.02-0.05 → **p_max ≈ 36-200 sparse patterns** (very small absolute; the brain stores them HIERARCHICALLY through systems consolidation, not statically).

- **Cheap quantitative claim:** the brain's hippocampus is NOT a high-capacity store; it's a HIGH-FIDELITY recent-experience cache. The bulk capacity lives in the cortex; the hippocampus's job is to BUFFER + REPLAY.

- **Yassa & Stark (2011, TINS); Bakker et al. (2008, Science):** behavioural fMRI evidence that DG/CA3 implements pattern separation in humans on mnemonic similarity tasks (DG signal scales with input dissimilarity).

### Stream D: ML continual-learning at scale + the impossibility result

- **Cheng (2026, arxiv 2603.07415) "Context Channel Capacity":** the field-redefining result. Defines **C_ctx = mutual information between architecture's context signal and generated parameters**. **Proves: zero-forgetting requires C_ctx ≥ H(T), the task identity entropy.** Establishes the **Impossibility Triangle**: zero-forgetting + online-learning + finite-parameters CANNOT be simultaneously satisfied by sequential state-based learners. The escape route: conditional REGENERATION architectures (HyperNetworks; CLS-style replay-based ones) that redefine parameters as function values rather than states. **Direct application to substrate:** substrate must have a context signal (= the U1 KG keys, or the task-id, or a learned context-key) that conditions the W update. Without that, the impossibility theorem says forgetting is INEVITABLE at α > 0.

- **Tang et al. (2024, arxiv 2410.15318) "SNAP":** Sigmoidal Neuronal Adaptive Plasticity. Per-weight nonlinearity making weight update PROPORTIONAL to (1 - tanh(|w|/θ)): plastic at intermediate strengths, consolidated at strong strengths. **Empirical claim: "total protection against forgetting of previous tasks" in HEBBIAN-trained networks** (does NOT work for SGD-trained networks — Hebbian-specific). This is the per-weight version of biological LTP consolidation. Directly compatible with substrate's Hebbian W update.

- **van de Ven et al. (2020, Nature Communications) "Brain-inspired replay":** generative-replay with VAE-decoders implementing the hippocampal generator. Achieves competitive sequential-task retention without per-task storage. Backprop-based, but the architecture is the substrate-applicable design.

- **Asynchronous Hebbian/anti-Hebbian (arxiv 2501.02402):** plasticity-threshold in weakly-tuned neurons prevents catastrophic forgetting AS LONG AS NETWORK CAPACITY IS SUFFICIENT. Quantitative claim: a 100-unit Hebbian network with weight thresholds + sparsity 0.1 stores ~60 patterns at its theoretical capacity (matches Hopfield C ≈ 0.14N for sparse codes).

- **Order parameters / phase transitions (arxiv 2407.10315):** continual learning has a phase-transition in task-overlap × capacity-load space. Below critical load, near-zero forgetting is achievable; above critical load, forgetting is inevitable. Relevant to substrate's α=0.3 cliff (this IS a phase transition).

---

## L2 — FILTER TO SUBSTRATE-APPLICABLE

| Mechanism | Forward-only / Hebbian-compatible? | Composes with V_C × N_DIM lever? | Composes with U1 / W / refuse-gate / k-WTA? | Verdict |
|-----------|---------------|----------------------------|-------------------------------|---------|
| **CLS dual-store + 1:1 Hebbian generative replay** | YES (Gonzalez/Tadros 2020 confirmed pure Hebbian works) | YES (U1 + W are independent stores; both scale with V_C and N_DIM) | YES (U1 hippocampus, W cortex, refuse-gate guards both, k-WTA from drill #1 enhances DG-style separation) | **ACCEPT — top candidate** |
| **SNAP sigmoidal-weight consolidation** | YES (per-weight nonlinearity in update rule) | YES (orthogonal to V_C × N_DIM; works on the W matrix) | YES (drop-in change to W update) | **ACCEPT — secondary, composable with CLS** |
| **DG-style pattern separation (sparsifier before write)** | YES (k-WTA from drill #1 already meets this) | YES | YES (drill #1 already proposed this) | **ACCEPT but DEDUPLICATE with drill #1** |
| **Context Channel Capacity audit** | YES (diagnostic, not mechanism) | n/a | YES (tells us which substrate config CAN-vs-CANNOT achieve zero-forget) | **ACCEPT as design tool** |
| **Sleep-stage temporal compression (replay speedup)** | YES | n/a | Compute-only optimization | **DEFER** |
| **Predictive coding consolidation (top-down gradient)** | NO (backprop) | n/a | n/a | **REJECT** |
| **VAE-decoder generative replay (van de Ven)** | NO (VAE = backprop) | partial | Could be replaced by W-sample-and-rewrite | REJECT in pure form; the PRINCIPLE (replay from latent generator) is what we adopt |

---

## L3 — DEEP DRILL ON TOP 1-2 MECHANISMS

### 3.1 CLS dual-store + Hebbian generative replay (PRIMARY)

**Architecture mapping (substrate ↔ biology):**

| Brain structure | Function | Substrate analogue (status) |
|----|----|----|
| Entorhinal cortex (input) | Sensory pre-processing | Pythia frozen encoder at ingest (CERT 591) |
| Dentate Gyrus (DG) | Sparse pattern separation | k-WTA-VQ at f≈0.05-0.10 (drill #1; pending) |
| CA3 | Episodic store with recurrent attractor | U1 multi-value KG (CERT 584, set-recall 0.99 @ 50k) |
| CA1 | Hippocampal output / replay generator | U1 read-side; sample old keys for replay |
| Cortex | Distributed slow store | Hebbian W matrix (a8 capacity bound α=0.3 cliff) |
| Sharp-wave-ripples | Replay events | A re-write pass: sample (k_old, v_old) from U1, re-Hebbian-bind into W |
| LTP consolidation | Per-weight stabilization | SNAP sigmoidal weight rule (pending; orthogonal) |
| Slow-vs-fast learning rates | Decoupled timescales | substrate has implicit timescales but no rate decoupling yet |

**Mathematical core (McClelland 1995, formalized):**

The cortex W weight update at time t is:
```
W_t = W_{t-1} + η_cortex · (k_new ⊗ v_new + Σ_replay (k_replay ⊗ v_replay))
```
where η_cortex is small (slow learning), and the sum runs over 1-3 sampled replays per new-experience. The hippocampus update:
```
U_t = U_{t-1} ∪ {(k_new, v_new)}
```
fast, all-or-nothing per-trial. Replay samples come from U: `(k_replay, v_replay) ~ Uniform(U_t)` (or task-weighted).

**Why this lifts the α=0.3 cliff:** at α=0.5 in the substrate today, recall drops to 0.527 because new writes interfere with old keys (Hebbian crosstalk grows ~√(N_items/N_DIM)). With 1:1 replay, each new write is paired with an old re-write — and the EFFECTIVE α stays at 0.5 in terms of slots used, but the OLD keys get RE-REINFORCED at each step, preventing decay. The crosstalk floor remains (so this isn't infinite capacity), but the FORGETTING term (the asymmetry that makes old keys decay faster than new) is eliminated. Expected gain: extends usable-capacity bound from α=0.3 to α≈0.5-0.7 (close to the random-coding capacity bound ~0.14 of Hopfield-style stores; substrate's superposition is more capacity-rich than classical Hopfield per CERT 592).

**Why pure Hebbian replay works (Gonzalez 2020 + Tadros 2022 cited evidence):** at sleep-replay phase, the network sees no labels and no gradients. It just re-presents (key, value) pairs to itself sampled from the episodic store. The Hebbian update on these pairs is mathematically equivalent to the original write — no information beyond what the substrate already has. **Substrate-only-decode gate trivially preserved** (the replay loop calls no LLM; it samples from U1 and writes into W using existing primitives).

**Optimal replay ratio (1:1 from biology + ML re-validation):**
- McClelland 1995: cortex weight changes should be small enough that 1 new experience doesn't dominate; biology effectively implements 1:1 to 3:1 replay-to-new ratio over sleep.
- van de Ven 2020 + arxiv 2507.11393: 1:1 latent-space replay ratio is optimal in modern ML benchmarks (split-MNIST, CIFAR).
- Substrate prior: a8 saturation curve shows that DOUBLING the writes (1:1 replay = 2x writes) does NOT collapse recall as long as effective α stays below cliff. So 1:1 replay is compatible with the a8 capacity bound provided we ingest 2x slower wall-time.

**Replay schedule options:**
- **Per-ingest replay (online)**: every new write is paired with k_replay sampled re-writes.
- **Batch replay (offline)**: ingest M new items, then replay K old items, alternating.
- Biology does both: online ripples during quiet wake + offline sleep replay. Substrate: choose per-ingest for simplicity; batch as a follow-on.

### 3.2 SNAP sigmoidal-weight consolidation (SECONDARY, ORTHOGONAL)

**Mechanism (Tang 2024, arxiv 2410.15318):** replace the linear Hebbian update `W += η · k ⊗ v` with a **plasticity-modulated update**:
```
W += η · σ(|W|/θ_consol) · (k ⊗ v)
where σ is sigmoidal: large near |W|=0 (plastic), zero near |W|>>θ (consolidated)
```
Reasoning: biological synapses at intermediate strength are highly plastic; once consolidated via LTP, they resist change. SNAP claims **total forgetting protection** in Hebbian nets but ONLY when applied with sufficient capacity.

**Substrate compatibility:** the substrate W matrix is bound-by-Hebbian-superposition (not gradient-trained). The sigmoidal rule is a per-weight modification of the update — substrate-native. Orthogonal to CLS replay (CLS prevents the WRITE-PHASE crosstalk; SNAP prevents the OVERWRITE of already-consolidated weights).

**Cost:** trivial (one element-wise nonlinearity in the W update).

**Risk:** SNAP locks consolidated weights; if a consolidated entry is WRONG, it CANNOT be corrected. Refuse-gate (U1's 0.97 OOD-refuse) becomes critical: only consolidate values that pass the refuse-gate. This composes naturally.

**Composition with CLS:** CLS provides replay that keeps old weights ALIVE; SNAP provides per-weight thresholds that prevent NEW writes from overwriting consolidated old weights. The two are stacked: replay-first (during ingest), SNAP gates the W update (every step). Predicted multiplicative effect.

---

## L4 — CELL-DESIGN IMPLICATIONS + PRE-REG

### Primary cell: `c1_cls_replay_continual_ingest_v1`

**Scope:** Sequential ingest of J=10 disjoint task-batches (M=5k facts each, drawn from FB15k-237 partitioned by relation-type to ensure task-independence) into U1+W; measure task-A recall after task-J ingest with vs. without 1:1 Hebbian generative replay.

**Independent variables:**
- `replay_mode` ∈ {NONE, ONLINE_1to1, ONLINE_3to1, BATCH_1to1}
- `total_load_alpha` ∈ {0.1, 0.3, 0.5, 0.75} (controlled via N_DIM; α=N_total_items/N_DIM)
- `J_tasks` = 10 fixed (sequential task-batches, ~5k items each)

**Fixed:**
- N_DIM ∈ {auto-set to hit target α}
- 3 seeds (7, 17, 23)
- Pythia-encoded FB15k-237 corpus partitioned by relation-type (10 disjoint relation-groups)

**Anchors (replicates required):**
- α=0.3 NONE replay anchor must reproduce a8 acc=1.000 ± 0.02 (sanity check).
- α=1.5 NONE replay anchor must reproduce a8 acc=0.10 ± 0.05 (capacity floor sanity).

**Primary metric:** `task_A_recall_after_J` = recall@K (set-recall, same as U1) on task-1 facts after all J tasks have been ingested.

**Derived metric:** `forgetting_curve(j)` = task-1 recall measured after each successive task j ∈ {1..10}.

**Secondary metrics:** task-J (most-recent) recall (catastrophic-stability tradeoff); refuse-gate fidelity on out-of-corpus queries (does replay degrade refuse?); ingest wall-time overhead (replay adds ~50-100% wall).

### PRE-REGISTERED HARD THRESHOLDS

**HARD-PASS (chain-grade, mechanism validated):**
- At α=0.5 (cliff regime): task-A recall@J=10 ≥ 0.85 WITH ONLINE_1to1 replay
- At α=0.5: NONE replay shows task-A recall@J=10 ≤ 0.40 (catastrophic-forgetting baseline confirmed)
- Replay-vs-NONE delta ≥ 0.40 at α=0.5
- cv ≤ 0.05 across 3 seeds for both arms
- Refuse-gate accept-rate degrades < 0.05 (replay doesn't pollute refuse)
- Most-recent task-J recall remains ≥ 0.80 (no stability-plasticity collapse)
- Substrate-only-decode gate: zero LLM forward calls at ingest or eval (grep audit + counter assertion)
- Version-marker: `replay_mode`, `total_load_alpha`, `J_tasks`, `replay_ratio` baked into metrics.json

**HARD-PASS-PLUS (super-pass — CLS extends substrate capacity envelope):**
- At α=0.75 (post-cliff, formerly collapsed): task-A recall@J=10 ≥ 0.70 WITH replay (raises usable α from 0.3 to 0.75 — would be a 2.5x capacity boost)

**MIDDLE_BAND (proven bound, partial mechanism):**
- Replay-vs-NONE delta ∈ [0.15, 0.40] at α=0.5 (mechanism real but smaller-than-predicted)

**HARD-FAIL (mechanism wrong):**
- Replay-vs-NONE delta < 0.10 at ALL α — replay does NOT rescue forgetting → the substrate's α-cliff is NOT a forgetting phenomenon; it's a different mode (re-route to SNAP cell, or to capacity-redesign)
- OR: replay-vs-NONE shows recall DEGRADATION (replay hurts) → the replay loop is mis-implemented or substrate has a unique mechanism

**Discriminating-regime requirement (C5):** the CAN-fail regime is α=0.1 (well below cliff — both arms should be ~1.0; replay adds NOTHING) AND α=1.5 (well above cliff — both arms should collapse; replay can't save catastrophic overload). Both endpoints provide a sanity bracket.

**Version-marker requirement:** metrics.json must include `replay_mode`, `replay_ratio`, `J_tasks`, `task_partition_method`, `effective_alpha_per_task`, `total_load_alpha`, `consolidation_rule` ('none' or 'snap_sigmoidal') — prevents experiment-confusion at landed-VET.

### Compute cost
- Each task ingest = ~5k Hebbian writes ≈ 30s on CPU at N_DIM=8192 (per a8 timing).
- ONLINE_1to1 replay doubles the per-task work → ~60s per task × 10 tasks = ~10min per seed.
- 4 replay modes × 4 α values × 3 seeds = 48 runs ≈ 8 hours remote_cpu.
- **Phased recommendation:** Phase 1: ONLINE_1to1 vs NONE at α=0.5 only, 3 seeds → ~1 hour, decisive on the hypothesis. Phase 2 (CONDITIONAL on Phase 1 HARD-PASS): full grid.

### Secondary cell (CONDITIONAL on c1 HARD-PASS): `c2_snap_consolidation_compose_v1`

**Scope:** apply SNAP sigmoidal-weight rule on top of CLS replay; verify multiplicative gain.
**Independent variable:** consolidation threshold θ_consol ∈ {0.5σ, 1σ, 2σ} of |W|; rule on/off.
**Pre-reg HARD-PASS:** task-A recall@J=10 at α=0.75 ≥ 0.85 (post-cliff with full CLS+SNAP).
**Pre-reg HARD-FAIL:** SNAP adds < 0.05 over CLS-alone at any θ.

### Conditional cell (CONDITIONAL on c1 HARD-FAIL): `c1b_diagnostic_forgetting_mode_v1`

If replay fails, the α-cliff is not a forgetting phenomenon. Diagnostic:
- Is the cliff a CAPACITY-saturation (Hopfield-style) or a CROSSTALK phenomenon?
- Test: ingest 5k items into N_DIM=16384 vs. 32768; compare cliff position. If cliff scales linearly with N_DIM, it's capacity-saturation → no replay fix exists; route to Path-A V_C scaling. If cliff doesn't move, it's crosstalk-coding → route to k-WTA-VQ (drill #1) for sparser writes.

---

## FALSIFIABLE PREDICTIONS

### Prediction 1 (PRIMARY) — CLS replay lifts the α-cliff
**Hypothesis:** 1:1 Hebbian generative replay (sampled from U1) reduces sequential-task forgetting in the substrate at α=0.5 from ≤ 0.40 (catastrophic baseline) to ≥ 0.85 (rescued recall).
**Mechanism:** replay re-reinforces old keys at each step, eliminating the asymmetric-decay term in Hebbian crosstalk; equivalent to McClelland's slow-cortex interleaving training.
**HARD-PASS:** task-A recall@J=10 ≥ 0.85 at α=0.5 with ONLINE_1to1 replay.
**HARD-FAIL:** replay-vs-NONE delta < 0.10 at α=0.5.
**Calibrated P(HARD-PASS): 0.45** (capped at novel-synthesis ceiling 0.50; deflated 0.05 because: the CLS mechanism is well-validated in ML and biology but has NOT been validated specifically on substrate's Hebbian-superposition arithmetic; cap-int integration with U1 untested; the α-cliff may have a different cause than catastrophic forgetting — could be a Hopfield saturation that replay cannot rescue).

### Prediction 2 (SECONDARY) — Replay extends usable α from 0.3 to ≥ 0.6
**Hypothesis:** with full CLS replay, the practical usable load (α at which task-A recall remains ≥ 0.80 after J=10 tasks) extends from 0.3 (a8 baseline) to ≥ 0.6 — a 2x capacity envelope expansion.
**HARD-PASS:** α_practical_max ≥ 0.6 (where task-A recall ≥ 0.80 at J=10).
**HARD-FAIL:** α_practical_max ≤ 0.35 (no envelope expansion).
**Calibrated P: 0.35** (independent prediction; the magnitude depends on Hopfield-vs-Willshaw-vs-substrate capacity character; substrate is closer to Willshaw per CERT 591/592, which has steeper capacity walls).

### Prediction 3 (CONDITIONAL on Prediction 1 PASSES) — SNAP composes multiplicatively
**Hypothesis:** SNAP sigmoidal consolidation on top of CLS replay extends α_practical_max further from ≥ 0.6 (CLS-only) to ≥ 0.75 (CLS+SNAP).
**HARD-PASS:** α_practical_max (CLS+SNAP) ≥ 0.75.
**HARD-FAIL:** SNAP adds < 0.05 over CLS alone.
**Calibrated P: 0.30** (Tang 2024 claims "total protection" in Hebbian nets — robust upstream evidence; deflation comes from substrate-specific composition risk + over-consolidation risk on Hebbian-superposition writes that need to remain plastic at moderate strength).

### Prediction 4 (NULLABILITY BRACKET) — at α=0.1 both arms reach ~1.0
**Hypothesis:** at α=0.1 (well below cliff), NONE-replay AND ONLINE_1to1-replay BOTH achieve task-A recall ≥ 0.95 at J=10. Replay-delta ≈ 0.
**Purpose:** confirms below-cliff regime is not where the mechanism operates; sanity check on a8 reproducibility.
**HARD-FAIL:** if replay HURTS at α=0.1 → mechanism is destructive at low load, abandon.

### Prediction 5 (REVIVAL ROUTE if HARD-FAIL) — diagnostic on cliff-mode
**Hypothesis:** if replay does not rescue forgetting, then the α=0.3 cliff is NOT a catastrophic-forgetting phenomenon but a HOPFIELD-style capacity saturation. The revival cell `c1b` (above) tests this.
**Pre-registered routing:** SAME-CYCLE Director note routing the negative (per USER STANDING) with revival angle "Hopfield-saturation diagnostic + k-WTA-VQ from drill #1".

### Prediction 6 (CHEAP DIAGNOSTIC, no separate cell) — Context Channel Capacity audit
**Hypothesis:** the substrate-as-designed (no replay, no context-routing) has C_ctx ≈ 0 (no context signal); per Cheng 2026, forgetting is INEVITABLE. Adding U1 as a context signal (task-key conditioning) provides C_ctx > 0. Replay implicitly does this by re-presenting task-conditioned writes.
**Use:** an architectural-honesty statement in the cell design note; not a measurement, but a CLAIM the cell tests indirectly. **If the substrate succeeds at α=0.5 without ANY context signal, Cheng 2026 says it MUST be implicitly using one** (the random key itself is a context signal); document accordingly.

---

## CROSS-THREAD SYNTHESIS

### Composes with brain-drill #1 (within-concept floor / k-WTA-VQ)
- Drill #1 proposes k-WTA-VQ at biological sparsity f≈0.05-0.10 — this IS the DG-style pattern separator before the CA3 store.
- The CLS architecture predicts that PATTERN-SEPARATED writes are MUCH more robust to forgetting than raw writes (DG's whole purpose).
- **Cross-composition:** drill #1 k-WTA + drill #2 CLS-replay should be MULTIPLICATIVE. k-WTA at f=0.05 reduces crosstalk per-write; replay reinforces old writes. Together, the predicted usable-α extends from 0.3 to possibly 1.0+ (limited by Willshaw capacity for sparse codes ≈ 2 N_DIM / log(N_DIM) which is huge for N_DIM=8192).

### Composes with U1 KG ingest-eval (CERT 584)
- U1 already has the multi-value Hebbian + set-readout-top-k + refuse-gate stack. This IS the hippocampal store at 50k scale with set-recall 0.99, refuse 0.97/0.96.
- The CLS extension is small: add a SAMPLE-AND-REPLAY function that draws from U1 and rewrites to W during continual ingest of NEW facts.
- The U1 chain-grade rules the substrate is READY: the hippocampal piece is built and validated. We need the cortex-loop and replay-bridge.
- **U1 OPEN-C deferred (frozen-encoder semantic baseline)** is orthogonal — c1 doesn't need it (we're testing forgetting on the SUBSTRATE's own writes, not against an encoder baseline).

### Composes with 27x-no-forget MEASURED_MECHANISM (a8 cliff)
- The a8 result IS the substrate's baseline forgetting curve: perfect recall up to α=0.3, cliff at α=0.5, collapse at α=1.5.
- c1 takes a8's anchor and EXTENDS it to the J-task sequential regime. With replay, the cliff should MOVE.
- The intuitive frame: a8 = the substrate's RAM capacity test (how many random keys can we hold?). c1 = the substrate's CONTINUAL-LEARNING test (can we keep task-A while learning task-B..J?). They measure different things; both matter.

### Composes with Hebbian-superposition capacity battery (~327 capacity, baa06f0a)
- The 327-capacity finding is for INDEPENDENT random keys with NN reconstruction.
- The substrate's Hebbian superposition is NN-character (not classical-Hopfield); CERT 592 shows extrapolation beyond classical Hopfield ceiling at moderate α.
- c1 tests whether the NN-character helps OR hurts continual learning. **Prediction:** NN-character is BETTER at capacity but MORE prone to interference (richer overlapping representations have more crosstalk). Replay should rescue this disproportionately.

### Composes with k-WTA-VQ (drill #1, pending cell)
- k-WTA-VQ at the WRITE path IS the DG-style sparsifier.
- c1 can be re-run after k-WTA-VQ lands to measure the multiplicative gain.
- **Order matters:** drill #1 (k-WTA) tests within-concept entropy. Drill #2 (CLS replay) tests across-task forgetting. Both should land independently; their composition is a follow-on.

### Composes with substrate-LM under continual document-stream ingest
- This is the PRODUCT-LEVEL composition. If the glass-box-LLM ingests new documents continuously (no retraining), the CLS+replay+SNAP+k-WTA stack is the architecture that lets it learn at scale without catastrophic forgetting.
- This is the SUBSTRATE'S CORE ADVANTAGE OVER LLMS: LLMs cannot continual-learn (retraining required; in-context window finite). Substrate CAN, IF the CLS+replay machinery is built. c1 is the proof-of-concept that the machinery works.

### Composes with refuse-gate (U1 0.97 OOD-refuse)
- A failure mode of replay: re-presenting a CORRUPTED key (one that was already misremembered) reinforces the error. SNAP exacerbates this.
- The refuse-gate (already in U1) serves as a sanity check: only replay keys that the substrate STILL refuses correctly when queried OOD. This is a substrate-native "memory integrity check" that biology lacks explicitly (or implements via sleep-pruning).

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **CLS is the substrate's MOAT vs. LLMs.** LLMs require offline retraining for new knowledge; substrate CAN ingest online. But the substrate's value of online-ingest only materializes if it doesn't catastrophically forget. CLS+replay turns the substrate's online-ingest from "small-batch demo" into "production-scale continual document stream". This is the path to glass-box-LLM as a LIVING substrate (vs. a frozen one).

2. **The two-store architecture is already present.** U1 (hippocampus) + W (cortex). The product story is: "the substrate has a brain-like two-memory factorization out of the box; new facts go in immediately (U1 episodic), then consolidate to the slow cortex (W) via replay." This is BIOLOGICALLY accurate AND substrate-native AND testable.

3. **The Impossibility Triangle defines the cert-architecture constraints.** Per Cheng 2026: any single-store substrate config is provably forgetting-bound. The substrate's design MUST have either (a) context signals (U1 keys are this), (b) replay (c1 builds this), or (c) regeneration (HyperNetwork-style; not in substrate roadmap). This is a HARD architectural fact, not a heuristic.

4. **SNAP is a 1-line substrate primitive change.** If c1 lands HARD-PASS, c2 (SNAP) is a sigmoidal nonlinearity in the W update — trivial to ship. Combined gains predicted multiplicative.

5. **Forgetting curves become a substrate-LM benchmark.** Every future substrate-LM cell should report the forgetting curve (task-A recall at J=1..J_max) at multiple α — not just one-shot recall. This is the CONTINUAL benchmark that LLMs cannot match.

6. **The substrate's brain-mapping is GENUINELY tight, not metaphor.** k-WTA = DG, U1 = CA3, W = cortex, replay loop = SWR, SNAP = LTP. Each correspondence has a specific mathematical operation and a verified biological reference. This isn't biology-as-inspiration; it's biology-as-spec.

---

## L5 — CROSS-SUBSTRATE COMPOSITION (the path-forward map)

```
                          CATASTROPHIC FORGETTING (untested at scale)
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
       c1 CLS replay              c2 SNAP weight          c1b diagnostic
       hippocampus+cortex         consolidation           (cliff-mode probe)
       P(HARD-PASS)=0.45          P(HARD-PASS)=0.30       conditional on c1 FAIL
            │
   ┌────────┼────────┐
   ▼        ▼        ▼
α=0.1   α=0.5     α=0.75
(null   (cliff:   (post-cliff:
bracket) decisive) capacity envelope)
   │
   ▼  (if HARD-PASS at α=0.5)
   ┌────────────────┴────────────────┐
   ▼                                 ▼
c1 + drill #1 k-WTA              c1 + c2 SNAP
(DG-style separator              (per-weight forget-
adds at write)                   protection adds)
   │                                 │
   └────────────────┬────────────────┘
                    ▼
       FULL CLS substrate stack
       (k-WTA + U1 + W + replay + SNAP)
       predicted: usable α → 1.0+
                    │
                    ▼ (if HARD-PASS)
       Glass-box-LLM continual-document-stream
       substrate's MOAT vs. LLM realized
                    │
                    ▼
       Compose with N1 substrate-LM (MM) +
       Hebbian-superposition #7 (CERT 591) +
       U1 inference-2hop (CERT 584)
       ⇒ substrate-native lifelong learner
```

**If c1 HARD-FAIL:**
```
c1 HARD-FAIL (replay does NOT rescue forgetting)
    │
    ├─→ ROUTE TO RESEARCH (USER STANDING)
    │   revival angle: c1b diagnostic — is cliff Hopfield-saturation OR crosstalk?
    │
    └─→ if Hopfield: route to Path A V_C scaling (more capacity)
        if crosstalk: route to k-WTA-VQ (drill #1 lands first)
```

---

## CITATIONS (verified, count = 16)

1. McClelland, J.L., McNaughton, B.L., O'Reilly, R.C. (1995). "Why there are complementary learning systems in the hippocampus and neocortex: insights from the successes and failures of connectionist models of learning and memory." Psychological Review 102(3): 419-457. (CLS foundational; the two-system thesis.) [ResearchGate](https://www.researchgate.net/publication/15575602_Why_There_are_Complementary_Learning_Systems_in_the_Hippocampus_and_Neocortex_Insights_from_the_Successes_and_Failures_of_Connectionist_Models_of_Learning_and_Memory)

2. Kumaran, D., Hassabis, D., McClelland, J.L. (2016). "What learning systems do intelligent agents need? Complementary Learning Systems theory updated." Trends in Cognitive Sciences 20(7): 512-534. (Modern CLS for AI; explicit substrate design rationale.) [CBMM PDF](https://www.cnbc.cmu.edu/~tai/nc19journalclubs/KumaranHassabisMcC16CLSUpdate.pdf)

3. O'Reilly, R.C. (2014). "Complementary Learning Systems." Cognitive Science. (DG/CA3/CA1 architecture mapping.) [Wiley](https://onlinelibrary.wiley.com/doi/10.1111/j.1551-6709.2011.01214.x)

4. Wilson, M.A., McNaughton, B.L. (1994). "Reactivation of hippocampal ensemble memories during sleep." Science 265(5172): 676-679. (Canonical replay paper; ~20x temporal compression.)

5. Diekelmann, S., Born, J. (2010). "The memory function of sleep." Nature Reviews Neuroscience 11: 114-126. (Sleep replay rates and consolidation timescales.)

6. Klinzing, J.G., Niethard, N., Born, J. (2019). "Mechanisms of systems memory consolidation during sleep." Nature Neuroscience 22: 1598-1610. [Nature](https://www.nature.com/articles/s41593-019-0467-3) (Replay-to-experience ratios; SWR mechanism.)

7. Rasch, B., Born, J. (2013). "About sleep's role in memory." Physiological Reviews 93(2): 681-766. (Synaptic vs systems consolidation distinction.)

8. Gonzalez, O.C., et al. (2020). "Can sleep protect memories from catastrophic forgetting?" eLife 9:e51005. (Sleep-style Hebbian replay rescues forgotten tasks in ANNs.)

9. Tadros, T., Krishnan, G.P., Ramyaa, R., Bazhenov, M. (2022). "Sleep-like unsupervised replay reduces catastrophic forgetting in artificial neural networks." Nature Communications. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9755223/) (Pure Hebbian replay; 19.49% → 48.47% retention; 5-task MNIST.)

10. van de Ven, G.M., Siegelmann, H.T., Tolias, A.S. (2020). "Brain-inspired replay for continual learning with artificial neural networks." Nature Communications 11: 4069. [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7426273/) (Generative replay benchmark; backprop but architecture transferable.)

11. Shin, H., Lee, J.K., Kim, J., Kim, J. (2017). "Continual Learning with Deep Generative Replay." NeurIPS 2017. (Original generative-replay paper.)

12. Rolls, E.T. (2013). "The mechanisms for pattern completion and pattern separation in the hippocampus." Frontiers in Systems Neuroscience 7:74. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3812781/) (DG sparse separation + CA3 attractor completion; capacity bounds.)

13. Cayco-Gajic, N.A., Silver, R.A. (2019). "Re-evaluating Circuit Mechanisms Underlying Pattern Separation." Neuron 101: 584-602. (DG circuit model; sparse + expansion.)

14. Cheng, R. (2026). "Context Channel Capacity: An Information-Theoretic Framework for Understanding Catastrophic Forgetting." arxiv 2603.07415. [arxiv](https://arxiv.org/abs/2603.07415) (Impossibility Triangle; C_ctx ≥ H(T) requirement.)

15. Tang, K., et al. (2024). "SNAP: Stopping Catastrophic Forgetting in Hebbian Learning with Sigmoidal Neuronal Adaptive Plasticity." arxiv 2410.15318. [arxiv](https://arxiv.org/abs/2410.15318) [OpenReview](https://openreview.net/pdf?id=Vo0XJGyFQb) (Per-weight LTP-like consolidation; total protection in Hebbian nets.)

16. Yan, Y., et al. (2025). "A Neural Network Model of Complementary Learning Systems: Pattern Separation and Completion for Continual Learning." arxiv 2507.11393. [arxiv](https://arxiv.org/html/2507.11393v1) (VAE+MHN CLS for split-MNIST; 1:1 replay ratio optimal; 89.71% vs 67.75% no-replay.)

---

## LIT-SCAN CALIBRATION NOTES

- All probability estimates deflated 0.15-0.25 from raw LM confidence.
- **Novel-synthesis cap at 0.50 applied:** the CLS replay loop wired specifically to the substrate's U1 + W + Hebbian-superposition has no prior empirical validation in this exact configuration. P(HARD-PASS) = 0.45 reflects the cap + deflation. CLS-replay is well-validated in deep nets (van de Ven 2020) and in spiking/Hebbian (Tadros 2022); the specific substrate composition is the novel piece.
- **HARD-FAIL thresholds mandatory and listed for every prediction.**
- The DIRECTIONALITY (replay reduces forgetting) is HIGHLY confident (raw P ≈ 0.75-0.85, robust across 3 independent literatures: McClelland CLS, Tadros sleep-replay, van de Ven brain-inspired-replay). The MAGNITUDE (≥ 0.85 task-A retention at α=0.5) is where the deflation hits — the substrate's specific Hebbian-superposition arithmetic may behave differently from MNIST/CIFAR benchmarks.
- The substrate's α=0.3 cliff anchor (a8 HARD_PASS) is the load-bearing prior; without it, the cell-design has no calibration. With it, c1 has a clear sanity bracket.
- **Cheng 2026 Impossibility Triangle is a STRONG architectural result** but does NOT directly predict a specific magnitude; it predicts WHICH ARCHITECTURES CAN WORK (CLS counts; single-store doesn't). The substrate's design already has the right ingredients.

---

## DISPATCH RECOMMENDATION

**Immediate (Exp-Dev, after current sequencing):** `c1_cls_replay_continual_ingest_v1`
- Same harness scaffold as U1 (already validated at 50k scale).
- Phase 1: ONLINE_1to1 vs NONE at α=0.5 only, J=10 tasks, 3 seeds. ~1 hour remote_cpu. **Decisive on the primary hypothesis.**
- Phase 2 (CONDITIONAL on Phase 1 HARD-PASS): full grid α∈{0.1, 0.3, 0.5, 0.75} × replay_mode∈{NONE, ONLINE_1to1, ONLINE_3to1, BATCH_1to1}, 3 seeds. ~8 hr.
- Anchors: α=0.3 NONE replicates a8 acc=1.000; α=1.5 NONE replicates a8 acc=0.10.
- Version-marker: `replay_mode`, `replay_ratio`, `J_tasks`, `total_load_alpha`, `effective_alpha_per_task`, `task_partition_method`.

**Composition prep (free piggyback after c1 lands):**
- Include c1b diagnostic measurements (N_DIM-scaling at fixed M) at no extra cost.

**Conditional next:** `c2_snap_consolidation_compose_v1` if c1 HARD-PASS at α=0.5.

**Ordering vs drill #1 k-WTA:**
- **Drill #1 and drill #2 are INDEPENDENT** (k-WTA tests within-concept entropy; CLS tests across-task forgetting). They can ship in parallel.
- Drill #2 c1 should land BEFORE drill #1 k-WTA if compute is constrained: c1's a8-anchor is firmer (HARD_PASS), and the replay-rescue mechanism is more directly substrate-product-relevant (continual ingest IS the moat). Drill #1 is for within-concept compression.

**Ordering vs N3 / N4 / Path A:**
- c1 is CONTINUAL LEARNING capability (substrate-LM moat), not LM-decode capacity. ORTHOGONAL to N-cells. Ship independently.

---

## PLAIN-ENGLISH WRAP (Fix #13)

The substrate has been claiming "no catastrophic forgetting" based on a one-shot capacity-saturation test (a8), but never tested under the ACTUAL conditions where forgetting matters: ingest TASK A, then TASK B, then TASK C... and ask whether A survives. That's continual learning. Biology solved continual learning ~300 million years ago by separating fast/episodic (hippocampus) from slow/general (cortex), with a SLEEP REPLAY loop that re-presents old memories interleaved with new. The math is settled (McClelland 1995, validated through 2026): you need either two stores + replay, or per-weight consolidation thresholds (SNAP), or a hyper-network. The substrate ALREADY HAS TWO STORES (U1 is the hippocampus at CERT 584; the W matrix is the cortex). The only missing piece is the REPLAY LOOP — sample old keys from U1, re-Hebbian-bind them into W alongside new keys, at a 1:1 ratio. That's a substrate-native code change with no LLM forward calls and no backprop, fully compatible with the substrate-only-decode gate. Cell `c1_cls_replay_continual_ingest_v1` tests this in ~1 hour on remote_cpu with hard pre-registered bands. If it lands (P=0.45), the substrate has a working continual-learning loop — the missing capability that makes it a credible LLM-alternative for online knowledge ingest.

---

-- Research (Opus synthesis, lit-scan via 8 parallel web queries + 2 paper fetches, deflated per calibration). Companion to drill #1 (within-concept floor). Both drills converge on the same architectural prior: the substrate's right configuration is biologically tight — DG sparse separator (drill #1) + CA3/cortex two-store with replay (drill #2) + LTP-like per-weight consolidation (SNAP). Each cell ships independently; the full stack is the path to glass-box-LLM continual-document-stream.
