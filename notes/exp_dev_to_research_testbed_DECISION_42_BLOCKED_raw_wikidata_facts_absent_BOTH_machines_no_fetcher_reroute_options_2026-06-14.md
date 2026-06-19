# Exp-Dev (Prover) -> Research (Director) + Testbed: DECISION 42 BLOCKED -- raw wikidata facts file absent on BOTH machines (verified); no fetcher script exists; pipeline runner ready but has no input. Re-route needed. INGEST_BLOCKED (not INGEST_COMPLETE).

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** INGEST_BLOCKED
**Re:** DECISION 42 ingest execution. Verified the premise before running a 1-2hr job. ACTUAL (10th rule); not proceeding on a false premise (don't fabricate / don't ingest wrong-format data).

## BLOCKER: the raw facts file does not exist anywhere
DECISION 42 (inheriting the Testbed BLOCKER note) assumed `data/external/wikidata/wikidata_truthy_50m.jsonl` "lives on REMOTE DESKTOP." It does NOT. Verified:
- **Remote desktop** (C:/dev/hd-instrument): `data/external/wikidata/` -> NO_WIKIDATA_DIR; broad `dir /s /b data\external` for wikidata/truthy/.nt -> empty.
- **Laptop** (d:/AI/hd-instrument): no `data/external/wikidata/`; `data/external/` has only coq_corpus + mizar_mml + proofwiki; broad find for wikidata/truthy/.nt -> only the already-mapped 111-atom shard.
- **No fetcher/download script** for wikidata exists in tools/ (only pip internals).
- Remote desktop git HEAD is also far behind (d78ffe8a, testbed Cycle-50) vs laptop a9920aac -- so the pipeline runner + mapper v2 are not even on the remote yet (separate sync issue; easily scp'd, but moot without input data).

## What IS available (and why it doesn't drop in)
- `data/substrate_index/external/wikidata_atoms.shard_0000.jsonl` -- 111 atoms, ALREADY MAPPED (not raw facts), non-scientific (Beethoven etc); Testbed already rejected as not-the-target. Cannot feed the pipeline (pipeline expects RAW facts.jsonl -> mapper -> atoms).
- `data/external/{coq_corpus, mizar_mml, proofwiki}` -- real scientific/formal-math corpora, PRESENT on laptop. BUT (a) wrong format: `substrate_facts_jsonl_to_atoms_v2.py` expects wikidata-style facts.jsonl with qclass/qcode fields, not coq/mizar/proofwiki text; needs a format adapter. (b) math-heavy: overlaps the substrate's existing math coverage; low value for the held-out GAP topics (active_inference, free_energy_principle, predictive_coding -- neuroscience/ML, not formal math).

## Pipeline status (ready, just no input)
- `tools/substrate_ingest_pipeline_runner_v1.py` is pure-stdlib (sys/json/time/subprocess/argparse/shutil/pathlib) -- confirms R1 (no LLM/bge/torch). It subprocess-calls `tools/substrate_facts_jsonl_to_atoms_v2.py` with required `--facts-jsonl`. Everything is ready EXCEPT the input facts file.

## Re-route options (Director/USER call)
1. **Obtain a wikidata truthy slice (download).** The full truthy dump is tens of GB; even a slice needs a source URL + download infra + disk/bandwidth. **Needs USER** (disk space + bandwidth + which source/slice). No fetcher exists; one would need writing. Highest fidelity to DECISION 36 intent (broad science, covers the held-out gap topic-space for FUTURE held-out authoring).
2. **Re-scope ingest to an EXISTING corpus (coq/mizar/proofwiki).** I write a format adapter (corpus text -> facts.jsonl schema the mapper consumes) -- a small dev task, UNBLOCKED, my lane, no download. Trade-off: math-heavy, less NEW coverage; expands gap class less for the neuroscience held-out topics. But it's runnable TODAY and still enlarges the atom base + provides a real ingest exercise of the R3 capability-preservation invariant.
3. **Synthetic scientific facts.jsonl slice.** Author a small synthetic facts file in the mapper's schema (e.g., from a curated science term list). Artificial but controllable + fast. Lower scientific authenticity.

## Recommendation
- If the goal is robustly enlarging the held-out GAP class for the M4 decision (the strategic driver per DECISION 39c/41): option 1 (real wikidata science) is the right source, but it's **USER-gated** (download/disk/bandwidth + source URL + a fetcher to write).
- If the goal is to exercise the ingest pipeline + capability-preservation invariant + add SOME coverage NOW while wikidata is sourced: option 2 (I adapt coq/mizar/proofwiki) is unblocked and I can start immediately on your go.
- I did NOT run anything (no false-premise run; no wrong-format ingest). Awaiting re-route.

## What I need from Director/USER
- Which option? If option 1: USER must provide/approve a wikidata source + confirm disk/bandwidth (and authorize me to write a fetcher). If option 2: your GO and I start the format adapter now (unblocked).

-- EXP-DEV (Prover)
