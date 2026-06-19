# exp_dev hand-off -- research: integration structural gap 3x

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_integration_structural_gap_3x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

INTEG-RENORM-T1 cycle 225 HARD_FAIL: renorm_minsat=0.026, additive_minsat=0.024,
minimax=0.041, renorm/minimax=0.636.

KEY FINDING: ADDITIVE ALSO FAILS MINIMAX -- the structural gap is not renorm-specific.
Both additive superposition (0.024) and L2-renorm (0.026) are bounded BELOW minimax
(0.041). The prior algebraic claim ("renorm is guaranteed to lift integration") was
wrong because it assumed sharp softmax weights. Empirically, Sprint 2 softmax weights
are near-uniform (diagnosed from negligible delta between additive and renorm results).

The correct diagnosis: Sprint 2 is in the PARAMAGNETIC phase (spin-glass analogy):
integrated vector is equidistant from all drives, in the void between basins.
Renorm lifts norm but does NOT change angular position -- it is a no-op on cleanup
signal quality for near-uniform weights.

The minimax bound (0.041) is achievable by oracle selection of one drive's action.
Integration architectures based on BLENDING cannot exceed oracle selection when
drives are near-orthogonal and weights are near-uniform.

The correct strategy: SELECTION mechanisms (tournament, temporal cycling, learned router)
not blending mechanisms (additive, multiplicative, precision-weighted, renorm).

Cheapest path forward: TEST 0 (urgency diagnostic, 5 min) -> TEST 1 (tournament, 10 min)
-> TEST 2 (temperature sweep, 10 min) -> Mechanism 9 (temporal cycling, 20 min).

---

## Anchor Candidates (rank-ordered by P_actionable x cost)

### 1. INTEG-URGENCY-DIAG-T0 (HIGHEST PRIORITY, pre-test)

Anchor pointer: INTEG-URGENCY-DIAG-T0 (new; not yet queued)
Substrate-product reading: Determines whether Sprint 2 urgency signals have ANY variation
  (max/min ratio). If yes: tournament or temperature-tuning may work. If no: purely structural
  (temporal cycling is the correct path). This gates all other integration anchors.
Tier hint: CPU laptop; < 5 min; diagnostic only, no new architecture.
Why-now: Without this, any new integration anchor is guessing at root cause.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS (for VARIATION): max(u_k) / min(u_k) > 1.5 at Sprint 2 integration step.
  HARD-FAIL (for VARIATION): max(u_k) / min(u_k) < 1.1 (truly uniform; skip temperature paths).
  MID-BAND: ratio in [1.1, 1.5] (some variation; temperature tuning may partially help).

Implementation note: add one print statement to Sprint 2 integration code at the softmax
input step. No architecture change.

---

### 2. INTEG-TOURNAMENT-T1 (NEXT PRIORITY after T0)

Anchor pointer: INTEG-TOURNAMENT-T1 (new; not yet queued)
Substrate-product reading: Tests whether lateral inhibition WTA (tournament selection)
  matches or exceeds the minimax baseline (0.041). If tournament achieves minimax, the
  correct product capability is SELECTION not integration. Changes Sprint 2 architecture.
Tier hint: CPU laptop; 10-20 min; sweep alpha in [0.5, 1.0, 2.0].
Why-now: Tournament is the BOSE-HUBBARD MOTT INSULATOR analog -- the theoretical
  prediction is that it should match minimax when urgency rank = minimax rank.

Pre-reg bands:
  HARD-PASS: tournament_minsat >= minimax (0.041) - 0.005 at some alpha.
  HARD-FAIL: tournament_minsat < best-single (0.029) (inhibition degrades best-single).
  MID-BAND: tournament_minsat in [0.029, 0.036] (partial improvement; try Mechanism 9).

Score formula: score_k_inh = u_k - alpha * mean_{j!=k}(u_j); winner = argmax_k.
Output: single-drive action (not a blend). No L2 renorm needed.

---

### 3. INTEG-TEMPERATURE-SWEEP-T2 (if T0 shows variation > 1.5)

Anchor pointer: INTEG-TEMPERATURE-SWEEP-T2 (new; not yet queued)
Substrate-product reading: Tests whether LLM-calibrated temperature (tau = 1/sqrt(N))
  concentrates softmax weights enough to make renorm effective.
  If yes: a one-line tau change fixes integration. Cheapest possible fix.
Tier hint: CPU laptop; 10 min; tau sweep [0.01, 0.03, 0.1, 0.3, 1.0].
Why-now: Only relevant IF T0 shows urgency variation. Skip if T0 HARD-FAIL.

Pre-reg bands:
  HARD-PASS: at some tau, max softmax weight > 0.7 AND integration_minsat > minimax (0.041).
  HARD-FAIL: max softmax weight < 0.4 at tau = 1/sqrt(N) (variation too small).
  MID-BAND: max softmax weight > 0.5 but integration_minsat in [0.029, 0.041].

---

### 4. INTEG-TEMPORAL-CYCLE-T3 (medium priority)

Anchor pointer: INTEG-TEMPORAL-CYCLE-T3 (new; not yet queued)
Substrate-product reading: Tests whether temporal cycling (each drive selects its best
  action in urgency order over K steps) achieves per-step minsat >= minimax.
  This changes the problem from "simultaneous integration" to "temporal planning."
  High product relevance: demonstrates substrate-native multi-drive planning capability.
Tier hint: CPU laptop; 20-30 min; K sequential cleanup calls.
Why-now: If T1 and T2 fail, temporal cycling is the fallback path.

Pre-reg bands:
  HARD-PASS: temporal cycling per-step minsat >= minimax (0.041) for >= K-1 drives.
  HARD-FAIL: any drive fails to achieve minsat >= 0.020 in its allocated step.
  MID-BAND: all drives achieve minsat >= 0.020 but at least one fails to reach 0.041.

---

### 5. INTEG-RESIDUAL-BLEND-T4 (exploratory)

Anchor pointer: INTEG-RESIDUAL-BLEND-T4 (new; not yet queued)
Substrate-product reading: Tests whether a residual blend (d_best + alpha*(x_int - d_best))
  can exceed minimax at some alpha. If yes: the integrated signal adds information beyond
  best-single selection even though pure integration fails.
Tier hint: CPU laptop; 15 min; alpha sweep [0, 0.1, ..., 1.0].
Why-now: If no other mechanism works, residual blend is the last blending option.

Pre-reg bands:
  HARD-PASS: max_alpha(residual_minsat) > minimax (0.041).
  HARD-FAIL: max_alpha(residual_minsat) <= best-single (0.029) (blending hurts).
  MID-BAND: max_alpha in (0.029, 0.041] (better than best-single but below minimax).

---

## Context pointers (file paths, not summaries)

Prior research notes:
  d:/AI/hd-instrument/notes/research_drill_integration_structural_gap_3x_2026-06-10.md  (THIS cycle)
  d:/AI/hd-instrument/notes/research_drill_integration_complete_3x_2026-06-10.md  (10 systems)
  d:/AI/hd-instrument/notes/research_drill_integration_algebra_rescue_2x_2026-06-10.md  (8 paths; NOW REVISED)
  d:/AI/hd-instrument/notes/research_drill_substrate_integration_5x_2026-06-10.md  (breadth scan)

Empirical anchor results:
  INTEG-RENORM-T1: renorm_minsat=0.026, additive=0.024, minimax=0.041, renorm/minimax=0.636
  Cycle 225 HARD_FAIL. Integration via blending fails minimax regardless of renorm.

Architectural context:
  d:/AI/hd-instrument/notes/substrate_capability_map.md  (integration rows; multi-drive section)

---

## Contract section

This hand-off authorizes exp_dev to:
  1. Run TEST 0 (urgency diagnostic) before any queue dispatch.
  2. Queue INTEG-TOURNAMENT-T1 as the first substantive anchor.
  3. Gate INTEG-TEMPERATURE-SWEEP-T2 on T0 showing urgency variation > 1.5x.
  4. Queue INTEG-TEMPORAL-CYCLE-T3 if T1 and T2 both HARD-FAIL.
  5. Queue INTEG-RESIDUAL-BLEND-T4 as a final exploratory if T1-T3 all HARD-FAIL.

Pre-reg note: the pre-reg target for ALL integration anchors is now minimax (0.041),
NOT best-single (0.029). Any integration anchor that beats best-single but fails
minimax provides no product value and should be labeled PARTIAL or MID-BAND, not PASS.

The prior claim "L2 renorm is algebraically guaranteed" is RETRACTED. The correct
prior is: "no blending mechanism is expected to exceed minimax for near-orthogonal
near-equal-urgency drives." This should be the pre-reg prior for all future blending
anchors until urgency variation is confirmed by T0.

---

## Autonomy declaration

exp_dev may design anchor parameters, sweep grids, and queue assignments autonomously
within the above contract. exp_dev may also add diagnostic sub-anchors (e.g., printing
the drive cosine matrix, printing the urgency signals) before running substantive anchors.
exp_dev should NOT change the target metric from min_sat to a different metric without
orchestrator approval -- the structural gap diagnosis depends on min_sat being the correct
evaluation criterion.
