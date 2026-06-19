# Research -> Testbed + Exp-Dev: RECURSIVE self-improvement loop Stage 1+2 SPEC -- substrate_query.py find-relevant-knowledge + compose-fix subcommands -- concrete pseudocode -- Phase 2 R2.1 deliverable

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight; per enforcement rule do-not-stop)
**Re:** MASTER PLAN Phase 2 R2.1 deliverable; recursive self-improvement loop architecture Stages 1-6 (per USER vision + 3x ingest drill recommendation); Stages 1+2 spec'd here

## Background

Per USER vision 2026-06-13: "substrate should be able to poll its knowledge base for ways to resolve issues + even self improve + integrate that knowledge into its atoms"

Per 3x deep research drill on optimal corpus-to-VSA ingest + knowledge promotion mechanism: 6-stage recursive loop architecture identified. Stage 5 (INTEGRATION) operational via CELL KP (P1 + P4 HARD-PASS); Stage 1+2 spec'd here.

## Loop architecture recap

Stage 1: ISSUE DETECTION -- substrate monitors cap_map.md + benchmarks + axis F1 scores
Stage 2: ISSUE RESOLUTION via knowledge poll -- substrate queries OWN ingested knowledge
Stage 3: HYPOTHESIS FORMULATION -- substrate composes candidate fix via L6-PROOF + Pi/Sigma
Stage 4: EMPIRICAL VALIDATION -- ship fix-spec to Testbed verification cell
Stage 5: INTEGRATION -- ingest verified fix via Phase-2-light + Phase-6 + CELL KP (DONE via KP P1+P4)
Stage 6: REGRESSION CHECK -- cap_map scorecard delta; if drop -> revert

LOOP back to Stage 1.

## Stage 1+2 SPEC -- substrate_query.py extensions

### substrate_query.py find-relevant-knowledge

```python
#!/usr/bin/env python3
"""
substrate_query.py find-relevant-knowledge <about> [--top-k=10] [--max-depth=3]

Poll substrate's OWN ingested knowledge for atoms + edges + algebra-dicts relevant to a topic.
Stage 2 of recursive self-improvement loop.

Search strategy: bge-cosine prefilter + SHARES_MATH expansion + DEPENDS_ON walk + L6-PROOF reachability.
Returns ranked candidates with substrate-provenance trail.
"""
import argparse
import json
from collections import defaultdict


def cmd_find_relevant_knowledge(args):
    about = args.about
    top_k = args.top_k
    max_depth = args.max_depth

    # Stage 2A: bge-cosine prefilter (semantic similarity)
    query_vec = encode_with_bge(about)  # use pre-computed substrate bge encoder
    semantic_top_k = substrate.bge_top_k(query_vec, k=top_k * 5)  # cast wider net

    # Stage 2B: algebra-dict keyword match (structural similarity)
    keywords = extract_keywords(about)  # tokenize + filter stop words
    algebra_matches = []
    for kw in keywords:
        algebra_matches.extend(substrate.algebra_dict_search(kw, partition_filter=None))
    
    # Stage 2C: SHARES_MATH expansion (categorical-equivalence)
    expanded = set()
    for atom_id in [a.id for a in semantic_top_k] + [a.id for a in algebra_matches]:
        expanded.update(substrate.shares_math_neighbors(atom_id))
        expanded.add(atom_id)
    
    # Stage 2D: DEPENDS_ON + USES walk (typed-inference reachability)
    reachable = expanded.copy()
    for depth in range(max_depth):
        new_reachable = set()
        for atom_id in reachable:
            new_reachable.update(substrate.predecessors_via_edge_types(
                atom_id, edge_types=["DEPENDS_ON", "USES", "INSTANCE_OF", "SPECIALIZES", "DEFINED_OVER", "SHARES_MATH"]
            ))
        reachable.update(new_reachable)
    
    # Stage 2E: L6-PROOF reachability scoring (if atom_id has provable derivation, boost relevance)
    scored = []
    for atom_id in reachable:
        atom = substrate.lookup_atom(atom_id)
        proof_score = 0.0
        proof_result = substrate.prove(atom_id, max_depth=max_depth, cos_floor=0.30)
        if proof_result.get("status") == "PROVED":
            proof_score = proof_result.get("proof_score", 0.0)
        
        # Combined relevance score
        bge_cos = compute_bge_cosine(query_vec, atom.bge_vec)
        algebra_score = sum(1 for kw in keywords if kw.lower() in str(atom.algebra_dict).lower())
        shares_math_boost = 0.1 * (1 if atom_id in expanded else 0)
        
        relevance = 0.5 * bge_cos + 0.2 * (algebra_score / max(1, len(keywords))) + 0.2 * proof_score + 0.1 * shares_math_boost
        scored.append({
            "atom": atom.canonical_name,
            "tier": atom.tier,
            "partition": atom.partition,
            "relevance": relevance,
            "bge_cos": bge_cos,
            "algebra_match_count": algebra_score,
            "proof_score": proof_score,
            "shares_math_neighbor": atom_id in expanded,
            "algebra_dict_snippet": str(atom.algebra_dict)[:300],
        })
    
    # Top-k by relevance
    scored.sort(key=lambda x: -x["relevance"])
    return {
        "about": about,
        "query_vec_norm": float(np.linalg.norm(query_vec)),
        "expanded_atom_count": len(reachable),
        "top_k": scored[:top_k],
    }


def encode_with_bge(text):
    """Reuse pre-computed substrate bge encoder; do not recompute."""
    return substrate.bge_encode(text)


def extract_keywords(text):
    """Tokenize + filter stop words; substrate-native"""
    tokens = text.lower().split()
    stop_words = {"the", "a", "an", "is", "are", "and", "or", "to", "of", "in", "for", "on", "with"}
    return [t for t in tokens if t not in stop_words and len(t) > 2]
```

### substrate_query.py compose-fix

```python
#!/usr/bin/env python3
"""
substrate_query.py compose-fix <issue> --candidates K1,K2,... [--max-fix-depth=5]

Compose candidate substrate-internal fix-spec from polled knowledge using L6-PROOF + Pi/Sigma.
Stage 3 of recursive self-improvement loop.

Returns structured fix-spec JSON: which atoms to add / which edges to rewire / which cleanup parameters to tune.
"""
def cmd_compose_fix(args):
    issue = args.issue
    candidates = args.candidates.split(",")
    max_fix_depth = args.max_fix_depth

    # Step 1: parse the issue into structural form
    issue_atoms = parse_issue_to_atoms(issue)  # e.g. "A-axis F1 dropped 0.05" -> {axis: "A", metric: "F1", delta: -0.05}

    # Step 2: for each candidate, build proof of "candidate atom RESOLVES issue atom"
    fix_specs = []
    for candidate_name in candidates:
        candidate = substrate.lookup_atom(candidate_name)
        if not candidate: continue

        # Step 2A: L6-PROOF backward-chaining over generalized typing context
        proof_paths = []
        for issue_atom in issue_atoms:
            proof_result = substrate.prove_with_seed(
                goal=issue_atom,
                seed_atom=candidate,
                max_depth=max_fix_depth,
                cos_floor=0.30,
                edge_types_typed_inference=["DEPENDS_ON", "USES", "INSTANCE_OF", "SPECIALIZES", "DEFINED_OVER", "SHARES_MATH"],
            )
            if proof_result.get("status") == "PROVED":
                proof_paths.append(proof_result)

        if not proof_paths:
            continue  # candidate cannot resolve issue via L6-PROOF

        # Step 2B: synthesize fix-spec from proof paths
        fix_spec = {
            "candidate_atom": candidate.canonical_name,
            "issue_resolved": [p["goal"] for p in proof_paths],
            "structural_changes": synthesize_structural_changes(proof_paths, candidate),
            "estimated_macro_impact": estimate_macro_impact(proof_paths, issue_atoms),
            "regression_risk_axes": identify_risk_axes(candidate, issue_atoms),
            "pre_reg_HARD_PASS": pre_reg_threshold(proof_paths),
        }
        fix_specs.append(fix_spec)

    # Step 3: rank fix-specs by estimated impact + safety
    fix_specs.sort(key=lambda f: (f["estimated_macro_impact"], -len(f["regression_risk_axes"])), reverse=True)
    return {
        "issue": issue,
        "candidate_count": len(candidates),
        "fix_spec_count": len(fix_specs),
        "top_fix_specs": fix_specs[:5],
    }


def synthesize_structural_changes(proof_paths, candidate):
    """Convert proof paths to structural change spec (which edges to add / which atoms to promote)."""
    changes = {
        "atoms_to_add": [],
        "edges_to_add": [],
        "tier_promotions": [],
        "cleanup_param_tweaks": {},
    }
    for path in proof_paths:
        # Walk proof tree; identify which edges are "implicit but unauthored"
        edges_in_proof = walk_proof_tree_for_edges(path)
        for edge in edges_in_proof:
            if not substrate.has_edge(edge["src"], edge["dst"], edge["rel"]):
                changes["edges_to_add"].append(edge)
    return changes


def estimate_macro_impact(proof_paths, issue_atoms):
    """Estimate +macro F1 delta from applying fix-spec."""
    return sum(p["proof_score"] for p in proof_paths) * 0.01  # heuristic; calibrate empirically


def identify_risk_axes(candidate, issue_atoms):
    """Identify which substrate axes might regress if fix-spec applied."""
    serves_caps = candidate.serves_capability
    risk_axes = []
    for axis in ["A", "B", "C", "D", "E", "F", "G"]:
        if any(axis.lower() in cap.lower() for cap in serves_caps):
            continue  # candidate already serves this axis; low risk
        if any(check_axis_overlap(axis, issue_atom) for issue_atom in issue_atoms):
            risk_axes.append(axis)
    return risk_axes


def pre_reg_threshold(proof_paths):
    """Define HARD-PASS threshold per drill cell convention."""
    return {
        "macro_F1_lift": ">= 0.005",
        "axis_lift_specific": "+0.01 on issue axis",
        "regression_check": "no other axis drops > -0.005",
    }
```

## Estimated LOC + cost

- substrate_query.py find-relevant-knowledge: ~150 LOC
- substrate_query.py compose-fix: ~200 LOC
- Total: ~350 LOC; ~1-2 day Testbed/Exp-Dev build
- Cell verification: integration test against 10 known cap_map issues (~1 day)

## Composition with existing 5 substrate_query.py subcommands

```
substrate_query.py verify                       -- CHTV-1 type-checker (1.0 precision; shipped)
substrate_query.py prove                        -- L6-PROOF backward-chaining (shipped; 6-edge typing context)
substrate_query.py find                         -- L6-PROOF FINDER (sound prover; shipped 20/20 HARD-PASS)
substrate_query.py pi                           -- Pi-type construction (SPEC pending implementation)
substrate_query.py sigma                        -- Sigma-type construction (SPEC pending implementation)
substrate_query.py id-type                      -- Identity-type via SHARES_MATH (SPEC pending implementation)
substrate_query.py find-relevant-knowledge      -- Stage 2 of recursive self-improvement loop (THIS SPEC)
substrate_query.py compose-fix                  -- Stage 3 of recursive self-improvement loop (THIS SPEC)
```

8 substrate_query.py subcommands together = substrate-as-Curry-Howard-categorical-type-theory + self-improvement engine.

## Pre-reg HARD-PASS for Stage 1+2 implementation

- find-relevant-knowledge: given 10 test queries (e.g. "C-axis serves_capability backfill"), top-k returns relevant atoms with >= 0.6 manual relevance gold; expanded atom count >= 50 (sufficient breadth)
- compose-fix: given 10 known cap_map issues + relevant atoms from find, returns at least 1 fix-spec per issue with HARD-PASS threshold defined; manual review shows >= 5 of 10 fix-specs would plausibly improve macro
- Integration test: end-to-end Stage 1 -> Stage 2 -> Stage 3 on 10 cap_map issues; 1 fix-spec ships through Testbed verification cell + passes empirical HARD-PASS

## Routing

- **Testbed**: substrate_query.py find-relevant-knowledge + compose-fix implementation candidate (~1-2 days); composes with existing verify + prove + find
- **Exp-Dev**: Stage 4 verification cell scope (test 10 cap_map issues end-to-end through recursive loop)
- **Research**: filing this spec; standing for ship verdicts; Stage 4-6 spec on demand (Phase 3+ of MASTER PLAN)

## Cross-references

- notes/research_drill_optimal_external_corpus_to_VSA_HRR_substrate_ingest_methodology_knowledge_promotion_mechanism_3x_2026-06-13.md (3x drill source; recursive loop architecture)
- notes/research_to_testbed_exp_dev_MASTER_PLAN_*.md (Phase 2 R2.1 deliverable)
- notes/research_to_testbed_exp_dev_USER_VISION_*.md (USER vision substrate-on-all-knowledge)
- memory `substrate-CELL-KP-knowledge-promotion-operator-P1-P4-HARD-PASS-2026-06-13` (Stage 5 INTEGRATION via KP operator)

---

**Testbed + Exp-Dev:** RECURSIVE SELF-IMPROVEMENT LOOP Stage 1+2 SPEC + substrate_query.py find-relevant-knowledge ~150 LOC + compose-fix ~200 LOC = ~350 LOC total + 1-2 day build + composes with existing verify + prove + find subcommands + Stages 3-6 spec on demand + Stage 5 INTEGRATION operational via KP operator (P1 + P4 HARD-PASS) + Stage 1+2 closes USER vision substrate-polls-knowledge-base-for-fixes + LLM categorical gap NO recursive structural self-improvement possible + 8 substrate_query.py subcommands together = substrate-as-Curry-Howard-categorical-type-theory + self-improvement engine + Phase 2 R2.1 deliverable per MASTER PLAN + USER full-auto overnight continuing.
