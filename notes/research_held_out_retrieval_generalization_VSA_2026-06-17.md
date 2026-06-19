# Research drill: held-out retrieval + generalization for VSA + nonlinear-readout substrate (2026-06-17 ~20:25)

**From:** Research (Director) via Sonnet sub-agent (Agent tool subagent_type=research)
**Date:** 2026-06-17 ~20:25 (Skunkworks cert-owner pick #1 of 3; T2/T3 research-onboarding)
**Discipline:** SAFE generic queries per loop SAFETY block + 11th-rule clean (WebSearch+WebFetch factual retrieval not LLM-judge); evidence-of-search shown; ASCII

## HEADLINE

Field has CAPACITY benchmarks (Plate 3pct-error; Frady-Sommer resonator quadratic-in-N) but **NO standardized held-out CORPUS-generalization benchmark for VSA cleanup memory** -- paraphrase / OOD / hard-negative protocols (PAWS, HotpotQA-distractor, MinHash-dedup, AssoMem) are mature in NLP/LLM-memory and **structurally importable into VSA**. Sparse readout (entmax/sparsemax-Hopfield) PROVABLY exceeds dense softmax on capacity AND length-OOD per Hu-Wu-Martins NeurIPS 2023, BUT a SHARP memorization-vs-generalization PHASE TRANSITION (Biroli 2025; "Too Big to Think" 2025) is the dominant phenomenon -- **graceful held-out generalization from nonlinear readout cannot be assumed**. Held-out failure-mode taxonomy maps to 4-channel diagnostic panel + composed deconfound stack as cheap decisive instrument.

## 4-CHANNEL DIAGNOSTIC PANEL (the held-out instrument)

1. **Attention-entropy** (softmax one-hot collapse diagnostic; Zhai 2023)
2. **Per-neuron energy profile** (cleanup prototype-collapse diagnostic; McAlister-Robins-Szymanski)
3. **Embedding-cluster silhouette** (wrong-cluster confident-hallucination diagnostic)
4. **Per-subgroup OOD accuracy** (catastrophic distribution-shift diagnostic; Nagarajan 2020)

Composed deconfound stack: D5 MinHash dedup → D2 sub-critical operating point → D3 PAWS-style hard-negative distractors → D7 scrambled-key negative-control (smoke gate).

## FALSIFIABLE PRE-REGISTERED BANDS (sacrosanct both directions per NEGATIVITY-BIAS USER-LOCKED rule)

**HARD-PASS** (must clear ALL):
- Scrambled-key control (D7) <= 2x chance baseline (binding is active variable; not embedding stats)
- Attention-entropy on held-out > 0.5 * entropy on training (no one-hot collapse)
- Energy-profile fingerprint matches LEARNED-class signature on >=80% of correct retrievals
- Near-OOD accuracy >= 70% of in-dist accuracy
- Top-1 cluster silhouette > 0.3 AND cluster CONTAINS correct key

**HARD-FAIL** (any one triggers):
- Scrambled-key control > 5x chance (binding NOT load-bearing; embedding-stats artifact)
- Attention-entropy on held-out < 0.1 * training (softmax one-hot collapse mode)
- Prototype-energy fingerprint uniformly negative on >50% retrievals (cleanup mode-collapse)
- Cluster silhouette > 0.5 BUT cluster wrong (wrong-cluster confident-hallucination)
- Near-OOD accuracy < 30% of in-dist (catastrophic distribution-shift)
- Operating point sweep crosses memorization-vs-generalization phase boundary with spurious-state density peaking AT boundary (Biroli 2025 prediction)

## CLOSING 3 BULLETS (Drill Q5)

1. **Most underexplored single-cell experiment**: PAWS-style lexical-overlap-controlled hard-negative retrieval applied to VSA cleanup — **zero papers do this in verified search**; high product-relevance; isolates SEMANTIC binding from surface-similarity. T3 conjecture: substrate cleanup will fail PAWS-style at <40% accuracy (mirroring SOTA NLP) REGARDLESS of capacity headroom = TRUE held-out test orthogonal to capacity.

2. **Strongest measurement (no-Goodhart-aware)**: Multi-channel diagnostic panel (entropy + energy + silhouette + subgroup) gated by scrambled-key D7 negative-control. NO single metric (top-1, recall@k, perplexity gap) is robust — each is gameable. Composed panel is gameable ONLY by genuinely solving the four named failure modes = no-Goodhart property. Biroli 2025 spurious-state-density at phase-boundary = most novel single signal but requires regime sweep.

3. **Open theoretical question relevant to tonight's nonlinear-readout cells**: Where is the precise THRESHOLD (as function of readout_dim, num_stored_patterns, sparsity alpha) for memorization-vs-generalization PHASE TRANSITION in entmax/sparsemax-Hopfield readout? Literature has the PHENOMENON (Hu-Wu-Martins 2023; Biroli 2025; "Too Big to Think" 2025) but NO closed-form threshold. Tonight's 3 nonlinear-readout FULL cells implicitly probe this surface but with no pre-registered phase-boundary hypothesis. **T3 prediction: held-out generalization for nonlinear readout is NON-MONOTONIC with capacity utilization, peaking at sub-critical regime and collapsing at and above critical load** — directly testable with regime sweep.

## CROSS-THREAD SYNTHESIS (substrate-context)

- Composes with ARCH-B SPARSITY_NEUTRAL confirmed today: phase-transition warns ARCH-B's capacity lift may NOT auto-yield held-out lift; cliff may have moved not vanished
- Composes with C1 entmax cert-grade tonight: regime sweep needed to verify entmax's literature-claimed advantage carries to held-out
- Composes with refuse-gate FULL (real-held-out q54-q65): tonight's verdict IS one data point on this phase-transition surface; one cell is insufficient — regime sweep tomorrow
- Composes with DEGENERATE-REGIME-NOT-REFUTATION (Store-CONFIRMED 8 witnesses): scrambled-key control D7 falsely passes if substrate has degenerate structure — defensive check needed
- Composes with verify-the-referent at experiment-design layer: the "held-out" referent must actually be disjoint (time-disjoint slice not random split)

## P_deflated calibration (lit-scan penalty applied)

- 4-channel diagnostic panel distinguishes 4 named failure modes: **0.55** (each diagnostic lit-mature; -0.20 from raw 0.75)
- Composed deconfound stack closes capacity-confound for substrate held-out: **0.45** (novel-synthesis cap 0.50; -0.20 from raw 0.65)
- Sparse readout inherits graceful novel-composition held-out generalization: **0.20** (novel-synthesis territory; capped 0.50 then deflated)
- Held-out-corpus VSA benchmark is genuine field gap (not search miss): **0.65** (negative-search-result on PAWS-applied-to-VSA strongly supports)

## Verified citations (30+ across 4 parallel Sonnet lit-scan sub-agents)

- [Plate HRR](https://redwood.berkeley.edu/wp-content/uploads/2020/08/Plate-HRR-IEEE-TransNN.pdf) — 3% error capacity protocol
- [Frady/Sommer Resonator](https://arxiv.org/abs/1906.11684) — quadratic-in-N capacity
- [Ramsauer Modern Hopfield](https://arxiv.org/pdf/2007.13505) — softmax = Hopfield equivalence
- [Hu-Wu-Martins Sparse Hopfield NeurIPS 2023](https://arxiv.org/html/2309.12673) — M >= M_Dense
- ["Too Big to Think" 2025](https://arxiv.org/html/2506.09099v2) — capacity cliff 40/40 -> 0/40
- [Biroli DAM->Diffusion 2025](https://arxiv.org/html/2505.21777v1) — memorization-generalization phase transition
- [Zhai attention-entropy collapse ICML 2023](https://proceedings.mlr.press/v202/zhai23a) — softmax one-hot diagnostic
- [McAlister-Robins-Szymanski 2024](https://arxiv.org/abs/2407.03342) — prototype-attractor collapse + energy fingerprint
- [Nagarajan OOD skew](https://arxiv.org/abs/2010.15775) — geometric+statistical confound
- [Zhang PAWS](https://arxiv.org/abs/1904.01130) — <40% SOTA on hard-negative paraphrase
- [Lee MinHash dedup ACL 2022](https://aclanthology.org/2022.acl-long.577/) — train-test contamination protocol
- [Schlegel/Neubert/Protzel VSA capacity-equalized](https://arxiv.org/pdf/2001.11797) — 99% accuracy bundle-threshold sweep
- [A-Hop Adaptive Hopfield 2025](https://arxiv.org/html/2511.20609v1) — variant-distribution retrieval reframing
- [AssoMem](https://www.researchgate.net/publication/396462346_AssoMem) — multi-signal AM retrieval +5.82% over SOTA on LongMemEval_l

## Next-drill candidate

Network-science / graph-theory adjacency: cluster-isolation / spectral-gap analysis of cleanup-memory codebook as graph (nodes=stored memories, edges=similarity); held-out generalization predicted by spectral-gap separation. Tier-1b adjacency to spin-glass (replica) + free-probability. High relevance to mode (d) wrong-cluster diagnostic panel.

T2/T3 ready for substrate research-finding onboarding (T2 = literature-supported; T3 = inferred-hypothesis).

-- Research (Director) via Sonnet sub-agent
