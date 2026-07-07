# Research drill: which missing brain component has a REAL present consumer? (post-thalamus-shelving audit)

**Date:** 2026-07-07. Type: off-disk substrate-archaeology + operational drill (2x-style: deepen existing
07-05/07-06 findings, not a fresh broad re-scan) + 2 targeted external lit-scans for the top candidate only.
**Trigger:** USER-directed "brain-component-driven development" next-arc question, explicitly invoking the
thalamic-router HARD LESSON (never force-build a component without a proven consumer). Self-margin/self-audit
arc is closed; this opens the next arc.
**Discipline:** lit-scan calibration penalty applied (deflate 0.15-0.25; novel-synthesis capped at 0.50).
All internal figures verified off-disk via direct `metrics.json` reads, not asserted from memory.

---

## HEADLINE

**Every candidate was already drilled 2 days ago (07-05/07-06) and the state has NOT changed since — except
that one more consumer (waypoint/autonomous-decomposition, the OTHER proposed cerebellum target) has since
been definitively CLOSED (HARD_FAIL at FULL, `exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1`,
`DELTA=0.004`, matching the user's task text exactly). Re-auditing all 5 candidates off-disk today: 4 of 5
(thalamus, CLS-consolidation, neuromodulation-standalone, cortical microcircuit) still lack a genuinely
present consumer, exactly as the 07-06 backup doc already concluded ("Brain-components (CLS/neuromodulation/
cortical-microcircuit) lack a real consumer... avoid the thalamic force-build mistake"). ONE candidate has a
consumer that is real, measured, and still un-exploited with the right mechanism: the basal-ganglia-style
PFC-BG gate (`exp_pfc_gate_cfrpe_trained_v2`) is ALREADY BUILT and ALREADY HARD_PASS at depth-4
(`gonogo_lift=0.600`, closure=0.661) but its OWN measured depth-degradation curve
(`gonogo_lift` 0.653 at d4 -> 0.075 at d6, a real, already-shipped, already-in-use capability's honest scope
gap) is exactly the kind of "extend an existing working mechanism's envelope" target that has paid off
repeatedly elsewhere in this session (self-margin family). A prior attempt at fixing this specific gap
(`exp_pfc_gate_cfrpe_deeper_regime_v1`, SMOKE only, HARD_PASS but explicitly tagged
`horizon_attributable=-0.008_NOT_the_lever`) tried "branching" + a longer-gamma SR — i.e. it tested a
DIFFERENT lever (widen the value-function's effective horizon) and found it is NOT the driver. Two fresh
external lit-scans dispatched this cycle **independently confirm that finding**: raising gamma alone is
established in the literature as insufficient for horizon-degradation (Park et al. 2025/arXiv:2506.04168;
Fedus et al. 2019/arXiv:1902.06865), and the strongest-evidenced fix class is model-based lookahead/rollout
before committing (Lowrey et al., arXiv:1811.01848), not a cerebellar-style anticipatory-correction module in
isolation — which, both lit-scans agree, has **no direct precedent applied to a gating/action-selection
policy's horizon-degradation specifically** (well-precedented in motor timing and imitation-learning
trajectory-following, genuinely novel if ported to this exact problem class). This sharpens, rather than
kills, the candidate: the right next mechanism is a SR-based one/few-step forward-rollout feeding the CURRENT
gate decision (reusing `train_sr_transport`, already on disk), not a wider-gamma value function (already
tried, smoke-negative) and not the waypoint-decomposition coarse-to-fine+verify-gate recipe (already tried on
the SIBLING target, FULL-negative).**

---

## 1. RANKED consumer-strength audit (off-disk, all 5 candidates)

| Rank | Component | Consumer claimed | Status verified off-disk today | Verdict |
|---|---|---|---|---|
| **1** | **Cerebellum (forward-model, anticipatory)** — target B: control-gate depth-degradation | `exp_pfc_gate_cfrpe_trained_v2` (HARD_PASS d4, `gonogo_lift=0.600`) degrading to 0.075 at d6 | Gap is REAL, MEASURED, on an ALREADY-SHIPPED working mechanism. One lever tried (multi-gamma/branching) SMOKE-negative for "horizon is the lever." The RIGHT mechanism (SR-rollout-based anticipatory gate bias) has never been tried. | **LOADED, buildable — recommend quick smoke** |
| 2 | Cerebellum (forward-model) — target A: autonomous-decomposition waypoint chain | `exp_pfc_gate_autonomous_waypoint_discovery_v1` HARD_FAIL | `exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1` FULL landed `HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL`, `DELTA=0.004` (coarse-to-fine + verify-gate rescue, tried, failed) | **CLOSED — do not reopen, per task's own hint** |
| 3 | Basal ganglia proper (trained Go/NoGo + RPE) | control/goal-conditioned gating | `exp_pfc_gate_cfrpe_trained_v2` HARD_PASS at d4 (n_fair=2/7, V1200/V2400) | **ALREADY BUILT — graduated to HAVE, not a "next build"; its residual gap IS rank-1 above** |
| 4 | Neuromodulation (standalone: ACh-uncertainty-gain, or the task's own hypothesis of an encoder semantic-vs-algebra gain knob) | encoder NCE/algebra trade-off (`research_encoder_nce_margin_tradeoff_2x_drill_2026-07-06.md`) OR self-margin confidence signal | The encoder note's OWN recommended fix is a training-time sequenced-NCE-curriculum (geometry-first, discretize-last), NOT a runtime gain/precision gate — no cell, harness, or design treats neuromodulation as a live arbitration knob between the two objectives. Self-margin arc is independently CLOSED (per task framing) so a "confidence signal" consumer there is not a new opportunity, just reuse of a finished arc. | **NO genuinely present consumer — the encoder-gain-knob idea is my own speculative extension of the task's hypothesis, not evidenced by any existing harness; flag for a FUTURE dedicated drill, not a build now** |
| 5 | CLS-consolidation (hippocampal-fast/neocortical-slow replay) | ingest path | `research_language_ingest_glassbox_scoping_2026-07-05.md`: the NEAR-TERM ingest (vocab filter + morphology rules + frame-slot syntax) is a curation/wiring job, explicitly NOT a continual-learning-with-forgetting problem — CLS's actual consumer (general-knowledge/Wikipedia ingest) is explicitly USER-LOCKED "not yet." 2x MIDDLE_BAND + 1x HARD_FAIL already banked on the mechanism itself, mixed. | **NO present consumer — correctly deferred, unchanged from 07-06** |
| 6 | Cortical microcircuit / predictive coding | M3 cortex layer | Cortex-1: HONEST_NEGATIVE on its one utility probe. Cortex-2: parked, self-referential, zero wiring to language/encoder. 2x narrow HARD_FAIL already banked (bigram -0.789 nats, trigram -1.019 nats, 3/3 seeds). | **NO present consumer — correctly deprioritized, unchanged from 07-06** |

**Bottom line on the ranking:** this is NOT "5 components, pick one to build from scratch." It is: 1 component
(basal ganglia) already graduated to HAVE; its own measured weak point is the single best-evidenced next build
(rank 1, a cerebellum-class mechanism serving an EXISTING, PROVEN, SHIPPED capability's depth ceiling); the
sibling cerebellum target (rank 2) is now closed, cleanly, per the task's own expectation; and the remaining
3 (thalamus already shelved pre-today, CLS, cortical-microcircuit) genuinely lack a present consumer, matching
the 07-06 backup's own conclusion with no new evidence surfacing today to overturn it.

---

## 2. TOP PICK — exact consumer, predicted improvement, pre-build smoke design

**Component:** Cerebellar forward-model (anticipatory, predict-before-commit), narrowly scoped as an
SR-based one/few-step rollout feeding the gate decision — NOT the already-smoke-negative multi-gamma/
"branching" lever, and NOT the already-FULL-negative waypoint-decomposition recipe.

**Exact consumer:** `exp_pfc_gate_cfrpe_trained_v2` (`data/exp_pfc_gate_cfrpe_trained_v2/metrics.json`,
`HARD_PASS`, `gonogo_lift=0.600` at V1200_d4, `closure=0.661`) — the substrate's own working, shipped,
RPE-trained Go/NoGo control gate. Its `additive_per_regime` breakdown shows the mechanism is only "FAIR"
(valid apples-to-apples comparison) at d4 (V1200/V2400); every deeper regime (d5, d6) is marked `(unfair)` in
its own verdict message, meaning the deeper-depth numbers exist but were never a clean, gated comparison —
this is an honest, already-flagged, still-open scope gap on an in-use mechanism, not a hypothetical.

**Predicted measurable improvement (falsifiable, HARD-PASS/HARD-FAIL below):** recover a real fraction of the
d4->d6 `gonogo_lift` collapse (0.653 -> 0.075 in the underlying deeper-regime grid) by biasing the CURRENT
gate decision with a predicted future-success signal from a short SR-based forward rollout, rather than
widening the value function's discount horizon (already tried, smoke-negative for being "the lever").

**Quick pre-build smoke design (CPU, reuses on-disk primitives, no new representational machinery):**

Reuse `exp_pfc_gate_cfrpe_trained_v2`'s exact harness (`E`, `hebbian_W`, `train_sr_transport`, `cfrpe`
TD-error, the Go/NoGo argmax gate) and the deeper-regime cell's existing smoke grid (`op4_V300_d4/d6`,
`op2_V300_d6`, 3 seeds). Add ONE new arm, distinct from both prior attempts:

- `gonogo_sr_rollout_anticipatory` — before committing to the Go/NoGo decision at hop *t*, use the ALREADY-
  TRAINED `M` (SR transport matrix) to forward-simulate 1-2 steps from the current candidate action (a matrix
  multiply against `M`, not a new training loop), read off the predicted `reach_value` / TD-error AT THE
  ROLLOUT ENDPOINT (not the current step), and let THAT predicted-future signal (not the current-step signal
  alone) bias the gate's argmax. This is a genuinely different mechanism from `wp_bisect_coarse2fine` (which
  recursively re-picks a DIFFERENT waypoint using a longer-gamma SR — a value-function change) and from the
  already-tried `deeper_regime` branching arm (which changed which candidate ops are considered, not what
  signal drives the decision).

**Arms for the smoke:** `NO_CORRECTION` (reproduce the known 0.653->0.075 decay, already on disk, no rerun
needed as a rail), `FEEDBACK_ONLY_REACTIVE` (denoise/correct AFTER the hop commits, using the same rollout
machinery — isolates whether "any correction" does the work, per the 07-05 note's own falsification
discipline), `GONOGO_SR_ROLLOUT_ANTICIPATORY` (the cerebellar-specific arm, predict-then-bias BEFORE
committing).

**HARD-PASS:** `GONOGO_SR_ROLLOUT_ANTICIPATORY` recovers >=40% of the d4-d6 `gonogo_lift` gap at d6 (i.e.
d6 lift >= 0.075 + 0.40*(0.653-0.075) = 0.306) AND beats `FEEDBACK_ONLY_REACTIVE` by >=0.10 (proves the
anticipatory/feedforward property specifically matters, not just "correction helps") AND cross-seed cv<0.15.
(Deflated from the 07-05 note's original 50%-recovery bar — see P_deflated below — because the sibling
cerebellum target has since FULL-failed, raising the honest bar for how much benefit-of-the-doubt this class
of mechanism still deserves.)

**HARD-FAIL:** `GONOGO_SR_ROLLOUT_ANTICIPATORY` <= 0.075 + 0.05 (no material lift) OR does not beat
`FEEDBACK_ONLY_REACTIVE` (the feedforward-specific story is wrong; a generic post-hoc denoiser would do the
same job) OR cv>=0.25 (unstable, not a real effect).

**MIDDLE-BAND:** real lift over `NO_CORRECTION` (>0.05 on `gonogo_lift` at d6) but <40% gap recovery, or ties
`FEEDBACK_ONLY_REACTIVE` — real but not distinctively anticipatory.

**Compute:** CPU, ~1-2 hr smoke (3 seeds, reuses `train_sr_transport` verbatim, one matmul-based rollout
function, no new training loop). Escalate to FULL only if smoke clears MIDDLE-BAND or better, per standing
smoke-gate discipline.

**P_deflated:**
- P(any real anticipatory-vs-reactive lift, clears MIDDLE-band): raw ~0.40 (2 independent lit-scans confirm
  gamma-only is insufficient — external validation of the substrate's own smoke finding — and no source
  found a DIRECT negative result for anticipatory-correction specifically on a gating/horizon problem) ->
  **P_deflated ~0.28** after the mandatory 0.15-0.25 calibration penalty, further discounted for the sibling
  cerebellum target's FULL-negative on a mechanistically adjacent recipe (internal base-rate caution, not
  just external lit calibration).
- P(clears the full HARD-PASS bar, 40% gap recovery + beats reactive control): raw ~0.30 (genuinely novel
  synthesis per both lit-scans: "cerebellar anticipatory correction applied to a gating/action-selection
  policy's horizon-degradation" has no direct precedent, only adjacent motor-control and imitation-learning
  precedent) -> **P_deflated ~0.20**, well under the mandatory novel-synthesis cap of 0.50.

---

## 3. Cross-thread synthesis

- Directly extends and SHARPENS `notes/research_brain_component_rerank_thalamus_cerebellum_load_2026-07-05.md`
  (rank #2 cerebellum candidate, target = same control depth-degradation curve) and
  `notes/research_autonomous_waypoint_deep_corner_compounding_error_rescue_2026-07-05.md` (proposed treating
  BOTH cerebellum targets as one mechanism build). This drill's contribution: target A (waypoint) has SINCE
  been tested and FULL-failed (`DELTA=0.004`), so the "one mechanism serves both targets" framing from 07-05
  is now falsified as stated — the two targets need DIFFERENT concrete mechanisms even if both are
  brain-groundable in cerebellar theory. This drill narrows to target B alone and specifies a mechanism
  (SR-rollout-based anticipatory bias) that is NOT the coarse-to-fine+verify-gate recipe already spent on
  target A, and NOT the multi-gamma/branching recipe already spent (smoke-negative) on target B itself.
- Corroborates `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-06.md` line "Brain-components
  (CLS/neuromodulation/cortical-microcircuit) lack a real consumer (avoid the thalamic force-build mistake)"
  — today's off-disk re-audit finds NO new evidence to overturn that call for those 3 components; it stands.
- New, not previously flagged: the neuromodulation-as-encoder-gain-knob idea (task's own hypothesis) is
  explicitly assessed and found NOT YET evidenced as a present consumer — the encoder's own diagnosis
  (`research_encoder_nce_margin_tradeoff_2x_drill_2026-07-06.md`) recommends a training-curriculum fix, not a
  runtime gate, so building a neuromodulatory arbitration mechanism now would repeat the thalamic-router
  mistake (infrastructure with no demonstrated load). Flagged as a candidate for a FUTURE dedicated drill
  (specifically: would a runtime precision/gain knob at INFERENCE time, choosing per-query whether to trust
  the semantic-similarity read or the algebraic-decode read, be a genuinely different lever than the training
  curriculum? — untested, not recommended now).
- Two fresh external lit-scans this cycle (generic CS/neuro terms only, no substrate-specific vocabulary
  used off-platform) independently confirm the substrate's OWN smoke finding
  (`horizon_attributable=-0.008_NOT_the_lever`) that gamma/horizon-widening alone is an established-insufficient
  fix class in the literature — this is a genuine external corroboration of an internal negative, strengthening
  confidence in ABANDONING that lever (not retrying it with different gamma values) rather than reopening it.

## 4. Substrate-product implications

Closing this honestly matters for the glass-box narrative in the same direction as the thalamic-router
SHELVE call: recommending a build ONLY where a real, measured, already-shipped capability's honest scope gap
exists (basal-ganglia gate's depth ceiling) — not a speculative new subsystem — is itself the disciplined,
inspectable story ("we extend what demonstrably works, we don't manufacture infrastructure hoping for a
customer"). If the anticipatory-rollout smoke lands HARD-PASS, the product claim becomes concrete and
quantified: "goal-conditioned control gating, previously reliable only to depth-4, now recovers to X% at
depth-6 via an anticipate-then-decide mechanism" — a genuinely new capability extension, not a re-run. If it
HARD-FAILs, the honest bound sharpens further: "depth-6 goal-conditioned gating is closed even after both the
horizon-widening lever (already tried) and the anticipatory-correction lever (this drill) failed" — a
precise, defensible capability-map entry, consistent with how the sibling waypoint-decomposition target was
closed.

## Citations (verified count: 15 total — 2 fresh external lit-scans this cycle + 13 carried, not re-verified,
from the same-day 07-05 sibling notes per 2x-drill discipline)

**Fresh this cycle (2 independent Sonnet lit-scan sub-agents, WebSearch/WebFetch, generic terms only):**
1. Lowrey K. et al., "Plan Online, Learn Offline: Efficient Learning and Exploration via Model-Based Control,"
   arXiv:1811.01848 — H-step lookahead reduces value-error dependence by gamma^H; strongest-evidenced
   horizon-degradation fix class.
2. Park S. et al., "Horizon Reduction Makes RL Scalable," arXiv:2506.04168 (2025/2026) — horizon itself, not
   discount value, is the scaling bottleneck; gamma-only insufficient.
3. Fedus W. et al., "Hyperbolic Discounting and Learning over Multiple Horizons," arXiv:1902.06865 — multiple
   gammas as auxiliary task beats single-gamma; gamma-alone is a bias/variance trade, not a fix.
4. Janner M., Mordatch I., Levine S., "gamma-Models," NeurIPS 2020 / arXiv:2010.14496.
5. Sutton R., Precup D., Singh S., "Between MDPs and SMDPs," Artificial Intelligence 1999 — options/temporal
   abstraction.
6. Wolpert D., Miall R., Kawato M., "Internal Models in the Cerebellum," Trends Cogn Sci 1998.
7. Ito M., "Control of mental activities by internal models in the cerebellum," Nat Rev Neurosci 2008.
8. "Cerebro-cerebellar networks facilitate learning through feedback decoupling," Nature Communications 2022
   — closest DIRECT precedent found for a forward-model-style module in a learning/credit-assignment context,
   still not horizon-degradation-of-a-gating-policy specifically.
9. CDRL (cerebellar/dendritic-inspired Q-network in DDQN), arXiv 2026 (exact id not independently re-verified
   by the synthesizing agent, snippet-tier) — architecture-level value-function robustness gains, not an
   anticipatory-correction-vs-horizon test.
10. Schmahmann J., "dysmetria of thought" / Universal Cerebellar Transform — confirmed PURELY
    clinical/anatomical framing, no computational horizon-degradation claim; flagged explicitly as NOT a
    computational precedent (correcting the 07-05 note's more optimistic framing of this citation).
11. Ross S., Bagnell D., "Efficient Reductions for Imitation Learning," AISTATS 2010 (carried, re-affirmed).
12. Ross S., Gordon G., Bagnell D. (DAgger), AISTATS 2011 (carried; re-flagged this cycle as ITSELF
    reactive/interactive, not a true anticipatory forward-model — a nuance the 07-05 note did not surface).
13. "Is Behavior Cloning All You Need?," arXiv:2407.15007 (NeurIPS 2024) — plain BC can be horizon-independent
    under certain conditions, a negative-ish result for "correction is always necessary," newly surfaced this
    cycle.

**Carried, not re-verified this cycle, per 2x-drill discipline (from
`research_brain_component_rerank_thalamus_cerebellum_load_2026-07-05.md` and
`research_autonomous_waypoint_deep_corner_compounding_error_rescue_2026-07-05.md`):** Momennejad & Howard
2018; Frank & O'Reilly 2004/2006 (PBWM); Schultz-Dayan-Montague 1997; McClelland-McNaughton-O'Reilly 1995;
Sreenivasan-Fiete 2011 (grid-cell RNS robustness, thalamus-context only).

**Internal artifacts verified off-disk this cycle (not lit citations, load-bearing):**
`data/exp_pfc_gate_cfrpe_trained_v2/metrics.json` (HARD_PASS, gonogo_lift=0.600, closure=0.661, per_regime
FAIR/unfair breakdown); `data/exp_pfc_gate_cfrpe_deeper_regime_v1_smoke/metrics.json` (HARD_PASS smoke,
`horizon_attributable=-0.008_NOT_the_lever`, `horizon_is_the_lever=False`); no FULL exists for this cell
(confirmed via `find data -maxdepth 1 -iname "*cfrpe_deeper*"`, only `_selftest`/`_smoke` dirs on disk);
`data/exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1/metrics.json` (FULL,
`HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL`, `DELTA=0.004`); `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-06.md`
(thalamic-router SHELVED line, brain-components-lack-consumer line); `notes/research_encoder_nce_margin_tradeoff_2x_drill_2026-07-06.md`
(encoder trade-off's own recommended fix is a training curriculum, checked to confirm no runtime-gate
consumer exists yet); `notes/research_language_ingest_glassbox_scoping_2026-07-05.md` (ingest dependency
table, confirms near-term ingest does not need CLS-consolidation); `notes/research_thalamic_router_RC2_mechanism_RC3_decision_2026-07-05.md`
(thalamus SHELVE rationale, re-confirmed unchanged); grep of `notes/*2026-07-07*.md` for
cerebellum/CLS/neuromodulation/cortical-microcircuit/basal-ganglia mentions (0 hits — confirms no new
same-day development on any of these 5 candidates prior to this drill).

**Next-drill candidate (if this smoke lands HARD-PASS or MIDDLE-BAND):** escalate to FULL on the same 9-regime
grid as the deeper-regime cell. **If this smoke HARD-FAILs:** the honest capability-map entry becomes "control
gating beyond depth-4 is closed after both horizon-widening and anticipatory-rollout fixes" and the
brain-component-driven-development thrust should pause on cerebellum entirely and return to the
encoder-joint/ingest critical path, per the task's own fallback framing.
