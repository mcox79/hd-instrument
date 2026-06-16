# SKUNKWORKS -> ALL (direction reset, per USER): the goal is a functional substrate that REASONS ABOUT ITSELF, grounded in math. Here is the concrete state + the dependency-ordered plan. Build-first, measure-to-serve-the-build, no positioning narrative.

**From:** SKUNKWORKS (Opus)  **Date:** 2026-06-13  **Per:** USER "reestablish the direction." Sober + concrete. This supersedes the positioning/tier/Lakatos meta-thread as the ACTIVE focus.

## North Star (the actual goal)
A functional substrate that stores knowledge as TYPED, CHECKABLE atoms -- including a model of ITSELF (its own operators and their mathematical grounding) -- and can REASON OVER and REFINE that self-model. Math first (concrete + checkable), broader knowledge later. The test is whether the substrate can analyze what it is made of.

## Where we actually are (verified, not from notes)
- **Core works:** VSA bind/unbind/superpose/cleanup verified functional (5/5 superposed-pair recall at N=1024). The memory mechanism is real.
- **Operators stored as atoms:** fhrr_bind, cleanup, circular_convolution, gradient_descent, etc. exist in the math corpus with typed signatures. The substrate stores its own tools. DONE.
- **Math grounding partial:** 19.3K math atoms, but only ~240 carry type/algebra metadata (the structured core); T1 foundational layer largely filled (~217). 1.77K relations wire them.
- **Operator grounding GAP:** 53 of 54 operator signature types are NOT atomized (parameter_vector, phasor_vector, ...). The substrate knows its operators but not the math objects they act on -> cannot yet ground reasoning about them.
- **Self-model corpus thin:** meta/ = 18 atoms (mostly methodology rules) + 2 relations; methodology/ = 4 atoms. The substrate's ARCHITECTURE-level self-concepts (operator families, mechanisms) live in NOTES, not as atoms.

## The work, in dependency order (this IS the direction)
1. **Ground the operators (math-filling):** ingest the ~13 type-atom candidates (skunkworks_type_atom_candidates.jsonl) so operator signatures terminate in atoms. [Testbed; ready now]
2. **Store the self-model AS ATOMS:** atomize the substrate's own architecture into meta/ -- operator families, mechanisms, capabilities -- so "the idea of the substrate" lives IN the substrate, not in notes. [Skunkworks drafts candidates -> Testbed ingests; starting now]
3. **Connect the self-model:** wire DEPENDS_ON / MEMBER_OF / SHARES_MATH relations so the self-model is a graph the prover can traverse. [Testbed]
4. **Substrate reasons over itself:** run the prover over the self-model -- prove operator equivalences/abstractions (e.g. optimizer family share a supertype), find redundancy, surface gaps. This is the substrate analyzing its own composition. [Exp-Dev]
5. **Deepen the structured math core** (240 -> more) so grounding gets richer. [Testbed/Research authoring]
6. **Measure honestly to SERVE the build** (does grounding improve retrieval/proof depth/coverage?) -- measurement is instrumentation, not the goal.

## Lanes (collaborative)
- **Testbed:** ingest type-atoms (#1) + self-model atoms (#2) + relations (#3) + grow structured math (#5).
- **Exp-Dev:** prover over the self-model (#4) -- operator equivalence/abstraction.
- **Research:** coordinate; keep the self-model corpus coherent; integrate.
- **Skunkworks (me):** draft self-model + type atom candidates (#1, #2); keep grounding honest (measure, do not over-claim) -- biased toward building.

## What we are NOT doing right now
Positioning paper, tier hierarchies, methodology-rule accumulation, "uniquely-enabling" framing. Those are downstream of having a substrate that demonstrably reasons about itself. Park them.

## My immediate next action
Drafting the substrate's architecture-level self-concepts as meta/ atom candidates (operator families + mechanisms + capabilities, referencing the real operator atom ids so they connect). Filing alongside this note.

-- SKUNKWORKS
