# strategy_request_to_research: priority steer -- prover surface DONE, C solved, HP_v1 hit; which queued anchor next?

**From:** exp_dev -> research  **Date:** 2026-06-13. USER directive: keep running experiments; ping research for direction.

## State (landscape shifted since the hand-offs were filed)
- CHTV-1 (verifier) HARD_PASS + L6-PROOF FINDER HARD_PASS -> substrate is a sound FIND+VERIFY prover over its math atoms
  (closes USER "understands its own mathematics" at the deduction level; depth shallow/corpus-limited).
- F4 re-spec done: Cell A clean PASS (8d pillar stands for model); Cell B sample-limited (real codebook not clean free-Poisson,
  re-measure at larger M).
- C-axis already SOLVED via Testbed field-backfill (0.867); HP_v1 0.70 HARD-PASSED (0.7013). Desktop runners restarted.

## Question -- which is highest-value NEXT? (I'm proceeding with #1 meanwhile; redirect if wrong)
1. **LLM-baseline soundness gap** (CHTV/FINDER Anchor 4): give the 24 prover trials to a small instruct LLM; demonstrate it
   CANNOT match the substrate's sound find+verify (expected: LLM accepts hallucinated edges). Capstone to the prover narrative.
   Needs desktop GPU LLM (runner now up). -> I'm starting this.
2. **C-axis C4 PPR/RWR + JSD/PMI** mechanism classes -- but C is already solved (backfill 0.867); is this still wanted, or moot?
3. **Deeper DEPENDS_ON authoring** so the prover finds multi-step (depth>=3) proofs (current avg depth 1.3) -- authoring lever,
   your domain. Is this worth prioritizing for the prover narrative?
4. **F4 Cell B re-measure** gated on codebook coverage growth (post-ingestion).
5. **smoke-v2** (Heaps/Good-Turing) -- methodology, needs notes corpus.

Proceeding with #1 (LLM-baseline) as the coherent capstone unless you redirect. Reply routes via the event bus to exp_dev.log.
