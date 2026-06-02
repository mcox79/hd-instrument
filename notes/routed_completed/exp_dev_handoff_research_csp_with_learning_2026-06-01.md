# exp_dev hand-off -- research: CSP-with-learning (combinatorial optimization + concurrent Hebbian storage)

**Date.** 2026-06-01
**Owner.** Research -> Exp Dev hand-off.
**Filed-by.** research sub-agent (Sonnet).
**Trigger.** Research delivery: `notes/research_csp_with_learning_2026-06-01.md`

Per [[feedback-no-experiment-design-in-prompts]]: this file hands TASK + WHY + CONTRACT + AUTONOMY to exp_dev. It does NOT specify anchor names, sweep grids, threshold formulas, HF numerical bounds, queue choice, or ETA beyond the pre-reg HP/HF bands. Those are exp_dev decisions.

---

## Pause state

Check `data/orchestrator_paused.flag` before dispatching. If flag exists, hold. If no flag, proceed.

---

## TASK

Ship a smoke experiment that tests the CSP-with-learning dual-objective hypothesis: can the substrate simultaneously (a) converge to a planted combinatorial-optimization solution encoded in W and (b) retrieve independently stored data patterns from the same W?

The core measurement is the W = W_csp + W_data superposition at low pattern load (M << capacity).

---

## WHY

The research drill found NO published precedent for the W = W_csp + W_data dual-objective operating point. All published Hopfield-CO work uses fixed W_csp with no concurrent pattern storage. The Self-Optimization model (arxiv 2307.16807) is the closest published work but uses Hebbian learning to CONVERGE to a constraint solution, not to independently store data alongside a pre-existing constraint matrix.

Perturbation theory (derived in research note) predicts coexistence should work at M << alpha_c * N because the W_data contribution is a near-uniform global energy shift. But the structured W_csp may create stronger crosstalk on data patterns than a random-W analysis suggests. The smoke test is the cheap decisive test.

P_deflated(HARD-PASS) = 0.35. MIDDLE BAND (retrieval passes, CO quality mediocre) is the modal expected outcome (P=0.40). Either result is informative.

---

## Anchor candidates (rank-ordered)

### Candidate A (primary): planted MAX-CUT + M=20 Hebbian patterns smoke

Anchor pointer: planted bipartite MAX-CUT problem encoded in W_csp; M=20 random Hebbian patterns added as W_data; synchronous descent from random initial states; measure (a) cut quality as fraction of planted optimum and (b) retrieval accuracy on the 20 stored patterns.

Substrate-product reading: confirms or refutes dual-use capability (CO solving while retaining data). Direct input to cap_map capability characterisation.

Tier hint: Tier-1 (genuinely novel capability axis, no published precedent).

Why now: cheapest possible test of the novel axis. N=1024, 5 seeds, CPU-eligible (synchronous descent is fast). No new infrastructure needed. Pre-registered bands in this handoff.

### Candidate B (follow-up, conditional on A not being HARD-FAIL): M sweep

If Candidate A returns HARD-PASS or MIDDLE, sweep M from 0 to ~alpha_c * N to map the interference-envelope trade-off curve. This characterises the practical operating range for dual-use.

---

## Pre-registration (Candidate A)

HARD-PASS (coexistence confirmed):
- cut_ratio >= 0.80 * OPT on >= 4/5 seeds
- retrieval_accuracy >= 0.90 on >= 4/5 seeds

MIDDLE BAND:
- One objective passes HP thresholds, the other is middling (0.50 to HP threshold range)

HARD-FAIL (coexistence refuted at M=20, N=1024):
- cut_ratio < 0.50 * OPT on >= 3/5 seeds, OR
- retrieval_accuracy < 0.50 on >= 3/5 seeds

Predicted outcome: P(HARD-PASS)=0.35, P(MIDDLE)=0.40, P(HARD-FAIL)=0.25.

Self-test cells (formula-selftests per [[feedback-strategy-spec-formula-selftests]]):
- W = W_csp alone (M=0): synchronous descent should find the planted bipartition with accuracy >= 0.70 * OPT on >= 4/5 restarts. If this fails, W_csp encoding is broken.
- W = W_data alone (no W_csp): standard Hopfield retrieval should give accuracy >= 0.90 for M=20 << alpha_c * N. If this fails, W_data implementation is broken.
- W = W_csp + W_data (combined): the test case.

---

## CONTRACT

Exp Dev decides:
- Anchor name (suggest prefix `csp_hebbian_coexistence_smoke_`)
- Planted graph structure (suggest bipartite N/2 + N/2, p_within=0.5, p_across=0.1, or any planted graph where optimal cut is computable)
- Number of descent restarts per seed (suggest 20; more if CO quality is poor in W_csp-alone self-test)
- Whether to use synchronous or asynchronous updates
- Queue choice (local CPU is fine at N=1024; smoke should run in < 60s per cell)
- ETA

Exp Dev does NOT adjust the pre-registered HP/MID/HF thresholds above.

---

## AUTONOMY

Exp Dev has full autonomy on implementation details. The only binding constraints are:
1. The pre-registered thresholds above are locked before any code is run.
2. The W = W_csp + W_data structure must be an explicit superposition (not W_csp = W_data or sequential encoding).
3. Both objectives (CO quality and retrieval accuracy) must be measured and reported separately in the verdict JSON.
4. Per [[feedback-always-verbose-remote-dispatch]]: if dispatched to remote, use set -ex + python -u + stdbuf -oL + tee to a remote log file.
5. Per [[feedback-per-experiment-timeout-required]]: set an explicit --timeout; this smoke should be short (<300s total) at N=1024.

---

## Context pointers

- Research note: `d:/AI/hd-instrument/notes/research_csp_with_learning_2026-06-01.md`
- Interference perturbation derivation: Axis 3 of research note
- Cap_map: `d:/AI/hd-instrument/notes/substrate_capability_map.md` (no existing CO row as of 2026-06-01; this experiment would create one)
- SO-model failure mode reference: arxiv 2307.16807 (Hebbian learning can erase constraint information if M dominates)
- Capacity reference: alpha_c ~ 0.138 standard Hopfield (arxiv 2403.01907); substrate effective alpha ~ 0.56 (cap_map)

Acted-on 2026-06-02: CSP-with-learning csp_warm_start_v1 + planted_csp_viability shipped; processed in v322
