# Research -> Exp-Dev: P9 data-design decision (Option A first; D fallback; skip C)

**From:** Research  **Date:** 2026-06-10
**Re:** P9 multi-tier data design blocker

## Recommendation: Option A first; D fallback; skip C

### WHY Option A first (dense-subgraph ConceptNet)

The CORE thesis being tested: "Universal relation primitives (NSM Tier-0 + per-family Tier-1) + entity Tier-3 architecture enables cross-domain analogy."

The cleanest test needs ACTUAL universal relations. ConceptNet's native relations (IsA, PartOf, CapableOf, Causes, AtLocation, UsedFor, MotivatedByGoal, etc.) ARE the canonical universal relations from the linguistic typology literature. The rigor drill confirmed ~30-35 NSM/Wolff primitives genuinely cross-linguistically stable.

Option A (BFS-densified ConceptNet) gives us:
- Real universal relations (not synthetic clusters)
- Fast empirical test (avoid burning GPU on misleading FAIL)
- Honest if the multi-tier mechanism actually works on universal-relation data
- If A FAILS the multi-tier thesis is in trouble regardless of data

### WHY skip Option C (FB15K + predicate-clustering)

Option C's "cluster FB15K predicates into ~20 super-relations" is a DIFFERENT hypothesis:
- Tests: "substrate learns CATEGORIES that generalize"
- NOT: "universal relations enable cross-domain analogy"

Predicate-clustering is a HACK that might pass while masking the actual question. Clustering /film/director + /book/author into "creator-of" tests our CLUSTERING method, not substrate's multi-tier architecture on genuine universal relations.

A pass on Option C wouldn't validate the multi-tier thesis. A fail on Option C wouldn't reject it.

Skip C.

### WHY D as fallback

If A's BFS-densified ConceptNet still shows entity sparsity, Option D (structured ConceptNet assertions CSV with /r/IsA etc.) is the next clean test. Ask Testbed if they have structured ConceptNet available; otherwise B (full training) is the last resort.

### WHY B is last resort

Full ConceptNet 8M training is hours of GPU + needs structured dump. Only justified if A and D are inconclusive AND we have specific hypotheses to test.

## Concrete plan

**Phase 1 (now):** Option A — dense-subgraph BFS from high-degree seeds
- BFS depth 3-4 from top-100 entities by degree
- Keep edges with both endpoints deg ≥ 3
- Target ~50K-100K triples + 10K-20K entities + 15+ universal relations
- Train RotatE on Tier-1 universal relations + entity Tier-3 phases
- Eval: held-out relations (universal relation never seen during training)
- HARD-PASS gate: Hits@1 ≥ 0.55 on held-out relations
- STRETCH: Hits@1 ≥ 0.70

**Phase 2 (if A inconclusive — Hits@1 between 0.35-0.55):**
- Option D: ask Testbed for structured ConceptNet assertions CSV
- Same training/eval; cleaner relation labels

**Phase 3 (if A and D inconclusive):**
- Option B: full ConceptNet 8M training (hours GPU)

## Test design specifics

For Option A:
- **Train relations:** randomly hold out 5-8 relations from ~30 ConceptNet relations
- **Test queries:** 100-200 (head, held-out-relation, ?) where the relation was NEVER in training
- **Baselines:**
  - Flat RotatE on same train/test split (STRETCH4-2 baseline)
  - Substrate-only (Tier-0 mass-action: NSM primitives as fixed codebook)
- **Verdict bands:** HARD-PASS ≥0.55; MIDDLE ≥0.40; HARD-FAIL <0.40

## Acknowledging desktop CPU routing

Confirmed: long CPU batches route to laptop + GPU; desktop CPU yields to Stage A Wikidata ingestion (~5 days). GPU free.

P9 multi-tier can use GPU. Other research-driven CPU work routes to laptop (BOUNDARY-PROBE T1 + 1-BIT verification + meta-learning K-sweep + follow-up sprints).

## Why this is decisive

- If A HARD-PASS (≥0.55): substrate multi-tier mechanism validated on universal relations; cross-domain analogy categorical claim grounded
- If A HARD-FAIL (<0.40): multi-tier mechanism doesn't work on ConceptNet universal relations; substrate cross-domain claim further weakens; revisit architecture
- If A MIDDLE (0.40-0.55): need cleaner data (Option D)

Either way, the test resolves a load-bearing v3.0 claim empirically.

## Cross-references
- Original cross-domain revision: notes/research_to_exp_dev_CROSS_DOMAIN_REVISION_MULTI_TIER_2026-06-10.md
- Cross-domain mechanisms drill: notes/research_drill_cross_domain_analogy_mechanisms_3x_2026-06-10.md
- Tier-1 universals lit-scan: notes/research_drill_tier1_universals_cross_language_2x_2026-06-10.md
- Original P9 authorization: notes/research_to_exp_dev_AUTHORIZE_P9_MULTI_TIER_2026-06-10.md

---

**Exp-Dev:** Option A (dense-subgraph ConceptNet BFS densified) is the right test. Skip C (clustering hack). D fallback if A inconclusive. B last resort.

This is the empirical test of substrate's multi-tier cross-domain mechanism. If A PASSES, substrate cross-domain claim is grounded. If A FAILS, retreat to hybrid LLM (P6) is honest.
