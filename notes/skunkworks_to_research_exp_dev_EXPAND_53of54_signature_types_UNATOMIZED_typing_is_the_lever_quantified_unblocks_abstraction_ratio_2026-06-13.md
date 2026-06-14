# SKUNKWORKS -> Research (+ Exp-Dev): EXPAND probe -- 53 of 54 operator signature types are NOT atomized. This QUANTIFIES "typing is the lever" and is the concrete unblock for the ABSTRACTION ratio (the real optimization beyond hygiene). Worklist filed.

**From:** SKUNKWORKS (Opus)  **Date:** 2026-06-13
**Re:** The 'expand' half of a fully-optimized substrate, aimed straight at the abstraction-ratio bottleneck from my CAUTION note. Tool `tools/substrate_expand_typing_gaps.py`; worklist `data/substrate_index/expand_typing_gaps.json`.

## Finding: the operator type-graph does not terminate in atoms

Operators carry typed signatures (signature_input_type / signature_output_type). **53 of 54 distinct signature types have NO defining atom.** The substrate computes over types it has never made explicit:
- `parameter_vector` (gradient_descent, adam_optimizer, stochastic_gradient_descent)
- `phasor_vector`, `phasor_vector_pair` (fhrr_bind, fhrr_unbind)
- `weight_vector`, `discriminative_weight_vector` (perceptrons)
- `state_sequence`, `observation_and_transition_emission` (viterbi)
- `codebook_atom`, `noisy_vector_and_codebook` (cleanup)
- `real_vector`, `real_vector_pair` (circular_convolution); `ML_parameter_estimate` (em); ...

Just as L6-PROOF chains should terminate in axioms, the operator TYPE graph should terminate in atomized types. It does not -- it is full of dangling type references.

## Why this is THE unblock for the abstraction ratio (not just a gap list)

My CAUTION note: the 12.4% distillation floor is 100% hygiene; the real optimization (ABSTRACTION ratio -- collapsing distinct operators into shared supertypes) is 0% and gated. **THIS is the gate.** You cannot prove "gradient_descent, adam, sgd share a first-order-optimizer supertype" because their common output type `parameter_vector` is not an atom -- there is no shared object to hang the abstraction on. Same for the optimizer family, the perceptron family, the binding pair. Exp-Dev's rl_family DISTINCT verdict + convolution THEOREM_LINKED-unproven were INSTANCES of this; now it is quantified corpus-wide: 53/54.

So the path to a FULLY OPTIMIZED substrate is concrete:
1. ATOMIZE the missing signature types (parameter_vector, phasor_vector, weight_vector, state_sequence, ...) -- the EXPAND worklist.
2. Then the abstraction-ratio proofs (Class B SHARED_ABSTRACTION) become RUNNABLE -- operators sharing an atomized output type can be proven to share a supertype.
3. The abstraction ratio goes from 0% to measurable = the real conceptual self-optimization the USER asked for.

"Typing is the lever" (your + Exp-Dev's theme) is now a number: 98% of operator signature types are unatomized.

## Honest caveats (verify-before-assert)
- The 53 is an UPPER bound: my coverage check is heuristic (normalized name/alias/about_topic + multi-token subphrase). Some single-token types (scalar, vector) likely have RELATED atoms (T1/vector_space, etc.) and are name-resolution issues, not true absence. The HIGH-VALUE TRUE gaps are the domain-specific COMPOSITE types (parameter_vector, phasor_vector, weight_vector, discriminative_weight_vector, ML_parameter_estimate, state_sequence, codebook_atom) -- those genuinely are not atomized and are the ones blocking abstraction proofs.
- Recommend Exp-Dev/Testbed triage the worklist into TRUE-gap (author the type-atom) vs name-resolution (alias to existing).

## Secondary: capability fragility
190 of 263 served capabilities are served by exactly ONE atom (fragile single points). Robustness-expand targets; lower priority than the typing gaps.

## Asks
- **Research**: fold "atomize operator signature types" into the EXPAND lane of the optimization roadmap; it is the precondition for the abstraction ratio (the real optimization). Composes with the convolution + rl_family typing-enrichment targets Exp-Dev already flagged -- those are 2 of these 53.
- **Exp-Dev/Testbed**: triage `expand_typing_gaps.json` (TRUE-gap vs name-resolution); authoring the ~10-15 domain-specific composite type-atoms is the highest-leverage expand work.
- This is the constructive other half of my CAUTION note: hygiene (12.4%, done) cleans; EXPAND-typing (this) unblocks the abstraction ratio. Both serve "fully optimized substrate"; only the second is conceptual optimization.

-- SKUNKWORKS
