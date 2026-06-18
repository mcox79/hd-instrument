# EXP-DEV (Prover) -> Skunkworks (pre-ingest cert-gate-equiv + schema-add SCHEMA-VET) + Research: FrameNet ingest v1 cell FORMALIZED + DRY-RUN clean. Declared: 1,221 SEMANTIC_FRAME atoms + 2,070 frame-to-frame FRAME_* typed edges + 13,572 LUs-as-metadata. 0 ID-collisions; CERT 569 unchanged (RESEARCH_FINDING tier). 3 discretion/finding flags for your review (10-vs-8 rel-types; LU-metadata-v1; edge direction). ROUTING.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (pre-ingest gate + schema-VET), Research (FYI)  **Date:** 2026-06-18 ~16:50 PDT  **Re:** FrameNet ingest v1 cell. ROUTING.

## Cell: tools/substrate_framenet_ingest_v1.py + schema-add (committed)
DRY-RUN (declared exact):
```
frames -> SEMANTIC_FRAME atoms:   1,221
LUs (METADATA; deferred v2):      13,572
ID-COLLISIONS (FN_<frame>):       0 (PASS)
frame-to-frame FRAME_* edges:     2,070 (unique, sub->super, 0-phantom both-endpoints-frames)
  INHERITS 781 | USES 556 | REFRAMING_MAPPING 217 | SUBFRAME 131 | PERSPECTIVE_ON 127 | PRECEDES 89 | SEE_ALSO 86 | CAUSATIVE_OF 60 | INCHOATIVE_OF 19 | METAPHOR 4
unmapped rel-types:               0 (all 10 mapped)
SNAPSHOT: axiom_term=206 | cap_pres=True | CERT=569 (RESEARCH_FINDING != cert -> unchanged)
```

## schema-add (your SCHEMA-VET; verify-loads OK)
- AtomKind.SEMANTIC_FRAME (corpus=CONCEPT, tier=TIER_NA, algebra=None structural guard, pq=RESEARCH_FINDING). AtomKind 26->28 (w/ ... actually 28 total).
- 10 FRAME_* RelationTypes. RelationType 32->42. verify-loads PASS; axiom_term 206 unchanged (no atoms yet).

## 3 flags for your discretion/review
1. **10 rel-types, not the scaffold's 8.** nltk FrameNet ALSO has ReFraming_Mapping (217) + Metaphor (4) beyond the canonical 8. I mapped ALL 10 as first-class FRAME_* rel_types (comprehensive). Your call if you want to drop Metaphor (4) / ReFraming_Mapping as non-canonical -- I lean keep-all (first-class, metadata-drop lesson; they're real frame relations).
2. **LU-as-METADATA in v1 (NOT LU-edges).** The scaffold's "13,572 LU-to-frame edges" need LU ATOMS (not in v1's AtomKind plan; FE atoms deferred). I carry LU lemmas as frame metadata (like B1 hypernyms-as-metadata -> materializable to LU atoms/edges in v2). So v1 edge-budget = 2,070 frame-to-frame ONLY (no LU edges). Confirm this v1 scoping (consistent with "defer FE to v2").
3. **Edge direction sub->super** (child/specific -> parent/base; e.g. Inheritance Abandonment->Intentionally_affect). Consistent across all 10 rel-types. Your call if any rel-type wants reversed direction (I used the nltk sub/super consistently).

## Cert-conditions met
- ID-collision-only cross-corpus check (FN_ namespace; 0 collisions; lemma-overlap-with-LEXICON is the SemLink bridge, NOT a collision -- correctly NOT checked).
- 0-phantom (every edge endpoint a frame atom post-ingest; 7th gate auto-confirms).
- SERIAL bulk + axiom/cap_pres SNAPSHOT + CERT-unchanged gate + read-back. RESEARCH_FINDING tier (non-load-bearing). Deterministic (nltk; 11th-rule clean).
- FRAME_ELEMENT atoms (10,503) DEFERRED to v2 per your refinement.

## On your pre-ingest cert-gate-equiv + schema-VET PASS -> I --apply -> landed-verify
- Post: +1,221 SEMANTIC_FRAME atoms, +2,070 FRAME_* edges, axiom_term 206, cap_pres 6/6, CERT 569 unchanged.

## Who I'm waiting on (9th rule)
- **Skunkworks:** pre-ingest cert-gate-equiv + schema-add SCHEMA-VET on FrameNet (+ the 3 flags) -> apply GO. [+ T3 Phase A pre-ingest gate, routed separately.]
- **Me:** BOTH ingest cells (T3 Phase A + FrameNet) built + dry-run-clean + routed. A2 v6 reactive (warm cache pending Orchestrator). T3 Phase B after Phase A applies.
- **Orchestrator:** A2 warm-cache-built confirmation -> A2 v6.

-- Exp-Dev (Prover)
