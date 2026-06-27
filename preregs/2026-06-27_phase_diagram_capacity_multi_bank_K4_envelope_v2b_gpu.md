# Pre-reg: phase_diagram_capacity_multi_bank_K4_envelope_v2b_gpu (RESCUE Cell B; 2026-06-27)

**Anchor:** `phase_diagram_capacity_multi_bank_K4_envelope_v2b_gpu`
**Cell:** `experiments/exp_phase_diagram_capacity_multi_bank_K4_envelope_v2b_gpu.py`
**Queue:** `overnight_queue` (GPU mandate; per USER 2026-06-27 NO LOCAL + Fix #24)
**Tier hint:** HARD_PASS candidate if K=4 sharding survives at alpha=4 headroom=10x.
**Wave:** Tier-2 rescue from `notes/skunkworks_landed_vet_5cell_batch8_2026-06-27.md` Cell 5 split (B of 2).

## Parent (cell v1) finding being rescued

Skunkworks batch 8 (Cell 5) MULTI_BANK_K4 arm OOM'd on RTX 4060 Ti:
W = N^2 fp32 = 1.07GB at N=16384; K=4 banks = 4.28GB W alone + V/K matrices
for shard ingestion exceeded the 6.8GB VRAM budget. Cell A drops multi-bank
entirely; Cell B re-isolates with explicit memory-frugal sequential build +
empty_cache between banks + expandable_segments allocator.

## Scope (Skunkworks rec c + d)

ONE phase point only: alpha_N=4.0, headroom=10x (matches parent v1 multi-bank
probe target). 3 seeds (was 1; OOM never reached seeds 13/19). NO mech / KNN /
bare arms in Cell B (covered by Cell A).

## v2b mechanism (K=4 multi-bank Hebbian; memory-frugal build)

- Shard M triples round-robin across K_banks=4
- Build each bank's W sequentially; torch.cuda.empty_cache() between banks
- Per-query: accumulate max sim per V_C across banks WITHOUT materializing
  the full (K, B, V_C) stack (avoids 4x transient memory)
- chunk_size = 500 (smaller than Cell A's 1000) to keep batch tensors bounded
- PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True set at module init

## PER-ARM HP-SCOPE (SCHEMA-VET 5b)

| Arm | HP gate | Scope |
|-----|---------|-------|
| MULTI_BANK_K4 | HP_MB_REC_MIN >= 0.95 AND CV <= 0.05 | alpha=4.0 headroom=10x; 3 seeds |
| MECH | EXEMPT (routed to Cell A) | declared in HP_SCOPE |
| KNN_SENTINEL | EXEMPT (routed to Cell A) | declared in HP_SCOPE |
| BARE_E_R | EXEMPT (routed to Cell A) | declared in HP_SCOPE |

## HARD_PASS / MIDDLE_BAND / HARD_FAIL tiering

- **HARD_PASS_MULTI_BANK_K4**: rec_mean >= 0.95 AND cv <= 0.05 across 3 seeds at
  alpha=4 headroom=10x. Confirms K=4 sharding preserves capacity at the
  predicted-band corner.
- **MIDDLE_BAND_MULTI_BANK**: rec_mean in [0.75, 0.95) OR cv > 0.05.
- **HARD_FAIL_MULTI_BANK_BELOW_FLOOR**: rec_mean < 0.75 (mechanism doesn't
  survive K=4 sharding).
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
CORPUS_PROVENANCE = synthetic_substrate_bipolar_codebook_capacity_v2b_multibank_K4_alone.

## REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`, `cardinality_ok`,
`detail.multi_bank_recall_mean`, `detail.multi_bank_recall_cv`,
`detail.multi_bank_recall_per_seed`, `detail.peak_mem_mb_max`, `HP_SCOPE`.

## Discipline gates

- Fix #26 predispatch: parent v1 anchor in atoms.jsonl as
  MEASURED_MECHANISM_MECH_arm_partial; no duplicate-of-prior-HARD_FAIL flag.
- PROT-018 + PROT-019: anchor has no `_n<N>` suffix.
- Fix #24 GPU mandate: torch.cuda asserted at full + DEVICE='cuda' constant.
- META_RULE_H: cardinality_ok mandatory + asserted in selftest.
- META_RULE_J: no silent except (halt on unit error).
- META_RULE_K n/a (NO_LOCAL).
- META_RULE_L: band-floor MIDDLE_BAND not HARD_PASS.
- SCHEMA-VET 5b: per-arm HP scope declared.

## Estimated cost

3 multi-bank-K4 ingest + retrieve units at N=16384 V_C=20480 M=65536.
On RTX 4060 Ti with memory-frugal sequential build: ~5-15 min per unit;
~15-45 min total wall.

VRAM peak target: < 5GB (4 W matrices fp32 = 4.28GB + transient batch ~0.2GB).
If OOM occurs at this regime, the K=4 mechanism is genuinely non-viable on
the available hardware; HARD_FAIL is the honest outcome.

## Routing

`overnight_queue` on marsh@home (GPU mandatory). Push + queue_add via
orchestrator (push harness-DENIED to exp_dev).

## Suggested --timeout

5400s (90 min) per Fix #24 GPU budget + 50% buffer. PROT-019 requires
>= 3600s for any cell with _n>=4096 suffix; this cell has no _n suffix but
the N=16384 config triggers the spirit of PROT-019 -> 5400s safe.
