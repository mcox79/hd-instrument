# Design: earned semantic-relation inference (satisfy/thwart/cause discrimination + unstated-goal inference)

**Date:** 2026-08-03. **Filed by:** Director (main thread, no dispatch — design/scoping only, per task).
**Purpose:** de-risk + aim the USER's likely-next build on the frontier atom 29640 named
("comprehension_frontier_semantic_relation_synthesis") — the a/b/c investment fork (earn / supply / hybrid).

---

## 0. KB-check (mandatory before design; USER-locked 2026-07-01)

Four `substrate_query.sh --chunk-content --schema-version v2 --tau 0.15 --k 5` queries run before writing anything:

| query | top cosine | verdict |
|---|---|---|
| "satisfy thwart causal relation inference unstated goal coherence" | 0.3818 (`gated_fusion_relation_inference`, capability_registry) | **false-positive match** — see below |
| "situation model coherence margin prediction error event relation inference" | 0.4375 (`research_drill_CI_comprehension_loop_situation_model_brain_mechanism_2026-07-21.md`) | real prior art, build-on |
| "theory of mind mentalizing intention attribution unstated goal inference reader" | 0.3164 (`research_social_interactive_language_acquisition_5x_2026-07-09.md`) | adjacent, different application (reference resolution, not relation/goal inference) |
| "script schema expected event sequence narrative comprehension knowledge structures" | 0.2959 (`research_drill_substrate_novel_concept_formation_2x_2026-06-10.md`) | Schank-Abelson script theory already banked |

**On the top hit (0.3818):** `gated_fusion_relation_inference` (capability_registry, HARD_PASS, WIRED) is a
*text+grounding score-level fusion operator* for the encoder (per-axis learned gate replacing z-avg). Its
"relation-inference" naming refers to a grounding-mammal-relation eval task, not discourse/event relation
inference. Read in full — it is **not prior art on this frontier**, just a name collision; noted here so a
future query doesn't re-read it as a false lead.

**Genuine prior-work base this design builds on (credited, not rediscovered):**
- `notes/research_drill_CI_comprehension_loop_situation_model_brain_mechanism_2026-07-21.md` — names Kintsch CI
  + prediction-error/coherence-gate as the design target for the accumulate organ (already implemented).
- `notes/inference_leap_scoping_beyond_role_decode_2026-08-02.md` — this session's own scoping note that named
  causal-link binding as the next capability, chose explicit-connective-triggered links as the first rung, and
  is the direct design ancestor of the causal-link/goal-pairing cells synthesized in atom 29640.
- `hdlab/self_improving_loop.py` (2026-08-02 promotion) — the validated `decode_coherence_margins` /
  `route_passage` controller: reuses `AccumulateRegister` role-decode top1-vs-runner-up margin as a **gold-free
  coherence signal** to autonomously keep/revert coreference-resolution candidates. This is the concrete
  substrate-native mechanism this design proposes reusing (Section 2).
- Atoms 29633/29634/29636/29638/29639/29640 (math/atoms.jsonl) — the measured frontier itself (Section headline
  numbers cited throughout).
- Schank & Abelson (1977) script theory, already banked (`research_drill_substrate_novel_concept_formation_2x_2026-06-10.md`).

No experiment cell exists yet that applies the coherence-margin controller to relation-type discrimination or
goal-state inference — confirmed genuinely novel at the application level (cosine <0.32 for the two most
relevant fresh queries), while every underlying primitive and citation is reused, not reinvented.

---

## 1. Biology: how does the brain infer these relations without lexical cues?

Four converging literatures, synthesized into one mechanism claim:

**(a) Kintsch Construction-Integration (CI).** CONSTRUCTION activates a *permissive* network of candidate
propositions from text + prior knowledge — including inconsistent/wrong candidates. INTEGRATION is a
constraint-satisfaction *settling* process (spreading activation) that suppresses incoherent candidates and
strengthens coherent ones; the settled state IS the inferred meaning. Applied to relation inference: a relation
(CAUSE / SATISFY / THWART / RESTATE) between two events is not retrieved from a lexical cue at all — it is
**one of several candidate propositions activated during CONSTRUCTION, and it survives INTEGRATION precisely
because binding it into the discourse network raises overall coherence** (reduces the number of dangling,
unconnected, or contradictory nodes) more than any competing candidate relation would. This reframes "infer the
relation" as "run the settling dynamics and read off which relation-hypothesis the network converges to."

**(b) Trabasso causal-network + goal-plan chains.** Trabasso & van den Broek's causal-network model represents a
narrative as events linked by CAUSE edges, with an event's causal status defined relative to an actor's GOAL-PLAN
structure (necessity/sufficiency for reaching a goal-state), not by lexical connectives — causal connectivity
(not textual adjacency) predicts recall/importance (Trabasso & Sperry 1985; Trabasso & van den Broek 1985,
*JML* 24; both already cited in this session's own `inference_leap_scoping...` note). Critically, this is where
SATISFY vs THWART vs RESTATE get their content: given a tracked goal-state G for an actor, an event SATISFIES G
if it transitions G to achieved, THWARTS G if it transitions G to blocked, and RESTATES it if it leaves G's
state unchanged while repeating G's propositional content. This is a **goal-STATE-transition semantics**, not a
surface-content-overlap semantics — which is exactly why content-overlap heuristics cannot distinguish satisfy
from restate (Section 2 makes this precise).

**(c) Zacks/Zwaan event-segmentation via prediction error.** Event Segmentation Theory (Zacks & Tversky 2001;
Zacks et al. 2007, both banked) holds that perceivers maintain a running predictive model of "what happens
next"; a new event boundary is perceived when prediction error spikes. Extending this to relation-TYPE
inference (a step beyond boundary detection, consistent with the theory's own framing): **the relation that
best explains the transition — i.e. that minimizes forward prediction error / maximizes post-hoc coherence — is
the one the comprehender adopts.** This is the same settling logic as (a), stated in a predictive-processing
vocabulary instead of a constraint-satisfaction vocabulary; both licenses are standard in the literature and are
treated here as two views of one mechanism, not two competing ones.

**(d) Mentalizing / Theory-of-Mind network (rTPJ, mPFC).** Saxe & Kanwisher (2003) and the substantial rTPJ
literature since (well-established, not freshly re-verified via web this pass — standard citation, confidence
deflated per lit-scan-calibration discipline) show a dedicated network selectively engaged when explicitly
attributing beliefs/intentions to an agent, distinct from general executive/attention machinery. Applied to
UNSTATED goals specifically: when no goal-statement is lexically present, mentalizing machinery generates a
goal hypothesis via **abductive inference over the agent's action** — "why would this agent do X, given what I
know about agents in this kind of situation?" — biased by script/schema prior knowledge (see (e)) toward
goal-explanations that are typical for the recognized situation type, and the hypothesis is retained/revised
based on whether it predicts the agent's SUBSEQUENT behavior.

**(e) Schank-Abelson scripts/plans.** Script APPLICATION (Schank & Abelson 1977, already banked) supplies the
goal-hypothesis SPACE for (d): recognizing a situation-schema (e.g. "child breaks something valuable") activates
an expected goal ("avoid punishment" / "make amends") without any need for the text to state it — because the
schema itself carries the goal as a slot-filler default. This is precisely WHY 6/9 goal-mediated causal links in
this session's gold have no lexical goal-marker: the goal is pragmatically obvious given the recognized
situation-schema, exactly as Schank predicted, and the reader/schema supplies it, not the text.

**Synthesis — the core brain mechanism**: relation-type and unstated-goal inference are **abductive,
coherence/prediction-error-maximizing inferences over a structured hypothesis space supplied by script/plan
prior knowledge**, resolved by CI-style constraint-satisfaction settling (equivalently, prediction-error
minimization). Two separable sub-jobs fall out of this: (i) WHERE does the hypothesis space come from (scripts/
plans — a knowledge/data question), and (ii) HOW is a hypothesis SCORED against the discourse so far (coherence/
prediction-error — a mechanism question). This maps directly onto the earn-vs-supply fork: (ii) is earnable from
the substrate's own signals; (i) is closer to a supplied-knowledge question. Section 2 develops (ii); Section 3
develops (i); Section 4 (fork c) combines them, which is what the biology itself predicts should happen (scripts
generate hypotheses, coherence-settling selects among them) — not an ad hoc engineering compromise.

---

## 2. Substrate-native earned lever: reuse the coherence-margin, and why it differs from the crude overlap probe

**The existing validated signal.** `hdlab/self_improving_loop.decode_coherence_margins` builds a fresh
`AccumulateRegister`/`MultiBankAccumulateRegister` from a set of (role, event-slot, cluster-id) bindings, then
for each position reports the **top1-vs-runner-up role-decode margin** at that position's own (cluster,
event-slot) query. `route_passage` computes this margin under a BASELINE cluster assignment and under CANDIDATE
alternate assignments, and adopts whichever candidate raises the margin (averaged over positions the candidate
actually changed) above an abstain band — entirely gold-free. This is validated (per that module's own scope
note) at ~67% of oracle achievable gain on DENSE content, but only TIES baseline (with a false-keep failure
mode) on sparser content — **content-density-gated, not general-purpose.** This caveat carries forward
unchanged into everything below.

**Why this is structurally the CI/prediction-error mechanism from Section 1, not a metaphor:** the margin is
literally "how well does this candidate binding fit into the already-accumulated structure" — a settling-quality
readout — computed the same way regardless of what is bound (currently: which entity a mention resolves to; the
proposal below: which relation/goal-state an event participates in). Reusing it for relation-type inference is
not a new mechanism class, it is the SAME organ answering a different binding-hypothesis question — consistent
with the wire-don't-island / no-new-mechanism-class discipline already governing this arc's cells (the causal-
link pilot and the situation-model accumulate-vs-overwrite cell both explicitly followed this "assemble proven
organs" pattern; see their pre-regs).

**Why the earlier coherence-overlap probe over-fired (atom 29634, recall=0.556, FP=0.31, `signal1_attackable:
False`) and this differs:** that probe is a **content-word-overlap** heuristic between two spans — a
textbase/lexical-cohesion signal in Kintsch's own terminology, not a situation-model-level signal. It fires
whenever two spans share vocabulary, REGARDLESS of whether binding them into the discourse structure actually
increases coherence. This is exactly why it cannot discriminate satisfy from restate: **restating a wish
necessarily repeats the wish's own words, so restate pairs score HIGH on lexical overlap by construction** — the
same failure mode that makes textbase-level cohesion a poor proxy for situation-model-level coherence in the CI
literature generally. The accumulate-register margin is different in kind, not just degree: it measures whether
a candidate BINDING (a structural commitment — "this event resolves that goal-slot") is consistent with the rest
of the bound structure, which is exactly the situation-model-level question Kintsch's model says the brain
actually asks. Restating a goal (no state transition) and satisfying it (state transition to resolved) are
structurally different commitments even when their surface words are identical — so a margin computed over the
BOUND STATE, not the raw text, has a chance to separate them where overlap cannot, in principle.

**Honest caveat (mandatory, do not let this design over-promise):** this is a NEW APPLICATION, not a validated
one. The coherence-margin controller has only ever been validated for "which entity does a mention resolve to,"
and even there only on dense content. Whether the SAME margin-delta computation is sensitive to
goal-state-transition semantics (satisfy/thwart/restate) is an open empirical question, not a re-derivation of
an existing result. Anne of Green Gables prose is exactly the kind of content (moderate density, not the dense-
pronoun-verbatim eval the mechanism was validated on) where the controller's own scope note predicts degraded
signal. **Cap confidence at P<=0.50 (novel-synthesis cap) before any run; treat Section 4's fork-(a) pilot as the
test of this specific claim, not as a foregone conclusion.**

**Concrete design for satisfy-vs-restate:** extend the existing `CausalLinkRegister` pattern (already built this
session, `hdlab.situation_model_accumulate.CausalLinkRegister`, subclasses `AccumulateRegister` verbatim) with a
parallel **GOAL_STATE register**: per goal-referent, a `GOAL_OPEN` key bound to the opening event's idx (already
have this from the goal-extractor), plus a `GOAL_STATE` key whose bound value is one of `{OPEN, SATISFIED,
THWARTED}` (three fixed atomic vectors, same construction as role vectors — no new vector class). For each
candidate close-event C, construct TWO counterfactual writes — `bind(GOAL_STATE_key, SATISFIED)` vs leave state
`OPEN`/write a content-only mention with no state-key at all (the "restate" case: content repeated, state
unchanged) — into a copy of the register, then decode the SAME downstream role-queries the causal-link organ
already answers (query_cause_of / query_effect_of for events after C) under each counterfactual and take the
margin delta, exactly as `route_passage` does for coreference candidates. **The relation-type inference reduces
to: which counterfactual write raises downstream decode margin more.** This is a direct transplant of the
validated controller's ADOPTION RULE (`decide_keep_or_revert`, abstain-band gate) onto a new binding-hypothesis
space, using the same primitives, same margin computation, same abstain-band adoption logic.

**Where this lever does NOT reach:** it can only rank/select among hypotheses that already exist as candidate
bindings. It cannot invent a goal that was never extracted at all — it has nothing to write a counterfactual
binding FOR. This is the reason 6/9 extraction-bound goal-mediated items are out of scope for this lever alone
(Section 3/4 addresses that half).

---

## 3. Supplied-data option (forks b/c): minimal relational knowledge and its ceiling

**What generic commonsense KBs already cost, measured (do not re-try):** atom 29634 measured ConceptNet
causal-edge lookup at recall=0.056 (1/18), and that single hit is a degenerate self-loop ("work"->"work") —
**effective recall is 0/18 for real story-specific causal links.** 17/18 gold causal links in this text are
story-specific (Marilla's specific threats, Anne's specific temperament, this book's specific plot mechanics),
not generic-commonsense-matchable. This sets a hard, already-measured ceiling: **large generic commonsense KBs
are not the right supplied-data shape for this problem** — confirmed empirically, not assumed.

**What a minimal, right-shaped supplied resource looks like:** not a big KB, but a small hand/LLM-authored
**SATISFY/THWART/RESTATE relation-frame + goal-schema library** — per the "supply a dictionary/lexicon is
allowed data" discipline (USER-locked 2026-08-02), this is DATA (a small structured vocabulary of goal-types and
their typical resolution patterns), not a bolt-on reading MECHANISM. Concretely: ~15-25 GENERIC children's-
narrative goal-schema frames (e.g. `WANT_OBJECT`, `WANT_APPROVAL`, `WANT_TO_AVOID_PUNISHMENT`, `WANT_ACCEPTANCE`,
`WANT_REVENGE_OR_FAIRNESS`), each frame carrying (a) a short set of typical triggering situation-cues (for
GENERATING a goal hypothesis when no lexical opener exists — the script-application step from Section 1e), and
(b) a typical SATISFY-pattern and THWART-pattern (a state-transition template, not text to match verbatim).

**Ceiling estimate (deflated per lit-scan-calibration discipline, capped at 0.50 for novel synthesis):** such a
library is GENERIC by construction (reusable across any children's narrative, not hand-fit to this book's
answer key) but Anne of Green Gables mixes generic goal-types (wanting acceptance/approval — well covered by a
generic library) with idiosyncratic specifics (wanting a *specific dress with puffed sleeves*, a *specific
scholarship*) that a generic frame can recognize the goal-TYPE of but not the goal's specific content without
some text-grounding step. Realistic estimate: a well-built ~20-frame library plausibly covers the goal-TYPE for
a MAJORITY of the 6 extraction-bound items (most children's-story goals are one of a small number of recurring
types), but exact recall on THIS specific 6-item set should be estimated at roughly **0.30-0.50 (2-3 of 6)**,
not near-complete — deflated from a naive "should cover everything generic" intuition specifically because this
frontier synthesis (atom 29640) already found lexical/pattern methods repeatedly over-promise and under-deliver
on this exact text. **This estimate is speculative (no cell has run) and should be treated as a pre-registration
target for fork b/c's own can-fail gate, not a claim.**

**Overfitting risk (must be designed against, not discovered after the fact):** whoever authors the frame
library will have necessarily read this book's gold goals while authoring it, creating a real risk of covertly
relabeling gold answers as "generic frames." Mitigation for the fair test: author the frame library from
GENERIC children's-narrative goal knowledge only (a small number of well-known universal goal-types), NOT by
reverse-engineering this book's specific 9 gold items, and if possible score it against a second, disjoint text
(a different McGuffey grade's narrative excerpts, already available in the corpus) as an out-of-sample check
before trusting any in-sample number on Anne of Green Gables.

---

## 4. Minimal first build + fair test + can-fail, per fork

### Fork (a) — EARN: coherence-margin as satisfy-vs-restate discriminator (cheapest, recommended FIRST)

- **Cell:** on the 3 pairing-bound goal-mediated items (atom 29639's decomposition: open extracted, but
  content-overlap pairing selects a topical restatement instead of the true distal satisfy event), build the
  GOAL_STATE-register counterfactual-margin mechanism from Section 2 and score which of {true satisfy event,
  the restatement event the overlap-pairing wrongly picked} the coherence-margin-delta prefers.
- **Arms:** (i) coherence-margin-delta (the proposed earned mechanism); (ii) content-overlap score (the EXISTING
  atom-29634/29639 baseline — already measured to fail this exact discrimination, reused not re-run except as
  the same-cell control); (iii) random floor.
- **Can-fail (mandatory, per project discipline):** arm (ii) MUST fail to discriminate on this set (expected —
  it is the SAME signal already shown to over-fire on this exact failure mode; if it unexpectedly succeeds here,
  investigate the harness before trusting anything). Arm (iii) must sit at chance. If arm (i) does not clear a
  real margin over BOTH (ii) and (iii), this is evidence against the "reuse coherence-margin for relation-type"
  hypothesis specifically, and should be reported as a genuine negative (not a ceiling — see Section 2's
  standing caveat about density-gating; investigate whether Anne's content density is the issue before
  concluding the mechanism itself fails).
- **Honest scope:** N=3 is a diagnostic pilot, not a powered test — explicitly flag before running (mirrors the
  causal-link pilot's own "N=10/14 is a pilot, mine to 25-40" honesty pattern). If the pilot is directionally
  positive, the next step is mining more satisfy/restate minimal pairs (same workflow already used for the
  causal-link and coref gold, not a new methodology) before treating any number as a scored claim.
- **Cost:** near-zero new data (reuses existing gold + existing organs); a few hours of hdlab extension work.
  This is why it should run FIRST — it tests the single most novel, most load-bearing idea in this design at
  minimum cost, and is a cheap falsification gate before any script-library-authoring investment (forks b/c).

### Fork (b) — SUPPLY: hand-authored goal-schema library, lookup-only

- **Cell:** author the ~15-25 frame library (Section 3), run pure schema-cue lookup against the 6
  extraction-bound goal-mediated items (no coherence-margin selection step — this isolates the supplied-data
  ceiling from the earned mechanism, per the project's "vet every base ingredient separately" discipline).
- **Can-fail:** ConceptNet-generic baseline is ALREADY measured at effective 0/18 (atom 29634) — reuse that
  number as the standing near-zero floor (do not re-run); the hand-authored library must clear a materially
  higher bar to be worth building further. Pre-registered target per Section 3's estimate: HARD_PASS if
  >=2/6 recovered on the in-sample set AND the out-of-sample disjoint-text check (Section 3's overfitting
  mitigation) is not degenerate (library isn't purely this-book-specific).
- **Honest scope:** N=6 is tiny; any number here is exploratory. The out-of-sample check is not optional —
  without it this fork cannot be trusted at all, since the same person authoring the library has seen the
  answer key.

### Fork (c) — HYBRID (structurally matches Section 1's biology best; recommended as the SECOND build, after (a))

- **Cell:** use fork (b)'s library ONLY to GENERATE candidate goal-hypotheses for the 6 extraction-bound items
  (the script-application/mentalizing-hypothesis-generation step, Section 1d/1e), then use fork (a)'s
  coherence-margin mechanism to SELECT among candidates: bind each candidate hypothesized goal into the
  situation model and check whether the SUBSEQUENT gold-linked event's decode margin rises under the correct
  candidate more than under (i) no-goal-hypothesis and (ii) a wrong candidate drawn from the same library
  (same-library distractor, not a strawman) — directly testing whether the earned signal adds selection value
  ON TOP OF supply, which is the actual question the fork-c framing poses (not just "does supply alone work,"
  already fork b's question).
- **Can-fail:** hybrid-selected accuracy must beat BOTH pure-library-lookup-alone (fork b's arm) and a
  random-candidate-from-library floor; if the coherence-margin selection step adds nothing over pure lookup,
  that is a real (and useful) negative result — it says the supplied data was doing all the work and the earned
  layer was decorative for this particular sub-task, which is exactly the kind of honest finding the symmetric-
  anti-negativity discipline requires reporting even though it would be less exciting than a hybrid win.
- **Sequencing rationale:** fork (c) is gated on fork (a)'s mechanism existing (reuses its counterfactual-margin
  code directly) and fork (b)'s library existing — so it is naturally the third artifact to exist, even though
  it is the fork closest to what Section 1's biology actually predicts (scripts generate, coherence selects).

---

## 5. Recommendation

**Sequence: (a) first, (b) second (can run in parallel with (a) once someone starts authoring the library, since
they don't share code), (c) third.** Rationale: (a) is the cheapest possible test of the single most novel claim
in this whole design (reusing the validated coherence-margin controller for relation-type, not just coreference)
and can genuinely falsify the "earn" half of the fork before any authoring investment is made in (b)/(c). (b) is
a bounded, cheap authoring task with an already-known hard floor (ConceptNet's 0/18) to beat and a real
overfitting risk that must be designed against up front, not discovered after. (c) is the fork closest to the
biology's own answer (scripts generate hypotheses, coherence-settling selects among them) but should not be the
FIRST build because it inherits both (a)'s and (b)'s open risks at once — building it first would confound "did
supply work" with "did the earned signal add anything," exactly the base-ingredient-conflation this project's
own "vet every base ingredient separately" discipline warns against.

**Confidence, explicitly capped per lit-scan-calibration discipline:** the biology grounding (Section 1) is
well-established literature, high confidence in the CITATIONS themselves, but MODERATE-LOW confidence (deflated
0.15-0.25 from a naive read) in how cleanly it maps onto this substrate's specific representations — this is a
novel-synthesis application, capped at P<=0.50 for any of the three forks succeeding as designed on first
attempt. Fork (a)'s pilot is designed specifically to buy real evidence on this cheaply before any larger
investment.

---

## Sources cited

Kintsch, W. — Construction-Integration model (already banked, `research_drill_CI_comprehension_loop_situation_model_brain_mechanism_2026-07-21.md`).
Trabasso, T. & Sperry, L. (1985), *Journal of Memory and Language* 24; Trabasso, T. & van den Broek, P. (1985), *JML* 24 — causal-network model of narrative comprehension (already banked, `inference_leap_scoping_beyond_role_decode_2026-08-02.md`).
Zacks, J.M. & Tversky, B. (2001), *Psychological Bulletin* 127; Zacks, J.M. et al. (2007), *Psychological Bulletin* 133 — event-segmentation prediction-error boundaries (already banked, same note).
Zwaan, R.A., Langston, M.C. & Graesser, A.C. (1995), *Psychological Science* 6; Zwaan, R.A. & Radvansky, G.A. (1998), *Psychological Bulletin* 123 — event-indexing model.
Saxe, R. & Kanwisher, N. (2003), *NeuroImage* 19 — rTPJ selective involvement in explicit mental-state attribution (standard citation, not freshly web-verified this pass — confidence deflated accordingly per lit-scan-calibration discipline).
Schank, R.C. & Abelson, R.P. (1977), *Scripts, Plans, Goals, and Understanding* — script application supplying default goal slot-fillers (already banked, `research_drill_substrate_novel_concept_formation_2x_2026-06-10.md`).
McKoon, G. & Ratcliff, R. (1992), *Psychological Review* 99 vs. Graesser, A.C., Singer, M. & Trabasso, T. (1994), *Psychological Review* 101 — automaticity debate for implicit bridging (already banked, cited for completeness; not directly load-bearing for this design's recommendation).

No new web research was dispatched for this note (design/scoping only, per task instruction). All empirical
numbers (atoms 29633/29634/29636/29638/29639/29640) were read directly off `data/substrate_index/math/atoms.jsonl`
this pass, not recalled from memory.
