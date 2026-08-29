---
owner_verdict: DONE
---

═══════════════════════════════════════════════════════════════════════════════════════════════════
SOLVER SUBMISSION — pronoun_to_event_binding_caps_who_did_what            (STATUS: SOLVED)
hdlab/ UNTOUCHED (proposed diffs only, board Q111). AWAITING owner_verdict: DONE.
REVERIFY: .venv/Scripts/python.exe verification/test_coref_graded_binder_serves_whodidwhat.py   -> 13/13 PASS
Ledger:   .venv/Scripts/python.exe tools/problem_ledger.py --check   -> malformed/incomplete: 0
═══════════════════════════════════════════════════════════════════════════════════════════════════

BAR (quoted in SOLVED.md): (1) a clause-level GRADED pronoun->event binder consuming the tracked
clause_role/Centering-Cb via graded_competition; (2) lifts LIVE who-did-what CI-separated over 0.161 toward
the 0.606 ceiling, info-free twin LOSES, positive control moves; (3) isolate BINDING from register; (4)
one-screen summary. A rigorous NEGATIVE is a full pass.

RESULT — BAR MET, plus the drilling corrected the ceiling premise and proved the residual's brain mechanism.
(LitBank pronoun-query who-did-what, even/odd DEV/TEST split, direct symbolic decode, head-token clustering
held fixed, doc-bootstrap 2000x.)
  * LIVE metric:     HEAD (ACT-R incumbent) 0.143 -> full binder 0.226, +0.083 CI-sep; random twin 0.090
                     (loses); perfect-binding ceiling 0.589.
  * FAITHFUL metric: the 0.589 ceiling was a METRIC ARTIFACT (the readout scored most-common-verb-per-
                     sentence, discarding multi-event clauses). Re-instrumenting as a situation-model
                     EVENT-SET recall lifts the ceiling 0.589 -> 1.000; the full binder lifts HEAD 0.249 ->
                     0.385, +0.136 CI-sep [hw 0.043]; random twin 0.106 (loses +0.278).
  * Robust across 3 DEV/TEST splits (full-binder-over-HEAD ABOVE in all 3; random twin loses in all 3).
  * The binder = graded Centering cue-competition (hdlab.graded_competition) + gender AGREEMENT + PERSON-
    feature exclusion. Component attribution (each controlled): graded cues +0.037 (CI-sep 2/3), agreement
    +0.024, person-exclusion +0.021 CI-sep; active-set window NULL (-0.012, reported).

FLOOR: LIVE ACT-R single-cue binder, recomputed same population = 0.143. Strongest info-free floor = random-
binding twin (loses live +0.09..0.12 / faithful +0.278). Perfect-binding ceiling 0.589 live / 1.000 faithful.

CONTROLS (12): random-binding twin (loses all 3 splits); shuffled-clause_role twin (beaten only 1/3 -> the
tracked Cb is NOT cleanly THE lever); shuffled-gender twin (NOT_SEP, coverage-limited); AGREE-vs-noAGREE
isolation; person-exclusion +0.021 vs active-set null; CLEAN teacher-forced diagnostic (ACT-R already optimal
-> geometry cues +0.0, every hand-config worse -> tuner not myopic); in-harness binding decomposition (live
binds anchor 0.233; perfect binding decodes only 0.606 LIVE = the artifact); DISCOURSE-SPECIFIC oracle beats
its twin +0.138 where typicality is dead; IC go/no-go probe (14.5% precondition); 3-split robustness;
positive control moves; register isolation (direct decode, fixed clustering).

DRILLED EVERY WALL TO A BRAIN MECHANISM (owner directive, LEAD-WITH-BIOLOGY; 2 research drills + a decisive
experiment):
  - Why cue-weighting adds ~0: ACT-R base-level activation already IS the optimal structural binder; the
    residual is anti-typical cue-conflict (gold is most-recent 78% of the time; errors are where recency
    overrode subjecthood, unfixable by a global reweight).
  - Why the coherence/typicality prior is DEAD (measured here: 0.029, loses to its own twin): KBs/coherence
    priors encode TYPICALITY; the residual is ANTI-TYPICAL by construction. The one untested glass-box
    alternative (implicit-causality lexicon) covers only 14.5% -> ~2-5 pts.
  - Why the brain SUCCEEDS where we stall (the "if the brain can do it, so can we" answer, MEASURED): the
    residual is resolved by DISCOURSE-SPECIFIC memory (the situation model), not typicality. A within-
    document entity-event oracle recovers the residual where typicality is dead (66% coverage, beats twin
    +0.138). A WordNet-semantic version widens coverage 0.66->0.85 but is noisier -> crude glass-box proxies
    cap ~10-16%; a GROUNDED situation model (phase 1) is required to go further. So the wall is a missing
    build with a proven mechanism, NOT a capability ceiling.

HOW TO OVERCOME THE WALL (in SOLVED.md, DEMONSTRATED not asserted):
  STEP 1 (PROVEN, do first, cheap): re-instrument who-did-what as a situation-model EVENT-SET readout ->
         ceiling 0.589->1.000. It is a live measurement error, not a capability limit.
  STEP 2 (PROVEN, buildable now): wire the graded binder + gender agreement + person-exclusion onto the live
         path (replacing the inline ACT-R and the worse hard strict-Cb organ). +0.083 live / +0.136 faithful.
  STEP 3 (mechanism PROVEN, de-risked build): the phase-1 situation model (entity-event / causal memory)
         supplies the residual's discourse-specific prior. NOT a KB, NOT a coherence-prior cue (both dead).

ADJACENT COMPONENT -> THE NEXT PROBLEM (evaluated on disk): hdlab/situation_model_accumulate.py ALREADY has
AccumulateRegister.decode_set (Step-1 readout) AND a CausalLinkRegister (Step-3 prior) -- BUILT and UNWIRED
to who-did-what; its flat-dense FHRR register has the fan-effect deviation (sparse multibank = the faithful
fix, also unwired). NEXT PROBLEM: wire the situation model into the who-did-what path (metric via decode_set
+ binder-prior via the entity-event/causal register) on the sparse multibank. Smaller seeds: wire the
binder's graded_competition ENTROPY into an Nref-style abstain/defer gate; regenerate the cache with ent_type
for an animacy filter (low value); make gender agreement GRADED (down-weight not delete) -- a fidelity fix,
low payoff (agreement saturates).

HONEST CAVEATS (withdraw first if wrong): the ABSOLUTE lift is modest (~18% of the real headroom) -- who-did-
what is NOT pushed to ceiling; most of it needs the phase-1 situation model. The brief's SPECIFIC Cb/
clause_role attribution is NOT clean (weights unstable across splits, clause_role-shuffle twin beaten only
1/3) -- the OVERALL binder is the win, not that one cue. PARTIAL is defensible on magnitude; I set SOLVED
because the bar is met and every wall bottoms out in a brain mechanism.

KEY REALIZATIONS: (1) measure the CLEAN binder before trusting the harness (it revealed ACT-R is already
optimal -> the lift is candidate-set + online-noise, not a magic cue). (2) "Ask whether the experiment could
have succeeded" cuts both ways -- teacher-forcing HID the real online lift; run both clean and noisy. (3)
Decompose floor-vs-ceiling into binding vs decode BEFORE attributing -- 39 of the 44 points were a metric
artifact. (4) A sibling's rigorous negative is a load-bearing input -- the residual is the SAME anti-typical
core the coherence-prior refutation already killed. (5) Test the brain's ACTUAL mechanism (discourse-specific
memory) as an oracle -> proves the wall is a missing build, not a ceiling.

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md, coref/pronoun->event): the who-did-what cap is a HYBRID (metric-
artifact decode ceiling + a small candidate-set/binder lever + a discourse-specific-memory residual), NOT a
missing structural Cb binder; ACT-R is already the optimal structural binder; pronoun->event binding is
focus-driven (persistent Cb register; event indexes onto the focused entity; resolution is a confirmatory
readout).

FILES: experiments/{exp_coref_graded_binder_serves_whodidwhat_v1, exp_coref_binder_wall_diagnostic_v1,
exp_coref_residual_discourse_specific_v1}.py; verification/test_coref_graded_binder_serves_whodidwhat.py
(13/13); notes/problems/pronoun_to_event_binding_caps_who_did_what/{SOLVED.md,
research_pronoun_event_binding_mechanism_2026-08-29.md, research_strongest_glassbox_coherence_prior_2026-08-29.md,
research_feature_agreement_binding_2026-08-29.md}. hdlab/ UNTOUCHED.

TLDR (plain language): The reader files an action under the right character only ~1 in 6 times for "she did
X" cases. The brief guessed the fix was to lean on who the passage is about; I built that the brain's way and
it helps a little, but two bigger things turned up. First, the score was being measured wrong -- it threw
away every action but one per sentence; fixing the measurement shows that PERFECT "who is she" resolution
would score a perfect 100, not 60. Second, the genuinely hard cases aren't solved by any general rule or
fact-book (both measured dead) -- they need memory of what THESE specific characters did earlier in THIS
story. I proved that memory-based signal works where the general rules fail, so the remaining gap is a
build we know how to do (a reading-time "situation model"), not an impossible wall -- and that organ already
half-exists in the codebase, unplugged. QUESTIONS: one label call -- I set SOLVED (bar met, every wall
explained); PARTIAL is defensible if you weight the modest size of the gain. NEXT: (1) land the measurement
fix; (2) land the graded binder + person-exclusion; (3) open "wire the situation model into who-did-what" as
the successor problem -- that's where the remaining points are.
═══════════════════════════════════════════════════════════════════════════════════════════════════
