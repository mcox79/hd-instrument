# Experiment M3: asymmetric relations

**Date:** 2026-05-16
**Phase:** Week 7 molecule experiments

## Hypothesis

Encoding `loves(A, B)` as bundle(bind(AGENT, A), bind(PATIENT, B)) preserves role distinction. Querying by AGENT recovers A; by PATIENT recovers B. Swapping the fillers (loves(B, A)) returns swapped recoveries. Role confusion (AGENT query returning the patient) should be zero.

## Predicted

- forward AGENT query: 30/30 correct.
- forward PATIENT query: 30/30 correct.
- swapped AGENT query: 30/30 correct.
- role_confusion: 0/30.

## Falsification

- Any forward AGENT query returning the patient: roles aren't actually distinguishable.
- Forward and swapped giving the same recovery: the substrate isn't position-aware.

## Result (2026-05-16)

| Check | Predicted | Observed | Outcome |
|---|---|---|---|
| Forward correct (loves(A,B): AGENT->A, PATIENT->B) | 30/30 | 30/30 | confirmed |
| Swapped correct (loves(B,A): AGENT->B, PATIENT->A) | 30/30 | 30/30 | confirmed |
| Role confusion (forward AGENT returning B) | 0/30 | 0/30 | confirmed |

## Takeaway

Roles (AGENT, PATIENT) and fillers occupy genuinely orthogonal subspaces under FHRR binding. Swapping filler identity flips the recovery as expected, with zero leakage between roles. This is the simplest non-trivial demonstration of order-sensitive relational encoding in the substrate.

This result is exactly what theory predicts — no surprise here, which is itself useful confirmation. M2 and M4 produced surprises that overturned predictions; M3 is the boring-but-correct sanity check.
