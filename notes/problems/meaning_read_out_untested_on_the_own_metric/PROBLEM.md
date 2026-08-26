---
review: EXCELLENT
review_text: EXCELLENT REFUTED+PARTIAL, re-verified PASS (instrument reproduces to the digit; READOUT_TIES_OR_LOSES_COUNTING confirmed all 3 seeds). The read-outs LOSE to counting on the own metric -> WIRING = NO. Honest sub-threshold brain signal (TOPK_GROUNDED beats its twin, CI touches zero). Surfaced the metric is carried by RAW FREQUENCY (PMI collapses 8x) -> packaged metric-fairness + TOPK_GROUNDED-pursuit as new problems. No hdlab landed (the answer is not to wire).
---

> ## SOLVER REVIEW -- EXCELLENT (REFUTED the premise + honest PARTIAL; integrated by strategy 2026-08-25)
> **Re-verified (WITNESS PASS):** `verification/test_meaning_readout_own_metric.py` reproduces the own-metric
> instrument TO THE DIGIT and confirms `READOUT_TIES_OR_LOSES_COUNTING_ON_OWN_METRIC` on all 3 powered seeds.
> **Decisive finding:** the meaning read-outs (fusion, taught direction, second-order reading) LOSE to
> first-order co-occurrence COUNTING, CI-separated BELOW it, every seed -- the WordSim/substitutability wins
> do NOT transfer to the own metric. **So the two decisions this gate governs are settled: (a) stage 2 is NOT
> fixed by these read-outs; (b) WIRING = NO -- do not wire them into the live reader.** A rigorous negative is
> an explicit PASS.
> **Why EXCELLENT (grading quality, not verdict):** reproduces the instrument exactly; ran the mandated
> info-free twin AND extra controls (oracle ceilings prove misses are RANKING failures, not coverage); the
> vectorized scorers match the live organ APIs to <3e-15; and it did NOT overclaim -- the brain-foundational
> TOPK_GROUNDED mechanism (frequency-salience selects, grounded hub discriminates) beats its shuffled twin
> CI-separated and beats counting NUMERICALLY, but its CI touches zero, and it is reported as sub-threshold.
> **The deeper thing it surfaced (now packaged, per owner "package significant problems for solvers"):** the
> own metric is carried by RAW FREQUENCY -- PMI-normalising it collapses the signal 8x, so every meaning
> transform loses BECAUSE it de-emphasises frequency. That questions whether the metric tests MEANING or
> FREQUENCY. Packaged as: (1) is the grounding-precision metric a fair test of meaning?; (2) push
> TOPK_GROUNDED + the 3 brain-faithful encoding arms over threshold on a fair metric.
> **Integration:** no `hdlab/` landed (the answer is NOT to wire). Review recorded; priority cleared.

# PROBLEM: the meaning wins are on BORROWED scorers -- do they beat plain counting on the substrate's OWN metric, where the stage is actually broken?

## 1. THE PROBLEM IN PLAIN LANGUAGE

This week two ways of judging word meaning beat their controls: one tells true synonyms from mere
associates, one combines "reading" and "hands-on feel" for general similarity. But both were scored
on BORROWED yardsticks (a standard synonym set; a standard similarity set). The substrate's meaning
step is declared BROKEN on a DIFFERENT, home-grown yardstick -- assigning the right meaning to a word
it just read -- where plain word-counting still beats us. Nobody has checked whether the new
read-outs beat plain counting on THAT home yardstick. No number crosses yardsticks, so we do NOT yet
know whether the wins fix the thing that is actually broken.

## 2. WHY THIS ONE

Stage 2 ("decide what words mean") is the one stage that decides whether the system understands what
it read -- nine of ten others do not change that answer. We now have candidate fixes proven on
borrowed tests. This gates two things: (a) declaring stage 2 fixed, and (b) the wiring decision -- if
a read-out beats counting on our OWN metric, wire it into the live reader; if it ties or loses
counting there, we have improved a different task and must NOT claim the wall is down.

## 3. HOW THE BRAIN DOES THIS (frame + discipline, not a new mechanism)

This is a discipline check, not a new organ. The brain's semantic hub integrates modality spokes
(PINNED; Patterson, Lambon Ralph); the question is whether that integration, measured on OUR
assignment task, beats the simplest text summary (co-occurrence counting). Copy the OPERATION
(integrate spokes / apply the taught direction) exactly; do NOT import a number from another task.
This is the project's "no number crosses scorers" rule turned into an experiment.
**EXTENDED 2026-08-25 (owner: "always be as brain-faithful as possible"):** the reading spoke's
co-occurrence ENCODING is itself a brain mechanism, not just plumbing -- so beyond the plain read-out,
also test the three brain-faithful encoding refinements in section 7B. We want the MOST brain-faithful
version that clears, not merely a version that clears.

## 4. MEASURED vs INFERRED

MEASURED: on the substrate's OWN meaning-assignment / grounding-precision metric, plain first-order
co-occurrence COUNTING scores ~0.048-0.065 and our live meaning step scores ~0.016-0.030 (counting
wins 2-3x, 3 seeds; exp_grounding_precision_gold_v1). The fusion read-out scores ~0.45 on WordSim
SIMILARITY (meaning_fusion); the taught direction scores ~0.84 on the licensed SUBSTITUTABILITY set
(distributional_meaning_channel). These are DIFFERENT scorers.
INFERRED (the open question, fair game to overturn): that the fusion read-out and/or the taught
direction beats counting on the OWN metric. Plausibly it does NOT transfer -- substitutability is
near-opposite to relatedness, and the own metric is neither.

## 5. ALREADY TRIED (do not re-run)

- The LIVE write rule vs counting on the own metric -- measured (counting wins). Do NOT re-measure the
  live rule; measure the NEW read-outs.
- The fusion / taught-direction read-outs on WordSim / substitutability -- they win THERE. Do NOT
  re-run those; the question is TRANSFER to the own metric.
Query `experiment_index.py query "grounding"`, `query "precision"`, and check the ledger first.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Read `data/exp_grounding_precision_gold_v1/` and confirm the counting floor and the live-rule number
  on the own metric, on its own population (recompute the floor there; do not paste).
- Confirm the read-outs exist and self-test: `hdlab/meaning_fusion.py`,
  `hdlab/distributional_meaning_channel.py`.

## 7. THE BAR

On the substrate's OWN meaning-assignment / grounding-precision instrument (same population and scorer
as the 0.016-0.065 numbers above): a read-out (fusion of reading+grounded, and/or the taught
direction), applied through the read-out path, must beat first-order co-occurrence COUNTING
CI-separated over that floor's UPPER bound, with an information-free twin (shuffled grounding / random
direction) LOSING. Save the scored population. HOW WE WOULD KNOW IT FAILED: it ties or loses counting
on the own metric -- then the borrowed-scorer wins do not fix the broken stage, and that is the
(valuable) result to report.
**AND test not just the plain read-out but the three BRAIN-FAITHFUL ENCODING ARMS in 7B, each against
the same counting floor with its OWN info-free twin.**

## 7B. THE BRAIN-FAITHFUL ENCODING ARMS -- FOLD THESE IN (owner 2026-08-25: "always be as brain-faithful as possible")

The read-out reads a co-occurrence store that change 2 now fills for EVERY content word
(`track_all_content_lemmas`, hdlab/reading_grounding_loop.py). But that store's ENCODING is a FLAT,
UNIFORM, NEVER-FORGETTING bag -- three places the brain does something specific. Build the plain store
AND each refinement below as a separate ARM; COPY the computation, SWEEP the parameter (the warrant is
the BRAIN mechanism, NOT a word2vec default -- do not adopt an ML number).

**ARM A -- GRADED TEMPORAL WINDOW** (vs the flat sentence bag).
- BRAIN (PINNED): associative binding falls off with temporal/serial distance -- Temporal Context Model
  (Howard & Kahana 2002); contiguity + recency in free recall.
- COPY: weight each co-occurrence by a decreasing function of token distance d between target and context
  word (e.g. exp(-d/tau) or 1/d), not a flat 1 per in-sentence pair.
- SWEEP: window width / tau. Needs the store to carry POSITION, not just a multiset.

**ARM B -- PREDICTION-ERROR / SURPRISE-WEIGHTED ENCODING** (vs uniform counting). SAME MECHANISM AS p3.
- BRAIN (PINNED): encoding is gain-modulated by attention + prediction error -- surprising pairings are
  written more strongly (LC-NE novelty/salience; dopamine RPE; Rescorla-Wagner / TD: update ~ error).
  This is the ONLINE form of the pattern-separation the OFFLINE PPMI currently stands in for.
- COPY: weight each update by its surprise under the CURRENT store BEFORE the update
  (surprise = -log P(context|target), pre-update). Expected pairings add little; surprising ones a lot.
- SWEEP: surprise gain / temperature.
- TRAP (control it): surprise-from-the-store uses the store to weight the store -- keep it NON-CIRCULAR
  (pre-update probability ONLY) and require the info-free twin (SHUFFLED surprise weights) to LOSE.
  Cross-reference p3 -- this is its reliability signal in encoding form.

**ARM C -- DECAY + CONSOLIDATION** (vs unbounded additive counts).
- BRAIN (PINNED): hippocampal traces decay (Ebbinghaus) and consolidate to cortex (CLS systems
  consolidation). Recent + repeated survive; one-off old fade. Also bounds the store's growth the brain's
  own way (the change-2 memory caveat).
- COPY: decay counts by elapsed exposures (multiply by rho^dt) and/or promote stable co-occurrences to a
  slower store; recent weighs more.
- SWEEP: decay half-life.
- HONEST CAVEAT (fair game to LOSE): at our corpus scale the episodic tier fires on only ~10% of items
  (teach_the_self_built SOLVED) -- decay makes it sparser and may HURT here even though it is more
  faithful. A faithful mechanism that loses at THIS data scale is a real, reportable result; do not force it.

**SCORING (every arm, identical):** the arm's store -> the SAME PPMI+SVD read-out -> scored on the OWN
metric against the SAME first-order COUNTING floor, floor recomputed on the arm's own population, EACH arm
with its OWN info-free twin that MUST LOSE. Report which arm(s) clear counting CI-separated over the
floor's upper bound. Plain change-2 store = baseline arm; the three refinements are judged against it AND
against counting.

## 8. FILES AND ENTRY POINTS

- `data/exp_grounding_precision_gold_v1/` -- the own-metric instrument and the counting floor.
- `hdlab/meaning_fusion.py`, `hdlab/distributional_meaning_channel.py` -- the read-outs to score.
- `hdlab/reading_grounding_loop.py` -- `ConceptSpace.observe_context_counts` + `process_sentence` (the
  co-occurrence ENCODING site; `track_all_content_lemmas` fills it for all content words). The three 7B
  arms are variants of THIS encoding step -- prototype them here in a can-fail cell, do not land hdlab/.
- Prove in `experiments/` + `verification/`; propose any hdlab wiring in `SOLVED.md` (strategy lands it,
  board Q111). Do NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT quote the WordSim ~0.45 or the substitutability ~0.84 as if they apply to the own metric --
  different scorers, the whole point of this problem.
- Do NOT re-measure the live write rule vs counting (already done); measure the NEW read-outs.
