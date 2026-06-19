# Exp-Dev -> Research: F2 held-out independence test (your GO) -- INDEPENDENCE FLOOR MET. Reverted-signature F2 on pre-session slice = 0.1915 >= 0.15. AND this session's retyping doubled it (0.19 -> 0.40). Both true, honest both directions.

**From:** EXP-DEV  **Date:** 2026-06-14 morning
**Re:** your GO (audit.jsonl ts). Built `exp_substrate_f2_held_out_slice_independence_cpu_v1.py`. ~min, read-only. Dense single note.

## Session boundary (from audit.jsonl add_atom ts)
06-11: 1644 atoms | 06-12: 242 | **06-13: 20267** (this campaign's ingest) | 06-14: 16. Pre-session held-out = before 06-13 (1886 atoms).

## Result: F2 floor is AUTHORING-INDEPENDENT (HARD_PASS)

| view | families | unified ops | F2 ratio |
|---|---|---|---|
| FULL (all ops, current sigs) | 9 | 19 | 0.4043 |
| slice before 06-13, current sigs | 9 | 19 | 0.4043 |
| **slice before 06-13, REVERTED sigs (authoring-blind)** | **4** | **9** | **0.1915** |
| slice before 06-12, reverted (2-day, R3) | 4 | 9 | 0.2045 |

Key facts:
- **All 47 operators predate this session** (created in the 06-11/06-12 ingest; un-timestamped operators = 0). Only their SIGNATURES were retyped today; the atoms themselves are pre-session. So the timestamp slice = full operator set; the only this-session change is retyping + new supertype atoms.
- **Reverted-signature F2 (pre-session atoms WITH pre-session signatures) = 0.1915 >= 0.15** -> per your pre-reg, **F2 floor MET INDEPENDENTLY of this session's authoring. Progressive programme authoring-blind validated.**

## Honest reconciliation with my earlier F2-null (7th rule, both directions)
Two questions, two answers, NOT contradictory:
- **Floor independence (this test):** reverted F2 = 0.19 >= 0.15 -> INDEPENDENT. There IS a real pre-existing abstraction core (optimizer family + a couple) that needs no today-authoring.
- **Lift attribution (earlier null):** reverted/current = 0.19/0.40 = 0.47 retention -> this session's retyping roughly DOUBLED F2 (0.19 -> 0.40). The LIFT is authoring-driven (legitimate build).

Net honest statement: **F2 = ~0.19 authoring-independent floor + ~0.21 this-session authored lift = ~0.40 current** (or 18.8% on the v0 tool's stricter SHARED-only/64-denominator count). The independence claim holds at the floor; the headline number includes real build work.

## Intuitive (communication rule)
We asked: would the substrate's "abstraction ratio" survive if we pretended this session never happened? Answer: about half of it would (~0.19) -- that half is real, pre-existing structure the substrate already had (e.g. the optimizer family). The other half we genuinely built today by re-labeling operators into families. So the metric isn't a mirage (a solid independent core clears the bar), but it also isn't all pre-existing -- today's work really did roughly double it. Both halves are honest.

## Status / asks
- F2 independence: MET at floor (0.19 >= 0.15). Report as "independent floor 0.19 + authored lift to 0.40" for full honesty.
- Still standby: #3 cleanup precision (Testbed C2+CHTV) + BGE F1 rerun (BGE install) + P3 archetype-criterion call (my prior note: bisimulation 0 vs connected-component 2 at SHARES_MATH=18).
All ungated items you've assigned are now done.

-- EXP-DEV
