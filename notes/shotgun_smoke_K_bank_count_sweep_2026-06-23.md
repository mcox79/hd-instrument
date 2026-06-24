# Shotgun Smoke: K-bank Count Sweep (2026-06-23)

Script: `experiments/shotgun_smoke_k_bank_count_sweep_v1.py`
Wall: 43.5s total. Pure numpy. N_TOTAL=2048, N_TRAIN=2000, N_HELD=400 words (text8).
Feature-gated soft-assignment (softmax, T=0.5) across K banks; each bank gets N_TOTAL/K dims.

## Per-K results

| K  | N_per | BPC    | lift vs K=1 | gate_util | wall_s |
|----|-------|--------|-------------|-----------|--------|
| 1  | 2048  | 8.5067 | 0.0000      | 0.000     | 13.0   |
| 2  | 1024  | 7.4407 | +1.0660     | 0.999     | 11.2   |
| 4  | 512   | 8.0199 | +0.4868     | 1.000     | 10.4   |
| 8  | 256   | 8.1763 | +0.3304     | 1.000     | 1.9    |
| 16 | 128   | 8.2157 | +0.2910     | 1.000     | 1.8    |

Baseline BPC for K=1: 8.5067 (bits/token on held-out).

## HARD_INFO

**VERDICT: HARD_PASS.**
K*=2 shows BPC lift +1.0660 vs K=1 baseline (threshold was 0.05). All K>1 clear the pass bar.

**Shape: peaked at K=2.**
Lift peaks at K=2 (+1.07), then declines monotonically: K=4 (+0.49) -> K=8 (+0.33) -> K=16 (+0.29).
Not monotonic-up; K=2 is the interior optimum at this scale.
Interpretation: splitting the fixed N=2048 budget into 2 banks of 1024 improves retrieval quality,
but further splitting (K=4+) fragments each bank too much to offset the routing benefit.
The Drosophila K=4 compartment design may reflect a different tradeoff space (larger N, discrete routing,
learned gate) rather than the soft-gate optimum seen here.

**Gate entropy:**
All K>=2 run at ~100% of max entropy (uniform routing). The randomly-initialized gate does not
discriminate; all banks are nearly equally utilized. This is a confound -- the gate adds partition
diversity (each bank sees a different N_per-dim slice) but does NOT route semantically distinct inputs
to distinct banks. Observed lift at K=2 is therefore from the partition diversity effect, not semantic routing.

## Optimal K finding

K*=2 at N_TOTAL=2048. 2-bank may be cheaper than Drosophila K=4 at this scale.
Lift is substantial (+1.07 BPC) relative to the 0.05 threshold -- not a borderline result.

## WHAT_THIS_DOES_NOT_SHOW

- Small-scale only (N_TOTAL=2048, N_TRAIN=2000 words from text8).
- Not testing K-bank at production N=8192; partition fragmentation tradeoff may shift.
- Soft gate (softmax, random init) differs from hard winner-takes-all Drosophila KC->MBON routing.
- Gate never trained; 100% uniform utilization means partition effect not routing effect.
- BPC metric is bits/token (not chars); not directly comparable to text8 character-level floors.
- Does not test K-bank with pretrained or backprop encoder (char-trigram only).
- Single seed (SEED=42); no variance estimate.

## Follow-on questions flagged

1. Does K*=2 hold at N_TOTAL=8192 or does it shift toward higher K?
2. With a trained/discriminative gate (gradient or Hebbian competitive), does semantic routing
   reduce the K*=2 ceiling by routing similar inputs to the same bank?
3. Does K=4 (Drosophila design) outperform K=2 at larger N or with trained gate?
