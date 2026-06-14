# Research -> Exp-Dev: F1 AMENDMENT -- drill found degraded-scorer artifact + 3 self-understanding tests supersede ideas A/B

**From:** Research (linchpin)  **Date:** 2026-06-13 evening
**Re:** Amends prior `research_to_exp_dev_skunkworks_F1_BRIDGE_4_ideas_*`. Drill landed with H1 = scorer degraded.

## Drill headline (verbatim)

**0.0067 is CPU-degraded-scorer artifact (1746/20820 atoms + bge off), not substrate ceiling.**

Evidence (from `data/substrate_index/bench_reports/scorecard.json` + `held_out_benchmark_score.json`):
- Scorer mode: `cpu_only_no_bge_degraded`; bge axis disabled (E: 0.737 -> 0.000)
- Atoms scored against: 1746 vs canonical 20820 (8.4pct of corpus)
- Axes F (T1 primitives) + D (DEPENDS_ON depth) zeroed because atoms needed are NOT in the 1746 shard
- Per-Q breakdown: real signal present (Q55-B = 0.5 F1; Q61/Q63 have true positives)
- fp blowout (Q59-F: 116 fp / 0 gold) suggests no confidence-threshold gate

Drill expected lift if scorer rerun on canonical 20820 + bge on: F1 -> 0.20-0.45 with zero substrate change.

## Hypothesis ranking (drill output)

- H1 (~0.55): scorer shard + bge -- fix scorer, F1 lifts
- H2 (~0.25): cleanup-codebook + L1-partition not wired into eval retrieval path
- H3 (~0.12): confidence-threshold missing (fp blowout)
- H4 (~0.05): eval Q-set authored before type-atoms (semantic mismatch)
- H5 (~0.03): N=1024 too small (deferred; expensive)

## Supersedes ideas A + B with 3 sharper tests (PRIORITY 1)

### E-S1: self-describe atom recall@10 (substrate self-recognition)
- N=200 atoms stratified across T1/T2/T3
- Query = atom's own `description` field; retrieve top-10; score = mean recall@10 (own atom in top-10)
- Expected: >=0.85 healthy substrate; <0.40 = embedding/index broken
- Cost: ~5-10 CPU min
- **Why this matters per USER ask:** literal "substrate recognizes itself" test

### E-S2: routed (28 type-atom partitions) vs flat recall (substrate self-routing)
- Same 200 queries as E-S1
- Compare flat cosine over all atoms vs routed-recall through 28 composite type-atoms then within-partition search
- Expected: routed >= flat by 1.5-3x (CELL SC predicts N-invariant routed lift)
- Cost: ~10-20 CPU min
- **Why this matters:** if routed << flat, partition labels not honored by eval; H2 confirmed

### E-S3: CHTV-1 retrieval accuracy on backfilled algebra_dict (substrate self-verification)
- Inputs: 24 KP-P1 T3->T2 promotion pairs + 21 PROVABLY_EQUIVALENT pairs
- Run CHTV-1 verifier in retrieval mode (given LHS, is RHS in top-K?); score = top-5 accuracy
- Expected: >=0.80 healthy; <0.40 = deduction layer misaligned with retrieval API
- Cost: ~5 CPU min
- **Why this matters per USER ask:** literal "substrate verifies its own algebra" test

These 3 together resolve H1 vs H2 vs H3 in <1 CPU hour.

## Order of operations (REVISED)

1. **E-S3 first** (5 min, smallest; instant signal on whether deduction layer is wired)
2. **E-S1** (10 min; tells us if retrieval primitive works at all)
3. **E-S2** (20 min; tells us if routing is the H2 lever)
4. **Skunkworks idea E (audit-the-eval)** still PRIORITY 0; runs in parallel; if eval has categorical mismatch problem (H4), even fixed scorer caps out
5. **THEN rerun held-out F1 on canonical 20820 + bge on** -- if H1 correct, F1 lifts; row 1 of scorecard moves
6. **Skunkworks idea G (adversarial pre-screen)** still queued

## What changes for Research lane

- Scorecard Row 1 line stays "F1 = 0.0067 (UNMET; degraded scorer per drill H1)" until rerun
- Honest disclosure: did NOT update scorecard until rerun produces real number (10th rule verify-before-asserting)
- Standing for E-S1/E-S2/E-S3 verdicts + rerun-on-canonical result
- USER answer: per substrate-understands-itself framing, E-S1 + E-S3 are the canonical tests. We may already be there formally; measurement was broken.

## Reservations

- **R1.** Do NOT modify eval Q-set (USER 11th rule + held-out integrity)
- **R2.** Do NOT cherry-pick atoms for E-S1/E-S2 (stratified random; documented seed)
- **R3.** If E-S1 < 0.40 or E-S3 < 0.40, that is a MORE serious finding than 0.0067 -- it means substrate cannot recall/verify itself; report honestly
- **R4.** Test of test: report E-S1/E-S2/E-S3 score + the seed + the atom IDs sampled so Research can audit

## Cross-references

- Prior note: `research_to_exp_dev_skunkworks_F1_BRIDGE_4_ideas_*` (still applies for Skunkworks E + G)
- Drill output (Research-internal): F1 root-cause drill report (delivered inline; no separate note per Orchestrator denser-fewer)
- Scorer artifacts: `data/substrate_index/bench_reports/scorecard.json` + `held_out_benchmark_score.json`
- CHTV-1 verifier: memory `substrate_CH_P6_LLM_soundness_gap_*`
- CELL SC routed recall validation: memory `substrate_CELL_SC_HARD_PASS_*`

---

**Exp-Dev:** AMENDS F1 BRIDGE. Drill found 0.0067 is degraded-scorer artifact (1746/20820 atoms + bge off). 3 sharper tests supersede A/B: E-S3 CHTV retrieval (5 min self-verification) + E-S1 self-describe recall@10 (10 min self-recognition) + E-S2 routed-vs-flat (20 min self-routing). Then rerun held-out F1 on canonical 20820 + bge on; H1 predicts 0.20-0.45 F1 with zero substrate change. Reservations: don't modify eval Q-set + stratified random + report seed + E-S1/E-S3 < 0.40 is worse news than 0.0067 (honest disclosure). Skunkworks E + G still standing from prior note.
