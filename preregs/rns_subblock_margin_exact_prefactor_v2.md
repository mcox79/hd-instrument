# PRE-REG: exp_rns_subblock_margin_exact_prefactor_v2

**Cell:** `experiments/exp_rns_subblock_margin_exact_prefactor_v2.py`
**Anchor:** `rns_subblock_margin_exact_prefactor_v2`
**Author:** exp_dev  **Date:** 2026-07-06
**Extends:** `exp_rns_subblock_margin_selfcheck_v1` (landed HARD_PASS, MM tier -- v1 cell + v1 metrics untouched)
**Source derivation (bands/mechanism):** `notes/research_decode_margin_exact_prefactor_derivation_2026-07-06.md`
(Sec. 2 numeric verification against v1's landed 120-pt surface; Sec. 4 cell spec).

**Prior-work check (substrate KB):** `substrate_query "exact prefactor decode collapse boundary order
statistic M-ary orthogonal signaling margin self-check"` -> top hit cosine 0.25 (`state_boundary`, wordnet),
NONE at cosine>0.30. This v2 is a deliberate, cited DIRECT EXTENSION of the landed v1 (the base cell the
derivation note improves on), not a rediscovery of an unrelated arc. Genuinely novel along its target axis
(exact order-statistic prefactor for the arithmetic-set decode margin).

## Claim (MM -> CG promotion)
v1 validated that the substrate's closed-form decode-collapse-boundary prediction MATCHES the measured collapse
in SCALING (`SB* ~ sigma^2`), but its LOOSE union-bound prefactor over-predicts the boundary `SB*` by a MEASURED
`gm_ratio_err` of 2.39-2.73x (MEASURED@data/exp_rns_subblock_margin_selfcheck_v1/metrics.json:per_modulus:
m=9 2.727x / m=19 2.388x / m=43 2.544x). This v2 adds the EXACT prefactor: the substrate predicts `SB*` via the
exact M-ary orthogonal-signaling order statistic (route (b), NOT chord-distance (a), NOT RMT (c)):
`P_correct = E_z[ Phi(mu + z)^(m-1) ]`, `z ~ N(0,1)`, `mu = sqrt(2*sb)/sigma`. This makes the substrate predict
its OWN decode-collapse boundary EXACTLY (not just the scaling). Monitor-not-control (USER-locked): the cell only
REPORTS the tighter margin number; it NEVER changes `sb`, edits a landed cell, or triggers a rebuild. NOT
self-improvement. Honest tier -- CG-candidate (exact self-prediction); VET decides.

## Mechanism (measurement machinery reused VERBATIM from v1 -> reproduces v1's surface deterministically)
Per `(m, sb, sigma)`:
- **Task A (MEASURE, VERBATIM v1):** encode residue `r in [0,m)` as `codebook[r]`, corrupt with complex Gaussian
  noise `~CN(0,sigma^2)` per dim, decode via per-sub-block phasor argmax; acc = frac(argmax==r), seed-averaged.
  Identical `phasor_codebook` / `collapsed_codebook` / `decode_acc` / RNG seeding as v1 -> the FULL measured
  surface is bit-identical to v1's landed surface (identical seeds (7,13,19,23,29), trials=800).
- **Task B (PREDICT, NEW -- exact):** `P_correct = E_z[ Phi(mu+z)^(m-1) ]`, `mu=sqrt(2*sb)/sigma`, via 64-point
  Gauss-Hermite quadrature (numpy `polynomial.hermite.hermgauss` + stdlib `math.erfc` -- NO scipy). Exact given
  the `m-1` competitor decision statistics are mutually independent (a structural fact of this
  random-per-dim-frequency codebook; verified to ~1% via the union-vs-exact residual check in the source note).
- **Task B' (CONTROL/BASELINE):** v1's `pred_acc_union = 1-(m-1)Q(sqrt(sb)/sigma)` -- KEPT live, must stay
  loose (~2.5x). The first-order Boole truncation of the exact order statistic.
- **Task C (CHECK):** does the EXACT prediction tighten `SB*` to `<= 1.5x` (the CG bar) while the union bound
  stays `~2.5x`, showing the exact formula is the load-bearing improvement?

## Arms (measurements PAIRED on identical residues + noise draws where compared)
- `measured_decode` [MECHANISM] -- phase-linear codebook decode acc under noise (VERBATIM v1).
- `predict_exact` [PREDICTION, the new discriminator] -- the EXACT order statistic `E_z[Phi(mu+z)^(m-1)]`.
- `predict_union` [CONTROL / BASELINE] -- v1's loose union bound `1-(m-1)Q(sqrt(sb)/sigma)`. Must stay ~2.5x.
- `predict_wrong_scaling` [CONTROL 1, unchanged] -- SNR LINEAR in sb (`sb/sigma`) -> `SB* ~ sigma^1`. Falsified.
- `collapsed_codebook` [CONTROL 2, must-collapse, unchanged] -- rank-1 codebook -> acc `~1/m` at EVERY sb.
- `noiseless_diag` [DIAGNOSTIC, unchanged] -- sigma=0 acc vs sb (number-theoretic exactness). Not pass-gated.

## Regimes (sweep axes -- IDENTICAL to v1)
- Moduli `m in {9, 19, 43}` (largest modulus of small/mid/large arithmetic regimes).
- Sub-block dim `sb in {4,8,16,32,64,128,256,512,1024,2730}` (collapsed up to shipped `sb=2730`).
- Injected noise `sigma in {6,8,11,16}`.
- Seeds (7,13,19,23,29) FULL; (7,13,19) smoke. Trials 800 FULL; 250 smoke.

## Pre-registered bands
**NEW exact-prefactor discriminator (the CG-promotion bar):**
| Metric | HARD-PASS | HARD-FAIL | MIDDLE |
|---|---|---|---|
| exact-arm SB* geom-mean ratio-error `gm_exact` (per m) | `<= 1.5x` at ALL 3 moduli | `> 4x` at any modulus | in `(1.5x, 4x]` |
| relative improvement `gm_union / gm_exact` (per m) | `>= 1.5x` at ALL 3 moduli | `< 1.5x` at any modulus | -- |

**RETAINED from v1 (already HARD_PASSED; not expected to move -- v2 only adds a prefactor arm):**
| Metric | HARD-PASS | HARD-FAIL |
|---|---|---|
| reachability (each m,sigma) | acc brackets 0.5 in-grid AND dips `<= 0.30` | any (m,sigma) not reachable |
| measured scaling exponent `p_meas` (per m) | in `[1.6, 2.4]` (THEORY 2.0) | outside `[1.2, 2.8]` |
| union reproduces: `\|p_meas - p_union\|` (per m) | `<= 0.4` | -- |
| wrong-scaling separated: `\|p_meas - p_wrong\|` (per m) | `>= 0.6` | -- |
| exponent-error advantage `\|p_meas-p_wrong\| / \|p_meas-p_union\|` (min) | `>= 2.0` | `< 1.2` |
| UNION-arm SB* geom-mean ratio-error (per m) | `<= 4x` (baseline stays loose) | -- |
| collapsed control acc (per m, max over grid) | `<= 3/m` | `> 0.40` (leak) |

**HARD-PASS requires ALL of:** exact `<= 1.5x` at all 3 moduli AND rel-improve `>= 1.5x` at all 3 moduli AND all
v1 gates (reachability + p_meas-in-band + union-reproduces + wrong-separated + advantage + union-offset-bounded
+ collapsed-collapses). `SB_SHIPPED=2730` sits predicted-safe at every sigma (retrospective validation),
reported.

**Smoke discriminator-fires gate (loose vs the FULL 1.5x canonical bar, to tolerate reduced-trial SB* noise):**
`gm_exact < 2.0` AND `rel_improve > 1.3` at every modulus. Canonical `<= 1.5x` bar is FULL-only.

## PRE-DISPATCH VERIFICATION (done -- assert measured == expected BEFORE dispatch)
**(1) Cheap decisive test against v1's LANDED full-seed 120-pt surface (zero new trials):** the exact formula
recomputed on `data/exp_rns_subblock_margin_selfcheck_v1/metrics.json:per_unit` gives
`gm_exact = 1.109(m9) / 1.049(m19) / 1.015(m43)` -- ALL `<= 1.5x`; `gm_union = 2.727 / 2.388 / 2.544`;
pointwise vs measured (120 pts) union RMS 0.264 / max 0.687, exact RMS 0.012 / max 0.047. Reproduces the source
note (Sec. 2) EXACTLY. Because v2 reuses the measurement VERBATIM with identical seeds, the v2 FULL measured
surface == v1's landed surface, so the v2 FULL exact-arm result is DETERMINISTICALLY 1.109/1.049/1.015 (all
`<1.5x` -> FULL HARD_PASS predicted with certainty).
**(2) Fresh smoke (3 seeds, 250 trials, full sb grid):** HARD_PASS, gm_exact `=1.14/1.05/1.07x` (all `<1.5x`
even at smoke scale), gm_union `2.80/2.39/2.68x`, rel_improve `2.46/2.27/2.50x`, p_meas `[1.83,2.08,1.89]`,
p_exact `[2.01,1.99,2.01]`, collapsed control collapses (max 0.137), reach_fail []. (MEASURED@data/
exp_rns_subblock_margin_exact_prefactor_v2/metrics.json, run_mode=smoke, 33226B, cardinality 120/120,
arms_differ True with 5 distinct surfaces.)
**(3) Gauss-Hermite node convergence** at the hardest corner (m=43, sb=4, sigma=16): n=48 0.03383828, n=64
0.03383767, n=96 0.03383760 -> n=64 converged to 6 decimals. No integration-window edge case at smallest sb.

## SCHEMA-VET fields
- **Compute architecture:** `(b) sequential-CPU with justification`. numpy complex64; trials VECTORIZED (matmul
  `(m x sb)@(sb x T)` + argmax); exact prediction = 64-pt Gauss-Hermite (numpy, no scipy). Smoke MEASURED 5.8s;
  full est ~25s. Carve-outs: cell IS the substrate-primitive being validated (bit-exact reference) AND total
  wall << the 10s-per-phase-point batching threshold. No GPU speedup relevant. No batching required.
- **Storage strategy:** `no_storage_algebraic_decode`. Single-codeword decode; no items stored/superposed.
- **cardinality_ok:** EXPECTED_N_UNITS = n_moduli * n_sigma * n_sb = 3*4*10 = 120. Gated; smoke MEASURED 120/120.
- **arms_differ_verified:** phase codebook hash != collapsed(rank-1); exact-prediction surface != union-
  prediction surface != wrong-scaling surface; measured surface != collapsed-control surface. MEASURED True
  (5 distinct surface hashes).
- **final_metrics_atomicity:** `tmp_replace` (metrics.json.tmp -> os.replace). MEASURED no leftover .tmp.
- **except ordering:** `except SystemExit: raise` before `except Exception` (no BaseException, no bare except).
  Grep gate MEASURED clean.
- **crlb / discriminator_reachability:** True. This cell IS the capacity-feasibility instrument. The exact
  order-statistic prefactor's tightness (`<=1.5x`) is a REACHABLE threshold: verified 1.01-1.11x on v1's landed
  full surface pre-dispatch. The 0.5-crossing SB* is bracketed inside the swept grid for every (m,sigma)
  (MEASURED@v1 + reproduced fresh in smoke).
- **baseline_in_band (META_RULE_AG):** PREDICTION-MATCH test, not a difficulty baseline. Measured surface spans
  ~0.05-0.20 (collapsed) up to 1.0 (safe); collapsed arm is a declared must-collapse CONTROL (~1/m) exempt.
  Union-bound arm is a live loose CONTROL (~2.5x); exact arm is the new MECHANISM. Discriminator (exact-boundary
  vs union-boundary tightness) does NOT saturate at scale (both are deterministic closed forms).
- **discriminator survives scale:** option A -- smoke runs the FULL sb grid (up to sb=2730 shipped), ALL 3
  moduli, ALL 4 noise levels; smoke reduces trials/seeds ONLY. The predictions are DETERMINISTIC closed forms
  (identical at smoke and full); only the measured SB* estimate refines with more seeds/trials (smoke gm_exact
  1.14/1.05/1.07 -> full 1.109/1.049/1.015). exact-arm tightening + collapse-reachable + scaling-exponent-match
  + wrong-scaling-separation + collapsed-collapse all FIRE in smoke (MEASURED).
- **run_mode verification:** metrics assert run_mode==mode; smoke landed run_mode=smoke, 33226B, HARD_PASS.
- **defensive error-checking:** start_marker + heartbeat + crash-diagnostic + atomic metrics = passed_all_4.
- **progress_logging:** `line_buffered_stdout` (sys.stdout.reconfigure line_buffering + per-unit flush). N/A as
  mandatory (wall << 1800s) but present.
- **positive_control (gate D):** the union-bound arm reproduces v1's `gm_ratio_err_correct` AT THE TEST REGIME
  (cited prior atom v1 metrics: 2.727/2.388/2.544; v2 union arm reproduces to within measurement noise --
  smoke measured 2.80/2.39/2.68, full deterministically 2.727/2.388/2.544 since same seeds). The phase-linear
  FPE decode primitive is reproduced by the noiseless diagnostic (exact at shipped sb=2730; prime moduli exact
  at any sb) + `formula_selftest` (Q + Phi monotone; union/exact exponent ~2, wrong ~1; shipped-safe; exact
  order-stat normalization at mu=0 == 1/m; exact >= union pointwise). All MEASURED PASS all modes.
- **functional_requirements (gate E):**
  1. predict decode-collapse boundary EXACTLY from config params -> exact order statistic
     `E_z[Phi(mu+z)^(m-1)]` (this cell's new increment; reuses landed phasor codebook + argmax).
  2. measure actual decode margin -> phase-linear FPE decode under injected noise (VERBATIM v1).
  3. check own EXACT prediction vs measurement -> gm_exact `<=1.5x` (CG bar) + relative-improvement vs union.
  4. isolate load-bearing ingredient -> union-bound control (independence-exact vs loose Boole-truncation) +
     wrong-scaling control (sqrt vs linear) + collapsed control (structure vs dimensions).
- **effective_vs_nominal (gate A):** ALIGNED. Swept axes = (sb, m, sigma); each experienced directly by the
  single-sub-block decode (no partition routing dilutes any axis).
- **discriminating_fraction (gate B):** the collapse boundary is REACHABLE at every (m,sigma) -- MEASURED@smoke
  reach_fail=[] (12/12 (m,sigma) bracket 0.5 and dip <= 0.30). The exact vs union gap is discriminating at
  every modulus (rel_improve 2.27-2.50x >> 1).

## FULL staging
FULL = same 3 moduli, sb grid, 4 sigmas, seeds (7,13,19,23,29), trials=800. CPU-scale (numpy, est ~25s), ZERO
referent (self-contained synthetic codebooks; no cert_ledger / pool / re-encode dependency -> NON-PARKED, clean
remote gate). Per USER-lock FULL must NOT go to `local_cpu_queue` (SMOKE-only on local); canonical run = remote
landing. Route FULL to `remote_cpu_queue` via Orchestrator (push to origin/main required; harness-denied to
exp_dev). Timeout: 600s (generous; expected ~25s). Predicted landing: HARD_PASS, gm_exact 1.109/1.049/1.015x
(all `<1.5x`), gm_union 2.727/2.388/2.544x, rel_improve 2.46/2.28/2.51x (deterministic -- same seeds as v1).
