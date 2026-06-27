# Pre-reg: substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced (ANCHOR 1 v2 patch; TOOLING; 2026-06-27)

**Anchor:** `substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced`
**Cell:** `experiments/exp_substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced.py`
**Queue:** `remote_cpu_queue` (NO LOCAL per USER 2026-06-27)
**Tier hint:** TOOLING patch; reuses chain-grade chunker primitive `hdlab/director_kb_chunk_ingest.py`.

## Source

Agent a38d457eada23b1ae reported content-vs-filename discriminator FIRED+PASSED inside `_instrumentation_selftest`, but Skunkworks batch 5 searched `metrics.json` + `entities.jsonl` + `atoms.jsonl` across all 3 arm dirs and found NO banana/elephant strings -- discriminator outcome never surfaced to metrics. Cert tier accordingly held back.

## Scope

v2 SURFACES the content-vs-filename discriminator as a real ARM in the cell, logging results to `metrics.json` so Skunkworks (and any auditor) can verify the discriminator outcome directly off-disk rather than trusting selftest stdout.

Two-part fix:

1. **Add `ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST` as a 4th arm.** Uses the same 2-file synthetic corpus (elephant_filename containing banana content; banana_filename containing elephant content). After ingest, queries `"banana"` + `"elephant"` against the resulting KB. For each query, records:
   - `top_1_chunk_entity` (the entity string of the top-ranked result)
   - `top_1_source_paths` (the file(s) the top-1 came from)
   - `top_1_cosine`
   - `assertion_passed`: bool = (top-1 chunk content contains the queried word, REGARDLESS of source filename). Equivalently for queried word `w`, the top-1 entity's text OR the chunk text linked to the top-1 entity contains `w`.
   - Full `top_5_atoms` for audit.
2. **Persist the 2-file synthetic KB to the arm workdir** (`_arm_content_vs_filename/kb`) so Skunkworks can re-query directly off-disk if needed.

This makes the discriminator (a) AUDITABLE off `metrics.json` alone (b) RE-RUNNABLE off the persisted arm KB (c) NEVER vacuously satisfied because the assertion fires per-arm and is logged.

## Arms (4 total; v1's 3 + new tripwire)

### ARM_CHUNK_SMOKE_NOTES_ONLY
Unchanged from v1; sanity rail.

### ARM_CHUNK_FULL
Unchanged from v1; full ingest envelope check.

### ARM_CHUNK_REINGEST_DET
Unchanged from v1; Principle 2 determinism.

### ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST (NEW v2)
- Build 2-file synthetic corpus (deterministic, in tempdir but persisted as arm_dir/kb).
- Run chunk ingest at N_DIM=2048 seed=17.
- Query "banana" and "elephant"; record top-5 atoms + per-query assertion.
- `arm.ok` = both queries return content-correct top-1 (banana query top-1 contains "banana"; elephant query top-1 contains "elephant").
- PASS bar baked into per-arm result; verdict logic gates HARD_PASS on `arm.ok`.

## Success criteria

HARD_PASS = all 4 arms ok AND ARM_CHUNK_FULL within HP envelope AND ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST both queries content-correct.

The new arm's HARD_PASS bar:
- `banana_query_assertion_passed == True` (top-1 entity text OR linked chunk text contains "banana")
- `elephant_query_assertion_passed == True` (same for "elephant")
- Both assertion outcomes + top-5 atom dumps surface in `metrics.json`

## Failure (REJECT)

- New arm: either query returns top-1 from the WRONG-content file (= v1 filename-index behavior; v2 architectural improvement not realized)
- Existing v1 HARD_FAIL criteria (det violation, envelope, coverage, avg_chunks_per_file)

## REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`, `cardinality_ok`,
`summary.arms[ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST].banana_query_top_5_atoms`,
`summary.arms[ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST].elephant_query_top_5_atoms`,
`summary.arms[ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST].banana_query_assertion_passed`,
`summary.arms[ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST].elephant_query_assertion_passed`.

## cardinality_ok

`summary.cardinality_ok = (n_chunks_in_discriminator_arm >= 2) AND (avg_chunks_per_file_in_full >= HP_MIN_AVG_CHUNKS_PER_FILE)`.

## Discipline gates

- Fix #26: pre-dispatch referent check (notes/ + memory/ dirs exist).
- META_RULE_H: cardinality_ok mandatory.
- META_RULE_J: discriminator surfaces to metrics (Skunkworks batch 5 root cause: discriminator-output-must-surface).
- META_RULE_L: real data + synthetic discriminator both audited.

## Estimated cost

Should land in <5 min on remote_cpu. Same envelope as v1 (HP <=900s for FULL arm; +10s for new discriminator arm).

## Routing

`remote_cpu_queue` on marsh@home (per USER 2026-06-27 NO LOCAL directive). Push + queue_add via orchestrator (push is harness-DENIED to exp_dev).
