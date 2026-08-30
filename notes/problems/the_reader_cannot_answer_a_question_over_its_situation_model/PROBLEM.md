---
priority:
review: STRONG
review_text: "SOLVED (owner-DONE) integrated 2026-08-30 — the comprehension→reasoning CAPSTONE: the reader can now be ASKED a question over its situation model, AND it doubles as a WIRING-DEBT DIAGNOSTIC + measurement instrument. Reverified FIRST-HAND: test_situation_model_qa.py 8/8 (scaffold-free, HEAVY — 100 LitBank docs / 16,587 questions; recomputes every headline). A unified glass-box QA interface (SituationQA) routes a structure-dependent question to the dimension holding the answer and READS THE ANSWER OFF the accumulated model (never re-reading; the Kintsch textbase-vs-situation-model dissociation is the PINNED floor). NO LLM (routing or gold). THREE CI-SEP WINS: WHICH-ENTITY/coref 0.556 vs 0.424 most-frequent-entity (+0.087 [0.053,0.208]; reverify 0.665>0.505, pos-control model-right/recency-wrong 88>22); WHEN/before-after 0.926 vs 0.366 text-order (+0.55; ⚠️ HONEST caveat withdraw-first: model+gold share the tense signal); WHO-DID-WHAT 0.145 vs 0.017 word-overlap (+0.11; modest — the assembly's dimension, at its role-lever ceiling, residual coref-bound). Info-free TWIN = 0.000 on EVERY dimension (deranged router loses CI-sep everywhere); positive control 3.7:1 (the accumulated model resolves 1059 antecedents the re-reading floor misses vs 288). RIGOROUS NEGATIVE on WHY/causal 0.442 vs 0.652 adjacency (−0.31) = a WIRING-DEBT DIAGNOSTIC: the live causal dimension is a connective PLACEHOLDER; the real force_dynamics_typer (0.929, owner-DONE) is BUILT-but-UNWIRED (→ p2 causation-wiring is exactly the fix, and THIS instrument will measure its payoff). Correct HARD-ABSTAIN on WHERE 1.00 / WHO-BELIEVES 0.96 (location_register / belief_partition are built-but-unwired ISLANDS — glass-box honesty: never-tracked, not guessing, NOT a wrong answer). GENERALIZATION (the owner's first-class axis — the excellent-grade core): a wh-word ANSWER-TYPE + WordNet head-noun router (Roberts QUD; Cysouw wh→ontology universal; glass-box, no LLM) generalizes to NOVEL cue words 1.00 vs the soft cue-table 0.40 vs an exact-keyword switch 0.00 — and it MATTERS end-to-end: under a natural PARAPHRASE the cue-table's ANSWER accuracy COLLAPSES (coref 0.556→0.071) while the wh-ontology router PRESERVES it (0.556→0.556; reverify 0.665→0.665 vs cue-table→0.14). Reference architecture SEM (Franklin 2020). BRAIN-FAITHFUL PINNED: answer-from-the-model-not-re-reading (Kintsch); the router is SOFT + PARALLEL + THRESHOLD-GATED cue-race (Lewis & Vasishth 2005; abstain = a feeling-of-knowing gate), dimension→subsystem specialization real (PPA/space, time-cells/order, pSTS/who, mPFC/cause, TPJ/belief). HONEST BOUNDS (withdraw-first): temporal shares its tense signal with its gold (withdraw first); coref is the reader's EXISTING coref reframed as QA (a real +0.087 but not a new capability); corpus generalization UNTESTED (all LitBank 19c — no 2nd narrative coref gold on the shelf); the capstone is AS MUCH A WIRING-DEBT DIAGNOSTIC as a broad comprehension demonstration (only 3 of 6 dimensions win; 2 correctly abstain and 1 loses precisely BECAUSE their organs are unwired). Grade STRONG (a real new capability — the QA interface + the paraphrase-robust wh-ontology router — with rigorous 3-win + rigorous-negative + correct-abstain measurement and an excellent-grade generalization core; deflated from EXCELLENT because it MEASURES the wiring debt more than it broadly demonstrates comprehension, and its two strongest single numbers carry honest caveats). STRATEGY LANDINGS QUEUED (Q111 — DEDICATED efforts): (1) LAND THE QUERY API — promote the SituationQA wh-ontology router + add `SituationModel.answer(question)` (a pure-addition 'ask it' method) — a dedicated extraction (the router lives in a 1123-line cell with an exp dependency on exp_name_entity_clustering); it gives the reader a queryable interface AND is the measurement instrument. (2) WIRE the built-but-idle dimension organs DIMENSION-BY-DIMENSION, RE-MEASURING WITH THIS INSTRUMENT each time (force_dynamics_typer→_read_causation turns the causal NEGATIVE into a candidate win — this is p2; location_register→where; belief_partition+observation-cue→who-believes; state_register; temporal_order_register). (3) swap the router's head-noun resolver WordNet→the idle distributional_meaning_channel (retires a standing wiring debt). Audit §2b folded. **STRATEGIC VALUE: this is now the end-to-end MEASUREMENT INSTRUMENT for the whole assembly / wiring-debt burn-down — each dimension-wiring gets re-measured with it.**"
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-30 (grade: STRONG; SOLVED owner-DONE)
> **Verdict:** the comprehension→reasoning capstone — the reader can now be ASKED a question, and it doubles as a
> wiring-debt measurement instrument. Reverified first-hand (`test_situation_model_qa.py` **8/8**, heavy — 16,587 Qs / 100
> LitBank docs). A glass-box QA interface routes a question to the dimension holding the answer and reads it off the accumulated
> model (never re-reading; Kintsch). **3 CI-sep wins** (which-entity +0.087, when +0.55 [tense-shared caveat], who-did-what +0.11;
> twin 0.000 everywhere). **Rigorous NEGATIVE on why/causal** (0.442 vs 0.652 — the causal dimension is a placeholder; the real
> `force_dynamics_typer` is built-but-unwired → p2 fixes it). **Correct hard-ABSTAIN** on where/who-believes (unwired islands —
> honest, not guessing). **Generalization (the excellent core):** a wh-ontology answer-type router preserves answer accuracy
> under paraphrase (0.556→0.556) where a keyword router collapses (→0.071). Honest bounds (temporal tense-shared; coref reframed;
> LitBank-only). **Grade STRONG.** Landings QUEUED (dedicated): promote the query API (`SituationModel.answer`), wire the idle
> dimension organs dimension-by-dimension re-measuring with this instrument, swap the head-noun resolver to the meaning channel.
> **This is now the end-to-end measurement instrument for the whole assembly / wiring-debt burn-down.** Audit §2b folded; `priority:` cleared.

# PROBLEM: the reader builds a rich SituationModel (entities+coref, events+who-did-what roles, TIME order, CAUSATION type, ENTITIES-state, ToM belief) but there is NO way to ASK IT A QUESTION and get an answer — `hdlab.situation_reader.SituationModel` is a data-holder (entities / events / coref_resolutions / timeline_frames / causal_links) with NO query/answer method, and there is no unified QA organ. The ASSEMBLY (`wire_the_predarg_frontend_and_binder_into_the_live_reader`) proved ONE dimension end-to-end — WHO-DID-WHAT — can be queried over the live reader and beats a positional floor. But comprehension IS question-answering across ALL the dimensions: "where is X now?", "did it happen before or after Y?", "what caused Z?", "who does A think has the ball?", "which 'she'?". Those queries are NOT wired end-to-end and their reader-level QA accuracy is UNMEASURED. Build a UNIFIED, glass-box QA interface over the live SituationModel — route a structure-dependent question to the right dimension organ and answer from the accumulated model, NOT by re-reading — and measure it on real narrative CI-separated over a retrieval/word-overlap floor with the info-free twin LOSING. This is the reasoning+demonstration CAPSTONE: it converts the validated-organ library into a reader that MEASURABLY ANSWERS COMPREHENSION QUESTIONS. Compose the ALREADY-BUILT dimension organs; do NOT rebuild them.

**slug:** `the_reader_cannot_answer_a_question_over_its_situation_model` — **opened:** 2026-08-30 by the strategy session
(the comprehension→REASONING capstone: the SituationModel has all five Zwaan dimensions but no query interface; the
assembly demonstrated only the WHO-DID-WHAT slice end-to-end). **status:** OPEN — a MECHANISM (routing + per-dimension
readout) + MEASUREMENT problem that COMPOSES integrated organs. You build + validate in `experiments/`; strategy lands any
hdlab change (Q111). NO external LLM at inference (the invariant). **SEQUENCING:** this composes the BUILT dimensions
(SPACE/location, TIME/temporal-order, CAUSATION/force-typer, ENTITIES/coref+state, who-did-what). The in-flight belief-timeline
(p4), patient-tendency (p7) and causal-network (p8) DEEPEN specific dimensions — this capstone should compose whatever is
integrated when you start; it does not depend on those landing first, and it must NOT rebuild them.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `5` — HIGH value (this is the "how will I know it's
> really working" demonstration: a reader that ANSWERS questions), but a CAPSTONE that composes the per-dimension organs, so
> ranked below the coref-residual focus-stack (p3, the biggest remaining accuracy lever) and the in-flight dimension builds.
> **Dependency web:** composes `situation_reader` (SituationModel) + the dimension organs (location_register, temporal_order,
> force_dynamics_typer, graded_coref_pick, the who-did-what binder, belief_partition). **⚠️ COORDINATE:** the eventual hdlab
> landing adds a query interface to `situation_reader`, which the assembly reader-wiring landings also touch — BUILD + measure
> in `experiments/` (reader-independent); strategy sequences the landings. **Re-rank per the owner.**

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps — AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) — that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a person reads a story, they build a mental model of it — who's who, what happened, where things are, in what order,
why, and what each character believes — and then they can *answer questions* about it without re-reading. Our reader now
builds that mental model (all those pieces exist), but it has no "ask it a question" button: the model just sits there as
data. We proved ONE kind of question works end-to-end — "who did what to whom" — and it beats a dumb word-matching baseline.
But "where is the ball now?", "did she leave before or after it moved?", "what caused the fire?", "who thinks the ball is in
the basket?" are never actually asked-and-answered from the model, so we don't know if the model is good enough to answer
them. Build one glass-box "ask the model a question" interface — send each question to the right piece of the model and read
the answer off it (not by re-scanning the text) — and show it answers real-story questions better than a baseline that just
matches question words to text words.

## 2. WHY THIS ONE
It is the CAPSTONE the whole situation-model program was for: comprehension is not "extract structure," it is "answer
questions using that structure" (Kintsch's situation model exists to support inference and question-answering; Zwaan's
event-indexing model is validated by exactly these dimension probes). We have spent the program building the dimensions;
this is the first time we ASK THE MODEL and measure whether it can answer — the honest "is it really working?" test the
owner keeps asking for, generalised past the single who-did-what slice the assembly measured. It also surfaces WHICH
dimensions' organs actually pay off end-to-end (the assembly did this for roles: some lifts were real, some were metric
artifacts) — so it is both a demonstration and a diagnostic that seeds the next round of fidelity work.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** comprehension builds a SITUATION MODEL whose PURPOSE is inference and question-answering
  (Kintsch 1988 construction-integration; van Dijk & Kintsch 1983); readers answer probe questions by CONSULTING the
  maintained model, not by re-reading (the model is the queryable memory — Zwaan & Radvansky 1998 event-indexing; the
  hippocampal/DMN situation model). A question SELECTS the relevant dimension (a "where" question queries the spatial index,
  a "when" question the temporal order, a "who-believes" question the ToM partition) — question-type → dimension routing is
  the retrieval-cue-selects-the-store computation.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the question→dimension ROUTER (how a surface question maps to a
  dimension + a slot), the per-dimension READOUT format, and any confidence/abstain threshold. **Copy the COMPUTATION**
  (route by question type to the dimension that holds the answer; read the answer off the accumulated model). **REUSE** the
  integrated dimension organs (do NOT rebuild): coref + who-did-what binder (ENTITIES / who), `location_register` (SPACE /
  where), the temporal-order register (TIME / before-after), the force-dynamics typer (CAUSATION / why), `belief_partition`
  (ToM / who-thinks-what), the state register (ENTITIES-state / what-condition). SWEEP the router + readout + threshold.
- **NOT brain-faithful:** answering by RE-READING / word-overlap against the raw text (that is the FLOOR, not the model);
  a single monolithic classifier that ignores the dimension structure; an external LLM.

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** the assembly measured WHO-DID-WHAT end-to-end over the live reader
  (`wire_the_predarg_frontend_and_binder_into_the_live_reader`, STRONG: role +0.225 CI-sep, who-did-what +0.095 on LitBank).
  The dimension organs are integrated + witnessed (SPACE `location_register`; TIME temporal-order register; CAUSATION
  force-dynamics typer; ENTITIES coref+state; ToM `belief_partition`). `SituationModel` holds entities/events/coref_resolutions/
  timeline_frames/causal_links.
- **INFERRED (to prove):** that ROUTING a structure-dependent question to the right dimension + reading the answer off the
  accumulated SituationModel answers real-narrative comprehension questions CI-separated over a retrieval/word-overlap floor,
  info-free twin LOSING — OR a rigorous, quantified NEGATIVE (e.g. "the model answers where/when CI-sep but who-believes is
  at floor because the ToM population is ~0 in this corpus" — which dimensions pay off, which don't, and why).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT rebuild any dimension organ (coref, who-did-what binder, location/temporal/causation/state/belief) — COMPOSE them.
- Do NOT re-measure ONLY who-did-what (the assembly did that) — the NEW value is the OTHER dimensions' end-to-end QA + the
  UNIFIED router. Do NOT answer by re-reading / word-overlap (that IS the floor). Do NOT build a monolithic LLM-style QA head
  (glass-box routing to dimensions is the point). Do NOT let the prior generic "wire everything" negative
  (`wire_the_validated_organs_into_the_live_reader_and_measure_end_to_end`, which LOST to counting) recur — beat the floor by
  ROUTING to the right dimension, which counting cannot do.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/situation_reader.py` (the SituationModel fields + read()); the assembly SOLVED
  `wire_the_predarg_frontend_and_binder_into_the_live_reader/SOLVED.md` (how who-did-what was queried end-to-end, the
  `_score_event_set` pattern, the counting floor); each dimension organ's SOLVED for its readout. Run
  `tools/experiment_index.py query "question"` / `"answer"` / `"query"` / `"probe"` (SINGLE keywords) AND check
  `notes/STATUS.md` — confirm no existing QA-over-situation-model organ (strategy checked: none as of 2026-08-30, but VERIFY).
  Audit: the §2b entries for every dimension you route to. **Mind the CORPUS-AGE confound:** keep the questions
  STRUCTURE-dependent (who/where/when/why/who-believes), NOT word-MEANING-dependent — structure is corpus-age-robust; a
  meaning-similarity question on 19c/McGuffey prose scored on modern gold is the confounded case.

## 7. THE BAR
PASSES only with ALL of:
1. **A glass-box UNIFIED QA interface** (built in `experiments/`, proposing a `SituationModel.answer(question)` /
   `situation_reader` query API): routes a structure-dependent question to the dimension organ that holds the answer and
   reads the answer off the ACCUMULATED model (not by re-reading). Copy the computation; SWEEP the router + readout. Cover at
   least THREE dimensions beyond who-did-what (e.g. where / when / why / who-believes / what-state). NO external LLM.
2. **Answers CI-separated over the retrieval floor** — a real-narrative structure-dependent question set (constructed from
   LitBank/real narrative with gold answers, per dimension); the floor = a RETRIEVAL / question-word-overlap answerer (pick
   the text span/entity with max word overlap with the question) recomputed on the SAME questions; the **info-free twin**
   (route each question to a RANDOM dimension, or shuffle the model→answer mapping) LOSES CI-separated; report CI half-width
   + null p95; NO number crosses dimensions/populations (report per-dimension AND aggregate). A **POSITIVE control**: a
   question whose answer requires the accumulated model (e.g. "where is X now" after a move the floor's local overlap misses).
3. **Isolates the MODEL contribution per dimension** — for each dimension, ablate to the retrieval floor with the SAME router
   and show the lift is the dimension organ's readout, not the routing alone; report which dimensions pay off and which are
   at floor (a rigorous per-dimension negative is a PASS — it says which organs help end-to-end).
4. **One-screen summary:** question set → floor → twin → per-dimension + aggregate QA accuracy → which dimensions pay off →
   corpus-age note → verdict. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "unified QA beats the retrieval floor CI-sep on where/when/who-did-what but ties on
why/who-believes because those populations are sparse in real narrative — the router works; the corpus lacks the cases").

## 8. FILES AND ENTRY POINTS
- **Compose (integrated — REUSE, do not rebuild):** `hdlab/situation_reader.py` (SituationModel + read()); the dimension
  organs (`location_register`, the temporal-order register, `force_dynamics_typer`, `graded_coref_pick` + the who-did-what
  binder, `belief_partition`, the state register). **Motivation:** the assembly SOLVED (who-did-what end-to-end + the counting
  floor); the 5-dimension Zwaan map. Audit + heavy→REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The dimension organs + the who-did-what end-to-end result are the INGREDIENTS, not your result — the deliverable is the
UNIFIED QA interface (question→dimension routing + per-dimension readout off the accumulated model) and its measurement over
a retrieval floor across MULTIPLE dimensions. Do NOT rebuild any dimension organ, do NOT answer by re-reading, do NOT
re-measure only who-did-what. Strategy owns any hdlab landing and sequences it with the reader-wiring.
