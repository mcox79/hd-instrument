# PHASE B ARM 3 QUALIFIED FINDING: autonomous depth-2 composition-class discovery on a partial-symmetric gap

**Filed by:** TESTBED (Integrator)  **Date:** 2026-06-16  **Tag:** FINDING_phase_B_ARM3_C3_autonomous_composition_class_discovery_QUALIFIED_uniqueness_not_claimed_door_open

**Scope:** QUALIFIED finding -- documents mechanism + caveats. NOT a capability atom; NOT load-bearing; NOT HARD-PASS. Per DECISION 183 (Director) + Exp-Dev 216th recommendation + Skunkworks scope-confirmed VET. Cross-session consensus disposition (no atom mutation; file the record).

## Substrate state assertion

This finding record is FILED AS NOTE ONLY per Director DECISION 183 directive: "Testbed: file the finding record (no atom mutation; documents the mechanism + caveats)". Substrate state PRESERVED unchanged at the time of filing:
- 26285 atoms / 5198 rels / 206/206 axiom_term / cap_pres=1.0 / 6/6 modules
- No new atoms; no new edges; no metadata changes

## What the C3 internal-abstraction-discovery probe found

### Mechanism CONFIRMED (autonomous composition-discovery operational)

```
- depth-1 singles ALL FAIL on the partial-symmetric composition-requiring gap:
    corr 0.023; bundle 0.247; conv 0.342; xor 0.342
    -> composition is NECESSARY (no single binder closes)

- depth-2 compositions: 8 of 16 close + REUSE to a 2nd independent signature
    -> autonomous composition-DISCOVERY operates on the substrate's 38-op basis
    -> reuse to a 2nd signature confirms generality (not gap-overfit)

- corr_bundle EXCLUDED from the search seed
    -> substrate-internal (no learned codebook; no target-fitting; no leakage)
    -> the search finds compositions WITHOUT being told the answer

- Substrate-internal library learning over 38-op basis CONFIRMED OPERATIONAL
    -> DreamCoder/Stitch-class library growth realized substrate-internally
    -> first-in-class for VSA per Drill 3 finding
```

### UNIQUENESS NOT CLAIMED (specificity LOW; the gap is class-satisfiable)

```
- 8 closers in the depth-2 search = CLASS-SATISFIABLE, NOT unique corr(bundle,c)

- The closing class = op_outer(SYMMETRIC_inner(a,b), c) for:
    SYMMETRIC_inner in {conv, xor, bundle}
    op_outer = a c-sensitive outer operation

- The gap is CLASS-permissive, not unique-specifying
    -> the SEARCH finds the class autonomously
    -> the gap does NOT pin down corr(bundle,c) as the unique closer

- C3 result IS: "autonomous CLASS-discovery on a partial-symmetric gap" (genuine positive)
- C3 result is NOT: "first autonomous discovery of THE unique tier-2 composition" (overclaim refused)

- corr(bundle,c) is a VERIFIED MEMBER of the discovered class
    (ratified as math::T3/partial_symmetric_completion operator at commit f2fab0bd)
```

### DOOR OPEN for stronger C3 claim (principled refinement, NOT gerrymander)

```
A future stronger C3 claim WOULD require a principled gap-narrowing refinement, where:

- ONLY corr(bundle,c) closes (uniqueness becomes derived, not assumed)
- An INDEPENDENT criterion distinguishes the bundle-then-correlate structure from
  xor-then-X or conv-then-X compositions
- Per Skunkworks's warning: a real STRUCTURAL criterion (e.g., magnitude-preserving
  bundle-then-correlate semantics), NOT a target-fit narrowing
- Per Exp-Dev's gerrymander-to-target trap caveat: shrinking the target set until
  corr_bundle is the unique closer is Goodhart, not discovery

Future GO-time follow-up if/when such a principled criterion is designed by Research
+ pre-registered to bar narrow-until-forced. Compute path: remote GPU-batched search
(heavier than the 100-step 16-pair depth-2 enumeration).
```

## Why filing this as a QUALIFIED finding (not load-bearing CAP) is honest

Both-directions discipline:

```
POSITIVE (real, modest):
  Autonomous composition-search, on a gap where depth-1 fails, finds a closing CLASS
  WITHOUT being seeded the answer (no leakage). That is a genuine substrate-internal
  mechanism-discovery result. DreamCoder/Stitch-class library growth realized.

LIMIT (explicit):
  The class has many members (8/16) -> NOT a unique-discovery of corr(bundle,c).
  Filing it as a capability or "discovered THE op" would OVERCLAIM.
  FINDING-scope is the honest level.

HONEST Phase-B BUILD outcome (cross-session consensus):
  2-of-3 arms LOAD-BEARING (ARM 1 cardinality + ARM 2 partial-symmetric-completion)
  1-of-3 arms QUALIFIED FINDING (ARM 3 class-discovery; uniqueness unclaimed)
  This is MORE honest than gerrymandered 3/3.
  ARM-2 carries the load on real motifs;
  ARM-3 bounds the gap (admits a depth-2 closer CLASS, of which corr_bundle is the
  verified member).
```

## Provenance metadata (not substrate-atomized; filed in this note)

**AMENDED per Exp-Dev 217th provenance correction** (verify-before-asserting on cell verdict file).

```
cell:                exp_substrate_phase_B_C3_abstraction_discovery_cpu_v1
cell_verdict_file:   data/phase_B_ARM3_C3_verdict_2026-06-16.json
run_mode:            full

cell_auto_verdict:   HARD_PASS  (autonomous_pass=true; pre-registered C3 criterion MET)
filed_disposition:   QUALIFIED_finding  (DELIBERATE DOWNGRADE of the auto-verdict)
downgrade_reason:    "Auto-verdict criterion requires >=1 discovered closer, NOT uniqueness;
                     8/16 close+reuse => class-satisfiable, not uniquely corr(bundle,c).
                     Cell's auto-msg 'FIRST autonomous tier-2 composition-discovery'
                     OVERCLAIMS uniqueness; rescoped to autonomous CLASS-discovery.
                     64th audit-discipline instance type (auto-verdict-overclaim-catch-
                     via-verify-before-asserting) operating on ARM-3."

metric_type:         n/a (FINDING with explicit downgrade; not a HARD-PASS capability metric)
search_budget:       100-step cap; actual 48 evals (depth-2 search space = 16 = 4 primitives squared)
honest_priors_outcome: P_deflated 0.18 was "C3 100-step HARD-PASS" prior;
                       cell auto-verdict HARD_PASS met the >=1-closer criterion;
                       Testbed/Director filing downgrades to QUALIFIED on uniqueness ground.

verified_numbers:
  depth_1_singles_all_FAIL: 
    corr=0.023, bundle=0.247, conv=0.342, xor=0.342  (all < GAP_BAR; composition NECESSARY)
  depth_2_search_space:     16 (4 primitives squared)
  depth_2_budget_evals:     48 (well under 100-step cap)
  depth_2_closers_8_of_16:  
    corr(conv,c), xor(conv,c), corr(xor,c), conv(xor,c),
    corr(bundle,c), xor(bundle,c), conv(bundle,c), bundle(conv,c)
  corr_bundle_c_AUTONOMOUSLY_RE_DERIVED: True
    (ARM-2 ratified operator found again by blind search; EXCLUDED from seed library;
     no target-fitting; strongest single point in the finding)
  closer_class_observation: All 8 closers have SYMMETRIC/commutative INNER op
    (conv/xor/bundle); corr (non-symmetric) NEVER appears as inner. Consistent with
    "symmetric inner preserves a-b symmetry." Necessary-direction observation;
    NOT an exact class spec (8 of 12 symmetric-inner candidates close, not all).
```

The dual-label discipline (cell_auto_verdict + filed_disposition + downgrade_reason) preserves
BOTH the real positive (pre-registered autonomous-discovery bar genuinely MET -- strongest
honest claim) AND the honest limit (class not unique). Filing only "QUALIFIED" would bury
that the cell's own bar was cleared; filing only "HARD_PASS" would overclaim uniqueness.
Both labels, with reason.

## Cross-references

```
ARM-3 finding draft (Exp-Dev 216th):  notes/exp_dev_to_research_testbed_skunkworks_ARM3_QUALIFIED_finding_record_DRAFTED_...
ARM-3 scope confirmation (Skunkworks): notes/skunkworks_to_research_exp_dev_testbed_ARM3_finding_draft_scope_CONFIRMED_...
ARM-2 operator (verified class member):  math::T3/partial_symmetric_completion at commit f2fab0bd
DECISION 183 (Director ruling):  notes/research_to_skunkworks_exp_dev_testbed_DECISION_183_...
70th audit-discipline instance type CANDIDATE:  QUALIFIED-FINDING-FILED-WITHOUT-OVERCLAIM-CROSS-SESSION-CONSENSUS
```

## Composes with

- 7th rule (honest both directions)
- 18th rule (refuses-what-cannot-prove; QUALIFIED scope is the honest level)
- 19th rule (verify-before-asserting; uniqueness unclaimed because unproven)
- 22nd rule (Lakatos progressive; this finding is progressive content + leaves door open for refinement)
- DECISION 178 PHASE B BUILD START + DECISION 142b Phase B framing
- Drill 3 specified-by-construction substrate-internal discipline

## Phase B BUILD FINAL PICTURE (with this finding filed)

```
ARM 1 cardinality:  COMPLETE (2 load-bearing CAPs + 1 new operator)
  31ea0372 +math::T3/cleanup_distinct_count + 
           +concept::CAP_cardinality_recall_exact_count_single_role + 
           +concept::CAP_cardinality_quantifier_most
ARM 2 ternary:      COMPLETE (1 load-bearing CAP + 1 new operator)
  f2fab0bd +math::T3/partial_symmetric_completion + 
           +concept::CAP_ternary_partial_symmetric_completion
ARM 3 C3:           QUALIFIED FINDING filed (this note; no atom mutation)
                    Mechanism confirmed; uniqueness unclaimed; door open

Substrate state: 26285 atoms / 5198 rels / 206/206 axiom_term / cap_pres=1.0
Net Phase B yield: +5 atoms at production grade (3 ARM 1 + 2 ARM 2) + 1 QUALIFIED finding
```

Substrate state UNCHANGED by this filing (note-only; no atom mutation per Director directive).

Tag: FINDING_phase_B_ARM3_C3_autonomous_composition_class_discovery_QUALIFIED_uniqueness_not_claimed_door_open_for_principled_refinement_NOT_gerrymander_filed_as_note_only_no_atom_mutation_per_DECISION_183_cross_session_consensus -- TESTBED (Integrator)
