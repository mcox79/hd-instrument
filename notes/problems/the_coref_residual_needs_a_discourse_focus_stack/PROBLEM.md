---
priority:
review: EXCELLENT
review_text: "SOLVED (owner-DONE) integrated 2026-08-30 — a MODEL result: a rigorous NEGATIVE on the brief's named mechanism + the REAL brain-faithful fix found by reading the hard cases, validated through the ACTUAL landed resolver, and generalization-tested exhaustively (exactly the owner's push). Reverified FIRST-HAND: test_coref_residual_focus_and_participant.py 45/45 (scaffold-free; recomputes every headline from source INCLUDING the landing validation through graded_antecedent_pick, W38-W45). (1) FOCUS-STACK REFUTED: a faithful Grosz-Sidner push/pop focus stack given the STRONGEST oracle segmentation (gold quote spans + paragraph breaks + entity-topic-shift) diverges from finer TOKEN-locality in 1/420 and does NOT beat it (focus 0.481 vs token-recency 0.479, NOT_SEP); quote-shuffle twin ties; the ~50-60% focus estimate (speculative by-elimination) is disproven — a rigorous negative = a full pass, and the key discipline lesson: the solver's FIRST focus stack keyed on (segment, token-position) which is monotone and silently reduced to token-recency (measure the oracle with the BRAIN's operation or you measure your own bug). (2) THE REAL FIX = HARD PHI-AGREEMENT on the candidate set. The pool (~45 candidates) admits grammatically-impossible antecedents because the substrate's _gn_compat is PERMISSIVE (unknown passes) — above all the discourse PARTICIPANT (the narrator 'I'/'we', most salient so grabbed for every 'he'/'she'). PERSON exclusion +0.083 CI-sep on the residual (recall 1.000); ANIMACY a 2nd clean lever (+0.123 LEXICAL no-gold-NER; it/its +0.125; person+animacy COMPOSE +0.152); GENDER the PRINCIPLED EXCEPTION (+0.010 NOT_SEP — person/animacy are established immediately by the pronoun form / head noun, a freshly-named character's gender is not, so it cannot fire causally — the exception proves the rule; positive gender was a LEAK that used future mentions). (3) VALIDATED THROUGH THE ACTUAL LANDED graded_antecedent_pick: a REFINED pure-participant rule (says I/we AND never narrated in 3rd person = the true narrator, not a talkative character) lifts the FULL deployed workload n=9139 0.786->0.841 (+0.054 CI-sep, recall 0.996); residual 0.057->0.219 (+0.162); +animacy 0.854. (4) GENERALIZES every aspect tested: 1st-person +0.147 CI-sep, 3rd-person +0.006 ABOVE (no longer a regression), person AND neuter classes, every exclusion threshold from 'any 1st/2nd mention' (+0.117) to '100% participant' (+0.050) beats the floor (not a tuned knob), cross-linguistic UNIVERSALS (Benveniste 1966; Mancini 2011 person-violation N400; Cysouw 2003; Silverstein 1976), and the lexical no-gold-NER arm beats gold entity-type (the anti-cute-trick test: a principle helps proportional to how much a text violates it — 1st-person +0.137, 3rd-person neutral; a trick would help uniformly). Info-free random-drop twin LOSES (recall collapses to 0.64). BRAIN-FAITHFUL PINNED: person + animacy are OBLIGATORY, immediately-established, cross-linguistically universal anaphora constraints; HARD EXCLUSION is MORE faithful than a graded down-weight (recall 1.000 confirms the corpus essentially never violates it). OUR-INVENTION (flagged): the refined participant proxy + the lexical animacy lexicon. HONEST withdrawals: the focus stack does not help (1/420); NO large modern natural coref corpus on disk (generalization rests on the within-LitBank genre split + cross-linguistic universality + the no-gold-NER arm); the residual is not closed to zero (they/them is animacy-unconstrained; a finer clause-locality slice + a ~2-3% genuinely-semantic core remain). Grade EXCELLENT (rigorous negative on the named mechanism, real fix from reading the cases, validated through the REAL resolver, exhaustive generalization + anti-cute-trick, exemplary honesty). hdlab landing DONE (Q111, additive/opt-in): appended is_discourse_participant + phi_agreement_keep + FIRST_SECOND_PERSON_EXT to graded_coref_pick.py (compose with keep_after_pool_cleanup; existing callers byte-unchanged; inert until a caller opts in); witness test_phi_agreement_prefilter_organ.py added. The reader-WIRING (apply the pre-filter to the live coref pool) is COUPLED with the assembly (Changes 2-3). Do NOT add the focus stack / a positive gender cue / the global (non-refined) participant rule. Audit §2b folded. Follow-ons: they/them animacy-unconstrained resolution; confidence-gated finer clause-locality (the biggest remaining slice); the ~2-3% semantic core."
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-30 (grade: EXCELLENT; SOLVED owner-DONE)
> **Verdict:** a model result. Reverified first-hand (`test_coref_residual_focus_and_participant.py` **45/45**,
> scaffold-free — recomputes the landing validation through the real `graded_antecedent_pick`). **(1)** The brief's named
> mechanism (Grosz-Sidner focus STACK) is **REFUTED** with a direct oracle — a perfect-segmentation stack diverges from
> finer token-locality in **1/420** and does not beat it (0.481 vs 0.479, NOT_SEP; twin ties). A rigorous negative = a full
> pass. **(2)** The real fix, found by **reading the misses**: the candidate pool violates hard phi-agreement (the permissive
> `_gn_compat` admits the narrator "I" for "he/she", and objects/places for people). Hardening **person + animacy** exclusion
> lifts the **actual landed resolver 0.786→0.841 (+0.054 CI-sep, n=9139, recall 0.996)**; residual 0.057→0.219. Gender is the
> principled exception (established too late to be causal). **(3)** Generalizes every way tested (the owner's push):
> 1st-person +0.147, 3rd-person +0.006 no-regression, person+neuter, threshold-robust, cross-linguistically universal, and a
> no-gold-NER arm that beats gold (anti-cute-trick). Exemplary honesty (withdraws the focus stack, the gender leak, the
> open residual). **Grade EXCELLENT.** hdlab landing **DONE (additive/opt-in)** — `is_discourse_participant` +
> `phi_agreement_keep` appended to `graded_coref_pick.py` (existing callers byte-unchanged; reader-wiring coupled with the
> assembly). Audit §2b folded; `priority:` cleared. **This closes the standing coref-residual wall's KB/focus theories and
> replaces them with a recall-safe grammar filter.**

# PROBLEM: the reader's coreference resolver fails on the ANTI-TYPICAL residual — the cases where the correct antecedent is NOT the most salient/topical entity (topic-SHIFT cases; on the ~205-case LitBank structurally-dominated residual the gold antecedent's mean recency rank is 1.99, i.e. the resolver grabs the topical/most-frequent entity when it should not, ~0.356 of the time). This residual has now been triangulated by THREE integrated results to be NOT fixable by the levers already tried: the coherence/next-mention PRIOR is REFUTED (six typicality cues all dead/anti-predictive on the anti-typical core — `the_reader_has_no_coherence_next_mention_prior`), a static commonsense KB is DEAD (~2-3%, measured TWICE — the discourse-fact drill `exp_coref_residual_world_knowledge_ceiling_v1` AND the assembly's own residual drill), and a "better interference model" is a TIE (Jager/Engelmann/Vasishth 2017: no interference with a fully-cue-matching antecedent). What remains, and what every drill points to, is DISCOURSE ATTENTIONAL STATE: the correct antecedent is the entity in FOCUS given the discourse's segment/topic structure, which is NOT the same as the most recent or most frequent mention. Build a glass-box Grosz & Sidner (1986) focus-STACK / Kehler-Rohde QUD entity-tracker over the accumulating situation model — a STRUCTURAL, KB-FREE model of which entity is "in focus" as the discourse pushes/pops segments — and validate it resolves the anti-typical residual CI-separated over the salience/recency floor with the info-free twin (shuffled focus transitions) LOSING. This is the assembly's own drill-confirmed #1 next problem and the standing coref-residual wall.

**slug:** `the_coref_residual_needs_a_discourse_focus_stack` — **opened:** 2026-08-30 by the strategy session (the decomposition-seeded #1 follow-on of the integrated ASSEMBLY `wire_the_predarg_frontend_and_binder_into_the_live_reader` — its residual drill measured who-did-what on real prose is ENTIRELY coreference-bound, perfect binding → 1.000, and the residual is discourse-focus / topic-shift bound; TRIANGULATED by the integrated `the_discourse_fact_reasoner_is_unvalidated_on_natural_text` which independently measured a KB dead ~2-3% on the same residual). **status:** OPEN — a MECHANISM + BUILD problem (a new organ over the accumulating situation model). You build + validate in `experiments/`; strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3` — the HIGHEST-value open problem: it is the SOLE remaining lever on the coref residual after three integrated results EXCLUDED the coherence prior, the static KB, and the interference model, and coreference is the measured bottleneck of who-did-what on real literary prose (the assembly proved perfect binding → 1.000; the graded binder recovers only ~12% of the headroom; ~67% remains, ALL coref). A brain-faithful focus tracker is the highest-leverage comprehension lever we have identified. **Dependency web:** operates over the accumulating situation model (the ENTITY track + the `temporal_order_register` segment/order) and re-ranks the existing coref candidate pool (`hdlab/graded_coref_pick`); COMPLEMENTARY to the assembly's graded binder (that handles cue-COMPETITION where the pool is gn-ambiguous; THIS handles topic-SHIFT where the correct antecedent is anti-salient — different sub-populations). ⚠️ **COORDINATE:** the eventual hdlab landing wires into the coref path, which the strategy-owned assembly reader-wiring landing (Changes 2-3) also touches — so BUILD + VALIDATE in `experiments/` (reader-independent); strategy sequences the landings. **Re-rank per the owner.**

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
When you read "she," you usually mean the person the story is currently about — the one in focus. Our reader does that well.
But sometimes the right answer is NOT the obvious, most-talked-about character: the story briefly shifts to someone else, and
"she" points there. Those topic-shift cases are exactly where our reader breaks — it keeps grabbing the main character. We
have now proven, three separate ways, that the fixes we'd normally reach for do NOT work here: a "who usually does this"
prior points the wrong way (by construction these are the atypical cases), a facts/knowledge database resolves almost none
of them (~2-3%), and a better memory-interference model just ties. What every one of those dead ends points to is the same
thing: the answer is whichever character the discourse has put IN FOCUS right now, and focus is a structured thing that
pushes and pops as the story changes topic — not simply "the most recent" or "the most frequent" mention. Build the reader a
proper, inspectable focus tracker (the linguistics calls it a focus stack / centering) and show it gets these topic-shift
pronouns right where a "grab the salient one" reader gets them wrong.

## 2. WHY THIS ONE
It is the SOLE remaining lever on the measured #1 bottleneck of reading comprehension on real prose. The assembly proved
who-did-what on literary prose is ENTIRELY coreference-bound (perfect pronoun binding → 1.000; the parse and name-clustering
are NOT bottlenecks), the graded binder recovers only ~12% of the headroom, and ~67% remains — ALL coreference. Three
integrated results have now EXCLUDED the other candidate levers (coherence prior REFUTED; static KB dead ~2-3% measured
twice; interference model a tie), and all three point to the SAME mechanism: discourse attentional state / focus. This is
not a narrow patch — attentional-state tracking is foundational to reference, discourse coherence, and dramatic structure,
and it is the assembly's own drill-confirmed highest-priority next build.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** discourse comprehension maintains an ATTENTIONAL STATE — a focus of attention over entities
  that is STRUCTURED by the discourse's segment hierarchy and shifts (pushes/pops) as topics open and close (Grosz & Sidner
  1986, *Attention, Intentions, and the Structure of Discourse*). Reference resolution CONSULTS this attentional state, not
  raw recency: the preferred antecedent is the backward-looking center Cb, and transitions have a preference order
  (Continue > Retain > Smooth-Shift > Rough-Shift) that a reader uses to choose among candidates (Centering Theory — Grosz,
  Joshi & Weinstein 1995; Walker/Brennan). The Question-Under-Discussion structures which entity is in focus (Roberts 2012;
  Kehler & Rohde 2016 integrate coherence + QUD). Neurally: the situation model holds a working-memory focus (a small set of
  attended entities, PFC/parietal attentional control; the hippocampal/PCC situation model for the segment structure), and
  anaphora reactivates the attended referent. A topic SHIFT is a segment push/pop that changes which entity is Cb.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the exact STACK representation (push/pop discipline, stack depth), the
  transition-cost / preference weighting, any focus-decay or salience threshold, and how segment boundaries are detected.
  **Copy the COMPUTATION** (an entity is in focus per the discourse segment structure; the preferred antecedent is the
  in-focus Cb, with the Centering transition preference breaking ties; a topic-shift antecedent is chosen when the segment
  structure — not recency — puts a non-salient entity in focus). **SWEEP** the representation, the transition weights, and
  the segment-boundary detector. **REUSE** `hdlab/graded_coref_pick` (re-rank its existing candidate pool by focus-state) +
  the accumulating situation-model ENTITY track + the `temporal_order_register` (segment/order signal).
- **NOT brain-faithful:** a pure recency/frequency salience prior (that IS the current floor and it grabs the wrong entity
  on the residual — the failure mode); a "who typically does this" typicality prior (REFUTED — the residual is anti-typical
  by construction); a static commonsense KB (measured dead ~2-3%); an external LLM.

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE / RE-MEASURE — do not re-derive blindly):** the anti-typical residual population and its
  character — the ~205-case LitBank structurally-dominated residual (gold antecedent mean recency rank 1.99; resolver grabs
  the topical/most-frequent entity ~0.356 of the time); the three EXCLUSIONS — coherence prior REFUTED
  (`the_reader_has_no_coherence_next_mention_prior`, integrated), static KB dead ~2-3% (the discourse-fact drill
  `exp_coref_residual_world_knowledge_ceiling_v1` AND the assembly's residual drill — see the ⚠️ below), interference a tie
  (Jager 2017). `hdlab/graded_coref_pick` (the graded candidate-retrieval scoring core, integrated).
- **⚠️ RE-MEASURE, DO NOT LEAN ON (a strategy VET-flag):** the KB-dead oracle cell
  `exp_coref_residual_world_knowledge_ceiling_v1` is disk-verified but NOT independently VET'd. Your can-fail oracle test
  (bar item 1) must ESTABLISH the residual's ceiling itself (a perfect focus-oracle) — do not cite the un-VET'd ~2-3% as a
  premise; re-derive the KB-dead / focus-oracle numbers on your own instrumented population.
- **INFERRED (to prove):** that a discourse focus-stack (segment-structured, observation over the entity track, re-ranking
  the coref pool by in-focus Cb + Centering transition preference) resolves the anti-typical residual CI-separated over the
  salience/recency floor with the info-free twin LOSING — OR a rigorous reason it doesn't (e.g. segment boundaries are
  unrecoverable from surface text at the needed precision — quantify the boundary-detection ceiling and its effect).

## 5. ALREADY TRIED / DO NOT RE-RUN
- **EXCLUDED levers — do NOT re-propose (each integrated + measured):** the coherence/next-mention PRIOR (six typicality
  cues dead/anti-predictive on the anti-typical core); a static commonsense KB (~2-3% twice); a "better interference model"
  (Jager/Engelmann/Vasishth 2017 — a tie, not a resolver). Do NOT route this to Phase-1 meaning/grounding (the discourse-fact
  drill REFUTED the world-knowledge hypothesis for this residual).
- Do NOT rebuild `graded_coref_pick` (REUSE it — re-rank its pool). Do NOT test on the cue-COMPETITION population the
  assembly's graded binder already owns (gn-ambiguous pools) — THIS problem is the topic-SHIFT / anti-salient residual, a
  DIFFERENT sub-population. Do NOT validate only on constructed pairs — the residual is a REAL LitBank population.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read the assembly SOLVED `wire_the_predarg_frontend_and_binder_into_the_live_reader/SOLVED.md` (Deepening 3 + 4: the
  residual decomposition + the world-knowledge-DEAD drill + the Grosz-Sidner recommendation) and its
  `research_coref_residual_mechanism_on_literary_prose_2026-08-30.md`; `the_discourse_fact_reasoner_is_unvalidated_on_natural_text/SOLVED.md`
  (the KB-dead-on-residual measurement + the "syntactic binder owns the residual" law); `the_reader_has_no_coherence_next_mention_prior/SOLVED.md`
  (the REFUTED typicality cues + the positive control that DOES pass — the mechanism works, the population lacked the cases).
  Read `hdlab/graded_coref_pick.py` + the ENTITY track + `temporal_order_register`. Run `tools/experiment_index.py query
  "coref"` / `"centering"` / `"focus"` / `"salience"` / `"residual"` (SINGLE keywords). Audit: the newest §2b coref +
  discourse-fact entries. **Mind the CORPUS-AGE confound** — the residual is 19c LitBank prose; the focus-stack is STRUCTURAL
  (less confounded than a meaning cue), but any lexical/meaning sub-cue is age-exposed.

## 7. THE BAR
PASSES only with ALL of:
1. **A can-fail ORACLE ceiling FIRST (before building the mechanism):** on the anti-typical residual population, a PERFECT
   focus-oracle (an oracle that knows the in-focus entity per gold segment structure) must clear the residual CI-separated
   over the salience/recency floor — establishing headroom EXISTS for a focus mechanism (if a perfect focus-oracle does NOT
   beat the floor, the mechanism is the wrong lever and that is a rigorous NEGATIVE worth reporting). Re-derive this on your
   OWN instrumented population; do not cite the un-VET'd prior number.
2. **A glass-box discourse FOCUS-STACK** (built in `experiments/`): segment-structured attentional state over the entity
   track; the preferred antecedent = the in-focus Cb with the Centering transition preference breaking ties; re-ranks the
   `graded_coref_pick` candidate pool. Copy the computation; SWEEP the representation + transition weights + segment
   detector. NO external LLM.
3. **Resolves the anti-typical residual CI-separated over the salience/recency floor** — the floor = the current recency/
   frequency-salience resolver (or `graded_coref_pick` as-is) recomputed on the SAME residual population; the **info-free
   twin** (shuffled focus transitions / randomized segment boundaries — so the focus signal is destroyed but the pool is
   unchanged) LOSES CI-separated; report CI half-width + null p95; no number crosses populations. A **POSITIVE control** the
   metric can move (a topic-shift scene where the correct antecedent is anti-salient because the discourse pushed a new
   segment — which the salience floor misses).
4. **Isolates the FOCUS-STRUCTURE contribution** — hold the candidate pool fixed and show the lift is the focus/segment
   structure, not a better mention detector or a recency retune (ablate to a flat-attention re-ranker with the SAME pool).
5. **One-screen summary:** residual population → oracle ceiling → floor → twin → focus-stack lift → incidence/segment-
   boundary-recovery bound on real narrative → verdict. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "a perfect focus-oracle clears the residual CI-sep, but segment boundaries are
recoverable from surface text at only X precision, bounding the buildable lift to Y — positive control confirms the
mechanism, naming boundary detection as the next gap").

## 8. FILES AND ENTRY POINTS
- **Reuse / re-rank (integrated — do not rebuild):** `hdlab/graded_coref_pick.py` (the graded candidate pool); the
  accumulating situation-model ENTITY track; `temporal_order_register` (segment/order). **Motivation + residual population:**
  `wire_the_predarg_frontend_and_binder_into_the_live_reader/SOLVED.md` (Deepening 3-4) +
  `research_coref_residual_mechanism_on_literary_prose_2026-08-30.md`; `the_discourse_fact_reasoner_is_unvalidated_on_natural_text/SOLVED.md`;
  `the_reader_has_no_coherence_next_mention_prior/SOLVED.md`; the drill cells `exp_coref_residual_world_knowledge_ceiling_v1`
  (RE-MEASURE, do not cite). Audit + heavy→REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The excluded levers (coherence prior, static KB, interference model) are DEAD on this residual — do not re-propose them. The
integrated coref organs are the INGREDIENTS, not your result — the deliverable is the FOCUS-STACK mechanism and its
measurement on the anti-typical residual over the salience floor. Establish the oracle ceiling FIRST (re-derived, not cited).
Strategy owns any hdlab landing and sequences it with the assembly reader-wiring.
