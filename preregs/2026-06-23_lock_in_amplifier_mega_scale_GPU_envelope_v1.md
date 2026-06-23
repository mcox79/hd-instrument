# Pre-registration: lock_in_amplifier_mega_scale_GPU_envelope_v1

**Date:** 2026-06-23
**Anchor:** lock_in_amplifier_mega_scale_GPU_envelope_v1
**Queue:** overnight_queue (GPU)
**N_DIM:** 32768, **Seeds:** 3 [7, 17, 23], **M:** 5000
**Timeout:** 7200s (2hr safety margin per USER spec)

## Scientific question

The smoke (N=1024, M=50, anchor lock_in_amplifier_hd_frequency_smoke_v1) was
HARD_PASS. The v1_FULL (N=8192, M=500, anchor
lock_in_amplifier_hd_frequency_v1_FULL) was chain-grade-eligible at substrate
scale with ~16x lift at P=64. Does the mechanism hold at LLM scale
(N_DIM=32768, M=5000) and where in (sigma, k_signal, P) does it saturate?

Mega-scale envelope mapping tells us the operating regime substrate-product
can claim for the lock-in primitive. If still works = formal chain-grade
promotion candidate. If fails at large M = scope-narrow chain-grade.

## Arms (6)

1. ARM_BASELINE_SINGLE_SHOT (reproduces Shannon-floor at sigma=128/256;
   expected baseline ~ 1/M = 0.0002 in deep noise band)
2. ARM_LOCK_IN_P16
3. ARM_LOCK_IN_P32
4. ARM_LOCK_IN_P64
5. ARM_LOCK_IN_P128
6. ARM_LOCK_IN_P256

## Sweeps

- sigma_sweep_MEGA = [8, 16, 32, 64, 128, 256, 512] (extends envelope; tests
  Shannon-floor at lock-in regime)
- k_signal_sweep = [31, 127, 1023, 4095] (coprime-to-N_DIM=32768; tests
  frequency invariance at scale)
- P_phases_sweep = [16, 32, 64, 128, 256] (extends P beyond v1; tests
  sqrt(P/2) law at mega-P)
- N_EVAL = 500
- seeds = [7, 17, 23]

## Pre-registered bands

**HARD-PASS (formal chain-grade promotion candidate):**
- ARM_LOCK_IN_P256 lift >= sqrt(P/2) = sqrt(128) = 11.31x over
  ARM_BASELINE_SINGLE_SHOT at the discriminating sigma (baseline recall in
  band [0.05, 0.30])
- cv (std/mean) across {seeds x k_signal} at ARM_LOCK_IN_P256 / discrim_sigma
  <= 0.20
- Frequency-invariance confirmed: CV of per-k mean-recall across the 4
  k_signal values <= 0.20 (lift uniform across coprime-to-N frequencies)
- Sanity self-tests pass:
    (a) P=1 endpoint: lock_in == baseline byte-for-byte across all sigmas
    (b) sigma=0 endpoint: lock-in protocol recovers signal exactly via
        cos^2 sum normalization (P in {16, 32, 64, 128, 256})
    (c) permutation orthogonality at N=32768: |roll(v,k) @ v / N| < 0.1 for
        k in {1, 127, 1023, 4095} on random gaussian v
    (d) low-sigma (sigma=2) all-arms recall >= 0.95: lock-in unnecessary
        below noise floor

**MIDDLE:** P256 lift in (2.0x, 5.0x) -- partial mechanism characterization;
tune P or k_signal further. Also MIDDLE if P256 lift > 5.0x but HP gate
fails on cv/base-in-band/freq-cv.

**HARD-FAIL:** ARM_LOCK_IN_P64 lift < 2.0x at N=32768, M=5000 -- mechanism
stops working at LLM scale; smoke + v1_FULL were small-regime artifacts;
chain-grade scope-narrow to M <= 500.

## Calibration rationale

HP factor 11.31x = sqrt(P/2) at P=256 is the TEXTBOOK lock-in amplifier
SNR-improvement factor (signal coheres as sum cos^2 = P/2; noise variance
grows as sum cos^2 = P/2; SNR lift = sqrt(P/2)). At P=256 this is sqrt(128).
The v1_FULL empirically observed ~16x at P=64 vs textbook sqrt(32)=5.65x --
exceeded prediction because ceiling at recall=1.0 hit below discriminating
sigma. Pre-reg uses TEXTBOOK prediction (not empirical ceiling-bound result)
as the chain-grade threshold to avoid post-hoc reframing.

HP cv <= 0.20 enforces lift is consistent across k_signal frequency choices
(mechanism is frequency-invariant within coprime-to-N subspace) and across
seeds (mechanism is codebook-realization-invariant).

HF threshold P64 lift < 2.0x ensures HF only when the mechanism fundamentally
fails at LLM scale, not when sqrt(P/2) factor is merely missed by a small
margin (that would be MIDDLE_BAND).

## N-suffix / protocol section

Anchor name contains NO _n<N> suffix; PROT-018/019/021 are no-op. Production
N_DIM=32768 is enforced inside the script via the SMOKE/FULL branch (FULL
sets N_DIM=32768). _seed_checkpoint is wired discipline-voluntarily per the
USER spec for mega-scale dispatches (per-seed checkpoint + restartable).

PROT-020 (GPU queue requires torch): script imports torch and uses
torch.cuda. Compliant.

## Timeout estimate

v1_FULL config (N=8192, M=500, seeds=3, sigmas=6, P_sweep=6, k=5) was
estimated at ~18min GPU. Mega-scale extension factors:
- N_DIM: 32768 vs 8192 = 4x (matmul is linear in N for (N_EVAL, N) x (N, M))
- M: 5000 vs 500 = 10x (matmul output dim)
- N_EVAL: 500 vs 200 = 2.5x
- P_SWEEP avg P higher (P_avg ~ 100 vs ~20 in v1 = ~5x in per-(seed,arm,k,sigma) inner loop)
- sigmas: 7 vs 6 = 1.17x
- k_signal: 4 vs 5 = 0.8x

Per-config cost scaling: (4 * 10 * 2.5 = 100x) inner matmul cost vs v1_FULL
per inner config, with config-count factor (1.17 * 0.8 * P-density) ~= 4x.
Total ~400x inner work * 18min = order-of-magnitude 30-60min on GPU per USER
spec; the dominant cost is the per-phase torch.roll + matmul over a (500,
32768) tensor against a (5000, 32768) codebook.

USER-specified timeout: 7200s (2hr safety margin). Use 7200s. Below the
PROT-019 _n>=8192 floor of 21600s because the anchor has no _n suffix and
the USER explicitly authorized 7200s as the safety margin.

formula:
  ceil(1.5 * v1_wall_s * 100 inner * 4 config) ~= 1.5 * 1080 * 100 * 4 = 648000s
  This is wildly high because v1 "1080s" already reflects most of the
  per-config cost; only the config-count factor compounds, not the inner
  matmul which is already in v1's wall.
  Better estimate: v1_wall (1080s) * (P-density 5x) * (N x M scaling 4 * 10 = 40x)
  But GPU bandwidth scales with N*M, not N*M per config; empirically a 40x
  matmul is ~40x wall = ~12 hours. USER spec 7200s assumes GPU bandwidth
  saturates at lower scale; if 7200s is exceeded the cell checkpoints out
  per-seed (resumable).

timeout_s = 7200 (USER spec; per-seed checkpoint enables resume)

## Checkpoint discipline

Script imports experiments._seed_checkpoint (write_partial_key +
resumable_seeds + aggregate_partials + write_metrics). Per-seed partials at
data/exp_<NAME>/partial_metrics_<seed>.json. Mid-run kill/OOM/timeout
resumes from completed seeds on next ship. Run_config N/M/run_mode guards
prevent smoke partials contaminating FULL resume.

## GPU-actually-used discipline (Fix #24)

Script imports torch and asserts cuda at non-smoke launch. All inner-loop ops
are torch.cuda tensors:
  - codebook construction: torch.randint on DEVICE
  - cue selection: tensor index on DEVICE
  - per-phase noise: torch.randn(generator on DEVICE)
  - roll: torch.roll on DEVICE (in-place GPU)
  - matmul: received @ codebook.T on DEVICE  -- the dominant cost
  - argmax: torch.argmax on DEVICE
No host-CPU transfers in the inner loop. Per-config wall is matmul-bound on
(500, 32768) x (32768, 5000).

GPU util target: >= 50% at peak during matmul phase. Validate via nvidia-smi
sampling during run if available; not a hard gate but a sanity check.

## REMOTE VERIFY checklist (post-ship)

1. Confirm queue_add.sh post-ship VERIFIED line ("present in remote
   overnight_queue/queue.json")
2. Poll data/recent_landings.jsonl + data/exp_lock_in_amplifier_mega_scale_GPU_envelope_v1/
   metrics.json on the remote
3. Per-arm per-sigma metrics readable (NOT only verdict_msg per Fix #28)
4. cv values present and computed across seeds*k_signal
5. freq_invariance_cv computed across k_signal values at P=256/discrim_sigma

## Outcome routing

- HARD_PASS -> Skunkworks landed-VET; if confirmed, formal chain-grade
  promotion candidate; atomize as substrate-native chain-grade primitive;
  hdlab/ primitive update SAME CYCLE per cadence rule (USER 2026-06-22).
- HARD_FAIL -> chain-grade scope-narrow to M <= 500; Research drill into
  why mechanism fails at LLM scale (matmul-noise dominates? cos basis
  collapses at this codebook density?); 2x revival drill.
- MIDDLE -> tune P or k_signal further; consider P=512 or k_signal=8191
  variants in next-arc cell.
