# exp_dev hand-off — v195 pipeline refill (queue=0 emergency)

**Filed:** 2026-05-24 by orchestrator (sub-agent context; main thread will dispatch exp_dev wrapper).

**Trigger:** 6-verdict batch processed at v195; all 6 closed/saturated. GPU queue, CPU queue, local queue all at 0. ACTIVE (no pause flag). Pipeline-pacing reflex gates fired — refill is priority #1.

**Pause state:** ACTIVE (`data/orchestrator_paused.flag` absent).

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## What just closed (6-verdict batch v195)

1. **MOE_KSWEEP_HARD_FAIL_REJECTED** — R-PRIME-2 user's #1 hypothesis KILLED; lift=0.004 flat in K. MoE-on-substrate REJECTED.
2. **K6_HARD_FAIL_NO_GENERALIZATION** — K6 axis 2 (hold-out compositional eval) REJECTED at higher N; no compositional generalization at the tested envelope.
3. **LYAP_HARD_FAIL_FAR_FROM_EDGE** — Field-A reservoir-computing Lyapunov spectrum REJECTED; substrate is firmly chaotic at the operating point, not edge-of-chaos.
4. **KKL_HARD_PASS_LOW_INFLUENCE** — F-6 Boolean axis PASSES at all operating points; substrate boundaries are low-influence/well-distributed. Move 🔬 → 🟡 candidate.
5. **RPRIME3_R1_HARD_FAIL_GEOMETRY_NARROWED** — R-PRIME-3 R1 alternative-geometry rescue FAILS; move to R2 (sub-corpus scale).
6. **BETM_LOGFORGET_MIDDLE_BAND** — 4/5 BIC fits log-form (median gap 2.23, borderline); D_exp wins on 5/5 seeds vs B_log on 4/5; logarithmic-forgetting hypothesis WEAKLY SUPPORTED, exponential decay CONTENDER.

---

## Top-N ANCHORS for refill (rank-ordered; exp_dev picks 6 across queues)

Pick at least 2 GPU + 3 CPU + 1 local per the user's queue-depth directive. exp_dev decides per-anchor queue routing per the Tier A/B/C policy in `agents/exp_dev.md` Section 0.

### Anchor candidates (in priority order)

1. **R-PRIME-1 PAC-Bayes KL-accumulation floor — empirical probe**
   - Anchor pointer: `notes/strategy_decisions_2026-05-24.md` Ship 1 reassignment (post-R-PRIME-3 closure).
   - Substrate-product reading: with task-pair-geometry REJECTED (v193 + v195 R-PRIME-3 R1 narrowing), PAC-Bayes KL-accumulation between task posteriors is the next-leading geometry-free retention floor framing per [[feedback-dont-overextend-theorems]].
   - Tier: likely GPU (multi-task, multi-N).
   - Why now: PROMOTED at v193 from Ship 6 to Ship 1; R-PRIME-3 R1 closure at v195 doubles this priority.

2. **Bet M logarithmic-forgetting LONGER-T fit (R3 Ebbinghaus longer-t)**
   - Anchor pointer: v195 BETM_LOGFORGET_MIDDLE_BAND verdict; existing t=1..21 sweep needs extension to t in {1..200} per v192 rescue R3.
   - Substrate-product reading: 4/5 BIC fits log at borderline gap; longer-t resolves whether log-form survives or D_exp wins decisively. Closed-form predictor candidate either way.
   - Tier: likely Remote CPU (long chain, single-config).
   - Why now: verdict is borderline; longer-t is the clean resolver.

3. **K2 4-stage M1 hierarchical replay (mechanism-class rescue)**
   - Anchor pointer: v193 K2 axis 3 SATURATION; M1 rescue filed inline ("replay sub-task chunks not whole tasks").
   - Substrate-product reading: all 3 tuning axes (N + epochs / Phase-A consolidation / Phase-D weighting) saturated at retA~0.74; mechanism-class change is the leverage path.
   - Tier: GPU (4-stage continual chain).
   - Why now: K2 row is leading promotable candidate; mechanism-class rescue is the gate.

4. **K6 axis 2 hierarchical composition pre-binding (mechanism-class rescue)**
   - Anchor pointer: v193 K6 axis 1 N-scaling SATURATION-AT-SCALE; axes 2/3/4 remain.
   - Substrate-product reading: dim-scaling exhausted; axis 2 (explicit hierarchical composition pre-binding) is the leading remaining axis per v195 closure narrative.
   - Tier: GPU.
   - Why now: K6 row state hinges on axis 2/3/4 outcome; sequencing the cheapest mechanism-class probe first per PROT-004 cheapest-first rule.

5. **F-6 Boolean envelope-expansion drill**
   - Anchor pointer: v195 KKL_HARD_PASS_LOW_INFLUENCE verdict; F-6 Boolean substrate boundaries PASS at tested density envelope.
   - Substrate-product reading: F-6 row moves 🔬 → 🟡 candidate; envelope expansion to broader density / codebook / N envelope per [[feedback-envelope-expansion-fail-bands]] is the validation gate for promotion to ✅.
   - Tier: CPU or local (post-hoc analysis on existing infrastructure + broader sweep).
   - Why now: clean PASS at a new envelope; expand the envelope per the validation discipline before any promotion.

6. **Bet D analyzer pass at K=32 / K=64 (Ship 3 from v192 prioritized roadmap)**
   - Anchor pointer: `notes/orchestrator_prioritized_roadmap_2026-05-24.md` Ship 3.
   - Substrate-product reading: analyzer-only, near-zero compute, extends Gap(K) curve from 4 to 6 points enabling AGS-scaling fit. Synergistic with Path 3 AGS scaling-law extrapolation already shipping (v191).
   - Tier: local (analyzer-only).
   - Why now: cheap; fills local queue; analyzer pass on existing checkpoints with no fresh model training.

### Stretch candidates (if exp_dev has bandwidth for 7+)

7. **R-PRIME-3 R2 sub-corpus geometry rescue** — alt-scale geometry probe (within-corpus chunks not between-corpus pairs); R1 narrowing closed but R2 preserves the broader idea space.
8. **K2 M3 explicit memory consolidation (sleep-cycle simulation)** — mechanism-class rescue from v193 inline list.

---

## Context pointers (pointers, not summaries)

- `notes/substrate_capability_map.md` — current cap_map v195 (this batch); read latest block.
- `notes/orchestrator_prioritized_roadmap_2026-05-24.md` — Ship 1-5 + reserved; R-PRIME-3 + R-PRIME-2 (Ship 1 + Ship 4) closed by this batch.
- `notes/research_R_PRIME_directions_2026-05-24.md` — R-PRIME-1 through R-PRIME-6 directions (R-PRIME-2 + R-PRIME-3 closed; R-PRIME-1 elevated).
- `notes/research_existing_data_analyses_2026-05-24.md` — 6 prior shifts from zero-compute mining.
- `notes/research_field_scope_update_2026-05-24.md` — 8 NEW Tier-1b fields (nonequilibrium-stat-mech, mesoscopic-transport, structural-glasses-MCT, percolation, RMT-beyond-FP, network-science, sparse-coding, population-genetics) added to research scope; some anchors above may want to invoke these.
- Pause state line: ACTIVE (`data/orchestrator_paused.flag` absent).

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE smoke.
- Self-test per [[feedback-formula-selftests]].
- Multi-seed FULL on smoke clearance.
- Queue routing per Tier A/B/C in `agents/exp_dev.md` Section 0.
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- POST-SHIP REMOTE VERIFY via the queue_add.sh exit code (5 = post-ship verification failed) per [[feedback-ship-name-collision]].
- status_log entry per anchor with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: anchor name, N, M, K, seed count, threshold bands (HARD-PASS + HARD-FAIL), queue choice (Tier A/B/C), ETA, smoke profile, FULL profile. The orchestrator passes anchor POINTERS only. If exp_dev wants to substitute a different anchor from the recent verdict-rescue list (e.g., K2 M4 increased N at fixed M instead of M1 hierarchical replay), that's exp_dev's call.

---

## Filed by

Orchestrator main thread (sub-agent inline cycle), 2026-05-24, post v195 6-verdict batch. Hand-off ready for `/exp_dev notes/exp_dev_handoff_v195_pipeline_refill_2026-05-24.md` dispatch.

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
