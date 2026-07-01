# Pre-reg: multihop_reasoning_vc_axis_sweep_gpu_v1

**Date:** 2026-07-01
**Cell:** experiments/exp_multihop_reasoning_vc_axis_sweep_gpu_v1.py
**Anchor:** multihop_reasoning_vc_axis_sweep_gpu_v1
**Parents:**
- Cell: exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1 (Landing 6 family)
- Cell: exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1 (Landing 10 family)
- Sibling: exp_multihop_reasoning_scale_invariance_N_axis_gpu_v1 (CG-expansion axis (a); N-axis)
- Sibling: exp_multihop_reasoning_partition_size_sweep_gpu_v1 (CG-expansion axis (b); PART_SIZE-axis; Wave 14 SCALE_VARIANT)
- Prereg: preregs/2026-07-01_multihop_reasoning_partition_size_sweep_gpu_v1.md
**Author role:** hdi_exp_dev (via Director spawn 2026-07-01)

**Prior-work check (substrate-KB concept-query 2026-07-01, exp_dev on spawn):**
- Q "multihop V_C vocabulary size axis scale invariance": top hits at cosine=0.28 (below 0.30
  novelty threshold):
  - Rank 1 (0.279): 'Multihop' entity from `notes/orchestrator_to_research_results_summary_2026-06-09_cycle205.md`
  - Rank 2 (0.257): 'C3. Vocabulary size and Zipf coverage' — different mechanism (lexical fluency)
  - Rank 3 (0.255): 'Variant 3: Larger concept vocabulary (V_c sweep)' — earlier design variant note
- Rediscovery-vs-novel: **GENUINELY NEW** along the V_C-axis. No prior cell sweeps V_C at
  fixed N=8192, PART_SIZE=10 as multihop per-step chain-cleanup probe. The Landing-21 LLN cell
  showed V_C-axis affects OOD leak floor (sqrt(2 log V_C / N)) — different mechanism.
- Reproducer arm at V_C=200 must reproduce parent REFs (0.858 at d=15, 0.682 at d=30) as
  internal consistency check.

---

## Purpose / hypothesis

Atom 11 (Skunkworks 2026-07-01, MM_STANDARD) claims per-step accuracy of partition-oracle
multihop is invariant across depths d=15-60 at fixed N=8192, PART_SIZE=10. Skunkworks named
three CG-expansion axes; this cell adds a **fourth orthogonal axis** to the multihop
phase-diagram characterization:
- (a) different N at same PART_SIZE — covered by sibling N_axis cell
- (b) different PART_SIZE at same N — sibling PS-axis cell (Wave 14: SCALE_VARIANT)
- (c) extended depth — deferred
- **(d) different V_C at same PART_SIZE, same N — this cell**

**Hypothesis (LOAD-BEARING):** partition-oracle per-hop cleanup accuracy at fixed depth is
invariant to V_C ∈ {100, 200, 400} at N=8192, PART_SIZE=10. If per_step_mean(d=15, V_C) is
within ±0.05 of REF_15HOP=0.858 for all three V_C values, and per_step_mean(d=30, V_C) is
within ±0.05 of REF_30HOP=0.682, this satisfies CG-expansion axis (d) and lifts Atom 11 to
CG on V_C-axis.

**Motivating mechanistic prediction:** if the PS-axis sibling showed per-step degrades with
PART_SIZE (SCALE_VARIANT), the natural interpretation is that chain-cleanup is
argmax-cleanup-arity-limited (PART_SIZE-limited). Under that model, holding PART_SIZE fixed
while varying V_C should yield SCALE_INVARIANT per_step because the local cleanup arity
is the operative bottleneck, not total vocabulary size. If instead per_step degrades with
V_C at fixed PART_SIZE, that falsifies the "PART_SIZE-limited-cleanup" reading and points
to a total-vocabulary-density effect (more concepts in W → more binding-noise from bystanders).

**Alternative outcomes (informational):**
- Per_step degrades monotonically with V_C: total-vocab-density-limited (informative)
- Per_step improves monotonically with V_C: unexpected; probably chain-diversity effect
  (larger V_C means chain-nodes more spread; fewer collisions per chain)
- Non-monotonic: anomaly, requires investigation

## HYPOTHESIZED vs MEASURED discipline (META_RULE_AC)

REFs re-verified off-disk against parent cells 2026-07-01 (same sources as PS-axis prereg):
- `data/exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1/metrics.json`
  d=15 per_step_acc mean across seeds {11,13,19} = 0.8517, 0.8570, 0.8427; pooled 0.850
- `data/exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1/metrics.json`
  d=15 pooled 0.858; d=30 pooled 0.682

**Convention chosen (matches sibling cells):** `per_step_mean` primary; `per_step_geometric =
top1^(1/depth)` reported informationally per-arm (Atom 11 spawn-cited derived-per-hop form).

## Cell design

### Substrate config (holds fixed across arms)
- N = 8192 (dimensionality)
- V_P = 10 (predicates)
- K_set = 20 (bindings per cue)
- n_chains = 200
- max_depth = 30 (built once per V_C; d=15 slice reuses same chains)
- PART_SIZE = 10 (fixed)
- Encoder = bipolar substrate-native (E, R on cuda; row-normalized)
- Binding = elementwise product; scale sqrt(N); Hebbian outer-product ingest

### V_C axis (the sweep)
- V_C ∈ {100, 200, 400}  → n_partitions = V_C / PART_SIZE ∈ {10, 20, 40}

Declared confound: n_partitions varies with V_C (since PART_SIZE fixed at 10). This is the
INHERENT structure of "vary V_C at same PART_SIZE" — the argmax-cleanup arity is HELD FIXED
at 10 candidates (design purpose), but the number of partitions to route through varies.
CRLB floor 0.10 is CONSTANT across all 6 arms.

### Arms (6)
- `ARM_D15_VC100`:  d=15  V_C=100  n_partitions=10  (V_C rail; smaller vocab)
- `ARM_D30_VC100`:  d=30  V_C=100  n_partitions=10  (V_C rail; smaller vocab)
- `ARM_D15_VC200`:  d=15  V_C=200  n_partitions=20  (reproducer / parent regime)
- `ARM_D30_VC200`:  d=30  V_C=200  n_partitions=20  (reproducer / parent regime)
- `ARM_D15_VC400`:  d=15  V_C=400  n_partitions=40  (V_C rail; larger vocab)
- `ARM_D30_VC400`:  d=30  V_C=400  n_partitions=40  (V_C rail; larger vocab)

Per V_C: fresh E (bipolar V_C x N), fresh chains + W (chains sample nodes from V_C so V_C
is a chain-construction parameter and must be rebuilt). d=15 and d=30 within the same V_C
share the same E/chains/W (d=15 uses chain-prefix slice), isolating depth as sole varier
within a V_C. Across V_C, only V_C changes (PART_SIZE, N, V_P, n_chains, max_depth, seed
sequence are held fixed).

### Seeds
[7, 13, 19] — 3 seeds per arm. EXPECTED_N_UNITS = 3.

CARDINALITY_OK = True; verdict emits HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if
observed_n_units < 3.

### Verdict gates (LOCKED at module init; META_RULE_L strictly-above-floor applied)

**Reference values (all MEASURED @ N=8192, PART_SIZE=10, V_C=200):**
- REF_15HOP = 0.858 (pooled 6 values from parent extension + ceiling cells)
- REF_30HOP = 0.682 (pooled 3 values from ceiling cell)

**HP_D15_VC<v>** (per V_C v in {100, 200, 400}):
- HARD_PASS iff |per_step_mean(d=15, v) - 0.858| <= 0.05 AND cv_across_seeds <= 0.10

**HP_D30_VC<v>** (per V_C v):
- HARD_PASS iff |per_step_mean(d=30, v) - 0.682| <= 0.05 AND cv_across_seeds <= 0.10

**HF_SCALE_VARIANCE** (any arm):
- HARD_FAIL iff |per_step_mean - REF| > 0.10 at any of the 6 arms

**HF_MECHANISM_DEATH** (any arm):
- HARD_FAIL iff top1 < 0.10 at any arm (mechanism cliff)

**Verdict tiers:**
- `CHAIN_GRADE_SCALE_INVARIANT_VC_AXIS`   — all 6 arms HP; Atom 11 CG-lift on V_C-axis;
  PART_SIZE-limited-cleanup hypothesis SUPPORTED (complements PS-axis SCALE_VARIANT)
- `PARTIAL_SCALE_INVARIANT_D15_ONLY`      — all d=15 arms HP; d=30 mixed
- `PARTIAL_SCALE_INVARIANT_D30_ONLY`      — all d=30 arms HP; d=15 mixed (unlikely)
- `PARTIAL_SCALE_INVARIANT_MIDDLE_VC_ONLY`— only V_C=200 reproducer HP (rail failure)
- `SCALE_VARIANT_VC_AXIS`                 — HF_SCALE_VARIANCE fires; total-vocab-density
  effect present; PART_SIZE-limited-cleanup reading FALSIFIED
- `MECHANISM_DEATH`                       — HF_MECHANISM_DEATH fires
- `MIDDLE_BAND`                           — inconclusive
- `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` — insufficient seeds

### CRLB floor (META_RULE_9)

Per-arm floor = 1/PART_SIZE = 0.10 (constant across all arms since PART_SIZE fixed):
- All V_C: CRLB floor = 0.100

All parent REFs (per_step_mean 0.68-0.86) sit well above the floor; discriminator window
HP band (REF ± 0.05) reachable by construction at V_C=200 reproducer arm (parent CG
demonstrates it); HF_MECHANISM_DEATH (top1 < 0.10) reachable at all arms (floor 0.10 at
the death boundary; mechanism failure would push top1 below 0.10).

### Discriminator reachability

Both HP + HF sides reachable per V_C:
- HP: reached at V_C=200 reproducer regime by construction
- HF_SCALE_VARIANCE: reached if V_C genuinely shifts per_step by > 0.10 (empirical question;
  hypothesis is INVARIANT under PART_SIZE-limited-cleanup model)
- HF_MECHANISM_DEATH: reached at all V_C (crlb floor 0.10 is at death boundary)

### Discriminator-survives-scale (USER 2026-06-26 rule)

Smoke uses full-N=8192 with n_chains=30 (reduced) but same V_C grid + PART_SIZE=10.
Reproducer arm (V_C=200) at full-N smoke must show top1 within loose window (smoke
n_chains=30 inflates top1 vs full n_chains=200 due to reduced W-interference; smoke
gate only asserts mechanism operates end-to-end at all 6 arms). This satisfies Check A
(smoke at full-N).

## Wall estimate
Sibling PS-axis cell (~268 MB W at N=8192) landed in ~200-300s per 3-seed run on GPU with 6
arms. This cell rebuilds E + chains + W per V_C (3x per seed) vs 1x in PS-axis. Expected
seed wall ~150-200s on GPU (3x the ingest cost); total ~500-600s for 3 seeds. Local CPU
smoke ~60-90s (1 seed, n_chains=30, 3 V_C rebuilds).

## Timeout
--timeout 3600 (60min hard cap; ample margin vs 500-600s estimate)

## Backend
torch.cuda (GPU) mandatory for full run; smoke OK on CPU.

## Queue
overnight_queue (GPU dispatch via hdi_orchestrator; harness-DENIED direct push)

## Dispatch pointer
Post-smoke handoff via SendMessage to hdi_orchestrator with commit hash + spec.
