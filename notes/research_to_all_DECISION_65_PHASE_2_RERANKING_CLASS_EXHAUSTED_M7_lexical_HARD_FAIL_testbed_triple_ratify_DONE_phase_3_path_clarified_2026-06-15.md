# Research (Director) -> ALL: DECISION 65 -- Phase 2 RERANKING MECHANISM CLASS exhausted (M7 lexical HARD_FAIL closes the last variant; bge already captures lexical; deeper realization = reranking has NO ROOM on new concepts because bge is near-optimal); Testbed TRIPLE RATIFY DONE (DECISIONS 54 + 49c + 49a; R3 PASS; substrate 26272 -> 26286 atoms / 5231 -> 5263 relations); 40th honest finding closes Phase 2; Phase 3 path CRYSTALLIZED (the 3 dispatched drills + Skunkworks edge-proposal audit are precisely Phase 3 PREP)

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~09:20
**Re:** Exp-Dev M7 result + Testbed triple ratify (both commits pending). 40th honest finding. Per USER overnight full-auto + auto mode + USER strategic-research dispatch.

## ACK -- Testbed TRIPLE RATIFY DONE

Testbed cleared the entire queue from STATUS_REQUEST (~14.5h after my ping):
- **DECISION 54 RELABEL:** 5475/5510 wikidata atoms updated in-place; spot-check `wikidata_Q182505` aliases now include "Bayes' theorem"; R2 clean
- **DECISION 49c:** 14 qclass atoms + 14 SPECIALIZES edges to category_type; closes 5133 dangling DEPENDS_ON edges
- **DECISION 49a:** 12 SHARES_MATH bridges (18 symmetric; 9 new + 6 already-existing; 1 weak-flagged retained per Skunkworks discipline)
- **R3 invariants PRESERVED:** 213/213 axiom termination + capability_preservation=1.0 + Tier 1+2 modules execute
- **Substrate state delta:** atoms 26272->26286 (+14); relations 5231->5263 (+32)

Excellent Testbed delivery. Phase 2 ingest substrate-state-mutation work is COMPLETE.

## ACK -- 40th honest finding (M7 lexical HARD_FAIL + deeper realization)

Exp-Dev ran M7 lexical (question-conditional lexical reweight of bge top-K; dev-tuned, no held-out Goodhart):
- DEV (q01-q53): best delta=0.05 lifted 0.233 -> 0.254 (helps on dev)
- TRANSFER q54-q65: bge 0.148 -> M7 0.148 (+0.000 unchanged)
- TRANSFER 56d (new concepts): bge 0.217 -> M7 0.194 (-0.023 HURTS)
- HARD_FAIL. Dev lift does not transfer; on new concepts, lexical M7 actively hurts.

**Why (Exp-Dev's diagnosis):** bge already captures lexical content-term overlap. M7 lexical double-counts + adds noise on questions where the lexically-overlapping atom is NOT gold.

## DEEPER REALIZATION (Exp-Dev's substrate-architectural insight; the SHARPEST framing yet)

ALL reranking mechanisms (M4d / M6 / M7) re-rank the bge top-K pool. A reranker can lift F1 ONLY if:
(a) the gold is IN the pool but bge-ranked-low, AND
(b) the reranker has a signal that PROMOTES it over distractors

**On 56d (new concepts):**
- bge baseline is already 0.217 (textbook-style Q matches atom name/desc well; bge is NEAR-OPTIMAL on the candidate pool)
- ROOM for any reranker to exceed bge is SMALL by construction
- Graph signal absent (new concepts graph-sparse)
- Lexical signal redundant (bge captures)
- Proof signal flat (97pct axiom-terminating)

**On q54-q65 (in-distribution):**
- bge baseline 0.148 (substrate-self-knowledge-style Q is HARD for bge -- big room)
- Gold atoms are graph-rich (M4d has signal)
- M4d +0.124 lift is the consequence

**Conclusion:** the substrate-internal RERANKING MECHANISM CLASS is structurally limited to amplifying questions where bge is wrong AND the substrate has orthogonal signal. New-concept retrieval has neither condition.

## DECISION 65a -- Phase 2 RERANKING CLASS DECLARED EXHAUSTED (with mechanism-architectural reason)

```
PHASE 2 MECHANISM EXPLORATION (final compressed state)
  
  WORKS (substrate's distinctive capability):
    M4d sparse consensus graph walk        IN-DISTRIBUTION +0.124 (0.148 -> 0.272)
    
  MECHANISM CLASSES EXHAUSTED (with structural reasons):
    Graph augmentation (PRF/49a/proof/normalize/density-aware)
      -- structural: dilution; selectivity is load-bearing
    Reranking (M6 proof / M7 lexical)
      -- structural: bge near-optimal on textbook-style Q; no room
    Manual edge authoring as generalization test (55a/56d-v2)
      -- structural: connect-the-atom, not generalization (Skunkworks 39th)
  
  REMAINING (Phase 2; in flight):
    M7 type-match variant (LOW-ODDS per Exp-Dev; cheap try IF non-LLM type-extractor; OPTIONAL)
    55a substrate-completeness extension (Skunkworks; routine; not a generalization test)
    51c M4d re-run on enriched graph (UNBLOCKED by Testbed; measure in-distribution lift; ~30 min)
    49b real-groups re-run (UNBLOCKED; cheap; substrate diagnostic)
    Skunkworks Auditor post-ratify gate (axiom termination + capability_preservation across 46a+49a+49c)
  
  REMAINING (Phase 3; the new central question):
    AUTONOMOUS edge-discovery / CO-EVOLVE-1 -- substrate proposes + verifies + integrates edges
      without LLM (11th rule); enables new-concept generalization
```

## DECISION 65b -- Phase 3 PATH CRYSTALLIZED

USER's strategic question "what are we trying to do and how can we make it work?" -- answered by the M7 result + the deeper realization:

**The thing we are trying to do:** make substrate AUTONOMOUSLY grow its own typed-operator graph around new concepts, so that M4d's amplifier (already proven for in-distribution) extends to ANY concept once its neighborhood is grown. WITHOUT LLM in the operator core (11th rule).

**How to make it work (the 3-component research program; ALREADY DISPATCHED):**

1. **3x deep literature drill (in flight; ETA ~15-30 min):** non-LLM autonomous KG completion / rule mining / pattern-based ontology learning -- what mechanisms work without LLM, and what are the soundness guarantees?
2. **2x deep literature drill (in flight; ETA ~15-30 min):** self-improving / bootstrap / co-evolution architectures -- what's the proven shape of an autonomous loop that doesn't collapse?
3. **Skunkworks substrate-internal design cell (dispatched; ETA ~2-3 hrs):** audit substrate's existing primitives (bge-similarity / L6-PROOF / type-signature / co-occurrence / foundation-primitive) for sound edge proposal; report precision / FP rate / type-coverage on a small witness set

**After all 3 return:** Director synthesizes Phase 3 CO-EVOLVE-1 architectural spec. THIS is the substrate's path forward.

## DECISION 65c -- Phase 2 close-out work (parallel; Exp-Dev bandwidth)

While Phase 3 prep is in flight, complete the Phase 2 hygiene:
1. **51c M4d re-run on enriched graph** (~30 min Exp-Dev): measure in-distribution lift from +14 atoms + +32 edges; expected lift on q54-q65 modest (atoms are orthogonal to held-out concepts) but corroborates the substrate-completeness claim
2. **49b real-groups re-run** (~30 min Exp-Dev): now that wikidata atoms are bge-distinguishable, do real granular SHARED_ABSTRACTION groups emerge? cheap diagnostic
3. **Optional M7 type-match variant** (Director DEFER per Exp-Dev's low-odds estimate; only if cheap non-LLM type-extractor available)
4. **Skunkworks Auditor post-ratify gate** (per Skunkworks's stated commitment; verify axiom termination + capability_preservation across 46a + 49a + 49c)

## DECISION 65d -- substrate-product positioning SHARPEST yet (6-claim package now)

Adding to the 5-claim package from DECISION 64:

**Claim 6 (mechanism-class architectural limit):** "The substrate's reranking mechanism class (M4d/M6/M7) amplifies questions where bge is bge-hard AND substrate has orthogonal signal (e.g. typed-graph density). On textbook-style new-concept questions where bge is near-optimal AND substrate's graph signal is absent, reranking has structurally no room. The substrate's distinctive capability is therefore for IN-DISTRIBUTION CONCEPT AMPLIFICATION; new-concept retrieval is bge-baseline 0.217 (Phase 3 will address via autonomous graph-growth)."

The substrate-product positioning is now ARCHITECTURALLY CHARACTERIZED. The "what M4d does" + "what M4d doesn't do" + "what extension protocol" + "what Phase 3 question" + "what mechanism-class limit" framing is complete and defensible.

## Session tally

65 cumulative decisions. 40 honest signals (Auditor 13 + Prover 24 + Director 3). The substrate's three-role discipline has produced an unusually clean substrate-product characterization in one session:
- 1 mechanism that works (M4d sparse-consensus +0.124 in-distribution)
- 3 mechanism classes exhausted (augmentation; reranking; manual-author-as-generalization)
- 4 measurement-refutes-prediction events (PRF; M6 proof; normalize-leverage; structural-VOID design)
- 2 honest size caveats (n=7; 9/14 dev-overlap)
- 1 deep architectural insight (reranking room shrinks where bge is near-optimal)
- Substrate-product positioning gains 6 distinct claims, each measured and characterized

## Cross-references

- Testbed TRIPLE RATIFY (this commit responds): pending commit
- Exp-Dev M7 lexical HARD_FAIL (this commit responds): pending commit
- DECISION 64 (Option A 55a reframe): commit `d37b210a`
- DECISION 63 (Option 1 + 56d-v2): commits `e513fe8a` + `badc5cd1`
- DECISION 62 (decisive 56d): commit `c52e126a`
- DECISION 60 (graph-walk exhausted): commit `8ce78073`
- Phase 3 design cell + 2 lit drills: commit `76302db1`

## Safety / invariants

- ASCII only
- 11th rule (substrate-on-its-own): Phase 3 research focuses on non-LLM autonomous extension
- 22nd rule (held-out DO-NOT-INGEST): preserved across triple ratify (R2 clean per Testbed)
- 15th rule (commit-and-reveal): 56d + 56d-v2 SHA-locked
- 18th rule (refuse-what-cannot-prove): substrate refuses M7 lexical claim (HARD_FAIL)
- 19th rule: substrate continues to update honestly per measurement
- 100pct axiom termination + capability_preservation=1.0 preserved

---

**ALL three roles:**
- **Exp-Dev (Prover):** ACK 40th honest finding (deepest mechanism-architectural insight of session); dispatch 51c M4d re-run on enriched graph (~30 min) + 49b real-groups re-run (~30 min) in parallel; M7 type-match variant OPTIONAL (defer); standby for Phase 3 dispatch when 3 research outputs return.
- **Skunkworks (Auditor):** continue redesigned 55a substrate-completeness pass (per DECISION 64) AND substrate-internal edge-proposal primitives audit (per design cell dispatched commit 76302db1; ~2-3 hrs); plus post-ratify Auditor gate on 46a+49a+49c (axiom termination + capability_preservation verify).
- **Testbed (Integrator):** ratify queue CLEAR for now; future 55a substrate-completeness edges arrive when Skunkworks delivers.

Tag: PHASE_2_RERANKING_EXHAUSTED_TRIPLE_RATIFY_DONE_PHASE_3_PATH_CRYSTALLIZED -- Research (Director)
