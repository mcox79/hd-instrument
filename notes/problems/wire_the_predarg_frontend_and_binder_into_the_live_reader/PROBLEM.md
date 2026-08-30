---
priority:
review: STRONG
review_text: "The ASSEMBLY milestone, POSITIVE. Routing the live reader's role path through a real parse -> the landed event-semantic router (+ a NEW quotative-inversion agent fix) -> the graded binder lifts who-did-what over the POSITIONAL incumbent +0.225/+0.247 CI-sep, reproduced FIRST-HAND through the actual SituationReader.read() class (0.551->0.798); info-free ROLE and BIND twins both lose CI-sep; LitBank who-did-what +0.095 CI-sep; regression 6.5%. Reverified first-hand 10/10 + 6/6 + 2/2. Grade STRONG (not EXCELLENT): the milestone's counting-floor axis is met only with an asterisk -- it beats the word-counting floor decisively on the incumbent's inputs (+0.264) but only marginally on the reader's OWN matched representation (+0.022, CI touches 0), and the measurement discipline says the matched store is the fair floor -- so the reader went from LOSING to counting (prior attempt) to TYING/edging it, while decisively beating its prior self. Exemplary honesty (flags PARTIAL-if-literal-bar, withdraws unestablished claims, corrected its own world-knowledge hypothesis via a drill). hdlab 3-part diff landed by strategy (Q111)."
---

> ## ✅ SOLVER REVIEW — STRONG (integrated 2026-08-29 by the strategy session; owner_verdict: DONE)
> **The near-term ASSEMBLY milestone, and it is a genuine POSITIVE** — the first time the validated role/binder organs
> beat the live reader end-to-end on the exact real-narrative instrument a prior generic "wire everything" attempt LOST on.
>
> **Reverified FIRST-HAND (recomputed fresh, not cached):** `test_wire_predarg_binder_live_reader.py` **10/10**;
> `test_wire_predarg_binder_litbank_whodidwhat.py` **6/6**; `test_wire_predarg_binder_live_reader_integration.py` **2/2**
> (byte-identical OFF; quotative fixed live; RECIPIENT emitted; role lift **0.551->0.798 +0.247 CI-sep THROUGH the live
> `SituationReader.read()` class**). Numbers reproduce the SOLVED (bootstrap variation only).
>
> **What carries the grade (the load-bearing result):** the wired role path beats the POSITIONAL incumbent **+0.225
> [+0.150,+0.303] CI-sep** (family) / +0.219 (exact grain), and the magnitude **originates in the live reader class**
> (+0.247). The dominant lever is a REAL fidelity bug the solver found in the LANDED `predicate_argument_frontend`
> router: it computes the COMM verb class but only for recipients, so on "said Fred" it brands the postverbal speaker
> the object — quotative inversion is worth **+0.253 CI-sep** by itself and is PINNED-in-principle (FrameNet
> Statement / VerbNet say-37.7 / eADM animacy). Info-free ROLE twin loses +0.292; info-free BIND twin loses; a 2nd
> binding-sensitive metric confirms +0.171; HYBRID good-enough fallback (Ferreira dual-route) halves regression to 6.5%.
> On LitBank the graded binder lifts who-did-what +0.095 CI-sep and the real arc parse TIES gold (-0.005) —
> who-did-what is ENTIRELY coreference-bound (perfect-binding oracle -> 1.000, non-binding residual -> 0.000).
>
> **Why STRONG, not EXCELLENT (the honest asterisk, surfaced to the owner):** the milestone's "beat a word-counting
> baseline CI-separated" axis is met only partially. vs the content-lemma counting floor the wired reader wins **+0.264
> CI-sep on the incumbent's (positional) inputs**, but only **+0.022 (CI touches 0, NOT CI-sep) on the reader's OWN
> matched representation**, and loses to the oracle-input 0.983 — which the prior attempt itself established is
> non-discriminating (ties everything on clean inputs, collapses to 0.253 on paraphrase), so per the measurement
> discipline (recompute the floor on the item's OWN representation) the fair floor is the matched store. Net: the reader
> went from LOSING to counting (prior attempt) to TYING/edging it, while decisively beating its prior self — real
> progress on the milestone, but not yet the clean CI-separated word-counting win. The solver flags all of this and
> offers "PARTIAL if the literal bar demands 0.983" — exemplary honesty.
>
> **Convergences that strengthen it:** (1) a coref-residual drill REFUTED the solver's own world-knowledge hypothesis
> (a commonsense KB resolves ~2-3% of the residual) — the residual is discourse-focus / topic-shift bound (Grosz-Sidner
> focus stack), converging with the standing fact that the anti-typical residual is NOT a KB/coherence-prior gap. (2) the
> archaic-prose parse TIES gold on who-did-what — converging with the already-integrated parse-confound retirement.
>
> **hdlab landing (Q111, strategy):** the 3-part additive/default-byte-identical diff — (1) quotative-inversion agent
> handling in `predicate_argument_frontend`, (2) a `role_route in {positional,predarg,hybrid}` option on
> `situation_reader` fed by a persisted parse frontend, (3) the graded binder for pronoun resolution. AUDIT UPDATE folded
> (§2b). NEXT PROBLEM seeded: a glass-box Grosz-Sidner focus-STACK / QUD entity-tracker for the coref residual.

# PROBLEM: the live reader (`hdlab/situation_reader.py`) assigns who-did-what POSITIONALLY — agent = the sentence's subject-mention, patient = the nearest post-predicate nominal (`_assign_roles`/`_pick_role_mentions`) — with NO dependency parse, so it produces only agent/patient and CANNOT use the validated organs that already beat that: the landed `hdlab/predicate_argument_frontend.route_predicate_arguments` (the event-semantic router: goal/location/path/source/recipient the positional rule scores 0.000 on, +five roles CI-separated on FrameNet gold) and the who-did-what graded binder (graded Centering cue-competition + gender agreement + person-exclusion, +0.083 live / +0.136 re-instrumented CI-sep). They are ISLANDED. ASSEMBLE them into the live reader — supply the parse (dependency heads) the front-end needs from an existing parser (`hdlab/arc_parser` / `candidate_generator`, the same heads source the front-end was validated on), route `situation_reader`'s role assignment through the front-end + binder, and MEASURE the end-to-end who-did-what / role lift over BOTH the current positional reader AND the strong content-word-COUNTING floor a prior wiring attempt found beats a naive wired reader — with no-regression on the cases the positional reader already gets right. You build + validate in `experiments/` and propose the hdlab diff; strategy does the final `hdlab/` write (Q111). NO external LLM at inference (the invariant).

**slug:** `wire_the_predarg_frontend_and_binder_into_the_live_reader` — **opened:** 2026-08-29 by the strategy session (the
ASSEMBLY-PHASE unblocker: the integrated `no_shared_shallow_predicate_argument_front_end` (p7) + `pronoun_to_event_binding_caps_who_did_what` (p3) each landed a validated role organ that the LIVE reader does not use; a design-gate audit found `situation_reader` is POSITIONAL with no parse). **status:** OPEN — a WIRING + MEASUREMENT problem. You compose the LANDED organs in `experiments/` + measure end-to-end + propose the hdlab diff; strategy lands it (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3` — the HIGHEST-leverage move: the substrate has
> accumulated validated role/space/time organs that the LIVE reader ignores (wire-don't-island debt), and this is the
> assembly step that converts "organs that work in the lab" into "a reader that measurably comprehends." It also unblocks
> the hardest cases (a real parse feeding the live reader). **This IS a solver problem** despite touching the reader: you
> build + validate the wiring in `experiments/` and propose the diff (the standard flow); strategy does the mechanical
> `hdlab/` write. **Dependency web:** consumes a parse (the parse-QUALITY improvement is the sibling `role_assignment_is_untested_on_archaic_literary_prose`, p8 — use whatever parse exists now and measure; a better parse compounds later); composes `predicate_argument_frontend`, the graded binder, `graded_coref_pick`. **COORDINATE:** the predarg de-dup and the who-did-what binder both rewrite `situation_reader`'s role path — do them as ONE pass. **Re-rank per the owner.**

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
We have built and validated several "reading skills" — one that works out the full role of every phrase (who acted, what
moved, the destination, the location, the route, the source, the recipient), and one that binds "she did X" to the right
character better than the reader's current rule. But the live reader doesn't use them: it still figures out who-did-what by
crude position (the subject noun is the doer, the next noun is the done-to) and it has no grammatical parse of the sentence
at all. So the validated skills sit on the shelf. This problem is the ASSEMBLY step: give the live reader a parse, plug in
the validated skills, and MEASURE whether the reader's end-to-end understanding actually improves — honestly, against both
its current rule AND a dumb word-counting baseline that a previous attempt found is surprisingly hard to beat.

## 2. WHY THIS ONE
It is the assembly-phase unblocker: the substrate keeps accumulating validated organs the live reader ignores, so the
gap between "the parts work" and "the reader is good" widens every cycle. Closing it is what turns the library into a
functioning reader, and it directly unblocks the hardest cases (which need a real parse on the live path). A prior generic
wiring attempt (`wire_the_validated_organs_into_the_live_reader_and_measure_end_to_end`) returned a RIGOROUS NEGATIVE — the
end-to-end who-did-what was beaten by a content-lemma-overlap COUNTING floor (role ~0.98 on its population) — so this is
NOT a foregone win: the specific lesson is that the wired reader must beat that counting floor, not just its own positional rule.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** comprehension is INCREMENTAL role binding over a parse — the brain assigns thematic roles
  from argument structure (a parse), not from raw linear position (Competition Model; MacDonald constraint-satisfaction;
  the parse feeds the situation model's (entity, role, event) binding — Kintsch CI; Zwaan-Radvansky). Linear-position role
  assignment is a degenerate fallback the brain uses only when structure is unavailable (good-enough processing).
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the exact PARSE SOURCE (which existing parser supplies heads) and the
  fallback policy when the parse is unreliable. **Copy the COMPUTATION** (route roles through argument structure via the
  landed `predicate_argument_frontend` + bind who-did-what via the landed graded binder); SWEEP the parse source + the
  abstain/fallback threshold. Reuse the LANDED organs (`hdlab/predicate_argument_frontend`, the graded binder,
  `graded_coref_pick`, `hdlab/arc_parser`) — do NOT re-derive them.
- **NOT brain-faithful:** the current POSITIONAL role assignment (`_assign_roles` — linear, parse-free, agent/patient only);
  a wiring that regresses the cases the positional reader already handles; an external LLM parse (the invariant).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** the landed `predicate_argument_frontend` recovers five roles the
  positional/inline rule scores 0.000 on (FrameNet FE gold, CI-sep, twin below each); the graded who-did-what binder lifts
  live who-did-what +0.083 / +0.136 CI-sep (random twin loses, 3-split robust); `situation_reader._assign_roles` is
  positional with no heads (design-gate audit). The prior generic wiring found a content-lemma COUNTING floor beats a naive
  wired reader end-to-end (role ~0.98 on its population) — the floor to beat.
- **INFERRED (to prove):** that routing the live reader's role assignment through the parse + the front-end + the binder
  lifts end-to-end who-did-what / role accuracy CI-separated over BOTH (a) the current positional reader AND (b) the
  content-word-counting floor, on real narrative, with the info-free twin losing and NO regression on the positional
  reader's already-correct cases — OR a rigorous, well-attributed reason it cannot (e.g. the parse quality on archaic prose
  caps it — quantified, handing the cap to p8 — with the mechanism proven on the modern-parseable subset).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-derive the role organs (the `predicate_argument_frontend`, the graded binder, `graded_coref_pick` are LANDED +
  witnessed — compose them). Do NOT re-run the generic "wire everything and measure" (it returned the counting-floor
  negative — inherit that floor as a REQUIRED control). Do NOT build a new parser from scratch (use an existing one; the
  parse-quality fix is the sibling p8). Do NOT write `hdlab/` (propose the diff; strategy lands it, Q111).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/situation_reader.py` (`_assign_roles`/`_pick_role_mentions`/`_assign_frame_primary_roles` — the positional
  path + its default-OFF gates), `hdlab/predicate_argument_frontend.py` (`route_predicate_arguments` — needs tokens, upos,
  heads, verb_idx) + its witness, the graded who-did-what binder (`pronoun_to_event_binding_caps_who_did_what/SOLVED.md`,
  `exp_coref_graded_binder_serves_whodidwhat_v1.py`), `hdlab/arc_parser.py` / the candidate_generator (a heads source), and
  the prior negative `wire_the_validated_organs_into_the_live_reader_and_measure_end_to_end/SOLVED.md` (the COUNTING floor).
  Run `tools/experiment_index.py query "whodidwhat"` / `"positional"` / `"parse"`. Audit: the newest §2b predarg + who-did-what
  entries. **Mind the CORPUS-AGE confound** (the parse degrades on archaic prose — quantify, don't blame the wiring for it).

## 7. THE BAR
PASSES only with ALL of:
1. **The live reader's role assignment routed through a parse → `predicate_argument_frontend` → the graded who-did-what
   binder** (built + measured in `experiments/`, composing the LANDED organs; a proposed `hdlab/situation_reader` diff, NOT
   an `hdlab/` write). Supply heads from an existing parser; SWEEP the parse source + abstain threshold. NO external LLM.
2. **Lifts end-to-end who-did-what / role accuracy CI-separated over BOTH floors on real narrative** — (a) the current
   POSITIONAL reader recomputed on the same population, AND (b) the content-lemma-overlap COUNTING floor from the prior
   attempt. The **info-free twin** (shuffled heads / random binding) LOSES CI-separated; report CI half-width + null p95; no
   number crosses populations.
3. **NO REGRESSION:** on the cases the positional reader already gets right, the wired reader must be byte-or-CI-equal (the
   wiring adds roles + fixes bindings, it must not break what worked). Report the regression count explicitly.
4. **One-screen summary:** parse source → floors (positional + counting) → twin → end-to-end lift → regression count →
   verdict, + the proposed `hdlab/situation_reader` diff. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "the wired reader beats the positional rule but the counting floor still wins
because the parse on archaic prose is too degraded — quantified at UAS X, handing the cap to p8 — with the mechanism proven
CI-sep on the modern-parseable subset").

## 8. FILES AND ENTRY POINTS
- **Compose (LANDED — do not rewrite):** `hdlab/predicate_argument_frontend.py`, the graded who-did-what binder
  (`experiments/exp_coref_graded_binder_serves_whodidwhat_v1.py`), `hdlab/graded_coref_pick.py`, `hdlab/arc_parser.py` /
  candidate_generator (heads). **Wire into (propose diff):** `hdlab/situation_reader.py` (`_assign_roles` / the role path).
- **Inherit the floor:** `wire_the_validated_organs_into_the_live_reader_and_measure_end_to_end/SOLVED.md` (the counting
  floor). Audit + heavy→REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The role organs' isolated wins (FrameNet five-role, +0.083/+0.136 who-did-what) are the MOTIVATION, not your result — the
deliverable is the END-TO-END lift on the LIVE reader over BOTH floors, with no regression. Do NOT re-derive the organs,
re-run the generic wiring, or write `hdlab/`. Strategy does the final `hdlab/` write from your proposed diff.
