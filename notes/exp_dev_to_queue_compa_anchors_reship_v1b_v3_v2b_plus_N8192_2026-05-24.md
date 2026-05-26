# Exp Dev → Queue: Composition A chain RE-SHIP (v1b + v3 + v2b) plus N=8192 E2 follow-up

**Filed**: 2026-05-24
**Trigger**: Prior dispatch's v1/v2 names failed to enqueue (queue_add.sh dedup ambiguity); orchestrator diagnostic confirmed 0 hits for `vamp_iterates` and `audit_trail_pipeline_v2` on the remote queue. Re-shipping under suffixed unique names. Also adds Anchor 4 N=8192 follow-up after E2 N=16384 timeout.

**Pause flag**: cleared (`data/orchestrator_paused.flag` absent — verified directly at file system level pre-ship).

**Name-uniqueness verification (pre-ship)**:
- `wave14_cap8_vamp_iterates_srht_hadamard_v1b` — confirmed ABSENT from `data/overnight_queue/queue.json` and from remote `data/remote_cpu_queue/queue.json`; absent from local script directory before file copy.
- `wave14_cap12_cap8_audit_trail_pipeline_v3` — confirmed ABSENT from both queues; remote queue holds the v1 only (v2 was the failed enqueue).
- `wave14_mp_ks_noise_envelope_sweep_v2b` — confirmed ABSENT from both queues; remote queue holds the v1 only.
- `wave14_interp_family_N8192_v1` — confirmed ABSENT (the existing entry is `_N16384_v1`).

---

| queue            | name                                                | script                                                                       | prereg                                                                  | timeout(s) |
|------------------|-----------------------------------------------------|------------------------------------------------------------------------------|-------------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_cap8_vamp_iterates_srht_hadamard_v1b         | experiments/exp_wave14_cap8_vamp_iterates_srht_hadamard_v1b.py               | preregs/2026-05-24_wave14_cap8_vamp_iterates_srht_hadamard_v1b.md       | 3600       |
| remote_cpu_queue | wave14_cap12_cap8_audit_trail_pipeline_v3           | experiments/exp_wave14_cap12_cap8_audit_trail_pipeline_v3.py                 | preregs/2026-05-24_wave14_cap12_cap8_audit_trail_pipeline_v3.md         | 3600       |
| remote_cpu_queue | wave14_mp_ks_noise_envelope_sweep_v2b               | experiments/exp_wave14_mp_ks_noise_envelope_sweep_v2b.py                     | preregs/2026-05-24_wave14_mp_ks_noise_envelope_sweep_v2b.md             | 4500       |
| overnight_queue  | wave14_interp_family_N8192_v1                       | experiments/exp_wave14_interp_family_N8192_v1.py                             | preregs/2026-05-24_wave14_interp_family_N8192_v1.md                     | 9000       |

---

## Per-anchor purpose + smoke result

### Anchor 1 — wave14_cap8_vamp_iterates_srht_hadamard_v1b
- **Purpose**: Generate VAMP iterate traces at Cap 8 protocol shape (N=4096, 3 alpha × 5 seeds × 2 codebooks = 30 files) for SRHT + Hadamard. Fills the v1 audit-trail data gap (rho=1.0 on Kerdock but NaN on SRHT/Hadamard because no iterate files).
- **Output**: `data/exp_wave14_cap8_vamp_iterates_srht_hadamard_v1b/iterates/{srht,hadamard}/alpha_{0p50,0p75,1p00}/seed_*.json`.
- **Self-test**: PASS (alpha_label, builders@4096, VAMP iid sanity, verdict branches, iterate round-trip).
- **Smoke**: PASS at N=64 / 1 seed / SRHT only → CAP8_ITERATES_GENERATED; metrics.json valid.

### Anchor 2 — wave14_cap12_cap8_audit_trail_pipeline_v3 (depends on Anchor 1's output dir `_v1b`)
- **Purpose**: Re-run Composition A audit at full N=4096 / 5 seeds across all 4 hard families (kerdock + srht + hadamard + rm_1_m) using Anchor 1's iterate traces. Resolves Composition A LICENSE / KILL / MIDDLE BAND.
- **ITERATE_ROOT** repointed: now reads from `data/exp_wave14_cap8_vamp_iterates_srht_hadamard_v1b/iterates/` (not v1). Verified via grep.
- **Self-test**: PASS (v1 inherited + iterate fingerprint + load missing + verdict branches).
- **Smoke**: PASS at N=1024 / 1 seed / 2 codebooks → COMPA_AUDIT_INCONCLUSIVE (expected — only 1 of 4 hard families measured at smoke scale); Kerdock rho=1.0 reproduced from v1.
- **Serialization**: includes 15-min file-exists wait for Anchor 1's iterate files; per-queue runner serialization should make the wait brief in normal operation.

### Anchor 3 — wave14_mp_ks_noise_envelope_sweep_v2b
- **Purpose**: Higher-stats fine eta grid {0.01, 0.02, 0.03, 0.04, 0.05} at 20 seeds × 5 codebooks; resolves the non-monotonic v1' MIDDLE BAND.
- **Self-test**: PASS (9/9 cases).
- **Smoke**: PASS at N=64 / 1 seed / 4 cells → MP_KS_NOISE_ENVELOPE_SWEEP_V2_INCONCLUSIVE (expected at smoke scale, "Missing envelope cells: have 4 need 25"); metrics.json valid.

### Anchor 4 — wave14_interp_family_N8192_v1 (NEW — substrate-honest E2 follow-up)
- **Purpose**: Test the AMP-error predictor at N=8192 (one step below the original customer-scale target N=16384, which TIMED OUT on the overnight runner). Substrate-honest: better to verify at the largest N we can complete in budget than to leave the N-envelope unresolved.
- **Queue**: `overnight_queue` (GPU; depth probe).
- **Kerdock structural absence**: log2(8192) = 13 (odd) → Kerdock builder unsupported at N=8192. Script auto-skips Kerdock@N=8192; verdict requires ≥2 of {SRHT, Hadamard} present at N=8192 (Kerdock remains tested at N=1024 and N=4096).
- **COMPUTE BUDGET**: Expected 60-120 min on GPU; queue timeout 9000s (150 min) gives ~30 min headroom. TIMEOUT treated as informational, NOT a HARD FAIL.
- **Self-test**: PASS (9/9 cases).
- **Smoke**: PASS at N=64 / 1 seed / 3 alpha × 2 families → INTERP_FAMILY_N8192_INCONCLUSIVE (expected — no N=8192 cells in smoke); metrics.json valid.
- **HARD bands**: PASS = rho ≥ 0.50 on BOTH (SRHT, Hadamard) at N=8192 AND max VAMP rel-err < 0.20. FAIL = rho < 0.30 on EITHER. MIDDLE = rho in [0.30, 0.50) or VAMP in [0.20, 0.30).

---

## Queue depth after ship

- `remote_cpu_queue`: +3 pending (this shipment); serial dependency chain Anchor 1 → Anchor 2; Anchor 3 independent.
- `overnight_queue`: +1 pending (Anchor 4) on top of any GPU-queued items.
- `local_cpu_queue`: unchanged.

## Notes

- All four scripts include `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` at top (defense-in-depth).
- All four scripts include `--self-test` and `--smoke` entry points.
- Anchor 2 has a 15-min file-exists-wait + graceful fallback to spectrum-only mode if Anchor 1 fails (per-queue serial runners should make this unnecessary, but defense-in-depth).
- Per [[feedback-envelope-expansion-fail-bands]]: all four preregs include explicit HARD PASS / HARD FAIL / MIDDLE BAND specs. Anchor 4 also includes an explicit TIMEOUT outcome (substrate-honest follow-up: TIMEOUT ≠ FAIL).
- v1 / v2 / v3 naming context: the failed prior ship was v1/v2/v2, which collided (silently) with already-present v1 entries in queue_add.sh dedup. This re-ship uses v1b / v3 / v2b suffixes for absolute uniqueness.
