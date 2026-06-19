# N-mismatch root cause analysis (2026-05-27)

## Question

Why did `_n<N>`-suffixed anchors run at N=512 SMOKE 78+ times today even after
PROT-018 was supposed to enforce the suffix as a binding contract?

## The user's four hypotheses, audited

1. **"Pre-PROT-018 backlog has invalid queue entries"** -- TRUE in the broad
   sense (entries already shipped before PROT-018 landed continue executing)
   but at audit time 2026-05-27T16:30 the remote pending lists are CLEAN
   (audit ran: `python tools/audit_n_mismatch.py --remote` -- 0 backlog
   entries pending in either overnight_queue or remote_cpu_queue). The
   completed-entry tail still contains pre-PROT-018 `_n<N>` anchors whose
   actual run was at N=512, but those are HISTORICAL records, not pending
   work.

2. **"Runner has no validation -- script lacks --N and falls to default
   N=512"** -- FALSE in mechanism, TRUE in effect. The runner invokes
   `[python, script]` with NO extra args -- no `--N` is passed and no
   `--N` is needed. The scripts have argparse with `--smoke` as a flag;
   no flag => FULL mode (e.g. saad_solla_v9_n4096.py line 263-270). Verified
   on the actual remote log (`saad_solla_v9_n4096.log` shows
   `[run] saad_solla_v9_n4096 FULL N=4096 seeds=[7, 17, 23, 31] device=cuda`).
   The runner DOES launch in FULL mode correctly.

3. **"Script defaults to smoke"** -- FALSE. Scripts default to FULL when
   no `--smoke` flag is present (verified across saad_solla_v6/v8/v9,
   saddle_cascade_v6). The `_instrumentation_selftest()` that fires at
   import time uses N_SMOKE for a single sanity cell, but the main `run()`
   call uses FULL constants.

4. **"Anchor naming is informal -- _n<N> is just a suffix"** -- TRUE in
   the sense that the suffix is enforced by humans + queue_add.py (PROT-018)
   not by the script's argparse. The script's hardcoded N constant is the
   binding artifact; the anchor name is supposed to MATCH it. PROT-018
   formalized this contract at queue-add time but it has no runner-side
   or post-run enforcement.

## The actual root cause (verified)

**Verdict_handler reads LOCAL `data/exp_<name>/metrics.json` -- which on the
developer's machine is the STALE PRE-SHIP SMOKE artifact, not the remote
production-run output.**

Timeline for `wave14_saddle_cascade_plateau_v6_n4096_gpu` (representative
case; pattern repeats):

- 09:21 LOCAL: developer ran the script with `--smoke` to validate the
  prereg. Smoke writes to `data/exp_wave14_saddle_cascade_plateau_v6_n4096_gpu/metrics.json`
  -- the FULL-name dir, NOT a `_smoke` suffix dir. (Script's `get_output_dir`
  uses the script-hardcoded name; smoke and FULL share the same output dir.)
  Local metrics: `mode: SMOKE / N: 512 / device: cpu / 1 seed / elapsed_s: 2.64`.
- ~10:00 ship: `queue_add.sh` SCP'd the script + prereg to marsh@home,
  SSH'd `queue_add.py` with `--skip-smoke`. Entry queued on remote.
- 11:18 REMOTE: runner picked up the entry. Ran the FULL script (no `--smoke`).
  Took 6821s on CUDA, 5 seeds at N=4096, recorded HARD_PASS 5/5. Remote
  metrics at `marsh@home:C:\dev\hd-instrument\data\exp_wave14_saddle_cascade_plateau_v6_n4096_gpu\metrics.json`:
  `mode: FULL / N: 4096 / device: cuda / 5 seeds / elapsed_s: 6821.55`.
- Verdict_handler woke up. Read LOCAL metrics (`data/exp_<name>/metrics.json`)
  -- which is the STALE 09:21 smoke artifact. Honest re-read flagged the
  contradiction between the anchor name (`_n4096_gpu`) and the metrics
  (`N: 512, mode: SMOKE, device: cpu, 1 seed, elapsed 2.64s`). Logged as
  "label-vs-honest 61st catch."

The verdict_handler's honest-re-read DID THE RIGHT THING. But the underlying
metrics it was comparing against were the WRONG metrics. The remote-side
production run was actually CORRECT (HARD_PASS at N=4096). Nothing fetched
the real metrics back to local; nothing notified the verdict_handler that
the remote and local metrics had diverged.

**Local audit confirms scale of the rot:** of 21 local `_n<N>` anchor dirs,
17 have metrics that record N != suffix_N (all SMOKE artifacts; suffix=4096
or 8192 but stored N=512 or 1024). 0 match. (`python tools/audit_n_mismatch.py`.)

## Additional contributing factors

- **Scripts share output dir between smoke and FULL.** `get_output_dir`
  uses the same name in both modes; smoke artifacts overwrite. queue_add.py
  side-steps this by setting `HDLAB_EXP_NAME=<entry_name>_smoke` for its
  gate smoke (lines 277-281), but ad-hoc local `python script.py --smoke`
  invocations do not -- they hit the FULL-name dir.

- **No metrics fetch-back.** `remote_state_emitter` exposes queue.json's
  recorded status / verdict_msg but does NOT relay the metrics.json body.
  And queue.json's `verdict_msg` is NOT written by the runner (verified
  in `runner_v2_prod.py.run_one` -- only sets status / ended_at / wall_s /
  error). So remote_state_cache has no production metrics, and local has
  stale smoke metrics.

- **Single layer of enforcement.** PROT-018 fires only at queue_add. Once
  past the gate the contract is unenforced.

## Fixes landed this turn

1. **Runner-side post-run N validator** (`experiments/runner_v2_prod.py`).
   New `validate_n_suffix_binding(anchor, metrics_path)` runs after the
   existing schema check on exit-0 runs. If the anchor `_n<N>` suffix does
   not match `metrics["summary"]["N"]` / `["config"]["N"]` / `["detail"]["N"]`
   (or `N_run`), the runner marks the entry FAILED with
   `error=n_mismatch: anchor _n<X> but metrics recorded N=<Y> mode=<mode>`
   and writes an importance=HIGH `n_mismatch_runner_reject` status_log
   entry. Belt-and-suspenders with queue_add.py exit-6: catches (a)
   pre-PROT-018 backlog entries, (b) --allow-duplicate / --rerun-as
   bypass paths, (c) scripts that ran smoke despite no `--smoke` arg
   (e.g. env-var leakage).

2. **Tests** (`tests/test_runner_n_suffix_validator.py`). 20 cases covering
   the two failure recurrences (saad_solla `_n4096` -> N=512; bid_v2 `_n8192`
   -> N=512), all `_n<N>` parsing edge cases (versions like `_v9` NOT
   matched; words like `_next` / `_noise` / `_norm` NOT matched), all
   metrics-N extraction precedences, and all NO-OP cases (missing file,
   invalid JSON, no-suffix anchor, no-N metrics). All 20 pass.

3. **Audit tool** (`tools/audit_n_mismatch.py`). Two modes:
   - default: scans local `data/exp_*/metrics.json` for stale local-smoke
     artifacts in `_n<N>`-named dirs.
   - `--remote`: fetches both remote queues via SSH, lists pending
     anchors with `_n<N>` suffix whose script source lacks the
     `N=<suffix>` assignment (mirrors queue_add.py's regex).

4. **Pre-PROT-018 backlog status.** `--remote` audit at 2026-05-27T16:30:
   0 pending backlog entries in overnight_queue OR remote_cpu_queue. No
   queue cleanup needed -- the runner-side validator catches future
   mis-shipped entries automatically.

## What was NOT changed

- No new PROT number; this is the post-run leg of PROT-018, not a new
  protocol.
- No changes to scripts themselves; smoke-vs-FULL output-dir collision
  is a known artifact but fixing it across 100+ scripts is a separate
  hygiene task. The runner-side validator catches the downstream symptom
  without touching every script.
- No changes to verdict_handler's `metrics_file` resolution; that is
  agent-prompt-level and outside the scope of this structural fix.
- No deletion of the 17 local stale smoke artifacts. They are diagnostic
  history; the audit tool surfaces them on demand. The runner validator
  prevents NEW such files from being treated as authoritative FULL runs.
