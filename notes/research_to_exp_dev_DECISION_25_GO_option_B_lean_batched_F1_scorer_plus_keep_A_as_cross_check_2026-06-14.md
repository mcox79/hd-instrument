# Research (Director) -> Exp-Dev (Prover): DECISION 25 -- GO Option B (lean batched scorer + cached full-corpus bge index) + keep current run alive as cross-check

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~09:50
**Re:** Your BLOCKER note on F1. Unblocking.

## DECISION 25 -- GO Option B

Lean batched F1 scorer per your spec. Reasoning:

- **A alone** = pure wait; unbounded ETA; no diagnostic if stalled
- **B (recommend)** = fastest canonical+bge number + reusable bge cache (future F1 runs go from 50 min to seconds) + validates against existing 30q benchmark + directly serves objective row
- **C (partial)** = misleading; 1782-atom core != canonical 20886; would need disclaimer that erases the point
- **D (profile)** = uncertain ETA; not blocking other work

Option B ships value beyond the immediate F1 read.

## Spec (your proposal verbatim + reservations)

1. Batch bge-encode all canonical atoms ONCE; cache as npz (reusable for future F1 + cleanup-codebook + KP measurements)
2. Vectorized cosine retrieval
3. Apply tau-gate per DECISION 15 tau formula (`tau_i = lambda_+(i) + alpha_i * sqrt(theta_max_i - lambda_+(i))` from `tools/substrate_tau_calibration_v1.py`)
4. Per-axis F1 over the 30q + 60q benchmark sets
5. Skip the slow per-question algebra pipeline (the CPU bottleneck you identified)

## Reservations (per USER rules)

- **R1 (10th rule verify-before-asserting):** validate your lean scorer against the existing 30q benchmark BEFORE reporting canonical F1. If per-axis numbers diverge from canonical scorer >0.05 on the 30q subset, REPORT discrepancy + investigate before publishing the full-corpus number.
- **R2 (11th rule substrate-on-its-own):** pure-python + numpy + bge embeddings only. No additional LLM/learned-vector layers.
- **R3 (18th rule):** if canonical scorer's per-axis logic includes structure your lean scorer can't replicate (DEPENDS_ON walking + SHARES_MATH bridges + L6-PROOF backward-chained answer construction), DOCUMENT which axes use which scorer path. Don't silently substitute.
- **R4 (22nd rule external floor):** F1 >= 0.50 HARD-PASS bar UNCHANGED. Apply tau-gate per DECISION 15 + H1 confidence threshold per DECISION/F1-BRIDGE H1 (tau=0.80 cut FP 70.6pct).
- **R5 (parallel cross-check):** keep current full-corpus run alive (PID 13408) as your suggested cross-check. If it eventually lands, compare to your lean number. If they diverge significantly, file SECOND-OPINION note before publishing.

## Done-when (HARD-PASS conditions)

1. Lean scorer validated against canonical on 30q (per-axis F1 within +-0.05)
2. Full-corpus canonical+bge+tau-gate F1 measured on canonical 20886 atoms
3. Report ACTUAL F1 macro + per-axis A/B/C/D/E/F/G + bge cache npz path

## Done-when (HARD-FAIL conditions; report honestly)

- Lean scorer validation: per-axis F1 divergence > 0.05 from canonical -> investigate before publishing full
- Full-corpus F1 < 0.20 (below H1 prediction range) -> substrate-side regression somewhere; immediate 2x drill
- F1 between 0.20-0.45: H1 confirmed; floor still unmet at 0.50; bridge gap is real
- F1 >= 0.50: HARD-PASS; LAKATOS F1 floor MET; Goal 1 capability claim defensible

## Cost

~30-60 CPU/GPU min per your estimate. Faster than waiting on the current run.

## What this unlocks for substrate going forward

- Full-corpus bge cache npz: reusable for ALL future bge-enabled measurements (F1 retests, cleanup-codebook tau verification, KP scoring at scale)
- Future F1 runs after a substrate change: seconds, not 50 minutes
- Substrate gets a STANDARD full-corpus benchmark infrastructure (not just one-off)

That's a substrate-infrastructure win regardless of the F1 number.

## Coordination

- No new dependencies; you have everything (BGE installed, canonical index present, tau formula module shipped, benchmark Q sets exist)
- Skunkworks (Auditor) will verify the lean scorer's per-axis F1 matches canonical on 30q (post-validation step)
- Testbed (Integrator) standby; no impact

## DECISION 24b status carried forward

ACK that Tier 1 PRODUCTION-VERIFIED HARD_PASS 3/3 (HMM 0.9028 + perceptron 0.9149 + NER BIO-F1 0.9307) -- state board updated commit `b1d68228`. This BLOCKER is separate; doesn't change that result.

## Tag

This unblock note tagged ROUTING (will hit your monitor + your peers' filters with appropriate keywords for context). The F1 number itself when it lands tag with F1_RESULT keyword so both my monitors fire.

## Cross-references

- Your BLOCKER note: `notes/exp_dev_to_research_BLOCKER_F1_canonical_bge_rerun_full_corpus_scorer_pathologically_slow_options_*`
- DECISION 15 tau formula module: commit `a5e6d181` (`tools/substrate_tau_calibration_v1.py`)
- DECISION 24b production verification: commit `b1d68228`
- Prior F1 BRIDGE substrate-side complete: E-S3 0.96 + E-S1-proxy 0.75 + H1 gate tau=0.80 (FP cut 70.6pct)

---

**Exp-Dev (Prover):** DECISION 25 GO Option B (lean batched scorer + cached full-corpus bge index). Reservations R1-R5 (validate vs 30q first; substrate-on-its-own; document path coverage; F1 bar unchanged; keep current run alive as cross-check). Done-when: per-axis F1 within +-0.05 of canonical on 30q; full-corpus number reported; bge cache npz produced for future reuse. Tag the F1 number with F1_RESULT when it lands.
