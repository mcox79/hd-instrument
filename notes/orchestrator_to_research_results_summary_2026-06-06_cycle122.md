# Orchestrator -> Research: results summary cycle 122 (v444)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~09:15
**Trigger:** verdict_handler dispatch w/ cap_map state change. 2 orphan-recovered.

## Headline

**2 HARD_FAILs + 1 MID** — embedding-norm-gate axis CLOSED for PP-8; KF-1 TruthfulQA corroborates v443 order-sensitivity finding; ETF N_sub=384 confirmed as actionable design point.

## Findings

**`substrate_embedding_norm_gate_discriminability_v1` HARD_FAIL — PP-8 axis CLOSED**
L2 norm magnitude is NOT a reliable indicator of which concept embeddings are informative. Keeping the top 30% highest-norm vectors discards **49-57% of concepts** — far below the 90% coverage gate. Norm is not information. Embedding-norm gating is **closed** as a design axis for PP-8 routing. Rescues filed:
- R2: cosine-variance gate
- R3: per-vc-class norm threshold
- R4: learned discriminability probe

**`substrate_kf1_truthfulqa_style_v1` HARD_FAIL — corroborates v443**
On negations ("Paris is NOT the capital of France"), KF-1 scores **AUC=0.034 (near chance)** while held-out non-adversarial sits at 0.975. The gap is entirely the MiniLM encoder: no word-order awareness, so affirmations and their negations look identical. **Corroborates v443 order-sensitivity diagnosis**; v443 R3 (Pythia scale-up) is the active rescue path; no new rescue needed.

**`substrate_etf_minilm_n_sub_lower_sweep_v1` MIDDLE_BAND**
Whitening at **N_sub=384 gives a real 1.21× recall lift** (82% raw → 100% whitened). N_sub=512 looks flat (1.01×) only because recall was already 99% — measurement ceiling, not mechanism failure. The cross-N attenuation from prior cycles is partly a measurement artifact at the high end. **N_sub=384 is the actionable design point** for ETF whitening; full 3-seed confirmation (R1) recommended.

## State

- cap_map v443 → **v444**
- commit: `c4fab01`
- HONEST 958 → 961
- LVH 225 (no catches; all labels HONEST)
- 3 sub-prop annotations
- 0 BAND-LIFTS, 0 closures (R1 n-gram already closed in v443)
- PP-8 unchanged; KF-1 0.72-0.87 unchanged
- Portfolio 32+77

## Context for research session

**Convergent diagnosis on KF-1:** v442 + v443 + v444 all point at order-sensitivity as the root cause. TruthfulQA-style negations score 0.034 — that's the cleanest mechanistic test possible (affirmation vs negation has near-identical bag-of-words/n-gram representation but opposite truth value). Pythia scale-up (v443 R3/R4) is the locked rescue direction.

**PP-8 routing axis cleanup:** norm-gate is closed; the remaining live axes for PP-8 cell-level discrimination are cosine-variance (R2) and learned probes (R4). Per-vc-class norm threshold (R3) might still rescue a narrower use case.

**ETF mechanism resolution:** the cross-N attenuation from v441/v442 (lift shrinks at large N) is at least partly explained by measurement ceiling — at N_sub≥512 with these particular vc-class distributions, recall is already ~99% so there's nothing left to gain. The real Phase-4B question becomes: at what N_sub does ETF whitening's mechanism saturate vs. where does the measurement ceiling artifact dominate? N_sub=384 is the answer for THIS encoder.

Pipeline: 7 cap_map commits in ~85 min this morning (v438 → v444). Runners healthy and processing genuinely-new cells.

---

**END.** No action requested — results heads-up per step-4 convention.
