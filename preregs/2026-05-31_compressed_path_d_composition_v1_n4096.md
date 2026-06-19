# Pre-registration: compressed_path_d_composition_v1_n4096

**Date:** 2026-05-31
**Anchor:** compressed_path_d_composition_v1_n4096
**Queue:** remote_cpu_queue
**Script:** experiments/exp_compressed_path_d_composition_v1_n4096.py
**Cap-map rows:** PP-2 (state compression) x R-PATH-D-NO-CEILING (composition test)

## Hypothesis

Path D depth=5 accuracy is preserved (>= 0.95) when running on a c_quant/bits8
quantized substrate W at N=4096. Compression does not interfere with the
multi-hop traversal mechanism.

## Pre-registered Bands

**HARD-PASS:** acc_compressed >= 0.95 on BOTH M values [8192, 32768] in 4/5+ seeds.
Composition is production-ready -- c_quant/bits8 is safe as compression layer
for Path D deployment.

**HARD-FAIL:** acc_compressed < 0.70 in majority of cells (n > cells/2). Compression
materially breaks Path D accuracy. PP-2 foothold carries deployment caveat.

**MIDDLE-BAND:** acc_compressed 0.70-0.95 OR passes M=8192 (nominal) but fails
M=32768 (over-capacity). Composition marginal -- deployment caveats required.

## Middle-band outcome plan

If MIDDLE_BAND: characterize the capacity boundary. If nominal M=8192 holds but
over-cap M=32768 degrades: report "compression safe up to 2N, degrades at 8N".
Strategy decides whether to add a cap constraint to PP-2 foothold annotation.

## Config

- N = 4096 (PROT-018 binding)
- M_GRID_FULL = [8192, 32768] (2N nominal, 8N over-capacity)
- depth = 5, K_paths = 100
- N_STARTS = 100 (number of start nodes for Path D)
- Seeds: [7, 17, 23, 31, 41] (5 seeds)
- Two arms per cell: baseline W (uncompressed) vs c_quant/bits8 W
- device: CPU (remote_cpu_queue)
- Total cells: 10 (2 M x 5 seeds)

## Timeout estimate

- smoke_wall_s = 0.31s (N=1024, 1 seed, 1 M=2048, 20 starts)
- FULL: N=4096 (4x), 10 cells (10x more), 100 starts (5x more per cell)
- formula: ceil(1.5 * 0.31 * (4096/1024)^1.5 * (10/1) * (100/20))
  = ceil(1.5 * 0.31 * 8 * 10 * 5) = ceil(186) = 186s
- rounded to 300s floor
- **timeout_s = 300**
- Note: M=32768 may be slower than M=2048 for build_shared; adding margin.

## Smoke result

N=1024, 1 seed, M=2048: CPD_MIDDLE_BAND (expected -- 1 seed is insufficient for HP)
acc_baseline=1.000, acc_compressed=1.000, delta=0.000. 0.31s elapsed.
No suspicious results. Proceeding to FULL.
Note: N_SMOKE=512 was rejected (odd log2=9 fails Kerdock codebook). Fixed to N_SMOKE=1024.

## N-suffix binding (PROT-018)

Anchor name _n4096 binds N_FULL = 4096. Verified: `N = 4096` in script.

## Strategic context

Composition B classification (SCORE-level): c_quant/bits8 x Path D -- does compression
preserve the primary mechanism? If YES, PP-2 foothold is mechanism-compatible and
the compression layer can be deployed transparently under Path D workloads.
