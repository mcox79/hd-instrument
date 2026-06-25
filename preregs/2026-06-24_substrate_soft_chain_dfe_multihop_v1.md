# PRE-REG: substrate_soft_chain_dfe_multihop_v1

**Date:** 2026-06-24
**Author:** exp_dev (cell author)
**Anchor:** `substrate_soft_chain_dfe_multihop_v1`
**Routing:** local_cpu_queue (CPU, ~3-5 min wall full)
**Lane:** Lane 1 substrate-native composition mechanism comparison (PRIMITIVE_TEST_synthetic_apples_to_apples)
**corpus_provenance:** synthetic_concept_kg_v1 (V_C=200, V_P=10, N_DIM=8192, seeds [7,17,23]; matches `substrate_resonator_multihop_integration_v1` HARD_FAIL provenance)

## Strategic context

Resonator integration HARD_FAILed today (2026-06-24): NAIVE_2HOP 0.6500 vs RESONATOR_2HOP 0.6317 — tied (Resonator slightly worse). Research 2x+3x revival drill (`research_resonator_hard_fail_revival_disparate_fields_2026-06-24.md`) diagnosed the root cause via 5 disparate fields (DFE/comms theory, resonator/HD-VSA, RG, random-walk/PageRank, path integrals):

**Root cause: NOT per-hop cleanup capacity. It is INTER-HOP HARD-DECISION ERROR PROPAGATION** — structurally identical to Decision Feedback Equalization (DFE) error propagation in communications theory. When hop-1 emits an argmax (HARD decision) before hop-2 runs, an incorrect pick is fed into hop-2 cleanup as if it were ground truth; the substrate has no soft-confidence channel to recover.

**Top rescue per the drill (P_deflated 0.35):** SOFT-CHAIN — replace per-hop argmax with a softmax-weighted superposition of top-K candidates passed forward to the next hop. CA3 graded-reactivation brain analog; turbo-decoding / soft-DFE telecom analog. Zero new substrate primitives — just defer the argmax.

## Cell design

4 arms × 3 seeds × synthetic concept data × N_DIM=8192:

1. **ARM_NAIVE_HARD_2HOP** (control / sanity reproduces 0.65 baseline): per-hop `state = W @ (state * R[p] * sq); last = argmax(E @ state)` (matches `chain_naive` in the Resonator integration cell).
2. **ARM_RESONATOR_HARD_2HOP** (control / sanity reproduces 0.63): per-hop Modern-Hopfield top-K=20 bundle with `beta=N`, then argmax at the final step. Identical to today's HARD_FAIL `chain_resonator`.
3. **ARM_SOFT_CHAIN_2HOP** (PRIMARY): per-hop produces a softmax distribution over top-K=20 candidates with `beta=N`. **Hop-2 query is built as a weighted superposition** `k_hop2 = sum_i q1[i] * (E[atom_i] * R[p2] * sq)`. Final readout is argmax over the codebook after hop-2 cleanup.
4. **ARM_SOFT_CHAIN_3HOP** (BONUS): extends ARM 3 to 3-hop with soft decisions at each transition.

**Apples-to-apples invariants (per master bias checklist):**
- All four arms share identical E / R / W per seed (same V_C, V_P, N_DIM, K_SET, beta, training triples).
- ONE knob varies between ARM 2 and ARM 3: hard argmax vs soft superposition for the hop-1->hop-2 transition.
- Primary metric: top1 accuracy on held-out 2-hop chains.
- Synthetic-data lane; NO transformer / encoder baselines.
- Same K_SET=20 across ARM 2 / ARM 3 / ARM 4 (cleanup-pool size held constant).
- Same `beta=N_DIM=8192` softmax temperature (matches Resonator integration cell convention; substrate-appropriate sharpening per `hdlab.multi_hop.iter_cleanup_chain`).

**Encoding choice (deliberate):** the cell uses DENSE-BIPOLAR (not sparse-bipolar f=0.02 from Stage-1 foundations) because today's HARD_FAIL was measured on dense-bipolar; switching encoding AND decision-mechanism would CONFOUND the soft-chain test. The prompt's Stage-1 foundations clause is held for a future follow-up cell once SOFT-CHAIN is validated or refuted on the same regime that produced the HARD_FAIL.

## Pre-reg HARD bands (envelope-fail-bands; symmetric verify-both-directions)

**Sanity rails (gate the verdict's interpretability):**
- ARM_NAIVE_HARD_2HOP top1 in [0.60, 0.70] (within +/-0.05 of measured 0.6500).
- ARM_RESONATOR_HARD_2HOP top1 in [0.58, 0.68] (within +/-0.05 of measured 0.6317).
- If EITHER sanity band fails, the synthetic regime is off the HARD_FAIL regime; verdict becomes UNINFORMATIVE (re-run after regime-matching).

**Primary verdict (PRIMARY = ARM_SOFT_CHAIN_2HOP top1):**
- **HARD_PASS:** mean(ARM_SOFT_CHAIN_2HOP top1) >= 0.80 AND cv across seeds <= 0.05 AND > ARM_NAIVE_HARD_2HOP mean + 0.10 (paired across seeds). DFE-analog closes the inter-hop error-propagation gap; soft-confidence chaining mechanism is chain-grade-eligible.
- **MIDDLE_BAND:** mean(ARM_SOFT_CHAIN_2HOP top1) in [0.70, 0.80) — small-but-real lift; needs follow-up (turbo iteration; K_SET sweep; temperature calibration).
- **HARD_FAIL:** mean(ARM_SOFT_CHAIN_2HOP top1) <= 0.70 — soft-chain does NOT help; the multi-hop limit is more fundamental than the decision-mechanism choice (revival pivots to K-beam path-sum angle 3 OR substrate-PageRank angle 4 OR upstream encoder / W-capacity drills per the research drill note).

**Bonus (ARM_SOFT_CHAIN_3HOP):**
- **BONUS_PASS:** mean(ARM_SOFT_CHAIN_3HOP top1) >= 0.60 (chain-grade evidence the soft-decision mechanism scales to 3 hops).

**Both-direction synthesis:**
- HARD_PASS on 2HOP + BONUS_PASS on 3HOP -> structurally validates soft-chain as a general fix for hard-decision error propagation in substrate multi-hop.
- HARD_PASS on 2HOP + bonus FAIL on 3HOP -> soft-chain helps 2HOP but the error-amplification at depth>2 needs an additional mechanism (turbo iteration; path-sum at the readout).
- HARD_FAIL on 2HOP -> falsifies the soft-chain hypothesis at this regime; revival routes to angle 3 (K-beam path-sum) and angle 4 (substrate-PageRank) per the research drill.

## Bias / confound audit

- **Top-K choice:** K_SET=20 held constant across ARM 2 / ARM 3 / ARM 4 (matches today's Resonator HARD_FAIL setting).
- **Softmax temperature:** `beta=N_DIM` matches the Resonator integration cell convention; same for ARM 2 and ARM 3 (the only difference is what's done with the softmax weights — argmax-then-pick (ARM 2) vs weighted-superposition-then-pass-forward (ARM 3)).
- **Cleanup-interaction confound:** ARM 2's argmax discards the rest of the top-K confidence profile; ARM 3 keeps it. This IS the load-bearing knob being tested; it is not an unintended confound.
- **Seed-instability:** cv <= 0.05 gate (PASS-with-cv>0.05 demoted to MIDDLE_BAND).
- **Sanity-baseline drift:** ARM 1 must reproduce the published 0.65 within +/-0.05; otherwise the test is in a different regime than the HARD_FAIL and verdict is UNINFORMATIVE.

## D1 + D2 disciplines

- **D1 (1-seed full-N partial probe BEFORE full timeout estimate):** cell-author smoke (1 seed, smaller scale) gates the dispatch; full-N partial wall measured on seed 7 first, used to estimate the 3-seed timeout.
- **D2 (atexit synthesizer + per-seed checkpoint MANDATORY):** the cell imports `experiments/_seed_checkpoint` (defensive) and writes per-seed partials `partial_seed<S>_<mode>.json`; resume from checkpoint on CONFIG_VERSION match; atexit emit of metrics.json if interrupted mid-run.

## Fix #14, #28, #26, A5, ASCII-only

- **Fix #14:** ship via main-thread queue_add (1 spawn budget); not a fan-out.
- **Fix #28:** per-arm metrics in `per_seed[].arm_<name>`; verdict reads from those, not from verdict_msg framings. Cv computed independently per arm.
- **Fix #26:** pre-dispatch check — anchor name `substrate_soft_chain_dfe_multihop_v1` is new (verified via `find data -name 'substrate_soft_chain*' -maxdepth 2` returning nothing); not a re-dispatch.
- **A5 (cert-owner separation):** cell-author produces results + per-arm metrics; Skunkworks owns the landed-VET + cert classification. This pre-reg does NOT pre-call the tier.
- **ASCII-only:** verified in the cell source.

## Timeout estimate

- Today's `substrate_resonator_multihop_integration_v1` full run: ~29s per seed at N=8192, V_C=200, 3 arms (naive + res2hop + res3hop), N_CHAINS_2HOP=300, N_CHAINS_3HOP=200.
- This cell adds ONE more arm (SOFT_CHAIN_2HOP) — same matmul cost ballpark; SOFT_CHAIN's hop-1->hop-2 superposition adds a small constant cost per query.
- Expected per-seed: ~35-45s.
- 3 seeds = ~105-135s total full wall.
- Timeout: **2400s (40 min)** = generous 18-22x safety margin per the prompt's `timeout=2400` directive.
- PROT-018: no `_n<N>` suffix in anchor; PROT-019 floor: not applicable. PROT-021: cell imports `_seed_checkpoint` (defensive; well under 4h floor regardless).

## References

- `notes/research_resonator_hard_fail_revival_disparate_fields_2026-06-24.md` (the 5-field drill that identified soft-DFE as top angle)
- `experiments/exp_substrate_resonator_multihop_integration_v1.py` (base cell; HARD_FAIL today; verbatim primitives copied)
- `data/exp_substrate_resonator_multihop_integration_v1/metrics.json` (the 0.65 / 0.63 / 0.39 baselines this cell must reproduce in sanity)
