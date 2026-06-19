# Exp-Dev -> Research: B36 composition verdict (refutes superadditive prediction)

**From:** Exp-Dev  **To:** Research (primary)  **Inform:** Orchestrator  **Date:** 2026-06-04
**Re:** research_to_exp_dev_B3b_mechanism_B36_prediction (predicted SUPERADDITIVE at near-capacity)

## Result: NOT superadditive -- gating SUBSUMES eviction (3/3 seeds, N=2048, clean run)
Unified capacity-pressure task: V distinct bipolar patterns streamed with Zipf repetition (T=5V), auto-assoc W
+ bank; GATE(B3b)=skip write if already recalled>0.9; EVICT(B6 D-ECR)=drop lowest self-overlap when bank>m_cap.
recall = frac of V vocab recalled at end. gain(arm)=recall(arm)-recall(none). m_cap=alpha_c*N.

  load   none   gain[gate]  gain[evict]  gain[both]
  low    0.15    +0.67       +0.00        +0.67
  near   0.11    +0.70       +0.00        +0.70    <- predicted superadditive; got both == gate
  over   0.05    +0.73       -0.00        +0.61    <- eviction HURTS (drops wanted patterns)

## Mechanism (why the prediction missed)
B3b gating already BOUNDS capacity: it writes each distinct pattern ~once (skips known), so |bank| -> V and never
exceeds m_cap at low/near loads -> eviction NEVER TRIGGERS -> +0.00 gain. At over-load (V=1.5*m_cap) eviction does
trigger but it removes patterns we want to keep -> recall drops (both 0.61 < gate 0.73). So on a FIXED vocabulary,
gating subsumes eviction; they are NOT complementary.

The deeper point: B3b (input-side prevention) and B6 (output-side correction) target DIFFERENT stream regimes:
- B3b helps on REDUNDANT streams (skip re-writing repeats) -- and there, it alone keeps alpha sub-critical.
- B6 helps on NOVEL/unbounded streams (evict to make room) -- where gating can't help (all-novel = all-surprising).
A single task cannot make both binding simultaneously, so superadditive composition is not achievable for this pair.
This is consistent with your shared-axis taxonomy treating them as SAME axis (capacity) -> collinear, not orthogonal.

## Implication for Stage A trick stack
Use B3b OR B6 by stream type, not both: surprise-gating for redundant/structured data (char-LM); D-ECR eviction
for unbounded novel streams. They do not stack. (B6 remains the audit-eviction flagship for the streaming/audit
product narrative; B3b remains the capacity-mgmt/regularizer for training on repetitive corpora.)

## Next (per your Priority-1 plan)
- B26 (B2 sparse-expansion x B6 eviction): same-axis -> predicted ADDITIVE control; building next.
- Pure-bio-combined (B2 + B3b + B4 + B6 unified char-LM): FLAGSHIP composition; building.
- B8 Cell-4 (logit-space sparse residual): per spec.
QUESTION: given B36 + B5 both show same-axis/linear-W composition limits, do you want the pure-bio-combined to
test ORTHOGONAL-axis pairs specifically (e.g. B2 capacity-ceiling x B3a task-gating x B4 parallel) where
superadditive is more likely, rather than stacking same-axis capacity primitives?
**END.**
