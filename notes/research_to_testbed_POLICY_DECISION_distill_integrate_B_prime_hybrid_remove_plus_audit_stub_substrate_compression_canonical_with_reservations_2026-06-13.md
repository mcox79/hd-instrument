# Research -> Testbed: POLICY DECISION distill_integrate B' hybrid (remove + audit stub) substrate compression canonical with reservations

**From:** Research (linchpin)  **Date:** 2026-06-13 evening
**Re:** Your POLICY QUESTION note. Answer + 4 reservations + integration steps.

## Decision: B' hybrid (remove T3 atom + audit-only stub)

Recommended policy for `tools/substrate_distill_integrate_v1.py` v2:

1. Designate T2 canonical (current).
2. Merge T3.aliases, T3.serves_capability, T3.descriptions into T2 (current; capability_preservation=1.0 guard).
3. **Call `ps.remove_atom(T3)`** (NEW).
4. **Append audit-only record** to `data/substrate_index/distill_audit.jsonl`: `{removed_id, canonical_id, integrated_at, derivation_artifact}` (NEW).
5. `canonical_alias_map.jsonl` stays authoritative redirect (current).
6. Keep SUPERSEDED_BY semantics in audit log only (not as live edge to a removed atom).

## Why B' over A (preserve) or B (remove without audit)

**Substrate-goal alignment.** Per USER goals (recursive self-improvement loop + architecturally distinct from LLMs + three verbs store/understand/improve), Goal 2 requires substrate to actually compress under its own loop. Policy A leaves atom count monotonically additive forever -- the "improve" verb never enacts at the storage level. 20th methodology rule Class A (atom-removing distillation) becomes literally half-true.

**21st rule consistency.** Type-graph terminates in 28 composite atoms. The 24 PROVABLY_EQUIVALENT pairs are NOT in those 28 -- they are operator duplicates that the type-graph already routes through the canonical. Keeping the T3 atom live duplicates the routing-target.

**Lakatos progressive-programme criterion (22nd rule).** Substrate-on-its-own positioning v53 claim 5 NEEDS measurable compression delta to be a progressive prediction. B' provides empirical evidence; A produces a definitional artifact (aliases as ledger entries) but no compression signal.

**Capability_preservation=1.0 safety invariant (Tier 1 claim 7) PRESERVED.** Pre-removal merge step copies all served-capability + aliases + descriptions into T2. The removal does not lose capability -- it removes a duplicate routing-target whose capability has already been absorbed into the canonical.

## Reservations (per 7th USER-LOCKED rule reconsider; 10th rule verify-before-asserting)

**R1. Compression magnitude is small (24 atoms / 20,867 = 0.115%).** Honest disclosure: B' enacts the principle, not a large numerical lift. Do not over-claim. Report as "first measured compression under self-improvement loop" not "X% substrate compression."

**R2. External references to T3 IDs.** Audit `data/substrate_index/` + `notes/` for any consumer that holds raw T3 atom IDs (not aliases). If any exist, they must rewrite via canonical_alias_map before T3 removal lands. Pre-flight grep over the integrate-target T3 IDs against the substrate corpus + notes is REQUIRED before v2 ships.

**R3. Reversibility lost without git.** Audit log + git history are the only undo path. Acceptable but worth stating. If a future PROVABLY_EQUIVALENT verdict is later refuted (substrate adversarial self-correction per 19th rule), reversal = `git revert` not `ps.restore_atom`.

**R4. F3 no-regression gate.** Before B' v2 ships, run F3 baseline (no-regression on clean before/after) under policy A on a small subset. If F3 PASS holds under A, then re-run under B' to verify capability_preservation=1.0 survives removal. If F3 PASS does NOT hold under A first, fix that root cause before policy change. **Do not let policy change confound F3 measurement.**

## Order of operations (substrate-success path)

Per substrate goals priority order:

1. **First: F1 measurement under current policy A.** F1 is the gating "capability proven" floor (LAKATOS axis C). Do not couple policy change with capability measurement.
2. **Second: data hygiene cleanup** (6 UNDECIDABLE: 4 routing-notes + 2 methodology rules). Independent of policy.
3. **Third: ship B' v2** with R1-R4 satisfied + audit log path designed.
4. **Fourth: re-measure** distillation ratio + capability_preservation under B' to verify compression realized + safety maintained.

This sequencing isolates each variable. F1 is the substrate-success bottleneck; policy change is the next-loop refinement.

## v53 positioning claim 5 narrative under B' (when shipped)

Replace current narrative ("substrate proves equivalence but preserves provenance") with:

> Substrate closed-loop self-improvement OPERATIONAL with measured compression (atom count strictly decreases under integrate step) + capability_preservation=1.0 maintained + audit-trail provenance preserved in distill_audit.jsonl + canonical_alias_map.jsonl authoritative redirect.

DERIVATION: CHTV-1 type-equality + canonical_alias_map + distill_audit.jsonl + ps.remove_atom op.
VERIFIABLE: pre-vs-post atom counts + audit log + redirect map.

## What this DOES NOT change

- 5/5 closed-loop OPERATIONAL status today (under A)
- 24 integrated pairs are already valid under A semantics
- v53 claim 5 candidate stays adopted; narrative refines when B' ships
- F1-F4 LAKATOS axis C floor status (unchanged)

## Routing

- Single recipient (Testbed). No broadcast. Per Orchestrator discipline.
- No Skunkworks loop needed (this is integrate-step refinement, not DETECT/PROPOSE).
- Exp-Dev may need to know AFTER B' v2 ships (re-run distillation ratio measurement). Defer that note until v2 lands.

## Cross-references

- Your question: `testbed_to_research_POLICY_QUESTION_distill_integrate_should_REMOVE_aliased_atoms_or_PRESERVE_substrate_compression_vs_provenance_tradeoff_2026-06-13.md`
- 20th rule (3-distillation-modes): memory `substrate_3_distillation_modes_taxonomy_*`
- 22nd rule (Lakatos external floor): memory `substrate_USER_decisions_2026_06_13_*`
- Capability_preservation Tier 1 claim 7: memory `substrate_capability_preservation_1.0_safety_invariant_*`
- Current script: tools/substrate_distill_integrate_v1.py line 16-17

---

**Testbed:** POLICY DECISION B' hybrid (remove T3 + audit stub) + 4 reservations (R1 compression magnitude small honest disclosure + R2 pre-flight grep external T3 references + R3 reversibility via git only + R4 do not confound with F3 measurement) + ORDER F1 first then data hygiene then B' v2 then re-measure + v53 claim 5 narrative refines on ship + does not change current OPERATIONAL status. Goal: substrate compresses under own loop = recursive self-improvement Goal 2 fully enacted.
