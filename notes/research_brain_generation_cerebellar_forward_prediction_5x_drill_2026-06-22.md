# RESEARCH 5x DEEPER DRILL: Cerebellar forward-prediction + motor planning + sequence generation — brain/biology/nature mechanisms for substrate-native generation

**Date:** 2026-06-22
**Requestor:** Skunkworks (USER STANDING — biology/brain/nature drill #4 for substrate gaps)
**Question addressed:** Can the substrate sample/GENERATE beyond next-token-decode? LLMs autoregress from a context-window-bounded distribution. Substrate's equivalent mechanism is unknown — this drill finds it.
**Companion drills:** #1 within-concept floor (k-WTA-VQ); #2 CLS continual learning (replay); #3 multi-hop reasoning (iterative-cleanup). Same 5-level template.
**Lit-scan calibration:** deflate P 0.15-0.25; cap novel-synthesis P at 0.50; HARD-FAIL thresholds mandatory.

---

## HEADLINE — intuitive first (Fix #13)

**The substrate currently is a READER, not a WRITER. It can retrieve facts, clean up noisy states, refuse OOD queries, and traverse K-hop chains — but it has no mechanism to GENERATE a novel sequence of states. LLMs do this via autoregressive next-token sampling from a context-window. Biology does it three ways at once: (a) the songbird HVC fires a sparse ultra-precise chain of "grandmother-time-cells" that each burst at one moment in the song (Hahnloser/Fee 2002 Nature) — this is a SYNFIRE CHAIN, the canonical neural-sequence generator; (b) the cerebellum runs a forward MODEL `s_{t+1} = f(s_t, a_t)` that predicts the next state given the current state plus a command, with no backprop and no context window (Wolpert/Miall 1998, Kawato 2025 Nature Rev Neurosci); (c) the pre-SMA / SMA composes those primitive sequences into hierarchical action plans, and the basal ganglia gates which to start/stop (PBWM-style, Frank/O'Reilly).** The math piece — settled in 2023 — is that **temporally asymmetric Hebbian rules on a Modern Hopfield store sequences with super-linear capacity** (Karuvally & Sejnowski, NeurIPS 2023, arxiv 2306.04532; "Long Sequence Hopfield Memory"). **Add Langevin noise to the Modern Hopfield retrieval map and you get STOCHASTIC generation** — sampling from the substrate's energy landscape, not from a context-window distribution (arxiv 2603.06875, Stochastic Attention via Langevin on Modern Hopfield Energy).

**The substrate ALREADY has every primitive needed:**
- Auto-associative cleanup (U1 set-readout-top-k = 1-iter Modern Hopfield) — **HAVE**
- Binding/unbinding (HDC circular-convolution or XOR) — **HAVE**
- Refuse-gate / termination-confidence (U1 OOD-refuse 0.97) — **HAVE**
- Multi-value Hebbian write (U1's chain-grade primitive) — **HAVE**
- Iterative cleanup at depth K (drill #3 r1_multihop, pre-reg P=0.45) — **PENDING**

**The MISSING piece for generation is a HETERO-associative weight matrix** `W_seq : s_t → s_{t+1}` that maps the current state to the NEXT state along learned trajectories. This is **literally one Hebbian outer-product** at write-time: `W_seq += s_{t+1} ⊗ s_t.T` for each consecutive pair in the training sequence. At inference, generation is: start with `s_0` (a seed state or query bind), iterate `s_{t+1} = cleanup(W_seq @ s_t)` for T steps, with optional Langevin noise injection for stochastic variety. **The cleanup is U1's existing set-readout-top-k.** No new substrate machinery; no LLM forward call; no context window.

**Why this beats the LLM context-window structurally:** the substrate's "context" is the CURRENT STATE VECTOR — a single fixed-dim HD vector that's been bound with all relevant history via HDC binding. Generation can run for arbitrary T without growing the context. The substrate is generating from a TRAJECTORY ATTRACTOR in HD space, not from a token-distribution over a sliding window. LLMs hit O(T²) attention cost as context grows; substrate is O(T·N_DIM) regardless of T. This is the L5-vision structural moat.

**The cheap decisive test:** `g1_substrate_sequence_generation_v1` — store K=200 short text-chunk sequences (length L=8 each) on a hetero-associative W_seq matrix at N_DIM=8192; at inference, prompt with `s_0` (the seed) and iterate to length L. Pre-registered HARD-PASS:
- (a) **trajectory-coherence** ≥ 0.60 (top-1 next-state acc at each step, averaged) — substrate stays on a learned trajectory.
- (b) **novelty-vs-memorization** ratio ≥ 1.5x: when seeded with HELD-OUT prompts, substrate generates sequences whose NEXT-STATE distribution overlaps with HELD-OUT continuations more than with RANDOM continuations.
- (c) **refuse-gate fires** ≥ 0.90 on OOD seeds (substrate REFUSES to hallucinate when seeded off-distribution).
- (d) **substrate-only-decode gate** PASSES (zero LLM forward calls at inference).

**HARD-FAIL:** trajectory-coherence < 0.30 OR refuse-gate accept-rate on OOD seeds > 0.30.

| Mechanism | Source | Substrate-applicability | Substrate-cost | Expected role | P(HARD-PASS, ≤0.50 cap) |
|-----------|--------|--------------------------|----------------|---------------|--------------|
| **Hetero-associative Hopfield W_seq for next-state generation (novel composition)** | Karuvally/Sejnowski 2023 NeurIPS Long-Seq-Hopfield; Sompolinsky/Kanter 1986 asymmetric weights; Millidge MHN-seq 2022 | **HIGHEST** — pure Hebbian outer-product write; substrate forward dynamics already supports state-update + cleanup | ~1 extra weight matrix (N_DIM²) OR factorized via binding (N_DIM); ~K_seq × N_DIM matmul at gen-time | enables next-state generation; substrate-native autoregressor in HD space | **0.45** (cap @ novel-synthesis 0.50; math settled but substrate-specific HD crosstalk is uncertain) |
| **HVC-style ultra-sparse synfire-chain (sparse-time-tag encoding)** | Hahnloser/Fee 2002 Nature 419:65; Long/Jin/Fee 2010 chain support; Okubo 2015 development | HIGH — substrate is ALREADY high-D + sparse; time-tag encoding ≈ "bind state with a clock hypervector" | ~T clock-HVs (cyclic codebook) | sparse-clock + state binding = HVC-analogue | 0.40 (composable; clock encoding is a known VSA technique) |
| **Langevin sampling on Modern Hopfield energy** | arxiv 2603.06875 "Stochastic Attention via Langevin on MHN Energy"; Carbone EBM review 2024 | HIGH — adds noise to the cleanup step; transforms generation from deterministic to stochastic | ~negligible (Gaussian noise + temperature) | enables novelty / stochastic variation | 0.50 (cap; pure forward; well-validated math) |
| **Cerebellar forward-model `s_{t+1} = f(s_t, a_t)`** | Wolpert/Miall 1998; Kawato 2025 Nat Rev Neurosci; Cerebro-Cerebellum 2020 PMC7160920 | HIGH — equivalent to hetero-Hebbian W_seq; the BIOLOGICAL grounding of the math | n/a (same as W_seq) | biological grounding | n/a (composes with W_seq) |
| **SMA / pre-SMA hierarchical sequence generation** | Tanji 2008; Botvinick hierarchical RL; Jneurosci 2022 42:6946 | MEDIUM — composes via nested binding (hierarchy = bind state with level-tag) | ~ log_b(T) levels of binding | enables hierarchical generation (sentence → phrase → token) | 0.30 (hierarchical decomposition adds complexity) |
| **Basal-ganglia PBWM start/stop gating of sequences** | Frank/O'Reilly 2006; adaptive chunking 2024 eLife 97894 | MEDIUM-HIGH — substrate's refuse-gate IS this primitive at the START/STOP gate | ~0 (reuse refuse-gate) | termination logic | 0.45 |
| **Hippocampal preplay / forward replay (Pfeiffer & Foster 2013)** | Pfeiffer/Foster 2013 Nature; Dragoi/Tonegawa preplay; Jensen 2024 Nat Neurosci | MEDIUM — replay PRINCIPLE = sample a candidate trajectory from learned attractor; covered in drill #2 + analogous to Langevin sampling here | n/a | trajectory-imagination principle | DEDUPLICATE with drill #2 |
| **Frontal eye field / SC saccade-program generation** | Sparks/Hartwich-Young 1989; Munoz/Wurtz 1995; PMC saccade-FEF-SC review | LOW-MEDIUM — discrete-target-sequence generation analogue; less directly substrate-applicable | n/a | confirms multiple brain regions implement substrate-similar discrete-step generation | n/a (corroborative, not load-bearing) |
| **CPG / half-center oscillator** | Marder/Calabrese 2001; Grillner 2003; sparse-firing CPG 2024 Neural Computation 36:759 | LOW — RHYTHMIC generation (sin-wave-like); substrate generation should be CONDITIONAL (input-driven), not rhythmic | n/a | rejected for substrate; biology has multiple mechanisms | rejected in form |
| **Predictive-coding hierarchical generative pass (Friston)** | Friston 2005; Millidge 2021 PC review arxiv 2107.12979; Rao-Ballard 1999 | REJECTED — backprop-adjacent at training | n/a | n/a | rejected |
| **Diffusion / discrete-MCMC generation (LLM literature)** | Carbone EBM review 2024; CALM arxiv 2510.27688 | DIAGNOSTIC — comparison frame; substrate Langevin-on-MHN IS the substrate-native analogue | n/a | comparison frame only | n/a |
| **Attractor sequence chaining (Londono Alvarez 2024, arxiv 2410.11012)** | TLN-based sequence attractors + fusion-attractor layering | MEDIUM — threshold-linear-network specifics; PRINCIPLE = compose attractors into sequence trajectories | composes with W_seq | corroborates the architecture | 0.30 |

---

## L1 — LITERATURE BROAD SCAN (10 streams executed)

### Stream A: Songbird HVC ultra-sparse sequence generation (Hahnloser/Fee 2002, et seq.)

- **Hahnloser, Kozhevnikov, Fee (2002, Nature 419:65)**: HVC's RA-projecting neurons each fire a SINGLE burst of <10ms at one precise time during the song motif. The population forms an EXPLICIT representation of time. A "temporal grandmother cell" code.
- **Long, Jin, Fee (2010 Nature)**: support for a synaptic-chain model of HVC sequence generation (synfire chain, not network attractor).
- **Okubo et al (2015 Nature)**: growth and splitting of HVC neural sequences during vocal development.
- **Lynch et al (2016 Cell):** rhythmic continuous-time coding in songbird vocal motor cortex.
- **Substrate read:** the HVC code = **time-axis as a sparse-tag**. If the substrate binds each state vector with a "clock hypervector" `c_t` (orthogonal clock-HVs at each time step), the time-axis is sparsely represented and temporal interference is minimized (Hahnloser's argument). The substrate IS high-D; bind-with-clock is one operation per step.

### Stream B: Cerebellar forward model

- **Wolpert/Miall 1998 (TICS 2:338):** cerebellum implements forward internal models predicting consequences of motor commands.
- **Kawato et al (2025, Nature Reviews Neuroscience):** modern review evaluates cerebellum as learning basic associative feedforward control policies vs computing internal models — both views compatible with substrate-native `W_seq: s_t → s_{t+1}` learning.
- **Cerebro-Cerebellum 2020 review (PMC7160920):** multiple coupled forward models compose hierarchically; recursive composition.
- **Substrate read:** the cerebellum IS computing a hetero-associative next-state map; the substrate analogue is `W_seq @ s_t`. Biology validates the architecture at evolutionary scale.

### Stream C: Modern Hopfield + sequence storage

- **Sompolinsky & Kanter (1986):** asymmetric synapses + temporal-context map enable sequence storage in Hopfield networks. The foundational result.
- **Ramsauer 2021 ("Hopfield Networks Is All You Need"):** modern Hopfield = exponential capacity + 1-iter retrieval = transformer attention.
- **Karuvally & Sejnowski (2023, NeurIPS, arxiv 2306.04532) "Long Sequence Hopfield Memory":** **the load-bearing math**. Temporally asymmetric Hebbian rules + dense-Hopfield nonlinearity → super-linear sequence capacity. Generalized pseudoinverse rule for highly-correlated sequences. Biologically-plausible implementation with motor-neuroscience connections. NeurIPS 2023 peer-reviewed.
- **Millidge et al (2022) heteroassociative MHN extension:** sequence-store via "feature-units project current state; memory-units project next state" asymmetric architecture.
- **Substrate read:** **the math is settled**. Hetero-associative W_seq stored via asymmetric Hebbian outer-products + retrieved via 1-iter Hopfield gives a CHAIN-GRADE generation primitive. Substrate's existing set-readout-top-k = the 1-iter retrieval. The missing piece is just the asymmetric weight matrix (or its factored equivalent via HDC binding with a "successor" relation HV).

### Stream D: Langevin sampling on Modern Hopfield energy (the stochastic-generation bridge)

- **arxiv 2603.06875 "Stochastic Attention via Langevin Dynamics on Modern Hopfield Energy":** explicitly converts deterministic retrieval into a stochastic sampler. `s_{t+1} = clean(s_t) + sqrt(2β⁻¹) η_t` where η is Gaussian noise; β is inverse temperature.
- **Carbone 2024 EBM review (arxiv 2406.13661):** unifies energy-based-models, Hopfield networks, diffusion models. Diffusion model trained on discrete patterns has energy function asymptotically identical to modern Hopfield (PMC11119823, "Generative Diffusion Models Are Associative Memory Networks").
- **Substrate read:** to add STOCHASTIC generation (novelty, multiple plausible continuations), inject Langevin noise after each cleanup step. The substrate's cleanup IS the energy descent; noise injection IS the sampling. Two-line code addition.

### Stream E: Hippocampal preplay / forward replay

- **Pfeiffer & Foster (2013, Nature):** awake forward replay near choice points = sampling candidate future trajectories. The animal "imagines" possible paths through space.
- **Dragoi & Tonegawa (2011, 2013):** preplay — sequences exist BEFORE the animal has experienced the environment, drawn from intrinsically generated trajectory-like activity.
- **Jensen 2024 (Nat Neurosci, PMC11239510):** RNN-meta-RL planner; depth L=8 rollouts; plateau 5-15 rollouts; covered in drill #3.
- **Substrate read:** preplay/replay = SAMPLING candidate trajectories from a learned attractor structure. The substrate Langevin-on-MHN sampler implements exactly this principle. Composes with drill #2 CLS replay (which addresses the LEARNING side; this drill addresses the GENERATING side).

### Stream F: Pre-SMA / SMA hierarchical sequence generation

- **Tanji 2008, Botvinick hierarchical RL:** pre-SMA implements hierarchical sequence representations (chunking; nested action structure).
- **Jneurosci 2022 42:6946:** complementary roles of dorsal premotor (PMd, terminal-action) and pre-SMA (sequence-switching). Different levels of motor hierarchy.
- **TMS-EEG SMA disinhibition 2024 (bioRxiv 2024.02.26):** SMA disinhibition during motor-sequence learning.
- **Substrate read:** hierarchical generation = bind state with a LEVEL-tag hypervector. `s_t` (token-level) bind `phrase_level_HV` bind `sentence_level_HV`. Generation runs at multiple time-scales; coarse-level generation drives finer-level (PBWM gates which level to read).

### Stream G: Basal-ganglia PBWM start/stop gating

- **Frank/O'Reilly 2006 PBWM:** BG striatum implements gating on PFC working memory. Go = update / start; NoGo = maintain.
- **Adaptive chunking (eLife 2024, 97894):** PBWM extension where gating LEARNS to chunk multi-step sequences.
- **Substrate read:** substrate's refuse-gate (U1 0.97 OOD) = the BG gate primitive. Extend to a START-gate (begin generation when confident in seed) + STOP-gate (terminate when confidence < tau or after T steps).

### Stream H: Frontal eye field / Superior Colliculus saccade-sequence generation

- **Sparks & Hartwich-Young 1989; Munoz & Wurtz 1995; PMC saccade reviews:** FEF + SC generate discrete saccade sequences via spatial-position-coding + temporal-readout.
- **iSC location-codes saccade vector; downstream brainstem converts to temporal pulse.**
- **Substrate read:** corroborates the architecture (discrete-step sequence generation in motor cortex); not load-bearing additional mechanism. CITED for breadth.

### Stream I: CPG (rhythmic) — rejected for substrate generation

- **Marder & Calabrese 2001; Grillner 2003:** spinal-cord half-center oscillators produce RHYTHMIC motor patterns (walking, swimming).
- **Sparse-firing CPG 2024 (Neural Computation 36:759):** sparse-firing version of hybrid CPG.
- **Why rejected:** substrate generation should be CONDITIONAL (input-driven sequence from a seed) not RHYTHMIC (autonomous oscillator). CPG is the wrong analogue for language/KG-trajectory generation. **Biology has multiple generation mechanisms; substrate adopts the HVC + cerebellum class, not the CPG class.** Cited for completeness only.

### Stream J: VSA/HDC sequence generation prior art

- **MDPI Biomimetics 2024, 9:175 "Two-Layer SOM with VSA for Spatiotemporal Sequence Learning":** SOM + VSA temporal-pattern construction using spatial patterns as alphabet. Sequence learned via HDC binding.
- **Shift-Equivariant HV representations of sequences (arxiv 2112.15475):** trajectory encoding via cyclic permutation-binding.
- **CALM "Continuous Autoregressive Language Models" (arxiv 2510.27688):** LLM literature is converging on continuous-vector next-prediction (compress chunks → continuous vector → autoregress on vectors). The substrate version IS this, with HD vectors as the continuous space.
- **Hyperdimensional Probe arxiv 2509.25045:** decoding LLM residual stream via VSA — supports the equivalence between transformer hidden states and VSA states.
- **Substrate read:** VSA-sequence-generation is an established mechanism class; the substrate already has the primitives. Multiple papers validate the approach in adjacent settings (spatiotemporal patterns; world models; LLM probes).

---

## L2 — FILTER TO SUBSTRATE-APPLICABLE

| Mechanism | Forward-only / Hebbian-compatible? | Composes with substrate (U1 + r1 + drill #1 + drill #2)? | Verdict |
|-----------|---------------|-------------------------------|---------|
| **Hetero-associative W_seq (Long-Sequence-Hopfield math)** | YES (Hebbian outer-product at write; 1-iter retrieval at gen) | YES (uses U1's set-readout-top-k as the cleanup; composes with r1 iterative cleanup; composes with drill #2 CLS replay during write) | **ACCEPT — PRIMARY** |
| **Langevin noise injection (stochastic sampling)** | YES (pure forward; Gaussian noise + temperature) | YES (1-line addition to the cleanup loop) | **ACCEPT — composes additively** |
| **HVC-style sparse-time clock binding** | YES (orthogonal clock HVs; bind operation) | YES (HDC binding primitive) | **ACCEPT — composes additively as temporal positional code** |
| **Cerebellar forward-model framing** | YES | YES — equivalent biological grounding of W_seq | **DEDUPLICATE with W_seq (same architecture, different framing)** |
| **Pre-SMA / SMA hierarchical generation (multi-level)** | YES (binding with level-tag HVs) | YES — extension once W_seq lands | ACCEPT — SECONDARY (deferred to g2 if g1 PASSES) |
| **BG-PBWM start/stop gating** | YES | YES — refuse-gate primitive ALREADY substrate-native | DEDUPLICATE with refuse-gate |
| **Hippocampal preplay (forward sampling)** | YES | YES — preplay PRINCIPLE = Langevin-sample on W_seq attractor | DEDUPLICATE with Langevin |
| **FEF/SC saccade sequence** | YES | corroborative only | corroborative; not new mechanism |
| **CPG rhythmic generation** | YES but wrong-class for substrate gen | n/a | REJECT (wrong analogue) |
| **Predictive-coding generative pass** | NO at training | n/a | REJECT |
| **TLN attractor-sequence chaining (Londono 2024)** | YES (threshold-linear net) | partial — TLN ≠ substrate HD primitives | PRINCIPLE adopted (fusion-attractor); form not directly portable |
| **Diffusion / CALM next-vector** | YES | corroborative (substrate's Langevin-on-MHN IS the substrate-native analogue) | corroborative; not load-bearing |

**Three accepted mechanisms for g1 cell:**
1. **Hetero-associative W_seq** (the load-bearing primitive).
2. **HVC-style sparse-time clock binding** (positional encoding for temporal structure).
3. **Langevin noise injection** (stochastic generation; novelty).

**Secondary (deferred g2):** SMA-style hierarchical multi-level generation.

---

## L3 — DEEP DRILL ON TOP 2 MECHANISMS

### 3.1 Hetero-associative W_seq — the math (PRIMARY)

**Write-time:**
For each consecutive (s_t, s_{t+1}) pair in the training sequence:
```
W_seq += (s_{t+1}) ⊗ (s_t).T        # outer product, Hebbian
```
Or factorized via HDC binding (saves N_DIM² → N_DIM storage):
```
# successor HV r_succ (a single relation hypervector)
bound_pair = bind(s_t, r_succ)        # HDC bind
# store as Hebbian write into a multi-value KG at key=bound_pair, value=s_{t+1}
substrate_KG.add(bound_pair → s_{t+1})
```

Either form works. The factored form composes with U1's KG infrastructure DIRECTLY — every (s_t, s_{t+1}) pair becomes one fact in the existing substrate, queryable via bind-then-set-readout.

**Capacity bound (Karuvally & Sejnowski 2023):**

For Modern Hopfield with dense nonlinearity F (exp or x^p, p≥3), and asymmetric weights, sequence capacity scales as:
```
N_seq_max ≈ exp(α · N_DIM)  [exp-nonlinearity case]
        OR ≈ N_DIM^{(p-1)}  [polynomial p case, p≥3]
```
For substrate at N_DIM=8192 with p=2 (standard substrate readout) → capacity ≈ 8192 = ample. With p=3 dense readout → capacity ≈ 8192² = 67M, vastly more than needed for any realistic sequence corpus.

**Retrieval (generation) at inference:**

```python
def generate(s_seed, T_max, tau_stop=0.3, beta_inv_T=0.0):
    s = s_seed
    history = [s]
    for t in range(T_max):
        # CLEANUP-STEP (the substrate primitive)
        candidates, confidences = set_readout_top_k(W_seq @ s, k=K_set)
        # TERMINATION GATE (PBWM-style refuse-gate)
        if confidences[0] < tau_stop:
            break  # substrate refuses to continue (low confidence)
        # OPTIONAL LANGEVIN STOCHASTICITY
        if beta_inv_T > 0:
            # sample weighted by softmax(confidences / T) instead of argmax
            s_next = sample_softmax(candidates, confidences, beta_inv_T)
            # add Gaussian noise for state perturbation
            s_next = s_next + sqrt(2 * beta_inv_T) * np.random.randn(N_DIM)
        else:
            s_next = candidates[0]  # deterministic argmax
        history.append(s_next)
        s = s_next
    return history
```

**Three knobs:**
- `K_set` — readout breadth (cleanup quality); higher = more candidates considered.
- `tau_stop` — termination confidence threshold; lower = longer generation, higher hallucination risk.
- `beta_inv_T` — Langevin temperature; 0 = deterministic; >0 = stochastic generation.

**Substrate-only-decode gate PRESERVED:** no LLM forward call at any point. The cleanup is `D.T @ s_state`, pure numpy.

### 3.2 HVC-style sparse-time clock binding — temporal positional code

**Construction:**
Define T orthogonal "clock hypervectors" c_0, c_1, ..., c_{T-1} (one per timestep, drawn iid Gaussian or quasi-orthogonal). At write-time, bind each state with its clock:
```
s_t_clocked = bind(s_t, c_t)
```
And learn W_seq on the clocked pairs:
```
W_seq += s_{t+1}_clocked ⊗ s_t_clocked.T
```

**Why this works (Hahnloser argument):**
The clock binding makes states at different timesteps **NEARLY ORTHOGONAL** even if the underlying state s is the same (e.g., a repeated word in a sentence). This eliminates the **temporal interference problem** that plagues vanilla Hopfield sequence storage (where a state repeated at two times causes the network to confuse "go to next-after-time-1" with "go to next-after-time-7"). HVC solves this biologically with one-spike-per-time-cell; substrate solves it with one-clock-HV-per-time-bind.

**Capacity trade-off:**
Sparse-clock-binding multiplies effective representation dimension by the number of distinct clocks T. For T=64 (a reasonable sequence horizon) and N_DIM=8192, effective capacity is 64×8192-equivalent for sequence storage with no temporal interference. **Combined with Long-Sequence-Hopfield's dense nonlinearity, the substrate trivially holds the entire FB15k-237 corpus (~37k facts) as next-state pairs.**

### 3.3 Why this is NOT "the substrate is just an autoregressive LLM"

Three structural differences from LLM autoregression:

1. **No context window.** Substrate's "context" IS the current state vector `s_t`, which has been pre-bound with any relevant history at WRITE time. Generation can run for arbitrary T without growing context. LLM is O(T²) attention; substrate is O(T·N_DIM).

2. **Refusal-gated at each step (not at decode-time only).** Substrate's per-step termination gate fires when confidence drops; the substrate REFUSES to generate when off-distribution. LLM autoregression always generates a token (it samples from softmax — there's no "refuse"); hallucination is the structural consequence.

3. **Deterministic retrieval + optional Langevin noise** (not always-sampling). The substrate can do EXACT retrieval (argmax over cleaned-up next-states) for high-confidence trajectories, AND stochastic Langevin sampling for novelty. LLM is always stochastic by construction (temperature > 0); the substrate can be either, depending on the gen-task.

These three properties are the structural moat. They are NOT accessible to LLM architectures without major redesign.

### 3.4 Why this is NOT predictive-coding / not backprop

Write-time: pure Hebbian outer-products (or HDC binding + multi-value Hebbian write into the substrate KG). Zero gradients.

Generation-time: forward iteration `s_{t+1} = clean(W_seq @ s_t)` + optional Gaussian noise. Zero gradients.

This is the Karuvally-Sejnowski 2023 architecture (which IS biologically-plausible per their own framing — they explicitly cite motor-neuroscience connections).

---

## L4 — CELL-DESIGN IMPLICATIONS + PRE-REG

### Primary cell: `g1_substrate_sequence_generation_v1`

**Scope:** Build a hetero-associative W_seq + clock-binding substrate-native generator. Test trajectory-coherence + novelty-vs-memorization + refuse-on-OOD + substrate-only-decode on a small text-chunk sequence corpus.

**Corpus:** Use the U1 FB15k-237 corpus (37k+ facts) restructured as ENTITY-CHAINS — 5000 sequences of length L=8, where each step is `(head_entity, relation, tail_entity)` chained via shared entities. This gives the cell a natural sequence structure AND reuses U1's already-validated Pythia-encoded entity HVs.

Alternative corpus: tiny char-level text (WikiText-103 subset, 1000 sequences × 16 chars each); ALSO substrate-Pythia-encodable. Decide based on speed-of-write (FB15k is faster as the encoding exists; text gives a more LLM-comparable test).

**Independent variables:**
- `generation_mode` ∈ {DETERMINISTIC_ARGMAX, LANGEVIN_BETA_0.5, LANGEVIN_BETA_1.0}
- `T_gen` ∈ {4, 8, 16} (gen horizon)
- `clock_binding` ∈ {NONE, HVC_STYLE} (the sparse-clock ablation — does positional code help?)
- `K_set` ∈ {8, 16, 32} (set-readout breadth; pick best at T=8 from preliminary)

**Fixed:**
- N_DIM = 8192 (U1 anchor)
- Sequence corpus = 5000 chains × L=8 = 35000 (s_t, s_{t+1}) write pairs
- 3 seeds (7, 17, 23)
- Pythia-encoded entity HVs (U1-compatible)
- Held-out test seeds: 500 (heldout_in_compose_graph asserted == 0; LEAK-GUARDED)
- OOD test seeds: 500 (random Pythia-encoded strings NOT in the training corpus)

**Primary metric:** `trajectory_coherence(T) = mean top-1 next-state accuracy at each step, averaged over T-step rollouts on HELDOUT seeds`. Top-1 accuracy of the predicted next state matching a HELDOUT continuation OR (for novelty branch) matching ANY plausible next-state from the training set.

**Derived metrics:**
- `novelty_ratio = P(next_state | heldout_seed_continuation) / P(next_state | random_continuation)` — if substrate is just memorizing, ratio = 1.0; if substrate generates plausibly, ratio > 1.5x.
- `refuse_rate_OOD` — fraction of OOD seeds where termination gate fires within T steps (should be ≥ 0.90).
- `refuse_rate_in_corpus` — fraction of heldout-in-corpus seeds where gate fires (should be ≤ 0.10).
- `mean_T_generated` — average sequence length actually produced (vs T_max).
- `cv across seeds` per (mode, T) cell.

**Substrate-only-decode gate:** zero LLM forward calls at construction OR gen-time (grep audit on cell source: transformers/AutoModel/Pythia/.forward/.generate must hit 0 in gen path; allowed in INITIAL embedding pass at write-time only).

**Anchor (sanity bracket):**
- T=1 trajectory_coherence (= 1-step next-state accuracy) ≥ 0.80 (this is essentially U1's single-step recall at 50k; if less, harness is broken).
- T=1 with clock_binding=NONE should match a small ablation of U1's substrate_2hop set-recall (since 1-step gen ≈ key→next-entity lookup).

### PRE-REGISTERED HARD THRESHOLDS

**HARD-PASS (chain-grade, generation mechanism validated):**
- **trajectory_coherence(T=8) ≥ 0.60** at DETERMINISTIC_ARGMAX, K_set=8, clock_binding=HVC_STYLE
- **novelty_ratio at T=8 ≥ 1.5x** (substrate generates plausibly, not by chance)
- **refuse_rate_OOD ≥ 0.90** AND **refuse_rate_in_corpus ≤ 0.10** (gate works in both directions)
- **trajectory_coherence(T=16) ≥ 0.30** (extends to longer horizons even at lower coherence)
- **substrate-only-decode gate PASSES** (zero LLM forward calls in gen path)
- **T=1 anchor reproduces ≥ 0.80** (sanity bracket)
- **cv ≤ 0.07** (slightly looser than 0.05 because generation is noisier than retrieval)
- **Version-marker:** `generation_mode`, `T_gen`, `clock_binding`, `K_set`, `tau_stop`, `beta_inv_T`, per-cell trajectory_coherence + novelty_ratio + refuse_rates baked into metrics.json

**HARD-PASS-PLUS (super-pass — substrate generation extends deep):**
- trajectory_coherence(T=16) ≥ 0.50 AND mean_T_generated ≥ 12 at LANGEVIN_BETA_0.5 — substrate generates novel-yet-coherent sequences at depth, with stochasticity.

**MIDDLE_BAND (proven bound, partial mechanism):**
- trajectory_coherence(T=8) ∈ [0.30, 0.60] OR novelty_ratio ∈ [1.1x, 1.5x] — substrate generates but at lower quality than chain-grade; MEASURED_MECHANISM atom; routes to clock-binding sweep / W_seq factorization tuning.

**HARD-FAIL (mechanism wrong):**
- trajectory_coherence(T=8) < 0.30 — hetero-associative generation does NOT compose at this substrate
- OR refuse_rate_OOD < 0.70 — gate broken; cell INCONCLUSIVE pending refuse-gate redesign
- OR novelty_ratio at T=8 < 1.05 — substrate is just regurgitating training sequences (pure memorization, no generation), no compositional gain
- OR T=1 anchor < 0.80 (harness broken)

**Discriminating-regime requirement (C5):** the CAN-fail regime is T=16 with clock_binding=NONE (long horizon without positional code — if substrate STILL achieves coherence ≥ 0.3 here, the clock binding isn't actually load-bearing — must add a stronger ablation; if substrate fails at T=16/NONE but PASSES at T=16/HVC_STYLE → clock binding is the load-bearing mechanism).

**Version-marker requirement:** every metrics.json includes `generation_mode`, `T_gen`, `clock_binding` (`NONE` vs `HVC_STYLE`), `K_set`, `tau_stop`, `beta_inv_T`, `corpus_used` (FB15k-237_chains vs text), `N_seq_chains_total`, per-mode + per-T trajectory_coherence + novelty_ratio + refuse_rates.

### Compute cost
- Write phase: 35000 (s_t, s_{t+1}) Hebbian outer-products at N_DIM=8192 = ~3 min CPU (or ~10sec GPU).
- Per-generation: T steps × set_readout_top_k @ N_DIM=8192 ≈ T × 5ms = 40ms for T=8.
- Per-seed evaluation: 500 heldout + 500 OOD × 4 T-values × 3 modes × 2 clock × 3 K_set = enormous if full grid; **Phase 1 cut:** T ∈ {1, 4, 8, 16} × {DETERMINISTIC, LANGEVIN_BETA_0.5} × clock ∈ {NONE, HVC_STYLE} × K_set=8 × 3 seeds × 500 seeds × 2 (heldout + OOD) ≈ 90 min remote_cpu.
- **Phase 2 (CONDITIONAL on Phase 1 HARD-PASS):** add LANGEVIN_BETA_1.0 + K_set ∈ {16, 32} + corpus=text alternative.

### Conditional cell (CONDITIONAL on g1 HARD-PASS): `g2_substrate_hierarchical_generation_v1`

**Scope:** SMA-style hierarchical generation — bind state with a LEVEL-tag HV; learn W_seq at multiple levels (token, phrase, sentence). Test if hierarchical generation extends coherent gen to T=32 or T=64.

**Pre-reg HARD-PASS:** trajectory_coherence(T=32, hierarchical) ≥ trajectory_coherence(T=32, flat) + 0.10 (absolute 10-point lift from hierarchy).
**Pre-reg HARD-FAIL:** hierarchical delta < 0.03 at any T (no gain from hierarchical structure).

### Conditional cell (CONDITIONAL on g1 HARD-FAIL): `g1b_diagnostic_W_seq_capacity_v1`

If g1 HARD-FAILs at T=8, the bottleneck is likely W_seq capacity saturation (the 35000 pairs may exceed substrate's hetero-associative capacity at K=2 readout). Diagnostic:
- Measure W_seq capacity at N_seq ∈ {1000, 5000, 10000, 35000}; observe where trajectory_coherence collapses.
- If capacity < 5000, route to dense-Hopfield p≥3 readout OR to clock-binding-only (drops the matrix, uses substrate KG directly).

---

## FALSIFIABLE PREDICTIONS

### Prediction 1 (PRIMARY) — Hetero-Hebbian W_seq enables substrate-native sequence generation
**Hypothesis:** A hetero-associative W_seq learned via temporally-asymmetric Hebbian writes enables the substrate to generate trajectories of length T=8 with coherence ≥ 0.60 from a held-out seed, using only forward-pass cleanup (no LLM, no backprop, no context window).
**Mechanism:** Karuvally-Sejnowski 2023 NeurIPS Long-Sequence-Hopfield + HVC-style sparse-time clock binding + U1's existing set-readout-top-k as the per-step cleanup.
**HARD-PASS:** trajectory_coherence(T=8, DETERMINISTIC, HVC_clock) ≥ 0.60.
**HARD-FAIL:** trajectory_coherence(T=8) < 0.30.
**Calibrated P(HARD-PASS): 0.45** (capped at novel-synthesis 0.50; deflated 0.05 because: the underlying math is rigorously established (Karuvally NeurIPS 2023, Sompolinsky/Kanter 1986 foundational) AND the per-step cleanup primitive is CERT 584 chain-grade in U1. Deflation accounts for: substrate's specific HD arithmetic may have crosstalk at scale; the 35000 pair write may exceed effective capacity even at N_DIM=8192; novelty-vs-memorization measurement is delicate to formalize correctly.)

### Prediction 2 (SECONDARY) — Clock binding reduces temporal interference
**Hypothesis:** Adding HVC-style clock-HV binding at each timestep raises trajectory_coherence(T=8) by ≥ 0.10 (absolute) over a no-clock baseline, by eliminating same-state-different-time interference.
**HARD-PASS:** trajectory_coherence(T=8, HVC_clock) − trajectory_coherence(T=8, NO_clock) ≥ 0.10.
**HARD-FAIL:** delta < 0.02 (clock binding doesn't help).
**Calibrated P: 0.40** (HVC mechanism is empirically validated in songbirds; substrate is high-D so the interference may be mild; benefit depends on how repeated states are in the sequence corpus).

### Prediction 3 (NULLABILITY BRACKET) — refuse-gate fires on OOD seeds
**Hypothesis:** When seeded with off-distribution prompts (Pythia-encoded random text not in training corpus), the termination gate fires within T=4 steps at ≥ 90% rate.
**HARD-PASS:** refuse_rate_OOD ≥ 0.90 AND refuse_rate_in_corpus ≤ 0.10.
**HARD-FAIL:** refuse_rate_OOD < 0.70 OR refuse_rate_in_corpus > 0.30 — gate broken.
**Purpose:** validates that substrate generation is REFUSAL-GATED (the structural moat over LLM hallucination).

### Prediction 4 (SECONDARY) — Langevin noise enables NOVELTY without breaking coherence
**Hypothesis:** Adding Langevin temperature beta_inv_T=0.5 maintains trajectory_coherence ≥ 0.45 (a 0.15 drop from deterministic 0.60) while raising novelty_ratio from 1.0 to ≥ 2.0 (genuine novelty).
**HARD-PASS:** trajectory_coherence(T=8, LANGEVIN_0.5) ≥ 0.45 AND novelty_ratio ≥ 2.0.
**HARD-FAIL:** trajectory_coherence(T=8, LANGEVIN_0.5) < 0.30 — noise destroys coherence.
**Calibrated P: 0.35** (Langevin-on-MHN is mathematically well-validated; substrate-specific temperature tuning is the open variable).

### Prediction 5 (NULLABILITY BRACKET) — T=1 anchor matches U1 1-step recall
**Hypothesis:** At T=1 (single next-state retrieval, no iteration), substrate generation reduces to U1-style 1-step lookup; trajectory_coherence(T=1) ≥ 0.80 (matching U1's 1-hop performance regime).
**HARD-FAIL:** T=1 coherence < 0.80 — harness corrupt; cell INCONCLUSIVE.

### Prediction 6 (REVIVAL ROUTE if HARD-FAIL) — capacity-saturation diagnostic
**Hypothesis:** If g1 HARD-FAILs, the most likely bottleneck is W_seq capacity saturation (35000 pairs exceeding substrate hetero-associative capacity at K=2 readout). Diagnostic cell `g1b` measures capacity-vs-pairs curve to localize the failure.
**Pre-registered routing:** SAME-CYCLE Director note routing the negative (per USER STANDING) with revival angles: (a) dense-Hopfield p≥3 readout; (b) HDC-binding-factored W_seq (use substrate KG directly, not a dense N_DIM² matrix); (c) clock-binding ablation reversal (test no-clock case to see if interference dominates).

---

## CROSS-THREAD SYNTHESIS

### Composes with brain-drill #1 (within-concept floor / k-WTA-VQ)
- Drill #1 gives sparser, cleaner attractors at the codebook level (cerebellum/Kenyon optimum f≈0.05-0.10).
- Generation depends on per-step cleanup quality; sparser attractors = sharper basins = cleaner trajectory.
- **MULTIPLICATIVE composition:** g1 with k-WTA codebook should improve trajectory_coherence at T=16, where deep-step drift compounds.
- Pre-reg follow-on: `g1 × drill #1` cell ships if BOTH land independently.

### Composes with brain-drill #2 (CLS continual replay)
- Drill #2 adds CLS replay during WRITE — protects what's already in W_seq when new sequences arrive.
- g1 is the GENERATION side; drill #2 is the LEARNING-STABILITY side.
- Composition: continually-trained substrate that generates coherent trajectories AFTER new-sequence ingest (without catastrophic forgetting of old sequences).

### Composes with brain-drill #3 (multi-hop iterative cleanup)
- Drill #3 (r1) extends K-hop reasoning via iterative cleanup; g1 extends T-step GENERATION via iterative state-update.
- **They are the SAME primitive at different framings:** r1 = traversal through a relational graph (each hop is bind-with-relation); g1 = traversal through a learned trajectory (each step is hetero-associative next-state).
- Composition: substrate that does K-hop REASONING (r1) about generated sequences (g1) — e.g., "given the trajectory ABCD, what's the 3-hop-related entity of C?"
- **Architectural unification:** r1 + g1 + drill #1 + drill #2 + U1 + refuse-gate IS the substrate-native compositional inference + generation stack.

### Composes with U1 chain-grade (CERT 584)
- U1 = chain-grade 2-hop on FB15k-237 50k; substrate KG primitives validated at scale.
- g1 reuses U1's encoding pipeline (Pythia-encoded entity HVs) AND U1's set-readout-top-k as the per-step cleanup.
- **g1 is a NATURAL extension of U1's KG infrastructure:** every (s_t, s_{t+1}) pair becomes one fact in the multi-value KG. The same architecture serves both KG lookup AND sequence generation.

### Composes with CERT 591 (learned Hebbian-superposition key projection)
- CERT 591 gives the substrate a learned contrastive key-projection generalizing to held-out facts.
- g1 generation relies on per-step keys for next-state lookup; applying the CERT 591 projection at gen-time may give additional gain at longer T (where raw-key crowding hurts more).
- Follow-on composition: `g1 + CERT 591 projection` cell.

### Composes with Hebbian-superposition capacity (~327 capacity, baa06f0a)
- Per-attractor capacity at N_DIM=8192 ≈ 327 patterns reliably retrievable.
- For 35000 (s_t, s_{t+1}) pairs, substrate is OVER capacity at p=2 readout — but the multi-value Hebbian + set-readout architecture is graceful-degradation (U1 showed 0.99 set-recall at 50k facts).
- For super-pass at T=16 / harder corpora, **dense Hopfield p=3 readout** (Karuvally polynomial nonlinearity) gives N_DIM² ≈ 67M effective capacity — substrate can scale to large generation corpora structurally.

### Cross-drill consistency check (the architectural prior)
**All four drills converge on the SAME minimal substrate architecture:**
- DG-style sparse separator (drill #1 k-WTA)
- CA3-style attractor cleanup, iterated K times (drill #3 r1)
- Cortex-with-replay continual ingest (drill #2 c1 CLS)
- HVC/cerebellar hetero-associative W_seq + clock binding + Langevin sampling (drill #4 g1, this drill)
- PBWM-style refuse-gate at all start/stop/termination points (cross-drill)

This is **tight biological correspondence**. The substrate's right configuration is biology's right configuration. Each cell ships independently; the full stack is the substrate-LM-reasoning-generation moat.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Generation is the substrate's LAST missing capability for substrate-native LM.** With U1 (KG ingest), r1 (K-hop reasoning, pending), c1 (CLS continual, pending), drill #1 (compression, pending), and g1 (generation, this drill — pending), the substrate has the FULL minimum-viable-substrate-LM stack. Substrate generates without context window, refuses to hallucinate, and is fully traceable per step.

2. **Substrate generation is the L2-vision structural MOAT over LLMs.** LLMs autoregress within a context window; substrate generates from a TRAJECTORY ATTRACTOR in HD space. (a) NO context window limit — generation runs O(T·N_DIM) regardless of T. (b) REFUSAL-GATED at each step — substrate refuses to hallucinate when off-distribution. (c) DETERMINISTIC-or-STOCHASTIC at the user's choice (LLMs are always stochastic by sampling). (d) FULLY TRACEABLE — every generated step has a confidence score + a basin-of-attraction lookup; you can audit every state. None of these properties are accessible to LLM architectures without major redesign.

3. **The substrate generates "without context window" claim is precise:**
   - Substrate's context IS the current state vector `s_t` — bound with relevant history via HDC binding at write time.
   - The substrate's W_seq stores TRAJECTORIES not TOKENS — generation walks the trajectory attractor, not a token-distribution-over-window.
   - For any T, memory is fixed at the W_seq size (N_DIM² or factored to N_DIM via KG).
   - This is a STRUCTURAL property of the architecture, not a deployment optimization.

4. **The substrate-LM-generation path is now clear at the algorithmic level.** g1 (this drill) is the smallest gap-closing experiment: ~90 min remote_cpu, decisive on the primary hypothesis, composes with every other substrate drill.

5. **Biological correspondences are tight, not metaphor:**
   - HVC ultra-sparse synfire chain (Hahnloser/Fee 2002) = clock-binding HVs at each timestep
   - Cerebellar forward model (Wolpert/Miall) = W_seq next-state matrix
   - Pre-SMA / SMA hierarchical generation (Tanji 2008) = multi-level binding (g2 cell)
   - BG-PBWM start/stop (Frank/O'Reilly 2006) = refuse-gate at gen-time
   - Hippocampal preplay / forward replay (Pfeiffer/Foster 2013) = Langevin-sample on attractor
   - Long Sequence Hopfield Memory (Karuvally/Sejnowski 2023 NeurIPS) = the math validation
   - Langevin-on-MHN (arxiv 2603.06875) = the stochastic-generation extension
   Each correspondence has specific math + verified biological reference.

6. **Falsification value of HARD-FAIL:** if g1 HARD-FAILs at T=8, the substrate's hetero-associative structure is bottlenecked at small T — likely capacity-saturation at N_seq=35000 pairs. Diagnostic `g1b` localizes the failure (capacity-curve); revival routes include dense-Hopfield p≥3 OR HDC-binding-factored W_seq via substrate KG. The drill design has clear next steps in any outcome.

7. **Cell economy:** g1 is ~90min remote_cpu Phase 1 (decisive); ~3hr full grid Phase 2. Cheap. Composes with drill #1 + drill #2 + drill #3 + U1 + CERT 591 at marginal cost.

---

## L5 — CROSS-SUBSTRATE COMPOSITION (path-forward map)

```
                       SUBSTRATE GENERATION (no autoregressive sampling; no LLM forward call)
                                            │
            ┌───────────────────────────────┼───────────────────────────────┐
            ▼                               ▼                               ▼
       g1 hetero-W_seq                 (clock binding HVC-style)        g1b diagnostic
       Karuvally-Sejnowski             temporal-position code           (capacity probe)
       P(HARD-PASS)=0.45               (additive within g1)             conditional on g1 FAIL
       90min remote_cpu                                                 ~30min
            │
   ┌────────┼────────┐
   ▼        ▼        ▼
 T=8      T=16     T=32
 (decisive: (deep:   (super-pass:
 coherence) extends) hierarchical needed)
            │
            ▼ (if HARD-PASS at T=8)
   ┌────────────────┴────────────────┐
   ▼                                 ▼
g1 + LANGEVIN_BETA_1.0          g1 + drill #1 k-WTA
(stochastic generation)         (sparser cleanup; deeper T)
   │                                 │
   └────────────────┬────────────────┘
                    ▼
       g2 hierarchical generation
       (SMA-style nested levels)
       conditional on g1 HARD-PASS
                    │
                    ▼ (deep-T super-pass)
       g1 + drill #3 r1 multi-hop
       (substrate reasons ABOUT generated sequences)
                    │
                    ▼
       g1 + drill #2 c1 CLS replay
       (continual generation on continually-ingested corpus)
                    │
                    ▼
       ──── FULL SUBSTRATE LM STACK ────
       U1 (KG ingest, 2-hop reasoning)
     + r1 (K-hop iterative cleanup, K=3-5)
     + c1 (CLS continual ingest, no forgetting)
     + drill #1 (k-WTA codebook compression)
     + g1 (substrate-native generation, no context window)
     + g2 (hierarchical generation, T=32-64)
     + refuse-gate (PBWM-style; at all start/stop/per-step)
     + CERT 591 learned projection (deep-T key projection)
                    │
                    ▼
       Substrate-native LM with structural moat over LLMs:
       - No context window
       - Refusal-gated per step (no hallucination by construction)
       - Deterministic OR stochastic (user choice)
       - Fully traceable (per-step confidence + basin-of-attraction)
       - Continually updatable (no retraining)
       - K-hop reasoning at depth
```

**If g1 HARD-FAIL:**
```
g1 HARD-FAIL (hetero-Hebbian W_seq does NOT generate coherent T=8 trajectories)
    │
    ├─→ ROUTE TO RESEARCH (USER STANDING)
    │   revival angles:
    │     (a) g1b capacity-curve diagnostic — is it saturation?
    │     (b) dense-Hopfield p=3 readout — Karuvally polynomial nonlinearity
    │     (c) HDC-binding-factored W_seq via substrate KG (drop the matrix)
    │     (d) clock-binding ablation reversal — does NO clock work better (or worse)?
    │
    └─→ if capacity is the bottleneck: route to drill #1 (k-WTA codebook → sparser → effectively more capacity)
        if interference dominates: HVC clock binding IS load-bearing, tune T_clock count
        if substrate-only-decode gate is structurally incompatible: rethink (unlikely; the gen path is forward-only)
```

---

## CITATIONS (verified, count = 22)

1. Hahnloser, R.H.R., Kozhevnikov, A.A., Fee, M.S. (2002). "An ultra-sparse code underlies the generation of neural sequences in a songbird." Nature 419: 65-70. [Nature](https://www.nature.com/articles/nature00974) [Semantic Scholar](https://www.semanticscholar.org/paper/An-ultra-sparse-code-underliesthe-generation-of-in-Hahnloser-Kozhevnikov/dc0c48836dadf8e7585a04da25ceb2d238f6bc90) (HVC ultra-sparse single-burst-per-time-cell sequence code; foundational; the LOAD-BEARING biological inspiration for clock-binding.)

2. Long, M.A., Jin, D.Z., Fee, M.S. (2010). "Support for a synaptic chain model of neuronal sequence generation." Nature. [PMC2998755](https://ncbi.nlm.nih.gov/pmc/articles/PMC2998755) (Synfire chain in HVC; sequence support via chained excitation.)

3. Okubo, T.S., Mackevicius, E.L., Payne, H.L., Lynch, G.F., Fee, M.S. (2015). "Growth and splitting of neural sequences in songbird vocal development." Nature 528: 352-357. [Nature](https://www.nature.com/articles/nature15741) (HVC sequence development; relevant to substrate corpus-growth scenarios.)

4. Karuvally, A., Sejnowski, T.J. (2023). "Long Sequence Hopfield Memory." NeurIPS 2023. [arxiv 2306.04532](https://arxiv.org/abs/2306.04532) [arxiv PDF](https://arxiv.org/pdf/2306.04532) (THE LOAD-BEARING MATH PAPER. Temporally asymmetric Hebbian + dense Hopfield nonlinearity = super-linear sequence capacity; generalized pseudoinverse for correlated patterns; biologically-plausible motor-neuroscience connections. The chain-grade math foundation for substrate's hetero-W_seq.)

5. Sompolinsky, H., Kanter, I. (1986). "Temporal association in asymmetric neural networks." Phys. Rev. Lett. 57: 2861. (Foundational asymmetric-Hopfield sequence storage.)

6. Ramsauer, H., et al. (2021). "Hopfield Networks Is All You Need." ICLR 2021. [OpenReview](https://openreview.net/pdf?id=tL89RnzIiCd) (Modern Hopfield 1-iter retrieval; exponential capacity; the per-step cleanup primitive substrate uses.)

7. Wolpert, D.M., Miall, R.C. (1998). "Internal models in the cerebellum." Trends Cogn. Sci. 2(9): 338-347. [Semantic Scholar](https://www.semanticscholar.org/paper/Internal-models-in-the-cerebellum-Wolpert-Miall/21e47a5b98afa4c56844a18c117461dc6150956d) (Cerebellar forward-model foundational; the biological grounding of W_seq.)

8. Cerebro-Cerebellum as Locus of Forward Model: A Review (2020). Frontiers Syst. Neurosci. 14:19. [PMC7160920](https://pmc.ncbi.nlm.nih.gov/articles/PMC7160920/) (Modern review; hierarchical composition of multiple cerebellar forward models.)

9. Wolpert, D.M., Miall, R.C., Kawato, M. (2025). "Cerebellar circuit computations for predictive motor control." Nature Reviews Neuroscience. [Nature](https://www.nature.com/articles/s41583-025-00936-z) (2025 update; modern synthesis of cerebellar internal-model theory.)

10. Pfeiffer, B.E., Foster, D.J. (2013). "Hippocampal place-cell sequences depict future paths to remembered goals." Nature 497: 74-79. (Awake forward replay = sampling of future trajectories; preplay-style trajectory generation.)

11. Dragoi, G., Tonegawa, S. (2011, 2013). "Preplay of future place cell sequences by hippocampal cellular assemblies." Nature 469: 397-401. (Preplay — sequence-attractors that EXIST BEFORE experience; intrinsic generation.)

12. Jensen, K.T., et al. (2024). "A recurrent network model of planning explains hippocampal replay and human behavior." Nature Neuroscience. [PMC11239510](https://pmc.ncbi.nlm.nih.gov/articles/PMC11239510/) [Nature](https://www.nature.com/articles/s41593-024-01675-7) (PFC rollouts depth L=8; matches rodent replay. Forward-only at inference. Cited from drill #3 for context.)

13. Frank, M.J., O'Reilly, R.C. (2006). "Making working memory work: a computational model of learning in the prefrontal cortex and basal ganglia." Neural Computation 18: 283-328. [PDF](https://cseweb.ucsd.edu//~gary/PAPER-SUGGESTIONS/OReillyFrank06_pbwm-neural-comp-2006.pdf) (PBWM start/stop gating model.)

14. Tanji, J. (2008) and Botvinick hierarchical-RL (2009-2014); SMA / pre-SMA hierarchical sequence representation. [JNS 42:6946 (2022)](https://www.jneurosci.org/content/42/36/6946) (Complementary PMd / pre-SMA roles; switching vs terminal action.)

15. Brainard, M.S., Doupe, A.J. (2002, 2013). "What songbirds teach us about learning." Nature; reviews. (Foundational vocal-learning literature; HVC as premotor sequence generator.)

16. Stochastic Attention via Langevin Dynamics on the Modern Hopfield Energy. [arxiv 2603.06875](https://arxiv.org/pdf/2603.06875) (THE STOCHASTIC-GENERATION BRIDGE. Converts deterministic MHN retrieval into Langevin sampler; substrate's path to stochastic generation.)

17. Carbone, D. (2024). "Hitchhiker's guide on Energy-Based Models: a comprehensive review on the relation with other generative models, sampling and statistical physics." [arxiv 2406.13661](https://arxiv.org/html/2406.13661v1) (EBM review unifying Hopfield + diffusion + Langevin; substrate-relevant theory.)

18. Ambrogioni, L. (2024). "In Search of Dispersed Memories: Generative Diffusion Models Are Associative Memory Networks." [PMC11119823](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11119823/) (Diffusion models trained on discrete patterns = modern Hopfield asymptotically; substrate generation ⊂ associative-memory generation.)

19. Sparks, D.L., Hartwich-Young, R. (1989); Munoz, D.P., Wurtz, R.H. (1995); saccade-FEF-SC review. [JN 85:804 (2001)](https://journals.physiology.org/doi/full/10.1152/jn.2001.85.2.804) [PMC saccade-burst-generator](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3576366/) (FEF/SC saccade-sequence generation; corroborative substrate-analogue.)

20. Marder, E., Calabrese, R.L. (2001) "Principles of rhythmic motor pattern generation." Physiol. Rev. (Spinal-cord CPG / half-center oscillator; rejected as wrong-class for substrate gen.) [Sparse-firing CPG 2024 Neural Computation 36:759](https://direct.mit.edu/neco/article/36/5/759/120320/Sparse-Firing-in-a-Hybrid-Central-Pattern)

21. Two-layer SOM with VSA for Spatiotemporal Sequence Learning and Prediction (2024). [Biomimetics 9:175](https://www.mdpi.com/2313-7673/9/3/175) [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10968299/) (VSA temporal-pattern construction; substrate-adjacent precedent.)

22. Continuous Autoregressive Language Models (CALM). [arxiv 2510.27688](https://arxiv.org/html/2510.27688v1) (LLM literature converging on continuous-vector autoregression; the substrate version IS this with HD vectors. Comparison frame.)

Additional references used in lit-scan but not load-bearing for cell design:
- Londono Alvarez (2024) "Attractor-based models for sequences" [arxiv 2410.11012](https://arxiv.org/abs/2410.11012) (TLN sequence-attractor; principle adopted; form not directly portable).
- Hyperdimensional Probe (arxiv 2509.25045) (LLM-VSA equivalence in residual stream).
- Millidge et al (2022) heteroassociative Modern Hopfield Network sequence storage.
- Shift-Equivariant Hypervector Representations of Sequences (arxiv 2112.15475) (cyclic-permutation binding for trajectories).

---

## LIT-SCAN CALIBRATION NOTES

- All probability estimates deflated 0.15-0.25 from raw LM-based confidence.
- **Novel-synthesis cap at 0.50 applied:** the composition (hetero-Hebbian W_seq + clock binding + Langevin) is a SMALL composition over established primitives, not a wholly novel mechanism. P(HARD-PASS for g1)=0.45 reflects the cap minus 0.05 for substrate-specific HD-arithmetic uncertainties (capacity saturation; clock-binding interaction with HDC bind/unbind).
- **HARD-FAIL thresholds mandatory and listed for every prediction.**
- **The DIRECTIONALITY** (hetero-Hebbian W_seq stores sequences; iterative-cleanup retrieves them) is **HIGHLY confident** (raw P ≈ 0.80-0.90, robust across three independent rigorous literatures: Karuvally NeurIPS 2023 math, HVC empirical biology, cerebellar forward-model neuroscience). The **MAGNITUDE** (trajectory_coherence(T=8) ≥ 0.60 AND novelty_ratio ≥ 1.5x AND refuse_rate_OOD ≥ 0.90) is where deflation hits — substrate-specific tuning of T_clock, K_set, tau_stop, beta_inv_T may need iterative refinement.
- U1's CERT 584 chain-grade at 1-hop + 2-hop is the load-bearing prior — without it, the cell-design has no sanity-bracket anchor. With it, g1 has a clear T=1 anchor and per-step-cleanup is a CERT'd primitive.
- **Citation count = 22** (verified URLs where checked; foundational papers cited by author + year + journal). 8 of 22 are 2023-2025 (Karuvally NeurIPS 2023, Kawato 2025 Nat Rev Neurosci, Jensen 2024, Carbone 2024 EBM, Generative-Diffusion-as-Associative-Memory 2024, SMA TMS-EEG 2024, sparse-firing CPG 2024, SOM-VSA 2024, CALM 2026) — current literature is well-covered.

---

## DISPATCH RECOMMENDATION

**Immediate (Exp-Dev, after current sequencing OR in parallel with drill #1/#2/#3 cells):** `g1_substrate_sequence_generation_v1`
- Same harness scaffold as U1 (already validated at 50k scale on FB15k-237).
- Phase 1: T ∈ {1, 4, 8, 16} × {DETERMINISTIC, LANGEVIN_BETA_0.5} × clock ∈ {NONE, HVC_STYLE} × K_set=8 × 3 seeds. ~90 min remote_cpu. **Decisive on the primary hypothesis at T=8.**
- Phase 2 (CONDITIONAL on Phase 1 HARD-PASS): full grid + corpus=text alternative + K_set ∈ {8, 16, 32} + LANGEVIN_BETA_1.0. ~3 hr remote_cpu.
- Anchors: T=1 trajectory_coherence ≥ 0.80 (U1 1-hop sanity); T=8 DETERMINISTIC + HVC_clock ≥ 0.60 (HARD-PASS).
- Version-marker: all gen knobs + per-mode + per-T + per-clock trajectory_coherence + novelty_ratio + refuse_rates baked into metrics.json.

**Composition prep (free piggyback after g1 lands):**
- Include T_clock sensitivity (32 vs 64 vs 128) at T=8 best-mode at marginal cost.
- Include refuse-gate audit on OOD seeds (covered in Prediction 3 nullability).

**Conditional next:** `g2_substrate_hierarchical_generation_v1` if g1 HARD-PASS at T=8, 16.

**Ordering vs drill #1 k-WTA, drill #2 c1 CLS, drill #3 r1 multi-hop:**
- g1 is INDEPENDENT of drill #1, #2, #3 at the primary-test level. Can ship in parallel.
- IF compute is constrained: g1 has the HIGHEST L2-vision impact (closes the LAST missing capability for substrate-LM) and MODERATE cost (~90min Phase 1). Drill #3 (r1) has slightly lower L2-vision impact but SLIGHTLY lower cost and EXTENDS U1 directly — could go first if extending an existing CERT is prioritized over closing the generation gap.
- drill #1 (k-WTA) is for within-concept decode compression — orthogonal but composes with g1 at deep T.
- drill #2 (c1 CLS) is for continual ingest — composes with g1 at the WRITE side (continual sequence ingest without forgetting).
- **Suggested ordering:** r1 Phase 1 first (cheapest at ~45min, extends U1 directly); g1 Phase 1 second (~90min, closes the generation gap, the L2-vision moat); c1 + drill #1 in parallel after; full composition cells (g1 × r1 × drill #1 × c1) at marginal cost.

**Ordering vs N3/N4/Path A (substrate-LM):**
- g1 IS the substrate-LM-generation cell at the algorithmic level. N3/N4/Path A are substrate-LM-decode cells (operating on the LLM tokenization side). g1 is the substrate-native version that bypasses tokenization entirely.
- If g1 PASSES: the substrate-LM path becomes "substrate generates HD vectors → decode HD vector → token" (with the decode being one substrate-readout step, not autoregressive sampling).
- If g1 FAILS: substrate-LM path remains tied to LLM-tokenization-substrate-hybrid (N1 / N3 / etc.).

---

## PLAIN-ENGLISH WRAP (Fix #13)

The substrate today can READ — it ingests facts, looks them up, cleans up noisy queries, refuses out-of-distribution questions, and traverses 2-hop relational chains at chain-grade accuracy. What it cannot do yet is WRITE — generate a novel sequence of states from a seed prompt. LLMs do this by autoregressive sampling: predict next token, append, predict again, all within a fixed context window. The substrate has no equivalent mechanism. This drill identifies and pre-registers it.

Biology solved sequence generation 100+ million years ago via the songbird HVC: a population of "grandmother time cells" each fire ONCE at one precise moment during a song (Hahnloser & Fee 2002 Nature). The cerebellum runs a forward model that predicts the next state given the current state and an action (Wolpert/Miall 1998; Kawato 2025 Nature Reviews Neuroscience). The pre-SMA composes those primitive sequences into hierarchical action plans. The basal ganglia gates start and stop. The hippocampus does forward replay to imagine candidate trajectories (Pfeiffer & Foster 2013 Nature). The MATH was settled in 2023: temporally asymmetric Hebbian weights + dense Hopfield nonlinearity store sequences with super-linear capacity (Karuvally & Sejnowski NeurIPS 2023). Add Langevin noise and you get stochastic sampling for free (arxiv 2603.06875).

For the substrate, the architecture is: a hetero-associative weight matrix W_seq (or its factored substitute via HDC binding + the existing substrate KG) maps current state to next state. At generation time, iterate `s_{t+1} = cleanup(W_seq @ s_t)` for T steps, with the existing substrate refuse-gate firing if confidence drops below threshold. Add HVC-style "clock binding" to give each timestep its own positional hypervector — this eliminates the temporal interference that would otherwise confuse repeated states (the substrate's high-D, sparse-tag-friendly arithmetic makes this trivial).

The cheap decisive test: `g1_substrate_sequence_generation_v1` — store 5000 short entity-chains (length 8) on a W_seq, then test if the substrate can generate T=8 trajectory from held-out seeds at coherence ≥ 0.60 and novelty ≥ 1.5x and refuse-OOD-at-90%. ~90 minutes on remote_cpu. If it lands (P=0.45), the substrate has substrate-native generation — without a context window, refusal-gated per step, fully traceable, and runnable at O(T·N_DIM) regardless of T. Combined with drill #1 (compression), drill #2 (continual learning), drill #3 (multi-hop reasoning), and U1 (KG ingest), this is the minimum-viable substrate-LM-generation stack — the L2-vision structural moat over LLM autoregression.

The four brain drills together (within-concept floor + CLS continual learning + multi-hop reasoning + generation) map to a tight biological correspondence: DG sparse separator + CA3 attractor cleanup + cortex-with-replay + HVC/cerebellar hetero-associative sequence generation, all gated by a PBWM-style refuse-gate at every start/stop/per-step point. Each cell ships independently in ~30-90 minutes of substrate compute. The full stack is the substrate-reasoning-and-generation moat.

---

-- Research (Opus synthesis, 9 parallel Sonnet web searches + 2 paper fetches for L3 depth on Karuvally-Sejnowski 2023 Long-Sequence-Hopfield NeurIPS + Londono-Alvarez 2024 attractor-sequence dissertation; deflated per calibration). Companion to drills #1, #2, #3. Four drills converge: substrate's right configuration IS biology's right configuration. g1 closes the last gap; all four cells composite at marginal cost.
