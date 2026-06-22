# Pre-reg: n4_kwta_soft_decode_v1

**Date:** 2026-06-22
**Anchor:** n4_kwta_soft_decode_v1
**Cell:** experiments/exp_n4_kwta_soft_decode_v1.py
**Source-of-truth pre-reg (brain-drill #1 L4 + L5):** notes/research_brain_within_concept_floor_5x_drill_2026-06-22.md
**Author:** Exp-Dev (brain-drill #1 payload; novel-synthesis P=0.40 capped per Research lit-scan calibration)

## Scientific question

Does top-k SOFT kWTA-VQ assignment (cerebellum / Kenyon-cell / dentate-gyrus
biological-sparsity analogue) at INGEST + READ of the substrate decode matrix
D LOWER the within-concept token-entropy floor relative to hard one-hot VQ at
V_C=1024, N_DIM=16384, K=1?

Bigram-gap closure (~1.13 bits substrate vs text8 bigram 3.844; ~2.9 bits to
ceiling at every PROJ_DIM) is the live L2-substrate frontier. Brain-drill #1
identifies coding-level f = k/V_C ~= 0.05-0.10 as the cerebellum / mushroom-
body / DG optimum (Litwin-Kumar 2017, Modi-Stevens 2020, Cayco-Gajic & Silver
2019). Substrate currently operates at f = 1/V_C ~= 0.001 -- 50-100x sparser
than biological optimum. Hypothesis: lifting coding level toward biological
optimum via top-k soft assignment lowers ceiling_bpc.

## Mechanism

Replace the hard `km.predict()` -> single-concept assignment with TOP-K SOFT
assignment + softmax(-dists/tau) weight; accumulate D over the top-k concepts
similarity-weighted at write; pool D over the top-k concept rows at read.

Forward-only Hebbian-compatible. Substrate-only-decode preserved (zero LLM
forward calls). Same V_C, same N_DIM. Just a `k > 1` knob on write+read.

Phase 1 grid: k in {1, 8, 32} (3 arms; brain-drill-spec).
  k=1: hard-one-hot anchor (must reproduce N2 ceiling_bpc=2.049 within 0.05)
  k=8: f_eff=0.008 (below biological optimum; multiplicity-direction test)
  k=32: f_eff=0.031 (approaching biological optimum at V_C=1024)
TAU=1.0 (softmax temperature; Phase-1 default).

## Fixed config

V_C=1024 ; N_DIM=16384 ; K=1 ; f=0.006 ; MAX_DOCS=100000 ; SEEDS=[7,17,23] ;
SPLIT=0.8 ; LAM_BACKOFF=0.1 ; INTERP_B=0.3 ; LR_DECODE=1.0 ;
TAU=1.0 ; K_GRID=[1, 8, 32] ; assignment_mode=top_k_soft.

## Pre-registered HARD bands (brain-drill #1 L4)

**HARD_PASS (chain-grade, ALL of):**
- some K_VALUE>1 has ceiling_bpc_mean <= 1.75 (>= 0.30 bits drop from N2's 2.049)
- same K_VALUE has substrate_bpc_mean <= 4.75 (>= 0.21 bits drop from N2's 4.959)
- substrate_bpc_cv <= 0.05 across 3 seeds for the passing K
- not saturated (alpha < 1.0)
- substrate-only-decode (LLM forward calls == 0; asserted + logged)
- best K != 1 (mechanism IS multiplicity; k=1 winning = noise effect)
- run_mode == "full" (no smoke-mislabel-as-full; Fix #5 pre-flight gate)

**HARD_PASS_PLUS:** substrate_bpc_mean < bigram_bpc=3.844 at some K (bigram-beating).

**MIDDLE_BAND (partial mechanism, ANY of):**
- ceiling_bpc drops 0.10-0.30 bits vs k=1 at some K>1
- substrate_bpc improves >= 0.10 bits vs k=1 but doesn't beat HARD_PASS bar

**HARD_FAIL (ALL preempt MIDDLE_BAND):**
- best ceiling_bpc change < 0.05 bits across all K>1 (mechanism falsified;
  route to n5 hippocampal-episodic + Path A V_C scaling per brain-drill Pred 5)
- OR anchor mismatch (K=1 ceiling differs from N2's 2.049 > 0.05 bits)
- OR substrate-only gate violated (LLM forward call counter > 0)
- OR wrong-direction (ceiling monotonically WORSE with K = soft averaging
  destructive at this V_C; brain-drill Prediction 1 falsified-with-sign)
- OR run_mode != "full" (stale smoke metric; Fix #5)

## Discriminating-regime guards (Fix #16, C5)

- **CAN-fail-low regime:** K=1 endpoint = current N2 baseline; must REPLICATE
  N2 ceiling=2.049 within 0.05 (the anchor check). Failure = harness corrupt.
- **CAN-fail-high regime:** brain-drill predicts k=32 in or near optimum band;
  if ALL K>1 arms FAIL to improve, hypothesis is falsified (HARD_FAIL).
- **NULLABILITY:** Prediction 4 (k=V_C uniform pooling -> unigram-level entropy)
  is NOT in Phase-1 grid; deferred to Phase-2 sanity probe at best-K if HARD_PASS.

## Version markers (BPC-affecting; AST-verified at selftest)

`CONFIG_VERSION` includes:
- `K_GRID=1-8-32`
- `ASSIGN=top_k_soft`
- `TAU=1.000`
- `V_C=1024`, `N_DIM=16384`, `K=1`, `f=0.0060`

`per_unit` rows include:
- `assignment_mode`, `k_value`, `tau`, `effective_coding_level = k/V_C`

## Composable follow-ons (conditional on n4 outcome)

- **HARD_PASS Phase 2:** k in {4, 16, 64} for finer resolution + tau-sweep at
  best-K. Also: n4 + MKN smoothing (orthogonal within-row smoothing axis;
  P=0.45 additional 0.05-0.15 BPC).
- **HARD_PASS Prediction 3:** K=2 depth arm at best-K (verifies n2 floor-masked
  depth-gain surfaces post-floor-drop; free piggyback).
- **HARD_FAIL revival:** route to Research with revival angle "n5 hippocampal-
  episodic + Path A V_C scaling" (USER STANDING route-negatives-to-research rule).

## Dispatch parameters

- **Queue:** remote_cpu_queue (residuals_per_token.npz lives on marsh@home)
- **Timeout:** 14400s (4h floor; PROT-021-compliant since cell imports
  _seed_checkpoint and per-seed-resume tested)
- **Smoke-gate:** local --self-test PASSES (13/13 tests including k=1==argmax,
  weights-sum=1, end-to-end synthetic BPC finite, LLM-call counter=0).
  Local --smoke cannot run (residuals_per_token.npz lives on remote);
  smoke-on-remote happens during runner pickup OR before-full via single-seed
  smoke envelope (covered by --smoke at remote-side small-N + small-MAX_DOCS).

## HONEST SCOPE CAVEAT

n6/n7 substrate-CHAR-LM smoke HARD_FAILed today on a DIFFERENT substrate-LM
mechanism (the char-level pythia substrate path). This cell uses the
EXISTING Pythia-residual-per-token decode pipeline (N2/n3 chain-grade
scaffold; ceiling=2.049, substrate=4.959, bigram=3.844 verified at N2).
The k=1 ANCHOR check IS the smoke-equivalent: K=1 must reproduce N2's
2.049 ceiling within 0.05 bits, else HARD_FAIL.

If the n4 anchor check FAILS at full, that's evidence the residuals_per_token
pipeline is corrupted on remote -- HALT and route to Director (NOT a kWTA-
mechanism failure; an infrastructure failure).

## Compute estimate

Per n3 wall (3 seeds x 3 arms x N_DIM=16384 = 1263s = 21 min total):
- k=1 (hard one-hot): ~140s/seed (same cost as n3 hard VQ)
- k=8: ~250s/seed (8x soft-pool overhead)
- k=32: ~700s/seed (32x soft-pool overhead)
- Total per seed: ~1090s ; 3 seeds: ~3270s ~= 55 minutes
- Generous 4x headroom for IO + k=32 unmeasured: 14400s (4h)

PROT-021 OK: cell imports `experiments._seed_checkpoint` (per-seed-resume).
PROT-018 not applicable (no _n<N> suffix in anchor name).
PROT-019 not applicable (no large-N anchor-name suffix).
PROT-020 not applicable (numpy-only on CPU queue is correct).
