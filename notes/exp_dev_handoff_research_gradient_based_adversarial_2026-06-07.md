# exp_dev hand-off -- research: gradient-based (white-box) adversarial attacks

**Filed-by:** research sub-agent, 2026-06-07
**Trigger:** notes/research_drill_gradient_based_adversarial_attacks_2x_2026-06-07.md
**Pause state:** CHECK data/orchestrator_paused.flag before dispatching. If flag present, hold.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS only.
exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name,
ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Context

Adversarial testing Drill C refuted 5/6 adaptive-attack predictions (AUC >= 0.97 on all tested attack
types). The sole remaining CCA2-tier gap is gradient-based (white-box) attacks. Today's research drill
mapped the attack surface, quantified P_deflated per attack class, and identified 5 empirical cells.

The primary finding: KF-1 cosine has a smooth, well-defined gradient surface (P_deflated = 0.52 that
GBDA-class attack achieves AUC drop > 0.15). The HOC1 + KF-1 defense paradox provides genuine
multi-layer protection (joint evasion P_deflated = 0.22). A separate cross-hop Merkle gap was
identified (P_deflated = 0.35) that is independent of gradient attacks and is closeable with ~200 lines.

---

## Anchor candidates (rank-ordered; exp_dev picks based on queue state and budget)

### Anchor 1 (PRIORITY): GBDA-style gradient attack on KF-1 [GATE DECISION]

- Pointer: research note Section 7 Cell A + Section 9 (Cheap decisive test)
- Substrate-product reading: P_deflated = 0.52 that AUC drops > 0.15. This is the gate for all
  downstream hardening. If HARD-FAIL (AUC drop > 0.25): trigger randomized smoothing + AT pipeline.
  If HARD-PASS (AUC drop < 0.05): gradient robustness is genuine and architecture class deserves credit.
- Tier hint: GPU (gradient computation; Gumbel-softmax relaxation; needs backprop through encoder)
- Why now: This is the primary open threat after today's 5/6 refutation result. All other hardening
  decisions gate on this result.

---

### Anchor 2: KF-1 false-positive rate under gradient optimization [EVADE-AS-LEGITIMATE]

- Pointer: research note Section 7 Cell B
- Substrate-product reading: P_deflated = 0.42 that false-positive rate > 0.10. Measures whether
  fabricated claims can be made to LOOK grounded (not just whether true claims are detected). Different
  attack surface from Anchor 1.
- Tier hint: GPU (gradient optimization of input)
- Why now: Complementary to Anchor 1. Together they bound both directions of KF-1 evasion.

---

### Anchor 3: HOC1 + KF-1 joint evasion under gradient attack [DUAL-LAYER STRESS TEST]

- Pointer: research note Section 7 Cell C
- Substrate-product reading: P_deflated = 0.22 for joint evasion > 0.20. Defense-in-depth paradox
  (Section 2 HOC1 analysis) predicts this is hard. Empirical test either confirms the paradox is real
  or reveals that the attacker can navigate both constraints simultaneously.
- Tier hint: GPU (more complex attack loss landscape; longer wall than Anchor 1)
- Why now: If Anchor 1 shows AUC drop, Anchor 3 determines whether HOC1 saves the detection.

---

### Anchor 4: Randomized smoothing certified radius measurement [DEFENSE VALIDATION]

- Pointer: research note Section 7 Cell D + Section 4 Tier 1 rescue
- Substrate-product reading: P_deflated = 0.38 for HARD-PASS (certified radius > 0.05 with < 0.03
  clean AUC drop). Validates the proposed Tier 1 rescue mechanism. If HARD-PASS, randomized smoothing
  is the immediate production-ready defense.
- Tier hint: GPU (N=100 sample majority vote; moderate compute)
- Why now: If Anchor 1 shows AUC drop, Anchor 4 determines whether the mitigation is deployable.

---

### Anchor 5: Cross-hop Merkle gap test + H2 cross-hop NEG1 validation [INDEPENDENT GAP]

- Pointer: research note Section 7 Cell E + Section 2 Merkle + Section 5 H2
- Substrate-product reading: P_deflated = 0.52 for > 70% catch rate with H2. This is INDEPENDENT of
  gradient attacks. Closes the cross-hop input-crafting gap that was not caught by any prior adversarial
  test. Very cheap to implement (~200 lines, one NEG1 forward pass per hop-pair).
- Tier hint: CPU or local (NEG1 forward passes; no backprop needed; modest compute)
- Why now: Cheapest of the 5 cells. Should ship regardless of Anchor 1-4 results. Addresses a
  distinct vulnerability class.

---

## Context pointers

- Research note (full analysis): d:/AI/hd-instrument/notes/research_drill_gradient_based_adversarial_attacks_2x_2026-06-07.md
- Prior adaptive-attack drill: d:/AI/hd-instrument/notes/research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md
- Prior level-1 attack surface: d:/AI/hd-instrument/notes/research_drill_adversarial_substrate_divergence_2026-06-07.md
- Defense analysis v1: d:/AI/hd-instrument/notes/research_adversarial_defense_analysis_v1_2026-05-30.md
- Exp-dev role contract: d:/AI/hd-instrument/tools/orchestrator/agents/exp_dev.md
- Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract

exp_dev takes full ownership of anchor design: seed count, N, threshold formulas, queue routing,
smoke vs full mode, ETA, failure-mode mitigations. Research role ends at this file.

Orchestrator: review pause flag before dispatching exp_dev. Anchor 1 is the gate; if queue is full,
Anchor 1 and Anchor 5 should be prioritized (Anchor 1 = highest strategic value, Anchor 5 = cheapest).

## Autonomy declaration

exp_dev is free to reorder anchors, merge Cell A+B into one anchor, or split any cell further. The
only constraint: do not encode experiment design decisions in the dispatch prompt per
[[feedback-no-experiment-design-in-prompts]].
