# PRE-REG: exp_math_compositional_derivation_depth_self_margin_v1

**Cell:** `experiments/exp_math_compositional_derivation_depth_self_margin_v1.py`
**Anchor:** `math_compositional_derivation_depth_self_margin_v1`
**Author:** exp_dev  **Date:** 2026-07-06
**Prior-work check (substrate KB):** `bash tools/substrate_query.sh "compositional multi-step arithmetic
derivation chain depth exactness cliff self-margin prediction"` -> top hit `decomposition_reaction` (wordnet)
cosine=0.329; no prior *compositional-arithmetic-depth* or *self-margin-applied-to-arithmetic* cell at
cosine>0.30. Genuinely novel: FIRST cell that CHAINS the landed exact single-op arithmetic primitives
(add `exp_math_rns_add_chain_v1` FULL exact=1.000; subtract/compare `exp_math_rns_subtract_compare_v1`
FULL HARD_PASS; multiply `exp_math_rns_multiply_star_v1` FULL HARD_PASS) into multi-hop derivations and
tests whether the CHAIN_GRADE reasoning-depth self-margin
(`exp_reasoning_depth_exact_order_statistic_self_margin_v1`) predicts the compositional cliff. Respects
prim!=compos (`feedback_chain_grade_primitives_not_trivially_composable_2026-06-28`).

## Claim (two headlines)
**HEADLINE 1 (capability):** composed multi-step arithmetic derivations evaluated end-to-end ON THE
SUBSTRATE (real bind / conj-bind / star_power / decode) stay EXACT vs ground-truth modular arithmetic to
deep D for add/sub (LOSSLESS: phases ADD, float error accumulates linearly -> exact to D>=128); the MULTIPLY
cliff at D~8-16 is a FLOAT32 phase-compounding NUMERICAL accumulation (composed `z**e` multiplies per-dim
phase error by e each hop), NOT decode noise, and is REMOVED by decode-recode (phase reset -> exact to
D>=128). Answers the task's "clean-code accumulation vs decode noise" -> it is clean-code numerics.

**HEADLINE 2 (self-prediction):** feed the noisy-readout per-hop decode SNR (operands read from a B-item
superposition bundle via key-unbind; B = SNR knob, mu=sqrt(2 sb/(B-1))) into the SAME extreme-value capture
order statistic + series-reliability law D*=ln(0.5)/ln(p_hop). HONEST FORK (pre-registered): (a) the law
PREDICTS the cliff -> transfers; or (b) it OVER-predicts the cliff (observed deeper) -> the arithmetic-chain
family DIFFERS from the associative family because modular arithmetic HEALS decode errors. MEASURED: (a) for
the NON-ABSORBING add chain the LAW transfers tightly; (b) for the ABSORBING-ZERO mul chain it over-predicts
the cliff dramatically. The self-margin is a SAFE (never over-promising) depth bound for arithmetic.

## Arms
**CLEAN (HEADLINE 1; fresh isolated operands; per regime x seed):**
- `addsub` [CAPABILITY] alternating bind/conj-bind (no intermediate decode). Expect exact to D_max.
- `mul_starpower` [DISCRIMINATOR] composed star_power (no re-encode) -> NUMERICAL phase-compounding cliff.
- `mul_reencode` [FIX] decode-recode each hop (phase reset) -> exact to D_max.
- `hetero_starpower` / `hetero_reencode` realistic derivation cycle [add,mul,sub,mul], star_power vs reencode.
- `scrambled_op` [CONTROL] substrate applies WRONG op vs ground truth -> exact-through-depth collapses.
- `random_codebook` [CONTROL] hetero on non-phase-linear codebook -> garbage decode -> exact ~0.

**NOISY (HEADLINE 2; operands read from a real B-item key-bound superposition working-memory):**
- `add` family (non-absorbing) and `mul` family (absorbing-zero), decode-recode chains over depth grid, per
  bundle-load op-point B. Predictors of the observed cliff D*: `Dmeasured` (series law fed MEASURED p_hop --
  tests whether the LAW holds), `Dexact` (parameter-free capture order statistic), `Dloose` (occupancy-binary
  union-bound control, biased -> discriminator-fires).

## Regimes / grids
N=8192, R=3, sb=2730 (real substrate; never reduced). Clean: small (7,8,9) M=504 + mid (16,17,19) M=5168.
Noisy: small only. Clean depths FULL {1,2,4,8,12,16,24,32,48,64,96,128}. Noisy depths {1,2,3,4,6,8,12,16,24,
32,48,64}, D_MAX=64, USABLE_FLOOR=0.5. B-grid FULL {180,260,360,500,700,1000}. Seeds FULL {7,13,19,23,29}.

## Pre-registered bands
| Metric | HARD-PASS | HARD-FAIL |
|---|---|---|
| `addsub` exact-through-depth @ D=128 (min over regimes/seeds) | >= 0.99 | < 0.90 (lossless composition broken) |
| `mul_reencode` + `hetero_reencode` exact @ D=128 (min) | >= 0.99 | < 0.90 |
| `mul_starpower` crossing depth (numerical cliff MUST be real+reachable) | in [3, 40] | -- |
| `fix_gap` = reencode_exact - starpower_exact @ D=128 | >= 0.50 | -- |
| controls (`scrambled_op`/`random_codebook`) exact @ D=4 (max) | <= 0.15 | >= 0.40 (vacuous/leak) |
| H2 add-family: series law ratio-error (measured p) at all non-censored B | <= 1.5 (tight) | > 2.0 |
| H2 add-family: law geomean(pred/obs) | in [0.80, 1.25] (unbiased) | -- |
| H2 discriminator: >=2 non-censored add op-points, loose strictly worse, robustness ordering mul>add | required for HARD_PASS | -- |
| H2 discriminating_fraction (Gate B) | >= 0.30 | -- |
| H2 mul-family transfer verdict | REPORTED honest fork (transfers OR over-predicts) | -- |

## SCHEMA-VET fields
- **Compute architecture:** `(b) sequential-CPU with justification`. numpy complex64; the cell IS the
  substrate primitive-composition being validated (bit-exact reference chains); genuine sequential dependency
  (each hop depends on prior running state). No GPU batching applicable to a serial derivation walk. Smoke
  wall MEASURED 114s; FULL est ~8-15 min.
- **Storage strategy:** `clean=no_storage_algebraic; noisy=sharded_key_bound_superposition_bundle`. Clean
  chains compose via algebraic bind/star (single running codeword, no store). Noisy chains use SHARDED
  key-bound superposition (each stored number its own key-bound term) -- the compositional-store default; the
  bundle IS the noisy-readout discriminator (per cross-cell law), and readout is per-item key-unbind not a
  blended gist. Declared per META_RULE_STORAGE.
- **cardinality_ok:** EXPECTED_N_UNITS = n_clean(regimes*seeds*7 arms) + n_noisy(2 ops*|B|*seeds). Gated;
  smoke MEASURED 66/66 (`cardinality_ok:true`).
- **arms_differ_verified:** phase codebook hash != random codebook hash; distinct-op recovered-value arrays
  differ (addsub != mul_starpower; hetero_reencode != scrambled_op). MEASURED True.
  arms_differ_exempted: {mul_reencode, hetero_reencode} may SHARE exact-truth values (both exact) -> NOT
  hash-compared; we hash CODEBOOKS + recovered-value arrays of the DISTINCT-op arms (which differ).
- **final_metrics_atomicity:** `tmp_replace` (metrics.json.tmp -> os.replace). selftest/smoke write to
  distinct `_selftest`/`_smoke` HDLAB_EXP_NAME dirs (no canonical clobber).
- **except ordering:** `except SystemExit: raise` before `except Exception` (grep-gated: no BaseException,
  no bare except). MEASURED clean.
- **crlb / discriminator_reachability:** True. CLEAN operands: per-residue argmax SNR huge (signal sim==1.0,
  distractor sim ~ N(0,1/(2 sb))) -> collision-free (probe MEASURED clean decode==1.000 to sb=2). NOISY
  operands: bundle-load B places per-hop decode error in a discriminating band (MEASURED@probe: add family
  non-censored at B in {360,500,700,1000}, cliffs at D~{24,6,2.6,1.2}). crlb_n_a NOT claimed: the SNR /
  order-statistic argument IS the capacity-feasibility analysis.
- **baseline_in_band (META_RULE_AG):** HEADLINE 1 is an exactness/correctness test (addsub + *_reencode ~1.0
  by lossless construction; scrambled_op/random_codebook are declared CONTROLS ~0.0, exempt). The NON-trivial
  measured content is the mul_starpower NUMERICAL cliff (MEASURED crossing 8.62), its rescue (fix_gap), and
  the HEADLINE-2 op-point sweep which DOES span the discriminating band (Gate B MEASURED 0.50 >= 0.30).
- **discriminator survives scale:** option A -- smoke runs at FULL N=8192, FULL sb=2730, BOTH regimes, full
  B-grid; reduces only seeds / n_chain / max clean depth. mul cliff + reencode rescue + control collapse +
  add-vs-mul robustness ordering all FIRE in smoke.
- **run_mode verification:** metrics assert run_mode==mode; smoke landed run_mode=smoke size 22193B.
- **defensive error-checking:** start_marker + heartbeat + crash-diagnostic + atomic metrics = passed_all_4.
  Non-finite (mul_starpower phase blowup) is DETECTED (decode_int returns -1) and counted as a chain failure
  -- no silent crash, no NaN propagation. `cell_chunked:false` (all-CPU, wall < 15 min, per-unit heartbeat +
  atomic final write; runner death re-runs the cheap cell -- same precedent as landed add/sub/mul cells).
- **progress_logging:** `print_flush_true` (per-unit `_say` flush + `_heartbeat.jsonl`). timeout 2700s (>=1800)
  -> mandatory; satisfied.
- **positive_control (gate D):** single-step add/sub/multiply primitive identities reproduced AT TEST REGIME
  in `composition_selftest` (decode(bind)==(a+b), decode(conj-bind)==(a-b), decode(star_power)==(a*b)) for
  EVERY regime before arms; MEASURED PASS all modes. Cited prior: add exact=1.000
  MEASURED@data/exp_math_rns_add_chain_v1/metrics.json:arms.small.phase_linear_add.exact_mean.
- **functional_requirements (gate E):**
  1. multi-hop numeric derivation -> chain existing exact primitives (bind/conj-bind/star_power).
  2. exact-through-depth measurement -> decode-recode reference + integer ground truth per hop.
  3. depth-cliff localization -> crossing_depth over depth grid (reused from CHAIN_GRADE self-margin cell).
  4. cliff prediction -> capture order statistic + series-reliability D* (reused verbatim from self-margin cell).
  5. noisy per-hop decode SNR -> key-bound superposition bundle readout (real superpose/decode).
- **effective_vs_nominal (gate A):** ALIGNED. Swept axes: clean depth D (each op experiences exactly D);
  noisy bundle-load B -> the predictor consumes exactly the B-derived per-hop SNR (mu=sqrt(2 sb/(B-1))).
- **signal_shape_compatibility (gate C):** all composition edges operate on full-N enc(int) phasors ->
  SHAPE_MATCH. decode-recode edge decode(phasor)->int->encode(int)->phasor = SHAPE_MATCH.
- **discriminating_fraction (gate B):** MEASURED 0.50 (fraction of (op,B) op-points with observed cliff in
  (1.5, D_MAX-0.5)); >= 0.30.

## SMOKE RESULT (MEASURED@data/exp_math_compositional_derivation_depth_self_margin_v1_smoke/metrics.json)
HARD_PASS (wall 114s, size 22193B, run_mode=smoke, cardinality 66/66, arms_differ True).
- HEADLINE 1: addsub_min=1.000, reencode_min=1.000 (exact to D=64 both regimes); mul_starpower NUMERICAL
  cliff crossing=8.62 (d64=0.000); fix_gap=1.000; hetero_starpower cliff ~16.5; controls ctrl_max=0.000.
- HEADLINE 2 add family: LAW_TRANSFERS_TIGHT, law geomean(pred/obs)=1.049, per-B ratio_measured
  [1.119,1.03,1.011,1.062] (series law within ~1.12x of observed); order statistic
  conservative_underpromises_depth; loose control strictly worse (True); n_noncensored=4.
- HEADLINE 2 mul family: DOES_NOT_TRANSFER_OVERPREDICTS_CLIFF (predicted_cliff_but_censored=3, n_noncensored
  =1) -- absorbing-zero robustness heals operand read-errors; chain censored (>64) where series law predicts
  cliff at D~2-14.
- discriminating_fraction=0.50; robustness_ordering mul-more-robust-than-add=True.

## FULL staging
FULL = both regimes, seeds {7,13,19,23,29} (>=5 per task), clean depths to 128, noisy B-grid
{180,260,360,500,700,1000}, n_clean=50, n_noisy=120. Per USER-lock FULL must NOT go to local_cpu_queue
(SMOKE-only on local). Route FULL to `remote_cpu_queue` via `tools/queue_add.py` (SCP-based). Timeout 2700s
(est ~8-15 min; generous for slower remote CPU; < 4h so no prereq justification needed).
