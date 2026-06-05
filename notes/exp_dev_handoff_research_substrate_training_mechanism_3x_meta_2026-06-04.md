# exp_dev hand-off -- research: substrate-as-training-mechanism 3x META drill

**Filed-by:** research sub-agent
**Date:** 2026-06-04
**Trigger:** d:/AI/hd-instrument/notes/research_drill_substrate_as_training_mechanism_3x_meta_2026-06-04.md
**Pause state:** check data/orchestrator_paused.flag before queueing

Per [[feedback-no-experiment-design-in-prompts]]: this file hands ANCHOR CANDIDATES + WHY-NOW + CONTEXT POINTERS to exp_dev. exp_dev designs the sweep grids, threshold formulas, and queue entries autonomously.

---

## Anchor candidates (rank-ordered)

**Rank 1 -- Mutual information probe: does any substrate signal contain language-predictive information?**
- Anchor pointer: Off-line MI probe using KSG estimator (Kraskov-Stoegbauer-Grassberger 2004) on substrate retrieval output, anti-Hebbian residual, and module address activations against next-character identity. Compute I(signal; next_char) on 1000 held-out characters.
- Substrate-product reading: if I > 0.01 bits for any signal, the substrate is not informationally orthogonal to language statistics -- proceed to readout training. If I < 0.001 for all signals, HF3 triggered (substrate dynamics orthogonal to language).
- Tier hint: CPU smoke, < 5 minutes wall; no GPU required. Cheapest possible decisive test.
- Why-now: this is the cheap decisive test from the 3x meta drill. It costs almost nothing and immediately partitions the design space: either substrate features carry language information (proceed to readout) or they do not (escalate to fundamental feasibility review).

**Rank 2 -- Single-channel readout: trainable linear layer on substrate retrieval signal**
- Anchor pointer: Replace 8-channel orchestration with a single substrate signal (whichever MI probe shows highest I(signal; next_char)) fed through a trainable 1-hidden-layer MLP readout (gradient descent on cross-entropy). Substrate parameters frozen during readout training.
- Substrate-product reading: tests Design Change C. If BPC improvement > 0.05 bits over baseline after readout training: substrate features are extractable but the multi-channel framework was hiding them. If BPC improvement < 0.02: single-channel readout also fails, escalate to Design Change B.
- Tier hint: CPU quick probe, < 30 min wall; 3-5 seeds.
- Why-now: directly tests whether Constraint 3 (8-channel gradient conflict geometry) was the dominant failure mode. Isolates constraint from Constraint 1.

**Rank 3 -- Contrastive Hebbian phase: add error-driven gating to substrate writes**
- Anchor pointer: Augment substrate's Hebbian write with a local error signal e_t = (target one-hot) - (retrieval output). Gate write as delta_W += eta * e_t * x_t^T. Implement as thin wrapper around existing substrate write. Target: BPC improvement > 0.3 bits over uniform baseline.
- Substrate-product reading: tests Design Change A (contrastive phase addition). Directly tests whether Constraint 1 (Hebbian expressivity ceiling) is bypassed when a supervised signal gates the write. This is the RBM CD-1 equivalent for the substrate.
- Tier hint: GPU smoke (single run, ~2-4h); 5 seeds; char-level benchmark.
- Why-now: contrastive Hebbian learning has validated convergence theory (Xie-Seung 2003; Scellier-Bengio EP); the addition is surgically small (error gate on existing write path). If this works at small scale, it opens substrate-as-trainable-layer for the full LLM path.

**Rank 4 -- Substrate-as-retrieval-layer hybrid: gradient-train output head only (Design Change B)**
- Anchor pointer: Freeze all substrate parameters after a standard initialization run. Train a 2-layer gradient-based MLP to read from substrate retrieval vectors and predict next character. Baseline comparison: pure MLP of same parameter count with no substrate.
- Substrate-product reading: tests whether substrate attractor states carry learnable representations when not required to be the training mechanism. If BPC < 2.5 and beats pure MLP baseline: substrate-as-memory-module path is validated for char-level LM. Direct product path for auditable memory + retrieval capability.
- Tier hint: GPU smoke (single A100, ~2h); direct precedent in DeltaNet + reservoir computing LM papers.
- Why-now: DeltaNet (NeurIPS 2024) and reservoir computing LM (arXiv:2507.15779, 2026) both validate this architecture class at scale. Char-level variant at 5k params is lowest-cost empirical test of the hypothesis.

---

## Context pointers

- Research note (full synthesis): d:/AI/hd-instrument/notes/research_drill_substrate_as_training_mechanism_3x_meta_2026-06-04.md
- Prior drill (substrate-as-full-LLM-training): d:/AI/hd-instrument/notes/research_drill_substrate_as_full_llm_training_deep_dive_2026-06-03.md
- Prior handoff (substrate LLM training 2026-06-03): d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_llm_training_2026-06-03.md
- DeltaNet paper (outer-product delta-rule LLM): arXiv:2406.06484 (NeurIPS 2024)
- Reservoir computing as LM: arXiv:2507.15779 (2026)
- signSGD paper: arXiv:1802.04434 (ICML 2018)
- KSG mutual information estimator: Kraskov, Stoegbauer, Grassberger (2004) Phys Rev E
- Xie-Seung contrastive Hebbian: Neural Computation 2003
- cap_map rows affected: auditable-memory (core), hierarchical-retrieval (🟢), compositional-algebra

---

## Contract

exp_dev receives this file, reads the context pointers, designs the experiment anchors (sweep grids, threshold formulas, N choices, queue entry names, pre-reg bands) autonomously. No experiment design is provided here per [[feedback-no-experiment-design-in-prompts]].

## Autonomy declaration

exp_dev has full autonomy over: anchor naming, parameter grids, hard-pass/hard-fail threshold formulas, queue choice (CPU vs GPU), seed count, timeout formula per [[feedback-per-experiment-timeout-required]], and cap_map decision logic post-verdict. Orchestrator approves queue before dispatch.
