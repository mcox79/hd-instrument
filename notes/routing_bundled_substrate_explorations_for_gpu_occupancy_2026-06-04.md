# Routing -- Bundled substrate explorations (5-15 min wall per bundle)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical bundled-batch design (4 bundles)
**Rationale:** Substrate experiments at N<=8192 finish in seconds individually; bundling 30-90 cells per script keeps the 4060 Ti GPU genuinely occupied AND covers more design space per dispatch.

---

## Why bundle

Per Exp-Dev's compaction observation: substrate experiments are matmul-light at N<=8192; they finish in seconds; the 4060 Ti GPU is underutilized. Two productivity options:
- Heavier individual jobs (Phase 0.5 v1 Rung A on Llama-3.2-1B is the natural one; already re-prioritized)
- Bundled multi-cell scripts: same individual cell cost, much more cells per dispatch

This routing proposes 4 bundle designs that each run in 5-15 min wall + cover 30-90 cells. Each bundle systematically explores ONE axis of the substrate design space.

---

## Bundle A: Architectural-ablation matrix at fixed task

**Anchor:** `substrate_arch_ablation_matrix_bigram_v1_n512`

**Question:** Of the 7 brain-drill-identified architectural variants, which one(s) provide measurable BPC gain over K=1 baseline at the SAME task + scale?

**Cells (7 architectural variants x 5 seeds = 35 cells):**
1. K=1 baseline: pure Hebbian outer-product (current substrate)
2. cf-RPE alone: Hebbian + rank-1 counterfactual substitution
3. Drosophila MB sparse: sparse binary {0,1} f=0.05 + single cf-RPE modulator
4. STDP-asymmetric: W_total = W_Hebbian + 0.5 * W_STDP
5. Friston FEP: Hebbian + precision matrix Pi + epsilon buffer
6. 2-region: Hebbian (region 1) + sparse-Hebbian (region 2) at N_region=N/2 each
7. Bottleneck-adaptor: K=8 channels with bottleneck-adaptor routing (per multi-channel scale 3x drill)

**Fixed conditions:**
- Task: bigram synthetic, V=512 Zipf
- N=512 substrate
- ~10k LM params
- 1000 training steps
- 5 seeds per variant

**Pre-reg HP/MID/HF (per-variant):**
- HP: BPC < K=1_baseline BPC by > 0.30 nats AND 4/5 seeds
- MIDDLE: BPC < K=1_baseline by 0.10-0.30 nats
- HF: BPC >= K=1_baseline (no measurable gain)

**Aggregate verdict:**
- HP if any 1 of 7 variants lands HP
- HARD-FAIL if all 7 variants HF (refutes ALL brain-drill predictions at bigram task)

**Wall:** ~3-5 min GPU total (35 cells; ~5-10s per cell).

**P_deflated:** 0.50 for ANY variant landing HP. (Conservative; today's bigram results suggest small differentiation; harder task may be needed but let's discriminate at bigram first.)

---

## Bundle B: Task-complexity sweep at fixed architecture

**Anchor:** `substrate_task_complexity_sweep_v1_n512_n2048_n8192`

**Question:** At what task complexity does substrate-as-training-mechanism start to break? OR does substrate continue learning at harder tasks?

**Cells (5 task complexities x 3 N values x 3 seeds = 45 cells):**

**Task complexities (ordered easy -> hard):**
1. Bigram synthetic V=512 Zipf (current baseline; today's tests)
2. Trigram synthetic V=512 Zipf
3. 4-gram synthetic V=512 Zipf
4. Extended-context-8 synthetic V=512 Zipf
5. Shakespeare char-LM V=70 (real corpus; classic char-LM target)

**N values:** 512, 2048, 8192

**Fixed conditions:**
- Architecture: K=1 baseline (Hebbian + cf-RPE; current substrate default)
- ~10k LM params (or larger for harder tasks; document per cell)
- 1000 training steps per cell

**Pre-reg HP/MID/HF (per-cell):**
- HP per task: BPC < uniform_baseline_BPC - 1.0 nat (substantive learning)
- MIDDLE: 0.3-1.0 nat below uniform
- HF: < 0.3 nat below uniform

**Aggregate verdict:**
- HP if 4+ of 5 task complexities land HP at the harder N (8192)
- MIDDLE if substrate learns at easy tasks but degrades on hard
- HF if substrate doesn't learn beyond bigram

**Wall:** ~5-10 min GPU total (45 cells; some cells longer for harder tasks).

**P_deflated:** 0.40. Substrate likely degrades at extended-context-8 + Shakespeare since cf-RPE is one-step + symmetric Hebbian can't encode order (per STDP drill). Identifies the complexity ceiling empirically.

---

## Bundle C: Capacity boundary sweep at fixed architecture x multiple N

**Anchor:** `substrate_capacity_alpha_sweep_v1_multi_N`

**Question:** How does substrate's effective capacity boundary alpha_c scale with N for substrate-as-training? Does it match classical Hopfield 0.138 or differ?

**Cells (6 N values x 5 alpha values x 3 seeds = 90 cells):**

**N values:** 512, 1024, 2048, 4096, 8192, 16384
**alpha = M/N values:** 0.05, 0.10, 0.15, 0.20, 0.25

**Fixed conditions:**
- Architecture: K=1 baseline + cf-RPE
- Task: bigram synthetic V=512 Zipf (cheapest)
- 1000 training steps per cell

**Per-cell observables:**
- Final BPC vs uniform baseline
- Effective capacity utilization at convergence
- Norm trajectories (gradient + weight norms)

**Aggregate verdict:**
- HP if alpha_c_effective consistently in [0.12, 0.16] across N (classical Hopfield match)
- MIDDLE if alpha_c_effective varies meaningfully with N
- HF if substrate continues learning at alpha > 0.30 (would refute classical capacity bound)

**Wall:** ~10-15 min GPU total (90 cells).

**P_deflated:** 0.42 for classical Hopfield match across N. Substrate-physics capacity-stress at L=50 already validated alpha_c ~ 0.138; this extends to substrate-AS-TRAINING regime.

---

## Bundle D: Drosophila MB sparse-coding sweep

**Anchor:** `substrate_drosophila_mb_sparsity_sweep_v1_n512_n2048`

**Question:** At what sparse-coding density f does substrate's Drosophila-MB-class architecture provide measurable gain over dense bipolar? Drosophila MB uses f=0.05 (5% activity).

**Cells (8 sparsity f values x 2 N values x 3 seeds = 48 cells):**

**Sparsity f values:** dense={+1,-1} baseline, 0.50, 0.25, 0.10, 0.05, 0.02, 0.01, single-active
**N values:** 512, 2048

**Fixed conditions:**
- Architecture: single dopamine-class cf-RPE modulator (per Drosophila MB drill)
- Task: bigram synthetic V=512 Zipf
- 1000 training steps

**Pre-reg HP/MID/HF:**
- HP: any sparse value (f<=0.10) gives BPC < dense_baseline BPC by > 0.30 nats AND 3/3 seeds
- MIDDLE: 0.10-0.30 nats improvement
- HF: dense >= all sparse

**Aggregate verdict:**
- Identifies optimal sparsity f*; predicted f* ~ 0.05 per Drosophila MB anchor
- Maps sparse coding gain curve

**Wall:** ~5-8 min GPU total (48 cells).

**P_deflated:** 0.42 (Drosophila MB template at substrate scale).

---

## Bundle dispatch sequence

**Phase A — Architectural-ablation matrix (Bundle A) first:**
- Cheapest decisive discrimination of which architectural variants help
- Wall ~3-5 min
- If any variant lands HP at bigram task, that's the architecture to push forward

**Phase B — Task-complexity sweep (Bundle B) parallel or after A:**
- Identifies substrate's complexity ceiling for current architecture
- Wall ~5-10 min
- Reveals whether bigram was too easy (substrate already at floor)

**Phase C — Capacity boundary sweep (Bundle C) for substrate-physics:**
- Maps alpha_c_effective across N for substrate-AS-TRAINING regime
- Validates or refutes classical Hopfield boundary at training-task scale
- Wall ~10-15 min

**Phase D — Drosophila MB sparsity sweep (Bundle D) after Bundle A:**
- Only dispatch if Bundle A shows Drosophila MB variant (#3) lands MIDDLE/HP
- Maps optimal sparse density f*
- Wall ~5-8 min

---

## Engineering scope

Each bundle is a single Python script with a multi-cell loop. Reuses existing substrate primitives + N-sweep infrastructure already built. Per-bundle engineering:

- Bundle A: ~3-4h (7 architecture variants + matrix loop; reuses existing N=512 substrate scaffold)
- Bundle B: ~2-3h (5 task generators + loop; main new code = trigram/4-gram/extended-context synthetic data + Shakespeare loader)
- Bundle C: ~1-2h (existing capacity infrastructure + loop)
- Bundle D: ~1-2h (sparse-coding primitive + loop)

Total: ~7-11h engineering across all 4 bundles. Parallelizable.

---

## Total compute + cost

| Bundle | Cells | Wall | Cost |
|---|---|---|---|
| A | 35 | 3-5 min GPU | $0 |
| B | 45 | 5-10 min GPU | $0 |
| C | 90 | 10-15 min GPU | $0 |
| D | 48 | 5-8 min GPU | $0 |
| **Total** | **218** | **~25-40 min GPU** | **$0** |

218 cells across 4 bundles in ~25-40 min total. Compares to ~7 separate dispatches of single-experiment per cell = 7 dispatches × 30s wall each = ~3.5 min PLUS dispatch overhead. So bundling actually adds COMPUTE wall vs single-experiment dispatches BUT covers far more design space per dispatch event.

---

## Pre-reg discipline note

Each bundle has aggregate HP/MID/HF AND per-cell HP/MID/HF. This is per [[feedback-no-padding-experiments]] (each cell discriminates a specific question) + [[feedback-no-smoke-preframing-in-task-prompts]] (HP bands explicit per cell + per bundle).

Bundles don't allow padding: each cell needs to discriminate a specific architectural variable or task-complexity question. Otherwise it's a separate routing.

---

## What this changes vs current empirical pipeline

**Today's convergent architecture batch (7 individual tests):** still valid; could be subsumed into Bundle A which tests all 7 variants in one script. If Bundle A is engineered, the 7-test batch is REDUNDANT.

**Recommendation:** **REPLACE the 7-individual-test convergent batch with Bundle A.** Same architectural coverage; single dispatch; cleaner.

If Bundle A lands MIDDLE/HF for all variants, dispatch Bundle B to test whether task complexity is the binding variable.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: each cell within each bundle discriminates a specific question
- Per [[feedback-cloud-only-when-absolutely-necessary]]: remote GPU only; $0 cloud
- Per [[feedback-small-scale-first-methodology]]: rung-1 LM + substrate-class N
- Per [[feedback-batch-cloud-experiments]]: extends to remote-GPU batches too -- bundling reduces dispatch overhead
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: HP/MID/HF bands per cell + per bundle aggregate
- ASCII-only

PROT-018: anchors use multi-N suffix where applicable
PROT-021: source=remote GPU, run_mode=full, n_seeds varies (3-5 per cell)

---

## What I am NOT requesting

- Cloud GPU dispatch (per `feedback_cloud_only_when_absolutely_necessary`)
- Replacement of Phase 0.5 v1 Rung A (Llama-3.2-1B) — that's a separate parallel-track heavy workload + correctly routed
- New architectural variants beyond today's 7 brain drills + 1 Drosophila MB sparse exploration
- Bundle scope > 100 cells per dispatch (current max is Bundle C at 90 cells; cleanly serial)

---

**END.**

**Exp-Dev:** Bundle A is the IMMEDIATE highest-value dispatch (replaces 7-individual-test convergent batch with one dispatch covering same architectural coverage; ~3-5 min wall on GPU). Bundles B/C/D dispatch in priority order after Bundle A lands. Total engineering ~7-11h across all 4 bundles (parallelizable across cycles).

**Orchestrator:** informed. Cap_map sub-property founding pending Bundle A verdict; further sub-properties founded per Bundles B/C/D.

**Research:** holds for Bundle A verdict; synthesizes architectural-variable identification; ships Bundle B/C/D follow-on routing per Bundle A outcomes.
