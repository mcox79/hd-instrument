---
priority:
review: STRONG
review_text: "SOLVED (owner-DONE) integrated 2026-08-29 — bar MET, with exemplary drilling that CORRECTED the brief's own premise. Reverified FIRST-HAND: test_coref_graded_binder_serves_whodidwhat.py 13/13 PASS. A brain-faithful clause-level graded pronoun→event binder (graded Centering cue-competition via hdlab.graded_competition + gender agreement + person-feature exclusion) LIFTS live who-did-what CI-separated over the ACT-R incumbent: LIVE 0.143→0.226 (+0.083 CI-sep [hw 0.026]); re-instrumented event-set metric 0.249→0.385 (+0.136 CI-sep [hw 0.043]); the info-free random-binding twin LOSES in all 3 DEV/TEST splits; positive control moves; register isolated (direct decode, fixed clustering). TWO drilling findings reshape the causal story, both PROVEN: (1) the 0.589 perfect-binding ceiling was a METRIC ARTIFACT (the live readout scored most-common-verb-per-sentence, discarding multi-event clauses) — re-instrumenting as a situation-model EVENT-SET recall lifts the ceiling to 1.000 (the single highest-leverage change); (2) the residual is DISCOURSE-SPECIFIC-MEMORY-bound — a within-document entity-event oracle recovers it where generic typicality is DEAD (66% cov, beats twin +0.138), while a coherence/selectional prior is measured dead (0.029, loses to twin) — so the wall is a missing build (the phase-1 situation model) with a PROVEN mechanism, not a capability ceiling. HONEST BOUNDS (owner-flagged, I concur): the absolute lift is MODEST (~18% of the +0.44 headroom — who-did-what is NOT pushed to ceiling); the brief's SPECIFIC Cb/clause_role attribution does NOT hold (clause_role-shuffle twin beaten only 1/3; on CLEAN teacher-forced binding ACT-R base-level activation is ALREADY the optimal structural binder, +0.0 for geometry cues) — the OVERALL binder (graded cues + agreement + person-exclusion) is the win, not the named cue. Grade STRONG (bar met, brain-mechanism-drilled, self-corrected the premise; not EXCELLENT because the lift is modest and the brief's central hypothesis was refuted — the solver's honesty about that is a strength). hdlab landing: the earned STEP-1 (re-instrument the live who-did-what metric as event-set recall — the biggest lever) + STEP-2 (wire the graded binder + agreement + person-exclusion onto the live path, replacing inline ACT-R + the worse strict-Cb organ) are COUPLED live-path/measured-no-regression work → QUEUED as a careful follow-on (person-exclusion core already landed in graded_coref_pick). AUDIT §2b folded: the who-did-what cap is a HYBRID (metric-artifact decode ceiling + a small candidate-set/binder lever + a discourse-specific-memory residual), NOT a missing structural Cb binder; pronoun→event binding is FOCUS-DRIVEN. STEP-3 (wire the situation model into who-did-what) is the successor — packaged/flagged separately."
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-29 (grade: STRONG; SOLVED owner-DONE)
> **Verdict:** bar MET, with exemplary drilling that CORRECTED the brief's own premise. Reverified first-hand
> (`test_coref_graded_binder_serves_whodidwhat.py` **13/13 PASS**). A brain-faithful clause-level graded pronoun→event
> binder (graded Centering cue-competition via `hdlab.graded_competition` + gender agreement + person-feature exclusion)
> lifts live who-did-what CI-separated over the ACT-R incumbent — **LIVE 0.143→0.226 (+0.083)**; re-instrumented event-set
> metric **0.249→0.385 (+0.136)**; info-free random twin loses in all 3 splits; positive control moves; register isolated.
> **Two proven drilling findings reshape the causal story:** (1) the 0.589 "perfect-binding ceiling" was a **METRIC
> ARTIFACT** (the readout scored most-common-verb-per-sentence, discarding multi-event clauses) → re-instrumenting as a
> situation-model EVENT-SET recall lifts the ceiling to **1.000** (the single highest-leverage change); (2) the residual is
> **discourse-specific-memory-bound** — a within-document entity-event oracle recovers it where generic typicality is DEAD
> (66% cov, beats twin +0.138), coherence/selectional priors measured dead (0.029) → the wall is a missing build with a
> proven mechanism, not a capability ceiling.
> **Honest bounds (I concur):** the absolute lift is MODEST (~18% of the +0.44 headroom); the brief's SPECIFIC Cb/clause_role
> attribution does **NOT** hold (clause_role-shuffle twin beaten only 1/3; on clean teacher-forced binding ACT-R is already
> the optimal *structural* binder) — the OVERALL binder is the win, not the named cue. The solver's honesty about its own
> brief's refuted hypothesis is a strength.
> **Grade STRONG** (bar met, brain-mechanism-drilled, self-corrected; not EXCELLENT because the lift is modest and the
> central hypothesis was refuted).
> **Landing (Q111):** the earned STEP-1 (re-instrument the live who-did-what metric as event-set recall — the biggest
> lever) + STEP-2 (wire the graded binder + agreement + person-exclusion onto the live path, replacing inline ACT-R + the
> worse strict-Cb organ) are COUPLED live-path / measured-no-regression work → **QUEUED** as a careful follow-on (the
> person-exclusion core is already landed in `graded_coref_pick`). **Audit** §2b folded: the who-did-what cap is a HYBRID
> (metric-artifact decode ceiling + a small binder lever + a discourse-specific-memory residual), pronoun→event binding is
> FOCUS-DRIVEN. **STEP-3** (wire the built-but-unwired situation model — `decode_set` + `CausalLinkRegister` — into
> who-did-what) is the successor problem, packaged separately.

# PROBLEM: the reader resolves a pronoun to its ANTECEDENT (which entity — the integrated graded coref) but does NOT bind the resolved entity to the CLAUSE's EVENT/action, and THIS — proven by decomposition, not asserted — is the dominant cap on who-did-what: perfect pronoun→event binding on the SAME clustering recovers the WHOLE who-did-what gap (0.161 → 0.606, +0.444 CI-separated), while better name clustering adds +0.000. Build a clause-level GRADED pronoun→event binder that wires the tracked-but-UNUSED clause_role / Centering-Cb topicality into the graded scorer, and lift who-did-what CI-separated over the live path toward that ceiling with the info-free twin losing

**slug:** `pronoun_to_event_binding_caps_who_did_what` — **opened:** 2026-08-28 by the strategy session (the DOMINANT lever
DECISIVELY PROVEN by the integrated `the_name_branch_shatters_one_character_into_many_entities`, owner-DONE/EXCELLENT — a
rigorous negative whose decomposition showed pronoun→event binding, NOT name clustering, is the who-did-what cap).
**status:** OPEN — a MECHANISM + WIRING problem. You build + validate in `experiments/`; strategy lands any hdlab change
(Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3` — the HIGHEST-leverage open build: the +0.444
> who-did-what lever is MEASURED and reproducible (three separate problems have now surfaced `clause_role`/Centering-Cb as
> TRACKED-BUT-UNUSED). Who-did-what is the core reading capability the whole stack feeds (entity tracking, the situation
> model, ToM). This is the successor a rigorous refutation identified, not a hunch. **Re-rank per the owner.**

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
"Elizabeth entered. **She** picked up the letter." To answer "who picked up the letter?" the reader must do TWO things:
(1) resolve "She" → Elizabeth (which entity — the integrated graded coref does this well), AND (2) bind that resolved
entity to the CLAUSE's action (picked-up) — the who-did-WHAT step. The reader does the first but not the second well: the
name-clustering integration PROVED, by decomposition, that this second step is the dominant cap. On the who-did-what task
the live reader scores 0.161; giving it PERFECT pronoun→event binding on the SAME entity clustering jumps it to 0.606
(**+0.444, CI-separated**) — and given perfect binding, better name clustering adds **+0.000**. So the whole gap is the
pronoun→event binding, not the entity representation. And the fix is on disk waiting: the substrate TRACKS each clause's
grammatical role and a Centering backward-looking-center (Cb) topicality signal, but the graded who-did-what scorer does
NOT USE them (this is the THIRD separate problem to flag `clause_role`/Cb as tracked-but-unused). The task: build a
clause-level GRADED pronoun→event binder that wires those tracked signals into the scorer, and lift who-did-what
CI-separated over the live 0.161 toward the 0.606 perfect-binding ceiling, with the info-free twin losing.

## 2. WHY THIS ONE
It is the MEASURED dominant lever on who-did-what — the core reading capability the whole stack feeds (entity tracking,
the situation model, the ToM observation cue, "where is X"). +0.444 of proven headroom sits behind ONE mechanism, and
its inputs are already tracked but unused. A rigorous refutation (name clustering) cleared the alternatives and pointed
exactly here; this is where the who-did-what points actually are.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** binding a referent to an event/action is the situation model's core operation (the
  (entity, role, event) binding; Kintsch construction-integration; Zwaan event-indexing). The brain resolves WHO the
  clause is about with **Centering** — the backward-looking center **Cb** (the most salient entity carried forward), and
  grammatical prominence (subjecthood) — as GRADED, incremental cue-based salience (Gordon/Grosz/Joshi Centering Theory;
  Lewis & Vasishth 2005 cue-based retrieval; the reader's own `graded_competition` currency). A pronoun preferentially
  binds to the Cb, and the clause's event binds to that entity.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the exact graded scorer over the tracked cues (Cb topicality,
  clause_role/subjecthood, recency) and the binding threshold. Copy the COMPUTATION (graded cue-based clause-level
  entity→event binding using Cb); SWEEP the cue weights + threshold. Reuse the tracked `clause_role`/Cb + the substrate's
  `graded_competition`, not a hand-rolled rule.
- **NOT brain-faithful:** the current path that IGNORES the tracked clause_role/Cb (leaving the who-did-what binding to a
  weaker cue), or a fixed most-recent-subject rule (the same rigidity the coref integration already showed loses to a
  graded read). No external coref/LLM at inference (the invariant).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** the name-clustering decomposition
  (`the_name_branch_shatters_one_character_into_many_entities`, `exp_name_clustering_serves_whodidwhat_v1.py`): live
  who-did-what 0.161; HEAD_OPB (head clustering + PERFECT pronoun→event binding) 0.606, **+0.444 CI-sep**; ORGAN_OPB ≈
  HEAD_OPB +0.000 (name clustering irrelevant given perfect binding); a register FAN effect is present (unifying aliases
  can HURT — see the multibank line). `clause_role`/Centering-Cb are TRACKED but UNUSED by the graded scorer (flagged 3×).
- **INFERRED (to prove):** that a clause-level graded pronoun→event binder using the tracked Cb/clause_role lifts the
  LIVE who-did-what CI-separated over 0.161 toward the 0.606 ceiling — or a rigorous reason the remaining gap to 0.606 is
  the eval-harness multi-verb-per-clause ambiguity (a definition limit the decomposition already named), not a missing
  mechanism.

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-solve name clustering (a rigorous negative: it is NOT the lever) or the pronoun→ANTECEDENT link (the
  integrated graded coref already does which-entity well). Do NOT rebuild the FHRR binding operator. REUSE the tracked
  `clause_role`/Cb + `graded_competition`; the PERFECT-binding arm (HEAD_OPB) is the oracle ceiling, not your result —
  build the REAL graded binder toward it. Mind the register FAN effect (the multibank line) — do not conflate binding
  quality with register capacity.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `the_name_branch_shatters_one_character_into_many_entities/SOLVED.md` (the decomposition + the HEAD_OPB oracle) and
  `experiments/exp_name_clustering_serves_whodidwhat_v1.py` (the who-did-what harness + arms). Read
  `hdlab/coreference_resolver.py` (where `clause_role`/Cb are tracked) and `hdlab/graded_competition.py` (the scorer).
  `tools/experiment_index.py query "who did what"` / `"centering"` / `"clause_role"` / `"pronoun"`. Audit: the newest §2b
  name-clustering entry + the coref entry. **Mind the CORPUS-AGE confound** (LitBank is older literary prose — the
  archaic-prose parse-quality concern, sibling brief `role_assignment_is_untested_on_archaic_literary_prose`, may degrade
  the subjecthood cue).

## 7. THE BAR
PASSES only with ALL of:
1. **A clause-level GRADED pronoun→event binder** (built in `experiments/`) that consumes the tracked `clause_role`/
   Centering-Cb topicality via `graded_competition`. Copy the computation; SWEEP the cue weights + threshold.
2. **Lifts the LIVE who-did-what CI-separated over the current path** (0.161, recomputed on the same population) toward
   the perfect-binding ceiling (0.606); the **info-free twin** (shuffled Cb / random binding order) LOSES CI-separated;
   report CI half-width + null p95; no number crosses populations. A **POSITIVE control** the metric can move (a
   Cb-decisive clause the binder gets and the current path cannot).
3. **Isolates BINDING from register capacity** (the fan effect): hold the clustering + store fixed so the measured lift
   is the binder, not the store (the decomposition's HEAD arm is the control).
4. **One-screen summary:** cues wired → floor → twin → who-did-what lift vs the 0.606 ceiling → verdict. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "a faithful graded Cb binder lifts who-did-what to X < 0.606 and the residual to
the ceiling is the harness's multi-verb-per-clause ambiguity, not a missing mechanism" — with the positive control
confirming the metric can move — closes how much of the +0.444 is recoverable by a real binder).

## 8. FILES AND ENTRY POINTS
- Decomposition + harness: `experiments/exp_name_clustering_serves_whodidwhat_v1.py`; the name-clustering SOLVED. Wire
  from: `hdlab/coreference_resolver.py` (clause_role/Cb tracking), `hdlab/graded_competition.py` (the scorer);
  compose-with: `hdlab/situation_model_accumulate.py` (the (entity,role,event) register). Audit +
  heavy→REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The +0.444 HEAD_OPB oracle is the MOTIVATING ceiling (from the name-clustering integration), not your result — build the
REAL graded binder toward it and recompute the live floor on your population. Do NOT re-solve name clustering or the
pronoun-antecedent link. Strategy owns any hdlab landing — you propose the binder, you do not write `hdlab/`.
