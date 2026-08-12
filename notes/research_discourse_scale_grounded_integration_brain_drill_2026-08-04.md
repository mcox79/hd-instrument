# Discourse-scale grounded integration — brain drill (2026-08-04)

**Method:** FORMALIZE discipline (deep-brain map -> per-component SHAPE/POSITION/METRIC compare
-> name gap -> brain-accurate first step). KB-checked (`director_kb_query.py`, cosine 0.30-0.35 —
weak/partial prior coverage, mostly this same week's drills). Read
`notes/brain_component_functional_map_2026-08-04.md` (organ inventory, disk-verified import
graph) and `hdlab/situation_model_accumulate.py` + `tools/read_anne_glassbox_v2_honest_ledger.py`
directly (code-level, not summary). 2 parallel Sonnet lit-scan sub-agents dispatched for
citation-density breadth (DMN/TRW/event-segmentation thread; situation-model/appraisal thread);
I (Sonnet, synthesis) integrated. Design drill only — no cell authored/dispatched.

---

## HEADLINE

The gap is **NOT primarily a missing brain mechanism** — it is **(c) a representation gap wearing
a wiring-fix costume**. We disk-verified the live situation-model register's `role_vocab =
["agent", "mentioned"]` (`tools/read_anne_glassbox_v2_honest_ledger.py:428`) — there is no GOAL,
CAUSATION, or INTENTIONALITY slot in the accumulated model at all, exactly the three of Zwaan's
five event-indexing dimensions (time/space/causation/intentionality/protagonist) our reader
doesn't track. `CausalLinkRegister` exists but binds only event-index-to-event-index CAUSE/EFFECT
pairs *given as input* (0.9722 capacity, not a selector — per 08-03 ledger), not goal-state or
outcome-valence. Grounded appraisal (`exp_grounded_appraisal_sim_earned_v1`) is a separate
islanded organ that has never been pointed at `AccumulateRegister` at all — it reads local
event-structs, not the accumulated register. So: there is currently **nothing dispersed for the
situation model to integrate**, because the dimensions goal-blocking/affect/causal appraisal
needs were never in the register's vocabulary to begin with. Wiring the appraisal function to the
existing accumulated register (the "wiring fix" reading) would still fail, because the register
has no GOAL/OUTCOME slots to unbind. This is confirmed by the requester's own evidence: VIEW-2
grounded appraisal fires at ~1.4% on naturalistic withhold sentences with no concentration — flat,
not degraded-but-present, consistent with "nothing to bind," not "binding at the wrong window."

**P_deflated = 0.40** (lit-scan calibration penalty applied: base confidence ~0.60 on the brain
literature itself — well-established, multiply-replicated — deflated 0.20 for the substrate-side
adjudication, which rests on reading two source files rather than a full pipeline trace, and for
uncertainty in whether adding goal/causation slots alone clears the wall vs. requiring the
temporal-window/event-boundary mechanism too).

---

## 1. The neuroscience of discourse-scale integration + reading meaning off the integrated model

### 1a. Cortical hierarchy of temporal receptive windows (TRW) — the DMN is the long-window integrator

**Hasson, Yang, Vallines, Heeger, Rubin 2008** (*J Neurosci* 28(10):2539-2550): silent films
scrambled at multiple timescales, measured inter-subject reliability. Early visual cortex (V1,
MT+) reliable under any scrambling (short/sub-second TRW). Higher areas (STS, precuneus, TPJ)
lost reliability under scrambling — a graded cortical hierarchy of integration-window length, not
a binary sensory/cognitive split.

**Lerner, Honey, Silbert, Hasson 2011** (*J Neurosci* 31(8):2906-2915): the direct discourse
analog. A narrated story scrambled at word/sentence/paragraph granularity. Early auditory/language
cortex tracked local (word-level) structure regardless of scrambling. **DMN nodes — precuneus/PCC,
angular gyrus, medial PFC, TPJ, lateral temporal cortex — required intact paragraph-level
structure** to sustain coherent, temporally-extended responses; paragraph-level scrambling
destroyed their tracking even though local word/sentence content was intact. This is the direct
neural substrate for "dispersed-across-sentences must land in the longest-window integrator" —
the DMN literally cannot form a coherent representation unless paragraph-scale structure survives.

### 1b. Event-boundary detection decides WHAT window to integrate over

**Zacks, Speer, Swallow, Braver, Reynolds 2007** (*Psychol Bull* 133:273-293, Event Segmentation
Theory): perceptual/comprehension systems continuously predict the ongoing event; when prediction
error spikes, an event boundary is perceived and a NEW event model is instantiated. This answers
the "what window" question dynamically — integration continues while predictions hold, a window
closes when predictability breaks — not a fixed clock or fixed sentence-count.

**Baldassano, Chen, Zadbood, Pillow, Hasson, Norman 2017** (*Neuron* 95(3):709-721): data-driven
HMM segmentation of fMRI during continuous narrative found a **nested hierarchy** — short events
in sensory cortex, progressively longer/coarser events in higher-order regions (angular gyrus,
posterior medial cortex). High-order event boundaries triggered a **transient hippocampal spike**,
and the size of that spike predicted whether the event was later reinstated in free recall —
hippocampus marks the CLOSE of an integration window for storage/consolidation.

**Chen, Leong, Honey, Yong, Norman, Hasson 2017** (*Nat Neurosci* 20(1):115-125): DMN/angular
gyrus/precuneus patterns during free recall were more similar ACROSS PEOPLE recalling the same
narrative event than within-person perception-vs-recall — evidence the DMN holds a shared,
abstracted, schema-like representation (genuinely integrated content), not a replay of raw
perceptual sequence.

### 1c. Situation-model construction/updating — Kintsch, Zwaan, van Dijk

**Kintsch 1988/1998** (Construction-Integration): three levels — surface code, textbase
(propositional, local inference), **situation model** (integrates textbase + world knowledge,
referentially grounded). Construction loosely activates propositions + associated knowledge
(including irrelevant items); integration settles via constraint-satisfaction/spreading
activation into a coherent structure. The situation model is explicitly the level where
inference-beyond-literal-text happens, reached only after an integration step.

**Zwaan & Radvansky 1998** (*Psychol Bull* 123:162-185) + **Zwaan, Langston, Graesser 1995**
event-indexing model: readers monitor **five dimensions** — time, space, **causation**,
**intentionality (protagonist goals)**, protagonist — as they build the situation model.
Reading-time studies show a discontinuity cost: sentences that break continuity on protagonist or
temporal dimensions relative to the ACCUMULATED model (not the prior sentence alone) cost more
reading time. This is the strongest direct behavioral evidence comprehenders track a genuinely
multidimensional accumulated model, and — critically for the crux below — **goal/intentionality
and causation are named, explicitly-tracked dimensions of that model, not emergent properties of
tracking entities alone.** (Caveat: the spatial-shift leg of the model is the weakest/least
replicated — flagged, doesn't affect the causation/intentionality legs used here.)

**van Dijk & Kintsch 1983**: macrostructure (strategically-derived gist/topic) organizes local
propositions into global coherence across paragraphs — an explicit, online, above-sentence-level
process.

### 1d. Hippocampal relational binding of non-adjacent narrative elements

**Ranganath & Ritchey 2012** (*Nat Rev Neurosci* 13:713-726, PMAT framework): posterior-medial
system (parahippocampal cortex, retrosplenial cortex — context/spatiotemporal) vs.
anterior-temporal system (perirhinal cortex — item/affective), converging on hippocampus for
relational binding. Newer work (Neuron 2023, bioRxiv "Bridges not walls" 2020, Commun Biol 2025)
shows hippocampal boundary-evoked patterns are MORE similar between distant, non-adjacent events
that belong to one coherent narrative than between distant unrelated events — hippocampus performs
genuine long-range relational binding, not recency-chaining. Hippocampus-vmPFC connectivity
predicts sequencing/integration; hippocampus-posteromedial-cortex connectivity predicts
boundary-triggered encoding — a two-process split mapping onto Kintsch's construction (encode) vs.
integration (bind-across-distance).

### 1e. Appraisal computed over the represented situation, not surface features

**Moors, Ellsworth, Scherer, Frijda 2013** (*Emotion Review* 5:119-124) and the broader
Lazarus/Scherer appraisal-theory consensus: appraisal dimensions (goal-relevance,
goal-congruence/blocking, causal attribution/agency, coping potential) are evaluated over a
REPRESENTED situation relative to goals/concerns — not raw stimulus/surface features. (Exact
quoted dimension list from this specific paper unverified in the lit-scan — PDF fetch failed;
existence/venue confirmed via SAGE/PhilPapers; the general claim is not contested in the field and
is independently supported by the Zwaan intentionality/causation dimensions above.)

**Bottom line of Part 1:** the brain's answer is a THREE-PART pipeline — (i) DMN long-TRW cortex
provides the substrate capable of holding paragraph-scale content live, (ii) event-segmentation
(prediction-error-gated) decides window boundaries and triggers hippocampal
binding/consolidation at each boundary, (iii) the situation model that gets built and updated
EXPLICITLY tracks causation and intentionality/goals as first-class dimensions (Zwaan) — and
appraisal (goal-blocking, affect) is computed by reading THOSE dimensions off the model, not by
re-scanning surface text.

---

## 2. Per-component compare (SHAPE / POSITION / METRIC) vs our organs

| Brain component | Our organ | SHAPE (mechanism match?) | POSITION (pipeline placement?) | METRIC (reproduces the function?) | Verdict |
|---|---|---|---|---|---|
| DMN long-TRW cortex (holds paragraph-scale content live, survives local scrambling) | `situation_model_accumulate.AccumulateRegister` / `MultiBankAccumulateRegister` (FHRR bundle-accumulate register, hub per functional map) | RIGHT SHAPE — bundle-accumulate over a persistent register is a legitimate "hold content live across many local events" mechanism, structurally analogous to sustained cortical activity surviving local scrambling | RIGHT POSITION — sits after per-sentence extraction, before decode; the intended discourse-scale hub | **WRONG METRIC for this question**: it accumulates only `role_vocab=["agent","mentioned"]` bindings (disk-verified, `read_anne_glassbox_v2_honest_ledger.py:428`) — capacity-verified (atom 29609, 1.0/0.46/0.21 accumulate/overwrite/floor) but never measured on whether it holds goal/causation content, because that content is never written to it | **GAP (c) — representation gap.** Organ exists, shape is right, but nothing dispersed is ever written into it for appraisal to later read |
| Event-segmentation / prediction-error boundary detection (Zacks; decides WHAT window) | `predictive_coding.py` (novelty/prediction-error residual detector) | RIGHT SHAPE — HARD_PASS as exactly a needs-new-schema-vs-fits discriminator (disequilibrium test, p=0.0003, IQR-overlap 0.0) | **WRONG POSITION** — per functional map, ISLANDED from the reader; imported 0x by the comprehension hub or any standing loop; only lives in throwaway probe cells | Validated on a DIFFERENT task (schema-minting trigger), never run as an event-boundary detector over the reading stream | **GAP — wiring, not build.** The organ that could decide integration-window boundaries is built and validated for the adjacent function; it has never been pointed at the reading pipeline at all |
| Hippocampal relational binding of non-adjacent elements | `coreference_resolver.py` (entity-identity backward search) | PARTIAL SHAPE — coreference is A form of relational binding (which entity is which), but Zwaan's causation/intentionality dimensions are NOT entity-identity; binding "this outcome causally resolves that goal" is a different relation type than "this pronoun refers to that entity" | Right position (feeds situation model) | **FALSIFIED for the adjacent-but-different task**: the coref backward-search was found to implement RECENCY not genuine relational retrieval (0/4 on the recency-trap, per MEMORY 08-03) — the exact failure mode predicted if a recency-shaped mechanism is asked to do hippocampal-style long-range binding | **GAP — the organ we have does a NEIGHBORING relation-type (entity-coref), already shown not to generalize to causal/goal binding when tested directly** |
| Causal binding (event-to-event CAUSE/EFFECT) | `situation_model_accumulate.CausalLinkRegister` | RIGHT SHAPE (same accumulate-organ, reused correctly per MEMORY's reuse discipline) | Right position, extends the hub | **METRIC MISLEADING**: 0.9722 is GIVEN-link write/read capacity — the links must already be identified and supplied; it is not a selector that discovers which event causes which from dispersed text (explicit ledger correction, 08-03) | **GAP — a write/read capacity exists, the SELECTION/DISCOVERY step (which is what "integrate dispersed causation" requires) does not** |
| Goal/intentionality representation (Zwaan dimension) | none found — `exp_goal_*` cells exist per functional map ("PARTIAL — goal_register/goal_close cells on CausalLinkRegister; no standing organ") | NO SHAPE — no dedicated goal-state slot/vector class anywhere in the live register | N/A | N/A | **GAP — BUILD.** This is the one component with no existing organ at all, not even an islanded one |
| Appraisal over the integrated model (goal-blocking -> affect) | `exp_grounded_appraisal_sim_earned_v1` (islanded, per functional map: "blocked on event-extraction to populate appraisal slots") | RIGHT SHAPE for appraisal itself (MECHANISM_EARNS validated: 5 seeds, all 3 floors fail, revenge emerges with no supplied label) | **WRONG POSITION** — reads LOCAL event-structs (2-event bundled window per the 08-03 brain-fidelity audit finding, item 5 in KB scan above: "no GOAL slot, no OUTCOME slot... each event-struct exists only transiently inside a 2-event bundled window"), never the accumulated `AccumulateRegister`/situation model at all | Validated on curated/idealized input where goal+action+outcome are adjacent; never tested reading FROM the accumulated register | **GAP — wiring AND representation.** Even if wired to the register today, the register has no goal/outcome slots to read (confirms the crux is BOTH (a) and (c), not either alone) |

---

## 3. The adjudicated CRUX

The requester posed three hypotheses: (a) wiring fix, (b) missing hierarchical-temporal/
event-boundary build, (c) representation gap (situation model doesn't track the needed
dimensions).

**Adjudication: (c) is the PRIMARY and BLOCKING gap; (a) is real but downstream of (c) and would
not by itself fix anything; (b) is real but SECONDARY — needed for scaling past short passages,
not for the 1.4%-flat failure mode currently measured.**

Evidence:
1. Disk-verified `role_vocab=["agent","mentioned"]` — the live situation model literally cannot
   hold a goal or an outcome-valence, regardless of window size or wiring. This alone explains a
   flat, non-concentrating 1.4% fire rate on naturalistic text: there's no goal/outcome content in
   the register for appraisal to trigger on even in principle, at ANY discourse scale.
2. Wiring the appraisal function to `AccumulateRegister` today (pure (a) fix) would still return
   ~0, because `unbind`+cleanup-argmax against a register with no goal/outcome bindings decodes
   noise, not signal — a wiring fix cannot manufacture content that was never written.
3. Zwaan's event-indexing model (Part 1c) independently converges on the same diagnosis from the
   behavioral-neuroscience side: causation and intentionality are named as EXPLICIT, SEPARATELY
   TRACKED dimensions of the situation model, distinct from protagonist/entity tracking — which is
   exactly the dimension our register omits while it does carry an entity/"agent" dimension.
4. (b) — the hierarchical-temporal/event-boundary mechanism — matters for a different, later
   failure mode: once goal/outcome slots exist, WHICH window's worth of accumulated content to
   read appraisal off (a whole chapter vs. the current event) becomes a real question, and we do
   NOT currently have that mechanism wired (`predictive_coding.py` is islanded from the reader).
   But this is not what's producing the CURRENT flat 1.4% result — a representation with no
   content to threshold on will read as flat regardless of window discipline. (b) is the next wall
   after (c) is fixed, not the current one.
5. The hippocampal-relational-binding component (coref backward-search) was independently
   FALSIFIED as recency-shaped rather than genuinely relational (MEMORY 08-03) — this predicts
   that even once goal/outcome slots exist, a naive reuse of the coref mechanism to bind DISPERSED
   goal-action-outcome triples will likely fail the same way (privileging the nearest candidate),
   which is a live risk for the first-step design below, not a reason to avoid building the slots.

**Confidence on the adjudication itself: MEDIUM.** The (c)-primary reading rests on one grep
(`role_vocab=`) plus one docstring read plus the 08-03 audit note's own text — solid disk evidence,
not a full pipeline trace. It's possible some other consumer of the register writes goal/outcome
content under a different key name not caught by the grep; recommend a 10-minute follow-up grep
for any `role_vocab` construction site with more than 2 roles anywhere in `experiments/` before
committing engineering effort to the first step below.

---

## 4. Organ inventory: do we have it or must we build it (per component)

| Component | Have it? | Organ | Action |
|---|---|---|---|
| Long-window persistent register (DMN analog) | YES, right shape | `AccumulateRegister`/`MultiBankAccumulateRegister` | Reuse as-is; extend its role_vocab (see Step below) |
| Event-boundary/window decision (Zacks analog) | YES, validated, WRONG task/position | `predictive_coding.py` | Re-point/wire, don't rebuild (Exhibit A per functional map — highest-leverage wire already named independently) |
| Relational binding of dispersed elements | PARTIAL, falsified for the needed generalization | `coreference_resolver.py` (entity-coref only) | Do NOT reuse the falsified backward-search pattern for goal-action-outcome binding without a fix; treat as a documented risk, not a solved sub-problem |
| Causal link write/read | YES, right shape, given-link only | `CausalLinkRegister` | Reuse for storage once links are identified; still need a discovery/selection step upstream (unsolved, tracked separately per functional map: "causal-coherence selection (M_backward) — GAP/in-progress") |
| Goal/intentionality slot | NO | — | **BUILD** (smallest true gap: add a GOAL role + an OUTCOME-VALENCE role to the register's role_vocab, mirroring how CAUSE/EFFECT was added as a meta-role set on the SAME accumulate organ) |
| Appraisal-over-integrated-model | Appraisal function YES (islanded); appraisal-over-REGISTER NO | `exp_grounded_appraisal_sim_earned_v1` | Re-point its read side from local 2-event bundled window to `AccumulateRegister.decode(entity, GOAL/OUTCOME role)` once those roles exist |

---

## 5. Concrete brain-accurate first step + can-fail bar

**First step (smallest change, in the (c)-primary reading):** extend `AccumulateRegister`'s
role_vocab used by the live reader from `["agent", "mentioned"]` to include `GOAL` and
`OUTCOME_VALENCE` roles, following the EXACT pattern `CausalLinkRegister` already used to add
`CAUSE`/`EFFECT` as a meta-role set on the same accumulate organ (`situation_model_accumulate.py`
lines 161-209) — no new binding/cleanup mechanism, same organ, same validated capacity math, just
a third role-pair written at extraction time whenever a goal-statement or outcome-statement is
identified in a sentence, regardless of which entity/sentence it's attached to. Then re-point
`exp_grounded_appraisal_sim_earned_v1`'s read side to decode GOAL and OUTCOME_VALENCE off the
accumulated register for the relevant entity instead of its current local 2-event bundled window.
This is brain-accurate in POSITION (matches Zwaan: goal/causation as tracked dimensions of the
SAME situation model that already tracks protagonist) and in SHAPE (reuses the identical
accumulate-bind-unbind organ already validated at atom 29609, mirroring the brain's reuse of one
relational-binding substrate — hippocampus — across dimension types per Ranganath/Ritchey PMAT).

It deliberately does NOT yet build the event-boundary/window-decision mechanism (Part 3's
secondary gap (b)) — that is the correct SECOND step, gated on whether the first step alone
clears the wall (see can-fail bar).

**Can-fail bar (pre-registered):**
- **HARD-PASS**: on the same naturalistic withhold-sentence eval that currently measures ~1.4%
  flat fire rate, VIEW-2 grounded appraisal (now reading GOAL+OUTCOME_VALENCE off the accumulated
  register) fires on a MEANINGFULLY CONCENTRATED subset — i.e., fire rate on true goal-blocked
  items is at least 3x the fire rate on non-goal-blocked control items (not just a uniform lift),
  discriminating rather than uniformly noisier.
- **MIDDLE-BAND**: fire rate rises above 1.4% but stays roughly uniform across goal-blocked vs.
  control items (no discrimination) — indicates the SLOTS help capacity but the SELECTION/binding
  step (which goal binds to which outcome across dispersed sentences) is the real remaining wall,
  pointing at gap (b)/hippocampal-binding-generalization as the next target, not appraisal itself.
- **HARD-FAIL**: fire rate stays flat at ~1.4% or drops — falsifies the (c)-primary reading
  entirely; would mean the representation gap was NOT the blocker and the wiring/window mechanism
  (b) must be built first regardless of slots. In that case, re-open hypothesis (a)/(b) and check
  the "some other consumer writes goal content under a different key" risk flagged in Part 3.

---

## 6. Honest confidence + biggest risk

**Confidence: MEDIUM (P_deflated=0.40).** The neuroscience half (Part 1) is high-confidence,
multiply-replicated, textbook literature — the deflation is entirely on the substrate-side
adjudication (Part 3), which is disk-evidence-based but not a full pipeline trace, and on whether
extending role_vocab alone (vs. needing the event-boundary mechanism too) actually clears the
wall — genuinely uncertain until tested.

**Biggest risk:** the coreference-resolver's documented falsification (recency-shaped, not
genuinely relational, 0/4 on the recency-trap) is a warning sign for the natural next
implementation temptation — reusing the SAME backward-search pattern to decide which GOAL binds to
which OUTCOME across dispersed sentences once slots exist. If that reuse is done naively, the
architecture will likely reproduce the identical recency-privileging failure one level up (picking
the nearest goal-outcome pair instead of the causally-correct dispersed one), which is precisely
the naturalistic-prose failure mode the requester is trying to escape. The first step above sidesteps
this risk by NOT yet building any binding/selection logic — it only adds the slots and re-points
appraisal's read source — but the SECOND step (goal-outcome binding across dispersed sentences)
should explicitly design against recency-privileging from day one, per the causal-coherence
credit-assignment 2x drill (2026-08-03) which already flagged this as an open, unsolved
selector problem.

---

## Citations (verified count)

Verified via 2 independent parallel Sonnet lit-scan sub-agents (WebSearch/WebFetch, secondary
sources cross-checked): **9 of 10** citations independently corroborated with venue/year/finding
(Hasson 2008, Lerner 2011, Baldassano 2017, Chen 2017, Zacks 2007, Kintsch 1988/1998, Zwaan &
Radvansky 1998 / Zwaan-Langston-Graesser 1995, van Dijk & Kintsch 1983, Ranganath & Ritchey 2012).
**1 of 10 partially unverified**: Moors, Ellsworth, Scherer, Frijda 2013 — venue/existence
confirmed (SAGE/PhilPapers listings) but exact quoted appraisal-dimension list not independently
re-derived from primary text (PDF fetch failed); flagged, not used as load-bearing evidence (the
Zwaan intentionality/causation dimensions independently carry the same claim). Radvansky 2012
Event Horizon Model cited from general knowledge, not independently re-verified by the sub-agents
in this pass — flag as MEDIUM confidence, consistent with but not confirmed against a fresh fetch.
