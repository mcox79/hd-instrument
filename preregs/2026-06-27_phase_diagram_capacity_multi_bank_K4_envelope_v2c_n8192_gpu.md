# Pre-reg: phase_diagram_capacity_multi_bank_K4_envelope_v2c_n8192_gpu (RESCUE Cell B v2c; 2026-06-27)

**Anchor:** `phase_diagram_capacity_multi_bank_K4_envelope_v2c_n8192_gpu`
**Cell:** `experiments/exp_phase_diagram_capacity_multi_bank_K4_envelope_v2c_n8192_gpu.py`
**Queue:** `overnight_queue` (GPU mandate; per USER 2026-06-27 NO LOCAL + Fix #24)
**Tier hint:** HARD_PASS candidate if K=4 sharding survives at alpha=4 headroom=10x at N=8192.
**Parent:** v2b `notes/skunkworks_landed_vet_5cell_batch8_2026-06-27.md` Cell 5 split (B of 2); v2b OOM at N=16384.

## Parent (cell v2b) finding being rescued

v2b ran 130s on remote then HARD_FAIL_UNIT_EXCEPTION CUDA OOM at K=4 ingest:
1.024 GiB alloc on top of 5.38 GiB already allocated; ceiling 6.80 GiB on
the 8 GiB RTX 4060 Ti. The memory-frugal sequential build did not bring
v2b under budget at N=16384.

Per orchestrator flag-back option #3 (cheapest, preserves alpha>=4
finding): halve N_DIM 16384 -> 8192. W matrix is N^2 fp32, so per-bank W
shrinks from 1.07GB -> 268MB; 4 banks total = 1.07GB vs. v2b's 4.28GB.
Plus transient batch tensors at ~0.2GB -> peak target < 1.5GB, well under
the 6.8GB budget. All other params (alpha=4.0, headroom=10x, K=4 banks,
3 seeds) unchanged.

The capacity claim ("substrate exceeds predicted band at alpha>=4") is
**alpha-relative not N-relative** -- testing at N=8192 alpha=4 headroom=10x
still discriminates the Skunkworks batch 8 finding.

## Scope

ONE phase point only: alpha_N=4.0, headroom=10x. 3 seeds [11, 13, 19].
NO mech / KNN / bare arms in Cell B (covered by Cell A).

## v2c mechanism (K=4 multi-bank Hebbian; memory-frugal build at N=8192)

- Shard M=32768 triples round-robin across K_banks=4 (8192/bank)
- Build each bank's W=(8192, 8192) fp32 sequentially; torch.cuda.empty_cache() between banks
- Per-query: accumulate max sim per V_C across banks WITHOUT materializing the full (K, B, V_C) stack
- chunk_size = 500 to keep batch tensors bounded
- PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True set at module init

## PER-ARM HP-SCOPE (SCHEMA-VET 5b)

| Arm | HP gate | Scope |
|-----|---------|-------|
| MULTI_BANK_K4 | HP_MB_REC_MIN >= 0.95 AND CV <= 0.05 | alpha=4.0 h=10x N=8192; 3 seeds |
| MECH | EXEMPT (routed to Cell A) | declared in HP_SCOPE |
| KNN_SENTINEL | EXEMPT (routed to Cell A) | declared in HP_SCOPE |
| BARE_E_R | EXEMPT (routed to Cell A) | declared in HP_SCOPE |

## HARD_PASS / MIDDLE_BAND / HARD_FAIL tiering

- **HARD_PASS_MULTI_BANK_K4_N8192**: rec_mean >= 0.95 AND cv <= 0.05 across 3 seeds at
  alpha=4 headroom=10x N=8192. Confirms K=4 sharding preserves capacity at the
  predicted-band corner (alpha-relative claim).
- **MIDDLE_BAND_MULTI_BANK_N8192**: rec_mean in [0.75, 0.95) OR cv > 0.05.
- **HARD_FAIL_MULTI_BANK_BELOW_FLOOR_N8192**: rec_mean < 0.75 (mechanism doesn't survive K=4 sharding).
- **HARD_FAIL_UNIT_EXCEPTION**: any OOM / CUDA error halts loop (META_RULE_J).

## HARD_FAIL conditions

- Unit exception including OOM (META_RULE_J halt-on-error).
- Cardinality breach: observed n_units < EXPECTED_N_UNITS=3 (META_RULE_H).
- Substrate-only violation: any _llm_forward_calls > 0.
- BIAS-S regime drift (alpha_N / headroom / keys_unique_mode mismatch).
- GPU not available at full mode (Fix #24 mandate; exit 1 at main).

## Cardinality

EXPECTED_N_UNITS at full = 1 phase point * 3 seeds = 3.
META_RULE_H HARD_FAIL on breach.

## GPU mandate (Fix #24; load-bearing)

- DEVICE = 'cuda' constant (module init)
- torch.cuda.is_available() asserted at __main__ entry (full mode); HARD exit
- per-unit torch.cuda.reset_peak_memory_stats + peak_mem_mb logged
- empty_cache() between bank builds
- expandable_segments:True allocator set at module init

## Substrate-only-decode gate

n_llm_forward_calls per arm = 0.

## Real data / synthetic provenance

100% synthetic-substrate-bipolar (no external data).
CORPUS_PROVENANCE = synthetic_substrate_bipolar_codebook_capacity_v2c_multibank_K4_n8192.

## REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`, `cardinality_ok`,
`N_DIM`, `detail.multi_bank_recall_mean`, `detail.multi_bank_recall_cv`,
`detail.multi_bank_recall_per_seed`, `detail.peak_mem_mb_max`, `detail.N_DIM`,
`HP_SCOPE`.

## Discipline gates

- Fix #26 predispatch: v2b anchor in atoms.jsonl as
  HARD_FAIL_UNIT_EXCEPTION_OOM; v2c is rescue with smaller N (not duplicate).
- PROT-018 + PROT-019: anchor includes `_n8192` suffix; cell has explicit
  N_DIM=8192 assertion in selftest T10 binding the suffix to the config
  (no ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH).
- Fix #24 GPU mandate: torch.cuda asserted at full + DEVICE='cuda' constant.
- META_RULE_H: cardinality_ok mandatory + asserted in selftest T8.
- META_RULE_J: no silent except (halt on unit error).
- META_RULE_K n/a (NO_LOCAL).
- META_RULE_L: band-floor MIDDLE_BAND not HARD_PASS.
- SCHEMA-VET 5b: per-arm HP scope declared.

## Discriminator-must-survive-scale (USER 2026-06-26)

The discriminator at N=8192 alpha=4 h=10x is rec >= 0.95 with cv <= 0.05.
Substrate tolerance scales with N (more dimensions -> easier capacity);
shrinking N from 16384 -> 8192 makes the test *harder* on the substrate
side, so a PASS at N=8192 is strictly stronger evidence than a PASS at
N=16384. If N=8192 fails the discriminator while v2b would have passed
at N=16384 (counterfactual), the substrate's capacity claim is
N-dependent and the alpha-relative framing breaks -- in that case the
result is MIDDLE_BAND not HARD_PASS, and Skunkworks should request a
N-sweep variant before generalization. This is acceptable risk per
USER 2026-06-26 "MIDDLE_BAND is a real verdict, not consolation prize".

## Estimated cost

3 MULTI_BANK_K4 ingest + retrieve units at N=8192 V_C=10240 M=32768.
On RTX 4060 Ti with memory-frugal sequential build: ~2-5 min per unit;
~6-15 min total wall (smaller than v2b due to N^2 compute scaling).

VRAM peak target: ~1.5 GB (4 W matrices fp32 @ N=8192 = 1.07GB +
transient batch tensors ~0.2GB + V/K codebook ~0.3GB). Well under 6.8GB.

## Routing

`overnight_queue` on marsh@home (GPU mandatory). Push + queue_add via
orchestrator (push harness-DENIED to exp_dev).

## Suggested --timeout

3600s (60 min) per Fix #24 GPU budget + buffer. Shorter than v2b's 5400s
because N=8192 compute is ~4x cheaper than N=16384 (N^2 ops).
