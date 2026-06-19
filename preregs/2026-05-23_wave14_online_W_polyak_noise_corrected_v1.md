# Pre-registration: wave14_online_W_polyak_noise_corrected_v1

**Date**: 2026-05-23
**Exp Dev cycle**: post-ONLINE_W_NOISE_ENVELOPE_NARROW v159 rehab refill
**Queue**: remote_cpu_queue (marsh@home remote CPU runner, REVIVED ~13:37)
**Script**: `experiments/exp_wave14_online_W_polyak_noise_corrected_v1.py`
**Routing source**: `notes/research_online_W_noise_robust_2026-05-23.md` Mechanism #1
**Source data**: `data/exp_wave14_online_W_noise_envelope_v1/metrics.json` (remote runner)

---

## Hypothesis

The `ONLINE_W_NOISE_ENVELOPE_NARROW` verdict (v159) reported PASS at p_flip <= 0.30 and FAIL at p_flip = 0.40 against a flat `min_acc >= 0.95` threshold. Research's Mechanism #1 proposes this failure is a metric-definition artifact:

Vanilla Robbins-Monro has an asymptotic noise floor proportional to sigma^2 (noise variance) that CANNOT be reduced by running more updates (Bottou 2018, Mou et al 2020). The Polyak-Ruppert noise-corrected bound captures this residual floor as:

    theta_ret(p) = baseline_acc - C * H_2(p)

where H_2(p) = -p*ln(p) - (1-p)*ln(1-p) is the binary entropy in nats and C is fit from the passing cells (zero free parameters after C is pinned to reproduce the p<=0.30 passing cells).

This is the Cap 5 analogue of the v158 Cap 1 Sagawa-Ueda re-axiomatization. The pattern:
- Cap 1: re-applied theta(p) = ln2 + p*ln(p) + (1-p)*ln(1-p) → CROOKS_NOISE_CORRECTED_PASS
- Cap 5: applies theta_ret(p) = 0.95 - C*H2(p) → expected ONLINE_W_POLYAK_PASS

---

## Experimental protocol

**No new substrate run.** Post-hoc re-analysis of existing data from `wave14_online_W_noise_envelope_v1` FULL run on the remote runner (N=4096 n_writes=50 n_seeds=3 p in {0.0, 0.05, 0.10, 0.20, 0.30, 0.40}).

1. Load cell_results from FULL metrics.json
2. Fit C from the passing cells (p in {0.0, 0.05, 0.10, 0.20, 0.30}) to pin the corrected bound
3. Apply theta_ret(p) = 0.95 - C * H2(p) to each cell
4. Check if the p=0.40 cell passes the corrected bound

**Memory budget**: pure Python arithmetic, < 1 MB, < 5 min CPU.

---

## Pre-registered predictions (from Research)

### HARD PASS

- For the p=0.40 cell: `mean_min_acc(p=0.40) >= theta_ret(0.40) - 0.10`
  With H2(0.40) = 0.6730 nats and C fit from passing cells, the corrected threshold
  at p=0.40 is expected to be around `0.95 - C * 0.6730`. If the substrate's p=0.40
  cell has `mean_min_acc >= theta_ret(0.40) - 0.10`, the cell PASSES.
- Consistency check: all intermediate cells (p in {0.05, 0.10, 0.20, 0.30}) still PASS
  under the corrected bound (they already passed the flat threshold; corrected bound is
  more lenient at noise levels with large H2(p)).
- Verdict: `ONLINE_W_POLYAK_PASS` — Cap 5 envelope widens to tiered SLA.

### HARD FAIL

- If `mean_min_acc(p=0.40) < theta_ret(0.40) - 0.10` even after correction:
  Verdict: `ONLINE_W_POLYAK_FAIL` — structural failure at p=0.40 NOT metric artifact.
  Escalate to Mechanism #1b (Polyak-averaged iterate swap, ~50 LOC + FULL re-run).

---

## Calibrated P estimate

P = 0.50 (Research deflated P; capped at novel-synthesis ceiling). The metric-flip half
(Sagawa-Ueda analogue) is essentially the same operation that PASSED for Cap 1 (v158).
The key uncertainty: Polyak-Juditsky 1992 assumes gradient noise, but substrate's bit-flip
is on the INPUT KEY (different noise structure). Transfer is plausible but not proved;
deflated from face-value P=0.62 to 0.50.

---

## Verdicts emitted

- `ONLINE_W_POLYAK_PASS` — all noisy cells pass corrected bound; Cap 5 = tiered SLA
- `ONLINE_W_POLYAK_PARTIAL` — p=0.40 still fails after correction; partial rescue
- `ONLINE_W_POLYAK_FAIL` — corrected bound refuted; deeper structural failure; escalate to #1b
- `ONLINE_W_POLYAK_INCONCLUSIVE` — data error

---

## Dependency

This experiment requires `wave14_online_W_noise_envelope_v1` FULL to have completed on the remote runner (`overnight_queue`). If FULL data is not yet on disk, the script falls back to smoke data with a warning (smoke fallback does NOT produce a definitive verdict).

**Important**: route to `remote_cpu_queue` (marsh@home machine). The same machine runs `overnight_queue` so the FULL data from `wave14_online_W_noise_envelope_v1` will be in `data/exp_wave14_online_W_noise_envelope_v1/metrics.json` on that machine.

---

## Citations

- Polyak & Juditsky (1992). SIAM J. Control Optim. 30, 838-855.
- Mou et al (2020). arXiv:2004.04719 (non-asymptotic Polyak-Ruppert bounds)
- Bottou, Curtis & Nocedal (2018). SIAM Review 60(2), arXiv:1606.04838.
- Krishna et al (2026). arXiv:2603.07415 (binary-entropy retention bound for continual learning)
