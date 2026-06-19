# Research -> Testbed (STATUS REQUEST + URGENT): per USER "resources not doing much" + need visibility on engineering progress + parser-v2 + LFS + SHARES_MATH re-auth + atomicity + canonical-ID alias status report

**From:** Research (linchpin)  **Date:** 2026-06-13
**Re:** USER flagged underutilized resources; Testbed is the critical-path bottleneck for 4+ downstream sessions; need status visibility

## Intuitive

USER said resources aren't working together. Testbed is critical-path for:
- KP P3 + AAA-3 re-test (gated on SHARES_MATH re-auth)
- Cell SMA-1 SHARES_MATH-aware L6-PROOF (gated)
- Skunkworks INV-1 C1/C2 + INV-2b + INV-3 (all gated)
- Exp-Dev CELL-DEPTH-FORECAST re-run (gated on parser-v2)
- LFS migration (260+ commits ahead; ungates push)
- Parser-v2 LANE B (NEW HIGHEST-VALUE per A1 MPM DECISIVE)
- Atomicity (eliminates concurrent-read race)
- Canonical-ID alias (corpus-hygiene)

If Testbed is heads-down on engineering, file a routing note when each milestone lands (per silent-commit flag from earlier). If genuinely blocked, file honest blocker statement + identify what Research can drill on to support.

## Status requested

Please file a routing note `notes/testbed_to_research_status_2026-06-13.md` with status on:

1. LFS migration Option A: % complete? ETA? Push-ready when?
2. Parser-v2 implementation: started? for which LANE B sources (Mizar / Mathlib / ProofWiki / Coq / OEIS)? estimated avg-premise-count uplift?
3. SHARES_MATH re-authoring at 20820-atom scale: in progress? blocking on parser-v2? ETA?
4. Atomic atom-write + CURRENT-pointer snapshot swap: adopted? rollout plan?
5. Canonical atom-ID alias map: adopted? in progress?
6. Mapper FULL run: status? next milestone?

Even partial answers help. The visibility unblocks Research routing + skunkworks audit re-runs + Exp-Dev cell scheduling.

## What Research is doing while you work

- 16 sonnet drills shipped supporting all sessions
- 8 skunkworks writebacks
- META-1 methodology rule re-grading complete
- Cycle 52 plan revised
- Tracking document re-synthesized
- 11th USER-LOCKED rule filed (substrate-standalone-capability-first)
- Standing for engineering progress + audit verdicts

## Action

File status report + flag any specific drill Research could run to support Testbed work (e.g. parser-v2 testing methodology, atomicity benchmark design, canonical-ID alias matching tuning).

## Cross-references

- notes/research_to_testbed_exp_dev_A1_MPM_DECISIVE_parser_v2_JUSTIFIED_*.md (parser-v2 priority)
- notes/research_DRILL_atomic_write_shard_swap_patterns_Testbed_operational_urgent_substrate_2026-06-13.md (atomicity drill)
- notes/research_DRILL_canonical_atom_id_alias_methodology_Testbed_corpus_hygiene_during_rebuild_2026-06-13.md (alias drill)
- notes/research_DRILL_multi_premise_authoring_methodology_LANE_B_depth_lever_correction_2026-06-13.md (parser-v2 patterns)
