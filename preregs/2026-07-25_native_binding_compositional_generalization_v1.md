# Pre-reg: native_binding_compositional_generalization_v1

- **Date:** 2026-07-25
- **Cell:** `experiments/exp_native_binding_compositional_generalization_v1.py`
- **Design of record:** `notes/research_native_binding_compositional_generalization_2026-07-25.md` (Sections 3a/3b, arms 1-5, SHAPE/PLACE/METRIC) + 2 Director additions.
- **Trigger:** atom 29556 (flat item+relation->property MLP hub) VET-confirmed structural systematicity failure (ho_lift 0.0). Separate the BINDING bottleneck from the MEANING bottleneck.
- **Contract:** INLINE-LOCAL foreground-to-completion (GloVe/WordNet git-ignored, not remote-portable; ~3-4 min); NO push/remote-persist; ASCII-only; deterministic; repo `.venv`; agent-reported VET-PENDING (skunkworks owns VET).

## One variable
The COMBINATION MECHANISM only. Item meaning representation (frozen `SemanticHDEncoder.fused`, 300d, identical to 29544/45/46/29556), property targets, domains/relations, and eval question are held byte-identical across arms.

## Corrected held-out split (Section 3a; the load-bearing fix, built + unit-checked FIRST)
Held pool = ONLY the four category-correlated relations (`energy:byproduct`, `metal:source`, `planet:moons`, `animal:body`), and ONLY items whose value is SHARED with >=1 kept same-value in-train item (value groups of size s hold out `s//2`, keeping `ceil(s/2)>=1`; size-1/unique-value groups NEVER held -> cleanly excludes the note's `mars:moons=two`). Coverage guards (literal Fodor-Pylyshyn): held item still appears under other relations in train; held relation still appears with other items in train. Self-test asserts held relations are category-correlated-only and never leak into train.

## Metric (DELIBERATE, DOCUMENTED deviation from the note -- author catch, reported not silent)
PROPERTY-VALUE recovery, NOT 29556 concept-recovery. Concept-recovery (argmax over the 6 concepts) is mathematically ILL-POSED for category-correlated relations because the target value is SHARED across a category (a perfect systematic model maps all 4 renewables to "clean" -> the concepts tie -> argmax scores ~0 for a perfect model). Property-value recovery = argmax cosine over the (domain,relation) distinct property-VALUE meaning vectors (e.g. `{clean, smoke, radiation}`); correct iff argmax value == the item's true value. Applied IDENTICALLY to all arms. Chance = mean 1/|value-set|.

## Arms (all on the SAME corrected split + metric)
1. FROZEN (no learning; shared baseline; GloVe MEANING-CONTROL, not an adopted encoder -- Director addition i)
2. FLAT-MLP (29556 hub; concat + tanh hidden32) -- baseline to beat
3. NATIVE-BINDING (fixed role_HV + fixed `hdlab.binding.bind` HRR circular-conv + SINGLE linear readout M) -- GATING arm
4. SHUFFLED-LABEL control for arm 3 (train permuted, eval TRUE)
5. BROKEN-BINDING (concat + SAME single linear readout) -- binding-necessity ablation
6. BIND-then-MLP (fixed bind + small MLP readout) -- completes the {bind,concat} x {linear,MLP} 2x2
3n. NATIVE-ENCODER (Director addition ii; DIAGNOSTIC, non-gating): item = REAL `hdlab.concept_encoder.ConceptEncoder` HD + same fixed bind + linear M. CONSTRUCTION-SENSITIVE (category structure designer-imposed via a synthetic non-leaky corpus; shares GloVe frozen baseline).

## Pre-registered bands (a priori; gate on arm 3; NO tuning to force a win)
- **HARD_PASS** = `bind_ho_lift >= 0.25` AND real-vs-shuffled sep `>= 0.15` AND shuffled stays flat AND flat-MLP `ho_lift < 0.10` AND `bind_over_concat >= 0.10` (binding is the unique lever).
- **MIDDLE** = `bind_ho_lift in [0.10, 0.25)` with controls holding; OR `bind_over_concat < 0.10` (systematicity from linear readout/format, not binding); OR flat-MLP ALSO `>= 0.10` (29556's 0.0 was a split/metric artifact).
- **HARD_FAIL** = `bind_ho_lift < 0.10` (sub-diagnose: role near-orth + frozen-not-saturated guards first).
- **INVALID** = shuffled matches/exceeds real (leak); OR role max pairwise cos `>= 0.50`; OR frozen held `>= 0.85` (vacuous).
- **Base-rate correction (principled, a-priori-consistent):** category-correlated value sets are imbalanced, so the shuffled-LABEL control is a per-relation MAJORITY-CLASS guesser -- it legitimately rises above chance. The real systematicity control is `shuffle_sep = bind_ho - shuf_ho` (lift BEYOND base-rate), gated at 0.15; `shuffled_flat` is a reported diagnostic only. This makes the control STRICTER, not looser.

## Interpretation frame (separates bottlenecks)
HARD_PASS on arm 3 => binding IS the systematicity fix; remaining gap = meaning (attack earned encoder next). arm 3n => is the fully-native stack there yet. HARD_FAIL => binding alone insufficient (re-implicates the frozen-meaning wall; Lake-MLC training-regime is the next lever).

## MEASURED result (this cell; full run)
- verdict = **MIDDLE**. `MEASURED@data/exp_native_binding_compositional_generalization_v1/metrics.json`.
- 2x2 ho_lift over frozen (max exposure): bind+linear 0.2222, concat+linear 0.2222, bind+MLP 0.0, concat+MLP(flat-MLP) 0.0 -> lever is READOUT-LINEARITY, not the bind-vs-concat format (`bind_over_concat=0.0`).
- Systematicity beyond base-rate `shuffle_sep=0.1111 < 0.15` (shuffled base-rate reaches 0.6667); frozen 0.5556 (chance 0.4259); role max cos 0.19/0.06.
- arm 3n native-encoder held 0.8889 (ho_lift vs frozen-GloVe 0.3333), within/cross-cat cos 0.70/0.03 -- CONSTRUCTION-DETERMINED (synthetic category structure); higher than GloVe arm 3 because planted structure is cleaner than GloVe's conflated meaning. NOT evidence the unsupervised encoder discovers structure.

## Compute / schema
- `compute_architecture`: sequential-CPU justified (tiny scale, wall ~3-4 min; reuses substrate bind primitive; bind features fixed -> precomputed once per arm, only readout iterates).
- `final_metrics_atomicity`: tmp_replace. `crlb_n/a`: argmax over small value contrast set, no continuous-noise CRLB. `storage`: no_composition (single-hop item x relation bind). `deterministic_seeding`: fixed int seeds + numpy default_rng + sorted; no builtin-hash. `arms_differ_verified`: true. `discriminator_fires`: bind_ho > frozen at smoke (verified). `baseline_in_band`: frozen 0.5556 in (chance, 0.85).
