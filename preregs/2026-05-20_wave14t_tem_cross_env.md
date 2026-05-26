# Pre-registration: wave14t_tem_cross_env (compositional schema test)

Date: 2026-05-20
Status: Pre-registered, oracle-asserted, gated
Experiment: [exp_wave14t_tem_cross_env.py](../experiments/exp_wave14t_tem_cross_env.py)

## Why

This is the highest-upside capability test. If our substrate transfers role-
presence detection across environments with disjoint filler atoms, we have a
compositional schema that no transformer demonstrates at the byte level.

## Hypothesis (H)

The substrate's Hadamard binding produces role-filler representations where
the ROLE atom is invariant under filler substitution. A linear probe trained
to detect role-presence on env-A bundles should transfer with accuracy >=
1.5x of both (PCA-projected baseline) and (random-label baseline).

## Kill criterion

If substrate transfer < 1.15x PCA baseline, the binding isn't producing
transferable schema — we have only env-specific structure (failed claim).

## Oracle assertions

1. Substrate in-env accuracy >= 0.85 (probe works within env-A)
2. PCA transfer accuracy < 0.75 (PCA does NOT accidentally solve the task)

## Operational definition

- N=4096, n_roles=8, 30 fillers per env (disjoint sets for A and B)
- Each scene: bundle of 3 (role, filler) bindings where role ⊗ filler is
  Hadamard product
- Train: 2000 env-A scenes
- Test in-env: 500 env-A scenes
- Test transfer: 500 env-B scenes (same 8 roles, different fillers)
- Linear probe: ridge regression on bundle → role-presence labels (8 binary)
- Three methods compared:
  - SUBSTRATE: raw bundles
  - PCA: project to top-8 PCs of env-A train, then probe
  - RANDOM: shuffle train labels, then probe
- 7 seeds

## Cited mechanism

- Whittington et al. 2020 Cell, Tolman-Eichenbaum Machine: factorized
  representation of role-filler structure
- Plate 1995 HRR, Smolensky 1990 TPR: tensor product role-filler binding
- Frady-Sommer 2020 Resonator Networks: factor recovery via iterative resonance

## Expected runtime

Smoke (N=512, 1 seed): ~10 sec
Full (N=4096, 7 seeds): ~10-15 min on GPU

## Verdict labels

- `TEM_SCHEMA_CONFIRMED`: substrate >= 1.5x baselines AND > 0.65 absolute
- `TEM_SCHEMA_PARTIAL`: substrate > 1.15x baselines but not 1.5x
- `TEM_NO_SCHEMA`: substrate barely beats baselines
- `TEM_INCONCLUSIVE`: empty data

## What product decision this enables

CONFIRMED: substrate has compositional generalization at byte level that
transformers don't demonstrate. **This is the central LLM-displacement
claim.** Headline pitch.

PARTIAL: real but bounded. Position carefully.

NO_SCHEMA: substrate doesn't do real compositional transfer; binding is
just a vector trick. Drop the compositional pitch.
