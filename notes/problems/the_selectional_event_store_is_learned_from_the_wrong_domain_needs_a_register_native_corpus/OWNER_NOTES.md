---
owner_verdict: DONE
---

SOLUTION SUBMISSION -- the_selectional_event_store_is_learned_from_the_wrong_domain_needs_a_register_native_corpus

STATUS: SOLVED (witness verification/test_register_native_store.py 5/5+2; problem_ledger --check clean;
WIP until owner_verdict: DONE).

THE PROBLEM I WAS ASSIGNED: the reader's per-verb selectional/event knowledge (which things a verb acts on)
is learned from the WRONG DOMAIN (Simple-English-Wikipedia). A parent oracle-ladder dissection claimed DOMAIN
MATCH of the selectional corpus is the #1 who-did-what lever (+0.149). Build a deployable, no-gold,
REGISTER-NATIVE selectional/event store (offline from a DISJOINT domain-matched corpus, FHRR-bound) and prove
it recovers who-did-what over the out-of-domain store on held-out data -- or locate why it doesn't.

WHAT I BUILT + RESULT: the QA test is grade-school SCIENCE prose, so I built a no-gold store from a genuinely
DISJOINT science corpus (ARC, leakage-guarded: 0 test sentences in the store), bound with the substrate's FHRR
joint event codec (reusing hdlab.binding), and tested held-out who-did-what.
  * THE PARENT'S +0.149 WAS TOPICAL NEAR-LEAKAGE. On a truly disjoint corpus the MARGINAL (verb->object) store
    TIES simplewiki (-0.008, not sep) -- the +0.149 came from leave-one-sentence-out on the TEST corpus itself.
  * THE DOMAIN LEVER IS REAL BUT LIVES IN THE JOINT EVENT CODE, not the marginal store: the FHRR (subj,verb,obj)
    store RECOVERS who-did-what CI-separated over simplewiki -- soft-AND conjunctive kernel +0.036 CI-sep on
    BOTH slices, twin LOSES, wrong-domain fiction LOSES, and simplewiki has MORE triples yet loses (domain, not
    volume). Stable at 3M tokens (the true modest size, ~+0.035). This is a positive prediction of joint
    conjunctive binding (Frankland-Greene): register knowledge is a property of who-did-what-to-what structure.
  * GENERALIZES within-register (unseen fillers); across register the store is the robust fallback where the
    parser fails (19c non-canonical: parser 0.008, store 0.30).

CONTROLS: verb-shuffled twin (same corpus, wrong-domain labels) loses CI-sep; wrong-domain fiction loses;
leakage guard n_leak=0; data-volume excluded (simplewiki has more triples, loses).

KEY REALIZATIONS: (1) a genuinely disjoint corpus dissolves the marginal +0.149 -- the probe and the
deliverable measure different things, and the gap IS the leakage. (2) The domain signal is in the JOINT, not
the marginal (clean single-variable dissociation: same knowledge, two representations). (3) The store looked
worthless on a broken structural cue and valuable on a real parse -- "ask whether it could have succeeded"
paid off. (4) OWNER-DIRECTED: I nearly reinvented graded_role_assigner / graded_competition /
convergent_cue_reader -- they are owner-DONE and ARE the brain-foundational integrator; this problem's store
is the SELECTIONAL cue they were missing.

DEEP DIVE (owner-driven) -- who-did-what taken to the wall, brain-foundationally, ALL by composing owner-DONE
organs: position 0.474 -> real parse 0.588 -> +voice/store-gate 0.628 -> +agreement 0.634 -> convergent
precision-weighting (convergent_cue_reader over the structural cue + this store) 0.658 = 68% of chance->human
(from 34%). Every step CI-separated. Then EXHAUSTIVE: I composed every brain-foundational organ on the better
parser (incremental_parser, predictive_reader precision #4, conceptual_meaning #8, conflict-driven precision)
-- NONE beats ~0.65; the integration is SATURATED and brain-foundational. Signal-loss decomposition proves
why: when the parse is correct we score 0.989; the ENTIRE remaining deficit is parse-attach failures, and the
substrate's own parser LOSES to spaCy en_core_web_sm (+0.073). So the PARSER is the sole cross-task lever.

PROPOSED hdlab WIRE (Q111, default-off, witnessed): ship the register-native FHRR event store as an offline
per-domain asset, wired as the SELECTIONAL cue into graded_role_assigner / convergent_cue_reader (NOT a new
organ, NOT the marginal store). AUDIT UPDATE: correct the p5 "+0.149" row to the disjoint-corpus reality
(marginal ties; ~+0.035 joint-only); the who-did-what levers are the structural parse + this store the parse
unlocks; grounded-12d/generative/animacy/conceptual are measured NON-levers.

FILES: experiments/exp_register_native_store_v1.py, exp_brain_faithful_who_did_what_v1.py,
exp_parser_headroom_v1.py, exp_richer_extraction_v1.py, exp_error_decomposition_v1.py,
exp_optimized_who_did_what_v1.py, exp_brain_foundational_integrator_v1.py,
exp_full_brain_foundational_reader_v1.py, exp_full_stack_spacy_v1.py; verification/test_register_native_store.py;
data/exp_register_native_store_v1/*. REVERIFY: .venv/Scripts/python.exe verification/test_register_native_store.py

#1 FOLLOW-ON (drafted): the parser is the cross-task bottleneck -- see
notes/problems/the_selectional_event_store.../PROPOSED_FOLLOWON_parser_is_the_cross_task_bottleneck.md.

TLDR (plain English): the word-knowledge store I was asked to build works -- but the earlier big number was an
artifact of learning from the very passages being tested; on genuinely separate science text the benefit is
smaller and only shows up when the reader stores whole events (who did what to what), which is how the brain
does it. Standing on that, I pushed who-did-what from ~47% to ~66% of the way to human by wiring our existing
brain-faithful organs together, and proved there's nothing left to gain from combining cues. The one thing
between us and human-level is the grammar-reader (the parser): when it's right we're at 99%, and ours is worse
than a small off-the-shelf model -- so that's the #1 next problem.

QUESTIONS: none blocking. NEXT STEPS: (1) mark DONE when satisfied; (2) strategy files the parser follow-on as
priority 1; (3) fold the AUDIT UPDATE. Nothing pushed or integrated -- awaiting your verdict.
