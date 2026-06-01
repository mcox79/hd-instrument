# Strategy request: KF-5 phase-mechanism v2 (basin-volume alternate signature)

**Filed by:** verdict_handler v268 -> v269 batched 16-verdict
**Date:** 2026-05-29
**Recipient:** exp_dev

## TASK

Reship a KF-5 phase-mechanism rescue with an alternate phase-signature operationalization. Current KF-5 phase-mechanism HARD_FAILS with ratio=1.0 (range_m2/range_m8=1.0 = RANGE INVARIANT under over-capacity M_frac=8), but KF-5 base capability from v267 architecture-level survival is UNCHANGED.

## WHY

The KF-5 phase-mechanism subhypothesis was: range degrades as M_frac crosses into over-capacity (range_m2/range_m8 > 1.5 = phase-signature). v269 kf5_phase_v1 returned ratio=1.00 = no degradation = subhypothesis closed. BUT range may be the wrong signature; alternate phase-signatures (basin-volume, spectral-gap, free-energy-slope) may show the over-capacity transition that range misses. Per [[feedback-rehabilitation-after-rejection]] 3 rescue arms needed before subhypothesis closure consideration.

## CONTRACT

- Build kf5_phase_v2_n4096.py that operationalizes phase-signature as: (a) basin-volume ratio (volume of attractor basin at M_frac=2 vs M_frac=8 via attractor-counting in small perturbation neighborhoods); OR (b) spectral-gap ratio (gap between top-2 eigenvalues of weight matrix at M_frac=2 vs M_frac=8); OR (c) free-energy-slope (slope of log-partition function in beta at M_frac=2 vs M_frac=8).
- 3-seed minimum, N=4096, M_fracs={2.0, 8.0} (matches v1 protocol for direct comparison).
- HP: signature_ratio >= 1.5 (rescue target — proves phase-signature exists in some operationalization); HF: signature_ratio < 1.0.
- Include `--timeout 1800` per [[feedback-per-experiment-timeout-required]].
- Anchor name MUST honor `_n4096` PROT-018 binding contract.

## AUTONOMY

exp_dev chooses which alternate signature (a/b/c) to implement first cheapest-first per [[feedback-rescue-sketch-first-sequencing]]; spectral-gap is likely cheapest (existing eigenvalue infrastructure) so probable first choice.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
