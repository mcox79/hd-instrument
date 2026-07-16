# Research: how biological systems calibrate a fast/slow decision-route threshold

Director drill, 2026-07-16. Single-pass Sonnet lit-scan (5 parallel WebSearch queries across SDT criterion-setting,
DDM boundary-setting, BCM metaplasticity, consolidation-route adaptivity, and normative cost-of-error theory).
Directly extends `notes/research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15.md`, which left the
three gate thresholds (`SCHEMA_FIT_MIN=0.5`, `SURPRISE_MIN=0.5`, `RECURRENCE_MIN=3`) as **picked, not derived**
values. This drill asks the narrower, load-bearing follow-up question: does biology set this KIND of threshold as
(a) fixed, (b) experience-adapted, (c) homeostatic set-point, or (d) normative cost/base-rate calculation — and is
that the SAME mechanism-type across literatures, or several different ones bundled under one name?

## HEADLINE

The fast/slow route boundary in biological systems is **ADAPTIVE, but via at least THREE mechanistically distinct
knobs that the literature never unifies into one model** — this mirrors, almost exactly, last night's finding that
the CLS ingest-gate's three signals (schema-fit/surprise/recurrence) are separately evidenced but never formally
combined. (1) SDT/DDM criterion and boundary-separation are demonstrably trial-history- and reward-rate-adaptive,
with a normative optimum (Bogacz et al. 2006) that human/animal behavior approximates but does NOT hit exactly
(Norton et al. 2017 show systematically suboptimal, recency-weighted updating — not the Bayes-optimal rule, a
leaky heuristic approximation of it). (2) The DDM boundary is ALSO adjusted online, causally, by a distinct
subcortical circuit (STN hyperdirect pathway, Frank et al.; pre-SMA, Cavanagh et al.) that raises threshold under
CONFLICT specifically — a different input variable than reward-rate/base-rate. (3) BCM's sliding LTP/LTD threshold
(Bienenstock-Cooper-Munro 1982; Abraham heterosynaptic in vivo evidence, PNAS 2001) is real, well-evidenced, and
IS homeostatic in the technical sense (regulates around a recent-activity set-point) — but it operates at the
single-synapse plasticity-direction level, not at a route-selection/decision level, and no paper connects it
directly to a fast/slow PROCESSING-ROUTE choice. (4) The hippocampal-fast/cortical-slow consolidation boundary
ITSELF is empirically adaptive to schema-richness (Tse et al. 2007/2011) — this is NOT treated as a fixed
biological constant in the literature — but **no paper was found that derives this specific transition rate from
a formal reward-rate/Bayes-cost optimization analogous to Bogacz's DDM treatment.** That gap is the single most
actionable finding for the substrate: the normative machinery exists and is well-validated for perceptual
decisions, but has never been extended, even theoretically, to the memory-system consolidation-route boundary.

## Findings by area (with calibration-penalized confidence)

**1. SDT criterion-setting — ADAPTIVE, primary evidence, well-replicated.**
Green & Swets (1966) is the classical fixed-criterion baseline theory, but Norton, Fleming, Daw & Landy (2017,
*PLoS Comput Biol* 13:e1005304) show observers keep updating criterion trial-by-trial even after prolonged
training in a STATIC environment, using a suboptimal recency-weighted rule (not the Bayes-optimal static
criterion SDT itself prescribes). Lak-style auditory-detection work (PMC4259461) and a 2024 *Comput Brain Behav*
paper reconciling criterion-learning with the generalized matching law both confirm trial-history/reinforcement-
history dependence. Confidence: HIGH this is adaptive (primary behavioral data, replicated); moderate-only on
whether it is "optimal" adaptation (it is not — systematically suboptimal/leaky).

**2. DDM boundary-setting — ADAPTIVE, causal neural evidence, two distinct drivers.**
Boundary separation is manipulable by task instruction (classic SAT manipulation) and shown causally
neuro-modulable: pre-SMA TMS/TBS selectively shifts response threshold (ScienceDirect 2016 TBS study); STN DBS in
Parkinson's patients under speed pressure lowers effective threshold and increases impulsive errors (Springer
2016; PMC4893074); STN spiking activity and mediofrontal (pre-SMA/dACC) activity scale with trial-by-trial
DECISION CONFLICT specifically (Frank et al., *Nat Neurosci* 2011/PMC3394226; PMC3296967), and this is a
computationally distinct signal from reward-rate/base-rate optimization — the hyperdirect pathway raises
threshold when responses COMPETE, independent of prior probability. This is genuinely two adaptive levers
(conflict-driven urgency-brake vs. reward-rate-driven baseline), not one. Confidence: HIGH (multiple independent
causal-manipulation studies, convergent).

**3. BCM sliding threshold — real, homeostatic, but a DIFFERENT mechanism-type than a route boundary — gap
flagged.**
Abraham's in vivo dentate gyrus work (PNAS 2001, PMC6622209 follow-up) directly confirms the modification
threshold theta_M shifts with recent postsynaptic activity history, exactly as BCM theory (1982) predicts and
independent of synaptic scaling (Turrigiano) which acts on synaptic WEIGHTS rather than the plasticity threshold
itself. This is a real, primary-data-confirmed homeostatic set-point. But it is a single-synapse LTP/LTD-direction
threshold, not a route-selection (fast-track vs slow-track, or encode-now vs hold) decision — no paper found
treats it as the same computational object as an SDT/DDM criterion. Confidence: HIGH that BCM sliding-threshold is
real; confidence LOW/UNRESOLVED that it is mechanistically the same TYPE of object as a decision-route boundary —
flagging this as an explicit "not found, and probably a category error to assume it" result.

**4. Consolidation-route boundary adaptivity — ADAPTIVE (schema-dependent), but NOT normatively derived —
the key gap.**
Tse et al. (2007, *Science* 316:76-82; 2011, *Science* 333:891-895) directly show the hippocampal-independence
transition is schema-gated, not a fixed ~48h constant: schema-consistent new learning becomes hippocampus-
independent within 48h (vs. multi-week baseline) while schema-INCONSISTENT material does not. Multiple secondary
sources (van Kesteren et al. 2012 SLIMM; "To update or to create?" *Phil Trans R Soc B* 2024) reinforce that
prior-knowledge/schema-richness is the governing variable, not elapsed time per se. This is solid, replicated,
primary-data adaptivity — the literature explicitly rejects treating the transition as fixed. **However: no paper
in this search derives the transition RATE from an explicit cost-of-error / base-rate / reward-rate optimization
argument** — the Bogacz-style normative apparatus that exists for perceptual DDM boundaries has never (in this
search) been applied to memory-system consolidation timing. This is a genuine, actionable gap, not a search
failure — the two literatures (perceptual decision normative theory vs. memory consolidation biology) appear not
to have been connected.

**5. Normative cost-of-error framework — well-established theory, proven for perceptual decisions, unproven for
memory routing.**
Neyman-Pearson lemma + Bayes-risk minimization gives the general form: threshold tau* = C_FP/(C_FP+C_FN), i.e. a
likelihood-ratio cutoff set by relative error costs and (via the likelihood ratio itself) base rates. Bogacz et
al. (2006, *Psychol Rev*) proved this is EXACTLY the DDM's reward-rate-optimal boundary/starting-point solution for
2AFC tasks, later extended to sequential/serial-correlated trials (arXiv 1806.03872, Nguyen et al. 2019) where the
optimal policy uses a Markov-transition-aware prior update. This is the correct normative BENCHMARK. Confidence:
HIGH this is the right normative form; HIGH confidence that biological systems only approximate it (per findings
1-2, with a systematic leaky/recency bias, not the closed-form optimum).

## Cheap decisive test

Reuse the already-fitted `additive_map` `(X,D)` from the ingest-gate pilot design (2026-07-15 note, Section 6) and
run TWO threshold policies side by side on the SAME batches 1+3 (redundant-skip / noise-reject) slice, changing
nothing else:
- **Policy F (fixed):** current design — `SURPRISE_MIN=0.5` constant, as pre-registered.
- **Policy A (adaptive/normative-lite):** `SURPRISE_MIN_t = f(recent moving-average surprise rate, RECURRENCE_MIN
  hit-rate)` — an exponentially-weighted online update of the threshold toward the Bayes-optimal cutoff implied by
  the CURRENT observed ratio of redundant-vs-novel candidates in the last W cycles (a direct, cheap implementation
  of the Neyman-Pearson tau* = C_FP/(C_FP+C_FN) form, with C_FP/C_FN as pre-registered constants and the base-rate
  term estimated online — i.e., literally combining findings 1, 2, and 5 above into one candidate mechanism).

Compare skip-rate/discard-rate accuracy (vs. the same HARD-PASS bars already set: batch1 skip-rate >=80%, batch3
consolidate-rate <=5%) AND track whether Policy A's threshold trajectory correlates with the true underlying
redundancy rate of the stream (a directly falsifiable claim distinct from mere pass/fail).

## Falsifiable predictions

**HARD-PASS (supports building Policy A / online-adaptive threshold over Policy F / fixed):**
- Policy A meets or exceeds Policy F on both HARD-PASS bars (batch1 skip >=80%, batch3 consolidate <=5%) AND
- Policy A's threshold trajectory correlates with the local moving base-rate of genuinely-novel vs. redundant
  candidates at r >= 0.5 (confirms the mechanism is doing normative base-rate tracking, not just adding free
  parameters that overfit the specific pilot batches).

**HARD-FAIL (supports keeping Policy F / fixed threshold, i.e., biology's homeostatic-set-point answer wins over
the per-decision-normative answer for THIS substrate):**
- Policy A shows no accuracy improvement over Policy F (delta < 5% relative on either bar), OR
- Policy A improves accuracy but its trajectory does NOT track the local base-rate (r < 0.2) — meaning the gain
  came from extra degrees of freedom / overfitting the pilot batches, not from doing the claimed normative
  calculation — in which case a SIMPLER homeostatic (BCM-style, one slow global set-point, not per-decision
  Bayes update) mechanism should be tried next instead, per finding 3's distinction.

**MIDDLE (realistic modal expectation, given finding 1's "suboptimal but real" result in the human literature):**
Policy A improves the harder batch-2 (genuine-novel-reliable, MRR-improvement) case noticeably more than the easy
batch-1/3 cases, mirroring the literature's finding that adaptive criterion-shifting matters most under
non-stationary/base-rate-shifting conditions, not under a static distribution — this would argue for building the
adaptive threshold specifically for the SLOW-TRACK/ambiguous middle band, not uniformly across all three gates.

## Cross-thread synthesis

- Directly sharpens `research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15.md`: that note flagged
  `SCHEMA_FIT_MIN/SURPRISE_MIN/RECURRENCE_MIN` as picked-not-derived; this drill supplies the missing normative
  form (Neyman-Pearson/Bayes-risk tau*) AND the honest caveat that biological systems only approximate it with a
  recency-leaky heuristic (Norton et al. 2017) — meaning an exactly-optimal Bayes threshold is likely the WRONG
  brain-faithful target; a leaky/EWMA-style approximate tracker is the more brain-faithful design, not a bug to
  engineer out.
- Directly informs the memory-stated CURRENT THRUST (07-16 session state): "assign the 3 gate-signals... RACE 3
  arms (brain-faithful vs my-learned-weights vs hybrid)". This note supplies the brain-faithful arm's actual
  mechanism candidates: (i) recency-weighted/leaky online criterion update for SURPRISE_MIN (per SDT finding 1),
  (ii) conflict-triggered threshold raise, structurally analogous to STN hyperdirect braking, as a candidate
  mechanism for the "HOLD for provenance review" branch when surprise AND recurrence both fire simultaneously
  (finding 2), and (iii) an explicit flag that BCM-style homeostasis (finding 3) is likely the wrong donor
  mechanism for route-selection specifically — it is evidenced at the wrong level of the system (synapse-local
  plasticity direction, not decision routing) — steering the "brain-faithful" arm away from a plausible-looking but
  probably-mismatched analogy.
- Consistent with the PIVOT's foundation-building framing (project_PIVOT... 07-14): normative cost-of-error theory
  (finding 5) is exactly the kind of "ideal-observer" benchmark the substrate can implement exactly (glass-box,
  no LLM needed) even where biology itself only approximates it — a case where the substrate-product can exceed
  the biological reference on the NORMATIVE axis while still being informed by the biological MECHANISM axis for
  which approximation (leaky-EWMA, not full Bayes update) to prefer for stability/interpretability reasons.

## Substrate-product implications

1. Do NOT implement `SURPRISE_MIN` as a hand-picked constant if this cheap decisive test passes — replace it with
   a cheap, already-financially-costed EWMA threshold-tracker (a few added lines over the existing `score_all`
   call), directly informed by SDT criterion-learning literature (finding 1) and the Neyman-Pearson normative form
   (finding 5). This is a near-zero-cost upgrade path from the already-pre-registered pilot design.
2. Do NOT try to unify BCM-style homeostasis with the ingest-gate route-selection threshold — literature gives no
   support for treating these as the same mechanism-type (finding 3); prevents a plausible-looking but likely
   wrong design detour.
3. The conflict-driven threshold-raise mechanism (finding 2, STN/pre-SMA analog) maps naturally onto the
   already-designed "distinct-novelty -> hold for provenance review" branch (2026-07-15 note, Section 4B) — when
   surprise is high AND recurrence is borderline (structurally "conflicting evidence" about whether this is
   reliable), raising the effective threshold before committing is exactly the biological conflict-braking
   pattern, giving that branch a first-principles justification rather than an ad hoc design choice.
4. The single biggest actionable gap (finding 4/5) is that NO literature connects consolidation-route timing to a
   formal reward-rate/cost optimization — meaning the substrate's ingest-gate, if it builds this connection, is
   not "copying a known brain algorithm" but doing genuinely novel cross-literature synthesis. Per the lit-scan
   calibration discipline, this novel-synthesis claim is capped at P=0.50 regardless of how clean the individual
   ingredients look.

## Citations (verified count: 17 sources via WebSearch snippets/abstracts; full-text not independently fetched —
flag as abstract/snippet-level verification, not primary full-text read, for all entries below)

Green, D.M. & Swets, J.A. (1966). *Signal Detection Theory and Psychophysics*. Wiley. [theory, secondary/textbook]

Norton, E.H., Fleming, S.M., Daw, N.D., Landy, M.S. (2017). "Suboptimal Criterion Learning in Static and Dynamic
Environments." *PLoS Computational Biology* 13(1):e1005304. [primary, verified via PLOS/PMC5242548]

"Reconciling Signal-Detection Models of Criterion Learning with the Generalized Matching Law" (2024).
*Computational Brain & Behavior*. [primary, verified via Springer abstract]

"Decision Criterion Dynamics in Animals Performing an Auditory Detection Task" (PMC4259461). [primary, verified via
PMC abstract; author/year not independently confirmed beyond snippet]

Bogacz, R., Brown, E., Moehlis, J., Holmes, P., Cohen, J.D. (2006). "The physics of optimal decision making: a
formal analysis of models of performance in two-alternative forced-choice tasks." *Psychological Review*
113(4):700-765. [primary, well-known reward-rate-optimal DDM derivation; verified via ResearchGate abstract]

Nguyen et al. (2019). "Optimizing sequential decisions in the drift-diffusion model." *Journal of Mathematical
Psychology*. arXiv:1806.03872. [primary, verified via arXiv]

Frank, M.J. et al. — STN/hyperdirect pathway decision-threshold modulation; "Subthalamic nucleus stimulation
reverses mediofrontal influence over decision threshold," *Nature Neuroscience* (2011), PMC3394226. [primary,
verified via PMC/Nature abstract]

"Neuronal Activity in the Human Subthalamic Nucleus Encodes Decision Conflict during Action Selection" (PMC3296967).
[primary, verified via PMC abstract]

STN DBS Parkinson's speed-pressure impulsivity study, *Experimental Brain Research* (2016) /
PMC4893074. [primary, verified via Springer/PMC abstract]

Pre-SMA continuous theta-burst stimulation study, *ScienceDirect* (2016), affecting response threshold
specifically vs. DLPFC affecting drift rate. [primary, verified via ScienceDirect abstract]

Bienenstock, E.L., Cooper, L.N., Munro, P.W. (1982). "Theory for the development of neuron selectivity."
*Journal of Neuroscience* 2(1):32-48. [primary theory, foundational BCM paper; not independently re-fetched this
cycle, cited via Scholarpedia/Nature Reviews secondary confirmation]

Abraham, W.C. et al. (2001). "Heterosynaptic metaplasticity in the hippocampus in vivo: a BCM-like modifiable
threshold for LTP." *PNAS* 98(19):10924-10929. [primary, verified via PNAS/PubMed abstract]

"Calcium-Dependent But Action Potential-Independent BCM-Like Metaplasticity in the Hippocampus," *J Neurosci*
(2012), PMC6622209. [primary, verified via PMC abstract]

Cooper, L.N. & Bear, M.F. (2012). "The BCM theory of synapse modification at 30: interaction of theory with
experiment." *Nature Reviews Neuroscience* 13:798-810. [secondary/review, verified via Nature abstract]

Tse, D. et al. (2007). "Schemas and memory consolidation." *Science* 316:76-82. [primary, previously verified in
2026-07-15 note, re-cited here for the schema-adaptivity-of-consolidation-rate claim]

Tse, D. et al. (2011). "Schema-dependent gene activation and memory encoding in neocortex." *Science* 333:891-895.
[primary, previously verified]

Neyman-Pearson lemma / Bayes-risk asymmetric-loss threshold form (tau* = C_FP/(C_FP+C_FN)) — standard decision-
theory result, sourced this cycle via lecture notes (data102.org) and general decision-theory secondary sources,
not a single primary paper. [theory, textbook-level, well-established — not a novel or contested result]

## Deflated confidence (lit-scan calibration: deflate 0.15-0.25 off undeflated read; novel-synthesis capped at 0.50)

- P(fast/slow route boundary in biology is better described as ADAPTIVE than FIXED, across SDT/DDM/consolidation
  literatures jointly) = **0.60** (undeflated ~0.80 — this is about as convergent as lit-scans get: every literature
  searched gave primary adaptive evidence and none defended a fixed-criterion account for these three systems;
  deflated modestly because "adaptive" is a compound claim bundling 3 distinct mechanisms that the search cannot
  itself prove are analogous to each other).
- P(BCM sliding-threshold and decision-route-boundary are the SAME mechanism-type, i.e., that homeostatic
  metaplasticity is a valid engineering donor for the ingest-gate route threshold) = **0.20** (undeflated ~0.30-0.35;
  deflated further because this is closer to a "not found" result — no direct literature connects these two
  objects, and the a priori structural mismatch, single-synapse vs. system-level routing, argues against the
  analogy holding).
- P(a normative reward-rate/cost-of-error derivation of the consolidation-route transition rate, applying
  Bogacz-style optimality to the Tse/schema-consolidation literature, would be genuinely NOVEL cross-literature
  synthesis, not already published somewhere unfound) = **0.50** (capped at the novel-synthesis ceiling per
  calibration discipline; this search's coverage of the consolidation literature was not exhaustive enough to rule
  out that such a connection exists in a corner of the computational-psychiatry or theoretical-neuroscience
  literature not surfaced by these 5 queries).
- P(the cheap decisive test as specified — Policy A vs Policy F on the already-fitted additive_map pilot batches —
  would show a HARD-PASS result favoring adaptive-threshold) = **0.40** (undeflated ~0.55-0.60; the SDT literature's
  finding that human/animal adaptation is SUBOPTIMAL/leaky, not exactly Bayes-optimal, is itself informative:
  it suggests the pilot is more likely to land in the MIDDLE band — some improvement, concentrated in the harder
  ambiguous cases — than a clean joint HARD-PASS across all bars).

## Next-drill candidate

If the cheap decisive test (Policy A vs Policy F) is run and lands in MIDDLE (adaptive threshold helps mainly on
ambiguous/slow-track cases, not uniformly): the natural next drill is the STN/pre-SMA conflict-braking literature
specifically (finding 2) as a candidate mechanism for the "HOLD for provenance review" branch — a `learning-rules`-
adjacent or `network-science-graph-theory` question (is there a cheap graph-local proxy for "response conflict"
analogous to STN's role, computable from the additive_map's existing candidate-ranking distribution — e.g., the
margin between top-1 and top-2 scored targets — that could gate the same way conflict gates DDM threshold).
This is untested and would be a genuinely new (not-yet-drilled) angle: `decision-conflict-as-ranking-margin`.
