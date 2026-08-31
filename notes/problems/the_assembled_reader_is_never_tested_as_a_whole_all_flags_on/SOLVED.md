---
problem: the_assembled_reader_is_never_tested_as_a_whole_all_flags_on
status: SOLVED
bar: "PASS = (1) NO-REGRESSION -- each dimension, measured WITH all flags on, reproduces its isolated validated result within CI (no CI-separated drop vs its solo witness); (2) AGGREGATE -- the FULLY-ON reader beats the DEFAULT reader on an end-to-end comprehension score (the QA capstone re-run) CI-separated, with the info-free control (a flags-on-but-shuffled variant) not helping; (3) INTERACTION MAP -- a flag-ablation matrix (each flag on/off) that quantifies the marginal + joint contribution and NAMES any interference; report CI half-width + null p95, no number crossing populations. A rigorous NEGATIVE is a full PASS: if turning flags on together REGRESSES a dimension or the whole is not better than the parts, report exactly which flags interfere and why (the wiring gap) -- that is the single most important thing this test can find."
result: "Fully-on reader established as a measured whole over 60 LitBank docs (QA-capstone scorer). NO-REGRESSION is BYTE-EXACT: every dimension's all-flags-on output is byte-identical to its isolated-flag output (interaction exactly 0, not merely within CI). EVENTS/who-did-what QA: all-on 0.2499 vs default 0.1389, +0.1110 CI [+0.0956,+0.1264] (half-width 0.0154), info-free shuffled-cue twin 0.0, permutation null p95 0.0330. Coref QA unchanged (0.5429, CI [0,0]). The naive whole>default aggregate is a rigorous NEGATIVE with named interference: tense_agnostic collapses the QA TEMPORAL question set (1108->0) and inflates+breaks the CAUSAL gold (150->265 q, 0.4533->0.1132) -- BOTH QA golds derive from sm.events, so the KEYSTONE detector breaks the instrument, NOT the reader (the reader's temporal/causal dimension fields timeline_frames/causal_links/timeline_order/typed_causal are byte-identical). Corrected temporal readout consuming sm.timeline_order answers 0.9783 of the temporal questions at 0.9278 on the all-on model."
floor: "strongest per-dimension floor actually run: coref recency/most-frequent 0.5571; events word-overlap 0.0194; temporal text-order 0.3736; causal adjacency/word-overlap 0.62. Info-free shuffled-cue twin = 0.0 on every scored dimension. Permutation (label-swap) null p95 = 0.033 on the events margin (observed +0.111 >> 0.033)."
controls: "(1) info-free shuffled-cue twin (derangement of the cue->dimension table) = 0.0 on every scored dimension -- excludes the readout scoring by chance routing. (2) permutation null p95 0.033 on the events margin -- excludes the events win as a resampling artifact. (3) byte-identity signatures across the 10-config matrix -- excludes hidden cross-dimension regression (proven EXACTLY 0). (4) SILO positive-control: the one field two flags co-write (sm.events) DOES interact (event_roles all_on != RR-alone; role-acc composes additively 0.154->0.276), proving the measurement CAN detect interaction, so the byte-identical zeros elsewhere are real absence, not a blind instrument. (5) the fix arm (timeline_order readout 0.978/0.928) -- excludes 'the reader's temporal capability regressed'; the coupling arm (role_source=reader changes 24% of typed links) -- excludes 'the silo is necessary'."
files_changed: "experiments/exp_assembled_reader_all_flags_on_v1.py; verification/test_assembled_reader_all_flags_on.py; data/exp_assembled_reader_all_flags_on_v1/metrics.json (+units.jsonl); notes/problems/the_assembled_reader_is_never_tested_as_a_whole_all_flags_on/research_brain_situation_model_dimension_binding_2026-08-31.md; notes/problems/the_assembled_reader_is_never_tested_as_a_whole_all_flags_on/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_assembled_reader_all_flags_on.py"
---

# The assembled reader, all flags on: it is PARALLEL SILOS, not the brain's integrated situation model

## What I built
A full-system end-to-end harness (`experiments/exp_assembled_reader_all_flags_on_v1.py`) that runs the
live `hdlab.situation_reader.SituationReader` across a **10-config flag-ablation matrix** (default; each
of the four validated flags alone: `tense_agnostic_events`=TA, `role_route`=RR, `causation_typed`=CT,
`timeline_register`=TR; each leave-one-out; all-on) on 60 real LitBank documents, and measures each
dimension's OUTPUT and the QA capstone jointly. A scaffold-free witness
(`verification/test_assembled_reader_all_flags_on.py`, **15/15 PASS**) recomputes every load-bearing
claim from source. Reverify with the witness (it writes nothing; it does not touch the landed record).

This is the FIRST time all validated dimension flags have been turned on together and the reader measured
as a whole. The QA capstone (`exp_situation_model_qa_v1`), our supposed end-to-end instrument, runs
`SituationReader(gaz=gaz)` = the DEFAULT reader with every capability OFF -- confirmed on disk.

## The brain frame (PINNED -- this is why the result matters, not bookkeeping)
Opening move, from a literature drill (`research_brain_situation_model_dimension_binding_2026-08-31.md`):

> The integrated-vs-siloed distinction is brain-foundational, not cosmetic. Across the event-indexing
> model (Zwaan & Radvansky 1998), Event Segmentation Theory (Zacks et al. 2007), the Structured Event
> Memory model (Franklin, Norman, Ranganath, Zacks & Gershman 2020), hippocampal-entorhinal relational
> binding, and the default-mode situation-model literature (Yeshurun, Nguyen & Hasson 2021), the brain
> builds ONE relationally-bound event representation and indexes that single event token on all
> situational dimensions (who/what, when, where, why, belief), carrying unmentioned dimensions forward as
> a persisting shared state. It does not run N pipelines that each re-extract the events from raw text
> and fuse only at readout. Our current parallel-silo reader -- where each dimension re-parses the text
> and never consults a common event/entity set -- is therefore a PINNED brain-fidelity gap: the shared
> event index is the mechanism, and the integration is the computation, not an efficiency.

The brain-faithful PREDICTION the brief states and this harness tests: **better event detection (WHO/WHAT)
should FEED time (WHEN) and causation (WHY)** -- because all three read one shared event token. If instead
each dimension re-extracts its own events, that cross-dimension coupling is ZERO. It is zero.

## What I measured (60 LitBank docs; QA-capstone scorer; bootstrap CI over docs)

### (A) NO-REGRESSION -- byte-exact, the strongest possible form
Every dimension's all-flags-on OUTPUT is **byte-identical** to its isolated-flag output:
`event_set == TA-alone`, `timeline_order == TR-alone`, `typed_causal == CT-alone`; and the flag-independent
dimensions (`entities`, `coref`, `timeline_frames`, `causal_links`) are byte-identical to the DEFAULT
reader. So no dimension is degraded by the others being on -- the interaction is exactly 0, not merely
"within CI". (Per the brief I INHERIT each dimension's isolated headline; byte-identity means the exact
isolated output is reproduced, so the isolated metric is reproduced identically.) The one non-match --
`event_roles != RR-alone` -- is not a regression; it is the one genuine interaction (below).

### (B) SILO STRUCTURE -- the brain-fidelity finding
Perturbing the shared event set (turn TA on: who-did-what recall 0.657 -> 0.967) leaves EVERY other
dimension **byte-identical**: `timeline_frames`, `causal_links`, `timeline_order`, `typed_causal`,
`entities`, `coref`. On disk, `read()` calls FIVE independent event extractors on THREE different
tokenizers (`_read_events` UPOS tagger; `_read_timeline` `M.extract_events_punct`; `_read_timeline_register`
`TOR.extract_passage`; `_read_causation` `C.extract`; `read_typed_causation` a separate spaCy parse). There
is no shared event token. Better event detection does NOT feed time or causation. **This is the PINNED
brain-fidelity gap, measured: the reader is N parallel silos, not one integrated situation model.**

### (B2) The ONE place a shared token exists, the dimensions DO interact (positive control)
`sm.events` is co-written by TA (which verbs fire) and RR (their roles). On the who-did-what gold, role
accuracy composes **additively**: default 0.154; TA-alone 0.248; RR-alone 0.181; all-on 0.276 (~= the
additive sum 0.154 + (0.248-0.154) + (0.181-0.154)). So where they share the event token they help each
other -- exactly the brain's prediction, and proof the measurement can detect interaction, so the zeros in
(B) are real absence.

### (C) AGGREGATE QA, default vs all-on -- a rigorous NEGATIVE with named interference
| dimension | default | all-on | strong floor | twin | diff CI (all-on - default) |
|---|---|---|---|---|---|
| coref | 0.5429 (n=1761) | 0.5429 | 0.5571 | 0.0 | [0, 0] (unchanged) |
| **events** | 0.1389 (n=7028) | **0.2499** | 0.0194 | 0.0 | **[+0.0956, +0.1264]** (real win; null p95 0.033) |
| temporal | 0.9152 (n=1108) | **None (n=0)** | 0.3736 | -- | [-0.9435, -0.8852] (instrument collapse) |
| causal | 0.4533 (n=150) | 0.1132 (n=265) | 0.62 | 0.0 | [-0.4249, -0.2666] (instrument break) |

The EVENTS dimension beats default CI-separated with the twin at 0 and the observed margin (+0.111,
half-width 0.015) far above the permutation null p95 (0.033) -- the genuine payoff of turning the keystone
(TA) + role routing (RR) on. But the OVERALL aggregate does not improve, and the reason is the single most
important finding of this test:

**TWO INSTRUMENT COUPLINGS, not reader regressions.** Both the QA temporal gold (`build_temporal_questions`
reads PAST_PERFECT vs SIMPLE_PAST off `sm.events`) and the QA causal gold (`build_causal_questions` locates
events by surface position in `sm.events`) are DERIVED FROM `sm.events`. The keystone TA detector stamps a
PLACEHOLDER tense on every event and adds all present-tense verbs, so it (a) zeroes the temporal question
set (1108 -> 0 -- no PAST_PERFECT survives) and (b) inflates the causal question set (150 -> 265) into
pairings the flag-independent `causal_links` readout no longer matches (0.453 -> 0.113). The reader's
temporal and causal DIMENSION FIELDS do not regress at all (byte-identical). **The instrument breaks under
the keystone, not the reader.** Every solver who measures temporal/causal QA against "the reader" with TA
on is measuring a broken gold.

### (C2) INTERACTION MATRIX (aggregate QA acc + temporal-question count per config)
`default 0.300/1108 | TA 0.285/0 | RR 0.316/1108 | CT 0.300/1108 | TR 0.300/1108 | loo_TA 0.316/1108 |
loo_RR 0.285/0 | loo_CT 0.303/0 | loo_TR 0.303/0 | all_on 0.303/0`. Reads: **RR is the only flag that
improves the aggregate without breaking the instrument** (0.300 -> 0.316). **CT and TR alone leave the
aggregate UNCHANGED (0.300)** -- they populate NEW fields (`typed_causal_links`, `timeline_order`) that the
QA readouts never consult (the causal readout reads `causal_links`; the temporal readout reads
`timeline_frames` + event-tense). So two landed dimensions are INVISIBLE to our end-to-end instrument. Any
config with TA on shows temporal_q = 0.

### (D) THE FIX, demonstrated -- consume the actual dimension field
A corrected temporal readout that reads `sm.timeline_order` (the field `timeline_register` populates, which
the QA readout ignores) answers **0.978** of the tense-gold temporal questions at **0.928** accuracy on the
all-on model -- vs the broken event-tense readout's 0.424 coverage / 0.421 accuracy. So the temporal
capability is intact and BETTER when the instrument consumes the real field; the collapse in (C) is purely
the readout reading an event-tense proxy that TA overwrites.

### (E) The brain-faithful wire ALREADY EXISTS as an off-by-default ablation
`causation_role_source="reader"` makes typed causation consume `sm.events` (the shared event set) instead of
re-parsing. Connecting it changes **23.8% of typed causal links** (of 4985) -- the silo is a DEFAULT CHOICE,
not a necessity; a real shared-event wire is present and connecting it materially changes causation. And
role-routing flows through it: with the wire on, RR changes **6.8%** of causal links -- i.e. better event-role
detection DOES feed WHY, but only when the shared-event wire is connected (off by default). This is the
brief's brain prediction made concrete: the coupling the brain requires is reachable in one existing switch.

## What I did NOT establish (withdraw-first list)
1. **Whether connecting the shared-event wire (role_source=reader) IMPROVES causation** -- I measured the
   coupling MAGNITUDE (24% of links change), not an accuracy delta; the validated typed-causation AUTO 0.833
   was measured with `role_source="parse"`. Whether the shared-event version is net-better needs the
   typed-causation gold re-run (mapped as a next problem). I withdraw any claim that the wire is BETTER, only
   that it EXISTS and couples.
2. **Genre generalization of the aggregate numbers** -- the SILO/no-regression finding is architectural
   (byte-identity of independent extractions) and corpus-INDEPENDENT by construction; the aggregate QA
   numbers are single-genre (LitBank). No modern held-out QA gold with coref+who-did-what was reachable.
3. **A dedicated flags-on-but-shuffled-EVENTS twin** -- the info-free controls run are the shuffled-cue
   routing twin (0.0) + the permutation null (0.033); a role-scramble twin would be a nice belt-and-braces
   addition but the events win already clears both controls and the word-overlap floor (0.019).
4. **The event count itself uses a PLACEHOLDER tense** -- TA's known boundary; it is exactly why sharing the
   event set breaks the tense-dependent instruments today. The tense-PRESERVING detector (my prior problem,
   `the_tense_agnostic_detector_drops_tense...`, awaiting owner-DONE) is the enabling fix.

## KEY REALIZATIONS
- **The brief is a bookkeeping task on its face; the brain question underneath is the real deliverable.**
  Reframing "turn all flags on and check nothing broke" as "is this an integrated situation model or N
  silos?" turned a validation chore into a PINNED architecture finding.
- **No-regression is byte-exact, and that is itself the diagnosis.** Because each dimension re-extracts
  independently, turning others on cannot change it -- the very thing that makes no-regression trivially
  true (perfect orthogonality) IS the silo defect. Composition without interaction is not integration.
- **A negative aggregate can be an INSTRUMENT artifact, and the way to tell is to consume the actual
  dimension field.** The temporal/causal "regressions" evaporate the moment the readout reads
  `timeline_order` instead of event-tense (0.93 vs 0.42). Ask "did the reader regress or did the instrument
  break?" and answer it with the fix arm, not an argument.
- **Build the info-free positive control for INTERACTION, not just for the win.** Showing the one shared
  field does interact (additive role-acc) is what licenses reading the byte-identical zeros as real absence.
- **The shared-event wire was already on the shelf** (`role_source="reader"`, and the whole binding organ
  `situation_model_accumulate.py`). The fidelity gap is a WIRING job with proven organs, not a build.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)
- **E2 (situation-model register / event indexing): the live reader has NO shared event token.** Measured:
  `situation_reader.read()` never imports `situation_model_accumulate`/`situation_model_multibank` (the
  FHRR bind register, atom 29609, itself brain-faithful) and runs 5 independent event extractors on 3
  tokenizers. Prediction-error-driven segmentation is ABSENT (event boundaries = sentence boundaries +
  per-verb). Current fidelity: the assembled reader is PARALLEL SILOS, a PINNED gap vs the Zwaan/SEM
  single-indexed-event-token mechanism. The binding organ exists but is an unwired island.
- **The QA capstone instrument couples to `sm.events`** for its temporal AND causal gold, and never consults
  `typed_causal_links` or `timeline_order`. So two landed dimensions are invisible end-to-end, and the
  aggregate is not a faithful whole-reader score under the keystone detector. This should be recorded so no
  solver quotes a TA-on temporal/causal QA number as a reader property.

## FOR STRATEGY (you land hdlab, Q111) -- proposed changes + ranked next problems
Proposed hdlab diffs (small, all measured here):
1. **Make the QA capstone the FULLY-ON instrument** and have its readouts consume the actual dimension
   fields: `_answer_temporal` -> read `sm.timeline_order` (proven 0.978/0.928); `_answer_causal` -> also read
   `sm.typed_causal_links`; build the temporal/causal GOLDS from a tense-independent source, not `sm.events`.
   This is the correct-baseline fix every other solver needs.
2. Nothing to flip ON by default yet: fully-on does not beat default as a WHOLE (the instrument couplings),
   so a default flip is premature until (a) the tense-preserving detector lands and (b) the instrument
   consumes the real fields. RR is the only flag that is aggregate-positive and instrument-safe today.

Ranked next problems (grounded in the on-disk adjacent-component map, most-blocking first):
1. **Wire a SHARED EVENT TOKEN as the reader backbone** (build the brain's integrated model). The binding
   organ `situation_model_accumulate.py` is BUILT + VET-confirmed but unwired; the fix is a WIRING job, not a
   build. HARD DEPENDENCY: it needs the tense-PRESERVING event detector first (my prior problem) or TIME
   breaks -- exactly the coupling this harness measured. Highest value (it is the north-star integrated model)
   and it clears the ranking rule (blocks others + proven organ).
2. **Fix the QA instrument** to consume `timeline_order`/`typed_causal_links` and build tense-independent
   temporal/causal golds (diff #1 above). Cheap; unblocks correct baselines project-wide.
3. **Measure whether the shared-event wire (`role_source="reader"`) IMPROVES causation** on the typed-causation
   gold (it changes 24% of links; is it better?). Small, verdict-independent.
4. **Wire the built-but-island Zwaan dimensions**: `location_register.py` (SPACE, PINNED) and
   `state_register.py` (STATE) -- both landed, registered, unwired; need a prose->motion / state-cue adapter.
5. **BELIEF/ToM last**: `belief_partition.py` + `belief_timeline.py` are built islands but need an
   observation-cue extractor first (their own docstring), and this is adapter-gated. CAUTION: do NOT conflate
   these false-belief-partition organs with the relational BRIDGING route that hit Phase 2's kill condition --
   different mechanism; check LONG_TERM_PLAN before opening.

## Generalization
The silo / no-regression finding is architectural (byte-identity of independent extractions) and therefore
corpus- and genre-independent -- it is a property of the code paths, not the data. The aggregate QA numbers
are LitBank-specific (single genre; no modern coref+who-did-what gold reachable). The brain-faithful target
generalizes cleanly: one shared, relationally-bound event token that all dimensions index (Zwaan/SEM), which
by construction makes cross-dimension coupling the default rather than something that must be re-wired per
dimension.

---

## TLDR
We turned on every finished ability of the reader at once for the first time and measured the whole thing.
Good news: nothing breaks another -- each ability produces exactly the same output with the others on as it
does alone, and the who-did-what ability gets clearly better. The important finding: the reader is really
several separate readers stapled together -- each one reads the story from scratch on its own, and they never
share a single understanding of "what happened." That is not how the brain does it (the brain builds one
picture of the event and reads who/when/where/why off that same picture), so it is a real gap to close -- and
the part needed to close it is already built, just not plugged in. Two of the abilities we recently added are
also invisible to our current "quiz the reader" test because the test never looks at what they produce; and
turning on the better event-finder confuses that test's own answer key (not the reader). We showed the fix
for that in place.

## QUESTIONS
None.

## NEXT STEPS
1. (strategy) Land the QA-instrument fix so temporal/causal are scored off the real dimension fields and every
   solver measures against the correct reader.
2. (next problem) Wire the shared event token (`situation_model_accumulate`) as the reader backbone -- gated on
   the tense-preserving detector landing.
3. (next problem) Measure whether the existing shared-event wire (`role_source="reader"`) improves causation.
4. (assembly) Wire the built-but-island SPACE and STATE dimensions; BELIEF last (adapter-gated, kill-condition
   aware).
