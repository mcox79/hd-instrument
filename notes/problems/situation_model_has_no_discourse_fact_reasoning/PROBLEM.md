---
priority: 5
review:
review_text:
---

# PROBLEM: the situation model tracks WHO the characters are (entity nodes) but accumulates no QUERYABLE per-entity DISCOURSE FACTS — the specific "who did what to whom in THIS text" — in a form it can REASON OVER, so on the anti-typical coreference residual (the ~1-in-5 hard cases where grammar, salience, plausibility AND a static knowledge base all point the WRONG way — just MEASURED as the Winograd core) it has nothing to fall back on. Build a reading-built, queryable per-entity FACT store (accumulate (entity, relation, value) predicate-argument facts as the reader processes text) plus a BRIDGING/RESOLUTION operator that resolves a reference by retrieving the accumulated fact that makes the current clause coherent, and show it recovers discourse-fact-decisive cases CI-separated over the fact-BLIND reader with the info-free twin losing — WITHOUT a static commonsense KG (measured dead) and WITHOUT an external LLM (the invariant).

**slug:** `situation_model_has_no_discourse_fact_reasoning` — **opened:** 2026-08-29 by the strategy session (the MEASURED #1
residual lever surfaced by the integrated `the_reader_has_no_coherence_next_mention_prior`, owner-DONE/EXCELLENT — a
rigorous negative whose six-channel refutation named the situation-model discourse-fact store, NOT a coherence prior /
parser / static KG, as the residual's real fix). **status:** OPEN — a MECHANISM + BUILD problem (the comprehension→REASONING
frontier). You build + validate in `experiments/`; strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `5` — HIGH leverage and PHASE-ALIGNED (the owner's named
> comprehension→REASONING next phase): this is the residual's real lever as MEASURED (six brain-faithful channels are all
> dead on the anti-typical residual; the disambiguator is a specific-discourse fact the situation model must accumulate and
> reason over), and the capability GENERALISES far beyond coref — bridging inference, next-event prediction, question
> answering, and the ToM observation cue all consume a queryable discourse-fact memory. Ranked below p3
> (`pronoun_to_event_binding_caps_who_did_what`, +0.444 PROVEN headroom, DOWNSTREAM of this — p3 binds an ALREADY-RESOLVED
> entity to its event; THIS brief RESOLVES the anti-typical entity itself) and p4 (the TIME situation-model facet), because
> its immediate coref-residual leverage is bounded (n=205, an irreducible specific-fact slice) and it is a deep build — but
> the CAPABILITY is the reasoning frontier. **Dependency web:** consumes richer distributional semantics (the p1
> representation lane — the coarse 12-dim grounded space caps the fast selectional layer) and the entity nodes
> (`the_situation_model_tracks_words_not_entities`, SOLVED); composes with the graded coref resolver + situation_model_accumulate.
> **Re-rank per the owner.**

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
"The parson rode past the mare. **He** hummed a tune." We know "he" is the parson — not only because riders (people) hum,
but because we have been READING and hold a little memory of who is doing what in THIS story (the parson is the one riding).
Our reader resolves the EASY "who is she?" cases with grammar. But we just MEASURED that on the ~1-in-5 HARD cases — the
"anti-typical" residual where grammar, salience, word-plausibility AND a 1.2-million-fact knowledge base all point the
WRONG way — the reader has nothing to fall back on. It tracks WHO the characters are (entity nodes exist) but it does NOT
accumulate, in a form it can look things up in and reason over, the specific FACTS about them ("the parson is the one
riding"; "Cheryl is the one who dumped her boyfriend"). The brain resolves these with the slow situation-model RESOLUTION
stage — bridging over facts built BY READING. The task: build a reading-built, QUERYABLE per-entity discourse-FACT memory
plus a reasoning step that resolves a reference by retrieving the fact that makes the current clause coherent, and show it
recovers hard cases that grammar/salience/plausibility/a static fact-base cannot — with no outside AI.

## 2. WHY THIS ONE
It is the residual's real lever AS MEASURED, not a hunch. The just-integrated coherence-prior refutation
(`the_reader_has_no_coherence_next_mention_prior`, owner-DONE/EXCELLENT) proved SIX independent brain-faithful channels
all dead or anti-predictive on the anti-typical residual — for ONE structural reason: the residual is BY CONSTRUCTION the
cases where the typical answer is wrong, so every typicality cue (salience, structure, selectional plausibility,
commonsense-KB connectivity) points the wrong way. The disambiguator is a SPECIFIC-DISCOURSE fact ("who did what in THIS
text"), which a static commonsense KG structurally lacks (MEASURED: 86.8% coverage but 2.8% discrimination — it connects
every candidate but cannot pick the atypical gold) and word-plausibility cannot supply (both candidates are typical
fillers). And it is the owner's named comprehension→REASONING frontier: a queryable discourse-fact memory + bridging is
the capability that generalises to next-event prediction, bridging inference, question answering, and the ToM observation
cue — not a coref-only patch.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** the situation model's slow RESOLUTION stage (Garrod & Sanford 1994) accumulates a
  discourse representation of SPECIFIC entities and their predicate-argument relations, and BRIDGING inference (Clark 1975
  "bridging"; Hobbs et al. abduction; Kehler & Rohde probabilistic coherence) resolves a reference by finding the entity
  whose accumulated role/fact makes the current clause coherent. This is Kintsch's construction-integration (1988) and
  Zwaan & Radvansky's event-indexing (1998); the hippocampus episodically BINDS the (entity, relation, value) conjunction
  and neocortex integrates it; the N400 indexes the coherence/integration cost. World knowledge integrates as fast as word
  meaning (Hagoort 2004), but the DECIDING fact here is discourse-SPECIFIC — held in the situation model, not semantic memory.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the exact fact REPRESENTATION (FHRR-bound `entity ⊛ relation ⊛ value`
  triples in a queryable store over `situation_model_accumulate`), the BRIDGING/retrieval operator (cue the store with the
  current clause's predicate/role, resolve to the best-coherence accumulated entity via `graded_competition`), and the
  confidence/abstain threshold. **Copy the COMPUTATION** (accumulate per-entity predicate-argument facts BY READING; resolve
  reference by retrieving the fact that makes the clause coherent); **SWEEP the representation + threshold.** Reuse the FHRR
  binding, `situation_model_accumulate`'s (entity, role, event) register, `graded_competition`, and the coref stream — NOT a
  hand-rolled rule.
- **NOT brain-faithful:** a STATIC commonsense KG or single-hop plausibility cue (MEASURED DEAD: 2.8% discrimination — the
  documented Winograd ceiling; the ATL hub is DISTRIBUTIONAL/PDP, not symbolic — a KG is not implementation-faithful); an
  external LLM / coref at inference (the invariant); a fact store the reader does not actually BUILD FROM THE TEXT (leakage).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** the coherence-prior refutation
  (`the_reader_has_no_coherence_next_mention_prior`, owner-DONE; `exp_coref_coherence_next_mention_prior_v1.py`,
  `exp_coref_residual_world_knowledge_ceiling_v1.py`): on the anti-typical LitBank residual (n=205, TEST) ALL six channels
  dead/anti-predictive (coherence prior 2.9% oracle, clean-parse structure below chance on cross-domain GAP, WordNet
  selectional 2.0%, ConceptNet/CSKG 2.8% DESPITE 86.8% coverage); the residual is DEFINED as gold-is-NOT-most-recent /
  subject / frequent (gold recency-rank ~2; resolver grabs the most-frequent entity 36%); the RESOLUTION mechanism CAN move
  the metric where the deciding fact is present (positive control 8/8 selectional + 8/8 implicit-causality on constructed
  pairs). Entity NODES already exist (`the_situation_model_tracks_words_not_entities`, SOLVED: AUGMENT keeps BOTH a global
  gist AND entity nodes). The (entity, role, event) register exists (`hdlab/situation_model_accumulate.py`).
- **INFERRED (to prove):** that a reading-built, queryable per-entity FACT store + a bridging/RESOLUTION step lifts a
  discourse-fact-decisive population CI-separated over the fact-BLIND reader (graded coref + entity nodes, no fact store),
  with the info-free twin (shuffled facts / random fact→entity assignment) LOSING — OR a rigorous reason the recoverable
  slice is bounded under the no-LLM invariant (the irreducible specific-interpersonal-world-fact slice the parent named),
  the positive control confirming the metric CAN move.

## 5. ALREADY TRIED / DO NOT RE-RUN
- **Do NOT build a static commonsense KG / single-hop plausibility cue** — MEASURED DEAD on the residual (2.8%
  discrimination despite 86.8% coverage; the documented Winograd ceiling). Do NOT rebuild the coherence next-mention prior
  (refuted), the entity-node tracker (exists), or the FHRR binding operator (pinned). **Do NOT re-solve p3**
  (`pronoun_to_event_binding_caps_who_did_what`) — that binds an ALREADY-RESOLVED entity to its clause event (structural,
  clause_role/Cb); THIS brief is UPSTREAM — it RESOLVES the anti-typical entity itself via accumulated discourse facts, on
  the cases where structural coref FAILS. REUSE `situation_model_accumulate` + the coref stream; the fact store is built BY
  READING (no leakage from gold or an outside model).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `the_reader_has_no_coherence_next_mention_prior/SOLVED.md` (the six-channel refutation, the anti-typical-by-
  construction insight, the positive control) and its `research_world_knowledge_for_reference_2026-08-29.md` (HOW the brain
  applies world knowledge to reference — Garrod-Sanford resolution, ATL PDP hub). Read `hdlab/situation_model_accumulate.py`
  (the (entity, role, event) register), `hdlab/coreference_resolver.py` (the resolved-entity stream), `hdlab/graded_competition.py`
  (the scorer), and `the_situation_model_tracks_words_not_entities/SOLVED.md` (the entity nodes). Run
  `tools/experiment_index.py query "situationmodel"` / `"resolution"` / `"bridging"` / `"coref"` (SINGLE keywords). Audit:
  the newest §2b coref entry (2026-08-29). **Mind the CORPUS-AGE confound** (LitBank/McGuffey are older prose — archaic
  parse noise degrades the extracted facts; test on a clean-parse population too, as the parent's GAP arm did).

## 7. THE BAR
PASSES only with ALL of:
1. **A reading-built, QUERYABLE per-entity discourse-FACT store** (built in `experiments/`): accumulate `(entity, relation,
   value)` predicate-argument facts AS the reader processes text (FHRR-bound over `situation_model_accumulate`), plus a
   BRIDGING/RESOLUTION operator that resolves a reference by retrieving the accumulated fact that makes the current clause
   coherent (via `graded_competition`). Copy the computation; SWEEP the representation + threshold. NO static KG, NO external LLM.
2. **Beats the fact-BLIND reader CI-separated on a discourse-fact-decisive population** — the anti-typical coref residual
   recomputed on the same population, AND/OR a LARGER annotated "accumulate-a-fact-then-refer" task (build one to get power
   beyond n=205). Floor = the graded coref + entity nodes with NO fact store, recomputed on the population. The **info-free
   twin** (shuffled facts / random fact→entity assignment) LOSES CI-separated; report CI half-width + null p95; no number
   crosses populations. A **POSITIVE control** the metric can move (a case an accumulated discourse fact decides and the
   fact-blind reader cannot).
3. **The lift is the FACT STORE + REASONING, not leakage:** ablate the fact store → the reader drops to the fact-blind
   floor; the facts must be BUILT FROM THE TEXT (a gold-leak / outside-model arm is inadmissible); a STATIC-KG arm must NOT
   reproduce the lift (it is measured dead — if it does, the population is not really discourse-fact-decisive).
4. **One-screen summary:** fact representation → population → floor → twin → lift vs the fact-blind reader → verdict. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "a faithful reading-built fact store + bridging resolution recovers X of the
anti-typical residual and the remainder is the irreducible specific-interpersonal-fact slice under the no-LLM invariant —
positive control confirming the mechanism moves the metric"; this closes how much of the residual a glass-box discourse-fact
memory can recover, versus the parent's finding that no typicality cue and no static KG can).

## 8. FILES AND ENTRY POINTS
- **Motivation + refutation (REUSE, do not redo):** `the_reader_has_no_coherence_next_mention_prior/{SOLVED.md,
  research_world_knowledge_for_reference_2026-08-29.md}`; the coref residual harness
  `experiments/exp_coref_coherence_next_mention_prior_v1.py` + the world-knowledge-ceiling arm
  `experiments/exp_coref_residual_world_knowledge_ceiling_v1.py`.
- **Build over:** `hdlab/situation_model_accumulate.py` (the (entity, role, event) register), `hdlab/coreference_resolver.py`
  (the resolved-entity stream + tracked clause_role/Cb), `hdlab/graded_competition.py` (the scorer). Compose-with the entity
  nodes (`the_situation_model_tracks_words_not_entities`). Audit + heavy→REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The six-channel refutation and the 2.8%-discrimination static-KG death are the MOTIVATION (from the coherence integration),
not your result — build the reading-built fact store + bridging resolution and recompute the fact-blind floor on YOUR
population. Do NOT build a static KG (measured dead), re-solve the coherence prior (refuted), or re-solve p3's event-binding
(downstream, different mechanism). Strategy owns any hdlab landing — you propose the store + operator, you do not write `hdlab/`.
