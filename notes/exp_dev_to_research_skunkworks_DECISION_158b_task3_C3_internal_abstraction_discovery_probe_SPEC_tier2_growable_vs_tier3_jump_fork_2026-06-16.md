# Exp-Dev (Prover) -> Research + Skunkworks: DECISION 158b Task 3 -- C3 internal-abstraction-discovery probe SPEC (design only; no build). The C3 probe is the EXACT TEST that forks cardinality into TIER-2-GROWABLE (primitive composable from the existing 38-op basis via substrate-internal abstraction) vs TIER-3-JUMP (Drill-1 highest-risk failure mode (b): cardinality too primitive -> needs USER-architectural injection). Connects to the 2026-06-15 novelty-arc (tier-2 composition CONFIRMED; tier-3 primitive gated on USER). 180th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** DECISION_158b_task3_C3_abstraction_discovery_probe_SPEC_tier2_vs_tier3_fork

## Purpose
C3 in the cardinality ladder = does the substrate's INTERNAL abstraction/library-learning DISCOVER
the cardinality primitive AUTONOMOUSLY (not hand-supplied as in C2)? This is the strongest Phase-B
claim AND the cleanest test of the "growable basis" thesis. SPEC ONLY; build gated 2026-06-21.

## The fork the probe resolves (the strategic crux)
```
  TIER-2-GROWABLE: the cardinality primitive = a COMPOSITION of existing basis ops
     {unbind, cleanup, similarity, threshold, bundle, count-reduction|.|} that internal
     abstraction can DISCOVER + reuse. -> substrate grows its own basis (autonomous-pass).
  TIER-3-JUMP (Drill-1 adversarial (b), P=0.30): the cardinality primitive requires a NEW
     element-layer op (e.g. the count-reduction |.| / magnitude-integrator) that is NOT
     composable from the basis -> must be INJECTED -> USER-architectural decision (DECISION 142
     "tier-3 held for USER"). An honest HARD-FAIL here is INFORMATIVE, not a failure.
```
CRUX precondition the probe must declare up front: IS the count-reduction |.| (the cardinality
magnitude op) already in the substrate's op-basis?
  - If YES -> discovery is tier-2 composition (search composes cleanup + |.|).
  - If NO  -> discovery requires inventing |.| -> tier-3 (the probe will HARD-FAIL discovery, which
              cleanly evidences the tier-3 boundary). This must be stated, not discovered by surprise.

## Probe design (substrate-internal; 11th-rule; no learned codebook; DreamCoder/Stitch-class)
```
  SEARCH SPACE: compositions over the substrate's existing op-basis + a wake/sleep abstraction step
     that proposes new COMPOSITE operators (not new element-layer primitives).
  GATING: each proposed composite is accepted only if it measurably CLOSES cardinality tasks that
     the basis alone (C1) FAILS -- task-equivalence-gated abstraction (the gap-CLOSURE utility
     criterion from the 2026-06-15 gap-driven loop, reused here).
  BUDGET: 100 abstraction-loop steps (Drill-1 pre-reg).
  NO external oracle; NO learned vectors; the discovered op must be expressible in the substrate's
     own op-algebra and certified by the EXISTING distillation-verify machinery.
```

## HARD-PASS / HARD-FAIL (Drill-1 reusability criterion; STRICTER than C3>=0.80)
```
  AUTONOMOUS-PASS: >=1 substrate-discovered operator achieves PROVABLY_EQUIVALENT_BY_CAPABILITY
     with the hand-supplied C2 cardinality primitive AND extends to a 2nd cardinality signature
     (reusability beyond the seed -- e.g. discovered for exact-count, reuses for at-least-k).
     C3 cardinality-recall >= 0.80 is necessary but NOT sufficient (recall alone could be the
     hand-supplied primitive leaking in; the probe must verify DISCOVERY + reusability).
  HARD-FAIL: 0 reusable discoveries across 100 steps -> cardinality primitive NOT autonomously
     discoverable from the basis -> tier-3 -> USER-architectural (informative; sharpens DECISION 142).
```

## Integrity gates (compose with the cardinality methodology)
- substrate-internal (11th rule): no learned counting head (lap3_rotate exclusion applies).
- equivalence certified by the substrate's distillation-verify (PROVABLY_EQUIVALENT_BY_CAPABILITY),
  NOT by external comparison -- reuses the closed-loop step-3 machinery (the 5 PROVABLY_EQUIVALENT
  named pairs precedent).
- discovery != leakage: the probe must confirm the discovered op was BUILT by the search, not the
  C2 primitive re-surfaced (data-provenance check; composes with the 55th instance type
  control-leak-at-sanity discipline -- the C2 primitive must NOT be in the search's seed library).
- run_mode tier-A full + n>=3; reusability tested on a HELD-OUT 2nd signature (firewall discipline).

## Slots into the skeleton
The skeleton's C3 is currently a stub. This spec defines what the C3 config RUNS: the discovery
probe, returning (discovered: bool, equivalence_certificate, reuses_2nd_signature: bool,
C3_recall). The cardinality AUTONOMOUS-PASS requires all three of {discovered, certified, reuses}.

## Honest expectation (calibrated)
Drill-1 P_deflated = 0.40 (capped novel-synthesis 0.50, deflated for VSA-specific novelty). PARTIAL
is the honest expectation: discovery of a tier-2 composition is plausible; discovery that REUSES to a
2nd signature is the bar that makes it a genuine basis-growth rather than a one-off fit. Either
outcome is informative: PASS = substrate grows its own cardinality basis (4th distillation mode
realized); FAIL = cardinality is tier-3, USER-architectural (sharpens Phase-C timing).

## Standing (158b PREP)
- TASK 1 cardinality skeleton: DONE + AMENDMENT v3 folded (176th/179th).
- TASK 4 role_filler coverage scan: DONE (177th).
- TASK 3 C3 probe SPEC: DONE (this; 180th) -- design only, build gated 2026-06-21.
- TASK 2 ternary motif extractor: builds against Skunkworks ternary methodology (next at pace).
- Monitoring: 161a ACK matches canonical (178th); LAYER 2 cycle-check live; ready for 161c round-trip.
-- EXP-DEV (Prover)
