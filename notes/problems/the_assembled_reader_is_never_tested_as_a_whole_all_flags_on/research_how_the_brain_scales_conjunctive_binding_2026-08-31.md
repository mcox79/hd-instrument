# How the brain scales conjunctive/relational binding (research drill, 2026-08-31)

SOLVER drill for `the_assembled_reader_is_never_tested_as_a_whole_all_flags_on`.
Question: my bound-event-token demo used only 2 events. A passage has hundreds. A single passage-level
FHRR/VSA bundle superposes many bindings and its SNR degrades ~1/sqrt(M) with the number M of bundled
items (Plate 2003; Frady, Kleyko & Sommer 2018; Clarysse/Schlegel/Kleyko capacity analysis, arXiv
2301.10352). So: how does the BRAIN hold many bindings without crosstalk, and what is the faithful
scalable architecture? Lead with biology.

## 1. THE CAPACITY LIMIT OF BINDING
- **Cowan (2001) ~4 chunks** in the focus of attention when chunking is prevented; **Miller 7+/-2**
  when chunking (long-term grouping) is allowed -- both correct, different quantities (Mathy/Feldman;
  Journal of Cognition 2024 review). The brain's *active* simultaneous-binding limit is small (~4).
- **Luck & Vogel (1997)**: slot model, ~4 bound objects; capacity limited by number of OBJECTS
  (conjunctions), not raw features. **Binding is the capacity-limiting, attentionally-demanding step**
  -- newer work (JOV 2021; Journal of Cognition "WM capacity limits memory for bindings") shows the
  *conjunction*, not feature storage, is what saturates. This is the direct brain analog of VSA
  bundling crosstalk: a handful of active bindings, then interference.
- Verdict for us: the brain's answer is NOT "raise the bundle capacity" -- it is "keep the number of
  simultaneously-active bindings at ~4."

## 2. THETA-GAMMA PHASE MULTIPLEXING (the anti-crosstalk code for the ACTIVE register)
- **Lisman & Idiart (1995), Science 267:1512** "Storage of 7+/-2 short-term memories in oscillatory
  subcycles": ~7 gamma sub-cycles nest in one theta cycle; each item fires in its OWN gamma sub-cycle.
  Items are **phase-separated (time-slotted), NOT superposed** -- refreshed each theta cycle. Lisman &
  Jensen (2013) theta-gamma neural code.
- Mapping to VSA: phase-coding == **separable slots, not one bundle**. This is exactly a multibank /
  slotted register. The brain's fix for "many bindings without interference" is orthogonal SLOTS in
  time, i.e. it AVOIDS superposition for the active set. A single superposed passage register is the
  thing the brain's oscillatory code is built specifically NOT to do.

## 3. PATTERN SEPARATION (the anti-crosstalk code for the EPISODIC store -- a DIFFERENT tier)
- DG granule-cell sparse coding orthogonalizes overlapping EC inputs; sparse DG->CA3 decorrelates and
  **raises the STORAGE capacity of the episodic autoassociator** (Treves & Rolls 1994; Yassa & Stark
  2011; O'Reilly & McClelland). Winner-take-all + feedback inhibition => sparse non-overlapping codes.
- CRITICAL distinction for us: pattern separation raises the capacity of the **long-term episodic
  store written one event at a time**, NOT the number of bindings simultaneously ACTIVE in WM. It is
  the right mechanism for the *offloaded* tier, the wrong mechanism for the *active* register.
- This reframes the project's DG HARD_FAILs (`exp_dg_pattern_separation_mcscript_purity_v1`,
  `..._selfplay_dg_..._xfit_v1`): DG was tested on active-read / coreference crosstalk -- a job the
  brain gives to phase-slots and to segmentation, NOT to DG. DG's faithful job is decorrelating the
  CONSOLIDATED episodic store so retrieved past events don't collide. Tested on the right tier it may
  not fail the same way; it was tested on the wrong tier.

## 4. SEGMENTATION AS CHUNKING (the real answer -- the brain does NOT hold one giant scene)
- **Event Segmentation Theory** (Zacks et al. 2007; Kurby & Zacks 2008): the brain maintains ONE
  active "working event model," predicts forward from it, and when **prediction error spikes** it
  UPDATES -- an event boundary -- flushing the finished event to episodic (hippocampal) memory and
  resetting the active model. The active bound register stays SMALL (current event, in a hierarchy).
- **SEM** (Franklin, Norman, Ranganath, Zacks & Gershman 2020, Psych Review): latent-cause /
  probabilistic segmentation -- infers boundaries, learns schemata, reconstructs past events by
  RETRIEVING stored segments. Boundary = discontinuity between the event model's prediction and
  observation. **Bayesian surprise predicts human segmentation in story listening** (Kumar et al.
  2023, Cognitive Science) -- directly the narrative case.
- Verdict: a passage-level single bound register is NOT brain-faithful. The brain chunks the stream
  into events at prediction-error boundaries; each segment is a small bound model; older segments live
  in episodic memory and are RETRIEVED on demand (coreference, bridging, anaphora).

## 5. THE VERDICT -- brain-faithful SCALABLE shared-event-token architecture
Not (a). The answer is **(b) + (c) + (d) at DIFFERENT tiers**:

1. **ACTIVE register = ONE current event token** (its role-filler bindings), capacity ~4, held in a
   **slotted / multibank register (theta-gamma phase-separation analog), NOT one superposed bundle.**
   FHRR binding stays the algebra; the store organization is slots, not a passage-wide bundle.
2. **BOUNDARY controller = prediction-error / Bayesian-surprise detector** (EST/SEM). On a spike:
   FLUSH the completed event token to the episodic store, RESET the active model.
3. **EPISODIC store = pattern-separated sparse codes** (DG->CA3 analog): each flushed event gets a
   decorrelated, retrievable code. High capacity BECAUSE only ~1 event is bundled-active at a time and
   the hundreds of past ones are orthogonalized and indexed, not superposed.
4. **RETRIEVAL** pulls a prior event token back into the active register for cross-event inference.

**Is a single passage-level bound representation IMPOSSIBLE, or merely degraded?** Merely degraded, and
demonstrably NOT what the brain does. VSA *can* bundle hundreds, but retrieval SNR falls ~1/sqrt(M) so
a passage register is quantitatively lossy AND biologically wrong. The neuroscience says: **must
chunk.** The scalable faithful design is small active token + surprise-triggered segmentation +
pattern-separated episodic consolidation + retrieval -- scalable to hundreds of events because at most
~1 event's bindings are ever superposed at once.

### Mapping to BUILT organs
- **FHRR bundle register** -> the ACTIVE event token, kept SMALL (one event), never passage-level.
- **multibank register** -> the slot/phase-multiplexing structure holding the few active bindings
  without crosstalk (theta-gamma faithful). This, not a single bundle, is the assembled-reader's WM.
- **DG pattern separation** -> the EPISODIC store tier (offloaded events), NOT the active read. Its
  prior HARD_FAILs were on the wrong tier.
- **predictive-coding / surprise organ** -> the BOUNDARY controller (flush + reset).

### Testable consequence for the assembled-reader-all-flags-on cell
An "all flags on" reader that keeps ONE passage-level bundle should DEGRADE as events accumulate
(crosstalk ~1/sqrt(M)); a segmented reader (surprise-boundary flush to a pattern-separated episodic
store + retrieval) should hold accuracy flat with passage length. The discriminating experiment is
accuracy-vs-number-of-events for single-bundle vs segmented+episodic, on same-type event coreference /
bridging (from the companion note `research_what_integration_buys_and_how_to_test_it`). Predicted:
single-bundle collapses with event count; segmented stays flat. That is the can-fail test of "must
chunk."

### Key citations
Cowan 2001 (magical number 4); Miller 1956 (7+/-2); Luck & Vogel 1997 (VWM slots / binding capacity),
JOV 2021 & J.Cognition (binding is the limiting step); Lisman & Idiart 1995 Science (theta-gamma
subcycles), Lisman & Jensen 2013 (theta-gamma code); Treves & Rolls 1994, Yassa & Stark 2011,
O'Reilly & McClelland (DG pattern separation / episodic capacity); Zacks et al. 2007 & Kurby & Zacks
2008 (Event Segmentation Theory); Franklin, Norman, Ranganath, Zacks & Gershman 2020 Psych Review
(SEM); Kumar et al. 2023 Cognitive Science (Bayesian surprise -> segmentation in stories); Plate 2003 /
Frady, Kleyko & Sommer 2018 / Kleyko et al. 2022 (VSA bundling capacity, SNR ~1/sqrt(M)).
