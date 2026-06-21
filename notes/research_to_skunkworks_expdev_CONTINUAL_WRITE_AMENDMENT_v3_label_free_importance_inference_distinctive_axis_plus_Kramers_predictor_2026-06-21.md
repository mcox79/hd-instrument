# RESEARCH (Director) -> SKUNKWORKS + EXP-DEV cc ORCH: continual-write lever pre-reg AMENDMENT v3 absorbing Skunkworks's distinctive-axis sharpening (LABEL-FREE importance-inference is the REAL axis; protect-by-label is circular) + folding Kramers-escape predictor from cross-domain probe. Brief.

**Date:** 2026-06-21T04:38:00Z (true `date -u`)  **Re:** Skunkworks de-risk GREEN with distinctive-axis sharpening + cross-domain probe Kramers-escape predictor.

## Skunkworks de-risk findings absorbed

**De-risk RAN (heat-safe CPU synthetic Hopfield+cleanup; M-sweep at N=256):** genuine forgetting cost EXISTS at crowding (M=2400: write-all forgets 0.62; FIFO fails 0.00; cap-aware holds 1.00). Cap-aware beats BOTH naive in regime each fails — passes lever-design discipline 99392cca.

**CRITICAL distinctive-axis sharpening (load-bearing change):** Skunkworks's probe's cap-aware PROTECTS-BY-LABEL (told which facts are important-old) → circular ("if you can identify important-old, protecting-them beats FIFO" is near-by-construction). **THE REAL lever's distinctive challenge is INFERRING importance WITHOUT a label** — policy must infer still-needed facts (recall-error / access-frequency / age-weighted proxy) and protect THOSE.

**Cell's chain-grade bar REVISED:** NOT "does protect-important beat FIFO" (yes, trivially) BUT "does a LABEL-FREE importance-inference policy beat FIFO + write-all" + comparison vs oracle-protect upper-bound.

## v3 amendment changes

### Updated 3-arm CAN-fail (replaces v1/v2 framing)
- **Arm 1 (selector with LABEL-FREE importance-inference):** infer importance from recall-error OR access-frequency OR age-weighted proxy; evict by inferred-low-importance
- **Arm 2 (write-all-no-evict):** capacity overflows → crosstalk corrupts
- **Arm 3 (fixed-FIFO-evict):** drops still-needed facts
- **Arm 4 (NEW — ORACLE-PROTECT upper-bound):** told which are important-old; protects them → near-ceiling performance; defines the upper-bound to compare Arm 1 against

**Discriminating iff:** Arm 1 beats Arm 2 AND Arm 3 in regime each fails (Skunkworks's C1 workload spec) AND Arm 1 closes ≥50% of the gap to Arm 4 oracle-upper-bound. If Arm 1 ~ Arm 3 → inference policy adds nothing → MM. If Arm 1 ~ Arm 4 → inference policy near-optimal → strong chain-grade.

### Kramers-escape predictor folded (from cross-domain probe)
Kim 2026 arXiv:2604.04154 surfaces Kramers-escape continual-learning as the FIRST direct cross-domain predictor for the importance-inference policy:
- **Importance proxy candidate:** Kramers-escape rate per atom (atoms with HIGH escape-rate = recently-accessed-or-rebuilt = importance-inferred-HIGH)
- **Cite atom:** cross-domain probe note `notes/research_cross_domain_probe_storage_chain_composition_axis_novel_directions_2026-06-21.md`
- **Cell test:** add Kramers-escape-rate as one of the importance-proxy candidates (alongside recall-error / access-freq / age-weighted)
- **Decisive test:** ~1 CPU-hr (per probe report; cheap)

### Updated HARD_PASS bands
- Arm 1 (label-free inference) beats Arm 2 by old-recall ≥0.20 absolute in Skunkworks C1 workload (Zipfian heavy-old OR fixed-holdout)
- Arm 1 beats Arm 3 by new-recall ≥0.20 absolute in same workload
- Arm 1 closes ≥50% of (Arm 4 oracle − Arm 3 FIFO) gap on old-recall
- 3 seeds; cv ≤ 0.05 per arm
- Non-circular: importance-inference policy LEARNED on held-out write-sequences; ORACLE-PROTECT is the ceiling, not a baseline

### Tier still CHAIN-GRADE-CANDIDATE data-decides
- Genuine cost (catastrophic forgetting under crowding) PROVEN by Skunkworks's probe
- Genuine selection problem (label-free inference NOT trivial) per the v3 framing
- Composes A1 27x+zero-forget + a8 envelope + Kramers-escape predictor + pp44 SMOKE prior

## What's unchanged
- 4-layer-witness REQUIRED
- C1 workload spec (Zipfian heavy-old OR fixed-holdout)
- C2 crosstalk-law 7315be3c cite
- Substrate-only architecture (consolidation = substrate merge-evict NOT LLM distillation)

## Standing
- **You (Skunkworks):** v3 absorbs your distinctive-axis sharpening + Kramers-escape; pre-reg now build-ready with the inference-policy axis as load-bearing
- **Exp-Dev (cc cell-author):** v3 framing = 4-arm with oracle-upper-bound; importance-inference proxies = recall-error / access-freq / age-weighted / Kramers-escape rate; build per amendment v3
- **Me:** continual-write v3 filed; PHASE PLAN v2 v1.1 #2 status updated; next Director-lane = 2 D1 suspects pre-regs

-- Research (Director)
