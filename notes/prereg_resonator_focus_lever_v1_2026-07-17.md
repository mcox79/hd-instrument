# Pre-reg: substrate_resonator_focus_lever_v1

**Date:** 2026-07-17. **Filed by:** exp_dev (cell author).
**Trigger:** Director task -- cheap decisive test of whether anything raises the resonator's
joint-factor "focus" beyond its ~F=3-4 sweet spot. Source: `notes/research_wm_focus_limit_functional_increase_2026-07-17.md`
(the drill) + `notes/research_working_memory_integration_upper_limit_2026-07-16.md`.

Prior-work check (SUBSTRATE-KB CONCEPT-QUERY, mandatory before authoring): ran
`bash tools/substrate_query.sh "resonator joint factorization focus limit hierarchical chunking
sequential factor resolution capacity peak"`. Top hit cosine=0.4248 = `resonator_factorization_v1`
itself (the base harness this cell extends, prior verdict MIDDLE_BAND) -- no independent prior cell
already tests hierarchical/decorrelated F-scaling above cosine=0.30. This cell is a genuine
extension, not a rediscovery.

## Regime calibration (MANDATORY read before the bands below)

The drill's "known F=3-4 sweet spot" is a LITERATURE reference (Frady et al. 2020's own
regime/init), not yet measured on THIS substrate's `resonate()` implementation. Two facts
established by direct measurement before locking this pre-reg:

1. The ALREADY-LANDED `data/exp_resonator_factorization_v1/metrics.json` is `run_mode: smoke`
   (never landed FULL). Re-running that cell FULL (`python experiments/exp_resonator_factorization_v1.py`,
   this session) at its own default N=2048/M=30 gives: K2=1.000, K3=0.613, K4=0.047
   MEASURED@d:/AI/hd-instrument/data/exp_resonator_factorization_v1/metrics.json:per_seed[0].by
   -- i.e. K=4 is ALREADY collapsed at that regime, not a sweet spot.
2. A calibration sweep (this session, scratch script, N x M x K grid, TRIALS=30-40,
   MAX_IT=100-200) located a regime where the peaked capacity curve is clean and K=4 sits at a
   genuine (if moderate, not saturated) reference point: **N=16384, M=8, MAX_IT=200**:
   K3=1.000, K4=0.700, K6=0.067, K8=0.000 (TRIALS=40 dry run;
   HYPOTHESIZED@this-prereg-calibration-run, to be re-measured at full TRIALS inside the committed
   cell before the verdict is read).

This regime is adopted for the FULL cell: **N_DIM=16384, M_FACTOR=8 (per-slot codebook size),
MAX_IT=200**. K=4 (REF) is a real, moderate (not saturated) reference -- the pre-reg bands below
are stated as RATIOS against REF (measured live, in-run), not hardcoded absolutes, so they remain
valid regardless of small run-to-run fluctuation in the exact REF value.

## Arms (per Director's task; core 3, deferring iv/v -- see "Deferred arms" below)

1. **FLAT** (control, must-fail at high F): one joint `resonate()` call over all F factor slots
   at once, F in {3, 4, 6, 8}. Reuses `resonate()`/`cleanup()`/`phasor()` verbatim from
   `experiments/exp_resonator_factorization_v1.py`.
2. **HIERARCHICAL** (mechanism, drill's #1 lever): split F into two groups of <=4
   (F=6 -> 3+3, F=8 -> 4+4). Stage 1: `resonate()` group A's ka factors alone (own per-slot
   codebooks) -> decoded indices -> reconstruct `s_A_hat` (product of the DECODED, not
   ground-truth, codewords -- so stage-1 errors genuinely propagate, matching the
   Christiansen & Chater "leaky chunk-and-pass" compounding-noise prediction). Stage 2: isolate
   group B via `s_B_isolated = S * conj(s_A_hat)` (the exact same unbind primitive `resonate()`
   already uses internally -- no new primitive), then `resonate()` group B's kb factors alone.
   Overall success = stage-1 exact match AND stage-2 exact match (same "all factors correct"
   criterion as FLAT, for a fair comparison). S itself (the full F-way composite) is IDENTICAL
   bit-for-bit to FLAT's S (bind is associative/commutative) -- the two arms differ ONLY in
   decode strategy, not in what was encoded.
3. **DECORRELATED codebook** (tests Prediction 3 -- should show NO peak shift): same FLAT
   `resonate()` decode, same F in {3,4,6,8}, but the per-slot codebook's phase-generating matrix
   is orthogonalized (QR on the theta matrix, rescaled to match the baseline's phase-spread,
   wrapped into [-pi,pi]) before exponentiating to unit-modulus phasors -- decorrelates the
   codebook's cross-row structure while leaving the bind/unbind math untouched (exp(1j*theta) is
   unit-modulus regardless of how theta was generated, so `resonate()`'s invertibility is exactly
   preserved; zero risk to the core primitive). The DENSE/baseline reference for this comparison
   is FLAT's own already-computed per-K accuracy (reused directly, not independently redrawn) --
   this removes RNG-draw noise as a confound between "dense" and "decorrelated" (they'd otherwise
   differ for reasons unrelated to decorrelation) and saves compute (only the orthogonalized
   condition needs a fresh run). Caveat (declared up front, not discovered after the fact): with
   M=8 << N=16384 the baseline i.i.d. codebook is ALREADY close to orthogonal, so this
   manipulation may have limited headroom -- if so, that itself is informative (decorrelation has
   nothing to fix at this M/N ratio) and will be reported honestly, not papered over.

### Deferred arms (per task's own instruction: "if iv/v are too much for one cell, note as
immediate follow-up")

- **(iv) paging/streaming register composition**: not built this cell -- genuinely more complex
  (needs a store/rotate mechanic on top of the resonator, not a reuse of existing decode paths
  alone). Flagged as immediate follow-up.
- **(v) orthogonal-subspace decoupled channels**: NOT built fresh -- **already substantially
  answered by prior banked data**: `data/exp_substrate_R6_b2_x_sparse_resonator_v1_n5000/metrics.json`
  uses BLOCK-LOCAL disjoint-subspace codebooks (each of K factors lives in its own non-overlapping
  N/K-sized block) and decodes cleanly to `kmax_res=26` (vs the shared-subspace joint-bind
  resonator's ~F=3-4 ceiling measured here) MEASURED@data/exp_substrate_R6_b2_x_sparse_resonator_v1_n5000/metrics.json.
  This is suggestive PRIOR EVIDENCE that dedicating orthogonal subspaces per factor avoids the
  interference wall entirely -- but it is NOT a clean apples-to-apples test of arm (v)'s question,
  because block-local decode is a mechanistically DIFFERENT operation (no cross-factor binding is
  even possible across blocks; you trade full joint-bind expressiveness for the capacity). A
  dedicated arm-(v) cell (orthogonal subspaces WITHIN a still-jointly-bindable representation) is
  still warranted as a follow-up, not substituted by this citation.

## Functional requirements (gate E)

| Requirement (plain English) | Existing primitive |
|---|---|
| Encode F multiplicatively-bound factors | FHRR complex bind (elementwise multiply), `exp_resonator_factorization_v1.phasor` |
| Jointly decode F factors from one composite | `resonate()` iterative alternating-unbind + codebook cleanup |
| Isolate a sub-composite given a known multiplicand | elementwise complex multiply by conjugate (the exact unbind step `resonate()` already performs internally) |
| Decorrelate a codebook's cross-row structure | QR orthogonalization of the phase-generating matrix (new, but confined to codebook CONSTRUCTION, not bind/unbind math) |

No new bind/unbind/cleanup primitive is introduced. QR-based codebook decorrelation is the one
genuinely new (small, low-risk) piece of code in this cell.

## Compute architecture

- **Class: (b) sequential-CPU with justification.** Each resonate() call is O(K * MAX_IT * M * N)
  -- small (N<=16384, M=8, K<=8); numpy BLAS matvecs are fast even sequentially. Wall-time sanity:
  measured ~0.4-0.5s/call at this N. Total FULL estimate: ~960 resonate() calls/seed x 3 seeds x
  ~0.45s = ~22 min. GPU batching would add engineering risk for a "cheap decisive test" whose
  entire point is reusing existing CPU numpy harnesses unchanged; sequential CPU is justified by
  the <10-min-per-seed wall time and by cell-type (IS the substrate primitive under test, per the
  GPU-batching exemption for primitive-validation cells).
- **Storage strategy:** no_storage / no_composition beyond the single per-trial bind -- this is a
  single-hop factorization capacity test, not a multi-hop chain.

## Pre-registered bands (locked before FULL dispatch)

Let REF = mean FLAT accuracy at F=4, measured live in this run (averaged over 3 seeds).

**HARD-PASS** (hierarchy is the right lever for focus; decorrelation is not) -- ALL of:
- (a) `hier_F6_acc >= 0.70 * REF` AND `hier_F8_acc >= 0.40 * REF`
- (b) `flat_F6_acc <= 0.30 * REF` AND `flat_F8_acc <= 0.15 * REF` (flat craters, matching the
  literature's peaked non-monotonic curve)
- (c) `hier_F6_acc - flat_F6_acc >= 0.30` (absolute) AND `hier_F8_acc - flat_F8_acc >= 0.20`
  (absolute) -- hierarchy demonstrably rescues accuracy flat loses
- (d) `abs(decorr_F6_acc - flat_F6_acc) <= 0.15` AND `abs(decorr_F8_acc - flat_F8_acc) <= 0.15`
  (decorrelation does not materially rescue the flat collapse -- confirms the two-axis distinction)

**HARD-FAIL:**
- `abs(hier_F6_acc - flat_F6_acc) <= 0.05` AND `abs(hier_F8_acc - flat_F8_acc) <= 0.05`
  (hierarchy provides no rescue at either F -- the drill's #1 lever would be falsified; deprioritize
  in favor of #2 decoupled-channels or #3 paging), OR
- `decorr_F6_acc - flat_F6_acc >= 0.30` (absolute) (decorrelation ALSO rescues focus -- a genuine
  positive surprise contradicting Prediction 3; would need immediate reframing per the research
  note's own instruction, NOT treated as a failure of this cell)

**MIDDLE_BAND:** anything not cleanly meeting HARD-PASS or HARD-FAIL (e.g. hierarchy rescues F=6
but not F=8; or decorrelation shows a partial 0.05-0.30 absolute rescue).

Rationale for ratios instead of the drill's raw 90%/85% suggestion: REF is empirically moderate
(~0.7, not ~1.0) at the calibrated regime, and the two-stage mechanism's own arithmetic predicts
hier_F6 (ka=kb=3, individually EASIER than K4) should land near or above REF, while hier_F8
(ka=kb=4, individually AS HARD as K4) should land near REF^2/REF ~ REF*(K4-stage-success) --
i.e. compounding math predicts hier_F8 sits below REF even in the mechanism-working case. Setting
the F8 floor at 0.40*REF (not 0.85*REF) reflects this honestly rather than adopting the drill's
literature-derived numbers unchanged for a regime the drill's authors did not measure on this
substrate.

## Schema-VET checklist

- `cardinality_ok`: EXPECTED_N_UNITS = n_seeds(3) x [flat K-count(4) + decorr-orthogonalized K-count(4) + hier F-count(2)] = 3 x 10 = 30 per-seed-arm units (decorr's "dense" reference reuses flat's own numbers, zero extra units); verdict logic asserts `len(per_unit) == 30`.
- `arms_differ_verified`: hash-check on final per-K accuracy arrays across flat/hier/decorr (mandatory smoke gate).
- `final_metrics_atomicity`: "tmp_replace" (via `write_metrics`'s existing os.replace atomic write).
- except-ordering: `except SystemExit: raise` / `except KeyboardInterrupt: raise` / `except Exception as e:` (no bare except, no BaseException) around `main()`.
- `crlb_n/a`: "iterative alternating-projection resonance has no published closed-form success-probability formula (Frady 2020 report the operational-capacity curve as an empirical quadratic fit, not closed-form); feasibility established via the empirical regime-calibration dry run above, not an analytic bound."
- `discriminator_reachability`: true (calibration dry run shows K4 in a measurable, non-saturated band and K6/K8 genuinely near-floor -- real room for arms to differ).
- `baseline_in_band`: FLAT-at-F4 (REF) is the actual "baseline in measurable band" checkpoint (~0.7, comfortably 0.05<REF<0.95). FLAT-at-F6/F8 is DELIBERATELY the must-fail control and is EXEMPTED from the 0.05-0.95 band requirement (HP_SCOPE below) -- being near floor there is the intended, correct behavior of the control arm, not a violation.
- `HP_SCOPE`: `{flat_F4: [baseline_in_band], flat_F6/F8: [], hier_F6/F8: [hard_pass_rescue_gates], decorr_F3/F4/F6/F8: [hard_pass_no_shift_gate]}`.
- `calibration_check`: "adaptive_with_discriminator_gate" -- regime (N=16384, M=8) was chosen via the dry-run calibration above specifically because the DEFAULT/literature regime (N=2048, M=30) was already shown (by directly running the existing landed cell FULL) to crater at K=4, which would make this cell's own F=4 "reference" meaningless. The adaptive choice is principled (documented dry-run numbers above) and the discriminator still fires (K6/K8 genuinely collapse relative to K4 at the chosen regime) -- not p-hacked for a predetermined PASS.
- `real_code_path`: self-test constructs the actual `resonate()`, `cleanup()`, hierarchical 2-stage isolate-and-resolve, and QR-decorrelation functions at N=64/M=4/K=2+2 tiny scale (not a synthetic-only branch).
- `progress_logging`: "print_flush_true" (declared defensively; estimated wall time ~22min/seed x 3 = ~66min total, may exceed the 30min/1800s trigger depending on machine speed).
- `deterministic_seeding`: true -- all RNG via `np.random.default_rng(seed)` with fixed integer seeds per seed-slot; no `hash()`-derived seeding anywhere.

## Dispatch

INFRA note: `local_cpu_queue` runner is DOWN. Per task contract, run INLINE/foreground (local
compute authorized). No queue_add dispatch for this cell. Commit-before-run guard: commit this
pre-reg + cell file BEFORE running FULL so the autonomous pipeline can see the pre-registration
timestamp precede the result.
