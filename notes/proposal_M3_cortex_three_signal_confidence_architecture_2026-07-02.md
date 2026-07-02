# Proposal — M3 cortex three-signal confidence architecture

**Filed:** 2026-07-02 mid-afternoon (post-restart session)
**Status:** strategic proposal; USER go/no-go on scope + sequencing
**Emerged from:** research 2x drill on h4 HF revival (a66bd7d45ff1f408d) + skunkworks h4 audit (a135cce573fd8410c)

## ⚠️ REGIME CAVEAT — added 2026-07-02 ~15:15 UTC after h4b smoke-HF

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
