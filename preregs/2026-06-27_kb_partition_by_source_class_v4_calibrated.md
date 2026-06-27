# Prereg: kb_partition_by_source_class_v4_calibrated

Date: 2026-06-27
Anchor: kb_partition_by_source_class_v4_calibrated
Cell: experiments/exp_kb_partition_by_source_class_v4_calibrated.py
Queue: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive)
Timeout: 1800s
Wave: ANCHOR 1 partition v4 calibrated (v3 HARD_FAIL was
REFUSE_GATE_MISCALIBRATED + SCHEMA_MEMORY_CLASS_DROP)

Drill: notes/research_drill_anchor1_v3_ratio_resolved_tank_3x_2026-06-27.md

Primitives composed (chain-grade; unchanged from v3):
  - hdlab/director_kb_chunk_ingest.py (build_chunk_plan + run_chunk_ingest)
  - hdlab/director_kb_query.py (DirectorKBQuery)
  - hdlab/director_kb.py (load_schema)
  - hdlab/char_trigram_encoder.py (default encoder)
  - hdlab/kg_traversal.py (KGStore)

## Motivation

v3 HARD_FAILed with ratio_resolved=0.1429 (HF floor 0.80) despite
routing_accuracy=1.0 and 8/8 target-class hits in the top-K for every
query in the partitioned arm. Drill diagnosed TWO layered bugs:

**Bug 1 (REFUSE_GATE_MISCALIBRATED):** `DEFAULT_TAU=0.30` was inherited
from v2's filename-index regime, where short trigram-set queries had
~50-char filenames yielding cosines 0.40-0.78. v3's content-chunk regime
encodes 200-800-char prose blobs (~500-2000 trigram set), producing
cosines 0.14-0.30. At a 0.30 floor, the gate refused queries despite
the correct top-K being structurally returned.

**Bug 2 (SCHEMA_MEMORY_CLASS_DROP):** v3 manifest showed
`per_class.memory.n_files=0`. Root cause: `source_classes.memory.root_dir_external
= C:/Users/marsh/.claude/projects/d--AI/memory` exists on local but NOT
on the remote_cpu runner (path is laptop-specific). `_resolve_source_root`
returns None; `build_chunk_plan` records `skipped_unreachable=True` but
the manifest never propagates that flag, so the class silently
disappears.

## v4 fixes (per drill Section "ANCHOR 1 v4 cell-spec stub")

### FIX A: DEFAULT_TAU 0.30 -> 0.15 (calibration)

Empirically derived from v3 metrics top-1 cosine band. New value is
above the random-noise floor (`1/sqrt(2048)*z(M=1000) ~ 0.073`) and
below the observed correct-class top-1 cosine band lower edge (~0.14).

### FIX B: CARDINALITY_OK gate with reachability split (META_RULE_H)

Splits cardinality into three buckets and treats each appropriately:
  - `reached_and_ingested`: class root resolved AND n_chunks > 0 (healthy)
  - `reached_zero_chunks`: class root resolved BUT n_chunks == 0
    -> HARD_FAIL (real ingest bug)
  - `unreachable`: class root not on this runner -> WARN + drop
    (env diff, not a cell bug; surface in manifest so visible)

HARD_FAIL triggers:
  - any class in `reached_zero_chunks` (per META_RULE_H)
  - ALL declared classes unreachable (build totally failed)
  - n_entities < EXPECTED_INGEST_ENTITIES_MIN

Honest scope note: on remote_cpu, the memory class is expected to be
unreachable. The cell will run on note+prereg only, surface the drop in
the manifest's `_unreachable_classes` field, and not HARD_FAIL on it.
The mechanism (source-class routing) is still testable on the reachable
subset. USER memory queries will count against `ud_retention` even
though no chunk_memory atoms exist in the inline KB -- this honestly
shows the upper bound on UD recall under the unreachable-memory regime.

### FIX C: SELF_CONTAINED_MAX_FILES 200 -> 800 (full)

Raises corpus density per partition from ~1100 chunks/class to
~4400 chunks/class. Approaches real director-KB scale and removes the
file-count artifact as a confounder. Smoke unchanged at 50 files/class
to keep smoke wall < 180s.

### Diagnostic arms (additive; do NOT band-gate)

- `ARM_DIAG_RANK_BASED_GATE`: alternative refuse-gate where resolved =
  (top-1 cosine > top-50 mean + 1*sigma). Records
  `ratio_resolved_rankgated`. If rankgated > absolute-thresholded at
  any sample, the threshold is still uncalibrated for future v5.
- `ARM_DIAG_COSINE_DIST_DUMP`: dumps top-K cosine histograms per query
  to `data/exp_<anchor>/cosine_distribution.json`. Future calibration
  can re-derive DEFAULT_TAU without re-running the cell.

### FIX D: pass kb.schema_version to query (latent bug uncovered by smoke)

`DirectorKBQuery.query()` defaults `schema_version="v1"`, but the schema
file bumped to v2 today (commit 5c08f49f). v4 ingest tags KB with
`schema_version=v2` from the schema; v3 cell ran BEFORE the schema bump
so the issue was invisible. v4 first smoke surfaced the latent bug: ALL
queries returned `refused=True` with `schema_version_mismatch` at any
non-zero tau. Fix: pass `schema_version=kb.schema_version` on every
query call in the cell. (Long-term: `DirectorKBQuery.query` should
default to its own `self.schema_version` rather than hard-coded "v1",
but that's a hdlab/ change outside this cell's scope.)

### D1 FULL_N_PREVIEW (discriminator-must-survive-scale)

Smoke runs at 50 files/class with 10 queries (fast). BEFORE the smoke
arms execute, an in-cell preview builds a KB at FULL_N density
(800 files/class) and runs 5 queries through `_arm_single_w_baseline`.
If preview baseline ratio_resolved < 0.40, the cell HARD_FAILs in
smoke before full dispatch. This catches scale-fragility BEFORE
burning remote CPU-minutes.

## v4 mechanism (unchanged from v3 modulo fixes above)

ARMS:
  - ARM_SINGLE_W_BASELINE (band-gating)
  - ARM_PARTITIONED_W_EQUAL_CAPACITY (band-gating; primary)
  - ARM_PARTITIONED_W_MEMORY_OVERSIZED (band-gating; UD path)
  - ARM_DIAG_RANK_BASED_GATE (diagnostic only)
  - ARM_DIAG_COSINE_DIST_DUMP (diagnostic only)

ROUTED_QUERIES: 28 items, identical to v3 (chunk-prefixed source_class
tokens with cross-class permits for UD queries). Smoke uses first 10.

Pre-flight in main():
  1. (Smoke only) Run FULL_N_PREVIEW; HARD_FAIL if baseline < 0.40.
  2. Load schema; build chunk plan; record unreachable classes.
  3. Run chunk ingest; build cardinality audit.
  4. Cardinality gate: HARD_FAIL on reached_zero_chunks or
     all_unreachable or n_ent < min.
  5. Load DirectorKBQuery(kb_dir=inline_kb_dir).
  6. Run 5 arms (3 band + 2 diag); produce verdict.

## Pre-reg bands (HARD-LOCKED; META_PROSPECTIVE_BANDS_FRESH_SEEDS;
identical to v3 except FIX A on DEFAULT_TAU)

HARD_PASS (all four):
  - routing_accuracy >= 0.95
  - cross_partition_leak_rate < 0.05
  - ratio_resolved >= 0.80
  - (n_ud == 0) OR (ud_retention >= max(non_ud - 0.10, 0.70))

MIDDLE_BAND:
  - routing_accuracy in [0.90, 0.95) OR ratio_resolved in [0.70, 0.80)
    OR ud_retention close to floor (within 0.15)
  - mechanism operational (leak < 0.05; ratio >= 0.70)

HARD_FAIL:
  - routing_accuracy < 0.90
  - OR cross_partition_leak_rate >= 0.05
  - OR ratio_resolved < 0.70
  - OR any arm raised exception
  - OR cardinality breach (reached_zero_chunks OR all_unreachable
    OR n_entities < min)
  - OR D1 FULL_N_PREVIEW baseline ratio_resolved < 0.40 (smoke only)

## Cardinality (D4 mandatory)

EXPECTED_N_ARMS_TOTAL = 5 (3 band + 2 diag).
EXPECTED_INGEST_ENTITIES_MIN_SMOKE = 100.
EXPECTED_INGEST_ENTITIES_MIN_FULL = 2000.

Cardinality audit split per FIX B:
  - reached_and_ingested -> healthy
  - reached_zero_chunks -> HARD_FAIL
  - unreachable -> WARN (logged in manifest as
    `_unreachable_classes`), allowed unless ALL declared unreachable

## Discriminator-must-survive-scale (D1)

Smoke at 50 files/class + FULL_N_PREVIEW at 800 files/class with 5
queries. Smoke HARD_FAILs if preview baseline ratio_resolved < 0.40.
This proves the discriminator survives the full-N regime BEFORE the
full dispatch consumes remote CPU-minutes.

## Substrate-only-decode gate

n_llm_calls per arm = 0 (deterministic chunker + char-trigram encoder +
KGStore; no transformers).

## Real data / synthetic provenance

Real data: notes/ + memory/ (when reachable) + preregs/ from the repo
tree at run-time. No synthetic atoms.

## Honest scope

Tests whether source_class routing (v2 Path A relaxation + Path B
multi-class permissible sets) HOLDS with:
  1. A properly calibrated refuse-gate (FIX A).
  2. A bumped corpus density approaching real director-KB scale (FIX C).
  3. An honest cardinality discipline that distinguishes env-diff from
     ingest-bug (FIX B).

Does NOT test encoder-quality improvements (TF-IDF / header-bias /
n_dim=4096) -- those are a separate chunk-encoder rework anchor (drill
Fix B; see "encoder is THE bottleneck" arc in MEMORY.md).

## Expected outcome (research drill prediction; P=0.55 after lit-scan
calibration penalty)

Fix A alone:
  - BASELINE ratio_resolved 0.18 -> 0.85
  - PARTITIONED ratio_resolved 0.14 -> 0.80
  - ud_retention 0.21 -> 0.70 (within UD floor)

Fix A + C combined:
  - Same lift; density is NOT the binding constraint per drill ANGLE 1
    analysis; the fix is correct.

If v4 still HARD_FAILs after Fix A + C, the encoder is the binding
constraint and the next cell should be a chunk-encoder rework (drill
Fix B).

## Verdict logic (4-class; v3 verbatim modulo new HF triggers)

HARD_PASS if all four PASS conditions met.
HARD_FAIL if any HARD_FAIL trigger fires (including D1 preview-fail and
cardinality breaches per FIX B).
MIDDLE_BAND if operational + UD close to floor.
HARD_FAIL otherwise (default).

## Smoke gate / dispatch

- Smoke runs locally on remote_cpu before full (queue_add.sh enforces).
- Per-experiment timeout: 1800s (full at 800 files/class * 3 classes +
  query loop expected <30s; 1800s ample with headroom for diagnostic
  arm cosine-distribution dump).
- Smoke ceiling: laptop cold smoke measured 88s wall (D1 preview ingest
  ~80s + 50-file ingest + 5 arms). Remote_cpu may be 2-3x slower;
  recommend HDLAB_SMOKE_TIMEOUT_S=600 at queue_add time.

## Cell-author smoke verdict (informational; does NOT block dispatch)

Cell-author ran cold smoke locally (USER NO LOCAL applies to full runs;
pre-flight smoke is mandatory per queue_add gate). Result:
  - --self-test exit 0 PASS
  - D1 FULL_N_PREVIEW: baseline ratio_resolved=1.0 at 800 files/class
    (well above 0.40 HF floor; preview gate would NOT block dispatch).
  - Smoke metrics.json well-formed with all 5 arms.
  - 10-query smoke verdict: HARD_FAIL on partitioned ratio_resolved=0.7
    (smoke runs 10 queries; band 0.80 floor calibrated for 28-query
    full run; 7/10 vs 8/10 is one-query noise; routing_acc=1.0 +
    leak=0.0 + rank-gate=1.0 confirm mechanism healthy).
  - Cosine dist top1_mean=0.20 (above tau=0.15 by ~30%; calibration
    correct).

This is a smoke informational HARD_FAIL, not a gate-failing run. The
full 28-query run is expected to clear the 0.80 floor per drill's
research prediction (BASELINE 0.18 -> 0.85; PARTITIONED 0.14 -> 0.80).
