# Pre-registration: substrate_c3_segregated_dual_W_spectrum_replication_v1

**Date:** 2026-06-24
**Anchor:** substrate_c3_segregated_dual_W_spectrum_replication_v1
**Queue:** local_cpu_queue
**N:** 4096, **Seeds:** [7, 17, 23], **J/M:** J=5 / M=400 (alpha_total=0.488)

## Scientific question

Does SPATIAL SEGREGATION of the CL update operator (cortex + hippocampus on
SEPARATE W matrices, with ONE-WAY replay coupling) rescue the
`exp_substrate_continual_learning_spectrum_v1` HARD_FAIL (forgetting_p1=0.65,
transfer=0.000 at alpha_total=0.49)? The CL spectrum cell HARD_FAILed because
cf-RPE delta-rule + Hebbian replay are antagonistic when applied to the SAME
W matrix (smoke-calibration note in cl-spectrum source, lines 168-181). The
brain solves this via spatial segregation: hippocampus does online Hebbian
write; cortex receives only one-way replayed patterns; no shared update
operator. This cell tests whether the brain-grounded segregated architecture
rescues substrate CL.

## Pre-registered bands

**HARD_PASS_CL_MOAT_REAL** (primary; substrate has a real CL moat):
- `ARM_SEGREGATED_DUAL_W_ONE_WAY_REPLAY` forgetting_p1 < 0.20
- `ARM_SEGREGATED_DUAL_W_ONE_WAY_REPLAY` transfer_final > 0.30
- delta vs `ARM_FUSED_W_CFRPE_HEBBIAN` >= 0.40
- cv (across seeds) < 0.05 required for cert tier

**HARD_PASS_PARTIAL** (some improvement; not full moat; reported as MIDDLE_BAND):
- forgetting_p1 in [0.20, 0.50]
- delta vs FUSED_W >= 0.15

**HARD_FAIL_DECISIVE** (segregation does NOT fix CL spectrum):
- forgetting_p1 >= 0.50 OR delta vs FUSED_W < 0.15
- Interpretation: deeper architectural redesign needed; route to research.

**MIDDLE_BAND:** characterized but doesn't clear HP_PARTIAL bars.

**Sanity rails:**
- `ARM_BASELINE_STATIC` phase-1 initial recall in [0.85, 1.00]
- `ARM_FUSED_W_CFRPE_HEBBIAN` forgetting_p1 in [0.55, 0.75]
  (reproduces cl-spectrum HARD_FAIL within +/- 0.10 of 0.65; verifies the
  harness reproduces prior HARD_FAIL and is not a measurement artifact)

## Calibration rationale

Forgetting_p1 < 0.20 chosen because cl-spectrum HARD_FAIL bar is > 0.50 and
HARD_PASS bar was <= 0.10 for the full system; 0.20 is a chain-grade-real
threshold halfway between the two (substrate must show SIGNIFICANT rescue,
not marginal). Transfer > 0.30 chosen because cl-spectrum transfer was 0.000
at the HARD_FAIL point; any non-trivial new-domain acquisition is a real lift
and 0.30 is the original cl-spectrum HARD_FAIL trip-line lower bound. Delta
vs FUSED_W >= 0.40 chosen because FUSED_W will reproduce cl-spectrum's 0.65
forgetting; a forgetting reduction of 0.40 to 0.25 or below isolates the
architectural-segregation contribution. cv < 0.05 enforces across-seed
reproducibility; one-way-replay architectures with strong recency weighting
should be highly seed-stable (replay schedule is deterministic given seed).

P(HARD_PASS_CL_MOAT_REAL) estimate: 0.55 (per research drill ANCHOR 1
recommendation, at novel-synthesis cap because substrate-internal diagnostic
comments at cl-spectrum lines 168-181 provided direct mechanism evidence).

## Apples-to-apples (Lane 1: substrate-native CL architecture comparison)

Same J=5, M=400, N_DIM=4096, alpha_total=0.488, 3 seeds, same probe protocol
(N_PROBE=60, NOISE_FRAC=0.20, N_RETRIEVE_STEPS=5), same metrics
(forgetting_p1, transfer_final), same synthetic-bipolar atoms per domain
permutation, same RECENCY_WEIGHT=4.0, same N_REPLAY_PASSES=10,
same N_CFRPE_PASSES=5, same ALPHA_FAST=1.0, ALPHA_SLOW=0.1, ALPHA_CFRPE=0.05.

ONLY the architecture (single-W vs dual-W) and the replay direction (none vs
scheduled hippo->cortex) vary across arms. K_BANKS routing is dropped from
all arms (cl-spectrum FULL_CL used K=2; this cell isolates the segregation
lever; K-bank routing is a separate architectural lever scheduled for c4
anchor per drill).

**INTRA_LANE_DELTA:** ARM 4 vs ARM 5 varies ONE thing (one-way replay
schedule on/off; both have identical dual-W structure and identical cf-RPE).

**Confound audit:**
- dual-W matrix-size matched to single-W (each is N_DIM x N_DIM; total memory
  doubles vs single-W but arm-internal architecture is the lever, not memory)
- replay schedule identical to spectrum cell's CLS_REPLAY (recency-weighted,
  same alpha_per_pass, same n_passes, same draw size)
- cf-RPE schedule identical to spectrum cell (same alpha, same n_passes)
- ARM_FUSED_W_CFRPE_HEBBIAN reproduces cl-spectrum FULL_CL minus K-bank
  routing; expected to reproduce forgetting~0.65 (sanity rail)

## N-suffix section

Anchor has NO `_n<N>` suffix (matches cl-spectrum anchor pattern). Production
N = 4096 encoded in script `N_DIM = 4096` constant and asserted at import.
PROT-018 binding satisfied via in-script assertion + run_config={"N":N_DIM}
checkpoint guard.

## Timeout estimate

Smoke (J=3, M=200, N=4096, 2 seeds, 5 arms): expected wall ~ 70-110s.
Full (J=5, M=400, N=4096, 3 seeds, 5 arms): each segregated arm has roughly
2x flops of cl-spectrum FULL_CL (two W's written per phase + cls-replay +
cf-RPE on cortex). cl-spectrum full wall was ~862s. Scaling estimate:
  ceil(1.5 * 862 * (5/5)^1.0 * (3/3) * 2.0_dual_W_factor) = ~2586s
PROT-019 floor for N>=4096 is 14400s (4h) when using `_n4096` suffix; this
anchor uses no suffix so PROT-019 does not enforce the floor. Setting
timeout_s = 5400s (1.5h) provides 2x headroom over the dual-W scaling
estimate; matches cl-spectrum's 5400s budget; checkpoint-resumable so
timeout interruption preserves per-seed work.

timeout_s = 5400

## Cell-author dispatch decisions

- Queue: local_cpu_queue (numpy-only; matches cl-spectrum routing; ~30-45 min
  wall well within local-CPU comfort budget; no remote SCP/SSH push needed)
- Per-seed checkpoint via experiments/_seed_checkpoint.py (PROT-021)
- atexit metrics synthesizer (writes metrics.json even on timeout/kill)
- 5 arms x 3 seeds = 15 unit runs per full execution
- Self-test gate: 4 formula self-tests + dual-W segregation invariant

## Cites

- experiments/exp_substrate_continual_learning_spectrum_v1.py (apples-to-apples base)
- experiments/exp_two_substrate_fastslow_cls_cpu_v1.py (substrate dual-store)
- experiments/exp_hippocampal_nonrecip_replay_v1.py (non-reciprocal replay)
- notes/exp_dev_handoff_research_continual_learning_architectural_revival_2x_drill_2026-06-24.md
- Research drill ANCHOR 1 recommendation: HIGHEST PRIORITY for closing
  cl-spectrum HARD_FAIL via substrate-mined primitive

## Strategic context

USER standing emphasis: CL is "big plus" + substrate has 6-of-11 brain-CL
primitives LANDED. CL spectrum HARD_FAIL was fused-W antagonism (per drill
diagnosis). Segregated dual-W tests if architectural separation rescues the
CL moat. HARD_PASS_CL_MOAT_REAL validates the substrate-product CL story;
HARD_FAIL_DECISIVE says deeper architectural redesign needed (route to
research for next-mechanism scour, e.g. cascade-STC-SWR depth states,
indexed-K8 routing).
