# Pre-registration: wave14h_alpha_sweep

Date: 2026-05-20
Status: Pre-registered, gated, queueable
Experiment: [exp_wave14h_alpha_sweep.py](../experiments/exp_wave14h_alpha_sweep.py)

## Why

wave14h tonight gave 76.7pp leak reduction (80% → 3.3%) at ALPHA_ERASE=1.0 but
kept_recall dropped 78% → 68%, missing the 80% target. The math-based fix
works; the parameter wasn't tuned. This sweep maps the leak vs kept-recall
frontier and identifies the operating point for the GDPR positioning.

## Hypothesis (H)

There exists alpha in [0.2, 1.5] giving leak_rate <= 5% AND kept_recall >= 85%
(GDPR-grade operating point).

Backup: if H fails, there exists alpha giving leak_rate <= 10% AND
kept_recall >= 80% (Pareto-acceptable operating point).

## Kill criterion

If no alpha satisfies even the backup criterion (leak <= 10% AND kept >= 80%),
the anti-Hebbian rank-1 mechanism is insufficient as written and needs
extension (e.g. structured codebook for keys, multi-step erase, etc).

## Cited mechanism

- ROME (Meng 2022, arXiv:2202.05262) — rank-1 W edits for fact editing in GPT-2
- MEMIT (Meng 2022 mass editing follow-up) — same family of mechanism
- wave14g_research_wside_erasure.md (our derivation): anti-Hebbian rank-1 is
  the math-backed fix for the cycle-12 GDPR gap

## Operational definition

- N=4096, n_facts=100 random ±1 (key, value) pairs, n_erase=30
- W = sum_i v_i k_i^T / N (delta-rule equivalent for random keys)
- Method A: no W edit (baseline; expect full leak)
- Method B: anti-Hebbian rank-1 erase per fact, with parameter alpha
- Sweep alpha in {0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.85, 1.0, 1.2, 1.5}
- 5 seeds per alpha
- Metrics: method_B leak_mean (fraction of erased facts still retrievable),
  method_B kept_mean (fraction of non-erased facts still retrievable)

## Expected runtime

Smoke (N=512, 1 seed, 2 alphas): ~5 sec
Full (N=4096, 5 seeds, 10 alphas): ~3 min on GPU

## Verdict labels

- `ALPHA_SWEEP_HITS_TARGET`: some alpha satisfies leak <= 5% AND kept >= 85%
- `ALPHA_SWEEP_PARTIAL`: some alpha satisfies leak <= 10% AND kept >= 80%
- `ALPHA_SWEEP_NO_FRONTIER`: even the weaker criterion fails
- `ALPHA_SWEEP_INCONCLUSIVE`: empty per_alpha (script bug)

## What product decision this enables

HITS_TARGET → GDPR-grade erase is a real product differentiator at alpha=X.
Pitch language: "Cryptographic-grade forgetting in our memory tier:
provable <=5% leak with <=15pp recall cost. Math-backed, regulator-friendly."

PARTIAL → softer positioning: "Tunable erasure tradeoff curve, customers
choose their (leak, recall) operating point."

NO_FRONTIER → erase story is partial-only; lean into other capabilities.
