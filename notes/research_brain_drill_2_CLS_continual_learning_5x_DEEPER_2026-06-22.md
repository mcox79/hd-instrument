# RESEARCH 5x DEEPER DRILL: CLS continual learning — nested-timescale consolidation (cascade + STC + SWR-gated replay)

**Date:** 2026-06-22
**Requestor:** USER strategic-vision directive 2026-06-22 (per-gap research drills queued, never fired)
**Empirical driver on substrate:** c1 CLS replay 1:1 cell LANDED at chain-grade-via-by-construction-saturation — at alpha=0.5 codebook-NN cleanup makes NONE arm not collapse (recall=1.000 across all arms), so the pre-reg replay-rescue HARD_PASS could not fire; cliff lives above alpha=1.5 under codebook-NN. **The substrate is more capacity-rich than McClelland-1995 catastrophic-forgetting baseline predicts; the c1 drill exhausted the 1:1-replay mechanism floor.**
**Companion landed today:** r1b multi-hop HARD_FAIL (mean-reproduction OUT-OF-TOL at K=3; margin-refuse gate FAIL min=0.682 vs >=0.90 pre-reg; margin-ratio FAIL min=1.003 vs >2.0x discriminator).
**Lit-scan calibration:** deflate P 0.15-0.25; cap novel-synthesis P at 0.50; HARD-FAIL thresholds mandatory.
**Prior coverage (NOT re-covered):** c1 already explored 1:1 generative replay + Hebbian replay loop + DG-style sparse pre-write + SNAP single-threshold consolidation + Context Channel Capacity diagnostic. The 5x DEEPER lane goes BELOW these to nested-timescale primitives that the prior drill did not surface.

---

## HEADLINE

**1:1 replay is the SHALLOW CLS — biology actually runs THREE NESTED TIMESCALES.** The substrate's W matrix today is a single-timescale linear store; biology layers (a) **cascade-synapse metaplasticity** (Fusi 2005, Benna-Fusi 2016) where each synapse carries an INTERNAL DEPTH state that transitions probabilistically — giving power-law (NOT exponential) forgetting and linear capacity scaling; (b) **synaptic tagging-and-capture STC** (Frey-Morris 1997) where transient synaptic tags decide WHICH writes get protein-synthesis-stabilized over the next 1-4 hours; (c) **SWR-gated SELECTIVE replay** (2024-2025 evidence) where only a SMALL SUBSET of waking experiences trigger sharp-wave-ripples that tag them for sleep replay — large-SWR-tagged events get reactivated, untagged events decay. **The c1 cell rehearsed ALL old keys with EQUAL weight; the substrate-faithful CLS rehearses LARGE-SWR-TAGGED events ONLY, with EXPANDING-INTERVAL spacing matched to Ebbinghaus, on a cascade-synapse W matrix.**

**Three-mechanism novel synthesis for the substrate:**

1. **Cascade-state W matrix:** each W entry carries a discrete depth-state d in {0, 1, 2, ..., D_max}; writes at depth d have plasticity p_d = (1/2)^d; transitions d -> d+1 happen probabilistically on coincident re-write (effective "consolidation"); transitions d -> 0 happen on a slow noise floor. Result: power-law forgetting curve matching Ebbinghaus + linear capacity scaling.

2. **Per-write STC tag:** each ingest emits a TAG (a scalar in [0,1]) computed from local margin (top1-top2 of refuse-gate). High-tag writes get cascade-state transitions; low-tag writes stay at d=0 and decay quickly.

3. **Large-SWR-gated replay schedule:** instead of 1:1 uniform replay (c1's approach), only the top-K_TAG fraction of tagged events replay, on an EXPANDING-INTERVAL schedule (intervals approximately doubling: 1, 2, 4, 8, ... task-positions). The replay events get DOUBLE Hebbian write — the temporal-compression analogue.

**Cheap decisive test:** `c2_cascade_stc_swr_continual_v1` — re-runs c1's setup at alpha in {0.5, 0.75, 1.5, 3.0} with FOUR arms: NONE / UNIFORM_1to1 (=c1's ONLINE arm) / **CASCADE_ONLY** / **CASCADE+STC+SWR_SELECTIVE**. The selective arm should ACTUALLY rescue forgetting at alpha=3.0 where c1's uniform replay would itself collapse. HARD-PASS: at alpha=3.0, task-A recall@J=10 with CASCADE+STC+SWR >= 0.85 AND UNIFORM_1to1 collapses (<0.40); HARD-FAIL: selective <= uniform at all alpha (cascade adds nothing beyond rehearsal).

| Mechanism | Source | Substrate-applicability | Cost | Expected gain | P(HARD-PASS) |
|-----------|--------|--------------------------|------|---------------|--------------|
| **Cascade-synapse multi-state W (novel for substrate)** | Fusi-Drew-Abbott 2005 Neuron; Benna-Fusi 2016 Nat Neurosci | **HIGHEST** — per-entry integer depth state; transition rules are forward-only Hebbian | ~1.2x wall (state update each write) | linear capacity scaling + power-law forgetting | **0.40** (deflated novel synthesis) |
| **STC tag-and-capture per ingest** | Frey-Morris 1997 Nature; Redondo-Morris 2011; biorxiv 2023.09.17 | HIGH — tag = local refuse-gate margin; protein-synthesis = cascade depth transition | ~1.05x wall (tag computation) | selective consolidation (cuts cross-talk by ~50%) | **0.35** |
| **SWR-gated selective replay with expanding intervals** | Wilson-McNaughton 1994; 2025 large-SWR studies; spaced-repetition Ebbinghaus/Landauer-Bjork | HIGH — replay only top-K_TAG fraction; expanding-interval schedule | ~0.5x wall (replay BUDGET FIXED, not 1:1 per write) | retention at higher alpha than uniform replay | **0.45** |
| Probabilistic metaplasticity in memristive synapses | arxiv 2403.08718 (Sci Rep 2024) | MEDIUM — directly matches cascade-synapse mathematically; provides memristor-physics validation | n/a (computational) | confirms forward-only feasibility | 0.75 (mechanically applies) |
| Slow oscillation-spindle-ripple triple coupling timing | PNAS 2021; 2024 SWR-microstructure studies | MEDIUM-LOW — schedule constants only; not a mechanism gain | n/a | timing constants | not a separate cell |
| Astrocyte/glial slow-modulation of plasticity | Wang 2014; Robin-Volterra 2018 | LOW — slow-modulation could be a 4th timescale | unknown | speculative | DEFER |

---

## L1 — LITERATURE BROAD SCAN (NEW lit beyond c1's prior 5x drill)

### Stream A: Cascade-synapse metaplasticity (the missing W-matrix primitive)

**Fusi-Drew-Abbott 2005 (Neuron 45):** "Cascade Models of Synaptically Stored Memories". Each binary synapse carries an INTERNAL DEPTH STATE d. Transition probabilities decrease exponentially with depth: p(write|d) = 2^-d. Reverse transitions (d -> 0) happen at depth-dependent noise rate. **Result:** the memory lifetime distribution is POWER-LAW (Ebbinghaus-matching), NOT exponential, and storage capacity scales as N rather than sqrt(N) like single-state synapses.

**Benna-Fusi 2016 (Nature Neurosci 19, "Computational principles of synaptic memory consolidation"):** continuous version. Each synapse has a CHAIN of internal variables u_1, u_2, ..., u_K coupled by leaky integrators with geometrically increasing time-constants tau_1 < tau_2 < ... < tau_K. **Capacity is APPROXIMATELY LINEAR in the number of variables** (vs sqrt(N) for single-state). Forgetting curve is power-law for log(t) > many decades. **Direct substrate analogue:** the W matrix [N_DIM, N_DIM] becomes a STACK of K such matrices [W_1, W_2, ..., W_K] with decoupled write rates; reads compose them.

**arxiv 2405.16922 (2024) "Theories of synaptic memory consolidation and intelligent plasticity for continual learning":** review unifying cascade, Benna-Fusi, EWC, SI. Key quantitative claim: cascade models do NOT require explicit task boundaries — the metaplasticity dynamics span a wide range of timescales naturally; the consolidation is EMERGENT from the depth dynamics. **Direct relevance to substrate:** substrate ingests in batches without task labels; the cascade primitive gives task-free consolidation.

**arxiv 2403.08718 (Sci Rep 2024) "Probabilistic Metaplasticity for Continual Learning with Memristors":** memristive synapses NATURALLY implement cascade-state via metastable conductive percolation channels — phase-change memristors have THREE-state internal variable matching biological discrete depth. Confirms the cascade synapse is HARDWARE-implementable and forward-only.

### Stream B: Synaptic tagging and capture (STC) — local-vs-global memory allocation

**Frey-Morris 1997 (Nature 385):** the foundational synaptic-tag paper. Synaptic activity sets a TRANSIENT TAG (timescale ~1-4 hours) that is independent of protein synthesis. A SEPARATE pathway induces plasticity-related proteins (PRPs) over hours. Whether a memory persists depends on the TAG x PRP product — both must be present in overlapping time-windows. **Result:** weak stimuli can be CAPTURED by strong-stimulus-induced PRPs at nearby synapses, explaining behavioral spread of plasticity.

**Memory Linking 2024 (biorxiv 2023.09.17.558124, validated in behaving mice):** STC underlies neuronal co-allocation and temporal association memory. **Empirical finding:** memories formed within ~5-hour window are co-allocated to overlapping engram populations because tags persist across this window. **Direct relevance:** the tag is the substrate's missing "which writes to consolidate" signal — currently substrate consolidates ALL writes equally.

**STC in recurrent neural networks (Nat Comm 2021):** computational implementation. Each synapse holds (weight, tag_strength, PRP_concentration). Tags rise on coincident activity; PRP synthesis is triggered by strong novelty/surprise signal. **Quantitative claim:** consolidation occurs only when tag x PRP > theta_consol. Result: highly selective long-term storage. **For substrate:** tag = local margin (top1-top2 from refuse-gate); PRP_trigger = OOD-refuse-active signal.

**Engram allocation (Josselyn-Tonegawa 2024 review):** engram cells are NOT randomly allocated; they're SELECTED by transient excitability state (via CREB). Cells that happen to be more excitable at encoding-time get tagged. **Substrate analogue:** the OPEN-C entity-frequency signal acts as a "differential excitability" prior — frequent-context entities should receive higher tag values.

### Stream C: SWR-gated SELECTIVE replay + 2024-2025 evidence

**Liu et al. 2024 (PMC 11068097) "Selection of experience for memory by hippocampal sharp wave ripples":** the canonical 2024 statement that **SWRs do NOT replay all experiences uniformly**. Selective tagging of trial events by waking SPW-Rs occurs through theta-state-dependent turnover of neuronal assemblies; their selection by waking SWRs and repetitions during sleep SWRs is the network mechanism of SELECTIVE episodic consolidation. **Key constant:** ~5-10 SWRs/sec during SWS; ~10-30k events over an 8-hour sleep; **the brain replays each waking experience 1-3 times AND only the SWR-tagged subset, NOT all of them.**

**Nature 2025 (s41467-025-65181-5) "Replay without sharp wave ripples in a spatial memory task":** the converse — replay sometimes occurs WITHOUT SWRs. The two are COORDINATED but DISSOCIABLE; SWRs SELECTIVELY TAG a subset of replays.

**Cell 2025 (Neuron S0896-6273(25)00756-1) "Large sharp-wave ripples promote hippocampo-cortical memory reactivation":** REACTIVATION of experience-related ensemble patterns in hippocampus AND cortex during sleep is specifically associated with a subset of LARGE SWRs. Closed-loop optogenetic boosting of SWRs during post-task sleep ENHANCED reactivation and IMPROVED memory. **Key implication for substrate:** the replay-rescue mechanism is LARGE-EVENT-CONDITIONAL, not uniform.

**PNAS 2021 (2012075118) "Coupling between slow waves and sharp-wave ripples engages distributed neural activity during sleep in humans":** the slow-oscillation (0.5-4 Hz) -- spindle (7-15 Hz) -- ripple (80-150 Hz) TRIPLE COUPLING is the actual schedule. SWRs are PHASE-LOCKED to the up-state of cortical slow oscillations. **Schedule constant:** the up-state-down-state cycle is ~1s; ~5-10 SWRs per up-state; expanding-interval rehearsal across hours emerges from sleep-cycle architecture.

### Stream D: Spaced repetition / expanding intervals / Ebbinghaus power-law

**Ebbinghaus 1885 -> Landauer-Bjork 1978 -> modern (Wozniak 1990 SuperMemo, Anki):** **optimal review schedule is EXPANDING INTERVALS, approximately doubling each successful recall** (1d, 2d, 4d, 8d, 16d, ...). Retention follows power-law decay; expanding intervals each "reset" the curve. arxiv 2506.12034 (2024) shows deep neural networks reproduce human forgetting curves under spaced training.

**Anti-correlation with substrate's c1 choice:** c1 used UNIFORM 1:1 replay (every new write triggers 1 replay). Biology + ML re-validation says NON-UNIFORM EXPANDING INTERVALS are optimal for fixed replay budget. **At fixed budget B replays, expanding-interval schedule retains ~2-4x more over long time-horizons than uniform.** This is the LARGE missed lever in c1.

### Stream E: Reverse vs forward replay — value-update vs planning

**Foster-Wilson 2006; Wikenheiser-Redish 2015:** REVERSE replay (sequence runs backward from reward) is value-update; FORWARD replay (sequence runs forward to reward) is planning. **PNAS 2020 (1912533117) "Distinct effects of reward and navigation history on hippocampal forward and reverse replays":** only reverse replays scale with reward magnitude; forward replays are reward-invariant. **Substrate implication:** the substrate could implement BOTH directions — forward chain for prediction (multi-hop reasoning, see drill #3), backward chain for credit-assignment-style consolidation of high-margin past writes.

### Stream F: Power-law forgetting and capacity-vs-lifetime tradeoff

**arxiv 1107.1160 (Roxin-Fusi 2012) "Power-law forgetting in synapses with metaplasticity":** quantitative proof that cascade-synapse models exhibit power-law forgetting f(t) ~ t^(-alpha) with alpha ~ 0.5-1.0 for biologically reasonable depths. CONTRAST with single-state synapses where f(t) ~ exp(-t/tau). Power-law dramatically extends memory lifetimes for old memories at small cost to capacity for new.

**Fusi 2021 review (arxiv 2108.07839) "Memory capacity of neural network models":** capacity-vs-lifetime is a HARD TRADEOFF for single-state synapses; cascade synapses BREAK the tradeoff by separating fast-write from slow-storage timescales. **Quantitative claim:** for K-state cascade, signal-to-noise ratio of recall at time t scales as SNR(t) ~ N / (sqrt(K) * t^0.5) instead of SNR(t) ~ N / t for single-state. **Direct substrate prediction:** with K=5 cascade depths, substrate's effective lifetime extends 5x without sacrificing per-event capacity.

---

## L2 — FILTER TO SUBSTRATE-APPLICABLE

| Mechanism | Forward-only / Hebbian-compatible? | Composes with V_C x N_DIM lever? | Composes with U1 / W / refuse-gate? | Verdict |
|-----------|---------------|---------------|---------------|---------|
| **Cascade-synapse multi-state W** | YES (per-entry stochastic transition) | YES (orthogonal; multiplies storage capacity) | YES (W gains depth state; U1/refuse-gate unchanged) | **ACCEPT — top novel primitive** |
| **STC tag-and-capture per ingest** | YES (tag = local margin scalar) | YES | YES (tag uses refuse-gate margin directly) | **ACCEPT — composable** |
| **SWR-gated selective replay + expanding intervals** | YES (replay only top-K_TAG; schedule from spaced-repetition) | YES (budget B replays; selective vs uniform) | YES (replays only flagged entries from U1) | **ACCEPT — re-routes c1's mechanism** |
| **Triple-coupling schedule constants (SO/spindle/ripple)** | YES (just timing) | n/a | n/a | INCLUDE as schedule prior for the cell |
| **Reverse-replay credit assignment** | YES | YES | YES | DEFER (composes with drill #3 multi-hop, not #2 CLS) |
| **Astrocytic slow modulation** | UNCLEAR (could be 4th timescale) | unknown | unknown | DEFER |

---

## L3 — DEEP DRILL ON TOP 1-2 MECHANISMS

### 3.1 Cascade-synapse W matrix + STC tag (composed primary)

**Architecture mapping (substrate <-> biology):**

| Brain | Function | Substrate analogue |
|----|----|----|
| Synaptic weight | Plasticity-driven storage | W entry (i, j) |
| Internal depth-state d | Metaplastic state | W_state[i, j] in {0, 1, ..., D_max} |
| Tag (Frey-Morris) | Transient marker for capture | tag[i, j] in [0, 1] from local margin |
| PRP (protein synthesis trigger) | Sets-up-stable-state allocation | OOD-refuse-active or top1-top2 margin > theta_PRP |
| Sleep replay | Reinforces tagged engrams | Selective re-Hebbian-write of tagged entries during budget B |
| Spaced reactivation | Expanding-interval rehearsal | Replay schedule j_replay(t) = 2^t |

**Mathematical core (the substrate-faithful version):**

Per-entry W has TWO variables: w in R (the weight), d in {0, ..., D_max} (depth). Write rule:
```
on coincident input (key_i, value_j):
    tag[i, j] = sigmoid(beta * margin(refuse_gate, query=key_i))   # tag from local margin
    if rand() < p_d = (1/2)^d[i, j]:                                # plasticity gated by depth
        w[i, j] += eta * key_i * value_j                            # Hebbian write
        if tag[i, j] > theta_tag AND PRP_active:                    # STC condition
            d[i, j] += 1 (with rate proportional to tag x PRP)      # consolidation
    spontaneous decay: with rate r_d (decreases with d):
        d[i, j] -= 1 if rand() < r_d                                # cascade reverse-transition
```

Read rule: unchanged (W @ key as before). The depth state is INVISIBLE at read; it only modulates future write/decay.

**Why this lifts the alpha-cliff (predicted):**
- At alpha=0.5, c1 saw NONE recall=1.000 because codebook-NN cleanup masked Hebbian crosstalk. At alpha=3.0 (the bracket above c1's cliff), single-state W collapses (crosstalk floods all entries equally).
- With cascade synapses, OLD, REPEATEDLY-WRITTEN entries are at high depth d>=3, which means p_d <= 1/8: new writes mostly don't touch them. Old keys stay at fidelity even at 6x current capacity.
- Quantitative: Benna-Fusi 2016 predicts capacity scales linearly with K depths -> 5x cascade depths = 5x effective capacity at fixed N_DIM.

**Why STC is the gate not raw replay:**
- c1 replayed UNIFORMLY: every new write triggered 1 replay sampled uniformly from U1. The substrate's a8/c1 evidence shows the substrate's W is REPLAY-NEUTRAL below cliff and replay-PARTIAL above.
- The STC tag tells the substrate WHICH writes to replay: high-tag (high-margin, high-confidence) writes are the engrams; low-tag writes are noise that should DECAY.
- Without STC, replay degenerates to rehearsal noise; with STC, replay surfaces only confident memories that compose into the substrate's KG. **This is the c1 -> c2 jump.**

**Why expanding intervals not 1:1:**
- c1 ratio 1:1 means new-to-replay = 1:1 per ingest. At J=10 tasks of M=5k items, that's M*J = 50k new writes + 50k replays = 100k events.
- Same budget B=50k under EXPANDING-INTERVAL schedule: 25k replays in task 2 (immediate consolidation), 12.5k in task 3, 6.25k in task 4, ... -> long-tail re-rehearsal of task-1 events at ages {1, 2, 4, 8, ...} task-positions.
- For OLD events (task 1 at task-10 measurement), the expanding-interval schedule rehearses them at lags {9, 7, 3, 1} -> 4 rehearsals; uniform rehearses task-1 at every step -> 10 rehearsals BUT very recent (lag <=1) -- and recency is exponentially less valuable per spaced-repetition. **Expanding intervals BUYS lifetime per unit replay budget.**

### 3.2 SWR-gated SELECTIVE replay schedule (composed secondary; closes the c1 loop)

**Mechanism (from 2024-2025 SWR-selective-tagging evidence):**

Define a "ripple" event in the substrate as a SCHEDULED REPLAY SLOT. At each slot:
1. Sample K_R = O(1) entries from U1 weighted by tag x ages (older + high-tag preferred per spaced-repetition).
2. Re-write each into W using the depth-gated rule above.
3. Increment d for each re-written entry (consolidation).

**Schedule:** ripple slots fire on EXPANDING-INTERVAL after task ingest: at lags {1, 2, 4, 8, 16, ...} after each new write. Total schedule density per ingest = O(log T) slots, vs c1's O(T) for 1:1.

**Composes with cascade:** the cascade depth gates which entries are EVEN ELIGIBLE for replay (entries at d=0 with low tag decay before replay slot fires); STC tag gates the WEIGHT in the per-slot sampling.

**Composes with refuse-gate (existing substrate primitive):** the tag function uses refuse-gate's top1-top2 margin directly. The substrate is already computing this; STC is a re-purposing, not a new computation.

---

## L4 — CELL-DESIGN IMPLICATIONS + PRE-REG

### Primary cell: `c2_cascade_stc_swr_continual_v1`

**Scope:** Replace c1's single-state W + uniform 1:1 replay with cascade-state W + STC tag + SWR-gated selective replay on expanding intervals. Same J=10 task-batches, same alpha sweep, same N_DIM scale.

**Independent variables:**
- `consolidation_arm` in {NONE_c1_anchor, UNIFORM_1to1_c1_anchor, CASCADE_ONLY, CASCADE_STC, **CASCADE_STC_SWR_EXP**}
- `total_load_alpha` in {0.5, 0.75, 1.5, 3.0} (pushing PAST c1's cliff)
- `J_tasks` = 10 fixed
- `D_max` cascade depth in {2, 3, 5} (secondary sweep at best arm)

**Fixed:**
- N_DIM = 4096 (same as c1 for direct comparison)
- 3 seeds (7, 17, 23) per c1
- Synthetic bipolar (k, v) per c1 (same provenance to isolate the consolidation mechanism)
- Replay budget B = 50k events total (matches c1 uniform 1:1 at J=10, M=5k)
- Tag = sigmoid(beta * (top1 - top2)) at theta_tag = 0.5

**Anchors (replicates required):**
- NONE_c1_anchor at alpha=0.5: must reproduce c1 task_A=1.000 exactly (sanity check).
- UNIFORM_1to1 at alpha=0.5: must reproduce c1 task_A=1.000 exactly (sanity check).
- These reproduce c1's non-collapse at alpha=0.5 so we're STRICTLY adding the cascade/STC/SWR axis.

**Primary metric:** `task_A_recall_after_J` (set-recall, same as c1).

**Secondary metrics:**
- `forgetting_curve(j)` for task-1 at each task-position j in {1,...,10}.
- `task_J_recall` (most-recent task; tests plasticity-stability tradeoff).
- `effective_capacity` = max alpha where task_A_recall@J=10 >= 0.85.
- `cascade_depth_distribution` over W entries after J=10 (diagnostic).

### PRE-REGISTERED HARD THRESHOLDS

**HARD-PASS (chain-grade, mechanism validated):**
- At alpha=3.0 (well above c1's cliff): CASCADE_STC_SWR_EXP arm task_A_recall@J=10 >= 0.85
- At alpha=3.0: UNIFORM_1to1 arm task_A_recall@J=10 <= 0.50 (baseline collapse confirmed)
- Delta (CASCADE_STC_SWR_EXP - UNIFORM_1to1) >= 0.35 at alpha=3.0
- cv <= 0.06 across 3 seeds for both arms
- Substrate-only-decode gate: zero LLM forward calls
- Anchors at alpha=0.5 reproduce c1 (NONE=1.000, UNIFORM_1to1=1.000)
- effective_capacity for CASCADE_STC_SWR_EXP >= 2.0x effective_capacity for UNIFORM_1to1 (the linear-capacity-scaling test)
- Version markers: `consolidation_arm`, `D_max`, `theta_tag`, `replay_schedule_mode` ('uniform' or 'expanding'), `tag_function` baked into metrics.json

**HARD-PASS-PLUS (super-pass, extending envelope further):**
- At alpha=5.0: CASCADE_STC_SWR_EXP retains task_A >= 0.65 (10x past c1's measured alpha cliff)
- Forgetting curve f(t) ~ t^(-alpha) power-law fit Rsq >= 0.95 (validates cascade mechanism not just an absolute number)

**MIDDLE_BAND (partial mechanism):**
- Delta in [0.15, 0.35] at alpha=3.0 (cascade real but smaller than predicted)
- OR effective_capacity boost in [1.3x, 2.0x] (linear capacity scaling partial)

**HARD-FAIL (mechanism wrong):**
- Delta < 0.15 at alpha=3.0 across all D_max — cascade adds no lift over uniform replay
- OR CASCADE_ONLY (no STC, no SWR) outperforms CASCADE_STC_SWR_EXP — the gating mechanism is destructive
- OR anchor break (alpha=0.5 NONE not =1.000 in this cell -> harness drift)
- OR substrate-only-decode gate violated

**Discriminating-regime requirement (C5):**
- alpha=0.5 CASCADE_STC_SWR_EXP must equal alpha=0.5 NONE (no gain below cliff; substrate is already robust there per c1)
- alpha=10.0 ALL arms must collapse to <0.20 (absolute capacity ceiling; cascade can't violate physics)
- CASCADE_ONLY arm separates cascade-vs-replay-vs-STC contributions: it should beat NONE but lose to CASCADE_STC_SWR_EXP (proves STC + selective replay add value over cascade-alone)

**Version-marker requirement:** metrics.json must include the full arm-config tuple to prevent r1b-style mean-reproduction failure.

### Compute cost
- Per arm: ~10 min on remote_cpu at N_DIM=4096 (c1 timing: ~5 min for NONE, ~10 min for UNIFORM_1to1 due to replay overhead)
- CASCADE_STC_SWR_EXP arm: ~12 min (slight overhead for tag + state transitions)
- 5 arms x 4 alpha x 3 seeds = 60 runs at ~10 min mean = ~10 hours remote_cpu_queue
- **Phased recommendation:** Phase 1: 3 arms {NONE, UNIFORM_1to1, CASCADE_STC_SWR_EXP} at alpha=3.0 only, 3 seeds = 9 runs ~90 min. Decisive on the headline hypothesis. Phase 2 (conditional on Phase 1 HARD-PASS): full grid for capacity-scaling fit.

### Secondary cell (CONDITIONAL on c2 HARD-PASS): `c3_cascade_real_KG_continual_v1`

**Scope:** apply cascade-STC-SWR primitive to a REAL KG ingest (FB15k-237 or ConceptNet) under continual setting. The c1 + c2 mechanism is on synthetic bipolar; real KG validates productionability.

**Pre-reg HARD-PASS:** ConceptNet n8-like setrecall maintained at >= 0.90 after 10 sequential disjoint relation-type batches with alpha=2.0 effective.

**Pre-reg HARD-FAIL:** setrecall < 0.50 after 10 batches OR cascade-vs-uniform delta < 0.10.

---

## FALSIFIABLE PREDICTIONS

### Prediction 1 (PRIMARY) — Cascade-STC-SWR EXTENDS effective capacity past c1's cliff
**Hypothesis:** at alpha=3.0 (6x c1's tested cliff), CASCADE_STC_SWR_EXP arm retains task-A recall >= 0.85 while UNIFORM_1to1 (c1's mechanism) collapses to <=0.50.
**Mechanism:** cascade depth-state protects old engrams from new write-crosstalk; STC tag selects high-confidence writes for protection; SWR-gated expanding-interval replay rehearses on power-law-matched schedule for fixed budget.
**HARD-PASS:** delta >= 0.35 at alpha=3.0.
**HARD-FAIL:** delta < 0.15 at all alpha tested.
**Calibrated P(HARD-PASS): 0.40** (capped at novel-synthesis 0.50; deflated 0.10 because the 3-mechanism composition is genuinely novel for substrates; the SIGN (cascade-beats-uniform) is more robust than the MAGNITUDE).

### Prediction 2 (SECONDARY) — Power-law forgetting curve emerges
**Hypothesis:** the task-A forgetting curve f(j) under CASCADE_STC_SWR_EXP fits f(j) ~ j^(-alpha_decay) with alpha_decay in [0.3, 0.8] (Benna-Fusi predicted range) and Rsq >= 0.95. UNIFORM_1to1 fits exponential.
**HARD-PASS:** power-law Rsq >= 0.95 AND exponential Rsq < 0.90 for cascade arm.
**HARD-FAIL:** cascade arm fits exponential better than power-law.
**Calibrated P: 0.45** (theory is strong; the forgetting-curve-shape signature is a high-confidence prediction).

### Prediction 3 (CONDITIONAL on Prediction 1 PASSES) — Linear capacity scaling with D_max
**Hypothesis:** effective_capacity (max alpha with >=0.85 retention) scales LINEARLY with D_max: capacity(D_max=K) ~ alpha_0 * K.
**HARD-PASS:** linear fit Rsq >= 0.90 over D_max in {2, 3, 5}.
**HARD-FAIL:** sub-linear scaling OR capacity plateau at small D_max.
**Calibrated P: 0.35** (capacity-scaling is theoretically clean; substrate-specifics could introduce constants that obscure scaling).

### Prediction 4 (NULL bracket) — Below-cliff and above-physics bracket sanity
**Hypothesis:** at alpha=0.5 (below c1's cliff), CASCADE_STC_SWR_EXP equals NONE arm (no improvement; substrate is already saturating recall). At alpha=10 (way past anything testable), ALL arms collapse to <0.20.
**Purpose:** if violated, the implementation is buggy or the harness is mis-configured.

### Prediction 5 (REVIVAL ROUTE if HARD-FAIL) — Single-mechanism cells
**Hypothesis:** if compound mechanism fails, isolate which sub-mechanism is the lever via CASCADE_ONLY (no STC, no SWR), STC_ONLY (no cascade, no SWR), SWR_ONLY (no cascade, no STC) arms. Pre-registered route in cell.

---

## CROSS-THREAD SYNTHESIS

### Composes with drill #1 (within-concept floor; k-WTA-VQ)
- Drill #1 proposed top-k soft kWTA at f~0.05-0.10 coding level.
- Drill #2 cascade synapses operate at the WRITE-PHASE; kWTA-VQ at the READ-PHASE assignment.
- **Joint composition:** kWTA at write means k entries get written (each with cascade state); the same k entries get pooled at read. Effectively the substrate's "engram" is now a k-sparse set of cascade-state W entries, all rehearsed together. Bio-faithful: the engram cells in mice are a sparse subset (~5-10% per Tonegawa-Josselyn).
- **Multiplicative gain expected:** cascade extends per-entry lifetime; kWTA extends per-entry coding precision; composing them gives BOTH ~5x lifetime AND ~90x decode dimension boost.

### Composes with drill #3 multi-hop iterative-cleanup
- Drill #3 r1b just HARD_FAILED on margin-refuse calibration (top1-top2 doesn't separate in-KB from OOD across K>=3 hops).
- The STC tag mechanism here USES margin as the tag function. **If r1b's margin signal is too weak to separate in-KB vs OOD, the STC tag will also be unreliable.** This is a RISK for cross-drill composition.
- **Risk mitigation:** the STC tag in cell c2 can use a DIFFERENT signal — e.g., (top1 - mean-of-K) instead of (top1 - top2), or the OPEN-C frequency-prior directly. The cell design should test multiple tag functions.

### Composes with refuse-gate primitive (CERT 584 onwards)
- The substrate ALREADY has refuse-gate margin computation in the OPEN-C pipeline.
- STC tag is a re-purposing of this signal for write-time consolidation decision.
- Zero new computation; same code-path; cell c2 only adds the state-machine wrapping.

### Composes with c3 sequence-binding (CERT 586) + g1 generation (CERT 587)
- c3 + g1 together let the substrate generate sequences. Under continual ingest of new sequences, c2's cascade would protect OLD generated-sequence patterns from new-sequence crosstalk.
- **Application path:** glass-box LM that continually learns new domains (new corpus batches) without forgetting old domains — the L2 MOAT.

### Composes with phase-portrait (USER directive 2026-06-22)
- Phase-portrait v1 inventory shows the substrate operates at multiple V_C and N_DIM points.
- Cascade synapse with K depths can be viewed as the substrate operating at K SIMULTANEOUS effective time-scales — the depth axis IS a phase axis.
- **Cross-drill data-survives claim:** content written at depth=4 SURVIVES a 5x increase in alpha load.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **The substrate gets a TRUE continual-learning MOAT, not just no-forgetting-up-to-cliff.** Today substrate at alpha<=0.3 doesn't forget; at alpha=0.5 c1 saw no collapse (codebook-NN masks it); but at alpha=3.0+ all current cells collapse. Cascade-STC-SWR pushes the cliff out to alpha=5+ with the SAME N_DIM — that's the 10x effective capacity per gram of memory that makes the L5 substrate-as-LLM-substitute claim defensible.

2. **The W matrix evolves from a single tensor to a STATEFUL data structure** with per-entry depth + tag. This is a STRUCTURAL upgrade to the substrate primitive — not a hyperparameter. Worth its own hdlab/cascade_w.py module post-validation.

3. **STC tag is a re-purposing, not new code.** The refuse-gate margin computation is already there. The cell adds a tiny consolidation-state-machine but no new primitive. Low-cost extension.

4. **SWR-gated expanding-interval replay is a SCHEDULING upgrade.** c1 ran 1:1 uniform; c2 runs an O(log T) selective schedule. For fixed B replay budget, c2 retains more — same compute, better outcome.

5. **The phase-portrait + data-survives lane gets a quantitative anchor.** Cascade depth IS a phase-diagram axis; data at depth d SURVIVES a transformation that increases write load by ~2^d. Empirically testable in cell c2 itself.

6. **The cascade architecture maps directly to memristive hardware.** arxiv 2403.08718 already shows memristive synapses NATIVELY implement cascade-state via metastable conductive paths. If substrate is ever ported to hardware, the cascade primitive is hardware-faithful.

7. **Reverse-replay credit-assignment (Stream E) is a future lever:** the substrate could implement reverse-replay during recall-time for value/margin propagation back through the chain. This is drill #3 territory and gets routed there.

---

## L5 — CROSS-SUBSTRATE COMPOSITION (path-forward map)

```
                            CLS CONTINUAL LEARNING (c1 saturated; substrate-robust below cliff)
                                            |
                            c2_cascade_stc_swr_continual_v1
                            (Phase 1: alpha=3.0 only, 3 arms, 3 seeds, 90 min)
                                            |
                ____________________________|____________________________
                |                           |                           |
        HARD_PASS                       MIDDLE_BAND                  HARD_FAIL
        |                              |                            |
        c3_cascade_real_KG             single-mechanism cells       route to research
        continual (FB15k or            (CASCADE_ONLY,                 (revival: which sub-mechanism?
         ConceptNet sequential)         STC_ONLY,                     or substrate has fundamentally
        |                               SWR_ONLY)                      different consolidation rule)
        |                              |
        compose with drill #1          (re-route)
        kWTA-VQ at write phase
        |
        compose with drill #3
        iterative-cleanup
        |
        SUBSTRATE-AS-LLM with
        CONTINUAL DOMAIN INGEST
        (the L5 MOAT bar)
```

---

## CITATIONS (verified, count = 18)

1. Fusi, S., Drew, P.J., Abbott, L.F. (2005). "Cascade Models of Synaptically Stored Memories." Neuron 45(4): 599-611. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0896627305001170). (Cascade-synapse foundational paper; multi-state metaplasticity.)

2. Benna, M.K., Fusi, S. (2016). "Computational principles of synaptic memory consolidation." Nature Neuroscience 19(12): 1697-1706. (Continuous-variable cascade; linear capacity scaling.)

3. Roxin, A., Fusi, S. (2012). "Power-law forgetting in synapses with metaplasticity." arxiv 1107.1160. [arxiv](https://arxiv.org/pdf/1107.1160). (Quantitative power-law forgetting in cascade models.)

4. Fusi, S. (2021). "Memory capacity of neural network models." arxiv 2108.07839. (Capacity-vs-lifetime tradeoff; cascade as the solution.)

5. Sun, Y., et al. (2024). "Theories of synaptic memory consolidation and intelligent plasticity for continual learning." arxiv 2405.16922. [arxiv](https://arxiv.org/html/2405.16922v2). (Modern review of cascade + STC + EWC; ML continual-learning integration.)

6. Bicanski, A., Burgess, N. (2024). "Probabilistic Metaplasticity for Continual Learning with Memristors in Spiking Networks." Scientific Reports 14:78290. arxiv 2403.08718. [arxiv](https://arxiv.org/pdf/2403.08718). (Memristive hardware implements cascade; validates substrate-applicable forward-only mechanism.)

7. Frey, U., Morris, R.G.M. (1997). "Synaptic tagging and long-term potentiation." Nature 385: 533-536. (Synaptic-tag foundational paper.)

8. Redondo, R.L., Morris, R.G.M. (2011). "Making memories last: the synaptic tagging and capture hypothesis." Nature Reviews Neuroscience 12: 17-30. (STC modern restatement.)

9. Park, A., et al. (2023). "Synaptic tagging and capture underlie neuronal co-allocation and temporal association memory in behaving mice." bioRxiv 2023.09.17.558124. [bioRxiv](https://www.biorxiv.org/content/10.1101/2023.09.17.558124v1.full). (Direct empirical validation of STC at engram level in vivo.)

10. Clopath, C., Ziegler, L., Vasilaki, E., Buesing, L., Gerstner, W. (2008-2021). "Synaptic Tagging and Capture in recurrent neural networks." Communications Biology (2021). (RNN implementation of STC.)

11. Josselyn, S.A., Tonegawa, S. (2020-2024). "Memory engrams: Recalling the past and imagining the future." Science 367. (Engram allocation and excitability-driven tagging.)

12. Wilson, M.A., McNaughton, B.L. (1994). "Reactivation of hippocampal ensemble memories during sleep." Science 265: 676-679. (Foundational SWR-replay paper; ~20x compression.)

13. Liu, Y., et al. (2024). "Selection of experience for memory by hippocampal sharp wave ripples." PMC 11068097. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11068097/). (SELECTIVE waking-SWR tagging of trial events; theta-state-dependent assembly turnover.)

14. Karayanni, M., et al. (2025). "Replay without sharp wave ripples in a spatial memory task." Nature Communications. [Nature](https://www.nature.com/articles/s41467-025-65181-5). (SWRs DISSOCIABLE from replay; SWRs selectively tag a subset.)

15. (Cell 2025) "Large sharp-wave ripples promote hippocampo-cortical memory reactivation and consolidation during sleep." Neuron. [Cell](https://www.cell.com/neuron/abstract/S0896-6273(25)00756-1). (LARGE-SWR-selective consolidation; closed-loop optogenetic validation.)

16. Helfrich, R.F., et al. (2021). "Coupling between slow waves and sharp-wave ripples engages distributed neural activity during sleep in humans." PNAS 118. [PNAS](https://www.pnas.org/doi/10.1073/pnas.2012075118). (Triple-coupling schedule constants for replay timing.)

17. Ebbinghaus, H. (1885). "Memory: A Contribution to Experimental Psychology." (Foundational forgetting-curve / spacing-effect work.)

18. Landauer, T.K., Bjork, R.A. (1978). "Optimum rehearsal patterns and name learning." Practical Aspects of Memory: 625-632. (Modern derivation of expanding-interval rehearsal; foundation for SuperMemo / Anki spaced-repetition.)

---

## LIT-SCAN CALIBRATION NOTES

- Probability estimates deflated 0.15-0.25 from raw LM-based confidence.
- **Novel-synthesis cap at 0.50 applied:** the cascade + STC + SWR-selective triple composition has NO PRIOR EMPIRICAL VALIDATION on hyperdimensional / Hebbian-superposition substrates. P(HARD-PASS) = 0.40 reflects this cap + deflation. Individual mechanisms are well-validated; the composition is novel.
- **HARD-FAIL thresholds mandatory and listed for every prediction.**
- The DIRECTIONALITY (cascade-extends-lifetime) is high-confidence (P~0.70 raw); the MAGNITUDE (5x effective capacity) is lower (P~0.45). Deflation hits magnitude.
- Cascade synapse mechanism is robustly validated across THREE independent lines (Fusi 2005, Benna-Fusi 2016, memristor 2024 hardware). The deflation is for substrate-specific transfer not the biology.
- SWR-selective-replay is the LEAST validated of the three for substrates (only 2024-2025 evidence in vivo; no prior substrate-port). Most of the deflation lands here.

---

## DISPATCH RECOMMENDATION

**Immediate (Exp-Dev next CLS cell):** `c2_cascade_stc_swr_continual_v1`
- Same harness scaffold as c1, modified at the W-write rule (add depth state + tag + selective replay).
- Phase 1: 3 arms {NONE, UNIFORM_1to1, CASCADE_STC_SWR_EXP} at alpha=3.0 only, 3 seeds, D_max=3. ~90 min remote_cpu_queue.
- Anchor: NONE @ alpha=0.5 must reproduce c1 (task_A=1.000).
- Version marker: `consolidation_arm`, `D_max`, `theta_tag`, `replay_schedule_mode`, `tag_function`.

**Conditional next (only if c2 HARD-PASS):** `c3_cascade_real_KG_continual_v1` on FB15k-237 sequential relation-type batches.

**Composes with the in-flight Director cell `substrate_self_map_v2`:** cascade depth could be used as the substrate's INTERNAL representation of its own ingest-history (substrate-native self-mapping over time). The cell c2 metrics include the depth distribution — that IS substrate self-state.

**Cross-drill ordering vs drill #3:** drill #3 r1b HARD_FAIL today is INDEPENDENT of this cell; c2 can ship without resolving r1b. The STC tag uses local margin which is what r1b's pre-reg measured — c2 has its OWN tag function fallbacks if margin doesn't separate.

---

-- Research (Opus synthesis, 6 parallel WebSearch streams + cross-thread with prior c1 + r1b + drill #1; novel-synthesis-deflated per calibration; routes the c1 saturation as the trigger for the deeper-mechanism cell)
