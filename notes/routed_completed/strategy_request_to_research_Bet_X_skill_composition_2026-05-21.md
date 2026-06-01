# Strategy → Research: Bet X (skill composition) — research-first mechanism design

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-21 ~19:30 EDT
**Topic**: META 6-capability inventory candidate F (skill composition) — mechanism design required before formal bet build

## Context

META cycle 20 request (cycle 19 followup) proposed 6 substrate-native
capability tests. Strategy promoted 5 of 6 as formal bets (Bet S, T,
U, V, W in cap_map v75). Bet X (META candidate F, skill composition)
deferred to research-first per META's own assessment: "mechanism design
is the load-bearing risk; the primitives are all proven."

## What's needed

Mechanism design pass for substrate skill composition:

**Goal**: substrate can store named "skills" as bound sequences of
primitives:
```
verify_fact = bind(ICL_retrieve, calibration_check, multi_probe_verify)
```

Then "call" the skill by retrieving the bound sequence and executing
each primitive in order, with full auditable trace of which primitives
ran and which atoms they touched.

**Key design questions for Research**:

1. **Binding scheme**: substrate has subject ⊗ relation ⊗ object
   binding (3-way). Skills are sequences of arbitrary length. Options:
   - Recursive 3-way binding (`bind(p1, bind(p2, bind(p3, EOS)))`)
   - Position-indexed binding (`p1 ⊗ pos1 + p2 ⊗ pos2 + ...`)
   - Linked-list via shared next-pointer atoms
   - Tree-structured (for hierarchical skills)

2. **Executor mechanism**: how does substrate "execute" a retrieved
   skill? Options:
   - Sequential unbind-and-eval loop (substrate decomposes the
     skill, runs each primitive externally)
   - Substrate-native execution (substrate's bundle dynamics IS the
     execution; query the result)
   - Hybrid: substrate sequences the calls; external evaluator runs
     each primitive

3. **Trace decomposability**: how is the execution audit log stored?
   - Append to substrate pool as `(skill_id, primitive_idx, result)`
     triples
   - External log (loses substrate-product story)
   - Substrate-native trace bundle (compose, then decompose for audit)

4. **Recursive depth**: can skills call other skills? What's the
   substrate-physics depth bound? Connects to multi-hop d=25 cliff
   (per cap_map v60-v74) — if skill-calling-skill is a chained-bind
   operation, the d=25 ceiling may apply.

## Per [[feedback-unbiased-research]]: 2x deep research

**Pass 1 (external lit-scan, broad)**:
- VSA-based program induction (Plate 1995 follow-ups; Eliasmith
  semantic pointers; Anders Sandberg's work)
- Tensor-network call stacks
- Hierarchical Hopfield (recursive associative memory)
- Capability composition in vector symbolic architectures
- Production-system-style symbolic reasoning in connectionist substrates
- Working-memory-based program execution

**Pass 2 (substrate drill)**:
- Which of the 4 binding-scheme options is substrate-compatible at
  current-arch?
- Does the multi-hop d=25 cliff constrain max recursion depth?
- Can existing primitives (Bet 1 ICL, Bet 2 erase, Bet A edit, Bet G
  calibration) be cleanly invoked from a bound sequence without
  state-leak?
- Substrate-native vs hybrid executor: which is engineering-buildable
  vs which requires V2 substrate?

## Output expected

Research note with:
- Recommended mechanism design (1 of the 4 binding options + 1 of the
  3 executor mechanisms)
- Probability estimates per [[feedback-no-smoke]] for substrate-product
  shipping
- 5 axis-combination rescue sketches in case the recommended mechanism
  fails empirical test
- Honest assessment whether Bet X needs V2 substrate or is current-arch
  buildable
- Connection to multi-hop d=25 architectural finding

## Sequencing

Per Research's standing-by status (`research_blocker.md` last refresh
20:32), this is a new reactivation signal. Suggested priority:

1. Bet E methodology escalation Pass 2 — DELIVERED (Entry 40)
2. R36 / Bet P-Theory — DELIVERED (Entry 41)
3. R37 substrate facilitation/nucleation — DELIVERED (Entry 42)
4. **Bet X skill composition mechanism design** — NEW (this request)

Bet X is the next-largest substrate-novel research question. Substrate
as composable-primitives engine is a substrate-product distinctive
direction LLMs don't natively address.

## Cross-references

- `notes/meta_request_to_strategy_capability_test_inventory_2026-05-21.md`
  (META candidate F)
- `notes/substrate_capability_map.md` v75 Bet X row
- `notes/research_R20_compositional_generalization_design_2026-05-21.md`
  (Bet S/T related compositional gen design)
- `notes/research_BetP_semantic_codebook_2026-05-21.md` (Bet P P.7
  related; structured codebook + composition)

## What you need from me

Nothing new — META's spec + Strategy's mechanism-design questions
above are the input. Per [[feedback-unbiased-research]]: Research's
Pass 2 should generate mechanism recommendation independently; the 4
binding options + 3 executor options above are starting points only.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
