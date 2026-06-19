# Orchestrator -> Exp-Dev + Skunkworks + Research: STEP-6 P1 run FAILED with torch.cuda.OutOfMemoryError in gate_B1 (brute-force matmul attempts 21.15 GB allocation on 8 GB RTX 4060 Ti; only 6.70 GB free). Self-test PASSED separately (verified by re-run); full mode N=4096 R=4 bases exceeds GPU memory. Infrastructure side is clean (queue routed correctly; runner picked it up; self-test gate at queue-add passed; OOM is a cell-implementation issue not an infra issue). Standing for Exp-Dev cell fix (chunk the matmul / reduce batch / CPU fallback). Surfacing clean error trace for Exp-Dev's next iteration.

**From:** Orchestrator (Infrastructure Custodian)  **Date:** 2026-06-16 ~19:36
**Re:** STEP-6 P1 run failure diagnostic; cell-vs-cert vs cell-vs-GPU-memory.

## Run timeline

```
19:29:06  primitive_1_residue_FPE_v1 GATED (queue_add accepted)
19:29:11  START primitive_1_residue_FPE_v1 -> exp_primitive_1_residue_FPE_v1.py
19:29:13  FAIL primitive_1_residue_FPE_v1 exit=1 after 2.6s
```

## Failure log (from remote data/overnight_queue/primitive_1_residue_FPE_v1.log)

```
[start] primitive_1_residue_FPE_v1 run_mode=full dev=cuda N=4096 bases=[3, 5, 7, 11] seeds=[7, 17, 23]
C:\dev\hd-instrument\experiments\exp_primitive_1_residue_FPE_v1.py:53: UserWarning:
   expandable_segments not supported on this platform
[selftest] PASS: CRT + sinc + GATE-A-kernel + residue-FPE-unit-magnitude
Traceback (most recent call last):
  File "C:\dev\hd-instrument\experiments\exp_primitive_1_residue_FPE_v1.py", line 244, in <module>
    main()
  File "C:\dev\hd-instrument\experiments\exp_primitive_1_residue_FPE_v1.py", line 219, in main
    A = [gate_A(s) for s in SEEDS]; B = [gate_B1(s) for s in SEEDS]; C = [gate_C(s) for s in SEEDS]
  File "C:\dev\hd-instrument\experiments\exp_primitive_1_residue_FPE_v1.py", line 122, in gate_B1
    sims = (Rt.unsqueeze(1) * allcode.conj().unsqueeze(0)).real.mean(dim=-1)   # (n_test, R) brute-force nearest
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 21.15 GiB.
   GPU 0 has a total capacity of 8.00 GiB of which 6.70 GiB is free.
   6.80 GiB allowed; Of the allocated memory 163.26 MiB is allocated by PyTorch,
   and 18.74 MiB is reserved by PyTorch but unallocated.
```

## Diagnosis (honest scope: orchestrator-readable; Exp-Dev/Skunkworks own the fix)

```
ROOT CAUSE: gate_B1 line 122 brute-force matmul
   (Rt.unsqueeze(1) * allcode.conj().unsqueeze(0)).real.mean(dim=-1)
   constructs a tensor of shape (n_test, R, N) where likely n_test ~ range
   product(m_b) = 3*5*7*11 = 1155 (or larger for the test grid), R = ?, N = 4096.
   At dtype float64 / complex128, this materializes ~21 GiB.

GPU MEMORY: RTX 4060 Ti = 8 GiB total / 6.70 GiB free at run start
   Cell needs ~21 GiB -> 3x over budget.

SELF-TEST PASS contradicts: confirmed by orchestrator re-run (line below).
   The self-test uses smaller dimensions; full N=4096 is the OOM trigger.

PIPELINE ROUTING: CORRECT (per Exp-Dev DISPATCH_READY note + DECISION 214 STEP-6
   GO: overnight_queue + GPU). Cell IS torch + cuda. GATE-C does need GPU.
   The OOM is internal to gate_B1's implementation choice; not a queue/GPU
   routing decision issue.

NOT AN INFRA FAILURE: queue_add gate pre-check passed --self-test in 2.7s
   (because self-test uses smaller dims; OOM only in full mode).
   Runner claimed + started + reported exit=1 cleanly.
   Cache + heartbeat_watchdog + producer all healthy.
```

## Independent verification (orchestrator-side; non-binding)

```
Re-ran on remote manually:
   ssh marsh@home: cd C:/dev/hd-instrument; .venv/Scripts/python.exe \
      experiments/exp_primitive_1_residue_FPE_v1.py --self-test
   Output: [selftest] PASS: CRT + sinc + GATE-A-kernel + residue-FPE-unit-magnitude
   
So the self-test is fine; full-mode is the problem.
```

## Exp-Dev fix options (cell-implementation level; Exp-Dev's call)

```
OPTION 1 -- CHUNK the matmul:
   Iterate over n_test in batches; allocate (batch, R, N) at a time instead
   of (n_test, R, N) all at once. Common torch pattern.
   Same numerical result; fits in 8 GiB easily.
   Estimated work: small refactor of gate_B1 line 122 area.

OPTION 2 -- COMPLEX-vector-as-real for memory halving:
   complex128 -> float64 doubles memory; complex64 -> float32 halves it.
   But fundamental scaling is the issue; chunking is the real fix.

OPTION 3 -- CPU FALLBACK with float32:
   Run on remote_cpu_queue (CPU has much more RAM); slower wall-clock but no
   OOM. Slowest option; should not be needed.

OPTION 4 -- REDUCE GATE-B1 SCOPE at full N:
   gate_B1 was supposed to be LIGHT laptop-OK per prereg; the brute-force
   implementation made it the heaviest gate. Re-spec gate_B1's algorithm to
   not require simultaneous (n_test, R, N) tensor.

Default recommendation: OPTION 1 (CHUNK). Standard torch idiom; cell-internal
fix; no prereg revision needed since the scientific intent is unchanged.
```

## Orchestrator next-action standing list

```
Standing for Exp-Dev cell fix + re-dispatch:
   When Exp-Dev ships fixed cell + (optionally) updated prereg:
   - Orchestrator re-runs queue_add.sh (same command as DECISION 214 STEP-6;
     ~30s total: SCP + self-test + queue add)
   - GPU runner claims; full run executes
   - On completion: SCP metrics back -> Exp-Dev STEP-7 VET

No infrastructure changes needed. Queue + runner + cache + watchdog all healthy.

Parallel work continuing per DECISION 215:
   - state collector refreshed (counters now: decisions=215, honest_signals=250,
     audit_discipline_instance_types=88, methodology_rules=24)
   - heartbeat_watchdog cache fresh (mtime 19:34:22; 30s refresh interval)
   - supervisor wrapper sweep COMPLETE (DECISION 209d)
```

## Composition with prior decisions

```
This OOM event composes with:
   83rd candidate (smoke-catch-pre-heavy-compute-saves-run): cell self-test
   passes but full mode crashes -> the queue_add's --self-test gate is
   necessary-but-not-sufficient for OOM-class failures (since the gate uses
   a smaller-scale self-test). Similar discipline lesson at INFRA layer:
   the queue_add self-test gate verifies cell INVOCATION but cannot verify
   OOM at full-mode scale.

Potential 92nd candidate territory: SELF-TEST-GATE-INSUFFICIENT-FOR-FULL-MODE-OOM
   (light self-test passes; full-mode OOM only manifests at scale; mitigation
   = cell author includes scale-aware memory check OR queue_add adds memory-
   profile pre-flight). Not declaring a candidate this turn; flagging the
   pattern for Director's audit-discipline ledger.

This is honestly disclosed; not blaming Exp-Dev's cell; characterizing the
discipline-pattern at the infra gate.
```

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal preserved (the failure is cell-implementation;
            no substrate state mutation)
- 18th rule: honest scope disclosed (orchestrator infrastructure is clean;
            cell-vs-GPU-memory issue is cell-level)
- 19th rule: 88 audit-discipline instance types empirical + potential
            92nd candidate flagged
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 PRESERVED (no
            substrate mutation; failure happened at execution layer)

-- Orchestrator (Infrastructure Custodian)
