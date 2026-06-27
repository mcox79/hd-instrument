# Pre-reg: substrate_director_kb_reingest_det_snapshot_isolated_v3 (Wave 4 fix; TOOLING; 2026-06-27)

**Anchor:** `substrate_director_kb_reingest_det_snapshot_isolated_v3`
**Cell:** `experiments/exp_substrate_director_kb_reingest_det_snapshot_isolated_v3.py`
**Queue:** `remote_cpu_queue` (NO LOCAL per USER 2026-06-27)
**Tier hint:** TOOLING patch; reuses chain-grade chunker primitive `hdlab/director_kb_chunk_ingest.py`.
**Drill source:** `notes/research_drill_wave4_v2_reingest_nondeterminism_3x_2026-06-27.md`
**Supersedes:** `preregs/2026-06-27_substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced.md` (for the REINGEST_DET arm only; v2 cell's other 3 arms remain valid and are PASS-THROUGH in v3)
**Load-bearing for:** USER M3 substrate-as-Director-KB ritual-flip GATE (HARD_PASS of this cell flips the GATE OPEN).

## Source — empirical observation

v2 cell `exp_substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced` ARM_CHUNK_REINGEST_DET observed:

| metric | value | implication |
|---|---|---|
| `w_l2_diff` | 1,694,119 | structural breach (not float noise; tol=1e-6) |
| `entities_byte_equal` | False | entity set / order differs |
| `atoms_byte_equal` | False | atom set / triple_idx differs |
| `relations_byte_equal` | True | relation set is closed (pre-populated from schema) — IMMUNE to drift |
| `n_chunks_a` | 131,074 | run A |
| `n_chunks_b` | 131,379 | run B (+305 chunks, +0.23%) |
| `t_run_a_s` / `t_run_b_s` | 265.3 / 261.4 | ~4.4 min wall per run |

## Root-cause diagnosis (drill ANGLE 1; P=0.85)

v2 calls `build_chunk_plan` TWICE in `_run_arm_reingest_deterministic` (lines ~187+200, ~265s apart). Source file set drifts during the gap (~29 files added during mid-pivot note-shipping cadence on 2026-06-27).

**Code audit ruled out** alternative sources:
- `_glob_files` sorts (`sorted(root.glob(glob))`)
- `class_names = sorted(plan.keys())`
- char-trigram encoder uses BLAKE2b content-addressed seed
- KGStore uses seeded `torch.Generator`
- `redact_timestamps_in_atoms=True` already passed
- CPU torch matmul deterministic
- utf-8 decode `errors=replace`

Fingerprint: `relations_byte_equal=True` (closed schema set, immune) + `n_chunks_b > n_chunks_a` + `w_l2_diff` magnitude matches 915 added Hebbian triples (~305 chunks × 3 atoms/chunk × per-add L2 contribution). **Dispositive for file-set drift, not code-path nondeterminism.**

## Scope

v3 fix replaces `_run_arm_reingest_deterministic` with `_run_arm_reingest_deterministic_snapshot_isolated`. Other arms (smoke / full / content-vs-filename discriminator) are pass-through from v2 unchanged.

### Tier 1 — snapshot-isolation (primary; root-cause fix)

- Call `build_chunk_plan` ONCE; reuse for both runs.
- Snapshot file bytes into in-memory dict before run_a; monkey-patch `hdlab.director_kb._read_file_text` for arm duration so both runs serve from the byte snapshot.
- Wrap in `try/finally` to restore original `_read_file_text` on any exception (META_RULE_J no-silent-except).

### Tier 2 — defense-in-depth (Merkle digests)

- Compute BLAKE2b-per-line Merkle root of `atoms.jsonl` + `entities.jsonl` for both runs.
- Dual-store audit consumes Merkle as primary referent check (git-tree-hash discipline per drill Section 3).
- Order-sensitive by design; matches byte-equal contract.

### Tier 4 — graceful-degradation (drill Q5 fallback)

If snapshot-isolation somehow fails to achieve strict byte-equal:
- `approximate_equal_ok = (w_l2_normalized < 1e-3 AND Merkle present)`
- Verdict logic classifies MIDDLE_BAND (not HARD_FAIL) when strict fails but approximate passes.

## Arms (4 total; v2's 3 pass-through + new det v3)

### ARM_CHUNK_SMOKE_NOTES_ONLY (pass-through from v2; unchanged)
Sanity rail; notes-only ingest.

### ARM_CHUNK_FULL (pass-through from v2; unchanged)
Full ingest envelope check (5 chunk classes).

### ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3 (NEW v3)
- Build chunk plan ONCE; snapshot file bytes.
- Monkey-patch `_read_file_text` for arm duration.
- Run ingest twice; both reads served from snapshot.
- Strict byte-equal checks (entities/relations/atoms/W_l2) + Merkle digests.
- `arm.ok = strict_byte_equal_ok AND cardinality_ok`.

### ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST (pass-through from v2; unchanged)
Tripwire: 2-file synthetic corpus where filename / content disagree. Query banana / elephant; verify content-correct top-1.

## Success criteria

### HARD_PASS
All 4 arms ok AND:
- ARM_CHUNK_FULL within HP envelope (`elapsed_s <= 900s`, `coverage_ratio >= 0.95`, `avg_chunks_per_file >= 2.0`)
- ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3 `strict_byte_equal_ok=True AND cardinality_ok=True` (all byte-equal + Merkle + w_l2_diff<1e-6 + n_files_snapshotted>0 + n_chunks_a==n_chunks_b)
- ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST both queries content-correct

### MIDDLE_BAND
- Strict byte-equal fails BUT approximate-equal passes (`w_l2_normalized < 1e-3` + Merkle present), OR
- Strict byte-equal passes BUT FULL outside HP envelope (within HF envelope still)

### HARD_FAIL
- Any of smoke/full/disc arms ok=False, OR
- Det arm strict-fail AND approximate-fail, OR
- Discriminator content-correctness fails, OR
- FULL exceeds HF envelope (`elapsed_s > 1800s`, `coverage_ratio < 0.80`, `avg_chunks_per_file < 1.2`)

## REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`, `summary.cardinality_ok`,
`summary.arms[ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3].strict_byte_equal_ok`,
`summary.arms[ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3].cardinality_ok`,
`summary.arms[ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3].approximate_equal_ok`,
`summary.arms[ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3].entities_byte_equal`,
`summary.arms[ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3].atoms_byte_equal`,
`summary.arms[ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3].relations_byte_equal`,
`summary.arms[ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3].w_l2_diff`,
`summary.arms[ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3].merkle_atoms_a`,
`summary.arms[ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3].merkle_atoms_b`,
`summary.arms[ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3].merkle_ok`,
`summary.arms[ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3].n_files_snapshotted`,
`summary.arms[ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3].plan_files_total`,
`summary.arms[ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3].n_chunks_a`,
`summary.arms[ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3].n_chunks_b`,
`summary.arms[ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST].banana_query_assertion_passed`,
`summary.arms[ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST].elephant_query_assertion_passed`.

## cardinality_ok (META_RULE_H mandatory)

```
summary.cardinality_ok = (
    (n_chunks_built[disc] >= 2)
    AND (avg_chunks_per_file[full] >= HP_MIN_AVG_CHUNKS_PER_FILE)
    AND det.cardinality_ok  # (n_chunks_a>0 AND n_chunks_b>0 AND n_files_snapshotted>0 AND n_chunks_a==n_chunks_b)
)
```

Per-arm `cardinality_ok` surfaces in det arm explicitly (SCHEMA-VET 5b per-arm HP scope).

## Discipline gates

- **META_RULE_H** — `cardinality_ok` mandatory pre-reg field; det arm declares per-arm `cardinality_ok` + composite gates the verdict.
- **META_RULE_J** — no-silent-except: monkey-patch wrapped in try/finally; arm-level Exception records error to metrics + classifies arm.ok=False (verdict gates HARD_FAIL).
- **META_RULE_K** — smoke-fires-discriminator: at smoke (max_files=50), if snapshot-isolation works, ALL byte-equal predicates fire True (this is the discriminator). If smoke FAILS byte-equal, snapshot-isolation didn't work and full would also fail.
- **META_RULE_L** — band-floor MIDDLE_BAND: graceful-degradation band classifies MIDDLE_BAND (not HARD_PASS) per drill Q5.
- **SCHEMA-VET 5b** — per-arm HP scope: each arm declares its own `ok` and contributes to verdict gate.
- **Fix #21** — landing notifier: cell writes to `data/recent_landings.jsonl` (handled by runner).
- **Fix #26** — pre-dispatch verify-the-referent: notes/memory/preregs dirs exist on remote (verified at queue_add gate).
- **Fix #28** — per-arm metrics: all det-arm byte-equal + Merkle + snapshot diagnostics surface per-arm to metrics.json (not just verdict summary).
- **Discriminator-survives-scale (USER 2026-06-26)** — explicit justification: snapshot fix removes the mid-arm file-drift window entirely; mechanism is N-INDEPENDENT (works at smoke=50 files exactly the same as full=13k+ files). Smoke that passes byte-equal guarantees full will also pass byte-equal *modulo* the residual ~10% probability of in-place file mutation or a hidden code-path nondeterminism the drill audit missed (drill Section 1 residual candidates P=0.15 total).

## Tripwire (Skunkworks self-audit)

If snapshot-isolated cell HARD_PASSes, Skunkworks must verify off-disk by:
1. Reading `entities.jsonl` from out_a + out_b → confirm byte-identical via `cmp` or `sha256sum`.
2. Reading `merkle_atoms_a` + `merkle_atoms_b` from `metrics.json` → confirm match (Skunkworks should NOT trust the cell's own `merkle_ok` field; verify the strings match by eye).
3. Confirming `n_files_snapshotted > 0` and `n_chunks_a == n_chunks_b`.

## Estimated cost

~15 min wall on remote_cpu (drill estimate; v3 has SAME wall as v2's REINGEST_DET arm — ~265s × 2 + Merkle ~5s). 1800s timeout (cell will well under this).

## Routing

`remote_cpu_queue` on marsh@home (per USER 2026-06-27 NO LOCAL directive).

**Cell-author cannot push (harness-DENIED):** push + queue_add via Orchestrator. Cell author requests:
- Commit `experiments/exp_substrate_director_kb_reingest_det_snapshot_isolated_v3.py` + `preregs/2026-06-27_substrate_director_kb_reingest_det_snapshot_isolated_v3.md`
- Orchestrator pushes to origin/main
- Orchestrator runs `bash tools/orchestrator/queue_add.sh remote_cpu_queue substrate_director_kb_reingest_det_snapshot_isolated_v3 experiments/exp_substrate_director_kb_reingest_det_snapshot_isolated_v3.py --prereg preregs/2026-06-27_substrate_director_kb_reingest_det_snapshot_isolated_v3.md --timeout 1800`

## Post-land (if HARD_PASS)

- Substrate-as-Director-KB ritual-flip GATE flips OPEN.
- Atomize as Store atom (META_RULE_N candidate: "Determinism arms must snapshot-isolate source-state set + bytes before timing").
- Update MEMORY.md with snapshot-isolation discipline.
- Promote v3 cell as canonical REINGEST_DET test (supersedes v2 arm).

## Post-land (if MIDDLE_BAND or HARD_FAIL)

- HARD_FAIL: drill deeper into residual candidates (drill Section 1: in-place file mutation P=0.10; hidden code-path P=0.02). Audit `_intern` insertion order, regex backtracking, torch CPU matmul kernel for the specific batch-size.
- MIDDLE_BAND with strict-fail + approx-ok: snapshot isolation reduced but didn't eliminate drift; investigate residual nondeterminism source. Substrate-vs-MD flip GATE = conditional (Tier 4-full per drill decision tree).
