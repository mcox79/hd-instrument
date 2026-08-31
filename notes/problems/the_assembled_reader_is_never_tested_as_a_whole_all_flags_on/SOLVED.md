---
problem: the_assembled_reader_is_never_tested_as_a_whole_all_flags_on
status: SOLVED
bar: "PASS = (1) NO-REGRESSION -- each dimension, measured WITH all flags on, reproduces its isolated validated result within CI (no CI-separated drop vs its solo witness); (2) AGGREGATE -- the FULLY-ON reader beats the DEFAULT reader on an end-to-end comprehension score (the QA capstone re-run) CI-separated, with the info-free control (a flags-on-but-shuffled variant) not helping; (3) INTERACTION MAP -- a flag-ablation matrix (each flag on/off) that quantifies the marginal + joint contribution and NAMES any interference; report CI half-width + null p95, no number crossing populations. A rigorous NEGATIVE is a full PASS: if turning flags on together REGRESSES a dimension or the whole is not better than the parts, report exactly which flags interfere and why (the wiring gap) -- that is the single most important thing this test can find."
result: "Full-system harness over 100 LitBank docs (10-config flag matrix; QA-capstone scorer). (1) NO-REGRESSION is BYTE-EXACT: every dimension's all-flags-on output is byte-identical to its isolated-flag output (interaction exactly 0). (2) AGGREGATE -- MET POSITIVELY once the instrument reads each dimension's CORRECT field: fully-on-corrected 0.3993 vs default 0.3222, +0.0771 CI [+0.0664,+0.0891] (half-width 0.0114), CI-SEPARATED, info-free scrambled-agent twin 0.0976 (collapses); driven by events 0.158->0.2715 (CI [+0.0999,+0.1278]), coref/temporal/causal held (no CI-separated change). The NAIVE aggregate does NOT beat default only because the QA temporal+causal GOLDS are derived from sm.events, which the tense-agnostic keystone rewrites -- an INSTRUMENT coupling, not a reader regression (the reader's dimension fields are byte-identical). (3) INTERACTION MAP: full 10-config matrix; the one shared field (sm.events) composes ADDITIVELY (who-did-what role-acc default 0.158 + TA 0.085 + RR 0.023 = 0.267 ~= observed all-on 0.2715; interaction +0.005); events-margin permutation null p95 0.0245."
floor: "Strongest per-dimension floor actually run: coref recency/most-frequent 0.5613; events word-overlap 0.017; temporal text-order 0.3664; causal adjacency/overlap 0.6479. Corrected-aggregate info-free twin (scrambled event agents) = 0.0976 vs the 0.2715 real events accuracy. Naive-aggregate info-free shuffled-cue twin = 0.0 on every scored dimension. Events-margin permutation (label-swap) null p95 = 0.0245 (observed margin +0.10 >> 0.0245)."
controls: "(1) info-free scrambled-agent twin on the corrected aggregate = 0.0976 (events win collapses) -- excludes the win being anything but real role content. (2) shuffled-cue routing twin = 0.0 on every dimension -- excludes chance routing. (3) permutation null p95 0.0245 on the events margin -- excludes a resampling artifact. (4) byte-identity signatures across the 10-config matrix -- excludes hidden cross-dimension regression (proven EXACTLY 0). (5) SILO positive control: the one co-written field (sm.events) DOES interact (event_roles all_on != RR; role-acc additive) -- proves the measurement CAN detect interaction, so the byte-identical zeros elsewhere are real absence. (6) corrected-temporal fix arm (timeline_order readout) + causation-wire arm (parse vs reader 0.833==0.833 on the curated gold) -- exclude 'the reader regressed' and 'the silo is necessary' respectively. (7) instrument faithfulness cross-check: my default per-dim (coref 0.556/events 0.145/temporal 0.926/causal 0.442) reproduces the QA capstone's landed 100-doc numbers -- confirms faithful instrument reuse."
files_changed: "experiments/exp_assembled_reader_all_flags_on_v1.py; experiments/exp_assembled_reader_corrected_aggregate_v1.py; experiments/exp_assembled_reader_integration_diagnostics_v1.py; experiments/exp_integrated_shared_event_token_poc_v1.py; verification/test_assembled_reader_all_flags_on.py; data/exp_assembled_reader_all_flags_on_v1/metrics.json (+units.jsonl); data/exp_assembled_reader_corrected_aggregate_v1/metrics.json; data/exp_assembled_reader_integration_diagnostics_v1/metrics.json; data/exp_integrated_shared_event_token_poc_v1/metrics.json; notes/problems/the_assembled_reader_is_never_tested_as_a_whole_all_flags_on/research_brain_situation_model_dimension_binding_2026-08-31.md; notes/problems/the_assembled_reader_is_never_tested_as_a_whole_all_flags_on/research_what_integration_buys_and_how_to_test_it_2026-08-31.md; notes/problems/the_assembled_reader_is_never_tested_as_a_whole_all_flags_on/research_how_the_brain_scales_conjunctive_binding_2026-08-31.md; notes/problems/the_assembled_reader_is_never_tested_as_a_whole_all_flags_on/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_assembled_reader_all_flags_on.py"
---

# The assembled reader, all flags on: PARALLEL SILOS, not the brain's integrated situation model -- but wired right, the whole beats the parts

## What I built
A full-system end-to-end harness that runs the live `hdlab.situation_reader.SituationReader` across a
**10-config flag-ablation matrix** (default; each of the 5 validated flags alone: `tense_agnostic_events`=TA,
`role_route`=RR, `causation_typed`=CT, `timeline_register`=TR, `spacy_pred_gate`=PG; leave-one-out; all-on)
on **100 LitBank documents**, measuring every dimension's OUTPUT and the QA capstone jointly. Three cells:
- `exp_assembled_reader_all_flags_on_v1.py` -- the matrix: no-regression, silo structure, event interaction, QA
  aggregate, interaction matrix, twins, the corrected-temporal fix, the shared-event coupling wire, null p95.
- `exp_assembled_reader_corrected_aggregate_v1.py` -- the HONEST whole-vs-parts aggregate (instrument reads each
  dimension's correct field), the 5th flag, and does-the-shared-event-wire-help-causation.
- `exp_assembled_reader_integration_diagnostics_v1.py` -- cross-dimension event-token overlap + off-genre silo.
Scaffold-free witness `verification/test_assembled_reader_all_flags_on.py` recomputes every load-bearing claim
from source. Reverify with the witness (it writes nothing; it does not touch the landed record).

This is the FIRST time all validated dimension flags were turned on together and the reader measured as a whole.
The QA capstone (`exp_situation_model_qa_v1`), our supposed end-to-end instrument, runs `SituationReader(gaz=gaz)`
= the DEFAULT reader with every capability OFF -- confirmed on disk.

## The brain frame (PINNED -- why this matters, not bookkeeping)
From a literature drill (`research_brain_situation_model_dimension_binding_2026-08-31.md`):

> The integrated-vs-siloed distinction is brain-foundational, not cosmetic. Across the event-indexing model
> (Zwaan & Radvansky 1998), Event Segmentation Theory (Zacks et al. 2007), the Structured Event Memory model
> (Franklin, Norman, Ranganath, Zacks & Gershman 2020), hippocampal-entorhinal relational binding, and the
> default-mode situation-model literature (Yeshurun, Nguyen & Hasson 2021), the brain builds ONE relationally-
> bound event representation and indexes that single event token on all situational dimensions (who/what, when,
> where, why, belief), carrying unmentioned dimensions forward as a persisting shared state. It does not run N
> pipelines that each re-extract the events from raw text and fuse only at readout. Our current parallel-silo
> reader -- where each dimension re-parses the text and never consults a common event/entity set -- is therefore
> a PINNED brain-fidelity gap: the shared event index is the mechanism, and the integration is the computation.

Brain-faithful PREDICTION under test: better event detection (WHO/WHAT) should FEED time (WHEN) and causation
(WHY), because all three read one shared event token. If each dimension re-extracts its own events, that
cross-dimension coupling is ZERO. It is zero.

## Findings (100 LitBank docs; CI over docs)

### (A) NO-REGRESSION -- byte-exact
Every dimension's all-flags-on OUTPUT is byte-identical to its isolated-flag output (`event_set==TA`,
`timeline_order==TR`, `typed_causal==CT`; the flag-independent `entities`/`coref`/`timeline_frames`/`causal_links`
== default). No dimension is degraded by the others being on -- interaction exactly 0. The one non-match
(`event_roles != RR-alone`) is the genuine interaction (below), not a regression.

### (B) SILO STRUCTURE -- the brain-fidelity finding
Perturbing the shared event set (TA on: who-did-what recall 0.656 -> 0.958) leaves EVERY other dimension
byte-identical. On disk, `read()` calls five independent event extractors on three tokenizers. There is no
shared event token; better event detection does not feed time or causation. **The reader is N parallel silos,
not one integrated situation model.**

### (B') CROSS-DIMENSION EVENT-TOKEN OVERLAP -- the silo cost, quantified
Fraction of a dimension's event lemmas that appear in `sm.events` (the event dimension): DEFAULT reader 1.0
(the tense-based extractors agree on past-tense narrative); ALL-ON reader timeline_frames 0.942 / timeline_order
0.925 / causal_links 0.937 / typed_causal 0.969. So the dimensions reference **largely-overlapping but
NON-IDENTICAL** event sets: the independent extractors diverge on 3-8% of events, and even the ~95% that
coincide by lemma are separate objects in separate lists, indexed independently. The silo cost is: 100%
redundant re-extraction + 3-8% outright event-set divergence + zero cross-dimension binding. (The HIGH overlap
is itself informative: a shared event set is FEASIBLE -- the events mostly coincide -- the architecture just
does not build it, so the fix is a wiring job.)

### (B'') OFF-GENRE GENERALIZATION
On 4 constructed MODERN (non-LitBank/non-McGuffey) passages, TA changes the event set but timeline_frames and
causal_links stay byte-identical (4/4). The silo structure is a property of the CODE, not the corpus.

### (B''') WHAT THE SILO ACTUALLY COSTS -- the BINDING PROBLEM (marginals vs joint), demonstrated
A 2nd research drill (`research_what_integration_buys_and_how_to_test_it_2026-08-31.md`) gives the
information-theoretic name for the defect: **a silo stores the MARGINALS (the set of agents, the set of
times, the set of causes); a bound event token stores the JOINT (which agent goes with which time/cause).**
This is the classic binding problem (Smolensky tensor-product binding; VSA/HDC). Any inference that is a
function of the JOINT -- not the product of marginals -- degrades for a silo. Integration-beats-silos is
EMPIRICALLY ESTABLISHED for the brain via a double dissociation (hippocampal amnesia keeps item/feature
memory = marginals, loses conjunctive memory + flexible inference = joint; Konkel & Cohen 2009) -- but is
OPEN for a reading reader. A controlled representational demonstration on the REAL FHRR algebra
(`exp_integrated_shared_event_token_poc_v1.py`, self-test PASS, 300 scenes): two SAME-TYPE events whose
marginal sets {t_a,t_b}/{o_a,o_b} are identical, query "what OUTCOME goes with the event whose TIME is t_a?".
| representation | same-type disambiguation | binding-shuffle flip |
|---|---|---|
| **JOINT** (bound event token) | **1.00** | **1.00** (shuffle-SENSITIVE) |
| **MARGINAL** (silo, strong late-fusion) | **0.47** (chance 0.5) | **0.00** (shuffle-INVARIANT) |
The bound token answers the binding query and collapses when the binding is shuffled (marginals held fixed);
the silo is at chance and is INVARIANT to the shuffle -- it provably lacks the joint. This is the concrete
data-structure reason the silo reader cannot do cross-dimensional inference, and it says the earlier
constructed-narrative failure was a design artifact (at type-cardinality 1 the joint is recoverable from the
marginals) -- not evidence against integration. It is a REPRESENTATIONAL demonstration, NOT a comprehension
score on real text; that proof is the next problem (design below).

### (B'''') SCALING -- a passage-level bound register is quantitatively lossy ("must chunk"), MEASURED
A 3rd drill (`research_how_the_brain_scales_conjunctive_binding_2026-08-31.md`): superposing many bindings into
ONE register loses retrieval SNR ~1/sqrt(M) (Plate; Frady/Kleyko/Sommer), so a passage-level bound token is
lossy -- and the brain does NOT do it. It keeps a SMALL active register (~4 bindings, theta-gamma phase-SLOTS not
superposition; Cowan; Lisman & Idiart 1995), SEGMENTS the stream at prediction-error boundaries (Zacks EST; SEM),
and consolidates flushed events to a pattern-separated episodic store (DG->CA3). Measured (`capacity_curve`, the
BUILT organs): a single flat bundle's decode accuracy over M accumulated events, M=[4,16,64,128,256,512] ->
[1.0, 1.0, 0.99, 0.80, 0.39, 0.12] (COLLAPSES ~1/sqrt(M)); the SLOTTED multibank register (theta-gamma analog) ->
[1.0,1.0,1.0,1.0,1.0,1.0] (holds). A LitBank passage carries ~100-250 events -- inside the collapse zone. So the
faithful shared event token is TIERED (small slotted active register + segmentation + pattern-separated episodic
+ retrieval), NOT one passage superposition -- correcting the next-problem architecture below.

### (B2) THE ONE SHARED FIELD interacts -- MARGINAL + JOINT (additivity)
`sm.events` is co-written by TA (which verbs fire) and RR (their roles). Who-did-what role accuracy (n=11523):
| config | role acc | marginal vs default |
|---|---|---|
| default | 0.1580 | -- |
| TA alone | 0.2433 | **+0.0853** |
| RR alone | 0.1812 | **+0.0232** |
| all-on (joint) | 0.2715 | **+0.1135** |
Additive prediction = 0.1580 + 0.0853 + 0.0232 = 0.2665; observed joint 0.2715 -> **interaction +0.005 (ADDITIVE)**.
Where they share the event token they help each other, additively -- the brain's prediction, and proof the
measurement can detect interaction (so the byte-identical zeros in (B) are real absence). For the silo dimensions
every flag's marginal on the reader's dimension OUTPUT is exactly 0.

### (C) NAIVE AGGREGATE QA -- a rigorous NEGATIVE with named interference
| dimension | default | all-on | strong floor | twin | diff CI |
|---|---|---|---|---|---|
| coref | 0.5559 (n=2799) | 0.5559 | 0.5613 | 0.0 | [0, 0] (unchanged) |
| **events** | 0.1448 (n=11523) | **0.2473** | 0.017 | 0.0 | **[+0.0905, +0.1154]** (null p95 0.0245) |
| temporal | 0.9259 (n=1998) | **None (n=0)** | 0.3664 | -- | [-0.945, -0.906] (instrument collapse) |
| causal | 0.4419 (n=267) | 0.1106 (n=461) | 0.6479 | 0.0 | [-0.389, -0.280] (instrument break) |

**TWO INSTRUMENT COUPLINGS, not reader regressions.** Both the QA temporal gold (`build_temporal_questions`
reads PAST_PERFECT vs SIMPLE_PAST off `sm.events`) and the QA causal gold (`build_causal_questions` locates
events by surface position in `sm.events`) are DERIVED FROM `sm.events`. The keystone TA detector stamps a
PLACEHOLDER tense and adds every present-tense verb, so it (a) zeroes the temporal question set (1998 -> 0) and
(b) inflates the causal set (267 -> 461) into pairings the flag-independent `causal_links` readout no longer
matches (0.442 -> 0.111). The reader's temporal/causal DIMENSION FIELDS do not regress (byte-identical). **The
instrument breaks under the keystone, not the reader** -- every solver who measures temporal/causal QA against
"the reader" with TA on is measuring a broken gold.

### (C-corrected) THE HONEST WHOLE-vs-PARTS AGGREGATE -- criterion (2), MET POSITIVELY
Build ONE fixed question set from the DEFAULT reader (real tense/positions -> a stable gold the keystone cannot
corrupt); answer each via the DEFAULT reader (baseline) vs the ALL-ON reader read through the CORRECTED readouts
(temporal <- `sm.timeline_order`, the actual dimension field; causal <- `causal_links` on the stable gold;
events/coref <- the all-on model):
| dimension | baseline | fully-on-corrected | on-base CI |
|---|---|---|---|
| coref | 0.5559 | 0.5559 | [0, 0] |
| **events** | 0.1580 | **0.2715** | **[+0.0999, +0.1278]** |
| temporal | 0.9259 | 0.9119 | [-0.0379, +0.0128] (equivalent -- no regression) |
| causal | 0.4382 | 0.4382 | [0, 0] |
| **AGGREGATE** | **0.3222** | **0.3993** | **[+0.0664, +0.0891] CI-SEPARATED** |
Info-free twin (scrambled event agents) = 0.0976 (the events win collapses). So **once the instrument reads each
dimension's correct field, the fully-on reader beats the default reader CI-separated (+0.077), driven by event
detection, with every other dimension held.** The naive-aggregate negative was ENTIRELY the instrument coupling.

### (C2) INTERACTION MATRIX + which flags move the aggregate
`default 0.313/1998q | TA 0.283/0q | RR 0.327/1998q | CT 0.313/1998q | TR 0.313/1998q | loo_TA 0.327 | loo_RR
0.283/0q | loo_CT/loo_TR/all_on 0.302/0q`. **RR is the only flag that improves the aggregate without breaking the
instrument. CT and TR alone leave the aggregate UNCHANGED** -- they populate NEW fields (`typed_causal_links`,
`timeline_order`) the QA readouts never consult, so two landed dimensions are invisible end-to-end.

### (D) THE FIX, demonstrated
The corrected temporal readout consuming `sm.timeline_order` answers 0.98 of the tense-gold temporal questions at
0.912 on the all-on model (vs the broken event-tense readout's 0.45 coverage / 0.44 accuracy on that same
placeholder-tense model). Against the DEFAULT reader's WORKING event-tense readout (0.926) it is statistically
equivalent -- so the correct claim is "no temporal regression when read via the right field," not "temporal
improvement."

### (E) The 5th flag + the shared-event wire
- **5th flag (`spacy_pred_gate`)**: suppresses 811 POS-mistagged predicates (default) / 1583 (all-on) and CHANGES
  the event set on 100/100 docs. It is an event-set flag that interacts with TA/RR on `sm.events`, not a silo
  dimension. ("All flags on" is thus 5 flags; the true-all-on config is measured.)
- **The shared-event wire ALREADY EXISTS**: `causation_role_source="reader"` makes typed causation consume
  `sm.events` instead of re-parsing. Connecting it changes 24.2% of typed links (of 8381); with it on, RR changes
  6.7% -- i.e. better event roles DO feed WHY, but only when the wire is connected (off by default). HONEST
  NEGATIVE on benefit: on the validated causation gold (n=42) parse and reader score IDENTICALLY (0.833 [0.714,
  0.929]) -- the curated gold is too clean to show a difference, and no NARRATIVE typed-causation gold exists on
  disk, so whether the wire IMPROVES causation is UNMEASURED (a next problem, not a win).

## What I did NOT establish (withdraw-first list)
1. **That the brain-faithful INTEGRATED architecture beats silos on comprehension of REAL TEXT.** I proved (a)
   the reader COMPOSES and reading each dimension right beats the weak default, and (b) at the REPRESENTATIONAL
   level, a bound event token carries the joint that a marginal silo provably lacks (the binding-shuffle
   demonstration, B'''). What is NOT yet established is the end-to-end COMPREHENSION win on real text -- that
   needs the full shared-token reader + a real cross-dimensional gold (design below), gated on the tense-
   preserving detector. The causation wire came back parse==reader on a gold too clean to discriminate, and my
   first constructed-narrative attempt was a design artifact (joint recoverable from marginals at cardinality 1).
2. **Genre generalization of the comprehension NUMBER.** The silo/no-regression/overlap findings generalize
   (architectural + the off-genre control); the +0.077 aggregate is single-genre (LitBank) -- no modern
   coref+who-did-what gold is on disk.
3. **The causal instrument "fix" is gold-stabilization, not a richer readout.** typed_causal_links answers a
   different (entity-level) question than the connective-direction gold, so I stabilized the gold rather than
   consuming the typed field; a typed-causation-consuming readout is unbuilt.
4. **Event count uses a PLACEHOLDER tense** (TA's known boundary) -- exactly why sharing the event set breaks the
   tense-dependent instruments today; the tense-PRESERVING detector (prior problem, awaiting owner-DONE) is the
   enabling fix.

## KEY REALIZATIONS
- **The brief is a bookkeeping task on its face; the brain question underneath is the deliverable.** Reframing
  "turn all flags on, check nothing broke" as "integrated model or N silos?" turned validation into a PINNED
  architecture finding.
- **No-regression is byte-exact, and that IS the diagnosis.** Perfect orthogonality (each dimension re-extracts
  independently) is what makes no-regression trivially true -- composition without interaction is not integration.
- **A negative aggregate can be an INSTRUMENT artifact; prove it by consuming the actual dimension field.** The
  temporal/causal "regressions" vanish with a stable gold + the timeline_order readout; corrected, the whole
  beats the parts CI-separated. Ask "did the reader regress or did the instrument break?" and answer with an arm.
- **High cross-dimension overlap is the good news.** The dimensions already reference ~95% the same events, so a
  shared token is feasible -- the fix is wiring, and the binding organ is already built.
- **Build the info-free control for the INTERACTION, not just the win.** Showing the shared field interacts
  (additive role-acc) licenses reading the byte-identical zeros as real absence.
- **The silo defect has a precise name: it stores the MARGINALS, not the JOINT (the binding problem).** This
  reframe is what unstuck the "does integration win?" question -- and it explains why my first proof failed
  (at type-cardinality 1 the joint is recoverable from the marginals, so the design leaked the joint into the
  marginals). The NON-GAMEABLE discriminator is BINDING-SHUFFLE INVARIANCE: a joint representation must be
  shuffle-SENSITIVE; a silo is INVARIANT. If your "integrated" arm is shuffle-invariant it is secretly a silo.
- **The brain MUST CHUNK -- so the obvious "one shared register for the passage" fix is itself not brain-faithful.**
  A single FHRR bundle collapses ~1/sqrt(M) (measured: 0.39 at 256 events; a passage has ~100-250), so the
  faithful design is a SMALL slotted active register + prediction-error segmentation + pattern-separated episodic
  store. Drilling the SCALING wall changed the next-problem architecture from "wire one register" to a tiered
  memory system -- and rehabilitated the shelved DG organ by showing its prior fails tested it on the wrong tier.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)
- **E2 (situation-model register / event indexing): the live reader has NO shared event token.** `read()` never
  imports `situation_model_accumulate`/`situation_model_multibank` (the FHRR bind register + `CausalLinkRegister`,
  both BUILT) and runs 5 independent event extractors on 3 tokenizers; PE-driven segmentation is ABSENT (boundaries
  = sentence splits). The assembled reader is PARALLEL SILOS -- a PINNED gap vs the Zwaan/SEM single-indexed-event-
  token mechanism. Quantified: cross-dimension event-token overlap 0.92-0.97 (non-identical sets); the binding
  organ exists but is an unwired island.
- **The QA capstone instrument couples to `sm.events`** for its temporal AND causal gold and never consults
  `typed_causal_links` or `timeline_order`; two landed dimensions are invisible end-to-end. Record so no solver
  quotes a TA-on temporal/causal QA number as a reader property.
- **A single passage-level bound register is NOT brain-faithful (measured "must chunk").** `capacity_curve`
  shows the flat FHRR bundle collapses ~1/sqrt(M) (M=256 -> 0.39; a passage has ~100-250 events), while the
  slotted multibank register holds (1.0 to M=512). The faithful scalable shared event token is TIERED: small
  slotted ACTIVE register + prediction-error SEGMENTATION (flush-and-reset) + pattern-separated EPISODIC store +
  retrieval. **ALL FOUR TIERS ARE BUILT ORGANS, none wired into `situation_reader` (verified: it imports none):**
  active token = FHRR bundle (`situation_model_accumulate`); slotted WM = `situation_model_multibank` +
  `hdlab/slot_attention_wm.py`; boundary controller = `hdlab/n400_coherence_monitor.py` (EST prediction-error
  boundary detector); episodic store = `hdlab/hippocampal_encoder.py` (DG sparse + CA3 auto-associator + CLS
  consolidation) + `cortical_recall.py`. So the next problem is an ASSEMBLY of existing organs, not a build.
- **DG pattern separation was tested on the WRONG TIER (adjacent-component rehabilitation).** The DG HARD_FAILs
  (`exp_dg_pattern_separation_mcscript_purity_v1`, `..._selfplay_dg..._xfit_v1`) tested DG on ACTIVE-read /
  coreference crosstalk. Per the scaling drill, DG's faithful job is the EPISODIC store (decorrelating the
  CONSOLIDATED events written one-at-a-time; Treves & Rolls 1994; Yassa & Stark 2011), NOT active WM (that is
  theta-gamma slots + capacity limit ~4). The prior negatives do not refute DG for its correct tier -- re-scope
  before re-quoting them.

## FOR STRATEGY (you land hdlab, Q111)

### Proposed hdlab diffs (small, all measured here)
1. **Make the QA capstone the FULLY-ON instrument, reading each dimension's correct field**: `_answer_temporal`
   -> `sm.timeline_order` (proven 0.912, statistically equal to the working default readout, and 0.98 coverage);
   build the temporal/causal GOLDS from a tense-independent source, not `sm.events`. This is the correct-baseline
   fix every other solver needs.
2. **No default flip yet.** Corrected, fully-on beats default (+0.077) -- but that is dimensions-read-correctly,
   not the integrated model; and the instrument must be fixed first. RR is the only flag that is aggregate-positive
   AND instrument-safe today.

### THE CORRECT BASELINE (the deliverable the brief asked for)
Every solver should measure against `SituationReader(tense_agnostic_events=True, role_route="wired",
causation_typed=True, timeline_register=True, spacy_pred_gate=True)` -- the fully-on reader -- NOT the default,
with two caveats: (a) score temporal via `sm.timeline_order`, not event-tense; (b) build temporal/causal golds
tense-independently. Its measured per-dimension performance: coref 0.556, who-did-what/events 0.272, temporal
0.912, causal 0.442; aggregate 0.399 vs the default reader's 0.322.

### THE EXACT NEXT PROBLEM: wire a SHARED EVENT TOKEN as the reader backbone (build the integrated model)
The binding substrate is BUILT (`situation_model_accumulate.AccumulateRegister.add_event(entity, role, event_idx)`
+ `decode`; `CausalLinkRegister.add_causal_link(cause_idx, effect_idx)` / `query_effect_of` / `query_cause_of`;
`make_situation_register` factory; `situation_model_multibank` for capacity) -- it is an unwired island. Exact steps:
1. **HARD DEPENDENCY: land the tense-preserving detector first** (prior problem) -- a shared event set needs real
   tense/aspect or TIME breaks (measured: placeholder tense collapses temporal 1998->0).
2. **One canonical event set**: `read()` builds `sm.events` once via the tense-preserving detector (real tense,
   roles from role_route); `EventRecord.global_idx` is the shared token id (already exists).
3. **Dimensions CONSUME sm.events, stop re-extracting**: `_read_timeline`/`_read_timeline_register`
   (situation_reader.py:842,:862) build `T.Event(...)` from `sm.events` and run the SAME Reichenbach ordering
   (`M.reconstruct_order_timeline`/`TOR.DiscreteOrderRegister` toposort) -- only the event SOURCE changes; flip
   `read_typed_causation` default `causation_role_source="parse"->"reader"`. **Engineering risk to budget: the
   ordering/causation modules use their OWN tokenization; align to sm.events via the existing
   `_align_events_to_toks` (situation_reader.py:724)** -- the main implementation cost (I hit this in the
   tense-preserving work).
4. **Bind via a TIERED register -- NOT one passage-level bundle (corrected by the scaling drill +
   `exp_integrated_shared_event_token_poc_v1.capacity_curve`).** MEASURED: a single flat FHRR bundle collapses
   as events accumulate (M=64 acc 0.99 -> M=256 0.39 -> M=512 0.12, ~1/sqrt(M) crosstalk), and a LitBank passage
   carries ~100-250 events -- squarely in the collapse zone. The brain-faithful, scalable design is TIERED
   (research_how_the_brain_scales_conjunctive_binding_2026-08-31.md): (a) a SMALL ACTIVE register = the current
   event token, ~4 bindings, SLOTTED via `situation_model_multibank.MultiBankAccumulateRegister` (the theta-gamma
   phase-slot analog -- MEASURED flat at 1.0 to M=512 where the single bundle is at 0.12), never a passage-level
   superposition; (b) a BOUNDARY CONTROLLER = a prediction-error / Bayesian-surprise detector (`predictive_coding`
   organ) that on a spike FLUSHES the completed token to episodic memory and RESETS the active model (Zacks EST /
   SEM); (c) an EPISODIC STORE = pattern-separated sparse codes (DG->CA3) so flushed events are decorrelated +
   retrievable; (d) RETRIEVAL pulls a prior token back into the active register for coreference/bridging. Bind
   who/what via `add_event(entity, role, global_idx)`, why via `CausalLinkRegister.add_causal_link`, when via the
   temporal rank.
5. **Event SEGMENTATION is now CENTRAL, not an add-on** (the drill's "must chunk" verdict): the boundary
   controller (b) is what keeps the active register in its faithful capacity -- without it a passage register is
   quantitatively lossy. **PRIOR-WORK CORRECTION (disk outranks the drill + an earlier draft of this file that
   called segmentation "un-built"): the boundary detector is ALREADY BUILT** -- `hdlab/n400_coherence_monitor.py`
   (an online EST event-boundary detector: graded content prediction error, running reset, EST relative
   threshold; also EST patch-boundaries in `information_foraging.py`, and `exp_event_boundary_relevance_gate_v1`
   HARD-PASS). So NONE of the four tiers is a from-scratch build; the next problem is an ASSEMBLY of built,
   unwired organs.
6. **Instrument**: QA decodes from `sm.event_register` by event_idx; golds tense-independent (diff #1).
**Validation bar (can-fail; drill-grounded design that a heuristic cannot game --
research_what_integration_buys_and_how_to_test_it_2026-08-31.md):** the discriminating task is SAME-TYPE event
disambiguation, where the marginals are held IDENTICAL across target and distractor and only the binding differs
(a lemma silo is at chance by construction). Concretely: **same-lemma EVENT COREFERENCE on the ECB+ corpus**
(Cybulska & Vossen; real within/cross-document event coref with trigger + participants + time + location;
filter to docs with >=2 mentions of the same trigger lemma; gold = cluster id). BASELINE it must beat: a
LATE-FUSION-of-marginals scorer (sum/max of independent per-dimension similarities -- agent overlap, time
overlap, lemma) + an SBERT baseline (so a win is not lexical overlap). INFO-FREE CONTROL (the clean can-fail
discriminator): **binding-shuffle** -- permute which time/participant attaches to which trigger while keeping the
marginal SETS identical; the integrated reader must drop toward chance and the silo must be invariant. WIN =
integrated beats late-fusion on same-type pairs AND is shuffle-sensitive. DATA-ACQUISITION ACTION: ECB+ is not
on disk -- acquire it (or, as a bridge, hand-build same-type bridging/anaphora items). The representational
half of this bar is ALREADY demonstrated on the FHRR algebra (B''': JOINT 1.00/shuffle-sensitive vs SILO
0.47/shuffle-invariant); the open half is the real-text reader.

### Other ranked next problems
2. **Acquire/build a NARRATIVE typed-causation gold** so "does the shared-event wire help WHY?" (it changes 24% of
   links; is it better?) becomes measurable -- the curated gold is too clean.
3. **Wire the built-but-island Zwaan dimensions**: `location_register.py` (SPACE, PINNED), `state_register.py`
   (STATE) -- landed, registered, unwired; need a prose->motion / state-cue adapter.
4. **BELIEF/ToM last**: `belief_partition.py` + `belief_timeline.py` are built islands but need an observation-cue
   extractor first (their own docstring); adapter-gated. CAUTION: these false-belief-partition organs are NOT the
   relational BRIDGING route that hit Phase 2's kill condition -- check LONG_TERM_PLAN before opening.

## Generalization
The silo / no-regression / overlap findings are architectural (byte-identity of independent extractions;
confirmed on off-genre modern text) and therefore corpus-independent. The +0.077 comprehension aggregate is
single-genre (LitBank; no modern coref+who-did-what gold on disk). The brain-faithful target generalizes: one
shared, relationally-bound event token that all dimensions index (Zwaan/SEM), which makes cross-dimension coupling
the default rather than something re-wired per dimension.

---

## TLDR
We turned on every finished ability of the reader at once for the first time and measured the whole thing on a
hundred stories. Nothing breaks anything else -- each ability produces exactly the same output with the others on
as it does alone -- and when we let the test read each ability off the right place, the fully-loaded reader clearly
beats the stripped-down default. The important finding underneath: the reader is really several separate readers
stapled together -- each re-reads the story on its own and they never share one picture of what happened -- which
is not how the brain works (the brain builds one picture of an event and reads who/when/where/why off that same
picture). That is a real gap to close, and the part needed to close it is already built and just unplugged; we
wrote the exact plug-in plan. Two recently-added abilities are also invisible to our current quiz because the quiz
never looks at what they produce, and the better event-finder confuses the quiz's own answer key (not the reader);
we showed the fix for both.

## QUESTIONS
None.

## NEXT STEPS
1. (strategy) Land the QA-instrument fix (score temporal/causal off the real dimension fields) so every solver
   measures against the correct fully-on reader, not the weak default.
2. (next problem) Wire the shared event token (`situation_model_accumulate`) as the reader backbone per the exact
   6-step plan above -- gated on the tense-preserving detector landing.
3. (next problem) Acquire a narrative typed-causation gold, then measure whether the shared-event wire improves WHY.
4. (assembly) Wire the built-but-island SPACE and STATE dimensions; BELIEF last (adapter-gated, kill-condition aware).

## INTEGRATED_BY_STRATEGY 2026-08-31 -- EXCELLENT (the assembled reader is PARALLEL SILOS = the BINDING PROBLEM; the fix is a TIERED bound-event-token backbone)

Reverified 19/19 FIRST-HAND (`verification/test_assembled_reader_all_flags_on.py`, the 4-doc smoke -- confirms the
MECHANISM byte-exactly; the 100-doc aggregate inherited, direction-reproduced +0.053 on 4 docs): silos byte-exact
([1][2][3][8]); the ONE interaction point ([4] role-routing consumes the event set); the QA instrument-coupling
([5] temporal 106->0, [6] causal readout blind to typed links) + FIX ([7] timeline_order 0.89 vs 0.36); corrected
aggregate survives a fixed gold ([9] events 0.2285 > 0.0993); the wiring gap ([10] shared-event organ built, unimported);
the BINDING-PROBLEM PoC ([11] JOINT disambiguation 1.00 / shuffle-flip 1.00 vs MARGINAL 0.44 / 0.00). Brain-faithful +
PINNED (Zwaan/Radvansky event-indexing = ONE bound token; SEM/Franklin 2020; the binding problem = marginals vs joint;
the brain MUST CHUNK -> tiered, not one superposition). Exemplary honesty (the first joint proof failed at cardinality 1;
the instrument-coupling self-diagnosis; DG-wrong-tier rehab). Graded EXCELLENT. Review + review_text in PROBLEM.md;
priority cleared; audit 2b + FORWARD_BACKLOG folded.

**RECONCILIATION (owner-prompted, disk-grounded):** does NOT contradict the prior "separate stores are optimal" findings
(factorized two-system / sparse cortex / keep-both CLS -- separation by FUNCTION/TIMESCALE, KEPT); the silos here are the
absence of within-EVENT BINDING (a different axis). A prior solver INDEPENDENTLY found the same wall
(`dimensional_phase_diagram_audit`: "the wall is front-end LINKING, not capacity"). p4 is corroborated, not contradicted;
the fix keeps the validated slotted/factorized stores + adds within-event binding.

**LANDING STATE (Q111): THREE decisions.**
- **(a) NO default flag-flip.** Only role_route is aggregate-positive + instrument-safe. Recorded the correct fully-on
  baseline + the silo/instrument caveats in `tools/reader_capabilities.py` (committed c49859fed) -- the correct baseline
  every solver needs.
- **(b) QA-INSTRUMENT FIX -- QUEUED.** Make the QA capstone read each dimension's CORRECT field (sm.timeline_order for
  temporal Qs -> 0.89; a tense-INDEPENDENT causal gold; consume typed_causal_links) instead of the naive sm.events
  readout the keystone rewrites. This is the correct-baseline instrument; land it before the next full-system measure.
- **(c) NEXT PROBLEM -- PACKAGED.** `the_assembled_reader_is_parallel_silos_assemble_the_tiered_bound_event_token`
  (priority 4, ABOVE reasoning per the owner): assemble the TIERED bound-event-token backbone (slot_attention_wm/
  situation_model_multibank slotted register + n400_coherence_monitor boundary + hippocampal_encoder episodic store --
  all built islands) so the dimensions bind onto ONE event token; validate on real event coreference (ECB+) vs a
  late-fusion-of-marginals baseline + the binding-shuffle control. This is the INTEGRATION the assembly was for, and a
  prerequisite for reasoning (you cannot reason over silos).

**🧭 STRATEGIC REFRAME:** the assembly programme is no longer "wire dimension N+1" -- it is "assemble the tiered binding
backbone so all dimensions bind to ONE event token." Wiring dimensions as separate flags was the necessary FIRST step
(each extracting correctly); binding them is the integration step. FORWARD_BACKLOG Phase B updated accordingly.
