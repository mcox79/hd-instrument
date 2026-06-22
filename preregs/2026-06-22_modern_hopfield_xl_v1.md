# modern_hopfield_xl_v1 -- Krotov exponential-energy Hopfield vs Classical Hebbian at LLM-class scale

**Date:** 2026-06-22
**Cell:** experiments/exp_modern_hopfield_xl_v1.py
**Lane:** USER strategic vision -- substrate-as-LLM-substitute storage. Modern Hopfield's
super-linear capacity could lift the substrate's storage ceiling by orders of magnitude.
**Queue:** overnight_queue (GPU; 4060 Ti)

## Scientific question

Classical Hopfield (1982 Hebbian) caps at M ~ 0.14 * N. The substrate's current W matrix
uses linear Hebbian and therefore inherits this 0.14*N bound. Krotov-style Modern Hopfield
(Ramsauer et al 2020 NeurIPS) with exponential-energy retrieval has theoretical
super-linear capacity M = O(exp(N)). Does this lift survive at LLM-class N=65536 with
M up to 10000 (above classical bound 0.14 * 65536 = 9175)?

This is a mechanism-discriminator cell: it must show that modern Hopfield BEATS classical
above its own capacity bound, not merely that modern works.

## Mechanism (exact formula)

Bipolar L2-normalized HD keys K (M, N). Noised query q = normalize(true_key + noise),
noise ~ N(0, 0.1 * I) on the bipolar key.

- **MODERN_HOPFIELD** (one-shot Krotov retrieval; Ramsauer 2020 formula):
  - sims = q @ K.T          shape (M,)
  - w = softmax(beta * sims) shape (M,)
  - ret = w @ K              shape (N,) -- the attractor superposition
  - top1 = argmax(K @ ret)
  - Batched: all (NQ,) probes share K via a single (NQ, M) matmul.

- **CLASSICAL_HEBBIAN** (Hopfield 1982; substrate's current storage):
  - Implicit W = (1/N) * K.T @ K never materialized (17 GB at N=65536).
  - y = W @ q = (1/N) * K.T @ (K @ q) shape (N,) -- one Hopfield update step.
  - top1 = argmax(K @ y).

- **SHUFFLED_QUERY** (mechanism-null floor):
  - Queries formed from RANDOMLY-PERMUTED keys (not the truth keys), same noise.
  - Run modern retrieval; compare to original truth indices.
  - Expected top-1 ~ 1/M (negligible at M=10000).

## Scale + dispatch

- N_DIM = 65536 (LLM-class; matches p1 v2 chain-grade ceiling 2026-06-22)
- M sweep = {1000, 2000, 5000, 10000}; alpha at M=10000 = 0.153 (above classical bound 0.14)
- beta sweep = {1.0, 2.0, 4.0, 8.0}; per (seed, M) the best-beta is reported for MODERN
- NQ = 100 noisy probes per arm per (seed, M)
- noise stdev = 0.1 on bipolar query
- seeds = [7, 17, 23] (3 seeds; cv across seeds reported)
- K (10000, 65536) fp32 = 2.62 GB; well within 4060 Ti's 8 GB VRAM
- Queue: overnight_queue (GPU mandate Fix #22; torch.cuda required)

## Pre-registered bands (locked from spawn prompt; both directions)

- **HARD_PASS at M=M_MAX=10000:**
  - MODERN_HOPFIELD best-beta top-1 >= 0.95
  - CLASSICAL_HEBBIAN top-1 <= 0.70
  - SHUFFLED_QUERY worst-beta top-1 <= 0.05
  - All seeds run; substrate-only gate (n_llm_calls == 0).

- **HARD_FAIL at M=M_MAX=10000:**
  - MODERN_HOPFIELD top-1 < 0.50, OR
  - (MODERN - CLASSICAL) gap < 0.10 (mechanism failed to beat classical above its bound), OR
  - SHUFFLED_QUERY top-1 > 0.05 (mechanism-null floor broken), OR
  - n_llm_calls != 0.

- **MIDDLE_BAND:** anything in between.

The discriminator pivot is M=10000 because the classical theoretical bound at N=65536 is
9175. M=10000 is the first load point that exceeds classical's capacity. If modern beats
classical there, super-linear capacity is empirically validated at LLM scale.

## Smoke gate evidence (pre-dispatch)

(Filled by cell-author at dispatch time)

- Local CPU --self-test: <PASS / FAIL with values>
- Remote GPU smoke (4060 Ti) wall + util: <s/s, util %>
- Smoke verdict: <HARD_PASS / HARD_FAIL / MIDDLE_BAND on tiny config>
- gpu_util_mean >= 50% steady-state (Fix #24): <PASS / FAIL>

## Discriminator-regime check (Fix #16)

At M=10000 (above classical bound 0.14*N=9175):
- MODERN >= 0.95 AND CLASSICAL <= 0.70 AND SHUFFLED <= 0.05  -> mechanism discriminating + working
- MODERN < 0.50 OR (MODERN - CLASSICAL) < 0.10                 -> mechanism null or non-discriminating
- The cell is "by-construction-discriminating": classical Hopfield's well-known capacity
  cliff at alpha=0.14 is what makes M=10000 the discriminator; if modern doesn't beat it,
  there is no super-linear lift.

## What this DOESN'T claim

- Does NOT claim modern Hopfield is drop-in for substrate W (integration cost unmeasured;
  this is mechanism viability + capacity-ceiling lift only).
- Does NOT claim noise-tolerance bounds (single stdev=0.1; orthogonal axis).
- Does NOT extend below N=65536 or above M=10000 (capacity-cliff sweep stops at 10000).
- Does NOT measure write throughput or update dynamics (one-shot retrieval only).
- Does NOT verify cross-encoder portability.

The claim if HARD_PASS: Krotov Modern Hopfield retrieval at LLM-class N=65536 achieves
>=95% top-1 at M=10000 (above classical 0.14*N bound) where classical caps at <=70%.
This is a capacity-ceiling lift candidate atom.

## Proposed atom ID (Skunkworks A5; if chain-grade)

math::T3/EXP_modern_hopfield_xl_v1 -- capacity-ceiling-lift candidate
(super-linear Krotov retrieval at N=65536, M=10000 above classical bound).

## SCHEMA-VET notes

This cell is a sibling of math::T3/EXP_p1_v2_action_at_any_position_LLM_class_v1 (CERT
588; chain-grade) on the storage-mechanism axis. Both run at N_DIM=65536 on the same GPU
runner with implicit-W discipline. The mechanism comparison (modern vs classical) is
empirically falsifiable AND mechanism-discriminating per Fix #16.

If HARD_PASS, this opens a substrate-architecture migration drill (linear-Hebbian-W -->
softmax-Krotov-W) which Research must lead with cost/benefit analysis (compute per write
+ retrieve, integration with CLS-replay, continual-learning interaction). If HARD_FAIL
the substrate's current 0.14*N bound is empirically confirmed at LLM scale and the
storage-ceiling-lift candidate is ruled out via this mechanism (route to 2x-revival drill:
Sparse Modern Hopfield variant per the 2026-06-16 sparse_hopfield_win_regime memo).

-- Exp-Dev (Prover); cell-author dispatch cycle 2026-06-22
