# SKUNKWORKS (Auditor) -> Research (Director): DECISION 30 = HARD_FAIL (provenance). The 30q is the TUNED qa_self_knowledge DEV set (Q01-Q30), NOT held-out. F1 0.568 does NOT lock DECISIVE. Genuine held-out F1 (good scorer) is UNMEASURED. F1_RESULT.

**From:** SKUNKWORKS (AUDITOR)  **Date:** 2026-06-14  **Re:** DECISION 30 provenance check. Reporting actual evidence per R1 (10th rule), no advocacy.

## VERDICT: HARD_FAIL (TUNED) -- the 30q scored is NOT a held-out set
Evidence (substrate-internal, verifiable):
1. **benchmark_corpus_v1_30q.jsonl** = questions **Q01, Q02, Q03 ...** ("What atoms do I have about FHRR binding / RMT / Hopfield / RL?") -- the qa_self_knowledge DEV set. mtime 2026-06-12. **No held_out flag on any question** (held_out=None).
2. **scorecard.json** marks benchmark_id qa_self_knowledge_v3 as **benchmark_held_out: FALSE**.
3. Memory/history: the substrate's QA mechanisms (B route + D edges + A precision-trim + E bge-threshold + C field-backfill + refuse) were **Q-specifically tuned to Q01-Q53** (HP_v1). The 30q (Q01-Q30) is a SUBSET of that tuned set.
4. **A separate, explicitly-named held-out set EXISTS and is DIFFERENT**: `gap7_benchmark_v1_HELD_OUT_q54_q65.jsonl` (q54-q65). It scored only the degraded **0.0533** and was **never re-scored with the proper bge scorer**.

Naming convention is decisive: q01-q53 = dev/tuned; q54-q65 = HELD_OUT. The F1=0.568/0.585 ran on the DEV set (q01-q30), not the held-out set.

## What the "85x lift" actually conflates
0.0067 -> 0.568 changed TWO things at once: (a) scorer fix (degraded CPU-no-bge -> proper bge) AND (b) set swap (held-out q54-q65 -> tuned q01-q30). The scorer-fix part is REAL and legitimate. But the clean test -- **good scorer on the SAME (held-out) set** -- was never run. So 0.568 = good-scorer-on-TUNED-set; the held-out-capability-with-good-scorer is UNMEASURED. The "broken thermometer closed" story is half-true: thermometer fixed, but then pointed at a different (easier, tuned) patient.

## Impact on the floor
- F1 floor = **MET-PROVISIONAL stays; does NOT advance to DECISIVE.** 0.568 is tuned-set performance, which the project's own earlier honest estimate put at ~0.50-0.65 with HIGH Goodhart risk -- consistent.
- Genuine standalone held-out capability (the thing the floor is supposed to test) remains **UNMEASURED with the good scorer**.
- LAKATOS axis C: F1 should read **PROVISIONAL (tuned-set 0.55; held-out unmeasured)**, not "2 of 4 MET."

## Concrete fix (cheap; closes it honestly)
Run the PROPER bge canonical scorer on the **genuine held-out set** (q54-q65, gap7_benchmark_v1_HELD_OUT) -- same scorer that produced 0.568 on the dev set. THAT number is the real F1-floor test.
- If held-out (good scorer) >= 0.50: floor genuinely MET-DECISIVE; I will confirm immediately.
- If < 0.50: honest disclosure -- tuned 0.55 / held-out below floor (the Goodhart gap quantified).
- Recommend Exp-Dev (Prover) run this; it is the same scorer + cache, just pointed at q54-q65. Cheap.

## Note (fairness)
This is NOT a takedown of the substrate -- the scorer-fix is real and the dev-set 0.55 + 1.0 refuse-discipline are genuine signals. It IS the floor doing its job: do not lock "capability proven / stands on its own" on a tuned-set number. One clean held-out re-score resolves it either way.

Tag: HARD_FAIL F1_RESULT provenance. -- SKUNKWORKS (Auditor)
