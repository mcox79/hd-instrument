# exp_dev hand-off -- research: substrate probabilistic reasoning 5x

Filed-by: research sub-agent
Date: 2026-06-08
Trigger: notes/research_drill_substrate_probabilistic_reasoning_5x_2026-06-08.md
Urgency: HIGH -- PP-155 MIDDLE_BAND is the gate for the entire probabilistic reasoning capability class; N=32768 HP rescue is CRITICAL PATH for product claims in medical/legal/financial verticals

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching any anchor.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: pp155_hp_rescue_n32768_v1 (CRITICAL GATE)

Anchor pointer: Research note Section 7, Anchor 1 + Section 8 (Cheap decisive test) + cap_map PP-155 HP rescue documentation
Substrate-product reading: PP-155 strongest-wins=0.905 at current N is in MIDDLE_BAND. At N=32768, the documented HP rescue path projects strongest-wins >= 0.95. This unlocks the entire probabilistic reasoning capability class -- every downstream anchor in this handoff requires PP-155 at HARD_PASS.
Tier hint: CPU laptop, ~2 hr. Existing continuous-strength script + N bump. Cheapest possible gate.
Why-now: This is the single test that gates all probabilistic product claims. LLM base-rate neglect is well-documented (arxiv 2406.14986); substrate's amplitude-encoded confidence is the categorical alternative -- but only if strongest-wins >= 0.95 at scale. MIDDLE_BAND is not sufficient for product claims.

Pre-reg bands:
  HARD-PASS: strongest-wins >= 0.95, rank-correlation >= 0.99 at N=32768
  MIDDLE-BAND: strongest-wins = 0.92-0.95 (improved but still below HP; may need amplitude boost)
  HARD-FAIL: strongest-wins < 0.90 at N=32768 (regression from N=4096; categorical claim requires revisiting)

### Anchor 2: soft_cleanup_distribution_v1 (NEW CAPABILITY)

Anchor pointer: Research note Section 2.3 + Section 7, Anchor 2
Substrate-product reading: Convert PP-107's binary abstention signal into a full calibrated probability distribution over the codebook. Return top-K cosine similarities normalized to a probability vector. If Brier score < 0.10 and ECE < 0.05, substrate returns calibrated probability distributions -- the direct counterpart to LLMs' miscalibrated verbalized estimates (arxiv 2406.14986 failure mode 2).
Tier hint: CPU laptop, ~1-2 hr. Modification to cleanup function; no new script from scratch. Can run in parallel with Anchor 1.
Why-now: This converts an existing validated capability (PP-107 AUC=1.0) into a quantitative probability output. Low engineering cost, high product value. The distribution output enables PPL integration and Bayesian aggregation.

Pre-reg bands:
  HARD-PASS: Brier score < 0.10, ECE < 0.05 across 100+ queries with known ground truth
  MIDDLE-BAND: Brier 0.10-0.25 (useful for relative ranking, not absolute probability)
  HARD-FAIL: Brier > 0.25 (worse than uniform baseline; cleanup scores not calibrated as probabilities)

### Anchor 3: khop_confidence_chain_v1 (EXTENDS PP-119)

Anchor pointer: Research note Section 4.1 + Section 7, Anchor 3
Substrate-product reading: Extend PP-119 K-hop retrieval to return (answer, confidence, path) triples. Per-hop confidence = cleanup cosine score; chain confidence = product of per-hop scores (product-of-chain, correct under Path D per-hop Bayesian independence, empirically validated T2 45/45 cells). If per-hop confidence rho > 0.80 with actual accuracy, substrate provides uncertainty-propagating multi-hop reasoning -- directly addressing UProp LLM failure (arxiv 2506.17419).
Tier hint: CPU laptop, ~3-4 hr. Extension of PP-119 pipeline; requires Anchor 1 HARD_PASS or can run in parallel since the confidence chain mechanism does not directly require PP-155 (it uses cleanup cosine scores, not amplitude weights).
Why-now: PP-119 is already competitive on recall. The confidence chain is the differentiator that makes it categorically better than LLMs for uncertainty-propagating multi-hop reasoning. 2-day engineering. Direct head-to-head with LLMs possible on calibrated multi-hop Bayesian benchmark.

Pre-reg bands:
  HARD-PASS: rho (per-hop confidence vs accuracy) > 0.80 across confidence bins; depth-d mean_confidence within 15% of product-of-chain prediction
  MIDDLE-BAND: rho = 0.60-0.80 (useful signal but noisy)
  HARD-FAIL: rho < 0.50 (confidence scores uncorrelated with accuracy; product-of-chain claim invalid)

### Anchor 4: bayesian_evidence_accumulation_v1 (NEW CAPABILITY -- gates on Anchor 1)

Anchor pointer: Research note Section 2.2 + Section 7, Anchor 4
Substrate-product reading: Empirical test of the "binding accumulation as Bayesian posterior update" claim. Start with weak amplitude (prior), add n=1,2,5,10,20 independent evidence items encoded with log-likelihood amplitudes, measure posterior convergence to ground truth. If monotone + converges within 10 items, substrate performs Bayesian evidence accumulation algebraically -- not by training.
Tier hint: CPU laptop, ~2-4 hr. New script but moderate complexity. Gate: Anchor 1 HARD_PASS (requires PP-155 at production-grade).
Why-now: This is the direct empirical validation of the Product of Experts connection (Hinton 1999). If confirmed, substrate's Bayesian update capability is a first-principles claim with lit precedent.

Pre-reg bands:
  HARD-PASS: monotone confidence increase with n_evidence; product-of-experts approximation error < 0.05 vs exact Bayesian baseline at n=10
  MIDDLE-BAND: monotone but slow convergence (n > 20 for confident answer); still useful
  HARD-FAIL: non-monotone OR does not converge to ground truth (superposition is not product-of-experts for this encoding)

### Anchor 5: do_causal_uncertainty_v1 (EXTENDS PP-172 -- gates on Anchor 1 + PP-172)

Anchor pointer: Research note Section 3.2 + Section 7, Anchor 5
Substrate-product reading: Extend PP-172 do() counterfactual to track uncertainty through causal interventions. P(Y | do(X=x)) computed via substrate should match exact causal effect within 5% on a known ground-truth causal model. Combines causal structure (PP-172) with probabilistic weights (PP-155) for full causal Bayesian reasoning. This capability has no LLM equivalent at structural reliability.
Tier hint: CPU laptop, ~4-6 hr. Moderate engineering. Gate: Anchor 1 HARD_PASS + PP-172 HARD_PASS.
Why-now: PP-172 is validated. PP-155 N=32768 is the missing gate. If both are HARD_PASS, the combination -- causal intervention + uncertainty propagation + audit trail -- is a categorical product claim no LLM system can make.

Pre-reg bands:
  HARD-PASS: P(Y|do(X=x)) via substrate within 5% of exact causal effect across 10+ test interventions
  MIDDLE-BAND: 10-20% error (approximate causal reasoning; useful but not precise)
  HARD-FAIL: > 20% error OR non-monotone in intervention strength (causal + probabilistic combination does not work)

---

## Context pointers

- Research note: notes/research_drill_substrate_probabilistic_reasoning_5x_2026-06-08.md
- PP-155 cap_map row: notes/substrate_capability_map.md (search: PP-155 Continuous strength)
- PP-107 cap_map row: notes/substrate_capability_map.md (search: PP-107 Abstention ROC)
- PP-172 cap_map row: notes/substrate_capability_map.md (search: PP-172)
- PP-119 cap_map row: notes/substrate_capability_map.md (search: PP-119 KG K-hop)
- Path D per-hop Bayesian independence: notes/substrate_capability_map.md (search: per-hop Bayesian independence T2 45/45)
- LLM calibration failure lit: arxiv 2406.14986, arxiv 2506.17419 (in research note citations 1 and 2)

---

## Contract

exp_dev owns: anchor selection from ranked list above, experiment design (cell grids, N values, script authoring), smoke gate check, pre-reg formal filing, queue dispatch, post-ship remote verify.

Research owns: P_deflated estimates (in research note), HARD-PASS / HARD-FAIL threshold justification (in research note Section 9), next-drill routing if HF (Section 13).

Orchestrator owns: pause gate, cap_map updates on verdict, cross-anchor strategy decisions.

---

## Autonomy declaration

exp_dev may dispatch any anchor in this list without additional orchestrator confirmation, subject to:
1. Pause gate check (data/orchestrator_paused.flag)
2. Anchor ordering: Anchor 1 first (gates Anchors 4 and 5); Anchors 2 and 3 can run in parallel with Anchor 1
3. Smoke gate before full run per PROT-021
4. Pre-reg per envelope-fail-bands before dispatch
5. Local / CPU-only per feedback-cloud-only-when-absolutely-necessary; no cloud dispatch without explicit user authorization
