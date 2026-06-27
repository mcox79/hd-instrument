# Pre-reg: substrate_director_kb_content_chunk_ingest_v1 (TOOLING; 2026-06-26)

**Anchor:** `substrate_director_kb_content_chunk_ingest_v1`
**Cell:** `experiments/exp_substrate_director_kb_content_chunk_ingest_v1.py`
**New primitive:** `hdlab/director_kb_chunk_ingest.py`
**Schema:** `config/director_kb_schema.json` (v1; additive use only -- 3 new
relation types `IS_CHUNK_OF`, `SECTION_HEADER`, `CHUNK_CONTENT` appended at
ingest time if not present, NOT a schema edit)
**Queue:** `local_cpu_queue`
**Tier hint:** TOOLING (not chain-grade-candidate). Success = OPERATIONAL.

## Source

USER Option A architectural fix 2026-06-26: current KB
(`substrate_director_kb_ingest_v1`) is a filename-metadata INDEX (entities =
filepaths; cosine query returns "this file has stuff about your query" --
user still must Read the file). Real KB should ingest CONTENT as atoms;
query returns ranked content snippets directly.

URGENT: ship cell + smoke before session compaction.

## Scope (ADDITIVE; does NOT replace v1)

Content-chunk ingest: for each text-mode source file, split body into
paragraph/section chunks (200-800 chars; respect markdown `##` boundaries).
Ingest each chunk as a SEPARATE atom whose entity = `<rel_path>::chunk<NNN>`
and whose `CHUNK_CONTENT` relation carries the actual chunk text.

Chunk source classes (TEXT modes only):
  - `note` (notes/)
  - `memory` (USER memory)
  - `prereg` (preregs/)
  - `director_plan` (data/director_plan.json)
  - `fleet_state` (data/fleet_waiting_on.md)

NOT chunked (jsonl/api/bio modes are file-level by construction; chunking
would corrupt their per-line entity semantics):
  - `metrics`, `cert_ledger`, `atoms`, `wordnet`, `verbnet`, `framenet`,
    `gene_ontology`, `kegg_pathway`, `neurolex`

The v1 filename-index module `hdlab/director_kb.py` keeps running unchanged;
both KBs can coexist at different on-disk paths (`data/substrate_director_kb_v1/`
filename, `data/substrate_director_kb_chunk_v1/` content-chunk).

## Arms (3 mandatory)

### ARM_CHUNK_SMOKE_NOTES_ONLY
- Chunk-ingest `notes/` only, capped at 50 files
- Verify: n_chunks > 0, avg_chunks_per_file >= 1.0, reject log present

### ARM_CHUNK_FULL
- Chunk-ingest all 5 TEXT classes (note + memory + prereg + director_plan +
  fleet_state) at full corpus size
- Verify: n_chunks >> n_files (avg >= 2.0), coverage >= 95%, all classes
  with files appear in per_class stats

### ARM_CHUNK_REINGEST_DET (LOAD-BEARING per Principle 2)
- Run ARM_CHUNK_FULL pipeline twice into separate temp dirs
- Assert: `entities.jsonl` + `relations.jsonl` + `atoms.jsonl` byte-equal
  (timestamps redacted); `W.pt` L2 diff < 1e-6
- If any fails -> HARD_FAIL (Principle 2 violated)

## Pre-reg HARD_PASS bands

- All 3 arms run without uncaught exceptions
- ARM_CHUNK_FULL elapsed_s <= 900s (15 min envelope; Principle 9)
- ARM_CHUNK_FULL coverage_ratio >= 0.95
- ARM_CHUNK_FULL avg_chunks_per_file >= 2.0 (cardinality_ok)
- ARM_CHUNK_REINGEST_DET passes exact-equal + W L2 < 1e-6
- Smoke discriminator: synthetic content-vs-filename test (file A named
  "elephant" with content "banana" outranks file B named "banana" with
  content "elephant" on query "banana") -- this is the LOAD-BEARING test
  that the architectural change actually delivers content-ranked retrieval

## Pre-reg HARD_FAIL bands

- ARM_CHUNK_FULL elapsed_s > 1800s (twice envelope)
- ARM_CHUNK_REINGEST_DET non-deterministic (Principle 2 violation)
- Coverage < 80% (dishonestly selective)
- avg_chunks_per_file < 1.2 (chunker degenerate; producing ~1 chunk/file =
  no benefit over v1 filename index)
- Smoke discriminator FAILS (content-query returns by filename = same
  behavior as v1 = no architectural improvement; CRITICAL TRIPWIRE)

## MIDDLE_BAND

- ARM_CHUNK_FULL between 900s and 1800s (works but exceeds envelope cap)
- Coverage between 80% and 95% (works but skip-rate visible in reject log)
- avg_chunks_per_file in [1.2, 2.0) (chunker producing few chunks; works
  but partial architectural benefit)

## Smoke gate

Smoke arm caps `max_files_per_class = 50` and runs all 3 arms on the reduced
corpus. Smoke must complete in <= 180s wall (queue_add SMOKE_TIMEOUT_S cap).

Smoke verifies (load-bearing per new discipline 2026-06-26):
1. mechanism (chunk extract + ingest + reload) works end-to-end
2. determinism arm passes on the small corpus
3. formula self-tests pass (HP/HF/MB discriminator)
4. chunker invariants (>=3 chunks from synthetic 2-header text;
   `Section A` + `Section B` headers preserved; marker content present)
5. **content-vs-filename discriminator** (the architectural fix actually
   delivers content-ranked retrieval; synthetic 2-file corpus with swapped
   filenames/content; query returns chunk by content not filename)

## Compose-on (chain-grade primitives)

- `hdlab.kg_traversal.KGStore` (CERT 584/585; Hebbian triple store)
- `hdlab.char_trigram_encoder.CharTrigramEncoder` (substrate-native text->HD)
- `hdlab.director_kb` (v1 ingest helpers `_read_file_text` /
  `_resolve_source_root` / `_glob_files` / `schema_hash` re-used; no new
  novel-synthesis primitives)
- `hdlab.director_kb_query.DirectorKBQuery` (existing query path with no
  modifications -- chunk atoms surface naturally because entities are
  chunk_ids that contain content-encoded vectors)

No novel-synthesis primitives. Principle 11 preserved.

## No-lock-in audit (USER constraint)

| Principle | Preserved by |
|---|---|
| 1. Filesystem canonical | Chunk ingest only READS source files. |
| 2. Wipe-and-rebuild safe | ARM_CHUNK_REINGEST_DET validates each run. |
| 3. Versioned | `chunk_ingest_version=v1` on every atom; dir is `data/substrate_director_kb_chunk_v1/`. |
| 4. Schema-as-config | Source classes resolved from schema; chunk relations added at ingest (extension, not edit). |
| 5. Multi-encoder | Atom carries `encoder=` tag. |
| 6. Director read-only | Cell writes; Director queries. |
| 7. Graceful degradation | Query path returns confidence; refuses on max_cosine < tau. |
| 8. Modular | Chunk ingest = separate module from v1 filename ingest; both run side-by-side. |
| 9. Compute envelope | Pre-reg HARD_FAIL at 30 min. |
| 10. Self-eviction | Chunks inherit source-file SUPERSEDES via IS_CHUNK_OF traversal. |
| 11. Chain-grade-only | KGStore + CharTrigramEncoder only. |
| 12. Source-controlled arch | This prereg + the cell + the primitive co-shipped this cycle. |

New disciplines (2026-06-26):
- **no silent except**: Cell wraps each arm in try/except + records error in
  arm dict; no `except: pass`.
- **smoke must fire discriminator**: Content-vs-filename test in
  `_instrumentation_selftest()` runs at import; if it fails the cell fails
  to import (no false-green smoke).
- **cardinality_ok pre-reg field**: `summary.cardinality_ok` = True iff
  ARM_CHUNK_FULL avg_chunks_per_file >= HP_MIN_AVG_CHUNKS_PER_FILE.

## Compute envelope

- Smoke: <= 180s wall on local CPU. Caps max_files_per_class=50.
- Full: <= 900s wall on local CPU (envelope cap Principle 9 = 15 min).
- Full timeout (queue): 1800s (2x envelope cap for safety margin).
- No GPU; numpy + torch CPU only.

## Timeout estimate

Full wall estimate at current corpus size:
- ~10000 notes + ~430 memory + ~1000 prereg + 1 director_plan + 1 fleet_state
  = ~11500 text files
- Avg ~3-5 chunks/file -> ~35-55k chunks
- Each chunk: char-trigram encode (microseconds) + 3 atoms
- KGStore ingest at ~50k triples ~ 30s
- I/O + write 4 jsonl + 3 .pt ~ 60s
- Total estimate: ~180-300s; pre-reg cap 900s (3x safety margin)

Queue timeout: 1800s (2x pre-reg cap for OS-noise safety).

## Reproduction

```
# Self-test (formula + chunker + content-vs-filename discriminator)
python experiments/exp_substrate_director_kb_content_chunk_ingest_v1.py --self-test

# Smoke
HDLAB_EXP_NAME=substrate_director_kb_content_chunk_ingest_v1_smoke \
  python experiments/exp_substrate_director_kb_content_chunk_ingest_v1.py --smoke

# Full
HDLAB_EXP_NAME=substrate_director_kb_content_chunk_ingest_v1 \
  python experiments/exp_substrate_director_kb_content_chunk_ingest_v1.py

# Query the chunk KB once full ingest lands (--chunk-content prints inline snippets)
python tools/director_kb_query.py --chunk-content "USER pivot today"
```

## Filed by

exp_dev (Opus 4.7-1M) on 2026-06-26, executing USER Option A architectural
fix request (urgent; pre-compaction window).
