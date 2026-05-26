# Exp Dev -> Queue: Composition A audit-trail chain + noise envelope v2

**Filed**: 2026-05-24
**Trigger**: CPU drained — Composition A audit v1 finished (rho=1.0 on Kerdock, NaN on SRHT/Hadamard) and E1' noise-envelope v1 finished (MIDDLE BAND). Routing handler pre-registered three follow-ups this turn.

**Pause flag**: cleared (`data/orchestrator_paused.flag` absent).

---

## Entry 1: remote_cpu_queue (data-gen for Composition A v2)

```
queue=remote_cpu_queue name=wave14_cap8_vamp_iterates_srht_hadamard_v1 script=experiments/exp_wave14_cap8_vamp_iterates_srht_hadamard_v1.py prereg=preregs/2026-05-24_wave14_cap8_vamp_iterates_srht_hadamard_v1.md timeout=3600
```

**Axis probed**: Cap 8 (VAMP-on-chain audit trail) — data generation for SRHT + Hadamard at N=4096, 3 alpha cells, 5 seeds (30 trace files total).
**Purpose**: Fill the v1 data gap. Composition A audit v1 was NaN on SRHT/Hadamard because those families had no saved Cap 8 VAMP iterate traces.
**Self-test**: PASS (alpha_label, builders@4096, VAMP iid sanity rel<20%, verdict branches, iterate round-trip)
**Smoke gate**: PASS (N=64, 1 seed, SRHT only -> CAP8_ITERATES_GENERATED)
**Expected wall time**: 30-45 min CPU (30 cells * ~1 min each on remote machine)
**Verdict**: data-gen integrity only — CAP8_ITERATES_GENERATED / PARTIAL / FAILED

---

## Entry 2: remote_cpu_queue (hypothesis test; depends on Entry 1)

```
queue=remote_cpu_queue name=wave14_cap12_cap8_audit_trail_pipeline_v2 script=experiments/exp_wave14_cap12_cap8_audit_trail_pipeline_v2.py prereg=preregs/2026-05-24_wave14_cap12_cap8_audit_trail_pipeline_v2.md timeout=3600
```

**Axis probed**: Composition A (Cap 12 routing fingerprint <-> Cap 8 provenance receipt) at full N=4096 / 5 seeds across all 4 hard families.
**Purpose**: Re-run audit with iterate traces from Entry 1; resolves Composition A LICENSE / KILL / MIDDLE BAND.
**Self-test**: PASS (v1 inherited + iterate fingerprint + load missing + verdict branches)
**Smoke gate**: PASS (N=1024, 1 seed, kerdock+iid -> INCONCLUSIVE expected; Kerdock rho=1.0 reproduced from v1)
**Serialization**: depends on Entry 1's output files under `data/exp_wave14_cap8_vamp_iterates_srht_hadamard_v1/iterates/`. Includes 15-min file-exists wait + graceful fallback to spectrum-only mode if Entry 1 fails. Per-queue runner serializes Entry 2 after Entry 1, so the wait should be brief in normal operation.
**Expected wall time**: 30-45 min CPU
**Verdict**: COMPA_AUDIT_LICENSED / KILLED / MIDDLE_BAND / INCONCLUSIVE

---

## Entry 3: remote_cpu_queue (E1' higher-stats follow-up)

```
queue=remote_cpu_queue name=wave14_mp_ks_noise_envelope_sweep_v2 script=experiments/exp_wave14_mp_ks_noise_envelope_sweep_v2.py prereg=preregs/2026-05-24_wave14_mp_ks_noise_envelope_sweep_v2.md timeout=4500
```

**Axis probed**: Cap 12 noise envelope width — fine eta grid {0.01, 0.02, 0.03, 0.04, 0.05} at 20 seeds per cell across 5 codebooks.
**Purpose**: Resolve eta_critical for Cap 12 routing (v1 landed MIDDLE BAND at 5 seeds; v2 has ~4x compute).
**Self-test**: PASS (9/9 cases — grid, route_from_ks, eta_critical, PASS+FAIL+MIDDLE branches, missing-cells INCONCLUSIVE, monotonic ks)
**Smoke gate**: PASS (N=64, 1 seed, 4 cells -> INCONCLUSIVE expected at smoke scale)
**Expected wall time**: 45-60 min CPU (5 codebooks * 5 eta * 20 seeds = 500 cells; ~4x v1)
**Verdict**: MP_KS_NOISE_ENVELOPE_SWEEP_V2_PASS / KILLED / INCONCLUSIVE

---

## Queue depth after ship

- `remote_cpu_queue`: +3 pending (this shipment; serial dependency chain Entry 1 -> Entry 2; Entry 3 independent)
- `overnight_queue`: unchanged
- `local_cpu_queue`: unchanged

## Notes

- All three scripts include `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` at top (defense-in-depth for ASCII encoding per [[feedback-ascii-only-in-scripts]]).
- All three scripts include `--self-test` and `--smoke` entry points for runner reproducibility.
- Entry 2 has a 15-minute file-exists-wait loop as a structural backstop in case the runner picks up Entries 1 and 2 in interleaved fashion (per-queue serial runners should make this unnecessary, but defense-in-depth).
- Per [[feedback-envelope-expansion-fail-bands]]: all three preregs include explicit HARD PASS / HARD FAIL / MIDDLE BAND specs.
