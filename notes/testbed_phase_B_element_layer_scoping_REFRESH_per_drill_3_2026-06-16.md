# TESTBED (Integrator) -> Research + Skunkworks + Exp-Dev: DECISION 158c TASK 4 deliverable -- Element-layer scoping memo REFRESH per Drill 3 specified-by-construction findings. Refreshes original a215e5ed memo with 3-question gate + 3-line definition + per-candidate thesis-preservation verdict. Substrate state UNCHANGED; standing-HELD per Phase C TIER-3 architecture decision USER lane.

**From:** TESTBED (Integrator)  **Date:** 2026-06-16  **Tag:** phase_B_element_layer_scoping_REFRESH_per_drill_3_specified_by_construction

## What this refresh adds to a215e5ed

The original scoping memo (commit `a215e5ed`, 2026-06-15) identified Option I (per-atom `elements` field) as the minimum-viable element-layer extension path. Drill 3 (notes/research_DEEP_DRILL_element_layer_thesis_preservation_20260616.md) sharpened the discipline: **element-layer extension is CONDITIONALLY thesis-preserving** — depends on whether the mechanism is *specified-by-construction* vs *learned-against-external-loss*.

This refresh imports Drill 3's 3-question gate + per-candidate verdict into the scoping discipline.

## 3-line definition (Drill 3 substrate-on-its-own invariant)

```
LINE 1 (no-label):       Mechanism requires NO external (input, target) labeled pair.
LINE 2 (no-external-loss): Mechanism requires NO objective defined over external truth.
LINE 3 (auditable):      Substrate can audit the mechanism end-to-end; every parameter from
                          closed-form spec, RNG seed, or substrate-resident algebra.
```

Any element-layer mechanism must PASS all 3 lines to remain substrate-on-its-own.

## 3-question pre-pass gate (Drill 3 protocol)

Before adopting any element-layer extension, run this gate:

```
Q1: Does the mechanism require any external labeled (input, target) pair to be specified,
    fit, or tuned? If YES -> REJECT.
Q2: Does the mechanism require an objective function defined over external truth (held-out
    accuracy, oracle correctness, human preference)? If YES -> REJECT.
Q3: Can the substrate itself audit the mechanism end-to-end (every parameter derived from a
    closed-form spec, RNG seed, or substrate-resident algebra)? If NO -> REJECT.

Only candidates passing all 3 Qs are eligible for the element-layer extension.
```

## Per-candidate thesis-preservation verdict (Drill 3)

```
                                   | Ext data? | Ext loss? | Auditable? | Verdict
Plate i.i.d. Gaussian              |    No     |    No     |    Yes     | PRESERVES
Kanerva bipolar                    |    No     |    No     |    Yes     | PRESERVES
FHRR unit phasors                  |    No     |    No     |    Yes     | PRESERVES
Sparse-block one-hot-per-block     |    No     |    No     |    Yes     | PRESERVES
GHRR block-diagonal (Alam 2024)    |    No     |    No     |    Yes     | PRESERVES
Residue / fractional-power         |    No     |    No     |    Yes     | PRESERVES (Frady-Sommer 2018; Kymn 2023)
NEF decoders (Eliasmith)           |    Yes    |    Yes    |  Partial   | VIOLATES
Reservoir w/ trained readout       |    Yes    |    Yes    |  Partial   | VIOLATES
LLM-as-element-source              |    Yes    |    Yes    |    No      | VIOLATES (per 11th rule)
Modern-Hopfield over codebook      |    No     |    No     |    Yes     | PRESERVES (Ramsauer 2020 when X = substrate codebook)
```

## 3 strongest substrate-internal candidates per Drill 3 (in order of expressivity gain)

```
CANDIDATE 1: Residue / fractional-power encoding
  Expressivity gain: continuous-magnitude + cardinality reasoning UNREACHABLE by pure binder algebra
  Composes with: Phase B cardinality target (CAP_cardinality_recall + CAP_quantifier_*)
  Spec: Frady-Sommer 2018; Kymn et al. 2023; residue arithmetic 2025
  Phase B fit: STRONG (directly serves cardinality)

CANDIDATE 2: GHRR block-diagonal binding (Alam et al. 2024)
  Expressivity gain: strictly larger algebra than FHRR (diagonal -> block-diagonal)
  Composes with: existing binders family (T2_FAM/binders)
  Spec: GHRR 2024 paper
  Phase B fit: MEDIUM (binder-algebra extension; tier-3 step)

CANDIDATE 3: Modern-Hopfield as substrate operator (Ramsauer 2020)
  Expressivity gain: continuous-magnitude soft-subset primitive over substrate codebook
  Composes with: existing AGS-classic-Hopfield (math::T2/amit_gutfreund_sompolinsky_capacity)
                 + per_binding_shard_cleanup (math::T3; ratified db9b3877)
                 + hopfield_pattern_deletion (math::T3; ratified db9b3877)
  Spec: Ramsauer 2020 "Hopfield Networks Is All You Need" - softmax-attention update
  Phase B fit: STRONG (composes with deletion discipline; continuous-magnitude extension)
  Note: math::T2/modern_hopfield_ramsauer already EXISTS in substrate (verified during
        PROMOTION #3 grounding pre-check; Exp-Dev's 168th regime catch confirmed AGS-classic
        was the RIGHT regime for the deletion cell, but modern_hopfield_ramsauer is the
        substrate atom for THIS extension path)
```

## Three rejected candidates (failed Drill 3 gate)

```
NEF decoders: fits decoders by regression vs target function -> VIOLATES Q1+Q2
Reservoir + trained readout: trains readout against external loss -> VIOLATES Q1+Q2
LLM-as-element-source: external learned truth -> VIOLATES Q1+Q2 + lap3_rotate scope class
```

## Refreshed 3-phase path (Option I with specified-by-construction filter)

```
PHASE 1 (Testbed; 30-60 min; reversible backward-compatible):
  Add `elements: list[ElementSpec] | None = None` to Atom dataclass (default None)
  ADD 3-question gate as REQUIRED METADATA on any atom using the elements field:
    elements_thesis_check: {
      no_external_label: bool,    # Q1 result
      no_external_loss: bool,      # Q2 result
      substrate_auditable: bool,   # Q3 result
      preserves_thesis: bool       # AND of Q1, Q2, Q3
    }
  If preserves_thesis == False: atom MUST be in concept-corpus only (NOT math); flag as
    LLM-HYBRID per 11th rule (analogous to PP-217 LLM-hybrid relabel pattern).

PHASE 2 (Skunkworks; 2-4 hrs; textbook-grounded authoring):
  Author element-sets for ~5-10 atoms in the PRESERVES family ONLY:
    - Plate i.i.d. Gaussian (T2 binders family)
    - Kanerva bipolar (T2 binders family)
    - FHRR unit phasors (T2 fhrr_bind family)
    - GHRR block-diagonal (T2 binders extension; NEW operator candidate)
    - Residue / fractional-power (T2 binders extension; NEW operator candidate;
      directly serves Phase B cardinality target)
  Each element-set INCLUDES the 3-question gate verification.
  DEFERRED: NEF decoders + reservoir variants + LLM-element-source (3 rejected per gate).

PHASE 3 (Exp-Dev; 1-2 hrs; carrier-extension utility metric):
  Re-run CONSTRUCT-2 R2 carrier-extension probe with element-set data available.
  Phase B Cluster A (cardinality) directly tests residue/fractional-power utility.

PHASE 4 (DEFERRED; USER architectural decision):
  Symbolic infinite carriers (NOT in Phase B scope; held-HELD per a215e5ed precedent)
```

## What changes from a215e5ed

```
ADDED:
  - 3-question gate as REQUIRED METADATA on any elements-field-using atom
  - Per-candidate thesis-preservation verdict (7 paths classified)
  - 3 PRESERVES candidates ranked by Phase B fit (residue > modern-Hopfield > GHRR)
  - 3 REJECTED candidates (NEF / reservoir-trained / LLM-element-source)
  - Direct composition with Phase B Cluster A cardinality target (residue path)
  - Direct composition with existing AGS-classic-Hopfield + per_binding_shard_cleanup +
    hopfield_pattern_deletion atoms (modern-Hopfield path; ratified db9b3877)
  - Tightened invariant: "no learned oracle, no external sensorium, all parameters
    substrate-derived" per Drill 3 Angle 6 recommendation

UNCHANGED:
  - Option I per-atom `elements` field schema (lowest risk; backward-compatible)
  - 4-phase incremental rollout (3 active + 1 deferred)
  - NO architectural commitment (USER lane gating)
  - 0 substrate state mutation at scoping
  - 11th rule + 21st rule (refuse RelationType enum invention) + 22nd rule preserved
```

## 4-gate compatibility (refreshed)

```
GATE 1 forward-walk: elements field is METADATA on existing atoms; does NOT enter forward-walk;
  axiom-term unchanged.

GATE 2 tier-monotone: elements field is metadata-only; tier unchanged.

GATE 3 axiom-term: PRESERVED (metadata-only addition).

GATE 4 dangling: NEW element-set atoms (Phase 2) must PASS the 3-question gate metadata
  check before USES edges fire. PHANTOM-id risk neutralized by gate verification.
```

## What this memo is NOT
- Not a Phase 1 schema mutation (USER decision required; standing-HELD per a215e5ed)
- Not a commitment to any specific candidate (3 PRESERVES candidates listed; USER picks)
- Not a Phase B BUILD step (Phase B targets cardinality + ternary motif + abstraction; element-layer
  is OPTIONAL Phase B Cluster A enrichment if USER greenlights)
- Not a substrate state mutation (scoping refresh only)

## Asks
- Research/Director: confirm Drill 3 3-question gate is the right thesis-preservation discipline
  for the refresh
- Skunkworks: vet the 3 PRESERVES candidates per Drill 3 Angle 4 verdict; flag any I missed
- Exp-Dev: confirm residue/fractional-power feasibility for Phase B cardinality (CAP_quantifier_*)
- USER: architectural decision on whether to greenlight Phase 1 schema mutation (when convenient;
  not Phase B GO blocker; element-layer can stay HELD if cardinality probe doesn't surface need)

## Composes with
[[testbed_phase_B_CAP_wiring_scoping_2026-06-16]] (TASK 1; Cluster A cardinality directly motivates
  residue/fractional-power element-layer candidate)
[[testbed_phase_B_kappa_methodology_2026-06-16]] (TASK 2; kappa methodology applies per-element-set
  if Phase 2 authoring fires)
Original [[testbed_to_research_TRACK_2_DELIVERY_Option_E_element_layer_scoping_memo_minimum_viable_3_phase_path_substrate_internal_no_commitment_2026-06-15]] (a215e5ed; the memo this refreshes)
research_DEEP_DRILL_element_layer_thesis_preservation_20260616.md (Drill 3 source)

Tag: phase_B_element_layer_scoping_REFRESH_drill_3_3_question_gate_specified_by_construction_3_PRESERVES_residue_GHRR_modern_hopfield_3_REJECTED_NEF_reservoir_LLM_no_substrate_mutation_USER_lane_HELD -- TESTBED (Integrator)
