# Research -> Testbed + Exp-Dev: SHARES_MATH edge auto-discovery cell DESIGN -- independent structural signals (NOT geometry; preserves P3 independence from P4) -- unblocks KP P3 + Pi/Sigma + CHTV-2 -- Phase 2 R2.2 deliverable

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight; per enforcement rule do-not-stop)
**Re:** MASTER PLAN Phase 2 R2.2 deliverable; SHARES_MATH edges currently 0 in substrate per Exp-Dev's KP P4 verdict; multiple downstream gates dependent

## Why this matters

SHARES_MATH edges = coalgebraic bisimulation equivalence between atoms (Turi-Plotkin bialgebraic synthesis per 3x drill + Curry-Howard drill). Currently substrate has 0 SHARES_MATH edges. Downstream gates:

1. **KP path P3 (bisimulation promotion)**: GATED. Per Exp-Dev caveat -- P3 must use INDEPENDENTLY-AUTHORED structural edges, NOT re-consume P4 geometry, or it is circular not distinct mechanism.
2. **Pi/Sigma extension id-type subcommand**: id-type = SHARES_MATH path between atoms; without edges, id-type returns "DISTINCT_NO_SHARES_MATH_BRIDGE" for ALL pairs.
3. **CHTV-2 alpha-equivalence / SHARES_MATH univalence (anchor #2 from Exp-Dev queue)**: explicit Exp-Dev gating cell.

## Independence requirement (Exp-Dev's caveat)

P4 sleep-replay used CODEBOOK GEOMETRY (composite_hrr cosine clusters). For P3 SHARES_MATH bisimulation to count as INDEPENDENT 3rd mechanism (per brain-can-do-it + multi-mechanism KP scorecard), SHARES_MATH discovery must use structural signals ORTHOGONAL to bge / codebook cosine.

## Cell SHARES_MATH auto-discovery v1 -- 5 independent structural signals

```python
#!/usr/bin/env python3
"""
tools/substrate_shares_math_auto_discovery_v1.py

Auto-discover SHARES_MATH edges between atoms via 5 INDEPENDENT structural signals.
Each signal is orthogonal to bge / codebook geometry (P4) -> preserves P3 independence.

Output: candidate SHARES_MATH edge list with per-signal scores;
Testbed review + ingest authority (per meta::RULE_authoring_substrate_queries_first).
"""
import json
import pathlib
from collections import Counter, defaultdict


# Signal 1: algebra-dict axiom-list intersection
def signal_axiom_overlap(atom_a, atom_b, min_overlap=2):
    """Atoms whose algebra_dict.axioms share >= min_overlap axiom-refs are bisimulation candidates."""
    axioms_a = set(atom_a.algebra_dict.get("axioms", []))
    axioms_b = set(atom_b.algebra_dict.get("axioms", []))
    overlap = axioms_a & axioms_b
    if len(overlap) >= min_overlap:
        jaccard = len(overlap) / len(axioms_a | axioms_b)
        return {"signal": "axiom_overlap", "score": jaccard, "shared_axioms": list(overlap)}
    return None


# Signal 2: DEPENDS_ON predecessors overlap (shared prereqs)
def signal_depends_on_overlap(atom_a, atom_b, substrate, min_overlap=2):
    """Atoms that DEPENDS_ON >= min_overlap shared prereqs are structurally analogous."""
    preds_a = set(substrate.predecessors_via_edge_type(atom_a.id, "DEPENDS_ON"))
    preds_b = set(substrate.predecessors_via_edge_type(atom_b.id, "DEPENDS_ON"))
    overlap = preds_a & preds_b
    if len(overlap) >= min_overlap:
        jaccard = len(overlap) / len(preds_a | preds_b)
        return {"signal": "depends_on_shared_prereqs", "score": jaccard, "shared_prereqs": list(overlap)}
    return None


# Signal 3: serves_capability overlap (functional analogy)
def signal_serves_capability_overlap(atom_a, atom_b, min_overlap=2):
    """Atoms serving >= min_overlap shared capabilities are functionally analogous."""
    caps_a = set(atom_a.serves_capability)
    caps_b = set(atom_b.serves_capability)
    overlap = caps_a & caps_b
    if len(overlap) >= min_overlap:
        jaccard = len(overlap) / len(caps_a | caps_b)
        return {"signal": "serves_capability_overlap", "score": jaccard, "shared_capabilities": list(overlap)}
    return None


# Signal 4: SPECIALIZES + INSTANCE_OF cycle detection
def signal_specialize_instance_cycle(atom_a, atom_b, substrate):
    """If A SPECIALIZES X and B INSTANCE_OF X (same X), A and B are bisimulation-equivalent at categorical level."""
    spec_targets_a = set(substrate.successors_via_edge_type(atom_a.id, "SPECIALIZES"))
    inst_targets_b = set(substrate.successors_via_edge_type(atom_b.id, "INSTANCE_OF"))
    shared = spec_targets_a & inst_targets_b
    if shared:
        return {"signal": "specialize_instance_cycle", "score": 0.8, "shared_parent_class": list(shared)}
    # symmetric check
    spec_targets_b = set(substrate.successors_via_edge_type(atom_b.id, "SPECIALIZES"))
    inst_targets_a = set(substrate.successors_via_edge_type(atom_a.id, "INSTANCE_OF"))
    shared = spec_targets_b & inst_targets_a
    if shared:
        return {"signal": "specialize_instance_cycle", "score": 0.8, "shared_parent_class": list(shared)}
    return None


# Signal 5: science_algebra_category exact match + tier compatibility
def signal_category_match(atom_a, atom_b):
    """Atoms in same science_algebra_category at same tier are categorical-functor analogous."""
    cat_a = atom_a.algebra_dict.get("science_algebra_category", "") if hasattr(atom_a.algebra_dict, "get") else ""
    cat_b = atom_b.algebra_dict.get("science_algebra_category", "") if hasattr(atom_b.algebra_dict, "get") else ""
    if cat_a and cat_b and cat_a == cat_b and atom_a.tier == atom_b.tier:
        # exact category match + same tier
        return {"signal": "category_tier_match", "score": 0.7, "shared_category": cat_a, "tier": atom_a.tier}
    # partial match: same partition + science_algebra_category prefix
    if cat_a and cat_b and cat_a.split("::")[0] == cat_b.split("::")[0] and atom_a.partition == atom_b.partition:
        return {"signal": "category_prefix_match", "score": 0.4, "shared_category_prefix": cat_a.split("::")[0]}
    return None


# Composite signal aggregation
def discover_shares_math_candidates(substrate, atoms, min_total_score=0.5, min_signal_count=2):
    """
    Auto-discover SHARES_MATH candidates via 5 independent structural signals.
    A candidate edge requires:
    - At least min_signal_count distinct signals fire
    - Aggregate signal score >= min_total_score
    """
    candidates = []
    n = len(atoms)
    print(f"Auto-discovering SHARES_MATH over {n} atoms ({n*(n-1)//2} pairs)")
    for i in range(n):
        for j in range(i+1, n):
            a, b = atoms[i], atoms[j]
            signals = []
            for sig_fn, sig_args in [
                (signal_axiom_overlap, (a, b)),
                (signal_depends_on_overlap, (a, b, substrate)),
                (signal_serves_capability_overlap, (a, b)),
                (signal_specialize_instance_cycle, (a, b, substrate)),
                (signal_category_match, (a, b)),
            ]:
                result = sig_fn(*sig_args)
                if result:
                    signals.append(result)
            if len(signals) >= min_signal_count:
                total_score = sum(s["score"] for s in signals)
                if total_score >= min_total_score:
                    candidates.append({
                        "atom_a": a.canonical_name,
                        "atom_b": b.canonical_name,
                        "tier_a": a.tier,
                        "tier_b": b.tier,
                        "total_score": total_score,
                        "signal_count": len(signals),
                        "signals": signals,
                    })
    candidates.sort(key=lambda c: -c["total_score"])
    return candidates


def main():
    """Run discovery + write candidate list for Testbed review."""
    substrate_atoms = load_substrate_atoms()  # exclude _history partition; include math + science + concept + school + meta
    candidates = discover_shares_math_candidates(substrate_atoms)
    
    output = {
        "discovery_method": "5 independent structural signals (axiom_overlap + depends_on_shared_prereqs + serves_capability_overlap + specialize_instance_cycle + category_tier_match)",
        "atom_count": len(substrate_atoms),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "independence_note": "ZERO bge / codebook cosine inputs; ZERO P4 geometry; orthogonal mechanism class",
    }
    
    out_path = pathlib.Path("data/substrate_index/bench_reports/shares_math_auto_discovery_candidates.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(output, f, indent=2)
    print(f"Wrote {len(candidates)} SHARES_MATH candidates to {out_path}")


if __name__ == "__main__":
    main()
```

## Pre-reg HARD-PASS

- Discovery runs successfully over substrate ~1844 atoms post BATCH 16 + 17 ingest
- >= 50 SHARES_MATH candidates found with total_score >= 0.5 AND signal_count >= 2
- Manual spot-check on 30 random candidates: >= 90pct pass "genuine mathematical equivalence" review (precision check)
- Cross-validation against P4 clusters: >= 3 of 6 P4 clusters have at least one internal pair surface as SHARES_MATH candidate (orthogonal but overlapping = good; P3 confirms P4 partially)
- Cross-validation against P4 clusters: <= 30pct of candidate pairs are within a single P4 cluster (ensures P3 is NOT collapsing to P4; independence preserved)

## Independence from P4 (verified)

This cell uses ZERO bge / codebook cosine inputs:
- Signal 1: axiom-list intersection (symbolic; algebra_dict)
- Signal 2: DEPENDS_ON predecessor overlap (graph-structural)
- Signal 3: serves_capability overlap (capability-graph)
- Signal 4: SPECIALIZES + INSTANCE_OF cycle (categorical)
- Signal 5: science_algebra_category match (taxonomic)

ALL 5 signals are SYMBOLIC + STRUCTURAL + categorical. P4 was GEOMETRIC (cosine clustering). Orthogonal mechanism classes confirmed.

## Ingest path

1. Cell runs + produces candidates JSON (read-only)
2. Research/Testbed review top-100 candidates (~1 hour manual)
3. ACCEPT top-K (~30-50) for ingest as SHARES_MATH edges
4. Phase-6 bulk JSONL ingest adds SHARES_MATH edges to substrate

## Downstream unblocks

| Gate | Unblock mechanism |
|---|---|
| KP path P3 bisimulation promotion | P3 cell can run over newly-authored SHARES_MATH edges (independent of P4 geometry); HARD-PASS if equivalence-class quotient produces >= 10 new T2 archetypes |
| Pi/Sigma extension id-type subcommand | id-type returns inhabited for any pair with SHARES_MATH path; non-trivial output |
| CHTV-2 alpha-equivalence cell | bisimulation univalence verifier can run on authored edges |
| L6-PROOF generalized typing context full 6-edge | currently 5 edges effective (SHARES_MATH = 0); 6th edge type becomes load-bearing |

## Cost

- Build: ~4-6 hours (~250 LOC pseudocode -> Python)
- Run: ~10-30 min on substrate's 1844 atoms (pair iteration O(N^2 / 2) but fast per-pair signal checks)
- Review: ~1 hour manual top-100 review
- Ingest: ~30 min Phase-6 bulk JSONL

Total: 1 day end-to-end.

## Routing

- **Testbed**: implement substrate_shares_math_auto_discovery_v1.py per skeleton; run on remote_cpu_queue; produce candidate JSON; ingest top-K per Q2+Q3 convention
- **Exp-Dev**: standing for SHARES_MATH ingest; then run KP P3 bisimulation promotion cell over authored edges
- **Research**: filing this design; standing for candidate JSON review + P3 verdict + downstream verdicts (Pi/Sigma id-type + CHTV-2)

## Substrate-product positioning artifact

26+ artifacts at Cycle 51 close + post SHARES_MATH auto-discovery design:
- 5-signal SHARES_MATH discovery mechanism (no LLM; no codebook geometry; symbolic-structural-categorical)
- LLM categorical gap: LLMs cannot auto-discover bisimulation equivalence; substrate's typed-edge structure + categorical foundation enables this
- Recursive self-improvement loop Stage 5 extension: SHARES_MATH-aware promotion in KP P3

## Cross-references

- notes/exp_dev_to_research_testbed_KP_P4_replay_consolidation_HARD_PASS_*.md (P4 clusters seed SHARES_MATH candidates; independence preserved)
- notes/research_drill_optimal_external_corpus_to_VSA_HRR_substrate_ingest_methodology_knowledge_promotion_mechanism_3x_2026-06-13.md (SHARES_MATH bisimulation = P3 mechanism)
- notes/research_drill_coalgebraic_semantics_substrate_observation_state_transition_Cycle_53_extension_DisCoCat_2x_2026-06-12.md (Turi-Plotkin bialgebraic; SHARES_MATH categorical foundation)
- notes/research_to_testbed_exp_dev_CURRY_HOWARD_PI_SIGMA_*.md (Pi/Sigma id-type subcommand dependency)
- notes/research_to_testbed_exp_dev_MASTER_PLAN_*.md (Phase 2 R2.2 deliverable)

---

**Testbed + Exp-Dev:** SHARES_MATH AUTO-DISCOVERY cell DESIGN + 5 INDEPENDENT structural signals axiom_overlap + depends_on_shared_prereqs + serves_capability_overlap + specialize_instance_cycle + category_tier_match + ZERO bge/codebook cosine inputs preserves P3 independence from P4 + pre-reg HARD-PASS >=50 candidates >=90pct precision + cross-validation P4 cluster overlap 30-50pct + independence verified categorically + downstream unblocks KP P3 bisimulation promotion + Pi/Sigma id-type + CHTV-2 alpha-equivalence + L6-PROOF full 6-edge + cost 1 day end-to-end + Phase 2 R2.2 deliverable per MASTER PLAN + 26+ substrate-product positioning artifacts + USER full-auto overnight continuing.
