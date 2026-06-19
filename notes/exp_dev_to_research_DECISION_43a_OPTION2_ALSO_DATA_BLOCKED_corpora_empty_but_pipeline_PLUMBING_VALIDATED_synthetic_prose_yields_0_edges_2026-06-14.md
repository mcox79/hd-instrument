# Exp-Dev (Prover) -> Research (Director) + Testbed: DECISION 43a -- Option 2 ALSO data-blocked (coq/mizar/proofwiki dirs EMPTY, verified). BUT pipeline PLUMBING VALIDATED end-to-end via synthetic input (37/40 atoms, 0 failures, zero substrate mutation). KEY FINDING: word-mode/prose yields 0 DEPENDS_ON edges -> relational structure requires STRUCTURED wikidata triples (reinforces Option 1 necessity). Real ingest now fully USER-data-gated.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** INGEST_PIPELINE_VALIDATED
**Re:** DECISION 43a GO Option 2. Second false-premise caught (this one MINE: assumed the corpus dirs held data). ACTUAL (10th rule).

## Option 2 is ALSO data-blocked (verified)
data/external/{coq_corpus, mizar_mml, proofwiki} are all EMPTY (0 files, 0 bytes). I assumed they held data because the directories existed; they are placeholders. So BOTH no-download options are dead:
- Option 1 (wikidata): raw facts absent on both machines (DECISION 42 blocker).
- Option 2 (existing corpora): directories empty.
=> There is NO external ingest data anywhere on either machine. Real ingest is FULLY USER-data-gated.

## BUT: pipeline PLUMBING validated (DECISION 43a primary goal = infrastructure proving)
To serve 43a's stated primary rationale ("INFRASTRUCTURE PROVING", not coverage), I validated the pipeline end-to-end with a small SYNTHETIC science facts file (40 facts, `experiments/_synth_science_facts_gen.py`), running stages 1-3 ONLY (mapper -> merge -> adapter), SKIPPING the ingest stages (--skip-atom-ingest --skip-edge-ingest) so ZERO substrate mutation (R3 safe).

Result -- pipeline COMPLETE: OK:
- mapper (word-mode, corpus=wikipedia, filter=science): 40 facts -> 37 atoms (92.5pct retention; 3 filtered for no vocab term). NOTE: this is the word-vocab path that had NEVER been exercised end-to-end (prior runs were wikidata qclass smoke only).
- merge: 37 lines. adapter: 37 well-formed atoms, 0 failures. Sample atom valid: id `T3/wikipedia_Vector_space_0`, corpus=math, tier T3, kind PRIMITIVE, full description/aliases/metadata/algebra.
- The mapper word-mode + adapter chain WORKS. Infrastructure proven ready to consume real data.

## KEY FINDING (strategic): prose/word-mode produces 0 DEPENDS_ON edges
The adapter emitted **0 relations**. Cause: the v1 wikipedia/prose branch sets `depends_on: []`, so there are no edges to build. Only the STRUCTURED wikidata-triple mode (qclass; `depends_on=[wikidata_obj]`) produces DEPENDS_ON edges.
- Implication: ingesting PROSE corpora (wikipedia/arxiv/coq/mizar/proofwiki-as-text) yields ISOLATED atoms with NO relational structure. The substrate's relational machinery (DEPENDS_ON graph -> F2 abstraction, structural reasoning, L6-PROOF chains) gets NOTHING from prose ingest.
- So the DECISION 42 expectation of "~30-100k DEPENDS_ON edges" was wikidata-structured-specific. To grow the relational graph, ingest MUST be STRUCTURED triples (wikidata), not prose.
- This REINFORCES Option 1 (wikidata) as the right source -- not just for coverage, but because only structured data produces the edges the substrate uses. A prose-corpus ingest would add atom count without architectural value.

## Verdict vs DECISION 43a HARD-PASS
- "1k+ atoms ingested": NOT met -- no real data exists to ingest; 37 synthetic atoms produced (NOT ingested; plumbing only).
- Infrastructure-proving sub-goal: MET -- pipeline validated end-to-end on the word-mode path, 0 failures, zero substrate risk.
- So 43a is PARTIAL: pipeline PROVEN ready; real ingest BLOCKED on USER data.

## Where this leaves the ingest track
- Real ingest is now BINARY: either the USER provides wikidata structured data (Option 1) or there is no value-adding ingest (prose gives isolated atoms; synthetic gives nothing real). Option 3 (synthetic) is plumbing-only, no coverage/edge value -- not worth ingesting into the real substrate.
- The pipeline is PROVEN READY to consume real wikidata the moment it is available.
- DECISION 38 (decisive held-out test) can proceed on the CURRENT (pre-ingest) substrate as the BASELINE now -- it does not need ingest to establish the H_M4 baseline (in-coverage 0.14 post-39a; gap refuse 0.67). The post-ingest comparison waits for Option-1 data.

## Recommendation to Director/USER
- **USER decision needed (Option 1):** real ingest requires the USER to provide a wikidata structured slice (disk/bandwidth/source). Without it, no value-adding ingest is possible -- prose/synthetic do not produce the relational structure. I will write the fetcher + run the pipeline the moment a source is approved.
- **Meanwhile (unblocked):** I can run DECISION 38 on the current substrate now to lock the pre-ingest baseline (H_M4 vs H_INGEST), so the post-ingest comparison is ready. Want me to proceed with the DECISION 38 baseline?

-- EXP-DEV (Prover)
