# FORMALIZE spec — the integrated SITUATION MODEL (brain component #5 / DMN): deep brain-fidelity audit at the coverage wall + build-ready increment plan

**Filed:** 2026-08-06 by Director (research), full-auto push, USER-authorized. This is the FORMALIZE
map for the biggest structural gap on the brain-component roadmap (#5, notes/brain_component_map_
narrative_comprehension_ROADMAP_2026-08-06.md) and the answer to USER's "is that the thing that
unlocks the rest? I need a holistic plan." Written per USER 2026-08-06: **"when hitting a wall, do a
deep audit of brain-foundational fidelity with how the brain does it"** — this doc IS that audit for
the coverage wall.

## THE WALL (measured this session, disk-verified)
Coverage, not representation, caps us. On experiments/data/goal_bearing_modern_eval_v1.jsonl (44 items):
- **18/44 (41%) OUTCOME_NEVER_TYPED** — no roster candidate gets an outcome typed at all.
- **owner-attribution real = 13/44 principled**, not the 22/44 headline: 9 "correct" are ALPHABETICAL
  tie-break artifacts (Director VET + relabeling probe on lw_ice_rescue_amy: rename amy->zztarget
  and it flips to wrong — artifact confirmed).
- polarity 31/44 abstain.
These are one wall seen four times: **there is no single accumulating situation model that every organ
reads from and writes to.** Each organ fires on one clause in isolation (`enumerate_and_score` reads
only `_sentences(text)[-1]`) and cannot see what another organ bound earlier. The outcome "types
nothing" because the meaning is dispersed across the passage.

## PHASE 1 — integration-vs-grounding split (measured, Director hand-VET'd)
Of the 31 coverage-failure items: **~29 INTEGRATION-limited (a whole-passage, coref-carrying,
bridging situation model would recover met/unmet relationally), ~0-2 pure GROUNDING-blocked.** Even the
2 grounding-flagged items (spoil-cake, flee-Potter) have an integration/bridging lever on close read.
=> the coverage wall is almost entirely INTEGRATION. This is the eval-scale confirmation of the pivot's
deep finding: **met/unmet is RELATIONAL (did-it-happen / goal-relation), not lexical verb-valence** —
in narrative you rarely need to ground a verb's intrinsic valence because the situation gives you
met/unmet relationally (negation, goal-echo/recurrence, affect reaction, cross-character granting).
The grounding wall is real and deep but a SMALLER residual for this task than the isolated-verb
experiments suggested. **#5 is the near-term keystone.**

## THE DEEP BRAIN-FIDELITY AUDIT — the DMN, per operation (SHAPE + POSITION + METRIC) vs ours vs gap

The DMN is not one mechanism; it is the brain's situation-model hub. Regions: posterior cingulate/
precuneus (central integration hub), mPFC (self/value + mentalizing), angular gyrus (cross-modal event
combination), lateral temporal + ATL (meaning store), hippocampus/MTL (relational binding + episodic
encode/reinstate). It sits at the TOP of the cortical temporal-receptive-window hierarchy (Hasson;
Baldassano 2017; Chen 2017): sensory cortex integrates over ms, language cortex over a sentence, the
DMN over tens of seconds-to-minutes. Its job: integrate the stream of role-bound propositions from
language cortex into ONE amodal, continuously-updated model — who/where/when/why/wanting-what —
segmented into events at prediction-error boundaries, each completed event handed to the hippocampus.

| # | DMN operation | Brain: SHAPE / POSITION / METRIC | OUR organ | Gap | Build |
|---|---|---|---|---|---|
| A | **Role-filler binding** (the substrate of any situation model) | SHAPE: bind fillers to roles, combine to propositions (tensor/conjunctive code). POSITION: LIFG/hippocampus, feeds the model. METRIC: relational-structure decodable | FHRR bind(role*filler)+bundle — **OWNED, fMRI-vindicated (Lalisse-Smolensky)** | none | reuse as-is |
| B | **Amodal gist coding** (not surface words) | SHAPE: modality-independent situation code. METRIC: same pattern across hear/read/recall + across people (Chen 2017) | concept vectors, never tokens — **OWNED (inherent to VSA)** | none | reuse as-is |
| C | **Long-timescale accumulation into ONE persistent register** | SHAPE: a state that persists+updates across many sentences (the "gist"). POSITION: PCC/precuneus hub. METRIC: tracks meaning depending on far-back context | AccumulateRegister + per-entity GoalOutcomeRegister — **OWNED, THIN + ISLANDED** | not shared: each organ keeps its own local state; no single register all organs read+write | **2a** |
| D | **Whole-model outcome resolution** (read the outcome off the integrated model, not the last clause) | SHAPE: the arriving event is interpreted against the WHOLE running model. POSITION: hub integration. METRIC: dispersed/implicit outcomes recovered | `enumerate_and_score` reads only `sents[-1]` (window-widening exists for did-it-happen only) | outcome typed from one sentence in isolation -> 41% never-typed | **2b** |
| E | **Event segmentation at prediction-error boundaries + carry-forward** | SHAPE: hold a stable state within an event, FLIP at high surprise; hand the finished event to hippocampus; carry entities forward. POSITION: DMN+hippocampus. METRIC: boundaries at PE peaks (Baldassano 2017; Zacks EST) | predictive_coding novelty organ (threshold_gate) = the PE detector — **OWNED as a trigger**; not wired as a segmenter | no segment-and-update; entities not carried across sentences ("the child"!->Amy) | **2c** |
| F | **The 5 event-index dimensions** (Zwaan): who / where / when / why / wanting-what | SHAPE: track+update each; break on ANY triggers update (reading slows). METRIC: discontinuity-driven update | who=coref/GoalOutcomeRegister (PARTIAL); why=CausalLinkRegister (THIN); wanting=goal-recog+congruence (PARTIAL); **where=MISSING; when=MISSING** | space+time absent; 3/5 thin | 2a-2c cover who/why/wanting; **space/when DEFERRED** |
| G | **Cross-character / multi-agent structure** (one agent's act caused by/changing another's goal-state) | SHAPE: typed edges linking TWO tracks (vicarious motivation/enablement, request). POSITION: mentalizing net (TPJ/mPFC). METRIC: correct owner via the LINK, not a single winner | select_outcome_owner = single-winner argmax; ties fall to ALPHABETICAL — **MISSING** | can't represent two linked characters; luck-artifacts | **2d** (= Plot-Units ADOPT #1 = USER's ToM build) |
| H | **Prediction (engine underneath)** | SHAPE: generative model predicts next event; PE drives update+segment+learn. Pervasive predictive coding | predictive_coding (thin) — **OWNED** | thin; used for novelty-mint, not narrative prediction | reuse in 2c |
| I | **Belief-revision / order-sensitive supersession** (a later event overrides an earlier state's affect) | SHAPE: TERMINATION — last-state-wins, order-aware. METRIC: reversal recovered | GoalOutcomeRegister.appraise() = symmetric n_unmet>n_met TALLY (Director-VET'd) — **not order-aware** | reversals mis-scored by majority vote | **2a** (= Plot-Units ADOPT TERMINATION) |
| J | **Stored failure-reasons** (why a goal failed, kept in state) | SHAPE: each goal object carries WHY (TALE-SPIN). METRIC: cause retrievable | congruence_decision computes a `detail`/`reason` dict then DISCARDS it | reason never promoted to persistent state | **2a first brick** (= Plot-Units ADAPT #4) |
| K | **Raw-event valence -> goal formation** (a negative event CREATES a goal) | SHAPE: MOTIVATION link (- -> M); amygdala/OFC valence -> PFC goal. METRIC: induced goal-holder correct | goal_congruence_appraisal_type force-dynamics branch = the "-" detector, but islanded in word_acquisition_loop | not exposed to the narrative pipeline; no goal-formation rule | **2c/2d** (= Plot-Units ADAPT #3) |

**Audit verdict:** of the ~11 DMN operations, we already OWN (at least thinly) 6 — binding, amodal
coding, accumulation, PE-detection, prediction, and 3 of the 5 index dimensions. The gaps are (i) the
INTEGRATION itself (C/D/E: one shared, whole-passage, carry-forward register — this is the keystone),
(ii) cross-character links (G), (iii) two small readout/formation fixes (I/J/K) that are largely
plumbing over C, and (iv) two index dimensions (space/when) that are DEFERRED (not what caps narrative
goal-outcome). Crucially: **#5 is mostly WIRING over owned, brain-faithful parts — not a new-mechanism
wall like grounding (#2/#8).** That is what makes it the right next build.

## BUILD PLAN — can-fail increments (each: brain-op, reuse, change, HARD-PASS/HARD-FAIL)

### Track A (cheap, near-term, #5-independent; three are the first bricks of 2a)
- **A1. Order-aware appraise() (op I / TERMINATION).** Change: `GoalOutcomeRegister.appraise()` returns
  a `superseded` readout — the LAST-recorded met/unmet for an entity is authoritative when it differs
  from an earlier one, alongside the existing tally (strict-ADD, tally kept). HARD-PASS: on 6-8
  hand-authored reversal items ("won the race, but was disqualified") the order-aware readout beats the
  tally readout, ZERO regression on non-reversal items + cert 220/3. HARD-FAIL: readouts never diverge
  (fix solves a non-problem) OR any regression.
- **A2. Stored blocking-cause (op J).** Change: `appraise()` gains `blocking_cause` populated from the
  `detail` dict already computed by `congruence_decision` at the UNMET call site (pure plumbing).
  HARD-PASS: on the subset where polarity UNMET is already correct, the stored cause names the
  verb/referent a human would point to for >=80% (small-N hand spot-check). HARD-FAIL: cause generic/
  uninformative on the majority.
- **A3. The 4 remaining did-it-happen items** (from BACKUP NEXT): goal-governing-verb recognition
  (lw_laurie/woz_lion/agg_gilbert), OOV-verb-no-object-referent (agg_anne_mrs_barry), ECM copula-
  referent (woz_dorothy), GAP-2 first-match (lw_meg) + GAP-4 lemma given->give (woz_scarecrow). Each a
  small can-fail fix; several overlap the never-typed set (same items, cheaper depth). HARD-PASS: net
  new-correct on the 15-subset without regression + cert 220/3.

### Phase 2 — the #5 keystone (build in order; each strict-ADD, cert 220/3 held, Director runs witness)
- **2a. Shared per-passage SituationRegister (ops C + I + J).** Change: one register per passage that
  every organ writes to and reads from; reuse AccumulateRegister + GoalOutcomeRegister unmodified as
  the storage; subsumes A1 (order-aware) + A2 (blocking-cause). Behavior-neutral first: replace the
  pipeline hand-offs with read/write to the shared register, prove BYTE-IDENTICAL output on all 44
  items (the register is the substrate, not yet a behavior change). HARD-PASS: 44/44 byte-identical +
  cert 220/3. HARD-FAIL: any output change (means the refactor leaked behavior).
- **2b. Whole-passage outcome resolution (op D).** Change: resolve the outcome slot against the shared
  register across the WHOLE passage (extend the did-it-happen window-widening from `sents[-1]` to the
  accumulated model). Directly attacks the 41% never-typed integration subset. HARD-PASS: never-typed
  18/44 -> <=12/44 (recover >=6 integration-limited items) with ZERO polarity regression on the
  currently-correct 13 + cert 220/3. HARD-FAIL: <3 recovered OR any regression OR a coincidentally-
  class-related earlier clause outcompetes the true outcome (the named window-widening risk).
- **2c. PE event-segmentation + entity carry-forward (ops E + H + K).** Change: wire predictive_coding
  as the segmenter — at a boundary, encode the finished event and carry entities forward so coref
  resolves across sentences ("the child" -> Amy); expose goal_congruence_appraisal_type's force-
  dynamics branch as `raw_event_valence` and, on a NEG event for an animate agent with no typed goal,
  hypothesize a MOTIVATION goal. HARD-PASS: cross-sentence coref recovers the gold owner on >=4 of the
  dispersed-owner items (lw_ice_rescue_amy-class) + induced-goal-holder beats 1/|roster| by a wide
  pre-registered margin on a TALE-SPIN-class harm-clause probe. HARD-FAIL: coref carry-forward
  regresses any currently-correct owner OR induced-goal at chance.
- **2d. Cross-character typed links (op G = Plot-Units ADOPT #1 = ToM build).** Change: when
  directed_goal_outcome_score ties across >1 candidate AND the outcome subject differs from the tied
  goal-holder(s), emit a typed cross-character edge (vicarious MOTIVATION / vicarious ENABLEMENT)
  INSTEAD of the alphabetical fallback; owner read off the edge. HARD-PASS (the decisive one): the
  roster-relabeling probe — swap the alphabetically-first entity on lw_ice_rescue_amy + >=2 more
  rescue/indirection items — owner stays correct across relabelings (proves edge-typing, not
  alphabetical luck). HARD-FAIL: accuracy roster-order-dependent on the relabeled set (still luck).

### Phase 3 — grounding residual (#2/#8), AFTER #5 sizes it
The ~0-2 pure-grounding items + any subset 2b/2c cannot type relationally. Approach via the already-
scoped anchor+propagate / earned-affect route (notes/research_anchor_propagate...; consequence-learning
loop). Deferred until #5 measures the true residual.

## WHAT UNLOCKS WHAT (dependency spine)
#5 integration (2a->2b->2c) -> coverage recovered -> owner-attribution un-starved + did-it-happen fed +
cross-character (2d) enabled. Grounding (#3) -> only the residual #5 cannot reach. #5 is the near-term
keystone; grounding is the deeper keystone behind it.

## NON-GOALS / DEFERRED (explicit)
- Space + time index dimensions (op F) — DEFERRED (not what caps narrative goal-outcome; add when a
  spatial/temporal task demands it).
- Tier-2 over-fire on incidental verbs (gather); registry rows for lexical_similarity /
  verb_lexical_similarity — tracked precision/housekeeping, fold into whichever phase touches those files.
- Grounding of intrinsic verb valence — Phase 3, not #5.
- Do NOT hand-build named complex units (COMPETITION/RETALIATION) — Plot-Units REJECT; falls out of
  2a+2c+2d via similarity search.

## INVARIANTS (hold throughout)
Glass-box always; no borrowed embedding / no LLM at inference / no bolt-on reader (the register is
DATA/structure we own, not a supplied mechanism); reuse owned organs (wire-don't-island); strict-ADD +
cert 220/3 per increment; Director runs every witness; store LOCAL, git-commit after every bank, no
origin push w/o in-session auth. Brain = existence-proof + reference standard.
