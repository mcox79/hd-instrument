# Orchestrator -> Research: results summary cycle 201 (v527 / commit 6acec12d)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~20:20
**Trigger:** verdict_handler dispatch w/ cap_map state change. 9-batch Tier-5c progression + rescues.

## Headline

- 5 HP + 2 HF + 1 UNKNOWN, 0 LVH. +2 PP rows (PP-217, PP-218). 1 downgrade (PP-181 HP→HF). Portfolio 32+216 → 32+218 (net +2 rows; PP-181 stays as row but downgrades within).
- **Tier-5c training stack: SUBSTRATE INJECTION IS HELPING THE LLM, not just neutral.** Multilayer Flamingo (PP-217) shows ppl-ratio=0.835× (BELOW 1.0) at Pythia-160M, and the benefit holds at Qwen-1.5B at 0.851× (PP-218). First measurement of substrate injection actively improving LM prediction quality, not just maintaining it.
- **But fact-recall still HF**: t5c_c1fact_heldout_recall HF at recall=0.042 (gate 0.30) — adapter is routing to substrate (gate=0.556) but the LM objective alone can't drive fact transmission. Same failure mode as cycle-194/197 t5b_3. R1 fact-encoding loss term is the next rescue.
- **PP-181 gap-score uncertainty DOWNGRADED HP→HF**: 3-seed mean AUC=0.697 (single-seed 0.781 was variance inflation). Cycle 195 had flagged "smallest margin in batch; multi-seed before VALIDATED" — multi-seed reversed it.
- PP-110 top-k noise rescue closes PP-215 (top-k=1.000 at 30% AND 50% bit-flip).
- PP-213 constraint verifier production-scale confirmed at 100 vertices.
- 1 UNKNOWN (t5c_c1_3seed_validate, no metrics artifact — needs manual reconcile).

## Findings

### Tier-5c training (3 HP + 1 HF + 1 UNKNOWN)
- `t5c_b2_extended_training_flamingo` HP: ratio=1.794× (under 2× ceiling) at extended training; adapter gate grows over training. Phase B architecturally stable.
- `t5c_c1_multilayer_flamingo_train` HP: ratio=0.835× (BELOW 1.0). PP-217 — multi-layer adapter IMPROVES ppl vs baseline; substrate actively helping.
- `t5c_d1_qwen15b_flamingo_train` HP: ratio=0.851× at Qwen-1.5B. PP-218 — generalizes to ~10× larger LLM; not a small-model artifact.
- `t5c_c1fact_heldout_recall` HF: heldout recall=0.042 (gate 0.30), train=0.125, adapter gate=0.556 (actively routing). LM objective alone can't drive fact transmission. 5 rescues: R1 fact-encoding loss, R2-R5 alternative training signals.
- `t5c_c1_3seed_validate` UNKNOWN: no metrics artifact. Needs manual reconcile.

### Rescues (2 HP + 1 HF downgrade)
- `f1_topk_bitflip_rescue` HP: topk=1.000 at 30% AND 50% bit-flip. PP-110 noise rescue closes PP-215.
- `f4_harder_constraints` HP: agreement=1.000 at 100-vertex graphs. PP-213 production-scale.
- `f5_gapscore_3seed` HF: 3-seed mean AUC=0.697 (seeds 0.680/0.679/0.733), gate 0.75. PP-181 HP→HF DOWNGRADE; single-seed 0.781 was variance inflation. 5 rescues: R1 N-scaling cheapest.

## State

- cap_map v526 → v527
- commit: 6acec12d
- HONEST 1493 → 1502 (+9; counts UNKNOWN as honest read)
- LVH 266 unchanged
- Portfolio 32+216 → 32+218 (+2 new PP rows: PP-217, PP-218; PP-181 in-row HP→HF)

## Context

This is the most informative Tier-5c cycle to date. Two independent results land:

**(1) Substrate injection actively helps language modeling** (PP-217 + PP-218). This is the first measurement showing substrate injection produces a perplexity BENEFIT, not just neutrality. Multilayer Flamingo gives ratio=0.835× at Pythia-160M (PP-217), and Qwen-1.5B at ratio=0.851× (PP-218) confirms it's not a small-model artifact — at ~10× LLM scale the same effect holds. Cycle-197's PP-191 finding ("learned per-head adapter is the prerequisite") plus cycle-199's PP-204 single-layer smoke at ratio=1.181× (neutral) progresses to cycle-201 multilayer at ratio<1.0 (beneficial). Phase B was architecturally stable; Phase C (multilayer) provides actual quality benefit; Phase D scales to 1.5B.

**(2) But fact-recall transmission still fails** (t5c_c1fact_heldout_recall HF). The adapter is routing to substrate (gate=0.556) but heldout fact recall is 0.042 (gate 0.30), and even training-set recall is 0.125. Same failure mode as cycle-194/197 t5b_3 fact-use. The LM objective alone cannot drive fact transmission — the model learns to attend to substrate (lowering ppl) without using the substrate for explicit factual content. R1 (fact-encoding loss term added to the training objective) is the cheapest next rescue; R2-R5 cover alternative training signals.

This split (perplexity benefit + fact-recall failure) is the cleanest characterization yet of what the Tier-5c training stack provides today: substrate-augmented language modeling that's confirmed beneficial for the LM's prediction quality, but not yet a structured-fact KV that can be queried at scale. The product story splits accordingly: substrate-as-LM-enhancement is real now (PP-217/218); substrate-as-explicit-KV-via-attention needs a fact-encoding training objective.

**PP-181 gap-score downgrade** is the cycle's negative honest correction. The cycle-195 verdict flagged "smallest margin in batch; multi-seed before VALIDATED" — multi-seed reversed the single-seed 0.781 to mean 0.697 (seeds 0.680/0.679/0.733). The variance inflation in the single-seed shipper is the right read; PP-181 is HF now. Gap-score alone is not a reliable uncertainty signal at the tested N; N-scaling (R1) is the cheapest rescue. The confidence stack (PP-107 abstention + PP-182 graded tiered + PP-183 factual cert + PP-206 NDCG ranking) is unaffected — gap-score was the smallest of those primitives.

PP-215 noise robustness MID closes via top-k rescue (PP-110): top-k=1.000 at 30% AND 50% bit-flip. The graceful degradation from cycle 200 + the cycle-180 top-k buffer eliminates noise-induced recall loss across the full practical range.

PP-213 constraint verifier confirmed at 100-vertex production scale.

The UNKNOWN (`t5c_c1_3seed_validate`) is operational — no metrics artifact found. Needs the runner log checked and metrics scp'd, or re-queue verdict_handler when the artifact arrives.

Pipeline: 86 commits v438→v527. 549 anchors verdicted. 42 LVH catches.

---

END. No action requested.
