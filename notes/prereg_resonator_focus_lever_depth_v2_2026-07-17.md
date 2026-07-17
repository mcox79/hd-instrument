# Pre-reg: substrate_resonator_focus_lever_depth_v2

**Date:** 2026-07-17. **Filed by:** exp_dev (cell author).
**Trigger:** Director task -- probe the hierarchical-staging DEPTH-vs-WIDTH tradeoff and the depth
ceiling at F=8, following up `exp_substrate_resonator_focus_lever_v1` (landed MIDDLE_BAND,
commits e38e711fe + c75da0e79). That cell showed 2-stage (4+4) only PARTIALLY rescues F=8
(hier_F8=0.161 = stage1_acc^2 = 0.40^2, two marginal K=4 decodes) while F=6 (3+3) gets a CLEAN
total rescue (1.000). Question: does a FINER split (3+3+2, or 2+2+2+2) beat the COARSER 4+4 at the
SAME total F=8 by keeping each stage more in-band, and where does adding depth stop helping?

Prior-work check (SUBSTRATE-KB CONCEPT-QUERY, mandatory before authoring): ran
`bash tools/substrate_query.sh "hierarchical staging depth width tradeoff resonator focus
factorization joint decode chunking"`. Top hits cosine=0.3115 (barely above the 0.30 threshold):
(1) a 2026-06-04 research-drill note flagging "resonator network depth ceiling analysis" as a
TIER-1 NEXT-DRILL CANDIDATE (never executed as a cell -- a suggestion, not a landed result), and
(2) a 2026-06-08 multimodal-scene-graph note stating "hierarchical binding depth with cleanup:
substrate supports depth 5-6" for a DIFFERENT primitive (bind+cleanup chain depth, not resonator
joint-factorization staging-width tradeoff). Neither is a landed empirical cell on THIS specific
question. This cell is a genuine, direct extension of the landed v1 cell, not a rediscovery.

## Harness reuse (verbatim per task pointer)

`make_theta`, `phasor_from_theta`, `cleanup`, `resonate`, `compose`, `make_books` are copied
UNCHANGED from `experiments/exp_substrate_resonator_focus_lever_v1.py`. Same regime:
**N_DIM=16384, M_FACTOR=8, MAX_IT=200**. The decorrelation arm (v1's arm iii) is NOT reused here --
out of scope for a depth-vs-width question (already answered: decorrelation is a storage-axis fix,
not a focus-axis fix).

### Generalizing v1's 2-stage recipe to N stages

v1's 2-stage hierarchical decode is, precisely: stage 1 decodes group A directly from its OWN
clean sub-composite `s_a = compose(books_a, true_a)` (no interference at this stage -- models
online/incremental "chunk-and-pass" encoding where group A is resolved before group B is even
layered in); stage 2 isolates group B from the full composite `s_full = s_a * s_b` by
conjugate-multiplying out the RECONSTRUCTED (not ground-truth) group-A identity
`s_a_hat = compose(books_a, dec_a)`, so stage-1 errors genuinely leak into stage 2 ("leaky
chunk-and-pass") while a correct stage-1 cancels cleanly.

The N-stage generalization (verified algebraically reduces EXACTLY to v1's 2-stage code at n=2,
confirmed in self-test below) tracks a running "partial composite through stage i" and
conjugate-removes ALL prior stages' reconstructions before decoding stage i:

```
group_sig[i] = compose(books[i], true[i])          # each stage's own clean sub-signal
running = 1; prior_recon = 1
for i in range(n_stages):
    running = running * group_sig[i]                # composite through stage i (online, no future groups revealed)
    s_iso = running * conj(prior_recon)              # remove all EARLIER stages' reconstructions
    dec[i] = resonate(s_iso, books[i], k_i)
    prior_recon = prior_recon * compose(books[i], dec[i])
```

No new bind/unbind/cleanup primitive introduced -- `decode_multistage` is pure orchestration of the
existing `resonate`/`compose` calls (functional-requirement gate E: "isolate a sub-composite given
known multiplicands" = the same conjugate-multiply `resonate()` already performs internally, now
applied iteratively across N stages instead of 2).

## Arms (all F=8 arms share TOTAL F=8; F=6 arms are a secondary, cheap ceiling-probe set)

**F=8 core set (the target regime):**
1. `flat_F8` -- one joint `resonate()` call over all 8 factors (must-fail control, reproduce v1's
   0.006).
2. `2stage_4_4` -- split [4,4] (reproduce v1's 0.161, the baseline TO BEAT).
3. `3stage_3_3_2` -- split [3,3,2] (candidate finer split).
4. `4stage_2_2_2_2` -- split [2,2,2,2] (candidate finest split / depth-ceiling probe).

**F=6 secondary set (cheap over-splitting-hurts-when-easy check; F=6 2-stage already known to
cleanly saturate at 1.000 per v1, so THIS set asks: does adding UNNECESSARY depth to an
already-easy regime cost anything?):**
5. `flat_F6` -- reproduce v1's 0.072 must-fail control.
6. `2stage_3_3` -- reproduce v1's 1.000 clean rescue.
7. `3stage_2_2_2` -- does over-splitting an easy regime hurt?

**REF arm:** `flat_F4` -- reproduced LIVE (not hardcoded) exactly as v1 did, since all bands below
are ratios against REF, not absolute numbers (regime-fluctuation-robust per v1's own rationale).

**F=10 explicitly OUT OF SCOPE this cell** (compute-proportionality / ONE VARIABLE discipline):
the core Director question is squarely about F=8 (where 2-stage already partially failed); adding
F=10 would require yet more split combinations for comparable coverage, diminishing focus and
adding ~25% wall time for arguably lower marginal information (flat_F10 would almost certainly
floor at 0, and F=6/F=8 already bracket the "does depth help / where does it stop" story). Flagged
as an immediate follow-up if F=8's finer-split result is informative enough to warrant pushing
further.

Total units/seed = 3 (flat F4/F6/F8... wait F4 counted once) -- precisely: flat{4,6,8}=3 +
stage_F8{2,3,4-stage}=3 + stage_F6{2,3-stage}=2 = **8 units/seed**. `EXPECTED_N_UNITS = 8 x 3
seeds = 24` (META_RULE_H).

## Compute architecture

- **Class: (b) sequential-CPU with justification** (same as v1). Per-trial cost of an N-stage
  split is `MAX_IT x sum(k_i)` = `MAX_IT x F` REGARDLESS of how F is split across stages (resonate's
  inner loop cost scales with its own K and MAX_IT is fixed at 200) -- so 3-stage and 4-stage arms
  cost ABOUT THE SAME as 2-stage at the same F, not more. Total F-equivalent-work per seed here
  (18 [flat] + 24 [3x F8-splits] + 12 [2x F6-splits] = 54) is close to v1's landed 56
  F-equivalent/seed (which took 1122s / 3 seeds = 374s/seed). Estimate: **~15-20 min total for 3
  seeds FULL**. Below the 30-min/1800s progress-logging trigger but declared defensively anyway
  (machine-speed variance).
- **Storage strategy:** no_storage / no_composition beyond the per-trial multi-stage bind -- single-hop
  factorization-capacity test, not a multi-hop chain (same as v1).

## Pre-registered bands (locked before FULL dispatch)

Let REF = mean `flat_F4` accuracy, measured live (3-seed mean). Let `floor = 0.40 * REF` (the
exact F8 floor v1's 2-stage MISSED, ~0.224 given v1's REF=0.561 -- recomputed live here, may shift
slightly with new book draws).

**Gate D reproduction check (baselines-must-reproduce, informs `repro_ok`):**
- `abs(flat_F6 - 0.0722) <= 0.10` (v1 landed: 0.0722)
- `abs(flat_F8 - 0.00556) <= 0.08` (v1 landed: 0.00556)
- `2stage_3_3 >= 0.85` (v1 landed: 1.000 -- clean ceiling, expect near-reproduction)
- `abs(2stage_4_4 - 0.1611) <= 0.12` (v1 landed: 0.1611; wide tolerance reflects the
  per-seed range 0.15-0.183 already observed PLUS additional between-book-draw variance -- each
  K-config's codebook is drawn ONCE per seed then reused across all 60 trials, so between-seed
  variance already captures most of this, but a fresh independent run may land a differently-lucky
  book)

If ANY reproduction check fails: `repro_ok=False` -> verdict forced to MIDDLE_BAND tagged
`GATE_D_REPRO_MISMATCH` (downstream finer-split arms are suspect per the same-primitive-different-run
Gate D logic; do not trust a HARD_PASS/HARD_FAIL read if the known baselines didn't reproduce).

**Core discriminator (only evaluated if `repro_ok=True`):** let
`best_finer_F8 = max(3stage_3_3_2_F8, 4stage_2_2_2_2_F8)`, `gap = best_finer_F8 - 2stage_4_4_F8`.

- **HARD-PASS:** `best_finer_F8 >= floor` AND `gap >= 0.05` (a finer split both clears the floor
  4+4 missed AND measurably beats 4+4, not just noise).
- **HARD-FAIL:** `gap <= 0.03` (finer is no better than 4+4 within noise -- depth-compounding
  dominates the in-band benefit; CAN-FAIL is real: more stages = more leaky-chunk-and-pass error
  propagation opportunities, and this pre-reg explicitly allows that to win).
- **MIDDLE_BAND:** anything else (e.g. `gap` in (0.03, 0.05) or finer helps but doesn't clear the
  floor).

**Depth-ceiling reporting (informational, not a pass/fail gate):**
- Compare `4stage_2_2_2_2_F8` vs `3stage_3_3_2_F8`: if the 4-stage split is NOT better (gap <= 0.03
  or negative), report "depth ceiling reached at 3 stages for F=8" in verdict_msg; if better,
  report "depth still helping through 4 stages, ceiling not reached in this test."
- Compare `3stage_2_2_2_F6` vs `2stage_3_3_F6`: if 3-stage is meaningfully WORSE (drop >= 0.10),
  report "over-splitting an already-easy regime costs accuracy" (a genuine possible negative
  finding on the depth axis, distinct from the F=8 result).

**Per-stage decode accuracies (MANDATORY, gate #5 of the design contract):** every arm reports
per-stage marginal accuracy (each stage's own unconditional exact-match rate) AND the measured
overall (joint, all-stages-correct) accuracy, alongside the NAIVE PRODUCT of per-stage marginals --
so the compounding law (overall ~ product of per-stage) is directly checkable, not just asserted.
Any large deviation between naive-product and measured-overall is reported honestly (expected:
some deviation, since later stages' actual difficulty is CONDITIONAL on earlier-stage correctness,
not independent -- the naive product is a first-order approximation, not an exact law).

## Schema-VET checklist

- `cardinality_ok`: `EXPECTED_N_UNITS = 3 seeds x 8 units/seed = 24`; verdict logic asserts
  `unit_count == 8` per seed (META_RULE_H).
- `arms_differ_verified`: hash-check across all per-seed-vector arms (flat_F4/F6/F8,
  2stage_4_4/3stage_3_3_2/4stage_2_2_2_2, 2stage_3_3/3stage_2_2_2) -- 8 arms, all shape (3,)
  (mandatory smoke gate, META_RULE_AF). **Declared exemption (general rule, not a hardcoded arm-name
  list):** smoke run confirmed FOUR configs whose every component stage is K<=3 (3stage_3_3_2_F8,
  4stage_2_2_2_2_F8, 2stage_3_3_F6, 3stage_2_2_2_F6) all saturate to 1.000 -- a genuine, honest tie
  (K<=3 decodes are near-ceiling by construction per v1's own regime; "over-splitting costs nothing"
  / "depth ceiling reached" are themselves valid findings, not copy-paste bugs). Symmetrically,
  must-fail controls (flat_F8, 2stage_4_4) can tie at 0.000 at low TRIALS. Any two arms that both
  land at a SATURATED extreme (0.0 or 1.0) are bit-identical as short float vectors regardless of
  whether their underlying per-trial decode mechanisms differ (they do). The exemption is therefore
  general -- "both arms saturated at floor or ceiling" -- not a fixed pair list; a tie at any
  NON-saturated (mid-range) value remains hard-asserted distinct and WOULD indicate a genuine
  copy-paste-same-computation bug.
- `final_metrics_atomicity`: "tmp_replace" (via `write_metrics`'s existing os.replace atomic write).
- except-ordering: `except SystemExit: raise` / `except KeyboardInterrupt: raise` /
  `except Exception as e:` (no bare except, no BaseException) around `main()`.
- `crlb_n/a`: "iterative alternating-projection resonance has no published closed-form
  success-probability formula (same as v1); feasibility established via v1's own already-measured
  regime calibration (K4 in-band, K6/K8 near-floor at N=16384/M=8), reused unchanged here."
- `discriminator_reachability`: true (v1 already measured K6/K8 genuinely near-floor and K3/K4
  in-band at this exact regime; this cell reuses the same regime, so reachability carries over).
- `baseline_in_band`: `flat_F4` (REF) is the in-band checkpoint (v1 measured ~0.56, comfortably
  0.05<REF<0.95). `flat_F6`/`flat_F8` are DELIBERATELY must-fail controls, EXEMPTED from the
  0.05-0.95 band (HP_SCOPE below).
- `HP_SCOPE`: `{flat_F4: [baseline_in_band], flat_F6/F8: [], 2stage/3stage/4stage_F8: [hard_pass_rescue_gate], 2stage/3stage_F6: [repro_check_only]}`.
- `calibration_check`: "default_ok_for_this_regime" -- N=16384/M=8/MAX_IT=200 is REUSED unchanged
  from v1's already-validated (non-p-hacked, dry-run-calibrated) regime; no new calibration
  decision made in this cell.
- `real_code_path`: self-test constructs the actual `resonate()`, `cleanup()`, `compose()`, AND the
  new `decode_multistage()` orchestration at N=64/M=4 tiny scale (2-stage k=[1,1], 3-stage
  k=[1,1,1], 4-stage k=[1,1,1,1], all exact-decode asserted) -- not a synthetic-only branch.
  ALSO verifies `decode_multistage` at n_stages=2 is algebraically IDENTICAL to v1's original
  2-stage inline code (same s_iso construction), not just "produces a plausible-looking answer."
- `progress_logging`: "print_flush_true" (declared defensively; estimated wall time ~15-20min,
  below the 30-min/1800s trigger but declared anyway per v1's own convention).
- `deterministic_seeding`: true -- all RNG via `np.random.default_rng(seed)` with fixed integer
  seeds (7, 17, 23, matching v1 for direct comparability); no `hash()`-derived seeding anywhere.
- **Discriminator-can-fail verification (design gate #2, MANDATORY at smoke):** self-test includes
  a synthetic unit test feeding hand-constructed aggregate numbers directly into the pure
  `verdict_core()` function, proving BOTH the HARD_PASS path (finer split clears floor + beats
  2-stage by >=0.05) AND the HARD_FAIL path (finer split ties or loses to 2-stage) are reachable --
  i.e. the test is not rigged to always favor finer splits.

## Dispatch

Run INLINE/foreground per task Contract (no queue_add; matches v1's own precedent --
`local_cpu_queue` runner status unchanged since v1). Commit-before-run guard: commit this pre-reg +
cell file BEFORE running FULL so the autonomous pipeline sees the pre-registration timestamp
precede the result.
