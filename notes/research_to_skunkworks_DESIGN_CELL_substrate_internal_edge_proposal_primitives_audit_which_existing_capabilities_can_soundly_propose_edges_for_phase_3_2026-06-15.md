# Research (Director) -> Skunkworks (Auditor): SUBSTRATE-INTERNAL DESIGN CELL -- audit which of substrate's existing primitives can soundly propose edges for autonomous Phase 3 CO-EVOLVE-1 (non-LLM; 11th rule); informs Phase 3 architecture design BEFORE dispatch

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~09:10
**Re:** USER strategic question (does this warrant research?); DECISION 64 reframe (autonomous generalization is Phase 3). Per overnight full-auto + auto mode.

## Why this cell now

USER asked: "what are we trying to do and how can we make it work?" The honest answer:
- Substrate generalizes to in-distribution concepts (M4d +0.124)
- Substrate does NOT generalize to new concepts (M4d +0.005)
- The gap = new concepts have no incident edges; M4d cannot amplify nothing
- Phase 3 CO-EVOLVE-1 = autonomous edge-discovery so new concepts gain edges WITHOUT manual authoring
- BUT: Phase 3 has never been operationally specified

This cell asks: of substrate's EXISTING primitives, which can SOUNDLY propose typed edges for atoms with empty neighborhoods?

## Candidate edge-proposal mechanisms (substrate-internal; for your audit)

For each, evaluate: feasibility / soundness / false-positive rate / scope. Use a 5-10 atom witness set drawn from substrate's existing high-degree atoms (so you can verify "does this mechanism propose the edges that already exist?" as a sanity check).

### Mechanism P1 -- bge-similarity edge proposal
- Procedure: for atom X with empty typed-edge inventory, find top-K bge-nearest substrate atoms; propose typed edges to them
- Sound? bge similarity is NOT a sound type guarantee; needs CHTV-style verification per proposed edge
- Type assignment: use type-signature matching to assign edge type (SHARES_MATH if same op type; DEPENDS_ON if X's def references Y's name; ...)
- Audit: how often does P1 propose the CORRECT type? what's the precision on the 5-10 atom witness set?

### Mechanism P2 -- L6-PROOF-driven DEPENDS_ON proposal
- Procedure: for atom X with claim Y in its definition, attempt L6-PROOF derivation Y from X's axioms / def
- If proof terminates -> propose DEPENDS_ON edge X->Y (provable dependency)
- Sound? L6-PROOF is sound by construction; any provable derivation IS a real DEPENDS_ON
- Limitation: only DEPENDS_ON edges (not SHARES_MATH or other types)
- Audit: how many existing DEPENDS_ON edges can L6-PROOF re-derive? what % of high-degree atoms?

### Mechanism P3 -- type-signature SHARES_MATH proposal
- Procedure: for atom X with operation_type T and output_type O, find substrate atoms with same (T, O); propose SHARES_MATH
- Sound? structural match is heuristic, not a proof; needs CHTV-style verification (do they actually share the math content?)
- Limitation: substrate's operation_type / output_type signals are partial (per skunkworks_self_reasoning_scorecard)
- Audit: precision on existing SHARES_MATH edges (does P3 propose them?)

### Mechanism P4 -- co-occurrence-driven USES proposal
- Procedure: for atom X with description / source text mentioning atom Y, propose USES X->Y
- Sound? text co-occurrence is NOT sufficient; needs CHTV-style verification of actual usage
- Limitation: depends on quality of atom descriptions / source provenance
- Audit: does P4 surface USES edges that already exist? false-positive rate?

### Mechanism P5 -- foundation-primitive SPECIALIZES proposal
- Procedure: for atom X with type Tk, propose SPECIALIZES X -> Tk-1's foundation primitive if X's def matches the primitive's pattern
- Sound? type-hierarchy traversal is structural; verifiable via 46a foundation primitive definitions
- Limitation: covers only SPECIALIZES, not the typed-edges M4d uses most
- Audit: does P5 recover existing SPECIALIZES edges?

## What the cell should produce

For each P1-P5:
1. **Precision audit on existing high-degree atoms** -- does the mechanism propose edges that already exist? (recall the actual edges; report fraction correctly proposed)
2. **False-positive estimate** -- of K proposed edges per atom, how many would FAIL CHTV?
3. **Type-coverage** -- which edge types (SHARES_MATH / DEPENDS_ON / USES / SPECIALIZES / INSTANCE_OF) does the mechanism cover?
4. **Soundness gate** -- can substrate VERIFY proposed edges via CHTV without external oracle?
5. **Composability** -- can P1-P5 compose into a multi-mechanism DETECT-PROPOSE pipeline?

## What this does NOT do

This cell does NOT propose new edges or modify substrate state. It is a STRUCTURAL AUDIT of substrate's existing capabilities for edge proposal. Output is a design memo, not new substrate atoms.

## HARD-PASS / HARD-FAIL

**HARD-PASS:** report delivered with the 5 mechanism audits; clear identification of which mechanisms have ACCEPTABLE precision (> 0.5) AND ACCEPTABLE false-positive rate (< 0.3) for Phase 3 use
**HARD-FAIL:**
- Any LLM-as-judge contamination (forbidden)
- Fabricated numbers (10th rule)
- Modifying substrate state (this is audit only)

## Composition with research drills

I have ALSO dispatched 2 background literature drills:
1. 3x deep on non-LLM autonomous KG completion / rule mining / pattern-based ontology learning
2. 2x deep on self-improving / bootstrap / co-evolution architectures in retrieval and reasoning

Your substrate-internal audit + the 2 literature drills together inform the Phase 3 CO-EVOLVE-1 ARCHITECTURE design. After all 3 return, Director synthesizes a Phase 3 dispatch spec.

## Cost

~2-3 hrs Skunkworks (substrate-internal counting + small-witness-set validation; no bge / no remote / no LLM). Lower priority than 55a redesigned (which is in flight) -- dispatch when 55a returns OR run in parallel if bandwidth.

## Safety / invariants

- ASCII only
- Substrate-on-its-own (11th rule): no LLM in audit; substrate uses its own primitives only
- No held-out question / gold inspection (uses only substrate's existing atoms; not held-out)
- No fabricated numbers (10th rule)
- 18th rule: each mechanism's precision / FP rate reported honestly; refuse to claim feasibility without measurement
- 19th rule: substrate's audit may refute Director's hypothesis that any P1-P5 is viable; report honestly

## What Phase 3 looks like if this audit + literature drills support it

```
LOOP CO-EVOLVE-1:
  while true:
    detect: substrate identifies LOW-DEGREE atom X (substrate-internal completeness signal)
    propose: P1-P5 multi-mechanism proposal set for X; rank by composite confidence
    verify: CHTV (+ L6-PROOF for DEPENDS_ON proposals); reject any failing edge
    integrate: atomically ratify verified edges; preserve capability_preservation=1.0 + 100pct axiom termination
    metric: re-run M4d on a held-out (rotating; 56d-v2 first; then future v3+); measure F1 delta
    if F1 delta on held-out > 0: continue
    if F1 delta on held-out <= 0 for N rounds: stop (saturation)
```

This is the operational DETECT-PROPOSE-VERIFY-INTEGRATE-METRIC-UP architecture; needs substrate-internal validation that P1-P5 mechanisms actually work.

Tag: SUBSTRATE_INTERNAL_DESIGN_CELL_EDGE_PROPOSAL_PRIMITIVES_AUDIT -- Research (Director)
