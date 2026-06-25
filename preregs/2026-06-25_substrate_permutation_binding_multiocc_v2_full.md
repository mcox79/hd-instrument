# Pre-registration: substrate_permutation_binding_multiocc_v2_full

**Date:** 2026-06-25
**Anchor:** substrate_permutation_binding_multiocc_v2_full
**Queue:** local_cpu_queue
**Seeds:** [11, 13, 19] (cross-cell consistent)
**D:** 512 (FHRR dim; smoke == full)

## Promotion context

USER 2026-06-25: the v1 cell (`exp_e3_permutation_binding_multiocc_cpu_v1`) HARD_PASS'd at n_seeds=1 (FHRR=0.0119,
permutation=1.0000, lift=+0.9881 on n=84 multi-occurrence subset). Not chain-grade-tier-eligible per BIAS-14.

v2: re-run at n_seeds=3 with PER-SEED FHRR-base perturbation. v1 used `_fhrr(crc32(name))` which is seed-independent. v2
XORs in the per-seed offset: `_fhrr_seeded(name, seed) = exp(1j * rng(crc32(name) ^ seed_hash).uniform(0, 2pi, D))`. Each
seed gets independent role + num vectors -> genuine cross-seed cv data.

## Strategic significance

HRR primitive UPGRADE: permutation-indexed binding rescues a known FHRR failure mode (same-role collision in superposition).
Recchia-Jones 2015 paper. Brain analogue Wei-Wang-Wang 2012 bump-attractor desync (the brain DOES this).

The mechanism unblocks multi-occurrence multi-hop arithmetic on word problems -- substrate can store + recover multiple
operands sharing the same semantic role without superposition mix. Composes with substrate's existing HRR cleanup.

## Mechanism (unchanged from v1)

For each pool of extracted (value, role, occ) operands:
- bind k-th occurrence of role with PERMUTED key roll(role_vec, k * 7) (cyclic shift)
- bundle via complex multiplication + bundle_norm
- unbind via complex conjugate; cleanup via cosine over prototype values

Baseline (FHRR): bind with plain role_vec (no occurrence index). Multi-occurrence operands collide.

Metric: answer-accuracy on the multi-occurrence subset of ASDiv 1-op problems = (recover operand_i + operand_j, execute
gold op, compare to answer).

## Pre-registered bands (LOCKED at module init via assert)

### HARD_PASS_CHAIN_GRADE
- permutation mean top1 >= 0.95
- FHRR baseline mean < 0.10
- lift mean >= 0.85
- cv across 3 seeds <= 0.05 (on permutation top1)

### HARD_PASS_PARTIAL (= MIDDLE_BAND)
- permutation mean 0.70 - 0.95 OR cv 0.05 - 0.10

### HARD_FAIL
- permutation mean < 0.70

## Q-discipline

v1 reported perm=1.0000 (saturation rail). With per-seed FHRR perturbation + 3 seeds:
- expect some seeds to slightly miss 1.000 (e.g., 0.988 or 0.976) — the cyclic-shift permutation is information-preserving
  but not infinite-cleanup
- cv should be very tight (the permutation either works at the cyclic-shift granularity or it doesn't)
- if all 3 seeds report exactly 1.000, suspect saturation; Skunkworks may demote to MEASURED_MECHANISM tier

## Cross-cell discipline

- ASCII only
- Substrate-only (no LLM forward calls; numpy + FHRR primitives only)
- Per-arm metrics in verdict_msg per Fix #28 (perm_per_seed + fhrr_per_seed + lift_per_seed + n_subset_per_seed)
- Bands locked at module init via assert (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
- Seeds [11, 13, 19]
- META_M6: NAIVE baseline = FHRR plain-role-key recall on SAME multi-occurrence subset, SAME seed (DERIVED in cell;
  no copy from another regime)

## Smoke-vs-full discipline

Smoke (1 seed, seed=11, items[:200]) vs full (3 seeds, all items) match on EVERY capacity-sensitive dimension:
- D=512 (both)
- FHRR primitives (both)
- ROLES + cues + extraction (both)
- multi-occurrence subset definition (both)
- gold-slot finder (both)

Differences: items used (200 vs all) and seed count. The multi-occurrence subset n in v1 smoke was 84 of items[:200] (so
~42% are multi-occ); full ASDiv has ~600 items -> expect n_subset ~250.

This is a benign smoke-vs-full size change (more items = more subset cases; not a regime change). The mechanism
(permutation-indexed binding) operates identically.

## Timeout estimate

Smoke wall (1 seed, items[:200], n_subset~84): ~0.08s per v1
formula: timeout_s = ceil(1.5 * 0.08 * (600/200)^1 * (3/1)) = 1s
Plus checkpoint overhead: **timeout_s = 300** (5min; conservative).

## PROT compliance

- PROT-018, 019, 020: do not apply.
- PROT-021: timeout < 14400s.

## Symmetric verify rail

Verdict reports:
- per-seed permutation top1, FHRR top1, lift
- per-seed n_subset (the test-set size rail)
- mean + cv across seeds for each metric

## Honest negatives possible

- Per-seed FHRR could vary (the per-value vector phases differ); if some seeds land favorably-aligned, FHRR could spike
  to ~0.15-0.20 in one seed (would fail HARD_PASS_FHRR_MAX); MIDDLE_BAND honestly.
- cv > 0.05 if permutation's cleanup margin is seed-sensitive on certain multi-occ-cases; MIDDLE_BAND honestly.
