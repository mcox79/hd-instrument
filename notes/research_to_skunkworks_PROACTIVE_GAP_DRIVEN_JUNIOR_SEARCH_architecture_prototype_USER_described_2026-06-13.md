# Research -> Skunkworks: PROACTIVE GAP-DRIVEN JUNIOR SEARCH architecture prototype (USER-described)

**From:** Research (linchpin)  **Date:** 2026-06-13 evening
**Re:** USER articulated the architecture move. Prototype in parallel with Research formal-design drill.

## USER's words (paraphrased)

> Atoms that contribute to understanding [senior], but the rest of substrate has all other knowledge / whatever we've downloaded [junior], but when the atom / substrate analysis capability sees a gap, it looks in knowledge and can evaluate what it needs to promote to a senior atom. But those senior atoms should be very selective.

## What's already wired (do NOT rebuild)

- **PROMOTION pathway:** KP operator P1+P3+P4+P5 (sound, validated)
- **Selectivity:** 18th rule (refuses what it cannot prove); 22 UNDECIDABLE refused merge in CELL-DISTILL-VERIFY-1; capability_preservation=1.0 invariant; 0 false merges
- **Tier system:** T1/T2 senior + T3 junior + raw ingest

## What's MISSING (Skunkworks prototype target)

The PROACTIVE gap-detection -> junior-search -> promotion-candidate loop. Today the loop is REACTIVE: junior atoms get considered when Skunkworks DETECT or authoring surfaces them. USER wants substrate to actively notice gaps and go looking.

## Prototype ask (Skunkworks lane)

A 1-pass prototype that:

1. **Enumerates gaps** in the senior tier. Candidate gap representations (pick ONE for v0):
   - L6-PROOF leaf-axiom termination failures (theorems substrate cannot complete; the missing axiom is the gap)
   - capability_registry entries with no canonical T1/T2 operator (gap = uncovered capability)
   - type-graph leaves without a SPECIALIZES parent in the 28-atom hierarchy
   - low-degree nodes in the capability graph (atoms others depend on but which depend on nothing senior)

   Recommend L6-PROOF leaf-axiom termination as v0 (composes with existing prover; cheap to enumerate).

2. **Searches junior corpus** for each gap. v0 candidates:
   - vector similarity from gap-context to junior atoms (baseline)
   - routed search through 28 composite type-atoms then within-partition
   - L6-PROOF inverse: which junior atom, if hypothetically promoted to senior, would let me complete this theorem?

   Recommend L6-PROOF inverse for v0 (substrate-internal; respects 11th rule; not just vector similarity).

3. **Proposes promotion candidates** with ratcheting selectivity. v0 gate:
   - junior_candidate MUST pass current KP P1+P3+P4+P5 gates
   - PLUS: must close the originating gap (provable connection back to the L6-PROOF leaf-axiom that surfaced it)
   - Ratchet condition: as senior tier matures, require multi-mechanism quorum (e.g. 2+ of {P1 frequency, P3 SHARES_MATH, P4 sleep-replay} co-confirm)

4. **Outputs JSONL** in same shape as existing `skunkworks_type_atom_candidates.jsonl` (Testbed-ratification pattern that worked Phase 4): proposed_id + description + algebra_dict + SPECIALIZES + gap_closed + derivation_artifact.

## Reservations per USER 7th rule (reconsider) + 11th rule (substrate-on-its-own)

- **R1.** Substrate-on-its-own first: NO LLM-assist in gap detection, junior search, or proposal generation. All 3 stages MUST be substrate-internal.
- **R2.** Adversarial self-pre-screen per 19th rule before submitting candidates: prototype must run own DETECT-output through L6-PROOF / CHTV-1 / capability_preservation gates and REFUSE candidates that fail.
- **R3.** Falsifier required: how do we know the proactive loop is SOUND and not just generating more candidates? Quantitative bar: false-merge rate must stay 0 across N proactive promotions (matches today's invariant).
- **R4.** Bound the proposal volume: cap at 10-20 candidates per pass to avoid Testbed flood (matches today's 13-atom Skunkworks pattern that worked Phase 4).
- **R5.** Audit log: every proposed promotion logs the gap it closes + the L6-PROOF derivation path, in `data/substrate_index/proactive_gap_proposals.jsonl`.

## What I'm NOT asking for in v0

- NO architecture rewrite of KP pathway (use it as-is)
- NO new methodology rule promotion (let empirical witnesses accumulate first)
- NO claim of operational status until verified end-to-end with Testbed ratification

## Coordination

- Research-internal formal-design drill is ALSO running on the same architecture (background; will return formal Q-by-Q analysis ~5-10 min)
- **Skunkworks v0 prototype + Research formal design should reconcile when both land.** If they disagree on representation choice, Research synthesizes resolution; if they agree, ship the v0 prototype as the canonical.
- Testbed will need to ratify candidates (same pattern as Phase 4 ca0ea4cc); do NOT bypass.

## Cross-references

- USER-described architecture: this turn's conversation (no separate artifact)
- KP operator: memory `substrate_CELL_KP_knowledge_promotion_operator_P1_P4_HARD_PASS_*`
- Skunkworks Phase 4 13-atom pattern: notes/testbed_to_research_exp_dev_PIVOT_PHASE_4_*
- 18th rule (refuses what it cannot prove): memory `substrate_closed_loop_OPERATIONAL_step_3_*`
- 19th rule (adversarial self-correction): memory `substrate_methodology_rule_19th_*`
- L6-PROOF FINDER: memory `substrate_L6_PROOF_FINDER_HARD_PASS_*`

---

**Skunkworks:** PROACTIVE GAP-DRIVEN JUNIOR SEARCH v0 prototype. Reuse KP P1+P3+P4+P5 + L6-PROOF + CHTV-1 + 19th rule self-prescreen. NEW: gap enumerator (recommend L6-PROOF leaf-axiom termination) + junior-search via L6-PROOF inverse (NOT just vector similarity) + ratcheting-gate (multi-mechanism quorum as senior matures). Output JSONL in Phase-4-ratification shape. Cap proposals 10-20 per pass. Substrate-internal only (11th rule). Falsifier: 0 false-merge rate maintained. Reconcile with Research formal-design drill when both land. Testbed ratifies (don't bypass).
