# Pre-registration: Dense/modern-Hopfield readout capacity vs pairwise, IID vs CORRELATED codes

Anchor: `dense_hopfield_readout_capacity_correlated_codes_v1`
Cell: `experiments/exp_dense_hopfield_readout_capacity_correlated_codes_v1.py`
Date: 2026-07-13
Author: exp_dev (Prover)
Queue target: `remote_cpu_queue` (CPU-appropriate; numpy; no GPU required)

## Question (PRIMARY)
Does a dense/modern-Hopfield readout -- a super-quadratic similarity/energy
separation in the cleanup/reconstruction step (higher-order polynomial
F(x)=relu(x)^n for n in {2,4,8}, plus an exp-family F(x)=exp(beta*x)) -- raise
RECOVERABLE-SIGNAL CAPACITY over the standard PAIRWISE readout (n=2), and
CRUCIALLY does that lift SURVIVE the substrate's ACTUAL correlated, structureless
relational code distribution, NOT merely idealized iid patterns?

This is the #1 lever from the 2026-07-13 5x drill (converged across the neuro
lens `notes/research_drillA_neuro_capacity_structure_2026-07-13.md` Test 1 and
the quantum lens `notes/research_drillA_quantum_capacity_structure_2026-07-13.md`
HP1/HP2/HF2). The premise: relational codes are arbitrary structureless labels
(nothing to compress -- proven dead across 5 fields); instead of fixing the
CODES, change the READOUT to a dense-associative-memory energy function that
sidesteps the "nothing to compress" wall. Codes + ingest UNCHANGED.

## Mechanism (glass-box, closed-form, no learned aggregator)
One-step dense-associative update (Krotov-Hopfield 2016 F(x)=x^n; Demircigil 2017
/ Ramsauer 2020 F(x)=exp). Stored patterns P (the codes, UNCHANGED), partial-cue
query q, similarities s_mu=<q,p_mu>, reconstruction
p_hat = sum_mu F(s_mu) p_mu / sum_mu F(s_mu). SUCCESS = faithful recovery:
cosine(p_hat, p_target) >= RECON_TAU AND target is the nearest codebook neighbour.
F does NOT change argmax(s) (both x^n and exp monotone), so a pure 1-NN readout is
n-invariant; F's ONLY lever is SHARPENING the superposition weights so spurious
patterns contribute less crosstalk to p_hat. Higher n / exp => sharper => cleaner
reconstruction => higher recoverable capacity. Structure-agnostic: no label is
compressed; only the readout nonlinearity varies.

## Distributions (the discriminating axis)
- `iid` (d_sub=None): near-orthogonal Gaussian codes = classical Hopfield/Krotov
  regime; the super-quad lift is textbook here. POSITIVE CONTROL.
- `corr_mild` (d_sub=64, off-diag |cos|~0.125), `corr_mod` (d_sub=24, ~0.204),
  `corr_strong` (d_sub=12, ~0.289): subspace-confined correlated codes =
  substrate's actual-style regime. Correlation inflates crosstalk AND pulls the
  reconstruction toward correlated neighbours (quantum-drill HF2 wall). The
  headline is the CORRELATED lift, reported across the mild->strong gradient.
- Correlation model = subspace-confinement, the same parametric stand-in used by
  the prior correlated-keys dense-Hopfield cell
  (`_substrate_cortex_hippo_dense_beta_sweep_v2_correlated_keys_core.py`; "the M3
  real-world regime"). SCOPING: this is a parametric correlation stand-in matched
  to a realistic off-diagonal cosine, NOT the literal store codes (glass-box,
  reproducible; no store build needed -- the whole lever is a readout change).

## Capacity metric (censoring-robust)
Per (dist, N, order): recall-vs-load curve over ALPHA_LADDER, crossing load
alpha* = M*/N at which recall crosses RECALL_THRESH=0.90 (linear interp). floored
at ALPHA_MIN=0.1 if it fails at the smallest load; censored at ALPHA_MAX (last
tested alpha) if it never fails -> a CONSERVATIVE lower bound on capacity.
lift(dist,N) = best-super-order alpha* / pairwise alpha*.
NOTE (censoring caveat): super-quad capacity is enormous (~N^(n-1) / exp), so on
iid + mild-corr it typically CENSORS at ALPHA_MAX -> reported lift is a
conservative LOWER BOUND, understating (never overstating) the true advantage.

## Config
- Orders: poly2 (BASELINE, pairwise), poly4, poly8, exp(beta=25).
- COS_TARGET=0.25 (partial cue); RECON_TAU=0.80; RECALL_THRESH=0.90.
- ALPHA_LADDER=[0.1,0.2,0.35,0.5,0.75,1.0,1.5,2.0,3.0,4.0], M_CAP=6144.
- N_LADDER (FULL)=[256,512,1024,2048]; SEEDS=[7,13,19].
- Storage strategy: SHARDED (each pattern its own vector; the whole point is an
  associative store of individual codes; no bundling).

## Bands (envelope-fail-bands; PASS + FAIL pre-declared)
Headline = `corr_lift` = geometric mean over correlated dists of per-dist geomean
lift across N (clean-baseline cells only; base-floored cells excluded to avoid
spurious rescue-inflation).

- HARD_PASS `CAPACITY_LIFT_REAL`: `corr_lift >= 1.50x` AND iid pos-control passes
  AND scramble collapses. (Strictly above the no-lift floor of 1.0x by 0.50; the
  neuro-drill HARD-PASS bar was >=1.5x, quantum-drill HP1 >=2x -- 1.5x is the
  more conservative of the two.)
- HARD_FAIL `NO_LIFT_ON_CORRELATED_CODES`: `corr_lift < 1.15x` while
  `iid_lift >= 1.50x` -- lifts on idealized iid but the correlation-hurts confound
  washes it on real correlated codes (quantum-drill HF2:
  `reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval`).
- MIDDLE_BAND `PARTIAL_LIFT_ON_CORRELATED`: `corr_lift` in [1.15, 1.50).
- FAIL-CLOSED `POSITIVE_CONTROL_BROKEN` (HARD_FAIL): `iid_lift < 1.50x` -- the
  readout is broken or the regime saturates; correlated result uninterpretable.
- FAIL-CLOSED `MUST_FAIL_CONTROL_DID_NOT_COLLAPSE` (HARD_FAIL): scramble readout
  (row-permuted weights: destroys similarity ranking, preserves weight-magnitude
  multiset) does not collapse to <=0.60 while intact >=0.70.

Per-dist corr lift + strongest-corr lift are also reported so the survival
GRADIENT is visible regardless of which headline bin fires.

## Predicted values (band-feasibility; MEASURED at SMOKE where noted)
- iid_lift (pos control): 12.20x  MEASURED@data/exp_dense_hopfield_readout_capacity_correlated_codes_v1_smoke/metrics.json:headline.iid_lift_geo (N in {256,512})
- corr_lift (headline):    8.87x  MEASURED@..._smoke/metrics.json:headline.corr_lift_geo
- per-dist corr lift: mild 16.71x / mod 9.71x / strong 4.31x  MEASURED@..._smoke/metrics.json:headline.corr_lift_per_dist
- scramble worst recall:  ~0.01   MEASURED@..._smoke/metrics.json:headline.worst_scramble_recall
- poly2 IID capacity ~ 0.14*N  CITED@Amit-Gutfreund-Sompolinsky 1985
- super-quad F(x)=x^n capacity ~ N^(n-1)  CITED@Krotov-Hopfield 2016
- exp-family exponential capacity  CITED@Demircigil 2017 / Ramsauer 2020
- MONO_MATCHED deployable oracle MRR = 0.4660  MEASURED@data/exp_map_builder_residue_module_ceiling_v1/metrics.json:gates.oracle_2x2_mrr.MONO_MATCHED
  (RNS-arena deployable reference; this cell does NOT reproduce it -- separate harness)

Discriminating-fraction (Gate B): at N=512 the poly2 baseline recall spans the
full range and crosses [0.30,0.70] for iid/corr_mild/corr_mod/corr_strong (e.g.
iid poly2 N512 curve = [1.0,1.0,1.0,0.94,0.48,0.06,0,0,0,0] MEASURED@..._smoke) ->
>=30% of ladder points in the discriminating band. `discriminating_fraction`
satisfied.

## Compute architecture
Class: (b) sequential-CPU. Justification: numpy matmuls (Q@P.T similarity, W@P
reconstruction) with BLAS multithreading; no GPU needed (per-readout GEMMs on
M<=6144, N<=2048 are CPU-cheap). Independent (dist,N,order,seed,alpha) points are
looped sequentially; total smoke wall = 84.9s at N in {256,512} x 3 seeds
MEASURED@..._smoke. Storage: SHARDED (individual code vectors). This is CPU-safe
per the "no local smokes / route execution remote" discipline -> `remote_cpu_queue`.

## SCHEMA-VET fields
- cardinality_ok: true (EXPECTED_N_UNITS = |N|=4 x |dist|=4 x |order|=4 x |seed|=3
  = 192 FULL; verdict emits HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if len != expected)
- baseline_in_band: true (poly2 crosses RECALL_THRESH in-band for all dists at
  smoke; not saturated >0.95 everywhere, not floored <0.05 everywhere)
- arms_differ_verified: true (self-test hash-tests poly2/4/8/exp separation
  weights bit-distinct; META_RULE_AF)
- arms_differ_exempted: [] (none)
- final_metrics_atomicity: tmp_replace (os.replace at end)
- calibration_check: default_ok_for_this_regime (closed-form readout; no tuned
  primitive defaults; correlation strength swept mild->strong)
- crlb_n/a: "capacity crossing is a MEASURED relative-lift band, not an absolute
  noise-floor threshold; the pairwise M* baseline is measured (not assumed) and
  the HP bar is a >=1.5x RATIO, always achievable-side of the 1.0x no-lift floor."
- discriminator_reachability: true (HP=1.5x ratio; smoke measured 8.87x)
- cell_chunked: false. Justification: fast pure-numpy CPU sweep (smoke 85s; FULL
  est ~30-60min); no GPU/OOM/zombie risk; single-file for remote_cpu portability;
  per-progress heartbeat + start-marker + crash-diagnostic present so silent death
  is observable; no cross-seed shared mutable state (each unit is independent).
- start_marker_written: true (_start_marker.json at run_sweep entry)
- crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics.json + traceback)
- heartbeat_present: true (_heartbeat.jsonl every 5 units)
- defensive_error_checking: "start_marker + crash_diagnostic + heartbeat present;
  cell_chunked exempted per justification above (single-file CPU sweep, independent units)"
- progress_logging: print_flush_true (line_buffering + flush=True on progress lines)

## §15 test-design gates
- sweep_alignment_verdict: ALIGNED (swept params N, alpha, order, dist each
  directly experienced by the readout; no partition/effective-param mismatch)
- discriminating_fraction: 0.5+ (>= 0.30; see above)
- composition_edges: [] (NO primitive-to-primitive composition; single closed-form
  readout stage -> no shape-mismatch surface)
- positive_control_arms: iid super-quad lift (self-test asserts poly8-poly2 recall
  gap > 0.15 on correlated codes at N=256; FULL requires iid_lift >= 1.50x). This
  is a NEW readout mechanism, not a re-invocation of a prior chain-grade primitive,
  so Gate D "reproduce prior CG at test regime" is N/A (no cited prior atom to
  reproduce); the positive control is the idealized-iid textbook lift instead.
- functional_requirements: (1) recoverable-capacity of an associative store ->
  dense reconstruction readout; (2) fair pairwise baseline -> poly2 arm; (3)
  must-fail floor -> scramble control; (4) idealized positive control -> iid arm.
- real_code_path_exercised: [make_codes, make_queries, dense_readout_recall,
  _separation_weights, capacity_curve, scramble_recall_at] (self-test constructs +
  calls each REAL fn the FULL uses; this cell builds NO KGStore -- its substrate
  IS the closed-form readout stack; F.1 declared+exercised)
- substrate_signature_checked: [dense_readout_recall] (self-test binds the readout
  call kwargs against inspect.signature; F.2/F.3; base/portable numpy only, no
  version-specific substrate kwargs -> no local/remote drift surface)
- guard_baseline_validated: N/A (no control-beats-baseline break-guard in this
  cell; F.4 not applicable -- declared N/A, warns-only, never blocks)

## Validity preflight (mode=enforce for F.1-F.4; classes 1-4 warn)
Self-test calls `run_validity_preflight([...])` with: real_code_path (F.1),
substrate_signature (F.2/F.3), positive_control (Class 1), metric_moves (Class 2),
negative_control_margin (Class 4, scramble >=3 seeds, margin 0.30). MEASURED:
self-test PASS under VALIDITY_PREFLIGHT_MODE=enforce (validity_ok=True).

## Smoke result (GATE)
`--self-test` (enforce): PASS (corr_gap poly8-poly2=0.953; p2 cross=0.12; p8
cross=2.62; scramble ~0.00; validity_ok=True).
`--smoke` (N in {256,512}, 3 seeds, 84.9s): HARD_PASS. iid pos-control 12.20x;
corr_lift 8.87x (mild 16.71x / mod 9.71x / strong 4.31x); scramble worst 0.008,
intact ~1.0; cardinality 96/96.

## Downstream
Landed-VET on the FULL by Skunkworks: confirm iid pos-control fires at N=2048
(watch for baseline censoring at ALPHA_MAX compressing the ratio), confirm the
correlated-lift gradient, and re-tier if any (dist,N) lift is dominated by
censoring/floor artifacts rather than genuine separation-sharpness.
