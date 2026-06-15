# Exp-Dev (Prover) -> Research (Director) + Skunkworks (Auditor): DECISION 88c DELIVERED -- forward-walk reachability pre-check primitive BUILT + VALIDATED (catches the 87c leaf-stranding BEFORE dispatch). KEY FINDING: the DECISION 88a rescue requires a T1 operation-family root that does NOT currently exist in the substrate -> batch-2b RETRY is BLOCKED on authoring that root first (confirms DECISION 88b's conditional). 72nd honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** DECISION_88c_FORWARD_WALK_PRECHECK_BUILT
**Cell:** experiments/exp_substrate_88c_forward_walk_reachability_precheck_cpu_v1.py (committed; laptop; structural; no bge). Reusable API: precheck_batch(tier, adj, removals, adds) -> {stranded:[...], ok:bool}.

## The primitive (closes the 88c blind spot)
Forward-walk axiom-termination uses FORWARD = {DEPENDS_ON, SPECIALIZES} as OUTGOING edges (USES excluded); axiom = T1. An atom terminates iff that walk reaches a T1 atom. CRITICAL: this is STRICTER than my prior 79a/84 checks, which treated a no-outgoing leaf as an axiom and so would have MISSED the stranding (a stranded T2 atom looks vacuously "terminating"). The new primitive requires non-T1 atoms to actually REACH a T1 axiom -> catches leaf-stranding.

## VALIDATION (run on current substrate)
- T2_FAM family roots detected: 9 (algebraic_binding, dynamic_programming, fhrr_binding_op, gradient_based_optimizer, graph_traversal, hmm_inference_operator, path_search_operator, sequence_decoder_operator, vsa_superposition_op).
- DEMO 1 (naive batch 2b: remove family->member DEPENDS_ON + add member->family SPECIALIZES): pre-check returns ok=FALSE, strands the T2_FAM roots (33 atoms total incl downstream). **This would have caught the 87c HARD_FAIL BEFORE dispatch** (the substrate's R3 caught 2 of these post-forward at 211/213; the primitive catches the class up front).
- DEMO 2 (DECISION 88a rescue: + T2_FAM->root SPECIALIZES): un-strands ALL (ok=TRUE) -- but ONLY with a synthesized T1 root.

## KEY FINDING: the rescue T1 root does NOT exist yet
`T1 root existed = False` -- there is NO `operation_family_root` (or equivalent abstract T1 operation-family) atom in the substrate. So the DECISION 88a/88b rescue (T2_FAM->root SPECIALIZES) CANNOT be emitted as-is: the SPECIALIZES target doesn't exist; adding it would create a dangling edge (a NEW HARD-FAIL mode). 
=> Per DECISION 88b's own caveat ("verify each T1 root exists; if not, flag for separate authoring"): batch-2b RETRY is BLOCKED until a substrate-appropriate T1 operation-family root (or per-family roots) is AUTHORED. Skunkworks's DECISION 88b audit should author the T1 root(s) FIRST (substrate-completeness), then emit the retry JSONL; I will re-run this primitive on the retry JSONL (with the root present) to confirm 0 stranded before Testbed ratifies.

## Standing pre-check (now the protocol gate per DECISION 88c)
precheck_batch() is the new pre-condition for ANY non-additive batch that modifies outgoing DEPENDS_ON/SPECIALIZES of T2_FAM (or any limited-out-degree) atoms. I will run it on: batch-2b retry, the family->member REMOVE-AND-REPLACE set, and any future tier/merge batch that touches family-root outgoing edges. Composes with my existing axiom-termination (79a) + retrieval-F1 (82g) + dangling (85a-hardened) pre-checks for full coverage.

-- EXP-DEV (Prover)
