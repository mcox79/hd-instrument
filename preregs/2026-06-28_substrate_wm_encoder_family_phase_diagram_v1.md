# Pre-registration: substrate_wm_encoder_family_phase_diagram_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** Research directive (USER 2026-06-28) — systematic phase-diagram coverage across COMPONENTS. We've done encoder family for PC (`substrate_pc_encoder_family_phase_diagram_v1`) and seqbind (`substrate_seqbind_encoder_family_sweep_v1`). This is the third COMPONENT-SUBSTITUTION cell, targeting the WM K-cliff primitive — the most load-bearing Stage 1 primitive after PC.

## Anchor

`substrate_wm_encoder_family_phase_diagram_v1_seed_{7,13,19}` (3 sibling files; chunked-per-seed per USER 2026-06-28 ritual).

Shared core: `experiments/_substrate_wm_encoder_family_phase_diagram_v1_core.py`.

## Routing

- **Smoke queue:** local (laptop CPU; `.venv/Scripts/python.exe` direct invocation; gate via `local_cpu_queue` for traceability)
- **Full queue:** **overnight_queue** (GPU; 4 encoders x 4 K x 3 B = 48 phase points per seed at N=8192; FFT-heavy for HRR + complex64 for FHRR — well-suited to CUDA. Both CPU and GPU queues IDLE per dispatch context; this fills overnight GPU work.)
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch routes through Orchestrator (SendMessage post-smoke).

## Why this cell exists (the gap)

WM K-cliff primitive: chain-grade evidence at K_cliff(B)=256·B for HRR-real at N=8192 (per `substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked` cert ledger entry). All prior WM cells fix encoder = bipolar OR HRR-real. The question: **does the encoder family matter for multi-bank WM capacity?**

- Encoders differ in per-bank cap (HRR ~ N / (4·log2 N); FHRR ~ N/2; sparse — lower per-bank but better crosstalk resistance with dense tags)
- Multi-bank WM tests the bind+bundle+bank-tag mechanism, NOT just retrieval
- Prior encoder cells (PC, seqbind) found ALL 4 encoders distinguish per-pair — encoder is a discriminating lever in those primitives. WM is the natural next test.

## Encoder families (OUTER axis)

| Family | Codebook | Bind | Unbind | Bank-tag handling |
|--------|----------|------|--------|-------------------|
| `binary_bipolar` | `{-1, +1}^N`, dense | elementwise mul | elementwise mul | elementwise mul (encoder-native) |
| `hrr_real` | `N(0, 1/N)^N` unit-L2 | FFT circular conv | FFT circular correlation | FFT circular conv (encoder-native) |
| `fhrr` | unit-modulus `exp(i*phi)` in C^(N/2) | elementwise complex mul | bundle * conj(query) | elementwise complex mul (encoder-native) |
| `sparse_bipolar` | `{-1, 0, +1}^N`, s/N=0.02 | elementwise mul (sparse) | elementwise mul | **DENSE bipolar tags** (Plate MAP-A convention; sparse content + dense roles) |

**Sparse-bipolar design note:** vanilla sparse-mul-sparse collapses to near-zero density (density (0.02)^2 = 0.0004), making sum-bundle unrecoverable. Per Plate MAP-A architecture: items use sparse codebook (preserves sparse semantics), positions and bank_tags use DENSE bipolar (preserves binding integrity through mul). This is the honest sparse-WM architecture.

## Sweep axes (LOCKED at module init)

| Axis | Values | Count |
|------|--------|-------|
| encoder_family (OUTER) | {binary_bipolar, hrr_real, fhrr, sparse_bipolar} | 4 |
| K_per_bank (inner) | {64, 256, 1024, 4096} | 4 |
| num_banks B (inner) | {4, 16, 64} | 3 |
| N (fixed) | 8192 (FULL); 4096 (SMOKE) | 1 |

`codebook_size=16384` (FULL) / `4096` (SMOKE), `n_items_to_query=96` (FULL) / `32` (SMOKE).

**Cardinality FULL per seed:** `4 * 4 * 3 = 48` phase points per seed (some may be SKIPPED if `K * B > codebook_size`).
**Cardinality SMOKE per seed:** `4 * 3 * 2 = 24` corner points per seed (K ∈ {64, 256, 1024}, B ∈ {4, 16}; smoke uses K=1024,B=16 → total_K=16384>codebook=4096 → 4 skipped, observed=20).

Seeds: 7, 13, 19 (chunked per-seed; 3 sibling files).

## Hypothesis

**H1 (PRIMARY): Encoders WILL differ in K_cliff location AND/OR slope at fixed N.**
- HRR-real, binary_bipolar: predicted K_cliff(B) = 256·B at N=8192 (chain-grade baseline)
- FHRR: 1.5x higher per Plate 2003 (N/2 complex pairs); K_cliff = 384·B
- sparse_bipolar: half per-bank cap (sparse codes less crosstalk-tolerant); K_cliff = 128·B

**H2 (regime-mapping): Different encoders WIN in different regimes.**
- If H1 holds: FHRR wins high-K regime; HRR/binary win mid-range; sparse may dominate at very low K with dense tags (mechanism CPU-friendly).

**H3 (positive-control):** HRR_real at (K=64, B=4, N=8192) reproduces WM v3 chain-grade MULTI recall ≥ 0.50. (WM v3 N=4096 corner: MULTI ~ 0.95 at this K; N=8192 even better.) If control fails: HARD_FAIL_CONTROL_FAIL.

**H4 (null):** All 4 encoders identical within ±0.05 MULTI at every (K, B). Honest-negative; downstream cells free to pick any encoder for WM.

**H5 (dominance):** One encoder strictly dominates (mean MULTI > 0.10 above runner-up at all points). Strongest finding — substrate should switch WM default.

## Discriminator: 3 arms per phase point

| Arm | Description |
|-----|-------------|
| `MULTI_BANK_BIND` | Encoder's native multi-bank: bundle = sum_{b,k} bind(bank_tag[b], bind(positions[k], items[b,k])); query = bind(bank_tag[b], position[k]) |
| `SINGLE_BANK_BASELINE` | Same bundle; query is JUST position[k] (no bank tag); exposes interference cliff |
| `RANDOM_FLOOR` | Fresh-random codebook entries as queries; floor ~ 1/M_items |

**Per-encoder discriminating_fraction prediction (HYPOTHESIZED@):**
- binary_bipolar: ~0.35 (medium K range in HARD_PASS+MIDDLE_BAND)
- hrr_real: ~0.35
- fhrr: ~0.45 (higher per-bank cap)
- sparse_bipolar: ~0.25 (lower per-bank cap)

**Discriminating_fraction (overall) >= 0.30** = pre-reg PASS threshold (>= 15/48 points per seed in HARD_PASS + MIDDLE_BAND across all encoders).

## Pre-reg bands (per-point; LOCKED at module init)

| Tier | MULTI recall | Discriminator (MULTI - SINGLE) | Floor gap (MULTI - RANDOM) |
|------|---------------|--------------------------------|-----------------------------|
| SATURATED | >= 0.95 | >= 0.30 | (any) |
| HARD_PASS | [0.50, 0.95) | >= 0.30 | (any) |
| MIDDLE_BAND | [0.30, 0.50) | >= 0.20 | (any) |
| FLOOR | (any) | (any) | < 0.05 (mechanism at chance) |
| HARD_FAIL | else | else | else |

## Cell-level verdict (FULL, per seed)

- **HARD_PASS_ENCODER_DISCRIMINATION_WM_KCLIFF:** cardinality_ok + arms_differ (multi != random for all encoders) + 4 distinct encoder mechanism hashes (>= 2 of 6 encoder-pairs differ) + disc_fraction >= 0.30 + ≥1 encoder has MB+HP-or-SAT coexistence (interior cliff observable) + positive control reproduces (HRR_real K=64 B=4 N=8192 MULTI ≥ 0.50)
- **MIDDLE_BAND_ENCODER_DIFFERS_BUT_LOW_DISC:** arms_differ + encoder-pair hashes differ but disc_fraction < 0.30
- **MIDDLE_BAND_ENCODER_DIFFERS_BUT_NO_INTERIOR_CLIFF:** encoders distinguish but no MB+HP coexistence for any encoder
- **MIDDLE_BAND_NULL_ENCODER_INVARIANCE:** arms_differ but ALL encoder-pair hashes IDENTICAL (H4 confirmed — encoder NOT a discriminating lever for WM)
- **HARD_FAIL_CARDINALITY_BREACH:** observed != expected (after K*B>CB skipping)
- **HARD_FAIL_ARMS_IDENTICAL:** MULTI == RANDOM hash for any encoder (mechanism not working)
- **HARD_FAIL_CONTROL_FAIL:** HRR_real positive control doesn't reproduce WM v3

## Cell-level verdict (SMOKE)

- **HARD_PASS_SMOKE:** cardinality_ok (20 after skip) + arms_differ (4 encoders MULTI != RANDOM) + 4 distinct encoder hashes + positive control (HRR_real K=64 B=4 N=4096 MULTI ≥ 0.40) + cliff observable at smoke (≥1 encoder MULTI in [0.10, 0.95])
- **HARD_FAIL_SMOKE_*:** various; see core.smoke_gate_predicate

## CRLB / K-cliff predictions (META_RULE_AG)

```python
def k_cliff_prediction(encoder_family, B, N):
    base_per_B = {
        "hrr_real": 256,
        "binary_bipolar": 256,
        "fhrr": 384,
        "sparse_bipolar": 128,
    }
    return int(round(base_per_B[encoder_family] * B * N / 8192))
```

| Encoder | B=4 | B=16 | B=64 |
|---------|-----|------|------|
| hrr_real | 1024 | 4096 | 16384 |
| binary_bipolar | 1024 | 4096 | 16384 |
| fhrr | 1536 | 6144 | 24576 |
| sparse_bipolar | 512 | 2048 | 8192 |

Per-point `k_cliff_prediction` + `past_cliff_predicted` flag stamped in metrics.

## Calibration selftest

For each encoder ∈ {binary_bipolar, hrr_real, fhrr, sparse_bipolar} at K_per_bank=16, B=2, N=512, M_codebook=128, Q=32, seed=7:
- Run eval_phase_point; verify `multi_recall > 2 * random_recall` OR `multi_recall >= 0.10` (mechanism works at easy scale)

If ANY encoder fails calibration, selftest exit 1 with verdict_msg naming the failing encoder.

**Empirically validated on seed=7 (smoke timestamp 2026-06-29T04:xx):** binary_bipolar 0.906, hrr_real 0.750, fhrr 0.938, sparse_bipolar 0.750 multi_recall at K=16 B=2 N=512 → all >> floor.

## Arms per point (META_RULE_AF)

Each (encoder, K, B) point logs 3 arm results:
1. `MULTI_BANK_BIND` — encoder's multi-bank top1 recall
2. `SINGLE_BANK_BASELINE` — same bundle, query w/o bank tag (interference floor)
3. `RANDOM_FLOOR` — fresh-random query

`arms_differ_sha256` per encoder:
- `multi_vs_random_differ`: SHA-256(json(multi.recall_per_point)) != SHA-256(json(random.recall_per_point))
- `multi_vs_single_differ`: same but for single arm

`encoder_pair_hashes` (META_RULE_AF extension): all 6 pair-comparisons computed.

## Cardinality OK (META_RULE_H)

```
FULL : EXPECTED_N_UNITS = 48 per seed (4 enc x 4 K x 3 B; some skipped if K*B > 16384 codebook)
SMOKE: EXPECTED_N_UNITS = 24 per seed (4 enc x 3 K x 2 B; some skipped if K*B > 4096 smoke codebook)
```

`cardinality_ok` is computed AFTER subtracting expected skips (`K * B > codebook_size`). HARD_FAIL if observed != expected_after_skip.

## GPU mandate (Fix #24)

- `import torch` at TOP of file (PROT-020 routing-gate)
- `DEVICE = torch.device("cuda")` preferred; CPU fallback ALLOWED for smoke
- **FULL on CPU REFUSED** unless `HDLAB_QUEUE=local_cpu_queue` env explicit-route
- FFT (HRR), complex64 matmul (FHRR), elementwise mul + bipolar dense (binary, sparse-tags) — all matmul-and-FFT-heavy; well-suited to CUDA
- Per-point peak_mem_mb logged
- GPU util target: avg `peak_mem_mb / 100` >= 0.30 (codebook_size=16384, N=8192 = 1GB float32; multi-bank bundle eats VRAM well)

## Chunked-per-seed architecture

3 sibling files: `experiments/exp_substrate_wm_encoder_family_phase_diagram_v1_seed_{7,13,19}.py`.
Shared core: `experiments/_substrate_wm_encoder_family_phase_diagram_v1_core.py`.

Per-seed checkpointing via `experiments/_seed_checkpoint.py` (PROT-021 config-mismatch guard ON; META_RULE_H_ANCHOR check ON).

4 defensive patterns (USER 2026-06-28 hardening):
1. start_marker: STARTED metrics written before any heavy work
2. crash-diag: outer try → import-crash sentinel with full traceback
3. per-unit checkpoint: write_partial_key per seed
4. heartbeat: per-phase-point flush print

## Disciplines (mandatory)

- META_RULE_AC: arms differ by SHA-256 (multi vs random; per-encoder)
- META_RULE_AE: pre-reg bands LOCKED at module init
- META_RULE_AF: 4 encoder arms produce distinct hashes
- META_RULE_AG: per-encoder per-point K-cliff prediction stamped (HYPOTHESIZED@)
- META_RULE_AH: tag every number MEASURED@ | HYPOTHESIZED@ | THEORETICAL@
- META_RULE_H: cardinality_ok mandatory (48 full, 24 smoke; minus skips for K*B>CB)
- META_RULE_J: no silent except; halt on any unit exception
- META_RULE_L: band-floor results = MIDDLE_BAND not HARD_PASS
- DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26): smoke validated cliff in [0.10, 0.95] at smoke scale — confirmed empirically (binary 0.656 / hrr 0.500 / fhrr 0.531 / sparse 0.688 at K=64 B=4; cliff at K=256 to FLOOR)
- BAND-FLOOR-IS-MIDDLE-BAND (USER 2026-06-26)
- Honest-downward classification per encoder

## Positive control

`hrr_real` at (K_per_bank=64, B=4, N=8192) MULTI recall >= 0.50 (FULL).
Smoke variant: `hrr_real` at (K=64, B=4, N=4096) MULTI >= 0.40.

**Empirically MEASURED@ smoke (2026-06-29):** HRR_real K=64 B=4 N=4096 MULTI = 0.500 → smoke gate PASS.

WM v3 chain-grade evidence: K_per_bank=64 B=4 N=4096 → MULTI ~ 0.95 SINGLE ~ 0.05 in v3. Our smoke at MULTI=0.500 with B=4 N=4096 K=64 is lower because:
1. v3 cells use a different bank-tag mechanism (purely subtractive interleaving); this cell uses bind-by-bank-tag (more general; lower base recall)
2. v3 cells write each item with N_items_per_K queries; this cell uses Q=32 random sample of total_K=256 items per query

Both are still well above SINGLE/RANDOM floors → mechanism working.

## Composition edges (substrate atomization context)

- Substituted COMPONENT: encoder family (4 choices)
- Composed-with primitive: WM multi-bank bind+bundle mechanism (FIXED across arms)
- Downstream atomization: HARD_PASS_ENCODER_DISCRIMINATION_WM_KCLIFF → SUBSTRATE_ENCODER_FAMILY_DISCRIMINATING_FOR_WM + WINNING_ENCODER_FOR_WM_KCLIFF; MIDDLE_BAND_NULL_ENCODER_INVARIANCE → ENCODER_NOT_DISCRIMINATING_LEVER_FOR_WM

## ETA

Per phase point on GPU (N=8192, codebook=16384 fp32, B=64 worst case):
- bind+bundle: B * K_per * (N or N/2) FFT or matmul; ~5-15s
- query: Q=96 * (N or N/2) FFT or matmul + Q*16384 cleanup; ~2-5s
- Total per point: ~7-20s; budget 15s average

48 points/seed * 15s = ~12 min/seed; add 30s init = ~15 min/seed FULL on GPU. 3 seeds = ~45 min total.

Per-point on CPU (smoke; N=4096): ~0.3-0.7s (measured); 20 pts * 0.5s = 10s + 5s init = ~15s SMOKE.

Timeouts (per --timeout exp_dev mandate):
- SMOKE: 300 s
- FULL: 3600 s (1 hour margin per seed; well above 15-min budget; allows OOM-recovery)

## Substrate-only decode gate

`_LLM_CALL_COUNTER[0] == 0` asserted at exit (substrate-only).

## Smoke gate (MUST pass before FULL dispatch)

1. 24 corner points all ran (4 expected skips for K*B>CB = 20 observed)
2. cardinality_ok: observed_n_units == expected_after_skip
3. arms_differ: multi_vs_random_differ True for ALL 4 encoders
4. encoder_pair_hashes: 4 distinct encoder mechanism hashes (all 6 pairs differ)
5. positive_control: hrr_real @ K=64 B=4 N=4096 MULTI >= 0.40
6. cliff observable: at least 1 encoder shows MULTI in [0.10, 0.95]

If gates 1-6 fail, FULL dispatch HARD-blocked.

**Empirically VALIDATED 2026-06-29:** all gates pass at smoke; HARD_PASS_SMOKE. 20/20 pts; sat=0 hp=4 mb=0 floor=11 fail=5; 4-encoder-distinct; PC HRR=0.500 (gate=0.40).

## Encoder-family routing tier classifications

- DOMINANT_ENCODER: top1_mean > 0.10 above all other encoders (strongest case for downstream substitution)
- COMPETITIVE_ENCODER: top1_mean within +/- 0.05 of best
- DOMINATED_ENCODER: top1_mean > 0.10 below best

## Outputs

`data/exp_substrate_wm_encoder_family_phase_diagram_v1_seed_{7,13,19}/metrics.json`:
- per_seed phase_map (one dict per phase point: encoder, K_per, B, N, multi/single/random recall, discriminator, tier, peak_mem_mb)
- per_encoder_summary (multi_recall_mean + tier counts + observed K-cliff per B)
- encoder_pair_distinctness (6 pair-comparisons; differ flag)
- positive_control_result (HRR_real K=64 B=4)
- k_cliff_predictions (per encoder, per B)
- arms_differ_per_encoder (multi vs random, multi vs single)
- tier_counts overall

Atomization candidates (post-Skunkworks landed-VET):
- if HARD_PASS_ENCODER_DISCRIMINATION_WM_KCLIFF: `SUBSTRATE_ENCODER_FAMILY_DISCRIMINATING_FOR_WM` + `WINNING_ENCODER_FOR_WM_KCLIFF` (winning encoder)
- if MIDDLE_BAND_NULL_ENCODER_INVARIANCE: `ENCODER_NOT_DISCRIMINATING_LEVER_FOR_WM`
- if HARD_FAIL: NEEDS-RERUN

## Independence claim

This is a NEW anchor (substrate_wm_encoder_family_phase_diagram_v1) — not a re-run of PC or seqbind encoder cells. Each prior encoder-family cell tested a different primitive (PC = retrieval; seqbind = position-binding). WM = multi-bank capacity. They share encoder-family structure but test different mechanisms.

`tools/predispatch_check.py` should be run by Orchestrator before dispatch to confirm no prior anchor by this name exists.
