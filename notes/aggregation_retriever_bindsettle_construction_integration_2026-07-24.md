# AGGREGATION RETRIEVER -- brain-faithful bind+settle over ~2-3 central facts (staged 2026-07-24)

**GATED:** dispatch after the CLIMB FULL (b5ivtud7g) confirms the single-item floor + skunkworks VETs the WorldTree task-shape read. This is the sharpened next cell after the diagnostic.

## WHY (gold-grounded)
ARC is a MULTI-FACT AGGREGATION task, not single-fact lookup: WorldTree V2.1 gold = mean 5.69 facts/Q, only 6.4% single-fact; core reasoning ~2.5 CENTRAL facts (Easy 2.42 / Challenge 2.61); ~40% of support = lexical/taxonomic GLUE (KINDOF 32% + SYNONYMY 19%). Every single-ITEM retriever we tried caps ~0.35 (char-trigram, semantic-IR, fact-triples) because it fetches ONE thing when the task needs ~6. The lever = combine the few right central facts, bridged by meaning.

## BRAIN-FAITHFUL DESIGN CONSTRAINT (USER-LOCKED, non-negotiable)
The aggregator MUST be CONSTRUCTION-INTEGRATION (Kintsch/van-Dijk parallel constraint-satisfaction = the substrate's BIND+SETTLE), NOT an engineering "retrieve top-k, sum cosines, argmax." Facts must MUTUALLY CONSTRAIN and SETTLE. A score-sum aggregator that beats the floor is REJECTED as brain-unfaithful.
- **Working-memory vessel:** the ~2-3 CENTRAL facts fit COWAN-4 -> use the EXISTING 4-slot role-bundle working memory (role_slot_summarizer M1.7 HARD_PASS / working_memory_hrr_slots_PRODUCTION_v1) as the focus that binds+settles the central facts.
- **Spreading activation:** the ~40% lexical/taxonomic glue (SYNONYMY/KINDOF) = Collins&Loftus spreading activation over semantic memory -> the SemanticHDEncoder (GloVe+WordNet, 29533) bridges question-words to fact-words. This is the glue's faithful analog (activated periphery, not held in the 4-focus).
- **Aggregate vs chain:** brain does both (hippocampal-entorhinal chains + cortical convergence); ARC is short-aggregate-dominant -> aggregation here is match-mechanism-to-task. khop (substrate/khop.py, built for long FB15K paths) is the WRONG tool for THIS task, not wrong in general -- do NOT force it.

## THE CELL (exp_dev designs N/bands/seeds)
- INPUT: an ARC question + choices. RETRIEVE a candidate SET (top-k facts) from the vetted semantic fact store for the stem+choice, bridged via semantic/kindof.
- AGGREGATE by BIND+SETTLE: load candidate central facts into the 4-slot working memory, let them mutually constrain + settle (construction-integration), score each choice by the settled support. Glass-box: the settled fact set per answer is inspectable (PER-HOP-AUDIT analog for aggregation).
- BASELINE (fair, must PROVABLY fail): single-item retrieval (the ~0.35 floor) -- if bind+settle aggregation does NOT beat it, that's the discriminator working. Also a NON-brain-faithful score-sum arm as a contrast (to show settle > sum, or honestly report if it doesn't).
- ORACLE (optional, powerful): WorldTree gold explanations (data/corpora/worldtree/, local) give the GOLD support-set per question -> can measure retrieval recall of the central facts + upper-bound the aggregator (if given gold facts, does bind+settle answer correctly? isolates RETRIEVAL failure from AGGREGATION failure).
- CONTROLS: empty~chance, scramble-collapse, no answer-key leak, broad answer-agnostic ingest.
- HONEST QUESTION: does brain-faithful bind+settle aggregation beat the single-item ~0.35 floor on ARC (Easy AND Challenge)? If it LOSES, presume impl-bug until proven structural (brain does this -> we're doing it wrong). Report Easy vs Challenge separately (same mechanism expected to lift both; Challenge modestly harder).

## KNOWLEDGE SOURCE UPGRADE (discovered 2026-07-24) -- WorldTree TABLESTORE, not (just) ConceptNet
The CLIMB smoke's mechanism-limit (ConceptNet triples too TERSE/COMMONSENSE for grade science) has a fix on disk: the WorldTree TABLESTORE = **9,808 curated SCIENCE facts across 81 relation-typed tables** (KINDOF/CAUSE/PARTOF/MADEOF/PREDATOR-PREY/HABITAT/CHEM-PERIODIC-TAB/PROCESSSTAGES/IFTHEN...), already semi-structured into typed (subject, REL, object) slots (e.g. CAUSE(acid, chemical change), KINDOF(ability, characteristic)). Science-specific + relation-typed + small (fully ingestible, no scale issue) = a MUCH better fit than ConceptNet commonsense. Likely: tablestore for science facts + ConceptNet for commonsense glue.
- **TEST-TARGETING GUARDRAIL (honest, mandatory):** the tablestore was authored to EXPLAIN WorldTree/ARC questions -> ingesting it + testing on ARC risks test-tailoring. Fairness design: (a) tablestore rows are GENERAL science facts (not per-question) so it's a legitimate domain-matched CURRICULUM, BUT (b) test on ARC questions whose gold explanations are HELD OUT of the ingested set (WorldTree gives the per-question explanation UIDs -> exclude test-question support facts from ingest), and (c) report the fair held-out number, NOT a leaked one. This is the 29530 test-targeting lesson applied. Distinguish "domain-matched curriculum" (legit) from "answer-leaked" (not).

## CRITICAL PERF BUG TO FIX (from the killed CLIMB FULL, 2026-07-24)
The CLIMB FULL (60k ConceptNet ingest) was KILLED after 68 min stuck at i=20000/60000, CPU-pegged, intervals BALLOONING = **O(n^2) ingest**: the FUZZY conflict check (semantic-similarity per insert) scans the WHOLE growing fact set each insert. At 60k that's ~billions of cosine ops. The aggregation cell uses the SAME ingest path -> MUST FIX or it re-thraches:
- Use the O(1) exact-hash index (29532) for EXACT conflicts; restrict FUZZY conflict to a BUCKET/ANN neighborhood (LSH), NOT a full linear scan; OR
- do fuzzy-conflict as a BATCHED POST-PASS after bulk load; OR
- disable fuzzy-conflict during bulk ingest (tablestore is only ~9808 facts -> even O(n^2) is ~10^8, tolerable; ConceptNet 60k is NOT).
- Also: cap GloVe vocab (top ~120k freq-ordered covers 'photosynthesis') to cut the memory footprint ~4x (the reader-arm agent's trick that avoided the thrash). Do NOT run two big-GloVe cells concurrently.

## CLIMB single-item floor -- MEASURED HERE, not separately
The standalone CLIMB FULL was killed (O(n^2) + superseded paradigm). Its purpose -- the single-item fact-retrieval floor at scale -- is now the BASELINE ARM of this aggregation cell. So this cell MUST include the single-item fact-retrieval baseline (the thing bind+settle aggregation must beat). Smoke-level signal to reproduce+beat: fact-retrieval KB_BELOW_FLOOR (trailed sentence-IR by -0.043 at n=400, mechanism-limited: terse triples lose context).

## POINTERS
- hdlab/hd_fact_store.py (vetted semantic store) ; experiments/exp_semantic_hd_encoder_meaning_match_v1.py (SemanticHDEncoder) ; role_slot_summarizer / working_memory_hrr_slots (the 4-slot bind+settle WM) ; experiments/exp_arc_fact_retrieval_semantic_kb_climb_v1.py (the single-item floor to beat) ; data/corpora/worldtree/WorldtreeExplanationCorpusV2.1_Feb2020/ (gold oracle) ; data/corpora/arc/ (measure).
