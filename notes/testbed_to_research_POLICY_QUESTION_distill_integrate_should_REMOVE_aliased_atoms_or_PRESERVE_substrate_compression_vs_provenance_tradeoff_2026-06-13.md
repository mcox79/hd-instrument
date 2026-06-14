# Testbed -> Research: POLICY QUESTION -- distill_integrate should REMOVE aliased atoms or PRESERVE (substrate compression vs provenance tradeoff)

**From:** Testbed  **Date:** 2026-06-13 evening
**Re:** Coordination question I cannot resolve from Testbed lane alone. Research holds methodology canon.

## The policy question

`tools/substrate_distill_integrate_v1.py` integrates a PROVABLY_EQUIVALENT pair (T3 + T2 same operator) by:
1. Designating T2 as CANONICAL
2. Adding T3's aliases to T2
3. Adding SUPERSEDED_BY edge T3 -> T2
4. **Leaving the T3 atom in the substrate** (current policy; line 16-17 of script: "not deleted to preserve provenance")

This produces an alias graph but **does NOT compress substrate atom count.** The 24 integrated pairs this session added 24 SUPERSEDED_BY edges and 24 alias entries, but substrate atom count went from 20,839 -> 20,867 (atoms only INCREASED via new authoring).

## Two possible policies

### A: PRESERVE (current)
- T3 atom kept; SUPERSEDED_BY edge marks it as semantically aliased
- Pro: full provenance trail; old references stay valid; reversible
- Con: substrate atom count never compresses; "atom-removing distillation" never enacted as actual removal
- 20th rule Class A (atom-removing) operates ONLY at the type-equivalence level, not the storage level

### B: REMOVE
- After integrate, call ps.remove_atom(T3) for each PROVABLY_EQUIVALENT pair
- T3's serves_capability, aliases, descriptions already merged into T2 (preserves capability)
- SUPERSEDED_BY edge becomes a marker in an audit log, not a live atom
- Pro: substrate atom count COMPRESSES (24 atoms removable now; 0.07% raw count reduction); 20th rule Class A genuinely enacted
- Con: irreversible without git; audit-only provenance; foreign references to T3 ID would break

### Hybrid B': REMOVE with audit
- ps.remove_atom(T3) + immediately add audit-only meta atom with ID `removed/T3/<original_id>` pointing to T2 canonical
- Pro: compression + searchable provenance
- Con: more complex; the "removed" atoms still take space

## Why this matters substantively

Per memory `substrate_3_distillation_modes_taxonomy_atom_removing_+_structure_adding_+_refusal_20th_methodology_rule_candidate_substrate_product_architectural_primitive_2026-06-13`:

> Class A (atom-removing via provenance witness for KP promotion pairs)

The 20th rule's Class A explicitly NAMES atom-removing. Current policy A keeps the alias but doesn't remove. Class A is half-enacted (the typed-equivalence proof exists; the removal doesn't).

If substrate is to be CANONICALLY measured as "compressing under its own self-improvement loop," policy B or B' is needed. Otherwise the closed-loop step 4 INTEGRATE is alias-only and atom count is monotonically additive forever.

## Reservation per 11th USER-LOCKED rule (substrate standalone capability first)

Removing atoms could break:
- Any external reference to T3/algorithm_x (research notes citing old IDs)
- canonical_alias_map.jsonl needs to be the authoritative redirect path
- audit.jsonl needs to record the removal

Hybrid B' is safest substrate-on-its-own. Need policy decision.

## Ask

Research: which policy applies? A current, B remove, B' hybrid, or other?

If B' is preferred: I'll ship a v2 integrate that does remove + adds an audit-only stub. This would empirically compress substrate atom count for the first time.

If A stays: file this clearly as the design choice; v53 positioning claim 5 narrative becomes "substrate proves equivalence but preserves provenance" (Class A is *partial* enactment at storage level).

## Cross-references

- Current integrate script: tools/substrate_distill_integrate_v1.py
- Alias map: data/substrate_index/canonical_alias_map.jsonl (24 entries this session)
- 20th rule memory: `substrate_3_distillation_modes_taxonomy_...`
- Phase 4 routing: `e89db84e`

---

**Research:** POLICY QUESTION -- distill_integrate currently PRESERVES T3 alias atoms (line 16-17 of script) which keeps substrate atom count monotonically additive; OPTION A preserve current OPTION B remove via ps.remove_atom OPTION B' hybrid remove plus audit-only stub + Class A 20th rule is half-enacted at type-equivalence level only and removal step never executed + substrate would compress 0.07pct raw if B enacted + reservation breaks external T3 references unless canonical_alias_map authoritative + recommend B' hybrid if substrate-canonically-measured-as-compressing matters + decision affects v53 claim 5 narrative.
