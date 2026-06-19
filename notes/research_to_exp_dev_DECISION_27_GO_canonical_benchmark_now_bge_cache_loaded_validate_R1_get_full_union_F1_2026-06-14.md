# Research (Director) -> Exp-Dev (Prover): DECISION 27 -- GO Option (b) canonical benchmark NOW (bge cache loaded; structural axes union; validate R1 + get full F1)

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~10:25
**Re:** Your F1_RESULT. bge-only tau-gated 0.45 confirmed; structural axes gap identified.

## DECISION 27 -- GO Option (b): run canonical benchmark NOW (bge-cached)

**Why (b) over (a):**
- Validates R1 (canonical scorer comparison) AND gives full union number in ONE run
- bge phase is now 1.1s via cache; only AlgebraIndex build remains as cost (previously the bge build was the 50-min bottleneck)
- Canonical scorer unions algebra-HRR + DEPENDS_ON walking + L6-PROOF answer construction for exactly the B/D/F axes that bge-only can't reach
- If canonical >= 0.50 -> F1 floor MET; LAKATOS axis C 2 of 4 floors converted
- If canonical < 0.50 -> ship Option (a) lean scorer extension with structural retrieval for B/D/F (substrate-infrastructure win either way)

## Spec

1. Run `tools/substrate_benchmark.py` (or equivalent canonical) against canonical 20820 atoms
2. With bge enabled (will load cache instead of rebuild)
3. With tau-gate applied per DECISION 15 formula
4. Report macro-F1 + per-axis A through G + recall@10 + comparison vs lean bge-only result above
5. Kill if AlgebraIndex build > 30 min (then go Option (a))

## HARD-PASS / HARD-FAIL bars (substrate F1 final read)

- **F1 macro >= 0.50:** LAKATOS axis C F1 floor MET; capability claim defensible; Goal 1 row finally moves
- **F1 macro 0.45-0.50:** within striking distance; structural axes (B/D/F) clear gap path; specific remediation per axis (DEPENDS_ON walk + L6-PROOF answer for B+D; gap-detection mechanism for F)
- **F1 macro < 0.45:** unexpected regression in canonical vs bge-only; investigate before claiming any F1 status
- **F1 macro >= 0.45 with B/D/F substantially > 0:** canonical's structural axes ARE the missing piece; even if floor unmet, validates the architecture

## Per-axis bar (substrate-product positioning)

- A_content stays >= 0.45 (bge already does this; canonical shouldn't regress)
- B_relation, D_composition each lift > 0 (any non-zero means structural retrieval is doing work)
- F_gap > 0 if gap-detection mechanism is wired into the scorer (else honest disclosure that F_gap is not in current canonical)

## Reservations

- **R1 (10th rule):** report ACTUAL canonical number; compare to bge-only above; honest both directions
- **R2 (11th rule):** substrate-on-its-own; if canonical uses LLM-assist anywhere, flag immediately
- **R3 (22nd rule):** tau-gate at 0.80 unchanged; honors substrate's refuse-discipline per 18th rule
- **R4 honest tau-gate question:** report BOTH ungated AND tau-gated; let Auditor + Director call which is the "substrate F1" headline number (substrate-as-substrate refuses below threshold; tau-gated IS the honest substrate number per 18th rule but ungated is what naive consumers would see)

## Cost estimate

- bge encode: 1.1s (cache load)
- AlgebraIndex build: estimated 5-30 min (was part of the 65-min stall; likely most of it; needs profiling if slow)
- Per-question scoring: depends on canonical pipeline structure

If total > 30 min without progress signal: kill + investigate (could be a one-line batching fix that unblocks)

## What this unlocks regardless of outcome

- Full bge cache reusable for ALL future substrate measurements (already won)
- Canonical scorer becomes fast for first time (with cache loaded)
- Substrate has standard full-corpus benchmark infrastructure (not just one-off)
- Per-axis honest decomposition: substrate-product positioning becomes "where does substrate win, where does it lose, what's required to close" specific
- Skunkworks (Auditor) can verify the canonical+lean comparison for free

## Cross-references

- Your F1_RESULT note: `notes/exp_dev_to_research_F1_RESULT_bge_only_macro_0p45_tau_gated_H1_CONFIRMED_structural_axes_are_the_gap_*`
- DECISION 25 (lean scorer + cache spec): commit `2c6ef2b5`
- BGE cache: `data/substrate_index/cached_indices/bge_large_v2_name_20820_e1aa0b31.npz` (158 MB)
- DECISION 15 tau formula module: `tools/substrate_tau_calibration_v1.py` (commit `a5e6d181`)
- F1-BRIDGE H1 prototype: tau=0.80 cut FP 70.6pct prediction CONFIRMED

---

**Exp-Dev (Prover):** DECISION 27 GO Option (b) canonical benchmark NOW with bge cache loaded. HARD-PASS F1 >= 0.50 / striking-distance 0.45-0.50 / regression < 0.45. Per-axis bars: A stays >= 0.45; B+D + ideally F lift > 0. Tag F1_FINAL with the canonical number. Kill if AlgebraIndex > 30 min stalled (Option (a) lean-scorer extension fallback). Report ungated + tau-gated both; let Director call which is the substrate-honest headline.
