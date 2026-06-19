# exp_dev hand-off -- research: substrate constraint solving and theorem proving (2x)

**Filed:** 2026-06-08 by research sub-agent.

**Trigger:** 2x deep research drill on substrate Datalog^neg compositional operators (AND/NOT/COUNT
cycles 192-193, 4/5 HP) and K-hop reasoning (K=12, PP-161) -- extending empirical foundation to
constraint solving and theorem proving capability claims.
Research note: notes/research_drill_substrate_constraint_theorem_2x_2026-06-08.md

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching queue-modifying actions.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS
only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice, anchor
name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Research finding summary (for context; exp_dev reads research note for detail)

The substrate's AND (PP-162, prec=1.000), NOT (PP-163/174, prec=1.000), COUNT (PP-175, acc=1.000),
and K-hop (PP-161, K=12) form the complete operator set of stratified Datalog, which is the
standard theoretical class for constraint propagation engines and bottom-up logic programming.
The complexity theorem says stratified Datalog is PTIME in data complexity. The substrate
already runs each operator in PTIME. The only missing empirical test is the outer fixpoint loop
(iterate until no new facts derived), which is a wrapper over existing ops.

For theorem proving: K-hop IS proof search (traverse "proved-by" edges from goal to axioms).
Termination is guaranteed (PP-177, cyclic-hierarchical halt=1.000). Depth-12 traversal covers
>= 95% of real Lean 4 proof steps (LeanCopilot 2024 finding). For premise selection in Lean/Coq,
the substrate replaces the BM25+embedding pipeline at sub-millisecond latency.

For CSP solving: AND-NOT (PP-174) IS arc consistency domain reduction. One pass per constraint
arc eliminates inconsistent domain values. The fixpoint loop terminates because domains shrink
monotonically. This gives a complete AC-3 constraint propagator in 15-20 lines of Python over
existing substrate ops.

The product claim: substrate enforces logical constraints at precision=1.000, with provenance
per step, at sub-millisecond latency, with zero LLM involvement. LLMs cannot match this on
negation, conjunction depth, or termination guarantees.

---

## Anchor candidates (rank-ordered)

### 1. Constraint violation detection (Latin square all-different)
  - Anchor pointer: research note Section "Level 6 Anchor D" -- encode all-different
    constraints for a 3x3 Latin square, generate 100 mixed valid/invalid assignments,
    measure violation detection precision and recall via AND-NOT.
  - Substrate-product reading: closes the constraint checking product claim. If precision
    and recall are both >= 0.95, the substrate can serve as a policy enforcement engine
    at storage speed. Directly relevant to compliance and EU AI Act Article 12 audit.
  - Tier hint: CPU only. Small N (4096-8192). Short run (~15 min). Extends PP-174 directly.
  - Why now: cheapest decisive test. 15-30 line wrapper over existing AND-NOT. Binary
    pass/fail with clear interpretation. HIGHEST PRIORITY for closing the CSP claim.

### 2. K-hop proof chain with negated intermediate precondition
  - Anchor pointer: research note Section "Level 6 Anchor C" -- synthetic theorem base
    with one negated precondition at an intermediate lemma; verify K=3 chain finds goal.
  - Substrate-product reading: confirms that K-hop proof search works when intermediate
    inference steps involve negation. This is the modal use case for formal verification
    ("Lemma L1 holds only when NOT A3"). If this fails, proof search with negated steps
    is broken and requires a design change.
  - Tier hint: CPU only. N=8192. Direct composition of PP-161 and PP-174.
  - Why now: opens the theorem-proving product story. If it passes, the substrate is a
    proof-search engine for negation-containing proof graphs. Short run, no GPU needed.

### 3. Datalog fixpoint convergence on small program
  - Anchor pointer: research note Section "Level 6 Anchor A" -- encode 10-20 Datalog^neg
    rules, run bottom-up evaluation loop to fixpoint, compare derived facts to reference
    Python Datalog interpreter.
  - Substrate-product reading: the most direct validation of the Datalog-equivalence claim.
    If derived facts match the reference interpreter exactly, the substrate is empirically
    equivalent to a stratified Datalog evaluator. This is a landmark capability claim.
  - Tier hint: CPU only. Small N. Requires a 30-50 line evaluation loop (pure Python,
    no new substrate primitives). Medium implementation effort, short run.
  - Why now: closes the Datalog equivalence claim with a verifiable comparison.

### 4. Premise selection recall@10 from synthetic 500-lemma library
  - Anchor pointer: research note Section "Level 6 Anchor E" -- encode 500 synthetic
    lemma bundles, query with 100 goal patterns, measure recall@10 of relevant premises.
  - Substrate-product reading: directly demonstrates the Lean 4 / Coq integration use case.
    If recall@10 >= 0.80, the substrate replaces the embedding-model premise selection
    pipeline at 10-100x lower latency. This is a direct head-to-head vs the LeanCopilot
    baseline.
  - Tier hint: CPU only. N=8192 (500 lemmas is well within capacity). Medium-length run.
  - Why now: opens the formal verification accelerator product story.

### 5. 3-SAT instance encoding and recovery
  - Anchor pointer: research note Section "Level 6 Anchor B" -- 10 satisfiable random
    3-SAT instances with 30 variables, 120 clauses; measure how many the substrate solves
    via AND-NOT cleanup from partial assignment.
  - Substrate-product reading: directly tests the Hopfield-as-SAT-solver analogy. This is
    a speculative result (P_deflated=0.45) -- failure is informative (tells us the Hopfield
    energy landscape does not reliably find SAT solutions at this scale), pass is a
    significant new capability claim.
  - Tier hint: CPU only. N=4096. Highest-risk anchor in the set. Run after Anchors 1-3
    confirm the baseline capability.
  - Why now: de-risks the SAT claim cheaply before any product framing investment.

---

## Context pointers (file paths only, no summaries)

- notes/research_drill_substrate_constraint_theorem_2x_2026-06-08.md (this drill's full text)
- notes/substrate_capability_map.md (PP-162, PP-163, PP-174, PP-175, PP-161, PP-160, PP-118, PP-177)
- data/orchestrator_status_log.jsonl (recent research delivery context)
- notes/exp_dev_handoff_research_GPU_Khop_infra_2x_2026-06-08.md (structural template reference)

---

## Contract section

exp_dev takes full autonomy on:
- Anchor naming (do not use the names above as anchor file names; exp_dev names anchors)
- N, M, K, seed count, threshold bands
- Whether to smoke first or go straight to full
- Queue routing (overnight vs local CPU vs remote_cpu_queue)
- Order of dispatch (may reorder based on queue state)
- Whether to batch these into a single dispatch or spread across cycles

Research does NOT specify any of these. The anchor POINTERS and SUBSTRATE-PRODUCT READINGS
above are the handoff payload. exp_dev reads the research note for full mechanism detail.

## Autonomy declaration

exp_dev owns experiment design end-to-end. Research delivers findings and falsifiable
predictions. The boundary is clean. No override of exp_dev design decisions from this note.
