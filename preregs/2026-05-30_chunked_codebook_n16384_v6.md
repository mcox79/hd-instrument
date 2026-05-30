# Prereg: chunked_codebook_n16384_v6

**Date:** 2026-05-30
**Anchor:** chunked_codebook_n16384_v6
**Script:** experiments/exp_chunked_codebook_n16384_v6.py
**Queue:** overnight_queue
**Timeout:** 43200s (battery-class for N=16384)

## Why this anchor

v4 and v5 (P2 sub3) HARD_FAILed on OOM at N=16384 codebook construction. The
Kerdock 4-coset codebook for N=16384 is (4N, N) = (65536, 16384) float32 =
4.3 GiB just for the codebook. v4/v5 used `torch.cat` at the end of
`make_kerdock_4coset_codebook` which doubles peak memory during the concat.

v6 SELECTED STRATEGY: **Strategy A** — pre-allocate the (4N, N) buffer
once, then place each (N, N) coset block directly into the buffer via
in-place row-assignment. NO `torch.cat`. Calls `torch.cuda.empty_cache`
between coset constructions.

(Strategy B = single-codeword streaming, Strategy C = CPU staging were not
selected because Strategy A is the simplest minimal change to v4/v5 and
the prior diagnosis was specifically the `cat`-induced doubling.)

## Sweep grid

- N = 16384 (PROT-018 _n16384 binding).
- M grid: {2048, 4096, 8192} (REDUCED from v4 spec per user; scale up in v7 if v6 succeeds).
- Seeds: {7, 17, 23} (3 seeds; codebook construction is deterministic-by-N, so
  seed variation is on the (key, value) sampling only).
- Per-(M, seed) checkpoint.

## Pre-registered bands

- **HARD_PASS (HP)** = chunked construction succeeds at ALL 3 M-points
  AND max GPU memory observed < 6 GiB AND mean recall at the largest M
  is >= 0.95 AND max_M_at_95_recall is identified >= 2048.
- **HARD_FAIL (HF)** = chunked construction OOMs at any M (chunking strategy
  insufficient). With HF_FAIL_ON_OOM=True the verdict aggregator treats any
  OOM at an M with NO surviving seed as HARD_FAIL.
- **MIDDLE_BAND (MB)** = chunking works at small M, OOMs at large M
  (intermediate result; informative about scaling). Specifically: when at
  least one seed succeeds at every M but some seeds OOM, OR when all seeds
  succeed but recall threshold not met at largest M.

## Outcome plan

| Verdict | Action |
|---|---|
| HARD_PASS | N=16384 substrate is viable; ship v7 to push past M=8192 and add deeper analysis. |
| HARD_FAIL | Strategy A insufficient; v7 switches to Strategy C (CPU staging) — costs latency but eliminates GPU codebook copy. |
| MIDDLE_BAND | Identify M_max_safe; cap_map row records "N=16384 substrate valid up to M_max_safe with Strategy A". |

## Closed-form self-tests in the script

- `make_kerdock_codebook_chunked(N=1024, device=cpu)` returns codebook of
  shape (4096, 1024) without OOM. (Smoke check.)
- `compute_verdict(fake_hp)` -> HARD_PASS for clean chunking + recall.
- `compute_verdict(fake_hf)` -> HARD_FAIL for OOM at all M.
- `compute_verdict(fake_mb)` -> HARD_FAIL when M=8192 has 0 successful seeds
  (per HF_FAIL_ON_OOM=True policy). The MIDDLE_BAND case is reached when some
  seeds succeed at every M but recall/peak threshold not met.

## OOM pre-check

Codebook (4N, N) at N=16384 float32 = 4.295 GiB (one allocation, no doubling).
W (N, N) = 1.073 GiB. keys+vals at M=8192 = 1.0 GiB. Scratch = ~0.5 GiB.
Pre-allocated peak budget = 4.3 + 1.07 + 1.0 + 0.5 ~= 6.9 GiB.

Per role contract: O(N^2) ops at N>4096 require pre-check. Estimated peak is
just above the 6 GiB ceiling; this is the EXACT regime we're testing. The
HARD_FAIL band at OOM captures the expected failure if Strategy A is
insufficient. The HP band at < 6 GiB documents whether Strategy A is enough.

Per-cell-seed checkpoint isolates OOM: if M=8192 OOMs, M=2048/4096 results
are still recorded.

## Multi-scale smoke

Smoke runs at N_SMOKE=4096 with M={256, 1024}. CPU smoke peak_gpu_gib = 0
(no GPU on the smoke machine). The smoke validates correctness of the
chunked construction algorithm; the GPU memory measurement happens during
FULL execution on the GPU runner via `torch.cuda.max_memory_allocated`.

**Smoke GPU memory peak (CPU smoke): 0.0 GiB (CPU run; GPU peak measured at FULL).**

## Timeout estimate

smoke_wall_s = 1.2s at N=4096 on CPU. FULL: N 4096->16384 (4x; exp=2.0 for
N^2 matmul) = 16x. seeds 1->3 (3x). M points 2->3 (1.5x). GPU is ~10x
faster than CPU for matmul.
Per-cell-seed CPU estimate: 1.2 * 16 = 19s. GPU estimate: 19 / 10 = 2s.
But codebook build dominates not matmul; ~30-300s per M on GPU.
9 cells * 300s = 2700s typical, 9 cells * 1200s = 10800s worst.

User pre-spec'd 43200s battery-class (12h) for safety margin given prior
v4/v5 OOMs at this scale.

**Timeout: 43200s** (user spec; battery-class for N=16384).

## PROT-018 _n16384 binding

`N = 16384` is a module-level constant. Verified by `grep -E "(N\s*=|n\s*=)\s*16384" experiments/exp_chunked_codebook_n16384_v6.py`.

## Dependency check

- experiments/exp_wave14y_erase_kerdock_v3.py (build_gf2t_tables, build_q_b_signs, v1.sylvester_hadamard) -- exists
- experiments/_seed_checkpoint.py -- exists
- No upstream data files required.
