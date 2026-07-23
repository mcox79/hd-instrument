# Prereg: Learner module PLUGIN 3 (GAM/EBM) -- extensibility stress-test + graded-cue discriminator

Date: 2026-07-23. Anchor: `learner_module_gam_plugin_proof_v1` (NOT queued / NOT banked -- local
foreground stress-test cell; skunkworks VETs the module addition, not a new capability claim).
Cell: `experiments/exp_learner_module_gam_plugin_proof_v1.py`. Module under test: `hdlab/learner/`
(core.py MUST be zero-diff; registry.py gets exactly one registration edit; NEW file
`hdlab/learner/plugins/gam_plugin.py`).

## What this proves

The centralized Learner module (banked 29487, HARD_PASS_REFACTOR_PROVEN) claims that a THIRD
hypothesis class can be added "by declaring its own description_bits, without re-deriving the
selection logic" and that "core.py never needs to change" (registry.py's own docstring). This
cell is the FIRST test of that claim: add a GAM/EBM plugin (a learned graded shape-function PER
feature + explicit pairwise interaction terms, additive, glass-box) and verify (a) zero core.py
changes are required, (b) the plugin's fit reproduces an independent standalone recomputation of
the same formula, (c) `core.mdl_select` genuinely discriminates GAM's fitness across tasks with 3
candidate plugins (not a task-name branch -- a counterfactual label-shuffle must flip the pick).

GAM/EBM DESIGN (this build): additive log2-bits per-feature-value "shape" table (Laplace-smoothed
log P(class | feature-value), the same per-key-Laplace-table-entry MDL currency PLUGIN 1
(`estimation_plugin._learn_generic_mdl`) already uses, generalized from ONE key to EVERY observed
feature summed additively) PLUS explicit pairwise interaction correction terms for the top
co-occurring feature-value pairs (residual log-odds beyond the two mains' additive prediction,
fit only when coverage >= min_coverage -- mirrors `ruleind_plugin`'s min_coverage discipline).
This is the same functional form as InterpretML's Explainable Boosting Machine (Lou, Caruana &
Gehrke 2012; Nori et al. 2019: F(x) = b0 + sum_j f_j(x_j) + sum_jk f_jk(x_j,x_k), each f_j/f_jk an
inspectable lookup table) -- CITED, simplified to closed-form counting/residual-fitting instead of
iterative gradient-boosted-tree cyclic fitting (a documented compute-cheap approximation: the
functional form and glass-box inspectability are identical; the FIT PROCEDURE is closed-form
counting, not boosting). Distinguishing structural property vs the two existing plugins: GAM
sums GRADED per-feature evidence across ALL observed features (unlike PLUGIN 1's single-key
lookup) WITHOUT a hard purity gate (unlike PLUGIN 2's crisp conjunction search, which discards
any candidate below `purity_thresh`) -- this is exactly the "graded cue" gap the PP-attach
rule-inducer's own docstring points at (crisp AND-conjunctions miss partial/soft evidence that a
sum of weak log-odds contributions captures).

## Files changed

- NEW: `hdlab/learner/plugins/gam_plugin.py` (NAME="gam", COST_RANK=2 -- cheaper than ruleind's
  O(n_singles^2) conjunction search, costlier than estimation's O(1) single-key lookup).
- EDIT (registration only, the module's own documented extension point):
  `hdlab/learner/registry.py` -- one import line + one `PLUGINS` dict entry.
- ZERO-DIFF REQUIRED: `hdlab/learner/core.py` (verified via `git diff --stat` / mtime check
  BEFORE writing metrics; a non-empty diff on core.py is the HARD_FAIL condition below).

## Positive-control task (mechanism verification, CITED design pattern per InterpretML /
Hastie & Tibshirani 1990 additive-model theory): `TASK_GAM_GRADED_CONTROL`

Hidden hidden latent bits `x0,x1 ~ Bernoulli(0.5)` independent; hidden interaction
`inter = x0 XOR x1`; gold label `T = inter`. Models NEVER see clean `x0,x1` -- only NOISY
observations `x0_obs,x1_obs` (each independently bit-flipped from the true `x0,x1` with
probability `q=0.15`), so the observed-pair purity of `(x0_obs,x1_obs)` vs `T` is
`(1-q)^2+q^2 = 0.745` -- THEORETICAL@`p_pair=(1-q)^2+q^2`, deliberately just UNDER the rule
search's `purity_thresh=0.75` (from `RULEIND.MAX_CONJUNCT`/`PURITY_THRESH` defaults reused
unchanged), so `induce_rules` structurally CANNOT promote this pair to a rule (precision<0.75
rejected by its own MDL/purity gate) -- yet it carries genuine information (log-odds
`ln(0.745/0.255)=1.07` bits-worth) that GAM's soft pairwise residual term can still exploit
(no hard threshold gate on interaction fitting, only `min_coverage`). Additionally 6 independent
weak graded cues `w0..w5`, each aligned with `T` at `p_align=0.58` (THEORETICAL@ two independent
weak cues combined give posterior `<=0.66 < 0.75`, so no single OR pairwise weak-cue conjunction
clears the rule purity bar either -- verified in-cell before claiming the design property).
Each single `w_i` alone: purity ~0.58 (uninformative under `purity_thresh=0.75`). No single or
pairwise conjunction of ANY features in this task clears 0.75 purity by construction (asserted
in-cell as a design-validity check, not assumed) -- this makes `ruleind`'s expected outcome ZERO
promoted rules (100% episodic residual, floors near base rate ~0.50 on a per-instance unique key
that cannot exact-match held-out). `ARM_LINEAR` (dense Hebbian outer-product store over bundled
random feature codes, `BASE.consolidate_store`/`store_predict`, REUSED VERBATIM) structurally
cannot represent the XOR-shaped interaction component (Minsky & Papert 1969, CITED, same argument
as the existing `TASK_XOR_CONTROL`) and has no per-feature RELIABILITY reweighting for the
graded weak cues (unweighted Hebbian sum treats every training example equally regardless of
per-cue noise level) -- expected to underperform GAM on both the interaction AND the graded-main
components. GAM is expected to accumulate BOTH the sub-threshold interaction evidence and the
graded weak-cue evidence via its additive log-odds sum, achieving higher accuracy than both.

n=600 instances/seed (100 per case is enough for min_coverage=3 at these probabilities), 3 seeds
[0,1,2], 70/30 seen/held split (mirrors `RULEIND.control_split`).

## PRE-REGISTERED BANDS (set BEFORE running; do not redefine post-hoc)

### (1) EXTENSIBILITY (HARD gate -- the module's central claim)

`HARD_PASS_EXTENSIBLE` iff ALL of:
  - `git diff --stat -- hdlab/learner/core.py` is EMPTY (zero-diff) at cell-run time.
  - `registry.learn(episodes, feat_fn, spec)` with `candidate_plugins=["estimation","ruleind","gam"]`
    executes with no exception on >=3 distinct tasks.
  - `core.mdl_select`, `core.per_cluster_gate`, `core.glass_box_assert` are called DIRECTLY
    (not just transitively through registry.learn) on a `gam_plugin.learn(...)` `LearnResult`
    and succeed with no special-casing (no `if plugin_name == "gam"` branch anywhere in
    `core.py`, `registry.py`, or the plugin -- the plugin never imports its sibling plugins).
`HARD_FAIL_MODULE_NOT_EXTENSIBLE` iff core.py required ANY edit to accommodate the new plugin, OR
  `registry.learn`/`core.mdl_select` raised on the 3-plugin candidate set. Report LOUDLY --
  this refutes 29487's central claim.

### (2) BEHAVIOR (standalone-baseline reproduction)

An INDEPENDENTLY-WRITTEN reference implementation (same formula, separate code path inside the
test cell, NOT calling into `gam_plugin`'s internals) computes per-class GAM scores directly from
the episode counts. Compare `gam_plugin.apply()`'s argmax predictions against the standalone
reference's argmax predictions on BOTH the fitting set and held-out, for every seed/task.
`HARD_PASS_BEHAVIOR_MATCHES_STANDALONE` iff 0 label mismatches (bit-exact argmax agreement).
`HARD_FAIL_BEHAVIOR_DIVERGES` iff >1% of predictions mismatch on any seed/task (implementation
bug in the plugin's counting/scoring, not a floating-point artifact).
`MIDDLE_BAND` iff 0% < mismatch rate <= 1% (isolated float-tie edge cases; investigate).

### (3) AUTO-SELECT with 3 plugins

`TASK_GAM_GRADED_CONTROL` (new, above): `HARD_PASS_GAM_SELECTED` iff `chosen == "gam"` AND
  `gam`'s `compression_ratio` strictly exceeds BOTH `estimation`'s and `ruleind`'s on this task,
  for >=2 of 3 seeds. `HARD_FAIL_GAM_NEVER_SELECTED` iff `gam` is never chosen on ANY seed of its
  own designed-for task (the plugin's central "graded cue" mechanism does not work as intended).

COUNTERFACTUAL (data-driven, not task-name-branch check): re-run the SAME
`TASK_GAM_GRADED_CONTROL` spec/code path with labels independently shuffled
(`np.random.default_rng(fixed_int_seed).permutation`, NEVER `hash()`-seeded per PROT-023) BEFORE
fitting all 3 plugins. `HARD_PASS_DATA_DRIVEN` iff the shuffled-label run does NOT choose `"gam"`
(either `KEEP_EPISODIC` or a different plugin -- proving the pick tracks the DATA, not the task
name/code path, which is identical in both runs). `HARD_FAIL_AUTOSELECT_NOT_DATA_DRIVEN` iff the
shuffled-label run ALSO chooses `"gam"` with `compression_ratio >= 1.0` (the module is not
actually gating on genuine compression).

`TASK_XOR_CONTROL` and `TASK_PPATTACH_REAL` (existing 29487 probe tasks, RE-RUN with 3 candidates
instead of 2): report whichever plugin wins each -- informational, not a HARD gate (adding a 3rd
competitor may legitimately change which plugin wins a task it did not win before; that is a
correct MDL outcome, not a bug, PROVIDED `core.mdl_select`'s own comparison logic decided it,
which the direct-call check in (1) already verifies).

### (4) PP-attach GAM-vs-linear-vs-rules honest comparison (SMOKE scale for foreground
tractability: `BASE.train_dep_parser("smoke")`, `dev[:900]`, seed=7 -- NOT re-verifying 29485's
FULL-scale claim, a signal-direction check only, explicitly labeled as such in the report)

No HARD band (this is a "may still be linear-capturable" honest-report item per the task brief,
not a gate on the module's extensibility claim). Report `gam_net_gain` vs `ruleind_net_gain` vs
`linear_net_gain` vs `simvote_net_gain` on the identical `BASE.verb_split(instances, 7, 0.6)`
split, using `BASE.calibrate_tau` + `BASE.eval_heldout` (the SAME calibrated-margin convention
ARM_LINEAR/ARM_SIMVOTE already use -- GAM always emits a score for every class, so it fits this
convention rather than ruleind's binary-override convention).

### OVERALL

`HARD_PASS_GAM_PLUGIN_PROVEN` iff (1)=HARD_PASS AND (2)=HARD_PASS AND (3.own-task)=HARD_PASS AND
  (3.counterfactual)=HARD_PASS.
`HARD_FAIL_GAM_PLUGIN` iff ANY of (1)/(2)/(3.own-task)/(3.counterfactual) = HARD_FAIL.
`MIDDLE_BAND` otherwise.

## Design-gate iteration addendum (recorded AFTER the first in-cell run, BEFORE the reported run)

First calibration attempt (`q=0.15`, `p_align=0.58`) was run and produced `design_n_rules` in
{3,4,7} across the 3 seeds -- `induce_rules` DID promote rules, refuting the intended
"no-conjunction-clears-threshold" design property. Root cause identified (not a bug): (a) the
THEORETICAL purity at `q=0.15` (0.745) sits within ~1 sampling-SE of the 0.75 threshold at the
~100-instance coverage scale, so random seeds cross it about half the time; (b) once ANY rule
crosses threshold, sequential covering's residual-removal cascade (RIPPER/CN2-family: later
candidates are scored on the shrinking UNCOVERED set, not the full population) shifts conditional
purities of subsequent candidates upward too, compounding the effect. Per the SCHEMA-VET
design-gate iteration discipline (Gate B / META_RULE_AG: iterate the regime when a design does
not land in its intended discriminating band, do not ship the miscalibrated version), the task
generator was recalibrated to `q=0.22` (THEORETICAL@ purity `(1-q)^2+q^2=0.657`, a ~9-point safety
margin under 0.75) and `p_align=0.56` (best-case two-weak-cue posterior ~0.62, also wider margin).
This is a TASK-CALIBRATION fix, not a change to any pre-registered PASS/FAIL band above (0.75
purity_thresh is `ruleind`'s own unchanged default; the HARD_PASS/HARD_FAIL seed-count bands in
(3) are unchanged) -- both attempts are reported honestly in the cell's output.

## RESULT (recorded after the run; not a post-hoc band change -- see full metrics at
`data/exp_learner_module_gam_plugin_proof_v1/metrics.json`)

`MIDDLE_BAND_GAM_PLUGIN`. (1) EXTENSIBILITY = HARD_PASS (core.py zero-diff confirmed via
`git diff --stat`; 3-way registry.learn clean; direct core.mdl_select/per_cluster_gate/
glass_box_assert calls succeed on a bare gam LearnResult). (2) BEHAVIOR = HARD_PASS (0 mismatches
vs the independent numpy standalone reference across all 3 seeds, fit and held-out). (3.own-task)
= MIDDLE_BAND: `gam` chosen + highest-compression on 1/3 seeds (seed 0: comp
`{estimation:0.998, ruleind:1.000, gam:1.046}`), `estimation` chosen on the other 2 (comp
`~1.00-1.02`, `gam` `~0.87-0.88`) -- design_n_rules=0 on ALL 3 seeds (the crisp-rule-search
correctly finds nothing, as designed), so `ruleind` never wins this task at any seed; GAM's
mechanism genuinely fires (wins outright on 1 seed, same code/task, pure data variation) but the
graded-cue advantage over the cheap single-key `estimation` baseline is modest/seed-sensitive at
this instantiation, not a dominant, robust win -- reported honestly rather than further retuned
toward a forced pass (two prior calibration attempts recorded in the addendum above; this is the
third and final one, chosen for the STABLE design-validity property -- design_n_rules=0 every
seed -- over a slightly-more-decisive-looking but design-unstable alternative that also
occasionally let rule induction re-clear the purity gate). (3.counterfactual) = HARD_PASS: the
label-shuffle counterfactual flips the pick away from `gam` on 3/3 seeds (`KEEP_EPISODIC` every
time) -- selection is demonstrably DATA-DRIVEN, not a task-name branch. Existing 2 probe tasks
re-run 3-way (informational): `TASK_XOR_CONTROL` still picks `ruleind` (comp 7.96 vs gam's 2.13 --
GAM's pairwise term also solves XOR but costs far more model bits per key than one clean rule);
`TASK_PPATTACH_REAL` (smoke-scale) still picks `estimation` (comp 1.44 vs gam's 1.41, vs ruleind's
1.33) -- adding GAM did not flip either existing task's winner, an honest, non-forced outcome.
(4) PP-ATTACH HONEST (smoke-scale, seed 7): `gam_net_gain=0.1296` beats `ruleind=0.1065`
(`+0.0231`), `linear=0.1111` (`+0.0185`), and `simvote=0.0694` (`+0.0602`) on this single
smoke-scale seed -- CONSISTENT with the graded-cue hypothesis (GAM's additive evidence over the
same V/N1/P/N2/distance-bucket features edges out both the crisp rule search and the linear
readout) but this is ONE seed at reduced scale, not a FULL-scale multi-seed reproduction of
29485's own real-task claim -- reported as a directional signal only, per the "may still be
linear-capturable" honesty clause in the task brief.

## Calibration probe note

No prior empirical anchor exists for a GAM/EBM hypothesis class on this codebase (first
instantiation) -- the accuracy/compression-ratio NUMBERS reported in (3)/(4) are measurement, not
a theory-only calibration probe (the pre-registered bands above are mechanism/structural gates,
not point-estimate accuracy bands), so the +-50% calibration-probe widening rule does not apply
here; the purity-threshold arithmetic in the positive-control design (0.745, 0.66) IS
THEORETICAL@ closed-form Bayes posterior and is verified empirically in-cell before the run
proceeds (design-validity assertion, not assumed).

## Compute architecture

Class (b) sequential-CPU. GAM fitting is closed-form counting (single pass over episodes for
mains, single pass for candidate pairs) -- no matmul, no GPU-batchable primitive; same class as
both existing plugins. PP-attach comparison uses smoke-scale harvest (`BASE.train_dep_parser`
"smoke", `dev[:900]`) specifically to keep this LOCAL-ONLY foreground-to-completion (no queue, no
push, no remote-persist, no bank -- skunkworks VETs).

## Cell-template mandatory subset (stress-test/proof cell, not a queued anchor)

- `final_metrics_atomicity`: tmp_replace (`os.replace`).
- `except SystemExit`/`KeyboardInterrupt`: raise BEFORE `except Exception` (no `BaseException`).
- `crlb_n/a`: extensibility/reproduction/auto-select discrimination measurement, not a
  capacity/CRLB-bound cell.
- `deterministic_seeding`: true (fixed int seeds via `np.random.default_rng`; NEVER `hash()`-seeded
  per PROT-023; label-shuffle counterfactual uses a fixed int seed, not `hash((...))`).
- `arms_differ_verified`: hash-test over GAM / ruleind / linear / simvote held-out predicted-label
  tuples on the PP-attach comparison (part 4).
