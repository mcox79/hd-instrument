# Research synthesis: brain-fidelity gap, event-prediction -> relation-inference (2026-08-03)

Filed by: research sub-agent (Sonnet), dispatched by Director per USER's re-issued existence-proof
principle ("if the brain can do it, it's possible; if we're not able to recreate that, we're doing
something wrong") after 4 negatives on the event-level relation/goal-inference predictor. Per the
two-gate discipline, a miss is a ceiling only if it passes BOTH gate1 (fair test) and gate2 (exactly
like the brain); the most recent (SR/TD) miss failed gate-2, so it is NOT a ceiling. This doc does
the end-to-end, cross-run adjudication the five background docs individually motivated but did not
jointly perform, and lands on ONE recommended mechanism.

## 0. KB-check and scope

Director's `substrate_query.sh` pass (tau=0.15, k=5, "event segmentation prediction narrative
comprehension brain fidelity relation inference") returned only generic FrameNet/WordNet lexical
near-misses and one weak hit on an unrelated prediction note -- no duplicate synthesis exists.
Proceeding. Per instruction, this is research-only: no experiment cells authored or dispatched, no
running work touched (SR/TD is landed-negative; the inverse-planning drill is the only other thing
live and untouched here).

**Read and NOT re-derived** (cited, built on): the two component-by-component brain-fidelity audits
(phase1 and v2-HARD_FAIL), the encoder-target-grain drill, the SR/TD predictive-mechanism drill, and
the inverse-planning/goal-inference drill -- all listed in the task brief, all already DOI/venue-
verified for their citation sets. This doc's own job, stated plainly: **adjudicate across the 4
empirical failures which single deviation is most load-bearing, test hypothesis 2 (wrong framing)
against the specific SR/TD failure signature which the prior docs did not have when they were
written (the phase1/v2 audits predate the SR/TD run; the SR/TD drill and the goal-inference drill
were written to arm that run, not to post-mortem it)**, and give ONE decisive recommendation.

---

## 1. The 4 failures, restated as one evidence table (disk-verified facts, not re-argued)

| # | Cell | Context | Objective/metric | Result | Signature |
|---|---|---|---|---|---|
| v1 | MSE event predictor | 2-event symmetric bundle (order-blind) | MSE point-regression to next event-struct | Beat only an unfair random-init strawman; lost to fair predict-mean baseline (cos_trained=0.98 to the constant mean) | **Mean-collapse**: the trained map converged to the unconditional mean, near-zero context sensitivity |
| v2 | Associative/retrieval | window=1 (regression from a bundle-degeneracy bug) | Literal-next-sentence retrieval vs 9 same-novel distractors | 0.108 trained vs 0.119 copy-context (LOST), vs 0.084 random, 0.098 mean; cosine_trained=0.578 (near-uniform) | **Mean-reversion recurring under a different gate**, plus an outright loss to a trivial local-continuity heuristic |
| Option B | Organ-routed readout (no trained predictor) | CausalLinkRegister + ToM organ over isolated 2-3-snippet triples | Overall 0.520 vs random 0.480; clean axes (unstated_goal, satisfy_restate) LOSE to random | Organs tested **crippled** -- without their proven non-adjacent multi-hop graph capability, on context-STRIPPED snippets | Not a faithful test of the organs' real operating mode |
| SR/TD | TD-bootstrapped contrastive successor map | Accumulated situation-model context (not window=1), causal-reachability ranking metric (not surface retrieval) | 0.2590 trained vs 0.2565 copy vs 0.2544 mean/random; margin +0.0025 vs the pre-registered 0.05 bar; n=3212 | Mean-collapse **structurally fixed** (cosine-to-mean 0.134 vs v1's 0.906 -- the SR mechanism's own prediction held) but **all four arms (trained, copy, mean, random) cluster within 0.005 of each other** | **Near-null margin across every baseline simultaneously, not just a loss to one baseline** |

This last row is the fact none of the five background docs had reason to dwell on, because the SR/TD
drill and the goal-inference drill were written to ARM that run (they precede it), and no post-mortem
of its specific numeric signature has been done until now. It is the most informative data point in
the whole sequence, for a reason argued in Section 3.

---

## 2. Testing the three hypotheses against this table (not asserting -- adjudicating)

### Hypothesis 3 (scale/curriculum) -- test first because it is the easiest to honestly REJECT for
these specific signatures, and should not be force-fit.

Mean-collapse under MSE (v1) is a **training-objective** pathology: `argmin_W E||Wx-y||^2` is
minimized at `E[y|x]` whenever x underdetermines y, REGARDLESS of how much data you throw at it --
more data makes the estimate of the conditional mean more precise, it does not stop the objective
from wanting the mean. This is a textbook property of squared-error regression under an
under-informative/high-entropy target, not a sample-size problem. Similarly, the SR/TD near-null
margin is NOT accompanied by any sign of undertraining (the mechanism's OWN diagnostic, cosine-to-
mean, dropped from 0.906 to 0.134 -- exactly what more/better training should produce) -- the arms
are close together because trained, copy, AND mean-baseline are all landing at roughly the same
place, which is the signature of an **information-theoretically flat target at this grain**, not a
data-starved model. **Verdict: REJECTED as an explanation for these four specific failures.** Scale/
curriculum/grounding may matter for a LATER, better-specified mechanism, but forcing it onto the
mean-collapse or the near-null-margin signatures we actually observed is not supported by the
evidence -- correctly flagged as such per the task brief's own instruction not to force-fit.

### Hypothesis 1 (segmentation-prediction unity) -- real, load-bearing, but not the SINGLE
explanation, and the SR/TD run's own design is the reason we can now say so with more precision than
the phase1/v2 audits could.

Sentence-split segmentation was UNCHANGED (still the naive regex heuristic) across all 4 runs,
including SR/TD -- so it remains a plausible contributor to every failure. But the SR/TD run
specifically fixed the two previously-diagnosed confounds (context breadth via the accumulated
situation model, and target grain via causal-reachability ranking instead of literal retrieval) and
STILL produced a near-null margin. If segmentation noise alone were the dominant remaining cause, the
expected failure signature would be a trained arm that is CONSISTENTLY WORSE than a fair baseline by
a clear margin (noisy input degrading otherwise-real learning) -- which is what v1 and v2 actually
show (mean-collapse, loss to copy). What SR/TD shows instead is different in kind: **all baselines,
including two that require no learning at all (mean, random), collapse to the same narrow band as
the trained arm.** That is not the fingerprint of "noisy segmentation degraded a real signal" -- it
is the fingerprint of "there is very little signal to find at this grain in the first place, for
ANYONE, trained or not." Segmentation quality is a real, independently-motivated fix (Zacks's own
theory says segmentation IS the predictive mechanism, not a separate stage feeding it) and should
still be built -- but it is not, by itself, sufficient to explain why SR/TD specifically landed where
it did, because a cleaner segmentation would sharpen the CANDIDATE events being predicted over, not
change the fact that surface-level narrative continuation is high-entropy at the sentence/event grain
regardless of how cleanly those events are individuated. **Rank: real, necessary, but secondary --
addresses candidate QUALITY, not the deeper framing problem Section below names as primary.**

### Hypothesis 2 (wrong target/framing: prediction-accuracy vs construction-integration) -- PRIMARY,
and the SR/TD near-null-margin signature is the strongest single piece of evidence for it that exists
in this whole sequence.

Kintsch's construction-integration model (already cited in the SR/TD drill, Section 3 there) says
comprehension does not proceed by accurately guessing the one correct next proposition -- it proceeds
by loosely overgenerating many candidate propositions via associative spread (a genuinely
UNCONSTRAINED, low-precision step) and then filtering to a coherent subset via constraint
satisfaction. Crucially, **the brain's own construction step is not judged by whether it correctly
predicts the single true continuation** -- most of what it generates is discarded. If narrative
comprehension does not require accurate single-token/single-event prediction, then a metric that
scores "did the trained predictor's TOP guess beat baselines' top guess" is testing a property the
brain itself does not need to have. This reframes every one of the 4 failures at once, not just
SR/TD:

- **v1 (MSE)**: point-regression is the sharpest possible version of "there is one correct answer";
  its objective function's own optimum (the conditional mean) is a direct symptom of trying to
  answer a question -- "what is THE next event" -- that does not have a single answer in real prose.
- **v2 (retrieval)**: literal-next-sentence retrieval against hard distractors is a slightly softer
  version of the same assumption (rank the one true continuation above alternatives); it still
  presumes there IS one identifiable "true" continuation worth ranking to the top, and copy-context
  wins specifically because local lexical continuity is real and cheap while "the correct schema-
  level continuation" is a much fuzzier, multi-valued target that a linear map cannot sharpen against.
- **Option B**: even here, the underlying ask was "does routing through the organs clear a FIXED
  0.52 accuracy bar" -- again an accuracy-maximization framing, now applied to organs whose actual
  proven competence (CausalLinkRegister, 0.9722) is COHERENCE-CHECKING given already-identified
  candidate relations, not first-pass generation of a single correct relation label from raw context.
  Testing a coherence-filter as if it were a first-pass accuracy-maximizing classifier is a category
  mismatch independent of the crippled-context problem the docs already flagged.
- **SR/TD**: with context and metric-grain both fixed, the remaining explanation for "everyone lands
  in the same narrow band, trained included" is that **accurate next-event prediction, scored as a
  single winner-take-all ranking task, is close to the ceiling ANY method can achieve at this grain in
  real narrative prose** -- consistent with real human next-word/next-sentence prediction studies,
  where surprisal is the norm rather than the exception (high entropy over plausible continuations is
  what makes prose informative to read at all). This is not "our predictor is bad" -- it is "the task
  we scored it on is not the task the brain is good at either."

**This is the single most parsimonious explanation across all 4 negatives.** It requires no auxiliary
assumption about any ONE run being uniquely crippled (each run had its own separate flaw, correctly
diagnosed by the prior audits) -- it explains why fixing each run's own separate flaw (mean-collapse
fixed by SR's structural property; context-starvation and surface-metric fixed by the accumulated-
context + reachability-ranking design) still did not produce a real result: because the target being
optimized (accurate top-1 next-event prediction, judged against baselines) was never the right
success criterion to begin with, in any of the four operationalizations.

---

## 3. The decisive additional argument: what "predict-next-event accuracy" would even MEAN if it
worked, versus what it needs to feed

Even granting a hypothetically perfect brain-faithful predictor (joint segmentation, full
accumulated context, hierarchical multi-timescale prediction-error, replay-generated negatives): its
job, biologically, is to generate a DISTRIBUTION over plausible next situational states, most of
which are individually wrong and are supposed to be wrong -- narrowing that distribution down to the
one true continuation is not what the mechanism is FOR. What is downstream of it (SATISFY/THWART/
CAUSE and unstated-goal judgments) is answered by the coherence/mentalizing INTEGRATION stage
checking the ACCUMULATED situation model against multiple indices at once (Zwaan's five indices),
not by reading the top-1 prediction off the construction stage directly. Put differently:
**"accurately predict the next event" was never the brain's actual deliverable on this task; it was
always an intermediate, deliberately-lossy step whose output is consumed, not scored, by a separate
filter.** Grading the construction stage on prediction accuracy is asking an intermediate computation
to be individually correct at a job the architecture as a whole was never designed to need it to be
correct at.

---

## 4. RANKED load-bearing fidelity gaps (most-responsible-for-the-4-failures first)

1. **(Highest) Wrong success criterion: prediction-accuracy-vs-baselines, applied to what should be a
   construction (overgenerate) stage, not a first-pass classifier.** Brain: construction generates
   many candidates, most individually wrong, filtered downstream; metric = does the FILTERED output
   answer relation queries correctly, not does the construction stage's top guess win a ranking
   contest. Ours: every one of the 4 attempts, in different operationalizations (point-regression,
   retrieval-ranking, fixed-accuracy-bar organ routing, reachability ranking), graded a construction-
   stage mechanism as if it were the final answer. This explains all 4 negatives with one story and is
   the only hypothesis that predicts the SR/TD near-null-margin-across-all-arms signature specifically
   (Section 2).
2. **(High, compounding) Segmentation is not yet the same mechanism as prediction (Zacks unity).**
   Sentence-split segmentation, unchanged across all 4 runs, degrades the QUALITY of whatever
   candidates a construction stage proposes -- real but secondary, because fixing it alone (without
   also fixing #1) would still leave a construction stage being graded on the wrong criterion.
3. **(Medium, largely already being addressed) Representational/context gaps**: missing GOAL/OUTCOME
   role slots (build_event_struct_v6, AGENT/ACTION/OBJECT only), and the earlier window=1/window=2
   context-starvation (already fixed once, in SR/TD, via the accumulated situation model -- this gap
   is the one MOST already resolved by prior work; keep the GOAL/OUTCOME slot fix live since Stage C
   readout, where it matters, has still never actually run end-to-end).
4. **(Low, evidence says REJECT for these specific failures) Scale/developmental curriculum/
   grounding.** Does not explain mean-collapse (an objective-function property) or the SR/TD
   near-null-margin-across-all-arms (an information-content property of the task, not of model
   capacity or data volume). Real axis for a much later stage of this program, not a explanation of
   what already happened.

---

## 5. THE recommended mechanism -- decisive

**Recommendation: (b) + (a) combined, in that priority order. Abandon prediction-accuracy-vs-
baselines as the success criterion for the event/successor predictor; repurpose it explicitly as a
Kintsch-style CONSTRUCTION (candidate-overgeneration) stage feeding the ALREADY-VALIDATED
integration/coherence-filter organs (CausalLinkRegister 0.9722 given relations; the coherence-gated
self-improving loop; the inverse-planning extension of theory_of_mind_sally_anne_nested_hrr_v1 for the
goal axis). Do NOT pursue (c) developmental curriculum for this frontier -- rejected per Section 2.
Do pursue (a), joint error-driven segmentation, as the NEXT hardening step after (b) is wired, because
it improves construction-stage candidate quality but is not itself sufficient without the reframe.**

If this reads as "predict-next-event was simply the wrong framing" -- that is exactly the claim, and
it parsimoniously explains all 4 negatives without needing to claim event-level prediction-error
learning is impossible as a paradigm. The paradigm (error-driven, event-grain learning) survives;
what does not survive is grading its output as a stand-alone answer instead of as raw material for
the coherence-filter that already works.

### Concrete glass-box spec (buildable in FHRR/VSA, no borrowed embeddings, no bolt-on reader)

**Construction stage** (reuses the already-built SR/TD-style predictive map, `build_event_struct_v6`,
and the goal-inference candidate mechanism from the inverse-planning drill -- no new learning
machinery, a re-purposing of what already exists):

1. Run the TD-bootstrapped contrastive successor predictor (`experiments/exp_event_level_sr_td_
   contrastive_relation_inference_phase2_v1.py`'s trained map, already landed) not to output a single
   argmax next-event, but its full ranked TOP-K candidate list of successor-event vectors (K on the
   order of 5-10), fed by the accumulated context from `hdlab/situation_model_accumulate.py` +
   `hdlab/situation_model_multibank.py` (already WIRED_AND_PIPELINE_USED).
2. In parallel, run the inverse-planning candidate-goal-scoring loop (per `theory_of_mind_
   sally_anne_nested_hrr_v1`'s existing per-agent bank + nested bind/unbind + cosine-cleanup
   readout + refuse-gate, extended per the goal-inference drill's Section 1c) to produce a ranked
   TOP-K candidate goal-schema list per active agent, drawn from tier-1 (replay from the accumulate
   register) or tier-2 (a small hand-bootstrapped goal-primitive set: approach/avoid/acquire/protect/
   inform) -- never tier-3 (externally-supplied schema list, forbidden).
3. **Neither candidate stream is scored against ground truth at this point.** Both streams are
   structurally homogeneous (ranked lists of FHRR-bound hypotheses) and are simply PASSED FORWARD.

**Integration stage** (reuses `CausalLinkRegister`, already disk-verified 0.9722 vs 0.0 cross-chapter
baseline, extended per the goal-inference drill's Section 3 to accept both candidate streams jointly):

4. For a given relation query (unstated_goal / satisfy_restate / thwart_cause) about events A and B,
   score each (successor-candidate, goal-candidate) PAIR by whether it renders the accumulated causal
   graph COHERENT -- i.e., does adopting this successor-candidate as "what actually happened next" and
   this goal-candidate as "what the agent was pursuing" produce a causal chain through
   `CausalLinkRegister`'s existing connectivity/reachability check that is MORE internally consistent
   (higher chain-membership score, non-adjacent links included) than the alternative candidate
   combinations. This is exactly Baker et al.'s joint belief-desire attribution (goal and causal/
   predictive inference constrain each other, not independently thresholded) mapped onto the organ we
   already validated.
5. The coherence-gated self-improving loop (already built, "calibrated flag + coherence-gated
   autonomy, gold-free on dense") supplies the accept/refuse decision: if no candidate combination
   clears a coherence-margin-over-runner-up threshold, REFUSE (reuse the sally-anne organ's Q4
   refuse-gate mechanism directly) rather than force a low-confidence answer.

**Segmentation hardening (next step, not blocking)**: once the above is running, replace the
sentence-split Stage A with boundaries placed at local maxima of the construction stage's OWN
candidate-set entropy/incoherence (a cheap scalar already available from the top-K candidate scores
the construction stage produces) -- literally Reynolds-Zacks-Braver's "boundary = spike in the same
predictive error signal used everywhere else," now buildable because the construction stage already
computes a per-position candidate-quality signal it can report on itself, no new primitive required.

### Fair, faithful, CAN-FAIL pre-registered test

**MECHANISM_ARM**: the construction+integration pipeline above, answering held-out gold
SATISFY/THWART/CAUSE + unstated-goal queries.

**Baselines** (three-arm minimum, matching the sally-anne organ's own convention):
- **BASELINE_INTEGRATION_ONLY**: `CausalLinkRegister` fed ONLY explicit/marked relations already
  present in text (no construction/candidate-overgeneration stage at all) -- this is the crippled
  Option-B-style test, kept as the baseline it should have been treated as, isolating whether
  construction (candidate generation for UNSTATED content) adds value over integration alone.
- **BASELINE_LEXICAL**: word-overlap heuristic answer to the relation query.
- **BASELINE_RANDOM**: uniform over candidate relation labels.

**HARD-PASS** (deflated, capped at P=0.50 per lit-scan-calibration discipline for this novel
synthesis): on held-out, PARAPHRASED narrative material, specifically on the UNSTATED-relation subset
(the 6/9 inferred, not marked, goals per atom 29637's own gold measurement) --
(i) MECHANISM_ARM beats BASELINE_INTEGRATION_ONLY by a wide margin (not noise-level) on exactly the
UNSTATED items, since that is the one thing integration-only structurally cannot do (it only has
explicit relations to work with);
(ii) MECHANISM_ARM beats BASELINE_LEXICAL by >=0.20 absolute (mirrors the goal-inference drill's own
threshold);
(iii) the refuse-gate fires honestly (>=0.60) on a held-out genuinely-ambiguous set;
(iv) none of (i)-(iii) degrade under paraphrase (directly re-testing the paraphrase-brittleness
failure mode already observed once in the falsified supplied-schema fork).

**HARD-FAIL** (the honest negative that would NOT be spun as another artifact): MECHANISM_ARM does not
beat BASELINE_INTEGRATION_ONLY on the unstated subset (construction added nothing over what
integration already does with explicit relations alone), OR the gains vanish under paraphrase (same
brittleness class already seen once). If this HARD-FAILS while genuinely brain-faithful (joint
segmentation not yet required for this HARD-FAIL condition, since Section 2 argues the reframe is the
primary lever, segmentation the secondary one) -- **this would NOT be evidence against the
Kintsch/organ-reuse architecture per se; per WHERE_WE_ARE_NOW's own already-logged honest finding, it
would instead corroborate that the residual bottleneck is CONTENT quality (structure-aware meaning
representation, the "months-circled encoder problem"), not architecture** -- i.e. a HARD-FAIL here
would sharpen, not reopen, the diagnosis already on record (the deep-earn content-encoding fork), not
license a conclusion of "impossible."

### Lock-compatibility

- Construction stage: TD/contrastive learning rule is earned (own FHRR representations, own
  prediction error, no borrowed embedding) -- already certified in the SR/TD drill's lock section,
  unchanged here.
- Goal-candidate source: tier-1 (own replay/accumulate buffer) or tier-2 (small hand-bootstrapped
  goal-primitive set, matching the standing "bootstrap primitive by hand, then hand rule-learning to
  the loop" discipline) -- both lock-compatible; tier-3 (external/LLM-supplied schema list) explicitly
  forbidden, as already flagged in the goal-inference drill.
- Integration stage: reuses `CausalLinkRegister` and the coherence-gated loop unchanged -- no new
  lock exposure, both already-validated organs.
- No bolt-on reader/parser anywhere in this spec; no borrowed-embedding encoder as mechanism.

### What is NEW in this synthesis vs the 5 background docs (credit where already earned, no
re-derivation)

- Docs 1-2 (phase1/v2 audits) did the component-by-component SHAPE/POSITION/METRIC mapping and
  correctly diagnosed window-starvation and surface-metric mismatch for v1/v2 specifically -- carried
  forward, not re-derived.
- Doc 3 (encoder-target drill) established the event/predicate-grain, componential-content
  conclusion -- carried forward.
- Doc 4 (SR/TD drill) supplied the TD/contrastive mechanism and FIRST proposed the Kintsch
  construction-integration frame as a "secondary, necessary complement" (its own Rank 2, P=0.55) --
  written BEFORE the SR/TD run executed, so it could not yet use that run's own result as evidence.
- Doc 5 (goal-inference drill) supplied the inverse-planning mechanism and independently converged on
  the same construction-integration frame from the goal axis.
- **This doc's own contribution**: (i) the cross-run adjudication of all 4 failures against three
  named hypotheses, using the SR/TD run's specific near-null-margin-ACROSS-ALL-ARMS signature (not
  available to docs 4-5 when written) as the decisive evidence that promotes "wrong success
  criterion" from a secondary complement (doc 4's Rank 2) to the PRIMARY explanation, ranked above
  segmentation; (ii) an explicit test-and-reject of the scale/curriculum hypothesis against the actual
  failure signatures, rather than leaving it open; (iii) one unified, ranked, pre-registered can-fail
  spec that composes construction (docs 4+5) with integration (docs 1-2's own Corrections 1-2) into a
  single testable pipeline with an honest HARD-FAIL condition that explicitly does not default to
  "impossible" but instead sharpens the already-logged content-encoding fork.

## Citations

All citations (Zacks & Swallow 2007; Zacks, Speer, Swallow, Braver, Reynolds 2007; Reynolds, Zacks &
Braver 2007; Speer, Zacks & Reynolds 2007; Trabasso & van den Broek 1985; Zwaan & Radvansky 1998;
Zwaan, Langston & Graesser 1995; Mar 2011; Kintsch 1988/1998; Dayan 1993; Stachenfeld, Botvinick &
Gershman 2017; Zheng et al. 2024 ICLR CDPC; Baker, Saxe & Tenenbaum 2009; Baker, Jara-Ettinger, Saxe &
Tenenbaum 2017) are carried forward, DOI/venue-verified in the five background docs listed at the top
of this file, not re-verified independently here -- this doc's contribution is the cross-run
adjudication (Sections 1-3), the ranked gap list (Section 4), and the unified mechanism + can-fail
spec (Section 5), verified count: 0 new citations fetched this session (deliberately reusing, not
re-deriving, per the task's own instruction not to re-earn credit already on record).

## HEADLINE

Across all 4 event-level relation-inference negatives, the single most parsimonious, load-bearing
deviation from the brain is not any one run's specific bug (each had its own, already correctly
diagnosed) -- it is that **every operationalization graded a construction-stage mechanism (predict
the next event) as if it were the final answer, when the brain's own architecture (Kintsch
construction-integration) never asks that stage to be individually accurate; it asks a downstream
coherence-filter (which we have already built and validated at 0.9722) to pick a good answer out of a
deliberately loose, mostly-wrong candidate set.** The SR/TD run's near-null margin ACROSS ALL
BASELINES SIMULTANEOUSLY (not a loss to one baseline) is the decisive evidence for this, because it
shows accurate top-1 prediction is close to an information-theoretic ceiling for real prose at this
grain, for any method -- consistent with human next-word/next-sentence prediction being genuinely hard
too. Recommendation: repurpose the already-built SR/TD predictor and the inverse-planning goal-scorer
as Kintsch-style CONSTRUCTION (overgenerate ranked candidates, unscored against ground truth) feeding
the already-validated CausalLinkRegister + coherence-gated loop as INTEGRATION (which answers the
actual relation queries); harden joint error-driven segmentation next, as a candidate-quality
improvement, not the primary fix; explicitly reject scale/curriculum as an explanation for these 4
specific failure signatures. P_deflated=0.50 (capped, novel synthesis) that this reframe resolves the
frontier; if it HARD-FAILS on the pre-registered test above, that sharpens (does not reopen) the
already-logged content-encoding deep-earn fork as the next investment, not a verdict of impossibility.
