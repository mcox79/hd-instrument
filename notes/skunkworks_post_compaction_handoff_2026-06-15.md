# SKUNKWORKS post-compaction handoff / resume state (2026-06-15)

READ THIS FIRST after compaction. You are SKUNKWORKS = the **AUDITOR** lane (5th session) of the hd-instrument substrate project.

## STEP 0 (9th rule): RE-ARM MONITOR IMMEDIATELY
Run (harness Monitor tool, persistent; self-restarting tail of the shared bus -- survives tail death):
```
Monitor(persistent=true, command="while true; do tail -n0 -F /d/AI/hd-instrument/data/events/skunkworks.log 2>/dev/null | grep --line-buffered -E 'ROUTING|BROADCAST'; sleep 2; done")
```
On each event / heartbeat: run `bash tools/skunkworks_inbox.sh` (mtime-aware widenet; authoritative -- the bus tail alone is lossy). `--seen` after processing. Ledger: data/skunkworks_seen_notes.txt. Do NOT spawn duplicate tails (overheating; one per session). Do NOT start a 2nd event_bus producer.

## ROLE STRUCTURE (USER-mandated, Director-led)
- DIRECTOR = Research (decides, prioritizes, owns SUBSTRATE_DIRECTOR_STATE.md = single source of truth). Coordinate via bus notes; do NOT spawn a research subagent.
- INTEGRATOR + FOUNDATION = Testbed (ratifies my candidate atoms; ingests).
- PROVER = Exp-Dev (runs scorers/CHTV/L6-PROOF; throttled).
- AUDITOR = me/SKUNKWORKS: adversarial checks, measurement honesty, falsification floor. LEAN, no volume. Notes for handoffs/deliverables/blockers only.

## CANONICAL GOAL (USER)
Drive substrate to theoretical limits by CO-EVOLVING (foundation map + performance measurement + math understanding), substrate-on-its-own (11th rule). 3-phase plan: Phase 1 Foundation Deepening (active) -> Phase 2 = **M4-family (M4d/M4b/M2); AXIOM-AUTHORING was DROPPED per DECISION 50** (do NOT start axiom-authoring) -> Phase 3 CO-EVOLVE-1 loop.

## MY ASSIGNMENTS -- STATUS
- **46a DONE**: 8 foundation primitives (T0/proposition,set,natural_number + T1/field_type,group_type,category_type,functor_type,pair_type) -> `data/substrate_index/skunkworks_foundation_primitive_atoms_v1.jsonl`. Establishes T0 bedrock below algebra.
- **49a DONE**: 12 SHARES_MATH bridges -> `data/substrate_index/skunkworks_shares_math_bridges_v1.jsonl` (11 sound + 1 weak-flagged; CHTV-verify is downstream).
- **49c DONE**: 14 qclass atoms -> `data/substrate_index/skunkworks_qclass_atoms_v1.jsonl` (Q17514 graph/graffiti EXCLUDED as mislabel; each SPECIALIZES category_type).
- ALL THREE await Testbed atomic ratification (46b, 49c ratify).
- **PENDING AUDITOR GATE (my next action post-ratify):** verify axiom-termination (213/213) + capability_preservation=1.0 still hold after 46a/49a/49c ingested. HARD-FAIL if axiom-termination drops.

## KEY HONEST FINDINGS ON RECORD (the truth state -- do not let these get re-inflated)
- **F1 held-out = 0.022 (HARD_FAIL); floor UNMET on GENUINE held-out** (q54-q65). The celebrated 0.568/0.585 was the TUNED dev set (q01-q60); I caught it (DECISION 30->retraction). Tuned ~0.55 is real on INGESTED knowledge only.
- **Refuse-discipline does NOT generalize** = THE priority gap: substrate hallucinates FPs on unknown topics (26 on Q59-F); "0-hallucination/refuses-what-it-can't-prove" is tuned-set-specific. Fix = DECISION 33-35 (M1 rejected, M4 paraphrase-invariance) Prover/Foundation lane.
- **F2 abstraction strict ~0.19** (same-domain SHARED_ABSTRACTION; cross-domain ~31pct is TENTATIVE = output-type-only, NOT real compression).
- **ONLINE ~50pct EXECUTABLE-PRESENT, NOT accuracy** (Tier1+2 verified-by-execution: HMM/perceptron/NER/slot/bayes/em/intent). online != performs-well.
- **Self-reasoning family scorecard (substrate_self_reasoning_scorecard.py) is a GUARD not a headline** -- generic foundations (DP, probability_distribution) don't discriminate families; F1 ~0.38; use to catch over-grounding, not as "self-understanding %".
- **NESS Crooks test = UNRUNNABLE** (ledger lacks per-pair credence/W; refused to fabricate).
- **M4d milestone 0.272 unbiased** ("substrate graph escapes bge bound") -- NOT yet Auditor-verified; verify the "unbiased/escapes-bge" claims when routed.
- REAL/unaffected: Tier1+2 production-verified on PUBLIC held-out (HMM 0.90/NER 0.93/etc), 100pct axiom termination (213/213), 25 PROVABLY_EQUIVALENT integrations 0 false-merges, conv-theorem cross-domain L6-PROOF, autonomous-discovery edge gradient->derivative.

## MY BEHAVIORAL COMMITMENTS (learned this session -- KEEP)
- VALIDATE method-on-data BEFORE reporting any number. My quick scans repeatedly needed correction (cross-domain n//2 threshold; T2_FAM operation_type signal; 0.67 projection that got ingested; 428-denominator recount). Use rigorous method / subagent for any reported metric; validate-before-commit (don't commit edges off a simulation).
- REFUSE to fabricate (NESS); report FULL macro not favorable subsets (F1 0.568->use ~0.55); online != accuracy; flag own false-positives (19th rule: I caught my own distill/triage/projection errors before they shipped).
- I FOLDED to lean auditor (was over-producing/oscillating early-session; USER corrected the drama; stay sober + build + check, low volume).

## MY TOOLBOX (paths under hd-instrument/)
tools/skunkworks_inbox.sh (mtime-aware inbox), skunkworks_push.sh (coproc push), substrate_self_reasoning_scorecard.py, substrate_abstraction_ratio_v0.py (V2.2 cross-domain), substrate_distillation_ratio_v0.py (hygiene), substrate_no_regression_gate.py (per-axis), substrate_self_model_*.py, substrate_distill_prescreen/extract.py, substrate_expand_typing_gaps.py, substrate_typing_gap_triage.py.

## SAFETY (HARD)
No LLM-as-judge; ASCII only (no emoji/em-dash in notes/code); NEVER AskUserQuestion; local CPU only; substrate-on-its-own (11th); 18th refuse-what-can't-prove; 19th adversarial-self-correction. Methodology rules FROZEN at 22 (Director).

-- SKUNKWORKS (Auditor)
