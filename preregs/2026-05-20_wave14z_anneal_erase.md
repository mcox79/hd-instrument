# Pre-registration: wave14z_anneal_erase

Date: 2026-05-20
Status: Pre-registered, oracle-asserted, gated, smoke-validated
Experiment: [exp_wave14z_anneal_erase.py](../experiments/exp_wave14z_anneal_erase.py)

## Why

User's materials-science insight: in real systems, ordered phases are destroyed
by raising temperature past Tc. The substrate analog is direct: raising
effective noise rate past a threshold should destroy stored patterns. The AGS
phase diagram T_g(alpha) = 1 + sqrt(alpha) gives the prediction.

Compares three erasure protocols:
- ANNEAL: W' = (1-eta) * W + eta * Gaussian. Global thermal disorder.
- DIRECT_SUBTRACT: W' = W - eta * (v_e outer k_e) / N. Exact rank-1 subtraction.
- ANTI_HEBBIAN: W' = W - eta * (W k_e)(k_e^T) / d. Self-referential (Mirage-prone).

## Hypothesis

DIRECT_SUBTRACT at eta=1.0 with orthogonal keys IS the ground truth (perfect
erase). With correlated keys, cross-talk reappears.

ANNEAL at eta near 1.0 collapses norm globally — destroys ALL patterns. This
is "factory reset" not selective forgetting, but it provides a real upper
bound on what's achievable.

Smoke evidence (N=512, n_facts=50): ANNEAL eta=1.0 passes argmax+rank+cos+
paraphrase probes; norm_ratio=0.309 just barely misses 0.30 threshold.

## Kill criterion

If all three methods fail the multi-probe under correlated keys at scale,
selective erasure under correlation is fundamentally hard for this substrate
geometry. Either accept "global anneal" as the only clean GDPR mechanism,
or pursue Householder preconditioning.

## Oracle assertion

DIRECT_SUBTRACT at eta=1.0 MUST kill direction (cosine <= 0.30). Norm may
stay high (cross-talk under correlation). This is a real physics finding
captured in the multi-probe.

## Operational definition

- N=4096, n_facts=300, n_erase=75, rank_L=75 (strong correlation)
- For each method, sweep eta across method-appropriate range
- 5 seeds, multi-probe metrics per (method, eta) cell
- All methods compared on identical (keys, values) sets per seed

## Cited mechanism

- AGS phase diagram (Amit-Gutfreund-Sompolinsky 1985)
- Bouchaud-Cugliandolo aging protocols (cond-mat/0603583)
- Kovacs effect (Riechers et al. arXiv:1910.10374)
- User's annealing insight (this session, 2026-05-20)
- ROME direct-subtraction analog (arXiv:2202.05262)

## Expected runtime

Smoke: ~5 sec
Full: ~10-15 min on GPU (3 methods x 5-10 etas x 5 seeds)

## Verdict labels

- `ANNEAL_DIRECT_WINS`: direct_subtract passes all probes
- `ANNEAL_THERMAL_WINS`: only anneal passes
- `ANNEAL_MULTIPLE_PASS`: 2+ methods pass
- `ANNEAL_AH_WINS`: anti-Hebbian only (unexpected)
- `ANNEAL_NONE_GDPR`: no method passes
- `ANNEAL_INCONCLUSIVE`: empty data

## What product decision this enables

DIRECT_WINS: GDPR mechanism is direct subtraction (canonical, ROME-aligned).
THERMAL_WINS: substrate offers "factory reset" only, not selective forgetting.
MULTIPLE_PASS: multiple defensible mechanisms; can pitch tunable choice.
NONE: substrate is fundamentally limited for selective GDPR; pivot.
