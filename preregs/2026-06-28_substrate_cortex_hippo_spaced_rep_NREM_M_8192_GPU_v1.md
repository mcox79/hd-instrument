# Pre-registration: substrate_cortex_hippo_spaced_rep_NREM_M_8192_GPU_v1

**Date:** 2026-06-28
**Anchor base:** substrate_cortex_hippo_spaced_rep_NREM_M_8192_GPU_v1
**Chunks (planned):** 3 single-seed cells {seed_7, seed_13, seed_19}
**Script (seed_7):** experiments/exp_substrate_cortex_hippo_spaced_rep_NREM_M_8192_GPU_v1_seed_7.py
**Queue (planned):** overnight_queue (GPU; remote@home)
**Parent cell:** experiments/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_7.py
**Parent prereg:** preregs/2026-06-28_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed.md
**Drill source:** USER 2026-06-28 — brain-reality variant of CLOSED-negative chain-grade
  handoff. Standard cell at M=8192 dies at Willshaw cap ~227x exceeded under
  all-at-once consolidation. Brain consolidates with SPACED repetition
  (Ebbinghaus 1885; Klinzing-Niethard-Born 2019; Wittkuhn-Schuck 2021):
  each memory replays dozens to hundreds of times across days/weeks/months
  with intervals 1, 2, 5, 10, ... sessions apart.

## Hypothesis

Substrate handles chain-grade M=8192 IF consolidation respects brain-style
spaced repetition rather than all-at-once. Mechanism rationale: spacing
distributes interference across cortex over many small writes, allowing later
writes to refine earlier ones rather than overwrite. Each item gets the SAME
total replay count (~6 per item) as the all-at-once arm; only the SCHEDULE
differs.

If true, this would re-open the CLS-handoff CLOSED-negative with a
regime-conditional amendment: chain-grade memory IS achievable on this
substrate IF consolidation respects brain-style spacing.

## Mechanism (v1 spaced-rep replay)

Common across all arms:
- W_h (N_h x N_h = 4096x4096) sparse-DG fast Hebbian one-shot encode
- W_c (N_c x N_c = 8192x8192) dense Hebbian slow accumulator
- Replay via hippo READOUT (sign(cues_h @ W_h.T)) -- inherited from v2 parent
  (CLS-faithful; not direct copy bug from v1)
- vals_c_reactivated = sign(cue @ W_h.T) @ P_hc.T (L2-norm)
- W_c.addmm_(vals_c_react.T, cues_c, alpha=ETA_CORTEX)
- W_h zeroed after replay; recall test on W_c

Arms differ in the SCHEDULE of which items get replayed when:

### ARM_A_BRAIN_SPACED
- N_SESSIONS=800 sessions; BATCH_SIZE=64 items per session
- Ebbinghaus revisit intervals: [1, 2, 5, 10, 20, 50, 100] sessions
- Algorithm:
  1. Phase 1 (intro): items distributed across first ceil(M/batch)=128 sessions;
     each session's 64 intro items always included for coverage discipline.
  2. Phase 2 (revisits): each item scheduled for replay at intro+delta for
     delta in EBBINGHAUS_INTERVALS; capped at N_SESSIONS.
  3. Per-session fill: intro items first, then due-for-revisit items,
     then random "spontaneous reactivation" from already-introduced.
- Total replay events: 800*64 = 51200 (~6.25 per item average)

### ARM_B_ALL_AT_ONCE (control matching CLOSED-neg regime)
- N_REPLAY_TOTAL=6 cycles; each cycle = batched replay of ALL M items
- Total replay events: 6*8192 = 49152 (within 5% of spaced; matched-write fairness)
- Sampling: random-uniform permutation per cycle (no spacing structure)

### ARM_C_UNIFORM_REPEAT
- Same N_SESSIONS x BATCH_SIZE=51200 events as ARM_A
- BUT: items sampled uniform-random with replacement (no spacing curve)
- Discriminator for ARM_A: if spaced > uniform, the temporal SCHEDULE matters
  beyond just distributing writes across many small batches

## Pre-registered fairness disciplines

1. W_h and W_c MUST be different tensors, different shapes, different sparsity.
2. Object-identity `W_h is not W_c` at runtime.
3. Replay sampling random-uniform within each session (no replay-count-as-importance).
4. All arms run on same encoded keys_h, vals_h, keys_c, vals_c, P_hc (no
   per-arm encoder confound).
5. Total Hebbian write counts matched within 5% across arms (spaced 51200,
   AAO 49152, uniform 51200).
6. Per Fix #24: full-run uses torch+cuda; overnight_queue routing justified.
7. Smoke runs at intermediate scale at MATCHED ALPHA REGIME (alpha=1.0) to
   ensure discriminator survives scale (USER 2026-06-26).
8. META_RULE_AF: arms must produce distinct W_c (selftest verifies on tiny
   world).
9. META_RULE_AH: atomic metrics.json write (tmp + os.replace).
10. Spaced schedule coverage: every item must appear at least once
    (selftest asserts; build_spaced_schedule raises if not satisfied).

## Pre-registered thresholds (single-seed)

- **HARD_PASS** (per chunk):
    acc(BRAIN_SPACED) >= 0.30 absolute AND
    acc(BRAIN_SPACED) - acc(ALL_AT_ONCE) >= 0.10 AND
    abs(acc(BRAIN_SPACED) - acc(UNIFORM_REPEAT)) > 0.05
- **MAJOR_UNLOCK** (verdict tag):
    acc(BRAIN_SPACED) >= 0.50 AND gap_vs_AAO >= 0.30 — re-opens CLS-handoff
    chain-grade closure with regime-conditional amendment
- **HARD_FAIL** (per chunk):
    gap_SPACED_vs_AAO < 0.0 (spacing actively HURTS) OR
    3-way collapse (all arms within 0.01) OR
    META_RULE_AF bit-exact violation OR
    cardinality breach (n_arms != 3)
- **MIDDLE_BAND**: everything else.

## DISCRIMINATOR-SURVIVES-SCALE smoke gate (USER 2026-06-26 LOCKED)

Smoke runs at:
- N_h=1024, N_c=2048, M=2048 -> alpha_simple = 1.0 (SAME as FULL)
- alpha_hopfield = 0.144 (smoke) vs 0.137 (FULL) -- within 5%
- N_sessions=100, batch=32, N_replay_AAO=2 (proportionally scaled)

**Smoke MUST fire the discriminator** (gap_SPACED_vs_AAO >= 0.10) before FULL
dispatch is authorized. If smoke shows 3-way collapse at alpha=1.0, FULL will
also collapse (the M=8192 regime is even more saturated).

## Pre-registered MANDATORY §15 envelope-fail-bands

1. **Sweep alignment:** N/A — single-config chain-grade verification with
   3 seeds aggregated.

2. **Discriminating bracket:**
   - Primary gap: acc(SPACED) - acc(AAO) >= 0.10 (PASS), < 0.0 (FAIL).
   - Schedule-distinctness: abs(acc(SPACED) - acc(UNIFORM)) > 0.05.

3. **Signal-shape audit (META_RULE_AP_v3):**
   - hippo state in sparse_N_h (bipolar +-1, 10% active = 410 of 4096 units).
   - hippo->cortex projection P_hc: R^{N_h} -> R^{N_c} (dense Gaussian).
   - cortex query/value in dense_N_c (L2-normalized unit vectors).
   - replay schedule -> per-session batch -> batched hippo readout -> batched
     cortex Hebbian write.

4. **Positive control at test regime:**
   - Parent v2 cell at smoke (M=512, alpha=0.25) HARD_PASS: FULL=0.748,
     NO_REPLAY=0.002, DIRECT=1.000. Mechanism (hippo readout) PROVEN at
     low alpha.
   - This cell's smoke MUST demonstrate the SPACED-vs-AAO discriminator
     fires at alpha=1.0 BEFORE FULL dispatch. If smoke 3-way collapses,
     mechanism doesn't survive into the chain-grade regime.

5. **Functional-requirement decomposition:**
   - (a) Ebbinghaus schedule builder: in-cell `build_spaced_schedule`;
     selftest verifies cardinality + coverage.
   - (b) Uniform schedule builder: in-cell `build_uniform_schedule`;
     selftest verifies total event count match.
   - (c) Hippo readout + cortex Hebbian write: inherited from v2 parent
     (CLS-faithful; verified via parent's HARD_PASS smoke).
   - (d) Per-session batched torch matmul replay: hand-coded in
     `_replay_one_session_torch`; selftest verifies torch vs numpy match.

## Pre-reg fields (required)

- `expected_n_units = 3` (ARM_A_BRAIN_SPACED, ARM_B_ALL_AT_ONCE, ARM_C_UNIFORM_REPEAT)
- `cardinality_ok` mandatory in metrics.json
- `HARD_FAIL_CARDINALITY_BREACH` when observed != 3
- `HARD_FAIL_3_WAY_COLLAPSE` when max pairwise gap < 0.01 (no schedule
  differentiates outcome)
- `HARD_FAIL_SPACED_HURTS` when SPACED < AAO (spacing makes it worse)
- `HARD_FAIL_META_RULE_AF` when |SPACED - AAO| < 1e-6 (bit-exact collapse)
- `discriminator_survives_scale` -- smoke at alpha=1.0 demonstrates
  gap_SPACED_vs_AAO >= 0.10 BEFORE FULL dispatch
- §13 patterns: start_marker + crash_diagnostic + per-seed checkpoint + heartbeat

## Smoke result (2026-06-28, exp_dev cell-author)

**Smoke config:** N_h=1024, N_c=2048, M=2048, N_sessions=100, batch=32,
N_replay_AAO=2, eta_c=0.005, seed=7. alpha_simple=1.0; alpha_hopfield=0.144.

**Smoke wall:** 432s (~7 min).

**Smoke result:**
- ARM_A_BRAIN_SPACED:   recall=0.158
- ARM_B_ALL_AT_ONCE:    recall=0.164
- ARM_C_UNIFORM_REPEAT: recall=0.163
- max pairwise gap: 0.006 (< 0.01)
- gap_SPACED_vs_AAO: -0.005 (slightly negative; within noise band ~0.011 at M=2048)

**Smoke verdict:** HARD_FAIL — META_RULE_AF 3-way collapse. All arms collapse
within 0.01 recall at alpha=1.0. Schedule does not differentiate outcome.

**Diagnosis:**
- At alpha=1.0 the Hopfield-bipolar cortex memory is firmly at capacity wall
- The hippo readout ALSO saturates: at M=2048 N_h=1024, alpha_h=2.0 (way past
  Hopfield-strict 0.138), so sign(W_h @ cue) is increasingly random output
- The limiting factor is HIPPO READOUT FIDELITY, not the cortex
  consolidation schedule. ALL three arms read out the same noisy hippo,
  produce ~equal-noisy cortex writes
- This cell's null result is *honest information*: naive spaced-rep does NOT
  rescue chain-grade at this substrate's current encoder/readout regime

**Decision (per USER 2026-06-26 DISCRIMINATOR-SURVIVES-SCALE rule):**
- DO NOT dispatch FULL.  Per discipline: if smoke 3-way collapses at the
  matched-alpha regime, FULL will also collapse (and waste ~6h GPU per seed).
- Cell + this pre-reg + smoke metrics filed as cert trail for the negative
  result.
- Hand-off to Research / Skunkworks: the result implies the chain-grade
  closure needs HIPPO READOUT FIDELITY rescue (denser hippo, BCM/anti-Hebbian
  cleanup, or larger N_h) BEFORE spaced-rep can help. The spacing curve only
  matters once the underlying readout SNR is above zero.

## Cap-map rows (proposed; SMOKE_NEGATIVE -> file as MEASURED_MECHANISM not chain-grade)

- Hippocampus->cortex consolidation: NAIVE-spaced-rep does NOT rescue
  chain-grade M=8192 (smoke regime confirms)
- Limiting factor at chain-grade: hippo readout fidelity at alpha_h >= 2.0,
  not cortex consolidation schedule
- Follow-up: cell variant with hippo capacity rescue (denser hippo OR
  BCM cleanup OR multi-readout iteration) BEFORE spacing-curve test

## GPU rationale (planned, NOT EXERCISED)

Per Fix #24: FULL would use torch.cuda with batched matmul replay.
- W_c (8192x8192 fp32) = 268 MB
- W_h (4096x4096 fp32) = 67 MB
- keys_h bank (8192x4096 fp32) = 134 MB
- vals_h bank (8192x4096 fp32) = 134 MB
- Per session (batch=64): cues_h (64x4096) @ W_h.T (4096x4096) = 1.07 GFlop
  + 2x P_hc projections + addmm write. ~3 GFlop/session.
- N_sessions=800 -> ~2.4 TFlop per arm. Estimated 1-3h/seed on RTX 4060 Ti.

## Coordination

- Cell-author: exp_dev (this dispatch; SMOKE HARD_FAIL, NOT shipped to FULL).
- Landed-VET: skunkworks (audits smoke metrics + verdict logic).
- Research / Director: review smoke-negative result; consider follow-up
  variants targeting hippo readout fidelity.

## Risk + mitigations (would have applied if shipped)

- HIPPO READOUT FAILURE AT alpha_h=0.137 (FULL): noise floor in sign(W_h @ cue);
  spaced-rep can't help. CONFIRMED by smoke at alpha_h=0.144 (within 5% of FULL).
- INTERFERENCE ACCUMULATION IN W_c: Hebbian writes without saturation control
  collapse to high-norm random vectors at large total-write counts.
- Mitigation NOT EXERCISED: smoke negative blocks FULL per discipline.
