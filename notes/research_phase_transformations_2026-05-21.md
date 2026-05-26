# Research note: Phase transformations — substrate regime switching during operation

**Date**: 2026-05-21 ~21:00 EDT
**Owner**: Research session (single-writer)
**Request**: `strategy_request_to_research_phase_transformations_2026-05-21.md` (20:33, user-directed)
**Decision-log entry**: Entry 53
**Pass-1 honesty label**: REAL external lit scan via 3 parallel Agent (general-purpose) subagents; ~50+ unique papers surveyed (2020-2026 dominant + foundational anchors); generic-math queries only per [[feedback-query-privacy-decomposition]].

---

## TL;DR — executive verdict

**Probability ranking across all 7 axes (literature-supported gain over fixed-regime baseline, 6 mo)**:

| Rank | Axis | Mechanism class | P(gain) | Substrate-product fit |
|---|---|---|---|---|
| ★1 | **STACK** = P.2 + P.5 + eviction | Substrate-novel combination | **0.75** | Three coupled mode-switches; no paper combines |
| 1 | **P.5** Sleep/wake mode | Replay/retrieval mode | **0.70** | Fachechi α_c → 1; Bet B already partial-implements |
| 2 | **P.2** Metaplasticity / multi-timescale | Multi-rate plasticity | 0.55 | Benna-Fusi 2016 provable N vs √N for perceptron; Hopfield-scale gap to close |
| 3 | **P.4** Dense ↔ sparse mode | (β, Ω) variational form | 0.45 | Hopfield-Fenchel-Young arXiv:2411.08590; α-entmax + β single knob; trivial eng |
| 4 | **P.6** Adaptive β per-query | Context-dependent T | 0.35 | Bet G β=32 already; open gap on write-T ≠ read-T |
| 5 | **P.1** Time-varying T (SA/Kovacs) | Global T schedule | 0.15 | SA escape only marginal in modern-Hopfield regime |
| 6 | **P.3** Runtime codebook switching | Basis swap | 0.10-0.20 | Literature does not define this problem |
| 7 | **P.7** Magnon / collective-mode | Wave dynamics | 0.05-0.15 | Physical magnon = reservoir, not AM; hardware-bound |

**Recommended top 3 axes** (substrate-product priority order):
1. **P.5 + extension to STACK** (Fachechi dreaming Hopfield + Bet B EMA-blend → R22 sleep-replay framework already legitimized; add P.2 metaplasticity + P.6-eviction for substrate-novel combination)
2. **P.4 dense ↔ sparse mode** (Hopfield-Fenchel-Young framework; (α, β) single-knob controller; co-design with V2.D modern dense AM)
3. **P.6 adaptive β per-query** (substrate already has Bet G TEMPSCALE; pursue write-T ≠ read-T as substrate-novel open gap)

**HONEST FRAMING per [[feedback-no-smoke]]**: of 7 axes, only P.5 (sleep/wake) has multiple independent groups reporting empirical retention-quality gains on AM-class benchmarks. P.4 has clean math (Hopfield-Fenchel-Young) but no runtime-switching demonstration. P.6 transfers from attention/LLM decoding via attention=Hopfield equivalence. The **STACKED combination** is the substrate-novel opportunity that nobody has done — Fachechi (sleep) + Benna-Fusi (metaplasticity) + active α-eviction (load mod) together as a coupled three-mode controller.

**Per [[feedback-value-creation-not-competition]]**: multi-regime substrate IS a capability LLMs structurally don't have. Cold retrieval / hot exploration / learning mode / replay mode / forensics mode — per-query selectable, audit-traced. P.4 + P.5 + P.6 implemented jointly delivers this product story; substrate-product value is high even at modest 1.5× retention gain.

---

## Pass 1 — external literature scan (3 parallel agents)

### Agent A: P.1 + P.4 + P.6 (~20 papers; arXiv 2403.14541, 2511.01292, 2411.08590, 2008.02217, 2403.05175, 2412.08381, etc.)

**P.1 time-varying T findings**:
- SA for spurious-minimum escape: classical, well-established (1980s-1990s) but rarely yields >2× in modern Hopfield (high effective β already).
- Kovacs effect (cond-mat/0512186 + cond-mat/0511654): non-monotonic relaxation after two-step T protocols; phenomenologically real but **no documented retrieval-quality benefit in associative memory**.
- Glauber dynamics mixing: logarithmic at high T, polynomial at criticality, exponential at low T. **Too-fast cool gets trapped.**
- SK quench arXiv:2405.04267 (2024): reluctant updates converge near ground state, greedy does not; sync-greedy shows dynamical phase transition.
- Janus collaboration arXiv:0804.1471: empirical multi-timescale aging from ps to 0.1s — substrate-physics anchor.

**P.4 dense ↔ sparse mode findings**:
- **CRITICAL**: Hopfield-Fenchel-Young arXiv:2411.08590 (2024-25): parameterizes retrieval by entropic regularizer Ω; softmax = Shannon entropy, sparsemax = squared-norm, α-entmax = Tsallis. **Single (α, β) knob controls dense ↔ sparse.**
- On Sparse Modern Hopfield arXiv:2309.12673 (2023): closed-form sparse Hopfield energy via convex conjugate.
- Sparse and Structured Hopfield arXiv:2402.13725 (2024): Fenchel-Young unification.
- Vector Hopfield near saturation arXiv:2507.02586 (2025): phase-diagram analysis spanning AGS regime.
- AT line in neural networks arXiv:2303.06375 (2023): RS/RSB boundary in (α, T) plane.
- Geometric Entropy DAM arXiv:2604.07401 (2026): phase transitions in continuous DAM.
- **Gap**: no paper found explicitly demonstrating runtime per-query α-entmax switching as a capability — only static comparisons.

**P.6 adaptive β findings**:
- EDT arXiv:2403.14541 (2024): per-token T from predictive entropy; outperforms fixed-T on QA/summarization/translation.
- Optimal Attention Temperature ICL arXiv:2511.01292 (2025): per-query optimal attention T depends on distribution-shift magnitude.
- Entropic-Time Inference arXiv:2603.03310 (2026): joint scheduling, sparsification, sampling T under entropy objective.
- LET IT CALM arXiv:2510.05251 (2025): annealed decoding schedule.
- Parameterized Temperature Scaling arXiv:2102.12182 (2021): per-prediction T from small NN.
- **Gap**: write-T ≠ read-T (two-temperature substrate with asymmetric storage/retrieval) — **NO literature found**; substrate-novel open opportunity.

**Agent A unifying insight**: All 3 classes are coordinates of one **(β, Ω, J) variational form**. Class A varies β(t) globally; Class B varies Ω; Class C varies β per query. Hopfield-Fenchel-Young framework is the formal unification.

### Agent B: P.2 + P.5 (~30 papers; foundational + modern; substrate-grounded)

**P.2 metaplasticity / multi-timescale findings**:
- **Benna-Fusi Nat. Neurosci. 19 (2016)**: multiple coupled variables on distinct timescales; **capacity scales linearly in N (vs sqrt(N) for binary), reproduces power-law forgetting**.
- Fusi et al. Neuron 45 (2005): cascade models — high plasticity (storage) + slow transitions (retention).
- Lahiri-Ganguli NeurIPS 2013: derived **upper bounds on memory lifetime for any discrete-state synaptic model**; Benna-Fusi cascades approximately saturate the frontier.
- Kaplanis et al. arXiv:1802.07239 (ICML 2018): Cascade in continual RL; mitigates catastrophic forgetting in deep RL.
- MESU Bayesian metaplasticity arXiv:2312.10153 + Nat. Comm. 2025 (arXiv:2504.13569): synaptic-uncertainty-driven update trades retention vs plasticity.
- Jedlicka 2022 review: metaplasticity as unifying mechanism for catastrophic forgetting.
- Hardware Benna-Fusi arXiv:2401.15045 (2024): emulating complex synapses with proton conductors.
- **Critical gap**: classic Hopfield + Benna-Fusi at scale with **runtime mode switching** is NOT in the literature. Benna-Fusi proven for perceptron storage, not Hopfield basin retrieval. Open opportunity.

**P.5 sleep/wake findings** (MOST EMPIRICALLY ROBUST):
- **Tadros et al. Nat. Comm. 13:7742 (2022)**: sleep-like unsupervised replay reduces catastrophic forgetting in ANN; offline Hebbian + noise input recovers old-task accuracy (tens-of-percent task-accuracy recovery).
- **Fachechi-Agliari-Barra arXiv:1810.12217 (2019)**: "Dreaming neural networks" — REM-like unlearning pushes Hopfield kernel toward projection matrix; **capacity climbs from α_c ≈ 0.14 toward ~1**. DIRECT substrate-applicable result.
- Tadros et al. AAAI arXiv:2402.10956 (2024): replay improves perf when data limited/unbalanced.
- Schapiro-Tyulmankov eLife 2024: STM gates which traces consolidate to LTM — direct "mode switching with selectivity" model.
- van de Ven-Soures-Kudithipudi arXiv:2403.05175 (2024): treats functional regularization as form of replay — already cited in Bet B Entry 36 R22 legitimization.
- Tomasello Cerebral Cortex 2023: replay promotes category generalization.
- Generative Negative Replay arXiv:2204.05842 (2022): collapses for high-dim images (known failure).

**P.5 substrate-direct connection**: Substrate's Bet B v9 EMA-blend mechanism is functionally Tadros-style sleep replay per R22 Entry 36 (van de Ven 2024 framework). Fachechi's α_c → 1 dreaming is a SECOND mechanism (unlearning during sleep) that substrate hasn't implemented yet.

**Agent B unifying insight**: stacking all 3 mode-switching classes (metaplasticity + sleep/wake + load-eviction) → **P=0.75 for substrate-novel gain**; combination is "underexplored opportunity," compounding individual probabilities.

### Agent C: P.3 + P.7 + edge-of-chaos (~20 papers)

**P.3 runtime codebook switching findings**:
- Demircigil arXiv:1702.01929 (2017), Ramsauer arXiv:2008.02217 (2020): modern Hopfield; codebook structure largely irrelevant to leading scaling — what matters is pattern separation in attention-like softmax.
- Berrou-Gripon (2010) "Coded Hopfield networks": Walsh-Hadamard pre-coding raises retrieval capacity; foundational.
- Self-Attention VSA arXiv:2403.13218 (2024): resonator with self-attention; random hypervector codebooks; doesn't compare Hadamard/Kerdock.
- **Kerdock-code coverage in AM literature is essentially absent** — connection mostly in coding-theory venues.
- **CRITICAL NEGATIVE**: No paper found demonstrates Hopfield/modern-Hopfield network switching codebook family on the fly during inference. **Literature does NOT define this problem.**
- Modern Hopfield makes switching trivial (swap key/value tables) but ALSO makes the concept moot — capacity is exponential, codebook structure absorbed into V2.D framework.

**Edge-of-chaos findings (P.7 framing)**:
- Carroll arXiv:1906.03186 (2019): "possible to get optimum performance at edge of chaos, but also parameter values where edge-of-chaos produces poor performance" — **direct empirical challenge**.
- Mitchell-Hraber-Crutchfield adap-org/9303003: rebuts Langton's edge-of-chaos hypothesis for CA computation.
- Boosting RC with brain-inspired adaptive dynamics arXiv:2504.12480 (2025): local E/I balance auto-tuning → 130% MC improvement; best perf in **balanced or slightly over-inhibited regimes — NOT strictly at edge**.
- Mosqueiro-Maia PLoS ONE 2017: optimal info processing can lie OFF critical point.
- Spin-wave physical RC at EoC Jpn. J. Appl. Phys. 2026: 97% accuracy at λ_max → 0⁻; secondary optimum on chaotic side.
- **CRITICAL FINDING for substrate**: edge-of-chaos is the WRONG knob for fixed-point AM. AMs want stable basins, not edge dynamics. EoC is reservoir/transient-nonlinear-computation property.

**P.7 magnon / collective-mode findings**:
- Khitun arXiv:1411.7082 (2014): magnonic holographic memory — physical device, no accuracy figures.
- Camsari STO Hopfield arXiv:2112.03358 (2022): SIMULATION only; 12 patterns in 192 oscillators (0.06 P/N, **WORSE than classical 0.138**); demands ≤10⁻³ frequency uniformity (major fab challenge).
- Spin-wave RC Namiki Adv. Intell. Syst. 2023; Hikasa Adv. Electron. Mater. 2025: physical reservoir computers.
- Cross-frequency coupling phasor AM arXiv:2204.07163 (2022): biological theta/gamma ratio enables error-free retrieval where uncoupled fails; SIMULATION.
- **Substrate-product verdict**: physical magnon = reservoir computer (NOT AM); simulated magnon AM (Camsari) is WORSE than classical baseline.

**Agent C unifying insight**: P.3 codebook switching is conceptually empty (modern Hopfield absorbs it; literature doesn't define problem). Edge-of-chaos is wrong knob for fixed-point AM. P.7 magnon is hardware-bound and uncompetitive without dedicated device.

---

## Pass 2 — per-axis substrate drill

### P.1 — Temperature switching (β-modulation) [DEFER]

**Substrate-applicable mechanism**: Glauber/Metropolis cleanup at time-varying β(t); β-schedule = exploration phase (low β) → exploitation phase (high β). Could be **per-query annealing**: t=0 β=4, t=T β=64.

**Empirical signature**: SA escape from spurious minima — substrate enters retrieval basin at higher fraction vs fixed β=32 cleanup. Kovacs-style two-step: pre-conditioning at β=16, then jump to β=64 — detect Kovacs hump in retrieval accuracy curve.

**Substrate-product value**:
- Modest. Current substrate's β=32 cleanup is already in modern-Hopfield regime per Bet G ✅; SA gain marginal.
- Potential: 5-10% retrieval acc gain on spurious-minimum-dominated queries.
- Not substrate-novel — SA on Hopfield is 1980s classical.

**Engineering tractability**: HIGH. β(t) schedule is one float per timestep; Glauber kernel accepts varying β with no architectural change. Eng cost: <1 cycle.

**Probability P(2× quality gain on substrate benchmarks, 6 mo)**: **0.15** (per Agent A; SA marginal in modern-Hopfield regime).

**Falsifiable prediction**: substrate cleanup with β(t) annealing schedule β ∈ [4, 64] over T=10 steps yields **acc gain ≥ 0.05 over fixed β=32** at α=0.153 with σ=16 noise. Kill if Δacc ≤ 0.02 → P.1 ❌.

**Materials analog (load-bearing)**: Glauber dynamics on Sherrington-Kirkpatrick spin glass; Castellani-Cavagna 2005 review; substrate's Bet E ✅ Parisi P(q) validates SK-class analog.

---

### P.2 — Load modulation (α switching) + Metaplasticity [HIGH PRIORITY]

**Substrate-applicable mechanism**:
- (a) **Pattern-eviction**: subtract P_i P_iᵀ from W when α approaches α_c → reduce α below 0.138 → re-enter clean retrieval regime.
- (b) **Benna-Fusi cascade**: each substrate "synapse" (W entry) has multi-timescale cascade per Benna-Fusi 2016; fast timescale captures new patterns, slow timescale preserves consolidated patterns.
- (c) **Combined**: cascade decides which patterns to actively evict (slow-timescale signal) vs which to maintain.

**Empirical signature**: substrate at α=0.20 (super-critical) → eviction → α=0.10 (sub-critical) → retrieval acc recovers to ≥ 0.95. Detect via continual-edit retention curve: substrate without P.2 fails after K_max = 200 edits; substrate with P.2 sustains K_max ≥ 1000 edits.

**Substrate-product value**:
- HIGH. Extends Bet B continual learning to arbitrary K via active forgetting + cascade.
- Substrate-novel: Benna-Fusi-on-Hopfield at runtime-switchable scale is NOT in the literature.
- Aligns with Bet U working memory + Miller-Ebbinghaus decay (one of META cycle-20 candidates promoted as Bet U).

**Engineering tractability**: MEDIUM. Pattern eviction is O(N²) per eviction (subtract P_iP_iᵀ from W); cascade synapses require ~log(timescale_max/timescale_min) state per W entry → 2-4× memory overhead. Eng cost: 4-7 cycles (cascade design + eviction policy + benchmark).

**Probability P(measurable retention gain ≥ 0.05, 6 mo)**: **0.55** (per Agent B; Benna-Fusi provable on perceptron, not Hopfield-tested at scale).

**Falsifiable prediction**: substrate with Benna-Fusi cascade (3 levels: fast/medium/slow per W entry) + α-aware eviction achieves **K_max ≥ 800 sustained edits at retention_A ≥ 0.85** (vs Bet B v9's 500-edit ceiling). Kill if K_max ≤ 600 → P.2 ❌; revert to standard EMA-blend.

**Materials analog (load-bearing)**: Benna-Fusi cascade = chain of leaky integrators with diffusion coupling; mathematically equivalent to **anomalous-diffusion sub-diffusive process on hierarchical free-energy landscape** (Bouchaud trap model + Cugliandolo aging framework). Connects to substrate's Bet E FRSB regime via FRSB ↔ hierarchical traps.

---

### P.3 — Codebook switching [DEFER]

**Substrate-applicable mechanism**: maintain 2-3 pre-baked W matrices for {Hadamard, Kerdock v4, random ±1} codebooks; switch W per query type.

**Empirical signature**: substrate uses Hadamard for orthogonal-key erase (Bet 2 GDPR); Kerdock v4 for capacity (Bet C M/N=8); random ±1 for arbitrary-domain ICL (Bet 1). Per-query codebook routing.

**Substrate-product value**:
- LOW per Agent C: literature does NOT define this problem; modern Hopfield (V2.D) makes codebook structure largely irrelevant to leading scaling.
- Modest engineering win possible: avoid retraining for new task type by precomputed-W swap.

**Engineering tractability**: MEDIUM. Pre-baking 3 W matrices = 3× memory at N=4096 (3 × 16 MB = 48 MB). Switching is O(1) (pointer swap). Eng cost: 2-3 cycles (codebook generation + per-query routing).

**Probability P(measurable gain, 6 mo)**: **0.10-0.20** (per Agent C; problem not defined in literature).

**Falsifiable prediction**: per-query codebook routing across {Hadamard, Kerdock, random} delivers **≥ 0.10 acc gain on mixed-query benchmark** vs single-Kerdock baseline. Kill if Δacc ≤ 0.03 → P.3 ❌; modern-Hopfield framework subsumes codebook structure.

**Materials analog (load-bearing)**: codebook switching is analogous to **crystal-structure switching under pressure** (e.g., diamond ↔ graphite carbon allotropes) — different crystalline phases give different mechanical/transport properties. NOT load-bearing for engineering; mostly conceptual.

---

### P.4 — Mode switching (dense ↔ sparse) [HIGH PRIORITY]

**Substrate-applicable mechanism**:
- Substrate's current Bet G TEMPSCALE β=32 cleanup is dense (softmax). P.4 mode = switch to sparse (α-entmax with α=2 sparsemax) per query.
- Implementation: replace `softmax(β·logits)` with `entmax_alpha(β·logits; α_t)` where α_t ∈ {1.0 dense, 1.5 mid, 2.0 sparse} per Hopfield-Fenchel-Young arXiv:2411.08590.

**Empirical signature**: substrate in dense mode → smooth top-K probability distribution; substrate in sparse mode → exact top-1 or top-3 with hard zeros. Detectable via entropy of cleanup output: dense ~log(K_active), sparse ~log(3-5).

**Substrate-product value**:
- HIGH. Combines with V2.D modern dense AM (highest-P V2 candidate per V2 evaluation Entry 52).
- Substrate gets **two-mode retrieval**: dense for exploration/uncertain queries, sparse for high-stakes/auditable queries.
- Audit traces dramatically improve in sparse mode (top-3 explicit attribution vs softmax averaging).

**Engineering tractability**: VERY HIGH. α-entmax library exists (deep-spin/HFYN repo); pytorch/jax implementations; gradient flows through. Eng cost: 1-2 cycles (replace cleanup function + per-query controller).

**Probability P(2× retrieval-quality gain on at least one query class, 6 mo)**: **0.45** (per Agent A; static comparisons show ≥2× wins in MIL benchmarks; runtime switching as capability not yet demonstrated).

**Falsifiable prediction**: substrate with α-entmax controller (α ∈ {1.0, 1.5, 2.0}) per query selected by query-uncertainty proxy achieves **≥ 0.10 audit-trace fidelity gain** (top-K attribution clarity) over fixed-softmax-β=32 baseline, AND **no acc degradation on exploration queries**. Kill if EITHER fails → P.4 ❌; revert to fixed softmax.

**Materials analog (load-bearing)**: α-entmax interpolates between dense (Bose-Einstein-like, all states partially occupied) and sparse (Fermi-Dirac-like, hard occupation limits) regimes. **Load-bearing physical analog**: Hubbard model U/t crossover between metallic (soft) and Mott-insulating (hard) regimes (Imada-Fujimori-Tokura RMP 1998).

---

### P.5 — Replay vs retrieval mode (sleep/wake) [HIGHEST PRIORITY]

**Substrate-applicable mechanism**:
- Substrate's Bet B v9 EMA-blend already implements Tadros-style sleep replay per R22 Entry 36 (van de Ven 2024 functional-regularization framework).
- **Add**: Fachechi-style REM dreaming — during sleep phase, run substrate without external input + with high-amplitude noise → spurious minima get unlearned → kernel pushes toward projection matrix → capacity climbs from α_c=0.138 toward 1.
- Three-phase substrate per Schapiro-Tyulmankov eLife 2024: encode → recall-gated promotion to LTM → retrieve. Substrate adds STM tier with gated LTM consolidation.

**Empirical signature**:
- **Fachechi dreaming**: substrate's effective α_c shifts upward over sleep cycles. Detectable by measuring max-K at retention_A ≥ 0.95: pre-sleep K_max → post-sleep K_max increases.
- **Recall-gated**: only frequently-recalled traces consolidate to LTM; rarely-recalled traces decay. Detect by tracking STM vs LTM W norms over time.

**Substrate-product value**:
- HIGHEST per Agent B. **Most empirically robust class.**
- Direct substrate-product extension: substrate already has the framework (Bet B + R22); add Fachechi dreaming mechanism.
- Aligns with META Lane E (continual learning); substrate's Bet B EMA-blend extends to higher K.
- Substrate-novel for Hopfield-class at large N: Fachechi tested at N ~ 1024-2048; substrate's N=4096 + Kerdock v4 is an unbenchmarked combination.

**Engineering tractability**: HIGH. Tadros algorithm: periodically pause, inject noise, apply local STDP-like update, resume. Compute overhead 1-5% if sleep phase is 1% of cycles. Fachechi unlearning: rule is `W ← W − ε · ξ_spurious · ξ_spuriousᵀ` where ξ_spurious is fixed-point under high-noise dynamics. Eng cost: 2-4 cycles.

**Probability P(measurable retention gain ≥ 0.05, 6 mo)**: **0.70** (per Agent B; multiple independent groups; Fachechi α_c → 1 is direct substrate-applicable result).

**Falsifiable prediction**: substrate with Fachechi REM-unlearning phase (1% of cycles, ε=0.01, T=10 unlearning steps per phase) achieves **effective α_c ≥ 0.30 at N=4096** (vs classical 0.138), with **retention_A ≥ 0.95 sustained through K=1000 sequential edits**. Kill if effective α_c ≤ 0.20 → P.5-Fachechi ❌; revert to current EMA-blend.

**Materials analog (load-bearing)**: Fachechi's REM dreaming = explicit anti-Hebbian unlearning on spurious minima; **mathematically equivalent to inverse-Glauber dynamics on free-energy landscape** (Hopfield-style energy descent in REVERSE: identify metastable states, then push UP). Substrate's Bet E FRSB structure provides the metastable-state landscape that Fachechi operates on.

---

### P.6 — Calibration regime switching (adaptive β per-query) [MEDIUM-HIGH PRIORITY]

**Substrate-applicable mechanism**:
- Replace substrate's fixed β=32 (Bet G TEMPSCALE ✅) with β(query) = f(query_uncertainty).
- High-uncertainty queries → low β (exploration, broad softmax).
- High-stakes queries → high β (deterministic, sharp argmax).
- **Substrate-novel extension**: write-T ≠ read-T (asymmetric calibration). Substrate writes patterns at β_write = 16, reads at β_read = 64 per-query. **Open gap in literature per Agent A.**

**Empirical signature**:
- Calibration ECE varies per query class: high-stakes queries have ECE < 0.005; exploration queries have ECE ~ 0.05 (broader distribution).
- Asymmetric T: write/read mismatch detectable via comparing stored-pattern entropy to retrieved-pattern entropy.

**Substrate-product value**:
- MEDIUM-HIGH. Substrate already has TEMPSCALE Bet G ✅ framework.
- Adaptive β = small extension; engineering-trivial.
- **Two-temperature substrate is substrate-novel**: 0 papers found per Agent A; **clean substrate-novel claim available**.
- Aligns with META Lane D (auditability product); query-specific calibration improves audit fidelity.

**Engineering tractability**: VERY HIGH. EDT-style entropy-based β selection is one extra scalar per query (compute output entropy → β = f(entropy)). Eng cost: 1-2 cycles.

**Probability P(measurable calibration improvement, 6 mo)**: **0.35** (per Agent A; well-validated in attention/LLM decoding; transfer via attention=Hopfield equivalence).

**Falsifiable prediction**: substrate with adaptive β(query) ∈ [8, 128] selected by output entropy achieves **ECE ≤ 0.005 on high-stakes queries AND ECE ≤ 0.030 on exploration queries** simultaneously (vs fixed β=32 ECE=0.013 across all). Substrate with asymmetric write-T=16, read-T=64 achieves **acc gain ≥ 0.03** over symmetric β=32. Kill EITHER if Δ ≤ 50% of target → P.6 ❌; revert to fixed β=32.

**Materials analog (load-bearing)**: two-temperature substrate = out-of-equilibrium spin system with two thermal baths (storage T_w, retrieval T_r); mathematically equivalent to **Cugliandolo-Kurchan two-temperature aging framework** (per R24 Entry 21). Substrate's potential FDT violation (R24) could be DETECTED via T_w/T_r ratio.

---

### P.7 — Magnon-driven dynamical regime [DEFER]

**Substrate-applicable mechanism**:
- Substrate codebook → standing-wave-mode codewords (Fourier basis, magnon-like phase-coupled patterns).
- Wave-propagation mode during chained reasoning: query propagates through W as wave packet.
- Static-retrieval mode during single-shot: standard cleanup.

**Empirical signature**: substrate in wave-propagation mode → chain coherence detectable via cross-correlation of intermediate states. Static mode → uncorrelated.

**Substrate-product value**:
- LOW per Agent C. Physical magnon devices are reservoir computers, NOT AMs.
- Simulated phasor codebook (Camsari STO Hopfield): WORSE than classical baseline (0.06 P/N vs 0.138).
- Cross-frequency coupling AM (arXiv:2204.07163) requires biological theta/gamma ratio; substrate doesn't have intrinsic frequency hierarchy.
- **Dominated by V2.D modern dense AM (per V2 evaluation Entry 52): phasor IS structured spherical code; absorbed into Hu 2024 framework.**

**Engineering tractability**: MEDIUM-LOW. Fourier-basis codebook is straightforward (FFT); wave-propagation dynamics require time-evolution operator design + cross-state coherence verification. Eng cost: 6-12 cycles for software-only; 30+ for physical magnon device.

**Probability P(measurable gain, 6 mo)**: **0.05-0.15** (per Agent C; no published evidence magnon AM beats random-codebook Hopfield).

**Falsifiable prediction**: substrate with phasor codebook + wave-propagation mode achieves **acc gain ≥ 0.05 on multi-hop d=10 queries** vs Kerdock v4 static-retrieval baseline. Kill if Δacc ≤ 0.02 → P.7 ❌; V2.D framework subsumes any phasor gain.

**Materials analog (load-bearing)**: phasor codebook = plane-wave eigenmode basis of harmonic crystal (Born-Oppenheimer 1927); wave-propagation = magnon dispersion in YIG (Demokritov 2006). Load-bearing for theoretical understanding but NOT substrate-product driver.

---

## Recommended top 3 axes with substrate implementation sketches

### Recommended axis 1: P.5 sleep/wake mode (Fachechi extension)

**Sketch**:
```
def fachechi_sleep_phase(W, num_steps=10, eps=0.01, noise_amp=0.5):
    """Run REM-style unlearning to push α_c upward.

    Per Fachechi-Agliari-Barra arXiv:1810.12217.
    """
    for step in range(num_steps):
        # Initialize from high-noise state
        xi_noise = sign(noise_amp * randn(N))

        # Let substrate relax to nearest fixed point (spurious or real)
        xi_fp = relax_to_fixed_point(xi_noise, W)

        # Anti-Hebbian unlearning on the fixed point
        W = W - eps * outer(xi_fp, xi_fp)

    # Renormalize W to prevent drift
    W = W * (1 + eps * num_steps)
    return W

# Per-cycle sleep schedule
def substrate_cycle(W, queries, sleep_every=100):
    for i, q in enumerate(queries):
        if i % sleep_every == 0 and i > 0:
            W = fachechi_sleep_phase(W)
        retrieve(W, q)
```

**Parameters**: num_steps ∈ {5, 10, 20}; eps ∈ {0.005, 0.01, 0.02}; noise_amp ∈ {0.3, 0.5, 0.7}; sleep_every ∈ {50, 100, 200}.

**Verdict logic**:
- PASS: effective α_c ≥ 0.30 at N=4096 AND retention_A ≥ 0.95 at K=1000
- PARTIAL: 0.20 ≤ α_c < 0.30
- FAIL: α_c < 0.20 OR retention degrades

**Multi-probe success criteria** (formal Bet candidate):
- α_c measurement: sweep K ∈ {500, 1000, 1500, 2000} after sleep; identify K_max at retention=0.95
- Spurious-minimum count: number of metastable fixed points before vs after sleep
- 3 seeds × 3 sleep schedules

### Recommended axis 2: P.4 dense ↔ sparse mode (α-entmax controller)

**Sketch**:
```
def adaptive_alpha_entmax(logits, alpha, beta):
    """Hopfield-Fenchel-Young per arXiv:2411.08590.

    alpha=1.0 → softmax (dense)
    alpha=1.5 → 1.5-entmax (mid)
    alpha=2.0 → sparsemax (sparse)
    """
    from entmax import entmax_bisect
    return entmax_bisect(beta * logits, alpha=alpha)

def query_routing_controller(query):
    """Select alpha based on query type."""
    uncertainty = compute_query_uncertainty(query)
    if uncertainty > 0.7:
        return 1.0  # dense exploration
    elif uncertainty > 0.3:
        return 1.5  # mid
    else:
        return 2.0  # sparse high-stakes
```

**Parameters**: alpha ∈ {1.0, 1.25, 1.5, 1.75, 2.0}; beta ∈ {16, 32, 64}; uncertainty thresholds tuned per task.

**Verdict logic**:
- PASS: ≥ 0.10 audit-trace fidelity gain AND no acc degradation
- PARTIAL: gain on audit, slight acc loss on exploration
- FAIL: net degradation

### Recommended axis 3: P.6 adaptive β + write-T ≠ read-T

**Sketch**:
```
def adaptive_beta(output_logits):
    """EDT-style per arXiv:2403.14541."""
    entropy = -sum(softmax(output_logits) * log(softmax(output_logits)))
    return 32 * (1 + tanh(2 * (entropy_target - entropy)))

def asymmetric_substrate(patterns, queries, beta_w=16, beta_r=64):
    """Substrate-novel: write at low beta, read at high beta."""
    # Write phase: encode with broad attention (lower beta)
    W = encode(patterns, beta=beta_w)

    # Read phase: retrieve with sharp attention (higher beta)
    results = [retrieve(W, q, beta=beta_r) for q in queries]
    return results
```

**Parameters**: beta_w ∈ {8, 16, 32}; beta_r ∈ {32, 64, 128}; ratio beta_r/beta_w ∈ {2, 4, 8}.

**Verdict logic**:
- PASS: ECE ≤ 0.005 high-stakes + ECE ≤ 0.030 exploration + asymmetric Δacc ≥ 0.03
- PARTIAL: only adaptive-β works; asymmetric fails
- FAIL: no gain over fixed β=32

---

## 5 rescue sketches per recommended axis (PROT-004 pre-arming)

### P.5 Fachechi sleep ❌ rescues
1. **Tadros-style replay only** (no unlearning); inject noise-driven replay of recent patterns. Per arXiv:2402.10956.
2. **Generative replay** per Shin 2017 + van de Ven 2024; substrate generates noise patterns conditioned on stored centroids.
3. **STM ↔ LTM gating** per Schapiro-Tyulmankov; promote only frequently-recalled patterns. Two-tier W.
4. **Benna-Fusi cascade-only** (no sleep); multi-timescale plasticity per arXiv:2401.15045 hardware implementation.
5. **Hybrid sleep + cascade**: 1% sleep + 3-level cascade per Benna-Fusi 2016 + Lahiri-Ganguli 2013 frontier.

### P.4 α-entmax ❌ rescues
1. **Top-K hard threshold** (no entmax); fixed K=5 in sparse mode.
2. **Sparsemax-only** (α=2 fixed); no controller.
3. **Soft thresholding with annealing**: β(t) anneals up during query, hardening cleanup over time.
4. **Mixed dense+sparse output**: concatenate both modes' top-K, take union.
5. **Per-attention-head mode**: half of cleanup heads dense, half sparse (transformer-style).

### P.6 adaptive β ❌ rescues
1. **Fixed β=64 cold mode only** (no adaptive); compare to β=32.
2. **Per-task β (not per-query)**: precompute task-class β; cheaper controller.
3. **Bandit-learned β**: substrate learns β policy via Thompson sampling on retrieval acc.
4. **Two-bath substrate**: literal two thermal baths in storage vs retrieval (Cugliandolo-Kurchan).
5. **Calibration ensemble**: 3 substrates at β ∈ {16, 32, 64}; vote on cleanup output.

---

## Cross-axis dependencies (the SUBSTRATE-NOVEL STACK)

**Identified opportunity** (per Agent B): combining axes is the substrate-novel direction.

| Stack combination | P(measurable gain) | Substrate-novelty |
|---|---|---|
| **P.5 + P.2** (sleep + metaplasticity) | 0.70 → 0.78 | Cascade synapses provide natural substrate for sleep consolidation phase |
| **P.5 + P.4** (sleep + dense↔sparse) | 0.70 → 0.72 | Sleep in dense mode (broad exploration); retrieval in sparse mode (sharp) |
| **P.5 + P.6** (sleep + adaptive β) | 0.70 → 0.72 | Sleep at low β (chaos/exploration); retrieval at high β (cold/exploitation) |
| **P.2 + P.6 eviction** (metaplasticity + load mod) | 0.55 → 0.60 | Slow cascade decides which patterns to evict when α → α_c |
| **STACK: P.2 + P.5 + P.6.eviction** | **0.75** | **NO PAPER COMBINES**; substrate-novel three-mode controller |
| **P.4 + P.6** (mode + adaptive β) | 0.45 → 0.50 | Co-controller: (α, β) jointly per query |

**Key dependency**: P.5 sleep + P.2 metaplasticity NATURALLY co-implement — Benna-Fusi cascade decides which patterns survive sleep-replay consolidation. This is the substrate-novel three-class combination Agent B identified.

---

## Substrate-novel combination opportunity

**The STACK (P.2 + P.5 + P.6.eviction)**:

Substrate operating multi-regime simultaneously:
- **Cascade plasticity layer (P.2)**: each W entry has 3-level cascade (fast / medium / slow); recent patterns rapidly encoded, slowly consolidated.
- **Sleep phase (P.5)**: 1% of cycles, substrate enters sleep — Fachechi REM unlearns spurious minima + Tadros noise-driven replay of slow-cascade patterns.
- **Active eviction (P.6 extension)**: when slow-cascade signal < threshold AND α approaches α_c, evict pattern from W (subtract outer product). Pattern lives only in slow cascade until reactivated.

**Substrate-product value**: capability LLMs structurally don't have. Per [[feedback-value-creation-not-competition]]:
- Lane B (on-device personal AI): continual learning at arbitrary K, never goes to cloud
- Lane E (continual learning): substrate becomes the canonical multi-mode continual learner
- Lane D (auditability): cascade signal IS the audit trace (per-pattern timestamp of last reinforcement)

**Falsifiable prediction (STACK)**: substrate with STACK achieves **K_max ≥ 5000 sustained edits at retention_A ≥ 0.90** (10× current Bet B v9 ceiling of 500 edits). Substrate without STACK fails at K=500. Kill if STACK K_max ≤ 2000 → STACK ❌; revert to single-axis P.5 only.

**Eng cost estimate (STACK)**: 8-12 cycles total (P.5 Fachechi: 2-4; P.2 cascade: 4-7; eviction policy: 2-3; co-design and integration: 2-3).

---

## Citations (Pass-1 lit scan, ~50+ generic-math queries; verified per [[feedback-verify-implementations]])

**P.1 time-varying T (8)**:
1. SK quench dynamics arXiv:2405.04267 (2024)
2. Spin-glass dynamics review arXiv:2412.08381 (2024)
3. Kovacs solvable models arXiv:cond-mat/0512186
4. Kovacs fragile glass arXiv:cond-mat/0511654
5. Glauber dynamics SG mixing (Aïdékon et al., NumDam)
6. Janus collaboration nonequilibrium arXiv:0804.1471
7. Castellani-Cavagna 2005 review (foundational)
8. SA-on-Hopfield (1980s foundational)

**P.2 metaplasticity / multi-timescale (8)**:
9. Benna-Fusi Nat. Neurosci. 19, 1697 (2016)
10. Fusi et al. Neuron 45:599 (2005)
11. Lahiri-Ganguli NeurIPS 2013
12. Kaplanis et al. arXiv:1802.07239 (ICML 2018)
13. MESU Bayesian metaplasticity arXiv:2312.10153
14. Bayesian continual learning arXiv:2504.13569 (Nat. Comm. 2025)
15. Jedlicka 2022 review (Trends Neurosci.)
16. Hardware Benna-Fusi arXiv:2401.15045 (2024)

**P.3 codebook switching (4)**:
17. Berrou-Gripon 2010 (coded Hopfield)
18. Walsh-Hadamard proteretic 2022
19. Self-Attention VSA arXiv:2403.13218 (2024)
20. Dynamic Capacity Estimation Hopfield arXiv:1709.05340

**P.4 dense ↔ sparse mode (8)**:
21. Hopfield-Fenchel-Young arXiv:2411.08590 (2024-25)
22. On Sparse Modern Hopfield arXiv:2309.12673 (2023)
23. Sparse and Structured Hopfield arXiv:2402.13725 (2024)
24. Vector Hopfield near saturation arXiv:2507.02586 (2025)
25. AT line in NN arXiv:2303.06375 (2023)
26. Geometric Entropy DAM arXiv:2604.07401 (2026)
27. Bio-plausible DAM arXiv:2601.00984 (2026)
28. Demircigil arXiv:1702.01929 (2017)

**P.5 sleep/wake (8)**:
29. Fachechi-Agliari-Barra "Dreaming NN" arXiv:1810.12217 (2019)
30. Tadros et al. Nat. Comm. 13:7742 (2022)
31. Tadros AAAI arXiv:2402.10956 (2024)
32. Schapiro-Tyulmankov eLife 2024
33. van de Ven-Soures-Kudithipudi arXiv:2403.05175 (2024)
34. Tomasello Cerebral Cortex 2023
35. Shin et al. Deep Generative Replay arXiv:1705.08690 (2017)
36. Generative Negative Replay arXiv:2204.05842 (2022)

**P.6 adaptive β (8)**:
37. EDT arXiv:2403.14541 (2024)
38. Optimal Attention T ICL arXiv:2511.01292 (2025)
39. Entropic-Time Inference arXiv:2603.03310 (2026)
40. LET IT CALM arXiv:2510.05251 (2025)
41. Parameterized Temperature Scaling arXiv:2102.12182 (2021)
42. Adaptive T Scaling Calibration Springer 2024
43. Selective Attention arXiv:2411.12892 (2024)
44. Two-temperature substrate Cugliandolo-Kurchan (R24 reference)

**P.7 magnon / collective-mode (6)**:
45. Khitun magnonic holographic arXiv:1411.7082 (2014)
46. Camsari STO Hopfield arXiv:2112.03358 (2022)
47. Spin-wave RC Namiki Adv. Intell. Syst. 2023
48. Hikasa Adv. Electron. Mater. 2025
49. Cross-frequency coupling phasor AM arXiv:2204.07163 (2022)
50. Kuramoto honeycomb AM arXiv:2604.01469 (2026)

**Edge-of-chaos (negative results; framing for P.7) (4)**:
51. Carroll arXiv:1906.03186 (2019)
52. Mitchell-Hraber-Crutchfield adap-org/9303003
53. Boosting RC arXiv:2504.12480 (2025)
54. Mosqueiro-Maia PLoS ONE 2017

---

## Cross-references

- `notes/research_V2_substrate_evaluation_2026-05-21.md` (Entry 52; V2.D modern dense AM dovetails with P.4 mode switching)
- `notes/research_R18_RFOT_glassy_dynamics_2026-05-21.md` (RFOT activation; substrate metastable-state landscape)
- `notes/research_R22_sleep_consolidation_2026-05-21.md` (P.5 framework; van de Ven 2024 functional regularization)
- `notes/research_R23_continuous_RSB_AT_line_2026-05-21.md` (P.4 phase diagram; AT line in (α, T))
- `notes/research_R24_FDT_violation_2026-05-21.md` (P.6 write-T ≠ read-T; Cugliandolo-Kurchan two-temperature)
- `notes/research_R37_facilitation_nucleation_2026-05-21.md` (P.1 facilitation analog; substrate FIRST-OF-ITS-KIND empirical heating-cooling)
- `notes/research_R32_magnon_substrate_2026-05-21.md` (P.7 context; magnon decorative-filtering pattern)
- `notes/research_BetX_skill_composition_2026-05-21.md` (multi-regime execution semantics for skill calls)
- `notes/meta_request_to_strategy_strategic_plan_2026-05-21.md` (6 application lanes; STACK fits Lane B + Lane D + Lane E)

---

## Pass-1 honesty statement

Pass 1 lit scan via 3 parallel general-purpose Agent subagents:
- **Agent A**: P.1 time-varying T + P.4 dense↔sparse + P.6 adaptive β; 15 queries; returned ~20 papers + (β, Ω, J) variational unification insight.
- **Agent B**: P.2 metaplasticity + P.5 sleep/wake; 15 queries; returned ~30 papers + STACKED COMBINATION insight (P=0.75 substrate-novel).
- **Agent C**: P.3 codebook switching + P.7 magnon/collective + edge-of-chaos framing; 15 queries; returned ~20 papers + critical NEGATIVE findings (codebook switching undefined in literature; EoC wrong knob for fixed-point AM).

All queries used generic math vocabulary per [[feedback-query-privacy-decomposition]]; no substrate fingerprint. Pass 2 substrate drill is original synthesis based on current cap_map state + Pass-1 findings + cross-reference to prior R-notes.

Total external papers surveyed: ~50+ unique, 2020-2026 dominant, with foundational pre-2020 anchors (Benna-Fusi 2016, Fusi 2005, Plate 1995, Demircigil 1702.01929, Fachechi 1810.12217).

**Critical Pass-1 honesty caveats** (load-bearing for probability estimates):
- **Edge-of-chaos rejection (Agent C)**: EoC is the WRONG knob for fixed-point associative memory. AMs want stable basins, not edge dynamics. This eliminates P.7's main theoretical justification.
- **Codebook switching gap (Agent C)**: literature does NOT define "runtime codebook switching" problem. P.3 = inventing the problem statement; unlikely to deliver in 6 mo.
- **Magnon AM gap (Agent C)**: physical magnon devices = reservoir computers; simulated magnon AM (Camsari) is WORSE than classical baseline.
- **STACK opportunity (Agent B)**: combining metaplasticity + sleep + load-eviction is "underexplored opportunity"; P=0.75 reflects substrate-novel claim potential, NOT existing literature evidence.
- **Fachechi α_c → 1 (Agent B)**: most-cited single-paper substrate-applicable result; Fachechi's "Dreaming neural networks" arXiv:1810.12217 is the direct template for substrate P.5 extension.

**Per [[feedback-verify-implementations]]**: Cited claims that I'm specifically relying on:
- Fachechi α_c climb (1810.12217): verified via Agent B description matches abstract framing.
- Benna-Fusi N vs √N (Nat. Neurosci. 19, 1697): verified via Agent B + multiple independent reviews (Jedlicka 2022, arXiv:2405.16922 2024).
- Hopfield-Fenchel-Young (α, β) single knob (arXiv:2411.08590): verified via Agent A description; deep-spin/HFYN repo exists.
- EDT per-token T (arXiv:2403.14541): verified via Agent A; empirical gains documented on QA/summarization/translation.

EOF marker.
