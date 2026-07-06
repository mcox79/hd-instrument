# PRE-REG: exp_rns_subblock_margin_selfcheck_v1

**Cell:** `experiments/exp_rns_subblock_margin_selfcheck_v1.py`
**Anchor:** `rns_subblock_margin_selfcheck_v1`
**Author:** exp_dev  **Date:** 2026-07-06
**Source pre-reg (bands/mechanism):** `notes/research_mechanism_selfverification_scoping_2026-07-06.md`
(Sec. 3 -- the ONE genuine, non-tautological, config-contingent self-check the drill found; the other 3
candidates -- CRT-uniqueness + add/multiply-homomorphism-exactness -- are BLR-theory tautologies, correctly
NOT built).
**Prior-work check (substrate KB):** substrate_query "sub-block dimension decode margin collision-free phasor
codebook modulus Welch bound decode collapse boundary" -> top hits at cosine 0.29-0.33 are ALL the ENCODER
per-cluster-extraction "codebook-collision/cluster-collapse" drill (LC3 basis-pursuit, EMA recovery) + a
wordnet "collision" fact. That is a DIFFERENT mechanism (extraction cluster-collapse defense), NOT the
phase-linear RNS sub-block decode-margin. No prior arithmetic decode-margin cell at cosine>0.30. Cell is
genuinely novel along its target axis (SB-vs-m/sigma decode margin of the arithmetic set), NOT a rediscovery.

## Claim
The substrate CHECKS a config-contingent property of its OWN arithmetic design that the 4 landed math cells
(`exp_math_rns_add_chain_v1`, `_subtract_compare_v1`, `_multiply_star_v1`) ASSERT verbatim but never verified:
"sb=2730 >> max modulus 43, so per-residue argmax is collision-free." This cell is the CHECK half of "the
substrate reasoning about its own design": it derives a closed-form prediction of WHERE per-sub-block decode
collapses as a function of the config parameters (sub-block dim `sb`, modulus `m`, injected noise `sigma`),
MEASURES the actual collapse, and checks its own prediction against the measurement. Monitor-not-control: the
cell only REPORTS the margin; it NEVER changes `sb` or edits a landed cell. USER-locked: narrow glass-box
self-CHECK of its own math config, honest tier (VET decides; prediction-vs-measurement is genuinely empirical).

## HONEST INVERTED PREMISE (MEASURED@probes 2026-07-06, reported prominently, NOT buried)
The drill hypothesized a NOISELESS Welch-bound decode-collapse boundary (SB vs modulus). Pre-dispatch numerical
probes MEASURED that **no such noiseless boundary exists for this codebook**: the phase-linear integer-frequency
codewords `codebook[r]=exp(i*2pi*k_j*r/m)` are the m DISTINCT roots of unity whenever any frequency `k_j` is
coprime to `m`, so per-residue argmax has an EXACT rank-1 similarity of 1.0 and is immune to high off-diagonal
correlation. **Noiseless decode is collision-free by NUMBER THEORY (frequency-modulus coprimality), not Welch/
SNR concentration.** For PRIME moduli every `k_j` in `[1,m)` is coprime -> decode is unconditionally exact at
ANY `sb>=1` (MEASURED@probe: m=19,43 acc=1.000 at sb=1). The Welch/Q-function collapse boundary is operative
ONLY under injected additive noise (a corrupted/bundled/noisy representation) -- which is exactly the RNS-
hardware NOISE-MARGIN regime the drill's own BIST analogy points to (VOH/VOL noise margins: conditionally-
guaranteed, genuinely violable). **This cell therefore verifies the Welch/Q-function prediction in the regime
where it IS the operative law: decode-under-additive-noise** (within exp_dev's granted autonomy over
formula/regime; note Sec. 3 "the discrete-integer-frequency codebook may have a different constant, or worse
tail behavior, than a fully-continuous-random-phasor idealization" -- the probe found the difference is
sharper: the noiseless boundary is number-theoretic, not statistical). The noiseless exactness is retained as a
documented diagnostic arm, an honest inversion analogous to the multiply cell's PRIME_NOT_REQUIRED finding.

## Mechanism (reuses phase-linear phasor FPE + argmax decode VERBATIM from the landed add cell)
Per `(m, sb, sigma)`:
- **Task A (MEASURE):** encode residue `r in [0,m)` as `codebook[r]`, corrupt with complex Gaussian noise
  `~CN(0,sigma^2)` per dim, decode via per-sub-block phasor argmax; accuracy = frac(argmax==r), seed-averaged.
- **Task B (PREDICT, closed form -- the substrate's OWN self-check):** `P_e <= (m-1)*Q(sqrt(sb)/sigma)`
  (THEORETICAL@Proakis M-ary matched-filter union bound; margin `sim[true]~1.0 - sim[comp]~0` has noise std
  `~sigma/sqrt(sb)` -> `Q(sqrt(sb)/sigma)`). Predicts collapse `SB* ~ sigma^2`.
- **Task C (CHECK):** does the predicted collapse boundary `SB*(sigma)` match the measured one? Primary
  invariant = the SCALING EXPONENT `p` of `SB* ~ sigma^p` (THEORETICAL `p=2`). The substrate's own formula
  reproduces `p`; a mis-derived wrong-scaling (SNR linear in sb) predicts `p~1` and is falsified.

## Arms (measurements PAIRED on identical residues + noise draws where compared)
- `measured_decode` [MECHANISM] -- phase-linear codebook decode acc under noise (seed-averaged).
- `predict_correct` [PREDICTION] -- the substrate's own closed-form `1-(m-1)Q(sqrt(sb)/sigma)`.
- `predict_wrong_scaling` [CONTROL 1] -- mis-derived, SNR LINEAR in sb (`sb/sigma`) -> predicts `SB* ~ sigma^1`.
  Isolates that the `sqrt(sb)` CLT-concentration scaling is load-bearing, not any monotonic-in-sb guess.
- `collapsed_codebook` [CONTROL 2, must-collapse] -- rank-1 codebook (all m residues share ONE bit-identical
  codeword) -> genuinely indistinguishable -> acc `~1/m` at EVERY sb incl the safe end. Isolates that
  distinguishable codeword STRUCTURE (not merely many dims) is what the formula models. (Note: a RANDOM-phasor
  codebook does NOT collapse -- random unit phasors are also near-orthogonal -- so the must-collapse control
  must be rank-degenerate, MEASURED@probe.)
- `noiseless_diag` [DIAGNOSTIC] -- sigma=0 decode acc vs sb (the number-theoretic exactness; prime m exact at
  any sb>=1). Reported, documents the inverted premise. Not pass-gated.

## Regimes (sweep axes)
- Moduli `m in {9, 19, 43}` -- the LARGEST modulus of the small/mid/large arithmetic regimes the landed math
  cells ship (small=(7,8,9) mid=(16,17,19) large=(40,41,43)); the sub-block margin is set by the largest
  modulus (most competing residues).
- Sub-block dim `sb in {4,8,16,32,64,128,256,512,1024,2730}` -- collapsed up to the SHIPPED substrate config
  sb=2730 (=N_DIM 8192 // R_MODULI 3). sb=2730 is the retrospective REAL-DATA ANCHOR.
- Injected noise `sigma in {6,8,11,16}` -- chosen (probe) so `SB*(sigma)` sweeps ACROSS the sb grid for every
  modulus, making the sigma^2 scaling law measurable.
- Seeds (7,13,19,23,29) FULL; (7,13,19) smoke. Trials 800 FULL; 250 smoke.

## Pre-registered bands (deflated per role discipline; P_deflated=0.40 from source note)
| Metric | HARD-PASS | HARD-FAIL | MIDDLE |
|---|---|---|---|
| reachability (each m,sigma) | acc brackets 0.5 in-grid AND dips <= 0.30 | any (m,sigma) not reachable | -- |
| measured scaling exponent `p_meas` (per m) | in [1.6, 2.4] (THEORY 2.0) | outside [1.2, 2.8] | in [1.6,2.4] w/ offset large |
| correct formula reproduces: `\|p_meas - p_correct\|` (per m) | <= 0.4 | -- | -- |
| wrong-scaling separated: `\|p_meas - p_wrong\|` (per m) | >= 0.6 | -- | -- |
| exponent-error advantage `\|p_meas-p_wrong\| / \|p_meas-p_correct\|` (min) | >= 2.0 | < 1.2 (sqrt-law not load-bearing) | in [1.2,2.0) |
| correct-formula SB* geom-mean ratio-error (per m) | <= 4x | > 8x | in (4x,8x] |
| collapsed control acc (per m, max over grid) | <= 3/m | > 0.40 (leak) | -- |

HARD-PASS requires ALL of: reachability + p_meas-in-band + correct-reproduces + wrong-separated + advantage +
bounded-offset + collapsed-collapses, at EVERY modulus. `SB_SHIPPED=2730` must sit predicted-safe at every
sigma (retrospective validation of the 4 landed cells' boilerplate) -- reported.

## SCHEMA-VET fields
- **Compute architecture:** `(b) sequential-CPU with justification`. numpy complex64; trials VECTORIZED
  (matmul `(m x sb)@(sb x T)` + argmax). Smoke MEASURED 4.4s; full est ~25s. Carve-outs: cell IS the
  substrate-primitive being validated (bit-exact reference) AND total wall << the 10s-per-phase-point batching
  threshold. No GPU speedup relevant. No batching required.
- **Storage strategy:** `no_storage_algebraic_decode`. Single-codeword decode (a bind result IS an exact
  codeword); no items stored/superposed -> sharded/bundled rule N/A.
- **cardinality_ok:** EXPECTED_N_UNITS = n_moduli * n_sigma * n_sb = 3*4*10 = 120. Gated; smoke MEASURED
  120/120.
- **arms_differ_verified:** phase codebook hash != collapsed(rank-1) codebook hash; correct-prediction surface
  hash != wrong-scaling surface hash; measured surface hash != collapsed-control surface hash. MEASURED True.
- **final_metrics_atomicity:** `tmp_replace` (metrics.json.tmp -> os.replace).
- **except ordering:** `except SystemExit: raise` before `except Exception` (no BaseException, no bare except).
  Grep gate MEASURED clean.
- **crlb / discriminator_reachability:** True. This cell IS the capacity-feasibility instrument. The
  decode-collapse boundary under additive noise IS the M-ary matched-filter bound `P_e<=(m-1)Q(sqrt(sb)/sigma)`.
  Probe MEASURED the 0.5-crossing SB* bracketed inside the swept grid for every (m,sigma). No unreachable
  threshold.
- **baseline_in_band (META_RULE_AG):** this is a REACHABILITY/PREDICTION-MATCH test, not a difficulty
  baseline. The measured acc surface intentionally spans ~0.05-0.20 (collapsed) up to 1.0 (safe); the
  collapsed-codebook arm is a declared must-collapse CONTROL (~1/m) exempt from the in-band rule. Discriminator
  = measured-collapse-boundary vs predicted-collapse-boundary (scaling exponent + bounded offset), which does
  NOT saturate at scale.
- **discriminator survives scale:** option A -- smoke runs the FULL sb grid (up to sb=2730 shipped), ALL 3
  moduli, ALL 4 noise levels; smoke reduces trials/seeds ONLY. collapse-reachable + scaling-exponent-match +
  wrong-scaling-separation + collapsed-control-collapse all FIRE in smoke (MEASURED).
- **run_mode verification:** metrics assert run_mode==mode; smoke landed run_mode=smoke, 28714B, HARD_PASS.
- **defensive error-checking:** start_marker + heartbeat + crash-diagnostic + atomic metrics = passed_all_4.
- **progress_logging:** `line_buffered_stdout` (sys.stdout.reconfigure line_buffering + per-unit flush). N/A as
  mandatory (wall << 1800s) but present.
- **positive_control (gate D):** the phase-linear FPE decode primitive is reproduced AT TEST REGIME by the
  noiseless diagnostic (decode exact at the shipped sb=2730 and, for prime moduli, at any sb>=1) + the
  `formula_selftest` (Q-function monotone; correct-formula exponent ~2, wrong-formula exponent ~1;
  shipped-sb-safe). Both MEASURED PASS all modes.
- **functional_requirements (gate E):**
  1. predict decode-collapse boundary from config params -> closed-form `(m-1)Q(sqrt(sb)/sigma)` (this cell's
     new increment; reuses landed phasor codebook + argmax).
  2. measure actual decode margin -> phase-linear FPE decode under injected noise (landed decode primitive).
  3. check own prediction vs measurement -> scaling-exponent match + bounded offset + wrong-scaling falsified.
  4. isolate load-bearing ingredient -> wrong-scaling control (sqrt vs linear) + collapsed control (structure
     vs dimensions).
- **effective_vs_nominal (gate A):** ALIGNED. Swept axes = (sb, m, sigma); each is experienced directly by the
  single-sub-block decode (no partition routing dilutes any axis).
- **discriminating_fraction (gate B):** the collapse boundary is REACHABLE at every (m,sigma) -- MEASURED@smoke
  reach_fail=[] (12/12 (m,sigma) bracket 0.5 and dip <= 0.30). >= 30% of grid points land in the discriminating
  band by construction (the sweep straddles the transition).

## SMOKE RESULT (MEASURED@data/exp_rns_subblock_margin_selfcheck_v1_smoke/metrics.json)
HARD_PASS (wall 4.4s, 28714B, run_mode=smoke, cardinality 120/120, arms_differ True, reach_fail []).
Per modulus: p_meas=[1.83(m9), 2.08(m19), 1.89(m43)] (all in [1.6,2.4], THEORY 2.0); p_correct=[1.99,1.97,2.17]
(reproduces ~2.0, exp_err<=0.28<=0.4); p_wrong=[0.93,0.97,1.21] (~1.0, exp_err>=0.68>=0.6, min advantage
2.41x>=2.0); correct-formula SB* offset bounded (gm_ratio_err<=2.80x<=4.0, the loose-union-bound systematic
over-prediction); collapsed control collapses (max 0.137<=3/9, per-m <=3/m). Shipped sb=2730 predicted+measured
safe at every sigma (acc>=0.988 at sigma=16). Noiseless diag: all moduli exact (1.000) at sb>=4; prime m
exact at sb=1 (probe). Interpretation: the substrate's closed-form decode-collapse-boundary prediction MATCHES
the measured collapse (scaling law reproduced, wrong-scaling falsified), retrospectively VALIDATING the 4
landed math cells' "sb=2730 >> max modulus" boilerplate as a huge (~3.6x) noise margin.

## FULL staging
FULL = same 3 moduli, sb grid, 4 sigmas, seeds (7,13,19,23,29), trials=800. CPU-scale (numpy, est ~25s), ZERO
referent (self-contained synthetic codebooks; no cert_ledger / pool / re-encode dependency -> NON-PARKED, clean
remote gate; deploy-independent). Per USER-lock FULL must NOT go to local_cpu_queue (SMOKE-only on local);
canonical run = remote landing. Route FULL to `remote_cpu_queue` via Orchestrator (push to origin/main
required; harness-denied to exp_dev). Timeout: 600s (generous; expected ~25s).
