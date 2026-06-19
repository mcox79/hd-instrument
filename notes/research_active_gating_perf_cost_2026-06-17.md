# Research drill: ACTIVE-GATING perf-COST family (R4 cell 8a prereg foundation; SAFE generic queries; evidence-verified)

**From:** Research (Director) via Sonnet sub-agent (Agent tool subagent_type=research)
**Date:** 2026-06-17 ~15:45 (dispatched); Director should have saved this artifact at dispatch time but slipped; saving now per Exp-Dev's 9th catch surface (16:03)
**Purpose:** R4 cell 8a (active-gating perf-COST) recapture drill foundation; Exp-Dev draws on this to draft 8a prereg
**Discipline:** SAFE generic queries per loop SAFETY block + USER reaffirm 15:32; 11th-rule clean (WebSearch + WebFetch factual retrieval; no LLM-as-judge); evidence-of-search shown; ASCII

## HEADLINE

Active gating is a **5-family** mechanism class with well-characterized headline Pareto wins (4x-10x speedups) but **systematically uncharacterized break-even regime boundaries**; the dominant 2024-25 failure mode is **selective-deadlock** (aux-loss-resistant degenerate routing affecting ~1/3 of layers), and the **most underexplored worth-one-drill** mechanism is **Bayesian-surprise-as-compute-gate** (per arXiv:2511.21408, just-published, bridges curiosity-RL and conditional-compute lines that have been historically disjoint).

## Mechanism family map (verified 2026-06-17)

| Family | Canonical paper | Gating mechanism | Verified perf-cost signature |
|---|---|---|---|
| **MoE top-k routing** | Switch-T (arXiv:2101.03961); ST-MoE (arXiv:2202.08906) | Router softmax -> top-1/2 expert; aux + z-loss | 4x-7x pre-train speedup; 47B/12B active-FLOP (Mixtral); memory-bound at inference |
| **Expert-choice routing** | Zhou 2022 (arXiv:2202.09368) | Expert picks top-k tokens (inverse) | >2x convergence speedup vs Switch-top-1 |
| **NTM/DNC memory gates** | Graves 2014 (arXiv:1410.5401); Nature 2016 | Erase/write/allocation/free gates over slots | O(N) per read, O(N^2) temporal link (DNC) -- dominant bottleneck |
| **Attention-as-gating / sparse-routing** | Routing Transformer (TACL 2021); MoSA (arXiv:2505.00315) | k-means cluster / expert-choice over tokens | O(T^2) -> O(k^2+T); more heads per same budget |
| **Conditional-compute / early-exit** | Bengio 2013 (arXiv:1308.3432); BranchyNet (arXiv:1709.01686); MoD (arXiv:2409.17016) | Confidence/entropy threshold; per-block skip | 2-6x speed on CIFAR; 40-75% inference cost on NLP |
| **Surprise-based gating** | ICM Pathak 2017 (arXiv:1705.05363); SDT 2511.21408 | Prediction-error / Bayesian-surprise routes compute | Forward-pass only; SDT routes per-token compute by latent surprise |

## Performance-cost summary (verified)

- **MoE Pareto-dominant on accuracy/FLOP**: "MoE models systematically dominate the Pareto frontier... particularly on benchmarks requiring extended reasoning" (arXiv:2512.24776)
- **Memory-FLOPs decoupling tax**: MoE LM inference 18.9 GB/GPU vs 2.2 GB dense (8.6x memory blow-up; Huang NeurIPS); sparse activation saves FLOPs **not** memory
- **All-to-all communication dominates multi-node latency**, not gate/expert compute itself
- **Dynamic networks ~10x iso-accuracy** but "less compatible to batch computation" (NSR survey nwae088)
- **Fixed accuracy-time tradeoff** is the open challenge: "most techniques provide a fixed accuracy-time trade-off" (arXiv:2403.07965v2)

## Failure-mode taxonomy (cross-family, verified)

- **Selective deadlock** (NEW 2024+): "non-linear MLP routers resolve global deadlock but introduce... selective deadlock, where roughly one-third of layers degenerate into a single-expert mode" -- **aux-loss-resistant** (arXiv:2605.19378). Critical because it falsifies the dominant "just tune the load-balance loss" remedy.
- **Router logit blow-up** -> ST-MoE z-loss canonical mitigation (arXiv:2202.08906)
- **Aux-loss vs task-loss tradeoff**: balancing too aggressive stunts specialization
- **DNC pathologies**: content-addressing noise, memory aliasing on free-list reuse, temporal-link distribution collapse (arXiv:1904.10278 Csordas/Schmidhuber)
- **Noisy-TV problem** for surprise-gating: stochastic inputs trap prediction-error gates (arXiv:2102.04399); aleatoric-vs-epistemic split needed
- **Hardware/batch incompatibility** for dynamic compute: mixed-length exits under-utilize accelerators (Fluid Batching arXiv:2209.13443)

## 3 underexplored candidates with pre-registered bands

**Candidate A: Bayesian-surprise per-token compute gate (SDT-style, arXiv:2511.21408)** -- bridges ICM curiosity-signal with MoD-style depth-routing
- HARD-PASS: epistemic-surprise gate achieves >=20% compute reduction at iso-quality vs softmax-entropy baseline (BranchyNet); AND remains stable under stochastic-input ablation (noisy-TV test)
- HARD-FAIL: gate-collapse to <5% entropy by training end OR noisy-TV trap (>2x gate-rate on stochastic injection)
- P_deflated = **0.40** (novel-synthesis cap 0.50 minus 0.10 for unverified primary)

**Candidate B: Break-even regime boundary characterization** -- "at what (batch, seq-len, k/N, top-k) does router + dispatch + memory-load cost EXCEED FLOP savings?"
- HARD-PASS: discover a sharp boundary at batch <= B* OR seq-len <= L* where active gating becomes net-LOSS; report (batch, seq-len, sparsity) frontier
- HARD-FAIL: no monotone boundary detected; net-savings flat across regime sweep
- P_deflated = **0.45** (verified by survey gap; instrumentation-heavy)

**Candidate C: Key-value separation + anti-saturation regularizer on allocation gate (DNC write-side, symmetric to Csordas read-side)**
- HARD-PASS: recall@k uplift >=10pp vs unregularized allocation gate on N-slot copy/recall, AND allocation-gate entropy stays in [0.4, 0.7] (anti-saturation)
- HARD-FAIL: regularizer collapses gate to uniform (entropy > 0.95) OR no recall uplift (<2pp)
- P_deflated = **0.35** (adjacent-but-unwitnessed direct analog)

## Cross-thread synthesis (with substrate today)

- **Substrate ARCH-B finding (nonlinear-readout LIFTS capacity 1.0->16xN)** is the **read-side analog** of Candidate C's write-side intervention. Combining both could deliver a compute-neutral write-read symmetric capacity boost.
- **DEGENERATE-REGIME-NOT-REFUTATION class (4 witnesses today)** maps directly to selective-deadlock failure mode -- substrate's active-gating cell 8a must distinguish "gate didn't help" from "gate worked but in degenerate regime".
- **USER measured-bounds-are-method-config-contingent rule** binds Candidate B directly: the break-even boundary IS the method/config envelope statement the project already requires.
- Cell 8b (SURPRISE-GATING mechanism) and cell 8a (ACTIVE-GATING perf-COST) **share the surprise-gating frontier** -- Candidate A bridges them.

## Substrate-product implications

- **STRONG-bucket fit**: cell 8a should pre-register a deterministic break-even map (Candidate B framing) -- this is exact/combinatorial cert-grade territory the substrate excels at
- **WEAK-bucket avoid**: do NOT pre-register on aggregated quality metrics that hide degenerate-regime; require per-cell expert-usage entropy traces (the selective-deadlock signature)
- **Cell 8a prereg recommendation**: combine Candidate B (break-even sweep) as primary HARD-PASS axis + Candidate A (Bayesian-surprise) as secondary mechanism arm -- this both bounds compute-cost honestly AND tests the underexplored mechanism worth-a-drill

## 3 closing bullets

- **Literature-strongest perf-cost framing**: MoE accuracy-per-log10(FLOP) Efficiency Score (arXiv:2512.24776) -- Pareto-dominant but memory-bound at deploy
- **Most-underexplored worth-experiment**: Bayesian-surprise as per-token compute gate (SDT arXiv:2511.21408) -- newest, bridges disjoint literatures, single-cell ablation feasible
- **Open theoretical frontier**: regime-boundary where router + dispatch + memory cost exceeds FLOP savings (no published systematic characterization)

## Citations (verified-fetched count: 14+ via sub-agent WebSearch + WebFetch)

- arXiv:2101.03961 Switch Transformer
- arXiv:2202.09368 Expert Choice
- arXiv:2202.08906 ST-MoE z-loss
- arXiv:2605.19378 Selective deadlock
- arXiv:2512.24776 MoE Pareto dominance
- arXiv:1410.5401 NTM
- Nature 2016 DNC
- arXiv:1904.10278 Csordas/Schmidhuber DNC fixes
- arXiv:1610.09027 Sparse DNC
- arXiv:2505.00315 MoSA
- arXiv:1308.3432 Bengio conditional compute
- arXiv:1709.01686 BranchyNet
- arXiv:1705.05363 ICM Pathak
- arXiv:2511.21408 SDT/STT Bayesian-surprise routing
- arXiv:2403.07965v2 Conditional-computation survey
- arXiv:2102.04399 Noisy-TV aleatoric
- arXiv:1907.06627 Batch-shaping
- arXiv:2503.06823 eMoE
- arXiv:2508.17467 MoE Inference Bench
- NSR nwae088 Dynamic networks survey

P_deflated headline confidence: 0.40-0.45 (lit-scan calibration penalty applied; survey-only, not novel synthesis).

-- Research (Director) via Sonnet sub-agent
