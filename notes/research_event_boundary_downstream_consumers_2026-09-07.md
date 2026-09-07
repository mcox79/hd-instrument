# Research: what does an event boundary CONSUME? — downstream-consumer map for `sem_event_segmenter` (2026-09-07)

Dispatched by Director: `hdlab/sem_event_segmenter.py` (Franklin/Gershman SEM schema-switch segmenter, Kumar-2023-validated,
rho ~0.12-0.15 vs actual humans = 56-68% of the noise ceiling, beats GPT-2 Bayesian surprise) is a LATENT island — no
live consumer. Question: brain-foundationally, what computation does a detected event boundary TRIGGER downstream,
so we wire the segmenter into the thing the brain actually feeds. 3 parallel Sonnet lit-scan sub-agents fetched and
read 11 primary sources live (PubMed/PMC/ScienceDirect/Nature/journal PDF); this note integrates their findings with
disk-verified facts about `hdlab/hippocampal_encoder.py`, `hdlab/situation_model_accumulate.py`,
`hdlab/bound_event_backbone.py`, and `hdlab/graded_coref_pick.py` (the LIVE default coref decay — see correction below).

Builds on, does not repeat: `notes/research_brain_event_segmentation_2026-08-05.md` (the segmentation MECHANISM
itself, Zwaan/Zacks/Baldassano) and `notes/problems/close_the_recurrent_predictive_coding_loop.../
research_event_segmentation_mechanism_2026-09-07.md` (the SEM computation that IS `sem_event_segmenter`, same-day).
Neither addresses what a boundary is CONSUMED BY once detected — that gap is this note.

## Disk-fact correction (verified before writing this note)

The task's disk fact (iv) — "coref uses ACT-R recency/activation" via `event_centrality_coref`'s Cowan-4 EventMemory
centrality tie-break — is **stale as of 2026-09-06**. Reading `hdlab/event_centrality_coref.py` and
`hdlab/graded_coref_pick.py`: the EventMemory centrality tie-break is now FORCED OFF by default (`graded_pick=True`
sets `query_memory=False`, because it measurably hurt: 0.4876 EC-off vs 0.4693 EC-on). The LIVE default pronoun pick
is `graded_coref_pick.graded_antecedent_pick` — a PINNED ACT-R base-level activation `A_i = ln(sum_k w_role(k) *
dt_k^-d)` where `dt_k = p_sent - m_sent + 1` is **pure linear sentence distance**, `d=3.0` (swept). This is actually
a BETTER hook than the old EventMemory: it is the exact ACT-R decay term the event-horizon literature (below) says
should have a boundary-crossing discontinuity added, and it is the mechanism that is actually live and scored.

## HEADLINE

Boundary-crossing has three literature-convergent downstream effects, ranked by build cost x evidence strength x
gap size on THIS substrate: **(1) an event-horizon discontinuity in retrieval/accessibility — cheapest, highest
leverage, and the current live coref decay term (`graded_coref_pick`) is missing exactly this term; (2) a
boundary-gated (not reset) situation-context blend — the substrate's accumulate-register already has the right
SHAPE (bundle = blend, not overwrite) but the blend is not currently triggered BY a boundary, it just runs flat
forever; (3) a boundary-phasic hippocampal write/reinstatement gate — the richest neural evidence, but the largest
build (touches `hippocampal_encoder`'s write path).** `bound_event_backbone`'s N400-monitor chunker (`segment_sizes`)
is the WRONG wire target regardless of which segmenter feeds it — it is dead output today and would stay dead output
with `sem_event_segmenter` substituted in, because nothing downstream of `BoundEpisodicStore` reads `segment_sizes`.
**P_deflated=0.45** (lit-scan calibration penalty applied; novel-synthesis cap 0.50; the 11 underlying citations are
individually high-confidence, primary-source-verified — the deflation is on the SYNTHESIS/ranking, not the papers).

## 1. Boundary-triggered episodic ENCODING (hippocampal write-gate)

**Verified primary sources** (Ben-Yakov & Dudai 2011, *J Neurosci* 31(24):9032-9042, DOI 10.1523/JNEUROSCI.0702-11.2011,
PMC6622928; Ben-Yakov & Henson 2018, *J Neurosci* 38(47):10057-10068, DOI 10.1523/JNEUROSCI.0524-18.2018, PMC6246887;
Sols, DuBrow, Davachi & Fuentemilla 2017, *Current Biology* 27(22):3499-3504, DOI 10.1016/j.cub.2017.09.057,
PMID 29129536):

- Ben-Yakov & Dudai 2011: hippocampal (+ dorsal striatal) activity **time-locked to clip OFFSET** is higher for
  later-remembered vs later-forgotten clips, with **no difference in activity during the ongoing clip** — the
  memory-predictive signal is discrete and appears only after offset, not a continuous accumulation.
- Ben-Yakov & Henson 2018: hippocampal BOLD shows discrete, boundary-locked transients scaling with boundary
  SALIENCE (how many independent observers agreed a boundary occurred there) — a phasic write-trigger, not a flat
  rate. (This paper does NOT itself test subsequent-memory prediction — that is Ben-Yakov & Dudai 2011's result;
  flagging the correction since the two are often conflated.)
- Sols/DuBrow/Davachi/Fuentemilla 2017 (title: "Event Boundaries Trigger Rapid Memory Reinstatement of the Prior
  Events to Promote Their Representation in Long-Term Memory" — note: Norman is NOT an author, corrected from the
  task's guess): scalp-EEG pattern similarity shows that **crossing a new boundary triggers rapid (~200-800ms)
  spontaneous reinstatement of the just-completed event's neural pattern**, and the reinstatement magnitude
  correlates with later cross-episode memory binding. This happens automatically during encoding, not on explicit
  recall demand.

**Verdict: encoding IS gated at boundaries — write/consolidation strength is boundary-phasic, and the moment of
writing is accompanied by a brief REPLAY of the just-closed event, not a steady per-item trickle.**

**Substrate mapping / fidelity gap:** `hdlab/hippocampal_encoder.py` `HippocampalEncoder.encode_and_write` (lines
274-280) loops every row of `X` and calls `self.ca3.write(codes[i])` uniformly — **every item gets an identical
one-shot Hebbian write, with no boundary-adjacency weighting and no replay-burst step**. This is a genuine fidelity
gap: CONFIRMED via `retrieve()`'s signature (`Q, use_ca3, sparsify_after_settle`) taking no boundary argument. The
substrate DOES already have the right machinery type for a fix — `cls_discrete_budget_consolidate` (same file,
lines 356-441) is a certified (CHAIN_GRADE) discrete-budget offline replay mechanism with a partial-cue SWR
mechanic — it just prioritizes replay uniformly (`replay_keys[:budget]`) rather than by boundary-adjacency salience.

## 2. Boundary-triggered event horizon / accessibility drop + order-memory disruption

**Verified primary sources** (Radvansky & Copeland 2006, *Memory & Cognition* 34(5):1150-1156, DOI
10.3758/BF03193261; Radvansky 2012, *Current Directions in Psych Science* 21(4):269-272; Radvansky & Zacks 2011,
*WIREs Cognitive Science*, DOI 10.1002/wcs.133; DuBrow & Davachi 2013, *J Exp Psych: General* 142(4):1277-1286, DOI
10.1037/a0034024, PMID 23957281; Ezzyat & Davachi 2011, *Psych Science* 22(2):243-252, DOI
10.1177/0956797610393742; Clewett, Gasser & Davachi 2020, *Nature Communications* 11:4007, DOI
10.1038/s41467-020-17851-9, PMID 32782282):

- **The "doorway effect"** (Radvansky & Copeland 2006): walking through a doorway (crossing a spatial event
  boundary) causes worse object-recognition accuracy for the just-left room's contents than an equal-distance
  walk WITHOUT a boundary. Distance is matched — the effect is the BOUNDARY, not elapsed time/distance.
- **The event horizon model** (Radvansky 2012; Radvansky & Zacks 2011): once a new event model opens, content from
  the just-closed event model drops in accessibility — a discontinuous step, not gradual decay.
- **DuBrow & Davachi 2013**: temporal-order memory is WORSE for item pairs that SPAN a boundary than for pairs
  WITHIN one event; order memory within an event is comparatively preserved. (A 2022 DuBrow-lab follow-up shows
  this can flip to enhancement under certain retrieval-task framings — the impairment result is the baseline.)
- **Ezzyat & Davachi 2011 + Clewett/Gasser/Davachi 2020**: items separated by a boundary are judged FARTHER apart
  in subjective time than same-true-distance within-event pairs (temporal expansion); Clewett et al. show this is
  accompanied by a **phasic pupil-dilation burst time-locked to the boundary itself** (not a ramp), which the
  authors tie to an LC-norepinephrine "network reset" signal, with the early pupil component tracking subjective
  expansion and a slower component predicting the order-memory impairment.

**Verdict: this is the strongest, most directly actionable finding — a documented DISCONTINUOUS accessibility drop
and order-memory disruption specifically AT boundaries, distinct from (additive to) ordinary recency decay, with a
phasic physiological marker confirming it is boundary-LOCKED, not gradual.**

**Substrate mapping / fidelity gap:** `hdlab/graded_coref_pick.py` `graded_antecedent_pick` (line 94) computes the
live ACT-R activation as `s = sum(ROLE_W[r] * dt(p_sent, sent)**(-d) ...)` — **pure linear sentence-distance decay,
with NO boundary-crossing term at all.** The event-horizon literature predicts a candidate whose only prior mention
sits across a segmenter-detected boundary from the pronoun should be systematically LESS accessible than the
distance-only decay currently gives it — an independently testable, currently-absent term. This is a precise,
small, high-confidence fidelity gap on the substrate's OWN live default pick, not a hypothetical.

**Secondary connection — the temporal reasoner.** `reason_over_event_time_order_and_duration_on_a_modern_gold` is
already INTEGRATED (`hdlab/temporal_reasoner.py`, before/after/overlap/duration over the timeline, TB-Dense/MCTACO
modern gold, 0.5933->0.6225 CI-sep). DuBrow & Davachi 2013 predicts before/after judgment accuracy (or confidence)
should be LOWER specifically for item pairs that cross a segmenter-detected boundary than for within-event pairs —
this is a **measurement-only** correlation against an ALREADY-BUILT, ALREADY-SCORED capability, zero new mechanism
required. See "cheap decisive test" below — this should run BEFORE committing engineering to fix #1.

## 3. Boundary-triggered situation-model update: gated BLEND, not reset

**Verified primary sources** (Franklin, Norman, Ranganath, Zacks & Gershman 2020, *Psych Review* 127(3):327-361,
DOI 10.1037/rev0000177; Pu, Kong, Ranganath & Melloni 2022, *Nature Communications* 13:622, DOI
10.1038/s41467-022-28216-9; Speer, Zacks & Reynolds 2007, *Psych Science* 18(5):449-455, DOI
10.1111/j.1467-9280.2007.01920.x; Sargent et al. 2013, *Cognition* 129(2):241-255, DOI
10.1016/j.cognition.2013.07.002):

- **Franklin/Gershman SEM 2020**: at a schema switch, the schema's LEARNED forward-dynamics parameters persist and
  are REUSED across future events assigned to that schema (a library, sticky-CRP reassignment) — "reset the
  instance, keep the schema," not full erasure. (Exact reset-of-instance-state wording not independently
  quote-verified by the sub-agent; the sticky-CRP reusable-schema architecture IS confirmed from multiple sources.)
- **Pu, Kong, Ranganath & Melloni 2022 — the exact equation**: `Ct = (1-lambda)[(1-p)*Ct-1 + p*C_IN] + lambda*C1` —
  a **gated, leaky blend**, explicitly NOT a hard reset to zero (despite the paper's title using "resetting"). At a
  boundary, the new context is normal drift PLUS a partial (proportion `lambda`) reinstatement of the FIRST event's
  context. This produces the paper's "dual role" result: boundaries IMPROVE within-event order memory but only
  PARTIALLY impair across-event order memory, plus a primacy-carryover effect — evidence against a wipe.
- **Speer, Zacks & Reynolds 2007**: DMN-adjacent regions (mPFC etc.) show transient activity increases at
  boundaries that track SITUATION-MODEL change specifically (e.g. goal shifts), not generic stimulus change —
  confirms the update is content-driven, not just "something happened."
- **Sargent et al. 2013**: individual differences in segmentation ability (agreement with normative boundary
  placement) UNIQUELY predict later event memory, independent of general cognitive ability — segmentation quality
  is causally/functionally upstream of memory quality, not a side effect of it.

**Verdict: the brain's update rule at a boundary is a gated partial-reinstatement blend of the prior context, not
a wipe — and this SHAPE (blend > overwrite) is something this substrate has ALREADY validated, just not yet coupled
to a boundary signal.**

**Substrate mapping / fidelity gap — the most interesting cross-thread finding of this drill:**
`hdlab/situation_model_accumulate.py`'s `AccumulateRegister` is validated (atom 29609) at **accumulate=1.0000 vs
overwrite=0.4600 vs floor=0.2100** — i.e. the substrate has ALREADY measured that blend-via-bundle beats
hard-overwrite, which is directionally the SAME finding as Pu et al.'s reset-vs-blend result. It even has a
`leak` parameter (Warden & Miller 2007 asymmetric recency write) that geometrically down-weights OLD events —
structurally close to Pu et al.'s `lambda*C1` term. **But the accumulation and the leak both run flat/continuously,
uncoupled to any boundary signal** — `event_idx` (the register's own boundary-index register) is caller-supplied
and nothing on disk auto-advances it at a detected schema switch (CONFIRMED: `add_event(entity, role, event_idx)`
requires the caller to pass `event_idx`; no method inspects a boundary flag). `bound_event_backbone.py`'s CHUNK
tier (`N400CoherenceMonitor`, producing `segment_sizes`) computes boundaries but **`segment_sizes` has zero
readers** (confirmed by grep — appears only in its own constructor call and attribute assignment, `resolve()` /
`corefer()` only touch `self.tokens`). This is why "swap the chunker for `sem_event_segmenter`" is a dead end AS
STATED — the pipe downstream of the chunker doesn't exist yet, independent of chunker quality.

## Ranked verdict — the three consumers, by build cost x evidence x current gap

| Rank | Consumer | Organ | Boundary-triggered computation | Build size | Fidelity gap today |
|---|---|---|---|---|---|
| 1 | Event-horizon retrieval/coref prior | `hdlab/graded_coref_pick.py` | Add a boundary-crossing discontinuity term to the ACT-R decay (on top of, not instead of, linear distance) | SMALL — one term in one live-scored function | Present, precise, cheap to fix |
| 2 | Gated situation-context blend | `hdlab/situation_model_accumulate.py` + `hdlab/bound_event_backbone.py` | Auto-advance `event_idx` at a detected schema switch; make `leak`/accumulate boundary-gated (Pu et al. equation) instead of flat | MEDIUM — wires an existing validated mechanism (accumulate>overwrite) to an existing detector | The SHAPE is already right; only the trigger is missing |
| 3 | Hippocampal write-gate + reinstatement replay | `hdlab/hippocampal_encoder.py` | Weight/replay-prioritize CA3 writes by boundary-adjacency salience (reuse `cls_discrete_budget_consolidate`'s replay machinery, boundary-weighted instead of uniform) | LARGEST — touches the write path + needs a designed recall task | Fully absent; richest neuroscience evidence but most surgery |

`bound_event_backbone`'s N400-monitor chunker: **not a consumer to fix** — its output has no reader regardless of
segmenter quality; fixing #2 (wiring `event_idx` advancement) is the correct way to give a segmenter's boundaries
a live effect, and it can use `sem_event_segmenter` directly as the boundary source once #2 exists.

## Cheap decisive test (run FIRST, before any build — zero new mechanism)

Correlate `sem_event_segmenter`'s boundary output against the ALREADY-INTEGRATED, ALREADY-SCORED
`hdlab/temporal_reasoner.py` before/after judgments on TB-Dense/MCTACO (both on disk, no 19c): for each scored
before/after item, does the item pair CROSS a segmenter-detected boundary (feed the reader's own per-sentence scene
vectors through `SEMEventSegmenter.observe()`, exactly per the module's documented wiring contract) or sit WITHIN
one event? This requires zero hdlab changes — it is a measurement correlating two already-built, already-verified
capabilities, and it directly tests whether the DuBrow & Davachi 2013 effect (worse order memory across boundaries)
shows up in OUR extracted representations before committing engineering to fix #1's coref decay term.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction A — event-horizon term in coref (Rank 1 build).** Adding a boundary-crossing decay term to
`graded_antecedent_pick`'s ACT-R activation (`A_i` multiplied by a boundary penalty, e.g. `exp(-beta * n_boundaries(k,
p_sent))`, beta swept) improves live pooled he/she coref accuracy on GUM/UD-EWT (modern, not 19c) over the current
pure-distance decay, CI-separated, with an info-free twin (shuffled boundary positions, same boundary COUNT/rate)
losing CI-separated.
- **HARD-PASS:** margin >= +0.01 CI-separated over the current default (`graded_pick` baseline, currently 0.6019
  pooled per `event_centrality_coref.py`'s own docstring), AND the shuffled-boundary twin loses by >= half that
  margin.
- **HARD-FAIL:** margin < +0.003 (below noise) OR the shuffled-boundary twin performs statistically indistinguishably
  from the real-boundary arm (meaning the term is tracking generic distance-noise, not boundary structure) — in
  that case the located cause is that `sem_event_segmenter`'s self-consistency (not human-validated correspondence)
  is too noisy a boundary signal for THIS use, not that the event-horizon effect doesn't exist.

**Prediction B — DuBrow order-memory correlation in the temporal reasoner (the cheap decisive test above).**
- **HARD-PASS:** before/after accuracy (or confidence margin) on TB-Dense/MCTACO items is measurably lower for
  boundary-crossing pairs than within-event pairs, matched for raw sentence distance, by >= 5 points, CI-separated.
- **HARD-FAIL:** no measurable gap (< 2 points, or CI-overlapping), OR the gap reverses sign — in that case the
  located cause is likely that the reader's own boundary detection and its own event/tense extraction are too
  correlated (the same underlying situation-model discontinuity drives both), making the correlation circular
  rather than informative; the test would need an INDEPENDENT boundary signal (e.g. the human-validated Kumar 2023
  archive's own boundaries, already fetched per SOLVED.md, if a comparable narrative text is used) to be decisive.

**Prediction C — accumulate register boundary-gating (Rank 2 build).** Auto-advancing `event_idx` at a detected
boundary (instead of leaving it caller-managed/static) and/or making `leak` boundary-triggered (a bigger decay step
specifically across a boundary vs within-event, per the Pu et al. equation) improves multi-event entity-tracking
decode accuracy at higher event loads (where the existing flat-bundle capacity cliff bites, per
`situation_model_multibank`'s own docstring: flat degrades to 0.6547 at n_events=256) relative to the current
flat/unboundaried accumulate, with an info-free twin (boundary positions shuffled) losing.
- **HARD-PASS:** >= 0.03 decode-accuracy lift at the load where flat already shows measurable degradation (per the
  cited multibank comparison), CI-separated, shuffled-boundary twin losing.
- **HARD-FAIL:** no lift, or the flat accumulate is already at its ceiling in the tested regime (in which case
  boundary-gating is a capacity-headroom fix for book-scale loads, not a near-term score mover — a legitimate,
  reportable located negative, not a failure of the mechanism).

## Cross-thread synthesis

This drill connects three previously-separate substrate threads that had not been linked: (a) the SEM segmenter
landing (SOLVED SS4h-4o, today's sister note) proved the boundary DETECTOR is human-validated; (b) the
accumulate-vs-overwrite result (atom 29609, `situation_model_accumulate` SOLVED) already proved the blend-not-reset
SHAPE independently, years before this drill connected it to Pu et al. 2022's boundary-reset literature; (c) the
graded ACT-R coref pick (landed 2026-08-28, made default 2026-09-06) already carries the exact currency
(recency-decayed activation) the event-horizon literature says needs a boundary term, but was built and landed
without that connection being drawn. None of these three needed new machinery to test the highest-leverage
prediction (A) — they needed to be WIRED to each other. This is a `[[feedback-dont-dismiss-adjacent-methods]]`-shaped
finding: the "obvious" wire target (`bound_event_backbone`, the module literally named for events) was a dead end,
while the actual leverage point was a module (`graded_coref_pick`) that doesn't mention "event" or "boundary"
anywhere in its name or docstring.

## Substrate-product implications

A segmenter that just emits `is_boundary` flags is not a product feature; a segmenter whose boundaries measurably
change WHO a pronoun resolves to, or WHETHER two events are judged correctly ordered, is. The single highest-value,
lowest-cost next step is Prediction A's build: it touches one already-live, already-scored function
(`graded_antecedent_pick`), reuses a validated detector (`sem_event_segmenter`) and a validated scoring pipeline
(GUM/UD-EWT coref board arm), and has a documented human-behavioral effect size range to aim for (DuBrow & Davachi's
and Radvansky's effects are large and replicated, not marginal). It also de-confounds a standing substrate question:
whether the ACT-R decay's `d=3.0` exponent (swept, not brain-pinned) is doing double duty as a proxy for boundary
crossings in narratives where boundaries and distance correlate — separating them will tell us whether `d` should
shrink once a real boundary term is added (the decay currently has to be steep enough to catch boundary effects it
can't see directly).

## VERDICT

**Yes, giving the SEM segmenter a live consumer is a good SOLVER problem — but the brief must NOT be framed as
"wire `sem_event_segmenter` into `bound_event_backbone`'s chunker."** That pipe has no reader on the other end
(`segment_sizes` is dead output regardless of chunker quality) and swapping the segmenter there would produce a
zero-measurable-effect landing — a wasted cycle that LOOKS wired but isn't live-scored. Frame the brief instead
around the CONSUMER, not the segmenter: **"give the live coref pick an event-horizon term"** — name
`graded_coref_pick.py`'s ACT-R decay as the target, `sem_event_segmenter` as the boundary source, DuBrow & Davachi
2013 / Radvansky 2012 as the brain-foundational mechanism to replicate (a boundary-crossing discontinuity ON TOP OF
recency decay, not instead of it), GUM/UD-EWT (modern, not 19c) as the gold, and the shuffled-boundary twin as the
info-free control. **Highest-leverage first build = Rank 1 (event-horizon coref term)** — smallest surgery, clearest
single-source literature backing (4 independently-replicated behavioral effects + 1 physiological marker), touches
a function that is ALREADY the sole live default pick (no wiring-debt argument needed), and is checkable on gold
that's already on disk. Recommend running the "cheap decisive test" (Prediction B, temporal-reasoner correlation)
as a same-day, zero-build sanity check first, since a positive read there independently corroborates that our own
representations carry the DuBrow effect before committing to the coref build.

## Citations (verified count)

**11 primary sources independently verified live** by the 3 lit-scan sub-agents (PubMed/PMC/ScienceDirect/Nature/
journal-PDF fetch, not from training memory) + 2 reused from `research_brain_event_segmentation_2026-08-05.md`
(already independently verified there, not re-fetched):
Ben-Yakov & Dudai 2011 (PMC6622928); Ben-Yakov & Henson 2018 (PMC6246887); Sols, DuBrow, Davachi & Fuentemilla 2017
(PMID 29129536); Radvansky & Copeland 2006 (DOI 10.3758/BF03193261); Radvansky 2012 (SAGE DOI
10.1177/0963721412451274); Radvansky & Zacks 2011 (WIREs DOI 10.1002/wcs.133); DuBrow & Davachi 2013 (PMID
23957281); Ezzyat & Davachi 2011 (DOI 10.1177/0956797610393742); Clewett, Gasser & Davachi 2020 (PMC7421896 /
Nature Comms); Pu, Kong, Ranganath & Melloni 2022 (PMC8810807, exact equation quote-verified from full text);
Sargent et al. 2013 (DOI 10.1016/j.cognition.2013.07.002); Speer, Zacks & Reynolds 2007 (DOI
10.1111/j.1467-9280.2007.01920.x, reused, previously verified); Franklin, Norman, Ranganath, Zacks & Gershman 2020
(DOI 10.1037/rev0000177, reused, previously verified + partially re-confirmed this pass — architecture confirmed,
exact reset-of-instance-state sentence not independently quote-verified, flagged above). 1 item flagged
UNVERIFIED-as-stated: Baldassano et al. 2017's fine-grained (phasic-vs-graded) sub-boundary temporal profile of the
hippocampal signal was not confirmable from the fetched abstract alone (the boundary-coupling and recall-prediction
findings ARE confirmed; only the millisecond-scale shape claim is short of primary-source confirmation) — not
propagated as fact above.

---
**TLDR (plain English):** We built a tool that can tell, the way a human reader does, when one "scene" in a story
ends and a new one begins. Right now nothing in the system actually reacts to that signal. We read what happens in
a real brain the instant it notices a scene change: it writes the just-finished scene into long-term memory right
at that moment (not gradually the whole time); it makes people and things from the old scene noticeably harder to
think about once the new scene starts, even more than ordinary forgetting would explain; and it makes it harder to
remember the correct ORDER of two things if they happened on opposite sides of the scene change, while order within
one scene stays easy. The cheapest, most valuable place to plug our tool in is the part of the system that decides
which earlier character a word like "she" refers to — right now it only asks "how many sentences back," never
"was there a scene change in between," even though the human evidence says that matters a lot. That's the
recommended next build. Two other real but bigger jobs (memory write-timing, and updating the running scene
summary) are also named and mapped, for later.

**QUESTIONS:** none.

**NEXT STEPS:** run the zero-build sanity check (does our own already-built order-reasoning tool show the same
across-scene-change memory dip humans show, correlating the existing segmenter against the existing temporal
reasoner's already-scored results) as a same-day check; if it corroborates, open a SOLVER problem framed around
`graded_coref_pick.py`'s ACT-R decay (not `bound_event_backbone`), citing this note + DuBrow & Davachi 2013 +
Radvansky 2012 as the brain-foundational mechanism, GUM/UD-EWT as the modern gold, and Prediction A's HARD-PASS/
HARD-FAIL bar above as the pre-registered bar.
