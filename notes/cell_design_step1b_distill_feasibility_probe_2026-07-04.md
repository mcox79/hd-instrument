# Cell-design note: Step 1b distillation feasibility probe (band calibration)

Date: 2026-07-04. Author: exp_dev (Step 1b cell author).
Purpose: pre-prereg feasibility probe per Gate B / CRLB discipline (predicted bands
computed in code BEFORE prereg). All numbers below are MEASURED by the probe scripts
(session scratchpad `probe_step1b_feasibility.py` + `probe_step1b_block_ext.py`,
configs reproduced below) on the REAL local BGE cache. ASCII only.

## Probe config (both probes)

- Teacher: `data/substrate_index/cached_indices/bge_large_v2_name_43905_8a40445a.npz`
  (43905 real KB concepts, BGE-large 1024-d, L2-normed; verified on disk).
- Split: seeded permutation (numpy default_rng(7)); train 4000, held-out 1000.
- Student: torch.nn.Linear(1024 -> 4096, bias=False), Adam lr=1e-3, 400 steps,
  batch 256, torch.manual_seed(7).
- Objective: relational KD (MSE on in-batch pairwise cosine matrix, off-diagonal)
  + 0.5 * InfoNCE (tau=0.07; positive = teacher top-1 NN; probe 1 negatives = teacher
  NN ranks 10-60 i.e. TOO-hard; probe 2 negatives = semi-hard teacher-cos band
  [0.3, 0.6] per algebra drill Q4).
- Probe 1 sparsifier: unstructured top-k=82 magnitude + sign (naive; identity STE).
- Probe 2 sparsifier: block-structured K=128 blocks x L=32, 1 active/block,
  argmax-hard forward + softmax/tanh soft backward (Gumbel-ST style, tau=1.0).
- Algebra probe 1: naive sparse-real -> FHRR complexify + dense random phasor keys
  (hdlab make_atoms/bind/unbind). Algebra probe 2 (SBC): block-local circular
  convolution via hdlab bind/unbind on [K,L]-reshaped codes, random one-hot-per-block
  signed keys. Cleanup: cosine argmax over V_eval=5000 codebook. 50-60 trials/point.

## MEASURED results

### Probe 1 (naive top-k + FHRR) -- the false-win, caught empirically

| arm | pearson_r (all held pairs) | hi80_cos (n=3241) | ret_agree@10 | keyed J=2/5/10/20 |
|---|---|---|---|---|
| DISTILLED_topk | 0.5500 | 0.9826 | 0.4855 | 1.000 / 0.983 / 0.800 / 0.483 |
| RANDOM_topk | 0.0016 | 0.0003 | 0.0015 | 1.000 / 1.000 / 1.000 / 1.000 |
| CHARPOS (Step-1-style) | 0.6335 | 0.6143 | 0.0655 | 1.000 / 0.650 / 0.300 / 0.083 |

Interpretation: naive distilled codes OVER-COLLAPSE the high-similarity tail
(0.983 vs teacher mean 0.845 on the same pairs) and pay for it in algebra:
roundtrip falls to 0.483 at J=20 while incoherent RANDOM codes hold 1.000.
This is exactly the false-win the algebra drill predicted (P ~0.12 path).
CHARPOS pearson_r is inflated by bulk-pair correlation; its hi-tail (0.61 vs
teacher 0.845) and ret_agree@10 (0.0655) show the real orthographic ceiling.

### Probe 2 (block code K=128 + SBC block-local circconv + semi-hard negatives)

- Semantic (held-out): spearman = 0.8072, pearson = 0.8320, hi80_cos = 0.6226
  (calib_err 0.2227, under-shoot side = margin-preserving), ret_agree@10 = 0.5162.
- Keyed roundtrip (production path): 1.000 at J=2,5,10,20. Shuffled-key control:
  0.000 hit-rate at J=5.
- Bundle-superposition (no keys; ablation's sensitive axis), per-item recall@J:
  BLOCK 1.000 / 0.664 / 0.248 / 0.106 at J=2/5/10/20;
  DENSE_SIGN control 0.624 (J=5) / 0.048 (J=20). Sparse block dominates dense.
- Semi-hard band [0.3,0.6] covers 0.801 of train pairs at this corpus.
- Wall: 188.5s total (400 train steps = ~140s CPU laptop, batch 256).

### CRLB-style resolution bound (computed in code)

Teacher pair-cos spread on 2000-concept sample: mean 0.5201, std 0.0918.
Block-code similarity estimator noise ~ sqrt(0.25/K):
K=64 -> attenuation bound r_max ~ 0.826 (CANNOT reach 0.85 GO);
K=102 -> ~0.880 (marginal); K=128 -> ~0.901 (clears 0.85 GO).
=> primary K_BLOCKS = 128 (L=32, sparsity 3.125%), consistent with the
design-ablation finding that ~3.1 pct dominates 2 pct
(`data/exp_encoder_design_ablation_v1_smoke/metrics.json`, commit e069ce430).

## Design deltas adopted from the two Director inputs

1. ADOPTED: block-structured sparsity (K blocks, 1 active/block) + block-local
   circular convolution (SBC) as the composition algebra, declared in prereg.
2. ADOPTED: relational similarity-distillation primary + InfoNCE semi-hard
   auxiliary; NO absolute-MSE term (never had one).
3. ADOPTED: semi-hard negatives from teacher-cos band [0.3,0.6] (probe 1 used
   too-hard ranks 10-60; probe 2 switched; hi-tail over-collapse disappeared).
4. ADOPTED: per-block argmax-ST with soft backward (Gumbel-ST family).
5. ADOPTED: dual-gate with BOTH keyed roundtrip (non-negotiable, reject B<0.90)
   AND bundle-superposition axis (ablation input) + shuffled-key + sparse-vs-dense
   controls.
6. ADOPTED: naive top-k+FHRR kept as in-cell comparison arm (false-win
   demonstrator), per Director instruction.
7. ADOPTED: N_DIM and K_BLOCKS parameterized; FULL sweeps K_BLOCKS {64,128}.
8. REJECTED (with reason): K_BLOCKS=64 as primary (ablation transfer suggestion
   "start near k=32-equivalent"): the CRLB bound shows K=64 cannot reach the 0.85
   Spearman GO band (r_max ~0.826); K=64 is kept as the FULL sweep secondary
   point to measure the rate-transfer question the ablation flagged.
9. REJECTED: mining hard negatives from teacher top-NN ranks (probe 1 did this;
   drill Q4 says top-NN are true positives; probe 2's semi-hard band is used).
