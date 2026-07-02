# Proposal — M3 cortex three-signal confidence architecture

**Filed:** 2026-07-02 mid-afternoon (post-restart session)
**Status:** strategic proposal; USER go/no-go on scope + sequencing
**Emerged from:** research 2x drill on h4 HF revival (a66bd7d45ff1f408d) + skunkworks h4 audit (a135cce573fd8410c)

## ⚡ UPDATED — SECOND DRILL LANDED 2026-07-02 ~16:20 UTC — REBRAND TO 4-SIGNAL

Second drill (abe94cac) landed ~14 min after first drill (ac7fa91). Both consistent at high level; abe94cac much more thorough (418 lines, 35 external + 7 substrate-KB citations, explicit Bayes-floor math). **Where they diverge, abe94cac wins.**

**Key upgrades vs ac7fa91:**
- **Bayes-floor exact match:** (μ,σ)=(0.622, 0.005) → Δ≥2.72e-3 for AUC=0.65; observed Δ≈8e-4 → AUC=0.545 hits Bayes-floor exactly. NO threshold tune recovers signal.
- **K_eff=60/(1+59·0.6)=1.65** — INTRA_COS=0.6 destroys 97% of √60 SNR gain. Density-family fundamentally can't work at h4-harness INTRA_COS.
- **Cross-study convergence at AUROC 0.55-0.65 at p≤5%** (Zou USENIX-Sec 2025 / Cleanlab 2024 / Farquhar Nature 2024) — h4/h4b hit literature wall exactly where predicted
- **Iteration-count subclass DEAD** per dense-Hopfield saturation; use first-step ΔE + σ_max(J) instead
- **REBRAND to 4-signal:** add stochastic-consistency as 4th orthogonal signal — **directly aligns with USER-LOCKED 2026-06-30 M3-cortex-must-inject-stochastic-noise-at-boundary directive**

**4-signal architecture:**
| Signal | Observable | Nature | Cell |
|---|---|---|---|
| Post-hoc | isotonic-calibrated cleanup margin | statistical | lap3_12 (in flight; rewrite w/ isotonic) |
| Spatial | top-1 vs top-2 gap | geometric | h4b (HF'd in current regime; needs redesign probe) |
| Dynamical | first-step ΔE + σ_max(J) | dynamical | new cell (NOT iteration-count; dead) |
| **Stochastic** | multi-sample predictive-entropy under N_perturb∈{1,8,16,32}, σ_input=0.05 | stochastic | **`lane_x_prime_stochastic_consistency_predictor_v1`** (top P_CG=0.42) |

**Recommended next cells (from abe94cac):**
1. **`lane_x_prime_stochastic_consistency_predictor_v1`** — h4-harness unchanged; N_perturb∈{1,8,16,32}, σ_input=0.05; continuous predictive-entropy scalar (NOT vote-count per ACL 2025); full-N=3600 preview smoke gate ≥0.55 (discriminator-must-survive-scale). This is the primary next spawn.
2. **`h4b_regime_redesign_probe_v1`** — parallel cheap: 6-arm intra_cos × p sweep; HARD_PASS Arm D at intra_cos=0.3+p=0.10 ≥0.68; disentangles regime-vs-mechanism verdict drivers (below).

**Verdict on original 3 signals:**
- **Post-hoc (lap3_12) — PROCEED unchanged** (in flight; both drills agree)
- **Spatial (h4b) — HF'd at h4-harness; alternatives available at reframed regime** (per h4b_regime_redesign_probe_v1)
- **Dynamical — subclass DEAD (iteration-count) but survives via first-step ΔE + σ_max(J)** (new mechanism)
- **Stochastic — NEW top pick (P_CG=0.42; aligns with USER-locked stochastic-noise-at-boundary)**

**Verdict — BOTH regime confound AND geometry-family mechanism limit.** Both drivers real; disentangled by h4b_regime_redesign_probe.

## ⚠️ SUPERSEDED — original 3-signal framing below (kept for history)

## ✅ REGIME DRILL VERDICT — added 2026-07-02 ~15:45 UTC after research drill ac7fa91 returned (superseded by 2nd drill above)

**Verdict: REGIME_CONFOUND (primary) + MECHANISM_LIMIT (secondary for geometry-family).**

Full note: `d:/AI/hd-instrument/notes/research_h4_harness_regime_vs_mechanism_drill_2026-07-02.md` (~230 lines).

**Fisher-discriminant proof:** empirical gap_std=0.0048 → d'≈0.16 (essentially overlapping distributions). AUC=0.70 would need μ-shift ≥ 0.0036, but per-item contamination shift under INTRA_COS=0.6 is ~0.0008 by geometry — **below floor by construction, not mechanism failure**.

**Literature grounding:** geometric-observable class works at 10-30% contamination (Sun 2022, Hendrycks 2017); sub-5% needs non-geometric signals (Carlini 2021 direct-memorization).

**Actionable decisions locked:**
1. **Lane X (dynamical) — PAUSE.** Dense-HF saturation + shared ridge geometry → P_CG 0.12-0.15 in current h4-harness. Regime-fix first (contam≥15% OR INTRA_COS≤0.4).
2. **lap3_12 (post-hoc calibration) — PROCEED.** Different mechanism class (calibrates existing score, doesn't PREDICT). Platt/isotonic literature has published effect sizes on weakly-monotone inputs. Unaffected by regime confound. Cell-author in flight.
3. **3-signal architecture REMAINS SOUND in principle.** Proving ground was wrong; individual signals need rederivation on reframed task.
4. **META atom recommendation (MM_TENTATIVE):** contamination-detection at contam ≤ 5% + INTRA_COS ≥ 0.6 is below-floor for geometric-observable class. Blocks future rediscovery. (Skunkworks already filed a related regime-hostility MM_TENTATIVE on h4b VET; expansion criterion → CG requires 3+ mechanism classes.)

**Reframed OOD-detection task skeleton (Phase 3 target after regime fix):**
- contam_fraction = 40% (not 4.6% — the confound)
- INTRA_COS = 0.35 (not 0.6 — reduces ridge saturation)
- Task = OOD-detection ("is query in-distribution vs OOD") not needle-finding ("which of 3600 items is the contaminated one")
- Joint 3-signal AUC target ≥ 0.75
- Individual signal targets: post-hoc AUC ≥ 0.65 / spatial AUC ≥ 0.65 / dynamical AUC ≥ 0.65 (all COULD work at these conditions per drill analysis)

**Path forward:**
- Phase 1: lap3_12 in flight (a4abeb) — completes post-hoc corner as calibration primitive
- Phase 2 (regime-fixed): after lap3_12 + h4b harness lessons, author reframed OOD task cell with all 3 signals as arms
- Phase 3 (combiner): only after 2+ signals CG on reframed task

## ⚠️ REGIME CAVEAT — added 2026-07-02 ~15:15 UTC after h4b smoke-HF (below is prior draft; superseded by regime drill verdict above)

h4b_margin_top1_top2_gap_predictor_v1 (commit `8c84c673a`) also HF'd at scale-preview smoke — AUC 0.545 at N=8192/items=3600 (below 0.55 reject threshold). **Two mechanism classes now HF in the same h4 harness** (INTRA_COS=0.6, PER=60, M=3600):

- Global density (h4 CG'd as HF_STRUCTURAL_BOUND)
- Spatial margin (h4b smoke-HF; FULL never dispatched — smoke gate saved compute)

Cell-author (h4b) surfaced: the h4-harness regime (contamination reaches top-K only 4.6% at full-N; gap distribution is narrow geometry-dominated ridge) may be structurally hostile to ANY contamination-detection mechanism at commercial scale. **Failure could be REGIME not MECHANISM CLASS.**

Before proceeding to Phase 2 (Lane X dynamical signal), a research drill on regime-vs-mechanism is needed:
- Is Lane X (cleanup-iteration count) susceptible to the same harness confound?
- Alternative task framing: instead of "predict which of 3600 stored items is contaminated", frame as "predict when substrate is out-of-distribution vs in-distribution" — different discriminator that doesn't require finding a 1-in-3601 needle
- Higher contamination fraction (e.g. 20%+) may make density/margin work but 4.6% doesn't

**Signals status after h4b:**
- Post-hoc (lap3_12) — UN-TESTED at scale; different mechanism class + different signal (calibrates a computed score, doesn't PREDICT uncertainty); may or may not be affected by same harness
- Spatial (h4b) — HF at smoke-preview in h4 harness; empirical closure of 8-month-old bio-calibrated-confidence-B1 anchor
- Dynamical (Lane X) — NOT yet designed; cell-author for h4b recommends "smoke-first regime redesign — current h4 harness may be confound"

The three-signal architecture is still SOUND IN PRINCIPLE — cortex needs multiple orthogonal signals. But the SPECIFIC IMPLEMENTATION under h4-harness contamination-detection may not be the right proving ground. Phase 3 (combiner) is unaffected in structure but individual signals may need re-derivation from a different task.

**Recommended pre-Phase-2 action:** research drill on regime-vs-mechanism BEFORE authoring Lane X. If the drill finds regime-confound, redesign all 3 signals against a better-conditioned task.

---

## Insight

M3 cortex needs a confidence signal to route each retrieval to one of `{ACCEPT, CLARIFY, REFUSE, RE-QUERY}`. h4 tried one signal (global cluster density) and HF'd at scale. Revival research surfaced not one but **three complementary observables** that jointly form a confidence vector:

| Signal | Observable | Nature | Cell status |
|---|---|---|---|
| **Post-hoc** | isotonic-calibrated top-1 score | statistical (regression on retrieval score) | `lap3_12_confidence_calibration_cpu_v1` — un-dispatched stub cell exists |
| **Spatial** | top-1 vs top-2 similarity gap | geometric (margin between winner and runner-up) | `h4b_margin_top1_top2_gap_predictor_v1` — cell-author in flight (agent a8b8) |
| **Dynamical** | cleanup-iteration count / energy delta | dynamical (attractor convergence rate) | `substrate_iterative_cleanup_cue_clamped_v1` + `substrate_multi_iteration_cleanup_LM_v1` primitives shipped; new Lane X cell needed |

Each signal has a distinct failure mode; each has a different mechanism class. **They are complementary, not redundant.**

---

## Why complementary (not redundant)

- **Post-hoc alone:** calibrates the winning score into a probability. Blind to how close 2nd-best is. Fails when 2 items are similarly-plausible (near-tie).
- **Spatial alone:** measures margin between top-2. Blind to whether either item is actually stored (both could be similarly-bad). Fails when the query is genuinely OOD and all matches are weak.
- **Dynamical alone:** measures how many cleanup iterations converge, or energy-drop over iterations. Blind to whether the converged answer is correct. Fails when cleanup rapidly finds a wrong-but-attractor answer.

Each single signal has a systematic blind spot. A **weighted vote or learned combiner** over the three has coverage of each failure mode by at least one signal.

---

## Prior work grounding

- **Ma et al 2006 population code** — brain cortex uses top-1/top-2 margin (spatial signal) as its native uncertainty proxy. This grounds the spatial signal.
- **Substrate-KB anchor `bio-calibrated-confidence-B1`** filed 2026-06-08 for exactly this population-code idea — sat unshipped for 8 months. h4b closes it.
- **Cleanup-iteration operating curve CG** (2026-07-01) — dynamical observable already characterized at cert-grade. Basis for Lane X.
- **Isotonic-calibration primitive** (`substrate_confidence_calibration_isotonic_v1`) — post-hoc primitive already in repo; lap3_12 exercises it end-to-end.

---

## Sequencing proposal

**Phase 1 (this session, in flight):**
- Ship `h4b_margin_top1_top2_gap_predictor_v1` (cell-author in flight)
- Author `lap3_12_confidence_calibration_cpu_v1` with revival-informed design (COMPLEMENTARY to h4b, not overlapping) — pending

**Phase 2 (next 1-2 sessions):**
- Author `sharded_confidence_lane_x_cleanup_iterations_v1` — Lane X dynamical signal
- Skunkworks-VET each individual signal at CG or MM tier

**Phase 3 (M3 integration, gated by USER cortex proposal):**
- Author `cortex_three_signal_confidence_combiner_v1`:
  - Arms: individual signals + weighted vote + learned combiner (small feed-forward)
  - Discriminator: joint AUC ≥ 0.80 (each individual should be 0.65-0.75; combiner beats any single by ≥ 0.05)
  - This is the M3-ready "confidence header" that hangs off the cortex composition
- Integrates with cortex integration proposal at `notes/proposal_cortex_integration_hdlab_module_2026-07-02.md`

---

## Downstream API sketch

```python
# hdlab/cortex_confidence.py (Phase 3 target)
class ConfidenceHeader:
    def __init__(self, substrate, combiner: Literal["vote","learned","calibrated_max"]):
        ...
    def score(self, query, retrieval) -> ConfidenceResponse:
        return ConfidenceResponse(
            post_hoc=self._isotonic(retrieval.top1_score),
            spatial=self._margin(retrieval.top1_score, retrieval.top2_score),
            dynamical=self._iter_energy(retrieval.cleanup_trace),
            combined=self._combine(...),
            route=self._route(...)  # ACCEPT/CLARIFY/REFUSE/RE-QUERY
        )
```

This is the callable that M3 conversational eval cells and M4 director cells use to decide "should substrate answer, ask for clarification, refuse, or re-query?"

---

## Cost estimate

- Phase 1 remaining (lap3_12 + finish h4b): ~1 day exp_dev work
- Phase 2 (Lane X): ~1 day
- Phase 3 (combiner + integration test): ~2 days
- Total to M3-ready confidence header: ~4 days sub-agent work

---

## USER decision points

Not blocking on USER for Phase 1 (h4b + lap3_12) — those are individual cells that stand on their own and the design is set.

**USER go/no-go needed for Phase 3** (three-signal combiner + integration into cortex). Alternatives to consider:
- (A) APPROVE: proceed sequentially through Phases 1-3 (~4 day path)
- (B) MODIFY: cortex integration proposal at `notes/proposal_cortex_integration_hdlab_module_2026-07-02.md` should include the three-signal ConfidenceHeader as one of its M1.9 components (bumping cortex phase count)
- (C) DEFER: land Phase 1-2 (individual signals CG) but hold combiner until USER has time to review architecture

Recommend (B) — bake ConfidenceHeader into the cortex proposal so the composed pipeline includes routing decisions natively; matches USER 2026-06-28 M3 architecture direction (cortex above substrate).

---

## References

- `notes/research_h4_revival_confidence_calibration_2x_drill_2026-07-02.md` — research 2x drill (a66bd7d45ff1f408d)
- `data/substrate_index/meta/atoms.jsonl` — atom `h4_cluster_density_contamination_predictor_hf_scale` (Skunkworks 2026-07-02)
- `notes/research_drill_biology_of_substrate_capabilities_5x_2026-06-08.md` — anchor `bio-calibrated-confidence-B1` (8 months un-shipped, closing via h4b)
- `notes/proposal_cortex_integration_hdlab_module_2026-07-02.md` — cortex module proposal (this three-signal architecture folds into it if Phase 3 approved)
- USER 2026-06-28 M3 architecture directive: cortex layer above substrate
- USER 2026-06-30 5x drill: M3 cortex must inject stochastic noise at boundary
