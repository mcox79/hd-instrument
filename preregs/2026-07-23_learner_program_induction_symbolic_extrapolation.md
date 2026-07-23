# Prereg: PLUGIN 4 program-induction for hdlab/learner + symbolic-extrapolation test on the
# implicative sign x negation unseen cell (bother-negated)

Filed BEFORE the official `self_test()` / `full` run of
`experiments/exp_learner_program_induction_symbolic_extrapolation_v1.py`. Design-phase informal
smoke checks (ad hoc `python -c` probes while building `hdlab/learner/plugins/proginduction_plugin.py`)
already surfaced the key mechanism finding below (see "Design-phase finding" section) -- this
prereg does NOT retune any band in response to that finding; the bands below are the task's
original spec, unmodified, and the official run is what produces the landed verdict.

## What this build is

PLUGIN 4 = program-induction (bounded enumerative symbolic regression over a small boolean DSL:
`atom | NOT | AND | OR | XOR | XNOR`), registered into the existing centralized Learner module
(`hdlab/learner/core.py` + `hdlab/learner/registry.py`, banked 29487/29489) as a 4th hypothesis-
class plugin, alongside `estimation` (29476-wrap) / `ruleind` (29485-wrap) / `gam` (29489, the
prior extensibility proof). New file: `hdlab/learner/plugins/proginduction_plugin.py`. One-line
registration edit to `hdlab/learner/registry.py` (import + `PLUGINS` dict entry). **Zero changes
to `hdlab/learner/core.py`** (extensibility claim, verified by `git diff --stat` at run time).

The plugin's `apply()` EVALUATES the induced boolean expression on the atom values of a new item
-- including atom-value combinations that never co-occurred in any training episode -- rather
than consulting a per-combination lookup table. This is the mechanism property (symbolic
extrapolation) that `estimation`/`ruleind`/`gam` structurally lack (they fall back to marginals/
episodic-residual on an unseen combo).

## Discriminator + reused data (per task spec)

Reuses banked 29492's data + features + associative-arm code paths verbatim:
`experiments/exp_learner_implicative_sign_supplied_generalization_v1.py`
(`feat_fn_sign`, `linear_fit`/`linear_predict`, `simvote_fit_predict`, `module_fit`/`module_predict`,
`scramble_items`, `GOLD.build_implicative_gold`). The "unseen (sign,neg) cell" = leave-one-verb-out
holding out `bother`, which uniquely zeroes the (sign=pos, negated=True) joint cell (n=6, all
gold=NOT_REALIZED; MEASURED@this run) -- the exact cell banked 29492 found the associative module
arm scores 0.0 on (a marginals-driven "REALIZED" mispredict for every item, per 29492's
`UNCOVERED_EXTRAPOLATION_PASS_MIN` framing: `acc_module_uncovered` measured 0.0 in that cell's own
run).

## Pre-registered bands (declared BEFORE the official run; task's original spec)

**HARD_PASS (ALL four must hold):**
1. `unseen_cell_acc_proginduction >= 0.80` -- proginduction's induced formula, applied to the
   bother-negated (pos,True) unseen cell, classifies it correctly (matches 29492's own
   `UNCOVERED_EXTRAPOLATION_PASS_MIN = 0.80` convention).
2. `module_autoselects_proginduction == True` -- `hdlab.learner.registry.learn()` with
   `proginduction` added as a 4th candidate (alongside estimation/ruleind/gam) on the
   bother-holdout training fold picks `chosen_name == "proginduction"` via `mdl_select` (the
   compact formula must out-compress ruleind's conjunction-lookup and gam's additive+interaction
   fit on THIS fold, not just beat the null).
3. `core_py_unchanged == True` -- `git diff --stat -- hdlab/learner/core.py` is empty.
4. `generality_2nd_task_pass == True` AND `generality_3rd_task_pass == True` -- the SAME plugin
   code (no task-specific branch) recovers the exactly-correct truth table (100% accuracy over
   the FULL domain, not just training rows) on (a) AND of 2 boolean atoms with the full 2x2 domain
   covered in training, and (b) 3-variable MAJORITY with the full 2^3 domain covered in training --
   proof this is a general DSL search, not an XNOR-hardcoded shortcut.

**HARD_FAIL (ANY holds):**
1. `unseen_cell_acc_proginduction < 0.80` (formula does not fill the unseen cell correctly), OR
2. `module_autoselects_proginduction == False` (MDL does not prefer the compact formula over the
   associative plugins on this fold), OR
3. `core_py_unchanged == False` (extensibility claim broken), OR
4. Either generality task scores < 1.0 on its own full domain (mechanism itself is broken /
   effectively hardcoded, not a general search).

If HARD_FAIL fires ONLY via (1)/(2) while (3) and (4) both hold (core untouched, general
mechanism verified sound on two independent full-domain tasks): report distinctly as
`HARD_FAIL_UNSEEN_CELL_UNIDENTIFIABLE` (mechanism sound, but THIS specific real-data cell is
information-theoretically unresolvable from the 3 populated cells alone, per the design-phase
finding below) rather than `HARD_FAIL_MECHANISM_BROKEN` (which would mean the search/grammar
itself doesn't work). Both are HARD_FAIL under the letter of bands 1-4 above; the distinction is
diagnostic, not a downgrade of the verdict.

## Design-phase finding (HYPOTHESIZED->MEASURED during build; stated here for pre-registration
## transparency, NOT used to retune any band above)

Ad hoc design-phase probes (informal, pre-official-run) found that on the bother-holdout fold,
the (sign,negated) 2x2 truth table has exactly 3 of 4 cells populated (train: (pos,False)=20,
(neg,False)=60, (neg,True)=23; (pos,True)=0 -- MEASURED@design-phase probe, reproduced by the
official run below). With exactly 1 cell fully unobserved, elementary Boolean counting shows
**exactly 2** functions of 2 binary atoms are consistent with the 3 observed cells (the one that
assigns the missing cell to whichever label, and its complement on that one cell) -- and the two
candidates that achieve a PURE (zero-training-error) partition on this data are `OR(sign=pos,
neg=True)` and `XOR(sign=pos, neg=True)`, which are **provably identical on all inputs except the
unobserved (1,1) cell** (OR and XOR differ ONLY at input (True,True)). A direct recompute
(MEASURED@design-phase probe) confirmed their `data_bits` are bit-identical
(2.8016619102115734 == 2.8016619102115734) and their `node_count` (hence `model_bits`) are equal
-- an EXACT MDL tie, not an approximate one. This is an information-theoretic property of the
data (3 known bits leave 1 bit of the 4-bit truth table undetermined), not an implementation
defect: NO compression-based search over this SAME 2-atom feature space can break this specific
tie without either (a) actual data in the missing cell, (b) a 3rd informative atom, or (c) an
external structural prior (e.g., Karttunen's definitional claim that "sign" is BY DEFINITION what
flips under negation -- a deductive fact, not a distributional regularity, which is exactly what
banked 29492's own brain-check flagged as the missing ingredient). THEORETICAL prediction for the
official run, given this finding: `unseen_cell_acc_proginduction` will land at 0.0 (the tie
resolves to whichever function is enumerated first in the DSL search, `OR` before `XOR` in this
implementation's fixed `_BINARY_OPS` order) -- i.e. THEORETICAL@this-analysis: HARD_FAIL via band
1, most likely also via band 2 (ruleind's per-rule accounting was separately observed, informally,
to out-compress a single shared 2-node formula on this same fold). Bands 3/4 are independent of
this finding and are expected to hold (mechanism-soundness checks on non-degenerate synthetic
data, unrelated to the real task's missing-cell identifiability wall).

## Controls (reported, non-gating unless stated)

- **Associative-arm reproduction**: `linear`/`simvote`/`module` (estimation+ruleind+gam only, no
  proginduction) reproduce 29492's own uncovered-subset result on the SAME bother-negated cell
  (expected ~0.0, matching banked 29492's `acc_module_uncovered` measurement) -- the must-fail
  contrast baseline.
- **Label-shuffle collapse**: `scramble_items` (29492's verbatim per-verb sign permutation,
  gold_class held at the TRUE entailment) must collapse proginduction's covered-subset accuracy
  relative to the true-sign run (delta >= 0.25, matching 29492's `SCRAMBLE_COLLAPSE_MIN`).
- **arms-differ hash check** (META_RULE_AF) across linear/simvote/module/proginduction predicted
  classes on the covered subset.

## Compute architecture

Class (b) sequential-CPU, closed-form enumeration + counting only (no torch, no matmul). n=114
real items + 2 tiny synthetic generality tasks (AND: 40 items; 3-var MAJORITY: 160 items). Wall
time sub-second to low-seconds. LOCAL-ONLY, foreground-to-completion, NO queue, NO push, NO
remote-persist, NO atom bank (skunkworks VETs separately). Deterministic:
OMP/MKL/OPENBLAS_NUM_THREADS=1, fixed int seeds only (no `hash()`-derived RNG/ordering, PROT-023).

## Cell-template mandates (applicable subset)

- `arms_differ_verified` at full (hash test over covered-subset linear/simvote/module/
  proginduction predicted-class tuples).
- `final_metrics_atomicity: tmp_replace` (`os.replace`).
- `except SystemExit`/`KeyboardInterrupt`: raise BEFORE `except Exception` (no `BaseException`).
- `crlb_n/a`: accuracy/compression-ratio + formula-recovery measurement, not a capacity/CRLB cell.
- `baseline_in_band: n/a` (linear/simvote are the discriminating baselines under test, per 29492's
  own precedent).
- `discriminator survives scale: n/a` (fixed real-data n=114 + 2 fixed tiny synthetic tasks, not
  scale-swept).
- `cardinality_ok`: `EXPECTED_N_UNITS=1` (single real-data bother-holdout fit + 2 generality tasks
  + scramble control + arms-differ check; no seed/sweep axis).
- `calibration_check: default_ok_for_this_regime` (MDL two-part code, module-wide formula, same
  currency as gam/ruleind/estimation).
- `deterministic_seeding: true`.
- All numbers in the cell docstring/report tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@.
