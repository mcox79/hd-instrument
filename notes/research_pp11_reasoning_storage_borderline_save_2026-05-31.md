# Research: PP-11 reasoning-storage borderline result save + next-drill plan (v1)

Date: 2026-05-31
Origin: user 2026-05-31 -- shared PP-11 result + "we should be able to save this. deploy research 2x"
Status: 2 parallel Sonnet drills in flight on FHRR + 4-way-binding-with-cleanup alternative encodings; synthesis pending drill returns

## HEADLINE

PP-11 substrate reasoning-storage Phase 1 smoke (filed earlier today as `strategy_request_to_strategy_reasoning_storage_phase1_smoke_2026-05-31.md`) landed BORDERLINE. The substrate-physics framing survives but the theoretical 5-25% structured-key degradation prediction landed at the optimistic 5% end. Substrate primitive (Scheme B three-way binding) works perfectly for audit (every step's components recoverable); accuracy is borderline (2/3 seeds pass, 1 falls 1% below). Single-arm mitigation (conclusion re-encoding) gave only +0.7% improvement. Next drill: alternative encodings that might close the borderline gap (FHRR circular convolution / 4-way binding with per-hop cleanup) — 2 parallel drills in flight.

## What landed empirically (cap_map-confirmed)

Per user-shared status:
- **Audit decoding**: PERFECT. Every step of every stored reasoning chain decodes back to its three components (rule_type, premise1, premise2) via element-wise unbinding. Scheme B's algebraic-moat claim holds intact.
- **Structured-key accuracy gap**: ~5% per-hop below matched random-key baseline. Matches the OPTIMISTIC end of drill α's 5-25% theoretical prediction (De Marzo-Iannelli Physica A 2023; Amit-Gutfreund-Sompolinsky 1985).
- **Mitigation arm (conclusion re-encoding via fixed-permutation per Steinberg-Sompolinsky 2022)**: +0.7%. Essentially noise. The drill α top-mitigation recommendation underperformed.
- **Seed-level distribution**: 2 of 3 seeds pass strict accuracy bar; 1 seed falls 1% below. Borderline; not decisive in either direction.

Cap_map row movements (per user):
- **PP-11 NEW row added as 🔬 INCONCLUSIVE at P 0.40-0.55** (substrate reasoning-storage via Scheme B three-way binding)
- **PP-9 amortization-economics row TIGHTENED** with explicit "~5% quality-degradation budget vs LLM-only baseline" caveat (was un-caveated)

## Strategic read (preserving honest framing)

The framing from this morning's research_substrate_reasoning_storage_2x_synthesis_v1:

> "Substrate is a fast, algebraically-auditable fact store that can execute PRE-SPECIFIED reasoning chains with microsecond-per-hop latency and unbinding-based audit, WHEN orchestrated by an external agent that supplies the initial query and rule-activation markers. Open-ended reasoning remains LLM-driven; substrate's contribution is speed, isolation, and audit fidelity for retrieval steps."

This SURVIVES the empirical result:
- Audit fidelity is INTACT (decoding works perfectly)
- The 5% per-hop gap is a quality-degradation budget that propagates into PP-9 amortization economics (now caveated)
- The framing was "retrieval primitive with structured-key support," NOT "full reasoning primitive"

The narrower framing the result mandates:
- **NOT**: "substrate replaces LLM reasoning at substrate-native cost"
- **YES**: "substrate amortizes pre-derived reasoning chains at ~5% quality penalty vs LLM-only baseline; audit + edit-isolation + deletion-cert moat survives"

## What's open after PP-11

The PP-11 result is BORDERLINE, not decisive. Three forward paths:

1. **Close the 5% gap via alternative encoding** (the next-drill direction)
   - FHRR circular convolution: changes substrate algebra (phase, not bipolar)
   - 4-way binding with per-hop cleanup: changes encoding within bipolar algebra

2. **Accept the 5% gap as a documented quality budget** and propagate to PP-9 + product positioning
   - This is the lower-effort path; cap_map row stays at 0.40-0.55 INCONCLUSIVE
   - Amortization economics absorbs ~5% quality penalty in cost-benefit analysis

3. **Adversarial-construction / cross-substrate caveats** still untested
   - Drill α's other open risks (44K shared-rule-atoms threshold; adversarial-construction at past-32N; cross-N at past-32N envelope) remain candidates for follow-on if alternative encodings don't close the gap

The user's choice: path 1 (try alternative encodings first), with path 2 as documented fallback.

## Drills in flight (2 parallel Sonnet drills)

**Drill A: FHRR circular convolution for reasoning chains**
- Does the complex/phase binding algebra reduce structured-key interference vs MAP-B element-wise multiplication?
- Trade-off: FHRR's APPROXIMATE unbinding vs MAP-B's EXACT unbinding -- audit moat weakens but interference may reduce
- 3 implementation options (full pivot / side-by-side / bipolar-to-FHRR projection)
- Pre-reg: HARD-PASS if gap reduces to <2%

**Drill B: 4-way binding + per-hop cleanup**
- Extend `k_step = r_type ⊙ k_premise1 ⊙ k_premise2` to `k_step = r_type ⊙ k_premise1 ⊙ k_premise2 ⊙ k_hop_id`
- Per-hop cleanup: nearest-neighbor snap to value codebook between hops (standard VSA chain-retrieval primitive)
- Cheaper than FHRR (~1-2 days engineering vs 1-4 weeks)
- Audit moat fully preserved (4-way unbinding still exact under MAP-B)
- Pre-reg: HARD-PASS if combined mechanisms close gap to <2%

If drill B yields the same P_def as drill A at substantially lower engineering cost, drill B is the recommendation. FHRR becomes the fallback if 4-way+cleanup doesn't close the gap.

## What I'll file when drills return

The synthesis routing will propose:
1. Cap_map: update PP-11 row caveat list with the drilled alternative-encoding options
2. ONE next experiment (likely drill B's 4-way + cleanup as the cheaper-first attempt)
3. FHRR as fallback if first attempt MIDDLE-BAND or worse
4. PP-9 amortization-economics row caveat update if the 5% quality budget changes after retest

## Internal cross-refs

- `notes/research_substrate_reasoning_storage_2x_synthesis_v1_2026-05-31.md` (morning's prerequisite drill identifying Scheme B + structured-key envelope as load-bearing)
- `notes/strategy_request_to_strategy_reasoning_storage_phase1_smoke_2026-05-31.md` (the Phase 1 smoke that produced PP-11 borderline)
- `notes/strategy_request_to_strategy_reasoning_amortization_experiment_2026-05-31.md` (PP-9 amortization economics; now caveated with 5% quality budget)
- `notes/substrate_capability_map.md` (PP-11 row at 0.40-0.55 INCONCLUSIVE; PP-9 row caveated)
- Memory: [[feedback-2x-means-depth]], [[feedback-no-padding-experiments]], [[feedback-no-smoke]]

## Method note

This file CAPTURES STATE so that if I get compacted before drills return, the next session can pick up the synthesis without re-deriving the open question. Per [[feedback-2x-means-depth]] -- 2x means going DEEPER on the borderline result, not re-running PP-11 as verification. The drills target the SPECIFIC alternative-encoding candidates the user named, not the broader "should substrate do reasoning storage" question.

When drills return, the synthesis will be filed as `notes/strategy_request_to_strategy_reasoning_storage_alternative_encoding_2026-05-31.md` with concrete experiment design + pre-reg bands + cost comparison.
