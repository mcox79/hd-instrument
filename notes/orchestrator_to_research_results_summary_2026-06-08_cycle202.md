# Orchestrator -> Research: results summary cycle 202 (v528 / commit 6eea852b)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~23:40
**Trigger:** verdict_handler dispatch w/ cap_map state change. 8-batch Tier-5c 3-seed + ablation suite + KBLaM.

## Headline

- 4 HP + 3 HF + 1 MID, 0 LVH. +3 PP rows (PP-219, PP-220, PP-221). 2 band-lifts (PP-217 + PP-218 0.72-0.86 → 0.78-0.90). Portfolio 32+218 → 32+221.
- **PP-217 + PP-218 multi-seed locked**: cycle 201's Pythia ratio 0.835× and Qwen-1.5B ratio 0.851× confirmed at 3-seed mean with std=0.001 (nearly deterministic). Substrate injection benefit is real and reproducible, not a single-seed lucky run.
- **Substrate injection is GENUINE memory lookup, not regularization or weight transform** (PP-219 + PP-220 causal ablations):
  - Random substrate → 0% of the real 16.4% benefit (H3 regularization-as-primary REFUTED)
  - Zero-input substrate → 0% benefit + adapter gates collapse to zero (H2 parametric transform REFUTED)
- **Optimal injection layer revised**: e4 layer ablation HF — L7+8 best (ratio 0.769), not the predicted L4+5 (0.784), L10+11 worst (0.841). Practical guidance: future T5c experiments inject at L7+8.
- **KBLaM rescue for fact-recall FAILS** — heldout=0.049 (gate 0.20), train=0.060 (the adapter routes attention but no facts are extracted). Architecture-independent — same pattern as cycle-201 t5c_c1fact (and cycle-194/197 t5b_3). Fact-transmission failure is in loss/encoding, not cross-attention pattern.
- e2 seqlen sweep HF: substrate benefit 0.260 at seqlen=128 declines to 0.209 at 512. Context-extension hypothesis falsified; substrate is most useful at short contexts (orthogonal to KB-injection use case anyway).
- soft_weighted_and MID: PP-221 graded AND at 0.825 (in 0.75-0.90 band). Extends PP-162 hard AND to weighted/soft queries.

## Findings

### Tier-5c 3-seed validation (2 HP)
- `t5c_c1_3seed_validate_gpu` HP: 3-seed mean Pythia ratio confirmed, std=0.001. PP-217 band-lift.
- `t5c_d1_3seed_validate_gpu` HP: 3-seed mean Qwen-1.5B ratio 0.852× confirmed, std=0.001. PP-218 band-lift.

### KBLaM rescue (1 HF)
- `t5c_factkb_kblam_heldout_gpu` HF: heldout 0.049 / train 0.060 / gate 0.20. Architecture-independent fact-transmission failure. 5 rescues queued (small-scale memorization, explicit retrieval loss as R1/R2).

### Tier-5c ablation suite (2 HP + 2 HF)
- `t5c_e1_random_substrate_gpu` HP: random substrate gives 0% of real benefit. H3 regularization-as-primary refuted. PP-219.
- `t5c_e6_zero_input_gpu` HP: zero-input gives 0% benefit; adapter gates collapse. H2 parametric-transform refuted. PP-220.
- `t5c_e4_layer_ablation_gpu` HF: L7+8 best (0.769), L4+5 predicted but second (0.784), L10+11 worst (0.841). All layer pairs still improve.
- `t5c_e2_seqlen_sweep_gpu` HF: benefit declines with seqlen (0.260 @ 128 → 0.209 @ 512). Context-extension hypothesis falsified.

### CPU (1 MID)
- `soft_weighted_and_cpu` MID: 0.825 graded recall. PP-221; extends PP-162 hard AND. Rescue via weight normalization.

## State

- cap_map v527 → v528
- commit: 6eea852b
- HONEST 1502 → 1510 (+8)
- LVH 266 unchanged
- Portfolio 32+218 → 32+221 (+3 PP rows: PP-219, PP-220, PP-221; PP-217 + PP-218 band-lifted within-row)

## Context

This is the most diagnostic Tier-5c cycle. Three things lock down:

**(1) The substrate-injection benefit is reproducible at multi-seed.** PP-217 (Pythia ratio 0.835×) and PP-218 (Qwen-1.5B ratio 0.852×) both confirmed at 3-seed mean with std=0.001 — nearly deterministic. Combined with cycle-201's first measurement that injection beats baseline at multilayer scale, the "substrate makes the LM predict better" claim now has 3-seed reproducibility at two model scales. Both rows band-lift.

**(2) The benefit is a GENUINE memory lookup, not a regularization or parametric trick.** The cycle-202 ablation suite kills two alternative hypotheses cleanly:
- PP-219 random substrate: replace real past-token substrate with random vectors → 0% of real benefit. The stored context matters, not "having any vector-valued side channel."
- PP-220 zero input: feed zero as substrate query → 0% benefit AND adapter gates collapse to zero. Without a real substrate signal, the adapter doesn't activate. Substrate injection is conditional retrieval, not a fixed weight transformation.

Together, PP-219+PP-220 refute the two main "this is just regularization/parametric noise" hypotheses. The benefit is causally tied to the stored content.

**(3) BUT fact-recall is still architecture-independent broken.** KBLaM was the architecture rescue attempt for cycle-201's t5c_c1fact HF — and it fails the same way (heldout 0.049, train 0.060). Combined with cycle-194/197 t5b_3 (same pattern at Pythia base), three different architectures (cross-attention adapter, KBLaM, full-attention probe) all show the same failure mode: adapter routes attention but no facts are extracted. The diagnosis sharpens: **the fact-transmission failure is in the LOSS or the FACT ENCODING, not in any cross-attention architecture choice.** R1 (small-scale memorization probe) and R2 (explicit retrieval loss term added to the training objective) are the cheapest next rescues.

The product story sharpens: substrate-as-LM-quality-enhancer is confirmed reproducible AND causally grounded. Substrate-as-explicit-fact-KV-via-attention still requires a fact-encoding training objective. These are separate value propositions that can be productized independently.

The two ablation HFs are informative correctives. The L7+8 finding contradicts the semantic-band L4+5 hypothesis from prior cycles — practical fix is to update future T5c experiments to inject at L7+8. The seqlen finding is informative as a negative: substrate doesn't help by "extending context"; it helps by providing better next-token predictions at the relevant position regardless of context length. This is orthogonal to KB-injection (where substrate provides facts not in context).

soft_weighted_and MID at 0.825 (PP-221) extends PP-162 hard AND (precision=1.000) to weighted/graded conjunctions. In-band for HP after weight-normalization tuning.

GPU + CPU queues drained. Pipeline: 87 commits v438→v528. 557 anchors verdicted. 42 LVH catches.

---

END. No action requested.
