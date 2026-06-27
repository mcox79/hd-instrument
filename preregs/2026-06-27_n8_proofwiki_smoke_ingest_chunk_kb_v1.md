# PRE-REG: n8_proofwiki_smoke_ingest_chunk_kb_v1

Author: exp_dev (Cell Author / Prover; spawn under Research lead)
Date: 2026-06-27
Anchor: `n8_proofwiki_smoke_ingest_chunk_kb_v1`
Source: research drill `notes/research_drill_math_science_extractor_design_2026-06-27.md` Section 3 (FIRST EXTRACTOR; rank-1)
Authorization: USER 2026-06-27 "overcome all of these" greenlight; ProofWiki is highest-signal-density math source for Phase 3 strategic anchor
Stage: Stage 3 (compositional understanding) — substrate-knows-math is prerequisite for USER strategic-vision Phase 3 "substrate proposes new mathematics"

## Scientific question

Does a SMOKE-tier ProofWiki ingest (500 Featured pages -> ~2500 content chunks
via existing chain-grade chunk-ingest pipeline) produce a chunk-KB that
ANSWERS theorem-name queries with TOP-1 cosine >= 0.85 AND verify-the-referent
content match AND analytical-scaling preserves the discriminator AND contamination
control passes (non-math queries don't rank math chunks above 0.5)?

## Mechanism class

KB ingest extension (new source class via no-lock-in Principle 4 schema config).
Composes ONLY on chain-grade primitives:
- chain-grade chunk-ingest pipeline (`hdlab/director_kb_chunk_ingest.py`;
  v1 HARD_PASS 2026-06-26)
- chain-grade query (`hdlab/director_kb_query.py`; v1 HARD_PASS 2026-06-26
  including `--filename-contains` rank-1 cosine=1.0)
- new: `hdlab/director_kb_math_sources.py` (mirrors `director_kb_bio_sources.py`
  pattern; fetch + parse + materialize ProofWiki Featured pages to disk)

DOES NOT rewrite the OLD ProofWiki extractor (`tools/substrate_ingest_proofwiki_v1.py`)
which targets the OLD `data/substrate_index/*/atoms.jsonl` partition. New
module writes to `data/math_kb_cache/proofwiki/<safe_filename>.md` for chunk
ingest to pick up via existing glob.

## Config

- N_DIM = 2048 (same as existing chunk-ingest v1; KB encoder default
  `char_trigram_v1`)
- SEED = 17
- MAX_PAGES (full smoke) = 500 ProofWiki "Featured" pages (~ 2500 chunks at
  4-6 chunks/page avg)
- MAX_PAGES (cell-author smoke) = 20 pages (~ 100 chunks; bounded; minimal
  network fetch; cached after first run)
- FETCH_THROTTLE_S = 1.0 (politeness; reuses bio_sources pattern)
- LICENSE_TAG = "CC-BY-SA-3.0"
- 5 probe queries (theorem names): Cauchy-Schwarz, Pythagoras, Bayes,
  Euler-Lagrange, Mean-Value-Theorem

## Arms (4 mandatory)

1. **ARM_BASELINE_FILENAME_QUERY** — query the EXISTING v1 filename-metadata
   KB for the 5 theorem names via `--filename-contains` substring. Records
   top-1 cosine + filename match. Establishes baseline before chunk-ingest
   adds content-aware retrieval.
2. **ARM_SMOKE_INGEST_500** — fetch + materialize ProofWiki Featured pages
   (MAX_PAGES = 500 full; 20 cell-author smoke) into
   `data/math_kb_cache/proofwiki/`; run chunk-ingest with new `proofwiki`
   source class; query 5 theorem-name probes against new chunks; record top-1
   cosine + chunk-content snippet for VERIFY-THE-REFERENT check.
3. **ARM_FULL_N_PREVIEW_DISCRIMINATOR** — same query as ARM_SMOKE_INGEST_500
   but cosine threshold projected analytically to N=35000 (full corpus):
   `tau_full = tau_smoke * sqrt(35000 / N_chunks_observed)`. If smoke top-1
   cosine doesn't clear scaled threshold, HARD_FAIL the discriminator (per
   discriminator-must-survive-scale USER 2026-06-26).
4. **ARM_CONTAMINATION_CONTROL** — query non-math terms ("Banana Republic",
   "Quarterly Earnings Report", "Soccer Tournament") against the new
   ProofWiki chunks; expect bottom-quartile cosine; if any top-1 cosine > 0.5,
   encoder is leaking surface-name similarity (BIAS-S regime failure per
   Mu-Viswanath).

## Metric

- `top1_cosine_per_probe` (list of 5; ARM_BASELINE_FILENAME_QUERY +
  ARM_SMOKE_INGEST_500)
- `top1_cosine_mean`, `top1_cosine_min` per arm
- `content_match_per_probe` (bool list; True iff returned chunk content body
  contains theorem-statement keyword(s))
- `analytical_scaling_passes` (bool; ARM_FULL_N_PREVIEW_DISCRIMINATOR)
- `contamination_max_cosine` per probe (ARM_CONTAMINATION_CONTROL); must be
  < 0.5 for all probes
- `n_chunks_observed`, `cardinality_ok` (META_RULE_H)
- `fetch_errors` (list; empty means clean fetch)

## Pre-registered bands (strictly-above-floor per META_RULE_L)

**HARD_PASS** (chain-grade-eligible ProofWiki smoke ingest):
- `ARM_SMOKE_INGEST_500.top1_cosine_min >= 0.85` (all 5 probes clear floor)
- AND `ARM_SMOKE_INGEST_500.content_match_per_probe` all True
  (verify-the-referent: content body contains theorem statement, not just
  filename match)
- AND `ARM_FULL_N_PREVIEW_DISCRIMINATOR.analytical_scaling_passes = True`
  (discriminator survives full-N projection)
- AND `ARM_CONTAMINATION_CONTROL.contamination_max_cosine < 0.5` for all 3
  non-math probes
- AND `cardinality_ok = True`
- AND `fetch_errors = []`

**MIDDLE_BAND**:
- ARM_SMOKE_INGEST_500.top1_cosine_mean >= 0.70 BUT `top1_cosine_min < 0.85`
  (some probes work, others don't)
- OR `analytical_scaling_passes = False` (discriminator doesn't survive scale;
  needs full-N test cell)

**HARD_FAIL**:
- `ARM_SMOKE_INGEST_500.top1_cosine_mean < 0.70`
- OR `ARM_CONTAMINATION_CONTROL.contamination_max_cosine > 0.5` (encoder
  leakage; BIAS-S regime failure)
- OR `cardinality_ok = False` (silent truncation)
- OR any `top1_cosine = 1.0` exactly with mismatched content (BIAS-Q suspect
  1.000; identity-match leak)
- OR `n_chunks_observed < 1500` (full) / `< 60` (smoke) — below
  HARD_FAIL_CARDINALITY_BREACH floor
- OR `n_chunks_observed > 4000` (full) — silent over-chunk

## Discriminator survives full-N (META_RULE_K — Option B analytical + Option C preview arm)

ARM_FULL_N_PREVIEW_DISCRIMINATOR is itself the survives-scale arm. Computes
scaled cosine threshold `tau_full = tau_smoke * sqrt(35000 / N_chunks_observed)`
per Mu-Viswanath anisotropy scaling and asserts ARM_SMOKE_INGEST_500 top-1
cosine clears the scaled threshold for all 5 probes.

If smoke discriminator FAILS this projection, this MIDDLE_BANDs the cell (NOT
HARD_PASS) — the smoke would pass alone but the full deployment wouldn't
survive scale.

## Cardinality (META_RULE_H)

- EXPECTED_N_CHUNKS (full smoke) ~ 2500 (500 pages * 5 chunks/page)
- EXPECTED_N_CHUNKS (cell-author smoke) ~ 100 (20 pages * 5 chunks/page)
- HARD_FAIL_CARDINALITY_BREACH if observed < 60 (smoke) / 1500 (full) OR
  > 4000 (full)
- `cardinality_ok` MANDATORY field in metrics.json

## No silent except (META_RULE_J)

All fetch errors recorded into `fetch_errors[]` list AND halt OR re-raise.
HTTP 404 on a specific page logged + skipped (acceptable; not all 500
Featured pages may resolve). Network failure on the bulk fetch halts.

## BIAS checklist (USER 2026-06-24 master checklist)

- **BIAS-S (regime check at scale)**: ARM_FULL_N_PREVIEW_DISCRIMINATOR is
  the load-bearing arm; encoder behavior must scale per Mu-Viswanath
- **BIAS-Q (suspect 1.000)**: any cosine = 1.000 exactly on a non-tautological
  probe flags identity-match leak (filename-shortcut, not content match)
- **BIAS-N (verify-the-referent)**: HARD_PASS requires CONTENT body match,
  not just filename match
- **BIAS-13 (contamination)**: ARM_CONTAMINATION_CONTROL with non-math probes

## Schema patch (additive; no-lock-in Principle 4)

Add to `config/director_kb_schema.json` `source_classes`:
```
"proofwiki": {
  "root_dir": "data/math_kb_cache/proofwiki",
  "glob": "**/*.md",
  "max_files": null,
  "encoding": "utf-8",
  "license_tag": "CC-BY-SA-3.0",
  "provenance_url_field": "proofwiki_url",
  "rejects_log_field": "skip_reason",
  "mode": "text"
}
```

Add to `entity_types`: `THEOREM`, `DEFINITION`, `AXIOM`, `PROOF`, `MATHEMATICAL_FIELD` (5)
Add to `relation_types`: `STATES_THEOREM`, `DEFINES`, `ASSUMES_AXIOM`, `PROOF_OF`, `CITES_THEOREM`, `IN_FIELD`, `GENERALIZES`, `SPECIAL_CASE_OF` (8)

Schema bump: `schema_version` v1 -> v2; `schema_date` -> 2026-06-27.

Principle-1 wipe-and-rebuild remains safe (existing schema-as-config design).

## Formula self-tests (run at module import)

1. Schema patch loaded: new entity_types + relation_types present
2. ProofWiki fetcher import + URL construction sanity (no actual fetch in
   self-test; cache-path computed deterministically)
3. Wikitext-to-markdown minimal transform: synthetic `[[X]] -> [X](X.md)`,
   `== H == -> ## H`, `{{template}} -> ` drop
4. Verdict-machinery selftest: synthetic HP / HF / MB / cardinality breach
5. Analytical scaling math sanity: tau_smoke=0.85, N=100 -> tau_full at
   N=35000 known value

## Queue / Dispatch

- Queue: `remote_cpu_queue` (CPU-only; CharTrigramEncoder is cheap)
- Estimated full smoke wall: 8 min (5 min fetch + 1 min materialize + 30s
  chunk-ingest + 1 min query)
- Per-experiment `--timeout`: 1800s (30 min; generous slack for network
  variability)
- Cell-author smoke wall budget: ~60s (20 pages; cached after first run)

## License + attribution

ProofWiki content licensed CC-BY-SA 3.0. Each materialized .md file's
YAML front-matter MUST include:
- `license: "CC-BY-SA-3.0"`
- `source_url: <proofwiki_url>`
- `attribution: "ProofWiki contributors"`

Chunk-ingest captures these via existing chunk metadata pipeline.

## Brain-grounding

N/A (KB ingest is tooling, not capability cell). Strategic-prerequisite for
USER vision Phase 3 (substrate proposes new mathematics).

## P_deflated (lit-scan calibration)

P_deflated = 0.50 (raw lit P=0.70 minus 0.20 calibration; HIGH P because
composes on chain-grade primitives + brain-grounding "humans learn math from
formal texts" existence proof gives high prior).

## Honest scope

The HARD_PASS claim is bounded to: 500 ProofWiki Featured pages smoke ingest
into chunk-KB v2; ProofWiki FULL ingest (~35k pages) requires a separate
cell after smoke HARD_PASS + USER vet of KB-size budget impact.

Zero LLM calls at inference (`zero_llm_calls_at_inference=True`).
