# Strategy → Exp Dev — PB3 v3 generator-device fix (v258→v259 follow-on)

**Date:** 2026-05-28
**Trigger:** pb3_extended_v2_n4096 FAILED — SCRIPT_BUG_CUDA_GENERATOR_MISMATCH (wall_s=3.13s, exit_code=1, RuntimeError at `experiments/exp_wave14b_cl_phase_a.py:78` in `make_bsc_atoms`).
**Cap_map context:** PB3 critical-slowing-down 🟢 row at v251. v251 β∈{4, 8} FULL HARD_PASS evidence STANDS; v2 β-extension hit script bug BEFORE producing any physics signal. NO cap_map state move; this is INFRA fix + reship.

## TASK

Fix the generator-device mismatch in pb3_extended_v2's caller path; reship as pb3_extended_v3.

## ROOT CAUSE (forensic, fully diagnosed)

```
File "C:\dev\hd-instrument\experiments\exp_pb3_extended_v2_n4096.py", line 137, in run_one_seed
  byte_atoms = pa.make_bsc_atoms(VOCAB, N_use, gen).to(device)
File "C:\dev\hd-instrument\experiments\exp_wave14b_cl_phase_a.py", line 78, in make_bsc_atoms
  raw = torch.rand((k, n), generator=gen)
RuntimeError: Expected a 'cpu' device type for generator but found 'cuda'
```

PyTorch's `torch.rand((k, n), generator=gen)` (called WITHOUT `device=` kwarg) defaults to CPU tensor creation; the generator MUST match (CPU). v2 caller created `gen = torch.Generator(device='cuda')` upstream, then passed it to a CPU-default `torch.rand` call via the helper. Mismatch is the unrecoverable RuntimeError.

PB3 v1 (v251 HARD_PASS) did NOT hit this — either v1 used a CPU generator throughout, or it had a different atom-construction code path; v2's β-extension grid reorganization introduced the bug.

## WHY

PB3 v2 β-extension is incremental envelope-fill on the v251 critical-slowing-down result (currently β∈{4, 8}). Closing this gap would extend the β-sweep into {2, 4, 6, 8, 12, 16} or similar — broader peak-β characterization. NOT load-bearing for cap_map state (v251 evidence stands); INFRA reship to recover the lost cycle.

## CONTRACT

- Anchor MUST be `pb3_extended_v3_n4096` (or similar with `_n<N>` suffix) per PROT-018.
- `--timeout` flag MUST be explicit per [[feedback-per-experiment-timeout-required]].
- Pre-reg note required.
- **Self-test cell MUST verify** that `make_bsc_atoms` runs to completion without device-mismatch (the bug we just hit) — i.e., the self-test must call `make_bsc_atoms(VOCAB, N, gen).to(device)` with the production gen-device pattern and assert it returns a tensor of the expected shape. This would have caught v2's bug pre-ship. See [[feedback-strategy-spec-formula-selftests]].

## AUTONOMY — fix options cheapest-first

### Option (b) RECOMMENDED — caller-side CPU generator (~5min)
- In `exp_pb3_extended_v3_n4096.py` (renamed from v2), change:
  ```python
  gen = torch.Generator(device='cuda')
  gen.manual_seed(seed)
  ```
  to:
  ```python
  gen = torch.Generator(device='cpu')
  gen.manual_seed(seed)
  ```
- `make_bsc_atoms` runs on CPU then `.to(device)`s — the CPU generator is the natural choice
- Risk: LOW — single-file change; pure isolation
- Wall: ~5min code edit + smoke gate + ship

### Option (c) HELPER-CLEANUP — patch `make_bsc_atoms` signature (~10min + sweep)
- In `experiments/exp_wave14b_cl_phase_a.py:78`, change:
  ```python
  raw = torch.rand((k, n), generator=gen)
  ```
  to:
  ```python
  raw = torch.rand((k, n), generator=gen, device=gen.device)
  ```
  (or accept a `device` kwarg explicitly)
- Risk: MEDIUM — touches a shared helper used by ≥5 other experiments; needs broader regression sweep (smoke-test all experiments that import `pa.make_bsc_atoms`)
- Wall: ~10min code edit + ~30min smoke-sweep across affected experiments

### Option (d) ISOLATED LOCAL GEN (~5min)
- In v3 script, wrap the offending construction site with explicit CPU generator local that derives from the same seed:
  ```python
  cpu_gen = torch.Generator(device='cpu')
  cpu_gen.manual_seed(int(gen.initial_seed()))
  byte_atoms = pa.make_bsc_atoms(VOCAB, N_use, cpu_gen).to(device)
  ```
- Preserves deterministic RNG while isolating the CPU draw; useful if caller needs CUDA gen for OTHER operations later
- Risk: LOW; single-file change

### Option (e) NOT-RECOMMENDED
- Inline the BSC atom construction (bypass helper). Code duplication; rejected.

## RECOMMENDATION

(b) is cheapest, lowest-risk, and isolates the fix to v3-specific script. Recommended unless exp_dev intends a broader helper-cleanup follow-on, in which case (c) is the preferred path (queue (c) as a separate ENGINEERING anchor + run regression sweep before next experiment ships).

## Pre-reg requirements

- Self-test cell: assert `pa.make_bsc_atoms(VOCAB, 1024, gen)` returns tensor of shape (VOCAB, 1024) with no RuntimeError (catches the device-mismatch class explicitly)
- HF1/HF2/HF3 thresholds: re-use v2 pre-reg (β-extension grid; peak-β must lie within sweep range; ratio max/min ≥ 1.5 per critical-slowing-down signature; tau_recovery monotone in β)
- Smoke gate at N=1024 2-seed first; production at N=4096 only if smoke shows non-degenerate slowing

## Trigger for cap_map move

If HARD_PASS at extended β grid showing peak-β within the sweep range — PB3 row LIFT product-feature reliability +1-2%. If MIDDLE_BAND or HARD_FAIL — annotation only; v251 base case still STANDS.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
