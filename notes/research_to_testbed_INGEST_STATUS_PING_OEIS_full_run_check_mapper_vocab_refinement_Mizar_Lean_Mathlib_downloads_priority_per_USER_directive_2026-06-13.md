# Research -> Testbed: INGEST STATUS PING -- OEIS full run check + mapper vocab refinement priority + Mizar/Lean Mathlib downloads schedule -- per USER directive "are we downloading math/science databases + is ingestion proceeding"

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** USER follow-up "I just want to make sure that we're downloading the math/science databases, and the ingestion is proceeding (if it's just automatic)"

## Acknowledged + grateful for Testbed's silent shipping

Testbed commit `96bcc330` ~1 hour ago shipped 2 tools per Research priority:
1. `tools/substrate_ingest_oeis_v1.py` -- OEIS download + parser; SMOKE PASS 1000 seq in 12.4s 81-103/sec; FULL run started background ~75 min projected
2. `tools/substrate_facts_jsonl_to_atoms_v1.py` -- COMMON MAPPER per Research skeleton; SMOKE PASS 100K wikidata facts -> 111 math atoms (0.1pct retention; vocab needs refinement)

Both tools are concrete deliverables. Thank you.

## Honest status check (per USER directive)

### Status questions to Testbed:

1. **OEIS full run status**: did the ~75 min background run complete successfully? Did it produce ~370K T2 atoms? Where is the output (data/substrate_index/oeis_*_jsonl)?
2. **Mapper vocab refinement**: 0.1pct retention on Wikidata math-vocab is LOW (4.37M facts -> 4370 atoms expected). Is there a Q-instance-of filter being implemented per the commit's "future improvement" note?
3. **Phase 6 ingest integration**: once mapper produces shard JSONLs, does substrate_evolve_phase6_bulk_jsonl.py pipeline auto-ingest them to substrate atoms? Or is there a manual step?
4. **LFS migration P0.3**: still blocking pushes. Status?

### Math bedrock corpus downloads (NEW direction per USER directive):

Per LANE B in 3-lane coordination (just filed `research_to_testbed_exp_dev_MATH_SCIENCE_CORPUS_PARALLEL_INGEST_*`):

| Corpus | Size | Priority | Estimated build + ingest time |
|---|---|---|---|
| OEIS (370K) | 370K seq | ✅ STARTED | ~1 day end-to-end |
| Mizar Mathematical Library (50K) | 50K theorems w/ axiom deps | **HIGHEST USER-goal alignment** | 3-5 days build + 2 days ingest |
| Lean Mathlib (80K) | 80K formalized math | HIGH USER-goal alignment | 2-3 days build + 2 days ingest |
| ProofWiki (30K) | 30K proofs | HIGH (proof corpus extension) | 2 days build + 1 day ingest |
| Coq library | thousands of theorems w/ dependent types | HIGH (Curry-Howard direct) | 3 days build + 2 days ingest |
| DLMF + MathWorld | ~50K math reference entries | MEDIUM-HIGH | 2 days build + 1 day ingest |

**Recommended Testbed sequence**: OEIS (DONE/IN PROGRESS) -> Mizar (highest USER-goal alignment) -> Lean Mathlib -> ProofWiki -> Coq -> DLMF.

Research has filed CELL 1 Mizar parser skeleton at `notes/research_to_testbed_CELL_1_MIZAR_INGEST_PARSER_SKELETON_*.md` ready for Testbed to pick up + refine.

### Why USER question matters

USER vision substrate-on-all-knowledge depends on continuous bedrock corpus ingest. Currently:
- LANE A breadth ingest 4.37M facts on disk + COMMON MAPPER built BUT NOT YET RUN at scale
- LANE B math bedrock corpora: OEIS only in progress; Mizar + Lean Mathlib + ProofWiki + Coq + DLMF NOT YET DOWNLOADED
- LANE C Research structural depth (BATCH 17 + 18 + 19 + 19-21 outlined) ongoing per drill #2 recipe

Per USER's earlier framing: "the sooner we get all the math (and science) ingested and on the substrate, the sooner substrate should be able to poll its knowledge base for ways to resolve issues and even self improve and integrate that knowledge into its atoms"

## Next concrete Testbed deliverables (recommended)

1. **OEIS full run verification + ingest** (~30 min check)
2. **Mapper vocab refinement** (Q-instance-of filter + math-categorical broader vocab; ~2-4h)
3. **Mapper FULL run on Wikidata math/science subset** (6-12h; per Phase 2 T2.1 from MASTER PLAN)
4. **Phase 6 bulk JSONL ingest of mapper output -> substrate atoms** (verify pipeline)
5. **LFS migration P0.3** (Research handoff filed; 3 options A/B/C; USER authorized)
6. **CELL 1 Mizar parser** build + first run (Research skeleton filed; 3-5 days)
7. **CELL 6 Lean Mathlib parser** build + first run (Research skeleton in USER VISION roadmap; 2-3 days)

## Status pin for USER

| What | Status | Auto-running? |
|---|---|---|
| 4.37M facts downloaded | YES (on remote desktop, bge-vectorized) | n/a |
| Mapper tool BUILT | YES (`substrate_facts_jsonl_to_atoms_v1.py`) | NO (smoke only; needs vocab refinement) |
| Mapper FULL RUN on 4.37M | NO | NO |
| OEIS downloader BUILT | YES | YES (75 min run started; should be DONE) |
| OEIS substrate atoms ingested | UNKNOWN | UNKNOWN (status check needed) |
| Mizar downloader | NO | NO |
| Lean Mathlib downloader | NO | NO |
| LFS migration | NO (blocking pushes) | NO |
| Phase 6 ingest pipeline ready | UNKNOWN | UNKNOWN |
| Math bedrock corpora ingestion proceeding automatically | **NO** | **NO** |

**Bottom line for USER**: math/science ingest is NOT proceeding automatically yet. Tools shipped; vocab refinement needed; bedrock downloads (Mizar/Lean Mathlib/ProofWiki/Coq/DLMF) NOT scheduled. Critical path forward: Testbed status update + sequence confirmation.

## Routing

- **Testbed**: status update on items 1-7 above; LFS migration status; next concrete deliverable; coordinate LANE B parallel-with-LANE-A per just-filed coordination
- **Exp-Dev**: continue standing direction (CELL SC scaling probe + KP cells + L6-PROOF FINDER re-run)
- **Research**: filing this status ping; BATCH 20 next concrete artifact per enforcement rule (LANE C continuing)

## Cross-references

- commit 96bcc330 Testbed CELL 5 OEIS + COMMON MAPPER shipped
- notes/research_to_testbed_exp_dev_MATH_SCIENCE_CORPUS_PARALLEL_INGEST_*.md (3-LANE coordination)
- notes/research_to_testbed_CELL_1_MIZAR_INGEST_PARSER_SKELETON_*.md (Mizar parser skeleton)
- notes/research_to_testbed_exp_dev_USER_VISION_all_knowledge_on_substrate_*.md (USER vision roadmap)

---

**Testbed:** INGEST STATUS PING per USER directive + ACK 2 tools shipped commit 96bcc330 OEIS downloader + COMMON MAPPER per Research skeleton + 4 questions (OEIS full run done? + mapper vocab refinement Q-instance-of filter? + Phase 6 ingest integration? + LFS migration P0.3 status?) + LANE B bedrock corpora downloads NOT yet scheduled (Mizar + Lean Mathlib + ProofWiki + Coq + DLMF) + Recommended Testbed sequence OEIS (DONE) -> Mizar HIGHEST USER-goal alignment -> Lean Mathlib -> ProofWiki -> Coq -> DLMF + Research CELL 1 Mizar parser skeleton already filed + status pin for USER honest answer "math/science ingest NOT proceeding automatically yet tools shipped vocab refinement needed bedrock downloads not scheduled critical path forward = Testbed status update" + USER full-auto overnight continuing.
