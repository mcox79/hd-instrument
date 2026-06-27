# Pre-reg: substrate_director_kb_bio_trio_ingest_v1

**Anchor:** substrate_director_kb_bio_trio_ingest_v1
**Filed-by:** exp_dev (Opus 4.7-1M)
**Date:** 2026-06-26
**Tier hint:** TOOLING (operational, not chain-grade-candidate)
**Queue:** local_cpu_queue
**Cell:** experiments/exp_substrate_director_kb_bio_trio_ingest_v1.py
**Schema delta:** config/director_kb_schema.json (ADD gene_ontology + kegg_pathway + neurolex source classes; ADD 18 bio relation types; ADD 12 bio entity types — additive, no replacement of existing v1)

## Trigger

USER 2026-06-26: "more biology (particularly neuro)" — substrate has structured biological knowledge directly aligned with our cortex content-extraction work (Wave 1 cortex E-tensor; cortex 4x cross-discipline drill). Having brain knowledge IN the substrate makes the substrate's reasoning about its own cortex-like mechanisms grounded.

## Scope

Extends the chain-grade Director-KB (ANCHOR 1 v1) with 3 biological corpora. Composes on the existing v1 ingest pipeline (chain-grade today; HARD_PASS 2026-06-26 with full_elapsed_s=14.306 / coverage=0.999 / W L2=0.0). New work is purely additive: new source classes + new parsers + new relation types in the schema config.

## Sources (additive)

1. **Gene Ontology (GO)** — `.obo` from `https://current.geneontology.org/ontology/go-basic.obo` (~32MB, ~45k terms). Relations: IS_A, PART_OF, REGULATES, POSITIVELY_REGULATES, NEGATIVELY_REGULATES, OCCURS_IN, NAMED, ALIAS_OF.
2. **KEGG pathways** — REST API `https://rest.kegg.jp/get/<pathway>/kgml`. Default focus: hsa04* signaling+neural pathways (~25 pathways FULL, 5 SMOKE). Politeness: 1.0s throttle between fetches at FETCH TIME (not ingest time). Relations: STEP_OF, CATALYZES, REACTANT_OF, PRODUCT_OF, REGULATES_PATHWAY.
3. **NeuroLex / NIF-Ontology** — SciCrunch GitHub raw TTL (NIF-Cell, NIF-GrossAnatomy, NIF-Molecule) + curated brain-region / cell-type / neurotransmitter fallback TSV (always present; guarantees basic neuro queries work even if SciCrunch URLs offline). Relations: PROJECTS_TO, RECEIVES_FROM, CONTAINS_CELL_TYPE, EXPRESSES_NEUROTRANSMITTER, BINDS_TO, IS_A, PART_OF.

All sources cached to `data/bio_kb_cache/{go,kegg,neurolex}/`; ingest reads from cache (deterministic — Principle 2).

## Pip installs

NONE. Pure std-library (urllib + xml.etree + re + json) + existing hdlab dependencies (torch + numpy). Curated NeuroLex fallback shipped in the source module.

## Arms (7)

- ARM_FETCH_SOURCES — pre-flight idempotent fetch; fails LOUD if GO unreachable OR KEGG REST down OR NIF empty (curated fallback always present)
- ARM_INGEST_GENE_ONTOLOGY — single-class ingest of GO; verify >= 1000 triples
- ARM_INGEST_KEGG_PATHWAY — single-class ingest of KEGG; verify >= 1000 triples
- ARM_INGEST_NEUROLEX — single-class ingest of NeuroLex; verify >= 1000 triples (curated fallback alone is 54; only via NIF TTLs do we hit the floor)
- ARM_INGEST_FULL_BIO_TRIO — all 3 bio classes together
- ARM_REINGEST_DETERMINISTIC — run FULL_BIO_TRIO twice; byte-equal entities/relations/atoms (timestamps redacted) + W L2 < 1e-6
- ARM_REGRESSION_EXISTING — ingest ALL classes (original v1 non-API + bio trio); verify existing-class triples preserved (>= 90% of v1 54195 baseline)

## Pre-reg PASS bands

- **HARD_PASS:** all 7 arms ok; ARM_INGEST_FULL_BIO_TRIO elapsed_s <= 600s (10 min envelope, Principle 9); per-class triples >= 1000; ARM_REINGEST_DETERMINISTIC byte-equal + W L2 < 1e-6; ARM_REGRESSION_EXISTING total >= 50000 triples + non_bio >= 45000 (>= 90% of 50000 floor); fetch errors empty.
- **HARD_FAIL:** any source unfetchable; OR ARM_INGEST_FULL_BIO_TRIO elapsed_s > 1800s (3x envelope); OR ARM_REINGEST_DETERMINISTIC non-deterministic (Principle 2 violation); OR per-class triples < 1000 (silent ingest failure); OR ARM_REGRESSION_EXISTING non_bio_triples < 45000 (existing-data loss > 10%).
- **MIDDLE_BAND:** all arms ok but bio_trio elapsed in (600s, 1800s] OR regression total in [50000, 54000).

## No-lock-in principles preserved

All 12 preserved per `notes/exp_dev_handoff_research_substrate_director_kb_dogfood_2026-06-26.md`. Concrete mapping:

- **P1 (filesystem source-of-truth):** All bio sources live in `data/bio_kb_cache/`; ingest reads, never writes back to GO/KEGG/NIF. Substrate-KB is index over cache.
- **P2 (wipe-and-rebuild safe):** ARM_REINGEST_DETERMINISTIC enforces byte-equal across runs. Cache files are deterministic bytes from upstream sources.
- **P3 (versioned pipeline):** New parsers in `hdlab/director_kb_bio_sources.py` v1; KB version unchanged (v1) since schema is additive. Future v2 can swap parsers.
- **P4 (schema-as-config):** All 3 new source classes are config-only in `config/director_kb_schema.json`. Parser dispatch via mode keys (`obo_go` / `kegg_kgml` / `nif_ttl`).
- **P5 (multi-encoder):** Bio classes use the same `char_trigram_v1` encoder as v1 (subjects are short ontology IDs + names; trigram-bag works well).
- **P6 (read-only from Director):** Director queries; ingest cell writes. Unchanged.
- **P7 (graceful degradation):** Query layer's existing refuse-gate covers low-confidence bio queries; Director falls back to grep over `data/bio_kb_cache/` if KB confidence below tau.
- **P8 (modular):** New parsers live in `director_kb_bio_sources.py` (separate from `director_kb.py` core). Adding a 4th bio source = 1 new function + 1 schema entry.
- **P9 (compute envelope):** Bio-trio ingest target <= 10 min (HP_MAX_BIO_TRIO_ELAPSED_S = 600s). HARD_FAIL at 30 min (3x envelope).
- **P10 (self-eviction):** Schema-extension only; existing superseded-by mechanism still applies to bio atoms.
- **P11 (chain-grade primitives only):** Composes on KGStore (chain-grade) + CharTrigramEncoder (chain-grade) + existing director_kb pipeline (chain-grade HARD_PASS 2026-06-26). No novel-synthesis primitives.
- **P12 (architecture in config + readme):** This prereg + the schema-config entries document the bio extension. No code changes outside parser dispatch.

## Sample queries (for post-ship verify in this session)

- "what biological process is GO:0007268 part of?" — should retrieve GO PART_OF chain
- "what reactions are in the glycolysis pathway?" — should retrieve KEGG hsa00010 STEP_OF reactions
- "what cell types are in the hippocampus CA3?" — should retrieve CONTAINS_CELL_TYPE for HIPPOCAMPUS_CA3

## API throttling notes

- KEGG REST: 1.0s sleep between `/get/<pathway>/kgml` calls per KEGG terms of service. Throttle at FETCH time only; ingest from cache is throttle-free.
- GO: single .obo download (~32MB); idempotent cache.
- NIF: 4 TTL files (~few MB total); idempotent cache. Curated fallback always written.

## Risk / fail-loud

- If GO endpoint moves: HARD_FAIL ARM_FETCH_SOURCES; remediation = update GO_OBO_URL in `hdlab/director_kb_bio_sources.py`.
- If KEGG rate-limits aggressively: HARD_FAIL ARM_FETCH_SOURCES; remediation = increase KEGG_THROTTLE_S; cache survives partial failures (idempotent).
- If SciCrunch GitHub goes 404 for all TTLs: NeuroLex degrades to curated-fallback-only (54 triples). This trips the per-class >= 1000 floor → HARD_FAIL. Mitigation: expand `NIF_CURATED_FALLBACK_TRIPLES` in the source module OR add another TTL fallback URL.

## Determinism contract

Given identical cached source bytes + schema_hash + N_DIM + seed:
- entities.jsonl byte-equal
- relations.jsonl byte-equal
- atoms.jsonl byte-equal (with `redact_timestamps_in_atoms=True`)
- W.pt L2 diff < 1e-6

Cache fetcher is idempotent; ingest is fully deterministic from cache.
