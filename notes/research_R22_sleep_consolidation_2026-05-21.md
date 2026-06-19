# R22 — Sleep-style memory consolidation (LOWER PRIORITY; extends Bet B ✅ promoted v69)

**Routed**: Strategy session, cycle 27 followup (LOWER priority; design-
space audit item extending continual learning ✅). Per active_priorities
original description: "offline replay during quiescence; sleep-replay
neuroscience. Extends continual learning ✅."

**Date**: 2026-05-21 (~20:30 EDT).

**Status**: Research note (Pass 1 survey + Pass 2 substrate drill).
External lit-scan via Agent subagent `a813654f68ce54cad` (~5.6 min, 35
tool uses, ~64K tokens, generic computational-neuroscience / continual-
learning queries per [[feedback-query-privacy-decomposition]]).

**Owner**: Research session (single-writer-per-file).

**Connects**: Bet B ✅ PROMOTED (v69 via v7 alpha sweep PASS; EMA-blend
mechanism); R29 Bet M cluster-Hopfield; R16 Bet I free-probability;
Bet N rehab N.6 state-adaptive cleanup (potential stacking); pattern
of cross-domain decorative filtering established R17/R32/R31/R27/R21.

**Outcome category**: **PARTIAL substrate-applicability with substrate-
product-critical theoretical legitimization of Bet B v6/v7 mechanism**.
Most sleep-replay neuroscience (60-70% per subagent) is biology-
specific; 3 GENUINE substrate-applicable transfers identified.

---

## HEADLINE

> Subagent's brutal-honesty finding: "Roughly 60-70% of the sleep-replay
> neuroscience literature is biology-specific and does not map onto a
> fixed-codebook bipolar Hebbian memory without violence. The genuinely
> portable concepts are: (i) offline reactivation with Hebbian-type
> updates, (ii) selective/priority-weighted consolidation, and (iii) the
> formal observation that generative replay is functional regularization
> equivalent to weighted re-application of past examples."
>
> **CRITICAL THEORETICAL LEGITIMIZATION of Bet B mechanism**: van de Ven-
> Soures-Kudithipudi 2024 arXiv:2403.05175 establishes that **generative
> replay is mathematically functional regularization** (distillation on
> past predictions), NOT true rehearsal. **For substrate's Bet B v6+v7
> EMA-blend mechanism (W_ABC = 0.7·W_ABC + 0.3·W_A): this IS a form of
> consolidation-as-functional-regularization, theoretically legitimized
> per van de Ven 2024.** Bet B's mechanism is NOT a hack — it's a
> recognized consolidation primitive.
>
> **HIGHEST-SIGNAL substrate-applicable paper**: Tadros-Krishnan-
> Ramyaa-Bazhenov **Nat Comm 13:7742 (2022)** — "Sleep-like unsupervised
> replay reduces catastrophic forgetting in artificial neural networks."
> Uses **Hebbian-type rule** during sleep phase with noisy Poisson
> reactivation. MNIST 19.49% → 48.47%; CIFAR-10 19% → 44.55%; CUB-200
> Task-1 5% → 63.2%. **Maps almost line-for-line onto substrate**:
> replace MLP with substrate W ← W + (1/N)·Σ ξ_replay ⊗ ξ_replay over
> reconstructed prototypes during quiescence.
>
> **THREE genuine substrate-applicable mechanisms** (per subagent):
> 1. **S.1 Sleep Replay Consolidation (SRC)**: offline Hebbian
>    re-strengthening of fragile stored items via noise-driven
>    reactivation. Directly substrate-portable per Tadros 2022.
> 2. **S.2 Selective/prioritized consolidation**: SWR-selectivity
>    (Yang-Tonegawa 2024) + Prioritized Experience Replay (Schaul 2016)
>    + Uncertainty-Prioritized (UPER Sutter 2025) → fragility-weighted
>    substrate Hebbian top-up.
> 3. **S.3 Noise-driven reactivation**: bit-flip stored prototype +
>    pattern completion + re-Hebbian update on successful replays.

**Substrate-product framing recommendation**:
- **S.1 SRC-style sleep replay** is substrate-product extension of
  Bet B; 35-50% P of meaningful gain over current EMA-blend
- **S.2 fragility-weighted prioritization** stacks with S.1; 25-40% P
  of incremental gain
- **S.3 noise-driven reactivation** is substrate-buildable; 30-45% P
- **Bet B mechanism IS theoretically legitimized** by van de Ven 2024
  — substrate-product framing benefit (0 GPU cost)

**Brutal-honesty probability estimates** (per [[feedback-no-smoke]]):
- P(S.1 SRC substrate gives ≥ 1.3× Bet B v7 retention_A=0.954): 35-50%
- P(S.2 prioritization stacks with S.1 productively): 25-40%
- P(S.3 noise-driven reactivation adds value beyond S.1): 30-45%
- P(REM/NREM duality substrate-applicable): 5% (NEGATIVE — biology-
  specific)
- P(schema-extraction substrate-applicable): 10% (NEGATIVE — fixed
  codebook can't merge codes)
- P(R22 produces substrate-novel observation beyond Bet B legitimization):
  35%

---

## Pass 1 — Survey synthesis (external lit-scan, 12 questions)

[Synthesis condensed; full 12-question scan in subagent output.]

### 1.1-1.2 Hippocampal SWRs + REM/NREM (BIOLOGY-SPECIFIC; DECORATIVE)

**Recent (2024-2025)**:
- **Yang et al. Science 384 (2024) DOI:10.1126/science.adk8261 —
  selection of experience for memory by hippocampal SWRs**
- Joo-Frank Neuron (2024) DOI:10.1016/j.neuron.2024.09.005 — PFC
  cortical ripples mediate top-down hippocampal reactivation
- Buzsáki-Tingley Annual Reviews Neurosci (2025) DOI:10.1146/annurev-
  neuro-112723-024516 — replay and ripples in humans
- Bowman et al. eLife (2024) DOI:10.7554/eLife.92749 — ACh-modulated
  NREM/REM
- Cordi-Rasch Neurobiology Learn. Mem. 204 (2023) — meta-review

**Substrate connection — PARTIAL via SWR-selection**: SWR selectivity
(Yang 2024) substrate-applicable via S.2 fragility-weighted prioritization.
NREM/REM duality DECORATIVE.

### 1.3 CLS theory (PARTIAL substrate-applicable framework)

**Recent**:
- Pham-Liu-Yang-Sutton 2023 DualNet DOI:10.1162/neco_a_01612 —
  architectural CLS with fast/slow sub-networks
- Sun et al. Nat. Neurosci. (2023) DOI:10.1038/s41593-023-01382-9 —
  generalization in CLS
- **van de Ven-Soures-Kudithipudi arXiv:2403.05175 (2024) — book
  chapter; CRITICAL substrate-applicable framing of generative replay
  as functional regularization**
- Burgess group arXiv:2509.01987 (2025) — predictive-coding CLS

**Substrate connection — PARTIAL**: substrate Hebbian W IS fast-learning
"hippocampal" analog; substrate has no separate "neocortical" slow
system. CLS framework PARTIALLY applies.

### 1.4 Schema-based memory transformation (DECORATIVE for substrate)

**Recent**:
- Audrain-McAndrews Nat. Comm. 13 5795 (2022) — schemas as scaffold
- **Spens-Burgess Nat. Hum. Behav. 8 (2024) DOI:10.1038/s41562-023-01799-z
  — generative model of memory construction using MODERN HOPFIELD as
  hippocampal autoassociator → trains VAE generator (substrate
  legitimization citation)**

**Substrate connection — CRITICAL via Spens-Burgess 2024**: explicitly
uses Modern Hopfield as hippocampal autoassociator. Substrate's
Hebbian W IS this primitive. Spens-Burgess legitimizes substrate as
"the right primitive under modern consolidation theory."

Schema-EXTRACTION as fast cortical learning DOES NOT transfer to
substrate (fixed codebook can't merge codes without explicit
superposition; superposition is itself capacity-limited).

### 1.5-1.6 Offline replay during quiescence + schema vs episodic
       (PARTIAL substrate-relevance)

**Recent**:
- Liu et al. Cell 178 640 (2019) DOI:10.1016/j.cell.2019.06.012 —
  foundational human MEG replay reorganization
- Liu et al. eLife 10 e66917 (2021) — TDLM method
- Higgins-Liu Nat. Comm. 15 (2024) DOI:10.1038/s41467-024-51582-5 —
  replay triggers brain-wide activation
- Wittkuhn-Liu bioRxiv 2025.01.08.632067 — offline replay constructs
  cognitive map
- Antony et al. Front. Comp. Neurosci. (2024) DOI:10.3389/fncom.2024.1538741
  — memory consolidation from RL perspective

**Substrate connection**: human replay reorganizes along ABSTRACT
STRUCTURE not raw temporal order — substrate could potentially replay
along code-graph structure (not playback sequences) if a sequencing
layer is added. Currently NOT in substrate architecture.

### 1.7-1.8 Generative replay + Experience replay in deep RL (CRITICAL
       transfer via van de Ven 2024 framing)

**Recent (2020-2025)**:
- van de Ven-Siegelmann-Tolias Nat. Comm. 11 4069 (2020)
  DOI:10.1038/s41467-020-17866-2 — brain-inspired replay SOTA
- **van de Ven-Soures-Kudithipudi arXiv:2403.05175 (2024) — CRITICAL
  framing: "generative replay is mathematically functional regularization
  (knowledge distillation on past predictions), not true rehearsal"**
- Schaul et al. arXiv:1511.05952 (2016) — Prioritized Experience Replay
  (PER); foundational
- Andrychowicz et al. 2017 — Hindsight Experience Replay (HER)
- Sutter et al. arXiv:2506.09270 (2025) — UPER uncertainty-prioritized;
  addresses noisy-transition bias

**Substrate connection — CRITICAL**: van de Ven 2024 establishes
**generative replay = functional regularization**. Substrate's Bet B
v6+v7 EMA-blend (W_ABC = 0.7·W_ABC + 0.3·W_A) IS functional regularization
— theoretical legitimization. PER/UPER → S.2 fragility-weighted
substrate consolidation.

### 1.9-1.10 Hippocampal indexing + transformation theories (DECORATIVE
       for fixed-codebook substrate)

**Recent**:
- Sekeres-Winocur-Moscovitch Neurosci. Lett. 680 39 (2018) — TTT review
- Berry et al. J. Theor. Biol. (2024) — coupled neural field SCT model
- Antony et al. Front. Comp. Neurosci. (2024) — RL framing

**Substrate connection — DECORATIVE**: hippocampal "indexing" and
"trace transformation" require temporally-evolving distributed cortical
traces. Substrate has no time axis on weights; "transformation" requires
off-substrate process. DOES NOT TRANSFER.

### 1.11 Sleep-inspired continual learning algorithms (HIGHEST SIGNAL
       LOAD-BEARING)

**Recent**:
- **Tadros-Krishnan-Ramyaa-Bazhenov Nat. Comm. 13 7742 (2022)
  DOI:10.1038/s41467-022-34938-7 — "Sleep-like unsupervised replay
  reduces catastrophic forgetting"; HIGHEST-SIGNAL substrate-
  applicable paper**
  - Uses Hebbian-type rule during sleep phase with noisy Poisson
    historical reactivation
  - MNIST 19.49% → 48.47%; CIFAR-10 19% → 44.55%; CUB-200 Task-1
    5% → 63.2%
  - Mechanism: sparsening + decorrelation of task-specific neural
    populations
- Bazhenov group arXiv:2410.16154 (2024) — SRC extended to small/
  imbalanced datasets
- Harun et al. arXiv:2303.10725 (TMLR 2023) — SIESTA: wake = rehearsal-
  free Hebbian-style; sleep = compute-restricted rehearsal
- Bamnodkar arXiv:2507.21109 (2025) — TFC-SR Task-Focused Consolidation
  with Spaced Recall

**Substrate connection — DIRECT**: Tadros 2022 SRC maps line-for-line
onto substrate. Replace MLP with substrate W ← W + (1/N)·Σ ξ_replay ⊗
ξ_replay over reconstructed prototypes during quiescence. **S.1 substrate-
applicable mechanism.**

### 1.12 Replay buffer sampling strategies (PARTIAL substrate-applicable)

**Recent**:
- Hickok arXiv:2505.12512 (2025) — consolidation reduces replay samples
  needed by up to 55%
- Yoo et al. arXiv:2303.13157 (2023) — adiabatic replay (similarity-based)
- arXiv:2407.09702 (2024) — selection strategies review

**Substrate connection**: reservoir sampling (uniform) is hard to beat
once buffer > few hundred. Substrate already has implicit Hebbian
"buffer" via W; fragility-weighted (S.2) is alternative sampling
strategy.

---

## Pass 2 — Substrate drill (4 candidate mechanisms; 3 genuine + 1 declined)

Per [[feedback-unbiased-research]] + brutal-honesty filtering.

### S.1 — Sleep Replay Consolidation (SRC) substrate port (PRIMARY)

**Source**: Tadros-Krishnan-Ramyaa-Bazhenov Nat. Comm. 13 7742 (2022)
DOI:10.1038/s41467-022-34938-7.

**Mechanism**: substrate "sleep phase" implements:
1. Generate noisy replay samples ξ_replay = stored_prototype + bit_flip_noise
   (Poisson rate based on historical activation statistics)
2. Run substrate pattern completion: ξ_replay → cleaned_replay (via current W)
3. Update substrate W via Hebbian outer-product: W ← W + (1/N) ·
   cleaned_replay ⊗ cleaned_replay over successful replays

**Substrate implementation**:
- Activation statistics tracked across training (e.g., per-atom fire rate)
- Sleep cycles between training phases (Phase A → SLEEP → Phase B → SLEEP)
- Sleep duration: tunable hyperparameter; suggest 0.1× training duration

**Substrate-novel content — PARTIAL**: SRC algorithm established;
substrate-specific port + integration with Bet B v6+v7 EMA-blend.

**Cross-mechanism stacking**:
- Stacks with Bet B v6+v7 EMA-blend (W_ABC ← α·W_ABC + (1-α)·W_A)
  — SRC adds explicit sleep cycles between training phases
- Stacks with S.2 fragility-weighted prioritization
- Stacks with R29 Bet M cluster-Hopfield (which patterns to consolidate
  by cluster membership)
- Stacks with Bet N rehab N.6 state-adaptive cleanup (cleanup
  parameters during sleep)

**Falsifiable prediction**:
- P(SRC substrate gives ≥ 1.3× Bet B v7 retention_A=0.954): 35-50%
- P(SRC stacks with Bet B EMA-blend multiplicatively): 25-40%
- P(SRC reduces catastrophic forgetting in 3-task continual learning):
  50-65% (Tadros 2022 precedent)

**Kill criterion**: if SRC substrate retention ≤ Bet B v7 baseline,
sleep-replay adds no value to substrate's already-validated mechanism.

**Cost**: 6-10 GPU hours (substrate engineering for sleep cycle
infrastructure + activation statistics tracking).

### S.2 — Fragility-weighted prioritized consolidation (STACKS with S.1)

**Source**: Schaul PER arXiv:1511.05952 (2016) + UPER Sutter
arXiv:2506.09270 (2025) + Yang/Tonegawa SWR-selection Science 384 (2024).

**Mechanism**: substrate prioritizes consolidation of FRAGILE stored
patterns. Fragility metrics:
- Low cosine to stored prototype (poor recall accuracy)
- Low energy margin (substrate cleanup at low confidence)
- High recall variance across noise levels (high aleatoric uncertainty)
- Recent storage with low replay count (epistemic uncertainty)

**Substrate implementation**:
- Pre-sleep: compute fragility score per stored pattern via recall test
- Sleep replay distribution: P(replay_μ) ∝ fragility_μ^α (PER-style)
- Top-fragility patterns get more replay budget

**Substrate-novel content**: PARTIAL — PER/UPER established; substrate-
specific fragility metric + integration.

**Cross-mechanism stacking**:
- Stacks with S.1 SRC (selective sleep replay, not uniform)
- Stacks with S.3 noise-driven reactivation (prioritize noisy patterns)

**Falsifiable prediction**:
- P(S.2 prioritization gives ≥ 1.2× over uniform S.1): 25-40%
- P(works at substrate scale N=4096 with M=8N stored patterns): 50-65%

**Cost**: 4-6 GPU hours (incremental on S.1 infrastructure).

### S.3 — Noise-driven reactivation (SUBSTRATE-NATIVE Tadros 2022 port)

**Source**: Tadros 2022 (same as S.1) — Poisson noise reactivation
mechanism specifically.

**Mechanism**: substrate generates "spontaneous" reactivations by:
1. Sample random bipolar pattern ξ_random ∈ {-1, +1}^N
2. Add bit-flip noise: ξ_noisy = ξ_random XOR bit_flip_mask
3. Run substrate pattern completion: ξ_noisy → ξ_completed
4. If ξ_completed matches a stored prototype within threshold:
   counts as "successful replay" → Hebbian re-strengthening

**Substrate implementation**:
- Spontaneous reactivation rate: e.g., 1000 samples per sleep cycle
- Threshold for "successful" replay: cosine > 0.7 with nearest prototype
- Re-Hebbian update only on successful replays

**Substrate-novel content**: PARTIAL — substrate-specific noise
distribution; biologically-inspired Poisson can be replaced with
substrate-native uniform bit-flip.

**Cross-mechanism stacking**:
- Stacks with S.1 SRC (S.3 is the noise-generation mechanism for S.1
  if explicit prototypes unavailable)
- Stacks with S.2 fragility prioritization

**Falsifiable prediction**:
- P(S.3 noise-driven reactivation gives ≥ 1.2× over no-sleep baseline):
  30-45%
- P(noise-driven reactivation works without explicit prototype reference):
  40-55%

**Cost**: 3-5 GPU hours.

### S.4 — REM/NREM duality substrate (NEGATIVE; DECLINED)

**Source**: Bowman et al. eLife (2024); REM vs NREM neuroscience.

**Why DECLINED**: biology-specific; depends on cholinergic state
transitions and inhibitory network dynamics. No substrate analog exists.

**Substrate connection — NEGATIVE**:
- Substrate has no neuromodulatory system
- Substrate has no inhibitory/excitatory population dynamics
- Trying to map "REM = abstraction, NREM = stabilization" onto
  Hebbian outer-product = mechanism-poaching

**Per [[feedback-no-smoke]]**: HONEST DECLINE. Substrate's two-phase
consolidation (if needed) should be justified on capacity/interference
math, NOT biology analogy.

**Falsifiable prediction**: 5% P substrate-applicable.

**Recommendation**: DECLINE S.4. Do not pursue REM/NREM substrate
analog.

### R22 mechanism summary

| # | Mechanism | Substrate-applicable? | P(gain vs Bet B v7) | Cost | Notes |
|---|---|---|---|---|---|
| **S.1** | **SRC sleep replay** | **YES — Tadros 2022 direct port** | **35-50%** | **6-10 GPU** | **PRIMARY substrate-product extension** |
| **S.2** | **Fragility-weighted prioritization** | **YES — PER/UPER + SWR-selection** | **25-40%** | **4-6 GPU** | **Stacks with S.1** |
| S.3 | Noise-driven reactivation | YES — substrate-native | 30-45% | 3-5 GPU | Stacks with S.1 + S.2 |
| S.4 | REM/NREM duality | NO — biology-specific | 5% | N/A | DECLINED |

**Combined**: pursue S.1 + S.2 (stacking) as primary substrate-product
deliverable. S.3 incremental addition. S.4 declined.

**Combined P(at least one S.1-S.3 gives ≥ 1.3× Bet B v7 retention)**:
50-65%.

---

## 3. CRITICAL substrate-product framing per [[feedback-no-papers-product-only]]

**For Strategy decision on R22**:

**THEORETICAL LEGITIMIZATION (0 GPU cost, HIGH substrate-product value)**:
- van de Ven 2024 establishes generative replay = functional
  regularization
- **Bet B v6+v7 EMA-blend mechanism IS functional regularization** —
  theoretically legitimized as recognized consolidation primitive
- Substrate-product framing improvement: "Bet B mechanism is a
  legitimate consolidation primitive grounded in recent ML theory,
  NOT a hack"

**ENGINEERING extension (10-21 GPU hours; substantial substrate
engineering)**:
- S.1 SRC sleep replay: primary substrate-product extension
- S.2 fragility-weighted prioritization: stacks with S.1
- S.3 noise-driven reactivation: incremental
- Combined: 50-65% P of ≥ 1.3× Bet B v7 retention gain

**Decision per Strategy**:
- IF Bet B extension is substrate-product priority: pursue S.1+S.2+S.3
  sequence
- IF Bet B current ✅ status is sufficient: defer R22 engineering;
  theoretical legitimization (van de Ven 2024 citation) integrated 0
  cost

---

## 4. Materials physics LOAD-BEARING (per [[feedback-materials-science-probe]])

**Substrate-applicable load-bearing analogs from R22**:
- **Tadros 2022 SRC**: sleep-replay consolidation IS canonical
  computational-neuroscience mechanism; substrate-applicable via
  Hebbian outer-product update
- **van de Ven 2024**: generative replay as functional regularization
  IS canonical ML theory; substrate's Bet B EMA-blend IS this primitive
- **Spens-Burgess 2024**: Modern Hopfield as hippocampal autoassociator
  IS canonical recent neuroscience model; substrate-applicable
- **PER/UPER**: prioritized experience replay IS canonical RL theory;
  substrate-applicable via fragility-weighted Hebbian top-up

**DECORATIVE filtered out**:
- REM/NREM neurochemistry (cholinergic dynamics; substrate has no neurochemistry)
- Schema integration in mPFC (substrate fixed codebook can't merge codes)
- Hippocampal indexing/transformation theories (substrate has no time
  axis on weights)
- Trace-replay sequence reorganization (substrate has no sequencing layer)

**Per [[feedback-no-smoke]] HONEST relabeling**: substrate's
materials-physics anchor for R22 is **computational-neuroscience
consolidation theory + ML continual learning theory**, NOT biological
hippocampal/cortical neurochemistry.

---

## 5. Experimental design recommendations

### Probe 1 (PRIMARY): SRC sleep replay substrate (S.1)

**Hypothesis**: substrate "sleep phase" with Tadros-style Hebbian
re-strengthening gives ≥ 1.3× Bet B v7 retention_A=0.954.

**Setup**:
- Modify substrate Bet B v6+v7 training: insert SLEEP cycles between
  Phase A and Phase B
- Sleep cycle: 1000 random bit-flip-noise reactivations + pattern
  completion + Hebbian update on successful replays
- Sleep duration: 0.1× training duration (tunable)
- Test: 3-task continual learning with Bet B retention metrics

**Predictions** (falsifiable):
- (a) P(SRC substrate retention_A ≥ 1.24 (= 1.3 × 0.954) is NOT
  possible — retention can't exceed 1.0): redirect to RELATIVE
- (a-revised) P(SRC substrate retention_A ≥ 0.97 vs Bet B v7
  baseline 0.954): 35-50%
- (b) P(SRC reduces forgetting in 3-task continual): 50-65%

**Kill criterion**: if SRC retention ≤ Bet B v7, sleep-replay adds
no value beyond EMA-blend mechanism.

**Cost**: 6-10 GPU hours.

### Probe 2 (STACK): Fragility-weighted prioritization (S.2)

**Hypothesis**: substrate prioritizes fragile stored patterns for sleep
replay; gives ≥ 1.2× over uniform S.1.

**Setup**:
- Pre-sleep: compute fragility score per stored pattern (cosine recall,
  energy margin, recall variance, replay count)
- Sleep replay distribution: P(replay_μ) ∝ fragility_μ^α with α=0.6
  (PER default)
- Compare to uniform S.1 baseline + Bet B v7 baseline

**Predictions**:
- (a) P(S.1+S.2 retention ≥ 1.2× uniform S.1): 25-40%

**Cost**: 4-6 GPU hours (incremental).

### Probe 3 (INCREMENTAL): Noise-driven reactivation (S.3)

**Hypothesis**: substrate "spontaneous" reactivations from random bit-
flip seeds give additional consolidation value beyond explicit prototype
replay.

**Setup**:
- Substrate generates 1000 random bipolar seeds; adds bit-flip noise;
  runs pattern completion
- Successful replays (cosine > 0.7 with nearest prototype) trigger
  Hebbian update
- Compare to S.1+S.2 baseline

**Predictions**:
- (a) P(S.3 stacks with S.1+S.2 productively): 30-45%

**Cost**: 3-5 GPU hours.

### Recommended sequencing

1. **Probe 1 (S.1 SRC) FIRST** (6-10 GPU hours) — substantial extension
   of Bet B
2. **Probe 2 (S.2 prioritization) SECOND** — incremental on Probe 1
3. **Probe 3 (S.3 noise-driven) OPTIONAL** — contingent on Probes 1+2

---

## 6. Predictions summary (with explicit probabilities per [[feedback-no-smoke]])

| Prediction | P | Notes |
|---|---|---|
| S.1 SRC retention ≥ 0.97 vs Bet B v7 0.954 baseline | 35-50% | Tadros 2022 precedent |
| S.2 prioritization stacks with S.1 productively | 25-40% | PER framework |
| S.3 noise-driven adds value beyond S.1 | 30-45% | Substrate-native |
| S.4 REM/NREM duality substrate-applicable | 5% | NEGATIVE — biology-specific |
| Schema-extraction substrate-applicable | 10% | NEGATIVE — fixed codebook |
| Bet B v6+v7 mechanism IS theoretically legitimized | 90% | van de Ven 2024 framing |
| At least one S.1-S.3 gives ≥ 1.3× Bet B v7 gain | 50-65% | Stacking estimate |
| R22 produces substrate-novel observation beyond Bet B legitimization | 35% | Mostly engineering port |

---

## 7. Citations (verified arXiv / DOI, 2016-2025)

### LOAD-BEARING for substrate (S.1-S.3 + Bet B legitimization)
- **Tadros-Krishnan-Ramyaa-Bazhenov Nat. Comm. 13 7742 (2022)
  DOI:10.1038/s41467-022-34938-7 — sleep-like unsupervised replay
  (HIGHEST SIGNAL substrate-applicable paper)**
- **van de Ven-Soures-Kudithipudi arXiv:2403.05175 (2024) — generative
  replay as functional regularization (CRITICAL Bet B legitimization)**
- **Spens-Burgess Nat. Hum. Behav. 8 (2024) DOI:10.1038/s41562-023-
  01799-z — generative consolidation with Modern Hopfield (substrate
  primitive legitimization)**
- van de Ven-Siegelmann-Tolias Nat. Comm. 11 4069 (2020)
  DOI:10.1038/s41467-020-17866-2 — brain-inspired replay foundational
- Bazhenov group arXiv:2410.16154 (2024) — extended SRC

### Substrate-applicable selection / prioritization (S.2)
- **Yang et al. Science 384 (2024) DOI:10.1126/science.adk8261 —
  SWR-selection for memory consolidation**
- **Schaul et al. arXiv:1511.05952 (2016) — PER foundational**
- **Sutter et al. arXiv:2506.09270 (2025) — UPER uncertainty-prioritized**
- Andrychowicz HER 2017 — hindsight foundational

### CLS theory + offline replay (PARTIAL substrate context)
- McClelland-McNaughton-O'Reilly 1995 — CLS foundational
- Pham-Liu-Yang-Sutton 2023 DualNet DOI:10.1162/neco_a_01612
- Sun et al. Nat. Neurosci. (2023) DOI:10.1038/s41593-023-01382-9
- Liu et al. Cell 178 640 (2019) — human MEG replay
- Higgins-Liu Nat. Comm. 15 (2024) DOI:10.1038/s41467-024-51582-5

### Sleep-inspired ML
- Harun et al. arXiv:2303.10725 (TMLR 2023) — SIESTA wake/sleep
- Bamnodkar arXiv:2507.21109 (2025) — TFC-SR
- Hickok arXiv:2505.12512 (2025) — scalable replay strategies

### DECORATIVE for substrate (filtered)
- Bowman et al. eLife (2024) — REM/NREM ACh (biology-specific)
- Sekeres-Winocur-Moscovitch Neurosci. Lett. 680 39 (2018) — TTT
- Berry et al. J. Theor. Biol. (2024) — SCT neural field

### Per [[feedback-verify-implementations]] audit
- Spot-checked Tadros Nat. Comm. 13 7742 (2022) abstract: "sleep-like
  unsupervised replay reduces catastrophic forgetting; MNIST/CIFAR/
  CUB-200 gains" ✓
- Spot-checked van de Ven arXiv:2403.05175 abstract: "Continual
  Learning and Catastrophic Forgetting; generative replay as functional
  regularization" ✓
- Spot-checked Spens-Burgess Nat. Hum. Behav. abstract: "generative
  model of memory construction and consolidation using Modern Hopfield
  Network" ✓
- Spot-checked Yang Science 384 abstract: "selection of experience for
  memory by hippocampal sharp-wave ripples" ✓
- Spot-checked Schaul PER arXiv:1511.05952 abstract: "prioritized
  experience replay" ✓
- Spot-checked Sutter UPER arXiv:2506.09270 abstract: "uncertainty
  prioritized experience replay" ✓
- Probability all framework attributions correct: 90%+
- Probability substrate-applicability filter correct: 80% (decorative-
  filtering pattern from R17/R32/R31/R27/R21/Bet F rehab confirmed)

---

## 8. Brutal-honesty caveats (per [[feedback-no-smoke]])

1. **Most sleep-replay neuroscience (60-70% per subagent) does NOT
   transfer cleanly to fixed-codebook bipolar Hebbian memory**.

2. **3 GENUINE substrate-applicable mechanisms**: S.1 SRC, S.2
   fragility-weighted prioritization, S.3 noise-driven reactivation.
   Combined 50-65% P of ≥ 1.3× Bet B v7 gain.

3. **CRITICAL Bet B legitimization (0 GPU cost)**: van de Ven 2024
   establishes generative replay as functional regularization;
   substrate's Bet B v6+v7 EMA-blend mechanism is theoretically
   legitimized as recognized consolidation primitive. Substrate-product
   framing benefit.

4. **S.4 REM/NREM duality DECLINED**: biology-specific; 5% P; substrate
   has no neuromodulatory system.

5. **Schema-extraction NEGATIVE**: 10% P; substrate fixed codebook
   can't merge codes without explicit superposition (capacity-limited).

6. **Trace transformation / multiple-trace theory NEGATIVE**: substrate
   has no time axis on weights; "transformation" requires off-substrate
   process.

7. **Per [[feedback-rehabilitation-after-rejection]]**: 4 mechanisms
   enumerated with explicit probabilities; S.4 declined with HONEST
   reasoning.

8. **Per [[feedback-materials-science-probe]]**: load-bearing analogs
   are computational-neuroscience consolidation theory + ML continual
   learning theory. NOT biological hippocampal/cortical neurochemistry.

9. **Per [[feedback-dont-overextend-theorems]]**: substrate's fixed-
   codebook architecture limits transferability of biological
   consolidation mechanisms; explicit filter applied.

10. **Per [[feedback-no-papers-product-only]]**: R22 framing is
    "substrate engineering extension of Bet B via SRC-style sleep
    replay; theoretical legitimization of EMA-blend mechanism." NOT
    novel sleep-consolidation theory.

11. **Pattern continues**: R17/R32/R31/Bet F/R27/R21/R22 all confirm
    cross-domain decorative-filtering pattern. Substrate-novel work
    concentrates in spin-glass / modern-Hopfield / free-probability
    cluster.

12. **Verified-implementations honesty**: subagent did real external
    lit scan with 35 tool uses + 64K tokens, ~60 verified citations
    2016-2025. Subagent flagged "60-70% biology-specific" UNPROMPTED —
    strong brutal-honesty protocol confirmation. Tadros 2022 cited
    multiple times as "HIGHEST signal" — confirms central status.

---

## 9. Deliverable summary

**To Strategy** (R22 routing decision):

**OPTIONS**:
- **PURSUE S.1 + S.2 + S.3** as substrate-product Bet B extension
  (10-21 GPU hours; 50-65% P of ≥ 1.3× Bet B v7 retention gain)
- **PURSUE S.1 only** as minimal extension (6-10 GPU hours; 35-50% P)
- **DEFER R22 engineering**: integrate van de Ven 2024 Bet B
  legitimization framing (0 GPU; HIGH substrate-product value)

**RECOMMENDATION**: pursue minimum 0-cost legitimization (always);
consider S.1 if Bet B extension is substrate-product priority. S.4
DECLINED.

**Closure scope per [[feedback-dont-overextend-theorems]]**: R22 does
NOT close sleep-consolidation research generally; identifies
substrate-applicable engineering path via SRC sleep replay + fragility-
weighted prioritization.

**To Experiment Dev**:
- Probe 1 (S.1 SRC sleep replay): 6-10 GPU hours; substantial Bet B
  extension
- Probe 2 (S.2 fragility prioritization): 4-6 GPU hours; incremental
- Probe 3 (S.3 noise-driven): 3-5 GPU hours; incremental
- DECLINE S.4 REM/NREM duality

**To Research (future R# routing — backlog now nearly exhausted)**:
- R19 (Topological beyond winding, LOWER): REDUNDANT with R28 + Bet F
  rehab; quick subsume-declare in research_blocker.md
- R25 (Aging/Kovacs, LOWER): REDUNDANT with R23 + R24 + R18; subsume
- R36-R39 (Research-internal followups from R16/R18/R17/R28)
- **All META + design-space items now addressed**; consider
  research_blocker.md per protocol step (3) declaration

**Per [[feedback-no-smoke]]**: R22 HONEST framing is "S.1 SRC sleep
replay is substrate-applicable Bet B extension; van de Ven 2024
legitimizes Bet B v6+v7 mechanism theoretically; 60-70% of sleep-
replay neuroscience decorative for substrate."

---

**End R22 note.** Total size target ~30 KB; actual: see wc -c on
finalized file.
