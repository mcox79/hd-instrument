# Pre-reg: causal/process-role enrichment probe-recovery test v1 (causal_enrichment_probe_recovery_v1)

Date: 2026-08-11. Cell: `experiments/exp_causal_enrichment_probe_recovery_v1.py`. Author: exp_dev.
Serves the three-tier knowledge-sourcing gather-layer drill's pre-registered "cheap decisive test"
(`notes/research_three_tier_knowledge_sourcing_gather_layer_2026-08-11.md`, "Cheap decisive test" +
"Falsifiable predictions" sections). Data-diagnostic cell (NOT a substrate-mechanism arm sweep, NOT
a canonical foundation rebuild). Artifact lands under `data/exp_causal_enrichment_probe_recovery_v1/`
only; the canonical `data/cskg_foundation_v1/` store is READ-ONLY input, never mutated. NO origin push
(hard constraint this cycle) -> this cell runs INLINE-LOCAL foreground-to-completion, not via
queue_add/remote dispatch (INLINE-LOCAL MANDATE, exp_dev.md SS "NO HEAVY LOCAL DETACHED FITS").

## PRIOR-WORK CHECK (SUBSTRATE-KB CONCEPT-QUERY, mandatory before authoring)
`bash tools/substrate_query.sh "causal knowledge ingestion CauseNet process role probe recovery
held-out"` -> top cosine = 0.2852 (entity `cause problems`, generic concept-index atom), all other
hits < 0.28. **No prior-arc cell at cosine>0.30** -> this cell is genuinely novel, not a rediscovery.

## WHAT
Ingest two zero-license-gate, low-engineering-risk sources identified by the gather-layer sourcing
drill, as an ENRICHED overlay on the already-landed `data/cskg_foundation_v1/` graph (not a mutation
of that store):
1. **CauseNet-Precision** (`data/bio_kb_cache/causenet/causenet-precision.jsonl.bz2`, 137.87 MB,
   197,806 rows, CC BY 4.0, downloaded this cycle from
   `https://groups.uni-paderborn.de/wdqa/causenet/causality-graphs/causenet-precision.jsonl.bz2`) ->
   every row is a typed `(cause_concept, cn:Causes, effect_concept)` edge.
2. **go.obo full re-download** (`data/bio_kb_cache/go/go.obo`, 36.7 MB, downloaded this cycle from
   `https://current.geneontology.org/ontology/go.obo`, same CC BY 4.0 OBO Foundry host as the
   already-owned `go-basic.obo`) -> restores the `regulates` / `positively_regulates` /
   `negatively_regulates` relationship lines go-basic strips. Parsed via the EXISTING
   `hdlab.director_kb_bio_sources.parse_gene_ontology()` (already-owned schema-as-config triple
   extractor, `obo_go` mode; reused verbatim, zero new parser engineering). Verified this cycle:
   go-basic.obo yields 0 regulates-family relationship lines; go.obo yields 8,190
   (2,939 REGULATES + 2,627 POSITIVELY_REGULATES + 2,624 NEGATIVELY_REGULATES) `THEORETICAL@grep count
   on disk this cycle`. Reactome/Rhea/WorldTree/OpenStax are explicitly OUT OF SCOPE this cycle
   (director's scoping instruction: no new parser-mode engineering, no EULA/license-unresolved
   sources).

Build a held-out N=40 "X consumes/produces/causes Y in process Z" probe set (see PROBES section),
independently hand-authored (not copy-pasted from CauseNet/GO/any ingested source; provenance =
general world knowledge). Measure recovery rate (fraction of probes reconstructable via a **1-2 hop,
every-hop-causal-typed** graph path) under 4 conditions: BASELINE (CSKG alone), ENRICHED (CSKG +
CauseNet + GO-regulates), SHUFFLE control (enriched graph, relation labels permuted), RANDOM-EDGES
control (baseline + equal-count random non-causal edges instead of the real sources).

## RECOVERY-FUNCTION DEFINITION (exact, falsifiable)
Graph = undirected multigraph over canon'd concept-name nodes (canon = lower; collapse non-alnum runs
to `_`; strip -- IDENTICAL normalization to `exp_cskg_foundation_v1.canon()`, reused verbatim so probe
node ids match CSKG's own node ids without re-mapping). `CAUSAL_RELS` = the relation-type set a hop
must belong to for the hop to count (see CAUSAL_RELS section). For probe `(subject, object)`:
- **1-hop RECOVERED** if an edge `(subject, r, object)` (either direction) exists with `r in
  CAUSAL_RELS`.
- **2-hop RECOVERED** if a node `mid` exists such that `(subject, r1, mid)` AND `(mid, r2, object)`
  (either direction each) both exist with `r1, r2 in CAUSAL_RELS` (BOTH hops must be causal-typed --
  a single causal hop plus one arbitrary connector hop does NOT count; this avoids hub-node false
  positives and matches the strictness of `exp_cskg_foundation_v1.relation_reconstruction_gate`'s own
  affinity-based discriminator, which is also purely relation-type-gated).
- Else NOT recovered.
`recovery_rate` = fraction of the 40 probes recovered (1-hop OR 2-hop) under a given graph condition.

## CAUSAL_RELS bucket (exact; reproduces the scout's disk-verified 14.83% "generous bucket")
`CAUSAL_RELS_BASE` = `{"/r/Causes", "at:xEffect", "at:oEffect", "/r/HasSubevent",
"/r/HasFirstSubevent", "/r/HasLastSubevent"}` (exactly the 6 relations the gather-layer drill's
"generous bucket" cites). Self-test reproduces `sum(counts) / spine_directed_edges = 184,484 /
1,244,136 = 0.1483` -> **MEASURED@data/cskg_foundation_v1/metrics.json:relation_distribution (this
cycle's recompute)** = 14.83%, exact match to the scout's disk-verified figure (Gate-D-style positive-
control reproduction at the same regime, catches a mis-loaded/mis-filtered baseline before the probe
loop runs). `NEW_RELS` = `{"cn:Causes", "REGULATES", "POSITIVELY_REGULATES", "NEGATIVELY_REGULATES"}`.
`ENRICHED_CAUSAL_RELS = CAUSAL_RELS_BASE | NEW_RELS` (used for ALL 4 conditions' recovery function, so
the function itself never changes across conditions -- only the GRAPH changes).

## PROBES (N=40; provenance = hand-authored by exp_dev this cycle, general world/science knowledge,
independent of any resource under test)
40 probes spanning combustion/fire (5), weather/water-cycle (5), general plant biology (5, deliberately
NOT GO-jargon per director's "do not over-weight biology reactions that only Reactome/Rhea would
carry"), human physiology/everyday (8), mechanical/physics (6), household chemistry/cooking (6),
astronomy/geology (5). Each probe = `{id, subject, object, gloss, domain}`, canon'd at load time. Full
list is embedded in the cell as `PROBES` (single source of truth, reviewable in the .py). Two of the
40 (`accident`x`death`-style and `smoking`x`lung_cancer`-style pairs) were DELIBERATELY AVOIDED after
inspecting the CauseNet sample/head during source-vetting this cycle, to keep probe authorship clean
of anything literally observed in the source under test -- documented here as the no-leak audit trail.
`NO_LEAK_AUDIT`: probe subject/object pairs checked against the concept-pairs visible in
`causenet-sample.json` (first 15 rows) and the raw file's first 5 rows inspected during vetting; zero
overlap confirmed by inspection (all 40 probes use distinct subject/object vocabulary from those 20
observed pairs).

## GRAPH CONSTRUCTION PER CONDITION
- **BASELINE**: all spine typed edges from `data/cskg_foundation_v1/edges_shard_*.jsonl` (16 shards)
  + `heldout_edges.jsonl` (this cell's own probes are independent of CSKG's internal held-out split,
  so using the full spine, train+heldout, is the fair "CSKG alone" condition) = 1,238,686 edges.
- **NEW_SOURCE_EDGES**: `causenet_edges` (regex-extracted `(cause,effect)` pairs from the bz2, canon'd,
  self-loops dropped, `sorted(set(...))` deduped) + `go_edges` (REGULATES-family triples from
  `parse_gene_ontology(go.obo)`, term_id resolved to canon'd term NAME via the same parse's `NAMED`
  triples, self-loops dropped, `sorted(set(...))` deduped).
- **ENRICHED** = BASELINE + NEW_SOURCE_EDGES.
- **SHUFFLE control** = ENRICHED edge list with relation labels permuted across the FULL combined
  list (`numpy.random.default_rng(SHUFFLE_SEED).permutation`, fixed seed 20260811, NOT `hash()` or
  `list(set())` -- PYTHONHASHSEED-safe per project determinism discipline), (subject,object) pairs
  held fixed. Same pattern as `exp_cskg_foundation_v1.relation_reconstruction_gate`'s own shuffle
  control (global permutation of ALL train relation labels, not just the new-source subset).
- **RANDOM-EDGES control** = BASELINE + `len(NEW_SOURCE_EDGES)` random edges, endpoints uniformly
  sampled (fixed seed 20260812) from the pooled node vocabulary (BASELINE nodes UNION
  NEW_SOURCE_EDGES' entity names, so the random control has the SAME entity-coverage envelope as the
  real enrichment -- isolates "random pairing + non-causal label" as the ONLY manipulated variable),
  relation type sampled (fixed seed 20260813) from BASELINE's own NON-causal relation-frequency
  distribution (not a synthetic sentinel -- more realistic "same kind of graph noise" than an
  always-excluded label, while still structurally outside `ENRICHED_CAUSAL_RELS` by construction).
  **Honest framing (declared before running, not post-hoc)**: because the recovery function requires
  every hop to be `ENRICHED_CAUSAL_RELS`-typed, and the random edges' relation type is drawn from the
  set of relations NOT in `ENRICHED_CAUSAL_RELS`, this control is expected to reproduce BASELINE
  recovery near-exactly by construction. A failure here (`random_recovery` rising materially toward
  `enriched_recovery`) would indicate an IMPLEMENTATION BUG in the `ENRICHED_CAUSAL_RELS` gating, not
  a scientific finding about graph density -- it is reported as a code-correctness validity check,
  not inflated as an independent discovery. This is declared honestly per the director's own framing
  ("report it honestly either way").

## FALSIFIABLE PRE-REGISTERED BANDS (verbatim from the gather-layer drill, operationalized)
```
gain = enriched_recovery - baseline_recovery
shuffle_collapse_ok = abs(shuffle_recovery - baseline_recovery) <= 0.05
random_stays_low_ok = abs(random_recovery - baseline_recovery) <= 0.10
random_matches_enriched = abs(random_recovery - enriched_recovery) <= 0.05

HARD_FAIL if: gain < 0.10  OR  NOT shuffle_collapse_ok  OR  random_matches_enriched
HARD_PASS if (and only if, HARD_FAIL conditions all false):
    gain >= 0.30  AND  shuffle_collapse_ok  AND  random_stays_low_ok
MIDDLE_BAND: otherwise (gain in [0.10, 0.30), controls clean)
```
HARD_FAIL is checked FIRST (a failed control invalidates an apparent large raw gain).

## CAUSAL-EDGE-FRACTION GAP-CLOSURE METRIC (deliverable per director's instruction)
Report pre/post, both the strict bucket (`/r/Causes` + `cn:Causes`) and the generous bucket
(`CAUSAL_RELS_BASE` + `NEW_RELS`), as fractions of total edges, baseline vs enriched. This is the
concrete, falsifiable "did the gather layer close the disk-verified 1.39%/14.83% causal-sparsity gap"
measurement the drill note calls for as a standing acceptance-gate metric.

## COMPUTE ARCHITECTURE
(c) mixed with justification -- CPU-only, no GPU. This is a DIRECTIONAL GATE / coverage-diagnostic
question (does adding typed causal content raise a structural recall proxy), not a substrate-mechanism
magnitude claim -- per exp_dev.md's COMPUTE-PROPORTIONALITY rule, the cheapest decisive method is a
structural graph/count proxy (adjacency-dict BFS to depth 2 over ~1.2-1.6M edges), NOT any HD
vector/KGE encoding or training fit. Storage strategy: `no_storage` (in-memory adjacency dict per
condition, discarded after recovery computation; nothing persisted to `substrate_index`). Measured
wall time this cycle (component timing tests, this session): CauseNet regex-parse of the full bz2 =
70.4s; GO full-parse = 1.2s; baseline-edge load ~= single-digit seconds; 4x adjacency-dict builds over
up to 1.6M edges each ~= tens of seconds combined. Total FULL estimated <= 4 min, comfortably inside a
single foreground Bash call with an explicit 600s timeout (INLINE-LOCAL MANDATE, since remote dispatch
is unavailable this cycle -- NO ORIGIN PUSH).

## SCHEMA-VET DECLARATIONS
- `cardinality_ok`: N/A, not a sweep-axis cell (4 fixed conditions, not a swept parameter) ->
  declared `cardinality_n/a: "single deterministic pass over 4 pre-defined graph conditions, no swept
  parameter axis"`.
- `crlb_floor_computed`: N/A, no argmax-noise/capacity discriminator -> `crlb_n/a: "structural
  graph-path recall proxy, not a capacity/argmax-noise measurement"`.
- `baseline_in_band` (META_RULE_AG): EXEMPTED, rationale declared inline in "RANDOM-EDGES control"
  honesty note above and here: this is a KB-coverage/recall diagnostic (parallel to
  `exp_cskg_foundation_v1`'s own can-fail gate, which also does not declare AG), not a substrate-
  mechanism arm-vs-baseline-arm gate. A near-zero or zero BASELINE recovery is the EXPECTED and
  diagnostically meaningful starting point (directly matches the disk-verified 1.39% causal-edge
  sparsity), not a saturation/floor design failure requiring regime-iteration. `baseline_in_band_
  exempted: true`.
- `arms_differ_verified`: mandatory, checked at self-test AND full run via a hash of each condition's
  sorted edge-list.
- `final_metrics_atomicity`: `tmp_replace` (single-shot cell, `metrics.json.tmp` -> `os.replace`).
- `except SystemExit: raise` before `except Exception` (not `BaseException`): yes, per template.
- `cell_chunked`: false -- N/A, rationale: "no seed/arm sweep axis; single deterministic pass;
  estimated wall time <=4 min, well under any per-unit-checkpoint-justifying duration."
- `start_marker_written` / `crash_diagnostic_present` / `heartbeat_present`: all true (heartbeat at
  each major stage: baseline loaded, causenet parsed, go parsed, each of the 4 adjacency builds,
  recovery computed).
- `progress_logging`: N/A -- `timeout_s` for this cell is well under the 1800s (30 min) threshold
  that makes `SS 17 PRINT-PROGRESS FLUSHING` mandatory; heartbeats are included anyway (see above) as
  defense-in-depth since this cycle runs INLINE-LOCAL foreground with an operator watching.
- `real_code_path_and_signature_preflight`: self-test constructs the REAL objects at tiny scale --
  reads a real small sample of `edges_shard_00.jsonl`, calls the REAL `parse_gene_ontology()` against
  the REAL `go.obo` file capped via `max_terms=50`, regex-parses the first ~200 real lines of the REAL
  `causenet-precision.jsonl.bz2`. Declared entrypoints: `parse_gene_ontology`, `_extract_causenet_pairs`,
  `_recover`, `_canon`. Positive-control sanity: a KNOWN CSKG causal edge from the loaded sample must
  recover (hop=1) at baseline; a synthetic disconnected pair must NOT recover (hop=0) -- guards against
  a vacuously-always-true or always-false recovery function.
- `deterministic_seeding`: true -- all RNG via `numpy.random.default_rng(<fixed int seed>)`;
  `sorted(set(...))` for all dedupe; no `hash()`-seeded RNG.

## TIMEOUT / RUN MODE
`--self-test`: tiny-scale, target <10s. FULL (default `--run-mode full`, no `--self-test` flag):
target <=4 min measured; INLINE-LOCAL foreground Bash call with explicit `timeout: 600000` (10 min
cap, per INLINE-LOCAL MANDATE) as the safety margin. Not dispatched via `queue_add.sh` /
`local_cpu_queue` / `remote_cpu_queue` this cycle (NO ORIGIN PUSH constraint makes remote dispatch
mechanically unavailable; local_cpu_queue is FULL-run-restricted per the 2026-07-01 USER lock, and
this run is lightweight enough that the INLINE-LOCAL MANDATE's foreground path is the correct,
disciplined choice rather than a queue workaround).
