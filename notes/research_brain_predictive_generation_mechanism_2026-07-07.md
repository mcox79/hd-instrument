# Research: how the brain does predictive generation -- grounding Stage-4's generation mechanism

**Date:** 2026-07-07. **Type:** Deep evaluation drill (USER-directed; no cell dispatch, no cell design
commitment -- mechanism-grounding + build recommendation only, per task framing).
**Trigger:** the substrate has a documented, repeated, 4-cell negative result on context-depth for predictive
generation (`exp_n2_context_depth_hd_binding_v1` bpc 5.00->5.05->5.18 as K=1->2->3, HARD_FAIL; plus
`exp_n5_trigram_concept_lm_v1` and `exp_substrate_direct_gen_lm_wikitext_trigram_v3_n8192_gpu`, both
HARD_FAIL; one MIDDLE_BAND `exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu`) -- context accumulation
makes prediction WORSE with depth. Brain=best-in-class reference (USER-locked): the brain does not have this
failure, so its actual predictive-generation mechanism is the target to ground Stage 4's fix in.
**Method:** field advisor run (output below, correctly overridden -- this is a USER-directed mechanism-grounding
question, Trigger-E equivalent, matching the explicit precedent of the 2026-07-07 stage-4 note). 3 parallel
Sonnet lit-scan sub-agents, one per mechanism cluster (predictive coding + cortical microcircuit; successor
representation; hippocampal sequence generation + cerebellar forward models), generic neuro/math search terms
only per query-privacy. Lit-scan calibration penalty applied throughout (deflate 0.15-0.25; novel-synthesis P
capped 0.50).

**Field advisor (context, correctly overridden by Trigger-E):** top candidates this cycle were free-probability
(F4 free cumulants) and semiconductor/stochastic-dynamics (Glauber/Metropolis/FFS) adjacents -- none of these
touch predictive-generation neuroscience. This drill is the USER-directed exception (mechanism-grounding for a
named, load-bearing capability gap), not a field-advisor-ranked pick.

---

## HEADLINE

**Two independent, well-evidenced brain mechanisms -- predictive coding (Rao-Ballard/Friston) and the successor
representation (Dayan/Stachenfeld) -- converge on the SAME underlying principle, and it is a DIFFERENT, DEEPER
antidote than the one already queued as the next GPU probe.** The already-recommended fix
(`research_stage4_generation_load_bearing_gap_and_gpu_probe_2026-07-07.md`'s `CLEANUP_PER_STEP` arm) is the
**shallow version**: accumulate raw, noisy context every step exactly as the 4 failed cells do, then run a
CA3-style attractor cleanup afterward to denoise the mess. The brain's actual mechanism, on both the
predictive-coding and successor-representation reads, is the **deep version**: never accumulate the raw signal
in the first place. At every step the brain (a) generates a PREDICTION from its current state, (b) compares
prediction to the actual next input and keeps only the RESIDUAL (prediction error), and (c) updates its running
state using that residual -- via a bootstrapped delta-rule (SR: TD(0)) or a precision-weighted gradient step
(predictive coding: Kalman-filter-equivalent) -- not by literally summing the raw observations. This bounds
per-step noise injection structurally (a Kalman filter's steady-state error covariance is bounded; a raw
running-sum estimator's variance is not), independent of and IN ADDITION TO the CA3-style discrete-attractor
reset that the hippocampal replay/theta-sequence literature separately supports. **The two brain mechanisms are
complementary, not redundant: CA3-cleanup cleans up noise AFTER it enters the state (a regenerative digital
repeater, confirmed by this session's lit-scan as plausible for hippocampal replay); predictive-coding/SR
REDUCES how much noise enters the state per step in the first place (a differential/predictive encoder, the
neuroscience analog of DPCM in signal processing).** Best-grounded, cheapest-to-build antidote: swap the
substrate's existing hetero-associative context->next-item matrix from a static count/Hebbian update to a
TD-bootstrapped delta-rule update (the successor-representation read) -- this is a small, well-specified
algorithmic change to an already-existing primitive, not a new architecture, and it is the ONE lever among the
five evaluated that both (a) is a documented, evidence-strong brain mechanism and (b) requires no new substrate
machinery to prototype.

---

## 1. RANKED brain mechanisms (addresses-noise-compounding x VSA-implementability x evidence-strength)

| Rank | Mechanism | Addresses noise-compounding | VSA/substrate-implementable now | Evidence strength | Verdict |
|---|---|---|---|---|---|
| **1** | **Successor representation** (Dayan 1993; Stachenfeld, Botvinick & Gershman 2017, *Nat. Neurosci.*) | YES -- TD-bootstrapped delta-rule update has a fundamentally different bias/variance profile than Monte-Carlo/raw accumulation (bounded bias vs. unbounded variance growth) | **HIGH, immediately.** SR's learned matrix M = (I - gamma*T)^-1 is a linear operator over state/feature space, learned by a Hebbian-shaped delta rule -- structurally the SAME OBJECT as the substrate's existing hetero-associative context->next-item matrix (`W_hetero`, already used in `exp_n1_concept_lm_substrate_native_token_decode_v3_1` and the queued `CLEANUP_PER_STEP` cell). The only change needed is the LEARNING RULE: TD(0) bootstrap instead of static count/Hebbian outer-product. Successor FEATURES (Barreto et al. 2017/2019, NeurIPS/arXiv:1606.05312) generalize this to arbitrary feature vectors -- directly matches the substrate's concept-code representation, no discrete-state assumption needed. | Moderate-strong: Stachenfeld et al. 2017 fit to place/grid-cell data is a genuine multi-study empirical convergence (independently corroborated by Mehta et al. 1997 PNAS place-field skew data), not a normative retrofit; the underlying TD/dopamine machinery is independently well-established. Contested specifics: whether grid cells are literally SR eigenvectors is still debated. | **Best-grounded, buildable antidote. Top build recommendation.** |
| **2** | **Predictive coding / free-energy principle** (Rao & Ballard 1999, *Nat. Neurosci.*; Friston 2005/2010; Bogacz 2017, *J. Math. Psych.*) | YES, most FORMALLY of the five: Sennesh/Millidge et al. (arXiv:2111.10530) derive the Kalman filter as the exact steady-state fixed point of free-energy gradient descent -- a Kalman filter's error covariance is PROVABLY bounded (discrete algebraic Riccati fixed point) because each step re-weights only the CURRENT residual by a precision-dependent gain and discounts stale evidence, whereas a naive running-sum accumulator's variance grows with sample count. Precision-weighting (Feldman & Friston 2010) is a direct SNR argument: literally the Kalman gain term, down-weighting noisy channels. | HIGH but requires restructuring the accumulation loop into two channels (predict + error), not a one-line change: maintain a running PREDICTED-next-code vector separately from the actual-observed code, subtract (unbind) to get the residual, superpose ONLY the residual into the running state (weighted by an estimated precision/confidence), then predict again. Whittington & Bogacz 2017 give a concrete, substrate-independent 3-node wiring template (prediction node / error node / local Hebbian update) that maps cleanly onto bind/superpose/cleanup. | Strong theory, partial direct evidence: Rao-Ballard's surround-suppression account is well-supported; the broader active-inference framework is mathematically rigorous with converging but incomplete in-vivo confirmation (per a 2021 Simons Foundation piece explicitly flagged by the lit-scan: direct causal proof of the full scheme remains incomplete). | **Deepest theoretical grounding for WHY noise doesn't compound; second-priority build (see Section 3 for how it composes with #1).** |
| 3 | **Canonical cortical microcircuit** (Bastos, Usrey, Adams, Mangun, Fries & Friston 2012, *Neuron*) | Same as #2 -- this is the anatomical WIRING of #2, not an independent algorithmic mechanism | Gives a concrete layer-role template (L2/3 = error/feedforward, L5/6 = prediction/feedback, L4 = raw input relay) that maps onto a substrate design as "two parallel channels instead of one blended context vector" -- useful IMPLEMENTATION GUIDANCE for #2, not a separate build. | Well-motivated synthesis with strong anatomical corroboration (Felleman & Van Essen 1991 feedforward/feedback laminar rule) and oscillatory-band evidence (feedforward=gamma, feedback=alpha/beta), but still an unproven-at-cellular-resolution framework per the same evidence caveat as #2. | Not independently ranked -- a wiring-detail sub-component of #2. |
| 4 | **Hippocampal theta phase-precession + replay/preplay** (O'Keefe & Recce 1993; Skaggs et al. 1996; Foster & Wilson 2006/2007; Diba & Buzsaki 2007; Dragoi & Tonegawa 2011) | PARTIALLY: the discrete/compressed (~10-20ms per step) nature of theta sequences and replay, contrasted with continuous-attractor drift/diffusion literature (Zhang 1996; Compte et al. 2000, which explicitly treats noise-accumulation as an intrinsic continuous-attractor failure mode), FAVORS but does not directly PROVE a per-step discrete-attractor-reset interpretation. Chenkov, Sprekeler & Kempter 2017 (*PLoS Comput Biol*) show recurrent-boosted "assembly" chaining (functionally = per-step attractor convergence before handoff) permits reliable sequence propagation with far sparser connectivity than pure feedforward (synfire) chains -- structurally consistent with per-step cleanup, not a direct single-cell demonstration of it. | Already scoped -- this IS the neuroscience justification for the ALREADY-QUEUED `CLEANUP_PER_STEP` GPU probe, not a new mechanism. | Theta sequences/replay/preplay themselves: well-established (multiply replicated, Nature/Nat.Neurosci-tier). The specific "each replay step = one attractor-basin convergence acting as cleanup" synthesis: plausible, modeling-supported, NOT directly experimentally confirmed at the single-step level. | **Confirms/raises the prior on the already-planned `CLEANUP_PER_STEP` probe (the shallow-version antidote) -- does not add a new mechanism beyond it.** |
| 5 | **Cerebellar forward models** (Wolpert, Miall & Kawato 1998; Wolpert & Kawato 1998; Ito 2008; Sokolov, Miall & Ivry 2017) | NO, not for THIS problem. The lit-scan is explicit: the canonical cerebellar forward model predicts sensory consequences of a motor command that is ALREADY KNOWN internally (via efference copy) -- it cancels self-generated, known-cause noise and compensates for feedback delay. This is mechanistically a different problem than predicting an UNKNOWN external continuation (e.g., next-token prediction); no paper was found demonstrating cerebellar forward-model machinery solving open-ended unknown-content prediction, only the cognition-extension literature (Ito 2008; Sokolov et al. 2017) speculating by analogy. | Not applicable as the generation mechanism itself. Possibly relevant LATER as a self-confidence/error-monitoring signal on the substrate's OWN generation output (predict-my-own-output-quality), a distinct, narrower future use, not the core mechanism. | Motor forward-model architecture: well-established. Cognitive extension: actively researched hypothesis, not settled, and its applicability to unknown-content prediction is explicitly an open, unverified extrapolation per the lit-scan. | **Ruled out as a generation-mechanism candidate for this gap.** Flag for a distinct, later use (self-monitoring / confidence-calibration of generation output), not this drill's scope. |

---

## 2. The cross-cutting theme: is predictive-coding-with-error-correction the biological form of "per-step re-clean"? Is the brain's predictive state literally a regenerative repeater?

**Answer: partially yes, but the honest answer is that there are TWO distinct regenerative mechanisms in the
brain, not one, and they solve different halves of the noise-compounding problem.**

1. **The CA3-attractor/hippocampal-replay side IS literally a regenerative repeater**, in the same sense already
   established for multi-hop reasoning (`research_noise_compounding_bound_deep_mechanism_2026-07-07.md`'s
   diagnosis: reasoning-depth survives because it hard-resets to an EXTERNAL fixed codebook at every hop, a
   digital-repeater analogy). The theta-sequence/replay literature (discrete, compressed, ~10-20ms steps;
   attractor-network sequence models showing recurrent-boosted assemblies functioning as per-step convergence
   points) is structurally the SAME regenerative-repeater pattern applied to sequence GENERATION rather than
   multi-hop TRAVERSAL. This is the mechanism the already-queued `CLEANUP_PER_STEP` GPU probe targets, and this
   drill's lit-scan RAISES confidence in that probe (independent literature convergence on discrete-attractor
   reset as a real, evidenced brain strategy for sequence stepping) without changing its design.

2. **The predictive-coding/SR side is a DIFFERENT kind of noise control, and the more precise analogy is NOT a
   repeater but a differential/predictive ENCODER** -- literally the neuroscience analog of differential/predictive
   pulse-code modulation (DPCM) in signal processing: transmit (store, accumulate) only the part of the signal
   that was NOT already predictable from the running model, because that residual is smaller and carries less
   redundant information than the raw signal. A repeater cleans up noise AFTER it has entered the state (removes
   an already-injected error). A predictive/differential encoder REDUCES how much new information/noise enters
   the state PER STEP in the first place, by construction (only the surprise gets written in). These are
   genuinely complementary, not the same fix twice: **repeater = clean what's there; predictive encoder = inject
   less to begin with.** The strongest version of the antidote uses BOTH: predict, keep only the residual,
   inject the (smaller) residual into the state, THEN attractor-clean the result -- which is exactly the
   composed build recommendation in Section 3.

**This is a genuine refinement of, not a contradiction to, the already-filed noise-compounding drill** -- that
drill correctly identified "hard reset to an external ground truth" as the reasoning-depth fix; this drill adds
that the brain's generation-specific solution ALSO reduces the noise-injection RATE per step (via prediction-error
encoding), a mechanism the reasoning-depth chain does not need (because it fully re-anchors to ground-truth
codewords each hop and therefore has near-zero residual noise per hop by construction) but that generation likely
does need, because generation's "ground truth" at each step is the actual, genuinely-novel next token -- there is
no external codebook to hard-reset against for content that hasn't been generated yet.

---

## 3. BUILD RECOMMENDATION: predictive-residual context update, composed with existing primitives

**Distinguishing from the CA3-cleanup probe already queued:** `CLEANUP_PER_STEP` (the already-recommended next
GPU arm in `research_stage4_generation_load_bearing_gap_and_gpu_probe_2026-07-07.md`) is the SHALLOW version --
same raw-bind accumulation as all 4 prior failed cells, with a cleanup step bolted on afterward. This drill's
recommendation is the DEEP version and should be framed as a FOLLOW-ON arm, not a replacement, sequenced by the
`CLEANUP_PER_STEP` result (see decision table below).

**The composed mechanism (all four pieces are existing substrate primitives, no new architecture):**

```
c_0 = clean_zero_vector
for t in 1..K:
    p_t       = hetero_associative_readout(W_hetero, c_{t-1})     # PREDICT: existing primitive, same lookup
                                                                    # already used for decode
    e_t       = unbind(encode(token_t), p_t)                       # ERROR: residual against prediction, NOT
                                                                    # the raw token itself
    c_t_raw   = bind(c_{t-1}, position_shift) + e_t                # accumulate ONLY the residual, not raw token
    c_t_clean = iterative_attractor.cleanup(c_t_raw)               # CA3-style reset, same as CLEANUP_PER_STEP
    W_hetero  = W_hetero + alpha * TD_bootstrap_delta(c_{t-1}, c_t_clean, token_t)   # SR-style learning update,
                                                                    # replaces static count/Hebbian update rule
predict token_{K+1} from hetero-associative readout keyed on c_K_clean
```

This composes: sequence/positional binding (existing), CA3 cleanup attractor (existing, already the
`CLEANUP_PER_STEP` mechanism), hetero-associative context->next-item memory (existing, `W_hetero`), and ONE new
element -- a TD-bootstrapped delta-rule replacing the static count/Hebbian update on `W_hetero`, plus injecting
the residual `e_t` rather than the raw token into the accumulator. Both the residual-injection and the
TD-bootstrap-learning-rule changes are independently motivated by the lit-scan (predictive coding for the
former, successor representation for the latter) and are cheap to implement as arm variants on the SAME already-
GPU-proven cell (`exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu.py`) the prior note already targets.

**How this reverses the context-hurts-with-depth curve (the mechanistic claim under test):** the 4 failed cells
all accumulate strictly MORE raw, uncleaned, unweighted information per step as K grows -- variance grows with
K by construction, exactly the unbounded-running-sum-accumulator failure mode the Kalman/predictive-coding
literature explicitly contrasts against bounded steady-state filters. If the substrate's `W_hetero` already
gives even a mediocre prediction (and the MIDDLE_BAND 2nd-order-trigram cell shows it does -- beats bigram-count),
injecting only the residual should inject LESS novel noise per step than injecting the raw token would, and the
TD-bootstrap update means `W_hetero` itself keeps improving its own predictions from the residual signal, rather
than being a fixed count table. Both effects point the same direction: less noise entering the state per step,
plus attractor cleanup on top removing what noise remains.

**Decision-sequencing against the already-queued probe:**

| If `CLEANUP_PER_STEP` (shallow, already queued) result is... | Recommended next step |
|---|---|
| HARD_PASS (fixes the depth curve outright) | This drill's deeper mechanism becomes an OPTIMIZATION, not a rescue -- test whether adding residual-injection + TD-bootstrap further IMPROVES the already-fixed curve (does it beat a bigram-count baseline outright, not just flatten the curve) |
| MIDDLE_BAND (helps but doesn't fully fix) | This drill's mechanism becomes the PRIMARY next lever -- the residual/TD-bootstrap changes address exactly the part of the problem that per-step cleanup ALONE cannot (the noise-injection RATE, not just after-the-fact denoising) |
| HARD_FAIL (cleanup alone does not fix it) | This drill's mechanism is the correct redirect BEFORE falling back to the "representation-capacity ceiling" branch already named in the prior note -- a HARD_FAIL for cleanup-alone does not rule out the deeper predictive-residual mechanism, since that note's own attractor-malfunction risk flag (`iterative_attractor.py`'s documented HARD_FAIL history at high-storage/high-noise operating points) could equally explain a cleanup-alone failure without saying anything about whether reducing injected noise per step (this drill's fix) would also fail |

---

## Cheap decisive test (analysis-level -- no cell design here per task scope; sequencing pointer for exp_dev)

Given `CLEANUP_PER_STEP` is already the queued next GPU arm, the cheap decisive test for THIS drill's
contribution is: **add ONE further arm, `PREDICT_RESIDUAL_TD`, to the same cell**, run at SMOKE scale (same
reduced-corpus, N=8192, K in {1,2,3} smoke grid already specified for `CLEANUP_PER_STEP`) alongside it, not
sequentially -- since both arms reuse the identical harness and baselines, the marginal smoke cost of adding
the second arm is small relative to running the first arm alone. GO/NO-GO signature:
- **GO:** `PREDICT_RESIDUAL_TD` at K=2/K=3 shows LOWER bpc than `CLEANUP_PER_STEP` at the same K (residual
  injection + TD-bootstrap beats cleanup-alone), even if `CLEANUP_PER_STEP` itself already passes.
- **NO-GO:** `PREDICT_RESIDUAL_TD` performs the same as or worse than `CLEANUP_PER_STEP` -- the residual/TD
  refinement adds no value over cleanup alone at this scale; the SR/predictive-coding mechanism does not
  transfer to this substrate's decode regime even though the brain-literature grounding for it is strong (a
  real possible outcome: the brain's advantage may depend on continuous online adaptation over millions of
  steps, a regime this single-corpus smoke test cannot replicate).

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Claim under test: "injecting only the prediction-residual (not the raw token) into the context accumulator,
combined with a TD-bootstrapped update to the hetero-associative context->next-item matrix, further reduces
context-depth degradation beyond per-step attractor cleanup alone."**

- **HARD-PASS:** `PREDICT_RESIDUAL_TD` beats `CLEANUP_PER_STEP` by >= 0.2 bits at K>=3 AND the improvement grows
  (not shrinks) with K AND the TD-bootstrap update shows monotonically improving `W_hetero` prediction accuracy
  over the corpus stream (evidence the learning rule itself is converging, not diverging) AND holds across >= 3
  seeds (CV <= 0.15).
- **HARD-FAIL:** `PREDICT_RESIDUAL_TD` performs the same as or worse than `CLEANUP_PER_STEP` at all K, OR the
  TD-bootstrap update diverges/oscillates (W_hetero prediction accuracy degrades over the stream rather than
  improving), OR the residual `e_t` turns out to carry MORE effective noise than the raw token would (e.g. if
  `p_t` predictions are frequently wrong, the residual can be dominated by the wrong-prediction's own vector
  rather than being genuinely smaller/cleaner than the raw signal -- a real, specifically-flagged risk since the
  substrate's own concept-recall rate is only ~0.507 per `exp_n1_concept_lm_substrate_native_token_decode_v3_1`,
  meaning roughly half of all predictions are wrong and could inject MORE noise via a bad residual, not less).
- **MIDDLE_BAND:** helps at low K (2-3) but the advantage does not persist or grow at higher K -- would indicate
  the mechanism helps but doesn't fully replace the need for a capacity-side fix (disjoint-block context
  encoding, already named in the prior note as the fallback lever).
- P(claim holds) raw ~0.40-0.45 (two independently strong-evidenced brain mechanisms, converging on the same
  qualitative prediction, composed from primitives already proven individually -- but never tested together on
  this exact substrate, and the flagged concept-recall-rate risk above is a real, quantified reason the residual
  could be noisier than the raw signal rather than cleaner) -> **P_deflated ~0.25-0.30** after the mandatory
  lit-scan calibration penalty (deflate 0.15, novel-synthesis cap 0.50 applied) AND after weighting the
  substrate's own 4-attempt, 0-HARD_PASS track record on this exact problem family. This is a genuinely
  uncertain bet, slightly more optimistic than the shallow `CLEANUP_PER_STEP` arm's own P_deflated (~0.20-0.25
  per the prior note) because it is grounded in TWO independent converging brain mechanisms rather than one, but
  not confidently so given the un-tested-in-combination risk and the concept-recall-rate noise-injection risk.

---

## Honest bounds: what's genuinely VSA-implementable now vs. aspirational

**Implementable now, with existing primitives, cheap arm addition:**
- Successor-representation-style TD-bootstrap update to `W_hetero` (Section 3) -- a delta-rule swap on an
  existing matrix, no new architecture.
- Residual injection (`unbind(actual, predicted)` instead of raw `encode(token)`) into the context accumulator
  -- a straightforward composition of existing bind/unbind primitives.
- Per-step CA3 cleanup -- already scoped by the sibling probe, `iterative_attractor.py` already exists.

**Aspirational / NOT directly implementable without further design work:**
- The full canonical-microcircuit two-channel (separate prediction-layer vs error-layer) architecture (Section
  1, rank 3) -- conceptually clean but would require restructuring the substrate's context representation into
  two parallel channels rather than one blended vector; worth prototyping only if the single-channel
  residual-injection version (Section 3) shows a real effect and a cleaner separation is needed to push further.
- Precision-weighting (attention-as-gain) on the residual -- the substrate has no current per-step confidence
  estimate wired into the context-update step; `substrate_router/noise_channel.py` (M1.3, already built) is the
  nearest existing primitive that COULD supply this signal but is not yet wired into a generation-context loop.
  Flagged as a natural Phase-2 addition, not required for the Phase-1 test above.
- Cerebellar forward-model-style self-monitoring of generation quality -- explicitly out of scope for THIS gap
  (Section 1, rank 5); a distinct, later capability (confidence-calibration on the substrate's own output), not
  part of the core generation-mechanism fix.

**Cite neuroscience honestly:** the strongest, most direct evidentiary claims in this note are (a) the
Kalman-filter-as-fixed-point-of-free-energy-descent derivation (Sennesh/Millidge et al., arXiv:2111.10530 --
formal, verifiable), and (b) the Stachenfeld et al. 2017 fit of SR to place/grid-cell data, independently
corroborated by Mehta et al. 1997's place-field-skew experimental result. The weakest, most speculative claim is
the cerebellar-forward-models-generalize-to-cognition extension (Ito 2008; Sokolov et al. 2017) -- explicitly
ruled out as this gap's mechanism, not relied upon anywhere in the build recommendation.

---

## Cross-thread synthesis

- Directly extends and refines (does not contradict) `research_stage4_generation_load_bearing_gap_and_gpu_probe_2026-07-07.md`
  -- confirms `CLEANUP_PER_STEP` as the correct shallow-first probe (Section 1, rank 4's independent literature
  convergence on discrete-attractor sequence-stepping raises confidence in it) while adding a deeper,
  sequenced follow-on (Section 3) grounded in two DIFFERENT brain mechanisms than the one that note already cites.
- Directly connects to `research_noise_compounding_bound_deep_mechanism_2026-07-07.md`'s "regenerative repeater"
  framing for multi-hop reasoning -- Section 2 above makes the explicit distinction this drill was asked to
  resolve: reasoning's fix (hard reset to ground truth) and generation's likely fix (predictive-residual
  encoding + reset) are RELATED but not IDENTICAL, because reasoning has an external ground-truth codebook to
  reset against at every hop and generation does not (the next token is genuinely novel, not a known target).
- Uses `research_reasoning_depth_self_margin_closed_form_2026-07-06.md`'s per-hop survival law as the reference
  quantitative target the prior note already proposed fitting to the `CLEANUP_PER_STEP` depth curve -- this
  drill does not re-derive that law, it clarifies which mechanism (shallow reset vs deep residual-reduction)
  should be expected to fit it and why.
- Corroborates (does not extend) the `research_2x_drill_ca3_anti_signal_at_cluster_codebook_mechanism_analysis_2026-07-03.md`
  finding that CA3-style auto-associative cleanup is a well-precedented, upstream-preprocessing-dependent
  mechanism -- consistent with this drill's finding that CA3-style attractor reset is real and evidenced but is
  ONE HALF of the brain's antidote, not the whole story.

## Substrate-product implications

- Per the USER-locked framing: this is diagnostic/mechanism-grounding, not a claim of parity with an LLM. The
  substrate does not currently do non-trivial predictive generation; this note identifies the SPECIFIC brain
  mechanism (predictive-residual encoding + TD-bootstrapped associative learning, composed with the already-
  planned attractor cleanup) as the best-grounded next lever, with an honest, quantified risk (the ~0.507
  concept-recall rate could make residual injection NOISIER, not cleaner, if predictions are frequently wrong).
- If the composed mechanism works: the substrate gains not just a working predictive-generation primitive but a
  principled, brain-grounded EXPLANATION for why it works (two complementary noise-control mechanisms, not one),
  which generalizes as a design pattern to any future substrate component that accumulates state over
  many steps (not just language generation) -- multi-turn dialogue state, long-horizon reasoning chains, or any
  context-carrying loop.
- If it fails (the NO-GO / HARD-FAIL branches above): the honest next lever is already named (disjoint-block/
  frame-slot-style context representation, per the prior note) -- and this drill's negative result would
  additionally tell us the concept-recall-rate is currently too low for residual-based prediction to help (a
  concrete, actionable diagnostic pointing back to codebook/VQ granularity as the root fix, not the sequencing
  mechanism).
- Either way, this keeps the brain-grounding discipline structural rather than a one-off citation exercise: the
  next generation-mechanism probe now has a specific, falsifiable, two-mechanism (not one-mechanism) hypothesis
  to test, sequenced correctly against the probe already queued.

## Citations (verified count this cycle)

Verified via direct WebSearch/WebFetch this cycle (19): Rao & Ballard 1999 (*Nat. Neurosci.*); Bogacz 2017
(*J. Math. Psych.* 76); Sennesh/Millidge et al., arXiv:2111.10530; Bastos, Usrey, Adams, Mangun, Fries & Friston
2012 (*Neuron* 76); Whittington & Bogacz 2017 (*Neural Computation* 29(5)); Kok, Rahnev, Jehee, Lau & de Lange
2012 (*Cerebral Cortex*); Simons Foundation 2021 evidence-strength piece; Dayan 1993 (*Neural Computation* 5(4));
Stachenfeld, Botvinick & Gershman 2017 (*Nat. Neurosci.* 20); Gershman 2018 (*J. Neurosci.* 38); Barreto et al.
2017/2019 (NeurIPS/arXiv:1606.05312, arXiv:1901.10964); Mehta, Barnes & McNaughton 1997 (*PNAS* 94); O'Keefe &
Recce 1993; Skaggs, McNaughton, Wilson & Barnes 1996 (*Hippocampus*); Foster & Wilson 2007 (*Hippocampus*); Diba
& Buzsaki 2007 (*Nat. Neurosci.* 10); Dragoi & Tonegawa 2011 (*Nature* 469); Chenkov, Sprekeler & Kempter 2017
(*PLoS Comput. Biol.*); Wolpert & Kawato 1998 (*Neural Networks*) / Wolpert, Miall & Kawato 1998 (*Trends Cogn.
Sci.*); Ito 2008 (*Nat. Rev. Neurosci.* 9); Sokolov, Miall & Ivry 2017 (*Trends Cogn. Sci.* 21).

Recalled from training, NOT independently re-verified via search this cycle (flagged, lower confidence, 11):
Friston 2005/2010 free-energy principle papers; Millidge, Seth & Buckley 2021 review; Felleman & Van Essen 1991
laminar feedforward/feedback rule; Feldman & Friston 2010 precision/attention; Sutton & Barto TD bias-variance
framing (standard RL-textbook content, corroborated generically not via a single primary source); Foster &
Wilson 2006 (reverse replay); Wilson & McNaughton 1994; Zhang 1996 and Compte et al. 2000 (continuous-attractor
drift/diffusion -- general CANN drift claims were corroborated via search but not these exact papers); Hopfield
1995; Levy 1996.

Total citations: 30 (19 verified this cycle, 11 flagged as training-recall).
