# Research: brain-foundation drill — event segmentation (angle 1 of 3)

Date: 2026-08-05. Dispatched by Director as a hardening-check on `hdlab/situation_reader.py`
`_read_events` / `experiments/_temporal_ordering.py extract_events` before further clause-coverage
extension. LIVE-VERIFIED lit-scan (3 parallel Sonnet sub-agents, WebSearch/WebFetch against
pubmed/arxiv/sciencedirect/wustl/ualberta primary-source PDFs). Calibration penalty per
[[feedback-lit-scan-calibration-penalty]] applied throughout.

## HEADLINE

The brain's event unit is a **situation-model discontinuity gated by (change in) prediction
error over ~5 tracked dimensions (time/space/causation/goal/protagonist)**, held in a
**persistently-updated, boundary-reinstated working-memory event model** (not independent
per-clause tuples), and segmented at **multiple nested cortical timescales** simultaneously.
Our extractor gets the **predicate-decomposition** part right (more predicates per clause is
formally correct — VERIFIED) but is missing the **three actual mechanism components**: (1) a
relevance/discontinuity GATE (currently every syntactically-valid content verb becomes an
event, unconditionally), (2) a PERSISTENT incrementally-updated event model (currently each
event is an independent role-bundle write into a flat bounded focus, not update-in-place +
reinstate-at-boundary), (3) MULTI-TIMESCALE hierarchy (currently flat, single clause-level
granularity only). Extending clause coverage (coordinated/participial/modal-subordinate,
landed same-day 2026-08-05 per `_temporal_ordering.py` docstring) is a **real, brain-consistent
step forward on axis (predicate decomposition)** but does **not address** axes (1)-(3), which
are the actual shape-gap. Confidence in this verdict: **P=0.45 (deflated)**.

## 1. Event Segmentation Theory — prediction error (VERIFIED, with a nuance flag)

- Zacks & Tversky 2001, *Psychological Bulletin* 127:3-23 — hierarchical event structure
  (taxonomy + partonomy), the conceptual precursor. VERIFIED (PubMed 11271755).
- Zacks, Speer, Swallow, Braver, Reynolds 2007, "Event Perception: A Mind/Brain Perspective,"
  *Psychological Bulletin* 133:273-293 — states the prediction-error mechanism explicitly:
  perceptual systems continuously predict "what happens next"; boundaries are perceived when
  transient prediction error spikes. VERIFIED (PubMed 17338600).
- Reynolds, Zacks & Braver 2007, *Cognitive Science* — computational (RNN) model. VERIFIED
  finding, IMPORTANT NUANCE: raw instantaneous prediction error did **not** track human
  boundary judgments well; it was **error relative to a running baseline** (a change-in-error
  signal, not error magnitude) that matched behavioral boundaries. This matters for our
  extractor: a naive "fire whenever the local model is surprised" rule is the WRONG
  operationalization; the correct one is relative/contrastive.
- Speer, Zacks & Reynolds 2007, *Psychological Science* 18:449-455 — direct fMRI: neural
  transients at boundaries correlate with situational-dimension change (e.g. goal shifts).
  VERIFIED (PubMed 17576286). FLAG: no study found that decodes a literal trial-by-trial
  "prediction error" quantity from fMRI and shows it spikes at boundaries — the fMRI evidence is
  boundary-locked transients + a separate computational model that reproduces boundary
  placement via prediction-error dynamics. These are complementary, not one single direct test.
  **UNVERIFIED as a literally-measured brain PE signal**; VERIFIED as the field's working
  mechanistic account.

## 2. Zwaan event-indexing model (VERIFIED)

Zwaan & Radvansky 1998, *Psychological Bulletin* 123:162-185 (full text pulled) — readers track
5 dimensions: TIME, SPACE, CAUSATION, INTENTIONALITY/GOAL, PROTAGONIST. Discontinuity along any
dimension triggers updating; effects are roughly additive across simultaneously-changing
dimensions. This is the **cue inventory** that feeds the prediction-error mechanism in (1) — not
a separate/competing account. VERIFIED.

## 3. Multi-timescale nested segmentation (VERIFIED, strong)

Baldassano, Chen, Zadbood, Pillow, Hasson, Norman 2017, *Neuron* 95(3):709-721 — data-driven HMM
on fMRI finds a **nested cortical hierarchy**: short events (seconds) in sensory cortex,
progressively longer events (up to minutes) in high-order regions (angular gyrus, posterior
medial cortex / precuneus) that represent abstract multimodal situation models; high-order
boundaries coupled to **hippocampal activity that predicted later free-recall reinstatement**.
VERIFIED (ScienceDirect DOI 10.1016/j.neuron.2017.06.041; also biorxiv preprint). This directly
confirms Zacks & Tversky's behavioral partonomy claim with a neural mechanism: segmentation is
NOT a single flat pass — it is simultaneous at multiple granularities, coarse events built from
fine ones.

### DMN persistent event model + hippocampal boundary encoding (VERIFIED, one correction)

- DMN (mPFC, posterior medial/precuneus, angular gyrus) shows transient activity increases at
  boundaries driven by situation-model change (Speer et al. 2007, above). VERIFIED.
- Ben-Yakov & Dudai 2011 (*J Neurosci*, PubMed 21677186) and Ben-Yakov & Henson 2018 ("The
  Hippocampal Film Editor," *J Neurosci* 38:10057) — hippocampal activity reliably spikes AT
  event boundaries, is sensitive+specific to those moments, reflects rapid post-boundary replay
  of the just-completed event, and predicts subsequent episodic memory strength. VERIFIED —
  boundaries are literally where episodic traces get "stamped."
- **CORRECTION to the prompt's framing:** "re-initialized at boundaries" (i.e. a hard reset to
  blank) is **NOT** what the literature says. The verified language is **reinstatement /
  reactivation** of prior event content at boundaries (including anticipatory reinstatement of
  familiar narrative structure), not erasure-and-restart. This is a materially different, less
  lossy mechanism than "reset" — closer to our Cowan-4 `ChunkedFocus` compress-and-carry-forward
  behavior than to a fresh re-init, actually. Flag this correction as load-bearing for design:
  do NOT build a "wipe the event model at every boundary" primitive; build a
  compress/carry-forward + hippocampal-style boundary-tagged consolidation instead (closer to
  what the substrate's bounded focus already approximates for MEMORY, but the EVENTS dimension
  currently has no analogous incremental-update-in-place behavior — see verdict below).

## 4. Granularity: predicate vs. state-change; clause vs. event (VERIFIED, mixed)

- Vendler 1957 / Dowty: aspectual classes (state/activity/accomplishment/achievement) are
  properties of the VP-level predicate; achievements/accomplishments decompose internally into
  a change-of-state (CAUSE/BECOME) structure. VERIFIED.
- Davidson/Parsons neo-Davidsonian event semantics: **one predicate = one event variable**, and
  **causatives explicitly decompose into two events** ("X caused Y to Z" = a causing-event +Ↄ a
  becoming-event); non-finite/participial adjuncts generally carry their **own** event variable
  distinct from the matrix clause. VERIFIED (Parsons PDF, Landman lecture notes). This is a
  clean formal-semantics endorsement of "more predicates per clause = more events," i.e. it
  **directly supports** the coordinated/participial/modal-subordinate extension our extractor
  just landed (2026-08-05) — that piece is brain(mind)-consistent, not a convenient proxy.
- Zacks & Speer 2009 ("Segmentation in Reading and Film Comprehension") coded event boundaries
  **relative to clauses** operationally — clause is the annotation grain in the human data, not
  a claim that clauses ARE the causal unit. A clause is registered as a boundary only when one
  of the 5 Zwaan dimensions actually shifts — **not every clause, and not every predicate**.
  VERIFIED mechanism: **goal/situational-relevance gating exists and is selective**; segmentation
  is explicitly modulated by task/goal relevance (participants segment more at spatial shifts
  when instructed to attend to space vs. characters) — this is the strongest, most actionable
  verified finding for our extractor: **statives and low-relevance predicates should NOT
  automatically become events; only predicates that mark a goal/causal/spatial/temporal/
  protagonist state-change should.** VERIFIED (eLife "Multiple event segmentation mechanisms in
  the human brain" review + Zacks Psych Bull 2007).
- UNVERIFIED (searched, not found): a study directly quantifying "how many event-segmentation
  units come out of one complex multi-clause sentence" — i.e. no primary source found that
  explicitly counts boundaries-per-sentence for coordinated/participial constructions. This is
  the one genuine gap in the lit-scan; the inference that finer-than-sentence granularity is
  standard practice is reasonable but not directly nailed down.

## Cross-thread synthesis

This drill sits adjacent to the existing brain-faithfulness audits on coref (Centering/Cb,
FAITHFUL) and Component-3 thematic-role labeling (frame-primary, WIRED 2026-08-05). Coref and
Component-3 both concluded "the brain does X via mechanism Y, and our organ approximates Y with
measured degradation" — this drill finds the SAME shape of gap for events: the brain's mechanism
(prediction-error-gated, persistently-updated, multi-timescale event MODEL) is qualitatively
different from what the extractor currently does (unconditional flat per-predicate extraction
into independent role bundles), even though the predicate-decomposition sub-piece (Davidsonian
multi-event-per-clause) that was extended today IS the correct target on ITS axis.

This also connects to the [[project_build_the_6yo_grounded_foundation]] pivot: goal-relevant
state-change gating (item 4) is exactly the kind of grounded-goal signal that pivot argues text
alone can't supply — an event extractor that gates on "did this predicate change a
goal/causal/spatial/protagonist state" needs a representation of what the tracked goals/states
ARE, which is squarely the grounded-foundation gap, not a POS-tagger extension.

## Substrate-product implications

1. **Do not treat "extend clause coverage" as closing the event-extraction gap.** It closes the
   predicate-decomposition sub-problem (verified brain/mind-consistent) but leaves the three
   real gaps open: relevance gating, persistent model update, multi-timescale hierarchy.
2. **Cheapest next win: add a relevance/discontinuity gate.** Concretely: an emitted event
   should carry a `is_boundary: bool` computed from whether AGENT/PATIENT/goal-relevant-state
   differs from the previous event's state along >=1 of the Zwaan 5 dimensions (character
   changed, causal link present, tense/time shifted, spatial marker present) — this is cheap
   (reuses coref's entity-continuity signal + the existing causal/temporal readers already in
   `situation_reader.py`) and directly implements the single most load-bearing verified finding
   (item 4: selective, not blanket, extraction).
3. **Medium-cost: persistent event MODEL instead of independent bundles.** Rather than each
   event being an isolated `{PRED, AGENT, PATIENT, TENSE}` bundle pushed into `ChunkedFocus`,
   maintain one updating state-of-affairs record (who/what/where/goal) that gets UPDATED
   in-place on non-boundary predicates and only gets a fresh slot at a genuine boundary — closer
   to the verified "reinstatement not reset" mechanism, and closer to what `ChunkedFocus`
   already does for compress/carry-forward at the MEMORY dimension (this would extend that same
   discipline to the EVENTS dimension, which currently lacks it).
4. **Higher-cost, defer: multi-timescale hierarchy** (fine events nested in coarse
   scenes/episodes) — real per Baldassano et al., but this is a bigger structural addition and
   should wait until (2) and (3) exist to update.

## Cheap decisive test

Build the `is_boundary` gate (implication #2) as a POST-HOC classifier over already-emitted
events (no new extraction mechanism) and measure: does gating out non-boundary predicates
change the F1 against McGuffey/LitBank gold role annotations in the direction predicted (higher
precision on "event" identification if gold events correlate with situational discontinuity,
even if recall drops)? This is a same-day, CPU-only smoke — reuses existing gold files.

## Falsifiable predictions

- **HARD-PASS:** gating emitted events by an Zwaan-5-dimension discontinuity signal
  (entity-change OR causal-link-present OR tense-shift OR new-spatial-marker) raises
  precision-against-gold-event-boundaries by >=10 points relative to the current
  "every content verb is an event" baseline, with recall loss <=15 points.
- **HARD-FAIL:** gating produces <3 points precision change either direction, OR recall
  collapses by >30 points (indicating the gate is not tracking situational relevance at all,
  just filtering predicates near-randomly) — in that case the Zwaan-dimension signals as
  currently available (coref clusters, causal links, tense) are too noisy/sparse in this
  passage set to serve as a boundary proxy, and the gate needs richer situational features
  before it's worth wiring.

## Direct verdict

"One predicate per sentence via POS tagger, extend to more clauses" is **NOT** a brain-faithful
operationalization of event segmentation — and the extension actually already landed
(2026-08-05, same-day docstring in `_temporal_ordering.py`) is honestly better characterized as
"one-event-per-syntactically-valid-predicate, now covering more predicate types per clause,"
which is a genuine formal-semantics-consistent step (Davidsonian multi-event-per-clause,
VERIFIED) but is not the brain's unit. The brain's unit is a **prediction-error-gated,
persistently-updated, multi-timescale situation-model discontinuity** — segmentation is
SELECTIVE (not every predicate becomes a boundary; statives/low-relevance predicates do not,
per the strongest verified finding in this drill) and the result is an INCREMENTALLY-MAINTAINED
model (reinstated, not reset, at boundaries) rather than a stream of independent tuples.
Extending clause coverage is a real step toward the right shape on ONE axis
(predicate-decomposition) but is a patch, not the fix, on the other two axes (relevance gating,
persistent-model update) that are the actual gap. Recommend: ship the relevance gate (implication
#2) next — cheapest, most directly verified, and it's the item this drill is most confident
about.

**Confidence: P=0.45 (deflated per calibration discipline; novel-synthesis cap 0.50 applied —
this is a design-verdict synthesis across 3 independent verified lit threads, not a single
directly-tested claim).** The individual VERIFIED citations above carry high confidence
(primary-source-checked); the deflation applies to the SYNTHESIS step (mapping the verified
mechanism onto "this is exactly what our extractor is missing" is my interpretive read, not
itself literature-verified).

## Citations (verified count)

11 primary/secondary sources independently verified live this pass (PubMed/ScienceDirect/
university PDF/preprint fetch, not from training-memory):
Zacks & Tversky 2001 (PubMed 11271755); Zacks et al. 2007 Mind/Brain Perspective (PubMed
17338600); Reynolds, Zacks & Braver 2007 (PubMed 21635310); Speer, Zacks & Reynolds 2007
(PubMed 17576286); Zwaan & Radvansky 1998 (full PDF, ualberta); Baldassano et al. 2017 Neuron
(ScienceDirect DOI 10.1016/j.neuron.2017.06.041); Ben-Yakov & Dudai 2011 (PubMed 21677186);
Ben-Yakov & Henson 2018 J Neurosci 38:10057; Vendler 1957 (PDF, uchicago); Parsons *Events in
the Semantics of English* (PDF, colorado); Zacks & Speer 2009 (PMC8710938). 2 sources flagged
UNVERIFIED (literal decoded fMRI prediction-error signal at boundaries; direct
multi-event-per-complex-sentence segmentation count study) — both explicitly caveated above,
not propagated as fact.
