# Pre-reg: substrate_director_kb_remote_provision_v1

Date: 2026-06-27
Anchor: substrate_director_kb_remote_provision_v1
Cell: experiments/exp_substrate_director_kb_remote_provision_v1.py
Queue: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive)
Wave: Tier-1 from research drill `notes/research_drill_kb_referent_missing_systemic_3x_2026-06-27.md`

Primitives composed:
  - tools/sync_canonical_kb_to_remote.sh (atomic-swap SCP)
  - hdlab/director_kb_query.DirectorKBQuery (post-sync sample-query equivalence check)

## Motivation

Three cells HARD_FAILed 2026-06-27 with KB_REFERENT_MISSING:
  - exp_kb_partition_by_source_class_v2 (ANCHOR 1)
  - exp_kb_dual_store_audit_v1 (ANCHOR 5)
  - exp_kb_coarse_grain_at_promotion_v2_chain_grade_path (ANCHOR 3)

Common root cause: `load_default_kb(REPO)` prefers
`data/substrate_director_kb_v1/manifest.json` but the canonical KB exists
only on the laptop; it has never been mirrored to the remote_cpu_queue
runner. Without provisioning, ANCHOR 5 dual-store stays blocked
permanently (its test target IS the canonical substrate; a self-contained
mini-KB rewrites what it measures).

## Scope

This is a one-shot provisioning cell that the remote_cpu runner executes
to verify the canonical KB is freshly mirrored from local. Cell orchestration:
the cell runs on remote; it SSH's BACK to laptop's `sync_canonical_kb_to_remote.sh`
to trigger the push, then verifies via DirectorKBQuery.load_default_kb().

The simpler routing (run sync_canonical_kb_to_remote.sh from laptop, then
verify on remote) is delegated to the cell's 3 arms below: ARM 1 runs the
local freshness check, ARM 2 invokes the sync script, ARM 3 SSH-verifies
the remote landed-KB matches local.

## Arms (3 mandatory)

### ARM_LOCAL_INGEST_FRESHNESS_CHECK
Verify local canonical KB exists and was rotated by continuous-ingest within
the last 24h. Reads:
  - data/substrate_director_kb_v1/manifest.json (n_entities, kb_version, encoder, n_dim)
  - mtime of manifest.json (freshness)
Asserts:
  - manifest.n_entities >= 500_000
  - manifest.coverage_ratio >= 0.99
  - Mtime within 86400s (24h) of run start (continuous-ingest health)
ok = all assertions hold.

### ARM_REMOTE_SYNC
Invoke `bash tools/sync_canonical_kb_to_remote.sh`. Capture stdout/stderr +
exit code. Records sync wall-clock, bytes transferred (from audit log
appended by the script), local-vs-remote n_entities post-swap.
ok = exit code 0 AND audit log "complete" line shows ok:true.

### ARM_REMOTE_VERIFY
Open SSH connection to marsh@home and run an in-line Python that:
  - Imports DirectorKBQuery from hdlab.director_kb_query
  - Calls load_default_kb() with REPO=C:/dev/hd-instrument
  - Prints n_entities, kb_version, schema_version, encoder_name
  - Runs a sample query "substrate director kb ingest" with k=3 and prints
    top-1 atom string + cosine
Then compares remote outputs against local equivalents:
  - n_entities match (exact equality)
  - kb_version match (string equality)
  - encoder_name match (string equality)
  - Top-1 atom string for the canary query matches (string equality)
ok = all 4 match.

## Pre-reg bands (HARD-LOCKED; META_PROSPECTIVE_BANDS_FRESH_SEEDS)

HARD_PASS (all four conditions):
  - local n_entities >= 500_000 AND coverage_ratio >= 0.99
  - remote_post_sync n_entities EXACTLY equals local n_entities
  - remote_post_sync load_default_kb() opens without exception
  - remote_post_sync top-1 atom for canary query exactly matches local top-1
    (sample-query equivalence)

MIDDLE_BAND:
  - local OK but remote_post_sync n_entities in [0.95, 1.0) * local
    (partial sync / network truncation; still operational but suspect)

HARD_FAIL:
  - local n_entities < 500_000 OR coverage_ratio < 0.99
  - OR remote_post_sync n_entities == 0
  - OR remote manifest unparseable
  - OR SSH connection failed
  - OR SCP encountered error
  - OR canary-query top-1 atom string differs between local and remote

## Cardinality (D4 mandatory)

EXPECTED_N_ARMS = 3 (local_freshness / remote_sync / remote_verify).
HARD_FAIL_CARDINALITY_BREACH = len(arms) != 3.

## Discriminator-must-survive-scale (D1)

Not applicable: this cell verifies a binary "did the mirror land identically"
property. The discriminator is "exact n_entities equality AND exact top-1
atom match"; this property does not weaken with scale (the canonical KB IS
the full 577k-entity scale).

## Smoke discipline

NO LOCAL smoke (USER 2026-06-27 NO LOCAL directive). The cell is dispatched
to remote_cpu_queue with --self-test only (no --smoke run). Self-test
verifies argparse + import + verdict-band formula self-tests pass. No
network operation runs in --self-test.

For full dispatch, the cell runs ARM_REMOTE_SYNC which IS the heavy
operation. There is no separate smoke/full distinction here; provisioning
is binary.

## Substrate-only-decode gate

n_llm_calls = 0 (deterministic SCP + DirectorKBQuery sample queries; no
transformers anywhere in the loop).

## Real data / synthetic provenance

100% real. The canonical KB built by the continuous-ingest scheduled task
is the input; no synthetic atoms.

## Honest scope

This cell verifies the MIRROR works. It does NOT re-test:
  - Whether the canonical KB ingest pipeline is correct (separate cell).
  - Whether load_default_kb() correctly prefers canonical over legacy
    (covered by hdlab unit tests).
  - Whether downstream cells (ANCHOR 3/5) succeed once provisioned (their
    own cells).

## Required REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`, `summary.local_n_entities`,
`summary.remote_n_entities`, `summary.local_kb_version`,
`summary.remote_kb_version`, `summary.canary_query_top1_match`,
`summary.sync_wall_s`.

## Cadence

After first chain-grade PASS, register the sync script as a Windows
scheduled task on the laptop at 6h cadence (or post-canonical-ingest hook),
mirroring the existing `hd_director_kb_continuous_ingest` task pattern.

## Estimated cost

ARM_LOCAL_INGEST_FRESHNESS_CHECK: < 1s.
ARM_REMOTE_SYNC: 5-30 min (4.9 GB over LAN; first sync slowest).
ARM_REMOTE_VERIFY: 30-90s (SSH + remote python KB load).
Total wall: ~30 min worst case; ~6 min steady-state when KB already up-to-date.

## Routing

`remote_cpu_queue` on marsh@home (per USER 2026-06-27 NO LOCAL directive).
Push + queue_add via orchestrator (push is harness-DENIED to exp_dev).

NOTE on cell-host paradox: this cell needs to ORCHESTRATE the sync, and the
sync itself runs from laptop->remote. We pick the simpler path: cell runs
on remote, ARM 2 invokes sync via `ssh marsh@<laptop>` reverse-SSH to
trigger laptop-side `bash tools/sync_canonical_kb_to_remote.sh`. If reverse
SSH not available on this network, cell falls back to "instruction to
Director: invoke sync manually then re-dispatch verify-only cell." The
cell's HARD_FAIL band catches both modes honestly.
