# exp_dev hand-off -- research: continual full CLS 5x streams

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_continual_full_cls_5x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale only. exp_dev designs actual anchors, sweep
grids, thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist
(or confirm with orchestrator). Do not ship if paused.

---

## Context summary

Substrate currently has 1/4 of full CLS: episodic fast-store (W_fast outer-product write)
only. Three blocks are ABSENT: cortical slow-generalizer, consolidation scheduler,
schema-accelerated write path. Sprint 2 validated frequency-decay synthetically.

Five streams (biology, brain, crazy-arch, physics, LLM) converge on a two-mechanism
substrate-native full CLS architecture:

1. DUAL-SUBSTRATE-CLS: add W_slow (low-rank outer-product accumulator, alpha ~ 0.01);
   offline replay from W_fast rows into W_slow; retrieval blends both.
   P_deflated = 0.45.

2. STRETCHED-EXPONENTIAL-DECAY (KWW): generalize Sprint-2 frequency-decay from
   exp(-t/tau) to exp(-(t/tau)^beta) with beta ~ 0.6; tau_i scales with write_count_i.
   P_deflated = 0.50.

Plus four supporting mechanisms (each < 1 day implementation):
3. PHASE-TRANSITION-SCHEDULER: trigger consolidation when K/N > 0.4 (pre-cliff).
4. RECONSOLIDATION-EDIT-WINDOW: bound memory editing to tau_recon steps post-write.
5. ACTIVE-INFERENCE-REPLAY: prioritize replay by prediction-error magnitude.
6. SCHEMA-ACCELERATED-WRITE: fast-track items with cosine > theta_schema to W_slow.

All mechanisms are pure outer-product algebra, CPU-only, no autograd required.
All are compatible with existing substrate N, W_fast, and retrieval infrastructure.

---

## Anchor candidates (rank-ordered by P_actionable x prerequisite order)

### 1. CLS-1 -- Dual-substrate split on continual stream (HIGHEST PRIORITY)

Anchor pointer: CLS-DUAL-SUBSTRATE-1 (new; not yet queued)
Substrate-product reading: Measures whether adding W_slow + offline replay recovers
  recall on oldest items in a long continual stream. Direct test of the missing
  cortical-slow-generalizer block. If HARD-PASS, full CLS architecture is achievable
  in 1-2 days of code. If HARD-FAIL, alpha and N_buffer selection need revision first.
Tier hint: CPU laptop; < 1 hr wall; uses existing W_fast infrastructure.
Why-now: Gate for all downstream CLS experiments. Cheapest decisive test; runs first.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: recall@1 on epoch-1 items >= 0.70 with dual-substrate
              vs <= 0.30 with W_fast alone (> 0.40 improvement)
  HARD-FAIL: recall@1 epoch-1 < 0.50 with dual-substrate (consolidation not working)
  MID-BAND: recall@1 epoch-1 in [0.50, 0.70] -- useful signal, alpha/N_buffer need tuning
  Stream: 1000-item continual (start with 1000 before scaling to 10K)
  Consolidation trigger: every N_buffer = 100 writes
  W_slow alpha: 0.01 (slow learner; main parameter to sweep if MID-BAND)
  Retrieval blend beta: 0.5 (equal weight; adjust based on item age)

### 2. CLS-2 -- KWW vs exponential decay fit (DIAGNOSTIC, independent of CLS-1)

Anchor pointer: CLS-KWW-DECAY-2 (new; not yet queued)
Substrate-product reading: Determines whether Sprint-2 frequency-decay is better
  described by stretched-exponential (beta < 1) than pure exponential (beta = 1).
  HARD-PASS means the existing frequency-decay code should be upgraded to KWW; the
  additional parameter beta gives better long-tail retention prediction. HARD-FAIL
  means pure exponential is sufficient and KWW adds no value.
Tier hint: CPU laptop; < 1 hr wall; modifies Sprint-2 frequency-decay code.
Why-now: Independent of CLS-1; can run in parallel. Sprint-2 code is the baseline.

Pre-reg bands:
  HARD-PASS: best-fit beta < 0.85 AND delta_BIC > 10 favoring KWW over exponential
  HARD-FAIL: best-fit beta > 0.95 (pure exponential; no benefit from KWW)
  MID-BAND: beta in [0.85, 0.95] (weak stretch; marginal benefit)
  Stream: 1000-step stream; 4 retrieval frequencies (10%, 30%, 70%, 100%)
  Retention measured at: t = 10, 50, 100, 500, 1000 steps

### 3. CLS-3 -- Reconsolidation window editing budget (DEPENDENT on CLS-1 pass or mid-band)

Anchor pointer: CLS-RECON-WINDOW-3 (new; not yet queued)
Substrate-product reading: Validates the editing budget: recall@1 >= 0.90 for
  K_edit = sqrt(N) sequential edits with bounded reconsolidation window.
  Directly validates the PP-225 editing story with a concrete interference budget.
  HARD-PASS gives a defensible product claim: "edit up to sqrt(N) facts without
  accuracy loss, with algebraic audit trail per edit."
Tier hint: CPU laptop; < 1 hr wall.
Why-now: Extends validated memory_editing capability (PP-225); incremental enhancement.

Pre-reg bands:
  HARD-PASS: recall@1 >= 0.90 for K_edit = sqrt(N) sequential edits
  HARD-FAIL: recall@1 < 0.70 for K_edit = sqrt(N)/2
  MID-BAND: recall@1 in [0.70, 0.90] for K_edit = sqrt(N)

### 4. CLS-4 -- Schema-accelerated write (DEPENDENT on CLS-1 pass)

Anchor pointer: CLS-SCHEMA-WRITE-4 (new; not yet queued)
Substrate-product reading: Tests whether schema-compatible items (high cosine to W_slow
  rows) retain better at long timescales than novel items. HARD-PASS enables the product
  claim "add domain schema to unlock accelerated learning in that domain" (upsell feature).
Tier hint: CPU laptop; < 1 hr wall.
Why-now: Requires W_slow (CLS-1 prerequisite).

Pre-reg bands:
  HARD-PASS: schema-compatible recall@1 > novel recall@1 by >= 0.15 at t = 500 writes
  HARD-FAIL: schema-compatible recall@1 <= novel recall@1 (no benefit from schema path)
  MID-BAND: schema-compatible recall@1 > novel by [0.05, 0.15]

### 5. CLS-5 -- Self-replay schema extraction (DEPENDENT on CLS-1 pass)

Anchor pointer: CLS-SELF-REPLAY-5 (new; not yet queued)
Substrate-product reading: Tests whether offline self-replay from W_fast rows into
  W_slow produces spontaneous dimensionality reduction (rank(W_slow) decreases with
  replay passes). HARD-PASS means W_slow spontaneously extracts schemas from episodes
  without external schema labels -- a key capability claim for the generalizer block.
Tier hint: CPU laptop; < 1 hr wall.
Why-now: Requires W_slow (CLS-1 prerequisite). Validates the NeuroDream/songbird
  self-replay mechanism at pure-algebra level.

Pre-reg bands:
  HARD-PASS: rank(W_slow, epsilon=0.01) at R=1000 <= 0.5 * rank at R=1
  HARD-FAIL: rank(W_slow) does NOT decrease with R
  MID-BAND: rank decreases but by < 50% (partial schema extraction)

---

## Recommended dispatch order

1. CLS-1 and CLS-2 in parallel (both CPU, independent, < 1 hr each)
2. If CLS-1 HARD-PASS or MID-BAND: queue CLS-3, CLS-4, CLS-5
3. If CLS-1 HARD-FAIL: sweep alpha (0.001, 0.01, 0.1) and N_buffer (50, 100, 500) first

---

## Context pointers (file paths, not summaries)

- Research note: d:/AI/hd-instrument/notes/research_drill_continual_full_cls_5x_2026-06-10.md
- Sprint-2 frequency-decay code: check data/ for Sprint-2 validated frequency-decay scripts
- Memory editing baseline: data/exp_PP-225/ metrics.json (validated memory_editing)
- K/N capacity cliff: data/exp_decompose_K_cliff/ metrics.json (K/N = 0.56 validated x2)
- Pool retrieval (blend architecture): data/exp_phase_b2_pool_size_sweep/ metrics.json
- Substrate capability map: d:/AI/hd-instrument/notes/substrate_capability_map.md
  (see "Continual learning" section: replay BWT recovery validated, Hebbian-only validated)

---

## Contract section

Research claims these mechanisms are ALGEBRAICALLY GROUNDED (not empirically validated):
- Dual-substrate CLS: grounded in McClelland 1995 CLS theory + NeuroDream 2025 NN validation.
- KWW decay: grounded in glass physics + biological memory literature.
- Reconsolidation window: grounded in ROME scaling law + Nader reconsolidation literature.
- Schema-accelerated write: grounded in Tse 2007/2011 schema consolidation experiments.
- Self-replay: grounded in songbird template learning + NeuroDream 2025.

None of the above have been run on the ACTUAL substrate yet. CLS-1 through CLS-5
are the pre-test gates. P_deflated values (0.40-0.50) reflect this.

Per [[feedback-drill-pretest-required]]: run CLS-1 (small 1000-item stream, CPU, < 1 hr)
BEFORE authorizing any engineering investment in W_slow infrastructure changes.

---

## Autonomy declaration

exp_dev determines: anchor ID naming, sweep grid widths, queue assignment (local_cpu vs
overnight_queue), exact code structure, hyperparameter ranges beyond those pre-registered
above, and whether to batch CLS-1 and CLS-2 into a single dispatch or run sequentially.
Research pre-reg bands are recommendations; exp_dev may tighten or relax before dispatch
based on substrate-specific constraints observed in code review.
