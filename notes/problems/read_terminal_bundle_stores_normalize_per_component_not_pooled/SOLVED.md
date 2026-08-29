---
problem: read_terminal_bundle_stores_normalize_per_component_not_pooled
status: PARTIAL
bar: "PASSES only with ALL of (per read-terminal caller you evaluate -- cover at least the argmax/cleanup family AND one cosine consumer): 1. Switch the caller's read-terminal bundle to a pooled divisive norm, measured on that caller's OWN validated task/gold. 2. Pooled >= per-component CI-separated on that task (recompute the per-component floor on the same population), with the info-free twin LOSING CI-separated; report CI half-width + null p95 -- OR a rigorous NULL (the caller's readout is provably scale/direction-insensitive) that CLOSES that caller. 3. A POSITIVE control the metric can move. 4. One-screen summary: per-caller table + the recommended default per caller. A rigorous NEGATIVE is a FULL PASS."
result: "Per-caller, LIVE recompute on each caller's OWN validated task. TYPER (selection_weighted_sharded_typer, role-typing MET/UNMET, n_test=24): divnorm on the read-terminal sup_map does NOT help -- it HURTS at low load, delta vs per-component floor = -0.0625 [-0.101,-0.024] (n_train=8), -0.0486 [-0.080,-0.017] (16), -0.0312 [-0.056,-0.010] (24), all CI-separated BELOW; neutral at high load (+0.0069 [0.000,+0.017] @40; 0.000 @48). COSINE consumers (lexical_similarity 29-triple tier task): ordered_frac IDENTICAL 0.9655 across per-component / divnorm(dot) / divnorm(ncos) -- a NULL. goal_achievement: bundle holds <= len(ATTRIBUTES)=6 items -> cannot overload -> neutral. register + multibank: already switched (parent, cited)."
floor: "The per-component (S_i/|S_i|) default, recomputed on each caller's own population: TYPER PERCOMP mean_acc 0.8333 (n_train=40, 5 seeds, bit-for-bit faithful to the landed organ); COSINE PERCOMP ordered_frac 0.9655 (29 triples, == the landed n11c number); readout-principle grid per-component argmax/serial recomputed per load."
controls: "INFO-FREE TWINS lose: typer scrambled-label 0.507 vs 0.750; cosine scrambled-feature 0.207-0.310 vs 0.9655. POSITIVE CONTROLS that MOVE the metric: readout-principle grid at m=64 overload, divnorm-minus-percomp = +0.115 argmax / +0.621 gain-matched-serial; cosine graded-discriminability d' 1.02->1.44 at N=128 (divnorm carries the extra dynamic range). FAITHFULNESS GATE: typer PERCOMP == landed 0.8333. ROUND-TRIP CONTROL: unbind-key norm inert under argmax cleanup (per-component ~= divnorm at every load)."
files_changed: "experiments/exp_read_terminal_divnorm_readout_principle_v1.py, experiments/exp_read_terminal_divnorm_cosine_family_v1.py, experiments/exp_read_terminal_divnorm_typer_v1.py, verification/test_read_terminal_divnorm.py, notes/problems/read_terminal_bundle_stores_normalize_per_component_not_pooled/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_read_terminal_divnorm.py"
---

## What this is

The brief asked me to carry the register's pooled-divisive-norm win across "EVERY enumerated read-terminal
`bundling.bundle` caller" -- switching each to `norm="divnorm"` and measuring. I did, on each caller's own
validated task. **The disk refutes the brief's central premise and I then established the correct rule
underneath it.** The measurement bar is fully met (rigorous per-caller verdicts + positive controls + info-free
twins losing); the headline is that **no additional caller should be switched**, and the reason is not
"read-terminal-ness" at all.

## The refutation (disk outranks the brief), then the real rule

**The brief's premise:** "read-terminal (unbind+cleanup, or cosine) vs re-bound is the discriminator; the
per-component default is the wrong choice for the WHOLE consumer set; switch them all." Two parts of that are
wrong on disk:

1. **The map's "I found NO caller that re-binds the bundle as an operand" is factually false.** The typer's
   `_item_role_subbundle` (line 274) is used as the SECOND OPERAND of `binding.bind(sub, outcome)` (line 293)
   AND as the UNBIND KEY of `binding.unbind(sup_map, sub)` (lines 313/332/346/360). It is not read-terminal; it
   is a re-bound key. (It turns out not to matter in practice -- see below -- but the classification the brief
   rests on is wrong.)

2. **Read-terminal-ness is NOT what predicts benefit. READOUT CLASS + LOAD is.** Per-component renorm
   (`S_i/|S_i|`) is a *per-component nonlinearity* that distorts the bundle's DIRECTION; pooled divnorm is a
   *global scalar* of the raw sum that preserves direction. So divnorm `>=` per-component for **every**
   direction-sensitive read, the gap GROWS WITH LOAD, and it is far LARGEST for the gain-matched *iterative
   serial* decode. Measured on one fixed store (`readout_principle` cell), divnorm minus per-component at
   overload m=64: **per-slot argmax +0.115, gain-matched serial +0.621.** At low load (m<=8) there is no gap at
   all. (The argmax +0.11 independently reproduces the parent register's own argmax gain 0.53->0.64 -- a
   corroboration, not a re-derivation.)

So the benefit needs BOTH (a) an overloaded store AND (b) a direction-sensitive readout, ideally the
gain-matched serial decode. **Among the enumerated callers, only `situation_model_accumulate` and
`situation_model_multibank` have both -- and they were already switched by the parent problem.** Every other
enumerated caller fails one condition, MEASURED per caller:

| caller | bundle site | readout | its load | divnorm vs per-component (on its OWN task) | recommended default |
|---|---|---|---|---|---|
| `situation_model_accumulate` (register) | read-terminal | **serial** decode-and-suppress | overloads | **WINS** serial 0.37->0.99, argmax 0.53->0.64 (parent) | **divnorm** (LANDED) |
| `situation_model_multibank` (default) | read-terminal | **serial** per bank | overloads | **WINS** (parent witness) | **divnorm** (LANDED) |
| `selection_weighted_sharded_typer` sup_map | read-terminal | weighted **cross-role argmax combine** | n_train pairs / 2 labels | **HURTS at low load** -0.06/-0.05/-0.03 CI-sep; neutral high | **per-component** (keep) |
| `selection_weighted_sharded_typer` sub-bundle | **re-bound KEY** (not read-terminal) | is an unbind key | mostly singletons | **inert** (round-trip percomp~=divnorm; 59% singletons) | **per-component** (keep) |
| `goal_achievement` utility bundle | read-terminal | argmax cleanup + margin | <= 6 attributes (cannot overload) | **neutral** (no-overload regime) | **per-component** (keep) |
| `lexical_similarity` / `verb_lexical_similarity` | read-terminal | **cosine** (`Re<a,b>/d`) | 2-5 features (coarse tiers) | **NULL** ordered_frac identical 0.9655 | **per-component** (keep) |
| `quality_relation` | (transitive via `concept_similarity`) | cosine | -- | inherits lexical_similarity's null | **per-component** (keep) |

## What I built and measured

Three experiment cells (each `--self-test` green, torch-only, sub-10s, no spaCy) + one scaffold-free witness
(`test_read_terminal_divnorm.py`, 10/10) that LIVE-recomputes every load-bearing claim on the real organs and
the real validated tasks.

- **`exp_read_terminal_divnorm_readout_principle_v1.py`** -- the mechanism. One superposed store, per-component
  vs divnorm x {argmax, serial-plain, serial-pooled}, over a load sweep. Establishes the readout+load rule and
  reproduces the register's argmax+serial gains on a synthetic store (the known-answer positive control).
- **`exp_read_terminal_divnorm_cosine_family_v1.py`** -- the cosine consumers on the exp_n11c 29-triple tier
  task. ordered_frac identical across three arms (per-component == divnorm-dot == divnorm-ncos); info-free twin
  (scrambled features) loses; positive control shows divnorm holds ~1.4x more graded-overlap discriminability
  (d') at large bundle size -- headroom the coarse, low-load task never uses. Also proves the coupling identity:
  under per-component every concept vector has constant norm sqrt(d), so the organ's `Re<a,b>/d` readout IS
  already the exact normalized cosine there.
- **`exp_read_terminal_divnorm_typer_v1.py`** -- the typer on its landed 0.8333 task, with a byte-faithful
  norm-injected subclass (PERCOMP reproduces 0.8333 bit-for-bit, certifying no drift). divnorm on the sup_map
  HURTS at low load (CI-sep), overload sweep, DIVNORM_KEY inert, singleton diagnostic, synthetic key round-trip.

## Why the typer is HURT by divnorm (the brain-foundational reason)

The typer's readout is not a single overloaded register -- it is a weighted **cross-role** combine:
`combined[y] += shard_weight[r] * cleanup_score_r[y]` over roles. divnorm rescales each role's sup_map by a
DIFFERENT pooled scalar (`mean|sup_map_r|`), which silently reweights the roles -- on top of the *explicit*,
LOO-learned `shard_weights_` the organ already computes. That double-counts the per-role gain, and at low
n_train (noisy, unequal per-role item counts) it miscalibrates the combine -> CI-separated harm. Per-component,
which gives every role the same unit-magnitude scale, is the correct default for a readout that does its own
explicit cross-shard weighting. This is a real, general caution: **do not inject an implicit pooled gain into a
readout that already applies an explicit learned gain.**

## KEY REALIZATIONS

1. **The discriminator is the READOUT + LOAD, not read-terminal-vs-rebound.** The brief (and the parent's
   adjacency map) framed it as "read-terminal bundles need divnorm." The measured truth: per-component distorts
   *direction*, so divnorm helps any direction-sensitive read UNDER OVERLOAD, most for the gain-matched serial
   decode. Reframing from "read-terminal?" to "does this readout iterate, and does the store overload?" is what
   made the per-caller verdicts fall out cleanly.
2. **"argmax is scale-invariant, so divnorm is neutral" is WRONG** -- and catching that was the pivot. argmax is
   invariant to a *global scalar* (raw-sum vs divnorm), but per-component is a *per-component* change of
   direction, so divnorm-argmax beats per-component-argmax at overload (+0.13, matching the parent's 0.53->0.64).
3. **The cosine readout's calibration is coupled to per-component:** constant norm sqrt(d) makes `Re<a,b>/d` the
   exact normalized cosine. So per-component is not a defect there -- it is the correct, byte-identical, cheaper
   normalized-cosine op; divnorm would need a true normalized-cosine readout just to break even.
4. **The typer sub-bundle is a re-bound unbind KEY, not a read-terminal bundle** -- the map's "no caller
   re-binds" is false. But the key norm is measured INERT under argmax cleanup, and 59% of the typer's
   sub-bundles are singletons where per-component == divnorm exactly. So the classification error has no
   practical cost -- worth knowing so a future "switch every read-terminal caller" script does not touch it.
5. **A bundle that cannot overload cannot benefit.** goal_achievement's vocabulary is 6 attributes, so its
   bundle sits permanently in the no-gap regime -- a structural (not empirical) neutral.
6. **The positive control had to be redesigned twice.** A monotonic K-ladder showed both norms track overlap
   (rank-preserving), hiding the effect. The real positive control is discriminability UNDER NOISE as bundle
   size grows -- there divnorm's preserved dynamic range shows up (d' 1.4x), and the register's serial overload
   shows the big lever. "Can the metric move?" needed the *right* stressor, not the first one.

## What I did NOT establish / would withdraw first

- I did NOT run goal_achievement on its own end-to-end dataset; I bounded it by its 6-attribute load + the grid.
  If I had to withdraw one claim first, it is the goal_achievement "neutral" -- it is inference-from-load, not a
  full task measurement (though the load bound is structural and hard to escape).
- I did NOT measure the `sign()`-on-a-bundle sibling family (`grounding_acquisition_loop`, `situation_focus`,
  `role_slot_summarizer`, `event_bundle`). Those are bipolar/BSC (a different code), not FHRR `bundling.bundle`,
  so the `norm="divnorm"` option does not even apply to them. The SAME readout+load principle should govern
  them (measure at each sign-caller's readout+load), but that is a separate build -- flagged, not claimed.
- I did NOT deeply profile `script_grain_acquisition_loop` (iterative_attractor + cosine). Its readout is the
  one non-argmax, non-plain-cosine case (a Hopfield attractor), so it is the single caller that COULD behave
  like the serial decode IF it overloads -- but it bundles few traces per grain. Flagged as the one caller
  worth a targeted follow-on measurement.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, the register-norm entry / general rule)

The §2b general rule as written ("a read-terminal bundle must be normalized by pooled divisive norm, never
per-component") is **too broad and mis-attributed**. Corrected, measured rule:

> Per-component renorm distorts a bundle's DIRECTION; pooled divisive norm preserves it. So divnorm `>=`
> per-component for any DIRECTION-SENSITIVE read, the gap grows with STORE LOAD, and is LARGEST for the
> gain-matched ITERATIVE serial decode (register: serial 0.37->0.99), MODEST for per-slot argmax (0.53->0.64),
> and UNUSED by a low-load / coarse-margin task (cosine consumers: null). The discriminator is readout-class +
> load, NOT read-terminal-vs-rebound. Two measured cautions: (i) the enumerated adjacency map's "no caller
> re-binds" is wrong -- `selection_weighted_sharded_typer`'s sub-bundle is a re-bound unbind key; (ii) injecting
> divnorm into a readout that already applies an EXPLICIT learned per-shard gain (the typer's cross-role combine)
> HURTS (CI-separated at low load) by double-counting the gain. Recommended defaults: divnorm for
> register+multibank (landed); per-component everywhere else enumerated.

Brain-fidelity label unchanged from the parent: pooled divisive normalization is DIRECTLY CONFIRMED in
sensory/decision cortex (Carandini & Heeger 2012; Louie & Glimcher) and is an OUR-EXTENSION-UNDER-TEST for a
memory register; the NEGATIVE ("don't renormalize per-component") is the well-grounded half. This problem adds:
its benefit is gated on load + readout, so it is not a substrate-wide default -- it is an overload-store,
serial-readout op.

## Proposed hdlab change (strategy lands it, Q111)

**None required, and that is the result.** The two callers that benefit (register, multibank) are already on
`norm="divnorm"`. Do NOT switch the typer (measured harm at low load), goal_achievement (cannot overload), or
the cosine consumers (null; per-component is their exact normalized cosine). Optional, low-value: a one-line
comment at each of those `bundling.bundle` call sites noting "read-terminal but argmax/cosine at low load ->
per-component is correct here (see this problem)" so a future substrate-wide sweep does not blindly flip them.

## TLDR (plain language)

A recent fix made one memory organ far more reliable by changing how it re-scales a stack of stored facts
before reading them back. The question here was: should every other organ that stacks-and-reads facts get the
same change? I measured each one on its own real task. **The answer is no -- none of the others should change.**
The fix only helps when an organ is (1) overloaded with many stacked facts AND (2) reads them back by a
step-by-step "peel-off" method. Only the two memory-register organs do both, and they were already changed. One
organ (the role-typer) is actually made *worse* by the change at normal data sizes, because it already does its
own careful weighting and the change double-counts it. The word-similarity organs are unaffected (their read is
already the right kind of scaling). So the broad "change them all" idea is wrong; the precise rule is "change it
only for an overloaded, peel-off-read store," which is already done.

## QUESTIONS

None.

## NEXT STEPS

1. (strategy) Re-verify `verification/test_read_terminal_divnorm.py` (10/10) and fold the AUDIT UPDATE into
   `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (correct the §2b general rule from "read-terminal -> divnorm" to
   "overloaded store + iterative/direction-sensitive readout -> divnorm").
2. (candidate follow-on, LOW priority) The `sign()`-on-a-bundle bipolar family -- `norm="divnorm"` does not
   apply (different code); a graded/pooled read is the analog, and the readout+load principle should be measured
   there. This is the map's follow-on #2, now with the corrected rule to test against.
3. (candidate follow-on, LOW priority) `script_grain_acquisition_loop`'s iterative_attractor -- the one
   non-argmax, non-plain-cosine readout; worth a targeted measurement IF its trace bundles ever overload.
4. (no action) Register + multibank remain on divnorm; nothing else switches.
