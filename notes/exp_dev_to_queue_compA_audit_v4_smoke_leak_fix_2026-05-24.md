# Exp Dev -> Queue: Composition A audit v4 (smoke-leak fix; first true 4-family test)

**Filed**: 2026-05-24
**Trigger**: CAP8_ITERATES_GENERATED — v1c data-generation anchor wrote 30 valid trace files at `data/exp_wave14_cap8_vamp_iterates_srht_hadamard_v1c/iterates/`. The v3 attempt at this audit produced smoke-mode metrics that the verdict_handler read as full-mode (fabricated rho values for SRHT / Hadamard / RM(1,m) that weren't in summary). v4 fixes the smoke-leak structurally and re-points ITERATE_ROOT to v1c.

**Pause flag**: cleared (`data/orchestrator_paused.flag` absent, confirmed at file system level pre-ship).

**Name-uniqueness verification (pre-ship)**:
- `wave14_cap12_cap8_audit_trail_pipeline_v4` — confirmed ABSENT from local `data/overnight_queue/queue.json`, local `data/local_cpu_queue/queue.json`, AND remote `data/remote_cpu_queue/queue.json`. v3 (the smoke-leak attempt) is present in remote queue with status="completed".

---

| queue            | name                                              | script                                                                | prereg                                                            | timeout(s) |
|------------------|---------------------------------------------------|-----------------------------------------------------------------------|-------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_cap12_cap8_audit_trail_pipeline_v4         | experiments/exp_wave14_cap12_cap8_audit_trail_pipeline_v4.py          | preregs/2026-05-24_wave14_cap12_cap8_audit_trail_pipeline_v4.md   | 3600       |

---

## Anchor — wave14_cap12_cap8_audit_trail_pipeline_v4
- **Purpose**: Composition A's first true 4-family quantitative test. Compute Spearman rho(kappa_n divergence, Schur-Weyl irrep (n)-mass deviation) for ALL 4 hard families (kerdock + srht + hadamard + rm_1_m) at N=4096 / 5 seeds, using the v1c VAMP iterate traces for SRHT + Hadamard. Resolves Composition A LICENSE / KILL / MIDDLE BAND.
- **What changed vs v3**:
  - **ITERATE_ROOT repointed** from `_v1b` (v3) to `_v1c` (v4) — v1c generated 30 valid traces; v1b was verdict-judge-failed.
  - **mode marker in metrics.json (top-level)** — `metrics["mode"]` is "full" or "smoke" so verdict_handler can structurally check before trusting per-family rho.
  - **rho_by_family lifted to top-level metrics** — honest-reread is a dict lookup, not a re-walk through nested arrays.
  - **run_main hard-asserts mode=full and 4 hard families** — refuses to write non-smoke metrics.json if any hard family is missing.
  - **iid Gauss x Schur-Weyl analytical self-test** — verifies the analytical formula AND the empirical extraction at c=1 give mass_(2,) close to 1.0.
- **Self-test**: PASS (v3 inherited + ITERATE_ROOT v1c pointing + iid-Gauss x Schur-Weyl analytical baseline). Empirical iid Gauss mass_(2,) = 1.000000 at N=M=1024, mp_mass_(2,) = 1.000000 analytical.
- **Smoke**: PASS at N=1024 / 1 seed / 2 codebooks → COMPA_AUDIT_INCONCLUSIVE (expected — only 1/4 hard families measured at smoke scale); Kerdock rho=1.0 reproduced; mode="smoke" explicitly stamped in metrics; smoke output dir is `_v4_smoke` (not `_v4`).
- **Bonus diagnostic**: per-family rho reported with 6 decimal places to distinguish v3 SRHT==Hadamard==0.533 algebraic-equivalence vs smoke-leak-artifact.

## Per [[feedback-envelope-expansion-fail-bands]] explicit bands

- **HARD PASS (Composition A LICENSED, 12th-capability adjacent)**: rho_aggregate >= 0.60 across >= 3/4 hard families AND no family < 0.30 AND no family TIED.
- **HARD FAIL (Composition A KILLED, prose-only)**: rho < 0.30 on >= 2/4 hard families with finite rho.
- **MIDDLE BAND (Composition A holds narrowly)**: anything else.

## Queue depth after ship

- `remote_cpu_queue`: +1 pending → already RUNNING at ship verification time (cpu_runner_0 picked up immediately; status="running", started_at=2026-05-24T07:43:58).
- `overnight_queue`: unchanged.
- `local_cpu_queue`: unchanged.

## Notes

- Script includes `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` at top.
- Script includes `--self-test` and `--smoke` entry points.
- Script reuses v3's measurement loop entirely (loader, fingerprint, verdict) and only overrides `run_experiment`, `validate_metrics`, `write_metrics`, `run_main` to stamp mode marker + rho_by_family + defense-in-depth assertions.
- Per [[feedback-verdict-msg-honest-reread]]: metrics.json now contains structural mode/rho_by_family/n_codebooks_measured at top level; verdict_handler can no longer fabricate rho values for missing families.
- Per [[feedback-ship-name-collision]]: name uniqueness verified BEFORE queue_add.sh AND queue entry presence verified AFTER (entry found running on cpu_runner_0).
