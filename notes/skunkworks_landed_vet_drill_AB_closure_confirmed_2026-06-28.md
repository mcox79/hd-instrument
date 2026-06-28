# Skunkworks landed-VET: Drill A (option-critic) + Drill B (block-sparse) HARD_FAILs; capability closure CONFIRMED

**Date:** 2026-06-28
**Atomized by:** skunkworks_atomize_drill_AB_closure_confirmed_2026-06-28
**Discipline ref:** feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28
**Supersedes:** preliminary 3-cell closure (commit eda3d108)

## Verdict summary (independent recompute confirms)

| Cell | Verdict | Mechanism arm | Best non-mech | Best lift | arms_distinct | cardinality_ok |
|---|---|---|---|---|---|---|
| option_critic_v1 (Drill A) | HARD_FAIL | OC_FULL=0.000 | PF=0.100 | OC-V3=0.000 / OC-FLAT=-0.050 | True (6 SHA-256) | 120/120 |
| block_sparse_v1 (Drill B) | HARD_FAIL | BS_OPTS=0.100 | RB=0.200 | OPTS-RB=-0.100 | True (6 SHA-256) | 120/120 |

Both pass arms_distinct + cardinality_ok + chance_floor=2.143e-05 (1/6^6 exact) + discriminator-survives-scale at N=8192 / depth=6.

## Drill A key tell (REINFORCE plumbing works, hierarchical structure doesn't)
- flat_reinforce train: 0.12 -> 0.20 over 100 episodes (DELTA +0.08, learning)
- option_critic_full train: 0.04 -> 0.00 over 100 episodes (DELTA -0.04, anti-learning)
- Diagnosis: reward signal diluted across pi/beta/Q-U per option; hierarchical credit-assignment ambiguity prevents convergence; failure is at the HIERARCHICAL-STRUCTURE level, not the optimizer

## Drill B key tell (encoding-axis falsified)
- random_blocks (0.200) BEATS block_sparse_options_full (0.100) by 2x
- structured block-sparse doesn't preserve compositional planning signal any better than random-block; in fact 2x worse
- Diagnosis: failure is NOT an encoding-format problem; block-assignment actively HARMFUL; substrate's hierarchical-planning failure is a more fundamental compositional-credit-assignment problem

## Combined triangulation
4 mechanism classes (closed-form D_macro / state-cond-disjoint / Sutton-Precup options / Bacon-Roy option-critic) AND 2 encoding-formats (bundled HRR / block-sparse) all converge on the same root cause: substrate compositional credit-assignment at composite-depth=6 in bipolar-HRR N=8192 regime is fundamentally blocked, regardless of mechanism class or encoding format.

## Atoms landed (4)
1. **math::T3 OC HF** (`dab285c0d338611d`) cert_class=mechanism_characterization HONEST_NEGATIVE
2. **math::T3 BS HF** (`fa7e20363ed8b403`) cert_class=mechanism_characterization HONEST_NEGATIVE
3. **math::T3 CLOSURE CONFIRMED** (`c82ded1ef6f94591`) cert_class=capability_closed_CONFIRMED_5_cells_2x_drill_satisfied HONEST_NEGATIVE; supersedes preliminary 3-cell closure (commit eda3d108)
4. **meta::T_methodology META_RULE_AO_v2** (`2fb7d7757010ac66`) CONFIRMED methodology rule; supersedes META_RULE_AO with 2x-drill confirmation layer

## A5 PRE/POST
- math: 28644 -> 28647 (+3)
- meta atoms: 239 -> 240 (+1)
- meta audit: 394 -> 395 (+1)
- math audit: 41046 -> 41049 (+3)
- cert_ledger: 871 -> 874 (+3)
- Fresh-load round-trip survival: OK (all 4 atom ids retrievable via fresh open)

## CERT trajectory
- Closure-confirmation = honest-negative capability characterization (cert_increment_delta=0)
- 3 HONEST_NEGATIVE rulings; CERT N unchanged
- Substrate state: hierarchical-planning capability box CLOSED CONFIRMED at substrate bipolar-HRR N=8192 depth=6 regime

## 2x-drill discipline status
**SATISFIED.** Per USER feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28, both revival drills returned HARD_FAIL at cell-level with distinct mechanism classes (Bacon-Roy option-critic for Drill A; Hersche block-sparse encoding axis for Drill B). Closure stands per USER's discipline.

## Recommended next steps (atomized as part of closure-confirmed atom)
- substrate-product pivot (pretrained-encoder swap-in: word2vec / pythia)
- regime-shift to lower composite-depth (e.g. depth=3 or depth=4) as scaffolded scope-narrowing
- abandon hierarchical-planning at this regime; reframe M3 demo around chain-grade strengths (audit-device, KG-traversal, refuse-gate, multi-hop iter_cleanup)
- M4 substrate-as-research-director Director-options framing DEFERRED (CONFIRMED at the bipolar-HRR regime)
