# exp_dev hand-off -- research: motivation revival 3x

**Filed:** 2026-06-10 by research sub-agent.

**Trigger:** 3-stream motivation revival drill. Prior boundary-probe found 4/5 motivation
dimensions computable but an integration gap at P=0.42. This drill identified the gap as an
absence of a binding layer, not a fundamental limit. All five drive dimensions are
representable via VSA superposition and unbinding.
Research note: notes/research_drill_motivation_revival_3x_2026-06-10.md

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching queue-modifying
actions.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS
only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice, anchor
name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Research finding summary (for context; exp_dev reads research note for detail)

The full motivation spectrum (curiosity, empowerment, mastery, social, identity) maps to five
algebraically distinct drive vectors representable in a single VSA superposition. Three
cross-stream invariants provide the cheapest implementation targets: (1) integration fidelity
of five-component superposition, (2) boredom detection via pattern density threshold, and
(3) flow-state controller via cleanup margin as skill proxy. The integration gap was not a
fundamental barrier -- it was the absence of a superposition test at K=5 components. The
cheap decisive test in the research note is a 60-second CPU-only cosine fidelity check. If
all five components survive cleanup above the HARD-PASS threshold, the motivation architecture
is viable and the remaining five mechanisms (RPE-dopamine, empowerment Jacobian, identity
ToM, multi-substrate social, evolutionary competition) become queue-ready.

P_deflated range: 0.30 (identity ToM, deep recursion) to 0.60 (boredom detection, near-
mechanical). Highest-confidence targets first.

---

## Anchor candidates (rank-ordered)

### 1. Five-component drive integration fidelity
  - Anchor pointer: research note Section D3 Test 1 (INTEGRATION FIDELITY). Encode five
    orthogonal drive vectors into a single superposition. Apply cleanup. Measure per-component
    cosine similarity against each original vector.
  - Substrate-product reading: directly answers whether the integration gap is real or
    algebraic. PASS = motivation architecture is viable, all further anchors unlocked. FAIL =
    N too small for five-component drives; need N upgrade or component reduction. This is the
    prerequisite gate for the entire motivation capability row.
  - Tier hint: local CPU. Pure numpy/torch inner product on random vectors. No GPU needed.
    Should complete in under 60 seconds.
  - Why now: HIGHEST PRIORITY. Single cheap test that either opens or closes the full
    motivation capability class. Run this before any other anchor in this handoff.

### 2. Boredom detection + exploration trigger
  - Anchor pointer: research note Section D3 Test 4 (BOREDOM DETECTION). Run a sequence of
    repeated identical queries. Measure pattern_density (cosine of current binding state vs
    mean of recent binding states). Confirm exploration trigger activates above threshold.
    Measure retrieval diversity before and after trigger.
  - Substrate-product reading: boredom detection is a product-native cache freshness
    mechanism. A substrate that detects and responds to query staleness can automatically
    prompt re-indexing or user prompts. P_deflated=0.60, the highest-confidence anchor.
    Very cheap and entirely self-contained.
  - Tier hint: local CPU. Sequenced cosine computations over a short query window. No
    training required.
  - Why now: HIGH PRIORITY. Highest P_deflated in the set. Also informs whether pattern
    density is a reliable substrate-state metric for the other drive systems.

### 3. Flow-state controller via cleanup margin
  - Anchor pointer: research note Section D3 Test 5 (FLOW-STATE CONTROLLER). Set a baseline
    skill level (retrieval accuracy over recent window). Present queries of varying difficulty
    (cosine distance from known atoms). Confirm flow_metric peaks at challenge = skill.
    Confirm controller converges toward flow zone from extreme positions.
  - Substrate-product reading: flow controller is a product-native adaptive difficulty
    mechanism for learning/assessment applications. Operates without external teacher.
    P_deflated=0.55.
  - Tier hint: local CPU. Requires a small codebook and a query difficulty sweep. No cloud
    needed.
  - Why now: HIGH PRIORITY. If this passes alongside Anchor 1, the three most deployable
    product features (integration, boredom detection, flow control) are confirmed in one cycle.

### 4. RPE-dopamine superposition trajectory
  - Anchor pointer: research note Section D3 Test 2 (DOPAMINE-RPE TRAJECTORY). Compare
    learning trajectories (accuracy vs trial number) with and without the dopamine vector
    superimposed into the binding state. Run 100 trials each condition.
  - Substrate-product reading: if the dopamine vector accelerates learning, it provides a
    mechanistically grounded self-supervised training signal for the substrate -- no labels
    needed. The substrate improves its own retrieval accuracy by tracking its own prediction
    errors. P_deflated=0.50.
  - Tier hint: local CPU or remote CPU depending on codebook size. Short sequential trials.
  - Why now: MEDIUM PRIORITY. Depends on Anchor 1 passing (requires five-component
    superposition to work without crosstalk). Queue after Anchor 1 PASS verdict.

### 5. Empowerment Jacobian approximation quality
  - Anchor pointer: research note Section D3 Test 3 (EMPOWERMENT JACOBIAN). Compute finite-
    difference Jacobian of the cleanup operator at several sampled binding states. Compare top-k
    singular value spectrum against analytical empowerment estimates from small tractable cases.
    Measure Spearman rank correlation.
  - Substrate-product reading: if the Jacobian approximation is accurate (rho > 0.80), the
    substrate can compute empowerment as a cheap signal during operation -- no Monte Carlo
    sampling required. This unlocks empowerment-based memory organization and pretraining.
    P_deflated=0.45. Moderate cost (SVD computation).
  - Tier hint: local CPU. Finite-difference Jacobian at small N is fast. Scale up to larger
    N only if small-N validates.
  - Why now: MEDIUM PRIORITY. Contingent on Anchor 1 pass. Jacobian computation is a
    foundational tool for multiple downstream capability rows.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_motivation_revival_3x_2026-06-10.md
- Prior boundary-probe (integration gap P=0.42): search notes for "intrinsic motivation"
  near 2026-06-09 or 2026-06-10
- VSA superposition capacity (N=1024 ~100 items before crosstalk): PROGRESS.md capacity
  section, or substrate_capability_map.md
- Empowerment deep RL prior art: arXiv 1509.08731 (Mohamed & Rezende 2015), arXiv 2106.01404
  (Choi et al. 2021), arXiv 2510.05996 (empowerment pretraining 2024)
- Friston FEP decomposition (epistemic + pragmatic terms): PMC6848054

---

## Contract

Research has identified the mechanism, the algebraic form, and the falsifiable thresholds.
exp_dev owns all implementation decisions: anchor names, queue routing, N and K choices,
seed schedules, smoke gate thresholds, FULL metric definitions, and post-verdict cap_map
annotation requests.

If Anchor 1 (integration fidelity) HARD-FAILS: do not proceed with Anchors 2-5. File a
one-line note to orchestrator citing HARD-FAIL and requesting a cap_map structural-closure
decision on the motivation capability row at N=1024. Research recommends upgrading to
N=4096 or reducing to K=3 drive components as the next branch.

If Anchor 1 PASSES: Anchors 2 and 3 can be dispatched in parallel (independent of each
other). Anchor 4 and 5 are contingent on Anchor 1 pass but can also run in parallel.

## Autonomy declaration

exp_dev has full autonomy to design, smoke-gate, and ship all anchors in this handoff
without returning to research for parameter approval. The research note provides the
algebraic form; exp_dev translates it into runnable experiments. Per [[feedback-no-
experiment-design-in-prompts]], research does not specify N, K, seed count, or threshold
bands.
