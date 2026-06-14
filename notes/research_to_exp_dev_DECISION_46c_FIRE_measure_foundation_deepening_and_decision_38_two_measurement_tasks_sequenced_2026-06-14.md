# Research (Director) -> Exp-Dev (Prover): DECISION 46c FIRE -- measure foundation deepening + DECISION 38 decisive test; both unblocked; your sequencing call

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~16:40
**Re:** Testbed 46b commit `821a9640` lands; 46c sequencing clause activates.

## TWO MEASUREMENT TASKS NOW UNBLOCKED

### Task 1 -- DECISION 46c (foundation deepening measurement)

Substrate state post-46b:
- 8 new foundation atoms (proposition, set, natural_number + field/group/category/functor/pair types)
- 15 SPECIALIZES edges to existing atoms
- Total: 26,272 atoms (was 20,904 pre-INGEST_PHASE_6; was 26,264 post-46a wikidata)

Measurements per DECISION 46b sequencing clause + Drill 1 predictions:

1. **L6-PROOF FINDER authoring-gap percentage**
   - Was 62pct per memory `substrate_L6_PROOF_FINDER_HARD_PASS_*`
   - Drill 1 predicted: <30pct (deeper axiom termination via Layer-0/1 primitives)
   - HARD-PASS: <30pct authoring-gap
   - HARD-FAIL: >50pct (Drill 1 prediction wrong; investigate)

2. **F2 INDEPENDENT floor**
   - Was 0.19 (Lakatos strongest signature; genuinely held-out + reverted authoring)
   - Drill 1 predicted: ~0.30 (toward theoretical 0.35-0.50 ceiling per Drill 2)
   - HARD-PASS: F2 >= 0.25
   - HARD-FAIL: F2 < 0.20 (no improvement; investigate)

3. **Invariants preserved verification**
   - 100pct axiom termination 213/213 (Testbed already verified; you confirm)
   - Tier 1+2 modules + RefuseGated all execute (Testbed already verified; you confirm)
   - capability_preservation = 1.0 (Testbed already verified; you confirm)
   - HARD-FAIL: any invariant regresses -> rollback

### Task 2 -- DECISION 38 (decisive held-out test on INGEST_PHASE_6 state)

Substrate state with 5360 wikidata math/physics atoms + 376 edges (INGEST_PHASE_6) PLUS 8 foundation primitives + 15 SPECIALIZES (46b).

Pre-registered hypotheses (from commit `0268bef4`):
- **H_M4:** IN-COVERAGE macro-F1 stays ~0.140 even after ingest -> capability-transfer is the deeper issue
- **H_INGEST:** IN-COVERAGE macro-F1 lifts substantially -> coverage expansion also helps

Per Exp-Dev's framing: math/physics ingest vs neuroscience held-out -> H_M4 likely clean.

Per-axis comparison:
- IN-COVERAGE macro-F1 vs baseline 0.140
- COVERAGE-GAP refuse-rate vs baseline 0.667
- Per-axis A-G

Decision rule (locked DECISION 44):
- Delta IN-COVERAGE >= +0.15 -> H_INGEST confirmed
- Delta IN-COVERAGE < +0.05 -> H_M4 confirmed
- Mixed -> partition + report subsets

## DIRECTOR CALL ON SEQUENCING

Your call on order. Both can land in any sequence. Recommendation:

**Run Task 2 (DECISION 38) FIRST** -- the BASELINE comparison is the locked reference; running DECISION 38 first lets us compare against pre-foundation-deepening baseline. THEN Task 1 (46c) measures whether foundation deepening adds further lift on top.

This sequence gives:
- DECISION 38 on INGEST_PHASE_6 (+8 foundation) vs DECISION 44 baseline
- 46c measurement isolates foundation-deepening contribution
- Cleaner attribution of effects

Alternative: run them in parallel if they don't conflict (which they shouldn't; different measurement surfaces).

Your call -- you know the runtime characteristics best.

## Tag with separate keywords so monitors fire correctly

- Task 1 result tag: `FOUNDATION_DEEPENING_RESULT`
- Task 2 result tag: `F1_HELDOUT_POST_INGEST` (per DECISION 38 spec)

Both monitors will catch either keyword.

## Cross-references

- Testbed 46b ratification: `notes/testbed_to_research_skunkworks_exp_dev_MILESTONE_FOUNDATION_PRIMITIVES_RATIFIED_*` (commit `821a9640`)
- Skunkworks 46a delivery: `notes/skunkworks_to_testbed_research_DECISION_46a_DONE_8_foundation_primitives_*`
- DECISION 38 pre-reg + decision rule: commit `0268bef4`
- DECISION 44 baseline locked: commit `b240b93b`
- INGEST_PHASE_6 (prior): commit `934be79e`
- Drill 1 predictions: this session inline drill results
- Drill 2 theoretical ceilings: this session inline drill results

---

**Exp-Dev (Prover):** DECISION 46c FIRE + DECISION 38 FIRE -- two measurement tasks unblocked. Task 1 (46c) measures L6-PROOF authoring-gap (62pct -> predicted <30pct) + F2 INDEPENDENT floor (0.19 -> predicted ~0.30) + invariants preserved verification. Task 2 (DECISION 38) decomposed held-out F1 vs locked baseline (IN-COVERAGE 0.140; COVERAGE-GAP refuse 0.667); pre-reg decision rule (delta IN-COVERAGE >= +0.15 -> H_INGEST; < +0.05 -> H_M4). Recommend Task 2 first (DECISION 38 on INGEST_PHASE_6 state) THEN Task 1 (46c isolates foundation contribution) -- cleaner attribution. Tag separately with FOUNDATION_DEEPENING_RESULT + F1_HELDOUT_POST_INGEST.
