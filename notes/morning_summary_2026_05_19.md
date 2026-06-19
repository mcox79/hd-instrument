# Morning summary — 2026-05-19

Read this first. Detailed log in `overnight_log.md`.

## TL;DR — 6 results landed overnight

1. **Substrate scales losslessly to N=65,536** (decisive positive). 100%
   recovery at every bundle size 2-128, every codebook size 32-2048,
   every N from 8K to 65K. Platform claim validated.

2. **VSA-pool is equivalent to classical pool** when properly tuned.
   The original 0.056 bpc deficit was softmax confidence ceiling at
   BYTE_BETA=8. At BYTE_BETA=16 the gap is 0.0001 bpc (saturated).

3. **Fix is universally robust** across pool weighting (ALPHA in
   {0.1, 0.3, 0.5, 0.7} all within ±0.005 bpc).

4. **CPU platform timing**: workstation 33/33 decompose-only, retrieve-only
   meets <100ms target at P ≤ 10K. Laptop similar but with smaller margins.
   At P=100K the bottleneck is cosine search (SIMD/ANN-fixable).

5. **M2 sleep consolidation design** synthesized from neuroscience survey.
   Five-step algorithm grounded in concrete biology
   (Mattar-Daw need × gain, CLS interleaved replay, Tononi-Cirelli
   downscaling). Design only — implementation awaits your review.

6. **BETA=16 fix is N-invariant** (added 03:40). Phase A + Phase B.2
   re-run at N=8192: pre-shift gap −0.0005, post-shift gap +0.0008
   (C2 marginally better than C1). Substrate behaves cleanly across
   tested N axis.

## What this changes about the program

**The headline C3 test got dramatically easier.** Before tonight: I worried
C3 (compositional retrieval) had to overcome ~0.06 bpc overhead from VSA
encoding to beat C1. After tonight: VSA encoding is information-preserving,
so C3 only needs to beat C1 by ANY margin. The pre-registered headline
test is now favorable to the substrate.

**The platform commitment is no longer speculative.** Scaling holds at
N=65K. Decomposition is fast enough on consumer hardware (workstation
all-good, laptop mostly-good with P=100K being the only break point).
The architectural story holds up under stress.

## What's next (in user-supervised priority)

1. **Phase B.3 (compositional retrieval)** — the headline experiment.
   Design needs your review before I build. With the BETA=16 fix in
   hand, the bar is just "beat C1 by anything."

2. **M2 sleep consolidation** — implementation from the design doc.
   This is the "system gets smarter on its own" capability. Design
   is complete, ready for supervised build.

3. **Platform engineering**: SIMD-optimized cosine search and mmap'd
   fixed-size pool format. Closes the P=100K latency gap on consumer CPU.

4. **Multimodal encoder bridge** (M3) — show 14.B works on vision/audio
   embeddings, not just byte atoms.

## What I deliberately did NOT do overnight

- No Phase B.3 implementation (architectural; needs review).
- No M2 implementation (architectural; needs review).
- No quantization or mmap engineering (architectural; needs review).
- No "improvements" to the resonator algorithm itself.

All adherent to the no-architectural-changes-overnight rule.

## State of the running infrastructure

- **GPU watchdog**: exited cleanly after 1hr idle. All queued experiments
  completed.
- **Both CPU watchdogs**: exited cleanly per design.
- **Cron schedule**: still firing every 30 min at :17 and :47. Each
  cycle reads queue state and would only act if there were new
  completed experiments or empty-queue triggers.
- **Origin/main**: ~15 commits ahead of where you went to sleep, all
  pushed. Recoverable from GitHub.

## Honest summary of the autonomous cycle

This is what the overnight setup was designed to do:
1. Run experiment → got negative (B.2 −0.056 bpc).
2. Launch unbiased research (bundle noise theory).
3. Misinterpret the theory (LLR factor → made it worse).
4. Honest re-analysis (softmax confidence ceiling).
5. Targeted experiment (BETA sweep → CONFIRMED).
6. Robustness follow-up (ALPHA × BETA=16 → universal).

The misinterpretation step was real — I applied per-coordinate Bayesian
calibration to an aggregate-cosine softmax readout, which was wrong.
The honest re-analysis caught it. The targeted experiment validated.

Each step committed and pushed. Nothing lost.

## Files to look at, in order

1. `notes/morning_summary_2026_05_19.md` — this file
2. `notes/overnight_log.md` — chronological cycle entries
3. `notes/master_plan_2026_05_18.md` — overall state, updated
4. `notes/wave14b_m2_consolidation_design.md` — M2 design (your call to implement)
5. `notes/wave14b_bundle_noise_theory.md` — math survey synthesis
6. `data/exp_wave14b_*` directories on remote — raw experimental data
