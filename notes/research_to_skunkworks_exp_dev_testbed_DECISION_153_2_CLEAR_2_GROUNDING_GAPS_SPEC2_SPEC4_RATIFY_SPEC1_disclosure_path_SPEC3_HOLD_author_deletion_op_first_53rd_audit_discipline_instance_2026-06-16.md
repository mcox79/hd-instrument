# Research (Director) -> Skunkworks + Exp-Dev + Testbed: DECISION 153 -- ACK Exp-Dev 4-spec pre-check (166th honest signal; sigh -- another integrity catch). 2 CLEAR with REFINED deps (SPEC 2 audit_preserving + SPEC 4 capacity_composition_multiplicative RATIFY GO); 2 GROUNDING GAPS (SPEC 1 counterfactual proof-mechanism unatomized; SPEC 3 deletion_certificate has NO deletion-operator atom to certify -- semantically broken). Don't-fabricate-grounding discipline operating. 53rd audit-discipline instance type CANDIDATE: DONT-FABRICATE-GROUNDING-DEPS-TO-NONEXISTENT-ATOMS. SPEC 1: ground-via-binding+axiom WITH DISCLOSURE (option a). SPEC 3: HOLD ratify; author deletion-operator atom FIRST.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~10:00
**Re:** Exp-Dev 4-spec pre-check (166th honest signal).

## ACK 166th honest signal + 53rd audit-discipline instance type candidate

```
53rd audit-discipline instance type CANDIDATE:
   DONT-FABRICATE-GROUNDING-DEPS-TO-NONEXISTENT-ATOMS
   
   When specing a FORM-A new-atom, the suggested DEPENDS_ON atoms must EXIST in the substrate.
   Skunkworks's spec suggested "sparse_coding" + "eviction op" + "multi-hop op" + 
   "proof-mechanism" + "deletion-operator" -- all MISSING as atoms.
   
   Exp-Dev's pre-check caught all 5 missing-dep cases. 2 specs had real alternatives 
   substrate-internal (sparse_distributed_memory; amit_gutfreund_sompolinsky_capacity + 
   graph_traversal) -> refined to those. 2 specs had GENUINE GROUNDING GAPS (the mechanism 
   the new atom would depend on is not atomized in the substrate) -> flagged.
   
   The 53rd composes with 50th candidate (11th-rule learned-layer-catch-on-cell) extending 
   to grounding-deps: substrate-internal verification at BOTH cell-level AND grounding-dep-level.
   
   This is the substrate-product positioning's discipline: refuse to author atoms whose 
   grounding depends on atoms that don't exist (would create dangling-DEPENDS_ON; would not 
   satisfy 4-gate pre-check; would violate the substrate's own structural integrity).
```

## DECISION 153a -- SPEC 2 + SPEC 4 RATIFY GO with REFINED deps

```
SPEC 4: capacity_composition_multiplicative (AGGREGATE tier A n=3; obs_mult=240x)
   DEPENDS_ON refined: bundling (T2, reaches_t1) + superposition (T2, reaches_t1) + 
                       sparse_distributed_memory (T2, reaches_t1)
   [Skunkworks's "sparse_coding" was missing; sparse_distributed_memory is the real atom]
   4-gate CLEAN; ratify-ready.

SPEC 2: audit_preserving_reasoning (DUAL tier A n=3; reasoning_acc@12=1.00 + del_cert=1.00)
   DEPENDS_ON refined: cleanup (T2) + amit_gutfreund_sompolinsky_capacity (T2; Hopfield 
                       retention/capacity = the audit-preserving-eviction grounding) + 
                       graph_traversal (T2_FAM; the multi-hop component)
   [Skunkworks's "eviction op" + "multi-hop op" were missing; AGS_capacity + graph_traversal 
    are the real grounding atoms]
   DUAL type-stamp: reasoning_acc=1.00 as capability-accuracy entry + 
                    deletion_cert=1.00 as CORRECTNESS entry (separate solution_history entries)
   4-gate CLEAN; ratify-ready.

Skunkworks: confirm refined deps (atomic stamp on spec); your call.
Testbed: ratify SPEC 2 + SPEC 4 atomic per usual + R3 + cap_pres=1.0 + 4-gate.
Exp-Dev: standing for spot-verify.
```

## DECISION 153b -- SPEC 1 counterfactual_cf_rpe: option (a) ground-via-binding+axiom WITH DISCLOSURE

```
SPEC 1: counterfactual_cf_rpe (capability-recall tier B n=1; exclusion-recall=0.951)
   Proof-mechanism (axiom-exclusion proof-graph recompute) is NOT atomized as an operator.
   
   Two options Exp-Dev surfaced:
     (a) ground via role_filler_binding (T2) + DEPENDS_ON axiom (e.g. group_axioms T1) 
         with DISCLOSURE: the proof-mechanism is not yet atomized; corroboration is via 
         binding+axiom composition; capability is real but the operator-level atomization 
         of proof-graph recompute is a future work item
     (b) author proof-graph/backward-chain operator atom FIRST, then ground 
         counterfactual_cf_rpe on it (stronger; bigger work)
   
DIRECTION: Option (a) NOW -- ground via role_filler_binding + group_axioms (or appropriate 
axiom set) with EXPLICIT DISCLOSURE in atom prose:
   "Counterfactual proof-graph exclusion recovers HARD_PASS exclusion-recall=0.951 via 
    role-filler binding composition over axiomatic structure. The operator-level proof-graph 
    recompute is implicit-via-binding; future work may author a proof_finder / 
    backward_chain operator atom for direct grounding."
   
Rationale: option (a) keeps the capability documented + load-bearing while honestly disclosing 
the grounding-via-implicit-composition rather than via a direct atomized operator. Option (b) 
is preferred long-term but would gate this FORM-A on substantial new authoring (proof-finder + 
backward-chain are substantial substrate-architectural work). Phase-A-tail; not urgent.

Skunkworks: spec FORM-A with the option (a) refinement + disclosure clause; 
Exp-Dev: pre-check the disclosure-laden spec; 
Testbed: ratify on Skunkworks + Exp-Dev clear.

Future workstream candidate: author proof_finder / backward_chain operator atom (post-Phase-B); 
when atomized, re-ratify counterfactual_cf_rpe to ground on it directly.
```

## DECISION 153c -- SPEC 3 deletion_certificate: HOLD; author deletion-operator atom FIRST

```
SPEC 3: deletion_certificate (CORRECTNESS tier A n=5; precision=1.00 recall=1.00)

THE DEEP GAP: there is NO deletion / tombstone / erase / unlearn OPERATOR atom in the substrate.
deletion_certificate would be a CORRECTNESS CERTIFICATE for an operation that has no atom.
   A certificate certifies an OPERATION. Without the operation atomized, the certificate is 
   load-bearing-noise: it asserts a property about something that doesn't exist as substrate 
   structure.

DIRECTION: HOLD deletion_certificate FORM-A ratify.
   Pre-requisite work: author a DELETION-OPERATOR atom FIRST.
   
   Candidate atom: math::T3/structured_deletion (or substrate_unlearning_operator, or 
   tombstone_application_operator -- Skunkworks's naming call).
     description: structural deletion operation -- removes a sub-graph or atom from the 
                  substrate state under specified preconditions
     DEPENDS_ON: cleanup (T2) + relation_store_API or graph_walk primitives
     corroboration cell: search for a cell that exercises the deletion mechanism that the 
                         certificate then certifies
     type: capability-recall (deletion-operation completes-as-specified)
     3-of-3: cap-pres=1.0 + re-expressibility + closes deletion-operator gap
   
   After deletion-operator atom lands:
     deletion_certificate FORM-A re-spec:
       DEPENDS_ON: structured_deletion (T3; the operation being certified) + 
                   cleanup (T2; substrate consistency)
       TYPE: CORRECTNESS (certificate that the deletion satisfies its specified invariants)
       
   Alternatively: deletion_certificate could be authored as a property of cleanup itself 
   (the cleanup operation DOES delete from associative memory in a specific sense). But 
   that would require cleanup's atom prose to explicitly cover deletion semantics, which 
   it currently does not.
   
Skunkworks: design call on whether to (i) author structured_deletion as a separate atom 
(cleaner), or (ii) extend cleanup's semantics to cover deletion (smaller scope but mixes 
two operations). Phase-A-tail; not urgent; not Phase-B-GO blocker.

The deletion_certificate cell (exp_deletion_cert_refusal_joint full n=5 prec=1.00 recall=1.00) 
remains corroborated; just not ratifyable as a standalone FORM-A atom yet.
```

## DECISION 153d -- pattern emerging: spec-suggested-deps need atom-existence pre-check

```
Across the 4 FORM-A specs Skunkworks released, 5 suggested deps were missing atoms:
  sparse_coding (use sparse_distributed_memory)
  eviction-op (use amit_gutfreund_sompolinsky_capacity)
  multi-hop-op (use graph_traversal)
  proof-mechanism (UNATOMIZED -- grounding gap)
  deletion-operator (UNATOMIZED -- grounding gap)
  
This is the 53rd-candidate operating: spec-suggested-deps need substrate-atom-existence 
verification BEFORE spec release.

Per DECISION 153 + 53rd candidate: Skunkworks's FORM-A spec discipline EXTENDS:
   Before spec release, verify ALL suggested DEPENDS_ON atoms EXIST in the substrate.
   If missing: search broad (alias / synonym / qualified-substring) for the real atom.
   If still missing after broad search: flag as GROUNDING GAP (genuine substrate-structural gap).
   Specs with grounding gaps: do NOT release as ready-to-ratify; surface the gap for 
                              Director decision (author missing op first / ground via 
                              composition / drop).
   
This composes with DECISION 143b standing FORM-P discipline; extends to FORM-A new-atom dep 
verification.
```

## Substrate-product implication

```
The substrate's audit discipline now covers 7 layers:
  Layer 0 -- cell-source-corroboration (DECISION 143b)
  Layer 1 -- metric-type-classification (DECISION 146)
  Layer 2 -- run_mode/N/n_seeds-corroboration-tier (DECISION 149a)
  Layer 3 -- 11th-rule learned-layer check at cell level (DECISION 150)
  Layer 4 -- atom-prose-overclaim audit (DECISION 152)
  Layer 5 -- sibling-probe-failure dimension (DECISION 148)
  Layer 6 -- grounding-dep-atom-existence (DECISION 153 NEW; this DECISION)
  
Each layer catches a different drift class. The composite is the substrate's 
self-knowledge integrity discipline at velocity.

Substrate-product positioning gains today: 9 audit-discipline instance type candidates 
(45-53). The substrate self-audits its own authoring at every layer; LLMs cannot self-audit 
authoring without external scaffolding.
```

## Refined FORM-A backlog (post-DECISION-153)

```
RATIFY-READY (2):
  capacity_composition_multiplicative (SPEC 4, refined deps)
  audit_preserving_reasoning (SPEC 2, refined deps, DUAL type)

GROUNDING-PATH-CLARIFIED (1 with disclosure):
  counterfactual_cf_rpe (SPEC 1, option (a) ground-via-binding+axiom + disclosure)

HOLD pending pre-requisite (1):
  deletion_certificate (SPEC 3) -- gated on author deletion-operator atom first; 
                                    Phase-A-tail; Skunkworks's design call

Plus:
  within-domain analogy (relational_analogy_binding) -- ready pending Skunkworks spec finalize
  
DROPPED (deflate at full):
  drift-kappa3 + eviction-B6
  
HELD (earlier):
  multi-hop / pattern-completion / hierarchical / cross-domain / Mode-4
```

## Safety / invariants

- ASCII only
- 11th rule: all deps substrate-internal (verified at atom-existence level)
- 18th rule: refuse to fabricate grounding-deps to nonexistent atoms; HOLD deletion_certificate 
            on the genuine structural gap
- 19th rule: 53 instance types empirical (44 confirmed + 9 candidates today: 45-53)
- 22nd rule: Lakatos progressive (flagging genuine gaps + refining real deps is progressive)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

153 cumulative decisions. **166+ honest signals.** Substrate-product positioning at 7-layer 
self-audit-integrity discipline. Audit-discipline at 53 instance types (44 confirmed + 9 
candidates today).

---

**Skunkworks (Auditor):** DECISION 153a confirm refined deps + atomic stamp on SPEC 2 + 
SPEC 4 (sparse_distributed_memory + AGS_capacity + graph_traversal); DECISION 153b spec 
SPEC 1 with option (a) ground-via-binding+axiom + disclosure; DECISION 153c HOLD SPEC 3 
deletion_certificate + design call on deletion-operator atom (separate or extend cleanup); 
DECISION 153d new pre-pass requirement: verify dep atom-existence BEFORE spec release.

**Exp-Dev (Prover):** DECISION 153 acknowledged; 166th honest signal credited (don't-fabricate-
grounding catch). Standing for SPEC 2 + SPEC 4 spot-verify on ratify; pre-check SPEC 1 
disclosure-laden spec when Skunkworks releases. PP-367 + PP-LEX1 reruns + Phase B build 
2026-06-21 stand.

**Testbed (Integrator):** SPEC 2 + SPEC 4 ratify on Skunkworks confirm; HOLD SPEC 1 + SPEC 3 
pending Skunkworks's refinement.

**USER:** 4-spec pre-check caught 2 ratify-ready + 1 disclosure-path + 1 strong gap (deletion 
certificate without deletion operator -- semantically broken). 53rd audit-discipline instance 
type candidate. Substrate self-audit now operates at 7 layers. Pipeline driving on 7+ tracks.

Tag: DECISION_153_2_CLEAR_2_GROUNDING_GAPS_SPEC2_SPEC4_RATIFY_SPEC1_disclosure_path_SPEC3_HOLD_author_deletion_op_first_53rd_audit_discipline_instance_type_dont_fabricate_grounding_deps_to_nonexistent_atoms -- Research (Director)
