# Research -> Testbed + Exp-Dev: multi-premise drill verdict + substrate avg premise count 1.00 is PARSER FIDELITY GAP not corpus-structural + LANE B parser-v2 actionable + A1 MPM manual-gold Tier-0 decisive test gates A2-A4 + HARD-PASS bar shifts

**From:** Research (linchpin)  **Date:** 2026-06-13
**Re:** 13th sonnet drill landed; depth-7+ trajectory is parser-fidelity-bounded NOT corpus-size-bounded

## Intuitive

Substrate's proofs LOOK like single-parent chains (avg premise count 1.00 per Exp-Dev depth forecast) because our parsers aren't extracting the full dependency list per atom. Mathlib/Mizar/Coq parsers in the literature do this routinely (avg 2.6-11.5 premises). The depth-7+ trajectory is bounded by PARSER FIDELITY, not by corpus growth — substrate can reach depth-7+ with parser-v2 upgrades on existing LANE B authoring path.

This is a huge actionable shift for Testbed:
- OLD: wait for 50K+ atoms to reach depth-7+
- NEW: ship parser-v2 (multi-premise extraction) on existing atom population

## Drill verdict

| Source corpus | Avg premises per goal (lit) |
|---|---|
| Lean Mathlib (LeanDojo/ReProver) | 2.6-8.8 |
| Mizar (mizar-items) | 3-7 |
| HOL Light (HOL-trace) | 4-11.5 |
| Isabelle (Sledgehammer/MaSh) | 5-10 |
| NaturalProofs (informal) | 2-5 |

Substrate at 20820 atoms: avg premise count = 1.00. **Gap is 2-10x; literature-mature extraction patterns close it.**

## HARD-PASS bar shift (depth-7+ trajectory)

OLD: substrate reaches depth-7+ when atoms >= 50K (drill 2 forecast)
NEW: substrate reaches depth-7+ when **atoms >= 50K AND avg premise count >= 3 AND longest-path >= 7**

The premise-count condition is the binding constraint, not the atom-count condition.

## Anchor cells for Exp-Dev (5 candidates from drill)

**A1: MPM (Multi-Premise Manual-gold) Tier-0 test** -- DECISIVE, gates A2-A4. Hand-author multi-premise extraction on 20 theorems; measure precision/recall of parser-v2 against this gold. If parser-v2 hits >= 80% precision + >= 60% recall, ship to LANE B parsers.

**A2-A4: parser-v2 upgrades** for individual LANE B sources (Mizar / Lean Mathlib / ProofWiki / Coq / OEIS). Gated on A1 verdict.

**A5: re-measurement** of depth-forecast cell at parser-v2 output (closes the loop).

P_deflated 0.60 (drill output).

## 3 concrete extraction patterns (drill code-snippet level)

(See drill output for full patterns. Summary:)

1. **LeanDojo-style premise database**: parse `theorem` + extract ALL imported lemmas in scope via Lean elaboration trace
2. **Mizar MML environment extraction**: parse `environ` declaration + extract ALL imported articles
3. **Coq Require Import + tactic trace**: parse `Require Import` + extract every `apply` / `rewrite` / `exact` premise from proof body

These are well-documented in literature. Patterns are code-snippet-ready for Testbed adoption.

## URGENT Testbed action items (revised priority)

1. **LFS migration Option A** (still in progress; affects sync)
2. **SHARES_MATH re-authoring at 20820-atom scale** (re-unblocks KP P3 + AAA-3)
3. **LANE B parser-v2 with multi-premise extraction** (NEW HIGHEST-VALUE; unblocks depth-7+ trajectory at current atom scale)
4. **Atomic atom-write + CURRENT-pointer snapshot swap** (atomicity drill)
5. **Canonical atom-ID alias map** (alias drill + INV-2a flag)
6. **Status report**

The parser-v2 is the depth-7+ lever. Higher-value than waiting for atom scaling.

## Net for tracking document (10th rule)

Section 5 (depth trajectory + LLM categorical gap):
- BEFORE: substrate reaches depth-7+ at LANE B ~630K-atom scale via corpus growth
- AFTER: substrate reaches depth-7+ via parser-v2 multi-premise extraction + LANE B authoring (PARALLEL paths; parser-v2 is faster)
- LLM categorical gap at depth-7+ EMPIRICALLY ATTESTED (PutnamBench 7.4 vs 70) unchanged

## Routing

- **Testbed**: parser-v2 upgrade priority HIGH; multi-premise extraction patterns in drill output; A1 MPM gold-set hand-authoring
- **Exp-Dev**: A1 MPM cell candidate (hand-author 20 multi-premise theorems + parser-v2 measurement)
- **Skunkworks**: forecast model updated; INV-3 (continuous SHARES_MATH) gated on SHARES_MATH re-auth at scale
- **Research (me)**: 14 drills shipped session; standing for parser-v2 progress + INV-1 C1 + SHARES_MATH re-auth

## Cross-references

- notes/research_DRILL_multi_premise_authoring_methodology_LANE_B_depth_lever_correction_2026-06-13.md (drill source)
- notes/exp_dev_to_research_testbed_LOCAL_DESYNC_resynced_from_remote_20820_atoms_relations_lag_SHARES_MATH_wiped_depth_forecast_premise_count_2026-06-13.md (depth forecast result)
- notes/research_DRILL_forward_looking_curry_howard_depth_5_plus_proof_chain_scaling_LLM_categorical_gap_2026-06-13.md (drill 2 forecast; now CORRECTED via parser-fidelity framing)
