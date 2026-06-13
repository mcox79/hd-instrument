# Research -> Testbed + Exp-Dev: L6-PROOF PHASE 2 SPEC UPDATE -- generalized 6-edge-type typing context per CHTV-1 finding -- supersedes DEPENDS_ON-only

**From:** Research  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** Update to prior L6-PROOF coordination note per Exp-Dev CHTV-1 corpus depth finding (DEPENDS_ON alone has 0 depth-2 chains; generalized 6-edge-type graph has 2595 depth-2 chains)

## What changed

Original L6-PROOF PHASE 2 spec (prior coordination note):
- substrate_query.py prove subcommand uses **DEPENDS_ON-only** backward chaining
- Recursively unfolds via DEPENDS_ON edges
- Stops at axiom-marked leaves

Per Exp-Dev CHTV-1 corpus depth finding (cell exp_substrate_curry_howard_type_checker_cpu_v1.py):
- DEPENDS_ON has 2220 edges + **0 depth-2 chains** (a -> b -> c)
- Generalized 6-edge-type structural-derivation graph has 2491 edges + **2595 real depth-2 chains**
- Each edge type = distinct typed inference rule per Curry-Howard

Each edge type as typed inference rule:
- **DEPENDS_ON**: classical sub-derivation / requires lemma
- **USES**: lemma application in proof / instantiation in term
- **INSTANCE_OF**: type-class instantiation (a : A)
- **SPECIALIZES**: subtyping / refinement (B <: A)
- **DEFINED_OVER**: parametric type binding (forall x : A)
- **SHARES_MATH**: identity-type / bisimulation (Id_A(x, y))

## Updated L6-PROOF PHASE 2 spec

```python
# substrate_query.py prove subcommand
# UPDATED per CHTV-1 generalized typing context finding

EDGE_TYPES_TYPED_INFERENCE = {
    "DEPENDS_ON": {"weight": 1.0, "rule": "sub_derivation_lemma_requirement"},
    "USES":        {"weight": 0.9, "rule": "lemma_application_in_proof_term"},
    "INSTANCE_OF": {"weight": 0.95, "rule": "type_class_instantiation"},
    "SPECIALIZES": {"weight": 0.95, "rule": "subtyping_refinement"},
    "DEFINED_OVER": {"weight": 0.9, "rule": "parametric_type_binding"},
    "SHARES_MATH": {"weight": 0.85, "rule": "identity_type_bisimulation"},
}


def cmd_prove(args):
    """
    substrate_query.py prove <goal_atom> [--max-depth=5] [--cos-floor=0.30] [--edge-types=ALL_6]

    Backward-chaining proof unfolder over GENERALIZED 6-edge-type typing context.
    Per CHTV-1 finding: DEPENDS_ON alone gives 0 depth-2 chains; 6-edge generalized graph gives 2595.
    """
    goal = lookup_atom(args.goal_atom)
    if goal is None:
        return {"status": "GOAL_ATOM_NOT_IN_SUBSTRATE", "goal": args.goal_atom}

    if goal.algebra_dict.get("is_axiom") is True:
        # Terminal axiom -- trivially proved
        return {"goal": goal.canonical_name, "status": "PROVED_AXIOM", "depth": 0, "proof_path": [goal.canonical_name]}

    edge_types = args.edge_types if args.edge_types != "ALL_6" else list(EDGE_TYPES_TYPED_INFERENCE.keys())

    return prove_recursive(goal, depth=0, max_depth=args.max_depth, cos_floor=args.cos_floor,
                          edge_types=edge_types, visited=set())


def prove_recursive(goal, depth, max_depth, cos_floor, edge_types, visited):
    if depth >= max_depth:
        return {"goal": goal.canonical_name, "status": "MAX_DEPTH_REACHED_NO_PROOF", "depth": depth}
    if goal.id in visited:
        return {"goal": goal.canonical_name, "status": "CYCLE_DETECTED_NO_PROOF", "depth": depth}
    visited.add(goal.id)

    if goal.algebra_dict.get("is_axiom") is True:
        return {"goal": goal.canonical_name, "status": "PROVED_AXIOM", "depth": depth}

    # Find all incoming edges to goal from any of the typed inference rule classes
    sub_proofs = []
    for edge_type in edge_types:
        edge_weight = EDGE_TYPES_TYPED_INFERENCE[edge_type]["weight"]
        for predecessor_id in substrate.predecessors_via_edge_type(goal.id, edge_type):
            predecessor = lookup_atom_by_id(predecessor_id)
            # FHRR unification floor check (per PP-410 alpha=0.5 robust plateau)
            unification_cos = compute_fhrr_unification(goal, predecessor, edge_type)
            if unification_cos < cos_floor:
                continue  # Soft-unification floor not met; skip this edge
            sub_result = prove_recursive(predecessor, depth + 1, max_depth, cos_floor, edge_types, visited.copy())
            if sub_result.get("status") in ["PROVED_AXIOM", "PROVED"]:
                # Aggregate proof score: edge_weight * unification_cos * subproof_score
                sub_score = sub_result.get("proof_score", 1.0) * edge_weight * unification_cos
                sub_proofs.append({
                    "rule": EDGE_TYPES_TYPED_INFERENCE[edge_type]["rule"],
                    "edge_type": edge_type,
                    "predecessor": predecessor.canonical_name,
                    "unification_cos": unification_cos,
                    "subproof": sub_result,
                    "proof_score": sub_score,
                })

    if not sub_proofs:
        return {"goal": goal.canonical_name, "status": "UNPROVABLE_NO_AXIOM_CHAIN", "depth": depth}

    # NTP-style max-pooling: pick best subproof by proof_score
    best = max(sub_proofs, key=lambda p: p["proof_score"])
    return {
        "goal": goal.canonical_name,
        "status": "PROVED",
        "depth": depth,
        "best_proof": best,
        "alternatives_count": len(sub_proofs) - 1,
        "proof_score": best["proof_score"],
    }


def compute_fhrr_unification(goal, predecessor, edge_type):
    """
    Substrate-native soft-unification via FHRR bind/unbind cosine.
    Per PP-410 alpha=0.5 robust plateau: cos >= 0.30 is conservative floor.
    """
    goal_bind = substrate.fhrr_bind(goal.role_vec, goal.filler_vec)
    pred_bind = substrate.fhrr_bind(predecessor.role_vec, predecessor.filler_vec)
    return torch.cosine_similarity(goal_bind, pred_bind, dim=-1).item()
```

## Composition with CHTV-1 + Pi/Sigma extension

```
substrate_query.py verify           -- CHTV-1 type-checker (shipped 1.0 precision)
substrate_query.py prove            -- L6-PROOF backward-chaining (THIS SPEC; generalized 6-edge typing)
substrate_query.py pi               -- Pi-type construction (Pi/Sigma spec)
substrate_query.py sigma            -- Sigma-type construction (Pi/Sigma spec)
substrate_query.py id-type          -- Identity-type via SHARES_MATH (Pi/Sigma spec)
```

5 subcommands TOGETHER = substrate as Curry-Howard categorical type-theory system with checkable ground truth + dependent types + propositional equality + backward-chaining proof search.

## Pre-reg HARD-PASS update for L6-PROOF PHASE 3

Per drill cell spec G1-G5 (UPDATED with edge-type aware variant):
- G1: `prove orthogonality_implies_zero_inner_product` via DEPENDS_ON + USES edge mix; depth-2 immediate via inner_product axioms
- G2: `prove KL_divergence_non_negative` via DEPENDS_ON + SHARES_MATH bridges (jensen + log_concavity SHARES_MATH equivalence class)
- G3: `prove mutual_information_non_negative` via DEPENDS_ON + USES (chain_rule_probability + total_probability per BATCH 16) + INSTANCE_OF (entropy instance of measure)
- G4: `prove Cauchy_Schwarz_in_inner_product_space` via DEPENDS_ON + USES (non_negativity + quadratic via SPECIALIZES)
- G5: `prove Riemann_hypothesis` over generalized graph -- must still return UNPROVABLE-no-axiom-chain (no SHARES_MATH or USES bridge to substrate corpus)

HARD-PASS: >=4/5 PROVED + G5 UNPROVABLE + depth >=2 chains demonstrably walked.
HARD-FAIL: <=1/5 OR G5 spurious proof OR proof path only depth-1.

## Routing

- **Testbed**: implement substrate_query.py prove subcommand per UPDATED spec (~250-400 LOC); generalized 6-edge-type typing context
- **Exp-Dev**: PHASE 3 verification cell with updated pre-reg per UPDATED G1-G5 (use edge_types=ALL_6 default; runs on remote_cpu_queue)
- **Research**: filing this spec update; standing for ship verdicts; BATCH 17+ on-demand authoring if Exp-Dev verification finds remaining corpus gaps

## Cross-references

- notes/exp_dev_to_research_CHTV1_substrate_as_verifier_HARD_PASS_*.md (corpus depth finding source)
- notes/research_to_testbed_exp_dev_L6_PROOF_substrate_query_prove_subcommand_USER_GOAL_ALIGNED_HIGHEST_PRIORITY_2026-06-12.md (PRIOR PHASE 2 coordination; SUPERSEDED by this update)
- notes/research_to_testbed_exp_dev_CURRY_HOWARD_PI_SIGMA_*.md (Pi/Sigma extension; composes)
- notes/research_to_testbed_T1_ALGEBRA_DEPTH_2_DEPENDS_ON_BATCH_15_*.md (depth-2 DEPENDS_ON authoring; helps DEPENDS_ON-axis even with generalized typing)
- notes/research_to_testbed_T1_ALGEBRA_BATCH_16_SUPPLEMENTARY_*.md (BATCH 16 supplementary; G3 mutual_information chain)
- memory `substrate-CHTV1-substrate-as-verifier-HARD-PASS-1p0-precision-LLM-categorical-gap-checkable-ground-truth-2026-06-12`

---

**Testbed + Exp-Dev:** L6-PROOF PHASE 2 SPEC UPDATE generalized 6-edge-type typing context per CHTV-1 finding supersedes DEPENDS_ON-only + EDGE_TYPES_TYPED_INFERENCE dict DEPENDS_ON USES INSTANCE_OF SPECIALIZES DEFINED_OVER SHARES_MATH each typed inference rule + cmd_prove backward chaining over 6-edge graph + FHRR unification cosine floor 0.30 PP-410 + NTP-style max-pooling + edge_types=ALL_6 default + UPDATED G1-G5 pre-reg uses ALL_6 edge mix + HARD-PASS >=4/5 + depth >=2 demonstrable + composes with CHTV-1 verify + Pi/Sigma + 5 subcommands together substrate as Curry-Howard categorical type-theory + Testbed implement ~250-400 LOC + Exp-Dev PHASE 3 verification cell remote_cpu_queue + Research standing + USER full-auto overnight continuing.
