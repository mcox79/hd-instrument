# Adjacent-component brain-fidelity + optimization map (owner: "evaluate adjacent components for brain foundation and optimization potential")

**From the solver on `the_register_bundle_renorm_breaks_the_serial_readout`.** This is a MAP for strategy's
problem-filing, not a build (solver scope: I do not write hdlab/). Each row: component, how it normalizes a bundle,
how the bundle is CONSUMED (the discriminator), brain-fidelity verdict, on-disk evidence, optimization leverage.

## The unifying principle this problem surfaced

The register result is one instance of a GENERAL substrate rule:

> **A bundle that is READ (unbind+cleanup, or cosine-compared) — not RE-BOUND as an operand — must be normalized by a
> POOLED / SCALAR divisive gain (Carandini-Heeger 2012), never by a PER-COMPONENT nonlinearity.** Per-component
> nonlinearities (`S_i/|S_i|` renorm; `sign(S_i)`) discard the graded/linear structure that both the serial readout AND
> graded cleanup need. Pooled divisive normalization preserves it. (Per-component renorm's ONLY correct use is
> torus-closure for an atom that will be RE-BOUND.)

**Brain-fidelity labeling (refined by research drill A, 2026-08-28):** pooled divisive normalization is DIRECTLY
CONFIRMED in sensory + decision/value cortex (Carandini & Heeger 2012; Louie & Glimcher 2011/2017 LIP/OFC). Its
application to a hippocampal/WM *memory register* is a STRUCTURALLY-MOTIVATED EXTENSION BY ANALOGY (not a recorded
hippocampal circuit) — label it OUR-EXTENSION-UNDER-TEST, not PINNED. The NEGATIVE half is stronger: per-component
instantaneous magnitude-erasure has NO fast biological analogue (Turrigiano scaling is slow/weight-level/structure-
preserving; photoreceptor adaptation is history-based/structure-preserving). So "don't renormalize per-component" is
well-grounded; "use pooled divisive normalization instead" is the faithful analogy, labeled as such.

## The blast radius: `bundling.bundle` callers (grep-enumerated, hdlab/), classified by CONSUMPTION

`hdlab/bundling.py::bundle` defaults to PER-COMPONENT renorm (`S_i/|S_i|`). Enumerated callers:

| component | bundle -> consumed by | re-bound or READ-terminal? | inherits the per-component sub-optimality? | on-disk evidence |
|---|---|---|---|---|
| `situation_model_accumulate` (register) | unbind + `cleanup_argmax` / serial | **READ-terminal** | **YES — MEASURED** (this problem) | witness N1-N4: serial 0.325->1.000; argmax 0.512->0.644 |
| `situation_model_multibank` (DEFAULT backend) | per-bank unbind + `cleanup_argmax` / serial | **READ-terminal** | **YES — MEASURED (witness N8)** | multibank.py:114,145 `bundling.bundle`; compose M=384/8banks: serial 0.733->1.000, argmax 0.654->0.765 |
| `selection_weighted_sharded_typer` | `cleanup_argmax` (unbind-then-score) | **READ-terminal** | **LIKELY — measurement pending** | typer.py:52-54 docstring: ".cleanup_argmax FHRR unbind-then-score"; validated 0.8333 |
| `script_grain_acquisition_loop` | `iterative_attractor` + cosine (`_cos`) | **READ-terminal** | **LIKELY — measurement pending** | loop.py:170 bundle; :187 "cosine-based CA3/DG matching"; :105 iterative_attractor |
| `goal_achievement` | unbind + argmax-with-margin cleanup + FHRR cosine | **READ-terminal** | **LIKELY — measurement pending** | goal_achievement.py:492 "unbind + argmax-with-margin cleanup"; :849 weighted bundle |
| `lexical_similarity` / `verb_lexical_similarity` | graded **cosine** (ATL-hub analog) | **READ-terminal (cosine)** | **DISTINCT readout — measurement pending** | lexsim.py:10-13 bundle-into-concept -> cosine (Lambon Ralph 2024 ATL) |
| `quality_relation` | `concept_similarity` (cosine, built on bundle) | **READ-terminal (cosine)** | **DISTINCT readout — measurement pending** | quality_relation.py:50 "concept_similarity built on bundle" |

**Reading:** every enumerated caller is READ-terminal; I found NO caller that re-binds the bundle as an operand (the
one case where per-component renorm is correct). So the per-component renorm default in `bundling.bundle` is
sub-optimal for its entire measured consumer set. **My own witness N3 is the general evidence for the cleanup_argmax
family:** `argmax:divnorm >= argmax:percomp` at EVERY load (scale-invariance makes divisive == raw-sum argmax, which the
prior `the_core_binding_operator_may_not_be_brain_faithful` showed beats per-component 32/32). The cosine-readout
consumers (`lexical_similarity`, `quality_relation`) are a DISTINCT question (cosine of a per-component-renormed bundle
vs a pooled-normed one) and need their own measurement — flagged, not claimed.

## The sibling family: `sign()`-on-a-bundle (the SAME wrong-op, already audit-flagged)

`sign(Σ ±1)` is the bipolar/MAP-VSA analogue of per-component renorm — another per-component nonlinearity that discards
the graded structure. The audit already flags these with the pooled-divisive-norm verdict AND partial measurements:
- `grounding_acquisition_loop` — audit line ~1176: "WRONG-OP: `sign(Σ±1)` where the brain does pooled divisive
  normalisation; amplifies a noise dim to full weight ~1 in 7."
- `situation_focus`, `role_slot_summarizer`, `event_bundle` — audit lines ~1009/1023: `sign()`-on-a-bundle sites;
  "GRADED beats SIGN by a CI-separated, GROWING margin" (line ~1001); the brain-faithful family is "graded / divisive-
  norm at read-out."

**My contribution to this family:** the register result supplies the MECHANISM (pooled divisive normalization) and a
proven, parameter-flat fix for the FHRR-magnitude arm. The `sign()` arm and the per-component-renorm arm are the SAME
fidelity gap in two code formats; a single "pooled divisive normalization at read-terminal bundles" principle covers both.

## Candidate follow-on problems, ranked by leverage (for strategy to file)

1. **`read_terminal_bundles_use_per_component_norm` (HIGH leverage, broad).** Audit every `bundling.bundle` caller;
   classify re-bound vs read-terminal (this note is the starting map); switch read-terminal ones to `norm="divnorm"`.
   First deliverable per the strategy protocol = a number showing the DEFECT costs each organ something (measure
   per-component vs pooled on THAT organ's own task + floor + twin). My register measurement + the sign-family
   measurements are the existence proof that the cost is real; the open question is per-organ magnitude.
2. **`sign_bundles_should_be_pooled_divisive_norm` (MEDIUM-HIGH, partly measured).** The `sign()` sibling family. Already
   has direction-of-effect measured (graded>sign). The unification with the divisive-norm mechanism (this problem) makes
   it a clean, mechanism-backed fix rather than an empirical tweak.
3. **`cosine_readout_bundles_under_per_component_norm` (MEDIUM, distinct readout).** `lexical_similarity` /
   `quality_relation` / verb-sim read bundles by COSINE, not unbind-decode. Per-component renorm distorts cosine
   differently than binding recovery; whether pooled divisive norm helps the ATL-hub similarity is UNMEASURED. Worth a
   focused probe because these organs gate real comprehension links.
4. **The M>=96 register capacity bound = the sparse-store lever (p2), already owned.** Not a new problem; the norm fix is
   a PREREQUISITE for the p2 sparse store to be serial-readable (they compose, parent measured 12-16x). Cross-reference,
   don't re-file.

## What I did NOT do (scope + honesty)

- I did NOT measure the per-component cost on organs 3-7 above — that is each follow-on's first deliverable. I classified
  their READOUT (from their own docstrings) and inferred inheritance from the SHARED cleanup_argmax/cosine readout; the
  register is the only one measured here.
- I did NOT read every `sign()` file (15 files); I relied on the audit's existing flags + measurements for that family
  and cross-referenced them. A full sign()-caller classification is part of follow-on #2.
