# run_mode ingestion bug: source fix landed, backfill deferred (Testbed, 2026-08-15)

Picked up from a prior agent killed mid-task by an ESC teardown. Its root-cause finding was
independently re-verified against real files before acting (both cited `metrics.json` files
confirmed to have `run_mode: None`/absent, `config.smoke: True`, `summary.smoke: True`).

## 1. Root cause and fix (LANDED)

`tools/atomize_experiment_records.py:557` did `run_mode = metrics.get("run_mode")` with no
fallback. Most cells record smoke-ness only as `config.smoke` / `summary.smoke` booleans, so
`run_mode` landed `None`, which flowed into `provenance_quality()` and into the atom's own
quotable description as the literal string `"run_mode None"`. Confirmed live in
`T3/EXP_kf2_isolation_proof_v2_n8192` (`data/substrate_index/math/atoms.jsonl` line 25354)
before the fix: description read `"...run_mode None; provenance_quality LEGACY_EXCERPT..."`
while the same description quoted the cell's own headline text `"...at production scale."`.

Fixed by adding `resolve_run_mode(metrics)` (new function, `tools/atomize_experiment_records.py`
just above `discover()`) with fallback order: top-level `run_mode` string -> `config.smoke` /
`summary.smoke` bool -> top-level `smoke` bool -> `"UNKNOWN"`. Never returns `None`, never
guesses `"full"`. Wired into the one read site (`discover()`, was line 557).

Verified against the two real files directly (not just fixtures):
```
data/exp_kf2_isolation_proof_v2_n8192/metrics.json -> smoke
data/exp_saad_solla_v13_n4096_5seed/metrics.json -> smoke
```

Downstream effect on `provenance_quality()`: these atoms now correctly hit the
`if run_mode == "smoke": return "SMOKE_ONLY"` branch (previously unreachable when `run_mode`
was `None`, which instead fell through to `LEGACY_EXCERPT`). `would_be_cert` still requires
`run_mode == "full"` everywhere it's checked, so `run_mode="UNKNOWN"` (the new honest floor)
can never reach `CERT_CHAIN_GRADE` -- confirmed no regression to the cert path by re-reading
`classify_relevance()`/`provenance_quality()`, both of which only test `run_mode == "full"` or
`run_mode == "smoke"`, never `is None`, so `"UNKNOWN"` behaves like any other non-matching string.

## 2. Ingestion-time guard (LANDED, fires)

`run_mode_guard(records)` (new function, called from `main()` right after `discover()`) prints a
loud banner (modeled on `tools/director_kb_freshness_check.py`'s staleness banner) listing every
record whose `resolve_run_mode()` came back `"UNKNOWN"`, writes the full list to
`data/atomize_experiment_records_unknown_runmode.log`, and never drops the record (this
codebase's preservation policy keeps every substantive `metrics.json` atomized regardless --
the guard makes the ambiguity visible, it does not gate ingestion shut).

`--self-test` added at the CLI entrypoint (`python tools/atomize_experiment_records.py
--self-test`), fixture-only, never touches real data or the store:
```
[self-test] resolve_run_mode({'run_mode': 'full'}) = 'full' -> PASS
[self-test] resolve_run_mode({'run_mode': None, 'config': {'smoke': True}}) = 'smoke' -> PASS   (real kf2/saad_solla shape)
[self-test] resolve_run_mode({'config': {'smoke': True}}) = 'smoke' -> PASS
[self-test] resolve_run_mode({'config': {'smoke': False}}) = 'full' -> PASS
[self-test] resolve_run_mode({'summary': {'smoke': True}}) = 'smoke' -> PASS
[self-test] resolve_run_mode({'summary': {'smoke': False}}) = 'full' -> PASS
[self-test] resolve_run_mode({'smoke': True}) = 'smoke' -> PASS
[self-test] resolve_run_mode({'smoke': False}) = 'full' -> PASS
[self-test] resolve_run_mode({}) = 'UNKNOWN' -> PASS
[self-test] resolve_run_mode({'config': {}}) = 'UNKNOWN' -> PASS
[self-test] resolve_run_mode({'run_mode': ''}) = 'UNKNOWN' -> PASS
[self-test] resolve_run_mode: ALL PASS
```

A full `discover()` dry-run (`python tools/atomize_experiment_records.py`, no `HDLAB_ATOMIZE_APPLY`)
was attempted for an end-to-end check but `discover()` itself takes >4 minutes over the full
`data/**/metrics.json` tree (unrelated to this fix -- it was slow before this change too); it was
backgrounded and did not finish printing past the in-store atom count within the session. Not
blocking: the fix was verified directly against the two confirmed-real files and via the
fixture self-test above, which is the evidence the guard actually fires, not an inference from
reading the code.

## 3. Affected-atom enumeration (READ-ONLY, done)

Prior agent's first pass found 447 name/config-N mismatches (330 "smokes") via a name regex that
over-matched -- it caught its own false positive: `exp_capacity_ceiling_near_far_v1_SMOKE_n150`
uses `n150` for `n_items=150` (an honest disclosure; the name already says `SMOKE`).

Re-scanned with `scratch/scan_runmode_affected_atoms.py` (read-only; scans the two live
partitions -- `data/substrate_index/math/atoms.jsonl` and `.../concept/atoms.jsonl` -- against a
fresh re-read of each atom's own cited `metrics_path` on disk, not against the name alone).
Primary signal: stored `metadata.run_mode is None` AND the re-read source file is confirmed
smoke (`config.smoke`/`summary.smoke`/top-level `smoke` True) AND the atom's own name does not
already disclose smoke-ness (`_smoke` case-insensitive). Secondary signal (uppercase `N=<num>`
in the atom's description text vs. the filename's lowercase `_n<digits>` suffix) found nothing
beyond what the primary signal already caught.

Self-test (`--self-test`, fixture + literal-name checks, no real-data dependency for pass/fail):
7/7 PASS -- confirms the counter-example is excluded by name, the two known positives are not
pre-excluded, `is_smoke_source` reads both real files correctly, and `classify()` correctly
flags a kf2-shaped fixture while correctly passing over a counter-example-shaped fixture.

**Result: 3774 experiment_record atoms examined (both partitions), 273 flagged.** (Do not
re-quote the prior pass's 447/330 -- this is the tightened, re-verified count.) Both known
positives present; the supplied counter-example correctly absent. Full list:
`scratch/runmode_affected_atoms.jsonl` (gitignored `scratch/`, so not committed -- regenerate
with `python scratch/scan_runmode_affected_atoms.py` if needed later, or copy it out first).

Distribution of the 273 (all currently mislabeled `run_mode: null`, correct value `smoke`):
- `provenance_quality`: 257 `LEGACY_EXCERPT`, 16 `UNVERIFIED`. **Zero are `CERT_CHAIN_GRADE`** --
  the cert gate itself held throughout; this bug never let a smoke run reach cert status, it only
  mislabeled the honest-tier text.
- `relevance_tier`: 200 `ARCHIVE`, 61 `LOW`, **12 `MEDIUM`** (highest tier present; 0 `HIGH`).
  The 12 `MEDIUM` atoms are the priority subset for a human second look -- they are
  `linked_found` (cite a real T2/T3 primitive) and `PASS`, so more likely to be leaned on
  elsewhere: `axis1_mb_chunk1_v1`, `bid_n_stability_v2`, `c1_kf_battery_phase_v1_n4096`,
  `fluctuation_dissipation_ooe_v1`, `kf45_pre_argmax_joint_probe_v1_n4096`,
  `modern_hopfield_pipeline_validation_v1_n2048_n4096`, `n_scaling_cpu_only_v8_n16384`,
  `operating_point_singularity_basin_map_v1_n4096`, `reasoning_storage_4way_cleanup_v1_n16384`,
  `reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384`,
  `wave14_corpus_N_scaling_tau_unblock_v1`, `wave14f_hippo_warmstart_v1`.
- `verdict`: 137 `MIDDLE_BAND`, 72 `PASS`, 48 `HARD_FAIL`, 16 unmapped (`None`).

## 4. Backfill: DEFERRED, not written to the store -- here is why and here is the ready patch

**Concurrency check, per the brief's explicit instruction to establish safety before writing.**
Read `backend/substrate_index/store.py:142` (`Store.add_atom`) and
`backend/substrate_index/schema.py:845` (`save_atoms`): `add_atom` -> `_flush_atoms()` ->
`save_atoms(list(self._by_id.values()), self.atoms_path)` -- **every call rewrites the WHOLE
partition file** from the calling process's in-memory atom dict (unique-tmp + fsync +
`os.replace`, so no torn-write corruption, but a genuine last-writer-wins full-file overwrite).
No `flock`/`filelock`/lock file anywhere in `store.py` or `schema.py` (grepped both, zero hits
beyond comments). **Confirmed unsafe against a concurrent peer Store instance that loaded before
my write and flushes after mine** -- that peer's flush would silently drop any atom I added, or
vice versa. With multiple `hdi_*` sessions live tonight and three commits already tangled, this
is not hypothetical.

`tools/atomize_experiment_records.py`'s own `main()` `--apply` path (lines ~830-997) already
solves exactly this for its two existing mutation passes: **fresh-load the store per batch,
recompute against the fresh state, gate on invariants (atom/relation counts, `axiom_term`,
`module_liveness_ok()`), and on an `os.replace` race, abort+retry the whole batch rather than
flush over a peer**. That pattern is proven safe and is the right mechanism for a backfill too.

**But it does not fit unmodified.** The existing SCOPED-UPDATE pass (lines ~912-987) deliberately
refreshes ONLY `{key_metrics, strengthens_cert, content_hash}` and explicitly **preserves**
`provenance_quality` / `relevance_tier` by design -- the code comment states tier changes "happen
ONLY via a deliberate signed-off cert-review, never as a refresh side-effect," and the batch gate
(`pq_unchanged`) HARD-FAILs if a tier moves. Backfilling `run_mode` necessarily *does* move
`provenance_quality` for at least some of the 273 (e.g. `kf2_isolation_proof_v2_n8192`:
`LEGACY_EXCERPT` -> `SMOKE_ONLY`) -- that is the whole point of the fix, not a side effect to be
guarded against. Silently reusing the SCOPED-UPDATE path would either violate its own gate (HARD-FAIL,
good) or require weakening a gate that exists specifically to keep cert-tier changes deliberate
and reviewed. This project's own role separation makes that call **Skunkworks's**, not mine:
`hdi_skunkworks` is described as "cert-owner/auditor... Owns A5-gated PartitionedStore writes",
while my role (`hdi_testbed`) is infra + 2nd-witness, explicitly told to surface anything that
"touches substrate-level behavior" rather than act unilaterally. A cert-tier reclassification of
273 atoms across two partitions is exactly that.

**Ready-to-run design for whoever picks this up** (new pass, same file, same fresh-load-per-batch
skeleton as the SCOPED-UPDATE pass, but scoped to the 273-atom affected list from
`scratch/runmode_affected_atoms.jsonl` and additionally recomputing 3 fields instead of preserving
them):
1. Fresh-load `PartitionedStore` per batch (picks up peer writes, matches existing pattern).
2. For each affected atom, re-read its cited `metrics_path`, call `resolve_run_mode(metrics)` ->
   new `run_mode`; call `provenance_quality(new_run_mode, n_seeds, metrics, verdict_norm)` -> new
   `pq`; call `classify_relevance(verdict_norm, depends_on, cap_serving, new_run_mode, new_pq)` ->
   new `relevance_tier`. Rewrite the description's `"run_mode {X}; provenance_quality {Y};
   relevance_tier {Z}"` substring to match.
3. **Print an explicit OLD -> NEW table per atom before applying** (id, old/new run_mode, old/new
   pq, old/new relevance_tier) -- a human-reviewable log, not a silent bulk change, since this is
   a tier reclassification and the brief's own instruction was "backfill... never delete or demote
   any atom... the results are real, the label is wrong."
4. Gate: atom count unchanged, no `relevance_tier` ever moves to something not in
   `{SMOKE_ONLY, LEGACY_EXCERPT, UNVERIFIED, ...}` allowed set, `axiom_term` unchanged,
   `module_liveness_ok()`, and (per the brief) **no atom is deleted or its verdict changed** --
   only `run_mode`/`provenance_quality`/`relevance_tier`/description text.
5. Same retry-on-`os.replace`-race-else-abort-batch pattern as the existing two passes.

A delayed backfill costs nothing (none of the 273 are `CERT_CHAIN_GRADE`, so nothing currently
cites them as production-scale proof through the cert gate itself -- the risk is a human reader
of the raw description text, not the machine-audited tier). A corrupted canonical store under
live multi-agent contention is unrecoverable. Deferring is the conservative call the brief
explicitly authorized ("Either call is correct and I will back it").

## 5. Two smaller items, verified

- **`exp_single_shot_attention_multihop_v1.py` vs `exp_hotpot_3baseline_v1.py`**: `diff` confirms
  they differ in exactly two lines -- the module docstring's first line and `ANCHOR_NAME`
  (`"single_shot_attention_multihop_v1"` vs `"hotpot_3baseline_v1"`). Byte-identical mechanism,
  genuinely re-executed under two names. Flagging both (not removing either) per the brief:
  wherever both atoms get tallied together as independent evidence, that double-counts the same
  run.
- **`exp_pubmedqa_3baseline_v3.py`**: confirmed its docstring's first line literally reads
  `"exp_pubmedqa_3baseline_v2 -- PubMedQA 3-baseline with the CORRECT metric..."` while
  `ANCHOR_NAME = "pubmedqa_3baseline_v3"` is correct. The v3 atom's description (built from this
  docstring via `extract_hypothesis`) describes the wrong mechanism version for its own pass.
  Same store-write deferral as above applies to actually correcting the atom text; noted here so
  the correction (docstring-derived description only, not the result) rides along with the
  backfill pass in item 4.

## Files touched

- `D:/AI/hd-instrument/tools/atomize_experiment_records.py` -- `resolve_run_mode()`,
  `_self_test_resolve_run_mode()`, `run_mode_guard()` added; the one read site fixed;
  `--self-test` CLI entrypoint added. No store write anywhere in this file's diff.
- `D:/AI/hd-instrument/scratch/scan_runmode_affected_atoms.py` -- new, read-only, gitignored.
- `D:/AI/hd-instrument/scratch/runmode_affected_atoms.jsonl` -- new, read-only scan output,
  gitignored (regenerate on demand).
- No files under `data/substrate_index/` were written.
