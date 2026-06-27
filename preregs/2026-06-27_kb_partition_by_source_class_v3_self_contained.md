# Prereg: kb_partition_by_source_class_v3_self_contained

Date: 2026-06-27
Anchor: kb_partition_by_source_class_v3_self_contained
Cell: experiments/exp_kb_partition_by_source_class_v3_self_contained.py
Queue: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive)
Wave: ANCHOR 1 partition v3 rescue (v2 HARD_FAIL was KB_REFERENT_MISSING)

Primitives composed (chain-grade):
  - hdlab/director_kb_chunk_ingest.py (build_chunk_plan + run_chunk_ingest)
  - hdlab/director_kb_query.py (DirectorKBQuery)
  - hdlab/director_kb.py (load_schema)
  - hdlab/char_trigram_encoder.py (default encoder)
  - hdlab/kg_traversal.py (KGStore)

## Motivation

v2 HARD_FAILed on remote with KB_REFERENT_MISSING: the cell loaded
`load_default_kb(REPO)` which expects an upstream
`data/exp_substrate_director_kb_ingest_v1/_arm_full/kb` directory; that
directory exists on local but is NOT on the remote_cpu runner (it is an
artifact of a local-only ingest cell).

The MECHANISM (source-class routing + Path A relaxed criterion + Path B
cross-cutting permissible-class queries) is UNCHANGED from v2; only the
LOAD path is fixed: v3 builds a labeled mini-KB IN-CELL by calling
`hdlab.director_kb_chunk_ingest.run_chunk_ingest` against
`notes/`, `memory/`, and `preregs/` from the repo root. This makes the
cell self-contained (no upstream cell required) and therefore remote-
ready.

## v3 mechanism (mechanism vs v2 unchanged; only load path differs)

ARMS (3 mandatory; identical to v2):
  - ARM_SINGLE_W_BASELINE             - unpartitioned baseline reference
  - ARM_PARTITIONED_W_EQUAL_CAPACITY  - source_class filter; routing acc
  - ARM_PARTITIONED_W_MEMORY_OVERSIZED - USER memory partition 4x k-floor

ROUTED_QUERIES (28 items; identical to v2; multi-class permissible for
cross-cutting queries per Path B). Smoke uses first 10.

Pre-flight in main():
  1. Load schema (REPO/config/director_kb_schema.json).
  2. Build chunk plan with chunk_classes = ("note", "memory", "prereg")
     and max_files_per_class = SELF_CONTAINED_MAX_FILES (default 200;
     smoke 50). Drops the v1 dependency entirely.
  3. Run chunk ingest into REPO/data/exp_<anchor>/_inline_kb/.
  4. Construct DirectorKBQuery(kb_dir=<inline_kb>).
  5. Run 3 arms; produce v2 verdict bands verbatim.

## Pre-reg bands (HARD-LOCKED; META_PROSPECTIVE_BANDS_FRESH_SEEDS;
identical to v2)

HARD_PASS (all four conditions):
  - routing_accuracy >= 0.95
  - cross_partition_leak_rate < 0.05
  - ratio_resolved >= 0.80
  - (n_ud == 0) OR (ud_retention >= max(non_ud - 0.10, 0.70))

MIDDLE_BAND:
  - routing_accuracy in [0.90, 0.95) OR ratio_resolved in [0.70, 0.80)
    OR ud_retention close to floor (within 0.15)
  - mechanism operational (leak < 0.05; ratio >= 0.70)

HARD_FAIL:
  - routing_accuracy < 0.90 (below MB floor)
  - OR cross_partition_leak_rate >= 0.05
  - OR ratio_resolved < 0.70
  - OR any arm raised an exception
  - OR ingest produced 0 entities (KB build failed)

## Cardinality (D4 mandatory)

EXPECTED_N_ARMS = 3 (baseline / partitioned-equal / memory-oversized).
HARD_FAIL_CARDINALITY_BREACH = len(arms) != 3.
EXPECTED_INGEST_ENTITIES_MIN = 100 (smoke) / 500 (full); below = HF.

## Discriminator-must-survive-scale (D1)

Smoke runs at 50 files/class with first 10 ROUTED_QUERIES; full uses
200 files/class with all 28 ROUTED_QUERIES. Source-class routing is a
filter operation; correctness should be regime-stable (not a saturation-
sensitive measurement). The v2-relaxed bands (Path A) already account
for the partition's strict-subset structural lossiness; v3 inherits that
relaxation unchanged.

## Substrate-only-decode gate

n_llm_calls per arm = 0 (deterministic chunker + char-trigram encoder +
KGStore; no transformers).

## Real data / synthetic provenance

Real data: notes/ + memory/ + preregs/ from the repo tree at run-time.
No synthetic atoms. The cell uses the actual substrate codebase as its
labeled corpus.

## Honest scope

Tests whether source_class routing (with v2 Path A relaxation + Path B
multi-class permissible sets) holds when the labeled KB is built IN-CELL
from repo-local sources (no upstream dependency). Does NOT re-test the
ingest pipeline correctness (that is ANCHOR 1 v2 / content_chunk_v1's
job).

## Verdict logic (4-class; v2 verbatim)

HARD_PASS if all four PASS conditions met.
HARD_FAIL if any HARD_FAIL trigger fires.
MIDDLE_BAND if operational + UD close to floor.
HARD_FAIL otherwise (default).
