# Pre-registration: lock_in_amplifier_hd_frequency_v1_FULL

**Date:** 2026-06-23
**Anchor:** lock_in_amplifier_hd_frequency_v1_FULL
**Queue:** overnight_queue (GPU)
**N:** 8192, **Seeds:** 3 [7, 17, 23], **M:** 500

## Scientific question

The smoke at N=1024, M=50 (anchor: lock_in_amplifier_hd_frequency_smoke_v1, verdict
HARD_PASS) confirmed a substrate-native "lock-in amplifier" mechanism: cyclic-
permutation as HD frequency carrier, transmit-side cos-weighting, demodulate-and-
match against codebook. P=32 lifted recall@1 8.17x over baseline at sigma=32
(in-band stress).

This FULL production-scale validation asks: does the mechanism scale to
N_DIM=8192 (8x linear), M=500 (10x capacity), with 5 coprime-to-N frequencies
{1, 7, 31, 127, 1023} and P up to 64? If yes, the substrate-native lock-in
amplifier is a chain-grade primitive across substrate scales.

## Pre-registered bands

**HARD-PASS:**
- ARM_LOCK_IN_P64 mean recall@1 lift >= 5.65x = sqrt(P/2) = sqrt(32) over
  ARM_BASELINE_SINGLE_SHOT at the discriminating sigma (baseline recall in
  band [0.05, 0.30]).
- cv (std/mean) across {seeds x k_signal} at ARM_LOCK_IN_P64 / discrim_sigma
  <= 0.20.
- Sanity self-tests pass:
    (a) P=1 endpoint: lock_in == baseline byte-for-byte at all sigmas
    (b) sigma=0 endpoint: lock-in v2 protocol recovers signal exactly via
        cos^2 sum normalization (P>=4)
    (c) permutation orthogonality at N=8192: |roll(v,k) @ v / N| < 0.1 for
        k in {1, 127, 1023} on random gaussian v

**MIDDLE:** lift in (1.0x baseline, 2.0x baseline) -- partial mechanism
characterization at P32; tune P or k_signal.

**HARD-FAIL:** ARM_LOCK_IN_P32 lift < 2.0x at discriminating sigma --
mechanism collapses at production scale; smoke result was small-regime
artifact.

## Calibration rationale

Pre-reg HP factor 5.65x = sqrt(P/2) at P=64 is the TEXTBOOK lock-in amplifier
SNR-improvement factor (signal coheres as sum cos^2 = P/2; noise variance grows
as sum cos^2 = P/2; SNR lift = sqrt(P/2)). At P=64 this is sqrt(32). The smoke
empirically observed 8.17x at P=32 vs textbook sqrt(16)=4x -- this exceeds the
prediction because the ceiling at recall=1.0 is hit at sigma below the
discriminating sigma. Pre-reg uses the textbook prediction (not the smoke's
ceiling-bound result) as the chain-grade threshold to avoid post-hoc reframing.

HP cv <= 0.20 enforces that lift is consistent across k_signal frequency choices
(mechanism is frequency-invariant within the coprime-to-N subspace) and across
seeds (mechanism is codebook-realization-invariant).

HF threshold P32 lift < 2.0x ensures we declare HF only when the mechanism
fundamentally fails at production scale, not when the textbook sqrt(P/2) factor
is merely missed by a small margin (that would be MIDDLE_BAND).

## N-suffix section

Anchor name does not include an _n<N> suffix; PROT-018 is a no-op. Production
N_DIM=8192 is enforced inside the script via the SMOKE/FULL branch (FULL sets
N_DIM=8192). PROT-019 timeout floor and PROT-021 checkpoint requirement also
trigger only with _n<N>; we wire _seed_checkpoint discipline-voluntarily.

## Timeout estimate

Smoke wall: 0.44s total at N=1024, M=50, seeds=2, sigmas=5, P_sweep={1,8,32}=3,
k_signal=1. Smoke per-(seed,arm,sigma,k) ~ 0.44/30 = 0.015s on CPU laptop.

FULL config: N=8192 (8x linear), M=500 (10x linear in matmul against codebook),
seeds=3, sigmas=6, P_sweep=6 (avg P higher), k_signal=5. Total configs:
3 * 6 * 6 * 5 = 540 vs smoke's 30 (18x).

Per-config inner cost: torch.cuda matmul N_EVAL=200 x N=8192 against codebook
M=500 + P roll/cos passes. GPU should run each config in <2s.
Estimate: 540 * 2 = 1080s = 18min wall on GPU.

Add 1.5x safety margin (per PROT-019 spirit): 1620s.

USER-specified timeout: 5400s (1.5hr safety margin). Use 5400s.

formula:
  ceil(1.5 * 0.44 * (8192/1024)^1.0 * (3/2)) = ceil(1.5 * 0.44 * 8 * 1.5) = 8
  This is wildly low because smoke ran on CPU at small scale; the dominant
  cost driver at production is the 18x config-count, not the per-config wall.
  Empirical estimate above (18min GPU) is the load-bearing number.

timeout_s = 5400

## Checkpoint discipline

Script imports experiments._seed_checkpoint (write_partial_key + resumable_seeds
+ aggregate_partials + write_metrics). Per-seed partials at
data/exp_<NAME>/partial_metrics_<seed>.json. Mid-run kill/OOM/timeout resumes
from completed seeds on next ship. Run_config N/M/run_mode guards prevent
smoke partials contaminating FULL resume.

## GPU-actually-used discipline (Fix #24)

Script imports torch and asserts cuda.is_available() at non-smoke launch
(falls back to CPU only for smoke / self-test). All inner-loop ops are
torch.cuda tensors:
  - codebook construction: torch.randint on DEVICE
  - cue selection: tensor index on DEVICE
  - per-phase noise: torch.randn(generator on DEVICE)
  - roll: torch.roll on DEVICE (in-place GPU)
  - matmul: received @ codebook.T on DEVICE
  - argmax: torch.argmax on DEVICE
No host-CPU transfers in the inner loop. Per-config wall is matmul-bound.

## REMOTE VERIFY checklist (post-ship)

1. Confirm queue_add.sh post-ship VERIFIED line ("present in remote
   overnight_queue/queue.json")
2. Poll data/recent_landings.jsonl + data/exp_lock_in_amplifier_hd_frequency_v1_FULL/
   metrics.json on the remote (path mirrors via remote_sync); if not landed
   in turn cycle, defer to landing_notifier
3. Per-arm per-sigma metrics readable (NOT only verdict_msg per Fix #28)
4. cv values present and computed across seeds*k_signal
