# PRE-REG: Learned-recurrent settling fix (v1) -- rehabilitation of the settling-parse-selector HARD_FAIL

Date: 2026-07-20
Cell: experiments/exp_settling_fix_learned_recurrent_v1.py
Anchor: settling_fix_learned_recurrent_v1
Author: hdi_exp_dev (design handed off complete from research drill; author implements, does not redesign)
Queue: LOCAL (single codebook build + cheap settling loops; run to completion in foreground when authorized)
needs_orchestrator_store_sync: True

## WHAT / WHY

`settling_parse_selector_richness_v1` landed MIDDLE_BAND/practically-HARD_FAIL: at the richest level
(vocab_size=12000, N_DIM=1024, 17M tokens, seed 7+13), `acc_settle` pooled across richness levels sits
at chance (~0.49-0.53), `mean_final_residual` at every level is ~4e-6 to 1.5e-5 -- MEASURED@d:/AI/hd-
instrument/data/settling_parse_selector_richness_v1/metrics.json:per_level_summary.tok17000000.mean_
final_residual = 1.4789402484893799e-05 -- and the settling arm LOSES to the G3 one-shot thematic-fit
baseline (gap=-0.062: settle_acc=0.531 vs baseline_acc=0.594). A brain-drill
(`notes/research_brain_learned_recurrent_settling_sentence_gestalt_2026-07-20.md`) diagnosed why: the
beta=20 one-shot softmax cleanup is the ZERO-NOISE LIMIT of the Hopfield/EBM/diffusion family (arXiv:
2506.05178 unification result) -- it collapses to a near-fixed-point in ~1 iteration, so residual-of-
change sits at the float32 noise floor by construction, not because coherence carries no signal. The
brain's Sentence-Gestalt mechanism (Rabovsky, Hansen & McClelland 2018) stays graded because (i) its
loss has no one-hot target and (ii) training shifts "the work" from activation-change to connection-
weights. The fix moves along the SAME temperature axis toward the graded regime via a LEARNED scalar,
not a new mechanism.

Full grounding: `notes/research_brain_learned_recurrent_settling_sentence_gestalt_2026-07-20.md`
(HEADLINE, section 3 "the unifying build-fix", "Cheap decisive test", "Falsifiable predictions" --
verbatim bands below) + `notes/research_brain_settle_to_coherence_parse_selection_2026-07-20.md` (G5
item set, G3 baseline, G8 convergence-breakdown convention, the originally-measured noise floor).

## PRIOR-WORK CHECK (mandatory, USER-locked 2026-07-01)

This cell is an explicit, director-commissioned REHABILITATION of a specific named HARD_FAIL
(`settling_parse_selector_richness_v1`), not a fresh concept search -- the "prior work" IS the cell
being rehabilitated and its own two research notes (read in full above), so a fresh substrate_query.sh
concept sweep would only re-surface those same two notes. Ran it anyway per the standing discipline:
`bash tools/substrate_query.sh "learned recurrent settling temperature beta damped step diffusion
Hopfield coherence"`. Prior-work check: top hits are the two source notes themselves (settling_parse_
selector richness note + the learned-recurrent-settling brain drill, both cosine>0.30, both already
read in full above and being directly built on/rehabilitated) -- no OTHER unrelated prior cell surfaced
at cosine>0.30. This is a rehabilitation of a named prior result, not a rediscovery.

## REUSE DISCIPLINE (one-variable: ONLY the settling dynamic differs across the 4 variants)

Reused VERBATIM from `experiments/exp_settling_parse_selector_richness_v1.py` (imported, not
reimplemented, so the codebook/item/seed identity is structural, not a promise):
- `load_pp_candidates`, `select_balanced_items` (same PP-attachment G5 item set, same
  `ITEM_SAMPLE_SEED=0` class-balanced sample)
- `build_fixed_vocab`, `build_richness_codebook` (same ppmi_svd codebook builder)
- `make_role_atoms` (same 5 fixed structural role atoms, seed=999), `compose_candidate` (same
  role-filler binding, same G6 construction symmetry), `_l2norm_rows_np`
- `settle` (the ORIGINAL one-shot beta=20 loop -- this literally IS variant A)
- `score_baseline_thematic_fit` (the G3 real baseline, for the HARD-PASS-2 comparison)

NEW in this cell (the only things that vary): `settle_damped` (adds a damped step to the SAME
unbind-cleanup-rebind loop), `settle_random_control` (D's must-fail direction-randomization),
`_fit_beta` (C's grid search on a held-out FIT split). Everything else -- codebook, items, roles,
seeds -- is byte-identical to the source cell's construction path.

## REGIME (single codebook, no richness sweep -- this drill is about the settling DYNAMIC, not richness)

**FULL** (matches the source cell's RICHEST level exactly, where the noise floor was measured):
vocab_size=12000, N_DIM=1024, n_tokens=17,000,000, min_count=5, seed=7, n_per_class=24 (48 items,
same class-balanced PP-attachment set).

**SMOKE** (matches the source cell's SMOKE preview level -- DISCRIMINATOR-MUST-SURVIVE-SCALE option C,
same reduced vocab/N previewing the FULL richness token-count): vocab_size=3000, N_DIM=256,
n_tokens=8,000,000, min_count=5, seed=7, n_per_class=6 (12 items).

## THE 4 VARIANTS (same codebook/items/seed within a run; only the settling dynamic differs)

- **(A) BASELINE** -- the already-measured one-shot beta=20 cleanup, reproduced verbatim via the
  imported `settle()` function, BETA_HIGH=20.0, T_MAX_A=6 (original's T_MAX), TAIL_K=2 (original's
  tail-k). This IS the HARD_FAIL floor; reproducing it fresh in this cell is the sanity check that the
  codebook/item reuse is faithful (its measured residual variance should match the historical ~1e-5
  scale before any other variant is interpreted).
- **(B) DAMPED-STEP alone** -- `s_next = normalize(s + alpha*(cleanup(s) - s))`, alpha=0.25 (HAND-SET,
  no learning), SAME beta=20.0, T_MAX_FIX=8 (longer than A's budget, to give the damped trajectory room
  to show whether it is genuinely multi-step or still collapses immediately).
- **(C) DAMPED-STEP + LEARNED effective-beta** -- same damped-step structure/alpha as (B), but beta is
  fit by grid search on a HELD-OUT FIT split of the gold labels (BETA_GRID = [0.5, 1.0, 2.0, 3.0, 5.0,
  8.0, 12.0, 20.0]; select the value maximizing FIT-split selection accuracy, tie-broken toward the
  SMALLEST beta -- i.e. prefer the more-graded regime on ties, never the sharper one). Scored/reported
  on the DISJOINT EVAL split for every accuracy/correlation claim (residual-variance/convergence-class
  statistics, which do not compare against gold labels, are additionally reported on the full item set
  for statistical power, per the "no fitting on eval labels USED FOR SCORING" reading -- variance/
  convergence-class is a structural property, not a label-scoring claim).
- **(D) MUST-FAIL CONTROL -- random-recurrent update** -- same damped-step structure/alpha/T_MAX_FIX as
  (B)/(C), but the per-iteration "cleanup" direction is replaced by a random unit vector (deterministic
  per-item-per-candidate RNG seed, fixed-int formula, never `hash()`/`list(set())` per PROT-023) instead
  of the codebook-softmax reconstruction. Decouples "multi-step recurrence exists" from "the direction is
  learned/meaningful."

## FIT/EVAL SPLIT (mandatory guard #2 -- no fitting on the eval labels used for scoring)

Class-balanced half-split of the item set: V-attach items split via `np.random.default_rng(555)`
permutation, N-attach items via `np.random.default_rng(556)` permutation, each split 50/50 with
`sorted()` index lists (PROT-023, never `list(set())`/`hash()`-derived ordering). FULL: 24 FIT / 24
EVAL (12+12 per class each). SMOKE: 6 FIT / 6 EVAL (3+3 per class each). The fitted beta (C) is chosen
using ONLY FIT-split accuracy; every accuracy/margin/correlation number used in the HARD-PASS/HARD-FAIL
gates for (C) is computed on EVAL only.

## READOUTS (per the drill's "Cheap decisive test", all 4 variants)

(i) **Residual-of-change magnitude + variance across items**: pooled tail-mean residuals (mean of last
TAIL_K=2 iterations, same convention as the source cell) across all items x both candidates; variance
compared to variant (A)'s own freshly-measured floor variance (reported in `log10` orders of magnitude
above floor) -- NOT the historical constant alone, so the comparison is apples-to-apples within THIS
run's exact codebook build (the historical value above is cited as an independent cross-check that the
reproduction lands in the same ~1e-5 ballpark).
(ii) **Iteration-count-to-convergence + correct/spurious/non-convergent breakdown** (G8 convention): a
trajectory "converges" at the first iteration t where `residual_t <= 0.05 * residual_1` (RELATIVE
threshold, not absolute -- normalizes across variants whose residual SCALE may differ by orders of
magnitude, and directly operationalizes "1-2 step collapse" vs "genuine multi-step" per the HARD-PASS/
FAIL bands: converged at t<=2 = one/two-step; t in [3, T_MAX_FIX] = genuine multi-step; never converged
within T_MAX_FIX = non-convergent). Per-item: `correct` = predicted candidate's trajectory converged AND
matched gold; `spurious` = converged but wrong; `non_convergent` = the predicted candidate's trajectory
never converged within budget.
(iii) **Spearman rho** between a signed preference score (`pref_score = tail_residual_V -
tail_residual_N`, positive = N-attach preferred) and gold (`1` if N-attach else `0`), on EVAL only for
(C), full-set for (A)/(B)/(D) (no fitting occurred for these three, so no held-out concern).

## FALSIFIABLE PREDICTIONS (copied verbatim from the research note's "Falsifiable predictions" section)

**HARD-PASS (all must hold):**
1. Variant (C) residual variance spans >=3 orders of magnitude above the noise floor measured in the
   original failed cell (demonstrably NOT pinned at the float32 chance value).
2. Variant (C)'s residual (or selection accuracy) correlates with gold plausibility at Spearman
   rho>=0.3, OR beats the one-shot thematic-fit baseline (G3, MEASURED@ ~0.58-0.59 at this exact
   regime) by >=10 percentage points selection accuracy.
3. Variant (C) outperforms variant (A) (trivial, A measured at/near chance) AND outperforms variant (D)
   (must-fail random-recurrent control) by a non-trivial pre-registered margin (>=10 percentage points
   selection accuracy, same convention as G3's margin).
4. The fitted effective-beta in variant (C) lands measurably below beta_c/below the hand-set beta=20
   (i.e. the grid search does NOT select the grid's maximum value), confirmed via genuine multi-step
   (not 1-2 step) convergence -- majority of (C)'s pooled iteration-count classifications land in the
   multi-step band, not the 1-2-step band.

**HARD-FAIL (any one is sufficient to refute -- reported EXPLICITLY if it fires, never silently
re-tuned away):**
1. Variant (C)'s residual stays pinned at/near the float32 noise floor (< 1 order of magnitude above
   the freshly-measured (A) floor) regardless of the learned-beta/damped-step change -- codebook
   pattern-separation forces collapse; the graded regime does not exist for this codebook without also
   changing codebook construction.
2. Variant (C) does NOT beat variant (D) (must-fail random-recurrent control) at all (EVAL accuracy <=
   D's EVAL accuracy) -- multi-step recurrence alone, not the learned direction, explains any gain.
3. Variant (C) shows nonzero residual variance (>= 1 order of magnitude above floor) but null gold
   correlation (|rho| < 0.15 on EVAL) AND does not beat G3 by the 10pp margin -- graded but not
   meaningful.
4. The beta fit in variant (C) converges back to the SAME high-gain value as the grid's maximum (i.e.
   selects beta=20.0, the grid's ceiling) -- the fixed point WAS optimal for this codebook's geometry;
   the informative-graded-residual premise is false for this substrate as currently constructed.

**MIDDLE_BAND**: none of the HARD-FAIL conditions fire but not all 4 HARD-PASS conditions hold
(e.g., beats D and shows a lower-than-20 beta, but the richness/margin falls short of the full bar).

## MUST-FAIL CONTROL PRECONDITION (design-gate, checked at smoke BEFORE any full/interpretation)

Variant (D) must genuinely fail to discriminate: EVAL accuracy should sit near chance (no more than a
generous +-0.20 band around 0.50 at smoke's tiny N=6-eval sample; a materially higher D accuracy at
smoke would indicate construction leakage in the random-control implementation and blocks trusting the
gate-2/gate-3 comparisons against it). Reported explicitly as `must_fail_D_fires` in metrics; if it does
NOT fire, this is reported and the C-vs-D comparison is flagged UNRELIABLE rather than silently used.

## CELL-TEMPLATE MANDATORY declarations

- `arms_differ_verified`: hash-check on the RAW RESIDUAL TRAJECTORIES (all items x both candidates x
  all iterations), not just discrete predictions -- more sensitive to an accidental same-function-reuse
  bug than a prediction-only hash, since discrete predictions MAY legitimately coincide across variants
  (e.g. damping not flipping any decision) without that being a bug. `arms_differ_exempted`: predictions
  (not trajectories) may coincide between (A) and (B) legitimately if damping never flips a decision;
  this is NOT exempted from the trajectory-hash check, only from a naive prediction-only check.
- `final_metrics_atomicity`: `tmp_replace` (os.replace), single-shot (no tuning iteration).
- `except SystemExit: raise` BEFORE `except Exception` (no bare/BaseException).
- `crlb_n/a`: "residual/coherence discrimination test; no argmax-capacity noise floor of the CRLB form;
  this cell's own floor is EMPIRICALLY measured fresh from variant (A) each run, not assumed."
- `baseline_in_band`: G3 baseline + majority-class sanity control reported (informational; not a gating
  condition for this cell's core HP/HF logic, which is about the 4 settling variants).
- `discriminator survives scale`: smoke previews the FULL richness token-count (8M, same as the source
  cell's smoke preview) at reduced vocab_size/N_DIM -- DISCRIMINATOR-MUST-SURVIVE-SCALE option C.
- `cardinality_ok`: `EXPECTED_N_UNITS = n_items` (one codebook, one seed, all 4 variants scored per item
  in a single pass) = 48 for FULL, 12 for SMOKE.
- per-unit failure-class instrumentation (no bare except).
- `deterministic_seeding`: fixed int seeds throughout (item sample seed 0, role seed 999, codebook seed
  7, FIT/EVAL split seeds 555/556, D's per-item-per-candidate seed base 707070 + deterministic mixed-
  radix offset); no `hash()`/`list(set())` ordering (PROT-023 compliant; `sorted()` used for split index
  lists).
- all numbers in the cell/report tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@.

## Compute architecture

Class: (b) sequential-CPU with justification -- ONE codebook fit (vocab_size=12000, N_DIM=1024, 17M
tokens; MEASURED@ from the source cell's own dry-run, ~120-150s per fit at this exact regime) dominates
wall time; the 4 settling variants are cheap elementwise bind/unbind + small (vocab_size-dim) softmax
matmuls per item/candidate/iteration (48 items x 2 candidates x <=8-10 iterations x 5 roles, a few
thousand tiny vector-matrix ops per variant; (C)'s grid search adds ~8x the (B)-equivalent cost on the
24-item FIT split only). Estimated FULL wall time ~6-9 minutes total -- run foreground-to-completion
when authorized (not detached), per COMPUTE-PROPORTIONALITY. Suggested `--timeout` when dispatched:
900s (FULL), 180s (SMOKE) -- 50% margin over the formula estimate above. Storage: no persistent store;
in-memory per-run. THIS SPAWN: design + smoke ONLY, no queue_add, no full run, no push (per Director's
task contract).

## Deflated confidence

P_deflated(fix HARD-PASSes) = 0.40 -- HYPOTHESIZED@notes/research_brain_learned_recurrent_settling_
sentence_gestalt_2026-07-20.md (the research note's own deflated estimate; novel-synthesis cap applied,
genuine risk that this codebook's pattern-separation places beta_c above beta=20's neighborhood
entirely). Reported as hypothesis-pending-VET, not fact, per the standing "caveat interpretation"
discipline. Do not round up regardless of smoke outcome.
