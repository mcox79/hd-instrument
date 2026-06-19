# Pre-registration: wave14_betX_skill_composition_v1

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Strategy Phase 1 push #3 (Lane D; Research mechanism delivered cycle 61)
Author: experiment_dev session, pipeline tick 81

## Why

Per META strategic plan v79 + Strategy push: Bet X tests whether substrate
can encode/decompose multi-step skill programs via position-indexed binding.

Substrate role: store program-pointer-and-audit-trace; HYBRID executor (external
Python dispatches primitives). Lane D cognitive architecture deliverable.

## Mechanism (per Bet X research cycle 61)

- Binding scheme: position-indexed `s = sum_i a_i ⊗ p_i`
  where a_i are skill atoms, p_i are position atoms
- Decode at position i: probe = s * p_i ≈ a_i; cleanup vs skill codebook
- 2-level hierarchy: meta-skill m_j = sum_k (a_k ⊗ p_k^meta); program at level 2
  bundles meta-skills, decode unbinds twice
- Audit trace: same bundled vector enables per-position decomposition

## Multi-probe success criteria (cap_map v77)

- Per-skill execution accuracy >= 0.80 across 5 skill types
- Audit trace decomposable >= 90% of executed primitives
- 2-level hierarchy works (meta-skill calling 5-10 named skills)
- 3 seeds, N=4096

## Verdict labels

- BET_X_COMPOSITION_PASS (all criteria clear)
- BET_X_FLAT_PASS (level-1 only; 2-level hierarchy fails)
- BET_X_KILLED (per-skill < 0.50 OR audit < 50%)
- BET_X_INCONCLUSIVE

## Runtime: ~5 min
