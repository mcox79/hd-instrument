# exp_dev -> Research: BTSP sequence-learning v1+v2 BOTH HARD_FAIL -- additive Hebbian ALREADY solves order-binding (capability there; BTSP wrong mechanism for this task class TOO)

**From:** exp_dev (Opus 4.7 agent spawn)
**To:** Research (Director)
**Date:** 2026-06-27 ~17:32 PDT
**Topic:** USER-directed BTSP for "tall stand vs stand tall" language order — full ship + verdict

---

## TL;DR (1 line)

Two cells shipped today on the RIGHT task class per drill Angle B; **additive Hebbian already does order-sensitive sequence binding at 1.000 recall** (substrate has the capability), and **BTSP binary-flip catastrophically collapses (0.030 recall) at substrate's sparse regime even on this RIGHT task class**. Closes the BTSP arc; opens an honest "substrate already has Stage-3 order-sensitive binding via additive" capability claim.

---

## CELLS SHIPPED

| cell | smoke verdict | BTSP order_disc | Additive order_disc | finding |
|------|---------------|-----------------|---------------------|---------|
| `btsp_sequence_learning_one_shot_word_pair_v1` | HARD_FAIL (saturation) | 1.000 | 1.000 | fresh-W per pair = trivial; all arms saturate |
| `btsp_sequence_learning_one_shot_word_pair_v2` | HARD_FAIL (saturation + BTSP collapse) | 0.020 | 1.000 | shared-W; additive STILL trivial; BTSP collapses to noise |

Both committed (1e2241c6 + 2b75c381) + smoked on overnight_queue GPU runner. v1 self-test PASS in 3.3s; v2 self-test PASS in 3.3s. Smoke metrics in `data/exp_btsp_sequence_learning_one_shot_word_pair_v{1,2}_smoke/metrics.json` on remote.

## V2 SMOKE NUMBERS (honest re-read off per_seed, not just verdict_msg)

- Regime: N=2048, V=200, N_PAIRS=50 -> 100 bindings into ONE shared 2048x2048 W (load = 100 / 2048 = 0.049).
- `additive_hebbian`: recall_correct=1.000, cross_order_confusion=0.000, **order_disc=1.000** (perfect; substrate trivially solves).
- `random_tag_50pct`: recall_correct=1.000, **order_disc=1.000** (50% random tagging also trivially solves; control showing "any storage that touches synapses" works at this load).
- `btsp_sparse_tag_5pct`: recall_correct=0.030, cross_order_confusion=0.010, **order_disc=0.020** (collapse to noise; binary-W at fp=0.005/fq=0.0025 doesn't establish enough signal to retrieve).
- `btsp_sparse_tag_paired_reward`: recall_correct=0.000, **order_disc=0.000** (paired-reward gate fires; but the gate adds restriction on top of an already-broken arm).

Diagnostic arm (vary atom orthogonality at BTSP_5PCT) on v1 confirmed mechanism is well-formed: ortho atoms 0.95, partial 0.45, identical 0.0 — the testbed isn't broken, the BTSP storage rule is.

## HONEST INTERPRETATIONS (per Fix #28 + Step 0 discipline; do not over-claim)

**Finding A (load-bearing positive):** **substrate already has order-sensitive one-shot sequence binding at 1.000 recall at this regime via plain additive Hebbian + roll-position binding + random HD context tags.** "tall stand" vs "stand tall" IS distinguished by argmax(W @ S, all 2*N_PAIRS contexts). This is a Stage-3 capability that does NOT require BTSP. The substrate's existing primitives (HRR-style position-bind via torch.roll + Hebbian outer-product storage + cosine readout against a context bank) are sufficient.

  - Caveat: this is at LOW load (100 bindings into 2048-dim W; alpha=0.049). At higher load (the FULL regime would be 400 bindings into 16384-dim W; alpha=0.024 — actually LOWER alpha at full because N grew faster than N_PAIRS), additive should remain easy. The DISCRIMINATING REGIME for additive's breakdown is much higher alpha; **a future N_PAIRS-sweep cell could find where additive itself collapses, then test if BTSP or another mechanism rescues at THAT regime.**

**Finding B (load-bearing negative):** **BTSP binary-flip mechanism at Wu-Maass spec (fp=0.005, fq=0.0025) does NOT work for substrate's sequence-binding task class at substrate-default scale.** Even with the RIGHT task class (per drill Angle B reframing), binary-W collapses to noise because the read-signal is buried — at fp=0.005, each S is sparsified to ~10 active positions; tagging top fq=0.0025 of 4M synapses ~10000 synapses per binding × 100 bindings = scattered binary flips that don't aggregate coherently into a recoverable signal via `W @ S`. Convergent with earlier BTSP-binary HARD_FAILs at prototype-classification (drill Angle A1 sparse regime sweep is therefore unlikely to rescue at this task class either; the issue is binary-W's information bandwidth in HD substrate, not just the input sparsity).

**Finding C (META-finding):** **smoke discriminator survival is harder than expected when the BASELINE arm is the trivial-solver.** v1 smoke caught ALL arms at saturation; v2 redesign at higher load STILL has additive at saturation. For BTSP to discriminate against additive, we'd need a regime where ADDITIVE fails first (capacity > additive ceiling) — but at THAT regime, BTSP's binary-W is likely to fail too because binary noise grows faster than the signal. This is consistent with binary-synapse literature: binary-W's regime of advantage is robustness under perturbation at fixed capacity, NOT capacity-extension.

## RECOMMENDATIONS

**1. Close the BTSP-binary arc as HONEST_NEG for this substrate class.** Two task classes (prototype-classification, sequence-binding) × multiple sparse-regime probes consistently show BTSP binary-W collapses. The drill's Angle A sparse-regime sweep can still ship for completeness (TOP-2 `btsp_binary_synapse_v3_sparse_regime_swept` per drill), but I suspect it'll find the same.

**2. Atomize finding A as a substrate capability**: "substrate has one-shot order-sensitive sequence binding at load alpha=0.049 via additive Hebbian + position-binding + context-tag retrieval" — this is the Stage-3 capability USER asked about ("tall stand vs stand tall"), and we have it. NOT via BTSP, but via the substrate's existing primitives.

**3. Open a NEW drill: discriminating-regime for additive's order-binding breakdown.** When does additive collapse on this task class? Sweep N_PAIRS / N_DIM to find the capacity cliff. THAT regime is where mechanism comparison (additive vs STC vs hierarchical-W vs BTSP-on-the-rescue) becomes scientifically meaningful. The drill's TOP-1 STC cell is well-positioned for THAT regime.

**4. Honest USER framing**: substrate already has the capability USER asked about. BTSP was the WRONG mechanism but USER's intuition about "scoring word weight based on order" is correct — the substrate does score order via position-binding, just not via BTSP's tagging. The exciting next step is finding WHERE additive breaks down and what mechanism rescues it there (not pushing BTSP through more regimes).

## SUSPECTED FOLLOWUPS (queue when Research approves)

- (optional, scientific-completeness) ship `btsp_binary_synapse_v3_sparse_regime_swept` per drill TOP-2 to formally close BTSP-binary at the prototype-classification task class.
- (recommended, Stage-3 capability scour) ship `additive_hebbian_sequence_binding_capacity_cliff_sweep_v1` -- sweep N_PAIRS in {50, 100, 200, 500, 1000, 2000, 5000} at N=16384 to find additive's order-disc collapse; this gives us the operational capacity envelope for substrate's existing sequence-binding capability.
- (drill TOP-1 follow-through) ship STC at the cliff regime once we know where it is.

## FILES

- `experiments/exp_btsp_sequence_learning_one_shot_word_pair_v1.py` (commit 1e2241c6)
- `preregs/2026-06-27_btsp_sequence_learning_one_shot_word_pair_v1.md`
- `experiments/exp_btsp_sequence_learning_one_shot_word_pair_v2.py` (commit 2b75c381)
- `preregs/2026-06-27_btsp_sequence_learning_one_shot_word_pair_v2.md`
- Remote metrics: `marsh@home:C:/dev/hd-instrument/data/exp_btsp_sequence_learning_one_shot_word_pair_v{1,2}_smoke/metrics.json`

-- exp_dev
