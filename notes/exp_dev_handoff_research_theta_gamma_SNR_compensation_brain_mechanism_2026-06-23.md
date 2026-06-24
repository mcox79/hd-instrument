# exp_dev hand-off — research: theta-gamma SNR compensation via brain-grounded structural compose

**Filed-by:** Research (Opus 4.7-1M) 2026-06-23
**Trigger:** Director + USER routing on theta-gamma nested v1 smoke HARD_FAIL (recall=0.906 vs single 0.994 at sigma=16). 2x drill on brain SNR compensation mechanisms identified 4 brain structural amplifiers (PV-sparsification + CA3-attractor + ACh-gating + STDP-compression); v1 compose tests cheapest 2 (sparse + cleanup) using substrate-validated primitives.
**Source research note:** `d:/AI/hd-instrument/notes/research_theta_gamma_SNR_compensation_brain_mechanism_2026-06-23.md`
**Pause state:** check `d:/AI/hd-instrument/data/orchestrator_paused.flag` at dispatch time.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off provides anchor candidates, pointers, and rationale. exp_dev owns the empirical-design decisions (exact arm layout, smoke gating, dispatch routing).

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (PRIMARY) — substrate_theta_gamma_nested_with_brain_compensation_smoke_v1

- **Substrate-product reading:** test whether brain-canonical structural compensators (sparse-codebook + per-gamma-cycle attractor cleanup) recover the structural SNR deficit (1.51x = 3.6 dB) of nested theta-gamma vs single-frequency at equal phase budget. If yes, substrate gains a multi-item-per-gamma-cycle buffer holding 4-8 items at recall >= 0.95 — the substrate-native analog of LLM attention window per gamma cycle.
- **Tier hint:** chain-grade-eligible IF Predictions 1 AND 2 both HARD_PASS (META atom = brain-compensated-nested recovers-and-exceeds single-frequency); otherwise MEASURED_MECHANISM or HARD_FAIL routes to TDM-gating v2.
- **Why now:** v1 nested cell HARD_FAILed at smoke; structural SNR deficit explained by brain-mechanism gap; compose cell uses ONLY substrate-validated primitives (CERT 592 sparse-bipolar + existing cleanup); cheap CPU smoke (~15-30min); directly answers "is brain-compose the missing structural piece?"

### ANCHOR 2 (CONDITIONAL on Anchor 1 MIDDLE_BAND or HARD_FAIL) — substrate_theta_gamma_tdm_gating_architecture_pivot_smoke_v2

- **Substrate-product reading:** replace cos-weighted accumulator with binary-gated phase-window item-slot encoding (TDM = time-division-multiplex, brain-canonical per Stream B). Each gamma slot holds ONE item with FULL SNR budget; query targets a specific (theta, gamma) slot rather than coherent-averaging across all phases. This is the architecture pivot if v1 brain-compose insufficient.
- **Tier hint:** novel mechanism; cap P_deflated 0.40 (untested architecture); HARD_PASS = recall@1 at sigma=32 >= single-frequency recall + 0.05.
- **Why now:** only dispatch AFTER Anchor 1 verdict; sequencing matters because Anchor 1 is cheaper and uses zero new primitives.

### ANCHOR 3 (DEFERRED if v1 HARD_PASS) — substrate_theta_gamma_brain_compose_FULL_v2

- **Substrate-product reading:** scale Anchor 1 to N=4096, M=500 on remote_cpu_queue ~45-90min. Production-scale validation of the v1 smoke HARD_PASS.
- **Tier hint:** chain-grade-eligible IF v1 HARD_PASS AND FULL confirms within +-0.05 recall bands.
- **Why now:** only dispatch AFTER Anchor 1 smoke HARD_PASS; production scale not warranted if smoke doesn't pass.

---

## Context pointers (read before authoring; do NOT re-read in hand-off)

- `d:/AI/hd-instrument/notes/research_theta_gamma_SNR_compensation_brain_mechanism_2026-06-23.md` (this drill's research note; L3-L4 contain the SNR algebra + pre-reg HARD bands)
- `d:/AI/hd-instrument/experiments/exp_substrate_theta_gamma_nested_oscillation_LM_v1.py` (v1 cell that HARD_FAILed at smoke; reuse `theta_gamma_nested_demod` and `single_lockin_demod` unchanged)
- `d:/AI/hd-instrument/preregs/2026-06-23_substrate_theta_gamma_nested_oscillation_LM_v1.md` (v1 prereg; reuse arm conventions)
- `d:/AI/hd-instrument/experiments/exp_lock_in_amplifier_hd_frequency_v1_FULL.py` (single-frequency chain-grade primitive; baseline reference)
- `d:/AI/hd-instrument/notes/next_iteration_composition_spec_2026-06-23.md` (Gap F spec context)
- `d:/AI/hd-instrument/notes/research_drill_lock_in_per_hop_composition_depth_2026-06-23.md` (sister drill on multi-hop lock-in)
- `d:/AI/hd-instrument/notes/research_drill_sparse_bipolar_depth_enc1_composition_2026-06-23.md` (CERT 592 sparse-bipolar context; substrate-validated)
- CERT 592 sparse-bipolar bundle-capacity (load-bearing chain-grade for sparsification compensator)
- `d:/AI/hd-instrument/hdlab/` — check for `sparse_bipolar.py` and `cleanup.py`; inline if not landed (~30+20 = ~50 lines)

---

## Pre-reg HARD bands (from research note L4, restated)

### HARD_PASS (any one suffices; if A+B both, chain-grade-eligible):
- **CRITERION_A:** ARM_NESTED_BRAIN_FULL recall@1 at sigma=16, N=4096 >= ARM_SINGLE_LOCKIN recall@1 - 0.02 (recovers within 2pp; brain-compose closes structural deficit)
- **CRITERION_B:** ARM_NESTED_BRAIN_FULL recall@1 at sigma=32 >= ARM_SINGLE_LOCKIN recall@1 + 0.05 (brain-compose BEATS single in mid-noise regime; per-cycle cleanup leverage)
- **CRITERION_C:** ablation arms (NESTED_SPARSE alone, NESTED_CLEANUP alone) each add >=0.10 recall vs NESTED_BASELINE at sigma=16 (load-bearing-ness per-compensator confirmed)

### HARD_FAIL:
- ARM_NESTED_BRAIN_FULL recall@1 <= ARM_NESTED_BASELINE recall@1 + 0.03 at ALL tested sigmas (compensators add NOTHING; pivot to Anchor 2 TDM-gating)
- OR ARM_NESTED_SPARSE alone < ARM_NESTED_BASELINE at sigma=16 (sparse-codebook breaks demod; substrate-incompatible)
- OR ARM_NESTED_CLEANUP alone catastrophically degrades at sigma=4 control (cleanup-snap-away pathology like ca3 cell)

### MIDDLE_BAND:
- ARM_NESTED_BRAIN_FULL exceeds NESTED_BASELINE by 0.05-0.10 but doesn't reach single-frequency baseline. Partial compensation; v2 tunes sparsity f-grid + cleanup tau-grid OR moves to TDM-gating (Anchor 2).

## Arm layout (5 arms, per research note L5 + negativity check #3 control)

1. ARM_SINGLE_LOCKIN (baseline; existing P=32 single-frequency lock-in on dense bipolar codebook)
2. ARM_NESTED_BASELINE (current v1 cell; theta-gamma demod on dense bipolar codebook; NO cleanup)
3. ARM_NESTED_SPARSE (theta-gamma demod on SPARSE-bipolar codebook f=0.02; NO cleanup)
4. ARM_NESTED_CLEANUP (theta-gamma demod on dense codebook; PER-GAMMA-CYCLE Hopfield cleanup with refuse-gate tau=0.3)
5. ARM_NESTED_BRAIN_FULL (sparse codebook + per-cycle cleanup; compose 3+4)
6. **[CONTROL]** ARM_SINGLE_LOCKIN_SPARSE (single-frequency lock-in on sparse codebook; isolates brain-compose load-bearing-ness from sparse-only load-bearing-ness per negativity-check #3)

Total 6 arms; cell can present as 5 official arms + 1 control without inflating verdict logic.

---

## Config (smoke, from research note)

- N=512, M=50, seeds=[7,17,23], sigmas=[4,8,16,32,64], N_EVAL=80
- P_theta=4, P_gamma=7 (total 28 nested phases)
- P_single=32 (single-frequency baseline; equivalent total phases)
- k_theta=1, k_gamma=31
- Sparse fraction f=0.02 (CERT 592 best regime)
- Cleanup: single Hopfield iteration (cosine-snap to nearest codebook), refuse if cosine_margin < 0.3
- Routing: local_cpu_queue (pure numpy; ~15-30min CPU)

## Config (full; gates on smoke HARD_PASS)

- N=4096, M=500, seeds=[7,17,23], sigmas=[4,8,16,32,64,128]
- P_theta=8, P_gamma=7 (total 56 nested phases)
- P_single=64
- Routing: remote_cpu_queue ~45-90min

---

## Contract (per [[exp_dev-cell-author-responsibilities]])

- Per [[feedback-fix26-predispatch-verify-the-referent-gate]]: run `tools/predispatch_check.py substrate_theta_gamma_nested_with_brain_compensation_smoke_v1` BEFORE cell-author spawn (catches duplicate dispatches; recent HARD_FAIL re-dispatches)
- Per [[feedback-long-cells-must-checkpoint-resume-restartable]]: per-seed checkpoint via `_seed_checkpoint.py` (reuse from v1 cell)
- Per [[feedback-foreground-vs-background-for-sequential-store-ledger-writes]]: smoke runs foreground (sequential Store + cert_ledger writes)
- Per [[feedback-fix17-runtime-measurement-strict]]: measure smoke wall_s before full dispatch
- Per [[feedback-fix14-spawn-budget-le-3]]: respect 3-in-flight ceiling
- Self-test mandatory (per `_instrumentation_selftest` pattern in v1 cell): P=1 endpoint, sigma=0 recovery, sparse-codebook generation correctness, cleanup-snap idempotence at sigma=0
- Cell-author smoke per `peek_arm_metrics.py` BEFORE any framing (Fix #28: read per-arm metrics, not verdict_msg)
- Per [[feedback-encoder-picks-emerge-from-data-not-user-arbitration]]: arm picks come from HARD-band data, not USER arbitration

## Autonomy declaration

exp_dev owns: exact cell-file name + path (anchor name above is canonical), smoke gating decision, per-arm metric instrumentation, refuse-gate threshold tau (research note suggests 0.3; exp_dev may tune within [0.2, 0.4] for substrate-tractability), checkpoint granularity, dispatch routing (local_cpu_queue smoke confirmed; full TBD per smoke result).

exp_dev does NOT own: HARD bands (pre-registered above; immutable post-dispatch), brain-grounded mechanism choice (sparse + cleanup; pivot to TDM-gating only if v1 HARD_FAIL), 5-arm structure (1 control + 4 ablation/compose; control is mandatory per negativity-check).

Research will NOT re-dispatch until exp_dev returns verdict OR routes back with structural blocker.
