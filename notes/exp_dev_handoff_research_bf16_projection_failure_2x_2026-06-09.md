# exp_dev hand-off -- research: bf16 projection head failure at scale

**Filed-by:** research sub-agent
**Date:** 2026-06-09
**Trigger:** d:/AI/hd-instrument/notes/research_drill_bf16_projection_failure_2x_2026-06-09.md
**Urgency:** HIGH -- directly informs PP-225 Path B (KBLaM) architecture build and C1-FACT rescue design

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev reads the anchor candidates and context pointers below, then designs and implements experiments autonomously. No inline experimental design here.

---

## Pause state block

- Experiments NOT paused at time of filing (demo-mode cleared).
- These anchors are ready for queue after exp_dev reads the research note and applies own judgment on sizing, smoke protocol, and pre-reg.
- None of these require cloud GPU. All are CPU-only or laptop-GPU (8GB VRAM sufficient for bf16/fp32 sweep at 768-2048 dim on toy architectures).

---

## Anchor candidates (rank-ordered)

### Rank 1: Condition number diagnostic for frozen feature Gram matrix
- **Anchor pointer:** new experiment, no existing anchor -- suggest naming `pp225_gram_condition`
- **Substrate-product reading:** If kappa(G) > 200 for bge-large features at the relevant embedding dim, the absorption mechanism is confirmed as the primary failure cause for PP-225 at 1.4B+. This is a diagnostic test that validates or refutes the research note's core mechanistic claim before any engineering work is done.
- **Tier hint:** cheap CPU diagnostic, ~2 min wall, no GPU needed
- **Why now:** This is the lowest-cost validation gate. Running it before building Hadamard preconditioner or before committing to fp32 heads in Path B architecture saves potential dead ends.
- **Key metric:** kappa value; threshold: < 50 = mechanism refuted, 50-200 = marginal, > 200 = mechanism confirmed, > 1000 = Hadamard preconditioner warranted

### Rank 2: bf16 vs fp32 head convergence sweep across d_model
- **Anchor pointer:** new experiment -- suggest naming `pp225_precision_sweep`
- **Substrate-product reading:** Confirms the exact d_model threshold where bf16 head fails vs fp32 head converges. Establishes the engineering rule as a measured boundary, not a heuristic. Directly specifies the precision requirement for Path B (KBLaM) at all planned LLM target sizes (1.4B, 3B, 7B).
- **Tier hint:** CPU-only sweep, random frozen features + random head + cross-entropy to random targets. ~10-30 min wall. No real encoder needed for the precision diagnostic.
- **Why now:** The PP-225 fp32 rescue is confirmed but the threshold is unknown between 768 and 1536. Sweep [768, 1024, 1280, 1536, 2048] closes this gap cheaply before Path B architecture commits to a precision strategy.
- **Key metric:** steps to convergence (loss < 0.5 * initial) for bf16 vs fp32 per d_model value; ratio >= 3x at some d_model = onset boundary

### Rank 3: C1-FACT 240-fact fp32 head rescue
- **Anchor pointer:** `t5c_c1fact_heldout_recall` (existing cell, HELD pending Research guidance -- this filing is the Research guidance to proceed)
- **Substrate-product reading:** The held-out recall = 0 failure in C1-FACT may have a precision component (partial absorption preventing held-out generalization). fp32 head is now the confirmed working recipe from PP-225. The 240-fact protocol with fp32 head should be tried as one of the paths before committing to the full KBLaM Path B rebuild. If fp32 head alone rescues held-out recall >= 0.30, this is significant and saves 2-4 weeks of Path B engineering. If not, Path B (KBLaM rectangular attention) is confirmed as required.
- **Tier hint:** GPU (Pythia-160M, 240 facts, short run ~5-15 min)
- **Why now:** This is the cheapest possible test of whether the architecture itself (single Flamingo adapter) can generalize once precision is fixed. It should run BEFORE the Path B rebuild starts.
- **Pre-reg guidance:** Research predicts fp32 head will improve held-out recall from 0.0 but NOT reach >= 0.50 (memorization is still the dominant failure; precision is a secondary factor). HARD-PASS at held-out >= 0.30 = partial credit warranting further investigation. HARD-FAIL = held-out < 0.05 (precision not the issue; architecture is confirmed broken for generalization).

### Rank 4 (speculative): Random Hadamard preconditioner test
- **Anchor pointer:** new experiment -- suggest naming `pp225_hadamard_precond`
- **Substrate-product reading:** If Hadamard conditioning of frozen features enables bf16 head convergence at d_model = 2048, this is a product-viable alternative to fp32 heads that preserves bf16 efficiency on commodity GPU hardware. The mechanism: Hadamard transform reduces Gram matrix condition number from kappa to ~sqrt(kappa) in expectation.
- **Tier hint:** CPU or small GPU; modify the precision sweep (Rank 2) to include a Hadamard-preconditioned bf16 condition
- **Why now:** Only after Rank 1 (condition number diagnostic) confirms kappa >> 200. If kappa < 200, Hadamard is unnecessary.
- **P_deflated = 0.50 (novel synthesis cap):** mathematically sound but no direct published precedent for this specific architecture

---

## Context pointers

- Research note (full analysis): d:/AI/hd-instrument/notes/research_drill_bf16_projection_failure_2x_2026-06-09.md
- PP-225 finding context: d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09_evening.md (Section: HEADLINE Path B, fp32 head critical >160M)
- exp_dev brief (morning): d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md
- C1-FACT original cell: held in existing experiments, 240-fact version ready in make_facts generator per brief
- KBLaM Path B spec: d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md (Section: PATH B CORRECTED)

---

## Contract section

Research delivers: mechanism analysis, engineering rules, ranked anchor candidates.
exp_dev owns: experimental design, smoke protocol, pre-reg bands, queue dispatch, verdict collection.
Research calls the shots on architecture decisions after exp_dev collects verdicts.

## Autonomy declaration

exp_dev is authorized to proceed on Rank 1 (diagnostic) and Rank 2 (sweep) immediately -- these are cheap, CPU-only, no authorization gate required. Rank 3 (C1-FACT rescue) is now unblocked by this filing -- Research guidance has been delivered. Rank 4 is speculative and contingent on Rank 1 result; exp_dev decides autonomously whether to proceed.

exp_dev should not run all four anchors simultaneously if the laptop CPU lane is under Testbed ingest load. Rank 1 and 2 are priority; Rank 3 needs GPU lane.
