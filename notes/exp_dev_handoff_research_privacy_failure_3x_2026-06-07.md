# exp_dev hand-off -- research: privacy failure mechanism (3x deep drill)

Filed-by: research sub-agent
Trigger: notes/research_drill_privacy_failure_mechanism_3x_2026-06-07.md
Date: 2026-06-07

## Pause state block
This file is written unconditionally. exp_dev MUST check data/orchestrator_paused.flag before dispatching to queue. If paused, hold this handoff until resume.

## Per [[feedback-no-experiment-design-in-prompts]]
This file provides TASK + WHY + CONTRACT + AUTONOMY pointers only. exp_dev decides anchor names, sweep grids, threshold formulas, queue choice, and ETA. No inline experiment design below.

---

## Anchor candidates (rank-ordered)

### Rank 1: Cell F1 -- cone-aware cosine rescaling (ZKL privacy test)
- Anchor pointer: Subtract mean embedding mu from all stored and query vectors before cosine scoring; measure ZKL(50) and top-1 recall before and after
- Substrate-product reading: If cone-aware centering reduces ZKL from 0.22 baseline to <0.14, this is a zero-cost architectural fix for the SRHT+DP privacy failure; directly addresses the cone-dominated false-positive membership signal identified in the research note; passes = HIPAA-grade claim path opens
- Tier hint: CPU probe, laptop or remote CPU, ~2hr wall including eval; no GPU needed; numpy/scipy only
- Why-now: Highest P_deflated (0.42) of all linear-method paths; directly attacks identified geometric cause; lowest cost; if it works it takes priority over everything else in the privacy roadmap

### Rank 2: Cell B1 -- rank randomization top-k
- Anchor pointer: After scoring, shuffle top-k=5 results with Mallows distribution; sweep temperature theta in {0.5, 1.0, 2.0, 5.0}; measure ZKL(50) at each theta; measure top-1 precision vs theta
- Substrate-product reading: Tests the hypothesis that DP score-noise failed because rank was preserved; if ZKL decreases by >=0.04 at any theta, rank order IS the exploited signal and rank-randomized retrieval mode is the fix; if ZKL does not move at any theta, the grounding-attack signal is upstream of rank (content-based) and Path B is definitively closed
- Tier hint: CPU probe; ~1hr wall; can run in parallel with F1
- Why-now: Directly tests why DP failed (the rank-not-score hypothesis); 1-hour test; definitive yes/no on a clean mechanistic question; results interpret both this failure and the DP failure in one sweep

### Rank 3: Cell A1 -- privacy-objective whitening
- Anchor pointer: Optimize whitening matrix W to maximize cosine-distribution entropy (rather than current variance-equalization objective); scipy L-BFGS-B on 2048x2048 W; measure ZKL and recall pre/post
- Substrate-product reading: If entropy-objective whitening achieves ZKL <0.14 with recall >=0.85, the production whitening step can be upgraded to the compound objective (alpha * retrieval + (1-alpha) * privacy) with no new infrastructure; key architectural question: are the retrieval-separating and membership-leaking subspaces separable by a learned linear projection?
- Tier hint: CPU probe; ~2hr wall including scipy optimization; can run after F1+B1 results are in (or in parallel if compute allows)
- Why-now: Higher P_deflated (0.38) than Path B; compound-objective whitening is a natural extension of existing production whitening with no new components

### Rank 4: Cell E1 -- membership inference AUROC oracle (baseline calibration)
- Anchor pointer: Train a simple logistic classifier on cosine(query, stored_fact) to predict membership; measure AUROC on held-out members vs non-members; establishes the ZKL-to-AUROC mapping needed to interpret ZKL=0.10 in regulatory terms
- Substrate-product reading: ZKL<0.10 corresponds to some AUROC value; if AUROC=0.55 at ZKL=0.10, the HIPAA claim is well-grounded; if AUROC=0.72 at ZKL=0.10, the target is too weak; this calibration cell has zero privacy-engineering value but is required for honest product claim documentation
- Tier hint: CPU probe; ~30 min wall; straightforward sklearn logistic regression; can be bundled with F1 or B1 run
- Why-now: Recommended combination with F1 since both run on the same eval set; adds negligible extra time; clarifies regulatory interpretation of ZKL targets

### Rank 5: Cell C1 -- DP write-time utility curve (if F1+B1+A1 all fail)
- Anchor pointer: Store noisy vectors d_i + N(0, sigma_w^2 I); sweep sigma_w in {0.1, 0.2, 0.3, 0.5, 0.8}; measure ZKL and top-1 recall at each sigma_w; find the crossing point where ZKL target is met vs where recall degrades below 0.80
- Substrate-product reading: Determines if there exists ANY sigma_w in the write-noise space where both ZKL<0.12 AND recall>=0.80; the research note predicts no such sigma_w exists for Llama; if prediction is wrong (sigma_w=0.35 achieves both targets), write-time DP is viable; if prediction is right, the utility-privacy frontier is empirically confirmed and the theoretical floor analysis is validated
- Tier hint: CPU probe; ~2hr wall; only dispatch if F1+B1+A1 all yield ZKL>=0.18
- Why-now: Conditional on other paths failing; provides formal DP guarantee if it works; validates floor theory if it fails

---

## Context pointers (file paths, not summaries)
- Research note: d:/AI/hd-instrument/notes/research_drill_privacy_failure_mechanism_3x_2026-06-07.md
- Prior federated privacy handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_federated_privacy_substrate_2x_2026-06-07.md
- Production architecture lock: d:/AI/hd-instrument/memory/production_architecture_locked_2026-06-07.md
- Post-compaction brief: d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07.md
- Prior federated privacy research note: check notes/ for research_drill_federated_privacy_substrate_2x_2026-06-07.md

---

## Contract section

exp_dev commits to:
1. Check data/orchestrator_paused.flag before any queue dispatch.
2. Pre-register HARD-PASS / HARD-FAIL bands per research note Section 4 table before writing any anchor script.
3. Run F1 and B1 in parallel (they are independent; same eval set).
4. Run Cell E1 bundled with F1 (same eval set; negligible extra cost).
5. Report ZKL AND top-1 recall/precision for every cell (both metrics required; neither alone is sufficient).
6. If F1 ZKL is WORSE than baseline (>0.22), note this explicitly in verdict_msg: it means the cone axis IS the membership discriminant and confirms the same-subspace hypothesis.
7. Do NOT proceed to Path D (encoder fine-tuning) planning without explicit orchestrator authorization. Path D is a 1-2 week commitment; exp_dev does not initiate multi-week work unilaterally.
8. Combine with Cell E (from the prior federated handoff, exp_dev_handoff_research_federated_privacy_substrate_2x_2026-06-07.md) if not yet dispatched: they share the same oracle test structure.

## Autonomy declaration

exp_dev has full autonomy over:
- Anchor names and queue slot selection
- Exact sweep grid values within the ranges named in each cell description
- Implementation details of the Mallows shuffle (can substitute Plackett-Luce if preferred)
- Whether to run A1 in parallel with F1+B1 or sequentially after results
- Whether to combine Cell E1 oracle with an existing pending federated probe
- Threshold formulas for ZKL computation (use the same formula as the prior DP sweep for comparability)
- ETA estimation and queue assignment (CPU vs remote CPU)
