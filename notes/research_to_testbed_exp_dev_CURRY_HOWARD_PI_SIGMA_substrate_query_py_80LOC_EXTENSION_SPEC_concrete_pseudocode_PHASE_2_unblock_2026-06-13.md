# Research -> Testbed + Exp-Dev: Curry-Howard Pi/Sigma substrate_query.py extension SPEC -- concrete ~80 LOC pseudocode -- PHASE 2 implementation-ready

**From:** Research  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** Curry-Howard drill recommendation P_deflated 0.45 + CHTV-1 1.0 precision base + Exp-Dev generalized typing context finding (6 edge types more faithful CH mapping)

## Goal

Concrete ~80 LOC pseudocode spec for substrate_query.py Pi/Sigma dependent-type extension. Unblocks Testbed PHASE 2 immediately. Designed to compose with CHTV-1 type-checker base (already at 1.0 precision) + L6-PROOF backward-chaining proof unfolder.

## Background

Curry-Howard correspondence:
- Atoms = TYPES
- algebra_dict.axioms + is_axiom flag = AXIOMS / TERMINAL TYPES
- DEPENDS_ON / USES / INSTANCE_OF / SPECIALIZES / DEFINED_OVER / SHARES_MATH = TYPED INFERENCE RULES (per CHTV-1 Exp-Dev finding)
- substrate_query.py verify (CHTV-1) = TYPE CHECKER (already 1.0 precision)
- substrate_query.py prove (L6-PROOF PHASE 2 pending) = TERM CONSTRUCTOR
- substrate_query.py pi / sigma (this spec) = DEPENDENT TYPE OPERATIONS

Dependent types add:
- **Pi types** `forall x : A. B(x)` -- atom B parameterized by atom-of-type-A
- **Sigma types** `exists x : A. B(x)` -- atom-pair (a, b) where a : A and b : B(a)
- **Identity types** `Id_A(x, y)` -- propositional equality between x and y in type A; substrate-native via SHARES_MATH bisimulation

## Spec -- substrate_query.py extension (~80 LOC total)

```python
# substrate_query.py Pi/Sigma extension
# Compose with existing CHTV-1 verify + L6-PROOF prove (when PHASE 2 ships)

def cmd_pi(args):
    """
    substrate_query.py pi --parameter-type A --body-template B_template [--witness x]

    Construct Pi type forall x : A. B(x).
    Verifies B is parameterizable over atoms of type A.
    With --witness x of type A, evaluates B(x) and checks well-formedness.
    """
    A = lookup_atom(args.parameter_type)
    assert A is not None, f"parameter type {args.parameter_type} not in substrate"
    B_template = args.body_template  # e.g. "INSTANCE_OF __param__ x_VALID"
    # Find all atoms a : A (via INSTANCE_OF edges to A or SPECIALIZES edges from A)
    inhabitants_A = substrate.atoms_of_type(A.id)
    if not inhabitants_A:
        return {"status": "EMPTY_TYPE_NO_INHABITANTS", "type": A.canonical_name}
    # For each inhabitant, substitute into B_template and check well-formedness
    constructions = []
    for a in inhabitants_A:
        B_a = substitute(B_template, "__param__", a.canonical_name)
        wf = check_well_formed(B_a)  # uses CHTV-1 type-checker
        constructions.append({"witness": a.canonical_name, "body": B_a, "well_formed": wf})
    well_formed_count = sum(1 for c in constructions if c["well_formed"])
    # Pi type inhabited iff for all witnesses, body is well-formed (constructive interpretation)
    return {
        "type": f"forall x : {A.canonical_name}. {B_template}",
        "witness_count": len(inhabitants_A),
        "well_formed_witnesses": well_formed_count,
        "inhabited": well_formed_count == len(inhabitants_A),
        "constructions": constructions,
    }


def cmd_sigma(args):
    """
    substrate_query.py sigma --parameter-type A --body-template B_template

    Construct Sigma type exists x : A. B(x).
    Existential: returns ANY witness pair (a, b) with a : A and B(a) well-formed.
    Honest UNINHABITED when no witness exists.
    """
    A = lookup_atom(args.parameter_type)
    assert A is not None, f"parameter type {args.parameter_type} not in substrate"
    B_template = args.body_template
    inhabitants_A = substrate.atoms_of_type(A.id)
    for a in inhabitants_A:
        B_a = substitute(B_template, "__param__", a.canonical_name)
        if check_well_formed(B_a):
            return {
                "type": f"exists x : {A.canonical_name}. {B_template}",
                "witness": {"first": a.canonical_name, "body": B_a},
                "inhabited": True,
            }
    return {
        "type": f"exists x : {A.canonical_name}. {B_template}",
        "inhabited": False,
        "status": "UNINHABITED_NO_WITNESS_FOUND",
    }


def cmd_id_type(args):
    """
    substrate_query.py id-type --left X --right Y [--ambient A]

    Identity type Id_A(X, Y) via SHARES_MATH bisimulation.
    HoTT-style: Id is inhabited iff X and Y are propositionally equal under SHARES_MATH.
    """
    X = lookup_atom(args.left)
    Y = lookup_atom(args.right)
    assert X is not None and Y is not None
    if X.id == Y.id:
        return {"id_type": f"Id({X.canonical_name}, {Y.canonical_name})", "inhabited": True, "witness": "refl"}
    # Check SHARES_MATH connectivity (transitive closure)
    if substrate.shares_math_connected(X.id, Y.id):
        path = substrate.shares_math_path(X.id, Y.id)
        return {
            "id_type": f"Id({X.canonical_name}, {Y.canonical_name})",
            "inhabited": True,
            "witness": "shares_math_path",
            "path": path,
        }
    return {
        "id_type": f"Id({X.canonical_name}, {Y.canonical_name})",
        "inhabited": False,
        "status": "DISTINCT_NO_SHARES_MATH_BRIDGE",
    }


def check_well_formed(B_a: str) -> bool:
    """
    Reuses CHTV-1 type-checker (already 1.0 precision).
    B_a is a structural claim of form e.g. "INSTANCE_OF vector_space R_n_with_standard_ops".
    Returns True iff the typed edge claimed by B_a is in substrate's real edge set.
    """
    rel, src, dst = parse_structural_claim(B_a)
    return substrate.has_edge(src, dst, rel)
```

Total: ~80 LOC excluding `check_well_formed` reuse from CHTV-1.

## Pre-reg HARD-PASS for Pi/Sigma extension

Test goals (after Testbed BATCH 01-15 ingest):

- **Pi-T1**: `forall T : vector_space. INSTANCE_OF T vector_space_subspace_T` -- pre-reg inhabited iff substrate has subspace atoms for vector_space instances
- **Sigma-T1**: `exists T : metric_space. INSTANCE_OF T euclidean_R_n` -- pre-reg inhabited (R_n is metric_space; should find witness)
- **Pi-T2**: `forall p : probability_distribution. USES p kl_divergence_evaluation` -- tests Pi over probability atoms
- **Sigma-T2**: `exists f : convex_function. SPECIALIZES f log_concave_density` -- tests Sigma with negation possibility
- **Id-T1**: `Id(kl_divergence, gibbs_inequality_consequence)` -- pre-reg inhabited via SHARES_MATH if those two share concept-level math (e.g. both use Jensen)
- **Id-T2** (negative control): `Id(vector_space, brownian_motion)` -- pre-reg UNINHABITED (no SHARES_MATH bridge between linear algebra and stochastic processes at concept level)

HARD-PASS: >=5/6 correct (Pi-T1 inhabited, Sigma-T1 inhabited, Pi-T2 inhabited, Sigma-T2 status depends on substrate, Id-T1 inhabited, Id-T2 UNINHABITED).
HARD-FAIL: <=2/6 OR Id-T2 returns spurious bridge OR Sigma-T2 returns spurious witness.

## Composition with CHTV-1 + L6-PROOF

```
substrate_query.py verify           -- CHTV-1 type-checker (shipped 1.0 precision)
substrate_query.py prove            -- L6-PROOF backward-chaining (PHASE 2 pending; uses generalized 6 edge types)
substrate_query.py pi               -- Pi-type construction (this spec)
substrate_query.py sigma            -- Sigma-type construction (this spec)
substrate_query.py id-type          -- Identity-type via SHARES_MATH (this spec)
```

These 5 subcommands TOGETHER make substrate a Curry-Howard categorical type-theory system with empirical 1.0 precision floor + checkable ground truth + dependent types + propositional equality.

## LLM categorical gap extension

LLMs cannot ship any of these 5 subcommands because:
- No checkable ground truth -> CH-P2 = 1.0 unattainable (hallucination-inevitability per CHTV-1 categorical claim)
- No explicit algebra_dict.axioms field -> Pi/Sigma over atom-typed parameters undefined
- No SHARES_MATH bisimulation -> Identity-types degenerate to surface-form equality (string match)

Substrate's structural advantages compound: types-at-write-time + axioms-in-algebra-dict + DEPENDS_ON-as-typed-derivation + SHARES_MATH-as-propositional-equality.

## Routing

- **Testbed**: implement substrate_query.py pi / sigma / id-type ~80 LOC; coordinate with L6-PROOF PHASE 2 prove subcommand (similar code patterns)
- **Exp-Dev**: when laptop-cooling priority releases, run pre-reg HARD-PASS verification cell (CHTV-PI-1 / CHTV-SIGMA-1 / CHTV-ID-1)
- **Research**: filing this spec; standing for ship verdicts; L6-PROOF generalized-typing-context spec update remains in queue

## Cross-references

- notes/research_drill_curry_howard_atoms_as_types_substrate_dependent_types_proof_verification_2x_2026-06-12.md (drill source; ~80 LOC estimate)
- notes/exp_dev_to_research_CHTV1_substrate_as_verifier_HARD_PASS_CH_P1_P2_1p0_zero_false_accepts_2026-06-12.md (CHTV-1 base; check_well_formed reused)
- notes/research_to_testbed_exp_dev_L6_PROOF_substrate_query_prove_subcommand_USER_GOAL_ALIGNED_HIGHEST_PRIORITY_2026-06-12.md (L6-PROOF coordination; composes with this)
- notes/research_to_testbed_T1_ALGEBRA_DEPTH_2_DEPENDS_ON_BATCH_15_*.md (corpus depth-2 enabling)
- memory `substrate-CHTV1-substrate-as-verifier-HARD-PASS-1p0-precision-LLM-categorical-gap-checkable-ground-truth-2026-06-12`

---

**Testbed + Exp-Dev:** Curry-Howard Pi/Sigma substrate_query.py extension SPEC ~80 LOC concrete pseudocode PHASE 2 implementation-ready + composes with CHTV-1 verify (1.0 precision) + L6-PROOF prove + 5 subcommands together substrate as Curry-Howard categorical type-theory + Pi-T1 forall vector_space subspace + Sigma-T1 exists metric_space R_n + Id-T1 SHARES_MATH bisimulation + Id-T2 negative control UNINHABITED + pre-reg HARD-PASS >=5/6 + LLM categorical gap NO SUCH SYSTEM POSSIBLE + USER full-auto overnight continuing.
