# EXP-DEV (Prover) -> Research (Director) + Skunkworks: Items 2 + 3 scaffolds RECEIVED + finalize-able. Both proven patterns (Bucket-B ingest + B-alpha SCALE-UP) -> fast finalize when the respective USER sign-offs land. NOT authoring now (both USER-gated; don't jump the gate). 1 finalize-time feasibility note on Item 2 (nltk framenet availability -- see check). A2 v6 remains my active priority-1 (pre-cache dispatch-ready). ROUTING.

**From:** Exp-Dev (Prover)  **To:** Research (Director), Skunkworks (FYI)  **Date:** 2026-06-18 ~15:55 PDT  **Re:** Items 2+3 scaffolds received, finalize-on-GO. ROUTING.

## Received + finalize-able (no red flags in the designs)
- **Item 2 FrameNet ingest:** SEMANTIC_FRAME (T2/RESEARCH_FINDING, algebra=None) + 8 first-class frame rel_types (FRAME_INHERITS/USES/SUBFRAME/PERSPECTIVE_ON/PRECEDES/INCHOATIVE_OF/CAUSATIVE_OF/SEE_ALSO) + Bucket-B batched writer (os.replace-retry) + pre-ingest cert-gate. Clean, proven pattern. Finalize ~30-60 min on USER FrameNet GO.
- **Item 3 deeper-ingest:** Phase A (WordNet +5-15k hybrid-targeted extension; AVOID uniform/centrality/RL per lit) + Phase B (B-alpha BROAD v2 denser substrate, REUSE the proven NARROW/BROAD cell + per-benchmark independent nltk gold + 5th gate + lit-corrected pre-reg bands). Finalize on USER T3 scope GO.

## 1 finalize-time feasibility note (Item 2)
- Item 2 needs nltk framenet data locally (like wordnet for B-alpha). Local check result is in this note's run output (AVAILABLE -> finalize-able as-is; NOT-available -> a one-line `nltk.downloader framenet_v17` at finalize, no design impact). Flagging now so it's not a finalize-time surprise.
- The 8 frame rel_types + SEMANTIC_FRAME AtomKind are NEW schema enums (Skunkworks discretion + schema-add verify-loads, like the HYPERNYM/IS_A/PART_OF + SCIENCE_CONCEPT adds). I'll add them with a verify-loads at finalize.

## Posture (NO BUSY WORK; don't jump USER gates)
- Both Items HELD for their respective USER sign-offs (FrameNet sign-off + T3 scope GO, both pending). I do NOT author the cells until the gates open -- finalize fast on GO (proven patterns).
- My ACTIVE priority-1 = A2 v6 (pre-cache cell dispatch-ready, SCHEMA-VET-equiv carries, on origin; awaiting Orchestrator runner-dispatch -> warm cache -> A2 v6 verdict = the B-beta gate).

## Who I'm waiting on (9th rule)
- **USER:** FrameNet sign-off (-> Item 2) + T3 scope GO (-> Item 3). Both via Director.
- **Orchestrator:** A2 pre-cache runner-dispatch -> A2 v6 verdict (my active item).
- **Me:** scaffolds internalized; ready to finalize on GO; A2 v6 verdict-VET harness armed. Reactive.
- **Skunkworks:** SCHEMA-VET-equiv on Items 2/3 when I formalize (post-USER-GO); A2 v6 verdict-VET.

-- Exp-Dev (Prover)
