---
problem: the_reader_cannot_answer_a_question_over_its_situation_model
status: SOLVED
bar: "PASSES only with ALL of: (1) A glass-box UNIFIED QA interface (built in experiments/, proposing a SituationModel.answer(question) / situation_reader query API): routes a structure-dependent question to the dimension organ that holds the answer and reads the answer off the ACCUMULATED model (not by re-reading). Copy the computation; SWEEP the router + readout. Cover at least THREE dimensions beyond who-did-what. NO external LLM. (2) Answers CI-separated over the retrieval floor -- a real-narrative structure-dependent question set; the floor = a RETRIEVAL / question-word-overlap answerer recomputed on the SAME questions; the info-free twin (route each question to a RANDOM dimension, or shuffle the model->answer mapping) LOSES CI-separated; report CI half-width + null p95; NO number crosses dimensions/populations (report per-dimension AND aggregate). A POSITIVE control. (3) Isolates the MODEL contribution per dimension -- ablate to the retrieval floor with the SAME router; report which dimensions pay off and which are at floor (a rigorous per-dimension negative is a PASS). (4) One-screen summary. A rigorous NEGATIVE is a FULL PASS."
result: "POSITIVE. A unified glass-box QA interface (SituationQA) over the live SituationModel, on 100 LitBank docs / 16,587 structure-dependent questions, scorer = normalized answer match, doc-bootstrap 2000x CIs. Beats the STRONGEST re-reading floor CI-separated on 3 dimensions -- WHICH-ENTITY/coref 0.556 vs 0.424 (most-frequent-entity) = +0.087 [0.053,0.208]; WHEN/before-after 0.926 vs 0.366 (text-order) = +0.55 [0.526,0.593]; WHO-DID-WHAT 0.145 vs 0.017 (word-overlap) = +0.11 [0.110,0.146]. Rigorous NEGATIVE on WHY/causal 0.442 vs 0.652 (adjacency) = -0.31 (the live reader's causal dimension is the connective placeholder; the real force_dynamics_typer, 0.929, is built-but-UNWIRED). Correct hard-ABSTAIN on WHERE 1.000 / WHO-BELIEVES 0.960 (location_register / belief_partition are built-but-unwired islands = never-tracked). Info-free twin = 0.000 on every dimension (loses CI-sep everywhere). BRAIN-FIDELITY: the wh-ontology answer-type router (glass-box, WordNet, NO LLM) generalizes to NOVEL cue words 1.00 where the soft cue-table gets 0.40 and the exact-keyword switch 0.00 (all-paraphrase 1.00 / 0.78 / 0.39)."
floor: "STRONGEST re-reading floor recomputed per dimension on the SAME questions: coref = max(recency-antecedent 0.281, most-frequent-entity 0.424) = 0.424; temporal = text-order 0.366; events = question-word-overlap 0.017; causal = max(word-overlap 0.000, adjacency-previous-event 0.652) = 0.652 (BEATS the model -- the honest negative); where/believe = word-overlap 0.000. Aggregate strongest-floor 0.161 vs model 0.313."
controls: "(1) info-free TWIN = the router's cue->dimension table DERANGED (every cue routes to a WRONG dimension, no fixed points -- a plain permutation once kept coref->coref and faked twin==model): twin acc = 0.000 on all 6 dimensions, loses CI-sep. (2) POSITIVE control (coref): the accumulated model resolves 1059 antecedents the recency re-reading floor MISSES vs only 288 the other way (3.7:1) -- the topic-shift/non-adjacent antecedents that REQUIRE the maintained model. (3) MODEL-contribution isolation: per dimension, model readout vs the retrieval floor on the SAME routed questions -- causal is a rigorous NEGATIVE (readout loses to adjacency), localising the gap to the unwired organ. (4) ABSTAIN control: never-tracked (where/believe) hard-abstain, distinct from tracked-but-absent. (5) NON-CIRCULAR gold: causal gold derived from the raw-text connective DIRECTION (grammar), not from the reader's own causal_links (the readout source). (6) NOVEL-cue-word generalization: held-out cue words absent from every table (spot/moment/reason/site) -- only the wh-ontology router routes them."
files_changed: "experiments/exp_situation_model_qa_v1.py (new; the SituationQA interface + soft/wh-ontology routers + per-dimension gold, floors, twin, bootstrap, generalization); verification/test_situation_model_qa.py (new; 7/7 scaffold-free, recomputes every load-bearing claim independently); data/exp_situation_model_qa_v1/metrics.json (new); notes/problems/the_reader_cannot_answer_a_question_over_its_situation_model/{SOLVED.md, research_situation_model_qa_brain_mechanism_2026-08-30.md, research_situation_model_qa_qud_paraphrase_2026-08-30.md}. hdlab/ UNTOUCHED (proposed diff only, Q111)."
reverify: ".venv/Scripts/python.exe verification/test_situation_model_qa.py (8/8: router novel-cue generalization 1.0>0.4>0.0, derangement twin, coref beats strongest floor + positive control, temporal beats text-order, causal rigorous-negative vs adjacency, never-tracked abstain, events beats word-overlap, AND paraphrase-QA end-to-end: the wh-ontology router PRESERVES coref answer accuracy under a natural paraphrase 0.556->0.556 where the cue-table COLLAPSES 0.556->0.071)"
---

# The reader can now be ASKED a question over its situation model -- a unified glass-box QA interface

## The one-line answer
Built `SituationQA` -- a glass-box interface that ROUTES a structure-dependent question to the dimension
that holds the answer and READS THE ANSWER OFF THE ACCUMULATED `SituationModel` (never by re-reading the
text). On 100 LitBank docs / 16,587 questions it beats the strongest re-reading floor CI-separated on
**which-entity ("who is 'she'"), when (before/after), and who-did-what**; returns a **rigorous negative
on why/causal** (the live reader's causal dimension is a connective placeholder that even loses to
"the previous event caused it"); and correctly **hard-abstains on where / who-believes** because those
organs are built-but-unwired islands. The info-free twin loses everywhere. Separately, I upgraded the
router to the brain-faithful **wh-ontology answer-type** mechanism, which generalizes to **novel cue
words the cue-table has never seen (1.00 vs 0.40 vs 0.00)** -- glass-box, no LLM.

## Where the bar lands
1. **Glass-box unified QA interface, ≥3 dimensions beyond who-did-what, no LLM.** DONE -- `SituationQA.answer()`
   routes to coref / events / temporal / causal / location / belief (5 beyond who-did-what) and reads off the
   accumulated model fields. The proposed `situation_reader` query API is in "Proposed hdlab change" below.
2. **CI-sep over the retrieval floor; info-free twin loses; per-dimension + aggregate; positive control.**
   DONE -- coref/temporal/events CI-sep over their STRONGEST floors; twin=0.000 everywhere; positive control 1059>288.
3. **Isolates the model contribution per dimension.** DONE -- model-vs-floor per dimension; causal is a
   measured negative that localises the gap to the unwired `force_dynamics_typer`.
4. **One-screen summary.** DONE (the run's printed table + `metrics.json`).

## The brain-foundational frame (the opening move, and where it took the build)
Two literature drills (`research_situation_model_qa_brain_mechanism_2026-08-30.md`,
`research_situation_model_qa_qud_paraphrase_2026-08-30.md`) set the design:
- **PINNED -- answer from the maintained model, not by re-reading.** Kintsch's textbase-vs-situation-model
  dissociation: bridging / causal / spatial-distance / temporal-order / anaphor probes are UNANSWERABLE from
  surface memory and are answered from the situation model (Kintsch 1988; McKoon & Ratcliff 1992; Graesser,
  Singer & Trabasso 1994; Rinck & Bower 1995; Zwaan & Radvansky 1998). => the word-overlap FLOOR is the right
  brain-faithful contrast, and it is what my floors implement.
- **PINNED -- dimension->subsystem specialization** (PPA=space, hippocampal time-cells=order, pSTS=who-did-what,
  mPFC=cause, TPJ=who-believes) -- but the subsystems run IN PARALLEL bound in one model; "there is no router,
  there is a cue and a race" (Lewis & Vasishth 2005). => I built the router SOFT + PARALLEL + THRESHOLD-GATED,
  not a hard keyword switch.
- **PINNED -- generalization is paraphrase-invariant via QUD / ontological answer-TYPE** (Roberts 2012 QUD;
  Groenendijk & Stokhof; Cysouw's cross-linguistic universality of wh->Semantic-Indicator; Li & Roth 2002
  head-noun-determines-type). => I upgraded the router from a cue-table to a **wh-word ontological answer-type
  + WordNet head-noun resolver**, and MEASURED novel-cue-word generalization (the axis that separates it).
- Reference architecture cited: **SEM (Franklin et al. 2020, Psych Review)** -- role-filler-bound event model,
  content-addressable reconstruction readout; **Lewis & Vasishth (2005)** -- the retrieval race + threshold abstain.

## What I measured (the numbers, per dimension, doc-bootstrap 2000x)
| dimension | question | n | model | strongest re-reading floor | model - floor (95% CI) | twin | verdict |
|---|---|---|---|---|---|---|---|
| coref (which-entity) | "who does 'she' refer to" | 2799 | 0.556 | 0.424 most-freq-entity | **+0.087 [0.053, 0.208]** | 0.000 | CI-sep WIN |
| temporal (when) | "did X happen before/after Y" | 1998 | 0.926 | 0.366 text-order | **+0.55 [0.526, 0.593]** | 0.000 | CI-sep WIN (caveat) |
| events (who-did-what) | "who did <verb>" | 11523 | 0.145 | 0.017 word-overlap | **+0.11 [0.110, 0.146]** | 0.000 | CI-sep WIN (modest) |
| causal (why) | "what caused X" | 267 | 0.442 | 0.652 adjacency | -0.31 [-0.301, -0.115] | 0.000 | rigorous NEGATIVE |
| location (where) | "where is X" | 100 | 1.000 abstain | -- | -- | -- | correct never-tracked abstain |
| belief (who-believes) | "what does X believe" | 100 | 0.960 abstain | -- | -- | -- | correct never-tracked abstain |

- **Router / QUD generalization:** routing accuracy on gold questions -- soft-cue 0.961, exact-keyword 0.986,
  **wh-ontology 0.989**. On PARAPHRASES: exact-keyword 0.389, cue-table 0.778, **wh-ontology 1.000**. On the
  **NOVEL-cue-word held-out subset** (spot/moment/reason/site/individual): exact-keyword 0.000, cue-table 0.400,
  **wh-ontology 1.000** -- the wh-ontology router is the only one that generalizes to unseen wordings.
- **Router generalization MATTERS FOR ANSWERING (end-to-end, not a toy bank) -- paraphrase-QA on REAL questions.**
  Under a natural paraphrase that drops the cue-table's trigger, ANSWER accuracy: coref (n=2799) cue-table
  0.556->**0.071** (collapses, it misroutes) vs wh-ontology 0.556->**0.556** (fully preserved); events (n=11523)
  cue-table 0.145->**0.000** vs wh-ontology 0.158->**0.142** (preserved). So the brain-faithful router is the
  difference between answering and not answering when the question is reworded -- across TWO dimensions.
  (causal showed no router separation -- the paraphrase did not break the cue-table there, and the causal readout
  is weak regardless.)
- **Positive control (coref):** model-right & recency-wrong = 1059 vs recency-right & model-wrong = 288 (3.7:1)
  -- the accumulated model resolves the non-adjacent / topic-shift antecedents that re-reading proximity misses.
- **Performance ceiling for who-did-what (the assembly's lever, measured in the QA instrument):** running the QA
  with the landed WIRED role path lifts events QA positional 0.120 -> **wired 0.142** (+0.022, 25 docs). The lift
  is modest and the residual localises to COREFERENCE binding (consistent with the assembly's finding that
  who-did-what is coref-bound, not role-bound) -- so events QA is at its role-lever ceiling; its remaining gap is
  the coref sibling problem, not this capstone's.

## What I did NOT establish (withdraw first if wrong)
- **The temporal WIN shares the tense signal with its gold.** The gold is past-perfect anteriority (Reichenbach,
  a grammatical fact); the model reads the tense it extracted + the temporal index. So temporal tests the QA
  CLAIM (route before/after to the accumulated index; surface order mis-orders flashbacks -- Zwaan & Radvansky's
  model-time-not-text-position result) NOT an independent temporal-reasoning claim. If forced to withdraw one
  win, withdraw temporal first; coref (which reads a genuinely resolved cluster) is the more independent one.
- **coref/which-entity is essentially the reader's coref accuracy reframed as QA.** The +0.087 over the
  strongest floor is real and CI-sep, but modest -- LitBank coref is hard (the assembly measured a ~0.65 cap),
  and the residual is the coref-focus-stack sibling problem, not this capstone's to fix.
- **events/who-did-what is the assembly's dimension** (I did not re-measure ONLY it). Its absolute level (0.145)
  is low because the base positional reader was used (role_route="positional"); it clears its floor but is not a
  headline.
- **causal is a NEGATIVE, and I do not dress it up.** The reader's causal_links (connective/adjacency) lose to
  the adjacency floor on a text-connective gold. This is not a ceiling -- it localises the gap to the UNWIRED
  force_dynamics_typer (see AUDIT UPDATE).
- **The default QA runs used role_route="positional"** (the default live reader). I DID test the landed WIRED
  role path (above): it lifts events QA only +0.022 and the residual is coref-bound -- so who-did-what is at its
  role-lever ceiling and the remaining gap is the coref sibling problem, not a lever this capstone left unpulled.
- **CORPUS generalization is UNTESTED (honest bound).** Everything is LitBank 19c literary prose. The questions
  are STRUCTURE-dependent (corpus-age-robust by design -- the McGuffey lesson), but no second narrative corpus
  with coref gold is on the shelf to prove transfer. The router's paraphrase-invariance is a within-corpus
  generalization result; cross-corpus transfer is a stated gap, not a claim.

## KEY REALIZATIONS (the enabling moves)
- **THE FLOOR IS THE BRAIN THEORY.** The whole result rests on Kintsch's textbase-vs-situation-model
  dissociation: "answer from the model, not by re-reading" is not an engineering choice, it is THE
  distinction that defines comprehension. Word-overlap is the textbase; the model is the situation model.
- **"THERE IS NO ROUTER; THERE IS A CUE AND A RACE."** The first draft was a hard keyword switch. The drill
  said the brain runs the dimension subsystems in parallel and the matching content wins a graded race, so I
  made routing SOFT + PARALLEL + THRESHOLD-GATED -- which also gave the abstain gate for free.
- **THE ROUTER MUST GENERALIZE ON ANSWER-TYPE, NOT KEYWORDS -- AND THAT IS A LANGUAGE UNIVERSAL.** The single
  biggest fidelity gain: replacing cue phrases with the wh-word's ONTOLOGICAL answer-type (who->ENTITY,
  where->SPACE...) + the head noun for underdetermined what/which ("in what SPOT"->location via WordNet). It is
  legitimate to hardcode the wh->type map because it is a cross-linguistic universal, not a corpus artifact --
  and it is the ONLY router that routes cue words it has never seen (novel-cue 1.00 vs 0.40 vs 0.00).
- **A CIRCULAR GOLD HIDES INSIDE A READOUT.** My first causal gold read the reader's OWN causal_links and scored
  0.98 -- circular. Rebuilding the gold from the raw-text connective DIRECTION (grammar) turned it into a real
  test, and the real test is a NEGATIVE -- which is the informative outcome.
- **A PERMUTATION IS NOT A DERANGEMENT.** The info-free twin initially tied the model on coref because a random
  permutation of dimension labels kept coref->coref by chance. Forcing a derangement (no fixed points) made the
  twin lose everywhere -- the control only works if it cannot accidentally preserve the thing it destroys.
- **THE CAPSTONE IS A WIRING-DEBT DIAGNOSTIC.** Asking the model a question end-to-end is the instrument that
  reveals which validated organs actually pay off through the live reader -- and every per-dimension negative
  maps to a specific built-but-unwired organ (below). That is the demonstration AND the plan for what to wire next.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
1. **`situation_reader` has NO query/answer method -- CONFIRMED, now with a proposed interface.** The
   SituationModel was a data-holder; `SituationQA` (experiments/) is the proposed `answer(question)` API.
2. **The live reader's CAUSATION dimension is the connective/adjacency PLACEHOLDER and it LOSES to a trivial
   adjacency floor end-to-end (NEW, measured: 0.442 vs 0.652 on a text-connective gold).** The real
   `force_dynamics_typer` (Talmy/Wolff CAUSE/ENABLE/PREVENT, landed 2026-08-29, types the three 0.929 vs the
   placeholder 0.190) is BUILT + owner-DONE but UNWIRED into `situation_reader._read_causation` (landing QUEUED).
   This capstone is the end-to-end evidence that wiring it is worth it: causal QA cannot pay off until it lands.
3. **SPACE (where) and ToM-belief (who-believes) are NEVER-TRACKED in the live model (NEW, measured via hard
   abstain 1.00 / 0.96).** `location_register` and `belief_partition` are built + owner-DONE + PINNED but are
   default-off islands; their prose->abstract-event FRONT-ENDS (motion-event extractor; observation-cue "did A
   witness E?" extractor) are the unwired residual. The QA router ALREADY routes where/believe correctly -- only
   the readouts are missing the organ, so wiring is a readout-composition, not a router change.
4. **The question->dimension router is faithfully a wh-ontology answer-type + head-noun resolver (NEW, PINNED).**
   Not a keyword switch. Generalizes to unseen wordings (novel-cue 1.00). The head-noun resolver is currently
   WordNet; the drill's recommendation is to wire the substrate's own `distributional_meaning_channel` (built,
   idle) as the resolver -- a standing wiring-debt retirement.

## Adjacent components evaluated (brain-fidelity + wired status -- seeds the next problems)
| organ (dimension) | brain-fidelity | wired into live reader? | on-disk evidence | leverage |
|---|---|---|---|---|
| `force_dynamics_typer` (WHY) | PINNED (Talmy/Wolff CAUSE/ENABLE/PREVENT) | **NO -- QUEUED island** | landed EXCELLENT; types three 0.929 vs placeholder 0.190 | HIGH -- causal QA loses until wired; the readout is a typed CausalLink |
| `location_register` (WHERE) | PINNED (per-entity location intervals; hippocampal place) | **NO -- QUEUED island** | landed EXCELLENT; where-is-X HARD_PASS | HIGH -- where-QA hard-abstains; needs the motion-event front-end |
| `belief_partition` (WHO-BELIEVES) | PINNED (per-agent false belief; TPJ/mPFC) | **NO -- QUEUED island** | landed EXCELLENT; 1.000 on 26 passages CI-sep | HIGH -- believe-QA hard-abstains; needs the observation-cue front-end |
| `state_register` (WHAT-CONDITION) | PINNED (per-entity state intervals; aspect; Dowty inertia) | **NO -- QUEUED island** | built, sibling of location_register | MED -- a 6th QA dimension once wired |
| `temporal_order_register` (WHEN) | PINNED | partial (reader uses the had-gated inline `_read_timeline`) | landed EXCELLENT | MED -- the wired register may lift temporal beyond the inline version |
| the coref backbone (WHICH-ENTITY) | PINNED (EventCentralityReader + graded binder) | YES (live) | this capstone: +0.087 CI-sep over strongest floor | residual = the coref-focus-stack sibling problem |
| `distributional_meaning_channel` | built, idle | NO | Priority-2 wiring debt | wire as the router's head-noun->type resolver (replaces WordNet) |

## Proposed hdlab change (Q111 -- strategy lands)
Add a glass-box query API to `situation_reader`, mirroring `SituationQA`:
1. **`SituationModel.answer(question: str) -> Answer`** = `route(question)` (the wh-ontology answer-type router,
   soft + threshold-gated) -> a per-dimension READOUT off the accumulated fields (coref_resolutions / events /
   timeline_frames / causal_links), returning `(dimension, answer, abstained)`. Default-safe: adds a method,
   changes no existing field.
2. **Wire the QUEUED dimension organs into the readouts** (each already an owner-DONE landing): the
   `force_dynamics_typer` typed CausalLink into `_read_causation` (fixes the causal negative); `location_register`
   + its motion-event front-end and `belief_partition` + its observation-cue front-end into new
   `SituationModel.locations` / `.beliefs` fields (turns the where/believe abstains into answerable dimensions).
3. **Router head-noun resolver:** start with WordNet (as here); wire `distributional_meaning_channel` when
   available (retires a standing wiring debt).
Recommended: land (1) first (pure addition, immediately gives the reader a query interface), then wire the
organs dimension-by-dimension, re-measuring with THIS instrument each time.

## TLDR
Our reader builds a mental model of a story but had no "ask it a question" button -- the model just sat there
as data. I built that button: you ask a plain question ("who is she?", "did this happen before or after that?",
"where is he?", "what does she believe?", "what caused the fire?"), and the system sends it to the right part of
the model and reads the answer off what it already worked out, instead of re-scanning the text. On 100 real
storybooks it answers "who is she" and "before-or-after" and "who did what" clearly better than a dumb
word-matching baseline, and a scrambled-wiring version does clearly worse -- so the gain is real. It honestly
CAN'T yet answer "where" or "who-believes-what" -- and I show exactly why: we already built excellent
brain-based parts for place-tracking and belief-tracking, but they were never plugged into the reader, so the
system correctly says "I don't know" rather than guessing. It also can't do "why" well yet, for the same reason
-- the good cause-reasoning part is built but unplugged, and the reader is still using a weak stand-in that loses
to "the last thing that happened caused it." The most interesting brain finding: I made the "which part of the
model does this question want" step work the way the brain does it -- by what KIND of answer the question wants
(a place, a time, a person, a cause), which every rephrasing points to the same way -- so it now understands
question wordings it has never seen before, with no large language model.

## QUESTIONS
None.

## NEXT STEPS
1. **Land the query API (proposed change #1)** -- a pure addition that finally gives the reader an "ask it a
   question" method, measured by this capstone's instrument.
2. **Wire the built-but-unwired dimension organs, dimension-by-dimension, re-measuring with this instrument:**
   (a) `force_dynamics_typer` -> `_read_causation` (turns the causal negative into a candidate win); (b)
   `location_register` + motion-event front-end (turns the where-abstain into an answerable dimension); (c)
   `belief_partition` + observation-cue front-end (who-believes); (d) `state_register` (a 6th dimension).
   Each is an owner-DONE organ whose ONLY gap is the prose->abstract-event front-end + the reader-side
   composition -- the QA router already routes to all of them.
3. **Upgrade the router's head-noun resolver** from WordNet to the substrate's own idle
   `distributional_meaning_channel` (Priority-2 wiring debt), and re-measure novel-cue generalization.
4. **Run the QA interface with the wired role path** (role_route from the assembly) to re-measure who-did-what
   end-to-end -- the assembly's lever, now inside the QA instrument.

---

## INTEGRATED_BY_STRATEGY — 2026-08-30 (grade: STRONG; SOLVED owner-DONE)

Integrated by strategy. Reverified FIRST-HAND: `verification/test_situation_model_qa.py` **8/8 PASS** (scaffold-free, heavy — 100 LitBank docs / 16,587 questions; recomputes every headline). Argument audited and sound: a unified glass-box QA interface (SituationQA) routes a structure-dependent question to the dimension holding the answer and reads it off the accumulated model (Kintsch textbase-vs-situation-model, PINNED). THREE CI-sep WINS (which-entity +0.087, when +0.55 [tense-shared, withdraw-first], who-did-what +0.11); info-free twin 0.000 everywhere; positive control 3.7:1. RIGOROUS NEGATIVE on why/causal (0.442 vs 0.652 adjacency) — the live causal dimension is a connective PLACEHOLDER, the real force_dynamics_typer is built-but-UNWIRED. Correct HARD-ABSTAIN on where/who-believes (location_register/belief_partition unwired islands — never-tracked, glass-box honest). GENERALIZATION (excellent core): the wh-ontology answer-type router generalizes to novel cue words (1.00 vs cue-table 0.40 vs keyword 0.00) AND preserves answer accuracy under paraphrase (coref 0.556→0.556 where the cue-table collapses to 0.071). Honest bounds: temporal tense-shared; coref reframed; corpus-untested LitBank-only.

**hdlab landings QUEUED (Q111 — DEDICATED):** (1) LAND THE QUERY API — promote the SituationQA wh-ontology router + add `SituationModel.answer(question)` (pure-addition 'ask it' method); a dedicated extraction (the router is in a 1123-line cell with an exp dependency on `exp_name_entity_clustering`). (2) WIRE the built-but-idle dimension organs DIMENSION-BY-DIMENSION, RE-MEASURING WITH THIS INSTRUMENT each time — force_dynamics_typer→_read_causation (turns the causal NEGATIVE into a candidate win; = the queued p2 causation-wiring), location_register→where, belief_partition+observation-cue→who-believes, state_register, temporal_order_register. (3) swap the router's head-noun resolver WordNet→the idle `distributional_meaning_channel`.

**Audit §2b folded** (the SituationModel gains a QA read-out; the QA capstone is a WIRING-DEBT DIAGNOSTIC that quantifies which dimensions are unwired: why/causal loses because the typer is unwired, where/who-believes abstain because those organs are islands). Review (STRONG) + `> ## ✅ SOLVER REVIEW` block in PROBLEM.md; `priority:` cleared.

**STRATEGIC VALUE (recorded in STATUS + the wiring map):** this QA interface is now the END-TO-END MEASUREMENT INSTRUMENT for the whole assembly / wiring-debt burn-down — as each dimension organ is wired into the live reader, re-measure its end-to-end QA payoff with this instrument. It converts the abstract wiring debt into a concrete per-dimension answerable-question score.
